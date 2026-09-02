 Prompt Caching - GroqDocs Docs Login Playground API Keys Dashboard Docs Log In Documentation Docs API Reference Search Docs Getting Started Overview Quickstart Models OpenAI Compatibility Responses API Rate Limits Templates API Reference Core Features Text Generation Speech to Text Text to Speech Orpheus OCR and Image Recognition Reasoning Content Moderation Structured Outputs Prompt Caching Tools &amp; Integrations Tool Use Overview Groq Built-In Tools Web Search Visit Website Code Execution Wolfram Alpha Browser Search (GPT OSS Models) Remote Tools and MCP Connectors Local Tool Calling Integrations Catalog Coding with Groq Factory Droid OpenCode Kilo Code Roo Code Cline Compound (Agentic AI) Overview Built-In Tools Systems Use Cases Guides Prompting Guide Basics Patterns Model Migration Assistant Message Prefilling Service Tiers Service Tiers Performance Tier Flex Processing Batch Processing Advanced LoRA Inference Production Readiness Production Checklist Optimizing Latency Security Onboarding Prometheus Metrics Account and Console Spend Limits Projects Model Permissions Billing FAQs Your Data Developer Resources SDK Libraries Groq Badge Developer Community OpenBench Error Codes Changelog Legal Policies &amp; Notices Search Docs API Reference Getting Started Overview Quickstart Models OpenAI Compatibility Responses API Rate Limits Templates API Reference Core Features Text Generation Speech to Text Text to Speech Orpheus OCR and Image Recognition Reasoning Content Moderation Structured Outputs Prompt Caching Tools &amp; Integrations Tool Use Overview Groq Built-In Tools Web Search Visit Website Code Execution Wolfram Alpha Browser Search (GPT OSS Models) Remote Tools and MCP Connectors Local Tool Calling Integrations Catalog Coding with Groq Factory Droid OpenCode Kilo Code Roo Code Cline Compound (Agentic AI) Overview Built-In Tools Systems Use Cases Guides Prompting Guide Basics Patterns Model Migration Assistant Message Prefilling Service Tiers Service Tiers Performance Tier Flex Processing Batch Processing Advanced LoRA Inference Production Readiness Production Checklist Optimizing Latency Security Onboarding Prometheus Metrics Account and Console Spend Limits Projects Model Permissions Billing FAQs Your Data Developer Resources SDK Libraries Groq Badge Developer Community OpenBench Error Codes Changelog Legal Policies &amp; Notices Prompt Caching Copy page 
 Model prompts often contain repetitive content, such as system prompts and tool definitions.
Prompt caching automatically reuses computation from recent requests when they share a common prefix, delivering significant cost savings and improved response times while maintaining data privacy through volatile-only storage that expires automatically. 
 Prompt caching works automatically on all your API requests with no code changes required and no additional fees. 
 How It Works 
 Prefix Matching : When you send a request, the system examines and identifies matching prefixes from recently processed requests stored temporarily in volatile memory. Prefixes can include system prompts, tool definitions, few-shot examples, and more. 
 Cache Hit : If a matching prefix is found, cached computation is reused, dramatically reducing latency and token costs by 50% for cached portions. 
 Cache Miss : If no match exists, your prompt is processed normally, with the prefix temporarily cached for potential future matches. 
 Automatic Expiration : All cached data automatically expires after 2 hours without use. 
 Prompt caching works automatically on all your API requests to supported models with no code changes required and no additional fees. Groq tries to maximize cache hits, but this is not guaranteed. Pricing discount will only apply on successful cache hits. 
 Cached tokens do not count towards your rate limits. However, cached tokens are subtracted from your limits after processing, so it&#x27;s still possible to hit your limits if you are sending a large number of input tokens in parallel requests. 
 Supported Models 
 Prompt caching is currently only supported for the following models: 
 Model ID Model openai/gpt-oss-20b GPT-OSS 20B openai/gpt-oss-120b GPT-OSS 120B openai/gpt-oss-safeguard-20b GPT-OSS-Safeguard 20B 
 We&#x27;re starting with a limited selection of models and will roll out prompt caching to more models soon. 
 Pricing 
 Prompt caching is provided at no additional cost. There is a 50% discount for cached input tokens. 
 Structuring Prompts for Optimal Caching 
 Cache hits are only possible for exact prefix matches within a prompt. To realize caching benefits, you need to think strategically about prompt organization: 
 Optimal Prompt Structure 
 Place static content like instructions and examples at the beginning of your prompt, and put variable content, such as user-specific information, at the end. This maximizes the length of the reusable prefix across different requests. 
 If you put variable information (like timestamps or user IDs) at the beginning, even identical system instructions later in the prompt won&#x27;t benefit from caching because the prefixes won&#x27;t match. 
 Place static content first: 
 System prompts and instructions 
 Few-shot examples 
 Tool definitions 
 Schema definitions 
 Common context or background information 
 Place dynamic content last: 
 User-specific queries 
 Variable data 
 Timestamps 
 Session-specific information 
 Unique identifiers 
 Example Structure 
 curl [SYSTEM PROMPT - Static]
 [TOOL DEFINITIONS - Static] 
 [FEW-SHOT EXAMPLES - Static]
 [COMMON INSTRUCTIONS - Static]
 [USER QUERY - Dynamic]
 [SESSION DATA - Dynamic] 
 This structure maximizes the likelihood that the static prefix portion will match across different requests, enabling cache hits while keeping user-specific content at the end. 
 Prompt Caching Examples 
 Multi turn conversations Large prompts and context Tool definitions and use Python import Groq from &quot;groq-sdk&quot;;
