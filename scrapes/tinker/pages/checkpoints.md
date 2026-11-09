# Manage Checkpoints

TrainingClients can save checkpoints for resuming training later, or serving the checkpoint for sampling.

| Method                                                                                                                              | Use it to                        | Path                                        |
| ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | ------------------------------------------- |
| [`save_state`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/trainingclient/#save_state)                             | Resume training                  | `tinker://<run_id>/weights/<name>`          |
| [`save_weights_for_sampler`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/trainingclient/#save_weights_for_sampler) | Sample or open in the Playground | `tinker://<run_id>/sampler_weights/<name>`  |
| [`save_weights_external`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/trainingclient/#save_weights_external)       | Download for use outside Tinker  | `tinker://<run_id>/external_weights/<name>` |

## Training checkpoints

Save the full training state, including Adam's moment estimates, with `save_state`:

```python
checkpoint = await training_client.save_state("step-100", user_metadata={ "step": "100", "recipe": "example" })
print(checkpoint.path)  # tinker://<run_id>/weights/step-100

# load without optimizer state
training_client = await service_client.create_training_client_from_state(checkpoint.path)

# load with optimizer state
training_client = await service_client.create_training_client_from_state_with_optimizer(checkpoint.path)

# view checkpoint in Tinker console
print(checkpoint.get_console_url())
```

## Sampler checkpoints

`save_weights_for_sampler` saves only the weights and not gradient or optimizer state for sampling in one of the following ways:

- Load using [`SamplingClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/samplingclient/index.md)
- Use with [`OpenAI`](https://tinker-docs.thinkingmachines.ai/tinker/compatible-apis/openai/index.md) or [`Anthropic`](https://tinker-docs.thinkingmachines.ai/tinker/compatible-apis/anthropic/index.md) compatible APIs
- Chat with it in the [Tinker Playground](https://tinker.thinkingmachines.ai/playground)

```python
sampler_checkpoint = await training_client.save_weights_for_sampler("step-100", user_metadata={ "step": "100", "recipe": "example" })
print(sampler_checkpoint.path)  # tinker://<run_id>/sampler_weights/step-100

# load the checkpoint into a sampling client
sampling_client = await service_client.create_sampling_client(model_path=sampler_checkpoint.path)

# chat with checkpoint in Tinker Playground
print(sampler_checkpoint.get_playground_url())

# manage checkpoint in Tinker console
print(sampler_checkpoint.get_console_url())
```

To sample during training from weights that update as you train, rather than from a fixed checkpoint, see [Inflight Sampling](https://tinker-docs.thinkingmachines.ai/tinker/howto/inflight_sampling/index.md).

## Expiration

Checkpoint storage is charged at $0.10 per GB per month. To ensure checkpoints are not kept forever, you can set a TTL (time to live) when saving a checkpoint.

```python
await training_client.save_state("step-100", ttl_seconds=24 * 3600)

await training_client.save_weights_for_sampler("step-100", ttl_seconds=24 * 3600)
```

Without a TTL, a checkpoint is kept until you delete it. To change the TTL later, see [Set a TTL](#set-a-ttl) below.

## Manage with RestClient

Use the standalone [`RestClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/restclient/index.md) to manage checkpoints after they are saved. It does not need a `ServiceClient` or create a training session.

```python
import tinker

rest_client = tinker.RestClient()
```

### List checkpoints

`list_checkpoints` lists the checkpoints of a single training run. `list_user_checkpoints` lists them across all of your runs, newest first:

```python
response = await rest_client.list_checkpoints("<run_id>")
for checkpoint in response.checkpoints:
    print(checkpoint.checkpoint_type, checkpoint.tinker_path)

recent = await rest_client.list_user_checkpoints(limit=10)
```

### Set a TTL

Change or remove a checkpoint's TTL after it is saved:

```python
# Expire in 7 days
await rest_client.set_checkpoint_ttl_from_tinker_path(path, ttl_seconds=7 * 24 * 3600)

# Keep indefinitely
await rest_client.set_checkpoint_ttl_from_tinker_path(path, ttl_seconds=None)
```

### Publish a checkpoint

Publishing a checkpoint lets other Tinker users load it from its path. Only the owner of the training run can publish or unpublish:

```python
await rest_client.publish_checkpoint_from_tinker_path(path)

await rest_client.unpublish_checkpoint_from_tinker_path(path)
```

### Download weights

Use [`save_weights_external`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/trainingclient/#save_weights_external) to export weights for use outside Tinker. Then [`get_external_weights_urls`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/restclient/#get_external_weights_urls) returns one signed download URL per file, keyed by its path relative to the checkpoint root. It accepts `external_weights` checkpoints, not `weights` or `sampler_weights` paths.

```python
import asyncio
from pathlib import Path
import urllib.request

external_checkpoint = await training_client.save_weights_external("step-100")
print(external_checkpoint.path)  # tinker://<run_id>/external_weights/step-100

downloads = await rest_client.get_external_weights_urls(external_checkpoint.path)
output_dir = Path("./exported-weights").resolve()
for relative_path, url in downloads.urls.items():
    destination = (output_dir / relative_path).resolve()
    if not destination.is_relative_to(output_dir):
        raise ValueError(f"Unsafe checkpoint file path: {relative_path}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(urllib.request.urlretrieve, url, destination)
```

The URLs are valid until `downloads.expires`; request fresh URLs if they expire before the download finishes. [`tinker checkpoint download`](https://tinker-docs.thinkingmachines.ai/tinker/cli/checkpoint/#checkpoint-download) also supports external weights paths and refreshes URLs during long downloads:

```bash
tinker checkpoint download tinker://<run_id>/external_weights/step-100 --output ./models/
```

For deployment options, see [Tinker Cookbook Deployment](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/basics/index.md):

- [Merge into a HuggingFace Model](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/export-hf/index.md): one standalone model you can load with `transformers`, vLLM, or SGLang
- [Build a PEFT LoRA Adapter](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/lora-adapter/index.md): a lightweight adapter to serve on top of the base model in vLLM or SGLang
- [Publish to HuggingFace Hub](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/publish-hub/index.md): upload either one to the Hub
