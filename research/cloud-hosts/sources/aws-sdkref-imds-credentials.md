# IMDS credential provider

**Note**
For help in understanding the layout of settings pages, or in interpreting the **Support by AWS SDKs and tools** table that follows, see [Understanding the settings pages of this guide](settings-reference.md#settingsPages).

Instance Metadata Service (IMDS) provides data about your instance that you can use to configure or manage the running instance. For more information about the data available, see [Work with instance metadata](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html) in the *Amazon EC2 User Guide*. Amazon EC2 provides a local endpoint available to instances that can provide various bits of information to the instance. If the instance has a role attached, it can provide a set of credentials that are valid for that role. The SDKs can use that endpoint to resolve credentials as part of their [default credential provider chain](standardized-credentials.md#credentialProviderChain). Instance Metadata Service Version 2 (IMDSv2), a more secure version of IMDS that uses a session token, is used by default. If that fails due to a non-retryable condition (HTTP error codes 403, 404, 405), IMDSv1 is used as a fallback.

Configure this functionality by using the following:

**`AWS_EC2_METADATA_DISABLED` - environment variable**
Whether or not to attempt to use Amazon EC2 Instance Metadata Service (IMDS) to obtain credentials.
**Default value:** `false`.
**Valid values:**
+ **`true`** – Do not use IMDS to obtain credentials.
+ **`false`** – Use IMDS to obtain credentials.

**`ec2_metadata_v1_disabled` - shared AWS `config` file setting`AWS_EC2_METADATA_V1_DISABLED` - environment variable`aws.disableEc2MetadataV1` - JVM system property: Java/Kotlin only**
Whether or not to use Instance Metadata Service Version 1 (IMDSv1) as a fallback if IMDSv2 fails.
New SDKs don't support IMDSv1 and, thus, don't support this setting. For details, see table [Support by AWS SDKs and tools](#feature-imds-credentials-sdk-compat).
**Default value:** `false`.
**Valid values:**
+ **`true`** – Do not use IMDSv1 as a fallback.
+ **`false`** – Use IMDSv1 as a fallback.

**`ec2_metadata_service_endpoint` - shared AWS `config` file setting`AWS_EC2_METADATA_SERVICE_ENDPOINT` - environment variable`aws.ec2MetadataServiceEndpoint` - JVM system property: Java/Kotlin only**
The endpoint of IMDS. This value overrides the default location that AWS SDKs and tools will search for Amazon EC2 instance metadata.
**Default value:** If `ec2_metadata_service_endpoint_mode` equals `IPv4`, then default endpoint is `http://169.254.169.254`. If `ec2_metadata_service_endpoint_mode` equals `IPv6`, then default endpoint is `http://[fd00:ec2::254]`.
**Valid values:** Valid URI.

**`ec2_metadata_service_endpoint_mode` - shared AWS `config` file setting`AWS_EC2_METADATA_SERVICE_ENDPOINT_MODE` - environment variable`aws.ec2MetadataServiceEndpointMode` - JVM system property: Java/Kotlin only**
The endpoint mode of IMDS.
**Default value:**`IPv4`.
**Valid values:** `IPv4`, `IPv6`.

**Note**
The IMDS credential provider is a part of the [Understand the credential provider chain](standardized-credentials.md#credentialProviderChain). However, the IMDS credential provider is only checked after several other providers that are in this series. Therefore, if you want your program use this provider's credentials, you must remove other valid credential providers from your configuration or use a different profile. Alternatively, instead of relying on the credential provider chain to automatically discover which provider returns valid credentials, specify the use of the IMDS credential provider in code. You can specify credential sources directly when you create service clients.

## Security for IMDS credentials

By default, when the AWS SDK is not configured with valid credentials the SDK will attempt to use the Amazon EC2 Instance Metadata Service (IMDS) to retrieve credentials for an AWS role. This behavior can be disabled by setting the `AWS_EC2_METADATA_DISABLED` environment variable to `true`. This prevents unnecessary network activity and enhances security on untrusted networks where the Amazon EC2 Instance Metadata Service may be impersonated.

**Note**
AWS SDK clients configured with valid credentials will never use IMDS to retrieve credentials, regardless of any of these settings.

### Disabling use of Amazon EC2 IMDS credentials

How you set this environment variable depends on what operating system is in use as well as whether or not you want the change to be persistent.

#### Linux and macOS

Customers using Linux or macOS can set this environment variable with the following command:

```
$ export AWS_EC2_METADATA_DISABLED=true
```

If you want this setting to be persistent across multiple shell sessions and system restarts, you can add the above command to your shell profile file, such as `.bash_profile`, `.zsh_profile`, or `.profile`.

#### Windows

Customers using Windows can set this environment variable with the following command:

```
$ set AWS_EC2_METADATA_DISABLED=true
```

If you want this setting to be persistent across multiple shell sessions and system restarts can use the following command instead:

```
$ setx AWS_EC2_METADATA_DISABLED=true
```

**Note**
The **setx** command does not apply the value to the current shell session, so you will need to reload or reopen the shell for the change to take effect.

## Support by AWS SDKs and tools

The following SDKs support the features and settings described in this topic. Any partial exceptions are noted. Any JVM system property settings are supported by the AWS SDK for Java and the AWS SDK for Kotlin only.

| SDK | Supported | Notes or more information |
| --- | --- | --- |
| [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/) | Yes |  |
| [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/) | Yes |  |
| [SDK for Go V2 (1.x)](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/) | Yes |  |
| [SDK for Go 1.x (V1)](https://docs.aws.amazon.com/sdk-for-go/latest/developer-guide/) | Yes | To use shared config file settings, you must turn on loading from the config file; see [Sessions](https://docs.aws.amazon.com/sdk-for-go/api/aws/session/). |
| [SDK for Java 2.x](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/) | Yes |  |
| [SDK for Java 1.x](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/) | Partial | JVM system properties: Use com.amazonaws.sdk.disableEc2MetadataV1 instead of aws.disableEc2MetadataV1; aws.ec2MetadataServiceEndpoint and aws.ec2MetadataServiceEndpointMode not supported.  |
| [SDK for JavaScript 3.x](https://docs.aws.amazon.com/sdk-for-javascript/latest/developer-guide/) | Yes |  |
| [SDK for JavaScript 2.x](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/) | Yes |  |
| [SDK for Kotlin](https://docs.aws.amazon.com/sdk-for-kotlin/latest/developer-guide/) | Yes | Does not use IMDSv1 fallback. |
| [SDK for .NET 4.x](https://docs.aws.amazon.com/sdk-for-net/latest/developer-guide/) | Yes |  |
| [SDK for .NET 3.x](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/) | Yes |  |
| [SDK for PHP 3.x](https://docs.aws.amazon.com/sdk-for-php/latest/developer-guide/) | Yes |  |
| [SDK for Python (Boto3)](https://docs.aws.amazon.com/boto3/latest/) | Yes |  |
| [SDK for Ruby 3.x](https://docs.aws.amazon.com/sdk-for-ruby/latest/developer-guide/) | Yes |  |
| [SDK for Rust](https://docs.aws.amazon.com/sdk-for-rust/latest/dg/) | Yes | Does not use IMDSv1 fallback. |
| [SDK for Swift](https://docs.aws.amazon.com/sdk-for-swift/latest/developer-guide/) | Yes |  |
| [Tools for PowerShell V5](https://docs.aws.amazon.com/powershell/latest/userguide/) | Yes | You can disable IMDSv1 fallback explicitly in code using [Amazon.Util.EC2InstanceMetadata]::EC2MetadataV1Disabled = $true. |
| [Tools for PowerShell V4](https://docs.aws.amazon.com/powershell/v4/userguide/) | Yes | You can disable IMDSv1 fallback explicitly in code using [Amazon.Util.EC2InstanceMetadata]::EC2MetadataV1Disabled = $true. |
