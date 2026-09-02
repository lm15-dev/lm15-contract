 Structured Outputs - GroqDocs Docs Login Playground API Keys Dashboard Docs Log In Documentation Docs API Reference Search Docs Getting Started Overview Quickstart Models OpenAI Compatibility Responses API Rate Limits Templates API Reference Core Features Text Generation Speech to Text Text to Speech Orpheus OCR and Image Recognition Reasoning Content Moderation Structured Outputs Prompt Caching Tools &amp; Integrations Tool Use Overview Groq Built-In Tools Web Search Visit Website Code Execution Wolfram Alpha Browser Search (GPT OSS Models) Remote Tools and MCP Connectors Local Tool Calling Integrations Catalog Coding with Groq Factory Droid OpenCode Kilo Code Roo Code Cline Compound (Agentic AI) Overview Built-In Tools Systems Use Cases Guides Prompting Guide Basics Patterns Model Migration Assistant Message Prefilling Service Tiers Service Tiers Performance Tier Flex Processing Batch Processing Advanced LoRA Inference Production Readiness Production Checklist Optimizing Latency Security Onboarding Prometheus Metrics Account and Console Spend Limits Projects Model Permissions Billing FAQs Your Data Developer Resources SDK Libraries Groq Badge Developer Community OpenBench Error Codes Changelog Legal Policies &amp; Notices Search Docs API Reference Getting Started Overview Quickstart Models OpenAI Compatibility Responses API Rate Limits Templates API Reference Core Features Text Generation Speech to Text Text to Speech Orpheus OCR and Image Recognition Reasoning Content Moderation Structured Outputs Prompt Caching Tools &amp; Integrations Tool Use Overview Groq Built-In Tools Web Search Visit Website Code Execution Wolfram Alpha Browser Search (GPT OSS Models) Remote Tools and MCP Connectors Local Tool Calling Integrations Catalog Coding with Groq Factory Droid OpenCode Kilo Code Roo Code Cline Compound (Agentic AI) Overview Built-In Tools Systems Use Cases Guides Prompting Guide Basics Patterns Model Migration Assistant Message Prefilling Service Tiers Service Tiers Performance Tier Flex Processing Batch Processing Advanced LoRA Inference Production Readiness Production Checklist Optimizing Latency Security Onboarding Prometheus Metrics Account and Console Spend Limits Projects Model Permissions Billing FAQs Your Data Developer Resources SDK Libraries Groq Badge Developer Community OpenBench Error Codes Changelog Legal Policies &amp; Notices Structured Outputs Copy page 
 Guarantee model responses strictly conform to your JSON schema for reliable, type-safe data structures. 
 Introduction 
 Structured Outputs is a feature that ensures your model responses conform to your provided JSON Schema . The feature offers two modes with different guarantees and requirements: 
 Best-effort Mode Strict Mode Strict Mode ( strict: true ) With strict: true , the model uses constrained decoding to guarantee that the output will always match your schema exactly. This mode: 
 Never errors or produces invalid JSON - The model is constrained at the token level to only generate valid outputs 
 100% schema adherence - Every response will perfectly match your JSON Schema 
 Stricter requirements - All fields must be required and objects must set additionalProperties: false 
 Limited model support - Currently only available on select models (see Supported Models ) - we&#x27;re working on adding more models in the future. If you run into 400 errors, we&#x27;d appreciate repros posted to our developer forum . 
 This is the recommended mode when available, as it provides the strongest guarantees for production applications. Example usage: JSON { 
 &quot;response_format&quot; : { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;schema_name&quot; , 
 &quot;strict&quot; : true , 
 &quot;schema&quot; : { ... } 
 } 
 } 
 } Best-effort Mode ( strict: false ) With strict: false (the default behavior), the model attempts to match your schema but without hard constraints: 
 Valid JSON, but schema adherence not guaranteed - May produce valid JSON that does not match your schema (for example, wrong field types or missing/extra fields) 
 Possible errors and malformed output - Can sometimes produce malformed JSON syntax or trigger 400 errors due to schema validation failures 
 Fewer requirements - More flexible schema constraints, such as optional fields 
 Broader model support - Available on all models that support Structured Outputs 
 This mode is suitable when you need structured outputs but can handle occasional validation errors with retry logic. Example usage: JSON { 
 &quot;response_format&quot; : { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;schema_name&quot; , 
 &quot;strict&quot; : false , // or omit this field (defaults to false) 
 &quot;schema&quot; : { ... } 
 } 
 } 
 } 
 Not sure which mode to use? See Choosing Between Strict and Best-effort Mode for a detailed comparison. 
 Key benefits of Structured Outputs: 
 Type-safe responses: Reduce validation and retry logic for malformed outputs 
 Programmatic refusal detection: Detect safety-based model refusals programmatically 
 Simplified prompting: Less complex prompts needed for consistent formatting 
 In addition to supporting Structured Outputs in our API, our SDKs also enable you to easily define your schemas with Pydantic and Zod to ensure further type safety. The examples below show how to extract structured information from unstructured text. 
 Supported models 
 Structured Outputs is available in two modes: strict: true (with constrained decoding) and strict: false (default, best-effort validation). 
 Best-effort Mode Strict Mode Models with Strict Mode ( strict: true ) The following models support strict: true , which uses constrained decoding to guarantee schema-compliant output: Model ID Model openai/gpt-oss-20b GPT-OSS 20B openai/gpt-oss-120b GPT-OSS 120B qwen/qwen3.8-27b Qwen 3.8 27B Models with Best-effort Mode ( strict: false ) The following models support Structured Outputs with strict: false (default), which attempts schema compliance but may occasionally error: Model ID Model openai/gpt-oss-20b GPT-OSS 20B openai/gpt-oss-120b GPT-OSS 120B openai/gpt-oss-safeguard-20b Safety GPT OSS 20B qwen/qwen3.8-27b Qwen 3.8 27B 
 For all other models, you can use JSON Object Mode to get a valid JSON object, though it may not match your schema. 
 Streaming and tool use are not currently supported with Structured Outputs. 
 Getting a structured response from unstructured text 
 Python import Groq from &quot;groq-sdk&quot;;
