---
layout: Conceptual
title: Azure OpenAI image and audio REST API reference (2024-10-21) - Microsoft Foundry | Microsoft Learn
canonicalUrl: https://learn.microsoft.com/en-us/azure/foundry/openai/reference
breadcrumb_path: ../../breadcrumb/azure-ai/toc.json
feedback_help_link_url: https://learn.microsoft.com/answers/tags/133/azure
feedback_help_link_type: get-help-at-qna
feedback_product_url: https://feedback.azure.com/d365community/forum/79b1327d-d925-ec11-b6e6-000d3a4f06a4
feedback_system: Standard
permissioned-type: public
recommendations: false
recommendation_types:
- Training
- Certification
uhfHeaderId: azure-ai-foundry
ms.suite: office
author: alvinashcraft
learn_banner_products:
- azure
manager: mcleans
ms.author: aashcraft
ms.collection: ce-skilling-ai-copilot
ms.update-cycle: 90-days
ms.service: microsoft-foundry
description: Reference for the Azure OpenAI image generation and audio (speech) REST API operations in the 2024-10-21 GA release.
ms.subservice: foundry-openai
ms.topic: reference
ms.date: 2026-05-19T00:00:00.0000000Z
ai-usage: ai-assisted
ms.custom:
- classic-and-new
- ignite-2023
- doc-kit-assisted
locale: en-us
document_id: 8881f459-b48c-ab9a-64a9-ce5fac39212d
document_version_independent_id: 6e4e1104-a441-8d65-b7d9-ee6dcc9a255c
updated_at: 2026-06-24T22:12:00.0000000Z
original_content_git_url: https://github.com/MicrosoftDocs/azure-ai-docs-pr/blob/live/articles/foundry/openai/reference.md
gitcommit: https://github.com/MicrosoftDocs/azure-ai-docs-pr/blob/4bf7fd09d1f07de2f941412e0154c99cc263ccc1/articles/foundry/openai/reference.md
git_commit_id: 4bf7fd09d1f07de2f941412e0154c99cc263ccc1
site_name: Docs
depot_name: Learn.azure-ai
page_type: conceptual
toc_rel: ../toc.json
word_count: 1975
asset_id: foundry/openai/reference
moniker_range_name:
monikers: []
item_type: Content
source_path: articles/foundry/openai/reference.md
cmProducts:
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/8a6e4dad-7050-4ce7-83f9-eb4123577a54
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/c6f99e62-1cf6-4b71-af9b-649b05f80cce
spProducts:
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/0a5fc323-00ce-4c20-9095-41948f54c83f
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/3f56b378-07a9-4fa1-afe8-9889fdc77628
platformId: eea42959-b14d-4884-8e91-a240feabd3df
---

# Azure OpenAI image and audio REST API reference (2024-10-21) - Microsoft Foundry | Microsoft Learn

This article documents the image generation and audio (speech) data plane inference REST API operations for Azure OpenAI in the `2024-10-21` GA release. For chat completions, embeddings, completions, and all other operations, see the [official Azure OpenAI REST API reference](/en-us/rest/api/microsoft-foundry/azureopenai/chat?view=rest-microsoft-foundry-2024-10-21&preserve-view=true).

## API specs

Managing and interacting with Azure OpenAI models and resources is divided across three primary API surfaces:

- Control plane
- Data plane - authoring
- Data plane - inference

Each API surface/specification encapsulates a different set of Azure OpenAI capabilities. Each API has its own unique set of preview and stable/generally available (GA) API releases. Preview releases currently tend to follow a monthly cadence.

Important

