> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Using Batch API for Bulk Processing

> Upload JSONL requests, create and monitor Batch API jobs, and download results for large-scale asynchronous inference.

When you need to process large-scale tasks with low real-time requirements, the Batch API is the ideal choice. It supports submitting tasks in bulk via files, saving 40% on inference costs compared to real-time API calls.

<Note>
  Batch API supports both the `kimi-k2.7-code` and `kimi-k2.6` models; `kimi-k3` is not supported. The `temperature`, `top_p`, and other parameters cannot be modified for these models — do not include them in the request body.
</Note>

<CardGroup cols={2}>
  <Card title="Create Batch" icon="plus" href="/docs/api/batch-create">
    Upload a JSONL file and create a batch task
  </Card>

  <Card title="List Batches" icon="list" href="/docs/api/batch-list">
    List batch tasks for your organization
  </Card>

  <Card title="Retrieve Batch" icon="circle-info" href="/docs/api/batch-retrieve">
    Get status and details for a specific batch task
  </Card>

  <Card title="Cancel Batch" icon="xmark" href="/docs/api/batch-cancel">
    Cancel an in-progress batch task
  </Card>
</CardGroup>

## Workflow

This guide walks through a complete text classification example using the Batch API:

### 1. Build the Input File

Each line in the JSONL file is an independent JSON object representing a single inference request:

```json theme={null}
{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "kimi-k2.6", "messages": [{"role": "system", "content": "You are a text classification assistant."}, {"role": "user", "content": "Classify this text: AI is transforming the world"}]}}
```

| Field       | Required | Description                                                                    |
| ----------- | -------- | ------------------------------------------------------------------------------ |
| `custom_id` | Yes      | Custom request identifier for tracking results, must be unique within the file |
| `method`    | Yes      | Request method, must be `POST`                                                 |
| `url`       | Yes      | Request endpoint, must be `/v1/chat/completions`                               |
| `body`      | Yes      | Request body, same parameters as the [Chat Completions API](/docs/api/chat)         |

<Warning>
  The `model` in `body` must be either `kimi-k2.7-code` or `kimi-k2.6`. The `temperature`, `top_p`, `n`, `presence_penalty`, and `frequency_penalty` parameters cannot be modified for these models. Do not include these parameters in the `body`.
</Warning>

<Note>
  **Input file requirements:**

  * File must be in `.jsonl` format, non-empty, and no larger than 100MB
  * Each line must be a valid JSON object containing `custom_id`, `method`, `url`, and `body` fields
  * `custom_id` must be unique within the file
  * All lines must use the same `model` — only one model per batch is allowed
  * `method` must be `POST`, `url` must be `/v1/chat/completions`
  * The specified model must exist and the user must have access to it
</Note>

### 2. Upload the File

Upload the JSONL file via the [Upload File](/docs/api/files-upload) endpoint with `purpose` set to `"batch"`.

<CodeGroup>
  ```python Python theme={null}
  import os
  from openai import OpenAI
  from openai.types import FileObject

  client = OpenAI(
      api_key=os.environ.get("MOONSHOT_API_KEY"),
      base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
  )

  file_object: FileObject = client.files.create(
      file=open("batch_requests.jsonl", "rb"),
      purpose="batch",
  )
  print(file_object.id)  # Save file_id for the next step
  ```

  ```bash cURL theme={null}
  curl ${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/files \
    -H "Authorization: Bearer $MOONSHOT_API_KEY" \
    -F purpose="batch" \
    -F file="@batch_requests.jsonl"
  ```

  ```javascript Node.js theme={null}
  const OpenAI = require("openai");
  const fs = require("fs");

  const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
  });

  async function main() {
      const fileObject = await client.files.create({
          file: fs.createReadStream("batch_requests.jsonl"),
          purpose: "batch"
      });
      console.log(fileObject.id);  // Save file_id for the next step
  }

  main();
  ```
</CodeGroup>

### 3. Create the Task

Call the [Create Batch](/docs/api/batch-create) endpoint with `input_file_id` and `completion_window`. We recommend setting a generous time window for larger datasets.

