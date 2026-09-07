# IAM Identity Center credential provider

**Note**
For help in understanding the layout of settings pages, or in interpreting the **Support by AWS SDKs and tools** table that follows, see [Understanding the settings pages of this guide](settings-reference.md#settingsPages).

This authentication mechanism uses AWS IAM Identity Center to get single sign-on (SSO) access to AWS services for your code.

**Note**
In the AWS SDK API documentation, the IAM Identity Center credential provider is called the SSO credential provider.

After you enable IAM Identity Center, you define a profile for its settings in your shared AWS `config` file. This profile is used to connect to the IAM Identity Center access portal. When a user successfully authenticates with IAM Identity Center, the portal returns short-term credentials for the IAM role associated with that user. To learn how the SDK gets temporary credentials from the configuration and uses them for AWS service requests, see [How IAM Identity Center authentication is resolved for AWS SDKs and tools](understanding-sso.md).

There are two ways to configure IAM Identity Center through the `config` file:
+ **(Recommended) SSO token provider configuration** – Extended session durations. Includes support for custom session durations.
+ **Legacy non-refreshable configuration** – Uses a fixed, eight-hour session.

In both configurations, you need to sign in again when your session expires.

The following two guides contain additional information about IAM Identity Center:
+ [AWS IAM Identity Center User Guide](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html)
+ [AWS IAM Identity Center Portal API Reference](https://docs.aws.amazon.com/singlesignon/latest/PortalAPIReference/Welcome.html)

For a deep dive on how the SDKs and tools use and refresh credentials using this configuration, see [How IAM Identity Center authentication is resolved for AWS SDKs and tools](understanding-sso.md).

## Prerequisites

You must first enable IAM Identity Center. For details about enabling IAM Identity Center authentication, see [Enabling AWS IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/get-set-up-for-idc.html) in the *AWS IAM Identity Center User Guide*.

**Note**
Alternatively, for complete prerequisites **and** the necessary shared `config` file configuration that is detailed on this page, see the guided instructions for setting up [Using IAM Identity Center to authenticate AWS SDK and tools](access-sso.md).

## SSO token provider configuration

When you use the SSO token provider configuration, your AWS SDK or tool automatically refreshes your session up to your extended session period. For more information on session duration and maximum duration, see [Configure the session duration of the AWS access portal and IAM Identity Center integrated applications](https://docs.aws.amazon.com/singlesignon/latest/userguide/configure-user-session.html) in the *AWS IAM Identity Center User Guide*.

The `sso-session` section of the `config` file is used to group configuration variables for acquiring SSO access tokens, which can then be used to acquire AWS credentials. For more details on this section within a `config` file, see [Format of the config file](file-format.md#file-format-config).

The following shared `config` file example configures the SDK or tool using a `dev` profile to request IAM Identity Center credentials.

```
[profile {{dev}}]
sso_session = {{my-sso}}
sso_account_id = {{111122223333}}
sso_role_name = {{SampleRole}}

[sso-session {{my-sso}}]
sso_region = {{us-east-1}}
sso_start_url = {{https://my-sso-portal.awsapps.com/start}}
sso_registration_scopes = {{sso:account:access}}
```

**Note**
For `sso_region`, use the AWS Region where your IAM Identity Center instance is configured. This can differ from your default AWS Region. You can find this value on the IAM Identity Center console **Dashboard**.

The previous examples shows that you define an `sso-session` section and associate it to a profile. Typically, `sso_account_id` and `sso_role_name` must be set in the `profile` section so that the SDK can request AWS credentials. `sso_region`, `sso_start_url`, and `sso_registration_scopes` must be set within the `sso-session` section.

`sso_account_id` and `sso_role_name` aren't required for all scenarios of SSO token configuration. If your application only uses AWS services that support bearer authentication, then traditional AWS credentials are not needed. Bearer authentication is an HTTP authentication scheme that uses security tokens called bearer tokens. In this scenario, `sso_account_id` and `sso_role_name` aren't required. See the individual AWS service guide to determine if the service supports bearer token authorization.

Registration scopes are configured as part of an `sso-session`. Scope is a mechanism in OAuth 2.0 to limit an application's access to a user's account. The previous example sets `sso_registration_scopes` to provide necessary access for listing accounts and roles.

The following example shows how you can reuse the same `sso-session` configuration across multiple profiles.

```
[profile {{dev}}]
sso_session = {{my-sso}}
sso_account_id = {{111122223333}}
sso_role_name = {{SampleRole}}

[profile prod]
sso_session = {{my-sso}}
sso_account_id = {{111122223333}}
sso_role_name = {{SampleRole2}}

[sso-session {{my-sso}}]
sso_region = {{us-east-1}}
sso_start_url = {{https://my-sso-portal.awsapps.com/start}}
sso_registration_scopes = {{sso:account:access}}
```

The authentication token is cached to disk under the `~/.aws/sso/cache` directory with a file name based on the session name.

## Legacy non-refreshable configuration

Automated token refresh isn't supported using the legacy non-refreshable configuration. We recommend using the [SSO token provider configuration](#sso-token-config) instead.

**Important**
With the legacy configuration, your session is fixed at eight hours and cannot be refreshed automatically. When the session expires, any code that resolves new credentials fails authentication until you run `aws sso login` again. If you have long-running processes or automation, use the SSO token provider configuration, which supports automatic token refresh.

To use the legacy non-refreshable configuration, you must specify the following settings within your profile:
+ `sso_start_url`
+ `sso_region`
+ `sso_account_id`
+ `sso_role_name`

You specify the user portal for a profile with the `sso_start_url` and `sso_region` settings. You specify permissions with the `sso_account_id` and `sso_role_name` settings.

The following example sets the four required values in the `config` file.

```
[profile {{my-sso-profile}}]
sso_start_url = {{https://my-sso-portal.awsapps.com/start}}
sso_region = {{us-west-2}}
sso_account_id = {{111122223333}}
sso_role_name = {{SSOReadOnlyRole}}
```

The authentication token is cached to disk under the `~/.aws/sso/cache` directory with a file name based on the `sso_start_url`.

## IAM Identity Center credential provider settings

Configure this functionality by using the following:

**`sso_start_url` - shared AWS `config` file setting**
The URL that points to your organization's IAM Identity Center issuer URL or access portal URL. For more information, see [Using the AWS access portal](https://docs.aws.amazon.com/singlesignon/latest/userguide/using-the-portal.html) in the *AWS IAM Identity Center User Guide*.
 To find this value, open the [IAM Identity Center console](https://console.aws.amazon.com/singlesignon), view the **Dashboard**, find **AWS access portal URL**.
+ Alternatively, starting with version **2.22.0** of the AWS CLI, you can instead use the value for **AWS Issuer URL**.

**`sso_region` - shared AWS `config` file setting**
The AWS Region that contains your IAM Identity Center portal host; that is, the Region you selected before enabling IAM Identity Center. This is independent from your default AWS Region, and can be different.
For a complete list of the AWS Regions and their codes, see [Regional Endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html#regional-endpoints) in the *Amazon Web Services General Reference*. To find this value, open the [IAM Identity Center console](https://console.aws.amazon.com/singlesignon), view the **Dashboard**, and find **Region**.

**`sso_account_id` - shared AWS `config` file setting**
The numeric ID of the AWS account that was added through the AWS Organizations service to use for authentication.
To see the list of available accounts, go to the [IAM Identity Center console](https://console.aws.amazon.com/singlesignon) and open the **AWS accounts** page. You can also see the list of available accounts using the [ListAccounts](https://docs.aws.amazon.com/singlesignon/latest/PortalAPIReference/API_ListAccounts.html) API method in the *AWS IAM Identity Center Portal API Reference*. For example, you can call the AWS CLI method [list-accounts](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sso/list-accounts.html).

**`sso_role_name` - shared AWS `config` file setting**
The name of a permission set provisioned as an IAM role that defines the user's resulting permissions. The role must exist in the AWS account specified by `sso_account_id`. Use the role name, not the role Amazon Resource Name (ARN).
Permission sets have IAM policies and custom permissions policies attached to them and define the level of access that users have to their assigned AWS accounts.
To see the list of available permission sets per AWS account, go to the [IAM Identity Center console](https://console.aws.amazon.com/singlesignon) and open the **AWS accounts** page. Choose the correct permission set name listed in the AWS accounts table. You can also see the list of available permission sets using the [ListAccountRoles](https://docs.aws.amazon.com/singlesignon/latest/PortalAPIReference/API_ListAccountRoles.html) API method in the *AWS IAM Identity Center Portal API Reference*. For example, you can call the AWS CLI method [list-account-roles](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sso/list-account-roles.html).

**`sso_registration_scopes` - shared AWS `config` file setting**
A comma-delimited list of valid scope strings to be authorized for the `sso-session`. An application can request one or more scopes, and the access token issued to the application is limited to the scopes granted. A minimum scope of `sso:account:access` must be granted to get a refresh token back from the IAM Identity Center service. For the list of available access scope options, see [Access scopes](https://docs.aws.amazon.com/singlesignon/latest/userguide/customermanagedapps-saml2-oauth2.html#oidc-concept) in the *AWS IAM Identity Center User Guide*.
These scopes define the permissions requested to be authorized for the registered OIDC client and access tokens retrieved by the client. Scopes authorize access to IAM Identity Center bearer token authorized endpoints.
This setting doesn't apply to the legacy non-refreshable configuration. Tokens issued using the legacy configuration are limited to scope `sso:account:access` implicitly.

## Support by AWS SDKs and tools

The following SDKs support the features and settings described in this topic. Any partial exceptions are noted. Any JVM system property settings are supported by the AWS SDK for Java and the AWS SDK for Kotlin only.

| SDK | Supported | Notes or more information |
| --- | --- | --- |
| [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/) | Yes |  |
| [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/) | Yes |  |
| [SDK for Go V2 (1.x)](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/) | Yes |  |
| [SDK for Go 1.x (V1)](https://docs.aws.amazon.com/sdk-for-go/latest/developer-guide/) | Yes | To use shared config file settings, you must turn on loading from the config file; see [Sessions](https://docs.aws.amazon.com/sdk-for-go/api/aws/session/). |
| [SDK for Java 2.x](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/) | Yes | Configuration values also supported in credentials file. |
| [SDK for Java 1.x](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/) | No |  |
| [SDK for JavaScript 3.x](https://docs.aws.amazon.com/sdk-for-javascript/latest/developer-guide/) | Yes |  |
| [SDK for JavaScript 2.x](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/) | Yes |  |
| [SDK for Kotlin](https://docs.aws.amazon.com/sdk-for-kotlin/latest/developer-guide/) | Yes |  |
| [SDK for .NET 4.x](https://docs.aws.amazon.com/sdk-for-net/latest/developer-guide/) | Yes |  |
| [SDK for .NET 3.x](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/) | Yes |  |
| [SDK for PHP 3.x](https://docs.aws.amazon.com/sdk-for-php/latest/developer-guide/) | Yes |  |
| [SDK for Python (Boto3)](https://docs.aws.amazon.com/boto3/latest/) | Yes |  |
| [SDK for Ruby 3.x](https://docs.aws.amazon.com/sdk-for-ruby/latest/developer-guide/) | Yes |  |
| [SDK for Rust](https://docs.aws.amazon.com/sdk-for-rust/latest/dg/) | Partial | Legacy non-refreshable configuration only. |
| [SDK for Swift](https://docs.aws.amazon.com/sdk-for-swift/latest/developer-guide/) | Yes |  |
| [Tools for PowerShell V5](https://docs.aws.amazon.com/powershell/latest/userguide/) | Yes |  |
| [Tools for PowerShell V4](https://docs.aws.amazon.com/powershell/v4/userguide/) | Yes |  |

**Note**
Here are the relevant docs for AWS Toolkits and IAM Identity Center authentication:
**VS Code** – [Connecting to AWS](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/connect.html) - Covers IAM Identity Center sign-in via Start URL and browser-based auth.
**Visual Studio** – [AWS IAM Identity Center credentials in AWS Toolkit for Visual Studio](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/sso-credentials.html) - Covers configuring SSO profiles.
**JetBrains** – [Connecting the AWS Toolkit for JetBrains to your AWS account](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/account-connect.html) - Covers how to connect the AWS Toolkit for JetBrains to your AWS account.
