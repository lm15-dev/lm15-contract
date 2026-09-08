# 2026-09-08 — MAP-11: a provider id placed in a URL path is percent-encoded

Ratification: RATIFIED 2026-09-08 — Maxime Rivest, in session ("i ratify, go!", second session of the day), after the finding was explained with the three options (do nothing / refuse / encode) and their failure modes, and "encode, keeping `/` only on the resource-name dialect" accepted. Transcribed. Drafted from the Rust port's surfaces differential probe (`lm15-rs/findings/2026-09-08-id-path-escaping.md`): both the reference and the port interpolated `file_id` / `batch_id` / `cache_id` / `video_id` verbatim into `…/files/{id}`-shaped paths.

## What this changes

One rule, ten pinned cases, two implementation edits, one harness refinement:

1. **The rule.** `docs/mapping-rules.md` gains MAP-11: an id placed in a URL path is RFC 3986 percent-encoded over its UTF-8 bytes. A resource-name dialect (Gemini: `files/abc`, `cachedContents/abc`, `batches/abc`, `models/m/operations/abc`) keeps `/` literal and encodes everything else, `:` included (the dialect appends its own `:download` / `:cancel`); a flat-id dialect (OpenAI, Anthropic, xAI) encodes `/` too. Never decoded first. Server-provided URLs (Anthropic `results_url`, a Gemini file `uri`) are not ids and stay verbatim.
2. **The pins.** `cases/<provider>/{files,batch,cache,video}_id_escaping.json` — ten hand-authored, build-only cases (no wire exchange: no provider has ever returned such an id) whose id carries a space, `?`, `#`, `%` and, on Gemini, `:`; the expected URL is `quote(id, safe)` applied by hand over each surface's live-captured route. files 39 → 48, batch 35 → 41, cache 9 → 11, video 24 → 27.
3. **The reference.** `lm15/providers/common.py` `path_id(id, resource_name=)`, applied at every id-in-path site of the four dialects (files get/delete/download, batch status/cancel, cache get/update/delete, video status/content).
4. **The harness.** `tools/audit.py` demanded a golden for every files/batch/video case; a golden pins parses, and a build-only case has none, so the rule now fires only when a step pins a body. `harness/fake_shim.py` found a surface case by provider alone and now matches (provider, op, id), since a provider has two cases on a surface. `harness/selftest.py`: baseline green, 37 mutations caught.

## Why

- An id is an opaque string the provider handed back. Pasted raw, a `?` starts a query string and a `#` a fragment: the request silently names a different resource. Neither implementation would notice; a 404 would look like "no such id".
- Of the three options, only "encode" has no silent failure mode. Doing nothing misroutes silently. Refusing ids with reserved characters is loud but throws away the caller's meaning where encoding preserves it. Encoding's one failure mode — a provider that returned a pre-encoded id gets double-encoded — is a 404, loud.
- `/` is the one character whose treatment is dialect-specific. Gemini's ids are resource names whose segments are the route. On a flat-id wire a literal slash changes the operation: `file_get("x/content")` would download `x`. So `/` is kept only where the wire's ids require it.

## Considered and rejected

- A uniform "keep `/` everywhere" rule (one sentence, simpler): rejected by the `x/content` example above.
- Rejecting reserved characters instead of encoding: strictly worse than encoding when encoding is unambiguous (see Why).
- Decoding before encoding ("normalize"): would make a legitimately `%`-containing id unreachable and hide what the provider actually returned. Sent as given.

## Evidence

- Every real id in the corpus and the live receipts (`file-…`, `batch_…`, `msgbatch_…`, `files/…`, `cachedContents/…`, `operations/…`, UUIDs) is path-safe: the ten new cases change no existing pinned byte.
- Reference and Rust after the fix: all fifteen directions green at this commit, both shims; `tools/audit.py`, `spec_drift.py`, `check_provenance.py`, `check_secrecy.py` clean; selftest OK.

## Trade-offs, stated

- Ten cases with no wire exchange enter the corpus. They pin a rule, not a capture; their provenance says so. The alternative — trusting two implementations to agree without a pin — is what let the gap exist.
- A provider that one day returns pre-encoded ids would need a MAP-11 amendment naming it; the failure would be a 404 on the first such id, never a wrong resource.
