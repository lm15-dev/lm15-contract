# Live-validated openai_chat cases (vLLM + SGLang), 2026-06-10

Six new wire cases under `cases/openai_chat/` for the OpenAI Chat
Completions dialect adapter (`OpenAIChatLM`, lm15-python2 HEAD), each
live-validated per AUTHORITY.md against two self-hosted OpenAI-compatible
servers on the maintainer's GPU box, both serving `Qwen/Qwen3.5-0.8B`:

- vLLM 0.22.1 — `http://192.168.2.24:8000/v1` (cases `*_vllm`)
- SGLang — `http://192.168.2.24:30000/v1` (cases `*_sglang`)

Target pinned per case via the top-level `base_url` field
(changes/2026-06-10-protocol-base-url.md). Wire `request` side is the
adapter's actual `build_request` output (via `python -m lm15.vet`,
default compat, api_key `test-key-123`), sent verbatim; every case
returned HTTP 200 and the verbatim body (SSE transcript for streaming)
is pinned under `bodies/openai_chat.<feature>/<timestamp>.txt`.

Auth: both servers run with auth disabled — they returned 200 with the
bogus bearer `test-key-123` AND with no Authorization header at all. The
fixtures pin the adapter's normal `Bearer test-key-123` header.

## Receipts (UTC capture timestamp = pinned body filename, all HTTP 200, model Qwen/Qwen3.5-0.8B)

| case | target | timestamp | finish_reason | unmapped |
|---|---|---|---|---|
| openai_chat.basic_text_vllm | vLLM | 2026-06-10T19-31-52Z | stop | none |
| openai_chat.streaming_vllm | vLLM | 2026-06-10T19-31-53Z | stop | none |
| openai_chat.tools_vllm | vLLM | 2026-06-10T19-31-53Z | stop | none |
| openai_chat.basic_text_sglang | SGLang | 2026-06-10T19-31-53Z | stop | none |
| openai_chat.streaming_sglang | SGLang | 2026-06-10T19-31-53Z | stop | none |
| openai_chat.tools_sglang | SGLang | 2026-06-10T19-31-54Z | stop | none |

## Cross-check summary (complete / stream / tools, both targets)

All twelve probes (6 pinned + tool_choice variants probed report-only)
parsed through `OpenAIChatLM` with an EMPTY `_lm15_unmapped` canary —
neither server's extension fields (vLLM: `stop_reason`, `token_ids`,
`routed_experts`, `prompt_logprobs`, `kv_transfer_params`; SGLang:
`matched_stop`, `metadata.weight_version`, usage-level
`reasoning_tokens`) trip the canary because the parser only records
unmapped values inside fields it inspects.

Differences vs the Groq captures (2026-06-10-openai-chat-live-cases.md):

- **Tool calling is template-only on both servers.** This vLLM instance
  runs without `--tool-call-parser`: `tool_choice` `"auto"`, `"required"`,
  and named-function are all HTTP 400 (`BadRequestError`); only `"none"`
  is accepted with tools declared. So `tools_vllm` pins the only
  live-validatable tools round (`tool_choice: "none"`), and the model
  still emits a raw `<tool_call>...</tool_call>` block as plain `content`.
  SGLang accepts `"auto"` (pinned in `tools_sglang`) but, also lacking a
  parser, returns the same raw `<tool_call>` text with
  `tool_calls: null` and `finish_reason: "stop"`. Net: unlike Groq,
  NEITHER server produced structured `tool_calls`; both tools cases
  canonicalize to a single TextPart with finish_reason `stop`. Honest
  per AUTHORITY.md — live behavior wins.
- **No thinking emitted.** Qwen3.5-0.8B is a thinking model, but with
  default compat (no `enable_thinking` / `chat_template_kwargs`) both
  servers returned `reasoning_content: null` (SGLang) / `reasoning: null`
  (vLLM); no ThinkingParts appeared (the parser would map them).
- **Streaming usage placement.** Both servers honor
  `stream_options.include_usage` Groq-style with a final usage-only
  chunk, but unlike Groq they do NOT also duplicate usage onto the
  finish_reason chunk. The adapter emits the correct
  `StreamEndEvent(usage=...)` (pinned in the goldens' event traces:
  e.g. vLLM 14/22/36), but the python materializer lets the empty
  `[DONE]` EndEvent clobber it, so the materialized Response usage is
  all zeros for both streaming cases. The earlier ollama cross-check
  blamed ollama for "all-zero token counts" — the wire bodies here show
  real numbers, so this is an lm15-python2 materialization flaw
  (out of scope for this change; lm15-python2 is read-only here), now
  pinned by the scribe-draft goldens as a known regression baseline.
- **Usage extensions.** Groq adds `queue_time`/`prompt_time`/...; vLLM
  adds none but sends `prompt_tokens_details: null`; SGLang adds a
  top-level `usage.reasoning_tokens` (the adapter only reads
  `completion_tokens_details.reasoning_tokens`, so it is ignored —
  canonical `reasoning_tokens` stays absent).
- **Chunking.** vLLM streams a leading `{"role":"assistant","content":""}`
  chunk plus occasional empty-content chunks (dropped by the adapter,
  not emitted as deltas); SGLang sends `reasoning_content: null` on every
  delta chunk and `matched_stop` on the finish chunk.

Notes:

- Goldens drafted by `tools/scribe_goldens.py` (scribe-draft,
  UNREVIEWED — regression pins, not correctness). The scribe rewrote all
  other goldens (its known behavior); those were restored via
  `git checkout` and only the six new goldens are committed.
- `canonical_request` blocks are hand-authored DRAFTS pending human
  review per AUTHORITY.md canonical-facts precedence.
