---
layout: Reference
monikers:
- azure-python
defaultMoniker: azure-python
versioningType: Ranged
title: azure.identity.EnvironmentCredential class | Microsoft Learn
canonicalUrl: https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.environmentcredential?view=azure-python
config_moniker_range: azure-python
uid: azure.identity.EnvironmentCredential
module: azure.identity
uhfHeaderId: Azure
feedback_system: OpenSource
feedback_product_url: https://github.com/Azure/azure-sdk-for-python/issues
breadcrumb_path: /python/azure/bread/toc.json
apiPlatform: python
author: lmazuel
ms.manager: smortaz
ms.author: lmazuel
ms.devlang: python
ms.date: 2018-05-23T00:00:00.0000000Z
ms.topic: generated-reference
locale: en-us
document_id: 5d5ffd13-22fe-0b7f-d411-8d620e71119d
document_version_independent_id: 6ae7c6be-bbaf-a334-d296-be3834193a9d
updated_at: 2026-08-12T11:12:00.0000000Z
original_content_git_url: https://github.com/MicrosoftDocs/azure-docs-sdk-python/blob/live/docs-ref-autogen/azure-identity/azure.identity.EnvironmentCredential.yml
gitcommit: https://github.com/MicrosoftDocs/azure-docs-sdk-python/blob/e33b5d74db4cde92e8647c3396ed57d69bfb7921/docs-ref-autogen/azure-identity/azure.identity.EnvironmentCredential.yml
git_commit_id: e33b5d74db4cde92e8647c3396ed57d69bfb7921
default_moniker: azure-python
site_name: Docs
depot_name: MSDN.python-sdk
in_right_rail: h2h3
page_type: python
page_kind: class
description: "A credential configured by environment variables. This credential is capable of authenticating as a service principal using a client secret or a certificate. Configuration is attempted in this order, using these environment variables: Service principal with secret:  AZURE_TENANT_ID: ID of the service principal's tenant. Also called its 'directory' ID.  AZURE_CLIENT_ID: the service principal's client ID  AZURE_CLIENT_SECRET: one of the service principal's client secrets  AZURE_AUTHORITY_HOST: authority of a Microsoft Entra endpoint, for example "login.microsoftonline.com", the authority for Azure Public Cloud, which is the default when no value is given.   Service principal with certificate:  AZURE_TENANT_ID: ID of the service principal's tenant. Also called its 'directory' ID.  AZURE_CLIENT_ID: the service principal's client ID  AZURE_CLIENT_CERTIFICATE_PATH: path to a PEM or PKCS12 certificate file including the private key.  AZURE_CLIENT_CERTIFICATE_PASSWORD: (optional) password of the certificate file, if any.  AZURE_CLIENT_SEND_CERTIFICATE_CHAIN: (optional) If True, the credential will send the public certificate chain in the x5c header of each token request's JWT. This is required for Subject Name/Issuer (SNI) authentication. Defaults to False.  AZURE_AUTHORITY_HOST: authority of a Microsoft Entra endpoint, for example "login.microsoftonline.com", the authority for Azure Public Cloud, which is the default when no value is given.   "
toc_rel: ../_splitted/azure.identity/toc.json
feedback_help_link_type: ''
feedback_help_link_url: ''
search.mshattr.devlang: python
asset_id: api/azure-identity/azure.identity.environmentcredential
moniker_range_name: db4cc4146095cc059ef03e10f2246414
monikers:
- azure-python
item_type: Content
source_path: docs-ref-autogen/azure-identity/azure.identity.EnvironmentCredential.yml
cmProducts:
- https://authoring-docs-microsoft.poolparty.biz/devrel/68ec7f3a-2bc6-459f-b959-19beb729907d
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/57eae307-c3a1-4cac-b645-1a899934bac8
spProducts:
- https://authoring-docs-microsoft.poolparty.biz/devrel/90370425-aca4-4a39-9533-d52e5e002a5d
- https://microsoft-devrel.poolparty.biz/DevRelOfferingOntology/ee561821-1ac7-45a8-9409-6ba5eb7a5b97
platformId: 8e69be5d-61e4-d679-4f9e-fb46a2ae751a
---

# EnvironmentCredential Class

A credential configured by environment variables.

This credential is capable of authenticating as a service principal using a client secret or a certificate. Configuration is attempted in this order, using these environment variables:

Service principal with secret:

- **AZURE\_TENANT\_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
- **AZURE\_CLIENT\_ID**: the service principal's client ID
- **AZURE\_CLIENT\_SECRET**: one of the service principal's client secrets
- **AZURE\_AUTHORITY\_HOST**: authority of a Microsoft Entra endpoint, for example "login.microsoftonline.com", the authority for Azure Public Cloud, which is the default when no value is given.

Service principal with certificate:

- **AZURE\_TENANT\_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
- **AZURE\_CLIENT\_ID**: the service principal's client ID
- **AZURE\_CLIENT\_CERTIFICATE\_PATH**: path to a PEM or PKCS12 certificate file including the private key.
- **AZURE\_CLIENT\_CERTIFICATE\_PASSWORD**: (optional) password of the certificate file, if any.
- **AZURE\_CLIENT\_SEND\_CERTIFICATE\_CHAIN**: (optional) If True, the credential will send the public certificate chain in the x5c header of each token request's JWT. This is required for Subject Name/Issuer (SNI) authentication. Defaults to False.
- **AZURE\_AUTHORITY\_HOST**: authority of a Microsoft Entra endpoint, for example "login.microsoftonline.com", the authority for Azure Public Cloud, which is the default when no value is given.

## Constructor

```python
EnvironmentCredential(**kwargs: Any)
```

#### Examples

Create an EnvironmentCredential.

```python

   from azure.identity import EnvironmentCredential

   credential = EnvironmentCredential()

```

## Methods

| close | Close the credential's transport session. |
| --- | --- |
| get_token | Request an access token for *scopes*.

This method is called automatically by Azure SDK clients. |
| get_token_info | Request an access token for *scopes*.

This is an alternative to *get\_token* to enable certain scenarios that require additional properties on the token. This method is called automatically by Azure SDK clients. |

### close

Close the credential's transport session.

```python
close() -> None
```

### get\_token

Request an access token for *scopes*.

This method is called automatically by Azure SDK clients.

```python
get_token(*scopes: str, claims: str | None = None, tenant_id: str | None = None, **kwargs: Any) -> AccessToken
```

#### Parameters

| Name | Description |
| --- | --- |
| scopes

Required | [str](https://docs.python.org/3/library/stdtypes.html#str)

desired scopes for the access token. This method requires at least one scope. For more information about scopes, see [https://learn.microsoft.com/entra/identity-platform/scopes-oidc](/en-us/entra/identity-platform/scopes-oidc). |

#### Keyword-Only Parameters

| Name | Description |
| --- | --- |
| claims | [str](https://docs.python.org/3/library/stdtypes.html#str)

additional claims required in the token, such as those returned in a resource provider's claims challenge following an authorization failure.

Default value: None |
| tenant\_id | [str](https://docs.python.org/3/library/stdtypes.html#str)

optional tenant to include in the token request.

Default value: None |

#### Returns

| Type | Description |
| --- | --- |
| [AccessToken](../azure-core/azure.core.credentials.accesstoken) | An access token with the desired scopes. |

#### Exceptions

| Type | Description |
| --- | --- |
| [CredentialUnavailableError](azure.identity.credentialunavailableerror) | environment variable configuration is incomplete |

### get\_token\_info

Request an access token for *scopes*.

This is an alternative to *get\_token* to enable certain scenarios that require additional properties on the token. This method is called automatically by Azure SDK clients.

```python
get_token_info(*scopes: str, options: TokenRequestOptions | None = None) -> AccessTokenInfo
```

#### Parameters

| Name | Description |
| --- | --- |
| scopes

Required | [str](https://docs.python.org/3/library/stdtypes.html#str)

desired scope for the access token. This method requires at least one scope. For more information about scopes, see [https://learn.microsoft.com/entra/identity-platform/scopes-oidc](/en-us/entra/identity-platform/scopes-oidc). |

#### Keyword-Only Parameters

| Name | Description |
| --- | --- |
| options | [TokenRequestOptions](../azure-core/azure.core.credentials.tokenrequestoptions)

A dictionary of options for the token request. Unknown options will be ignored. Optional.

Default value: None |

#### Returns

| Type | Description |
| --- | --- |
| [AccessTokenInfo](../azure-core/azure.core.credentials.accesstokeninfo) | An AccessTokenInfo instance containing information about the token. |

#### Exceptions

| Type | Description |
| --- | --- |
| [CredentialUnavailableError](azure.identity.credentialunavailableerror) | environment variable configuration is incomplete. |

---

## Other Supported Versions

- [azure-python-preview](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.environmentcredential?view=azure-python-preview&accept=text/markdown)
