 
 Context Caching | DeepSeek API Docs 
 Skip to main content DeepSeek API Docs English English 中文（中国） DeepSeek Platform Quick Start Your First API Call Models &amp; Pricing Token &amp; Token Usage Rate Limit &amp; Isolation Error Codes Agent Integrations API Guides Vision Thinking Mode Multi-round Conversation Chat Prefix Completion (Beta) FIM Completion (Beta) JSON Output Tool Calls Files API Context Caching Using the Responses API Using the Anthropic API API Reference News Other Resources FAQ Change Log API Guides Context Caching On this page Context Caching 
 The DeepSeek API Context Caching on Disk Technology is enabled by default for all users, allowing them to benefit without needing to modify their code. 
 Each user request will trigger the construction of a hard disk cache. If subsequent requests have overlapping prefixes with previous requests, the overlapping part will only be fetched from the cache, which counts as a &quot;cache hit.&quot; 
 Cache Persistence and Hit Rules ​ 
 A cache hit requires that the corresponding prefix has already been &quot;persisted&quot; (written to the disk cache). Due to the Sliding Window Attention mechanism, the storage and matching of cached prefixes differs from before. Each cached prefix is an independent, complete unit. A subsequent request can only hit the cache if it fully matches a cache prefix unit . 
 When cache prefixes are persisted: ​ 
 Persistence at request boundaries : Each request will produce two cache prefix units at the end position of the user input and the end position of the model output . A subsequent request can hit the cache if it fully matches them. 
 Common prefix detection persistence : When the system detects a common prefix across multiple requests, it will persist that common prefix as an independent cache prefix unit . A subsequent request can hit the cache if it fully reuses that cache prefix unit . 
 Persistence at fixed token intervals : For long inputs or long outputs, the system will carve out cache prefix units at fixed token intervals, to avoid long prefixes from being completely uncacheable due to never reaching an end position. 
 Example 1: A user&#x27;s first-round request is A + B , and the second-round request is A + B + C . The second request can fully match the cache prefix unit A + B , hitting the cache for A + B . See Example 1 below. 
 Example 2: A user&#x27;s first-round request is A + B , and the second-round request is A + C . The second request cannot hit the cache, because A + C does not fully match the first round&#x27;s cache prefix unit ( A + B ). However, at this point the system will detect that the two requests share a common prefix A , and persist A as a cache prefix unit . When a third-round request A + D arrives, it can fully match the cache prefix unit A , hitting the cache for A . See Example 2 below. 
 Example 1: Multi-round Conversation ​ 
 First Request 
 messages: [ {&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: &quot;You are a helpful assistant&quot;}, {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;What is the capital of China?&quot;} ] 
 Second Request 
 messages: [ {&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: &quot;You are a helpful assistant&quot;}, {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;What is the capital of China?&quot;}, {&quot;role&quot;: &quot;assistant&quot;, &quot;content&quot;: &quot;The capital of China is Beijing.&quot;}, {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;What is the capital of the United States?&quot;} ] 
 In this example, the second request can fully reuse the cache prefix unit from the first request, which will count as a &quot;cache hit.&quot; 
 Example 2: Long Text Q&amp;A ​ 
 First Request 
 messages: [ {&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: &quot;You are an experienced financial report analyst...&quot;} {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;&lt;financial report content&gt;\n\nPlease summarize the key information of this financial report.&quot;} ] 
 Second Request 
 messages: [ {&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: &quot;You are an experienced financial report analyst...&quot;} {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;&lt;financial report content&gt;\n\nPlease analyze the profitability of this financial report.&quot;} ] 
 Third Request 
 messages: [ {&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: &quot;You are an experienced financial report analyst...&quot;} {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;&lt;financial report content&gt;\n\nPlease analyze the ratio of the company&#x27;s revenue to expenses.&quot;} ] 
 In the above example, the first two requests will not hit the cache. After the first two requests are completed, the system will identify the system message + &lt;financial report content&gt; in the user message as a cache prefix unit and persist it. In the third request, since it fully matches the previously persisted cache prefix unit , it can hit the cache. 
 Checking Cache Hit Status ​ 
 In the response from the DeepSeek API, we have added two fields in the usage section to reflect the cache hit status of the request: 
 prompt_cache_hit_tokens : The number of tokens in the input of this request that resulted in a cache hit. 
 prompt_cache_miss_tokens : The number of tokens in the input of this request that did not result in a cache hit. 
 Hard Disk Cache and Output Randomness ​ 
 The hard disk cache only matches the prefix part of the user&#x27;s input. The output is still generated through computation and inference, and it is influenced by parameters such as temperature, introducing randomness. 
 Additional Notes ​ 
 The cache system works on a &quot;best-effort&quot; basis and does not guarantee a 100% cache hit rate. 
 Cache construction takes seconds. Once the cache is no longer in use, it will be automatically cleared, usually within a few hours to a few days. 
 Previous Files API Next Using the Responses API Cache Persistence and Hit Rules When cache prefixes are persisted: Example 1: Multi-round Conversation Example 2: Long Text Q&amp;A Checking Cache Hit Status Hard Disk Cache and Output Randomness Additional Notes WeChat Official Account 
 Community Email Discord Twitter More GitHub Copyright © 2026 DeepSeek, Inc. 
 