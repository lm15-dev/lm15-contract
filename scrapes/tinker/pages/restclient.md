# RestClient

*Generated from tinker 0.38.0 at commit [`4fb85c7`](https://github.com/thinking-machines-lab/tinker/tree/4fb85c7a2be46300f340cedd16ef2fab881c0c38). Source links point at that snapshot.*

## *class* [**tinker.RestClient**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L62)(*\_holder=None*, *base_url=None*, *api_key=None*)

Client for REST API operations like listing checkpoints and metadata.

The RestClient provides access to various REST endpoints for querying model information, checkpoints, and other resources. Construct one directly with `RestClient()`; no ServiceClient or training session is needed.

**Key methods:**

- get_server_capabilities() - get the models the caller can use and the server's features
- list_checkpoints() - list available model checkpoints (both training and sampler)
- list_user_checkpoints() - list all checkpoints across all user's training runs
- get_training_run() - get model information and metadata as ModelEntry
- delete_checkpoint() - delete an existing checkpoint for a training run
- get_billing_usage(), get_current_checkpoint_storage_usage(), get_audit_log() - (deprecated) admin-only operations, now on [`AdminClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/adminclient/index.md)
- get_external_weights_urls() - get per-file signed URLs for an external weights checkpoint
- copy_weights() - copy a checkpoint into a selected project
- publish_checkpoint_from_tinker_path() - publish a checkpoint to make it public
- unpublish_checkpoint_from_tinker_path() - unpublish a checkpoint to make it private
- set_checkpoint_ttl_from_tinker_path() - set or remove TTL on a checkpoint
- assign_session_project() - move a session into a project
- whoami() - get the calling principal's user URN and email
- export_session_trace() - export a session's timeline as a Perfetto trace and get a signed download URL
- search_sessions() - (experimental) search your organization's sessions, newest first

A RestClient constructed directly talks to the REST API only: no session is created on the server, so no project is needed and nothing shows up in the sessions list. Its connections are shared by every client constructed this way with the same base URL and API key, stay open for the life of the process, and need no closing.

Operations that need an organization admin or billing-admin role live on [`AdminClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/adminclient/index.md), which is constructed the same way.

**Parameters:**

- [**\_holder**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L122) (*[InternalClientHolder](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/internal_client_holder.py#L259) | None*, default: `None`) – Internal use only. The client managing HTTP connections and async operations that a [`ServiceClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/serviceclient/index.md) hands over; it cannot be combined with `base_url` or `api_key`.
- [**base_url**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L124) (*str | None*, default: `None`) – The Tinker API URL. Defaults to the `TINKER_BASE_URL` environment variable, then to the production API.
- [**api_key**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L125) (*str | None*, default: `None`) – The Tinker API key. Defaults to the `TINKER_API_KEY` environment variable, then to the stored credentials.

**Example:**

```python
rest_client = tinker.RestClient()
checkpoints = rest_client.list_user_checkpoints().result()
print(f"Found {len(checkpoints.checkpoints)} checkpoints")

training_run = rest_client.get_training_run("run-id").result()
print(f"Training Run: {training_run.training_run_id}, LoRA: {training_run.is_lora}")
checkpoints = rest_client.list_checkpoints("run-id").result()
print(f"Found {len(checkpoints.checkpoints)} checkpoints")
for checkpoint in checkpoints.checkpoints:
    print(f"  {checkpoint.checkpoint_type}: {checkpoint.checkpoint_id}")
```

### [**get_server_capabilities**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L138)()

Query the server's supported features and capabilities.

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`GetServerCapabilitiesResponse`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/getservercapabilitiesresponse/index.md) with the models the caller can use, features, and limits. Await it, or call `.result()`.

**Example:**

```python
capabilities = rest_client.get_server_capabilities().result()
for model in capabilities.supported_models:
    print(model.model_name)
```

### [**get_training_run**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L188)(*training_run_id*, *access_scope='owned'*)

Get training run info.

**Parameters:**

- [**training_run_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L190) (*types.[ModelID](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/types/model_id.py#L5)*) – The training run ID to get information for
- [**access_scope**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L191) (*Literal['owned', 'accessible']*, default: `'owned'`)

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the training run information. Await it, or call `.result()`.

**Example:**

```python
future = rest_client.get_training_run("run-id")
response = future.result()  # or `await future`
print(f"Training Run ID: {response.training_run_id}, Base: {response.base_model}")
```

### [**get_training_run_by_tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L226)(*tinker_path*, *access_scope='owned'*)

Get training run info.

**Parameters:**

- [**tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L227) (*str*) – The tinker path to the checkpoint
- [**access_scope**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L227) (*Literal['owned', 'accessible']*, default: `'owned'`)

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the training run information. Await it, or call `.result()`.

**Example:**

```python
future = rest_client.get_training_run_by_tinker_path("tinker://run-id/weights/checkpoint-001")
response = future.result()  # or `await future`
print(f"Training Run ID: {response.training_run_id}, Base: {response.base_model}")
```

### [**get_weights_info_by_tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L269)(*tinker_path*)

Get checkpoint information from a tinker path.

**Parameters:**

- [**tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L270) (*str*) – The tinker path to the checkpoint

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the checkpoint information. The future is awaitable.

**Example:**

```python
future = rest_client.get_weights_info_by_tinker_path("tinker://run-id/weights/checkpoint-001")
response = future.result()  # or await future
print(f"Base Model: {response.base_model}, LoRA Rank: {response.lora_rank}")
```

### [**list_training_runs**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L333)(*limit=20*, *offset=0*, *access_scope='owned'*, *project_id=None*)

List training runs with pagination support.

**Parameters:**

- [**limit**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L335) (*int*, default: `20`) – Maximum number of training runs to return (default 20)
- [**offset**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L336) (*int*, default: `0`) – Offset for pagination (default 0)
- [**access_scope**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L337) (*Literal['owned', 'accessible']*, default: `'owned'`)
- [**project_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L338) (*str | None*, default: `None`) – If provided, only return training runs in this project

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`TrainingRunsResponse`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/trainingrunsresponse/index.md) with training runs and cursor info. Await it, or call `.result()`.

**Example:**

```python
future = rest_client.list_training_runs(limit=50)
response = future.result()  # or `await future`
print(f"Found {len(response.training_runs)} training runs")
print(f"Total: {response.cursor.total_count}")
# Get next page
next_page = rest_client.list_training_runs(limit=50, offset=50)
# Only runs in a given project
project_runs = rest_client.list_training_runs(project_id="my-project-id").result()
```

### [**list_checkpoints**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L405)(*training_run_id*)

List available checkpoints (both training and sampler).

**Parameters:**

- [**training_run_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L406) (*types.[ModelID](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/types/model_id.py#L5)*) – The training run ID to list checkpoints for

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`CheckpointsListResponse`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/checkpointslistresponse/index.md) with available checkpoints. Await it, or call `.result()`.

**Example:**

```python
future = rest_client.list_checkpoints("run-id")
response = future.result()  # or `await future`
for checkpoint in response.checkpoints:
    if checkpoint.checkpoint_type == "training":
        print(f"Training checkpoint: {checkpoint.checkpoint_id}")
    elif checkpoint.checkpoint_type == "sampler":
        print(f"Sampler checkpoint: {checkpoint.checkpoint_id}")
```

### [**get_external_weights_urls**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L467)(*tinker_path*)

Get signed download URLs, one per file, for an external weights checkpoint.

**Parameters:**

- [**tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L468) (*str*) – The checkpoint's tinker path, as returned by `save_weights_external` (`tinker://<training_run_id>/external_weights/<name>`)

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`ExternalWeightsUrlsResponse`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/externalweightsurlsresponse/index.md): `urls` maps each file path (relative to the checkpoint root) to a signed URL, valid until `expires`. Await it, or call `.result()`.

### [**delete_checkpoint**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L517)(*training_run_id*, *checkpoint_id*)

Delete a checkpoint for a training run.

**Parameters:**

- [**training_run_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L518) (*types.[ModelID](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/types/model_id.py#L5)*)
- [**checkpoint_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L518) (*str*)

**Returns:** *[APIFuture](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md)[None]*

### [**delete_checkpoint_from_tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L541)(*tinker_path*)

Delete a checkpoint referenced by a tinker path.

**Parameters:**

- [**tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L541) (*str*)

**Returns:** *[APIFuture](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md)[None]*

### [**get_audit_log**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L569)(*event_type='all'*, *day=None*)

Deprecated: use [`AdminClient.get_audit_log()`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/adminclient/index.md) instead. This method will be removed in a subsequent release.

**Parameters:**

- [**event_type**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L571) (*Literal['all', 'checkpoints', 'projects', 'teams', 'organizations']*, default: `'all'`)
- [**day**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L572) (*date | None*, default: `None`)

**Returns:** *[APIFuture](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md)\[types.[AuditLogResponse](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/auditlogresponse/index.md)\]*

### [**copy_weights**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L623)(*path*, *destination_project_id=None*, *ttl_seconds=None*, *weights_access_token=None*)

Copy a checkpoint into a selected project.

Storage is shared with the source, so no bytes are duplicated. The copy keeps the source's checkpoint kind and belongs to a new training run that cannot be trained on.

**Parameters:**

- [**path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L625) (*str*) – Tinker path of the checkpoint to copy
- [**destination_project_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L626) (*str | None*, default: `None`) – Project that will own the copy. If omitted, defaults to the `TINKER_PROJECT_ID` environment variable.
- [**ttl_seconds**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L628) (*int | None*, default: `None`) – Seconds until the copy expires, between 1 hour (3600) and 10 years, or None for no expiry
- [**weights_access_token**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L629) (*str | None*, default: `None`) – Optional access token for copying weights readable under a different account

**Returns:**

- A future for the tinker path of the copy. Await it, or call `.result()`.

**Raises:**

- `ValueError`: If neither a destination project nor `TINKER_PROJECT_ID` is set

**Example:**

```python
copied_path = rest_client.copy_weights(
    "tinker://run-id/weights/step-400", "proj-archive"
).result()
print(copied_path)
```

### [**publish_checkpoint_from_tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L713)(*tinker_path*)

Publish a checkpoint referenced by a tinker path to make it publicly accessible.

Only the exact owner of the training run can publish checkpoints. Published checkpoints can be unpublished using the unpublish_checkpoint_from_tinker_path method.

**Parameters:**

- [**tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L713) (*str*) – The tinker path to the checkpoint (e.g., "tinker://run-id/weights/0001")

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) that completes when the checkpoint is published. Await it, or call `.result()`.

**Raises:**

HTTPException: 400 if checkpoint identifier is invalid HTTPException: 404 if checkpoint not found or user doesn't own the training run HTTPException: 409 if checkpoint is already public HTTPException: 500 if there's an error publishing the checkpoint

**Example:**

```python
future = rest_client.publish_checkpoint_from_tinker_path("tinker://run-id/weights/0001")
future.result()  # or `await future`
print("Checkpoint published successfully")
```

### [**unpublish_checkpoint_from_tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L776)(*tinker_path*)

Unpublish a checkpoint referenced by a tinker path to make it private again.

Only the exact owner of the training run can unpublish checkpoints. This reverses the effect of publishing a checkpoint.

**Parameters:**

- [**tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L776) (*str*) – The tinker path to the checkpoint (e.g., "tinker://run-id/weights/0001")

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) that completes when the checkpoint is unpublished. Await it, or call `.result()`.

**Raises:**

HTTPException: 400 if checkpoint identifier is invalid HTTPException: 404 if checkpoint not found or user doesn't own the training run HTTPException: 409 if checkpoint is already private HTTPException: 500 if there's an error unpublishing the checkpoint

**Example:**

```python
future = rest_client.unpublish_checkpoint_from_tinker_path("tinker://run-id/weights/0001")
future.result()  # or `await future`
print("Checkpoint unpublished successfully")
```

### [**set_checkpoint_ttl_from_tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L840)(*tinker_path*, *ttl_seconds*)

Set or remove the TTL on a checkpoint referenced by a tinker path.

If ttl_seconds is provided, the checkpoint will expire after that many seconds from now. It must be between 1 hour (3600) and 10 years. If ttl_seconds is None, any existing expiration will be removed.

**Parameters:**

- [**tinker_path**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L841) (*str*) – The tinker path to the checkpoint (e.g., "tinker://run-id/weights/0001")
- [**ttl_seconds**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L841) (*int | None*) – Seconds until expiration (1 hour to 10 years), or None to remove TTL

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) that completes when the TTL is set. Await it, or call `.result()`.

**Raises:**

HTTPException: 400 if checkpoint identifier is invalid or ttl_seconds is out of range HTTPException: 404 if checkpoint not found or user doesn't own the training run HTTPException: 500 if there's an error setting the TTL

**Example:**

```python
future = rest_client.set_checkpoint_ttl_from_tinker_path("tinker://run-id/weights/0001", 86400)
future.result()  # or `await future`
print("Checkpoint TTL set successfully")
```

### [**list_user_checkpoints**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L912)(*limit=100*, *offset=0*)

List all checkpoints for the current user across all their training runs.

This method retrieves checkpoints from all training runs owned by the authenticated user, sorted by time (newest first). It supports pagination for efficiently handling large numbers of checkpoints.

**Parameters:**

- [**limit**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L913) (*int*, default: `100`) – Maximum number of checkpoints to return (default 100)
- [**offset**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L913) (*int*, default: `0`) – Offset for pagination (default 0)

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`CheckpointsListResponse`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/checkpointslistresponse/index.md) with checkpoints and cursor info. Await it, or call `.result()`.

**Example:**

```python
future = rest_client.list_user_checkpoints(limit=50)
response = future.result()  # or `await future`
print(f"Found {len(response.checkpoints)} checkpoints")
print(f"Total: {response.cursor.total_count if response.cursor else 'Unknown'}")
for checkpoint in response.checkpoints:
    print(f"  {checkpoint.training_run_id}/{checkpoint.checkpoint_id}")
# Get next page if there are more checkpoints
if response.cursor and response.cursor.offset + response.cursor.limit < response.cursor.total_count:
    next_page = rest_client.list_user_checkpoints(limit=50, offset=50)
```

### [**get_session**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L980)(*session_id*, *access_scope='owned'*)

Get session information including all training runs and samplers.

**Parameters:**

- [**session_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L981) (*str*) – The session ID to get information for
- [**access_scope**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L981) (*Literal['owned', 'accessible']*, default: `'owned'`)

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`GetSessionResponse`](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/types/get_session_response.py#L7) with training_run_ids, sampler_ids, and user_metadata. Await it, or call `.result()`.

**Example:**

```python
future = rest_client.get_session("session-id")
response = future.result()  # or `await future`
print(f"Training runs: {len(response.training_run_ids)}")
print(f"Samplers: {len(response.sampler_ids)}")
print(f"User metadata: {response.user_metadata}")
```

### [**list_sessions**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1045)(*limit=20*, *offset=0*, *access_scope='owned'*)

List sessions with pagination support.

**Parameters:**

- [**limit**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1047) (*int*, default: `20`) – Maximum number of sessions to return (default 20)
- [**offset**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1048) (*int*, default: `0`) – Offset for pagination (default 0)
- [**access_scope**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1049) (*Literal['owned', 'accessible']*, default: `'owned'`)

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`ListSessionsResponse`](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/types/list_sessions_response.py#L6) with list of session IDs. Await it, or call `.result()`.

**Example:**

```python
future = rest_client.list_sessions(limit=50)
response = future.result()  # or `await future`
print(f"Found {len(response.sessions)} sessions")
# Get next page
next_page = rest_client.list_sessions(limit=50, offset=50)
```

### [**assign_session_project**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1112)(*session_id*, *project_id*)

Move a session (and all of its training runs/samplers) into a project.

Use this to attach a previously-created session to a project, or to move a session between projects. Clearing the project is not supported — sessions cannot be moved out of a project once placed.

**Parameters:**

- [**session_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1112) (*str*) – The session ID to move
- [**project_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1112) (*str*) – The destination project ID

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) that completes when the session has been moved. Await it, or call `.result()`.

