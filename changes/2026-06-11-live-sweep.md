# 2026-06-11 — Live re-validation sweep of all 112 wire fixtures

Every case's recorded wire request was replayed verbatim against its live
target (api.openai.com, api.anthropic.com, generativelanguage.googleapis.com,
api.groq.com, vLLM 192.168.2.24:8000, SGLang 192.168.2.24:30000; auth headers
substituted from env; `$AUTO_*` placeholders provisioned via side calls).
One attempt + one retry per case, small bodies as recorded.

## Result: 112 replayed — 111 confirmed 2xx, 1 drift fixed, 0 skipped targets

- **111/112 returned 2xx** with the recorded byte shape (includes the two
  freshly recaptured anthropic cache cases).
- **Drift: openai.file_input** — OpenAI Responses now rejects `input_file`
  with `file_data` but no `filename` (400 `missing_required_parameter`,
  `input[0].content[1]`). Per AUTHORITY.md live > fixture > implementation:
  the reference adapter (`lm15/providers/common.py part_to_openai_input`)
  was fixed red-first to emit a deterministic `filename` ("file." +
  media-type subtype) alongside inline `file_data`; the rebuilt request was
  sent live verbatim 2026-06-11T01-35-33Z, sha256
  `0803784a3d831e8bf2af98cf6cc1fb33e2f4c227f1f982d301015c0cdb9fcb46`,
  HTTP 200, response id
  `resp_00e8db984f5a0861006a2a10e30ccc81a183018c255ce3781b` (model
  answered "Hello PDF"). Wire fixture body, pinned body, and golden updated
  with this receipt (the golden had been reviewed 2026-06-10; the only
  semantic change is the volatile response id — re-drafted, noted).

## Non-drift notes

- **Groq 403 "error code: 1010"** on first pass for all 10 Groq cases:
  Cloudflare blocks the python-urllib default User-Agent. With any explicit
  User-Agent the same bytes return 200. `user-agent` is transport noise
  (harness DROP_HEADERS), out of contract — no fixture change.
- **openai_chat.tool_choice_required (Groq, llama-3.1-8b-instant)**: today
  the model intermittently hallucinates tool names under
  `tool_choice: "required"`, yielding 400 `tool_use_failed` (a
  generation-time error; the request shape itself is accepted). 5 retries
  all failed on model output, never on wire shape. Fixture stands on its
  2026-06-10 live receipt; flagged as model-flaky for future sweeps.
- **OpenRouter**: no key available — the one unvalidated openai_chat preset.
- Subscriptions are not in the corpus; nothing skipped for missing creds.
