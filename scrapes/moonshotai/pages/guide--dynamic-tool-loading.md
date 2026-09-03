> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Dynamically Loaded Tools

> Append tool definitions to Kimi conversations on demand to reduce token usage, improve tool selection, and preserve prefix caching.

When your application needs a large number of tools, declaring all of them up front in the top-level `tools` field of every request leads to **Tool Definition Bloat**: every request carries the descriptions and parameter schemas of all tools, driving up token usage, and the more candidate tools there are, the more likely the model picks the wrong tool or constructs invalid call arguments.

Dynamically Loaded Tools let you **inject tools on demand** during a conversation: start with only a few core tools, and insert additional tools into `messages` when the conversation actually needs them, which reduces token usage and improves tool-selection accuracy at the same time. Because tool declarations are only ever **appended** to the end of `messages`, the existing conversation prefix stays unchanged, so dynamic loading does not break the prefix cache you have already built up and can be combined with [Context Caching](/docs/guide/use-context-caching-feature-of-kimi-api) to further reduce cost and latency. For the reasoning behind this design (lazy loading, tool registry) and combined practices, see [Kimi K3 API Tool Calling Best Practices](/docs/guide/kimi-k3-tool-calling-best-practice).

<img src="https://mintcdn.com/moonshotai/shUqCColwVByinAO/assets/pics/dynamically-loaded-tools.jpg?fit=max&auto=format&n=shUqCColwVByinAO&q=85&s=a48a51647477d774f628a4516e299aa5" alt="Dynamically loaded tools at a glance: fetch only the tools you need, when you need them" width="1254" height="1254" data-path="assets/pics/dynamically-loaded-tools.jpg" />

## Inject tool declarations into messages

Insert a message with `role` set to `system` into `messages`, and declare the tools to load through that message's `tools` field. The declaration format is identical to the top-level `tools` field of the request, and must contain the **complete** tool definition (`name`, `description`, `parameters`):

```json theme={null}
{
  "messages": [
    {
      "role": "system",
      "content": "You are Kimi, an AI assistant developed by Moonshot AI.\nYou are capable of a wide range of tasks, including:\n📝 Q&A & Explanation – Answer all kinds of questions, ranging from scientific knowledge to daily life matters\n✍️ Writing Assistance – Draft essays, emails and reports, or polish your written text\n💻 Coding Support – Write and debug code, and explain technical concepts\n🔍 Analysis & Summarization – Process lengthy documents, extract key points and analyze data\n🌍 Translation – Support mutual translation between multiple languages\n💡 Brainstorming – Help you expand ideas and generate creative inspirations\nYou also accept extremely long context inputs, making you ideal for users who need analysis or summaries of lengthy documents."
    },
    {
      "role": "user",
      "content": "Calculate fuel consumption."
    },
    {
      "role": "system",
      "tools": [
        {
          "type": "function",
          "function": {
            "name": "Calculator",
            "description": "A calculator that evaluates a single arithmetic expression",
            "parameters": {
              "type": "object",
              "properties": {
                "expr": {
                  "type": "string",
                  "description": "An arithmetic expression in JavaScript syntax; supports basic arithmetic, exponentiation, logarithms, and trigonometric functions"
                }
              },
              "required": ["expr"]
            }
          }
        }
      ]
    }
  ]
}
```

A few things to know:

