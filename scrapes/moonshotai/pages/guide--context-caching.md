> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use the Context Caching Feature of Kimi API

> Understand Kimi API automatic context caching, cache-hit conditions, billing, usage fields, and use cases for reducing cost and latency.

Context Caching pre-stores large amounts of data that may be requested frequently; when the same information is requested again, the system serves it directly from the cache instead of recomputing or retrieving it from the original source, saving time and resources. In the Kimi API, Context Caching is automatically enabled for all model requests: when the system detects repeated initial contexts (such as system prompts, knowledge documents, or tool definitions), it automatically reuses the cached content for cost optimization and faster responses, with no manual cache creation or management required.

## Use Context Caching for frequent requests over a fixed context

Context Caching is especially suitable for scenarios with frequent requests that repeatedly reference a large initial context, such as:

* QA bots that provide extensive preset content, such as product documentation assistants.
* Frequent queries against a fixed document collection, such as public disclosure Q\&A tools for listed companies.
* Periodic analysis of static codebases or knowledge bases, such as various Copilot Agents.
* Viral AI applications with sudden traffic spikes.
* Agent applications with complex interaction rules.

## Context Caching vs. RAG: how to choose

RAG (Retrieval-Augmented Generation) is widely used in the industry for cost reduction in long-text scenarios. Context Caching's cost reduction is highly dependent on business characteristics, while RAG's is not. The main differences are:

| Dimension        | Context Caching                                                                                           | RAG                                                                                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Business cost    | Extremely high cost compression in specific scenarios, up to 90%                                          | Any business can reduce costs, but recall accuracy issues may degrade answer quality                                      |
| Development cost | Relatively low; the system handles caching automatically, with no additional integration or tuning needed | Relatively high; requires combining RAG with Embedding and continuous business-specific tuning                            |
| Extra benefit    | Average first-token latency can drop to within 5s in long-text scenarios                                  | Original text length can be extended to very long, friendly to scenarios requiring millions of words of context in one go |

> **Recommendation**: For frequent queries against fixed content (e.g., FAQs, document Q\&A), prioritize Context Caching; if the content is extremely long and query directions are unfixed, consider a RAG solution.

## No configuration needed: caching is automatic

Context Caching uses a fully automatic caching mechanism — just call the API as usual:

* **No manual creation**: The system automatically identifies and caches frequently used initial contexts.
* **No cache ID references**: When calling `/v1/chat/completions`, simply pass messages in the normal way, and the system will automatically match caches in the background.
* **No TTL management**: Cache lifecycle is managed automatically by the system, with no manual intervention required.

The system will automatically trigger cache optimization at the appropriate times.

<Note>
  A new request can hit the prefix cache only when the previous request's prompt tokens exceed 256. If the previous request's prompt tokens are below 256, the request is not cached and is discarded.
</Note>

## Billing

For Context Caching billing methods and pricing details, see the [billing information on the Product Pricing page](/docs/pricing/chat#billing-logic).

## Notes

* **Cache hit conditions**: The system automatically optimizes caching for frequently repeated initial contexts. Make sure your knowledge content, system prompts, and tool definitions are relatively stable for better cache hit rates.
* **Multi-turn conversations**: Place fixed large contexts (such as knowledge documents) at the beginning of the `messages` array (before the system message), then append user questions and model replies; the system will automatically identify and cache this fixed content.
* **No extra configuration**: Context Caching is automatically effective for all requests — you do not need to modify your API calling method or add extra parameters; just focus on your prompt design and business logic.
