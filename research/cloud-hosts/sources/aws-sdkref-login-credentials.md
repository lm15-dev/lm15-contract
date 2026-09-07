# Login credentials provider

You can [use your existing AWS Management Console sign-in credentials](https://docs.amazon.aws.com/sdkref/latest/guide/access-login.html) to acquire short-term credentials that can be used for programmatic access. After you complete the browser-based authentication flow, AWS generates temporary credentials that work across local development tools like the AWS CLI, AWS Tools for PowerShell and AWS SDKs.

To generate these credentials, run the `aws login` command in the AWS CLI, or the `Invoke-AWSLogin` cmdlet in AWS Tools for PowerShell. The resulting short-term credentials will be cached locally, where they can be reused by the AWS SDKs. The short-term credentials expire in 15 minutes, but the CLI and SDKs will automatically refresh them as needed up to 12 hours. When the refresh token expires, you'll be prompted to log in again via the CLI or PowerShell.

The login command will update the profile you specify with the `login_session` setting, which stores the identity of the management console session that you selected during the login workflow.

```
[profile console]
login_session = arn:aws:iam::0123456789012:user/username
region = us-west-2
```

By default, the short-term credentials and refresh token are stored in a JSON file in the `~/.aws/login/cache` directory on Linux and macOS, or `%USERPROFILE%\.aws\login\cache` on Windows. The filename is based on the login session name. You can override the directory by setting the `AWS_LOGIN_CACHE_DIRECTORY` environment variable.

## Login Provider Settings

Configure this functionality by using the following:

**`AWS_LOGIN_CACHE_DIRECTORY` - environment variable**
Alternative directory where the CLI and SDKs will store the cached credentials that map to a login session profile.
Default value: `~/.aws/login/cache` on Linux and macOS, or `%USERPROFILE%\.aws\login\cache` on Windows.

## Support by AWS SDKs and tools

The following SDKs support the features and settings described in this topic. Any partial exceptions are noted. Any JVM system property settings are supported by the AWS SDK for Java and the AWS SDK for Kotlin only.

| SDK | Supported | Notes or more information |
| --- | --- | --- |
| [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/) | Yes |  |
| [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/) | Yes |  |
| [SDK for Go V2 (1.x)](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/) | No |  |
| [SDK for Go 1.x (V1)](https://docs.aws.amazon.com/sdk-for-go/latest/developer-guide/) | Yes |  |
| [SDK for Java 2.x](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/) | Yes |  |
| [SDK for Java 1.x](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/) | No |  |
| [SDK for JavaScript 3.x](https://docs.aws.amazon.com/sdk-for-javascript/latest/developer-guide/) | Yes |  |
| [SDK for JavaScript 2.x](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/) | No |  |
| [SDK for Kotlin](https://docs.aws.amazon.com/sdk-for-kotlin/latest/developer-guide/) | Yes |  |
| [SDK for .NET 4.x](https://docs.aws.amazon.com/sdk-for-net/latest/developer-guide/) | Yes |  |
| [SDK for .NET 3.x](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/) | Yes |  |
| [SDK for PHP 3.x](https://docs.aws.amazon.com/sdk-for-php/latest/developer-guide/) | Yes |  |
| [SDK for Python (Boto3)](https://docs.aws.amazon.com/boto3/latest/) | Yes | Requires CRT |
| [SDK for Ruby 3.x](https://docs.aws.amazon.com/sdk-for-ruby/latest/developer-guide/) | Yes |  |
| [SDK for Rust](https://docs.aws.amazon.com/sdk-for-rust/latest/dg/) | Yes |  |
| [Tools for PowerShell V5](https://docs.aws.amazon.com/powershell/latest/userguide/) | Yes |  |
| [Tools for PowerShell V4](https://docs.aws.amazon.com/powershell/v4/userguide/) | No |  |
