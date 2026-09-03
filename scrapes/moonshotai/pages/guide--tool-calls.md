> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use Kimi API for Tool Calls

> Define, register, and execute Kimi API `tool_calls`, return tool results, and handle tool calls in streaming responses.

Tool calls (`tool_calls`) let the Kimi large language model go beyond "talking" to "doing": the model decides whether to call a tool based on the conversation context, generates the call arguments in JSON, and your application executes the tool and returns the result so the model can produce the final reply. With `tool_calls`, the Kimi large language model can help you search the internet, query databases, and even control smart home devices. This page walks through the full flow — defining, registering, and executing tools — with an internet-search example, plus notes for streaming and other scenarios.

## The Complete Flow of a Tool Call

A tool call involves the following steps:

1. Define the tool using JSON Schema format;
2. Submit the defined tool to the Kimi large language model via the `tools` parameter. You can submit multiple tools at once;
3. The Kimi large language model will decide which tool(s) to use based on the context of the current conversation. It can also choose not to use any tools;
4. The Kimi large language model will output the parameters and information needed to call the tool in JSON format;
5. Use the parameters output by the Kimi large language model to execute the corresponding tool and submit the results back to the Kimi large language model;
6. The Kimi large language model will respond to the user based on the results of the tool execution;

<Tip>
  If your application needs a large tool inventory (dozens or hundreds of tools), use [Dynamically Loaded Tools](/docs/guide/use-dynamic-tool-loading) to inject tool definitions on demand instead of submitting them all at once — this significantly reduces token usage and improves tool-selection accuracy.
</Tip>

## Give the Model Internet Access with Tool Calls

The knowledge of the Kimi large language model comes from its training data, so it cannot answer time-sensitive questions from what it already knows. The example below uses two tools — a "search engine" and a "web browser" — to show how the model can search for the latest information and answer based on it.

### Define Tools with JSON Schema

When people look up information online, they usually open a search engine (such as Baidu or Bing), browse the search results, and then open one or more result pages to get the knowledge they need. Abstracting these two actions into tools gives us a "search engine" and a "web browser" — described in JSON Schema and submitted to the Kimi large language model, so it can search and browse the web just like humans do.

Tool definitions are written in JSON Schema format:

