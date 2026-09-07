# InvokeModel

Invokes the specified Amazon Bedrock model to run inference using the prompt and inference parameters provided in the request body. You use model inference to generate text, images, and embeddings.

For example code, see [Invoke model code examples](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-invoke.html#inference-example-invoke).

This operation requires permission for the `bedrock:InvokeModel` action.

**Important**
To deny all inference access to resources that you specify in the modelId field, you need to deny access to the `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` actions. Doing this also denies access to the resource through the Converse API actions ([Converse](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) and [ConverseStream](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html)). For more information see [Deny access for inference on specific models](https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_id-based-policy-examples.html#security_iam_id-based-policy-examples-deny-inference).

For troubleshooting some of the common errors you might encounter when using the `InvokeModel` API, see [Troubleshooting Amazon Bedrock API Error Codes](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html) in the Amazon Bedrock User Guide

## Request Syntax

```
POST /model/{{modelId}}/invoke HTTP/1.1
Content-Type: {{contentType}}
Accept: {{accept}}
X-Amzn-Bedrock-Trace: {{trace}}
X-Amzn-Bedrock-GuardrailIdentifier: {{guardrailIdentifier}}
X-Amzn-Bedrock-GuardrailVersion: {{guardrailVersion}}
X-Amzn-Bedrock-PerformanceConfig-Latency: {{performanceConfigLatency}}
X-Amzn-Bedrock-Service-Tier: {{serviceTier}}
X-Amzn-Bedrock-Request-Metadata: {{requestMetadata}}

{{body}}
```

## URI Request Parameters

The request uses the following URI parameters.

 ** [accept](#API_runtime_InvokeModel_RequestSyntax) **
The desired MIME type of the inference body in the response. The default value is `application/json`.

 ** [contentType](#API_runtime_InvokeModel_RequestSyntax) **
The MIME type of the input data in the request. You must specify `application/json`.

 ** [guardrailIdentifier](#API_runtime_InvokeModel_RequestSyntax) **
The unique identifier of the guardrail that you want to use. If you don't provide a value, no guardrail is applied to the invocation.
An error will be thrown in the following situations.
+ You don't provide a guardrail identifier but you specify the `amazon-bedrock-guardrailConfig` field in the request body.
+ You enable the guardrail but the `contentType` isn't `application/json`.
+ You provide a guardrail identifier, but `guardrailVersion` isn't specified.
Length Constraints: Minimum length of 0. Maximum length of 2048.
Pattern: `(|([a-z0-9]+)|(arn:aws(-[^:]+)?:bedrock:[a-z0-9-]{1,20}:[0-9]{12}:guardrail/[a-z0-9]+))`

 ** [guardrailVersion](#API_runtime_InvokeModel_RequestSyntax) **
The version number for the guardrail. The value can also be `DRAFT`.
Pattern: `(|([1-9][0-9]{0,7})|(DRAFT))`

 ** [modelId](#API_runtime_InvokeModel_RequestSyntax) **
Specifies the model or throughput with which to run inference, or the prompt resource to use in inference. The value depends on the resource that you use:
+ If you use a base model, specify the model ID or its ARN. For a list of model IDs for base models, see [Amazon Bedrock base model IDs (on-demand throughput)](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html) in the Amazon Bedrock User Guide.
+ If you use an Amazon Bedrock Marketplace model, specify the ID or ARN of the marketplace endpoint that you created. For more information about Amazon Bedrock Marketplace and setting up an endpoint, see [Amazon Bedrock Marketplace](https://docs.aws.amazon.com/bedrock/latest/userguide/amazon-bedrock-marketplace.html) in the Amazon Bedrock User Guide.
+ If you use an inference profile, specify the inference profile ID or its ARN. For a list of inference profile IDs, see [Supported Regions and models for cross-region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference-support.html) in the Amazon Bedrock User Guide.
+ If you use a prompt created through [Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html), specify the ARN of the prompt version. For more information, see [Test a prompt using Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-test.html).
+ If you use a provisioned model, specify the ARN of the Provisioned Throughput. For more information, see [Run inference using a Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-thru-use.html) in the Amazon Bedrock User Guide.
+ If you use a custom model, specify the ARN of the custom model deployment (for on-demand inference) or the ARN of your provisioned model (for Provisioned Throughput). For more information, see [Use a custom model in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-use.html) in the Amazon Bedrock User Guide.
+ If you use an [imported model](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-import-model.html), specify the ARN of the imported model. You can get the model ARN from a successful call to [CreateModelImportJob](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_CreateModelImportJob.html) or from the Imported models page in the Amazon Bedrock console.
Length Constraints: Minimum length of 1. Maximum length of 2048.
Pattern: `(arn:aws(-[^:]+)?:bedrock:[a-z0-9-]{1,20}:(([0-9]{12}:custom-model/[a-z0-9-]{1,63}[.]{1}[a-z0-9-]{1,63}/[a-z0-9]{12})|(:foundation-model/[a-z0-9-]{1,63}[.]{1}[a-z0-9-]{1,63}([.:]?[a-z0-9-]{1,63}))|([0-9]{12}:imported-model/[a-z0-9]{12})|([0-9]{12}:provisioned-model/[a-z0-9]{12})|([0-9]{12}:custom-model-deployment/[a-z0-9]{12})|([0-9]{12}:(inference-profile|application-inference-profile)/[a-zA-Z0-9-:.]+)))|([a-z0-9-]{1,63}[.]{1}[a-z0-9-]{1,63}([.:]?[a-z0-9-]{1,63}))|(([0-9a-zA-Z][_-]?)+)|([a-zA-Z0-9-:.]+)$|(^(arn:aws(-[^:]+)?:bedrock:[a-z0-9-]{1,20}:[0-9]{12}:prompt/[0-9a-zA-Z]{10}(?::[0-9]{1,5})?))$|(^arn:aws:sagemaker:[a-z0-9-]+:[0-9]{12}:endpoint/[a-zA-Z0-9-]+$)|(^arn:aws(-[^:]+)?:bedrock:([0-9a-z-]{1,20}):([0-9]{12}):(default-)?prompt-router/[a-zA-Z0-9-:.]+$)`
Required: Yes

 ** [performanceConfigLatency](#API_runtime_InvokeModel_RequestSyntax) **
Model performance settings for the request.
Valid Values: `standard | optimized`

 ** [requestMetadata](#API_runtime_InvokeModel_RequestSyntax) **
Key-value pairs that you can use to filter invocation logs.
Length Constraints: Minimum length of 0. Maximum length of 8500.

 ** [serviceTier](#API_runtime_InvokeModel_RequestSyntax) **
Specifies the processing tier type used for serving the request.
Valid Values: `priority | default | flex | reserved`

 ** [trace](#API_runtime_InvokeModel_RequestSyntax) **
Specifies whether to enable or disable the Bedrock trace. If enabled, you can see the full Bedrock trace.
Valid Values: `ENABLED | DISABLED | ENABLED_FULL`

## Request Body

The request accepts the following binary data.

 ** [body](#API_runtime_InvokeModel_RequestSyntax) **
The prompt and inference parameters in the format specified in the `contentType` in the header. You must provide the body in JSON format. To see the format and content of the request and response bodies for different models, refer to [Inference parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html). For more information, see [Run inference](https://docs.aws.amazon.com/bedrock/latest/userguide/api-methods-run.html) in the Bedrock User Guide.
Length Constraints: Minimum length of 0. Maximum length of 25000000.

## Response Syntax

```
HTTP/1.1 200
Content-Type: {{contentType}}
X-Amzn-Bedrock-PerformanceConfig-Latency: {{performanceConfigLatency}}
X-Amzn-Bedrock-Service-Tier: {{serviceTier}}

{{body}}
```

## Response Elements

If the action is successful, the service sends back an HTTP 200 response.

The response returns the following HTTP headers.

 ** [contentType](#API_runtime_InvokeModel_ResponseSyntax) **
The MIME type of the inference result.

 ** [performanceConfigLatency](#API_runtime_InvokeModel_ResponseSyntax) **
Model performance settings for the request.
Valid Values: `standard | optimized`

 ** [serviceTier](#API_runtime_InvokeModel_ResponseSyntax) **
Specifies the processing tier type used for serving the request.
Valid Values: `priority | default | flex | reserved`

The response returns the following as the HTTP body.

 ** [body](#API_runtime_InvokeModel_ResponseSyntax) **
Inference response from the model in the format specified in the `contentType` header. To see the format and content of the request and response bodies for different models, refer to [Inference parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html).
Length Constraints: Minimum length of 0. Maximum length of 25000000.

## Errors

For information about the errors that are common to all actions, see [Common Error Types](CommonErrors.md).

 ** AccessDeniedException **
The request is denied because you do not have sufficient permissions to perform the requested action. For troubleshooting this error, see [AccessDeniedException](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-access-denied) in the Amazon Bedrock User Guide
HTTP Status Code: 403

 ** InternalServerException **
An internal server error occurred. For troubleshooting this error, see [InternalFailure](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-internal-failure) in the Amazon Bedrock User Guide
HTTP Status Code: 500

 ** ModelErrorException **
The request failed due to an error while processing the model.
 ** originalStatusCode **
The original status code.
 ** resourceName **
The resource name.
HTTP Status Code: 424

 ** ModelNotReadyException **
The model specified in the request is not ready to serve inference requests. The AWS SDK will automatically retry the operation up to 5 times. For information about configuring automatic retries, see [Retry behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html) in the *AWS SDKs and Tools* reference guide.
HTTP Status Code: 429

 ** ModelTimeoutException **
The request took too long to process. Processing time exceeded the model timeout length.
HTTP Status Code: 408

 ** ResourceNotFoundException **
The specified resource ARN was not found. For troubleshooting this error, see [ResourceNotFound](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-resource-not-found) in the Amazon Bedrock User Guide
HTTP Status Code: 404

 ** ServiceQuotaExceededException **
Your request exceeds the service quota for your account. You can view your quotas at [Viewing service quotas](https://docs.aws.amazon.com/servicequotas/latest/userguide/gs-request-quota.html). You can resubmit your request later.
HTTP Status Code: 400

 ** ServiceUnavailableException **
The service isn't currently available. For troubleshooting this error, see [ServiceUnavailable](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-service-unavailable) in the Amazon Bedrock User Guide
HTTP Status Code: 503

 ** ThrottlingException **
Your request was denied due to exceeding the account quotas for *Amazon Bedrock*. For troubleshooting this error, see [ThrottlingException](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-throttling-exception) in the Amazon Bedrock User Guide
HTTP Status Code: 429

 ** ValidationException **
The input fails to satisfy the constraints specified by *Amazon Bedrock*. For troubleshooting this error, see [ValidationError](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-validation-error) in the Amazon Bedrock User Guide
HTTP Status Code: 400

## Examples

### Run inference on a text model

Send an invoke request to run inference on a Titan Text G1 - Express model. We set the `accept` parameter to accept any content type in the response.

#### Sample Request

```
POST https://bedrock-runtime.us-east-1.amazonaws.com/model/amazon.titan-text-express-v1/invoke

-H accept: */*
-H content-type: application/json

Payload
{"inputText": "Hello world"}
```

### Run inference on an image model

In the following example, the request sets the `accept` parameter to `image/png`.

#### Sample Request

```
POST https://bedrock-runtime.us-east-1.amazonaws.com/model/stability.stable-diffusion-xl-v1/invoke

-H accept: image/png
-H content-type: application/json

Payload
{"inputText": "Picture of a bird"}
```

### Use a guardrail

This example shows how to use a guardrail with `InvokeModel`.

#### Sample Request

```
POST /model/modelId/invoke HTTP/1.1
Accept: accept
Content-Type: contentType
X-Amzn-Bedrock-GuardrailIdentifier: guardrailIdentifier
X-Amzn-Bedrock-GuardrailVersion: guardrailVersion
X-Amzn-Bedrock-GuardrailTrace: guardrailTrace
X-Amzn-Bedrock-Trace: trace

body

// body
{
    "amazon-bedrock-guardrailConfig": {
        "tagSuffix": "string"
    }
}
```

### Example response

This is an example response from `InvokeModel` when using a guardrail.

#### Sample Request

```
HTTP/1.1 200
Content-Type: contentType

body

// body
{
  "amazon-bedrock-guardrailAction": "INTERVENED | NONE",
  "amazon-bedrock-trace": {
    "guardrails": {
      //  Detailed guardrail trace
    }
  }
}
```

### Use an inference profile in model invocation

The following request calls the US Anthropic Claude 3.5 Sonnet inference profile to route traffic to the us-east-1 and us-west-2 regions.

#### Sample Request

```
POST /model/us.anthropic.claude-3-5-sonnet-20240620-v1:0/invoke HTTP/1.1

{
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hello world"
                }
            ]
        }
    ]
}
```

## See Also

For more information about using this API in one of the language-specific AWS SDKs, see the following:
+  [AWS Command Line Interface V2](https://docs.aws.amazon.com/goto/cli2/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for .NET V4](https://docs.aws.amazon.com/goto/DotNetSDKV4/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for C\+\+](https://docs.aws.amazon.com/goto/SdkForCpp/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for Go v2](https://docs.aws.amazon.com/goto/SdkForGoV2/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for Java V2](https://docs.aws.amazon.com/goto/SdkForJavaV2/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for JavaScript V3](https://docs.aws.amazon.com/goto/SdkForJavaScriptV3/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for Kotlin](https://docs.aws.amazon.com/goto/SdkForKotlin/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for PHP V3](https://docs.aws.amazon.com/goto/SdkForPHPV3/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for Python](https://docs.aws.amazon.com/goto/boto3/bedrock-runtime-2023-09-30/InvokeModel)
+  [AWS SDK for Ruby V3](https://docs.aws.amazon.com/goto/SdkForRubyV3/bedrock-runtime-2023-09-30/InvokeModel)
