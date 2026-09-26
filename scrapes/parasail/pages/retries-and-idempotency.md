> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/operate-in-production/retries-and-idempotency.md).

# Retries and Idempotency

Handle 429 responses and transient errors with exponential backoff, sensible timeouts, and safe retries against the Parasail API.

Production clients should expect occasional transient errors and retry them safely. This page covers when Parasail returns `429 Too Many Requests`, how to back off, how to set timeouts, and what you can and can't assume about retry idempotency.

## When you'll see `429 Too Many Requests`

A `429` means a request was throttled and should be retried later. There are two common causes on Parasail:

* **Account rate limits.** Every account has a requests-per-minute (RPM) limit based on its product tier. Exceeding it returns `429`. See [Limits and quotas](/parasail-docs/operate-in-production/limits-and-quotas.md#rate-limits) for the per-tier limits and how to raise them.
* **Dedicated max concurrent connections.** A Dedicated Instance returns **429 Too Many Requests** when concurrent requests reach the **Max Concurrent Connections per Replica** limit, until space frees up. This protects quality of service and works in tandem with autoscaling. See [Dedicated Instances](/parasail-docs/products/overview-1.md) and [Auto-Scaling](/parasail-docs/products/overview-1/auto-scaling.md).

In both cases the right response is the same: wait, then retry with backoff.

## Exponential backoff

Retry transient errors (`429`, and `5xx` server errors) with exponential backoff and jitter, rather than retrying immediately in a tight loop. Cap the number of attempts so a request can't retry forever.

The OpenAI Python SDK already retries certain errors automatically; you can configure `max_retries` on the client and still wrap calls for full control:

```python
import random
import time

from openai import OpenAI, APIStatusError, APITimeoutError, APIConnectionError

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>",
    timeout=30,        # seconds; fail fast instead of hanging
    max_retries=0,     # disable built-in retries so we control backoff here
)

def chat_with_backoff(messages, model, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return client.chat.completions.create(model=model, messages=messages)
        except (APITimeoutError, APIConnectionError):
            retryable = True
        except APIStatusError as e:
            # Retry on throttling and server errors; fail fast on 4xx like 400/401/404.
            retryable = e.status_code == 429 or e.status_code >= 500
            if not retryable:
                raise
        if attempt == max_attempts - 1:
            raise
        # Exponential backoff with full jitter: 1s, 2s, 4s, ... plus randomness.
        sleep = min(2 ** attempt, 30) * (0.5 + random.random() / 2)
        time.sleep(sleep)

response = chat_with_backoff(
    messages=[{"role": "user", "content": "Hello"}],
    model="<your-model>",
)
print(response.choices[0].message.content)
```

## Setting timeouts

Always set a client-side timeout so a stalled connection fails fast and can be retried, instead of hanging indefinitely. The example above sets `timeout=30` on the client; you can also override it per request:

```python
client.with_options(timeout=60).chat.completions.create(...)
```

Choose a timeout that comfortably exceeds your model's expected latency. Long generations and large batch-style requests need more headroom than short completions.

## Safe retries and idempotency

Retrying is only safe if a duplicated request can't cause unintended side effects. For Parasail's inference endpoints (chat completions, embeddings), a retried request simply produces another completion—there is no state to corrupt—so retrying a failed or timed-out call is generally safe. The main caveat is that you may be **billed for both** a request that actually succeeded server-side and its retry, if the original response was lost in transit.

Parasail exposes an **OpenAI-compatible API**, and the repository does not document an idempotency-key mechanism. Treat retries as **not guaranteed idempotent**: a retry can result in a second execution rather than returning the original response. To limit duplicate work:

* Keep `max_attempts` small and only retry genuinely retryable errors (`429`, `5xx`, timeouts).
* For **batch** workloads, prefer the per-request `custom_id` to match outputs to inputs and resubmit only the requests that failed, rather than resubmitting whole batches. See [Batch Troubleshooting](/parasail-docs/products/quickstart/troubleshooting.md).

The public Parasail docs do not define an idempotency-key header. If your workflow cannot tolerate duplicate execution, deduplicate on the client side with your own request IDs and only retry operations that are safe to run again.

## Next steps

* [Limits and quotas](/parasail-docs/operate-in-production/limits-and-quotas.md#rate-limits)—per-tier RPM limits and increases
* [Operate in Production](/parasail-docs/operate-in-production/overview.md)—the full operations hub
* [Dedicated Instances](/parasail-docs/products/overview-1.md)—max concurrent connections and 429 behavior
* [Batch Troubleshooting](/parasail-docs/products/quickstart/troubleshooting.md)—handling per-request failures