> [JSON Schema](https://json-schema.org/) is a vocabulary that you can use to annotate and validate JSON documents.
>
> [JSON Schema](https://json-schema.org/) is a JSON document used to describe the format of JSON data.

We define the following JSON Schema:

```json theme={null}
{
	"type": "object",
	"properties": {
		"name": {
			"type": "string"
		}
	}
}
```

This JSON Schema defines a JSON Object that contains a field named `name`, and the type of this field is `string`, for example:

```json theme={null}
{
	"name": "Hei"
}
```

By describing our tool definitions using JSON Schema, we can make it clearer and more intuitive for the Kimi large language model to understand what parameters our tools require, as well as the type and description of each parameter. Now let's define the "search engine" and "web browser" tools mentioned earlier:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    tools = [
    	{
    		"type": "function", # The agreed-upon field type, currently supports function as a value
    		"function": { # When type is function, use the function field to define the specific function content
    			"name": "search", # The name of the function. Please use English letters, numbers, hyphens, and underscores as the function name
    			"description": """ 
    				Search for content on the internet using a search engine.

    				When your knowledge cannot answer the user's question, or when the user requests an online search, call this tool. Extract the content the user wants to search for from the conversation and use it as the value of the query parameter.
    				The search results include the website title, address (URL), and description.
    			""", # A description of the function, detailing its specific role and usage scenarios, to help the Kimi large language model correctly select which functions to use
    			"parameters": { # Use the parameters field to define the parameters the function accepts
    				"type": "object", # Always use type: object to make the Kimi large language model generate a JSON Object parameter
    				"required": ["query"], # Use the required field to tell the Kimi large language model which parameters are mandatory
    				"properties": { # The properties field contains the specific parameter definitions; you can define multiple parameters
    					"query": { # Here, the key is the parameter name, and the value is the specific definition of the parameter
    						"type": "string", # Use type to define the parameter type
    						"description": """
    							The content the user wants to search for, extracted from the user's question or conversation context.
    						""" # Use description to describe the parameter so that the Kimi large language model can better generate the parameter
    					}
    				}
    			}
    		}
    	},
    	{
    		"type": "function", # The agreed-upon field type, currently supports function as a value
    		"function": { # When type is function, use the function field to define the specific function content
    			"name": "crawl", # The name of the function. Please use English letters, numbers, hyphens, and underscores as the function name
    			"description": """
    				Retrieve web page content based on the website address (URL).
    			""", # A description of the function, detailing its specific role and usage scenarios, to help the Kimi large language model correctly select which functions to use
    			"parameters": { # Use the parameters field to define the parameters the function accepts
    				"type": "object", # Always use type: object to make the Kimi large language model generate a JSON Object parameter
    				"required": ["url"], # Use the required field to tell the Kimi large language model which parameters are mandatory
    				"properties": { # The properties field contains the specific parameter definitions; you can define multiple parameters
    					"url": { # Here, the key is the parameter name, and the value is the specific definition of the parameter
    						"type": "string", # Use type to define the parameter type
    						"description": """
    							The website address (URL) from which to retrieve content, usually obtained from search results.
    						""" # Use description to describe the parameter so that the Kimi large language model can better generate the parameter
    					}
    				}
    			}
    		}
    	}
    ]
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const tools = [
    	{
    		"type": "function", // The field "type" is a convention, currently supporting "function" as its value
    		"function": { // When "type" is "function", use the "function" field to define the specific function content
    			"name": "search", // The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
    			"description": ""/* 
    				Search for content on the internet using a search engine.
     
    				When your knowledge cannot answer the user's question, or when the user requests an online search, call this tool. Extract the content the user wants to search from the conversation as the value of the query parameter.
    				The search results include the website title, website address (URL), and website description.
    			*/, // Description of the function, write the specific function and usage scenarios here so that the Kimi large language model can correctly choose which functions to use
    			"parameters": { // Use the "parameters" field to define the parameters accepted by the function
    				"type": "object", // Always use "type": "object" to make the Kimi large language model generate a JSON Object parameter
    				"required": ["query"], // Use the "required" field to tell the Kimi large language model which parameters are required
    				"properties": { // The specific parameter definitions are in "properties", you can define multiple parameters
    					"query": { // Here, the key is the parameter name, and the value is the specific definition of the parameter
    						"type": "string", // Use "type" to define the parameter type
    						"description": ""/*
    							The content the user wants to search for, extract it from the user's question or chat context.
    						*/ // Use "description" to describe the parameter so that the Kimi large language model can better generate the parameter
    					}
    				}
    			}
    		}
    	},
    	{
    		"type": "function", // The field "type" is a convention, currently supporting "function" as its value
    		"function": { // When "type" is "function", use the "function" field to define the specific function content
    			"name": "crawl", // The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
    			"description": ""/*
    				Get the content of a webpage based on the website address (URL).
    			*/, // Description of the function, write the specific function and usage scenarios here so that the Kimi large language model can correctly choose which functions to use
    			"parameters": { // Use the "parameters" field to define the parameters accepted by the function
    				"type": "object", // Always use "type": "object" to make the Kimi large language model generate a JSON Object parameter
    				"required": ["url"], // Use the "required" field to tell the Kimi large language model which parameters are required
    				"properties": { // The specific parameter definitions are in "properties", you can define multiple parameters
    					"url": { // Here, the key is the parameter name, and the value is the specific definition of the parameter
    						"type": "string", // Use "type" to define the parameter type
    						"description": ""/*
    							The website address (URL) of the content to be obtained, which can usually be obtained from the search results.
    						*/ // Use "description" to describe the parameter so that the Kimi large language model can better generate the parameter
    					}
    				}
    			}
    		}
    	}
    ]
    ```
  </Tab>
</Tabs>

When defining tools using JSON Schema, we use the following fixed format:

```json theme={null}
{
	"type": "function",
	"function": {
		"name": "NAME",
		"description": "DESCRIPTION",
		"parameters": {
			"type": "object",
			"properties": {
				
			}
		}
	}
}
```

Here, `name`, `description`, and `parameters.properties` are defined by the tool provider. The `description` explains the specific function and when to use the tool, while `parameters` outlines the specific parameters needed to successfully call the tool, including parameter types and descriptions. **Ultimately, the Kimi large language model will generate a JSON Object that meets the defined requirements as the parameters (arguments) for the tool call based on the JSON Schema.**

### Register the Tools with the Model

Submit the `search` tool to the Kimi large language model and see if it can call the tool correctly:

<Note>
  The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
</Note>

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    from openai import OpenAI


    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url="https://api.moonshot.ai/v1",
    )

    tools = [
    	{
    		"type": "function", # The field "type" is a convention, currently supporting "function" as its value
    		"function": { # When "type" is "function", use the "function" field to define the specific function content
    			"name": "search", # The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
    			"description": """ 
    				Search for content on the internet using a search engine.

    				When your knowledge cannot answer the user's question, or when the user requests an online search, call this tool. Extract the content the user wants to search from the conversation as the value of the query parameter.
    				The search results include the website title, website address (URL), and website description.
    			""", # Description of the function, write the specific function and usage scenarios here so that the Kimi large language model can correctly choose which functions to use
    			"parameters": { # Use the "parameters" field to define the parameters accepted by the function
    				"type": "object", # Always use "type": "object" to make the Kimi large language model generate a JSON Object parameter
    				"required": ["query"], # Use the "required" field to tell the Kimi large language model which parameters are required
    				"properties": { # The specific parameter definitions are in "properties", you can define multiple parameters
    					"query": { # Here, the key is the parameter name, and the value is the specific definition of the parameter
    						"type": "string", # Use "type" to define the parameter type
    						"description": """
    							The content the user wants to search for, extract it from the user's question or chat context.
    						""" # Use "description" to describe the parameter so that the Kimi large language model can better generate the parameter
    					}
    				}
    			}
    		}
    	},
    	# {
    	# 	"type": "function", # The field "type" is a convention, currently supporting "function" as its value
    	# 	"function": { # When "type" is "function", use the "function" field to define the specific function content
    	# 		"name": "crawl", # The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
    	# 		"description": """
    	# 			Get the content of a webpage based on the website address (URL).
    	# 		""", // Description of the function, write the specific function and usage scenarios here so that the Kimi large language model can correctly choose which functions to use
    	# 		"parameters": { // Use the "parameters" field to define the parameters accepted by the function
    	# 			"type": "object", // Always use "type": "object" to make the Kimi large language model generate a JSON Object parameter
    	# 			"required": ["url"], // Use the "required" field to tell the Kimi large language model which parameters are required
    	# 			"properties": { // The specific parameter definitions are in "properties", you can define multiple parameters
    	# 				"url": { // Here, the key is the parameter name, and the value is the specific definition of the parameter
    	# 					"type": "string", // Use "type" to define the parameter type
    	# 					"description": """
    	# 						The website address (URL) of the content to be obtained, which can usually be obtained from the search results.
    	# 					""" // Use "description" to describe the parameter so that the Kimi large language model can better generate the parameter
    	# 				}
    	# 			}
    	# 		}
    	# 	}
    	# }
    ]

    completion = client.chat.completions.create(
        model="kimi-k3",
        messages=[
            {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are proficient in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You refuse to answer any questions related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated."},
            {"role": "user", "content": "Please search the internet for 'Context Caching' and tell me what it is."} # In the question, we ask Kimi large language model to search online
        ],
        tools=tools, # <-- We pass the defined tools to Kimi large language model via the tools parameter
    )

    print(completion.choices[0].model_dump_json(indent=4))
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const OpenAI = require("openai")
     
     
    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY, // Set the MOONSHOT_API_KEY environment variable before running this example
        baseURL: "https://api.moonshot.ai/v1",
    })
     
    const tools = [
    	{
    		"type": "function", // The agreed-upon field type, currently supports function as a value
    		"function": { // When type is function, use the function field to define the specific function content
    			"name": "search", // The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
    			"description": ""/* 
    				Search for content on the internet using a search engine.
     
    				When your knowledge cannot answer the user's question, or the user requests you to search online, call this tool. Extract the content the user wants to search from the conversation as the value of the query parameter.
    				The search results include the website title, website address (URL), and website description.
    			*/, // Description of the function, write the specific function's role and usage scenario here to help Kimi large language model correctly choose which functions to use
    			"parameters": { // Use the parameters field to define the parameters the function accepts
    				"type": "object", // Fixedly use type: object to make Kimi large language model generate a JSON Object parameter
    				"required": ["query"], // Use the required field to tell Kimi large language model which parameters are required
    				"properties": { // The specific parameter definitions are in properties, you can define multiple parameters
    					"query": { // Here, the key is the parameter name, and the value is the specific definition of the parameter
    						"type": "string", // Use type to define the parameter type
    						"description": ""/*
    							The content the user wants to search for, extracted from the user's question or chat context.
    						*/ // Use description to describe the parameter so that Kimi large language model can better generate the parameter
    					}
    				}
    			}
    		}
    	},
    	// {
    	// 	"type": "function", // The agreed-upon field type, currently supports function as a value
    	// 	"function": { // When type is function, use the function field to define the specific function content
    	// 		"name": "crawl", // The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
    	// 		"description": """
    	// 			Get the webpage content based on the website address (URL).
    	// 		""", // Description of the function, write the specific function's role and usage scenario here to help Kimi large language model correctly choose which functions to use
    	// 		"parameters": { // Use the parameters field to define the parameters the function accepts
    	// 			"type": "object", // Fixedly use type: object to make Kimi large language model generate a JSON Object parameter
    	// 			"required": ["url"], // Use the required field to tell Kimi large language model which parameters are required
    	// 			"properties": { // The specific parameter definitions are in properties, you can define multiple parameters
    	// 				"url": { // Here, the key is the parameter name, and the value is the specific definition of the parameter
    	// 					"type": "string", // Use type to define the parameter type
    	// 					"description": """
    	// 						The website address (URL) whose content needs to be obtained, usually the website address can be obtained from the search results.
    	// 					""" // Use description to describe the parameter so that Kimi large language model can better generate the parameter
    	// 				}
    	// 			}
    	// 		}
    	// 	}
    	// }
    ]

    async function main() {
        const completion = await client.chat.completions.create({
            model: "kimi-k3",
            messages: [
                {role: "system", content: "You are Kimi, an AI assistant provided by Moonshot AI. You are proficient in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You refuse to answer any questions related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated."},
                {role: "user", content: "Please search the internet for 'Context Caching' and tell me what it is."} // In the question, we ask Kimi large language model to search online
            ],
            tools: tools, // <-- We pass the defined tools to Kimi large language model via the tools parameter
        })
         
        console.log(JSON.stringify(completion.choices[0], null, 4))
    }

    main()
    ```
  </Tab>
</Tabs>

When the above code runs successfully, we get the response from Kimi large language model:

```json theme={null}
{
    "finish_reason": "tool_calls",
    "message": {
        "content": "",
        "role": "assistant",
        "tool_calls": [
            {
                "id": "search:0",
                "function": {
                    "arguments": "{\n    \"query\": \"Context Caching\"\n}",
                    "name": "search"
                },
                "type": "function"
            }
        ]
    }
}
```

Notice that in this response, the value of `finish_reason` is `tool_calls`, which means that the response is not the answer from Kimi large language model, but rather the tool that Kimi large language model has chosen to execute. You can determine whether the current response from Kimi large language model is a tool call `tool_calls` by checking the value of `finish_reason`.

At this point the `content` field in `message` is empty, because the model is executing `tool_calls` and has not yet generated a reply for the user. The newly added `tool_calls` field is a list containing all the tool call information for this turn — which shows that **the model can choose to call multiple tools at once, which can be different tools or the same tool with different parameters**. Each element in `tool_calls` represents one tool call: the Kimi large language model generates a unique `id` for each call, uses `function.name` to indicate the name of the tool function, and places the call parameters in `function.arguments` (`arguments` is a valid serialized JSON Object; additionally, the `type` parameter is currently a fixed value `function`).

Next, use the tool call parameters generated by the Kimi large language model to execute the corresponding tools.

### Execute the Tools and Return the Results

The Kimi large language model does not execute tools for you — once you receive the parameters it generates, your application must execute them. Why can't the model execute tools itself? Imagine a typical scenario: **you provide users with a smart robot based on the Kimi large language model. In this scenario, there are three roles: the user, the robot, and the Kimi large language model. The user asks the robot a question, the robot calls the Kimi large language model API, and returns the API result to the user. When using `tool_calls`, the user asks the robot a question, the robot calls the Kimi API with `tools`, the Kimi large language model returns the `tool_calls` parameters, the robot executes the `tool_calls`, submits the results back to the Kimi API, the Kimi large language model generates the message to be returned to the user (`finish_reason=stop`), and only then does the robot return the message to the user.** The entire `tool_calls` process is transparent and implicit to the user: users never directly "see" the tool calls, only the final reply presented by the robot.

The full example below executes the `tool_calls` returned by the Kimi large language model from the perspective of the "robot", demonstrating the tool-execution loop:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    from typing import *

    import json
    import httpx
    import os

    from openai import OpenAI


    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url="https://api.moonshot.ai/v1",
    )

    tools = [
    	{
    		"type": "function", # The field type is agreed upon, and currently supports function as a value
    		"function": { # When type is function, use the function field to define the specific function content
    			"name": "search", # The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
    			"description": """ 
    				Search for content on the internet using a search engine.

    				When your knowledge cannot answer the user's question, or the user requests you to perform an online search, call this tool. Extract the content the user wants to search from the conversation as the value of the query parameter.
    				The search results include the title of the website, the website address (URL), and a brief introduction to the website.
    			""", # Introduction to the function, write the specific function here, as well as the usage scenario, so that the Kimi large language model can correctly choose which functions to use
    			"parameters": { # Use the parameters field to define the parameters accepted by the function
    				"type": "object", # Fixed use type: object to make the Kimi large language model generate a JSON Object parameter
    				"required": ["query"], # Use the required field to tell the Kimi large language model which parameters are required
    				"properties": { # The specific parameter definitions are in properties, and you can define multiple parameters
    					"query": { # Here, the key is the parameter name, and the value is the specific definition of the parameter
    						"type": "string", # Use type to define the parameter type
    						"description": """
    							The content the user wants to search for, extracted from the user's question or chat context.
    						""" # Use description to describe the parameter so that the Kimi large language model can better generate the parameter
    					}
    				}
    			}
    		}
    	},
    	{
    		"type": "function", # The field type is agreed upon, and currently supports function as a value
    		"function": { # When type is function, use the function field to define the specific function content
    			"name": "crawl", # The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
    			"description": """
    				Get the content of a webpage based on the website address (URL).
    			""", # Introduction to the function, write the specific function here, as well as the usage scenario, so that the Kimi large language model can correctly choose which functions to use
    			"parameters": { # Use the parameters field to define the parameters accepted by the function
    				"type": "object", # Fixed use type: object to make the Kimi large language model generate a JSON Object parameter
    				"required": ["url"], # Use the required field to tell the Kimi large language model which parameters are required
    				"properties": { # The specific parameter definitions are in properties, and you can define multiple parameters
    					"url": { # Here, the key is the parameter name, and the value is the specific definition of the parameter
    						"type": "string", # Use type to define the parameter type
    						"description": """
    							The website address (URL) of the content to be obtained, which can usually be obtained from the search results.
    						""" # Use description to describe the parameter so that the Kimi large language model can better generate the parameter
    					}
    				}
    			}
    		}
    	}
    ]


    def search_impl(query: str) -> List[Dict[str, Any]]:
        """
        search_impl uses a search engine to search for query. Most mainstream search engines (such as Bing) provide API calls. You can choose
        your preferred search engine API and place the website title, link, and brief introduction information from the return results in a dict to return.

        This is just a simple example, and you may need to write some authentication, validation, and parsing code.
        """
        r = httpx.get("https://your.search.api", params={"query": query})
        return r.json()


    def search(arguments: Dict[str, Any]) -> Any:
        query = arguments["query"]
        result = search_impl(query)
        return {"result": result}


    def crawl_impl(url: str) -> str:
        """
        crawl_url gets the content of a webpage based on the url.

        This is just a simple example. In actual web scraping, you may need to write more code to handle complex situations, such as asynchronously loaded data; and after obtaining
        the webpage content, you can clean the webpage content according to your needs, such as retaining only the text or removing unnecessary content (such as advertisements).
        """
        r = httpx.get(url)
        return r.text


    def crawl(arguments: dict) -> str:
        url = arguments["url"]
        content = crawl_impl(url)
        return {"content": content}


    # Map each tool name and its corresponding function through tool_map so that when the Kimi large language model returns tool_calls, we can quickly find the function to execute
    tool_map = {
        "search": search,
        "crawl": crawl,
    }

    messages = [
        {"role": "system",
         "content": "You are Kimi, an artificial intelligence assistant provided by Moonshot AI. You are better at conversing in Chinese and English. You provide users with safe, helpful, and accurate answers. At the same time, you will refuse to answer any questions involving terrorism, racial discrimination, pornography, and violence. Moonshot AI is a proper noun and should not be translated into other languages."},
        {"role": "user", "content": "Please search for Context Caching online and tell me what it is."}  # Request Kimi large language model to perform an online search in the question
    ]

    finish_reason = None


    # Our basic process is to ask the Kimi large language model questions with the user's question and tools. If the Kimi large language model returns finish_reason: tool_calls, we execute the corresponding tool_calls,
    # and submit the execution results in the form of a message with role=tool back to the Kimi large language model. The Kimi large language model then generates the next content based on the tool_calls results:
    #
    #   1. If the Kimi large language model believes that the current tool call results can answer the user's question, it returns finish_reason: stop, and we exit the loop and print out message.content;
    #   2. If the Kimi large language model believes that the current tool call results cannot answer the user's question and needs to call the tool again, we continue to execute the next tool_calls in the loop until finish_reason is no longer tool_calls;
    #
    # During this process, we only return the result to the user when finish_reason is stop.

    while finish_reason is None or finish_reason == "tool_calls":
        completion = client.chat.completions.create(
            model="kimi-k3",
            messages=messages,
            tools=tools,  # <-- We submit the defined tools to the Kimi large language model through the tools parameter
        )
        choice = completion.choices[0]
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls": # <-- Determine whether the current return content contains tool_calls
            messages.append(choice.message) # <-- We add the assistant message returned to us by the Kimi large language model to the context so that the Kimi large language model can understand our request next time
            for tool_call in choice.message.tool_calls: # <-- tool_calls may be multiple, so we use a loop to execute them one by one
                tool_call_name = tool_call.function.name
                tool_call_arguments = json.loads(tool_call.function.arguments) # <-- arguments is a serialized JSON Object, and we need to deserialize it with json.loads
                tool_function = tool_map[tool_call_name] # <-- Quickly find which function to execute through tool_map
                tool_result = tool_function(tool_call_arguments)

                # Construct a message with role=tool using the function execution result to show the result of the tool call to the model;
                # Note that we need to provide the tool_call_id and name fields in the message so that the Kimi large language model
                # can correctly match the corresponding tool_call.
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result), # <-- We agree to submit the tool call result to the Kimi large language model in string format, so we use json.dumps to serialize the execution result into a string here
                })

    print(choice.message.content) # <-- Here, we return the reply generated by the model to the user
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const axios = require('axios');
    const openai = require('openai'); // You need to install the openai library

    const client = new openai.OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY, // Set the MOONSHOT_API_KEY environment variable before running this example
        baseURL: "https://api.moonshot.ai/v1",
    });

    const tools = [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search for content on the internet using a search engine.\n\nUse this tool when your knowledge can't answer the user's question or when the user asks you to search online. Extract the content the user wants to search for from the conversation and use it as the value for the query parameter.\nThe search results include the website title, URL, and a brief description.",
                "parameters": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The content the user wants to search for, extracted from the user's question or chat context."
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "crawl",
                "description": "Retrieve web page content based on a website URL.",
                "parameters": {
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the website whose content you want to retrieve, usually obtained from search results."
                        }
                    }
                }
            }
        }
    ];

    async function searchImpl(query) {
        const response = await axios.get("https://your.search.api", { params: { query } });
        return response.data;
    }

    async function search(args) {
        const query = args.query;
        const result = await searchImpl(query);
        return { "result": result };
    }

    async function crawlImpl(url) {
        const response = await axios.get(url);
        return response.data;
    }

    async function crawl(args) {
        const url = args.url;
        const content = await crawlImpl(url);
        return { "content": content };
    }

    const toolMap = {
        "search": search,
        "crawl": crawl,
    };

    const messages = [
        { "role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are proficient in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You will refuse to answer any questions involving terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated into other languages." },
        { "role": "user", "content": "Please search the internet for Context Caching and tell me what it is." }  // The user is asking Kimi to search online
    ];

    let finishReason = null;
    let choice;

    async function main() {
        while (finishReason === null || finishReason === "tool_calls") {
            const completion = await client.chat.completions.create({
                model: "kimi-k3",
                messages: messages,
                tools: tools,  // <-- We pass the defined tools to the Kimi large language model via the tools parameter
            });
            choice = completion.choices[0];
            finishReason = choice.finish_reason;
            if (finishReason === "tool_calls") { // <-- Check if the current response includes tool_calls
                messages.push(choice.message); // <-- Add the assistant message from Kimi to the context for the next request
                for (const toolCall of choice.message.tool_calls) { // <-- There might be multiple tool_calls, so we loop through each one
                    const toolCallName = toolCall.function.name;
                    const toolCallArguments = JSON.parse(toolCall.function.arguments); // <-- The arguments are a serialized JSON object, so we need to parse them
                    const toolFunction = toolMap[toolCallName]; // <-- Use tool_map to quickly find which function to execute
                    const toolResult = await toolFunction(toolCallArguments);

                    // Construct a role=tool message with the function execution result to show the model the outcome of the tool call;
                    // Note that we need to provide the tool_call_id and name fields in the message so that Kimi can correctly match the tool_call.
                    messages.push({
                        "role": "tool",
                        "tool_call_id": toolCall.id,
                        "name": toolCallName,
                        "content": JSON.stringify(toolResult), // <-- We agreed to submit the tool call result as a string, so we serialize it with JSON.stringify
                    });
                }
            }
        }
        console.log(choice.message.content); // <-- Finally, we return the model's response to the user
    }

    main();
    ```
  </Tab>
</Tabs>

We use a `while` loop to execute the code logic that includes tool calls because the Kimi large language model typically doesn't make just one tool call, especially in the context of online searching. Usually, Kimi will first call the `search` tool to get search results, and then call the `crawl` tool to convert the URLs in the search results into actual web page content. The overall structure of the `messages` is as follows:

```text theme={null}
system: prompt                                                                                               # System prompt
user: prompt                                                                                                 # User's question
assistant: tool_call(name=search, arguments={query: query})                                                  # Kimi returns a tool_call (single)
tool: search_result(tool_call_id=tool_call.id, name=search)                                                  # Submit the tool_call execution result
assistant: tool_call_1(name=crawl, arguments={url: url_1}), tool_call_2(name=crawl, arguments={url: url_2})  # Kimi continues to return tool_calls (multiple)
tool: crawl_content(tool_call_id=tool_call_1.id, name=crawl)                                                 # Submit the execution result of tool_call_1
tool: crawl_content(tool_call_id=tool_call_2.id, name=crawl)                                                 # Submit the execution result of tool_call_2
assistant: message_content(finish_reason=stop)                                                               # Kimi generates a reply to the user, ending the conversation
```

This completes the entire process of making "online query" tool calls. If you have implemented your own `search` and `crawl` methods, when you ask Kimi to search online, it will call the `search` and `crawl` tools and give you the correct response based on the tool call results.

## Handle tool\_calls in Streaming Output

In streaming output mode (`stream`), `tool_calls` work as well, but there are a few extra things to note:

* During streaming output, since `finish_reason` will appear in the last data chunk, it is recommended to check if the `delta.tool_calls` field exists to determine if the current response includes a tool call;
* During streaming output, `delta.content` will be output first, followed by `delta.tool_calls`, so you must wait until `delta.content` has finished outputting before you can determine and identify `tool_calls`;
* During streaming output, we will specify the `tool_call.id` and `tool_call.function.name` in the initial data chunk, and only `tool_call.function.arguments` will be output in subsequent chunks;
* During streaming output, if Kimi returns multiple `tool_calls` at once, we will use an additional field called `index` to indicate the index of the current `tool_call`, so that you can correctly concatenate the `tool_call.function.arguments` parameters. We use a code example from the streaming output section (without using the SDK) to illustrate how to do this:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    import json
    import httpx  # We use the httpx library to make our HTTP requests



    tools = [
        {
            "type": "function",  # The type field is fixed as "function"
            "function": {  # When type is "function", use the function field to define the specific function content
                "name": "search",  # The name of the function, please use English letters, numbers, hyphens, and underscores
                "description": """ 
    				Search the internet for content using a search engine.

    				When your knowledge cannot answer the user's question or the user requests an online search, call this tool. Extract the content the user wants to search from the conversation as the value of the query parameter.
    				The search results include the title of the website, the website's address (URL), and a brief introduction to the website.
    			""",  # Description of the function, explaining its specific role and usage scenarios to help the Kimi large language model choose the right functions
                "parameters": {  # Use the parameters field to define the parameters the function accepts
                    "type": "object",  # Always use type: object to make the Kimi large language model generate a JSON Object parameter
                    "required": ["query"],  # Use the required field to tell the Kimi large language model which parameters are mandatory
                    "properties": {  # Specific parameter definitions in properties, you can define multiple parameters
                        "query": {  # Here, the key is the parameter name, and the value is the specific definition of the parameter
                            "type": "string",  # Use type to define the parameter type
                            "description": """
    							The content the user wants to search for, extracted from the user's question or chat context.
    						"""  # Use description to help the Kimi large language model generate parameters more effectively
                        }
                    }
                }
            }
        },
    ]

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('MOONSHOT_API_KEY')}",
    }

    data = {
        "model": "kimi-k3",
        "messages": [
            {"role": "user", "content": "Please search for Context Caching technology online."}
        ],
        "stream": True,
        "tools": tools,  # <-- Add tool invocation
    }
    # Use httpx to send a chat request to the Kimi large language model and get the response r
    r = httpx.post("https://api.moonshot.ai/v1/chat/completions",
                   headers=header,
                   json=data)
    if r.status_code != 200:
        raise Exception(r.text)

    data: str

    # Here, we pre-build a List to store different response messages. Since we set n=2, we initialize the List with 2 elements
    messages = [{}, {}]

    # Here, we use the iter_lines method to read the response body line by line
    for line in r.iter_lines():
        # Remove leading and trailing spaces from each line to better handle data blocks
        line = line.strip()

        # Next, we need to handle three different cases:
        #   1. If the current line is empty, it indicates that the previous data block has been received (as mentioned earlier, data blocks are ended with two newline characters). We can deserialize the data block and print the corresponding content;
        #   2. If the current line is not empty and starts with data:, it indicates the start of a data block transmission. After removing the data: prefix, first check if it is the end marker [DONE]. If not, save the data content to the data variable;
        #   3. If the current line is not empty but does not start with data:, it means the current line still belongs to the previous data block being transmitted. Append the content of the current line to the end of the data variable;

        if len(line) == 0:
            chunk = json.loads(data)

            # Loop through all choices in each data block to get the message object corresponding to the index
            for choice in chunk["choices"]:
                index = choice["index"]
                message = messages[index]
                usage = choice.get("usage")
                if usage:
                    message["usage"] = usage
                delta = choice["delta"]
                role = delta.get("role")
                if role:
                    message["role"] = role
                content = delta.get("content")
                if content:
                    if "content" not in message:
                        message["content"] = content
                    else:
                        message["content"] = message["content"] + content

                # From here, we start processing tool_calls
                tool_calls = delta.get("tool_calls")  # <-- First, check if the data block contains tool_calls
                if tool_calls:
                    if "tool_calls" not in message:
                        message["tool_calls"] = []  # <-- If it contains tool_calls, initialize a list to store these tool_calls. Note that the list is empty at this point, with a length of 0
                    for tool_call in tool_calls:
                        tool_call_index = tool_call["index"]  # <-- Get the index of the current tool_call
                        if len(message["tool_calls"]) < (
                                tool_call_index + 1):  # <-- Expand the tool_calls list according to the index to access the corresponding tool_call via index
                            message["tool_calls"].extend([{}] * (tool_call_index + 1 - len(message["tool_calls"])))
                        tool_call_object = message["tool_calls"][tool_call_index]  # <-- Access the corresponding tool_call via index
                        tool_call_object["index"] = tool_call_index

                        # The following steps fill in the id, type, and function fields of each tool_call based on the information in the data block
                        # In the function field, there are name and arguments fields. The arguments field will be supplemented by each data block
                        # in the same way as the delta.content field.

                        tool_call_id = tool_call.get("id")
                        if tool_call_id:
                            tool_call_object["id"] = tool_call_id
                        tool_call_type = tool_call.get("type")
                        if tool_call_type:
                            tool_call_object["type"] = tool_call_type
                        tool_call_function = tool_call.get("function")
                        if tool_call_function:
                            if "function" not in tool_call_object:
                                tool_call_object["function"] = {}
                            tool_call_function_name = tool_call_function.get("name")
                            if tool_call_function_name:
                                tool_call_object["function"]["name"] = tool_call_function_name
                            tool_call_function_arguments = tool_call_function.get("arguments")
                            if tool_call_function_arguments:
                                if "arguments" not in tool_call_object["function"]:
                                    tool_call_object["function"]["arguments"] = tool_call_function_arguments
                                else:
                                    tool_call_object["function"]["arguments"] = tool_call_object["function"][
                                                                                "arguments"] + tool_call_function_arguments  # <-- Supplement the value of the function.arguments field sequentially
                        message["tool_calls"][tool_call_index] = tool_call_object

                data = ""  # Reset data
        elif line.startswith("data: "):
            data = line[len("data: "):]

            # When the data block content is [DONE], it indicates that all data blocks have been sent and the network connection can be disconnected
            if data == "[DONE]":
                break
        else:
            data = data + "\n" + line  # When appending content, add a newline character because this might be intentional line breaks in the data block

    # After assembling all messages, print their contents separately
    for index, message in enumerate(messages):
        print("index:", index)
        print("message:", json.dumps(message, ensure_ascii=False))
        print("")
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const os = require('os');
    const axios = require('axios');// Use the axios library to perform HTTP requests
     
    const tools = [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search the internet for content using a search engine.\n\nWhen your knowledge cannot answer the user's question or the user requests an online search, call this tool. Extract the content the user wants to search from the conversation as the value of the query parameter.\nThe search results include the title of the website, the website's address (URL), and a brief introduction to the website.",
                "parameters": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The content the user wants to search for, extracted from the user's question or chat context."
                        }
                    }
                }
            }
        },
    ];
     
    const header = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${process.env.MOONSHOT_API_KEY}`
    };

    const data = {
        "model": "kimi-k3",
        "messages": [
            {"role": "user", "content": "Please search for Context Caching technology online."}
        ],
        "stream": true,
        "tools": tools,
        "tool_choice": "auto"
    };

    axios.post("https://api.moonshot.ai/v1/chat/completions", 
        data, {
        headers: header,
        responseType: 'stream'   
    }).then(response => {
        if (response.status !== 200) {
            throw new Error(response.text);
        }

        let data = "";
        let messages = [{}, {}];

        response.data.on('data', chunk => {
            let line = chunk.toString().trim();

            if (line === "") {
                let chunk = JSON.parse(data);

                for (let choice of chunk.choices) {
                    let index = choice.index;
                    let message = messages[index];
                    let usage = choice.usage;
                    if (usage) message.usage = usage;
                    let delta = choice.delta;
                    let role = delta.role;
                    if (role) message.role = role;
                    let content = delta.content;
                    if (content) message.content = (message.content || "") + content;

                    let tool_calls = delta.tool_calls;
                    if (tool_calls) {
                        if (!message.tool_calls) message.tool_calls = [];
                        for (let tool_call of tool_calls) {
                            let tool_call_index = tool_call.index;
                            while (message.tool_calls.length < tool_call_index + 1) {
                                message.tool_calls.push({});
                            }
                            let tool_call_object = message.tool_calls[tool_call_index];
                            tool_call_object.index = tool_call_index;

                            let tool_call_id = tool_call.id;
                            if (tool_call_id) tool_call_object.id = tool_call_id;
                            let tool_call_type = tool_call.type;
                            if (tool_call_type) tool_call_object.type = tool_call_type;
                            let tool_call_function = tool_call.function;
                            if (tool_call_function) {
                                if (!tool_call_object.function) tool_call_object.function = {};
                                let tool_call_function_name = tool_call_function.name;
                                if (tool_call_function_name) tool_call_object.function.name = tool_call_function_name;
                                let tool_call_function_arguments = tool_call_function.arguments;
                                if (tool_call_function_arguments) {
                                    if (!tool_call_object.function.arguments) {
                                        tool_call_object.function.arguments = tool_call_function_arguments;
                                    } else {
                                        tool_call_object.function.arguments = tool_call_object.function.arguments + tool_call_function_arguments;
                                    }
                                }
                            }
                            message.tool_calls[tool_call_index] = tool_call_object;
                        }
                    }
                }
                data = ""; // Reset data
            } else if (line.startsWith("data: ")) {
                data = line.substring(6);
            } else {
                data = data + "\n" + line;
            }
        });

        response.data.on('end', () => {
            for (let index = 0; index < messages.length; index++) {
                console.log("index:", index);
                console.log("message:", JSON.stringify(messages[index], null, 4));
                console.log("");
            }
        });
    }).catch(error => {
        console.error("Request failed:", error);
    });
    ```
  </Tab>
</Tabs>

Below is an example of handling `tool_calls` in streaming output using the openai SDK:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    import json

    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        base_url="https://api.moonshot.ai/v1",
    )

    tools = [
        {
            "type": "function",  # The agreed-upon field type, currently supports function as a value
            "function": {  # When type is function, use the function field to define the specific function content
                "name": "search",  # The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
                "description": """ 
    				Search for content on the internet using a search engine.

    				When your knowledge cannot answer the user's question, or the user requests you to perform an online search, call this tool. Please extract the content the user wants to search from the conversation with the user as the value of the query parameter.
    				The search results include the title of the website, the website's address (URL), and the website's description.
    			""",  # The introduction of the function, write the specific function here and its usage scenarios so that the Kimi large language model can correctly choose which functions to use
                "parameters": {  # Use the parameters field to define the parameters accepted by the function
                    "type": "object",  # Fixed use type: object to make the Kimi large language model generate a JSON Object parameter
                    "required": ["query"],  # Use the required field to tell the Kimi large language model which parameters are required
                    "properties": {  # The properties are the specific parameter definitions, you can define multiple parameters
                        "query": {  # Here, the key is the parameter name, and the value is the specific definition of the parameter
                            "type": "string",  # Use type to define the parameter type
                            "description": """
    							The content the user is searching for, please extract it from the user's question or chat context.
    						"""  # Use description to describe the parameter so that the Kimi large language model can better generate the parameter
                        }
                    }
                }
            }
        },
    ]

    completion = client.chat.completions.create(
        model="kimi-k3",
        messages=[
            {"role": "user", "content": "Please search for Context Caching technology online."}
        ],
        stream=True,
        tools=tools,  # <-- Add tool invocation
    )

    # Here, we pre-build a List to store different response messages, since we set n=2, we initialize the List with 2 elements
    messages = [{}, {}]

    for chunk in completion:
        # Loop through all the choices in each data chunk and get the message object corresponding to the index
        for choice in chunk.choices:
            index = choice.index
            message = messages[index]
            delta = choice.delta
            role = delta.role
            if role:
                message["role"] = role
            content = delta.content
            if content:
                if "content" not in message:
                    message["content"] = content
                else:
                    message["content"] = message["content"] + content

            # From here, we start processing tool_calls
            tool_calls = delta.tool_calls  # <-- First check if the data chunk contains tool_calls
            if tool_calls:
                if "tool_calls" not in message:
                    message["tool_calls"] = []  # <-- If it contains tool_calls, we initialize a list to save these tool_calls, note that the list is empty at this time with a length of 0
                for tool_call in tool_calls:
                    tool_call_index = tool_call.index  # <-- Get the index of the current tool_call
                    if len(message["tool_calls"]) < (
                            tool_call_index + 1):  # <-- Expand the tool_calls list according to the index so that we can access the corresponding tool_call via the subscript
                        message["tool_calls"].extend([{}] * (tool_call_index + 1 - len(message["tool_calls"])))
                    tool_call_object = message["tool_calls"][tool_call_index]  # <-- Access the corresponding tool_call via the subscript
                    tool_call_object["index"] = tool_call_index

                    # The following steps are to fill in the id, type, and function fields of each tool_call based on the information in the data chunk
                    # In the function field, there are name and arguments fields, the arguments field will be supplemented by each data chunk
                    # Sequentially, just like the delta.content field.

                    tool_call_id = tool_call.id
                    if tool_call_id:
                        tool_call_object["id"] = tool_call_id
                    tool_call_type = tool_call.type
                    if tool_call_type:
                        tool_call_object["type"] = tool_call_type
                    tool_call_function = tool_call.function
                    if tool_call_function:
                        if "function" not in tool_call_object:
                            tool_call_object["function"] = {}
                        tool_call_function_name = tool_call_function.name
                        if tool_call_function_name:
                            tool_call_object["function"]["name"] = tool_call_function_name
                        tool_call_function_arguments = tool_call_function.arguments
                        if tool_call_function_arguments:
                            if "arguments" not in tool_call_object["function"]:
                                tool_call_object["function"]["arguments"] = tool_call_function_arguments
                            else:
                                tool_call_object["function"]["arguments"] = tool_call_object["function"][
                                                                                "arguments"] + tool_call_function_arguments  # <-- Sequentially supplement the value of the function.arguments field
                    message["tool_calls"][tool_call_index] = tool_call_object

    # After assembling all messages, we print their contents separately
    for index, message in enumerate(messages):
        print("index:", index)
        print("message:", json.dumps(message, ensure_ascii=False))
        print("")
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const os = require('os');
    const openai = require('openai'); // Need to install the openai library

    const client = new openai.OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: "https://api.moonshot.ai/v1"
    });

    const tools = [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search for content on the internet using a search engine.\n\nCall this tool when your knowledge cannot answer the user's question, or when the user requests an online search. Extract the content the user wants to search for from the conversation and use it as the value of the query parameter.\nThe search results include the website title, address (URL), and a brief description of the website.",
                "parameters": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The content the user wants to search for, extracted from the user's question or chat context."
                        }
                    }
                }
            }
        },
    ];

    async function main() {
        const response = await client.chat.completions.create({
            model: "kimi-k3",
            messages: [
                { "role": "user", "content": "Please search for Context Caching technology online." }
            ],
            stream: true,
            tools: tools,
            tool_choice: "auto"
        });

        let messages = [{}, {}];
        let data = '';

        for await (const chunk of response) {
             for (const choice of chunk.choices) {
                const index = choice.index;
                const message = messages[index];
                const delta = choice.delta;
                const role = delta.role;
                if (role) message.role = role;
                const content = delta.content;
                if (content) message.content = (message.content || "") + content;

                const tool_calls = delta.tool_calls;
                if (tool_calls) {
                    if (!message.tool_calls) message.tool_calls = [];
                    for (const tool_call of tool_calls) {
                        const tool_call_index = tool_call.index;
                        if (message.tool_calls.length < tool_call_index + 1) {
                            for (let i = message.tool_calls.length; i < tool_call_index + 1; i++) {
                                message.tool_calls.push({});
                            }
                        }
                        const tool_call_object = message.tool_calls[tool_call_index];
                        tool_call_object.index = tool_call_index;

                        const tool_call_id = tool_call.id;
                        if (tool_call_id) tool_call_object.id = tool_call_id;
                        const tool_call_type = tool_call.type;
                        if (tool_call_type) tool_call_object.type = tool_call_type;
                        const tool_call_function = tool_call.function;
                        if (tool_call_function) {
                            if (!tool_call_object.function) tool_call_object.function = {};
                            const tool_call_function_name = tool_call_function.name;
                            if (tool_call_function_name) tool_call_object.function.name = tool_call_function_name;
                            const tool_call_function_arguments = tool_call_function.arguments;
                            if (tool_call_function_arguments) {
                                if (!tool_call_object.function.arguments) {
                                    tool_call_object.function.arguments = tool_call_function_arguments;
                                } else {
                                    tool_call_object.function.arguments += tool_call_function_arguments;
                                }
                            }
                        }
                        message.tool_calls[tool_call_index] = tool_call_object;
                    }
                }
            }
        }

        for (let index = 0; index < messages.length; index++) {
            console.log("index:", index);
            console.log("message:", JSON.stringify(messages[index], null, 2));
            console.log("");
        }
    }

    main().catch(console.error);
    ```
  </Tab>
