
 Use deep thinking models via API | Model Studio - Alibaba Cloud Model Studio - Alibaba Cloud Documentation Center
 -->
Document Center
 &nbsp; 
 All Products 
Search
 Document Center 
 Alibaba Cloud Model Studio 
 User Guide (Models) 
 Model Playground 
 Text generation 
 Deep thinking 
all-products-head 
 This Product 
 This Product 
 All Products 
 Alibaba Cloud Model Studio:Deep thinking 
Document Center
 Alibaba Cloud Model Studio:Deep thinking 
Last Updated:Sep 02, 2026
 Deep thinking models reason before responding, improving accuracy on complex tasks like logical reasoning and math. 
 These examples use the OpenAI-compatible Chat Completion API and DashScope API. For the Responses API, see Deep thinking . 
 Usage 
 Model Studio supports deep thinking in two modes: 
 Hybrid thinking mode : Use the enable_thinking parameter to switch between thinking and non-thinking on a per-request basis: 
 Set to true — the model reasons before responding. 
 Set to false — the model responds directly, skipping the reasoning step. 
 OpenAI compatible 
 # Import dependencies and create a client...
completion = client.chat.completions.create(
 model=&quot;qwen3.8-max&quot;, # Select a model
 messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;Who are you&quot;}],
 # Since enable_thinking is not a standard OpenAI parameter, pass it in extra_body.
 extra_body={&quot;enable_thinking&quot;:True},
 # Enable streaming output.
 stream=True,
 # Configure the stream to include token consumption information in the last data packet.
 stream_options={
 &quot;include_usage&quot;: True
 }
)
 DashScope 
 The DashScope API for the Qwen3.5 series uses a multimodal interface. The following example returns a url error . For the correct usage, see Enable or disable thinking mode . 
 # Import dependencies...
response = MultiModalConversation.call(
 # If you have not set the environment variable, replace the next line with your Model Studio API key, for example: api_key = &quot;sk-xxx&quot;,
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 # You can use other deep thinking models as needed.
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 enable_thinking=True,
 stream=True,
 incremental_output=True
)
 Thinking-only mode : The model always reasons before responding — this behavior cannot be disabled. The request format is the same as hybrid thinking mode; no enable_thinking parameter is needed. 
 The API returns reasoning in the reasoning_content field and the answer in the content field. Because reasoning adds latency, all examples use streaming by default (recommended, so you can watch the reasoning in real time). Commercial thinking models also support non-streaming (synchronous) output; see the FAQ below for usage and caveats. Some models (such as the open-source qwen3-235b-a22b and qwen3-32b) support streaming only, and a non-streaming call returns an error. 
 Supported models 
 Qwen3.8 Qwen3.8 Max series (hybrid thinking mode, thinking enabled by default ): qwen3.8-max Qwen3.8 Flash series (hybrid thinking mode, thinking enabled by default ): qwen3.8-flash Qwen3.7 Qwen3.7 Max series (hybrid thinking mode, thinking enabled by default ): qwen3.7-max, qwen3.7-max-us, qwen3.7-max-2026-05-20, qwen3.7-max-2026-06-08 Qwen3.7 Max series ( thinking mode only ): qwen3.7-max-preview, qwen3.7-max-2026-05-17 Qwen3.7 Plus series (hybrid thinking mode, thinking enabled by default ): qwen3.7-plus, qwen3.7-plus-us, qwen3.7-plus-2026-05-26 Qwen3.7 Plus series (hybrid thinking mode, thinking enabled by default ): qwen3.7-flash, qwen3.7-flash-2026-07-15 Qwen3.6 Qwen3.6 Max series (hybrid thinking mode, thinking enabled by default ): qwen3.6-max-preview Qwen3.6 Plus series (hybrid thinking mode, thinking enabled by default ): qwen3.6-plus, qwen3.6-plus-2026-04-02 Qwen3.6 Flash series (hybrid thinking mode, thinking enabled by default ): qwen3.6-flash, qwen3.6-flash-2026-04-16 Open-source Qwen3.6 : qwen3.6-35b-a3b Qwen3.5 
 Commercial 
 Qwen3.5 Plus series (hybrid thinking mode, thinking enabled by default ): qwen3.5-plus, qwen3.5-plus-2026-02-15 
 Qwen3.5 Flash series (hybrid thinking mode, thinking enabled by default ): qwen3.5-flash, qwen3.5-flash-2026-02-23 
 Open-source 
 Hybrid thinking mode, thinking enabled by default : qwen3.5-397b-a17b, qwen3.5-122b-a10b, qwen3.5-27b, qwen3.5-35b-a3b 
 Qwen3 
 Commercial 
 Qwen Max series (hybrid thinking mode, thinking disabled by default): qwen3-max, qwen3-max-2026-01-23, qwen3-max-preview 
 Qwen Plus series (hybrid thinking mode, thinking disabled by default): qwen-plus, qwen-plus-latest, qwen-plus-2025-04-28 and later snapshot versions 
 Qwen Flash series (hybrid thinking mode, thinking disabled by default): qwen-flash, qwen-flash-2025-07-28 and later snapshot versions 
 Qwen Turbo series (hybrid thinking mode, thinking disabled by default): qwen-turbo and later snapshot versions 
 Open-source 
 Hybrid thinking mode, thinking enabled by default: qwen3-235b-a22b, qwen3-32b, qwen3-30b-a3b, qwen3-14b, qwen3-8b 
 Thinking-only mode: qwen3-next-80b-a3b-thinking, qwen3-235b-a22b-thinking-2507, qwen3-30b-a3b-thinking-2507 
 QwQ (based on Qwen2.5) Thinking-only mode: qwq-plus DeepSeek 
 Deployed on Alibaba Cloud Model Studio 
 Hybrid thinking mode, thinking disabled by default: deepseek-v4-pro, deepseek-v4-flash, deepseek-v3.2, deepseek-v3.2-exp, deepseek-v3.1 
 Thinking-only mode: deepseek-r1, deepseek-r1-0528, deepseek-r1 distilled models 
 Deployed on SiliconFlow 
 Hybrid thinking mode, thinking disabled by default: siliconflow/deepseek-v3.2, siliconflow/deepseek-v3.1-terminus 
 Thinking-only mode: siliconflow/deepseek-r1-0528 
 Deployed on Kuaishou Vanchin 
 Hybrid thinking mode, thinking disabled by default: vanchin/deepseek-v3.2-think, vanchin/deepseek-v3.1-terminus 
 Thinking-only mode: vanchin/deepseek-r1 
 GLM Hybrid thinking mode, thinking enabled by default: glm-5.2, glm-5.2-us, glm-5.2-fast-preview, glm-5.1, glm-5, glm-4.7, glm-4.6, glm-4.5, glm-4.5-air Kimi 
 Deployed on Alibaba Cloud Model Studio 
 Hybrid thinking mode, thinking disabled by default: kimi-k2.6, kimi-k2.5 
 Thinking-only mode: kimi-k2.7-code, kimi-k2-thinking 
 Deployed on Moonshot AI 
 Hybrid thinking mode, thinking enabled by default: kimi/kimi-k2.6, kimi/kimi-k2.5 
 Thinking-only mode: kimi/kimi-k2.7-code-highspeed, kimi/kimi-k2.7-code 
 MiniMax 
 Deployed on Alibaba Cloud Model Studio 
 Thinking-only mode: MiniMax-M2.5, MiniMax-M2.1 
 Model names, context windows, pricing, and snapshot versions are in the Model list . Rate limits are described in Rate limiting . 
 Getting started 
 Obtain an API key and set it as an environment variable. If you use an SDK, install the OpenAI or DashScope SDK (DashScope Java SDK version 2.19.4 or later is required). 
 The following example calls qwen3.8-max in thinking mode with streaming output. 
 OpenAI compatible Python Sample code from openai import OpenAI
import os
# Initialize the OpenAI client.
client = OpenAI(
 # API keys vary by region. To get an API key, see https://www.alibabacloud.com/help/en/model-studio/get-api-key
 # If an environment variable is not configured, provide your Model Studio API key directly: api_key=&quot;sk-xxx&quot;
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 # Configurations vary by region. Modify the base_url based on your region.
 base_url=&quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&quot;,
)
messages = [{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;Who are you&quot;}]
completion = client.chat.completions.create(
 model=&quot;qwen3.8-max&quot;, # You can replace this with other deep-thinking models as needed.
 messages=messages,
 extra_body={&quot;enable_thinking&quot;: True},
 stream=True,
 stream_options={
 &quot;include_usage&quot;: True
 },
)
reasoning_content = &quot;&quot; # Full thinking process
answer_content = &quot;&quot; # Full response
is_answering = False # Tracks if the response phase has started
print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Thinking process&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
for chunk in completion:
 if not chunk.choices:
 print(&quot;\nUsage:&quot;)
 print(chunk.usage)
 continue
 delta = chunk.choices[0].delta
 # Collect only the reasoning content.
 if hasattr(delta, &quot;reasoning_content&quot;) and delta.reasoning_content is not None:
 if not is_answering:
 print(delta.reasoning_content, end=&quot;&quot;, flush=True)
 reasoning_content += delta.reasoning_content
 # When content is received, start responding.
 if hasattr(delta, &quot;content&quot;) and delta.content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Full response&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
 is_answering = True
 print(delta.content, end=&quot;&quot;, flush=True)
 answer_content += delta.content
 Response ====================Thinking process====================
The user&#x27;s query &quot;Who are you?&quot; requires an accurate and friendly response. The answer should first establish my identity as Qwen, developed by Tongyi Lab at Alibaba Cloud. It will then outline key capabilities such as question answering, text generation, and logical reasoning. The language must be simple and the tone approachable. To encourage interaction, I will invite the user to ask more questions. Finally, I&#x27;ll check that all key details are present, including my name (Qwen) and developer, to provide a comprehensive answer.
====================Full response====================
Hello! I am Qwen, a large language model developed by Tongyi Lab at Alibaba Group. I can answer questions, generate text, perform logical reasoning, write code, and more, to provide you with high-quality information and services. You can call me Qwen. How can I help you?
 Node.js Sample code import OpenAI from &quot;openai&quot;;
