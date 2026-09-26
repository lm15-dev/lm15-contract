> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Inference Error Codes

> Common error codes, their meanings, and resolutions for inference requests

Understanding error codes helps you quickly diagnose and resolve issues when making inference requests to the Fireworks API.

## Common error codes

| **Code** | **Error Name**        | **Possible Issue(s)**                                                                                                                            | **How to Resolve**                                                                                                                                                            |
| -------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `400`    | Bad Request           | Invalid input or malformed request.                                                                                                              | Review the request parameters and ensure they match the expected format.                                                                                                      |
| `401`    | Unauthorized          | Invalid API key or insufficient permissions.                                                                                                     | Verify your API key and ensure it has the correct permissions.                                                                                                                |
| `402`    | Payment Required      | Account is not on a paid plan or has exceeded usage limits.                                                                                      | Check your billing status and ensure your payment method is up to date. Upgrade your plan if necessary.                                                                       |
| `403`    | Forbidden             | Authentication issues.                                                                                                                           | Verify you have the correct API key.                                                                                                                                          |
| `404`    | Not Found             | The API endpoint path doesn't exist, the model doesn't exist, the model is not deployed, or you don't have permission to access it.              | Verify the URL path in your request and ensure you are using the correct API endpoint. Check if the model exists and is available. Ensure you have the necessary permissions. |
| `405`    | Method Not Allowed    | Using an unsupported HTTP method (e.g., using GET instead of POST).                                                                              | Check the API documentation for the correct HTTP method.                                                                                                                      |
| `408`    | Request Timeout       | The request took too long to complete, possibly due to server overload or network issues.                                                        | Retry the request after a brief wait. Consider increasing the timeout value if applicable.                                                                                    |
| `412`    | Precondition Failed   | Account is suspended or there's an issue with account status. This error also occurs when attempting to invoke a LoRA model that failed to load. | Check your account status and billing information. For LoRA models, ensure the model was uploaded correctly and is compatible. Contact support if the issue persists.         |
| `413`    | Payload Too Large     | Input data exceeds the allowed size limit.                                                                                                       | Reduce the size of the input payload (e.g., by trimming large text or image data).                                                                                            |
| `429`    | Too Many Requests     | Rate limited (serverless) or deployment capacity exceeded (dedicated/on-demand).                                                                 | See [understanding 429 errors](#understanding-429-errors) below.                                                                                                              |
| `500`    | Internal Server Error | Server-side code bug that is unlikely to resolve on its own.                                                                                     | Contact Fireworks support immediately, as this error typically requires intervention from the engineering team.                                                               |
| `502`    | Bad Gateway           | The server received an invalid response from an upstream server.                                                                                 | Wait and retry the request. If the error persists, it may indicate a server outage.                                                                                           |
| `503`    | Service Unavailable   | The service is down for maintenance or experiencing issues.                                                                                      | Retry the request after some time. Check the [status page](https://status.fireworks.ai) for maintenance announcements.                                                        |
| `504`    | Gateway Timeout       | The server did not receive a response in time from an upstream server.                                                                           | Wait briefly and retry the request. Consider using a shorter input prompt if applicable.                                                                                      |
| `520`    | Unknown Error         | An unexpected error occurred with no clear explanation.                                                                                          | Retry the request. If the issue persists, contact support for further assistance.                                                                                             |

## Understanding 429 errors

HTTP 429 (`Too Many Requests`) can be returned on both serverless and dedicated/on-demand deployments, but the cause and recommended action differ.

### Serverless deployments

On serverless, a 429 means your account has exceeded its current serverless request or TPM limit. Standard serverless, Priority tier, and Fast all use the same public rate-limit policy, which combines request-rate limits with adaptive TPM limits and is designed to prevent very spiky traffic. To resolve:

* Wait briefly and retry with exponential backoff
* Smooth sudden bursts or spread traffic more evenly over time
* Check the rate-limit response headers returned with your requests
* Review [Serverless rate limits](/serverless/rate-limits) if you need more headroom, or use an [on-demand deployment](/guides/ondemand-deployments) for dedicated capacity

### Dedicated and on-demand deployments

On dedicated and on-demand deployments, **there are no account-level rate limits**. A 429 instead indicates that your deployment's processing capacity is saturated. The inference server returns 429 when the number of queued and active requests exceeds what the deployment's GPUs can handle at that moment.

This is a capacity signal, not quota enforcement. To resolve:

* **Reduce burst concurrency** — lower the number of parallel requests or add client-side rate limiting with backoff
* **Scale up the deployment** — add more replicas or GPUs to increase throughput
* **Optimize request patterns** — use shorter prompts, reduce max output tokens, or batch requests to lower per-request resource consumption

<Tip>
  If you consistently see 429 errors on a dedicated or on-demand deployment, it's an indicator that your current GPU allocation is undersized for your traffic. [Contact us](https://fireworks.ai/company/contact-us) to discuss increasing your deployment capacity.
</Tip>

## Troubleshooting tips

If you encounter an error not listed here:

* Review the API documentation for the correct usage of endpoints and parameters
* Check the [Fireworks status page](https://status.fireworks.ai) for any ongoing service disruptions
* Contact support at [support@fireworks.ai](mailto:support@fireworks.ai) or join our [Discord](https://discord.gg/fireworks-ai)

<Tip>
  Enable detailed error logging in your application to capture the full error response, including error messages and request IDs, which helps with debugging.
</Tip>
