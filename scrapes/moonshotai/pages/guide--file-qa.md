> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use Kimi API for File-Based Q&A

> Upload files, extract their contents, and add them to Kimi API conversations for single-file or multi-file question answering.

The Kimi intelligent assistant can upload files and answer questions based on those files. The Kimi API offers the same functionality. Below, we'll walk through a practical example of how to upload files and ask questions using the Kimi API:

<Note>
  The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
</Note>

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    from pathlib import Path
    from openai import OpenAI
     
    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url="https://api.moonshot.ai/v1",
    )
     
    # 'moonshot.pdf' is an example file. We support content extraction for text files such as pdf, doc, and txt.
    # Image files no longer support content extraction; for image understanding, upload with purpose="image" (see the vision model guide).
    # To upload a file, you can use the file upload API from the openai library. Create a file object using Path from the standard library pathlib and pass it to the file parameter. Set the purpose parameter to 'file-extract'. The file upload interface also supports other purpose values such as 'image' and 'video' (for native model understanding).
    file_object = client.files.create(file=Path("moonshot.pdf"), purpose="file-extract")
     
    # Get the result
    # file_content = client.files.retrieve_content(file_id=file_object.id)
    # Note: The retrieve_content API in some older examples is marked as deprecated in the latest version. You can use the following line instead (if you're using an older SDK version, you can continue using retrieve_content).
    file_content = client.files.content(file_id=file_object.id).text
     
    # Include the file content in the request as a system prompt
    messages = [
        {
            "role": "system",
            "content": "You are Kimi, an AI assistant provided by Moonshot AI. You excel in Chinese and English conversations. You provide users with safe, helpful, and accurate answers while rejecting any queries related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated.",
        },
        {
            "role": "system",
            "content": file_content, # <-- Here, we place the extracted file content (note that it's the content, not the file ID) in the request
        },
        {"role": "user", "content": "Please give a brief introduction to the content of moonshot.pdf"},
    ]
     
    # Then call the chat-completion API to get Kimi's response
    completion = client.chat.completions.create(
      model="kimi-k3",
      messages=messages
    )
     
    print(completion.choices[0].message)
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const OpenAI = require("openai");
    const fs = require("fs")
     
    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,  
        baseURL: "https://api.moonshot.ai/v1",
    });
     
    async function main() {
        // 'moonshot.pdf' is an example file. We support content extraction for text formats such as pdf, doc, and txt.
        // Image files no longer support content extraction; for image understanding, upload with purpose="image" (see the vision model guide).
        let file_object = await client.files.create({
            file: fs.createReadStream("moonshot.pdf"), 
            purpose: "file-extract"
        })
        // Get the result
        // file_content = client.files.retrieve_content(file_id=file_object.id)
        // Note: The retrieve_content API in some older examples is marked as deprecated in the latest version. You can use the following line instead (if you're using an older SDK version, you can continue using retrieve_content).
        let file_content = await (await client.files.content(file_object.id)).text()
     
        // Include it in the request
        let messages = [
            {
                "role": "system",
                "content": "You are Kimi, an AI assistant provided by Moonshot AI. You excel in Chinese and English conversations. You provide users with safe, helpful, and accurate answers while rejecting any queries related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated.",
            },
            {
                "role": "system",
                "content": file_content,
            },
            {"role": "user", "content": "Please give a brief introduction to the content of moonshot.pdf"},
        ]    
     
        const completion = await client.chat.completions.create({
            model: "kimi-k3",         
            messages: messages
        });
        console.log(completion.choices[0].message.content);    
    }
     
    main();
    ```
  </Tab>
</Tabs>

Let's review the basic steps and considerations for file-based Q\&A:

1. Upload the file to the Kimi server using the `/v1/files` interface or the `files.create` API in the SDK;
2. Retrieve the file content using the `/v1/files/{file_id}` interface or the `files.content` API in the SDK. The retrieved content is already formatted in a way that our recommended model can easily understand;
3. Place the extracted (and formatted) file content (not the file `id`) in the messages list as a system prompt;
4. Start asking questions about the file content;

**Note again: Place the file content in the prompt, not the file `id`.**

## Q\&A on Multiple Files

If you want to ask questions based on multiple files, it's quite simple. **Just place each file in a separate system prompt.** Here's how you can do it in code:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    from typing import *
     
    import os
    import json
    from pathlib import Path 
     
    from openai import OpenAI 
     
    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url="https://api.moonshot.ai/v1",
    )
     
     
    def upload_files(files: List[str]) -> List[Dict[str, Any]]:
        """
        upload_files uploads all the provided files (paths) via the '/v1/files' interface and generates file messages from the extracted content. Each file becomes an independent message with a role of 'system', which the Kimi large language model can correctly identify.
     
        :param files: A list of file paths to be uploaded. The paths can be absolute or relative, and should be passed as strings.
        :return: A list of messages containing the file content. Add these messages to the Context, i.e., the messages parameter when calling the `/v1/chat/completions` interface.
        """
        messages = []
     
        # For each file path, we upload the file, extract its content, and generate a message with a role of 'system', which is then added to the final messages list.
        for file in files:
            file_object = client.files.create(file=Path(file), purpose="file-extract")
            file_content = client.files.content(file_id=file_object.id).text
            messages.append({
                "role": "system",
                "content": file_content,
            })
     
        return messages 
     
     
    def main():
        file_messages = upload_files(files=["upload_files.py"])
     
        messages = [
            # We use the * syntax to unpack the file_messages, making them the first N messages in the messages list.
            *file_messages,
            {
                "role": "system",
                "content": "You are Kimi, an AI assistant provided by Moonshot AI. You excel in Chinese and English conversations. You provide users with safe, helpful, and accurate answers while rejecting any queries related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated.",
            },
            {
                "role": "user",
                "content": "Summarize the content of these files.",
            },
        ]
     
        print(json.dumps(messages, indent=2, ensure_ascii=False))
     
        completion = client.chat.completions.create(
            model="kimi-k3",
            messages=messages,
        )
     
        print(completion.choices[0].message.content)
     
     
    if __name__ == '__main__':
        main()
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const fs = require('fs');
    const path = require('path');
    const axios = require('axios');
    const OpenAI = require('openai');
     
    const client = new OpenAI({
        baseURL: "https://api.moonshot.ai/v1",
        // Set the MOONSHOT_API_KEY environment variable before running this example.
        apiKey: process.env.MOONSHOT_API_KEY,
    })
     
     
    async function upload_files(files){
        /* 
        The upload_files function uploads all the provided file paths through the file upload interface '/v1/files', 
        and generates a list of messages from the uploaded file contents. Each file will be a separate message, 
        and all these messages will have the role of 'system'. The Kimi large language model will correctly 
        recognize the file content within these system messages.

        We recommend placing the messages returned by upload_files at the head of the messages list.
        */
        let messages = []

        // For each file path, we upload the file, extract its content, and then generate a message with the 
        // role of 'system', which is added to the final list of messages to be returned.
        for (const file of files) {
            const file_object = await client.files.create({file: fs.createReadStream(path.resolve(file)), purpose: "file-extract"})        
            let file_content = await (await client.files.content(file_object.id)).text()
            messages.push({
                role: "system",
                content: file_content,
            })
        }
        
        return messages
    }

    async function main() {
        const fileMessages = await upload_files(
            ["upload_files.py"]
        )

        const messages = [
            // We use the ... syntax to destructure the file_messages, making them the first N messages in 
            // the messages list.
            ...fileMessages,
            {
                role: "system",
                content: "You are Kimi, an AI assistant provided by Moonshot AI, and you are particularly " +
                           "skilled in Chinese and English conversations. You provide users with safe, helpful, " +
                           "and accurate answers. At the same time, you refuse to answer any questions " +
                           "involving terrorism, racism, pornography, or violence. Moonshot AI is a proper " +
                           "noun and should not be translated into other languages.",
            },
            {
                role: "user",
                content: "Summarize the content of these files.",
            }
        ]

        console.log(JSON.stringify(messages, null, 2))

        const completion = await client.chat.completions.create({
            model: "kimi-k3",
            messages: messages,
        })

        console.log(completion.choices[0].message.content)
    } 
     
    main()
    ```
  </Tab>