const groq = new Groq();
const response = await groq.chat.completions.create({
 model: &quot;openai/gpt-oss-20b&quot;,
 messages: [
 { role: &quot;system&quot;, content: &quot;Extract product review information from the text.&quot; },
 {
 role: &quot;user&quot;,
 content: &quot;I bought the UltraSound Headphones last week and I&#x27;m really impressed! The noise cancellation is amazing and the battery lasts all day. Sound quality is crisp and clear. I&#x27;d give it 4.5 out of 5 stars.&quot;,
 },
 ],
 response_format: {
 type: &quot;json_schema&quot;,
 json_schema: {
 name: &quot;product_review&quot;,
 strict: true,
 schema: {
 type: &quot;object&quot;,
 properties: {
 product_name: { type: &quot;string&quot; },
 rating: { type: &quot;number&quot; },
 sentiment: { 
 type: &quot;string&quot;,
 enum: [&quot;positive&quot;, &quot;negative&quot;, &quot;neutral&quot;]
 },
 key_features: { 
 type: &quot;array&quot;,
 items: { type: &quot;string&quot; }
 }
 },
 required: [&quot;product_name&quot;, &quot;rating&quot;, &quot;sentiment&quot;, &quot;key_features&quot;],
 additionalProperties: false
 }
 }
 }
});
const result = JSON.parse(response.choices[0].message.content || &quot;{}&quot;);
console.log(result); from groq import Groq
 import json
 groq = Groq ( ) 
 response = groq . chat . completions . create ( 
 model = &quot;openai/gpt-oss-20b&quot; , 
 messages = [ 
 { &quot;role&quot; : &quot;system&quot; , &quot;content&quot; : &quot;Extract product review information from the text.&quot; } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;I bought the UltraSound Headphones last week and I&#x27;m really impressed! The noise cancellation is amazing and the battery lasts all day. Sound quality is crisp and clear. I&#x27;d give it 4.5 out of 5 stars.&quot; , 
 } , 
 ] , 
 response_format = { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;product_review&quot; , 
 &quot;strict&quot; : True , 
 &quot;schema&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;product_name&quot; : { &quot;type&quot; : &quot;string&quot; } , 
 &quot;rating&quot; : { &quot;type&quot; : &quot;number&quot; } , 
 &quot;sentiment&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;enum&quot; : [ &quot;positive&quot; , &quot;negative&quot; , &quot;neutral&quot; ] 
 } , 
 &quot;key_features&quot; : { 
 &quot;type&quot; : &quot;array&quot; , 
 &quot;items&quot; : { &quot;type&quot; : &quot;string&quot; } 
 } 
 } , 
 &quot;required&quot; : [ &quot;product_name&quot; , &quot;rating&quot; , &quot;sentiment&quot; , &quot;key_features&quot; ] , 
 &quot;additionalProperties&quot; : False 
 } 
 } 
 } 
 ) 
 result = json . loads ( response . choices [ 0 ] . message . content or &quot;{}&quot; ) 
 print ( json . dumps ( result , indent = 2 ) ) curl https://api.groq.com/openai/v1/chat/completions \
 -H &quot;Authorization: Bearer $GROQ_API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &#x27;{
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: &quot;Extract product review information from the text.&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;I bought the UltraSound Headphones last week and I&#x27;\&#x27;&#x27;m really impressed! The noise cancellation is amazing and the battery lasts all day. Sound quality is crisp and clear. I&#x27;\&#x27;&#x27;d give it 4.5 out of 5 stars.&quot;
 }
 ],
 &quot;response_format&quot;: {
 &quot;type&quot;: &quot;json_schema&quot;,
 &quot;json_schema&quot;: {
 &quot;name&quot;: &quot;product_review&quot;,
 &quot;strict&quot;: true,
 &quot;schema&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;product_name&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;rating&quot;: { &quot;type&quot;: &quot;number&quot; },
 &quot;sentiment&quot;: { 
 &quot;type&quot;: &quot;string&quot;,
 &quot;enum&quot;: [&quot;positive&quot;, &quot;negative&quot;, &quot;neutral&quot;]
 },
 &quot;key_features&quot;: { 
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: { &quot;type&quot;: &quot;string&quot; }
 }
 },
 &quot;required&quot;: [&quot;product_name&quot;, &quot;rating&quot;, &quot;sentiment&quot;, &quot;key_features&quot;],
 &quot;additionalProperties&quot;: false
 }
 }
 }
 }&#x27; 
 Example Output JSON { 
 product_name : &#x27;UltraSound Headphones&#x27; , 
 rating : 4.5 , 
 sentiment : &#x27;positive&#x27; , 
 key_features : [ 
 &#x27;amazing noise cancellation&#x27; , 
 &#x27;all-day battery life&#x27; , 
 &#x27;crisp and clear sound quality&#x27;
 ] 
 } 
 Choosing Between Strict and Best-effort Mode 
 Strict Mode ( strict: true ) Best-effort Mode ( strict: false ) Schema adherence Guaranteed - uses constrained decoding Best-effort - generally compliant Error handling Never produces invalid JSON May occasionally 400 errors or produce syntactically valid but schema-invalid JSON Requirements All fields must be required additionalProperties: false required More flexible constraints allowed Model support Limited (GPT-OSS 20B, 120B) All Structured Outputs models When to use Production apps requiring 100% reliability Development, prototyping, or when using unsupported models 
 Recommendation: Use Strict Mode ( strict: true ) when available for production applications. Fall back to Best-effort Mode ( strict: false ) for broader model support or during development. 
 Examples 
 SQL Query Generation Email Classification API Response Validation SQL Query Generation You can generate structured SQL queries from natural language descriptions, helping ensure proper syntax and including metadata about the query structure. Python import Groq from &quot;groq-sdk&quot;;
const groq = new Groq();
const response = await groq.chat.completions.create({
 model: &quot;openai/gpt-oss-120b&quot;,
 messages: [
 {
 role: &quot;system&quot;,
 content: &quot;You are a SQL expert. Generate structured SQL queries from natural language descriptions with proper syntax validation and metadata.&quot;,
 },
 { role: &quot;user&quot;, content: &quot;Find all customers who made orders over $500 in the last 30 days, show their name, email, and total order amount&quot; },
 ],
 response_format: {
 type: &quot;json_schema&quot;,
 json_schema: {
 name: &quot;sql_query_generation&quot;,
 schema: {
 type: &quot;object&quot;,
 properties: {
 query: { type: &quot;string&quot; },
 query_type: { 
 type: &quot;string&quot;, 
 enum: [&quot;SELECT&quot;, &quot;INSERT&quot;, &quot;UPDATE&quot;, &quot;DELETE&quot;, &quot;CREATE&quot;, &quot;ALTER&quot;, &quot;DROP&quot;] 
 },
 tables_used: {
 type: &quot;array&quot;,
 items: { type: &quot;string&quot; }
 },
 estimated_complexity: {
 type: &quot;string&quot;,
 enum: [&quot;low&quot;, &quot;medium&quot;, &quot;high&quot;]
 },
 execution_notes: {
 type: &quot;array&quot;,
 items: { type: &quot;string&quot; }
 },
 validation_status: {
 type: &quot;object&quot;,
 properties: {
 is_valid: { type: &quot;boolean&quot; },
 syntax_errors: {
 type: &quot;array&quot;,
 items: { type: &quot;string&quot; }
 }
 },
 required: [&quot;is_valid&quot;, &quot;syntax_errors&quot;],
 additionalProperties: false
 }
 },
 required: [&quot;query&quot;, &quot;query_type&quot;, &quot;tables_used&quot;, &quot;estimated_complexity&quot;, &quot;execution_notes&quot;, &quot;validation_status&quot;],
 additionalProperties: false
 }
 }
 }
});
const result = JSON.parse(response.choices[0].message.content || &quot;{}&quot;);
console.log(result); from groq import Groq
 from pydantic import BaseModel
 import json
 client = Groq ( ) 
 class ValidationStatus ( BaseModel ) : 
 is_valid : bool 
 syntax_errors : list [ str ] 
 class SQLQueryGeneration ( BaseModel ) : 
 query : str 
 query_type : str 
 tables_used : list [ str ] 
 estimated_complexity : str 
 execution_notes : list [ str ] 
 validation_status : ValidationStatus
 response = client . chat . completions . create ( 
 model = &quot;openai/gpt-oss-120b&quot; , 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a SQL expert. Generate structured SQL queries from natural language descriptions with proper syntax validation and metadata.&quot; , 
 } , 
 { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : &quot;Find all customers who made orders over $500 in the last 30 days, show their name, email, and total order amount&quot; } , 
 ] , 
 response_format = { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;sql_query_generation&quot; , 
 &quot;schema&quot; : SQLQueryGeneration . model_json_schema ( ) 
 } 
 } 
 ) 
 sql_query_generation = SQLQueryGeneration . model_validate ( json . loads ( response . choices [ 0 ] . message . content ) ) 
 print ( json . dumps ( sql_query_generation . model_dump ( ) , indent = 2 ) ) curl https://api.groq.com/openai/v1/chat/completions \
 -H &quot;Authorization: Bearer $GROQ_API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &#x27;{
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: &quot;You are a SQL expert. Generate structured SQL queries from natural language descriptions with proper syntax validation and metadata.&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Find all customers who made orders over $500 in the last 30 days, show their name, email, and total order amount&quot;
 }
 ],
 &quot;response_format&quot;: {
 &quot;type&quot;: &quot;json_schema&quot;,
 &quot;json_schema&quot;: {
 &quot;name&quot;: &quot;sql_query_generation&quot;,
 &quot;schema&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;query&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;query_type&quot;: { 
 &quot;type&quot;: &quot;string&quot;, 
 &quot;enum&quot;: [&quot;SELECT&quot;, &quot;INSERT&quot;, &quot;UPDATE&quot;, &quot;DELETE&quot;, &quot;CREATE&quot;, &quot;ALTER&quot;, &quot;DROP&quot;] 
 },
 &quot;tables_used&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;estimated_complexity&quot;: {
 &quot;type&quot;: &quot;string&quot;,
 &quot;enum&quot;: [&quot;low&quot;, &quot;medium&quot;, &quot;high&quot;]
 },
 &quot;execution_notes&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;validation_status&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;is_valid&quot;: { &quot;type&quot;: &quot;boolean&quot; },
 &quot;syntax_errors&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: { &quot;type&quot;: &quot;string&quot; }
 }
 },
 &quot;required&quot;: [&quot;is_valid&quot;, &quot;syntax_errors&quot;],
 &quot;additionalProperties&quot;: false
 }
 },
 &quot;required&quot;: [&quot;query&quot;, &quot;query_type&quot;, &quot;tables_used&quot;, &quot;estimated_complexity&quot;, &quot;execution_notes&quot;, &quot;validation_status&quot;],
 &quot;additionalProperties&quot;: false
 }
 }
 }
 }&#x27; Example Output JSON { 
 &quot;query&quot; : &quot;SELECT c.name, c.email, SUM(o.total_amount) as total_order_amount FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_date &gt;= DATE_SUB(NOW(), INTERVAL 30 DAY) AND o.total_amount &gt; 500 GROUP BY c.customer_id, c.name, c.email ORDER BY total_order_amount DESC&quot; , 
 &quot;query_type&quot; : &quot;SELECT&quot; , 
 &quot;tables_used&quot; : [ &quot;customers&quot; , &quot;orders&quot; ] , 
 &quot;estimated_complexity&quot; : &quot;medium&quot; , 
 &quot;execution_notes&quot; : [ 
 &quot;Query uses JOIN to connect customers and orders tables&quot; , 
 &quot;DATE_SUB function calculates 30 days ago from current date&quot; , 
 &quot;GROUP BY aggregates orders per customer&quot; , 
 &quot;Results ordered by total order amount descending&quot; 
 ] , 
 &quot;validation_status&quot; : { 
 &quot;is_valid&quot; : true , 
 &quot;syntax_errors&quot; : [ ] 
 } 
 } Email Classification You can classify emails into structured categories with confidence scores, priority levels, and suggested actions. Python import Groq from &quot;groq-sdk&quot;;