**Raises:**

HTTPException: 400 if `project_id` is missing HTTPException: 403 if the caller lacks access to the destination project HTTPException: 404 if the session is not found or not accessible

**Example:**

```python
future = rest_client.assign_session_project("session-id", "project-id")
future.result()
```

### [**export_session_trace**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1184)(*session_id*)

Export a session's timeline as a Perfetto trace and get a signed download URL.

Kicks off (or reuses) an async export job on the server that builds a Perfetto trace (`.pftrace`) of the session's training and sampling requests, polls until the file is uploaded, and returns a signed download URL. The URL expires after about an hour; call this method again to get a fresh one (the trace is not rebuilt if it is already up to date).

To download the trace, issue a plain HTTPS GET to the URL (no auth **headers needed):**

```python
import urllib.request

url = rest_client.export_session_trace("session-id").result()
urllib.request.urlretrieve(url, "session-id.pftrace")
```

or from a shell: `curl -o session.pftrace '<url>'` (quote the URL, it contains query parameters). Open the file in https://ui.perfetto.dev to view the timeline, or use `tinker session export-trace <session-id>` to do all of this from the CLI.

**Parameters:**

- [**session_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1184) (*str*) – The session ID to export a trace for

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the signed download URL for the `.pftrace` file. Await it, or call `.result()`.

