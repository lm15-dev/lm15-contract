> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# What is DeepInfra

> AI inference cloud — OpenAI-compatible API, 100s of open-source models, private GPU deployments, and GPU rental.

DeepInfra is an AI inference cloud that makes it simple to run the latest machine learning models at scale — LLMs, vision, embeddings, image generation, video generation, speech, and more.

## What you can do

<CardGroup cols={2}>
  <Card title="LLMs & Chat" icon="comments" href="/chat/overview">
    OpenAI-compatible API for 100+ LLMs. Swap your base URL, keep your code.
  </Card>

  <Card title="Vision & OCR" icon="eye" href="/chat/vision">
    Multimodal models for visual understanding and document text extraction.
  </Card>

  <Card title="Embeddings & Reranking" icon="vector-square" href="/apis/embeddings">
    State-of-the-art embedding and reranker models for search and RAG.
  </Card>

  <Card title="Image & Video Generation" icon="image" href="/apis/image-generation">
    FLUX, Stable Diffusion, text-to-video, and more.
  </Card>

  <Card title="Speech" icon="microphone" href="/apis/speech">
    Speech recognition (Whisper) and text-to-speech models.
  </Card>

  <Card title="Deploy Private Models" icon="lock" href="/private-models/overview">
    Run your own fine-tuned LLM on A100 / H100 / H200 / B200 / B300 with autoscaling.
  </Card>
</CardGroup>

## Why DeepInfra

**Drop-in OpenAI replacement.** Point your existing OpenAI SDK to `https://api.deepinfra.com/v1/openai` and your code works without changes. No migration required.

**Best price for open-source models.** DeepInfra consistently offers the lowest prices for open-source model inference. You only pay per token — no idle GPU time, no minimums, no seat fees. DeepInfra is also the provider with the most models on [OpenRouter](https://openrouter.ai/provider/deepinfra).

**Always-fresh model catalog.** DeepInfra is typically among the first providers to deploy a newly released model.

**Private deployments for compliance and customization.** Need to run your own fine-tuned weights, or require data isolation? Deploy a dedicated instance on A100/H100/H200/B200/B300 with autoscaling and a private endpoint — competitive GPU pricing, deployable in just a few clicks.

**GPU Clusters for training and full control.** Rent a B200 or B300 cluster with SSH access and run whatever you want.

## Get started in 60 seconds

<Card title="Quickstart" icon="play" href="/quickstart">
  Make your first API call — no installation required.
</Card>

## Quick example

```python theme={null}
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash-0731",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

Get your API key from the [Dashboard](https://deepinfra.com/dash/api_keys).
