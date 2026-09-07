# Access instance metadata for an EC2 instance

You can access EC2 instance metadata from inside of the instance itself or from the EC2 console, API, SDKs, or the AWS CLI. To get the current instance metadata settings for an instance from the console or command line, see [Query instance metadata options for existing instances](#query-IMDS-existing-instances).

You can also modify user data for instances with an EBS root volume. The instance must be in the stopped state. For console directions, see [Update the instance user data](user-data.md#user-data-modify). For a Linux example that uses the AWS CLI, see [modify-instance-attribute](https://docs.aws.amazon.com/cli/latest/reference/ec2/modify-instance-attribute.html). For a Windows example that uses the Tools for Windows PowerShell, see [User data and the Tools for Windows PowerShell](user-data.md#user-data-powershell).

**Note**
You are not billed for HTTP requests used to retrieve instance metadata and user data.

## Instance metadata access considerations

To avoid problems with instance metadata, consider the following.

**Instance launch failures due to IMDSv2 enforcement (`HttpTokensEnforced=enabled`)**
Before enabling IMDSv2 enforcement, you need all your software on the instance to support IMDSv2, after which you can change the default to disable IMDSv1 (`httpTokens=required`), after which you can enable enforcement. For more information, [Transition to using Instance Metadata Service Version 2](instance-metadata-transition-to-version-2.md).

**Command format**
The command format is different, depending on whether you use Instance Metadata Service Version 1 (IMDSv1) or Instance Metadata Service Version 2 (IMDSv2). By default, you can use both versions of the Instance Metadata Service. To require the use of IMDSv2, see [Use the Instance Metadata Service to access instance metadata](configuring-instance-metadata-service.md).

**If IMDSv2 is required, IMDSv1 does not work**
If you use IMDSv1 and receive no response, it's likely that IMDSv2 is required. To check whether IMDSv2 is required, select the instance to view its details. The **IMDSv2** value indicates either **Required** (you must use IMDSv2) or **Optional** (you can use either IMDSv2 or IMDSv1).

**(IMDSv2) Use /latest/api/token to retrieve the token**
Issuing `PUT` requests to any version-specific path, for example `/2021-03-23/api/token`, results in the metadata service returning 403 Forbidden errors. This behavior is intended.

**Metadata version**
To avoid having to update your code every time Amazon EC2 releases a new instance metadata build, we recommend that you use `latest` in the path, and not the version number.

**IPv6 support**
To retrieve instance metadata using an IPv6 address, ensure that you enable and use the IPv6 address of the IMDS `[fd00:ec2::254]` instead of the IPv4 address `169.254.169.254`. The instance must be a [Nitro-based instance](instance-types.md#instance-hypervisor-type) launched in a [subnet that supports IPv6](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html#subnet-ip-address-range).

**(Windows) Create custom AMIs using Windows Sysprep**
To ensure that IMDS works when you launch an instance from a custom Windows AMI, the AMI must be a standardized image created with Windows Sysprep. Otherwise, the IMDS won't work. For more information, see [Create an Amazon EC2 AMI using Windows Sysprep](ami-create-win-sysprep.md).

**In a container environment, consider reconfiguration or increasing the hop limit to 2**
The AWS SDKs use IMDSv2 calls by default. If the IMDSv2 call receives no response, some AWS SDKs retry the call and, if still unsuccessful, use IMDSv1. This can result in a delay, especially in a container environment. For those AWS SDKs that *require* IMDSv2, if the hop limit is 1 in a container environment, the call might not receive a response at all because going to the container is considered an additional network hop.
To mitigate these issues in a container environment, consider changing the configuration to pass settings (such as the AWS Region) directly to the container, or consider increasing the hop limit to 2. For information about the hop limit impact, see [Add defense in depth against open firewalls, reverse proxies, and SSRF vulnerabilities with enhancements to the EC2 Instance Metadata Service](https://aws.amazon.com/blogs/security/defense-in-depth-open-firewalls-reverse-proxies-ssrf-vulnerabilities-ec2-instance-metadata-service/). For information about changing the hop limit, see [Change the PUT response hop limit](configuring-IMDS-existing-instances.md#modify-PUT-response-hop-limit).

**Packets per second (PPS) limit**
There is a 1024 packet per second (PPS) limit to services that use [link-local](using-instance-addressing.md#link-local-addresses) addresses. This limit includes the aggregate of [Route 53 Resolver DNS Queries](https://docs.aws.amazon.com/vpc/latest/userguide/AmazonDNS-concepts.html#vpc-dns-limits), Instance Metadata Service (IMDS) requests, [Amazon Time Service Network Time Protocol (NTP)](set-time.md) requests, and [Windows Licensing Service (for Microsoft Windows based instances)](https://aws.amazon.com/windows/resources/licensing/) requests.

**Additional considerations for user data access**
+ User data is treated as opaque data: what you specify is what you get back upon retrieval. It is up to the instance to interpret and act on user data.
+ User data must be base64-encoded. Depending on the tool or SDK that you're using, the base64-encoding might be performed for you. For example:
  + The Amazon EC2 console can perform the base64-encoding for you or accept base64-encoded input.
  + [AWS CLI version 2](https://docs.aws.amazon.com/cli/latest/userguide/cliv2-migration-changes.html#cliv2-migration-binaryparam) performs base64-encoding of binary parameters for you by default. AWS CLI version 1 performs the base64-encoding of the `--user-data` parameter for you.
  + The AWS SDK for Python (Boto3) performs base64-encoding of the `UserData` parameter for you.
+ User data is limited to 16 KB, in raw form, before it is base64-encoded. The size of a string of length *n* after base64-encoding is ceil(*n*/3)\*4.
+ User data must be base64-decoded when you retrieve it. If you retrieve the data using instance metadata or the console, it's decoded for you automatically.
+ If you stop an instance, modify its user data, and start the instance, the updated user data is not run automatically when you start the instance. With Windows instances, you can configure settings so that updated user data scripts are run one time when you start the instance or every time you reboot or start the instance.
+ User data is an instance attribute. If you create an AMI from an instance, the instance user data is not included in the AMI.

## Access instance metadata from within an EC2 instance

Because your instance metadata is available from your running instance, you do not need to use the Amazon EC2 console or the AWS CLI. This can be helpful when you're writing scripts to run from your instance. For example, you can access the local IP address of your instance from instance metadata to manage a connection to an external application.

All of the following are considered instance metadata, but they are accessed in different ways. Select the tab that represents the type of instance metadata you want to access to see more information.

------
#### [ Metadata ]

Instance metadata properties are divided into categories. For a description of each instance metadata category, see [Instance metadata categories](ec2-instance-metadata.md#instancedata-data-categories).

To access instance metadata properties from within a running instance, get the data from the following IPv4 or IPv6 URIs. These IP addresses are link-local addresses and are valid only from the instance. For more information, see [Link-local addresses](using-instance-addressing.md#link-local-addresses).

**IPv4**

```
http://169.254.169.254/latest/meta-data/
```

**IPv6**

```
http://[fd00:ec2::254]/latest/meta-data/
```

------
#### [ Dynamic data ]

To retrieve dynamic data from within a running instance, use one of the following URIs.

**IPv4**

```
http://169.254.169.254/latest/dynamic/
```

**IPv6**

```
http://[fd00:ec2::254]/latest/dynamic/
```

**Examples: Access with cURL**
The following examples use `cURL` to retrieve the high-level instance identity categories.

*IMDSv2*

```
[ec2-user ~]$ TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` \
&& curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/dynamic/instance-identity/
rsa2048
pkcs7
document
signature
dsa2048
```

*IMDSv1*

```
[ec2-user ~]$ curl http://169.254.169.254/latest/dynamic/instance-identity/
rsa2048
pkcs7
document
signature
dsa2048
```

**Examples: Access with PowerShell**
The following examples use PowerShell to retrieve the high-level instance identity categories.

*IMDSv2*

```
PS C:\> [string]$token = Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token-ttl-seconds" = "21600"} -Method PUT -Uri http://169.254.169.254/latest/api/token
```

```
PS C:\> Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token" = $token} -Method GET -Uri http://169.254.169.254/latest/dynamic/instance-identity/
document
rsa2048
pkcs7
signature
```

*IMDSv1*

```
PS C:\> Invoke-RestMethod -uri http://169.254.169.254/latest/dynamic/instance-identity/
document
rsa2048
pkcs7
signature
```

For more information about dynamic data and examples of how to retrieve it, see [Instance identity documents for Amazon EC2 instances](instance-identity-documents.md).

------
#### [ User data ]

To retrieve user data from an instance, use one of the following URIs. To retrieve user data using the IPv6 address, you must enable it, and the instance must be a [Nitro-based instance](instance-types.md#instance-hypervisor-type) in a subnet that supports IPv6.

**IPv4**

```
http://169.254.169.254/latest/user-data
```

**IPv6**

```
http://[fd00:ec2::254]/latest/user-data
```

A request for user data returns the data as it is (content type `application/octet-stream`). If the instance does not have any user data, the request returns `404 - Not Found`.

**Examples: Access with cURL to retrieve comma-separated text**
The following examples use `cURL` to retrieve user data that was specified as comma-separated text.

*IMDSv2*

```
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` \
&& curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/user-data
1234,john,reboot,true | 4512,richard, | 173,,,
```

*IMDSv1*

```
curl http://169.254.169.254/latest/user-data
1234,john,reboot,true | 4512,richard, | 173,,,
```

**Examples: Access with PowerShell to retrieve comma-separated text**
The following examples use PowerShell to retrieve user data that was specified as comma-separated text.

*IMDSv2*

```
[string]$token = Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token-ttl-seconds" = "21600"} -Method PUT -Uri http://169.254.169.254/latest/api/token
```

```
Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token" = $token} -Method GET -Uri http://169.254.169.254/latest/user-data
1234,john,reboot,true | 4512,richard, | 173,,,
```

*IMDSv1*

```
Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token" = Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token-ttl-seconds" = "21600"} `
-Method PUT -Uri http://169.254.169.254/latest/api/token} -Method GET -uri http://169.254.169.254/latest/user-data
1234,john,reboot,true | 4512,richard, | 173,,,
```

**Examples: Access with cURL to retrieve a script**
The following examples use `cURL` to retrieve user data that was specified as a script.

*IMDSv2*

```
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` \
&& curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/user-data
#!/bin/bash
yum update -y
service httpd start
chkconfig httpd on
```

*IMDSv1*

```
curl http://169.254.169.254/latest/user-data
#!/bin/bash
yum update -y
service httpd start
chkconfig httpd on
```

**Examples: Access with PowerShell to retrieve a script**
The following examples use PowerShell to retrieve user data that was specified as a script.

*IMDSv2*

```
[string]$token = Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token-ttl-seconds" = "21600"} -Method PUT -Uri http://169.254.169.254/latest/api/token
```

```
Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token" = $token} -Method GET -Uri http://169.254.169.254/latest/user-data

$file = $env:SystemRoot + "\Temp\" + (Get-Date).ToString("MM-dd-yy-hh-mm")
New-Item $file -ItemType file

true
```

*IMDSv1*

```
Invoke-RestMethod -uri http://169.254.169.254/latest/user-data

$file = $env:SystemRoot + "\Temp\" + (Get-Date).ToString("MM-dd-yy-hh-mm")
New-Item $file -ItemType file

true
```

------

## Query instance metadata options for existing instances

You can query the instance metadata options for your existing instances.

------
#### [ Console ]

**To query the instance metadata options for an existing instance**

1. Open the Amazon EC2 console at [https://console.aws.amazon.com/ec2/](https://console.aws.amazon.com/ec2/).

1. In the navigation pane, choose **Instances**.

1. Select your instance and check the following fields:
   + **IMDSv2** – The value is either **Required** or **Optional**.
   + **Allow tags in instance metadata** – The value is either **Enabled** or **Disabled**.

1. With your instance selected, choose **Actions**, **Instance settings**, **Modify instance metadata options**.

   The dialog box displays whether the instance metadata service is enabled or disabled for the selected instance.

------
#### [ AWS CLI ]

**To query the instance metadata options for an existing instance**
Use the [describe-instances](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html) command.

```
aws ec2 describe-instances \
    --instance-id {{i-1234567898abcdef0}} \
    --query 'Reservations[].Instances[].MetadataOptions'
```

------
#### [ PowerShell ]

**To query the instance metadata options for an existing instance using the Tools for PowerShell**
Use the [Get-EC2Instance](https://docs.aws.amazon.com/powershell/latest/reference/items/Get-EC2Instance.html) cmdlet.

```
(Get-EC2Instance `
    -InstanceId {{i-1234567898abcdef0}}).Instances.MetadataOptions
```

------

## Responses and error messages

All instance metadata is returned as text (HTTP content type `text/plain`).

A request for a specific metadata resource returns the appropriate value, or a `404 - Not Found` HTTP error code if the resource is not available.

A request for a general metadata resource (the URI ends with a /) returns a list of available resources, or a `404 - Not Found` HTTP error code if there is no such resource. The list items are on separate lines, terminated by line feeds (ASCII 10).

If an IMDSv1 request receives no response, it's likely that IMDSv2 is required.

For requests made using IMDSv2, the following HTTP error codes can be returned:
+ `400 - Missing or Invalid Parameters` – The `PUT` request is not valid.
+ `401 - Unauthorized` – The `GET` request uses an invalid token. The recommended action is to generate a new token.
+ `403 - Forbidden` – The request is not allowed or the IMDS is turned off.
+ `404 - Not Found` – The resource is not available or there is no such resource.
+ `503` – The request could not be completed. Retry the request.

If the IMDS returns an error, **curl** prints the error message in the output and returns a success status code. The error message is stored in the `TOKEN` variable, which causes **curl** commands that use the token to fail. If you call **curl** with the **-f** option, it returns an error status code in the event of an HTTP server error. If you enable error handling, the shell can catch the error and stop the script.

## Query throttling

We throttle queries to the IMDS on a per-instance basis, and we place limits on the number of simultaneous connections from an instance to the IMDS.

If you're using the IMDS to retrieve AWS security credentials, avoid querying for credentials during every transaction or concurrently from a high number of threads or processes, as this might lead to throttling. Instead, we recommend that you cache the credentials until they start approaching their expiry time. For more information about IAM role and security credentials associated with the role, see [Retrieve security credentials from instance metadata](instance-metadata-security-credentials.md).

If you are throttled while accessing the IMDS, retry your query with an exponential backoff strategy.
