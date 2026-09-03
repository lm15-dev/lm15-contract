Quick Start
Rate Limit & Isolation
On this page
Rate Limit & Isolation

Concurrency Limit​

For each account, the concurrency limits for different DeepSeek API models are shown in the table below.

If you need higher concurrency, you can submit a capacity expansion request. We will match the appropriate concurrency based on your actual business needs. There is no additional cost for capacity expansion.

	deepseek-v4-pro	deepseek-v4-flash	deepseek-v4-flash-vision-exp
Concurrency Limit	500	2500	2500

A request counts as one concurrent connection from the time it is sent until the model response is complete

Concurrency limits are calculated at the account level, regardless of which API Key is used

For a given account, API requests within the concurrency limit will receive a response; when the concurrency limit is exceeded, you will receive an HTTP 429 error code

user_id Isolation​

You can pass the user_id parameter to the API to achieve fine-grained management of different users on your business side under the same account. The specific functions of user_id are as follows:

Content Safety Isolation: user_id is used to distinguish user identities on your business side for content safety handling

KVCache Isolation: user_id is used to isolate KVCache for users on your business side for privacy management

Scheduling Isolation: user_id is used for scheduling isolation of users on your business side

For regular API users, all user_id values are combined for concurrency limit calculation

For API users with increased concurrency quotas, we will limit the total concurrency under your account, and we will also impose concurrency limits on each user_id you pass (an empty id is treated as a special user_id). For each user_id, the concurrency limit for deepseek-v4-pro is 500, for deepseek-v4-flash is 2500, and for deepseek-v4-flash-vision-exp is 2500. If a user_id exceeds its limit, requests with that user_id under your account will receive an HTTP 429 error code

Setting user_id​

The user_id parameter must be a string matching the regex [a-zA-Z0-9\-_]+, with a maximum length of 512. Do not include user privacy information in user_id.

You can set the user_id parameter in the following ways:

OpenAI Chat Completions API​

HTTP request body:

{
    "model": "deepseek-v4-pro",
    "messages": {"role": "user", "content": "Hello!"},
    "user_id": "your_user_id"
}

If you are using the OpenAI SDK, you need to place the user_id parameter under the extra_body parameter:

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "Hello!"}],
    extra_body={"user_id": "your_user_id"}
)

Anthropic API​

HTTP request body:

{
    "model": "deepseek-v4-pro",
    "messages": {"role": "user", "content": "Hello!"},
    "metadata": {"user_id": "your_user_id"},
    "max_tokens": 1024
}

If you are using the Anthropic SDK, the calling method is as follows:

message = client.messages.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "type": "text", "content": "Hello!"}],
    metadata={"user_id": "your_user_id"},
    max_tokens=1024
)

Request Keep-Alive Mechanism​

After your request is sent, it may sometimes take a while to receive a response from the server. During this period, your HTTP request will remain connected, and you may continuously receive contents in the following formats:

Non-streaming requests: Continuously return empty lines

Streaming requests: Continuously return SSE keep-alive comments (: keep-alive)

These contents do not affect the parsing of the JSON body of the response. If you are parsing the HTTP responses yourself, please ensure to handle these empty lines or comments appropriately.

If the request has not started inference after 10 minutes, the server will close the connection.