import process from &#x27;process&#x27;;
// Initialize the OpenAI client.
const openai = new OpenAI({
 apiKey: process.env.DASHSCOPE_API_KEY, // Read from an environment variable.
 // The following is the base URL for the Singapore region. If you use models in the US (Virginia) region, change the base URL to https://{WorkspaceId}.us-east-1.maas.aliyuncs.com/compatible-mode/v1. The base URL varies by region. Update it for your deployment&#x27;s region.
 baseURL: &#x27;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&#x27;
});
let reasoningContent = &#x27;&#x27;;
let answerContent = &#x27;&#x27;;
let isAnswering = false;
async function main() {
 try {
 const messages = [{ role: &#x27;user&#x27;, content: &#x27;Who are you&#x27; }];
 const stream = await openai.chat.completions.create({
 model: &#x27;qwen-plus&#x27;,
 messages,
 stream: true,
 enable_thinking: true
 });
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Thinking process&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;\n&#x27;);
 for await (const chunk of stream) {
 if (!chunk.choices?.length) {
 console.log(&#x27;\nUsage:&#x27;);
 console.log(chunk.usage);
 continue;
 }
 const delta = chunk.choices[0].delta;
 // Collect only the reasoning content.
 if (delta.reasoning_content !== undefined &amp;&amp; delta.reasoning_content !== null) {
 if (!isAnswering) {
 process.stdout.write(delta.reasoning_content);
 }
 reasoningContent += delta.reasoning_content;
 }
 // When content is received, start responding.
 if (delta.content !== undefined &amp;&amp; delta.content) {
 if (!isAnswering) {
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Full response&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;\n&#x27;);
 isAnswering = true;
 }
 process.stdout.write(delta.content);
 answerContent += delta.content;
 }
 }
 } catch (error) {
 console.error(&#x27;Error:&#x27;, error);
 }
}
main();
 Response ====================Thinking process====================
The user&#x27;s direct query &quot;Who are you?&quot; requires a concise and clear response. The answer will state my identity as Qwen, a large language model from Alibaba Cloud. It will mention key functions like question answering, text generation, and logical reasoning, and highlight multilingual support (Chinese, English). To remain concise, use cases will be mentioned briefly, if at all. The tone will be friendly, and the response will end with an invitation for further questions. Finally, I&#x27;ll check to ensure accuracy without including unnecessary details like version numbers.
====================Full response====================
I am Qwen, a large language model developed by Tongyi Lab at Alibaba Group. I can perform a variety of tasks, including answering questions, generating text, logical reasoning, and coding, and I support multiple languages, including Chinese and English. If you have any questions or need help, feel free to ask me at any time!
 HTTP Sample code curl # ======= Important =======
# The following URL is for the Singapore region. For the China (Beijing) region, replace the URL with: https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
# For the US (Virginia) region, replace it with: https://{WorkspaceId}.us-east-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions
# === Remove this comment before execution ===
curl -X POST https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions \
-H &quot;Authorization: Bearer $DASHSCOPE_API_KEY&quot; \
-H &quot;Content-Type: application/json&quot; \
-d &#x27;{
 &quot;model&quot;: &quot;qwen3.8-max&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Who are you&quot;
 }
 ],
 &quot;stream&quot;: true,
 &quot;stream_options&quot;: {
 &quot;include_usage&quot;: true
 },
 &quot;enable_thinking&quot;: true
}&#x27;
 Response data: {&quot;choices&quot;:[{&quot;delta&quot;:{&quot;content&quot;:null,&quot;role&quot;:&quot;assistant&quot;,&quot;reasoning_content&quot;:&quot;&quot;},&quot;index&quot;:0,&quot;logprobs&quot;:null,&quot;finish_reason&quot;:null}],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:null,&quot;created&quot;:1745485391,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-e2edaf2c-8aaf-9e54-90e2-b21dd5045503&quot;}
.....
data: {&quot;choices&quot;:[{&quot;finish_reason&quot;:&quot;stop&quot;,&quot;delta&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:null},&quot;index&quot;:0,&quot;logprobs&quot;:null}],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:null,&quot;created&quot;:1745485391,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-e2edaf2c-8aaf-9e54-90e2-b21dd5045503&quot;}
data: {&quot;choices&quot;:[],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:{&quot;prompt_tokens&quot;:10,&quot;completion_tokens&quot;:360,&quot;total_tokens&quot;:370},&quot;created&quot;:1745485391,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-e2edaf2c-8aaf-9e54-90e2-b21dd5045503&quot;}
data: [DONE]
 DashScope 
 Because the DashScope API for the Qwen3.5 series uses a multimodal interface, the following example returns a url error . For the correct usage, see Enable or disable thinking mode . 
 Python Sample code import os
from dashscope import MultiModalConversation
import dashscope
# Configurations vary by region. Modify this value based on your region.
dashscope.base_http_api_url = &quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1&quot;
# Initialize request parameters
messages = [{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: [{&quot;text&quot;: &quot;Who are you?&quot;}]}]
completion = MultiModalConversation.call(
 # If an environment variable is not configured, replace the following line with your Model Studio API key: api_key = &quot;sk-xxx&quot;,
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 enable_thinking=True,
 stream=True,
 incremental_output=True,
)
# Full thinking process
reasoning_content = &quot;&quot;
# Full response
answer_content = &quot;&quot;
# Tracks if the response phase has started.
is_answering = False
print(&quot;=&quot; * 20 + &quot;Thinking process&quot; + &quot;=&quot; * 20)
for chunk in completion:
 # If both the thinking and response content are empty, ignore the chunk.
 content = chunk.output.choices[0].message.content
 reasoning = chunk.output.choices[0].message.reasoning_content
 if not content and reasoning == &quot;&quot;:
 pass
 else:
 # If the current chunk is part of the thinking process.
 if reasoning != &quot;&quot; and not content:
 print(reasoning, end=&quot;&quot;, flush=True)
 reasoning_content += reasoning
 # If the current chunk is part of the response.
 elif content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Full response&quot; + &quot;=&quot; * 20)
 is_answering = True
 print(content[0][&quot;text&quot;], end=&quot;&quot;, flush=True)
 answer_content += content[0][&quot;text&quot;]
# To print the full thinking process and full response, uncomment the following code.
# print(&quot;=&quot; * 20 + &quot;Full thinking process&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
# print(f&quot;{reasoning_content}&quot;)
# print(&quot;=&quot; * 20 + &quot;Full response&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
# print(f&quot;{answer_content}&quot;)
 Response ====================Thinking process====================
To answer the query &quot;Who are you?&quot;, the response must state my identity as Qwen, a large language model from Alibaba Cloud. It will then explain my purpose as a helpful assistant by outlining key functions like question answering, text generation, and logical reasoning. The response will maintain a conversational tone, avoiding jargon. To encourage further engagement, it will end with an open-ended question. Finally, I&#x27;ll check for clarity, conciseness, and a balance between a friendly and professional tone.
====================Full response====================
Hello! I am Qwen, a large-scale language model developed by Alibaba Cloud. I can answer questions, generate text, perform logical reasoning, write code, and more, to provide help and support. Whether you have a question about daily life or a professional topic, I will do my best to help. Is there anything I can help you with?
 Java Sample code // The version of the DashScope SDK must be 2.19.4 or later.
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversation;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationParam;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationResult;
import com.alibaba.dashscope.common.MultiModalMessage;
import com.alibaba.dashscope.common.Role;
import com.alibaba.dashscope.exception.ApiException;
import com.alibaba.dashscope.exception.InputRequiredException;
import com.alibaba.dashscope.exception.NoApiKeyException;
import com.alibaba.dashscope.exception.UploadFileException;
import io.reactivex.Flowable;
import java.lang.System;
import com.alibaba.dashscope.utils.Constants;
public class Main {
 static {
 // The following base_url is for the Singapore region. If you use a model in the Virginia region, you must change the base_url to https://{WorkspaceId}.us-east-1.maas.aliyuncs.com/api/v1.
 // Configurations vary by region. Modify the configuration based on your actual region.
 Constants.baseHttpApiUrl=&quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1&quot;;
 }
 private static final Logger logger = LoggerFactory.getLogger(Main.class);
 private static StringBuilder reasoningContent = new StringBuilder();
 private static StringBuilder finalContent = new StringBuilder();
 private static boolean isFirstPrint = true;
 private static void handleMultiModalConversationResult(MultiModalConversationResult message) {
 String reasoning = message.getOutput().getChoices().get(0).getMessage().getReasoningContent();
 List&lt;Map&lt;String, Object&gt;&gt; contentList = (List&lt;Map&lt;String, Object&gt;&gt;) message.getOutput().getChoices().get(0).getMessage().getContent();
 String content = (contentList != null &amp;&amp; !contentList.isEmpty()) ? (String) contentList.get(0).get(&quot;text&quot;) : &quot;&quot;;
 if (!reasoning.isEmpty()) {
 reasoningContent.append(reasoning);
 if (isFirstPrint) {
 System.out.println(&quot;====================Thinking Process====================&quot;);
 isFirstPrint = false;
 }
 System.out.print(reasoning);
 }
 if (!content.isEmpty()) {
 finalContent.append(content);
 if (!isFirstPrint) {
 System.out.println(&quot;\n====================Complete Response====================&quot;);
 isFirstPrint = true;
 }
 System.out.print(content);
 }
 }
 private static MultiModalConversationParam buildMultiModalConversationParam(MultiModalMessage userMsg) {
 return MultiModalConversationParam.builder()
 // API keys vary by region. To obtain an API key, visit https://www.alibabacloud.com/help/en/model-studio/get-api-key
 // If you have not configured the environment variable, replace the following line with your Alibaba Cloud Model Studio API key: .apiKey(&quot;sk-xxx&quot;)
 .apiKey(System.getenv(&quot;DASHSCOPE_API_KEY&quot;))
 .model(&quot;qwen3.8-max&quot;)
 .enableThinking(true)
 .incrementalOutput(true)
 .messages(Arrays.asList(userMsg))
 .build();
 }
 public static void streamCallWithMessage(MultiModalConversation conv, MultiModalMessage userMsg)
 throws NoApiKeyException, ApiException, InputRequiredException, UploadFileException {
 MultiModalConversationParam param = buildMultiModalConversationParam(userMsg);
 Flowable&lt;MultiModalConversationResult&gt; result = conv.streamCall(param);
 result.blockingForEach(message -&gt; handleMultiModalConversationResult(message));
 }
 public static void main(String[] args) {
 try {
 MultiModalConversation conv = new MultiModalConversation();
 MultiModalMessage userMsg = MultiModalMessage.builder().role(Role.USER.getValue()).content(Arrays.asList(Collections.singletonMap(&quot;text&quot;, &quot;Who are you?&quot;))).build();
 streamCallWithMessage(conv, userMsg);
// Print the final result.
// if (reasoningContent.length() &gt; 0) {
// System.out.println(&quot;\n====================Complete Response====================&quot;);
// System.out.println(finalContent.toString());
// }
 } catch (ApiException | NoApiKeyException | InputRequiredException | UploadFileException e) {
 logger.error(&quot;An exception occurred: {}&quot;, e.getMessage());
 }
 System.exit(0);
 }
}
 Response ====================Thinking process====================
