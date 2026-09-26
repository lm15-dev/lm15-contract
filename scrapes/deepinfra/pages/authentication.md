> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Authentication

> API tokens and scoped JWT for secure, scope-limited inference access.

This page covers authenticating **API requests**. For signing in to the dashboard itself, see [Signing In](/account/signing-in).

DeepInfra supports two authentication methods:

1. **API keys** — full-access tokens for your own use
2. **Scoped JWTs** — short-lived, scope-limited tokens you can issue to third parties

## API keys

Get your API keys from the [Dashboard](https://deepinfra.com/dash/api_keys). Use them in the `Authorization` header:

```bash theme={null}
Authorization: Bearer $DEEPINFRA_API_KEY
```

## Scoped JWT

Scoped JWT tokens let you grant limited inference access to third parties without sharing your API key. You can restrict the token by:

* **Models allowed** — specific model(s) only
* **Expiration** — time-limited (up to 1 year)
* **Spending limit** — maximum USD spend

Usage is counted against the API key that was used to sign the JWT.

### Create a scoped JWT

```bash theme={null}
curl -X POST "https://api.deepinfra.com/v1/scoped-jwt" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
  -d '{
      "api_key_name": "auto",
      "models": ["deepseek-ai/DeepSeek-V4-Flash-0731"],
      "expires_delta": 3600,
      "spending_limit": 1.0
  }'
```

Response:

```json theme={null}
{"token": "jwt:eyJhbGciOiJIUzI1NiIsImtpZCxxxxxxxxxxxxxxxxxx"}
```

This creates a token limited to `deepseek-ai/DeepSeek-V4-Flash-0731`, expiring in 1 hour, with a \$1.00 spending limit.

**Optional fields** (omit to remove restriction):

* `models` — allow any model
* `expires_delta` — no expiration (defaults to 1 year)
* `spending_limit` — no spending limit
* Use `expires_at` (unix timestamp) instead of `expires_delta` if preferred

### Inspect a JWT

```bash theme={null}
curl "https://api.deepinfra.com/v1/scoped-jwt?jwtoken=XXXX" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY"
```

```json theme={null}
{
  "expires_at": 1738843515,
  "models": ["deepseek-ai/DeepSeek-V4-Flash-0731"],
  "spending_limit": 1
}
```

### Use a scoped JWT

Use it exactly like a regular API key in the `Authorization` header:

```bash theme={null}
curl "https://api.deepinfra.com/v1/openai/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SCOPED_JWT" \
  -d '{
      "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
      "messages": [{"role": "user", "content": "Hello!"}]
    }'
```

Requests using disallowed models, expired tokens, or over-budget tokens will be rejected.

## JWT format (advanced)

You can create and inspect scoped JWTs yourself using standard JWT libraries.

### Header

```json theme={null}
{
    "alg": "HS256",
    "kid": "di:1000000000000:YXV0bw==",
    "typ": "JWT"
}
```

The `kid` field is `{user_id}:{base64(api_key_name)}` joined with colons. Only `HS256` (HMAC-SHA256) is supported.

### Payload

```json theme={null}
{
    "sub": "di:1000000000000",
    "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
    "exp": 1734616903
}
```

### Signature

```
HMAC_SHA256(
  api_key,
  base64urlEncoding(header) + '.' + base64urlEncoding(payload)
)
```

### Token format

```
jwt:{base64url(header)}.{base64url(payload)}.{base64url(signature)}
```
