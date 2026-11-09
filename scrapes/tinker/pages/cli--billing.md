# tinker billing

## **tinker billing**

View billing usage.

### tinker billing checkpoint-storage

Show current checkpoint storage and its projected run rate.

With no arguments, returns checkpoint storage usage for the entire authenticated organization, grouped by project and session owner. Use --project-id to limit results to one project within that organization. Checkpoint usage data can lag by 1-2 hours. Monthly costs are gross 720-hour projections using current publicly available rates, before credits and commits; they are not invoice amounts due.

**Options:**

- `--project-id TEXT` — Only show storage in this project
- `--csv PATH` — Write storage rows as CSV to PATH instead of table/JSON output ('-' for stdout)

### tinker billing usage *STARTING_ON* *ENDING_BEFORE*

Show hourly billing usage for your organization.

STARTING_ON and ENDING_BEFORE are RFC 3339 timestamps aligned to UTC hour boundaries (e.g. 2026-07-13T00:00:00Z), at most 14 days apart. Returns one row per (hour x usage type x base model x session x user), annotated with the project the usage belongs to. Session user metadata comes as a separate per-session table (JSON output / --sessions-csv) to join on session_id. Quantities are raw tokens / gigabyte-hours. Token and storage rows include estimated gross USD usage cost before credits and commits, plus the applicable effective rate per million tokens or per GB-month. Token cost is the token rate times token_count / 1,000,000; storage cost is the storage rate times gigabyte_hours / 720. These are not invoice amounts due. For a completed UTC day, each model/usage-category group is priced only after its full-day quantity reconciles with finalized invoice usage line items, or the latest draft when no finalized invoice is available. Other groups on the same day may remain null. The current incomplete UTC day instead uses the published Tinker rate-card snapshot, so its estimate is not invoice-reconciled and can change after the day completes. Table output renders an unavailable applicable cost or rate as `null`; CSV uses blank cells, while the typed SDK and JSON use null. The SDK response and JSON output also include `cost_data_through`, which marks the exclusive UTC boundary between the two pricing sources: non-null estimates before it use invoice-derived rates, while newer non-null estimates use fixed published rates. A cost or rate may still be null when the data required to price that row is unavailable. `cost_data_through` is null when the response has no completed day with invoice pricing data. Table and CSV output do not include this response-level field. Data lags real time by up to a few hours.

There are no filter flags: export the window once and filter the CSV/JSON client-side.

Requires billing view access in your organization.

**Options:**

- `--csv PATH` — Write usage rows as CSV to PATH instead of table/JSON output ('-' for stdout)
- `--sessions-csv PATH` — Also write the per-session side-table (session_id + user_metadata) as CSV to PATH ('-' for stdout); join it against the usage rows on session_id