**Raises:**

RuntimeError: if the export job fails

**Example:**

```python
url = rest_client.export_session_trace("session-id").result()
print(f"Download URL: {url}")
```

### [**whoami**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1238)()

Get the calling principal's identity.

Returns the user URN and organization URN associated with the credential in use, and the user's email when the principal is user-backed.

The identity is read from the claims of the JWT the SDK already holds from auth (cached and refreshed in the background), so this makes no server requests.

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`WhoamiResponse`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/whoamiresponse/index.md). The future is awaitable.

**Example:**

```python
# Sync usage
response = rest_client.whoami().result()
print(f"user: {response.user_urn}, org: {response.org_urn}, email: {response.email}")

# Async usage
response = await rest_client.whoami()
```

### [**get_sampler**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1275)(*sampler_id*)

Get sampler information.

**Parameters:**

- [**sampler_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1275) (*str*) – The sampler ID (sampling_session_id) to get information for

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing the [`GetSamplerResponse`](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/types/_pydantic_types/get_sampler_response.py#L4) with sampler details

**Example:**

```python
# Sync usage
future = rest_client.get_sampler("session-id:sample:0")
response = future.result()  # or `await future`
print(f"Base model: {response.base_model}")
print(f"Model path: {response.model_path}")

# Async usage
response = await rest_client.get_sampler("session-id:sample:0")
print(f"Base model: {response.base_model}")
```

### [**get_billing_usage**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1328)(*starting_on*, *ending_before*)

Deprecated: use [`AdminClient.get_billing_usage()`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/adminclient/index.md) instead. This method will be removed in a subsequent release.

**Parameters:**

- [**starting_on**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1330) (*datetime | str*)
- [**ending_before**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1331) (*datetime | str*)

**Returns:** *[APIFuture](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md)\[types.[BillingUsageResponse](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/billingusageresponse/index.md)\]*

### [**get_current_checkpoint_storage_usage**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1360)(*project_id=None*)

Deprecated: use [`AdminClient.get_current_checkpoint_storage_usage()`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/adminclient/index.md) instead. This method will be removed in a subsequent release.

**Parameters:**

- [**project_id**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1362) (*str | None*, default: `None`)

**Returns:** *[APIFuture](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md)\[types.[CurrentCheckpointStorageUsageResponse](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/currentcheckpointstorageusageresponse/index.md)\]*

### [**search_sessions**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1409)(*request*)

Search your organization's sessions, newest first.

Experimental: this API may change or be removed in any release.

Results are restricted to projects you may list. Page through them by passing each response's `next_cursor` as the next request's `cursor`.

**Parameters:**

- [**request**](https://github.com/thinking-machines-lab/tinker/blob/4fb85c7a2be46300f340cedd16ef2fab881c0c38/src/tinker/lib/public_interfaces/rest_client.py#L1410) (*types.[SessionSearchRequest](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/sessionsearchrequest/index.md)*) – The search filters, page size and cursor

**Returns:**

- An [`APIFuture`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/apifuture/index.md) containing one [`SessionSearchResponse`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/sessionsearchresponse/index.md) page. Await it, or call `.result()`.

**Example:**

```python
from tinker.types import AccessibleSearchOwner, SessionSearchRequest

request = SessionSearchRequest(display_name="nightly", owner=AccessibleSearchOwner())
page = rest_client.search_sessions(request).result()
while True:
    for session in page.sessions:
        print(session.session_id, session.display_name)
    if page.next_cursor is None:
        break
    request = request.model_copy(update={"cursor": page.next_cursor})
    page = rest_client.search_sessions(request).result()
```

## Referenced by

- [AdminClient.tinker.AdminClient](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/adminclient/#tinker-adminclient)
- [ServiceClient.create_rest_client](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/serviceclient/#create_rest_client)