const groq = new Groq();
const response = await groq.chat.completions.create({
 model: &quot;openai/gpt-oss-120b&quot;,
 messages: [
 {
 role: &quot;system&quot;,
 content: &quot;You are an email classification expert. Classify emails into structured categories with confidence scores, priority levels, and suggested actions.&quot;,
 },
 { role: &quot;user&quot;, content: &quot;Subject: URGENT: Server downtime affecting production\n\nHi Team,\n\nOur main production server went down at 2:30 PM EST. Customer-facing services are currently unavailable. We need immediate action to restore services. Please join the emergency call.\n\nBest regards,\nDevOps Team&quot; },
 ],
 response_format: {
 type: &quot;json_schema&quot;,
 json_schema: {
 name: &quot;email_classification&quot;,
 schema: {
 type: &quot;object&quot;,
 properties: {
 category: { 
 type: &quot;string&quot;, 
 enum: [&quot;urgent&quot;, &quot;support&quot;, &quot;sales&quot;, &quot;marketing&quot;, &quot;internal&quot;, &quot;spam&quot;, &quot;notification&quot;] 
 },
 priority: { 
 type: &quot;string&quot;, 
 enum: [&quot;low&quot;, &quot;medium&quot;, &quot;high&quot;, &quot;critical&quot;] 
 },
 confidence_score: { 
 type: &quot;number&quot;, 
 minimum: 0, 
 maximum: 1 
 },
 sentiment: { 
 type: &quot;string&quot;, 
 enum: [&quot;positive&quot;, &quot;negative&quot;, &quot;neutral&quot;] 
 },
 key_entities: {
 type: &quot;array&quot;,
 items: {
 type: &quot;object&quot;,
 properties: {
 entity: { type: &quot;string&quot; },
 type: { 
 type: &quot;string&quot;, 
 enum: [&quot;person&quot;, &quot;organization&quot;, &quot;location&quot;, &quot;datetime&quot;, &quot;system&quot;, &quot;product&quot;] 
 }
 },
 required: [&quot;entity&quot;, &quot;type&quot;],
 additionalProperties: false
 }
 },
 suggested_actions: {
 type: &quot;array&quot;,
 items: { type: &quot;string&quot; }
 },
 requires_immediate_attention: { type: &quot;boolean&quot; },
 estimated_response_time: { type: &quot;string&quot; }
 },
 required: [&quot;category&quot;, &quot;priority&quot;, &quot;confidence_score&quot;, &quot;sentiment&quot;, &quot;key_entities&quot;, &quot;suggested_actions&quot;, &quot;requires_immediate_attention&quot;, &quot;estimated_response_time&quot;],
 additionalProperties: false
 }
 }
 }
});
const result = JSON.parse(response.choices[0].message.content || &quot;{}&quot;);
console.log(result); from groq import Groq
 from pydantic import BaseModel
 import json
 client = Groq ( ) 
 class KeyEntity ( BaseModel ) : 
 entity : str 
 type : str 
 class EmailClassification ( BaseModel ) : 
 category : str 
 priority : str 
 confidence_score : float 
 sentiment : str 
 key_entities : list [ KeyEntity ] 
 suggested_actions : list [ str ] 
 requires_immediate_attention : bool 
 estimated_response_time : str 
 response = client . chat . completions . create ( 
 model = &quot;openai/gpt-oss-120b&quot; , 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are an email classification expert. Classify emails into structured categories with confidence scores, priority levels, and suggested actions.&quot; , 
 } , 
 { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : &quot;Subject: URGENT: Server downtime affecting production\\n\\nHi Team,\\n\\nOur main production server went down at 2:30 PM EST. Customer-facing services are currently unavailable. We need immediate action to restore services. Please join the emergency call.\\n\\nBest regards,\\nDevOps Team&quot; } , 
 ] , 
 response_format = { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;email_classification&quot; , 
 &quot;schema&quot; : EmailClassification . model_json_schema ( ) 
 } 
 } 
 ) 
 email_classification = EmailClassification . model_validate ( json . loads ( response . choices [ 0 ] . message . content ) ) 
 print ( json . dumps ( email_classification . model_dump ( ) , indent = 2 ) ) curl https://api.groq.com/openai/v1/chat/completions \
 -H &quot;Authorization: Bearer $GROQ_API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &#x27;{
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: &quot;You are an email classification expert. Classify emails into structured categories with confidence scores, priority levels, and suggested actions.&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Subject: URGENT: Server downtime affecting production\n\nHi Team,\n\nOur main production server went down at 2:30 PM EST. Customer-facing services are currently unavailable. We need immediate action to restore services. Please join the emergency call.\n\nBest regards,\nDevOps Team&quot;
 }
 ],
 &quot;response_format&quot;: {
 &quot;type&quot;: &quot;json_schema&quot;,
 &quot;json_schema&quot;: {
 &quot;name&quot;: &quot;email_classification&quot;,
 &quot;schema&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;category&quot;: { 
 &quot;type&quot;: &quot;string&quot;, 
 &quot;enum&quot;: [&quot;urgent&quot;, &quot;support&quot;, &quot;sales&quot;, &quot;marketing&quot;, &quot;internal&quot;, &quot;spam&quot;, &quot;notification&quot;] 
 },
 &quot;priority&quot;: { 
 &quot;type&quot;: &quot;string&quot;, 
 &quot;enum&quot;: [&quot;low&quot;, &quot;medium&quot;, &quot;high&quot;, &quot;critical&quot;] 
 },
 &quot;confidence_score&quot;: { 
 &quot;type&quot;: &quot;number&quot;, 
 &quot;minimum&quot;: 0, 
 &quot;maximum&quot;: 1 
 },
 &quot;sentiment&quot;: { 
 &quot;type&quot;: &quot;string&quot;, 
 &quot;enum&quot;: [&quot;positive&quot;, &quot;negative&quot;, &quot;neutral&quot;] 
 },
 &quot;key_entities&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;entity&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;type&quot;: { 
 &quot;type&quot;: &quot;string&quot;, 
 &quot;enum&quot;: [&quot;person&quot;, &quot;organization&quot;, &quot;location&quot;, &quot;datetime&quot;, &quot;system&quot;, &quot;product&quot;] 
 }
 },
 &quot;required&quot;: [&quot;entity&quot;, &quot;type&quot;],
 &quot;additionalProperties&quot;: false
 }
 },
 &quot;suggested_actions&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;requires_immediate_attention&quot;: { &quot;type&quot;: &quot;boolean&quot; },
 &quot;estimated_response_time&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;required&quot;: [&quot;category&quot;, &quot;priority&quot;, &quot;confidence_score&quot;, &quot;sentiment&quot;, &quot;key_entities&quot;, &quot;suggested_actions&quot;, &quot;requires_immediate_attention&quot;, &quot;estimated_response_time&quot;],
 &quot;additionalProperties&quot;: false
 }
 }
 }
 }&#x27; Example Output JSON { 
 &quot;category&quot; : &quot;urgent&quot; , 
 &quot;priority&quot; : &quot;critical&quot; , 
 &quot;confidence_score&quot; : 0.95 , 
 &quot;sentiment&quot; : &quot;negative&quot; , 
 &quot;key_entities&quot; : [ 
 { 
 &quot;entity&quot; : &quot;production server&quot; , 
 &quot;type&quot; : &quot;system&quot; 
 } , 
 { 
 &quot;entity&quot; : &quot;2:30 PM EST&quot; , 
 &quot;type&quot; : &quot;datetime&quot; 
 } , 
 { 
 &quot;entity&quot; : &quot;DevOps Team&quot; , 
 &quot;type&quot; : &quot;organization&quot; 
 } , 
 { 
 &quot;entity&quot; : &quot;customer-facing services&quot; , 
 &quot;type&quot; : &quot;system&quot; 
 } 
 ] , 
 &quot;suggested_actions&quot; : [ 
 &quot;Join emergency call immediately&quot; , 
 &quot;Escalate to senior DevOps team&quot; , 
 &quot;Activate incident response protocol&quot; , 
 &quot;Prepare customer communication&quot; , 
 &quot;Monitor service restoration progress&quot; 
 ] , 
 &quot;requires_immediate_attention&quot; : true , 
 &quot;estimated_response_time&quot; : &quot;immediate&quot; 
 } API Response Validation You can validate and structure API responses with error handling, status codes, and standardized data formats for reliable integration. Python import Groq from &quot;groq-sdk&quot;;
