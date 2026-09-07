---
layout: Conceptual
title: Azure AI Model Inference REST API | Microsoft Learn
canonicalUrl: https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/modelinference/
enable_rest_try_it: true
rest_product: Azure
uhfHeaderId: azure
breadcrumb_path: ../../../breadcrumb/toc.json
ms.author: fasantia
manager: smmark
author: santiagxf
ms.topic: reference
ms.devlang: rest-api
ms.date: 2025-04-09T00:00:00.0000000Z
ms.service: microsoft-foundry
description: REST API reference for Azure AI Model Inference in Azure AI Services
ms.subservice: foundry-model-inference
locale: en-us
moniker_definition_rel: ../../../.monikers.Azure.AzureRestApi.json
document_id: dbd47a92-e03a-6c88-693d-28937e1d29e8
document_version_independent_id: 53a749f0-8578-4627-6552-829bb6fd7ad5
updated_at: 2026-06-11T22:26:00.0000000Z
original_content_git_url: https://github.com/MicrosoftDocs/azure-docs-rest-apis/blob/live/docs-ref-conceptual/microsoft-foundry/modelinference/index.md
gitcommit: https://github.com/MicrosoftDocs/azure-docs-rest-apis/blob/e6a2984aa2993e8e56e59c3658d28d3f393a4ca5/docs-ref-conceptual/microsoft-foundry/modelinference/index.md
git_commit_id: e6a2984aa2993e8e56e59c3658d28d3f393a4ca5
site_name: Docs
depot_name: Azure.AzureRestApi
page_type: conceptual
toc_rel: ../../azure/toc.json
feedback_system: None
feedback_product_url: ''
feedback_help_link_type: ''
feedback_help_link_url: ''
word_count: 1012
asset_id: api/microsoft-foundry/modelinference/index
moniker_range_name:
monikers: []
item_type: Content
source_path: docs-ref-conceptual/microsoft-foundry/modelinference/index.md
cmProducts:
- https://authoring-docs-microsoft.poolparty.biz/devrel/68ec7f3a-2bc6-459f-b959-19beb729907d
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/c6f99e62-1cf6-4b71-af9b-649b05f80cce
spProducts:
- https://authoring-docs-microsoft.poolparty.biz/devrel/90370425-aca4-4a39-9533-d52e5e002a5d
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/3f56b378-07a9-4fa1-afe8-9889fdc77628
platformId: 303074fd-fa29-126d-258a-c9ac2f3f2159
---

# Azure AI Model Inference REST API | Microsoft Learn

The Azure AI model inference is an API that exposes a common set of capabilities for foundational models and that can be used by developers to consume predictions from a diverse set of models in a uniform and consistent way. Developers can talk with different models deployed in Azure AI Foundry portal without changing the underlying code they are using.

## Benefits

Foundational models, such as language models, have indeed made remarkable strides in recent years. These advancements have revolutionized various fields, including natural language processing and computer vision, and they have enabled applications like chatbots, virtual assistants, and language translation services.

While foundational models excel in specific domains, they lack a uniform set of capabilities. Some models are better at specific task and even across the same task, some models may approach the problem in one way while others in another. Developers can benefit from this diversity by **using the right model for the right job** allowing them to:

- Improve the performance in a specific downstream task.
- Use more efficient models for simpler tasks.
- Use smaller models that can run faster on specific tasks.
- Compose multiple models to develop intelligent experiences.

Having a uniform way to consume foundational models allow developers to realize all those benefits without sacrificing portability or changing the underlying code.

## Inference SDK support

The Azure AI Inference package allows you to consume all models supporting the Azure AI model inference API and easily change among them. Azure AI Inference package is part of the Azure AI Foundry SDK.

