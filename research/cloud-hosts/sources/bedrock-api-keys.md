# API keys

Amazon Bedrock API keys let you authenticate API requests using a bearer token instead of AWS credentials. There are two types:
+ **Short-term** – Lasts up to 12 hours (or the duration of your session, whichever is shorter). Inherits permissions from the IAM principal used to generate it. Recommended for production use.
+ **Long-term** – Lasts until a configured expiration date. Creates an IAM user with attached policies. Recommended only for exploration.

**Note**
All API calls are logged in AWS CloudTrail. API keys are passed as authorization headers and are not logged.

## Generate a short-term API key

Choose the tab for your preferred method, and then follow the steps:

------
#### [ Console ]

1. Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at [https://console.aws.amazon.com/bedrock](https://console.aws.amazon.com/bedrock).

1. In the left navigation pane, select **API keys**.

1. In the **Short-term API keys** tab, choose **Generate short-term API keys**.

The key expires when your console session expires (max 12 hours). To generate a key for a different Region, switch Regions in the console first.

------
#### [ Python ]

Install the token generator:

```
pip install aws-bedrock-token-generator
```

Generate a token:

```
from aws_bedrock_token_generator import provide_token

token = provide_token()
print(f"Token: {token}")
```

------
#### [ Javascript ]

Install the token generator:

```
npm install @aws/bedrock-token-generator
```

Generate a token:

```
import { getTokenProvider } from "@aws/bedrock-token-generator";

const provideToken = getTokenProvider();
const token = await provideToken();
console.log(`Bearer Token: ${token}`);
```

------
#### [ Java ]

Add the dependency (Maven):

```

    software.amazon.bedrock
    aws-bedrock-token-generator
    1.1.0

```

Generate a token:

```
import software.amazon.bedrock.token.BedrockTokenGenerator;

BedrockTokenGenerator tokenGenerator = BedrockTokenGenerator.builder().build();
String token = tokenGenerator.getToken();
```

------

## Generate a long-term API key

**Warning**
Long-term keys are for exploration only. For production, use short-term keys. For more information, see [Alternatives to long-term access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds-programmatic-access.html#security-creds-alternatives-to-long-term-access-keys).

Choose the tab for your preferred method, and then follow the steps:

------
#### [ Console ]

1. Sign in to the AWS Management Console with an IAM identity that has permissions to use the Amazon Bedrock console. Then, open the Amazon Bedrock console at [https://console.aws.amazon.com/bedrock](https://console.aws.amazon.com/bedrock).

1. In the left navigation pane, select **API keys**.

1. In the **Long-term API keys** tab, choose **Generate long-term API keys**.

1. Choose an expiration time and optionally add permissions in **Advanced permissions**.

1. Choose **Generate**.

------
#### [ CLI ]

```
# Create an IAM user
aws iam create-user --user-name bedrock-api-user

# Attach permissions
aws iam attach-user-policy --user-name bedrock-api-user \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockLimitedAccess

# Generate the API key (replace NUMBER-OF-DAYS)
aws iam create-service-specific-credential \
    --user-name bedrock-api-user \
    --service-name bedrock.amazonaws.com \
    --credential-age-days {{${NUMBER-OF-DAYS}}}
```

The `ServiceApiKeyValue` in the response is your API key.

To deactivate or delete the key later, use the `ServiceSpecificCredentialId` from the response:

```
# Deactivate the key
aws iam update-service-specific-credential \
    --user-name bedrock-api-user \
    --service-specific-credential-id {{${ServiceSpecificCredentialId}}} \
    --status Inactive

# Delete the key permanently
aws iam delete-service-specific-credential \
    --user-name bedrock-api-user \
    --service-specific-credential-id {{${ServiceSpecificCredentialId}}}
```

------
#### [ Python ]

```
import boto3

iam_client = boto3.client("iam")

# Create IAM user
iam_client.create_user(UserName="bedrock-api-user")

# Attach permissions
iam_client.attach_user_policy(
    UserName="bedrock-api-user",
    PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockLimitedAccess"
)

# Generate API key
response = iam_client.create_service_specific_credential(
    UserName="bedrock-api-user",
    ServiceName="bedrock.amazonaws.com",
    CredentialAgeDays=30
)
api_key = response["ServiceSpecificCredential"]["ServiceApiKeyValue"]
print(api_key)
```

------

## Use an API key

Set the key as an environment variable:

```
# macOS/Linux
export AWS_BEARER_TOKEN_BEDROCK={{${api-key}}}

# Windows
setx AWS_BEARER_TOKEN_BEDROCK "{{${api-key}}}"
```

Or pass it directly in the `Authorization` header:

```
Authorization: Bearer {{${api-key}}}
```

**Example: Make a Converse request**
choose the tab for your preferred method, and then follow the steps:

------
#### [ cURL ]

```
curl -X POST "https://bedrock-runtime.us-east-1.amazonaws.com/model/us.anthropic.claude-sonnet-4-6/converse" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AWS_BEARER_TOKEN_BEDROCK" \
  -d '{
    "messages": [{"role": "user", "content": [{"text": "Hello"}]}]
  }'
```

------
#### [ Python (boto3) ]

```
import os
import boto3

os.environ['AWS_BEARER_TOKEN_BEDROCK'] = "{{${api-key}}}"

client = boto3.client("bedrock-runtime", region_name="us-east-1")
response = client.converse(
    modelId="us.anthropic.claude-sonnet-4-6",
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)
```

------

## Auto-refresh short-term keys

For long-running applications, call the token generator before each request. It returns a cached token if still valid or generates a new one automatically:

------
#### [ Python ]

```
from aws_bedrock_token_generator import provide_token
import requests

url = "https://bedrock-runtime.us-west-2.amazonaws.com/model/us.anthropic.claude-sonnet-4-6/converse"
payload = {"messages": [{"role": "user", "content": [{"text": "Hello"}]}]}

# Call provide_token() before each request — it handles caching/refresh
token = provide_token()
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

------
#### [ Javascript ]

```
import { getTokenProvider } from "@aws/bedrock-token-generator";

const provideToken = getTokenProvider();

const url = "https://bedrock-runtime.us-east-1.amazonaws.com/model/us.anthropic.claude-sonnet-4-6/converse";
const payload = {messages: [{role: "user", content: [{text: "Hello"}]}]};

// provideToken() handles caching/refresh automatically
const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${await provideToken()}`
};
await fetch(url, {method: 'POST', headers, body: JSON.stringify(payload)});
```

------

For more examples, see the token generator documentation: [Python](https://github.com/aws/aws-bedrock-token-generator-python/blob/main/README.md) \| [Javascript](https://github.com/aws/aws-bedrock-token-generator-js/blob/main/README.md) \| [Java](https://github.com/aws/aws-bedrock-token-generator-java/blob/main/README.md).

## Modify permissions

A long-term API key is associated with an IAM user. To change its permissions, modify the policies attached to that user. See [Adding and removing IAM identity permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html).

From the console: go to **API keys** > **Long-term API keys** > select your key > **Manage in IAM Console**.

## Compromised keys

If a key is compromised, take one of the following actions:

| Action | Key type | How |
| --- | --- | --- |
| Deactivate | Long-term | Console: API keys > select key > Actions > Deactivate. API: UpdateServiceSpecificCredential with Status=Inactive. |
| Reset | Long-term | Console: Actions > Reset key. API: ResetServiceSpecificCredential. |
| Delete | Long-term | Console: Actions > Delete. API: DeleteServiceSpecificCredential. |
| Invalidate session | Short-term | Invalidate the session used to generate the key, or attach an IAM policy that denies CallWithBearerToken ([Deny an identity the ability to make calls with an Amazon Bedrock API key](api-keys-revoke.md#api-keys-iam-policies-deny-call-with-bearer-token)). |

## Control who can generate and use API keys

IAM actions control API key generation and usage:
+ `iam:CreateServiceSpecificCredential` – Controls generation of long-term keys. Use the `iam:ServiceSpecificCredentialAgeDays` condition key to limit expiration (e.g., max 90 days).
+ `bedrock:CallWithBearerToken` – Controls usage of an API key through the Amazon Bedrock endpoint. Use the `bedrock:bearerTokenType` condition key with values `SHORT_TERM` or `LONG_TERM` to target specific key types.
+ `bedrock-mantle:CallWithBearerToken` – Controls usage of an API key through the Amazon Bedrock Mantle endpoint. Use the `bedrock-mantle:bearerTokenType` condition key with values `SHORT_TERM` or `LONG_TERM` to target specific key types.

**Example: Prevent an identity from using any API key**
Attach this policy to the identity:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": [
                "bedrock:CallWithBearerToken",
                "bedrock-mantle:CallWithBearerToken"
            ],
            "Resource": "*"
        }
    ]
}
```

**Example: Allow only short-lived keys (max 90 days)**
Attach this policy to the identity:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "iam:CreateServiceSpecificCredential",
            "Resource": "*",
            "Condition": {
                "NumericLessThanEquals": {
                    "iam:ServiceSpecificCredentialAgeDays": "90"
                },
                "StringEquals": {
                    "iam:ServiceSpecificCredentialServiceName": "bedrock.amazonaws.com"
                }
            }
        }
    ]
}
```

For more detailed policy examples, see [API keys reference](api-keys-reference.md).
