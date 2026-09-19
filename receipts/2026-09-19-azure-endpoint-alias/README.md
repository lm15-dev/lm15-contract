# Foundry hostname comparison — 2026-09-19

Live test on existing AIServices account `lm15-fdy-29d280ed6f8e`, eastus2,
resource group `lm15-lab`. Temporary deployment `lm15-endpoint-probe-deepseek`:
DeepSeek-V4-Flash, format DeepSeek, version 2026-04-23, GlobalStandard,
capacity 1. Azure reported provisioning Succeeded. Deleted after the test;
subsequent deployment listing returned `[]`. No existing deployments were
modified. No security settings or provisioned-throughput purchases changed.

Authentication: explicit Azure CLI Entra bearer token for
`https://ai.azure.com/.default`, obtained after the user completed browser
login on XPSwhite. Token retained in process memory only; not in receipts.
Requests sent from lambda using Python urllib, no SDK retry or hostname
fallback. Requests separated by at least 65 seconds after completion.

| Surface | services.ai.azure.com | openai.azure.com |
|---|---|---|
| /openai/v1/chat/completions | 200, `OK.` | 200, `OK.` |
| /openai/v1/responses | 200, `OK`; repeat control 200, `OK.` | 429 `no_capacity`; one explicit retry also 429 `no_capacity` |

The initial four calls used the same token and identical bodies per surface.
The two follow-up calls requested a token again; authentication method and
scope were unchanged. Per-call receipts preserve request body/hash, URL,
HTTP status, selected response headers and verbatim response body.

## What this proves

The old openai.azure.com alias **does serve a non-OpenAI model** through
Chat Completions on this Foundry account. The claim that non-OpenAI models
necessarily require services.ai.azure.com is false.

It does **not** prove the two hosts are interchangeable for all operations:
Responses succeeded twice on services.ai.azure.com but failed twice with
capacity errors on openai.azure.com. These errors are not DeploymentNotFound
and do not prove Responses is unsupported on the alias. The reason for the
host-dependent capacity result remains unverified; it could be transient
or due to internal routing. No latency conclusion can be drawn from this
small sequential sample.

This test covers DeepSeek-V4-Flash only, not Kimi or Claude. Recommend using
the advertised Foundry endpoint rather than guessing or automatically
switching hostnames. This experiment does not change the legacy OpenAI-kind
resource compatibility finding.
