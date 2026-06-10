#!/usr/bin/env python3
"""Language-neutral harness runner for the lm15 vet protocol.

Drives one vet shim subprocess (see harness/PROTOCOL.md and harness/shims.json)
over the JSONL pipe and performs ALL comparison harness-side, strictly:

- Strict typed deep-equality. ``true != 1``, ``1 != 1.0`` (single exception:
  int vs zero-fraction float inside ``usage`` fields, response/stream only).
- Absent, null, ``""``, ``[]``, ``{}`` are FIVE DIFFERENT VALUES everywhere.
- Auth headers are compared against the api_key the harness injected.
- Volatile paths (a case's ``"volatile"`` map) compare by presence + type only.

The shim only transforms; the harness never trusts it. Failures are reported
with the JSON path of the first difference — never papered over. This module
imports NOTHING from lm15: stdlib only.

Usage:
    python harness/check.py --shim python [--direction request|response|stream|error|serde|all]
                            [--case ID] [--report-dir harness/reports]
"""

from __future__ import annotations

import argparse
import base64
import datetime
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CONTRACT_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = CONTRACT_ROOT / "cases"
BODIES_DIR = CONTRACT_ROOT / "bodies"
ERRORS_DIR = CONTRACT_ROOT / "errors" / "cases"
GOLDENS_DIR = CONTRACT_ROOT / "goldens"
SERDE_FILE = CONTRACT_ROOT / "serde" / "canonical.json"
SHIMS_FILE = CONTRACT_ROOT / "harness" / "shims.json"
CHANGES_DIR = CONTRACT_ROOT / "changes"

DIRECTIONS = ("request", "response", "stream", "error", "serde")

# The api_key the harness injects into build_request; PROTOCOL.md requires the
# shim to use it verbatim and never read environment keys.
API_KEY = "test-key-123"

# Headers whose values carry the credential. Fixtures store the live key (or a
# $VAR placeholder / REDACTED), so these are the ONLY headers compared by
# format: the fixture supplies the shape (e.g. "Bearer <anything>"), the
# harness supplies the key. Everything else is verbatim.
AUTH_HEADERS = frozenset({"authorization", "x-api-key", "x-goog-api-key"})

# Transport noise dropped from BOTH sides before header comparison. This list
# is fixed; widening it weakens the oracle.
DROP_HEADERS = frozenset({"user-agent", "accept", "accept-encoding", "content-length", "host"})

VOLATILE_CLASSES = frozenset({"id", "timestamp", "usage-count", "duration"})

JsonObject = dict[str, Any]
PathSegs = tuple[Any, ...]  # str keys and int indexes

_ABSENT = object()  # absent is its own value, distinct from null/""/[]/{}


# ─── Strict comparison ───────────────────────────────────────────────

@dataclass(frozen=True)
class Diff:
    path: str
    expected: Any
    actual: Any
    note: str

    def to_dict(self) -> JsonObject:
        return {
            "path": self.path,
            "expected": "<absent>" if self.expected is _ABSENT else self.expected,
            "actual": "<absent>" if self.actual is _ABSENT else self.actual,
            "note": self.note,
        }


def render_path(segs: PathSegs) -> str:
    out = "$"
    for seg in segs:
        out += f"[{seg}]" if isinstance(seg, int) else f".{seg}"
    return out


def json_type(value: Any) -> str:
    if value is _ABSENT:
        return "absent"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _volatile_class(segs: PathSegs, volatile: JsonObject) -> str | None:
    """Match a diff path against a case's volatile map.

    Volatile keys are JSON paths; "$." prefixes and the comparison root
    ("canonical_response.") are optional so authors can write either form.
    """
    rendered = render_path(segs)
    candidates = {rendered, rendered[2:] if rendered.startswith("$.") else rendered}
    if rendered.startswith("$.canonical_response."):
        candidates.add(rendered[len("$.canonical_response."):])
    for key, cls in volatile.items():
        normalized = key[2:] if key.startswith("$.") else key
        if normalized in candidates or key in candidates:
            return str(cls) if cls in VOLATILE_CLASSES else None
    return None


