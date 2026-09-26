> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Reasoning

> Use reasoning models that think step-by-step before answering.

Reasoning models are trained to think step-by-step before responding with an answer. Given an input prompt, they first produce a chain of thought, visible as tokens in a dedicated output field (`reasoning` or `reasoning_content`, depending on the model), and then output a final answer in the `content` field.

## Supported models

Reasoning models fall into a few behavioral types:

* **Reasoning only:** Always produces reasoning tokens. Cannot be toggled off.
* **Hybrid:** Supports both reasoning and non-reasoning modes via `reasoning={"enabled": True/False}`.
* **Adjustable effort:** Supports the `reasoning_effort` parameter to control reasoning depth (`"low"`, `"medium"`, or `"high"`).

The following models support reasoning on [serverless inference](/docs/serverless/models):

| Model                | API string                         | Type                   | Context length |
| :------------------- | :--------------------------------- | :--------------------- | :------------- |
| MiniMax M3           | `MiniMaxAI/MiniMax-M3`             | Hybrid (on by default) | 512K           |
| DeepSeek V4 Pro 0813 | `deepseek-ai/DeepSeek-V4-Pro-0813` | Hybrid (on by default) | 1M             |
| GLM-5.2              | `zai-org/GLM-5.2`                  | Hybrid (on by default) | 512K           |
| Kimi K3              | `moonshotai/Kimi-K3`               | Hybrid (on by default) | 1M             |
| Qwen3.6 Plus         | `Qwen/Qwen3.6-Plus`                | Hybrid (on by default) | 1M             |
| Qwen3.5 9B           | `Qwen/Qwen3.5-9B`                  | Hybrid (on by default) | 262K           |
| GPT-OSS 120B         | `openai/gpt-oss-120b`              | Adjustable effort      | 128K           |

Additional reasoning models, including Kimi K2.6, GLM-5, Cogito v2.1 671B, DeepSeek-R1 and its distillations, Qwen QwQ-32B, and DeepSeek V3.1 (hybrid), are available for [dedicated model inference](/docs/dedicated-endpoints/models).

## Quickstart

