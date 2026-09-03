> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# How to Use Official Tools in Kimi API

> Review the official tools available on Kimi Open Platform and learn how to configure and call them through the Chat Completions API.

Kimi Open Platform offers a set of official tools that you can integrate into your own applications (all official tools are currently free for a limited time, except `web-search`, which is billed per call; when the tool load reaches capacity limits, temporary rate limiting measures may be applied). This page lists the available official tools and shows how to call and execute them through the Kimi API.

<Note>
  When using official tools such as web search with `kimi-k3`, use the Formula API official tools channel described on this page (OpenAI protocol, standard `function` tool); the example below has been verified with `kimi-k3`.
</Note>

## Choose an official tool to use

The following table lists the currently available official tools:

| Tool Name       | Tool Description                                                                                                                  |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `convert`       | Unit conversion tool, supporting length, mass, volume, temperature, area, time, energy, pressure, speed, and currency conversions |
| `web-search`    | Real-time information and internet search tool. For pricing and availability details, see [Web Search Price](/docs/pricing/tools)      |
| `rethink`       | Intelligent reasoning tool                                                                                                        |
| `random-choice` | Random selection tool                                                                                                             |
| `mew`           | Random cat meowing and blessing tool                                                                                              |
| `memory`        | Memory storage and retrieval system tool, supporting persistent storage of conversation history and user preferences              |
| `excel`         | Excel and CSV file analysis tool                                                                                                  |
| `date`          | Date and time processing tool                                                                                                     |
| `base64`        | Base64 encoding and decoding tool                                                                                                 |
| `fetch`         | URL content extraction Markdown formatting tool                                                                                   |
| `quickjs`       | Quick JS engine security execution JavaScript code tool                                                                           |
| `code-runner`   | Python code execution tool                                                                                                        |

## Full example: call the `web_search` official tool

