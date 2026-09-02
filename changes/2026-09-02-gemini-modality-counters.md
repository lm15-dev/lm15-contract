# 2026-09-02 — Gemini audio modality counters reach the audio slots

Ratification: accepted in advance — Maxime Rivest, in session ("i accept
all your recommendations"), for the recommendation in
`2026-09-02-review-followup.md` (review §4 item 7). One of the four
amended goldens is REVIEWED (`gemini.audio_inline`, June review); its
amendment is flagged here and carries an `amended` line. Stamp on reading.

## What changed

Gemini `promptTokensDetails[modality=AUDIO]` → `input_audio_tokens`;
`candidatesTokensDetails` / `responseTokensDetails[modality=AUDIO]` →
`output_audio_tokens`. Absent entry → `None` (INV-029). IMAGE and VIDEO
modalities have no canonical slot and stay in `provider_data` (stated).

Goldens: `gemini.audio_inline` (reviewed; `input_audio_tokens: 4`),
`gemini.live_text` (`output_audio_tokens: 28` on the turn end),
`gemini.live_tools` (56), `gemini.speech_gen` (59). Values are the
bodies' own numbers; the reference test
`test_gemini_modality_breakdowns_fill_the_audio_slots` pins the mapping
and the absent case.
