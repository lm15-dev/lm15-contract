---
meta:
  title: Authentication
  description: Create and manage API keys for authenticating requests to Meta Model API.
  keywords: authentication, API keys, key management, MODEL_API_KEY, Bearer token
cms:
  alias: /model-api/docs/authentication
  target: aidmc
---

# Authentication

Every request to Meta Model API needs an API key. Add your key and start building.

## Get an API key {#get-an-api-key}

Create and manage keys in the [**Model API dashboard**](/):

1. Log in and open the **API keys** tab.
2. Click **Create API key**, give it a descriptive name, and click **Create**.
3. Copy the key right away. You only see it once.

API keys look like this:

```plaintext title="API key format"
LLM|607358788850350|nx9.....LJY
```

## Use an API key {#use-an-api-key}

Pass the key as a Bearer token in the `Authorization` header:

```shell title="curl"
curl https://api.meta.ai/v1/chat/completions \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "muse-spark-1.1",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

Keep the key out of your code. Store it in an environment variable:

```shell
export MODEL_API_KEY="LLM|607358788850350|nx9.....LJY"
```

See [Get started](/docs/quickstart#first-call) for a full walkthrough.

The official [SDKs](/docs/sdks) read `MODEL_API_KEY` automatically when you don't pass a key to the client.

## Revoke an API key {#revoke-an-api-key}

Remove access in the **Model API dashboard**: click **Delete** next to the key you want to revoke. Deleting one key leaves other team keys untouched.

## API key safety {#api-key-safety}

A leaked key can burn your team's rate limits, access uploaded files, and send requests on your behalf. Lock it down with these practices:

1. **Use unique keys per application**: create a separate key for each app or developer so you can revoke one without breaking the rest.
2. **Keep keys out of client code**: mobile and browser code is visible to users. Proxy requests through a server you control.
3. **Never commit keys to version control**: load them from environment variables or a secrets manager, and add credential files to `.gitignore`.
4. **Use environment variables or a key manager**: centralize secrets so rotation stays simple and keys stay out of source files.
5. **Monitor for anomalies**: watch usage for unexpected spikes that suggest a leak, then revoke and rotate immediately.

> [!NOTE] Shared team rate limits
> Keys on the same team share rate limits. See [Pricing and rate limits](/docs/pricing-rate-limits) for details.