The following Python example uses the `web-search` official tool to show the full call chain (it only depends on `requests`). You can also interactively experience the capabilities of Kimi models and tools in the [Kimi Development Workbench](https://platform.kimi.ai/playground).

Using official tools through the Formula API follows the standard `function` tool flow of the OpenAI protocol, in 4 steps:

1. `GET /v1/formulas/{uri}/tools` — fetch the tool declarations (`uri` such as `moonshot/web-search:latest`);
2. `POST /v1/chat/completions` — send the tool declarations; the model returns standard `function`-type `tool_calls`;
3. `POST /v1/formulas/{uri}/fibers` — execute exactly what `tool_calls` specifies (`name` + `arguments` passed through verbatim; this step produces the tool\_call billing);
4. `POST /v1/chat/completions` — send the assistant message (with `tool_calls`) and the `role: "tool"` results to get the final answer.

The example defaults to `moonshot/web-search:latest`; set `FORMULA_URI` to another official tool's formula URI to try it: `moonshot/convert:latest`, `moonshot/web-search:latest`, `moonshot/rethink:latest`, `moonshot/random-choice:latest`, `moonshot/mew:latest`, `moonshot/memory:latest`, `moonshot/excel:latest`, `moonshot/date:latest`, `moonshot/base64:latest`, `moonshot/fetch:latest`, `moonshot/quickjs:latest`, `moonshot/code-runner:latest`

<Note>
  The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
</Note>

```python theme={null}
import os

import requests

BASE_URL = "https://api.moonshot.ai/v1"
API_KEY = os.environ["MOONSHOT_API_KEY"]
FORMULA_URI = "moonshot/web-search:latest"


def call(method: str, path: str, body: dict | None = None) -> dict:
    resp = requests.request(
        method,
        BASE_URL + path,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=body,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


# 1. Fetch the tool declarations
tools = call("GET", f"/formulas/{FORMULA_URI}/tools")["tools"]

messages = [
    {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI."},
    {"role": "user", "content": "What is the latest news about Moonshot AI?"},
]

while True:
    # 2. Send the request with the tool declarations (include full tools in every request)
    resp = call("POST", "/chat/completions",
                {"model": "kimi-k3", "messages": messages, "tools": tools})
    message = resp["choices"][0]["message"]
    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        # No tool_calls: print the final answer
        print(message["content"])
        break

    # Keep the assistant message (with tool_calls) verbatim; later rounds must include it
    messages.append({k: v for k, v in message.items()
                     if k in ("role", "content", "tool_calls")})

    for tc in tool_calls:
        fn = tc["function"]
        # 3. Execute the fiber exactly as tool_calls specifies (arguments verbatim; billed here)
        fiber = call("POST", f"/formulas/{FORMULA_URI}/fibers",
                     {"name": fn["name"], "arguments": fn["arguments"]})
        ctx = fiber.get("context", {})
        result = ctx.get("output") or ctx.get("encrypted_output") or ""
        # 4. Return the result as a role=tool message; tool_call_id must match tool_calls[].id
        messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
```

You only need to install `requests` and set the `MOONSHOT_API_KEY` environment variable before running.

## Understand the Formula concept

Before calling official tools, you need to understand Formula: it is a lightweight script engine collection that transforms Python scripts into "instant computing power that can be triggered by AI with one click" — developers only need to focus on writing code, while the platform handles startup, scheduling, isolation, billing, and recycling.

Formulas are called through semantic URIs (such as `moonshot/web-search:latest`). Each formula contains a declaration (telling the AI what it can do) and an implementation (Python code), and the platform automatically handles all underlying details (startup, isolation, recycling, etc.), making tools easy to share and reuse in the community. You can experience and debug these tools in Kimi Playground, or call them through the API in your applications.

## Call a Formula directly to run a tool

A formula URI generally consists of 3 parts, for example `moonshot/web-search:latest`: `web-search` is its `name`; the namespace currently only supports `moonshot`; and `latest` is the default tag.

For example, to call web search, you can send an HTTP request like this:

```bash theme={null}
export FORMULA_URI="moonshot/web-search:latest"
export MOONSHOT_BASE_URL="https://api.moonshot.ai/v1"

curl -X POST ${MOONSHOT_BASE_URL}/formulas/${FORMULA_URI}/fibers \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $MOONSHOT_API_KEY" \
-d '{
  "name": "web_search",
  "arguments": "{\"query\": \"Please look up the latest news about Moonshot AI.\"}"
}'
```

`web-search` was set as protected when created, so its result appears in the `context.encrypted_output` field, in a format similar to `----MOONSHOT ENCRYPTED BEGIN----... ----MOONSHOT ENCRYPTED END----`; this content can be passed directly into the tool call.

## Integrate official tools with Chat Completions

As shown in [Is 3214567 a prime number? An example of Tool Calls](/docs/api/tool-use), when using official tools with Chat Completions, there are several key points you need to align between the Formula API and the model.

### Fetch the tool definition and append it to the `tools` field

Given a formula URI (for example `moonshot/web-search:latest`), append it directly to the URL to request the tool declarations:

```bash theme={null}
curl ${MOONSHOT_BASE_URL}/formulas/${FORMULA_URI}/tools \
    -H "Authorization: Bearer $MOONSHOT_API_KEY"
```

Sample output:

```json theme={null}
{
  "object": "list",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "web_search",
        "description": "Search the web for information",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "description": "What to search for",
              "type": "string"
            }
          },
          "required": [ "query" ]
        }
      }
    }
  ]
}
```

Take the `tools` field from the response (always an array of dicts) and append it to your request's `tools` list — the platform guarantees this list is API-compatible.

Note that:

* If `type=function`, you need to ensure `function.name` is unique within a single API request, otherwise the chat completion request will be considered invalid and immediately returned with a 400 error (`invalid_request_error`, with a message like `function name get_weather is duplicated`);
* If you use multiple formulas at the same time, you need to maintain your own `function.name` -> `formula_uri` mapping for future reference.

### Handle the tool call returned by the model

If the chat completion returns `finish_reason=tool_calls`, the model has triggered a tool call, and the response looks like this:

```json theme={null}
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "web_search:0",
            "type": "function",
            "function": {
              "name": "web_search",
              "arguments": "{\"query\": \"What is the RGB value of sky blue?\" }"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

From `choices[0].message.tool_calls[0].function.name` you can tell that `web_search` needs to be called, and the `formula_uri` corresponding to `web_search` is `moonshot/web-search:latest`. Copy `choices[0].message.tool_calls[0].function` from the response in full as the body, and send a request to `${MOONSHOT_BASE_URL}/formulas/${FORMULA_URI}/fibers`.

Note that although the `function.arguments` output by the model is valid JSON in content, it is still an encoded string in format — you don't need to escape it; just use it directly as the body of the call.

### Handle the Fiber result and continue the conversation

A Fiber is a "process snapshot" of a specific execution, containing logs, Tracing, and resource usage, which is convenient for debugging and auditing. The `status` of the POST result may be `succeeded` or various types of errors; when it succeeds, the result looks like this:

```json theme={null}
{
  "id": "fiber-f43p7sby7ny111houyq1",
  "object": "fiber",
  "created_at": 1753440997,
  "lambda_id": "lambda-f3w8y6qcoqgi11h8q7ui",
  "status": "succeeded",
  "context": {
    "input": "{\"name\":\"web_search\",\"arguments\":\"{\\\"query\\\": \\\"What is the RGB value of sky blue?\\\" }\"}",
    "encrypted_output": "----MOONSHOT ENCRYPTED BEGIN----+nf6...DSM=----MOONSHOT ENCRYPTED END----"
  },
  "formula": "moonshot/web-search:latest",
  "organization_id": "staff",
  "project_id": "proj-88a5894a985646b5902b70909748ba16"
}
```

Search tools may return `encrypted_output`, while in general the result is `output` — this output is your input for the next round. When continuing the request, arrange the messages as follows:

```javascript theme={null}
messages = [
  /* other messages */
  { /* the return content of the previous round of the model */
    "role": "assistant",
    "tool_calls": [
      {
        "id": "web_search:0",
        "type": "function",
        "function": {
          "name": "web_search",
          "arguments": "{\"query\": \"What is the RGB value of sky blue?\" }"
        }
      }
    ]
  },
  { /* the information you need to supplement */
    "role": "tool",
    "tool_call_id": "web_search:0",  /* note that the id here needs to be aligned with the id in the previous tool_calls[] */
    "content": "----MOONSHOT ENCRYPTED BEGIN----+nf6...DSM=----MOONSHOT ENCRYPTED END----"
  }
]
```

The model can then continue with further reasoning.

## Notes

* The model may return more than one `tool_calls`; you must return results for all `tool_calls` for the model to continue, otherwise the request will be considered invalid and rejected;
* If the assistant message has `tool_calls`, the next messages must be exactly the same `role=tool` messages as the `tool_calls`, and `tool_call_id` must be aligned one-to-one with the previous `tool_calls.id`:
  * If there are multiple `tool_calls`, the order is not sensitive;
  * The ids of the `tool_calls` output by the model are always unique, and the ids in the `role=tool` messages must also be aligned with them;
  * The uniqueness requirement is only local to the `tool_calls`-response in this round, not for the entire conversation or globally.
