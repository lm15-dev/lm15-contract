---
layout: Conceptual
title: Microsoft Foundry REST Reference - Azure OpenAI - Chat | Microsoft Learn
canonicalUrl: https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/chat
enable_rest_try_it: true
rest_product: Azure
uhfHeaderId: azure
breadcrumb_path: ../../../breadcrumb/toc.json
ms.author: mbullwin
manager: nitinme
author: mrbullwinkle
ms.topic: reference
ms.devlang: rest-api
ms.date: 2026-05-27T00:00:00.0000000Z
ms.service: microsoft-foundry
description: Learn how to use the Microsoft Foundry REST Reference - Azure OpenAI - Chat
locale: en-us
moniker_definition_rel: ../../../.monikers.Azure.AzureRestApi.json
document_id: 92adf446-aba5-94f9-96c9-53aace8b9761
document_version_independent_id: c97e60bc-cc8d-861e-aee2-5ed94bf53c08
updated_at: 2026-07-09T22:18:00.0000000Z
original_content_git_url: https://github.com/MicrosoftDocs/azure-docs-rest-apis/blob/live/docs-ref-conceptual/microsoft-foundry/azureopenai/chat.md
gitcommit: https://github.com/MicrosoftDocs/azure-docs-rest-apis/blob/6462e3bdaa191c85756377a92350c4cdf6768346/docs-ref-conceptual/microsoft-foundry/azureopenai/chat.md
git_commit_id: 6462e3bdaa191c85756377a92350c4cdf6768346
site_name: Docs
depot_name: Azure.AzureRestApi
page_type: conceptual
toc_rel: ../../azure/toc.json
feedback_system: None
feedback_product_url: ''
feedback_help_link_type: ''
feedback_help_link_url: ''
word_count: 7070
asset_id: api/microsoft-foundry/azureopenai/chat
moniker_range_name:
monikers: []
item_type: Content
source_path: docs-ref-conceptual/microsoft-foundry/azureopenai/chat.md
cmProducts:
- https://authoring-docs-microsoft.poolparty.biz/devrel/540ac133-a371-4dbb-8f94-28d6cc77a70b
spProducts:
- https://authoring-docs-microsoft.poolparty.biz/devrel/60bfc045-f127-4841-9d00-ea35495a5800
platformId: 96c00cac-0fa6-b3ed-4f81-44d4fd1d4aac
---

# Microsoft Foundry REST Reference - Azure OpenAI - Chat | Microsoft Learn

**API Version:** v1

**Server:**`{endpoint}/openai/v1` — Azure AI Foundry Models APIs

**Server Variables:**

| Variable | Default | Description |
| --- | --- | --- |
| endpoint |  | A supported Azure AI Foundry Models APIs endpoint, including protocol and hostname.For example:`https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/`). |

## Authentication

### ApiKeyAuth (API Key)

Pass your API key in the `api-key` header.

### ApiKeyAuth\_ (API Key)

Pass your API key in the `authorization` header.

### OAuth2Auth (OAuth 2.0)

**Flow:** implicit

**Authorization URL:**`https://login.microsoftonline.com/common/oauth2/v2.0/authorize`

**Scopes:**

- `https://cognitiveservices.azure.com/.default`

### Security Requirements

Endpoints accept **any one** of the following authentication methods:

1. **ApiKeyAuth**
2. **ApiKeyAuth\_**
3. **OAuth2Auth** (scopes: `https://cognitiveservices.azure.com/.default`)

## Create chat completion

```HTTP
POST {endpoint}/openai/v1/chat/completions
```

Creates a chat completion.

### URI Parameters

| Name | In | Required | Type | Description |
| --- | --- | --- | --- | --- |
| endpoint | server | Yes | string | A supported Azure AI Foundry Models APIs endpoint, including protocol and hostname.For example:`https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/`). |
| api-version | query | No | stringPossible values: `v1`, `preview` | The explicit Azure AI Foundry Models API version to use for this request.`v1` if not otherwise specified. |

### Request Body

