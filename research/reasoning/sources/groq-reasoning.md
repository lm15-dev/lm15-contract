 Reasoning - GroqDocs Docs Login Playground API Keys Dashboard Docs Log In Documentation Docs API Reference Search Docs Getting Started Overview Quickstart Models OpenAI Compatibility Responses API Rate Limits Templates API Reference Core Features Text Generation Speech to Text Text to Speech Orpheus OCR and Image Recognition Reasoning Content Moderation Structured Outputs Prompt Caching Tools &amp; Integrations Tool Use Overview Groq Built-In Tools Web Search Visit Website Code Execution Wolfram Alpha Browser Search (GPT OSS Models) Remote Tools and MCP Connectors Local Tool Calling Integrations Catalog Coding with Groq Factory Droid OpenCode Kilo Code Roo Code Cline Compound (Agentic AI) Overview Built-In Tools Systems Use Cases Guides Prompting Guide Basics Patterns Model Migration Assistant Message Prefilling Service Tiers Service Tiers Performance Tier Flex Processing Batch Processing Advanced LoRA Inference Production Readiness Production Checklist Optimizing Latency Security Onboarding Prometheus Metrics Account and Console Spend Limits Projects Model Permissions Billing FAQs Your Data Developer Resources SDK Libraries Groq Badge Developer Community OpenBench Error Codes Changelog Legal Policies &amp; Notices Search Docs API Reference Getting Started Overview Quickstart Models OpenAI Compatibility Responses API Rate Limits Templates API Reference Core Features Text Generation Speech to Text Text to Speech Orpheus OCR and Image Recognition Reasoning Content Moderation Structured Outputs Prompt Caching Tools &amp; Integrations Tool Use Overview Groq Built-In Tools Web Search Visit Website Code Execution Wolfram Alpha Browser Search (GPT OSS Models) Remote Tools and MCP Connectors Local Tool Calling Integrations Catalog Coding with Groq Factory Droid OpenCode Kilo Code Roo Code Cline Compound (Agentic AI) Overview Built-In Tools Systems Use Cases Guides Prompting Guide Basics Patterns Model Migration Assistant Message Prefilling Service Tiers Service Tiers Performance Tier Flex Processing Batch Processing Advanced LoRA Inference Production Readiness Production Checklist Optimizing Latency Security Onboarding Prometheus Metrics Account and Console Spend Limits Projects Model Permissions Billing FAQs Your Data Developer Resources SDK Libraries Groq Badge Developer Community OpenBench Error Codes Changelog Legal Policies &amp; Notices Reasoning Copy page 
 Reasoning models excel at complex problem-solving tasks that require step-by-step analysis, logical deduction, and structured thinking and solution validation. With Groq inference speed, these types of models
can deliver instant reasoning capabilities critical for real-time applications. 
 Why Speed Matters for Reasoning 
 Reasoning models are capable of complex decision making with explicit reasoning chains that are part of the token output and used for decision-making, which make low-latency and fast inference essential.
Complex problems often require multiple chains of reasoning tokens where each step build on previous results. Low latency compounds benefits across reasoning chains and shaves off minutes of reasoning to a response in seconds. 
 Supported Models 
 Model ID Model openai/gpt-oss-20b OpenAI GPT-OSS 20B openai/gpt-oss-120b OpenAI GPT-OSS 120B openai/gpt-oss-safeguard-20b OpenAI GPT-OSS-Safeguard 20B qwen/qwen3.6-27b Qwen 3.6 27B qwen/qwen3.8-27b Qwen 3.8 27B minimaxai/minimax-m2.7 MiniMax M2.7 
 Reasoning Format 
 Groq API supports explicit reasoning formats through the reasoning_format parameter, giving you fine-grained control over how the model&#x27;s
reasoning process is presented. This is particularly valuable for valid JSON outputs, debugging, and understanding the model&#x27;s decision-making process. 
 Note: The format defaults to raw or parsed when JSON mode or tool use are enabled as those modes do not support raw . If reasoning is
