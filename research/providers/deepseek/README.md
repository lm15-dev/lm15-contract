# DeepSeek — provider dossier

Status ledger (the states from the provider-expansion plan, 2026-09-01):

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-01 | Pi 0.84.1 `/login deepseek` |
| researched | 2026-09-03 | this dossier; `scrapes/deepseek/pages/` (15 pages); `sources/` (terms, privacy) |
| implemented | 2026-09-03 | `lm15.registry.PROVIDERS["deepseek"]`, `lm15.access.DEEPSEEK`, compat preset `deepseek` |
| offline-conformant | 2026-09-03 | auth case `deepseek-env-selected`; support matrix pinned; registry tests |
| **live-verified** | — | **pending** — run `capture.py` with `DEEPSEEK_API_KEY`; see § Live validation |
| supported | — | after the receipts land and a reviewer signs the `changes/` entry |

Until the live row is filled, every wire claim below is at AUTHORITY.md
precedence level 2 (provider documentation), not level 1.  The support
matrix row for `deepseek` says so in its `_doc`.

## Identity

- Service: DeepSeek Open Platform, Hangzhou DeepSeek Artificial
  Intelligence Co., Ltd. (`sources/deepseek-open-platform-terms-of-service.md`).
- lm15 provider string: `deepseek` — **the Chat Completions wire only**.
- Console: https://platform.deepseek.com/api_keys
- Env key: `DEEPSEEK_API_KEY` (the name the provider's own examples use,
  `first-call.md:41,52`).

## Wire endpoints the same key opens

`first-call.md:9-11`, `pricing.md:11-12`, `guide--anthropic-api.md`:

| Endpoint | Base URL | Dialect | lm15 name |
|---|---|---|---|
| Chat Completions | `https://api.deepseek.com` (`/chat/completions`) | openai-chat | `deepseek` (this dossier) |
| Anthropic Messages | `https://api.deepseek.com/anthropic` | anthropic | not registered — candidate `deepseek-anthropic` |
| Responses API | (documented as supported; page not scraped) | openai-responses | not registered |
| Beta (prefix completion, FIM) | `https://api.deepseek.com/beta` | openai-chat + `prefix` field | not registered; user passes `base_url` |

This is the service-versus-wire-endpoint split from the plan in the
flesh: one credential, three protocols.  A provider string never guesses
a protocol, so each is its own registry entry when and if it lands.
The Anthropic endpoint maps `claude-opus*` → `deepseek-v4-pro` and
`claude-haiku*`/`claude-sonnet*` → `deepseek-v4-flash`, and maps any
unknown model to `deepseek-v4-flash` silently (`guide--anthropic-api.md:52-60`)
— a silent-substitution hazard to design around before registering it.

## Authentication

- `Authorization: Bearer <key>` (`first-call.md:41`).  `AccessPolicy`:
  `auth_modes=("bearer",)`, `credential_policy="key"`.
- No OAuth, no subscription flow, no ambient identity.  AUTH-1 chain:
  explicit `api_keys` → `$DEEPSEEK_API_KEY`.
- Billing model: **prepaid balance** (`terms § 6.1`, `pricing.md § Deduction
  Rules`).  A drained balance is HTTP 402 `Insufficient Balance`
  (`error-codes.md`), never a surprise invoice.  This satisfies lm15's
  "normal inference must not unexpectedly spend money" constraint better
  than post-paid providers do.
- Peak/off-peak pricing: peak is 01:00–04:00 and 06:00–10:00 UTC weekdays,
  off-peak is half price (`pricing.md:31-33`).  Cost varies by clock, not
  by request shape; nothing for lm15 to do beyond stating it.

## Models

`first-call.md:13-17`, `models--list.md`:

- `deepseek-v4-flash` (→ DeepSeek-V4-Flash-0731), `deepseek-v4-pro`
  (→ DeepSeek-V4-Pro-0813), `deepseek-v4-flash-vision-exp` (image input,
  experimental, 2026-08-21).
- 1M context, 384K max output, all three (`pricing.md:16-17`).
- `GET /models` → `{object: "list", data: [{id, object, owned_by}]}` — no
  prices, no context length, no modalities on the wire.  lm15's
  `ModelInfo` will carry ids only; `models: true` in the matrix.
