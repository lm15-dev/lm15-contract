# 2026-10-12 — The Muse Code subscription through the `meta` login

Status: amends the `meta` device profile (`auth/managed/profiles.json`) and
adds the managed run `meta-mint-subscription` (`auth/managed/runs/core.json`).
Decided in session 2026-10-12: the maintainer read the terms finding below
and chose the direct door ("Connect directly anyway"). The names, the
`meta.ai` address rule and the labels are the implementer's, stated here.

## Found

- The `meta` device login (Pi 0.87.0 port, `unverified`, no receipt) is the
  Muse Code subscription login. Live on a Power Usage plan
  (`receipts/2026-10-12-muse-code/`) it works as written, and the minted key
  reaches Muse Wonder Full (`muse-wonder-full-1.0`), which Meta sells only
  with the Power and Maximum Usage plans, on all three Meta wires.
- The mint reply carries what the port dropped: the API address
  (`base_url`) and the plan (`is_subs_active`, `subs_tier_name`).
- A re-mint answers the same key, so lm15's daily re-mint and Muse Code's
  own login never revoke each other.
- Meta's Model API terms (last updated 2026-10-09, § 3.2) say the Muse Code
  key "may not be used to access the Services outside the coding harness".
  Frozen with its hash in `research/providers/muse-code/sources/`.

## Changed

**D1 — The key goes where the mint says, and only to Meta.** A mint reply
with `base_url` stores it in the material (trailing slash removed);
`request_auth` returns it, and the router sends requests there. A value
that is not https on `meta.ai` or a `*.meta.ai` host, or that carries
userinfo or a query, is a `LoginDenied` before the key is sent anywhere. At
login that ends the attempt; at renewal the connection becomes
`needs_login`. No `base_url`: none, as before (the existing
`meta-device-login` run is unchanged).

**D2 — The connection names the plan.** `account_label` (untrusted display
text, AUTH-12) is the tier name when the subscription is active, "no Muse
Code subscription (pay-as-you-go)" when Meta says it is not, and absent when
the reply does not say. lm15 does not refuse a key without a plan: Meta
bills it pay-as-you-go, and the label says so.

**D3 — Still `unverified`, with the reason.** The method keeps
`availability: unverified`. Its reason now records the live evidence and the
terms clause, so `connect()` and every descriptor reader show why. A caller
opts in with `allow_unverified=True`, as for `claude-code` and
`openai-codex`.

**D4 — lm15 does not pretend to be Muse Code.** Muse Code sends
`x-client-id: tbh:exec` and a `muse-build/…` user-agent. Meta accepted the
key without either (live), so lm15 sends its own `lm15` identification, as
the `openai-codex` door does with `originator: lm15`. If Meta starts
requiring them, adding them is one header table entry.

## Not changed (stated trade-offs)

- **No reading of Muse Code's own login** (`~/.config/muse/auth.json`), the
  counterpart of the `claude-code-cli` and `codex-cli` external sources. Its
  layout is known only from the binary's strings, never from a real file.
  Add it once a `muse login` file has been seen.
- **`meta-chat` and `meta-anthropic` under a managed `Auth`.** The
  connection lists all three routes, but the managed router looks a
  connection up by the route's own name, so only `meta:` uses it today. This
  gap predates this change and applies to every multi-route descriptor.
- **Contributor mode.** Subscription traffic is Contributor mode by default
  (terms § 3.3): Meta may train on it unless the account setting is changed.
  lm15 neither reads nor changes that setting.

## Receipts

`receipts/2026-10-12-muse-code/REPORT.md` and `probe.json`.

## Ports

Python is the reference. Every port with the `meta` flow (TypeScript, Rust,
Go, Julia, R) carries D1 to D3 and passes `meta-mint-subscription`.