def first_difference(
    expected: Any,
    actual: Any,
    segs: PathSegs = (),
    *,
    volatile: JsonObject | None = None,
    usage_int_float: bool = False,
) -> Diff | None:
    """Strict typed deep-equality; returns the first difference or None.

    Absent, null, "", [], {} are five different values. true != 1, 1 != 1.0
    — except int vs zero-fraction float under a `usage` segment when
    `usage_int_float` is set (JS/Julia JSON emitters; scope fixed per
    PROTOCOL.md, never widened).
    """
    if volatile:
        cls = _volatile_class(segs, volatile)
        if cls is not None:
            if expected is _ABSENT or actual is _ABSENT:
                return Diff(render_path(segs), expected, actual, f"volatile({cls}): presence required")
            exp_t, act_t = json_type(expected), json_type(actual)
            number = {"integer", "float"}
            if exp_t != act_t and not (exp_t in number and act_t in number):
                return Diff(render_path(segs), expected, actual, f"volatile({cls}): type mismatch {exp_t} != {act_t}")
            return None

    if expected is _ABSENT:
        return Diff(render_path(segs), expected, actual, "unexpected key (absent in fixture)")
    if actual is _ABSENT:
        return Diff(render_path(segs), expected, actual, "missing key (absent in shim output)")

    exp_t, act_t = json_type(expected), json_type(actual)
    if exp_t != act_t:
        if (
            usage_int_float
            and {exp_t, act_t} == {"integer", "float"}
            and "usage" in segs
            and float(expected) == float(actual)
            and float(expected).is_integer()
        ):
            return None
        return Diff(render_path(segs), expected, actual, f"type mismatch: {exp_t} != {act_t}")

    if isinstance(expected, dict):
        for key in expected:
            diff = first_difference(
                expected[key], actual.get(key, _ABSENT), segs + (key,),
                volatile=volatile, usage_int_float=usage_int_float,
            )
            if diff is not None:
                return diff
        for key in actual:
            if key not in expected:
                return first_difference(_ABSENT, actual[key], segs + (key,),
                                        volatile=volatile, usage_int_float=usage_int_float)
        return None

    if isinstance(expected, list):
        if len(expected) != len(actual):
            return Diff(render_path(segs), expected, actual,
                        f"array length: {len(expected)} != {len(actual)}")
        for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
            diff = first_difference(exp_item, act_item, segs + (i,),
                                    volatile=volatile, usage_int_float=usage_int_float)
            if diff is not None:
                return diff
        return None

    if expected != actual:
        return Diff(render_path(segs), expected, actual, "value mismatch")
    return None


# ─── Shim subprocess ─────────────────────────────────────────────────

class HarnessError(RuntimeError):
    """The shim broke the protocol (crash, bad framing) — not a case failure."""


