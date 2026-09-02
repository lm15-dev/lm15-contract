In a typical AI workflow, you might pass the same input tokens over and over to
a model. The Gemini API offers implicit caching to optimize performance and costs.

> [!NOTE]
> **Note:** The **Interactions API** only supports implicit caching. Explicit caching (manually creating and managing cache objects) is not supported in the Interactions API. To use explicit caching, switch to the [generateContent API](https://ai.google.dev/gemini-api/docs/generate-content/caching).

## Implicit caching

Implicit caching is enabled by default for all Gemini 2.5 and newer models. It is
supported for both [stateful](https://ai.google.dev/gemini-api/docs/text-generation#multi-turn-conversations) (using `previous_interaction_id`)
and [stateless](https://ai.google.dev/gemini-api/docs/text-generation#stateless-conversations) conversation modes.
We automatically pass on cost savings if your request hits caches. There is nothing you need to do
in order to enable this. The minimum input
token count for context caching is listed in the following table for each model:

| Model | Min token limit |
|---|---|
| Gemini 3.7 Flash | 4,096 |
| Gemini 3.6 Flash | 4,096 |
| Gemini 3.5 Flash | 4,096 |
| Gemini 3.1 Pro Preview | 4,096 |
| Gemini 2.5 Flash | 2,048 |
| Gemini 2.5 Pro | 2,048 |

To increase the chance of an implicit cache hit:

- Try putting large and common contents at the beginning of your prompt
- Try to send requests with similar prefix in a short amount of time

You can see the number of tokens which were cache hits in the response object's
`usage.total_cached_tokens` (Python and JavaScript) field.