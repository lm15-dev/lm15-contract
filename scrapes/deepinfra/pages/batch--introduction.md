> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Introduction to Batch API

> Run large, non-urgent inference jobs asynchronously at 20% off — OpenAI-compatible file upload, batch, and results workflow.

The Batch API lets you submit large volumes of requests as a single asynchronous job and get the results back within 24 hours, billed at **20% below real-time pricing**. It's built for workloads that aren't latency-sensitive — embedding a whole corpus, classifying or summarizing a dataset, or running a model over an evaluation set.

It's **OpenAI-compatible**: if you've used OpenAI's Batch API, the workflow is identical — upload a JSONL file of requests, create a batch, poll for completion, and download the results. Point the OpenAI SDK at DeepInfra and your existing batch code works.

The endpoint is:

```
https://api.deepinfra.com/v1/openai
```

The only changes from your existing OpenAI code are the `base_url` and `api_key`, plus using a model from [our catalog](https://deepinfra.com/models).

<Note>
  Any OpenAI-compatible model available for real-time inference on a batch-supported endpoint can also be used in batch.
</Note>

## Supported endpoints

A batch runs all of its requests against a single endpoint. The supported endpoints are:

* `/v1/chat/completions`
* `/v1/completions`
* `/v1/embeddings`

<Warning>
  Other OpenAI batch endpoints — `/v1/images/generations`, `/v1/images/edits`, `/v1/moderations`, `/v1/responses`, `/v1/videos` — are **not yet** supported and are rejected at validation.
</Warning>

## Workflow

<Steps>
  <Step title="Prepare a JSONL input file" />

  <Step title="Upload the file" />

  <Step title="Create the batch" />

  <Step title="Poll for completion" />

  <Step title="Download the results" />
</Steps>

## Step 1 — Prepare the input file

The input is a [JSONL](https://jsonlines.org/) file with one request per line. Each line has a `custom_id`, the HTTP `method` (`POST`), the `url` (which must match the batch endpoint), and the request `body` — the exact JSON you'd send to that endpoint in real time.

<CodeGroup>
  ```jsonl Chat completions theme={null}
  {"custom_id": "req-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "deepseek-ai/DeepSeek-V4-Flash-0731", "messages": [{"role": "user", "content": "Hello!"}], "max_tokens": 100}}
  {"custom_id": "req-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "deepseek-ai/DeepSeek-V4-Flash-0731", "messages": [{"role": "user", "content": "Write a haiku about batching."}], "max_tokens": 100}}
  ```

  ```jsonl Embeddings theme={null}
  {"custom_id": "doc-1", "method": "POST", "url": "/v1/embeddings", "body": {"model": "Qwen/Qwen3-Embedding-8B", "input": "The food was delicious and the waiter...", "encoding_format": "float"}}
  {"custom_id": "doc-2", "method": "POST", "url": "/v1/embeddings", "body": {"model": "Qwen/Qwen3-Embedding-8B", "input": ["first text", "second text"], "encoding_format": "float"}}
  ```
</CodeGroup>

A few rules:

* **`custom_id` must be unique** across all requests in a file. It's how you match results back to requests, since output order isn't guaranteed.
* **`method` must be `POST`.**
* **`url` must equal the batch's `endpoint`** — you can't mix endpoints in one file.
* **All requests must use the same model.**
* Use a DeepInfra model id (e.g. `deepseek-ai/DeepSeek-V4-Flash-0731`), not an OpenAI model name.
* **`body` must match the request format of the corresponding endpoint** — it's the exact JSON you'd send to that endpoint in real time. See [Chat Completions](/chat/overview), [Text Completions](/apis/completions), or [Embeddings](/apis/embeddings).

## Step 2 — Upload the file

Upload the JSONL file with `purpose="batch"`. In return you get a [FileObject](/batch/file-endpoints#the-fileobject) containing the `id` of the uploaded file. For more information on how to upload a file, see [Create file](/batch/file-endpoints#create-file).

<CodeGroup>
  ```python Python theme={null}
  import os

  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ["DEEPINFRA_API_KEY"],
      base_url="https://api.deepinfra.com/v1/openai",
  )

  batch_input_file = client.files.create(
      file=open("requests.jsonl", "rb"),
      purpose="batch",
  )
  print(batch_input_file.id)
  ```

  ```javascript JavaScript theme={null}
  import fs from "fs";
  import OpenAI from "openai";

  const client = new OpenAI({
    apiKey: process.env.DEEPINFRA_API_KEY,
    baseURL: "https://api.deepinfra.com/v1/openai",
  });

  const batchInputFile = await client.files.create({
    file: fs.createReadStream("requests.jsonl"),
    purpose: "batch",
  });
  console.log(batchInputFile.id);
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/files" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -F purpose="batch" \
    -F file="@requests.jsonl"
  ```
</CodeGroup>

## Step 3 — Create the batch

Create the batch job from the uploaded input file, choosing the `endpoint` to run against. The batch starts executing as soon as it's created. For the exact details of creating a batch request, see [Create a batch](/batch/batch-endpoints#create-a-batch).

<CodeGroup>
  ```python Python theme={null}
  batch = client.batches.create(
      input_file_id=batch_input_file.id,
      endpoint="/v1/chat/completions",
      completion_window="24h",
      metadata={"description": "nightly eval run"},
      output_expires_after={"anchor": "created_at", "seconds": 604800},
  )
  print(batch.id, batch.status)
  ```

  ```javascript JavaScript theme={null}
  const batch = await client.batches.create({
    input_file_id: batchInputFile.id,
    endpoint: "/v1/chat/completions",
    completion_window: "24h",
    metadata: { description: "nightly eval run" },
    output_expires_after: { anchor: "created_at", seconds: 604800 },
  });
  console.log(batch.id, batch.status);
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/batches" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "input_file_id": "file_abc123",
      "endpoint": "/v1/chat/completions",
      "completion_window": "24h",
      "metadata": {"description": "nightly eval run"},
      "output_expires_after": {"anchor": "created_at", "seconds": 604800}
    }'
  ```
</CodeGroup>

## Step 4 — Check status

A batch runs asynchronously, so after creating it you can check its status to know when the results are ready. Retrieve the batch periodically and watch its `status` until it reaches a terminal state — `completed`, `failed`, `expired`, or `cancelled`. For details on retrieving a batch, see [Retrieve a batch](/batch/batch-endpoints#retrieve-a-batch).

<CodeGroup>
  ```python Python theme={null}
  batch = client.batches.retrieve(batch.id)
  print(batch.status)
  print(batch.request_counts)  # total / completed / failed
  ```

  ```javascript JavaScript theme={null}
  const updated = await client.batches.retrieve(batch.id);
  console.log(updated.status);
  console.log(updated.request_counts); // total / completed / failed
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/batches/batch_abc123" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY"
  ```
</CodeGroup>

A batch moves through several statuses — see [Batch status](/batch/batch-objects#batch-status) for what each one means.

You can track progress by checking the `usage` and `request_counts` fields when checking status.

Once the batch reaches a terminal state, the output and error files will be available, if they contain any information.

## Step 5 — Download the results

Once the batch reaches a terminal state, you can get either the [`errors`](/batch/batch-objects#errors) field, or the output and error files (`output_file_id` and `error_file_id`) from the [Batch object](/batch/batch-objects), depending on the state.

You can download the output and error files using the [Files API](/batch/file-endpoints#retrieve-file-content).

<CodeGroup>
  ```python Python theme={null}
  batch = client.batches.retrieve(batch.id)

  # Successful responses
  output = client.files.content(batch.output_file_id)
  print(output.text)

  # Failed / cancelled requests, if any
  if batch.error_file_id:
      errors = client.files.content(batch.error_file_id)
      print(errors.text)
  ```

  ```javascript JavaScript theme={null}
  const done = await client.batches.retrieve(batch.id);

  const output = await client.files.content(done.output_file_id);
  console.log(await output.text());

  if (done.error_file_id) {
    const errors = await client.files.content(done.error_file_id);
    console.log(await errors.text());
  }
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/files/file_out456/content" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY"
  ```
</CodeGroup>

Each result line carries the `custom_id` from the input so you can match it back to your request. Successful lines have a `response`; failed lines have an `error`. The `response` has a `body` field with the same format that the real-time API would return. The `error` has `code` and `message` fields that better describe why the line failed.

```jsonl theme={null}
{"id": "batch_req_xyz", "custom_id": "req-1", "response": {"status_code": 200, "body": {"choices": [{"message": {"role": "assistant", "content": "Hello!"}}]}}, "error": null}
{"id": "batch_req_abc", "custom_id": "req-2", "response": null, "error": {"code": "invalid_request", "message": "..."}}
```

## Cancel a batch

You can cancel a batch at any point while its status is non-terminal. Cancelling a batch puts it in the `cancelling` status for some time, after which it moves to `cancelled`.

<CodeGroup>
  ```python Python theme={null}
  client.batches.cancel(batch.id)
  ```

  ```javascript JavaScript theme={null}
  await client.batches.cancel(batch.id);
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.deepinfra.com/v1/openai/batches/batch_abc123/cancel" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY"
  ```
</CodeGroup>

## Pricing

Batch requests are billed at **20% less** than the corresponding real-time price for the same model and endpoint. The discount is applied automatically — there's nothing extra to configure.

## Rate limits

Batch requests and usage do not affect your real-time rate limits.

There are additional batch-related rate limits:

| Limit                       | Value  |
| --------------------------- | ------ |
| Requests (lines) per file   | 50,000 |
| Input file size             | 200 MB |
| Embedding inputs per file   | 50,000 |
| Concurrent batches per user | 100    |

## Related

* [Chat Completions](/chat/overview)
* [Text Completions](/apis/completions)
* [Embeddings](/apis/embeddings)
