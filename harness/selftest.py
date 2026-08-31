#!/usr/bin/env python3
"""Mutation self-test: prove the harness comparator actually catches drift.

Runs harness/check.py's comparison machinery against harness/fake_shim.py — a
shim that echoes the recorded-correct outputs (wire fixtures, goldens/, error
expectations) except for one injected mutation — and FAILS unless:

1. the unmutated echo (--mutation none) is fully green in every direction
   (so any red below is attributable to the mutation, not broken plumbing), and
2. EVERY mutation turns its target case red, with the first-difference
   reported at the mutated path.

The mutation classes pin the comparator's teeth: tool-name drift, text
corruption, absent-vs-empty conflation, usage arithmetic, event loss,
bool/int conflation, auth-chain state drift, and AUTH-5 sentinel leakage. A comparator weakened enough to miss any of them fails
this script, and with it CI (.github/workflows/contract.yml). This needs only
the contract repo — the fake shim reads fixtures and goldens, never lm15.

Usage: selftest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS_DIR))

import check


def fake_shim(mutation: str, target: str | None = None) -> check.Shim:
    command = [sys.executable, str(HARNESS_DIR / "fake_shim.py"), "--mutation", mutation]
    if target is not None:
        command += ["--target", target]
    return check.Shim(f"fake[{mutation}]", command, check.CONTRACT_ROOT)


def golden_cases() -> list[tuple[dict, dict]]:
    out = []
    for case in check.load_wire_cases():
        if "canonical_request" in case and "pinned_body" in case and check.golden_path(case).exists():
            out.append((case, json.loads(check.golden_path(case).read_text())))
    return out


def _contains(node, predicate) -> bool:
    if isinstance(node, dict):
        return predicate(node) or any(_contains(v, predicate) for v in node.values())
    if isinstance(node, list):
        return any(_contains(v, predicate) for v in node)
    return False


def _has_bool(node) -> bool:
    if isinstance(node, bool):
        return True
    if isinstance(node, dict):
        return any(_has_bool(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_bool(v) for v in node)
    return False


def pick_targets() -> dict[str, tuple[str, str]]:
    """mutation -> (direction, target case id); fails loudly if any target is missing."""
    cases = golden_cases()
    responses = [(c, g) for c, g in cases if not check.is_stream_case(c)]
    streams = [(c, g) for c, g in cases if check.is_stream_case(c)]

    def first(pairs, predicate, what: str) -> str:
        for case, golden in pairs:
            if predicate(case, golden):
                return case["id"]
        raise SystemExit(f"selftest: no target case for {what} — corpus/goldens too thin to self-test")

    targets = {
        "wrong_tool_name": ("response", first(
            responses,
            lambda c, g: _contains(g["canonical_response"],
                                   lambda n: n.get("type") == "tool_call" and isinstance(n.get("name"), str)),
            "wrong_tool_name (a response golden with a tool_call part)")),
        "garbage_text": ("response", first(
            responses,
            lambda c, g: _contains(g["canonical_response"],
                                   lambda n: n.get("type") == "text" and isinstance(n.get("text"), str)),
            "garbage_text (a response golden with a text part)")),
        "absent_empty": ("response", first(
            responses,
            lambda c, g: "provider_data" not in g["canonical_response"],
            "absent_empty (a response golden without provider_data — all of them, per PROTOCOL.md)")),
        "usage_off_by_1000": ("response", first(
            responses,
            lambda c, g: any(isinstance(v, int) and not isinstance(v, bool)
                             for v in g["canonical_response"].get("usage", {}).values()),
            "usage_off_by_1000 (a response golden with integer usage)")),
        "dropped_event": ("stream", first(
            streams,
            lambda c, g: len(g.get("events", [])) > 0,
            "dropped_event (a stream golden with events)")),
        "bool_as_int": ("request", first(
            [(c, g) for c, g in cases],
            lambda c, g: _has_bool(check.expected_wire_request(c)["body"]),
            "bool_as_int (a wire fixture with a boolean body leaf)")),
    }

    auth_cases = check.load_auth_fixture()["cases"]
    flip_target = next((c["id"] for c in auth_cases if c["expect"]["steps"]), None)
    if flip_target is None:
        raise SystemExit("selftest: no auth case with steps — auth fixture too thin to self-test")
    targets["auth_state_flip"] = ("auth", flip_target)
    targets["auth_sentinel_leak"] = ("auth", auth_cases[0]["id"])

    model_cases = check.load_model_cases()
    id_target = next(
        (c["id"] for c in model_cases
         if check.golden_path(c).exists()
         and json.loads(check.golden_path(c).read_text())["models"]),
        None,
    )
    param_target = next(
        (c["id"] for c in model_cases if c.get("request", {}).get("params")), None
    )
    if id_target is None or param_target is None:
        raise SystemExit("selftest: models corpus too thin to self-test (need a golden with "
                         "models and a case with query params)")
    # Models results are suffixed [build]/[parse]; the bare id drives the
    # --case filter and the fake shim target, the suffixed id the lookup.
    targets["models_wrong_id"] = ("models", f"{id_target}[parse]")
    targets["models_param_drop"] = ("models", f"{param_target}[build]")
    return targets


def run_direction(mutation: str, direction: str, case_filter: str | None,
                  report_dir: Path) -> check.DirectionReport:
    shim = fake_shim(mutation, case_filter)
    try:
        return check.run_direction(shim, direction, case_filter, report_dir)
    finally:
        try:
            shim.close()
        except Exception:
            pass


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="lm15-selftest-") as tmp:
        report_dir = Path(tmp)

        # 1. Baseline: the unmutated echo must be fully green everywhere.
        shim = fake_shim("none")
        try:
            for direction in check.DIRECTIONS:
                report = check.run_direction(shim, direction, None, report_dir)
                counts = report.counts
                ok = counts["fail"] == 0 and counts["pass"] > 0
                print(f"selftest: baseline {direction:>8}: pass {counts['pass']:3d}  "
                      f"fail {counts['fail']:3d}  skip {counts['skip']:3d} — {'OK' if ok else 'BROKEN'}")
                if not ok:
                    for result in report.results:
                        if result.status == "fail":
                            print(f"selftest:   baseline failure {result.case_id}: "
                                  f"{result.reason or ''} {result.diff.to_dict() if result.diff else ''}")
                    failures.append(f"baseline {direction} not green — echo plumbing broken, "
                                    f"mutation results would be meaningless")
        finally:
            try:
                shim.close()
            except Exception:
                pass

        # 2. Every mutation must be caught red on its target case.
        for mutation, (direction, case_id) in pick_targets().items():
            bare_id = case_id.split("[", 1)[0]
            report = run_direction(mutation, direction, bare_id, report_dir)
            result = next((r for r in report.results if r.case_id == case_id), None)
            if result is None:
                failures.append(f"{mutation}: target {case_id} produced no result in {direction}")
                print(f"selftest: mutation {mutation} → {case_id} [{direction}]: NO RESULT")
                continue
            if result.status != "fail":
                failures.append(f"{mutation}: NOT CAUGHT — {case_id} [{direction}] "
                                f"came back {result.status!r}; the comparator is too weak")
                print(f"selftest: mutation {mutation} → {case_id} [{direction}]: "
                      f"NOT CAUGHT ({result.status})")
                continue
            detail = (f"at {result.diff.path} — {result.diff.note}; "
                      f"expected {check._short(result.diff.expected)}, "
                      f"actual {check._short(result.diff.actual)}"
                      if result.diff else (result.reason or "failed"))
            print(f"selftest: mutation {mutation} → {case_id} [{direction}]: CAUGHT {detail}")

    if failures:
        for failure in failures:
            print(f"selftest: FAIL {failure}")
        print(f"selftest: {len(failures)} failure(s) — the harness comparator cannot be trusted")
        return 1
    print(f"selftest: OK — baseline green and all {len(pick_targets())} mutations caught red")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
