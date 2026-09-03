> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use Kimi K3 in Codex

> Connect Codex directly to Kimi K3 through the Kimi Responses API: set an API key, edit `~/.codex/config.toml`, and verify the connection in both Codex Desktop and the CLI.

Kimi Open Platform natively supports the [Responses API](/docs/api/responses) used by Codex, so Codex can use the `kimi-k3` model directly — no protocol conversion or local proxy is required.

<Note>
  Codex CLI supports text and image input, but does not provide a native video input channel — you cannot submit a video file directly as multimodal input to the model. This is a limitation of Codex CLI's input layer, not of the Kimi K3 model — the Kimi K3 API natively supports video input. Call `kimi-k3` directly as described in [Vision Input](/docs/guide/use-kimi-vision-model) for full video understanding, with no manual frame extraction required.
</Note>

## Prerequisites

Before you start, complete the following preparations. Follow the corresponding official instructions for installation and account-related operations; this guide does not repeat those procedures.

<CardGroup cols={2}>
  <Card title="Install Codex CLI" icon="terminal" href="https://developers.openai.com/codex/cli">
    Follow the official Codex documentation and start Codex CLI at least once. To use the Codex desktop app, [download it from the official site](https://chatgpt.com/codex) or run `codex app` after installing the CLI.
  </Card>

  <Card title="Create an API key" icon="key" href="https://platform.kimi.ai/console/api-keys">
    Create and save an API key in Kimi Open Platform.
  </Card>
</CardGroup>

## Step 1: Configure the API key

Codex reads the API key from an environment variable. Do not write the key into `config.toml`. To keep the key out of your shell history, enter it as follows:

<Tabs>
  <Tab title="macOS / Linux">
    ```bash theme={null}
    echo "Paste your Kimi API key and press Enter (input is hidden):"
    read -s KIMI_API_KEY
    export KIMI_API_KEY
    ```

    This only applies to the current terminal session. To persist it, add the `export` command to `~/.zshrc` (or `~/.bashrc` if you use bash on Linux). The file stores the key in plain text — set permissions accordingly.
  </Tab>

  <Tab title="Windows (PowerShell)">
    ```powershell theme={null}
    $env:KIMI_API_KEY="YOUR_KIMI_API_KEY"
    ```

    To persist it across sessions, add `KIMI_API_KEY` under **Settings > System > About > Advanced system settings > Environment Variables**.
  </Tab>
</Tabs>

## Step 2: Add Kimi as a model provider

Open `~/.codex/config.toml` (on Windows: `%USERPROFILE%\.codex\config.toml`) and add the following configuration. If `model` or `model_provider` already exist, replace their values:

```toml theme={null}
model = "kimi-k3"
model_provider = "kimi"
model_context_window = 1048576

[model_providers.kimi]
name = "Kimi"
base_url = "https://api.moonshot.ai/v1"
env_key = "KIMI_API_KEY"
wire_api = "responses"
```

| Setting                          | Type      | Purpose                                                                                                                           |
| -------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `wire_api = "responses"`         | `string`  | Connects to Kimi through the native Responses API — the key setting for the direct connection                                     |
| `env_key = "KIMI_API_KEY"`       | `string`  | Name of the environment variable Codex reads the API key from                                                                     |
| `model_context_window = 1048576` | `integer` | Matches the 1M context window of `kimi-k3`; without it, Codex falls back to default model metadata, which can degrade performance |

## Use Codex Desktop

After completing the API key and provider configuration above, quit and restart Desktop so it reloads `~/.codex/config.toml`.

After Desktop starts, open the model picker and select `kimi-k3`. The interface may show **Custom**, but requests still use the `kimi-k3` you configured.

<img src="https://mintcdn.com/moonshotai/vwk1GToU6RD4oxdy/assets/pics/codex-kimi/desktop-custom-provider.png?fit=max&auto=format&n=vwk1GToU6RD4oxdy&q=85&s=480b290d9937f00555e18c267dad6991" alt="The Desktop composer shows the &#x22;Custom&#x22; model label" width="1544" height="736" data-path="assets/pics/codex-kimi/desktop-custom-provider.png" />

Send a simple request like `hi` — a normal reply means the basic connection works:

<img src="https://mintcdn.com/moonshotai/vwk1GToU6RD4oxdy/assets/pics/codex-kimi/desktop-hello-verify.png?fit=max&auto=format&n=vwk1GToU6RD4oxdy&q=85&s=3cff1702002ee35765243561141feff1" alt="Kimi replies to a simple greeting in Desktop" width="2000" height="1063" data-path="assets/pics/codex-kimi/desktop-hello-verify.png" />

Next, send a task that exercises Codex's agent capabilities:

```text theme={null}
Inspect this repository and summarize its structure.
```

If Desktop continues generating a final answer after the tool results come back, model calls and tool calling are working properly.

## Use Codex CLI

Codex CLI shares the same user-level configuration as Desktop, so the configuration above applies to it as well. Enter your project directory and start Codex (if Codex CLI is already running, exit the current session first so it reloads the configuration):

```bash theme={null}
cd /path/to/your/project
codex
```

After startup, confirm that Codex CLI shows `kimi-k3` as the current model:

<img src="https://mintcdn.com/moonshotai/GuRAyEnWJ2mAZCpu/assets/pics/codex-kimi/verify-codex-cli.png?fit=max&auto=format&n=GuRAyEnWJ2mAZCpu&q=85&s=9fc744c9a811045db4e8f4bc28d47284" alt="Confirm kimi-k3 as the current model in Codex CLI" width="1140" height="291" data-path="assets/pics/codex-kimi/verify-codex-cli.png" />

Send a simple request (for example `hello`). A normal reply confirms that Codex is connected through the Kimi Responses API.

Under the hood, Codex sends requests to `POST https://api.moonshot.ai/v1/responses`. For request and response schema details, see the [Responses API reference](/docs/api/responses).

## Troubleshooting

<AccordionGroup>
  <Accordion title="401 Unauthorized">
    The API key is invalid, or the key and the base\_url belong to different platforms — API keys created on [platform.kimi.ai](https://platform.kimi.ai) only work with `https://api.moonshot.ai/v1`. Also confirm that `KIMI_API_KEY` is available in the environment used to start Codex or Desktop. For CLI, check it in the terminal where you start Codex with `test -n "$KIMI_API_KEY" && echo set || echo missing`.
  </Accordion>

  <Accordion title="400 web_search.search_context_size is not supported">
    The request includes the `search_context_size` parameter, which is not supported yet — remove it. Codex does not send this parameter by default, and the built-in web\_search tool works out of the box.
  </Accordion>

  <Accordion title="404 on /v1/responses">
    base\_url is wrong — make sure it is exactly `https://api.moonshot.ai/v1` (with the /v1 suffix). If you previously connected through CC Switch or another local router, also confirm base\_url no longer points at a local address such as `http://127.0.0.1:...`.
  </Accordion>

  <Accordion title="429 Rate Limit">
    You have hit a rate or concurrency limit. See [Rate limits](/docs/pricing/limits) for your tier's quotas.
  </Accordion>

  <Accordion title="Warning Model metadata for kimi-k3 not found">
    kimi-k3 is not in Codex's built-in model catalog. This warning is expected and does not affect usage — the `model_context_window = 1048576` from Step 2 already ensures the context window is treated as 1M.
  </Accordion>

  <Accordion title="Configuration changes do not take effect">
    Codex only reads config.toml at startup — exit and restart it. Also confirm you edited `~/.codex/config.toml` itself and that no `-c` flags or profiles are overriding it. If you previously connected through CC Switch, also turn off **Codex** under its **Settings > Routing** — otherwise it keeps rewriting config.toml and overwrites the new configuration.
  </Accordion>

  <Accordion title="Other HTTP errors">
    See [Error codes](/docs/api/errors) for the meaning of each status code.
  </Accordion>
</AccordionGroup>
