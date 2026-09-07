---
meta:
  title: Voice schemas
  description: Full schema and model definitions referenced by the Audio API endpoints.
  keywords: audio, schemas, models, types, API reference, schema reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/voice/schemas
  target: aidmc
---

# Voice schemas

The full schema and model definitions referenced by the [Audio](/docs/api-reference/voice/transcribe) endpoints. Each endpoint page links here for the detailed shape of its request and response objects.

## Schemas

<!-- Hand-hydrated. The fences below are what the openapi-schemas-for directive scoped to
     /asr would emit once an ASR spec exists.
     Source of truth: fbcode/realtimeai/voyager/external/asr/duplex.thrift + transcribe.thrift -->

```openapi-schema
kind: schema
name: AudioProgressEvent
schema:
  type: object
  description: >-
    One update on the independent audio-progress channel, multiplexed onto the same ordered event
    stream as transcript, lifecycle, and speaker events. Not part of any speech turn.
  required:
    - type
    - audioProcessedMs
  properties:
    type:
      type: string
      enum:
        - audioProgress
    audioProcessedMs:
      type: integer
      format: int64
      description: Total audio processed so far, in milliseconds from the start of the stream.
components:
  schemas: {}
page_linked_schemas:
  AudioProgressEvent: '#audio-progress-event'
```

```openapi-schema
kind: schema
name: Authorization
schema:
  type: object
  description: >-
    Credential authorizing the session. Consumed only by the server's authentication step and never
    forwarded to the model.
  required:
    - accessToken
  properties:
    accessToken:
      type: string
      description: '`Bearer ` followed by your Model API key. The prefix is part of the value.'
components:
  schemas: {}
page_linked_schemas:
  Authorization: '#authorization'
```

```openapi-schema
kind: schema
name: ErrorEvent
schema:
  type: object
  description: >-
    Fatal error the server sends just before it closes the session. The message is client-safe;
    internal detail is logged server-side only.
  required:
    - type
    - message
    - sessionId
  properties:
    type:
      type: string
      enum:
        - error
    message:
      type: string
      description: Human-readable, client-safe error message.
    sessionId:
      type: string
      description: Session id for log correlation. Empty if one has not been assigned yet.
components:
  schemas: {}
page_linked_schemas:
  ErrorEvent: '#error-event'
```

```openapi-schema
kind: schema
name: RealtimeHandshakeRequest
schema:
  type: object
  description: >-
    The first JSON text frame the client sends to open a realtime session, within 10 seconds of the
    socket opening. Configuration is fixed once the handshake is accepted.
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
        Encoding of the streamed binary frames, sent as the enum name. Both values are signed 16-bit
        little-endian mono. `PCM_24KHZ` is 48,000 bytes per second and is the model's native rate;
        `PCM_16KHZ` is 32,000 bytes per second and is resampled server-side. There is no default; an
        unset or unrecognized value is rejected.
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
        Transcription behavior, sent as the enum name. `PUSH_TO_TALK` is single-turn and the client
        delimits the turn by ending the stream. `ENDPOINTING` detects speech onset and endpoint, one
        turn per detected segment. `DIARIZATION` additionally attributes turns to speakers. Mode
        availability depends on the model.
    partialMode:
      type: string
      enum:
        - CUMULATIVE
        - DELTA
      default: CUMULATIVE
      description: >-
        Representation of partial transcript text, sent as the enum name. `CUMULATIVE` sends the
        complete current hypothesis each time, replacing the previous partial, so the model can revise
        text it already emitted. `DELTA` sends only newly emitted text for the client to append, and is
        not compatible with every model or mode.
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
        Languages to bias transcription toward, each as a language name, e.g. `["English", "French"]`.
        A list of languages, not free-form context. Omit it to let the model detect the language.
    zdrOverride:
      type: boolean
      description: >-
        Overrides the Zero Data Retention policy for this session. `true` forces metadata-only logging;
        `false` allows content retention. When unset, the authenticated caller's policy applies.
components:
  schemas: {}
page_linked_schemas:
  Authorization: '#authorization'
  RealtimeHandshakeRequest: '#realtime-handshake-request'
```

```openapi-schema
kind: schema
name: RealtimeHandshakeResponse
schema:
  type: object
  description: >-
    Server reply to a successful handshake, sent before any transcript frames. This is the only server
    frame with no `type` field.
  required:
    - sessionId
  properties:
    sessionId:
      type: string
      description: Session id for end-to-end log correlation.
components:
  schemas: {}
page_linked_schemas:
  RealtimeHandshakeResponse: '#realtime-handshake-response'
```

