# Process credential provider

**Note**
For help in understanding the layout of settings pages, or in interpreting the **Support by AWS SDKs and tools** table that follows, see [Understanding the settings pages of this guide](settings-reference.md#settingsPages).

SDKs provide a way to extend the credential provider chain for custom use cases. This provider can be used to provide custom implementations, such as retrieving credentials from an on-premises credentials store or integrating with your on-premises identify provider.

 For example, IAM Roles Anywhere uses `credential_process` to get temporary credentials on behalf of your application. To configure `credential_process` for this use, see [Using IAM Roles Anywhere to authenticate AWS SDKs and tools](access-rolesanywhere.md).

**Important**
The `credential_process` setting runs an external program on your system to retrieve credentials. Ensure that you trust the program specified in this setting, because anyone with write access to your shared `config` file can change the command that is run. Protect your `config` file with filesystem permissions appropriate for your operating system.

**Note**
The following describes a method of sourcing credentials from an external process and might be used if you are running software outside of AWS. If you are building on an AWS compute resource, use other credential providers. If using this option, you should make sure that the config file is as locked down as possible using security best practices for your operating system. Confirm that your custom credential tool does not write any secret information to `StdErr`, because the SDKs and AWS CLI can capture and log such information, potentially exposing it to unauthorized users.

Configure this functionality by using the following:

**`credential_process` - shared AWS `config` file setting**
Specifies an external command that the SDK or tool runs on your behalf to generate or retrieve authentication credentials to use. The setting specifies the name of a program/command that the SDK will invoke. When the SDK invokes the process, it waits for the process to write JSON data to `stdout`. The custom provider must return information in a specific format. That information contains the credentials that the SDK or tool can use to authenticate you.

**Note**
The process credential provider is a part of the [Understand the credential provider chain](standardized-credentials.md#credentialProviderChain). However, the process credential provider is only checked after several other providers that are in this series. Therefore, if you want your program use this provider's credentials, you must remove other valid credential providers from your configuration or use a different profile. Alternatively, instead of relying on the credential provider chain to automatically discover which provider returns valid credentials, specify the use of the process credential provider in code. You can specify credential sources directly when you create service clients.

## Specifying the path to the credentials program

The setting's value is a string that contains a path to a program that the SDK or development tool runs on your behalf:
+ The path and file name can consist of only these characters: A-Z, a-z, 0-9, hyphen ( - ), underscore ( \_ ), period ( . ), forward slash ( / ), backslash ( \\ ), and space.
+ If the path or file name contains a space, surround the complete path and file name with double-quotation marks (" ").
+ If a parameter name or a parameter value contains a space, surround that element with double-quotation marks (" "). Surround only the name or value, not the pair.
+ Don't include any environment variables in the strings. For example, don't include `$HOME` or `%USERPROFILE%`.
+ Don't specify the home folder as `~`. \* You must specify either the full path or a base file name. If there is a base file name, the system attempts to find the program within folders specified by the `PATH` environment variable. The path varies depending on the operating system:

  The following example shows setting credential\_process in the shared `config` file on Linux/macOS.

  ```
  credential_process = {{"/path/to/credentials.sh" parameterWithoutSpaces "parameter with spaces"}}
  ```

  The following example shows setting credential\_process in the shared `config` file on Windows.

  ```
  credential_process = {{"C:\Path\To\credentials.cmd" parameterWithoutSpaces "parameter with spaces"}}
  ```
+  Can be specified within a dedicated profile:

  ```
  [profile {{cred_process}}]
  credential_process = {{/Users/username/process.sh}}
  region = {{us-east-1}}
  ```

## Valid output from the credentials program

The SDK runs the command as specified in the profile and then reads data from the standard output stream. The command you specify, whether a script or binary program, must generate JSON output on `STDOUT` that matches the following syntax.

```
{
    "Version": 1,
    "AccessKeyId": "{{an AWS access key}}",
    "SecretAccessKey": "{{your AWS secret access key}}",
    "SessionToken": "{{the AWS session token for temporary credentials}}",
    "Expiration": "{{RFC3339 timestamp for when the credentials expire}}",
    "AccountId": "{{the AWS account ID associated with these credentials}}"
}
```

**Note**
As of this writing, the `Version` key must be set to `1`. This might increment over time as the structure evolves.

The `Expiration` key is an RFC3339 formatted timestamp. If the `Expiration` key isn't present in the tool's output, the SDK assumes that the credentials are long-term credentials that don't refresh. Otherwise, the credentials are considered temporary credentials, and they are automatically refreshed by rerunning the `credential_process` command before the credentials expire.

**Note**
The SDK does ***not*** cache external process credentials the way it does assume-role credentials. If caching is required, you must implement it in the external process.

**Note**
 `AccountId` is optional so credentials work without it, but providing it enables optimized endpoint resolution for services that support it. When the SDK knows which account the credentials belong to, certain AWS services can use account-specific endpoints. For example Amazon S3 can route requests to an account-scoped endpoint rather than the global endpoint. Without `AccountId`, the SDK must rely on other mechanisms to determine the account, or it cannot use account-based endpoint routing.

The external process can return a non-zero return code to indicate that an error occurred while retrieving the credentials.

## Support by AWS SDKs and tools

The following SDKs support the features and settings described in this topic. Any partial exceptions are noted. Any JVM system property settings are supported by the AWS SDK for Java and the AWS SDK for Kotlin only.

| SDK | Supported | Notes or more information |
| --- | --- | --- |
| [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/) | Yes |  |
| [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/) | Yes |  |
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
| [Tools for PowerShell V4](https://docs.aws.amazon.com/powershell/v4/userguide/) | Yes |  |
