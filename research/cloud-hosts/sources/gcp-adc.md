Home

          Documentation

          Developer tools

          Google Cloud SDK

          Authentication

          Guides

    Send feedback

      How Application Default Credentials works

      Stay organized with collections

      Save and categorize content based on your preferences.

This page describes the locations where Application Default Credentials (ADC)
looks for credentials. Understanding how ADC works can help you understand which
credentials ADC is using, and how it's finding them.

  Application Default Credentials (ADC) is a strategy used by the authentication libraries to automatically find
  credentials based on the application environment. The authentication libraries make those
  credentials available to
  Cloud Client Libraries and Google API Client Libraries.
  When you use ADC, your code can run in either a development or production environment without
  changing how your application authenticates to Google Cloud services and APIs.

For information about how to provide credentials to ADC, including how to
generate a local ADC file, see
Set up Application Default Credentials.

Search order

ADC searches for credentials in the following locations:

GOOGLE_APPLICATION_CREDENTIALS environment variable

A credential file created by using the gcloud auth application-default login command

The attached service account, returned by the metadata server

The order of the locations ADC checks for credentials is not related to
the relative merit of each location. For help with
understanding the best ways to provide credentials to ADC, see
Set up Application Default Credentials.

GOOGLE_APPLICATION_CREDENTIALS environment variable

You can use the GOOGLE_APPLICATION_CREDENTIALS environment variable to provide
the location of a credential JSON file. This JSON file can be one of the
following types of files:

A credential configuration file for Workforce Identity Federation

Workforce Identity Federation lets you use an external identity provider
(IdP) to authenticate and authorize users to access Google Cloud
resources. For more information, see
Workforce Identity Federation in the
Identity and Access Management (IAM) documentation.

A credential configuration file for Workload Identity Federation

Workload Identity Federation lets you use an external
IdP to authenticate and authorize workloads to access
Google Cloud resources. For more information, see
Authenticating by using client libraries, the gcloud CLI, or Terraform
in the Identity and Access Management (IAM) documentation.

A service account key

Service account keys create a security risk and are not recommended. Unlike
the other credential file types, compromised service account keys can be
used by a bad actor without any additional information. For more
information, see
Best practices for using and managing service account keys.

A credential file created by using the gcloud auth application-default login command

You can provide credentials to ADC by running the
gcloud auth application-default login command. This
command creates a JSON file containing the credentials you provide (either from
your user account or from impersonating a service account) and places it in a
well-known location on your file system. The location depends on your
operating system:

Linux, macOS: $HOME/.config/gcloud/application_default_credentials.json

Windows: %APPDATA%\gcloud\application_default_credentials.json

The credentials you provide to ADC by using the gcloud CLI are
distinct from your gcloud credentials—the credentials the
gcloud CLI uses to authenticate to Google Cloud. For more
information about these two sets of credentials, see
gcloud CLI authentication configuration and ADC configuration .

By default, the access tokens generated from a local ADC file created with user credentials
include the
  cloud-wide scope https://www.googleapis.com/auth/cloud-platform.
To specify scopes explicitly, you use the

  --scopes flag
with the gcloud auth application-default login command.

To add scopes for services outside of Google Cloud, such as Google Drive, you can do one of
the following:

    OAuth authentication:
    Create an OAuth client ID.
    Provide the client ID to the gcloud auth application-default login command
    by using the

          --client-id-file flag, and specify your scopes with the

      --scopes flag.

    Service account authentication: Create a service account.

      Impersonate the service account by providing its email address to the
    gcloud auth application-default login command with the
       --impersonate-service-account flag, and specify your scopes with the

         --scopes flag.

The attached service account

Many Google Cloud services let you attach a service account that can be
used to provide credentials for accessing Google Cloud APIs. If ADC does
not find credentials it can use in either the GOOGLE_APPLICATION_CREDENTIALS
environment variable or the well-known location for local ADC credentials,
it uses the metadata server to get credentials for the
service where the code is running.

Using the credentials from the attached service account is the preferred method
for finding credentials in a production environment on Google Cloud. To
use the attached service account, follow these steps:

Create a user-managed service account.

Grant that service account the least privileged
IAM roles possible.

Attach the service account to the resource where your code is running.

For help with creating a service account, see
Creating and managing service accounts. For help with attaching
a service account, see Attaching a service account to a resource.
For help with determining the required IAM roles for your service
account, see Choose predefined roles.

What's next

Learn the best ways to provide credentials to ADC.

Authenticate using the Cloud Client Libraries.

Explore authentication methods.

Learn about client libraries.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-08-26 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-08-26 UTC."],[],[]]
