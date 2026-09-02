 Tool Use Overview - GroqDocs Docs Login Playground API Keys Dashboard Docs Log In Documentation Docs API Reference Search Docs Getting Started Overview Quickstart Models OpenAI Compatibility Responses API Rate Limits Templates API Reference Core Features Text Generation Speech to Text Text to Speech Orpheus OCR and Image Recognition Reasoning Content Moderation Structured Outputs Prompt Caching Tools &amp; Integrations Tool Use Overview Groq Built-In Tools Web Search Visit Website Code Execution Wolfram Alpha Browser Search (GPT OSS Models) Remote Tools and MCP Connectors Local Tool Calling Integrations Catalog Coding with Groq Factory Droid OpenCode Kilo Code Roo Code Cline Compound (Agentic AI) Overview Built-In Tools Systems Use Cases Guides Prompting Guide Basics Patterns Model Migration Assistant Message Prefilling Service Tiers Service Tiers Performance Tier Flex Processing Batch Processing Advanced LoRA Inference Production Readiness Production Checklist Optimizing Latency Security Onboarding Prometheus Metrics Account and Console Spend Limits Projects Model Permissions Billing FAQs Your Data Developer Resources SDK Libraries Groq Badge Developer Community OpenBench Error Codes Changelog Legal Policies &amp; Notices Search Docs API Reference Getting Started Overview Quickstart Models OpenAI Compatibility Responses API Rate Limits Templates API Reference Core Features Text Generation Speech to Text Text to Speech Orpheus OCR and Image Recognition Reasoning Content Moderation Structured Outputs Prompt Caching Tools &amp; Integrations Tool Use Overview Groq Built-In Tools Web Search Visit Website Code Execution Wolfram Alpha Browser Search (GPT OSS Models) Remote Tools and MCP Connectors Local Tool Calling Integrations Catalog Coding with Groq Factory Droid OpenCode Kilo Code Roo Code Cline Compound (Agentic AI) Overview Built-In Tools Systems Use Cases Guides Prompting Guide Basics Patterns Model Migration Assistant Message Prefilling Service Tiers Service Tiers Performance Tier Flex Processing Batch Processing Advanced LoRA Inference Production Readiness Production Checklist Optimizing Latency Security Onboarding Prometheus Metrics Account and Console Spend Limits Projects Model Permissions Billing FAQs Your Data Developer Resources SDK Libraries Groq Badge Developer Community OpenBench Error Codes Changelog Legal Policies &amp; Notices Tool Use Copy page 
 Applications using LLMs become much more powerful when the model can interact with external resources, such as APIs, databases, and the web, to gather dynamic data or to perform actions. Tool use (or function calling) is what transforms a language model from a conversational interface into an autonomous agent capable of taking action, accessing real-time information, and solving complex multi-step problems. 
 This doc starts with a high-level overview of tool use and then dives into the details of how tool use works. If you&#x27;re already familiar with tool use, you can skip to the How to Use Tools on the Groq API section. 
 How Tool Use Works 
 There are a few important pieces in the tool calling process: 
 A request is made to the model with tool definitions 
 The model returns tool call requests 
 The tool is executed and results are returned to the model 
 The model evaluates the results and continues or completes 
 Let&#x27;s break down each step in more detail. 
 1. Initial Request with Tool Definitions 
 To use tools, the model must be provided with tool definitions. These tool definitions are in JSON schema format and are passed to the model via the tools parameter in the API request. 
 JSON // Sample request body with tool definitions and messages 
 { 
 &quot;tools&quot; : [ 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;get_weather&quot; , 
 &quot;description&quot; : &quot;Get current weather for a location&quot; , 
 &quot;parameters&quot; : { 
 // JSON Schema object 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;location&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;City and state, e.g. San Francisco, CA&quot; 
 } , 
 &quot;unit&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;enum&quot; : [ &quot;celsius&quot; , &quot;fahrenheit&quot; ] 
 } 
 } , 
 &quot;required&quot; : [ &quot;location&quot; ] 
 } 
 } 
 } 
 ] , 
 &quot;messages&quot; : [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a weather assistant. Respond to the user question and use tools if needed to answer the query.&quot; 
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;What&#x27;s the weather in San Francisco?&quot; 
 } 
 ] , 
 } 
 Key fields: 
 name : Function identifier 
 description : Helps the model decide when to use this tool 
 parameters : Function parameters defined as a JSON Schema object. Refer to JSON Schema for schema documentation. 
 2. Model Returns Tool Call Requests 
 When the model decides to use a tool, it returns structured tool calls in the response. The model returns a tool_calls array with the following fields: 
 JSON { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;tool_calls&quot; : [ { 
 &quot;id&quot; : &quot;call_abc123&quot; , 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;get_weather&quot; , 
 &quot;arguments&quot; : &quot;{\&quot;location\&quot;: \&quot;San Francisco, CA\&quot;, \&quot;unit\&quot;: \&quot;fahrenheit\&quot;}&quot; 
 } 
 } ] 
 } 
 Key fields: 
 id : Unique identifier you&#x27;ll reference when returning results 
 function.name : Which tool to execute 
 function.arguments : JSON string of arguments (needs parsing) 
 3. Tool Execution and Results 
 Application code will then execute the tool and create a new message with the results. This new message is appended to the conversation and sent back to the model. 
 JSON { 
 &quot;role&quot; : &quot;tool&quot; , 
 # must match the `id` from the assistant&#x27;s `tool_calls`
 &quot;tool_call_id&quot; : &quot;call_abc123&quot; , 
 &quot;name&quot; : &quot;get_weather&quot; , 
 &quot;content&quot; : &quot;{\&quot;temperature\&quot;: 72, \&quot;condition\&quot;: \&quot;sunny\&quot;, \&quot;unit\&quot;: \&quot;fahrenheit\&quot;}&quot; 
 } 
 Key connections: 
 The tool message&#x27;s tool_call_id must match the id from the assistant&#x27;s tool_calls 
 content can be any string value. Different tools may return different types of data. 
 The updated messages array is then sent back to the model for the next step 
 4. Model Evaluates Results and Decides Next Steps 
 The model is then provided with the updated messages array: 
 JSON [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;What&#x27;s the weather in San Francisco?&quot; 
 } , 
 { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;tool_calls&quot; : [ { 
 &quot;id&quot; : &quot;call_abc123&quot; , 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;get_weather&quot; , 
 &quot;arguments&quot; : &quot;{\&quot;location\&quot;: \&quot;San Francisco, CA\&quot;, \&quot;unit\&quot;: \&quot;fahrenheit\&quot;}&quot; 
 } 
 } ] 
 } , 
 { 
 &quot;role&quot; : &quot;tool&quot; , 
 &quot;tool_call_id&quot; : &quot;call_abc123&quot; , 
 &quot;name&quot; : &quot;get_weather&quot; , 
 &quot;content&quot; : &quot;{\&quot;temperature\&quot;: 72, \&quot;condition\&quot;: \&quot;sunny\&quot;, \&quot;unit\&quot;: \&quot;fahrenheit\&quot;}&quot; 
 } 
 ] 
 The model then analyzes the tool results and either: 
 Returns a final answer (no more tool_calls ) 
 Returns more tool call requests (loop continues) 
 JSON { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;content&quot; : &quot;The weather in San Francisco is sunny and 72 degrees Fahrenheit.&quot; 
 } 
 This tool-calling sequence is normally implemented in your application code, but Groq suports a number of ways to call tools server-side which allow your application code to remain simple while still allowing you to use tools. 
 Supported Models 
 All models hosted on Groq support tool use, and in general, we recommend the latest models for improved tool use capabilities: 
 Model ID Local &amp; Remote Tool Use Support? Parallel Tool Use Support? JSON Mode Support? Built-In Tools Support? openai/gpt-oss-20b Yes ✅ No ❌ Yes ✅ Yes ✅ openai/gpt-oss-120b Yes ✅ No ❌ Yes ✅ Yes ✅ openai/gpt-oss-safeguard-20b Yes ✅ No ❌ Yes ✅ No ❌ qwen/qwen3.6-27b Yes ✅ Yes ✅ Yes ✅ No ❌ qwen/qwen3.8-27b Yes ✅ No ❌ Yes ✅ No ❌ minimaxai/minimax-m2.7 Yes ✅ Yes ✅ Yes ✅ No ❌ llama-3.3-70b-versatile Yes ✅ Yes ✅ Yes ✅ No ❌ llama-3.1-8b-instant Yes ✅ Yes ✅ Yes ✅ No ❌ groq/compound No ❌ N/A Yes ✅ Yes ✅ groq/compound-mini No ❌ N/A Yes ✅ Yes ✅ 
 How to Use Tools on the Groq API 
 Groq supports three distinct patterns for tool use, each suited for different use cases: Groq built-in tools, remote tool calling via MCP servers, and local tool calling. 
 1. Groq Built-In Tools 
 Groq maintains a set of pre-built tools like web search, code execution, and website visiting that execute entirely on Groq&#x27;s infrastructure. These tools require minimal configuration and no tool orchestration on your end. With one API call, you get a capable, real-time AI agent. All tool calls happen in a single API call – when provided configured to have access to built-in tools, the model autonomously calls built-in tools and handles the entire agentic loop internally. 
 Ideal for: 
 Drop-in developer experience with zero setup 
 Applications requiring the lowest possible latency 
 Web search and browsing capabilities 
 Safe code execution environments 
 Single-call agentic responses 
 Supported models: 
 groq/compound and groq/compound-mini 
 openai/gpt-oss-20b and openai/gpt-oss-120b 
 Groq Built-In Tools Guide For more details, this guide covers how to use Groq&#x27;s server-side tools for instant agentic capabilities 
 2. Remote Tool Calling with MCP 
 The Model Context Protocol (MCP) is an open standard that allows models to connect to and execute external tools. Each MCP server hosts a set of tools, providing endpoints to fetch their definitions and execute them without requiring the end user to implement the underlying tool logic. 
 Groq supports MCP tool discovery and execution server-side via remote tool calling. Similar to built-in tools, this allows you to use third-party tools with minimal configuration and no tool orchestration on your end. To use remote tools, you provide an MCP server configuration, which includes the MCP server URL and authentication headers. Groq&#x27;s servers will connect to the MCP server, discover the available tools, pass them to the model, and execute any tools that are called server-side — all in a single API call. 
 Ideal for: 
 Standardized integrations (GitHub, databases, external APIs) 
 Tools maintained by third parties 
 Sharing tools across multiple applications 
 Accessing tools without hosting infrastructure 
 Remote Tools and MCP Guide For more details, this guide covers how to use MCP servers for third-party tool integrations 
 3. Local Tool Calling (Function Calling) 
 If you want the most control over tool execution logic, you can implement local tool calling. To do this, you manually write a set of functions and corresonding tool definitions. The tool definitions are provided to the model at inference time, and the model returns structured tool call requests (example provided above; a JSON object specifying which function to call and what arguments to use). Your application code then executes the function that corresponds to the tool call request locally and sends the results back to the model for the final response. 
 These functions can connect to external resources such as databases, APIs, and external services, but they are &quot;local&quot; in the sense that they are executed on the same machine as the application code. You can also connect to MCP servers locally to execute tools. This requires implementing code to discover tools from the MCP server, provide them to the model at inference time, routing any tool calls back to the MCP server for execution, and finally returning the results back to the model for the final response. 
 Ideal for: 
 Custom business logic 
 Internal APIs and databases 
 Proprietary workflows 
 Fine-grained control over security and execution 
 Local Tool Calling Guide Learn how to implement custom tools that execute in your application code 
 Comparison 
 Pattern You Provide Execution Location Orchestration API Calls Built-In List of enabled built-in tools Groq servers Groq manages Single call Remote MCP MCP server URL + auth MCP server Groq manages Single call Local Tool definitions + implementation Your code You manage loop Multiple (2+ per iteration) 
 Parallel Tool Use 
 Many models support parallel tool use , where multiple tools can be called simultaneously in a single request. This is crucial for efficient agentic systems: 
 Without parallel tool use: 
 curl Query: &quot;What&#x27;s the weather in NYC and LA?&quot;
 Call 1: get_weather(location=&quot;NYC&quot;) → Wait for result
 Call 2: get_weather(location=&quot;LA&quot;) → Wait for result
 Final response 
 With parallel tool use: 
 curl Query: &quot;What&#x27;s the weather in NYC and LA?&quot;
 Call 1: [get_weather(location=&quot;NYC&quot;), get_weather(location=&quot;LA&quot;)]
 Both execute simultaneously → Final response 
 Parallel tool use dramatically reduces latency for queries that require multiple tool calls. 
 Why Groq&#x27;s Speed Matters 
 Because agentic workflows involve multiple inference calls, using Groq&#x27;s fast inference can significantly improve the user experience of an agentic application: 
 Single tool call workflow : 2 inference calls instead of 1 (first call to determine if a tool call is needed, second call to send the tool call results back to the model) 
 Multi-tool workflow : 3-5+ inference calls 
 Complex agent loops : 10+ inference calls 
 With traditional inference speeds of 10-30 tokens/second, multi-tool workflows can feel painfully slow. Groq&#x27;s inference speed of 300-1,000+ tokens/second makes these agentic experiences feel instantaneous . 
 What&#x27;s Next? 
 Now that you understand the fundamentals of tool use and agentic systems, explore the specific patterns for using tools on the Groq API: 
 Groq Built-In Tools Use web search, code execution, and more without setup Remote Tools and MCP Connect to MCP servers for standardized tool integrations Local Tool Calling Define and execute custom tools in your application code Compound Systems Purpose-built agentic systems with built-in tools and orchestration Was this page helpful? Yes No Suggest Edits On this page 