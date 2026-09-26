> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/quickstart/serverless.md).

# Serverless

Make your first serverless inference call in under two minutes using the OpenAI SDK.

Make your first serverless API call in under two minutes. Serverless gives you on-demand access to popular open-source models with no setup—just call the API and pay per token.

## 1. Get an API key

1. Go to <https://www.saas.parasail.io/keys>.
2. Click **Create API Key**.
3. Copy the key—it's shown only once.

Store it in your environment:

```bash
export PARASAIL_API_KEY="your-api-key-here"
```

## 2. Install the OpenAI SDK

```bash
pip install openai
```

## 3. Make your first request

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)

chat_completion = client.chat.completions.create(
    model="parasail-deepseek-r1",
    messages=[{"role": "user", "content": "What is the capital of New York?"}]
)

print(chat_completion.choices[0].message.content)
```

## 4. List available models

```bash
curl https://api.parasail.io/v1/models \
  -H "Authorization: Bearer $PARASAIL_API_KEY"
```

## Next steps

* [Serverless overview](/parasail-docs/products/overview.md)—full serverless API guide
* [Parameters reference](/parasail-docs/api-reference/parameters.md)—temperature, top\_p, top\_k, and more
* [Responses API](/parasail-docs/products/overview/responses-api.md)—for multi-turn agentic workflows
* [Chat completions guide](/parasail-docs/guides/chat-completions.md)—understanding messages, roles, and chat templates
* [Use third-party tools](/parasail-docs/products/overview.md#using-third-party-tools-like-cline-anythingllm)—Cline, AnythingLLM, and other OpenAI-compatible tools
