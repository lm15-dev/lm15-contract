# 2026-09-06 — Offline contract tooling review before the next port baseline

Status: **tooling repairs reviewed; baseline approval remains blocked**. This entry
ratifies nothing and does not accept the mixed working tree as an oracle.
No live calls, access to real credentials, fixture re-scribing, or commits were made
in the tooling review. Those repairs leave wire bodies and canonical values
unchanged; 21 new cases have provenance-link corrections only. The later
parent correction to four stream goldens is recorded separately in
`2026-09-06-streamed-reasoning-state.md`.

## Repairs

- Capture dry runs use dummy credentials. AWS resolution is deferred until
  argument parsing, and SigV4 dry runs use the corpus test pair. Azure
  imports/help/dry runs do not load lab state; Entra probes cannot invoke
  CLIs or token exchange during dry runs. Batch dry runs now build all
  lifecycle requests without parsing an empty response or writing files;
  receipt and refusal writers respect dry-run mode.
- SigV4 capture refuses a chain result of `BearerToken`: it must not pin a
  bearer-authenticated call as evidence of a test-pair SigV4 signature.
- Failed model listings no longer become successful-surface fixtures.
  Azure Realtime capture has a main guard, explicit overwrite protection,
  and refuses dry-run work before credentials. Failed turns are receipts,
  not successful cases. Live-only ad-hoc bearer/mantle probes reject
  `--dry-run`; Nova's dry run uses fixed credentials. Azure provisioning
  rejects unknown/dry-run flags before state or paid operations and keeps
  recovery state if deletion fails. Secret outputs are created with a
  restrictive umask; bearer-token output replacement is atomic, mode 600,
  and does not follow an existing target symlink.
- New HTTP captures write a separate `exchange-<timestamp>-<uuid>.json`
  receipt for every completed exchange, with a hash of the **unredacted
  transport input** and a hash of the raw response. The hash format is
  stated in the receipt: UTF-8 compact JSON in order `method`, `url`,
  ordered `headers` pairs, `body_b64`. This is the adapter's transport
  input, not HTTP framing/headers later added by the network stack.
  `sent` is redacted, so its bytes cannot reconstruct that request hash.
  Individual run summaries are archived as well as updating `SUMMARY.json`.
  These additions do **not** retroactively supply missing capture hashes.
- Capture redaction covers query keys and explicitly overridden credentials,
  before console-summary truncation. Azure Anthropic beta probes use the
  live-accepted `x-api-key`; `api-key` remains an explicit negative probe.
  Mantle family probes send raw bodies so an existing canonical refusal
  does not prevent re-probing the wire. Canonical refusal assertions stay.
- Meta sibling-door provenance points to the actual shared Meta entry;
  Bedrock bearer provenance points to its bearer entry. Capture change
  slugs now support those shared/special entries rather than generating
  nonexistent per-door filenames.
- Harness `$file` reads and cloud auth-file writes are confined to the
  contract and sandbox HOME respectively; traversal, absolute paths and
  environment-file expansion are rejected. `PROTOCOL.md` corrects token
  op field names (`input`, parsed `body`), certificate-key expansion and
  SigV4 header handling to describe the pinned vector inputs. See
  `auth/token-vectors.json`, `auth/sigv4-vectors.json`, AUTH-2 and AUTH-11;
  no expected signature, JWT, credential, or response was changed.
- Secrecy scanning includes JSONL Realtime transcripts and frozen SigV4
  files. File exemptions are bound to fixed content digests as well as
  paths. Arbitrary AWS ids ending in `EXAMPLE` and arbitrary Bedrock
  tokens sharing a test-id prefix are no longer exempt. The existing
  documented examples/test-key material remain allowed, not real material
  inserted at those paths. Digest changes require review.
- The audit no longer calls stream framing or model placement token-vector
  coverage. Twelve policy enum names/mirrors are checked separately,
  exactly against spec table values; this is not runtime or serde coverage.
- Frozen-source fetching now records `saved_sha256` as well as the original
  response hash, since HTML-to-text conversion changes the saved bytes.
  Existing frozen sources/manifests were not rewritten.
- Added offline tooling regressions to CI and a signed-JWT build mutation
  to the comparator self-test. No assertion was weakened or comparator skip
  added. Capture-tool tests require the read-only Python sibling and are
  explicitly skipped when it is absent in a standalone contract checkout.

## Evidence and approval gaps remain

1. The cloud design has an existing recorded 2026-09-03 ratification.
   The Meta/live-door entries and the 2026-09-04 AUTH-2 bearer-key-header
   and AUTH-10 tenth-host amendments remain **pending**. In particular,
   `spec/vocabularies.md` still lists only `api_key` on `x-api-key`, whereas
   the draft AUTH-2 amendment admits `bearer_token`; ratification must
   reconcile them, not treat the green implementation as authority.
2. All 88 new goldens remain `scribe-draft`. Independent mapping reviews now
   exist under `research/baseline-review/`. Parent review corrected the
   missing Responses reasoning state under existing MAP-7 rules. Redacted
   thinking assembly, continuation policy, and the Azure pending-file fold
   still need decisions. New error expectations also need final acceptance.
   Offline equality does not supply this approval.
3. Existing live artifacts generally lack a contemporaneous request hash.
   SigV4 case signatures are regenerated with the test pair, not the actual
   sent authorization bytes. `SUMMARY.json` represents only the last run
   and sometimes just one `--only` feature. These limits cannot be repaired
   by inventing past receipts or hashing reconstructed requests as live ones.
4. The source manifest has 150 entries, all saved paths present. Of these,
   68 saved files match their original response hash and 82 HTML-to-text
   outputs have no saved-byte hash. This does not establish a hash mismatch
   in the source response; those original HTML bytes were not retained.
5. Meta terms review remains open. Azure Anthropic successful inference and
   Azure images are quota-blocked; Bedrock Claude is account-gated; AWS
   Platform and Vertex have no successful live pins here. Azure Batch proves
   upload/queue/status/cancel/list, not completed batch output. The proposed
   bearer-token-in-`x-api-key` path still lacks a successful harness wire
   capture. Event-stream framing is future phase-2 work, not token coverage.
6. Pre-existing tracked Moonshot sibling cases still contain 21 references
   to nonexistent per-door change filenames (the shared entry is
   `2026-09-03-moonshotai-wires.md`). Those are outside the new artifact
   repairs recorded here. The existing computer-use request/response skips
   and orphan allowlist entry also remain; no new skips were introduced.

## Offline validation

Independent offline checks also confirmed all 30 expected SigV4 stage
strings against the frozen AWS suite bytes, both JWT signatures using
OpenSSL and the corpus public key (no private key), their pinned claim
sets, and the certificate's `x5t` thumbprint. This verifies cryptographic
fixture integrity, not normative approval of the credential policies.

The full Python shim run uses `--no-check-pin` because the parent owns the
pin and commits. All fourteen directions are offline, including `live`
(which replays a recorded transcript). The parent report carries exact
counts and logs. Passing checks establish tooling consistency only; parent
review, canonical evidence review, and the missing approvals above remain
required before accepting a baseline.
