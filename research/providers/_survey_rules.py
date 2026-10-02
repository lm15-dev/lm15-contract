"""Decision rules: a provider survey's recorded answers → a drafted compat preset.

Pure and offline (stdlib only, no lm15 import), so the rules are unit-tested
in the contract's CI (tools/test_provider_survey.py) and a reviewer can read
every decision as code. The input is the probe receipts a survey wrote
(``survey.py run``): probe name → ``{"sent", "status", "body", ...}`` with the
body parsed JSON, or the raw text of a stream or a non-JSON reply.

Each rule answers one knob of ``OpenAIChatCompat`` (lm15-python
lm15/compat.py) from the SERVER's behaviour, the way the ratified presets were
decided (changes/2026-09-26-inference-hosts-live.md, 2026-09-03-zai-live.md):

- a server that refuses loudly (HTTP 4xx) needs nothing: MAP-5/MAP-8 are met
  by the server;
- a server that answers 200 and ignores what it was asked is silent, and the
  knob refuses client-side (MAP-8) or substitutes and records (MAP-13);
- a value the probes cannot establish is ``needs-you`` with the reason — never
  a guess. Knobs a survey cannot see at all (a documented field name, MAP-10
  media in tool results, builtin tools) are ``not-surveyed`` and say where the
  answer comes from.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

Receipts = dict[str, dict[str, Any]]

DECIDED, NEEDS_YOU, NOT_SURVEYED, CONVENTION = "decided", "needs-you", "not-surveyed", "convention"
CODE_WORD = "PELICAN-42"
PLACE_KEYS = {"city", "country"}

# Every probe the runner may send, by role: the rules read only these names.
PROBES = (
    "basic", "stream", "stream-plain", "cap-max_tokens", "cap-max_completion_tokens",
    "role-system", "role-developer", "user-field", "tools", "stream-tools",
    "tool-choice-required", "tool-choice-named", "tool-choice-none", "json-schema",
    "usage-repeat-1", "usage-repeat-2", "models", "error-auth", "error-model", "cors",
    "effort-low", "effort-high", "effort-none", "effort-none-off-model", "effort-none-always-on",
    "effort-word-minimal", "effort-word-medium", "effort-word-xhigh", "effort-word-max", "effort-word-bogus",
    "shape-thinking-enabled", "shape-thinking-disabled", "shape-reasoning-object",
    "tool-choice-required-reasoner",
    *(f"replay-{f}-{n}" for f in ("reasoning_content", "reasoning", "absent") for n in (1, 2, 3)),
)


@dataclass
class Finding:
    knob: str
    value: Any
    status: str
    evidence: list[str]
    note: str
    also: list[Any] = field(default_factory=list)  # other values the server equally honours
    override: tuple[str, dict[str, Any]] | None = None  # (model id prefix, knobs) for one model family

    def as_dict(self) -> dict[str, Any]:
        out = {"knob": self.knob, "value": self.value, "status": self.status, "evidence": self.evidence, "note": self.note}
        if self.also:
            out["also"] = self.also
        if self.override:
            out["override"] = {"prefix": self.override[0], "knobs": self.override[1]}
        return out


# ─── reading a receipt ───────────────────────────────────────────────


def status(rec: dict | None) -> int | None:
    return None if rec is None else rec.get("status")


def ok(rec: dict | None) -> bool:
    return status(rec) == 200


def loud(rec: dict | None) -> bool:
    """A refusal the caller sees: 4xx (5xx is a server failure, not an answer)."""
    s = status(rec)
    return s is not None and 400 <= s < 500


def message(rec: dict | None) -> dict:
    body = (rec or {}).get("body")
    if not isinstance(body, dict):
        return {}
    choices = body.get("choices") or [{}]
    return (choices[0] or {}).get("message") or {}


def finish(rec: dict | None) -> str | None:
    body = (rec or {}).get("body")
    if not isinstance(body, dict):
        return None
    return ((body.get("choices") or [{}])[0] or {}).get("finish_reason")


def content(rec: dict | None) -> str:
    value = message(rec).get("content")
    if isinstance(value, list):
        return "".join(p.get("text", "") for p in value if isinstance(p, dict))
    return value if isinstance(value, str) else ""


def tool_called(rec: dict | None) -> bool:
    return bool(message(rec).get("tool_calls"))


def usage(rec: dict | None) -> dict:
    body = (rec or {}).get("body")
    return (body.get("usage") or {}) if isinstance(body, dict) else {}


def reasoning_tokens(rec: dict | None) -> int:
    details = usage(rec).get("completion_tokens_details") or {}
    value = details.get("reasoning_tokens") if isinstance(details, dict) else None
    return int(value) if isinstance(value, (int, float)) else 0


def reasoning_text(rec: dict | None) -> str:
    m = message(rec)
    for key in ("reasoning_content", "reasoning"):
        if isinstance(m.get(key), str) and m[key].strip():
            return m[key]
    details = m.get("reasoning_details")
    if isinstance(details, list):
        return "".join(str(d.get("text", "")) for d in details if isinstance(d, dict))
    return ""


def reasoned(rec: dict | None) -> bool:
    """The reply shows reasoning happened: a trace, or reasoning tokens billed."""
    return reasoning_tokens(rec) > 0 or bool(reasoning_text(rec))


def sse_events(rec: dict | None) -> tuple[list[dict], bool]:
    body = (rec or {}).get("body")
    text = body if isinstance(body, str) else ""
    events, done = [], False
    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            done = True
            continue
        try:
            value = json.loads(data)
        except ValueError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events, done


def capped(rec: dict | None) -> bool:
    """A max-tokens field of 8 was honoured: the reply stopped for length, or stayed tiny."""
    if not ok(rec):
        return False
    completion = usage(rec).get("completion_tokens")
    return finish(rec) == "length" or (isinstance(completion, int) and completion <= 12)


def json_keys(text: str) -> set[str] | None:
    candidate = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", candidate, re.S)
    try:
        value = json.loads(fenced.group(1) if fenced else candidate)
    except ValueError:
        return None
    return set(value) if isinstance(value, dict) else None


def error_text(rec: dict | None) -> str:
    body = (rec or {}).get("body")
    return json.dumps(body)[:200] if isinstance(body, (dict, list)) else str(body)[:200]


def say(rec: dict | None) -> str:
    """One line on what the server did, for the evidence column."""
    if rec is None:
        return "not sent"
    s = status(rec)
    if s != 200:
        return f"HTTP {s}: {error_text(rec)[:120]}"
    bits = [f"200 finish={finish(rec)}"]
    if tool_called(rec):
        bits.append("tool call")
    if reasoning_tokens(rec):
        bits.append(f"reasoning_tokens={reasoning_tokens(rec)}")
    elif reasoning_text(rec):
        bits.append("reasoning trace")
    text = content(rec)
    if text:
        bits.append(repr(text[:50]))
    return ", ".join(bits)


# ─── the rules ───────────────────────────────────────────────────────


def rule_max_tokens_field(r: Receipts) -> Finding:
    names = ["cap-max_completion_tokens", "cap-max_tokens"]
    mct, mt = capped(r.get(names[0])), capped(r.get(names[1]))
    if mct:
        return Finding("max_tokens_field", "max_completion_tokens", DECIDED, names,
                       "max_completion_tokens: 8 stopped the reply (OpenAI's current field)", also=["max_tokens"] if mt else [])
    if mt:
        return Finding("max_tokens_field", "max_tokens", DECIDED, names, "only max_tokens: 8 stopped the reply")
    return Finding("max_tokens_field", None, NEEDS_YOU, names,
                   f"neither field capped the reply ({say(r.get(names[0]))}; {say(r.get(names[1]))})")


def rule_stream_usage(r: Receipts) -> Finding:
    rec = r.get("stream")
    events, done = sse_events(rec)
    with_usage = any(isinstance(e.get("usage"), dict) and e["usage"].get("prompt_tokens") is not None for e in events)
    tail = "" if done else "; no data: [DONE] line (the chat parser ends on the stream's close)"
    if ok(rec) and with_usage:
        return Finding("stream_usage", "include", DECIDED, ["stream"], "stream_options.include_usage honoured: usage on a chunk" + tail)
    if loud(rec) and ok(r.get("stream-plain")):
        return Finding("stream_usage", "omit", DECIDED, ["stream", "stream-plain"],
                       "stream_options refused (HTTP 4xx); a stream without it is accepted")
    if ok(rec):
        return Finding("stream_usage", None, NEEDS_YOU, ["stream"],
                       "stream_options accepted but no chunk carried usage: usage would read as not reported" + tail)
    return Finding("stream_usage", None, NEEDS_YOU, ["stream"], f"stream failed: {say(rec)}")


def rule_instruction_role(r: Receipts) -> Finding:
    system, developer = r.get("role-system"), r.get("role-developer")
    obeyed = "PINEAPPLE" in content(developer).upper()
    if ok(system):
        note = "a system message is accepted; " + (
            "the developer role is accepted and obeyed too" if ok(developer) and obeyed
            else "the developer role is " + ("accepted but not obeyed" if ok(developer) else f"refused ({say(developer)})"))
        return Finding("instruction_role", "system", DECIDED, ["role-system", "role-developer"], note,
                       also=["developer"] if ok(developer) and obeyed else [])
    return Finding("instruction_role", None, NEEDS_YOU, ["role-system"], f"a system message failed: {say(system)}")


def dial_read(low: dict | None, high: dict | None) -> bool:
    """The effort level changed the spend: high spent clearly more than low.
    Reasoning at both levels proves only that the model reasons."""
    lo, hi = reasoning_tokens(low), reasoning_tokens(high)
    return hi >= max(lo * 1.5, lo + 20)


def rule_thinking_format(r: Receipts, has_reasoner: bool) -> Finding:
    """Which dial the server reads, proved by an off switch that works or a
    spend that follows the level — never by "it reasoned"."""
    if not has_reasoner:
        return Finding("thinking_format", None, NEEDS_YOU, [], "no reasoning model was surveyed: name one in candidate.json, or state the server has none (\"none\")")
    low, high, none = r.get("effort-low"), r.get("effort-high"), r.get("effort-none")
    enabled, disabled = r.get("shape-thinking-enabled"), r.get("shape-thinking-disabled")
    off_model = r.get("effort-none-off-model")
    ev = ["effort-low", "effort-high", "effort-none", "effort-none-off-model", "shape-thinking-enabled", "shape-thinking-disabled"]
    if not (ok(low) and ok(high)):
        if ok(r.get("shape-reasoning-object")) and reasoned(r.get("shape-reasoning-object")):
            return Finding("thinking_format", "openrouter", NEEDS_YOU, ev + ["shape-reasoning-object"],
                           f"reasoning_effort refused ({say(low)}); the reasoning object works — confirm in the server's docs")
        return Finding("thinking_format", None, NEEDS_YOU, ev, f"reasoning_effort refused: {say(low)}")
    # An off switch works when it is accepted and the reply shows no reasoning;
    # the `off` model is a reasoning model that is documented to stop.
    effort_off = (ok(none) and not reasoned(none)) or (ok(off_model) and not reasoned(off_model))
    toggle_off = ok(disabled) and not reasoned(disabled) and ok(enabled) and reasoned(enabled)
    spend = f"low {reasoning_tokens(low)} / high {reasoning_tokens(high)} reasoning tokens"
    if toggle_off and not effort_off and ok(none) and reasoned(none):
        return Finding("thinking_format", "deepseek", DECIDED, ev,
                       f"reasoning_effort none was accepted and ignored; thinking.type=disabled stopped reasoning ({spend})")
    if effort_off:
        return Finding("thinking_format", "reasoning_effort", DECIDED, ev,
                       f"reasoning_effort none stopped reasoning ({spend})" +
                       ("; thinking.type=disabled works too, so the deepseek shape is equivalent" if toggle_off else ""),
                       also=["deepseek"] if toggle_off else [])
    if dial_read(low, high):
        return Finding("thinking_format", "reasoning_effort", DECIDED, ev, f"the spend follows reasoning_effort ({spend})",
                       also=["deepseek"] if toggle_off else [])
    if toggle_off:
        return Finding("thinking_format", "deepseek", DECIDED, ev,
                       f"thinking.type=disabled stopped reasoning; reasoning_effort showed no effect ({spend})")
    return Finding("thinking_format", None, NEEDS_YOU, ev,
                   f"neither off switch could be shown to work ({say(none)}; {say(disabled)}) and the spend did not follow "
                   f"the level ({spend}): the probes cannot tell which dial the server reads. Survey a model that can stop "
                   "reasoning (models.off), or decide from the docs")


def rule_reasoning_efforts(r: Receipts, has_reasoner: bool) -> Finding:
    if not has_reasoner:
        return Finding("reasoning_efforts", None, NOT_SURVEYED, [], "no reasoning model surveyed")
    words = ("minimal", "medium", "xhigh", "max", "bogus")
    names = [f"effort-word-{w}" for w in words]
    accepted = [w for w in words if ok(r.get(f"effort-word-{w}"))]
    refused = [w for w in words if loud(r.get(f"effort-word-{w}"))]
    if "bogus" in refused:
        return Finding("reasoning_efforts", None, DECIDED, names,
                       f"an unknown word is refused (HTTP 4xx), so levels need no list; accepted {accepted or 'none'}, refused {refused}")
    if "bogus" in accepted:
        return Finding("reasoning_efforts", None, NEEDS_YOU, names,
                       f"the server accepts the word 'bogus' (HTTP 200): it does not check levels, so the preset must list the "
                       f"model's native levels from the docs (MAP-7 rule 2). Accepted: {accepted}")
    return Finding("reasoning_efforts", None, NEEDS_YOU, names, f"'bogus' was neither accepted nor refused: {say(r.get('effort-word-bogus'))}")


def rule_reasoning_off_always_on(r: Receipts, always_on: str | None) -> list[Finding]:
    """The model that cannot stop reasoning, asked to stop: loud is fine; an
    accepted, ignored 'none' is a per-model `lowest` (Together GLM-5.3, 2026-09-26)."""
    rec = r.get("effort-none-always-on")
    if not always_on or rec is None:
        return []
    if ok(rec) and reasoned(rec):
        return [Finding("reasoning_off", None, DECIDED, ["effort-none-always-on"],
                        f"`{always_on}` accepted 'none' and reasoned anyway ({say(rec)}): lowest level, recorded (MAP-13 §4.2)",
                        override=(always_on, {"reasoning_off": "lowest"}))]
    return [Finding("reasoning_off", None, DECIDED, ["effort-none-always-on"], f"`{always_on}` and 'none': {say(rec)} — nothing to add")]


def rule_reasoning_off(r: Receipts, has_reasoner: bool, reasoner: str | None) -> Finding:
    if not has_reasoner:
        return Finding("reasoning_off", None, NOT_SURVEYED, [], "no reasoning model surveyed")
    none = r.get("effort-none")
    if loud(none):
        return Finding("reasoning_off", None, DECIDED, ["effort-none"],
                       f"the reasoning model refuses 'none' loudly ({say(none)}): MAP-5 is met by the server")
    if ok(none) and reasoned(none):
        return Finding("reasoning_off", None, DECIDED, ["effort-none"],
                       f"'none' accepted and the model reasoned anyway ({say(none)}): a paid no-op, so off becomes the lowest level, "
                       "recorded (MAP-13 §4.2) — for this model family", override=(reasoner or "", {"reasoning_off": "lowest"}))
    if ok(none):
        return Finding("reasoning_off", None, DECIDED, ["effort-none"], "'none' accepted and honoured: no reasoning in the reply")
    return Finding("reasoning_off", None, NEEDS_YOU, ["effort-none"], f"'none' gave {say(none)}")


def rule_thinking_replay(r: Receipts, has_replayer: bool) -> list[Finding]:
    if not has_replayer:
        return [Finding("thinking_replay", None, NEEDS_YOU, [], "no reasoning model surveyed for replay")]

    def recall(field_name: str) -> tuple[int, int, int]:
        recs = [r.get(f"replay-{field_name}-{n}") for n in (1, 2, 3)]
        hits = sum(1 for x in recs if ok(x) and CODE_WORD in (content(x) + reasoning_text(x)))
        return hits, sum(1 for x in recs if ok(x)), sum(1 for x in recs if loud(x))

    names = [f"replay-{f}-{n}" for f in ("reasoning_content", "reasoning", "absent") for n in (1, 2, 3)]
    rc, rs, absent = recall("reasoning_content"), recall("reasoning"), recall("absent")
    tally = (f"code word recalled via reasoning_content {rc[0]}/{rc[1]}, via reasoning {rs[0]}/{rs[1]}, "
             f"with no trace {absent[0]}/{absent[1]}")
    out: list[Finding] = []
    if absent[2] and not absent[1]:
        out.append(Finding("assistant_reasoning_content", "include_empty", NEEDS_YOU, names,
                           f"an assistant turn WITHOUT a reasoning field is refused ({say(r.get('replay-absent-1'))}): the server may "
                           "require reasoning_content on every assistant turn, as DeepSeek does — confirm in the docs"))
    if rc[0] >= 2 and absent[0] == 0:
        out.insert(0, Finding("thinking_replay", "native", DECIDED, names, tally + ": the replayed trace reaches the model"))
    elif rc[2] and rc[1] == 0:
        alt = (f"; the `reasoning` field is accepted and recalled {rs[0]}/{rs[1]}, but lm15's native replay sends "
               "reasoning_content, so using it needs a new knob (playbooks/provider.md kind A′)") if rs[1] else ""
        out.insert(0, Finding("thinking_replay", "omit", NEEDS_YOU, names,
                              tally + "; reasoning_content is refused on a replayed turn" + alt +
                              ". Choose omit (the trace is dropped) or as_text (the trace is pasted into the visible text)"))
    elif absent[0] > 0:
        out.insert(0, Finding("thinking_replay", None, NEEDS_YOU, names, tally + ": the model found the word without the trace, so the probe proves nothing"))
    else:
        out.insert(0, Finding("thinking_replay", None, NEEDS_YOU, names, tally +
                              ": too weak to show the trace reaches the model (2 of 3 needed); recall is sampled — re-run "
                              "`--only " + ",".join(f"replay-reasoning_content-{n}" for n in (1, 2, 3)) + "` or decide from the docs"))
    return out


def rule_forced_tool_choice(r: Receipts, reasoner: str | None) -> Finding:
    req, named, none = r.get("tool-choice-required"), r.get("tool-choice-named"), r.get("tool-choice-none")
    names = ["tool-choice-required", "tool-choice-named", "tool-choice-none"]
    silent = [n for n, rec, want in (("required", req, True), ("named", named, True), ("none", none, False))
              if ok(rec) and tool_called(rec) != want]
    honoured = [n for n, rec, want in (("required", req, True), ("named", named, True), ("none", none, False))
                if ok(rec) and tool_called(rec) == want]
    refused = [n for n, rec in (("required", req), ("named", named), ("none", none)) if loud(rec)]
    reasoner_rec = r.get("tool-choice-required-reasoner")
    override = None
    if reasoner and reasoner_rec is not None and (
            (ok(reasoner_rec) and not tool_called(reasoner_rec)) or (status(reasoner_rec) or 0) >= 500):
        override = (reasoner, {"forced_tool_choice": "reject"})
    # `value` is the provider-wide setting; `override` a per-model exception to it.
    detail = f"honoured {honoured or '-'}, ignored {silent or '-'}, refused {refused or '-'}"
    if silent:
        return Finding("forced_tool_choice", "reject", DECIDED, names + ["tool-choice-required-reasoner"],
                       detail + ": an ignored choice is a silent widening, so lm15 refuses it before the wire (MAP-8)")
    if honoured and not refused:
        return Finding("forced_tool_choice", None, DECIDED, names + ["tool-choice-required-reasoner"],
                       detail + (f"; the reasoning model {say(reasoner_rec)} → refuse for it" if override else ""), override=override)
    return Finding("forced_tool_choice", None, NEEDS_YOU, names, detail)


def rule_json_schema(r: Receipts) -> Finding:
    rec = r.get("json-schema")
    if loud(rec):
        return Finding("json_schema", None, DECIDED, ["json-schema"], f"refused loudly ({say(rec)}): nothing to add")
    if ok(rec):
        keys = json_keys(content(rec))
        if keys == PLACE_KEYS:
            return Finding("json_schema", None, DECIDED, ["json-schema"], "the reply is JSON with exactly the schema's keys")
        return Finding("json_schema", "reject", DECIDED, ["json-schema"],
                       f"HTTP 200 but the reply ignores the schema (keys {sorted(keys) if keys is not None else 'not JSON'}): refuse client-side (MAP-8)")
    return Finding("json_schema", None, NEEDS_YOU, ["json-schema"], say(rec))


def rule_user_field(r: Receipts) -> Finding:
    rec = r.get("user-field")
    if ok(rec):
        return Finding("user_field", None, NOT_SURVEYED, ["user-field"],
                       "`user` accepted (HTTP 200) — acceptance proves nothing: set the field the server's docs name (DeepSeek and Z.AI: user_id)")
    return Finding("user_field", None, NEEDS_YOU, ["user-field"], f"`user` refused ({say(rec)}): the docs name the field")


def rule_conventions() -> list[Finding]:
    return [
        Finding("tool_result_name", "omit", CONVENTION, [], "every Chat Completions preset omits it"),
        Finding("strict_tools", "omit", CONVENTION, [], "every Chat Completions preset omits it"),
        Finding("cache_control", "none", CONVENTION, ["usage-repeat-1", "usage-repeat-2"],
                "automatic caching or none: a key or long retention is dropped with a record; set otherwise only from the docs"),
        Finding("tool_result_media", "reject", NOT_SURVEYED, [],
                "MAP-10: reject until the tool-result matrix (research/providers/media_tool_results.py) receipts a cell; "
                "then 'images' or 'native', or an OPEN entry in tools/check_content_coverage.py"),
        Finding("builtin_tools", None, NOT_SURVEYED, [], "server-executed tools are named from the docs (groq is the only one today)"),
    ]


def facts(r: Receipts) -> dict[str, Any]:
    """What the survey found that is not a compat knob."""
    models = r.get("models")
    body = (models or {}).get("body")
    entries = body if isinstance(body, list) else (body.get("data") if isinstance(body, dict) else None)
    first, second = usage(r.get("usage-repeat-1")), usage(r.get("usage-repeat-2"))
    nested = (second.get("prompt_tokens_details") or {}).get("cached_tokens") if isinstance(second.get("prompt_tokens_details"), dict) else None
    flat = second.get("cached_tokens", second.get("prompt_cache_hit_tokens"))
    cors = r.get("cors") or {}
    return {
        "models": {"listed": isinstance(entries, list), "count": len(entries) if isinstance(entries, list) else None,
                   "shape": "array" if isinstance(body, list) else ("data" if isinstance(entries, list) else None),
                   "status": status(models)},
        "cached_tokens": {"nested": nested, "flat": flat, "first_call_keys": sorted(first)},
        "cors": {"status": cors.get("status"), "allow_origin": (cors.get("headers") or {}).get("access-control-allow-origin")},
        "errors": {"auth": {"status": status(r.get("error-auth")), "body": error_text(r.get("error-auth"))},
                   "model": {"status": status(r.get("error-model")), "body": error_text(r.get("error-model"))}},
        "tools": say(r.get("tools")),
    }


def analyze(r: Receipts, models: dict[str, str | None]) -> list[Finding]:
    reasoner = models.get("reasoner")
    replayer = models.get("replayer") or reasoner
    out = [
        rule_instruction_role(r),
        rule_max_tokens_field(r),
        rule_stream_usage(r),
        rule_thinking_format(r, bool(reasoner)),
        rule_reasoning_efforts(r, bool(reasoner)),
        rule_reasoning_off(r, bool(reasoner), reasoner),
        *rule_reasoning_off_always_on(r, models.get("always_on")),
        *rule_thinking_replay(r, bool(replayer)),
        rule_forced_tool_choice(r, reasoner),
        rule_json_schema(r),
        rule_user_field(r),
        *rule_conventions(),
    ]
    return out


def draft_preset(findings: list[Finding]) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    """The provider-wide knobs the findings set (never a needs-you value), and
    the per-model overrides, one entry per model prefix."""
    knobs: dict[str, Any] = {}
    overrides: dict[str, dict[str, Any]] = {}
    for f in findings:
        if f.status != NEEDS_YOU and f.value is not None:
            knobs[f.knob] = f.value
        if f.override and f.override[0]:
            overrides.setdefault(f.override[0], {}).update(f.override[1])
    return knobs, sorted(overrides.items())


# What a ratified preset holds that a survey cannot establish, by knob.
UNSURVEYABLE = {"user_field", "tool_result_media", "builtin_tools", "reasoning_efforts", "token_scoring", "routing", "extensions"}


def compare(findings: list[Finding], ratified: dict[str, Any]) -> list[dict[str, Any]]:
    """Draft against a ratified preset (a backtest): agree, equivalent, differ, or not surveyable."""
    by_knob: dict[str, Finding] = {}
    for f in findings:
        by_knob.setdefault(f.knob, f)  # the provider-wide finding comes first
    rows = []
    for knob in sorted(set(ratified) | {f.knob for f in findings if f.value is not None}):
        if knob == "model_overrides":
            continue
        want, f = ratified.get(knob), by_knob.get(knob)
        got = f.value if f else None
        if knob in UNSURVEYABLE:
            verdict = "not surveyable"
        elif got == want:
            verdict = "agree"
        elif f and want in f.also:
            verdict = "equivalent"
        elif f and f.status == NEEDS_YOU:
            verdict = "needs you"
        else:
            verdict = "differ"
        rows.append({"knob": knob, "ratified": want, "drafted": got, "verdict": verdict,
                     "status": f.status if f else "-", "note": f.note if f else ""})
    return rows


# ─── the candidate spec (research/providers/<id>/candidate.json) ─────

SPEC_DIALECTS = ("openai-chat",)  # the survey speaks the Chat Completions wire; other wires are follow-up work
MODEL_ROLES = ("plain", "reasoner", "off", "replayer", "always_on")


def validate_spec(spec: dict[str, Any]) -> list[str]:
    """Every problem with a candidate spec, as a sentence; [] when it can run."""
    problems: list[str] = []
    pid = spec.get("id")
    if not isinstance(pid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", pid or ""):
        problems.append("id: lower case, words joined by '-' (the lm15 provider string)")
    if not isinstance(spec.get("name"), str) or not spec.get("name"):
        problems.append("name: the provider's display name")
    if spec.get("dialect") not in SPEC_DIALECTS:
        problems.append(f"dialect: one of {', '.join(SPEC_DIALECTS)} (the wire the survey sends)")
    base = spec.get("base_url")
    if not isinstance(base, str) or not re.fullmatch(r"https://[^\s/?#@{}]+(?:/[^\s?#{}]*)?", base or "") or base.endswith("/"):
        problems.append("base_url: the documented https root without a trailing slash (…/v1); a URL with {placeholders} is a cloud door, not a survey candidate")
    if not isinstance(spec.get("env_key"), str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", spec.get("env_key") or ""):
        problems.append("env_key: the documented environment variable (UPPER_SNAKE)")
    models = spec.get("models")
    if not isinstance(models, dict):
        problems.append("models: an object of role -> model id")
    else:
        unknown = sorted(set(models) - set(MODEL_ROLES))
        if unknown:
            problems.append(f"models: unknown role(s) {unknown}; roles are {', '.join(MODEL_ROLES)}")
        if not isinstance(models.get("plain"), str) or not models.get("plain"):
            problems.append("models.plain: a non-reasoning instruct model (required)")
        for role in MODEL_ROLES:
            value = models.get(role)
            if value is not None and (not isinstance(value, str) or not value):
                problems.append(f"models.{role}: a model id or null")
    for key in ("console_url", "terms_url"):
        value = spec.get(key)
        if value is not None and (not isinstance(value, str) or not value.startswith("https://")):
            problems.append(f"{key}: an https URL or null")
    return problems


def compare_overrides(drafted: list[tuple[str, dict[str, Any]]], ratified: list) -> list[dict[str, Any]]:
    """Per-model knobs, matched when one prefix starts with the other (the
    survey names an exact model; a ratified rule may name its family)."""
    def related(a: str, b: str) -> bool:
        return a.startswith(b) or b.startswith(a)

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for rprefix, rknobs in ratified:
        for knob, value in rknobs.items():
            match = next(((p, k[knob]) for p, k in drafted if related(p, rprefix) and knob in k), None)
            if match:
                seen.add((match[0], knob))
            rows.append({"knob": knob, "ratified": f"`{rprefix}` = `{value}`",
                         "drafted": f"`{match[0]}` = `{match[1]}`" if match else "-",
                         "verdict": "agree" if match and match[1] == value else (
                             "not surveyable" if knob in UNSURVEYABLE else "differ" if match else "not drafted")})
    for p, k in drafted:
        for knob, value in k.items():
            if (p, knob) not in seen:
                rows.append({"knob": knob, "ratified": "-", "drafted": f"`{p}` = `{value}`", "verdict": "drafted only"})
    return rows


# ─── sweep: per-model knobs across many models (survey.py sweep) ─────

# mode -> (tool_choice, question); a forced call counts as honoured only if the
# model makes no call unprompted (control-auto) and the second try calls too
# (research/providers/deepinfra/tool_choice_survey.py, 2026-09-26).
SWEEP_TOOL_MODES = {
    "required": ("required", "Say ok."),
    "named": ({"type": "function", "function": {"name": "get_weather"}}, "Say ok."),
    "none": ("none", "What is the weather in Paris? Use the tool."),
    "control-auto": ("auto", "Say ok."),
    "required-2": ("required", "Say ok."),
}


def sweep_slug(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9.]+", "-", model).strip("-")


def tool_mode_verdict(mode: str, rec: dict | None) -> str:
    if rec is None:
        return "not sent"
    s = status(rec)
    if s is None:
        return "no answer"  # timed out or dropped: recorded, judged inconclusive
    if s != 200:
        return "server error" if (s or 0) >= 500 else "refused"
    called = tool_called(rec)
    if not called and finish(rec) == "length":
        return "cut short"  # the token budget ran out (often while reasoning): no answer to judge
    if mode == "control-auto":
        return "calls unprompted" if called else "no call"
    if mode == "none":
        if called:
            return "ignored"
        return "ignored" if re.search(r"get_weather|<function|\"name\"\s*:", content(rec)) else "honoured"
    return "honoured" if called else "ignored"


SWEEP_SEVERITY = ("fails", "ignores", "inconclusive", "refuses-loudly", "honours")


def sweep_worst(verdicts: list[tuple[str, str]]) -> tuple[str, str]:
    """Several samples of one model: the worst wins (one silent ignore is enough
    for MAP-8), and the detail lists every sample."""
    if not verdicts:
        return "not sent", ""
    worst = min(verdicts, key=lambda v: SWEEP_SEVERITY.index(v[0]) if v[0] in SWEEP_SEVERITY else len(SWEEP_SEVERITY))
    detail = worst[1] if len(verdicts) == 1 else f"{len(verdicts)} samples: " + "; ".join(v[0] for v in verdicts) + f" — worst: {worst[1]}"
    return worst[0], detail


def sweep_tool_choice(per_mode: dict[str, dict | None]) -> tuple[str, str]:
    """(verdict, detail): honours | ignores | refuses-loudly | fails | inconclusive."""
    v = {mode: tool_mode_verdict(mode, per_mode.get(f"sweep-{mode}")) for mode in SWEEP_TOOL_MODES}
    detail = ", ".join(f"{m} {v[m]}" for m in SWEEP_TOOL_MODES)
    forced = [v[m] for m in ("required", "named", "none", "required-2")]
    if "server error" in forced:
        return "fails", detail
    if "ignored" in forced:
        return "ignores", detail
    if v["control-auto"] == "calls unprompted" or "cut short" in forced or "no answer" in forced:
        return "inconclusive", detail
    if all(x == "honoured" for x in forced):
        return "honours", detail
    if all(x in ("honoured", "refused") for x in forced) and "refused" in forced:
        return "refuses-loudly", detail
    return "inconclusive", detail


def sweep_reasoning_off(rec: dict | None) -> tuple[str, str]:
    if rec is None:
        return "not sent", ""
    if loud(rec):
        return "refuses-loudly", say(rec)
    if ok(rec) and reasoned(rec):
        return "ignores", say(rec)
    if ok(rec):
        return "honours", say(rec)
    return "fails", say(rec)


def sweep_overrides(provider_forced: str | None, results: dict[str, dict[str, tuple[str, str]]]
                    ) -> tuple[list[tuple[str, dict[str, Any]]], list[str]]:
    """Per-model overrides relative to the provider-wide value, and the models
    left undecided. A provider that refuses a forced choice gets an allow-list
    of models that honour it; one that sends gets a deny-list of models that
    ignore it or fail on it (the DeepInfra and Together rules, 2026-09-26)."""
    overrides: list[tuple[str, dict[str, Any]]] = []
    undecided: list[str] = []
    for model, verdicts in results.items():
        knobs: dict[str, Any] = {}
        tool = verdicts.get("tool_choice", ("not sent", ""))[0]
        if provider_forced == "reject" and tool in ("honours", "refuses-loudly"):
            knobs["forced_tool_choice"] = "send"
        elif provider_forced != "reject" and tool in ("ignores", "fails"):
            knobs["forced_tool_choice"] = "reject"
        elif tool == "inconclusive":
            undecided.append(f"{model}: forced tool choice inconclusive ({verdicts['tool_choice'][1]})")
        if verdicts.get("reasoning_off", ("not sent", ""))[0] == "ignores":
            knobs["reasoning_off"] = "lowest"
        if knobs:
            overrides.append((model, knobs))
    return overrides, undecided
