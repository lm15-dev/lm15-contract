 
 JSON Output | DeepSeek API Docs 
 Skip to main content DeepSeek API Docs English English 中文（中国） DeepSeek Platform Quick Start Your First API Call Models &amp; Pricing Token &amp; Token Usage Rate Limit &amp; Isolation Error Codes Agent Integrations API Guides Vision Thinking Mode Multi-round Conversation Chat Prefix Completion (Beta) FIM Completion (Beta) JSON Output Tool Calls Files API Context Caching Using the Responses API Using the Anthropic API API Reference News Other Resources FAQ Change Log API Guides JSON Output On this page JSON Output 
 In many scenarios, users need the model to output in strict JSON format to achieve structured output, facilitating subsequent parsing. 
 DeepSeek provides JSON Output to ensure the model outputs valid JSON strings. 
 Notice ​ 
 To enable JSON Output, users should: 
 Set the response_format parameter to {&#x27;type&#x27;: &#x27;json_object&#x27;} . 
 Include the word &quot;json&quot; in the system or user prompt, and provide an example of the desired JSON format to guide the model in outputting valid JSON. 
 Set the max_tokens parameter reasonably to prevent the JSON string from being truncated midway. 
 When using the JSON Output feature, the API may occasionally return empty content. We are actively working on optimizing this issue. You can try modifying the prompt to mitigate such problems. 
 Sample Code ​ 
 Here is the complete Python code demonstrating the use of JSON Output: 
 import json from openai import OpenAI client = OpenAI ( api_key = &quot;&lt;your api key&gt;&quot; , base_url = &quot;https://api.deepseek.com&quot; , ) system_prompt = &quot;&quot;&quot; The user will provide some exam text. Please parse the &quot;question&quot; and &quot;answer&quot; and output them in JSON format. EXAMPLE INPUT: Which is the highest mountain in the world? Mount Everest. EXAMPLE JSON OUTPUT: { &quot;question&quot;: &quot;Which is the highest mountain in the world?&quot;, &quot;answer&quot;: &quot;Mount Everest&quot; } &quot;&quot;&quot; user_prompt = &quot;Which is the longest river in the world? The Nile River.&quot; messages = [ { &quot;role&quot; : &quot;system&quot; , &quot;content&quot; : system_prompt } , { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : user_prompt } ] response = client . chat . completions . create ( model = &quot;deepseek-v4-pro&quot; , messages = messages , response_format = { &#x27;type&#x27; : &#x27;json_object&#x27; } ) print ( json . loads ( response . choices [ 0 ] . message . content ) ) 
 The model will output: 
 { &quot;question&quot;: &quot;Which is the longest river in the world?&quot;, &quot;answer&quot;: &quot;The Nile River&quot; } Previous FIM Completion (Beta) Next Tool Calls Notice Sample Code WeChat Official Account 
 Community Email Discord Twitter More GitHub Copyright © 2026 DeepSeek, Inc. 
 