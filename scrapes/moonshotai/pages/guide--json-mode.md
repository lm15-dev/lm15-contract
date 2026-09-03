> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use Kimi API's JSON Mode

> Enable Kimi API JSON Mode with `response_format` and safely prompt for, receive, and parse structured JSON output.

JSON Mode makes the Kimi large language model output a valid, correctly parsable JSON document. When you need structured output — for example, summarizing an article into structured data like this — enable it with the `response_format` parameter:

```json theme={null}
{
	"title": "Article Title",
	"author": "Article Author",
	"publish_time": "Publication Time",
	"summary": "Article Summary"
}
```

## Enable JSON Mode with response\_format

If you only tell the Kimi large language model in the prompt: "Please output content in JSON format," the model can understand your request and generate a JSON document as required. However, the generated content often has some flaws: for instance, in addition to the JSON document, Kimi might output extra text to explain the JSON document —

```text theme={null}
Here is the JSON document you requested

{
	"title": "Article Title",
	"author": "Article Author",
	"publish_time": "Publication Time",
	"summary": "Article Summary"
}
```

—or the JSON document might be malformed and cannot be parsed correctly (note the comma at the end of the `summary` field on the last line):

```text theme={null}
{
	"title": "Article Title",
	"author": "Article Author",
	"publish_time": "Publication Time",
	"summary": "Article Summary",
}
```

The `response_format` parameter constrains the output format. Its default value is `{"type": "text"}`, which means ordinary text content with no formatting constraints. Set `response_format` to `{"type": "json_object"}` to enable JSON Mode, and the Kimi large language model will output a valid, correctly parsable JSON document as required.

Using JSON Mode takes three steps:

1. Define the output JSON format in the system or user prompt, including specific field names and field types; **the best practice is to provide a concrete output example and explain the meaning of each field**;
2. Set the `response_format` parameter to `{"type": "json_object"}`;
3. Parse the `content` in the message returned by the Kimi large language model; `message.content` is a valid JSON Object serialized as a string.

## Full example: a customer-service bot with mixed message types

Imagine a WeChat intelligent robot customer service (referred to as intelligent customer service): it uses the Kimi large language model to answer customer questions, and can reply not only with text messages but also with images, link cards, voice messages, and other types of messages, mixing different types of messages in a single response. For example, for customer product inquiries, it provides a text reply, a product image, and finally a purchase link (in the form of a link card).

The following code demonstrates how to use JSON Mode in this scenario to make the model output replies in a fixed structure, and how to parse each type of message in the returned content:

<Note>
  The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
