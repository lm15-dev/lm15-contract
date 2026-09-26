> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/operate-in-production/limits-and-quotas.md).

# Limits and Quotas

Rate limits, GPU quotas, and quota increase guidance for Parasail production workloads.

Parasail applies request rate limits and GPU quotas to protect shared capacity and help customers avoid unexpected usage.

## Rate limits

| Product class     |                      RPM | Token limit               |
| ----------------- | -----------------------: | ------------------------- |
| Serverless - Free |                        5 | Not currently enforced    |
| Serverless - User |                      500 | Not currently enforced    |
| Elastic Endpoints | Provisioned per endpoint | Set by endpoint agreement |
| Enterprise        |                Unlimited | Not currently enforced    |

Contact Parasail if your workload needs higher request limits.

## GPU quota

New customer organizations start with a quota of 4 GPUs shared across Batch and Dedicated services. The quota applies collectively across GPU types.

Examples:

* If current usage is 2 H100 GPUs and you submit a Batch job that requires 8 H100 GPUs, Parasail rejects the submission because it exceeds the 4 GPU quota.
* If a Dedicated deployment can auto-scale from 1 to 6 GPUs and the deployment already uses 4 GPUs, the quota prevents scaling to a fifth GPU.

If the deployment page shows `Insufficient quota`, the organization has reached its GPU quota.

## Request a quota increase

Use the [Quota Increase Form](https://parasail.clickup.com/forms/9011827181/f/8cjb4fd-5671/T54OWYUTZAAJIVOGIC) to request more GPU capacity. Quota increases up to 8 GPUs are available without additional justification. Requests for more than 8 GPUs require a short explanation of the workload.

## Next steps

* [Retries and Idempotency](/parasail-docs/operate-in-production/retries-and-idempotency.md)
* [Pricing](/parasail-docs/billing/pricing.md)
* [Dedicated Instances overview](/parasail-docs/products/overview-1.md)
* [Batch troubleshooting](/parasail-docs/products/quickstart/troubleshooting.md)
