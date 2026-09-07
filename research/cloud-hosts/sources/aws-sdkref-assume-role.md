# Assume role credential provider

**Note**
For help in understanding the layout of settings pages, or in interpreting the **Support by AWS SDKs and tools** table that follows, see [Understanding the settings pages of this guide](settings-reference.md#settingsPages).

Assuming a role involves using a set of temporary security credentials to access AWS resources that you might not have access to otherwise. These temporary credentials consist of an access key ID, a secret access key, and a security token.

To set up your SDK or tool to assume a role, you must first create or identify a specific *role* to assume. IAM roles are uniquely identified by a role Amazon Resource Name ([ARN](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html)). Roles establish trust relationships with another entity. The trusted entity that uses the role might be an AWS service, another AWS account, a web identity provider or OIDC, or SAML federation.

After the IAM role is identified, if you are trusted by that role, you can configure your SDK or tool to use the permissions that are granted by the role. To do this, use the following settings.

For guidance on getting started using these settings, see [Assuming a role with AWS credentials to authenticate AWS SDKs and tools](access-assume-role.md) in this guide.

## Assume role credential provider settings

Configure this functionality by using the following:

**`credential_source` - shared AWS `config` file setting**
Used within Amazon EC2 instances or Amazon Elastic Container Service containers to specify where the SDK or tool can find credentials that have permission to assume the role that you specify with the `role_arn` parameter.
**Default value:** None
**Valid values:**
+ **Environment** – Specifies that the SDK or tool is to retrieve source credentials from the environment variables [`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`](feature-static-credentials.md).
+ **Ec2InstanceMetadata** – Specifies that the SDK or tool is to use the [IAM role attached to the EC2 instance profile](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html) to get source credentials.
+ **EcsContainer** – Specifies that the SDK or tool is to use the [IAM role attached to the Amazon ECS container](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/instance_IAM_role.html) or the [IAM role attached to the Amazon EKS container](https://docs.aws.amazon.com/eks/latest/userguide/security-iam-service-with-iam.html) to get source credentials.
You cannot specify both `credential_source` and `source_profile` in the same profile.
Example of setting this in a `config` file to indicate that credentials should be sourced from Amazon EC2:

```
credential_source = Ec2InstanceMetadata
role_arn = arn:aws:iam::{{123456789012}}:role/{{my-role-name}}
```

**`duration_seconds` - shared AWS `config` file setting**
Specifies the maximum duration of the role session, in seconds.
This setting applies only when the profile specifies to assume a role.
**Default value:** 3600 seconds (one hour)
**Valid values:** The value can range from 900 seconds (15 minutes) up to the maximum session duration setting configured for the role (which can be a maximum of 43200 seconds, or 12 hours). For more information, see [View the Maximum Session Duration Setting for a Role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html#id_roles_use_view-role-max-session) in the *IAM User Guide*.
Example of setting this in a `config` file:

```
duration_seconds = {{43200}}
```

**`external_id` - shared AWS `config` file setting**
Specifies a unique identifier that is used by third parties to assume a role in their customers' accounts.
This setting applies only when the profile specifies to assume a role and the trust policy for the role requires a value for `ExternalId`. The value maps to the `ExternalId` parameter that is passed to the `AssumeRole` operation when the profile specifies a role.
**Default value:** None.
**Valid values:** See [How to use an External ID When Granting Access to Your AWS Resources to a Third Party](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html) in the *IAM User Guide*.
Example of setting this in a `config` file:

```
external_id = {{unique_value_assigned_by_3rd_party}}
```

**`mfa_serial` - shared AWS `config` file setting**
Specifies the identification or serial number of a multi-factor authentication (MFA) device that the user must use when assuming a role.
Required when assuming a role where the trust policy for that role includes a condition that requires MFA authentication. For more information about MFA, see [AWS Multi-factor authentication in IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa.html) in the *IAM User Guide*.
**Default value:** None.
**Valid values:** The value can be either a serial number for a hardware device (such as `GAHT12345678`), or an Amazon Resource Name (ARN) for a virtual MFA device. The format of the ARN is: `arn:aws:iam::{{account-id}}:mfa/{{mfa-device-name}}`
Example of setting this in a `config` file:
This example assumes a virtual MFA device, called `MyMFADevice`, that has been created for the account and enabled for a user.

```
mfa_serial = arn:aws:iam::{{123456789012}}:mfa/{{MyMFADevice}}
```

**`role_arn` - shared AWS `config` file setting`AWS_ROLE_ARN` - environment variable`aws.roleArn` - JVM system property: Java/Kotlin only**
Specifies the Amazon Resource Name (ARN) of an IAM role that you want to use to perform operations requested using this profile.
**Default value:** None.
**Valid values:** The value must be the ARN of an IAM role, formatted as follows: `arn:aws:iam::{{account-id}}:role/{{role-name}}`
 In addition, you must also specify **one** of the following settings:
+ `source_profile` – To identify another profile to use to find credentials that have permission to assume the role in this profile.
+ `credential_source` – To use either credentials identified by the current environment variables or credentials attached to an Amazon EC2 instance profile, or an Amazon ECS container instance.
+ `web_identity_token_file` – To use public identity providers or any OpenID Connect (OIDC)-compatible identity provider for users who have been authenticated in a mobile or web application.

**`role_session_name` - shared AWS `config` file setting`AWS_ROLE_SESSION_NAME` - environment variable`aws.roleSessionName` - JVM system property: Java/Kotlin only**
Specifies the name to attach to the role session. This name appears in AWS CloudTrail logs for entries associated with this session, which can be useful when auditing. For details, see [CloudTrail userIdentity element](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html) in the *AWS CloudTrail User Guide*.
**Default value:** An optional parameter. If you don't provide this value, a session name is generated automatically if the profile assumes a role.
**Valid values:** Provided to the `RoleSessionName` parameter when the AWS CLI or AWS API calls the `AssumeRole` operation (or operations such as the `AssumeRoleWithWebIdentity` operation) on your behalf. The value becomes part of the assumed role user Amazon Resource Name (ARN) that you can query, and shows up as part of the CloudTrail log entries for operations invoked by this profile.
 `arn:aws:sts::{{123456789012}}:assumed-role/{{my-role-name}}/{{my-role_session_name}}`.
Example of setting this in a `config` file:

```
role_session_name = {{my-role-session-name}}
```

**`source_profile` - shared AWS `config` file setting**
Specifies another profile whose credentials are used to assume the role specified by the `role_arn` setting in the original profile. To understand how profiles are used in the shared AWS `config` and `credentials` files, see [Shared `config` and `credentials` files](file-format.md).
If you specify a profile that is also an assume role profile, each role will be assumed in sequential order to fully resolve the credentials. This chain is stopped when the SDK encounters a profile with credentials. Role chaining limits your AWS CLI or AWS API role session to a maximum of one hour and can't be increased. For more information, see [Roles terms and concepts](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_terms-and-concepts.html) in the *IAM User Guide*.
**Default value:** None.
**Valid values:** A text string that consists of the name of a profile defined in the `config` and `credentials` files. You must also specify a value for `role_arn` in the current profile.
You cannot specify both `credential_source` and `source_profile` in the same profile.
Example of setting this in a config file:

```
[profile {{A}}]
source_profile = {{B}}
role_arn =  arn:aws:iam::{{123456789012}}:role/{{RoleA}}
role_session_name = {{ProfileARoleSession}}

[profile {{B}}]
credential_process = {{./aws_signing_helper credential-process --certificate /path/to/certificate --private-key /path/to/private-key --trust-anchor-arn arn:aws:rolesanywhere:region:account:trust-anchor/TA_ID --profile-arn arn:aws:rolesanywhere:region:account:profile/PROFILE_ID --role-arn arn:aws:iam::account:role/ROLE_ID}}
```
In the previous example, the `A` profile tells the SDK or tool to automatically look up the credentials for the linked `B` profile. In this case, the `B` profile uses the credential helper tool provided by [Using IAM Roles Anywhere to authenticate AWS SDKs and tools](access-rolesanywhere.md) to get credentials for the AWS SDK. Those temporary credentials are then used by your code to access AWS resources. The specified role must have attached IAM permissions policies that allow the requested code to run, such as the command, AWS service, or API method. Every action that is taken by profile `A` has the role session name included in CloudTrail logs.
For a second example of role chaining, the following configuration can be used if you have an application on an Amazon Elastic Compute Cloud instance, and you want to have that application assume another role.

```
[profile {{A}}]
source_profile = {{B}}
role_arn =  arn:aws:iam::{{123456789012}}:role/{{RoleA}}
role_session_name = {{ProfileARoleSession}}

[profile {{B}}]
credential_source=Ec2InstanceMetadata
```
Profile `A` will use the credentials from the Amazon EC2 instance to assume the specified role and will renew the credentials automatically.

**`web_identity_token_file` - shared AWS `config` file setting`AWS_WEB_IDENTITY_TOKEN_FILE` - environment variable`aws.webIdentityTokenFile` - JVM system property: Java/Kotlin only**
Specifies the path to a file that contains an access token from a [supported OAuth 2.0 provider](https://wikipedia.org/wiki/List_of_OAuth_providers) or [OpenID Connect ID identity provider](https://openid.net/developers/certified/).
This setting enables authentication by using web identity federation providers, such as [Google](https://developers.google.com/identity/protocols/OAuth2), [Facebook](https://developers.facebook.com/docs/facebook-login/overview), and [Amazon](https://login.amazon.com/), among many others. The SDK or developer tool loads the contents of this file and passes it as the `WebIdentityToken` argument when it calls the `AssumeRoleWithWebIdentity` operation on your behalf.
**Default value:** None.
**Valid values:** This value must be a path and file name. The file must contain an OAuth 2.0 access token or an OpenID Connect token that was provided to you by an identity provider. Relative paths are treated as relative to the working directory of the process.

## Support by AWS SDKs and tools

The following SDKs support the features and settings described in this topic. Any partial exceptions are noted. Any JVM system property settings are supported by the AWS SDK for Java and the AWS SDK for Kotlin only.

| SDK | Supported | Notes or more information |
| --- | --- | --- |
| [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/) | Yes |  |
| [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/) | Partial | credential\_source not supported. duration\_seconds not supported. mfa\_serial not supported. |
| [SDK for Go V2 (1.x)](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/) | Yes |  |
| [SDK for Go 1.x (V1)](https://docs.aws.amazon.com/sdk-for-go/latest/developer-guide/) | Yes | To use shared config file settings, you must turn on loading from the config file; see [Sessions](https://docs.aws.amazon.com/sdk-for-go/api/aws/session/). |
| [SDK for Java 2.x](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/) | Partial | mfa\_serial not supported. duration\_seconds not supported. |
| [SDK for Java 1.x](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/) | Partial | credential\_source not supported. mfa\_serial not supported. JVM system properties not supported.  |
| [SDK for JavaScript 3.x](https://docs.aws.amazon.com/sdk-for-javascript/latest/developer-guide/) | Yes |  |
| [SDK for JavaScript 2.x](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/) | Partial | credential\_source not supported. |
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
