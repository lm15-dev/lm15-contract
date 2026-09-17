#!/usr/bin/env python3
"""Receipt: the judgment schema answered on a vLLM server by token-trie scoring.

One tokenize pass per key path (recorded), then ONE batched /v1/completions call
with every trie node as a prompt and `logprob_token_ids` = union of child tokens.
Writes the verbatim request/response and the folded distributions. Run against
the 0.29 server (port 8001) for the positive receipt and the 0.25.1 family server
(port 8000) for the negative one (field silently dropped).
"""
import argparse, datetime, hashlib, json, math, time, urllib.request

SCHEMA = json.load(open(__file__.rsplit("/", 1)[0] + "/judgment-schema.json"))
NOTE = ("Ripe blackberry and cassis lead, framed by toasty oak and firm, fine-grained tannins. "
        "Long, layered finish with graphite and dried herbs. Impressive now; will reward a decade in the cellar.")
END = "<|im_end|>"


def http(url, path, payload, key=None):
    headers = {"Content-Type": "application/json"} | ({"Authorization": "Bearer " + key} if key else {})
    req = urllib.request.Request(url + path, data=json.dumps(payload).encode(), headers=headers)
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, json.loads(r.read()), time.perf_counter() - t
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), time.perf_counter() - t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8001"); ap.add_argument("--model", default="LiquidAI/LFM2.5-2.6B")
    ap.add_argument("--key"); ap.add_argument("--output", required=True); ap.add_argument("--end", default=END)
    ap.add_argument("--prefix", default="Answer:", help="assistant prefill before the key")
    ap.add_argument("--think", default="<think>\n</think>\n", help="reasoning-closing prefix ('' for models without it)")
    a = ap.parse_args()
    tok = lambda text: http(a.url, "/tokenize", {"model": a.model, "prompt": text, "add_special_tokens": False}, a.key)[1]["tokens"]
    detok = lambda ids: http(a.url, "/detokenize", {"model": a.model, "tokens": ids}, a.key)[1]["prompt"]

    # The questions, read off the schema exactly as MAP-14 reads them.
    questions = {}
    for name, prop in SCHEMA["properties"].items():
        if prop.get("type") == "boolean":
            keys = {"true": None, "false": None}
        else:
            keys = {str(b["const"]): b.get("description") for b in prop["anyOf"]}
        questions[name] = (prop["description"], keys, prop.get("type") == "integer")

    prompts, meta, union = [], [], set()
    prefix_count = len(tok(a.prefix + " "))
    for name, (instruction, keys, ordered) in questions.items():
        listed = "\n".join(f"- {k}" + (f": {d}" if d else "") for k, d in keys.items())
        ask = f"{instruction}\nOptions:\n{listed}\nAnswer with the option only, spelled exactly as listed."
        seqs = {k: tuple(tok(a.prefix + " " + k)[len(tok(a.prefix)):]) + (tok(a.end)[0],) for k in keys}
        nodes = {}
        for seq in seqs.values():
            for i in range(len(seq)):
                nodes.setdefault(seq[:i], set()).add(seq[i])
        for prefix, children in nodes.items():
            text_prefix = a.prefix + detok(list(prefix))
            prompts.append("<|startoftext|><|im_start|>user\n" + "Tasting note:\n" + NOTE + "\n\n" + ask +
                           "<|im_end|>\n<|im_start|>assistant\n" + a.think + text_prefix)
            meta.append({"question": name, "prefix": list(prefix), "children": sorted(children)})
            union |= children
        meta[-1]["seqs"] = {k: list(v) for k, v in seqs.items()}

    body = {"model": a.model, "prompt": prompts, "max_tokens": 1, "temperature": 1.0, "logprobs": 0,
            "return_tokens_as_token_ids": True, "logprob_token_ids": sorted(union)}
    status, reply, seconds = http(a.url, "/v1/completions", body, a.key)
    rec = {"captured": datetime.datetime.now(datetime.timezone.utc).isoformat(), "url": a.url, "model": a.model,
           "request_sha256": hashlib.sha256(json.dumps(body).encode()).hexdigest()[:16], "status": status,
           "seconds": round(seconds, 3), "nodes": meta, "request_body": body, "response_body": reply}
    if status == 200:
        choices = sorted(reply["choices"], key=lambda c: c["index"])
        per_q = {}
        honoured = True
        for choice, m in zip(choices, meta):
            top = choice["logprobs"]["top_logprobs"][0]
            got = {t: top.get(f"token_id:{t}") for t in m["children"]}
            if any(v is None for v in got.values()):
                honoured = False
            per_q.setdefault(m["question"], {})[tuple(m["prefix"])] = got
        rec["logprob_token_ids_honoured"] = honoured
        if honoured:
            dists, coverage = {}, {}
            for m in meta:
                if "seqs" not in m: continue
                q = m["question"]; raw = {}
                for k, seq in m["seqs"].items():
                    raw[k] = sum(per_q[q][tuple(seq[:i])][seq[i]] for i in range(len(seq)))
                coverage[q] = sum(math.exp(v) for v in raw.values())
                top = max(raw.values()); w = {k: math.exp(v - top) for k, v in raw.items()}; z = sum(w.values())
                dists[q] = {k: round(v / z, 4) for k, v in w.items()}
            rec["distributions"], rec["coverage"] = dists, coverage
            rec["server_version"] = http(a.url, "/version", {}, a.key)[1] if False else None
    json.dump(rec, open(a.output, "w"), indent=2)
    print(status, f"{seconds*1000:.0f}ms", len(prompts), "prompts", "| honoured:", rec.get("logprob_token_ids_honoured"))
    print(json.dumps(rec.get("distributions"), indent=1)); print("coverage", rec.get("coverage"))


if __name__ == "__main__":
    main()
