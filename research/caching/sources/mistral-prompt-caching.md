 Chat Docs &amp; API Search docs ⌘K Vibe Studio Inference &amp; Models Admin Resources API Reference Search docs ⌘K Toggle theme Reach out Try Studio Download OpenAPI Spec Home Getting Started Chat post Chat Completion Fim Embeddings Classifiers Files Models Batch Ocr Audio Transcriptions Audio Speech Audio Voices Events Workflows Workflows Deployments Workflows Events Workflows Executions Workflows Metrics Workflows Runs Workflows Schedules Public Preview Beta Agents Beta Conversations Beta Libraries Beta Libraries Documents Beta Libraries Accesses Beta Connectors Beta Admin Users Beta Admin Workspaces Beta Admin Api Keys Beta Admin Billing Beta Admin Audit Logs Beta Admin User Groups Beta Admin Scim Beta Admin Vibe Code Analytics Beta Admin Vibe Work Analytics Beta Observability Campaigns Beta Observability Chat Completion Events Beta Observability Chat Completion Events Fields Beta Observability Datasets Beta Observability Datasets Records Beta Observability Judges Beta Observability Logs Beta Observability Spans Beta Observability Traces Beta Prompts Beta Skills Beta Rag Ingestion Pipeline Configurations Beta Rag Search Indexes Beta Users Deprecated Deprecated Agents Getting Started Chat Chat Endpoints Chat Completion API. Toggle theme Examples Real world code examples 
 Chat Completion POST /v1/chat/completions # Chat Completion Request Body # application/json frequency_penalty # number | null The frequency_penalty penalizes the repetition of words based on their frequency in the generated text. A higher frequency penalty discourages the model from repeating words that have already appeared frequently in the output, promoting diversity and reducing repetition. guardrails # array &lt; GuardrailConfig &gt; | null max_tokens # integer | null The maximum number of tokens to generate in the completion. The token count of your prompt plus max_tokens cannot exceed the model&#x27;s context length. messages # * array &lt; SystemMessage | UserMessage | AssistantMessage | ToolMessage &gt; The prompt(s) to generate completions for, encoded as a list of dict with role and content. metadata # map &lt; any &gt; | null model # * string ID of the model to use. You can use the List Available Models API to see all of your available models, or see our Model overview for model descriptions. n # integer | null Number of completions to return for each request, input tokens are only billed once. parallel_tool_calls # boolean Default Value: true Whether to enable parallel function calling during tool use, when enabled the model can call multiple tools in parallel. prediction # Prediction | null Enable users to specify an expected completion, optimizing response times by leveraging known or predictable content. presence_penalty # number | null The presence_penalty determines how much the model penalizes the repetition of words or phrases. A higher presence penalty encourages the model to use a wider variety of words and phrases, making the output more diverse and creative. prompt_cache_key # string | null A cache key for prompt caching. Use the same key for requests with shared prompt prefixes, such as multi-turn conversations or repeated system prompts, to increase cache hits. Cached tokens are billed at 10% of the standard input token price. prompt_mode # &quot;reasoning&quot; Available options to the prompt_mode argument on the chat completion endpoint.
