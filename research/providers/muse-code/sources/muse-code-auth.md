# Authentication and billing

Muse Code needs a Meta credential before it can call the model. On first run it prompts you to choose how to authenticate: a browser sign-in or an API key. For scripts and CI, use an API key.

## Sign in

The first time you run Muse Code, start it in your project:

```bash
muse
```

On first run, Muse Code prompts you to authenticate and offers two options:

- **Sign in with your browser**: opens your web browser to approve the session, then returns you to the terminal.
- **Paste an API key**: paste a Meta API key directly, without the browser flow.

Muse Code stores the credential for you and resumes where you stopped. Reopen these options any time from an interactive session with `/login`.

> **NOTE: MMA accounts need an API key**
>
> Meta Managed Account (MMA) users, who sign up through **Business & Enterprise** on the Model API sign-in screen, must authenticate with an API key: MMA accounts can't use the browser sign-in flow. Choose **Paste an API key** at first run, or set `META_API_KEY` in your environment as shown in [Use an API key](https://dev.meta.ai/docs/muse-code/auth#api-keys).

## Use an API key

For a non-interactive environment, or to avoid the browser flow, authenticate with an API key. Set it in the environment:

```bash
export META_API_KEY="<your-key>"
```

Or store it with:

```bash
muse auth set
```

An API key always takes priority over a browser sign-in. Muse Code uses `META_API_KEY` if set, then a stored key, and only then a stored browser session. If an environment key hides a browser session you created, Muse Code tells you.

## Authenticate in CI

A pipeline has no browser, so provide `META_API_KEY` in the environment (from your CI secret store):

```bash
META_API_KEY="$MUSE_KEY" muse exec "Run the test suite and summarize failures."
```

See [headless and CI](https://dev.meta.ai/docs/muse-code/extending#headless) for non-interactive runs.

## Sign out

Remove the stored Meta credential with:

```bash
muse logout
```

`muse logout` clears the stored browser session and any stored key. It does **not** unset a `META_API_KEY` you exported in your environment. Remove that from your shell or secret store separately.

## Billing and plans

### Billing setup

Meta Model API billing is usage-based: you're billed for the tokens your requests consume. This page explains how to set up billing and how charges work. For step-by-step instructions, see how to [set up billing](https://dev.meta.ai/help/billing/set-up-billing) and [download invoices](https://dev.meta.ai/help/billing/download-invoice) in the Help Center.

Prefer a flat monthly rate instead of pay-as-you-go pricing? See [subscriptions](https://dev.meta.ai/docs/muse-code/subscriptions).

### How to add payment

A team admin needs to complete two steps:

1. **Add a payment method.** Go to [Billing](https://dev.meta.ai/billing) and add a payment method. See [How to set up billing](https://dev.meta.ai/help/billing/set-up-billing) for detailed instructions.
2. **Create an API key.** See [Authentication](https://dev.meta.ai/docs/authentication) for instructions.

Only team admins can manage payment methods and business information.

### How billing works

Charges are based on token usage. Every request consumes:

- **Input tokens**: your prompt, system instructions, and conversation history.
- **Output tokens**: the text the model generates. Output tokens typically cost more than input tokens.

Costs may vary by model. For current per-model rates, see [Pricing and rate limits](https://dev.meta.ai/docs/pricing-rate-limits).

> **NOTE: What counts as a token**
>
> A token is roughly 3–4 characters of English text. Non-English text and code often use more tokens per word, so equivalent requests can cost more depending on the language and content type. Use the [Usage dashboard](https://dev.meta.ai/usage) to see how many tokens your requests consume.

### When you're charged

Charges accrue as you use the API. Your payment method is charged in one of two situations:

- **Payment threshold reached.** Whenever your current balance reaches your payment threshold amount, your payment method is charged for that amount. As you make successful payments, your payment threshold may be raised until your account reaches a final threshold amount.
- **Monthly bill date.** Any remaining balance is automatically charged on the first of each month.

If you have a current balance, you can use **Pay now** on the [Billing](https://dev.meta.ai/billing) page to make an early payment before you reach your payment threshold or monthly bill date.

## Next steps

- Start your first session in the [overview](https://dev.meta.ai/docs/muse-code#first-run).
- Set your default model and preferences in [configuration and context](https://dev.meta.ai/docs/muse-code/configuration).
