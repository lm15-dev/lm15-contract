> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Text Models

> Query, track and manage inference for text models

<Info>
  New to Fireworks? Start with the [Serverless Quickstart](/getting-started/quickstart) for a step-by-step guide to making your first API call.
</Info>

Fireworks provides fast, cost-effective access to leading open-source text models through OpenAI-compatible APIs. Query models via serverless inference or dedicated deployments using the chat completions API (recommended), completions API, or responses API.

[Browse 100+ available models →](https://fireworks.ai/models)

## Chat Completions API

<Tabs>
  <Tab title="Python (Fireworks SDK)">
    ```python theme={null}
    from fireworks import Fireworks

    client = Fireworks()

    response = client.chat.completions.create(
      model="accounts/fireworks/models/deepseek-v3p1",
      messages=[{"role": "user", "content": "Explain quantum computing in simple terms"}]
    )

    print(response.choices[0].message.content)
    ```
  </Tab>

  <Tab title="Python (OpenAI SDK)">
    ```python theme={null}
    import os
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("FIREWORKS_API_KEY"),
        base_url="https://api.fireworks.ai/inference/v1"
    )

    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{
            "role": "user",
            "content": "Explain quantum computing in simple terms"
        }]
    )

    print(response.choices[0].message.content)
    ```
  </Tab>

  <Tab title="JavaScript">
    ```javascript theme={null}
    import OpenAI from "openai";

    const client = new OpenAI({
      apiKey: process.env.FIREWORKS_API_KEY,
      baseURL: "https://api.fireworks.ai/inference/v1",
    });

    const response = await client.chat.completions.create({
      model: "accounts/fireworks/models/deepseek-v3p1",
      messages: [
        {
          role: "user",
          content: "Explain quantum computing in simple terms",
        },
      ],
    });

    console.log(response.choices[0].message.content);
    ```
  </Tab>

  <Tab title="curl">
    ```bash theme={null}
    curl https://api.fireworks.ai/inference/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $FIREWORKS_API_KEY" \
      -d '{
        "model": "accounts/fireworks/models/deepseek-v3p1",
        "messages": [
          {
            "role": "user",
            "content": "Explain quantum computing in simple terms"
          }
        ]
      }'
    ```
  </Tab>
</Tabs>

<Tip>
  Most models automatically format your messages with the correct template. To verify the exact prompt used, enable the [`echo`](/guides/querying-text-models) parameter.
</Tip>

For **Priority tier** (`service_tier: "priority"`) and **Fast**, see [Serverless Modes](/serverless/serverless-modes).

## Alternative query methods

Fireworks also supports [Completions API](/guides/completions-api) and [Responses API](/guides/response-api).

## Querying dedicated deployments

For consistent performance, guaranteed capacity, or higher throughput, you can query [on-demand deployments](/guides/ondemand-deployments) instead of serverless models. Deployments use the same APIs with a deployment-specific identifier:

```
accounts/<ACCOUNT_ID>/deployments/<DEPLOYMENT_ID>
```

For example:

```python theme={null}
response = client.chat.completions.create(
    model="accounts/<ACCOUNT_ID>/deployments/<DEPLOYMENT_ID>",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Common patterns

### Multi-turn conversations

Maintain conversation history by including all previous messages:

```python theme={null}
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What's its population?"}
]

response = client.chat.completions.create(
    model="accounts/fireworks/models/deepseek-v3p1",
    messages=messages
)

print(response.choices[0].message.content)
```

The model uses the full conversation history to provide contextually relevant responses.

### System prompts

Override the default system prompt by setting the first message with `role: "system"`:

```python theme={null}
messages = [
    {"role": "system", "content": "You are a helpful Python expert who provides concise code examples."},
    {"role": "user", "content": "How do I read a CSV file?"}
]

