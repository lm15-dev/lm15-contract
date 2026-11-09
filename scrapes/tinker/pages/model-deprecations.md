# Model Deprecations

## How does Tinker handle model deprecation?

As new open-weight models are released, we aim to keep the Tinker model lineup current with the best options for different use cases. Regularly updating the model list allows us to keep throughput high and latency low on the models we offer.

When a new model version supersedes an older one in the same family with comparable or better performance, we may add the new version and begin retiring the older one. We also periodically review our model lineup based on usage and overall fit. If a model sees very low usage or no longer makes sense to offer, we may retire it. We'll aim to give advance notice via email and Tinker documentation before removing a model, along with a recommended replacement.

We suggest the following practices:

- Switch to the recommended replacements listed below for any deprecated models.
- Avoid building hard dependencies on any specific model, as models may be updated, replaced, or removed over time.
- Test replacement models well ahead of the retirement date and migrate your code once you've validated they work.

## Recommended replacements

| Retirement date  | Deprecated model                | Recommended replacement                                                               |
| ---------------- | ------------------------------- | ------------------------------------------------------------------------------------- |
| October 23, 2026 | `Qwen3.6-27B`                   | `Qwen3.8-27B`                                                                         |
| October 23, 2026 | `DeepSeek-V3.1`                 | `DeepSeek-V4.1-Flash-1017`                                                            |
| October 23, 2026 | `Nemotron-3-Nano-30B-A3B`       | `Nemotron-3.5-Lightning-30B-A3B`                                                      |
| July 12, 2026    | `Kimi-K2.5`                     | `Kimi-K2.6`                                                                           |
| June 12, 2026    | `Kimi-K2-Thinking`              | `Kimi-K2.6`                                                                           |
| June 12, 2026    | `Qwen3.5-35B-A3B`               | `Qwen3.6-35B-A3B`                                                                     |
| June 12, 2026    | `Qwen3.5-27B`                   | `Qwen3.8-27B`                                                                         |
| June 12, 2026    | `Qwen3-30B-A3B`                 | `Qwen3.6-35B-A3B`                                                                     |
| June 12, 2026    | `Qwen3-30B-A3B-Instruct-2507`   | `Qwen3.6-35B-A3B` (non-thinking mode)                                                 |
| June 12, 2026    | `Qwen3-VL-30B-A3B-Instruct`     | `Qwen3.6-35B-A3B` (includes vision)                                                   |
| June 12, 2026    | `Qwen3-32B`                     | `Qwen3.8-27B`                                                                         |
| June 12, 2026    | `Qwen3-235B-A22B-Instruct-2507` | `Qwen3.5-397B-A17B` (non-thinking mode)                                               |
| June 12, 2026    | `Qwen3-VL-235B-A22B-Instruct`   | `Qwen3.5-397B-A17B` (includes vision)                                                 |
| June 12, 2026    | `Qwen3-4B-Instruct-2507`        | `Qwen3.5-4B` (non-thinking mode)                                                      |
| June 12, 2026    | `Llama-3.3-70B-Instruct`        | `Nemotron-3-Super-120B-A12B`, `Qwen3.8-27B`, or `Qwen3.6-35B-A3B` (non-thinking mode) |
| June 12, 2026    | `Qwen3-30B-A3B-Base`            | `Qwen3.5-35B-A3B-Base`                                                                |
| June 12, 2026    | `Qwen3-8B-Base`                 | `Qwen3.5-9B-Base`                                                                     |
| June 12, 2026    | `Llama-3.1-8B-Instruct`         | `Qwen3.5-9B` (non-thinking mode)                                                      |
| June 12, 2026    | `Llama-3.1-70B` (Base)          | `Qwen3.5-35B-A3B-Base`                                                                |
| June 12, 2026    | `Llama-3.1-8B` (Base)           | `Qwen3.5-9B-Base`                                                                     |
| June 12, 2026    | `Llama-3.2-3B` (Base)           | `Qwen3.5-9B-Base`                                                                     |
| June 12, 2026    | `Llama-3.2-1B` (Base)           | `Qwen3.5-9B-Base`                                                                     |
| June 12, 2026    | `DeepSeek-V3.1-Base`            | `Qwen3.5-35B-A3B-Base`                                                                |
