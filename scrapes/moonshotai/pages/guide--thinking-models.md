> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Thinking Models

> Understand Kimi thinking modes, model selection, `reasoning_content`, multi-turn retention, tool calling, and reasoning-token billing.

Thinking models use reasoning tokens to "think" before producing a final answer — breaking down the problem, planning steps, and evaluating alternatives. The reasoning process is returned in the response's `reasoning_content` field. Thinking before answering improves performance on complex reasoning, code generation, and multi-step tool calling, at the cost of higher latency and token usage.

## Choose the right thinking model

This page covers the following thinking models:

* **`kimi-k3`**: the flagship thinking model; reasoning and Preserved Thinking are always on, and `reasoning_content` may be returned. Configure its reasoning effort with the top-level `reasoning_effort` request field, which supports `"low"` / `"high"` / `"max"` (default `"max"`).
* **`kimi-k2.7-code`**: code-focused; **thinking is always on**, and **Preserved Thinking is always on**. Its high-speed variant `kimi-k2.7-code-highspeed` is the same model with identical thinking behavior, and everything on this page applies to it as well.
* **`kimi-k2.6`**: the general-purpose thinking model; thinking is on by default, can be disabled, and **supports Preserved Thinking**.

The request parameters differ across these models:

| Request field      | `kimi-k3`                                      | `kimi-k2.7-code`                                                                                                                       | `kimi-k2.6`                                       |
| ------------------ | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `reasoning_effort` | `"low"` / `"high"` / `"max"` (default `"max"`) | Not supported                                                                                                                          | Not supported                                     |
| `thinking.type`    | —                                              | Only `"enabled"`; always thinks. Passing `"disabled"` errors                                                                           | `"enabled"` (default) / `"disabled"`              |
| `thinking.keep`    | —                                              | Omitting it or passing the valid value `"all"` is treated as `"all"` (always on, cannot be turned off); any other invalid value errors | `null` (default, not kept) / `"all"` (enables it) |

If you are doing benchmark testing with kimi api, please refer to this [benchmark best practice](/docs/guide/benchmark-best-practice).

## Basic calls

### Call kimi-k3

`kimi-k3` always reasons with Preserved Thinking always on; you do not need to (and should not) pass the `thinking` parameter — just set `model`, and optionally adjust [reasoning effort](/docs/guide/use-reasoning-effort) with the top-level `reasoning_effort` field:

