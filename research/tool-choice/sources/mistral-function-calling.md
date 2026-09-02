 Function Calling | Mistral Docs Docs &amp; API Search docs ⌘K Vibe Studio Inference &amp; Models Admin Resources API Reference Search docs ⌘K Toggle theme Reach out Try Studio Home Studio Overview Build Conversations Chat Completions Vision Reasoning Citations &amp; References Advanced Function Calling Structured Outputs Moderation &amp; Guardrailing Agents Connectors Workflows Search Agentic Search Libraries Search Toolkit Process Document AI Audio Batch Processing Safety &amp; utilities Embeddings Moderation &amp; Guardrailing Studio Conversations Function Calling Function Calling 
 Function calling, under the Tool Calling umbrella, allows Mistral models to connect to external local tools. By integrating Mistral models with external tools such as user defined functions or APIs, users can build applications catering to specific use cases and practical problems. In this guide, for instance, we wrote two functions for tracking payment status and payment date. We can use these two tools to provide answers for payment-related queries. 
 Tip Before continuing, we recommend reading the Chat Completions documentation to learn more about the chat completions API and how to use it before proceeding. 
 Before You Start Copy section link Before You Start 
 Available Models 
 Currently, among the function calling capable models, we have the following non-exhaustive list: 
 General Models Specialized Models Reasoning Models Mistral Large 3 - mistral-large-latest Devstral 2.0 - devstral-latest Magistral Medium 1.2 - magistral-medium-latest Mistral Medium 3.5 - mistral-medium-latest Devstral Small 2 - devstral-small-latest Magistral Small 1.2 - magistral-small-latest Mistral Small 3.2 - mistral-small-latest Voxtral Small - voxtral-small-latest Mistral Small Creative - labs-mistral-small-creative Codestral - codestral-latest Ministral 3 14B - ministral-14b-latest Ministral 3 8B - ministral-8b-latest Ministral 3 3B - ministral-3b-latest 
 For more exhaustive information about all our models, visit the Models Page . 
 Five Steps Copy section link Five Steps 
 Open in Colab ↗ 
 At a glance, there are five main steps with function calling: 
 1. Developer: Specify Functions/Tools, and a System Prompt (optional) 
 2. User: Query the Model powered with the new Functions/Tools 
 3. Model: Generates function arguments if applicable when necessary 
 4. Developer: Executes the corresponding function to obtain tool results 
 5. Model: Generates an answer based on the tool results 
 In general, a chat with function calling will always look like the following: 
 Sequence Type Role Flow No Function Call system * → user → assistant → user → ... Function Calling system * → user → assistant function call 1 → tool result 1 → assistant → user → ... Successive Function Calling system * → user → assistant fc.1 → tool r.1 → assistant fc.2 → tool r.2→ assistant → user → ... Parallel Function Calling system * → user → assistant fc.1, fc.2 → tool r.1 → tool r.2 → assistant → user → ... *optional 
 In this guide, we will walk through a simple function calling example to demonstrate how function calling works with Mistral models in these five steps. 
 Before we get started, let&#x27;s assume we have a dataframe consisting of payment transactions. When users ask questions about this dataframe, they can use certain tools to answer questions about this data. This is just an example to emulate an external database that the LLM cannot directly access. 
 python typescript import pandas as pd
 # Assuming we have the following data 
 data = { 
 &#x27;transaction_id&#x27; : [ &#x27;T1001&#x27; , &#x27;T1002&#x27; , &#x27;T1003&#x27; , &#x27;T1004&#x27; , &#x27;T1005&#x27; ] , 
 &#x27;customer_id&#x27; : [ &#x27;C001&#x27; , &#x27;C002&#x27; , &#x27;C003&#x27; , &#x27;C002&#x27; , &#x27;C001&#x27; ] , 
 &#x27;payment_amount&#x27; : [ 125.50 , 89.99 , 120.00 , 54.30 , 210.20 ] , 
 &#x27;payment_date&#x27; : [ &#x27;2021-10-05&#x27; , &#x27;2021-10-06&#x27; , &#x27;2021-10-07&#x27; , &#x27;2021-10-05&#x27; , &#x27;2021-10-08&#x27; ] , 
 &#x27;payment_status&#x27; : [ &#x27;Paid&#x27; , &#x27;Unpaid&#x27; , &#x27;Paid&#x27; , &#x27;Paid&#x27; , &#x27;Pending&#x27; ] 
 } 
 # Create DataFrame 
 df = pd . DataFrame ( data ) import pandas as pd
 # Assuming we have the following data 
 data = { 
 &#x27;transaction_id&#x27; : [ &#x27;T1001&#x27; , &#x27;T1002&#x27; , &#x27;T1003&#x27; , &#x27;T1004&#x27; , &#x27;T1005&#x27; ] , 
 &#x27;customer_id&#x27; : [ &#x27;C001&#x27; , &#x27;C002&#x27; , &#x27;C003&#x27; , &#x27;C002&#x27; , &#x27;C001&#x27; ] , 
 &#x27;payment_amount&#x27; : [ 125.50 , 89.99 , 120.00 , 54.30 , 210.20 ] , 
 &#x27;payment_date&#x27; : [ &#x27;2021-10-05&#x27; , &#x27;2021-10-06&#x27; , &#x27;2021-10-07&#x27; , &#x27;2021-10-05&#x27; , &#x27;2021-10-08&#x27; ] , 
 &#x27;payment_status&#x27; : [ &#x27;Paid&#x27; , &#x27;Unpaid&#x27; , &#x27;Paid&#x27; , &#x27;Paid&#x27; , &#x27;Pending&#x27; ] 
 } 
 # Create DataFrame 
 df = pd . DataFrame ( data ) 
 Step 1. Developer Copy section link Step 1. Developer 
 Functions and System Definitions 
 Developers can define all the necessary tools for their use cases. Often, we might have multiple tools at our disposal. For this example, let&#x27;s consider we have two functions as our two tools: 
 retrieve_payment_status : To retrieve payment status given a transaction ID. 
 retrieve_payment_date : To retrieve payment date given a transaction ID. 
 python typescript def retrieve_payment_status ( transaction_id : str ) - &gt; str : 
 &quot;Get payment status of a transaction&quot; 
 if transaction_id in df . transaction_id . values : 
 return json . dumps ( { &#x27;status&#x27; : df [ df . transaction_id == transaction_id ] . payment_status . item ( ) } ) 
 return json . dumps ( { &#x27;error&#x27; : &#x27;transaction id not found.&#x27; } ) 
 def retrieve_payment_date ( transaction_id : str ) - &gt; str : 
 &quot;Get payment date of a transaction&quot; 
 if transaction_id in df . transaction_id . values : 
 return json . dumps ( { &#x27;date&#x27; : df [ df . transaction_id == transaction_id ] . payment_date . item ( ) } ) 
 return json . dumps ( { &#x27;error&#x27; : &#x27;transaction id not found.&#x27; } ) def retrieve_payment_status ( transaction_id : str ) - &gt; str : 
 &quot;Get payment status of a transaction&quot; 
 if transaction_id in df . transaction_id . values : 
 return json . dumps ( { &#x27;status&#x27; : df [ df . transaction_id == transaction_id ] . payment_status . item ( ) } ) 
 return json . dumps ( { &#x27;error&#x27; : &#x27;transaction id not found.&#x27; } ) 
 def retrieve_payment_date ( transaction_id : str ) - &gt; str : 
 &quot;Get payment date of a transaction&quot; 
 if transaction_id in df . transaction_id . values : 
 return json . dumps ( { &#x27;date&#x27; : df [ df . transaction_id == transaction_id ] . payment_date . item ( ) } ) 
 return json . dumps ( { &#x27;error&#x27; : &#x27;transaction id not found.&#x27; } ) 
 For ease of use, we will organize the two functions into a dictionary where keys represent the functions names, and values are the functions themselves.
 This allows us to dynamically call each function based on its function name. 
 python typescript names_to_functions = { 
 &#x27;retrieve_payment_status&#x27; : retrieve_payment_status , 
 &#x27;retrieve_payment_date&#x27; : retrieve_payment_date , 
 } names_to_functions = { 
 &#x27;retrieve_payment_status&#x27; : retrieve_payment_status , 
 &#x27;retrieve_payment_date&#x27; : retrieve_payment_date , 
 } 
 When setting up a model capable of function calling and agentic workflows, it is recommended to provide context and custom instructions under the system role umbrella. You can do this by adding a system message to the chat history.
For this example, we will define a very simple system prompt to guide the model on how to use the provided tools. 
 python typescript messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a helpful assistant. You can use the following tools to help answer the user&#x27;s questions related to payment transactions.&quot; 
 } 
 ] messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a helpful assistant. You can use the following tools to help answer the user&#x27;s questions related to payment transactions.&quot; 
 } 
 ] 
 In order for models to understand these functions, we need to outline the function specifications with a JSON schema . Specifically, we need to describe the type, function name, function description, function parameters, and the required parameter for the function. Since we have two functions here, let&#x27;s list two function specifications in a list. 
 python typescript Raw JSON tools = [ 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_status&quot; , 
 &quot;description&quot; : &quot;Get payment status of a transaction&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;transaction_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The transaction id.&quot; , 
 } 
 } , 
 &quot;required&quot; : [ &quot;transaction_id&quot; ] , 
 } , 
 } , 
 } , 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_date&quot; , 
 &quot;description&quot; : &quot;Get payment date of a transaction&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;transaction_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The transaction id.&quot; , 
 } 
 } , 
 &quot;required&quot; : [ &quot;transaction_id&quot; ] , 
 } , 
 } , 
 } 
 ] 
 # Note: You can specify multiple parameters for each function in the `properties` object. tools = [ 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_status&quot; , 
 &quot;description&quot; : &quot;Get payment status of a transaction&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;transaction_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The transaction id.&quot; , 
 } 
 } , 
 &quot;required&quot; : [ &quot;transaction_id&quot; ] , 
 } , 
 } , 
 } , 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_date&quot; , 
 &quot;description&quot; : &quot;Get payment date of a transaction&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;transaction_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The transaction id.&quot; , 
 } 
 } , 
 &quot;required&quot; : [ &quot;transaction_id&quot; ] , 
 } , 
 } , 
 } 
 ] 
 # Note: You can specify multiple parameters for each function in the `properties` object. 
 Step 2. User Copy section link Step 2. User 
 Query the Model 
 With our functions and instructions ready, lets Suppose a user asks the following question: &quot;What&#x27;s the status of my transaction T1001?&quot; A standalone LLM would not be able to answer this question, as it needs to query the business logic backend to access the necessary data. But with function calling, we can use the tools we have defined to answer accordingly. 
 python typescript messages . append ( { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : &quot;What&#x27;s the status of my transaction T1001?&quot; } ) messages . append ( { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : &quot;What&#x27;s the status of my transaction T1001?&quot; } ) 
 The previous question expects the model to use the retrieve_payment_status function to get the payment status of transaction T1001. 
 Step 3. Model Copy section link Step 3. Model 
 Generate Function Arguments 
 How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It&#x27;s to: 
 Determine the appropriate function to use. 
 Identify if there is any essential information missing for a function. 
 Generate necessary arguments for the chosen function. 
 Developers can use tool_choice to specify how tools are used: 
 &quot;auto&quot;: default mode. Model decides if it uses the tool or not. 
 &quot;any&quot;: forces tool use. 
 &quot;none&quot;: prevents tool use. 
 And parallel_tool_calls to specify whether parallel tool calling is allowed. 
 true: default mode. The model decides if it uses parallel tool calls or not. 
 false: forces the model to use single tool calling. 
 With all our tools, system and query ready, we can call the model to either reply or use the tools, generating the necessary arguments for the chosen function . 
 python typescript Output V2 V1 import os
 from mistralai . client import Mistral
 api_key = os . environ [ &quot;MISTRAL_API_KEY&quot; ] 
 model = &quot;mistral-large-latest&quot; 
 client = Mistral ( api_key = api_key ) 
 response = client . chat . complete ( 
 model = model , # The model we want to use 
 messages = messages , # The message history, in this example we have a system (optional) + user query. 
 tools = tools , # The tools specifications 
 tool_choice = &quot;any&quot; , 
 parallel_tool_calls = False , 
 ) import os
 from mistralai . client import Mistral
 api_key = os . environ [ &quot;MISTRAL_API_KEY&quot; ] 
 model = &quot;mistral-large-latest&quot; 
 client = Mistral ( api_key = api_key ) 
 response = client . chat . complete ( 
 model = model , # The model we want to use 
 messages = messages , # The message history, in this example we have a system (optional) + user query. 
 tools = tools , # The tools specifications 
 tool_choice = &quot;any&quot; , 
 parallel_tool_calls = False , 
 ) 
 The model provided a tool call as a response, visit the raw output for more information: 
 [ 
 { 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_status&quot; , 
 &quot;arguments&quot; : &quot;{\&quot;transaction_id\&quot;: \&quot;T1001\&quot;}&quot; 
 } , 
 &quot;id&quot; : &quot;D681PevKs&quot; , 
 &quot;type&quot; : &quot;function&quot; 
 } 
 ] [ 
 { 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_status&quot; , 
 &quot;arguments&quot; : &quot;{\&quot;transaction_id\&quot;: \&quot;T1001\&quot;}&quot; 
 } , 
 &quot;id&quot; : &quot;D681PevKs&quot; , 
 &quot;type&quot; : &quot;function&quot; 
 } 
 ] 
 Let&#x27;s add the response message to the messages list history to continue the conversation. 
 python typescript messages . append ( response . choices [ 0 ] . message ) messages . append ( response . choices [ 0 ] . message ) 
 Here, we got the response including tool_calls with the chosen function name retrieve_payment_status and the arguments for this function, the next step is to execute the function. 
 Step 4. Developer Copy section link Step 4. Developer 
 Execute Functions 
 How do we execute the function? Currently, it is the developer&#x27;s responsibility to execute these functions and the function execution lies on the user/developer side. We have also introduced some tools executed server side for our Agents and Conversations API, visit Tools . 
 To execute it, we extract some useful function information from the model response including function_name and function_params . It&#x27;s clear here that our model has chosen to use retrieve_payment_status with the parameter transaction_id set to T1001. 
 python typescript Output import json
 tool_call = response . choices [ 0 ] . message . tool_calls [ 0 ] 
 function_name = tool_call . function . name # The function name to call 
 function_params = json . loads ( tool_call . function . arguments ) # The function arguments 
 print ( &quot;\nfunction_name: &quot; , function_name , &quot;\nfunction_params: &quot; , function_params ) import json
 tool_call = response . choices [ 0 ] . message . tool_calls [ 0 ] 
 function_name = tool_call . function . name # The function name to call 
 function_params = json . loads ( tool_call . function . arguments ) # The function arguments 
 print ( &quot;\nfunction_name: &quot; , function_name , &quot;\nfunction_params: &quot; , function_params ) 
 We then execute the corresponding function and we get the function output &#x27;{&quot;status&quot;: &quot;Paid&quot;}&#x27; . 
 python typescript Output function_result = names_to_functions [ function_name ] ( ** function_params ) 
 print ( function_result ) function_result = names_to_functions [ function_name ] ( ** function_params ) 
 print ( function_result ) 
 Step 5. Model Copy section link Step 5. Model 
 Generate Followup Answer 
 We can now provide the output from the tools/functions to our model, and in return, the model can produce a customised final response for the specific user (or in some cases, another tool call) 
 python typescript Output messages . append ( { 
 &quot;role&quot; : &quot;tool&quot; , 
 &quot;name&quot; : function_name , 
 &quot;content&quot; : function_result , 
 &quot;tool_call_id&quot; : tool_call . id 
 } ) 
 response = client . chat . complete ( 
 model = model , 
 messages = messages
 ) 
 response . choices [ 0 ] . message . content messages . append ( { 
 &quot;role&quot; : &quot;tool&quot; , 
 &quot;name&quot; : function_name , 
 &quot;content&quot; : function_result , 
 &quot;tool_call_id&quot; : tool_call . id 
 } ) 
 response = client . chat . complete ( 
 model = model , 
 messages = messages
 ) 
 response . choices [ 0 ] . message . content 
 Our model has successfully generated a response using the output from the tool, providing the final answer: 
 &quot;The status of your transaction with ID T1001 is Paid. Is there anything else I can assist you with?&quot; 
 Note A model is allowed to followup a tool call with another tool call. To handle such scenarios, you should recursively call the model with the new tool call until it generates a final answer . 
 Full Example Copy section link Full Example 
 Below you can find a full example of the above steps looping to simulate a chat session, interactivelly handling successive and/or parallel tool calls. 
 python typescript V2 V1 # Imports 
 import pandas as pd
 import os
 from mistralai . client import Mistral
 import json
 # Example Dataset to query from 
 data = { 
 &#x27;transaction_id&#x27; : [ &#x27;T1001&#x27; , &#x27;T1002&#x27; , &#x27;T1003&#x27; , &#x27;T1004&#x27; , &#x27;T1005&#x27; ] , 
 &#x27;customer_id&#x27; : [ &#x27;C001&#x27; , &#x27;C002&#x27; , &#x27;C003&#x27; , &#x27;C002&#x27; , &#x27;C001&#x27; ] , 
 &#x27;payment_amount&#x27; : [ 125.50 , 89.99 , 120.00 , 54.30 , 210.20 ] , 
 &#x27;payment_date&#x27; : [ &#x27;2021-10-05&#x27; , &#x27;2021-10-06&#x27; , &#x27;2021-10-07&#x27; , &#x27;2021-10-05&#x27; , &#x27;2021-10-08&#x27; ] , 
 &#x27;payment_status&#x27; : [ &#x27;Paid&#x27; , &#x27;Unpaid&#x27; , &#x27;Paid&#x27; , &#x27;Paid&#x27; , &#x27;Pending&#x27; ] 
 } 
 df = pd . DataFrame ( data ) 
 # Functions to be used as tools 
 def retrieve_payment_status ( transaction_id : str ) - &gt; str : 
 &quot;Get payment status of a transaction&quot; 
 if transaction_id in df . transaction_id . values : 
 return json . dumps ( { &#x27;status&#x27; : df [ df . transaction_id == transaction_id ] . payment_status . item ( ) } ) 
 return json . dumps ( { &#x27;error&#x27; : &#x27;transaction id not found.&#x27; } ) 
 def retrieve_payment_date ( transaction_id : str ) - &gt; str : 
 &quot;Get payment date of a transaction&quot; 
 if transaction_id in df . transaction_id . values : 
 return json . dumps ( { &#x27;date&#x27; : df [ df . transaction_id == transaction_id ] . payment_date . item ( ) } ) 
 return json . dumps ( { &#x27;error&#x27; : &#x27;transaction id not found.&#x27; } ) 
 # Map function names to the functions 
 names_to_functions = { 
 &#x27;retrieve_payment_status&#x27; : retrieve_payment_status , 
 &#x27;retrieve_payment_date&#x27; : retrieve_payment_date , 
 } 
 # Define the system prompt 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a helpful assistant. You can use the following tools to help answer the user&#x27;s questions related to payment transactions.&quot; 
 } 
 ] 
 # Define the tools specifications 
 tools = [ 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_status&quot; , 
 &quot;description&quot; : &quot;Get payment status of a transaction&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;transaction_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The transaction id.&quot; , 
 } 
 } , 
 &quot;required&quot; : [ &quot;transaction_id&quot; ] , 
 } , 
 } , 
 } , 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_date&quot; , 
 &quot;description&quot; : &quot;Get payment date of a transaction&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;transaction_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The transaction id.&quot; , 
 } 
 } , 
 &quot;required&quot; : [ &quot;transaction_id&quot; ] , 
 } , 
 } , 
 } 
 ] 
 # Note: You can specify multiple parameters for each function in the `properties` object. 
 # Initialize the client and model 
 api_key = os . environ [ &quot;MISTRAL_API_KEY&quot; ] 
 model = &quot;mistral-large-latest&quot; 
 client = Mistral ( api_key = api_key ) 
 temperature = 0.1 
 top_p = 0.9 
 # Chat loop 
 while True : 
 # The user query, example: &quot;What&#x27;s the status of my transaction T1001? After receiving the answer, provide the current status of T1001. Afte that, look for the next one between T1002 if previous status was &#x27;Paid&#x27; and T1003 if previous status was &#x27;Unpaid&#x27;.&quot; 
 user_query = input ( &quot;User: &quot; ) 
 if not user_query : 
 break 
 messages . append ( { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : user_query } ) 
 # Call the model 
 response = client . chat . complete ( 
 model = model , 
 messages = messages , 
 tools = tools , 
 temperature = temperature , 
 top_p = top_p
 ) 
 # Add the response message to the messages list 
 messages . append ( response . choices [ 0 ] . message ) 
 # Retrieve the function name and arguments if any, interactively until the model returns a final answer 
 while response . choices [ 0 ] . message . tool_calls : 
 # Print content in case we have interleaved tool calls and text content 
 if response . choices [ 0 ] . message . content : 
 print ( &quot;Assistant:&quot; , response . choices [ 0 ] . message . content ) 
 # Handle each tool call 
 for tool_call in response . choices [ 0 ] . message . tool_calls : 
 function_name = tool_call . function . name # The function name to call 
 function_params = json . loads ( tool_call . function . arguments ) # The function arguments 
 function_result = names_to_functions [ function_name ] ( ** function_params ) # The function result 
 # Print the function call 
 print ( f&quot;Tool { tool_call . id } :&quot; , f&quot; { function_name } ( { function_params } ) -&gt; { function_result } &quot; ) 
 # Add the function result to the messages list and call model 
 messages . append ( { 
 &quot;role&quot; : &quot;tool&quot; , 
 &quot;name&quot; : function_name , 
 &quot;content&quot; : function_result , 
 &quot;tool_call_id&quot; : tool_call . id 
 } ) 
 response = client . chat . complete ( 
 model = model , 
 messages = messages , 
 tools = tools , 
 temperature = temperature , 
 top_p = top_p
 ) 
 # Add the new response message to the messages list 
 messages . append ( response . choices [ 0 ] . message ) 
 # Print the final answer 
 print ( &quot;Assistant:&quot; , response . choices [ 0 ] . message . content ) # Imports 
 import pandas as pd
 import os
 from mistralai . client import Mistral
 import json
 # Example Dataset to query from 
 data = { 
 &#x27;transaction_id&#x27; : [ &#x27;T1001&#x27; , &#x27;T1002&#x27; , &#x27;T1003&#x27; , &#x27;T1004&#x27; , &#x27;T1005&#x27; ] , 
 &#x27;customer_id&#x27; : [ &#x27;C001&#x27; , &#x27;C002&#x27; , &#x27;C003&#x27; , &#x27;C002&#x27; , &#x27;C001&#x27; ] , 
 &#x27;payment_amount&#x27; : [ 125.50 , 89.99 , 120.00 , 54.30 , 210.20 ] , 
 &#x27;payment_date&#x27; : [ &#x27;2021-10-05&#x27; , &#x27;2021-10-06&#x27; , &#x27;2021-10-07&#x27; , &#x27;2021-10-05&#x27; , &#x27;2021-10-08&#x27; ] , 
 &#x27;payment_status&#x27; : [ &#x27;Paid&#x27; , &#x27;Unpaid&#x27; , &#x27;Paid&#x27; , &#x27;Paid&#x27; , &#x27;Pending&#x27; ] 
 } 
 df = pd . DataFrame ( data ) 
 # Functions to be used as tools 
 def retrieve_payment_status ( transaction_id : str ) - &gt; str : 
 &quot;Get payment status of a transaction&quot; 
 if transaction_id in df . transaction_id . values : 
 return json . dumps ( { &#x27;status&#x27; : df [ df . transaction_id == transaction_id ] . payment_status . item ( ) } ) 
 return json . dumps ( { &#x27;error&#x27; : &#x27;transaction id not found.&#x27; } ) 
 def retrieve_payment_date ( transaction_id : str ) - &gt; str : 
 &quot;Get payment date of a transaction&quot; 
 if transaction_id in df . transaction_id . values : 
 return json . dumps ( { &#x27;date&#x27; : df [ df . transaction_id == transaction_id ] . payment_date . item ( ) } ) 
 return json . dumps ( { &#x27;error&#x27; : &#x27;transaction id not found.&#x27; } ) 
 # Map function names to the functions 
 names_to_functions = { 
 &#x27;retrieve_payment_status&#x27; : retrieve_payment_status , 
 &#x27;retrieve_payment_date&#x27; : retrieve_payment_date , 
 } 
 # Define the system prompt 
 messages = [ 
 { 
 &quot;role&quot; : &quot;system&quot; , 
 &quot;content&quot; : &quot;You are a helpful assistant. You can use the following tools to help answer the user&#x27;s questions related to payment transactions.&quot; 
 } 
 ] 
 # Define the tools specifications 
 tools = [ 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_status&quot; , 
 &quot;description&quot; : &quot;Get payment status of a transaction&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;transaction_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The transaction id.&quot; , 
 } 
 } , 
 &quot;required&quot; : [ &quot;transaction_id&quot; ] , 
 } , 
 } , 
 } , 
 { 
 &quot;type&quot; : &quot;function&quot; , 
 &quot;function&quot; : { 
 &quot;name&quot; : &quot;retrieve_payment_date&quot; , 
 &quot;description&quot; : &quot;Get payment date of a transaction&quot; , 
 &quot;parameters&quot; : { 
 &quot;type&quot; : &quot;object&quot; , 
 &quot;properties&quot; : { 
 &quot;transaction_id&quot; : { 
 &quot;type&quot; : &quot;string&quot; , 
 &quot;description&quot; : &quot;The transaction id.&quot; , 
 } 
 } , 
 &quot;required&quot; : [ &quot;transaction_id&quot; ] , 
 } , 
 } , 
 } 
 ] 
 # Note: You can specify multiple parameters for each function in the `properties` object. 
 # Initialize the client and model 
 api_key = os . environ [ &quot;MISTRAL_API_KEY&quot; ] 
 model = &quot;mistral-large-latest&quot; 
 client = Mistral ( api_key = api_key ) 
 temperature = 0.1 
 top_p = 0.9 
 # Chat loop 
 while True : 
 # The user query, example: &quot;What&#x27;s the status of my transaction T1001? After receiving the answer, provide the current status of T1001. Afte that, look for the next one between T1002 if previous status was &#x27;Paid&#x27; and T1003 if previous status was &#x27;Unpaid&#x27;.&quot; 
 user_query = input ( &quot;User: &quot; ) 
 if not user_query : 
 break 
 messages . append ( { &quot;role&quot; : &quot;user&quot; , &quot;content&quot; : user_query } ) 
 # Call the model 
 response = client . chat . complete ( 
 model = model , 
 messages = messages , 
 tools = tools , 
 temperature = temperature , 
 top_p = top_p
 ) 
 # Add the response message to the messages list 
 messages . append ( response . choices [ 0 ] . message ) 
 # Retrieve the function name and arguments if any, interactively until the model returns a final answer 
 while response . choices [ 0 ] . message . tool_calls : 
 # Print content in case we have interleaved tool calls and text content 
 if response . choices [ 0 ] . message . content : 
 print ( &quot;Assistant:&quot; , response . choices [ 0 ] . message . content ) 
 # Handle each tool call 
 for tool_call in response . choices [ 0 ] . message . tool_calls : 
 function_name = tool_call . function . name # The function name to call 
 function_params = json . loads ( tool_call . function . arguments ) # The function arguments 
 function_result = names_to_functions [ function_name ] ( ** function_params ) # The function result 
 # Print the function call 
 print ( f&quot;Tool { tool_call . id } :&quot; , f&quot; { function_name } ( { function_params } ) -&gt; { function_result } &quot; ) 
 # Add the function result to the messages list and call model 
 messages . append ( { 
 &quot;role&quot; : &quot;tool&quot; , 
 &quot;name&quot; : function_name , 
 &quot;content&quot; : function_result , 
 &quot;tool_call_id&quot; : tool_call . id 
 } ) 
 response = client . chat . complete ( 
 model = model , 
 messages = messages , 
 tools = tools , 
 temperature = temperature , 
 top_p = top_p
 ) 
 # Add the new response message to the messages list 
 messages . append ( response . choices [ 0 ] . message ) 
 # Print the final answer 
 print ( &quot;Assistant:&quot; , response . choices [ 0 ] . message . content ) 
 More Copy section link More 
 If you are interested in function calling and want to explore built-in solutions, MCP, and other agentic use cases, we invite you to visit the Agents documentation here . WHY MISTRAL About us Our customers Careers Contact us EXPLORE AI Solutions Partners Research DOCUMENTATION Documentation Ambassadors Cookbooks BUILD Studio Vibe Mistral Code Mistral Compute Try the API LEGAL Terms of service Privacy policy Legal notice Privacy Choices Brand COMMUNITY Discord ↗ X ↗ Github ↗ LinkedIn ↗ Ambassadors Mistral AI © 2026 Toggle theme Prompt caching Structured Outputs 