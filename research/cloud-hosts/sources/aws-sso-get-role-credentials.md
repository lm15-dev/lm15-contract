# GetRoleCredentials

Returns the STS short-term credentials for a given role name that is assigned to the user.

## Request Syntax

```
GET /federation/credentials?account_id={{accountId}}&role_name={{roleName}} HTTP/1.1
x-amz-sso_bearer_token: {{accessToken}}
```

## URI Request Parameters

The request uses the following URI parameters.

 ** [accessToken](#API_GetRoleCredentials_RequestSyntax) **
The token issued by the `CreateToken` API call. For more information, see [CreateToken](https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/API_CreateToken.html) in the *IAM Identity Center OIDC API Reference Guide*.
Required: Yes

 ** [accountId](#API_GetRoleCredentials_RequestSyntax) **
The identifier for the AWS account that is assigned to the user.
Required: Yes

 ** [roleName](#API_GetRoleCredentials_RequestSyntax) **
The friendly name of the role that is assigned to the user.
Required: Yes

## Request Body

The request does not have a request body.

## Response Syntax

```
HTTP/1.1 200
Content-type: application/json

{
   "roleCredentials": {
      "accessKeyId": "string",
      "expiration": number,
      "secretAccessKey": "string",
      "sessionToken": "string"
   }
}
```

## Response Elements

If the action is successful, the service sends back an HTTP 200 response.

The following data is returned in JSON format by the service.

 ** [roleCredentials](#API_GetRoleCredentials_ResponseSyntax) **
The credentials for the role that is assigned to the user.
Type: [RoleCredentials](API_RoleCredentials.md) object

## Errors

For information about the errors that are common to all actions, see [Common Error Types](CommonErrors.md).

 ** InvalidRequestException **
Indicates that a problem occurred with the input to the request. For example, a required parameter might be missing or out of range.
HTTP Status Code: 400

 ** ResourceNotFoundException **
The specified resource doesn't exist.
HTTP Status Code: 404

 ** TooManyRequestsException **
Indicates that the request is being made too frequently and is more than what the server can handle.
HTTP Status Code: 429

 ** UnauthorizedException **
Indicates that the request is not authorized. This can happen due to an invalid access token in the request.
HTTP Status Code: 401

## See Also

For more information about using this API in one of the language-specific AWS SDKs, see the following:
+  [AWS Command Line Interface V2](https://docs.aws.amazon.com/goto/cli2/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for .NET V4](https://docs.aws.amazon.com/goto/DotNetSDKV4/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for C\+\+](https://docs.aws.amazon.com/goto/SdkForCpp/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for Go v2](https://docs.aws.amazon.com/goto/SdkForGoV2/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for Java V2](https://docs.aws.amazon.com/goto/SdkForJavaV2/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for JavaScript V3](https://docs.aws.amazon.com/goto/SdkForJavaScriptV3/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for Kotlin](https://docs.aws.amazon.com/goto/SdkForKotlin/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for PHP V3](https://docs.aws.amazon.com/goto/SdkForPHPV3/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for Python](https://docs.aws.amazon.com/goto/boto3/sso-2019-06-10/GetRoleCredentials)
+  [AWS SDK for Ruby V3](https://docs.aws.amazon.com/goto/SdkForRubyV3/sso-2019-06-10/GetRoleCredentials)