explicitly set to raw with JSON mode or tool use enabled, we will return a 400 error. 
 Options for Reasoning Format 
 reasoning_format Options Description parsed Separates reasoning into a dedicated message.reasoning field while keeping the response concise. raw Includes reasoning within &lt;think&gt; tags in the main text content. hidden Returns only the final answer. 
 Including Reasoning in the Response 
 You can also control whether reasoning is included in the response by setting the include_reasoning parameter. 
 include_reasoning Options Description true Includes the reasoning in a dedicated message.reasoning field. This is the default behavior. false Excludes reasoning from the response. 
 Note: The include_reasoning parameter cannot be used together with reasoning_format . These parameters are mutually exclusive. 
 Reasoning Effort 
 Options for Reasoning Effort (Qwen 3.6 27B) 
 The reasoning_effort parameter controls the level of effort the model will put into reasoning. Qwen 3.6 27B supports the following options: 
 reasoning_effort Options Description none Disable reasoning. The model will not use any reasoning tokens. default Enable reasoning. 
 Options for Reasoning Effort (Qwen 3.8 27B) 
 Qwen 3.8 27B supports the following options: 
 reasoning_effort Options Description none Disable reasoning. The model will not use any reasoning tokens. default Enable reasoning. low Enable reasoning with a low effort level. medium Enable reasoning with a medium effort level. high Enable reasoning with a high effort level. 
 Options for Reasoning Effort (GPT-OSS) 
 The reasoning_effort parameter controls the level of effort the model will put into reasoning. This is only supported by GPT-OSS 20B and GPT-OSS 120B . 
 reasoning_effort Options Description low Low effort reasoning. The model will use a small number of reasoning tokens. medium Medium effort reasoning. The model will use a moderate number of reasoning tokens. high High effort reasoning. The model will use a large number of reasoning tokens. 
 Quick Start 
 Get started with reasoning models using this basic example that demonstrates how to make a simple API call for complex problem-solving tasks. 
 Python import Groq from &#x27;groq-sdk&#x27;;
const client = new Groq();
const completion = await client.chat.completions.create({
 model: &quot;openai/gpt-oss-20b&quot;,
 messages: [
 {
 role: &quot;user&quot;,
 content: &quot;How many r&#x27;s are in the word strawberry?&quot;
 }
 ],
 temperature: 0.6,
 max_completion_tokens: 1024,
 top_p: 0.95,
 stream: true
});
for await (const chunk of completion) {
 process.stdout.write(chunk.choices[0].delta.content || &quot;&quot;);
} from groq import Groq
 client = Groq ( ) 
 completion = client . chat . completions . create ( 
 model = &quot;openai/gpt-oss-20b&quot; , 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;How many r&#x27;s are in the word strawberry?&quot; 
 } 
 ] , 
 temperature = 0.6 , 
 max_completion_tokens = 1024 , 
 top_p = 0.95 , 
 stream = True 
 ) 
 for chunk in completion : 
 print ( chunk . choices [ 0 ] . delta . content or &quot;&quot; , end = &quot;&quot; ) curl &quot;https://api.groq.com/openai/v1/chat/completions&quot; \
 -X POST \
 -H &quot;Content-Type: application/json&quot; \
 -H &quot;Authorization: Bearer ${GROQ_API_KEY}&quot; \
 -d &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How many r&#x27;\&#x27;&#x27;s are in the word strawberry?&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;temperature&quot;: 0.6,
 &quot;max_completion_tokens&quot;: 4096,
 &quot;top_p&quot;: 0.95,
 &quot;stream&quot;: true,
 &quot;stop&quot;: null
 }&#x27; 
 Quick Start with Tool Use 
 This example shows how to combine reasoning models with function calling to create intelligent agents that can perform actions while explaining their thought process. 
 curl curl https://api.groq.com//openai/v1/chat/completions -s \ 
 -H &quot;authorization: bearer $GROQ_API_KEY &quot; \ 
 -d &#x27;{
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;What is the weather like in Paris today?&quot;
 }
 ],
 &quot;tools&quot;: [
 {
 &quot;type&quot;: &quot;function&quot;,
 &quot;function&quot;: {
 &quot;name&quot;: &quot;get_weather&quot;,
 &quot;description&quot;: &quot;Get current temperature for a given location.&quot;,
 &quot;parameters&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;location&quot;: {
 &quot;type&quot;: &quot;string&quot;,
 &quot;description&quot;: &quot;City and country e.g. Bogotá, Colombia&quot;
 }
 },
 &quot;required&quot;: [
 &quot;location&quot;
 ],
 &quot;additionalProperties&quot;: false
 },
 &quot;strict&quot;: true
 }
 }
 ]}&#x27; 
 Recommended Configuration Parameters 
 Parameter Default Range Description messages - - Array of message objects. Important: Avoid system prompts - include all instructions in the user message! temperature 0.6 0.0 - 2.0 Controls randomness in responses. Lower values make responses more deterministic. Recommended range: 0.5-0.7 to prevent repetitions or incoherent outputs max_completion_tokens 1024 - Maximum length of model&#x27;s response. Default may be too low for complex reasoning - consider increasing for detailed step-by-step solutions top_p 0.95 0.0 - 1.0 Controls diversity of token selection stream false boolean Enables response streaming. Recommended for interactive reasoning tasks stop null string/array Custom stop sequences seed null integer Set for reproducible results. Important for benchmarking - run multiple tests with different seeds response_format {type: &quot;text&quot;} {type: &quot;json_object&quot;} or {type: &quot;text&quot;} Set to json_object type for structured output. reasoning_format raw &quot;parsed&quot; , &quot;raw&quot; , &quot;hidden&quot; Controls how model reasoning is presented in the response. Must be set to either parsed or hidden when using tool calling or JSON mode. reasoning_effort default &quot;none&quot; , &quot;default&quot; , &quot;low&quot; , &quot;medium&quot; , &quot;high&quot; Controls the level of effort the model will put into reasoning. none and default are only supported by Qwen 3.6 27B and Qwen 3.8 27B . low , medium , and high are only supported by GPT-OSS 20B , GPT-OSS 120B , and Qwen 3.8 27B . 
 Accessing Reasoning Content 
 Accessing the reasoning content in the response is dependent on the model and the reasoning format you are using. See the examples below for more details and refer to the Reasoning Format section for more information. 
 Non-GPT-OSS Models 
 Raw Parsed Hidden When using raw reasoning format, the reasoning content is accessible in the main text content of assistant responses within &lt;think&gt; tags. This example demonstrates making a request with reasoning_format set to raw to see the model&#x27;s internal thinking process alongside the final answer. Python import { Groq } from &#x27;groq-sdk&#x27;;
