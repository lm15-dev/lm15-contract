---
meta:
  title: Error handling
  description: Handle API errors, troubleshoot common issues, and build resilient Meta Model API integrations with proper retry logic.
  keywords: error handling, HTTP status codes, troubleshooting, retry logic, API errors
cms:
  alias: /model-api/docs/error-handling
  target: aidmc
---

# Error handling

Ship integrations that keep working when the API returns an error, hits a rate limit, or fails transiently. Meta Model API uses standard HTTP status codes and returns a descriptive error object that points to the problem.

## Error response format {#error-format}

A failed request returns a JSON error object:

```json
{
  "error": {
    "message": "`top_p`: The number must be `<= 1.0`.",
    "type": "invalid_request_error",
    "param": "top_p",
    "code": null
  }
}
```

| Field | Type | Description |
| :---- | :---- | :---- |
| `message` | string | Human-readable detail. This is the most reliable field for diagnosis. |
| `type` | string | Error category: `invalid_request_error` for 4xx validation and not-found errors, `authentication_error` for 401, `rate_limit_error` for 429, or `server_error` for 5xx. |
| `param` | string or null | Request field that caused the error, when applicable, such as `top_p` or `tools`. |
| `code` | string or null | Machine-readable code. Frequently `null` on validation errors, so prefer `type` and `message` for handling. Populated for cases such as `invalid_api_key`, `model_not_found`, `file_not_found`, `rate_limit_exceeded`, `server_shutting_down`, `service_overloaded`, `backend_unavailable`, `payload_too_large` for a request body over a size limit, `gateway_timeout` (a non-streaming request that ran past the server-side time limit), and `content_policy_violation` for a media content-policy denial. |

> [!NOTE] 404s have no error body
> A request to an unknown path returns `HTTP 404` with an **empty response body**: there is no JSON `error` envelope. Detect routing mistakes from the status code directly. Only matched endpoints return the JSON shape above.

> [!NOTE] Files list returns plain-text errors
> Query-string validation on the Files list endpoint (`GET /v1/files`) is a similar exception: an invalid `order` value such as `?order=sideways` currently returns `HTTP 400` with a plain-text body (`Content-Type: text/plain`), not the JSON `error` envelope. Branch on status code and `Content-Type` rather than assuming JSON on every 4xx from `/v1/files`.

## HTTP status codes {#status-codes}

### 400 Bad Request {#400}

The server could not process the request because a parameter was missing or invalid.

