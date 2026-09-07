# Using environment variables to globally configure AWS SDKs and tools

Environment variables provide another way to specify configuration options and credentials when using AWS SDKs and tools. Environment variables can be useful for scripting or temporarily setting a named profile as the default. For the list of environment variables supported by most SDKs, see [Environment variables list](settings-reference.md#EVarSettings).

**Precedence of options**
+ If you specify a setting by using its environment variable, it overrides any value loaded from a profile in the shared AWS `config` and `credentials` files.
+ If you specify a setting by using a parameter on the AWS CLI command line, it overrides any value from either the corresponding environment variable or a profile in the configuration file.

## How to set environment variables

The following examples show how you can configure environment variables for the default user.

------
#### [ Linux, macOS, or Unix ]

```
$ export AWS_ACCESS_KEY_ID={{AKIAIOSFODNN7EXAMPLE}}
$ export AWS_SECRET_ACCESS_KEY={{wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY}}
$ export AWS_SESSION_TOKEN={{AQoEXAMPLEH4aoAH0gNCAPy...truncated...zrkuWJOgQs8IZZaIv2BXIa2R4Olgk}}
$ export AWS_REGION={{us-west-2}}
```

Setting the environment variable changes the value used until the end of your shell session, or until you set the variable to a different value. You can make the variables persistent across future sessions by setting them in your shell's startup script.

------
#### [ Windows Command Prompt ]

```
C:\> setx AWS_ACCESS_KEY_ID {{AKIAIOSFODNN7EXAMPLE}}
C:\> setx AWS_SECRET_ACCESS_KEY {{wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY}}
C:\> setx AWS_SESSION_TOKEN {{AQoEXAMPLEH4aoAH0gNCAPy...truncated...zrkuWJOgQs8IZZaIv2BXIa2R4Olgk}}
C:\> setx AWS_REGION {{us-west-2}}
```

Using `[set](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/set_1)` to set an environment variable changes the value used until the end of the current Command Prompt session, or until you set the variable to a different value. Using [`setx`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/setx) to set an environment variable changes the value used in both the current Command Prompt session and all Command Prompt sessions that you create after running the command. It does ***not*** affect other command shells that are already running at the time you run the command.

------
#### [ PowerShell ]

```
PS C:\> $Env:AWS_ACCESS_KEY_ID="{{AKIAIOSFODNN7EXAMPLE}}"
PS C:\> $Env:AWS_SECRET_ACCESS_KEY="{{wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY}}"
PS C:\> $Env:AWS_SESSION_TOKEN="{{AQoEXAMPLEH4aoAH0gNCAPy...truncated...zrkuWJOgQs8IZZaIv2BXIa2R4Olgk}}"
PS C:\> $Env:AWS_REGION="{{us-west-2}}"
```

If you set an environment variable at the PowerShell prompt as shown in the previous examples, it saves the value for only the duration of the current session. To make the environment variable setting persistent across all PowerShell and Command Prompt sessions, store it by using the **System** application in **Control Panel**. Alternatively, you can set the variable for all future PowerShell sessions by adding it to your PowerShell profile. See the [PowerShell documentation](https://docs.microsoft.com/powershell/module/microsoft.powershell.core/about/about_environment_variables) for more information about storing environment variables or persisting them across sessions.

------

## Serverless environment variable setup

 If you use a serverless architecture for development, you have other options for setting environment variables. Depending on your container, you can use different strategies for code running in those containers to see and access environment variables, similar to non-cloud environments.

For example, with AWS Lambda, you can directly set environment variables. For details, see [Using AWS Lambda environment variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html) in the *AWS Lambda Developer Guide*.

In Serverless Framework, you can often set SDK environment variables in the `serverless.yml` file under the provider key under the environment setting. For information on the `serverless.yml` file, see [General function settings](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml#general-function-settings) in the Serverless Framework documentation.

Regardless of which mechanism you use to set container environment variables, there are some that are reserved by the container, such as those documented for Lambda at [Defined runtime environment variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime). Always consult the official documentation for the container that you're using to determine how environment variables are treated and whether there are any restrictions.
