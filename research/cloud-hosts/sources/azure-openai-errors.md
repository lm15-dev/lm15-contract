---
layout: Conceptual
title: Azure OpenAI in Microsoft Foundry Models Quotas and Limits - Microsoft Foundry | Microsoft Learn
canonicalUrl: https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits
breadcrumb_path: ../../breadcrumb/azure-ai/toc.json
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
author: alvinashcraft
learn_banner_products:
- azure
manager: mcleans
ms.author: aashcraft
ms.collection: ce-skilling-ai-copilot
ms.update-cycle: 90-days
ms.service: microsoft-foundry
description: This article features detailed descriptions and best practices on the quotas and limits for Azure OpenAI.
ms.reviewer: haakar
reviewer: haakar
ms.date: 2026-08-20T00:00:00.0000000Z
ms.subservice: foundry-openai
ms.topic: limits-and-quotas
ms.custom:
- classic-and-new
- ignite-2023
- references_regions
- build-2025
- doc-kit-assisted
ai-usage: ai-assisted
locale: en-us
document_id: 0fa6aa02-790c-4d48-bd1a-961b6da76d06
document_version_independent_id: 36d34794-6a72-c31e-4401-865fb92bbd7f
updated_at: 2026-08-20T22:12:00.0000000Z
original_content_git_url: https://github.com/MicrosoftDocs/azure-ai-docs-pr/blob/live/articles/foundry/openai/quotas-limits.md
gitcommit: https://github.com/MicrosoftDocs/azure-ai-docs-pr/blob/a7293ab57b2b33653cae505e60a79a37643d6c7f/articles/foundry/openai/quotas-limits.md
git_commit_id: a7293ab57b2b33653cae505e60a79a37643d6c7f
site_name: Docs
depot_name: Learn.azure-ai
page_type: conceptual
toc_rel: ../toc.json
word_count: 4413
asset_id: foundry/openai/quotas-limits
moniker_range_name:
monikers: []
item_type: Content
source_path: articles/foundry/openai/quotas-limits.md
cmProducts:
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/8a6e4dad-7050-4ce7-83f9-eb4123577a54
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/de19c5b8-e208-412e-9238-db3f631dea5b
- https://authoring-docs-microsoft.poolparty.biz/devrel/68ec7f3a-2bc6-459f-b959-19beb729907d
spProducts:
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/0a5fc323-00ce-4c20-9095-41948f54c83f
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/ea7bf5d6-7154-4ba9-8ebc-59117ccacd49
- https://authoring-docs-microsoft.poolparty.biz/devrel/90370425-aca4-4a39-9533-d52e5e002a5d
platformId: 30d951f7-9b26-2126-0c95-da15f0bb1105
---

# Azure OpenAI in Microsoft Foundry Models Quotas and Limits - Microsoft Foundry | Microsoft Learn

This article contains a quick reference and a detailed description of the quotas and limits for Azure OpenAI.

## Scope of quota

Quotas and limits aren't enforced at the tenant level. Instead, the highest level of quota restrictions is scoped at the Azure subscription level.

## Subscription-level quota management

Important

Subscription-level quota management in Microsoft Foundry started after **May 7, 2026**.

Starting with Realtime Translate and Realtime Whisper, and soon all models, Foundry tracks quota for deployments at the subscription level rather than per resource or per region. This approach brings consistency and predictability to how quota is managed across deployments, since all resources and regions in a subscription share the same quota pool.

This change consolidates quota into shared pools:

- **Global Standard**: Deployments of the same model and version share one quota pool across all regions in a subscription.
- **Data Zone Standard**: Deployments of the same model and version share one quota pool per data zone (for example, US or EU).

To learn more about quota allocation at the subscription level, see [Microsoft Foundry Models quotas and limits](../foundry-models/quotas-limits).

## Quota tiers

Microsoft is introducing quota tiers to improve the Foundry Models experience and reduce friction as workloads scale. Quotas now increase automatically with usage, helping avoid rate limit errors while also creating a fairer environment for all users. Seven tiers are available: Free Tier and Tiers 1 through 6 - with Tier 6 offering the highest quotas. A customer's initial assigned tier is based on their current usage of that model and their current relationship with Microsoft, such as Enterprise Agreement (EA or MCA-E) status. 

### What's changing for me?

Previously, Foundry offered only Default and Enterprise quota levels for pay as you go offer type, with a large gap between each level and a longer process to request increases. With Quota Tiers, all users are assigned a tier with quotas equal to or higher than their previous levels. Any previously approved quota increases are retained and will not be reduced. As usage grows, Foundry automatically increases quotas by moving users to higher tiers, and additional quota can still be requested through the quota form.

### How will a customer automatically move from one tier to another, for example what are the tier change criteria?

Automatic tier upgrades primarily depend on customer consumption trends across Foundry Models over time. If a customer's usage increases such that their current quota tier limits their ability to use Foundry Models, the system automatically upgrades the customer to the next higher tier. The system also considers a customer's relationship with Microsoft. Customers with Enterprise relationships (including EA and MCA-E) with Microsoft are assigned higher quota tiers. In addition, Microsoft also considers a customer's payment history to determine eligibility for automatic upgrades. 

### Can I opt out of auto upgrades?

Yes, you can opt out of auto upgrades to stay in your current tier regardless of changes in your consumption. Some customers use quota to manage their billing. Using quota to manage billing isn't the Azure best practice, but if your system is configured that way, you might not want to break it. To learn more about billing management and best practices, see [Cost Management](../concepts/manage-costs).

To opt out, you can set the following flag to `NoAutoUpgrade`:

```bash
curl -X PATCH \
  "https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.CognitiveServices/quotaTiers/default?api-version=2025-10-01-preview" \
  -H "Authorization: Bearer " \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "tierUpgradePolicy": "NoAutoUpgrade"
    }
  }'
```

Note

The opt out feature is preview and may be subject to change/removal in the future.

### Can I request more quota?