</Tabs>

## Use tool\_calls Instead of function\_call

`tool_calls` evolved from function calls (`function_call`), and `function_call` is a subset of `tool_calls` — in certain contexts, or when reading compatibility code, you can treat the two as equivalent. Since OpenAI has marked `function_call` and related parameters (such as `functions`) as "deprecated", our API will no longer support `function_call`; use `tool_calls` instead. Compared to `function_call`, `tool_calls` has the following advantages:

* It supports parallel calls. The Kimi large language model can return multiple `tool_calls` at once. You can use concurrency in your code to call these `tool_call` simultaneously, reducing time consumption;
* For `tool_calls` that have no dependencies, the Kimi large language model will also tend to call them in parallel. Compared to the original sequential calls of `function_call`, this reduces token consumption to some extent;

## Notes

* When `finish_reason=tool_calls`, `message.content` is occasionally not empty: it is usually the Kimi large language model explaining which tools it needs to call and why. If your tool call process takes a long time, or a single turn requires several sequential tool calls, this descriptive message can reduce the anxiety or dissatisfaction users feel while waiting, and helps them understand the tool call flow and intervene and correct in time (for example, terminating an incorrect tool call, or correcting the model's tool selection with a prompt in the next turn);
* The content in the `tools` parameter is also counted in the total Tokens. Please ensure that the total number of Tokens in `tools` and `messages` does not exceed the model's context window size.

### Keep Every tool\_call Matched to a tool Message

In tool call scenarios, messages are no longer a simple alternation of `system` / `user` / `assistant`:

```text theme={null}
system: ...
user: ...
assistant: ...
user: ...
assistant: ...
```

Instead, they look like this:

```text theme={null}
system: ...
user: ...
assistant: ...
tool: ...
tool: ...
assistant: ...
```

When the Kimi large language model generates `tool_calls`, make sure every `tool_call` has a corresponding message with `role=tool`, and that this message carries the correct `tool_call_id`: if the number of `role=tool` messages does not match the number of `tool_calls`, an error will occur; likewise, if the `tool_call_id` in a `role=tool` message cannot be matched with the `tool_call.id` in `tool_calls`, an error will occur.

### Troubleshoot the tool\_call\_id not found Error

If you encounter the `tool_call_id not found` error, it may be because you did not add the `role=assistant` message returned by the Kimi API to the messages list. The correct message sequence should look like this:

```text theme={null}
system: ...
user: ...
assistant: ...  # <-- Perhaps you did not add this assistant message to the messages list
tool: ...
tool: ...
assistant: ...
```

You can avoid the `tool_call_id not found` error by executing `messages.append(message)` each time you receive a return value from the Kimi API, to add the message returned by the Kimi API to the messages list.

*Note: Assistant messages added to the messages list before the `role=tool` message must fully include the `tool_calls` field and its values returned by the Kimi API. We recommend directly adding the `choice.message` returned by the Kimi API to the messages list "as is" to avoid potential errors.*
