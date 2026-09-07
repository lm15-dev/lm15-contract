# AWS SDKs and Tools standardized credential providers

Many credential providers have been standardized to consistent defaults and to work the same way across many SDKs. This consistency increases productivity and clarity when coding across multiple SDKs. All settings can be overridden in code. For details, see your specific SDK API.

**Important**
Not all SDKs support all providers, or even all aspects within a provider.

**Topics**
+ [Understand the credential provider chain](#credentialProviderChain)
+ [SDK-specific and tool-specific credential provider chains](#sdk-chains)
+ [AWS access keys](feature-static-credentials.md)
+ [Login provider](feature-login-credentials.md)
+ [Assume role provider](feature-assume-role-credentials.md)
+ [Container provider](feature-container-credentials.md)
+ [IAM Identity Center provider](feature-sso-credentials.md)
+ [IMDS provider](feature-imds-credentials.md)
+ [Process provider](feature-process-credentials.md)

## Understand the credential provider chain

All SDKs have a series of places (or sources) that they check in order to find valid credentials to use to make a request to an AWS service. After valid credentials are found, the search is stopped. This systematic search is called the credential provider chain.

When using one of the standardized credential providers, the AWS SDKs always attempt to renew credentials automatically when they expire. The built-in credential provider chain provides your application with the ability to refresh your credentials regardless of which provider you are using in the chain. No additional code is required for the SDK to do this.

Although the distinct chain used by each SDK varies, they most often include sources such as the following:

| Credential provider | Description |
| --- | --- |
| [AWS access keys](feature-static-credentials.md) | AWS access keys for an IAM user (such as AWS\_ACCESS\_KEY\_ID, and AWS\_SECRET\_ACCESS\_KEY).  |
| [Federate with web identity or OpenID Connect](access-assume-role-web.md#webidentity) - Assume role credential provider | Sign in using a well-known external identity provider (IdP), such as Login with Amazon, Facebook, Google, or any other OpenID Connect (OIDC)-compatible IdP. Assume the permissions of an IAM role using a JSON Web Token (JWT) from AWS Security Token Service (AWS STS). |
| [Login credentials provider](feature-login-credentials.md)  | Get credentials for a new or existing console session that you are logged in to. |
| [IAM Identity Center credential provider](feature-sso-credentials.md) | Get credentials from AWS IAM Identity Center. |
| [Assume role credential provider](feature-assume-role-credentials.md) | Get access to other resources by assuming the permissions of an IAM role. (Retrieve and then use temporary credentials for a role). |
| [Container credential provider](feature-container-credentials.md) | Amazon Elastic Container Service (Amazon ECS) and Amazon Elastic Kubernetes Service (Amazon EKS) credentials. The container credential provider fetches credentials for the customer's containerized application.  |
| [Process credential provider](feature-process-credentials.md) | Custom credential provider. Get your credentials from an external source or process, including IAM Roles Anywhere. |
| [IMDS credential provider](feature-imds-credentials.md) | Amazon Elastic Compute Cloud (Amazon EC2) instance profile credentials. Associate an IAM role with each of your EC2 instances. Temporary credentials for that role are made available to code running in the instance. The credentials are delivered through the Amazon EC2 metadata service.  |

 For each step in the chain, there are multiple ways to assign setting values. Setting values that are specified in code always take precedence. However, there are also [Environment variables](environment-variables.md) and the [Using shared `config` and `credentials` files to globally configure AWS SDKs and tools](file-format.md). For more information, see [Precedence of settings](settings-reference.md#precedenceOfSettings).

## SDK-specific and tool-specific credential provider chains

To go directly to your SDK's or tool's **specific** credential provider chain details, choose your SDK or tool from the following:
+ [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
+ [SDK for C\+\+](https://docs.aws.amazon.com/sdk-for-cpp/latest/developer-guide/credproviders.html)
+ [SDK for Go](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/configure-gosdk.html)
+ [SDK for Java](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/credentials-chain.html)
+ [SDK for JavaScript](https://docs.aws.amazon.com/sdk-for-javascript/latest/developer-guide/setting-credentials-node.html#credchain)
+ [SDK for Kotlin](https://docs.aws.amazon.com/sdk-for-kotlin/latest/developer-guide/credential-providers.html)
+ [SDK for .NET](https://docs.aws.amazon.com/sdk-for-net/latest/developer-guide/creds-assign.html)
+ [SDK for PHP](https://docs.aws.amazon.com/sdk-for-php/latest/developer-guide/guide_credentials.html)
+ [SDK for Python (Boto3)](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html)
+ [SDK for Ruby](https://docs.aws.amazon.com/sdk-for-ruby/latest/developer-guide/setup-config.html)
+ [SDK for Rust](https://docs.aws.amazon.com/sdk-for-rust/latest/dg/credproviders.html)
+ [SDK for Swift](https://docs.aws.amazon.com/sdk-for-swift/latest/developer-guide/using-configuration.html)
+ [Tools for PowerShell](https://docs.aws.amazon.com/powershell/latest/userguide/creds-assign.html)