const groq = new Groq();
async function multiTurnConversation() {
 // Initial conversation with system message and first user input
 const initialMessages = [
 {
 role: &quot;system&quot;,
 content: &quot;You are a helpful AI assistant that provides detailed explanations about complex topics. Always provide comprehensive answers with examples and context.&quot;
 },
 {
 role: &quot;user&quot;,
 content: &quot;What is quantum computing?&quot;
 }
 ];
 // First request - creates cache for system message
 const firstResponse = await groq.chat.completions.create({
 messages: initialMessages,
 model: &quot;openai/gpt-oss-120b&quot;
 });
 console.log(&quot;First response:&quot;, firstResponse.choices[0].message.content);
 console.log(&quot;Usage:&quot;, firstResponse.usage);
 // Continue conversation - system message and previous context will be cached
 const conversationMessages = [
 ...initialMessages,
 firstResponse.choices[0].message,
 {
 role: &quot;user&quot;,
 content: &quot;Can you give me a simple example of how quantum superposition works?&quot;
 }
 ];
 const secondResponse = await groq.chat.completions.create({
 messages: conversationMessages,
 model: &quot;openai/gpt-oss-120b&quot;
 });
 console.log(&quot;Second response:&quot;, secondResponse.choices[0].message.content);
 console.log(&quot;Usage:&quot;, secondResponse.usage);
 // Continue with third turn
 const thirdTurnMessages = [
 ...conversationMessages,
 secondResponse.choices[0].message,
 {
 role: &quot;user&quot;,
 content: &quot;How does this relate to quantum entanglement?&quot;
 }
 ];
 const thirdResponse = await groq.chat.completions.create({
 messages: thirdTurnMessages,
 model: &quot;openai/gpt-oss-120b&quot;
 });
 console.log(&quot;Third response:&quot;, thirdResponse.choices[0].message.content);
 console.log(&quot;Usage:&quot;, thirdResponse.usage);
}
multiTurnConversation().catch(console.error); import os
 from groq import Groq
 client = Groq ( ) 
 def multi_turn_conversation ( ) : 
 # Initial conversation with system message and first user input 
 initial_messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a helpful AI assistant that provides detailed explanations about complex topics. Always provide comprehensive answers with examples and context.&quot; 
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;What is quantum computing?&quot; 
 } 
 ] 
 # First request - creates cache for system message 
 first_response = client . chat . completions . create ( 
 messages = initial_messages , 
 model = &quot;openai/gpt-oss-120b&quot; 
 ) 
 print ( &quot;First response:&quot; , first_response . choices [ 0 ] . message . content ) 
 print ( &quot;Usage:&quot; , first_response . usage ) 
 # Continue conversation - system message and previous context will be cached 
 conversation_messages = [ 
 * initial_messages , 
 first_response . choices [ 0 ] . message , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;Can you give me a simple example of how quantum superposition works?&quot; 
 } 
 ] 
 second_response = client . chat . completions . create ( 
 messages = conversation_messages , 
 model = &quot;openai/gpt-oss-120b&quot; 
 ) 
 print ( &quot;Second response:&quot; , second_response . choices [ 0 ] . message . content ) 
 print ( &quot;Usage:&quot; , second_response . usage ) 
 # Continue with third turn 
 third_turn_messages = [ 
 * conversation_messages , 
 second_response . choices [ 0 ] . message , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;How does this relate to quantum entanglement?&quot; 
 } 
 ] 
 third_response = client . chat . completions . create ( 
 messages = third_turn_messages , 
 model = &quot;openai/gpt-oss-120b&quot; 
 ) 
 print ( &quot;Third response:&quot; , third_response . choices [ 0 ] . message . content ) 
 print ( &quot;Usage:&quot; , third_response . usage ) 
 if __name__ == &quot;__main__&quot; : 
 multi_turn_conversation ( ) #!/bin/bash
# Multi-turn conversation example with prompt caching
# Set your GROQ_API_KEY environment variable before running
API_KEY=&quot;${GROQ_API_KEY}&quot;
BASE_URL=&quot;https://api.groq.com/openai/v1&quot;
if [ -z &quot;$API_KEY&quot; ]; then
 echo &quot;Error: GROQ_API_KEY environment variable is not set&quot;
 exit 1
fi
echo &quot;=== First Request (Creates Cache) ===&quot;
# First request - creates cache for system message
FIRST_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: &quot;You are a helpful AI assistant that provides detailed explanations about complex topics. Always provide comprehensive answers with examples and context.&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;What is quantum computing?&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;
 }&#x27;)
echo &quot;First response:&quot;
echo &quot;$FIRST_RESPONSE&quot; | jq &#x27;.choices[0].message.content&#x27;
echo &quot;Usage:&quot;
echo &quot;$FIRST_RESPONSE&quot; | jq &#x27;.usage&#x27;
# Extract the assistant&#x27;s response for next turn
ASSISTANT_RESPONSE=$(echo &quot;$FIRST_RESPONSE&quot; | jq -r &#x27;.choices[0].message.content&#x27;)
echo -e &quot;\n=== Second Request (Uses Cache) ===&quot;
# Second request - system message and previous context will be cached
SECOND_PAYLOAD=$(jq -n \
 --arg system_content &quot;You are a helpful AI assistant that provides detailed explanations about complex topics. Always provide comprehensive answers with examples and context.&quot; \
 --arg user1_content &quot;What is quantum computing?&quot; \
 --arg assistant1_content &quot;$ASSISTANT_RESPONSE&quot; \
 --arg user2_content &quot;Can you give me a simple example of how quantum superposition works?&quot; \
 --arg model &quot;openai/gpt-oss-120b&quot; \
 &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: $system_content
 },
 {
 &quot;role&quot;: &quot;user&quot;, 
 &quot;content&quot;: $user1_content
 },
 {
 &quot;role&quot;: &quot;assistant&quot;,
 &quot;content&quot;: $assistant1_content
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: $user2_content
 }
 ],
 &quot;model&quot;: $model
 }&#x27;)
