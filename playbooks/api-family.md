# API family — the public surface, one name per concept, four languages

Status: RATIFIED 2026-09-06 (drafted 2026-09-02; ratified in session with the edits recorded in `changes/2026-09-06-ratification.md` D4). Companion to `port.md`.

`port.md` makes four ports agree on the wire. This page makes them agree on what a user types. The harness cannot check any row here; the reviewer does (`port.md` § Reviewing a port). A port that deviates from a row writes the reason under "Stated deviations" in its README.

Goal: a person who knows lm15 in two of these languages opens the third and is at home. Same words, same order, same shape. Only the casing and the language's own mechanics change.

## Rules

1. **One word per concept.** `complete`, `stream`, `Request`, `Response`, `Message`, `Router`. A port never introduces a synonym (`generate`, `chat`, `run`, `send`) for a concept that has a word here.
2. **Casing follows the language; the word does not.** Python and Rust `tool_calls`, TypeScript `toolCalls`, Go `ToolCalls`. The JSON key is `tool_calls` in all four (wire contract, `port.md` § Idioms).
3. **The user builds a `Request`, gets a `Response`.** Every entry point takes the canonical types. No port adds a convenience layer that hides them (no `router.ask("text")` returning a string).
4. **Async is the language's own.** Python ships both (`Async` prefix). TypeScript is async only. Go is sync with `context.Context`. Rust is async (tokio), with a `blocking` feature that mirrors the same names.
5. **Zero dependencies where the language allows it.** Python stdlib, TypeScript `fetch` + `WebSocket`, Go `net/http` + `x/net/websocket` or `nhooyr` (state which). Rust uses `reqwest` + `tokio` + `serde`; zero-dep is not a Rust idiom, so this is a stated deviation for the whole port, once.
6. **Positional layout is frozen at 1.0. Every field added later is keyword-only (or the language's equivalent: options struct / builder).**
7. **Prefer `reject` to a new send-as value. A compat knob exists only when the wire has no other way, the goal is unreachable without it, and at least two providers need it. Otherwise it is an `extensions` passthrough.**

## The core loop

| Concept | Python | TypeScript | Go | Rust |
|---|---|---|---|---|
| Entry point | `LMRouter()` | `new LMRouter()` | `lm15.NewRouter()` | `LMRouter::new()` |
| One call | `router.complete(req)` | `await router.complete(req)` | `router.Complete(ctx, req)` → `(*Response, error)` | `router.complete(&req).await?` |
| Stream | `router.stream(req)` → iterator of `StreamEvent` | `router.stream(req)` → `AsyncIterable<StreamEvent>` | `router.Stream(ctx, req)` → `iter.Seq2[StreamEvent, error]` | `router.stream(&req)` → `impl Stream<Item = Result<StreamEvent>>` |
| Assembled stream | `ResponseStream(events, req)`; iterate for text; `.response` | `new ResponseStream(events, req)`; `for await` text; `.response()` | `lm15.NewResponseStream(events, req)`; `.Text()` channel or `.Response()` | `ResponseStream::new(events, &req)`; `.text_chunks()`; `.response().await` |
| Request | `Request(model=, messages=, tools=, config=)` | `{ model, messages, tools?, config? }` typed as `Request` | `lm15.Request{Model:, Messages:, Tools:, Config:}` | `Request { model, messages, ..Default::default() }` |
| User message | `Message.user("hi")` | `Message.user("hi")` | `lm15.UserMessage("hi")` | `Message::user("hi")` |
| Assistant message | `Message.assistant(parts)` | `Message.assistant(parts)` | `lm15.AssistantMessage(parts...)` | `Message::assistant(parts)` |
| Tool result message | `Message.tool(call.id, result)` | `Message.tool(call.id, result)` | `lm15.ToolMessage(call.ID, result)` | `Message::tool(&call.id, result)` |
| Response text | `response.text` | `response.text` | `response.Text()` | `response.text()` |
| Tool calls | `response.tool_calls` | `response.toolCalls` | `response.ToolCalls()` | `response.tool_calls()` |
| Assistant turn to replay | `response.message` | `response.message` | `response.Message` | `response.message` |
| Usage | `response.usage.input_tokens` | `response.usage.inputTokens` | `response.Usage.InputTokens` (`*int`) | `response.usage.input_tokens` (`Option<u64>`) |
| Finish reason | `response.finish_reason` | `response.finishReason` | `response.FinishReason` | `response.finish_reason` |
| Config | `Config(temperature=0.2, max_tokens=100)` | `{ temperature: 0.2, maxTokens: 100 }` | `lm15.Config{Temperature: lm15.F(0.2), MaxTokens: lm15.I(100)}` | `Config { temperature: Some(0.2), max_tokens: Some(100), ..Default::default() }` |
| Model string | `"groq:llama-3.3-70b-versatile"` | same | same | same |

`Usage` counters are `absent`, not zero, when unreported (INV-029). Go uses pointers, Rust `Option`, TypeScript `undefined`. Never `0`.

## Providers, direct

| Concept | Python | TypeScript | Go | Rust |
|---|---|---|---|---|
| Provider object | `OpenAILM()`, `AnthropicLM()`, `GeminiLM()`, `OpenAIChatLM()`, `XaiLM()`, `ClaudeCodeLM()`, `OpenAICodexLM()` | same class names | `lm15.NewOpenAILM(opts...)` etc. | `OpenAILM::new()` etc. |
| Credential | `OpenAILM(api_key=...)` — a string, a credential value, or a zero-arg callable returning one | `new OpenAILM({ apiKey })` — a string, a credential value, or `() => Credential` | `lm15.WithAPIKey(s)` or `CredentialProvider` interface (one method returning the value) | `OpenAILM::builder().api_key(s)` or `impl CredentialProvider` (one method returning the value) |
| Host settings | `settings=` on every provider constructor and `RouterConfig.settings` | `settings` option object | `lm15.WithSettings(map)` | `HostSettings` builder field |
| Access policy (AUTH-10) | `AccessPolicy` value | same | `lm15.AccessPolicy` struct | `AccessPolicy` struct |
| List models | `lm.list_models()` | `lm.listModels()` | `lm.ListModels(ctx)` | `lm.list_models().await` |

A credential provider returns a credential value (`ApiKey`, `BearerToken`, `AwsCredentials`; AUTH-2); a plain string is the `ApiKey` shorthand. Python/TS/Julia: a zero-arg callable. Go/Rust: a single-method interface returning the value. Same in all four.

The same `complete` / `stream` names exist on a provider object and on the router. A user who learned one has learned the other.

## Ingest (MAP-12, provisional; ratified 2026-09-08)

| Concept | Python | TypeScript | Go | Rust |
|---|---|---|---|---|
| A Chat Completions request body → `Request` | `request_from_openai_chat(body, compat=None)` (module function; also `lm.request_from_openai_chat(body)` on `OpenAIChatLM`) | `requestFromOpenAIChat(body, { compat })`; `lm.requestFromOpenAIChat(body)` | `lm15.RequestFromOpenAIChat(body, opts...)`; `lm.RequestFromOpenAIChat(body)` | `request_from_openai_chat(&body, compat)` in the dialect module; `lm.request_from_openai_chat(&body)` |
| A Chat Completions response body → `Response` (MAP-12 rule 9, 2026-09-08) | `response_from_openai_chat(body, model=None, choice=None)`; `lm.response_from_openai_chat(body, ...)` | `responseFromOpenAIChat(body, { model, choice })`; `lm.responseFromOpenAIChat(body, ...)` | `lm15.ResponseFromOpenAIChat(body, opts...)`; `lm.ResponseFromOpenAIChat(body, ...)` | `response_from_openai_chat(&body, model, choice)`; `lm.response_from_openai_chat(&body, ...)` |

| The other libraries' call, as-is (2026-09-08, pending) | `router.complete_from_openai_chat(model, messages, **kwargs)`; `stream_from_openai_chat`; `request_from_openai_chat(model, messages, **kwargs) → (Request, lm)`; `openai_chat_model_string(model)` | `router.completeFromOpenAIChat(model, messages, opts)`; `streamFromOpenAIChat`; `requestFromOpenAIChat`; `openaiChatModelString` | `router.CompleteFromOpenAIChat(ctx, model, messages, opts)`; `StreamFromOpenAIChat`; `RequestFromOpenAIChat`; `lm15.OpenAIChatModelString` | `router.complete_from_openai_chat(model, &messages, opts)`; `stream_from_openai_chat`; `request_from_openai_chat`; `openai_chat_model_string` |

**The stated exception to rule 3.** `complete_from_openai_chat` is the one
entry point that does not take the canonical types: it takes the OpenAI
SDK's / litellm's call — `(model, messages, **kwargs)` — because that call
is what a migrating codebase holds, and a converter the user must find and
wire is a door half the users never open. It hides nothing: the result is
a canonical `Response`, `router.request_from_openai_chat(...)` returns the
`Request` it built and the LM it routes to, and every keyword goes through
MAP-12 (map / extensions / refuse by name). The model string is read by
`openai_chat_model_string`: an lm15 `provider:model` as-is; litellm's
`provider/model` through `LITELLM_PROVIDER_PREFIXES` (data; only the first
segment; an unlisted or two-door prefix such as `bedrock/` is refused by
name); a bare name by the router's rules except that an OpenAI model takes
the `openai-chat` door — the endpoint both libraries were using — where
`router.complete` would take Responses. Client keywords (`api_key`,
`api_base`, `timeout`, `num_retries`, `headers`, `cache`, `drop_params`,
…) are refused with the `RouterConfig` place named.

Python amendment (ratified 2026-09-09; `changes/2026-09-09-python-migration-ux.md`):
`complete_from_openai_chat(..., stream=True)` returns a lazy `ResponseStream`;
`False` or omission returns `Response`. Only booleans are accepted. Iterate
for text, use `.events()` for canonical events, and `.response` to consume
any remainder and obtain the assembled answer. `close()` / context-manager
exit releases the source without draining it; closing before completion
cannot produce a completed response. The async helper is awaited in both
modes, returning `Response` or `AsyncResponseStream`; use `async for`,
`await result.response()`, and `aclose()` / `async with`. Overloads expose
the return-type distinction. The native `complete(Request)` remains
single-return-type. `stream_from_...` remains the raw-event alternative.

Python's `explain_auth` also accepts a `Resolution` as its provider input.
It reads only that object's provider identity; `config=router.config` supplies
the actual router configuration. A resolution never embeds credentials.

One word for one concept: the function is named after the format it reads,
never `from_openai`, `parse_chat`, `import_messages`. They are dialect-module
functions, not `Request` / `Response` constructors: the canonical types stay vendor-free
(rule 3 — the user still gets a `Request`; nothing is hidden). `body` is the
JSON object a client would POST (`model`, `messages`, …), never a
`(model, messages, **kwargs)` spread — one shape in every language. `compat`
is the preset name or policy the dialect adapter takes; the method form uses
the adapter's own. The response door takes no compat (the response shape does
not vary by server), `model` for a body that carries none, and `choice` to
name one of several choices (unnamed, several is refused). Refusals are
`UnsupportedFeatureError` with the key named; malformed input is the
language's own error (MAP-12 rule 6). Ports implement the response door by
exposing their existing `parse_response` reader, never by a second reader.

