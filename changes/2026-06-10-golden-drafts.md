# 2026-06-10 — response/stream golden DRAFTS + harness mutation self-test

Tool: `tools/scribe_goldens.py` (committed, rerunnable; re-running on an
unchanged corpus rewrites identical drafts).

## What was drafted

For each of the 69 cases carrying both `canonical_request` and `pinned_body`,
the scribe replayed the pinned body through the reference vet shim
(`python -m lm15.vet` @ lm15-python2 HEAD) — `parse_response`, or
`replay_stream` for the 3 stream cases — and wrote
`goldens/<provider>/<feature>.json`:

- `canonical_response`: the materialized canonical Response.
- `events`: the full canonical event trace (stream cases only).
- `provenance`: `{"source": "scribe-draft", "date": "2026-06-10", "evidence":
  "derived from pinned body via python -m lm15.vet @ lm15-python2 HEAD;
  DRAFT — not frozen, see AUTHORITY.md", "pinned_body": "<filename>"}`.

Counts: **69 drafted, 0 failed, 0 no-body**; the 27 allowlisted orphans (no
`canonical_request`) drafted nothing. Bodies that are error bodies or whose
parse fails are recorded in `goldens/_failures.json` — currently empty, the
file exists so an empty failure set is explicit, not ambiguous.
`harness/check.py` was pointed at the new layout (previously a placeholder
`goldens/<case_id>.json`, flagged "define/adjust when goldens land").

## DRAFT status and the circularity (read this before trusting green)

These goldens are canonical facts derived from lm15-python2, which holds
**no oracle authority** (AUTHORITY.md, canonical-facts precedence: normative
rules > contract fixture > reference > ports). Running the python shim
against its own drafts is green **by construction**:

- `--direction response`: pass 66 / fail 0 / skip 25 (no-golden orphans)
- `--direction stream`:   pass  3 / fail 0 / skip  2 (no-golden orphans)

That green means exactly one thing: the drafts pin the reference's CURRENT
parse behavior, so any future regression in lm15-python2 — and any divergence
in a port — goes red against a recorded baseline. It does NOT mean the parses
are correct. Correctness is established only at freeze.

The comparator behind that green is itself tested: `harness/selftest.py`
(CI step in `.github/workflows/contract.yml`) replays recorded-correct
outputs through `harness/fake_shim.py` with injected mutations — wrong tool
name, garbage text, absent-vs-empty flip, usage off-by-1000, dropped stream
event, bool-as-int — and fails unless every mutation is caught red with the
first-difference at the mutated path. The fake shim must never be registered
in `harness/shims.json`: an oracle-echo shim is green by construction.

## Freeze procedure (per AUTHORITY.md)

Promoting a draft golden to an authoritative canonical fixture is a human
act, never an agent repair loop:

1. **Human review** of the golden's `canonical_response` (and `events`)
   against the normative rules — `docs/serde-rules.md` and the type
   docstrings (the forthcoming numbered invariants) — for the mapping of the
   pinned provider body into canonical types. The pinned body itself is a
   wire fact and already carries wire provenance on its case.
2. **Spec citation recorded**: the reviewed golden's `provenance` is rewritten
   from `scribe-draft` to a frozen source with the rule citation as
   `evidence`, in the same commit as a `changes/` entry naming the rules
   applied (AUTHORITY.md: a canonical fixture changes only with a spec
   citation).
3. After freeze, a frozen golden never changes to make an implementation
   pass. An implementation that disagrees with a frozen golden is wrong
   unless a normative rule says otherwise — then the rule is cited and the
   golden re-frozen, never silently edited.

Until step 2 happens, every file under `goldens/` is a DRAFT and its green is
a regression pin, not a correctness claim. Note: `tools/check_provenance.py`
does not yet scan `goldens/` (its allowed sources are wire-fact sources);
extending it to enforce golden provenance is freeze-time work.

## Gates run

- `tools/scribe_goldens.py`: drafted 69, failed 0, no-body 0,
  no-canonical-request 27.
- `harness/check.py --shim python --direction response`: 66/0/25;
  `--direction stream`: 3/0/2 (circular green, see above).
- `harness/selftest.py`: baseline green in all 5 directions, 6/6 mutations
  caught red (verified non-vacuous: an intentionally weakened comparator
  makes it exit 1).
- `tools/check_provenance.py`: OK. `tools/audit.py`: OK.
- `lm15-python2/conformance/run_all.py --strict`: OK; pytest: 252 passed.