SECOND_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &quot;$SECOND_PAYLOAD&quot;)
echo &quot;Second response:&quot;
echo &quot;$SECOND_RESPONSE&quot; | jq &#x27;.choices[0].message.content&#x27;
echo &quot;Usage:&quot;
echo &quot;$SECOND_RESPONSE&quot; | jq &#x27;.usage&#x27;
# Extract the second assistant response for third turn
SECOND_ASSISTANT_RESPONSE=$(echo &quot;$SECOND_RESPONSE&quot; | jq -r &#x27;.choices[0].message.content&#x27;)
echo -e &quot;\n=== Third Request (Uses Cache) ===&quot;
# Third request - even more conversation history cached
THIRD_PAYLOAD=$(jq -n \
 --arg system_content &quot;You are a helpful AI assistant that provides detailed explanations about complex topics. Always provide comprehensive answers with examples and context.&quot; \
 --arg user1_content &quot;What is quantum computing?&quot; \
 --arg assistant1_content &quot;$ASSISTANT_RESPONSE&quot; \
 --arg user2_content &quot;Can you give me a simple example of how quantum superposition works?&quot; \
 --arg assistant2_content &quot;$SECOND_ASSISTANT_RESPONSE&quot; \
 --arg user3_content &quot;How does this relate to quantum entanglement?&quot; \
 --arg model &quot;openai/gpt-oss-120b&quot; \
 &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: $system_content
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: $user1_content
 },
 {
 &quot;role&quot;: &quot;assistant&quot;, 
 &quot;content&quot;: $assistant1_content
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: $user2_content
 },
 {
 &quot;role&quot;: &quot;assistant&quot;,
 &quot;content&quot;: $assistant2_content
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: $user3_content
 }
 ],
 &quot;model&quot;: $model
 }&#x27;)
THIRD_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &quot;$THIRD_PAYLOAD&quot;)
echo &quot;Third response:&quot;
echo &quot;$THIRD_RESPONSE&quot; | jq &#x27;.choices[0].message.content&#x27;
echo &quot;Usage:&quot;
echo &quot;$THIRD_RESPONSE&quot; | jq &#x27;.usage&#x27; How Prompt Caching Works in Multi-Turn Conversations In this example, we demonstrate how to use prompt caching in a multi-turn conversation. During each turn, the system automatically caches the longest matching prefix from previous requests. The system message and conversation history that remain unchanged between requests will be cached, while only new user messages and assistant responses need fresh processing. This approach is useful for maintaining context in ongoing conversations without repeatedly processing the same information. For the first request: 
 prompt_tokens : Number of tokens in the system message and first user message 
 cached_tokens : 0 (no cache hit on first request) 
 For subsequent requests within the cache lifetime: 
 prompt_tokens : Total number of tokens in the entire conversation (system message + conversation history + new user message) 
 cached_tokens : Number of tokens in the system message and previous conversation history that were served from cache 
 When set up properly, you should see increasing cache efficiency as the conversation grows, with the system message and earlier conversation turns being served from cache while only new content requires processing. Python import Groq from &quot;groq-sdk&quot;;
