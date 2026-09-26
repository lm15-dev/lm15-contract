> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Overview

> Call 100+ open-source models with per-token pricing and no provisioning latency.

Serverless models are the fastest way to run inference on Together AI. Call any [supported model](/docs/serverless/models) instantly, with no minimum cost or provisioning latency. You pay only for the tokens, megapixels, or seconds of audio/video/speech you process.

Serverless uses the same [inference APIs](/docs/inference/overview#shared-inference-api) as [dedicated model inference](/docs/dedicated-endpoints/overview), so you can prototype on serverless and move to reserved hardware later without changing your application code.

## Get started

<CardGroup cols={3}>
  <Card title="Quickstart" icon="rocket" href="/docs/quickstart">
    Make your first API request in a few minutes.
  </Card>

  <Card title="Available models" icon="list" href="/docs/serverless/models">
    Browse the catalog of serverless models and their rates.
  </Card>

  <Card title="Recommended models" icon="sparkles" href="/docs/inference/recommended-models">
    See our picks by use case if you're not sure where to start.
  </Card>

  <Card title="Inference APIs" icon="code" href="/docs/inference/overview">
    Call chat, image, audio, embedding, and more through one API.
  </Card>

  <Card title="Batch inference" icon="stack-2" href="/docs/inference/batch/overview">
    Run asynchronous workloads at up to 50% lower cost.
  </Card>
</CardGroup>

## Rate limits

Serverless models are [rate-limited](/docs/serverless/rate-limits), so they work best when you're prototyping or evaluating a model, or when your production traffic is variable, bursty, or low enough that per-token pricing is cost-effective. If your traffic is steady, you need higher rate limits, or you want reserved hardware, you can request [provisioned throughput](/docs/inference/provisioned-throughput) or use a [dedicated endpoint](/docs/dedicated-endpoints/overview).

## Region selection

Together AI routes serverless requests across its own infrastructure, and the serving region is not selectable. If you need requests to run in a specific region (for latency, residency, or compliance reasons), use a [dedicated endpoint](/docs/dedicated-endpoints/overview) and pin its hardware to your target region.

## Pricing

Serverless models bill based on usage, with no minimums and no provisioning cost. You pay per unit of work, with units determined by model type:

* **Chat, language, embedding, and rerank:** Per input and output token.
* **Image generation:** Per megapixel of output.
* **Video generation:** Per second of output.
* **Speech-to-text and text-to-speech:** Per second of audio.

Per-model rates are in the [catalog tables](/docs/serverless/models), and on [together.ai/pricing](https://together.ai/pricing).

If you don't need real-time responses, some models are discounted up to 50% when run with [batch workloads](/docs/inference/batch/overview).

### Cached input discounts

Select serverless chat models bill cached input tokens at a steep discount. Caching is:

* **Automatic:** There is no header, parameter, or account toggle to enable it. Send the same prompt prefix again and any portion that's still warm in the shared cache is billed at the cached rate.
* **Prefix-based:** Only the longest matching prefix of your input counts as cached. Tokens after the first difference are billed at the standard input rate.
* **Best-effort and short-lived:** The serverless cache is shared across the fleet and entries are evicted as traffic shifts, so cache hits aren't guaranteed and there's no configurable retention window. For predictable cache behavior, use a [dedicated endpoint](/docs/dedicated-endpoints/requests#prompt-caching), where prompt caching is enabled by default and scoped to your own replicas.
* **Limited to supported models:** Only models with a value in the **Cached input pricing** column on [Chat models](/docs/serverless/models#chat-models) support cached input billing. Models without a cached price bill all input tokens at the standard rate.
