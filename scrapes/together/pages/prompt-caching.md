> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Prompt caching

> Together reuses previously processed prompt prefixes to lower input cost and time to first token.

Prompt caching reuses the work a model has already done on the beginning of a prompt. When a request starts with the same tokens as an earlier request, the model loads the saved state for that shared prefix instead of recomputing it, then processes only the tokens that follow.

Prompt caching is automatic on [serverless inference](/docs/serverless/overview) and [dedicated model inference](/docs/dedicated-endpoints/requests#prompt-caching). There's no parameter, header, or account setting to turn it on, and no cache ID or expiry setting to manage. Caching never changes how the model generates its output.

## How prompt caching works

To process a prompt, the model computes intermediate key-value (KV) states for every input token, which let it attend to earlier tokens while it generates. Prompt caching stores the KV states for a prompt's prefix, so a later request with the same prefix skips that computation.

The prefix is the prompt exactly as the model sees it, after the model's chat template renders your request into tokens. Everything the chat template renders counts toward the prefix:

* The system prompt and every earlier message, including images.
* Tool definitions in `tools`.
* Request settings the chat template renders into the prompt, such as `reasoning`, `reasoning_effort`, and `chat_template_kwargs`.

<Frame>
  <img src="https://mintcdn.com/togetherai-52386018/DUEk3Wgao1Ml_rVW/images/prompt-caching/prefix-contents.svg?fit=max&auto=format&n=DUEk3Wgao1Ml_rVW&q=85&s=8c852906d3c813aab700c6cc03505fc5" alt="Request messages, tools, and template settings feed into the chat template, which renders them into one sequence of prompt tokens. That rendered sequence is the prefix that prompt caching matches." width="706" height="180" data-path="images/prompt-caching/prefix-contents.svg" />
</Frame>

A request reuses the longest prefix it shares with a cached entry. Tokens up to the first difference can come from the cache, and every token from the first difference onward is processed from scratch.

<Frame>
  <img src="https://mintcdn.com/togetherai-52386018/DUEk3Wgao1Ml_rVW/images/prompt-caching/prefix-match.svg?fit=max&auto=format&n=DUEk3Wgao1Ml_rVW&q=85&s=7549b8fa50049a5f3b305ad493ded3ff" alt="Two requests share a system prompt and reference material but end with different questions. The second request reads 3,327 shared tokens from the cache and processes the 90 new tokens after the first difference." width="520" height="183" data-path="images/prompt-caching/prefix-match.svg" />
</Frame>

Cache entries typically last about an hour. This is done on a best effort basis. For serverless models, the cache is shared across the fleet, so under heavy load, entries may be evicted sooner. The minimum cacheable prefix length and the granularity of cached tokens vary by model and can change, so don't design your prompts around a specific threshold.

## Maximize cache hits

Any change that alters the rendered prompt ends the match at the point of the change. Structure requests so the part that changes comes last:

* **Put stable content first:** Place instructions, tool definitions, reference documents, and few-shot examples at the start of the prompt. Put per-request content, such as the user's question, timestamps, or retrieved snippets, at the end. A timestamp or username in the system prompt makes every request's prefix unique from that point on.
* **Append instead of rewriting:** In a multi-turn conversation, add new messages to the end of the history and keep earlier turns byte-identical, so the reusable prefix grows with each turn. Summarizing, truncating, or reordering the history changes the prefix from the first edited message onward.
* **Keep tools stable:** Send the same tool definitions, with the same names, descriptions, schemas, and order, on every request. Tool definitions are part of the prefix, so changing any of them ends the match where the chat template renders them.
* **Set reasoning options once per conversation:** Choose `reasoning` and `reasoning_effort` before the conversation starts. Changing them partway through changes the rendered prompt.
* **Pass reasoning back unchanged:** For models that use [preserved thinking](/docs/inference/chat/reasoning#preserved-thinking), return prior reasoning exactly as the model generated it. Editing or reordering it changes the prefix.
* **Serialize content deterministically:** If your code builds tool schemas or JSON message content, keep the key order the same between requests. The same data serialized in a different order renders as different tokens.
* **Stay on one model:** KV states are specific to the model that computed them, so a cache entry only serves requests to the same model.

Where dynamic content sits decides how much of the prompt the next request can reuse:

<Frame>
  <img src="https://mintcdn.com/togetherai-52386018/DUEk3Wgao1Ml_rVW/images/prompt-caching/dynamic-content-placement.svg?fit=max&auto=format&n=DUEk3Wgao1Ml_rVW&q=85&s=e5e2244d96b7e92b8ad7e880f7c799d8" alt="A timestamp placed before the system prompt leaves almost nothing reusable. The same timestamp placed after the system prompt lets the stable content be read from the cache." width="717" height="141" data-path="images/prompt-caching/dynamic-content-placement.svg" />
</Frame>

When each turn appends to the history, every request reuses most of the previous request's prompt:

<Frame>
  <img src="https://mintcdn.com/togetherai-52386018/DUEk3Wgao1Ml_rVW/images/prompt-caching/multi-turn-caching.svg?fit=max&auto=format&n=DUEk3Wgao1Ml_rVW&q=85&s=51b24660804fe4da28c9dab71ba00f3d" alt="Across three turns of a conversation, each request reads the previous request's prompt from the cache and processes only the latest assistant reply and user message." width="567" height="213" data-path="images/prompt-caching/multi-turn-caching.svg" />
</Frame>

When an earlier turn is summarized or truncated, the next request reuses only the content before the edit:

<Frame>
  <img src="https://mintcdn.com/togetherai-52386018/DUEk3Wgao1Ml_rVW/images/prompt-caching/edited-history.svg?fit=max&auto=format&n=DUEk3Wgao1Ml_rVW&q=85&s=b2c03e0d41f020af12d09584cfb5b2e1" alt="After an earlier user turn is edited, the next request reads only the system prompt from the cache. Everything from the edited turn onward is processed again." width="622" height="166" data-path="images/prompt-caching/edited-history.svg" />
</Frame>

## Route related requests with `prompt_cache_key`

Set `prompt_cache_key` to a stable string on requests that share a prefix, such as a conversation ID or a version name for your application's system prompt. Together uses the key to route those requests as a group, which raises the chance that each one lands where its prefix is already cached. The key improves the odds of a cache hit but doesn't guarantee one.

On dedicated endpoints, `prompt_cache_key` also serves as the request's sampling key for [routing stickiness](/docs/dedicated-endpoints/route-traffic#stickiness), so requests with the same key always route to the same deployment.

In the Python SDK, pass `prompt_cache_key` in `extra_body`, as shown in the example in the next section. In the TypeScript SDK and the REST API, pass it as a top-level request field.

## Check cached tokens

The `usage` object on each response reports how many prompt tokens came from the cache. This example sends two requests that share a long system prompt and prints the cached count for each:

<CodeGroup>
  ```python Python theme={null}
  from together import Together

  client = Together()

  # A long, stable prefix: instructions plus reference material.
  SYSTEM_PROMPT = "You are a support assistant for Acme Cloud. " + " ".join(
      f"Plan tier {i} refunds take {i % 7 + 1} business days."
      for i in range(300)
  )


  def ask(question):
      response = client.chat.completions.create(
          model="moonshotai/Kimi-K3",
          messages=[
              {"role": "system", "content": SYSTEM_PROMPT},
              {"role": "user", "content": question},
          ],
          max_tokens=64,
          extra_body={"prompt_cache_key": "acme-support"},
      )
      usage = response.usage.model_dump()
      cached = (usage.get("prompt_tokens_details") or {}).get(
          "cached_tokens", usage.get("cached_tokens", 0)
      )
      print(f"prompt_tokens={usage['prompt_tokens']} cached_tokens={cached}")


  ask("How long do refunds take for plan tier 12?")
  ask("How long do refunds take for plan tier 40?")
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  // A long, stable prefix: instructions plus reference material.
  const SYSTEM_PROMPT =
    "You are a support assistant for Acme Cloud. " +
    Array.from(
      { length: 300 },
      (_, i) => `Plan tier ${i} refunds take ${(i % 7) + 1} business days.`,
    ).join(" ");

  async function ask(question: string) {
    const response = await together.chat.completions.create({
      model: "moonshotai/Kimi-K3",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: question },
      ],
      max_tokens: 64,
      prompt_cache_key: "acme-support",
    } as any);

    // The SDK's usage type doesn't declare the cached token fields yet.
    const usage = response.usage as {
      prompt_tokens: number;
      prompt_tokens_details?: { cached_tokens?: number };
      cached_tokens?: number;
    };
    const cached =
      usage.prompt_tokens_details?.cached_tokens ?? usage.cached_tokens ?? 0;
    console.log(`prompt_tokens=${usage.prompt_tokens} cached_tokens=${cached}`);
  }

  await ask("How long do refunds take for plan tier 12?");
  await ask("How long do refunds take for plan tier 40?");
  ```

  ```bash cURL theme={null}
  # A long, stable prefix: instructions plus reference material.
  SYSTEM_PROMPT="You are a support assistant for Acme Cloud."
  for i in $(seq 0 299); do
    SYSTEM_PROMPT+=" Plan tier $i refunds take $((i % 7 + 1)) business days."
  done

  ask() {
    curl -s https://api.together.ai/v1/chat/completions \
      -H "Authorization: Bearer $TOGETHER_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$(jq -n --arg system "$SYSTEM_PROMPT" --arg question "$1" '{
        model: "moonshotai/Kimi-K3",
        prompt_cache_key: "acme-support",
        max_tokens: 64,
        messages: [
          {role: "system", content: $system},
          {role: "user", content: $question}
        ]
      }')" |
      jq -r '.usage | "prompt_tokens=\(.prompt_tokens) cached_tokens=\(.prompt_tokens_details.cached_tokens // .cached_tokens // 0)"'
  }

  ask "How long do refunds take for plan tier 12?"
  ask "How long do refunds take for plan tier 40?"
  ```
</CodeGroup>

You should see output similar to this:

```text theme={null}
prompt_tokens=3417 cached_tokens=21
prompt_tokens=3417 cached_tokens=3327
```

The second request reads 3,327 of its 3,417 prompt tokens from the cache. The rest are the tokens after the shared prefix: the new question and the tokens the chat template adds around it. The first request can also report a few cached tokens when the start of its rendered prompt matches an earlier request.

Kimi K3 reports the count in `usage.prompt_tokens_details.cached_tokens`. Some models return `cached_tokens` at the top level of `usage` instead, so the example checks both. See [OpenAI compatibility](/docs/inference/openai-compatibility#response-shape-differences) for the full shape of the `usage` object.

To track your cache hit rate, divide the total `cached_tokens` by the total `prompt_tokens` across your requests.

## Pricing

On serverless inference, cached tokens are billed at the model's cached input rate, listed in the **Cached input pricing** column of [Chat models](/docs/serverless/models#chat-models). All other input tokens are billed at the standard input rate. There's no charge for writing to the cache. Models without a cached input price bill every input token at the standard rate.

For example, the second request in [Check cached tokens](#check-cached-tokens) bills 3,327 cached tokens at Kimi K3's cached input rate and the remaining 90 tokens at its standard input rate.

Dedicated model inference bills for GPU time rather than tokens, so there's no cached-token discount. But caching still pays off: replicas skip computation for cached prefixes, so the same deployment can serve more tokens and reach its first token sooner.

Requests that hit the cache still count toward your [rate limits](/docs/serverless/rate-limits).
