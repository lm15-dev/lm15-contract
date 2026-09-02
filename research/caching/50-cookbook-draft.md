# Cookbook draft — Prompt caching (as it would read under MAP-6)

Caching makes repeated prompt beginnings cheaper and faster. You control it with one value, `Config(cache=CacheConfig(...))`. You see the result in `response.usage.cache_read_tokens` and `cache_write_tokens`.

## 1. Do nothing

```python
from lm15 import LMRouter, Request, Message

router = LMRouter()
response = router.complete(Request(model="gpt-5.6-sol", messages=[Message.user("hi")]))
print(response.usage.cache_read_tokens)   # None or a number: the provider's own automatic caching
```

Most providers cache on their own. You pay nothing extra and lm15 sends nothing extra. If the number stays `None`, the provider did not report a hit.

## 2. A chat that grows

Mark "everything so far" each turn. The next turn reuses it.

```python
from lm15 import Config, CacheConfig

history = [Message.user("Let's plan a trip.")]
while True:
    request = Request(
        model="claude-sonnet-5",
        system=INSTRUCTIONS,
        messages=history,
        config=Config(cache=CacheConfig(prefix_until_index=len(history) - 1)),
    )
    response = router.complete(request)
    history += [response.message, Message.user(input("> "))]
```

On OpenAI gpt-5.6 and later this is also what happens with no config at all, because OpenAI marks the latest message by itself.

## 3. One big document, many questions

Mark the document, not the question. Every question then reads the document from cache.

```python
request = Request(
    model="claude-sonnet-5",
    messages=[Message.user(DOCUMENT), Message.user(question)],
    config=Config(cache=CacheConfig(prefix_until_index=0)),
)
```

Do this on OpenAI gpt-5.6+ too. Without the mark, OpenAI's automatic mode writes the whole prompt to cache on every question and never reads it back, at 1.25× the input price. Measured, 2026-09-01.

## 4. Keep the beginning stable

A cache hit needs the same beginning: same model, same tools, same system prompt, same earlier messages. Put timestamps and user names at the end, not the start. Changing the tool list means a miss everywhere.

## 5. Gemini: a stored cache you create once

Gemini's guaranteed caching is a stored object with a lifetime. Create it, use its name, delete it when done.

```python
gemini = router.lm("gemini:x")
cache = gemini.cache_create(CacheCreateRequest(
    model="gemini-2.5-flash", system=INSTRUCTIONS, messages=[Message.user(DOCUMENT)], ttl_seconds=3600))
request = Request(
    model="gemini-2.5-flash",
    messages=[Message.user(question)],            # no system, no tools: they live in the cache
    config=Config(cache=CacheConfig(resource=cache.id)),
)
...
gemini.cache_delete(cache.id)
```

Storage is billed per token per hour while the cache exists.

## 6. When lm15 says no

`prefix_until_index`, `retention="long"`, `key`, and `resource` raise `UnsupportedFeatureError` on providers that cannot do that thing. lm15 never pretends. To write provider-agnostic code, use `CacheConfig()` with no arguments and let each provider do its own automatic caching.