The response to &quot;Who are you?&quot; must be based on my predefined identity as Qwen, a large language model from Alibaba Cloud. The answer will be conversational, concise, and easy to understand. It will first state my identity, then explain my functions, including text creation, logical reasoning, coding, and multilingual support. The tone will be friendly, and the response will end with an invitation for the user to ask for help, to encourage further interaction.
====================Full response====================
Hello! I am Qwen, a large language model from Alibaba Group. I can answer questions; create text such as stories, official documents, emails, and scripts; perform logical reasoning; write code; express opinions; and even play games. I am proficient in multiple languages, including but not limited to Chinese, English, German, French, and Spanish. Is there anything I can help you with?
 HTTP Sample code curl # ======= Important =======
# API keys vary by region. To get an API key, see https://www.alibabacloud.com/help/en/model-studio/get-api-key
# The following is the URL for the Singapore region. For the China (Beijing) region, replace the URL with: https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
# For the US (Virginia) region, replace the URL with: https://{WorkspaceId}.us-east-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
# === Remove this comment before execution ===
curl -X POST &quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation&quot; \
-H &quot;Authorization: Bearer $DASHSCOPE_API_KEY&quot; \
-H &quot;Content-Type: application/json&quot; \
-H &quot;X-DashScope-SSE: enable&quot; \
-d &#x27;{
 &quot;model&quot;: &quot;qwen3.8-max&quot;,
 &quot;input&quot;:{
 &quot;messages&quot;:[
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: [{&quot;text&quot;: &quot;Who are you?&quot;}]
 }
 ]
 },
 &quot;parameters&quot;:{
 &quot;enable_thinking&quot;: true,
 &quot;incremental_output&quot;: true,
 &quot;result_format&quot;: &quot;message&quot;
 }
}&#x27;
 Response id:1
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;Hmm&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:14,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:3},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:2
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;,&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:15,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:4},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:3
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;user&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:16,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:5},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:4
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;asks&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:17,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:6},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:5
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;“&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:18,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:7},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
......
id:358
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;help&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:373,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:362},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:359
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;,&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:374,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:363},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:360
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;Please feel free&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:375,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:364},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:361
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;to&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:376,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:365},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:362
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;let me know&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:377,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:366},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:363
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;!&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:378,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:367},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:364
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;stop&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:378,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:367},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
 Core capabilities 
 Toggle thinking and non-thinking modes 
 Thinking mode improves response quality but adds latency and cost. On hybrid thinking models, toggle it per request based on query complexity: 
 Set enable_thinking to false for simple queries — casual conversation, straightforward Q&amp;A. 
 Set enable_thinking to true for complex reasoning — logic problems, code generation, or math. 
 OpenAI compatible Important enable_thinking is not a standard OpenAI parameter. In the OpenAI Python SDK, pass it via extra_body . In the Node.js SDK, pass it as a top-level parameter. Python Sample code from openai import OpenAI
import os
# Initialize the OpenAI client.
client = OpenAI(
 # If the environment variable is not configured, replace the value with your Model Studio API key: api_key=&quot;sk-xxx&quot;
 # API keys differ by region. To get an API key, see https://www.alibabacloud.com/help/en/model-studio/get-api-key
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 # The following URL is for the Singapore region. When calling, replace WorkspaceId with your actual workspace ID. URLs vary by region.
 base_url=&quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&quot;,
)
messages = [{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;Who are you?&quot;}]
completion = client.chat.completions.create(
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 # Set enable_thinking in extra_body to enable the reasoning process.
 extra_body={&quot;enable_thinking&quot;: True},
 stream=True,
 stream_options={
 &quot;include_usage&quot;: True
 },
)
reasoning_content = &quot;&quot; # Full reasoning process
answer_content = &quot;&quot; # Full response
is_answering = False # Indicates if the response phase has started
print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Reasoning process&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
for chunk in completion:
 if not chunk.choices:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Token usage&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
 print(chunk.usage)
 continue
 delta = chunk.choices[0].delta
 # Collect only the reasoning content.
 if hasattr(delta, &quot;reasoning_content&quot;) and delta.reasoning_content is not None:
 if not is_answering:
 print(delta.reasoning_content, end=&quot;&quot;, flush=True)
 reasoning_content += delta.reasoning_content
 # When content is received, start the response.
 if hasattr(delta, &quot;content&quot;) and delta.content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Full response&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
 is_answering = True
 print(delta.content, end=&quot;&quot;, flush=True)
 answer_content += delta.content
 Response ====================Reasoning process====================
The user is asking &quot;Who are you?&quot;. I need to determine what they want to know. They might be interacting with me for the first time or want to confirm my identity. I should introduce myself as Qwen, developed by Tongyi Lab. Then, I should explain my capabilities, such as answering questions, creating text, and coding, so the user understands how I can assist them. I should also mention my multilingual support so international users know they can communicate in different languages. Finally, I should maintain a friendly tone and invite them to ask questions to encourage further interaction. The explanation must be clear and simple, avoiding technical jargon. The user likely wants a quick overview of my abilities, so I will focus on my functions and applications. I should also consider if any information is missing, such as mentioning Alibaba Group or more technical details. However, the user probably only needs basic information. I will ensure the response is friendly and professional, and encourages them to continue the conversation.
====================Full response====================
I am Qwen, a large-scale language model developed by Tongyi Lab. I can help you answer questions, create text, code, and express opinions. I support communication in multiple languages. How can I help you?
====================Token usage====================
CompletionUsage(completion_tokens=221, prompt_tokens=10, total_tokens=231, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=None, reasoning_tokens=172, rejected_prediction_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0))
 Node.js Sample code import OpenAI from &quot;openai&quot;;
import process from &#x27;process&#x27;;
// Initialize the OpenAI client.
const openai = new OpenAI({
 // If the environment variable is not configured, replace the value with your Model Studio API key: apiKey: &quot;sk-xxx&quot;
 apiKey: process.env.DASHSCOPE_API_KEY,
 // Configurations vary by region. Modify this based on your actual region.
 baseURL: &#x27;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&#x27;
});
let reasoningContent = &#x27;&#x27;; // Full reasoning process
let answerContent = &#x27;&#x27;; // Full response
let isAnswering = false; // Indicates if the response phase has started
async function main() {
 try {
 const messages = [{ role: &#x27;user&#x27;, content: &#x27;Who are you?&#x27; }];
 const stream = await openai.chat.completions.create({
 model: &#x27;qwen-plus&#x27;,
 messages,
 // In the Node.js SDK, non-standard parameters such as enable_thinking are passed as top-level properties and are not required in extra_body.
 enable_thinking: true,
 stream: true,
 stream_options: {
 include_usage: true
 },
 });
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Reasoning process&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;\n&#x27;);
 for await (const chunk of stream) {
 if (!chunk.choices?.length) {
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Token usage&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;\n&#x27;);
 console.log(chunk.usage);
 continue;
 }
 const delta = chunk.choices[0].delta;
 // Collect only the reasoning content.
 if (delta.reasoning_content !== undefined &amp;&amp; delta.reasoning_content !== null) {
 if (!isAnswering) {
 process.stdout.write(delta.reasoning_content);
 }
 reasoningContent += delta.reasoning_content;
 }
 // When content is received, start the response.
 if (delta.content !== undefined &amp;&amp; delta.content) {
 if (!isAnswering) {
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Full response&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;\n&#x27;);
 isAnswering = true;
 }
 process.stdout.write(delta.content);
 answerContent += delta.content;
 }
 }
 } catch (error) {
 console.error(&#x27;Error:&#x27;, error);
 }
}
main();
 Response ====================Reasoning process====================
The user is asking &quot;Who are you?&quot;. I need to determine what they want to know. They might be interacting with me for the first time or want to confirm my identity. I should introduce myself as Qwen, and mention my English name is also Qwen. Then, I will state that I am a large-scale language model independently developed by Tongyi Lab at Alibaba Group. Next, I should list my capabilities, such as answering questions, creating text, coding, and expressing opinions, so the user understands my purpose. I should also mention my multilingual support, which international users will find useful. Finally, I will invite them to ask questions with a friendly and open attitude. I must use simple, easy-to-understand language and avoid excessive technical jargon. The user may need help or just be curious, so the response should be welcoming and encourage further interaction. I should also consider if the user has deeper needs, such as testing my abilities or seeking specific help, but the initial response will focus on basic information and guidance. I will keep the tone conversational and use simple sentences for effective communication.
====================Full response====================
Hello! I am Qwen. I am a large-scale language model independently developed by Tongyi Lab at Alibaba Group. I can help you answer questions, create text such as stories, official documents, emails, and scripts, perform logical reasoning, code, and even express opinions and play games. I support multiple languages, including but not limited to Chinese, English, German, French, and Spanish.
If you have any questions or need help, feel free to ask!
====================Token usage====================
{
 prompt_tokens: 10,
 completion_tokens: 288,
 total_tokens: 298,
 completion_tokens_details: { reasoning_tokens: 188 },
 prompt_tokens_details: { cached_tokens: 0 }
}
 HTTP Sample code curl # ======= IMPORTANT =======
# API keys differ by region. To get an API key, see https://www.alibabacloud.com/help/en/model-studio/get-api-key
# The base_url varies by region. For more information, see https://www.alibabacloud.com/help/en/model-studio/regions/
# === Delete this comment before execution ===
curl -X POST https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions \
-H &quot;Authorization: Bearer $DASHSCOPE_API_KEY&quot; \
-H &quot;Content-Type: application/json&quot; \
-d &#x27;{
 &quot;model&quot;: &quot;qwen3.8-max&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Who are you?&quot;
 }
 ],
 &quot;stream&quot;: true,
 &quot;stream_options&quot;: {
 &quot;include_usage&quot;: true
 },
 &quot;enable_thinking&quot;: true
}&#x27;
 DashScope 
 The DashScope API for the Qwen3.5 series uses a multimodal interface. The following examples return a url error . For the correct usage, see Enable or disable thinking mode . 
 Python Sample code import os
