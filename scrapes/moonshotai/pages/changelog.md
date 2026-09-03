> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Platform Changelog

> Review historical Kimi Open Platform feature releases, model launches, product improvements, and issue fixes.

This page is updated periodically with Kimi Open Platform product updates and related documentation changes.

## August 31, 2026

* The `kimi-k2.5` and all `moonshot-v1` series models (including `-vision-preview` and `moonshot-v1-auto`) were retired across all platforms at 16:00 today. Calls to these models now return a 404 "model not found" error. Please migrate to [Kimi K3](/docs/guide/kimi-k3-quickstart).
* Files API updates: newly generated file IDs now carry the `file_` prefix; improved parsing of complex content such as tables and formulas; images are no longer OCR'd for text extraction (for image understanding, upload images with `purpose=image`; see [Use Vision Models](/docs/guide/use-kimi-vision-model)); files uploaded with the same name as an existing file are automatically renamed by the server.

## April 7, 2025

* Reduced model product pricing.
* Added support for inviting and managing organization members.
* Fixed an issue where the cursor could not move in the name field when creating a project.

## February 17, 2025

* Launched the `kimi-latest` model.
* Added support for exporting organization monthly bills.
* Fixed project rate limit display issues.
* Added support for project daily and monthly spending alerts.

## January 13, 2025

* Launched the `moonshot-v1-vision-preview` model.
* Added support for organization project management.
* Restored WeChat Pay QR code payments.
* Added support for overseas phone number registration and login.

## December 2, 2024

* Optimized the resource management list copy interaction to use hover and click.
* Optimized resource list sorting by upload time, from newest to oldest.
* Added support for multiple accounts under one verified business entity.
* Fixed an invoice cancellation failure issue.

## November 4, 2024

* Context Caching is now available to all users.
* Cache renewal no longer charges the creation fee.
* Added terms and agreements content to the documentation center.
* Updated and optimized API Key copy.
* Fixed frontend flickering after successful payment.
* Added a retry mechanism for invoice cancellation failures.
* Fixed issues with editing and deleting API Keys.

## September 30, 2024

* Added frontend support for file resource management.
* Split phone number rebinding into two frontend verification steps for the old and new phone numbers.
* Added verification-code purpose descriptions to SMS messages.
* Fixed an issue where the invoiceable amount was displayed incorrectly.
* Fixed an invoice issuance failure caused by spaces in the tax identification number.
* Added bank transfer processing time display for business verification.
* Added documentation for automatic disconnection and reconnection handling.
* Launched web search.

## August 28, 2024

* Launched `moonshot-v1-auto`.
* Added support for custom account balance alerts.
* Added support for phone number rebinding.
* Added support for account password login.
* Reduced Cache storage costs.
* Published the MoonPalace user guide.
* Released the Kimi Enterprise API.
* Added tier level display to basic user information.

## July 31, 2024

* Released MoonPalace, the Kimi API debugging tool.
* Optimized pagination for Context Caching management.
* Launched user spending analysis.
* Added an embedded Context Caching calculator entry point in the documentation.
* Relaxed the company name length check for business verification.
* Added support for changing an individual-verified user into a business-verified user.
* Updated the API getting started guide.

## July 10, 2024

* Opened the Context Caching public beta to Tier 3 through Tier 5 users.
* Added the developer community QR code.
* Published the third Context Caching practice blog for Kimi API Assistant.
* Published the second Context Caching practice blog for Kimi API Assistant.
* Published the blog "How Context Caching Saves Up to 90% of Invocation Costs for Kimi API Assistant".

## July 1, 2024

* Officially launched the Context Caching public beta.

## June 28, 2024

* Added the WeCom customer service QR code.
* Optimized the API Key count limit.
* Published the first Context Caching practice blog for Kimi API Assistant.
* Published the "Affordable Long-Text Processing" blog.
* Added support for voucher validity periods.

## May 29, 2024

* Launched the Blog space.
* Added Dark Mode support for Open Platform.
* Launched invoice management.
* Optimized WeChat Pay and Alipay QR code payments.

## April 30, 2024

* Launched Tool Calling.
* Launched identity verification.
* Launched corporate bank transfer.
* Launched WeChat Pay and Alipay payments.
* Added support for the balance monitoring API.