<Tabs>
  <Tab title="curl">
    ```bash theme={null}
    $ curl https://api.moonshot.ai/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $MOONSHOT_API_KEY" \
        -d '{
            "model": "kimi-k3",
            "messages": [
                {
                    "role": "user",
                    "content": "Prove that the square root of 2 is irrational."
                }
            ]
        }'
    ```
  </Tab>

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
        messages=[{"role": "user", "content": "Prove that the square root of 2 is irrational."}],
    )

    message = completion.choices[0].message
    if hasattr(message, "reasoning_content"):
        print(getattr(message, "reasoning_content"))
    print(message.content)
    ```
  </Tab>
</Tabs>

For multi-turn conversations and tool calls, pass the complete assistant message returned by the API back to `messages` as-is (including `reasoning_content`); see [Preserved Thinking](#preserved-thinking). For more K3 usage, see the [Kimi K3 Quickstart](/docs/guide/kimi-k3-quickstart).

### Call kimi-k2.7-code: no thinking parameter needed

`kimi-k2.7-code` is a code-focused thinking model, sharing the same thinking mechanism as `kimi-k2.6` (`reasoning_content`, multi-step tool calls, streaming, etc.); the only difference is in the `thinking` parameter (see the comparison table above). You do not need to (and should not) pass the `thinking` parameter — just switch the `model`, and the model always emits `reasoning_content`. Because Preserved Thinking is always on, in multi-turn conversations you must keep the `reasoning_content` of every historical assistant message in `messages` as-is.

The example below makes a minimal streaming call and separates the reasoning content from the final answer in the output:

<Tabs>
  <Tab title="curl">
    ```bash theme={null}
    $ curl https://api.moonshot.ai/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $MOONSHOT_API_KEY" \
        -d '{
            "model": "kimi-k2.7-code",
            "messages": [
                {
                    "role": "system",
                    "content": "You are Kimi."
                },
                {
                    "role": "user",
                    "content": "Implement quicksort in Python."
                }
            ]
        }'
    ```
  </Tab>

  <Tab title="python">
    ```python theme={null}
    import os
    import openai

    client = openai.Client(
        base_url="https://api.moonshot.ai/v1",
        api_key=os.getenv("MOONSHOT_API_KEY"),
    )

    stream = client.chat.completions.create(
        model="kimi-k2.7-code",
        messages=[
            {
                "role": "system",
                "content": "You are Kimi.",
            },
            {
                "role": "user",
                "content": "Implement quicksort in Python."
            },
        ],
        max_tokens=1024*32,
        stream=True,
        # temperature is not modifiable and thinking is always on; neither needs to be set
    )

    thinking = False
    for chunk in stream:
        if chunk.choices:
            choice = chunk.choices[0]
            if choice.delta and hasattr(choice.delta, "reasoning_content"):
                if not thinking:
                    thinking = True
                    print("=============Start Reasoning=============")
                print(getattr(choice.delta, "reasoning_content"), end="")
            if choice.delta and choice.delta.content:
                if thinking:
                    thinking = False
                    print("\n=============End Reasoning=============")
                print(choice.delta.content, end="")
    ```
  </Tab>
</Tabs>

### Call kimi-k2.6: reasoning output by default

`kimi-k2.6` is the general-purpose thinking model. Thinking is enabled by default, so the basic call below outputs reasoning content without passing the `thinking` parameter (to disable thinking or enable Preserved Thinking, see [the thinking parameter](#thinking-parameter) below):

<Tabs>
  <Tab title="curl">
    ```bash theme={null}
    $ curl https://api.moonshot.ai/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $MOONSHOT_API_KEY" \
        -d '{
            "model": "kimi-k2.6",
            "messages": [
                {
                    "role": "system",
                    "content": "You are Kimi."
                },
                {
                    "role": "user",
                    "content": "Please explain why 1+1=2."
                }
            ]
        }'
    ```
  </Tab>

  <Tab title="python">
    ```python theme={null}
    import os
    import openai

    client = openai.Client(
        base_url="https://api.moonshot.ai/v1",
        api_key=os.getenv("MOONSHOT_API_KEY"),
    )

    stream = client.chat.completions.create(
        model="kimi-k2.6",
        messages=[
            {
                "role": "system",
                "content": "You are Kimi.",
            },
            {
                "role": "user",
                "content": "Please explain why 1+1=2."
            },
        ],
        max_tokens=1024*32,
        stream=True,
        # temperature is not modifiable, so no need to set it; thinking is enabled by default, no extra parameters needed
    )

    thinking = False
    for chunk in stream:
        if chunk.choices:
            choice = chunk.choices[0]
            if choice.delta and hasattr(choice.delta, "reasoning_content"):
                if not thinking:
                    thinking = True
                    print("=============Start Reasoning=============")
                print(getattr(choice.delta, "reasoning_content"), end="")
            if choice.delta and choice.delta.content:
                if thinking:
                    thinking = False
                    print("\n=============End Reasoning=============")
                print(choice.delta.content, end="")
    ```
  </Tab>
</Tabs>

## Control thinking behavior

### K3: adjust reasoning effort with `reasoning_effort`

`kimi-k3` always reasons and does not support the `thinking` parameter. Adjust reasoning effort with the top-level `reasoning_effort` field (`"low"` / `"high"` / `"max"`, default `"max"`); see [Reasoning Effort](/docs/guide/use-reasoning-effort) for usage and examples.

<span id="thinking-parameter" />

### Control kimi-k2.6 thinking with the thinking parameter

`kimi-k2.6` controls thinking behavior via the `thinking` parameter, which has two sub-fields:

* `thinking.type`: `"enabled"` (default) | `"disabled"` — controls whether thinking is on. Since it defaults to `"enabled"`, the example above thinks without passing it explicitly; for a disable example see [Disable Thinking Capability Example](/docs/guide/kimi-k2-6-quickstart#disable-thinking-capability-example).
* `thinking.keep`: `null` (default, ignores historical turns' thinking) | `"all"` (keeps previous turns' `reasoning_content`, enabling Preserved Thinking — see [Preserved Thinking](#preserved-thinking) for usage).

## Read reasoning\_content from the response

For thinking models such as `kimi-k2.7-code` and `kimi-k2.6` (with thinking enabled), the API response carries the model's reasoning in the `reasoning_content` field. When reading this field:

* In the OpenAI SDK, `ChoiceDelta` and `ChatCompletionMessage` types do not provide a `reasoning_content` field directly, so you cannot access it via `.reasoning_content`. You must use `hasattr(obj, "reasoning_content")` to check if the field exists, and if so, use `getattr(obj, "reasoning_content")` to retrieve its value.
* If you use other frameworks or directly interface with the HTTP API, you can directly obtain the `reasoning_content` field at the same level as the `content` field.
* In streaming output (`stream=True`), the `reasoning_content` field will always appear before the `content` field. In your business logic, you can detect if the `content` field has been output to determine if the reasoning (inference process) is finished.
* Tokens in `reasoning_content` are also controlled by the `max_tokens` parameter: the sum of tokens in `reasoning_content` and `content` must be less than or equal to `max_tokens`.

## Configure multi-step tool calls

`kimi-k2.7-code` and `kimi-k2.6` (with thinking enabled) are designed to perform deep reasoning across multiple tool calls, enabling them to tackle highly complex tasks. To get reliable results, **always follow these configuration rules when using thinking models:**

* Within a single task (the multi-step reasoning produced during one tool-call loop), keep all of the reasoning content from the context (the `reasoning_content` field) and send it back with the request; the model will choose which parts are necessary and forward them for reasoning. Whether historical thinking is preserved *across turns* is controlled by `thinking.keep` (`kimi-k2.6` defaults to `null` and does not keep it, while `kimi-k2.7-code` always keeps it).
* Set `max_tokens >= 16000` to ensure the full `reasoning_content` and `content` can be returned without truncation.
* **Do not set `temperature`.** For `kimi-k2.7-code` and `kimi-k2.6`, `temperature` is not modifiable — use the default and do not pass it explicitly (see [Model Parameter Reference](/docs/api/models-overview)).
* Enable streaming (`stream=True`). Because thinking models return both `reasoning_content` and regular `content`, the response is larger than usual. Streaming delivers a better user experience and helps avoid network-timeout issues.

### Complete example: generate a daily news report

The example below demonstrates a "Daily News Report Generation" scenario. The model will sequentially call official tools like `date` (to get the date) and `web_search` (to search today's news), and will present deep reasoning throughout this process:

```python expandable theme={null}
import os
import json
import httpx
import openai


