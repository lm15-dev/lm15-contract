> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Reliability and Error Handling

> Recommended patterns for timeouts, retries, and error handling when building production applications on the Fireworks API.

Building reliable applications requires handling network conditions, transient errors, and long-running requests. This guide covers recommended patterns for production use.

## Timeout configuration

Set timeouts based on your workload type:

| Workload                             | Recommended client timeout     |
| ------------------------------------ | ------------------------------ |
| Interactive / chat                   | 30–60 seconds                  |
| Agentic (tool calls, multi-step)     | 5–30 minutes                   |
| Large model inference (long context) | 10–30 minutes                  |
| Batch job submission                 | 60 seconds (results are async) |

### Python SDK

```python theme={null}
from openai import OpenAI
import httpx

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<your-api-key>",
    timeout=httpx.Timeout(
        connect=10.0,
        read=1800.0,   # 30 min for long generations
        write=30.0,
        pool=10.0,
    ),
)
```

### Raw HTTP

```python theme={null}
import requests

response = requests.post(
    "https://api.fireworks.ai/inference/v1/chat/completions",
    headers={"Authorization": "Bearer <your-api-key>"},
    json={"model": "...", "messages": [...]},
    timeout=(10, 1800),  # (connect, read) in seconds
)
```

## Retry logic

### Which errors are retryable

| Status | Meaning               | Retry?                           |
| ------ | --------------------- | -------------------------------- |
| `429`  | Rate limit            | ✅ Yes — with backoff             |
| `500`  | Internal server error | ✅ Yes — transient                |
| `502`  | Bad gateway           | ✅ Yes — transient                |
| `503`  | Service unavailable   | ✅ Yes — with backoff             |
| `504`  | Gateway timeout       | ✅ Yes — transient                |
| `400`  | Bad request           | ❌ No — fix the request           |
| `401`  | Unauthorized          | ❌ No — check API key             |
| `404`  | Not found             | ❌ No — check model/deployment ID |
| `422`  | Unprocessable entity  | ❌ No — fix the request body      |

### Exponential backoff with jitter

```python theme={null}
import time, random
from openai import OpenAI, RateLimitError, APIStatusError

def call_with_retry(client, max_retries=5, base_delay=1.0, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
        except APIStatusError as e:
            if e.status_code in (500, 502, 503, 504):
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            else:
                raise
```

### OpenAI SDK built-in retry

```python theme={null}
client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<your-api-key>",
    max_retries=3,
)
```

## Handling 429 rate limits

**On serverless:** Limits scale automatically with sustained usage. For immediate capacity, contact support or switch to a dedicated deployment.

**On dedicated deployments:** Increase concurrency by raising replica counts (for example with `firectl deployment update` and autoscaling settings). See [Autoscaling](/deployments/autoscaling).

## Long-running training jobs

For RL / RFT trainer jobs, use [`reconnect_and_wait`](/fine-tuning/training-api/reference/trainer-job-manager) on the job manager to recover from preemption or transient failures. See [Trainer job manager](/fine-tuning/training-api/reference/trainer-job-manager) for parameters and examples.

To preserve optimizer state across interruptions, set `dcp_save_interval` in your training config. See [RFT parameters reference](/fine-tuning/rft-parameters-reference).

## The analytics dashboard vs. client-side failures

The Fireworks analytics and usage views count **server-acknowledged requests**. They do not capture connection errors that occur before a request reaches the server — those appear as failures on the client but may show as zero or reduced traffic in the console.

If your client shows failures but the dashboard looks clean, the issue is likely client-side: timeout before connection, DNS resolution failure, or network path problems.

Use [Exporting metrics](/deployments/exporting-metrics) for per-deployment Prometheus metrics that reflect what Fireworks infrastructure observed for dedicated deployments.
