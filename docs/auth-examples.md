# Authentication journeys — contract examples

**REVIEW DRAFT, 2026-09-22. These are static design examples, not executable
notebooks or claims about the installed SDKs.** Names illustrate idiomatic bindings;
[AUTH-12–26](../spec/auth-managed.md) fixes the behavior. Do not run these against
current packages or infer an implementation from one language's pseudocode.
Section 5 and the `begin_login`/`resume_login` calls in section 6 illustrate
[reserved](../spec/auth-managed-reserved.md) rules (resumable login across
requests); they bind nobody until promoted. Sections 1–4, 7 and 8 are core.

## 1. One deliberate setup operation, no provider strings to memorize

Python, interactive terminal:

```python
from lm15 import Message
from lm15.interactive import connect

with connect() as lm:
    print(lm.selection)  # account/route/model summary, never tokens
    answer = lm.complete(messages=[Message.user("Explain drought stress.")])
    print(answer.text)
```

TypeScript, interactive terminal:

```typescript
import { Message } from "lm15";
import { connect } from "lm15/interactive";

const lm = await connect();
try {
  console.log(lm.selection); // safe selection summary
  const answer = await lm.complete({ messages: [Message.user("Explain drought stress.")] });
  console.log(answer.text);
} finally {
  await lm.close(); // release owned resources; not logout
}
```

Illustrative screen, not captured output:

```text
Connections are saved privately on this computer.
Store: ~/.config/lm15/credentials.json

Use a saved connection, or connect another?
  My ChatGPT connection
  Connect another account or API key

Choose an available model
  [account catalog with exact route and source]

Ready: [connection label], [route], [model]
```

- No global account is installed. The returned client owns its selection.
- There is no paid verification prompt. Only the explicit `complete` does inference.
- Closing does not erase the saved connection. Next run may offer it for reuse.
- If model choice is cancelled after login, the UI says the login remains saved.
- A noninteractive server calling bare `connect()` receives interaction_required,
  not a prompt that hangs a worker. Use explicit scoped construction instead.
- A single available method may be mechanical; identity/billing is still shown.

## 2. The advanced pieces are the same ones

Python:

```python
from lm15 import LMRouter, RouterConfig
from lm15.auth import Auth, providers
from lm15.auth.terminal import TerminalUI

ui = TerminalUI(open_browser=False)  # useful over SSH
with Auth.local() as auth:
    methods = auth.methods(providers.openai_codex)  # definitions only
    connection = auth.login(providers.openai_codex, ui=ui)
    router = LMRouter(RouterConfig(auth=auth))
    choices = auth.model_choices(connection, refresh=True)  # explicit catalog I/O
    selection = ui.choose_model(choices)
    with router.bind(selection) as lm:
        print(lm.selection)
```

TypeScript:

```typescript
import { LMRouter } from "lm15";
import { providers } from "lm15/auth";
import { createLocalAuth } from "lm15/auth/node";
import { terminalUI } from "lm15/auth/terminal";

const auth = createLocalAuth();
const ui = terminalUI({ openBrowser: false });
try {
  const methods = auth.methods(providers.openaiCodex);
  const connection = await auth.login(providers.openaiCodex, { ui });
  const choices = await auth.modelChoices(connection, { refresh: true });
  const selection = await ui.chooseModel(choices);
  const lm = new LMRouter({ auth }).bind(selection);
  try { console.log(lm.selection); }
  finally { await lm.close(); }
} finally {
  await auth.close(); // explicit owner closes the supplied manager
}
```

The named descriptors are discoverable by autocomplete; dynamic choices can be
passed back as descriptors. IDs remain useful in saved configuration. UI labels
are never parsed into IDs. The model selection contains the exact routed model,
Connection ID and trusted instance revision, not a token or a bare model name.

## 3. Inspect versus verify versus use

```text
methods(provider)                 no file, callback, subprocess or network
connections()                    scoped metadata read, no network
status(connection)               scoped metadata read, no renewal
router.explain_auth(route)        actual source selection, no acquisition
verify(connection)               explicit supported provider check; may renew
model_choices(connection, true)  explicit catalog request; may renew
complete(request)                selected auth preparation and model request
```

Example saved-state view:

```json
{
  "presence": "saved",
  "usability": "renewal_due",
  "verification": {
    "state": "valid",
    "checked_at": "2026-09-22T10:00:00Z",
    "check_id": "provider-account-check"
  }
}
```

This says a check passed then, not that the account can use every model now.
Unreadable storage is an error, not `{ "presence": "absent" }`.

## 4. API keys and existing Azure code do not need this wizard

Existing unmanaged Python configuration keeps its meaning:

```python
router = LMRouter(RouterConfig(api_keys={"openai": my_key}))
router = LMRouter(RouterConfig(credentials={"azure": "platform"}, settings=azure_settings))
```

To deliberately save a key in managed storage:

```python
connection = auth.set_api_key(providers.openrouter, key=my_key)
router = LMRouter(RouterConfig(auth=auth))
```

`set_api_key` saves, does not verify, and refuses to replace a connection without
an explicit expected target. It does not set environment variables. Values are
literal keys, not a shell-command or variable-interpolation language.