from dashscope import MultiModalConversation
import dashscope
# Configurations vary by region. Modify this as needed.
dashscope.base_http_api_url = &quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1/&quot;
# Initialize request parameters.
messages = [{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: [{&quot;text&quot;: &quot;Who are you?&quot;}]}]
completion = MultiModalConversation.call(
 # If you have not set an environment variable, replace this with your Model Studio API key: api_key=&quot;sk-xxx&quot;
 # API keys are region-specific. To get an API key, see https://www.alibabacloud.com/help/en/model-studio/regions
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 enable_thinking=True, # Enable the thinking process.
 stream=True, # Enable streaming output.
 incremental_output=True, # Enable incremental output.
)
reasoning_content = &quot;&quot; # Full thinking process
answer_content = &quot;&quot; # Full response
is_answering = False # Indicates if the model is in the answering phase.
print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Thinking process&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
for chunk in completion:
 message = chunk.output.choices[0].message
 # Collect only the thinking content.
 if message.reasoning_content:
 if not is_answering:
 print(message.reasoning_content, end=&quot;&quot;, flush=True)
 reasoning_content += message.reasoning_content
 # When content is received, start building the response.
 if message.content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Full response&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
 is_answering = True
 print(message.content[0][&quot;text&quot;], end=&quot;&quot;, flush=True)
 answer_content += message.content[0][&quot;text&quot;]
print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Token usage&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
print(chunk.usage)
# After the loop, the reasoning_content and answer_content variables contain the complete content.
# You can perform subsequent processing here as needed.
# print(f&quot;\n\nFull thinking process:\n{reasoning_content}&quot;)
# print(f&quot;\nFull response:\n{answer_content}&quot;)
 Response ====================Thinking process====================
Okay, the user is asking &quot;Who are you?&quot;. I need to figure out what they want to know. They might be new to me or just want to confirm my identity. First, I should introduce myself as Qwen and state that I am a large-scale language model from Tongyi Lab. Then, I should explain my capabilities, such as answering questions, writing text, and coding, so the user knows what I can do. I should also mention my multilingual support for international users. Finally, I will be friendly and invite them to ask more questions to encourage interaction. It is important to use simple language and avoid technical jargon. The user might have other needs, like testing my abilities or getting help, so providing specific examples like writing stories, official documents, or emails would be helpful. I also need to make sure the response is well-structured. I can list my functions, but a natural flow might be better than bullets. I must also clarify that I am an AI assistant without personal consciousness and that my answers are based on training data to prevent misunderstandings. I should check if I missed any important details, like my multimodal capabilities or recent updates, but it is probably not necessary to go into too much detail for a first response. In short, the answer should be comprehensive but concise, friendly, and helpful, making the user feel understood and supported.
====================Full response====================
I am Qwen, a large-scale language model developed by Tongyi Lab of Alibaba Group. I can help you with the following:
1. **Answering questions**: I can try to answer your academic, general knowledge, or domain-specific questions.
2. **Creating text**: I can help you write stories, official documents, emails, scripts, and more.
3. **Logical reasoning**: I can help you with logical reasoning and problem-solving.
4. **Programming**: I can understand and generate code in various programming languages.
5. **Multilingual support**: I support multiple languages, including but not limited to Chinese, English, German, French, and Spanish.
If you have any questions or need help, feel free to let me know!
====================Token usage====================
{&quot;input_tokens&quot;: 11, &quot;output_tokens&quot;: 405, &quot;total_tokens&quot;: 416, &quot;output_tokens_details&quot;: {&quot;reasoning_tokens&quot;: 256}, &quot;prompt_tokens_details&quot;: {&quot;cached_tokens&quot;: 0}}
 Java Sample code // Requires DashScope SDK v2.19.4 or later.
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversation;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationParam;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationResult;
import com.alibaba.dashscope.common.MultiModalMessage;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import com.alibaba.dashscope.common.Role;
import com.alibaba.dashscope.exception.ApiException;
import com.alibaba.dashscope.exception.InputRequiredException;
import com.alibaba.dashscope.exception.NoApiKeyException;
import com.alibaba.dashscope.utils.Constants;
import com.alibaba.dashscope.exception.UploadFileException;
import io.reactivex.Flowable;
import java.lang.System;
import java.util.Arrays;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
public class Main {
 static {
 // The base HTTP API URL varies by region. Modify it according to your region.
 Constants.baseHttpApiUrl=&quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1&quot;;
 }
 private static final Logger logger = LoggerFactory.getLogger(Main.class);
 private static StringBuilder reasoningContent = new StringBuilder();
 private static StringBuilder finalContent = new StringBuilder();
 private static boolean isFirstPrint = true;
 private static void handleMultiModalConversationResult(MultiModalConversationResult message) {
 String reasoning = message.getOutput().getChoices().get(0).getMessage().getReasoningContent();
 List&lt;Map&lt;String, Object&gt;&gt; contentList = (List&lt;Map&lt;String, Object&gt;&gt;) message.getOutput().getChoices().get(0).getMessage().getContent();
 String content = (contentList != null &amp;&amp; !contentList.isEmpty()) ? (String) contentList.get(0).get(&quot;text&quot;) : &quot;&quot;;
 if (!reasoning.isEmpty()) {
 reasoningContent.append(reasoning);
 if (isFirstPrint) {
 System.out.println(&quot;====================Thinking process====================&quot;);
 isFirstPrint = false;
 }
 System.out.print(reasoning);
 }
 if (!content.isEmpty()) {
 finalContent.append(content);
 if (!isFirstPrint) {
 System.out.println(&quot;\n====================Full response====================&quot;);
 isFirstPrint = true;
 }
 System.out.print(content);
 }
 }
 private static MultiModalConversationParam buildMultiModalConversationParam(MultiModalMessage userMsg) {
 return MultiModalConversationParam.builder()
 // If you have not set an environment variable, replace the next line with your Model Studio API key: .apiKey(&quot;sk-xxx&quot;)
 .apiKey(System.getenv(&quot;DASHSCOPE_API_KEY&quot;))
 .model(&quot;qwen3.8-max&quot;)
 .enableThinking(true)
 .incrementalOutput(true)
 .messages(Arrays.asList(userMsg))
 .build();
 }
 public static void streamCallWithMessage(MultiModalConversation conv, MultiModalMessage userMsg)
 throws NoApiKeyException, ApiException, InputRequiredException, UploadFileException {
 MultiModalConversationParam param = buildMultiModalConversationParam(userMsg);
 Flowable&lt;MultiModalConversationResult&gt; result = conv.streamCall(param);
 result.blockingForEach(message -&gt; handleMultiModalConversationResult(message));
 }
 public static void main(String[] args) {
 try {
 MultiModalConversation conv = new MultiModalConversation();
 MultiModalMessage userMsg = MultiModalMessage.builder().role(Role.USER.getValue()).content(Arrays.asList(Collections.singletonMap(&quot;text&quot;, &quot;Who are you?&quot;))).build();
 streamCallWithMessage(conv, userMsg);
// Print the final result.
// if (reasoningContent.length() &gt; 0) {
// System.out.println(&quot;\n====================Full response====================&quot;);
// System.out.println(finalContent.toString());
// }
 } catch (ApiException | NoApiKeyException | InputRequiredException | UploadFileException e) {
 logger.error(&quot;An exception occurred: {}&quot;, e.getMessage());
 }
 System.exit(0);
 }
}
 Response ====================Thinking process====================
Okay, the user is asking &quot;Who are you?&quot;. I need to figure out what they want to know. They might want to know my identity or are just testing my response. First, I should clearly state that I am Qwen, a large-scale language model from Alibaba Group. Then, I should briefly introduce my capabilities, such as answering questions, writing text, and coding, so the user understands what I can do. I should also mention that I support multiple languages so international users know they can communicate with me in different languages. Finally, I will be friendly and invite them to ask questions to make them feel comfortable and willing to interact further. The answer should not be too long but should be comprehensive. The user might have follow-up questions about my technical details or use cases, but the initial answer should be simple and clear. I will make sure not to use technical jargon so all users can understand. I will check for any missing important information, such as multilingual support and specific examples of my functions. Okay, this should cover the user&#x27;s needs.
====================Full response====================
I am Qwen, a large-scale language model from Alibaba Group. I can answer questions, create text (such as stories, official documents, emails, and scripts), perform logical reasoning, code, express opinions, and play games. I also support multilingual communication, including but not limited to Chinese, English, German, French, and Spanish. If you have any questions or need help, feel free to let me know!
 HTTP Sample code curl # ======= IMPORTANT =======
# API keys are region-specific. To get an API key, see https://www.alibabacloud.com/help/en/model-studio/get-api-key
# The base_url varies by region. Modify it as needed.
# === Delete this comment before running ===
curl -X POST &quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation&quot; \
-H &quot;Authorization: Bearer $DASHSCOPE_API_KEY&quot; \
-H &quot;Content-Type: application/json&quot; \
-H &quot;X-DashScope-SSE: enable&quot; \
-d &#x27;{
 &quot;model&quot;: &quot;qwen3.8-max&quot;,
 &quot;input&quot;:{
 &quot;messages&quot;:[
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: [{&quot;text&quot;: &quot;Who are you?&quot;}]
 }
 ]
 },
 &quot;parameters&quot;:{
 &quot;enable_thinking&quot;: true,
 &quot;incremental_output&quot;: true,
 &quot;result_format&quot;: &quot;message&quot;
 }
}&#x27;
 Response id:1
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;Hmm&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:14,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:3},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:2
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;,&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:15,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:4},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:3
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;user&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:16,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:5},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:4
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot; asks&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:17,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:6},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:5
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot; \&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:18,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:7},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
......
id:358
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;help&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:373,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:362},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:359
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;,&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:374,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:363},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:360
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot; feel free&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:375,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:364},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:361
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot; to&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:376,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:365},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:362
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot; let me know&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:377,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:366},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:363
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;!&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:378,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:367},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
id:364
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;stop&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:378,&quot;input_tokens&quot;:11,&quot;output_tokens&quot;:367},&quot;request_id&quot;:&quot;25d58c29-c47b-9e8d-a0f1-d6c309ec58b1&quot;}
 For the Qwen3 open-source hybrid thinking models, along with the qwen-plus-2025-04-28 and models , you can also control thinking mode with prompt suffixes. When enable_thinking is true , append /no_think to a prompt to skip reasoning for that turn, or append /think to re-enable it. The model always follows the most recent /think or /no_think instruction. 
 Limit thinking length 
 Reasoning traces increase latency and token costs. Use thinking_budget to cap reasoning tokens. When the limit is reached, the model stops reasoning and responds immediately. This applies to Qwen3.8, Qwen3.7, Qwen3.6, Qwen3.5, Qwen3-VL, Qwen3, GLM and Kimi models. 
 thinking_budget defaults to the model&#x27;s maximum chain-of-thought length. Check the default for each model on its console page. 
 OpenAI compatible Python Sample code from openai import OpenAI
