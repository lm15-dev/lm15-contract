> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Kimi K3 API Tool Calling Best Practices

> When your agent has a large tool inventory, combine dynamic loading, tool_choice, and reasoning effort in the tool-calling flow.

When your agent has access to dozens or hundreds of tools, don't put every tool definition into the request — they eat up context and make the model more likely to pick the wrong tool. This guide walks through a tool-orchestration setup on Kimi K3: retrieve candidate tools with a search tool first, then inject tool definitions into the conversation on demand.

## Declare a search tool, not all your tools

At the start of a conversation, declare only a single `search_tools` function — implemented by your backend — plus a small set of core tools you expect to use in every turn:

```json theme={null}
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_tools",
        "description": "Search available tools by keyword and return matching tool names and summaries",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "Search keyword, e.g. github or database"
            }
          },
          "required": ["query"]
        }
      }
    }
  ]
}
```

In the system prompt, advertise the domain tags the model can search (for example, a tool catalog or business domains) so it knows to call `search_tools` first when it needs a tool. No matter how large your total inventory is, each request then only carries a handful of tool declarations.

## Use tool\_choice to force first-turn retrieval

The model may choose not to call any tool and answer from memory. To make sure it retrieves before answering, set `tool_choice: "required"` on the first turn:

```json theme={null}
{
  "model": "kimi-k3",
  "messages": [{"role": "user", "content": "Help me create a GitHub PR"}],
  "tools": ["..."],
  "tool_choice": "required"
}
```

After retrieval, switch `tool_choice` back to `"auto"` for subsequent requests. Changing `tool_choice` does not invalidate the prefix cache, so you can adjust it per request. See [Tool Choice](/docs/guide/use-tool-choice) for all accepted values.

## Inject tool definitions on demand

When `search_tools` returns candidate tools, your application inserts the full declarations of the matching tools into `messages` via a `system` message carrying a `tools` field. The tools become visible to the model starting from that message's position:

```json theme={null}
{
  "role": "system",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "create_github_pr",
        "description": "Create a pull request in the given repository",
        "parameters": {
          "type": "object",
          "properties": {}
        }
      }
    }
  ]
}
```

Dynamic declarations use exactly the same format as the top-level `tools` field — no second schema to maintain — and coexist with globally declared tools. Dynamic tool declarations apply per request and are not retained by the server. In the next request, the client can keep the original declaration so the tool remains available and the prefix cache can be reused, or remove it. If the tool is not declared elsewhere, the model cannot call that tool, and the changed prefix may miss the cache. See [Dynamically Loaded Tools](/docs/guide/use-dynamic-tool-loading) for full usage.

<Note>
  A new request can hit the prefix cache only when the previous request's prompt tokens exceed 256. If the previous request's prompt tokens are below 256, the request is not cached and is discarded. See [Context Caching](/docs/guide/use-context-caching-feature-of-kimi-api) for details.
</Note>

## Pick the reasoning effort for the task

The top-level `reasoning_effort` request field supports `low`, `high`, and `max`, with `max` as the default.

Decide on this setting before the conversation starts. Appending a dynamic tool declaration to the end of `messages` does not affect the cached prefix; removing or modifying an earlier tool declaration may affect cache hits after the point of change. Changing `tool_choice` does not invalidate the prefix cache. See [Reasoning Effort](/docs/guide/use-reasoning-effort) for configuration details.

## The complete flow

1. Conversation start: top-level `tools` carries only `search_tools` plus a few core tools;
2. First-turn retrieval: `tool_choice: "required"` forces the model to call `search_tools`;
3. Inject on demand: insert tool definitions via a `system` message based on the retrieval results;
4. Call directly: the model calls the loaded tools in subsequent generations;
5. Reasoning effort: decide on the top-level `reasoning_effort` setting before the conversation starts.

## Related reading

* [Dynamically Loaded Tools](/docs/guide/use-dynamic-tool-loading)
* [Tool Choice](/docs/guide/use-tool-choice)
* [How to fix repeated tool calls](/docs/guide/tool-call-repeat)
* [Reasoning Effort](/docs/guide/use-reasoning-effort)
* [Use Kimi API for Tool Calls](/docs/guide/use-kimi-api-to-complete-tool-calls)
* [Model Parameter Reference](/docs/api/models-overview)
