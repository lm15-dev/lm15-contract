# 2026-09-24 — A stored-cache resource where there is no such tier is refused, in every SDK

Status: implementation parity for a ratified rule (MAP-6 rule 7: "Providers
without the tier RAISE"); no rule changes.

## Found

lm15-rs had a unit test asserting that Groq *accepts* `config.cache.resource`
while Rust's code refused it: the test was the stale half. Checking every
provider in all four CI'd SDKs showed the opposite gap: lm15-python, lm15-ts
and lm15-go **dropped the resource silently** on providers with no cache
controls at all (Groq, DeepSeek, Z.AI, Ollama, xAI on the Chat wire; Meta on
the Anthropic wire), with no adaptation record. Only Rust followed the rule.

A resource stands in for the start of the prompt (the Gemini tier sends
`cachedContent` and only the messages after it). Dropping it sends the request
without that prefix: the model answers a different question. That is MAP-13's
refusal condition, not an adaptation.

## Changed

- lm15-python, lm15-ts, lm15-go: both OpenAI dialects' shared cache step, and
  the Anthropic dialect on a server without marks, raise
  `UnsupportedFeatureError(feature="config.cache.resource")`.
- lm15-rs: the stale test now expects the refusal.
- Cases: `<provider>.cache_resource_refused` for groq, deepseek, zai, ollama,
  xai and meta-anthropic.
- `tools/differential_requests.py` grows two settings, `cache_resource` and
  `cache_off`, never compared before: 1,995 requests, identical in Python,
  TypeScript, Go and Rust.