class FormulaChatClient:
    def __init__(self, base_url: str, api_key: str):
        """Initialize Formula client"""
        self.base_url = base_url
        self.api_key = api_key
        self.openai = openai.Client(
            base_url=base_url,
            api_key=api_key,
        )
        self.httpx = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
        # Using kimi-k2.6 model. Thinking is enabled by default
        self.model = "kimi-k2.6"

    def get_tools(self, formula_uri: str):
        """Get tool definitions from Formula API"""
        response = self.httpx.get(f"/formulas/{formula_uri}/tools")
        response.raise_for_status()
        
        try:
            return response.json().get("tools", [])
        except json.JSONDecodeError as e:
            print(f"Error: Unable to parse JSON (status code: {response.status_code})")
            print(f"Response content: {response.text[:500]}")
            raise

    def call_tool(self, formula_uri: str, function: str, args: dict):
        """Call an official tool"""
        response = self.httpx.post(
            f"/formulas/{formula_uri}/fibers",
            json={"name": function, "arguments": json.dumps(args)},
        )
        response.raise_for_status()
        fiber = response.json()
        
        if fiber.get("status", "") == "succeeded":
            return fiber["context"].get("output") or fiber["context"].get("encrypted_output")
        
        if "error" in fiber:
            return f"Error: {fiber['error']}"
        if "error" in fiber.get("context", {}):
            return f"Error: {fiber['context']['error']}"
        return "Error: Unknown error"

    def close(self):
        """Close the client connection"""
        self.httpx.close()


