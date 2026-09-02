# Design pass — how a cross-provider concept becomes a contract rule

A design pass is the procedure for any concept that must mean one thing
across many providers (caching, reasoning, tool choice, structured
output, ...). It exists because a mapping designed from two providers and
memory is found wrong on the third provider, months later. A pass ends in
receipts and a `changes/` entry, never in an opinion.

Run it with an agent that has full context and no design opinion. Judge
its output with one question: does every claim point at a receipt?

## Inputs the agent receives

1. `AUTHORITY.md`, `spec/*.md`, `lm15-python/docs/mapping-rules.md`,
   `lm15-dev/THEORY.md`.
2. The current adapter code for the concept.
3. Today's scrapes (`curl-fixtures/api-references/`) and the live model
   listings (`lm15-dev/model-listings/`).
4. Credentials through the environment; a dollar budget stated up front.
5. The exact deliverables (§8 and §9 below).

## Steps

1. **Frame without provider words.** One page: what the user controls,
   what they observe, what must never happen. This is the yardstick.
2. **List providers, including ones lm15 lacks.** A design that fits
   today's adapters breaks on the fifth provider.
3. **Scrape primary sources, dated, verbatim.** No memory. Save each page
   with URL, date, sha256, and HTTP status in a manifest.
4. **Fact sheet per provider, same columns for all.** Blank cells are
   findings too. Every cell cites a line in a scraped page.
5. **One experiment matrix, run live everywhere a key exists.** Same
   cells for every provider. Fresh nonces so earlier runs cannot pollute.
   Repeat the noisy cells. Record usage fields AND latency. Record cost.
6. **Abstract model, then map every provider into it.** For every
   canonical field and provider: native, extension, or raise. Never
   silent. Every cell implementable in Go and Rust.
7. **Attack it.** Different lenses: cold learner, library author on top,
   port implementer, cost accountant, provider-switcher mid-conversation.
   Concrete scenarios with stated outcomes. If a second agent is not
   available, say so; a self-review is weaker and must be labelled.
8. **Decision record.** One `changes/` entry: receipts, counter-evidence,
   the rule (a MAP number), spec table rows, trade-offs. Marked pending.
   The maintainer ratifies. This is the only step that needs a human.
9. **Fixtures before code.** A case per provider per behaviour, pinned
   bodies, goldens, a harness direction if there is a lifecycle. Then the
   reference implementation. Then port spec text.
10. **Expiry.** Every fact sheet carries a re-check date and the script
    that reruns step 5. Red before a user finds it.

## Outputs, by path

- `research/<concept>/00-frame.md`
- `research/<concept>/sources/manifest.json` + the pages
- `research/<concept>/10-facts-<provider>.md`
- `research/<concept>/20-experiments.py` + `20-results.json`
- `research/<concept>/30-model.md` (abstract model + mapping table)
- `research/<concept>/40-attack.md`
- `changes/<date>-<concept>.md` (pending)
- `cases/`, `bodies/`, `goldens/` additions

## Rules of the pass

- Nothing from memory. A claim without a scraped line or a receipt is
  deleted, not softened.
- Spend is stated before it happens and totalled after.
- Secrets never enter `research/`; the capture helper redacts headers.
- The pass may conclude "raise" for a provider. That is a valid design.
