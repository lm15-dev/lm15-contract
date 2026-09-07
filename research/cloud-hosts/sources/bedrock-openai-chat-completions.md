# Chat Completions API

The OpenAI Chat Completions API generates conversational responses using Amazon Bedrock models. For new applications, we recommend the `bedrock-runtime` endpoint (see [Chat Completions API (legacy reference)](inference-chat-completions.md)). This page documents the API on the `bedrock-mantle` endpoint, which is also fully supported. For complete API details, see the [OpenAI Chat Completions documentation](https://developers.openai.com/api/reference/chat-completions/overview).

| **Endpoint** | **Base URL** | **Authentication** |
| --- | --- | --- |
| bedrock-mantle | https://bedrock-mantle.{region}.api.aws/v1/chat/completions | Amazon Bedrock API key or AWS credentials |
| bedrock-runtime (recommended) | https://bedrock-runtime.{region}.amazonaws.com/openai/v1/chat/completions | AWS credentials (SigV4) or Amazon Bedrock API key |

Each endpoint has its own per-model token quotas. For details on the quotas applied to traffic on each endpoint, see [Quotas for the bedrock-mantle endpoint](quotas-mantle.md) and [Quotas for the bedrock-runtime endpoint](quotas-runtime.md).

## Chat Completions with the bedrock-mantle endpoint

The `bedrock-mantle` endpoint supports Amazon Bedrock API key authentication and the OpenAI SDK.

### List available models

To list models available on the `bedrock-mantle` endpoint, choose the tab for your preferred method, and then follow the steps:

------
#### [ OpenAI SDK (Python) ]

```
# List all available models using the OpenAI SDK
# Requires OPENAI_API_KEY and OPENAI_BASE_URL environment variables

from openai import OpenAI

client = OpenAI()

models = client.models.list()

for model in models.data:
    print(model.id)
```

------
#### [ HTTP request ]

```
# List all available models
# Requires OPENAI_API_KEY and OPENAI_BASE_URL environment variables

curl -X GET $OPENAI_BASE_URL/models \
   -H "Authorization: Bearer $OPENAI_API_KEY"
```

------

### Create a chat completion

Choose the tab for your preferred method, and then follow the steps:

------
#### [ OpenAI SDK (Python) ]

Configure the OpenAI client using environment variables:

```
# Create a chat completion using the OpenAI SDK
# Requires OPENAI_API_KEY and OPENAI_BASE_URL environment variables

from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(completion.choices[0].message)
```

------
#### [ HTTP request ]

Make a POST request to `/v1/chat/completions`:

```
# Create a chat completion
# Requires OPENAI_API_KEY and OPENAI_BASE_URL environment variables

curl -X POST $OPENAI_BASE_URL/chat/completions \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer $OPENAI_API_KEY" \
   -d '{
    "model": "openai.gpt-oss-120b",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
}'
```

------

**Streaming**
To receive responses incrementally, choose the tab for your preferred method, and then follow the steps:

------
#### [ OpenAI SDK (Python) ]

```
# Stream chat completion responses incrementally using the OpenAI SDK
# Requires OPENAI_API_KEY and OPENAI_BASE_URL environment variables

from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

------
#### [ HTTP request ]

Make a POST request to `/v1/chat/completions` with `stream` set to `true`:

```
# Stream chat completion responses incrementally
# Requires OPENAI_API_KEY and OPENAI_BASE_URL environment variables

curl -X POST $OPENAI_BASE_URL/chat/completions \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer $OPENAI_API_KEY" \
   -d '{
    "model": "openai.gpt-oss-120b",
    "messages": [
        {"role": "user", "content": "Tell me a story"}
    ],
    "stream": true
}'
```

------

## Chat Completions with the bedrock-runtime endpoint

The `bedrock-runtime` endpoint supports AWS SigV4 authentication and Amazon Bedrock API key authentication.

### List available models

To list models available on the `bedrock-runtime` endpoint, choose the tab for your preferred method, and then follow the steps:

------
#### [ OpenAI SDK (Python) ]

```
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1",
    api_key=os.environ.get("AWS_BEARER_TOKEN_BEDROCK")
)

models = client.models.list()
for model in models.data:
    print(model.id)
```

------
#### [ HTTP request ]

```
curl -X GET "https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1/models" \
  -H "Authorization: Bearer $AWS_BEARER_TOKEN_BEDROCK"
```

------

### Create a chat completion

Choose the tab for your preferred method, and then follow the steps:

------
#### [ OpenAI SDK (Python) ]

Configure the OpenAI client to point to the `bedrock-runtime` endpoint:

```
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1",
    api_key=os.environ.get("AWS_BEARER_TOKEN_BEDROCK")
)

response = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

------
#### [ HTTP request (API key) ]

