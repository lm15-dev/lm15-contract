# ConverseStream

Sends messages to the specified Amazon Bedrock model and returns the response in a stream. `ConverseStream` provides a consistent API that works with all Amazon Bedrock models that support messages. This allows you to write code once and use it with different models. Should a model have unique inference parameters, you can also pass those unique parameters to the model.

To find out if a model supports streaming, call [GetFoundationModel](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_GetFoundationModel.html) and check the `responseStreamingSupported` field in the response.

**Note**
The AWS CLI doesn't support streaming operations in Amazon Bedrock, including `ConverseStream`.

Amazon Bedrock doesn't store any text, images, or documents that you provide as content. The data is only used to generate the response.

You can submit a prompt by including it in the `messages` field, specifying the `modelId` of a foundation model or inference profile to run inference on it, and including any other fields that are relevant to your use case.

You can also submit a prompt from Prompt management by specifying the ARN of the prompt version and including a map of variables to values in the `promptVariables` field. You can append more messages to the prompt by using the `messages` field. If you use a prompt from Prompt management, you can't include the following fields in the request: `additionalModelRequestFields`, `inferenceConfig`, `system`, or `toolConfig`. Instead, these fields must be defined through Prompt management. For more information, see [Test a prompt using Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-test.html).

For information about the Converse API, see [Use the Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html). To use a guardrail, see [Use a guardrail with the Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-converse-api.html). To use a tool with a model, see [Tool use (Function calling)](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html).

