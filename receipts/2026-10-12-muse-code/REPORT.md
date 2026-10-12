# 2026-10-12 — Muse Code subscription, live

Account: the maintainer's Meta account, on the **Muse Code Power Usage**
plan (has a payment method). Machine: lambda. Every secret and all personal
data are redacted in `probe.json`.

| Step | Sent by | Result |
|---|---|---|
| Device authorization (`auth.meta.com/oidc/device/authorization/`, Muse Code client id) | stdlib probe | 200; `expires_in` 600, `interval` 5; `verification_uri_complete` on `auth.meta.com/oauth/device/` |
| Device token, code left unapproved | stdlib probe | 400 `{"error": "expired_token", "error_description": "device_code expired."}` at expiry |
| Device token, approved | stdlib probe | 200 `{access_token, token_type: "Bearer"}`: no `expires_in`, no `refresh_token` |
| Key mint (`api.meta.ai/muse-code/key`, `x-api-version: 1.0.0`, `{}`) | stdlib probe (`user-agent: muse-build/1.4.6 …`) | 200; 16 fields: `api_key` (`LLM|…`, 48 characters), `base_url` `https://api.meta.ai/v1`, `is_subs_active` true, `subs_tier_name`, `subs_usage` (5-hour window and weekly), payment and profile fields |
| Second mint, same identity token | stdlib probe | 200, **the same `api_key`** |
| Mint with `user-agent: lm15` | stdlib probe | 200, same fields |
| Mint through `lm15.login.flows.meta.MetaFlow.renew` | lm15-python (this change) | 200; `account_label` "Muse Code Power Usage", `base_url` kept |
| `GET /muse-code/models` | probe, Muse Code headers | 200; 9 ids with Muse Code metadata (context 1,007,997, output 128,000, efforts minimal…max) |
| `GET /v1/models` | probe, with and without Muse Code headers | 200; 12 ids, both Wonder Full variants included |
| `POST /v1/responses` `muse-wonder-1.0` | probe, with and without Muse Code headers | 200 "OK" both times: the server does not check the calling program |
| `POST /v1/responses` `muse-wonder-full-1.0` | probe | 200 "OK" |
| `POST /v1/chat/completions`, `POST /v1/messages` `muse-wonder-full-1.0` | probe | 200 on both wires |
| `complete` and `stream` `meta:muse-wonder-full-1.0` | lm15-python router | 200; "17*23 is 391." (335 output tokens, 318 reasoning); stream start, deltas, end |
| Bogus key on `/v1/models` | probe | 401 `{"error": {"code": "invalid_api_key", "type": "authentication_error"}}` |

Model ids on this plan: `muse-wonder-full-1.0`, `muse-wonder-full-1.0-contributor`,
`muse-wonder-1.0`, `muse-wonder-1.0-contributor`, `muse-spark-1.3`,
`muse-spark-1.3-contributor`, `muse-spark-1.2`, `muse-spark-1.2-contributor`,
`muse-image-1.0` (and, on `/v1/models` only, `sam-3.1`,
`muse-voice-transcribe-1.0`, `muse-spark-1.1`).

Not observed: a full device login driven by lm15-python itself (the probe
sent the same requests; only its `user-agent` differed, and the mint
accepts `lm15`), the key ever expiring, and the identity token ever being
refused.

What Muse Code itself sends for inference (offline capture, fake key,
`--base-url` pointed at localhost) is recorded in
`research/providers/muse-code/README.md`.