# Initialize client
base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
api_key = os.getenv("MOONSHOT_API_KEY")

if not api_key:
    raise ValueError("MOONSHOT_API_KEY environment variable not set. Please set your API key.")

print(f"Base URL: {base_url}")
print(f"API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}\n")

client = FormulaChatClient(base_url, api_key)

# Define the official tool Formula URIs to use
formula_uris = [
    "moonshot/date:latest",
    "moonshot/web-search:latest"
]

# Load all tool definitions and build mapping
print("Loading official tools...")
all_tools = []
tool_to_uri = {}  # function.name -> formula_uri

for uri in formula_uris:
    try:
        tools = client.get_tools(uri)
        for tool in tools:
            func = tool.get("function")
            if func:
                func_name = func.get("name")
                if func_name:
                    tool_to_uri[func_name] = uri
                    all_tools.append(tool)
                    print(f"  Loaded tool: {func_name} from {uri}")
    except Exception as e:
        print(f"  Warning: Failed to load tool {uri}: {e}")
        continue

print(f"Loaded {len(all_tools)} tools in total\n")

if not all_tools:
    raise ValueError("No tools loaded. Please check API key and network connection.")

# Initialize message list
messages = [
    {
        "role": "system",
        "content": "You are Kimi, a professional news analyst. You excel at collecting, analyzing, and organizing information to generate high-quality news reports.",
    },
]

# User request to generate today's news report
user_request = "Please help me generate a daily news report including important technology, economy, and society news."
messages.append({
    "role": "user",
    "content": user_request
})

print(f"User request: {user_request}\n")

# Begin multi-step conversation loop
max_iterations = 10  # Prevent infinite loops
for iteration in range(max_iterations):
    try:
        completion = client.openai.chat.completions.create(
            model=client.model,
            messages=messages,
            max_tokens=1024 * 32,
            tools=all_tools,
        )
    except openai.AuthenticationError as e:
        print(f"Authentication error: {e}")
        print("Please check if the API key is correct and has the required permissions")
        raise
    except Exception as e:
        print(f"Error while calling the model: {e}")
        raise
    
    # Get response
    message = completion.choices[0].message
    
    # Print reasoning process
    if hasattr(message, "reasoning_content"):
        print(f"=============Reasoning round {iteration + 1} starts=============")
        reasoning = getattr(message, "reasoning_content")
        if reasoning:
            print(reasoning[:500] + "..." if len(reasoning) > 500 else reasoning)
        print(f"=============Reasoning round {iteration + 1} ends=============\n")
    
    # Add assistant message to context (preserve reasoning_content)
    messages.append(message)
    
    # If the model did not call any tools, conversation is done
    if not message.tool_calls:
        print("=============Final Answer=============")
        print(message.content)
        break
    
    # Handle tool calls
    print(f"The model decided to call {len(message.tool_calls)} tool(s):\n")
    
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        print(f"Calling tool: {func_name}")
        print(f"Arguments: {json.dumps(args, ensure_ascii=False, indent=2)}")
        
        # Get corresponding formula_uri
        formula_uri = tool_to_uri.get(func_name)
        if not formula_uri:
            print(f"Error: Could not find Formula URI for tool {func_name}")
            continue
        
        # Call the tool
        result = client.call_tool(formula_uri, func_name, args)
        
        # Print result (truncate if too long)
        if len(str(result)) > 200:
            print(f"Tool result: {str(result)[:200]}...\n")
        else:
            print(f"Tool result: {result}\n")
        
        # Add tool result to message list
        tool_message = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": func_name,
            "content": result
        }
        messages.append(tool_message)

print("\nConversation completed!")