class Shim:
    """One shim process per run; ops streamed over the JSONL pipe."""

    def __init__(self, name: str, command: list[str], cwd: Path) -> None:
        self.name = name
        self.command = list(command)
        self.sandboxed = _unshare_available()
        argv = (["unshare", "-rn"] if self.sandboxed else []) + self.command
        self._next_id = 0
        self.proc = subprocess.Popen(
            argv,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def call(self, op: str, **fields: Any) -> JsonObject:
        self._next_id += 1
        req_id = f"{op}#{self._next_id}"
        request = {"op": op, "id": req_id, **fields}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        try:
            self.proc.stdin.write(json.dumps(request) + "\n")
            self.proc.stdin.flush()
            line = self.proc.stdout.readline()
        except (BrokenPipeError, OSError) as exc:
            raise HarnessError(f"shim pipe broke during {req_id}: {exc}; stderr: {self._stderr_tail()}")
        if not line:
            raise HarnessError(f"shim exited mid-stream at {req_id}; stderr: {self._stderr_tail()}")
        try:
            reply = json.loads(line)
        except json.JSONDecodeError as exc:
            raise HarnessError(f"shim emitted non-JSON for {req_id}: {line!r} ({exc})")
        if not isinstance(reply, dict) or reply.get("id") != req_id:
            raise HarnessError(f"shim broke framing: sent {req_id}, got {reply!r}")
        return reply

    def close(self) -> None:
        if self.proc.stdin is not None:
            self.proc.stdin.close()
        self.proc.wait(timeout=30)

    def _stderr_tail(self) -> str:
        if self.proc.stderr is None:
            return ""
        try:
            return self.proc.stderr.read()[-2000:]
        except Exception:
            return "<unreadable>"


def _unshare_available() -> bool:
    if shutil.which("unshare") is None:
        return False
    try:
        probe = subprocess.run(["unshare", "-rn", "true"], capture_output=True, timeout=10)
    except Exception:
        return False
    return probe.returncode == 0


def load_shim(name: str) -> Shim:
    registry = json.loads(SHIMS_FILE.read_text())
    entry = registry.get(name)
    if not isinstance(entry, dict):
        known = sorted(k for k in registry if not k.startswith("_"))
        raise HarnessError(f"unknown shim {name!r}; registered: {known} (see {SHIMS_FILE})")
    cwd = (CONTRACT_ROOT / entry["cwd"]).resolve()
    if not cwd.is_dir():
        raise HarnessError(f"shim {name!r} cwd does not exist: {cwd}")
    return Shim(name, entry["command"], cwd)


# ─── Corpus loading ──────────────────────────────────────────────────

def load_wire_cases() -> list[JsonObject]:
    return [json.loads(path.read_text()) for path in sorted(CASES_DIR.glob("*/*.json"))]


def load_error_cases() -> list[JsonObject]:
    cases: list[JsonObject] = []
    for path in sorted(ERRORS_DIR.glob("*.json")):
        cases.extend(json.loads(path.read_text())["cases"])
    return cases


def load_serde_cases() -> list[JsonObject]:
    return list(json.loads(SERDE_FILE.read_text())["cases"])


def pinned_body(case: JsonObject) -> bytes:
    return (BODIES_DIR / case["id"] / case["pinned_body"]).read_bytes()


def looks_like_sse(body: bytes) -> bool:
    head = body.lstrip()[:512]
    return head.startswith(b"event:") or head.startswith(b"data:") or b"\ndata:" in head


def is_stream_case(case: JsonObject) -> bool:
    """Case "stream" flag, falling back to a body sniff for unflagged SSE."""
    if case.get("stream") is True:
        return True
    if "pinned_body" not in case:
        return False
    try:
        return looks_like_sse(pinned_body(case))
    except OSError:
        return False


# ─── Results and reports ─────────────────────────────────────────────

@dataclass
class CaseResult:
    case_id: str
    status: str  # "pass" | "fail" | "skip"
    reason: str | None = None
    diff: Diff | None = None

    def to_dict(self) -> JsonObject:
        out: JsonObject = {"id": self.case_id, "status": self.status}
        if self.reason:
            out["reason"] = self.reason
        if self.diff is not None:
            out["first_difference"] = self.diff.to_dict()
        return out


@dataclass
class DirectionReport:
    direction: str
    results: list[CaseResult] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        counts = {"pass": 0, "fail": 0, "skip": 0}
        for result in self.results:
            counts[result.status] += 1
        return counts


def shim_reply_failure(case_id: str, reply: JsonObject) -> CaseResult:
    error = reply.get("error") or {}
    return CaseResult(
        case_id, "fail",
        reason=f"shim error: {error.get('type', '?')}: {error.get('message', '?')}",
    )


def write_reports(report: DirectionReport, shim: Shim, capabilities: JsonObject, report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "direction": report.direction,
        "shim": shim.name,
        "command": shim.command,
        "sandboxed": shim.sandboxed,
        "capabilities": capabilities,
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "summary": report.counts,
        "total": len(report.results),
        "results": [r.to_dict() for r in report.results],
    }
    json_path = report_dir / f"{report.direction}.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    counts = report.counts
    lines = [
        f"# vet harness — {report.direction} ({shim.name})",
        "",
        f"- generated: {payload['generated']}",
        f"- shim: `{' '.join(shim.command)}` (sandboxed: {shim.sandboxed})",
        f"- impl: {capabilities.get('language', '?')} {capabilities.get('impl_version', '?')}",
        f"- **pass {counts['pass']} / fail {counts['fail']} / skip {counts['skip']}** of {len(report.results)}",
        "",
    ]
    failures = [r for r in report.results if r.status == "fail"]
    if failures:
        lines.append("## Failures")
        lines.append("")
        for result in failures:
            lines.append(f"### {result.case_id}")
            if result.reason:
                lines.append(f"- {result.reason}")
            if result.diff is not None:
                lines.append(f"- path: `{result.diff.path}` — {result.diff.note}")
                lines.append(f"- expected: `{_short(result.diff.expected)}`")
                lines.append(f"- actual:   `{_short(result.diff.actual)}`")
            lines.append("")
    skips = [r for r in report.results if r.status == "skip"]
    if skips:
        lines.append("## Skips")
        lines.append("")
        for result in skips:
            lines.append(f"- {result.case_id}: {result.reason}")
        lines.append("")
    (report_dir / f"{report.direction}.md").write_text("\n".join(lines))


def _short(value: Any, limit: int = 200) -> str:
    if value is _ABSENT:
        return "<absent>"
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return text if len(text) <= limit else text[: limit - 1] + "…"


# ─── Direction: request ──────────────────────────────────────────────

def split_url(url: str) -> tuple[str, dict[str, str]]:
    import urllib.parse

    parsed = urllib.parse.urlparse(url)
    params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    base = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
    return base, params


def expected_wire_request(case: JsonObject) -> JsonObject:
    """The fixture's recorded wire request, shaped like build_request output.

    Header names are lowercased (PROTOCOL.md mandates lowercase on the shim
    side; captures store them as sent). Auth-header VALUES are rewritten to
    the harness-injected api_key, preserving the fixture's format (a
    "Bearer <anything>" fixture expects "Bearer test-key-123"). Transport
    noise (DROP_HEADERS) is removed. Nothing else is touched: empty
    containers, nulls, and every body byte compare strictly.
    """
    req = case["request"]
    url, params = split_url(str(req["url"]))
    if isinstance(req.get("params"), dict):
        params.update({str(k): str(v) for k, v in req["params"].items()})

    headers: dict[str, str] = {}
    for name, value in req.get("headers", {}).items():
        lower = str(name).lower()
        if lower in DROP_HEADERS:
            continue
        if lower in AUTH_HEADERS:
            value = f"Bearer {API_KEY}" if str(value).startswith("Bearer ") else API_KEY
        headers[lower] = value

    return {
        "method": req.get("method", "POST"),
        "url": url,
        "params": params,
        "headers": headers,
        # A fixture with no body records "no body sent": the shim's protocol
        # envelope expresses that as body: null.
        "body": req.get("body", None),
    }


def actual_wire_request(result: JsonObject) -> JsonObject:
    """The shim's build_request output, with DROP_HEADERS removed.

    No other normalization: names arrive lowercased per PROTOCOL.md, and a
    non-lowercase name is a real difference. body_b64 (the documented
    extension for non-JSON bodies) is kept so it surfaces as an unexpected
    key against JSON-body fixtures.
    """
    out = {key: result[key] for key in result}
    headers = out.get("headers")
    if isinstance(headers, dict):
        out["headers"] = {k: v for k, v in headers.items() if str(k).lower() not in DROP_HEADERS}
    return out


def run_request_direction(shim: Shim, case_filter: str | None) -> DirectionReport:
    report = DirectionReport("request")
    for case in load_wire_cases():
        case_id = case["id"]
        if case_filter and case_id != case_filter:
            continue
        if "canonical_request" not in case:
            report.results.append(CaseResult(case_id, "skip", reason="no canonical_request attached"))
            continue
        reply = shim.call(
            "build_request",
            provider=case["provider"],
            canonical_request=case["canonical_request"],
            stream=bool(case.get("stream", False)),
            api_key=API_KEY,
        )
        if not reply.get("ok"):
            report.results.append(shim_reply_failure(case_id, reply))
            continue
        expected = expected_wire_request(case)
        actual = actual_wire_request(reply["result"])
        volatile = case.get("volatile") or {}
        diff = None
        for key in ("method", "url", "params", "headers", "body"):
            diff = first_difference(
                expected.get(key, _ABSENT), actual.get(key, _ABSENT), (key,), volatile=volatile
            )
            if diff is not None:
                break
        if diff is None:
            for key in actual:
                if key not in expected:
                    diff = first_difference(_ABSENT, actual[key], (key,), volatile=volatile)
                    break
        if diff is None:
            report.results.append(CaseResult(case_id, "pass"))
        else:
            report.results.append(CaseResult(case_id, "fail", diff=diff))
    return report


# ─── Direction: serde ────────────────────────────────────────────────

def is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def omission_only(original: Any, roundtripped: Any) -> bool:
    """True iff `roundtripped` is `original` minus dropped EMPTY dict fields.

    This is the structural signature of docs/serde-rules.md's omission rule
    (a typed serializer omits its own null/""/[]/{} optional fields). The
    harness cannot tell typed levels from opaque payloads without lm15
    knowledge, so a match is only a CANDIDATE for canonicalization — the
    human reviews the proposal against the spec.
    """
    if isinstance(original, dict) and isinstance(roundtripped, dict):
        for key, value in original.items():
            if key in roundtripped:
                if not omission_only(value, roundtripped[key]):
                    return False
            elif not is_empty(value):
                return False
        return all(key in original for key in roundtripped)
    if isinstance(original, list) and isinstance(roundtripped, list):
        if len(original) != len(roundtripped):
            return False
        return all(omission_only(o, r) for o, r in zip(original, roundtripped))
    return first_difference(original, roundtripped) is None


SERDE_CHANGES_ENTRY = CHANGES_DIR / "2026-06-10-serde-canonical-form.md"


def write_canonicalization_proposal(flagged: list[JsonObject], report_dir: Path) -> None:
    """Non-canonical fixture values found: propose, never silently normalize.

    The runner keeps comparing against the ORIGINAL serde/canonical.json (red
    is honest). The proposal and the changes/ DRAFT exist so a human can
    decide at freeze time, per AUTHORITY.md (canonical fixtures change only
    with a spec citation).
    """
    corpus = json.loads(SERDE_FILE.read_text())
    by_id = {entry["id"]: entry for entry in flagged}
    for case in corpus["cases"]:
        entry = by_id.get(case["id"])
        if entry is not None:
            case["value"] = entry["proposed_value"]
            case["canonicalization"] = {
                "status": "PROPOSED",
                "rule": "docs/serde-rules.md — omission rule (typed serializers omit their own empty optional fields)",
                "original_value": entry["original_value"],
            }
    report_dir.mkdir(parents=True, exist_ok=True)
    proposal_path = report_dir / "serde-canonicalization-proposal.json"
    proposal_path.write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + "\n")

    if not SERDE_CHANGES_ENTRY.exists():
        ids = "\n".join(f"- `{entry['id']}`" for entry in flagged)
        SERDE_CHANGES_ENTRY.write_text(
            "# DRAFT — serde fixtures not in canonical form (omission rule)\n"
            "\n"
            "Status: DRAFT — pending human review at freeze time. The harness\n"
            "(`harness/check.py --direction serde`) keeps comparing against the\n"
            "ORIGINAL `serde/canonical.json`; the affected cases stay RED until a\n"
            "reviewed commit lands. No fixture was edited.\n"
            "\n"
            "Strict round-trip comparison found fixture values that differ from\n"
            "their round-tripped form ONLY by explicit empty optional fields at a\n"
            "typed object's own level — values that `docs/serde-rules.md` (the\n"
            "omission rule, normative per AUTHORITY.md canonical-facts precedence)\n"
            "says have exactly one canonical wire form with those fields omitted.\n"
            "\n"
            "Affected cases:\n"
            f"{ids}\n"
            "\n"
            "Proposed canonicalized corpus: `harness/reports/serde-canonicalization-proposal.json`\n"
            "(regenerated by the runner; harness/reports/ is gitignored). Caveat:\n"
            "the structural check cannot distinguish typed levels from opaque\n"
            "payloads (rule 3: opaque payloads are never mutated), so each case\n"
            "must be reviewed against the spec before the fixture changes, with\n"
            "this entry updated to cite the rule per AUTHORITY.md.\n"
        )


