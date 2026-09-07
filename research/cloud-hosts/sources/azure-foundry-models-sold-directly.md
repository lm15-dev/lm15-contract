---
layout: Conceptual
title: Foundry Models sold by Azure - Microsoft Foundry | Microsoft Learn
canonicalUrl: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure
breadcrumb_path: ../../../breadcrumb/azure-ai/toc.json
feedback_help_link_url: https://learn.microsoft.com/answers/tags/133/azure
feedback_help_link_type: get-help-at-qna
feedback_product_url: https://feedback.azure.com/d365community/forum/79b1327d-d925-ec11-b6e6-000d3a4f06a4
feedback_system: Standard
permissioned-type: public
recommendations: true
recommendation_types:
- Training
- Certification
uhfHeaderId: azure-ai-foundry
ms.suite: office
zone_pivot_group_filename: zone-pivots/azure-ai/zone-pivot-groups.json
author: msakande
learn_banner_products:
- azure
manager: mcleans
ms.author: mopeakande
ms.collection: ce-skilling-ai-copilot
ms.update-cycle: 90-days
ms.service: microsoft-foundry
description: Learn about Microsoft Foundry Models sold by Azure, their capabilities, deployment types, and regional availability for AI applications.
ms.date: 2026-08-26T00:00:00.0000000Z
ms.subservice: foundry-models
ms.topic: product-comparison
ms.custom:
- classic-and-new
- references_regions
- tool_generated
- build-aifnd
- build-2025
- pilot-ai-workflow-jan-2026
- doc-kit-assisted
ai-usage: ai-assisted
zone_pivot_groups: models-sold-directly-by-azure
locale: en-us
document_id: 03d4c1f4-6dcb-1263-3abc-263bc8e89246
document_version_independent_id: 5dbd3477-1d66-5aec-d8dd-93196ba23c1a
updated_at: 2026-08-27T17:28:00.0000000Z
original_content_git_url: https://github.com/MicrosoftDocs/azure-ai-docs-pr/blob/live/articles/foundry/foundry-models/concepts/models-sold-directly-by-azure.md
gitcommit: https://github.com/MicrosoftDocs/azure-ai-docs-pr/blob/8889e5f8d377a7575aa9761f873b3fe920c7ec04/articles/foundry/foundry-models/concepts/models-sold-directly-by-azure.md
git_commit_id: 8889e5f8d377a7575aa9761f873b3fe920c7ec04
site_name: Docs
depot_name: Learn.azure-ai
page_type: conceptual
toc_rel: ../../toc.json
word_count: 8185
asset_id: foundry/foundry-models/concepts/models-sold-directly-by-azure
moniker_range_name:
monikers: []
item_type: Content
source_path: articles/foundry/foundry-models/concepts/models-sold-directly-by-azure.md
cmProducts:
- https://authoring-docs-microsoft.poolparty.biz/devrel/540ac133-a371-4dbb-8f94-28d6cc77a70b
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/cbd33d8f-e9af-440e-8f1e-fc69e07b902b
- https://authoring-docs-microsoft.poolparty.biz/devrel/68ec7f3a-2bc6-459f-b959-19beb729907d
spProducts:
- https://authoring-docs-microsoft.poolparty.biz/devrel/60bfc045-f127-4841-9d00-ea35495a5800
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/3820371b-086e-47fb-9d1f-b215f569127a
- https://authoring-docs-microsoft.poolparty.biz/devrel/90370425-aca4-4a39-9533-d52e5e002a5d
platformId: 3bc60d4a-b3c8-dcfb-b686-571a6805ff5b
---

# Foundry Models sold by Azure - Microsoft Foundry | Microsoft Learn

Microsoft Foundry Models in the model catalog comprise two main categories, namely *Foundry Models sold by Azure* and *Foundry Models from partners and community*. This article lists a selection of Foundry Models sold by Azure, along with their capabilities, [deployment types](deployment-types), and regions of availability, **excluding deprecated and retired models**.

Models sold by Azure are also hosted by Azure and operated by Azure as part of the Foundry Models service. They include all Azure OpenAI models and specific, [selected models from top providers](models-sold-directly-by-azure?pivots=azure-direct-others). These models are billed through your Azure subscription, covered by Azure service-level agreements, and supported by Microsoft. To see a list of Foundry Models that are supported by the Foundry Agent Service, see [Models supported by Agent Service](../../agents/concepts/limits-quotas-regions), and for a list of Foundry Models from partners, see [Foundry Models from partners and community](models-from-partners).

Tip

Use the tabs at the top of this page to switch between [Azure OpenAI models](models-sold-directly-by-azure?pivots=azure-openai) and [Other model collections](models-sold-directly-by-azure?pivots=azure-direct-others) from providers like Cohere, DeepSeek, Meta, Mistral AI, and xAI.

::: zone pivot="azure-openai"

## Azure OpenAI in Microsoft Foundry models

Azure OpenAI is powered by a diverse set of models with different capabilities and price points. Model availability varies by region and cloud.

- To see **region availability for Azure OpenAI in Microsoft Foundry models grouped by deployment category**, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).
- For **Azure Government model availability**, refer to [Azure OpenAI in Azure Government](models-sold-directly-by-azure-gov).

### Model highlights