<CodeGroup>
  ```python Python theme={null}
  import os
  from openai import OpenAI
  from openai.types import Batch

  client = OpenAI(
      api_key=os.environ.get("MOONSHOT_API_KEY"),
      base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
  )

  batch: Batch = client.batches.create(
      input_file_id="your_file_id",
      endpoint="/v1/chat/completions",
      completion_window="24h",
  )
  print(batch.id)  # Save batch_id for polling
  ```

  ```bash cURL theme={null}
  curl ${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/batches \
    -H "Authorization: Bearer $MOONSHOT_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "input_file_id": "your_file_id",
      "endpoint": "/v1/chat/completions",
      "completion_window": "24h"
    }'
  ```

  ```javascript Node.js theme={null}
  const OpenAI = require("openai");

  const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
  });

  async function main() {
      const batch = await client.batches.create({
          input_file_id: "your_file_id",
          endpoint: "/v1/chat/completions",
          completion_window: "24h"
      });
      console.log(batch.id);  // Save batch_id for polling
  }

  main();
  ```
</CodeGroup>

### 4. Wait for Completion

After creation, the task enters `validating` status for input validation. Once validated, it moves to `in_progress`. Use the [Retrieve Batch](/docs/api/batch-retrieve) endpoint to poll for status updates.

<CodeGroup>
  ```python Python theme={null}
  import os
  import time
  from openai import OpenAI
  from openai.types import Batch

  client = OpenAI(
      api_key=os.environ.get("MOONSHOT_API_KEY"),
      base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
  )

  while True:
      batch: Batch = client.batches.retrieve("your_batch_id")
      completed: int = batch.request_counts.completed if batch.request_counts else 0
      total: int = batch.request_counts.total if batch.request_counts else 0
      print(f"Status: {batch.status} ({completed}/{total})")

      if batch.status == "completed":
          break
      elif batch.status in ("failed", "expired", "cancelled"):
          print(f"Task terminated: {batch.status}")
          break

      time.sleep(10)
  ```

  ```bash cURL theme={null}
  curl ${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/batches/your_batch_id \
    -H "Authorization: Bearer $MOONSHOT_API_KEY"
  ```

  ```javascript Node.js theme={null}
  const OpenAI = require("openai");

  const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
  });

  async function main() {
      let batch = await client.batches.retrieve("your_batch_id");
      while (!["completed", "failed", "expired", "cancelled"].includes(batch.status)) {
          await new Promise(r => setTimeout(r, 10000));
          batch = await client.batches.retrieve("your_batch_id");
          console.log(`Status: ${batch.status} (${batch.request_counts.completed}/${batch.request_counts.total})`);
      }
  }

  main();
  ```
</CodeGroup>

### 5. Process Results

When complete, `output_file_id` contains the results file ID. Download it via the [Get File Content](/docs/api/files-content) endpoint. If any requests failed, `error_file_id` contains the error details.

<CodeGroup>
  ```python Python theme={null}
  import json
  import os
  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ.get("MOONSHOT_API_KEY"),
      base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
  )

  output = client.files.content("your_output_file_id")
  for line in output.text.strip().split("\n"):
      result: dict = json.loads(line)
      custom_id: str = result["custom_id"]
      content: str = result["response"]["body"]["choices"][0]["message"]["content"]
      print(f"{custom_id}: {content}")
  ```

  ```bash cURL theme={null}
  curl ${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/files/your_output_file_id/content \
    -H "Authorization: Bearer $MOONSHOT_API_KEY" \
    -o results.jsonl
  ```

  ```javascript Node.js theme={null}
  const OpenAI = require("openai");

  const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
  });

  async function main() {
      const output = await client.files.content("your_output_file_id");
      const text = await output.text();
      for (const line of text.trim().split("\n")) {
          const data = JSON.parse(line);
          console.log(`${data.custom_id}: ${data.response.body.choices[0].message.content}`);
      }
  }

  main();
  ```
</CodeGroup>

Each line in the output file corresponds to a processed request:

```json theme={null}
{
  "id": "request-1",
  "custom_id": "request-1",
  "response": {
    "status_code": 200,
    "request_id": "",
    "body": {
      "id": "chatcmpl-xxx",
      "object": "chat.completion",
      "created": 1711475054,
      "model": "kimi-k2.6",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "This text belongs to the Technology category."
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 30,
        "completion_tokens": 10,
        "total_tokens": 40
      }
    }
  },
  "error": null
}
```

## Complete Code Examples

Complete scripts combining all steps above — copy and run directly:

<CodeGroup>
  ```python Python expandable theme={null}
  import json
  import os
  import time
  from pathlib import Path

  from openai import OpenAI

  MODEL = "kimi-k2.6"

  client = OpenAI(
      api_key=os.environ.get("MOONSHOT_API_KEY"),
      base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
  )


  def create_input_jsonl() -> Path:
      """Build a JSONL input file with classification requests."""
      texts: list[str] = [
          "Hamlet is one of Shakespeare's most famous tragedies",
          "Scientists discover new potentially habitable planet",
          "2024 Artificial Intelligence Development Report",
          "How to make a delicious braised pork dish",
          "Latest iPhone launch event details",
      ]

      requests: list[dict] = []
      for i, text in enumerate(texts):
          requests.append({
              "custom_id": f"text_{i}",
              "method": "POST",
              "url": "/v1/chat/completions",
              "body": {
                  "model": MODEL,
                  "messages": [
                      {"role": "system", "content": "You are a text classification expert. Classify texts into: Literature/News/Academic/Technology/Lifestyle"},
                      {"role": "user", "content": f"Please classify the following text: {text}"},
                  ],
              },
          })

      output_path = Path("classification_requests.jsonl")
      with output_path.open("w", encoding="utf-8") as f:
          for req in requests:
              f.write(json.dumps(req, ensure_ascii=False) + "\n")
      return output_path


  # 1. Build input file
  input_file: Path = create_input_jsonl()

  # 2. Upload file
  file_object = client.files.create(file=input_file, purpose="batch")
  print(f"File uploaded: {file_object.id}")

  # 3. Create batch task
  batch = client.batches.create(
      input_file_id=file_object.id,
      endpoint="/v1/chat/completions",
      completion_window="24h",
  )
  print(f"Batch created: {batch.id}")

  # 4. Poll for completion
  while True:
      batch = client.batches.retrieve(batch.id)
      print(f"Status: {batch.status} ({batch.request_counts.completed}/{batch.request_counts.total})")
      if batch.status == "completed":
          break
      elif batch.status in ("failed", "expired", "cancelled"):
          print(f"Task terminated: {batch.status}")
          exit(1)
      time.sleep(10)

  # 5. Process results
  output = client.files.content(batch.output_file_id)
  for line in output.text.strip().split("\n"):
      data: dict = json.loads(line)
      print(f"{data['custom_id']}: {data['response']['body']['choices'][0]['message']['content']}")
  ```

  ```javascript Node.js expandable theme={null}
  const OpenAI = require("openai");
  const fs = require("fs");

  const MODEL = "kimi-k2.6";

  const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
  });

  // 1. Build input file
  const texts = [
      "Hamlet is one of Shakespeare's most famous tragedies",
      "Scientists discover new potentially habitable planet",
      "2024 Artificial Intelligence Development Report",
      "How to make a delicious braised pork dish",
      "Latest iPhone launch event details"
  ];

  const lines = texts.map((text, i) => JSON.stringify({
      custom_id: `text_${i}`,
      method: "POST",
      url: "/v1/chat/completions",
      body: {
          model: MODEL,
          messages: [
              { role: "system", content: "You are a text classification expert. Classify texts into: Literature/News/Academic/Technology/Lifestyle" },
              { role: "user", content: `Please classify the following text: ${text}` }
          ]
      }
  }));
  fs.writeFileSync("classification_requests.jsonl", lines.join("\n") + "\n");

  async function main() {
      // 2. Upload file
      const fileObject = await client.files.create({
          file: fs.createReadStream("classification_requests.jsonl"),
          purpose: "batch"
      });
      console.log(`File uploaded: ${fileObject.id}`);

      // 3. Create batch task
      const batch = await client.batches.create({
          input_file_id: fileObject.id,
          endpoint: "/v1/chat/completions",
          completion_window: "24h"
      });
      console.log(`Batch created: ${batch.id}`);

      // 4. Poll for completion
      let current = batch;
      while (!["completed", "failed", "expired", "cancelled"].includes(current.status)) {
          await new Promise(r => setTimeout(r, 10000));
          current = await client.batches.retrieve(batch.id);
          console.log(`Status: ${current.status} (${current.request_counts.completed}/${current.request_counts.total})`);
      }

      if (current.status !== "completed") {
          console.error(`Task terminated: ${current.status}`);
          return;
      }

      // 5. Download and process results
      const output = await client.files.content(current.output_file_id);
      const text = await output.text();
      for (const line of text.trim().split("\n")) {
          const data = JSON.parse(line);
          console.log(`${data.custom_id}: ${data.response.body.choices[0].message.content}`);
      }
  }

  main();
  ```
