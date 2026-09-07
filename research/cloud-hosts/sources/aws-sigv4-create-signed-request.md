# Create a signed AWS API request

**Important**
If you use an AWS SDK (see [Sample Code and Libraries](https://aws.amazon.com/developer/)) or AWS Command Line Interface (AWS CLI) tool to send API requests to AWS, you can skip this section because the SDK and CLI clients authenticate your requests by using the access keys that you provide. Unless you have a good reason not to, we recommend that you always use an SDK or the CLI.
In Regions that support multiple signature versions, manually signing requests means you must specify which signature version is used. When you supply requests to Multi-Region Access Points, SDKs and the CLI automatically switch to using Signature Version 4A without additional configuration.

You can use the AWS SigV4 signing protocol to create a signed request for AWS API requests.

1. Creating a canonical request based on the request details.

1. Calculating a signature using your AWS credentials.

1. Adding this signature to the request as an Authorization header.

AWS then replicates this process and verifies the signature, granting or denying access accordingly.

To see how you can use AWS SigV4 to sign API requests, see [Request signature examples](reference_sigv-examples.md).

The following table describes the functions that are used in the process of creating a signed request. You need to implement code for these functions. For more information, see the [code examples in the AWS SDKs](reference_sigv.md#reference_aws-signing-resources).

| Function | Description |
| --- | --- |
| `Lowercase()` | Convert the string to lowercase. |
| `Hex()` | Lowercase base 16 encoding. |
| `SHA256Hash()` | Secure Hash Algorithm (SHA) cryptographic hash function. |
| `HMAC-SHA256()` | Computes HMAC by using the SHA256 algorithm with the signing key provided. This is the final signature when you sign with SigV4. |
| `ECDSA-Sign` | Elliptic Curve Digital Signature Algorithm (ECDSA) signature computed by using asymmetric signatures based on public-private key cryptography.  |
| `KDF(K, Label, Context, L)` | A NIST SP800-108 KDF in Counter Mode using the PRF function HMAC-SHA256 as defined in [NIST SP 800-108r1](https://doi.org/10.6028/NIST.SP.800-108r1-upd1). |
| `Oct2Int(byte[ ])` | An octet to integer function as described in ANSI X9.62. |
| `Trim()` | Remove any leading or trailing whitespace. |
| `UriEncode()` | URI encode every byte. UriEncode() must enforce the following rules:+  URI encode every byte except the unreserved characters: 'A'-'Z', 'a'-'z', '0'-'9', '-', '.', '\_', and '\~'.
+  The space character is a reserved character and must be encoded as "%20" (and not as "\+").
+  Each URI encoded byte is formed by a '%' and the two-digit hexadecimal value of the byte.
+  Letters in the hexadecimal value must be uppercase, for example "%1A".
+  Encode the forward slash character, '/', everywhere except in the object key name. For example, if the object key name is `photos/Jan/sample.jpg`, the forward slash in the key name is not encoded.   The standard UriEncode functions provided by your development platform might not work because of differences in implementation and related ambiguity in the underlying RFCs. We recommend that you write your own custom UriEncode function to make sure that your encoding will work.
To see an example of a UriEncode function in Java, see [Java Utilities](https://github.com/aws/aws-sdk-java/blob/master/aws-java-sdk-core/src/main/java/com/amazonaws/util/SdkHttpUtils.java#L66) on the GitHub website. |

**Note**
When signing your requests, you can use either AWS SigV4 or AWS SigV4a. The key difference between the two is determined by how the signature is calculated. With SigV4a, the region set is included in the string to sign, but is not part of the credential derivation step.

## Signing requests with temporary security credentials

Instead of using long-term credentials to sign a request, you can use temporary security credentials provided by AWS Security Token Service (AWS STS).

When you use temporary security credentials, you must add `X-Amz-Security-Token` to the Authorization header or include it in the query string to hold the session token. Some services require that you add `X-Amz-Security-Token` to the canonical request. Other services require only that you add `X-Amz-Security-Token` at the end, after you calculate the signature. Check the documentation for each AWS service for specific requirements.

## Summary of signing steps

**Create a canonical request**
Arrange the contents of your request (host, action, headers, etc.) into a standard canonical format. The canonical request is one of the inputs used to create the string to sign. For details on creating the canonical request, see [Elements of an AWS API request signature](reference_sigv-signing-elements.md).

**Create a hash of the canonical request**
Hash the canonical request using the same algorithm that you used to create the hash of the payload. The hash of the canonical request is a string of lowercase hexadecimal characters.

**Create a string to sign**
Create a string to sign with the canonical request and extra information such as the algorithm, request date, credential scope, and the hash of the canonical request.

**Derive a signing key**
Use the secret access key to derive the key used to sign the request.

**Calculate the signature**
Perform a keyed hash operation on the string to sign using the derived signing key as the hash key.

**Add the signature to the request**
Add the calculated signature to an HTTP header or to the query string of the request.

## Create a canonical request

To create a canonical request, concatenate the following strings, separated by newline characters. This helps make sure that the signature that you calculate can match the signature that AWS calculates.

```
{{}}\n
{{}}\n
{{}}\n
{{}}\n
{{}}\n
{{}}
```
+ {{HTTPMethod}} – The HTTP method, such as `GET`, `PUT`, `HEAD`, and `DELETE`.
+ {{CanonicalUri}} – The URI-encoded version of the absolute path component URI, starting with the `/` that follows the domain name and up to the end of the string or to the question mark character (`?`) if you have query string parameters. If the absolute path is empty, use a forward slash character (`/`). The URI in the following example, `/amzn-s3-demo-bucket/myphoto.jpg`, is the absolute path and you don't encode the `/` in the absolute path:

  ```
  http://s3.amazonaws.com/amzn-s3-demo-bucket/myphoto.jpg
  ```
+ {{CanonicalQueryString}} – The URI-encoded query string parameters. You URI-encode each name and value individually. You must also sort the parameters in the canonical query string alphabetically by key name. The sorting occurs after encoding. The query string in the following URI example is:

  ```
  http://s3.amazonaws.com/amzn-s3-demo-bucket?prefix=somePrefix&marker=someMarker&max-keys=2
  ```

  The canonical query string is as follows (line breaks are added to this example for readability):

  ```
  UriEncode("marker")+"="+UriEncode("someMarker")+"&"+
  UriEncode("max-keys")+"="+UriEncode("20") + "&" +
  UriEncode("prefix")+"="+UriEncode("somePrefix")
  ```

  When a request targets a subresource, the corresponding query parameter value will be an empty string (`""`). For example, the following URI identifies the `ACL` subresource on the `amzn-s3-demo-bucket` bucket:

  ```
  http://s3.amazonaws.com/amzn-s3-demo-bucket?acl
  ```

  In this case, the CanonicalQueryString would be:

  ```
  UriEncode("acl") + "=" + ""
  ```

  If the URI does not include a `?`, there is no query string in the request, and you set the canonical query string to an empty string (`""`). You will still need to include the newline character (`"\n"`).
+ {{CanonicalHeaders}} – A list of request headers with their values. Individual header name and value pairs are separated by the newline character (`"\n"`). The following is an example of a CanonicalHeader:

  ```
  Lowercase({{}})+":"+Trim({{}})+"\n"
  Lowercase({{}})+":"+Trim({{}})+"\n"
  ...
  Lowercase({{}})+":"+Trim({{}})+"\n"
  ```

  CanonicalHeaders list must include the following:
  + HTTP `host` header.
  + If the `Content-Type` header is present in the request, you must add it to the {{CanonicalHeaders}} list.
  + Any `x-amz-*` headers that you plan to include in your request must also be added. For example, if you are using temporary security credentials, you need to include `x-amz-security-token` in your request. You must add this header in the list of {{CanonicalHeaders}}.
  + For SigV4a, you must include a region set header that specifies the set of regions the request will be valid in. The header `X-Amz-Region-Set` is specified as a list of comma separated values. The following example shows a region header that allows a request to be made in both us-east-1 and us-west-1 regions.

    `X-Amz-Region-Set=us-east-1,us-west-1 `

    You can use wildcards (\*) in regions to specify multiple regions. In the following example, the header allows a request to be made in both us-west-1 and us-west-2.

    `X-Amz-Region-Set=us-west-*`
**Note**
The `x-amz-content-sha256` header is required for Amazon S3 AWS requests. It provides a hash of the request payload. If there is no payload, you must provide the hash of an empty string.

  Each header name must:
  + use lowercase characters.
  + appear in alphabetical order.
  + be followed by a colon (`:`).

  For values, you must:
  + trim any leading or trailing spaces.
  + convert sequential spaces to a single space.
  + separate the values for a multi-value header using commas.
  + You must include the host header (HTTP/1.1) or the :authority header (HTTP/2), and any `x-amz-*` headers in the signature. You can optionally include other standard headers in the signature, such as content-type.

  The `Lowercase()` and `Trim()` functions used in this example are described in the preceding section.

  The following is an example `CanonicalHeaders` string. The header names are in lowercase and sorted.

  ```
  host:s3.amazonaws.com
  x-amz-content-sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  x-amz-date:20130708T220855Z
  ```

**Note**
For the purpose of calculating an authorization signature, only the host and any `x-amz-*` headers are required; however, in order to prevent data tampering, you should consider including additional headers in the signature calculation.
Do not include hop-by-hop headers that are frequently altered during transit across a complex system. This includes all volatile transport headers that are mutated by proxies, load balancers, and the nodes in a distributed system, including `connection`, `x-amzn-trace-id`, `user-agent`, `keep-alive`, `transfer-encoding`, `TE`, `trailer`, `upgrade`, `proxy-authorization`, and `proxy-authenticate`.
+ {{SignedHeaders}} – An alphabetically sorted, semicolon-separated list of lowercase request header names. The request headers in the list are the same headers that you included in the `CanonicalHeaders` string. For the previous example, the value of {{SignedHeaders}} would be as follows:

  ```
  host;x-amz-content-sha256;x-amz-date
  ```
+ {{HashedPayload}} – A string created using the payload in the body of the HTTP request as input to a hash function. This string uses lowercase hexadecimal characters.

  ```
  Hex(SHA256Hash({{}}>))
  ```

  If there is no payload in the request, you compute a hash of the empty string, such as when you retrieve an object by using a `GET` request, there is nothing in the payload.

  ```
  Hex(SHA256Hash(""))
  ```
**Note**
For Amazon S3, include the literal string `UNSIGNED-PAYLOAD` when constructing a canonical request, and set the same value as the `x-amz-content-sha256` header value when sending the request.
`Hex(SHA256Hash("UNSIGNED-PAYLOAD"))`

## Create a hash of the canonical request

Create a hash (digest) of the canonical request using the same algorithm that you used to create the hash of the payload. The hash of the canonical request is a string of lowercase hexadecimal characters.

## Create a string to sign

To create a string to sign, concatenate the following strings, separated by newline characters. Do not end this string with a newline character.

```
{{Algorithm}} \n
{{RequestDateTime}} \n
{{CredentialScope}}  \n
{{HashedCanonicalRequest}}
```
+ {{Algorithm}} – The algorithm used to create the hash of the canonical request.
  + SigV4 – Use `AWS4-HMAC-SHA256` to specify the `HMAC-SHA256` hash algorithm.
  + SigV4a – Use `AWS4-ECDSA-P256-SHA256` to specify the `ECDSA-P256-SHA-256` hash algorithm.
+ {{RequestDateTime}} – The date and time used in the credential scope. This value is the current UTC time in ISO 8601 format (for example, `20130524T000000Z`).
+ {{CredentialScope}} – The credential scope, which restricts the resulting signature to the specified Region and service.
  + SigV4 – Credentials include your access key ID, the date in `YYYYMMDD` format, the Region code, the service code, and the `aws4_request` termination string, separated by slashes (/). The Region code, service code, and termination string must use lowercase characters. The string has the following format: `YYYYMMDD/region/service/aws4_request`.
  + SigV4a – Credentials include the date in `YYYYMMDD` format, the service name, and the `aws4_request` termination string, separated by slashes (/). Note that credential scope does not include the region as the region is covered in a separate header `X-Amz-Region-Set`. The string has the following format: `YYYYMMDD/service/aws4_request`.
+ {{HashedCanonicalRequest}} – The hash of the canonical request, calculated in the previous step.

The following is an example string to sign.

```
"{{}}" + "\n" +
timeStampISO8601Format + "\n" +
{{}} + "\n" +
Hex({{}}({{}}))
```

## Derive a signing key

To derive a signing key, choose one of the following processes to compute a signing key for either SigV4 or SigV4a.

### Deriving a signing key for SigV4

To derive a signing key for SigV4, perform a succession of keyed hash operations (HMAC) on the request date, Region, and service, with your AWS secret access key as the key for the initial hashing operation.

For each step, call the hash function with the required key and data. The result of each call to the hash function becomes the input for the next call to the hash function.

The following example shows how you derive the `SigningKey` used in the next section of this procedure, showing the order in which your input is concatenated and hashed. `HMAC-SHA256` is the hash function used to hash the data as shown.

```
DateKey = HMAC-SHA256("AWS4"+"{{}}", "{{}}")
DateRegionKey = HMAC-SHA256({{}}, "{{}}")
DateRegionServiceKey = HMAC-SHA256({{}}, "{{}}")
SigningKey = HMAC-SHA256({{}}, "aws4_request")
```

**Required input**
+ `Key` – A string that contains your secret access key.
+ `Date` – A string that contains the date used in the credential scope, in the format *YYYYMMDD*.
+ `Region` – A string that contains the Region code (for example, `us-east-1`).

  For a list of Region strings, see [Regional Endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html#regional-endpoints) in the *AWS General Reference*.
+ `Service` – A string that contains the service code (for example, `ec2`).
+ The string to sign that you created in the previous step.

**To derive a signing key for SigV4**

1. Concatenate `"AWS4"` and the secret access key. Call the hash function with the concatenated string as the key and the date string as the data.

   ```
   DateKey = hash("AWS4" + Key, Date)
   ```

1. Call the hash function with the result of the previous call as the key and the Region string as the data.

   ```
   DateRegionKey = hash(kDate, Region)
   ```

1. Call the hash function with the result of the previous call as the key and the service string as the data.

   The service code is defined by the service. You can use [get-products](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/pricing/get-products.html) in the *AWS Pricing CLI* to return the service code for a service.

   ```
   DateRegionServiceKey = hash(kRegion, Service)
   ```

1. Call the hash function with the result of the previous call as the key and "aws4\_request" as the data.

   ```
   SigningKey = hash(kService, "aws4_request")
   ```

### Deriving a signing key for SigV4a

To create a signing key for SigV4a, use the following process to derive a key pair from the secret access key. For an example of an implementation of this derivation, see the [C99 library implementation of AWS client-side authentication](https://github.com/awslabs/aws-c-auth/blob/e8360a65e0f3337d4ac827945e00c3b55a641a5f/source/key_derivation.c#L291.)

```
n = [NIST P-256 elliptic curve group order]
G = [NIST P-256 elliptic curve base point]
label = "AWS4-ECDSA-P256-SHA256"

akid = [AWS access key ID as a UTF8 string]
sk = [AWS secret access Key as a UTF8 Base64 string]

input_key = "AWS4A" || sk
count = 1
while (counter != 255) {
  context = akid || counter {{// note: counter is one byte}}
  key = KDF(input_key, label, context, 256)
  c = Oct2Int(key)
  if (c > n - 2) {
    counter++
  } else {
    k = c + 1   {{// private key}}
    Q = k * G   {{// public key}}
  }
}

if (c

After you have derived the signing key, calculate the signature to add to your request. This procedure varies based on the signature version you use.

**To calculate a signature for SigV4**

1. Call the hash function with the result of the previous call as the key and the **string to sign** as the data. Use the derived signing key as the hash key for this operation. The result is the signature as a binary value.

   ```
   signature = hash(SigningKey, {{string-to-sign}})
   ```

1. Convert the signature from binary to hexadecimal representation, in lowercase characters.

**To calculate a signature for SigV4a**

1. Using the digital signing algorithm (ECDSA P-256), sign the **string to sign** you created in the previous step. The key used for this signature is the private asymmetric key derived from the secret access key as described above.

   ```
   signature = base16({{ECDSA-Sign}}(k, {{string-to-sign}}))
   ```

1. Convert the signature from binary to hexadecimal representation, in lowercase characters.

## Add the signature to the request

Add the calculated signature to your request.

**Example: Authorization header**
**SigV4**
The following example shows an `Authorization` header for the `DescribeInstances` action using AWS SigV4. For readability, this example is formatted with line breaks. In your code, this must be a continuous string. There is no comma between the algorithm and `Credential`. However, the other elements must be separated by commas.

```
Authorization: AWS4-HMAC-SHA256
Credential=AKIAIOSFODNN7EXAMPLE/20220830/us-east-1/ec2/aws4_request,
SignedHeaders=host;x-amz-date,
Signature={{calculated-signature}}
```

**SigV4a**
The following example shows an Authorization header for the `CreateBucket` action using AWS SigV4a. For readability, this example is formatted with line breaks. In your code, this must be a continuous string. There is no comma between the algorithm and Credential. However, the other elements must be separated by commas.

```
Authorization: AWS4-ECDSA-P256-SHA256
Credential=AKIAIOSFODNN7EXAMPLE/20220830/s3/aws4_request,
SignedHeaders=host;x-amz-date;x-amz-region-set,
Signature={{calculated-signature}}
```

**Example: Request with authentication parameters in the query string**
**SigV4**
The following example shows a query for the `DescribeInstances` action using AWS SigV4 that includes the authentication information. For readability, this example is formatted with line breaks and is not URL encoded. In your code, the query string must be a continuous string that is URL encoded.

```
https://ec2.amazonaws.com/?
Action=DescribeInstances&
Version=2016-11-15&
X-Amz-Algorithm=AWS4-HMAC-SHA256&
X-Amz-Credential=AKIAIOSFODNN7EXAMPLE/20220830/us-east-1/ec2/aws4_request&
X-Amz-Date=20220830T123600Z&
X-Amz-SignedHeaders=host;x-amz-date&
X-Amz-Signature={{calculated-signature}}
```

**SigV4a**
The following example shows a query for the `CreateBucket` action using AWS SigV4a that includes the authentication information. For readability, this example is formatted with line breaks and is not URL encoded. In your code, the query string must be a continuous string that is URL encoded.

```
https://ec2.amazonaws.com/?
Action=CreateBucket&
Version=2016-11-15&
X-Amz-Algorithm=AWS4-ECDSA-P256-SHA256&
X-Amz-Credential=AKIAIOSFODNN7EXAMPLE/20220830/s3/aws4_request&
X-Amz-Region-Set=us-west-1&
X-Amz-Date=20220830T123600Z&
X-Amz-SignedHeaders=host;x-amz-date;x-amz-region-set&
X-Amz-Signature={{calculated-signature}}
```