import os
# Initialize the OpenAI client.
client = OpenAI(
 # If the environment variable is not configured, replace &quot;sk-xxx&quot; with your Model Studio API key.
 # API keys are region-specific. To get an API key, visit https://www.alibabacloud.com/help/en/model-studio/get-api-key.
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 # Configurations vary by region. Modify the base_url according to your region.
 base_url=&quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&quot;,
)
messages = [{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;Who are you&quot;}]
completion = client.chat.completions.create(
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 # The enable_thinking parameter enables the thinking process, and thinking_budget sets its token limit.
 extra_body={
 &quot;enable_thinking&quot;: True,
 &quot;thinking_budget&quot;: 50
 },
 stream=True,
 stream_options={
 &quot;include_usage&quot;: True
 },
)
reasoning_content = &quot;&quot; # Complete thinking process
answer_content = &quot;&quot; # Complete response
is_answering = False # Tracks if the response phase has started
print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Thinking process&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
for chunk in completion:
 if not chunk.choices:
 print(&quot;\nUsage:&quot;)
 print(chunk.usage)
 continue
 delta = chunk.choices[0].delta
 # Collect only the thinking content.
 if hasattr(delta, &quot;reasoning_content&quot;) and delta.reasoning_content is not None:
 if not is_answering:
 print(delta.reasoning_content, end=&quot;&quot;, flush=True)
 reasoning_content += delta.reasoning_content
 # When content is received, the response phase begins.
 if hasattr(delta, &quot;content&quot;) and delta.content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Complete response&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
 is_answering = True
 print(delta.content, end=&quot;&quot;, flush=True)
 answer_content += delta.content
 Response ====================Thinking process====================
Okay, the user is asking, &quot;Who are you?&quot; I need to provide a clear and friendly response. First, I should state my identity as Qwen, developed by Tongyi Lab at Alibaba Group. Next, I need to explain my main functions, such as answering
====================Complete response====================
I am Qwen, a large-scale language model developed by Tongyi Lab at Alibaba Group. I can answer questions, create text, perform logical reasoning, and write code.
 Node.js Sample code import OpenAI from &quot;openai&quot;;
import process from &#x27;process&#x27;;
// Initialize the OpenAI client.
const openai = new OpenAI({
 apiKey: process.env.DASHSCOPE_API_KEY, // Read from an environment variable.
 // Configurations vary by region. Modify the baseURL according to your region.
 baseURL: &#x27;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&#x27;
});
let reasoningContent = &#x27;&#x27;;
let answerContent = &#x27;&#x27;;
let isAnswering = false;
async function main() {
 try {
 const messages = [{ role: &#x27;user&#x27;, content: &#x27;Who are you&#x27; }];
 const stream = await openai.chat.completions.create({
 model: &#x27;qwen-plus&#x27;,
 messages,
 stream: true,
 // The enable_thinking parameter enables the thinking process, and thinking_budget sets its token limit.
 enable_thinking: true,
 thinking_budget: 50
 });
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Thinking process&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;\n&#x27;);
 for await (const chunk of stream) {
 if (!chunk.choices?.length) {
 console.log(&#x27;\nUsage:&#x27;);
 console.log(chunk.usage);
 continue;
 }
 const delta = chunk.choices[0].delta;
 // Collect only the thinking content.
 if (delta.reasoning_content !== undefined &amp;&amp; delta.reasoning_content !== null) {
 if (!isAnswering) {
 process.stdout.write(delta.reasoning_content);
 }
 reasoningContent += delta.reasoning_content;
 }
 // When content is received, the response phase begins.
 if (delta.content !== undefined &amp;&amp; delta.content) {
 if (!isAnswering) {
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Complete response&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;\n&#x27;);
 isAnswering = true;
 }
 process.stdout.write(delta.content);
 answerContent += delta.content;
 }
 }
 } catch (error) {
 console.error(&#x27;Error:&#x27;, error);
 }
}
main();
 Response ====================Thinking process====================
Okay, the user is asking, &quot;Who are you?&quot; I need to provide a clear and accurate response. First, I should state my identity as Qwen, developed by Tongyi Lab at Alibaba Group. Next, I should explain my main functions, such as answering questions
====================Complete response====================
I am Qwen, a large-scale language model developed by Tongyi Lab at Alibaba Group. I can answer questions, create text, perform logical reasoning, and write code.
 HTTP Sample code curl # ======= Important =======
# The following is the base URL for the Singapore region. For models in the China (Beijing) region, replace the URL with: https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
# For models in the US (Virginia) region, replace the URL with: https://{WorkspaceId}.us-east-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions
# === Remove this comment before execution ===
curl -X POST https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions \
-H &quot;Authorization: Bearer $DASHSCOPE_API_KEY&quot; \
-H &quot;Content-Type: application/json&quot; \
-d &#x27;{
 &quot;model&quot;: &quot;qwen3.8-max&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Who are you&quot;
 }
 ],
 &quot;stream&quot;: true,
 &quot;stream_options&quot;: {
 &quot;include_usage&quot;: true
 },
 &quot;enable_thinking&quot;: true,
 &quot;thinking_budget&quot;: 50
}&#x27;
 Response data: {&quot;choices&quot;:[{&quot;delta&quot;:{&quot;content&quot;:null,&quot;role&quot;:&quot;assistant&quot;,&quot;reasoning_content&quot;:&quot;&quot;},&quot;index&quot;:0,&quot;logprobs&quot;:null,&quot;finish_reason&quot;:null}],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:null,&quot;created&quot;:1745485391,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-e2edaf2c-8aaf-9e54-90e2-b21dd5045503&quot;}
.....
data: {&quot;choices&quot;:[{&quot;finish_reason&quot;:&quot;stop&quot;,&quot;delta&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:null},&quot;index&quot;:0,&quot;logprobs&quot;:null}],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:null,&quot;created&quot;:1745485391,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-e2edaf2c-8aaf-9e54-90e2-b21dd5045503&quot;}
data: {&quot;choices&quot;:[],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:{&quot;prompt_tokens&quot;:10,&quot;completion_tokens&quot;:360,&quot;total_tokens&quot;:370},&quot;created&quot;:1745485391,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-e2edaf2c-8aaf-9e54-90e2-b21dd5045503&quot;}
data: [DONE]
 DashScope 
 The DashScope API for the Qwen3.5 series uses a multimodal interface. The following example returns a url error . For the correct usage, see Enable or disable thinking mode . 
 Python Sample code import os
from dashscope import MultiModalConversation
import dashscope
# The following URL is for the Singapore region. When calling, replace WorkspaceId with your actual workspace ID. URLs vary by region.
dashscope.base_http_api_url = &quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1/&quot;
messages = [{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: [{&quot;text&quot;: &quot;Who are you?&quot;}]}]
completion = MultiModalConversation.call(
 # If the environment variable is not configured, replace the following line with your Model Studio API key: api_key = &quot;sk-xxx&quot;,
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 enable_thinking=True,
 # Sets the token limit for the thinking process.
 thinking_budget=50,
 stream=True,
 incremental_output=True,
)
# Stores the complete thinking process.
reasoning_content = &quot;&quot;
# Stores the complete response.
answer_content = &quot;&quot;
# Tracks if the response phase has started.
is_answering = False
print(&quot;=&quot; * 20 + &quot;Thinking process&quot; + &quot;=&quot; * 20)
for chunk in completion:
 # Ignore chunks where both thinking content and response content are empty.
 content = chunk.output.choices[0].message.content
 reasoning = chunk.output.choices[0].message.reasoning_content
 if not content and reasoning == &quot;&quot;:
 pass
 else:
 # If the current chunk contains thinking content.
 if reasoning != &quot;&quot; and not content:
 print(reasoning, end=&quot;&quot;, flush=True)
 reasoning_content += reasoning
 # If the current chunk contains response content.
 elif content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Complete response&quot; + &quot;=&quot; * 20)
 is_answering = True
 print(content[0][&quot;text&quot;], end=&quot;&quot;, flush=True)
 answer_content += content[0][&quot;text&quot;]
# To print the complete thinking process and response, uncomment and run the following code.
# print(&quot;=&quot; * 20 + &quot;Complete thinking process&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
# print(f&quot;{reasoning_content}&quot;)
# print(&quot;=&quot; * 20 + &quot;Complete response&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
# print(f&quot;{answer_content}&quot;)
 Response ====================Thinking process====================
Okay, the user is asking, &quot;Who are you?&quot; I need to provide a clear and friendly response. First, I must introduce myself as Qwen, developed by Tongyi Lab at Alibaba Group. Next, I should explain my main functions, such as
====================Complete response====================
I am Qwen, a large-scale language model developed by Tongyi Lab at Alibaba Group. I can answer questions, create text, perform logical reasoning, and write code.
 Java Sample code // The DashScope SDK version must be 2.19.4 or later.
