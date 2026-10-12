## Muse Wonder

Muse Wonder is Meta's most capable model, built for complex software engineering and long-horizon agentic work. It makes and verifies changes across many files in real repositories, and it plans, delegates to sub-agents, calls tools in parallel, and recovers from errors across many steps, following detailed instructions closely. Take on hard coding tasks, build personal and professional agents, and drive a desktop with [computer use](https://dev.meta.ai/docs/computer-use). Muse Wonder also handles [chat completion](https://dev.meta.ai/docs/protocols/chat-completions), [image understanding](https://dev.meta.ai/docs/image-understanding), [video and audio understanding](https://dev.meta.ai/docs/video-understanding), [tool calling](https://dev.meta.ai/docs/tool-calling), [structured output](https://dev.meta.ai/docs/structured-output), and [search grounding](https://dev.meta.ai/docs/search-grounding).

Muse Wonder takes text, image, video, audio, and PDF input, returns text, has a 1,048,576-token context window, and supports [reasoning effort](https://dev.meta.ai/docs/reasoning) levels from `"minimal"` to `"max"`.

> **NOTE: Preview**
>
> Muse Wonder is in preview. For more about the model, see the [Muse Wonder model page](https://dev.meta.ai/models/muse-wonder) and the [Muse Wonder model card](https://research.meta.ai/static/muse-wonder-model-card).

### Muse Wonder availability

Muse Wonder comes in two variants. Muse Wonder is on Model API and in [Muse Code](https://dev.meta.ai/docs/muse-code). Muse Wonder Full, the higher-capability variant, is available only in Muse Code with a subscription, so setting reasoning effort to `"max"` on Muse Wonder doesn't select it.

| Variant                         | Model API (pay-as-you-go)      | Muse Code                                                                                                                                                       |
| :------------------------------ | :----------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Muse Wonder (`muse-wonder-1.0`) | Available (Standard mode only) | Pay-as-you-go and [every plan](https://dev.meta.ai/docs/muse-code/subscriptions#about)                                                                          |
| Muse Wonder Full                | Not available                  | [Power Usage](https://dev.meta.ai/docs/muse-code/subscriptions#power-usage) and [Maximum Usage](https://dev.meta.ai/docs/muse-code/subscriptions#maximum-usage) |

With a subscription, Muse Wonder is available on every plan and Muse Wonder Full on the Power Usage and Maximum Usage plans, each in [Standard mode](https://dev.meta.ai/docs/pricing-rate-limits#standard-mode) and [Contributor mode](https://dev.meta.ai/docs/pricing-rate-limits#contributor-mode).

In Standard mode, your content — the prompts, code, files, and context you send, plus the model responses you get back — is not used to train Meta models. Muse Code subscribers can also use Contributor mode, which is on by default: it gives you more usage in exchange for letting Meta use your content to train future Meta models, and you can turn it off at any time in your settings. For Muse Wonder, Contributor mode isn't available on pay-as-you-go. See [Pricing and rate limits](https://dev.meta.ai/docs/pricing-rate-limits) for rates.

