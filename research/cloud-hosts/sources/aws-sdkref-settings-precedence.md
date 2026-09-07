# AWS SDKs and tools settings reference

SDKs provide language-specific APIs for AWS services. They take care of some of the heavy lifting necessary in successfully making API calls, including authentication, retry behavior, and more. To do this, the SDKs have flexible strategies to obtain credentials to use for your requests, to maintain settings to use with each service, and to obtain values to use for global settings.

You can find detailed information about configuration settings in the following sections:
+ [AWS SDKs and Tools standardized credential providers](standardized-credentials.md) – Common credential providers standardized across multiple SDKs.
+ [AWS SDKs and Tools standardized features](standardized-features.md) – Common features standardized across multiple SDKs.

## Creating service clients

 To programmatically access AWS services, SDKs use a client class/object for each AWS service. For example, if your application needs to access Amazon EC2, your application creates an Amazon EC2 client object to interface with that service. You then use the service client to make requests to that AWS service. In most SDKs, a service client object is immutable, so you must create a new client for each service to which you make requests and for making requests to the same service using a different configuration.

## Precedence of settings

Global settings configure features, credential providers, and other functionality that are supported by most SDKs and have a broad impact across AWS services. All SDKs have a series of places (or sources) that they check in order to find a value for global settings. The following is the setting lookup precedence:

1. Any explicit setting set in the code or on a service client itself takes precedence over anything else.
   + Some settings can be set on a per-operation basis, and can be changed as needed for each operation that you invoke. For the AWS CLI or AWS Tools for PowerShell, these take the form of per-operation parameters that you enter on the command line. For an SDK, explicit assignments can take the form of a parameter that you set when you instantiate an AWS service client or configuration object, or sometimes when you call an individual API.

1. Java/Kotlin only: The JVM system property for the setting is checked. If it's set, that value is used to configure the client.

1. The environment variable is checked. If it's set, that value is used to configure the client.

1. The SDK checks the shared `credentials` file for the setting. If it's set, the client uses it.

1. The shared `config` file for the setting. If the setting is present, the SDK uses it.
   + The `AWS_PROFILE` environment variable or the `aws.profile` JVM system property can be used to specify which profile that the SDK loads.

1. Any default value provided by the SDK source code itself is used last.

