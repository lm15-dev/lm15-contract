> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Send chat completions

> Query chat models with single prompts, multi-turn conversations, and system prompts.

<Tip>
  Using a coding agent? Install the [together-chat-completions](https://github.com/togethercomputer/skills/tree/main/skills/together-chat-completions) skill to let your agent write correct chat inference code automatically. See [agent skills](/docs/agent-skills) for details.
</Tip>

## Send a single query

Use `chat.completions.create` to send a single query to a chat model:

<CodeGroup>
  ```python Python theme={null}
  from together import Together

  client = Together()

  response = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      reasoning={"enabled": False},
      messages=[
          {
              "role": "user",
              "content": "What are some fun things to do in New York?",
          }
      ],
  )

  print(response.choices[0].message.content)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  const response = await together.chat.completions.create({
    model: "Qwen/Qwen3.5-9B",
    reasoning: { enabled: false },
    messages: [{ role: "user", content: "What are some fun things to do in New York?" }],
  });

  console.log(response.choices[0].message.content)
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
       	"model": "Qwen/Qwen3.5-9B",
        "reasoning": {"enabled": false},
       	"messages": [
       		{"role": "user", "content": "What are some fun things to do in New York?"}
       	]
       }'
  ```
</CodeGroup>

The `create` method takes a model name and a `messages` array. Each message is an object with content and a role naming the author.

In the example above, the role is `user`. The `user` role tells the model that the message comes from the end user of your system, for example, a customer using your chatbot app.

The other two roles are `assistant` and `system`, covered below.

## Multi-turn conversations

Every query to a chat model is self-contained, so models don't automatically remember prior queries. The `assistant` role solves this by carrying historical context for how a model has responded to prior queries, which makes it useful for chatbots and long-running conversations.

To provide a chat history for a new query, pass the previous messages to the `messages` array. Tag the user-provided messages with the `user` role and the model's responses with the `assistant` role:

<CodeGroup>
  ```python Python theme={null}
  import os
  from together import Together

  client = Together()

  response = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      reasoning={"enabled": False},
      messages=[
          {
              "role": "user",
              "content": "What are some fun things to do in New York?",
          },
          {
              "role": "assistant",
              "content": "You could go to the Empire State Building!",
          },
          {"role": "user", "content": "That sounds fun! Where is it?"},
      ],
  )

  print(response.choices[0].message.content)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  const response = await together.chat.completions.create({
    model: "Qwen/Qwen3.5-9B",
    reasoning: { enabled: false },
    messages: [
      { role: "user", content: "What are some fun things to do in New York?" },
      { role: "assistant", content: "You could go to the Empire State Building!"},
      { role: "user", content: "That sounds fun! Where is it?" },
    ],
  });

  console.log(response.choices[0].message.content);
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
       	"model": "Qwen/Qwen3.5-9B",
        "reasoning": {"enabled": false},
       	"messages": [
          {"role": "user", "content": "What are some fun things to do in New York?"},
          {"role": "assistant", "content": "You could go to the Empire State Building!"},
          {"role": "user", "content": "That sounds fun! Where is it?" }
       	]
       }'
  ```
</CodeGroup>

How your app stores historical messages is up to you.

## Add a system prompt

You can query a model with only a user message, but you'll typically want to give the model a system prompt with context for how to respond. For example, if you're building a travel chatbot, you might tell the model to act like a helpful travel guide.

To add a system prompt, provide an initial message with the `system` role:

<CodeGroup>
  ```python Python theme={null}
  import os
  from together import Together

  client = Together()

  response = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      reasoning={"enabled": False},
      messages=[
          {"role": "system", "content": "You are a helpful travel guide."},
          {
              "role": "user",
              "content": "What are some fun things to do in New York?",
          },
      ],
  )

  print(response.choices[0].message.content)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  const response = await together.chat.completions.create({
    model: "Qwen/Qwen3.5-9B",
    reasoning: { enabled: false },
    messages: [
      {"role": "system", "content": "You are a helpful travel guide."},
      { role: "user", content: "What are some fun things to do in New York?" },
    ],
  });

  console.log(response.choices[0].message.content);
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
       	"model": "Qwen/Qwen3.5-9B",
        "reasoning": {"enabled": false},
       	"messages": [
       		{"role": "system", "content": "You are a helpful travel guide."},
       		{"role": "user", "content": "What are some fun things to do in New York?"}
       	]
       }'
  ```
</CodeGroup>

## Stream responses

Models take time to generate a full response. Streaming returns chunks as they're produced, so your app can display partial results while the model is still running instead of waiting for the entire request to finish.

To return a stream, set the `stream` option to `True`.

<CodeGroup>
  ```python Python theme={null}
  import os
  from together import Together

  client = Together()

  stream = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      reasoning={"enabled": False},
      messages=[
          {
              "role": "user",
              "content": "What are some fun things to do in New York?",
          }
      ],
      stream=True,
  )

  for chunk in stream:
      if chunk.choices:
          print(chunk.choices[0].delta.content or "", end="", flush=True)
  ```

  ```typescript TypeScript theme={null}
  import Together from 'together-ai';

  const together = new Together();

  const stream = await together.chat.completions.create({
    model: 'Qwen/Qwen3.5-9B',
    reasoning: { enabled: false },
    messages: [
      { role: 'user', content: 'What are some fun things to do in New York?' },
    ],
    stream: true,
  });

  for await (const chunk of stream) {
    process.stdout.write(chunk.choices[0]?.delta?.content || '');
  }
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
       	"model": "Qwen/Qwen3.5-9B",
        "reasoning": {"enabled": false},
       	"messages": [
       		{"role": "user", "content": "What are some fun things to do in New York?"}
       	],
        "stream": true
       }'
       
  ## Response will be a stream of Server-Sent Events with JSON-encoded payloads. For example:
  ## 
  ## data: {"choices":[{"index":0,"delta":{"content":" A"}}],"id":"85ffbb8a6d2c4340-EWR","token":{"id":330,"text":" A","logprob":1,"special":false},"finish_reason":null,"generated_text":null,"stats":null,"usage":null,"created":1709700707,"object":"chat.completion.chunk"}
  ## data: {"choices":[{"index":0,"delta":{"content":":"}}],"id":"85ffbb8a6d2c4340-EWR","token":{"id":28747,"text":":","logprob":0,"special":false},"finish_reason":null,"generated_text":null,"stats":null,"usage":null,"created":1709700707,"object":"chat.completion.chunk"}
  ## data: {"choices":[{"index":0,"delta":{"content":" Sure"}}],"id":"85ffbb8a6d2c4340-EWR","token":{"id":12875,"text":" Sure","logprob":-0.00724411,"special":false},"finish_reason":null,"generated_text":null,"stats":null,"usage":null,"created":1709700707,"object":"chat.completion.chunk"}
  ```
</CodeGroup>

## Run async requests in parallel from Python

By default, Python's Together client runs requests synchronously, so multiple queries execute in sequence even when they're independent. To run independent calls in parallel, use the `AsyncTogether` module from the Python library:

```python Python theme={null}
import os, asyncio
from together import AsyncTogether

async_client = AsyncTogether()
messages = [
    "What are the top things to do in San Francisco?",
    "What country is Paris in?",
]


async def async_chat_completion(messages):
    async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))
    tasks = [
        async_client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": message}],
        )
        for message in messages
    ]
    responses = await asyncio.gather(*tasks)

    for response in responses:
        print(response.choices[0].message.content)


asyncio.run(async_chat_completion(messages))
```
