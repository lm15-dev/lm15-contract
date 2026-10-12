# Subscriptions

With a Muse Code subscription, you pay a flat monthly rate for usage of [Muse Code](https://dev.meta.ai/products/muse-code), instead of paying per token. Subscription benefits and availability may vary by region. Available benefits will be shown to you during onboarding before you subscribe.

## About subscriptions

To sign up for a Muse Code subscription, you will need a Meta Account. Using your Meta Account, you can create an associated Meta Model API account and sign up for a subscription. The subscription applies to the Muse Code API key that is automatically connected in the Muse Code CLI onboarding process. This credential is for use with Muse Code only. Any additional API keys you create under your Meta Model API account will be billed through [pay-as-you-go](https://dev.meta.ai/docs/muse-code/auth#billing).

You must be 18 or the age of majority in your country to subscribe. Your subscription is subject to the [Meta Subscription Terms of Service](https://www.facebook.com/legal/meta_subs_terms), and your use of Muse Code and the Meta Model API is governed by the [Meta Model API Terms of Service](https://dev.meta.ai/legal/terms-of-service) and the [Meta Model API Acceptable Use Policy](https://dev.meta.ai/legal/acceptable-use-policy).

How Meta uses your content — the prompts, code, files, and context you send, plus the model responses you get back — depends on whether [Contributor mode](https://dev.meta.ai/docs/muse-code/subscriptions#contributor-mode) is on in your settings, and is described in the [Meta Model API Terms of Service](https://dev.meta.ai/legal/terms-of-service).

There are 4 subscription plans available for Muse Code:

### Everyday Usage

- Access to the Muse model family
- Send 10-50 prompts every 5 hours, including image and video uploads
- Use voice mode
- Get access to web search

### High Usage

- Everything from the Everyday Usage plan
- 5x more usage than the Everyday Usage plan
- More multimodal inputs

### Power Usage

- Everything from the High Usage plan
- Access to the most powerful Muse models
- 20x more usage than the Everyday Usage plan
- Early access to new features
- Higher file uploads

### Maximum Usage

- Everything from the Power Usage plan
- 80x more usage than the Everyday Usage plan

## Contributor mode

Muse Code subscriptions default to Contributor mode. In Contributor mode, you get more usage from your plan in exchange for letting Meta use your content to train future Meta models. Contributor mode is a setting in Muse Code, and you can turn it off at any time, at which point your future content is not used to train Meta models (unless you turn it back on in your settings).

Muse Wonder and Muse Wonder Full are each available in either mode on the plans that include them. For the models each plan includes, see [Muse Wonder availability](https://dev.meta.ai/docs/models#muse-wonder-availability).

## Choose pay-as-you-go or a subscription

Muse Code supports 2 ways to pay for usage:

- **Pay-as-you-go**: billed per token consumed with your Meta Model API key. See [billing and plans](https://dev.meta.ai/docs/muse-code/auth#billing).
- **Subscription**: a flat monthly rate (see the plans above). It works only through the Muse Code CLI while signed in with your Meta Model API account.

If you reach your plan's usage limit, you can upgrade to the next plan, or wait until your limit refreshes. If you are on the Maximum Usage plan, you must wait for your limit to refresh. Usage through any additional API keys you create is billed pay-as-you-go.

## Subscribe

Sign in to Muse Code with your Meta Model API account on [dev.meta.ai](https://dev.meta.ai/), then subscribe through Accounts Center:

1. Go to **Subscriptions** in [Accounts Center](https://accountscenter.meta.com/).
2. Select **Muse Code**, then choose a plan and complete checkout.
3. On success, you will see a confirmation screen with a link to your receipt and the option to **Manage your subscription**.

## Change or cancel your plan

Manage your plan from **Manage your subscription** on the Subscriptions page in [Accounts Center](https://accountscenter.meta.com/). From an interactive session, type `/upgrade` to open Accounts Center in your browser.

- **Upgrade**: A plan upgrade takes effect immediately. You will be charged a prorated amount for the rest of the current billing cycle.
- **Downgrade**: A plan downgrade takes effect at the start of your next billing cycle. You will keep your current plan's usage limit until the next billing cycle.
- **Cancel**: From Accounts Center, go to Manage your subscription and select **Cancel subscription**. Your subscription stays active until the end of the current billing cycle, then you lose access to all benefits. Cancel at least 24 hours before your next billing date to avoid future charges.

## What happens when your subscription ends

A subscription ends one of 2 ways: you can cancel it (see [Change or cancel your plan](https://dev.meta.ai/docs/muse-code/subscriptions#change-or-cancel)), or Meta can revoke it.

Revocation is different from cancellation. When your subscription is revoked, you lose access immediately instead of at the end of your billing cycle. Meta may revoke a subscription for various reasons, including:

- **Payment failure**: your payment method fails and you have no backup payment method on file.
- **Policy violation**: your account violates the [Model API terms](https://dev.meta.ai/legal/terms-of-service), [Meta's Community Standards](https://transparency.meta.com/policies/community-standards) or [Meta Subscription Terms of Service](https://www.facebook.com/legal/meta_subs_terms).
- **Account deletion or deactivation**: deleting your account cancels the subscription immediately. Deactivating your account keeps the subscription active for 30 days. If you don't reactivate within that window, Meta revokes it.
- **Loss of eligibility**: for example, your account no longer meets the age requirement, or you move to a restricted territory.

To subscribe again after a revocation, your account must meet the eligibility requirements in [About subscriptions](https://dev.meta.ai/docs/muse-code/subscriptions#about).

## Billing cycle

Your subscription renews automatically each month on the date you first subscribed. If that date doesn't exist in a given month (for example, the 31st in a 30-day month), you're charged on the last day of that month instead.

Manage your payment method and view billing history from [Accounts Center](https://accountscenter.meta.com/).

**No refunds for canceled subscriptions**: if you cancel your subscription, you won't receive a credit or refund unless required by law.

## Next steps

- Set up sign-in and pay-as-you-go billing in [authentication and billing](https://dev.meta.ai/docs/muse-code/auth).
- Start your first session in the [overview](https://dev.meta.ai/docs/muse-code#first-run).