</CodeGroup>

## Batch Status Reference

| Status        | Description                                 |
| ------------- | ------------------------------------------- |
| `validating`  | Created, input data validation in progress  |
| `failed`      | Data validation failed, batch terminated    |
| `in_progress` | Validation passed, execution in progress    |
| `finalizing`  | Execution complete, preparing results       |
| `completed`   | Results ready, batch complete               |
| `expired`     | Did not complete within `completion_window` |
| `cancelling`  | Cancellation requested, pending             |
| `cancelled`   | Cancellation complete, batch terminated     |

## Task Management

### List Batches

Use the [List Batches](/docs/api/batch-list) endpoint to view all batch tasks in your organization.

<CodeGroup>
  ```python Python theme={null}
  import os
  from openai import OpenAI
  from openai.pagination import SyncCursorPage
  from openai.types import Batch

  client = OpenAI(
      api_key=os.environ.get("MOONSHOT_API_KEY"),
      base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
  )

  batches: SyncCursorPage[Batch] = client.batches.list(limit=10)
  for batch in batches.data:
      print(f"{batch.id} - {batch.status} ({batch.request_counts.completed}/{batch.request_counts.total})")
  ```

  ```bash cURL theme={null}
  curl "${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/batches?limit=10" \
    -H "Authorization: Bearer $MOONSHOT_API_KEY"
  ```

  ```javascript Node.js theme={null}
  const OpenAI = require("openai");

  const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
  });

  async function main() {
      const batches = await client.batches.list({ limit: 10 });
      for (const batch of batches.data) {
          console.log(`${batch.id} - ${batch.status} (${batch.request_counts.completed}/${batch.request_counts.total})`);
      }
  }

  main();
  ```
</CodeGroup>

### Cancel a Batch

Use the [Cancel Batch](/docs/api/batch-cancel) endpoint to cancel an in-progress task. Only tasks in `validating`, `in_progress`, or `finalizing` status can be cancelled. After cancellation, the status changes to `cancelling` and then `cancelled`.

<CodeGroup>
  ```python Python theme={null}
  import os
  from openai import OpenAI
  from openai.types import Batch

  client = OpenAI(
      api_key=os.environ.get("MOONSHOT_API_KEY"),
      base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
  )

  batch: Batch = client.batches.cancel("your_batch_id")
  print(f"Status: {batch.status}")  # cancelling
  ```

  ```bash cURL theme={null}
  curl -X POST ${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/batches/your_batch_id/cancel \
    -H "Authorization: Bearer $MOONSHOT_API_KEY"
  ```

  ```javascript Node.js theme={null}
  const OpenAI = require("openai");

  const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
  });

  async function main() {
      const batch = await client.batches.cancel("your_batch_id");
      console.log(`Status: ${batch.status}`);  // cancelling
  }

  main();
  ```
</CodeGroup>

## Multi-modal Batch Tasks

The Batch API supports image and video content in the input file. The key difference from text tasks is in **building the input file** — the rest of the workflow (upload, create task, poll, process results) is identical.

