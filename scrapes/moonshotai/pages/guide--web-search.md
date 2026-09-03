> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use Kimi API's Internet Search Functionality

> Add web search to Kimi API applications using the recommended official tool channel or the built-in `$web_search` flow for supported models.

<Note>
  When using web search with `kimi-k3`, we recommend the Formula API official tools channel (OpenAI protocol, standard `function` tool); see [How to Use Official Tools in Kimi API](/docs/guide/use-official-tools).
</Note>

`$web_search` (of type `builtin_function`) is Kimi's built-in web search tool function, implemented on top of the `tool_calls` usage: the model only generates the search arguments, while the search itself is defined and executed by the Kimi large language model. When you don't want to implement search-engine calls, page fetching, and content cleanup yourself, declare this built-in tool to get out-of-the-box web search.

Its basic usage and flow are the same as a regular `tool_calls` tool call — define the tool, submit it via `tools`, let the model generate the arguments, return the execution result, and get the model's reply. For the full flow, see [Use Kimi API to Complete Tool Calls](/docs/guide/use-kimi-api-to-complete-tool-calls); this page only highlights where `$web_search` differs from a regular `function`.

## Declare `$web_search`

Unlike an ordinary `tool`, the `$web_search` function does not require specific parameter descriptions — declaring only `type` and `function.name` in `tools` is enough to register it:

```python theme={null}
tools = [
	{
		"type": "builtin_function",  # <-- We use builtin_function to indicate Kimi built-in tools, which also distinguishes it from ordinary function
		"function": {
			"name": "$web_search",
		},
	},
]
```

**The `$web_search` function is prefixed with a dollar sign `$`, which is our agreed way to indicate Kimi built-in functions** (in ordinary `function` definitions, the dollar sign `$` is not allowed), and if there are other Kimi built-in functions in the future, they will also be prefixed with the dollar sign `$`.

**`$web_search` works directly with each model's reasoning behavior**: `kimi-k3` always reasons, and `kimi-k2.6` can also perform web search with thinking enabled.

`$web_search` can coexist with other ordinary `function` tools: within the same `tools` declaration, you can freely mix tools with `type=builtin_function` and `type=function`.

## Run the web search

When using the `$web_search` function, the basic flow is no different from that of a regular `function` — developers don't even need to modify the original code for executing `tool_calls`. The following example shows the complete flow: declare `$web_search`, ask a question, and loop over `tool_calls` until the model returns its final reply, where `search_impl` simply returns the model-generated arguments as-is:

<Note>
  The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
</Note>

