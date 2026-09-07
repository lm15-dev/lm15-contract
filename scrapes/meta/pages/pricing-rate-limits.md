---
meta:
  title: Pricing and rate limits
  description: Standard and contributor pricing tiers, per-token pricing, image pricing, Muse Voice Transcribe pricing, and rate limits for Meta Model API.
  keywords: pricing, standard tier, contributor tier, discounted pricing, training, pay-as-you-go, per-token pricing, cost, rate limits, requests per minute, tokens per minute, throttling, background, Muse Voice Transcribe, speech to text, transcription
cms:
  alias: /model-api/docs/pricing-rate-limits
  target: aidmc
---

# Pricing and rate limits

## Pricing {#pricing}

You pay only for what you use. Meta Model API bills text models per token, image generation per image, and Muse Voice Transcribe per minute of audio processed, with no minimums or upfront commitment.

### Standard tier {#standard-tier}

Models: `muse-spark-1.3`, `muse-spark-1.2`, `muse-spark-1.1`.

Standard pricing; your prompts and completions are not used to train Meta models. These versions share the same standard pricing:

| Usage | Price per 1M tokens |
| :---- | :---- |
| Cached input | $0.15 |
| Input | $1.25 |
| Output | $4.25 |

### Contributor tier {#contributor-tier}

Models: `muse-spark-1.3-contributor`, `muse-spark-1.2-contributor`.

Heavily discounted token pricing in exchange for permission to use your prompts and completions to train future Meta models. It lowers the barrier to entry for prototyping, testing integrations, and scaling experiments where training on your data is acceptable.

| Usage | Price per 1M tokens |
| :---- | :---- |
| Cached input | $0.002 |
| Input | $0.10 |
| Output | $0.20 |

### Muse Voice Transcribe {#muse-voice-transcribe-pricing}

[Muse Voice Transcribe](/docs/speech-to-text) is billed by minutes of audio processed.

| Usage | Price |
| :---- | :---- |
| Audio processed | $0.18 per hour |

Streaming and non-streaming transcription are priced the same. ZDR is priced at parity with Standard, and platform free-tier credits apply. The training-eligible discounted tier is not available for Muse Voice Transcribe at launch.

### Shared pricing notes

Cached input costs less. When part of your prompt matches a [cached prefix](/docs/prompt-caching), you pay the cached-input rate for those tokens. Check `cached_tokens` in the response to see how many were served from cache.

**Web search grounding** costs **$2.50 per 1,000 search queries**, in addition to the request's token cost. This applies to the [`web_search` tool](/docs/search-grounding) on text models such as [Muse Spark](/docs/models#muse-spark).

> [!NOTE] Muse Image search is included
> [Muse Image](/docs/models#muse-image)'s built-in web and image search is part of its per-image price and isn't charged separately. See [Image generation](#image-generation).

There is **no long-context premium**: you pay the same rate whether your context window is mostly empty or almost full.

### Image generation (Muse Image) {#image-generation}

[Muse Image](/docs/models#muse-image) is billed at a flat **$0.01 per generated image**. The price is the same regardless of prompt length, `reasoning_strength`, or the tools the model uses during generation, including its built-in web and image search, which isn't charged separately. A request that returns `n` images is billed for `n` images. You're billed only for images the model successfully generates and returns: images that fail to generate, or that are removed by safety filtering before they're returned, aren't counted. Image responses still include a `usage` object with token counts for reference, but image generation tokens are not included in token-based pricing for other models. See the [Image generation](/docs/image-generation#images-response) guide for the response shape.

## Rate limits {#rate-limits}

Rate limits control usage for your team and are set by pricing tier or model family.

For token-based models, the Standard tier covers `muse-spark-1.3`, `muse-spark-1.2`, and `muse-spark-1.1`; the Contributor tier covers `muse-spark-1.3-contributor` and `muse-spark-1.2-contributor`.

| Tier | Requests per minute (RPM) | Tokens per minute (TPM) |
| :---- | :---- | :---- |
| Standard | 3,000 | 4,000,000 |
| Contributor | 100 | 3,000,000 |

[Muse Image](/docs/models#muse-image) (`muse-image-1.0`) has a separate limit of **150 requests per minute**. Because it's [priced per image](#image-generation) rather than per token, it has no tokens-per-minute limit.

Limits apply **per team, not per API key**. If you use multiple keys in one team, all requests, tokens, images, and audio minutes count toward the relevant shared quota.

Token usage counts only **your** input and output tokens. Meta injects a small amount of steering context into every prompt (a system prompt and related scaffolding); those injected tokens are not billed and are excluded from the token counts reported in your `usage` and by the [token-counting endpoints](/docs/token-counting#injected-tokens).

> [!NOTE] Muse Voice Transcribe is metered differently
> RPM and TPM do not apply to [Muse Voice Transcribe](/docs/speech-to-text), which is metered by audio minutes and limited by active streams and streams started over time. See [Rate limits for Muse Voice Transcribe](#muse-voice-transcribe-rate-limits).

## Retry on 429 responses {#rate-limit-behavior}

If you exceed a request, token, image, audio, or stream-start limit, the API returns a rate-limit response. Requests succeed again once usage drops below the limit.

**Retry strategy:** Use exponential backoff with jitter. Start with a short delay such as 500 ms, double it after each consecutive rate-limit response, and add random jitter to avoid thundering-herd effects across concurrent clients.

## Read rate-limit headers {#rate-limit-headers}

Every successful token-based response includes headers that report your current limit and remaining quota:

| Header | Description |
| :---- | :---- |
| `x-ratelimit-limit-tokens` | Total token budget for the current window. |
| `x-ratelimit-remaining-tokens` | Tokens remaining before you hit the limit. |
| `x-ratelimit-limit-requests` | Total request budget for the current window. |
| `x-ratelimit-remaining-requests` | Requests remaining before you hit the limit. |

Read these headers and slow down before you hit a rate limit instead of reacting after one.

## Submit background responses within limits {#background-rate-limit}

Creating [background responses](/docs/protocols/responses#using-with-other-features) (`background: true`) counts against a separate per-team submission limit in addition to the RPM and TPM limits above. The default is **600 background submissions per minute, per team**.

If you exceed that cap, new background submissions return `HTTP 429 Too Many Requests` with a `Retry-After` header. Responses already running continue unaffected. Apply the same exponential-backoff-with-jitter strategy described above.

The cap applies only to starting new background responses. Standard RPM and TPM limits still apply to every request.

## Rate limits for Muse Voice Transcribe {#muse-voice-transcribe-rate-limits}

[Muse Voice Transcribe](/docs/speech-to-text) is limited by stream usage rather than tokens. Two dimensions are enforced at once:

| | Limit |
| :---- | :---- |
| Concurrent streams | 8 |
| Streams per hour | 1,000 |

**Concurrent streams** caps how many streaming sessions you hold open at the same moment. **Streams per hour** limits how many transcription sessions you start.

Both realtime and file transcription use the same budget. A rejected realtime stream closes with `1013`. A rejected file-transcription request returns `HTTP 429 Too Many Requests`.

> [!IMPORTANT]
> Confirm these rate-limit numbers against the launch configuration before publishing. They are present in the current mdoc draft but are not specified in Part A of the positioning SoT.

## Next steps

- [Muse Voice Transcribe](/docs/speech-to-text): stream audio or transcribe a file
- [Authentication](/docs/authentication): create and manage API keys
- [Get started](/docs/quickstart#first-call): make your first API call
- [Chat completion](/docs/protocols/chat-completions): start generating text with the core conversational endpoint