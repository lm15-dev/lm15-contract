> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Log Probabilities

> Get per-token log probabilities from LLM responses.

You can retrieve the log probability of each generated token. This is useful for uncertainty estimation, token-level filtering, confidence scoring, or building custom sampling logic.

Log probabilities are supported across all request modes:

* **OpenAI-compatible API** — using `logprobs` and `top_logprobs` parameters
* **DeepInfra Native API** — streaming and non-streaming

## OpenAI-compatible API

Set `logprobs: true` in your request. Optionally set `top_logprobs` (1–20) to also get the top alternative tokens at each position.

<CodeGroup>
  ```python Python theme={null}
  import os

  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ["DEEPINFRA_API_KEY"],
      base_url="https://api.deepinfra.com/v1/openai",
  )

  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "Say hello in one word"}],
      logprobs=True,
      top_logprobs=3,
  )

  for token in response.choices[0].logprobs.content:
      print(f"{token.token!r}: {token.logprob:.4f}")
      for alt in token.top_logprobs:
          print(f"  alt {alt.token!r}: {alt.logprob:.4f}")
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
      "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
      "messages": [{"role": "user", "content": "Say hello in one word"}],
      "logprobs": true,
      "top_logprobs": 3
    }'
  ```
</CodeGroup>

Response structure:

```json theme={null}
{
  "choices": [{
    "logprobs": {
      "content": [
        {
          "token": "Hello",
          "logprob": -0.0023,
          "top_logprobs": [
            {"token": "Hello", "logprob": -0.0023},
            {"token": "Hi", "logprob": -1.42},
            {"token": "Hey", "logprob": -3.87}
          ]
        }
      ]
    }
  }]
}
```

## DeepInfra Native API (streaming)

The native streaming API returns log probabilities inline with each token as it is generated.

```bash theme={null}
curl -X POST \
    -d '{"input": "I have this dream", "stream": true}' \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -H 'Content-Type: application/json' \
    'https://api.deepinfra.com/v1/inference/deepseek-ai/DeepSeek-V4-Flash-0731'
```

Response (streamed):

```
data: {"token": {"id": 29892, "text": ",", "logprob": -2.65625, "special": false}, "generated_text": null, "details": null}
data: {"token": {"id": 988, "text": " where", "logprob": -0.39575195, "special": false}, "generated_text": null, "details": null}
data: {"token": {"id": 1432, "text": " every", "logprob": -3.15625, "special": false}, "generated_text": null, "details": null}
data: {"token": {"id": 931, "text": " time", "logprob": -0.1385498, "special": false}, "generated_text": null, "details": null}
```

The `logprob` field is the log probability of the generated token (base e). Lower (more negative) values indicate less likely tokens.
