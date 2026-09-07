# Meta Model API
> Meta Model API is a Meta-hosted API service that helps you integrate Meta's models into your applications quickly and efficiently.

## Start here

- [Overview](https://dev.meta.ai/docs/overview.md): Build with Muse Spark, generate and edit images with Muse Image, transcribe speech with Muse Voice Transcribe, run the Muse Code CLI, or download Muse Glimmer open weights.
- [Quickstart](https://dev.meta.ai/docs/quickstart.md): Start fast with Muse Code, or get an API key and wire up your coding agent or SDK to make your first Muse Spark call on Meta Model API.
- [Authentication](https://dev.meta.ai/docs/authentication.md): Create and manage API keys for authenticating requests to Meta Model API.
- [Models](https://dev.meta.ai/docs/models.md): The Muse model families on Meta Model API, spanning Muse Spark, Muse Image, Muse Voice Transcribe, and the open-weight Muse Glimmer, and how to choose the right model.
- [SDKs and libraries](https://dev.meta.ai/docs/sdks.md): Use the OpenAI SDK (Python or TypeScript) or the Anthropic SDK with Meta Model API. No custom client required.
- [Pricing and rate limits](https://dev.meta.ai/docs/pricing-rate-limits.md): Standard and contributor pricing tiers, per-token pricing, image pricing, Muse Voice Transcribe pricing, and rate limits for Meta Model API.

## Capabilities

- [Tool calling](https://dev.meta.ai/docs/tool-calling.md): Define functions the model can invoke, execute them locally, and return results for the model to incorporate.
- [Tool search](https://dev.meta.ai/docs/tool-search.md): Let the model discover and load tools on demand to cut token usage and preserve cache across large tool sets.
- [Search grounding](https://dev.meta.ai/docs/search-grounding.md): Ground model responses in real-time web search results with inline citations.
- [Image understanding](https://dev.meta.ai/docs/image-understanding.md): Analyze images with text prompts using URLs, base64 encoding, or uploaded files.
- [Image generation](https://dev.meta.ai/docs/image-generation.md): Generate and edit images with Muse Image through a conversation: interleave text and reference images and refine across turns on the Responses API, or make one-off calls with the OpenAI-compatible images endpoints.
- [Speech to text](https://dev.meta.ai/docs/speech-to-text.md): Transcribe live audio or supported files with Muse Voice Transcribe on Meta Model API.
- [Video understanding](https://dev.meta.ai/docs/video-understanding.md): Analyze video and audio with text prompts—summarize clips, answer questions about footage, and transcribe speech—on the Responses API and Chat Completions.
- [File handling](https://dev.meta.ai/docs/file-handling.md): Send files to the model inline in a Responses or chat completion request, or upload them once with the Files API and reference them by ID.
- [Reasoning](https://dev.meta.ai/docs/reasoning.md): Control how much the model thinks before responding using the reasoning_effort parameter.
- [Structured output](https://dev.meta.ai/docs/structured-output.md): Constrain model output to match a JSON schema using the response_format parameter.
- [Prompt caching](https://dev.meta.ai/docs/prompt-caching.md): Prompt caching is automatic — repeated prompt prefixes are served from cache to cut latency and input-token cost, with no key or setup required.
- [Token counting](https://dev.meta.ai/docs/token-counting.md): Count the fully rendered input tokens for a request before inference, to check context-window fit.

## Protocols

- [Choosing an API](https://dev.meta.ai/docs/protocols.md): Compare the Responses, Chat Completions, and Messages formats on Meta Model API — same models, same auth, same cost — and pick the one your code already speaks.
- [Responses API](https://dev.meta.ai/docs/protocols/responses.md): Run agentic and multi-turn workloads on the Responses API with cross-turn reasoning replay, tool loops, search grounding, and file inputs.
- [Chat Completions API](https://dev.meta.ai/docs/protocols/chat-completions.md): Send messages and receive model-generated responses using the chat completions endpoint.
- [Messages API](https://dev.meta.ai/docs/protocols/messages.md): Call Muse Spark with the Messages API, the Anthropic Messages-compatible endpoint on Meta Model API.

## Cookbook

- [All recipes](https://dev.meta.ai/docs/cookbook.md): Working recipes for building on Meta Model API — API primitives, agent loops, and end-to-end use cases on Muse Spark.
- [API fundamentals](https://dev.meta.ai/docs/cookbook/api-fundamentals.md): Cookbook recipes for the Model API building blocks — chat completions, streaming, tool calling, structured output, caching, reasoning, vision, and search grounding.
- [Agent patterns](https://dev.meta.ai/docs/cookbook/agent-patterns.md): Cookbook recipes for turning Muse Spark into an agent — the core loop, interleaved reasoning and tool use, context management, and validated edits.
- [Use cases](https://dev.meta.ai/docs/cookbook/use-cases.md): End-to-end Model API recipes — multimodal perception, orchestration, and complete apps you can adapt, built on Muse Spark.
- [Building with Muse Code](https://dev.meta.ai/docs/cookbook/muse-code.md): Cookbook recipes for building durable agents with Muse Code — audit and resume, deterministic replay, staged approvals, sandboxing, immutable guardrails, subagent fanout, goals, bundled skills, scheduling, and side chats.
- [Muse Image](https://dev.meta.ai/docs/cookbook/muse-image.md): Recipes for generating, editing, and composing images with Muse Image, including web grounding, consistent series, and multi-turn edits.

## Muse Code

- [Overview](https://dev.meta.ai/docs/muse-code.md): Muse Code is Meta's coding agent for the terminal and CI, built on Muse Spark, with approvals, sandboxing, sessions, and multi-agent orchestration.
- [Authentication and billing](https://dev.meta.ai/docs/muse-code/auth.md): Sign in to Muse Code through your browser, use an API key for non-interactive runs, and manage billing.
- [Subscriptions](https://dev.meta.ai/docs/muse-code/subscriptions.md): Subscribe to a flat monthly rate for Muse Code instead of paying per token, choose a plan, and cancel or manage your subscription.
- [Permissions and safety](https://dev.meta.ai/docs/muse-code/permissions.md): Control what Muse Code can do with approval modes, stage-by-stage shell-command review, scoped trust, and an OS-enforced sandbox.
- [Working with the agent](https://dev.meta.ai/docs/muse-code/interactive.md): Drive an interactive Muse Code session with slash commands: steer a running turn, manage sessions, control context, set goals and loops, track tasks, and use voice.
- [Workflows](https://dev.meta.ai/docs/muse-code/workflows.md): Use Muse Code workflows to coordinate parallel agents, monitor their progress, and save repeatable multi-agent tasks.
- [Session messaging](https://dev.meta.ai/docs/muse-code/session-messaging.md): Name Muse Code sessions and send local messages between them for handoffs, review requests, and status updates.
- [Rewind a conversation](https://dev.meta.ai/docs/muse-code/rewind.md): Reopen an earlier Muse Code message in a new conversation branch without changing the original session or workspace files.
- [Configuration and context](https://dev.meta.ai/docs/muse-code/configuration.md): Configure Muse Code with the settings file, project instruction files, model and reasoning-effort selection, launch flags, and durable project memory.
- [Extending and automating](https://dev.meta.ai/docs/muse-code/extending.md): Scale Muse Code beyond a single interactive session — parallel subagents, reusable skills, lifecycle hooks, MCP servers, and headless runs for CI.
- [Changelog](https://dev.meta.ai/docs/muse-code/changelog.md): What's new, improved, and fixed in each Muse Code release.

## Muse Glimmer

- [Overview](https://dev.meta.ai/docs/muse-glimmer.md): Open-source multimodal model distilled from Muse Spark, built for local and edge deployment.
- [Get the model](https://dev.meta.ai/docs/muse-glimmer/get-the-model.md): Download Muse Glimmer weights and artifacts from Hugging Face and pick the build your runtime needs.
- [Prompting guide](https://dev.meta.ai/docs/muse-glimmer/prompting.md): Chat template, system prompts, reasoning, and tool calling for getting the most out of Muse Glimmer.
- [Quantization](https://dev.meta.ai/docs/muse-glimmer/quantization.md): Run Muse Glimmer's pre-quantized GGUF checkpoints on a single GPU with llama.cpp.
- [Speculative decoding](https://dev.meta.ai/docs/muse-glimmer/spec-decode.md): Accelerate Muse Glimmer inference with DFlash speculative decoding on llama.cpp, SGLang, and ExecuTorch.

### Run inference

- [Overview](https://dev.meta.ai/docs/muse-glimmer/deploy.md): Run Muse Glimmer on your own infrastructure or through a hosted cloud provider.
- [Deploy with vLLM](https://dev.meta.ai/docs/muse-glimmer/vllm.md): Serve Muse Glimmer with vLLM for production-grade throughput and OpenAI-compatible endpoints.
- [Deploy with SGLang](https://dev.meta.ai/docs/muse-glimmer/sglang.md): Serve Muse Glimmer with SGLang for high-throughput local inference with an OpenAI-compatible endpoint.
- [Deploy with llama.cpp](https://dev.meta.ai/docs/muse-glimmer/llama-cpp.md): Run Muse Glimmer locally with llama.cpp for CPU, mixed, and GPU inference.
- [Deploy with ExecuTorch](https://dev.meta.ai/docs/muse-glimmer/executorch.md): Export Muse Glimmer ahead of time and serve it on CUDA or Apple silicon with vision, tool calling, and DFlash speculative decoding.
- [Run with Together AI](https://dev.meta.ai/docs/muse-glimmer/together-ai.md): Run Muse Glimmer through Together AI's managed chat completions API.

### Customization

- [Overview](https://dev.meta.ai/docs/muse-glimmer/customization.md): Adapt Muse Glimmer to your domain with supervised fine-tuning (SFT) and reinforcement learning (RL).
- [Fine-tuning (SFT)](https://dev.meta.ai/docs/muse-glimmer/fine-tuning.md): Fine-tune Muse Glimmer with LoRA, QLoRA, or full-parameter supervised training for your domain.
- [Reinforcement learning](https://dev.meta.ai/docs/muse-glimmer/rl.md): Optimize Muse Glimmer against a reward signal with preference optimization (DPO) or online RL (GRPO/PPO).

## Agent guides

- [Coding agents](https://dev.meta.ai/docs/coding-agents.md): Connect coding agents like OpenCode, Codex, and Claude Code to Model API and drive Muse Spark for agentic coding workflows.
- [Agent frameworks](https://dev.meta.ai/docs/agent-frameworks.md): Run your own agent loop on Muse Spark with the Claude Agent SDK or the OpenAI Codex app-server.
- [Computer use](https://dev.meta.ai/docs/computer-use.md): Drive Muse Spark as a computer-use agent with a developer-defined computer tool — screenshots in, normalized actions out, executed in your own harness.

## API reference

- [Introduction](https://dev.meta.ai/docs/api-reference.md): The Meta Model API HTTP reference — base URL, authentication, and the Responses, Chat Completions, Messages, Files, Models, and Status resources.
- [Error handling](https://dev.meta.ai/docs/error-handling.md): Handle API errors, troubleshoot common issues, and build resilient Meta Model API integrations with proper retry logic.
- [Status](https://dev.meta.ai/docs/api-reference/status.md): API reference for the unauthenticated /v1/status service-health endpoint.

### Responses

- [Overview](https://dev.meta.ai/docs/api-reference/responses.md): API reference for the /v1/responses endpoints.
- [Create a response](https://dev.meta.ai/docs/api-reference/responses/create-response.md): API reference for creating a model response with POST /v1/responses.
- [Retrieve a response](https://dev.meta.ai/docs/api-reference/responses/retrieve-response.md): API reference for retrieving a model response with GET /v1/responses/{response_id}.
- [Delete a response](https://dev.meta.ai/docs/api-reference/responses/delete-response.md): API reference for deleting a model response with DELETE /v1/responses/{response_id}.
- [Cancel a response](https://dev.meta.ai/docs/api-reference/responses/cancel-response.md): API reference for cancelling an in-progress model response with POST /v1/responses/{response_id}/cancel.
- [Count input tokens](https://dev.meta.ai/docs/api-reference/responses/count-input-tokens.md): API reference for counting input tokens with POST /v1/responses/input_tokens.
- [Schemas](https://dev.meta.ai/docs/api-reference/responses/schemas.md): Full schema and model definitions referenced by the Responses API endpoints.

### Chat completions

- [Overview](https://dev.meta.ai/docs/api-reference/chat-completions.md): API reference for the POST /v1/chat/completions endpoint.
- [Create a chat completion](https://dev.meta.ai/docs/api-reference/chat-completions/create-chat-completion.md): API reference for generating a model response with POST /v1/chat/completions.
- [Schemas](https://dev.meta.ai/docs/api-reference/chat-completions/schemas.md): Full schema and model definitions referenced by the Chat completions API endpoint.

### Messages

- [Overview](https://dev.meta.ai/docs/api-reference/messages.md): API reference for the Anthropic-compatible /v1/messages endpoints.
- [Create a message](https://dev.meta.ai/docs/api-reference/messages/create-message.md): API reference for generating an Anthropic-compatible message with POST /v1/messages.
- [Count tokens](https://dev.meta.ai/docs/api-reference/messages/count-tokens.md): API reference for counting input tokens with POST /v1/messages/count_tokens.
- [Schemas](https://dev.meta.ai/docs/api-reference/messages/schemas.md): Full schema and model definitions referenced by the Anthropic-compatible Messages API endpoints.

### Files

- [Overview](https://dev.meta.ai/docs/api-reference/files.md): API reference for file upload, list, retrieve, content, and delete endpoints.
- [Upload a file](https://dev.meta.ai/docs/api-reference/files/upload-file.md): API reference for uploading a file with POST /v1/files.
- [List files](https://dev.meta.ai/docs/api-reference/files/list-files.md): API reference for listing uploaded files with GET /v1/files.
- [Retrieve a file](https://dev.meta.ai/docs/api-reference/files/retrieve-file.md): API reference for retrieving a file's metadata with GET /v1/files/{file_id}.
- [Retrieve file content](https://dev.meta.ai/docs/api-reference/files/retrieve-file-content.md): API reference for downloading a file's contents with GET /v1/files/{file_id}/content.
- [Delete a file](https://dev.meta.ai/docs/api-reference/files/delete-file.md): API reference for deleting an uploaded file with DELETE /v1/files/{file_id}.
- [Schemas](https://dev.meta.ai/docs/api-reference/files/schemas.md): Full schema and model definitions referenced by the Files API endpoints.

### Images

- [Overview](https://dev.meta.ai/docs/api-reference/images.md): API reference for the image generation and image editing endpoints.
- [Generate an image](https://dev.meta.ai/docs/api-reference/images/create-image.md): API reference for generating an image with POST /v1/images/generations.
- [Edit an image](https://dev.meta.ai/docs/api-reference/images/edit-image.md): API reference for editing or composing images with POST /v1/images/edits.
- [Schemas](https://dev.meta.ai/docs/api-reference/images/schemas.md): Full schema and model definitions referenced by the Images API endpoints.

### Voice

- [Overview](https://dev.meta.ai/docs/api-reference/voice.md): API reference for the audio transcription endpoints.
- [Transcribe a recording](https://dev.meta.ai/docs/api-reference/voice/transcribe.md): API reference for transcribing an audio file with POST /v1/asr/transcribe.
- [Transcribe in realtime](https://dev.meta.ai/docs/api-reference/voice/realtime.md): API reference for streaming transcription over a WebSocket at wss://api.meta.ai/v1/asr/realtime.
- [Schemas](https://dev.meta.ai/docs/api-reference/voice/schemas.md): Full schema and model definitions referenced by the Audio API endpoints.

### Models

- [Overview](https://dev.meta.ai/docs/api-reference/models.md): API reference for the /v1/models endpoints.
- [List models](https://dev.meta.ai/docs/api-reference/models/list-models.md): API reference for listing available models with GET /v1/models.
- [Retrieve a model](https://dev.meta.ai/docs/api-reference/models/retrieve-model.md): API reference for retrieving a single model's metadata with GET /v1/models/{model}.
- [Schemas](https://dev.meta.ai/docs/api-reference/models/schemas.md): Full schema and model definitions referenced by the Models API endpoints.