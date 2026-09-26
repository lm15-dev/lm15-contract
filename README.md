# lm15-contract

The specification and test corpus that every lm15 implementation is graded
against. lm15 is one request and response model for AI model providers,
implemented separately in Python, TypeScript, Rust and Go (and Julia, R and
earlier ports in progress). This repository is what makes them the same
library: the same program builds the same request and reads the same answer
in every language, because each one passes the checks defined here.

**This repository is the authority, not any implementation.** Read
[AUTHORITY.md](AUTHORITY.md) first: it says which evidence wins when things
disagree (live provider behavior, then provider documentation, then the
recorded fixtures, then any implementation, including the Python
reference) and how each kind of fixture may change.

## Where the languages stand

| Implementation | Release | Contract pin | Checks |
|---|---|---|---|
| [lm15-python](https://github.com/lm15-dev/lm15-python) (reference) | 1.0.1 | see its `CONTRACT_PIN` | all pass |
| [lm15-ts](https://github.com/lm15-dev/lm15-ts) | 1.0.0-rc.1 | `3763eec` | 1,583 / 1,583 |
| [lm15-rs](https://github.com/lm15-dev/lm15-rs) | 1.0.0-rc.1 | `3763eec` | 1,583 / 1,583 |
| [lm15-go](https://github.com/lm15-dev/lm15-go) | v1.1.0-rc.1 | `3763eec` | 1,583 / 1,583 |

Measured 2026-09-26 with `harness/check.py --direction all` at each pin.
[playbooks/parity.md](playbooks/parity.md) is the dated ledger.

## What's inside

| Path | What it holds |
|---|---|
| [`spec/`](spec/) | The canonical types, closed vocabularies and numbered invariants (`types.md`, `vocabularies.md`, `invariants.md`), credentials and sign-in (`auth.md`, `auth-managed.md`), the scope of 1.0 (`SCOPE.md`), and each provider's support and evidence (`support-matrix.json`). |
| [`docs/`](docs/) | The normative rules for exact JSON (`serde-rules.md`) and for mapping to and from each provider's wire (`mapping-rules.md`, MAP-1 to MAP-16). |
| `cases/`, `bodies/`, `errors/` | Recorded provider traffic: the request each case must build, the exact bytes the provider answered, and error envelopes. |
| `goldens/` | The canonical response and stream events each recorded answer must read as. |
| `serde/`, `mapping/`, `consumer/`, `router/`, `auth/` | Vectors: JSON round trips, content-decided mapping rules, bounded collection, model-string routing, credential resolution, signing, token exchange and the sign-in runs. |
| `receipts/` | The evidence behind each live capture: when, against which model, and hashes of the exact exchange. |
| `changes/` | One record per decision or rule change, with its evidence. |
| `harness/` | The language-neutral grader: [PROTOCOL.md](harness/PROTOCOL.md) (what an implementation's test shim speaks), `check.py` (the runner and comparator), `selftest.py` (proof the comparator catches drift). |
| `tools/` | Checks on the contract itself: provenance, secrecy, coverage, drift between spec and reference. |
| `research/`, `scrapes/` | Capture scripts and provider documentation snapshots. |
| [`playbooks/`](playbooks/) | [port.md](playbooks/port.md) (how to write a new language, module by module), [api-family.md](playbooks/api-family.md) (the public API shape every language follows). |

## How an implementation is graded

Each implementation ships a small program, its *vet shim*, that reads JSON
requests on stdin (build this request, parse this reply, replay this stream,
explain this credential...) and answers on stdout. The harness drives it in
a sandbox with no network and does all the comparing itself, in 18
directions: requests, responses, streams, errors, serialization,
credentials, token exchange, models, realtime sessions, files, batches,
media generation, video, stored caches, routing, Chat Completions ingest,
mapping vectors and sign-in.

```bash
python3 harness/check.py --shim python --direction all   # or typescript, rust, go
```

The harness refuses to grade an implementation against any commit other
than the one in its `CONTRACT_PIN`; use a clean checkout at that commit for
a reproducible result (`--no-check-pin` is for local development only).
Shims are registered in [harness/shims.json](harness/shims.json).

## Checking the contract itself

```bash
python3 tools/check_provenance.py     # every fixture says where it came from
python3 tools/check_secrecy.py        # no credential anywhere
python3 tools/audit.py
python3 tools/spec_drift.py           # needs ../lm15-python
python3 tools/check_content_coverage.py
python3 tools/check_gateway.py
python3 -m unittest discover -s tools -p 'test_*.py'
python3 harness/selftest.py           # the comparator catches every injected mutation
```

CI runs all of these on every push. The self-test proves the comparator has
teeth; it does not prove any implementation passes.

## Changing the contract

- **Recorded traffic** (`cases/`, `bodies/`) changes only with a new live
  capture and its receipt, recorded in a `changes/` entry.
- **Canonical fixtures** (`serde/`, goldens, `expect_lm15`) change only
  with a citation of the rule that makes the new value right.
- **A normative rule** changes only with a `changes/` entry explaining
  why, in the same commit; rules are ratified by the maintainer.
- Changes land here first; the Python reference moves its pin with the
  matching code, then each port.

Goldens drafted from the reference stay marked `scribe-draft` until an
independent review adds a `reviewed` line; a green harness run does not
approve them.
