# Model — the verdict table

The normative table is `tools/openai-chat-ingest-verdicts.json`, enforced
by `tools/audit.py`; this page is its reading guide. The rule is
`docs/mapping-rules.md` MAP-12.

## Buckets

| Verdict | Meaning | Round-trips? | Count (2026-09-08) |
|---|---|---|---|
| `map` | reads into a canonical field | yes | 27 body keys; 8 row rules, 6 block rules, 3 tool types, 5 tool_choice forms |
| `extensions` | verbatim into `config.extensions` | yes (the builder re-emits extensions verbatim) | 8 |
| `refuse` | `UnsupportedFeatureError` naming the key | n/a | 8 body keys; 4 row rules (`function` role, `name`, `audio`, `function_call`); `video_url`; `custom` tools and choices |
| `call-mode` | read and dropped: how the request is sent | n/a | 2 (`stream`, `stream_options`) |
| `default` | equal to the wire default; reads as absent | yes (same bytes) | `response_format {type: text}`, `strict: false`, `logprobs: false`, `json_schema.name == "response"` |

## Preset-conditioned rows

A row with a `when` is read only under that compat condition and refused
elsewhere: the reasoning spellings (`reasoning_effort` / `reasoning` /
`thinking` / `enable_thinking` / `chat_template_kwargs` / `reasoning_format`),
`user_id`, the prompt-cache keys, and Groq's server-executed tool types.
The condition is the same compat field the builder consults when it
WRITES that key, so the inverse pairs exactly with the builder under each
preset.

## Lossy classes (round trip not exact, pinned per case)

| Class | Wire cause | Cases |
|---|---|---|
| `thinking_as_text` | `thinking_replay="as_text"` | 5 |
| `tool_result_name_omitted` | `tool_result_name="omit"` | 14 |
| `leading_developer_as_system` | one instruction row for system and a leading developer message | 6 |

21 distinct cases (4 carry two classes).

## Coverage

- 118 recorded chat-dialect bodies round-trip (97 exact, 21 pinned lossy).
- 38 hand-authored foreign shapes, 10 of them refusals.
- 37 of 37 OpenAI-documented top-level parameters have a verdict; 8 more
  rows cover the spellings lm15's presets write for other servers.
