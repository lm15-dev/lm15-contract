---
meta:
  title: Transcribe in realtime
  description: API reference for streaming transcription over a WebSocket at wss://api.meta.ai/v1/asr/realtime.
  keywords: audio, realtime transcription, streaming speech to text, WebSocket, wss, /asr/realtime, handshake, server events, close codes, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/voice/realtime
  target: aidmc
---

# Transcribe in realtime

Stream audio over a WebSocket and receive transcripts, turn boundaries, and speaker labels as the audio arrives.

Connect to `wss://api.meta.ai/v1/asr/realtime`, send the handshake as the first JSON text frame within 10 seconds, then stream raw PCM as binary frames. This endpoint does not read the HTTP `Authorization` header; the credential travels in the handshake. Send `{"type": "endStream"}` to end input and keep reading until the server closes with `1000`.

> [!NOTE]
> This is a WebSocket session. The request body below is the handshake frame, and the event stream is the ordered sequence of server frames that follows the acknowledgement.

<!-- Hand-hydrated. The fence below is what the openapi directive for POST /asr/realtime
     would emit once an ASR spec exists.
     Source of truth: fbcode/realtimeai/voyager/external/asr/duplex.thrift + PROTOCOL.md -->

```openapi-schema
method: POST
path: /asr/realtime
operation:
  operationId: transcribeRealtime
  tags:
    - Audio
  summary: Open a realtime transcription session.
  description: >-
    Initiates a WebSocket session for streaming transcription. The client sends the handshake as the
    first JSON text frame, then streams signed 16-bit little-endian mono PCM as binary frames paced at
    approximately real time. Frame boundaries carry no meaning and contain no container header,
    timestamp, sequence number, or end marker.
  parameters:
    - name: sessionId
      in: query
      required: false
      description: >-
        Correlation id used in server-side logs and returned in the handshake response. When omitted,
        the server generates one. It is supplied here rather than in the handshake so it is known
        before the handshake frame arrives.
      schema:
        type: string
  requestBody:
    required: true
    description: The handshake, sent as the first JSON text frame after the socket opens.
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/RealtimeHandshakeRequest'
  responses:
    '200':
      description: >-
        The handshake acknowledgement, followed by the ordered stream of server events. The
        acknowledgement is the only server frame with no `type` field.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/RealtimeHandshakeResponse'
        text/event-stream:
          schema:
            $ref: '#/components/schemas/ServerMessage'
components:
  schemas:
    Authorization:
      type: object
      description: >-
        Credential authorizing the session. Consumed only by the server's authentication step and
        never forwarded to the model.
      required:
        - accessToken
      properties:
        accessToken:
          type: string
          description: '`Bearer ` followed by your Model API key. The prefix is part of the value.'
    RealtimeHandshakeRequest:
      type: object
      description: >-
        The first JSON text frame the client sends to open a realtime session, within 10 seconds of
        the socket opening. Configuration is fixed once the handshake is accepted.
      required:
        - authorization
        - audioEncoding
        - model
      properties:
        authorization:
          $ref: '#/components/schemas/Authorization'
        audioEncoding:
          type: string
          enum:
            - PCM_24KHZ
            - PCM_16KHZ
          description: >-
            Encoding of the streamed binary frames, sent as the enum name. Both values are signed
            16-bit little-endian mono. `PCM_24KHZ` is 48,000 bytes per second and is the model's
            native rate; `PCM_16KHZ` is 32,000 bytes per second and is resampled server-side. There is
            no default; an unset or unrecognized value is rejected.
        model:
          type: string
          description: Public model id. The model must support the requested mode.
        mode:
          type: string
          enum:
            - PUSH_TO_TALK
            - ENDPOINTING
            - DIARIZATION
          default: PUSH_TO_TALK
          description: >-
            Transcription behavior, sent as the enum name. `PUSH_TO_TALK` is single-turn and the
            client delimits the turn by ending the stream. `ENDPOINTING` detects speech onset and
            endpoint, one turn per detected segment. `DIARIZATION` additionally attributes turns to
            speakers. Mode availability depends on the model.
        partialMode:
          type: string
          enum:
            - CUMULATIVE
            - DELTA
          default: CUMULATIVE
          description: >-
            Representation of partial transcript text, sent as the enum name. `CUMULATIVE` sends the
            complete current hypothesis each time, replacing the previous partial, so the model can
            revise text it already emitted. `DELTA` sends only newly emitted text for the client to
            append, and is not compatible with every model or mode.
        emitAudioProgress:
          type: boolean
          default: true
          description: >-
            Whether the server emits `audioProgress` events. Compatible runtimes emit one event per
            processed audio chunk.
        keywords:
          type: array
          items:
            type: string
          description: >-
            Terms to bias recognition toward, such as names, jargon, and product words the model would
            otherwise mishear. Biasing does not guarantee an exact spelling.
        languageBias:
          type: array
          items:
            type: string
          description: >-
            Languages to bias transcription toward, each as a language name, e.g. `["English",
            "French"]`. A list of languages, not free-form context. Omit it to let the model detect
            the language.
        zdrOverride:
          type: boolean
          description: >-
            Overrides the Zero Data Retention policy for this session. `true` forces metadata-only
            logging; `false` allows content retention. When unset, the authenticated caller's policy
            applies.
page_linked_schemas:
  AudioProgressEvent: /docs/api-reference/voice/schemas#audio-progress-event
  ErrorEvent: /docs/api-reference/voice/schemas#error-event
  RealtimeHandshakeResponse: /docs/api-reference/voice/schemas#realtime-handshake-response
  ServerMessage: /docs/api-reference/voice/schemas#server-message
  SpeakerEvent: /docs/api-reference/voice/schemas#speaker-event
  SpeechCompleteEvent: /docs/api-reference/voice/schemas#speech-complete-event
  SpeechEndEvent: /docs/api-reference/voice/schemas#speech-end-event
  SpeechStartEvent: /docs/api-reference/voice/schemas#speech-start-event
  TranscriptEvent: /docs/api-reference/voice/schemas#transcript-event
```

