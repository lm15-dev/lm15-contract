Home

          Products

          Google Identity

          Authorization

          Google Account Authorization

    Send feedback

      Using OAuth 2.0 for Server to Server Applications

      Stay organized with collections

      Save and categorize content based on your preferences.

      Page Summary

        outlined_flag

          The Google OAuth 2.0 system supports server-to-server interactions using a service account, which acts on behalf of the application rather than an end user.

          Service accounts are typically used when an application accesses its own data via Google APIs, or when a Google Workspace administrator grants domain-wide authority to access user data on behalf of users.

          To implement server-to-server OAuth 2.0, you need to create a service account with associated credentials, optionally delegate domain-wide authority, and then use these credentials to request and use access tokens to call Google APIs.

          While direct HTTP interaction is possible for requesting access tokens, using Google APIs client libraries is strongly recommended due to the complexity and security risks associated with creating and signing JSON Web Tokens (JWTs).

          Some Google APIs allow authorized calls directly with a signed JWT as a bearer token, bypassing the need for an OAuth 2.0 access token request.

Important: If you are working with Google Cloud, unless you plan
  to build your own client library, use service accounts and a Cloud Client Library instead of
  performing authorization explicitly as described in this document. For more information, see
  Authentication Overview
  in the Google Cloud documentation.

  The Google OAuth 2.0 system supports server-to-server interactions such as those between a web
    application and a Google service. For this scenario you need a service account, which
    is an account that belongs to your application instead of to an individual end user. Your
    application calls Google APIs on behalf of the service account, so users aren't directly
    involved. This scenario is sometimes called "two-legged OAuth," or "2LO." (The related term
    "three-legged OAuth" refers to scenarios in which your application calls Google APIs on behalf
    of end users, and in which user consent is sometimes required.)

  See
    Best practices for service accounts for more information.

  Typically, an application uses a service account when the application uses Google APIs to work
    with its own data rather than a user's data. For example, an application that uses Google Cloud
    Datastore for data persistence would use a service account to authenticate its calls to the
    Google Cloud Datastore API.

  Google Workspace domain administrators can also
    grant service accounts domain-wide authority to access user
    data on behalf of users in the domain.

  This document describes how an application can complete the server-to-server OAuth 2.0 flow by
    using either a Google APIs client library (recommended) or HTTP.

  With some Google APIs, you can make authorized API calls using a signed JWT instead of
    using OAuth 2.0, which can save you a network request. See
    Addendum: Service account authorization without OAuth.

  Overview

  To support server-to-server interactions, first create a service account for your project in
    the API Console. If you want to access user data for users in
    your Google Workspace account, then delegate domain-wide access to the service account.

  Then, your application prepares to make authorized API calls by using the service account's
    credentials to request an access token from the OAuth 2.0 auth server.

  Finally, your application can use the access token to call Google APIs.

  Recommendation: Your application can complete these tasks either by
    using the Google APIs client library for your language, or by directly interacting with the
    OAuth 2.0 system using HTTP. However, the mechanics of server-to-server authentication
    interactions require applications to create and cryptographically sign JSON Web Tokens (JWTs),
    mistakes can cause serious errors that can have a severe impact on the security of your
    application.

    For this reason, we strongly encourage you to use libraries, such as the Google APIs client
      libraries, that abstract the cryptography away from your application code.

  Create a service account

  A service account's credentials include a generated email address that is unique and at least
    one public/private key pair. If domain-wide delegation is enabled, then a client ID is also part
    of the service account's credentials.

  If your application runs on Google App Engine, a service account is set up automatically when
    you create your project.

  If your application runs on Google Compute Engine, a service account is also set up
    automatically when you create your project, but you must specify the scopes that your
    application needs access to when you create a Google Compute Engine instance. For more
    information, see
    Preparing an instance to use service accounts.

  If your application doesn't run on Google App Engine or Google Compute Engine, you must obtain
    these credentials in the Google API Console. To generate service-account
    credentials, or to view the public credentials that you've already generated, do the following:

First, create a service account:

  Open the Service accounts page.

  If prompted, select a project, or create a new one.

  Click add Create service
    account.

  Under Service account details, type a name, ID, and description for the service
    account, then click Create and continue.

  Optional: Under Grant this service account access to project, select the IAM roles to
    grant to the service account.

  Click Continue.

  Optional: Under Grant users access to this service account, add the users or groups
    that are allowed to use and manage the service account.

  Click Done.

