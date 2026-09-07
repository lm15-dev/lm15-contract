---
meta:
  title: Token counting
  description: Count the fully rendered input tokens for a request before inference, to check context-window fit.
  keywords: token counting, input tokens, count tokens, context window, usage, Meta Model API
cms:
  alias: /model-api/docs/token-counting
  target: aidmc
---

# Token counting

Get an exact token count before you run inference. You stay inside the [context window](/docs/models) and size batches safely. Meta Model API renders the request and runs the selected model's tokenizer, so the count includes the context the model would receive.

## Count input tokens before you send {#count-input-tokens}

`POST /v1/responses/input_tokens` returns the number of tokens in the fully rendered input for the model call represented by your request. Send the supported fields from the body you would send to [`/v1/responses`](/docs/protocols/responses), at minimum `model` and `input`, then read `input_tokens` from the result. The server resolves `previous_response_id` history and applies the current request's instructions, tool definitions, media, and prompt scaffolding before tokenization.

```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses/input_tokens",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "input": "What is the capital of France?",
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses/input_tokens" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "What is the capital of France?"
}'
```


The response contains only the count:

```text
{
  "object": "response.input_tokens",
  "input_tokens": <integer>
}
```

**Validation:** The endpoint applies the same initial request and replay-structure validation as [`/v1/responses`](/docs/protocols/responses) for supported fields, including `function_call.arguments` JSON validity, `call_id` matching, tool definitions, and function-name constraints. Conversation resources are not supported; use `previous_response_id` for multi-turn history. If a check fails, the endpoint returns `HTTP 400` with the same error shape as a generation request. A successful count validates and tokenizes the initial rendered context; it does not predict context growth or validation after future hosted-tool results.

The endpoint tokenizes only. It does not generate output, execute hosted tools, create or store a response, or record generation usage. Use the result to check context-window fit, not to estimate billing. For the full endpoint reference, see [Count input tokens](/docs/api-reference/responses/count-input-tokens).

## Token counts are model-specific {#model-specific}

A count only applies to the model that produced it. Tokenizers differ per model, so the same text can map to different totals on different models. Always count against the model you will actually call, and recount when you switch models.

This is why you count through the API rather than a local tokenizer library: the `input_tokens` endpoint applies the target model's prompt template and tokenizer to the reconstructed request.

## Compare rendered context with response usage {#injected-tokens}

Every prompt includes Meta-injected steering context: a hidden system prompt, a default developer message, and tool scaffolding for built-in tools such as [web search](/docs/search-grounding). The count endpoint includes these tokens because they occupy the model's context.

Generated response usage is separate accounting data. Requests that execute hosted tools report `usage.input_tokens` cumulatively across model iterations. Each iteration contributes its reported input-token count after applying accounting adjustments, including injected-token discounts. Cumulative usage can therefore exceed both the preflight count and the final model context size.

Do not use `usage.input_tokens` as a final-context occupancy value. Use `POST /v1/responses/input_tokens` on the reconstructed request when you need a context-size measurement.

## Count multimodal input {#multimodal}

Images and files contribute to the input total. Their token contribution depends on the selected model and version, prompt template, media preprocessing, and image resolution. Fixed per-image or prompt-overhead estimates are not portable across deployments.

Measure representative payloads again after a model, tokenizer, prompt-template, or media-processing deployment. Use `input_tokens` instead of estimating from image count or dimensions. See [Image understanding](/docs/image-understanding) for supported formats and resizing behavior.

## Read token usage after a response {#usage}

Every non-streaming response reports accounting data in a `usage` object. Field names vary by endpoint:

- **Responses**: `{ input_tokens, output_tokens, total_tokens, input_tokens_details: { cached_tokens }, output_tokens_details: { reasoning_tokens } }`.
- **Chat Completions**: `{ prompt_tokens, completion_tokens, total_tokens, prompt_tokens_details: { cached_tokens }, completion_tokens_details: { reasoning_tokens } }`.

`reasoning_tokens` counts chain-of-thought tokens, a subset of the output total; `cached_tokens` counts prompt tokens served from the [prompt cache](/docs/prompt-caching). For a Responses request with hosted tools, `input_tokens` adds the reported input-token count from every model iteration after per-iteration accounting adjustments. When you stream with Chat Completions, request a final usage chunk with `stream_options: {"include_usage": true}`; on the Responses API, read `usage` from the final response object.

## Count tokens for Anthropic-format requests {#anthropic}

If you call the Anthropic-compatible [Messages API](/docs/api-reference/messages/create-message), count tokens with `POST /v1/messages/count_tokens`. It accepts the same Anthropic-shaped body as `/v1/messages` and returns `{ "input_tokens": <integer> }`. See [Count tokens](/docs/api-reference/messages/count-tokens) for the reference.

## Next steps

- Stay inside the window: check [Models](/docs/models) for the context limit, then compact history as conversations grow.
- Cut repeated-prefix spend by pairing your counts with [prompt caching](/docs/prompt-caching).
- Wire [Count input tokens](/docs/api-reference/responses/count-input-tokens) into preflight checks before large or variable requests.