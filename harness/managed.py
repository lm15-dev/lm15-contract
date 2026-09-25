"""The ``managed`` direction: managed authentication (AUTH-12–26) run end to end.

Each case in ``auth/managed/runs/*.json`` is one sandboxed program run: an
initial credential store, an environment, a scripted UI, a scripted auth
server and a list of public operations (login, configure, status, logout,
request-time resolution, the managed doctor, ...). The shim executes it
with every seam injected (``op: managed_run``, PROTOCOL.md § managed) and
returns what happened: one outcome per step, the ordered trace of prompts,
notices, auth HTTP requests and waits, and the store file afterwards.

The harness compares all three strictly after a fixed normalization:

- random identifiers (``cn_…`` connection ids, ``at_…`` attempt ids) become
  ``cn#1``, ``cn#2``, … in order of first appearance across the reply;
- the random OAuth values (``state``, ``code_challenge``, ``code_verifier``)
  are checked for their protocol relations first — the challenge is the
  S256 of the verifier sent later, the state sent to the token endpoint is
  the state in the authorization URL — then replaced by ``<random>``;
- numbers compare by value (``3600`` equals ``3600.0``): the store is JSON
  written by four languages, and JavaScript has one number type.

Secrecy (AUTH-21) is checked before normalization: the case's sentinel may
appear only in the private channels (auth HTTP bodies, the store file and a
``request_auth`` credential value), never in a step's public outcome, an
error, a prompt or a notice.

This module imports nothing from lm15.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

RUNS_DIR = Path(__file__).resolve().parent.parent / "auth" / "managed" / "runs"

_ID = re.compile(r"\b(cn|at)_[A-Za-z0-9_-]{8,}")
_RANDOM_PARAMS = ("state", "code_challenge", "code_verifier")


def load_runs() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for case in data["cases"]:
            case = dict(case)
            case["_file"] = path.name
            case.setdefault("sentinel", data.get("sentinel", "PRIVATE-MANAGED-TOKEN"))
            cases.append(case)
    return cases


# ─── normalization ───────────────────────────────────────────────────


def _numbers(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {k: _numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_numbers(v) for v in value]
    return value


def _rename_ids(value: Any, table: dict[str, str]) -> Any:
    if isinstance(value, str):
        def swap(match: re.Match[str]) -> str:
            raw = match.group(0)
            if raw not in table:
                kind = match.group(1)
                table[raw] = f"{kind}#{sum(1 for v in table.values() if v.startswith(kind + '#')) + 1}"
            return table[raw]
        return _ID.sub(swap, value)
    if isinstance(value, dict):
        # Sorted traversal: a store written with sorted keys (Go) and one
        # written in insertion order number their ids identically.
        renamed = {}
        for k in sorted(value):
            renamed[_rename_ids(k, table)] = _rename_ids(value[k], table)
        return renamed
    if isinstance(value, list):
        return [_rename_ids(v, table) for v in value]
    return value


def _s256(verifier: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")


def _random_query(url: str) -> tuple[str, dict[str, str]]:
    """The URL with its random parameters replaced, and their values."""
    split = urlsplit(url)
    params = parse_qsl(split.query, keep_blank_values=True)
    found = {k: v for k, v in params if k in _RANDOM_PARAMS}
    kept = [(k, "<random>" if k in _RANDOM_PARAMS else v) for k, v in params]
    return urlunsplit((split.scheme, split.netloc, split.path, urlencode(kept), split.fragment)), found


def check_oauth_relations(events: list[dict[str, Any]]) -> str | None:
    """PKCE and state, checked on the real values before they are masked.
    Returns a reason when a relation is broken."""
    issued: dict[str, str] = {}
    for event in events:
        if "step" in event:
            issued = {}
        notice = event.get("notice")
        if isinstance(notice, dict) and notice.get("type") == "auth_url":
            _, found = _random_query(str(notice.get("url", "")))
            issued = found
        http = event.get("http")
        if isinstance(http, dict) and isinstance(http.get("body"), dict):
            body = http["body"]
            verifier = body.get("code_verifier")
            challenge = issued.get("code_challenge")
            # A device flow can hand back a provider-made verifier (ChatGPT's
            # device authorization): the relation binds only when this attempt
            # issued a challenge itself.
            if isinstance(verifier, str) and challenge is not None:
                if _s256(verifier) != challenge:
                    return "PKCE broken: the code_challenge in the authorization URL is not S256(code_verifier)"
                if not re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", verifier):
                    return "PKCE verifier is not 43-128 unreserved characters (RFC 7636 §4.1)"
            state = body.get("state")
            if isinstance(state, str) and issued.get("state") is not None and state != issued["state"]:
                return "the state sent to the token endpoint is not the authorization URL's state"
    for key, value in issued.items():
        if key == "state" and len(value) < 22:
            return "the authorization state carries fewer than 128 bits (22 base64url characters)"
    return None


def _mask_random(value: Any) -> Any:
    """Mask the random OAuth values where OAuth puts them: auth HTTP bodies
    and authorization URLs in notices. A slot's ``state`` (ready, ...) is data."""
    if isinstance(value, list):
        return [_mask_random(v) for v in value]
    if not isinstance(value, dict):
        return value
    out = dict(value)
    http = out.get("http")
    if isinstance(http, dict):
        http = dict(http)
        if isinstance(http.get("body"), dict):
            http["body"] = {k: ("<random>" if k in _RANDOM_PARAMS and isinstance(v, str) else v)
                            for k, v in http["body"].items()}
        if isinstance(http.get("url"), str) and "?" in http["url"]:
            http["url"] = _random_query(http["url"])[0]
        out["http"] = http
    notice = out.get("notice")
    if isinstance(notice, dict) and isinstance(notice.get("url"), str) and "?" in notice["url"]:
        out["notice"] = {**notice, "url": _random_query(notice["url"])[0]}
    return out