import java.util.Arrays;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversation;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationParam;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationResult;
import com.alibaba.dashscope.common.MultiModalMessage;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import com.alibaba.dashscope.common.Role;
import com.alibaba.dashscope.exception.ApiException;
import com.alibaba.dashscope.exception.InputRequiredException;
import com.alibaba.dashscope.exception.NoApiKeyException;
import io.reactivex.Flowable;
import com.alibaba.dashscope.exception.UploadFileException;
import java.lang.System;
import com.alibaba.dashscope.utils.Constants;
public class Main {
 static {
 // The base HTTP API URL varies by region. Modify it according to your region.
 Constants.baseHttpApiUrl=&quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1&quot;;
 }
 private static final Logger logger = LoggerFactory.getLogger(Main.class);
 private static StringBuilder reasoningContent = new StringBuilder();
 private static StringBuilder finalContent = new StringBuilder();
 private static boolean isFirstPrint = true;
 private static void handleMultiModalConversationResult(MultiModalConversationResult message) {
 String reasoning = message.getOutput().getChoices().get(0).getMessage().getReasoningContent();
 List&lt;Map&lt;String, Object&gt;&gt; contentList = (List&lt;Map&lt;String, Object&gt;&gt;) message.getOutput().getChoices().get(0).getMessage().getContent();
 String content = (contentList != null &amp;&amp; !contentList.isEmpty()) ? (String) contentList.get(0).get(&quot;text&quot;) : &quot;&quot;;
 if (!reasoning.isEmpty()) {
 reasoningContent.append(reasoning);
 if (isFirstPrint) {
 System.out.println(&quot;====================Thinking process====================&quot;);
 isFirstPrint = false;
 }
 System.out.print(reasoning);
 }
 if (!content.isEmpty()) {
 finalContent.append(content);
 if (!isFirstPrint) {
 System.out.println(&quot;\n====================Complete response====================&quot;);
 isFirstPrint = true;
 }
 System.out.print(content);
 }
 }
 private static MultiModalConversationParam buildMultiModalConversationParam(MultiModalMessage userMsg) {
 return MultiModalConversationParam.builder()
 // If the environment variable is not configured, replace the following line with your Model Studio API key: .apiKey(&quot;sk-xxx&quot;)
 .apiKey(System.getenv(&quot;DASHSCOPE_API_KEY&quot;))
 .model(&quot;qwen3.8-max&quot;)
 .enableThinking(true)
 .thinkingBudget(50)
 .incrementalOutput(true)
 .messages(Arrays.asList(userMsg))
 .build();
 }
 public static void streamCallWithMessage(MultiModalConversation conv, MultiModalMessage userMsg)
 throws NoApiKeyException, ApiException, InputRequiredException, UploadFileException {
 MultiModalConversationParam param = buildMultiModalConversationParam(userMsg);
 Flowable&lt;MultiModalConversationResult&gt; result = conv.streamCall(param);
 result.blockingForEach(message -&gt; handleMultiModalConversationResult(message));
 }
 public static void main(String[] args) {
 try {
 MultiModalConversation conv = new MultiModalConversation();
 MultiModalMessage userMsg = MultiModalMessage.builder().role(Role.USER.getValue()).content(Arrays.asList(Collections.singletonMap(&quot;text&quot;, &quot;Who are you?&quot;))).build();
 streamCallWithMessage(conv, userMsg);
// Print the final result.
// if (reasoningContent.length() &gt; 0) {
// System.out.println(&quot;\n====================Complete response====================&quot;);
// System.out.println(finalContent.toString());
// }
 } catch (ApiException | NoApiKeyException | InputRequiredException | UploadFileException e) {
 logger.error(&quot;An exception occurred: {}&quot;, e.getMessage());
 }
 System.exit(0);
 }
}
 Response ====================Thinking process====================
Okay, the user is asking, &quot;Who are you?&quot; I need to provide a clear and friendly response. First, I must introduce myself as Qwen, developed by Tongyi Lab at Alibaba Group. Next, I should explain my main functions, such as
====================Complete response====================
I am Qwen, a large-scale language model developed by Tongyi Lab at Alibaba Group. I can answer questions, create text, perform logical reasoning, and write code.
 HTTP Sample code curl # ======= Important =======
# API keys are region-specific. To get an API key, visit https://www.alibabacloud.com/help/en/model-studio/get-api-key.
# The endpoint URL varies by region. Modify it according to your region.
# === Remove this comment before execution ===
curl -X POST &quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation&quot; \
-H &quot;Authorization: Bearer $DASHSCOPE_API_KEY&quot; \
-H &quot;Content-Type: application/json&quot; \
-H &quot;X-DashScope-SSE: enable&quot; \
-d &#x27;{
 &quot;model&quot;: &quot;qwen3.8-max&quot;,
 &quot;input&quot;:{
 &quot;messages&quot;:[
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: [{&quot;text&quot;: &quot;Who are you?&quot;}]
 }
 ]
 },
 &quot;parameters&quot;:{
 &quot;enable_thinking&quot;: true,
 &quot;thinking_budget&quot;: 50,
 &quot;incremental_output&quot;: true,
 &quot;result_format&quot;: &quot;message&quot;
 }
}&#x27;
 Response id:1
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;Okay&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:14,&quot;output_tokens&quot;:3,&quot;input_tokens&quot;:11,&quot;output_tokens_details&quot;:{&quot;reasoning_tokens&quot;:1}},&quot;request_id&quot;:&quot;2ce91085-3602-9c32-9c8b-fe3d583a2c38&quot;}
id:2
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;,&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:15,&quot;output_tokens&quot;:4,&quot;input_tokens&quot;:11,&quot;output_tokens_details&quot;:{&quot;reasoning_tokens&quot;:2}},&quot;request_id&quot;:&quot;2ce91085-3602-9c32-9c8b-fe3d583a2c38&quot;}
......
id:133
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;!&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:149,&quot;output_tokens&quot;:138,&quot;input_tokens&quot;:11,&quot;output_tokens_details&quot;:{&quot;reasoning_tokens&quot;:50}},&quot;request_id&quot;:&quot;2ce91085-3602-9c32-9c8b-fe3d583a2c38&quot;}
id:134
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;stop&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:149,&quot;output_tokens&quot;:138,&quot;input_tokens&quot;:11,&quot;output_tokens_details&quot;:{&quot;reasoning_tokens&quot;:50}},&quot;request_id&quot;:&quot;2ce91085-3602-9c32-9c8b-fe3d583a2c38&quot;}
 Pass the thinking process 
 By default, the model ignores reasoning_content in the messages history. Set preserve_thinking to true to pass prior reasoning to subsequent turns. The reasoning_content from earlier assistant messages is then appended to the model&#x27;s input. 
 Important The preserve_thinking parameter is only supported for qwen3.8-max series, qwen3.8-flash, qwen3.7-max, qwen3.7-max-us, qwen3.7-max-2026-05-20, qwen3.7-max-2026-06-08, qwen3.7-max-preview, qwen3.7-max-2026-05-17, qwen3.7-plus, qwen3.7-plus-us, qwen3.7-plus-2026-05-26, qwen3.6-max-preview, qwen3.6-plus, qwen3.6-plus-2026-04-02, qwen3.7-flash, qwen3.7-flash-2026-07-15, kimi-k2.7-code (deployed on Alibaba Cloud Model Studio), kimi-k2.6 (deployed on Alibaba Cloud Model Studio), kimi/kimi-k3 (deployed on Moonshot AI), kimi/kimi-k2.7-code-highspeed (deployed on Moonshot AI), kimi/kimi-k2.7-code (deployed on Moonshot AI), and kimi/kimi-k2.6 (deployed on Moonshot AI). 
 Enabling this parameter when history messages lack reasoning_content does not cause an error. 
 When enabled, reasoning_content from conversation history counts toward input tokens and billing. 
 OpenAI compatible Note preserve_thinking is not a standard OpenAI parameter. When you use the Python SDK, pass this parameter in extra_body . Python Sample code from openai import OpenAI
import os
client = OpenAI(
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 # Configurations vary by region. Modify this based on your actual region.
 base_url=&quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&quot;,
)
# First turn of the conversation
messages = [
 {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;I need to choose a message queue for an E-commerce system that handles tens of millions of messages per day. Please provide a recommendation.&quot;}
]
first_reasoning = &quot;&quot;
first_content = &quot;&quot;
is_answering = False
completion = client.chat.completions.create(
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 extra_body={&quot;enable_thinking&quot;: True},
 stream=True,
 stream_options={&quot;include_usage&quot;: True},
)
print(&quot;=&quot; * 20 + &quot;First-turn thought process&quot; + &quot;=&quot; * 20)
for chunk in completion:
 if not chunk.choices:
 continue
 delta = chunk.choices[0].delta
 if hasattr(delta, &quot;reasoning_content&quot;) and delta.reasoning_content is not None:
 first_reasoning += delta.reasoning_content
 if not is_answering:
 print(delta.reasoning_content, end=&quot;&quot;, flush=True)
 if hasattr(delta, &quot;content&quot;) and delta.content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;First-turn response&quot; + &quot;=&quot; * 20)
 is_answering = True
 print(delta.content, end=&quot;&quot;, flush=True)
 first_content += delta.content
# Second turn: Pass the thought process and ask why the model excluded Kafka
messages = [
 {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;I need to choose a message queue for an E-commerce system that handles tens of millions of messages per day. Please provide a recommendation.&quot;},
 {
 &quot;role&quot;: &quot;assistant&quot;,
 &quot;content&quot;: first_content,
 &quot;reasoning_content&quot;: first_reasoning,
 },
 {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;Why did you exclude Kafka in your comparison?&quot;},
]
reasoning_content = &quot;&quot;
answer_content = &quot;&quot;
is_answering = False
# Pass preserve_thinking through extra_body
completion = client.chat.completions.create(
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 extra_body={
 &quot;enable_thinking&quot;: True,
 &quot;preserve_thinking&quot;: True,
 },
 stream=True,
 stream_options={&quot;include_usage&quot;: True},
)
print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Second-turn thought process&quot; + &quot;=&quot; * 20)
for chunk in completion:
 if not chunk.choices:
 continue
 delta = chunk.choices[0].delta
 if hasattr(delta, &quot;reasoning_content&quot;) and delta.reasoning_content is not None:
 if not is_answering:
 print(delta.reasoning_content, end=&quot;&quot;, flush=True)
 reasoning_content += delta.reasoning_content
 if hasattr(delta, &quot;content&quot;) and delta.content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Second-turn response&quot; + &quot;=&quot; * 20)
 is_answering = True
 print(delta.content, end=&quot;&quot;, flush=True)
 answer_content += delta.content
 Response ====================First-turn thought process====================
