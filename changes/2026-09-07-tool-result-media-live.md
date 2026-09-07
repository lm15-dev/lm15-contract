# Live image-bearing tool results — 2026-09-07

> Superseded the same day by `2026-09-07-tool-result-content.md` (the ratified MAP-10 pass); kept as the record of the first probe.

## Scope

Evidence collection, not a blanket support change or a new canonical type.

All **31 registered provider bindings** were covered in the attempt ledger. There were **36 provider/model experiments**, **53 inference attempts** (including two connection failures), and two additional model-listing GETs. No automatic retries, provisioning, or deployments. Alternate-model experiments are separate, preserved observations.

The initial table contained three unavailable model choices. The Groq and Ollama replacements came from freshly captured `/models` listings; the corrected Bedrock Mantle spelling came from the existing pinned listing. Initial failures remain in the ledger.

- [Full results](../receipts/2026-09-07-tool-result-media/REPORT.md)
- [Machine-readable results](../receipts/2026-09-07-tool-result-media/REPORT.json)
- Capture: `research/providers/media_tool_results.py`
- Offline derivation: `research/providers/summarize_media_tool_results.py`
- Offline tests: `research/providers/test_media_tool_results.py`

## Method

Each first request asked the model to call `fetch_panel` for A and B. The actual returned assistant turn, call IDs, arguments, and reasoning state were replayed. No synthetic assistant tool call or fabricated signature was used.

Each tool returned a fresh 3-by-2 PNG of six shuffled colors. A returned only an image; B returned text plus an image. The answer order was not in the prompt or image metadata. Success required all twelve colors, in the correct order, associated with the correct tool calls.

The follow-up body used the candidate provider format, because several current adapters discard or refuse tool-result images. Its URL, credentials, host handling, and initial request came from LM15. Mutated SigV4 requests were re-signed. **These are raw-wire discovery probes, not a claim that the current SDK already emits them.**

The shared `_capture.py` machinery recorded redacted wire requests, request and response hashes, timestamps, and exchange status. Each run has its own folder. Raw responses and oracle images are retained; existing receipts were not overwritten.

## Eight exact visual successes

| Binding | Model tested | Result |
|---|---|---|
| anthropic | claude-haiku-4-5 | 12/12 colors, both tool associations |
| claude-code | claude-sonnet-5 | 12/12 |
| gemini | gemini-3.7-flash | 12/12 |
| xai | grok-4.20 | 12/12 |
| moonshotai | kimi-k2.6 | 12/12 |
| moonshotai-responses | kimi-k3 | 12/12 |
| moonshotai-anthropic | kimi-k3 | 12/12 |
| meta | muse-spark-1.3 | 12/12 |

These establish the tested model/host combinations, not every model offered by each provider.

## Three explicit image-result rejections

The first turn succeeded; the image-bearing second turn failed:

| Binding | Model | Result |
|---|---|---|
| groq | qwen/qwen3.8-27b | HTTP 400: tool message content must be a string |
| meta-chat | muse-spark-1.3 | HTTP 400: tool message content did not match a supported type |
| bedrock-chat | deepseek.v3.2 | HTTP 400: invalid tool-message content |

Groq is a useful counterexample to trusting a generated SDK union: the current model listing advertises image input and tools, but the actual tool-message array was rejected.

## HTTP 200 was not enough

- **DeepSeek Chat and Messages:** the model said both tool images arrived as `[Unsupported Image]`. Neither wire yielded a valid visual answer. Do not treat 200 as image support.
- **OpenAI Responses, gpt-4.1-mini:** requested the tools again rather than reporting the images.
- **OpenAI Responses, gpt-5.4-mini:** answered 8 of 12 cells correctly, but failed the exact visual check. This is partial evidence, not proof that images are wholly unsupported or reliably handled.
- **OpenAI Chat:** gpt-4.1-mini did not provide a visual answer; gpt-5.4-mini returned empty arrays.
- **Azure OpenAI Responses and Chat, gpt-4.1-mini:** no passing visual answer.
- **Meta Messages:** asked to retrieve panel A again instead of completing the answer.
- **Ollama, qwen3.5:0.8b:** accepted the wire but did not complete the visual check. Its small model and tool-message conversion both remain possible causes.

There are ten accepted-but-not-passing experiments, not ten proven unsupported providers.

## Blocked or inconclusive before testing image results

- OpenRouter: HTTP 401, user not found.
- Azure Claude: deployment not found.
- AWS-hosted Claude: missing host configuration.
- Bedrock Claude: HTTP 403.
- Bedrock Mantle Chat: tested Grok model not supported on the selected route, even after correcting its model ID.
- Vertex Gemini and Claude: Google credential refresh failed.
- Vertex express: missing `GOOGLE_API_KEY`.
- vLLM and SGLang: local endpoints not reachable.
- Codex and Z.AI: first response did not return exactly the requested pair of client tool calls. The probe stopped rather than fabricating a replay or exceeding its two-call design.

These outcomes say nothing definitive about image support. Read the individual receipts for the exact error, model, and endpoint.

## Fixture preparation

Each of the eight exact successes has a **`fixture-candidate.json`** beside its receipts. It contains the sent request, response artifact location, visual expectation, canonical request reconstruction where possible, and provenance.

The candidate check compares the current Python adapter's rebuilt JSON body with the actual sent body. Only `moonshotai-anthropic` matched exactly in this check. Interpret other differences carefully:

- Anthropic and Claude Code preserve the tool media, but their canonical replay omits the provider's `caller` metadata. This caused strict body inequality; it is not evidence that their tool images disappeared.
- Gemini, Chat-family adapters, and Responses-family adapters require the media mapping repairs identified earlier.

Candidates are deliberately **outside active `cases/` and `goldens/`**. Promotion requires public-adapter equality, a body copied into the corpus layout, reviewed expected output, and a passing harness run. No pin or support matrix was changed merely to make these probes pass.

## Integrity checks

- Ten offline probe tests passed, covering all four formats, both call IDs, replay preservation, Gemini optional IDs, SSE extraction, oracle construction, append-only writes, and credential redaction.
- Catalog/model coverage includes all 31 registry bindings.
- `tools/check_secrecy.py` passed on the new receipt tree.
- One early Ollama receipt has its public placeholder name over-redacted. The derived report identifies that provider by its directory; the original receipt remains untouched. The capture helper now excludes public placeholder keys from secret registration.

## Next implementation step

Keep `ToolResultPart.content` unchanged. Implement the proven formats, gated by provider/model support, then promote matching candidates. Preserve clear refusals for known incompatible combinations. Resolve authentication/deployment and first-turn issues before claiming coverage for blocked bindings.
