> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Serverless Rate Limits

> Adaptive rate limits grow and shrink with your usage

<a id="rate-limits-and-quotas" />

When using Serverless, you may experience `429 Too Many Requests` or `503 Service Overloaded`. To avoid 429s, you need to stay below our adaptive rate limits. To reduce the likelihood of 503s, you can upgrade to [Priority tier](/serverless/serverless-modes).

## What are your rate limits?

There are three metrics we use to rate limit accounts:

* **Total Prompt TPM** — input tokens per minute (cached + uncached).
* **Uncached Prompt TPM** — uncached input tokens per minute.
* **Generated TPM** — output tokens per minute.

**Enforcement uses TPM**, not TPS.

Adaptive rate limit ceilings depend on the model's total parameter count. Smaller models get higher ceilings:

<a id="model-size-tiers" />

| Tier       | Total parameters | Total Prompt TPM | Uncached Prompt TPM | Generated TPM |
| ---------- | ---------------- | ---------------- | ------------------- | ------------- |
| **Small**  | \< 400B          | 64.8M            | 16.2M               | 648k          |
| **Medium** | 400B – \< 1.6T   | 43.2M            | 10.8M               | 432k          |
| **Large**  | ≥ 1.6T           | 21.6M            | 5.4M                | 216k          |

Fast, Priority, and US-only variants of a model share the same tier and ceilings as the base model. Models without a known parameter count use **Large** ceilings.

Based on your usage, your adaptive limits will grow and shrink within these ceilings. If your traffic ramps up too quickly, you will get 429s.

<img src="https://mintcdn.com/fireworksai/YH2uwOIOrmQeCBpB/images/serverless/ratelimit-example.png?fit=max&auto=format&n=YH2uwOIOrmQeCBpB&q=85&s=c50f8e058fb94ba05c8d77e283a917c0" alt="kimi-k2p6 usage and rate limits" width="2124" height="1474" data-path="images/serverless/ratelimit-example.png" />

Your current effective rate limits (described in tokens per second) are in the response headers `X-Ratelimit-Limit-Tokens-Prompt`, `X-Ratelimit-Limit-Tokens-Cache-Adjusted-Prompt`, and `X-Ratelimit-Limit-Tokens-Generated`.

Adaptive rate limits have an upper and lower bound. A higher account [Spending Tier](/guides/quotas_usage/account-quotas#spending-tiers) correlates with higher upper bound rate limits; **enterprise accounts** get higher upper bounds automatically.

## FAQ

<AccordionGroup>
  <Accordion title="Am I guaranteed successful responses up to my rate limit?">
    **No.** Staying within your rate limits does not guarantee that every request succeeds. When a deployment is busy, your traffic can still be **load shed**, and those responses are **`503 Service Overloaded`**. To **decrease the chance** of being load shed, you can use [Priority tier](/serverless/serverless-modes), which is prioritized during high load.
  </Accordion>

  <Accordion title="How are rate limits scoped?">
    Rate limits are scoped **per account** and **per model**. **Fast** and **regular** model variants have **separate** limits. **Priority tier** and **regular** requests share the **same** rate limits for a given model.
  </Accordion>

  <Accordion title="How is my model's ceiling tier determined?">
    Ceiling tiers are based on the model's **total parameter count**: **Small** (\< 400B), **Medium** (400B – \< 1.6T), or **Large** (≥ 1.6T). See [Model size tiers](#model-size-tiers) for the ceiling values.
  </Accordion>

  <Accordion title="What should I do first when I see 429s?">
    First, try **exponential backoff** when retrying.
  </Accordion>

  <Accordion title="How do I get higher limits sooner?">
    Reach out to [inquiries@fireworks.ai](mailto:inquiries@fireworks.ai) for a custom solution if either of these applies:

    * **You need higher than the defaults from day one.** Your launch traffic exceeds the starting limit and you can't wait for the adaptive ramp.
    * **You're ramping past the highest upper bound.** You are already at the highest account Spending Tier and the adaptive rate limits are not growing.
  </Accordion>
</AccordionGroup>