const groq = new Groq();
async function analyzeLegalDocument() {
 // First request - creates cache for the large legal document
 const systemPrompt = `You are a legal expert AI assistant. Analyze the following legal document and provide detailed insights.
LEGAL DOCUMENT: &lt;entire contents of large legal document&gt;`;
 const firstAnalysis = await groq.chat.completions.create({
 messages: [
 {
 role: &quot;system&quot;,
 content: systemPrompt
 },
 {
 role: &quot;user&quot;,
 content: &quot;What are the key provisions regarding user account termination in this agreement?&quot;
 }
 ],
 model: &quot;openai/gpt-oss-120b&quot;
 });
 console.log(&quot;First analysis:&quot;, firstAnalysis.choices[0].message.content);
 console.log(&quot;Usage:&quot;, firstAnalysis.usage);
 // Second request - legal document will be cached, only new question processed
 const secondAnalysis = await groq.chat.completions.create({
 messages: [
 {
 role: &quot;system&quot;,
 content: systemPrompt
 },
 {
 role: &quot;user&quot;,
 content: &quot;What are the intellectual property rights implications for users who submit content?&quot;
 }
 ],
 model: &quot;openai/gpt-oss-120b&quot;
 });
 console.log(&quot;Second analysis:&quot;, secondAnalysis.choices[0].message.content);
 console.log(&quot;Usage:&quot;, secondAnalysis.usage);
 // Third request - same large context, different question
 const thirdAnalysis = await groq.chat.completions.create({
 messages: [
 {
 role: &quot;system&quot;,
 content: systemPrompt
 },
 {
 role: &quot;user&quot;,
 content: &quot;Are there any concerning limitations of liability clauses that users should be aware of?&quot;
 }
 ],
 model: &quot;openai/gpt-oss-120b&quot;
 });
 console.log(&quot;Third analysis:&quot;, thirdAnalysis.choices[0].message.content);
 console.log(&quot;Usage:&quot;, thirdAnalysis.usage);
}
analyzeLegalDocument().catch(console.error); from groq import Groq
 client = Groq ( ) 
 def analyze_legal_document ( ) : 
 # First request - creates cache for the large legal document 
 system_prompt = &quot;&quot;&quot;
 You are a legal expert AI assistant. Analyze the following legal document and provide detailed insights.\\n\\nLEGAL DOCUMENT:\\n&lt;entire contents of large legal document&gt;
 &quot;&quot;&quot; 
 first_analysis = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : system_prompt
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;What are the key provisions regarding user account termination in this agreement?&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-120b&quot; 
 ) 
 print ( &quot;First analysis:&quot; , first_analysis . choices [ 0 ] . message . content ) 
 print ( &quot;Usage:&quot; , first_analysis . usage ) 
 # Second request - legal document will be cached, only new question processed 
 second_analysis = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : system_prompt
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;What are the intellectual property rights implications for users who submit content?&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-120b&quot; 
 ) 
 print ( &quot;Second analysis:&quot; , second_analysis . choices [ 0 ] . message . content ) 
 print ( &quot;Usage:&quot; , second_analysis . usage ) 
 # Third request - same large context, different question 
 third_analysis = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : system_prompt
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;Are there any concerning limitations of liability clauses that users should be aware of?&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-120b&quot; 
 ) 
 print ( &quot;Third analysis:&quot; , third_analysis . choices [ 0 ] . message . content ) 
 print ( &quot;Usage:&quot; , third_analysis . usage ) 
 if __name__ == &quot;__main__&quot; : 
 analyze_legal_document ( ) #!/bin/bash
# Large prompts and context example with prompt caching
# Set your GROQ_API_KEY environment variable before running
API_KEY=&quot;${GROQ_API_KEY}&quot;
BASE_URL=&quot;https://api.groq.com/openai/v1&quot;
if [ -z &quot;$API_KEY&quot; ]; then
 echo &quot;Error: GROQ_API_KEY environment variable is not set&quot;
 exit 1
fi
SYSTEM_MESSAGE=&quot;You are a legal expert AI assistant. Analyze the following legal document and provide detailed insights.
LEGAL DOCUMENT: &lt;entire contents of large legal document&gt;&quot;
echo &quot;=== First Request (Creates Cache) ===&quot;
# First request - creates cache for the large legal document
FIRST_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &quot;$(jq -n \
 --arg system_msg &quot;$SYSTEM_MESSAGE&quot; \
 &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: $system_msg
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;What are the key provisions regarding user account termination in this agreement?&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;
 }&#x27;)&quot;)
echo &quot;First analysis:&quot;
echo &quot;$FIRST_RESPONSE&quot; | jq &#x27;.choices[0].message.content&#x27;
echo &quot;Usage:&quot;
echo &quot;$FIRST_RESPONSE&quot; | jq &#x27;.usage&#x27;
echo -e &quot;\\n=== Second Request (Uses Cache) ===&quot;
# Second request - legal document will be cached, only new question processed
SECOND_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &quot;$(jq -n \
 --arg system_msg &quot;$SYSTEM_MESSAGE&quot; \
 &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: $system_msg
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;What are the intellectual property rights implications for users who submit content?&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;
 }&#x27;)&quot;)
echo &quot;Second analysis:&quot;
echo &quot;$SECOND_RESPONSE&quot; | jq &#x27;.choices[0].message.content&#x27;
echo &quot;Usage:&quot;
echo &quot;$SECOND_RESPONSE&quot; | jq &#x27;.usage&#x27;
echo -e &quot;\\n=== Third Request (Uses Cache) ===&quot;
# Third request - same large context, different question
THIRD_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &quot;$(jq -n \
 --arg system_msg &quot;$SYSTEM_MESSAGE&quot; \
 &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: $system_msg
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Are there any concerning limitations of liability clauses that users should be aware of?&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;
 }&#x27;)&quot;)
echo &quot;Third analysis:&quot;
echo &quot;$THIRD_RESPONSE&quot; | jq &#x27;.choices[0].message.content&#x27;
echo &quot;Usage:&quot;
echo &quot;$THIRD_RESPONSE&quot; | jq &#x27;.usage&#x27; How Prompt Caching Works with Large Context In this example, we demonstrate caching large static content like legal documents, research papers, or extensive context that remains constant across multiple queries. The large legal document in the system message represents static content that benefits significantly from caching. Once cached, subsequent requests with different questions about the same document will reuse the cached computation for the document analysis, processing only the new user questions. This approach is particularly effective for document analysis, research assistance, or any scenario where you need to ask multiple questions about the same large piece of content. For the first request: 
 prompt_tokens : Total number of tokens in the system message (including the large legal document) and user message 
 cached_tokens : 0 (no cache hit on first request) 
 For subsequent requests within the cache lifetime: 
 prompt_tokens : Total number of tokens in the system message (including the large legal document) and user message 
 cached_tokens : Number of tokens in the entire cached system message (including the large legal document) 
 The caching efficiency is particularly high in this scenario since the large document (which may be thousands of tokens) is reused across multiple requests, while only small user queries (typically dozens of tokens) need fresh processing. Python import Groq from &quot;groq-sdk&quot;;