**Content-Type**: application/json

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| audio | OpenAI.CreateChatCompletionRequestAudio or null | Parameters for audio output. Required when audio output is requested with`modalities: ["audio"]`. | No |  |
| frequency\_penalty | number or null | Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.**Constraints:** min: -2, max: 2 | No |  |
| function\_call | string or OpenAI.ChatCompletionFunctionCallOption (deprecated) | Deprecated in favor of `tool_choice`. Controls which (if any) function is called by the model.`none` means the model will not call a function and instead generates a message.`auto` means the model can pick between generating a message or calling a function. Specifying a particular function via `{"name": "my_function"}` forces the model to call that function.`none` is the default when no functions are present. `auto` is the default if functions are present. | No |  |
| functions | array of OpenAI.ChatCompletionFunctions (deprecated) | Deprecated in favor of `tools`. A list of functions the model may generate JSON inputs for.**Constraints:** minItems: 1, maxItems: 128 | No |  |
| logit\_bias | object or null | Modify the likelihood of specified tokens appearing in the completion. Accepts a JSON object that maps tokens (specified by their token ID in the tokenizer) to an associated bias value from -100 to 100. Mathematically, the bias is added to the logits generated by the model prior to sampling. The exact effect will vary per model, but values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100 should result in a ban or exclusive selection of the relevant token. | No |  |
| logprobs | boolean or null | Whether to return log probabilities of the output tokens or not. If true, returns the log probabilities of each output token returned in the`content` of `message`. | No |  |
| max\_completion\_tokens | integer or null | An upper bound for the number of tokens that can be generated for acompletion, including visible output tokens and reasoning tokens. | No |  |
| max\_tokens | integer or null (deprecated) | The maximum number of tokens that can be generated in the chat completion.This value can be used to control costs for text generated via API.This value is now deprecated in favor of `max_completion_tokens`, and isnot compatible with o1 series models. | No |  |
| messages | array of OpenAI.ChatCompletionRequestMessage | A list of messages comprising the conversation so far. Depending on themodel you use, different message types (modalities) are supported,like text, images, and audio.**Constraints:** minItems: 1 | Yes |  |
| metadata | OpenAI.Metadata or null |  | No |  |
| modalities | OpenAI.ResponseModalities | Output types that you would like the model to generate.Most models are capable of generating text, which is the default:`["text"]`The `gpt-4o-audio-preview` model can also be used togenerate audio. To request that this model generateboth text and audio responses, you can use:`["text", "audio"]` | No |  |
| model | string | Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the model guide to browse and compare available models. | Yes |  |
| n | integer or null | How many chat completion choices to generate for each input message. Note that you will be charged based on the number of generated tokens across all of the choices. Keep `n` as `1` to minimize costs.**Constraints:** min: 1, max: 128 | No |  |
| parallel\_tool\_calls | boolean | Whether to enable parallel function calling during tool use. | No | True |
| prediction | OpenAI.PredictionContent or null | Configuration for a predicted output, which can greatly improveresponse times when large parts of the model response are knownahead of time. This is most common when you are regenerating afile with only minor changes to most of the content. | No |  |
| presence\_penalty | number or null | Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.**Constraints:** min: -2, max: 2 | No |  |
| prompt\_cache\_key | string | Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field. | No |  |
| prompt\_cache\_retention | string or null |  | No |  |
| reasoning\_effort | OpenAI.ReasoningEffort | Constrains effort on reasoning forreasoning models.Currently supported values are `none`, `minimal`, `low`, `medium`, `high`, and `xhigh`. Reducingreasoning effort can result in faster responses and fewer tokens usedon reasoning in a response.- `gpt-5.1` defaults to `none`, which does not perform reasoning. The supported reasoning values for `gpt-5.1` are `none`, `low`, `medium`, and `high`. Tool calls are supported for all reasoning values in gpt-5.1.- All models before `gpt-5.1` default to `medium` reasoning effort, and do not support `none`.- The `gpt-5-pro` model defaults to (and only supports) `high` reasoning effort.- `xhigh` is supported for all models after `gpt-5.1-codex-max`. | No |  |
| response\_format | OpenAI.CreateChatCompletionRequestResponseFormat | An object specifying the format that the model must output.Setting to `{ "type": "json_schema", "json_schema": {...} }` enablesStructured Outputs which ensures the model will match your supplied JSONschema. Learn more in the Setting to `{ "type": "json_object" }` enables the older JSON mode, whichensures the message the model generates is valid JSON. Using `json_schema`is preferred for models that support it. | No |  |
| └─ type | OpenAI.CreateChatCompletionRequestResponseFormatType |  | Yes |  |
| safety\_identifier | string | A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies. The IDs should be a string that uniquely identifies each user, with a maximum length of 64 characters. We recommend hashing their username or email address, in order to avoid sending us any identifying information. **Constraints:** maxLength: 64 | No |  |
| seed | integer or null (deprecated) | This feature is in Beta. If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same `seed` and parameters should return the same result. Determinism is not guaranteed, and you should refer to the `system_fingerprint` response parameter to monitor changes in the backend. | No |  |
| stop | OpenAI.StopConfiguration or null |  | No |  |
| store | boolean or null | Whether or not to store the output of this chat completion request foruse in model distillation or evals products. | No |  |
| stream | boolean or null | If set to true, the model response data will be streamed to the clientas it is generated using server-sent events. | No |  |
| stream\_options | OpenAI.ChatCompletionStreamOptions or null |  | No |  |
| temperature | number or null |  | No |  |
| tool\_choice | OpenAI.ChatCompletionToolChoiceOption | Controls which (if any) tool is called by the model.`none` means the model will not call any tool and instead generates a message.`auto` means the model can pick between generating a message or calling one or more tools.`required` means the model must call one or more tools.Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.`none` is the default when no tools are present. `auto` is the default if tools are present. | No |  |
| tools | array of OpenAI.ChatCompletionTool or OpenAI.CustomToolChatCompletions | A list of tools the model may call. You can provide either custom tools or function tools. | No |  |
| top\_logprobs | integer or null |  | No |  |
| top\_p | number or null |  | No |  |
| user | string (deprecated) | A unique identifier representing your end-user, which can help tomonitor and detect abuse. | No |  |
| user\_security\_context | AzureUserSecurityContext | User security context contains several parameters that describe the application itself, and the end user that interacts with the application. These fields assist your security operations teams to investigate and mitigate security incidents by providing a comprehensive approach to protecting your AI applications. [Learn more](https://aka.ms/TP4AI/Documentation/EndUserContext) about protecting AI applications using Microsoft Defender for Cloud. | No |  |
| verbosity | OpenAI.Verbosity | Constrains the verbosity of the model's response. Lower values will result inmore concise responses, while higher values will result in more verbose responses.Currently supported values are `low`, `medium`, and `high`. | No |  |

### Responses

**Status Code:** 200

**Description**: The request has succeeded.

| **Content-Type** | **Type** | **Description** |
| --- | --- | --- |
| application/json | object or object |  |

**Response Headers:**

| Header | Type | Description |
| --- | --- | --- |
| apim-request-id | string | A request ID used for troubleshooting purposes. |

**Status Code:** default

**Description**: An unexpected error response.

| **Content-Type** | **Type** | **Description** |
| --- | --- | --- |
| application/json | object |  |

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| code | string or null |  | Yes |  |
| inner\_error |  |  | No |  |
| message | string |  | Yes |  |
| param | string or null |  | No |  |
| type | string |  | No |  |

**Response Headers:**

| Header | Type | Description |
| --- | --- | --- |
| apim-request-id | string | A request ID used for troubleshooting purposes. |

### Examples

## Example

Creates a completion for the provided prompt, parameters and chosen model.

```HTTP
POST {endpoint}/openai/v1/chat/completions?api-version=latest&azure-beta=v1=preview

{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "you are a helpful assistant that talks like a pirate"
    },
    {
      "role": "user",
      "content": "can you tell me how to care for a parrot?"
    }
  ]
}
```

**Responses**:

Status Code: 200

```json
{
  "id": "chatcmpl-7R1nGnsXO8n4oi9UPz2f3UHdgAYMn",
  "created": 1686676106,
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "Ahoy matey! So ye be wantin' to care for a fine squawkin' parrot, eh? ..."
      }
    }
  ],
  "usage": {
    "completion_tokens": 557,
    "prompt_tokens": 33,
    "total_tokens": 590
  }
}
```

## Components

### AzureAIFoundryModelsApiVersion

| Property | Value |
| --- | --- |
| **Type** | string |
| **Values** | `v1``preview` |

### AzureContentFilterBlocklistResult

A collection of true/false filtering results for configured custom blocklists.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| details | array of object | The pairs of individual blocklist IDs and whether they resulted in a filtering action. | No |  |
| filtered | boolean | A value indicating whether any of the detailed blocklists resulted in a filtering action. | Yes |  |

### AzureContentFilterCompletionTextSpan

A representation of a span of completion text as used by Azure OpenAI content filter results.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| completion\_end\_offset | integer (int32) | Offset of the first UTF32 code point which is excluded from the span. This field is always equal to completion\_start\_offset for empty spans. This field is always larger than completion\_start\_offset for non-empty spans. | Yes |  |
| completion\_start\_offset | integer (int32) | Offset of the UTF32 code point which begins the span. | Yes |  |

### AzureContentFilterCompletionTextSpanDetectionResult

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| details | array of AzureContentFilterCompletionTextSpan | Detailed information about the detected completion text spans. | Yes |  |
| detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |

### AzureContentFilterCustomTopicResult

A collection of true/false filtering results for configured custom topics.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| details | array of object | The pairs of individual topic IDs and whether they are detected. | No |  |
| filtered | boolean | A value indicating whether any of the detailed topics resulted in a filtering action. | Yes |  |

### AzureContentFilterDetectionResult

A labeled content filter result item that indicates whether the content was detected and whether the content was filtered.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |

### AzureContentFilterPersonallyIdentifiableInformationResult

A content filter detection result for Personally Identifiable Information that includes harm extensions.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |
| redacted\_text | string | The redacted text with PII information removed or masked. | No |  |
| sub\_categories | array of AzurePiiSubCategoryResult | Detailed results for individual PIIHarmSubCategory(s). | No |  |

### AzureContentFilterResultForChoice

A content filter result for a single response item produced by a generative AI system.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| custom\_blocklists | AzureContentFilterBlocklistResult | A collection of true/false filtering results for configured custom blocklists. | No |  |
| └─ details | array of object | The pairs of individual blocklist IDs and whether they resulted in a filtering action. | No |  |
| └─ filtered | boolean | A value indicating whether the blocklist produced a filtering action. | Yes |  |
| └─ id | string | The ID of the custom blocklist evaluated. | Yes |  |
| └─ filtered | boolean | A value indicating whether any of the detailed blocklists resulted in a filtering action. | Yes |  |
| custom\_topics | AzureContentFilterCustomTopicResult | A collection of true/false filtering results for configured custom topics. | No |  |
| └─ details | array of object | The pairs of individual topic IDs and whether they are detected. | No |  |
| └─ detected | boolean | A value indicating whether the topic is detected. | Yes |  |
| └─ id | string | The ID of the custom topic evaluated. | Yes |  |
| └─ filtered | boolean | A value indicating whether any of the detailed topics resulted in a filtering action. | Yes |  |
| error | object | If present, details about an error that prevented content filtering from completing its evaluation. | No |  |
| └─ code | integer (int32) | A distinct, machine-readable code associated with the error. | Yes |  |
| └─ message | string | A human-readable message associated with the error. | Yes |  |
| hate | AzureContentFilterSeverityResult | A labeled content filter result item that indicates whether the content was filtered and what the qualitativeseverity level of the content was, as evaluated against content filter configuration for the category. | No |  |
| └─ filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| └─ severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |
| personally\_identifiable\_information | AzureContentFilterPersonallyIdentifiableInformationResult | A content filter detection result for Personally Identifiable Information that includes harm extensions. | No |  |
| └─ redacted\_text | string | The redacted text with PII information removed or masked. | No |  |
| └─ sub\_categories | array of AzurePiiSubCategoryResult | Detailed results for individual PIIHarmSubCategory(s). | No |  |
| profanity | AzureContentFilterDetectionResult | A labeled content filter result item that indicates whether the content was detected and whether the content wasfiltered. | No |  |
| └─ detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| └─ filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |
| protected\_material\_code | object | A detection result that describes a match against licensed code or other protected source material. | No |  |
| └─ citation | object | If available, the citation details describing the associated license and its location. | No |  |
| └─ URL | string (uri) | The URL associated with the license. | No |  |
| └─ license | string | The name or identifier of the license associated with the detection. | No |  |
| └─ detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| └─ filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |
| protected\_material\_text | AzureContentFilterDetectionResult | A labeled content filter result item that indicates whether the content was detected and whether the content wasfiltered. | No |  |
| └─ detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| └─ filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |
| self\_harm | AzureContentFilterSeverityResult | A labeled content filter result item that indicates whether the content was filtered and what the qualitativeseverity level of the content was, as evaluated against content filter configuration for the category. | No |  |
| └─ filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| └─ severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |
| sexual | AzureContentFilterSeverityResult | A labeled content filter result item that indicates whether the content was filtered and what the qualitativeseverity level of the content was, as evaluated against content filter configuration for the category. | No |  |
| └─ filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| └─ severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |
| ungrounded\_material | AzureContentFilterCompletionTextSpanDetectionResult |  | No |  |
| violence | AzureContentFilterSeverityResult | A labeled content filter result item that indicates whether the content was filtered and what the qualitativeseverity level of the content was, as evaluated against content filter configuration for the category. | No |  |
| └─ filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| └─ severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |

### AzureContentFilterResultForPrompt

A content filter result associated with a single input prompt item into a generative AI system.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content\_filter\_results | object | The content filter category details for the result. | No |  |
| └─ custom\_blocklists | AzureContentFilterBlocklistResult | A collection of true/false filtering results for configured custom blocklists. | No |  |
| └─ details | array of object | The pairs of individual blocklist IDs and whether they resulted in a filtering action. | No |  |
| └─ filtered | boolean | A value indicating whether the blocklist produced a filtering action. | Yes |  |
| └─ id | string | The ID of the custom blocklist evaluated. | Yes |  |
| └─ filtered | boolean | A value indicating whether any of the detailed blocklists resulted in a filtering action. | Yes |  |
| └─ custom\_topics | AzureContentFilterCustomTopicResult | A collection of true/false filtering results for configured custom topics. | No |  |
| └─ details | array of object | The pairs of individual topic IDs and whether they are detected. | No |  |
| └─ detected | boolean | A value indicating whether the topic is detected. | Yes |  |
| └─ id | string | The ID of the custom topic evaluated. | Yes |  |
| └─ filtered | boolean | A value indicating whether any of the detailed topics resulted in a filtering action. | Yes |  |
| └─ error | object | If present, details about an error that prevented content filtering from completing its evaluation. | No |  |
| └─ code | integer (int32) | A distinct, machine-readable code associated with the error. | Yes |  |
| └─ message | string | A human-readable message associated with the error. | Yes |  |
| └─ hate | AzureContentFilterSeverityResult | A labeled content filter result item that indicates whether the content was filtered and what the qualitativeseverity level of the content was, as evaluated against content filter configuration for the category. | No |  |
| └─ filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| └─ severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |
| └─ indirect\_attack | AzureContentFilterDetectionResult | A labeled content filter result item that indicates whether the content was detected and whether the content wasfiltered. | Yes |  |
| └─ detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| └─ filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |
| └─ jailbreak | AzureContentFilterDetectionResult | A labeled content filter result item that indicates whether the content was detected and whether the content wasfiltered. | Yes |  |
| └─ detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| └─ filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |
| └─ profanity | AzureContentFilterDetectionResult | A labeled content filter result item that indicates whether the content was detected and whether the content wasfiltered. | No |  |
| └─ detected | boolean | Whether the labeled content category was detected in the content. | Yes |  |
| └─ filtered | boolean | Whether the content detection resulted in a content filtering action. | Yes |  |
| └─ self\_harm | AzureContentFilterSeverityResult | A labeled content filter result item that indicates whether the content was filtered and what the qualitativeseverity level of the content was, as evaluated against content filter configuration for the category. | No |  |
| └─ filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| └─ severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |
| └─ sexual | AzureContentFilterSeverityResult | A labeled content filter result item that indicates whether the content was filtered and what the qualitativeseverity level of the content was, as evaluated against content filter configuration for the category. | No |  |
| └─ filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| └─ severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |
| └─ violence | AzureContentFilterSeverityResult | A labeled content filter result item that indicates whether the content was filtered and what the qualitativeseverity level of the content was, as evaluated against content filter configuration for the category. | No |  |
| └─ filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| └─ severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |
| prompt\_index | integer (int32) | The index of the input prompt associated with the accompanying content filter result categories. | No |  |

### AzureContentFilterSeverityResult

A labeled content filter result item that indicates whether the content was filtered and what the qualitative severity level of the content was, as evaluated against content filter configuration for the category.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| filtered | boolean | Whether the content severity resulted in a content filtering action. | Yes |  |
| severity | enum | The labeled severity of the content.Possible values: `safe`, `low`, `medium`, `high` | Yes |  |

### AzurePiiSubCategoryResult

Result details for individual PIIHarmSubCategory(s).

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| detected | boolean | Whether the labeled content subcategory was detected in the content. | Yes |  |
| filtered | boolean | Whether the content detection resulted in a content filtering action for this subcategory. | Yes |  |
| redacted | boolean | Whether the content was redacted for this subcategory. | Yes |  |
| sub\_category | string | The PIIHarmSubCategory that was evaluated. | Yes |  |

### AzureUserSecurityContext

User security context contains several parameters that describe the application itself, and the end user that interacts with the application. These fields assist your security operations teams to investigate and mitigate security incidents by providing a comprehensive approach to protecting your AI applications. [Learn more](https://aka.ms/TP4AI/Documentation/EndUserContext) about protecting AI applications using Microsoft Defender for Cloud.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| application\_name | string | The name of the application. Sensitive personal information should not be included in this field. | No |  |
| end\_user\_id | string | This identifier is the Microsoft Entra ID (formerly Azure Active Directory) user object ID used to authenticate end-users within the generative AI application. Sensitive personal information should not be included in this field. | No |  |
| end\_user\_tenant\_id | string | The Microsoft 365 tenant ID the end user belongs to. It's required when the generative AI application is multitenant. | No |  |
| source\_ip | string | Captures the original client's IP address. | No |  |

### OpenAI.ChatCompletionAllowedTools

*Allowed tools*

Constrains the tools available to the model to a pre-defined set.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| mode | enum | Constrains the tools available to the model to a pre-defined set.`auto` allows the model to pick from among the allowed tools and generate a message.`required` requires the model to call one or more of the allowed tools.Possible values: `auto`, `required` | Yes |  |
| tools | array of object | A list of tool definitions that the model should be allowed to call. For the Chat Completions API, the list of tool definitions might look like:`json
  [ { "type": "function", "function": { "name": "get_weather" } }, { "type": "function", "function": { "name": "get_time" } } ]
  ` | Yes |  |

### OpenAI.ChatCompletionAllowedToolsChoice

*Allowed tools*

Constrains the tools available to the model to a pre-defined set.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| allowed\_tools | OpenAI.ChatCompletionAllowedTools | Constrains the tools available to the model to a pre-defined set. | Yes |  |
| type | enum | Allowed tool configuration type. Always `allowed_tools`.Possible values: `allowed_tools` | Yes |  |

### OpenAI.ChatCompletionFunctionCallOption

Specifying a particular function via `{"name": "my_function"}` forces the model to call that function.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| name | string | The name of the function to call. | Yes |  |

### OpenAI.ChatCompletionFunctions

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| description | string | A description of what the function does, used by the model to choose when and how to call the function. | No |  |
| name | string | The name of the function to be called. Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length of 64. | Yes |  |
| parameters | OpenAI.FunctionParameters | The parameters the functions accepts, described as a JSON Schema object. See the JSON Schema reference for documentation about the format.Omitting `parameters` defines a function with an empty parameter list. | No |  |

### OpenAI.ChatCompletionMessageCustomToolCall

*Custom tool call*

A call to a custom tool created by the model.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| custom | OpenAI.ChatCompletionMessageCustomToolCallCustom |  | Yes |  |
| └─ input | string |  | Yes |  |
| └─ name | string |  | Yes |  |
| id | string | The ID of the tool call. | Yes |  |
| type | enum | The type of the tool. Always `custom`.Possible values: `custom` | Yes |  |

### OpenAI.ChatCompletionMessageCustomToolCallCustom

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| input | string |  | Yes |  |
| name | string |  | Yes |  |

### OpenAI.ChatCompletionMessageToolCall

*Function tool call*

A call to a function tool created by the model.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| function | OpenAI.ChatCompletionMessageToolCallFunction |  | Yes |  |
| └─ arguments | string |  | Yes |  |
| └─ name | string |  | Yes |  |
| id | string | The ID of the tool call. | Yes |  |
| type | enum | The type of the tool. Currently, only `function` is supported.Possible values: `function` | Yes |  |

### OpenAI.ChatCompletionMessageToolCallChunk

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| function | OpenAI.ChatCompletionMessageToolCallChunkFunction |  | No |  |
| id | string | The ID of the tool call. | No |  |
| index | integer |  | Yes |  |
| type | enum | The type of the tool. Currently, only `function` is supported.Possible values: `function` | No |  |

### OpenAI.ChatCompletionMessageToolCallChunkFunction

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| arguments | string |  | No |  |
| name | string |  | No |  |

### OpenAI.ChatCompletionMessageToolCallFunction

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| arguments | string |  | Yes |  |
| name | string |  | Yes |  |

### OpenAI.ChatCompletionMessageToolCalls

The tool calls generated by the model, such as function calls.

### OpenAI.ChatCompletionMessageToolCallsItem

The tool calls generated by the model, such as function calls.

### OpenAI.ChatCompletionNamedToolChoice

*Function tool choice*

Specifies a tool the model should use. Use to force the model to call a specific function.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| function | OpenAI.ChatCompletionNamedToolChoiceFunction |  | Yes |  |
| type | enum | For function calling, the type is always `function`.Possible values: `function` | Yes |  |

### OpenAI.ChatCompletionNamedToolChoiceCustom

*Custom tool choice*

Specifies a tool the model should use. Use to force the model to call a specific custom tool.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| custom | OpenAI.ChatCompletionNamedToolChoiceCustomCustom |  | Yes |  |
| type | enum | For custom tool calling, the type is always `custom`.Possible values: `custom` | Yes |  |

### OpenAI.ChatCompletionNamedToolChoiceCustomCustom

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| name | string |  | Yes |  |

### OpenAI.ChatCompletionNamedToolChoiceFunction

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| name | string |  | Yes |  |

### OpenAI.ChatCompletionRequestAssistantMessage

*Assistant message*

Messages sent by the model in response to user messages.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| audio | OpenAI.ChatCompletionRequestAssistantMessageAudio or null | Data about a previous audio response from the model. | No |  |
| content | string or array of OpenAI.ChatCompletionRequestAssistantMessageContentPart or null |  | No |  |
| function\_call | OpenAI.ChatCompletionRequestAssistantMessageFunctionCall or null |  | No |  |
| name | string | An optional name for the participant. Provides the model information to differentiate between participants of the same role. | No |  |
| refusal | string or null |  | No |  |
| role | enum | The role of the messages author, in this case `assistant`.Possible values: `assistant` | Yes |  |
| tool\_calls | OpenAI.ChatCompletionMessageToolCalls | The tool calls generated by the model, such as function calls. | No |  |

### OpenAI.ChatCompletionRequestAssistantMessageAudio

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| id | string |  | Yes |  |

### OpenAI.ChatCompletionRequestAssistantMessageContentPart

### Discriminator for OpenAI.ChatCompletionRequestAssistantMessageContentPart

This component uses the property `type` to discriminate between different types:

| Type Value | Schema |
| --- | --- |
| `refusal` | OpenAI.ChatCompletionRequestMessageContentPartRefusal |
| `text` | OpenAI.ChatCompletionRequestAssistantMessageContentPartChatCompletionRequestMessageContentPartText |

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| type | OpenAI.ChatCompletionRequestAssistantMessageContentPartType |  | Yes |  |

### OpenAI.ChatCompletionRequestAssistantMessageContentPartChatCompletionRequestMessageContentPartText

*Text content part*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| text | string | The text content. | Yes |  |
| type | enum | The type of the content part.Possible values: `text` | Yes |  |

### OpenAI.ChatCompletionRequestAssistantMessageContentPartType

| Property | Value |
| --- | --- |
| **Type** | string |
| **Values** | `text``refusal` |

### OpenAI.ChatCompletionRequestAssistantMessageFunctionCall

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| arguments | string |  | Yes |  |
| name | string |  | Yes |  |

### OpenAI.ChatCompletionRequestDeveloperMessage

*Developer message*

Developer-provided instructions that the model should follow, regardless of messages sent by the user. With o1 models and newer, `developer` messages replace the previous `system` messages.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | string or array of OpenAI.ChatCompletionRequestMessageContentPartText | The contents of the developer message. | Yes |  |
| name | string | An optional name for the participant. Provides the model information to differentiate between participants of the same role. | No |  |
| role | enum | The role of the messages author, in this case `developer`.Possible values: `developer` | Yes |  |

### OpenAI.ChatCompletionRequestFunctionMessage

*Function message*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | string or null |  | Yes |  |
| name | string | The name of the function to call. | Yes |  |
| role | enum | The role of the messages author, in this case `function`.Possible values: `function` | Yes |  |

### OpenAI.ChatCompletionRequestMessage

### Discriminator for OpenAI.ChatCompletionRequestMessage

This component uses the property `role` to discriminate between different types:

| Type Value | Schema |
| --- | --- |
| `assistant` | OpenAI.ChatCompletionRequestAssistantMessage |
| `developer` | OpenAI.ChatCompletionRequestDeveloperMessage |
| `function` | OpenAI.ChatCompletionRequestFunctionMessage |
| `system` | OpenAI.ChatCompletionRequestSystemMessage |
| `user` | OpenAI.ChatCompletionRequestUserMessage |
| `tool` | OpenAI.ChatCompletionRequestToolMessage |

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| role | OpenAI.ChatCompletionRequestMessageType |  | Yes |  |

### OpenAI.ChatCompletionRequestMessageContentPartAudio

*Audio content part*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| input\_audio | OpenAI.ChatCompletionRequestMessageContentPartAudioInputAudio |  | Yes |  |
| type | enum | The type of the content part. Always `input_audio`.Possible values: `input_audio` | Yes |  |

### OpenAI.ChatCompletionRequestMessageContentPartAudioInputAudio

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| data | string |  | Yes |  |
| format | enum | Possible values: `wav`, `mp3` | Yes |  |

### OpenAI.ChatCompletionRequestMessageContentPartFile

*File content part*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| file | OpenAI.ChatCompletionRequestMessageContentPartFileFile |  | Yes |  |
| type | enum | The type of the content part. Always `file`.Possible values: `file` | Yes |  |

### OpenAI.ChatCompletionRequestMessageContentPartFileFile

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| file\_data | string |  | No |  |
| file\_id | string |  | No |  |
| filename | string |  | No |  |

### OpenAI.ChatCompletionRequestMessageContentPartImage

*Image content part*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| image\_url | OpenAI.ChatCompletionRequestMessageContentPartImageImageUrl |  | Yes |  |
| type | enum | The type of the content part.Possible values: `image_url` | Yes |  |

### OpenAI.ChatCompletionRequestMessageContentPartImageImageUrl

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| detail | enum | Possible values: `auto`, `low`, `high` | No | auto |
| url | string (uri) |  | Yes |  |

### OpenAI.ChatCompletionRequestMessageContentPartRefusal

*Refusal content part*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| refusal | string | The refusal message generated by the model. | Yes |  |
| type | enum | The type of the content part.Possible values: `refusal` | Yes |  |

### OpenAI.ChatCompletionRequestMessageContentPartText

*Text content part*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| text | string | The text content. | Yes |  |
| type | enum | The type of the content part.Possible values: `text` | Yes |  |

### OpenAI.ChatCompletionRequestMessageType

| Property | Value |
| --- | --- |
| **Type** | string |
| **Values** | `developer``system``user``assistant``tool``function` |

### OpenAI.ChatCompletionRequestSystemMessage

*System message*

Developer-provided instructions that the model should follow, regardless of messages sent by the user. With o1 models and newer, use `developer` messages for this purpose instead.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | string or array of OpenAI.ChatCompletionRequestSystemMessageContentPart | The contents of the system message. | Yes |  |
| name | string | An optional name for the participant. Provides the model information to differentiate between participants of the same role. | No |  |
| role | enum | The role of the messages author, in this case `system`.Possible values: `system` | Yes |  |

### OpenAI.ChatCompletionRequestSystemMessageContentPart

References: OpenAI.ChatCompletionRequestMessageContentPartText

### OpenAI.ChatCompletionRequestToolMessage

*Tool message*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | string or array of OpenAI.ChatCompletionRequestToolMessageContentPart | The contents of the tool message. | Yes |  |
| role | enum | The role of the messages author, in this case `tool`.Possible values: `tool` | Yes |  |
| tool\_call\_id | string | Tool call that this message is responding to. | Yes |  |

### OpenAI.ChatCompletionRequestToolMessageContentPart

References: OpenAI.ChatCompletionRequestMessageContentPartText

### OpenAI.ChatCompletionRequestUserMessage

*User message*

Messages sent by an end user, containing prompts or additional context information.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | string or array of OpenAI.ChatCompletionRequestUserMessageContentPart | The contents of the user message. | Yes |  |
| name | string | An optional name for the participant. Provides the model information to differentiate between participants of the same role. | No |  |
| role | enum | The role of the messages author, in this case `user`.Possible values: `user` | Yes |  |

### OpenAI.ChatCompletionRequestUserMessageContentPart

### Discriminator for OpenAI.ChatCompletionRequestUserMessageContentPart

This component uses the property `type` to discriminate between different types:

| Type Value | Schema |
| --- | --- |
| `image_url` | OpenAI.ChatCompletionRequestMessageContentPartImage |
| `input_audio` | OpenAI.ChatCompletionRequestMessageContentPartAudio |
| `file` | OpenAI.ChatCompletionRequestMessageContentPartFile |
| `text` | OpenAI.ChatCompletionRequestUserMessageContentPartChatCompletionRequestMessageContentPartText |

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| type | OpenAI.ChatCompletionRequestUserMessageContentPartType |  | Yes |  |

### OpenAI.ChatCompletionRequestUserMessageContentPartChatCompletionRequestMessageContentPartText

*Text content part*

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| text | string | The text content. | Yes |  |
| type | enum | The type of the content part.Possible values: `text` | Yes |  |

### OpenAI.ChatCompletionRequestUserMessageContentPartType

| Property | Value |
| --- | --- |
| **Type** | string |
| **Values** | `text``image_url``input_audio``file` |

### OpenAI.ChatCompletionResponseMessage

If the audio output modality is requested, this object contains data about the audio response from the model.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| annotations | array of OpenAI.ChatCompletionResponseMessageAnnotations | Annotations for the message, when applicable, as when using the web search tool. | No |  |
| audio | OpenAI.ChatCompletionResponseMessageAudio or null |  | No |  |
| content | string or null |  | Yes |  |
| function\_call | OpenAI.ChatCompletionResponseMessageFunctionCall (deprecated) |  | No |  |
| └─ arguments | string |  | Yes |  |
| └─ name | string |  | Yes |  |
| reasoning\_content | string | An Azure-specific extension property containing generated reasoning content from supported models. | No |  |
| refusal | string or null |  | Yes |  |
| role | enum | The role of the author of this message.Possible values: `assistant` | Yes |  |
| tool\_calls | OpenAI.ChatCompletionMessageToolCallsItem | The tool calls generated by the model, such as function calls. | No |  |

### OpenAI.ChatCompletionResponseMessageAnnotations

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| type | enum | Possible values: `url_citation` | Yes |  |
| url\_citation | OpenAI.ChatCompletionResponseMessageAnnotationsUrlCitation |  | Yes |  |

### OpenAI.ChatCompletionResponseMessageAnnotationsUrlCitation

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| end\_index | integer |  | Yes |  |
| start\_index | integer |  | Yes |  |
| title | string |  | Yes |  |
| url | string (uri) |  | Yes |  |

### OpenAI.ChatCompletionResponseMessageAudio

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| data | string |  | Yes |  |
| expires\_at | integer (unixtime) |  | Yes |  |
| id | string |  | Yes |  |
| transcript | string |  | Yes |  |

### OpenAI.ChatCompletionResponseMessageFunctionCall

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| arguments | string |  | Yes |  |
| name | string |  | Yes |  |

### OpenAI.ChatCompletionStreamOptions

Options for streaming response. Only set this when you set `stream: true`.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| include\_obfuscation | boolean | When true, stream obfuscation will be enabled. Stream obfuscation adds random characters to an `obfuscation` field on streaming delta events to normalize payload sizes as a mitigation to certain side-channel attacks. These obfuscation fields are included by default, but add a small amount of overhead to the data stream. You can set `include_obfuscation` to false to optimize for bandwidth if you trust the network links between your application and the OpenAI API. | No |  |
| include\_usage | boolean | If set, an additional chunk will be streamed before the `data: [DONE]` message. The `usage` field on this chunk shows the token usage statistics for the entire request, and the `choices` field will always be an empty array. All other chunks will also include a `usage` field, but with a null value. **NOTE:** If the stream is interrupted, you may not receive the final usage chunk which contains the total token usage for the request. | No |  |

### OpenAI.ChatCompletionStreamResponseDelta

A chat completion delta generated by streamed model responses.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | string or null |  | No |  |
| function\_call | OpenAI.ChatCompletionStreamResponseDeltaFunctionCall (deprecated) |  | No |  |
| └─ arguments | string |  | No |  |
| └─ name | string |  | No |  |
| reasoning\_content | string | An Azure-specific extension property containing generated reasoning content from supported models. | No |  |
| refusal | string or null |  | No |  |
| role | enum | The role of the author of this message.Possible values: `developer`, `system`, `user`, `assistant`, `tool` | No |  |
| tool\_calls | array of OpenAI.ChatCompletionMessageToolCallChunk |  | No |  |

### OpenAI.ChatCompletionStreamResponseDeltaFunctionCall

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| arguments | string |  | No |  |
| name | string |  | No |  |

### OpenAI.ChatCompletionTokenLogprob

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| bytes | array of integer or null |  | Yes |  |
| logprob | number | The log probability of this token, if it is within the top 20 most likely tokens. Otherwise, the value `-9999.0` is used to signify that the token is very unlikely. | Yes |  |
| token | string | The token. | Yes |  |
| top\_logprobs | array of OpenAI.ChatCompletionTokenLogprobTopLogprobs | List of the most likely tokens and their log probability, at this token position. The number of entries may be fewer than the requested `top_logprobs`. | Yes |  |

### OpenAI.ChatCompletionTokenLogprobTopLogprobs

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| bytes | array of integer or null |  | Yes |  |
| logprob | number |  | Yes |  |
| token | string |  | Yes |  |

### OpenAI.ChatCompletionTool

*Function tool*

A function tool that can be used to generate a response.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| function | OpenAI.FunctionObject |  | Yes |  |
| type | enum | The type of the tool. Currently, only `function` is supported.Possible values: `function` | Yes |  |

### OpenAI.ChatCompletionToolChoiceOption

Controls which (if any) tool is called by the model. `none` means the model will not call any tool and instead generates a message. `auto` means the model can pick between generating a message or calling one or more tools. `required` means the model must call one or more tools. Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool. `none` is the default when no tools are present. `auto` is the default if tools are present.

This component can be one of the following:

- **string**: `none`, `auto`, `required`
- OpenAI.ChatCompletionAllowedToolsChoice
- OpenAI.ChatCompletionNamedToolChoice
- OpenAI.ChatCompletionNamedToolChoiceCustom

### OpenAI.CompletionUsage

Usage statistics for the completion request.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| completion\_tokens | integer | Number of tokens in the generated completion. | Yes |  |
| completion\_tokens\_details | OpenAI.CompletionUsageCompletionTokensDetails |  | No |  |
| └─ accepted\_prediction\_tokens | integer |  | No |  |
| └─ audio\_tokens | integer |  | No |  |
| └─ reasoning\_tokens | integer |  | No |  |
| └─ rejected\_prediction\_tokens | integer |  | No |  |
| prompt\_tokens | integer | Number of tokens in the prompt. | Yes |  |
| prompt\_tokens\_details | OpenAI.CompletionUsagePromptTokensDetails |  | No |  |
| └─ audio\_tokens | integer |  | No |  |
| └─ cached\_tokens | integer |  | No |  |
| total\_tokens | integer | Total number of tokens used in the request (prompt + completion). | Yes |  |

### OpenAI.CompletionUsageCompletionTokensDetails

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| accepted\_prediction\_tokens | integer |  | No |  |
| audio\_tokens | integer |  | No |  |
| reasoning\_tokens | integer |  | No |  |
| rejected\_prediction\_tokens | integer |  | No |  |

### OpenAI.CompletionUsagePromptTokensDetails

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| audio\_tokens | integer |  | No |  |
| cached\_tokens | integer |  | No |  |

### OpenAI.CreateChatCompletionRequestAudio

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| format | enum | Possible values: `wav`, `aac`, `mp3`, `flac`, `opus`, `pcm16` | Yes |  |
| voice | OpenAI.VoiceIdsOrCustomVoice | A built-in voice name or a custom voice reference. | Yes |  |

### OpenAI.CreateChatCompletionRequestResponseFormat

An object specifying the format that the model must output. Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the Structured Outputs guide. Setting to `{ "type": "json_object" }` enables the older JSON mode, which ensures the message the model generates is valid JSON. Using `json_schema` is preferred for models that support it.

### Discriminator for OpenAI.CreateChatCompletionRequestResponseFormat

This component uses the property `type` to discriminate between different types:

| Type Value | Schema |
| --- | --- |
| `json_schema` | OpenAI.ResponseFormatJsonSchema |
| `text` | OpenAI.CreateChatCompletionRequestResponseFormatResponseFormatText |
| `json_object` | OpenAI.CreateChatCompletionRequestResponseFormatResponseFormatJsonObject |

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| type | OpenAI.CreateChatCompletionRequestResponseFormatType |  | Yes |  |

### OpenAI.CreateChatCompletionRequestResponseFormatResponseFormatJsonObject

*JSON object*

JSON object response format. An older method of generating JSON responses. Using `json_schema` is recommended for models that support it. Note that the model will not generate JSON without a system or user message instructing it to do so.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| type | enum | The type of response format being defined. Always `json_object`.Possible values: `json_object` | Yes |  |

### OpenAI.CreateChatCompletionRequestResponseFormatResponseFormatText

*Text*

Default response format. Used to generate text responses.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| type | enum | The type of response format being defined. Always `text`.Possible values: `text` | Yes |  |

### OpenAI.CreateChatCompletionRequestResponseFormatType

| Property | Value |
| --- | --- |
| **Type** | string |
| **Values** | `text``json_schema``json_object` |

### OpenAI.CreateChatCompletionResponseChoices

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content\_filter\_results | AzureContentFilterResultForChoice | A content filter result for a single response item produced by a generative AI system. | No |  |
| finish\_reason | enum | Possible values: `stop`, `length`, `tool_calls`, `content_filter`, `function_call` | Yes |  |
| index | integer |  | Yes |  |
| logprobs | OpenAI.CreateChatCompletionResponseChoicesLogprobs or null |  | Yes |  |
| message | OpenAI.ChatCompletionResponseMessage | If the audio output modality is requested, this object contains dataabout the audio response from the model. | Yes |  |

### OpenAI.CreateChatCompletionResponseChoicesLogprobs

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | array of OpenAI.ChatCompletionTokenLogprob or null |  | Yes |  |
| refusal | array of OpenAI.ChatCompletionTokenLogprob or null |  | Yes |  |

### OpenAI.CreateChatCompletionStreamResponseChoices

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| delta | OpenAI.ChatCompletionStreamResponseDelta | A chat completion delta generated by streamed model responses. | Yes |  |
| finish\_reason | string or null |  | Yes |  |
| index | integer |  | Yes |  |
| logprobs | OpenAI.CreateChatCompletionStreamResponseChoicesLogprobs or null |  | No |  |

### OpenAI.CreateChatCompletionStreamResponseChoicesLogprobs

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | array of OpenAI.ChatCompletionTokenLogprob or null |  | Yes |  |
| refusal | array of OpenAI.ChatCompletionTokenLogprob or null |  | Yes |  |

### OpenAI.CustomToolChatCompletions

*Custom tool*

A custom tool that processes input using a specified format.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| custom | OpenAI.CustomToolChatCompletionsCustom |  | Yes |  |
| └─ description | string |  | No |  |
| └─ format | OpenAI.CustomToolChatCompletionsCustomFormatText or OpenAI.CustomToolChatCompletionsCustomFormatGrammar |  | No |  |
| └─ name | string |  | Yes |  |
| type | enum | The type of the custom tool. Always `custom`.Possible values: `custom` | Yes |  |

### OpenAI.CustomToolChatCompletionsCustom

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| description | string |  | No |  |
| format | OpenAI.CustomToolChatCompletionsCustomFormatText or OpenAI.CustomToolChatCompletionsCustomFormatGrammar |  | No |  |
| name | string |  | Yes |  |

### OpenAI.CustomToolChatCompletionsCustomFormatGrammar

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| grammar | OpenAI.CustomToolChatCompletionsCustomFormatGrammarGrammar |  | Yes |  |
| └─ definition | string |  | Yes |  |
| └─ syntax | enum | Possible values: `lark`, `regex` | Yes |  |
| type | enum | Possible values: `grammar` | Yes |  |

### OpenAI.CustomToolChatCompletionsCustomFormatGrammarGrammar

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| definition | string |  | Yes |  |
| syntax | enum | Possible values: `lark`, `regex` | Yes |  |

### OpenAI.CustomToolChatCompletionsCustomFormatText

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| type | enum | Possible values: `text` | Yes |  |

### OpenAI.FunctionObject

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| description | string | A description of what the function does, used by the model to choose when and how to call the function. | No |  |
| name | string | The name of the function to be called. Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length of 64. | Yes |  |
| parameters | OpenAI.FunctionParameters | The parameters the functions accepts, described as a JSON Schema object. See the JSON Schema reference for documentation about the format.Omitting `parameters` defines a function with an empty parameter list. | No |  |
| strict | boolean or null |  | No |  |

### OpenAI.FunctionParameters

The parameters the functions accepts, described as a JSON Schema object. See the JSON Schema reference for documentation about the format. Omitting `parameters` defines a function with an empty parameter list.

**Type**: object

### OpenAI.Metadata

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard. Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

**Type**: object

### OpenAI.PredictionContent

*Static Content*

Static predicted output content, such as the content of a text file that is being regenerated.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| content | string or array of OpenAI.ChatCompletionRequestMessageContentPartText | The content that should be matched when generating a model response. If generated tokens would match this content, the entire model response can be returned much more quickly. | Yes |  |
| type | enum | The type of the predicted content you want to provide. This type is currently always `content`.Possible values: `content` | Yes |  |

### OpenAI.ReasoningEffort

Constrains effort on reasoning for reasoning models. Currently supported values are `none`, `minimal`, `low`, `medium`, `high`, and `xhigh`. Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.

- `gpt-5.1` defaults to `none`, which does not perform reasoning. The supported reasoning values for `gpt-5.1` are `none`, `low`, `medium`, and `high`. Tool calls are supported for all reasoning values in gpt-5.1.
- All models before `gpt-5.1` default to `medium` reasoning effort, and do not support `none`.
- The `gpt-5-pro` model defaults to (and only supports) `high` reasoning effort.
- `xhigh` is supported for all models after `gpt-5.1-codex-max`.

| Property | Value |
| --- | --- |
| **Description** | Constrains effort on reasoning forreasoning models.Currently supported values are `none`, `minimal`, `low`, `medium`, `high`, and `xhigh`. Reducingreasoning effort can result in faster responses and fewer tokens usedon reasoning in a response.- `gpt-5.1` defaults to `none`, which does not perform reasoning. The supported reasoning values for `gpt-5.1` are `none`, `low`, `medium`, and `high`. Tool calls are supported for all reasoning values in gpt-5.1.- All models before `gpt-5.1` default to `medium` reasoning effort, and do not support `none`.- The `gpt-5-pro` model defaults to (and only supports) `high` reasoning effort.- `xhigh` is supported for all models after `gpt-5.1-codex-max`. |
| **Type** | string |
| **Values** | `none``minimal``low``medium``high``xhigh` |

### OpenAI.ResponseFormatJsonSchema

*JSON schema*

JSON Schema response format. Used to generate structured JSON responses.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| json\_schema | OpenAI.ResponseFormatJsonSchemaJsonSchema |  | Yes |  |
| └─ description | string |  | No |  |
| └─ name | string |  | Yes |  |
| └─ schema | OpenAI.ResponseFormatJsonSchemaSchema | The schema for the response format, described as a JSON Schema object.Learn how to build JSON schemas [here](https://json-schema.org/). | No |  |
| └─ strict | boolean or null |  | No |  |
| type | enum | The type of response format being defined. Always `json_schema`.Possible values: `json_schema` | Yes |  |

### OpenAI.ResponseFormatJsonSchemaJsonSchema

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| description | string |  | No |  |
| name | string |  | Yes |  |
| schema | OpenAI.ResponseFormatJsonSchemaSchema | The schema for the response format, described as a JSON Schema object.Learn how to build JSON schemas [here](https://json-schema.org/). | No |  |
| strict | boolean or null |  | No |  |

### OpenAI.ResponseFormatJsonSchemaSchema

*JSON schema*

The schema for the response format, described as a JSON Schema object. Learn how to build JSON schemas [here](https://json-schema.org/).

**Type**: object

### OpenAI.ResponseModalities

Output types that you would like the model to generate. Most models are capable of generating text, which is the default: `["text"]` The `gpt-4o-audio-preview` model can also be used to generate audio. To request that this model generate both text and audio responses, you can use: `["text", "audio"]`

This schema accepts one of the following types:

- **array**
- **null**

### OpenAI.StopConfiguration

Not supported with latest reasoning models `o3` and `o4-mini`. Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.

This component can be one of the following:

- **string**
- **array**

### OpenAI.Verbosity

Constrains the verbosity of the model's response. Lower values will result in more concise responses, while higher values will result in more verbose responses. Currently supported values are `low`, `medium`, and `high`.

| Property | Value |
| --- | --- |
| **Description** | Constrains the verbosity of the model's response. Lower values will result inmore concise responses, while higher values will result in more verbose responses.Currently supported values are `low`, `medium`, and `high`. |
| **Type** | string |
| **Values** | `low``medium``high` |

### OpenAI.VoiceIdsOrCustomVoice

*Voice*

A built-in voice name or a custom voice reference.

**Type**: OpenAI.VoiceIdsShared or object

A built-in voice name or a custom voice reference.

### OpenAI.VoiceIdsShared

| Property | Value |
| --- | --- |
| **Type** | string |
| **Values** | `alloy``ash``ballad``coral``echo``sage``shimmer``verse``marin``cedar` |
