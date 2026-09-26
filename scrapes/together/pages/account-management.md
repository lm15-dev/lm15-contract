> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Manage your account

> Sign up for Together AI, get your API key, and manage your account settings.

## Create an account

Head to [together.ai](https://www.together.ai/) and select **Get Started**. You can sign in with Google or GitHub.

Together uses OAuth (Open Authorization) instead of a traditional username and password. This keeps your account secure and means one less password to remember.

**Important:** You must always sign in with the same provider you used at signup. If you try a different provider, you'll see "This email is already linked to another sign-in method."

<Note>
  LinkedIn authentication was previously available but has been discontinued. If you signed up with LinkedIn, you can now sign in with Google or GitHub using the same email address.
</Note>

## Create an API key

Once your account is set up, create a Project API key to start making requests.

<Card title="API Keys & Authentication" icon="key" href="/docs/api-keys-authentication">
  Create, scope, and manage your API keys.
</Card>

## Change your email address

Because Together uses OAuth, email addresses can't be changed directly. To transfer your account to a new email:

1. **Create a new account** with your preferred email address
2. **Contact support** from your current email and provide the new email address
3. **Old account deactivation** -- your original account will be blocked to prevent confusion
4. **Update your integrations** -- update any API integrations to use your new account's API key

Once the transfer is complete, you'll have access to all your previous features and credits under the new email.

## Delete your account

You can delete your account through the self-service process. This complies with GDPR and other data protection regulations.

1. Log in to your Together AI account
2. Navigate to your profile settings at [api.together.ai/settings/profile](https://api.together.ai/settings/profile)
3. Scroll down to the **Privacy and Security** section
4. Select the **delete your account** link
5. Follow the prompts to confirm

<Warning>
  Account deletion removes all your personal data and unsubscribes you from all mailing lists. This cannot be undone. Due to OAuth authentication, you cannot create a new account using the same email address after deletion -- you would need a different email to sign up again.
</Warning>

If you run into any issues, [contact support](https://portal.usepylon.com/together-ai/forms/support-request).

## Next steps

Your account belongs to an *organization*: a shared workspace for managing member access, project collaboration, and billing in one place. Learn more by reading these pages:

<CardGroup cols={2}>
  <Card title="Organizations" icon="building" href="/docs/organizations">
    Learn how membership and project collaboration work on Together.
  </Card>

  <Card title="Roles and permissions" icon="shield" href="/docs/roles-permissions">
    Control what each member can do in your organization.
  </Card>

  <Card title="Projects" icon="folder" href="/docs/projects">
    Organize work so teammates can share API keys, models, and usage.
  </Card>
</CardGroup>