The user needs a message queue for an E-commerce system with tens of millions of daily messages. I will compare mainstream solutions based on dimensions such as throughput, reliability, delayed messages, and transaction support...
RocketMQ: Validated in Alibaba&#x27;s E-commerce scenarios, natively supports transactional and delayed messages, and provides strict partition-level ordering...
Kafka: Extremely high throughput, but lacks native support for transactional and delayed messages, requiring custom compensation mechanisms...
RabbitMQ: Low latency, but limited cluster scalability, with a peak TPS in the tens of thousands...
====================First-turn response====================
Considering the core needs of an E-commerce scenario (transactional messages, delayed messages, ordering, and peak handling), I recommend Apache RocketMQ. If your team already has a Kafka ecosystem or requires strong real-time analytics, Kafka is also a viable option.
====================Second-turn thought process====================
The user is asking why Kafka was excluded. Reviewing my historical thought process, I did not exclude Kafka; I gave it a 4-star rating. I will refer to my previous detailed comparison to explain...
In the last turn, I compared the differences between RocketMQ and Kafka regarding transactional messages, delayed messages, and ordering. Kafka&#x27;s main disadvantage is that it requires additional architectural design to compensate for E-commerce-specific semantics...
====================Second-turn response====================
I did not exclude Kafka. Kafka excels in throughput and ecosystem. The reason RocketMQ received a slightly higher rating is its better out-of-the-box match for core E-commerce workflows. RocketMQ natively supports transactional and delayed messages, while Kafka requires self-implementation through architectural patterns like the Outbox Pattern. If your team already has a Kafka ecosystem, it is fully capable of handling a scenario with tens of millions of messages.
 Node.js Sample code import OpenAI from &quot;openai&quot;;
import process from &#x27;process&#x27;;
const openai = new OpenAI({
 apiKey: process.env.DASHSCOPE_API_KEY,
 // Configurations vary by region. Modify this based on your actual region.
 baseURL: &#x27;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&#x27;
});
async function main() {
 // First turn of the conversation
 let firstReasoning = &#x27;&#x27;;
 let firstContent = &#x27;&#x27;;
 let isAnswering = false;
 const stream1 = await openai.chat.completions.create({
 model: &#x27;qwen3.7-plus&#x27;,
 messages: [{ role: &#x27;user&#x27;, content: &#x27;I need to choose a message queue for an E-commerce system that handles tens of millions of messages per day. Please provide a recommendation.&#x27; }],
 stream: true,
 enable_thinking: true
 });
 console.log(&#x27;=&#x27;.repeat(20) + &#x27;First-turn thought process&#x27; + &#x27;=&#x27;.repeat(20));
 for await (const chunk of stream1) {
 if (!chunk.choices?.length) continue;
 const delta = chunk.choices[0].delta;
 if (delta.reasoning_content !== undefined &amp;&amp; delta.reasoning_content !== null) {
 firstReasoning += delta.reasoning_content;
 if (!isAnswering) process.stdout.write(delta.reasoning_content);
 }
 if (delta.content !== undefined &amp;&amp; delta.content) {
 if (!isAnswering) {
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;First-turn response&#x27; + &#x27;=&#x27;.repeat(20));
 isAnswering = true;
 }
 process.stdout.write(delta.content);
 firstContent += delta.content;
 }
 }
 // Second turn: Pass the thought process
 let reasoningContent = &#x27;&#x27;;
 let answerContent = &#x27;&#x27;;
 isAnswering = false;
 const stream2 = await openai.chat.completions.create({
 model: &#x27;qwen3.7-plus&#x27;,
 messages: [
 { role: &#x27;user&#x27;, content: &#x27;I need to choose a message queue for an E-commerce system that handles tens of millions of messages per day. Please provide a recommendation.&#x27; },
 {
 role: &#x27;assistant&#x27;,
 content: firstContent,
 reasoning_content: firstReasoning
 },
 { role: &#x27;user&#x27;, content: &#x27;Why did you exclude Kafka in your comparison?&#x27; }
 ],
 stream: true,
 enable_thinking: true,
 // Pass preserve_thinking as a top-level parameter
 preserve_thinking: true
 });
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Second-turn thought process&#x27; + &#x27;=&#x27;.repeat(20));
 for await (const chunk of stream2) {
 if (!chunk.choices?.length) continue;
 const delta = chunk.choices[0].delta;
 if (delta.reasoning_content !== undefined &amp;&amp; delta.reasoning_content !== null) {
 if (!isAnswering) process.stdout.write(delta.reasoning_content);
 reasoningContent += delta.reasoning_content;
 }
 if (delta.content !== undefined &amp;&amp; delta.content) {
 if (!isAnswering) {
 console.log(&#x27;\n&#x27; + &#x27;=&#x27;.repeat(20) + &#x27;Second-turn response&#x27; + &#x27;=&#x27;.repeat(20));
 isAnswering = true;
 }
 process.stdout.write(delta.content);
 answerContent += delta.content;
 }
 }
}
main();
 Response ====================First-turn thought process====================
The user needs a message queue for an E-commerce system with tens of millions of daily messages. I will compare mainstream solutions based on dimensions such as throughput, reliability, delayed messages, and transaction support...
====================First-turn response====================
Considering the core needs of an E-commerce scenario, I recommend Apache RocketMQ. If your team already has a Kafka ecosystem, Kafka is also a viable option.
====================Second-turn thought process====================
The user is asking why Kafka was excluded. Referring to my previous thought process, I did not exclude Kafka...
====================Second-turn response====================
I did not exclude Kafka. Kafka excels in throughput and ecosystem. The reason RocketMQ received a slightly higher rating is its better out-of-the-box match for core E-commerce workflows.
 HTTP Sample code curl # The base_url varies by region. Modify it based on your actual region.
curl -X POST https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions \
-H &quot;Authorization: Bearer $DASHSCOPE_API_KEY&quot; \
-H &quot;Content-Type: application/json&quot; \
-d &#x27;{
 &quot;model&quot;: &quot;qwen3.8-max&quot;,
 &quot;messages&quot;: [
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;I need to choose a message queue for an E-commerce system that handles tens of millions of messages per day. Please provide a recommendation.&quot;
 },
 {
 &quot;role&quot;: &quot;assistant&quot;,
 &quot;content&quot;: &quot;Considering the core needs of an E-commerce scenario, I recommend Apache RocketMQ.&quot;,
 &quot;reasoning_content&quot;: &quot;The user needs a message queue for an E-commerce system with tens of millions of daily messages. RocketMQ natively supports transactional and delayed messages, making it more suitable for E-commerce scenarios. Kafka has extremely high throughput but requires custom compensation mechanisms.&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: &quot;Why did you exclude Kafka in your comparison?&quot;
 }
 ],
 &quot;stream&quot;: true,
 &quot;stream_options&quot;: {
 &quot;include_usage&quot;: true
 },
 &quot;enable_thinking&quot;: true,
 &quot;preserve_thinking&quot;: true
}&#x27;
 Response data: {&quot;choices&quot;:[{&quot;delta&quot;:{&quot;content&quot;:null,&quot;role&quot;:&quot;assistant&quot;,&quot;reasoning_content&quot;:&quot;&quot;},&quot;index&quot;:0,&quot;logprobs&quot;:null,&quot;finish_reason&quot;:null}],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:null,&quot;created&quot;:1743523200,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-example-001&quot;}
.....
data: {&quot;choices&quot;:[{&quot;finish_reason&quot;:&quot;stop&quot;,&quot;delta&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:null},&quot;index&quot;:0,&quot;logprobs&quot;:null}],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:null,&quot;created&quot;:1743523200,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-example-001&quot;}
data: {&quot;choices&quot;:[],&quot;object&quot;:&quot;chat.completion.chunk&quot;,&quot;usage&quot;:{&quot;prompt_tokens&quot;:3463,&quot;completion_tokens&quot;:2387,&quot;total_tokens&quot;:5850},&quot;created&quot;:1743523200,&quot;system_fingerprint&quot;:null,&quot;model&quot;:&quot;qwen3.8-max&quot;,&quot;id&quot;:&quot;chatcmpl-example-001&quot;}
data: [DONE]
 DashScope Note The Java SDK does not currently support the preserve_thinking parameter. When you make HTTP calls, place the preserve_thinking parameter in the parameters object. Python Sample code import os
from dashscope import MultiModalConversation
import dashscope
# The following URL is for the Singapore region. When calling, replace WorkspaceId with your actual workspace ID. URLs vary by region.
dashscope.base_http_api_url = &quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1/&quot;
# First turn of the conversation
messages = [
 {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: [{&quot;text&quot;: &quot;I need to choose a message queue for an E-commerce system that handles tens of millions of messages per day. Please provide a recommendation.&quot;}]}
]
first_reasoning = &quot;&quot;
first_content = &quot;&quot;
is_answering = False
completion = MultiModalConversation.call(
 # If the environment variable is not set, replace the next line with your Model Studio API key: api_key=&quot;sk-xxx&quot;
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 enable_thinking=True,
 stream=True,
 incremental_output=True,
)
print(&quot;=&quot; * 20 + &quot;First-turn thought process&quot; + &quot;=&quot; * 20)
for chunk in completion:
 content = chunk.output.choices[0].message.content
 reasoning = chunk.output.choices[0].message.reasoning_content
 if not content and reasoning == &quot;&quot;:
 pass
 else:
 if reasoning != &quot;&quot; and not content:
 print(reasoning, end=&quot;&quot;, flush=True)
 first_reasoning += reasoning
 elif content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;First-turn response&quot; + &quot;=&quot; * 20)
 is_answering = True
 print(content[0][&quot;text&quot;], end=&quot;&quot;, flush=True)
 first_content += content[0][&quot;text&quot;]
# Second turn: Pass the thought process
messages = [
 {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: [{&quot;text&quot;: &quot;I need to choose a message queue for an E-commerce system that handles tens of millions of messages per day. Please provide a recommendation.&quot;}]},
 {
 &quot;role&quot;: &quot;assistant&quot;,
 &quot;content&quot;: [{&quot;text&quot;: first_content}],
 &quot;reasoning_content&quot;: first_reasoning,
 },
 {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: [{&quot;text&quot;: &quot;Why did you exclude Kafka in your comparison?&quot;}]},
]
reasoning_content = &quot;&quot;
answer_content = &quot;&quot;
is_answering = False
completion = MultiModalConversation.call(
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 model=&quot;qwen3.8-max&quot;,
 messages=messages,
 enable_thinking=True,
 # Pass the thought process
 preserve_thinking=True,
 stream=True,
 incremental_output=True,
)
print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Second-turn thought process&quot; + &quot;=&quot; * 20)
for chunk in completion:
 content = chunk.output.choices[0].message.content
 reasoning = chunk.output.choices[0].message.reasoning_content
 if not content and reasoning == &quot;&quot;:
 pass
 else:
 if reasoning != &quot;&quot; and not content:
 print(reasoning, end=&quot;&quot;, flush=True)
 reasoning_content += reasoning
 elif content:
 if not is_answering:
 print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Second-turn response&quot; + &quot;=&quot; * 20)
 is_answering = True
 print(content[0][&quot;text&quot;], end=&quot;&quot;, flush=True)
 answer_content += content[0][&quot;text&quot;]
 ): print(chunk.output.choices[0].message.reasoning_content, end=&quot;&quot;, flush=True) reasoning_content += chunk.output.choices[0].message.reasoning_content elif chunk.output.choices[0].message.content != &quot;&quot;: if not is_answering: print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Second-turn response&quot; + &quot;=&quot; * 20) is_answering = True print(chunk.output.choices[0].message.content, end=&quot;&quot;, flush=True) answer_content += chunk.output.choices[0].message.content Response ====================First-turn thought process====================
