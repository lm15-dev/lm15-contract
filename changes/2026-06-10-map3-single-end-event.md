# 2026-06-10 — MAP-3: a stream yields exactly one StreamEndEvent (final)

## Normative rule (canonical-fact citation)

`lm15-python2/docs/mapping-rules.md` **MAP-3**, written 2026-06-10: an lm15
stream yields EXACTLY ONE `StreamEndEvent`, as the final event, carrying the
`finish_reason` and `usage` accumulated across the provider's terminal frames.
The canonical event trace (goldens, vet `replay_stream`, conformance
`parse_stream`) is the POST-coalesce trace. Implemented as a
provider-agnostic coalescer (`lm15.result.coalesce_stream`); adapters keep
stateless per-frame emission.

## Why

Multiple end events per stream (finish_reason-carrying end, usage-carrying
end, bare `[DONE]` / `message_stop` end) made consumer merge semantics
load-bearing, and they failed in live testing: `Result` treated the first end
as terminal, so the post-finish usage-only chunk that vLLM/SGLang/ollama send
(`stream_options.include_usage`) was never applied and the materialized
`Response.usage` came out all zeros. That known-bug baseline was pinned in
the `openai_chat/streaming_vllm` and `openai_chat/streaming_sglang` drafts.

## Golden changes (re-scribed via tools/scribe_goldens.py, --shim python)

Stream-direction goldens only; all other goldens, cases, bodies, errors and
serde vectors are untouched (verified byte-identical after re-scribe and
restored where the scribe only re-stamped provenance).

Draft goldens (scribe-draft, unreviewed — free to re-scribe):

- `openai_chat/streaming` — 3 end events -> 1 merged end (finish_reason
  `stop`, usage 37/10/47, identical values previously duplicated across the
  first two ends); `canonical_response` unchanged.
- `openai_chat/streaming_vllm` — 3 end events -> 1 merged end; KNOWN-BUG
  baseline corrected: `canonical_response.usage` 0/0/0 -> **14/22/36**.
  Evidence (wire fact, pinned body
  `bodies/openai_chat.streaming_vllm/2026-06-10T19-31-53Z.txt`): final
  usage-bearing chunk carries
  `"usage":{"prompt_tokens":14,"total_tokens":36,"completion_tokens":22}`.
- `openai_chat/streaming_sglang` — 3 end events -> 1 merged end; KNOWN-BUG
  baseline corrected: `canonical_response.usage` 0/0/0 -> **14/10/24**.
  Evidence (pinned body
  `bodies/openai_chat.streaming_sglang/2026-06-10T19-31-53Z.txt`):
  `"usage":{"prompt_tokens":14,"total_tokens":24,"completion_tokens":10,...}`.
- `openai/stream_options`, `openai/background` — re-scribed byte-identical
  (already a single end event carrying correct non-zero usage 12/2/14); no
  diff.

Reviewed goldens (approved oracle — change verified, not rewritten):

- `anthropic/streaming` — the ONLY reviewed golden whose content changes.
  Verified the diff is exactly "2 end events -> 1 merged end, same data": the
  `message_delta` end (finish_reason `stop`, usage 9/12/21, cache 0/0) and
  the bare `message_stop` end (all fields None) coalesce into one final end
  identical to the first; `canonical_response` unchanged. The `reviewed`
  provenance stamp is retained with a re-review note citing MAP-3 (the scribe
  strips stamps; it was restored by hand per the stamp-preservation rule).
- `gemini/streaming`, `openai/streaming` — event traces already contained a
  single final end; re-scribe produced no content diff and their `reviewed`
  stamps were restored untouched.