```
curl -X POST "https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AWS_BEARER_TOKEN_BEDROCK" \
  -d '{
    "model": "openai.gpt-oss-120b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

------
#### [ HTTP request (SigV4) ]

```
curl -X POST "https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  --aws-sigv4 "aws:amz:us-east-1:bedrock" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
  -d '{
    "model": "openai.gpt-oss-120b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

------

For more details on supported models, Regions, and advanced features with the `bedrock-runtime` endpoint, see [Chat Completions API (legacy reference)](inference-chat-completions.md).

## Include a guardrail in a chat completion

To include safeguards in model input and responses, apply a [guardrail](guardrails.md) when running model invocation by including the following [extra parameters](https://github.com/openai/openai-python#undocumented-request-params) as fields in the request body:
+ `extra_headers` – Maps to an object containing the following fields, which specify extra headers in the request:
  + `X-Amzn-Bedrock-GuardrailIdentifier` (required) – The ID of the guardrail.
  + `X-Amzn-Bedrock-GuardrailVersion` (required) – The version of the guardrail.
  + `X-Amzn-Bedrock-Trace` (optional) – Whether or not to enable the guardrail trace.
+ `extra_body` – Maps to an object. In that object, you can include the `amazon-bedrock-guardrailConfig` field, which maps to an object containing the following fields:
  + `tagSuffix` (optional) – Include this field for [input tagging](guardrails-tagging.md).

For more information about these parameters in Amazon Bedrock Guardrails, see [Test your guardrail](guardrails-test.md).

To see examples of using guardrails with OpenAI chat completions, choose the tab for your preferred method, and then follow the steps:

------
#### [ OpenAI SDK (Python) ]

```
import openai
from openai import OpenAIError

# Endpoint for Amazon Bedrock Runtime
bedrock_endpoint = "https://bedrock-runtime.us-west-2.amazonaws.com/openai/v1"

# Model ID
model_id = "openai.gpt-oss-20b-1:0"

# Replace with actual values
bedrock_api_key = "$AWS_BEARER_TOKEN_BEDROCK"
guardrail_id = "GR12345"
guardrail_version = "DRAFT"

client = openai.OpenAI(
    api_key=bedrock_api_key,
    base_url=bedrock_endpoint,
)

try:
    response = client.chat.completions.create(
        model=model_id,
        # Specify guardrail information in the header
        extra_headers={
            "X-Amzn-Bedrock-GuardrailIdentifier": guardrail_id,
            "X-Amzn-Bedrock-GuardrailVersion": guardrail_version,
            "X-Amzn-Bedrock-Trace": "ENABLED",
        },
        # Additional guardrail information can be specified in the body
        extra_body={
            "amazon-bedrock-guardrailConfig": {
                "tagSuffix": "xyz"  # Used for input tagging
            }
        },
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "assistant",
                "content": "Hello! How can I help you today?"
            },
            {
                "role": "user",
                "content": "What is the weather like today?"
            }
        ]
    )

    request_id = response._request_id
    print(f"Request ID: {request_id}")
    print(response)

except OpenAIError as e:
    print(f"An error occurred: {e}")
    if hasattr(e, 'response') and e.response is not None:
        request_id = e.response.headers.get("x-request-id")
        print(f"Request ID: {request_id}")
```

------
#### [ OpenAI SDK (Java) ]

```
import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.core.http.HttpResponseFor;
import com.openai.models.chat.completions.ChatCompletion;
import com.openai.models.chat.completions.ChatCompletionCreateParams;

// Endpoint for Amazon Bedrock Runtime
String bedrockEndpoint = "http://bedrock-runtime.us-west-2.amazonaws.com/openai/v1"

// Model ID
String modelId = "openai.gpt-oss-20b-1:0"

// Replace with actual values
String bedrockApiKey = "$AWS_BEARER_TOKEN_BEDROCK"
String guardrailId = "GR12345"
String guardrailVersion = "DRAFT"

OpenAIClient client = OpenAIOkHttpClient.builder()
        .apiKey(bedrockApiKey)
        .baseUrl(bedrockEndpoint)
        .build()

ChatCompletionCreateParams request = ChatCompletionCreateParams.builder()
        .addUserMessage("What is the temperature in Seattle?")
        .model(modelId)
        // Specify additional headers for the guardrail
        .putAdditionalHeader("X-Amzn-Bedrock-GuardrailIdentifier", guardrailId)
        .putAdditionalHeader("X-Amzn-Bedrock-GuardrailVersion", guardrailVersion)
        // Specify additional body parameters for the guardrail
        .putAdditionalBodyProperty(
                "amazon-bedrock-guardrailConfig",
                JsonValue.from(Map.of("tagSuffix", JsonValue.of("xyz"))) // Allows input tagging
        )
        .build();

HttpResponseFor rawChatCompletionResponse =
        client.chat().completions().withRawResponse().create(request);

final ChatCompletion chatCompletion = rawChatCompletionResponse.parse();

System.out.println(chatCompletion);
```

------
