> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Set Parameters for Multi-turn Chat

> Maintain message history, control context length, and construct multi-turn conversations with the stateless Kimi API.

Unlike the Kimi intelligent assistant, the Kimi API is **stateless** and has no memory of its own: across multiple requests, the model doesn't know what you asked in a previous request and won't remember any context—if you tell it you are 27 years old in one request, it won't know that in the next. To enable multi-turn conversations, manually maintain the context for each request by sending the conversation history along with the next request, so the model can see what has been discussed before.

<Note>
  The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
</Note>

## Give the model memory with the messages list

The following example modifies the one from the previous chapter to show how maintaining a `messages` list gives the model memory: each turn appends both the user's new message (role=user) and the model's reply (role=assistant) to the list, then sends the whole list with the request. The key points are annotated as comments in the code:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    from openai import OpenAI

    client = OpenAI(
        api_key = os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url = "https://api.moonshot.ai/v1",
    )

    # We define a global variable messages to keep track of the historical conversation messages between us and the Kimi large language model
    # The messages include both the questions we ask the Kimi large language model (role=user) and the replies it gives us (role=assistant)
    # Of course, it also includes the initial System Prompt (role=system)
    # The messages in the list are arranged in chronological order
    messages = [
        {"role": "system", "content": "You are Kimi, an artificial intelligence assistant provided by Moonshot AI. You are better at conversing in Chinese and English. You provide users with safe, helpful, and accurate answers. At the same time, you refuse to answer any questions involving terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages."},
    ]

    def chat(input: str) -> str:
        """
        The chat function supports multi-turn conversations. Each time the chat function is called to converse with the Kimi large language model, the model will 'see' the historical conversation messages that have already been generated. In other words, the Kimi large language model has a memory.
        """

        global messages

        # We construct the user's latest question as a message (role=user) and add it to the end of the messages list
        messages.append({
            "role": "user",
            "content": input,	
        })

        # We converse with the Kimi large language model, carrying the messages along
        completion = client.chat.completions.create(
            model="kimi-k3",
            messages=messages
        )

        # Through the API, we receive the reply message (role=assistant) from the Kimi large language model
        assistant_message = completion.choices[0].message

        # To give the Kimi large language model a complete memory, we must also add the message it returns to us to the messages list
        messages.append(assistant_message)

        return assistant_message.content

    print(chat("Hello, I am 27 years old this year."))
    print(chat("Do you know how old I am this year?")) # Here, based on the previous context, the Kimi large language model will know that you are 27 years old
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const OpenAI = require("openai")

    const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY, // Set the MOONSHOT_API_KEY environment variable before running this example
      baseURL: "https://api.moonshot.ai/v1",
    });

    // We define a global variable messages to keep track of the historical conversation messages between us and the Kimi large language model
    // The messages include both the questions we ask the Kimi large language model (role=user) and the replies it gives us (role=assistant)
    // Of course, it also includes the initial System Prompt (role=system)
    // The messages in the list are arranged in chronological order
    let messages = [
      {
        role: "system",
        content: "You are Kimi, an artificial intelligence assistant provided by Moonshot AI. You are better at conversing in Chinese and English. You provide users with safe, helpful, and accurate answers. At the same time, you refuse to answer any questions involving terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages.",
      },
    ];

    async function chat(input) {
      /**
       * The chat function supports multi-turn conversations. Each time the chat function is called to converse with the Kimi large language model, the model will 'see' the historical conversation messages that have already been generated. In other words, the Kimi large language model has a memory.
       */

      // We construct the user's latest question as a message (role=user) and add it to the end of the messages list
      messages.push({
        role: "user",
        content: input,
      });

      // We converse with the Kimi large language model, carrying the messages along
      const completion = await client.chat.completions.create({
        model: "kimi-k3",
        messages: messages
      });

      // Through the API, we receive the reply message (role=assistant) from the Kimi large language model
      const assistantMessage = completion.choices[0].message;

      // To give the Kimi large language model a complete memory, we must also add the message it returns to us to the messages list
      messages.push(assistantMessage);

      return assistantMessage.content;
    }

    // Example usage
    (async () => {
      console.log(await chat("Hello, I am 27 years old this year."));
      console.log(await chat("Do you know how old I am this year?")); // Here, based on the previous context, the Kimi large language model will know that you are 27 years old
    })();
    ```
  </Tab>
</Tabs>

Key points:

* The Kimi API has no built-in context memory; use the `messages` parameter to manually tell the model what has been discussed before;
* The `messages` list must store both the user's questions (role=user) and the model's replies (role=assistant).

## Truncate history to control context length

As the number of `chat` calls grows, the `messages` list keeps getting longer, so each request consumes more Tokens—eventually the messages in the list will exceed the context window supported by the model. Use a strategy to keep the `messages` list within a manageable range, for example by keeping only the latest 20 messages as the context for each request.

The following example shows how the `make_messages` function controls the number of messages in each request (keeping the latest 20 by default)—note how it ensures the System Messages remain in the list even when truncating:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    from openai import OpenAI 
     
    client = OpenAI(
        api_key = os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url = "https://api.moonshot.ai/v1",
    )

    # We place the System Messages in a separate list because every request should carry the System Messages.
    system_messages = [
    	{"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are more proficient in conversing in Chinese and English. You provide users with safe, helpful, and accurate responses. You also reject any questions involving terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages."},
    ]

    # We define a global variable messages to record the historical conversation messages between us and the Kimi large language model.
    # The messages include both the questions we pose to the Kimi large language model (role=user) and the replies from the Kimi large language model (role=assistant).
    # The messages are arranged in chronological order.
    messages = []


    def make_messages(input: str, n: int = 20) -> list[dict]:
    	"""
    	The make_messages function controls the number of messages in each request to keep it within a reasonable range, such as the default value of 20. When building the message list, we first add the System Prompt because it is essential no matter how the messages are truncated. Then, we obtain the latest n messages from the historical records as the messages for the request. In most scenarios, this ensures that the number of Tokens occupied by the request messages does not exceed the model's context window.
    	"""
    	global messages
    	
    	# First, we construct the user's latest question into a message (role=user) and add it to the end of the messages list.
    	messages.append({
    		"role": "user",
    		"content": input,	
    	})

    	# new_messages is the list of messages we will use for the next request. Let's build it now.
    	new_messages = []

    	# Every request must carry the System Messages, so we need to add the system_messages to the message list first.
    	# Note that even if the messages are truncated, the System Messages should still be in the messages list.
    	new_messages.extend(system_messages)

    	# Here, when the historical messages exceed n, we only keep the latest n messages.
    	if len(messages) > n:
    		messages = messages[-n:]

    	new_messages.extend(messages)
    	return new_messages


    def chat(input: str) -> str:
    	"""
    	The chat function supports multi-turn conversations. Each time the chat function is called to converse with the Kimi large language model, the model can "see" the historical conversation messages that have already been generated. In other words, the Kimi large language model has memory.
    	"""

    	# We converse with the Kimi large language model carrying the messages.
    	completion = client.chat.completions.create(
            model="kimi-k3",
            messages=make_messages(input)
        )
     
    	# Through the API, we obtain the reply message from the Kimi large language model (role=assistant).
    	assistant_message = completion.choices[0].message
     
    	# To ensure the Kimi large language model has a complete memory, we must add the message returned by the model to the messages list.
    	messages.append(assistant_message)
     
    	return assistant_message.content

    print(chat("Hello, I am 27 years old this year."))
    print(chat("Do you know how old I am this year?")) # Here, based on the previous context, the Kimi large language model will know that you are 27 years old this year.
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const OpenAI = require("openai")

    const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY, // Set the MOONSHOT_API_KEY environment variable before running this example
      baseURL: "https://api.moonshot.ai/v1",
    });

    // We place the System Messages in a separate list because every request should carry the System Messages.
    const systemMessages = [
      {
        role: "system",
        content: "You are Kimi, an AI assistant provided by Moonshot AI. You are more proficient in conversing in Chinese and English. You provide users with safe, helpful, and accurate responses. You also reject any questions involving terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages.",
      },
    ];

    // We define a global variable messages to record the historical conversation messages between us and the Kimi large language model.
    // The messages include both the questions we pose to the Kimi large language model (role=user) and the replies from the Kimi large language model (role=assistant).
    // The messages are arranged in chronological order.
    let messages = [];

    async function makeMessages(input, n = 20) {
      /**
       * The makeMessages function controls the number of messages in each request to keep it within a reasonable range, such as the default value of 20. When building the message list, we first add the System Prompt because it is essential no matter how the messages are truncated. Then, we obtain the latest n messages from the historical records as the messages for the request. In most scenarios, this ensures that the number of Tokens occupied by the request messages does not exceed the model's context window.
       */
      // First, we construct the user's latest question into a message (role=user) and add it to the end of the messages list.
      messages.push({
        role: "user",
        content: input,
      });

      // newMessages is the list of messages we will use for the next request. Let's build it now.
      let newMessages = [];

      // Every request must carry the System Messages, so we need to add the systemMessages to the message list first.
      // Note that even if the messages are truncated, the System Messages should still be in the messages list.
      newMessages = systemMessages.concat(newMessages);

      // Here, when the historical messages exceed n, we only keep the latest n messages.
      if (messages.length > n) {
        messages = messages.slice(-n);
      }

      newMessages = newMessages.concat(messages);
      return newMessages;
    }

    async function chat(input) {
      /**
       * The chat function supports multi-turn conversations. Each time the chat function is called to converse with the Kimi large language model, the model can "see" the historical conversation messages that have already been generated. In other words, the Kimi large language model has memory.
       */

      // We converse with the Kimi large language model carrying the messages.
      const completion = await client.chat.completions.create({
        model: "kimi-k3",
        messages: await makeMessages(input)
      });

      // Through the API, we obtain the reply message from the Kimi large language model (role=assistant).
      const assistantMessage = completion.choices[0].message;

      // To ensure the Kimi large language model has a complete memory, we must add the message returned by the model to the messages list.
      messages.push(assistantMessage);

      return assistantMessage.content;
    }

    (async () => {
      console.log(await chat("Hello, I am 27 years old this year."));
      console.log(await chat("Do you know how old I am this year?")); // Here, based on the previous context, the Kimi large language model will know that you are 27 years old this year.
    })();
    ```
  </Tab>
</Tabs>

## What else to consider in production

The examples above only cover the simplest invocation scenario. In real business logic, you may need to handle more scenarios and edge cases:

* In concurrent scenarios, additional read-write locks may be needed;
* For multi-user scenarios, maintain a separate `messages` list for each user;
* Persist the `messages` list;
* Use a more precise way to determine how many messages to retain in the `messages` list;
* Summarize the discarded messages and add the summary as a new message to the `messages` list;
* ……
