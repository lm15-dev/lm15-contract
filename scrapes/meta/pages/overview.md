---
meta:
  title: Get started with Muse Spark, Muse Image, Muse Voice Transcribe, and Muse Glimmer - Meta Model API
  description: Build with Muse Spark, generate and edit images with Muse Image, transcribe speech with Muse Voice Transcribe, run the Muse Code CLI, or download Muse Glimmer open weights.
  keywords: Meta Model API, Muse Spark, Muse Image, Muse Voice Transcribe, Muse Glimmer, speech to text, transcription, image generation, open weights, local inference, coding agent, quickstart, capabilities, cookbook
cms:
  layout: large
  alias: /model-api/docs/overview
  target: aidmc
---

# Build with Muse Spark, Muse Image, Muse Voice Transcribe, and Muse Glimmer

Muse Spark, Muse Image, Muse Voice Transcribe, and Muse Glimmer are part of the Muse model family.

[Muse Spark](#muse-spark) is served through Meta Model API, with agent-ready primitives and no extra setup: parallel tool calls, streamed tool-call arguments, reasoning that carries across turns, and a 1M-token context window.

[Muse Image](#muse-image) is served through Meta Model API too. It generates and edits images from a text prompt and refines them across turns.

[Muse Voice Transcribe](#muse-voice-transcribe) is Meta's speech-to-text model on Meta Model API. It transcribes streaming and non-streaming audio, with speaker attribution and turn detection in the model.

[Muse Glimmer](#muse-glimmer) delivers strong performance for its size class. It ships with open weights under a permissive Apache 2.0 license, so you can download it and run it on your own hardware.

## Build with Muse Spark {#muse-spark}

Call Meta Model API directly, run Muse Code, or connect the coding agent you already use. All three drive the same model over the same auth and billing.

### At a glance {#at-a-glance}

Everything you need to make your first call.

|  |  |
| --- | --- |
| **Base URL** | `https://api.meta.ai/v1` |
| **[Standard tier](/docs/pricing-rate-limits#standard-tier) models** | `muse-spark-1.3`, `muse-spark-1.2`, `muse-spark-1.1` |
| **[Contributor tier](/docs/pricing-rate-limits#contributor-tier) models** | `muse-spark-1.3-contributor`, `muse-spark-1.2-contributor` |
| **Context window** | 1,048,576 tokens |
| **Auth** | Bearer token (`MODEL_API_KEY`) |
| **Pricing** | Pay-as-you-go; see [Pricing and rate limits](/docs/pricing-rate-limits) |

### Call the API directly {#call-the-api}

Meta Model API is drop-in compatible with the OpenAI SDK, the Anthropic SDK, and OpenAI-compatible agent CLIs. Set your client's base URL, add your key, and keep the rest of your code.

Walk through your first call in the [quickstart](/docs/quickstart), or compare request formats in [Choosing an API](/docs/protocols).

### Run Muse Code {#muse-code}

Muse Code is a coding agent from Meta for the terminal and CI, built on Muse Spark. Install it, sign in, and run it in a project. It plans, edits, and runs commands to do a task, with approvals and an OS sandbox on from the first run.

Install the CLI on macOS or Linux:

```bash
curl -fsSL https://dev.meta.ai/install.sh | sh
```

Start building:

```bash
muse   # start Muse Code; on first run, choose a browser sign-in or paste an API key
```

> [!NOTE] Muse Code or the API
> Muse Code and the API are two ways to use the same model. Run Muse Code for a ready-made agent at the command line or in CI; call the API directly when you build your own agent or app.

Learn more in the [Muse Code overview](/docs/muse-code).

### Connect your coding agent {#existing-stack}

Already have a coding agent? Connect it to Model API and keep working. Muse Spark drives the same agentic loop of file edits, shell commands, and tool calls over an OpenAI- or Anthropic-compatible surface.

## Build with Muse Image {#muse-image}

Muse Image generates and edits images through Meta Model API. Send a text prompt and get an image back, refine it across turns, or edit an existing image. It uses the same base URL and auth as Muse Spark.

### At a glance {#muse-image-at-a-glance}

Everything you need to make your first image request.

|  |  |
| --- | --- |
| **Base URL** | `https://api.meta.ai/v1` |
| **Model** | `muse-image-1.0` |
| **Endpoints** | [`/v1/images/generations`](/docs/api-reference/images/create-image), [`/v1/images/edits`](/docs/api-reference/images/edit-image) |
| **Multi-turn editing** | [Responses API](/docs/protocols/responses) |
| **Output** | Image, as base64 or a signed URL |
| **Auth** | Bearer token (`MODEL_API_KEY`) |

Generate your first image and learn multi-turn editing in the [Image generation guide](/docs/image-generation).

## Build with Muse Voice Transcribe {#muse-voice-transcribe}

Muse Voice Transcribe brings speech-to-text to Meta Model API. Use it to transcribe live audio streams or supported audio files with one model that can detect speech turns, attribute speakers, and bias recognition toward your vocabulary.

### At a glance {#muse-voice-transcribe-at-a-glance}

|  |  |
| --- | --- |
| **Base URL** | `https://api.meta.ai/v1` |
| **Model** | `muse-voice-transcribe-1.0` |
| **Realtime endpoint** | `wss://api.meta.ai/v1/asr/realtime` |
| **File endpoint** | `POST /v1/asr/transcribe` |
| **Input** | Audio |
| **Output** | Transcript text with turn-level timing and optional speaker labels |
| **Pricing** | $0.18 per hour; see [Pricing and rate limits](/docs/pricing-rate-limits#muse-voice-transcribe-pricing) |

Muse Voice Transcribe is built for developers adding real-time speech to voice agents, meeting and call intelligence, live transcription, dictation, captioning, and high-volume transcription products.

It supports streaming speaker diarization, native endpointing and voice activity detection, contextual and keyword biasing, and 25 evaluated languages with code-switching. It returns turn-level timestamps, but not word-level timestamps. It is speech-to-text only; it does not synthesize speech or provide a speech-to-speech conversation API.

Start with the [Muse Voice Transcribe guide](/docs/speech-to-text).

## Build locally with Muse Glimmer {#muse-glimmer}

Muse Glimmer is Meta's open-weight multimodal model, distilled from Muse Spark and built to run on your own hardware. Unlike Muse Spark, Muse Image, and Muse Voice Transcribe, you don't call it over Model API - you download the weights and serve it through a runtime such as vLLM, SGLang, llama.cpp, or ExecuTorch.

Because it's self-hosted, Muse Glimmer has its own documentation section covering how to get the model, prompt it, deploy it, and customize it - rather than the API tiers and specs listed above.

- **[Muse Glimmer overview](/docs/muse-glimmer)**: variants, architecture, license, and launch partners.
- **[Get the model](/docs/muse-glimmer/get-the-model)**: download the weights and verify your setup.
- **[Run inference](/docs/muse-glimmer/deploy)**: pick a runtime and serve it locally.

## Explore the docs {#explore-the-docs}

Jump to the surface you need.

<tile-group col="3">
<tile color="elevated" icon="chain" href="/docs/quickstart" title="Quickstart"> Set your key, call the API, and read your first response.</tile>
<tile color="elevated" icon="chain" href="/docs/models" title="Models"> Muse Spark, Muse Image, Muse Voice Transcribe, and Muse Glimmer specs, plus pricing tiers.</tile>
<tile color="elevated" icon="chain" href="/docs/sdks" title="SDKs and libraries"> Official SDKs and the community libraries that work with Model API.</tile>
<tile color="elevated" icon="chain" href="/docs/cookbook" title="Cookbook"> Copy-paste recipes for primitives, agent loops, and use cases.</tile>
<tile color="elevated" icon="chain" href="/docs/pricing-rate-limits" title="Pricing and rate limits"> Per-token, per-image, and per-hour audio pricing, plus rate limits.</tile>
<tile color="elevated" icon="chain" href="/docs/api-reference" title="API reference"> Full request and response schemas for every endpoint.</tile>
</tile-group>

## Capabilities {#capabilities}

Muse Spark, Muse Image, and Muse Voice Transcribe ship production capabilities through Meta Model API. Each page explains the concept, shows code, and covers constraints. For the Muse Glimmer equivalents, see the [prompting guide](/docs/muse-glimmer/prompting).

<tile-group col="3">
<tile color="elevated" icon="chain" href="/docs/speech-to-text" title="Speech to text"> Transcribe streaming audio and supported files with Muse Voice Transcribe.</tile>
<tile color="elevated" icon="chain" href="/docs/tool-calling" title="Tool calling"> Connect the model to your APIs with parallel, streamed tool calls.</tile>
<tile color="elevated" icon="chain" href="/docs/tool-search" title="Tool search"> Discover and load deferred tools on demand to save tokens.</tile>
<tile color="elevated" icon="chain" href="/docs/search-grounding" title="Search grounding"> Real-time answers with inline citations, no retrieval stack to build.</tile>
<tile color="elevated" icon="chain" href="/docs/image-understanding" title="Image understanding"> Read photos, charts, documents, and screenshots.</tile>
<tile color="elevated" icon="chain" href="/docs/image-generation" title="Image generation"> Generate and edit images with Muse Image, and refine them turn by turn.</tile>
<tile color="elevated" icon="chain" href="/docs/video-understanding" title="Video understanding"> Summarize clips, ask questions about footage, and transcribe speech.</tile>
<tile color="elevated" icon="chain" href="/docs/file-handling" title="File handling"> Upload once and reference files by ID across requests.</tile>
<tile color="elevated" icon="chain" href="/docs/reasoning" title="Reasoning"> Dial reasoning effort up or down per request.</tile>
<tile color="elevated" icon="chain" href="/docs/structured-output" title="Structured output"> Return valid JSON that matches your schema every time.</tile>
<tile color="elevated" icon="chain" href="/docs/prompt-caching" title="Prompt caching"> Cache repeated prefixes to cut latency and cost.</tile>
<tile color="elevated" icon="chain" href="/docs/token-counting" title="Token counting"> Count input tokens before you send to estimate cost and fit context.</tile>
</tile-group>

## Protocols {#protocols}

Pick the request format your code already speaks: same models, same auth, same cost per token. These are Meta Model API surfaces; a local Muse Glimmer server exposes its own OpenAI-compatible endpoint through [vLLM](/docs/muse-glimmer/vllm) or [llama.cpp](/docs/muse-glimmer/llama-cpp). See [Choosing an API](/docs/protocols) to compare them.

<tile-group col="3">
<tile color="elevated" icon="chain" href="/docs/protocols/responses" title="Responses API"> Agentic, multi-step workloads with reasoning replay and server-managed state.</tile>
<tile color="elevated" icon="chain" href="/docs/protocols/chat-completions" title="Chat Completions API"> The OpenAI-compatible messages-array endpoint.</tile>
<tile color="elevated" icon="chain" href="/docs/protocols/messages" title="Messages API"> The Anthropic Messages-compatible endpoint.</tile>
</tile-group>

## Agent guides {#agent-guides}

Go deeper on building agents and integrations.

<tile-group col="3">
<tile color="elevated" icon="chain" href="/docs/coding-agents" title="Coding agents"> Wire Muse Spark into OpenCode, Codex, and other coding harnesses.</tile>
<tile color="elevated" icon="chain" href="/docs/agent-frameworks" title="Agent frameworks"> Build with LangChain, LlamaIndex, and the Vercel AI SDK.</tile>
<tile color="elevated" icon="chain" href="/docs/computer-use" title="Computer use"> Drive a desktop from screenshots with a computer-use agent.</tile>
</tile-group>

## Get unblocked {#get-unblocked}

Browse the [Help Center](/help) for accounts, API keys, billing, and rate-limit questions. For anything it doesn't cover, contact support through the Help Center.