response = client.chat.completions.create(
    model="accounts/fireworks/models/deepseek-v3p1",
    messages=messages
)
```

To completely omit the system prompt, set the first message's `content` to an empty string.

### Streaming responses

Stream tokens as they're generated for real time, interactive UX. Covered in detail in the [Serverless Quickstart](/getting-started/quickstart#streaming-responses).

```python theme={null}
stream = client.chat.completions.create(
    model="accounts/fireworks/models/deepseek-v3p1",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Aborting streams:** Close the connection to stop generation and avoid billing for ungenerated tokens:

```python theme={null}
for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
    if some_condition:
        stream.close()
        break
```

### Async requests

Use async clients to make multiple concurrent requests for better throughput:

<Tabs>
  <Tab title="Python (Fireworks SDK)">
    ```python theme={null}
    from fireworks import AsyncFireworks

    client = AsyncFireworks()

    async def main():
      response = await client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}]
      )
      print(response.choices[0].message.content)

    asyncio.run(main())
    ```
  </Tab>

  <Tab title="Python (OpenAI SDK)">
    ```python theme={null}
    import asyncio
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=os.environ.get("FIREWORKS_API_KEY"),
        base_url="https://api.fireworks.ai/inference/v1"
    )

    async def main():
        response = await client.chat.completions.create(
            model="accounts/fireworks/models/deepseek-v3p1",
            messages=[{"role": "user", "content": "Hello"}]
        )
        print(response.choices[0].message.content)

    asyncio.run(main())
    ```
  </Tab>

  <Tab title="JavaScript">
    ```javascript theme={null}
    import OpenAI from "openai";

    const client = new OpenAI({
      apiKey: process.env.FIREWORKS_API_KEY,
      baseURL: "https://api.fireworks.ai/inference/v1",
    });

    async function main() {
      const response = await client.chat.completions.create({
        model: "accounts/fireworks/models/deepseek-v3p1",
        messages: [{ role: "user", content: "Hello" }],
      });
      console.log(response.choices[0].message.content);
    }

    main();
    ```
  </Tab>
</Tabs>

### Usage & performance tracking

Every response includes token usage information and performance metrics for debugging and observability. For aggregate metrics over time, see the [usage dashboard](https://app.fireworks.ai/account/usage).

<Note>
  **The analytics and usage dashboard measures server-acknowledged requests, not every client-observed outcome.**

  The dashboard counts requests that successfully reached the Fireworks API. It does not capture connection timeouts before the request lands on the server, client-side retries before a successful attempt, or failures on the network path between your application and the API.

  If your application reports failures but the dashboard looks healthy, check client timeout configuration and network connectivity. For dedicated deployments, [Prometheus-style metrics](/deployments/exporting-metrics) reflect server-side behavior for that deployment.
</Note>

**Token usage** (prompt, completion, total tokens) is included in the response body for all requests.

**Performance metrics** (latency, time-to-first-token, etc.) are included in response headers for non-streaming requests. For streaming requests, use the [`perf_metrics_in_response`](/api-reference/post-chatcompletions) parameter to include all metrics in the response body.

<Tabs>
  <Tab title="Non-streaming">
    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}]
    )

    # Token usage (always included)
    print(response.usage.prompt_tokens)      # Tokens in your prompt
    print(response.usage.completion_tokens)  # Tokens generated
    print(response.usage.total_tokens)       # Total tokens billed

    # Performance metrics are in response headers:
    # fireworks-prompt-tokens, fireworks-server-time-to-first-token, etc.
    ```
  </Tab>

  <Tab title="Streaming (usage only)">
    ```python theme={null}
    stream = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
        
        # Usage is included in the final chunk
        if chunk.usage:
            print(f"\n\nTokens used: {chunk.usage.total_tokens}")
            print(f"Prompt: {chunk.usage.prompt_tokens}, Completion: {chunk.usage.completion_tokens}")
    ```
  </Tab>

  <Tab title="Streaming (with performance metrics)">
    ```python theme={null}
    stream = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello, world!"}],
        stream=True,
        extra_body={"perf_metrics_in_response": True}
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
        
        # Both usage and performance metrics are in the final chunk
        if chunk.choices[0].finish_reason:
            if chunk.usage:
                print(f"\n\nTokens: {chunk.usage.total_tokens}")
            if hasattr(chunk, 'perf_metrics'):
                print(f"Performance: {chunk.perf_metrics}")
    ```
  </Tab>
</Tabs>

<Note>
  Usage information is automatically included in the final chunk for streaming responses (the chunk with `finish_reason` set). This is a Fireworks extension - OpenAI SDK doesn't return usage for streaming by default.
</Note>

For all available metrics and details, see the [API reference documentation](/api-reference/post-chatcompletions).

<Tip>
  If you encounter errors during inference, see [Inference Error Codes](/guides/inference-error-codes) for common issues and resolutions.
</Tip>

## Advanced capabilities

Extend text models with additional features for structured outputs, tool integration, and performance optimization:

<CardGroup cols={3}>
  <Card title="Tool calling" href="/guides/function-calling" icon="function">
    Connect models to external tools and APIs with type-safe parameters
  </Card>

  <Card title="Structured outputs" href="/structured-responses/structured-response-formatting" icon="brackets-curly">
    Enforce JSON schemas for reliable data extraction
  </Card>

  <Card title="Responses API" href="/guides/response-api" icon="brain">
    Multi-step reasoning for complex problem-solving
  </Card>

  <Card title="Predicted outputs" href="/guides/predicted-outputs" icon="bolt">
    Speed up edits by predicting unchanged sections
  </Card>

  <Card title="Prompt caching" href="/guides/prompt-caching" icon="database">
    Cache common prompts to reduce latency and cost
  </Card>

  <Card title="Batch inference" href="/guides/batch-inference" icon="list-check">
    Process large volumes of requests asynchronously
  </Card>
</CardGroup>

## Configuration & debugging

<AccordionGroup>
  <Accordion title="Sampling parameters">
    Control how the model generates text. Fireworks automatically uses recommended sampling parameters from each model's HuggingFace `generation_config.json` when you don't specify them explicitly, ensuring optimal performance out-of-the-box.

    We pull `temperature`, `top_k`, `top_p`, `min_p`, and `typical_p` from the model's configuration when not explicitly provided.

    ### Temperature

    Adjust randomness (0 = deterministic, higher = more creative):

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Write a poem"}],
        temperature=0.7  # Override model default
    )
    ```

    ### Max tokens

    Control the maximum number of tokens in the generated completion:

    ```python theme={null}
    max_tokens=100  # Generate at most 100 tokens
    ```

    **Important notes:**

    * Default value is 2048 tokens if not specified
    * Most models support up to their full context window (e.g., 128K for DeepSeek R1)
    * When the limit is reached, you'll see `"finish_reason": "length"` in the response

    <Tip>
      Set `max_tokens` appropriately for your use case to avoid truncated responses. Check the model's context window in the [Model Library](https://fireworks.ai/models).
    </Tip>

    ### Top-p (nucleus sampling)

    Consider only the most probable tokens summing to `top_p` probability mass:

    ```python theme={null}
    top_p=0.9  # Consider top 90% probability mass
    ```

    ### Top-k

    Consider only the k most probable tokens:

    ```python theme={null}
    top_k=50  # Consider top 50 tokens
    ```

    ### Min-p

    Exclude tokens below a probability threshold:

    ```python theme={null}
    min_p=0.05  # Exclude tokens with <5% probability
    ```

    ### Typical-p

    Use typical sampling to select tokens with probability close to the entropy of the distribution:

    ```python theme={null}
    typical_p=0.95  # Consider tokens with typical probability
    ```

    ### Repetition penalties

    Reduce repetitive text with `frequency_penalty`, `presence_penalty`, or `repetition_penalty`:

    ```python theme={null}
    frequency_penalty=0.5,   # Penalize frequent tokens (OpenAI compatible)
    presence_penalty=0.5,    # Penalize any repeated token (OpenAI compatible)
    repetition_penalty=1.1   # Exponential penalty from prompt + output
    ```

    ### Sampling options header

    The `fireworks-sampling-options` header contains the actual default sampling parameters used for the model, including values from the model's HuggingFace `generation_config.json`:

    <Tabs>
      <Tab title="Python">
        ```python theme={null}
        response = client.chat.completions.with_raw_response.create(
          model="accounts/fireworks/models/deepseek-v3p1",
          messages=[{"role": "user", "content": "Hello"}]
        )

        # Access headers from the raw response
        sampling_options = response.headers.get('fireworks-sampling-options')
        print(sampling_options)  # e.g., '{"temperature": 0.7, "top_p": 0.9}'

        completion = response.parse()  # get the parsed response object
        print(completion.choices[0].message.content)
        ```
      </Tab>

      <Tab title="JavaScript">
        ```javascript theme={null}
        import OpenAI from "openai";

        const client = new OpenAI({
          apiKey: process.env.FIREWORKS_API_KEY,
          baseURL: "https://api.fireworks.ai/inference/v1",
        });

        const response = await client.chat.completions.with_raw_response.create({
          model: "accounts/fireworks/models/deepseek-v3p1",
          messages: [{ role: "user", content: "Hello" }],
        });

        // Access headers from the raw response
        const samplingOptions = response.headers.get('fireworks-sampling-options');
        console.log(samplingOptions); // e.g., '{"temperature": 0.7, "top_p": 0.9}'

        const completion = response.parse(); // get the parsed response object
        console.log(completion.choices[0].message.content);
        ```
      </Tab>
    </Tabs>

    See the [API reference](/api-reference/post-chatcompletions) for detailed parameter descriptions.
  </Accordion>

  <Accordion title="Multiple generations">
    Generate multiple completions in one request:

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Tell me a joke"}],
        n=3  # Generate 3 different jokes
    )

    for choice in response.choices:
        print(choice.message.content)
    ```
  </Accordion>

  <Accordion title="Token probabilities (logprobs)">
    Inspect token probabilities for debugging or analysis:

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}],
        logprobs=True,
        top_logprobs=5  # Show top 5 alternatives per token
    )

    for content in response.choices[0].logprobs.content:
        print(f"Token: {content.token}, Logprob: {content.logprob}")
    ```
  </Accordion>

  <Accordion title="Prompt inspection (echo & raw_output)">
    Verify how your prompt was formatted:

    **Echo:** Return the prompt along with the generation:

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}],
        echo=True
    )
    ```

    **Token IDs:** Return prompt and completion token IDs:

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}],
        return_token_ids=True
    )

    print(response.prompt_token_ids)      # Prompt token IDs
    print(response.choices[0].token_ids)  # Completion token IDs
    ```

    **Raw output:** See prompt fragments and raw completion:

    <Warning>
      Experimental API - may change without notice.
    </Warning>

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}],
        raw_output=True
    )

    print(response.choices[0].raw_output.completion)  # Raw completion
    ```
  </Accordion>

  <Accordion title="Ignore EOS token">
    Force generation to continue past the end-of-sequence token (useful for benchmarking):

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}],
        ignore_eos=True,
        max_tokens=100  # Will always generate exactly 100 tokens
    )
    ```

    <Note>
      Output quality may degrade when ignoring EOS. This API is experimental and should not be relied upon for production use cases.
    </Note>
  </Accordion>

  <Accordion title="Logit bias">
    Modify token probabilities to encourage or discourage specific tokens:

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}],
        logit_bias={
            123: 10.0,   # Strongly encourage token ID 123
            456: -50.0   # Strongly discourage token ID 456
        }
    )
    ```
  </Accordion>

  <Accordion title="Mirostat sampling">
    Control perplexity dynamically using the [Mirostat algorithm](https://arxiv.org/abs/2007.14966):

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/deepseek-v3p1",
        messages=[{"role": "user", "content": "Hello"}],
        mirostat_target=5.0,  # Target perplexity
        mirostat_lr=0.1       # Learning rate for adjustments
    )
    ```
  </Accordion>
