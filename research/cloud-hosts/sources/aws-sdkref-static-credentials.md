# AWS access keys

**Warning**
To avoid security risks, don't use IAM users for authentication when developing purpose-built software or working with real data. Instead, use federation with an identity provider such as [AWS IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html).

 AWS access keys for an IAM user can be used as your AWS credentials. The AWS SDK automatically uses these AWS credentials to sign API requests to AWS, so that your workloads can access your AWS resources and data securely and conveniently. It is recommended to always use the `aws_session_token` so that the credentials are temporary and no longer valid after they expire. Using long-term credentials is not recommended.

**Note**
If AWS becomes unable to refresh these temporary credentials, AWS may extend the validity of the credentials so that your workloads are not impacted.

 The shared AWS `credentials` file is the recommended location for storing credentials information because it is safely outside of application source directories and separate from the SDK-specific settings of the shared `config` file.

To learn more about AWS credentials and using access keys, see [AWS security credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html) and [Managing access keys for IAM users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) in the *IAM User Guide*.

Configure this functionality by using the following:

**`aws_access_key_id` - shared AWS `config` file setting`aws_access_key_id` - shared AWS `credentials` file setting *(recommended method)*`AWS_ACCESS_KEY_ID` - environment variable`aws.accessKeyId` - JVM system property: Java/Kotlin only**
Specifies the AWS access key used as part of the credentials to authenticate the user.

**`aws_secret_access_key` - shared AWS `config` file setting`aws_secret_access_key` - shared AWS `credentials` file setting *(recommended method)*`AWS_SECRET_ACCESS_KEY` - environment variable`aws.secretAccessKey` - JVM system property: Java/Kotlin only**
Specifies the AWS secret key used as part of the credentials to authenticate the user.

**`aws_session_token` - shared AWS `config` file setting`aws_session_token` - shared AWS `credentials` file setting *(recommended method)*`AWS_SESSION_TOKEN` - environment variable`aws.sessionToken` - JVM system property: Java/Kotlin only**
Specifies an AWS session token used as part of the credentials to authenticate the user. You receive this value as part of the temporary credentials returned by successful requests to assume a role. A session token is required only if you manually specify temporary security credentials. However, we recommend you always use temporary security credentials instead of long-term credentials. For security recommendations, see [Security best practices in IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html).

For instructions on how to obtain these values, see [Using short-term credentials to authenticate AWS SDKs and tools](access-temp-idc.md).

Example of setting these required values in the `config` or `credentials` file:

```
[default]
aws_access_key_id = {{AKIAIOSFODNN7EXAMPLE}}
aws_secret_access_key = {{wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY}}
aws_session_token = {{AQoEXAMPLEH4aoAH0gNCAPy...truncated...zrkuWJOgQs8IZZaIv2BXIa2R4Olgk}}
```

Linux/macOS example of setting environment variables via command line:

```
export AWS_ACCESS_KEY_ID={{AKIAIOSFODNN7EXAMPLE}}
export AWS_SECRET_ACCESS_KEY={{wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY}}
export AWS_SESSION_TOKEN={{AQoEXAMPLEH4aoAH0gNCAPy...truncated...zrkuWJOgQs8IZZaIv2BXIa2R4Olgk}}
```

Windows example of setting environment variables via command line:

```
setx AWS_ACCESS_KEY_ID {{AKIAIOSFODNN7EXAMPLE}}
setx AWS_SECRET_ACCESS_KEY {{wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY}}
setx AWS_SESSION_TOKEN {{AQoEXAMPLEH4aoAH0gNCAPy...truncated...zrkuWJOgQs8IZZaIv2BXIa2R4Olgk}}
```

## Support by AWS SDKs and tools

The following SDKs support the features and settings described in this topic. Any partial exceptions are noted. Any JVM system property settings are supported by the AWS SDK for Java and the AWS SDK for Kotlin only.

| SDK | Supported | Notes or more information |
| --- | --- | --- |
| [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/) | Yes |  |
| [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/) | Yes | shared config file not supported. |
| [SDK for Go V2 (1.x)](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/) | Yes |  |
| [SDK for Go 1.x (V1)](https://docs.aws.amazon.com/sdk-for-go/latest/developer-guide/) | Yes | To use shared config file settings, you must turn on loading from the config file; see [Sessions](https://docs.aws.amazon.com/sdk-for-go/api/aws/session/). |
| [SDK for Java 2.x](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/) | Yes |  |
| [SDK for Java 1.x](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/) | Yes |  |
| [SDK for JavaScript 3.x](https://docs.aws.amazon.com/sdk-for-javascript/latest/developer-guide/) | Yes |  |
| [SDK for JavaScript 2.x](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/) | Yes |  |
| [SDK for Kotlin](https://docs.aws.amazon.com/sdk-for-kotlin/latest/developer-guide/) | Yes |  |
| [SDK for .NET 4.x](https://docs.aws.amazon.com/sdk-for-net/latest/developer-guide/) | Yes |  |
| [SDK for .NET 3.x](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/) | Yes |  |
| [SDK for PHP 3.x](https://docs.aws.amazon.com/sdk-for-php/latest/developer-guide/) | Yes |  |
| [SDK for Python (Boto3)](https://docs.aws.amazon.com/boto3/latest/) | Yes |  |
| [SDK for Ruby 3.x](https://docs.aws.amazon.com/sdk-for-ruby/latest/developer-guide/) | Yes |  |
| [SDK for Rust](https://docs.aws.amazon.com/sdk-for-rust/latest/dg/) | Yes |  |
| [SDK for Swift](https://docs.aws.amazon.com/sdk-for-swift/latest/developer-guide/) | Yes |  |
| [Tools for PowerShell V5](https://docs.aws.amazon.com/powershell/latest/userguide/) | Yes |  |
| [Tools for PowerShell V4](https://docs.aws.amazon.com/powershell/v4/userguide/) | Yes | Environment variables not supported. |
