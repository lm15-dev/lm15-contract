> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Upload File

> Upload a file for text content extraction, image understanding, or video understanding. Supports text-based formats such as pdf, doc, and txt.

<Note>
  Each user can upload a maximum of 1,000 files. Each file must not exceed 100 MB, and the total size of all uploaded files must not exceed 10 GB. The file parsing service is currently free, but rate limiting may be applied during peak traffic periods.
</Note>

<Warning>
  Files API updates on August 31, 2026:

  * File ID change: newly generated file IDs now carry the `file_` prefix
  * Improved document parsing: better parsing of complex content such as tables and formulas
  * Image handling change: images are no longer OCR'd for text extraction. For image understanding, upload images with `purpose="image"`. See [Use Vision Models](/docs/guide/use-kimi-vision-model)
  * Automatic renaming of duplicate files: when an uploaded file has the same name as an existing file, the server automatically renames the new file to avoid conflicts
</Warning>

<Accordion title="Supported Formats">
  Supported formats include `.pdf`, `.txt`, `.csv`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.md`, `.dot`, `.epub`, `.html`, `.json`, `.mobi`, `.log`, `.go`, `.h`, `.c`, `.cpp`, `.cxx`, `.cc`, `.cs`, `.java`, `.js`, `.css`, `.jsp`, `.php`, `.py`, `.py3`, `.asp`, `.yaml`, `.yml`, `.ini`, `.conf`, `.ts`, `.tsx`, and more.

  Note: Image files no longer support content extraction (`file-extract`). For image understanding, upload images with `purpose="image"`. See [Use Vision Models](/docs/guide/use-kimi-vision-model).
</Accordion>

<Accordion title="File Content Extraction Example">
  When uploading a file, use `purpose="file-extract"` if you want the model to use the extracted file contents as context.

  <Tabs>
    <Tab title="python">
      ```python showLineNumbers expandable theme={null}
      from pathlib import Path
      import os

      from openai import OpenAI

      client = OpenAI(
          api_key=os.environ["MOONSHOT_API_KEY"],
          base_url = "https://api.moonshot.ai/v1",
      )

      # xlnet.pdf is an example file; we support text formats such as pdf and doc.
      file_object = client.files.create(file=Path("xlnet.pdf"), purpose="file-extract")

      # Note: retrieve_content is deprecated in the latest version.
      # If you are using the latest SDK, use files.content instead.
      file_content = client.files.content(file_id=file_object.id).text

      messages = [
          {
              "role": "system",
              "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are particularly skilled in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You will refuse to answer any questions involving terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages.",
          },
          {
              "role": "system",
              "content": file_content,
          },
          {"role": "user", "content": "Please give a brief introduction of what xlnet.pdf is about"},
      ]

      completion = client.chat.completions.create(
        model="kimi-k3",
        messages=messages,
        temperature=0.6,
      )

      print(completion.choices[0].message)
      ```
    </Tab>

    <Tab title="curl">
      ```bash showLineNumbers theme={null}
      # xlnet.pdf is a sample file

      curl https://api.moonshot.ai/v1/files \
        -H "Authorization: Bearer $MOONSHOT_API_KEY" \
        -F purpose="file-extract" \
        -F file="@xlnet.pdf"
      ```
    </Tab>

    <Tab title="node.js">
      ```js showLineNumbers expandable theme={null}
      const OpenAI = require("openai");
      const fs = require("fs");

      const client = new OpenAI({
          apiKey: process.env.MOONSHOT_API_KEY,
          baseURL: "https://api.moonshot.ai/v1",
      });

      async function main() {
          let file_object = await client.files.create({
              file: fs.createReadStream("xlnet.pdf"),
              purpose: "file-extract"
          });

          // retrieve_content is deprecated in the latest version.
          let file_content = await (await client.files.content(file_object.id)).text();

          let messages = [
              {
                  "role": "system",
                  "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are more proficient in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You will refuse to answer any questions related to terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages.",
              },
              {
                  "role": "system",
                  "content": file_content,
              },
              {"role": "user", "content": "Please give a brief introduction of what xlnet.pdf is about"},
          ];

          const completion = await client.chat.completions.create({
              model: "kimi-k3",
              messages: messages,
              temperature: 0.6
          });
          console.log(completion.choices[0].message.content);
      }

      main();
      ```
    </Tab>
  </Tabs>

  Replace `$MOONSHOT_API_KEY` with your own API key, or set it as an environment variable before making the call.
</Accordion>

<Accordion title="Multi-file Chat Example">
  If you want to upload multiple files and have a conversation with Kimi based on these files, you can use the following pattern:

  ```python expandable theme={null}
  from typing import *

  import os
  import json
  from pathlib import Path

  from openai import OpenAI

  client = OpenAI(
      base_url="https://api.moonshot.ai/v1",
      api_key=os.environ["MOONSHOT_API_KEY"],
  )


  def upload_files(files: List[str]) -> List[Dict[str, Any]]:
      """
      upload_files uploads all provided files (paths) via the file upload API '/v1/files',
      retrieves the uploaded file content, and generates file messages. Each file becomes
      an independent message with role set to system. The Kimi model will correctly
      recognize the file content in these system messages.

      :param files: A list of file paths to upload. Paths can be absolute or relative,
          passed as strings.
      :return: A list of messages containing file content. Add these messages to the Context,
          i.e., the messages parameter when calling the `/v1/chat/completions` API.
      """
      messages = []

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
          *file_messages,
          {
              "role": "system",
              "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are more proficient in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You will refuse to answer any questions related to terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages.",
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
</Accordion>

<Accordion title="Image or Video Understanding">
  When uploading image or video assets for native model understanding, use `purpose="image"` or `purpose="video"`.

  Please refer to [Using Vision Models](/docs/guide/use-kimi-vision-model) for end-to-end examples.
</Accordion>


## OpenAPI

````yaml POST /v1/files
openapi: 3.1.0
info:
  title: Moonshot AI API
  version: 1.0.0
  description: API for Moonshot AI / Kimi large language model services
servers:
  - url: https://api.moonshot.ai
    description: Production
security: []
paths:
  /v1/files:
    post:
      tags:
        - Files
      summary: Upload File
      description: >-
        Uploads a file for content extraction, image understanding, or video
        understanding. file-extract only supports content extraction from
        text-based files (such as pdf, doc, txt); for image understanding, use
        purpose=image.
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                  description: The file to upload
                purpose:
                  type: string
                  enum:
                    - file-extract
                    - image
                    - video
                    - batch
                  description: >-
                    Specifies how the uploaded file will be processed.
                    file-extract: extract content from text-based files (such as
                    pdf, doc, txt); images are not supported; image: upload
                    images for vision understanding; video: upload videos for
                    video understanding; batch: upload JSONL files for batch
                    processing
              required:
                - file
                - purpose
      responses:
        '200':
          description: Uploaded file metadata
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileObject'
        '400':
          description: Bad request - Invalid upload parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized - Invalid or missing API key
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
      security:
        - bearerAuth: []
components:
  schemas:
    FileObject:
      type: object
      properties:
        id:
          type: string
          description: Unique file identifier
        object:
          type: string
          description: Object type
          example: file
        bytes:
          type: integer
          description: File size in bytes
        created_at:
          type: integer
          description: Unix timestamp when the file was created
        filename:
          type: string
          description: Original file name
        purpose:
          type: string
          description: >-
            Purpose used when uploading the file. file-extract: extract content
            from text-based files (such as pdf, doc, txt); images are not
            supported; image: upload images for vision understanding; video:
            upload videos for video understanding; batch: upload JSONL files for
            batch processing
          enum:
            - file-extract
            - image
            - video
            - batch
        status:
          type: string
          description: Processing status of the file
          example: ready
        status_details:
          type: string
          description: Additional status details when processing fails or returns warnings
      required:
        - id
        - object
        - bytes
        - created_at
        - filename
        - purpose
        - status
    ErrorResponse:
      type: object
      properties:
        error:
          type: object
          properties:
            message:
              type: string
              description: Error message describing what went wrong
            type:
              type: string
              description: Error type
            code:
              type: string
              description: Error code
          required:
            - message
      required:
        - error
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        The Authorization header expects a Bearer token. Use an MOONSHOT_API_KEY
        as the token. This is a server-side secret key. Generate one on the [API
        keys page](https://platform.kimi.ai/console/api-keys) in your dashboard.

````