const groq = new Groq();
// Define comprehensive tool set
const tools = [
 {
 type: &quot;function&quot;,
 function: {
 name: &quot;get_weather&quot;,
 description: &quot;Get the current weather in a given location&quot;,
 parameters: {
 type: &quot;object&quot;,
 properties: {
 location: {
 type: &quot;string&quot;,
 description: &quot;The city and state, e.g. San Francisco, CA&quot;
 },
 unit: {
 type: &quot;string&quot;,
 enum: [&quot;celsius&quot;, &quot;fahrenheit&quot;],
 description: &quot;The unit of temperature&quot;
 }
 },
 required: [&quot;location&quot;]
 }
 }
 },
 {
 type: &quot;function&quot;,
 function: {
 name: &quot;calculate_math&quot;,
 description: &quot;Perform mathematical calculations&quot;,
 parameters: {
 type: &quot;object&quot;,
 properties: {
 expression: {
 type: &quot;string&quot;,
 description: &quot;Mathematical expression to evaluate, e.g. &#x27;2 + 2&#x27; or &#x27;sqrt(16)&#x27;&quot;
 }
 },
 required: [&quot;expression&quot;]
 }
 }
 },
 {
 type: &quot;function&quot;,
 function: {
 name: &quot;search_web&quot;,
 description: &quot;Search the web for current information&quot;,
 parameters: {
 type: &quot;object&quot;,
 properties: {
 query: {
 type: &quot;string&quot;,
 description: &quot;Search query&quot;
 },
 num_results: {
 type: &quot;integer&quot;,
 description: &quot;Number of results to return&quot;,
 minimum: 1,
 maximum: 10,
 default: 5
 }
 },
 required: [&quot;query&quot;]
 }
 }
 },
 {
 type: &quot;function&quot;,
 function: {
 name: &quot;get_time&quot;,
 description: &quot;Get the current time in a specific timezone&quot;,
 parameters: {
 type: &quot;object&quot;,
 properties: {
 timezone: {
 type: &quot;string&quot;,
 description: &quot;Timezone identifier, e.g. &#x27;America/New_York&#x27; or &#x27;UTC&#x27;&quot;
 }
 },
 required: [&quot;timezone&quot;]
 }
 }
 }
];
async function useToolsWithCaching() {
 // First request - creates cache for all tool definitions
 const systemPrompt = &quot;You are a helpful assistant with access to various tools. Use the appropriate tools to answer user questions accurately.&quot;;
 const firstRequest = await groq.chat.completions.create({
 messages: [
 {
 role: &quot;system&quot;,
 content: systemPrompt
 },
 {
 role: &quot;user&quot;,
 content: &quot;What&#x27;s the weather like in New York City?&quot;
 }
 ],
 model: &quot;openai/gpt-oss-120b&quot;,
 tools: tools
 });
 console.log(&quot;First request response:&quot;, firstRequest.choices[0].message);
 console.log(&quot;Usage:&quot;, firstRequest.usage);
 // Check if the model wants to use tools
 if (firstRequest.choices[0].message.tool_calls) {
 console.log(&quot;Tool calls requested:&quot;, firstRequest.choices[0].message.tool_calls);
 }
 // Second request - tool definitions will be cached
 const secondRequest = await groq.chat.completions.create({
 messages: [
 {
 role: &quot;system&quot;,
 content: systemPrompt
 },
 {
 role: &quot;user&quot;,
 content: &quot;Can you calculate the square root of 144 and tell me what time it is in Tokyo?&quot;
 }
 ],
 model: &quot;openai/gpt-oss-120b&quot;,
 tools: tools
 });
 console.log(&quot;Second request response:&quot;, secondRequest.choices[0].message);
 console.log(&quot;Usage:&quot;, secondRequest.usage);
 if (secondRequest.choices[0].message.tool_calls) {
 console.log(&quot;Tool calls requested:&quot;, secondRequest.choices[0].message.tool_calls);
 }
 // Third request - same tool definitions cached
 const thirdRequest = await groq.chat.completions.create({
 messages: [
 {
 role: &quot;system&quot;,
 content: systemPrompt
 },
 {
 role: &quot;user&quot;,
 content: &quot;Search for recent news about artificial intelligence developments.&quot;
 }
 ],
 model: &quot;openai/gpt-oss-120b&quot;,
 tools: tools
 });
 console.log(&quot;Third request response:&quot;, thirdRequest.choices[0].message);
 console.log(&quot;Usage:&quot;, thirdRequest.usage);
 if (thirdRequest.choices[0].message.tool_calls) {
 console.log(&quot;Tool calls requested:&quot;, thirdRequest.choices[0].message.tool_calls);
 }
}
useToolsWithCaching().catch(console.error); from groq import Groq
 client = Groq ( ) 
 # Define comprehensive tool set 
 tools = [ 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;get_weather&quot; , 
 &quot;description&quot; : &quot;Get the current weather in a given location&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;location&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The city and state, e.g. San Francisco, CA&quot; 
 } , 
 &quot;unit&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;enum&quot; : [ &quot;celsius&quot; , &quot;fahrenheit&quot; ] , 
 &quot;description&quot; : &quot;The unit of temperature&quot; 
 } 
 } , 
 &quot;required&quot; : [ &quot;location&quot; ] 
 } 
 } 
 } , 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;calculate_math&quot; , 
 &quot;description&quot; : &quot;Perform mathematical calculations&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;expression&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Mathematical expression to evaluate, e.g. &#x27;2 + 2&#x27; or &#x27;sqrt(16)&#x27;&quot; 
 } 
 } , 
 &quot;required&quot; : [ &quot;expression&quot; ] 
 } 
 } 
 } , 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;search_web&quot; , 
 &quot;description&quot; : &quot;Search the web for current information&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;query&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Search query&quot; 
 } , 
 &quot;num_results&quot; : { 
 &quot;type&quot; : &quot;integer&quot; , 
 &quot;description&quot; : &quot;Number of results to return&quot; , 
 &quot;minimum&quot; : 1 , 
 &quot;maximum&quot; : 10 , 
 &quot;default&quot; : 5 
 } 
 } , 
 &quot;required&quot; : [ &quot;query&quot; ] 
 } 
 } 
 } , 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;get_time&quot; , 
 &quot;description&quot; : &quot;Get the current time in a specific timezone&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;timezone&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Timezone identifier, e.g. &#x27;America/New_York&#x27; or &#x27;UTC&#x27;&quot; 
 } 
 } , 
 &quot;required&quot; : [ &quot;timezone&quot; ] 
 } 
 } 
 } 
 ] 
 def use_tools_with_caching ( ) : 
 # First request - creates cache for all tool definitions 
 first_request = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a helpful assistant with access to various tools. Use the appropriate tools to answer user questions accurately.&quot; 
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;What&#x27;s the weather like in New York City?&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-120b&quot; , 
 tools = tools
 ) 
 print ( &quot;First request response:&quot; , first_request . choices [ 0 ] . message ) 
 print ( &quot;Usage:&quot; , first_request . usage ) 
 # Check if the model wants to use tools 
 if first_request . choices [ 0 ] . message . tool_calls : 
 print ( &quot;Tool calls requested:&quot; , first_request . choices [ 0 ] . message . tool_calls ) 
 # Second request - tool definitions will be cached 
 second_request = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a helpful assistant with access to various tools. Use the appropriate tools to answer user questions accurately.&quot; 
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;Can you calculate the square root of 144 and tell me what time it is in Tokyo?&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-120b&quot; , 
 tools = tools
 ) 
 print ( &quot;Second request response:&quot; , second_request . choices [ 0 ] . message ) 
 print ( &quot;Usage:&quot; , second_request . usage ) 
 if second_request . choices [ 0 ] . message . tool_calls : 
 print ( &quot;Tool calls requested:&quot; , second_request . choices [ 0 ] . message . tool_calls ) 
 # Third request - same tool definitions cached 
 third_request = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a helpful assistant with access to various tools. Use the appropriate tools to answer user questions accurately.&quot; 
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;Search for recent news about artificial intelligence developments.&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-120b&quot; , 
 tools = tools
 ) 
 print ( &quot;Third request response:&quot; , third_request . choices [ 0 ] . message ) 
 print ( &quot;Usage:&quot; , third_request . usage ) 
 if third_request . choices [ 0 ] . message . tool_calls : 
 print ( &quot;Tool calls requested:&quot; , third_request . choices [ 0 ] . message . tool_calls ) 
 if __name__ == &quot;__main__&quot; : 
 use_tools_with_caching ( ) #!/bin/bash