const groq = new Groq();
const response = await groq.chat.completions.create({
 model: &quot;openai/gpt-oss-120b&quot;,
 messages: [
 {
 role: &quot;system&quot;,
 content: &quot;You are an API response validation expert. Validate and structure API responses with error handling, status codes, and standardized data formats for reliable integration.&quot;,
 },
 { role: &quot;user&quot;, content: &quot;Validate this API response: {\&quot;user_id\&quot;: \&quot;12345\&quot;, \&quot;email\&quot;: \&quot;invalid-email\&quot;, \&quot;created_at\&quot;: \&quot;2024-01-15T10:30:00Z\&quot;, \&quot;status\&quot;: \&quot;active\&quot;, \&quot;profile\&quot;: {\&quot;name\&quot;: \&quot;John Doe\&quot;, \&quot;age\&quot;: 25}}&quot; },
 ],
 response_format: {
 type: &quot;json_schema&quot;,
 json_schema: {
 name: &quot;api_response_validation&quot;,
 schema: {
 type: &quot;object&quot;,
 properties: {
 validation_result: {
 type: &quot;object&quot;,
 properties: {
 is_valid: { type: &quot;boolean&quot; },
 status_code: { type: &quot;integer&quot; },
 error_count: { type: &quot;integer&quot; }
 },
 required: [&quot;is_valid&quot;, &quot;status_code&quot;, &quot;error_count&quot;],
 additionalProperties: false
 },
 field_validations: {
 type: &quot;array&quot;,
 items: {
 type: &quot;object&quot;,
 properties: {
 field_name: { type: &quot;string&quot; },
 field_type: { type: &quot;string&quot; },
 is_valid: { type: &quot;boolean&quot; },
 error_message: { type: &quot;string&quot; },
 expected_format: { type: &quot;string&quot; }
 },
 required: [&quot;field_name&quot;, &quot;field_type&quot;, &quot;is_valid&quot;, &quot;error_message&quot;, &quot;expected_format&quot;],
 additionalProperties: false
 }
 },
 data_quality_score: { 
 type: &quot;number&quot;, 
 minimum: 0, 
 maximum: 1 
 },
 suggested_fixes: {
 type: &quot;array&quot;,
 items: { type: &quot;string&quot; }
 },
 compliance_check: {
 type: &quot;object&quot;,
 properties: {
 follows_rest_standards: { type: &quot;boolean&quot; },
 has_proper_error_handling: { type: &quot;boolean&quot; },
 includes_metadata: { type: &quot;boolean&quot; }
 },
 required: [&quot;follows_rest_standards&quot;, &quot;has_proper_error_handling&quot;, &quot;includes_metadata&quot;],
 additionalProperties: false
 },
 standardized_response: {
 type: &quot;object&quot;,
 properties: {
 success: { type: &quot;boolean&quot; },
 data: { type: &quot;object&quot; },
 errors: {
 type: &quot;array&quot;,
 items: { type: &quot;string&quot; }
 },
 metadata: {
 type: &quot;object&quot;,
 properties: {
 timestamp: { type: &quot;string&quot; },
 request_id: { type: &quot;string&quot; },
 version: { type: &quot;string&quot; }
 },
 required: [&quot;timestamp&quot;, &quot;request_id&quot;, &quot;version&quot;],
 additionalProperties: false
 }
 },
 required: [&quot;success&quot;, &quot;data&quot;, &quot;errors&quot;, &quot;metadata&quot;],
 additionalProperties: false
 }
 },
 required: [&quot;validation_result&quot;, &quot;field_validations&quot;, &quot;data_quality_score&quot;, &quot;suggested_fixes&quot;, &quot;compliance_check&quot;, &quot;standardized_response&quot;],
 additionalProperties: false
 }
 }
 }
});
const result = JSON.parse(response.choices[0].message.content || &quot;{}&quot;);
console.log(result); from groq import Groq
 from pydantic import BaseModel
 import json
 client = Groq ( ) 
 class ValidationResult ( BaseModel ) : 
 is_valid : bool 
 status_code : int 
 error_count : int 
 class FieldValidation ( BaseModel ) : 
 field_name : str 
 field_type : str 
 is_valid : bool 
 error_message : str 
 expected_format : str 
 class ComplianceCheck ( BaseModel ) : 
 follows_rest_standards : bool 
 has_proper_error_handling : bool 
 includes_metadata : bool 
 class Metadata ( BaseModel ) : 
 timestamp : str 
 request_id : str 
 version : str 
 class StandardizedResponse ( BaseModel ) : 
 success : bool 
 data : dict 
 errors : list [ str ] 
 metadata : Metadata
 class APIResponseValidation ( BaseModel ) : 
 validation_result : ValidationResult
 field_validations : list [ FieldValidation ] 
 data_quality_score : float 
 suggested_fixes : list [ str ] 
 compliance_check : ComplianceCheck
 standardized_response : StandardizedResponse
 response = client . chat . completions . create ( 
 model = &quot;openai/gpt-oss-120b&quot; , 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are an API response validation expert. Validate and structure API responses with error handling, status codes, and standardized data formats for reliable integration.&quot; , 
 } , 
 { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : &quot;Validate this API response: {\&quot;user_id\&quot;: \&quot;12345\&quot;, \&quot;email\&quot;: \&quot;invalid-email\&quot;, \&quot;created_at\&quot;: \&quot;2024-01-15T10:30:00Z\&quot;, \&quot;status\&quot;: \&quot;active\&quot;, \&quot;profile\&quot;: {\&quot;name\&quot;: \&quot;John Doe\&quot;, \&quot;age\&quot;: 25}}&quot; } , 
 ] , 
 response_format = { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;api_response_validation&quot; , 
 &quot;schema&quot; : APIResponseValidation . model_json_schema ( ) 
 } 
 } 
 ) 
 api_response_validation = APIResponseValidation . model_validate ( json . loads ( response . choices [ 0 ] . message . content ) ) 
 print ( json . dumps ( api_response_validation . model_dump ( ) , indent = 2 ) ) curl https://api.groq.com/openai/v1/chat/completions \
 -H &quot;Authorization: Bearer $GROQ_API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &#x27;{
 &quot;model&quot;: &quot;openai/gpt-oss-120b&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: &quot;You are an API response validation expert. Validate and structure API responses with error handling, status codes, and standardized data formats for reliable integration.&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Validate this API response: {\&quot;user_id\&quot;: \&quot;12345\&quot;, \&quot;email\&quot;: \&quot;invalid-email\&quot;, \&quot;created_at\&quot;: \&quot;2024-01-15T10:30:00Z\&quot;, \&quot;status\&quot;: \&quot;active\&quot;, \&quot;profile\&quot;: {\&quot;name\&quot;: \&quot;John Doe\&quot;, \&quot;age\&quot;: 25}}&quot;
 }
 ],
 &quot;response_format&quot;: {
 &quot;type&quot;: &quot;json_schema&quot;,
 &quot;json_schema&quot;: {
 &quot;name&quot;: &quot;api_response_validation&quot;,
 &quot;schema&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;validation_result&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;is_valid&quot;: { &quot;type&quot;: &quot;boolean&quot; },
 &quot;status_code&quot;: { &quot;type&quot;: &quot;integer&quot; },
 &quot;error_count&quot;: { &quot;type&quot;: &quot;integer&quot; }
 },
 &quot;required&quot;: [&quot;is_valid&quot;, &quot;status_code&quot;, &quot;error_count&quot;],
 &quot;additionalProperties&quot;: false
 },
 &quot;field_validations&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;field_name&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;field_type&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;is_valid&quot;: { &quot;type&quot;: &quot;boolean&quot; },
 &quot;error_message&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;expected_format&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;required&quot;: [&quot;field_name&quot;, &quot;field_type&quot;, &quot;is_valid&quot;, &quot;error_message&quot;, &quot;expected_format&quot;],
 &quot;additionalProperties&quot;: false
 }
 },
 &quot;data_quality_score&quot;: { 
 &quot;type&quot;: &quot;number&quot;, 
 &quot;minimum&quot;: 0, 
 &quot;maximum&quot;: 1 
 },
 &quot;suggested_fixes&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;compliance_check&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;follows_rest_standards&quot;: { &quot;type&quot;: &quot;boolean&quot; },
 &quot;has_proper_error_handling&quot;: { &quot;type&quot;: &quot;boolean&quot; },
 &quot;includes_metadata&quot;: { &quot;type&quot;: &quot;boolean&quot; }
 },
 &quot;required&quot;: [&quot;follows_rest_standards&quot;, &quot;has_proper_error_handling&quot;, &quot;includes_metadata&quot;],
 &quot;additionalProperties&quot;: false
 },
 &quot;standardized_response&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;success&quot;: { &quot;type&quot;: &quot;boolean&quot; },
 &quot;data&quot;: { &quot;type&quot;: &quot;object&quot; },
 &quot;errors&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;metadata&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;timestamp&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;request_id&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;version&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;required&quot;: [&quot;timestamp&quot;, &quot;request_id&quot;, &quot;version&quot;],
 &quot;additionalProperties&quot;: false
 }
 },
 &quot;required&quot;: [&quot;success&quot;, &quot;data&quot;, &quot;errors&quot;, &quot;metadata&quot;],
 &quot;additionalProperties&quot;: false
 }
 },
 &quot;required&quot;: [&quot;validation_result&quot;, &quot;field_validations&quot;, &quot;data_quality_score&quot;, &quot;suggested_fixes&quot;, &quot;compliance_check&quot;, &quot;standardized_response&quot;],
 &quot;additionalProperties&quot;: false
 }
 }
 }
 }&#x27; Example Output JSON { 
 &quot;validation_result&quot; : { 
 &quot;is_valid&quot; : false , 
 &quot;status_code&quot; : 400 , 
 &quot;error_count&quot; : 2 
 } , 
 &quot;field_validations&quot; : [ 
 { 
 &quot;field_name&quot; : &quot;user_id&quot; , 
 &quot;field_type&quot; : &quot;string&quot; , 
 &quot;is_valid&quot; : true , 
 &quot;error_message&quot; : &quot;&quot; , 
 &quot;expected_format&quot; : &quot;string&quot; 
 } , 
 { 
 &quot;field_name&quot; : &quot;email&quot; , 
 &quot;field_type&quot; : &quot;string&quot; , 
 &quot;is_valid&quot; : false , 
 &quot;error_message&quot; : &quot;Invalid email format&quot; , 
 &quot;expected_format&quot; : &quot;valid email address (e.g., [email&#160;protected] )&quot; 
 } 
 ] , 
 &quot;data_quality_score&quot; : 0.7 , 
 &quot;suggested_fixes&quot; : [ 
 &quot;Fix email format validation to ensure proper email structure&quot; , 
 &quot;Add proper error handling structure to response&quot; 
 ] , 
 &quot;compliance_check&quot; : { 
 &quot;follows_rest_standards&quot; : false , 
 &quot;has_proper_error_handling&quot; : false , 
 &quot;includes_metadata&quot; : false 
 } 
 } 
 Schema Validation Libraries 
 When working with Structured Outputs, you can use popular schema validation libraries like Zod for TypeScript and Pydantic for Python. These libraries provide type safety, runtime validation, and seamless integration with JSON Schema generation. 
 Support Ticket Classification 
 This example demonstrates how to classify customer support tickets using structured schemas with both Zod and Pydantic, ensuring consistent categorization and routing. 
 Zod (TypeScript) Pydantic (Python) TypeScript import Groq from &quot;groq-sdk&quot; ; 
 import { z } from &quot;zod&quot; ; 
 const groq = new Groq ( ) ; 
 const supportTicketSchema = z . object ( { 
 category : z . enum ( [ &quot;api&quot; , &quot;billing&quot; , &quot;account&quot; , &quot;bug&quot; , &quot;feature_request&quot; , &quot;integration&quot; , &quot;security&quot; , &quot;performance&quot; ] ) , 
 priority : z . enum ( [ &quot;low&quot; , &quot;medium&quot; , &quot;high&quot; , &quot;critical&quot; ] ) , 
 urgency_score : z . number ( ) , 
 customer_info : z . object ( { 
 name : z . string ( ) , 
 company : z . string ( ) . optional ( ) , 
 tier : z . enum ( [ &quot;free&quot; , &quot;paid&quot; , &quot;enterprise&quot; , &quot;trial&quot; ] ) 
 } ) , 
 technical_details : z . array ( z . object ( { 
 component : z . string ( ) , 
 error_code : z . string ( ) . optional ( ) , 
 description : z . string ( ) 
 } ) ) , 
 keywords : z . array ( z . string ( ) ) , 
 requires_escalation : z . boolean ( ) , 
 estimated_resolution_hours : z . number ( ) , 
 follow_up_date : z . string ( ) . datetime ( ) . optional ( ) , 
 summary : z . string ( ) 
 } ) ; 
 type SupportTicket = z . infer &lt; typeof supportTicketSchema &gt; ; 
 const response = await groq . chat . completions . create ( { 
 model : &quot;openai/gpt-oss-120b&quot; , 
 messages : [ 
 { 
 role : &quot;system&quot; , 
 content : ` You are a customer support ticket classifier for SaaS companies. 
 Analyze support tickets and categorize them for efficient routing and resolution.
 Output JSON only using the schema provided. ` , 
 } , 
 { 
 role : &quot;user&quot; , 
 content : ` Hello! I love your product and have been using it for 6 months. 
 I was wondering if you could add a dark mode feature to the dashboard? 
 Many of our team members work late hours and would really appreciate this. 
 Also, it would be great to have keyboard shortcuts for common actions. 
 Not urgent, but would be a nice enhancement! 
 Best, Mike from StartupXYZ ` 
 } , 
 ] , 
 response_format : { 
 type : &quot;json_schema&quot; , 
 json_schema : { 
 name : &quot;support_ticket_classification&quot; , 
 schema : z . toJSONSchema ( supportTicketSchema ) 
 } 
 } 
 } ) ; 
 const rawResult = JSON . parse ( response . choices [ 0 ] . message . content || &quot;{}&quot; ) ; 
 const result = supportTicketSchema . parse ( rawResult ) ; 
 console . log ( result ) ; Python from groq import Groq
 from pydantic import BaseModel , Field
 from typing import List , Optional , Literal
 from enum import Enum
 import json
 client = Groq ( ) 
 class SupportCategory ( str , Enum ) : 
 API = &quot;api&quot; 
 BILLING = &quot;billing&quot; 
 ACCOUNT = &quot;account&quot; 
 BUG = &quot;bug&quot; 
 FEATURE_REQUEST = &quot;feature_request&quot; 
 INTEGRATION = &quot;integration&quot; 
 SECURITY = &quot;security&quot; 
 PERFORMANCE = &quot;performance&quot; 
 class Priority ( str , Enum ) : 
 LOW = &quot;low&quot; 
 MEDIUM = &quot;medium&quot; 
 HIGH = &quot;high&quot; 
 CRITICAL = &quot;critical&quot; 
 class CustomerTier ( str , Enum ) : 
 FREE = &quot;free&quot; 
 PAID = &quot;paid&quot; 
 ENTERPRISE = &quot;enterprise&quot; 
 TRIAL = &quot;trial&quot; 
 class CustomerInfo ( BaseModel ) : 
 name : str 
 company : Optional [ str ] = None 
 tier : CustomerTier
 class TechnicalDetail ( BaseModel ) : 
 component : str 
 error_code : Optional [ str ] = None 
 description : str 
 class SupportTicket ( BaseModel ) : 
 category : SupportCategory
 priority : Priority
 urgency_score : float 
 customer_info : CustomerInfo
 technical_details : List [ TechnicalDetail ] 
 keywords : List [ str ] 
 requires_escalation : bool 
 estimated_resolution_hours : float 
 follow_up_date : Optional [ str ] = Field ( None , description = &quot;ISO datetime string&quot; ) 
 summary : str 
 response = client . chat . completions . create ( 
 model = &quot;openai/gpt-oss-120b&quot; , 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;&quot;&quot;You are a customer support ticket classifier for SaaS companies. 
 Analyze support tickets and categorize them for efficient routing and resolution.
 Output JSON only using the schema provided.&quot;&quot;&quot; , 
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;&quot;&quot;Hello! I love your product and have been using it for 6 months. 
 I was wondering if you could add a dark mode feature to the dashboard? 
 Many of our team members work late hours and would really appreciate this. 
 Also, it would be great to have keyboard shortcuts for common actions. 
 Not urgent, but would be a nice enhancement! 
 Best, Mike from StartupXYZ&quot;&quot;&quot; 
 } , 
 ] , 
 response_format = { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;support_ticket_classification&quot; , 
 &quot;schema&quot; : SupportTicket . model_json_schema ( ) 
 } 
 } 
 ) 
 raw_result = json . loads ( response . choices [ 0 ] . message . content or &quot;{}&quot; ) 
 result = SupportTicket . model_validate ( raw_result ) 
 print ( result . model_dump_json ( indent = 2 ) ) 
 Example Output JSON { 
 &quot;category&quot; : &quot;feature_request&quot; , 
 &quot;priority&quot; : &quot;low&quot; , 
 &quot;urgency_score&quot; : 2.5 , 
 &quot;customer_info&quot; : { 
 &quot;name&quot; : &quot;Mike&quot; , 
 &quot;company&quot; : &quot;StartupXYZ&quot; , 
 &quot;tier&quot; : &quot;paid&quot; 
 } , 
 &quot;technical_details&quot; : [ 
 { 
 &quot;component&quot; : &quot;dashboard&quot; , 
 &quot;description&quot; : &quot;Request for dark mode feature&quot; 
 } , 
 { 
 &quot;component&quot; : &quot;user_interface&quot; , 
 &quot;description&quot; : &quot;Request for keyboard shortcuts&quot; 
 } 
 ] , 
 &quot;keywords&quot; : [ &quot;dark mode&quot; , &quot;dashboard&quot; , &quot;keyboard shortcuts&quot; , &quot;enhancement&quot; ] , 
 &quot;requires_escalation&quot; : false , 
 &quot;estimated_resolution_hours&quot; : 40 , 
 &quot;summary&quot; : &quot;Feature request for dark mode and keyboard shortcuts from paying customer&quot; 
 } 
 Implementation Guide 
 Schema Definition 
 Design your JSON Schema to constrain model responses. Reference the examples above and see supported schema features for technical limitations. 
 API Integration 
 Include the schema in your API request using the response_format parameter. Choose between strict: true for guaranteed schema compliance or strict: false for best-effort validation: 
 Strict Mode Best-effort Mode Using Strict Mode ( strict: true ) Set strict: true for guaranteed schema compliance on supported models: JSON response_format : { type : &quot;json_schema&quot; , json_schema : { name : &quot;schema_name&quot; , strict : true , schema : … } } Complete implementation example: Python from groq import Groq
 import json
 client = Groq ( ) 
 response = client . chat . completions . create ( 
 model = &quot;openai/gpt-oss-20b&quot; , 
 messages = [ 
 { &quot;role&quot; : &quot;system&quot; , &quot;content&quot; : &quot;You are a helpful math tutor. Guide the user through the solution step by step.&quot; } , 
 { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : &quot;how can I solve 8x + 7 = -23&quot; } 
 ] , 
 response_format = { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;math_response&quot; , 
 &quot;strict&quot; : True , 
 &quot;schema&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;steps&quot; : { 
 &quot;type&quot; : &quot;array&quot; , 
 &quot;items&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;explanation&quot; : { &quot;type&quot; : &quot;string&quot; } , 
 &quot;output&quot; : { &quot;type&quot; : &quot;string&quot; } 
 } , 
 &quot;required&quot; : [ &quot;explanation&quot; , &quot;output&quot; ] , 
 &quot;additionalProperties&quot; : False 
 } 
 } , 
 &quot;final_answer&quot; : { &quot;type&quot; : &quot;string&quot; } 
 } , 
 &quot;required&quot; : [ &quot;steps&quot; , &quot;final_answer&quot; ] , 
 &quot;additionalProperties&quot; : False 
 } 
 } 
 } 
 ) 
 result = json . loads ( response . choices [ 0 ] . message . content ) 
 print ( json . dumps ( result , indent = 2 ) ) import Groq from &quot;groq-sdk&quot;;
