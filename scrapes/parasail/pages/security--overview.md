> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/security-and-account-management/overview.md).

# Security Overview

A security and account-management entry point for Parasail data handling, privacy, compliance, and API-key controls.

This page is a starting point for understanding how Parasail handles data and account controls.

## Trust Center and compliance

Use the [Parasail Trust Center](https://trust.parasail.io/) for current compliance information, security documentation, and certification status.

For legal and privacy terms, see:

* [Terms of Service](https://www.parasail.io/legal/terms)
* [Privacy Policy](https://www.parasail.io/legal/privacy-policy)

## Data privacy and retention

Parasail uses customer inputs and outputs to provide the requested inference service. In this section, **Input** means data, images, code, files, or other content you provide to the Platform, and **Output** means generated content or data returned by Parasail.

Parasail doesn't use Input, Output, customer prompts, uploaded files, fine-tuned model data, or personal data contained in Input or Output to train Parasail models or improve the Platform or Service. For optional model-training use, Parasail requires explicit customer agreement.

Parasail may collect operational metadata—data about usage that could identify you—such as usage statistics, API-token usage, selected models, token counts, timing, billing events, location, browser type, and engagement length. Parasail uses this metadata to operate, bill, secure, and improve the platform.

Use the Trust Center and Privacy Policy as the canonical sources for current legal, privacy, and compliance language.

## Product-specific retention summary

Parasail's privacy documentation distinguishes between interactive products and Batch for retention timing.

| Product area        | Input and output handling                                                                                                                                                         | Training use                                                                                      |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Serverless          | Parasail doesn't store or log personal data you send as Input, won't inspect it without your permission, and retains it only as long as necessary to generate and deliver Output. | Parasail doesn't use Input or Output to train Parasail models or improve the Platform or Service. |
| Dedicated Instances | Parasail doesn't store or log personal data you send as Input, won't inspect it without your permission, and retains it only as long as necessary to generate and deliver Output. | Parasail doesn't use Input or Output to train Parasail models or improve the Platform or Service. |
| Batch               | Parasail generally stores and logs personal data you send as Input for 30 days, though the specific time frame may vary.                                                          | Parasail doesn't use Input or Output to train Parasail models or improve the Platform or Service. |

## Security and account controls

Use [Account and API keys](/parasail-docs/security-and-account-management/account-api-keys.md) for organizations, account access, standard API keys, and read-only API keys. Use [Authentication](/parasail-docs/api-reference/authentication.md) for base URLs, bearer tokens, and SDK setup.

## Next steps

* [Account and API keys](/parasail-docs/security-and-account-management/account-api-keys.md)
* [Authentication](/parasail-docs/api-reference/authentication.md)
* [Pricing](/parasail-docs/billing/pricing.md)
