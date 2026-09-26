> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Log probabilities

> Return per-token log probabilities to measure model confidence and route low-confidence outputs to a stronger model.

Log probabilities (logprobs) are the per-token probabilities the model assigns when generating a response. Use them to measure how confident the model is for each token, gate low-confidence outputs, or compare them with alternatives the model considered. Common applications include classification, autocomplete ranking, retrieval evaluation, and content moderation.

## Enable logprobs

Pass `logprobs: 1` on a chat completion request:

```python Python theme={null}
from together import Together

client = Together()

completion = client.chat.completions.create(
    model="Qwen/Qwen3.5-9B",
    reasoning={"enabled": False},
    messages=[
        {
            "role": "user",
            "content": "What are the top 3 things to do in New York?",
        }
    ],
    max_tokens=10,
    logprobs=1,
)

print(completion.choices[0].logprobs)
```

The response includes a `logprobs` object on the choice. Its `content` field is a list of one entry per output token, each with the chosen `token`, its raw bytes, and a `logprob`. The `top_logprobs` field on each entry surfaces the alternatives the model considered:

```json JSON theme={null}
{
  "content": [
    {
      "token": "New",
      "bytes": [78, 101, 119],
      "logprob": -0.39648438,
      "top_logprobs": [{ "token": "New", "bytes": [78, 101, 119], "logprob": -0.39648438 }]
    },
    {
      "token": " York",
      "bytes": [32, 89, 111, 114, 107],
      "logprob": -2.026558e-6,
      "top_logprobs": [{ "token": " York", "bytes": [32, 89, 111, 114, 107], "logprob": -2.026558e-6 }]
    }
  ]
}
```

Logprobs are negative numbers because they're natural logs of probabilities (which are between 0 and 1). A value closer to 0 means higher confidence; a more negative value means lower confidence.

## Convert logprobs to probabilities

To get a probability between 0 and 1, take the exponential of the logprob:

```python Python theme={null}
import math


def probability(logprob: float) -> float:
    return math.exp(logprob)


probability(-0.39648438)
# 0.6726 → the model was 67% confident in "New" as the first token
```

For the example above, the second token (`" York"`) has a logprob of `-2.026558e-6`, which converts to roughly 0.999998. The model was effectively certain about `" York"` once it had committed to `"New"`.

Read the per-token logprob from `completion.choices[0].logprobs.content[i]["logprob"]`.

## Route by confidence

A common pattern is to run a fast, cheap model first, then escalate to a larger model only when the cheap one isn't confident. Logprobs let you measure that confidence per response.

The example below classifies an email into one of four categories. If the cheap model's confidence falls below a threshold, the application can re-run the request on a stronger model.

```python Python theme={null}
import math
from together import Together

client = Together()

completion = client.chat.completions.create(
    model="Qwen/Qwen3.5-9B",
    reasoning={"enabled": False},
    messages=[
        {
            "role": "system",
            "content": (
                "You are an email categorizer. Classify the email as one of: "
                "'work', 'personal', 'spam', or 'other'. "
                "Respond with the category name only."
            ),
        },
        {
            "role": "user",
            "content": (
                "I am writing to request a meeting next week to discuss the "
                "progress of Project X. We have reached several key "
                "milestones, and I believe it would be beneficial to review "
                "our current status and plan next steps together. Could we "
                "schedule a time that works best for you?"
            ),
        },
    ],
    logprobs=1,
)

label = completion.choices[0].message.content.strip()
top_logprob = completion.choices[0].logprobs.content[0]["logprob"]
confidence = math.exp(top_logprob)

print(f"Label: {label}, confidence: {confidence:.3f}")

if confidence < 0.85:
    # Confidence is low. Re-run on a larger model.
    pass
```

A typical response classifies the email as `work` with `confidence ≈ 0.99`, well above the threshold. For ambiguous emails the same model often returns confidence in the 0.5 to 0.7 range, which is the signal to escalate.

## When not to use logprobs

* **Open-ended generation:** Logprobs measure token-level certainty, not whether the response is correct. A confident wrong answer is still wrong.
* **Long outputs:** The first few tokens often dominate the meaning of a classification or routing decision. Logprobs deeper in a long response are noisier and less actionable.
* **Cross-model comparison:** Logprob magnitudes aren't directly comparable across model families. A 0.7 confidence from one model isn't the same as 0.7 from another.
