> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Overview

> Run asynchronous batch workloads at up to 50% lower cost.

<Tip>
  Using a coding agent? Install the [together-batch-inference](https://github.com/togethercomputer/skills/tree/main/skills/together-batch-inference) skill to let your agent write correct batch inference code automatically. See [agent skills](/docs/agent-skills) for details.
</Tip>

The batch API runs many independent inference requests asynchronously from a single uploaded JSONL file. You get up to 50% off serverless rates and a separate rate limit pool, in exchange for a job-shaped (rather than request-shaped) workflow.

You can start a batch job from the console, through the API/SDK, or with the CLI:

```bash theme={null}
# upload the file and create the batch
tg batches submit batch_input.jsonl --api chat.completions

# poll until COMPLETED
tg batches get <BATCH_ID>

# save the results
tg batches download <BATCH_ID> --output batch_output.jsonl
```

The [batch tutorial](/docs/inference/batch/tutorial) breaks down this flow and walks through the SDK and REST equivalents.

## When to use it

Consider using batch jobs when latency is not your primary concern. For example, when you want to classify a large dataset, run evaluations, generate synthetic data, or offline summarizations. The 24-hour completion window is a maximum, not a typical wait time. Small batches (under 1,000 requests) typically finish in minutes.

If your workload is interactive, depends on shared conversation state across requests, or needs sub-second responses, use the standard [chat completions](/docs/inference/chat/overview) endpoint instead.

## Rate limits

Batch jobs run against a separate rate-limit pool from the standard real-time API.

* Up to 50,000 requests per batch.
* Up to 100 MB per input file.
* Up to 10 MB per line in the input file. Inline base64 payloads, such as images embedded as `data:image/...;base64,` URLs, count toward this limit.
* Up to 30B tokens enqueued per model at any time.
* Completion window defaults to `24h` and cannot be changed. It is a best-effort target.

See [rate limits](/docs/serverless/rate-limits) for more info.

## Supported models

Most [serverless models](/docs/serverless/models) support batch processing through the `/v1/chat/completions` endpoint. Audio models like `openai/whisper-large-v3` run through `/v1/audio/transcriptions` and `/v1/audio/translations` — see [Run an audio transcription batch](/docs/inference/batch/tutorial#run-an-audio-transcription-batch) for the input format. Batch jobs can also run against [dedicated model inference](/docs/dedicated-endpoints/overview), but the discount does not apply to dedicated model inference usage.

### Discounted models

Selected serverless models run at 50% off batch rates:

| Model ID                                  |
| ----------------------------------------- |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` |
| `openai/whisper-large-v3`                 |

Models not listed run at standard rates.

## Run your first batch job

Follow the [batch tutorial](/docs/inference/batch/tutorial) for an end-to-end walkthrough: prepare a JSONL file, upload it, create the batch, poll until it finishes, and download the results.

Batch job results are returned in arbitrary order. Use the `custom_id` field on each input request to reconcile inputs with outputs and errors. A single uploaded file can back multiple batch jobs without re-uploading.

## Billing

Together bills you for each successful response in the output file. Failed requests in the error file aren't billed. [Cancelling a batch](/docs/inference/batch/manage#cancel-a-batch) doesn't refund successful responses generated before the cancel landed.

## Best practices

* **Aim for 1,000 to 10,000 requests per batch:** Smaller batches still work but waste the per-job overhead. Larger batches risk hitting the 50,000-request cap.
* **Keep `custom_id` values stable and meaningful:** Treat them as the join key between input, output, and error files.
* **For classification or labeling, set `max_tokens` to 4 and `temperature` to 0:** Constrain the system prompt to return only the label. Output tokens dominate cost on short-output workloads.
* **Validate your JSONL locally before uploading:** A malformed input file fails the entire batch in `VALIDATING`.
* **Track progress by status, not wall-clock time:** Complex or popular models can occasionally exceed the standard 24-hour window. As long as the status is `IN_PROGRESS`, the job is still being processed. Wait at least 72 hours of `IN_PROGRESS` before contacting support.
* **Always inspect the error file:** Even when the batch reports `COMPLETED`, per-request errors don't change the overall batch status.

## Next steps

* [Run a batch job](/docs/inference/batch/tutorial): tutorial walking through an end-to-end batch job from JSONL to results.
* [Manage batch jobs](/docs/inference/batch/manage): cancel, list, error files, and other operational reference.
* [Batches CLI](/reference/cli/batches): submit, list, retrieve, download, and cancel batch jobs from the terminal.
* [OpenAI compatibility](/docs/inference/openai-compatibility): how Together's Batch API compares to the OpenAI Batch endpoint.
