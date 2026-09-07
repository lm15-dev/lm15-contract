Home

          Documentation

          Security

          IAM

          Reference

    Send feedback

      Method: token

      Stay organized with collections

      Save and categorize content based on your preferences.

        HTTP request

        Request body

            JSON representation

        Response body

            JSON representation

        Try it!

        Exchanges a credential for a Google OAuth 2.0 access token.
The token asserts an external identity within an identity pool, or it applies a Credential Access Boundary to a Google access token. Note that workforce pools do not support Credential Access Boundaries.
When you call this method, do not send the Authorization HTTP header in the request. This method does not require the Authorization header, and using the header can cause the request to fail.

          HTTP request

          POST https://sts.googleapis.com/v1/token
The URL uses gRPC Transcoding syntax.

          Request body

          The request body contains data with the following structure:

                  JSON representation

{
  "grantType": string,
  "audience": string,
  "scope": string,
  "requestedTokenType": string,
  "subjectToken": string,
  "subjectTokenType": string,
  "options": string
}

                  Fields

                  grantType

                    string

                    Required. The grant type. Must be urn:ietf:params:oauth:grant-type:token-exchange, which indicates a token exchange.

                  audience

                    string

                    The full resource name of the identity provider; for example: //iam.googleapis.com/projects/<project-number>/locations/global/workloadIdentityPools/<pool-id>/providers/<provider-id> for workload identity pool providers, or //iam.googleapis.com/locations/global/workforcePools/<pool-id>/providers/<provider-id> for workforce pool providers. Required when exchanging an external credential for a Google access token.

                  scope

                    string

                    The OAuth 2.0 scopes to include on the resulting access token, formatted as a list of space-delimited, case-sensitive strings; for example, https://www.googleapis.com/auth/cloud-platform. Required when exchanging an external credential for a Google access token. For a list of OAuth 2.0 scopes, see OAuth 2.0 Scopes for Google APIs.

                  requestedTokenType

                    string

                    Required. An identifier for the type of requested security token. Can be urn:ietf:params:oauth:token-type:access_token or urn:ietf:params:oauth:token-type:access_boundary_intermediary_token.

                  subjectToken

                    string

                    Required. The input token.
This token is either an external credential issued by a workload identity  pool provider, or a short-lived access token issued by Google.
If the token is an OIDC JWT, it must use the JWT format defined in  RFC 7523, and the  subjectTokenType must be either urn:ietf:params:oauth:token-type:jwt  or urn:ietf:params:oauth:token-type:idToken.
The following headers are required:

                      kid: The identifier of the signing key securing the JWT.

                      alg: The cryptographic algorithm securing the JWT. Must be RS256 or  ES256.

                    The following payload fields are required. For more information, see  RFC 7523, Section 3:

                      iss: The issuer of the token. The issuer must provide a discovery  document at the URL <iss>/.well-known/openid-configuration, where  <iss> is the value of this field. The document must be formatted  according to section 4.2 of the  OIDC 1.0 Discovery  specification.

                      iat: The issue time, in seconds, since the Unix epoch. This timestamp  must be in the past and no more than 24 hours in the past, or the token  will be rejected. Note that this implies the token is only acceptable  within a time window of at most 24 hours.

                      exp: The expiration time, in seconds, since the Unix epoch. Shorter  expiration times are more secure. If possible, we recommend setting an  expiration time less than 6 hours.

                      sub: The identity asserted in the JWT.

                      aud: For workload identity pools, this must be a value specified in  the allowed audiences for the workload identity pool provider, or one of  the audiences allowed by default if no audiences were specified. See  https://cloud.google.com/iam/docs/reference/rest/v1/projects.locations.workloadIdentityPools.providers#oidc.  For workforce pools, this must match the client ID specified in the  provider configuration. See  https://cloud.google.com/iam/docs/reference/rest/v1/locations.workforcePools.providers#oidc.

                    Example header:

 {
   "alg": "RS256",
   "kid": "us-east-11"
 }

                    Example payload:

 {
   "iss": "https://accounts.google.com",
   "iat": 1517963104,
   "exp": 1517966704,
   "aud":
   "//iam.googleapis.com/projects/1234567890123/locations/global/workloadIdentityPools/my-pool/providers/my-provider",
   "sub": "113475438248934895348",
   "my_claims": {
     "additional_claim": "value"
   }
 }

                    If subjectToken is for AWS, it must be a serialized GetCallerIdentity  token. This token contains the same information as a request to the AWS  GetCallerIdentity()  method, as well as the AWS  signature  for the request information. Use Signature Version 4. Format the request  as URL-encoded JSON, and set the subjectTokenType parameter to  urn:ietf:params:aws:token-type:aws4_request.
