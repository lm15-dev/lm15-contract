# 2026-09-08 — The OpenAI Chat door is `openai-chat`; `openai_chat` names its wire

Ratification: RATIFIED 2026-09-08 — Maxime Rivest, in session ("i ratify,
go!"), after the finding was explained with both spellings' evidence and
the recommendation ("`openai-chat` wins, no debate") accepted. Transcribed.
Drafted from `lm15-rs/findings/2026-09-07-openai-chat-provider-spelling.md`
(the Rust module 6 review: `--direction models` 33 pass / 1 fail).

## What this changes

One golden, one spec sentence, one reference fix:

1. **The golden.** `goldens/openai_chat/models.json` pinned
   `$.models[*].provider = "openai_chat"` (fourteen entries). It now pins
   `"openai-chat"`, with the provenance block amended to say so. No wire
   byte changes; the pinned body is untouched.
2. **The rule.** `spec/vocabularies.md` § Open string namespaces gains the
   provider-string entry: provider strings are hyphenated; the underscore
   form is a permanent input alias and never an output value; `api_family`
   is a different, underscore-spelled namespace (the wire dialect).
3. **The reference.** `OpenAIChatLM.provider` (and its async mirror, the
   `OPENAI_CHAT_API` access policy, and the `_chat_content_parts` default)
   say `openai-chat`. Case files and the `goldens/openai_chat/` directory
   keep their name: a case's `provider` is harness INPUT, and the alias is
   accepted there by rule.

## Why

- Two namespaces met in one golden. Every `api_family` in the corpus is
  underscore-spelled (`openai_chat`, `openai_responses`,
  `anthropic_messages`, `gemini_generate_content`): it names a wire. Every
  other `provider` is hyphenated (`meta-chat`, `azure-chat`,
  `bedrock-mantle-chat`, `deepseek`): it names a door. `openai_chat` as a
  provider value was the reference adapter's self-name from before the
  registry existed (`lm15/registry.py` registers the door as
  `openai-chat`; `lm15/providers/openai_chat.py` never followed).
- The reference contradicted itself: `LMRouter().resolve("openai_chat:m")
  .provider == "openai-chat"` while `router.lm("openai_chat:m").provider ==
  "openai_chat"`, so a `ModelInfo.provider` from `list_models()` did not
  equal the `Resolution.provider` that produced the adapter.
- The 2026-09-02 independent review had this golden in front of it and
  added its provenance block without catching the value: fixture agreement
  with the reference proves little (AUTHORITY.md). The Rust port caught it
  by answering the registry id and refusing to absorb the failure.

## Considered and rejected

- Ratifying the underscore: it would make the one provider whose spelling
  differs from its registry id the OpenAI Chat door, break the rule every
  other provider follows, and leave the router's self-contradiction in
  place.
- Renaming `cases/openai_chat/`, the case ids and `goldens/openai_chat/`:
  churn across 26 case files and every receipt path for no semantic gain.
  Case keys are harness input where the alias is accepted; the corpus
  layout is not a canonical fact.

## Evidence

- Rust before this entry: `--direction models` 33 / 1, the one failure
  being this value; after: 34 / 0 with no port change.
- Reference after the fix: `--direction models` green; the full pytest
  suite green (`test_registry.py` no longer carries the "historical
  spelling" exception).

## Trade-offs, stated

- A consumer that compared `ModelInfo.provider == "openai_chat"` against
  the reference's old output breaks. lm15 is pre-1.0 and the underscore
  spelling was never the contract's value; the alias still works as
  input everywhere.