# Tool definitions and use example with prompt caching
# Set your GROQ_API_KEY environment variable before running
API_KEY=&quot;${GROQ_API_KEY}&quot;
BASE_URL=&quot;https://api.groq.com/openai/v1&quot;
if [[ -z &quot;$API_KEY&quot; ]]; then
 echo &quot;Error: GROQ_API_KEY environment variable is not set&quot;
 exit 1
fi
# Define comprehensive tool set
TOOLS=&#x27;[
 {
 &quot;type&quot;: &quot;function&quot;,
 &quot;function&quot;: {
 &quot;name&quot;: &quot;get_weather&quot;,
 &quot;description&quot;: &quot;Get the current weather in a given location&quot;,
 &quot;parameters&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;location&quot;: {
 &quot;type&quot;: &quot;string&quot;,
 &quot;description&quot;: &quot;The city and state, e.g. San Francisco, CA&quot;
 },
 &quot;unit&quot;: {
 &quot;type&quot;: &quot;string&quot;,
 &quot;enum&quot;: [&quot;celsius&quot;, &quot;fahrenheit&quot;],
 &quot;description&quot;: &quot;The unit of temperature&quot;
 }
 },
 &quot;required&quot;: [&quot;location&quot;]
 }
 }
 },
 {
 &quot;type&quot;: &quot;function&quot;,
 &quot;function&quot;: {
 &quot;name&quot;: &quot;calculate_math&quot;,
 &quot;description&quot;: &quot;Perform mathematical calculations&quot;,
 &quot;parameters&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;expression&quot;: {
 &quot;type&quot;: &quot;string&quot;,
 &quot;description&quot;: &quot;Mathematical expression to evaluate, e.g. &#x27;\&#x27;&#x27;2 + 2&#x27;\&#x27;&#x27; or &#x27;\&#x27;&#x27;sqrt(16)&#x27;\&#x27;&#x27;&quot;
 }
 },
 &quot;required&quot;: [&quot;expression&quot;]
 }
 }
 },
 {
 &quot;type&quot;: &quot;function&quot;,
 &quot;function&quot;: {
 &quot;name&quot;: &quot;search_web&quot;,
 &quot;description&quot;: &quot;Search the web for current information&quot;,
 &quot;parameters&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;query&quot;: {
 &quot;type&quot;: &quot;string&quot;,
 &quot;description&quot;: &quot;Search query&quot;
 },
 &quot;num_results&quot;: {
 &quot;type&quot;: &quot;integer&quot;,
 &quot;description&quot;: &quot;Number of results to return&quot;,
 &quot;minimum&quot;: 1,
 &quot;maximum&quot;: 10,
 &quot;default&quot;: 5
 }
 },
 &quot;required&quot;: [&quot;query&quot;]
 }
 }
 },
 {
 &quot;type&quot;: &quot;function&quot;,
 &quot;function&quot;: {
 &quot;name&quot;: &quot;get_time&quot;,
 &quot;description&quot;: &quot;Get the current time in a specific timezone&quot;,
 &quot;parameters&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;timezone&quot;: {
 &quot;type&quot;: &quot;string&quot;,
 &quot;description&quot;: &quot;Timezone identifier, e.g. &#x27;\&#x27;&#x27;America/New_York&#x27;\&#x27;&#x27; or &#x27;\&#x27;&#x27;UTC&#x27;\&#x27;&#x27;&quot;
 }
 },
 &quot;required&quot;: [&quot;timezone&quot;]
 }
 }
 }
]&#x27;
SYSTEM_MESSAGE=&quot;You are a helpful assistant with access to various tools. Use the appropriate tools to answer user questions accurately.&quot;
echo &quot;=== First Request (Creates Cache) ===&quot;
# First request - creates cache for all tool definitions
FIRST_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &quot;$(jq -n \
 --arg system_msg &quot;$SYSTEM_MESSAGE&quot; \
 --argjson tools &quot;$TOOLS&quot; \
 &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: $system_msg
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;What&#x27;\&#x27;&#x27;s the weather like in New York City?&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;,
 &quot;tools&quot;: $tools
 }&#x27;)&quot;)
