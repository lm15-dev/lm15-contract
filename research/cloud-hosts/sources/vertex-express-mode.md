Home

          Documentation

          AI and ML

          Gemini Enterprise Agent Platform

          Models

    Send feedback

      Gemini Enterprise Agent Platform in express mode overview

      Stay organized with collections

      Save and categorize content based on your preferences.

        Preview

          This feature is

        subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the
        Service Specific
        Terms.

        Pre-GA features are available "as is" and might have limited support.

      For more information, see the
      launch stage descriptions.

With Agent Platform in express mode, you can quickly sign up and begin
building generative AI applications on Google Cloud. This
simplified setup experience streamlines access to Google Cloud APIs by
simplifying organization, billing, and project management.

To learn more about Agent Platform in express mode, see Google Cloud
express mode FAQs.

Sign up for express mode

Agent Platform is available in express mode for developers with a
@gmail.com Google Account:

New users: New users to Google Cloud can sign up for an express
mode account in a free tier to try Agent Platform for free for up to
90 days, within the specified quotas. You don't need to provide billing
information to sign up in the free tier. You can upgrade to a paid tier by
adding a billing account.

Agent Platform in express mode is separate from, and not available
through, the Google Cloud Free
Program. If you are in the
Google Cloud Free Program, see the
other quickstarts in the Get Started section.

To sign up for Agent Platform in express mode, access Express Mode
from the Google Cloud console:

Go to Express Mode

After you're set up, you can start using Agent Platform in express mode
by following one of the tutorials:

Tutorial: Agent Studio in express mode

Tutorial: Agent Platform API in express mode

Learn about Agent Platform in express mode

When you sign up for express mode, Google Cloud enables APIs on your
behalf. This process happens in the background, so you can start using
Agent Platform without needing to manually configure resources.

When you sign up for express mode, you get access to the following:

Core Agent Studio features. Quickly test and customize prompts
for different generative AI models, and get the corresponding code to use in
your application.

An API key. Authenticate fast from your application.

Free tier for new Google Cloud users during 90 days. During the 90
day limit of the free tier for new Google Cloud users, you can use the
Agent Platform APIs that support express mode
for free, up to their quotas. You don't have to provide billing
information. You can increase your quota limits at any time by enabling
billing.

If you are an existing Google Cloud user or after enabling billing, the 90
day free tier is removed. You transition to a paid tier to access extended quota
limits and additional Google Cloud features. As your quotas are increased,
you only pay for what you use. At any time, you can choose to end express
mode and start using all the Google Cloud services and
capabilities.

The following table lists the differences between the express mode experiences
and the full Agent Platform experience:

    Item
    Agent Platform express mode in the free tier
    Full Agent Platform

    Time limit
    90 days
    Unlimited

    Available services
    Basic generative AI services.
    All Google Cloud services, including Agent Platform.

    Data sources
    Google Drive
    All data sources available in Google Cloud.

    Quota
    Free tier limits. See Available models and rate limits in express mode.
    Standard pay-as-you-go limits. See Rate limits.

    Standard format of API endpoints
    Specify API key instead of project ID and location. For example:

    https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:streamGenerateContent?key={API_KEY}

    Specify project ID and location. For example:

    https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:streamGenerateContent

Available models and rate limits in express mode

You can try out several models in express mode, including the latest
Gemini Flash models. The following table lists the models that are
available in express mode, along with their rate limits:

    Model category
    Available models
    Maximum requests per minute

    Gemini
    gemini-3.1-flash-image-preview
    Dynamic

    gemini-3.1-pro-preview
    Dynamic

    gemini-3-flash-preview
    Dynamic

    gemini-3-pro-preview
    Dynamic

    gemini-3-pro-image-preview
    Dynamic

    gemini-2.5-flash-image
    10

    gemini-2.5-flash-lite-preview-09-2025
    10

    gemini-2.5-flash-lite
    10

    gemini-2.5-pro
    10

    gemini-2.5-flash
    10

    gemini-2.5-flash-image
    10

    gemini-2.0-flash-001
    10

    gemini-2.0-flash-lite-001
    10