def run_serde_direction(shim: Shim, case_filter: str | None, report_dir: Path) -> DirectionReport:
    report = DirectionReport("serde")
    flagged: list[JsonObject] = []
    for case in load_serde_cases():
        case_id = case["id"]
        if case_filter and case_id != case_filter:
            continue
        reply = shim.call("serde_roundtrip", kind=case["kind"], value=case["value"])
        if not reply.get("ok"):
            report.results.append(shim_reply_failure(case_id, reply))
            continue
        roundtripped = reply["result"].get("value", _ABSENT)
        diff = first_difference(case["value"], roundtripped)
        if diff is None:
            report.results.append(CaseResult(case_id, "pass"))
            continue
        reason = None
        if roundtripped is not _ABSENT and omission_only(case["value"], roundtripped):
            reason = "fixture value not in canonical form (omission rule) — see canonicalization proposal"
            flagged.append({"id": case_id, "original_value": case["value"], "proposed_value": roundtripped})
        report.results.append(CaseResult(case_id, "fail", reason=reason, diff=diff))
    if flagged:
        write_canonicalization_proposal(flagged, report_dir)
    return report


# ─── Direction: error ────────────────────────────────────────────────

def run_error_direction(shim: Shim, case_filter: str | None) -> DirectionReport:
    report = DirectionReport("error")
    for case in load_error_cases():
        case_id = case["id"]
        if case_filter and case_id != case_filter:
            continue
        body = case["body"]
        body_text = body if isinstance(body, str) else json.dumps(body)
        reply = shim.call(
            "normalize_error", provider=case["provider"], status=int(case["status"]), body_text=body_text
        )
        if not reply.get("ok"):
            report.results.append(shim_reply_failure(case_id, reply))
            continue
        result = reply["result"]
        expected = case["expected"]
        # class/code/provider_code compare strictly (every current fixture
        # specifies all three); message only when the fixture pins one.
        diff = None
        for key in ("class", "code", "provider_code", "message"):
            if key not in expected:
                continue
            diff = first_difference(expected[key], result.get(key, _ABSENT), (key,))
            if diff is not None:
                break
        if diff is None:
            report.results.append(CaseResult(case_id, "pass"))
        else:
            report.results.append(CaseResult(case_id, "fail", diff=diff))
    return report


