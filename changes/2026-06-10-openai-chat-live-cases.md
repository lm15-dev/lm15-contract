# Live-validated openai_chat cases (Groq), 2026-06-10

Ten new wire cases under `cases/openai_chat/` for the OpenAI Chat
Completions dialect adapter (`OpenAIChatLM`, lm15-python2@66e4d61), each
live-validated against Groq per AUTHORITY.md (wire fixtures require a live
receipt).

- Canonical pinned target: `https://api.groq.com/openai/v1/chat/completions`
  (hosted/stable), recorded per case via the new top-level `base_url` field
  (see changes/2026-06-10-protocol-base-url.md).
- Model: `llama-3.1-8b-instant` (discovered via GET /openai/v1/models on
  2026-06-10).
- Wire `request` side is the adapter's actual `build_request` output
  (generated through `python -m lm15.vet`), sent verbatim; every case
  returned HTTP 200 and the verbatim response body (SSE transcript for
  `streaming`) is pinned under `bodies/openai_chat.<feature>/<timestamp>.txt`.
- All ten responses parse through the adapter with an EMPTY `_lm15_unmapped`
  canary.

Receipts (UTC capture timestamp = pinned body filename, all HTTP 200,
model llama-3.1-8b-instant):

| case | timestamp | finish_reason |
|---|---|---|
| openai_chat.basic_text | 2026-06-10T19-18-22Z | stop |
| openai_chat.system_prompt | 2026-06-10T19-18-22Z | stop |
| openai_chat.multi_turn | 2026-06-10T19-18-22Z | stop |
| openai_chat.streaming | 2026-06-10T19-18-23Z | stop |
| openai_chat.tools | 2026-06-10T19-18-23Z | tool_call |
| openai_chat.tool_choice_auto | 2026-06-10T19-18-23Z | tool_call |
| openai_chat.tool_choice_required | 2026-06-10T19-18-24Z | tool_call |
| openai_chat.temperature | 2026-06-10T19-18-24Z | stop |
| openai_chat.response_format_json_object | 2026-06-10T19-18-24Z | stop |
| openai_chat.max_tokens | 2026-06-10T19-18-25Z | stop |

Notes:
- `tool_choice_required` needed retries: llama-3.1-8b-instant intermittently
  fails Groq-side tool-call validation (`tool_use_failed`, HTTP 400). Failed
  attempts were not captured; the pinned body is the first HTTP 200.
- Ollama cross-check (report-only, no fixtures committed): basic_text,
  streaming, and tools re-run against `http://localhost:11434/v1`
  (qwen3.5:0.8b) all returned 200 and parsed cleanly (zero unmapped;
  reasoning_content mapped to ThinkingPart). Ollama's streaming usage chunk
  reported all-zero token counts.
- Goldens for these cases were drafted by `tools/scribe_goldens.py`
  (scribe-draft, UNREVIEWED — they pin regressions, not correctness).
- `canonical_request` blocks are hand-authored DRAFTS pending human review
  per AUTHORITY.md canonical-facts precedence.
- OpenRouter / vLLM / SGLang were not reachable; no fixtures were authored
  for them (no live receipt, none allowed).