<Tabs>
  <Tab title="python">
    ```python theme={null}
    from typing import *
     
    import os
    import json
     
    from openai import OpenAI
    from openai.types.chat.chat_completion import Choice
     
    client = OpenAI(
        base_url="https://api.moonshot.ai/v1",
        api_key=os.environ.get("MOONSHOT_API_KEY"),
    )
     
    # Specific implementation of the search tool, here we only need to return the arguments
    def search_impl(arguments: Dict[str, Any]) -> Any:
        """
        When using the search tool provided by Moonshot AI, you only need to return the arguments as-is,
        no additional processing logic is needed.

        But if you want to use other models and retain the web search functionality, you only need to modify the implementation here (e.g., calling search
        and getting web content, etc.), the function signature remains unchanged and still works.

        This maximizes compatibility, allowing you to switch between different models without needing destructive changes to the code.
        """
        return arguments
     
     
    def chat(messages) -> Choice:
        completion = client.chat.completions.create(
            model="kimi-k3",
            messages=messages,
            max_tokens=32768,
            tools=[
                {
                    "type": "builtin_function",  # <-- Use builtin_function to declare the $web_search function, please include the complete tools declaration in every request
                    "function": {
                        "name": "$web_search",
                    },
                }
            ]
        )
        return completion.choices[0]
     
     
    def main():
        messages = [
            {"role": "system", "content": "You are Kimi."},
        ]

        # Initial question
        messages.append({
            "role": "user",
            "content": "Please search for Moonshot AI Context Caching technology and tell me what it is."
        })
     
        finish_reason = None
        while finish_reason is None or finish_reason == "tool_calls":
            choice = chat(messages)
            finish_reason = choice.finish_reason
            if finish_reason == "tool_calls":  # <-- Determine whether the current returned content contains tool_calls
                messages.append(choice.message)  # <-- We also add the assistant message returned by the Kimi model to the context, so that the Kimi model can understand our request in the next request
                for tool_call in choice.message.tool_calls:  # <-- tool_calls may be multiple, so we use a loop to execute them one by one
                    tool_call_name = tool_call.function.name
                    tool_call_arguments = json.loads(tool_call.function.arguments)  # <-- arguments is a serialized JSON Object, we need to use json.loads to deserialize it
                    if tool_call_name == "$web_search":
                        tool_result = search_impl(tool_call_arguments)
                    else:
                        tool_result = f"Error: unable to find tool by name '{tool_call_name}'"

                    # Construct a role=tool message using the function execution result to show the model the tool call result;
                    # Note that we need to provide tool_call_id and name fields in the message so that the Kimi model
                    # can correctly match the corresponding tool_call.
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call_name,
                        "content": json.dumps(tool_result),  # <-- We agree to submit tool call results to the Kimi model in string format, so here we use json.dumps to serialize the execution result into a string
                    })

        print(choice.message.content)  # <-- Here, we return the reply generated by the model to the user
     
     
    if __name__ == '__main__':
        main()
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const openai = require('openai'); // Need to install openai library
     
    const client = new openai.OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: "https://api.moonshot.ai/v1",
    });
     
    const tools = [
        {
            "type": "builtin_function",
            "function": {
                "name": "$web_search",
            },
        }
    ];
     
    function search_impl(args) {
        return args
    }
     
    const messages = [
        { "role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are better at Chinese and English conversations. You will provide users with safe, helpful, and accurate answers. At the same time, you will refuse to answer any questions involving terrorism, racial discrimination, pornography, and violence. Moonshot AI is a proper noun and cannot be translated into other languages." },
        { "role": "user", "content": "Please search for the China A-share index on October 8, 2024?" }  // Ask Kimi model to search online in the question
    ];
     
    let finishReason = null;
     
    async function main() {
        while (finishReason === null || finishReason === "tool_calls") {
            const completion = await client.chat.completions.create({
                model: "kimi-k3",
                messages: messages,
                tools: tools  // <-- We submit the defined tools to the Kimi model through the tools parameter
            });
            const choice = completion.choices[0];
            console.log(choice);
            finishReason = choice.finish_reason;
            console.log(finishReason);
            if (finishReason === "tool_calls") { // <-- Check if the returned content contains tool_calls
                messages.push(choice.message); // <-- We add the assistant message returned by the Kimi model to the context so that the Kimi model can understand our request in the next request
                for (const toolCall of choice.message.tool_calls) { // <-- tool_calls may be multiple, so we use a loop to execute them one by one
                    const tool_call_name = toolCall.function.name;
                    const tool_call_arguments = JSON.parse(toolCall.function.arguments); // <-- arguments is a serialized JSON Object, we need to use JSON.parse to deserialize it
                    let tool_result;
                    if (tool_call_name == "$web_search") {
                      tool_result = search_impl(tool_call_arguments)
                    } else {
                      tool_result = 'no tool found'
                    }
     
     
                    // Construct a message with role=tool using the function execution result to show the model the tool call result;
                    // Note that we need to provide tool_call_id and name fields in the message so that the Kimi model
                    // can correctly match the corresponding tool_call.
                    console.log("toolCall.id");
                    console.log(toolCall.id);                
                    console.log("tool_call_name");
                    console.log(tool_call_name);
                    console.log("tool_result");
                    console.log(tool_result);                
                    messages.push({
                        "role": "tool",
                        "tool_call_id": toolCall.id,
                        "name": tool_call_name,
                        "content": JSON.stringify(tool_result), // <-- We agree to submit tool call results to the Kimi model in string format, so we use JSON.stringify to serialize the execution result into a string
                    });
                }
            }
            console.log(choice.message.content); // <-- Here, we return the model-generated reply to the user
        }
         
    }
     
    main();
    ```
  </Tab>
</Tabs>

Why doesn't `search_impl` need any logic for searching, parsing, or obtaining web content? As the name `builtin_function` suggests, `$web_search` is a built-in function of the Kimi large language model: it is defined by the Kimi large language model and executed by it as well.

1. When Kimi large language model generates a response with `finish_reason=tool_calls`, it means that Kimi large language model has realized that it needs to execute the `$web_search` function and has already prepared everything for it;
2. Kimi large language model will return the necessary parameters for executing the function in the form of `tool_call.function.arguments`. However, these parameters are not executed by the caller. The caller just needs to submit `tool_call.function.arguments` to Kimi large language model as they are, and Kimi large language model will execute the corresponding online search process;
3. When the user submits `tool_call.function.arguments` using a `message` with `role=tool`, Kimi large language model will immediately start the online search process and generate a readable message for the user based on the search and reading results, which is a `message` with `finish_reason=stop`;

## Switch to your own search implementation

The online search function provided by the Kimi API aims to offer a reliable large language model online search solution without breaking the compatibility of the original API and SDK, and it is fully compatible with the original `tool_calls` feature of the Kimi large language model. **If you want to switch from Kimi's online search function to your own implementation, you can do so in just two simple steps without disrupting the overall structure of your code:**

1. Modify the `tool` definition of `$web_search` to your own implementation (including `name`, `description` etc.). You may need to add additional information in `tool.function` to inform the model of the specific parameters it needs to generate. You can add any parameters you need in the `parameters` field;
2. Change the implementation of the `search_impl` function: when using Kimi's `$web_search`, you just need to return the input `arguments` as they are; if you use your own online search service, you may need to fully implement the `search` and `crawl` functions — call search engine APIs (or implement your own content search) to retrieve URLs and summaries, fetch web page content based on URLs (which might require different reading rules for different websites), clean and organize the fetched web page content into a format that the model can easily recognize, such as Markdown, and handle various errors and exceptions, such as no search results or failure to fetch web page content;