def normalize(result: dict[str, Any]) -> dict[str, Any]:
    table: dict[str, str] = {}
    out = {
        "steps": _rename_ids(result.get("steps"), table),
        "events": _rename_ids(result.get("events"), table),
        "store": _rename_ids(result.get("store"), table),
    }
    out["events"] = _mask_random(out["events"])
    return _numbers(out)


# ─── secrecy ─────────────────────────────────────────────────────────


def secrecy_violation(result: dict[str, Any], sentinel: str) -> str | None:
    steps = result.get("steps") or []
    for index, step in enumerate(steps):
        public = step
        if isinstance(step, dict) and step.get("ok") and isinstance(step.get("value"), dict) \
                and "credential" in step["value"]:
            public = {**step, "value": {**step["value"], "credential": None}}
        if sentinel in json.dumps(public, ensure_ascii=False):
            return f"AUTH-21: the sentinel appears in the public outcome of step {index}"
    for index, event in enumerate(result.get("events") or []):
        if "http" in event:
            continue  # the private request is the one place a token must go
        if sentinel in json.dumps(event, ensure_ascii=False):
            return f"AUTH-21: the sentinel appears in trace event {index} ({next(iter(event))})"
    return None


# ─── the direction ───────────────────────────────────────────────────


def shim_fields(case: dict[str, Any], tmp: Path) -> dict[str, Any]:
    home = Path(tempfile.mkdtemp(prefix="home-", dir=tmp))
    store_path = home / ".config" / "lm15" / "credentials.json"
    store_path.parent.mkdir(parents=True, exist_ok=True)
    initial = case.get("store")
    if isinstance(initial, dict) and "raw" in initial:
        store_path.write_text(initial["raw"], encoding="utf-8")
    elif isinstance(initial, dict) and "document" in initial:
        store_path.write_text(json.dumps(initial["document"], indent=2), encoding="utf-8")
    env = {k: v for k, v in (case.get("env") or {}).items()}
    env["HOME"] = str(home)
    env["LM15_CREDENTIALS_PATH"] = str(store_path)
    return {
        "store_path": str(store_path),
        "home": str(home),
        "env": env,
        "clock_ms": case.get("clock_ms", 1790000000000),
        "sentinel": case["sentinel"],
        "http": case.get("http", []),
        "ui": case.get("ui", []),
        "steps": case["steps"],
    }


def run_managed_direction(shim: Any, case_filter: str | None, *, report_factory: Callable[[str], Any],
                          case_result: Callable[..., Any], first_difference: Callable[..., Any],
                          shim_reply_failure: Callable[..., Any]) -> Any:
    report = report_factory("managed")
    with tempfile.TemporaryDirectory(prefix="lm15-managed-") as tmp_name:
        tmp = Path(tmp_name)
        for case in load_runs():
            case_id = case["id"]
            if case_filter and case_id != case_filter:
                continue
            fields = shim_fields(case, tmp)
            reply = shim.call("managed_run", **fields)
            if not reply.get("ok"):
                report.results.append(shim_reply_failure(case_id, reply))
                continue
            result = reply["result"]
            violation = secrecy_violation(result, fields["sentinel"])
            if violation:
                report.results.append(case_result(case_id, "fail", reason=violation))
                continue
            broken = check_oauth_relations(result.get("events") or [])
            if broken:
                report.results.append(case_result(case_id, "fail", reason=broken))
                continue
            actual = normalize(result)
            expect = _numbers(case["expect"])
            want = {key: expect[key] for key in ("steps", "events", "store") if key in expect}
            got = {key: actual.get(key) for key in want}
            diff = first_difference(want, got)
            report.results.append(case_result(case_id, "pass") if diff is None else case_result(case_id, "fail", diff=diff))
    return report
