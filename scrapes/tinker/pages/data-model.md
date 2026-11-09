# Data Model & Permissions

This page explains how Tinker organizes your data — organizations, projects, sessions, training runs, and checkpoints — and how access control and sharing work across them. Everything here applies equally to the [Tinker Console](https://tinker-console.thinkingmachines.ai) and the SDK: if the Console shows you a checkpoint, you can load it via the SDK, and if a role denies an action in one, it denies it in the other.

## The resource hierarchy

Tinker organizes data in this hierarchy:

```text
Organization
  ├─ Users
  ├─ Teams
  └─ Projects
       └─ Sessions  (one per ServiceClient)
            ├─ Training runs  (one per TrainingClient, one or more per session)
            │    └─ Checkpoints  (one or more per training run)
            └─ Sampling clients  (one per SamplingClient, one or more per session)
```

**Organization**: your top-level Tinker account. Billing, user management, and org-wide settings live here. A user can belong to multiple organizations, and organizations are completely isolated from each other.

**User**: an individual member of an organization, identified by email.

**Team**: a group of users within an org. Teams exist so you can grant project access to multiple users at once.

**Project**: the data-isolation boundary. Sessions, training runs, and checkpoints belong to a project, and access is governed by project membership.

**Session**: a connection between your SDK and Tinker. A [`ServiceClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/serviceclient/index.md) creates its session lazily when first needed, normally when creating a training or sampling client, and keeps it alive for that client's lifetime. Constructing the service client alone does not create a session. Every session belongs to a project: pass `project_id` to `ServiceClient(...)` to scope it to a specific project, or omit it and the session lands in your org's [Default project](#the-default-project). A session can host one or more sampling clients (one per [`SamplingClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/samplingclient/index.md)); each sampling client targets a single sampler checkpoint and shares the session's project scope.