</Note>

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    import json

    from openai import OpenAI
     
    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url="https://api.moonshot.ai/v1",
    )

    system_prompt = """
    You are the intelligent customer service of Moonshot AI (Kimi), responsible for answering various user questions. Please refer to the document content to reply to user questions. Your reply can be text, images, links, and you can include text, images, and links in a single response.

    Please output your reply in the following JSON format:

    {
        "text": "Text information",
        "image": "Image URL",
        "url": "Link URL"
    }

    Note: Please place the text information in the `text` field, put the image in the `image` field in the form of a link starting with `oss://`, and place the regular link in the `url` field.
    """

    completion = client.chat.completions.create(
        model="kimi-k3",
        messages=[
            {"role": "system",
             "content": "You are Kimi, an artificial intelligence assistant provided by Moonshot AI, excelling in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You will reject any questions involving terrorism, racism, pornography, and violence. Moonshot AI is a proper noun and should not be translated into other languages."},
            {"role": "system", "content": system_prompt}, # <-- Submit the system prompt with the output format to Kimi
            {"role": "user", "content": "Hello, my name is Li Lei, what is 1+1?"}
        ],
        response_format={"type": "json_object"}, # <-- Use the response_format parameter to specify the output format as json_object
    )

    # Since we have set JSON Mode, the message.content returned by the Kimi large language model is a serialized JSON Object string.
    # We use json.loads to parse its content and deserialize it into a Python dictionary.
    content = json.loads(completion.choices[0].message.content)

    # Parse text content
    if "text" in content:
    	# For demonstration purposes, we print the content;
    	# In real business logic, you may need to call the text message sending interface to send the generated text to the user.
        print("text:", content["text"])

    # Parse image content
    if "image" in content:
    	# For demonstration purposes, we print the content;
    	# In real business logic, you may need to first parse the image URL, download the image, and then call the image message sending
    	# interface to send the image to the user.
        print("image:", content["image"])

    # Parse link
    if "url" in content:
    	# For demonstration purposes, we print the content;
    	# In real business logic, you may need to call the link card sending interface to send the link to the user in the form of a card.
        print("url:", content["url"])
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const OpenAI = require("openai")
     
    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY, // Set the MOONSHOT_API_KEY environment variable before running this example
        baseURL: "https://api.moonshot.ai/v1",
    })
     
    system_prompt = `
    You are the intelligent customer service of Moonshot AI (Kimi), responsible for answering various user questions. Please refer to the document content to reply to user questions. Your reply can be text, images, links, and you can include text, images, and links in a single response.
    "
    " 
    Please output your reply in the following JSON format:
     
    {
        "text": "Text information",
        "image": "Image URL",
        "url": "Link URL"
    }
    "
    Note: Please place the text information in the 'text' field, put the image in the 'image' field in the form of a link starting with oss://, and place the regular link in the 'url' field.
    `
    async function main() {
        const completion = await client.chat.completions.create({
            model: "kimi-k3",
            messages: [
                {role: "system",
                 content: "You are Kimi, an artificial intelligence assistant provided by Moonshot AI, excelling in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You will reject any questions involving terrorism, racism, pornography, and violence. Moonshot AI is a proper noun and should not be translated into other languages."},
                {role: "system", content: system_prompt}, // <-- Submit the system prompt with the output format to Kimi
                {role: "user", content: "Hello, my name is Li Lei, what is 1+1?"}
            ],
            response_format: {type: "json_object"}, // <-- Use the response_format parameter to specify the output format as json_object
        })
         
        // Since we have set JSON Mode, the message.content returned by the Kimi large language model is a serialized JSON Object string.
        // We use JSON.parse to parse its content and deserialize it into a JavaScript object.
        content = JSON.parse(completion.choices[0].message.content)
         
        // Parse text content
        if (content.text) {
            // For demonstration purposes, we print the content;
            // In real business logic, you may need to call the text message sending interface to send the generated text to the user.
            console.log("text:", content.text)
        } 
        // Parse image content
        if (content.image) {
            // For demonstration purposes, we print the content;
            // In real business logic, you may need to first parse the image URL, download the image, and then call the image message sending
            // interface to send the image to the user.
            console.log("image:", content.image)
        } 
        // Parse link
        if (content.url) {
            // For demonstration purposes, we print the content;
            // In real business logic, you may need to call the link card sending interface to send the link to the user in the form of a card.
            console.log("url", content.url)
        }
    }

    main()
    ```
  </Tab>
</Tabs>

## Troubleshoot truncated JSON output

If you have correctly set the `response_format` parameter and specified the format of the JSON document in the prompt, but the JSON document you receive is incomplete or truncated and cannot be parsed correctly, check whether the `finish_reason` field in the return value is `length`.

A smaller `max_tokens` value will cause the model's output to be truncated, and this rule also applies when using JSON Mode. We recommend estimating the size of the output JSON document and setting a reasonable `max_tokens` value, so that you can correctly parse the JSON document returned by the Kimi large language model.

For a more detailed explanation of incomplete or truncated output from the Kimi large language model, see [Troubleshooting](/docs/guide/troubleshooting).

## Notes

* The Kimi large language model only generates JSON Object type JSON documents; do not prompt it to generate JSON Array or other types of JSON documents.
* If you do not correctly inform the Kimi large language model of the required JSON Object format, it will generate unexpected results.
