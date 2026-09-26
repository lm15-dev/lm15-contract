> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Rate Limits

> Default concurrent request limits and how to increase them.

## Default limit: 200 concurrent requests per model

Every account has a default limit of **200 concurrent requests per model**. If you query two different models simultaneously, you can handle 400 total concurrent requests (200 per model).

This limit is sufficient for most production applications, including services with hundreds of thousands of daily active users.

## Understanding concurrent vs. requests per minute

The rate limit is on *concurrent* requests, not per-minute volume. Throughput depends on how long each request takes:

| Avg Request Duration | Concurrent Limit | Approx RPM |
| -------------------- | :--------------: | :--------: |
| 1 second             |        200       | 12,000 RPM |
| 10 seconds           |        200       |  1,200 RPM |
| 60 seconds           |        200       |   200 RPM  |

As requests complete, new ones can immediately take their place.

## Batch jobs

For large batch jobs (e.g., embedding a knowledge base), use a [token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket) to stay under 200 concurrent requests. You'll still complete the work in a reasonable time.

## Rate limit errors

You'll receive HTTP **429** with a `Rate limited` message when the limit is exceeded.

Actions to take:

* Retry after a short delay
* Slow down your request rate
* Apply for a limit increase

<Note>
  You may occasionally receive **429** errors when a model becomes very busy, even if you're under the limit. Auto-scaling will kick in shortly. Retry after a brief wait.
</Note>

## Request a limit increase

You can request a rate limit increase in your [Dashboard → Account](https://deepinfra.com/dash/account). Include context about your use case.
