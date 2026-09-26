> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/billing/pricing.md).

# Pricing

Understand Parasail pricing across the Serverless per-token, Dedicated per-GPU-hour, and Batch discounted per-token tiers.

## Serverless Pricing: <a href="#serverless-pricing" id="serverless-pricing"></a>

Pricing for the “serverless” is token-based based on tokens split between input and output, and the amount you owe changes depending on which models you choose to use. You can find the pricing listed directly on the "Serverless" page for the Input/Output pricing. The pricing works per million tokens so if the model costs $1 for input and output pricing and you spend 250,000 tokens on input and 250,000 tokens on output, you get charged $.50 $0.25 for the input and $0.25 for the output.

Serverless prices are listed per 1M tokens and synced from the live API.

| Model                    | Model ID                                 | Input ($/1M) | Output ($/1M) | Cached input ($/1M) |
| ------------------------ | ---------------------------------------- | -----------: | ------------: | ------------------: |
| DeepSeek V4 Flash        | `parasail-deepseek-v4-flash`             |        $0.14 |         $0.28 |               $0.07 |
| DeepSeek V4 Flash (0731) | `parasail-deepseek-v4-flash-0731`        |        $0.14 |         $0.28 |               $0.05 |
| DeepSeek V4 Pro          | `parasail-deepseek-v4-pro`               |        $1.74 |         $3.48 |               $0.10 |
| DeepSeek V4 Pro (0813)   | `parasail-deepseek-v4-pro-0813`          |        $1.32 |         $3.96 |              $0.044 |
| deepseek-v41-flash       | `parasail-deepseek-v41-flash`            |        $0.30 |         $1.20 |              $0.006 |
| Gemma 3 27B              | `parasail-gemma3-27b-it`                 |        $0.08 |         $0.45 |               $0.04 |
| Gemma 4 26B-A4B          | `parasail-gemma-4-26b-a4b-it`            |        $0.13 |         $0.40 |               $0.05 |
| Gemma 4 31B              | `parasail-gemma-4-31b-it`                |        $0.15 |         $0.40 |               $0.06 |
| GLM-5.2                  | `parasail-glm-52`                        |        $1.40 |         $4.40 |               $0.26 |
| GLM-5.3 Flash            | `parasail-glm-53-flash`                  |        $0.15 |         $0.50 |               $0.03 |
| glm-53                   | `parasail-glm-53`                        |        $1.40 |         $4.40 |               $0.26 |
| gpt-oss-120b             | `parasail-gpt-oss-120b`                  |        $0.10 |         $0.75 |              $0.055 |
| gpt-oss-20b              | `parasail-gpt-oss-20b`                   |        $0.03 |         $0.15 |               $0.02 |
| Kimi K2.6                | `parasail-kimi-k26`                      |        $0.75 |         $3.50 |               $0.16 |
| Kimi K3                  | `parasail-kimi-k3`                       |        $3.00 |        $15.00 |               $0.30 |
| Llama 3.2 3B             | `parasail-llama-32-3b-instruct`          |        $0.05 |         $0.33 |                   — |
| Llama 3.3 70B (FP8)      | `parasail-llama-33-70b-fp8`              |        $0.22 |         $0.50 |               $0.11 |
| Llama 4 Maverick (FP8)   | `parasail-llama-4-maverick-instruct-fp8` |        $0.35 |         $1.00 |               $0.17 |
| MiniMax M3               | `parasail-minimax-m3`                    |        $0.30 |         $1.20 |               $0.06 |
| Mistral Nemo (FP8)       | `parasail-mistralaimistral-nemo`         |        $0.03 |         $0.03 |                   — |
| Mistral Small 3.2 24B    | `parasail-mistral-small-32-24b`          |        $0.09 |         $0.30 |               $0.05 |
| Qwen2.5-VL 72B           | `parasail-qwen25-vl-72b-instruct`        |        $0.80 |         $1.00 |               $0.40 |
| Qwen3 235B-A22B (2507)   | `parasail-qwen3-235b-a22b-instruct-2507` |        $0.14 |         $0.80 |               $0.05 |
| Qwen3-Coder-Next         | `parasail-qwen3-coder-next`              |        $0.12 |         $0.80 |               $0.07 |
| Qwen3-Next 80B           | `parasail-qwen-3-next-80b-instruct`      |        $0.10 |         $1.10 |               $0.07 |
| Qwen3-VL 235B-A22B       | `parasail-qwen3-vl-235b-a22b-instruct`   |        $0.21 |         $1.90 |               $0.10 |
| Qwen3-VL 8B              | `parasail-qwen3vl-8b-instruct`           |        $0.25 |         $0.75 |               $0.12 |
| Qwen3.5 35B-A3B          | `parasail-qwen3p5-35b-a3b`               |        $0.15 |         $1.00 |               $0.05 |
| Qwen3.5 397B-A17B        | `parasail-qwen35-397b-a17b`              |        $0.50 |         $3.60 |               $0.30 |
| Qwen3.5 9B               | `parasail-qwen35-9b`                     |        $0.10 |         $0.25 |                   — |
| Qwen3.6 35B-A3B          | `parasail-qwen3p6-35b-a3b`               |        $0.15 |         $1.00 |               $0.05 |
| Qwen3.8 27B (FP8)        | `parasail-qwen38-27b`                    |        $0.24 |         $2.20 |               $0.05 |
| UI-TARS 1.5 7B           | `parasail-ui-tars-1p5-7b`                |        $0.10 |         $0.20 |               $0.10 |

