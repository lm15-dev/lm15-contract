Use this guide to help you diagnose and resolve common issues that arise when
you call the Gemini API. You may encounter issues from either
the Gemini API backend service or the client SDKs. Our client SDKs are
open sourced in the following repositories:

- [python-genai](https://github.com/googleapis/python-genai)
- [js-genai](https://github.com/googleapis/js-genai)
- [go-genai](https://github.com/googleapis/go-genai)

If you encounter API key issues, verify that you have set up
your API key correctly per the [API key setup guide](https://ai.google.dev/gemini-api/docs/api-key).

## Error codes

For a complete reference of all error codes, including HTTP status codes,
generation blocked codes, and content error codes, see the
[API errors](https://ai.google.dev/gemini-api/docs/api-errors) page.

## Retry strategy

If you receive an error indicating that you should retry your request (such as a `429 RESOURCE_EXHAUSTED` or `503 UNAVAILABLE`), we recommend implementing an exponential backoff strategy. This means you wait a short time before the first retry, and then gradually increase the wait time between subsequent retries.

The official client SDKs for the Gemini API, such as the [Python SDK](https://github.com/googleapis/python-genai), include automatic retry logic with exponential backoff by default for handling transient errors like timeouts, network issues, and rate limits (`429` and `5xx` status codes). For example, the Python SDK automatically retries transient errors up to four times with an initial delay of approximately 1 second and a maximum delay of 60 seconds.

If you are making direct REST API requests or customizing your retry logic, follow these best practices to increase the likelihood of a successful request and prevent overwhelming the service:

- **Use exponential backoff:** Wait a short time before the first retry (for example, 1 second), then increase the delay exponentially (for example, 2s, 4s, 8s).
- **Add jitter:** Add random "jitter" to the delay to help prevent all clients from retrying at the exact same time.
- **Retry on specific errors:** Only retry on transient errors (like `429`, `408`, or `5xx`). Do not retry on client errors (like `400` or `403`) as they indicate issues like invalid API keys or bad syntax.
- **Set maximum retries:** Define a maximum number of retry attempts to prevent infinite loops.

## Check your API calls for model parameter errors

Verify that your model parameters are within the following values:

|---|---|
| **Model parameter** | **Values (range)** |
| Candidate count | 1-8 (integer) |
| Temperature | 0.0-1.0 |
| Max output tokens | Use the [models page](https://ai.google.dev/gemini-api/docs/models/gemini) to determine the maximum number of tokens for the model you are using. |
| TopP | 0.0-1.0 |

In addition to checking parameter values, make sure you're using the correct
[API version](https://ai.google.dev/gemini-api/docs/api-versions) (e.g., `/v1` or `/v1beta`) and
model that supports the features you need. For example, if a feature is in Beta
release, it will only be available in the `/v1beta` API version.

## Check if you have the right model

Verify that you are using a supported model listed on our [models
page](https://ai.google.dev/gemini-api/docs/models/gemini).

## Higher latency or token usage with 2.5 models

If you're observing higher latency or token usage with the 2.5 Flash and Pro
models, this can be because they come with **thinking is enabled by default** in
order to enhance quality. If you are prioritizing speed or need to minimize
costs, you can adjust or disable thinking.

Refer to [thinking page](https://ai.google.dev/gemini-api/docs/thinking#set-budget) for
guidance and sample code.

## Safety issues

If you see a prompt was blocked because of a safety setting in your API call,
review the prompt with respect to the filters you set in the API call.

If you see `BlockedReason.OTHER`, the query or response may violate the [terms
of service](https://ai.google.dev/terms) or be otherwise unsupported.

## Recitation issue

If you see the model stops generating output due to the RECITATION reason, this
means the model output may resemble certain data. To fix this, try to make
prompt / context as unique as possible and use a higher temperature.

> [!NOTE]
> The \`temperature\`, \`top_p\`, and \`top_k\` parameters control how the model generates responses. Although you can modify these parameters, we strongly recommend keeping them at their default values for Gemini 3.x models. Changing these parameters (for example, setting the temperature below 1.0) can cause unexpected behavior, such as looping or degraded performance, particularly in complex mathematical or reasoning tasks.

## Repetitive tokens issue

If you see repeated output tokens, try the following suggestions to help
reduce or eliminate them.

| Description | Cause | Suggested workaround |
| Repeated hyphens in Markdown tables | This can occur when the contents of the table are long as the model tries to create a visually aligned Markdown table. However, the alignment in Markdown is not necessary for correct rendering. | Add instructions in your prompt to give the model specific guidelines for generating Markdown tables. Provide examples that follow those guidelines. You can also try adjusting the temperature. For generating code or very structured output like Markdown tables, high temperature have shown to work better (\>= 0.8). The following is an example set of guidelines you can add to your prompt to prevent this issue: ``` # Markdown Table Format * Separator line: Markdown tables must include a separator line below the header row. The separator line must use only 3 hyphens per column, for example: |---|---|---|. Using more hypens like ---, ---, --- can result in errors. Always use |:---|, |---:|, or |---| in these separator strings. For example: | Date | Description | Attendees | |---|---|---| | 2024-10-26 | Annual Conference | 500 | | 2025-01-15 | Q1 Planning Session | 25 | * Alignment: Do not align columns. Always use |---|. For three columns, use |---|---|---| as the separator line. For four columns use |---|---|---|---| and so on. * Conciseness: Keep cell content brief and to the point. * Never pad column headers or other cells with lots of spaces to match with width of other content. Only a single space on each side is needed. For example, always do "| column name |" instead of "| column name                |". Extra spaces are wasteful. A markdown renderer will automatically take care displaying the content in a visually appealing form. ``` |
| Repeated tokens in Markdown tables | Similar to the repeated hyphens, this occurs when the model tries to visually align the contents of the table. The alignment in Markdown is not required for correct rendering. | - Try adding instructions like the following to your system prompt: ``` FOR TABLE HEADINGS, IMMEDIATELY ADD ' |' AFTER THE TABLE HEADING. ``` - Try adjusting the temperature. Higher temperatures (\>= 0.8) generally helps to eliminate repetitions or duplication in the output. |
| Repeated newlines (`\n`) in structured output | When the model input contains unicode or escape sequences like `\u` or `\t`, it can lead to repeated newlines. | - Check for and replace forbidden escape sequences with UTF-8 characters in your prompt. For example, `\u` escape sequence in your JSON examples can cause the model to use them in its output too. - Instruct the model on allowed escapes. Add a system instruction like this: ``` In quoted strings, the only allowed escape sequences are \\, \n, and \". Instead of \u escapes, use UTF-8. ``` |
| Repeated text in using structured output | When the model output has a different order for the fields than the defined structured schema, this can lead to repeating text. | - Don't specify the order of fields in your prompt. - Make all output fields required. |
| Repetitive tool calling | This can occur if the model loses the context of previous thoughts and/or call an unavailable endpoint that it's forced to. | Instruct the model to maintain state within its thought process. Add this to the end of your system instructions: ``` When thinking silently: ALWAYS start the thought with a brief (one sentence) recap of the current progress on the task. In particular, consider whether the task is already done. ``` |
| Repetitive text that's not part of structured output | This can occur if the model gets stuck on a request that it can't resolve. | - If thinking is turned on, avoid giving explicit orders for how to think through a problem in the instructions. Just ask for the final output. - Try a higher temperature \>= 0.8. - Add instructions like "Be concise", "Don't repeat yourself", or "Provide the answer once". |
|---|---|---|

## Blocked or non-working API keys

This section describes how to check whether your Gemini API key is blocked
and what to do about it.

### Understand why keys are blocked

We have identified a vulnerability where some API keys may have been publicly
exposed. To protect your data and prevent unauthorized access, we have
proactively blocked these known leaked keys from accessing the Gemini API.

### Confirm if your keys are affected

If your key is known to be leaked, you can no longer use that key with the
Gemini API. You can use [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-keys) to see if any of
your API keys are blocked from calling the Gemini API and generate new
keys. You may also see the following error returned when attempting to use
these keys:

    Your API key was reported as leaked. Please use another API key.

### Action for blocked API keys

You should generate new API keys for your Gemini API integrations using [Google
AI Studio](https://ai.google.dev/gemini-api/docs/api-keys). We strongly recommend reviewing your API
key management practices to ensure that your new keys are kept secure and are
not publicly exposed.

### Unexpected charges due to vulnerability

[Submit a billing support case](https://console.cloud.google.com/support/chat).
Our billing team is working on this, and we will communicate updates as soon as
possible.

### Google's security measures for leaked keys

**How is Google going to help secure my account from cost overrun and abuse if
my API keys are leaked?**

- We are moving towards issuing API keys when you request a new key using [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-keys) that will by default be limited to only Google AI Studio and not accept keys from other services. This will help prevent any unintended cross-key usage.
- We are defaulting to blocking API keys that are leaked and used with the Gemini API, helping prevent abuse of cost and your application data.
- You will be able to find the status of your API keys within [Google AI
  Studio](https://ai.google.dev/gemini-api/docs/api-keys) and we will work on communicating proactively when we identify your API keys are leaked for immediate action.

## Improve model output

For higher quality model outputs, explore writing more structured prompts. The
[prompt engineering guide](https://ai.google.dev/gemini-api/docs/prompting-strategies) page
introduces some basic concepts, strategies, and best practices to get you
started.

## Understand token limits

Read through our [Token guide](https://ai.google.dev/gemini-api/docs/tokens) to better understand how
to count tokens and their limits.

## Known issues

- The API supports only a number of select languages. Submitting prompts in unsupported languages can produce unexpected or even blocked responses. See [available languages](https://ai.google.dev/gemini-api/docs/models#supported-languages) for updates.

## File a bug

Join the discussion on the
[Google AI developer forum](https://discuss.ai.google.dev)
if you have questions.