```python title="Python (websockets)"
import asyncio
import json
import os
import uuid

import websockets

API_KEY = os.environ["MODEL_API_KEY"]

SESSION_ID = f"stream-{uuid.uuid4()}"
ASR_URI = f"wss://api.meta.ai/v1/asr/realtime?sessionId={SESSION_ID}"

# 16-bit little-endian mono PCM at 24 kHz, paced ~real time (80 ms per frame).
RATE = 24_000
FRAME_BYTES = RATE * 2 * 80 // 1000

async def transcribe_stream() -> None:
    async with websockets.connect(ASR_URI, open_timeout=30) as ws:
        # 1. Handshake: the first JSON text frame. The credential travels here,
        #    not in the Authorization header.
        await ws.send(
            json.dumps(
                {
                    "authorization": {"accessToken": f"Bearer {API_KEY}"},
                    "audioEncoding": "PCM_24KHZ",
                    "model": "muse-voice-transcribe-1.0",
                    "mode": "PUSH_TO_TALK",
                }
            )
        )
        handshake = json.loads(await ws.recv())
        if "sessionId" not in handshake:
            raise RuntimeError(f"Handshake failed: {handshake}")

        # 2. Read server events until the socket closes with 1000.
        async def receive_events() -> None:
            async for message in ws:
                if isinstance(message, bytes):
                    continue
                event = json.loads(message)
                if event.get("type") == "error":
                    raise RuntimeError(event["message"])
                if event.get("type") == "transcript":
                    end = "\n" if event.get("final") else "\r"
                    print(event["transcript"], end=end, flush=True)

        receiver = asyncio.create_task(receive_events())

        # 3. Stream raw PCM binary frames.
        with open("recording.pcm", "rb") as audio:
            while chunk := audio.read(FRAME_BYTES):
                await ws.send(chunk)
                await asyncio.sleep(0.08)

        # 4. Half-close input and keep reading until the server closes.
        await ws.send(json.dumps({"type": "endStream"}))
        await receiver

asyncio.run(transcribe_stream())
```


<!-- openapi-schemas-page: /docs/api-reference/voice/schemas -->

## Client frames {#client-frames}

Audio is sent as binary frames. The only client text frame after the handshake is the end-of-input marker, which half-closes the client-to-server direction and leaves the socket open so the server can flush pending results. Closing the socket instead also ends input, but can discard pending events.

```json title="JSON"
{ "type": "endStream" }
```

## Close codes {#close-codes}

| Code | Meaning | What to do |
|------|---------|------------|
| `1000` | Normal completion | Finish after consuming the final result. |
| `1008` | Invalid request, or a streaming-policy failure such as backlog or below-real-time ingress | Correct the configuration or the audio pacing. Retrying the same request fails again. |
| `1011` | Internal or backend failure | Retry with backoff. When the reason is `Max session duration reached`, open a new session. |
| `1013` | Rate limited | Back off before reconnecting. |

For modes, endpointing, diarization, session limits, and worked examples, see the [Speech to text](/docs/speech-to-text) feature page.