| Language | Documentation | Package | Examples |
| --- | --- | --- | --- |
| C# | [Reference](https://aka.ms/azsdk/azure-ai-inference/csharp/reference) | [azure-ai-inference (NuGet)](https://www.nuget.org/packages/Azure.AI.Inference/) | [C# examples](https://aka.ms/azsdk/azure-ai-inference/csharp/samples) |
| Java | [Reference](https://aka.ms/azsdk/azure-ai-inference/java/reference) | [azure-ai-inference (Maven)](https://central.sonatype.com/artifact/com.azure/azure-ai-inference/) | [Java examples](https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-inference/src/samples) |
| JavaScript | [Reference](/en-us/javascript/api/@azure-rest/ai-inference) | [@azure/ai-inference (npm)](https://www.npmjs.com/package/@azure/ai-inference) | [JavaScript examples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-inference-rest/samples) |
| Python | [Reference](https://aka.ms/azsdk/azure-ai-inference/python/reference) | [azure-ai-inference (PyPi)](https://pypi.org/project/azure-ai-inference/) | [Python examples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples) |

## Capabilities

The following section describes some of the capabilities the API exposes:

### Modalities

The API indicates how developers can consume predictions for the following modalities:

- [Get info](/en-us/rest/api/aifoundry/model-inference/get-model-info/get-model-info): Returns the information about the model deployed under the endpoint.
- [Text embeddings](/en-us/rest/api/aifoundry/model-inference/get-embeddings/get-embeddings): Creates an embedding vector representing the input text.
- [Chat completions](/en-us/rest/api/aifoundry/model-inference/get-chat-completions/get-chat-completions): Creates a model response for the given chat conversation.
- [Image embeddings](/en-us/rest/api/aifoundry/model-inference/get-image-embeddings/get-image-embeddings): Creates an embedding vector representing the input text and image.

### Extensibility

The Azure AI Model Inference API specifies a set of modalities and parameters that models can subscribe to. However, some models may have further capabilities that the ones the API indicates. On those cases, the API allows the developer to pass them as extra parameters in the payload.

By setting a header `extra-parameters: pass-through`, the API will attempt to pass any unknown parameter directly to the underlying model. If the model can handle that parameter, the request completes.

The following example shows a request passing the parameter `safe_prompt` supported by Mistral-Large, which isn't specified in the Azure AI Model Inference API.

**Request**

```HTTP
POST /chat/completions?api-version=2025-04-01
Authorization: Bearer 
Content-Type: application/json
extra-parameters: pass-through
```

```JSON
{
    "messages": [
    {
        "role": "system",
        "content": "You are a helpful assistant"
    },
    {
        "role": "user",
        "content": "Explain Riemann's conjecture in 1 paragraph"
    }
    ],
    "temperature": 0,
    "top_p": 1,
    "response_format": { "type": "text" },
    "safe_prompt": true
}
```

Note

The default value for `extra-parameters` is `error` which returns an error if an extra parameter is indicated in the payload. Alternatively, you can set `extra-parameters: drop` to drop any unknown parameter in the request. Use this capability in case you happen to be sending requests with extra parameters that you know the model won't support but you want the request to completes anyway. A typical example of this is indicating `seed` parameter.

### Models with disparate set of capabilities

The Azure AI Model Inference API indicates a general set of capabilities but each of the models can decide to implement them or not. A specific error is returned on those cases where the model can't support a specific parameter.

The following example shows the response for a chat completion request indicating the parameter `reponse_format` and asking for a reply in `JSON` format. In the example, since the model doesn't support such capability an error 422 is returned to the user.

**Request**

```HTTP
POST /chat/completions?api-version=2025-04-01
Authorization: Bearer 
Content-Type: application/json
```

```JSON
{
    "messages": [
    {
        "role": "system",
        "content": "You are a helpful assistant"
    },
    {
        "role": "user",
        "content": "Explain Riemann's conjecture in 1 paragraph"
    }
    ],
    "temperature": 0,
    "top_p": 1,
    "response_format": { "type": "json_object" },
}
```

**Response**

```JSON
{
    "status": 422,
    "code": "parameter_not_supported",
    "detail": {
        "loc": [ "body", "response_format" ],
        "input": "json_object"
    },
    "message": "One of the parameters contain invalid values."
}
```

Tip

You can inspect the property `details.loc` to understand the location of the offending parameter and `details.input` to see the value that was passed in the request.

## Content safety

The Azure AI model inference API supports [Azure AI Content Safety](../../../ai-studio/concepts/content-filtering.md). When using deployments with Azure AI Content Safety on, inputs and outputs pass through an ensemble of classification models aimed at detecting and preventing the output of harmful content. The content filtering (preview) system detects and takes action on specific categories of potentially harmful content in both input prompts and output completions.

The following example shows the response for a chat completion request that has triggered content safety.

**Request**

```HTTP
POST /chat/completions?api-version=2025-04-01
Authorization: Bearer 
Content-Type: application/json
```

```JSON
{
    "messages": [
    {
        "role": "system",
        "content": "You are a helpful assistant"
    },
    {
        "role": "user",
        "content": "Chopping tomatoes and cutting them into cubes or wedges are great ways to practice your knife skills."
    }
    ],
    "temperature": 0,
    "top_p": 1,
}
```

**Response**

```JSON
{
    "status": 400,
    "code": "content_filter",
    "message": "The response was filtered",
    "param": "messages",
    "type": null
}
```

## Getting started

Azure AI model inference API is available on Azure AI Services resources. You can get started with it the same way as any other Azure product where you [create and configure your resource for Azure AI model inference](/en-us/azure/ai-foundry/model-inference/how-to/quickstart-create-resources), or instance of the service, in your Azure Subscription. You can create as many resources as needed and configure them independently in case you have multiple teams with different requirements.

Once you create an Azure AI Services resource, you must deploy a model before you can start making API calls. By default, no models are available on it, so you can control which ones to start from. See the tutorial [Create your first model deployment in Azure AI model inference](/en-us/azure/ai-foundry/model-inference/how-to/create-model-deployments).