After completing the above steps, you will have successfully migrated from Kimi's online search function to your own implementation.

## Track web search token usage

When using the `$web_search` function provided by Kimi, the search results are also counted towards the tokens occupied by the prompt (i.e., `prompt_tokens`). Typically, since the results of web searches contain a lot of content, the token consumption can be quite high. To avoid unknowingly using up a large number of tokens, an extra `total_tokens` field is added under the `usage` object inside the generated `arguments` (read it as `arguments.usage.total_tokens`), informing the caller of the total number of tokens occupied by the search content. These tokens will be included in the `prompt_tokens` once the entire web search process is completed.

The following example shows how to read the `total_tokens` occupied by the search results, along with the token consumption of the whole conversation:

```python theme={null}
from typing import *
import os
import json
 
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
 
 
client = OpenAI(
    base_url="https://api.moonshot.ai/v1",
    api_key=os.environ.get("MOONSHOT_API_KEY"),
)
 
 
# Specific implementation of search tool, here we only need to return parameters
def search_impl(arguments: Dict[str, Any]) -> Any:
    """
    When using search tool provided by Moonshot AI, you only need to return arguments as is,
    without additional processing logic.
 
    But if you want to use other models and retain web search function, you only need to modify implementation here (such as calling search
    and getting web content, etc.), function signature remains same, still work.
 
    This maximizes compatibility, allowing you to switch between different models without breaking changes to code.
    """
    return arguments
 
 
def chat(messages) -> Choice:
    completion = client.chat.completions.create(
        model="kimi-k3",
        messages=messages,
        max_tokens=32768,
        tools=[
            {
                "type": "builtin_function",
                "function": {
                    "name": "$web_search",
                },
            }
        ]
    )
    usage = completion.usage
    choice = completion.choices[0]
 
    # =========================================================================
    # By judging finish_reason = stop, we print out the tokens consumed after completing the web search process
    if choice.finish_reason == "stop":
        print(f"chat_prompt_tokens:          {usage.prompt_tokens}")
        print(f"chat_completion_tokens:      {usage.completion_tokens}")
        print(f"chat_total_tokens:           {usage.total_tokens}")
    # =========================================================================
 
    return choice
 
 
def main():
    messages = [
        {"role": "system", "content": "You are Kimi."},
    ]
 
    # Initial question
    messages.append({
        "role": "user",
        "content": "Please search for Moonshot AI Context Caching technology and tell me what it is."
    })
 
    finish_reason = None
    while finish_reason is None or finish_reason == "tool_calls":
        choice = chat(messages)
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":
            # Append the complete assistant message, preserving reasoning_content and tool_calls unchanged.
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                tool_call_name = tool_call.function.name
                tool_call_arguments = json.loads(
                    tool_call.function.arguments)
                if tool_call_name == "$web_search":
 
    				# ===================================================================
                    # We print out the tokens generated by web search results during the web search process
                    search_content_total_tokens = tool_call_arguments.get("usage", {}).get("total_tokens")
                    print(f"search_content_total_tokens: {search_content_total_tokens}")
    				# ===================================================================
 
                    tool_result = search_impl(tool_call_arguments)
                else:
                    tool_result = f"Error: unable to find tool by name '{tool_call_name}'"
 
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result),
                })
 
    print(choice.message.content)
 
 
if __name__ == '__main__':
    main()
```

Running the above code yields the following output:

```shell theme={null}
search_content_total_tokens: 13046  # <-- This represents the number of tokens occupied by the web search results due to the web search action.
chat_prompt_tokens:          13212  # <-- This represents the number of input tokens, including the web search results.
chat_completion_tokens:      295    # <-- This represents the number of tokens generated by the Kimi large language model based on the web search results.
chat_total_tokens:           13507  # <-- This represents the total number of tokens consumed, including the web search process.

# The content generated by the Kimi large language model based on the web search results is omitted here.
```

## About Model Size Selection

Enabling web search significantly increases context length because search results are appended to the conversation. To avoid triggering `Input token length too long`, we recommend using `kimi-k3`, which has a 1M-token context window:

```python theme={null}
def chat(messages) -> Choice:
    completion = client.chat.completions.create(
        model="kimi-k3", 
        messages=messages,
        tools=[
            {
                "type": "builtin_function",  # <-- Use builtin_function to declare the $web_search function. Please include the full tools declaration in each request.
                "function": {
                    "name": "$web_search",
                },
            }
        ]
    )
    return completion.choices[0]
```

## Web search billing

In addition to token consumption, we also charge a call fee for each web search. For details, see [Pricing](/docs/pricing/tools).