- Concurrency limits per account: pro 500, flash 2500, vision 2500;
  exceeding → 429 (`rate-limit.md`).

## Request surface (`chat--create.md`) and the compat mapping

| lm15 knob | DeepSeek wire | Compat field / decision |
|---|---|---|
| system message | `role: system` | `instruction_role="system"` |
| `max_tokens` | `max_tokens` | `max_tokens_field="max_tokens"` |
| streaming | `stream: true`, `data: [DONE]`; `stream_options.include_usage` puts usage on the last chunk (`:173-180`) | `stream_usage="include"` |
| reasoning on + effort | `thinking: {type: enabled}` + `reasoning_effort: low\|high\|max`; **default is enabled/high**; `medium`,`xhigh` → `high` server-side; `minimal` undocumented (`guide--thinking-mode.md:10-22`) | `thinking_format="deepseek"` (already sends both) — **probe `minimal`** |
| reasoning off | `thinking: {type: disabled}` | same format; off is honoured per docs (unlike xAI) |
| thinking replay | `reasoning_content` on assistant messages; **required on every assistant turn when `tools` present, else 400** (`guide--thinking-mode.md:98-102`); ignored without tools | `thinking_replay="native"`, `assistant_reasoning_content="include_empty"` ← **changed in this pass** |
| tools | `tools[].function`, `tool_choice` none/auto/required/`{type:function,function:{name}}`, `strict` (default false) (`:201-258`) | dialect default; `strict_tools="omit"` |
| structured output | `response_format.type` ∈ {`text`, `json_object`} **only** (`:144-152`); prompt must say "json" | `json_schema` will reach the wire and **should** be rejected loudly — **probe** |
| temperature / top_p | accepted; **silently ignored in thinking mode** (`guide--thinking-mode.md:24`); default 1.0 | no compat knob; see § Open decisions |
| `frequency_penalty`, `presence_penalty` | deprecated, silently ignored (`:276-278`) | lm15 has no such Config fields; only via extensions |
| `stop` | string or array ≤16 | dialect default |
| logprobs | `logprobs`, `top_logprobs ≤ 20`; also on `reasoning_content` tokens (`:260-262`, `:370-410`) | dialect default; **probe** the reasoning logprobs shape (lm15 has no slot for it) |
| user identity | **`user_id`**, regex `[a-zA-Z0-9\-_]+`, ≤512 (`:264-274`, `rate-limit.md`) — not OpenAI's `user` | lm15 sends `user` — **probe**: rejected, ignored, or both accepted? May need a compat field `user_field` |
| prompt caching | automatic, on disk, no request field (`guide--kv-cache.md`) | `cache_control="none"` |
| images | `image_url` {url \| data URL, detail low/high/original/auto}, vision model only (`:64-73`) | dialect default; `images` stays false in the matrix (that column means *generation*) |
| files | `type: file` with `file_id` from "the Files API" (`:77-85`) — a Files API exists but is not scraped | `files: false` until researched |

## Response surface

- `choices[0].message.{content, reasoning_content, tool_calls}`; tool-call
  ids look like `call_00_…` (`guide--thinking-mode.md:190`).
- `finish_reason` ∈ stop, length, content_filter, tool_calls,
  **`insufficient_system_resource`** (`:303`).  The last one has no lm15
  `FinishReason`; the dialect records it as unmapped.  Decide: map to
  `error` or leave unmapped — needs a live sighting first.
- `usage`: `prompt_tokens`, `completion_tokens`, `total_tokens`,
  **`prompt_cache_hit_tokens`**, **`prompt_cache_miss_tokens`**,
  `completion_tokens_details.reasoning_tokens` (`:429-445`).  lm15's chat
  usage parser reads `prompt_tokens_details.cached_tokens`; DeepSeek's
  spelling is different.  **Probe** whether the body also carries
  `prompt_tokens_details`; if not, the parser needs to read
  `prompt_cache_hit_tokens` into `cache_read_tokens` (one line, but a
  contract change: `bodies/` + usage-semantics table).
- Errors: only HTTP codes are documented (`error-codes.md`: 400, 401,
  402, 422, 429, 500, 503).  The envelope shape is **not** documented;
  capture 401 and a 400 to pin it in `errors/cases/deepseek.json`.

## Capabilities by lm15 area (claim level)

