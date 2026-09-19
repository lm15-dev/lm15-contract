---
layout: Conceptual
title: How to generate text responses with Microsoft Foundry Models - Microsoft Foundry | Microsoft Learn
canonicalUrl: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/generate-responses
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
author: msakande
learn_banner_products:
- azure
manager: mcleans
ms.author: mopeakande
ms.collection: ce-skilling-ai-copilot
ms.update-cycle: 90-days
ms.service: microsoft-foundry
description: Learn how to generate text responses from Foundry Models, such as Microsoft AI and DeepSeek models, by using the Responses API.
ms.subservice: foundry-openai
ms.topic: how-to
ms.date: 2026-06-04T00:00:00.0000000Z
ms.reviewer: achand
reviewer: achandmsft
ms.custom:
- generated, pilot-ai-workflow-jan-2026
- classic-and-new
- doc-kit-assisted
ai-usage: ai-assisted
locale: en-us
document_id: a9903988-97bd-0f14-2a92-68392ca5408d
document_version_independent_id: 9d514eca-a32f-c421-9ac2-3012cda635f6
updated_at: 2026-06-11T22:32:00.0000000Z
original_content_git_url: https://github.com/MicrosoftDocs/azure-ai-docs-pr/blob/live/articles/foundry/foundry-models/how-to/generate-responses.md
gitcommit: https://github.com/MicrosoftDocs/azure-ai-docs-pr/blob/a9f50ef73434548c196ffaaceb88eed2655fdbf2/articles/foundry/foundry-models/how-to/generate-responses.md
git_commit_id: a9f50ef73434548c196ffaaceb88eed2655fdbf2
site_name: Docs
depot_name: Learn.azure-ai
page_type: conceptual
toc_rel: ../../toc.json
word_count: 1482
asset_id: foundry/foundry-models/how-to/generate-responses
moniker_range_name: 
monikers: []
item_type: Content
source_path: articles/foundry/foundry-models/how-to/generate-responses.md
cmProducts:
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/cbd33d8f-e9af-440e-8f1e-fc69e07b902b
- https://authoring-docs-microsoft.poolparty.biz/devrel/68ec7f3a-2bc6-459f-b959-19beb729907d
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/de19c5b8-e208-412e-9238-db3f631dea5b
spProducts:
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/3820371b-086e-47fb-9d1f-b215f569127a
- https://authoring-docs-microsoft.poolparty.biz/devrel/90370425-aca4-4a39-9533-d52e5e002a5d
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/ea7bf5d6-7154-4ba9-8ebc-59117ccacd49
platformId: 2f891492-892b-40e3-b8c2-5bd26060e94b
---

# How to generate text responses with Microsoft Foundry Models - Microsoft Foundry | Microsoft Learn

This article explains how to generate text responses for Foundry Models, such as Microsoft AI, DeepSeek, and Grok models, by using the Responses API. For a full list of the Foundry Models that support use of the Responses API, see Supported Foundry Models.

## Prerequisites

To use the Responses API with deployed models in your application, you need:

- An Azure subscription.
- A Foundry project. This kind of project is managed under a Foundry resource. If you don't have a Foundry project, see [Create a project for Microsoft Foundry](../../how-to/create-projects).
- Your Foundry project's endpoint URL, which is of the form `https://YOUR-RESOURCE-NAME.services.ai.azure.com/api/projects/YOUR_PROJECT_NAME`.
- A deployment of a Foundry Model, such as the `DeepSeek-R1-0528` model used in this article. If you don't have a deployment already, see [Add and configure Foundry Models](create-model-deployments) to add a model deployment to your resource.

### Use the AI model starter kit

