# Protocol addition: optional `base_url` on adapter-constructing ops

Additive, optional field documented in `harness/PROTOCOL.md`: when
`build_request`, `parse_response`, `replay_stream`, or `normalize_error`
carries `"base_url"`, the shim constructs the adapter against that base URL
instead of the provider default. The reference shim (`python -m lm15.vet`,
lm15-python2@66e4d61) already accepted it; this entry lands the documentation
and the harness side.

Motivation: provider `openai_chat` (the OpenAI Chat Completions dialect,
lm15-python2@66e4d61) speaks to many servers (OpenAI, ollama, Groq,
OpenRouter, vLLM, SGLang, …). Its case fixtures must pin which server they
were captured against; the new top-level case field `"base_url"` records it
and `harness/check.py` (`case_base_url`) and `tools/scribe_goldens.py`
forward it verbatim on every shim op.

Backward compatibility: cases without `"base_url"` behave exactly as before
(nothing is sent). No existing fixture, golden, or oracle value changed.
