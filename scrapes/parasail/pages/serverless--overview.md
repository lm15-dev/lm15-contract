> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/products/overview.md).

# Serverless

Our Serverless Service offers API based on Token Usage with Popular Models.

## API Usage:

#### UI API:

All of our serverless models are accessible using our OpenAPI spec API. On the Serverless page you can find example code to get the endpoints. If you click on a serverless model:

Our API Gateway is: <https://api.parasail.io/v1>

You will get example code like this:

```python
# pip install openai
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>"
)

chat_completion = client.chat.completions.create(
    model="parasail-deepseek-r1",
    messages=[{"role": "user", "content": "What is the capital of New York?"}]
)

print(chat_completion.choices[0].message.content)
```

You will need to get an API Key from your profile:

#### Getting an API Key:

Which will allow you to generate an API Key:

**The API Key is displayed one time at creation and is not able to be seen again.**

#### Programmatically Find Models:

You can find the model list by using our /models endpoint. You can find it by:

```
curl https://api.parasail.io/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

The API key can be found through the UI like above.

## Using Third-Party Tools Like Cline, AnythingLLM:

Our serverless OpenAI spec allows you to use third-party tools seamlessly just like other popular providers.

Taking the example of Cline, a popular coding tool within Visual Studio:

Find the model you want to use with cline like QwenCoder 32b or DeepSeekR1:

Find the model name, and have your [API Key Ready](#getting-an-api-key),

Then head over to your favorite tool like Cline:

Configure the tool with `https://api.parasail.io/v1` as the base URL, paste your Parasail API key, and select the model name from the Serverless model list.

## Next steps

* [Model-specific notes](/parasail-docs/products/overview/model-specific-notes.md)—DeepSeek, Qwen3.5, and GPT-OSS thinking and reasoning controls
* [Responses API](/parasail-docs/products/overview/responses-api.md)—multi-turn agentic workflows with tool calling
* [Parameters reference](/parasail-docs/api-reference/parameters.md)—sampling parameters such as temperature, top\_p, and top\_k
