 
 Prompt caching with Azure OpenAI in Microsoft Foundry Models - Microsoft Foundry | Microsoft Learn 
 Skip to main content
 Skip to Ask Learn chat experience
 This browser is no longer supported. 
 Upgrade to Microsoft Edge to take advantage of the latest features, security updates, and technical support.
 Download Microsoft Edge
 More info about Internet Explorer and Microsoft Edge
 Table of contents 
 Exit editor mode 
 Ask Learn 
 Ask Learn 
 Reading mode 
 Table of contents 
 Read in English 
 Add 
 Add to Plans 
 Edit 
 Copy Markdown 
 Print 
 Note 
 Access to this page requires authorization. You can try signing in or changing directories .
 Access to this page requires authorization. You can try changing directories .
 Prompt caching 
 Feedback 
 Summarize this article for me
 In this article
 Prompt caching reduces overall request latency and cost for longer prompts that have identical content at the beginning of the prompt. In this context, "prompt" refers to the input you send to the model as part of your chat completions or response creation requests. Rather than reprocessing the same input tokens over and over again, the service retains a temporary cache of processed input token computations to improve overall performance. Prompt caching has no impact on the output content returned in the model response beyond a reduction in latency and cost. 
 For supported models, cache reads are billed at a discount on input token pricing for Standard deployment types and up to 100% discount on input tokens for Provisioned deployment types. Prompt cache pricing is the same for both retention policies. 
 Important 
 Models before the GPT-5.6 family don't charge extra to write to the cache. On GPT-5.6 models and later model families, cache writes can incur charges in addition to discounted cache reads. To keep costs predictable, structure your prompts so that reused content stays identical across requests, which favors cache reads over cache writes. For current rates, see the Azure OpenAI pricing page . 
 Improve cache hit rates with a prompt cache key 
 On GPT-5.6 models and later model families, set the prompt_cache_key parameter and reuse the same key for requests that share long, common prompt prefixes. This parameter improves cache matching for related requests. You don't need a specific API version to use prompt_cache_key . For new integrations, use the v1 API . 
 If requests for the same prefix and prompt_cache_key combination exceed approximately 15 requests per minute, some requests might miss the cache. For higher-volume workloads, distribute requests across multiple keys while keeping a stable mapping between each key and its shared prompt prefixes. 
 Configure prompt cache breakpoints 
 On GPT-5.6 models and later model families, use explicit cache breakpoints to mark the end of a reusable prompt prefix. Both the Responses API and Chat Completions API support breakpoints. Azure OpenAI uses the same request structures as the OpenAI APIs, but set model to your Azure model deployment name. Content after the breakpoint can change without invalidating the cached prefix. 
 Standard pay-as-you-go deployments support prompt cache breakpoints. Provisioned Throughput managed (PTU-M) deployments don't support prompt cache breakpoints. 
 Set the request-wide cache policy by using prompt_cache_options.mode : 
 Mode 
 Behavior 
 implicit 
 The default. Azure OpenAI places a breakpoint on the latest message and also uses any explicit breakpoints that you provide. 
 explicit 
 Azure OpenAI uses only explicit breakpoints for cache reads and writes. If the request contains no explicit breakpoints, it doesn't use prompt caching or incur cache-write charges. 
 Set prompt_cache_options.ttl to 30m to configure the minimum cache lifetime for all breakpoints in the request. The 30m value is the default and the only supported value. This setting doesn't select the in-memory or extended retention policy. 
 Add prompt_cache_breakpoint: { "mode": "explicit" } to a supported prompt content block. The breakpoint includes the block and all prompt content before it in the reusable prefix. 
 The Responses API supports breakpoints on input_text , input_image , and input_file blocks. 
 The Chat Completions API supports breakpoints on text , image_url , input_audio , and file blocks. 
 Breakpoint limits 
 Each request can create up to four new cache writes. 
 In implicit mode, the breakpoint on the latest message uses one write slot, so the request can write up to the latest three explicit breakpoints. 
 In explicit mode, the request can write up to the latest four explicit breakpoints. 
 Breakpoints from earlier conversation turns are read-only. They can match the cache, but the request doesn't write them again. 
 For cache reads, Azure OpenAI considers up to the latest 50 breakpoints in the conversation. 
 In the following examples, the rendered prefix through the explicit breakpoint must contain at least 1,024 tokens to be cacheable. 
 The following Responses API request uses the default implicit mode and adds an explicit breakpoint after a stable reference file: 
 {
 "model": "&lt;your-gpt-5.6-deployment-name&gt;",
 "prompt_cache_key": "tenant:contoso:product-manual-v2",
 "input": [
 {
 "type": "message",
 "role": "user",
 "content": [
 {
 "type": "input_file",
 "file_id": "&lt;product-manual-file-id&gt;",
 "prompt_cache_breakpoint": { "mode": "explicit" }
 },
 {
 "type": "input_text",
 "text": "Summarize the troubleshooting procedures."
 }
 ]
 }
 ]
}
 The following Chat Completions API request uses explicit mode and marks the end of a reusable system message: 
 {
 "model": "&lt;your-gpt-5.6-deployment-name&gt;",
 "prompt_cache_key": "tenant:contoso:support-policy-v2",
 "prompt_cache_options": { "mode": "explicit", "ttl": "30m" },
 "messages": [
 {
 "role": "system",
 "content": [{
 "type": "text",
 "text": "&lt;at least 1,024 tokens of reusable instructions&gt;",
 "prompt_cache_breakpoint": { "mode": "explicit" }
 }]
 },
 {
 "role": "user",
 "content": "&lt;variable user input&gt;"
 }
 ]
}
 Note 
 Models before the GPT-5.6 family don't support prompt_cache_options or prompt_cache_breakpoint . Requests that include these parameters return a 400 error. Continue to use automatic prompt caching with these models. 
 Prompt cache retention 
 Prompt caching has two controls with different semantics: 
 On GPT-5.6 models and later model families, prompt_cache_options.ttl sets a minimum cache lifetime. It doesn't select a storage policy or maximum retention period. 
 For earlier models, prompt_cache_retention selects a maximum-retention policy. On GPT-5.6 models and later model families, this field doesn't apply and is deprecated. 
 On GPT-5.6 models and later model families, use prompt_cache_options.ttl to set the minimum lifetime of all breakpoints written by the request. The only supported value is 30m , which is also the default. A cached prefix remains eligible for reuse for at least 30 minutes, but the service might retain it longer. 
 For models before the GPT-5.6 family, set prompt_cache_retention on your Responses or Chat Completions request. Prompt caching can use either in-memory or extended retention policies. When available, extended prompt caching aims to retain the cache for longer, so that subsequent requests are more likely to match the cache. Prompt cache pricing is the same for both policies. 
 In-memory prompt cache retention 
 The system typically clears caches within 5 to 10 minutes of inactivity and always removes them within one hour of the cache's last use. The system doesn't share prompt caches between Azure subscriptions. 
 All Azure OpenAI models GPT-4o or newer support in-memory prompt cache retention. It applies to models that have chat-completion, completion, responses, or real-time operations. For models that don't have these operations, this feature isn't available. 
 Extended prompt cache retention 
 Extended prompt cache retention keeps cached prefixes active for longer, up to a maximum of 24 hours. Extended prompt caching works by offloading the key/value tensors to GPU-local storage when memory is full, which significantly increases the storage capacity available for caching. 
 Extended prompt cache retention is available for the following models: 
 gpt-5.5 
 gpt-5.4 
 gpt-5.3-codex 
 gpt-5.2 
 gpt-5.1-codex-max 
 gpt-5.1 
 gpt-5.1-codex 
 gpt-5.1-codex-mini 
 gpt-5.1-chat 
 gpt-5 
 gpt-5-codex 
 gpt-4.1 
 Configure per request 
 For gpt-5.4 and older models, if you don't specify a retention policy, the default is in_memory . Allowed values are in_memory and 24h . For gpt-5.5 , extended retention is enabled by default. 
 {
 "model": "&lt;your-gpt-5.4-deployment-name&gt;",
 "input": "Your prompt goes here...",
 "prompt_cache_retention": "24h"
}
 Getting started 
 To take advantage of prompt caching, a request must meet both of these requirements: 
 A minimum of 1,024 tokens in length. 
 The first 1,024 tokens in the prompt must be identical. 
 When a match is found between the token computations in a prompt and the current content of the prompt cache, it's referred to as a cache hit. Cache hits show up as cached_tokens under prompt_tokens_details in the chat completions response. 
 On GPT-5.6 models and later model families, Standard pay-as-you-go deployments report cache reads in cached_tokens and cache writes in cache_write_tokens . The following excerpt shows these fields in a Chat Completions response. JSON property order isn't significant and might vary. 
 {
 "usage": {
 "prompt_tokens": 1566,
 "completion_tokens": 1518,
 "total_tokens": 3084,
 "prompt_tokens_details": {
 "audio_tokens": null,
 "cached_tokens": 1408,
 "cache_write_tokens": 0
 },
 "completion_tokens_details": {
 "audio_tokens": null,
 "reasoning_tokens": 576
 }
 }
}
 On GPT-5.5 and earlier models, cache hits after the first 1,024 tokens occur in 128-token increments. This rounding doesn't apply to GPT-5.6 models and later model families. 
 A single character difference in the first 1,024 tokens results in a cache miss, which is characterized by a cached_tokens value of 0. Prompt caching is enabled by default for supported models. 
 Best practices 
 Place stable or repeated content at the beginning of the prompt and dynamic content at the end. Keep conversation context append-only. 
 Reuse a consistent prompt_cache_key for requests that share a prefix. For high-volume workloads, partition traffic across keys while keeping a stable mapping between each key and its prefixes. 
 On Standard pay-as-you-go deployments with GPT-5.6 models and later model families, place explicit breakpoints after stable content. Use explicit mode when you want only the breakpoints you provide to be eligible for cache reads and writes. 
 Monitor cache reads with cached_tokens . On Standard pay-as-you-go deployments with GPT-5.6 models and later model families, also monitor cache writes with cache_write_tokens and compare write volume with later cache reads. 
 Maintain a steady stream of requests with identical prefixes to improve cache reuse. 
 Frequently asked questions 
 The following answers clarify supported cache content, costs, deployment types, and data residency. 
 What is cached? 
 Feature support for o1-series models varies by model. For more information, see the dedicated reasoning models guide . 
 Prompt caching supports: 
 Caching supported 
 Description 
 Messages 
 The complete messages array: system, developer, user, and assistant content 
 Images 
 Images included in user messages, both as links or as base64-encoded data. The detail parameter must be set the same across requests. 
 Tool use 
 Both the messages array and tool definitions. 
 Structured outputs 
 Structured output schema is appended as a prefix to the system message. 
 To improve the likelihood of cache hits, structure your requests so that repetitive content occurs at the beginning of the messages array. 
 Can I disable prompt caching? 
 On Standard pay-as-you-go deployments with GPT-5.6 models and later model families, set prompt_cache_options.mode to explicit and don't add any explicit breakpoints. The request doesn't use prompt caching or incur cache-write charges. Earlier models and PTU-M deployments don't support this option; prompt caching remains enabled by default. 
 Do I pay extra to write to the cache? 
 On models before the GPT-5.6 family, there's no extra charge to write to the cache. On GPT-5.6 models and later model families, cache writes can incur charges in addition to discounted cache reads. To see current rates, go to the Azure OpenAI pricing page . 
 Do prompt cache breakpoints work with PTU-M? 
 On GPT-5.6 models and later model families, Standard pay-as-you-go deployments support prompt cache breakpoints and expose cache_write_tokens . Provisioned Throughput managed (PTU-M) deployments continue to support prompt caching, but they don't support prompt cache breakpoints or expose cache_write_tokens . 
 Does prompt caching work with data residency? 
 In-memory prompt caching is compatible with all data residency regions. Extended prompt caching temporarily stores data on GPU machines. Data stays within the data zone boundary for Data Zone Standard and Data Zone Provisioned deployment types, and within the regional boundary for Regional Standard and Regional Provisioned deployment types. 
 Related content 
 Azure OpenAI Responses API reference 
 Azure OpenAI Chat Completions API reference 
 Feedback 
 Was this page helpful?
 Yes 
 No 
 No 
 Need help with this topic?
 Want to try using Ask Learn to clarify or guide you through this topic?
 Ask Learn 
 Ask Learn 
 Suggest a fix? 
 Additional resources
 Last updated on 
 2026-08-11
 In this article 
 Was this page helpful?
 Need help with this topic?
 Want to try using Ask Learn to clarify or guide you through this topic?
 Ask Learn 
 Ask Learn 
 Suggest a fix? 
 en-us 
 Your Privacy Choices 
 Theme 
 Light 
 Dark 
 High contrast 
 AI Disclaimer 
 Previous Versions 
 Blog 
 Contribute 
 Privacy 
 Consumer Health Privacy 
 Terms of Use 
 Trademarks 
 &copy; Microsoft 2026 
 