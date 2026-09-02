 
 Prompt caching for faster model inference - Amazon Bedrock 
 View a markdown version of this page Prompt caching for faster model inference - Amazon Bedrock Documentation Amazon Bedrock User Guide Types of prompt caching Supported models, Regions, and explicit caching limits Prompt caching for models from Anthropic Prompt caching for models from OpenAI Getting started Prompt caching for faster model inference Prompt caching is an optional feature that you can use with supported models on Amazon Bedrock to
 reduce inference response latency and input token costs. Amazon Bedrock supports two types of prompt
 caching: Implicit Prompt Caching and
 Explicit Prompt Caching . Support for each
 type varies by model and API. Prompt caching can help when you have workloads with long and repeated contexts that are 
 frequently reused for multiple queries. For example, if you have a chatbot where users can 
 upload documents and ask questions about them, it can be time consuming for the model to 
 process the document every time the user provides input. With prompt caching, you can cache 
 the document so that future queries containing the document don't need to reprocess it. 
 Types of prompt caching 
 The two types differ in how reusable prompt content is selected: 
 Type 
 How it works 
 Request configuration 
 Implicit Prompt
 Caching 
 Amazon Bedrock and the model automatically attempt to reuse eligible prompt
 prefixes. 
 No cache controls or breakpoints are required in your request. 
 Explicit Prompt
 Caching 
 You identify reusable prompt prefixes by adding model-specific cache
 controls or breakpoints. 
 Your request must include the cache controls supported by the model
 and API. 
 Implicit Prompt Caching 
 Implicit Prompt Caching automatically attempts to reuse eligible prompt prefixes
 without requiring cache controls in your request. Keep static content at the
 beginning of your prompt and dynamic content at the end to increase the likelihood
 of an exact prefix match. 
 Implicit Prompt Caching is best effort. Repeating an identical prompt doesn't
 guarantee a cache hit, and cache-hit rates can vary. 
 Explicit Prompt Caching 
 Explicit Prompt Caching lets you identify reusable prompt prefixes using
 model-specific cache controls or cache
 checkpoints . Cache checkpoints are markers that define the
 contiguous subsection of your prompt that you want to cache. Prompt prefixes should
 remain static between requests. Changes to a prompt prefix in subsequent requests
 result in cache misses. 
 Cache checkpoints have a minimum and maximum number of tokens, depending on the
 model. You can only create a cache checkpoint if your total prompt prefix meets the
 minimum number of tokens. For example, Claude Opus 5 requires at
 least 512 tokens per cache checkpoint, Claude Sonnet 5 requires at
 least 1,024 tokens per cache checkpoint, and Claude Haiku 4.5 requires at least
 4,096 tokens per cache checkpoint. For a model with a 1,024-token minimum, your
 first cache checkpoint can be defined after 1,024 tokens and your second cache
 checkpoint can be defined after 2,048 tokens. If you add a cache checkpoint before
 meeting the minimum number of tokens, your inference still succeeds, but your
 prefix isn't cached. 
 The cache has a Time To Live (TTL), which resets with each successful cache hit.
 During this period, the context in the cache is preserved. If no cache hits occur
 within the TTL window, your cache expires. Many models support a 5-minute TTL.
 Check the model card for your model to see the exact TTL conditions. 
 Explicit Prompt Caching provides control over which prompt content is eligible
 for caching. It doesn't guarantee that an eligible request results in a cache
 hit. 
 Billing for cached tokens 
 For both Implicit Prompt Caching and Explicit Prompt Caching, tokens successfully
 read from cache are reported as cached tokens and billed at the model's cache-read
 rate. Tokens that aren't read from cache are billed at the standard input token
 rate. Depending on the model, tokens written to cache can be billed at a rate that
 is higher than the standard input token rate. For more information, see the
 Amazon Bedrock pricing page . 
 Important Support for prompt caching doesn't guarantee a cache hit for any request. Check
 the cache usage fields in the model response to determine whether tokens were read
 from or written to cache. 
 You can use prompt caching when you run inference in Amazon Bedrock with supported models.
 Availability of each prompt caching type varies by model and API. Prompt caching is
 available through the following Amazon Bedrock features: 
 Converse and ConverseStream APIs 
 You can carry on a conversation with a supported model. For Explicit
 Prompt Caching, specify cache checkpoints in your prompts. 
 InvokeModel and InvokeModelWithResponseStream
 APIs 
 You can submit single-prompt requests to supported models. For Explicit
 Prompt Caching, enable prompt caching and specify your cache
 checkpoints. 
 Prompt Caching with Cross-region Inference 
 Prompt caching can be used in conjunction with cross region inference. Cross-region 
 inference automatically selects the optimal AWS Region within your geography to 
 serve your inference request, thereby maximizing available resources and model 
 availability. At times of high demand, these optimizations may lead to increased cache writes. 
 Amazon Bedrock Prompt management 
 When you create or modify a prompt, you can
 choose to enable prompt caching. Depending on the model, you can cache
 system prompts, system instructions, and messages (user and assistant). You
 can also choose to disable prompt caching. 
 Note Prompt caching is only supported for on-demand inference endpoints. It is not supported with the batch inference API. 
 For models that support Explicit Prompt Caching, the APIs provide granular control
 over the prompt cache. You can set individual cache checkpoints within your prompts
 and add checkpoints up to the maximum allowed for the model. For more information, see
 Supported models, Regions, and explicit caching limits . 
 Supported models, Regions, and explicit caching limits 
 Prompt caching support varies by model and API. Model cards identify whether a model
 supports Implicit Prompt Caching, Explicit Prompt Caching, or both. Prompt caching is
 available in all AWS Regions where the supported models are available. To check model
 availability by Region, see Regional availability by models . 
 The following table lists models that support Explicit Prompt Caching, along with
 their token minimums, maximum number of cache checkpoints, and fields that allow cache
 checkpoints. 
 To see which prompt caching types a model supports, refer to
 Models at a glance , and then choose the model that
 you're interested in. 
 Model name 
 Model ID 
 Release Type 
 Minimum number of tokens per cache checkpoint 
 Maximum number of cache checkpoints per request 
 Supported TTL 
 Fields that accept prompt cache checkpoints 
 Claude Fable 5.1 
 anthropic.claude-fable-5-1 
 Generally Available 
 512 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Mythos 5.1 
 anthropic.claude-mythos-5-1 
 Gated 
 512 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Fable 5 
 anthropic.claude-fable-5 
 Generally Available 
 512 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Mythos 5 
 anthropic.claude-mythos-5 
 Gated 
 512 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Mythos Preview 
 anthropic.claude-mythos-preview 
 Gated 
 4,096 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Opus 5 
 anthropic.claude-opus-5 
 Generally Available 
 512 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Opus 4.8 
 anthropic.claude-opus-4-8 
 Generally Available 
 1,024 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Opus 4.7 
 anthropic.claude-opus-4-7 
 Generally Available 
 4,096 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Opus 4.6 
 anthropic.claude-opus-4-6-v1 
 Generally Available 
 4,096 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Opus 4.5 
 anthropic.claude-opus-4-5-20251101-v1:0 
 Generally Available 
 4,096 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Sonnet 5 
 anthropic.claude-sonnet-5 
 Generally Available 
 1,024 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Sonnet 4.6 
 anthropic.claude-sonnet-4-6 
 Generally Available 
 1,024 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude Sonnet 4.5 
 anthropic.claude-sonnet-4-5-20250929-v1:0 
 Generally Available 
 1,024 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 Claude 3.7 Sonnet 
 anthropic.claude-3-7-sonnet-20250219-v1:0 
 Generally Available 
 1,024 
 4 
 5 minutes 
 `system`, `messages`, and `tools` 
 Claude 3.5 Sonnet v2 
 anthropic.claude-3-5-sonnet-20241022-v2:0 
 Preview 
 1,024 
 4 
 5 minutes 
 `system`, `messages`, and `tools` 
 Claude Haiku 4.5 
 anthropic.claude-haiku-4-5-20251001-v1:0 
 Generally Available 
 4,096 
 4 
 5 minutes, 1 hour 
 `system`, `messages`, and `tools` 
 GPT-5.6 Sol 
 openai.gpt-5.6-sol 
 Generally Available 
 1,024 
 4 
 30 minutes 
 prompt_cache_breakpoint on input_text , input_image , and input_file blocks (Responses API) 
 GPT-5.6 Terra 
 openai.gpt-5.6-terra 
 Generally Available 
 1,024 
 4 
 30 minutes 
 prompt_cache_breakpoint on input_text , input_image , and input_file blocks (Responses API) 
 GPT-5.6 Luna 
 openai.gpt-5.6-luna 
 Generally Available 
 1,024 
 4 
 30 minutes 
 prompt_cache_breakpoint on input_text , input_image , and input_file blocks (Responses API) 
 To use the 1-hour TTL option with supported models (Claude Fable 5, Claude Opus 5,
 Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Opus 4.5,
 Claude Sonnet 5, Claude Sonnet 4.6, Claude Sonnet 4.5, and Claude Haiku 4.5),
 specify the ttl field in your cache checkpoint. In the Converse API, add "ttl": "1h" 
 to your cachePoint object. In the InvokeModel API for Claude models, add "ttl": "1h" 
 to your cache_control object. If no ttl value is provided, the default 5-minute
 caching behavior applies. The 1-hour TTL is useful for longer-running sessions or batch processing scenarios
 where you want to maintain the cache across extended periods. 
 Amazon Nova offers Implicit Prompt Caching for all text prompts, including
 User and System messages. This mechanism can provide latency
 benefits when prompts begin with repetitive parts, without explicit configuration.
 Amazon Nova models shown as supporting Explicit Prompt Caching in their model cards also let
 you specify cache checkpoints for more control over cache eligibility. 
 Prompt caching for models from Anthropic 
 Anthropic models that support prompt caching on Amazon Bedrock support both Implicit Prompt
 Caching and Explicit Prompt Caching. Implicit Prompt Caching automatically attempts to
 reuse eligible prompt prefixes without requiring cache controls in your
 request. 
 For Explicit Prompt Caching, Amazon Bedrock offers a simplified approach to cache management
 that reduces the complexity of manually placing cache checkpoints. Instead of
 requiring you to specify exact cache checkpoint locations, you can use automatic cache
 management with a single breakpoint at the end of your static content. 
 When you enable simplified cache management, the system automatically checks for cache hits at previous content block boundaries, looking back up to approximately 20 
 content blocks from your specified breakpoint. This allows the model to find the longest matching prefix from your cache without requiring you to predict the optimal 
 checkpoint locations. To use this, place a single cache checkpoint at the end of your static content, before any dynamic or variable content. The system will 
 automatically find the best cache match. 
 For more granular control, you can still use multiple cache checkpoints (up to 4 for Claude models) to specify exact cache boundaries. You should use multipled
 cache checkpoints if you are caching sections that change at different frequencies or want more control over exactly what gets cached. 
 Important The automatic prefix checking only looks back approximately 20 content blocks from your cache checkpoint. If your static content extends beyond this range, consider 
 using multiple cache checkpoints or restructuring your prompt to place the most frequently reused content within this range. 
 Best practices for using cache management in Anthropic Models 
 If you have prompts that are used at a regular cadence (i.e., system prompts that are used more frequently than every 5 minutes), continue to use the 5-minute cache,
 since this will continue to be refreshed at no additional charge. 
 The 1-hour cache is best used in the following scenarios: 
 When you have prompts that are likely used less frequently than 5 minutes, but more frequently than every hour. For example, when an agentic side-agent will
 take longer than 5 minutes, or when storing a long chat conversation with a user and you generally expect that user may not respond in the next 5 minutes. 
 When latency is important and your follow-up prompts may be sent beyond 5 minutes. 
 When you want to improve your rate limit use, since cache hits are not deducted against your rate limit. 
 You can use both 1-hour and 5-minute cache controls in the same request, but with an important constraint: Cache entries with longer TTL must appear before
 shorter TTLs (i.e., a 1-hour cache entry must appear before any 5-minute cache entries). 
 Prompt caching for models from OpenAI 
 OpenAI models on Amazon Bedrock support Implicit Prompt Caching through the Responses API.
 GPT-5.6 models also support Explicit Prompt Caching. The Responses API is available on
 both the bedrock-runtime and bedrock-mantle endpoints. 
 GPT-5.6 models 
 GPT-5.6 Sol ( openai.gpt-5.6-sol ), Terra
 ( openai.gpt-5.6-terra ), and Luna ( openai.gpt-5.6-luna )
 support both Implicit Prompt Caching and Explicit Prompt Caching. Explicit prompt
 cache breakpoints give you precise control over which portions of your prompt are
 eligible for caching. This is especially valuable for agentic workflows where
 system instructions, tool definitions, and reference files repeat across many calls
 while only the latest input changes. 
 Key characteristics: 
 Explicit cache breakpoints — Mark
 the exact end of a reusable prompt prefix by adding
 "prompt_cache_breakpoint": { "mode": "explicit"} to a supported
 content block. Cache modes — Set
 prompt_cache_options.mode to control breakpoint behavior: 
 implicit (default) — Places an automatic
 breakpoint on the latest message and also uses any explicit breakpoints
 you provide. explicit — Disables the automatic breakpoint.
 Only explicit breakpoints are used for cache reads and writes. If no
 explicit breakpoints exist, the request does not use prompt caching or
 incur cache-write charges. Minimum prefix length — 1,024
 tokens per breakpoint. 30-minute minimum TTL — Cached
 prefixes remain available for reuse for at least 30 minutes, long enough to
 cover the burst of calls a single agent run generates. The TTL is set via
 prompt_cache_options.ttl and defaults to
 30m . Cache write billing — Tokens
 written to cache are billed at 1.25× the uncached input token rate. Cache
 reads are billed at a 90% discount compared to uncached input
 tokens. Cached tokens do not count toward rate
 limits — Cached input tokens read through prompt caching do not
 count against the input-tokens-per-minute quota. 
 Understanding the response 
 The usage object in the response includes two cache-specific fields: 
 cached_tokens — Number of input tokens read from
 cache (billed at the cache-read discount rate). cache_write_tokens — Number of input tokens
 written to cache (billed at 1.25× the uncached input token
 rate). 
 When cached_tokens is greater than zero and
 cache_write_tokens is zero, your request fully matched an existing
 cache entry — no new writes occurred, and you received the maximum cost
 savings. 
 Best practices for using cache management in GPT 5.6 models 
 Place breakpoints after stable
 content — System instructions, tool definitions, and reference
 documents that don't change between calls should appear before the
 breakpoint. Content after the breakpoint can change freely without
 invalidating the cached prefix. Use explicit mode for
 agentic loops — When you want full control over what gets
 cached and want to avoid automatic breakpoints consuming write
 slots. Monitor
 cache_write_tokens — Compare cache-write volume
 against subsequent cache reads to understand net cost impact and adjust
 breakpoint placement accordingly. 
 GPT-5.5 and earlier models 
 For OpenAI models prior to GPT-5.6 (such as openai.gpt-5.5 and
 openai.gpt-5.4 ), Implicit Prompt Caching is automatic. You don't need
 to add any special parameters. The system automatically attempts to cache eligible
 prompt prefixes of 1,024 tokens or longer. Cache writes have no additional fee on
 these models. 
 Key characteristics: 
 Implicit Prompt Caching — No code
 changes are required. The system attempts to cache prefixes automatically based
 on exact prefix matching. Minimum prefix length — 1,024
 tokens. No cache write fee — Only cache
 reads are billed at a discounted rate. Cached tokens do not count toward rate
 limits — Cached input tokens read through prompt caching do not
 count against the input-tokens-per-minute quota. 
 Best practices for using cache management in GPT-5.5 and earlier models 
 Place static content (system prompts, tool definitions, reference
 documents) at the beginning of your prompt. Put variable content (user-specific input) at the end. Maintain a steady stream of requests with identical prefixes to
 minimize cache evictions. 
 Getting started 
 The following sections show you a brief overview of how to use the prompt caching
 feature for each method of interacting with models through Amazon Bedrock. 
 The Converse 
 API provides advanced and flexible options for implementing prompt caching
 in multi-turn conversations. For more information about the prompt requirements for each model, see
 the preceding section Supported models, Regions, and explicit caching limits . Example request The following examples show a cache checkpoint set in the
 messages , system , or tools 
 fields of a request to the Converse API. You can place checkpoints in any of these
 locations for a given request. For example, if sending a request to the
 Claude 3.5 Sonnet v2 model, you could place two cache checkpoints in
 messages , one cache checkpoint in system ,
 and one in tools . For more detailed information and examples of
 structuring and sending Converse API requests, see
 Inference using Converse API . Important Cache checkpoints are processed in this order: tools →
 system → messages . The minimum cache size is evaluated
 against the cumulative tokens across all three sections combined, not each section
 individually. Because the sections are chained, changing content in an earlier section
 invalidates the cache for later sections (for example, modifying tools 
 invalidates the system and messages caches). For best cache
 hit rates, place stable content ( tools , system ) before variable
 content ( messages ), and place cache checkpoints after the stable content. Specify the desired ttl value as below, when ttl value not specified the default behavior of
 5 minutes caching applies. "cachePoint" : { 
 "type": "default",
 "ttl" : "5m | 1h"
}
 messages checkpoints 
 In this example, the first image field provides an image to the model,
 and the second text field asks the model to analyze the image.
 As long as the number of tokens preceding the cachePoint 
 in the content object meets the minimum token count for the model,
 a cache checkpoint is created. 
 ...
