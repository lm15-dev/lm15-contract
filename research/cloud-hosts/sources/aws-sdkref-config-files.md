# Using shared `config` and `credentials` files to globally configure AWS SDKs and tools

The shared AWS `config` and `credentials` files are the most common way that you can specify authentication and configuration to an AWS SDK or tool.

The shared `config` and `credentials` files contain a set of profiles. A profile is a set of configuration settings, in key–value pairs, that is used by AWS SDKs, the AWS Command Line Interface (AWS CLI), and other tools. Configuration values are attached to a profile in order to configure some aspect of the SDK/tool when that profile is used. These files are "shared" in that the values take affect for any applications, processes, or SDKs on the local environment for a user.

Both the shared `config` and `credentials` files are plaintext files that contain only ASCII characters (UTF-8 encoded). They take the form of what are generally referred to as [INI files](https://wikipedia.org/wiki/INI_file).

## Profiles

Settings within the shared `config` and `credentials` files are associated with a specific profile. Multiple profiles can be defined within the file to create different setting configurations to apply in different development environments.

 The `[default]` profile contains the values that are used by an SDK or tool operation if a specific named profile is not specified. You can also create separate profiles that you can explicitly reference by name. Each profile can use different settings and values as needed by your application and scenario.

**Note**
`[default]` is simply an unnamed profile. This profile is named `default` because it is the default profile used by the SDK if the user does not specify a profile. It does not provide inherited default values to other profiles. If you set something in the `[default]` profile and you don't set it in a named profile, then the value isn't set when you use the named profile.

### Set a named profile

The `[default]` profile and multiple named profiles can exist in the same file. Use the following setting to select which profile's settings are used by your SDK or tool when running your code. Profiles can also be selected within code, or per-command when working with the AWS CLI.

Configure this functionality by setting one of the following:

**`AWS_PROFILE` - environment variable**
When this environment variable is set to a named profile or "default", all SDK code and AWS CLI commands use the settings in that profile.
Linux/macOS example of setting environment variables via command line:

```
export AWS_PROFILE="my_default_profile_name";
```
Windows example of setting environment variables via command line:

```
setx AWS_PROFILE "my_default_profile_name"
```

**`aws.profile` - JVM system property**
For SDK for Kotlin on the JVM and the SDK for Java 2.x, you can [set the `aws.profile` system property](jvm-system-properties.md#jvm-sys-props-set). When the SDK creates a service client, it uses the settings in the named profile unless the setting is overridden in code. The SDK for Java 1.x does not support this system property.

**Note**
If your application is on a server running multiple applications, we recommend you always used named profiles rather than the default profile. The default profile is automatically picked up by any AWS application in the environment and is shared amongst them. Thus, if someone else updates the default profile for their application it can unintentionally impact the others. To safeguard against this, define a named profile in the shared `config` file and then use that named profile in your application by setting the named profile in your code. You can use the environment variable or JVM system property to set the named profile if you know that it's scope only affects your application.

## Format of the config file

The `config` file is organized into sections. A section is a named collection of settings, and continues until another section definition line is encountered.

The `config` file is a plaintext file that uses the following format:
+ All entries in a section take the general form of `setting-name=value`.
+ Lines can be commented out by starting the line with a hashtag character (`#`).

### Section types

A section definition is a line that applies a name to a collection of settings. Section definition lines start and end with square brackets (`[` `]`). Inside the brackets, there is a section type identifier and a custom name for the section. You can use letters, numbers, hyphens ( `-` ), and underscores ( `_` ), but no spaces.

#### Section type: `default`

Example section definition line: `[default]`

 `[default]` is the only profile that does not require the `profile` section identifier.

The following example shows a basic `config` file with a `[default]` profile. It sets the [`region`](feature-region.md) setting. All settings that follow this line, up until another section definition is encountered, are part of this profile.

```
[default]
#Full line comment, this text is ignored.
region = us-east-2
```

#### Section type: `profile`

Example section definition line: `[profile {{dev}}]`

The `profile` section definition line is a named configuration grouping that you can apply for different development scenarios. To better understand named profiles, see the preceding section on Profiles.

The following example shows a `config` file with a `profile` section definition line and a named profile called `foo`. All settings that follow this line, up until another section definition is encountered, are part of this named profile.

```
[profile {{foo}}]
...settings...
```

Some settings have their own nested group of subsettings, such as the `s3` setting and subsettings in the following example. Associate the subsettings with the group by indenting them by one or more spaces.

```
[profile test]
region = us-west-2
s3 =
    max_concurrent_requests=10
    max_queue_size=1000
```

#### Section type: `sso-session`

Example section definition line: `[sso-session {{my-sso}}]`

The `sso-session` section definition line names a group of settings that you use to configure a profile to resolve AWS credentials using AWS IAM Identity Center. For more information on configuring single sign-on authentication, see [Using IAM Identity Center to authenticate AWS SDK and tools](access-sso.md). A profile is linked to a `sso-session` section by a key-value pair where `sso-session` is the key and the name of your `sso-session` section is the value, such as `sso-session = `.

The following example configures a profile that will get short-term AWS credentials for the "SampleRole" IAM role in the "111122223333" account using a token from the "my-sso". The "my-sso" `sso-session` section is referenced in the `profile` section by name using the `sso-session` key.

```
[profile {{dev}}]
sso_session = {{my-sso}}
sso_account_id = {{111122223333}}
sso_role_name = {{SampleRole}}

[sso-session {{my-sso}}]
sso_region = {{us-east-1}}
sso_start_url = {{https://my-sso-portal.awsapps.com/start}}
```

#### Section type: `services`

Example section definition line: `[services {{dev}}]`

**Note**
The `services` section supports service-specific endpoint customizations and is only available in SDKs and tools that include this feature. To see if this feature is available for your SDK, see [Support by AWS SDKs and tools](feature-ss-endpoints.md#ss-endpoints-sdk-compat) for service-specific endpoints.

The `services` section definition line names a group of settings that configures custom endpoints for AWS service requests. A profile is linked to a `services` section by a key-value pair where `services` is the key and the name of your `services` section is the value, such as `services = `.

 The `services` section is further separated into subsections by ` = ` lines, where `` is the AWS service identifier key. The AWS service identifier is based on the API model's `serviceId` by replacing all spaces with underscores and lowercasing all letters. For a list of all service identifier keys to use in the `services` section, see [Identifiers for service-specific endpoints](ss-endpoints-table.md). The service identifier key is followed by nested settings with each on its own line and indented by two spaces.

 The following example uses a `services` definition to configure the endpoint to use for requests made only to the Amazon DynamoDB service. The `"local-dynamodb"` `services` section is referenced in the `profile` section by name using the `services` key. The AWS service identifier key is `dynamodb`. The Amazon DynamoDB service subsection begins on the line `dynamodb = `. Any immediately following lines that are indented are included in that subsection and apply to that service.

```
[profile {{dev}}]
services = {{local-dynamodb}}

[services {{local-dynamodb}}]
dynamodb =
  endpoint_url = {{http://localhost:8000}}
```

For more information on custom endpoint configuration, see [Service-specific endpoints](feature-ss-endpoints.md).

## Format of the credentials file

The rules for the `credentials` file are generally identical to those for the `config` file, except that profile sections don't begin with the word `profile`. Use only the profile name itself between square brackets. The following example shows a `credentials` file with a named profile section called `foo`.

```
[{{foo}}]
...credential settings...
```

Only the following settings that are considered "secrets" or sensitive can be stored in the `credentials` file: `aws_access_key_id`,`aws_secret_access_key`, and `aws_session_token`. Although these settings can alternatively be placed in the shared `config` file, we recommend that you keep these sensitive values in the separate `credentials` file. This way, you can provide separate permissions for each file, if necessary.

The following example shows a basic `credentials` file with a `[default]` profile. It sets the [`aws_access_key_id`,`aws_secret_access_key`, and `aws_session_token`](feature-static-credentials.md) global settings.

```
[default]
aws_access_key_id={{AKIAIOSFODNN7EXAMPLE}}
aws_secret_access_key={{wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY}}
aws_session_token={{IQoJb3JpZ2luX2IQoJb3JpZ2luX2IQoJb3JpZ2luX2IQoJb3JpZ2luX2IQoJb3JpZVERYLONGSTRINGEXAMPLE}}
```

Regardless of whether you use a named profile or "`default`" in your `credentials` file, any settings here will be combined with any settings from your `config` file that uses the same profile name. If there are credentials in both files for a profile sharing the same name, the keys in the credentials file take precedence.
