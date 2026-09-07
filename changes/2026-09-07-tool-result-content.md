# 2026-09-07 — Tool-result content: MAP-10, the `tool_result_media` knob, fixtures

Status: **ratified by the maintainer 2026-09-07** (decisions 1–4 below:
"yes; one more receipt; move the docs; anything needed").

## What changed

- `docs/mapping-rules.md` **MAP-10 — Message content reaches the wire
  natively or raises** (rules 1–8, measured verdicts, one stated deviation).
- `spec/types.md` § ToolResultPart: content policy paragraph; the
  `tool_result_media` compat knob (`native | reject`) on the Chat,
  Responses and Anthropic compat tables.
- `docs/serde-rules.md`, `docs/mapping-rules.md` now live in this
  repository (moved from `lm15-python/docs/`, commit f5bceba) so a
  `CONTRACT_PIN` names every normative document. Stubs forward.
- Fixtures: `cases/<provider>/tool_result_{image,mixed,pair,pdf,error}.json`
  (native bindings, live-captured turn-2 wires) and
  `cases/<provider>/tool_result_image_raise.json` (reject presets,
  `expect_lm15.raises`). Bodies under `bodies/`. See "Fixtures" below.
- `tools/check_content_coverage.py`: every (dialect × preset × part kind)
  cell has a case or a documented raise; blank is drift.
- `harness/selftest.py`: mutations that drop an image, swap two call ids
  and strip `is_error` must fail the harness.
- `playbooks/port.md`: a port review probes cells outside the corpus.

## Why

The Rust port review (2026-09-07) probed a request the corpus did not
cover: an image inside a `ToolResultPart`. Both implementations sent the
literal string `[{"type": "image"}]` — HTTP 200, the model answered, the
caller paid. Every adapter except Anthropic rendered tool-result content
through the lossy `parts_to_text`. The corpus had 297 canonical requests,
17 with tool results, **zero with non-text content in one**. MAP-5..8
forbade silent drops for knobs; nobody had applied the rule to parts.

## Evidence

Design pass `research/tool-result-content/` (frame, 37 sources with
sha256, fact sheets for all 31 bindings, matrix runner, ledger, model,
attack). Receipts `receipts/2026-09-07-tool-result-media/`: ≈220 cells,
every turn-2 wire raw-patched (the SDK could not yet emit it), the
model's own turn replayed verbatim, a hidden visual oracle per cell, a
user-image control per model.

Headline receipts (ledger rows in `research/tool-result-content/20-results.md`):

- **native, exact**: anthropic, claude-code, gemini 3.7-flash, xai,
  moonshotai ×3, meta (Responses), meta-anthropic, zai — image, mixed,
  two-call association, `is_error`; documents where the door takes them.
- **openai (Responses)**: at the 64px oracle every OpenAI model failed the
  *user-image control* too — the oracle was unreadable, those rows are
  struck. At 256px/`detail: high`: control OK, then image/mixed/pair
  **exact on gpt-5.4**; gpt-4.1-mini 5/6 (model vision). Native.
- **openai-chat / azure-chat**: control OK on gpt-5.4, tool image not
  received at both oracles → silent degrade → `reject`.
- **deepseek / deepseek-anthropic**: 200 and the model reports
  `[Unsupported Image]` → `reject`.
- **groq**: SDK union says image; server 400 "must be a string" → `reject`.
- **gemini-2.5-flash**: 400 "Multimodal function responses are not
  supported for this model" → loud, server-side gate; no allowlist in lm15.
- **documents**: Responses `input_file` OK on openai; Anthropic
  `document` OK on anthropic/claude-code/meta-anthropic; Gemini pdf OK;
  400 on every Chat door tried and on all three Kimi doors.
- **codex**: the backend's terminal frame carries `output: []`; items
  arrive as `output_item.done`. Image received (5/6, mini model).

## Counter-evidence and what it does not prove

- No receipt for openrouter (401), ollama (timeouts on a 0.8b model),
  vllm/sglang (no server), azure-anthropic (deployment), aws/bedrock
  Claude (403 / host settings), vertex ×3 (OAuth). Their presets say
  `reject` **until a receipt**; the coverage tool lists them as open.
- Kimi's documented `video_url` tool row was not exercised; not ratified.
- Gemini's `$ref` interleave was not exercised; stated deviation.
- The pass records usage per cell but did not fold in price lists.

## Trade-offs, stated

- **Raise, not degrade.** A caller on a text-only server cannot pass an
  image tool result at all; they render to text themselves. Chosen because
  the alternative is the silent paid no-op the project exists to prevent.
- **Per-preset knob, not a model allowlist.** Model gating that fails
  loudly (Gemini 2.5) is left to the server; model gating that fails
  silently (OpenAI Chat) is a `reject` on the preset. A future model that
  gains the feature on a `reject` preset needs a receipt and a preset change.
- **`[error] ` text prefix on wires with no flag.** Lossy in the sense
  that the model sees text, not a flag; stated so ports produce the same
  bytes. The alternative — refusing `is_error` on Responses/Chat — would
  break every agent loop that reports failures.
- **Fixtures precede the SDK.** Several new cases fail today's reference
  (that is the point; AUTHORITY: implementations never win).

## Decisions taken (maintainer, 2026-09-07)

1. Raise-not-degrade ratified.
2. One more OpenAI receipt before pinning native: taken (gpt-5.4, 256px,
   exact on three cells).
3. Normative docs move into the contract: done.
4. Budget: unbounded for the pass; ≈220 cells, ≤2 calls each.
