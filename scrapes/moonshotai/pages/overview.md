> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Quickstart

> Create an API Key and complete your first Kimi API call.

Kimi API lets you interact with Kimi models and is compatible with both the OpenAI and Anthropic API formats. Prepare an API Key, choose a model, and configure `base_url` to make requests through the HTTP API, the OpenAI SDK, or the Anthropic SDK.

<Info>
  [Kimi K3](/docs/guide/kimi-k3-quickstart) is now officially available — Kimi's most capable model to date, with a 1M-token context window and native visual understanding. It is well suited for programming agent scenarios such as [Claude Code](guide/claude-code-kimi), as well as knowledge work and deep reasoning.
</Info>

## Get started

<Steps>
  <Step title="Get an API Key">
    Visit the [Kimi API Platform](https://platform.kimi.ai/), sign in, then go to [API Keys](https://platform.kimi.ai/console/api-keys) to create and copy an API Key.

    Keep your API Key secure. Do not share it with others or hard-code it directly in your application. We recommend storing it in an environment variable:

    ```bash theme={null}
    export MOONSHOT_API_KEY="YOUR_KIMI_API_KEY"
    ```

    <CardGroup cols={2}>
      <Card title="Kimi API Platform" icon="link" href="https://platform.kimi.ai/">
        Sign in to the platform to access the console, development workspace, and user center.
      </Card>

      <Card title="API Keys" icon="key" href="https://platform.kimi.ai/console/api-keys">
        Create, copy, and manage the keys used for API calls.
      </Card>
    </CardGroup>
  </Step>

  <Step title="Choose a model">
    For a quickstart, we recommend starting with Kimi K3; you can also choose Kimi K2.7 Code or Kimi K2.6 for specific scenarios.

    <CardGroup cols={3}>
      <Card title="Kimi K3" icon="rocket" href="/docs/guide/kimi-k3-quickstart">
        Kimi K3 is our flagship model for long-horizon coding and end-to-end knowledge work — 2.8 trillion parameters, a 1M-token context window, and industry-leading intelligence.
      </Card>

      <Card title="Kimi K2.7 Code" icon="code" href="/docs/guide/kimi-k2-7-code-quickstart">
        A coding-focused model with a 256K context window, text/image/video input, and thinking mode. Choose `kimi-k2.7-code-highspeed` when you need higher output speed.
      </Card>

      <Card title="Kimi K2.6" icon="brain" href="/docs/guide/kimi-k2-6-quickstart">
        A powerful general-purpose model with a 256K context window, text/image/video input, and both thinking and non-thinking modes. Use it for general chat, agent tasks, visual understanding, and complex reasoning.
      </Card>
    </CardGroup>

    <Tip>
      If you are not sure which model to choose, start with `kimi-k3`. If your task is mainly code generation, code editing, or programming agents and you need higher output speed, choose `kimi-k2.7-code-highspeed`.
    </Tip>
  </Step>

  <Step title="Choose an integration method">
    Kimi API is compatible with both the OpenAI and Anthropic API formats, so you can choose the integration method that best fits your technology stack.

    <CardGroup cols={2}>
      <Card title="Chat Completions API" icon="globe" href="/docs/api/chat">
        OpenAI-compatible format, with support for the OpenAI SDK and HTTP access from any language.
      </Card>

      <Card title="Responses API" icon="bolt" href="/docs/api/responses">
        OpenAI-compatible format for generating text/JSON output or calling function tools.
      </Card>

      <Card title="Messages API" icon="comment" href="/docs/api/messages">
        Anthropic Messages API compatible, for integrating with the Anthropic SDK, Claude Code, and similar tools.
      </Card>

      <Card title="Playground" icon="terminal" href="https://platform.kimi.ai/playground">
        Test prompts, model behavior, and business examples without writing code.
      </Card>
    </CardGroup>
  </Step>

  <Step title="Make your first call">
    The following examples use the Kimi K3 model. Replace `MOONSHOT_API_KEY` with the API Key you created on the platform, or set an environment variable with the same name before running the examples.

    <Note>
      The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
    </Note>

    <Tip>
      To use the high-speed model for coding scenarios, replace `kimi-k3` in the examples with `kimi-k2.7-code-highspeed`; to call Kimi K2.6, replace it with `kimi-k2.6`.
    </Tip>

    <Tabs>
      <Tab title="python">
        ```python theme={null}
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ["MOONSHOT_API_KEY"],
            base_url="https://api.moonshot.ai/v1",
        )

        completion = client.chat.completions.create(
            model="kimi-k3",
            messages=[
                {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are especially good at conversations in Chinese and English. You provide users with safe, helpful, and accurate answers. You also refuse to answer any questions involving terrorism, racism, pornography, violence, or similar harmful content. Moonshot AI is a proper noun and must not be translated into other languages."},
                {"role": "user", "content": "Hi, my name is Li Lei. What is 1+1?"}
            ]
        )

        print(completion.choices[0].message.content)
        ```
      </Tab>

      <Tab title="curl">
        ```bash theme={null}
        curl https://api.moonshot.ai/v1/chat/completions \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $MOONSHOT_API_KEY" \
            -d '{
                "model": "kimi-k3",
                "messages": [
                    {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are especially good at conversations in Chinese and English. You provide users with safe, helpful, and accurate answers. You also refuse to answer any questions involving terrorism, racism, pornography, violence, or similar harmful content. Moonshot AI is a proper noun and must not be translated into other languages."},
                    {"role": "user", "content": "Hi, my name is Li Lei. What is 1+1?"}
                ]
           }'
        ```
      </Tab>

      <Tab title="node.js">
        ```js theme={null}
        const OpenAI = require("openai");

        const client = new OpenAI({
          apiKey: process.env.MOONSHOT_API_KEY,
          baseURL: "https://api.moonshot.ai/v1",
        });

        async function main() {
          const completion = await client.chat.completions.create({
            model: "kimi-k3",
            messages: [
              {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are especially good at conversations in Chinese and English. You provide users with safe, helpful, and accurate answers. You also refuse to answer any questions involving terrorism, racism, pornography, violence, or similar harmful content. Moonshot AI is a proper noun and must not be translated into other languages."},
              {"role": "user", "content": "Hi, my name is Li Lei. What is 1+1?"}
            ]
          });

          console.log(completion.choices[0].message.content);
        }

        main();
        ```
      </Tab>
    </Tabs>

    Before running the examples, prepare:

    1. Python 3.8 or later, or Node.js 18 or later.
    2. OpenAI SDK 1.0.0 or later. Kimi API is compatible with the OpenAI API format, so you can call Kimi directly with the OpenAI Python or Node.js SDK.
       ```text theme={null}
       pip install --upgrade 'openai>=1.0' # Python
       npm install openai@latest # Node.js
       ```
    3. An API Key. Create an API Key in the [Kimi API Platform](https://platform.kimi.ai/console/api-keys), then pass it to the `OpenAI Client` so the platform can identify your account.

    If the code runs successfully without errors, you will see output similar to:

    ```text theme={null}
    Hello, Li Lei! 1+1 equals 2. This is a basic arithmetic question. If you have any other questions or need help, feel free to let me know.
    ```

    *Note: Because Kimi models are nondeterministic, the actual response may not exactly match the example above.*
  </Step>
</Steps>

## Explore more features

<CardGroup cols={3}>
  <Card title="Streaming output" icon="bolt" href="/docs/api/chat">
    Enable `stream` to receive tokens as they are generated. Useful for chat, code generation, and long-form text output.
  </Card>

  <Card title="Multi-turn chat" icon="comments" href="/docs/guide/engage-in-multi-turn-conversations-using-kimi-api">
    Maintain a `messages` list to preserve context history, letting the model remember the conversation.
  </Card>

  <Card title="Multimodal input" icon="image" href="/docs/guide/use-kimi-vision-model">
    Kimi K3, Kimi K2.7 Code, and Kimi K2.6 all support text, image, and video input.
  </Card>

  <Card title="Tool calls" icon="wrench" href="/docs/guide/use-kimi-api-to-complete-tool-calls">
    Let the model call external functions or APIs for Agent tasks, web search, and complex workflows.
  </Card>

  <Card title="JSON Mode" icon="code" href="/docs/guide/use-json-mode-feature-of-kimi-api">
    Force the model to output valid JSON for structured data extraction and downstream integration.
  </Card>

  <Card title="Thinking models" icon="brain" href="/docs/guide/use-thinking-models">
    Use reasoning capabilities for complex tasks, multi-step tool use, and Agent workflows.
  </Card>
</CardGroup>

### Streaming output

```json theme={null}
{
  "model": "kimi-k3",
  "messages": [
    {
      "role": "user",
      "content": "Please explain what recursion is and give a Python example."
    }
  ],
  "stream": true
}
```

### Multimodal input

```json theme={null}
{
  "model": "kimi-k3",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,..."
          }
        },
        {
          "type": "text",
          "text": "Please describe this image."
        }
      ]
    }
  ]
}
```

<Warning>
  For larger videos, or images and videos that need to be referenced multiple times, we recommend using file uploads. Images should be no larger than 4K resolution, and videos should be no larger than 1080p.
</Warning>

## Related resources

<CardGroup cols={2}>
  <Card title="Kimi K3 model" icon="rocket" href="/docs/guide/kimi-k3-quickstart">
    View Kimi K3 capabilities, calling examples, and best practices.
  </Card>

  <Card title="Kimi K2.7 Code model" icon="code" href="/docs/guide/kimi-k2-7-code-quickstart">
    View Kimi K2.7 Code capabilities, calling examples, and best practices.
  </Card>

  <Card title="Kimi K2.6 model" icon="brain" href="/docs/guide/kimi-k2-6-quickstart">
    View Kimi K2.6 capabilities, image/video understanding examples, and tool calling guidance.
  </Card>

  <Card title="Model list" icon="list" href="/docs/models">
    View currently available model names and descriptions.
  </Card>

  <Card title="Join the Kimi Developer Community" icon="comments" href="/docs/api/join-the-community">
    Ask questions, share feedback, and showcase what you are building with Kimi.
  </Card>
</CardGroup>
