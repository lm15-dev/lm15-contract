# Models & Pricing

All prices are per million tokens. Checkpoint storage is charged at $0.10 per GB per month.

If you have a request for a model that isn't listed here, you can [let us know](https://docs.google.com/forms/d/e/1FAIpQLSctA7fMX7SkX9530QkkPMiHYuW8aTfi_PeC4bSRCRHl1bFh4w/viewform?usp=dialog).

## Training

We provide a discount on cached prefill tokens.

39 models shown

Clear filters Reset pinned columns

| Model                                                                                                                                                                                            | Context | Size — Total params | Active — Params per token | Arch  | Type                    | Tinker ID                                                      | Prefill                             | Sample            | Train              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | ------------------- | ------------------------- | ----- | ----------------------- | -------------------------------------------------------------- | ----------------------------------- | ----------------- | ------------------ |
| Inkling 2 Small                                                                                                                                                                                  | 64K     | 594B                | 17B                       | MoE   | Hybrid + Vision         | thinkingmachines/Inkling-2-Small                               | $0.30, $0.03 (cached)               | $1.00             | $1.50              |
| Inkling 2 Small (256K)                                                                                                                                                                           | 256K    | 594B                | 17B                       | MoE   | Hybrid + Vision         | thinkingmachines/Inkling-2-Small:peft:262144                   | $0.30, $0.03 (cached)               | $1.00             | $3.00              |
| [Inkling](https://huggingface.co/thinkingmachines/Inkling)                                                                                                                                       | 64K     | 975B                | 41B                       | MoE   | Hybrid + Audio + Vision | thinkingmachines/Inkling                                       | $1.87, $0.374 (cached)              | $4.68             | $5.61              |
| [Inkling (256K)](https://huggingface.co/thinkingmachines/Inkling)                                                                                                                                | 256K    | 975B                | 41B                       | MoE   | Hybrid + Audio + Vision | thinkingmachines/Inkling:peft:262144                           | $1.87, $0.374 (cached)              | $4.68             | $11.23             |
| [Inkling-Small](https://huggingface.co/thinkingmachines/Inkling-Small)                                                                                                                           | 64K     | 276B                | 12B                       | MoE   | Hybrid + Audio + Vision | thinkingmachines/Inkling-Small                                 | $0.58, $0.116 (cached)              | $1.44             | $1.73              |
| [Inkling-Small (256K)](https://huggingface.co/thinkingmachines/Inkling-Small)                                                                                                                    | 256K    | 276B                | 12B                       | MoE   | Hybrid + Audio + Vision | thinkingmachines/Inkling-Small:peft:262144                     | $0.58, $0.116 (cached)              | $1.44             | $3.47              |
| [Nemotron-3.5-Super-VL-120B-A12B](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16) — Limited-time 50% discount                                                         | 64K     | 120B                | 12B                       | MoE   | Hybrid + Vision         | nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16             | ~~$1.14~~ $0.57, $0.114 (cached)    | ~~$2.88~~ $1.44   | ~~$2.552~~ $1.276  |
| [Nemotron-3.5-Super-VL-120B-A12B (256K)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16) — Limited-time 50% discount                                                  | 256K    | 120B                | 12B                       | MoE   | Hybrid + Vision         | nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16:peft:262144 | ~~$1.14~~ $0.57, $0.114 (cached)    | ~~$2.88~~ $1.44   | ~~$4.64~~ $2.32    |
| [Nemotron-3.5-Lightning-30B-A3B](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) — Limited-time 50% discount                                                           | 64K     | 30B                 | 3B                        | MoE   | Hybrid                  | nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16              | ~~$0.368~~ $0.184, $0.0368 (cached) | ~~$0.99~~ $0.495  | ~~$0.88~~ $0.44    |
| [Nemotron-3.5-Lightning-30B-A3B (256K)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) — Limited-time 50% discount                                                    | 256K    | 30B                 | 3B                        | MoE   | Hybrid                  | nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16:peft:262144  | ~~$0.368~~ $0.184, $0.0368 (cached) | ~~$0.99~~ $0.495  | ~~$1.60~~ $0.80    |
| [Nemotron-3-Ultra-550B-A55B](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16) — Limited-time 50% discount                                                                   | 64K     | 550B                | 55B                       | MoE   | Hybrid                  | nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16                  | ~~$3.60~~ $1.80, $0.36 (cached)     | ~~$12.45~~ $6.225 | ~~$10.956~~ $5.478 |
| [Nemotron-3-Ultra-550B-A55B (256K)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16) — Limited-time 50% discount                                                            | 256K    | 550B                | 55B                       | MoE   | Hybrid                  | nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16:peft:262144      | ~~$3.60~~ $1.80, $0.36 (cached)     | ~~$12.45~~ $6.225 | ~~$19.92~~ $9.96   |
| [Nemotron-3-Super-120B-A12B](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16) — Limited-time 50% discount                                                                   | 64K     | 120B                | 12B                       | MoE   | Hybrid                  | nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16                  | ~~$1.14~~ $0.57, $0.114 (cached)    | ~~$2.88~~ $1.44   | ~~$2.552~~ $1.276  |
| [Nemotron-3-Super-120B-A12B (256K)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16) — Limited-time 50% discount                                                            | 256K    | 120B                | 12B                       | MoE   | Hybrid                  | nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16:peft:262144      | ~~$1.14~~ $0.57, $0.114 (cached)    | ~~$2.88~~ $1.44   | ~~$4.64~~ $2.32    |
| [Nemotron-3-Nano-30B-A3B](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16) — [Retiring October 23](https://tinker-docs.thinkingmachines.ai/tinker/model-deprecations/index.md) | 64K     | 30B                 | 3.5B                      | MoE   | Hybrid                  | nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16                     | $0.195, $0.039 (cached)             | $0.495            | $0.44              |
| [GLM-5.3 (256K)](https://huggingface.co/zai-org/GLM-5.3)                                                                                                                                         | 256K    | 753B                | 40B                       | MoE   | Reasoning               | zai-org/GLM-5.3:peft:262144                                    | $3.78, $0.756 (cached)              | $12.15            | $14.58             |
| [GLM-5.3-Flash (256K)](https://huggingface.co/zai-org/GLM-5.3-Flash)                                                                                                                             | 256K    | 320B                | 18B                       | MoE   | Reasoning               | zai-org/GLM-5.3-Flash:peft:262144                              | $0.84, $0.168 (cached)              | $2.11             | $5.58              |
| [Kimi-K3.1-Pro (256K)](https://huggingface.co/moonshotai/Kimi-K3.1-Pro)                                                                                                                          | 256K    | 2.8T                | 104B                      | MoE   | Reasoning + Vision      | moonshotai/Kimi-K3.1-Pro:peft:262144                           | $6.00, $1.20 (cached)               | $25.00            | $32.00             |
| [Kimi-K2.6](https://huggingface.co/moonshotai/Kimi-K2.6)                                                                                                                                         | 32K     | 1T                  | 32B                       | MoE   | Hybrid + Vision         | moonshotai/Kimi-K2.6                                           | $2.205, $0.441 (cached)             | $5.49             | $4.84              |
| [Kimi-K2.6 (128K)](https://huggingface.co/moonshotai/Kimi-K2.6)                                                                                                                                  | 128K    | 1T                  | 32B                       | MoE   | Hybrid + Vision         | moonshotai/Kimi-K2.6:peft:131072                               | $2.205, $0.441 (cached)             | $5.49             | $15.40             |
| [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B)                                                                                                                                           | 64K     | 27B                 | 27B                       | Dense | Hybrid + Vision         | Qwen/Qwen3.8-27B                                               | $0.6975, $0.1395 (cached)           | $5.595            | $4.103             |
| [Qwen3.8-27B (256K)](https://huggingface.co/Qwen/Qwen3.8-27B)                                                                                                                                    | 256K    | 27B                 | 27B                       | Dense | Hybrid + Vision         | Qwen/Qwen3.8-27B:peft:262144                                   | $0.6975, $0.1395 (cached)           | $5.595            | $7.46              |
| [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)                                                                                                                                   | 64K     | 35B                 | 3B                        | MoE   | Hybrid + Vision         | Qwen/Qwen3.6-35B-A3B                                           | $0.45, $0.09 (cached)               | $1.335            | $1.177             |
| [Qwen3.6-35B-A3B (256K)](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)                                                                                                                            | 256K    | 35B                 | 3B                        | MoE   | Hybrid + Vision         | Qwen/Qwen3.6-35B-A3B:peft:262144                               | $0.45, $0.09 (cached)               | $1.335            | $2.14              |
| [Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B) — [Retiring October 23](https://tinker-docs.thinkingmachines.ai/tinker/model-deprecations/index.md)                                       | 64K     | 27B                 | 27B                       | Dense | Hybrid + Vision         | Qwen/Qwen3.6-27B                                               | $1.86, $0.372 (cached)              | $5.595            | $4.103             |
| [Qwen3.5-397B-A17B](https://huggingface.co/Qwen/Qwen3.5-397B-A17B)                                                                                                                               | 64K     | 397B                | 17B                       | MoE   | Hybrid + Vision         | Qwen/Qwen3.5-397B-A17B                                         | $1.65, $0.33 (cached)               | $7.50             | $6.60              |
| [Qwen3.5-397B-A17B (256K)](https://huggingface.co/Qwen/Qwen3.5-397B-A17B)                                                                                                                        | 256K    | 397B                | 17B                       | MoE   | Hybrid + Vision         | Qwen/Qwen3.5-397B-A17B:peft:262144                             | $1.65, $0.33 (cached)               | $7.50             | $12.00             |
| [Qwen3.5-35B-A3B-Base](https://huggingface.co/Qwen/Qwen3.5-35B-A3B-Base)                                                                                                                         | 64K     | 35B                 | 3B                        | MoE   | Base                    | Qwen/Qwen3.5-35B-A3B-Base                                      | $0.54, $0.108 (cached)              | $1.335            | $1.177             |
| [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B)                                                                                                                                             | 64K     | 9B                  | 9B                        | Dense | Hybrid + Vision         | Qwen/Qwen3.5-9B                                                | $0.30, $0.06 (cached)               | $0.807            | $1.463             |
| [Qwen3.5-9B-Base](https://huggingface.co/Qwen/Qwen3.5-9B-Base)                                                                                                                                   | 64K     | 9B                  | 9B                        | Dense | Base                    | Qwen/Qwen3.5-9B-Base                                           | $0.30, $0.06 (cached)               | $0.807            | $1.463             |
| [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)                                                                                                                                             | 64K     | 4B                  | 4B                        | Dense | Hybrid + Vision         | Qwen/Qwen3.5-4B                                                | $0.33, $0.066 (cached)              | $1.005            | $0.737             |
| [Qwen3.5-4B (256K)](https://huggingface.co/Qwen/Qwen3.5-4B)                                                                                                                                      | 256K    | 4B                  | 4B                        | Dense | Hybrid + Vision         | Qwen/Qwen3.5-4B:peft:262144                                    | $0.33, $0.066 (cached)              | $1.005            | $1.34              |
| [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B)                                                                                                                                                 | 32K     | 8B                  | 8B                        | Dense | Hybrid                  | Qwen/Qwen3-8B                                                  | $0.195, $0.039 (cached)             | $0.60             | $0.44              |
| [GPT-OSS-120B](https://huggingface.co/openai/gpt-oss-120b)                                                                                                                                       | 32K     | 117B                | 5B                        | MoE   | Reasoning               | openai/gpt-oss-120b                                            | $0.33, $0.066 (cached)              | $0.84             | $0.737             |
| [GPT-OSS-120B (128K)](https://huggingface.co/openai/gpt-oss-120b)                                                                                                                                | 128K    | 117B                | 5B                        | MoE   | Reasoning               | openai/gpt-oss-120b:peft:131072                                | $0.33, $0.066 (cached)              | $0.84             | $2.33              |
| [GPT-OSS-20B](https://huggingface.co/openai/gpt-oss-20b)                                                                                                                                         | 32K     | 21B                 | 3.6B                      | MoE   | Reasoning               | openai/gpt-oss-20b                                             | $0.18, $0.036 (cached)              | $0.45             | $0.396             |
| [DeepSeek-V4.1-Flash (256K)](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)                                                                                                             | 256K    | 552B                | 16B                       | MoE   | Hybrid                  | deepseek-ai/DeepSeek-V4.1-Flash:peft:262144                    | $0.60, $0.12 (cached)               | $3.60             | $4.98              |
| [DeepSeek-V4.1-Flash-1017 (256K)](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)                                                                                                   | 256K    | 552B                | 16B                       | MoE   | Hybrid                  | deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144               | $0.60, $0.12 (cached)               | $3.60             | $4.98              |
| [DeepSeek-V3.1](https://huggingface.co/deepseek-ai/DeepSeek-V3.1) — [Retiring October 23](https://tinker-docs.thinkingmachines.ai/tinker/model-deprecations/index.md)                            | 32K     | 671B                | 37B                       | MoE   | Hybrid                  | deepseek-ai/DeepSeek-V3.1                                      | $1.695, $0.339 (cached)             | $4.215            | $3.718             |
|                                                                                                                                                                                                  |         |                     |                           |       |                         |                                                                |                                     |                   |                    |
| ---                                                                                                                                                                                              | ---     | ---                 | ---                       | ---   | ---                     | ---                                                            | ---                                 | ---               | ---                |
| No models match these filters. Clear filters                                                                                                                                                     |         |                     |                           |       |                         |                                                                |                                     |                   |                    |

## Serverless Inference (Beta)

Serverless inference is currently in beta and is available for Inkling, Inkling-Small, and Inkling 2 Small only. If you're interested in production use, email us at [**tinker@thinkingmachines.ai**](mailto:tinker@thinkingmachines.ai?subject=Serverless%20Inference%20waitlist&body=Which%20organization%20you%20represent%3A%0A%0AWhich%20models%20you%20need%3A%0A%0AExpected%20volume%3A%0A%0ALatency%20requirements%3A%0A%0AUse%20case%3A%0A%0A) to join the waitlist. Please include which models you need, your expected volume and latency requirements, and your use case.

| Model                                                                  | Tinker ID                                                   | Context | Prefill (Input)       | Sample (Output) |
| ---------------------------------------------------------------------- | ----------------------------------------------------------- | ------- | --------------------- | --------------- |
| Inkling 2 Small                                                        | thinkingmachines/Inkling-2-Small:peft:262144:sampling-nvfp4 | 256K    | $0.30, $0.03 (cached) | $1.00           |
| [Inkling-Small](https://huggingface.co/thinkingmachines/Inkling-Small) | thinkingmachines/Inkling-Small:peft:262144:sampling-nvfp4   | 256K    | $0.30, $0.06 (cached) | $1.20           |
| [Inkling](https://huggingface.co/thinkingmachines/Inkling)             | thinkingmachines/Inkling:peft:262144:sampling-nvfp4         | 256K    | $1.00, $0.17 (cached) | $4.05           |

## Pricing Terms

- **Prefill**: Processing input/prompt tokens when sampling
- **Cached prefill**: The smaller price under each prefill price; applies to input tokens that hit the prompt cache (discounted)
- **Sample**: Generating output tokens
- **Train**: Forward and backward pass for gradient computation. Note: forward only passes invoked by training clients are billed at the training price.
- **Size**: Total parameters, as stated by the model's publisher
- **Active**: Parameters used per token — the same as Size for dense models, a fraction of it for MoE
- **Context**: Maximum sequence length. Models with `:peft:` suffix support extended context. Extended context costs more for training only; prefill and sampling prices are the same as the standard context.
- **Tinker ID**: The exact string to pass to `create_lora_training_client(base_model=...)` or `create_sampling_client(base_model=...)`

MoE models are priced by active parameters, making them significantly more cost-effective than dense models of similar quality.

## Model Types

- **Base**: Raw pretrained models with no chat or instruction tuning. Best for post-training research or running the full post-training pipeline yourself.
- **Reasoning**: Always produce chain-of-thought before their answer. Highest intelligence, higher latency and token cost.
- **Hybrid**: Run in both thinking and non-thinking modes. They reason by default, but chain-of-thought can be disabled via a renderer or argument for faster, cheaper direct answers.
- **Vision**: Vision-language models that accept images alongside text. Shown as a `+ Vision` suffix on the underlying type (for example, `Hybrid + Vision`).
- **Audio**: Models that accept audio alongside text. Shown as a `+ Audio` suffix on the underlying type.

**Architecture** is either **Dense** (all parameters active per token) or **MoE** (mixture-of-experts, only a subset of parameters active per token). MoE models are highlighted in amber.

## Choosing a Model

- **Cost-effective**: Use MoE models (highlighted in amber)
- **Research/post-training**: Use Base models
- **Task-specific fine-tuning**: Start with a Hybrid model
- **Low latency**: Use a Hybrid model with chain-of-thought disabled
- **High intelligence**: Use Reasoning or Hybrid models (chain-of-thought)
- **Vision tasks**: Use models with Vision in the type

## Machine-Readable Pricing

If you want to use this data programmatically (cost estimation, model pickers, dashboards), don't scrape the tables above. The data behind them is published as JSON alongside this page, and those files are the stable interface for scripts (the tables' HTML is presentational and may change):

- [models.json](https://tinker-docs.thinkingmachines.ai/tinker/models.json): the Training table. One object per model with `name`, `tinker_id`, `context`, `size`, `params`, `arch`, `type`, `url`, and per-million-token prices `prefill`, `cached_prefill`, `sample`, `train` (strings like `"$0.374"`). `params` and `active_params` are the total and per-token parameter counts as integers, as stated by the model's publisher (the Size and Active columns show them abbreviated); they are equal for dense models. `size` is the coarse bucket the Size filter uses, set by `params` (the filter lists each bucket's range). Temporarily discounted models also carry `original_*` price fields and a `note`.
- [serverless.json](https://tinker-docs.thinkingmachines.ai/tinker/serverless.json): the Serverless Inference table, with `name`, `tinker_id`, `context`, `url`, `input`, `cached_input`, `output`.

The `url` field is an empty string when no model-card link is provided.

For example:

```python
import json, urllib.request

url = "https://tinker-docs.thinkingmachines.ai/tinker/models.json"
models = json.load(urllib.request.urlopen(url))
for m in models:
    print(m["tinker_id"], m["train"])
```

## Retired Models

These models have been retired and can no longer be used for training or inference, grouped by retirement date. See [Model deprecations](https://tinker-docs.thinkingmachines.ai/tinker/model-deprecations/index.md) for the recommended replacement for each.

### July 12, 2026

- **Kimi:** `Kimi-K2.5`

### June 12, 2026

- **Qwen:** `Qwen3-235B-A22B-Instruct-2507`, `Qwen3-VL-235B-A22B-Instruct`, `Qwen3.5-35B-A3B`, `Qwen3.5-27B`, `Qwen3-32B`, `Qwen3-30B-A3B`, `Qwen3-30B-A3B-Instruct-2507`, `Qwen3-VL-30B-A3B-Instruct`, `Qwen3-30B-A3B-Base`, `Qwen3-8B-Base`, `Qwen3-4B-Instruct-2507`
- **Llama:** `Llama-3.3-70B-Instruct`, `Llama-3.1-70B`, `Llama-3.1-8B`, `Llama-3.1-8B-Instruct`, `Llama-3.2-3B`, `Llama-3.2-1B`
- **DeepSeek:** `DeepSeek-V3.1-Base`
- **Kimi:** `Kimi-K2-Thinking`
