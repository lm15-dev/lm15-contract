> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Serverless Inference Overview

> How Serverless Inference works on Fireworks: serverless modes, billing, request/response headers, prompt caching, model lifecycle, and when to choose Serverless Inference over On-demand

## What is Serverless Inference

Serverless Inference is multi-tenant inference for popular open models running on Fireworks-managed infrastructure. You point your client at `api.fireworks.ai`, send tokens, and pay only for what you use — no GPUs to size, no autoscaler to tune, no cold starts to wait through. Models eligible for Serverless carry the **Serverless** tag in the [model library](https://fireworks.ai/models). To make your first call, see the [Serverless quickstart](/getting-started/quickstart).

## Serverless products at a glance

Three modes run on the same Serverless framework. They share the same rate-limit policy, but route and price differently:

* **Standard** — the default mode. No `service_tier` parameter needed.
* **Priority** — higher reliability during peak periods. Opt in by setting `service_tier: "priority"` on chat completions. Priced at a premium.
* **Fast** — high-speed deployments for latency-sensitive workloads. Selected by switching the `model` ID to a Fast variant (for example, `accounts/fireworks/routers/kimi-k3-fast`).

For usage examples and the full list of supported models, see [Serverless Modes](/serverless/serverless-modes). For pricing by mode, see [Serverless pricing](/serverless/pricing).

## Billing

Serverless is priced per token. Three dimensions are billed:

* **Input tokens** — what you send to the model.
* **Cached input tokens** — input tokens served from prompt cache, discounted (default 50% of input on text and vision models, unless a model lists a different cached rate).
* **Generated tokens** — what the model produces.

Other things to know:

* The `usage` object in each response is the source of truth for what was billed (`prompt_tokens`, `completion_tokens`, `total_tokens`).
* **Batch inference** is billed at 50% of standard Serverless rates on both input and output. See [Batch inference](/guides/batch-inference).
* Your **spend tier** influences Serverless capacity caps. Your monthly spend limit is a separate account control. Higher spend tiers unlock higher TPM upper bounds. See [Account quotas](/guides/quotas_usage/account-quotas) and [Serverless rate limits](/serverless/rate-limits).

## Request and response headers

Headers a Serverless caller will set or read.

### Request headers

| Header                                     | Notes                                                                                                                                                   |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Authorization: Bearer $FIREWORKS_API_KEY` | Required for all requests.                                                                                                                              |
| `x-session-affinity`                       | Optional sticky-routing key. Pin repeated requests to the same replica to maximize prompt-cache hit rate. See [Prompt caching](/guides/prompt-caching). |

### Response headers

Fireworks sets the following on Serverless inference responses:

| Header                                           | What it tells you                                                                     |
| ------------------------------------------------ | ------------------------------------------------------------------------------------- |
| `fireworks-prompt-tokens`                        | Input tokens for the request.                                                         |
| `fireworks-cached-prompt-tokens`                 | Cached portion of the input. See [Prompt caching](/guides/prompt-caching#monitoring). |
| `X-Ratelimit-Limit-Tokens-Prompt`                | Your current Total Prompt Tokens per Second Limit.                                    |
| `X-Ratelimit-Limit-Tokens-Cache-Adjusted-Prompt` | Your current Total Uncached Prompt Tokens per Second Limit.                           |
| `X-Ratelimit-Limit-Tokens-Generated`             | Your current Total Generated Tokens per Second Limit.                                 |

<Tip>
  Streaming responses don't carry per-request perf headers. To get the same metrics in the streaming response body, set the `perf_metrics_in_response` parameter on the request. See [Querying text models](/guides/querying-text-models#usage--performance-tracking).
</Tip>

## Prompt caching

Prompt caching is on by default for every Serverless model. Cached input tokens are billed at the discounted rate (default 50% of input). Caching is replica-local, so to maximize hit rate you should route repeated prompts to the same replica — pass a stable identifier in `x-session-affinity` (or in the OpenAI `user` field) for each user or session whose prompts share a prefix.

For the full guide, including how to structure prompts for cache hits and how to read cache metrics, see [Prompt caching](/guides/prompt-caching).

## Serverless model lifecycle

Serverless models are managed by the Fireworks team and may be updated or deprecated as new models are released. We provide **at least 2 weeks advance notice** before removing any model, with longer notice periods for popular models based on usage.

For production workloads requiring long-term model stability, we recommend [on-demand deployments](/guides/ondemand-deployments), which give you full control over model versions and updates.

## Serverless vs On-demand

| When Serverless fits                                           | When On-demand fits                                                                |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Pay per token, only for what you use                           | Pay per GPU-hour for dedicated capacity                                            |
| You're using popular base models that Fireworks already hosts  | You're running custom base models or trained LoRA models (LoRA requires On-demand) |
| You don't want to manage scaling, replicas, or hardware sizing | You have custom latency requirements and want control over hardware and replicas   |

For dedicated infrastructure, see [On-demand deployments](/guides/ondemand-deployments).

## Next steps

<CardGroup cols={2}>
  <Card title="Serverless quickstart" icon="rocket" href="/getting-started/quickstart">
    Make your first Serverless API call.
  </Card>

  <Card title="Serverless Modes" icon="bolt" href="/serverless/serverless-modes">
    Higher-reliability and higher-speed modes.
  </Card>

  <Card title="US-only Serverless" icon="flag-usa" href="/serverless/us-only-serverless">
    Dedicated US routers for inference residency.
  </Card>

  <Card title="Pricing" icon="circle-dollar" href="/serverless/pricing">
    Per-token rates for text, vision, embeddings, and Priority.
  </Card>

  <Card title="Reserved Throughput" icon="gauge-high" href="/serverless/reserved-throughput">
    SLA-backed throughput that adds to your adaptive rate limits.
  </Card>

  <Card title="Rate limits" icon="gauge" href="/serverless/rate-limits">
    Adaptive TPM bounds and how the limit ramps with usage.
  </Card>

  <Card title="Prompt caching" icon="database" href="/guides/prompt-caching">
    How caching works and how to maximize hit rate.
  </Card>

  <Card title="On-demand deployments" icon="server" href="/guides/ondemand-deployments">
    Dedicated GPUs for predictable throughput and custom models.
  </Card>
</CardGroup>