const groq = new Groq();
const response = await groq.chat.completions.create({
 model: &quot;openai/gpt-oss-20b&quot;,
 messages: [
 { role: &quot;system&quot;, content: &quot;You are a helpful math tutor. Guide the user through the solution step by step.&quot; },
 { role: &quot;user&quot;, content: &quot;how can I solve 8x + 7 = -23&quot; }
 ],
 response_format: {
 type: &quot;json_schema&quot;,
 json_schema: {
 name: &quot;math_response&quot;,
 strict: true,
 schema: {
 type: &quot;object&quot;,
 properties: {
 steps: {
 type: &quot;array&quot;,
 items: {
 type: &quot;object&quot;,
 properties: {
 explanation: { type: &quot;string&quot; },
 output: { type: &quot;string&quot; }
 },
 required: [&quot;explanation&quot;, &quot;output&quot;],
 additionalProperties: false
 }
 },
 final_answer: { type: &quot;string&quot; }
 },
 required: [&quot;steps&quot;, &quot;final_answer&quot;],
 additionalProperties: false
 }
 }
 }
});
const result = JSON.parse(response.choices[0].message.content || &quot;{}&quot;);
console.log(result); curl https://api.groq.com/openai/v1/chat/completions \
 -H &quot;Authorization: Bearer $GROQ_API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &#x27;{
 &quot;model&quot;: &quot;openai/gpt-oss-20b&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: &quot;You are a helpful math tutor. Guide the user through the solution step by step.&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;how can I solve 8x + 7 = -23&quot;
 }
 ],
 &quot;response_format&quot;: {
 &quot;type&quot;: &quot;json_schema&quot;,
 &quot;json_schema&quot;: {
 &quot;name&quot;: &quot;math_response&quot;,
 &quot;strict&quot;: true,
 &quot;schema&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;steps&quot;: {
 &quot;type&quot;: &quot;array&quot;,
 &quot;items&quot;: {
 &quot;type&quot;: &quot;object&quot;,
 &quot;properties&quot;: {
 &quot;explanation&quot;: { &quot;type&quot;: &quot;string&quot; },
 &quot;output&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;required&quot;: [&quot;explanation&quot;, &quot;output&quot;],
 &quot;additionalProperties&quot;: false
 }
 },
 &quot;final_answer&quot;: { &quot;type&quot;: &quot;string&quot; }
 },
 &quot;required&quot;: [&quot;steps&quot;, &quot;final_answer&quot;],
 &quot;additionalProperties&quot;: false
 }
 }
 }
 }&#x27; Using Best-effort Mode ( strict: false ) Set strict: false or omit the parameter for best-effort validation: JSON response_format : { type : &quot;json_schema&quot; , json_schema : { name : &quot;schema_name&quot; , strict : false , schema : … } } Complete implementation example: curl curl curl 
 Error Handling 
 Error handling differs based on which mode you&#x27;re using: 
 Strict Mode Best-effort Mode With Strict Mode ( strict: true ) Constrained decoding guarantees schema-compliant output, so you won&#x27;t encounter schema validation errors. The model&#x27;s output will always match your JSON Schema perfectly. No error handling needed: Python # Simple and reliable - no try/catch needed for validation 
 response = client . chat . completions . create ( 
 model = &quot;openai/gpt-oss-20b&quot; , 
 messages = [ . . . ] , 
 response_format = { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;schema_name&quot; , 
 &quot;strict&quot; : True , 
 &quot;schema&quot; : { . . . } 
 } 
 } 
 ) 
 # Output is guaranteed to match schema 
 data = json . loads ( response . choices [ 0 ] . message . content ) With Best-effort Mode ( strict: false ) Schema validation failures may occur and return HTTP 400 errors with the message Generated JSON does not match the expected schema. Please adjust your prompt. Resolution strategies: 
 Retry requests for transient failures 
 Refine prompts for recurring schema mismatches 
 Simplify complex schemas if validation consistently fails 
 Consider migrating to strict: true for guaranteed compliance 
 Example with retry logic: Python # Recommended pattern for strict: false 
 max_retries = 3 
 for attempt in range ( max_retries ) : 
 try : 
 response = client . chat . completions . create ( 
 model = &quot;openai/gpt-oss-120b&quot; , 
 messages = [ . . . ] , 
 response_format = { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;schema_name&quot; , 
 &quot;strict&quot; : False , 
 &quot;schema&quot; : { . . . } 
 } 
 } 
 ) 
 data = json . loads ( response . choices [ 0 ] . message . content ) 
 validate_schema ( data ) # Manual validation 
 break 
 except ValidationError as e : 
 if attempt == max_retries - 1 : 
 raise 
 # Retry on validation failure 
 Best Practices 
 User input handling: Include explicit instructions for invalid or incompatible inputs. Models attempt schema adherence even with unrelated data, potentially causing hallucinations. Specify fallback responses (empty fields, error messages) for incompatible inputs. 
 Output quality: Structured outputs are designed to output schema compliance but not semantic accuracy. For persistent errors, refine instructions, add system message examples, or decompose complex tasks. See the prompt engineering guide for optimization techniques. 
 Migration Guide: Upgrading to Strict Mode 
 If you&#x27;re currently using Structured Outputs with strict: false (or without specifying the strict parameter), you can upgrade to strict: true for guaranteed schema compliance. Follow these steps: 
 Step 1: Verify Model Support 
 Ensure you&#x27;re using a model that supports strict: true . See the Supported Models section for more information. 
 Step 2: Update Your Schema 
 Make your schema compliant with strict: true requirements: 
 Mark all fields as required: 
 JSON { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;name&quot; : { &quot;type&quot; : &quot;string&quot; } , 
 &quot;age&quot; : { &quot;type&quot; : &quot;number&quot; } 
 } , 
 &quot;required&quot; : [ &quot;name&quot; , &quot;age&quot; ] // ← Ensure all properties are in required array 
 } 
 Add additionalProperties: false to all objects: 
 JSON { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;name&quot; : { &quot;type&quot; : &quot;string&quot; } , 
 &quot;email&quot; : { &quot;type&quot; : &quot;string&quot; } 
 } , 
 &quot;required&quot; : [ &quot;name&quot; , &quot;email&quot; ] , 
 &quot;additionalProperties&quot; : false // ← Add this to all objects 
 } 
 Handle optional fields with union types: 
 If you need optional fields, use union types with null : 
 JSON { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;name&quot; : { &quot;type&quot; : &quot;string&quot; } , 
 &quot;nickname&quot; : { 
 &quot;type&quot; : [ &quot;string&quot; , &quot;null&quot; ] // ← Use union type for optional fields 
 } 
 } , 
 &quot;required&quot; : [ &quot;name&quot; , &quot;nickname&quot; ] , // ← Field must still be in required array 
 &quot;additionalProperties&quot; : false 
 } 
 Step 3: Update API Calls 
 Add strict: true to your response_format : 
 JSON { 
 &quot;model&quot; : &quot;openai/gpt-oss-20b&quot; , 
 &quot;messages&quot; : [ ... ] , 
 &quot;response_format&quot; : { 
 &quot;type&quot; : &quot;json_schema&quot; , 
 &quot;json_schema&quot; : { 
 &quot;name&quot; : &quot;schema_name&quot; , 
 &quot;strict&quot; : true , // ← Add this line 
 &quot;schema&quot; : { ... } 
 } 
 } 
 } 
 Schema Requirements 
 Structured Outputs supports a JSON Schema subset with specific constraints for performance and reliability. 
 Supported Data Types 
 Primitives: String, Number, Boolean, Integer 
 Complex: Object, Array, Enum 
 Composition: anyOf (union types) 
 Schema Constraints by Mode 
 Best-effort Mode Strict Mode When using strict: true , your schema must follow these mandatory constraints: Required fields: All schema properties must be marked as required . Optional fields are not supported. JSON { 
 &quot;name&quot; : &quot;create_task&quot; , 
 &quot;description&quot; : &quot;Creates a new task in the project management system&quot; , 
 &quot;strict&quot; : true , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;title&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The task title or summary&quot; 
 } , 
 &quot;priority&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Task priority level&quot; , 
 &quot;enum&quot; : [ &quot;low&quot; , &quot;medium&quot; , &quot;high&quot; , &quot;urgent&quot; ] 
 } 
 } , 
 &quot;additionalProperties&quot; : false , 
 &quot;required&quot; : [ &quot;title&quot; , &quot;priority&quot; ] 
 } 
 } Closed objects: All objects must set additionalProperties: false to prevent undefined properties. This ensures strict schema adherence. Handling optional fields: Use union types with null to represent optional values: JSON { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;name&quot; : { &quot;type&quot; : &quot;string&quot; } , 
 &quot;nickname&quot; : { 
 &quot;type&quot; : [ &quot;string&quot; , &quot;null&quot; ] 
 } 
 } , 
 &quot;required&quot; : [ &quot;name&quot; , &quot;nickname&quot; ] , 
 &quot;additionalProperties&quot; : false 
 } When using strict: false (default), your schema has more flexibility: 
 Optional fields allowed: Not all properties need to be in required 
 additionalProperties: Can be true or omitted (though false is recommended) 
 More forgiving validation: Best-effort schema matching, but may occasionally produce errors or invalid JSON 
 Example with optional fields: JSON { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;name&quot; : { &quot;type&quot; : &quot;string&quot; } , 
 &quot;nickname&quot; : { &quot;type&quot; : &quot;string&quot; } 
 } , 
 &quot;required&quot; : [ &quot;name&quot; ] 
 } Note: While strict: false is more flexible, following the strict: true requirements will improve output quality and reduce validation errors. 
 Union types: Each schema within anyOf must comply with all subset restrictions: 
 JSON { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;payment_method&quot; : { 
 &quot;anyOf&quot; : [ 
 { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;description&quot; : &quot;Credit card payment information&quot; , 
 &quot;properties&quot; : { 
 &quot;card_number&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The credit card number&quot; 
 } , 
 &quot;expiry_date&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Card expiration date in MM/YY format&quot; 
 } , 
 &quot;cvv&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Card security code&quot; 
 } 
 } , 
 &quot;additionalProperties&quot; : false , 
 &quot;required&quot; : [ &quot;card_number&quot; , &quot;expiry_date&quot; , &quot;cvv&quot; ] 
 } , 
 { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;description&quot; : &quot;Bank transfer payment information&quot; , 
 &quot;properties&quot; : { 
 &quot;account_number&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Bank account number&quot; 
 } , 
 &quot;routing_number&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Bank routing number&quot; 
 } , 
 &quot;bank_name&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Name of the bank&quot; 
 } 
 } , 
 &quot;additionalProperties&quot; : false , 
 &quot;required&quot; : [ &quot;account_number&quot; , &quot;routing_number&quot; , &quot;bank_name&quot; ] 
 } 
 ] 
 } 
 } , 
 &quot;additionalProperties&quot; : false , 
 &quot;required&quot; : [ &quot;payment_method&quot; ] 
 } 
 Reusable subschemas: Define reusable components with $defs and reference them using $ref : 
 JSON { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;milestones&quot; : { 
 &quot;type&quot; : &quot;array&quot; , 
 &quot;items&quot; : { 
 &quot;$ref&quot; : &quot;#/$defs/milestone&quot; 
 } 
 } , 
 &quot;project_status&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;enum&quot; : [ &quot;planning&quot; , &quot;in_progress&quot; , &quot;completed&quot; , &quot;on_hold&quot; ] 
 } 
 } , 
 &quot;$defs&quot; : { 
 &quot;milestone&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;title&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Milestone name&quot; 
 } , 
 &quot;deadline&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Due date in ISO format&quot; 
 } , 
 &quot;completed&quot; : { 
 &quot;type&quot; : &quot;boolean&quot; 
 } 
 } , 
 &quot;required&quot; : [ &quot;title&quot; , &quot;deadline&quot; , &quot;completed&quot; ] , 
 &quot;additionalProperties&quot; : false 
 } 
 } , 
 &quot;required&quot; : [ &quot;milestones&quot; , &quot;project_status&quot; ] , 
 &quot;additionalProperties&quot; : false 
 } 
 Root recursion: Use # to reference the root schema: 
 JSON { 
 &quot;name&quot; : &quot;organization_chart&quot; , 
 &quot;description&quot; : &quot;Company organizational structure&quot; , 
 &quot;strict&quot; : true , 
 &quot;schema&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;employee_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Unique employee identifier&quot; 
 } , 
 &quot;name&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Employee full name&quot; 
 } , 
 &quot;position&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Job title or position&quot; , 
 &quot;enum&quot; : [ &quot;CEO&quot; , &quot;Manager&quot; , &quot;Developer&quot; , &quot;Designer&quot; , &quot;Analyst&quot; , &quot;Intern&quot; ] 
 } , 
 &quot;direct_reports&quot; : { 
 &quot;type&quot; : &quot;array&quot; , 
 &quot;description&quot; : &quot;Employees reporting to this person&quot; , 
 &quot;items&quot; : { 
 &quot;$ref&quot; : &quot;#&quot; 
 } 
 } , 
 &quot;contact_info&quot; : { 
 &quot;type&quot; : &quot;array&quot; , 
 &quot;description&quot; : &quot;Contact information for the employee&quot; , 
 &quot;items&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;type&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;Type of contact info&quot; , 
 &quot;enum&quot; : [ &quot;email&quot; , &quot;phone&quot; , &quot;slack&quot; ] 
 } , 
 &quot;value&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The contact value&quot; 
 } 
 } , 
 &quot;additionalProperties&quot; : false , 
 &quot;required&quot; : [ &quot;type&quot; , &quot;value&quot; ] 
 } 
 } 
 } , 
 &quot;required&quot; : [ 
 &quot;employee_id&quot; , 
 &quot;name&quot; , 
 &quot;position&quot; , 
 &quot;direct_reports&quot; , 
 &quot;contact_info&quot; 
 ] , 
 &quot;additionalProperties&quot; : false 
 } 
 } 
 Explicit recursion through definition references: 
 JSON { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;file_system&quot; : { 
 &quot;$ref&quot; : &quot;#/$defs/file_node&quot; 
 } 
 } , 
 &quot;$defs&quot; : { 
 &quot;file_node&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;name&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;File or directory name&quot; 
 } , 
 &quot;type&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;enum&quot; : [ &quot;file&quot; , &quot;directory&quot; ] 
 } , 
 &quot;size&quot; : { 
 &quot;type&quot; : &quot;number&quot; , 
 &quot;description&quot; : &quot;Size in bytes (0 for directories)&quot; 
 } , 
 &quot;children&quot; : { 
 &quot;anyOf&quot; : [ 
 { 
 &quot;type&quot; : &quot;array&quot; , 
 &quot;items&quot; : { 
 &quot;$ref&quot; : &quot;#/$defs/file_node&quot; 
 } 
 } , 
 { 
 &quot;type&quot; : &quot;null&quot; 
 } 
 ] 
 } 
 } , 
 &quot;additionalProperties&quot; : false , 
 &quot;required&quot; : [ &quot;name&quot; , &quot;type&quot; , &quot;size&quot; , &quot;children&quot; ] 
 } 
 } , 
 &quot;additionalProperties&quot; : false , 
 &quot;required&quot; : [ &quot;file_system&quot; ] 
 } 
 JSON Object Mode 
 JSON Object Mode provides basic JSON output validation without schema enforcement. Unlike Structured Outputs with json_schema mode, it is designed to output valid JSON syntax but not schema compliance. The endpoint will either return valid JSON or throw an error if the model cannot produce valid JSON syntax. Use Structured Outputs when available for your use case. 
 Strict Mode Best-effort Mode JSON Object Mode Valid JSON Always ✓ Usually ✓ Usually ✓ Schema adherence Guaranteed ✓ Best-effort No Can error No Occasionally Occasionally Requires schema Yes Yes No Model support Multiple models Multiple models All models Use case Production apps Development, broader compatibility Simple JSON without schema 
 Enable JSON Object Mode by setting response_format to { &quot;type&quot;: &quot;json_object&quot; } . 
 Requirements and limitations: 
 Include explicit JSON instructions in your prompt (system message or user input) 
 Outputs are syntactically valid JSON but may not match your intended schema 
 Combine with validation libraries and retry logic for schema compliance 
 Sentiment Analysis Example 
 This example shows prompt-guided JSON generation for sentiment analysis, adaptable to classification, extraction, or summarization tasks: 
 Python import { Groq } from &quot;groq-sdk&quot;;