```openapi-schema
kind: schema
name: ServerMessage
schema:
  description: >-
    Envelope for every server event after the handshake. The `type` field names the event and its
    payload is merged alongside it. Transcript, lifecycle, speaker, and progress events are multiplexed
    into one ordered stream. Dispatch on `type` and ignore unknown values.
  oneOf:
    - $ref: '#/components/schemas/TranscriptEvent'
    - $ref: '#/components/schemas/SpeechStartEvent'
    - $ref: '#/components/schemas/SpeechEndEvent'
    - $ref: '#/components/schemas/SpeechCompleteEvent'
    - $ref: '#/components/schemas/SpeakerEvent'
    - $ref: '#/components/schemas/AudioProgressEvent'
    - $ref: '#/components/schemas/ErrorEvent'
  discriminator:
    propertyName: type
    mapping:
      transcript: '#/components/schemas/TranscriptEvent'
      speechStart: '#/components/schemas/SpeechStartEvent'
      speechEnd: '#/components/schemas/SpeechEndEvent'
      speechComplete: '#/components/schemas/SpeechCompleteEvent'
      speaker: '#/components/schemas/SpeakerEvent'
      audioProgress: '#/components/schemas/AudioProgressEvent'
      error: '#/components/schemas/ErrorEvent'
components:
  schemas: {}
page_linked_schemas:
  AudioProgressEvent: '#audio-progress-event'
  ErrorEvent: '#error-event'
  ServerMessage: '#server-message'
  SpeakerEvent: '#speaker-event'
  SpeechCompleteEvent: '#speech-complete-event'
  SpeechEndEvent: '#speech-end-event'
  SpeechStartEvent: '#speech-start-event'
  TranscriptEvent: '#transcript-event'
```

```openapi-schema
kind: schema
name: SpeakerEvent
schema:
  type: object
  description: >-
    Labels the transcript span immediately before it: the span starts at the previous `speechStart` or
    `speaker` event, whichever came later, and ends here. Emitted in `DIARIZATION`. Does not indicate a
    speech boundary, a speaker change, or a final transcript, and the same label can repeat.
  required:
    - type
    - label
    - audioProcessedMs
  properties:
    type:
      type: string
      enum:
        - speaker
    label:
      type: string
      description: >-
        Model-generated speaker label, such as `A`. Meaningful only within one session, and not a
        verified identity.
    audioProcessedMs:
      type: integer
      format: int64
      description: >-
        Audio processed when the model emitted this label, in milliseconds from the start of the
        stream. Not a precise acoustic boundary.
components:
  schemas: {}
page_linked_schemas:
  SpeakerEvent: '#speaker-event'
```

```openapi-schema
kind: schema
name: SpeechCompleteEvent
schema:
  type: object
  description: The completed transcript for one speech turn, including any post processing.
  required:
    - type
    - audioProcessedMs
    - turnId
    - transcript
  properties:
    type:
      type: string
      enum:
        - speechComplete
    audioProcessedMs:
      type: integer
      format: int64
      description: >-
        Audio processed when the model emitted this event, in milliseconds from the start of the
        stream. Not a precise acoustic boundary.
    turnId:
      type: integer
      format: int32
      description: >-
        Id for this speech turn. Correlate lifecycle events by equality within the session; numbering
        is not otherwise meaningful.
    transcript:
      type: string
      description: >-
        Transcript for the entire turn. It can differ from the last partial, because the model may
        post-process the turn after speech ends.
components:
  schemas: {}
page_linked_schemas:
  SpeechCompleteEvent: '#speech-complete-event'
```

```openapi-schema
kind: schema
name: SpeechEndEvent
schema:
  type: object
  description: >-
    The model detected the end of speech. A boundary event, not the final transcript: use
    `speechComplete` for the turn's text.
  required:
    - type
    - audioProcessedMs
    - turnId
  properties:
    type:
      type: string
      enum:
        - speechEnd
    audioProcessedMs:
      type: integer
      format: int64
      description: >-
        Audio processed when the model emitted this event, in milliseconds from the start of the
        stream. Not a precise acoustic boundary.
    turnId:
      type: integer
      format: int32
      description: Id for this speech turn.
components:
  schemas: {}
page_linked_schemas:
  SpeechEndEvent: '#speech-end-event'
```

```openapi-schema
kind: schema
name: SpeechStartEvent
schema:
  type: object
  description: The model detected the beginning of speech.
  required:
    - type
    - audioProcessedMs
    - turnId
  properties:
    type:
      type: string
      enum:
        - speechStart
    audioProcessedMs:
      type: integer
      format: int64
      description: >-
        Audio processed when the model emitted this event, in milliseconds from the start of the
        stream. Not a precise acoustic boundary.
    turnId:
      type: integer
      format: int32
      description: >-
        Id for this speech turn. A later turn can open before an earlier turn's `speechComplete`
        arrives, so keep state keyed by `turnId`.
components:
  schemas: {}
page_linked_schemas:
  SpeechStartEvent: '#speech-start-event'
```