</Tabs>

## Best Practices for File Management

In general, the file upload and extraction features are designed to convert files of various formats into a format that our recommended model can easily understand. After completing the file upload and extraction steps, the extracted content can be stored locally. In the next file-based Q\&A request, there is no need to upload and extract the files again.

Since we have limited the number of files a single user can upload (up to 1000 files per user), we suggest that you regularly clean up the uploaded files after the extraction process is complete. You can periodically run the following code to clean up the uploaded files:

<Tabs>
  <Tab title="python">
    ```python theme={null}
    import os
    from openai import OpenAI
     
    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"], # Set the MOONSHOT_API_KEY environment variable before running this example
        base_url="https://api.moonshot.ai/v1",
    )

    file_list = client.files.list()
     
    for file in file_list.data:
    	client.files.delete(file_id=file.id)
    ```
  </Tab>

  <Tab title="node.js">
    ```js theme={null}
    const OpenAI = require("openai")
     
    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY, // Set the MOONSHOT_API_KEY environment variable before running this example
        baseURL: "https://api.moonshot.ai/v1",
    })

    async function main() {
        const file_list = await client.files.list()
     
        for (file of file_list.data) {
            await client.files.delete(file_id=file.id)
        }
    }

    main()
    ```
  </Tab>
</Tabs>

In the code above, we first list all the file details using the `files.list` API and then delete each file using the `files.delete` API. Regularly performing this operation ensures that file storage space is released, allowing subsequent file uploads and extractions to be successful.
