# 2026-09-01 — chat dialect stops silently dropping builtin tools

Ratified: Maxime Rivest, 2026-09-01 (session assent "go!" over the
flagged leftover in
changes/2026-09-01-logprobs-and-builtin-tool-forcing.md: the openai_chat
tools loop had no BuiltinTool branch — a `BuiltinTool` in
`Request.tools` vanished from the wire with no error, so a user could
believe a web search backed an answer that came from model memory).

## Evidence (live probes, 2026-09-01, captures in lm15-contract/receipts/2026-09-01-chat-builtin-tools/)

- **OpenAI chat wire**: `tools` carries `function`/`custom` only
  (chat--create.md); `web_search_options` exists but its search-preview
  models are DEPRECATED (probed: model_not_found).
- **Groq**: `{"type": "browser_search"}` and `{"type":
  "code_interpreter"}` are ACCEPTED and executed server-side
  (`message.executed_tools` trace; code run returned 17^13 exactly).
- **OpenRouter**: unknown tool types are SILENTLY IGNORED — 200 OK, no
  search, no error. Its `plugins: [{"id": "web"}]` path also failed to
  search when probed. Server-side silent drop is precisely the failure
  mode the client must guard against.
- **Groq generic forcing**: `tool_choice: "required"` with only a
  builtin is wire-accepted (enforced at generation time —
  `tool_use_failed` when the model answers in text). Named builtin
  forcing has no documented Groq form.

## Decision

Per-server typed policy with raise as the only safe default (option C
of the flagged decision; A-by-default):

- New compat knob `OpenAIChatCompat.builtin_tools:
  "auto" | "reject" | "groq"` (resolved default `"reject"`); the groq
  preset sets `"groq"`.
- `"reject"`: any `BuiltinTool` in `Request.tools` raises
  `UnsupportedFeatureError` — never dropped, never guessed.
- `"groq"`: canonical `web_search` → `browser_search`,
  `code_execution` → `code_interpreter`; `BuiltinTool.config` merges
  into the wire entry (e.g. `search_settings`). Unmapped canonical
  names raise.
- Named builtin forcing on the dialect still raises (unchanged); plain
  `mode="required"` flows through as the `"required"` string, which
  Groq accepts.
- Response side: `message.executed_tools` is a provider-executed trace
  and stays in provider_data (MAP-1), like OpenAI's `web_search_call`
  items and Anthropic's `server_tool_use` blocks.

Rejected alternatives, with the reason named:

- **Silent drop (status quo)**: violates the no-silent-drop rule; the
  user believes a tool ran.
- **Blind passthrough**: there is no single chat-dialect wire shape for
  builtins — passthrough fabricates shapes, and OpenRouter proves
  servers may swallow them silently, converting a client-side lie into
  a server-side one.

## Corpus note

The harness's vet protocol cannot yet select a compat preset for the
openai_chat shim (a pre-existing gap: NO preset-specific wire form —
groq's `max_tokens`, deepseek's `thinking`, etc. — is harness-covered
today; existing openai_chat cases all use the plain-OpenAI policy).
The Groq mapping is therefore pinned by lm15-python unit tests
(tests/test_chat_builtin_tools.py) and the live captures, not by a
contract case. Adding `compat` to the vet protocol is its own future
pass; when it lands, a `openai_chat.builtin_tools_groq` case should be
authored from the existing captures.

## End-to-end receipt

lm15 → Groq (`compat="groq"`, `openai/gpt-oss-20b`,
`BuiltinTool("web_search")`) answered with live-browsed content and the
`executed_tools` trace in provider_data (2026-09-01).
