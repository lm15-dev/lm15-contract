> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use the Streaming Feature of the Kimi API

> Use Kimi API server-sent events to reduce time to first token, parse incremental output, and capture final usage data.

After receiving a question, the Kimi large language model first performs inference and then generates the answer one Token at a time. Streaming sends Tokens to the client as soon as a certain number of them (usually 1 Token) is generated, instead of waiting until the full response is complete. Waiting for the complete response usually takes several seconds — for complex questions and long replies it can stretch to 10 or even 20 seconds; with streaming, users see the first Token immediately, which significantly reduces wait time. When you chat with [Kimi AI Assistant](https://kimi.ai), the reply appears character by character — that is streaming in action.

## Enable Streaming Output

Set `stream=True` in the request to enable streaming. The SDK then returns an iterable — loop over it to read data chunks one by one. Each chunk has a structure similar to a completion, except the `message` field is replaced by a `delta` field. If you need token usage in a streaming response, also pass `stream_options: {"include_usage": true}` (write `{"include_usage": True}` in the Python SDK).

A `delta` may carry three kinds of incremental data:

* `content`: the answer text, delivered fragment by fragment;
* `reasoning_content`: the reasoning output of thinking models, delivered before `content` and `tool_calls`. The SDK type definitions do not declare this field — in Python, read it with `hasattr`/`getattr`;
* `tool_calls`: tool calls. Fragments of the same tool call share the same `index`; `id`, `type`, and `function.name` appear only once, in the first fragment, while `function.arguments` arrives as JSON string fragments that must be appended (never overwritten) and parsed only after the stream ends.

The following example shows how to fold all three kinds of fragments while streaming:

<Note>
  The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
</Note>

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    import json
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url="https://api.moonshot.ai/v1",
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather of a city.",
                "parameters": {
                    "type": "object",
                    "required": ["city"],
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city, e.g. Beijing",
                        }
                    },
                },
            },
        }
    ]

    stream = client.chat.completions.create(
        model="kimi-k3",
        messages=[
            {"role": "system", "content": "You are Kimi, an artificial intelligence assistant provided by Moonshot AI, who is better at conversing in Chinese and English. You provide users with safe, helpful, and accurate answers. At the same time, you refuse to answer any questions related to terrorism, racism, pornography, and violence. Moonshot AI is a proper noun and should not be translated into other languages."},
            {"role": "user", "content": "What is the weather like in Beijing today?"},
        ],
        tools=tools,
        stream=True, # <-- Enable streaming output
        stream_options={"include_usage": True}, # <-- Request the final usage chunk
    )

    usage = None
    finish_reason = None
    reasoning_content = "" # <-- The folded reasoning fragments (thinking models)
    tool_calls = []        # <-- The reconstructed tool calls, one entry per index

    for chunk in stream:
        chunk_usage = chunk.usage
        if chunk_usage is None and chunk.choices:
            chunk_usage = getattr(chunk.choices[0], "usage", None)
        if chunk_usage:
            usage = chunk_usage
        if not chunk.choices:
            continue

        choice = chunk.choices[0]
        delta = choice.delta

        if choice.finish_reason:
            finish_reason = choice.finish_reason

        # reasoning_content arrives before content and tool_calls; it is not declared in the SDK types, so read it with hasattr/getattr
        if hasattr(delta, "reasoning_content"):
            reasoning_fragment = getattr(delta, "reasoning_content")
            if reasoning_fragment:
                reasoning_content += reasoning_fragment # <-- Append, never overwrite
                print(reasoning_fragment, end="")

        if delta.content:
            print(delta.content, end="")

        for tool_call in delta.tool_calls or []:
            index = tool_call.index # <-- Fragments of the same tool call share the same index
            while len(tool_calls) <= index:
                tool_calls.append({"id": "", "type": "", "name": "", "arguments": ""})
            current = tool_calls[index]
            if tool_call.id: # <-- id, type and name arrive only in the first fragment
                current["id"] = tool_call.id
            if tool_call.type:
                current["type"] = tool_call.type
            if tool_call.function:
                if tool_call.function.name:
                    current["name"] = tool_call.function.name
                if tool_call.function.arguments:
                    current["arguments"] += tool_call.function.arguments # <-- Append, never overwrite

    # When finish_reason is "tool_calls", execute the tools, then append the assistant message
    # (with tool_calls and the folded reasoning_content, i.e. Preserved Thinking) plus the
    # tool results to messages, and call the API again
    if finish_reason == "tool_calls":
        for tool_call in tool_calls:
            arguments = json.loads(tool_call["arguments"]) # <-- Parse the JSON only after all fragments are folded
            print(f"\ntool_call: {tool_call['id']} {tool_call['name']}({arguments})")

    if usage:
        print("\ntotal_tokens:", usage.total_tokens)
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const OpenAI = require('openai')

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY, // Set the MOONSHOT_API_KEY environment variable before running this example
        baseURL: "https://api.moonshot.ai/v1",
    })

    const tools = [
        {
            type: "function",
            function: {
                name: "get_weather",
                description: "Get the current weather of a city.",
                parameters: {
                    type: "object",
                    required: ["city"],
                    properties: {
                        city: {
                            type: "string",
                            description: "The name of the city, e.g. Beijing",
                        },
                    },
                },
            },
        },
    ]

    async function main() {
        const stream = await client.chat.completions.create({
            model: "kimi-k3",
            messages: [
                {role: "system", content: "You are Kimi, an artificial intelligence assistant provided by Moonshot AI, who is better at conversing in Chinese and English. You provide users with safe, helpful, and accurate answers. At the same time, you refuse to answer any questions related to terrorism, racism, pornography, and violence. Moonshot AI is a proper noun and should not be translated into other languages."},
                {role: "user", content: "What is the weather like in Beijing today?"},
            ],
            tools: tools, // <-- Declare the tools the model may call
            stream: true, // <-- Enable streaming output
            stream_options: {include_usage: true}, // <-- Request the final usage chunk
        })

        let usage;
        let finishReason;
        let reasoningContent = ""; // <-- The folded reasoning fragments (thinking models)
        const toolCalls = [];      // <-- The reconstructed tool calls, one entry per index

        for await (const chunk of stream) {
            const chunkUsage = chunk.usage ?? chunk.choices[0]?.usage;
            if (chunkUsage) usage = chunkUsage;
            if (chunk.choices.length === 0) continue;

            const choice = chunk.choices[0];
            const delta = choice.delta;

            if (choice.finish_reason) finishReason = choice.finish_reason;

            // reasoning_content arrives before content and tool_calls; it is not declared in the SDK types, but is present on the parsed object
            if (delta.reasoning_content) {
                reasoningContent += delta.reasoning_content; // <-- Append, never overwrite
                process.stdout.write(delta.reasoning_content);
            }

            if (delta.content) {
                process.stdout.write(delta.content);
            }

            for (const toolCall of delta.tool_calls ?? []) {
                const index = toolCall.index; // <-- Fragments of the same tool call share the same index
                while (toolCalls.length <= index) {
                    toolCalls.push({id: "", type: "", name: "", arguments: ""});
                }
                const current = toolCalls[index];
                if (toolCall.id) current.id = toolCall.id; // <-- id, type and name arrive only in the first fragment
                if (toolCall.type) current.type = toolCall.type;
                if (toolCall.function) {
                    if (toolCall.function.name) current.name = toolCall.function.name;
                    if (toolCall.function.arguments) {
                        current.arguments += toolCall.function.arguments; // <-- Append, never overwrite
                    }
                }
            }
        }

        // When finish_reason is "tool_calls", execute the tools, then append the assistant message
        // (with tool_calls and the folded reasoning_content, i.e. Preserved Thinking) plus the
        // tool results to messages, and call the API again
        if (finishReason === "tool_calls") {
            for (const toolCall of toolCalls) {
                const args = JSON.parse(toolCall.arguments); // <-- Parse the JSON only after all fragments are folded
                console.log(`\ntool_call: ${toolCall.id} ${toolCall.name}(${JSON.stringify(args)})`);
            }
        }

        if (usage) console.log("\ntotal_tokens:", usage.total_tokens);
    }

    main()
    ```
  </Tab>
</Tabs>

When `finish_reason` is `tool_calls`, the model is asking you to execute tools. After executing them, append the assistant message (including its `tool_calls` and, for thinking models, the folded `reasoning_content` — see [Preserved Thinking](/docs/guide/use-thinking-models)) together with the tool results to `messages`, then call the API again; see [Use the Kimi API to Complete Tool Calls](/docs/guide/use-kimi-api-to-complete-tool-calls) for the full flow. `tool_call.type` matches the declared tool type (`function` or `builtin_function`).

## Parse the SSE Response Body

With streaming enabled, the API no longer returns a JSON response (`Content-Type: application/json`); it returns `Content-Type: text/event-stream` (SSE) instead, which lets the server continuously push Tokens to the client. An [SSE](https://kimi.ai/share/cr7boh3dqn37a5q9tds0) response body looks like this:

```text theme={null}
data: {"id":"cmpl-1305b94c570f447fbde3180560736287","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k3","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}
 
data: {"id":"cmpl-1305b94c570f447fbde3180560736287","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k3","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}
 
...
 
data: {"id":"cmpl-1305b94c570f447fbde3180560736287","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k3","choices":[{"index":0,"delta":{"content":"."},"finish_reason":null}]}
 
data: {"id":"cmpl-1305b94c570f447fbde3180560736287","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k3","choices":[{"index":0,"delta":{},"finish_reason":"stop","usage":{"prompt_tokens":19,"completion_tokens":13,"total_tokens":32}}]}

data: {"id":"cmpl-1305b94c570f447fbde3180560736287","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k3","choices":[],"usage":{"prompt_tokens":19,"completion_tokens":13,"total_tokens":32}}
 
data: [DONE]
```

In the response body, each data chunk starts with the `data: ` prefix, followed by a valid JSON object, and ends with two newline characters `\n\n`. Once all chunks are transmitted, the server sends `data: [DONE]` to mark completion, at which point you can close the connection.

*Note: always use `data: [DONE]` to determine whether the data has been fully transmitted, not `finish_reason` or any other means. If you have not received `data: [DONE]`, do not consider the transmission complete even if `finish_reason=stop` was received; in other words, until `data: [DONE]` arrives, the message should be considered **incomplete**.*

During streaming, the `content` field is delivered chunk by chunk; `role` is not repeated in every chunk and appears only in the first one. For thinking models, `reasoning_content` is likewise delivered as incremental fragments ahead of `content`; when the model decides to call tools, `delta.tool_calls` carries tool-call fragments — fragments of the same call share the same `index`, `id`/`type`/`function.name` appear only in the first fragment, and `function.arguments` arrives as JSON string fragments that must be appended before parsing. When you pass `stream_options: {"include_usage": true}`, the server sends a final statistics chunk before `[DONE]`. This chunk has an empty `choices` array, and the total usage for the request is in the top-level `usage` field.

## Count Token Usage

There are two ways to count tokens. We recommend passing `stream_options: {"include_usage": true}`, waiting until all chunks have been transmitted, and reading the top-level `usage` field of the final statistics chunk to see the request's `prompt_tokens`/`completion_tokens`/`total_tokens`:

```text theme={null}
...
 
data: {"id":"cmpl-1305b94c570f447fbde3180560736287","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k3","choices":[],"usage":{"prompt_tokens":19,"completion_tokens":13,"total_tokens":32}}
                                                                                                                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                                                                                                            Read the top-level usage field of the final statistics chunk
data: [DONE]
```

<Note>
  The final statistics chunk does not contain model output, so its `choices` array is empty. When parsing a stream, do not assume that every chunk has `choices[0]`; read the total usage from `chunk.usage` on the final statistics chunk.
</Note>

However, a stream can be interrupted by uncontrollable factors such as a network drop or a client-side error, in which case the last chunk never arrives and the request's token consumption cannot be determined. To avoid this, save the content of every chunk you receive and, once the request ends (whether successfully or not), call the token-count endpoint to compute the actual consumption:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    import httpx
    from openai import OpenAI
     
    client = OpenAI(
        api_key = os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url = "https://api.moonshot.ai/v1",
    )
     
    stream = client.chat.completions.create(
        model = "kimi-k3",
        messages = [
            {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI, who excels in Chinese and English conversations. You provide users with safe, helpful, and accurate answers while rejecting any questions related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated."},
            {"role": "user", "content": "Hello, my name is Li Lei. What is 1+1?"}
        ],
        stream=True, # <-- Note here, we enable streaming output mode by setting stream=True
    )


    def estimate_token_count(input: str) -> int:
        """
        Implement your token calculation logic here, or directly call our token calculation interface to compute tokens.

        https://api.moonshot.ai/v1/tokenizers/estimate-token-count
        """
        header = {
            "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
        }
        data = {
            "model": "kimi-k3",
            "messages": [
                {"role": "user", "content": input},
            ]
        }
        r = httpx.post("https://api.moonshot.ai/v1/tokenizers/estimate-token-count", headers=header, json=data)
        r.raise_for_status()
        return r.json()["data"]["total_tokens"]


    completion = []
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            completion.append(delta.content)


    print("completion_tokens:", estimate_token_count("".join(completion)))
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const axios = require('axios');
    const OpenAI = require('openai');
     
    client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: "https://api.moonshot.ai/v1",
    })
     
     
    async function estimate_token_count(input_messages) {
        /*
        Implement your token calculation logic here, or directly call our token calculation interface to compute tokens.
     
        https://api.moonshot.ai/v1/tokenizers/estimate-token-count
        */
        header = {
            "Authorization": `Bearer ${process.env.MOONSHOT_API_KEY}`,
        }
        data = {
            "model": "kimi-k3",
            "messages": input_messages,
        }
        r = await axios.post("https://api.moonshot.ai/v1/tokenizers/estimate-token-count", data, {headers: header})
        .catch(function (error) {
            console.log(error)
        })
        return r.data.data.total_tokens
    } 

    async function main() {

        const stream = await client.chat.completions.create({
            model: "kimi-k3",
            messages: [
                {role: "system", content: "You are Kimi, an AI assistant provided by Moonshot AI, who excels in Chinese and English conversations. You provide users with safe, helpful, and accurate answers while rejecting any questions related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated."},
                {role: "user", content: "Hello, my name is Li Lei. What is 1+1?"}
            ],
            stream: true, // <-- Note here, we enable streaming output mode by setting stream=True
        })
        
        const completion = [];
        for await (chunk of stream) {
            const delta = chunk.choices[0].delta
            if (delta.content) {
                completion.push(delta.content)
            }
        }
         
        console.log("completion_tokens:", await estimate_token_count(completion.join("")))
    }

    main()
    ```
  </Tab>
</Tabs>

## Stop Streaming Output

To terminate the output early, simply close the HTTP connection or discard subsequent chunks — for example, `break` out of the loop:

```python theme={null}
for chunk in stream:
	if condition:
		break
```

## Handle SSE Without an SDK

In a language without an SDK, or when the SDK cannot accommodate your business logic, you can interface with the HTTP API directly to handle streaming output. The following examples show how to read and parse the [SSE](https://kimi.ai/share/cr7boh3dqn37a5q9tds0) response body line by line; see the code comments for details:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    import json
    import httpx # We use the httpx library to make our HTTP requests


    request_data = {
        "model": "kimi-k3",
        "messages": [
            # Specific messages
        ],
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    headers = {
        "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
    }

    usage = None

    # Use httpx.stream to process SSE lines as they arrive instead of buffering the entire response
    with httpx.stream(
        "POST",
        "https://api.moonshot.ai/v1/chat/completions",
        headers=headers,
        json=request_data,
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if not line.startswith("data: "):
                continue

            payload = line.removeprefix("data: ")
            if payload == "[DONE]":
                break

            chunk = json.loads(payload)
            choices = chunk.get("choices", [])
            chunk_usage = chunk.get("usage")
            if chunk_usage is None and choices:
                chunk_usage = choices[0].get("usage")
            if chunk_usage:
                usage = chunk_usage
            if not choices:
                continue

            choice = choices[0]
            delta = choice["delta"]
            role = delta.get("role")
            if role:
                print("role:", role)
            content = delta.get("content")
            if content:
                print(content, end="")

    if usage:
        print("\ntotal_tokens:", usage["total_tokens"])
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const axios = require('axios'); // Use the axios library to make HTTP requests

    const requestData = {
        "model": "kimi-k3",
        "messages": [
            // Specific messages
        ],
        "stream": true,
        "stream_options": {"include_usage": true},
    };

    // Use axios to send a chat request to the Kimi large language model and get the response r
    axios.post("https://api.moonshot.ai/v1/chat/completions", requestData, {
        headers: {
            "Authorization": `Bearer ${process.env.MOONSHOT_API_KEY}`,
        },
        responseType: 'stream',
    }).then(response => {
        let buffer = '';
        let usage;
        response.data.on('data', rawChunk => {
            buffer += rawChunk.toString();
            const events = buffer.split(/\r?\n\r?\n/);
            buffer = events.pop() ?? '';

            for (const event of events) {
                const dataLines = event
                    .split(/\r?\n/)
                    .filter(line => line.startsWith('data: '))
                    .map(line => line.slice(6));
                if (dataLines.length === 0) continue;

                const payload = dataLines.join('\n');
                if (payload === '[DONE]') {
                    if (usage) console.log("\ntotal_tokens:", usage.total_tokens);
                    response.data.destroy();
                    return;
                }

                try {
                    const chunk = JSON.parse(payload);
                    // The processing logic here can be replaced with your business logic, printing is just to demonstrate the process
                    const choices = chunk.choices || [];
                    const chunkUsage = chunk.usage ?? choices[0]?.usage;
                    if (chunkUsage) usage = chunkUsage;
                    if (choices.length === 0) {
                        continue;
                    }
                    const choice = choices[0];
                    const delta = choice.delta;
                    const role = delta.role;
                    if (role) {
                        console.log("role:", role);
                    }
                    const content = delta.content;
                    if (content) {
                        process.stdout.write(content);
                    }
                } catch (error) {
                    console.error("Error parsing JSON:", error);
                }
            }
        });
    }).catch(error => {
        console.error("Error in request:", error);
    });
    ```
  </Tab>
</Tabs>

Whatever the language, the basic steps for handling streaming output are the same:

1. Send an HTTP request with the `stream` parameter set to `true` in the request body;
2. Check the `Content-Type` in the response `Headers` — `text/event-stream` means the response is a streaming output;
3. Read the response line by line and parse the data chunks (in JSON format), locating chunk boundaries via the `data: ` prefix and newline characters `\n`;
4. A chunk whose content is `[DONE]` marks the end of the transmission.

## Multiple Responses (`n` Parameter)

<Note>
  Current models (`kimi-k3`, `kimi-k2.7-code`, `kimi-k2.6`) fix `n` at `1` and do not support returning multiple responses in a single request. Passing an `n` greater than 1 returns a 400 error (`invalid n: only 1 is allowed for this model`) for both streaming and non-streaming requests. See the [Model Parameter Reference](/docs/api/models-overview) for per-model parameter constraints.
</Note>
