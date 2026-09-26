# Gemini Live accepts parametersJsonSchema (2026-09-26)

lm15-python (MAP-16 build), `GeminiLM.live(LiveConfig(model="gemini-3.1-flash-live-preview", tools=(get_forecast,)))`,
where get_forecast's parameters carry `"additionalProperties": false`. The setup frame sent
`setup.tools[0].functionDeclarations[0].parametersJsonSchema` (verbatim schema); the server
answered setupComplete, and after `send_text("Use the tool: forecast for Montreal on 2026-10-01.")`
the session yielded `tool_call get_forecast {"location": "Montreal", "date": "2026-10-01"}`.
Observed by hand from the terminal; no frames were kept (the Live transcript format is the
2026-09-01 recorder's, not rerun here).
