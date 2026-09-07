# bedrock-chat — dossier

Amazon Bedrock's OpenAI Chat Completions door on `bedrock-runtime`
(`{region}.amazonaws.com/openai/v1`), SigV4 service `bedrock`.  Sources:
`research/cloud-hosts/sources/bedrock-openai-chat-completions.md`,
`bedrock-api-keys.md`; fact sheet `research/cloud-hosts/10-facts-aws.md`.

- Capture: `AWS_REGION=us-east-1 python3 research/providers/bedrock-chat/capture.py`
  (credentials from lm15's aws-chain; every case re-signed with the fixed
  test pair for the fixture).
- Live 2026-09-03: `changes/2026-09-03-bedrock-chat-live.md`,
  `receipts/2026-09-03-bedrock-chat/`.
- Model used: `openai.gpt-oss-20b-1:0` (no agreement needed).  Claude ids
  (`anthropic.claude-sonnet-5` form) need the account's Bedrock model
  agreement (403 until then).
- Use-case form from the CLI: `put-use-case-for-model-access --cli-binary-format raw-in-base64-out --form-data "$(printf %s "$JSON" | base64 -w0)"` — the blob is the base64 of the JSON `{companyName, companyWebsite, intendedUsers, industryOption, otherIndustryOption, useCases}` (learned from the stored form 2026-09-03; a raw-JSON blob answers "Invalid form data").
- Open cells: Claude on this door; bearer-key auth and `/models` under it;
  `cache_control`; a pinned 404 `model_not_found` envelope.
