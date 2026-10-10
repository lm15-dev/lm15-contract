# 2026-10-10 — A structured answer reads through `.text`; a thinking budget alone is enough

Status: written at the maintainer's request ("we need to find ways to make the
new tasks work on first attempts, either in the skills or in the library");
not yet ratified.

## How it was found

The coding-agent benchmark (lm15-dev `agent-bench/`, round 3: 882 runs, two
agent models, lm15 1.2.2) recorded the first `python solution.py` of every
run. Of 130 first runs that failed with LM15, two library behaviours caused
about 70:

1. **A schema with a boolean or enum property empties `.text` and `.json`.**
   MAP-14 answers a `json_schema` request that declares a judgment property
   with a `DataPart`. `Response.text` read only text parts, and `.json`
   parses `.text`, so both were empty while `.data` held the answer. A plain
   extraction schema with `vegetarian: boolean`, or an image question with
   `side: {"enum": ["left", "right"]}`, met this without asking for a
   judgment. About 50 first runs failed this way (`json.loads(None)`, "the
   model returned no text"), with and without the skill. Confirmed live on
   OpenAI, Gemini and Anthropic.
2. **`Reasoning(thinking_budget=1024)` was a TypeError.** `effort` has been
   required since 2026-09-02 so that `Reasoning()` does not mean off. A
   caller giving only a budget has stated an intent the grading table
   already maps; 17 first runs failed on the missing argument.

## Decisions

**D1. `Response.text` reads a `DataPart` answer as its compact JSON.** When
the message holds exactly one `DataPart` and otherwise only citation and
thinking parts, `.text` is the part's value rendered as on a text wire
(changes/2026-09-19-jev-state.md D3), so `.text`, `.parse_json()` and
`.json` read a structured answer whichever form the wire gave it. A message
with both text and data parts keeps `.text` empty (no guess about which is
the answer). `.data` is unchanged.

- Options: (a) answer with a `DataPart` only when probabilities are asked
  for; (b) make the accessors read it; (c) document `.data` and change
  nothing. Taken: (b). (a) changes what the wire reads into and the MAP-14
  cases, ratified 2026-09-17, for a problem that is in the accessors; (c)
  leaves `.text` empty for an answer the caller can see in the provider's
  own reply.
- Trade-off, stated: code that tested `response.text is None` to detect a
  judgment answer now sees JSON text. `.data_part` / `first(DataPart)` is the
  way to ask that question.

**D2. A `Reasoning` given only `thinking_budget` fills `effort`** from MAP-7
rule 3's table read the other way: the highest level whose budget is at or
below the given one (`minimal` below 1024). `Reasoning()` with neither is
still refused. A given `effort` is never changed. The canonical JSON always
carries `effort`, so serde is unchanged.

- On budget wires the budget is sent, as before (rule 5); on OpenAI and the
  chat dialect a budget still RAISES, so the filled word never reaches a wire
  that would read it differently from the budget.

**D3. Messages (no contract field).** Every SDK's `effort="none"` refusal
says lm15 spells it `"off"`; `thinking_budget=0` says the same; a
hand-built adapter with no key no longer says "set ANTHROPIC_API_KEY" (it
reads no environment, so that advice could not work): it names
`api_key=os.environ[...]` or the router.

## Pins

No harness direction exercises accessors or constructors from arguments, so
the rules are pinned by each SDK's own tests (`first_attempt` /
`test_first_attempt` / `test_types.py`), which check the table at every
boundary (512, 1024, 2047, 2048, 8192, 16384, 24576, 32768, 10^6) and the
`.text` rendering of a lone and a mixed `DataPart`. Contract checks:
1,904 of 1,904 in every SDK before and after.

| SDK | D1 | D2 | D3 |
|---|---|---|---|
| Python | `Response.text` | `Reasoning(thinking_budget=)` | effort, budget 0, adapter key |
| TypeScript | `Response.text` | `{ thinkingBudget }` | effort, budget 0, adapter key |
| Rust | `Response::text` | `Reasoning::with_budget`, `effort_for_budget` | adapter key |
| Go | `Response.Text` | `ReasoningBudget`, `Config.Validate` fills `Effort` | effort, budget 0, adapter key |
| Julia | `text(::Response)` | `Reasoning(; thinking_budget=)` | effort (adapter key already said so) |
| R | `response_text()` | `reasoning(thinking_budget = )` | effort, budget 0 |