The following parameters are required:

                      url: The URL of the AWS STS endpoint for GetCallerIdentity(), such  as  https://sts.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15.  Regional endpoints are also supported.

                      method: The HTTP request method: POST.

                      headers: The HTTP request headers, which must include:

                        Authorization: The request signature.

                        x-amz-date: The time you will send the request, formatted as an  ISO8601  Basic  string. This value is typically set to the current time and is used  to help prevent replay attacks.

                        host: The hostname of the url field; for example,  sts.amazonaws.com.

                        x-goog-cloud-target-resource: The full, canonical resource name of  the workload identity pool provider, with or without an https:  prefix. To help ensure data integrity, we recommend including this  header in the SignedHeaders field of the signed request. For  example:

   //iam.googleapis.com/projects/<project-number>/locations/global/workloadIdentityPools/<pool-id>/providers/<provider-id>
   https://iam.googleapis.com/projects/<project-number>/locations/global/workloadIdentityPools/<pool-id>/providers/<provider-id>

                    If you are using temporary security credentials provided by AWS, you must  also include the header x-amz-security-token, with the value set to the  session token.
The following example shows a GetCallerIdentity token:

 {
   "headers": [
     {"key": "x-amz-date", "value": "20200815T015049Z"},
     {"key": "Authorization",
      "value":
      "AWS4-HMAC-SHA256+Credential=$credential,+SignedHeaders=host;x-amz-date;x-goog-cloud-target-resource,+Signature=$signature"},
     {"key": "x-goog-cloud-target-resource",
      "value":
      "//iam.googleapis.com/projects/<project-number>/locations/global/workloadIdentityPools/<pool-id>/providers/<provider-id>"},
     {"key": "host", "value": "sts.amazonaws.com"}
.  ],
   "method": "POST",
   "url":
   "https://sts.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15"
 }

                    If the token is a SAML 2.0 assertion, it must use the format defined in  the SAML 2.0  spec,  and the subjectTokenType must be  urn:ietf:params:oauth:token-type:saml2. See  Verification of external  credentials  for details on how SAML 2.0 assertions are validated during token  exchanges.
You can also use a Google-issued OAuth 2.0 access token with this field  to obtain an access token with new security attributes applied, such as a  Credential Access Boundary. In this case, set subjectTokenType to  urn:ietf:params:oauth:token-type:access_token.
If an access token already contains security attributes, you cannot apply  additional security attributes.
If the request is for X.509 certificate-based authentication, the  subjectToken must be a JSON-formatted list of X.509 certificates in DER  format, as defined in RFC  7515.  subjectTokenType must be urn:ietf:params:oauth:token-type:mtls.  The following example shows a JSON-formatted list of X.509 certificate in  DER format:

 [\"MIIEYDCCA0i...\", \"MCIFFGAGTT0...\"]

                  subjectTokenType

                    string

                    Required. An identifier that indicates the type of the security token in the subjectToken parameter. Supported values are urn:ietf:params:oauth:token-type:jwt, urn:ietf:params:oauth:token-type:id_token, urn:ietf:params:aws:token-type:aws4_request, urn:ietf:params:oauth:token-type:access_token, urn:ietf:params:oauth:token-type:mtls, and urn:ietf:params:oauth:token-type:saml2.

                  options

                    string

                    A set of features that Security Token Service supports, in addition to the standard OAuth 2.0 token exchange, formatted as a serialized JSON object of Options.
The size of the parameter value must not exceed 4 * 1024 * 1024 characters (4 MB).

          Response body

              Response message for v1.token.

              If successful, the response body contains data with the following structure:

                    JSON representation

{
  "access_token": string,
  "issued_token_type": string,
  "token_type": string,
  "expires_in": integer,
  "access_boundary_session_key": string
}

                    Fields

                    access_token

                      string

                      An OAuth 2.0 security token, issued by Google, in response to the token exchange request.
Tokens can vary in size, depending in part on the size of mapped claims, up to a maximum of 12288 bytes (12 KB). Google reserves the right to change the token size and the maximum length at any time.

                    issued_token_type

                      string

                      The token type. Always matches the value of requestedTokenType from the request.

                    token_type

                      string

                      The type of access token. Always has the value Bearer.

                    expires_in

                      integer

                      The amount of time, in seconds, between the time when the access token was issued and the time when the access token will expire.
This field is absent when the subjectToken in the request is a a short-lived access token for a Cloud Identity or Google Workspace user account. In this case, the access token has the same expiration time as the subjectToken.

                    access_boundary_session_key

                      string (bytes format)

                      The access boundary session key. This key is used along with the access boundary intermediary token to generate Credential Access Boundary tokens at client side.
This field is absent when the requestedTokenType from the request is not urn:ietf:params:oauth:token-type:access_boundary_intermediary_token.
A base64-encoded string.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-03-13 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-13 UTC."],[],[]]
