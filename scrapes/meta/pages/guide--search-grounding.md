---
meta:
  title: Search grounding
  description: Ground model responses in real-time web search results with inline citations.
  keywords: search grounding, web search, grounded answers, citations, real-time data
cms:
  alias: /model-api/docs/search-grounding
  target: aidmc
---

# Search grounding

Build answers that stay current. Add one tool to your request and return accurate, cited responses grounded in the live web — no custom retrieval pipeline, search index, or RAG infrastructure to build or maintain.

> [!NOTE] Muse Image searches differently
> This page covers the `web_search` tool for text models such as [Muse Spark](/docs/models#muse-spark). [Muse Image](/docs/models#muse-image) does its own web and image search automatically while generating, with no `web_search` tool to add. See [Automatic grounding](/docs/image-generation#grounding).

## How it works {#how-it-works}

Add `web_search` to `tools` in a [Responses API](/docs/protocols/responses) request. The model evaluates the query and decides whether to search. When it does, the response includes:

- `web_search_call`: An output item confirming a search was performed.
- `url_citation`: Annotations on `output_text` blocks that tie specific spans to their source URLs.
- `results` (opt-in): The raw hits behind a `web_search_call`, returned when you include `include: ["web_search_call.results"]`. See [Inspect the raw search results](#search-results).

You send the question; the model handles search and synthesis.

## Basic usage {#basic-usage}

Call `client.responses.create()` with `tools=[{"type": "web_search"}]`:

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input="Who won the most recent Formula 1 race?",
    tools=[
        {
            "type": "web_search",
        },
    ],
)

print(response.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const response = await client.responses.create({
  model: 'muse-spark-1.3',
  input: 'Who won the most recent Formula 1 race?',
  tools: [
    {
      type: 'web_search',
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "input": "Who won the most recent Formula 1 race?",
        "tools": [
            {
                "type": "web_search",
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "Who won the most recent Formula 1 race?",
  "tools": [
    {
      "type": "web_search"
    }
  ]
}'
```


#### Example response

```json
{
  "id": "resp_123",
  "object": "response",
  "created_at": 1778250764,
  "status": "completed",
  "model": "muse-spark-1.1",
  "output": [
    {
      "id": "ws_789",
      "type": "web_search_call",
      "status": "completed"
    },
    {
      "id": "msg_b4d6e9c2ff37410a",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "**Muse Spark** was announced by Meta on **Wednesday, April 8, 2026**.\n\n- It was unveiled as the first AI model from Meta's new \"Muse\" family, developed by Meta Superintelligence Labs \n- Meta described it as a \"small and fast by design\" multimodal model built for real-time reasoning across WhatsApp, Instagram, Facebook, and Meta's smart glasses \n\nThe announcement came in a blog post on April 8, kicking off the week of April 6–10 that TechTarget covered in its roundup published April 10, 2026 .",
          "annotations": [
            {
              "type": "url_citation",
              "url": "https://www.techtarget.com/searchcio/feature/Weekly-news-roundup-Claude-Mythos-concerns-Muse-Spark-debut-and-US-infrastructure-disruption",
              "title": "Weekly news roundup: Claude Mythos concerns, Muse Spark debut and U.S. infrastructure disruption | TechTarget",
              "start_index": 38,
              "end_index": 76
            },
            {
              "type": "url_citation",
              "url": "https://www.thehindubusinessline.com/info-tech/meta-launches-muse-spark-1.1-ai-bets-big-on-superintelligence-push/article70840923.ece",
              "title": "Meta unveils Muse Spark AI model to compete in superintelligence race",
              "start_index": 175,
              "end_index": 225
            },
            {
              "type": "url_citation",
              "url": "https://www.techtarget.com/searchcio/feature/Weekly-news-roundup-Claude-Mythos-concerns-Muse-Spark-debut-and-US-infrastructure-disruption",
              "title": "Weekly news roundup: Claude Mythos concerns, Muse Spark debut and U.S. infrastructure disruption | TechTarget",
              "start_index": 380,
              "end_index": 460
            }
          ]
        }
      ]
    }
  ],
  ...
}
```

The `output` array holds both search metadata and the final answer. Iterate it to pull `web_search_call` items and `message` items.

## Inspect the raw search results {#search-results}

By default a `web_search_call` only reports that it ran (`id`, `type`, `status`). To see the sources it retrieved, add `include: ["web_search_call.results"]` to the request:

```json
{
  "model": "muse-spark-1.1",
  "input": "What was the score of the most recent Formula 1 race? Cite your source.",
  "tools": [{"type": "web_search"}],
  "include": ["web_search_call.results"]
}
```

Each `web_search_call` then includes a `results` array, one entry per retrieved source:

```json
{
  "id": "ws_789",
  "type": "web_search_call",
  "status": "completed",
  "results": [
    {
      "type": "text_result",
      "title": "2026 British Grand Prix",
      "url": "https://en.wikipedia.org/wiki/2026_British_Grand_Prix",
      "snippet": "Leclerc took his ninth Formula One victory, his first at the British Grand Prix..."
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `type` | Result kind; `text_result` for a web page. |
| `title` | Title of the retrieved page. |
| `url` | Source URL. |
| `snippet` | Extracted text the model saw from the page. |

The `results` list is every source the model considered; the `url_citation` annotations are the subset it actually cited.

## Working with citations {#working-with-citations}

When the model grounds an answer, it attaches `url_citation` annotations to `output_text` blocks. Each annotation includes:

| Field | Description |
|-------|-------------|
| `url` | Source URL the model cited |
| `title` | Page title of the source |
| `start_index` | Character offset where the cited passage begins in `text` |
| `end_index` | Character offset where the cited passage ends in `text` |

Use those fields to render inline citations, build footnotes, or link users to sources:

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.1",
    input=[{"role": "user", "content": "What is the current population of Tokyo?"}],
    tools=[{"type": "web_search"}],
)

for item in response.output:
    if item.type == "message":
        for block in item.content:
            if block.type == "output_text":
                print(block.text)
                print()

                if block.annotations:
                    print("Sources:")
                    for ann in block.annotations:
                        if ann.type == "url_citation":
                            cited_text = block.text[ann.start_index:ann.end_index]
                            print(f"  - \"{cited_text}\"")
                            print(f"    {ann.title}: {ann.url}")
```

## Controlling search context {#controlling-search-context}

`search_context_size` controls how much retrieved content reaches the model. More context helps on broader questions but increases latency and token usage.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input="Summarize recent developments in fusion energy research.",
    tools=[
        {
            "type": "web_search",
            "search_context_size": "high",
        },
    ],
)

print(response.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const response = await client.responses.create({
  model: 'muse-spark-1.3',
  input: 'Summarize recent developments in fusion energy research.',
  tools: [
    {
      type: 'web_search',
      search_context_size: 'high',
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "input": "Summarize recent developments in fusion energy research.",
        "tools": [
            {
                "type": "web_search",
                "search_context_size": "high",
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "Summarize recent developments in fusion energy research.",
  "tools": [
    {
      "type": "web_search",
      "search_context_size": "high"
    }
  ]
}'
```


Valid values:

| Value | Behavior |
|-------|----------|
| `"low"` | Minimal context. Fastest responses, lowest token usage. |
| `"medium"` | Balanced context. Good default for most queries. |
| `"high"` | Maximum context. Best for complex queries that benefit from more sources. |

## Localize results with user location {#user-location}

Pass an approximate `user_location` on the tool to bias search toward a locale — useful for "near me" and other location-sensitive queries. Every field is optional; supply only what you know. When set, `type` must be `"approximate"` (its default when omitted).

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input="What are the best-rated coffee shops near me?",
    tools=[
        {
            "type": "web_search",
            "user_location": {
                "type": "approximate",
                "country": "GB",
                "region": "London",
                "city": "London",
                "timezone": "Europe/London",
            },
        },
    ],
)

print(response.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const response = await client.responses.create({
  model: 'muse-spark-1.3',
  input: 'What are the best-rated coffee shops near me?',
  tools: [
    {
      type: 'web_search',
      user_location: {
        type: 'approximate',
        country: 'GB',
        region: 'London',
        city: 'London',
        timezone: 'Europe/London',
      },
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "input": "What are the best-rated coffee shops near me?",
        "tools": [
            {
                "type": "web_search",
                "user_location": {
                    "type": "approximate",
                    "country": "GB",
                    "region": "London",
                    "city": "London",
                    "timezone": "Europe/London",
                },
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "What are the best-rated coffee shops near me?",
  "tools": [
    {
      "type": "web_search",
      "user_location": {
        "type": "approximate",
        "country": "GB",
        "region": "London",
        "city": "London",
        "timezone": "Europe/London"
      }
    }
  ]
}'
```


| Field | Description |
|-------|-------------|
| `type` | Location approximation type. Optional; defaults to `"approximate"`, the only supported value. |
| `country` | Two-letter [ISO 3166-1](https://en.wikipedia.org/wiki/ISO_3166-1) code, such as `GB`. |
| `region` | Region as free text, such as `California`. |
| `city` | City as free text, such as `San Francisco`. |
| `timezone` | [IANA time zone](https://www.iana.org/time-zones) name, such as `America/Los_Angeles`. |

## Streaming {#streaming}

Stream search-grounded answers with `client.responses.stream()`. The stream emits search-call events first, then the answer tokens:

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

with client.responses.stream(
    model="muse-spark-1.1",
    input=[{"role": "user", "content": "What are the latest developments in AI regulation?"}],
    tools=[{"type": "web_search"}],
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print()

    response = stream.get_final_response()

for item in response.output:
    if item.type == "message":
        for block in item.content:
            if block.annotations:
                print("\nSources:")
                for ann in block.annotations:
                    if ann.type == "url_citation":
                        print(f"  - [{ann.title}]({ann.url})")
```

## Constraints {#constraints}

- **Responses API only**: Search grounding is not available through the [Chat Completions API](/docs/protocols/chat-completions).
- **Can be combined with developer-defined tools**: You can use `web_search` alongside developer-defined function tools in the same request. When you do, your function tools must not reuse a name reserved by the `web_search` internals (currently `browser.search`, `browser.open`, and `browser.find`). These reserved names are injected server-side and may change over time. A function tool whose name collides with one returns `HTTP 400` (`type: invalid_request_error`, `param: tools`). The restriction applies only when `web_search` is in the same request; these names are otherwise valid function names.
- **The model decides whether to search**: Enabling `web_search` does not guarantee a search on every request. The model evaluates the query and skips the search when it can answer confidently from its training data. Simple factual questions such as "What is the capital of France?" typically do not trigger a search.
- **Replaying `web_search_call` items in multi-turn input**: When you build conversation history manually (via the `input` array rather than `previous_response_id`) and include prior `web_search_call` items, the `id` field is optional. If omitted or `null`, the server auto-assigns a unique ID before validation. You do not need to store or replay server-assigned `web_search_call` IDs from earlier turns.

## Limitations {#limitations}

Search grounding is reliable for factual lookups and recent-events questions, but keep these limits in mind as you build:

- **Quality is still improving**: Answer quality and source selection continue to improve. Treat a search-grounded answer as a strong starting point rather than a final authority, and verify anything you depend on.
- **Coverage is incomplete**: Not every web source can be retrieved, so an answer may miss relevant pages or omit sources it would otherwise cite. Check the returned [`url_citation`s](#working-with-citations) and the raw [`results`](#search-results) to see what the model actually saw.
- **Best for focused questions**: Single-fact and recent-events queries are the most reliable. Complex, multi-hop research that chains many sources into one answer is less dependable today; break these into narrower requests where you can.
- **Search isn't guaranteed**: The model decides whether to search (see [Constraints](#constraints)), so enabling `web_search` does not force a search on every request.

## Next steps

- Explore the [Responses API](/docs/protocols/responses) to chain search-grounded turns with server-managed state.
- Pair citations with [structured output](/docs/structured-output) when you need grounded answers in a reliable JSON shape.
- Check the [Responses API reference](/docs/api-reference/responses) for the full parameter and response schema.