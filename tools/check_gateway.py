#!/usr/bin/env python3
"""Check the gateway capture record: schema, fixtures, and the invariants a
schema cannot say (changes/2026-09-19-capture-record.md).

1. SCHEMA        : gateway/schema/capture-v1.json parses, is draft 2020-12,
                   every $ref resolves, and uses only the keywords this
                   checker implements (an unknown keyword is a FAIL, never a
                   silent skip — a validator that ignores what it does not
                   understand validates nothing).
2. ROWS          : every line of every stream under gateway/examples/<day>/
                   and gateway/captures/<day>/ is a JSON object that validates
                   against its stream's row schema.
3. LEDGER        : exchange ids unique; the ULID's embedded millisecond is
                   the row's `t`; t_end >= t; latency >= ttfb; a model call
                   (api_family known) names a model unless it aborted before
                   any reply (error present, t_end absent: the body may never
                   have arrived); no response blob means
                   an error is recorded; adaptations only on a translate
                   lane; marked secrets carry locations, scrubbed ones do not.
4. EVENTS        : every event and decoded row names an existing exchange;
                   (id, seq) unique, seq contiguous from 0, offsets
                   non-decreasing; `dir` only on websocket exchanges.
5. BLOBS         : every referenced blob exists at raw/<h[:2]>/<h>.<ext>,
                   hashes to its name and has the recorded length; no blob on
                   disk is unreferenced; secret locations lie inside their
                   blob.
6. REDACTION     : inside every stored HTTP message, the C5 headers carry
                   only `[redacted:<n>]` values, and the row's `redacted`
                   list is exactly the set of names redacted; no secret query
                   parameter survives in path, upstream.url, or request line.
7. PROVENANCE    : an examples day carries _provenance.json with
                   synthetic:true and no wire_sha256; a captures day carries
                   _receipt.json and wire_sha256 on every blob (AUTHORITY.md).

Per AUTHORITY.md this tool never edits fixtures. Exit non-zero on any FAIL.

Usage: check_gateway.py [--root DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

STREAMS = {"exchanges": "exchange", "events": "event", "scan": "scan", "decoded": "decoded"}
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REDACTED_VALUE = re.compile(r"^\[redacted:\d+\]$")
REDACT_HEADERS = {"authorization", "proxy-authorization", "x-api-key", "x-goog-api-key", "cookie", "set-cookie"}
REDACT_HEADER_WORDS = ("token", "secret")  # singular token only: "tokens" is a rate-limit counter
SECRET_QUERY = {"key", "api_key", "access_token"}
CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
SUPPORTED_KEYWORDS = {
    "$schema", "$id", "title", "description", "oneOf", "$defs", "const", "type", "pattern",
    "enum", "properties", "required", "additionalProperties", "items", "minItems",
    "uniqueItems", "minimum", "maximum", "minLength", "$ref",
}
TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "integer": int, "number": (int, float), "null": type(None),
}


class Report:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.counts: dict[str, int] = {}

    def fail(self, msg: str) -> None:
        self.fails.append(msg)
        print(f"FAIL {msg}")

    def count(self, key: str, n: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + n


# --------------------------------------------------------------------------
# A deliberately small JSON Schema validator. It implements exactly the
# keywords the capture schema uses and refuses anything else, so the schema
# cannot grow past what is enforced without this file growing with it.
# tools/test_check_gateway.py cross-checks it against the `jsonschema`
# library whenever that library is installed.
# --------------------------------------------------------------------------

class SchemaError(Exception):
    pass


class Validator:
    def __init__(self, schema: dict):
        self.schema = schema
        self._audit(schema, "#")

    def _audit(self, node: dict, path: str) -> None:
        """Walk every subschema; refuse any keyword this validator does not implement."""
        for k, v in node.items():
            if k not in SUPPORTED_KEYWORDS:
                raise SchemaError(f"{path}: keyword {k!r} is not implemented by check_gateway.py")
            if k in ("properties", "$defs"):
                for name, sub in v.items():
                    self._audit(sub, f"{path}/{k}/{name}")
            elif k == "items" or (k == "additionalProperties" and isinstance(v, dict)):
                self._audit(v, f"{path}/{k}")
            elif k == "oneOf":
                for i, sub in enumerate(v):
                    self._audit(sub, f"{path}/{k}/{i}")
            elif k == "$ref":
                self.resolve(v)

    def resolve(self, ref: str) -> dict:
        if not ref.startswith("#/"):
            raise SchemaError(f"external $ref not supported: {ref}")
        node = self.schema
        for part in ref[2:].split("/"):
            if not isinstance(node, dict) or part not in node:
                raise SchemaError(f"$ref does not resolve: {ref}")
            node = node[part]
        return node

    def validate(self, value, schema: dict, path: str = "$") -> list[str]:
        errs: list[str] = []
        if "$ref" in schema:
            errs += self.validate(value, self.resolve(schema["$ref"]), path)
        if "const" in schema and value != schema["const"]:
            errs.append(f"{path}: expected const {schema['const']!r}, got {value!r}")
        if "type" in schema:
            types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
            ok = False
            for t in types:
                py = TYPES[t]
                if t in ("integer", "number") and isinstance(value, bool):
                    continue
                if isinstance(value, py):
                    ok = True
            if not ok:
                errs.append(f"{path}: expected type {schema['type']}, got {type(value).__name__}")
                return errs
        if "enum" in schema and value not in schema["enum"]:
            errs.append(f"{path}: {value!r} not in {schema['enum']}")
        if isinstance(value, str):
            if "pattern" in schema and not re.search(schema["pattern"], value):
                errs.append(f"{path}: {value!r} does not match /{schema['pattern']}/")
            if "minLength" in schema and len(value) < schema["minLength"]:
                errs.append(f"{path}: shorter than {schema['minLength']}")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in schema and value < schema["minimum"]:
                errs.append(f"{path}: {value} < minimum {schema['minimum']}")
            if "maximum" in schema and value > schema["maximum"]:
                errs.append(f"{path}: {value} > maximum {schema['maximum']}")
        if isinstance(value, list):
            if "minItems" in schema and len(value) < schema["minItems"]:
                errs.append(f"{path}: fewer than {schema['minItems']} items")
            if schema.get("uniqueItems"):
                seen = [json.dumps(v, sort_keys=True) for v in value]
                if len(set(seen)) != len(seen):
                    errs.append(f"{path}: items are not unique")
            if "items" in schema:
                for i, v in enumerate(value):
                    errs += self.validate(v, schema["items"], f"{path}[{i}]")
        if isinstance(value, dict):
            props = schema.get("properties", {})
            for k in schema.get("required", []):
                if k not in value:
                    errs.append(f"{path}: missing required {k!r}")
            for k, v in value.items():
                if k in props:
                    errs += self.validate(v, props[k], f"{path}.{k}")
                elif "additionalProperties" in schema:
                    ap = schema["additionalProperties"]
                    if ap is False:
                        errs.append(f"{path}: unknown field {k!r}")
                    elif isinstance(ap, dict):
                        errs += self.validate(v, ap, f"{path}.{k}")
        if "oneOf" in schema:
            matches = [s for s in schema["oneOf"] if not self.validate(value, s, path)]
            if len(matches) != 1:
                errs.append(f"{path}: oneOf matched {len(matches)} alternatives, need exactly 1")
        return errs


# --------------------------------------------------------------------------

def ulid_ms(u: str) -> int:
    n = 0
    for ch in u[:10]:
        n = n * 32 + CROCKFORD.index(ch)
    return n


def ts_ms(t: str) -> int:
    from datetime import datetime, timezone
    dt = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def read_jsonl(path: Path, rep: Report) -> list[dict]:
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            rep.fail(f"{path}:{n}: blank line (streams are one object per line, no blanks)")
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            rep.fail(f"{path}:{n}: not JSON: {e}")
            continue
        if not isinstance(obj, dict):
            rep.fail(f"{path}:{n}: not an object")
            continue
        rows.append(obj)
    return rows


def parse_http(data: bytes) -> tuple[str, list[tuple[str, str]], bytes] | None:
    sep = data.find(b"\r\n\r\n")
    if sep < 0:
        return None
    head = data[:sep].decode("latin-1").split("\r\n")
    start, headers = head[0], []
    for line in head[1:]:
        if ":" not in line:
            return None
        k, v = line.split(":", 1)
        headers.append((k.strip().lower(), v.strip()))
    return start, headers, data[sep + 4:]


def must_redact(name: str) -> bool:
    if name in REDACT_HEADERS:
        return True
    return re.search(r"token(?!s)|secret", name) is not None


def has_secret_query(s: str) -> str | None:
    q = s.split("?", 1)[1] if "?" in s else ""
    q = q.split(" ", 1)[0]
    for pair in q.split("&"):
        if pair.split("=", 1)[0].lower() in SECRET_QUERY:
            return pair.split("=", 1)[0]
    return None


def check_day(day_dir: Path, kind: str, validator: Validator, rep: Report) -> None:
    day = day_dir.name
    if not DAY_RE.match(day):
        rep.fail(f"{day_dir}: directory is not a YYYY-MM-DD day")
        return
    rows: dict[str, list[dict]] = {}
    for stream, defname in STREAMS.items():
        p = day_dir / stream / f"{day}.jsonl"
        if not p.exists():
            rows[stream] = []
            continue
        extra = [q for q in (day_dir / stream).iterdir() if q != p]
        for q in extra:
            rep.fail(f"{q}: a day directory holds exactly one file per stream, named {day}.jsonl")
        rows[stream] = read_jsonl(p, rep)
        schema = validator.resolve(f"#/$defs/{defname}")
        for i, row in enumerate(rows[stream], 1):
            for err in validator.validate(row, schema):
                rep.fail(f"{p}:{i}: {err}")
        rep.count(f"{kind}.{stream}", len(rows[stream]))

    # ---- ledger ----------------------------------------------------------
    ex: dict[str, dict] = {}
    for i, r in enumerate(rows["exchanges"], 1):
        where = f"{day}/exchanges:{i}"
        rid = r.get("id")
        if not isinstance(rid, str):
            continue
        if rid in ex:
            rep.fail(f"{where}: duplicate exchange id {rid}")
        ex[rid] = r
        try:
            if ulid_ms(rid) != ts_ms(r["t"]):
                rep.fail(f"{where}: ULID millisecond {ulid_ms(rid)} != t {r['t']}")
            if "t_end" in r and ts_ms(r["t_end"]) < ts_ms(r["t"]):
                rep.fail(f"{where}: t_end before t")
        except (ValueError, KeyError):
            pass  # the schema already reported the malformed field
        up = r.get("upstream", {})
        if "ttfb_ms" in up and "latency_ms" in up and up["latency_ms"] < up["ttfb_ms"]:
            rep.fail(f"{where}: latency_ms < ttfb_ms")
        aborted_early = "error" in r and "t_end" not in r
        if r.get("api_family") not in (None, "unknown") and "model" not in r and not aborted_early:
            rep.fail(f"{where}: api_family {r.get('api_family')} is a model call but no model is recorded")
        raw = r.get("raw", {})
        if "response" not in raw and "error" not in r:
            rep.fail(f"{where}: no response blob and no error: an exchange that ended without a reply must say why")
        if "t_end" not in r and ("usage" in r or "response" in raw):
            rep.fail(f"{where}: aborted (no t_end) yet carries usage or a response")
        if "adaptations" in r and r.get("route", {}).get("lane") != "translate":
            rep.fail(f"{where}: adaptations recorded outside a translate lane")
        sec = r.get("secrets")
        if sec:
            if sec.get("action") == "marked" and "locations" not in sec:
                rep.fail(f"{where}: marked secrets must say where")
            if sec.get("action") == "scrubbed" and "locations" in sec:
                rep.fail(f"{where}: scrubbed secrets cannot have locations (the bytes are gone)")
            if sec.get("found") is not None and sec.get("locations") and sec["found"] != len(sec["locations"]):
                rep.fail(f"{where}: secrets.found != number of locations")
        for field in ("path",):
            if isinstance(r.get(field), str):
                bad = has_secret_query(r[field])
                if bad:
                    rep.fail(f"{where}: secret query parameter {bad!r} survives in {field}")
        if isinstance(up.get("url"), str):
            bad = has_secret_query(up["url"])
            if bad:
                rep.fail(f"{where}: secret query parameter {bad!r} survives in upstream.url")
            if "@" in up["url"].split("/", 3)[2] if up["url"].count("/") >= 3 else False:
                rep.fail(f"{where}: upstream.url carries userinfo")

    # ---- events and decoded ----------------------------------------------
    seen: dict[str, list[dict]] = {}
    for i, e in enumerate(rows["events"], 1):
        eid = e.get("id")
        if eid not in ex:
            rep.fail(f"{day}/events:{i}: id {eid} is not an exchange of this day")
            continue
        seen.setdefault(eid, []).append(e)
        if "dir" in e and ex[eid].get("transport") != "websocket":
            rep.fail(f"{day}/events:{i}: dir is websocket-only; exchange {eid} is {ex[eid].get('transport')}")
    for eid, evs in seen.items():
        seqs = [e.get("seq") for e in evs]
        if sorted(seqs) != list(range(len(evs))):
            rep.fail(f"{day}/events: exchange {eid}: seq must be 0..{len(evs) - 1} exactly once each, got {sorted(seqs)}")
        offs = [e.get("t_offset_ms") for e in sorted(evs, key=lambda e: e.get("seq", 0))]
        if any(b < a for a, b in zip(offs, offs[1:])):
            rep.fail(f"{day}/events: exchange {eid}: t_offset_ms decreases along seq")
    for i, d in enumerate(rows["decoded"], 1):
        did = d.get("id")
        if did not in ex:
            rep.fail(f"{day}/decoded:{i}: id {did} is not an exchange of this day")
            continue
        st = d.get("status")
        if st == "full" and not ("request" in d and "response" in d):
            rep.fail(f"{day}/decoded:{i}: status full needs request and response")
        if st == "none" and ("request" in d or "response" in d):
            rep.fail(f"{day}/decoded:{i}: status none cannot carry canonical forms")
        if st == "partial" and "notes" not in d:
            rep.fail(f"{day}/decoded:{i}: status partial must say what was not decoded")
        if "events" in d and ex[did].get("transport") not in ("sse", "websocket"):
            rep.fail(f"{day}/decoded:{i}: an event trace on a non-streamed exchange")

    # ---- blobs and redaction ---------------------------------------------
    referenced: set[Path] = set()
    for rid, r in ex.items():
        raw = r.get("raw", {})
        redacted_names: set[str] = set()
        for which, ref in raw.items():
            if not isinstance(ref, dict) or not isinstance(ref.get("sha256"), str):
                continue
            h = ref["sha256"]
            ext = ".jsonl" if which == "frames" else ".http"
            p = day_dir / "raw" / h[:2] / f"{h}{ext}"
            referenced.add(p)
            if not p.exists():
                rep.fail(f"{day}/exchanges {rid}: raw.{which} blob {h[:12]}… missing at {p.relative_to(day_dir)}")
                continue
            data = p.read_bytes()
            if hashlib.sha256(data).hexdigest() != h:
                rep.fail(f"{day}/exchanges {rid}: raw.{which} blob does not hash to its name")
            if len(data) != ref.get("bytes"):
                rep.fail(f"{day}/exchanges {rid}: raw.{which}.bytes {ref.get('bytes')} != file length {len(data)}")
            if kind == "captures" and "wire_sha256" not in ref:
                rep.fail(f"{day}/exchanges {rid}: a promoted capture needs raw.{which}.wire_sha256 (AUTHORITY.md receipt)")
            if kind == "examples" and "wire_sha256" in ref:
                rep.fail(f"{day}/exchanges {rid}: a synthetic example cannot claim a wire hash")
            if ext == ".http":
                parsed = parse_http(data)
                if parsed is None:
                    rep.fail(f"{day}/exchanges {rid}: raw.{which} is not an HTTP message (start line, headers, CRLFCRLF, body)")
                    continue
                start, headers, body = parsed
                for name, value in headers:
                    if must_redact(name):
                        if not REDACTED_VALUE.match(value):
                            rep.fail(f"{day}/exchanges {rid}: raw.{which} header {name!r} is not redacted")
                        redacted_names.add(name)
                    elif REDACTED_VALUE.match(value):
                        redacted_names.add(name)
                if which == "request":
                    bad = has_secret_query(start)
                    if bad:
                        rep.fail(f"{day}/exchanges {rid}: secret query parameter {bad!r} in the stored request line")
                    if "content_encoding" not in ref and any(n in ("content-encoding", "transfer-encoding") for n, _ in headers):
                        rep.fail(f"{day}/exchanges {rid}: stored request keeps a wire framing header; store the decoded entity and record content_encoding")
                if which == "response" and any(n in ("content-encoding", "transfer-encoding") for n, _ in headers):
                    rep.fail(f"{day}/exchanges {rid}: stored response keeps a wire framing header; store the decoded entity and record content_encoding")
                clen = next((v for n, v in headers if n == "content-length"), None)
                if clen is not None and clen.isdigit() and int(clen) != len(body):
                    rep.fail(f"{day}/exchanges {rid}: raw.{which} content-length {clen} != stored body length {len(body)}")
            for loc in (r.get("secrets") or {}).get("locations", []):
                if loc.get("blob") == which and loc.get("offset", 0) + loc.get("length", 0) > len(data):
                    rep.fail(f"{day}/exchanges {rid}: secret location lies outside raw.{which}")
        declared = {n for n in r.get("redacted", []) if not n.startswith("query:")}
        if declared != redacted_names:
            rep.fail(f"{day}/exchanges {rid}: redacted {sorted(declared)} != headers actually redacted in blobs {sorted(redacted_names)}")
    raw_dir = day_dir / "raw"
    if raw_dir.exists():
        for p in sorted(raw_dir.rglob("*")):
            if p.is_file() and p not in referenced:
                rep.fail(f"{p.relative_to(day_dir.parent)}: blob on disk that no exchange references")
            if p.is_file() and p.parent.name != p.name[:2]:
                rep.fail(f"{p.relative_to(day_dir.parent)}: blob is not under raw/<sha256[:2]>/")

    # ---- provenance ------------------------------------------------------
    if kind == "examples":
        pv = day_dir / "_provenance.json"
        if not pv.exists():
            rep.fail(f"{day_dir}: examples day needs _provenance.json")
        else:
            try:
                if json.loads(pv.read_text()).get("synthetic") is not True:
                    rep.fail(f"{pv}: an examples day must declare synthetic: true")
            except json.JSONDecodeError as e:
                rep.fail(f"{pv}: not JSON: {e}")
    else:
        rc = day_dir / "_receipt.json"
        if not rc.exists():
            rep.fail(f"{day_dir}: captures day needs _receipt.json (gateway version, host, date, reviewer)")
        else:
            try:
                r = json.loads(rc.read_text())
                for k in ("gateway_version", "captured_on", "date", "reviewed_by"):
                    if k not in r:
                        rep.fail(f"{rc}: missing {k!r}")
            except json.JSONDecodeError as e:
                rep.fail(f"{rc}: not JSON: {e}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    root = ap.parse_args().root
    rep = Report()
    schema_path = root / "gateway" / "schema" / "capture-v1.json"
    try:
        schema = json.loads(schema_path.read_text())
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            rep.fail(f"{schema_path}: not draft 2020-12")
        validator = Validator(schema)
        for name in STREAMS.values():
            validator.resolve(f"#/$defs/{name}")
        if validator.resolve("#/$defs/version").get("const") != 1:
            rep.fail(f"{schema_path}: this checker enforces capture v1")
    except (OSError, json.JSONDecodeError, SchemaError) as e:
        rep.fail(f"{schema_path}: {e}")
        print(f"check_gateway: FAIL ({len(rep.fails)})")
        return 1
    for kind in ("examples", "captures"):
        base = root / "gateway" / kind
        if not base.exists():
            continue
        for day_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            check_day(day_dir, kind, validator, rep)
    summary = ", ".join(f"{k}={v}" for k, v in sorted(rep.counts.items())) or "no rows"
    if rep.fails:
        print(f"check_gateway: FAIL ({len(rep.fails)}) — {summary}")
        return 1
    print(f"check_gateway: OK — {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
