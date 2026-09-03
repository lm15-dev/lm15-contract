> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use Kimi in Claude Code

> Learn how to integrate the Kimi API into Claude Code and verify your configuration.

> This guide shows how to integrate Kimi's Anthropic-compatible endpoint (the [Messages API](/docs/api/messages)) into [Claude Code](https://claude.com/product/claude-code). Claude Code's interface and configuration options may change across versions; refer to your installed version.

## Install Claude Code

Skip this step if Claude Code is already installed. Use the native installer (recommended by Anthropic):

macOS and Linux:

```shell theme={null}
curl -fsSL https://claude.ai/install.sh | bash
```

Windows (PowerShell):

```powershell theme={null}
irm https://claude.ai/install.ps1 | iex
```

You can also install it as a global npm package (requires Node.js 22 or later):

```shell theme={null}
npm install -g @anthropic-ai/claude-code
```

<Accordion title="Install Node.js and initialize">
  macOS and Linux:

  ```shell theme={null}
  # Install Node.js
  curl -fsSL https://fnm.vercel.app/install | bash

  # Open a new terminal so fnm takes effect
  fnm install 24.3.0
  fnm default 24.3.0
  fnm use 24.3.0
  ```

  Windows (PowerShell):

  ```powershell theme={null}
  # Right-click the Windows button, click "Terminal", then run:
  winget install OpenJS.NodeJS
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

  # Close the terminal window and open a new one
  ```

  After installing Node.js, run the initialization once:

  ```shell theme={null}
  node --eval "
      const fs = require('fs');
      const path = require('path');
      const os = require('os');
      const homeDir = os.homedir();
      const filePath = path.join(homeDir, '.claude.json');
      if (fs.existsSync(filePath)) {
          const content = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
          fs.writeFileSync(filePath, JSON.stringify({ ...content, hasCompletedOnboarding: true }, null, 2), 'utf-8');
      } else {
          fs.writeFileSync(filePath, JSON.stringify({ hasCompletedOnboarding: true }, null, 2), 'utf-8');
      }"
  ```
</Accordion>

<Accordion title="Not a first-time install? Clean up legacy config and environment variables">
  If you previously modified `~/.claude/settings.json` with third-party tools or by hand, stale values left in its `env` field **override** environment variables exported in your terminal, so the new configuration may not take effect or model requests may be silently rewritten. Run this cleanup script first:

  ```shell theme={null}
  node --eval "
      const fs = require('fs');
      const path = require('path');
      const os = require('os');
      const settingsPath = path.join(os.homedir(), '.claude', 'settings.json');
      if (fs.existsSync(settingsPath)) {
          const content = JSON.parse(fs.readFileSync(settingsPath, 'utf-8'));
          if (content && typeof content === 'object' && content.env && typeof content.env === 'object') {
              for (const key of [
                  'ANTHROPIC_BASE_URL',
                  'ANTHROPIC_API_KEY',
                  'ANTHROPIC_AUTH_TOKEN',
                  'ANTHROPIC_MODEL',
                  'ANTHROPIC_SMALL_FAST_MODEL',
                  'CLAUDE_CODE_SUBAGENT_MODEL',
                  'ANTHROPIC_DEFAULT_OPUS_MODEL',
                  'ANTHROPIC_DEFAULT_OPUS_MODEL_NAME',
                  'ANTHROPIC_DEFAULT_SONNET_MODEL',
                  'ANTHROPIC_DEFAULT_SONNET_MODEL_NAME',
                  'ANTHROPIC_DEFAULT_HAIKU_MODEL',
                  'ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME',
                  'ANTHROPIC_DEFAULT_FABLE_MODEL',
                  'ANTHROPIC_DEFAULT_FABLE_MODEL_NAME',
                  'ENABLE_TOOL_SEARCH',
                  'CLAUDE_CODE_AUTO_COMPACT_WINDOW',
                  'CLAUDE_CODE_EFFORT_LEVEL',
              ]) {
                  delete content.env[key];
              }
              fs.writeFileSync(settingsPath, JSON.stringify(content, null, 2), 'utf-8');
          }
      }"
  ```

  The script only removes endpoint, credential, and model-related variables from `env`; it does not touch other settings in `settings.json` (permissions, theme, and so on).

  Also check shell config files such as `~/.zshrc` and `~/.bashrc` for stale `ANTHROPIC_*` exports (Windows users: check user environment variables) and delete them, otherwise they will interfere with the new configuration.
</Accordion>

## Get a Kimi API Key

