# 2026-09-01 — video generation: the ticket pattern's third factory

Ratified: Maxime Rivest, 2026-09-01 ("go, implement the video gen"),
over the design draft's 7 decisions (drafted and desk-checked earlier
the same day; graduated with the implementation).

## Contract surface

- Types: `VideoGenerationRequest` (model, prompt, `seconds`, `images`,
  extensions) and `VideoJobInfo` (id, status, progress %, created_at,
  model, provider_data). New closed `VideoStatus` vocabulary —
  `queued`/`running`/`completed`/`failed`/`cancelled` — reusing batch's
  words where meanings match; provider wire words (`pending`, `done`,
  `in_progress`) stay verbatim in provider_data.
- The result of a completed job is a `VideoPart` in the provider's own
  delivery mode: bytes for Sora (content endpoint, media type from the
  header) and Veo (the file URI is KEY-BOUND — 403 without the header,
  verified live — so a URL part would be unusable), a public URL for
  xAI (no-auth download verified).
- Honest raises: `seconds` on xAI (no wire slot); `images` on all
  three until the mappings are live-receipted (named reason: xAI's
  wire silently ignores unknown fields — pixel-verified during the
  edits campaign — so an unverified mapping could silently produce
  prompt-only videos); `video_list` on xAI (no endpoint, probed 404 —
  the stored ticket is the only copy, and no hidden local journal
  papers over it); Gemini lists per model (`model=` required).
- Support matrix: `EndpointSupport.video` pinned true for openai,
  gemini, xai. Routing rules `sora-` → openai, `veo-` → gemini.

## Serde and harness

Two kinds (`video_generation_request`, `video_job`, 4 fixtures, 94/94
corpus green). New `video` harness direction — `video_op_build` /
`video_op_parse` — with step cases for all three providers from live
captures (Sora submit→in_progress→completed + 1.4 MB MP4 content; Veo
operation→done + key-bound download; grok-imagine request_id→pending→
done + public URL). 24 results green; two new selftest mutations
(status vocabulary drift, delivery-URL drift) caught red — 21 total.

## Evidence

`lm15-contract/receipts/2026-09-01-video/` (Sora + Veo transcripts and
downloaded MP4s) and `receipts/2026-09-01-xai/` (grok-imagine). Live-proven
end-to-end via the shipped code: re-attach by id on all three wires,
results delivered in each honest mode, listing where wires list.