**Common causes:**
- Missing required parameters such as `model` or `messages`
- Invalid parameter values such as `temperature` outside the 0–2 range, or `top_p` outside `0 < top_p ≤ 1`, including `top_p: 0`
- `max_output_tokens` below the minimum of 16 on the Responses API
- Request input plus the requested output budget exceeds the model's context window: `input_tokens + max_output_tokens` must fit within it (see [Context window exceeded](#context-window-exceeded))
- Uploading or inlining a file larger than the size limit (up to 1 GiB via the Files API, 50 MB inline)
- Combining mutually exclusive features
- Declaring a function tool whose name collides with a built-in tool name reserved by `web_search` (returns `param: tools`)
- Invalid JSON in request body
- Duplicate `reasoning_id` values in Responses API requests
- Invalid conversation structure, such as a `function_call_output` whose `call_id` matches no `function_call`, a replayed `reasoning` item not followed by an assistant message or `function_call`, or intermediate assistant text replayed before a `function_call` without `phase: "commentary"` (see [Invalid conversation structure](#invalid-conversation-structure))
- Invalid message structure such as empty input, or unsupported role/turn combinations that violate the model's input-shape requirements
- Submitting media (a file, image, or inline content) that does not meet Meta's content policy; returns `code: content_policy_violation`
- Providing an image or media URL that cannot be fetched: for example, blocked by `robots.txt`, denied by fetch policy, failing DNS resolution, or otherwise unreachable. The error message identifies the specific fetch failure, for example an unreachable URL or a `robots.txt` denial
- Submitting a corrupt or truncated image whose bytes cannot be decoded; the error message identifies the affected image (`type: invalid_request_error`, `code: null`)
- Submitting an audio or video file that cannot be decoded: for example, an audio container with no audio track, a format the decoder does not recognize, or empty/corrupt media. The error message identifies the decode failure (`type: invalid_request_error`, `code: null`)

**Fix:** Read `message` and `param` to identify the problem. `code` is typically `null` for validation errors. Check the [API reference](/docs/api-reference/chat-completions) for valid parameter combinations.

### 401 Unauthorized {#401}

The API key was missing, invalid, or revoked.

**Common causes:**
- Missing `Authorization` header
- Malformed API key (not in `LLM|{id}|{secret}` format)
- Revoked or deleted API key
- Typo in the API key

```shell title="curl"
curl -X POST "https://api.meta.ai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model": "muse-spark-1.1", "messages": [...]}'
```

```json
{
  "error": {
    "message": "Unauthorized",
    "type": "authentication_error",
    "param": null,
    "code": "invalid_api_key"
  }
}
```

Both a missing key and an invalid, malformed, or revoked key return `type: authentication_error` with `code: invalid_api_key`.

**Fix:** Send a valid `Authorization: Bearer $MODEL_API_KEY` header. Verify the key in the [Model API dashboard](/) and that `MODEL_API_KEY` is set correctly. See [Authentication](/docs/authentication) for setup.

### 402 Payment Required {#402}

The request cannot be completed due to a billing issue.

**Common causes:**
- Insufficient balance or a lapsed payment method
- Billing account issue

```json
{
  "error": {
    "message": "Billing account issue. Please check your account status.",
    "type": "billing_error",
    "param": null,
    "code": "billing_not_configured"
  }
}
```

**Fix:** Check account status and billing details in the [Model API dashboard](/). Ensure your payment method is valid and your balance is sufficient.

### 403 Forbidden {#403}

The API key does not have permission to access the requested resource.

**Common causes:**
- API key lacks permission for the requested model or feature
- Team restrictions on specific endpoints

**Fix:** Verify your API key has access to the requested model and features in the [Model API dashboard](/).

### 404 Not Found {#404}

The requested resource does not exist.

**Common causes:**
- Invalid endpoint URL (typo in path)
- Referencing a non-existent file ID
- Referencing a non-existent model

```shell title="curl"
curl https://api.meta.ai/v1/files/file-nonexistent \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

```json
{
  "error": {
    "message": "No file found with id 'file-nonexistent'.",
    "type": "invalid_request_error",
    "param": null,
    "code": "file_not_found"
  }
}
```

Not-found errors carry a populated `code`: an unknown **model** returns `model_not_found` and an unknown **file** returns `file_not_found`. Branch on status and `type`, which are stable, rather than parsing `message`:

```json
{
  "error": {
    "message": "The model `bogus-model` does not exist or is not available",
    "type": "invalid_request_error",
    "param": null,
    "code": "model_not_found"
  }
}
```

**Fix:** Verify the resource ID. For files, list uploaded files via `GET /v1/files` to confirm the ID still exists. If you get a [503](#503) instead of a 404 when specifying a model, the registry lookup was inconclusive due to a transient backend issue — retry rather than treating the model as missing.

### 413 Payload Too Large {#413}

The request body exceeded a size limit.

**Common causes:**
- A background request (`background: true` on the Responses API) whose body exceeds **1 MiB** (1,048,576 bytes). This cap applies only to background creation requests and is measured on the JSON body, so a request that is valid synchronously can exceed it once `background: true` is set. It is much smaller than the 50 MB inline-media limit. See [Responses API → Background responses](/docs/protocols/responses#using-with-other-features).
- A `store=true` request with large inline base64 media that succeeds at inference but is too large to persist. Inference completes and the response is usable, but persistence fails because the serialized payload exceeds the storage tier's frame limit. The API returns 413 instead of a generic 503 so you can act on it. This applies to the non-streaming Responses path.

```json
{
  "error": {
    "message": "request body too large for background mode (1300000 bytes, max 1048576)",
    "type": "invalid_request_error",
    "param": null,
    "code": "payload_too_large"
  }
}
```

```json
{
  "error": {
    "message": "This response could not be stored because the request is too large (~16 MB) to persist with `store=true`. Upload large media via the Files API and reference it by `file_id` instead of inlining base64 data, or retry with `store=false`.",
    "type": "invalid_request_error",
    "param": null,
    "code": "payload_too_large"
  }
}
```

**Fix:** Reduce the body below the applicable limit. For background mode, stay under 1 MiB. For `store=true` persistence failures, upload large media via the [Files API](/docs/file-handling) and reference it by `file_id` instead of inlining base64, or set `store=false` if you do not need the response persisted. An uploaded file's bytes do not count toward the persisted payload. Do not retry unchanged.

### 429 Too Many Requests {#429}

Your team has exceeded the rate limit.

**Common causes:**
- Exceeding your team's requests-per-minute (RPM) limit
- Exceeding your team's tokens-per-minute (TPM) limit

The per-tier RPM and TPM values are listed in [Pricing and rate limits](/docs/pricing-rate-limits#rate-limits).

```json
{
  "error": {
    "message": "Rate limit exceeded. Please retry after 15 seconds.",
    "type": "rate_limit_error",
    "param": null,
    "code": "rate_limit_exceeded"
  }
}
```

**Fix:** Implement exponential backoff with jitter. The response includes a `Retry-After` header that tells you how long to wait. See [Pricing and rate limits](/docs/pricing-rate-limits) for retry strategy and proactive throttling using rate limit headers.

### 500 Internal Server Error {#500}

An unexpected error occurred on the server.

**Common causes:**
- Temporary service disruption
- Unexpected server-side issue
- Model output parsing failure: the model produced malformed output. This is not caused by your input and is safe to retry.

**Fix:** Retry with exponential backoff. If 500s persist after several retries, check the [API status page](/status) or contact support so we can investigate.

### 503 Service Unavailable {#503}

The server is temporarily unable to handle the request. Common causes:

- **Rolling deploy or restart** — the instance you reached is draining connections. Returns `code: server_shutting_down`.
- **Backend overload** — the backend has reached its active request limit. Returns `code: service_overloaded` with a `Retry-After: 60` header telling you how long to wait before retrying.
- **Backend unavailable** — a backend dependency was temporarily unreachable, so the request could not be fulfilled (for example: no available host, missing backend config, or a retryable upstream failure). Returns `code: backend_unavailable`. The model-lookup service is one such dependency: when it is the cause, the 503 means the API could not determine whether the requested model exists — distinct from a genuine model-not-found (which returns [404](#404) with `code: model_not_found`), where the model is confirmed absent.

```json
{
  "error": {
    "message": "Server is shutting down. Please retry your request.",
    "type": "server_error",
    "param": null,
    "code": "server_shutting_down"
  }
}
```

```json
{
  "error": {
    "message": "The backend is temporarily overloaded. Please retry.",
    "type": "server_error",
    "param": null,
    "code": "service_overloaded"
  }
}
```

```json
{
  "error": {
    "message": "The backend is temporarily unavailable. Please retry.",
    "type": "server_error",
    "param": null,
    "code": "backend_unavailable"
  }
}
```

All three cases are **always retryable**: replay the request and it routes to a healthy instance or the backend recovers. Each response carries a `Retry-After` header telling you how long to wait (`service_overloaded` and `backend_unavailable` use 60 seconds; `server_shutting_down` uses a shorter window of a few seconds, since the instance is only draining) — honor it before retrying, and fall back to your own exponential backoff if the header is absent. When a shutdown happens mid-stream, it arrives as a terminal `error` SSE event with `code: server_shutting_down` before the stream closes; detect it and retry the full request (see [Streaming errors](#streaming-errors)).

**Fix:** Retry with exponential backoff. These errors are transient and resolve without developer action.

### 504 Gateway Timeout {#504}

A **non-streaming** request ran past the server-side non-streaming time limit before a response was produced. The server drops the in-flight request and returns `HTTP 504` with a message advising you to switch to streaming.

```json
{
  "error": {
    "message": "Request exceeded the non-streaming server time limit before a response was produced. For large or slow requests, use the streaming API by setting \"stream\": true.",
    "type": "server_error",
    "param": null,
    "code": "gateway_timeout"
  }
}
```

This applies only to non-streaming requests. Streaming requests are not subject to this limit, because they return output incrementally as it is generated.

**Fix:** Do **not** simply retry — a repeated non-streaming request will usually exceed the limit again. Instead:

- **Stream the response** by setting `stream: true`. This is the recommended path for long or large generations and avoids the deadline entirely. See streaming on the [Responses API](/docs/protocols/responses#streaming) and [chat completion](/docs/protocols/chat-completions#streaming).
- **Run it in the background** with `background: true` on the [Responses API](/docs/protocols/responses#using-with-other-features), then poll or stream-retrieve the result.
- **Reduce the work per request** — shorter input, a smaller `max_output_tokens`, or a lower `reasoning_effort`.

## Handling errors in code {#handling-errors}

### Python (OpenAI SDK) {#python}

The OpenAI SDK raises typed exceptions. Branch on the type and retry only what is retryable:

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

client = OpenAI(
    api_key=os.environ["MODEL_API_KEY"],
    base_url="https://api.meta.ai/v1",
)

try:
    response = client.chat.completions.create(
        model="muse-spark-1.1",
        messages=[
            {"role": "user", "content": "Hello!"}
        ],
    )
    print(response.choices[0].message.content)

except AuthenticationError as e:
    # 401 Unauthorized - invalid API key
    print(f"Authentication failed: {e}")
    # Check your API key and ensure MODEL_API_KEY is set correctly

except RateLimitError as e:
    # 429 Too Many Requests - implement retry logic
    print(f"Rate limit exceeded: {e}")
    # Implement exponential backoff with jitter
    # See Rate limits page for retry strategy

except APIError as e:
    # 400, 402, 403, 404, 500, 503 errors
    print(f"API error: {e.status_code} - {e.message}")
    if e.status_code == 400:
        # Bad request - check parameters
        pass
    elif e.status_code == 402:
        # Billing issue - check account status
        pass
    elif e.status_code >= 500:
        # Server error - retry with backoff
        pass

except Exception as e:
    # Unexpected errors
    print(f"Unexpected error: {e}")
```

### TypeScript (OpenAI SDK) {#typescript}

```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.MODEL_API_KEY,
  baseURL: "https://api.meta.ai/v1",
});

try {
  const response = await client.chat.completions.create({
    model: "muse-spark-1.1",
    messages: [
      { role: "user", content: "Hello!" }
    ],
  });
  console.log(response.choices[0].message.content);

} catch (error) {
  if (error instanceof OpenAI.AuthenticationError) {
    // 401 Unauthorized
    console.error("Authentication failed:", error.message);
  } else if (error instanceof OpenAI.RateLimitError) {
    // 429 Too Many Requests
    console.error("Rate limit exceeded:", error.message);
    // Implement exponential backoff
  } else if (error instanceof OpenAI.APIError) {
    // 400, 402, 403, 404, 500, 503
    console.error(`API error ${error.status}:`, error.message);
  } else {
    // Unexpected errors
    console.error("Unexpected error:", error);
  }
}
```

### curl {#curl}

When using curl, check the HTTP status code and parse the error body:

```shell title="curl"
response=$(curl -s -w "\n%{http_code}" -X POST "https://api.meta.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "muse-spark-1.1",
    "messages": [{"role": "user", "content": "Hello"}]
  }')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  echo "Success: $body"
elif [ "$http_code" -eq 429 ]; then
  echo "Rate limit exceeded. Retry after delay."
  # Implement exponential backoff
elif [ "$http_code" -eq 401 ]; then
  echo "Authentication failed. Check your API key."
else
  echo "Error $http_code: $body"
fi
```

## Retry strategy {#retry-strategy}

For transient errors (429, 500, 503), use exponential backoff with jitter:

```python title="Python (OpenAI SDK)"
import os
import time
import random
from openai import OpenAI, RateLimitError, APIError

client = OpenAI(
    api_key=os.environ["MODEL_API_KEY"],
    base_url="https://api.meta.ai/v1",
)

def create_completion_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="muse-spark-1.1",
                messages=messages,
            )
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff with jitter: 2^attempt + random(0-1) seconds
            delay = (2 ** attempt) + random.random()
            print(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
        except APIError as e:
            if e.status_code >= 500 and attempt < max_retries - 1:
                # Retry server errors
                delay = (2 ** attempt) + random.random()
                print(f"Server error. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                raise

# Usage
response = create_completion_with_retry([
    {"role": "user", "content": "Hello!"}
])
```

**Best practices:**
- Start with a short delay (0.5-1 second) and double it on each retry
- Add random jitter (0-1 second) to avoid thundering-herd effects
- Limit retries to 3-5 attempts
- Do not retry 400, 401, 402, 403, 404, or 413 errors: these require fixing the request
- Log all errors for monitoring and debugging

## Streaming errors {#streaming-errors}

When you stream a response (`stream: true` on the Responses API), a failure mid-stream is delivered as a terminal server-sent event rather than an HTTP error status. Two terminal error events are possible:

- **`response.failed`**: a response-lifecycle event carrying the full response object with `status: "failed"` and a non-null `error` object. Used for response-level failures.
- **`error`**: a stream-interrupting event (`type: "error"`) emitted when the backend stream itself fails, such as a `server_shutting_down` shutdown mid-stream (see [503](#503)). It carries `code` and `message` at the top level rather than inside a response object.

In both cases the `code` is machine-readable (for example `server_error`, `rate_limit_exceeded`, or `server_shutting_down`) and `message` is sanitized: internal details are never exposed.

Handle both terminal events in your event loop alongside `response.completed` and `response.incomplete` so your application surfaces mid-stream failures to users. See [Responses API → Streaming](/docs/protocols/responses#streaming).

## Common issues and solutions {#common-issues}

### Invalid API key format {#invalid-key-format}

**Error:** `Unauthorized` (401), with `type: authentication_error` and `code: invalid_api_key`

**Cause:** API key not in `LLM|{numeric_id}|{secret}` format.

**Solution:** Copy the full key from the [Model API dashboard](/). Ensure no extra spaces or quotes. The key should start with `LLM|` and contain two pipe characters.

### Model not found {#model-not-found}

**Error:** `The model {model_id} does not exist or is not available` (404)

**Cause:** Typo in model ID or requesting a model your team does not have access to.

**Solution:** Use `muse-spark-1.1` (lowercase, hyphenated). List available models via `GET /v1/models` to verify access. See [Models](/docs/models) for the current lineup.

### File not found {#file-not-found}

**Error:** `No file found with id '{file_id}'.` (404)

**Cause:** Referencing a deleted file or typo in file ID.

**Solution:** List files via `GET /v1/files` to confirm the ID exists and has not been deleted. File IDs start with `file-`.

### Invalid reasoning ID {#invalid-reasoning-id}

**Error:** `Invalid reasoning ID format` (400)

**Cause:** Responses API request includes a `reasoning` item with an invalid ID.

**Solution:** Pass the reasoning item's `id` back unchanged: it is an `rs_`-prefixed value such as `rs_abc123`. Or omit `id` entirely, which is optional on input when `encrypted_content` is present. Include `encrypted_content` by requesting it via `include: ["reasoning.encrypted_content"]` with `store: false`. See [Responses API](/docs/protocols/responses#reasoning-items) for details.

### Invalid conversation structure {#invalid-conversation-structure}

**Error:** `HTTP 400` with `type: invalid_request_error` and a message describing the structural problem.

**Cause:** The `messages` array (Chat Completions) or `input` array (Responses API) is ordered in a way the server cannot interpret. The API validates structure and rejects sequences it cannot safely interpret rather than guessing intent. Common cases:

- A `function_call_output` whose `call_id` does not match any `function_call` in the same request (when no `previous_response_id` is set):

```json
{
  "error": {
    "message": "function_call_output call_id 'call_xyz' does not match any function_call call_id in the same request",
    "type": "invalid_request_error",
    "param": "call_id",
    "code": null
  }
}
```

- A replayed `reasoning` item not followed by an assistant message or `function_call` before a new `user`, `system`, or `developer` message:

```json
{
  "error": {
    "message": "Invalid conversation structure: reasoning items must be followed by an assistant message or function call before a new user, system, or developer message",
    "type": "invalid_request_error",
    "param": "input",
    "code": null
  }
}
```

- Intermediate assistant text replayed as a final answer immediately before a `function_call`. Tag intermediate assistant content with `phase: "commentary"` instead. See [Responses API → message phase](/docs/protocols/responses#message-phase).

**Solution:** Send well-formed history. For Chat Completions, follow every assistant `tool_calls` message with one `tool` message per call that carries the matching `tool_call_id`. For Responses API, keep `function_call` / `function_call_output` pairs consistent, preserve item order, and tag intermediate assistant content with `phase: "commentary"`. When you use `previous_response_id`, the server reconstructs history from stored responses, so these checks are relaxed. Fix the request and resend; do not retry unchanged.

### Context window exceeded {#context-window-exceeded}

**Error:** `HTTP 400`, with a message like `You passed {N} input tokens and requested {M} output tokens. However, the model's context length is only {context_length} tokens...`

**Cause:** Input tokens plus requested output tokens exceed the model's context window. The two share one budget: `input_tokens + max_output_tokens` must fit within the window.

```json
{
  "error": {
    "message": "You passed 1200064 input tokens and requested 1 output tokens. However, the model's context length is only 1048576 tokens, resulting in a maximum input length of 1048575 tokens. Please reduce the length of the input prompt",
    "type": "invalid_request_error",
    "param": null,
    "code": null
  }
}
```

**Solution:** Trim conversation history by dropping older messages or summarizing context, or lower the requested output tokens. To measure input size before sending, call `POST /v1/responses/input_tokens`. See [Chat completion](/docs/protocols/chat-completions#multi-turn) for history management strategies.

## Monitoring and alerting {#monitoring}

Log errors so you can track integration health and alert on regressions:

```python title="Python (OpenAI SDK)"
import logging
import os
from openai import OpenAI, APIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.environ["MODEL_API_KEY"],
    base_url="https://api.meta.ai/v1",
)

try:
    response = client.chat.completions.create(...)
except APIError as e:
    logger.error(
        "API error",
        extra={
            "status_code": e.status_code,
            "error_type": e.type,
            "error_code": e.code,
            "message": e.message,
        }
    )
    # Send to monitoring system (Datadog, Sentry, etc.)
    raise
```

**Monitor these metrics:**
- Error rate by status code, especially 5xx errors
- Rate limit hit frequency (429 errors)
- Authentication failure rate (401 errors), which may indicate leaked keys
- P95/P99 latency for successful requests

## Next steps

- Review [Pricing and rate limits](/docs/pricing-rate-limits) to build a 429 retry strategy and add proactive throttling.
- Set up [Authentication](/docs/authentication) correctly to avoid 401 errors from the start.
- Explore [SDKs and libraries](/docs/sdks) for language-specific error handling patterns you can drop in.
- Check the [API status page](/status) when you see persistent 500s or 503s.