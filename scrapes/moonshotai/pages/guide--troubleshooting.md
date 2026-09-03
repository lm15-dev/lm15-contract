> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Troubleshooting

> Troubleshoot common Kimi API issues involving accounts, billing, authentication, model parameters, output length, rate limits, and connectivity.

<AccordionGroup>
  <Accordion title="Are balances and API keys shared between the Kimi API Open Platform, Kimi Code, and Kimi Membership?">
    No. The Kimi API Open Platform, Kimi Code, and Kimi Membership are independent products. Their billing models, balances/benefits, and API keys are not interchangeable:

    * The Kimi API Open Platform is pay-as-you-go with no subscription plan. To call the Kimi API, create an API key in the Open Platform console and use the endpoint for your region — see [Products and Plans](/docs/guide/product-plans).
    * Kimi Code is a separate coding product. Its API keys are not interchangeable with Open Platform keys. See the [Kimi Code documentation](https://www.kimi.com/code/docs/en/) for setup.
    * Kimi Membership (subscription) benefits do not convert into Open Platform balance, and Open Platform top-up balance cannot be used to purchase Kimi Membership or Kimi Code plans.

    Using a key from another product against the Open Platform endpoint returns 401 or 404 errors. See the checklist in "Why do I get 401, 404, or permission denied?" below.
  </Accordion>

  <Accordion title="Why do I still get 429 after topping up?">
    429 is not a single cause. Check the `error.type` in the response first:

    * `engine_overloaded_error`: the service node is under high load (for example, peak-hour capacity pressure). Wait as indicated by `Retry-After`, reduce concurrency, and retry with exponential backoff. This error is caused by server-side capacity — topping up or upgrading your tier does not resolve it;
    * `rate_limit_reached_error`: an organization-level concurrency, RPM, TPM, or TPD limit was reached. Reduce request frequency, or see [Top-up and Rate Limits](/docs/pricing/limits) to upgrade your tier;
    * `exceeded_current_quota_error`: insufficient balance, an overdue account, or an expired voucher. Check `available_balance` with the [balance API](/docs/api/balance) and top up.

    Note that clients such as the OpenAI SDK retry automatically by default, so one operation may be amplified into multiple requests that consume rate-limit quota. Check the actual request count and client logs when troubleshooting.

    Requests interrupted by a 429 error are not charged.
  </Accordion>

  <Accordion title="Why do I get 401, 404, or permission denied?">
    Check in the following order:

    1. Whether the key comes from the product you are calling: Open Platform API keys and Kimi Code keys are not interchangeable;
    2. Whether the key's region matches the endpoint: accounts, balances, and keys on platform.kimi.ai are isolated from other regional Kimi platforms;
    3. Whether the account has available balance, and whether your voucher covers the target model;
    4. Call `GET /v1/models` with the same key to confirm the target model is in the returned list;
    5. Whether the model name matches your integration path: direct API calls and Codex use `kimi-k3`, while Claude Code uses the compatible alias `kimi-k3[1m]`. Follow the corresponding integration tutorial;
    6. Clear stale environment variables, proxies, and old configurations in local routing tools such as CC Switch, and confirm which key and endpoint actually take effect.

    See also: [Error Codes](/docs/api/errors), [Use Kimi in Claude Code](/docs/guide/claude-code-kimi), [Use Kimi in Codex](/docs/guide/codex-kimi).
  </Accordion>

  <Accordion title="A third-party agent or IDE still fails after configuring Kimi — how do I locate the problem?">
    Split the chain into two layers: the Kimi API and the third-party tool.

    1. Call the Kimi API directly with the same key, endpoint, and model (see the cURL example in the [Kimi K3 quickstart](/docs/guide/kimi-k3-quickstart#basic-call));
    2. If the direct call fails, resolve balance, authentication, model permission, or request parameter issues first;
    3. If the direct call succeeds but the third-party tool still fails, check the tool's logs — focus on protocol conversion, streaming responses, timeout settings, and automatic retries;
    4. When using [Claude Code](/docs/guide/claude-code-kimi), [Codex](/docs/guide/codex-kimi), [OpenCode](/docs/guide/open-code), and similar tools, follow the corresponding tutorial — model names and configuration may differ;
    5. Keep the client version, time of occurrence, `request_id`, actual request endpoint, and redacted logs for further troubleshooting.

    Note that third-party tools such as CC Switch and Trae are not maintained by the Kimi Open Platform. If the direct API call works but the tool fails, contact the tool's support channel as well.
  </Accordion>

  <Accordion title="Why was I charged when the agent showed no result?">
    No result on the client does not mean the API request failed. When a coding tool stops waiting too early, a proxy disconnects, or a local timeout occurs, the client may stop displaying while the server-side request still completes and produces an actual call record.

    Check in order:

    1. The HTTP status code and `request_id` of the request;
    2. The `usage` field in the API response;
    3. Whether the client retried automatically, spawned sub-agents, or looped tool calls;
    4. The usage dashboard and billing details in the console;
    5. Timeout and connection errors in the client logs.

    If the platform records still clearly disagree with the client records, email [api-service@moonshot.ai](mailto:api-service@moonshot.ai) with your organization ID, project, time of occurrence, `request_id`, model, client version, redacted logs, and billing details.
  </Accordion>

  <Accordion title="How do I review billing details and report unexpected charges?">
    First open the [Open Platform console](https://platform.kimi.ai/console) to review the usage dashboard and billing details. Reconcile them against client logs and the `usage` returned by the API by time, project, model, and `request_id`.

    If you need help from the platform team, prepare: organization ID, project name, time of occurrence (with time zone), `request_id`, model name, client and version, redacted logs, and relevant billing or export records, then email [api-service@moonshot.ai](mailto:api-service@moonshot.ai).
  </Accordion>

  <Accordion title="Does Context Caching require manual configuration?">
    No. The Kimi API automatically attempts to cache repeated initial context — no cache ID, TTL, or extra request parameters are needed.

    Keeping the initial prefix stable (system prompt, tool definitions, long documents) helps subsequent requests hit the cache. Modifying the prefix may reduce the hit rate. See [Context Caching](/docs/guide/use-context-caching-feature-of-kimi-api).
  </Accordion>

  <Accordion title="What do I need to use Kimi K3?">
    Kimi K3 is unlocked after a successful top-up (minimum \$1). Your cumulative top-up amount also determines your account tier and rate limits — see [Recharge and Rate Limits](/docs/pricing/limits) and the [Kimi K3 quickstart](/docs/guide/kimi-k3-quickstart).
  </Accordion>

  <Accordion title="How do I choose a reasoning effort level for Kimi K3?">
    K3 always thinks. Set the reasoning effort with the top-level `reasoning_effort` field: `low`, `high`, or `max` (default `max`). Use higher levels for more complex tasks; lower levels reduce latency and token consumption for simple tasks.

    See [Reasoning Effort](/docs/guide/use-reasoning-effort) for details and examples.
  </Accordion>

  <Accordion title="How do I turn off Kimi K3's chain-of-thought?">
    You can't — K3 always thinks. If the reasoning takes too long, set `reasoning_effort` to `low` to reduce the reasoning effort. See [Reasoning Effort](/docs/guide/use-reasoning-effort).
  </Accordion>

  <Accordion title="Can I try the models before topping up?">
    You can run a minimal test in the [Playground](https://platform.kimi.ai/playground) to confirm whether a model and prompt fit your scenario, and use the [MoonPalace debugging tool](/docs/guide/use-moonpalace) to capture complete requests while coding. Available models and voucher coverage are subject to what the Playground and account pages actually show.
  </Accordion>

  <Accordion title="Why does the model repeatedly call the same tool when using `tool_calls`?">
    Check the message layout first (add `choice.message` as is, match `tool_call_id`, assemble streamed `tool_calls` correctly). If the repetition persists, add client-side repeated-call detection and append system prompt reminders. See [How to fix repeated tool calls](/docs/guide/tool-call-repeat).
  </Accordion>

  <Accordion title="Why are API results different from Kimi Assistant results?">
    The Kimi API and Kimi Assistant are different product experiences. The model version, system prompt, context management, tool configuration, and product policies may differ, so identical input does not necessarily produce identical output.

    When using the API, choose a model, set the system prompt, manage conversation context, and declare the required tools for your application. See the [Model List](/docs/models) and [Model Parameter Reference](/docs/api/models-overview) for available models and parameter differences.
  </Accordion>

  <Accordion title={"Does the Kimi API have Kimi Assistant's \"web browsing\" feature?"}>
    <Warning>
      The web search (`web_search`) is currently being updated. We do not recommend using this functionality in the near term. This documentation is outdated; please follow subsequent content updates.
    </Warning>

    Yes. The Kimi API provides the built-in `$web_search` tool. Declare it as a `builtin_function` in the request's `tools` field and handle its results through the standard `tool_calls` flow. Web search is not enabled automatically for every API request.

    See [Use Web Search with the Kimi API](/docs/guide/use-web-search) for the declaration and complete example. To connect your own or a third-party search service, see [Use the Kimi API for Tool Calls](/docs/guide/use-kimi-api-to-complete-tool-calls).
  </Accordion>

  <Accordion title="The content returned by the Kimi API is incomplete or truncated">
    If the content returned by the Kimi API is incomplete, truncated, or shorter than expected, first check the value of `choice.finish_reason` in the response body. If the value is `length`, it means the number of tokens generated by the current model exceeded the `max_completion_tokens` parameter in the request. In this case, the Kimi API only returns up to `max_completion_tokens` tokens, and any extra content is discarded.

    When you encounter `finish_reason=length`, and you want the Kimi model to continue from the previous response, you can use Partial Mode. For details, see:

    [Use Partial Mode with the Kimi API](/docs/guide/use-partial-mode-feature-of-kimi-api)

    To avoid `finish_reason=length`, we recommend increasing `max_completion_tokens` appropriately. A best practice is to use the [estimate-token-count](/docs/api/estimate) API to calculate the number of tokens in the input, then subtract that number from the maximum context window supported by the selected model. For example, `kimi-k3` supports up to 1M tokens, while `kimi-k2.7-code` and `kimi-k2.6` support up to 256k tokens. The remaining value can be used as the upper bound for `max_completion_tokens` in the current request.
  </Accordion>

  <Accordion title="What is the output length of the Kimi model?">
    * For `kimi-k3`, `max_completion_tokens` defaults to 131072, and the maximum output length is `1024*1024 - prompt_tokens`.
    * For `kimi-k2.7-code` and `kimi-k2.6`, the maximum output length is `256*1024 - prompt_tokens`.
  </Accordion>

  <Accordion title="How many Chinese characters does the Kimi model support?">
    * `kimi-k3` supports approximately 1,500,000 Chinese characters.
    * `kimi-k2.7-code` and `kimi-k2.6` support approximately 400,000 Chinese characters.

    *Note: These are estimates. Actual results may vary.*
  </Accordion>

  <Accordion title="File extraction is inaccurate, or images cannot be recognized">
    We provide file upload and parsing services for various file formats. **For text-based files, we extract the text content.**

    *Note: Image files and image-only PDFs no longer support content extraction. To understand image content, upload images with `purpose="image"`.*

    For the complete list of supported file formats and how to use image understanding, see:

    [Files Upload API](/docs/api/files-upload)

    [Use Vision Models](/docs/guide/use-kimi-vision-model)
  </Accordion>

  <Accordion title="When using the `files` API, I want to reference file content with `file_id`">
    We currently do not support referencing file content as context through a file `file_id`.
  </Accordion>

  <Accordion title="Error: `content_filter: The request was rejected because it was considered high risk`">
    The input to the Kimi API, or the output from the Kimi model, contains unsafe or sensitive content. **Note: Content generated by the Kimi model may also contain unsafe or sensitive content, which can trigger a `content_filter` error.**

    If you call the API through a third-party platform or tool, first confirm that the error was actually returned by the Kimi API: third-party platforms may apply their own content safety policies and error wording, so their messages do not necessarily come from the Kimi API. Check the third-party platform's logs as well.

    The platform cannot disclose the exact safety rules that were triggered. You can try narrowing the request scope, removing content that may cause false positives, and retry.
  </Accordion>

  <Accordion title="Connection-related errors">
    If you frequently encounter errors such as `Connection Error` or `Connection Time Out` while using the Kimi API, check the following in order:

    1. Whether your program code or SDK has a default timeout setting.
    2. Whether you are using any type of proxy server, and whether the proxy server network and timeout settings are correct.

    Another possible cause is generating too many tokens without enabling streaming output with `stream=True`. In this case, the request may wait too long for generation to finish and trigger a timeout in an intermediate gateway. Some gateway applications determine whether a request is valid by checking whether the server has returned a `status_code` and `header`. When `stream=True` is not used, the Kimi server waits until generation is complete before sending the `header`. While waiting for that `header`, some gateway applications may close long-running connections, causing connection-related errors.

    **We recommend enabling streaming output with `stream=True` to reduce connection-related errors as much as possible.**
  </Accordion>

  <Accordion title="The TPM or RPM limit in the error message does not match my account tier">
    If you encounter a `rate_limit_reached_error` while using the Kimi API, for example:

    ```text theme={null}
    rate_limit_reached_error: Your account {uid}<{ak-id}> request reached TPM rate limit, current:{current_tpm}, limit:{max_tpm}
    ```

    but the TPM or RPM limit in the error message does not match the TPM or RPM shown in the dashboard, first check whether you are using the correct `api_key` for the current account. In most cases, this mismatch is caused by using the wrong `api_key`, such as accidentally using a key provided by another user or mixing up keys across multiple accounts.
  </Accordion>

  <Accordion title="Error: `model_not_found`">
    Make sure your SDK is configured with `base_url=https://api.moonshot.ai/v1`. The `model_not_found` error is usually caused by using the OpenAI SDK without setting `base_url`, which sends the request to OpenAI servers instead. OpenAI then returns the `model_not_found` error.
  </Accordion>

  <Accordion title="The Kimi model makes numerical calculation errors">
    Due to the uncertainty of model generation, the Kimi model may make calculation errors of varying severity when performing numerical computations. We recommend using tool calls (`tool_calls`) to provide calculator functionality to the Kimi model. For more information, see our tool calling guide:

    [Use the Kimi API for Tool Calls (`tool_calls`)](/docs/guide/use-kimi-api-to-complete-tool-calls)
  </Accordion>

  <Accordion title="The Kimi model cannot answer today's date">
    The Kimi model cannot access highly time-sensitive information such as the current date. However, you can provide this information in the system prompt. For example:

    <Note>
      The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
    </Note>

    <Tabs>
      <Tab title="python">
        ```python theme={null}
        import os
        from datetime import datetime
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ['MOONSHOT_API_KEY'],
            base_url="https://api.moonshot.ai/v1",
        )

        # Generate the current date with datetime and add it to the system prompt.
        system_prompt = f"""
        You are Kimi, and today's date is {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        """

        completion = client.chat.completions.create(
            model="kimi-k3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "What is today's date?"},
            ],
        )

        print(completion.choices[0].message.content)  # Output: Today's date is July 31, 2024.
        ```
      </Tab>

      <Tab title="node.js">
        ```js theme={null}
        const OpenAI = require('openai')

        client = new OpenAI({
            apiKey: process.env.MOONSHOT_API_KEY,
            baseURL: "https://api.moonshot.ai/v1",
        })

        // Generate the current date with Date and add it to the system prompt.
        system_prompt = `You are Kimi, and today's date is ${new Date().toString()}`

        async function main() {
            completion = await client.chat.completions.create({
                model: "kimi-k3",
                messages: [
                    {role: "system", content: system_prompt},
                    {role: "user", content: "What is today's date?"},
                ],
            })

            console.log(completion.choices[0].message.content)  // Output: Today's date is July 31, 2024.
        }

        main()
        ```
      </Tab>
    </Tabs>
  </Accordion>

  <Accordion title="How do I handle errors without using an SDK?">
    In some cases, you may need to integrate with the Kimi API directly instead of using the OpenAI SDK. When integrating directly, decide the next processing step based on the status returned by the API. In general, HTTP status code 200 indicates success, while 4xx and 5xx status codes indicate failure. We return error information in JSON format. See the following code snippets for example handling logic:

    <Tabs>
      <Tab title="python">
        ```python theme={null}
        import os
        import httpx

        header = {
            "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
        }

        messages = [
            {"role": "system", "content": "You are Kimi"},
            {"role": "user", "content": "Hello."},
        ]

        r = httpx.post("https://api.moonshot.ai/v1/chat/completions",
                       headers=header,
                       json={
                           "model": "kimi-k3",  # A correct model enters the status_code == 200 branch below.
                           # "model": "moonshot-v1-129k",  # An incorrect model name enters the else branch below.
                           "messages": messages,
                       })

        if r.status_code == 200:  # Normal handling for a request with a correct model.
            completion = r.json()
            print(completion["choices"][0]["message"]["content"])
        else:  # Error handling for a request with an incorrect model name.
            # For demonstration, we only print the error here.
            # In production logic, you may want to log, interrupt the request, retry, and so on.
            error = r.json()
            print(f"error: status={r.status_code}, type='{error['error']['type']}', message='{error['error']['message']}'")
        ```
      </Tab>

      <Tab title="node.js">
        ```js theme={null}
        const axios = require('axios');

        header = {
            "Authorization": `Bearer ${process.env.MOONSHOT_API_KEY}`,
        }

        messages = [
            {"role": "system", "content": "You are Kimi"},
            {"role": "user", "content": "Hello."},
        ]

        async function main() {
            r = await axios.post("https://api.moonshot.ai/v1/chat/completions",
                {
                    "model": "kimi-k3",  // A correct model enters the success branch below.
                    //"model": "moonshot-v1-129k",  // An incorrect model name enters the error branch.
                    "messages": messages,
                },
                {
                    headers: header,
                    validateStatus: function (status) {
                        return status == 200; // Resolve only when the status code is 200.
                    }
                },
             ).catch(function (error) {
                console.log(`error: ${error.message}`)
             })

            if (r) {  // Normal handling for a request with a correct model.
                console.log(r.data.choices[0].message.content)
            }
        }

        main()
        ```
      </Tab>
    </Tabs>

    Our error messages follow this format:

    ```json theme={null}
    {
    	"error": {
    		"type": "error_type",
    		"message": "error_message"
    	}
    }
    ```

    For the complete error reference, see:

    [Error Reference](/docs/api/errors)
  </Accordion>

  <Accordion title="Why do some requests respond quickly while others respond slowly when the prompts are similar?">
    If some requests with similar prompts respond quickly, for example in 3 seconds, while others respond slowly, for example in 20 seconds, this is usually because the Kimi model generated different numbers of tokens. In general, the number of generated tokens is proportional to the total response time of the Kimi API. The more tokens generated, the longer the full response takes.

    Note that the number of generated tokens only affects the response time for the complete request, meaning the time until the final token is generated. You can set `stream=True` and observe the time to first token, abbreviated as TTFT. In normal cases, when prompt lengths are similar, TTFT should not vary significantly.
  </Accordion>

  <Accordion title="I set `max_completion_tokens=2000` to make Kimi output 2,000 characters, but the output is shorter">
    > Note: `max_tokens` is deprecated. Please use `max_completion_tokens` instead. The two fields have the same meaning.

    The `max_completion_tokens` parameter means: **when calling `/v1/chat/completions`, it specifies the maximum number of tokens the model is allowed to generate. Once the number of generated tokens exceeds `max_completion_tokens`, the model stops generating the next token**.

    `max_completion_tokens` is used to:

    1. Help the caller determine which model to use. For example, when `prompt_tokens + max_completion_tokens <= 256 * 1024`, you can choose `kimi-k2.6`.
    2. Prevent the Kimi model from generating too much unexpected content in unusual cases, which could cause extra cost. For example, the model might repeatedly output whitespace.

    `max_completion_tokens` does not tell the Kimi model how many tokens to output. In other words, **`max_completion_tokens` is not used as part of the prompt input to the Kimi model**. If you want the model to output a specific number of characters, use these general approaches:

    * For outputs under 1,000 characters:
      1. Clearly specify the desired character count in the prompt.
      2. Manually or programmatically check whether the output length meets expectations. If not, tell the model in a second round that the output is too long or too short, then ask it to generate a new version.
    * For outputs over 1,000 characters or much longer:
      1. Split the expected output by structure or chapter, create a template, and use placeholders to mark where the model should fill in content.
      2. Ask the Kimi model to fill each placeholder one by one, then assemble the complete long-form text.
  </Accordion>

  <Accordion title="I only made one request in a minute, but triggered `Your account reached max request`">
    The OpenAI SDK usually includes a retry mechanism:

    > Certain errors are automatically retried 2 times by default, with a short exponential backoff. Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors are all retried by default.

    This retry mechanism retries 2 times by default when an error occurs, for a total of 3 requests. In unstable network conditions or other cases that may cause request errors, using the OpenAI SDK can expand one request into 2 or 3 requests. All of these requests count toward your RPM quota.

    *Note: For users on a `tier0` account using the OpenAI SDK, one failed request may consume the entire RPM quota because of the default retry mechanism.*
  </Accordion>

  <Accordion title="I used `base64` encoding for my text content to make transmission easier">
    Please do not do this. Encoding files with `base64` can cause massive token consumption. If your file type is supported by our `/v1/files` API, upload the file through the files API and extract its content there.

    For binary files or files in other encoded formats, the Kimi model currently cannot parse the content. Do not add this content to the context.
  </Accordion>

  <Accordion title="Why can't I use a key from another Kimi platform on platform.kimi.ai?">
    Kimi Open Platform provides separate regional platforms. For users outside mainland China, use platform.kimi.ai. Accounts and keys from different regional platforms are independent and cannot be mixed.

    If you use the wrong key for a platform, you will receive a `401 invalid_authentication_error`. If you receive a 401 error, first check whether you are using a key from the wrong platform.

    * International open platform `base_url`: [https://api.moonshot.ai/v1](https://api.moonshot.ai/v1)
  </Accordion>
</AccordionGroup>
