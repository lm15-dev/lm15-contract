# 2026-08-31 — remove the training/fine-tuning scaffolding (pre-1.0 scope cut)

Ratified: Maxime Rivest, 2026-08-31 (session assent: "we should also
remove the training / fine_tuning for now.. but we should know how to do
inference with a finetuned model" … "yes cut that too!"); transcribed.

Removes the reserved-but-unimplemented training surface. Nothing ever
implemented it: the flags defaulted false everywhere and no adapter, no
endpoint, no port touched them. 1.0.0 has never shipped, so this is a
pre-release scope cut.

## The principle (the part that stays)

lm15 does INFERENCE with fine-tuned models, not training. That capability
is untouched and already complete:

- `ModelOrigin` (`type`, `id`, `base_model`) describes fine-tune
  provenance — the `model_info.full` serde fixture still pins exactly
  this (`origin.type: "fine-tune"`, `base_model: "omega-3"`).
- Provider-hosted fine-tunes (`ft:` ids) flow through the normal chat
  contract; self-served tuned weights flow through the `openai_chat`
  dialect (vLLM/SGLang cases pinned live).

When training endpoints are wanted later, they arrive as a designed
surface through the changes process — not as dormant flags that imply a
promise no code keeps.

## What is removed

- Reference (lm15-python): `TrainingModelInfo` and `TrainingPricing`,
  the `ModelInfo.training` field and its serde, the
  `EndpointSupport.fine_tuning`/`training_session` flags, their tests,
  and their doc coverage (model-hydration.md, using-model-profiles.md,
  serde-rules.md Number-rule citation).
- Contract: the `training` block of the `model_info.full` serde fixture
  (a frozen-fixture amendment, hence the ratification above; edited
  identically in both landing copies per the dual-landing rule) and the
  `model_info.origin/inference/training` citation in spec/invariants.md.

## Evidence at landing time

- lm15-python: full suite green; serde mirror and contract fixture
  byte-identical on the shared value.
- Contract: provenance, audit, spec_drift, secrecy OK; all seven harness
  directions green; selftest 10/10 mutations caught.