"messages": [
 { 
 "role": "user",
 "content": [
 { 
 "image": { 
 "bytes": "asfb14tscve..."
 }
 },
 { 
 "text": "What's in this image?"
 },
 { 
 "cachePoint": { 
 "type": "default"
 }
 }
 ]
 }
]
... 
 system checkpoints 
 In this example, you provide your system prompt in the
 text field. Additionally, you can add a
 cachePoint field to cache the system prompt. 
 ...
 "system": [ 
 { 
 "text": "You are an app that creates play lists for a radio station that plays rock and pop music. Only return song names and the artist. "
 },
 { 
 "cachePoint": { 
 "type": "default"
 }
 }
 ],
... 
 tools checkpoints 
 In this example, you provide your tool definition in the
 toolSpec field. (Alternatively, you can call a tool that
 you've previously defined. For more information, see Use a tool to complete an Amazon Bedrock model response .) Afterward, you can add
 a cachePoint field to cache the tool. 
 ...
toolConfig= { 
 "tools": [
 { 
 "toolSpec": { 
 "name": "top_song",
 "description": "Get the most popular song played on a radio station.",
 "inputSchema": { 
 "json": { 
 "type": "object",
 "properties": { 
 "sign": { 
 "type": "string",
 "description": "The call sign for the radio station for which you want the most popular song. Example calls signs are WZPZ and WKRP."
 }
 },
 "required": [
 "sign"
 ]
 }
 }
 }
 },
 { 
 "cachePoint": { 
 "type": "default"
 }
 }
 ]
}
... 
 The model response from the Converse API includes three new fields that are specific to prompt
 caching. The cacheReadInputTokens and
 cacheWriteInputTokens values tell you how many tokens were
 read from the cache and how many tokens were written to the cache because of
 your previous request. The cacheDetails values tell you the ttl
 used for the number of token written to cache. These are values that you're charged for by Amazon Bedrock,
 at a rate that's lower than the cost of full model inference. Important When prompt caching is enabled, the inputTokens field represents only the non-cached input tokens (tokens that were not read from or written to the cache). To calculate the total input tokens sent in a request, use the following formula: total input tokens = inputTokens + cacheReadInputTokens + cacheWriteInputTokens Prompt caching is enabled by default when you call the InvokeModel API. 
 You can set cache checkpoints at any point in
 your request body, similar to the previous example for the Converse API. 
 Anthropic Claude 
 The following example shows how to structure the body of your InvokeModel
 request for the Anthropic Claude 3.5 Sonnet v2 model. Note that the exact format and fields of the
 body for InvokeModel requests may vary depending on the model you choose. To see the
 format and content of the request and response bodies for different models, see
 Inference request parameters and response fields for foundation models . 
 Specify the desired ttl value as below, when ttl value not specified the default behavior of
 5 minutes caching applies. 
 "cache_control" : { 
 "type": "ephemeral",
 "ttl" : "5m | 1h"
}
 body= { 
 "anthropic_version": "bedrock-2023-05-31",
 "system":"Reply concisely",
 "messages": [
 { 
 "role": "user",
 "content": [
 { 
 "type": "text",
 "text": "Describe the best way to learn programming."
 },
 { 
 "type": "text",
 "text": "Add additional context here for the prompt that meets the minimum token requirement for your chosen model.",
 "cache_control": { 
 "type": "ephemeral"
 }
 }
 ]
 }
 ],
 "max_tokens": 2048,
 "temperature": 0.5,
 "top_p": 0.8,
 "stop_sequences": [
 "stop"
 ],
 "top_k": 250
} 
 Amazon Nova 
 The following example shows how to structure the body of your InvokeModel
 request for the Amazon Nova model. Note that the exact format and fields of the
 body for InvokeModel requests may vary depending on the model you choose. To see the
 format and content of the request and response bodies for different models, see
 Inference request parameters and response fields for foundation models . 
 { 
 "system": [ { 
 "text": "Reply Concisely"
 }],
 "messages": [ { 
 "role": "user",
 "content": [ { 
 "text": "Describe the best way to learn programming"
 },
 { 
 "text": "Add additional context here for the prompt that meets the minimum token requirement for your chosen model.",
 "cachePoint": { 
 "type": "default"
 }
 }]
 }],
 "inferenceConfig": { 
 "maxTokens": 300,
 "topP": 0.1,
 "topK": 20,
 "temperature": 0.3
 }
} 
 For more information about sending an InvokeModel request, see
 Submit a single prompt with InvokeModel . For OpenAI models, you use the Responses API — available on both the
 bedrock-runtime and bedrock-mantle endpoints —
 with prompt caching parameters specific to the model generation. For GPT-5.6
 models, you control caching with explicit breakpoints. For GPT-5.5 and earlier,
 caching is automatic. GPT-5.6 example with explicit cache breakpoints The following example shows a Responses API request to 
 openai.gpt-5.6-sol using explicit cache breakpoints. The system
 instruction is cached and reused across subsequent requests. { 
 "model": "openai.gpt-5.6-sol",
 "prompt_cache_key": "my-app:system-prompt-v1",
 "prompt_cache_options": { 
 "mode": "explicit"
 },
 "input": [
 { 
 "type": "message",
 "role": "developer",
 "content": [
 { 
 "type": "input_text",
 "text": "You are a technical support agent. Use the company knowledge base to answer questions. Follow these guidelines: 1. Always cite the relevant documentation section. 2. If unsure, escalate to a human agent. 3. Be concise but thorough...",
 "prompt_cache_breakpoint": { 
 "mode": "explicit"
 }
 }
 ]
 },
 { 
 "type": "message",
 "role": "user",
 "content": [
 { 
 "type": "input_text",
 "text": "How do I configure SSO for my organization?"
 }
 ]
 }
 ]
} GPT-5.5 example with automatic caching For GPT-5.5 and earlier models, prompt caching is automatic. No breakpoints
 or cache keys are needed — just ensure your prompt prefix exceeds 1,024 tokens. { 
 "model": "openai.gpt-5.5",
 "input": [
 { 
 "type": "message",
 "role": "developer",
 "content": [
 { 
 "type": "input_text",
 "text": "You are a technical support agent. Use the company knowledge base to answer questions..."
 }
 ]
 },
 { 
 "type": "message",
 "role": "user",
 "content": [
 { 
 "type": "input_text",
 "text": "How do I configure SSO for my organization?"
 }
 ]
 }
 ]
} Response The response includes cache usage metrics in the usage object: { 
 "id": "resp_abc123",
 "output": [...],
 "usage": { 
 "input_tokens": 2048,
 "output_tokens": 256,
 "total_tokens": 2304,
 "input_tokens_details": { 
 "cached_tokens": 1920,
 "cache_write_tokens": 0
 }
 }
} In this response, 1,920 tokens were served from cache and no new tokens were
 written, indicating a full cache hit with maximum cost savings. In a chat playground in the Amazon Bedrock console, you can turn on the prompt caching
 option, and Amazon Bedrock automatically creates cache checkpoints for you. Follow the instructions in Generate responses in the console using playgrounds to get started with prompting in an Amazon Bedrock
 playground. For supported models, prompt caching is automatically turned on
 in the playground. However, if it's not, then do the following to turn on prompt caching: 
 Open the Configurations menu. 
 Turn on the Prompt caching toggle. 
 Run your prompts. 
 After your combined input and model responses reach the minimum required
 number of tokens for a checkpoint (which varies by model), Amazon Bedrock automatically
 creates the first cache checkpoint for you. As you continue chatting, each
 subsequent reach of the minimum number of tokens creates a new checkpoint, up to
 the maximum number of checkpoints allowed for the model. You can view your cache
 checkpoints at any time by choosing View cache checkpoints 
 next to the Prompt caching toggle, as shown in the following screenshot. 
 You can view how many tokens are being read from and written to the cache due
 to each interaction with the model by viewing the Caching metrics 
 pop-up ( 
 ) in the playground responses. 
 If you turn off the prompt caching toggle while in the middle of a
 conversation, you can continue chatting with the model. 
 Javascript is disabled or is unavailable in your browser. To use the Amazon Web Services Documentation, Javascript must be enabled. Please refer to your browser's Help pages for instructions. Document Conventions Request a quota increase Best practices Did this page help you? - Yes Thanks for letting us know we're doing a good job! If you've got a moment, please tell us what we did right so we can do more of it. Did this page help you? - No Thanks for letting us know this page needs work. We're sorry we let you down. If you've got a moment, please tell us how we can make the documentation better. 