const groq = new Groq();
const chatCompletion = await groq.chat.completions.create({
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;qwen/qwen3.6-27b&quot;,
 &quot;stream&quot;: false,
 &quot;reasoning_format&quot;: &quot;raw&quot;
});
console.log(chatCompletion.choices[0].message); from groq import Groq
 client = Groq ( ) 
 chat_completion = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;How do airplanes fly? Be concise.&quot; 
 } 
 ] , 
 model = &quot;qwen/qwen3.6-27b&quot; , 
 stream = False , 
 reasoning_format = &quot;raw&quot; 
 ) 
 print ( chat_completion . choices [ 0 ] . message ) curl https://api.groq.com/openai/v1/chat/completions -s \
 -H &quot;authorization: bearer $GROQ_API_KEY&quot; \
 -H &quot;content-type: application/json&quot; \
 -d &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;qwen/qwen3.6-27b&quot;,
 &quot;stream&quot;: false,
 &quot;reasoning_format&quot;: &quot;raw&quot;
 }&#x27; Example Output (response.choices[0].message) JSON { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;content&quot; : &quot;&lt;think&gt;Okay, the user is asking how airplanes fly and wants a concise answer. Let me start by recalling the basics of flight mechanics. First, lift is essential. Airplanes generate lift with their wings. The shape of the wing, or airfoil, causes air to move faster over the top, creating lower pressure compared to the bottom. This pressure difference lifts the plane. But wait, I should mention Bernoulli&#x27;s principle here. Also, angle of attack affects lift by directing airflow downward, which pushes the wing up by Newton&#x27;s third law. Both factors contribute to lift. Thrust is needed to move the plane forward, providing the speed necessary for lift. Engines like jet engines or propellers generate thrust. Drag is the opposing force; the plane must overcome it. Stability and control come into play too—ailerons, rudder, elevator for maneuvers. Wait, the user wants it concise. Maybe I should prioritize the main points: lift due to wings&#x27; shape and angle, thrust from engines, and balance forces. Avoid getting too technical with equations but mention the key components. Also, mention that controlled flight involves managing these forces. Let me make sure I&#x27;m not missing anything crucial. Maybe lift, thrust, drag, weight—those are the four forces. But since the user wants it brief, I can simplify to the main elements without listing all four forces. Double-check if Bernoulli&#x27;s principle is accurate here. Some debates exist about its role versus Newton&#x27;s laws, but a simplified explanation is acceptable here. Also, mention that the engines provide forward motion, which is crucial for sustaining lift. Putting it all together: airplanes fly by generating lift through their wings&#x27; design and angle of attack, using engines for thrust to maintain speed, and controlling flight with adjustable surfaces. Should be concise and cover the essentials.&lt;/think&gt;Airplanes fly by generating **lift** through the shape of their wings (airfoils), which causes faster airflow over the top and slower air underneath, creating a pressure difference. **Thrust** from engines (or propellers) propels them forward, countering **drag**, while **control surfaces** (ailerons, rudder, elevator) adjust airflow for stability and direction. Lift must overcome **weight** (gravity) to stay aloft.&quot; 
 } When using parsed reasoning format, the model&#x27;s reasoning is separated into a dedicated reasoning field, making it easier to access both the final answer and the thinking process programmatically. This format is ideal for applications that need to process or display reasoning content separately from the main response. Python import { Groq } from &#x27;groq-sdk&#x27;;