**Marked for demotion.** `OpenAIResponsesCompat.edit_image_field` and `commentary_phase` are single-provider knobs (Meta). They stay in 1.0.0a; they move to `extensions` in the next alpha unless a second provider needs them (rule 7). Note only; no code change now.

## Tools

| Concept | Python | TypeScript | Go | Rust |
|---|---|---|---|---|
| Declare a tool | `tool(fn)` derives schema from the signature | `tool(fn, { name, description, parameters })` — schema explicit | `lm15.FunctionTool{Name:, Description:, Parameters: schema}` | `FunctionTool { name, description, parameters }` |
| Tool call part | `ToolCallPart(id, name, input)` | `{ type: "tool_call", id, name, input }` | `lm15.ToolCallPart{ID, Name, Input}` | `Part::ToolCall { id, name, input }` |
| Loop | user runs the function, sends `Message.tool(...)`, calls `complete` again | same | same | same |

Stated deviation, all three non-Python ports: no derivation from a function signature. Python can read a signature at runtime; the others cannot without a build step or a schema library. The schema is written by the user. This is one deviation, stated here, not four.

## Types and serde

| Concept | Python | TypeScript | Go | Rust |
|---|---|---|---|---|
| `Part` and friends | classes, `.type` field | discriminated union on `type` | sealed interface, one struct per variant, `Kind()` | `enum Part`, `#[serde(tag = "type")]` |
| To canonical JSON | `to_dict(x)` / `to_json(x)` | `toJSON(x)` | `json.Marshal(x)` (custom marshalers) | `serde_json::to_string(&x)` |
| From canonical JSON | `from_dict(Request, d)` | `Request.fromJSON(d)` | `json.Unmarshal(b, &req)` | `serde_json::from_str::<Request>(s)` |
| Validation | constructor raises | constructor throws | `lm15.NewRequest(...)` returns error; struct literal + `req.Validate()` | constructor returns `Result`; `Default` + `validate()` |
| Immutability | frozen dataclasses | `readonly` fields | by convention, copies | owned values |

