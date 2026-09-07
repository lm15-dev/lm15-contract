---
meta:
  title: Transcribe a recording
  description: API reference for transcribing an audio file with POST /v1/asr/transcribe.
  keywords: audio, transcribe, file transcription, speech to text, POST /asr/transcribe, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/voice/transcribe
  target: aidmc
---

# Transcribe a recording

Transcribe one complete audio recording in a single request.

Send `multipart/form-data` with two parts: `request`, the transcription settings as JSON, and `audio`, the clip. The `Accept` header selects between a buffered JSON body, a server-sent event stream, and plain text.

<!-- Hand-hydrated. The fence below is what the openapi directive for POST /asr/transcribe
     would emit once an ASR spec exists.
     Source of truth: fbcode/realtimeai/voyager/external/asr/transcribe.thrift + duplex.thrift -->

```openapi-schema
method: POST
path: /asr/transcribe
operation:
  operationId: transcribeRecording
  tags:
    - Audio
  summary: Transcribe a complete audio recording.
  parameters:
    - name: sessionId
      in: query
      required: false
      description: >-
        Correlation id used in server-side logs and echoed in the response. When omitted, the server
        generates one.
      schema:
        type: string
  requestBody:
    required: true
    content:
      multipart/form-data:
        schema:
          type: object
          required:
            - request
            - audio
          properties:
            request:
              $ref: '#/components/schemas/TranscribeRequest'
            audio:
              type: string
              format: binary
              description: >-
                A RIFF/WAVE container holding mono 16-bit integer PCM at 16 kHz or 24 kHz. Convert other
                formats before uploading. Maximum 32 MB and 10 minutes of audio.
  responses:
    '200':
      description: >-
        The transcript, in the shape selected by `Accept`. `application/json`, `*/*`, or an absent
        header returns the buffered body. `text/event-stream` returns the realtime event stream, which
        ends after the last event and appends no summary. `text/plain` returns one turn per line in
        `ENDPOINTING`, or lines of the form `A:Hello` in `DIARIZATION`.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TranscribeResponse'
        text/event-stream:
          schema:
            $ref: '#/components/schemas/ServerMessage'
    '400':
      description: >-
        The audio is not a supported WAV file, the audio exceeds 10 minutes, or the body is not
        `multipart/form-data`.
    '406':
      description: The `Accept` header requested a media type this endpoint does not produce.
    '413':
      description: The request body exceeds the maximum of 32 MB.
    '429':
      description: >-
        The caller reached its concurrency or hourly session limit. Retry with exponential backoff.
    '500':
      description: >-
        Transcription failed, or processing exceeded the server budget. Once an event stream has
        started there is no status left to set, so the failure arrives as a terminal `error` event on
        the open stream under `HTTP 200`.
components:
  schemas:
    TranscribeRequest:
      type: object
      description: The `request` part of the multipart body, sent as JSON.
      required:
        - model
        - audioEncoding
      properties:
        model:
          type: string
          description: Public model id. The model must support the requested mode.
        audioEncoding:
          type: string
          enum:
            - WAV
          description: >-
            Container of the uploaded `audio` part, sent as the enum name. `WAV` is a RIFF/WAVE
            container holding mono integer PCM at 16 kHz or 24 kHz. There is no default; an unset or
            unrecognized value is rejected.
        mode:
          type: string
          enum:
            - PUSH_TO_TALK
            - ENDPOINTING
            - DIARIZATION
          default: PUSH_TO_TALK
          description: >-
            Transcription behavior, sent as the enum name. `PUSH_TO_TALK` is single-turn and the
            uploaded clip is the turn. `ENDPOINTING` detects speech onset and endpoint, one turn per
            detected segment. `DIARIZATION` additionally attributes turns to speakers. Mode
            availability depends on the model.
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
        partialMode:
          type: string
          enum:
            - CUMULATIVE
            - DELTA
          default: CUMULATIVE
          description: >-
            Representation of partial transcript text, sent as the enum name. Applies to
            `text/event-stream` responses only. `CUMULATIVE` replaces the previous partial; `DELTA`
            sends only newly emitted text for the client to append.
        emitAudioProgress:
          type: boolean
          default: true
          description: >-
            Whether to emit `audioProgress` events. Applies to `text/event-stream` responses only; the
            buffered responses never surface them.
page_linked_schemas:
  AudioProgressEvent: /docs/api-reference/voice/schemas#audio-progress-event
  ErrorEvent: /docs/api-reference/voice/schemas#error-event
  ServerMessage: /docs/api-reference/voice/schemas#server-message
  SpeakerEvent: /docs/api-reference/voice/schemas#speaker-event
  SpeechCompleteEvent: /docs/api-reference/voice/schemas#speech-complete-event
  SpeechEndEvent: /docs/api-reference/voice/schemas#speech-end-event
  SpeechStartEvent: /docs/api-reference/voice/schemas#speech-start-event
  TranscribeResponse: /docs/api-reference/voice/schemas#transcribe-response
  TranscriptEvent: /docs/api-reference/voice/schemas#transcript-event
  Turn: /docs/api-reference/voice/schemas#turn
```

```shell title="curl"
curl -X POST "https://api.meta.ai/v1/asr/transcribe" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Accept: application/json" \
  -F 'request={"model":"muse-voice-transcribe-1.0","audioEncoding":"WAV","mode":"PUSH_TO_TALK"};type=application/json' \
  -F "audio=@recording.wav;type=audio/wav"
```
```python title="Python (requests)"
import json
import os

import requests

with open("recording.wav", "rb") as audio:
    response = requests.post(
        "https://api.meta.ai/v1/asr/transcribe",
        headers={
            "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
            "Accept": "application/json",
        },
        files={
            "request": (
                None,
                json.dumps(
                    {
                        "model": "muse-voice-transcribe-1.0",
                        "audioEncoding": "WAV",
                        "mode": "PUSH_TO_TALK",
                    }
                ),
                "application/json",
            ),
            "audio": ("recording.wav", audio, "audio/wav"),
        },
    )
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```


<!-- openapi-schemas-page: /docs/api-reference/voice/schemas -->

Errors carry an HTTP status and a single client-safe message, with no `type`, `param`, or `code` field. Retain the session id: it is the only correlation handle for a support request.

For audio conversion, modes, and worked examples, see the [Speech to text](/docs/speech-to-text) feature page.