const groq = new Groq();
const chatCompletion = await groq.chat.completions.create({
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;qwen/qwen3.6-27b&quot;,
 &quot;stream&quot;: false,
 &quot;reasoning_format&quot;: &quot;parsed&quot;
});
console.log(chatCompletion.choices[0].message); from groq import Groq
 client = Groq ( ) 
 chat_completion = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;How do airplanes fly? Be concise.&quot; 
 } 
 ] , 
 model = &quot;qwen/qwen3.6-27b&quot; , 
 stream = False , 
 reasoning_format = &quot;parsed&quot; 
 ) 
 print ( chat_completion . choices [ 0 ] . message ) curl https://api.groq.com/openai/v1/chat/completions -s \
 -H &quot;authorization: bearer $GROQ_API_KEY&quot; \
 -H &quot;content-type: application/json&quot; \
 -d &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;qwen/qwen3.6-27b&quot;,
 &quot;stream&quot;: false,
 &quot;reasoning_format&quot;: &quot;parsed&quot;
 }&#x27; Example Output (response.choices[0].message) JSON { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;content&quot; : &quot;Airplanes fly by generating **lift** through their wings&#x27; shape (airfoils), creating a pressure difference (lower pressure above, higher below). **Thrust** from engines overcomes drag, propelling the plane forward. Controlled movement (pitch, roll, yaw) adjusts lift and direction. In short: **lift + thrust &gt; weight + drag** enables flight.&quot; , 
 &quot;reasoning&quot; : &quot;Okay, the user is asking how airplanes fly and wants a concise answer. Let me break this down. First, I need to recall the basic principles of flight. The main concepts are lift, thrust, drag, and weight. Lift is generated by the wings, right? The shape of the wing causes air to move faster over the top, creating lower pressure compared to the bottom, which lifts the plane. Then there&#x27;s thrust from the engines, which pushes the plane forward, overcoming drag. Drag is the resistance from the air. The pilot controls the plane&#x27;s direction with surfaces like ailerons, elevators, and rudders. Also, Newton&#x27;s third law comes into play with the engines pushing air backward, propelling the plane forward. Wait, the question is asking for conciseness. I should make sure not to include too much detail. Maybe mention the four forces, the wing&#x27;s shape (airfoil), and how the engines generate thrust. Avoid getting into too much depth about different types of engines or control surfaces unless necessary. Is there anything else important? Maybe the angle of attack? Or the balance between the forces. But keeping it simple. The answer should be brief enough. Let me check the key points again: lift due to wing shape causing pressure difference, thrust overcoming drag, controlled movement. That should cover it without being too technical.&quot; , 
 } When using hidden reasoning format, only the final answer is returned without any visible reasoning content. This is useful for applications where you want the benefits of reasoning models but don&#x27;t need to expose the thinking process to end users. The model will still reason, but the reasoning content will not be returned in the response. Python import { Groq } from &#x27;groq-sdk&#x27;;