Next, create a service account key:

  Click the email address for the service account you created.

  Click the Keys tab.

  In the Add key drop-down list, select Create new key.

  Click Create.

 Your new public/private key pair is generated and downloaded to your machine; it serves as
the only copy of the private key. You are responsible for storing it securely.
If you lose this key pair, you will need to generate a new one.

  To learn more, see

      Best practices for managing service account keys.

  You can return to the
    API Console at any time to view the email address, public
    key fingerprints, and other information, or to generate additional public/private key pairs. For
    more details about service account credentials in the
    API Console, see
    Service accounts in the API Console
    help file.

  Take note of the service account's email address and store the service account's private key
    file in a location accessible to your application. Your application needs them to make
    authorized API calls.

  Note: You must store and manage private keys securely in both
    development and production environments. Google does not keep a copy of your private keys, only
    your public keys. See the
    Handle client credentials securely section of OAuth 2.0 Policies for more information.

  Delegate domain-wide authority to the service account

  Using a Google Workspace account, a Workspace administrator of the organization can authorize an
    application to access Workspace user data on behalf of users in the Google Workspace domain. For example,
    an application that uses the Google Calendar API to add events to the calendars of all users in
    a Google Workspace domain would use a service account to access the Google Calendar API on
    behalf of users. Authorizing a service account to access data on behalf of users in a domain is
    sometimes referred to as "delegating domain-wide authority" to a service account.

  Note: When you use Google Workspace Marketplace to install an
    application for your domain, the required permissions are automatically granted to the
    application during installation. You don't need to manually authorize the service accounts that
    the application uses.

  Note: Although you can use service accounts in applications that run
    from a Google Workspace domain, service accounts are not members of your Google Workspace
    account and aren't subject to domain policies set by Google Workspace administrators. For
    example, a policy set in the Google Workspace Admin console to restrict the ability of
    Google Workspace end users to share documents outside of the domain wouldn't apply to service
    accounts.

  To delegate domain-wide authority to a service account, a super administrator of the Google
    Workspace domain must complete the following steps:

    From your Google Workspace domain's  Admin console,
      go to Main menu menu > Security >
        Access and data control > API Controls.

    In the Domain wide delegation pane, select Manage Domain Wide Delegation.

    Click Add new.

    In the Client ID field, enter the service account's Client ID. You can find
      your service account's client ID in the Service accounts page.

    In the OAuth scopes (comma-delimited) field, enter the list of scopes that your
      application should be granted access to. For example, if your application needs domain-wide
      full access to the Google Drive API and the Google Calendar API, enter:
      https://www.googleapis.com/auth/drive, https://www.googleapis.com/auth/calendar.

    Click Authorize.

  Your application now has the authority to make API calls as users in your Workspace domain (to
    "impersonate" users). When you prepare to make these delegated API calls, you will explicitly specify the user to
    impersonate.

  Note: It usually takes a few minutes for impersonation access to be
    granted after the client ID was added, but in some cases, it might take up to 24 hours to
    propagate to all users of your Google Account.

  Make a delegated API call

  The following sections show how to make an authorized API call using a Google APIs client
    library or by directly interacting with the OAuth 2.0 system using HTTP.

  Tip: If you are using Google Workspace APIs, comprehensive examples are
    available in the
    Google Workspace developer samples on GitHub
    and the Google Workspace Developer
    products page.

      Java

      After you obtain the client email address and private key from the
        API Console, use the
        Google Auth Library for Java
        to create a GoogleCredentials object from the service account's credentials and
        the scopes your application needs access to. For example:

import com.google.auth.oauth2.GoogleCredentials;
import com.google.api.services.sqladmin.SQLAdminScopes;

// ...

GoogleCredentials credentials = GoogleCredentials.fromStream(new FileInputStream("ServiceAccountKey.json"))
    .createScoped(Collections.singleton(SQLAdminScopes.SQLSERVICE_ADMIN));

      If you are developing an app on Google Cloud, you can use the
        application default credentials
        instead, which can simplify the process.

      Delegate domain-wide authority

      If you have delegated domain-wide access to the service account and you want to impersonate
        a user account, specify the email address of the user account with the
        createDelegated method of the GoogleCredentials object. For
        example:

GoogleCredentials credentials = GoogleCredentials.fromStream(new FileInputStream("ServiceAccountKey.json"))
    .createScoped(Collections.singleton(SQLAdminScopes.SQLSERVICE_ADMIN))
    .createDelegated("workspace-user@example.com");

      The GoogleCredentials object is used to call the createDelegated()
        method. The argument for the createDelegated() method must be a user which belongs to your
        Workspace account. Your code making the request will use this credential to call Google
        APIs using your service account.

      Python

      After you obtain the client email address and private key from the
        API Console, use the
        Google APIs Client Library for Python
        to complete the following steps:

        Create a Credentials object from the service account's credentials and the
          scopes your application needs access to. For example:

from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = '/path/to/ServiceAccountKey.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

          If you are developing an app on Google Cloud, you can use the
            application default credentials
            instead, which can simplify the process.

        Delegate domain-wide authority
          If you have delegated domain-wide access to the service account and you want to
            impersonate a user account, use the with_subject method of an existing
            ServiceAccountCredentials object. For example:

delegated_credentials = credentials.with_subject('user@example.org')

      Use the Credentials object to call Google APIs in your application.

      HTTP/REST

      Recommendation: Although your application can complete
        these tasks by directly interacting with the OAuth 2.0 system using HTTP, the mechanics of
        server-to-server authentication interactions require applications to create and
        cryptographically sign JSON Web Tokens (JWTs), mistakes can cause serious errors that can
        have a severe impact on the security of your application.

        For this reason, we strongly encourage you to use libraries, such as the Google APIs
          client libraries, that abstract the cryptography away from your application
          code.

      After you obtain the client ID and private key from the
        API Console, your application needs to complete the
        following steps:

        Create a JSON Web Token (JWT, pronounced, "jot") which includes a header, a claim set,
          and a signature.

        Request an access token from the Google OAuth 2.0 Authorization Server.

        Handle the JSON response that the Authorization Server returns.

      The sections that follow describe how to complete these steps.

      If the response includes an access token, you can use the access token to
        call a Google API. (If the response does not include an access
        token, your JWT and token request might not be properly formed, or the service account might
        not have permission to access the requested scopes.)

      When the access token expires, your application generates another
        JWT, signs it, and requests another access token.

          Figure 1. Your server application uses a JWT to request a token from the Google
          Authorization Server, then uses the token to call a Google API endpoint. No end user is
          involved.

      The rest of this section describes the specifics of creating a JWT, signing the JWT,
        forming the access token request, and handling the response.

        Create a JWT

        A JWT is composed of three parts: a header, a claim set, and a
          signature. The header and claim set are JSON objects. These JSON objects are serialized to
          UTF-8 bytes, then encoded using the Base64url encoding. This encoding provides resilience
          against encoding changes due to repeated encoding operations. The header, claim set, and
          signature are concatenated together with a period (.) character.

        A JWT is composed as follows:

{Base64url encoded header}.{Base64url encoded claim set}.{Base64url encoded signature}

        The base string for the signature is as follows:

{Base64url encoded header}.{Base64url encoded claim set}

        Construct the JWT header

        The header consists of two required fields: the signing algorithm and format of
          the assertion, and an optional key ID:

            Algorithm is mandatory, and has only one value: "alg": "RS256".

            Format is mandatory, and has only one value: "typ": "JWT".

            Key ID is optional, and is the
        ID of the service account key used to sign the JWT. If an an
              incorrect Key ID is specified, all keys associated with the service account are
              tried. If no valid key is found, the token is rejected. Google reserves the right to
              reject tokens with incorrect key IDs.

        Service accounts rely on the RSA SHA-256 algorithm and the JWT token format. As a result,
          the JSON representation of the header is as follows:

{"alg":"RS256","typ":"JWT", "kid":"370ab79b4513eb9bad7c9bd16a95cb76b5b2a56a"}

        The Base64url representation of this is as follows:

eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsICJraWQiOiIzNzBhYjc5YjQ1MTNlYjliYWQ3YzliZDE2YTk1Y2I3NmI1YjJhNTZhIn0=

        Construct the JWT claim set

        The JWT claim set contains information about the JWT, including the permissions being
          requested (scopes), the target of the token, the issuer, the time the token was issued,
          and the lifetime of the token. Most of the fields are mandatory. Like the JWT header, the
          JWT claim set is a JSON object and is used in the calculation of the signature.

        Required claims

        The required claims in the JWT claim set may appear in any order in the claim set.

              Name
              Description

              iss
              The email address of the service account.

              scope
              A space-delimited list of the permissions that the application requests.

              aud
              A descriptor of the intended target of the assertion. When making an access token
                request this value is always https://oauth2.googleapis.com/token.

              exp
              The expiration time of the assertion, specified as seconds since 00:00:00 UTC,
                January 1, 1970. This value has a maximum of 1 hour after the issued time.

              iat
              The time the assertion was issued, specified as seconds since 00:00:00 UTC,
                January 1, 1970.

        This is an example of a JSON representation of the required fields in a JWT claim set:

{
  "iss": "761326798069-r5mljlln1rd4lrbhg75efgigp36m78j5@developer.gserviceaccount.com",
  "scope": "https://www.googleapis.com/auth/devstorage.read_only",
  "aud": "https://oauth2.googleapis.com/token",
  "exp": 1328554385,
  "iat": 1328550785
}

        Additional claims

        In some enterprise cases, an application can use domain-wide delegation to act on behalf
          of a particular user in an organization. Permission to perform this type of impersonation
          must be granted before an application can impersonate a user, and is usually handled by a
          super administrator. For more information, see
          Control API access with domain-wide delegation.

        To obtain an access token that grants an application delegated access to a resource,
          include the email address of the user in the JWT claim set as the value of the
          sub field.

              Name
              Description

              sub
              The email address of the user for which the application is requesting delegated
                access.

        If an application does not have permission to impersonate a user, the response to an
          access token request that includes the sub field will be an
          error.

        This is an example of a JWT claim set that includes the sub field:

{
  "iss": "761326798069-r5mljlln1rd4lrbhg75efgigp36m78j5@developer.gserviceaccount.com",
  "sub": "some.user@example.com",
  "scope": "https://www.googleapis.com/auth/prediction",
  "aud": "https://oauth2.googleapis.com/token",
  "exp": 1328554385,
  "iat": 1328550785
}

        Encoding the JWT claim set

        Like the JWT header, the JWT claim set should be serialized to UTF-8 and Base64url-safe
          encoded. This is an example of a JSON representation of a JWT Claim set:

{
  "iss": "761326798069-r5mljlln1rd4lrbhg75efgigp36m78j5@developer.gserviceaccount.com",
  "scope": "https://www.googleapis.com/auth/prediction",
  "aud": "https://oauth2.googleapis.com/token",
  "exp": 1328554385,
  "iat": 1328550785
}

        Compute the signature

        JSON Web Signature
          (JWS) is the specification that guides the mechanics of generating the signature for the
          JWT. The input for the signature is the byte array of the following content:

{Base64url encoded header}.{Base64url encoded claim set}

        The signing algorithm in the JWT header must be used when computing the signature. The
          only signing algorithm supported by the Google OAuth 2.0 Authorization Server is RSA using
          SHA-256 hashing algorithm. This is expressed as RS256 in the alg
          field in the JWT header.

        Sign the UTF-8 representation of the input using SHA256withRSA (also known as
          RSASSA-PKCS1-V1_5-SIGN with the SHA-256 hash function) with the private key obtained from
          the Google API Console. The output will be a byte array.

        The signature must then be Base64url encoded. The header, claim set, and signature are
          concatenated together with a period (.) character. The result is the JWT. It
          should be the following (line breaks added for clarity):

{Base64url encoded header}.
{Base64url encoded claim set}.
{Base64url encoded signature}

        This is an example of a JWT before Base64url encoding:

{"alg":"RS256","typ":"JWT"}.
{
"iss":"761326798069-r5mljlln1rd4lrbhg75efgigp36m78j5@developer.gserviceaccount.com",
"scope":"https://www.googleapis.com/auth/prediction",
"aud":"https://oauth2.googleapis.com/token",
"exp":1328554385,
"iat":1328550785
}.
[signature bytes]

        This is an example of a JWT that has been signed and is ready for transmission:

eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3NjEzMjY3OTgwNjktcjVtbGpsbG4xcmQ0bHJiaGc3NWVmZ2lncDM2bTc4ajVAZGV2ZWxvcGVyLmdzZXJ2aWNlYWNjb3VudC5jb20iLCJzY29wZSI6Imh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL2F1dGgvcHJlZGljdGlvbiIsImF1ZCI6Imh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92NC90b2tlbiIsImV4cCI6MTMyODU1NDM4NSwiaWF0IjoxMzI4NTUwNzg1fQ.UFUt59SUM2_AW4cRU8Y0BYVQsNTo4n7AFsNrqOpYiICDu37vVt-tw38UKzjmUKtcRsLLjrR3gFW3dNDMx_pL9DVjgVHDdYirtrCekUHOYoa1CMR66nxep5q5cBQ4y4u2kIgSvChCTc9pmLLNoIem-ruCecAJYgI9Ks7pTnW1gkOKs0x3YpiLpzplVHAkkHztaXiJdtpBcY1OXyo6jTQCa3Lk2Q3va1dPkh_d--GU2M5flgd8xNBPYw4vxyt0mP59XZlHMpztZt0soSgObf7G3GXArreF_6tpbFsS3z2t5zkEiHuWJXpzcYr5zWTRPDEHsejeBSG8EgpLDce2380ROQ

        Request an access token

        After generating the signed JWT, an application can use it to request an access token.
          This access token request is an HTTPS POST request, and the body is URL
          encoded. For example:

https://oauth2.googleapis.com/token

        The following parameters are required in the HTTPS POST request:

              Name
              Description

              grant_type
              Use the following string, URL-encoded as necessary:
                urn:ietf:params:oauth:grant-type:jwt-bearer

              assertion
              The JWT, including signature.

        This is a raw dump of the HTTPS POST request used in an access token
          request:

POST /token HTTP/1.1
Host: oauth2.googleapis.com
Content-Type: application/x-www-form-urlencoded

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3NjEzMjY3OTgwNjktcjVtbGpsbG4xcmQ0bHJiaGc3NWVmZ2lncDM2bTc4ajVAZGV2ZWxvcGVyLmdzZXJ2aWNlYWNjb3VudC5jb20iLCJzY29wZSI6Imh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL2F1dGgvcHJlZGljdGlvbiIsImF1ZCI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi90b2tlbiIsImV4cCI6MTMyODU3MzM4MSwiaWF0IjoxMzI4NTY5NzgxfQ.ixOUGehweEVX_UKXv5BbbwVEdcz6AYS-6uQV6fGorGKrHf3LIJnyREw9evE-gs2bmMaQI5_UbabvI4k-mQE4kBqtmSpTzxYBL1TCd7Kv5nTZoUC1CmwmWCFqT9RE6D7XSgPUh_jF1qskLa2w0rxMSjwruNKbysgRNctZPln7cqQ

        This is the same request, using curl:

curl -d 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3NjEzMjY3OTgwNjktcjVtbGpsbG4xcmQ0bHJiaGc3NWVmZ2lncDM2bTc4ajVAZGV2ZWxvcGVyLmdzZXJ2aWNlYWNjb3VudC5jb20iLCJzY29wZSI6Imh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL2F1dGgvcHJlZGljdGlvbiIsImF1ZCI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi90b2tlbiIsImV4cCI6MTMyODU3MzM4MSwiaWF0IjoxMzI4NTY5NzgxfQ.RZVpzWygMLuL-n3GwjW1_yhQhrqDacyvaXkuf8HcJl8EtXYjGjMaW5oiM5cgAaIorrqgYlp4DPF_GuncFqg9uDZrx7pMmCZ_yHfxhSCXru3gbXrZvAIicNQZMFxrEEn4REVuq7DjkTMyCMGCY1dpMa8aWfTQFt3Eh7smLchaZsU
' https://oauth2.googleapis.com/token

        Response handling

        If the JWT and access token request are properly formed and the service account has
          permission to perform the operation, then the JSON response from the Authorization Server
          includes an access token. The following is an example response:

