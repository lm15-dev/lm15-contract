> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Parameters

> The full list of parameters you can pass to the chat completions endpoint.

A high-level overview of chat completion parameters and when to use them. For parameters tied to a specific capability (structured outputs, function calling, logprobs, streaming), see [Capability-specific parameters](#capability-specific-parameters) at the bottom.

For the complete schema, including every supported field along with its types and ranges, see the [chat completions API reference](/reference/chat-completions).

<Note>
  **Where to find a model's default parameter values:** Each model publishes its defaults in the `generation_config.json` file on Hugging Face. For example, Llama 3.3 70B Instruct lists `temperature: 0.6` and `top_p: 0.9`. If a parameter isn't defined there, no value is passed for it (the inference engine's own default applies).
</Note>

## Quick reference

Match the problem you're solving to the parameter most likely to help.

* **Output cuts off mid-sentence:** Increase `max_tokens`.
* **Need exactly one token (yes/no, class label):** Set `max_tokens` to `1`.
* **Responses feel generic or repetitive:** Increase `temperature`, or set `frequency_penalty` to a small positive value.
* **Output loops on the same phrase:** Set `repetition_penalty` to about `1.1`.
* **Need the same answer every run (evals, regression tests):** Set `seed` and use a low `temperature`.
* **Need machine-parseable output:** Use `response_format` with a JSON schema. See [Structured outputs](/docs/inference/chat/structured-outputs).
* **Need token-level confidence scores:** Set `logprobs`. See [Logprobs](/docs/inference/chat/logprobs).

## Length and stopping

### `max_tokens`

The maximum number of tokens the model is allowed to generate in the response. Shorter values return faster but risk truncating the answer mid-sentence.

Increase this when the model is cutting off long answers. Decrease it (sometimes to `1`) when you only need a single token, like a yes/no or a class label.

Typical default: unset (the model generates until it hits a stop condition or the context limit).

### `stop`

A string or list of strings that tell the model to stop generating as soon as one of them is produced. Useful for short, structured outputs where you know the boundary, for example a newline between rows or a closing tag.

Set it when you want the model to stop early without parsing the response yourself. Leave it unset for free-form text.

Typical default: unset.

<CodeGroup>
  ```python Python theme={null}
  import os
  from together import Together

  client = Together()

  response = client.chat.completions.create(
      model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
      messages=[
          {
              "role": "user",
              "content": "Classify this review as Positive or Negative: 'Loved it.'",
          },
      ],
      max_tokens=100,
      stop=["\n\n"],
  )
  print(response.choices[0].message.content)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const client = new Together();

  const response = await client.chat.completions.create({
    model: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages: [
      { role: "user", content: "Classify this review as Positive or Negative: 'Loved it.'" },
    ],
    max_tokens: 100,
    stop: ["\n\n"],
  });
  console.log(response.choices[0].message.content);
  ```

  ```bash cURL theme={null}
  curl -X POST https://api.together.ai/v1/chat/completions \
    -H "Authorization: Bearer $TOGETHER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
      "messages": [
        {"role": "user", "content": "Classify this review as Positive or Negative: '\''Loved it.'\''"}
      ],
      "max_tokens": 100,
      "stop": ["\n\n"]
    }'
  ```
</CodeGroup>

## Sampling

`temperature`, `top_p`, and `top_k` all narrow the candidate token set. In most cases, you'll want to tune one of them and leave the others at their defaults. Similarly, `repetition_penalty`, `frequency_penalty`, and `presence_penalty` all discourage repetition in different ways. Pick the parameter that fits the issue you're trying to address rather than stacking them all together.

### `temperature`

A decimal that controls how random the output is. `0` always picks the highest-probability token (deterministic for a given prompt). Values closer to `1` introduce more variety. Values above `1` are usually too noisy for production workloads.

Lower it for extraction, classification, and other tasks where there is one right answer. Raise it for brainstorming, creative writing, or when responses feel repetitive.

Typical default: model-specific (often `0.7`, see `generation_config.json`).

### `top_p`

Nucleus sampling. The model samples only from the smallest set of tokens whose cumulative probability exceeds `top_p`. A value of `0.9` means "only consider tokens that together make up the top 90% of probability mass."

Use it as a softer alternative to `temperature`. Most users tune one or the other, not both.

Typical default: `1.0` (no truncation).

### `top_k`

Limits sampling to the `k` most likely next tokens. `top_k=1` is greedy decoding. Larger values allow more variety.

Use it when you want a hard cap on the candidate set. Like `top_p`, prefer tuning either `top_k` or `top_p`, not both.

Typical default: `0` or unset (no cap).

### `repetition_penalty`

Reduces the probability of tokens that have already appeared anywhere in the prompt or response. Values above `1.0` discourage repetition. Values below `1.0` encourage it.

Raise it slightly (for example, `1.1`) when the model loops or repeats phrases. Leave it at `1.0` otherwise, since aggressive values degrade fluency.

Typical default: `1.0`.

### `frequency_penalty`

Penalizes tokens proportionally to how often they have already appeared in the response so far. Higher positive values make the model less likely to repeat the same exact tokens. Negative values make repetition more likely. Range: `-2.0` to `2.0`.

Use it to reduce verbatim repetition in long generations (lists, summaries, code). It is finer-grained than `repetition_penalty` because the penalty scales with frequency.

Typical default: `0`.

### `presence_penalty`

Penalizes tokens that have appeared at all in the response so far, regardless of how many times. Higher positive values push the model toward new topics and vocabulary. Range: `-2.0` to `2.0`.

Use it when you want the model to cover more ground (idea generation, topic expansion) rather than circle the same concepts.

Typical default: `0`.

### `seed`

An integer that makes sampling deterministic. With the same `seed`, prompt, model, and parameters, the model returns the same response. Determinism is best-effort and may not hold across model or backend updates.

Set it for reproducibility in evals, regression tests, and debugging.

Typical default: unset (responses vary between calls).

<CodeGroup>
  ```python Python theme={null}
  import os
  from together import Together

  client = Together()

  response = client.chat.completions.create(
      model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
      messages=[
          {"role": "user", "content": "Give me one fun fact about octopuses."}
      ],
      seed=42,
      temperature=0.7,
  )
  print(response.choices[0].message.content)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const client = new Together();

  const response = await client.chat.completions.create({
    model: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages: [{ role: "user", content: "Give me one fun fact about octopuses." }],
    seed: 42,
    temperature: 0.7,
  });
  console.log(response.choices[0].message.content);
  ```

  ```bash cURL theme={null}
  curl -X POST https://api.together.ai/v1/chat/completions \
    -H "Authorization: Bearer $TOGETHER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
      "messages": [{"role": "user", "content": "Give me one fun fact about octopuses."}],
      "seed": 42,
      "temperature": 0.7
    }'
  ```
</CodeGroup>

## Response shape

### `n`

The number of independent completions to generate for a given prompt. Each completion appears as a separate entry in `choices`. Higher values cost more (you pay for the output tokens of every completion).

Use it for ranking or self-consistency: generate several candidates, then pick or vote among them.

Typical default: `1`.

## Capability-specific parameters

These parameters belong to features with their own dedicated pages. Each link below covers the full schema, supported models, and end-to-end examples.

* **`response_format`:** Constrain the output to JSON or a JSON Schema so you can parse it directly. See [Structured outputs](/docs/inference/chat/structured-outputs).
* **`tools` and `tool_choice`:** Let the model call functions you define, with control over whether and which tool it picks. See [Function calling](/docs/inference/function-calling/overview).
* **`logprobs`:** Return per-token log probabilities for confidence scoring and token-level analysis. See [Logprobs](/docs/inference/chat/logprobs).
* **`stream`:** Receive the response as server-sent events as the model generates them. See [Stream responses](/docs/inference/chat/overview#stream-responses).
