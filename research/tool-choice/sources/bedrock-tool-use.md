 
 Use a tool to complete an Amazon Bedrock model response - Amazon Bedrock 
 View a markdown version of this page Use a tool to complete an Amazon Bedrock model response - Amazon Bedrock Documentation Amazon Bedrock User Guide Use a tool to complete an Amazon Bedrock model response You can use the Amazon Bedrock API to give a model access to tools that can help it generate responses for messages that you send to the model. For example, you might have a chat application that lets users find out the most popular song played on a radio station. To answer a request for the most popular song, a model needs a tool that can query and return the song information. Note You can now use structured outputs with tool use. See Get validated JSON results from models for more details. In Amazon Bedrock, the model doesn't directly call the tool. When you send a message, you also supply definitions for one or more tools that could help the model generate a response. The model decides when a tool is needed; your application code (or Amazon Bedrock itself, in server-side mode) executes the tool and returns the result for the model to incorporate in its final response. Amazon Bedrock supports three modes of tool use, depending on which API you call and which model family you use: 
 Mode 
 Who runs the tool 
 When to use it 
 Client-side tool use 
 Your application code, after the model returns a tool-call request. 
 Most use cases. Available with the Responses, Chat Completions, Converse, and InvokeModel APIs. 
 Server-side tool use 
 Amazon Bedrock itself. You register a Lambda function or AgentCore Gateway, and Amazon Bedrock invokes the tool on the model's behalf. 
 Centralized, secure tool execution without managing orchestration in your application. Currently available on the Responses API. 
 Anthropic Claude tool use 
 Your application code, using Anthropic-defined tool types ( computer_* , bash_* , text_editor_* , memory_* ) and the Anthropic Messages API request format. 
 Computer use, code execution, file editing, persistent memory, or fine-grained tool streaming with Claude models on bedrock-runtime or bedrock-mantle . 
 Javascript is disabled or is unavailable in your browser. To use the Amazon Web Services Documentation, Javascript must be enabled. Please refer to your browser's Help pages for instructions. Document Conventions Supported Regions and models Client-side Did this page help you? - Yes Thanks for letting us know we're doing a good job! If you've got a moment, please tell us what we did right so we can do more of it. Did this page help you? - No Thanks for letting us know this page needs work. We're sorry we let you down. If you've got a moment, please tell us how we can make the documentation better. 