# ─── Directions: response / stream ───────────────────────────────────

def run_parse_direction(shim: Shim, direction: str, case_filter: str | None) -> DirectionReport:
    """parse_response (direction="response") or replay_stream ("stream").

    Compares against goldens/<case_id>.json: {"canonical_response": ...} plus
    optional "events" for stream cases. No golden yet → honest "no-golden"
    skip (counted, never a pass). Any non-empty "unmapped" fails the case.
    """
    want_stream = direction == "stream"
    report = DirectionReport(direction)
    for case in load_wire_cases():
        case_id = case["id"]
        if case_filter and case_id != case_filter:
            continue
        if "pinned_body" not in case:
            report.results.append(CaseResult(case_id, "skip", reason="no pinned_body"))
            continue
        if is_stream_case(case) != want_stream:
            continue
        golden_path = GOLDENS_DIR / f"{case_id}.json"
        if not golden_path.exists():
            report.results.append(CaseResult(case_id, "skip", reason="no-golden"))
            continue
        if "canonical_request" not in case:
            report.results.append(CaseResult(case_id, "skip", reason="no canonical_request attached"))
            continue
        golden = json.loads(golden_path.read_text())
        body_b64 = base64.b64encode(pinned_body(case)).decode("ascii")
        if want_stream:
            reply = shim.call(
                "replay_stream",
                provider=case["provider"],
                canonical_request=case["canonical_request"],
                body_b64=body_b64,
            )
        else:
            reply = shim.call(
                "parse_response",
                provider=case["provider"],
                canonical_request=case["canonical_request"],
                status=int(case.get("expect", {}).get("status", 200)),
                body_b64=body_b64,
            )
        if not reply.get("ok"):
            report.results.append(shim_reply_failure(case_id, reply))
            continue
        result = reply["result"]
        unmapped = result.get("unmapped")
        if unmapped:
            report.results.append(
                CaseResult(case_id, "fail", reason=f"unmapped provider fields: {unmapped}")
            )
            continue
        volatile = case.get("volatile") or {}
        diff = first_difference(
            golden["canonical_response"],
            result.get("canonical_response", _ABSENT),
            ("canonical_response",),
            volatile=volatile,
            usage_int_float=True,
        )
        if diff is None and want_stream and "events" in golden:
            diff = first_difference(
                golden["events"], result.get("events", _ABSENT), ("events",),
                volatile=volatile, usage_int_float=True,
            )
        if diff is None:
            report.results.append(CaseResult(case_id, "pass"))
        else:
            report.results.append(CaseResult(case_id, "fail", diff=diff))
    return report