## Dedicated Pricing: <a href="#dedicated-pricing" id="dedicated-pricing"></a>

Each dedicated instance costs according to graphics processing unit per hour. Parasail offers various configurations of the hardware fleet to hit your indicated cost, performance, and latency targets. You have the ability to have your dedicated instances automatically scale the number of graphics processing units as your workload fluctuates, but Parasail offers scale-down policy configuration to meet your needs. A scale down policy is when you want the server to automatically turn off. During run time you get the possible option and amount of replicas you want for the model you chose with the pricing displayed on the option:

<figure><img src="https://3807676826-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FLSXNQZeD4w30hUaiugTx%2Fuploads%2Fgit-blob-4873f067ad928ca4d9bd5431387654e1ae8a1445%2FScreenshot%202025-04-02%20at%2012.02.17%E2%80%AFPM.png?alt=media" alt=""><figcaption></figcaption></figure>

## Batch Pricing: <a href="#batch-pricing" id="batch-pricing"></a>

Pricing for the “batch” Use Case is token-based based on total amount of tokens, discounted to reflect the fact that your queries don't get processed in real time, and the amount you owe changes depending on which models you choose to use.

The default pricing bases itself on parameter size unless the model is a named model.

Batch gets billed on a 50% discount of the Serverless Price. Cached tokens are also an additional 50% off. If the model is an FP16 quant model it's 30% more, FP8 models incur no additional costs.

The current Price:

<table><thead><tr><th>Parameter Count</th><th>Size</th><th width="100">Serverless Price</th><th>Batch Price FP8</th><th>Batch Price FP16</th><th>Cache Price FP8</th><th>Cache Price FP16</th></tr></thead><tbody><tr><td>0-4 B</td><td>0-4 B</td><td>$0.05</td><td>$0.025</td><td>$0.033</td><td>$0.013</td><td>$0.016</td></tr><tr><td>4.1-8 B</td><td>4.1-8 B</td><td>$0.08</td><td>$0.040</td><td>$0.052</td><td>$0.020</td><td>$0.026</td></tr><tr><td>LLM_Model_8.1-16 B</td><td>8.1-16 B</td><td>$0.11</td><td>$0.055</td><td>$0.072</td><td>$0.028</td><td>$0.036</td></tr><tr><td>LLM_Model_16.1 B-21 B</td><td>16.1 B-21 B</td><td>$0.45</td><td>$0.225</td><td>$0.293</td><td>$0.113</td><td>$0.146</td></tr><tr><td>LLM_Model_21.1 B-41 B</td><td>21.1 B-41 B</td><td>$0.50</td><td>$0.250</td><td>$0.325</td><td>$0.125</td><td>$0.163</td></tr><tr><td>LLM_Model_41.1 B-80 B</td><td>41.1 B-80 B</td><td>$0.70</td><td>$0.350</td><td>$0.455</td><td>$0.175</td><td>$0.228</td></tr><tr><td>LLM_Model_80.1 B-404 B</td><td>80.1 B-404 B</td><td>$0.80</td><td>$0.400</td><td>$0.520</td><td>$0.200</td><td>$0.260</td></tr><tr><td>LLM_Model_405 B</td><td>405 B</td><td>$1.75</td><td>$0.875</td><td>$1.138</td><td>$0.438</td><td>$0.569</td></tr></tbody></table>

## Billing and payments

Usage belongs to the active organization on your account. All users in an organization contribute usage to the same organization bill.

Use the Parasail dashboard to manage payment methods, review invoices, and confirm the organization you are billing against. If you belong to multiple organizations, switch to the correct organization before creating API keys, launching Dedicated deployments, or submitting Batch jobs.

### Standard billing

Unless you have pre-negotiated invoicing, Parasail bills usage in arrears. Parasail automatically charges your card after your organization's accrued usage reaches $25, then reconciles any remaining balance at the end of the billing cycle.

To increase the automatic charge threshold or move to an Enterprise contract, [contact Parasail](https://help.parasail.io/).

### Payment methods

To use models, create API keys, and access paid platform services, add a credit card. Without a card, you can still view the platform but can't use models or API keys.

Stripe processes credit card information. Parasail doesn't store Payment Card Industry cardholder data.

### Invoices

The Billing page shows the services your organization has consumed, past invoices, and the current invoice for the month.

### Enterprise billing cycle

For Enterprise contracts, Parasail bills monthly unless the contract sets a different cycle. The standard cycle is:

1. Invoice period: first through last day of the month.
2. Reconciliation: first day of the following month.
3. Stripe submission: second day of the following month.
4. Invoice approval: third day of the following month.
5. Payment terms: Net 30.

## Next steps

* [Limits and quotas](/parasail-docs/operate-in-production/limits-and-quotas.md)
* [Billing API](/parasail-docs/api-reference/billing-api.md)
* [Serverless overview](/parasail-docs/products/overview.md)
* [Dedicated Instances overview](/parasail-docs/products/overview-1.md)
* [Batch guide](/parasail-docs/products/quickstart.md)
