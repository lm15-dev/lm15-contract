> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Batch API

> Process large-scale async workloads at a discount

Process large volumes of requests asynchronously at **50% off** [Serverless per-token prices](https://docs.fireworks.ai/serverless/pricing). Batch API is ideal for:

* Data labeling and synthetic data generation
* Training smaller models with larger ones ([distillation guide](https://fireworks.ai/blog/deepseek-r1-distillation-reasoning))
* Large-scale evaluations and benchmarking
* Document processing and more

<Tip>
  Batch jobs automatically use [prompt caching](/guides/prompt-caching) for additional 50% cost savings on cached tokens. Maximize cache hits by placing static content first in your prompts.
</Tip>

<Frame>
  <iframe src="https://www.youtube.com/embed/JI3J3zH7ASw" width="100%" height="420" title="Run a batch inference job on Fireworks" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerPolicy="strict-origin-when-cross-origin" allowFullScreen />
</Frame>

## Model compatibility

Not all models support the Batch API. Before submitting a batch job, verify your target model is batch-compatible.

* **Base Models** – Any model that supports [On-Demand Deployments](https://docs.fireworks.ai/guides/ondemand-deployments) in the [Model Library](https://fireworks.ai/models)
* **Custom Models** – Your uploaded or trained models built on a batch-compatible base model

*Note: Newly added models may have a delay before being supported. See [Quantization](/models/quantization) for precision info.*

<Note>
  If a model does not support batch inference, submitting a job may not produce an immediate error — the job can remain in a pending state and never schedule. Always verify compatibility before submitting.
</Note>

**If your batch job is not running:**

1. If validation failed, check your JSONL input — each line must be a complete, valid JSON object matching the request schema.
2. Batch jobs wait to be scheduled in a "pending" state during the selected time window, so it may not run immediately.
3. If the job has been "creating" a deployment for more than 30 minutes, contact support with your job ID.
   1. Confirm the model supports batch inference (see above).
   2. Check that your account has sufficient quota for batch jobs.
4. Progress may pause while waiting on capacity. The job will resume automatically.

## Getting Started

<AccordionGroup>
  <Accordion title="1. Prepare Your Dataset">
    Datasets must be in JSONL format (one JSON object per line):

    **Requirements:**

    * **File format:** JSONL (each line is a valid JSON object)
    * **Size limit:** Up to 80 GiB
    * **Required fields:** `custom_id` (unique) and `body` (request parameters)
    * **Input mode:** `body.messages` (standard) or `body.prompt_token_ids` (pre-tokenized) — mutually exclusive

    **Example dataset (messages):**

    ```json theme={null}
    {"custom_id": "request-1", "body": {"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of France?"}], "max_tokens": 100}}
    {"custom_id": "request-2", "body": {"messages": [{"role": "user", "content": "Explain quantum computing"}], "temperature": 0.7}}
    {"custom_id": "request-3", "body": {"messages": [{"role": "user", "content": "Tell me a joke"}]}}
    ```

    <Tip>
      If every row shares the same `system` message, you can omit it from the dataset and set it once at the job level with `--system-prompt` instead — see [Job-level system prompt](#job-level-system-prompt). This shrinks your upload and keeps prompt-caching intact.
    </Tip>

    **Example dataset (pre-tokenized):**

    When you need byte-identical inputs (e.g. a custom tokenizer or renderer), use `prompt_token_ids` instead of `messages`. The server skips chat-template rendering and feeds your token IDs directly to generation. Mutually exclusive with `messages` — do not include both.

    ```json theme={null}
    {"custom_id": "request-1", "body": {"prompt_token_ids": [163587, 2482, 163601, 71079, 17522, 13], "max_tokens": 100}}
    ```

    <Warning>
      Token IDs must be valid for the vocabulary of the **specific model** the job targets. An out-of-vocabulary ID fails that row with a terminal 400 (no retry), so re-tokenize when you change models.
    </Warning>

    <Warning>
      A job-level `system_prompt` cannot be combined with `prompt_token_ids` — the prompt is already tokenized, so there is nowhere to prepend a system message. Set `system_prompt` only for `messages`-based jobs.
    </Warning>

    <Warning>
      Set `user` or `prompt_cache_key` in the body. Without message text, the gateway has nothing to hash for content-based cache affinity, so each row routes independently and prompt-cache hit rates drop.
    </Warning>

    Save as `batch_input_data.jsonl` locally.
  </Accordion>

  <Accordion title="2. Upload Your Dataset">
    <Tabs>
      <Tab title="UI">
        You can simply navigate to the dataset tab, click `Create Dataset` and follow the wizard.

        <img src="https://mintcdn.com/fireworksai/3EhcJE4PKaydIoxl/images/fine-tuning/dataset.png?fit=max&auto=format&n=3EhcJE4PKaydIoxl&q=85&s=0b5955b3abbd38b2725fb2881d57b8ee" alt="Dataset Upload" width="2168" height="1415" data-path="images/fine-tuning/dataset.png" />
      </Tab>

      <Tab title="firectl">
        ```bash theme={null}
        firectl dataset create batch-input-dataset ./batch_input_data.jsonl
        ```
      </Tab>

      <Tab title="HTTP API">
        You need to make two separate HTTP requests. One for creating the dataset entry and one for uploading the dataset. Full reference here: [Create dataset](/api-reference/create-dataset).

        ```bash theme={null}
        # Create Dataset Entry
        curl -X POST "https://api.fireworks.ai/v1/accounts/${ACCOUNT_ID}/datasets" \
          -H "Authorization: Bearer ${API_KEY}" \
          -H "Content-Type: application/json" \
          -d '{
            "datasetId": "batch-input-dataset",
            "dataset": { "userUploaded": {} }
          }'

        # Upload JSONL file
        curl -X POST "https://api.fireworks.ai/v1/accounts/${ACCOUNT_ID}/datasets/batch-input-dataset:upload" \
          -H "Authorization: Bearer ${API_KEY}" \
          -F "file=@./batch_input_data.jsonl"
        ```
      </Tab>
    </Tabs>
  </Accordion>

  <Accordion title="3. Create a Batch Job">
    <Tabs>
      <Tab title="UI">
        Navigate to the Batch Inference tab and click "Create Batch Inference Job". Choose your batch-eligible model from the dropdown selector:

        <img alt="BIJ Model Selector" lightAlt="BIJ Model Select" darkAlt="BIJ Model Selector" title="BIJ Model Selector" src="https://mintcdn.com/fireworksai/YH2uwOIOrmQeCBpB/images/batch-inference/BIJ_Model_Selector.png?fit=max&auto=format&n=YH2uwOIOrmQeCBpB&q=85&s=2176934ba84ff4cee49b0df6a2d58afe" className="dark:hidden" width="1840" height="970" data-path="images/batch-inference/BIJ_Model_Selector.png" />

        Select your dataset:

        <img alt="BIJ Dataset Selector" lightAlt="BIJ Dataset Selector" darkAlt="BIJ Dataset Selector" src="https://mintcdn.com/fireworksai/YH2uwOIOrmQeCBpB/images/batch-inference/BIJ_Dataset_Selector.png?fit=max&auto=format&n=YH2uwOIOrmQeCBpB&q=85&s=3951881558624efca09290a05a935f30" title="BIJ Dataset Selector" className="dark:hidden" width="1820" height="1126" data-path="images/batch-inference/BIJ_Dataset_Selector.png" />

        Configure optional settings:

        <img alt="BIJ Optional Settings Selector" lightAlt="BIJ Optional Settings" darkAlt="BIJ Optional Settings" src="https://mintcdn.com/fireworksai/YH2uwOIOrmQeCBpB/images/batch-inference/BIJ_Optional_Settings_Selector.png?fit=max&auto=format&n=YH2uwOIOrmQeCBpB&q=85&s=d8809531f0557b468439e553be78c674" title="BIJ Optional Settings Selector" className="dark:hidden" width="1822" height="1318" data-path="images/batch-inference/BIJ_Optional_Settings_Selector.png" />
      </Tab>

      <Tab title="firectl">
        ```bash theme={null}
        firectl batch-inference-job create \
          --model accounts/fireworks/models/llama-v3p1-8b-instruct \
          --input-dataset-id batch-input-dataset
        ```

        With additional parameters:

        ```bash theme={null}
        firectl batch-inference-job create \
          --job-id my-batch-job \
          --model accounts/fireworks/models/llama-v3p1-8b-instruct \
          --input-dataset-id batch-input-dataset \
          --output-dataset-id batch-output-dataset \
          --system-prompt "You are a helpful assistant." \
          --max-tokens 1024 \
          --temperature 0.7 \
          --top-p 0.9
        ```
      </Tab>

      <Tab title="HTTP API">
        ```bash theme={null}
        curl -X POST "https://api.fireworks.ai/v1/accounts/${ACCOUNT_ID}/batchInferenceJobs?batchInferenceJobId=my-batch-job" \
          -H "Authorization: Bearer ${API_KEY}" \
          -H "Content-Type: application/json" \
          -d '{
            "model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
            "inputDatasetId": "accounts/'${ACCOUNT_ID}'/datasets/batch-input-dataset",
            "outputDatasetId": "accounts/'${ACCOUNT_ID}'/datasets/batch-output-dataset",
            "systemPrompt": "You are a helpful assistant.",
            "inferenceParameters": {
              "maxTokens": 1024,
              "temperature": 0.7,
              "topP": 0.9
            }
          }'
        ```
      </Tab>
    </Tabs>
  </Accordion>

  <Accordion title="4. Monitor Your Job">
    <Tabs>
      <Tab title="UI">
        View all your batch inference jobs in the dashboard:

        <img src="https://mintcdn.com/fireworksai/YH2uwOIOrmQeCBpB/images/batch-inference/BIJ_List.png?fit=max&auto=format&n=YH2uwOIOrmQeCBpB&q=85&s=f205ca5d4e7fdfbb706ead3d0e30f86e" alt="BIJ List" width="3840" height="1986" data-path="images/batch-inference/BIJ_List.png" />
      </Tab>

      <Tab title="firectl">
        ```bash theme={null}
        # Get job status
        firectl batch-inference-job get my-batch-job

        # List all batch jobs
        firectl batch-inference-job list
        ```
      </Tab>

      <Tab title="HTTP API">
        ```bash theme={null}
        # Get specific job
        curl -X GET "https://api.fireworks.ai/v1/accounts/${ACCOUNT_ID}/batchInferenceJobs/my-batch-job" \
          -H "Authorization: Bearer ${API_KEY}"

        # List all jobs
        curl -X GET "https://api.fireworks.ai/v1/accounts/${ACCOUNT_ID}/batchInferenceJobs" \
          -H "Authorization: Bearer ${API_KEY}"
        ```
      </Tab>
    </Tabs>
  </Accordion>

  <Accordion title="5. Download Results">
    <Tabs>
      <Tab title="UI">
        Navigate to the output dataset and download the results:

        <img alt="BIJ Download Output" lightAlt="BIJ Download Output" darkAlt="BIJ Download Output" src="https://mintcdn.com/fireworksai/YH2uwOIOrmQeCBpB/images/batch-inference/BIJ_Download_Output.png?fit=max&auto=format&n=YH2uwOIOrmQeCBpB&q=85&s=e8e05a3aef8d35a49e8124d5b9ad7ecc" title="BIJ Download Output" className="dark:hidden" width="2518" height="1384" data-path="images/batch-inference/BIJ_Download_Output.png" />
      </Tab>

      <Tab title="firectl">
        ```bash theme={null}
        firectl dataset download batch-output-dataset
        ```
      </Tab>

      <Tab title="HTTP API">
        ```bash theme={null}
        # Get download endpoint and save response
        curl -s -X GET "https://api.fireworks.ai/v1/accounts/${ACCOUNT_ID}/datasets/batch-output-dataset:getDownloadEndpoint" \
          -H "Authorization: Bearer ${API_KEY}" \
          -d '{}' > download.json

        # Extract and download all files
        jq -r '.filenameToSignedUrls | to_entries[] | "\(.key) \(.value)"' download.json | \
        while read -r object_path signed_url; do
            fname=$(basename "$object_path")
            echo "Downloading → $fname"
            curl -L -o "$fname" "$signed_url"
        done
        ```
      </Tab>
    </Tabs>

    <Tip>
      The output dataset contains two files: a **results file** (successful responses in JSONL format) and an **error file** (failed requests with debugging info).
    </Tip>
  </Accordion>
</AccordionGroup>

## Job-level system prompt

Set one static `system` message for the entire job instead of repeating it on every dataset row. When provided, the batch runner injects it as a leading `system` message into **every input row that does not already begin with a `system` message** — a row's own leading `system` message always takes precedence, so you can override the job-level prompt per-row when needed.

This is useful when all rows share a large, fixed system prompt (e.g. a rubric or output-schema spec). Removing it from every row shrinks the input dataset (less upload, stays under the 80 GiB limit), and because the injected prefix is byte-identical across rows, [prompt caching](/guides/prompt-caching) still applies.

```bash theme={null}
firectl batch-inference-job create \
  --model accounts/fireworks/models/llama-v3p1-8b-instruct \
  --input-dataset-id batch-input-dataset \
  --system-prompt "You are a helpful assistant that responds in JSON."
```

For a long or multi-line prompt, pass it from a file to preserve newlines and avoid shell-escaping:

```bash theme={null}
firectl batch-inference-job create \
  --model accounts/fireworks/models/llama-v3p1-8b-instruct \
  --input-dataset-id batch-input-dataset \
  --system-prompt "$(cat ./system_prompt.txt)"
```

The equivalent HTTP field is `systemPrompt`:

```json theme={null}
{
  "model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
  "inputDatasetId": "accounts/${ACCOUNT_ID}/datasets/batch-input-dataset",
  "systemPrompt": "You are a helpful assistant that responds in JSON."
}
```

<Note>
  The injected system message counts toward the model's context window. If your system prompt is very large and your rows also include long content (e.g. media), the combined prompt may exceed the model's context length — the job will run but produce no completions. Keep the system prompt + per-row content within the model's context limit, or trim the prompt.
</Note>

## Reference

<AccordionGroup>
  <Accordion title="Job states">
    Batch jobs progress through several states:

    | State          | Description                                                                    |
    | -------------- | ------------------------------------------------------------------------------ |
    | **VALIDATING** | Dataset is being validated for format requirements                             |
    | **PENDING**    | Job is queued and waiting for resources                                        |
    | **RUNNING**    | Actively processing requests                                                   |
    | **COMPLETED**  | All requests successfully processed                                            |
    | **FAILED**     | Unrecoverable error occurred (check status message)                            |
    | **EXPIRED**    | Exceeded chosen time limit (12, 24, 48, 72 hrs). Completed requests are saved. |
  </Accordion>

  <Accordion title="Supported models">
    * **Base Models** – Any model that supports [On-Demand Deployments](https://docs.fireworks.ai/guides/ondemand-deployments) in the [Model Library](https://fireworks.ai/models)
    * **Custom Models** – Your uploaded or trained models built on a batch-compatible base model

    *Note: Newly added models may have a delay before being supported. See [Quantization](/models/quantization) for precision info.*
  </Accordion>

  <Accordion title="Limits and constraints">
    * **Per-request limits:** Same as [Chat Completion API limits](/api-reference/post-chatcompletions)
    * **Input dataset:** Up to 80 GiB
    * **Output dataset:** Max 8GB (job may expire early if limit is reached)
    * **Job expiration:** Select from 12, 24, 48, 72 hours maximum in Optional Settings
  </Accordion>

  <Accordion title="Handling expired jobs">
    Jobs expire after 24 hours. Completed rows are billed and saved to the output dataset.

    **Resume processing:**

    ```bash theme={null}
    firectl batch-inference-job create \
      --continue-from original-job-id \
      --model accounts/fireworks/models/llama-v3p1-8b-instruct \
      --output-dataset-id new-output-dataset
    ```

    This processes only unfinished/failed requests from the original job.

    **Download complete lineage:**

    ```bash theme={null}
    firectl dataset download output-dataset-id --download-lineage
    ```

    Downloads all datasets in the continuation chain.
  </Accordion>

  <Accordion title="Best practices">
    * **Validate thoroughly:** Check dataset format before uploading
    * **Descriptive IDs:** Use meaningful `custom_id` values for tracking
    * **Optimize tokens:** Set reasonable `max_tokens` limits
    * **Monitor progress:** Track long-running jobs regularly
    * **Cache optimization:** Place static content first in prompts
    * **Shared system prompt:** If every row uses the same system message, set it once with `--system-prompt` instead of repeating it per row — smaller upload and cache-friendly (see [Job-level system prompt](#job-level-system-prompt))
  </Accordion>
</AccordionGroup>

## Next Steps

<CardGroup cols={3}>
  <Card title="Prompt Caching" icon="bolt" href="/guides/prompt-caching">
    Maximize cost savings with automatic prompt caching
  </Card>

  <Card title="Training" icon="sparkles" href="/fine-tuning/finetuning-intro">
    Create custom models for your batch workloads
  </Card>

  <Card title="API Reference" icon="code" href="/api-reference/create-batch-inference-job">
    Full API documentation for Batch API
  </Card>
</CardGroup>
