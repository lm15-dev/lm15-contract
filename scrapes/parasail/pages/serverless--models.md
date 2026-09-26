> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/products/overview/models.md).

# Models

Available Serverless models and live token pricing for Parasail.

This catalog is generated daily from the live models endpoint. Use these IDs as the `model` value in your requests. See the [models endpoint](/parasail-docs/api-reference/models-endpoint.md), [pricing](/parasail-docs/billing/pricing.md), and [model recommendations](/parasail-docs/guides/model-recommendations.md).

| Model                    | Model ID                                 | Context window | Max output | Quantization | Input ($/1M) | Output ($/1M) | Cached input ($/1M) |
| ------------------------ | ---------------------------------------- | -------------: | ---------: | ------------ | -----------: | ------------: | ------------------: |
| DeepSeek V4 Flash        | `parasail-deepseek-v4-flash`             |      1,048,576 |  1,048,576 | FP8          |        $0.14 |         $0.28 |               $0.07 |
| DeepSeek V4 Flash (0731) | `parasail-deepseek-v4-flash-0731`        |      1,048,576 |  1,048,576 | FP8          |        $0.14 |         $0.28 |               $0.05 |
| DeepSeek V4 Pro          | `parasail-deepseek-v4-pro`               |      1,048,576 |  1,048,576 | FP8          |        $1.74 |         $3.48 |               $0.10 |
| DeepSeek V4 Pro (0813)   | `parasail-deepseek-v4-pro-0813`          |      1,048,576 |  1,048,576 | FP8          |        $1.32 |         $3.96 |              $0.044 |
| deepseek-v41-flash       | `parasail-deepseek-v41-flash`            |      1,048,576 |  1,048,576 | FP8          |        $0.30 |         $1.20 |              $0.006 |
| Gemma 3 27B              | `parasail-gemma3-27b-it`                 |        131,072 |    131,072 | FP8          |        $0.08 |         $0.45 |               $0.04 |
| Gemma 4 26B-A4B          | `parasail-gemma-4-26b-a4b-it`            |        262,144 |    262,144 | BF16         |        $0.13 |         $0.40 |               $0.05 |
| Gemma 4 31B              | `parasail-gemma-4-31b-it`                |        262,144 |    262,144 | FP8          |        $0.15 |         $0.40 |               $0.06 |
| GLM-5.2                  | `parasail-glm-52`                        |        262,144 |    262,144 | FP4          |        $1.40 |         $4.40 |               $0.26 |
| GLM-5.3 Flash            | `parasail-glm-53-flash`                  |      1,048,576 |  1,048,576 | FP8          |        $0.15 |         $0.50 |               $0.03 |
| glm-53                   | `parasail-glm-53`                        |      1,048,576 |  1,048,576 | FP8          |        $1.40 |         $4.40 |               $0.26 |
| gpt-oss-120b             | `parasail-gpt-oss-120b`                  |        131,072 |    131,072 | FP4          |        $0.10 |         $0.75 |              $0.055 |
| gpt-oss-20b              | `parasail-gpt-oss-20b`                   |        131,072 |    131,072 | FP4          |        $0.03 |         $0.15 |               $0.02 |
| Kimi K2.6                | `parasail-kimi-k26`                      |        262,144 |    262,144 | INT4         |        $0.75 |         $3.50 |               $0.16 |
| Kimi K3                  | `parasail-kimi-k3`                       |      1,048,576 |  1,048,576 | FP4          |        $3.00 |        $15.00 |               $0.30 |
| Llama 3.2 3B             | `parasail-llama-32-3b-instruct`          |        131,072 |    131,072 | BF16         |        $0.05 |         $0.33 |                   — |
| Llama 3.3 70B (FP8)      | `parasail-llama-33-70b-fp8`              |        131,072 |     16,384 | FP8          |        $0.22 |         $0.50 |               $0.11 |
| Llama 4 Maverick (FP8)   | `parasail-llama-4-maverick-instruct-fp8` |        524,288 |     32,768 | FP8          |        $0.35 |         $1.00 |               $0.17 |
| MiniMax M3               | `parasail-minimax-m3`                    |      1,048,576 |    524,288 | FP8          |        $0.30 |         $1.20 |               $0.06 |
| Mistral Nemo (FP8)       | `parasail-mistralaimistral-nemo`         |        131,072 |    131,072 | FP8          |        $0.03 |         $0.03 |                   — |
| Mistral Small 3.2 24B    | `parasail-mistral-small-32-24b`          |        131,072 |     32,768 | BF16         |        $0.09 |         $0.30 |               $0.05 |
| Qwen2.5-VL 72B           | `parasail-qwen25-vl-72b-instruct`        |        128,000 |    128,000 | FP8          |        $0.80 |         $1.00 |               $0.40 |
| Qwen3 235B-A22B (2507)   | `parasail-qwen3-235b-a22b-instruct-2507` |        131,072 |    131,072 | FP8          |        $0.14 |         $0.80 |               $0.05 |
| Qwen3-Coder-Next         | `parasail-qwen3-coder-next`              |        262,144 |    262,144 | BF16         |        $0.12 |         $0.80 |               $0.07 |
| Qwen3-Next 80B           | `parasail-qwen-3-next-80b-instruct`      |        262,144 |    262,144 | FP8          |        $0.10 |         $1.10 |               $0.07 |
| Qwen3-VL 235B-A22B       | `parasail-qwen3-vl-235b-a22b-instruct`   |        131,072 |     32,768 | FP8          |        $0.21 |         $1.90 |               $0.10 |
| Qwen3-VL 8B              | `parasail-qwen3vl-8b-instruct`           |        262,144 |    262,144 | BF16         |        $0.25 |         $0.75 |               $0.12 |
| Qwen3.5 35B-A3B          | `parasail-qwen3p5-35b-a3b`               |        262,144 |    262,144 | FP8          |        $0.15 |         $1.00 |               $0.05 |
| Qwen3.5 397B-A17B        | `parasail-qwen35-397b-a17b`              |        262,144 |    262,144 | FP8          |        $0.50 |         $3.60 |               $0.30 |
| Qwen3.5 9B               | `parasail-qwen35-9b`                     |        262,144 |    262,144 | BF16         |        $0.10 |         $0.25 |                   — |
| Qwen3.6 35B-A3B          | `parasail-qwen3p6-35b-a3b`               |        262,144 |    262,144 | FP8          |        $0.15 |         $1.00 |               $0.05 |
| Qwen3.8 27B (FP8)        | `parasail-qwen38-27b`                    |        262,144 |    262,144 | FP8          |        $0.24 |         $2.20 |               $0.05 |
| UI-TARS 1.5 7B           | `parasail-ui-tars-1p5-7b`                |        128,000 |      2,048 | BF16         |        $0.10 |         $0.20 |               $0.10 |
