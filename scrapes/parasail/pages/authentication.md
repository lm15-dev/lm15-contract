> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/api-reference/authentication.md).

# Authentication

API key creation, base URLs, and authentication for the Parasail API.

All Parasail API requests use bearer token authentication. The API is fully OpenAI-compatible.

## Base URLs

| Product/API      | Base URL                     | Notes                          |
| ---------------- | ---------------------------- | ------------------------------ |
| Chat Completions | `https://api.parasail.io/v1` | OpenAI-compatible              |
| Responses API    | `https://api.parasail.io/v1` | OpenAI-compatible              |
| Embeddings       | `https://api.parasail.io/v1` | OpenAI-compatible              |
| Batch API        | `https://api.parasail.io/v1` | `/v1/batches`                  |
| Files API        | `https://api.parasail.io/v1` | `/v1/files`, for batch uploads |

`https://api.parasail.io/v1` is the single gateway for all Parasail inference and batch APIs. Don't use legacy Parasail API hosts in new integrations.

## Getting an API key

1. Go to <https://www.saas.parasail.io/keys>.
2. Click **Create API Key**.
3. Copy the key immediately—it's displayed only once.

## Using your API key

Pass your API key in the `Authorization` header:

```
Authorization: Bearer <PARASAIL_API_KEY>
```

### With the OpenAI SDK in Python

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)
```

### With cURL

```bash
curl https://api.parasail.io/v1/models \
  -H "Authorization: Bearer $PARASAIL_API_KEY"
```

### Environment variable

Store your key in an environment variable rather than hardcoding it:

```bash
export PARASAIL_API_KEY="your-api-key-here"
```

## API key types

* **Standard API keys**—full read/write access to inference and management endpoints.
* **Read-only API keys**—GET-only access to listed management endpoints for monitoring, billing, and deployment inspection. They can't run inference or mutate account or deployment state. See [Account and API keys](/parasail-docs/security-and-account-management/account-api-keys.md).

## Organization-based billing

Your API key belongs to an organization. The organization receives charges for all usage. See [Account and API keys](/parasail-docs/security-and-account-management/account-api-keys.md) for details on organizations and switching between them.