| Area | Claim | Level |
|---|---|---|
| auth | bearer key | docs |
| model listing | ids only | docs |
| complete | yes | docs |
| streaming | yes, usage on last chunk | docs |
| tools | yes, with mandatory reasoning replay | docs |
| structured output | `json_object` only | docs |
| reasoning | on by default, effort low/high/max, off supported | docs |
| images (input) | vision-exp model only | docs |
| documents | Files API exists, unresearched | — |
| usage | yes, DeepSeek cache fields | docs |
| errors | codes only | docs |
| files / batch / generated media / live | none documented | — |

## Terms-of-service verdict

Source: `sources/deepseek-open-platform-terms-of-service.md` (release
2026-04-22, effective 2026-04-29, sha256 in the file header).

- § 1.1 grants API access "into various downstream systems, applications,
  or functionalities … providing services to both internal and external
  end users".  § 4.2 permits "derivative product development, training
  other models (such as model distillation)".  General-purpose library
  use is squarely inside the grant.
- § 2.2: the key is the developer's; do not share or expose it.  lm15
  never renders it (AUTH-5).
- § 10.1: governed by PRC mainland law.
- Privacy policy: data is "collected, processed and stored in People's
  Republic of China" (`sources/deepseek-privacy-policy.md § Where We
  Store`).  Not a library concern, but a user-facing fact the docs must
  state plainly.

**Verdict: allowed, API key only.**  No OAuth client to borrow, no
coding-plan restriction, no ambiguity.

## Open decisions (need live evidence before they become rules)

1. **`user` vs `user_id`.**  If DeepSeek rejects `user`, lm15's promoted
   `Config.user_id` is broken on this provider and a compat field
   `user_field: "user" | "user_id"` is the fix.  If DeepSeek ignores
   `user`, it is a silent no-op and the same fix applies (a silent drop of
   a privacy/isolation knob is worse than an error).
2. **Temperature in thinking mode.**  Silently ignored by the server.
   lm15's precedent (xAI reasoning-off) raises on silent *paid* no-ops;
   temperature costs nothing extra.  Proposed: do not raise, document in
   `providers-and-models.md`.  Counter-argument: `temperature=0` for
   coding is a determinism promise the user thinks they have.  Decide at
   review.
3. **`minimal` effort.**  Not in DeepSeek's list.  Probe: 400 (loud, fine)
   or mapped (record the mapping).
4. **`json_schema` response_format.**  Expect a 4xx.  If instead it is
   silently treated as `json_object`, that is a silent widening and needs a
   compat knob (`structured_output: "json_schema" | "json_object_only"`)
   so lm15 raises `UnsupportedFeatureError` before the wire.
5. **Cache usage spelling.**  See § Response surface.
6. **`insufficient_system_resource`.**  Mapping, after a sighting.

## Live validation

`capture.py` in this directory is the controlled validator from the plan:
it holds the key (from `DEEPSEEK_API_KEY`, never written anywhere),
builds every request through the adapter (`build_request`), sends it
verbatim, and writes:

- `cases/deepseek/<feature>.json` with the adapter's wire as `request`
  and the key replaced by `$DEEPSEEK_API_KEY`;
- `bodies/deepseek.<feature>/<timestamp>.txt` verbatim;
- `receipts/2026-09-03-deepseek/` — the probe outputs for the open
  decisions above, plus `models.json` and the error envelopes;
- a summary on stdout to paste into the `changes/` entry.

Cost: under $0.05 at off-peak flash prices.  Run:

```bash
cd lm15-contract
DEEPSEEK_API_KEY=… python3 research/providers/deepseek/capture.py
python3 tools/check_secrecy.py && python3 tools/audit.py --python2 ../lm15-python
python3 harness/check.py --shim python --no-check-pin
```

Then fill the ledger row, decide the open items, and amend
`changes/2026-09-03-provider-registry.md` (or write a follow-up entry)
with the receipt table.

## Pi comparison (input, not authority)

Pi 0.84.1 (`pi-ai/dist/providers/deepseek.js`, read 2026-09-03) registers
`deepseek` as one OpenAI Chat Completions provider: base URL
`https://api.deepseek.com`, env `DEEPSEEK_API_KEY`, a static model list.
lm15 agrees on all three.  Pi does not expose the Anthropic or Responses
endpoints either.