{
  "access_token": "1/8xbJqaOZXSUZbHLl5EOtu1pxz3fmmetKx9W8CV4t79M",
  "scope": "https://www.googleapis.com/auth/prediction"
  "token_type": "Bearer",
  "expires_in": 3600
}

        Access tokens can be reused during the duration window specified by the
          expires_in value.

  Important Security Consideration: Understanding Impersonation

  When you delegate domain-wide authority, you are not granting the service account direct access
  to all user data. Instead, you are authorizing it to impersonate specific users when making
  API calls.

  Access is on Behalf of a User: Your application must specify which user to impersonate for each
  API request. The application then acts with the permissions of that specific user, not with any
  elevated or domain-wide privileges.

  Permissions are Limited: The service account's access is constrained by two factors: the
  permissions of the impersonated user and the OAuth scopes you authorize in the Admin console. It
  cannot access data that the impersonated user themselves cannot access.

  Principle of Least Privilege: Because this feature allows access to user data without their
  direct consent, it is critical to follow security best practices. Only grant the necessary OAuth
  scopes, and ensure you understand the security implications.

  For detailed security guidelines, refer to
  Domain-wide delegation best practices.

  Call Google APIs

      Java

      Use the GoogleCredentials object to call Google APIs by completing the
        following steps:

        Create a service object for the API that you want to call using the
          GoogleCredentials object. For example:

SQLAdmin sqladmin =
    new SQLAdmin.Builder(httpTransport, JSON_FACTORY, credentials).build();

        Make requests to the API service using the
          interface provided by the service object.
          For example, to list the instances of Cloud SQL databases in the exciting-example-123
          project:

SQLAdmin.Instances.List instances =
    sqladmin.instances().list("exciting-example-123").execute();

      Python

      Use the authorized Credentials object to call Google APIs by completing the
        following steps:

        Build a service object for the API that you want to call. You build a service object
          by calling the build function with the name and version of the API and the
          authorized Credentials object. For example, to call version 1beta3 of the
          Cloud SQL Administration API:

import googleapiclient.discovery

sqladmin = googleapiclient.discovery.build('sqladmin', 'v1beta3', credentials=credentials)

        Make requests to the API service using the
          interface provided by the service object.
          For example, to list the instances of Cloud SQL databases in the exciting-example-123
          project:

response = sqladmin.instances().list(project='exciting-example-123').execute()

      HTTP/REST

After your application obtains an access token, you can use the token to make calls to a Google
  API on behalf of a given service account or
  user account if the scope(s) of access required by the API have been granted. To do this, include
  the access token in a request to the API by including either an access_token query
  parameter or an Authorization HTTP header Bearer value. When possible,
  the HTTP header is preferable, because query strings tend to be visible in server logs. In most
  cases you can use a client library to set up your calls to Google APIs (for example, when
  calling the Drive Files API).

You can try out all the Google APIs and view their scopes at the
  OAuth 2.0 Playground.

HTTP GET examples

A call to the

    drive.files
  endpoint (the Drive Files API) using the Authorization: Bearer HTTP
  header might look like the following. Note that you need to specify your own access token:

GET /drive/v2/files HTTP/1.1
Host: www.googleapis.com
Authorization: Bearer access_token

Here is a call to the same API for the authenticated user using the access_token
  query string parameter:

GET https://www.googleapis.com/drive/v2/files?access_token=access_token

curl examples

You can test these commands with the curl command-line application. Here's an
  example that uses the HTTP header option (preferred):

curl -H "Authorization: Bearer access_token" https://www.googleapis.com/drive/v2/files

Or, alternatively, the query string parameter option:

curl https://www.googleapis.com/drive/v2/files?access_token=access_token

        When access tokens expire

        Access tokens issued by the Google OAuth 2.0 Authorization Server expire after the duration
          provided by the expires_in value. When an access token expires, then the
          application should generate another JWT, sign it, and request another access token.