**Training run**: a single fine-tuning workstream inside a session. A training run corresponds 1:1 with a [`TrainingClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/trainingclient/index.md) (created by [`create_lora_training_client()`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/serviceclient/#create_lora_training_client)). A session can have more than one training run — for example, when you train two models concurrently by calling `create_lora_training_client()` twice. The API sometimes refers to a training run as a "model" because it's tied to a `model_id`; the two terms mean the same thing.

**Checkpoint**: weights saved from a training run, identified by a `tinker://` path. The two checkpoint types used for training and sampling within Tinker are:

|                                        | `SAMPLER_WEIGHTS`            | `WEIGHTS`                      |
| -------------------------------------- | ---------------------------- | ------------------------------ |
| Created by                             | `save_weights_for_sampler()` | `save_state()`                 |
| Contains                               | weights only                 | weights + full optimizer state |
| Can be sampled from                    | ✓                            | — (returns a `400`)            |
| Can initialize / resume a training run | —                            | ✓                              |

To sample from a training run's current state, save a `SAMPLER_WEIGHTS` checkpoint with `save_weights_for_sampler()`; to branch or resume training, save a `WEIGHTS` checkpoint with `save_state()`. For files to use outside Tinker, `save_weights_external()` creates an `external_weights` checkpoint instead; see [Download weights](https://tinker-docs.thinkingmachines.ai/tinker/howto/checkpoints/#download-weights).

Every checkpoint inherits its project from the session that produced it — only sessions are attached to projects, and training runs and checkpoints both inherit that project.

### Creating an organization

When you first sign in to Tinker, we create a personal organization for you automatically, and you are its Admin. It starts out unnamed: the account menu in the bottom-left corner of the Console shows a **Name your organization** entry until you give it a proper name, and you'll need to do that before you can invite teammates or manage teams.

You can create additional organizations at any time: open that same account menu, choose **My organizations**, expand **Create a new organization**, and enter a name. Whoever creates an organization becomes its Admin. Creating an organization is free and needs no billing setup, but each organization is billed separately, and training and sampling requests are rejected until the organization has a balance (see [Billing](https://tinker-console.thinkingmachines.ai/billing/balance)) or an enterprise agreement.

Each organization is fully isolated: members, projects, training runs, checkpoints, and billing do not carry over between them. If you belong to more than one, switch between them from the same **My organizations** page.

### Finding your data in the Console

The [Tinker Console](https://tinker-console.thinkingmachines.ai) mirrors this hierarchy. **Projects** in the sidebar lists your org's projects — including the Default project — with who each one is shared with and how many sessions it contains. Clicking into a project shows its **sessions**; a session's page lists the **training runs** it hosts (base model, LoRA rank), and a training run's page lists its **checkpoints**, each with its type, expiry, and full `tinker://` path ready to copy into `SamplingClient` or `create_lora_training_client()`.

## Roles

Tinker uses two layers of roles: **organization-level** (broad) and **project-level** (per-project).

### Organization-level roles

| Capability                                           | Admin   | Member                            | Billing Admin |
| ---------------------------------------------------- | ------- | --------------------------------- | ------------- |
| Invite / remove users, change roles                  | ✓       | —                                 | —             |
| Edit / manage teams                                  | ✓       | —                                 | —             |
| View teams                                           | ✓ (all) | ✓ (own teams + org-visible teams) | —             |
| Create projects                                      | ✓       | ✓ (configurable)                  | —             |
| Manage *any* project (membership, settings, archive) | ✓       | — (only where Project Manager)    | —             |
| View billing / pay invoices                          | ✓       | —                                 | ✓             |
| View usage & spend breakdown                         | ✓       | ✓                                 | ✓             |

- **Admin** is the most powerful role: admins manage users, teams, billing, and every project in the org. We recommend keeping at least two Admins per org so access isn't bottlenecked on one person.
- **Member** can create projects and do all data work, but cannot manage users or billing. Members see the teams they belong to plus any team marked visible to the org, and they see other users only through shared teams and projects (not the full org roster).
- **Billing Admin** can view spend, pay invoices, and update payment information, but **cannot see project data, training runs, or checkpoints**. This role is for finance/procurement users who need billing access without product access.
- Project creation is enabled for both Admins and Members by default; an org setting can restrict it to Admins only.
- An Admin managing a project (editing its grants, archiving it) does not implicitly get to operate other members' *running* sessions — live session operations always stay with the session creator (see [Project-scoped sessions](#project-scoped-sessions)).

### Project-level roles

A user (or team) is granted one of three roles on a project. The last column shows what an org Admin can do on a project where they hold none of these grants:

|                                                            | Project Manager | Project Member | Project Sampler | Org Admin (no grant) |
| ---------------------------------------------------------- | --------------- | -------------- | --------------- | -------------------- |
| List & read `SAMPLER_WEIGHTS` checkpoints                  | ✓               | ✓              | ✓               | —                    |
| Run inference (create sampling clients)                    | ✓               | ✓              | ✓               | —                    |
| List & read `WEIGHTS` checkpoints, sessions, training runs | ✓               | ✓              | —               | —                    |
| Create sessions, start training runs, save checkpoints     | ✓               | ✓              | —               | —                    |
| Download checkpoint archives (export)                      | ✓               | ✓              | —               | —                    |
| Copy checkpoints to another project                        | ✓               | ✓              | —               | —                    |
| Restore a deleted checkpoint from backup                   | ✓               | ✓              | —               | —                    |
| Delete checkpoints / sessions / training runs              | ✓               | —              | —               | ✓                    |
| Set checkpoint TTLs, publish / unpublish checkpoints       | ✓               | —              | —               | ✓                    |
| Manage project membership and team grants                  | ✓               | —              | —               | ✓                    |
| Edit project settings, archive, mark read-only             | ✓               | —              | —               | ✓                    |

An org Admin can manage every project in the org, but the Admin role alone gives no access to a project's data. To read checkpoints, resume training, or sample in a project, an Admin adds themselves (or a team they're on) to it as a Project Manager or Member. Until then, data operations in that project behave as if it doesn't exist: creating a session with its `project_id` returns `404 Project not found`, and reading its training runs or checkpoint metadata returns `404`. This keeps admin duties (fixing sharing, cleaning up storage) separate from data access, so an admin account doesn't implicitly read or train on every project.

**Project Sampler** is a deliberately narrow role: it lets a principal run inference against a project's sampler checkpoints without seeing how the models are produced. A Sampler cannot see `WEIGHTS` (training-state) checkpoints, sessions, or training runs at all, and cannot use any checkpoint they can see as training init weights — that requires a `WEIGHTS` checkpoint plus read access the Sampler role doesn't grant. The intended pattern for downstream applications: a Project Manager or Member shares a `SAMPLER_WEIGHTS` checkpoint path out of band (a config value or environment variable), and the sampler principal uses that path to call inference. The role grants use of the weights on-platform, not possession of the bytes: a Sampler can read a sampler checkpoint's metadata and sample from it, but cannot export its weights. [Exporting weights](https://tinker-docs.thinkingmachines.ai/tinker/howto/checkpoints/#download-weights) requires Project Member or Manager on the checkpoint's project.

Cross-project operations compose two checks: the action permission on the project you're operating in, and the resource permission on the project that owns each resource you consume. For example, initializing a training run in project B from a checkpoint in project A requires the ability to start training runs in B **and** read access to the `WEIGHTS` checkpoint in A.

> **Every project always has at least one Project Manager**
>
> A manager can be removed (or step down) only if at least one other manager remains. To hand off a project, promote a new manager first.

## Sharing

Sharing is **project-based and team-mediated**. You cannot share an individual session, training run, or checkpoint — sharing happens at the project boundary, and everything in the project is shared together. Projects cannot be made public, inside or outside your org: anything outside the project boundary is invisible.

A user has access to a project if any of the following holds:

1. **A direct user grant** on the project (Manager, Member, or Sampler). The project's creator is auto-granted Project Manager this way — there is no special "creator" status, so a creator's access can be revoked like anyone else's.
1. **A team grant**: they belong to a team that has been granted a role on the project. Every member of the team inherits that role, and access updates automatically as people join or leave the team.
1. **An org-wide grant** on the project, which gives every org member the granted role. Small orgs often use this for a single shared project; the [Default project](#the-default-project) ships with one.

If a user has access via multiple paths, the **most permissive role wins**. A user with a direct Member grant who is also on a team granted Manager is a Project Manager on that project.

To share a project in the Console, a Project Manager (or org Admin) opens the project and adds users or teams, choosing a role for each grant.

### Team visibility

Each team is either **private** (visible only to its members and org admins — it doesn't appear in listings or pickers for anyone else) or **visible to the org** (any org member can see it and grant projects to it). Org admins set a team's visibility and the org-wide default for newly created teams.

Visibility governs *discovery*, not collaboration: once a private team has been granted to a project, members of that project can see the team's grant in the project's sharing metadata — you have to be able to tell who you're collaborating with. The team stays invisible to anyone who has access to neither the team nor a project it's granted on.

## Data isolation

### Project-scoped sessions

All data produced by a session — training runs, checkpoints, metadata — is scoped to the session's project. One rule sits outside the role tables: **only the session creator can perform live session operations** (training steps, sampling calls, weight saves), even when other project members can read and write the underlying resources. This prevents a teammate from accidentally disrupting your running job. Once data is saved, though, the *project* owns it: any project member can read it under the role rules above, and a creator who loses project access loses access to their own past data too.

### The Default project

Every org has exactly one **Default project**, and it cannot be deleted. When a session is created without a `project_id`, it lands there, and everything it produces belongs to it like any other project.

Out of the box, the Default project carries an org-wide **Project Member** grant: any org member can list, read, and write its sessions, training runs, and checkpoints, so data created without a `project_id` is visible to your whole org. Live operations stay creator-only as always.

The Default project is otherwise an ordinary project — an org admin (and, once one exists, a Project Manager) can reshape its membership and roles like any other project. If you want isolation or a specific set of collaborators from the start, create your session in a dedicated project with `project_id=...`.

### When someone leaves a project or the org

- **Data stays in the project.** If a user is removed from a project, the sessions, runs, and checkpoints they created remain, owned by the project and accessible to remaining project members.
- **The departing user loses access** to that data, unless they still reach the project via another path (e.g. a team grant).
- The Default project is no exception: when a user leaves the org, the data they created there remains with the org.

This is by design — all data belongs to a project, and a project belongs to the org, not to any individual.

### Session-create errors

- **`project_id` doesn't resolve**: the call returns a `404`, whether the project doesn't exist or exists but isn't accessible to you — the response never leaks the existence of projects you can't see. Ask an Admin or the project's Manager to add you.
- **The project is read-only**: creating a session is rejected (see [Read-only projects](#read-only-projects)).
- **No `project_id`**: the session is created in the Default project. This succeeds for any org member unless the Default project has been made read-only, in which case you must pass an explicit `project_id`.

### Checkpoint deletion and backups

Deleting a checkpoint is permanent. As protection against accidental deletion, Tinker offers an optional backup feature: with backups enabled for your org, a deleted checkpoint can be restored (you pay for the backup storage while backups are retained). Restoring follows the same rules as writing: a Project Manager or Project Member on the checkpoint's project can restore; a Project Sampler cannot.

### Read-only projects

A Project Manager or org admin can mark any project **read-only**. Its existing data stays fully readable and loadable, but the project accepts no new work: no new sessions, training runs, or checkpoint saves, and existing data can't be modified or deleted. The setting can be lifted at any time. Two common uses:

- **Archive a finished project** to preserve its runs and checkpoints for reference while preventing accidental changes.
- **Require explicit projects**: make the Default project read-only, and sessions created without a `project_id` are rejected — so all work must happen in a named, access-controlled project.

## Copying checkpoints between projects

Use **checkpoint copy** to make a checkpoint available in another project without moving its source session. A copy produces an independent checkpoint in the destination project — after the copy, the two are unlinked. The caller needs Manager or Member on **both** projects (read on the source, write on the destination).

Copying is also how work in the Default project gets moved into a dedicated project, e.g. to share it with a specific set of collaborators rather than the whole org. See [`copy_checkpoint.py`](https://github.com/thinking-machines-lab/tinker-cookbook/blob/main/tinker_cookbook/scripts/copy_checkpoint.py) in the cookbook for a ready-made script. This script is deprecated; use `await service_client.copy_weights(...)` ([`ServiceClient.copy_weights`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/serviceclient/#copy_weights)) with a client scoped to the destination project instead. This returns the copied checkpoint's `tinker://` path. You can also use `await rest_client.copy_weights(...)` ([`RestClient.copy_weights`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/restclient/#copy_weights)) with a standalone `tinker.RestClient()` and an explicit `destination_project_id`, without constructing a `ServiceClient`. Copying creates a new archival training run and session to hold the checkpoint; that run cannot be trained on.

To move an existing session and its training runs/samplers instead of copying a checkpoint, use [`RestClient.assign_session_project`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/restclient/#assign_session_project). The destination must be a project; clearing a session's project is not supported.

______________________________________________________________________

Questions or feedback? See [Support](https://tinker-docs.thinkingmachines.ai/support/index.md).