Create an API key on the [Kimi Platform](https://platform.kimi.ai/console/api-keys), and use it to replace `YOUR_MOONSHOT_API_KEY` below.

## Configure Environment Variables

Write the following variables into the `env` field of `~/.claude/settings.json`, then restart Claude Code for them to take effect. This example sets the HAIKU tier to `kimi-k2.7-code` and all other tiers to `kimi-k3[1m]`.

```json theme={null}
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.moonshot.ai/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "YOUR_MOONSHOT_API_KEY",
    "ANTHROPIC_MODEL": "kimi-k3[1m]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "kimi-k3[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "kimi-k3[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "kimi-k2.7-code",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "kimi-k3[1m]",
    "CLAUDE_CODE_SUBAGENT_MODEL": "kimi-k3[1m]",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
    "CLAUDE_CODE_EFFORT_LEVEL": "max"
  }
}
```

Note: the `env` block in `settings.json` **overrides** same-named variables exported in your terminal. This file contains your API key in plain text; do not commit it to git.

### Configuration Reference

Claude Code uses different model tiers for different scenarios (main conversation, background summarization, sub-agents, and so on). Configuring only some of the variables makes the corresponding scenarios fail silently:

| Variable                                                                                                                              | Purpose                                      | If not configured                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------- |
| `ANTHROPIC_BASE_URL`                                                                                                                  | Kimi endpoint address                        | Requests go to Anthropic's official endpoint and fail authentication               |
| `ANTHROPIC_AUTH_TOKEN`                                                                                                                | Kimi API key                                 | Returns 401 authentication errors                                                  |
| `ANTHROPIC_MODEL`                                                                                                                     | Main conversation model                      | Model-not-found errors                                                             |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` / `ANTHROPIC_DEFAULT_HAIKU_MODEL` / `ANTHROPIC_DEFAULT_FABLE_MODEL` | Model used by each task tier                 | Tasks on the corresponding tier fail                                               |
| `CLAUDE_CODE_SUBAGENT_MODEL`                                                                                                          | Sub-agent model                              | Sub-agent tasks fail or degrade noticeably                                         |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW`                                                                                                     | Context window that triggers auto-compaction | Too small compacts early and loses context; too large causes context-length errors |
| `CLAUDE_CODE_EFFORT_LEVEL`                                                                                                            | Reasoning effort                             | Set to `max`; lower values may reduce quality on complex tasks                     |

## Models and Thinking Behavior

How the three models behave in Claude Code:

| Model               | Thinking mode                    | Notes                                                                                          |
| ------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------- |
| `kimi-k3` (default) | On by default, can be turned off | Works out of the box, no extra configuration needed                                            |
| `kimi-k2.7-code`    | Forced on, cannot be turned off  | Must enable Thinking in Claude Code (`Option+T` on macOS, `Alt+T` on Windows/Linux) before use |
| `kimi-k2.6`         | Optional                         | Good for latency-sensitive simple tasks                                                        |

With thinking off, requests to `kimi-k2.7-code` are rejected with `400 invalid thinking: only type=enabled is allowed for this model`.

## Confirm That the Configuration Took Effect

After configuring, you can first verify the endpoint and API key with curl:

```shell theme={null}
curl https://api.moonshot.ai/anthropic/v1/messages \
  --header "Authorization: Bearer YOUR_MOONSHOT_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{"model": "kimi-k3", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]}'
```

A normal JSON response means the endpoint and credential both work; a 401 means the API key is invalid or does not match the platform. Once confirmed, start Claude Code and enter `/status`:

* Base URL should show `https://api.moonshot.ai/anthropic`
* Model should show `kimi-k3[1m]`

<img src="https://mintcdn.com/moonshotai/itBsZbTU0XGFr-f_/assets/pics/cline/status.png?fit=max&auto=format&n=itBsZbTU0XGFr-f_&q=85&s=84464149fd3af7d1d4c00fe45900bf94" alt="status" width="1140" height="260" data-path="assets/pics/cline/status.png" />

Claude Code's `/model` menu shows the models you have configured.

<img src="https://mintcdn.com/moonshotai/sVOfnDeZovTyhGGi/assets/pics/cline/model-menu.png?fit=max&auto=format&n=sVOfnDeZovTyhGGi&q=85&s=1d452912c71a4c14e70c1f4acd348b7a" alt="model-menu" width="1140" height="308" data-path="assets/pics/cline/model-menu.png" />

Finally, send any message (for example `hello`). Receiving a normal reply confirms the end-to-end setup works:

<img src="https://mintcdn.com/moonshotai/sVOfnDeZovTyhGGi/assets/pics/cline/chat-verify.png?fit=max&auto=format&n=sVOfnDeZovTyhGGi&q=85&s=3f4547d2f09a2bc223912b68a14dee49" alt="chat-verify" width="1140" height="340" data-path="assets/pics/cline/chat-verify.png" />

## FAQ

<AccordionGroup>
  <Accordion title="401 authentication errors">
    * Check that `ANTHROPIC_AUTH_TOKEN` is a valid Kimi API key, and that `YOUR_MOONSHOT_API_KEY` has been replaced with your key;
    * Make sure `ANTHROPIC_BASE_URL` matches the platform where you created the key — create the key on the platform linked in "Get a Kimi API Key" above and use the endpoint shown on this page;
    * If you previously configured `ANTHROPIC_API_KEY`, remove it to avoid conflicts with `ANTHROPIC_AUTH_TOKEN` when both are present.
  </Accordion>

  <Accordion title="Model not found">
    Check the spelling of every model variable (`kimi-k3[1m]`), and make sure there are no extra spaces or quotes.
  </Accordion>

  <Accordion title="Background tasks or sub-agent errors">
    Usually `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_FABLE_MODEL`, or `CLAUDE_CODE_SUBAGENT_MODEL` is not configured, so the scenario requests a model name the Kimi endpoint cannot recognize. Fill them in per the Configuration Reference above.
  </Accordion>

  <Accordion title="Changes do not take effect">
    * Check for stale values in the `env` field of `~/.claude/settings.json`; run the cleanup script in the collapsed section above;
    * Check shell config files such as `~/.zshrc` and `~/.bashrc` for stale `ANTHROPIC_*` exports;
    * Restart Claude Code after modifying `settings.json`.
  </Accordion>

  <Accordion title="Previously signed in with /login">
    `ANTHROPIC_AUTH_TOKEN` takes precedence over a saved login, so no action is usually needed. Enter `/status` to confirm the active credential source; run `/logout` to clear a saved login.
  </Accordion>
</AccordionGroup>