</AccordionGroup>

## Understanding tokens

Language models process text in chunks called **tokens**. In English, a token can be as short as one character or as long as one word. Different model families use different **tokenizers**, so the same text may translate to different token counts depending on the model.

**Why tokens matter:**

* Models have maximum context lengths measured in tokens
* Pricing is based on token usage (prompt + completion)
* Token count affects response time

For Llama models, use [this tokenizer tool](https://belladoreai.github.io/llama-tokenizer-js/example-demo/build/) to estimate token counts. Actual usage is returned in the `usage` field of every API response.

## OpenAI SDK migration

Fireworks provides an OpenAI-compatible API, making migration from OpenAI straightforward. For detailed information on setup, usage examples, and API compatibility notes, see the [OpenAI compatibility guide](/tools-sdks/openai-compatibility).

## Next steps

<CardGroup cols={3}>
  <Card title="Vision models" href="/guides/querying-vision-language-models" icon="image">
    Process images alongside text
  </Card>

  <Card title="Embeddings" href="/guides/querying-embeddings-models" icon="database">
    Generate vector representations for search
  </Card>

  <Card title="On-demand deployments" href="/guides/ondemand-deployments" icon="server">
    Deploy models on dedicated GPUs
  </Card>

  <Card title="Training" href="/fine-tuning/finetuning-intro" icon="sliders">
    Customize models for your use case
  </Card>

  <Card title="Error codes" href="/guides/inference-error-codes" icon="circle-exclamation">
    Troubleshoot common inference errors
  </Card>

  <Card title="API Reference" href="/api-reference/post-chatcompletions" icon="code">
    Complete API documentation
  </Card>
</CardGroup>
