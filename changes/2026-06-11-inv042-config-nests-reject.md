# 2026-06-11 — INV-042 resolved: malformed config nests raise, never drop

Decision (maintainer delegation): `config_from_dict` raises `TypeError` when
`tool_choice`/`reasoning`/`cache` is present but not a JSON object. Canonical
JSON input that is malformed is an ERROR, never silent data loss — the old
behavior silently treated a mistyped nest as absent, changing what the
caller's request asks for.

`null` still reads as absent. The telemetry/metadata nests (`response.usage`,
`stream end.usage`, `model_info.origin/inference/training`,
`live_config.input_format/output_format`) remain lenient: they describe what
a provider reported, so treating a non-dict as absent loses nothing the
caller authored.

Spec rows changed: spec/invariants.md INV-042 rewritten (split rule:
caller-authored config nests reject, telemetry nests lenient);
spec/types.md Config section notes the TypeError.

Implementation: lm15-python2 `lm15/serde.py::config_from_dict` via
`_config_nest`; red-first reject coverage in
`lm15-python2/tests/test_spec_decisions_1_0.py`. No fixtures changed (no
fixture carried a malformed nest — they were unreachable by construction
from any conforming serializer).
