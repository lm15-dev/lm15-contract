Home

          Documentation

          Compute

          Compute Engine

          Guides

    Send feedback

      Authenticate workloads to Google Cloud APIs using service accounts

      Stay organized with collections

      Save and categorize content based on your preferences.

This page describes how to use service accounts to enable apps running on
your virtual machine (VM) instances to authenticate to Google Cloud APIs and
authorize access to resources.

To use service accounts for authentication, you must first ensure that your VM
is configured to use a service account. To do this complete one of the following
procedures:

To set up service account during VM creation, see
Create a VM that uses a user-managed service account.

To set up service account on an existing VM, see
Change the attached service account.

Before you begin

Review the
  Service accounts overview.

  If you haven't already, set up authentication.
  Authentication verifies your identity for access to Google Cloud services and APIs. To run
  code or samples from a local development environment, you can authenticate to
  Compute Engine by selecting one of the following options:

      To use the Python samples on this page in a local development environment, install and
      initialize the gcloud CLI, and then set up Application Default Credentials with
      your user credentials.

        Install the Google Cloud CLI.

          If you're using an external identity provider (IdP), you must first

              sign in to the gcloud CLI with your federated identity.

        If you're using a local shell, then create local authentication credentials for your user
        account:

gcloud auth application-default login

      You don't need to do this if you're using Cloud Shell.

        If an authentication error is returned, and you are using an external identity provider
        (IdP), confirm that you have

          signed in to the gcloud CLI with your federated identity.

    For more information, see

      Set up authentication for a local development environment.

Overview

After you have set up a VM instance to run using a service account, an application
running on the VM instance can use one of the following methods for authentication:

For most applications, choose one of the following:

Use Application Default Credentials and a client library

Use the Google Cloud CLI

For applications that require an OAuth2 access token,
request and use access tokens directly from the metadata server

Authenticating applications using service account credentials

After setting up an instance to run as a service account, you can use
service account credentials to authenticate applications running on the instance.

Authenticating applications with a client library

Client libraries can use
Application Default Credentials
to authenticate with Google APIs and send requests to those APIs.
Application Default Credentials lets applications automatically obtain
credentials from multiple sources so you can test your application locally and
then deploy it to a Compute Engine instance without changing the
application code.

For information about setting up Application Default Credentials, see
Provide credentials to Application Default Credentials.

This example uses the
Python client library
to authenticate and make a request to the Cloud Storage API to list the buckets in
a project. The example uses the following procedure:

Obtain the necessary authentication credentials for the Cloud Storage API
and initialize the Cloud Storage service with the build() method
and the credentials.

List buckets in Cloud Storage.

You can run this sample on an instance that has access to manage buckets in
Cloud Storage.

Note: You might need to run this script with sudo.

import argparse
from typing import List

from google.cloud import storage

def create_client() -> storage.Client:
    """
    Construct a client object for the Storage API using the
    application default credentials.

    Returns:
        Storage API client object.
    """
    # Construct the service object for interacting with the Cloud Storage API -
    # the 'storage' service, at version 'v1'.
    # Authentication is provided by application default credentials.
    # When running locally, these are available after running
    # `gcloud auth application-default login`. When running on Compute
    # Engine, these are available from the environment.
    return storage.Client()

def list_buckets(client: storage.Client, project_id: str) -> List[storage.Bucket]:
    """
    Retrieve bucket list of a project using provided client object.

    Args:
        client: Storage API client object.
        project_id: name of the project to list buckets from.

    Returns:
        List of Buckets found in the project.
    """
    buckets = client.list_buckets()
    return list(buckets)

def main(project_id: str) -> None:
    client = create_client()
    buckets = list_buckets(client, project_id)
    print(buckets)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("project_id", help="Your Google Cloud Project ID.")

    args = parser.parse_args()

    main(args.project_id)

Authenticating applications directly with access tokens

For most applications, you can authenticate by using
Application Default Credentials,
which finds credentials and manages tokens for you. However, if your application
requires you to provide an OAuth2 access token, Compute Engine lets you
get an access token from its metadata server for use in your application. By
default, the metadata server returns an access token with all scopes specified for the
instance's service account. If your application requires limited permissions, you
can request downscoped or restricted tokens. For more information, see
Obtain specific OAuth2 access tokens.

There are several options for obtaining and using these
access tokens to authenticate your applications. For example, you can use
curl to create a simple request, or use a programming language like Python
for more flexibility.

 cURL
To use curl to request an access token and send a request to an API:

On the instance where your application runs, query the
metadata server
for an access token by running the following command:

$ curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" \
-H "Metadata-Flavor: Google"

The request returns a response similar to:

{
      "access_token":"ya29.AHES6ZRN3-HlhAPya30GnW_bHSb_QtAS08i85nHq39HE3C2LTrCARA",
      "expires_in":3599,
      "token_type":"Bearer"
 }

For API requests you need to include the access_token value, not the
entire response. If you have the
jq command-line JSON processor
installed you can use the following command to extract the access token
value from the response:

$ ACCESS_TOKEN=`curl \
"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" \
-H "Metadata-Flavor: Google" | jq -r '.access_token'`

Copy the value of the access_token property from the response and
use it to send requests to the API. For example, the following request
prints a list of instances in your project from a certain zone:

$ curl https://compute.googleapis.com/compute/v1/projects/PROJECT_ID/zones/ZONE/instances \
-H "Authorization":"Bearer ACCESS_TOKEN"

Replace the following:

PROJECT_ID: the project ID for this
request.

ZONE: the zone to list VMs from.

ACCESS_TOKEN: the access token value you
 got from the previous step.

Note: By default, the access token includes all scopes that you specified
when you created the instance. To limit permissions, you can request a
downscoped or restricted token as described in
Obtain specific OAuth2 access tokens.
However, you cannot request scopes beyond what you specified during instance
creation or update. For example, if the instance was configured with only
the https://www.googleapis.com/auth/storage-full scope for
Cloud Storage, then it can't use the access token to make a request
to BigQuery.
For information about the parameters that you can set in your request,
see the System parameters documentation.

 Python
This example demonstrates how to request a token to access the
Cloud Storage API in a Python application. The example uses the following
procedure:

Request an access token from the metadata server.

Extract the access token from the server response.

Use the access token to make a request to Cloud Storage.

If the request is successful, the script prints the response.

import argparse

import requests

METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/"
METADATA_HEADERS = {"Metadata-Flavor": "Google"}
SERVICE_ACCOUNT = "default"

def get_access_token() -> str:
    """
    Retrieves access token from the metadata server.

    Returns:
        The access token.
    """
    url = f"{METADATA_URL}instance/service-accounts/{SERVICE_ACCOUNT}/token"

    # Request an access token from the metadata server.
    r = requests.get(url, headers=METADATA_HEADERS)
    r.raise_for_status()

    # Extract the access token from the response.
    access_token = r.json()["access_token"]

    return access_token

def list_buckets(project_id: str, access_token: str) -> dict:
    """
    Calls Storage API to retrieve a list of buckets.

    Args:
        project_id: name of the project to list buckets from.
        access_token: access token to authenticate with.

    Returns:
        Response from the API.
    """
    url = "https://www.googleapis.com/storage/v1/b"
    params = {"project": project_id}
    headers = {"Authorization": f"Bearer {access_token}"}

    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()

    return r.json()

def main(project_id: str) -> None:
    """
    Retrieves access token from metadata server and uses it to list
    buckets in a project.

    Args:
        project_id: name of the project to list buckets from.
    """
    access_token = get_access_token()
    buckets = list_buckets(project_id, access_token)
    print(buckets)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("project_id", help="Your Google Cloud project ID.")

    args = parser.parse_args()

    main(args.project_id)

Access tokens expire after a short period of time. The metadata server caches
access tokens until they have 5 minutes of remaining time before they
expire. If tokens are unable to be cached, requests that exceed 50 queries
per second might be rate limited. Your applications must have a valid access
token for their API calls to succeed.

Authenticating tools on an instance using a service account

Some applications might use commands from the gcloud CLI, which is
included by default in most Compute Engine images. The
gcloud CLI automatically recognizes an instance's service account and
relevant permissions granted to the service account. Specifically, if you grant
the correct roles to the service account, you can use the gcloud CLI
from your instances without having to use gcloud auth login.

This service account recognition happens automatically and applies only to the
gcloud CLI that is included with the instance. If you create
new tools or add custom tools, you must authorize your application
using a client library or by
using access tokens directly in your application.

To take advantage of automatic service account recognition,
grant the appropriate IAM roles
to the service account and
attach the service account to the instance.
For example, if you grant a service account the roles/storage.objectAdmin
role, the gcloud CLI can automatically manage and access
Cloud Storage objects.

Likewise, if you enable roles/compute.instanceAdmin.v1 for the service account,
the gcloud compute tool can automatically manage instances.

What's next

Authenticate workloads to other workloads over mTLS .

Learn more about Service Accounts.

Learn more about Compute Engine IAM roles and permissions.

Learn more about best practices for working with service accounts.

      Try it for yourself

      If you're new to Google Cloud, create an account to evaluate how
      Compute Engine performs in real-world
      scenarios. New customers also get $300 in free credits to run, test, and
      deploy workloads.

        Try Compute Engine free

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-08-26 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-08-26 UTC."],[],[]]
