# ListFoundationModels

Lists Amazon Bedrock foundation models that you can use. You can filter the results with the request parameters. For more information, see [Foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/foundation-models.html) in the [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-service.html).

## Request Syntax

```
GET /foundation-models?byCustomizationType={{byCustomizationType}}&byInferenceType={{byInferenceType}}&byOutputModality={{byOutputModality}}&byProvider={{byProvider}} HTTP/1.1
```

## URI Request Parameters

The request uses the following URI parameters.

 ** [byCustomizationType](#API_ListFoundationModels_RequestSyntax) **
Return models that support the customization type that you specify. For more information, see [Custom models](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html) in the [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-service.html).
Valid Values: `FINE_TUNING | CONTINUED_PRE_TRAINING | DISTILLATION`

 ** [byInferenceType](#API_ListFoundationModels_RequestSyntax) **
Return models that support the inference type that you specify. For more information, see [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) in the [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-service.html).
Valid Values: `ON_DEMAND | PROVISIONED`

 ** [byOutputModality](#API_ListFoundationModels_RequestSyntax) **
Return models that support the output modality that you specify.
Valid Values: `TEXT | IMAGE | EMBEDDING`

 ** [byProvider](#API_ListFoundationModels_RequestSyntax) **
Return models belonging to the model provider that you specify.
Pattern: `[A-Za-z0-9- ]{1,63}`

## Request Body

The request does not have a request body.

## Response Syntax

```
HTTP/1.1 200
Content-type: application/json

{
   "modelSummaries": [
      {
         "customizationsSupported": [ "string" ],
         "inferenceTypesSupported": [ "string" ],
         "inputModalities": [ "string" ],
         "modelArn": "string",
         "modelId": "string",
         "modelLifecycle": {
            "endOfLifeTime": "string",
            "legacyTime": "string",
            "publicExtendedAccessTime": "string",
            "startOfLifeTime": "string",
            "status": "string"
         },
         "modelName": "string",
         "outputModalities": [ "string" ],
         "providerName": "string",
         "responseStreamingSupported": boolean
      }
   ]
}
```

## Response Elements

If the action is successful, the service sends back an HTTP 200 response.

The following data is returned in JSON format by the service.

 ** [modelSummaries](#API_ListFoundationModels_ResponseSyntax) **
A list of Amazon Bedrock foundation models.
Type: Array of [FoundationModelSummary](API_FoundationModelSummary.md) objects

## Errors

For information about the errors that are common to all actions, see [Common Error Types](CommonErrors.md).

 ** AccessDeniedException **
The request is denied because of missing access permissions.
HTTP Status Code: 403

 ** InternalServerException **
An internal server error occurred. Retry your request.
HTTP Status Code: 500

 ** ThrottlingException **
The number of requests exceeds the limit. Resubmit your request later.
HTTP Status Code: 429

 ** ValidationException **
Input validation failed. Check your request parameters and retry the request.
HTTP Status Code: 400

## See Also

For more information about using this API in one of the language-specific AWS SDKs, see the following:
+  [AWS Command Line Interface V2](https://docs.aws.amazon.com/goto/cli2/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for .NET V4](https://docs.aws.amazon.com/goto/DotNetSDKV4/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for C\+\+](https://docs.aws.amazon.com/goto/SdkForCpp/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for Go v2](https://docs.aws.amazon.com/goto/SdkForGoV2/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for Java V2](https://docs.aws.amazon.com/goto/SdkForJavaV2/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for JavaScript V3](https://docs.aws.amazon.com/goto/SdkForJavaScriptV3/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for Kotlin](https://docs.aws.amazon.com/goto/SdkForKotlin/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for PHP V3](https://docs.aws.amazon.com/goto/SdkForPHPV3/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for Python](https://docs.aws.amazon.com/goto/boto3/bedrock-2023-04-20/ListFoundationModels)
+  [AWS SDK for Ruby V3](https://docs.aws.amazon.com/goto/SdkForRubyV3/bedrock-2023-04-20/ListFoundationModels)
