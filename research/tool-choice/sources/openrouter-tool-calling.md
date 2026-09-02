> ## Documentation Index
> Fetch the complete documentation index at: https://openrouter.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Client Tools

> Use client tools in your prompts

export const Template = ({children, data}) => {
  const replace = s => s.replace(/\{\{(\w+)\}\}/g, (_, k) => (k in data) ? data[k] : `{{${k}}}`);
  const leafText = node => typeof node === 'string' ? node : node?.$$typeof && typeof node.props?.children === 'string' ? node.props.children : null;
  const collapseTokens = nodes => {
    const out = [];
    let i = 0;
    while (i < nodes.length) {
      const ta = leafText(nodes[i]);
      const tb = leafText(nodes[i + 1]);
      const tc = leafText(nodes[i + 2]);
      if (ta != null && tb != null && tc != null) {
        const m = (ta + tb + tc).match(/^([\s\S]*)\{\{(\w+)\}\}([\s\S]*)$/);
        if (m && (m[2] in data)) {
          out.push(m[1] + data[m[2]] + m[3]);
          i += 3;
          continue;
        }
      }
      out.push(nodes[i]);
      i++;
    }
    return out;
  };
  const process = node => {
    if (typeof node === 'string') return replace(node);
    if (Array.isArray(node)) return collapseTokens(node.map(process));
    if (node && typeof node === 'object') {
      if (node.$$typeof) return {
        ...node,
        props: process(node.props)
      };
      return Object.fromEntries(Object.entries(node).map(([k, v]) => [k, process(v)]));
    }
    return node;
  };
  return <>{process(children)}</>;
};

export const Model = {
  GPT_4_Omni: 'openai/gpt-4o'
};

export const API_KEY_REF = '<OPENROUTER_API_KEY>';

Tool calls (also known as function calls) give an LLM access to external tools. The LLM does not call the tools directly. Instead, it suggests the tool to call. The user then calls the tool separately and provides the results back to the LLM. Finally, the LLM formats the response into an answer to the user's original question.

OpenRouter standardizes the tool calling interface across models and providers, making it easy to integrate external tools with any supported model.