**Note**
Some SDKs and tools might check in a different order. Also, some SDKs and tools support other methods of storing and retrieving parameters. For example, the AWS SDK for .NET supports an additional source called the [SDK Store](https://docs.aws.amazon.com/sdk-for-net/latest/developer-guide/sdk-store.html). For more information about providers that are unique to a SDK or tool, see the specific guide for the SDK or tool that you are using.

The order determines which methods take precedence and override others. For example, if you set up a profile in the shared `config` file, it's only found and used after the SDK or tool checks the other places first. This means that if you put a setting in the `credentials` file, it is used instead of one found in the `config` file. If you configure an environment variable with a setting and value, it would override that setting in both the `credentials` and `config` files. And finally, a setting on the individual operation (AWS CLI command-line parameter or API parameter) or in code would override all other values for that one command.

## Understanding the settings pages of this guide

The pages within the **Settings reference** section of this guide detail the available settings that can be set through various mechanisms. The tables that follow list the config and credential file settings, environment variables, and (for Java and Kotlin SDKs) the JVM settings that can be used outside of your code to configure the feature. Each linked topic in each list takes you to the corresponding settings page.
+ [`Config` file settings list](#ConfigFileSettings)
+ [`Credentials` file settings list](#CredFileSettings)
+ [Environment variables list](#EVarSettings)
+ [JVM system properties list](#JVMSettings)

 Each credential provider or feature has a page where the settings that are used to configure that functionality are listed. For each setting, you can often set the value either by adding the setting to a configuration file, or by setting an environment variable, or (for Java and Kotlin only) by setting a JVM system property. Each setting lists all supported methods of setting the value in a block above the details of the description. Although the [precedence](#precedenceOfSettings) varies, the resulting functionality is the same regardless of how you set it.

The description will include the default value, if any, that takes effect if you do nothing. It also defines what a valid value is for that setting.

 For example, let's look at a setting from the [Request compression](feature-compression.md) feature page.

The `disable_request_compression` example setting's information documents the following:
+ There are three equivalent ways to control request compression outside of your codebase. You can either:
  + Set it in your config file using `disable_request_compression`
  +  Set it as an environment variable using `AWS_DISABLE_REQUEST_COMPRESSION`
  + Or, if you are using the Java or Kotlin SDK, set it as a JVM system property using `aws.disableRequestCompression`
**Note**
There might also be a way to configure the same functionality directly in your code, but this Reference does not cover this since it is unique to each SDK. If you want to set your configuration in the code itself, see your specific SDK guide or API reference.
+ If you do nothing, the value will default to `false`.
+ The only valid values for this Boolean setting are `true` and `false`.

At the bottom of each feature page there is a **Support by AWS SDKs and tools** table.

This table shows whether your SDK supports the settings that are listed on the page. The `Supported` column indicates the support level with the following values:
+ `Yes` – The settings are fully supported by the SDK as written.
+ `Partial` – Some of the settings are supported or the behavior deviates from the description. For `Partial`, an additional note indicates the deviation.
+ `No` – None of the settings are supported. This doesn't make claims as to whether the same functionality might be achieved in code; it only indicates that the listed external configuration settings are not supported.

## `Config` file settings list

The settings listed in the following table can be assigned in the shared AWS `config` file. They are global and affect all AWS services. SDKs and tools may also support unique settings and environment variables. To see the settings and environment variables supported by only an individual SDK or tool, see that specific SDK or tool guide.

| Setting name | Details |
| --- | --- |
|  account\_id\_endpoint\_mode  | [Account-based endpoints](feature-account-endpoints.md)  |
|  api\_versions  | [General configuration settings](feature-gen-config.md)  |
|  auth\_scheme\_preference  | [Authentication scheme](feature-auth-scheme.md)  |
|  aws\_access\_key\_id  | [AWS access keys](feature-static-credentials.md)  |
|  aws\_account\_id  | [Account-based endpoints](feature-account-endpoints.md)  |
|  aws\_secret\_access\_key  | [AWS access keys](feature-static-credentials.md)  |
|  aws\_session\_token  | [AWS access keys](feature-static-credentials.md)  |
|  ca\_bundle  | [General configuration settings](feature-gen-config.md)  |
|  credential\_process  | [Process credential provider](feature-process-credentials.md)  |
|  credential\_source  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  defaults\_mode  | [Smart configuration defaults](feature-smart-config-defaults.md)  |
|  disable\_host\_prefix\_injection  | [Host prefix injection](feature-host-prefix.md)  |
|  disable\_request\_compression  | [Request compression](feature-compression.md)  |
|  duration\_seconds  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  ec2\_metadata\_service\_endpoint  | [IMDS credential provider](feature-imds-credentials.md)  |
|  ec2\_metadata\_service\_endpoint\_mode  | [IMDS credential provider](feature-imds-credentials.md)  |
|  ec2\_metadata\_v1\_disabled  | [IMDS credential provider](feature-imds-credentials.md)  |
|  endpoint\_discovery\_enabled  | [Endpoint discovery](feature-endpoint-discovery.md)  |
|  endpoint\_url  | [Service-specific endpoints](feature-ss-endpoints.md)  |
|  external\_id  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  ignore\_configured\_endpoint\_urls  | [Service-specific endpoints](feature-ss-endpoints.md)  |
|  max\_attempts  | [Retry behavior](feature-retry-behavior.md)  |
|  metadata\_service\_num\_attempts  | [Amazon EC2 instance metadata](feature-ec2-instance-metadata.md)  |
|  metadata\_service\_timeout  | [Amazon EC2 instance metadata](feature-ec2-instance-metadata.md)  |
|  mfa\_serial  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  output  | [General configuration settings](feature-gen-config.md)  |
|  parameter\_validation  | [General configuration settings](feature-gen-config.md)  |
|  region  | [AWS Region](feature-region.md)  |
|  request\_checksum\_calculation  | [Data Integrity Protections for Amazon S3](feature-dataintegrity.md)  |
|  request\_min\_compression\_size\_bytes  | [Request compression](feature-compression.md)  |
|  response\_checksum\_validation  | [Data Integrity Protections for Amazon S3](feature-dataintegrity.md)  |
|  retry\_mode  | [Retry behavior](feature-retry-behavior.md)  |
|  role\_arn  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  role\_session\_name  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  s3\_disable\_express\_session\_auth  | [S3 Express One Zone session authentication](feature-s3-express.md)  |
|  s3\_disable\_multiregion\_access\_points  | [Amazon S3 Multi-Region Access Points](feature-s3-mrap.md)  |
|  s3\_use\_arn\_region  | [Amazon S3 access points](feature-s3-access-point.md)  |
|  sdk\_ua\_app\_id  | [Application ID](feature-appid.md)  |
|  sigv4a\_signing\_region\_set  | [Authentication scheme](feature-auth-scheme.md)  |
|  source\_profile  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  sso\_account\_id  | [IAM Identity Center credential provider](feature-sso-credentials.md)  |
|  sso\_region  | [IAM Identity Center credential provider](feature-sso-credentials.md)  |
|  sso\_registration\_scopes  | [IAM Identity Center credential provider](feature-sso-credentials.md)  |
|  sso\_role\_name  | [IAM Identity Center credential provider](feature-sso-credentials.md)  |
|  sso\_start\_url  | [IAM Identity Center credential provider](feature-sso-credentials.md)  |
|  sts\_regional\_endpoints  | [AWS STS Regional endpoints](feature-sts-regionalized-endpoints.md)  |
|  use\_dualstack\_endpoint  | [Dual-stack and FIPS endpoints](feature-endpoints.md)  |
|  use\_fips\_endpoint  | [Dual-stack and FIPS endpoints](feature-endpoints.md)  |
|  web\_identity\_token\_file  | [Assume role credential provider](feature-assume-role-credentials.md)  |

## `Credentials` file settings list

The settings listed in the following table can be assigned in the shared AWS `credentials` file. They are global and affect all AWS services. SDKs and tools may also support unique settings and environment variables. To see the settings and environment variables supported by only an individual SDK or tool, see that specific SDK or tool guide.

| Setting name | Details |
| --- | --- |
|  aws\_access\_key\_id  | [AWS access keys](feature-static-credentials.md)  |
|  aws\_secret\_access\_key  | [AWS access keys](feature-static-credentials.md)  |
|  aws\_session\_token  | [AWS access keys](feature-static-credentials.md)  |

## Environment variables list

Environment variables supported by most SDKs are listed in the following table. They are global and affect all AWS services. SDKs and tools may also support unique settings and environment variables. To see the settings and environment variables supported by only an individual SDK or tool, see that specific SDK or tool guide.

| Setting name | Details |
| --- | --- |
|  AWS\_ACCESS\_KEY\_ID  | [AWS access keys](feature-static-credentials.md)  |
|  AWS\_ACCOUNT\_ID  | [Account-based endpoints](feature-account-endpoints.md)  |
|  AWS\_ACCOUNT\_ID\_ENDPOINT\_MODE  | [Account-based endpoints](feature-account-endpoints.md)  |
|  AWS\_AUTH\_SCHEME\_PREFERENCE  | [Authentication scheme](feature-auth-scheme.md)  |
|  AWS\_CA\_BUNDLE  | [General configuration settings](feature-gen-config.md)  |
|  AWS\_CONFIG\_FILE  | [Finding and changing the location of the shared `config` and `credentials` files of AWS SDKs and tools](file-location.md)  |
|  AWS\_CONTAINER\_AUTHORIZATION\_TOKEN  | [Container credential provider](feature-container-credentials.md)  |
|  AWS\_CONTAINER\_AUTHORIZATION\_TOKEN\_FILE  | [Container credential provider](feature-container-credentials.md)  |
|  AWS\_CONTAINER\_CREDENTIALS\_FULL\_URI  | [Container credential provider](feature-container-credentials.md)  |
|  AWS\_CONTAINER\_CREDENTIALS\_RELATIVE\_URI  | [Container credential provider](feature-container-credentials.md)  |
|  AWS\_DEFAULTS\_MODE  | [Smart configuration defaults](feature-smart-config-defaults.md)  |
|  AWS\_DISABLE\_HOST\_PREFIX\_INJECTION  | [Host prefix injection](feature-host-prefix.md)  |
|  AWS\_DISABLE\_REQUEST\_COMPRESSION  | [Request compression](feature-compression.md)  |
|  AWS\_EC2\_METADATA\_DISABLED  | [IMDS credential provider](feature-imds-credentials.md)  |
|  AWS\_EC2\_METADATA\_SERVICE\_ENDPOINT  | [IMDS credential provider](feature-imds-credentials.md)  |
|  AWS\_EC2\_METADATA\_SERVICE\_ENDPOINT\_MODE  | [IMDS credential provider](feature-imds-credentials.md)  |
|  AWS\_EC2\_METADATA\_V1\_DISABLED  | [IMDS credential provider](feature-imds-credentials.md)  |
|  AWS\_ENABLE\_ENDPOINT\_DISCOVERY  | [Endpoint discovery](feature-endpoint-discovery.md)  |
|  AWS\_ENDPOINT\_URL  | [Service-specific endpoints](feature-ss-endpoints.md)  |
|  AWS\_ENDPOINT\_URL\_  | [Service-specific endpoints](feature-ss-endpoints.md)  |
|  AWS\_IGNORE\_CONFIGURED\_ENDPOINT\_URLS  | [Service-specific endpoints](feature-ss-endpoints.md)  |
|  AWS\_MAX\_ATTEMPTS  | [Retry behavior](feature-retry-behavior.md)  |
|  AWS\_METADATA\_SERVICE\_NUM\_ATTEMPTS  | [Amazon EC2 instance metadata](feature-ec2-instance-metadata.md)  |
|  AWS\_METADATA\_SERVICE\_TIMEOUT  | [Amazon EC2 instance metadata](feature-ec2-instance-metadata.md)  |
|  AWS\_PROFILE  | [Using shared `config` and `credentials` files to globally configure AWS SDKs and tools](file-format.md)  |
|  AWS\_REGION  | [AWS Region](feature-region.md)  |
|  AWS\_REQUEST\_CHECKSUM\_CALCULATION  | [Data Integrity Protections for Amazon S3](feature-dataintegrity.md)  |
|  AWS\_REQUEST\_MIN\_COMPRESSION\_SIZE\_BYTES  | [Request compression](feature-compression.md)  |
|  AWS\_RESPONSE\_CHECKSUM\_VALIDATION  | [Data Integrity Protections for Amazon S3](feature-dataintegrity.md)  |
|  AWS\_RETRY\_MODE  | [Retry behavior](feature-retry-behavior.md)  |
|  AWS\_ROLE\_ARN  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  AWS\_ROLE\_SESSION\_NAME  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  AWS\_S3\_DISABLE\_EXPRESS\_SESSION\_AUTH  | [S3 Express One Zone session authentication](feature-s3-express.md)  |
|  AWS\_S3\_DISABLE\_MULTIREGION\_ACCESS\_POINTS  | [Amazon S3 Multi-Region Access Points](feature-s3-mrap.md)  |
|  AWS\_S3\_USE\_ARN\_REGION  | [Amazon S3 access points](feature-s3-access-point.md)  |
|  AWS\_SDK\_UA\_APP\_ID  | [Application ID](feature-appid.md)  |
|  AWS\_SECRET\_ACCESS\_KEY  | [AWS access keys](feature-static-credentials.md)  |
|  AWS\_SESSION\_TOKEN  | [AWS access keys](feature-static-credentials.md)  |
|  AWS\_SHARED\_CREDENTIALS\_FILE  | [Finding and changing the location of the shared `config` and `credentials` files of AWS SDKs and tools](file-location.md)  |
|  AWS\_SIGV4A\_SIGNING\_REGION\_SET  | [Authentication scheme](feature-auth-scheme.md)  |
|  AWS\_STS\_REGIONAL\_ENDPOINTS  | [AWS STS Regional endpoints](feature-sts-regionalized-endpoints.md)  |
|  AWS\_USE\_DUALSTACK\_ENDPOINT  | [Dual-stack and FIPS endpoints](feature-endpoints.md)  |
|  AWS\_USE\_FIPS\_ENDPOINT  | [Dual-stack and FIPS endpoints](feature-endpoints.md)  |
|  AWS\_WEB\_IDENTITY\_TOKEN\_FILE  | [Assume role credential provider](feature-assume-role-credentials.md)  |

## JVM system properties list

You can use the following JVM system properties for the AWS SDK for Java and the AWS SDK for Kotlin (targeting the JVM). See [How to set JVM system properties](jvm-system-properties.md#jvm-sys-props-set) for instructions on how to set JVM system properties.

| Setting name | Details |
| --- | --- |
|  aws.accessKeyId  | [AWS access keys](feature-static-credentials.md)  |
|  aws.accountId  | [Account-based endpoints](feature-account-endpoints.md)  |
|  aws.accountIdEndpointMode  | [Account-based endpoints](feature-account-endpoints.md)  |
|  aws.authSchemePreference  | [Authentication scheme](feature-auth-scheme.md)  |
|  aws.configFile  | [Finding and changing the location of the shared `config` and `credentials` files of AWS SDKs and tools](file-location.md)  |
|  aws.defaultsMode  | [Smart configuration defaults](feature-smart-config-defaults.md)  |
|  aws.disableEc2MetadataV1  | [IMDS credential provider](feature-imds-credentials.md)  |
|  aws.disableHostPrefixInjection  | [Host prefix injection](feature-host-prefix.md)  |
|  aws.disableRequestCompression  | [Request compression](feature-compression.md)  |
|  aws.disableS3ExpressAuth  | [S3 Express One Zone session authentication](feature-s3-express.md)  |
|  aws.ec2MetadataServiceEndpoint  | [IMDS credential provider](feature-imds-credentials.md)  |
|  aws.ec2MetadataServiceEndpointMode  | [IMDS credential provider](feature-imds-credentials.md)  |
|  aws.endpointDiscoveryEnabled  | [Endpoint discovery](feature-endpoint-discovery.md)  |
|  aws.endpointUrl  | [Service-specific endpoints](feature-ss-endpoints.md)  |
|  aws.endpointUrl  | [Service-specific endpoints](feature-ss-endpoints.md)  |
|  aws.ignoreConfiguredEndpointUrls  | [Service-specific endpoints](feature-ss-endpoints.md)  |
|  aws.maxAttempts  | [Retry behavior](feature-retry-behavior.md)  |
|  aws.profile  | [Using shared `config` and `credentials` files to globally configure AWS SDKs and tools](file-format.md)  |
|  aws.region  | [AWS Region](feature-region.md)  |
|  aws.requestChecksumCalculation  | [Data Integrity Protections for Amazon S3](feature-dataintegrity.md)  |
|  aws.requestMinCompressionSizeBytes  | [Request compression](feature-compression.md)  |
|  aws.responseChecksumValidation  | [Data Integrity Protections for Amazon S3](feature-dataintegrity.md)  |
|  aws.retryMode  | [Retry behavior](feature-retry-behavior.md)  |
|  aws.roleArn  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  aws.roleSessionName  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  aws.s3DisableMultiRegionAccessPoints  | [Amazon S3 Multi-Region Access Points](feature-s3-mrap.md)  |
|  aws.s3UseArnRegion  | [Amazon S3 access points](feature-s3-access-point.md)  |
|  aws.secretAccessKey  | [AWS access keys](feature-static-credentials.md)  |
|  aws.sessionToken  | [AWS access keys](feature-static-credentials.md)  |
|  aws.sharedCredentialsFile  | [Finding and changing the location of the shared `config` and `credentials` files of AWS SDKs and tools](file-location.md)  |
|  aws.useDualstackEndpoint  | [Dual-stack and FIPS endpoints](feature-endpoints.md)  |
|  aws.useFipsEndpoint  | [Dual-stack and FIPS endpoints](feature-endpoints.md)  |
|  aws.webIdentityTokenFile  | [Assume role credential provider](feature-assume-role-credentials.md)  |
|  sdk.ua.appId  | [Application ID](feature-appid.md)  |
