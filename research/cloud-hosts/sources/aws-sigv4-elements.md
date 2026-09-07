# AWS Signature Version 4 for API requests

**Important**
If you use an AWS SDK (see [Sample Code and Libraries](https://aws.amazon.com/developer/)) or AWS Command Line Interface (AWS CLI) tool to send API requests to AWS, you can skip the signature process, as the SDK and CLI clients authenticate your requests by using the access keys that you provide. Unless you have a good reason not to, we recommend that you always use an SDK or the CLI.
In Regions that support multiple signature versions, manually signing requests means you must specify which signature version to use. When you supply requests to Multi-Region Access Points, SDKs and the CLI automatically switch to using Signature Version 4A without additional configuration.

Authentication information that you send in a request must include a signature. AWS Signature Version 4 (SigV4) is the AWS signing protocol for adding authentication information to AWS API requests.

You don't use your secret access key to sign API requests. Instead, you use the SigV4 signing process. Signing requests involves:

1. Creating a canonical request based on the request details.

1. Calculating a signature using your AWS credentials.

1. Adding this signature to the request as an Authorization header.

AWS then replicates this process and verifies the signature, granting or denying access accordingly.

Symmetric SigV4 requires you to derive a key that is scoped to a single AWS service, in a single AWS region, on a particular day. This makes the key and calculated signature different for each region, meaning you must know the region the signature is destined for.

Asymmetric Signature Version 4 (SigV4a) is an extension that supports signing with a new algorithm, and generating individual signatures that are verifiable in more than one AWS region. With SigV4a, you can sign a request for multiple regions, with seamless routing and failover between regions. When you use the AWS SDK or AWS CLI to invoke functionality that requires multi-region signing, the signature type is automatically changed to use SigV4a. For details, see [How AWS SigV4a works](#how-sigv4a-works).

## How AWS SigV4 works

The following steps describe the general process of computing a signature with SigV4:

1. The **string to sign** depends on the request type. For example, when you use the HTTP Authorization header or the query parameters for authentication, you use a combination of request elements to create the string to sign. For an HTTP POST request, the `POST` policy in the request is the string you sign.

1. The **signing key** is a series of calculations, with the result of each step fed into the next. The final step is the signing key.

1. When an AWS service receives an authenticated request, it recreates the **signature** using the authentication information contained in the request. If the signatures match, the service processes the request. Otherwise, it rejects the request.

For more information, see [Elements of an AWS API request signature](reference_sigv-signing-elements.md).

## How AWS SigV4a works

SigV4a uses asymmetric signatures based on public-private key cryptography. SigV4a goes through a similar scoped credentials derivation process as SigV4, except SigV4a uses the same key to sign all requests without needing to derive a distinct signing key based on the date, service, and region. An [Elliptic Curve Digital Signature Algorithm](https://csrc.nist.gov/glossary/term/ecdsa) (ECDSA) keypair can be derived from your existing AWS secret access key.

The system uses asymmetric cryptography to verify multi-region signatures, so that AWS only needs to store your public keys. Public keys are not secret and can't be used to sign requests. Asymmetric signatures are required for multi-region API requests, such as with Amazon S3 Multi-Region Access Points.

The following steps describe the general process of computing a signature with SigV4a:

1. The **string to sign** depends on the request type. For example, when you use the HTTP Authorization header or the query parameters for authentication, you use a combination of request elements to create the string to sign. For an HTTP POST request, the `POST` policy in the request is the string you sign.

1. The **signing key** is derived from an AWS secret access key through a series of calculations, with the result of each step fed into the next. The final step produces the keypair.

1. When an AWS service receives a request signed with SigV4a, AWS verifies the signature using only the public half of the keypair. If the signature is valid, the request is authenticated and the service processes the request. Requests with invalid signatures are rejected.

For more information about SigV4a for multi-Region API requests, see the [sigv4a-signing-examples](https://github.com/aws-samples/sigv4a-signing-examples) project on GitHub.

## When to sign requests

When you write custom code that sends API requests to AWS, you must include code that signs the requests. You might write custom code because:
+ You are working with a programming language for which there is no AWS SDK.
+ You need complete control over how requests are sent to AWS.

While API requests authenticate access with AWS SigV4, AWS SDKs and the AWS CLI authenticate your requests by using the access keys that you provide. For more information about authenticating with AWS SDKs and the AWS CLI, see [Additional resources](#reference_aws-signing-resources).

## Why requests are signed

The signing process helps secure requests in the following ways:
+ **Verify the identity of the requester**

  Authenticated requests require a signature that you create by using your access keys (access key ID, secret access key). If you are using temporary security credentials, the signature calculations also require a security token. For more information, see [AWS security credentials programmatic access](security-creds-programmatic-access.md).
+ **Protect data in transit**

  To prevent tampering with a request while it's in transit, some of the request elements are used to calculate a hash (digest) of the request, and the resulting hash value is included as part of the request. When an AWS service receives the request, it uses the same information to calculate a hash and matches it against the hash value in your request. If the values don't match, AWS denies the request.
+ **Protect against potential replay attacks**

  In most cases, a request must reach AWS within five minutes of the time stamp in the request. Otherwise, AWS denies the request.

AWS SigV4 can be expressed in the HTTP Authorization header or as a query string in the URL. For more information, see [Authentication methods](reference_sigv-authentication-methods.md).

## Additional resources

+ For more information about the SigV4 signing process for different services, see [Request signature examples](reference_sigv-examples.md).
+ To configure credentials for programmatic access for the AWS CLI, see [Authentication and access credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html) in the *AWS Command Line Interface User Guide*.
+ The AWS SDKs include source code on GitHub for signing AWS API requests. For code samples, see [Example projects in AWS samples repository](reference_sigv-examples.md#signature-v4-examples-sdk).
  + AWS SDK for .NET – [AWSSigV4Signer.cs](https://github.com/aws/aws-sdk-net/blob/main/sdk/src/Core/Amazon.Runtime/Signing/AWSSigV4Signer.cs)
  + AWS SDK for C\+\+ – [AWSAuthV4Signer.cpp](https://github.com/aws/aws-sdk-cpp/blob/main/src/aws-cpp-sdk-core/source/auth/signer/AWSAuthV4Signer.cpp)
  + AWS SDK for Go – [sigv4.go](https://github.com/aws/smithy-go/blob/a4c9efcda6aa54c75d1a130d1320a2709eebf51d/aws-http-auth/sigv4/sigv4.go)
  + AWS SDK for Java – [BaseAws4Signer.java](https://github.com/aws/aws-sdk-java-v2/blob/master/core/auth/src/main/java/software/amazon/awssdk/auth/signer/internal/BaseAws4Signer.java)
  + AWS SDK for JavaScript – [signature-v4](https://github.com/smithy-lang/smithy-typescript/tree/main/packages/signature-v4)
  + AWS SDK for PHP – [SignatureV4.php](https://github.com/aws/aws-sdk-php/blob/master/src/Signature/SignatureV4.php)
  + AWS SDK for Python (Boto) – [signers.py](https://github.com/boto/botocore/blob/develop/botocore/signers.py)
  + AWS SDK for Ruby – [signer.rb](https://github.com/aws/aws-sdk-ruby/blob/version-3/gems/aws-sigv4/lib/aws-sigv4/signer.rb)
+ If you encounter errors when signing requests, see [Troubleshoot Signature Version 4 signing for AWS API requests](reference_sigv-troubleshooting.md).
