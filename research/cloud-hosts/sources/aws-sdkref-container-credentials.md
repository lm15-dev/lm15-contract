# Container credential provider

**Note**
For help in understanding the layout of settings pages, or in interpreting the **Support by AWS SDKs and tools** table that follows, see [Understanding the settings pages of this guide](settings-reference.md#settingsPages).

The container credential provider fetches credentials for customer's containerized application. This credential provider is useful for Amazon Elastic Container Service (Amazon ECS) and Amazon Elastic Kubernetes Service (Amazon EKS) customers. SDKs attempt to load credentials from the specified HTTP endpoint through a GET request.

If you use Amazon ECS, we recommend you use a task IAM Role for improved credential isolation, authorization, and auditability. When configured, Amazon ECS sets the `AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` environment variable that the SDKs and tools use to obtain credentials. To configure Amazon ECS for this functionality, see [Task IAM role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html) in the *Amazon Elastic Container Service Developer Guide*.

If you use Amazon EKS, we recommend you use Amazon EKS Pod Identity for improved credential isolation, least privilege, auditability, independent operation, reusability, and scalability. Both your Pod and an IAM role are associated with a Kubernetes service account to manage credentials for your applications. To learn more on Amazon EKS Pod Identity, see [Amazon EKS Pod Identities](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html) in the **Amazon EKS User Guide**. When configured, Amazon EKS sets the `AWS_CONTAINER_CREDENTIALS_FULL_URI` and `AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE` environment variables that the SDKs and tools use to obtain credentials. For setup information, see [Setting up the Amazon EKS Pod Identity Agent](https://docs.aws.amazon.com/eks/latest/userguide/pod-id-agent-setup.html) in the **Amazon EKS User Guide** or [Amazon EKS Pod Identity simplifies IAM permissions for applications on Amazon EKS clusters](https://aws.amazon.com/blogs/aws/amazon-eks-pod-identity-simplifies-iam-permissions-for-applications-on-amazon-eks-clusters/) at the AWS Blog website.

Configure this functionality by using the following:

**`AWS_CONTAINER_CREDENTIALS_FULL_URI` - environment variable**
Specifies the full HTTP URL endpoint for the SDK to use when making a request for credentials. This includes both the scheme and the host.
**Default value:** None.
**Valid values:** Valid URI.
*Note: This setting is an alternative to `AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` and will only be used if `AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` is not set. *
Linux/macOS example of setting environment variables via command line:

```
export AWS_CONTAINER_CREDENTIALS_FULL_URI={{http://localhost/get-credentials}}
```
or

```
export AWS_CONTAINER_CREDENTIALS_FULL_URI={{http://localhost:8080/get-credentials}}
```

**`AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` - environment variable**
Specifies the relative HTTP URL endpoint for the SDK to use when making a request for credentials. The value is appended to the default Amazon ECS hostname of `169.254.170.2`.
**Default value:** None.
**Valid values:** Valid relative URI.
Linux/macOS example of setting environment variables via command line:

```
export AWS_CONTAINER_CREDENTIALS_RELATIVE_URI={{/get-credentials?a=1}}
```

**`AWS_CONTAINER_AUTHORIZATION_TOKEN` - environment variable**
Specifies an authorization token in plain text. If this variable is set, the SDK will set the Authorization header on the HTTP request with the environment variable's value.
**Default value:** None.
**Valid values:** String.
*Note: This setting is an alternative to `AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE` and will only be used if `AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE` is not set. *
Linux/macOS example of setting environment variables via command line:

```
export AWS_CONTAINER_CREDENTIALS_FULL_URI={{http://localhost/get-credential}}
export AWS_CONTAINER_AUTHORIZATION_TOKEN={{Basic abcd}}
```

**`AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE` - environment variable**
Specifies an absolute file path to a file that contains the authorization token in plain text.
**Default value:** None.
**Valid values:** String.
Linux/macOS example of setting environment variables via command line:

```
export AWS_CONTAINER_CREDENTIALS_FULL_URI={{http://localhost/get-credential}}
export AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE={{/path/to/token}}
```

## Support by AWS SDKs and tools

The following SDKs support the features and settings described in this topic. Any partial exceptions are noted. Any JVM system property settings are supported by the AWS SDK for Java and the AWS SDK for Kotlin only.

| SDK | Supported | Notes or more information |
| --- | --- | --- |
| [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/) | Yes |  |
| [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/) | Yes |  |
| [SDK for Go V2 (1.x)](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/) | Yes |  |
| [SDK for Go 1.x (V1)](https://docs.aws.amazon.com/sdk-for-go/latest/developer-guide/) | Yes |  |
| [SDK for Java 2.x](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/) | Yes | When [Lambda SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html#snapstart-runtimes) is activated, AWS\_CONTAINER\_CREDENTIALS\_FULL\_URI and AWS\_CONTAINER\_AUTHORIZATION\_TOKEN are automatically used for authentication. |
| [SDK for Java 1.x](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/) | Yes | When [Lambda SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html#snapstart-runtimes) is activated, AWS\_CONTAINER\_CREDENTIALS\_FULL\_URI and AWS\_CONTAINER\_AUTHORIZATION\_TOKEN are automatically used for authentication. |
| [SDK for JavaScript 3.x](https://docs.aws.amazon.com/sdk-for-javascript/latest/developer-guide/) | Yes |  |
| [SDK for JavaScript 2.x](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/) | Yes |  |
| [SDK for Kotlin](https://docs.aws.amazon.com/sdk-for-kotlin/latest/developer-guide/) | Yes |  |
| [SDK for .NET 4.x](https://docs.aws.amazon.com/sdk-for-net/latest/developer-guide/) | Yes | When [Lambda SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html#snapstart-runtimes) is activated, AWS\_CONTAINER\_CREDENTIALS\_FULL\_URI and AWS\_CONTAINER\_AUTHORIZATION\_TOKEN are automatically used for authentication. |
| [SDK for .NET 3.x](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/) | Yes | When [Lambda SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html#snapstart-runtimes) is activated, AWS\_CONTAINER\_CREDENTIALS\_FULL\_URI and AWS\_CONTAINER\_AUTHORIZATION\_TOKEN are automatically used for authentication. |
| [SDK for PHP 3.x](https://docs.aws.amazon.com/sdk-for-php/latest/developer-guide/) | Yes |  |
| [SDK for Python (Boto3)](https://docs.aws.amazon.com/boto3/latest/) | Yes | When [Lambda SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html#snapstart-runtimes) is activated, AWS\_CONTAINER\_CREDENTIALS\_FULL\_URI and AWS\_CONTAINER\_AUTHORIZATION\_TOKEN are automatically used for authentication. |
| [SDK for Ruby 3.x](https://docs.aws.amazon.com/sdk-for-ruby/latest/developer-guide/) | Yes |  |
| [SDK for Rust](https://docs.aws.amazon.com/sdk-for-rust/latest/dg/) | Yes |  |
| [SDK for Swift](https://docs.aws.amazon.com/sdk-for-swift/latest/developer-guide/) | Yes |  |
| [Tools for PowerShell V5](https://docs.aws.amazon.com/powershell/latest/userguide/) | Yes |  |
| [Tools for PowerShell V4](https://docs.aws.amazon.com/powershell/v4/userguide/) | Yes |  |