# Cleanup
client.close()
```

This process demonstrates how thinking models such as `kimi-k2.7-code` and `kimi-k2.6` (with thinking enabled) use deep reasoning to plan and execute complex multi-step tasks, with detailed reasoning steps (`reasoning_content`) preserved in the context to ensure accurate tool use at every stage.

<span id="preserved-thinking" />

## Preserve thinking across turns (Preserved Thinking)

Preserved Thinking means passing the `reasoning_content` of previous turns through to the model in a multi-turn conversation, so that the model can continue its prior chain of thought when reasoning in the current turn.

For `kimi-k2.6`, use the `thinking.keep` parameter in the request body to control whether historical thinking is preserved:

| Value                      | Behavior                                                                        |
| -------------------------- | ------------------------------------------------------------------------------- |
| `null` / omitted (default) | Historical `reasoning_content` is ignored. Shorter context and lower cost.      |
| `"all"`                    | Historical `reasoning_content` is fully preserved, enabling Preserved Thinking. |

<Note>
  `thinking.keep` only affects `reasoning_content` from historical turns; it does **not** change whether the model generates/outputs thinking content within the current turn (that is controlled by `thinking.type`). Recommended to use `keep: "all"` together with `type: "enabled"`.

  For `kimi-k2.7-code`, Preserved Thinking is always on and cannot be turned off: `thinking.keep` is treated as `"all"` whether you omit it or pass the only valid value `"all"` (passing any other invalid value returns an error). When using this model you must therefore (not optionally) keep the `reasoning_content` of historical assistant messages in `messages` as-is, exactly as shown in the example below.
</Note>

When using `keep: "all"`, keep the `reasoning_content` from every historical assistant message in `messages` as-is. The simplest way is to append the assistant message returned from the previous API call directly back into `messages`, as shown below:

<Tabs>
  <Tab title="curl">
    ```bash theme={null}
    $ curl https://api.moonshot.ai/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $MOONSHOT_API_KEY" \
        -d '{
            "model": "kimi-k2.6",
            "messages": [
                {"role": "system", "content": "You are Kimi."},
                {"role": "user", "content": "First question..."},
                {
                    "role": "assistant",
                    "reasoning_content": "<reasoning_content returned by the previous API call>",
                    "content": "<final answer returned by the previous API call>"
                },
                {"role": "user", "content": "Please continue the analysis and derive the next step."}
            ],
            "thinking": {
                "type": "enabled",
                "keep": "all"
            }
        }'
    ```
  </Tab>

  <Tab title="python">
    ```python theme={null}
    import os
    import openai

    client = openai.Client(
        base_url="https://api.moonshot.ai/v1",
        api_key=os.getenv("MOONSHOT_API_KEY"),
    )

    # Keep the assistant message (including reasoning_content) from every previous API call in messages
    messages = [
        {"role": "system", "content": "You are Kimi."},
        {"role": "user", "content": "First question..."},
        {
            "role": "assistant",
            "reasoning_content": "<reasoning_content returned by the previous API call>",
            "content": "<final answer returned by the previous API call>",
        },
        {"role": "user", "content": "Please continue the analysis and derive the next step."},
    ]

    response = client.chat.completions.create(
        model="kimi-k2.6",
        messages=messages,
        stream=True,
        extra_body={"thinking": {"type": "enabled", "keep": "all"}},
    )
    ```
  </Tab>
</Tabs>

<Warning>
  `reasoning_content` counts toward token consumption. When Preserved Thinking is enabled, historical thinking content keeps occupying the context window and is billed accordingly. Use it wisely.
</Warning>

## Frequently Asked Questions

### Q1: Why should I keep `reasoning_content`?

A: Keeping `reasoning_content` ensures continuity in multi-step reasoning, especially during tool calls. Pass the complete assistant message returned by the API back in `messages` as-is. For K3, this is required in multi-turn conversations and tool-call loops. For K2.x, cross-turn preservation follows each model's `thinking.keep` behavior: `kimi-k2.6` does not preserve it by default, while `kimi-k2.7-code` always does.

### Q2: Does `reasoning_content` consume extra tokens?

A: Yes, `reasoning_content` counts towards your input/output token quota. For detailed pricing, see [Pricing](/docs/pricing/chat).