Yes, using the [quota request form](https://aka.ms/oai/stuquotarequest) you can always request more quota. If the request is approved, the current tier will remain the same, but with more quota assigned.

### How do I check my subscription's quota tier?

You can currently check you quota tier with the [control plane API](/en-us/rest/api/microsoftfoundry/accountmanagement/quota-tiers/get?view=rest-microsoftfoundry-accountmanagement-2025-10-01-preview&tabs=HTTP&preserve-view=true):

# [Bash](#tab/bash)
```bash
curl -X GET \
  "https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.CognitiveServices/quotaTiers?api-version=2025-10-01-preview" \
  -H "Authorization: Bearer $(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)" \
  -H "Content-Type: application/json"
```

# [Python](#tab/python)
```python
import requests
import json
from azure.identity import DefaultAzureCredential

subscriptionId = "{YOUR-SUBSCRIPTION-ID}"
api_version = "2025-10-01-preview" 
base_url = "https://management.azure.com"

token_credential = DefaultAzureCredential()
token = token_credential.get_token('https://management.azure.com/.default')
headers = {
    'Authorization': 'Bearer ' + token.token,
    'Content-Type': 'application/json'
}

list_url = (
    f"{base_url}/subscriptions/{subscriptionId}"
    f"/providers/Microsoft.CognitiveServices/quotaTiers"
    f"?api-version={api_version}"
)

response = requests.get(list_url, headers=headers)
print(json.dumps(response.json(), indent=2))

```

# [Output](#tab/output)
```json
{
  "value": [
    {
      "properties": {
        "currentTierName": "Tier 1",
        "assignmentDate": "2025-10-18T05:09:05.6334222Z",
        "tierUpgradePolicy": "OnceUpgradeIsAvailable"
      },
      "id": "/subscriptions/aaaaa-bbbbb-ccccc-dddd-eeeeeee/providers/Microsoft.CognitiveServices/quotaTiers/default",
      "name": "default",
      "type": "Microsoft.CognitiveServices/quotaTiers"
    }
  ]
}
```

---

### Quota tier reference

All `gpt-chat-latest` versions use the same tier-level TPM limit shown in each tier. Versions `2026-05-05`, `2026-05-28`, and `2026-06-24`^1^ use 10 RPM per 1,000 TPM. Version `2026-08-06`^2^ uses 1 RPM per 1,000 TPM, so the tables list the versions separately.

# [Tier 1](#tab/tier1)
### Tier 1

| Model Name | Deployment Type | Requests Per Minute (RPM) | Tokens Per Minute (TPM) |
| --- | --- | --- | --- |
| codex-mini | GlobalStandard | 1,000 | 1,000,000 |
| computer-use-preview | GlobalStandard | 4,500 | 450,000 |
| gpt-4.1 | DataZoneStandard | 300 | 300,000 |
| gpt-4.1 | GlobalStandard | 1,000 | 1,000,000 |
| gpt-4.1-mini | DataZoneStandard | 2,000 | 2,000,000 |
| gpt-4.1-mini | GlobalStandard | 5,000 | 5,000,000 |
| gpt-4.1-mini | Standard | 6,000 | 6,000,000 |
| gpt-4.1-nano | DataZoneStandard | 2,000 | 2,000,000 |
| gpt-4.1-nano | GlobalStandard | 5,000 | 5,000,000 |
| gpt-4o | DataZoneStandard | 300 / 10s | 300,000 |
| gpt-4o-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini | DataZoneStandard | 10,000 | 1,000,000 |
| gpt-4o-mini | GlobalStandard | 20,000 | 2,000,000 |
| gpt-4o-mini-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-4o-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-5 | DataZoneStandard | 3,000 | 300,000 |
| gpt-5 | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5-chat | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5-codex | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5-mini | DataZoneStandard | 300 | 300,000 |
| gpt-5-mini | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5-nano | DataZoneStandard | 2,000 | 2,000,000 |
| gpt-5-nano | GlobalStandard | 5,000 | 5,000,000 |
| gpt-5-pro | GlobalStandard | 1,600 | 160,000 |
| gpt-5.1 | DataZoneStandard | 3,000 | 300,000 |
| gpt-5.1 | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5.1 | Standard | 3,000 | 300,000 |
| gpt-5.1-chat | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5.1-codex | DataZoneStandard | 3,000 | 300,000 |
| gpt-5.1-codex | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5.1-codex-max | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5.1-codex-mini | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5.2 | DataZoneStandard | 3,000 | 300,000 |
| gpt-5.2 | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5.2-chat | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5.3-chat | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5.2-codex | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5.3-codex | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5.4 | DataZoneStandard | 300 | 300,000 |
| gpt-5.4 | GlobalStandard | 10,000 | 1,000,000 |
| gpt-5.4-pro | GlobalStandard | 160 | 160,000 |
| gpt-5.4-mini | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5.4-nano | DataZoneStandard | 2,000 | 2,000,000 |
| gpt-5.4-nano | GlobalStandard | 5,000 | 5,000,000 |
| gpt-5.5 | DataZoneStandard | 333 | 333,000 |
| gpt-5.5 | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5.6-luna | DataZoneStandard | 333 | 333,000 |
| gpt-5.6-luna | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5.6-sol | DataZoneStandard | 333 | 333,000 |
| gpt-5.6-sol | GlobalStandard | 1,000 | 1,000,000 |
| gpt-5.6-terra | DataZoneStandard | 333 | 333,000 |
| gpt-5.6-terra | GlobalStandard | 1,000 | 1,000,000 |
| gpt-chat-latest^1^ | GlobalStandard | 10,000 | 1,000,000 |
| gpt-chat-latest^2^ | GlobalStandard | 1,000 | 1,000,000 |
| gpt-audio | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-image-1 | GlobalStandard | 9 | - |
| gpt-image-1-mini | GlobalStandard | 12 | - |
| gpt-image-1.5 | DataZoneStandard | 3 | - |
| gpt-image-1.5 | GlobalStandard | 9 | - |
| gpt-image-2 | DataZoneStandard | 2 | - |
| gpt-image-2 | GlobalStandard | 6 | - |
| gpt-realtime | GlobalStandard | 200 | 100,000 |
| model-router | DataZoneStandard | 300 | 300,000 |
| model-router | GlobalStandard | 1,000 | 1,000,000 |
| o1 | DataZoneStandard | 100 | 600,000 |
| o1 | GlobalStandard | 500 | 3,000,000 |
| o3 | DataZoneStandard | 300 | 300,000 |
| o3 | GlobalStandard | 1,000 | 1,000,000 |
| o3-deep-research | GlobalStandard | 3,000 | 3,000,000 |
| o3-mini | DataZoneStandard | 200 | 2,000,000 |
| o3-mini | GlobalStandard | 500 | 5,000,000 |
| o3-pro | GlobalStandard | 160 | 1,600,000 |
| o4-mini | DataZoneStandard | 300 / 10s | 300,000 |
| o4-mini | GlobalStandard | 1,000 | 1,000,000 |
| text-embedding-3-large | DataZoneStandard | 1,000 | 1,000,000 |
| text-embedding-3-large | GlobalStandard | 1000 / 10s | 1,000,000 |
| text-embedding-3-small | DataZoneStandard | 1,000 | 1,000,000 |
| text-embedding-3-small | GlobalStandard | 1000 / 10s | 1,000,000 |

# [Tier 2](#tab/tier2)
### Tier 2

| Model Name | Deployment Type | Requests Per Minute (RPM) | Tokens Per Minute (TPM) |
| --- | --- | --- | --- |
| codex-mini | GlobalStandard | 2,000 | 2,000,000 |
| computer-use-preview | GlobalStandard | 20,000 | 2,000,000 |
| gpt-4.1 | DataZoneStandard | 1,000 | 1,000,000 |
| gpt-4.1 | GlobalStandard | 3,000 | 3,000,000 |
| gpt-4.1-mini | DataZoneStandard | 6,000 | 6,000,000 |
| gpt-4.1-mini | GlobalStandard | 16,000 | 16,000,000 |
| gpt-4.1-mini | Standard | 12,000 | 12,000,000 |
| gpt-4.1-nano | DataZoneStandard | 6,000 | 6,000,000 |
| gpt-4.1-nano | GlobalStandard | 16,000 | 16,000,000 |
| gpt-4o | DataZoneStandard | 1000 / 10s | 1,000,000 |
| gpt-4o-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini | DataZoneStandard | 30,000 | 3,000,000 |
| gpt-4o-mini | GlobalStandard | 90,000 | 9,000,000 |
| gpt-4o-mini-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-4o-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-5 | DataZoneStandard | 10,000 | 1,000,000 |
| gpt-5 | GlobalStandard | 30,000 | 3,000,000 |
| gpt-5-chat | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5-codex | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5-mini | DataZoneStandard | 670 | 670,000 |
| gpt-5-mini | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5-nano | DataZoneStandard | 6,000 | 6,000,000 |
| gpt-5-nano | GlobalStandard | 16,000 | 16,000,000 |
| gpt-5-pro | GlobalStandard | 3,500 | 350,000 |
| gpt-5.1 | DataZoneStandard | 6,700 | 670,000 |
| gpt-5.1 | GlobalStandard | 20,000 | 2,000,000 |
| gpt-5.1 | Standard | 6,700 | 670,000 |
| gpt-5.1-chat | GlobalStandard | 20,000 | 2,000,000 |
| gpt-5.1-codex | DataZoneStandard | 6,700 | 670,000 |
| gpt-5.1-codex | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5.1-codex-max | GlobalStandard | 20,000 | 2,000,000 |
| gpt-5.1-codex-mini | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5.2 | DataZoneStandard | 6,700 | 670,000 |
| gpt-5.2 | GlobalStandard | 20,000 | 2,000,000 |
| gpt-5.2-chat | GlobalStandard | 20,000 | 2,000,000 |
| gpt-5.3-chat | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5.2-codex | GlobalStandard | 20,000 | 2,000,000 |
| gpt-5.3-codex | GlobalStandard | 20,000 | 2,000,000 |
| gpt-5.4 | DataZoneStandard | 670 | 670,000 |
| gpt-5.4 | GlobalStandard | 20,000 | 2,000,000 |
| gpt-5.4-pro | GlobalStandard | 350 | 350,000 |
| gpt-5.4-mini | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5.4-nano | DataZoneStandard | 6,000 | 6,000,000 |
| gpt-5.4-nano | GlobalStandard | 16,000 | 16,000,000 |
| gpt-5.5 | DataZoneStandard | 667 | 667,000 |
| gpt-5.5 | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5.6-luna | DataZoneStandard | 667 | 667,000 |
| gpt-5.6-luna | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5.6-sol | DataZoneStandard | 667 | 667,000 |
| gpt-5.6-sol | GlobalStandard | 2,000 | 2,000,000 |
| gpt-5.6-terra | DataZoneStandard | 667 | 667,000 |
| gpt-5.6-terra | GlobalStandard | 2,000 | 2,000,000 |
| gpt-chat-latest^1^ | GlobalStandard | 20,000 | 2,000,000 |
| gpt-chat-latest^2^ | GlobalStandard | 2,000 | 2,000,000 |
| gpt-audio | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-image-1 | GlobalStandard | 18 | - |
| gpt-image-1-mini | GlobalStandard | 27 | - |
| gpt-image-1.5 | DataZoneStandard | 5 | - |
| gpt-image-1.5 | GlobalStandard | 15 | - |
| gpt-image-2 | DataZoneStandard | 4 | - |
| gpt-image-2 | GlobalStandard | 12 | - |
| gpt-realtime | GlobalStandard | 200 | 100,000 |
| model-router | DataZoneStandard | 670 | 670,000 |
| model-router | GlobalStandard | 2,000 | 2,000,000 |
| o1 | DataZoneStandard | 225 | 1,350,000 |
| o1 | GlobalStandard | 1,000 | 6,000,000 |
| o3 | DataZoneStandard | 670 | 670,000 |
| o3 | GlobalStandard | 2,000 | 2,000,000 |
| o3-deep-research | GlobalStandard | 7,000 | 7,000,000 |
| o3-mini | DataZoneStandard | 350 | 3,500,000 |
| o3-mini | GlobalStandard | 1,000 | 10,000,000 |
| o3-pro | GlobalStandard | 350 | 3,500,000 |
| o4-mini | DataZoneStandard | 670 / 10s | 670,000 |
| o4-mini | GlobalStandard | 2,000 | 2,000,000 |
| text-embedding-3-large | DataZoneStandard | 2,000 | 2,000,000 |
| text-embedding-3-large | GlobalStandard | 2000 / 10s | 2,000,000 |
| text-embedding-3-small | DataZoneStandard | 2,000 | 2,000,000 |
| text-embedding-3-small | GlobalStandard | 2000 / 10s | 2,000,000 |

# [Tier 3](#tab/tier3)
### Tier 3

| Model Name | Deployment Type | Requests Per Minute (RPM) | Tokens Per Minute (TPM) |
| --- | --- | --- | --- |
| codex-mini | GlobalStandard | 4,000 | 4,000,000 |
| computer-use-preview | GlobalStandard | 70,000 | 7,000,000 |
| gpt-4.1 | DataZoneStandard | 3,000 | 3,000,000 |
| gpt-4.1 | GlobalStandard | 9,000 | 9,000,000 |
| gpt-4.1-mini | DataZoneStandard | 16,000 | 16,000,000 |
| gpt-4.1-mini | GlobalStandard | 46,000 | 46,000,000 |
| gpt-4.1-mini | Standard | 30,000 | 30,000,000 |
| gpt-4.1-nano | DataZoneStandard | 16,000 | 16,000,000 |
| gpt-4.1-nano | GlobalStandard | 46,000 | 46,000,000 |
| gpt-4o | DataZoneStandard | 3000 / 10s | 3,000,000 |
| gpt-4o-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini | DataZoneStandard | 70,000 | 7,000,000 |
| gpt-4o-mini | GlobalStandard | 330,000 | 33,000,000 |
| gpt-4o-mini-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-4o-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-5 | DataZoneStandard | 30,000 | 3,000,000 |
| gpt-5 | GlobalStandard | 90,000 | 9,000,000 |
| gpt-5-chat | GlobalStandard | 3,000 | 3,000,000 |
| gpt-5-codex | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5-mini | DataZoneStandard | 1,000 | 1,000,000 |
| gpt-5-mini | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5-nano | DataZoneStandard | 16,000 | 16,000,000 |
| gpt-5-nano | GlobalStandard | 46,000 | 46,000,000 |
| gpt-5-pro | GlobalStandard | 7,000 | 700,000 |
| gpt-5.1 | DataZoneStandard | 10,000 | 1,000,000 |
| gpt-5.1 | GlobalStandard | 40,000 | 4,000,000 |
| gpt-5.1 | Standard | 10,000 | 1,000,000 |
| gpt-5.1-chat | GlobalStandard | 30,000 | 3,000,000 |
| gpt-5.1-codex | DataZoneStandard | 10,000 | 1,000,000 |
| gpt-5.1-codex | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5.1-codex-max | GlobalStandard | 40,000 | 4,000,000 |
| gpt-5.1-codex-mini | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5.2 | DataZoneStandard | 10,000 | 1,000,000 |
| gpt-5.2 | GlobalStandard | 40,000 | 4,000,000 |
| gpt-5.2-chat | GlobalStandard | 30,000 | 3,000,000 |
| gpt-5.3-chat | GlobalStandard | 3,000 | 3,000,000 |
| gpt-5.2-codex | GlobalStandard | 40,000 | 4,000,000 |
| gpt-5.3-codex | GlobalStandard | 40,000 | 4,000,000 |
| gpt-5.4 | DataZoneStandard | 1,000 | 1,000,000 |
| gpt-5.4 | GlobalStandard | 40,000 | 4,000,000 |
| gpt-5.4-pro | GlobalStandard | 700 | 700,000 |
| gpt-5.4-mini | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5.4-nano | DataZoneStandard | 16,000 | 16,000,000 |
| gpt-5.4-nano | GlobalStandard | 46,000 | 46,000,000 |
| gpt-5.5 | DataZoneStandard | 1,333 | 1,333,000 |
| gpt-5.5 | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5.6-luna | DataZoneStandard | 1,333 | 1,333,000 |
| gpt-5.6-luna | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5.6-sol | DataZoneStandard | 1,333 | 1,333,000 |
| gpt-5.6-sol | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5.6-terra | DataZoneStandard | 1,333 | 1,333,000 |
| gpt-5.6-terra | GlobalStandard | 4,000 | 4,000,000 |
| gpt-chat-latest^1^ | GlobalStandard | 30,000 | 3,000,000 |
| gpt-chat-latest^2^ | GlobalStandard | 3,000 | 3,000,000 |
| gpt-audio | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-image-1 | GlobalStandard | 30 | - |
| gpt-image-1-mini | GlobalStandard | 54 | - |
| gpt-image-1.5 | DataZoneStandard | 10 | - |
| gpt-image-1.5 | GlobalStandard | 30 | - |
| gpt-image-2 | DataZoneStandard | 6 | - |
| gpt-image-2 | GlobalStandard | 18 | - |
| gpt-realtime | GlobalStandard | 200 | 100,000 |
| model-router | DataZoneStandard | 1,000 | 1,000,000 |
| model-router | GlobalStandard | 4,000 | 4,000,000 |
| o1 | DataZoneStandard | 450 | 2,700,000 |
| o1 | GlobalStandard | 2,000 | 12,000,000 |
| o3 | DataZoneStandard | 1,000 | 1,000,000 |
| o3 | GlobalStandard | 4,000 | 4,000,000 |
| o3-deep-research | GlobalStandard | 13,000 | 13,000,000 |
| o3-mini | DataZoneStandard | 900 | 9,000,000 |
| o3-mini | GlobalStandard | 2,000 | 20,000,000 |
| o3-pro | GlobalStandard | 715 | 7,150,000 |
| o4-mini | DataZoneStandard | 1000 / 10s | 1,000,000 |
| o4-mini | GlobalStandard | 4,000 | 4,000,000 |
| text-embedding-3-large | DataZoneStandard | 4,000 | 4,000,000 |
| text-embedding-3-large | GlobalStandard | 4000 / 10s | 4,000,000 |
| text-embedding-3-small | DataZoneStandard | 4,000 | 4,000,000 |
| text-embedding-3-small | GlobalStandard | 4000 / 10s | 4,000,000 |

# [Tier 4](#tab/tier4)
### Tier 4

| Model Name | Deployment Type | Requests Per Minute (RPM) | Tokens Per Minute (TPM) |
| --- | --- | --- | --- |
| codex-mini | GlobalStandard | 7,000 | 7,000,000 |
| computer-use-preview | GlobalStandard | 160,000 | 16,000,000 |
| gpt-4.1 | DataZoneStandard | 6,000 | 6,000,000 |
| gpt-4.1 | GlobalStandard | 18,000 | 18,000,000 |
| gpt-4.1-mini | DataZoneStandard | 31,000 | 31,000,000 |
| gpt-4.1-mini | GlobalStandard | 90,000 | 90,000,000 |
| gpt-4.1-mini | Standard | 75,000 | 75,000,000 |
| gpt-4.1-nano | DataZoneStandard | 31,000 | 31,000,000 |
| gpt-4.1-nano | GlobalStandard | 90,000 | 90,000,000 |
| gpt-4o | DataZoneStandard | 6000 / 10s | 6,000,000 |
| gpt-4o-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini | DataZoneStandard | 130,000 | 13,000,000 |
| gpt-4o-mini | GlobalStandard | 780,000 | 78,000,000 |
| gpt-4o-mini-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-4o-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-5 | DataZoneStandard | 60,000 | 6,000,000 |
| gpt-5 | GlobalStandard | 180,000 | 18,000,000 |
| gpt-5-chat | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5-codex | GlobalStandard | 7,000 | 7,000,000 |
| gpt-5-mini | DataZoneStandard | 2,000 | 2,000,000 |
| gpt-5-mini | GlobalStandard | 7,000 | 7,000,000 |
| gpt-5-nano | DataZoneStandard | 31,000 | 31,000,000 |
| gpt-5-nano | GlobalStandard | 90,000 | 90,000,000 |
| gpt-5-pro | GlobalStandard | 11,500 | 1,150,000 |
| gpt-5.1 | DataZoneStandard | 20,000 | 2,000,000 |
| gpt-5.1 | GlobalStandard | 70,000 | 7,000,000 |
| gpt-5.1 | Standard | 20,000 | 2,000,000 |
| gpt-5.1-chat | GlobalStandard | 40,000 | 4,000,000 |
| gpt-5.1-codex | DataZoneStandard | 20,000 | 2,000,000 |
| gpt-5.1-codex | GlobalStandard | 7,000 | 7,000,000 |
| gpt-5.1-codex-max | GlobalStandard | 70,000 | 7,000,000 |
| gpt-5.1-codex-mini | GlobalStandard | 7,000 | 7,000,000 |
| gpt-5.2 | DataZoneStandard | 20,000 | 2,000,000 |
| gpt-5.2 | GlobalStandard | 70,000 | 7,000,000 |
| gpt-5.2-chat | GlobalStandard | 40,000 | 4,000,000 |
| gpt-5.3-chat | GlobalStandard | 4,000 | 4,000,000 |
| gpt-5.2-codex | GlobalStandard | 70,000 | 7,000,000 |
| gpt-5.3-codex | GlobalStandard | 70,000 | 7,000,000 |
| gpt-5.4 | DataZoneStandard | 2,000 | 2,000,000 |
| gpt-5.4 | GlobalStandard | 70,000 | 7,000,000 |
| gpt-5.4-pro | GlobalStandard | 1,150 | 1,150,000 |
| gpt-5.4-mini | GlobalStandard | 7,000 | 7,000,000 |
| gpt-5.4-nano | DataZoneStandard | 31,000 | 31,000,000 |
| gpt-5.4-nano | GlobalStandard | 90,000 | 90,000,000 |
| gpt-5.5 | DataZoneStandard | 2,333 | 2,333,000 |
| gpt-5.5 | GlobalStandard | 7,000 | 7,000,000 |
| gpt-5.6-luna | DataZoneStandard | 2,333 | 2,333,000 |
| gpt-5.6-luna | GlobalStandard | 7,000 | 7,000,000 |
| gpt-5.6-sol | DataZoneStandard | 2,333 | 2,333,000 |
| gpt-5.6-sol | GlobalStandard | 7,000 | 7,000,000 |
| gpt-5.6-terra | DataZoneStandard | 2,333 | 2,333,000 |
| gpt-5.6-terra | GlobalStandard | 7,000 | 7,000,000 |
| gpt-chat-latest^1^ | GlobalStandard | 40,000 | 4,000,000 |
| gpt-chat-latest^2^ | GlobalStandard | 4,000 | 4,000,000 |
| gpt-audio | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-image-1 | GlobalStandard | 45 | - |
| gpt-image-1-mini | GlobalStandard | 84 | - |
| gpt-image-1.5 | DataZoneStandard | 15 | - |
| gpt-image-1.5 | GlobalStandard | 45 | - |
| gpt-image-2 | DataZoneStandard | 8 | - |
| gpt-image-2 | GlobalStandard | 24 | - |
| gpt-realtime | GlobalStandard | 200 | 100,000 |
| model-router | DataZoneStandard | 2,000 | 2,000,000 |
| model-router | GlobalStandard | 7,000 | 7,000,000 |
| o1 | DataZoneStandard | 700 | 4,200,000 |
| o1 | GlobalStandard | 4,000 | 24,000,000 |
| o3 | DataZoneStandard | 2,000 | 2,000,000 |
| o3 | GlobalStandard | 7,000 | 7,000,000 |
| o3-deep-research | GlobalStandard | 21,000 | 21,000,000 |
| o3-mini | DataZoneStandard | 1,000 | 10,000,000 |
| o3-mini | GlobalStandard | 4,000 | 40,000,000 |
| o3-pro | GlobalStandard | 1,150 | 11,500,000 |
| o4-mini | DataZoneStandard | 2000 / 10s | 2,000,000 |
| o4-mini | GlobalStandard | 7,000 | 7,000,000 |
| text-embedding-3-large | DataZoneStandard | 7,000 | 7,000,000 |
| text-embedding-3-large | GlobalStandard | 7000 / 10s | 7,000,000 |
| text-embedding-3-small | DataZoneStandard | 7,000 | 7,000,000 |
| text-embedding-3-small | GlobalStandard | 7000 / 10s | 7,000,000 |

# [Tier 5](#tab/tier5)
### Tier 5

| Model Name | Deployment Type | Requests Per Minute (RPM) | Tokens Per Minute (TPM) |
| --- | --- | --- | --- |
| codex-mini | GlobalStandard | 10,000 | 10,000,000 |
| computer-use-preview | GlobalStandard | 300,000 | 30,000,000 |
| gpt-4.1 | DataZoneStandard | 10,000 | 10,000,000 |
| gpt-4.1 | GlobalStandard | 30,000 | 30,000,000 |
| gpt-4.1-mini | DataZoneStandard | 50,000 | 50,000,000 |
| gpt-4.1-mini | GlobalStandard | 150,000 | 150,000,000 |
| gpt-4.1-mini | Standard | 150,000 | 150,000,000 |
| gpt-4.1-nano | DataZoneStandard | 50,000 | 50,000,000 |
| gpt-4.1-nano | GlobalStandard | 150,000 | 150,000,000 |
| gpt-4o | DataZoneStandard | 10000 / 10s | 10,000,000 |
| gpt-4o-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini | DataZoneStandard | 200,000 | 20,000,000 |
| gpt-4o-mini | GlobalStandard | 1,500,000 | 150,000,000 |
| gpt-4o-mini-audio-preview | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-4o-mini-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-4o-realtime-preview | GlobalStandard | 36 | 6,000 |
| gpt-5 | DataZoneStandard | 100,000 | 10,000,000 |
| gpt-5 | GlobalStandard | 300,000 | 30,000,000 |
| gpt-5-chat | GlobalStandard | 5,000 | 5,000,000 |
| gpt-5-codex | GlobalStandard | 10,000 | 10,000,000 |
| gpt-5-mini | DataZoneStandard | 3,000 | 3,000,000 |
| gpt-5-mini | GlobalStandard | 10,000 | 10,000,000 |
| gpt-5-nano | DataZoneStandard | 50,000 | 50,000,000 |
| gpt-5-nano | GlobalStandard | 150,000 | 150,000,000 |
| gpt-5-pro | GlobalStandard | 16,000 | 1,600,000 |
| gpt-5.1 | DataZoneStandard | 30,000 | 3,000,000 |
| gpt-5.1 | GlobalStandard | 100,000 | 10,000,000 |
| gpt-5.1 | Standard | 30,000 | 3,000,000 |
| gpt-5.1-chat | GlobalStandard | 50,000 | 5,000,000 |
| gpt-5.1-codex | DataZoneStandard | 30,000 | 3,000,000 |
| gpt-5.1-codex | GlobalStandard | 10,000 | 10,000,000 |
| gpt-5.1-codex-max | GlobalStandard | 100,000 | 10,000,000 |
| gpt-5.1-codex-mini | GlobalStandard | 10,000 | 10,000,000 |
| gpt-5.2 | DataZoneStandard | 30,000 | 3,000,000 |
| gpt-5.2 | GlobalStandard | 100,000 | 10,000,000 |
| gpt-5.2-chat | GlobalStandard | 50,000 | 5,000,000 |
| gpt-5.3-chat | GlobalStandard | 5,000 | 5,000,000 |
| gpt-5.2-codex | GlobalStandard | 100,000 | 10,000,000 |
| gpt-5.3-codex | GlobalStandard | 100,000 | 10,000,000 |
| gpt-5.4 | DataZoneStandard | 3,000 | 3,000,000 |
| gpt-5.4 | GlobalStandard | 100,000 | 10,000,000 |
| gpt-5.4-pro | GlobalStandard | 1,600 | 1,600,000 |
| gpt-5.4-mini | GlobalStandard | 10,000 | 10,000,000 |
| gpt-5.4-nano | DataZoneStandard | 50,000 | 50,000,000 |
| gpt-5.4-nano | GlobalStandard | 150,000 | 150,000,000 |
| gpt-5.5 | DataZoneStandard | 3,000 | 3,000,000 |
| gpt-5.5 | GlobalStandard | 10,000 | 10,000,000 |
| gpt-5.6-luna | DataZoneStandard | 3,333 | 3,333,000 |
| gpt-5.6-luna | GlobalStandard | 10,000 | 10,000,000 |
| gpt-5.6-sol | DataZoneStandard | 3,333 | 3,333,000 |
| gpt-5.6-sol | GlobalStandard | 10,000 | 10,000,000 |
| gpt-5.6-terra | DataZoneStandard | 3,333 | 3,333,000 |
| gpt-5.6-terra | GlobalStandard | 10,000 | 10,000,000 |
| gpt-chat-latest^1^ | GlobalStandard | 50,000 | 5,000,000 |
| gpt-chat-latest^2^ | GlobalStandard | 5,000 | 5,000,000 |
| gpt-audio | GlobalStandard | 30000 / 10s | 30,000,000 |
| gpt-image-1 | GlobalStandard | 60 | - |
| gpt-image-1-mini | GlobalStandard | 120 | - |
| gpt-image-1.5 | DataZoneStandard | 20 | - |
| gpt-image-1.5 | GlobalStandard | 60 | - |
| gpt-image-2 | DataZoneStandard | 10 | - |
| gpt-image-2 | GlobalStandard | 30 | - |
| gpt-realtime | GlobalStandard | 200 | 100,000 |
| model-router | DataZoneStandard | 3,000 | 3,000,000 |
| model-router | GlobalStandard | 10,000 | 10,000,000 |
| o1 | DataZoneStandard | 1,000 | 6,000,000 |
| o1 | GlobalStandard | 5,000 | 30,000,000 |
| o3 | DataZoneStandard | 3,000 | 3,000,000 |
| o3 | GlobalStandard | 10,000 | 10,000,000 |
| o3-deep-research | GlobalStandard | 30,000 | 30,000,000 |
| o3-mini | DataZoneStandard | 2,000 | 20,000,000 |
| o3-mini | GlobalStandard | 5,000 | 50,000,000 |
| o3-pro | GlobalStandard | 1,600 | 16,000,000 |
| o4-mini | DataZoneStandard | 3000 / 10s | 3,000,000 |
| o4-mini | GlobalStandard | 10,000 | 10,000,000 |
| text-embedding-3-large | DataZoneStandard | 10,000 | 10,000,000 |
| text-embedding-3-large | GlobalStandard | 10000 / 10s | 10,000,000 |
| text-embedding-3-small | DataZoneStandard | 10,000 | 10,000,000 |
| text-embedding-3-small | GlobalStandard | 10000 / 10s | 10,000,000 |

# [Tier 6](#tab/tier6)
### Tier 6

| Model Name | Deployment Type | Requests Per Minute (RPM) | Tokens Per Minute (TPM) |
| --- | --- | --- | --- |
| codex-mini | GlobalStandard | 15,000 | 15,000,000 |
| computer-use-preview | GlobalStandard | 450,000 | 45,000,000 |
| gpt-4.1 | DataZoneStandard | 15,000 | 15,000,000 |
| gpt-4.1 | GlobalStandard | 45,000 | 45,000,000 |
| gpt-4.1-mini | DataZoneStandard | 75,000 | 75,000,000 |
| gpt-4.1-mini | GlobalStandard | 225,000 | 225,000,000 |
| gpt-4.1-mini | Standard | 225,000 | 225,000,000 |
| gpt-4.1-nano | DataZoneStandard | 75,000 | 75,000,000 |
| gpt-4.1-nano | GlobalStandard | 225,000 | 225,000,000 |
| gpt-4o | DataZoneStandard | 15000 / 10s | 15,000,000 |
| gpt-4o-audio-preview | GlobalStandard | 45000 / 10s | 45,000,000 |
| gpt-4o-mini | DataZoneStandard | 300,000 | 30,000,000 |
| gpt-4o-mini | GlobalStandard | 2,250,000 | 225,000,000 |
| gpt-4o-mini-audio-preview | GlobalStandard | 45000 / 10s | 45,000,000 |
| gpt-4o-mini-realtime-preview | GlobalStandard | 54 | 9,000 |
| gpt-4o-realtime-preview | GlobalStandard | 54 | 9,000 |
| gpt-5 | DataZoneStandard | 150,000 | 15,000,000 |
| gpt-5 | GlobalStandard | 450,000 | 45,000,000 |
| gpt-5-chat | GlobalStandard | 8,000 | 8,000,000 |
| gpt-5-codex | GlobalStandard | 15,000 | 15,000,000 |
| gpt-5-mini | DataZoneStandard | 4,000 | 4,000,000 |
| gpt-5-mini | GlobalStandard | 15,000 | 15,000,000 |
| gpt-5-nano | DataZoneStandard | 75,000 | 75,000,000 |
| gpt-5-nano | GlobalStandard | 225,000 | 225,000,000 |
| gpt-5-pro | GlobalStandard | 24,000 | 2,400,000 |
| gpt-5.1 | DataZoneStandard | 40,000 | 4,000,000 |
| gpt-5.1 | GlobalStandard | 150,000 | 15,000,000 |
| gpt-5.1 | Standard | 40,000 | 4,000,000 |
| gpt-5.1-chat | GlobalStandard | 80,000 | 8,000,000 |
| gpt-5.1-codex | DataZoneStandard | 40,000 | 4,000,000 |
| gpt-5.1-codex | GlobalStandard | 15,000 | 15,000,000 |
| gpt-5.1-codex-max | GlobalStandard | 150,000 | 15,000,000 |
| gpt-5.1-codex-mini | GlobalStandard | 15,000 | 15,000,000 |
| gpt-5.2 | DataZoneStandard | 40,000 | 4,000,000 |
| gpt-5.2 | GlobalStandard | 150,000 | 15,000,000 |
| gpt-5.2-chat | GlobalStandard | 80,000 | 8,000,000 |
| gpt-5.3-chat | GlobalStandard | 8,000 | 8,000,000 |
| gpt-5.2-codex | GlobalStandard | 150,000 | 15,000,000 |
| gpt-5.3-codex | GlobalStandard | 150,000 | 15,000,000 |
| gpt-5.4 | DataZoneStandard | 4,000 | 4,000,000 |
| gpt-5.4 | GlobalStandard | 150,000 | 15,000,000 |
| gpt-5.4-pro | GlobalStandard | 2,400 | 2,400,000 |
| gpt-5.4-mini | GlobalStandard | 15,000 | 15,000,000 |
| gpt-5.4-nano | DataZoneStandard | 75,000 | 75,000,000 |
| gpt-5.4-nano | GlobalStandard | 225,000 | 225,000,000 |
| gpt-5.5 | DataZoneStandard | 5,000 | 5,000,000 |
| gpt-5.5 | GlobalStandard | 15,000 | 15,000,000 |
| gpt-5.6-luna | DataZoneStandard | 5,000 | 5,000,000 |
| gpt-5.6-luna | GlobalStandard | 15,000 | 15,000,000 |
| gpt-5.6-sol | DataZoneStandard | 5,000 | 5,000,000 |
| gpt-5.6-sol | GlobalStandard | 15,000 | 15,000,000 |
| gpt-5.6-terra | DataZoneStandard | 5,000 | 5,000,000 |
| gpt-5.6-terra | GlobalStandard | 15,000 | 15,000,000 |
| gpt-chat-latest^1^ | GlobalStandard | 80,000 | 8,000,000 |
| gpt-chat-latest^2^ | GlobalStandard | 8,000 | 8,000,000 |
| gpt-audio | GlobalStandard | 45000 / 10s | 45,000,000 |
| gpt-image-1 | GlobalStandard | 90 | - |
| gpt-image-1-mini | GlobalStandard | 180 | - |
| gpt-image-1.5 | DataZoneStandard | 30 | - |
| gpt-image-1.5 | GlobalStandard | 90 | - |
| gpt-image-2 | DataZoneStandard | 12 | - |
| gpt-image-2 | GlobalStandard | 36 | - |
| gpt-realtime | GlobalStandard | 300 | 150,000 |
| model-router | DataZoneStandard | 4,000 | 4,000,000 |
| model-router | GlobalStandard | 15,000 | 15,000,000 |
| o1 | DataZoneStandard | 2,000 | 12,000,000 |
| o1 | GlobalStandard | 8,000 | 48,000,000 |
| o3 | DataZoneStandard | 4,000 | 4,000,000 |
| o3 | GlobalStandard | 15,000 | 15,000,000 |
| o3-deep-research | GlobalStandard | 45,000 | 45,000,000 |
| o3-mini | DataZoneStandard | 3,000 | 30,000,000 |
| o3-mini | GlobalStandard | 8,000 | 80,000,000 |
| o3-pro | GlobalStandard | 2,400 | 24,000,000 |
| o4-mini | DataZoneStandard | 4000 / 10s | 4,000,000 |
| o4-mini | GlobalStandard | 15,000 | 15,000,000 |
| text-embedding-3-large | DataZoneStandard | 15,000 | 15,000,000 |
| text-embedding-3-large | GlobalStandard | 15000 / 10s | 15,000,000 |
| text-embedding-3-small | DataZoneStandard | 15,000 | 15,000,000 |
| text-embedding-3-small | GlobalStandard | 15000 / 10s | 15,000,000 |

# [Tier 0](#tab/tier0)
### Tier 0

| Model Name | Deployment Type | Requests Per Minute (RPM) | Tokens Per Minute (TPM) |
| --- | --- | --- | --- |
| gpt-4.1-mini | GlobalStandard | 200 | 200,000 |
| gpt-5-mini | GlobalStandard | 500 | 500,000 |
| o4-mini | GlobalStandard | 100 | 100,000 |
| text-embedding-3-small | GlobalStandard | 1000 / 10s | 1,000,000 |

---

## Quotas and limits reference

The following section provides you with a quick guide to the default quotas and limits that apply to Azure OpenAI:

| Limit name | Limit value |
| --- | --- |
| Azure OpenAI resources per Azure subscription | 30. |
| Default GPT-image-1 quota limits | 9 requests per minute |
| Default GPT-image-1-mini quota limits | 12 requests per minute |
| Default GPT-image-1.5 quota limits | 9 requests per minute |
| Default GPT-image-2 quota limits | 9 requests per minute |
| Default Sora quota limits | 60 requests per minute. |
| Default Sora 2 quota limits | 2 job requests^1^ per minute |
| Default speech-to-text audio API quota limits | 3 requests per minute. |
| Maximum prompt tokens per request | Varies per model. For more information, see [Azure OpenAI models](../foundry-models/concepts/models-sold-directly-by-azure). |
| Maximum standard deployments per resource | 32. |
| Maximum fine-tuned model deployments | 10. |
| Total number of training jobs per resource | 100. |
| Maximum simultaneously running training jobs per resource | Standard and global training: 3;  Developer training: 5 |
| Maximum training jobs queued | 20. |
| Maximum files per resource (fine-tuning) | 100. |
| Total size of all files per resource (fine-tuning) | 1 GB. |
| Maximum training job time (job fails if exceeded) | 720 hours. |
| Maximum training job size `(tokens in training file) x (# of epochs)` | 2 billion. |
| Maximum size of all files per upload (Azure OpenAI on your data) | 16 MB. |
| Maximum number of inputs in array with `/embeddings` | 2,048. |
| Maximum tokens per `/embeddings` request (sum across all inputs) | 300,000. |
| Maximum number of `/chat/completions` messages | 2,048. |
| Maximum number of `/chat/completions` functions | 128. |
| Maximum number of `/chat/completions` tools | 128. |
| Maximum number of provisioned throughput units per deployment | 100,000. |
| Maximum files per assistant or thread | 10,000 when using the API or the [Microsoft Foundry portal](https://ai.azure.com/?cid=learnDocs). |
| Maximum file size for assistants and fine-tuning | 512 MB via the API200 MB via the [Foundry portal](https://ai.azure.com/?cid=learnDocs). |
| Maximum file upload requests per resource | 30 requests per second. |
| Maximum size for all uploaded files for assistants | 200 GB. |
| Assistants token limit | 2,000,000 token limit. |
| `GPT-4o` and `GPT-4.1` maximum images per request (number of images in the messages array or conversation history) | 50. |
| `GPT-4 vision-preview` and `GPT-4 turbo-2024-04-09` default maximum tokens | 16.  Increase the `max_tokens` parameter value to avoid truncated responses. `GPT-4o` maximum tokens defaults to 4,096. |
| Maximum number of custom headers in API requests^2^ | 10. |
| Message character limit | 1,048,576. |
| Message size for audio files | 20 MB. |

^1^ The Sora 2 RPM quota only counts video job requests. Other types of requests aren't rate-limited.

^2^ Our current APIs allow up to 10 custom headers, which are passed through the pipeline and returned. Some customers now exceed this header count, which results in HTTP 431 errors. There's no solution for this error, other than to reduce header volume. In future API versions, we won't pass through custom headers. We recommend that customers don't depend on custom headers in future system architectures.

Note

Quota limits are subject to change.

## Batch limits

| Limit name | Limit value |
| --- | --- |
| Maximum batch input files (no expiration) | 500 |
| Maximum batch input files (expiration set) | 10,000 |
| Maximum input file size | 200 MB |
| Maximum input file size - [Bring your own storage (BYOS)](../../foundry-classic/openai/how-to/batch-blob-storage) | 1 GB |
| Maximum requests per file | 100,000 |

Note

Set expiration for input files to increase the per-resource limit and manage stored files. Batch input file limits don't apply to output files, such as `result.jsonl` and `error.jsonl`. To avoid Files API input file limits, use [Batch with Azure Blob Storage](../../foundry-classic/openai/how-to/batch-blob-storage).

## Batch quota

The table shows the batch quota limit. Quota values for global batch are represented in terms of enqueued tokens. When you submit a file for batch processing, the number of tokens in the file is counted. Until the batch job reaches a terminal state, those tokens count against your total enqueued token limit.

### Global batch

| Model | Enterprise and MCA-E | Default | Monthly credit card-based subscriptions | MSDN subscriptions | Azure for Students, free trials |
| --- | --- | --- | --- | --- | --- |
| `gpt-4.1` | 5B | 200M | 50M | 90K | N/A |
| `gpt-4.1 mini` | 15B | 1B | 50M | 90K | N/A |
| `gpt-4.1-nano` | 15B | 1B | 50M | 90K | N/A |
| `gpt-4o` | 5B | 200M | 50M | 90K | N/A |
| `gpt-4o-mini` | 15B | 1B | 50M | 90K | N/A |
| `gpt-4-turbo` | 300M | 80M | 40M | 90K | N/A |
| `gpt-4` | 150M | 30M | 5M | 100K | N/A |
| `o3-mini` | 15B | 1B | 50M | 90K | N/A |
| `o4-mini` | 15B | 1B | 50M | 90K | N/A |
| `gpt-5` | 5B | 200M | 50M | 90K | N/A |
| `gpt-5.1` | 5B | 200M | 50M | 90K | N/A |
| `gpt-5.2` | 5B | 200M | 50M | N/A | N/A |
| `gpt-5.4` | 5B | 200M | 50M | N/A | N/A |
| `gpt-5.4-mini` | 5B | 200M | 50M | N/A | N/A |
| `gpt-5.4-nano` | 5B | 200M | 50M | N/A | N/A |
| `gpt-5.5` | 5B | 200M | 50M | 90K | N/A |

B = billion | M = million | K = thousand

### Data zone batch

| Model | Enterprise and MCA-E | Default | Monthly credit card-based subscriptions | MSDN subscriptions | Azure for Students, free trials |
| --- | --- | --- | --- | --- | --- |
| `gpt-4.1` | 500M | 30M | 30M | 90K | N/A |
| `gpt-4.1-mini` | 1.5B | 100M | 50M | 90K | N/A |
| `gpt-4o` | 500M | 30M | 30M | 90K | N/A |
| `gpt-4o-mini` | 1.5B | 100M | 50M | 90K | N/A |
| `o3-mini` | 1.5B | 100M | 50M | 90K | N/A |
| `gpt-5` | 5B | 200M | 50M | 90K | N/A |
| `gpt-5.1` | 5B | 200M | 50M | 90K | N/A |
| `gpt-5.4` | 5B | 200M | 50M | N/A | N/A |
| `gpt-5.4-mini` | 5B | 200M | 50M | N/A | N/A |
| `gpt-5.5` | 5B | 200M | 50M | 90K | N/A |

## gpt-oss

| Model | Tokens per minute (TPM) | Requests per minute (RPM) |
| --- | --- | --- |
| `gpt-oss-120b` | 5 M | 5 K |

## Usage tiers

Global Standard deployments use the global infrastructure of Azure. They dynamically route customer traffic to the data center with the best availability for the customer's inference requests. Similarly, Data Zone Standard deployments allow you to use the global infrastructure of Azure to dynamically route traffic to the data center within the Microsoft-defined data zone with the best availability for each request. This practice enables more consistent latency for customers with low to medium levels of traffic. Customers with high sustained levels of usage might see greater variability in response latency.

Azure OpenAI usage tiers are designed to provide consistent performance for most customers with low to medium levels of traffic. Each usage tier defines the maximum throughput (tokens per minute) you can expect with predictable latency. When your usage stays within your assigned tier, latency remains stable and response times are consistent.

### What happens if you exceed your usage tier?

- If your request throughput exceeds your usage tier—especially during periods of high demand—your response latency may increase significantly.
- Latency can vary and, in some cases, may be more than two times higher than when operating within your usage tier.
- This variability is most noticeable for customers with high sustained usage or bursty traffic patterns.

### Recommended actions if you exceed your usage tier

If you encounter 429 errors or notice increased latency variability, take the following steps:

- Request a quota increase: visit the Azure portal to request a higher quota for your subscription.
- Consider upgrading to a premium offer (PTU): for latency-critical or high-volume workloads, upgrade to Provisioned Throughput Units (PTU). PTU provides dedicated resources, guaranteed capacity, and predictable latency—even at scale. This is the best choice for mission-critical applications that require consistent performance.
- Monitor your usage: regularly review your usage metrics in the Azure portal to ensure you're operating within your tier limits. Adjust your workload or deployment strategy as needed.

You might receive **429 (Too Many Requests)** responses even when token usage metrics appear below your quota. For an explanation of why this happens, see [Why you might see 429s even when token usage metrics are below quota](how-to/quota#why-you-might-see-429s-even-when-token-usage-metrics-are-below-quota).

The usage limit determines the level of usage above which customers might see larger variability in response latency. A customer's usage is defined per model. It's the total number of tokens consumed across all deployments in all subscriptions in all regions for a given tenant.

Note

Usage tiers apply only to Standard, Data Zone Standard, and Global Standard deployment types. Usage tiers don't apply to global batch and provisioned throughput deployments.

### Global Standard, Data Zone Standard, and Standard

| Model | Usage tiers per month |
| --- | --- |
| `gpt-5` | 32 billion tokens |
| `gpt-5-mini` | 160 billion tokens |
| `gpt-5-nano` | 800 billion tokens |
| `gpt-5-chat` | 32 billion tokens |
| `gpt-4` + `gpt-4-32k` (all versions) | 6 billion tokens |
| `gpt-4o` | 12 billion tokens |
| `gpt-4o-mini` | 85 billion tokens |
| `o3-mini` | 50 billion tokens |
| `o1` | 4 billion tokens |
| `o4-mini` | 50 billion tokens |
| `o3` | 5 billion tokens |
| `gpt-4.1` | 30 billion tokens |
| `gpt-4.1-mini` | 150 billion tokens |
| `gpt-4.1-nano` | 550 billion tokens |
| `gpt-5.1` | 86 billion tokens |
| `gpt-5.1-codex` | 86 billion tokens |
| `gpt-5.2` | 60 billion tokens |
| `gpt-5.3-codex` | 60 billion tokens |
| `gpt-5.4` | 50 billion tokens |
| `gpt-5.4-mini` | 165 billion tokens |
| `gpt-5.4-nano` | 605 billion tokens |
| `gpt-5.5` | 25 billion tokens |
| `gpt-5.6-sol` | 25 billion tokens |

### General best practices to remain within rate limits

To minimize issues related to rate limits, it's a good idea to use the following techniques:

- Implement retry logic in your application.
- Avoid sharp changes in the workload. Increase the workload gradually.
- Test different load increase patterns.
- Increase the quota assigned to your deployment. Move quota from another deployment, if necessary.

For detailed best practices, retry-with-backoff code samples, and a 429 troubleshooting guide, see [Manage Azure OpenAI in Microsoft Foundry Models quota](how-to/quota#rate-limit-best-practices).

## Request quota increases

Submit the [quota increase request form](https://aka.ms/oai/stuquotarequest) to request quota increases for [Foundry Models sold by Azure](../foundry-models/concepts/models-sold-directly-by-azure), Azure OpenAI models, and Anthropic models. Except for Anthropic models, [Models from partners and community](../foundry-models/concepts/models-from-partners) don't support quota increases.

Quota increase requests are processed in the order they're received, and priority goes to customers who actively use their existing quota allocation. Requests that don't meet this condition might be denied.

## Regional quota capacity limits

You can view quota availability by region for your subscription in the [Foundry portal](https://ai.azure.com/resource/quota).

To check quota and capacity programmatically, see [Programmatically check quota and capacity](how-to/quota#programmatically-check-quota-and-capacity) in the quota management guide. That section covers two complementary REST APIs: the **Usages API** for checking consumption against limits, and the **Model Capacities API** for checking available deployment capacity by model and region.

Note

Currently, both the Foundry portal and the capacity APIs return quota and capacity information for models that are [retired](concepts/model-retirements) and no longer available for new deployments.