Values represent high-level intent. Assignment to actual SPs is handled internally.
System prompt may include knowledge cutoff date, model capabilities, tone to use, safety guidelines, etc. random_seed # integer | null The seed to use for random sampling. If set, different calls will generate deterministic results. reasoning_effort # &quot;none&quot; | &quot;minimal&quot; | &quot;low&quot; | &quot;medium&quot; | &quot;high&quot; | &quot;xhigh&quot; response_format # ResponseFormat | null Specify the format that the model must output. By default it will use { &quot;type&quot;: &quot;text&quot; } . Setting to { &quot;type&quot;: &quot;json_object&quot; } enables JSON mode, which guarantees the message the model generates is in JSON. When using JSON mode you MUST also instruct the model to produce JSON yourself with a system or a user message. Setting to { &quot;type&quot;: &quot;json_schema&quot; } enables JSON schema mode, which guarantees the message the model generates is in JSON and follows the schema you provide. safe_prompt # boolean Default Value: false Whether to inject a safety prompt before all conversations. service_tier # &quot;auto&quot; | &quot;standard_only&quot; Determines whether to serve the request using priority or standard capacity. stop # string | array &lt; string &gt; | null Stop generation if this token is detected. Or if one of these tokens is detected when providing an array stream # boolean Default Value: false Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON. temperature # number | null What sampling temperature to use, we recommend between 0.0 and 0.7. Higher values like 0.7 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both. The default value varies depending on the model you are targeting. Call the /models endpoint to retrieve the appropriate value. tool_choice # ToolChoice | &quot;auto&quot; | &quot;none&quot; | &quot;any&quot; | &quot;required&quot; Controls which (if any) tool is called by the model. none means the model will not call any tool and instead generates a message. auto means the model can pick between generating a message or calling one or more tools. any or required means the model must call one or more tools. Specifying a particular tool via {&quot;type&quot;: &quot;function&quot;, &quot;function&quot;: {&quot;name&quot;: &quot;my_function&quot;}} forces the model to call that tool. tools # array &lt; Tool | WebSearchTool | WebSearchPremiumTool | CodeInterpreterTool | ImageGenerationTool | DocumentLibraryTool | CustomConnector &gt; | null A list of tools the model may call. Use this to provide a list of functions the model may generate JSON inputs for. top_p # number | null Nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both. 200 (application/json) 200 (text/event-stream) Successful Response choices # * array &lt; ChatCompletionChoice &gt; created # * integer id # * string model # * string object # * string usage # * UsageInfo Response Type event-stream &lt; CompletionEvent &gt; Successful Response CompletionEvent # {object} Playground Test the endpoints live TypeScript Python cURL import { Mistral } from &quot;@mistralai/mistralai&quot; ; 
 const client = new Mistral ( { apiKey : process . env . MISTRAL_API_KEY } ) ; 
 const response = await client . chat . complete ( { 
 model : &quot;mistral-large-latest&quot; , 
 messages : [ 
 { 
 role : &quot;user&quot; , 
 content : &quot;Who is the best French painter? Answer in one short sentence.&quot; , 
 } , 
 ] , 
 } ) ; 
 console . log ( response . choices [ 0 ] . message . content ) ; 
 import { Mistral } from &quot;@mistralai/mistralai&quot; ; 
 const client = new Mistral ( { apiKey : process . env . MISTRAL_API_KEY } ) ; 
 const response = await client . chat . complete ( { 
 model : &quot;mistral-large-latest&quot; , 
 messages : [ 
 { 
 role : &quot;user&quot; , 
 content : &quot;Who is the best French painter? Answer in one short sentence.&quot; , 
 } , 
 ] , 
 } ) ; 
 console . log ( response . choices [ 0 ] . message . content ) ; 
 V2 V1 from mistralai . client import Mistral
 import os
 with Mistral ( 
 api_key = os . getenv ( &quot;MISTRAL_API_KEY&quot; , &quot;&quot; ) , 
 ) as mistral : 
 response = mistral . chat . complete ( 
 model = &quot;mistral-large-latest&quot; , 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;Who is the best French painter? Answer in one short sentence.&quot; , 
 } 
 ] , 
 ) 
 print ( response . choices [ 0 ] . message . content ) 
 from mistralai . client import Mistral
 import os
 with Mistral ( 
 api_key = os . getenv ( &quot;MISTRAL_API_KEY&quot; , &quot;&quot; ) , 
 ) as mistral : 
 response = mistral . chat . complete ( 
 model = &quot;mistral-large-latest&quot; , 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;Who is the best French painter? Answer in one short sentence.&quot; , 
 } 
 ] , 
 ) 
 print ( response . choices [ 0 ] . message . content ) 
 curl https://api.mistral.ai/v1/chat/completions \ 
 -H &quot;Content-Type: application/json&quot; \ 
 -H &quot;Authorization: Bearer $MISTRAL_API_KEY &quot; \ 
 -d &#x27;{
 &quot;model&quot;: &quot;mistral-large-latest&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Who is the best French painter? Answer in one short sentence.&quot;
 }
 ]
 }&#x27; 
 curl https://api.mistral.ai/v1/chat/completions \ 
 -H &quot;Content-Type: application/json&quot; \ 
 -H &quot;Authorization: Bearer $MISTRAL_API_KEY &quot; \ 
 -d &#x27;{
 &quot;model&quot;: &quot;mistral-large-latest&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Who is the best French painter? Answer in one short sentence.&quot;
 }
 ]
 }&#x27; 
 200 (application/json) 200 (text/event-stream) { 
 &quot;choices&quot; : [ 
 { 
 &quot;finish_reason&quot; : &quot;stop&quot; , 
 &quot;index&quot; : &quot;&lt;to fill&gt;&quot; 
 } 
 ] , 
 &quot;created&quot; : &quot;1702256327&quot; , 
 &quot;id&quot; : &quot;cmpl-e5cc70bb28c444948073e77776eb30ef&quot; , 
 &quot;model&quot; : &quot;mistral-small-latest&quot; , 
 &quot;object&quot; : &quot;chat.completion&quot; , 
 &quot;usage&quot; : { } 
 } { 
 &quot;choices&quot; : [ 
 { 
 &quot;finish_reason&quot; : &quot;stop&quot; , 
 &quot;index&quot; : &quot;&lt;to fill&gt;&quot; 
 } 
 ] , 
 &quot;created&quot; : &quot;1702256327&quot; , 
 &quot;id&quot; : &quot;cmpl-e5cc70bb28c444948073e77776eb30ef&quot; , 
 &quot;model&quot; : &quot;mistral-small-latest&quot; , 
 &quot;object&quot; : &quot;chat.completion&quot; , 
 &quot;usage&quot; : { } 
 } null null WHY MISTRAL About us Our customers Careers Contact us EXPLORE AI Solutions Partners Research DOCUMENTATION Documentation Ambassadors Cookbooks BUILD Studio Vibe Mistral Code Mistral Compute Try the API LEGAL Terms of service Privacy policy Legal notice Privacy Choices Brand COMMUNITY Discord ↗ X ↗ Github ↗ LinkedIn ↗ Ambassadors Mistral AI © 2026 Toggle theme 