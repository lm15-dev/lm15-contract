# Service-specific endpoints

**Note**
For help in understanding the layout of settings pages, or in interpreting the **Support by AWS SDKs and tools** table that follows, see [Understanding the settings pages of this guide](settings-reference.md#settingsPages).

Service-specific endpoint configuration provides the option to use an endpoint of your choosing for API requests and to have that choice persist. These settings provide flexibility to support local endpoints, VPC endpoints, and third-party local AWS development environments. Different endpoints can be used for testing and production environments. You can specify an endpoint URL for individual AWS services.

Configure this functionality by using the following:

**`endpoint_url` - shared AWS `config` file setting`AWS_ENDPOINT_URL` - environment variable`aws.endpointUrl` - JVM system property: Java/Kotlin only**
When specified directly within a profile or as an environment variable, this setting specifies the endpoint that is used for all service requests. This endpoint is overridden by any configured service-specific endpoint.
You can also use this setting within a `services` section of a shared AWS `config` file to set a custom endpoint for a specific service. For a list of all service identifier keys to use for subsections within the `services` section, see [Identifiers for service-specific endpoints](ss-endpoints-table.md).
**Default value:** `none`
**Valid values:** A URL including the scheme and host for the endpoint. The URL can optionally contain a path component that contains one or more path segments.

**`AWS_ENDPOINT_URL_` - environment variable`aws.endpointUrl` - JVM system property: Java/Kotlin only**
`AWS_ENDPOINT_URL_`, where `` is the AWS service identifier, sets a custom endpoint for a specific service. For a list of all service-specific environment variables, see [Identifiers for service-specific endpoints](ss-endpoints-table.md).
This service-specific endpoint overrides any global endpoint set in `AWS_ENDPOINT_URL`.
**Default value:** `none`
**Valid values:** A URL including the scheme and host for the endpoint. The URL can optionally contain a path component that contains one or more path segments.

**`ignore_configured_endpoint_urls` - shared AWS `config` file setting`AWS_IGNORE_CONFIGURED_ENDPOINT_URLS` - environment variable`aws.ignoreConfiguredEndpointUrls` - JVM system property: Java/Kotlin only**
This setting is used to ignore all custom endpoints configurations.
Note that any explicit endpoint set in the code or on a service client itself is used regardless of this setting. For example, including the `--endpoint-url` command line parameter with an AWS CLI command or passing an endpoint URL into a client constructor will always take effect.
**Default value:** `false`
**Valid values:**
+ **`true`** – The SDK or tool does not read any custom configuration options from the shared `config` file or from environment variables for setting an endpoint URL.
+ **`false`** – The SDK or tool uses any available user-provided endpoints from the shared `config` file or from environment variables.

## Configure endpoints using environment variables

To route requests for all services to a custom endpoint URL, set the `AWS_ENDPOINT_URL` global environment variable.

```
export AWS_ENDPOINT_URL={{http://localhost:4567}}
```

To route requests for a specific AWS service to a custom endpoint URL, use the `AWS_ENDPOINT_URL_` environment variable. Amazon DynamoDB has a `serviceId` of [`DynamoDB`](https://github.com/boto/botocore/blob/bcaf618c4b93c067efa0b85d3e92f3985ff60906/botocore/data/dynamodb/2012-08-10/service-2.json#L10). For this service, the endpoint URL environment variable is `AWS_ENDPOINT_URL_DYNAMODB`. This endpoint takes precedence over the global endpoint set in `AWS_ENDPOINT_URL` for this service.

```
export AWS_ENDPOINT_URL_DYNAMODB={{http://localhost:5678}}
```

 As another example, AWS Elastic Beanstalk has a `serviceId` of [`Elastic Beanstalk`](https://github.com/boto/botocore/blob/bcaf618c4b93c067efa0b85d3e92f3985ff60906/botocore/data/elasticbeanstalk/2010-12-01/service-2.json#L9). The AWS service identifier is based on the API model's `serviceId` by replacing all spaces with underscores and uppercasing all letters. To set the endpoint for this service, the corresponding environment variable is `AWS_ENDPOINT_URL_ELASTIC_BEANSTALK`. For a list of all service-specific environment variables, see [Identifiers for service-specific endpoints](ss-endpoints-table.md).

```
export AWS_ENDPOINT_URL_ELASTIC_BEANSTALK={{http://localhost:5567}}
```

## Configure endpoints using the shared `config` file

In the shared `config` file, `endpoint_url` is used in different places for different functionality.
+ `endpoint_url` specified directly within a `profile` makes that endpoint the global endpoint.
+ `endpoint_url` nested under a service identifier key within a `services` section makes that endpoint apply to requests made only to that service. For details on defining a `services` section in your shared `config` file, see [Format of the config file](file-format.md#file-format-config).

 The following example uses a `services` definition to configure a service-specific endpoint URL to be used for Amazon S3 and a custom global endpoint to be used for all other services:

```
[profile {{dev-s3-specific-and-global}}]
endpoint_url = {{http://localhost:1234}}
services = {{s3-specific}}

[services {{s3-specific}}]
s3 =
  endpoint_url = {{https://play.min.io:9000}}
```

A single profile can configure endpoints for multiple services. This example shows how to set the service-specific endpoint URLs for Amazon S3 and AWS Elastic Beanstalk in the same profile. AWS Elastic Beanstalk has a `serviceId` of [`Elastic Beanstalk`](https://github.com/boto/botocore/blob/bcaf618c4b93c067efa0b85d3e92f3985ff60906/botocore/data/elasticbeanstalk/2010-12-01/service-2.json#L9). The AWS service identifier is based on the API model's `serviceId` by replacing all spaces with underscores and lowercasing all letters. Thus, the service identifier key becomes `elastic_beanstalk` and settings for this service begin on the line `elastic_beanstalk = `. For a list of all service identifier keys to use in the `services` section, see [Identifiers for service-specific endpoints](ss-endpoints-table.md).

```
[services {{testing-s3-and-eb}}]
s3 =
  endpoint_url = {{http://localhost:4567}}
elastic_beanstalk =
  endpoint_url = {{http://localhost:8000}}

[profile {{dev}}]
services = {{testing-s3-and-eb}}
```

The service configuration section can be used from multiple profiles. For example, two profiles can use the same `services` definition while altering other profile properties:

```
[services {{testing-s3}}]
s3 =
  endpoint_url = {{https://localhost:4567}}

[profile {{testing-json}}]
output = json
services = {{testing-s3}}

[profile {{testing-text}}]
output = text
services = {{testing-s3}}
```

## Configure endpoints in profiles using role-based credentials

If your profile has role-based credentials configured through a `source_profile` parameter for IAM assume role functionality, the SDK only uses service configurations for the specified profile. It does not use profiles that are role chained to it. For example, using the following shared `config` file:

```
[profile {{A}}]
credential_source = {{Ec2InstanceMetadata}}
endpoint_url = {{https://profile-a-endpoint.aws/}}

[profile {{B}}]
source_profile = {{A}}
role_arn = {{arn:aws:iam::123456789012:role/roleB}}
services = {{profileB}}

[services {{profileB}}]
ec2 =
  endpoint_url = {{https://profile-b-ec2-endpoint.aws}}
```

 If you use profile `B` and make a call in your code to Amazon EC2, the endpoint resolves as `https://profile-b-ec2-endpoint.aws`. If your code makes a request to any other service, the endpoint resolution will not follow any custom logic. The endpoint does not resolve to the global endpoint defined in profile `A`. For a global endpoint to take effect for profile `B`, you would need to set `endpoint_url` directly within profile `B`. For more information on the `source_profile` setting, see [Assume role credential provider](feature-assume-role-credentials.md).

## Precedence of settings

 The settings for this feature can be used at the same time but only one value will take priority per service. For API calls made to a given AWS service, the following order is used to select a value:

1. Any explicit setting set in the code or on a service client itself takes precedence over anything else.
   + For the AWS CLI, this is the value provided by the `--endpoint-url` command line parameter. For an SDK, explicit assignments can take the form of a parameter that you set when you instantiate an AWS service client or configuration object.

1. The value provided by a service-specific environment variable such as `AWS_ENDPOINT_URL_DYNAMODB`.

1. The value provided by the `AWS_ENDPOINT_URL` global endpoint environment variable.

1. The value provided by the `endpoint_url` setting nested under a service identifier key within a `services` section of the shared `config` file.

1. The value provided by the `endpoint_url` setting specified directly within a `profile` of the shared `config` file.

1. Any default endpoint URL for the respective AWS service is used last.

## Support by AWS SDKs and tools

The following SDKs support the features and settings described in this topic. Any partial exceptions are noted. Any JVM system property settings are supported by the AWS SDK for Java and the AWS SDK for Kotlin only.

| SDK | Supported | Notes or more information |
| --- | --- | --- |
| [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/) | Yes |  |
| [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/) | Yes |  |
| [SDK for Go V2 (1.x)](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/) | Yes |  |
| [SDK for Go 1.x (V1)](https://docs.aws.amazon.com/sdk-for-go/latest/developer-guide/) | No |  |
| [SDK for Java 2.x](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/) | Yes |  |
| [SDK for Java 1.x](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/) | No |  |
| [SDK for JavaScript 3.x](https://docs.aws.amazon.com/sdk-for-javascript/latest/developer-guide/) | Yes |  |
| [SDK for JavaScript 2.x](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/) | No |  |
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