| Models | Description |
| --- | --- |
| [GPT-5.6 series](models-sold-directly-by-azure#gpt-56) | **NEW**`gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` |
| [GPT-chat-latest (preview)](models-sold-directly-by-azure#gpt-chat-latest) | **NEW**`gpt-chat-latest`**Preview** |
| [GPT-5.5 series](models-sold-directly-by-azure#gpt-55) | `gpt-5.5` |
| [GPT-5.4 series](models-sold-directly-by-azure#gpt-54) | `gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-5.4`, `gpt-5.4-pro` |
| [GPT-5.3 series](models-sold-directly-by-azure#gpt-53) | `gpt-5.3-chat`, `gpt-5.3-codex` |
| [GPT-5.2 series](models-sold-directly-by-azure#gpt-52) | `gpt-5.2-codex`, `gpt-5.2`, `gpt-5.2-chat`**Preview** |
| [GPT-5.1 series](models-sold-directly-by-azure#gpt-51) | `gpt-5.1`, `gpt-5.1-chat`**Preview**, `gpt-5.1-codex`, `gpt-5.1-codex-mini` |
| [Sora](/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure?pivots=azure-openai&tabs=global-standard-aoai%2Cstandard-chat-completions%2Cglobal-standard#video-generation-models) | **NEW** sora-2 |
| [GPT-5 series](models-sold-directly-by-azure#gpt-5) | `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-chat`**Preview** |
| [gpt-oss](models-sold-directly-by-azure#gpt-oss) | open-weight reasoning models |
| [codex-mini](models-sold-directly-by-azure#o-series-models) | Fine-tuned version of `o4-mini`. |
| [GPT-4.1 series](models-sold-directly-by-azure#gpt-41-series) | `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano` |
| [computer-use-preview](models-sold-directly-by-azure#computer-use-preview) | An experimental model trained for use with the Responses API computer use tool. |
| [o-series models](models-sold-directly-by-azure#o-series-models) | [Reasoning models](../../openai/how-to/reasoning) with advanced problem solving and increased focus and capability. |
| [GPT-4o, GPT-4o mini, and GPT-4 Turbo](models-sold-directly-by-azure#gpt-4o-and-gpt-4-turbo) | Capable Azure OpenAI models with multimodal versions, which can accept both text and images as input. |
| [Embeddings](models-sold-directly-by-azure#embeddings) | A set of models that can convert text into numerical vector form to facilitate text similarity. |
| [Image generation](models-sold-directly-by-azure#image-generation-models) | A series of models that can generate original images from natural language. |
| [`Video generation`](models-sold-directly-by-azure#video-generation-models) | A model that can generate original video scenes from text instructions. |
| [Audio](models-sold-directly-by-azure#audio-models) | A series of models for speech to text, translation, and text to speech. GPT-4o audio models support either low latency *speech in, speech out* conversational interactions or audio generation. |

### Understand model token limits

The **Context Window** column lists the total number of tokens that a model can process in a request. When a row lists separate **Input** and **Output** values, these values are individual limits. They aren't additive allowances that you can always use together. Input tokens, generated output tokens, and reasoning tokens share the available context budget. More input leaves fewer tokens for generation.

The **Max Output Tokens** column sets an upper limit, not a guaranteed output size. An API parameter such as `max_output_tokens` doesn't reserve tokens when the request has less context budget available.

## GPT-chat-latest

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-chat-latest` (2026-08-06)**Preview** | - [Reasoning](../../openai/how-to/reasoning).  - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs  - Functions, tools, and parallel tool calling. | 400,000Input: 272,000Output: 128,000 | 128,000 | February 2026 |
| `gpt-chat-latest` (2026-06-24)**Preview** | - [Reasoning](../../openai/how-to/reasoning).  - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs  - Functions, tools, and parallel tool calling. | 128,000 Input: 111,616  Output: 16,384 | 16,384 | August 2025 |
| `gpt-chat-latest` (2026-05-28)**Preview** | - [Reasoning](../../openai/how-to/reasoning).  - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs  - Functions, tools, and parallel tool calling. | 128,000 Input: 111,616  Output: 16,384 | 16,384 | August 2025 |
| `gpt-chat-latest` (2026-05-05)**Preview** | - [Reasoning](../../openai/how-to/reasoning).  - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs  - Functions, tools, and parallel tool calling. | 128,000 Input: 111,616  Output: 16,384 | 16,384 | August 2025 |

`gpt-chat-latest` uses a fixed, nonzero reasoning level, so it can generate reasoning tokens for some requests. Unlike other reasoning models, you can't configure this level with the `reasoning_effort` parameter.

You might also see this model referred to by OpenAI as GPT-5.5 Instant or in the OpenAI API as `chat-latest`. In Microsoft Foundry, the product name for this release is `gpt-chat-latest`. The model continues to follow the existing [Preview lifecycle](../../openai/concepts/model-retirements) and standard notice periods. The team is also evaluating ways to simplify how customers access continuously updated models over time, but current behavior remains unchanged as that work continues.

## GPT-5.6

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-5.6-sol` (2026-07-09) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses).  - [Multi-agent orchestration](../../openai/how-to/responses-multi-agent) (preview). - Chat Completions API.  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Computer use](../../../foundry-classic/openai/how-to/computer-use) - [Full summary of capabilities](../../openai/how-to/reasoning). | 1,050,000 Input: 922,000Output: 128,000 | 128,000 | June 2026 |
| `gpt-5.6-terra` (2026-07-09) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses).  - [Multi-agent orchestration](../../openai/how-to/responses-multi-agent) (preview). - Chat Completions API.  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Computer use](../../../foundry-classic/openai/how-to/computer-use) - [Full summary of capabilities](../../openai/how-to/reasoning). | 1,050,000 Input: 922,000Output: 128,000 | 128,000 | June 2026 |
| `gpt-5.6-luna` (2026-07-09) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses).  - [Multi-agent orchestration](../../openai/how-to/responses-multi-agent) (preview). - Chat Completions API.  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Computer use](../../../foundry-classic/openai/how-to/computer-use) - [Full summary of capabilities](../../openai/how-to/reasoning). | 1,050,000 Input: 922,000Output: 128,000 | 128,000 | June 2026 |

Note

Keep the following in mind when you deploy and call the `gpt-5.6` models:

- Some [quota tiers](../../openai/quotas-limits) require quota requests for `gpt-5.6` to deploy this model. Tier 5 and Tier 6 subscriptions have quota by default. See [Microsoft Foundry Models quotas and limits](/en-us/azure/foundry/foundry-models/quotas-limits) for more information about quotas and limits in Microsoft Foundry.
- Standard pay-as-you-go deployments of the GPT-5.6 model family and later models use separate rates for short-context and long-context requests. Each GPT-5.6 model handles both types of requests. For GPT-5.6, prompts with more than 272,000 input tokens use long-context pricing for the full request, not only for tokens beyond the threshold. Later models might use different thresholds. For current rates, see [Azure OpenAI pricing](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/).
- These models support the Chat Completions API and function tools, but not both at the same time unless `reasoning_effort` is `none`. Use the Responses API for tool calling. For more information, see [Tool calling with reasoning models](../../openai/how-to/reasoning#tool-calling-with-reasoning-models).

## GPT-5.5

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-5.5` (2026-04-24) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses). - Chat Completions API.  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Computer use](../../../foundry-classic/openai/how-to/computer-use) - [Full summary of capabilities](../../openai/how-to/reasoning). | 1,050,000 Input: 922,000Output: 128,000 | 128,000 | December 2025 |

### Responses API token budget

For the current GPT-5.5 Responses API implementation, the effective combined prompt and generation budget is approximately 922,000 tokens. This API limit is lower than the model's 1,050,000-token context window. You can't combine a 922,000-token prompt with 128,000 generated tokens in one request. Calculate the approximate generation budget as follows:

`available generation tokens = 922,000 - prompt tokens`

For example, a request with 921,549 prompt tokens has the following token budget:

- Prompt tokens: 921,549.
- Effective context budget: 922,000.
- Remaining generation budget: 451 tokens.

The model can generate at most the remaining 451 tokens, even if you set `max_output_tokens` to 64,000 or 128,000. This generation budget includes visible output and reasoning tokens.

Reaching the available token budget doesn't necessarily produce an HTTP error. A request can return HTTP status code 200 with an incomplete response. Check `status` for `incomplete` and `incomplete_details.reason` for `max_output_tokens` to determine whether generation stopped at the token limit.

Note

Some [quota tiers](../../openai/quotas-limits) will require quota requests for `gpt-5.5` to be able to deploy this model. Tier 5 and Tier 6 subscriptions have quota by default.

## GPT-5.4

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-5.4` (2026-03-05) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses). - Chat Completions API.  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Computer use](../../../foundry-classic/openai/how-to/computer-use) - [Full summary of capabilities](../../openai/how-to/reasoning). | 1,050,000 Input: 922,000Output: 128,000 | 128,000 | August 2025 |
| `gpt-5.4-pro` (2026-03-05) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses).  - Text and image processing.  - Functions & tools  - [Full summary of capabilities](../../openai/how-to/reasoning). | 1,050,000 Input: 922,000Output: 128,000 | 128,000 | August 2025 |
| `gpt-5.4-mini` (2026-03-17) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses). - Chat Completions API.  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Computer use](../../../foundry-classic/openai/how-to/computer-use) - [Full summary of capabilities](../../openai/how-to/reasoning). | 400,000Input: 272,000Output: 128,000 | 128,000 | August 2025 |
| `gpt-5.4-nano` (2026-03-17) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses). - Chat Completions API.  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning). | 400,000Input: 272,000Output: 128,000 | 128,000 | August 2025 |

## GPT-5.3

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-5.3-codex` (2026-02-24) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning).  - Optimized for [Codex CLI & Codex VS Code extension](../../openai/how-to/codex) | 400,000Input: 272,000Output: 128,000 | 128,000 | August 2025 |
| `gpt-5.3-chat` (2026-03-03)**Preview** | - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs  - Functions, tools, and parallel tool calling. | 128,000 Input: 111,616  Output: 16,384 | 16,384 | August 2025 |

## GPT-5.2

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-5.2-codex` (2026-01-14) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning).  - Optimized for [Codex CLI & Codex VS Code extension](../../openai/how-to/codex) | 400,000Input: 272,000Output: 128,000 | 128,000 |  |
| `gpt-5.2` (2025-12-11) | - [Reasoning](../../openai/how-to/reasoning) - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning). | 400,000Input: 272,000Output: 128,000 | 128,000 | August 2025 |
| `gpt-5.2-chat` (2025-12-11)**Preview** | - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs  - Functions, tools, and parallel tool calling. | 128,000 Input: 111,616  Output: 16,384 | 16,384 | August 2025 |
| `gpt-5.2-chat` (2026-02-10)**Preview** | - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs  - Functions, tools, and parallel tool calling. | 128,000 Input: 111,616  Output: 16,384 | 16,384 | August 2025 |

Caution

We don't recommend using preview models in production. We'll upgrade all deployments of preview models to either future preview versions or to the latest stable, generally available version. Models that are designated preview don't follow the standard Azure OpenAI model lifecycle.

## GPT-5.1

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-5.1` (2025-11-13) | - [Reasoning](../../openai/how-to/reasoning) - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning). | 400,000Input: 272,000Output: 128,000 | 128,000 | September 30, 2024 |
| `gpt-5.1-chat` (2025-11-13) **Preview** | - [Reasoning](../../openai/how-to/reasoning) - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs  - Functions, tools, and parallel tool calling. | 128,000 Input: 111,616  Output: 16,384 | 16,384 | September 30, 2024 |
| `gpt-5.1-codex` (2025-11-13) | - [Responses API](../../openai/how-to/responses) only.  - Text and image processing  - Structured outputs.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning) - Optimized for [Codex CLI & Codex VS Code extension](../../openai/how-to/codex) | 400,000Input: 272,000Output: 128,000 | 128,000 | September 30, 2024 |
| `gpt-5.1-codex-mini` (2025-11-13) | - [Responses API](../../openai/how-to/responses) only.  - Text and image processing  - Structured outputs.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning) - Optimized for [Codex CLI & Codex VS Code extension](../../openai/how-to/codex) | 400,000Input: 272,000Output: 128,000 | 128,000 | September 30, 2024 |
| `gpt-5.1-codex-max` (2025-12-04) | - [Responses API](../../openai/how-to/responses) only.  - Text and image processing  - Structured outputs. - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning) - Optimized for [Codex CLI & Codex VS Code extension](../../openai/how-to/codex) | 400,000Input: 272,000Output: 128,000 | 128,000 | September 30, 2024 |

Caution

We don't recommend using preview models in production. We'll upgrade all deployments of preview models to either future preview versions or to the latest stable, generally available version. Models that are designated preview don't follow the standard Azure OpenAI model lifecycle.

Important

- `gpt-5.1``reasoning_effort` defaults to `none`. When upgrading from previous reasoning models to `gpt-5.1`, keep in mind that you may need to update your code to explicitly pass a `reasoning_effort` level if you want reasoning to occur.
- `gpt-5.1-chat` adds built-in reasoning capabilities. Like other [reasoning models](../../openai/how-to/reasoning) it does not support parameters like `temperature`. If you upgrade from using `gpt-5-chat` (which is not a reasoning model) to `gpt-5.1-chat` make sure you remove any custom parameters like `temperature` from your code which are not supported by reasoning models.
- `gpt-5.1-codex-max` adds support for setting `reasoning_effort` to `xhigh`. Reasoning effort `none` is not supported with `gpt-5.1-codex-max`.

## GPT-5

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-5` (2025-08-07) | - [Reasoning](../../openai/how-to/reasoning) - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning). | 400,000Input: 272,000Output: 128,000 | 128,000 | September 30, 2024 |
| `gpt-5-mini` (2025-08-07) | - [Reasoning](../../openai/how-to/reasoning) - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning). | 400,000Input: 272,000Output: 128,000 | 128,000 | May 31, 2024 |
| `gpt-5-nano` (2025-08-07) | - [Reasoning](../../openai/how-to/reasoning) - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning). | 400,000Input: 272,000Output: 128,000 | 128,000 | May 31, 2024 |
| `gpt-5-chat` (2025-08-07)**Preview** | - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - **Input**: Text/Image  - **Output**: Text only | 128,000 | 16,384 | September 30, 2024 |
| `gpt-5-chat` (2025-10-03)**Preview**^1^ | - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - **Input**: Text/Image  - **Output**: Text only | 128,000 | 16,384 | September 30, 2024 |
| `gpt-5-codex` (2025-09-11) | - [Responses API](../../openai/how-to/responses) only.  - **Input**: Text/Image  - **Output**: Text only  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling.  - [Full summary of capabilities](../../openai/how-to/reasoning) - Optimized for [Codex CLI & Codex VS Code extension](../../openai/how-to/codex) | 400,000Input: 272,000Output: 128,000 | 128,000 | - |
| `gpt-5-pro` (2025-10-06) | - [Reasoning](../../openai/how-to/reasoning) - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions and tools  - [Full summary of capabilities](../../openai/how-to/reasoning). | 400,000Input: 272,000Output: 128,000 | 128,000 | September 30, 2024 |

Note

^1^`gpt-5-chat` version `2025-10-03` introduces a significant enhancement focused on emotional intelligence and mental health capabilities. This upgrade integrates specialized datasets and refined response strategies to improve the model's ability to do the following:

- **Understand and interpret emotional context** more accurately, enabling nuanced and empathetic interactions.
- **Provide supportive, responsible responses** in conversations related to mental health, ensuring sensitivity and adherence to best practices.

These improvements aim to make GPT-5-chat more context-aware, human-centric, and reliable in scenarios where emotional tone and well-being considerations are critical.

Caution

We don't recommend using preview models in production. We'll upgrade all deployments of preview models to either future preview versions or to the latest stable, generally available version. Models that are designated preview don't follow the standard Azure OpenAI model lifecycle.

## gpt-oss

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context Window | Max Output Tokens | Training Data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-oss-120b`^1^ (Preview) | - Text in/text out only  - Chat Completions API  - Streaming  - Function calling  - Structured outputs  - Reasoning  - Available for deployment^1^ and via [managed compute](../../../foundry-classic/how-to/deploy-models-managed) | 131,072 | 131,072 | May 31, 2024 |
| `gpt-oss-20b` (Preview) | - Text in/text out only  - Chat Completions API  - Streaming  - Function calling  - Structured outputs  - Reasoning  - Available via [managed compute](../../../foundry-classic/how-to/deploy-models-managed) and [Foundry Local](../../../foundry-local/what-is-foundry-local) | 131,072 | 131,072 | May 31, 2024 |

^1^ Unlike other Azure OpenAI models, `gpt-oss-120b` requires a [Foundry project](/en-us/azure/ai-foundry/quickstarts/get-started-code?tabs=azure-ai-foundry) to deploy the model.

### Deploy with code

```cli
az cognitiveservices account deployment create \
  --name "Foundry-project-resource" \
  --resource-group "test-rg" \
  --deployment-name "gpt-oss-120b" \
  --model-name "gpt-oss-120b" \
  --model-version "1" \
  --model-format "OpenAI-OSS" \
  --sku-capacity 10 \
  --sku-name "GlobalStandard"
```

## GPT-4.1 series

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context window | Max output tokens | Training data (up to) |
| --- | --- | --- | --- | --- |
| `gpt-4.1` (2025-04-14) | - Text and image input  - Text output  - Chat completions API - Responses API  - Streaming  - Function calling  - Structured outputs (chat completions) | - 1,047,576  - 300,000 (standard deployments)  - 128,000 (provisioned managed and batch deployments) | 32,768 | May 31, 2024 |
| `gpt-4.1-nano` (2025-04-14) | - Text and image input  - Text output  - Chat completions API - Responses API  - Streaming  - Function calling  - Structured outputs (chat completions) | - 1,047,576  - 300,000 (standard deployments)  - 128,000 (provisioned managed and batch deployments) | 32,768 | May 31, 2024 |
| `gpt-4.1-mini` (2025-04-14) | - Text and image input  - Text output  - Chat completions API - Responses API  - Streaming  - Function calling  - Structured outputs (chat completions) | - 1,047,576  - 300,000 (standard deployments)  - 128,000 (provisioned managed and batch deployments) | 32,768 | May 31, 2024 |

Note

Provisioned managed deployments of GPT-4.1 series models support context lengths less than 128,000 tokens. A request that exceeds this limit returns an HTTP 400 error. To handle long-context requests on a provisioned deployment, enable [spillover](../../openai/how-to/spillover-traffic-management), which routes those requests to a corresponding standard deployment.

### Known issue

A known issue affects all GPT-4.1 series models. Large tool or function call definitions that exceed 300,000 tokens cause failures, even though the models' 1 million token context limit isn't reached.

The errors can vary based on API call and underlying payload characteristics.

Here are the error messages for the Chat Completions API:

- `Error code: 400 - {'error': {'message': "This model's maximum context length is 300000 tokens. However, your messages resulted in 350564 tokens (100 in the messages, 350464 in the functions). Please reduce the length of the messages or functions.", 'type': 'invalid_request_error', 'param': 'messages', 'code': 'context_length_exceeded'}}`
- `Error code: 400 - {'error': {'message': "Invalid 'tools[0].function.description': string too long. Expected a string with maximum length 1048576, but got a string with length 2778531 instead.", 'type': 'invalid_request_error', 'param': 'tools[0].function.description', 'code': 'string_above_max_length'}}`

Here's the error message for the Responses API:

- `Error code: 500 - {'error': {'message': 'The server had an error processing your request. Sorry about that! You can retry your request, or contact us through an Azure support request at: https://go.microsoft.com/fwlink/?linkid=2213926 if you keep seeing this error. (Please include the request ID d2008353-291d-428f-adc1-defb5d9fb109 in your email.)', 'type': 'server_error', 'param': None, 'code': None}}`

## computer-use-preview

An experimental model trained for use with the [Responses API](../../openai/how-to/responses) computer use tool.

It can be used with third-party libraries to allow the model to control mouse and keyboard input, while getting context from screenshots of the current environment.

Caution

We don't recommend using preview models in production. We'll upgrade all deployments of preview models to either future preview versions or to the latest stable, generally available version. Models that are designated preview don't follow the standard Azure OpenAI model lifecycle.

Registration is required to access `computer-use-preview`. Access is granted based on Microsoft's eligibility criteria. Customers who have access to other limited access models still need to request access for this model.

To request access, go to [`computer-use-preview` limited access model application](https://aka.ms/oai/cuaaccess). When access is granted, you need to create a deployment for the model.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Context window | Max output tokens | Training data (up to) |
| --- | --- | --- | --- | --- |
| `computer-use-preview` (2025-03-11) | Specialized model for use with the [Responses API](../../openai/how-to/responses) computer use tool - Tools - Streaming- Text (input/output)- Image (input) | 8,192 | 1,024 | October 2023 |

## O-Series models

The Azure OpenAI O-Series models are designed to tackle reasoning and problem-solving tasks with increased focus and capability. These models spend more time processing and understanding the user's request, making them exceptionally strong in areas like science, coding, and math, compared to previous iterations.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Max request (tokens) | Training data (up to) |
| --- | --- | --- | --- |
| `codex-mini` (2025-05-16) | Fine-tuned version of `o4-mini`.  - [Responses API](../../openai/how-to/responses). - Structured outputs. - Text and image processing.  - Functions and tools.[Full summary of capabilities](../../openai/how-to/reasoning). | Input: 200,000  Output: 100,000 | May 31, 2024 |
| `o3-pro` (2025-06-10) | - [Responses API](../../openai/how-to/responses). - Structured outputs. - Text and image processing.  - Functions and tools.[Full summary of capabilities](../../openai/how-to/reasoning). | Input: 200,000  Output: 100,000 | May 31, 2024 |
| `o4-mini` (2025-04-16) | - *New* reasoning model, offering [enhanced reasoning abilities](../../openai/how-to/reasoning).  - Chat Completions API.  - [Responses API](../../openai/how-to/responses). - Structured outputs. - Text and image processing.  - Functions and tools.[Full summary of capabilities](../../openai/how-to/reasoning). | Input: 200,000  Output: 100,000 | May 31, 2024 |
| `o3` (2025-04-16) | - *New* reasoning model, offering [enhanced reasoning abilities](../../openai/how-to/reasoning).  - Chat Completions API.  - [Responses API](../../openai/how-to/responses).  - Structured outputs. - Text and image processing.  - Functions, tools, and parallel tool calling. [Full summary of capabilities](../../openai/how-to/reasoning). | Input: 200,000  Output: 100,000 | May 31, 2024 |
| `o3-mini` (2025-01-31) | - [Enhanced reasoning abilities](../../openai/how-to/reasoning).  - Structured outputs. - Text-only processing.  - Functions and tools. | Input: 200,000  Output: 100,000 | October 2023 |
| `o1` (2024-12-17) | - [Enhanced reasoning abilities](../../openai/how-to/reasoning).  - Structured outputs. - Text and image processing.  - Functions and tools. | Input: 200,000  Output: 100,000 | October 2023 |
| `o1-preview`^1^ (2024-09-12) | Older preview version. | Input: 128,000  Output: 32,768 | October 2023 |
| `o1-mini`^2^ (2024-09-12) | A faster and more cost-efficient option in the o1 series, ideal for coding tasks that require speed and lower resource consumption.  - Global Standard deployment available by default.  - Standard (regional) deployments are currently only available for select customers who received access as part of the `o1-preview` limited access release. | Input: 128,000  Output: 65,536 | October 2023 |

^1^`o1-preview` is available only for customers who were granted access as part of the original limited access.

^2^`o1-mini` is currently available to all customers for Global Standard deployment. Select customers were granted standard (regional) deployment access to `o1-mini` as part of the `o1-preview` limited access release. At this time, access to `o1-mini` standard (regional) deployments isn't being expanded.

`o3-deep-research` is currently only available with Foundry Agent Service. To learn more, see the [Deep Research tool guidance](/en-us/azure/ai-foundry/agents/how-to/tools/deep-research).

To learn more about advanced o-series models, see [Getting started with reasoning models](../../openai/how-to/reasoning).

## GPT-4o and GPT-4 Turbo

GPT-4o integrates text and images in a single model, which enables it to handle multiple data types simultaneously. This multimodal approach enhances accuracy and responsiveness in human-computer interactions. GPT-4o matches GPT-4 Turbo in English text and coding tasks while offering superior performance in non-English language tasks and vision tasks, setting new benchmarks for AI capabilities.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

## GPT-4 and GPT-4 Turbo models

You can use these models only with the Chat Completions API. To learn how Azure OpenAI handles model version upgrades, see [Model versions](../../../foundry-classic/openai/concepts/model-versions). To learn how to view and configure the model version settings of your GPT-4 deployments, see [Working with models](../../openai/how-to/working-with-models).

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

| Model ID | Description | Max request (tokens) | Training data (up to) |
| --- | --- | --- | --- |
| `gpt-4o` (2024-11-20)  GPT-4o (Omni) | - Structured outputs. - Text and image processing.  - JSON Mode.  - Parallel function calling.  - Enhanced accuracy and responsiveness.  - Parity with English text and coding tasks compared to GPT-4 Turbo with Vision.  - Superior performance in non-English languages and in vision tasks.  - Enhanced creative writing ability. | Input: 128,000  Output: 16,384 | October 2023 |
| `gpt-4o` (2024-08-06)  GPT-4o (Omni) | - Structured outputs. - Text and image processing.  - JSON Mode.  - Parallel function calling.  - Enhanced accuracy and responsiveness.  - Parity with English text and coding tasks compared to GPT-4 Turbo with Vision.  - Superior performance in non-English languages and in vision tasks. | Input: 128,000  Output: 16,384 | October 2023 |
| `gpt-4o-mini` (2024-07-18)  GPT-4o mini | - Fast, inexpensive, capable model ideal for replacing GPT-3.5 Turbo series models.  - Text and image processing. - JSON Mode.  - Parallel function calling. | Input: 128,000  Output: 16,384 | October 2023 |
| `gpt-4o` (2024-05-13)  GPT-4o (Omni) | - Text and image processing.  - JSON Mode.  - Parallel function calling.  - Enhanced accuracy and responsiveness.  - Parity with English text and coding tasks compared to GPT-4 Turbo with Vision.  - Superior performance in non-English languages and in vision tasks. | Input: 128,000  Output: 4,096 | October 2023 |
| `gpt-4`^1^ (turbo-2024-04-09) GPT-4 Turbo with Vision | New generally available model.  - Replacement for all previous GPT-4 preview models (`vision-preview`, `1106-Preview`, `0125-Preview`).  - Feature availability is currently different, depending on the method of input and the deployment type. | Input: 128,000  Output: 4,096 | December 2023 |

^1^ The provisioned version of `gpt-4` version `turbo-2024-04-09` is currently limited to text only. For more information on provisioned deployments, see [Provisioned guidance](../../openai/concepts/provisioned-throughput).

Caution

We don't recommend that you use preview models in production. We'll upgrade all deployments of preview models to either future preview versions or to the latest stable, generally available version. Models that are designated preview don't follow the standard Azure OpenAI model lifecycle.

## Embeddings

`text-embedding-3-large` is the latest and most capable embedding model. You can't upgrade between embedding models. To move from `text-embedding-ada-002` to `text-embedding-3-large`, you need to generate new embeddings.

- `text-embedding-3-large`
- `text-embedding-3-small`
- `text-embedding-ada-002`

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### Capabilities

OpenAI reports that testing shows that both the large and small third generation embeddings models offer better average multi-language retrieval performance with the [MIRACL](https://github.com/project-miracl/miracl) benchmark. They still maintain performance for English tasks with the [MTEB](https://github.com/embeddings-benchmark/mteb) benchmark.

| Evaluation benchmark | `text-embedding-ada-002` | `text-embedding-3-small` | `text-embedding-3-large` |
| --- | --- | --- | --- |
| MIRACL average | 31.4 | 44.0 | 54.9 |
| MTEB average | 61.0 | 62.3 | 64.6 |

The third generation embeddings models support reducing the size of the embedding via a new `dimensions` parameter. Typically, larger embeddings are more expensive from a compute, memory, and storage perspective. When you can adjust the number of dimensions, you gain more control over overall cost and performance. The `dimensions` parameter isn't supported in all versions of the OpenAI 1.x Python library. To take advantage of this parameter, we recommend that you upgrade to the latest version: `pip install openai --upgrade`.

OpenAI's MTEB benchmark testing found that even when the third-generation model's dimensions are reduced to less than the 1,536 dimensions of `text-embedding-ada-002`, performance remains slightly better.

These models can be used only with Embedding API requests.

| Model ID | Max request (tokens) | Output dimensions | Training data (up to) |
| --- | --- | --- | --- |
| `text-embedding-ada-002` (version 2) | 8,192 | 1,536 | Sep 2021 |
| `text-embedding-ada-002` (version 1) | 2,046 | 1,536 | Sep 2021 |
| `text-embedding-3-large` | 8,192 | 3,072 | Sep 2021 |
| `text-embedding-3-small` | 8,192 | 1,536 | Sep 2021 |

Note

When you send an array of inputs for embedding, the maximum number of input items in the array per call to the embedding endpoint is 2,048.

## Image generation models

The image generation models generate images from text prompts that the user provides. Image generation models include `gpt-image-1`, `gpt-image-1-mini`, `gpt-image-1.5`, and `gpt-image-2`.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model ID | Max request (characters) |
| --- | --- |
| `gpt-image-1` | 4,000 |
| `gpt-image-1-mini` | 4,000 |
| `gpt-image-1.5` | 4,000 |
| `gpt-image-2` | 4,000 |

## Video generation models

Sora-2 is an AI model from OpenAI that creates realistic and imaginative video scenes from text instructions. It's in preview.

| Model ID | Max request (characters) |
| --- | --- |
| `sora-2` | 4,000 |

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

## Audio models

Audio models in Azure OpenAI are available via the `realtime`, `completions`, and `audio` APIs.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

### GPT-4o audio models

The GPT-4o audio models are part of the GPT-4o model family and support either low-latency, *speech in, speech out* conversational interactions or audio generation.

Caution

We don't recommend using preview models in production. We'll upgrade all deployments of preview models to either future preview versions or to the latest stable, generally available version. Models that are designated preview don't follow the standard Azure OpenAI model lifecycle.

Details about maximum request tokens and training data are available in the following table:

| Model ID | Description | Max request (tokens) | Training data (up to) |
| --- | --- | --- | --- |
| `gpt-4o-mini-audio-preview` (2024-12-17)**Preview** | Audio model for audio and text generation. | Input: 128,000  Output: 16,384 | September 2023 |
| `gpt-4o-audio-preview` (2024-12-17) | Audio model for audio and text generation. | Input: 128,000  Output: 16,384 | September 2023 |
| `gpt-4o-realtime-preview` (2025-06-03) | Audio model for real-time audio processing. | Input: 32,000  Output: 4,096 | October 2023 |
| `gpt-4o-realtime-preview` (2024-12-17) | Audio model for real-time audio processing. | Input: 16,000  Output: 4,096 | October 2023 |
| `gpt-4o-mini-realtime-preview` (2024-12-17)**Preview** | Audio model for real-time audio processing. | Input: 128,000  Output: 4,096 | October 2023 |
| `gpt-audio`(2025-08-28)`gpt-audio-mini`(2025-10-06) | Audio model for audio and text generation. | Input: 128,00  Output: 16,384 | October 2023 |
| `gpt-realtime` (2025-08-28) (GA)`gpt-realtime-mini` (2025-10-06)`gpt-realtime-mini` (2025-12-15) | Audio model for real-time audio processing. | Input: 32,000  Output: 4,096 | October 2023 |
| `gpt-audio-1.5` (2026-02-23) | Audio model for audio and text generation. | Input: 128,000  Output: 16,384 | September 2024 |
| `gpt-realtime-1.5` (2026-02-23) | Audio model for real-time audio processing. | Input: 32,000  Output: 4,096 | September 2024 |
| `gpt-realtime-translate` (2026-05-06) | Audio model for real-time multilingual translation with translated speech and text output. | Input: 32,000  Output: 4,096 | September 2024 |
| `gpt-realtime-whisper` (2026-05-06) | Audio model for real-time low-latency transcription. | Input: 32,000  Output: 4,096 | September 2024 |
| `gpt-live-transcribe` (2026-07-29) | Audio model for real-time low-latency transcription. Current recommended model for realtime transcription scenarios. | Input: 32,000  Output: 4,096 | September 2024 |
| `gpt-realtime-2` (2026-05-07) | Audio model for real-time audio processing. | Input: 32,000  Output: 4,096 | September 2024 |
| `gpt-realtime-2.1` (2026-07-07)`gpt-realtime-2.1-mini` (2026-07-07)**preview** | Audio models for real-time audio processing. Minor updates over `gpt-realtime-2` with improved silence and noise handling. | Input: 32,000  Output: 4,096 | September 2024 |

Note

`gpt-realtime-translate`, `gpt-realtime-whisper`, and `gpt-live-transcribe` use duration-based billing. Most other realtime models use token-based input and output pricing. For current rates, see the [Azure OpenAI pricing page](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/).

### Audio API

The audio models via the `/audio` API can be used for speech to text, translation, and text to speech.

#### Speech-to-text models

| Model ID | Description | Max request (audio file size) |
| --- | --- | --- |
| `whisper` | General-purpose speech recognition model. | 25 MB |
| `gpt-transcribe` | Offline speech-to-text model for file transcription via `POST /v1/audio/transcriptions`. Supports language hints. | 25 MB |
| `gpt-4o-transcribe` (2025-03-20)**Preview** | Speech-to-text model powered by GPT-4o. | 25 MB |
| `gpt-4o-mini-transcribe` (2025-03-20)**Preview** | Speech-to-text model powered by GPT-4o mini. | 25 MB |
| `gpt-4o-transcribe-diarize` (2025-10-15)**Preview** | Speech-to-text model with automatic speech recognition. | 25 MB |
| `gpt-4o-mini-transcribe` (2025-12-15)**Preview** | Speech-to-text model with automatic speech recognition. Improved transcription accuracy and robustness. | 25 MB |

Important

`gpt-transcribe` is an offline transcription model and isn't a Realtime API model. For streaming transcription, use `gpt-realtime-whisper` or `gpt-live-transcribe`. `gpt-realtime-whisper` and `gpt-live-transcribe` appear in the **GPT-4o audio models** table because they're Realtime API models, not `/audio` API speech-to-text models.

#### Speech translation models

| Model ID | Description | Max request (audio file size) |
| --- | --- | --- |
| `whisper` | General-purpose speech recognition model. | 25 MB |

#### Text-to-speech models (preview)

| Model ID | Description |
| --- | --- |
| `tts`**Preview** | Text-to-speech model optimized for speed. |
| `tts-hd`**Preview** | Text-to-speech model optimized for quality. |
| `gpt-4o-mini-tts` (2025-03-20) | Text-to-speech model powered by GPT-4o mini.You can guide the voice to speak in a specific style or tone. |
| `gpt-4o-mini-tts` (2025-12-15) | Text-to-speech model powered by GPT-4o mini.You can guide the voice to speak in a specific style or tone. |

## Fine-tuning models

The following models are supported for fine-tuning:

| Model ID | Standard regions | Data Zone | Global | Developer | Methods | Status | Modality |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gpt-4o-mini` (2024-07-18) | North Central US  Sweden Central | US | ✅ | ✅ | SFT | GA | Text to text |
| `gpt-4o` (2024-08-06) | East US2  North Central US  Sweden Central | US | ✅ | ✅ | SFT, DPO | GA | Text and vision to text |
| `gpt-4.1` (2025-04-14) | North Central US  Sweden Central | US | ✅ | ✅ | SFT, DPO | GA | Text and vision to text |
| `gpt-4.1-mini` (2025-04-14) | North Central US  Sweden Central | US | ✅ | ✅ | SFT, DPO | GA | Text to text |
| `gpt-4.1-nano` (2025-04-14) | North Central US  Sweden Central | US | ✅ | ✅ | SFT, DPO | GA | Text to text |
| `o4-mini` (2025-04-16) | East US2  Sweden Central | US | ✅ | ❌ | RFT | GA | Text to text |
| `gpt-5` (2025-08-07) | North Central US  Sweden Central | US | ✅ | ✅ | RFT | GA^\*^ | Text to text |
| `Ministral-3B` (2411) | Not supported | US | ✅ | ❌ | SFT | GA | Text to text |
| `Qwen-32B` | Not supported | US | ✅ | ❌ | SFT | GA | Text to text |
| `Llama-3.3-70B-Instruct` | Not supported | US | ✅ | ❌ | SFT | GA | Text to text |
| `gpt-oss-20b` | Not supported | US | ✅ | ❌ | SFT | GA | Text to text |

^\*^ GPT-5 support for reinforcement fine-tuning is generally available, but access is gated and available by invitation only. Contact your Microsoft account team if you're interested in enrollment.

Or you can fine-tune a previously fine-tuned model, formatted as `base-model.ft-{jobid}`.

Note

Open-source models (Ministral-3B, Qwen-32B, Llama-3.3-70B-Instruct, gpt-oss-20b) are only supported on Foundry resources and in the new Foundry UI.

Note

Global training provides [more affordable](https://aka.ms/aoai-pricing) training per token, but doesn't offer [data residency](https://aka.ms/data-residency). It's currently available to Foundry resources in the following regions:

- Australia East
- Brazil South
- Canada Central
- Canada East
- East US
- East US2
- France Central
- Germany West Central
- Italy North
- Japan East *(no vision support)*
- Korea Central
- North Central US
- Norway East
- Poland Central *(no 4.1-nano support)*
- Southeast Asia
- South Africa North
- South Central US
- South India
- Spain Central
- Sweden Central
- Switzerland West
- Switzerland North
- UK South
- West Europe
- West US
- West US3

## Assistants (preview)

For Assistants, you need a combination of a supported model and a supported region. Certain tools and capabilities require the latest models. The following models are available in the Assistants API, SDK, and Foundry. The following table is for standard deployment. For information on provisioned throughput unit availability, see [Provisioned throughput models](models-sold-directly-by-azure-region-availability?pivots=provisioned). The listed models and regions can be used with both Assistants v1 and v2. You can use [Global Standard models](models-sold-directly-by-azure-region-availability) if they're supported in the following regions.

| Region | gpt-4o, 2024-05-13 | gpt-4o, 2024-08-06 | gpt-4o-mini, 2024-07-18 | gpt-4, 0613 | gpt-4, 1106-Preview | gpt-4, 0125-Preview | gpt-4, turbo-2024-04-09 | gpt-4-32k, 0613 | gpt-35-turbo, 0613 | gpt-35-turbo, 1106 | gpt-35-turbo, 0125 | gpt-35-turbo-16k, 0613 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| australiaeast | - | - | - | ✅ | ✅ | - | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| eastus | ✅ | ✅ | ✅ | - | - | ✅ | ✅ | - | ✅ | - | ✅ | ✅ |
| eastus2 | ✅ | ✅ | ✅ | - | ✅ | - | ✅ | - | ✅ | - | ✅ | ✅ |
| francecentral | - | - | - | ✅ | ✅ | - | - | ✅ | ✅ | ✅ | - | ✅ |
| japaneast | - | - | - | - | - | - | - | - | ✅ | - | ✅ | ✅ |
| norwayeast | - | - | - | - | ✅ | - | - | - | - | - | - | - |
| southindia | - | - | - | - | ✅ | - | - | - | - | ✅ | ✅ | - |
| swedencentral | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ | ✅ | ✅ | - | ✅ |
| uksouth | - | - | - | - | ✅ | ✅ | - | - | ✅ | ✅ | ✅ | ✅ |
| westus | ✅ | ✅ | ✅ | - | ✅ | - | ✅ | - | - | ✅ | ✅ | - |
| westus3 | ✅ | ✅ | ✅ | - | ✅ | - | ✅ | - | - | - | ✅ | - |

## Model retirement

For the latest information on model retirements, refer to the [Model retirement schedule](../../openai/concepts/model-retirement-schedule).

::: zone-end

::: zone pivot="azure-direct-others"

## Black Forest Labs models sold by Azure

Black Forest Labs (BFL) FLUX models bring state-of-the-art image generation to Microsoft Foundry, enabling you to generate and edit high-quality images from text prompts and reference images. FLUX models support a range of capabilities including text-to-image generation, multi-reference image editing, and in-context generation and editing.

You can run these models through the BFL service provider API and through the [images/generations and images/edits endpoints](../../openai/reference-preview).

To work with FLUX models in Foundry, see [Deploy and use FLUX models in Microsoft Foundry](../how-to/use-foundry-models-flux).

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model | Type & API endpoint | Capabilities |
| --- | --- | --- |
| `FLUX.2-flex` | **Image generation** - [BFL service provider API](https://docs.bfl.ai/flux_2/flux2_text_to_image): `/providers/blackforestlabs/v1/flux-2-flex` | - **Input:** text and image (32,000 tokens and up to 10 images^i^)  - **Output:** One Image  - **Tool calling:** No  - **Response formats:** Image (PNG and JPG)  - **Key features:** Fine-grained control; multi-reference support for up to 10 images  - **Additional parameters:**`guidance`: Controls how closely the output follows the prompt. Minimum: 1.5, maximum: 10, default: 4.5. Higher = closer prompt adherence. `steps`: Number of inference steps. Maximum: 50, default: 50. Higher = more detail, slower. |
| `FLUX.2-pro` | **Image generation** - [BFL service provider API](https://docs.bfl.ai/flux_2/flux2_text_to_image): `/providers/blackforestlabs/v1/flux-2-pro` | - **Input:** text and image (32,000 tokens and up to 8 images^ii^)  - **Output:** One Image  - **Tool calling:** No  - **Response formats:** Image (PNG and JPG)  - **Key features:** Multi-reference support for up to 8 images; more grounded in real-world knowledge; greater output flexibility; enhanced performance  - **Additional parameters:***(In provider-specific API only)* Supports all parameters. |
| `FLUX.1-Kontext-pro` | **Image generation** - [Image API](../../openai/reference-preview): `https:///openai/deployments/{deployment-id}/images/generations` and `https:///openai/deployments/{deployment-id}/images/edits` - [BFL service provider API](https://docs.bfl.ai/kontext/kontext_text_to_image): `/providers/blackforestlabs/v1/flux-kontext-pro?api-version=preview` | - **Input:** text and image (5,000 tokens and 1 image)  - **Output:** One Image  - **Tool calling:** No  - **Response formats:** Image (PNG and JPG)  - **Key features:** Character consistency, advanced editing  - **Additional parameters:***(In provider-specific API only)*`seed`, `aspect ratio`, `input_image`, `prompt_unsampling`, `safety_tolerance`, `output_format` |
| `FLUX-1.1-pro` | **Image generation** - [Image API](../../openai/reference-preview): `https:///openai/deployments/{deployment-id}/images/generations` - [BFL service provider API](https://docs.bfl.ai/flux_models/flux_1_1_pro): `/providers/blackforestlabs/v1/flux-pro-1.1?api-version=preview` | - **Input:** text (5,000 tokens and 1 image)  - **Output:** One Image  - **Tool calling:** No  - **Response formats:** Image (PNG and JPG)  - **Key features:** Fast inference speed, strong prompt adherence, competitive pricing, scalable generation  - **Additional parameters:***(In provider-specific API only)*`width`, `height`, `prompt_unsampling`, `seed`, `safety_tolerance`, `output_format` |

^i,ii^ Support for **multiple reference images** is available for FLUX.2 [pro] (Preview) and FLUX.2 [flex] (Preview) by using the API, but *not* in the playground.

## Cohere models sold by Azure

The Cohere family of models includes various models optimized for different use cases, including chat completions, rerank/text classification, and embeddings. Cohere models are optimized for various use cases that include reasoning, summarization, and question answering.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model | Type | Capabilities |
| --- | --- | --- |
| `Cohere-parse-v5`**Preview** | image-to-text | - **Input:** images, tables, and forms  - **Output:** Markdown  - **Languages:**`en`, `fr`, `es`, `it`, `de`, `pt-br`, `ja`, `ko`, `zh-cn`, and `ar` - **Tool calling:** No  - **Response formats:** Markdown |
| `Cohere-rerank-v4.0-pro` | text classification (rerank) | - **Input:** text  - **Output:** text  - **Languages:**`en`, `fr`, `es`, `it`, `de`, `pt-br`, `ja`, `zh-cn`, `ar`, `vi`, `hi`, `ru`, `id`, and `nl` - **Tool calling:** No  - **Response formats:** JSON |
| `Cohere-rerank-v4.0-fast` | text classification (rerank) | - **Input:** text  - **Output:** text  - **Languages:**`en`, `fr`, `es`, `it`, `de`, `pt-br`, `ja`, `zh-cn`, `ar`, `vi`, `hi`, `ru`, `id`, and `nl` - **Tool calling:** No  - **Response formats:** JSON |
| `Cohere-command-a-plus-05-2026`**Preview** | chat-completion  (with reasoning content) | - **Input:** text (128,000 tokens)  - **Output:** text (64,000 tokens)  - **Languages:**`en`, `fr`, `es`, `it`, `de`, `pt-br`, `ja`, `ko`, `zh-cn`, and `ar` - **Tool calling:** Yes  - **Response formats:** Text |
| `Cohere-command-a` | chat-completion | - **Input:** text (131,072 tokens)  - **Output:** text (8,182 tokens)  - **Languages:**`en`, `fr`, `es`, `it`, `de`, `pt-br`, `ja`, `ko`, `zh-cn`, and `ar` - **Tool calling:** Yes  - **Response formats:** Text, JSON |
| `embed-v-4-0` | embeddings | - **Input:** text (512 tokens) and images (2MM pixels)  - **Output:** Vector (256, 512, 1024, 1536 dim.)  - **Languages:**`en`, `fr`, `es`, `it`, `de`, `pt-br`, `ja`, `ko`, `zh-cn`, and `ar` |

## DeepSeek models sold by Azure

The DeepSeek family of models includes several reasoning models, which excel at reasoning tasks by using a step-by-step training process, such as language, scientific reasoning, and coding tasks.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model | Type | Capabilities |
| --- | --- | --- |
| `DeepSeek-V4-Pro` | chat-completion  (with reasoning content) | - **Input:** text (1,000,000 tokens)  - **Output:** text (384,000 tokens)  - **Languages:**`en` and `zh` - **Tool calling:** No  - **Response formats:** Text, JSON |
| `DeepSeek-V4-Flash-0731`**Preview** | chat-completion  (with reasoning content) | - **Input:** text (1,000,000 tokens)  - **Output:** text (384,000 tokens)  - **Languages:**`en` and `zh` - **Tool calling:** No  - **Response formats:** Text, JSON |
| `DeepSeek-V4-Flash` | chat-completion  (with reasoning content) | - **Input:** text (1,000,000 tokens)  - **Output:** text (384,000 tokens)  - **Languages:**`en` and `zh` - **Tool calling:** No  - **Response formats:** Text, JSON |
| `DeepSeek-V3.2-Speciale` | chat-completion  (with reasoning content) | - **Input:** text (128,000 tokens)  - **Output:** text (128,000 tokens)  - **Languages:**`en` and `zh` - **Tool calling:** No  - **Response formats:** Text, JSON |
| `DeepSeek-V3.2` | chat-completion  (with reasoning content) | - **Input:** text (128,000 tokens)  - **Output:** text (128,000 tokens)  - **Languages:**`en` and `zh` - **Tool calling:** No  - **Response formats:** Text, JSON |

## Meta models sold by Azure

Meta Llama models and tools are a collection of pretrained and fine-tuned generative AI text and image reasoning models. Meta models range in scale to include:

- Small language models (SLMs) like 1B and 3B Base and Instruct models for on-device and edge inferencing
- Mid-size large language models (LLMs) like 7B, 8B, and 70B Base and Instruct models
- High-performance models like Meta Llama 3.1-405B Instruct for synthetic data generation and distillation use cases.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model | Type | Capabilities |
| --- | --- | --- |
| `Llama-4-Maverick-17B-128E-Instruct-FP8` | chat-completion | - **Input:** text and images (1M tokens)  - **Output:** text (1M tokens)  - **Languages:**`ar`, `en`, `fr`, `de`, `hi`, `id`, `it`, `pt`, `es`, `tl`, `th`, and `vi` - **Tool calling:** No  - **Response formats:** Text |
| `Llama-3.3-70B-Instruct` | chat-completion | - **Input:** text (128,000 tokens)  - **Output:** text (8,192 tokens)  - **Languages:**`en`, `de`, `fr`, `it`, `pt`, `hi`, `es`, and `th` - **Tool calling:** No  - **Response formats:** Text |

Several Meta models are also available [from partners and community](models-from-partners#meta).

## Microsoft models sold by Azure

Microsoft models include various model groups such as Model Router, MAI models, Phi models, healthcare AI models, and more. Several Microsoft models are also available [from partners and community](models-from-partners#microsoft).

To work with MAI models, see these how-to articles:

- MAI models available in Foundry: [MAI-Image models](../how-to/use-foundry-models-mai-image) and [MAI-Thinking models](../how-to/use-foundry-models-mai-thinking).
- MAI models available through Azure Speech in Foundry Tools: [MAI-Voice](/en-us/azure/ai-services/speech-service/mai-voices) and [MAI-Transcribe](/en-us/azure/ai-services/speech-service/mai-transcribe).

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model | Type | Capabilities |
| --- | --- | --- |
| `MAI-Thinking-1`**Preview** | chat-completion  (with reasoning content). See [API endpoints](../how-to/use-foundry-models-mai-thinking#api-endpoints) for details. | - **Input:** text.  - **Output:** text (up to 64,000 tokens).  - **Context length:** 256,000 tokens  - **Tool calling:** Yes.  - **Response formats:** Text.  - **Key features:** OpenAI Chat Completions compatibility; Encrypted Chain-of-Thought |
| `MAI-Image-2.5-Pro`**Preview** | Image-to-Image and Text-to-Image. See [API endpoints](../how-to/use-foundry-models-mai#api-endpoints) for details. | - **Input:** text, image (JPEG or PNG format for image editing workflows)  - **Output:** One image  - **Context length**: 32,000 tokens  - **Tool calling:** No  - **Response formats:** Image (PNG)  - **Languages:**`en` - **Key features:** High-quality text-to-image generation; Image editing that supports precise, surgical edits without disrupting the rest of the image; Capability to generate more photo-realistic imagery with consistent visual structure than previous models. Well suited for tasks such as concept visualization, creative content generation, image editing workflows, and production design.  - **Parameters:**`width`, `height`, `prompt` Minimum 768×768 pixels; maximum total pixel count 1,048,576 (equivalent to 1024×1024). Either dimension can exceed 1024 as long as the total pixel count stays within the limit (for example, 768×1365 is a valid size). |
| `MAI-Image-2.5-Flash`**Preview** | Image-to-Image and Text-to-Image. See [API endpoints](../how-to/use-foundry-models-mai#api-endpoints) for details. | - **Input:** text, image (JPEG or PNG format for image editing workflows)  - **Output:** One image  - **Context length**: 32,000 tokens  - **Tool calling:** No  - **Response formats:** Image (PNG)  - **Languages:**`en` - **Key features:** High-quality text-to-image generation; Image editing that supports precise, surgical edits without disrupting the rest of the image; Capability to generate realistic imagery with consistent visual structure. Well suited for tasks such as concept visualization, creative content generation, image editing workflows, and production design.  - **Parameters:**`width`, `height`, `prompt` Minimum 768×768 pixels; maximum total pixel count 1,048,576 (equivalent to 1024×1024). Either dimension can exceed 1024 as long as the total pixel count stays within the limit (for example, 768×1365 is a valid size). |
| `MAI-Image-2.5`**Preview** | Image-to-Image and Text-to-Image. See [API endpoints](../how-to/use-foundry-models-mai#api-endpoints) for details. | - **Input:** text, image (JPEG or PNG format for image editing workflows)  - **Output:** One image  - **Context length**: 32,000 tokens  - **Tool calling:** No  - **Response formats:** Image (PNG)  - **Languages:**`en` - **Key features:** High-quality text-to-image generation; Image editing that supports precise, surgical edits without disrupting the rest of the image; Capability to generate realistic imagery with consistent visual structure. Well suited for tasks such as concept visualization, creative content generation, image editing workflows, and production design.  - **Parameters:**`width`, `height`, `prompt` Minimum 768×768 pixels; maximum total pixel count 1,048,576 (equivalent to 1024×1024). Either dimension can exceed 1024 as long as the total pixel count stays within the limit (for example, 768×1365 is a valid size). |
| `model-router`^1^ | chat-completion | More details in [Model router overview](/en-us/azure/ai-foundry/openai/how-to/model-router).  - **Input:** text, image  - **Output:** text (max output tokens varies^2^) **Context window:** 200,000^3^ - **Languages:**`en` |

^1^**Model router version**`2025-11-18`.

^2^**Max output tokens** varies for underlying models in the model router. For example, 32,768 (`GPT-4.1 series`), 100,000 (`o4-mini`), 128,000 (`gpt-5 reasoning models`), and 16,384 (`gpt-5-chat`).

^3^ Larger **context windows** are compatible with *some* of the underlying models of the Model Router. That means an API call with a larger context succeeds only if the prompt gets routed to one of such models. Otherwise, the call fails.

## Mistral models sold by Azure

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model | Type | Capabilities |
| --- | --- | --- |
| `mistral-document-ai-2512` | Image-to-Text | - **Input:** image or PDF pages (30 pages, max 30MB PDF file)  - **Output:** text  - **Languages:**`en` - **Tool calling:** no  - **Response formats:** Text, JSON, Markdown |
| `mistral-medium-3-5`**Preview** | chat-completion | - **Input:** text (128,000 tokens), image  - **Output:** text (128,000 tokens)  - **Tool calling:** No  - **Response formats:** Text, JSON |
| `mistral-ocr-4-0`**Preview** | Image-to-Text | - **Input:** image or PDF pages (30 pages, max 30MB PDF file)  - **Output:** text  - **Languages:**`en` - **Tool calling:** no  - **Response formats:** Text, JSON, Markdown |
| `Mistral-Large-3`**Preview** | chat-completion | - **Input:** text, image  - **Output:** text  - **Languages:**`en`, `fr`, `de`, `es`, `it`, `pt`, `nl`, `zh`, `ja`, `ko`, and `ar` - **Tool calling:** Yes  - **Response formats:** Text, JSON |

Several Mistral models are also available [from partners and community](models-from-partners#mistral-ai).

## Moonshot AI models sold by Azure

Moonshot AI models include Kimi K2.6 (Preview) and Kimi K2.5 (Preview), multimodal reasoning models that accept text and image input.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model | Type | Capabilities |
| --- | --- | --- |
| `Kimi-K2.7-Code`**Preview** | chat-completion  (with reasoning content) | - **Input:** text and image (262,144 tokens)  - **Output:** text (262,144 tokens)  - **Languages:**`en` and `zh` - **Tool calling:** Yes  - **Response formats:** Text |
| `Kimi-K2.6`**Preview** | chat-completion  (with reasoning content) | - **Input:** text and image (262,144 tokens)  - **Output:** text (262,144 tokens)  - **Languages:**`en` and `zh` - **Tool calling:** Yes  - **Response formats:** Text |
| `Kimi-K2.5`**Preview** | chat-completion  (with reasoning content) | - **Input:** text and image (262,144 tokens)  - **Output:** text (262,144 tokens)  - **Languages:**`en` and `zh` - **Tool calling:** Yes  - **Response formats:** Text |

See [this model collection in the Foundry portal](https://ai.azure.com/explore/models?&selectedCollection=Moonshot+ai/?cid=learnDocs).

## SpaceXAI models sold by Azure

SpaceXAI's Grok models in Foundry Models include a diverse set of reasoning and non-reasoning models designed for enterprise use cases such as data extraction, coding, text summarization, and agentic applications.

To work with Grok models, see [Deploy and use Grok models in Foundry](../how-to/use-foundry-models-grok).

[Registration is required for access to](https://aka.ms/xai/grok-4)`grok-code-fast-1` and `grok-4`.

For model availability across all regions, grouped by deployment category, see [Region availability for Foundry Models sold by Azure](models-sold-directly-by-azure-region-availability).

| Model | Type | Capabilities |
| --- | --- | --- |
| `grok-4.6`**Preview** | chat-completion | - **Input:** text, image  - **Output:** text (128,000 tokens max)  - **Context window:** 200,000 tokens - **Languages:**`en` - **Tool calling:** yes  - **Response formats:** text, JSON |
| `grok-4.3`**Preview** | chat-completion | - **Input:** text (200,000 tokens)  - **Output:** text (8,192 tokens)  - **Languages:**`en` - **Tool calling:** yes  - **Response formats:** text |
| `grok-4-20-reasoning`**Preview** | chat-completion | - **Input:** text (262,000 tokens)  - **Output:** text (8,192 tokens)  - **Languages:**`en` - **Tool calling:** yes  - **Response formats:** text |
| `grok-4-20-non-reasoning`**Preview** | chat-completion | - **Input:** text (262,000 tokens)  - **Output:** text (8,192 tokens)  - **Languages:**`en` - **Tool calling:** yes  - **Response formats:** text |
| `grok-4.1-fast-reasoning` | chat-completion | - **Input:** text, image (128,000 tokens)  - **Output:** text (128,000 tokens)  - **Languages:**`en` - **Tool calling:** yes  - **Response formats:** text |
| `grok-4.1-fast-non-reasoning` | chat-completion | - **Input:** text, image (128,000 tokens)  - **Output:** text (128,000 tokens)  - **Languages:**`en` - **Tool calling:** yes  - **Response formats:** text |
| `grok-4` | chat-completion | - **Input:** text (262,000 tokens)  - **Output:** text (8,192 tokens)  - **Languages:**`en` - **Tool calling:** yes  - **Response formats:** text |
| `grok-code-fast-1` | chat-completion | - **Input:** text (256,000 tokens)  - **Output:** text (8,192 tokens)  - **Languages:**`en` - **Tool calling:** yes  - **Response formats:** text |

::: zone-end
