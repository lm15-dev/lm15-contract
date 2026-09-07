---
meta:
  title: Quickstart — Meta Model API
  description: Start fast with Muse Code, or get an API key and wire up your coding agent or SDK to make your first Muse Spark call on Meta Model API.
  keywords: Meta Model API, quickstart, Muse Spark, Muse Code, coding agent, OpenAI SDK, MODEL_API_KEY
cms:
  alias: /model-api/docs/quickstart
  target: aidmc
---

# Quickstart

Make your first [Muse Spark](/docs/models#muse-spark) call in minutes. The fastest path is Muse Code, Meta's coding agent for the terminal. Prefer your own stack? Model API is drop-in compatible with the OpenAI SDK, the Anthropic SDK, and OpenAI-compatible agent CLIs, so most stacks work with a base-URL and key change. This page uses the [Responses API](/docs/protocols/responses) for direct calls; if your code already speaks Chat Completions or Anthropic Messages, see [Choosing an API](/docs/protocols).

## Start with Muse Code {#muse-code}

Muse Code is Meta's coding agent for the terminal and CI, built on Muse Spark. Install it, sign in through your browser, and start building. No API key or provider config to wire up.

Install the CLI on macOS or Linux:

```bash
curl -fsSL https://dev.meta.ai/install.sh | sh
```

Start building:

```bash
muse   # start Muse Code; on first run, choose a browser sign-in or paste an API key
```

On first run, `muse` prompts you to sign in, so you can skip [Set your API key](#api-key) below unless you're also calling the API directly. For headless [CI runs](/docs/muse-code/extending#headless), first run, and permissions, see the [Muse Code overview](/docs/muse-code).

## Use with your coding agent {#agent-setup}

Any harness that supports an OpenAI-compatible or custom provider plugs into Model API via [Responses](/docs/protocols/responses) or [Chat Completions](/docs/protocols/chat-completions). Anthropic-format harnesses like Claude Code plug in via the [Messages API](/docs/protocols/messages) instead, pointed at `https://api.meta.ai` with your `MODEL_API_KEY`. Most tools ask for three values: the base URL `https://api.meta.ai/v1`, your `MODEL_API_KEY`, and the model ID `muse-spark-1.3`.

### Two-step setup {#two-step-setup}

**Step 1: Get an API key.** Grab one from the [Model API dashboard](/) and export it as `MODEL_API_KEY` (see [Set your API key](#api-key)).

**Step 2: Paste this into your coding agent.** OpenCode and other self-configuring agents (Goose, Roo, and more) register a provider straight from a prompt. In a session running on your current model, paste:

```text
Add a new provider to my config for Meta Model API:
- Provider key: "meta", display name "Meta Model API"
- npm adapter: "@ai-sdk/openai" (targets the Responses API)
- Base URL: https://api.meta.ai/v1
- Model: "muse-spark-1.3"
- Reasoning: true, with reasoningEffort "high", reasoningSummary "auto", and include ["reasoning.encrypted_content"]
- Limits: context 1048576, output 131072
- Modalities: input ["text", "image", "pdf", "video"], output ["text"]
- Read the key from the MODEL_API_KEY environment variable
```

Select `muse-spark-1.3` and start coding. That's it. For Codex, Claude Code, or hand-written config, see the [full coding agents guide](/docs/coding-agents).

### OpenCode config {#opencode}

Prefer to edit the config yourself? Manual setup follows the same shape everywhere: register a provider, point it at the base URL, and select `muse-spark-1.3`. Here's the complete block for OpenCode, a popular coding CLI.

Add to your `opencode.json` (global at `~/.config/opencode/opencode.json` or per-project). Use the `@ai-sdk/openai` adapter, which drives Muse Spark over the Responses API — this enables native multimodal input (images and PDFs) and replays encrypted reasoning across turns, so the model retains its prior reasoning during tool loops:

```json
{
  "provider": {
    "meta": {
      "name": "Meta Model API",
      "npm": "@ai-sdk/openai",
      "options": {
        "baseURL": "https://api.meta.ai/v1"
      },
      "models": {
        "muse-spark-1.3": {
          "name": "muse-spark-1.3",
          "reasoning": true,
          "limit": {
            "context": 1048576,
            "output": 131072
          },
          "modalities": {
            "input": ["text", "image", "pdf", "video"],
            "output": ["text"]
          },
          "options": {
            "reasoningEffort": "high",
            "reasoningSummary": "auto",
            "include": ["reasoning.encrypted_content"]
          }
        }
      }
    }
  }
}
```

Run `/connect`, select the `meta` provider, and enter your API key when prompted. Restart OpenCode and select Muse Spark.

> [!NOTE] Encrypted reasoning carries continuity
> The `include: ["reasoning.encrypted_content"]` setting is what carries Muse Spark's reasoning across turns. Without it, the model reasons from scratch each turn and can lose the thread in multi-step loops. If you don't need reasoning continuity or native PDF input, the simpler `@ai-sdk/openai-compatible` adapter works as a fallback. See the [full coding agents guide](/docs/coding-agents#opencode-config) for both adapters and the tradeoffs.

### Any OpenAI-compatible tool {#any-tool}

If your tool has a "base URL" or "API base" field, set it to `https://api.meta.ai/v1` and use `muse-spark-1.3` as the model. This works for LangChain, LlamaIndex, Vercel AI SDK, Continue, and most agentic frameworks.

## Make your first API call {#first-call}

Want to call the API directly? Set your key, then send a request. You'll need a [Model API account](/) and either `curl`, Python 3.9+, or Node.js 18+.

### Set your API key {#api-key}

Get a key from the [Model API dashboard](/) → **API keys** → **Create API key**. Store it as an environment variable so it stays out of your code:

**macOS / Linux:**

```shell
export MODEL_API_KEY="your-api-key-here"
```

**Windows (PowerShell):**

```powershell
$env:MODEL_API_KEY = "your-api-key-here"
```

To persist it across sessions, add the export line to your `~/.bashrc` or `~/.zshrc` (macOS/Linux), or set it through **System > Environment Variables** (Windows).

> [!NOTE] Key storage and rotation
> See the [Authentication guide](/docs/authentication) for how to store and rotate keys.

### Call the API {#call-the-api}

With your key set, send your first request:

#### curl

```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "What is the capital of France?"
}'
```

> [!NOTE] Windows environment variables
> Windows users: use `%MODEL_API_KEY%` (cmd) or `$env:MODEL_API_KEY` (PowerShell) instead of `$MODEL_API_KEY`.

#### Python (OpenAI SDK)

```shell
pip install openai
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input="What is the capital of France?",
)

print(response.model_dump_json(indent=2))
```

#### TypeScript (OpenAI SDK)

```shell
npm install openai
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
  input: 'What is the capital of France?',
});

console.log(JSON.stringify(response, null, 2));
```

> [!NOTE] Pass the API key explicitly
> The OpenAI SDK doesn't auto-read `MODEL_API_KEY`. Always pass `api_key` explicitly or set `OPENAI_API_KEY` to your Model API key. See [Authentication](/docs/authentication) for details.

A successful call returns generated text plus usage, status, and other response metadata.

## Troubleshooting {#troubleshooting}

- **`401` `authentication_error`**: your key isn't set or isn't valid. Check `echo $MODEL_API_KEY` and confirm it matches a key in the dashboard.
- **`404` `model_not_found`**: use a valid model ID such as `muse-spark-1.3` (the default in these examples) or `muse-spark-1.1` exactly.

For other status codes, retries, and error shapes, see the [error handling guide](/docs/error-handling).

## Next steps

- Automate coding tasks from your terminal or CI with [Muse Code](/docs/muse-code).
- Configure OpenCode and other harnesses in the [full coding agents guide](/docs/coding-agents).
- Add live web access with cited answers using [search grounding](/docs/search-grounding).
- Copy a runnable starter from the [Cookbook](/docs/cookbook), or verify params in the [API reference](/docs/api-reference).