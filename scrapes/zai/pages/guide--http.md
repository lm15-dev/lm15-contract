> ## Documentation Index
> Fetch the complete documentation index at: https://docs.z.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# HTTP API Calls

Z.AI provides standard HTTP API interfaces that support multiple programming languages and development environments, allowing you to easily integrate Z.AI's powerful capabilities.

### Core Advantages

<CardGroup cols={2}>
  <Card title="Cross-platform Compatible" icon="globe">
    Supports all programming languages and platforms that support HTTP protocol
  </Card>

  <Card title="Standard Protocol" icon="shield-check">
    Based on RESTful design, follows HTTP standards, easy to understand and use
  </Card>

  <Card title="Flexible Integration" icon="puzzle-piece">
    Can be integrated into any existing applications and systems
  </Card>

  <Card title="Real-time Calls" icon="bolt">
    Supports synchronous and asynchronous calls to meet different scenario requirements
  </Card>
</CardGroup>

## Get API Key

1. Access [Z.AI Open Platform](https://z.ai/model-api), Register or Login.
2. Create an API Key in the [API Keys](https://z.ai/manage-apikey/apikey-list) management page.
3. Copy your API Key for use.

## API Basic Information

### General API Endpoint

```
https://api.z.ai/api/paas/v4/
```

<Warning>
  When using GLM Coding Plan, please follow the [tutorial](/devpack/quick-start) to configure your dedicated endpoint.
</Warning>

### Request Header Requirements

```http theme={null}
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
```

### Supported Authentication Methods

<Tabs>
  <Tab title="API Key Authentication">
    The simplest authentication method, directly using your API Key:

    ```bash theme={null}
    curl --location 'https://api.z.ai/api/paas/v4/chat/completions' \
    --header 'Authorization: Bearer YOUR_API_KEY' \
    --header 'Accept-Language: en-US,en' \
    --header 'Content-Type: application/json' \
    --data '{
        "model": "glm-5.3",
        "messages": [
            {
                "role": "user",
                "content": "Hello"
            }
        ]
    }'
    ```
  </Tab>

  <Tab title="JWT Token Authentication">
    Use JWT Token for authentication, suitable for scenarios requiring higher security:
    Install PyJWT

    ```shell theme={null}
    pip install PyJWT
    ```

    ```python theme={null}
    import time
    import jwt

    def generate_token(apikey: str, exp_seconds: int):
        try:
            id, secret = apikey.split(".")
        except Exception as e:
            raise Exception("invalid apikey", e)

        payload = {
            "api_key": id,
            "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
            "timestamp": int(round(time.time() * 1000)),
        }

        return jwt.encode(
            payload,
            secret,
            algorithm="HS256",
            headers={"alg": "HS256", "sign_type": "SIGN"},
        )

    # Use the generated token
    token = generate_token("your-api-key", 3600)  # 1 hour validity
    ```
  </Tab>
</Tabs>

## Basic Call Examples

### Simple Conversation

```bash theme={null}
curl --location 'https://api.z.ai/api/paas/v4/chat/completions' \
--header 'Authorization: Bearer YOUR_API_KEY' \
--header 'Accept-Language: en-US,en' \
--header 'Content-Type: application/json' \
--data '{
    "model": "glm-5.3",
    "messages": [
        {
            "role": "user",
            "content": "Please introduce the development history of artificial intelligence"
        }
    ],
    "temperature": 1.0,
    "max_tokens": 1024
}'
```

### Streaming Response

```bash theme={null}
curl --location 'https://api.z.ai/api/paas/v4/chat/completions' \
--header 'Authorization: Bearer YOUR_API_KEY' \
--header 'Accept-Language: en-US,en' \
--header 'Content-Type: application/json' \
--data '{
    "model": "glm-5.3",
    "messages": [
        {
            "role": "user",
            "content": "Write a poem about spring"
        }
    ],
    "stream": true
}'
```

### Multi-turn Conversation

```bash theme={null}
curl --location 'https://api.z.ai/api/paas/v4/chat/completions' \
--header 'Authorization: Bearer YOUR_API_KEY' \
--header 'Accept-Language: en-US,en' \
--header 'Content-Type: application/json' \
--data '{
    "model": "glm-5.3",
    "messages": [
        {
            "role": "system",
            "content": "You are a professional programming assistant"
        },
        {
            "role": "user",
            "content": "What is recursion?"
        },
        {
            "role": "assistant",
            "content": "Recursion is a programming technique where a function calls itself to solve problems..."
        },
        {
            "role": "user",
            "content": "Can you give me an example of Python recursion?"
        }
    ]
}'
```

## Common Programming Language Examples

<Tabs>
  <Tab title="Python">
    ```python theme={null}
    import requests
    import json

    def call_zai_api(messages, model="glm-5.3"):
        url = "https://api.z.ai/api/paas/v4/chat/completions"

        headers = {
            "Authorization": "Bearer YOUR_API_KEY",
            "Content-Type": "application/json",
            "Accept-Language": "en-US,en"
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": 1.0
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API call failed: {response.status_code}, {response.text}")

    # Usage example
    messages = [
        {"role": "user", "content": "Hello, please introduce yourself"}
    ]

    result = call_zai_api(messages)
    print(result['choices'][0]['message']['content'])
    ```
  </Tab>

  <Tab title="JavaScript">
    ```javascript theme={null}
    async function callZAPI(messages, model = 'glm-5.3') {
        const url = 'https://api.z.ai/api/paas/v4/chat/completions';

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer YOUR_API_KEY',
                'Content-Type': 'application/json',
                'Accept-Language': 'en-US,en'
            },
            body: JSON.stringify({
                model: model,
                messages: messages,
                temperature: 1.0
            })
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.status}`);
        }

        return await response.json();
    }

    // Usage example
    const messages = [
        { role: 'user', content: 'Hello, please introduce yourself' }
    ];

    callZAPI(messages)
        .then(result => {
            console.log(result.choices[0].message.content);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    ```
  </Tab>

  <Tab title="Java">
    ```java theme={null}
    import com.fasterxml.jackson.databind.ObjectMapper;
    import okhttp3.MediaType;
    import okhttp3.OkHttpClient;
    import okhttp3.Request;
    import okhttp3.RequestBody;
    import okhttp3.Response;
    import java.util.Collections;
    import java.util.HashMap;
    import java.util.Map;

    public class AgentExample {

        public static void main(String[] args) throws Exception {

            OkHttpClient client = new OkHttpClient();
            ObjectMapper mapper = new ObjectMapper();
            Map<String, String> messages = new HashMap<>(8);
            messages.put("role", "user");
            messages.put("content", "Hello, please introduce yourself");
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", "glm-5.3");
            requestBody.put("messages", Collections.singletonList(messages));
            requestBody.put("temperature", 1.0);

            String jsonBody = mapper.writeValueAsString(requestBody);
            MediaType JSON = MediaType.get("application/json; charset=utf-8");
            RequestBody body = RequestBody.create(JSON, jsonBody);
            Request request = new Request.Builder()
                .url("https://api.z.ai/api/paas/v4/chat/completions")
                .addHeader("Authorization", "Bearer your_api_key")
                .addHeader("Content-Type", "application/json")
                .addHeader("Accept-Language", "en-US,en")
                .post(body)
                .build();
            try (Response response = client.newCall(request).execute()) {
                System.out.println(response.body().string());
            }
        }
    }
    ```
  </Tab>
</Tabs>

## Best Practices

<CardGroup cols={2}>
  <Card title="Security" icon="shield">
    * Properly secure API Keys, do not hard-code them in your code
    * Use environment variables or configuration files to store sensitive information
    * Regularly rotate API Keys
  </Card>

  <Card title="Performance Optimization" icon="gauge-high">
    * Implement connection pooling and session reuse
    * Set reasonable timeout values
    * Use asynchronous requests for high-concurrency scenarios
  </Card>

  <Card title="Error Handling" icon="code">
    * Implement exponential backoff retry mechanisms
    * Log detailed error information
    * Set reasonable timeout and retry limits
  </Card>

  <Card title="Monitoring" icon="chart-line">
    * Monitor API call frequency and success rates
    * Track response times and error rates
    * Set up alerting mechanisms
  </Card>
</CardGroup>

## Get More

<CardGroup cols={2}>
  <Card title="API Documentation" icon="book" href="/api-reference">
    View complete API interface documentation and parameter descriptions
  </Card>

  <Card title="Technical Support" icon="headset" href="https://z.ai/contact">
    Get technical support and assistance
  </Card>
</CardGroup>

<Note>
  It is recommended to use HTTPS protocol in production environments and implement appropriate security measures to protect your API keys and data transmission.
</Note>