Canonical JSON keys are the wire contract and are the same in all four. The omission rule (`docs/serde-rules.md`) is the same in all four.

## Errors

| Concept | Python | TypeScript | Go | Rust |
|---|---|---|---|---|
| Root | `LM15Error` | `LM15Error extends Error` | `*lm15.Error` | `enum Lm15Error` |
| Class | subclasses (`RateLimitError`, ...) | subclasses, same names | `lm15.ErrorKind` enum, same names, `errors.As` | variants, same names |
| ErrorCode | `.code` | `.code` | `.Code` | `.code()` |
| Retryable | `RETRYABLE_ERRORS` | `RETRYABLE_ERRORS` | `err.Retryable()` | `err.is_retryable()` |
| Message | never pinned | same | same | same |

The class NAME and the ErrorCode are the family. The mechanism is the language's.

## Names that do not change

These identifiers are the same string in all four, casing aside:

`LMRouter`, `Request`, `Response`, `Message`, `Config`, `Usage`, `Tool`, `FunctionTool`, `BuiltinTool`, `ToolChoice`, `Reasoning`, `CacheConfig`, `ContinuationState`, every `*Part`, every `*Delta`, every `Stream*Event`, every `*LM` provider, every error class, `ResponseStream`, `ModelInfo`, `AccessPolicy`, `complete`, `stream`, `list_models`, `request_from_openai_chat`, `response_from_openai_chat`, `user`, `assistant`, `tool`, `text`, `tool_calls`, `usage`, `finish_reason`, `message`.

## Reviewing against this page

1. Open the port's README quick start. It must read like `lm15-python/docs/getting-started.md` with the casing changed.
2. Grep the port for the synonyms in rule 1. Each hit is a finding.
3. Every row above is either matched or listed under "Stated deviations".
