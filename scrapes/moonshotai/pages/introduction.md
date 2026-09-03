> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Main Concepts

> Learn the core Kimi API concepts behind models, prompts, tokens, context windows, streaming, tool calling, and multimodal input.

## Text and Multimodal Models

`kimi-k3` is Kimi's flagship model, built for long-horizon coding and end-to-end knowledge work, with native visual understanding; `kimi-k2.6` supports text, image, and video input, as well as thinking and non-thinking modes, and is suitable for conversation, code generation, visual understanding, and agent tasks. The input to a model is commonly called a "prompt", and clear instructions plus representative examples are the most effective way to get stable outputs. Other models are also available — see the [Model List](/docs/models) for details.

## Language Model Inference Service

The language model inference service is an API service based on the pretrained models developed and trained by us (Moonshot AI). Today, the platform offers three interfaces — Chat Completions, Responses, and Messages (Anthropic-compatible) — for conversation, code generation, visual understanding, and agent tasks. Models do not directly access external resources such as the internet or databases by default, but you can extend them with official tools or custom tool calls when needed.

## Token

Text generation models process text in units called Tokens. A Token represents a common sequence of characters. For example, a single English character like "antidisestablishmentarianism" might be broken down into a combination of several Tokens, while a short and common phrase like "word" might be represented by a single Token. Generally speaking, for a typical English text, 1 Token is roughly equivalent to 3-4 English characters.

It is important to note that the total length of Input and Output cannot exceed the selected model's maximum context length. For example, `kimi-k3` supports a context window of up to 1M tokens. For other models' context lengths, see the [Model List](/docs/models).

## Rate Limits

How do these rate limits work?

Rate limits are measured in four ways: concurrency, RPM (requests per minute), TPM (tokens per minute), and TPD (tokens per day). The rate limit can be reached in any of these categories, depending on which one is hit first. For example, you might send 20 requests to ChatCompletions, each with only 100 Tokens, and you would hit the limit (if your RPM limit is 20), even if you haven't reached 200k Tokens in those 20 requests (assuming your TPM limit is 200k).

For the gateway, for convenience, we calculate rate limits based on the max\_completion\_tokens parameter in the request. This means that if your request includes the max\_completion\_tokens parameter, we will use this parameter to calculate the rate limit. If your request does not include the max\_completion\_tokens parameter, we will use the default max\_completion\_tokens parameter to calculate the rate limit. After you make a request, we will determine whether you have reached the rate limit based on the number of Tokens in your request plus the number of max\_completion\_tokens in your parameter, regardless of the actual number of Tokens generated.

In the billing process, we calculate the cost based on the number of Tokens in your request plus the actual number of Tokens generated.

### Other Important Notes:

* Rate limits are enforced at the user level, not the key level.
* Currently, we share rate limits across all models.

## Model List

For all available models and their capabilities, see the [Model List](/docs/models) page.

# Usage Guide

## Getting an API Key

You need an API key to use our service. You can create an [API key](https://platform.kimi.ai/console/api-keys) in our [Console](https://platform.kimi.ai/console).

## Sending Requests

You can use our Chat Completions API to send requests. You need to provide an API key and a model name. You can choose to use the default max\_completion\_tokens parameter or customize the max\_completion\_tokens parameter. You can refer to the [Chat API documentation](/docs/api/chat) for the calling method.

## Handling Responses

Generally, we set a 2 hours timeout. If a single request exceeds this time, we will return a 504 error. If your request exceeds the rate limit, we will return a 429 error. If your request is successful, we will return a response in JSON format.

If you need to quickly process some tasks, you can use the non-streaming mode of our Chat Completions API. In this mode, we will return all the generated text in one request. If you need more control, you can use the streaming mode. In this mode, we will return an [SSE](https://kimi.moonshot.cn/share/cr7boh3dqn37a5q9tds0) stream, where you can obtain the generated text. This can provide a better user experience, and you can also interrupt the request at any time without wasting resources.
