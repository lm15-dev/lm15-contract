#!/usr/bin/env python3
"""Write mapping/usage.json: the MAP-19 and InferencePricing.estimate vectors.

Every expected cost is computed here, from the rule in spec/types.md
(InferencePricing, "estimate"), with plain arithmetic in the order the rule
fixes, so the file never depends on an implementation:

    total = 0.0
    for tokens, rate in ((uncached, input), (cache_read, read), (cache_write, write), (output, out)):
        if tokens: total += tokens * rate / 1_000_000

Every expected usage of a ``parse`` vector is written by hand from MAP-19
(docs/mapping-rules.md) and checked against INV-029 here.

    python3 tools/make_usage_vectors.py           # write
    python3 tools/make_usage_vectors.py --check   # exit 1 when the file is stale
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mapping" / "usage.json"

SOL = {"input_per_million": 2.0, "output_per_million": 10.0, "cache_read_per_million": 0.1,
       "cache_write_per_million": 2.5, "currency": "USD",
       "tiers": [{"above_input_tokens": 272000, "input_per_million": 4.0, "output_per_million": 15.0,
                  "cache_read_per_million": 0.2, "cache_write_per_million": 5.0}]}
HAIKU = {"input_per_million": 0.1, "output_per_million": 0.5, "cache_read_per_million": 0.01,
         "cache_write_per_million": 0.125, "currency": "USD",
         "tiers": [{"above_input_tokens": 100000, "input_per_million": 0.5, "output_per_million": 2.5,
                    "cache_read_per_million": 0.05, "cache_write_per_million": 0.625}]}
FLAT = {"input_per_million": 1.0, "output_per_million": 4.0, "currency": "USD"}
NO_WRITE_PRICE = {"input_per_million": 0.3, "output_per_million": 2.5, "cache_read_per_million": 0.03, "currency": "USD"}
WRITES_AS_INPUT = {**NO_WRITE_PRICE, "cache_write_per_million": 0.3}
TWO_TIERS = {"input_per_million": 1.0, "output_per_million": 2.0, "cache_read_per_million": 0.1,
             "cache_write_per_million": 1.0, "currency": "USD",
             "tiers": [{"above_input_tokens": 1000, "input_per_million": 2.0, "output_per_million": 4.0,
                        "cache_read_per_million": 0.2, "cache_write_per_million": 2.0},
                       {"above_input_tokens": 2000, "input_per_million": 3.0, "output_per_million": 6.0,
                        "cache_read_per_million": 0.3, "cache_write_per_million": 3.0}]}
TIER_WITHOUT_READ = {"input_per_million": 2.0, "output_per_million": 10.0, "cache_read_per_million": 0.1,
                     "cache_write_per_million": 2.5, "currency": "USD",
                     "tiers": [{"above_input_tokens": 272000, "input_per_million": 4.0, "output_per_million": 15.0}]}


def cost(pricing: dict, usage: dict) -> float | None:
    i, o = usage.get("input_tokens"), usage.get("output_tokens")
    if i is None or o is None:
        return None
    if (usage.get("input_audio_tokens") or 0) > 0 or (usage.get("output_audio_tokens") or 0) > 0:
        return None
    rates = pricing
    for tier in pricing.get("tiers", []):
        if i > tier["above_input_tokens"]:
            rates = tier
    r_in, r_out = rates.get("input_per_million"), rates.get("output_per_million")
    r_read, r_write = rates.get("cache_read_per_million"), rates.get("cache_write_per_million")
    read, write = usage.get("cache_read_tokens"), usage.get("cache_write_tokens")
    if read is None:
        if r_read is None or r_read != r_in:
            return None
        read = 0
    if write is None:
        if r_write is None or r_write != r_in:
            return None
        write = 0
    total = 0.0
    for tokens, rate in ((i - read - write, r_in), (read, r_read), (write, r_write), (o, r_out)):
        if tokens == 0:
            continue
        if rate is None:
            return None
        total += tokens * rate / 1_000_000
    return total


ESTIMATES = [
    ("cached_history", SOL, {"input_tokens": 100000, "output_tokens": 1000, "cache_read_tokens": 90000, "cache_write_tokens": 0},
     "Most of the prompt is re-read history: 10,000 uncached at 2.00, 90,000 read at 0.10, 1,000 out at 10.00 (the 1.x estimate charged the 90,000 twice)."),
    ("long_prompt_tier", SOL, {"input_tokens": 300000, "output_tokens": 1000, "cache_read_tokens": 290000, "cache_write_tokens": 0},
     "Over 272,000 input tokens the whole call pays the tier's rates, cache reads included."),
    ("threshold_is_exclusive", SOL, {"input_tokens": 272000, "output_tokens": 10, "cache_read_tokens": 0, "cache_write_tokens": 0},
     "Exactly at the threshold the base rates apply: a tier starts ABOVE above_input_tokens."),
    ("cache_counts_toward_threshold", HAIKU, {"input_tokens": 100001, "output_tokens": 100, "cache_read_tokens": 99000, "cache_write_tokens": 1000},
     "Anthropic counts cache reads and writes in the prompt length: 1 uncached token puts the call over 100,000."),
    ("writes_priced", HAIKU, {"input_tokens": 5000, "output_tokens": 100, "cache_read_tokens": 0, "cache_write_tokens": 4000},
     "Cache writes at their own rate."),
    ("reasoning_is_output", SOL, {"input_tokens": 10, "output_tokens": 500, "total_tokens": 510, "cache_read_tokens": 0, "cache_write_tokens": 0, "reasoning_tokens": 480},
     "Reasoning is part of output_tokens and costs nothing extra."),
    ("all_zero", SOL, {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0},
     "A call that reports no tokens costs 0.0, not unknown."),
    ("two_tiers_highest_wins", TWO_TIERS, {"input_tokens": 2500, "output_tokens": 10, "cache_read_tokens": 500, "cache_write_tokens": 0},
     "The highest tier whose threshold is exceeded."),
    ("two_tiers_middle", TWO_TIERS, {"input_tokens": 1500, "output_tokens": 10, "cache_read_tokens": 500, "cache_write_tokens": 0},
     "Between the thresholds: the first tier."),
    ("input_unknown", SOL, {"output_tokens": 10, "cache_read_tokens": 0, "cache_write_tokens": 0},
     "No input count: unknown, never a smaller number."),
    ("output_unknown", SOL, {"input_tokens": 10, "total_tokens": 25, "cache_read_tokens": 0, "cache_write_tokens": 0},
     "No output count (a withheld split): unknown."),
    ("cache_read_unknown", SOL, {"input_tokens": 1000, "output_tokens": 10},
     "The provider did not say how much was read from cache, and reads are cheaper: unknown."),
    ("cache_read_unknown_same_rate", {**FLAT, "cache_read_per_million": 1.0, "cache_write_per_million": 1.0}, {"input_tokens": 1000, "output_tokens": 10},
     "Unknown cache counters cannot change the price when both cost the same as input."),
    ("cache_write_unknown_no_rate", NO_WRITE_PRICE, {"input_tokens": 1000, "output_tokens": 10, "cache_read_tokens": 200},
     "A write count was not reported and the catalog states no write rate: unknown (an absent rate is never zero, nor the input rate)."),
    ("cache_write_unknown_writes_as_input", WRITES_AS_INPUT, {"input_tokens": 1000, "output_tokens": 10, "cache_read_tokens": 200},
     "The catalog states writes cost the same as input, so the unreported write count does not matter."),
    ("zero_bucket_needs_no_rate", FLAT, {"input_tokens": 1000, "output_tokens": 10, "cache_read_tokens": 0, "cache_write_tokens": 0},
     "A bucket with no tokens needs no rate."),
    ("bucket_without_rate", FLAT, {"input_tokens": 1000, "output_tokens": 10, "cache_read_tokens": 100, "cache_write_tokens": 0},
     "Tokens in a bucket whose rate is unknown: unknown."),
    ("tier_rate_not_inherited", TIER_WITHOUT_READ, {"input_tokens": 300000, "output_tokens": 10, "cache_read_tokens": 1000, "cache_write_tokens": 0},
     "A tier that states no cache-read rate does not borrow the base rate."),
    ("audio_tokens", SOL, {"input_tokens": 1000, "output_tokens": 10, "cache_read_tokens": 0, "cache_write_tokens": 0, "input_audio_tokens": 200},
     "Audio has its own prices, which the four rates do not carry: unknown."),
    ("audio_reported_zero", SOL, {"input_tokens": 1000, "output_tokens": 10, "cache_read_tokens": 0, "cache_write_tokens": 0, "input_audio_tokens": 0, "output_audio_tokens": 0},
     "Audio reported as zero changes nothing."),
]

USAGE_REJECTS = [
    ("cache_exceeds_input", {"input_tokens": 3, "output_tokens": 6, "cache_write_tokens": 3275},
     "A 1.x Anthropic record: cache counters were beside input. Parts never exceed their whole (INV-029)."),
    ("cache_sum_exceeds_input", {"input_tokens": 10, "output_tokens": 1, "cache_read_tokens": 6, "cache_write_tokens": 6},
     "Read and written tokens are disjoint parts of input."),
    ("reasoning_exceeds_output", {"input_tokens": 19, "output_tokens": 48, "reasoning_tokens": 155},
     "A 1.x Gemini record: reasoning was beside output."),
    ("input_audio_exceeds_input", {"input_tokens": 5, "output_tokens": 1, "input_audio_tokens": 6}, "Input audio is part of input."),
    ("output_audio_exceeds_output", {"input_tokens": 5, "output_tokens": 1, "output_audio_tokens": 2}, "Output audio is part of output."),
    ("total_not_sum", {"input_tokens": 19, "output_tokens": 48, "total_tokens": 222},
     "An explicit total equals input + output when both are present."),
]

USAGE_ACCEPTS = [
    ("parts_within_wholes", {"input_tokens": 3278, "output_tokens": 6, "total_tokens": 3284, "cache_read_tokens": 0, "cache_write_tokens": 3275},
     "anthropic.cache_history under MAP-19."),
    ("total_without_split", {"total_tokens": 20, "cache_read_tokens": 12},
     "A withheld split (MAP-19 rule 3): the provider's total stays, input and output are unknown."),
    ("parts_alone", {"cache_read_tokens": 4, "reasoning_tokens": 7}, "Parts without their wholes are not checked against anything."),
]

PRICING_REJECTS = [
    ("tiers_descending", {**FLAT, "tiers": [{"above_input_tokens": 2000, "input_per_million": 2.0}, {"above_input_tokens": 1000, "input_per_million": 3.0}]},
     "Tiers are in strictly ascending threshold order (one canonical form)."),
    ("tiers_duplicate_threshold", {**FLAT, "tiers": [{"above_input_tokens": 1000, "input_per_million": 2.0}, {"above_input_tokens": 1000, "input_per_million": 3.0}]},
     "Two tiers cannot start at the same length."),
    ("tier_threshold_zero", {**FLAT, "tiers": [{"above_input_tokens": 0, "input_per_million": 2.0}]}, "A threshold is a positive integer."),
    ("tier_threshold_missing", {**FLAT, "tiers": [{"input_per_million": 2.0}]}, "A tier names its threshold."),
    ("tier_rate_negative", {**FLAT, "tiers": [{"above_input_tokens": 1000, "input_per_million": -1.0}]}, "Rates are >= 0."),
]


def chat_body(usage: dict) -> str:
    return json.dumps({"id": "chatcmpl-usage-vector", "object": "chat.completion", "model": "m", "choices": [
        {"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}], "usage": usage})


def anthropic_body(usage: dict) -> str:
    return json.dumps({"id": "msg_usage_vector", "type": "message", "role": "assistant", "model": "m",
                       "content": [{"type": "text", "text": "ok"}], "stop_reason": "end_turn", "usage": usage})


def gemini_body(usage: dict) -> str:
    return json.dumps({"candidates": [{"content": {"role": "model", "parts": [{"text": "ok"}]}, "finishReason": "STOP"}],
                       "usageMetadata": usage, "modelVersion": "m"})


def responses_body(usage: dict) -> str:
    return json.dumps({"id": "resp_usage_vector", "object": "response", "status": "completed", "model": "m",
                       "output": [{"type": "message", "id": "msg_1", "role": "assistant", "status": "completed",
                                   "content": [{"type": "output_text", "text": "ok", "annotations": []}]}],
                       "usage": usage})


PARSE = [
    ("xai.reasoning_beside_completion", "xai", "grok-4.6", chat_body({"prompt_tokens": 254, "completion_tokens": 9, "total_tokens": 374, "prompt_tokens_details": {"cached_tokens": 192}, "completion_tokens_details": {"reasoning_tokens": 111}}),
     {"input_tokens": 254, "output_tokens": 120, "total_tokens": 374, "cache_read_tokens": 192, "reasoning_tokens": 111},
     "MAP-19 rule 4, preset reasoning_usage=separate: output is completion + reasoning (xai.structured_output)."),
    ("xai.no_reasoning_count_total_proves_none", "xai", "grok-4.6", chat_body({"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}),
     {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
     "No reasoning count, and a total of prompt + completion: no reasoning was spent, so output is the completion."),
    ("xai.no_reasoning_count_no_total", "xai", "grok-4.6", chat_body({"prompt_tokens": 10, "completion_tokens": 5}),
     {"input_tokens": 10},
     "No reasoning count and nothing to rule it out: output is unknown, never the completion alone."),
    ("openai_chat.total_disagrees", "openai-chat", "gpt-5.4", chat_body({"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 20}),
     {"total_tokens": 20},
     "MAP-19 rule 3: the provider counted 5 tokens lm15 does not place; input and output are withheld, the total stays."),
    ("openai_chat.cached_exceeds_prompt", "openai-chat", "gpt-5.4", chat_body({"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "prompt_tokens_details": {"cached_tokens": 12}}),
     {"output_tokens": 5, "total_tokens": 15, "cache_read_tokens": 12},
     "A server that counted cached tokens beside the prompt would break the declared rule; input is withheld rather than undercounted."),
    ("openai_chat.reasoning_exceeds_completion", "openai-chat", "gpt-5.4", chat_body({"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 20, "completion_tokens_details": {"reasoning_tokens": 8}}),
     {"input_tokens": 10, "total_tokens": 20, "reasoning_tokens": 8},
     "A server that counts reasoning beside the completion without a preset saying so: output is withheld, never 2."),
    ("anthropic.cache_counters_missing", "anthropic", "claude-sonnet-5-5", anthropic_body({"input_tokens": 10, "output_tokens": 5}),
     {"output_tokens": 5},
     "MAP-19 rule 5: the wire's input_tokens excludes the cache; without both cache counters canonical input is unknown."),
    ("anthropic.cache_beside_input", "anthropic", "claude-sonnet-5-5", anthropic_body({"input_tokens": 3, "cache_creation_input_tokens": 24, "cache_read_input_tokens": 3275, "output_tokens": 6}),
     {"input_tokens": 3302, "output_tokens": 6, "total_tokens": 3308, "cache_read_tokens": 3275, "cache_write_tokens": 24},
     "Canonical input is input + cache read + cache write (anthropic.cache_history's second turn)."),
    ("gemini.tool_use_and_thoughts", "gemini", "gemini-3.8-flash", gemini_body({"promptTokenCount": 10, "toolUsePromptTokenCount": 4, "candidatesTokenCount": 3, "thoughtsTokenCount": 6, "totalTokenCount": 23}),
     {"input_tokens": 14, "output_tokens": 9, "total_tokens": 23, "cache_read_tokens": 0, "reasoning_tokens": 6},
     "MAP-19 rule 6: input is prompt + tool use, output is answer + thoughts; absent counters inside usageMetadata are 0 (proto3)."),
    ("gemini.uncounted_tokens", "gemini", "gemini-3.8-flash", gemini_body({"promptTokenCount": 10, "candidatesTokenCount": 3, "totalTokenCount": 20}),
     {"total_tokens": 20, "cache_read_tokens": 0, "reasoning_tokens": 0},
     "A total no mapped counter explains: input and output are withheld."),
    ("openai.reasoning_exceeds_output", "openai", "gpt-5.4", responses_body({"input_tokens": 10, "output_tokens": 2, "total_tokens": 12, "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 8}}),
     {"input_tokens": 10, "total_tokens": 12, "cache_read_tokens": 0, "reasoning_tokens": 8},
     "Responses: a part larger than its whole withholds the whole."),
]


def inv029(u: dict) -> bool:
    i, o = u.get("input_tokens"), u.get("output_tokens")
    if i is not None and (u.get("cache_read_tokens", 0) + u.get("cache_write_tokens", 0) > i or u.get("input_audio_tokens", 0) > i):
        return False
    if o is not None and (u.get("reasoning_tokens", 0) > o or u.get("output_audio_tokens", 0) > o):
        return False
    return not ("total_tokens" in u and i is not None and o is not None and u["total_tokens"] != i + o)


def render() -> str:
    for _, _, _, _, usage, _ in PARSE:
        assert inv029(usage), usage
    for _, usage, _ in USAGE_REJECTS:
        assert not inv029(usage), usage
    for _, usage, _ in USAGE_ACCEPTS:
        assert inv029(usage), usage
    doc = {
        "description": (
            "MAP-19 (docs/mapping-rules.md) and InferencePricing.estimate (spec/types.md) vectors. "
            "The harness's mapping direction sends each `estimate` vector to estimate_cost and compares `cost` "
            "exactly (null = unknown); sends each `usage_reject` to serde_roundtrip kind usage and each "
            "`pricing_reject` to estimate_cost, both of which must answer ok:false; round-trips each "
            "`usage_accept`; and reads each `parse` body with parse_response, comparing the canonical "
            "response's usage. Generated by tools/make_usage_vectors.py; do not edit by hand."),
        "provenance": {"source": "hand-authored", "date": "2026-10-31", "evidence": (
            "spec/types.md Usage and InferencePricing; spec/invariants.md INV-029, INV-057; docs/mapping-rules.md MAP-19; "
            "changes/2026-10-31-usage-one-meaning.md. Rates of `sol`/`haiku` vectors are the published list prices of "
            "gpt-6.1-sol and claude-haiku-5-5 on 2026-10-31 (developers.openai.com/api/docs/pricing, "
            "platform.claude.com/docs/en/about-claude/pricing); parse bodies are minimal hand-authored replies "
            "whose usage objects follow the recorded ones cited in each `why`.")},
        "estimate": [{"id": i, "pricing": p, "usage": u, "cost": cost(p, u), "why": w} for i, p, u, w in ESTIMATES],
        "usage_reject": [{"id": i, "usage": u, "why": w} for i, u, w in USAGE_REJECTS],
        "usage_accept": [{"id": i, "usage": u, "why": w} for i, u, w in USAGE_ACCEPTS],
        "pricing_reject": [{"id": i, "pricing": p, "why": w} for i, p, w in PRICING_REJECTS],
        "parse": [{"id": i, "provider": prov, "canonical_request": {"model": model, "messages": [{"role": "user", "parts": [{"type": "text", "text": "hi"}]}]},
                   "body": body, "usage": usage, "why": w} for i, prov, model, body, usage, w in PARSE],
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"{OUT.relative_to(ROOT)} is stale: run python3 tools/make_usage_vectors.py", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
