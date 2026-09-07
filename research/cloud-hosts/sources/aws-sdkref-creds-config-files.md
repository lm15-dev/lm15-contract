# Globally configuring AWS SDKs and tools

With AWS SDKs and other AWS developer tools, such as the AWS Command Line Interface (AWS CLI), you can interact with AWS service APIs. Before attempting that, however, you must configure the SDK or tool with the information that it needs to perform the requested operation.

This information includes the following items:
+ **Credentials information** that identifies who is calling the API. The credentials are used to encrypt the request to the AWS servers. Using this information, AWS confirms your identity and can retrieve permissions policies associated with it. Then it can determine what actions you're allowed to perform.
+ **Other configuration details** that you use to tell the AWS CLI or SDK how to process the request, where to send the request (to which AWS service endpoint), and how to interpret or display the response.

Each SDK or tool supports multiple sources that you can use to supply the required credential and configuration information. Some sources are unique to the SDK or tool, and you must refer to the documentation for that tool or SDK for the details on how to use that method.

However, the AWS SDKs and tools support common settings from primary sources beyond the code itself. This section covers the following topics:

**Topics**
+ [Using shared `config` and `credentials` files to globally configure AWS SDKs and tools](file-format.md)
+ [Finding and changing the location of the shared `config` and `credentials` files of AWS SDKs and tools](file-location.md)
+ [Using environment variables to globally configure AWS SDKs and tools](environment-variables.md)
+ [Using JVM system properties to globally configure AWS SDK for Java and AWS SDK for Kotlin](jvm-system-properties.md)
