# Using Inkling

Inkling is Thinking Machines Lab's model family tailored for Tinker: general-purpose models that can code, reason, and call tools. Model effort can be controlled by a float. Inkling is also natively multimodal. Every Inkling model accepts image input, and Inkling and Inkling-Small also accept audio input.

Use [`tml-renderers`](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/tml-renderers/index.md) to construct all of these inputs.

Messages can be OpenAI-compatible Cookbook dictionaries or typed `tml_renderers.chat` objects. Use the format that matches your application.

## Get started

Install the Cookbook, which includes the `tml_renderers` package that Inkling's renderer and scripts depend on:

```bash
uv pip install tinker-cookbook
```

Set the model name in your existing Cookbook workflow:

```python
model_name = "thinkingmachines/Inkling-2-Small"
```

We recommend sweeping learning rate and [thinking effort](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/thinking-effort/index.md) to adapt Inkling to your use case. Use [`sample_reasoning.py`](https://github.com/thinking-machines-lab/tinker-cookbook/blob/main/tinker_cookbook/scripts/inkling/sample_reasoning.py) to compare standard effort values.

The Cookbook selects Inkling's recommended renderer automatically. Each guide links to its corresponding runnable example.

## Learn more

- **[tml-renderers](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/tml-renderers/index.md)** — Message formats, tools, rendering, and training.
- **[Thinking effort](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/thinking-effort/index.md)** — Effort controls, recommended sweep values, and scaling results.
- **[Audio](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/audio/index.md)** and **[Images](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/images/index.md)** — Multimodal input requirements.
- **[Rendering tutorial](https://tinker-docs.thinkingmachines.ai/tutorials/core-concepts/rendering/index.md)** — How renderers bridge messages and model tokens.
- **[Tinker sampling quickstart](https://tinker-docs.thinkingmachines.ai/tinker/quickstart/index.md)** — The lower-level sampling flow.