const groq = new Groq();
async function main() {
 const response = await groq.chat.completions.create({
 model: &quot;openai/gpt-oss-20b&quot;,
 messages: [
 {
 role: &quot;system&quot;,
 content: `You are a data analysis API that performs sentiment analysis on text.
 Respond only with JSON using this format:
 {
 &quot;sentiment_analysis&quot;: {
 &quot;sentiment&quot;: &quot;positive|negative|neutral&quot;,
 &quot;confidence_score&quot;: 0.95,
 &quot;key_phrases&quot;: [
 {
 &quot;phrase&quot;: &quot;detected key phrase&quot;,
 &quot;sentiment&quot;: &quot;positive|negative|neutral&quot;
 }
 ],
 &quot;summary&quot;: &quot;One sentence summary of the overall sentiment&quot;
 }
 }`
 },
 { role: &quot;user&quot;, content: &quot;Analyze the sentiment of this customer review: &#x27;I absolutely love this product! The quality exceeded my expectations, though shipping took longer than expected.&#x27;&quot; }
 ],
 response_format: { type: &quot;json_object&quot; }
 });
 const result = JSON.parse(response.choices[0].message.content || &quot;{}&quot;);
 console.log(result);
}
main(); from groq import Groq
 import json
 client = Groq ( ) 
 def main ( ) : 
 response = client . chat . completions . create ( 
 model = &quot;llama-3.3-70b-versatile&quot; , 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;&quot;&quot;You are a data analysis API that performs sentiment analysis on text.
 Respond only with JSON using this format:
 {
 &quot;sentiment_analysis&quot;: {
 &quot;sentiment&quot;: &quot;positive|negative|neutral&quot;,
 &quot;confidence_score&quot;: 0.95,
 &quot;key_phrases&quot;: [
 {
 &quot;phrase&quot;: &quot;detected key phrase&quot;,
 &quot;sentiment&quot;: &quot;positive|negative|neutral&quot;
 }
 ],
 &quot;summary&quot;: &quot;One sentence summary of the overall sentiment&quot;
 }
 }&quot;&quot;&quot; 
 } , 
 { 
 &quot;role&quot; : &quot;user&quot; , 
 &quot;content&quot; : &quot;Analyze the sentiment of this customer review: &#x27;I absolutely love this product! The quality exceeded my expectations, though shipping took longer than expected.&#x27;&quot; 
 } 
 ] , 
 response_format = { &quot;type&quot; : &quot;json_object&quot; } 
 ) 
 result = json . loads ( response . choices [ 0 ] . message . content ) 
 print ( json . dumps ( result , indent = 2 ) ) 
 if __name__ == &quot;__main__&quot; : 
 main ( ) curl https://api.groq.com/openai/v1/chat/completions \
 -H &quot;Authorization: Bearer $GROQ_API_KEY&quot; \
 -H &quot;Content-Type: application/json&quot; \
 -d &#x27;{
 &quot;model&quot;: &quot;llama-3.3-70b-versatile&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;system&quot;,
 &quot;content&quot;: &quot;You are a data analysis API that performs sentiment analysis on text. Respond only with JSON using this format: { \&quot;sentiment_analysis\&quot;: { \&quot;sentiment\&quot;: \&quot;positive|negative|neutral\&quot;, \&quot;confidence_score\&quot;: 0.95, \&quot;key_phrases\&quot;: [ { \&quot;phrase\&quot;: \&quot;detected key phrase\&quot;, \&quot;sentiment\&quot;: \&quot;positive|negative|neutral\&quot; } ], \&quot;summary\&quot;: \&quot;One sentence summary of the overall sentiment\&quot; } }&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Analyze the sentiment of this customer review: &#x27;\&#x27;&#x27;I absolutely love this product! The quality exceeded my expectations, though shipping took longer than expected.&#x27;\&#x27;&#x27;&quot;
 }
 ],
 &quot;response_format&quot;: { &quot;type&quot;: &quot;json_object&quot; }
 }&#x27; 
 System prompts structure the output format while maintaining JSON validity. However, keep in mind that the JSON object output may not match your schema. 
 Example Output JSON { 
 &quot;sentiment_analysis&quot; : { 
 &quot;sentiment&quot; : &quot;positive&quot; , 
 &quot;confidence_score&quot; : 0.84 , 
 &quot;key_phrases&quot; : [ 
 { 
 &quot;phrase&quot; : &quot;absolutely love this product&quot; , 
 &quot;sentiment&quot; : &quot;positive&quot; 
 } , 
 { 
 &quot;phrase&quot; : &quot;quality exceeded my expectations&quot; , 
 &quot;sentiment&quot; : &quot;positive&quot; 
 } 
 ] , 
 &quot;summary&quot; : &quot;The reviewer loves the product&#x27;s quality, but was slightly disappointed with the shipping time.&quot; 
 } 
 } 
 Response structure: 
 sentiment : Classification (positive/negative/neutral) 
 confidence_score : Confidence level (0-1 scale) 
 key_phrases : Extracted phrases with individual sentiment scores 
 summary : Analysis overview and main findings 
 Was this page helpful? Yes No Suggest Edits On this page 