The user needs a message queue for an E-commerce system with tens of millions of daily messages. I will compare mainstream solutions based on dimensions such as throughput, reliability, delayed messages, and transaction support...
====================First-turn response====================
Considering the core needs of an E-commerce scenario, I recommend Apache RocketMQ. If your team already has a Kafka ecosystem, Kafka is also a viable option.
====================Second-turn thought process====================
The user is asking why Kafka was excluded. Referring to my previous thought process, I did not exclude Kafka...
====================Second-turn response====================
I did not exclude Kafka. Kafka excels in throughput and ecosystem. The reason RocketMQ received a slightly higher rating is its better out-of-the-box match for core E-commerce workflows.
 HTTP Sample code curl # The base_url varies by region. Modify it based on your actual region.
curl -X POST &quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation&quot; \
-H &quot;Authorization: Bearer $DASHSCOPE_API_KEY&quot; \
-H &quot;Content-Type: application/json&quot; \
-H &quot;X-DashScope-SSE: enable&quot; \
-d &#x27;{
 &quot;model&quot;: &quot;qwen3.8-max&quot;,
 &quot;input&quot;:{
 &quot;messages&quot;:[
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: [{&quot;text&quot;: &quot;I need to choose a message queue for an E-commerce system that handles tens of millions of messages per day. Please provide a recommendation.&quot;}]
 },
 {
 &quot;role&quot;: &quot;assistant&quot;,
 &quot;content&quot;: [{&quot;text&quot;: &quot;Considering the core needs of an E-commerce scenario, I recommend Apache RocketMQ.&quot;}],
 &quot;reasoning_content&quot;: &quot;The user needs a message queue for an E-commerce system with tens of millions of daily messages. RocketMQ natively supports transactional and delayed messages, making it more suitable for E-commerce scenarios. Kafka has extremely high throughput but requires custom compensation mechanisms.&quot;
 },
 {
 &quot;role&quot;: &quot;user&quot;,
 &quot;content&quot;: [{&quot;text&quot;: &quot;Why did you exclude Kafka in your comparison?&quot;}]
 }
 ]
 },
 &quot;parameters&quot;:{
 &quot;enable_thinking&quot;: true,
 &quot;preserve_thinking&quot;: true,
 &quot;incremental_output&quot;: true,
 &quot;result_format&quot;: &quot;message&quot;
 }
}&#x27;
 Response id:1
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;user&quot;},&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:3466,&quot;output_tokens&quot;:3,&quot;input_tokens&quot;:3463,&quot;output_tokens_details&quot;:{&quot;reasoning_tokens&quot;:1}},&quot;request_id&quot;:&quot;example-request-001&quot;}
id:2
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;follow-up&quot;},&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;null&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:3467,&quot;output_tokens&quot;:4,&quot;input_tokens&quot;:3463,&quot;output_tokens_details&quot;:{&quot;reasoning_tokens&quot;:2}},&quot;request_id&quot;:&quot;example-request-001&quot;}
......
id:200
event:result
:HTTP_STATUS/200
data:{&quot;output&quot;:{&quot;choices&quot;:[{&quot;message&quot;:{&quot;content&quot;:&quot;&quot;,&quot;reasoning_content&quot;:&quot;&quot;,&quot;role&quot;:&quot;assistant&quot;},&quot;finish_reason&quot;:&quot;stop&quot;}]},&quot;usage&quot;:{&quot;total_tokens&quot;:5850,&quot;output_tokens&quot;:2387,&quot;input_tokens&quot;:3463,&quot;output_tokens_details&quot;:{&quot;reasoning_tokens&quot;:1347}},&quot;request_id&quot;:&quot;example-request-001&quot;}
 Other features 
 Multi-turn conversations 
 Tool calling 
 Web search 
 Billing 
 Thinking content is billed per output token. 
 Some hybrid thinking models price thinking and non-thinking modes differently. 
 If a thinking-mode model produces no reasoning output, non-thinking pricing applies. 
 FAQ 
 Q: How do I disable thinking mode? This depends on the model type: 
 For hybrid thinking models, such as qwen-plus and deepseek-v3.2-exp, set enable_thinking to false . 
 For thinking-only models, such as qwen3-235b-a22b-thinking-2507 and deepseek-r1, the thinking mode cannot be disabled. 
 Q: Why is qwen3.7-plus slow to respond, and how do I troubleshoot it? qwen3.7-plus is a hybrid thinking model with thinking mode enabled by default. The thinking process generates a large number of reasoning tokens — more than 60% of the total output tokens in measurements — so the total latency of a single call is much higher than in non-thinking mode. The token generation speed itself is normal, at about 52 to 54 tokens/s. The longer total latency comes from the number of tokens that the thinking process produces, not from a slower model or a network fault. To troubleshoot the latency, follow these steps: 
 Check whether thinking mode is enabled. It is enabled by default for qwen3.7-plus. If the response returns the reasoning_content field, thinking mode is active. 
 Review completion_tokens and reasoning_tokens in the usage statistics of the response. A high proportion of reasoning_tokens means that the long total latency is expected behavior of thinking mode. 
 If you do not need the reasoning process, set enable_thinking to false in the request to disable thinking mode. This greatly reduces output tokens and lowers total latency by 60% to 75% in measurements. 
 If you want to keep the reasoning capability, use streaming output. You receive the first token sooner and can watch the reasoning in real time instead of waiting for the full response. 
 Usage statistics show the total latency of a single call, including the time spent generating reasoning tokens. This is not the generation latency of an individual token. 
 Q: How do I call a thinking model in non-streaming (synchronous) mode? The examples in this topic use streaming by default (recommended, so you can watch the reasoning in real time and avoid a long wait). Commercial thinking models (such as qwen-plus, qwen3-max, and qwen-flash) also support non-streaming (synchronous) output, returning the full reasoning and answer in a single response. 
 When you switch an example from streaming to non-streaming, also update the response-parsing code : a non-streaming call returns a complete response object ( completion ). Do not iterate it with for chunk in completion as in the streaming example (this raises &#x27;tuple&#x27; object has no attribute &#x27;choices&#x27; ). Instead, read completion.choices[0].message.reasoning_content (reasoning) and completion.choices[0].message.content (answer) directly. Also, when stream=False , do not set the stream_options parameter. 
 The following example calls qwen3.8-max in thinking mode without streaming, using the OpenAI-compatible interface: from openai import OpenAI
import os
client = OpenAI(
 # API keys differ by region. Get an API key: https://www.alibabacloud.com/help/en/model-studio/get-api-key
 # If the environment variable is not configured, replace the line below with your Model Studio API key: api_key=&quot;sk-xxx&quot;
 api_key=os.getenv(&quot;DASHSCOPE_API_KEY&quot;),
 # The following is the configuration for the Singapore region. Replace WorkspaceId with your real workspace ID; configurations differ by region.
 base_url=&quot;https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1&quot;,
)
completion = client.chat.completions.create(
 model=&quot;qwen3.8-max&quot;, # Replace with a thinking model that supports non-streaming output
 messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: &quot;Who are you?&quot;}],
 extra_body={&quot;enable_thinking&quot;: True},
 stream=False, # Non-streaming (synchronous) output; do not set stream_options when stream=False
)
# A non-streaming call returns a complete response object. Read message directly; do not iterate.
message = completion.choices[0].message
print(&quot;=&quot; * 20 + &quot;Reasoning&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
print(getattr(message, &quot;reasoning_content&quot;, &quot;&quot;) or &quot;&quot;)
print(&quot;\n&quot; + &quot;=&quot; * 20 + &quot;Answer&quot; + &quot;=&quot; * 20 + &quot;\n&quot;)
print(message.content)
 Some models (such as the open-source qwen3-235b-a22b and qwen3-32b) support streaming only. A non-streaming call returns the error parameter.enable_thinking only support stream call ; use streaming for these models. 
 Q: How do I purchase tokens after my free quota is used up? Top up your account in the Expenses and Costs center. Your account must have no overdue payments to call models. 
 After the free quota runs out, calls are billed per minute. View spending in Bill Details . 
 Q: Can I upload images or documents as input? These models accept text only. Qwen3-VL and QVQ support deep thinking on images . 
 Q: How do I view token consumption and the number of calls? One hour after you call a model, go to the Monitoring ( Singapore or Beijing ) page. Set the query conditions, such as the time range and workspace. Then, in the Models area, find the target model and click Monitor in the Actions column to view the model&#x27;s call statistics. For more information, see the Monitoring document. 
 Data is updated hourly. During peak periods, there may be an hour-level latency. 
 Q: What do I do if a long prompt fails to generate a response or times out? If a call with a long prompt fails or times out, thinking mode ( enable_thinking=true ) is usually enabled. Thinking mode increases processing time, which can truncate the response or cause the request to time out when the prompt is long. Solutions: 
 Disable thinking mode: set enable_thinking to false . Processing time can drop from about 50 seconds to about 30 seconds. 
 Enable streaming output: set stream to true to avoid the timeout limit of non-streaming mode. 
 Increase the timeout: to keep thinking mode enabled, set the client timeout to 180 seconds or longer. 
 API reference 
 For input and response parameters, see Text Generation . 
 Error codes 
 If a call fails, see Error codes . 
Thank you! We've received your feedback.
 