For Gemini 2.0 models, the Live API isn't available in the
Google Cloud console in express mode. To use the Live API in express
mode, use the Agent Platform API or the Google Gen AI SDK.

Agent Platform in express mode workflow

You can start sending requests from your application to Agent Platform
APIs in three steps:

After signing up for express mode, use
Agent Studio to quickly try Agent Platform features:

Go to Agent Studio

For example, select Agent Studio > Create prompt to create and
optimize multimodal prompts using a variety of Gemini models.

Get the code for what you implemented with the UI.

On the prompt page, click Build with code > Get code. A panel opens
showing code that programmatically sends the same requests that you
implemented in the UI. You can get the code for a programming language or
curl. You can use Google Colab to try
the Python code.

Use your API key to authenticate with the Agent Platform API.

In Google Cloud console in express mode, open APIs & Services > Credentials:

Go to Credentials

Then, copy your Generative Language API Key into your code where it says
"YOUR_API_KEY". For example:

  Python

The Google Gen AI SDK for Python is available on PyPI and GitHub:

google-genai on PyPI

python-genai on GitHub

To learn more, see the
Python SDK reference (opens in a new tab).

from google import genai

# TODO(developer): Update below line
API_KEY = "YOUR_API_KEY"

client = genai.Client(vertexai=True, api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Explain bubble sort to me.",
)

print(response.text)
# Example response:
# Bubble Sort is a simple sorting algorithm that repeatedly steps through the list

What's different in express mode

Agent Platform in express mode provides a subset of the features for
generative AI. Therefore, some of the Agent Platform
documentation is not relevant if you signed up in express mode. For details on
the available API endpoints in express mode, see the Agent Platform in
express mode REST API
reference.

In addition, customers in Google Cloud typically use
organizations and projects to work with resources (for example, to call an
API endpoint). When using Agent Platform in express mode, you don't need
to worry about organizations or projects. However, you might see them mentioned
in some of the Google Cloud documentation that you reference while you're
using Agent Platform in express mode. You can still use the
documentation, but ignore concepts and instructions that refer to organizations
and projects. In addition, the location you
selected when signing up in express mode is used throughout your experience.

When calling REST API endpoints in express mode, you'll use the endpoint format
for express mode and specify your API key. For example:

      Standard endpoint URL
      https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:streamGenerateContent

      Endpoint URL in express mode
      https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:streamGenerateContent?key={API_KEY}

View and manage API keys

To authenticate with Agent Platform API endpoints that support express
mode,
use the API key that was created for you during sign-up or any key that you've
created in express mode. An API key is an encrypted string that is
auto-generated for you when you sign up in express mode. These API keys can be
viewed and managed on the APIs & Services page.

To learn more about the best practices for managing API keys, see Best
practices for managing API keys.

To view and manage your API keys, do the following:

In the Google Cloud console, go to the API Keys page:

Go to API Keys

Enable and manage billing

You can increase your quotas and remove the 90 day limit by enabling billing.

After enabling billing, you pay only for what you use. You can also save your
prompts and access additional settings in the Google Cloud console that are that
grayed out when billing isn't enabled.

To manage billing, do the following:

Go to the Agent Studio Overview page in express mode.

Go to Agent Studio

In Google Cloud console in express mode, open Billing:

Go to Billing

Manage your billing accounts.

Start using all Google Cloud capabilities and services

Express mode is designed to help you get started quickly. When you're ready to
use other Google Cloud services or need more control over your
environment, you can transition your express mode account to a standard
Google Cloud account. This process is sometimes called upgrade.

You can start using all the capabilities and services available in
Google Cloud in your project by upgrading your express mode account.

To upgrade from express mode, do the following:

Go to the Agent Studio Overview page in express mode.

Go to Agent Studio

Click Activate now and follow the instructions.

After you upgrade from express mode, specify your project ID and location
instead of your API key when you call the REST API endpoints. For example:

https://{location}-aiplatform.googleapis.com/v1/projects/{projectid}/locations/{location}/publishers/google/models/{model}:streamGenerateContent

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-09-02 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-09-02 UTC."],[],[]]
