# Troubleshoot Signature Version 4 signing for AWS API requests

**Important**
Unless you are using the AWS SDKs or CLI, you must write code to calculate signatures that provide authentication information in your requests. SigV4 signature calculation can be a complex undertaking, and we recommend that you use the AWS SDKs or CLI whenever possible.

When you develop code that creates a signed request, you might receive HTTP 403 `SignatureDoesNotMatch` from AWS services. These errors mean that the signature value in your HTTP request to AWS did not match the signature that the AWS service calculated. HTTP 401 `Unauthorized` errors return when permissions do not allow the caller to make the request.

API requests might return an error if:
+ The API request isn't signed and the API request uses IAM authentication.
+ The IAM credentials used to sign the request are incorrect or don't have permissions to invoke the API.
+ The signature of the signed API request doesn't match the signature that the AWS service calculated.
+ The API request header is incorrect.

**Note**
Update your signing protocol from AWS Signature version 2 (SigV2) to AWS Signature version 4 (SigV4) before exploring other error solutions. Services, such as Amazon S3, and Regions no longer support SigV2 signing.

**Topics**
+ [Credential errors](#signature-v4-troubleshooting-credential)
+ [Canonical request and signing string errors](#signature-v4-troubleshooting-canonical-errors)
+ [Credential scope errors](#signature-v4-troubleshooting-credential-scope)
+ [Key signing errors](#signature-v4-troubleshooting-key-signing)

## Credential errors

Make sure that the API request is signed with SigV4. If the API request isn't signed, then you might receive the error: `Missing Authentication Token`. [Add the missing signature](https://docs.aws.amazon.com/IAM/latest/UserGuide/create-signed-request.html#add-signature-to-request) and resend the request.

Verify that the authentication credentials for the access key and secret key are correct. If the access key is incorrect, then you might receive the error: `Unauthorized`. Make sure the entity used to sign the request is authorized to make the request. For details, see [Troubleshoot access denied error messages](troubleshoot_access-denied.md).

## Canonical request and signing string errors

If you incorrectly calculated the canonical request in [Create a hash of the canonical request](reference_sigv-create-signed-request.md#create-canonical-request-hash) or [Create a string to sign](reference_sigv-create-signed-request.md#create-string-to-sign), the signature verification step performed by the service fails with the error message:

```
The request signature we calculated does not match the signature you provided
```

When the AWS service receives a signed request, it recalculates the signature. If there are differences in the values, then the signatures don’t match. Compare the canonical request and string to your signed request with the value in the error message. Modify the signing process if there are any differences.

**Note**
You can also verify that you didn't send the request through a proxy that modifies the headers or the request.

**Example canonical request**

```
GET                                                      -------- HTTP method
/                                                        -------- Path. For API stage endpoint, it should be /{stage-name}/{resource-path}
                                                         -------- Query string key-value pair. Leave it blank if the request doesn't have a query string.
content-type:application/json                            -------- Header key-value pair. One header per line.
host:0123456789.execute-api.us-east-1.amazonaws.com      -------- Host and x-amz-date are required headers for all signed requests.
x-amz-date:20220806T024003Z

content-type;host;x-amz-date                             -------- A list of signed headers
d167e99c53f15b0c105101d468ae35a3dc9187839ca081095e340f3649a04501        -------- Hash of the payload
```

To verify that the secret key matches the access key ID, you can test them with a known working implementation. For example, use an AWS SDK or the AWS CLI to make a request to AWS.

### API request header

When the authorization header is empty, the credential key or signature is missing or incorrect, the header doesn’t start with an algorithm name, or the key value pairs don’t include an equal sign, you receive one of the following errors:
+ Authorization header cannot be empty.
+ Authorization header requires 'Credential' parameter.
+ Authorization header requires 'Signature' parameter.
+ The signature contains an invalid key=value pair (missing equal-sign) in Authorization header.

Make sure that the SigV4 authorization header you added in [Calculate the signature](reference_sigv-create-signed-request.md#calculate-signature) includes the correct credential key, and also includes the request date using either HTTP Date or the `x-amz-date` header.

If you received an IncompleteSignatureException error and the construction of the signature is correct, you can verify that the authorization header was not modified in transit to the AWS service by computing a SHA-256 hash and B64 encoding of the authorization header in your client-side request.

1. Get the [authorization header](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv-authentication-methods.html) you sent in the request. Your authorization header appears similar to the following example:

   ```
   Authorization: AWS4-HMAC-SHA256
   Credential=AKIAIOSFODNN7EXAMPLE/20130524/us-east-1/s3/aws4_request,
   SignedHeaders=host;range;x-amz-date,
   Signature=example-generated-signature
   ```

1. Compute a SHA-256 hash of the authorization header.

   ```
   hashSHA256(rawAuthorizationHeader) = hashedAuthorizationHeader
   ```

1. Encode the hashed authorization header to Base64 format.

   ```
   base64(hashedAuthorizationHeader) = encodedHashedAuthorizationHeader
   ```

1. Compare the hashed and encoded string you just calculated against the string you received in your error message. Your error message should be similar to the following example:

   ```
   com.amazon.coral.service#IncompleteSignatureException:
   The signature contains an in-valid key=value pair (missing equal-sign)
   in Authorization header (hashed with SHA-256 and encoded with Base64):
   '9c574f83b4b950926da4a99c2b43418b3db8d97d571b5e18dd0e4f3c3ed1ed2c'.
   ```
+ If the two hashes differ, then some part of the authorization header changed in transit. This change could be due to your network or client handlers attaching signed headers or changing the authorization header in some way.
+ If the two hashes match, the authorization header you sent in the request matches what AWS received. Review the error message you received to determine if the issue is the result of incorrect credentials or signature. These errors are covered in the other sections on this page.

## Credential scope errors

The credential scope you created in [Create a string to sign](reference_sigv-create-signed-request.md#create-string-to-sign) restricts a signature to a specific date, Region, and service. This string has the following format:

```
{{YYYYMMDD}}/{{region}}/{{service}}/aws4_request
```

**Note**
If you are using SigV4a, the Region is not included in credential scope.

**Date**
If the credential scope does not specify the same date as the x-amz-date header, the signature verification step fails with the following error message:

```
Date in Credential scope does not match YYYYMMDD from ISO-8601 version of date from HTTP
```

If the request specifies a time in the future, the signature verification step fails with the following error message:

```
Signature not yet current: {{date}} is still later than {{date}}
```

If the request has expired, the signature verification step fails with the following error message:

```
Signature expired: {{date}} is now earlier than {{date}}
```

**Region**
If the credential scope does not specify the same Region as the request, the signature verification step fails with the following error message:

```
Credential should be scoped to a valid Region, not {{region-code}}
```

**Service**
If the credential scope does not specify the same service as the host header, the signature verification step fails with the following error message:

```
Credential should be scoped to correct service: '{{service}}'
```

**Termination string**
If the credential scope does not end with aws4\_request, the signature verification step fails with the following error message:

```
Credential should be scoped with a valid terminator: 'aws4_request'
```

## Key signing errors

Errors that are caused by incorrect derivation of the signing key or improper use of cryptography are more difficult to troubleshoot. After you verify that the canonical string and the string to sign are correct, you can also check for one of the following issues:
+ The secret access key does not match the access key ID that you specified.
+ There is a problem with your key derivation code.

To verify that the secret key matches the access key ID, you can test them with a known working implementation. For example, use an AWS SDK or the AWS CLI to make a request to AWS. For examples, see [Request signature examples](reference_sigv-examples.md)