For example code, see [Conversation streaming example](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html#messages-streaming-inference-example).

This operation requires permission for the `bedrock:InvokeModelWithResponseStream` action.

**Important**
To deny all inference access to resources that you specify in the modelId field, you need to deny access to the `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` actions. Doing this also denies access to the resource through the base inference actions ([InvokeModel](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html) and [InvokeModelWithResponseStream](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html)). For more information see [Deny access for inference on specific models](https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_id-based-policy-examples.html#security_iam_id-based-policy-examples-deny-inference).

For troubleshooting some of the common errors you might encounter when using the `ConverseStream` API, see [Troubleshooting Amazon Bedrock API Error Codes](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html) in the Amazon Bedrock User Guide

## Request Syntax

```
POST /model/{{modelId}}/converse-stream HTTP/1.1
Content-type: application/json

{
   "additionalModelRequestFields": {{JSON value}},
   "additionalModelResponseFieldPaths": [ "{{string}}" ],
   "guardrailConfig": {
      "guardrailIdentifier": "{{string}}",
      "guardrailVersion": "{{string}}",
      "streamProcessingMode": "{{string}}",
      "trace": "{{string}}"
   },
   "inferenceConfig": {
      "maxTokens": {{number}},
      "stopSequences": [ "{{string}}" ],
      "temperature": {{number}},
      "topP": {{number}}
   },
   "messages": [
      {
         "content": [
            { ... }
         ],
         "role": "{{string}}"
      }
   ],
   "outputConfig": {
      "textFormat": {
         "structure": { ... },
         "type": "{{string}}"
      }
   },
   "performanceConfig": {
      "latency": "{{string}}"
   },
   "promptVariables": {
      "{{string}}" : { ... }
   },
   "requestMetadata": {
      "{{string}}" : "{{string}}"
   },
   "serviceTier": {
      "type": "{{string}}"
   },
   "system": [
      { ... }
   ],
   "toolConfig": {
      "toolChoice": { ... },
      "tools": [
         { ... }
      ]
   }
}
```

## URI Request Parameters

The request uses the following URI parameters.

 ** [modelId](#API_runtime_ConverseStream_RequestSyntax) **
Specifies the model or throughput with which to run inference, or the prompt resource to use in inference. The value depends on the resource that you use:
+ If you use a base model, specify the model ID or its ARN. For a list of model IDs for base models, see [Amazon Bedrock base model IDs (on-demand throughput)](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html) in the Amazon Bedrock User Guide.
+ If you use an Amazon Bedrock Marketplace model, specify the ID or ARN of the marketplace endpoint that you created. For more information about Amazon Bedrock Marketplace and setting up an endpoint, see [Amazon Bedrock Marketplace](https://docs.aws.amazon.com/bedrock/latest/userguide/amazon-bedrock-marketplace.html) in the Amazon Bedrock User Guide.
+ If you use an inference profile, specify the inference profile ID or its ARN. For a list of inference profile IDs, see [Supported Regions and models for cross-region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference-support.html) in the Amazon Bedrock User Guide.
+ If you use a prompt created through [Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html), specify the ARN of the prompt version. For more information, see [Test a prompt using Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-test.html).
+ If you use a provisioned model, specify the ARN of the Provisioned Throughput. For more information, see [Run inference using a Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-thru-use.html) in the Amazon Bedrock User Guide.
+ If you use a custom model, specify the ARN of the custom model deployment (for on-demand inference) or the ARN of your provisioned model (for Provisioned Throughput). For more information, see [Use a custom model in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-use.html) in the Amazon Bedrock User Guide.
Length Constraints: Minimum length of 1. Maximum length of 2048.
Pattern: `(arn:aws(-[^:]+)?:bedrock:[a-z0-9-]{1,20}:(([0-9]{12}:custom-model/[a-z0-9-]{1,63}[.]{1}[a-z0-9-]{1,63}/[a-z0-9]{12})|(:foundation-model/[a-z0-9-]{1,63}[.]{1}[a-z0-9-]{1,63}([.:]?[a-z0-9-]{1,63}))|([0-9]{12}:imported-model/[a-z0-9]{12})|([0-9]{12}:provisioned-model/[a-z0-9]{12})|([0-9]{12}:custom-model-deployment/[a-z0-9]{12})|([0-9]{12}:(inference-profile|application-inference-profile)/[a-zA-Z0-9-:.]+)))|([a-z0-9-]{1,63}[.]{1}[a-z0-9-]{1,63}([.:]?[a-z0-9-]{1,63}))|(([0-9a-zA-Z][_-]?)+)|([a-zA-Z0-9-:.]+)|(^(arn:aws(-[^:]+)?:bedrock:[a-z0-9-]{1,20}:[0-9]{12}:prompt/[0-9a-zA-Z]{10}(?::[0-9]{1,5})?))$|(^arn:aws:sagemaker:[a-z0-9-]+:[0-9]{12}:endpoint/[a-zA-Z0-9-]+$)|(^arn:aws(-[^:]+)?:bedrock:([0-9a-z-]{1,20}):([0-9]{12}):(default-)?prompt-router/[a-zA-Z0-9-:.]+$)`
Required: Yes

## Request Body

The request accepts the following data in JSON format.

 ** [additionalModelRequestFields](#API_runtime_ConverseStream_RequestSyntax) **
Additional inference parameters that the model supports, beyond the base set of inference parameters that `Converse` and `ConverseStream` support in the `inferenceConfig` field. For more information, see [Model parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html).
Type: JSON value
Required: No

 ** [additionalModelResponseFieldPaths](#API_runtime_ConverseStream_RequestSyntax) **
Additional model parameters field paths to return in the response. `Converse` and `ConverseStream` return the requested fields as a JSON Pointer object in the `additionalModelResponseFields` field. The following is example JSON for `additionalModelResponseFieldPaths`.
 `[ "/stop_sequence" ]`
For information about the JSON Pointer syntax, see the [Internet Engineering Task Force (IETF)](https://datatracker.ietf.org/doc/html/rfc6901) documentation.
 `Converse` and `ConverseStream` reject an empty JSON Pointer or incorrectly structured JSON Pointer with a `400` error code. if the JSON Pointer is valid, but the requested field is not in the model response, it is ignored by `Converse`.
Type: Array of strings
Array Members: Minimum number of 0 items. Maximum number of 10 items.
Length Constraints: Minimum length of 1. Maximum length of 256.
Required: No

 ** [guardrailConfig](#API_runtime_ConverseStream_RequestSyntax) **
Configuration information for a guardrail that you want to use in the request. If you include `guardContent` blocks in the `content` field in the `messages` field, the guardrail operates only on those messages. If you include no `guardContent` blocks, the guardrail operates on all messages in the request body and in any included prompt resource.
Type: [GuardrailStreamConfiguration](API_runtime_GuardrailStreamConfiguration.md) object
Required: No

 ** [inferenceConfig](#API_runtime_ConverseStream_RequestSyntax) **
Inference parameters to pass to the model. `Converse` and `ConverseStream` support a base set of inference parameters. If you need to pass additional parameters that the model supports, use the `additionalModelRequestFields` request field.
Type: [InferenceConfiguration](API_runtime_InferenceConfiguration.md) object
Required: No

 ** [messages](#API_runtime_ConverseStream_RequestSyntax) **
The messages that you want to send to the model.
Type: Array of [Message](API_runtime_Message.md) objects
Required: No

 ** [outputConfig](#API_runtime_ConverseStream_RequestSyntax) **
Output configuration for a model response.
Type: [OutputConfig](API_runtime_OutputConfig.md) object
Required: No

 ** [performanceConfig](#API_runtime_ConverseStream_RequestSyntax) **
Model performance settings for the request.
Type: [PerformanceConfiguration](API_runtime_PerformanceConfiguration.md) object
Required: No

 ** [promptVariables](#API_runtime_ConverseStream_RequestSyntax) **
Contains a map of variables in a prompt from Prompt management to objects containing the values to fill in for them when running model invocation. This field is ignored if you don't specify a prompt resource in the `modelId` field.
Type: String to [PromptVariableValues](API_runtime_PromptVariableValues.md) object map
Required: No

 ** [requestMetadata](#API_runtime_ConverseStream_RequestSyntax) **
Key-value pairs that you can use to filter invocation logs.
Type: String to string map
Map Entries: Maximum number of 16 items.
Key Length Constraints: Minimum length of 1. Maximum length of 256.
Key Pattern: `[a-zA-Z0-9\s:_@$#=/+,-.]{1,256}`
Value Length Constraints: Minimum length of 0. Maximum length of 256.
Value Pattern: `[a-zA-Z0-9\s:_@$#=/+,-.]{0,256}`
Required: No

 ** [serviceTier](#API_runtime_ConverseStream_RequestSyntax) **
Specifies the processing tier configuration used for serving the request.
Type: [ServiceTier](API_runtime_ServiceTier.md) object
Required: No

 ** [system](#API_runtime_ConverseStream_RequestSyntax) **
A prompt that provides instructions or context to the model about the task it should perform, or the persona it should adopt during the conversation.
Type: Array of [SystemContentBlock](API_runtime_SystemContentBlock.md) objects
Required: No

 ** [toolConfig](#API_runtime_ConverseStream_RequestSyntax) **
Configuration information for the tools that the model can use when generating a response.
For information about models that support streaming tool use, see [Supported models and model features](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html#conversation-inference-supported-models-features).
Type: [ToolConfiguration](API_runtime_ToolConfiguration.md) object
Required: No

## Response Syntax

```
HTTP/1.1 200
Content-type: application/json

{
   "contentBlockDelta": {
      "contentBlockIndex": number,
      "delta": { ... }
   },
   "contentBlockStart": {
      "contentBlockIndex": number,
      "start": { ... }
   },
   "contentBlockStop": {
      "contentBlockIndex": number
   },
   "internalServerException": {
   },
   "messageStart": {
      "role": "string"
   },
   "messageStop": {
      "additionalModelResponseFields": JSON value,
      "stopReason": "string"
   },
   "metadata": {
      "metrics": {
         "latencyMs": number
      },
      "performanceConfig": {
         "latency": "string"
      },
      "serviceTier": {
         "type": "string"
      },
      "trace": {
         "guardrail": {
            "actionReason": "string",
            "inputAssessment": {
               "string" : {
                  "appliedGuardrailDetails": {
                     "guardrailArn": "string",
                     "guardrailId": "string",
                     "guardrailOrigin": [ "string" ],
                     "guardrailOwnership": "string",
                     "guardrailVersion": "string"
                  },
                  "automatedReasoningPolicy": {
                     "findings": [
                        { ... }
                     ]
                  },
                  "contentPolicy": {
                     "filters": [
                        {
                           "action": "string",
                           "confidence": "string",
                           "detected": boolean,
                           "filterStrength": "string",
                           "type": "string"
                        }
                     ]
                  },
                  "contextualGroundingPolicy": {
                     "filters": [
                        {
                           "action": "string",
                           "detected": boolean,
                           "score": number,
                           "threshold": number,
                           "type": "string"
                        }
                     ]
                  },
                  "invocationMetrics": {
                     "guardrailCoverage": {
                        "images": {
                           "guarded": number,
                           "total": number
                        },
                        "textCharacters": {
                           "guarded": number,
                           "total": number
                        }
                     },
                     "guardrailProcessingLatency": number,
                     "usage": {
                        "automatedReasoningPolicies": number,
                        "automatedReasoningPolicyUnits": number,
                        "contentPolicyImageUnits": number,
                        "contentPolicyUnits": number,
                        "contextualGroundingPolicyUnits": number,
                        "sensitiveInformationPolicyFreeUnits": number,
                        "sensitiveInformationPolicyUnits": number,
                        "topicPolicyUnits": number,
                        "wordPolicyUnits": number
                     }
                  },
                  "sensitiveInformationPolicy": {
                     "piiEntities": [
                        {
                           "action": "string",
                           "detected": boolean,
                           "match": "string",
                           "type": "string"
                        }
                     ],
                     "regexes": [
                        {
                           "action": "string",
                           "detected": boolean,
                           "match": "string",
                           "name": "string",
                           "regex": "string"
                        }
                     ]
                  },
                  "topicPolicy": {
                     "topics": [
                        {
                           "action": "string",
                           "detected": boolean,
                           "name": "string",
                           "type": "string"
                        }
                     ]
                  },
                  "wordPolicy": {
                     "customWords": [
                        {
                           "action": "string",
                           "detected": boolean,
                           "match": "string"
                        }
                     ],
                     "managedWordLists": [
                        {
                           "action": "string",
                           "detected": boolean,
                           "match": "string",
                           "type": "string"
                        }
                     ]
                  }
               }
            },
            "modelOutput": [ "string" ],
            "outputAssessments": {
               "string" : [
                  {
                     "appliedGuardrailDetails": {
                        "guardrailArn": "string",
                        "guardrailId": "string",
                        "guardrailOrigin": [ "string" ],
                        "guardrailOwnership": "string",
                        "guardrailVersion": "string"
                     },
                     "automatedReasoningPolicy": {
                        "findings": [
                           { ... }
                        ]
                     },
                     "contentPolicy": {
                        "filters": [
                           {
                              "action": "string",
                              "confidence": "string",
                              "detected": boolean,
                              "filterStrength": "string",
                              "type": "string"
                           }
                        ]
                     },
                     "contextualGroundingPolicy": {
                        "filters": [
                           {
                              "action": "string",
                              "detected": boolean,
                              "score": number,
                              "threshold": number,
                              "type": "string"
                           }
                        ]
                     },
                     "invocationMetrics": {
                        "guardrailCoverage": {
                           "images": {
                              "guarded": number,
                              "total": number
                           },
                           "textCharacters": {
                              "guarded": number,
                              "total": number
                           }
                        },
                        "guardrailProcessingLatency": number,
                        "usage": {
                           "automatedReasoningPolicies": number,
                           "automatedReasoningPolicyUnits": number,
                           "contentPolicyImageUnits": number,
                           "contentPolicyUnits": number,
                           "contextualGroundingPolicyUnits": number,
                           "sensitiveInformationPolicyFreeUnits": number,
                           "sensitiveInformationPolicyUnits": number,
                           "topicPolicyUnits": number,
                           "wordPolicyUnits": number
                        }
                     },
                     "sensitiveInformationPolicy": {
                        "piiEntities": [
                           {
                              "action": "string",
                              "detected": boolean,
                              "match": "string",
                              "type": "string"
                           }
                        ],
                        "regexes": [
                           {
                              "action": "string",
                              "detected": boolean,
                              "match": "string",
                              "name": "string",
                              "regex": "string"
                           }
                        ]
                     },
                     "topicPolicy": {
                        "topics": [
                           {
                              "action": "string",
                              "detected": boolean,
                              "name": "string",
                              "type": "string"
                           }
                        ]
                     },
                     "wordPolicy": {
                        "customWords": [
                           {
                              "action": "string",
                              "detected": boolean,
                              "match": "string"
                           }
                        ],
                        "managedWordLists": [
                           {
                              "action": "string",
                              "detected": boolean,
                              "match": "string",
                              "type": "string"
                           }
                        ]
                     }
                  }
               ]
            }
         },
         "promptRouter": {
            "invokedModelId": "string"
         }
      },
      "usage": {
         "cacheDetails": [
            {
               "inputTokens": number,
               "ttl": "string"
            }
         ],
         "cacheReadInputTokens": number,
         "cacheWriteInputTokens": number,
         "inputTokens": number,
         "outputTokens": number,
         "totalTokens": number
      }
   },
   "modelStreamErrorException": {
   },
   "serviceUnavailableException": {
   },
   "throttlingException": {
   },
   "validationException": {
   }
}
```

## Response Elements

If the action is successful, the service sends back an HTTP 200 response.

The following data is returned in JSON format by the service.

 ** [contentBlockDelta](#API_runtime_ConverseStream_ResponseSyntax) **
The messages output content block delta.
Type: [ContentBlockDeltaEvent](API_runtime_ContentBlockDeltaEvent.md) object

 ** [contentBlockStart](#API_runtime_ConverseStream_ResponseSyntax) **
Start information for a content block.
Type: [ContentBlockStartEvent](API_runtime_ContentBlockStartEvent.md) object

 ** [contentBlockStop](#API_runtime_ConverseStream_ResponseSyntax) **
Stop information for a content block.
Type: [ContentBlockStopEvent](API_runtime_ContentBlockStopEvent.md) object

 ** [internalServerException](#API_runtime_ConverseStream_ResponseSyntax) **
An internal server error occurred. Retry your request.
Type: Exception
HTTP Status Code: 500

 ** [messageStart](#API_runtime_ConverseStream_ResponseSyntax) **
Message start information.
Type: [MessageStartEvent](API_runtime_MessageStartEvent.md) object

 ** [messageStop](#API_runtime_ConverseStream_ResponseSyntax) **
Message stop information.
Type: [MessageStopEvent](API_runtime_MessageStopEvent.md) object

 ** [metadata](#API_runtime_ConverseStream_ResponseSyntax) **
Metadata for the converse output stream.
Type: [ConverseStreamMetadataEvent](API_runtime_ConverseStreamMetadataEvent.md) object

 ** [modelStreamErrorException](#API_runtime_ConverseStream_ResponseSyntax) **
A streaming error occurred. Retry your request.
Type: Exception
HTTP Status Code: 424

 ** [serviceUnavailableException](#API_runtime_ConverseStream_ResponseSyntax) **
The service isn't currently available. For troubleshooting this error, see [ServiceUnavailable](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-service-unavailable) in the Amazon Bedrock User Guide
Type: Exception
HTTP Status Code: 503

 ** [throttlingException](#API_runtime_ConverseStream_ResponseSyntax) **
Your request was denied due to exceeding the account quotas for *Amazon Bedrock*. For troubleshooting this error, see [ThrottlingException](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-throttling-exception) in the Amazon Bedrock User Guide.
Type: Exception
HTTP Status Code: 429

 ** [validationException](#API_runtime_ConverseStream_ResponseSyntax) **
The input fails to satisfy the constraints specified by *Amazon Bedrock*. For troubleshooting this error, see [ValidationError](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html#ts-validation-error) in the Amazon Bedrock User Guide.
Type: Exception
HTTP Status Code: 400

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

### Send a message to a model and stream the response.

Send a message to Anthropic Claude Sonnet with `ConverseStream` and stream the response.

#### Sample Request

```
POST /model/anthropic.claude-3-sonnet-20240229-v1:0/converse-stream HTTP/1.1
{
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "text": "Write an article about impact of high inflation to GDP of a country"
                }
            ]
        }
    ],
    "system": [{"text" : "You are an economist with access to lots of data"}],
    "inferenceConfig": {
        "maxTokens": 1000,
        "temperature": 0.5
    }
}
```

## See Also

For more information about using this API in one of the language-specific AWS SDKs, see the following:
+  [AWS Command Line Interface V2](https://docs.aws.amazon.com/goto/cli2/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for .NET V4](https://docs.aws.amazon.com/goto/DotNetSDKV4/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for C\+\+](https://docs.aws.amazon.com/goto/SdkForCpp/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for Go v2](https://docs.aws.amazon.com/goto/SdkForGoV2/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for Java V2](https://docs.aws.amazon.com/goto/SdkForJavaV2/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for JavaScript V3](https://docs.aws.amazon.com/goto/SdkForJavaScriptV3/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for Kotlin](https://docs.aws.amazon.com/goto/SdkForKotlin/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for PHP V3](https://docs.aws.amazon.com/goto/SdkForPHPV3/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for Python](https://docs.aws.amazon.com/goto/boto3/bedrock-runtime-2023-09-30/ConverseStream)
+  [AWS SDK for Ruby V3](https://docs.aws.amazon.com/goto/SdkForRubyV3/bedrock-runtime-2023-09-30/ConverseStream)