echo &quot;First request response:&quot;
echo &quot;$FIRST_RESPONSE&quot; | jq &#x27;.choices[0].message&#x27;
echo &quot;Usage:&quot;
echo &quot;$FIRST_RESPONSE&quot; | jq &#x27;.usage&#x27;
# Check if tool calls were requested
TOOL_CALLS=$(echo &quot;$FIRST_RESPONSE&quot; | jq &#x27;.choices[0].message.tool_calls // empty&#x27;)
if [[ -n &quot;$TOOL_CALLS&quot; &amp;&amp; &quot;$TOOL_CALLS&quot; != &quot;null&quot; ]]; then
 echo &quot;Tool calls requested:&quot;
 echo &quot;$TOOL_CALLS&quot;
fi
echo -e &quot;\n=== Second Request (Uses Cache) ===&quot;
# Second request - tool definitions will be cached
SECOND_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &quot;$(jq -n \
 --arg system_msg &quot;$SYSTEM_MESSAGE&quot; \
 --argjson tools &quot;$TOOLS&quot; \
 &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: $system_msg
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Can you calculate the square root of 144 and tell me what time it is in Tokyo?&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;,
 &quot;tools&quot;: $tools
 }&#x27;)&quot;)
echo &quot;Second request response:&quot;
echo &quot;$SECOND_RESPONSE&quot; | jq &#x27;.choices[0].message&#x27;
echo &quot;Usage:&quot;
echo &quot;$SECOND_RESPONSE&quot; | jq &#x27;.usage&#x27;
# Check if tool calls were requested
TOOL_CALLS=$(echo &quot;$SECOND_RESPONSE&quot; | jq &#x27;.choices[0].message.tool_calls // empty&#x27;)
if [[ -n &quot;$TOOL_CALLS&quot; &amp;&amp; &quot;$TOOL_CALLS&quot; != &quot;null&quot; ]]; then
 echo &quot;Tool calls requested:&quot;
 echo &quot;$TOOL_CALLS&quot;
fi
echo -e &quot;\n=== Third Request (Uses Cache) ===&quot;
# Third request - same tool definitions cached
THIRD_RESPONSE=$(curl -s -X POST &quot;$BASE_URL/chat/completions&quot; \
 -H &quot;Authorization: Bearer $API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &quot;$(jq -n \
 --arg system_msg &quot;$SYSTEM_MESSAGE&quot; \
 --argjson tools &quot;$TOOLS&quot; \
 &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: $system_msg
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Search for recent news about artificial intelligence developments.&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;,
 &quot;tools&quot;: $tools
 }&#x27;)&quot;)
echo &quot;Third request response:&quot;
echo &quot;$THIRD_RESPONSE&quot; | jq &#x27;.choices[0].message&#x27;
echo &quot;Usage:&quot;
echo &quot;$THIRD_RESPONSE&quot; | jq &#x27;.usage&#x27;
# Check if tool calls were requested
TOOL_CALLS=$(echo &quot;$THIRD_RESPONSE&quot; | jq &#x27;.choices[0].message.tool_calls // empty&#x27;)
if [[ -n &quot;$TOOL_CALLS&quot; &amp;&amp; &quot;$TOOL_CALLS&quot; != &quot;null&quot; ]]; then
 echo &quot;Tool calls requested:&quot;
 echo &quot;$TOOL_CALLS&quot;
fi How Prompt Caching Works with Tool Definitions In this example, we demonstrate caching tool definitions. All tool definitions, including their schemas, descriptions, and parameters, are cached as a single prefix when they remain consistent across requests. This is particularly valuable when you have a comprehensive set of tools that you want to reuse across multiple requests without re-processing them each time. The system message and all tool definitions form the static prefix that gets cached, while user queries remain dynamic and are processed fresh for each request. This approach is useful when you have a consistent set of tools that you want to reuse across multiple requests without re-processing them each time. For the first request: 
 prompt_tokens : Total number of tokens in the system message, tool definitions, and user message 
 cached_tokens : 0 (no cache hit on first request) 
 For subsequent requests within the cache lifetime: 
 prompt_tokens : Total number of tokens in the system message, tool definitions, and user message 
 cached_tokens : Number of tokens in all cached tool definitions and system prompt 
 Tool definitions can be quite lengthy due to detailed parameter schemas and descriptions, making caching particularly beneficial for reducing both latency and costs when the same tool set is used repeatedly. 
 Requirements and Limitations 
 Caching Requirements 
 Exact Prefix Matching : Cache hits require exact matches of the beginning of your prompt 
 Minimum Prompt Length : The minimum cacheable prompt length varies by model, ranging from 128 to 1024 tokens depending on the specific model used 
 To check how much of your prompt was cached, see the response usage fields . 
 What Can Be Cached 
 Complete message arrays including system, user, and assistant messages 
 Tool definitions and function schemas 
 System instructions and prompt templates 
 One-shot and few-shot examples 
 Structured output schemas 
 Large static content like legal documents, research papers, or extensive context that remains constant across multiple queries 
 Image inputs , including image URLs and base64-encoded images 
 Limitations 
 Exact Matching : Even minor changes in cached portions prevent cache hits and force a new cache to be created 
 No Manual Control : Cache clearing and management is automatic only 
 Tracking Cache Usage 
 You can monitor how many tokens are being served from cache by examining the usage field in your API response. The response includes detailed token usage information, including how many tokens were cached. 
 Response Usage Structure 
 JSON { 
 &quot;id&quot; : &quot;chatcmpl-...&quot; , 
 &quot;model&quot; : &quot;openai/gpt-oss-120b&quot; , 
 &quot;usage&quot; : { 
 &quot;queue_time&quot; : 0.026959759 , 
 &quot;prompt_tokens&quot; : 4641 , 
 &quot;prompt_time&quot; : 0.009995497 , 
 &quot;completion_tokens&quot; : 1817 , 
 &quot;completion_time&quot; : 5.57691751 , 
 &quot;total_tokens&quot; : 6458 , 
 &quot;total_time&quot; : 5.586913007 , 
 &quot;prompt_tokens_details&quot; : { 
 &quot;cached_tokens&quot; : 4608 
 } 
 } , 
 ... other fields
 } 
 Understanding the Fields 
 prompt_tokens : Total number of tokens in your input prompt 
 cached_tokens : Number of input tokens that were served from cache (within prompt_tokens_details ) 
 completion_tokens : Number of tokens in the model&#x27;s response 
 total_tokens : Sum of prompt and completion tokens 
 In the example above, out of 4641 prompt tokens, 4608 tokens (99.3%) were served from cache, resulting in significant cost savings and improved response time. 
 Calculating Cache Hit Rate 
 To calculate your cache hit rate: 
 Cache Hit Rate = cached_tokens / prompt_tokens × 100%
 For the example above: 4608 / 4641 × 100% = 99.3% 
 A higher cache hit rate indicates better prompt structure optimization leading to lower latency and more cost savings. 
 Troubleshooting 
 Verify that sections that you want to cache are identical between requests 
 Check that calls are made within the cache lifetime (a few hours). Calls that are too far apart will not benefit from caching. 
 Ensure that tool_choice , tool usage, and image usage remain consistent between calls 
 Validate that you are caching at least the minimum number of tokens through the usage fields . 
 Changes to cached sections, including tool_choice and image usage, will invalidate the cache and require a new cache to be created. Subsequent calls will use the new cache. 
 Frequently Asked Questions 
 How is data privacy maintained with caching? 
 All cached data exists only in volatile memory and automatically expires within a few hours. No prompt or response content is ever stored in persistent storage or shared between organizations. 
 Does caching affect the quality or consistency of responses? 
 No. Prompt caching only affects the processing of the input prompt, not the generation of responses. The actual model inference and response generation occur normally, maintaining identical output quality whether caching is used or not. 
 Can I disable prompt caching? 
 Prompt caching is automatically enabled and cannot be manually disabled. This helps customers benefit from reduced costs and latency. Prompts are not stored in persistent storage. 
 How do I know if my requests are benefiting from caching? 
 You can track cache usage by examining the usage field in your API responses. Cache hits are not guaranteed, but Groq tries to maximize them. See the Tracking Cache Usage section above for detailed information on how to monitor cached tokens and calculate your cache hit rate. 
 Are there any additional costs for using prompt caching? 
 No. Prompt caching is provided at no additional cost and can help to reduce your costs by 50% for cached tokens while improving response times. 
 Does caching affect rate limits? 
 Cached tokens do not count toward your rate limits. 
 Can I manually clear or refresh caches? 
 No manual cache management is available. All cache expiration and cleanup happens automatically. 
 Does the prompt caching discount work with batch requests? 
 Batch requests can still benefit from prompt caching, but the prompt caching discount does not stack with the batch discount. Batch requests already receive a 50% discount on all tokens, and while caching functionality remains active, no additional discount is applied to cached tokens in batch requests. Was this page helpful? Yes No Suggest Edits On this page 