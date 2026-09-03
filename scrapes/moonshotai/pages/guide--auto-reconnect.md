> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Automatic Reconnection on Disconnect

> Implement automatic reconnection for Kimi API streaming requests and use Partial Mode to continue generation after an interruption.

Due to concurrency limits, complex network environments, and other unforeseen circumstances, our connections may sometimes be interrupted. Typically, these intermittent disruptions don't last long. We want our services to remain stable even in such cases. Implementing a simple reconnection feature can be achieved with just a few lines of code.

<Note>
  The examples on this page use the latest model `kimi-k3` by default. K3 configures reasoning effort with the top-level `reasoning_effort` request field (supports `"low"` / `"high"` / `"max"`, default `"max"`). To use another model such as `kimi-k2.6`, just replace the `model` field — parameter configurations differ across models. See the [Model Parameter Reference](/docs/api/models-overview).
</Note>

```python theme={null}
import os

from openai import OpenAI
import time

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url = "https://api.moonshot.ai/v1",
)

def chat_once(msgs):
    response = client.chat.completions.create(
        model = "kimi-k3",
        messages = msgs
    )
    return response.choices[0].message.content

def chat(input: str, max_attempts: int = 100) -> str | None:
    messages = [
        {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are proficient in Chinese and English conversations. You aim to provide users with safe, helpful, and accurate answers. You will refuse to answer any questions related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated into other languages."},
    ]

    # We construct the user's latest question as a message (role=user) and append it to the end of the messages list
    messages.append({
        "role": "user",
        "content": input,
    })
    st_time = time.time()
    for i in range(max_attempts):
        print(f"Attempts: {i+1}/{max_attempts}")
        try:
            response = chat_once(messages)
            ed_time = time.time()
            print("Query Successful!")
            print(f"Query Time: {ed_time-st_time}")
            return response
        except Exception as e:
            print(e)
            time.sleep(1)
            continue

    print("Query Failed.")
    return

print(chat("Hello, please tell me a fairy tale."))
```

The code above implements a simple reconnection feature, allowing up to 100 retries with a 1-second wait between each attempt. You can adjust these values and the conditions for retries based on your specific needs.
