---
layout: Reference
monikers:
- azure-cli-latest
defaultMoniker: azure-cli-latest
versioningType: Ranged
title: az account | Microsoft Learn
canonicalUrl: https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-latest
config_moniker_range: azure-cli-latest
uid: az_account
breadcrumb_path: /cli/azure/breadcrumb/toc.json
feedback_system: OpenSource
feedback_product_url: https://github.com/Azure/azure-cli/issues/new/choose
feedback_help_link_url: https://techcommunity.microsoft.com/t5/azure/ct-p/Azure
feedback_help_link_type: ask-the-community
keywords: azure, cli, command line
author: mikefrobbins
ms.author: mirobb
ms.manager: akashdubey
ms.date: 2026-08-04T00:00:00.0000000Z
ms.devlang: azurecli
ms.service: azure
uhfHeaderId: Azure
devlang: azurecli
ms.topic: generated-reference
locale: en-us
document_id: 0a576abb-da6e-eca7-ff6b-f0e8e95eb0f6
document_version_independent_id: b04eb8a3-36fa-1e6f-cd44-40f5c6ba45b7
updated_at: 2026-04-07T08:52:00.0000000Z
original_content_git_url: https://github.com/MicrosoftDocs/azure-docs-cli/blob/live/docs-ref-autogen/Latest-version/latest/account.yml
gitcommit: https://github.com/MicrosoftDocs/azure-docs-cli/blob/6eda315c56043d2331b33b5d5b77bca41b526645/docs-ref-autogen/Latest-version/latest/account.yml
git_commit_id: 6eda315c56043d2331b33b5d5b77bca41b526645
default_moniker: azure-cli-latest
site_name: Docs
depot_name: Azure.azure-cli-docs
page_type: azure-cli
page_kind: group
interactive_type: azurecli
toc_rel: command/toc.json
asset_id: account
moniker_range_name: 222556dbd796e16164f44898973c0b99
monikers:
- azure-cli-latest
item_type: Content
source_path: docs-ref-autogen/Latest-version/latest/account.yml
platformId: c108e56f-c736-aa21-47d3-629725ad4646
---

# az account

Note

This command group has commands that are defined in both Azure CLI and at least one extension. Install each extension to benefit from its extended capabilities. [Learn more](/en-us/cli/azure/azure-cli-extensions-overview) about extensions.

Manage Azure subscription information.

## Commands