A saved cloud setup is explicitly a source recipe:

```python
connection = auth.configure(providers.azure, source="platform", settings=azure_settings)
```

No token is acquired until an explicit verification/catalog/model operation needs
one. The existing Azure named-platform behavior remains its meaning. Choosing a
cloud chain, rather than a deterministic named source, is visible and may select
a different principal as the environment changes; it is not a pinned account.

## 5. Web/server login that survives redirects (reserved tier)

The server owns application login/session authorization. The provider login is
an additional connection, not a substitute for authenticating the app's user.

Language-neutral HTTP controller sequence:

```text
POST /connections/start (CSRF-protected)
  authenticate application user
  auth = manager over that user's authorized store scope
  attempt = auth.begin_login(selected_descriptor,
                             method=selected_supported_method,
                             return_uri=SERVER_CONFIGURED_CALLBACK)
  save attempt.id in that user's server-side session
  return only attempt's safe next UI step to that user

GET /connections/callback
  authenticate the returning application session
  retrieve its attempt.id (do not accept another user's ID from the URL)
  auth = manager over the same authorized scope
  attempt = auth.resume_login(attempt.id, callback(returned_url), step_revision)
  remove code/state from the browser location with a clean redirect
  display committed Connection, or the next safe step/problem
```

For cross-site identity-provider returns, the app chooses an appropriate session
cookie/handoff mechanism and CSRF/state defenses; it must not assume a cookie
will be sent in every redirect mode. If the session is unavailable, recover app
session ownership first, never accept the provider code as proof of scope.

The private verifier/device code is in the store. A second process can continue
with the same trusted definitions. Duplicate success returns the recorded result;
it does not repeat token exchange. A returned Connection describes the original
commit; current `status` is checked if another tab may already have logged it out.

Browser-only OpenRouter is the same state machine with explicit tab-scoped storage
and an approved return URL. It is not a permission to embed client secrets, read
CLI files, or assume another provider permits direct browser exchanges.

## 6. Replacing and forgetting an account

```text
current = status(binding).connection
new = login(binding, ui=ui, replace=current.id, expected_generation=current.identity_generation)
# current remains usable while the user approves the new account
# (reserved tier: the same with begin_login / resume_login across requests)
# new has a new ID; an old bound client now fails connection_changed

logout(new.id)
# removes it locally, invalidates pending work, does not revoke remotely
logout(new.id)
# idempotent; must not erase a later replacement
```

Cancellation before commit preserves the previous connection. Cancellation after
commit does not undo it: inspect the attempt and use explicit logout if desired.
An in-flight request already admitted for sending may finish after logout.

## 7. Canonical request construction remains available

```python
lm = connect(capability="structured-output")
try:
    req = lm.request(
        messages=[Message.user(abstract)],
        config=Config(response_format=answer_schema),
    )
    print(req.model)       # exact selected route:model
    response = lm.complete(req)
finally:
    lm.close()
```

`lm.request` is pure. It does not renew credentials or contact a provider.
The result is a canonical Request, and complete returns the full Response,
including usage, adaptations and continuation data. A conflicting model in a
supplied Request is selection_mismatch, not a silent switch.

For a chatbot, append `response.message`, not reconstructed display text. For
classification, each input row is an explicit request; LM15 does not silently
batch, retry or create a conversation between unrelated rows. DuckDB functions
that make requests must be marked as side-effecting and results materialized
before export. These remain application recipes, not new auth abstractions.

## 8. Language idioms without changing the contract

| Language | Natural shape | Cancellation |
|---|---|---|
| Python | sync `Auth`, native `AsyncAuth`; keyword options; context managers | explicit sync cancel control / asyncio task cancellation |
| TypeScript | promise operations, options objects, synchronous local descriptors | AbortSignal |
| Rust | async Result; small builders for options; owned/shared scoped handles | documented task/drop behavior plus durable cancel |
| Go | ordinary options structs, explicit errors | context.Context |
| R | `connect_interactive`, `auth_login`, client-first verbs, table-friendly metadata | interrupts and explicit cancel controls |
| Julia | ordinary functions and structured values | task interruption |
| Java | typed result/interfaces and options | interruption/cancellation controls |
| .NET | Task-based I/O and typed options | CancellationToken |
| Ruby | keyword arguments, ordinary values and explicit block/resource lifetimes | documented interruption/cancel hook |
| Swift | async/await, Sendable-safe values and scoped services | task cancellation |

R illustration: `lm <- connect_interactive(capability = "structured-output")`.
Go illustration: `lm, err := interactive.Connect(ctx, options)`.
Rust illustration: `let lm = interactive::connect().await?;`.
These are spellings of the same operation, not independent behavior contracts.

A user interface should show safe actionable guidance such as:

```text
Your selected connection could not be renewed.
Sign in again deliberately. No other account was used.
```

An expired attempt says to start a new attempt. A storage failure says the login
was not safely saved (or the commit outcome is unknown). A generic retry button
must not repeat a possibly consumed authorization code. Typed reasons, not text
matching, govern those choices.