There is now a new preview inference API. Learn more in our [API lifecycle guide](api-version-lifecycle#api-evolution).

| API | Latest preview release | Latest GA release | Specifications | Description |
| --- | --- | --- | --- | --- |
| **Control plane** | `2025-07-01-preview` | [`2025-06-01`](/en-us/rest/api/microsoftfoundry/accountmanagement/operation-groups?view=rest-microsoftfoundry-accountmanagement-2025-06-01&preserve-view=true) | [Spec files](https://github.com/Azure/azure-rest-api-specs/blob/main/specification/cognitiveservices/resource-manager/Microsoft.CognitiveServices/stable/2025-06-01/cognitiveservices.json) | The control plane API is used for operations like [creating resources](/en-us/rest/api/microsoftfoundry/accountmanagement/accounts/create?view=rest-microsoftfoundry-accountmanagement-2025-06-01&tabs=HTTP&preserve-view=true), [model deployment](/en-us/rest/api/microsoftfoundry/accountmanagement/deployments/create-or-update?view=rest-microsoftfoundry-accountmanagement-2025-06-01&tabs=HTTP&preserve-view=true), and other higher level resource management tasks. The control plane also governs what is possible to do with capabilities like Azure Resource Manager, Bicep, Terraform, and Azure CLI. |
| **Data plane** | [`v1 preview`](/en-us/rest/api/microsoft-foundry/azureopenai/chat?view=rest-microsoft-foundry-v1-preview&preserve-view=true) | [`v1`](/en-us/rest/api/microsoft-foundry/azureopenai/chat?view=rest-microsoft-foundry-v1&preserve-view=true) | [Spec files](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/ai/data-plane/OpenAI.v1) | The data plane API controls inference and authoring operations. |

## Authentication

Azure OpenAI provides two methods for authentication. You can use either API Keys or Microsoft Entra ID.

- **API Key authentication**: For this type of authentication, all API requests must include the API Key in the `api-key` HTTP header. The [Quickstart](how-to/responses) provides guidance for how to make calls with this type of authentication.
- **Microsoft Entra ID authentication**: You can authenticate an API call using a Microsoft Entra token. Authentication tokens are included in a request as the `Authorization` header. The token provided must be preceded by `Bearer`, for example `Bearer YOUR_AUTH_TOKEN`. You can read our how-to guide on [authenticating with Microsoft Entra ID](../../foundry-classic/openai/how-to/managed-identity).

### REST API versioning

The service APIs are versioned using the `api-version` query parameter. All versions follow the YYYY-MM-DD date structure. For example:

```http
POST https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME/chat/completions?api-version=2024-06-01
```

## Data plane inference

The rest of this article covers the image and audio operations in the GA release of the Azure OpenAI data plane inference specification, `2024-10-21`.

For the preview image and audio operations, see the [preview image and audio REST API reference](reference-preview).

## Transcriptions - Create

```HTTP
POST https://{endpoint}/openai/deployments/{deployment-id}/audio/transcriptions?api-version=2024-10-21
```

Transcribes audio into the input language.

### URI Parameters

| Name | In | Required | Type | Description |
| --- | --- | --- | --- | --- |
| endpoint | path | Yes | stringurl | Supported Azure OpenAI endpoints (protocol and hostname, for example: `https://aoairesource.openai.azure.com`. Replace "aoairesource" with your Azure OpenAI resource name). https://{your-resource-name}.openai.azure.com |
| deployment-id | path | Yes | string | Deployment ID of the speech to text model.For information about supported models, see [/azure/ai-foundry/openai/concepts/models#audio-models]. |
| api-version | query | Yes | string | API version |

### Request Header

| Name | Required | Type | Description |
| --- | --- | --- | --- |
| api-key | True | string | Provide Azure OpenAI API key here |

### Request Body

**Content-Type**: multipart/form-data

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| file | string | The audio file object to transcribe. | Yes |  |
| prompt | string | An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language. | No |  |
| response\_format | audioResponseFormat | Defines the format of the output. | No |  |
| temperature | number | The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use log probability to automatically increase the temperature until certain thresholds are hit. | No | 0 |
| language | string | The language of the input audio. Supplying the input language in ISO-639-1 format will improve accuracy and latency. | No |  |

### Responses

**Status Code:** 200

**Description**: OK

| **Content-Type** | **Type** | **Description** |
| --- | --- | --- |
| application/json | audioResponse or audioVerboseResponse |  |
| text/plain | string | Transcribed text in the output format (when response\_format was one of text, vtt or srt). |

### Examples

### Example

Gets transcribed text and associated metadata from provided spoken audio data.

```HTTP
POST https://{endpoint}/openai/deployments/{deployment-id}/audio/transcriptions?api-version=2024-10-21

```

**Responses**: Status Code: 200

```json
{
  "body": {
    "text": "A structured object when requesting json or verbose_json"
  }
}
```

### Example

Gets transcribed text and associated metadata from provided spoken audio data.

```HTTP
POST https://{endpoint}/openai/deployments/{deployment-id}/audio/transcriptions?api-version=2024-10-21

"---multipart-boundary\nContent-Disposition: form-data; name=\"file\"; filename=\"file.wav\"\nContent-Type: application/octet-stream\n\nRIFF..audio.data.omitted\n---multipart-boundary--"

```

**Responses**: Status Code: 200

```json
{
  "type": "string",
  "example": "plain text when requesting text, srt, or vtt"
}
```

## Translations - Create

```HTTP
POST https://{endpoint}/openai/deployments/{deployment-id}/audio/translations?api-version=2024-10-21
```

Transcribes and translates input audio into English text.

### URI Parameters

| Name | In | Required | Type | Description |
| --- | --- | --- | --- | --- |
| endpoint | path | Yes | stringurl | Supported Azure OpenAI endpoints (protocol and hostname, for example: `https://aoairesource.openai.azure.com`. Replace "aoairesource" with your Azure OpenAI resource name). https://{your-resource-name}.openai.azure.com |
| deployment-id | path | Yes | string | Deployment ID of the transcription model which was deployed.For information about supported models, see [/azure/ai-foundry/openai/concepts/models#audio-models]. |
| api-version | query | Yes | string | API version |

### Request Header

| Name | Required | Type | Description |
| --- | --- | --- | --- |
| api-key | True | string | Provide Azure OpenAI API key here |

### Request Body

**Content-Type**: multipart/form-data

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| file | string | The audio file to translate. | Yes |  |
| prompt | string | An optional text to guide the model's style or continue a previous audio segment. The prompt should be in English. | No |  |
| response\_format | audioResponseFormat | Defines the format of the output. | No |  |
| temperature | number | The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use log probability to automatically increase the temperature until certain thresholds are hit. | No | 0 |

### Responses

**Status Code:** 200

**Description**: OK

| **Content-Type** | **Type** | **Description** |
| --- | --- | --- |
| application/json | audioResponse or audioVerboseResponse |  |
| text/plain | string | Transcribed text in the output format (when response\_format was one of text, vtt or srt). |

### Examples

### Example

Gets English language transcribed text and associated metadata from provided spoken audio data.

```HTTP
POST https://{endpoint}/openai/deployments/{deployment-id}/audio/translations?api-version=2024-10-21

"---multipart-boundary\nContent-Disposition: form-data; name=\"file\"; filename=\"file.wav\"\nContent-Type: application/octet-stream\n\nRIFF..audio.data.omitted\n---multipart-boundary--"

```

**Responses**: Status Code: 200

```json
{
  "body": {
    "text": "A structured object when requesting json or verbose_json"
  }
}
```

### Example

Gets English language transcribed text and associated metadata from provided spoken audio data.

```HTTP
POST https://{endpoint}/openai/deployments/{deployment-id}/audio/translations?api-version=2024-10-21

"---multipart-boundary\nContent-Disposition: form-data; name=\"file\"; filename=\"file.wav\"\nContent-Type: application/octet-stream\n\nRIFF..audio.data.omitted\n---multipart-boundary--"

```

**Responses**: Status Code: 200

```json
{
  "type": "string",
  "example": "plain text when requesting text, srt, or vtt"
}
```

## Image generation

```HTTP
POST https://{endpoint}/openai/deployments/{deployment-id}/images/generations?api-version=2024-10-21
```

Generates a batch of images from a text caption on a given dall-e model deployment

### URI Parameters

| Name | In | Required | Type | Description |
| --- | --- | --- | --- | --- |
| endpoint | path | Yes | stringurl | Supported Azure OpenAI endpoints (protocol and hostname, for example: `https://aoairesource.openai.azure.com`. Replace "aoairesource" with your Azure OpenAI resource name). https://{your-resource-name}.openai.azure.com |
| deployment-id | path | Yes | string | Deployment ID of the dall-e model which was deployed. |
| api-version | query | Yes | string | API version |

### Request Header

| Name | Required | Type | Description |
| --- | --- | --- | --- |
| api-key | True | string | Provide Azure OpenAI API key here |

### Request Body

**Content-Type**: application/json

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| prompt | string | A text description of the desired image(s). The maximum length is 4,000 characters. | Yes |  |
| n | integer | The number of images to generate. | No | 1 |
| size | imageSize | The size of the generated images. | No | 1024x1024 |
| response\_format | imagesResponseFormat | The format in which the generated images are returned. | No | url |
| user | string | A unique identifier representing your end-user, which can help to monitor and detect abuse. | No |  |
| quality | imageQuality | The quality of the image that will be generated. | No | standard |
| style | imageStyle | The style of the generated images. | No | vivid |

### Responses

**Status Code:** 200

**Description**: Ok

| **Content-Type** | **Type** | **Description** |
| --- | --- | --- |
| application/json | generateImagesResponse |  |

**Status Code:** default

**Description**: An error occurred.

| **Content-Type** | **Type** | **Description** |
| --- | --- | --- |
| application/json | dalleErrorResponse |  |

### Examples

### Example

Creates images given a prompt.

```HTTP
POST https://{endpoint}/openai/deployments/{deployment-id}/images/generations?api-version=2024-10-21

{
 "prompt": "In the style of WordArt, Microsoft Clippy wearing a cowboy hat.",
 "n": 1,
 "style": "natural",
 "quality": "standard"
}

```

**Responses**: Status Code: 200

```json
{
  "body": {
    "created": 1698342300,
    "data": [
      {
        "revised_prompt": "A vivid, natural representation of Microsoft Clippy wearing a cowboy hat.",
        "prompt_filter_results": {
          "sexual": {
            "severity": "safe",
            "filtered": false
          },
          "violence": {
            "severity": "safe",
            "filtered": false
          },
          "hate": {
            "severity": "safe",
            "filtered": false
          },
          "self_harm": {
            "severity": "safe",
            "filtered": false
          },
          "profanity": {
            "detected": false,
            "filtered": false
          }
        },
        "url": "https://dalletipusw2.blob.core.windows.net/private/images/e5451cc6-b1ad-4747-bd46-b89a3a3b8bc3/generated_00.png?se=2023-10-27T17%3A45%3A09Z&...",
        "content_filter_results": {
          "sexual": {
            "severity": "safe",
            "filtered": false
          },
          "violence": {
            "severity": "safe",
            "filtered": false
          },
          "hate": {
            "severity": "safe",
            "filtered": false
          },
          "self_harm": {
            "severity": "safe",
            "filtered": false
          }
        }
      }
    ]
  }
}
```

## Components

For the schema definitions used by chat, completions, embeddings, and other text operations, see the [Azure OpenAI REST API reference](/en-us/rest/api/microsoft-foundry/azureopenai/chat?view=rest-microsoft-foundry-v1&preserve-view=true). The following schemas support the image and audio operations on this page.

### innerErrorCode

Error codes for the inner error object.

**Description**: Error codes for the inner error object.

**Type**: string

**Default**:

**Enum Name**: InnerErrorCode

**Enum Values**:

| Value | Description |
| --- | --- |
| ResponsibleAIPolicyViolation | The prompt violated one of more content filter rules. |

### dalleErrorResponse

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| error | dalleError |  | No |  |

### dalleError

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| param | string |  | No |  |
| type | string |  | No |  |
| inner\_error | dalleInnerError | Inner error with additional details. | No |  |

### dalleInnerError

Inner error with additional details.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| code | innerErrorCode | Error codes for the inner error object. | No |  |
| content\_filter\_results | dalleFilterResults | Information about the content filtering category (hate, sexual, violence, self\_harm), if it has been detected, as well as the severity level (very\_low, low, medium, high-scale that determines the intensity and risk level of harmful content) and if it has been filtered or not. Information about jailbreak content and profanity, if it has been detected, and if it has been filtered or not. And information about customer blocklist, if it has been filtered and its id. | No |  |
| revised\_prompt | string | The prompt that was used to generate the image, if there was any revision to the prompt. | No |  |

### contentFilterSeverityResult

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| filtered | boolean |  | Yes |  |
| severity | string |  | No |  |

### contentFilterDetectedResult

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| filtered | boolean |  | Yes |  |
| detected | boolean |  | No |  |

### dalleFilterResults

Information about the content filtering category (hate, sexual, violence, self\_harm), if it has been detected, as well as the severity level (very\_low, low, medium, high-scale that determines the intensity and risk level of harmful content) and if it has been filtered or not. Information about jailbreak content and profanity, if it has been detected, and if it has been filtered or not. And information about customer blocklist, if it has been filtered and its id.

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| sexual | contentFilterSeverityResult |  | No |  |
| violence | contentFilterSeverityResult |  | No |  |
| hate | contentFilterSeverityResult |  | No |  |
| self\_harm | contentFilterSeverityResult |  | No |  |
| profanity | contentFilterDetectedResult |  | No |  |
| jailbreak | contentFilterDetectedResult |  | No |  |

### audioResponse

Translation or transcription response when response\_format was json

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| text | string | Translated or transcribed text. | Yes |  |

### audioVerboseResponse

Translation or transcription response when response\_format was verbose\_json

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| text | string | Translated or transcribed text. | Yes |  |
| task | string | Type of audio task. | No |  |
| language | string | Language. | No |  |
| duration | number | Duration. | No |  |
| segments | array |  | No |  |

### audioResponseFormat

Defines the format of the output.

**Description**: Defines the format of the output.

**Type**: string

**Default**:

**Enum Values**:

- json
- text
- srt
- verbose\_json
- vtt

### imageQuality

The quality of the image that will be generated.

**Description**: The quality of the image that will be generated.

**Type**: string

**Default**: standard

**Enum Name**: Quality

**Enum Values**:

| Value | Description |
| --- | --- |
| standard | Standard quality creates images with standard quality. |
| hd | HD quality creates images with finer details and greater consistency across the image. |

### imagesResponseFormat

The format in which the generated images are returned.

**Description**: The format in which the generated images are returned.

**Type**: string

**Default**: url

**Enum Name**: ImagesResponseFormat

**Enum Values**:

| Value | Description |
| --- | --- |
| url | The URL that provides temporary access to download the generated images. |
| b64\_json | The generated images are returned as base64 encoded string. |

### imageSize

The size of the generated images.

**Description**: The size of the generated images.

**Type**: string

**Default**: 1024x1024

**Enum Name**: Size

**Enum Values**:

| Value | Description |
| --- | --- |
| 1792x1024 | The desired size of the generated image is 1792x1024 pixels. |
| 1024x1792 | The desired size of the generated image is 1024x1792 pixels. |
| 1024x1024 | The desired size of the generated image is 1024x1024 pixels. |

### imageStyle

The style of the generated images.

**Description**: The style of the generated images.

**Type**: string

**Default**: vivid

**Enum Name**: Style

**Enum Values**:

| Value | Description |
| --- | --- |
| vivid | Vivid creates images that are hyper-realistic and dramatic. |
| natural | Natural creates images that are more natural and less hyper-realistic. |

### generateImagesResponse

| Name | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| created | integer | The unix timestamp when the operation was created. | Yes |  |
| data | array | The result data of the operation, if successful | Yes |  |