const groq = new Groq();
const chatCompletion = await groq.chat.completions.create({
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;qwen/qwen3.6-27b&quot;,
 &quot;stream&quot;: false,
 &quot;reasoning_format&quot;: &quot;hidden&quot;
});
console.log(chatCompletion.choices[0].message); from groq import Groq
 client = Groq ( ) 
 chat_completion = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;How do airplanes fly? Be concise.&quot; 
 } 
 ] , 
 model = &quot;qwen/qwen3.6-27b&quot; , 
 stream = False , 
 reasoning_format = &quot;hidden&quot; 
 ) 
 print ( chat_completion . choices [ 0 ] . message ) curl https://api.groq.com/openai/v1/chat/completions -s \
 -H &quot;authorization: bearer $GROQ_API_KEY&quot; \
 -H &quot;content-type: application/json&quot; \
 -d &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;qwen/qwen3.6-27b&quot;,
 &quot;stream&quot;: false,
 &quot;reasoning_format&quot;: &quot;hidden&quot;
 }&#x27; Example Output (response.choices[0].message) JSON { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;content&quot; : &quot;Airplanes fly by generating **lift** via airfoil-shaped wings, which create a pressure difference (Bernoulli’s principle) as air moves faster over the curved top surface. **Thrust** from engines overcomes air **drag**, maintaining forward motion to sustain lift. Control surfaces (ailerons, elevators, rudder) adjust **direction** and **altitude**, balancing **weight** (gravity) and lift for stable flight.&quot; 
 } 
 GPT-OSS Models 
 With openai/gpt-oss-20b and openai/gpt-oss-120b , the reasoning_format parameter is not supported.
By default, these models will include reasoning content in the reasoning field of the assistant response.
You can also control whether reasoning is included in the response by setting the include_reasoning parameter. 
 Reasoning Excluded Reasoning Included Reasoning Included (High) Python import { Groq } from &#x27;groq-sdk&#x27;;
const groq = new Groq();
const chatCompletion = await groq.chat.completions.create({
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;stream&quot;: false,
 &quot;include_reasoning&quot;: false
});
console.log(chatCompletion.choices[0].message); from groq import Groq
 client = Groq ( ) 
 chat_completion = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;How do airplanes fly? Be concise.&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-20b&quot; , 
 stream = False , 
 include_reasoning = False 
 ) 
 print ( chat_completion . choices [ 0 ] . message ) curl https://api.groq.com/openai/v1/chat/completions -s \
 -H &quot;authorization: bearer $GROQ_API_KEY&quot; \
 -H &quot;content-type: application/json&quot; \
 -d &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;stream&quot;: false,
 &quot;include_reasoning&quot;: false
 }&#x27; Example Output (response.choices[0].message) JSON { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;content&quot; : &quot;Airplanes fly because their wings are shaped like airfoils that slice the air and produce lift: air travels faster over the curved upper surface (Bernoulli principle) and/or is deflected downward, creating an upward lift force that exceeds gravity. Engines provide thrust to overcome drag and keep the aircraft moving forward, so lift can keep it aloft. Control surfaces then balance lift, weight, thrust, and drag to steer and maintain flight.&quot; 
 } Python import { Groq } from &#x27;groq-sdk&#x27;;
const groq = new Groq();
const chatCompletion = await groq.chat.completions.create({
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;stream&quot;: false
});
console.log(chatCompletion.choices[0].message); from groq import Groq
 client = Groq ( ) 
 chat_completion = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;How do airplanes fly? Be concise.&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-20b&quot; , 
 stream = False 
 ) 
 print ( chat_completion . choices [ 0 ] . message ) curl https://api.groq.com/openai/v1/chat/completions -s \
 -H &quot;authorization: bearer $GROQ_API_KEY&quot; \
 -H &quot;content-type: application/json&quot; \
 -d &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;stream&quot;: false
 }&#x27; Example Output (response.choices[0].message) JSON { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;content&quot; : &quot;Airplanes fly because their wings are shaped like airfoils that slice the air and produce lift: air travels faster over the curved upper surface (Bernoulli principle) and/or is deflected downward, creating an upward lift force that exceeds gravity. Engines provide thrust to overcome drag and keep the aircraft moving forward, so lift can keep it aloft. Control surfaces then balance lift, weight, thrust, and drag to steer and maintain flight.&quot; , 
 &quot;reasoning&quot; : &quot;We need concise answer: planes fly because of lift generated from wings due to airfoil shape, Bernoulli, angle of attack, thrust vs drag. So concisely explain: plane wings shape produces lift, engines provide thrust, controls manage pitch etc. Also mention aerodynamics: lift &gt; weight, thrust &gt; drag. So answer concise. Let&#x27;s prepare: \&quot;airplane wings produce lift due to airfoil shape... engine thrust propels...\&quot; etc.&quot; 
 } Python import { Groq } from &#x27;groq-sdk&#x27;;
