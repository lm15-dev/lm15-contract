# 2026-10-10 — A refused key is `auth` everywhere (MAP-18); a key put where a name goes is never repeated (AUTH-1, AUTH-5)

Status: written at the maintainer's request ("make sure we fully close all
gaps"); not yet ratified.

## How it was found

A coding-agent benchmark (lm15-dev `agent-bench/`, 2026-10-10) asked agents to
build the same programs with LM15, LiteLLM and each provider's own SDK, then
re-ran and graded the programs. Two LM15 defects showed up in the transcripts,
not in the corpus:

1. **A bad Gemini key was `InvalidRequestError`.** Every LM15 program that
   classified a bad Gemini key called it an invalid request (12 of 12 runs, two
   agent models); the Gemini SDK and LiteLLM said authentication. The corpus
   pinned `gemini.auth_permission_denied`, a hand-authored 403 with
   `PERMISSION_DENIED` that Gemini does not send for a bad key, so every SDK
   passed while being wrong.
2. **A key given as `credential=` was printed.** Agents guessing the
   constructor wrote `AnthropicLM(credential=os.environ["ANTHROPIC_API_KEY"])`
   (26 of 75 first runs with the old skill). The refusal repeated the value:
   `anthropic: credential='sk-ant-…' names a cloud identity…`. AUTH-5 already
   forbade key material in exception messages; the value was not recognized
   as key material because the argument is meant for a name.

## Evidence

`receipts/2026-10-10-auth-failed/` (capture script
`research/auth-failed/capture.py`): one request to each of 18 HTTP routes
reachable from the lab, built by lm15-python 1.2.1 and sent unchanged, with
the fixed fake key `lm15-invalid-key-0000000000`. Nothing is redacted; the key
is not secret.

| answer | routes |
|---|---|
| 401, already `AuthError` | openai, openai-chat, anthropic, groq, deepseek, deepseek-anthropic, moonshotai, moonshotai-anthropic, openrouter, zai, together, fireworks, deepinfra, parasail, meta, meta-chat |
| 400 `INVALID_ARGUMENT`, ErrorInfo reason `API_KEY_INVALID`, "API key not valid. Please pass a valid API key." | gemini (was `InvalidRequestError`) |
| 400 `invalid-argument`, "Incorrect API key provided. You can obtain an API key from https://console.x.ai." | xai (was `InvalidRequestError`; on 2026-09-01 its keyless answer was 401) |

TypeSafe was not probed: the router refuses a request to it before sending
(`UnsupportedFeatureError` for `complete`).

## Decisions

**D1. MAP-18: a provider's "this key is not valid" is `auth`, by pinned
form.** `spec/auth-failed.json` holds the forms, checked before every other
test on every path that turns an HTTP reply into a `ProviderError`. Same
mechanism as MAP-15 (exact provider code plus text tests, one live receipt per
form, never widened), with one addition: a form may name a Google
`google.rpc.ErrorInfo` `reason`.

- Options for Gemini: (a) match the sentence "API key not valid."; (b) match
  the ErrorInfo reason `API_KEY_INVALID`; (c) map every 400
  `INVALID_ARGUMENT` whose message mentions "API key". Taken: (b). Google's
  error model documents `reason` as the stable machine-readable field, and the
  expired-key answer shares it; (a) breaks on rewording; (c) would widen
  beyond the receipt.
- xAI sends no reason; its form matches the sentence's start, as MAP-15's xAI
  form does.
- Rejected: changing `INVALID_ARGUMENT`'s row in the Gemini table to `auth`.
  It is also Gemini's answer to an empty part, a bad schema, an unknown
  field.

Trade-off, stated: a provider that rewords a form without a reason falls back
to `InvalidRequestError`, its class before this rule, until a new receipt.

**D2. AUTH-1 named credentials, amended: a value that is not one of the four
names is a key in the wrong place.** The refusal never repeats it, says it is
not shown "because it may be a key", and says where a key goes (the
language's `api_key` argument or the router's `api_keys`). A refusal repeats
the value only when it is one of the four names. AUTH-5 names the case: key
material includes any value a caller passed in a slot meant for a name.

- Options: (a) accept a key given as `credential=` on a door without a cloud
  chain; (b) refuse without repeating it and say where it goes. Taken: (b).
  (a) makes one argument mean two things, and on a cloud door a key and a
  name are both legal values with different meanings; a guess there could
  pick the wrong identity silently.

## Cases

- `errors/cases/gemini.json`: new `gemini.auth_api_key_invalid` (the live body,
  `AuthError`), new `gemini.invalid_argument_other_reason` (the same envelope
  with another reason, still `InvalidRequestError`: the reason decides, not
  the words). `gemini.auth_permission_denied` is kept: Gemini does answer 403
  `PERMISSION_DENIED` for a key without access to a resource.
- `errors/cases/xai.json`: new `xai.auth_incorrect_key`.
- `auth/named-credentials.json`: new `anthropic-key-given-as-credential` (a
  door with no cloud chain) and `vertex-key-given-as-credential` (a cloud
  door, unknown name); the sentinel is the value given; `expect.error` is
  "may be a key". Ports that read this file also assert the sentinel is
  absent from the refusal's message and repr.

Error direction: 105 → 108 cases.

## Implementations

The same table and check in every SDK; the misplaced-key refusal fixed where
it repeated the value.

| SDK | Repeated the value before | Error direction | Own suite |
|---|---|---|---|
| Python | adapter, doctor, cloud door, `RouterConfig(credentials=…)` | 108/108 | 3,670 passed |
| TypeScript | no (message now says where a key goes) | 108/108 | 532 passed |
| Rust | cloud door (`unknown named credential "…"`) | 108/108 | 572 passed, clippy clean |
| Go | adapter, doctor, cloud door, `RouterConfig.Credentials` | 108/108 | passed |
| Julia | adapter (both refusals) | 108/108 | passed |
| R | cloud door (`Unknown named identity '…'`) | see the parity ledger | |

Not moved: Java, Ruby, .NET and Swift (outside the parity table, as in
previous changes).