**Supported Models**: You can find models that support tool calling by filtering on [openrouter.ai/models?supported\_parameters=tools](https://openrouter.ai/models?supported_parameters=tools).

If you prefer to learn from a full end-to-end example, keep reading.

## Request Body Examples

Tool calling with OpenRouter involves three key steps. Here are the essential request body formats for each step:

### Step 1: Inference Request with Tools

```json expandable lines theme={null}
{
  "model": "google/gemini-3-flash-preview",
  "messages": [
    {
      "role": "user",
      "content": "What are the titles of some James Joyce books?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_gutenberg_books",
        "description": "Search for books in the Project Gutenberg library",
        "parameters": {
          "type": "object",
          "properties": {
            "search_terms": {
              "type": "array",
              "items": {"type": "string"},
              "description": "List of search terms to find books"
            }
          },
          "required": ["search_terms"]
        }
      }
    }
  ]
}
```

### Step 2: Tool Execution (Client-Side)

After receiving the model's response with `tool_calls`, execute the requested tool locally and prepare the result:

```javascript lines theme={null}
// Model responds with tool_calls, you execute the tool locally
const toolResult = await searchGutenbergBooks(["James", "Joyce"]);
```

### Step 3: Inference Request with Tool Results

```json expandable lines theme={null}
{
  "model": "google/gemini-3-flash-preview",
  "messages": [
    {
      "role": "user",
      "content": "What are the titles of some James Joyce books?"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_abc123",
          "type": "function",
          "function": {
            "name": "search_gutenberg_books",
            "arguments": "{\"search_terms\": [\"James\", \"Joyce\"]}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_abc123",
      "content": "[{\"id\": 4300, \"title\": \"Ulysses\", \"authors\": [{\"name\": \"Joyce, James\"}]}]"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_gutenberg_books",
        "description": "Search for books in the Project Gutenberg library",
        "parameters": {
          "type": "object",
          "properties": {
            "search_terms": {
              "type": "array",
              "items": {"type": "string"},
              "description": "List of search terms to find books"
            }
          },
          "required": ["search_terms"]
        }
      }
    }
  ]
}
```

**Note**: The `tools` parameter must be included in every request (Steps 1 and 3) so the router can validate the tool schema on each call.

### Tool Calling Example

Here is an end-to-end example that gives LLMs the ability to call an external API -- in this case Project Gutenberg, to search for books.

First, let's do some basic setup:

<Template
  data={{
API_KEY_REF,
MODEL: 'google/gemini-3-flash-preview'
}}
>
  <CodeGroup>
    ```typescript title="TypeScript SDK" expandable lines theme={null}
    import type { ChatFunctionTool, ChatMessages, ChatResult, ChatToolCall } from '@openrouter/sdk/models';
    import { OpenRouter } from '@openrouter/sdk';

    const OPENROUTER_API_KEY = "{{API_KEY_REF}}";

    // You can use any model that supports tool calling
    const MODEL = "{{MODEL}}";

    const openRouter = new OpenRouter({
      apiKey: OPENROUTER_API_KEY,
    });

    const task = "What are the titles of some James Joyce books?";

    const messages: ChatMessages[] = [
      {
        role: "system",
        content: "You are a helpful assistant."
      },
      {
        role: "user",
        content: task,
      }
    ];
    ```

    ```python Python expandable lines theme={null}
    import json, requests
    from openai import OpenAI

    OPENROUTER_API_KEY = f"{{API_KEY_REF}}"

    # You can use any model that supports tool calling
    MODEL = "{{MODEL}}"

    openai_client = OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=OPENROUTER_API_KEY,
    )

    task = "What are the titles of some James Joyce books?"

    messages = [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": task,
      }
    ]

    ```

    ```typescript title="TypeScript (fetch)" lines theme={null}
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer {{API_KEY_REF}}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: '{{MODEL}}',
        messages: [
          { role: 'system', content: 'You are a helpful assistant.' },
          {
            role: 'user',
            content: 'What are the titles of some James Joyce books?',
          },
        ],
      }),
    });
    ```
  </CodeGroup>
</Template>

### Define the Tool

Next, we define the tool that we want to call. Remember, the tool is going to get *requested* by the LLM, but the code we are writing here is ultimately responsible for executing the call and returning the results to the LLM.

<Template
  data={{
API_KEY_REF,
MODEL: 'google/gemini-3-flash-preview'
}}
>
  <CodeGroup>
    ```typescript title="TypeScript SDK" expandable lines theme={null}
    type Book = {
      id: number;
      title: string;
      authors: { name: string }[];
    };

    async function searchGutenbergBooks(searchTerms: string[]): Promise<Book[]> {
      const searchQuery = searchTerms.join(' ');
      const url = 'https://gutendex.com/books';
      const response = await fetch(`${url}?search=${searchQuery}`);
      const data: unknown = await response.json();

      if (!isGutenbergResponse(data)) {
        throw new Error('Invalid response from the Gutenberg API');
      }

      return data.results.map((book) => ({
        id: book.id,
        title: book.title,
        authors: book.authors.map((author) => ({ name: author.name })),
      }));
    }

    const tools: ChatFunctionTool[] = [
      {
        type: 'function',
        function: {
          name: 'searchGutenbergBooks',
          description:
            'Search for books in the Project Gutenberg library based on specified search terms',
          parameters: {
            type: 'object',
            properties: {
              search_terms: {
                type: 'array',
                items: {
                  type: 'string',
                },
                description:
                  "List of search terms to find books in the Gutenberg library (e.g. ['dickens', 'great'] to search for books by Dickens with 'great' in the title)",
              },
            },
            required: ['search_terms'],
          },
        },
      },
    ];

    function parseSearchTerms(argumentsJson: string): string[] {
      const args: unknown = JSON.parse(argumentsJson);

      if (
        !isRecord(args) ||
        !isStringArray(args.search_terms)
      ) {
        throw new Error('Invalid arguments for searchGutenbergBooks');
      }

      return args.search_terms;
    }

    function isGutenbergResponse(value: unknown): value is { results: Book[] } {
      return isRecord(value) && Array.isArray(value.results) && value.results.every(isBook);
    }

    function isBook(value: unknown): value is Book {
      return (
        isRecord(value) &&
        typeof value.id === 'number' &&
        typeof value.title === 'string' &&
        Array.isArray(value.authors) &&
        value.authors.every(isBookAuthor)
      );
    }

    function isBookAuthor(value: unknown): value is { name: string } {
      return isRecord(value) && typeof value.name === 'string';
    }

    function isStringArray(value: unknown): value is string[] {
      return Array.isArray(value) && value.every((item: unknown) => typeof item === 'string');
    }

    function isRecord(value: unknown): value is Record<string, unknown> {
      return typeof value === 'object' && value !== null;
    }
    ```

    ```python Python expandable lines theme={null}
    def search_gutenberg_books(search_terms):
        search_query = " ".join(search_terms)
        url = "https://gutendex.com/books"
        response = requests.get(url, params={"search": search_query})

        simplified_results = []
        for book in response.json().get("results", []):
            simplified_results.append({
                "id": book.get("id"),
                "title": book.get("title"),
                "authors": book.get("authors")
            })

        return simplified_results

    tools = [
      {
        "type": "function",
        "function": {
          "name": "search_gutenberg_books",
          "description": "Search for books in the Project Gutenberg library based on specified search terms",
          "parameters": {
            "type": "object",
            "properties": {
              "search_terms": {
                "type": "array",
                "items": {
                  "type": "string"
                },
                "description": "List of search terms to find books in the Gutenberg library (e.g. ['dickens', 'great'] to search for books by Dickens with 'great' in the title)"
              }
            },
            "required": ["search_terms"]
          }
        }
      }
    ]

    TOOL_MAPPING = {
        "search_gutenberg_books": search_gutenberg_books
    }

    ```
  </CodeGroup>
</Template>

Note that the "tool" is just a normal function. We then write a JSON "spec" compatible with the OpenAI function calling parameter. We'll pass that spec to the LLM so that it knows this tool is available and how to use it. It will request the tool when needed, along with any arguments. We'll then marshal the tool call locally, make the function call, and return the results to the LLM.

### Tool use and tool results

Let's make the first OpenRouter API call to the model:

<Template
  data={{
API_KEY_REF,
MODEL: 'google/gemini-3-flash-preview'
}}
>
  <CodeGroup>
    ```typescript title="TypeScript SDK" lines theme={null}
    const result = await openRouter.chat.send({
      chatRequest: {
        model: '{{MODEL}}',
        tools,
        messages,
        stream: false,
      },
    });

    if (result instanceof ReadableStream) {
      throw new Error('Expected a non-streaming response');
    }

    const firstChoice = result.choices[0];

    if (!firstChoice) {
      throw new Error('Expected the model to return a choice');
    }

    const response_1 = firstChoice.message;
    ```

    ```python Python lines theme={null}
    request_1 = {
        "model": {{MODEL}},
        "tools": tools,
        "messages": messages
    }

    response_1 = openai_client.chat.completions.create(**request_1).choices[0].message
    ```

    ```typescript title="TypeScript (fetch)" lines theme={null}
    const request_1 = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer {{API_KEY_REF}}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: '{{MODEL}}',
        tools,
        messages,
      }),
    });

    const data = await request_1.json();
    const response_1 = data.choices[0].message;
    ```
  </CodeGroup>
</Template>

The LLM responds with a finish reason of `tool_calls`, and a `tool_calls` array. In a generic LLM response-handler, you would want to check the `finish_reason` before processing tool calls, but here we will assume it's the case. Let's keep going, by processing the tool call:

<Template
  data={{
API_KEY_REF,
MODEL: 'google/gemini-3-flash-preview'
}}
>
  <CodeGroup>
    ```typescript title="TypeScript SDK" lines theme={null}
    // Append the response to the messages array so the LLM has the full context
    // It's easy to forget this step!
    messages.push(response_1);

    // Now we process the requested tool calls, and use our book lookup tool
    if (!response_1.toolCalls || response_1.toolCalls.length === 0) {
      throw new Error('Expected the model to request a tool call');
    }

    for (const toolCall of response_1.toolCalls) {
      if (toolCall.function.name !== 'searchGutenbergBooks') {
        throw new Error(`Unknown tool: ${toolCall.function.name}`);
      }

      const searchTerms = parseSearchTerms(toolCall.function.arguments);
      const toolResponse = await searchGutenbergBooks(searchTerms);
      messages.push({
        role: 'tool',
        toolCallId: toolCall.id,
        content: JSON.stringify(toolResponse),
      });
    }
    ```

    ```python Python lines theme={null}
    # Append the response to the messages array so the LLM has the full context
    # It's easy to forget this step!
    messages.append(response_1)

    # Now we process the requested tool calls, and use our book lookup tool
    for tool_call in response_1.tool_calls:
        '''
        In this case we only provided one tool, so we know what function to call.
        When providing multiple tools, you can inspect `tool_call.function.name`
        to figure out what function you need to call locally.
        '''
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        tool_response = TOOL_MAPPING[tool_name](**tool_args)
        messages.append({
          "role": "tool",
          "tool_call_id": tool_call.id,
          "content": json.dumps(tool_response),
        })
    ```
  </CodeGroup>
</Template>

The messages array now has:

1. Our original request
2. The LLM's response (containing a tool call request)
3. The result of the tool call (a json object returned from the Project Gutenberg API)

Now, we can make a second OpenRouter API call, and hopefully get our result!

<Template
  data={{
API_KEY_REF,
MODEL: 'google/gemini-3-flash-preview'
}}
>
  <CodeGroup>
    ```typescript title="TypeScript SDK" lines theme={null}
    const response_2 = await openRouter.chat.send({
      chatRequest: {
        model: '{{MODEL}}',
        messages,
        tools,
        stream: false,
      },
    });

    if (response_2 instanceof ReadableStream) {
      throw new Error('Expected a non-streaming response');
    }

    const finalChoice = response_2.choices[0];

    if (!finalChoice) {
      throw new Error('Expected the model to return a choice');
    }

    console.log(finalChoice.message.content);
    ```

    ```python Python lines theme={null}
    request_2 = {
      "model": MODEL,
      "messages": messages,
      "tools": tools
    }

    response_2 = openai_client.chat.completions.create(**request_2)

    print(response_2.choices[0].message.content)
    ```

    ```typescript title="TypeScript (fetch)" lines theme={null}
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer {{API_KEY_REF}}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: '{{MODEL}}',
        messages,
        tools,
      }),
    });

    const data = await response.json();
    console.log(data.choices[0].message.content);
    ```
  </CodeGroup>
</Template>

The output will be something like:

```text lines theme={null}
Here are some books by James Joyce:

*   *Ulysses*
*   *Dubliners*
*   *A Portrait of the Artist as a Young Man*
*   *Chamber Music*
*   *Exiles: A Play in Three Acts*
```

We did it! We've successfully used a tool in a prompt.

## Interleaved Thinking

Interleaved thinking allows models to reason between tool calls, enabling more sophisticated decision-making after receiving tool results. This feature helps models chain multiple tool calls with reasoning steps in between and make nuanced decisions based on intermediate results.

**Important**: Interleaved thinking increases token usage and response latency. Consider your budget and performance requirements when enabling this feature.

### How Interleaved Thinking Works

With interleaved thinking, the model can:

* Reason about the results of a tool call before deciding what to do next
* Chain multiple tool calls with reasoning steps in between
* Make more nuanced decisions based on intermediate results
* Provide transparent reasoning for its tool selection process

### Example: Multi-Step Research with Reasoning

Here's an example showing how a model might use interleaved thinking to research a topic across multiple sources:

**Initial Request:**

```json expandable lines theme={null}
{
  "model": "anthropic/claude-sonnet-4.5",
  "messages": [
    {
      "role": "user",
      "content": "Research the environmental impact of electric vehicles and provide a comprehensive analysis."
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_academic_papers",
        "description": "Search for academic papers on a given topic",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {"type": "string"},
            "field": {"type": "string"}
          },
          "required": ["query"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_latest_statistics",
        "description": "Get latest statistics on a topic",
        "parameters": {
          "type": "object",
          "properties": {
            "topic": {"type": "string"},
            "year": {"type": "integer"}
          },
          "required": ["topic"]
        }
      }
    }
  ]
}
```

**Model's Reasoning and Tool Calls:**

1. **Initial Thinking**: "I need to research electric vehicle environmental impact. Let me start with academic papers to get peer-reviewed research."

2. **First Tool Call**: `search_academic_papers({"query": "electric vehicle lifecycle environmental impact", "field": "environmental science"})`

3. **After First Tool Result**: "The papers show mixed results on manufacturing impact. I need current statistics to complement this academic research."

4. **Second Tool Call**: `get_latest_statistics({"topic": "electric vehicle carbon footprint", "year": 2024})`

5. **After Second Tool Result**: "Now I have both academic research and current data. Let me search for manufacturing-specific studies to address the gaps I found."

6. **Third Tool Call**: `search_academic_papers({"query": "electric vehicle battery manufacturing environmental cost", "field": "materials science"})`

7. **Final Analysis**: Synthesizes all gathered information into a comprehensive response.

### Best Practices for Interleaved Thinking

* **Clear Tool Descriptions**: Provide detailed descriptions so the model can reason about when to use each tool
* **Structured Parameters**: Use well-defined parameter schemas to help the model make precise tool calls
* **Context Preservation**: Maintain conversation context across multiple tool interactions
* **Error Handling**: Design tools to provide meaningful error messages that help the model adjust its approach

### Implementation Considerations

When implementing interleaved thinking:

* Models may take longer to respond due to additional reasoning steps
* Token usage will be higher due to the reasoning process
* The quality of reasoning depends on the model's capabilities
* Some models may be better suited for this approach than others

## A Simple Agentic Loop

In the example above, the calls are made explicitly and sequentially. To handle a wide variety of user inputs and tool calls, you can use an agentic loop.

Here's an example of a simple agentic loop (using the same `tools` and initial `messages` as above):

<Template
  data={{
API_KEY_REF,
MODEL: 'google/gemini-3-flash-preview'
}}
>
  <CodeGroup>
    ```typescript title="TypeScript SDK" expandable lines theme={null}
    async function callLLM(messages: ChatMessages[]): Promise<ChatResult> {
      const result = await openRouter.chat.send({
        chatRequest: {
          model: '{{MODEL}}',
          tools,
          messages,
          stream: false,
        },
      });

      if (result instanceof ReadableStream) {
        throw new Error('Expected a non-streaming response');
      }

      const choice = result.choices[0];

      if (!choice) {
        throw new Error('Expected the model to return a choice');
      }

      messages.push(choice.message);
      return result;
    }

    async function getToolResponse(toolCall: ChatToolCall): Promise<ChatMessages> {
      if (toolCall.function.name !== 'searchGutenbergBooks') {
        throw new Error(`Unknown tool: ${toolCall.function.name}`);
      }

      const searchTerms = parseSearchTerms(toolCall.function.arguments);
      const toolResult = await searchGutenbergBooks(searchTerms);

      return {
        role: 'tool',
        toolCallId: toolCall.id,
        content: JSON.stringify(toolResult),
      };
    }

    const maxIterations = 10;
    let iterationCount = 0;
    let didReachMaxIterations = true;

    while (iterationCount < maxIterations) {
      iterationCount++;
      const response = await callLLM(messages);
      const choice = response.choices[0];

      if (!choice) {
        throw new Error('Expected the model to return a choice');
      }

      const toolCalls = choice.message.toolCalls;

      if (!toolCalls || toolCalls.length === 0) {
        didReachMaxIterations = false;
        break;
      }

      for (const toolCall of toolCalls) {
        messages.push(await getToolResponse(toolCall));
      }
    }

    if (didReachMaxIterations) {
      console.warn("Warning: Maximum iterations reached");
    }

    console.log(messages[messages.length - 1].content);
    ```

    ```python Python expandable lines theme={null}
    def call_llm(msgs):
        resp = openai_client.chat.completions.create(
            model={{MODEL}},
            tools=tools,
            messages=msgs
        )
        msgs.append(resp.choices[0].message.dict())
        return resp

    def get_tool_response(tool_call):
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        # Look up the correct tool locally, and call it with the provided arguments
        # Other tools can be added without changing the agentic loop
        tool_result = TOOL_MAPPING[tool_name](**tool_args)

        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result),
        }

    max_iterations = 10
    iteration_count = 0
    reached_max_iterations = True

    while iteration_count < max_iterations:
        iteration_count += 1
        resp = call_llm(messages)

        tool_calls = resp.choices[0].message.tool_calls
        if not tool_calls:
            reached_max_iterations = False
            break

        for tool_call in tool_calls:
            messages.append(get_tool_response(tool_call))

    if reached_max_iterations:
        print("Warning: Maximum iterations reached")

    print(messages[-1]['content'])

    ```
  </CodeGroup>
</Template>

## Best Practices and Advanced Patterns

### Function Definition Guidelines

When defining tools for LLMs, follow these best practices:

**Clear and Descriptive Names**: Use descriptive function names that clearly indicate the tool's purpose.

```json lines theme={null}
// Good: Clear and specific
{ "name": "get_weather_forecast" }
```

```json lines theme={null}
// Avoid: Too vague
{ "name": "weather" }
```

**Comprehensive Descriptions**: Provide detailed descriptions that help the model understand when and how to use the tool.

```json lines theme={null}
{
  "description": "Get current weather conditions and 5-day forecast for a specific location. Supports cities, zip codes, and coordinates.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City name, zip code, or coordinates (lat,lng). Examples: 'New York', '10001', '40.7128,-74.0060'"
      },
      "units": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "Temperature unit preference",
        "default": "celsius"
      }
    },
    "required": ["location"]
  }
}
```

### Streaming with Tool Calls

When using streaming responses with tool calls, handle the different content types appropriately:

```typescript expandable lines theme={null}
const stream = await fetch('/api/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'anthropic/claude-sonnet-4.5',
    messages: messages,
    tools: tools,
    stream: true
  })
});

const reader = stream.body.getReader();
let toolCalls = [];

while (true) {
  const { done, value } = await reader.read();
  if (done) {
    break;
  }

  const chunk = new TextDecoder().decode(value);
  const lines = chunk.split('\n').filter(line => line.trim());

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));

      if (data.choices[0].delta.tool_calls) {
        toolCalls.push(...data.choices[0].delta.tool_calls);
      }

      if (data.choices[0].delta.finish_reason === 'tool_calls') {
        await handleToolCalls(toolCalls);
      } else if (data.choices[0].delta.finish_reason === 'stop') {
        // Regular completion without tool calls
        break;
      }
    }
  }
}
```

### Tool Choice Configuration

Control tool usage with the `tool_choice` parameter:

```json lines theme={null}
// Let model decide (default)
{ "tool_choice": "auto" }
```

```json lines theme={null}
// Disable tool usage
{ "tool_choice": "none" }
```

```json lines theme={null}
// Force specific tool
{
  "tool_choice": {
    "type": "function",
    "function": {"name": "search_database"}
  }
}
```

### Parallel Tool Calls

Control whether multiple tools can be called simultaneously with the `parallel_tool_calls` parameter (default is true for most models):

```json lines theme={null}
// Disable parallel tool calls - tools will be called sequentially
{ "parallel_tool_calls": false }
```

When `parallel_tool_calls` is `false`, the model will only request one tool call at a time instead of potentially multiple calls in parallel.

### Multi-Tool Workflows

Design tools that work well together:

```json expandable lines theme={null}
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_products",
        "description": "Search for products in the catalog"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_product_details",
        "description": "Get detailed information about a specific product"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "check_inventory",
        "description": "Check current inventory levels for a product"
      }
    }
  ]
}
```

This allows the model to naturally chain operations: search → get details → check inventory.

### Reliability Tracking

OpenRouter tracks how reliably each provider completes tool calls and surfaces this as the **Tool Call Error Rate** on the Performance tab of every model page. The same signal drives [Auto Exacto](/docs/guides/routing/auto-exacto) provider ordering on tool-calling requests. For the exact validator, JSON Schema draft, regex semantics, and per-tool-call classification, see [How Tool-Calling Success Rate Is Measured](/docs/guides/routing/auto-exacto#how-tool-calling-success-rate-is-measured).

For more details on OpenRouter's message format and tool parameters, see the [API Reference](/docs/api_reference/overview).