const groq = new Groq();
const chatCompletion = await groq.chat.completions.create({
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;reasoning_effort&quot;: &quot;high&quot;,
 &quot;include_reasoning&quot;: true,
 &quot;stream&quot;: false
});
console.log(chatCompletion.choices[0].message); from groq import Groq
 client = Groq ( ) 
 chat_completion = client . chat . completions . create ( 
 messages = [ 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;How do airplanes fly? Be concise.&quot; 
 } 
 ] , 
 model = &quot;openai/gpt-oss-20b&quot; , 
 reasoning_effort = &quot;high&quot; , 
 include_reasoning = True , 
 stream = False 
 ) 
 print ( chat_completion . choices [ 0 ] . message ) curl https://api.groq.com/openai/v1/chat/completions -s \
 -H &quot;authorization: bearer $GROQ_API_KEY&quot; \
 -H &quot;content-type: application/json&quot; \
 -d &#x27;{
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;How do airplanes fly? Be concise.&quot;
 }
 ],
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;reasoning_effort&quot;: &quot;high&quot;,
 &quot;include_reasoning&quot;: true,
 &quot;stream&quot;: false
 }&#x27; Example Output (response.choices[0].message) JSON { 
 &quot;role&quot; : &quot;assistant&quot; , 
 &quot;content&quot; : &quot;Planes fly because their wings, shaped like airfoils, move through the air to create a pressure difference that produces lift. Engines generate thrust to overcome drag, while lift balances the plane’s weight. When lift equals weight and thrust equals drag, the aircraft flies level; if lift exceeds weight it climbs, and if thrust exceeds drag it accelerates.&quot; , 
 &quot;reasoning&quot; : &quot;The user asks: How do airplanes fly? Be concise. The user wants a concise answer. I must answer succinctly. The answer: basically lift, thrust, drag, weight. The plane&#x27;s wings generate lift due to Bernoulli or angle of attack, engines produce thrust. Balanced forces. Maybe mention lift &gt; weight for climb, etc. Or just mention wings shape, airfoil, Bernoulli&#x27;s principle, Newton&#x27;s third law, lift, thrust, etc. Keep concise. We can give a short paragraph: Airplanes fly because the wings are shaped to produce lift, the engines generate thrust, and the plane&#x27;s weight pulls down; lift must balance weight, and thrust must overcome drag. That&#x27;s it. Should be concise. Let&#x27;s answer in maybe one or two sentences: An airplane generates lift by moving through air over its wing-shaped surfaces, creating a pressure difference; engines produce thrust to counteract drag, and the lift force balances weight, allowing flight. That is concise. Alternatively: Planes fly because the wings produce lift (pressure difference due to shape and motion), engines provide thrust, and the aircraft&#x27;s weight pulls downward; lift equals weight and thrust equals drag for level flight. Thus answer.&quot; 
 } 
 Optimizing Performance 
 Temperature and Token Management 
 The model performs best with temperature settings between 0.5-0.7, with lower values (closer to 0.5) producing more consistent mathematical proofs and higher values allowing for more creative problem-solving approaches. Monitor and adjust your token usage based on the complexity of your reasoning tasks - while the default max_completion_tokens is 1024, complex proofs may require higher limits. 
 Prompt Engineering 
 To ensure accurate, step-by-step reasoning while maintaining high performance: 
 DeepSeek-R1 works best when all instructions are included directly in user messages rather than system prompts. 
 Structure your prompts to request explicit validation steps and intermediate calculations. 
 Avoid few-shot prompting and go for zero-shot prompting only. 
 Was this page helpful? Yes No Suggest Edits On this page 