<Accordion title="Image Batch Processing Example">
  There are two ways to include images:

  * **Base64 inline**: Encode images as base64 directly in the JSONL. Suitable for small images. Note that base64 inflates file size by \~33% — keep the 100MB file size limit in mind.
  * **File reference**: Upload images first via the Files API (`purpose="image"`), then reference them in the JSONL using `ms://<file_id>`. Better for large images or image reuse.

  Both methods are provided below — switch between them as needed:

  <CodeGroup>
    ```python Python expandable theme={null}
    import base64
    import json
    import os
    import time
    from pathlib import Path

    from openai import OpenAI
    from openai.types import Batch, FileObject

    client = OpenAI(
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
    )

    MODEL = "kimi-k2.6"
    PROMPT = "Classify this image: Landscape/Portrait/Food/Architecture/Other"
    SYSTEM = "You are an image classification assistant."


    def build_request_base64(custom_id: str, image_path: str) -> dict:
        """Method 1: Encode the image as base64 and embed it directly in the JSONL.
        Best for small images — no extra upload step needed."""
        with open(image_path, "rb") as f:
            image_data: str = base64.b64encode(f.read()).decode("utf-8")
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
                            {"type": "text", "text": PROMPT},
                        ],
                    },
                ],
            },
        }


    def build_request_upload(custom_id: str, image_path: str) -> dict:
        """Method 2: Upload the image first, then reference it via ms://<file_id>.
        Best for large images or when the same image is reused across requests."""
        file_object: FileObject = client.files.create(
            file=open(image_path, "rb"),
            purpose="image",
        )
        print(f"Image uploaded: {image_path} -> {file_object.id}")
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"ms://{file_object.id}"}},
                            {"type": "text", "text": PROMPT},
                        ],
                    },
                ],
            },
        }


    # ====== Choose your build method here ======
    build_request = build_request_base64  # or build_request_upload
    # ============================================

    # 1. Build input file
    images: list[str] = ["image1.png", "image2.png", "image3.png"]
    requests: list[dict] = [build_request(f"img-{i}", path) for i, path in enumerate(images)]

    input_path = Path("image_batch_requests.jsonl")
    with input_path.open("w", encoding="utf-8") as f:
        for req in requests:
            f.write(json.dumps(req, ensure_ascii=False) + "\n")

    # 2. Upload JSONL and create task
    file_object: FileObject = client.files.create(file=input_path, purpose="batch")
    batch: Batch = client.batches.create(
        input_file_id=file_object.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    print(f"Batch created: {batch.id}")

    # 3. Poll for completion
    while True:
        batch = client.batches.retrieve(batch.id)
        print(f"Status: {batch.status} ({batch.request_counts.completed}/{batch.request_counts.total})")
        if batch.status == "completed":
            break
        elif batch.status in ("failed", "expired", "cancelled"):
            print(f"Task terminated: {batch.status}")
            exit(1)
        time.sleep(10)

    # 4. Process results
    output = client.files.content(batch.output_file_id)
    for line in output.text.strip().split("\n"):
        data: dict = json.loads(line)
        print(f"{data['custom_id']}: {data['response']['body']['choices'][0]['message']['content']}")
    ```

    ```javascript Node.js expandable theme={null}
    const OpenAI = require("openai");
    const fs = require("fs");

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
    });

    const MODEL = "kimi-k2.6";
    const PROMPT = "Classify this image: Landscape/Portrait/Food/Architecture/Other";
    const SYSTEM = "You are an image classification assistant.";

    /** Method 1: Encode the image as base64 and embed it directly in the JSONL.
     *  Best for small images — no extra upload step needed. */
    function buildRequestBase64(customId, imagePath) {
        const imageData = fs.readFileSync(imagePath).toString("base64");
        return {
            custom_id: customId,
            method: "POST",
            url: "/v1/chat/completions",
            body: {
                model: MODEL,
                messages: [
                    { role: "system", content: SYSTEM },
                    {
                        role: "user",
                        content: [
                            { type: "image_url", image_url: { url: `data:image/png;base64,${imageData}` } },
                            { type: "text", text: PROMPT },
                        ],
                    },
                ],
            },
        };
    }

    /** Method 2: Upload the image first, then reference it via ms://<file_id>.
     *  Best for large images or when the same image is reused across requests. */
    async function buildRequestUpload(customId, imagePath) {
        const fileObject = await client.files.create({
            file: fs.createReadStream(imagePath),
            purpose: "image"
        });
        console.log(`Image uploaded: ${imagePath} -> ${fileObject.id}`);
        return {
            custom_id: customId,
            method: "POST",
            url: "/v1/chat/completions",
            body: {
                model: MODEL,
                messages: [
                    { role: "system", content: SYSTEM },
                    {
                        role: "user",
                        content: [
                            { type: "image_url", image_url: { url: `ms://${fileObject.id}` } },
                            { type: "text", text: PROMPT },
                        ],
                    },
                ],
            },
        };
    }

    async function main() {
        // ====== Choose your build method here ======
        const useUpload = false; // set to true for file reference method
        // ============================================

        // 1. Build input file
        const images = ["image1.png", "image2.png", "image3.png"];
        const requests = [];
        for (let i = 0; i < images.length; i++) {
            const req = useUpload
                ? await buildRequestUpload(`img-${i}`, images[i])
                : buildRequestBase64(`img-${i}`, images[i]);
            requests.push(JSON.stringify(req));
        }
        fs.writeFileSync("image_batch_requests.jsonl", requests.join("\n") + "\n");

        // 2. Upload JSONL and create task
        const fileObject = await client.files.create({
            file: fs.createReadStream("image_batch_requests.jsonl"),
            purpose: "batch"
        });
        const batch = await client.batches.create({
            input_file_id: fileObject.id,
            endpoint: "/v1/chat/completions",
            completion_window: "24h"
        });
        console.log(`Batch created: ${batch.id}`);

        // 3. Poll for completion
        let current = batch;
        while (!["completed", "failed", "expired", "cancelled"].includes(current.status)) {
            await new Promise(r => setTimeout(r, 10000));
            current = await client.batches.retrieve(batch.id);
            console.log(`Status: ${current.status} (${current.request_counts.completed}/${current.request_counts.total})`);
        }

        if (current.status !== "completed") {
            console.error(`Task terminated: ${current.status}`);
            return;
        }

        // 4. Process results
        const output = await client.files.content(current.output_file_id);
        const text = await output.text();
        for (const line of text.trim().split("\n")) {
            const data = JSON.parse(line);
            console.log(`${data.custom_id}: ${data.response.body.choices[0].message.content}`);
        }
    }

    main();
    ```
  </CodeGroup>
</Accordion>

<Accordion title="Video Batch Processing Example">
  There are two ways to include videos:

  * **Base64 inline**: Encode videos as base64 directly in the JSONL. Suitable for small videos. Note that base64 inflates file size by \~33% — keep the 100MB file size limit in mind.
  * **File reference**: Upload videos first via the Files API (`purpose="video"`), then reference them in the JSONL using `ms://<file_id>`. Better for large videos or video reuse.

  Both methods are provided below — switch between them as needed:

  <CodeGroup>
    ```python Python expandable theme={null}
    import base64
    import json
    import os
    import time
    from pathlib import Path

    from openai import OpenAI
    from openai.types import Batch, FileObject

    MODEL = "kimi-k2.6"

    client = OpenAI(
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
    )

    PROMPT = "Summarize the main content of this video."
    SYSTEM = "You are a video content analysis assistant."


    def build_request_base64(custom_id: str, video_path: str) -> dict:
        """Method 1: Encode the video as base64 and embed it directly in the JSONL.
        Best for small videos — no extra upload step needed."""
        with open(video_path, "rb") as f:
            video_data: str = base64.b64encode(f.read()).decode("utf-8")
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {
                        "role": "user",
                        "content": [
                            {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{video_data}"}},
                            {"type": "text", "text": PROMPT},
                        ],
                    },
                ],
            },
        }


    def build_request_upload(custom_id: str, video_path: str) -> dict:
        """Method 2: Upload the video first, then reference it via ms://<file_id>.
        Best for large videos or when the same video is reused across requests."""
        file_object: FileObject = client.files.create(
            file=open(video_path, "rb"),
            purpose="video",
        )
        print(f"Video uploaded: {video_path} -> {file_object.id}")
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {
                        "role": "user",
                        "content": [
                            {"type": "video_url", "video_url": {"url": f"ms://{file_object.id}"}},
                            {"type": "text", "text": PROMPT},
                        ],
                    },
                ],
            },
        }


    # ====== Choose your build method here ======
    build_request = build_request_base64  # or build_request_upload
    # ============================================

    # 1. Build input file
    videos: list[str] = ["video1.mp4", "video2.mp4", "video3.mp4"]
    requests: list[dict] = [build_request(f"video-{i}", path) for i, path in enumerate(videos)]

    input_path = Path("video_batch_requests.jsonl")
    with input_path.open("w", encoding="utf-8") as f:
        for req in requests:
            f.write(json.dumps(req, ensure_ascii=False) + "\n")

    # 2. Upload JSONL and create task
    batch_file: FileObject = client.files.create(file=input_path, purpose="batch")
    batch: Batch = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    print(f"Batch created: {batch.id}")

    # 3. Poll for completion
    while True:
        batch = client.batches.retrieve(batch.id)
        print(f"Status: {batch.status} ({batch.request_counts.completed}/{batch.request_counts.total})")
        if batch.status == "completed":
            break
        elif batch.status in ("failed", "expired", "cancelled"):
            print(f"Task terminated: {batch.status}")
            exit(1)
        time.sleep(10)

    # 4. Process results
    output = client.files.content(batch.output_file_id)
    for line in output.text.strip().split("\n"):
        data: dict = json.loads(line)
        print(f"{data['custom_id']}: {data['response']['body']['choices'][0]['message']['content']}")
    ```

    ```javascript Node.js expandable theme={null}
    const OpenAI = require("openai");
    const fs = require("fs");

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
    });

    const MODEL = "kimi-k2.6";
    const PROMPT = "Summarize the main content of this video.";
    const SYSTEM = "You are a video content analysis assistant.";

    /** Method 1: Encode the video as base64 and embed it directly in the JSONL.
     *  Best for small videos — no extra upload step needed. */
    function buildRequestBase64(customId, videoPath) {
        const videoData = fs.readFileSync(videoPath).toString("base64");
        return {
            custom_id: customId,
            method: "POST",
            url: "/v1/chat/completions",
            body: {
                model: MODEL,
                messages: [
                    { role: "system", content: SYSTEM },
                    {
                        role: "user",
                        content: [
                            { type: "video_url", video_url: { url: `data:video/mp4;base64,${videoData}` } },
                            { type: "text", text: PROMPT },
                        ],
                    },
                ],
            },
        };
    }

    /** Method 2: Upload the video first, then reference it via ms://<file_id>.
     *  Best for large videos or when the same video is reused across requests. */
    async function buildRequestUpload(customId, videoPath) {
        const fileObject = await client.files.create({
            file: fs.createReadStream(videoPath),
            purpose: "video"
        });
        console.log(`Video uploaded: ${videoPath} -> ${fileObject.id}`);
        return {
            custom_id: customId,
            method: "POST",
            url: "/v1/chat/completions",
            body: {
                model: MODEL,
                messages: [
                    { role: "system", content: SYSTEM },
                    {
                        role: "user",
                        content: [
                            { type: "video_url", video_url: { url: `ms://${fileObject.id}` } },
                            { type: "text", text: PROMPT },
                        ],
                    },
                ],
            },
        };
    }

    async function main() {
        // ====== Choose your build method here ======
        const useUpload = false; // set to true for file reference method
        // ============================================

        // 1. Build input file
        const videos = ["video1.mp4", "video2.mp4", "video3.mp4"];
        const requests = [];
        for (let i = 0; i < videos.length; i++) {
            const req = useUpload
                ? await buildRequestUpload(`video-${i}`, videos[i])
                : buildRequestBase64(`video-${i}`, videos[i]);
            requests.push(JSON.stringify(req));
        }
        fs.writeFileSync("video_batch_requests.jsonl", requests.join("\n") + "\n");

        // 2. Upload JSONL and create task
        const batchFile = await client.files.create({
            file: fs.createReadStream("video_batch_requests.jsonl"),
            purpose: "batch"
        });
        const batch = await client.batches.create({
            input_file_id: batchFile.id,
            endpoint: "/v1/chat/completions",
            completion_window: "24h"
        });
        console.log(`Batch created: ${batch.id}`);

        // 3. Poll for completion
        let current = batch;
        while (!["completed", "failed", "expired", "cancelled"].includes(current.status)) {
            await new Promise(r => setTimeout(r, 10000));
            current = await client.batches.retrieve(batch.id);
            console.log(`Status: ${current.status} (${current.request_counts.completed}/${current.request_counts.total})`);
        }

        if (current.status !== "completed") {
            console.error(`Task terminated: ${current.status}`);
            return;
        }

        // 4. Process results
        const output = await client.files.content(current.output_file_id);
        const text = await output.text();
        for (const line of text.trim().split("\n")) {
            const data = JSON.parse(line);
            console.log(`${data.custom_id}: ${data.response.body.choices[0].message.content}`);
        }
    }

    main();
    ```
  </CodeGroup>
</Accordion>

## Best Practices

* Set `completion_window` based on data volume — use `3d` or `7d` for larger datasets
* Poll every 10-60 seconds to avoid excessive requests
* Process results into databases or reports as needed
* For very large files, consider splitting into multiple batches
