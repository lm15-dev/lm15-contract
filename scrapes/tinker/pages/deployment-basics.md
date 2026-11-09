# Deployment Basics

Tinker trains LoRA adapters and keeps the resulting checkpoints in Tinker storage. To serve a checkpoint outside Tinker, download it and use `tinker_cookbook.weights` to turn it into an artifact your serving stack understands.

| Guide                                                                                                            | Output                                                    | Use it when                                                                                                     |
| ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| [Merge into a HuggingFace Model](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/export-hf/index.md) | A standalone model directory (GBs)                        | You want one deployable model with no LoRA dependency, loadable by `transformers`, vLLM, SGLang, or TGI         |
| [Build a PEFT LoRA Adapter](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/lora-adapter/index.md)   | `adapter_config.json` + `adapter_model.safetensors` (MBs) | You want to keep one base model and hot-swap adapters in vLLM or SGLang                                         |
| [Publish to HuggingFace Hub](https://tinker-docs.thinkingmachines.ai/cookbook/deployment/publish-hub/index.md)   | A Hub repository                                          | You want to share or version either of the above                                                                |
| [Coding with OpenCode](https://tinker-docs.thinkingmachines.ai/tinker/opencode/index.md)                         | Nothing to export                                         | You want to chat or code with a checkpoint straight from your terminal, via Tinker's OpenAI-compatible endpoint |

## Prerequisites

- A **sampler checkpoint**, saved with `save_weights_for_sampler`. Its path looks like `tinker://<run_id>/sampler_weights/<name>` and the archive contains the adapter weights and config that the build functions read. See [Manage Checkpoints](https://tinker-docs.thinkingmachines.ai/tinker/howto/checkpoints/index.md) for saving and downloading checkpoints.
- `tinker-cookbook` installed, and a `TINKER_API_KEY` in your environment.

## Download the checkpoint

Every export path starts with the adapter on local disk. `weights.download` fetches the archive and extracts it, returning the directory it wrote:

```python
from tinker_cookbook import weights

adapter_dir = weights.download(
    tinker_path="tinker://<run_id>/sampler_weights/final",
    output_dir="./adapter",
)
```

The same thing from the shell:

```bash
tinker checkpoint download tinker://<run_id>/sampler_weights/final --output ./
```

See [`tinker checkpoint download`](https://tinker-docs.thinkingmachines.ai/tinker/cli/checkpoint/#checkpoint-download) for the directory naming and `--force` behavior.

## Model support

Merging is supported for every model family Tinker trains. PEFT adapter export depends on the serving framework supporting LoRA for that architecture (for example, vLLM does not serve DeepSeek V3.1 or Kimi-K2.6 adapters). The [weights module README](https://github.com/thinking-machines-lab/tinker-cookbook/blob/main/tinker_cookbook/weights/README.md) has the per-family support matrix and vLLM compatibility notes.
