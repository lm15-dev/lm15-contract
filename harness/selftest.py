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
end-event provider_data loss (D9 presence rule), bool/int conflation,
auth-chain state drift, and AUTH-5 sentinel leakage. A comparator weakened enough to miss any of them fails
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
    # A pinned-raise golden (expect_lm15.raises; e.g. tool_call_unnamed_complete,
    # 2026-09-07) carries provenance only — nothing to mutate; skip it.
    responses = [(c, g) for c, g in cases if not check.is_stream_case(c) and "canonical_response" in g]
    streams = [(c, g) for c, g in cases if check.is_stream_case(c) and "events" in g]

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
            lambda c, g: len(g.get("events", [])) > 0 and "canonical_response" in g,
            "dropped_event (a stream golden with events)")),
        "end_provider_data_dropped": ("stream", first(
            streams,
            lambda c, g: check.expected_raise(c, "replay_stream") is None and any(
                isinstance(e, dict) and e.get("type") == "end" and "provider_data" in e
                for e in g.get("events", [])),
            "end_provider_data_dropped (a stream golden whose end event carries provider_data)")),
        "assembly_guesses_name": ("stream", first(
            streams,
            lambda c, g: check.expected_raise(c, "replay_stream") is not None,
            "assembly_guesses_name (a stream case that pins a refusal)")),
        "build_maps_a_refused_cell": ("request", first(
            [(c, {}) for c in check.load_wire_cases()],
            lambda c, g: check.expected_raise(c, "build_request") is not None,
            "build_maps_a_refused_cell (a request case that pins a refusal)")),
        "tool_result_image_dropped": ("request", first(
            [(c, {}) for c in check.load_wire_cases()],
            lambda c, g: c.get("feature") == "tool_result_image",
            "tool_result_image_dropped (a tool_result_image case)")),
        "tool_result_ids_swapped": ("request", first(
            [(c, {}) for c in check.load_wire_cases()],
            lambda c, g: c.get("feature") == "tool_result_pair",
            "tool_result_ids_swapped (a tool_result_pair case)")),
        "tool_result_error_stripped": ("request", first(
            [(c, {}) for c in check.load_wire_cases()],
            lambda c, g: c.get("feature") == "tool_result_error",
            "tool_result_error_stripped (a tool_result_error case)")),
        "bool_as_int": ("request", first(
            [(c, g) for c, g in cases],
            lambda c, g: "request" in c and _has_bool(check.expected_wire_request(c)["body"]),
            "bool_as_int (a wire fixture with a boolean body leaf)")),
        "pinned_credential_scheme_drift": ("request", first(
            [(c, {}) for c in check.load_wire_cases()],
            lambda c, g: isinstance(c.get("credential"), dict) and c["credential"].get("kind") == "bearer_token"
                         and "authorization" in check.expected_wire_request(c)["headers"],
            "pinned_credential_scheme_drift (a request case pinning a bearer_token credential)")),
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

    live_cases = check.load_live_cases()
    decode_target = next(
        (c["id"] for c in live_cases
         if check.golden_path(c).exists()
         and any(g for g in json.loads(check.golden_path(c).read_text())["events"])),
        None,
    )
    encode_target = next(
        (c["id"] for c in live_cases
         if any(e["dir"] == "client" and e.get("kind") == "event" and e["frames"]
                for e in check.load_live_transcript(c))),
        None,
    )
    if decode_target is None or encode_target is None:
        raise SystemExit("selftest: live corpus too thin to self-test (need a golden with "
                         "events and a transcript with client frames)")
    targets["live_dropped_event"] = ("live", f"{decode_target}[decode]")
    targets["live_frame_key_drop"] = ("live", f"{encode_target}[encode]")

    gen_cases = check.load_surface_cases("generation")
    media_target = next((c["id"] for c in gen_cases if check.golden_path(c).exists()), None)
    text_target = next(
        (c["id"] for c in gen_cases
         if check.golden_path(c).exists()
         and json.loads(check.golden_path(c).read_text())["response"].get("text")),
        None,
    )
    multipart_target = next(
        (c["id"] for c in gen_cases if isinstance(c.get("request", {}).get("body_b64"), str)), None
    )
    if media_target is None or text_target is None or multipart_target is None:
        raise SystemExit("selftest: generation corpus too thin to self-test (need a golden, "
                         "a narration-text golden, and a multipart build case)")
    targets["gen_wrong_media_type"] = ("generation", f"{media_target}[parse]")
    targets["gen_dropped_narration"] = ("generation", f"{text_target}[parse]")
    targets["gen_multipart_field_drop"] = ("generation", f"{multipart_target}[build]")

    files_cases = check.load_surface_cases("files")
    readiness_target = None
    param_target_files = None
    for c in files_cases:
        golden = json.loads(check.golden_path(c).read_text()) if check.golden_path(c).exists() else {}
        for step in c["steps"]:
            key = step.get("golden_key", step["file_op"])
            if readiness_target is None and step.get("parse") == "info" and golden.get(key, {}).get("readiness") == "ready":
                readiness_target = (c["id"], step["file_op"])
            if param_target_files is None and step.get("request", {}).get("params"):
                param_target_files = (c["id"], step["file_op"])
    if readiness_target is None or param_target_files is None:
        raise SystemExit("selftest: files corpus too thin to self-test (need a ready golden "
                         "and a build step with query params)")
    targets["file_readiness_flip"] = ("files", f"{readiness_target[0]}[{readiness_target[1]}.parse]")
    targets["file_param_drop"] = ("files", f"{param_target_files[0]}[{param_target_files[1]}]")

    batch_cases = check.load_surface_cases("batch")
    swap_target = next(
        (c["id"] for c in batch_cases
         if check.golden_path(c).exists()
         and len(json.loads(check.golden_path(c).read_text()).get("entries", [])) >= 2),
        None,
    )
    vocab_target = next(
        (c["id"] for c in batch_cases
         if check.golden_path(c).exists()
         and json.loads(check.golden_path(c).read_text()).get("status", {}).get("status") == "completed"),
        None,
    )
    if swap_target is None or vocab_target is None:
        raise SystemExit("selftest: batch corpus too thin to self-test (need >=2 entries "
                         "and a completed status golden)")
    targets["batch_entry_order_swap"] = ("batch", f"{swap_target}[result_fetches.parse]")
    targets["batch_status_vocab_drift"] = ("batch", f"{vocab_target}[status.parse]")

    cache_cases = check.load_surface_cases("cache")
    expiry_target = next(
        ((c["id"], s["cache_op"]) for c in cache_cases for s in c["steps"]
         if s.get("pinned_body") and check.golden_path(c).exists()
         and json.loads(check.golden_path(c).read_text()).get(s.get("golden_key", s["cache_op"]), {}).get("expires_at")),
        None,
    )
    create_target = next(
        (c["id"] for c in cache_cases if any(s["cache_op"] == "create" and isinstance(s.get("request", {}).get("body"), dict)
                                             and "model" in s["request"]["body"] for s in c["steps"])),
        None,
    )
    if expiry_target is None or create_target is None:
        raise SystemExit("selftest: cache corpus too thin to self-test (need an expires_at golden and a create step with a model)")
    targets["cache_expiry_drift"] = ("cache", f"{expiry_target[0]}[{expiry_target[1]}.parse]")
    targets["cache_model_drop"] = ("cache", f"{create_target}[create]")

    video_cases = check.load_surface_cases("video")
    video_vocab = next(
        (c["id"] for c in video_cases
         if check.golden_path(c).exists()
         and json.loads(check.golden_path(c).read_text()).get("done", {}).get("status") == "completed"),
        None,
    )
    video_url = next(
        (c["id"] for c in video_cases
         if check.golden_path(c).exists()
         and json.loads(check.golden_path(c).read_text()).get("part", {}).get("url")),
        None,
    )
    if video_vocab is None or video_url is None:
        raise SystemExit("selftest: video corpus too thin to self-test (need a completed "
                         "status golden and a URL-delivered part golden)")
    targets["video_status_vocab_drift"] = ("video", f"{video_vocab}[done.parse]")
    targets["video_part_url_drift"] = ("video", f"{video_url}[part.parse]")

    router_cases = check.load_router_fixture()["cases"]
    ambiguous_target = next((c["id"] for c in router_cases if c["expect"].get("error", {}).get("code") == "ambiguous_model"), None)
    unknown_target = next((c["id"] for c in router_cases if c["expect"].get("error", {}).get("code") == "unknown_model"), None)
    hyphen_target = next((c["id"] for c in router_cases if "-" in c["expect"].get("provider", "")), None)
    alias_target = next((c["id"] for c in router_cases if "catalog" in c and c["expect"].get("model") not in (None, c["model"])), None)
    if None in (ambiguous_target, unknown_target, hyphen_target, alias_target):
        raise SystemExit("selftest: router corpus too thin to self-test (need an ambiguous_model case, "
                         "an unknown_model case, a hyphenated provider, and an alias resolution)")
    targets["router_class_drift"] = ("router", ambiguous_target)
    targets["router_resolves_instead_of_refusing"] = ("router", unknown_target)
    targets["router_provider_underscore"] = ("router", hyphen_target)
    targets["router_alias_not_resolved"] = ("router", alias_target)

    sigv4_cases = json.loads(check.SIGV4_FILE.read_text(encoding="utf-8"))["cases"]
    token_cases = json.loads(check.TOKEN_FILE.read_text(encoding="utf-8"))["cases"]
    parse_target = next((c["id"] for c in token_cases if c["id"].endswith(".parse")), None)
    if not sigv4_cases or parse_target is None:
        raise SystemExit("selftest: token corpus too thin to self-test (need a SigV4 vector "
                         "and a token-exchange parse vector)")
    targets["sigv4_signature_drift"] = ("token", f"sigv4.{sigv4_cases[0]['id']}")
    targets["token_credential_drift"] = ("token", f"token.{parse_target}")
    assertion_target = next((c["id"] for c in token_cases if c["id"].endswith(".build")
                             and "assertion" in c["expect"]["request"].get("body", {})), None)
    if assertion_target is None:
        raise SystemExit("selftest: token corpus needs a signed assertion build vector")
    targets["token_assertion_drift"] = ("token", f"token.{assertion_target}")

    ingest_cases = check.load_ingest_cases()
    config_target = next(
        (c["id"] for c in ingest_cases
         if check.ingest_expectation(c)[0] == "canonical" and check.ingest_expectation(c)[1].get("config")),
        None,
    )
    refusal_target = next((c["id"] for c in ingest_cases if check.ingest_expectation(c)[0] == "raises"), None)
    if config_target is None or refusal_target is None:
        raise SystemExit("selftest: ingest corpus too thin to self-test (need a body with generation "
                         "knobs and a pinned refusal)")
    targets["ingest_drops_config"] = ("ingest", config_target)
    targets["ingest_maps_a_refused_key"] = ("ingest", refusal_target)
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
