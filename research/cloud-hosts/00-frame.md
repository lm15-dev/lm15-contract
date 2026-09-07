# Cloud hosts — the frame (no provider words)

## What the user is trying to do

Reach a model they already know, through the cloud their company already
pays and already secured, with the identity the machine already has. They
did not choose the cloud for the model. They chose it for billing, data
residency, audit, and private networking. The model API is the same one
they would call directly; only the door is different.

## What the user wants to control

1. **Which door.** The same model name, prefixed by the host: the wire
   format does not change, the URL and the credential do.
2. **Where.** A region or location, because data residency is the reason
   the host exists. Sometimes a project, a resource, or a deployment name
   the cloud made them create.
3. **Which identity.** Usually none explicitly: the machine's ambient
   identity, in the order the cloud's own tooling would pick it. When they
   do choose, an explicit choice must beat every ambient one.
4. **Which endpoint.** A private endpoint, a sovereign cloud, a proxy, a
   custom certificate authority. All by configuration, never by code.

## What the user wants to observe

1. Which identity was used, and why the others lost (the doctor).
2. That the request went to the region they configured.
3. The same response, usage, and errors they would see through the
   public API of the same model. Nothing hidden by the host.
4. When a credential is expiring, that it refreshed, and where it came
   from.

## What must never happen

1. **A different identity than the cloud's own SDK would pick** on the
   same machine. That is a security bug: audit logs name the wrong
   principal; a permission boundary is crossed.
2. A credential leaves the machine in a form that is not what the cloud
   asked for (a private key sent instead of a signed assertion; a key
   logged; a signature computed over the wrong bytes and rejected in a way
   that reveals the secret).
3. A silent fallback from a configured identity to a weaker ambient one.
4. A request to a different region than configured, including for
   listing models, token exchange, and metadata.
5. A feature of the model that the host does not carry, silently dropped.
   The support row says what the door carries; a missing surface raises.
6. A token cached past its expiry, or refreshed by two processes at once.
7. A stream that the host re-frames (a different envelope than the public
   API) leaking that framing to the user: events are the canonical events.
8. Interactive login started by the library. The cloud's own tool owns it;
   the library reads what that tool stored and names the command to run.

## Questions the pass must answer with receipts

- For each host: the exact credential chain order in the cloud's own
  default credential resolver, with the environment variables, file
  paths, and endpoints of each rung.
- Which rungs need only HTTP and file reads; which need signing; which
  signing algorithm; what a fixed-clock, fixed-key test vector looks like.
- For each host and each dialect it carries: the URL template, where the
  model name goes, which body fields are removed or added, and how the
  stream is framed.
- Which model surfaces (files, batches, caches, listing, live) the host
  carries, and through which endpoint and signing scope.
- What the error envelopes look like when the host, not the model,
  rejects: wrong region, no model access, expired token, throttled.
- Which token lifetimes and refresh endpoints exist, and what the
  cloud's tooling stores on disk that we may borrow (format, path,
  expiry field).
- Regional, global, sovereign, and private endpoint host patterns.

## Out of scope for this pass

- Interactive login flows (device, browser). AUTH-9 stands: the cloud
  CLI owns them.
- Control-plane operations (creating deployments, granting model access).
- Cost accounting across clouds.