# ─── Main ────────────────────────────────────────────────────────────

def run_direction(shim: Shim, direction: str, case_filter: str | None, report_dir: Path) -> DirectionReport:
    if direction == "request":
        return run_request_direction(shim, case_filter)
    if direction == "serde":
        return run_serde_direction(shim, case_filter, report_dir)
    if direction == "error":
        return run_error_direction(shim, case_filter)
    if direction in ("response", "stream"):
        return run_parse_direction(shim, direction, case_filter)
    raise ValueError(f"unknown direction: {direction}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--shim", required=True, help="shim name from harness/shims.json")
    parser.add_argument("--direction", default="all", choices=DIRECTIONS + ("all",))
    parser.add_argument("--case", default=None, help="run only the case with this id")
    parser.add_argument(
        "--report-dir", default="harness/reports",
        help="report directory (relative paths resolve against the lm15-contract root)",
    )
    args = parser.parse_args(argv)

    report_dir = Path(args.report_dir)
    if not report_dir.is_absolute():
        report_dir = CONTRACT_ROOT / report_dir

    directions = list(DIRECTIONS) if args.direction == "all" else [args.direction]

    try:
        shim = load_shim(args.shim)
    except HarnessError as exc:
        print(f"harness error: {exc}", file=sys.stderr)
        return 2

    failed = False
    try:
        capabilities_reply = shim.call("capabilities")
        capabilities = capabilities_reply.get("result", {}) if capabilities_reply.get("ok") else {}
        if not shim.sandboxed:
            print("warning: unshare -rn unavailable — shim runs WITHOUT no-network enforcement", file=sys.stderr)
        for direction in directions:
            report = run_direction(shim, direction, args.case, report_dir)
            write_reports(report, shim, capabilities, report_dir)
            counts = report.counts
            print(
                f"{direction:>8}: pass {counts['pass']:3d}  fail {counts['fail']:3d}  "
                f"skip {counts['skip']:3d}  (report: {report_dir / (direction + '.json')})"
            )
            if counts["fail"]:
                failed = True
    except HarnessError as exc:
        print(f"harness error: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            shim.close()
        except Exception:
            pass

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
