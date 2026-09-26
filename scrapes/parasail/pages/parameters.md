> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/api-reference/parameters.md).

# Parameters

Sampling parameters for the Parasail chat completions and text completions APIs.

Parasail supports all parameters that vLLM supports. These parameters control the randomness, diversity, and length of model outputs.

## Sampling parameters

### `temperature` (default: 1.0)

Controls randomness in token selection.

* Higher values (>1.0) increase randomness.
* Lower values (<1.0) make outputs more deterministic.
* A value of 0 forces greedy decoding.

### `top_p` (Nucleus Sampling) (default: 1.0)

Controls the probability mass of token selection.

* Only considers tokens that sum up to `top_p` probability.
* Lower values (for example, 0.9) limit token choices to more likely options.
* Higher values (close to 1.0) allow a broader range of tokens.

### `top_k` (default: -1, disabled)

Limits token selection to the top `k` most probable tokens.

* Lower values (for example, `top_k=50`) make output more deterministic.
* If `-1`, this setting is ignored.
* Since `top_k` is not in the OpenAI spec, pass it in the `extra_body` field.

### `max_tokens` (default: None)

Sets the maximum number of tokens to generate. Helps prevent excessively long responses.

### `repetition_penalty` (default: 1.0)

Penalizes repeated tokens to avoid looping responses. Common values: 1.1 to 1.2.

### `presence_penalty` (default: 0.0)

Increases the likelihood of introducing new tokens. Useful for making outputs more diverse.

### `frequency_penalty` (default: 0.0)

Penalizes tokens that have appeared frequently. Helps prevent excessive repetition of common words.

### `seed` (default: None)

Sets a fixed seed for reproducible results. Useful for debugging or deterministic sampling.

## How parameters work together

* Setting `temperature=0` forces deterministic output (greedy decoding).
* Using `top_p` and `top_k` together balances diversity and coherence.
* `repetition_penalty` and `presence_penalty` help avoid repetitive loops.

## Example

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>"
)

response = client.chat.completions.create(
    model="parasail-deepseek-r1",
    messages=[{"role": "user", "content": "Write a creative story about a robot."}],
    max_completion_tokens=1000,
    temperature=0.7,
    top_p=0.1,
    repetition_penalty=1.1,
    extra_body={"top_k": 50}
)

print(response.choices[0].message.content)
```

## Next steps

* [Chat completions API](/parasail-docs/api-reference/chat-completions.md)—full chat completions API spec and endpoint compatibility matrix
* [Structured output guide](/parasail-docs/guides/structured-output.md)—constrain outputs to JSON
* [Responses API](/parasail-docs/api-reference/responses-api.md)—parameters for agentic, multi-turn calls
