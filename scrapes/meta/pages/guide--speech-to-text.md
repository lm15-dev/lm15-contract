---
meta:
  title: Speech to text
  description: Transcribe live audio or supported files with Muse Voice Transcribe on Meta Model API.
  keywords: Muse Voice Transcribe, speech to text, transcription, streaming, WebSocket, diarization, endpointing, voice activity detection
cms:
  alias: /model-api/docs/speech-to-text
  target: aidmc
---

# Speech to text

[Muse Voice Transcribe](/docs/models#muse-voice-transcribe) is Meta's speech-to-text model on Meta Model API. Transcribe live audio or an existing recording, with speech-turn detection, speaker labels, and vocabulary biasing.

## Available endpoints {#endpoints}

Both endpoints run the same model.

| Endpoint | Use it for | How you connect |
|---|---|---|
| `wss://api.meta.ai/v1/asr/realtime` | Live audio: voice agents, dictation, captions | WebSocket. Authenticate in the handshake frame; the `Authorization` header is ignored. |
| `POST https://api.meta.ai/v1/asr/transcribe` | A recording you already have | Multipart upload. Authenticate with the `Authorization` header. |

See the [Voice API reference](/docs/api-reference/voice) for full request and response schemas.

## Features {#features}

| Feature | What you get |
|---|---|
| [Language biasing](#language-biasing) | 25 supported languages with code-switching, plus a hint to steer recognition toward the languages you expect |
| [Vocabulary biasing](#keywords) | Better recognition of product names, people, places, acronyms, and domain terms |
| [Speech-turn detection](#endpointing) | One completed transcript per utterance without running your own voice activity detection |
| [Speaker labels](#diarization) | Speaker attribution such as `A` and `B` for multi-speaker audio |
| [Partial transcripts](#partials-and-finals) | Text that updates while a speaker is talking |
| [Progress events](#audio-progress) | A running count of audio processed, for progress indicators and to confirm a long session is still alive |

> [!NOTE]
> Muse Voice Transcribe returns turn-level timestamps, not word-level timestamps. Word-level timestamps, confidence scores, sound event detection, emotion detection, and transcript reformatting are not available.

## Modes {#modes}

Set `mode` in the handshake or the `transcribe` request. On `realtime`, it is fixed for a session once it starts.

| Mode | What you get |
|---|---|
| `PUSH_TO_TALK` (default) | Single-turn transcription. You delimit the turn — for example, by pressing a mic button — as in a voice command, dictation, or a controlled recording. |
| [`ENDPOINTING`](#endpointing) | Model-detected turn boundaries, one turn per detected speech segment. |
| [`DIARIZATION`](#diarization) | Automatic speaker detection and attribution. |

## Detect speech turns with endpointing {#endpointing}

`ENDPOINTING` makes the model find the edges of each utterance. Both endpoints follow the same turn-detection pattern: on `realtime`, and on `transcribe` when you [request an event stream](#transcribe-accept), the turns arrive as events while the audio is processed; otherwise `transcribe` returns them in a [`turns` array](#transcribe-response) in the JSON response.

Each event is named by its `type` field:

| The model... | sends |
|---|---|
| hears speech begin | `speechStart` |
| recognizes words as they arrive | `transcript`, repeatedly |
| hears speech stop | `speechEnd` |
| finishes cleaning up the turn | `speechComplete` |

A single turn looks like this on the wire:

```json
{"type":"speechStart","turnId":1,"audioProcessedMs":1200}
{"type":"transcript","transcript":"how is the","final":false,"audioProcessedMs":2400}
{"type":"transcript","transcript":"how is the weather","final":false,"audioProcessedMs":3200}
{"type":"speechEnd","turnId":1,"audioProcessedMs":3600}
{"type":"speechComplete","turnId":1,"transcript":"How is the weather?","audioProcessedMs":3600}
```

Every event and its fields are listed under [`ServerMessage`](/docs/api-reference/voice/schemas#server-message).

Three things to build around:

- **`speechEnd` is not the transcript.** It marks the boundary. The text arrives in `speechComplete`, and the model may post-process the turn in between, so it can differ from the last [partial](#partials-and-finals). Note the added punctuation and capitalization above.
- **Turns can overlap.** A later turn can open before an earlier turn's `speechComplete` arrives, so key your state on `turnId` rather than assuming order.
- **Partials carry no `turnId`.** A `transcript` event belongs to the turn opened by the most recent `speechStart`.

## Label speakers with diarization {#diarization}

`DIARIZATION` works out who is speaking, so a multi-speaker recording comes back attributed rather than as one run of text.

It marks a possible new speaker rather than a clean speech endpoint, so it is **not tuned for low-latency, voice-command use** — use [`ENDPOINTING`](#endpointing) for that. It builds on the same events and adds [`speaker`](/docs/api-reference/voice/schemas#speaker-event) events while a turn is active:

```json
{"type":"speechStart","turnId":1,"audioProcessedMs":1200}
{"type":"transcript","transcript":"thanks for calling","final":false,"audioProcessedMs":2400}
{"type":"speaker","label":"A","audioProcessedMs":2480}
{"type":"transcript","transcript":"thanks for calling how can i help","final":false,"audioProcessedMs":3400}
{"type":"speaker","label":"A","audioProcessedMs":3520}
{"type":"speechEnd","turnId":1,"audioProcessedMs":3600}
{"type":"speechComplete","turnId":1,"transcript":"Thanks for calling. How can I help?","audioProcessedMs":3600}
```

A `speaker` event labels the audio *behind* it: the span runs from the previous `speechStart` or `speaker` event, whichever came later, up to this one.

A `speaker` event does not indicate a speech boundary, a speaker change, or a final transcript. Across a session the model can emit the same label more than once; within a single turn there is exactly one `speaker` event. You can merge consecutive spans that use the same label.

Treat labels such as `A` and `B` as session-scoped identifiers. They are not verified names, and a label does not identify the same person across separate sessions.

## Language biasing {#language-biasing}

Muse Voice Transcribe supports 25 languages with code-switching:

Arabic, Bengali, Dutch, English, French, German, Hebrew, Hindi, Indonesian, Italian, Japanese, Kannada, Korean, Malay, Mandarin Chinese, Marathi, Polish, Portuguese, Spanish, Tagalog, Tamil, Telugu, Thai, Turkish, and Vietnamese.

`languageBias` tells the model which language or languages to expect before it hears the audio. It is a list of languages, not free-form context:

```json
{ "languageBias": ["English", "French"] }
```

A hint steers recognition toward those languages; it does not force the model to use them. Omit it and the model detects the language on its own. To bias toward specific words, use `keywords`.

## Bias toward your own vocabulary {#keywords}

Set `keywords` for product names, people, places, acronyms, and other terms the model might mishear.

```json
{ "keywords": ["Acme Mobile", "eSIM", "5G"] }
```

Keywords bias recognition but do not guarantee an exact spelling.

Set both `languageBias` and `keywords` when you start: in the handshake for `realtime`, or in the `request` part for `transcribe`. Neither can change once a session is running.

## Quickstart {#quickstart}

### Transcribe a microphone {#quickstart-mic}

Before you begin:

1. Create a key in the [Model API dashboard](/). Copy the key when it is shown.
2. Install Python 3.9 or later, then run `python -m pip install websockets sounddevice`.
3. Export your key and the Muse Voice Transcribe model ID:

```bash
export MODEL_API_KEY="<your-api-key>"
export ASR_MODEL="muse-voice-transcribe-1.0"
```

This example records ten seconds from your default microphone, sends `endStream`, and waits for the transcript.

The `sessionId` query parameter is optional on both endpoints: supply one to correlate with your logs, or omit it and the server generates one.

```python
import asyncio
import json
import os
import sys
import uuid

import sounddevice as sd
import websockets

API_KEY = os.environ["MODEL_API_KEY"]
MODEL = os.environ["ASR_MODEL"]

SESSION_ID = f"mic-{uuid.uuid4()}"
ASR_URI = f"wss://api.meta.ai/v1/asr/realtime?sessionId={SESSION_ID}"

RATE = 24_000
FRAME_SAMPLES = RATE * 80 // 1000
RECORD_SECONDS = 10

async def transcribe_mic() -> None:
    async with websockets.connect(ASR_URI, open_timeout=30) as ws:
        await ws.send(
            json.dumps(
                {
                    "authorization": {"accessToken": f"Bearer {API_KEY}"},
                    "audioEncoding": "PCM_24KHZ",
                    "model": MODEL,
                    "mode": "PUSH_TO_TALK",
                    "partialMode": "CUMULATIVE",
                    "emitAudioProgress": False,
                }
            )
        )

        handshake = json.loads(await ws.recv())
        if "sessionId" not in handshake:
            raise RuntimeError(f"Handshake failed: {handshake}")
        print(f"Session: {handshake['sessionId']}")
        print(f"Speak for {RECORD_SECONDS} seconds...")

        loop = asyncio.get_running_loop()
        audio_queue: asyncio.Queue[bytes] = asyncio.Queue()

        def on_audio(indata, frames, time_info, status):
            if status:
                print(status, file=sys.stderr)
            loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

        async def receive_events() -> None:
            previous_length = 0
            async for message in ws:
                if isinstance(message, bytes):
                    continue

                event = json.loads(message)
                if event.get("type") == "error":
                    raise RuntimeError(event["message"])
                if event.get("type") != "transcript":
                    continue

                transcript = event["transcript"]
                padding = " " * max(0, previous_length - len(transcript))
                end = "\n" if event.get("final") else "\r"
                print(f"{transcript}{padding}", end=end, flush=True)
                previous_length = len(transcript)

        receiver = asyncio.create_task(receive_events())

        with sd.RawInputStream(
            samplerate=RATE,
            channels=1,
            dtype="int16",
            blocksize=FRAME_SAMPLES,
            callback=on_audio,
        ):
            deadline = loop.time() + RECORD_SECONDS
            while loop.time() < deadline:
                await ws.send(await audio_queue.get())

        while not audio_queue.empty():
            await ws.send(audio_queue.get_nowait())

        await ws.send(json.dumps({"type": "endStream"}))
        await receiver

asyncio.run(transcribe_mic())
```

The first JSON text frame configures the session. See [the handshake](#connect) for every field, or the [API reference](/docs/api-reference/voice/realtime) for full types and defaults.

Each partial replaces the previous one, so the example rewrites the terminal line instead of appending. The server closes the socket after the completed transcript.

### Transcribe a file {#quickstart-file}

Send a supported WAV file and receive the transcript in one HTTP request.

```text
POST /v1/asr/transcribe?sessionId=<your-id>
```

#### Convert your audio file first {#convert-audio}

The endpoint accepts a RIFF/WAVE container with mono, 16-bit integer PCM at 16 kHz or 24 kHz. Convert other formats before uploading them:

```bash
ffmpeg -i input.m4a -ac 1 -ar 24000 -c:a pcm_s16le -map_metadata -1 output.wav
```

- `-c:a pcm_s16le` writes 16-bit integer PCM.
- `-ac 1` converts the audio to mono.
- `-ar 24000` uses the model's native sample rate.
- `-map_metadata -1` removes metadata and embedded artwork.

#### Send the request {#transcribe-request}

Send a `multipart/form-data` request with two parts:

- `request`: the transcription settings as JSON.
- `audio`: the WAV file.

The default response is JSON:

```bash
curl --fail-with-body \
  'https://api.meta.ai/v1/asr/transcribe?sessionId=my-session-id' \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -F 'request={"mode":"DIARIZATION","model":"muse-voice-transcribe-1.0","audioEncoding":"WAV"};type=application/json' \
  -F 'audio=@meeting_audio.wav'
```

The `request` part takes the same settings as the [handshake](#connect), minus `authorization` and `zdrOverride`. See the [API reference](/docs/api-reference/voice/transcribe) for full types and defaults.

`partialMode` and `emitAudioProgress` affect [`text/event-stream` responses](#transcribe-accept) only.

#### Read the response {#transcribe-response}

```json
{
  "sessionId": "9f1c...",
  "transcript": "How is the weather? It is raining.",
  "audioDurationMs": 8240,
  "turns": [
    {
      "turnId": 1,
      "startMs": 1520,
      "endMs": 4640,
      "transcript": "How is the weather?",
      "speaker": "A"
    },
    {
      "turnId": 2,
      "startMs": 5900,
      "endMs": 8240,
      "transcript": "It is raining.",
      "speaker": "B"
    }
  ]
}
```

- `transcript`: the complete transcript, in every mode.
- `turns`: detected speech turns in `ENDPOINTING` and `DIARIZATION`; empty in `PUSH_TO_TALK`. See [`Turn`](/docs/api-reference/voice/schemas#turn) for the full shape.
- `speaker`: `DIARIZATION` only. Labels identify speakers within this transcription.
- `startMs`, `endMs`: turn boundaries. Word-level timestamps are not available.

#### Choose another response format {#transcribe-accept}

Set the `Accept` header when you do not want the default JSON response:

| `Accept` | Response |
|---|---|
| `application/json`, `*/*`, or absent | One JSON response with the complete transcript |
| `text/event-stream` | Server-sent events matching the `realtime` server-event format |
| `text/plain` | Plain text; one turn per line in `ENDPOINTING`, or lines such as `A:Hello` in `DIARIZATION` |

Set the header on the request. The stream ends after the last event, with no JSON summary appended:

```bash
curl --fail-with-body -N \
  'https://api.meta.ai/v1/asr/transcribe?sessionId=my-session-id' \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H 'Accept: text/event-stream' \
  -F 'request={"mode":"ENDPOINTING","model":"muse-voice-transcribe-1.0","audioEncoding":"WAV"};type=application/json' \
  -F 'audio=@meeting_audio.wav'
```

Events match the `realtime` format:

```text
event: transcript
data: {"type":"transcript","transcript":"How is the weather","final":false,"audioProcessedMs":2400}

event: speechComplete
data: {"type":"speechComplete","turnId":1,"transcript":"How is the weather?","audioProcessedMs":4640}
```

An unsupported `Accept` value returns `406`.

#### Stay under the size caps {#transcribe-limits}

| Condition | Response | What to do |
|---|---|---|
| Request body exceeds 32 MB | `413` | Upload a smaller file or split it into shorter clips. |
| Audio exceeds 10 minutes | `400` | Split the recording into clips of 10 minutes or less. |
| Audio is not a supported WAV file | `400` | Convert it to mono, 16-bit PCM WAV at 16 kHz or 24 kHz. |
| Tenant rate or concurrency limit is reached | `429` | Retry with exponential backoff. |
| Processing exceeds the server budget | `500`, or a terminal `error` SSE event | Retry once. If it fails again, contact support with the session ID. |

## What you can build {#what-you-can-build}

- **[Voice agents](#quickstart-mic)**: stream live audio, receive partial transcripts, and use model-detected turn boundaries to decide when a speaker has finished.
- **[Meeting and call intelligence](#diarization)**: transcribe multi-speaker conversations with speaker labels and turn-level timestamps.
- **[Live transcription, dictation, and captions](#modes)**: convert speech to text while audio is still arriving.
- **[File transcription](#quickstart-file)**: send a supported audio file and receive a complete transcript in one HTTP request.

## Migrate a realtime integration {#migrate}

If you already stream to another provider, keep your capture architecture and adapt the transport:

- **Open one WebSocket.** Connect to `/v1/asr/realtime` and send the handshake as the first JSON text frame.
- **Authenticate in the handshake.** Put `Bearer ` followed by your Model API key in `authorization.accessToken`. Do not send an HTTP `Authorization` header for the WebSocket endpoint.
- **Send raw PCM frames.** Use signed 16-bit little-endian mono audio at 24 kHz or 16 kHz. Decode WAV, MP3, Opus, or other containers before streaming.
- **Pace audio in real time.** Do not upload buffered audio as quickly as the network allows. The server rejects streams that run too far ahead or remain slower than real time.
- **Replace cumulative partials.** With `CUMULATIVE`, each partial supersedes the previous partial for the active turn. Do not append it.
- **Choose a completion event.** Use `final: true` in `PUSH_TO_TALK`. Use `speechComplete` and its `turnId` in `ENDPOINTING` and `DIARIZATION`.
- **Let the model detect turns.** `realtime` has no client-side turn commit. `endStream` ends the complete session, not one turn.
- **End input explicitly.** Drain queued audio, send `{"type": "endStream"}`, and send nothing more — this closes the client-to-server direction. Keep reading until the server closes with `1000`.
- **Reconnect before the max session duration.** A realtime session runs for up to 60 minutes. A new WebSocket creates a new session, and the API has no resume token, so join transcripts in your application.
- **Ignore unknown event types.** This keeps your client compatible with future additive server events.

Use the [close codes](#close-codes) to decide whether to fix the request, retry with backoff, or finish normally.

## Pricing {#availability-pricing}

Pricing is `$0.18 per hour` of audio processed. Streaming and non-streaming transcription are priced the same, and ZDR is priced at parity with Standard. Platform free-tier credits apply.

You are billed for the audio the transcription engine actually processed, rounded down to whole seconds — a 30.4-second recording is billed as 30 seconds. Requests that fail before producing a transcript, and rate-limited (`429`) requests, are not billed.

## Advanced {#advanced}

Wire-level detail for hardening an integration, debugging a dropped session, or writing a client from scratch.

### Connect and authenticate {#connect}

Served at `api.meta.ai`, the same host as Meta Model API.

```text
wss://api.meta.ai/v1/asr/realtime?sessionId=<your-id>
```

`sessionId` is optional; the server generates one if you omit it and returns it in the handshake response.

Send the handshake as the first JSON text frame, within 10 seconds of connecting. Put `Bearer ` followed by your Model API key in `authorization.accessToken`. `realtime` does not read an HTTP `Authorization` header or API-key query parameter.

The nine handshake fields, with types, allowed values, and defaults, are in the [API reference](/docs/api-reference/voice/realtime).

The server responds with a handshake acknowledgement:

```json
{ "sessionId": "550e8400-e29b-41d4-a716-446655440000" }
```

This acknowledgement has no `type` field. Every later server JSON frame has a `type`.

### Send audio {#audio-format}

Send raw pulse-code modulation (PCM) audio: signed 16-bit little-endian, mono.

- `PCM_24KHZ`: 24 kHz and 48,000 bytes per second. Prefer this engine-native rate.
- `PCM_16KHZ`: 16 kHz and 32,000 bytes per second. The server resamples it.

Audio goes in binary frames; the handshake, control messages, and events go in JSON text frames.

Frame boundaries carry no meaning: no container header, timestamp, sequence number, or end marker. Pace frames at approximately real time.

### Read partials and finals {#partials-and-finals}

While someone is still speaking, the model emits interim `transcript` events, called partials, so you can show text as it arrives instead of waiting for the turn to end. `partialMode` controls what each partial contains. Set it in the `realtime` handshake or the `transcribe` request:

- **CUMULATIVE** is the default. Each `transcript` event contains the complete current hypothesis. Replace the previous partial instead of concatenating it. A new partial can revise or remove earlier text.
- **DELTA** contains new per-chunk text. Use it with `/v1/asr/transcribe` and `Accept: text/event-stream`.

Completion depends on the mode:

| Mode | Completion signal |
|---|---|
| `PUSH_TO_TALK` | A `transcript` event with `final: true` |
| `ENDPOINTING` | A `speechComplete` event for each `turnId` |
| `DIARIZATION` | A `speechComplete` event for each `turnId` |

In `DELTA` mode, the `final: true` event contains the complete transcript rather than one final increment.

### Manage the session lifecycle {#session-lifecycle}

1. **Connect** to `wss://api.meta.ai/v1/asr/realtime?sessionId=<id>`.
2. **Send the handshake** as the first JSON text frame, within 10 seconds.
3. **Wait for the handshake acknowledgement** before sending audio.
4. **Stream audio** as binary frames paced at real time.
5. **End input** by draining the outbound queue and sending `{"type": "endStream"}`. Send no further events after this — it closes the client-to-server stream.
6. **Keep reading** while the server emits pending results.
7. **Finish** when the server closes with `1000`.

`endStream` marks end of input and leaves the socket open so the server can flush pending results. Closing the socket also ends input, but can discard pending events. A detected end of speech does not end the session.

### Track audio progress {#audio-progress}

With `emitAudioProgress` on (the default), the server sends `audioProgress` with `audioProcessedMs` as it consumes audio, independent of speech and turn state. Set it to `false` if you do not need them.

Treat `audioProcessedMs` as processing progress, not a word timestamp.

### Keep the session alive {#limits}

The server checks these conditions once a second:

- **Handshake deadline**: send the handshake within 10 seconds of connecting.
- **Session length**: reconnect before the max session duration. The `realtime` default is 60 minutes.
- **Backlog**: do not send audio more than five seconds ahead of processing.
- **Pacing**: send audio at approximately real-time speed. If a live source remains connected during silence, continue sending PCM silence.
- **Idle input**: the server closes a stream that stops sending audio without sending `endStream`.
- **Idle output**: the server closes a session if output stalls after end-of-input.

### Work within the rate limits {#rate-limits}

Two per-tenant dimensions: concurrent open streams, and streams started per hour.

| | Limit |
|---|---|
| Concurrent streams | 8 |
| Streams per hour | 1,000 |

Both endpoints use the same budget. A rejected `realtime` stream closes with [`1013`](/docs/api-reference/voice/realtime#close-codes). A rejected `transcribe` request returns `429`. Back off before retrying.

### Read the error event {#error-event}

Before a fatal close, the server sends an `error` event when the connection still permits it:

```json
{ "type": "error", "message": "human-readable message", "sessionId": "<id>" }
```

Log the message with the session ID. Use the close code to decide whether to retry. See [`ErrorEvent`](/docs/api-reference/voice/schemas#error-event) for the field list.

### Handle close codes {#close-codes}

Every session ends with a WebSocket close code that tells you whether to retry, fix the request, or stop. Retain the session ID either way. See [close codes](/docs/api-reference/voice/realtime#close-codes) for the full list.