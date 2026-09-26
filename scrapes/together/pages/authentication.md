> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Authentication

> Create, manage, and authenticate with project-scoped API keys.

Together AI uses API keys to authenticate requests. Keys are scoped to [projects](/docs/projects), meaning a key only has access to the resources within its project.

## Create an API key

Create independent API keys for separate use cases, systems, or workloads. For example, one for production, one for development, one for CI/CD, and one for inference.

<Steps>
  <Step title="Open the project">
    Navigate to the project you want to create a key for.
  </Step>

  <Step title="Open API key settings">
    Go to the project's [API keys settings](https://api.together.ai/settings/projects/~current/api-keys).
  </Step>

  <Step title="Create the key">
    Select **Create API Key** and enter a name. To make the key expire automatically, select **Set an expiration date** and choose a preset or custom date. Then select **Create**.
  </Step>

  <Step title="Copy the key">
    Copy the key immediately. It won't be shown again.
  </Step>
</Steps>

<Warning>
  New API keys are displayed only once at creation. Save them in a secure location, such as a secrets manager, immediately. If you lose a key, you'll need to create a new one.
</Warning>

## Best practices

* **Name your keys descriptively** (for example, `prod-inference`, `ci-pipeline`, `dev-local`) so you can identify and rotate them.
* **Set expiration dates** for keys used in temporary or testing contexts. Select **Set an expiration date** when creating a key, or **Set expiration** in the three-dot menu next to an existing key. To keep a key that's scheduled to expire, select **Cancel expiration** from the same menu.
* **Rotate keys regularly** and revoke any that are no longer in use.
* **Never commit keys to source control.** Use environment variables or a secrets manager.
* **Treat keys as secrets.** Anyone holding a key has full access to its project's resources and can spend your credit balance, which auto-recharge tops back up. If you suspect a key has leaked, revoke it immediately and create a new one.

## Set as an environment variable

To use the Together Python or TypeScript SDKs, set your key as an environment variable in your shell:

<CodeGroup>
  ```bash macOS / Linux theme={null}
  export TOGETHER_API_KEY="your_api_key"
  ```

  ```powershell Windows (PowerShell) theme={null}
  $env:TOGETHER_API_KEY="your_api_key"
  ```
</CodeGroup>

Or add it to a `.env` file in your project directory:

```dotenv .env theme={null}
TOGETHER_API_KEY=your_api_key
```

## Authenticate a request

Include your API key in the `Authorization` header of every API request:

```bash theme={null}
curl https://api.together.ai/v1/chat/completions \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Project key scoping

API keys are scoped to projects:

* A key created in project A can only access resources in project A.
* Keys persist even if the collaborator who created them is removed from the project.
* Both project admins and member-role collaborators can create and revoke keys.

This means you can safely share a project API key with a CI/CD pipeline or external collaborator without giving them access to resources in other projects.

<Note>
  Keys created before multi-project support was enabled are scoped to your organization's default project.
</Note>

## Playground

The [Together AI playground](https://api.together.ai/playground/) recognizes all API keys associated with your account. When you use the playground, it shows available models across all your keys and projects.

## Cost analytics and usage

Use API key IDs to segment usage and cost by key and workload. The `api_key_id` field is supported for inference and code interpreter requests, so you can track which keys are driving spend in your [project's cost analytics](https://api.together.ai/settings/projects/~current/cost-analytics).

## Limitations

**No per-key usage limits:** You can't cap spend or rate-limit individual API keys. Usage limits apply at the organization level.

## Vercel integration

When you connect a Vercel project from [Integrations settings](https://api.together.ai/settings/integrations), each linked Vercel project gets its own dedicated API key. Together creates the key in your organization's default project and sets it as the `TOGETHER_API_KEY` environment variable in the Vercel project.

Manage or revoke these keys from the default project's [API keys settings](https://api.together.ai/settings/projects/~current/api-keys), like any other key. Disconnecting a Vercel project removes the environment variable from Vercel but doesn't revoke the key.

<Note>
  This is the Together console Vercel integration. For the npm AI SDK provider, see [Vercel AI SDK](/docs/using-together-with-vercels-ai-sdk).
</Note>

## Legacy API keys

Your organization may have a legacy API key scoped to its default project. It appears in that project's [API keys settings](https://api.together.ai/settings/projects/~current/api-keys) with a **Deprecated** badge.

Legacy keys are deprecated, and you should **avoid using them in production.** These keys can't be scoped to a specific project or workload, and can't be revoked (only regenerated if compromised). Use [project-scoped API keys](#create-an-api-key) instead.

### Regenerate a legacy key

If a legacy key is compromised, any project admin or editor can rotate it. In the project's [API keys settings](https://api.together.ai/settings/projects/~current/api-keys), open the three-dot menu on the key's row, select **Regenerate legacy key**, and confirm.

<Warning>
  Regenerating a legacy key invalidates the current key immediately, and the new key is shown only once. Copy it right away and update every application that used the old key.
</Warning>

## Related resources

<CardGroup cols={2}>
  <Card title="Projects" icon="folder" href="/docs/projects">
    Understand how API keys are scoped to projects.
  </Card>

  <Card title="Roles and permissions" icon="shield" href="/docs/roles-permissions">
    See who can create and manage API keys.
  </Card>
</CardGroup>