Reasoning models return the chain of thought in a separate field alongside `content` in the response. The field name varies by model (see [Handle reasoning tokens](#handle-reasoning-tokens)). Reasoning models produce longer outputs, so you should stream the response:

<CodeGroup>
  ```python Python theme={null}
  from together import Together

  client = Together()

  stream = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Pro-0813",
      messages=[
          {
              "role": "user",
              "content": "Which number is bigger, 9.11 or 9.9?",
          }
      ],
      stream=True,
  )

  for chunk in stream:
      if chunk.choices:
          delta = chunk.choices[0].delta

          # Show reasoning tokens if present
          if hasattr(delta, "reasoning") and delta.reasoning:
              print(delta.reasoning, end="", flush=True)

          # Show content tokens if present
          if hasattr(delta, "content") and delta.content:
              print(delta.content, end="", flush=True)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";
  import type { ChatCompletionChunk } from "together-ai/resources/chat/completions";

  const together = new Together();

  const stream = await together.chat.completions.stream({
    model: "deepseek-ai/DeepSeek-V4-Pro-0813",
    messages: [
      { role: "user", content: "Which number is bigger, 9.11 or 9.9?" },
    ],
  } as any);

  for await (const chunk of stream) {
    const delta = chunk.choices[0]?.delta as ChatCompletionChunk.Choice.Delta & {
      reasoning?: string;
    };

    // Show reasoning tokens if present
    if (delta?.reasoning) process.stdout.write(delta.reasoning);

    // Show content tokens if present
    if (delta?.content) process.stdout.write(delta.content);
  }
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
          "model": "deepseek-ai/DeepSeek-V4-Pro-0813",
          "messages": [
            {"role": "user", "content": "Which number is bigger, 9.11 or 9.9?"}
          ],
          "stream": true
       }'
  ```
</CodeGroup>

The response contains both the model's reasoning process and the final answer:

```json theme={null}
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "9.9 is bigger than 9.11.",
        "reasoning": "Let me compare 9.11 and 9.9. Both have 9 as the integer part, so I need to compare the decimal parts: 0.11 vs 0.9. Since 0.9 = 0.90, and 0.90 > 0.11, we know 9.9 > 9.11."
      }
    }
  ]
}
```

<Info>
  DeepSeek-R1 uses a different format. It outputs reasoning inside `<think>` tags within the `content` field rather than a separate `reasoning` field. See [Handle reasoning tokens](#handle-reasoning-tokens) for details.
</Info>

## Enable and disable reasoning

Hybrid models let you toggle reasoning on or off using the `reasoning` parameter. This is useful when you want reasoning for complex queries but want faster, cheaper responses for simple ones.

<CodeGroup>
  ```python Python theme={null}
  from together import Together

  client = Together()

  # Enable reasoning
  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Pro-0813",
      messages=[
          {
              "role": "user",
              "content": "Prove that the square root of 2 is irrational.",
          }
      ],
      reasoning={"enabled": True},
      stream=True,
  )

  for chunk in response:
      if not chunk.choices:
          continue
      delta = chunk.choices[0].delta

      if hasattr(delta, "reasoning") and delta.reasoning:
          print(delta.reasoning, end="", flush=True)

      if hasattr(delta, "content") and delta.content:
          print(delta.content, end="", flush=True)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  const stream = await together.chat.completions.stream({
    model: "deepseek-ai/DeepSeek-V4-Pro-0813",
    messages: [
      { role: "user", content: "Prove that the square root of 2 is irrational." },
    ],
    reasoning: { enabled: true },
  });

  for await (const chunk of stream) {
    const delta = chunk.choices[0]?.delta;

    if (delta?.reasoning) process.stdout.write(delta.reasoning);
    if (delta?.content) process.stdout.write(delta.content);
  }
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
          "model": "deepseek-ai/DeepSeek-V4-Pro-0813",
          "messages": [
            {"role": "user", "content": "Prove that the square root of 2 is irrational."}
          ],
          "reasoning": {"enabled": true},
          "stream": true
       }'
  ```
</CodeGroup>

Alternatively, you can enable or disable reasoning using `chat_template_kwargs`:

```python theme={null}
response = client.chat.completions.create(
    model="Qwen/Qwen3.5-9B",
    messages=[
        {
            "role": "user",
            "content": "Prove that the square root of 2 is irrational.",
        }
    ],
    chat_template_kwargs={
        "thinking": True,
        # or use "enable_thinking": True
    },
    stream=True,
)
```

<Warning>
  GLM-5.2 has thinking enabled by default. Pass `reasoning={"enabled": False}` to disable it for simple tasks where reasoning overhead isn't needed.
</Warning>

For the list of hybrid models, see [Supported models](#supported-models).

<Info>
  For DeepSeek V3.1, function calling only works in non-reasoning mode (`reasoning={"enabled": False}`).
</Info>

## Reasoning effort

GPT-OSS models support a `reasoning_effort` parameter that controls how much computation the model spends on reasoning. This lets you balance accuracy against cost and latency.

* **`"low"`**: Faster responses for simpler tasks with reduced reasoning depth.
* **`"medium"`**: Balanced performance for most use cases (recommended default).
* **`"high"`**: Maximum reasoning for complex problems. Set `max_tokens` to \~30,000 with this setting.

DeepSeek V4 Pro 0813 accepts only `"high"` and `"max"` for `reasoning_effort`. Other values are mapped automatically:

* `"low"` and `"medium"` map to `"high"`.
* `"high"` and `"xhigh"` map to `"max"`.

<CodeGroup>
  ```python Python theme={null}
  from together import Together

  client = Together()

  stream = client.chat.completions.create(
      model="openai/gpt-oss-120b",
      messages=[
          {
              "role": "user",
              "content": "Solve: If all roses are flowers and some flowers are red, can we conclude that some roses are red?",
          }
      ],
      temperature=1.0,
      top_p=1.0,
      reasoning_effort="medium",
      stream=True,
  )

  for chunk in stream:
      if chunk.choices:
          print(chunk.choices[0].delta.content or "", end="", flush=True)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  const stream = await together.chat.completions.create({
    model: "openai/gpt-oss-120b",
    messages: [
      {
        role: "user",
        content:
          "Solve: If all roses are flowers and some flowers are red, can we conclude that some roses are red?",
      },
    ],
    temperature: 1.0,
    top_p: 1.0,
    reasoning_effort: "medium",
    stream: true,
  });

  for await (const chunk of stream) {
    process.stdout.write(chunk.choices[0]?.delta?.content || "");
  }
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
          "model": "openai/gpt-oss-120b",
          "messages": [
            {"role": "user", "content": "Solve: If all roses are flowers and some flowers are red, can we conclude that some roses are red?"}
          ],
          "temperature": 1.0,
          "top_p": 1.0,
          "reasoning_effort": "medium",
          "stream": true
       }'
  ```
</CodeGroup>

### Controlling reasoning depth via prompting

For models that don't support a `reasoning_effort` parameter, you can influence how much the model thinks by including instructions in your prompt. This is a simple way to reduce token usage and latency when the problem doesn't warrant deep reasoning.

Ask the model to keep its thinking concise:

```python theme={null}
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Pro-0813",
    messages=[
        {
            "role": "user",
            "content": "Please be succinct in your thinking.\n\nWhat is the derivative of x^3 + 2x?",
        }
    ],
    stream=True,
)
```

You can also suggest an approximate budget for the reasoning process:

```python theme={null}
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Pro-0813",
    messages=[
        {
            "role": "user",
            "content": "Please use around 1000 words to think, but do not literally count each one.\n\nExplain why quicksort has O(n log n) average-case complexity.",
        }
    ],
    stream=True,
)
```

<Info>
  This technique works across all reasoning models. The model won't hit an exact word count, but it reliably produces shorter or longer reasoning chains in response to the guidance. Combine it with `max_tokens` for a hard ceiling on total output.
</Info>

## Thinking modes

Many of our models support advanced thinking modes that control how reasoning integrates with tool calling and multi-turn conversations.

### Interleaved thinking

The default mode. The model reasons between tool calls and after receiving tool results, enabling complex step-by-step reasoning where it interprets each tool output before deciding what to do next.

```python theme={null}
from together import Together

client = Together()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"],
            },
        },
    }
]

response = client.chat.completions.create(
    model="zai-org/GLM-5.2",
    messages=[
        {"role": "user", "content": "What's the weather in Paris and Tokyo?"}
    ],
    tools=tools,
)

print(
    json.dumps(
        response.choices[0].message.model_dump()["tool_calls"],
        indent=2,
    )
)
```

In this mode, the model will reason about which tool to call first, interpret the result, then reason again before making the next call.

### Preserved thinking

The model retains reasoning content from previous assistant turns in the conversation context, improving reasoning continuity and cache hit rates. This is ideal for coding agents and multi-turn agentic workflows.

Enable preserved thinking by setting `clear_thinking` to `false`:

```python theme={null}
response = client.chat.completions.create(
    model="zai-org/GLM-5.2",
    messages=messages,
    tools=tools,
    stream=True,
    chat_template_kwargs={
        "clear_thinking": False,  # Preserved Thinking
    },
)
```

When using preserved thinking, include the unmodified `reasoning_content` from previous turns back in the conversation:

```python theme={null}
messages.append(
    {
        "role": "assistant",
        "content": content,
        "reasoning_content": reasoning_content,  # Return reasoning content faithfully
        "tool_calls": tool_calls,
    }
)
```

<Warning>
  When using preserved thinking, all consecutive `reasoning_content` blocks must exactly match the original sequence generated by the model. Don't reorder or edit these blocks. Otherwise, performance may degrade and cache hit rates will drop.
</Warning>

### Turn-level thinking

Control reasoning on a per-turn basis within the same session. Enable thinking for hard turns (planning, debugging) and disable it for simple ones (facts, rewording) to save cost.

For a complete streamed tool-calling example, see the [GLM-5.3 quickstart](/docs/glm-5.3-quickstart#call-tools).

## Handle reasoning tokens

There are two patterns for accessing reasoning tokens, depending on the model.

### Separate reasoning field

Some models (DeepSeek V4 Pro 0813, GPT-OSS) return reasoning in a dedicated `reasoning` field on the response message or streaming delta. Others (Kimi K3, GLM-5.2, MiniMax M3) use a `reasoning_content` field the same way:

```python theme={null}
from together import Together

client = Together()

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Pro-0813",
    messages=[
        {
            "role": "user",
            "content": "Say test 10 times",
        }
    ],
)

print("Reasoning:", response.choices[0].message.reasoning)
print("Answer:", response.choices[0].message.content)
```

<Note>
  Use the same field for input and output. The model returns its chain of thought in `reasoning` or `reasoning_content` (also on the streaming `delta`), and you pass it back under the same key when you send a prior assistant turn to the API for [preserved thinking](#preserved-thinking) or multi-turn tool calling.
</Note>

### `<think>` tags in content

DeepSeek-R1 embeds reasoning directly in the `content` field using `<think>` tags:

```plain theme={null}
<think>
Let me compare 9.11 and 9.9 by looking at their decimal parts...
0.11 vs 0.9 , since 0.9 is larger, 9.9 > 9.11.
</think>

**Answer:** 9.9 is bigger.
```

To extract the reasoning and answer separately:

```python theme={null}
import re

content = response.choices[0].message.content

think_match = re.search(r"<think>(.*?)</think>", content, re.DOTALL)

reasoning = think_match.group(1).strip() if think_match else ""

answer = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
```

## Structured outputs with reasoning models

Reasoning models can return JSON that conforms to a schema, the same way non-reasoning models do. The model still produces its chain of thought in the `reasoning` field, then writes the structured answer to `content`.

Example: have DeepSeek V4 Pro 0813 solve a math problem and return the steps as typed JSON.

```python Python theme={null}
import json
from together import Together
from pydantic import BaseModel

client = Together()


class Step(BaseModel):
    explanation: str
    output: str


class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str


completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Pro-0813",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful math tutor. Guide the user through the solution step by step.",
        },
        {"role": "user", "content": "how can I solve 8x + 7 = -23"},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "math_reasoning",
            "schema": MathReasoning.model_json_schema(),
        },
    },
)

math_reasoning = json.loads(completion.choices[0].message.content)
print(json.dumps(math_reasoning, indent=2))
```

Example output:

```json JSON theme={null}
{
  "steps": [
    {
      "explanation": "To solve 8x + 7 = -23, I need to isolate x.",
      "output": ""
    },
    {
      "explanation": "Subtract 7 from both sides.",
      "output": "8x = -30"
    },
    {
      "explanation": "Divide both sides by 8.",
      "output": "x = -30/8 = -15/4"
    }
  ],
  "final_answer": "x = -15/4"
}
```

For the full structured-outputs reference, see [Structured outputs](/docs/inference/chat/structured-outputs).

## Prompting best practices

Prompt reasoning models differently than standard models:

| Tip                                         | Details                                                                                                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Use the right temperature**               | DeepSeek-R1: 0.6. DeepSeek V4 Pro 0813 / GLM-5.2 / Kimi K3 / GPT-OSS: 1.0.                                                                                          |
| **System prompts vary by model**            | DeepSeek-R1: omit system prompts entirely. Kimi models: use `"You are Kimi, an AI assistant created by Moonshot AI."` GPT-OSS: use the `developer` role message.    |
| **Don't add chain-of-thought instructions** | These models already reason step-by-step. Telling them to "think step by step" is unnecessary and can hurt performance.                                             |
| **Avoid few-shot examples**                 | Few-shot prompting can degrade performance. Describe the task and desired output format instead.                                                                    |
| **Think in goals, not steps**               | Provide high-level objectives (e.g., "Analyze this data and identify trends") and let the model determine the methodology. Over-prompting limits reasoning ability. |
| **Structure your prompt**                   | Use XML tags, markdown formatting, or labeled sections to separate different parts of your prompt.                                                                  |
| **Set generous `max_tokens`**               | Reasoning tokens can number in the tens of thousands for complex problems. Ensure your `max_tokens` accommodates both reasoning and content.                        |

## When not to use reasoning

Non-reasoning models are a better fit when:

* **Latency is critical**: Real-time voice agents, instant-response chatbots, or other applications that need fast responses.
* **Tasks are straightforward**: Simple classification, basic text generation, factual lookups, or quick summaries don't benefit from extended reasoning.
* **Cost is the priority**: High-volume pipelines processing many simple queries. Reasoning tokens significantly increase per-query costs.

For these use cases, consider faster non-reasoning models like [Llama 3.3 70B](/docs/serverless/models) or [Qwen3.5 9B](/docs/serverless/models).

## Manage costs and latency

Reasoning tokens can vary from a few hundred for simple problems to tens of thousands for complex challenges. Strategies to keep costs and latency in check:

* **Count reasoning tokens**: Reasoning output is billed as completion tokens and reported under `usage.completion_tokens_details.reasoning_tokens`. See [OpenAI compatibility](/docs/inference/openai-compatibility#response-shape-differences) for the full usage-object shape, which varies by model.
* **Use `max_tokens`**: Set a token limit to cap total output. This reduces costs but may truncate reasoning on complex problems. Find the right balance for your use case.
* **Toggle reasoning on hybrid models**: Use `reasoning={"enabled": False}` for simple queries and only enable it when the task benefits from deeper analysis.
* **Use reasoning effort levels**: On GPT-OSS, use `reasoning_effort="low"` for routine tasks and `"high"` for critical decisions.
* **Use turn-level thinking**: On GLM-5.2, disable thinking for simple turns and enable it only for complex ones within the same session.
* **Prompt for shorter reasoning**: Include instructions like "Be succinct in your thinking" to reduce reasoning token usage on simpler problems. See [Controlling reasoning depth via prompting](#controlling-reasoning-depth-via-prompting).
* **Stream responses**: Since reasoning models produce longer outputs, streaming with `stream=True` provides a better user experience by showing partial results as they arrive.