JWT error codes

        error field
        error_description field
        Meaning
        How to resolve

        unauthorized_client
        Unauthorized client or scope in request.
        If you're trying to use domain-wide delegation, the service account is not authorized in
          the Admin console of the user's domain.

          Ensure that the service account is authorized in the
            Domain-wide delegation page of the Admin console for the user in the
            sub claim (field).

          While it usually takes a few minutes, it might take up to 24 hours for authorization to
            propagate to all users in your Google Account.

        unauthorized_client
        Client is unauthorized to retrieve access tokens using this method, or client not
          authorized for any of the scopes requested.

          A service account was authorized using the client email address rather than the client ID
          (numeric) in the Admin console, or a Google Group was used for authorization.

          In the
            Domain-wide delegation page in the Admin console, remove the client, and re-add it
          with the numeric ID, or remove the Google Group and replace it with the individual service
          or user account.

        access_denied
        (any value)
        If you're using Domain-wide delegation, one or more requested scopes aren't authorized
          in the Admin console.

          Ensure that the service account is authorized in the

              Domain-wide delegation page of the Admin console for the user in the
            sub claim (field), and that it includes all of the scopes you're requesting
            in the scope claim of your JWT.

            Confirm that access to Google services is not restricted by reviewing
              Manage access to services that
                aren't controlled individually.

          While it usually takes a few minutes, it might take up to 24 hours for authorization to
            propagate to all users in your Google Account.

        admin_policy_enforced
        (any value)
        The Google Account is unable to authorize one or more scopes requested due to the
          policies of their Google Workspace administrator.

          See the Google Workspace Admin help article
            Control which third-party &
            internal apps access Google Workspace data for more information about how an
            administrator may restrict access to all scopes or sensitive and restricted scopes until
            access is explicitly granted to your OAuth client ID.

        invalid_client
        (any value)

          The OAuth client or JWT token is invalid or incorrectly configured.

          Refer to the error description for details.

          Make sure the JWT token is valid and contains correct claims.

          Check that the OAuth client and service account are
            configured correctly and that you are using the correct email address.

          Check that the JWT token is correct and was issued for the client ID in the
            request.

        deleted_client
        (any value)

          The OAuth client being used to make the request has been deleted. Deletion can happen
            manually or automatically in the case of
            unused
               clients . Deleted clients can be restored within 30 days of the deletion.
            Learn
              more.

          Use a client ID that is still active.

        invalid_grant
        Not a valid email or Invalid email or User ID.
        The user doesn't exist.
        Check that the email address in the sub claim (field) is correct.

        invalid_grant

          Invalid JWT: Token must be a short-lived token (60 minutes) and in a reasonable
            timeframe. Check your 'iat' and 'exp' values and use a clock with skew to account for
            clock differences between systems.

        Usually, it means that the local system time is not correct. It could also happen if the
          exp value is more than 65 mins in the future from the iat value,
          or the exp value is lower than iat value.

          Make sure that the clock on the system where the JWT is generated is correct. If
            necessary, sync your time with
            Google NTP.

        invalid_grant
        Invalid JWT Signature.

          The JWT assertion is signed with a private key not associated with the service account
            identified by the client email or the key that was used has been deleted, disabled, or
            has expired.

          Alternatively, the JWT assertion might be encoded incorrectly - it must be
            Base64-encoded, without newlines or padding equal signs.

          Decode the JWT claim set and verify the key that signed the assertion is associated
            with the service account.

          Try to use a Google-provided OAuth library to make sure the JWT is generated correctly.

        invalid_scope
        Invalid OAuth scope or ID token audience provided.
        No scopes were requested (empty list of scopes), or one of the requested scopes doesn't
          exist (i.e. is invalid).

          Ensure that the scope claim (field) of the JWT is populated, and compare
            the scopes that it contains with the documented scopes for the APIs you want to use, to
            ensure there are no errors or typos.

          Note that the list of scopes in the scope claim needs to be separated by
            spaces, not commas.

        disabled_client
        The OAuth client was disabled.
        The key used to sign the JWT assertion is disabled.

          Go to the Google API Console, and under IAM & Admin
            > Service Accounts, enable the service account which contains the "Key ID" used
            to sign the assertion.

        org_internal
        This client is restricted to users within its organization.
        The OAuth client ID in the request is part of a project limiting access to Google
          Accounts in a specific

          Google Cloud Organization.

          Use a service account from the organization to authenticate. Confirm the
            user type
            configuration for your OAuth application.

  Addendum: Service account authorization without OAuth

  With some Google APIs, you can make authorized API calls using a signed JWT directly as a
    bearer token, rather than an OAuth 2.0 access token. When this is possible, you can avoid having
    to make a network request to Google's authorization server before making an API call.

  If the API you want to call has a service definition published in the
    Google APIs GitHub repository,
    you can make authorized API calls using a JWT instead of an access token. To do so:

    Create a service account. Be sure to
      keep the JSON file you get when you create the account.

    Using any standard JWT library, such as one found at
      jwt.io, create a JWT with a header
      and payload like the following example:

{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "abcdef1234567890"
}
.
{
  "iss": "123456-compute@developer.gserviceaccount.com",
  "sub": "123456-compute@developer.gserviceaccount.com",
  "aud": "https://firestore.googleapis.com/",
  "iat": 1511900000,
  "exp": 1511903600
}

      For the kid field in the header, specify your service account's private key
        ID. You can find this value in the private_key_id field of your service account
        JSON file.

      For the iss and sub fields, specify your service account's email
        address. You can find this value in the client_email field of your service
        account JSON file. This value uniquely identifies the client, and functionally is the
        client ID.

      For the aud field, specify the API endpoint. For example:
https://SERVICE.googleapis.com/.

      For the iat field, specify the current Unix epoch time, and for the
        exp field, specify the time exactly 3600 seconds later, when the JWT will
        expire.

  Sign the JWT with RSA-256 using the private key found in your service account JSON file.

  For example:

      Java

      Using
        google-auth-library-java and
        java-jwt:

import com.google.auth.oauth2.ServiceAccountCredentials;
...
GoogleCredentials credentials =
        GoogleCredentials.fromStream(new FileInputStream("MyProject-1234.json"));
PrivateKey privateKey = ((ServiceAccountCredentials) credentials).getPrivateKey();
String privateKeyId = ((ServiceAccountCredentials) credentials).getPrivateKeyId();

long now = System.currentTimeMillis();

try {
    Algorithm algorithm = Algorithm.RSA256(null, privateKey);
    String signedJwt = JWT.create()
        .withKeyId(privateKeyId)
        .withIssuer("123456-compute@developer.gserviceaccount.com")
        .withSubject("123456-compute@developer.gserviceaccount.com")
        .withAudience("https://firestore.googleapis.com/")
        .withIssuedAt(new Date(now))
        .withExpiresAt(new Date(now + 3600 * 1000L))
        .sign(algorithm);
} catch ...

      Python

      Using PyJWT:

iat = time.time()
exp = iat + 3600
payload = {'iss': '123456-compute@developer.gserviceaccount.com',
           'sub': '123456-compute@developer.gserviceaccount.com',
           'aud': 'https://firestore.googleapis.com/',
           'iat': iat,
           'exp': exp}
additional_headers = {'kid': PRIVATE_KEY_ID_FROM_JSON}
signed_jwt = jwt.encode(payload, PRIVATE_KEY_FROM_JSON, headers=additional_headers,
                       algorithm='RS256')

    Call the API, using the signed JWT as the bearer token:

GET /v1/projects/abc/databases/123/indexes HTTP/1.1
Authorization: Bearer SIGNED_JWT
Host: firestore.googleapis.com

  Implement Cross-Account Protection

  An additional step you should take to protect your users' accounts is implementing Cross-Account
  Protection by utilizing Google's Cross-Account Protection Service. This service lets you
  subscribe to security event notifications which provide information to your application about
  major changes to the user account. You can then use the information to take action depending on
  how you decide to respond to events.

  Some examples of the event types sent to your app by Google's Cross-Account Protection Service are:

    https://schemas.openid.net/secevent/risc/event-type/sessions-revoked

    https://schemas.openid.net/secevent/oauth/event-type/token-revoked

    https://schemas.openid.net/secevent/risc/event-type/account-disabled

  See the

    Protect user accounts with Cross-Account Protection page

  for more information on how to implement Cross Account Protection and for the full list of available events.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-03-23 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Missing the information I need","missingTheInformationINeed","thumb-down"],["Too complicated / too many steps","tooComplicatedTooManySteps","thumb-down"],["Out of date","outOfDate","thumb-down"],["Samples / code issue","samplesCodeIssue","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-03-23 UTC."],[],[]]