| Name | Description | Type | Status |
| --- | --- | --- | --- |
| [az account accept-ownership-status](account#az-account-accept-ownership-status) | Accept subscription ownership status. | Extension | GA |
| [az account alias](account/alias) | Manage subscription alias. | Extension | GA |
| [az account alias create](account/alias#az-account-alias-create) | Create Alias Subscription. | Extension | GA |
| [az account alias delete](account/alias#az-account-alias-delete) | Delete Alias. | Extension | GA |
| [az account alias list](account/alias#az-account-alias-list) | List Alias Subscriptions. | Extension | GA |
| [az account alias show](account/alias#az-account-alias-show) | Get Alias Subscription. | Extension | GA |
| [az account alias wait](account/alias#az-account-alias-wait) | Place the CLI in a waiting state until a condition of the account alias is met. | Extension | GA |
| [az account clear](account#az-account-clear) | Clear all subscriptions from the CLI's local cache. | Core | GA |
| [az account create](account#az-account-create) | Create a subscription. | Extension | Preview |
| [az account get-access-token](account#az-account-get-access-token) | Get a token for utilities to access Azure. | Core | GA |
| [az account list](account#az-account-list) | Get a list of subscriptions for the logged in account. By default, only 'Enabled' subscriptions from the current cloud is shown. | Core | GA |
| [az account list-locations](account#az-account-list-locations) | List supported regions for the current subscription. | Core | GA |
| [az account lock](account/lock) | Manage Azure subscription level locks. | Core | GA |
| [az account lock create](account/lock#az-account-lock-create) | Create a subscription lock. | Core | GA |
| [az account lock delete](account/lock#az-account-lock-delete) | Delete a subscription lock. | Core | GA |
| [az account lock list](account/lock#az-account-lock-list) | List lock information in the subscription. | Core | GA |
| [az account lock show](account/lock#az-account-lock-show) | Show the details of a subscription lock. | Core | GA |
| [az account lock update](account/lock#az-account-lock-update) | Update a subscription lock. | Core | GA |
| [az account management-group](account/management-group) | Manage Azure Management Groups. | Core | GA |
| [az account management-group check-name-availability](account/management-group#az-account-management-group-check-name-availability) | Check if a Management Group Name is Valid. | Core | GA |
| [az account management-group create](account/management-group#az-account-management-group-create) | Create a new management group. | Core | GA |
| [az account management-group delete](account/management-group#az-account-management-group-delete) | Delete an existing management group. | Core | GA |
| [az account management-group entities](account/management-group/entities) | Entity operations (Management Group and Subscriptions) for Management Groups. | Core | GA |
| [az account management-group entities list](account/management-group/entities#az-account-management-group-entities-list) | List all entities for the authenticated user. | Core | GA |
| [az account management-group hierarchy-settings](account/management-group/hierarchy-settings) | Provide operations for hierarchy settings defined at the management group level. Settings can only be set on the root Management Group of the hierarchy. | Core | GA |
| [az account management-group hierarchy-settings create](account/management-group/hierarchy-settings#az-account-management-group-hierarchy-settings-create) | Create hierarchy settings defined at the Management Group level. | Core | GA |
| [az account management-group hierarchy-settings delete](account/management-group/hierarchy-settings#az-account-management-group-hierarchy-settings-delete) | Delete the hierarchy settings defined at the Management Group level. | Core | GA |
| [az account management-group hierarchy-settings list](account/management-group/hierarchy-settings#az-account-management-group-hierarchy-settings-list) | Get all the hierarchy settings defined at the Management Group level. | Core | GA |
| [az account management-group hierarchy-settings update](account/management-group/hierarchy-settings#az-account-management-group-hierarchy-settings-update) | Update the hierarchy settings defined at the Management Group level. | Core | GA |
| [az account management-group list](account/management-group#az-account-management-group-list) | List all management groups in the current tenant. | Core | GA |
| [az account management-group show](account/management-group#az-account-management-group-show) | Get the details of the management group. | Core | GA |
| [az account management-group subscription](account/management-group/subscription) | Subscription operations for Management Groups. | Core | GA |
| [az account management-group subscription add](account/management-group/subscription#az-account-management-group-subscription-add) | Add a subscription to a management group. | Core | GA |
| [az account management-group subscription remove](account/management-group/subscription#az-account-management-group-subscription-remove) | Remove an existing subscription from a management group. | Core | GA |
| [az account management-group subscription show](account/management-group/subscription#az-account-management-group-subscription-show) | Show the details of a subscription under a known management group. | Core | GA |
| [az account management-group subscription show-sub-under-mg](account/management-group/subscription#az-account-management-group-subscription-show-sub-under-mg) | Get the subscription under a management group. | Core | GA |
| [az account management-group tenant-backfill](account/management-group/tenant-backfill) | Backfill Tenant Subscription Operations for Management Groups. | Core | GA |
| [az account management-group tenant-backfill get](account/management-group/tenant-backfill#az-account-management-group-tenant-backfill-get) | Get the backfill status for a tenant. | Core | GA |
| [az account management-group tenant-backfill start](account/management-group/tenant-backfill#az-account-management-group-tenant-backfill-start) | Start backfilling subscriptions for a tenant. | Core | GA |
| [az account management-group update](account/management-group#az-account-management-group-update) | Update an existing management group. | Core | GA |
| [az account set](account#az-account-set) | Set a subscription to be the current active subscription. | Core | GA |
| [az account show](account#az-account-show) | Get the details of a subscription. | Core | GA |
| [az account subscription](account/subscription) | Manage subscriptions. | Extension | Experimental |
| [az account subscription cancel](account/subscription#az-account-subscription-cancel) | Cancel subscription. | Extension | Experimental |
| [az account subscription enable](account/subscription#az-account-subscription-enable) | Enable subscription. | Extension | Experimental |
| [az account subscription list](account/subscription#az-account-subscription-list) | Get all subscriptions for a tenant. | Extension | Experimental |
| [az account subscription list-location](account/subscription#az-account-subscription-list-location) | This operation provides all the locations that are available for resource providers; however, each resource provider may support a subset of this list. | Extension | Experimental |
| [az account subscription rename](account/subscription#az-account-subscription-rename) | Rename subscription. | Extension | Experimental |
| [az account subscription show](account/subscription#az-account-subscription-show) | Get details about a specified subscription. | Extension | Experimental |
| [az account tenant](account/tenant) | Manage tenant. | Extension | Experimental |
| [az account tenant list](account/tenant#az-account-tenant-list) | Get the tenants for your account. | Extension | Experimental |

## az account accept-ownership-status

Accept subscription ownership status.

```azurecli
az account accept-ownership-status --subscription-id
                                   [--acquire-policy-token]
                                   [--change-reference]
```

### Required Parameters

--subscription-id

Subscription Id. Required.

### Optional Parameters

The following parameters are optional, but depending on the context, one or more might become required for the command to execute successfully.

--acquire-policy-token

Acquiring an Azure Policy token automatically for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--change-reference

The related change reference ID for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

 Global Parameters 

--debug

Increase logging verbosity to show all debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

--help -h

Show this help message and exit.

--only-show-errors

Only show errors, suppressing warnings.

| Property | Value |
| --- | --- |
| Default value: | False |

--output -o

Output format.

| Property | Value |
| --- | --- |
| Default value: | json |
| Accepted values: | json, jsonc, none, table, tsv, yaml, yamlc |

--query

JMESPath query string. See http://jmespath.org/ for more information and examples.

--verbose

Increase logging verbosity. Use --debug for full debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

## az account clear

Clear all subscriptions from the CLI's local cache.

To clear the current subscription, use 'az logout'.

```azurecli
az account clear [--acquire-policy-token]
                 [--change-reference]
```

### Optional Parameters

The following parameters are optional, but depending on the context, one or more might become required for the command to execute successfully.

--acquire-policy-token

Acquiring an Azure Policy token automatically for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--change-reference

The related change reference ID for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

 Global Parameters 

--debug

Increase logging verbosity to show all debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

--help -h

Show this help message and exit.

--only-show-errors

Only show errors, suppressing warnings.

| Property | Value |
| --- | --- |
| Default value: | False |

--output -o

Output format.

| Property | Value |
| --- | --- |
| Default value: | json |
| Accepted values: | json, jsonc, none, table, tsv, yaml, yamlc |

--query

JMESPath query string. See http://jmespath.org/ for more information and examples.

--verbose

Increase logging verbosity. Use --debug for full debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

## az account create

Preview

This command is in preview and under development. Reference and support levels: https://aka.ms/CLI_refstatus

Create a subscription.

```azurecli
az account create --enrollment-account-name --enrollment-account-object-id
                  --offer-type {MS-AZR-0017P, MS-AZR-0148P, MS-AZR-USGOV-0015P, MS-AZR-USGOV-0017P, MS-AZR-USGOV-0148P}
                  [--acquire-policy-token]
                  [--change-reference]
                  [--display-name]
                  [--no-wait {0, 1, f, false, n, no, t, true, y, yes}]
                  [--owner-object-id]
                  [--owner-spn]
                  [--owner-upn]
```

### Required Parameters

--enrollment-account-name --enrollment-account-object-id

The name of the enrollment account to which the subscription will be billed.

--offer-type

The offer type of the subscription. For example, MS-AZR-0017P(EnterpriseAgreement) and MS-AZR-0148P(EnterpriseAgreement devTest) are available. Allowed values: MS-AZR-0017P, MS-AZR-0148P, MS-AZR-USGOV-0015P, MS-AZR-USGOV-0017P, MS-AZR-USGOV-0148P.

| Property | Value |
| --- | --- |
| Accepted values: | MS-AZR-0017P, MS-AZR-0148P, MS-AZR-USGOV-0015P, MS-AZR-USGOV-0017P, MS-AZR-USGOV-0148P |

### Optional Parameters

The following parameters are optional, but depending on the context, one or more might become required for the command to execute successfully.

--acquire-policy-token

Acquiring an Azure Policy token automatically for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--change-reference

The related change reference ID for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--display-name

The display name of the subscription.

--no-wait

Do not wait for the long-running operation to finish.

| Property | Value |
| --- | --- |
| Accepted values: | 0, 1, f, false, n, no, t, true, y, yes |

--owner-object-id

The object id(s) of the owner(s) which should be granted access to the new subscription.

--owner-spn

The service principal name(s) of the owner(s) which should be granted access to the new subscription.

--owner-upn

The user principal name(s) of owner(s) who should be granted access to the new subscription.

 Global Parameters 

--debug

Increase logging verbosity to show all debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

--help -h

Show this help message and exit.

--only-show-errors

Only show errors, suppressing warnings.

| Property | Value |
| --- | --- |
| Default value: | False |

--output -o

Output format.

| Property | Value |
| --- | --- |
| Default value: | json |
| Accepted values: | json, jsonc, none, table, tsv, yaml, yamlc |

--query

JMESPath query string. See http://jmespath.org/ for more information and examples.

--verbose

Increase logging verbosity. Use --debug for full debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

## az account get-access-token

Get a token for utilities to access Azure.

The token will be valid for at least 5 minutes with the maximum at 60 minutes. If the subscription argument isn't specified, the current account is used.

In the output, `expires_on` represents a POSIX timestamp and `expiresOn` represents a local datetime. It is recommended for downstream applications to use `expires_on` because it is in UTC.

```azurecli
az account get-access-token [--acquire-policy-token]
                            [--change-reference]
                            [--name --subscription]
                            [--resource]
                            [--resource-type {aad-graph, arm, batch, data-lake, media, ms-graph, oss-rdbms}]
                            [--scope]
                            [--tenant]
```

### Examples

Get an access token for the current account

```azurecli
az account get-access-token
```

Get an access token for a specific subscription

```azurecli
az account get-access-token --subscription 00000000-0000-0000-0000-000000000000
```

Get an access token for a specific tenant

```azurecli
az account get-access-token --tenant 00000000-0000-0000-0000-000000000000
```

Get an access token to use with MS Graph API

```azurecli
az account get-access-token --resource-type ms-graph
```

### Optional Parameters

The following parameters are optional, but depending on the context, one or more might become required for the command to execute successfully.

--acquire-policy-token

Acquiring an Azure Policy token automatically for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--change-reference

The related change reference ID for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--name --subscription -n -s

Name or ID of subscription.

--resource

Azure resource endpoints in Microsoft Entra v1.0.

--resource-type

Type of well-known resource.

| Property | Value |
| --- | --- |
| Accepted values: | aad-graph, arm, batch, data-lake, media, ms-graph, oss-rdbms |

--scope

Space-separated scopes in Microsoft Entra v2.0. Default to Azure Resource Manager.

--tenant -t

Tenant ID for which the token is acquired. Only available for user and service principal account, not for managed identity or Cloud Shell account.

 Global Parameters 

--debug

Increase logging verbosity to show all debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

--help -h

Show this help message and exit.

--only-show-errors

Only show errors, suppressing warnings.

| Property | Value |
| --- | --- |
| Default value: | False |

--output -o

Output format.

| Property | Value |
| --- | --- |
| Default value: | json |
| Accepted values: | json, jsonc, none, table, tsv, yaml, yamlc |

--query

JMESPath query string. See http://jmespath.org/ for more information and examples.

--verbose

Increase logging verbosity. Use --debug for full debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

## az account list

Get a list of subscriptions for the logged in account. By default, only 'Enabled' subscriptions from the current cloud is shown.

```azurecli
az account list [--all]
                [--refresh]
```

### Optional Parameters

The following parameters are optional, but depending on the context, one or more might become required for the command to execute successfully.

--all

List all subscriptions from all clouds, including subscriptions that are not 'Enabled'.

| Property | Value |
| --- | --- |
| Default value: | False |

--refresh

Retrieve up-to-date subscriptions from server.

| Property | Value |
| --- | --- |
| Default value: | False |

 Global Parameters 

--debug

Increase logging verbosity to show all debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

--help -h

Show this help message and exit.

--only-show-errors

Only show errors, suppressing warnings.

| Property | Value |
| --- | --- |
| Default value: | False |

--output -o

Output format.

| Property | Value |
| --- | --- |
| Default value: | json |
| Accepted values: | json, jsonc, none, table, tsv, yaml, yamlc |

--query

JMESPath query string. See http://jmespath.org/ for more information and examples.

--verbose

Increase logging verbosity. Use --debug for full debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

## az account list-locations

List supported regions for the current subscription.

```azurecli
az account list-locations [--acquire-policy-token]
                          [--change-reference]
                          [--include-extended-locations {0, 1, f, false, n, no, t, true, y, yes}]
```

### Optional Parameters

The following parameters are optional, but depending on the context, one or more might become required for the command to execute successfully.

--acquire-policy-token

Acquiring an Azure Policy token automatically for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--change-reference

The related change reference ID for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--include-extended-locations

Whether to include extended locations.

| Property | Value |
| --- | --- |
| Accepted values: | 0, 1, f, false, n, no, t, true, y, yes |

 Global Parameters 

--debug

Increase logging verbosity to show all debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

--help -h

Show this help message and exit.

--only-show-errors

Only show errors, suppressing warnings.

| Property | Value |
| --- | --- |
| Default value: | False |

--output -o

Output format.

| Property | Value |
| --- | --- |
| Default value: | json |
| Accepted values: | json, jsonc, none, table, tsv, yaml, yamlc |

--query

JMESPath query string. See http://jmespath.org/ for more information and examples.

--verbose

Increase logging verbosity. Use --debug for full debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

## az account set

Set a subscription to be the current active subscription.

```azurecli
az account set --name --subscription
               [--acquire-policy-token]
               [--change-reference]
```

### Required Parameters

--name --subscription -n -s

Name or ID of subscription.

### Optional Parameters

The following parameters are optional, but depending on the context, one or more might become required for the command to execute successfully.

--acquire-policy-token

Acquiring an Azure Policy token automatically for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

--change-reference

The related change reference ID for this resource operation.

| Property | Value |
| --- | --- |
| Parameter group: | Global Policy Arguments |

 Global Parameters 

--debug

Increase logging verbosity to show all debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

--help -h

Show this help message and exit.

--only-show-errors

Only show errors, suppressing warnings.

| Property | Value |
| --- | --- |
| Default value: | False |

--output -o

Output format.

| Property | Value |
| --- | --- |
| Default value: | json |
| Accepted values: | json, jsonc, none, table, tsv, yaml, yamlc |

--query

JMESPath query string. See http://jmespath.org/ for more information and examples.

--verbose

Increase logging verbosity. Use --debug for full debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

## az account show

Get the details of a subscription.

If the subscription isn't specified, shows the details of the default subscription.

```azurecli
az account show [--name --subscription]
```

### Optional Parameters

The following parameters are optional, but depending on the context, one or more might become required for the command to execute successfully.

--name --subscription -n -s

Name or ID of subscription.

 Global Parameters 

--debug

Increase logging verbosity to show all debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

--help -h

Show this help message and exit.

--only-show-errors

Only show errors, suppressing warnings.

| Property | Value |
| --- | --- |
| Default value: | False |

--output -o

Output format.

| Property | Value |
| --- | --- |
| Default value: | json |
| Accepted values: | json, jsonc, none, table, tsv, yaml, yamlc |

--query

JMESPath query string. See http://jmespath.org/ for more information and examples.

--verbose

Increase logging verbosity. Use --debug for full debug logs.

| Property | Value |
| --- | --- |
| Default value: | False |

---

## Other Supported Versions

- [azure-cli-lts-2017-03-09-profile](https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-lts-2017-03-09-profile&accept=text/markdown)
- [azure-cli-lts-2018-03-01-hybrid](https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-lts-2018-03-01-hybrid&accept=text/markdown)
- [azure-cli-lts-2019-03-01-hybrid](https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-lts-2019-03-01-hybrid&accept=text/markdown)
- [azure-cli-lts-2020-09-01-hybrid](https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-lts-2020-09-01-hybrid&accept=text/markdown)
- [azure-cli-lts](https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-lts&accept=text/markdown)