The code snippets in this article are from the [AI model starter kit](https://aka.ms/ai-model-start). Use this starter kit as a quick way to get started with complete cloud infrastructure and code needed to call Foundry Models, using a stable OpenAI library with the Responses API.

## Use the Responses API to generate text

Use the code in this section to make Responses API calls for Foundry Models. In the code samples, you create the client to consume the model and then send it a basic request.

Tip

When you deploy a model in the Foundry portal, you assign it a deployment name. Use this deployment name (not the model catalog ID) in the `model` parameter of your API calls.

Note

Use keyless authentication with **Microsoft Entra ID**. To learn more about keyless authentication, see [What is Microsoft Entra authentication?](/en-us/entra/identity/authentication/overview-authentication) and [DefaultAzureCredential](/en-us/azure/developer/python/sdk/authentication/overview#defaultazurecredential).

# [Python](#tab/python)
1. Install libraries, including the Azure Identity client library:

    ```bash
    pip install azure-identity
    pip install -U openai
    ```
2. Use the following code to configure the OpenAI client object in the project route, specify your deployment, and generate responses.

    ```python
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    from openai import OpenAI
    
    project_endpoint = "https://YOUR-RESOURCE-NAME.services.ai.azure.com/api/projects/YOUR_PROJECT_NAME"
    # Build the base URL: project_endpoint + /openai/v1 (no api-version needed)
    base_url = project_endpoint.rstrip("/") + "/openai/v1"
    
    # Use get_bearer_token_provider for automatic token refresh
    credential = DefaultAzureCredential()
    client = OpenAI(
        base_url=base_url,
        api_key=get_bearer_token_provider(credential, "https://ai.azure.com/.default"),
    )
    
    response = client.responses.create(
        model="DeepSeek-R1-0528", # Replace with your deployment name, not the model ID 
        input="What are the top 3 benefits of cloud computing? Be concise.",
        max_output_tokens=2000,
    )
    
    print(f"Response: {response.output_text}")
    print(f"Status:   {response.status}")
    print(f"Output tokens: {response.usage.output_tokens}") 
    ```

# [C#](#tab/dotnet)
1. Install the Azure Identity client library:

    ```dotnetcli
    dotnet add package Azure.Identity
    dotnet add package OpenAI
    ```
2. Use the following code to configure the OpenAI client object in the project route, specify your deployment, and generate responses.

    ```csharp
    using System.ClientModel;
    using Azure.Identity;
    using OpenAI;
    using OpenAI.Responses;
    
    var deploymentName = "DeepSeek-R1-0528"; // Replace with your deployment name, not the model ID 
    var project_endpoint = "https://YOUR-RESOURCE-NAME.services.ai.azure.com/api/projects/YOUR_PROJECT_NAME";
    
    // Get EntraID token for keyless auth
    var credential = new DefaultAzureCredential();
    var token = await credential.GetTokenAsync(
        new Azure.Core.TokenRequestContext(["https://ai.azure.com/.default"])
    );
    
    // Standard OpenAI client — no AzureOpenAI wrapper (no api-version needed with /v1 path)
    var baseUrl = project_endpoint.TrimEnd('/') + "/openai/v1";
    var client = new OpenAIClient(
        new ApiKeyCredential(token.Token),
        new OpenAIClientOptions { Endpoint = new Uri(baseUrl) });    
    
    // GetResponsesClient takes no parameter; model goes in CreateResponseOptions
    var responseClient = client.GetResponsesClient(deploymentName);
    var result = await responseClient.CreateResponseAsync(new CreateResponseOptions(
        [ResponseItem.CreateUserMessageItem("What are the top 3 benefits of cloud computing? Be concise.")])
        { MaxOutputTokenCount = 500 }
    );
    Console.WriteLine($"Response: {result.Value.GetOutputText()}");
    Console.WriteLine($"Status:   {result.Value.Status}");
    Console.WriteLine($"Output tokens: {result.Value.Usage.OutputTokenCount}");
    
    ```

# [JavaScript](#tab/javascript)
1. Install the Azure Identity client library before you can use `DefaultAzureCredential`:

    ```bash
    npm install @azure/identity
    npm install openai
    ```
2. Use the following code to configure the OpenAI client object in the project route, specify your deployment, and generate responses.

    ```javascript
    import OpenAI from "openai";
    import { DefaultAzureCredential } from "@azure/identity";
    
    async function getToken() {
      const credential = new DefaultAzureCredential();
      const tokenResponse = await credential.getToken(
        "https://ai.azure.com/.default"
      );
      return tokenResponse.token;
    }
    
    async function main() {
        const projectEndpoint = "https://YOUR-RESOURCE-NAME.services.ai.azure.com/api/projects/YOUR_PROJECT_NAME";
        const deploymentName = "DeepSeek-R1-0528"; // Replace with your deployment name, not the model ID 
    
        const baseURL = projectEndpoint.replace(/\/+$/, "") + "/openai/v1";
        const token = await getToken();
    
        const client = new OpenAI({
            baseURL,
            apiKey: token,
          });
    
        const response = await client.responses.create({
            model: deploymentName,
            input: "What are the top 3 benefits of cloud computing? Be concise.",
            max_output_tokens: 500,
          });
    
        console.log(`Response: ${response.output_text}`);
        console.log(`Status:   ${response.status}`);
        console.log(`Output tokens: ${response.usage?.output_tokens}`);
    }
    
    main();
    ```

# [Java](#tab/java)
Authentication with Microsoft Entra ID requires some initial setup. First, install the Azure Identity client library. For more options on how to install this library, see [Azure Identity client library for Java](https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/identity/azure-identity/README.md#include-the-package).

1. Add the Azure Identity client library:

    ```xml
    <dependencies>
        <dependency>
            <groupId>com.openai</groupId>
            <artifactId>openai-java</artifactId>
            <version>4.22.0</version>
        </dependency>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-identity</artifactId>
            <version>1.18.4</version>
        </dependency>
    </dependencies>
    ```

    After setup, choose which type of credential from `azure.identity` to use. For example, use `DefaultAzureCredential` to authenticate the client. `DefaultAzureCredential` is the easiest option because it finds the best credential to use in its running environment.
2. Use the following code to configure the OpenAI client object in the project route, specify your deployment, and generate responses.

    ```java
    import com.azure.core.credential.TokenRequestContext;
    import com.azure.identity.DefaultAzureCredentialBuilder;
    import com.openai.client.OpenAIClient;
    import com.openai.client.okhttp.OpenAIOkHttpClient;
    import com.openai.models.responses.Response;
    import com.openai.models.responses.ResponseCreateParams;
    
    public class Sample {
    
        // Return the final assistant message text from a Responses API result.
        static String getOutputText(Response response) {
            var sb = new StringBuilder();
            response.output().stream()
                    .flatMap(item -> item.message().stream())
                    .flatMap(message -> message.content().stream())
                    .flatMap(content -> content.outputText().stream())
                    .forEach(outputText -> sb.append(outputText.text()));
            return sb.toString();
        }
    
        public static void main(String[] args) {
            String endpoint = "https://YOUR-RESOURCE-NAME.services.ai.azure.com/api/projects/YOUR_PROJECT_NAME";
            String deploymentName = "DeepSeek-R1-0528"; // Replace with your deployment name, not the model ID
    
            // Get EntraID token for keyless auth
            var credential = new DefaultAzureCredentialBuilder().build();
            var context = new TokenRequestContext().addScopes("https://ai.azure.com/.default");
            String token = credential.getToken(context).block().getToken();
    
            // Standard OpenAI client — no Azure wrapper
            // Java SDK uses /openai/v1 path (no api-version needed; SDK manages versioning internally)
            String baseUrl = endpoint.replaceAll("/+$", "") + "/openai/v1";
            OpenAIClient client = OpenAIOkHttpClient.builder()
                    .baseUrl(baseUrl)
                    .apiKey(token)
                    .build();
    
            var response = client.responses().create(
                    ResponseCreateParams.builder()
                            .model(deploymentName)
                            .input("What are the top 3 benefits of cloud computing? Be concise.")
                            .maxOutputTokens(500)
                            .build()
            );
            System.out.printf("Response: %s%n", getOutputText(response));
            System.out.printf("Status:   %s%n", response.status());
            response.usage().ifPresent(u ->
                    System.out.printf("Output tokens: %d%n", u.outputTokens()));
        }
    }
    ```

# [Go](#tab/go)
1. Before running the sample, install the required Go modules.

    ```bash
    go get github.com/Azure/azure-sdk-for-go/sdk/azcore@v1.21.0
    go get github.com/Azure/azure-sdk-for-go/sdk/azidentity@v1.13.1
    go get github.com/openai/openai-go/v3@v3.22.0
    ```
2. Use the following code to configure the OpenAI client object in the project route, specify your deployment, and generate responses.

    ```go
    package main
    
    import (
        "context"
        "fmt"
        "os"
        "strings"
    
        "github.com/Azure/azure-sdk-for-go/sdk/azcore/policy"
        "github.com/Azure/azure-sdk-for-go/sdk/azidentity"
        "github.com/openai/openai-go/v3"
        "github.com/openai/openai-go/v3/option"
        "github.com/openai/openai-go/v3/responses"
    )
    
    func main() {
        projectEndpoint := "https://YOUR-RESOURCE-NAME.services.ai.azure.com/api/projects/YOUR_PROJECT_NAME"
        deploymentName := "DeepSeek-R1-0528" // Replace with your deployment name, not the model ID
    
        ctx := context.Background()
    
        // Get EntraID token for keyless auth
        credential, err := azidentity.NewDefaultAzureCredential(nil)
        if err != nil {
            fmt.Fprintf(os.Stderr, "Failed to create credential: %v\n", err)
            os.Exit(1)
        }
        token, err := credential.GetToken(ctx, policy.TokenRequestOptions{
            Scopes: []string{"https://ai.azure.com/.default"},
        })
        if err != nil {
            fmt.Fprintf(os.Stderr, "Failed to get token: %v\n", err)
            os.Exit(1)
        }
    
        // Standard OpenAI client — no Azure wrapper (no api-version needed with /v1 path)
        baseURL := strings.TrimRight(projectEndpoint, "/") + "/openai/v1"
        client := openai.NewClient(
            option.WithBaseURL(baseURL),
            option.WithAPIKey(token.Token),
        )
    
        resp, err := client.Responses.New(ctx, responses.ResponseNewParams{
            Model: deploymentName,
            Input: responses.ResponseNewParamsInputUnion{
                OfString: openai.String("What are the top 3 benefits of cloud computing? Be concise."),
            },
            MaxOutputTokens: openai.Int(500),
        })
        if err != nil {
            fmt.Fprintf(os.Stderr, "API error: %v\n", err)
            os.Exit(1)
        }
    
        fmt.Printf("Response: %s\n", resp.OutputText())
        fmt.Printf("Status:   %s\n", resp.Status)
        fmt.Printf("Output tokens: %d\n", resp.Usage.OutputTokens)
    }
    ```

---

The response includes the generated text along with model and usage metadata.

## Supported Foundry Models

A selection of Foundry Models are supported for use with the Responses API.

### View supported models in the Foundry portal

To see a full list of the supported models in the Foundry portal:

1. Sign in to [Microsoft Foundry](https://ai.azure.com/?cid=learnDocs). Make sure the **New Foundry** toggle is on. These steps refer to **Foundry (new)**.![](../../media/version-banner/new-foundry.png)
2. Select **Discover** in the upper-right navigation, then **Models** in the left pane.
3. Open the **Capabilities** dropdown and select the **Agent supported** filter.

### List of supported models

This section lists some of the Foundry Models that are supported for use with the Responses API. For the Azure OpenAI models that are supported, see [Available Azure OpenAI models](../../agents/concepts/limits-quotas-regions).

**Foundry Models sold by Azure:**

- **MAI-DS-R1**: Deterministic, precision-focused reasoning.
- **grok-4**: Frontier-scale reasoning for complex, multiple-step problem solving.
- **grok-4-fast-reasoning**: Accelerated agentic reasoning optimized for workflow automation.
- **grok-4-fast-non-reasoning**: High-throughput, low-latency generation and system routing.
- **grok-3**: Strong reasoning for complex, system-level workflows.
- **grok-3-mini**: Lightweight model optimized for interactive, high-volume use cases.
- **Llama-3.3-70B-Instruct**: Versatile model for enterprise Q&A, decision support, and system orchestration.
- **Llama-4-Maverick-17B-128E-Instruct-FP8**: FP8-optimized model that delivers fast, cost-efficient inference.
- **DeepSeek-V3-0324**: Multimodal understanding across text and images.
- **DeepSeek-V3.1**: Enhanced multimodal reasoning and grounded retrieval.
- **DeepSeek-V3.2**: Model that harmonizes high computational efficiency with superior reasoning and agent performance.
- **DeepSeek-V3.2-Speciale**: Specialized DeepSeek-V3.2 variant.
- **DeepSeek-R1-0528**: Advanced long-form and multiple-step reasoning.
- **gpt-oss-120b**: Open-ecosystem model that supports transparency and reproducibility.

## Troubleshoot common errors

| Error | Cause | Resolution |
| --- | --- | --- |
| 401 Unauthorized | Invalid or expired credential | Verify your `DefaultAzureCredential` has the **Cognitive Services OpenAI User** role assigned on the resource. |
| 404 Not Found | Wrong endpoint or deployment name | Confirm your endpoint URL includes `/api/projects/YOUR_PROJECT_NAME` and the deployment name matches your Foundry portal. |
| 400 Model not supported | Model doesn't support Responses API | Check the supported models list and verify your deployment uses a compatible model. |