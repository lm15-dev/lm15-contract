> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/security-and-account-management/account-api-keys.md).

# Account and API Keys

Manage Parasail organizations, account access, and read-only API keys.

## Organizations

Your Parasail user account belongs to an organization. The active organization receives charges for usage from API keys, Dedicated deployments, and Batch jobs.

If you belong to multiple organizations, switch to the correct organization before creating keys or launching workloads.

## Members

Organization owners can invite members from the Parasail dashboard. Members should create their own API keys instead of sharing keys.

## API keys

Create API keys from the Parasail dashboard. Store keys in environment variables such as `PARASAIL_API_KEY` and avoid pasting secrets directly into source code.

```bash
export PARASAIL_API_KEY="<your-api-key>"
```

Use the key with the OpenAI SDK by setting the Parasail base URL:

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)
```

## Read-only API keys

Read-only API keys give safe, scoped access for inspection workflows. A read-only key can send `GET` requests only to the management API endpoints in the allowed-endpoints table. Parasail rejects every other endpoint and every non-`GET` method.

Use read-only keys for dashboards, audits, billing review, deployment-status monitors, and integrations that should never run inference, create workloads, or change account state.

### Create a read-only key

1. Open the **API Keys** page in the Parasail dashboard.
2. Click **Create API Key**.
3. Under **Access Level**, select **Read-only**.
4. Give the key a name, then click **Create**.
5. Copy the key value immediately; Parasail shows it only once.

Read-only keys appear in the API Keys list with a **Read-only** badge.

### Allowed read-only endpoints

Read-only keys can use only the following endpoints with `GET`:

| Method | Endpoint                                    | Description                                        |
| ------ | ------------------------------------------- | -------------------------------------------------- |
| `GET`  | `/api/v1/openrouter/models`                 | List models available through OpenRouter.          |
| `GET`  | `/api/v1/dedicated/devices`                 | List supported GPU and hardware types.             |
| `GET`  | `/api/v1/dedicated/support`                 | Check whether a model supports dedicated hardware. |
| `GET`  | `/api/v1/dedicated/performance`             | Get model and hardware performance estimates.      |
| `GET`  | `/api/v1/dedicated/deployments`             | List your dedicated deployments.                   |
| `GET`  | `/api/v1/dedicated/deployments/{id}`        | Fetch one dedicated deployment.                    |
| `GET`  | `/api/v1/dedicated/deployments/{id}/models` | List models on one dedicated deployment.           |
| `GET`  | `/v1/billing/invoices`                      | List invoices.                                     |
| `GET`  | `/v1/billing/invoices/current`              | Fetch the current invoice.                         |
| `GET`  | `/v1/billing/invoices/{invoiceId}`          | Fetch one invoice.                                 |

### What read-only keys can't do

Read-only keys can't:

* Run inference, including calls to `/openai/*` or OpenAI-compatible inference endpoints such as `/v1/chat/completions`.
* Create, update, pause, resume, scale, or delete deployments or Batch jobs.
* Rotate keys, change account settings, invite members, or mutate billing settings.
* Use `POST`, `PATCH`, `PUT`, or `DELETE` anywhere.
* Access any management endpoint that isn't listed in the allowed-endpoints table.

### Examples

A read-only key can list dedicated deployments:

```http
GET /api/v1/dedicated/deployments HTTP/1.1
Host: api.parasail.io
Authorization: Bearer <read-only-api-key>
```

The same key can't create a deployment. Parasail returns `403 Forbidden` for a mutation:

```http
POST /api/v1/dedicated/deployments HTTP/1.1
Host: api.parasail.io
Authorization: Bearer <read-only-api-key>
Content-Type: application/json
```

Example response:

```json
{
  "type": "about:blank",
  "title": "Forbidden",
  "status": 403,
  "detail": "This API key is read-only",
  "instance": "/api/v1/dedicated/deployments"
}
```

A read-only key also can't run inference. A request such as `POST /v1/chat/completions` returns `403 Forbidden`.

## Next steps

* [Authentication](/parasail-docs/api-reference/authentication.md)
* [Security overview](/parasail-docs/security-and-account-management/overview.md)
* [Pricing](/parasail-docs/billing/pricing.md)
