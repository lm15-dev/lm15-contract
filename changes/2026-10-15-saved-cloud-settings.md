# 2026-10-15 — A saved cloud recipe's settings reach the request (AUTH-15)

Request: Maxime Rivest, 2026-10-15, in session ("take that branch, add the
additional fix and merge, and do the change in all other languages"), over
lm15-python pull request #21 by Rolf Fredheim (`fix(router): preserve managed
cloud settings and provider aliases`). D1 is what AUTH-15 already says. **D2
and D3 state a precedence the text left open and await Maxime's
ratification**; each is one line in each port.

## The problem

`Auth.configure(provider, method="cloud", answers={"named": …},
settings={"project": …, "location": …})` saves a cloud recipe with its host
settings, and AUTH-15 says executing the recipe "uses the existing cloud rules,
including their settings". Every port saved the settings and then built the
managed route from the router's own `settings` entry alone: a Vertex recipe
saved with its project failed at construction with "setting 'project' is
required", or quietly took `GOOGLE_CLOUD_PROJECT` and the default location
`global` instead. Found by Rolf
Fredheim in lm15-python; the same omission was confirmed by reading the managed
router of TypeScript, Rust, Go, Julia and R.

lm15-python also read the router's `settings` entry by the exact provider
string on three paths (managed, unmanaged cloud doors, `plan()`) and the
doctor, so `settings={"vertex_anthropic": …}` was ignored although AUTH-1
accepts the underscore spelling for every per-provider entry. The other five
ports already matched either spelling.

## Decisions

**D1 — A selected cloud recipe's saved settings are the route's host
settings.** They are given values: ahead of the environment and of the cloud's
own configuration, as an explicit entry is.

**D2 — The router's explicit settings entry refines them setting by setting.**
`settings={"vertex-anthropic": {"project": "other"}}` over a recipe saved with
a project and a location sends the other project and the saved location. The
entry is matched under either spelling of the provider.

**D3 — An explicit credential selects no connection.** With an `api_keys`
entry or a named identity in `credentials`, the scope's connection is not
consulted (AUTH-15 order), so none of its settings apply: the settings come
from the explicit entry, then the environment, as on an unmanaged router.

## Evidence

`auth/managed/runs/core.json` case `cloud-recipe-settings` (expectations
captured from lm15-python with the fix and read against D1–D3): one saved
Vertex recipe, `GOOGLE_CLOUD_PROJECT` set, then four routes — the saved
settings alone; an underscore-spelled entry naming the project; a
hyphen-spelled entry naming the location; an explicit key with a location
entry (the project then comes from the environment). The harness gains the
`route` step (PROTOCOL.md § managed_run). lm15-python at 48ab49d fails the
case: it builds the route with the environment's project and the default
location `global`, as though nothing had been saved. Every port passes it
after its fix.

## Not changed

- `plan()` still builds with placeholder settings where the explicit entry
  and the environment give none: it reads no saved connection, by design
  ("no stored login is read"). A managed route whose project lives only in its
  saved recipe therefore plans with the placeholder project. Recorded, not
  fixed here.
- `configure` does not check a recipe's settings against the door's host
  settings; an unknown name now fails at the first request
  (`unknown host setting(s)`), where before it was ignored.
