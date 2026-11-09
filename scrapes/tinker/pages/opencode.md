# Coding with a tinker model using OpenCode

> **Prerequisites**
>
> - A saved Tinker checkpoint (see [Manage Checkpoints](https://tinker-docs.thinkingmachines.ai/tinker/howto/checkpoints/index.md))
> - [OpenCode](https://opencode.ai) installed
> - A `TINKER_API_KEY` (get one from the [Tinker Console](https://tinker.thinkingmachines.ai/keys))

OpenCode can talk to any OpenAI-compatible endpoint. Tinker exposes one, so you can chat or code with a fine-tuned checkpoint directly from your terminal — no export or download needed.

## Step 1: Get your checkpoint path

The checkpoint must be a **sampler checkpoint** (saved via `save_weights_for_sampler`, not a raw training checkpoint). After saving, you get a path like:

```text
tinker://86c57e7e-d609-5865-b5b1-b986732dc41d:train:0/sampler_weights/000043
```

This is the model ID you will use in the config.

## Step 2: Add a provider to `opencode.json`

Create or edit `opencode.json` in your project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "tinker": {
      "env": ["TINKER_API_KEY"],
      "npm": "@ai-sdk/openai-compatible",
      "models": {
        "tinker://YOUR_CHECKPOINT_PATH": {
          "name": "My Fine-Tuned Model",
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true,
          "cost": { "input": 0, "output": 0 },
          "limit": {
            "context": 32768,
            "output": 8192
          },
          "options": {
            "separate_reasoning": true
          }
        }
      },
      "options": {
        "baseURL": "https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1",
        "apiKey": "{env:TINKER_API_KEY}"
      }
    }
  }
}
```

Replace `tinker://YOUR_CHECKPOINT_PATH` with the actual checkpoint path from Step 1.

### Config fields

| Field                        | Purpose                                                                     |
| ---------------------------- | --------------------------------------------------------------------------- |
| `npm`                        | Must be `@ai-sdk/openai-compatible` — tells OpenCode how to talk to the API |
| `env`                        | Lists required env vars; OpenCode warns if they're missing                  |
| `options.baseURL`            | Tinker's OpenAI-compatible endpoint                                         |
| `options.apiKey`             | Supports `{env:VAR}` substitution — never hardcode keys                     |
| `models.<id>`                | The key must match the checkpoint path exactly                              |
| `limit.context`              | Max input tokens (32768 for most Tinker models)                             |
| `limit.output`               | Max output tokens                                                           |
| `options.separate_reasoning` | Set `true` if the model uses thinking tokens (e.g. Kimi-K2 family)          |

## Step 3: Export your API key

```bash
export TINKER_API_KEY="your-api-key-here"
```

## Step 4: Launch OpenCode

```bash
opencode
```

Select your model from the model picker (`tinker/tinker://...`). You're now chatting with your fine-tuned checkpoint.

## Using a base model (no fine-tuning)

You can also point at a base model on Tinker's sampler:

```json
"models": {
  "moonshotai/Kimi-K2.6": {
    "name": "Kimi K2.6",
    "reasoning": true,
    "limit": { "context": 32768, "output": 8192 },
    "options": { "separate_reasoning": true }
  }
}
```

## Next steps

- [Merge into a HuggingFace Model](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/export-hf/index.md) — export a standalone model for self-hosting
- [Build a PEFT LoRA Adapter](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/lora-adapter/index.md) — export an adapter for vLLM / SGLang serving