```openapi-schema
kind: schema
name: TranscribeRequest
schema:
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
        Container of the uploaded `audio` part, sent as the enum name. `WAV` is a RIFF/WAVE container
        holding mono integer PCM at 16 kHz or 24 kHz. There is no default; an unset or unrecognized
        value is rejected.
    mode:
      type: string
      enum:
        - PUSH_TO_TALK
        - ENDPOINTING
        - DIARIZATION
      default: PUSH_TO_TALK
      description: >-
        Transcription behavior, sent as the enum name. `PUSH_TO_TALK` is single-turn and the uploaded
        clip is the turn. `ENDPOINTING` detects speech onset and endpoint, one turn per detected
        segment. `DIARIZATION` additionally attributes turns to speakers. Mode availability depends on
        the model.
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
        Languages to bias transcription toward, each as a language name, e.g. `["English", "French"]`.
        A list of languages, not free-form context. Omit it to let the model detect the language.
    partialMode:
      type: string
      enum:
        - CUMULATIVE
        - DELTA
      default: CUMULATIVE
      description: >-
        Representation of partial transcript text, sent as the enum name. Applies to
        `text/event-stream` responses only. `CUMULATIVE` replaces the previous partial; `DELTA` sends
        only newly emitted text for the client to append.
    emitAudioProgress:
      type: boolean
      default: true
      description: >-
        Whether to emit `audioProgress` events. Applies to `text/event-stream` responses only; the
        buffered responses never surface them.
components:
  schemas: {}
page_linked_schemas:
  TranscribeRequest: '#transcribe-request'
```

```openapi-schema
kind: schema
name: TranscribeResponse
schema:
  type: object
  description: The buffered `application/json` response.
  required:
    - sessionId
    - transcript
    - audioDurationMs
    - turns
  properties:
    sessionId:
      type: string
      description: >-
        The `sessionId` query parameter, or the id the server generated when it was absent.
    transcript:
      type: string
      description: >-
        Final transcript for the whole clip. Populated in every mode; in the multi-turn modes it is the
        turn transcripts joined in turn order.
    audioDurationMs:
      type: integer
      format: int64
      description: Total audio duration processed, in milliseconds.
    turns:
      type: array
      items:
        $ref: '#/components/schemas/Turn'
      description: >-
        Every turn the model reported, in ascending `turnId` order. Empty in `PUSH_TO_TALK`. A turn the
        clip ended part-way through carries the boundaries the model gave and an empty transcript.
components:
  schemas: {}
page_linked_schemas:
  TranscribeResponse: '#transcribe-response'
  Turn: '#turn'
```

```openapi-schema
kind: schema
name: TranscriptEvent
schema:
  type: object
  description: One streamed transcript update.
  required:
    - type
    - transcript
    - final
    - audioProcessedMs
  properties:
    type:
      type: string
      enum:
        - transcript
    transcript:
      type: string
      description: >-
        Transcript text for this segment. Under `CUMULATIVE` it replaces the previous partial; under
        `DELTA` it is appended.
    final:
      type: boolean
      description: >-
        Transcript stability as reported by the model. In `PUSH_TO_TALK`, `true` marks stream
        completion. In `ENDPOINTING` and `DIARIZATION`, use `speechComplete` for turn completion
        instead.
    audioProcessedMs:
      type: integer
      format: int64
      description: Total audio processed so far, in milliseconds.
components:
  schemas: {}
page_linked_schemas:
  TranscriptEvent: '#transcript-event'
```

```openapi-schema
kind: schema
name: Turn
schema:
  type: object
  description: >-
    One speech turn the model detected, reported in the buffered transcribe response. Populated in
    `ENDPOINTING` and `DIARIZATION` only.
  required:
    - turnId
    - startMs
    - endMs
    - transcript
  properties:
    turnId:
      type: integer
      format: int32
      description: >-
        Id for this turn. Turns are reported in ascending id order; numbering is not otherwise
        meaningful.
    startMs:
      type: integer
      format: int64
      description: >-
        Audio processed when the model detected the turn's speech onset, in milliseconds from the start
        of the clip. Not a precise acoustic boundary.
    endMs:
      type: integer
      format: int64
      description: >-
        Audio processed when the model detected the turn's speech end, in milliseconds from the start
        of the clip. Not a precise acoustic boundary.
    transcript:
      type: string
      description: Finalized transcript for this turn, including any post processing.
    speaker:
      type: string
      description: Model-generated speaker label, such as `A`. Present in `DIARIZATION` only.
components:
  schemas: {}
page_linked_schemas:
  Turn: '#turn'
```