* A `system` message carrying `tools` has the **same standing as ordinary input messages**: the tools become visible to the model starting from the position where the message appears in the `messages` list;
* Dynamically loaded tools **coexist** with the global tools declared in the top-level `tools` field, and the model can see both;
* A dynamically injected tool declaration must be a **complete** tool definition; you cannot pass only a tool name or reference a tool already declared globally.

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
                    "role": "system",
                    "content": "You are Kimi, an AI assistant developed by Moonshot AI.\nYou are capable of a wide range of tasks, including:\n📝 Q&A & Explanation – Answer all kinds of questions, ranging from scientific knowledge to daily life matters\n✍️ Writing Assistance – Draft essays, emails and reports, or polish your written text\n💻 Coding Support – Write and debug code, and explain technical concepts\n🔍 Analysis & Summarization – Process lengthy documents, extract key points and analyze data\n🌍 Translation – Support mutual translation between multiple languages\n💡 Brainstorming – Help you expand ideas and generate creative inspirations\nYou also accept extremely long context inputs, making you ideal for users who need analysis or summaries of lengthy documents."
                },
                {
                    "role": "user",
                    "content": "Help me compute 23 * 47."
                },
                {
                    "role": "system",
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "Calculator",
                                "description": "A calculator that evaluates a single arithmetic expression",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "expr": {
                                            "type": "string",
                                            "description": "An arithmetic expression in JavaScript syntax; supports basic arithmetic, exponentiation, logarithms, and trigonometric functions"
                                        }
                                    },
                                    "required": ["expr"]
                                }
                            }
                        }
                    ]
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
        messages=[
            {"role": "system", "content": "You are Kimi, an AI assistant developed by Moonshot AI.\nYou are capable of a wide range of tasks, including:\n📝 Q&A & Explanation – Answer all kinds of questions, ranging from scientific knowledge to daily life matters\n✍️ Writing Assistance – Draft essays, emails and reports, or polish your written text\n💻 Coding Support – Write and debug code, and explain technical concepts\n🔍 Analysis & Summarization – Process lengthy documents, extract key points and analyze data\n🌍 Translation – Support mutual translation between multiple languages\n💡 Brainstorming – Help you expand ideas and generate creative inspirations\nYou also accept extremely long context inputs, making you ideal for users who need analysis or summaries of lengthy documents."},
            {"role": "user", "content": "Help me compute 23 * 47."},
            # Dynamically load tools: insert a system message carrying a tools field
            {
                "role": "system",
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "Calculator",
                            "description": "A calculator that evaluates a single arithmetic expression",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "expr": {
                                        "type": "string",
                                        "description": "An arithmetic expression in JavaScript syntax; supports basic arithmetic, exponentiation, logarithms, and trigonometric functions",
                                    }
                                },
                                "required": ["expr"],
                            },
                        },
                    }
                ],
            },
        ],
    )

    print(completion.choices[0].message.tool_calls)
    ```
  </Tab>
</Tabs>

## Implementing tool search with dynamic loading

There is no dedicated tool-search API. If you have a large tool inventory, you can implement tool search yourself by combining a **custom search tool with dynamically loaded tools**:

1. Declare only a single `search_tools` function in the top-level `tools` field, implemented by your backend, which returns matching tool names and summaries for a given keyword;
2. In the system prompt, advertise the searchable keywords (e.g. a tool catalog or domain tags) so the model knows to call `search_tools` first when it needs a tool;
3. Based on what `search_tools` returns, your application inserts the **full declarations** of the matching tools into `messages` via a `system` message carrying a `tools` field;
4. The model can then call these newly loaded tools in subsequent generations.

No matter how large the total tool inventory is, each request then only carries a handful of tool declarations, keeping both the context window and the model's selection pressure under control.

## Impact on context caching

Dynamically loaded tools can be combined with [Context Caching](/docs/guide/use-context-caching-feature-of-kimi-api). Context caching works by prefix matching: only the leading portion of the current request that is identical to a previous request can hit the cache, and any change within the prefix invalidates the cache from that point onward. How you inject tool declarations therefore directly determines your cache hit rate. Follow these principles to keep a high hit rate while loading tools on demand:

* **Append, never insert**: always append new tool declarations to the end of `messages`. The existing prefix stays unchanged and the established cache is unaffected. Inserting or modifying any message in the middle of the conversation (including an already injected tool declaration) invalidates the cache from that point onward;
* **Keep injected declarations**: dynamic tool declarations apply per request and are not retained by the server. We recommend carrying previously loaded declarations unchanged in subsequent requests, as this keeps the tools available and preserves a stable prefix for consistent cache hits; you may, however, adjust this behavior according to your business requirements. If a declaration is omitted, it ceases to apply, and the model cannot invoke that tool unless it is declared elsewhere. In addition, because `messages` has changed, the prefix following that point may no longer hit the cache;
* **Pin core tools at the top level and leave them unchanged**: declare the tools you need every turn as global tools in the top-level `tools` field, and keep them unchanged afterwards. Top-level global tool declarations do not affect cache hits, so keeping them stable preserves the effectiveness of the prefix cache. Use dynamic injection only for on-demand tools.

| Operation                                                                                         | Effect on the prefix cache                         |
| :------------------------------------------------------------------------------------------------ | :------------------------------------------------- |
| Appending a tool declaration at the end of `messages`                                             | Existing prefix cache unaffected                   |
| Carrying previously injected declarations unchanged                                               | Prefix remains stable, sustaining cache hits       |
| Deleting or modifying a message mid-conversation, or inserting a new declaration mid-conversation | Cache after the point of change may be invalidated |
| Declaring global tools in the top-level `tools` field                                             | Cache hits unaffected                              |

Note the threshold for caching to take effect: a new request can hit the prefix cache only when the previous request's prompt tokens exceed 256; below 256 tokens the request is not cached and is discarded. See [Context Caching](/docs/guide/use-context-caching-feature-of-kimi-api) for details.

## Notes

* Dynamic tool declarations use **exactly the same format** as global `tools` declarations, so you maintain a single schema and migration stays cheap;
* A `system` message carrying `tools` also consumes context length, so only inject the tools the current conversation genuinely needs;
* Dynamically loaded tools are currently supported only on `kimi-k3`; on other models (e.g. `kimi-k2.6`) the request fails with a `tokenization failed` error;
* A `system` message carrying `tools` must not also carry a `content` field, otherwise the request fails with a 400 error (`cannot be used with content`); with the OpenAI SDK you can pass the `tools` field through directly in `messages`, with no `extra_body` needed.

## Related reading

* [Kimi K3 API Tool Calling Best Practices](/docs/guide/kimi-k3-tool-calling-best-practice): combined practices for dynamic loading, tool\_choice, and reasoning effort
* [Tool Choice](/docs/guide/use-tool-choice): constrain the model's tool-calling behavior with `tool_choice`
* [Use Kimi API for Tool Calls](/docs/guide/use-kimi-api-to-complete-tool-calls): the complete tool-calling workflow and examples
* [Model Parameter Reference](/docs/api/models-overview): per-model support for parameters such as `tool_choice`
