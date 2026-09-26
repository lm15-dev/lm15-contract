> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Rate limits

> Together AI applies dynamic per-model rate limits that scale with your sustained traffic on serverless inference.

Rate limits cap how often you can call Together AI [serverless models](/docs/serverless/models). They protect platform capacity and keep the service available across users. Limits are set per organization and per model, and they adjust based on your recent usage.

Requests that exceed your limit return a `429 Too Many Requests` error.

## Dynamic rate limits

Together uses dynamic rate limits instead of fixed thresholds. Each organization has a dynamic rate per model that adjusts based on:

* The model's live capacity.
* Your recent successful usage on that model.

Sustained, successful traffic raises your dynamic rate over time. Sudden spikes far above your recent usage may be throttled.

The exact formula is evolving as Together tunes the system, but the practical takeaway is that steady, successful traffic raises your limit, and bursts well beyond your recent usage do not.

### How Together handles traffic spikes

The Together platform buffers sudden traffic spikes so that every user keeps receiving timely responses. Best-effort smoothing absorbs most bursts before any limiting is applied.

If a burst still produces failures, the error code you get back depends on whether the failed request was below or above your dynamic rate:

* **Requests at or below your dynamic rate** return `503 Service Unavailable`. These failures are attributed to platform capacity, i.e., the model is overloaded and unable to serve requests (not due to your usage).
* **Requests above your dynamic rate** return `429 Too Many Requests` with one of these error types:
  * `error_type: "dynamic_request_limited"` for request-based limiting.
  * `error_type: "dynamic_token_limited"` for token-based limiting.

### Rewards for sustained traffic

Steady traffic helps Together predict demand and scale capacity over time. If your request rate increases gradually and stays consistent, your success rate will improve, which raises your dynamic rate (the burst cushion based on recent successful usage). The platform then ramps up capacity to match the new steady load, leaving more headroom for future bursts.

## Best practices

To maximize successful requests on serverless models:

* Stay within your rate limit.
* Send steady, consistent traffic. Avoid bursts.

For example, if your limit is 60 requests per minute (RPM), send roughly 1 request per second (RPS) across the minute rather than 60 requests in a single second. The shorter the window you concentrate requests into, the burstier the traffic. Together does its best to serve bursty traffic, but success depends on the model's real-time load and available capacity at that moment.

When a request is rate limited, the `429` response includes `x-ratelimit-reset`, which reports the suggested retry interval for the model. Consider using **exponential backoff** so requests continue trying again with increasing wait times, instead of failing immediately. For spend and usage trends across keys and workloads, see your project's [cost analytics page](https://api.together.ai/settings/projects/~current/cost-analytics).

### Inspect your current rate limit

Dynamic rate limits adjust with usage, so there are no fixed per-model limits published. The most reliable signal is the response itself: successful requests come back without rate-limit headers, and when you hit a `429` the response includes `x-ratelimit-reset` with the number of seconds to wait before retrying.

<CodeGroup>
  ```python Python theme={null}
  import os
  from together import Together

  client = Together(api_key=os.environ["TOGETHER_API_KEY"])

  response = client.chat.completions.with_raw_response.create(
      model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
      messages=[{"role": "user", "content": "ping"}],
  )

  reset = response.http_response.headers.get("x-ratelimit-reset")
  if reset is None:
      print("status:", response.http_response.status_code, "(not rate limited)")
  else:
      print("rate limited, retry in", reset, "seconds")
  ```

  ```bash cURL theme={null}
  curl -i https://api.together.ai/v1/chat/completions \
    -H "Authorization: Bearer $TOGETHER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
      "messages": [{"role": "user", "content": "ping"}]
    }' | grep -i "x-ratelimit-reset" || echo "not rate limited"
  ```
</CodeGroup>

If you need a known, fixed limit (for capacity planning or strict SLAs), use a [dedicated endpoint](/docs/dedicated-endpoints/overview) instead.

## Alternatives for high-volume or bursty workloads

If your workload needs higher throughput or runs in large bursts, consider:

* [Batch inference](/docs/inference/batch/overview) for high request or token volumes when latency is not critical. You pay for what you use, with discounts on most models.
* [Provisioned throughput](/docs/inference/provisioned-throughput) for production workloads on stock models that need a defined SLA covering committed throughput (TPM) and reliability.
* [Dedicated inference](/docs/dedicated-endpoints/overview) for predictable, reserved capacity that you control. Use it for fine-tuned models, or workloads that need direct control over hardware, latency, and throughput.
