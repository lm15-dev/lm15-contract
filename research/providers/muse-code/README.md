# Muse Code subscription (Meta) — provider dossier

The Muse Code subscription is Meta's flat-rate plan for its coding agent
(the "Coding Harness Subscription" of the Meta Model API terms). It is the
Meta counterpart of `claude-code` (Claude Pro/Max) and `openai-codex`
(ChatGPT plan): playbook `provider.md` kind **D, subscription login**.

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-10-12 | maintainer request ("add the Muse Wonder subscription, like Codex and Claude Code") |
| researched | 2026-10-12 | this file; terms and docs frozen under `sources/` (`SHA256SUMS`); the Muse Code 1.4.6 binary read offline; one offline capture of its inference request |
| terms verdict | 2026-10-12 | **not allowed as a direct door** (below) |
| decision | 2026-10-12 | the maintainer chose the direct door (option B) with the risk stated |
| implemented | 2026-10-12 | the existing `meta` device login, amended: `changes/2026-10-12-muse-code-subscription.md` |
| live-verified | 2026-10-12 | `receipts/2026-10-12-muse-code/` (login, mint, re-mint, inference on `muse-wonder-full-1.0`) |
| supported | — | not claimed: the method stays `unverified` because of § 3.2 |

## Terms verdict (read first)

Meta Model API Terms, last updated **2026-10-09**
(`sources/meta-model-api-terms-2026-10-09.txt`), § 3.2:

> Access to the Services under a Coding Harness Subscription is enabled by a
> Meta Model API key or other credential that Meta connects for use with the
> coding harness. That key or credential is for use only with the coding
> harness under your Coding Harness Subscription, is subject to the
> restrictions on Meta Model API keys in Section 3.1, and may not be used to
> access the Services outside the coding harness or to circumvent your
> subscription's usage limits or billing.

The subscription page says the same in plain words: "This credential is for
use with Muse Code only" and "It works only through the Muse Code CLI while
signed in" (`sources/muse-code-subscriptions.md`).

Consequences:

1. A `claude-code`/`openai-codex`-style door (lm15 holds the subscription
   key and calls `api.meta.ai` itself) is the use § 3.2 forbids. The account
   at risk is a **Meta Account**, the one linked across Facebook, Instagram
   and WhatsApp (§ 3.1).
2. lm15 already ships this door: the `meta` login method `device`
   (`lm15/login/flows/meta.py` and its ports, profile `auth/managed/profiles.json`
   `providers/meta`), ported from Pi 0.87.0, which predates these terms. It
   mints exactly the key § 3.2 restricts and sends it to the public API.
   It is marked `unverified` and has no receipt.
3. Subscription use is **Contributor mode by default** (§ 3.3): prompts,
   files and answers may be used to train Meta models unless the account
   setting is changed.

## How Muse Code signs in (Muse Code 1.4.6, read from the binary)

- `muse login`: RFC 8628 device code at `https://auth.meta.com`
  (`/oidc/device/authorization/`, `/oidc/device/token/`), client id
  `1031625952748946`. The identity token is not accepted for inference.
- Key mint: `POST https://api.meta.ai/muse-code/key`, `Authorization: Bearer
  <identity token>`, `x-api-version: 1.0.0`. The reply (`MintedKey`, 15
  fields) carries `api_key` **and a `base_url`** ("mint response missing
  api_key or base_url"), plus `require_payment`, `action_url`, `user_*`,
  `is_subs_active`, `subs_tier_id`, `subs_tier_name`,
  `is_subs_upgrade_available`, `has_payment_method`, `can_subscribe`,
  `subs_usage` (5-hour and weekly windows: `used_percent`, `resets_at`,
  `window_duration_mins`). Errors it names: `MODEL_API__ONBOARDING_REQUIRED`,
  payment method missing (Model API), subscription missing
  (`https://accountscenter.meta.com/muse_code/?ep=no_payg`).
  The Pi port ignored `base_url` and every subscription field; lm15 now
  reads both (`changes/2026-10-12-muse-code-subscription.md`). Live, the
  mint answers the same key on every call.
- Stored at `~/.config/muse/auth.json` (honours `XDG_CONFIG_HOME`, not
  `HOME`), `providers.meta`: `access_token`, `obtained_via`, `refresh_token`,
  `expires_at`, `api_key`, `api_base_url`, `user_full_name`, `user_email`,
  `user_avatar_url`, `subs_active`; or `{api_key}` for a pasted key.
- Precedence (docs): `META_API_KEY`, then a stored key, then the browser
  login. An ambient `META_API_KEY` therefore turns a subscriber's Muse Code
  into pay-as-you-go.

## What Muse Code sends (offline capture, fake key, `--base-url` to localhost)

- `GET {root}/muse-code/models` (the model list lives under `/muse-code/`,
  not `/v1/models`).
- `POST {base}/responses`: plain OpenAI Responses, streaming,
  `store: false`, `reasoning: {effort, summary: "auto"}`,
  `include: ["reasoning.encrypted_content"]`, `prompt_cache_key`,
  `max_output_tokens: 128000`.
- Headers: `authorization: Bearer <key>`, `x-client-id: tbh:exec`,
  `user-agent: muse-build/1.4.6 (non-interactive; linux-x86_64; build …)`,
  `x-tbh-session-id`, `x-meta-ai-gateway-session-id`, `x-tbh-agent-role`,
  `traceparent`.

## Models

- `muse-wonder-1.0`: Model API (pay-as-you-go, Standard mode only) and Muse
  Code (every plan). Already reachable through lm15's `meta` provider with a
  `META_API_KEY`.
- **Muse Wonder Full**: `muse-wonder-full-1.0` (and
  `muse-wonder-full-1.0-contributor`), Power or Maximum Usage plan only.
  Listed by both `/muse-code/models` and `/v1/models` for the minted key,
  and answers on the Responses, Chat Completions and Messages wires (live
  2026-10-12).

## Options the maintainer was given (B chosen 2026-10-12)

- **A. Drive Muse Code itself.** lm15 runs `muse serve` (the published MSP
  session protocol over stdio) or `muse exec --json`; Muse Code holds the
  login. Within § 3.2. Cost: every call is a Muse Code agent turn with its
  own system prompt and tools, so lm15's exact-messages, caller-tools and
  structured-output semantics do not map one to one.
- **B. Direct door anyway** (as `claude-code`/`openai-codex`). Fastest and
  gives the clean lm15 interface; breaches § 3.2 and risks the Meta Account.
- **C. No subscription door.** Keep `meta` with a `META_API_KEY`
  (pay-as-you-go `muse-wonder-1.0`); retire or relabel the `device` method,
  since it mints the restricted key.
