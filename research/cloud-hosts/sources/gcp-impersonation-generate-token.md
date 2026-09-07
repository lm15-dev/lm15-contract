Home

          Documentation

          Security

          IAM

          Reference

    Send feedback

      Method: projects.serviceAccounts.generateAccessToken

      Stay organized with collections

      Save and categorize content based on your preferences.

        HTTP request

        Path parameters

        Request body

            JSON representation

        Response body

            JSON representation

        Authorization scopes

        Try it!

        Generates an OAuth 2.0 access token for a service account.

          HTTP request

          POST https://iamcredentials.googleapis.com/v1/{name=projects/*/serviceAccounts/*}:generateAccessToken
The URL uses gRPC Transcoding syntax.

          Path parameters

                Parameters

                name

                  string

                  Required. The resource name of the service account for which the credentials are requested, in the following format: projects/-/serviceAccounts/{ACCOUNT_EMAIL_OR_UNIQUEID}. The - wildcard character is required; replacing it with a project ID is invalid.

                  Authorization requires the following IAM permission on the specified resource name:

                    iam.serviceAccounts.getAccessToken

          Request body

          The request body contains data with the following structure:

                  JSON representation

{
  "delegates": [
    string
  ],
  "scope": [
    string
  ],
  "lifetime": string
}

                  Fields

                  delegates[]

                    string

                    The sequence of service accounts in a delegation chain. This field is required for delegated requests. For direct requests, which are more common, do not specify this field.
Each service account must be granted the roles/iam.serviceAccountTokenCreator role on its next service account in the chain. The last service account in the chain must be granted the roles/iam.serviceAccountTokenCreator role on the service account that is specified in the name field of the request.
The delegates must have the following format: projects/-/serviceAccounts/{ACCOUNT_EMAIL_OR_UNIQUEID}. The - wildcard character is required; replacing it with a project ID is invalid.

                  scope[]

                    string

                    Required. Code to identify the scopes to be included in the OAuth 2.0 access token. See https://developers.google.com/identity/protocols/googlescopes for more information. At least one value required.

                  lifetime

                    string (Duration format)

                    The desired lifetime duration of the access token in seconds.
By default, the maximum allowed value is 1 hour. To set a lifetime of up to 12 hours, you can add the service account as an allowed value in an Organization Policy that enforces the constraints/iam.allowServiceAccountCredentialLifetimeExtension constraint. See detailed instructions at https://cloud.google.com/iam/help/credentials/lifetime
If a value is not specified, the token's lifetime will be set to a default value of 1 hour.
A duration in seconds with up to nine fractional digits, ending with 's'. Example: "3.5s".

          Response body

              If successful, the response body contains data with the following structure:

                    JSON representation

{
  "accessToken": string,
  "expireTime": string
}

                    Fields

                    accessToken

                      string

                      The OAuth 2.0 access token.

                    expireTime

                      string (Timestamp format)

                      Token expiration time. The expiration time is always set.
Uses RFC 3339, where generated output will always be Z-normalized and uses 0, 3, 6 or 9 fractional digits. Offsets other than "Z" are also accepted. Examples: "2014-10-02T15:01:23Z", "2014-10-02T15:01:23.045123456Z" or "2014-10-02T15:01:23+05:30".

          Authorization scopes

          Requires one of the following OAuth scopes:

            https://www.googleapis.com/auth/iam

            https://www.googleapis.com/auth/cloud-platform

          For more information, see the Authentication Overview.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2025-05-21 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2025-05-21 UTC."],[],[]]
