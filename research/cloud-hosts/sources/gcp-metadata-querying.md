Home

          Documentation

          Compute

          Compute Engine

          Guides

    Send feedback

      View and query VM metadata

      Stay organized with collections

      Save and categorize content based on your preferences.

      Linux

      Windows

You can view and query metadata values for
your compute instances to configure your applications,
manage compute instances, optimize performance, and troubleshoot configurations.
Every compute instance in Google Cloud's Compute Engine stores its
metadata on a dedicated metadata server. Your compute instances automatically
access this metadata through the metadata server API without needing additional authorization.
This document shows you how to programmatically query metadata from within a
compute instance and how to view custom metadata.

If you encounter errors when accessing the metadata server, review
Troubleshooting metadata server access issues.

Pro Tip:
Maintenance events
can cause occasional disruptions to the availability of the metadata server for
less than one second. During this time the metadata server might return a
Error 503 HTTP server response. To make your applications resilient
to maintenance events, we recommend that you implement retry logic for
applications that query the metadata server.

Before you begin

For Windows Server instances, use
  PowerShell 3.0 or later.
  We recommend that you use ctrl+v to paste the copied code blocks.

Review the basics of how VM metadata for Compute Engine is defined,
  categorized, and arranged. For more information, see
  About VM metadata.

  If you haven't already, set up authentication.
  Authentication verifies your identity for access to Google Cloud services and APIs. To run
  code or samples from a local development environment, you can authenticate to
  Compute Engine by selecting one of the following options:

      Select the tab for how you plan to use the samples on this page:

        Console

        When you use the Google Cloud console to access Google Cloud services and
        APIs, you don't need to set up authentication.

        gcloud

        Install the Google Cloud CLI.

          After installation,
          initialize the Google Cloud CLI by running the following command:

gcloud init

        If you're using an external identity provider (IdP), you must first

          sign in to the gcloud CLI with your federated identity.

    Note: If you installed the gcloud CLI previously, make sure you have
    the latest version by running gcloud components update.

  Set a default region and zone.

        Python

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

        REST

    To use the REST API samples on this page in a local development environment, you use the
    credentials you provide to the gcloud CLI.

        Install the Google Cloud CLI.

        If you're using an external identity provider (IdP), you must first

          sign in to the gcloud CLI with your federated identity.

  For more information, see
  Authenticate for using REST
  in the Google Cloud authentication documentation.

Required roles

The following roles and permissions are needed to view custom metadata from
outside the Compute Engine instance by using the Google Cloud console, the
Google Cloud CLI, or REST. If you are programmatically querying the
metadata from within the compute instance, then you only need the roles and
permissions for connecting to the instance.

      To get the permissions that
      you need to view custom metadata from outside the compute instance,

      ask your administrator to grant you the
    following IAM roles:

            Compute Instance Admin (v1)  (roles/compute.instanceAdmin.v1)
              on the  compute instance or project

            If your compute instances use service accounts:
              Service Account User  (roles/iam.serviceAccountUser)
              on the service account  or project

  For more information about granting roles, see Manage access to projects, folders, and organizations.

          These predefined roles contain

        the permissions required to view custom metadata from outside the compute instance. To see the exact permissions that are
        required, expand the Required permissions section:

        Required permissions

        The following permissions are required to view custom metadata from outside the compute instance:

                To view custom project metadata:
                  compute.projects.get
                  on the project

                To view custom zonal metadata:
                  compute.instanceSettings.get
                  on the  instance settings in the required zone in the project

                To view custom metadata for a compute instance:
                  compute.instances.get
                  on the  compute instance

                If your compute instances use service accounts:
                  iam.serviceAccounts.actAs
                  on the service accounts or project

        You might also be able to get
          these permissions
        with custom roles or
        other predefined roles.

Programmatically query metadata

You can access all metadata by querying the metadata value entries
programmatically from within a Linux or Windows instance. From within your
compute instance, you can programmatically query your metadata values in one of
the following ways by using tools such as curl on Linux or Invoke-RestMethod
on Windows:

Query a single metadata entry

Query a metadata directory listing

Obtain specific OAuth2 access tokens

Query metadata changes using the wait-for-change feature

Metadata server endpoints

To programmatically query metadata, from within a compute instance , you have
the following metadata server endpoints:

For all compute instances, you can query the metadata server by using one of
the following HTTP endpoints:

The DNS name: http://metadata.google.internal/computeMetadata/v1 (Recommended)

The IPv4 address: http://169.254.169.254/computeMetadata/v1

The IPv6 address (only for IPv6-only instances): http://fd20:ce::254/computeMetadata/v1

For Shielded VMs, you
can query the metadata server by using one of the following:

The HTTP endpoints for all compute instances.

The HTTPS endpoints (available in Preview):

The DNS name: https://metadata.google.internal/computeMetadata/v1 (Recommended)

The IPv4 address: https://169.254.169.254/computeMetadata/v1

The IPv6 address (only for IPv6-only instances): https://fd20:ce::254/computeMetadata/v1

To see the format for querying the HTTPS endpoint, see
Query metadata by using the HTTPS metadata server endpoint.

Most examples in this document use the HTTP endpoint. However, you can access
all the same metadata entries whether you use the HTTPS or the HTTP endpoint.

Parts of a metadata request

The following table summarizes the main parts of a metadata query request.

Components
Description

Root URLs
All metadata values are defined as sub-paths below
the following root URLs:

  HTTP endpoint:

http://metadata.google.internal/computeMetadata/v1

http://169.254.169.254/computeMetadata/v1

http://metadata.goog/computeMetadata/v1

http://fd20:ce::254/computeMetadata/v1
 (only for IPv6-only compute instances)

  HTTPS endpoint (Preview):

https://metadata.google.internal/computeMetadata/v1

https://169.254.169.254/computeMetadata/v1

https://fd20:ce::254/computeMetadata/v1
 (only for IPv6-only compute instances)

Request header

This header indicates that the request was sent with the intention of
retrieving metadata values, rather than unintentionally from an insecure source,
and lets the metadata server return the data you requested. If you don't provide
this header, the metadata server denies your request.

Metadata-Flavor: Google

The legacy X-Google-Metadata-Request header
is deprecated. All new and existing
applications must use the Metadata-Flavor: Google header instead.

Query a single metadata entry

Use the following commands to query a single metadata entry.

 Linux

Connect to your Linux instance.

From your Linux instance, use the
curl tool to make a query. To
query for a compute instance or project metadata entry, run the following
command:

curl "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY" -H "Metadata-Flavor: Google"

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

For example, to query the boot image for the compute instance, run the
following query:

user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/image" -H "Metadata-Flavor: Google"

The output is similar to the following:

projects/rhel-cloud/global/images/rhel-8-v20210122

 Windows

Connect to your Windows compute instance.

From your Windows instance, use the
Invoke-RestMethod command to make a query.
To query for a compute instance or project metadata entry, run the
following command:

$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY")
$value

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

For example, to query the boot image for the compute instance, run the
following query:

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/instance/image")
$value

The output is similar to the following:

projects/windows-cloud/global/images/windows-server-2019-dc-v20210112

Query metadata directory listings

Use the following commands to query metadata directory listings. Directory
listings are metadata entries that contain other metadata keys. Any metadata
entry ending in a trailing slash is a directory listing

 Linux

Connect to your Linux compute instance.

To query for a compute instance instance or project metadata directory,
from your Linux instance, run the following command:

  curl "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_DIRECTORY/" -H "Metadata-Flavor: Google"

  Replace the PATH_TO_METADATA_DIRECTORY with the path to
  the VM instance or project metadata directory for which you want to recursively
  query the listings. For example:

    To view the attributes project metadata directory entry, the
    path to specify is project/attributes/.

    To view the disks VM instance metadata directory entry, the path
    to specify is instance/disks/.

For example, consider the disks/ entry, which is a directory of disks
that is attached to the compute instance. To query the disks/ entry,
complete the following steps:

Run the curl tool
command on the disks directory.

user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/disks/" -H "Metadata-Flavor: Google"

The output is similar to the following:

0/
1/
2/

If you want more information about disk 0/ directory, you can then
query the specific URL for that directory:

user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/disks/0/" -H "Metadata-Flavor: Google"

The output is similar to the following:

device-name
index
mode
type

Then to query the disk type (type) for disks 0/, you can run the following:

user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/disks/0/type" -H "Metadata-Flavor: Google"

The output is similar to the following:

PERSISTENT

 Windows
The disks/ entry is a directory of disks that is attached to the compute
instance. To query the disks entry, complete the following steps:

Connect to your Windows compute instance.

To query for a compute instance or project metadata directory,
from your Windows compute instance, run the following command:

$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_DIRECTORY/")
$value

  Replace the PATH_TO_METADATA_DIRECTORY with the path to
  the VM instance or project metadata directory for which you want to recursively
  query the listings. For example:

    To view the attributes project metadata directory entry, the
    path to specify is project/attributes/.

    To view the disks VM instance metadata directory entry, the path
    to specify is instance/disks/.

For example, consider the disks/ entry, which is a directory of disks
that is attached to the compute instance. To query the disks/ entry, complete the
following steps:

Use the
Invoke-RestMethod command on the disks directory.

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/instance/disks/")
$value

The output is similar to the following:

0/
1/
2/

If you want more information about disk 0/ directory, you can query the
specific URL for that directory:

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/instance/disks/0/")
$value

The output is similar to the following:

device-name
index
mode
type

Then to query the disk type (type) for disks 0/, you can run the following:

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/instance/disks/0/type")
$value

The output is similar to the following:

PERSISTENT

Recursively query directory listings

If you want to return all contents under a directory, use the recursive=true
query parameter with your request:

 Linux

Connect to your Linux compute instance.

From your Linux compute instance, use the curl tool
to make a query. To recursively query the listings for a compute instance or
project metadata directory, run the following command:

curl "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_DIRECTORY/?recursive=true" -H "Metadata-Flavor: Google"

  Replace the PATH_TO_METADATA_DIRECTORY with the path to
  the VM instance or project metadata directory for which you want to recursively
  query the listings. For example:

    To view the attributes project metadata directory entry, the
    path to specify is project/attributes/.

    To view the disks VM instance metadata directory entry, the path
    to specify is instance/disks/.

For example, the following command recursively queries the instance
metadata listings for the disks/ directory.

  user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/disks/?recursive=true" -H "Metadata-Flavor: Google"

The output is similar to the following:

  [{"deviceName":"boot","index":0,"mode":"READ_WRITE","type":"PERSISTENT"},
  {"deviceName":"persistent-disk-1","index":1,"mode":"READ_WRITE","type":"PERSISTENT"},
  {"deviceName":"persistent-disk-2","index":2,"mode":"READ_ONLY","type":"PERSISTENT"}]

By default, recursive contents are returned in JSON format. If you want to
return these contents in text format, append the alt=text query parameter:

  user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/disks/?recursive=true&alt=text" -H "Metadata-Flavor: Google"

The output is similar to the following:

  0/device-name boot
  0/index 0
  0/mode READ_WRITE
  0/type PERSISTENT
  1/device-name persistent-disk-1
  1/index 1
  1/mode READ_WRITE
  1/type PERSISTENT
  2/device-name persistent-disk-1
  2/index 2
  2/mode READ_ONLY
  2/type PERSISTENT

 Windows

Connect to your Windows compute instance.

From your Windows compute instance, use the
Invoke-RestMethod command to make a
query. To recursively query the listings for a compute instance or project
metadata directory, run the following command:

  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
            -Uri "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_DIRECTORY/?recursive=true")
  $value

  Replace the PATH_TO_METADATA_DIRECTORY with the path to
  the VM instance or project metadata directory for which you want to recursively
  query the listings. For example:

    To view the attributes project metadata directory entry, the
    path to specify is project/attributes/.

    To view the disks VM instance metadata directory entry, the path
    to specify is instance/disks/.

For example, the following command recursively queries the instance
metadata listings for the disks/ directory.

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/instance/disks/?recursive=true")
$value

The output is similar to the following:

[{"deviceName":"boot","index":0,"mode":"READ_WRITE","type":"PERSISTENT"},
{"deviceName":"persistent-disk-1","index":1,"mode":"READ_WRITE","type":"PERSISTENT"},
{"deviceName":"persistent-disk-2","index":2,"mode":"READ_ONLY","type":"PERSISTENT"}]

By default, recursive contents are returned in JSON format. If you want to
return these contents in text format, append the alt=text query parameter:

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/instance/disks/?recursive=true&alt=text")
$value

The output is similar to the following:

0/device-name boot
0/index 0
0/mode READ_WRITE
0/type PERSISTENT
1/device-name persistent-disk-1
1/index 1
1/mode READ_WRITE
1/type PERSISTENT
2/device-name persistent-disk-1
2/index 2
2/mode READ_ONLY
2/type PERSISTENT

Format query output

By default, each endpoint has a predefined format for the response. Some endpoints
might return data in JSON format by default, while other endpoints might return
data as a string. You can override the default data format specification by
using the alt=json or alt=text query parameters, which return data in JSON
string format or as a plain text representation, respectively.

 Linux

Connect to your Linux compute instance.

From your Linux compute instance, use the curl tool
to make a query. To change the query response data format for a compute
instance or project metadata entry, run the following command:

curl "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY?alt=DATA_FORMAT" -H "Metadata-Flavor: Google"

Replace the following:

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

DATA_FORMAT: the format in which you want
the query response data—for example, text or json.

Example

For example, the tags key
automatically returns data in JSON format. You can return data in text
format instead, by specifying the alt=text query parameter.

Default query

  user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/tags" -H "Metadata-Flavor: Google"

The output is similar to the following:

  ["http-server", "db-client", "app-server", "mysql-server"]

Query with formatting

  user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/tags?alt=text" -H "Metadata-Flavor: Google"

The output is similar to the following:

  http-server
  db-client
  app-server
  mysql-server

 Windows

Connect to your Windows compute instance.

From your Windows compute instance, use the
Invoke-RestMethod command to make a
query. To change the query response data format for a compute instance or
project metadata entry, run the following command:

  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
            -Uri "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY?alt=DATA_FORMAT")
  $value

Replace the following:

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

DATA_FORMAT: the format in which you want
the query response data—for example, text or json.

Example

For example, the tags key
automatically returns data in JSON format. You can return data in text
format instead, by specifying the alt=text query parameter.

Default query

  PS C:>
  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
            -Uri "http://metadata.google.internal/computeMetadata/v1/instance/tags")
  $value

The output is similar to the following:

  ["http-server", "db-client", "app-server", "mysql-server"]

Query with formatting

  PS C:>
  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
            -Uri "http://metadata.google.internal/computeMetadata/v1/instance/tags?alt=text")
  $value

The output is similar to the following:

  http-server
  db-client
  app-server
  mysql-server

Obtain specific OAuth2 access tokens

By default, when you query the metadata server for an OAuth2 access token from the /computeMetadata/v1/instance/service-accounts/default/token endpoint, the returned token includes all scopes that you specified for the service account when you created or updated the instance.

To request an access token downscoped to specific, limited scopes, you must use the scopes query parameter in combination with the enforce_scopes=true query parameter. The scopes you request must be a subset of the scopes you specified for the instance.

Note: The enforce_scopes query parameter accepts true, 1, yes, or y. Explicitly setting enforce_scopes to false (or equivalent false values like 0, no, or n) causes the metadata server to reject the request with an HTTP 400 (Bad Request) error.
 Linux

Connect to your Linux compute instance.

From your Linux compute instance, use the curl tool to request a token with limited scopes:

curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token?enforce_scopes=true&scopes=SCOPE_1,SCOPE_2,..." -H "Metadata-Flavor: Google"

Replace SCOPE_1,SCOPE_2,... with a comma-separated list of OAuth2 scopes.

For example, to request a token downscoped to read-only access for Cloud Storage:

user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token?enforce_scopes=true&scopes=https://www.googleapis.com/auth/devstorage.read_only" -H "Metadata-Flavor: Google"

The output is similar to the following:

{
  "access_token": "ya29.c....",
  "expires_in": 3599,
  "token_type": "Bearer"
}

 Windows

Connect to your Windows compute instance.

From your Windows compute instance, use the Invoke-RestMethod command to request a token with limited scopes:

$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token?enforce_scopes=true&scopes=SCOPE_1,SCOPE_2,...")
$value

Replace SCOPE_1,SCOPE_2,... with a comma-separated list of OAuth2 scopes.

For example, to request a token downscoped to read-only access for Cloud Storage:

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token?enforce_scopes=true&scopes=https://www.googleapis.com/auth/devstorage.read_only")
$value

The output is similar to the following:

access_token    : ya29.c....
expires_in      : 3599
token_type      : Bearer

Alternatively, you can enforce this downscoping behavior for all token requests by setting the enable-access-token-enforce-scopes custom metadata key to true at the instance or project level. If you set this key to true, the metadata server automatically downscopes any token request that includes the scopes parameter, even if the request doesn't include enforce_scopes=true.

Query metadata changes using the wait-for-change feature

Given that metadata values can change while your compute instance is running, the
metadata server can be notified of metadata changes by using the
wait-for-change feature. With this option, the request only returns an
output when your specified metadata has changed.

You can use this feature on custom metadata or server-defined metadata, so if
anything changes about your compute instance or project, or if someone updates a custom
metadata entry, you can programmatically react to the change.

For example, you can perform a
request on the tags key so that the request only returns if the contents of
the tags metadata has changed. When the request returns, it provides the new
value of that metadata key.

The wait-for-change feature also lets you match with your request and
set timeouts.

When working with thewait-for-change feature, consider the following:

You can only perform a wait-for-change request on a
metadata endpoint or recursively on the contents of a directory. You cannot
perform a wait-for-change request on a directory listing.
If you try to do this, the metadata server fails your request and returns a
400 Invalid Request error.

You cannot perform a wait-for-change request for a service
account token. If you try to make a wait-for-change request to the service
account token URL, the request fails immediately and returns a
400 Invalid Request error.

To perform a wait-for-change request, query a metadata key and append the
?wait_for_change=true query parameter:

 Linux

Connect to your Linux compute instance.

From your Linux compute instance, use the curl tool
to make a query. To perform a wait-for-change request for a compute instance
or project metadata entry, run the following command:

curl "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY?wait_for_change=true" -H "Metadata-Flavor: Google"

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

After there is a change to the specified metadata key, the query returns
with the new value.

Examples

In this example, if a request is made to the setInstanceTags method, the
request returns with the new values:

  user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/tags?wait_for_change=true" -H "Metadata-Flavor: Google"

The output is similar to the following:

  http-server
  db-client

You can also perform a wait-for-change request recursively on the
contents of a directory:

  user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/attributes/?recursive=true&wait_for_change=true" -H "Metadata-Flavor: Google"

The metadata server returns the new contents if there is any change:

  {"foo":"bar","baz":"bat"}

 Windows

Connect to your Windows compute instance.

From your Windows compute instance, use the
Invoke-RestMethod command to make a
query. To perform a wait-for-change request for a compute instance or project
metadata entry, run the following command:

$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} `
          -Uri "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY?wait_for_change=true")
$value

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

After there is a change to the specified metadata key, the query returns
with the new value.

Examples

After there is a change to the specified metadata key, the query returns
with the new value. In this example, if a request is made to the
setInstanceTags method, the request returns with the new values:

  PS C:>
  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
            -Uri "http://metadata.google.internal/computeMetadata/v1/instance/tags?wait_for_change=true")
  $value

The output is similar to the following:

  http-server
  db-client

You can also perform a wait-for-change request recursively on the contents of a
directory:

  PS C:>
  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
            -Uri "http://metadata.google.internal/computeMetadata/v1/instance/attributes?recursive=true&wait_for_change=true")
  $value

The metadata server returns the new contents if there is any change:

  {"foo":"bar","baz":"bat"}

Use ETags

When you submit a wait-for-change query, the metadata server returns a
response if anything has changed in the contents of that metadata. However,
there is an inherent race condition between a metadata update and a
wait-for-change request being issued, so it's useful to have a reliable way to
know you are getting the latest metadata value.

To help with this, you can use the last_etag query parameter, which compares
the ETag value you provide with the ETag value saved on the metadata server. If
the ETag values match, then the wait-for-change request is accepted. If the
ETag values don't match, this indicates that the contents of the metadata has
changed since the last time you retrieved the ETag value, and the metadata
server returns immediately with this latest value.

 Linux
To get the current ETag value for a metadata key, complete the following
steps:

Connect to your Linux compute instance.

Make a request to that key and print the headers. To do this, use the
curl tool with the -v flag.
To get the current ETag for a compute instance or project metadata entry, run
the following command:

curl -v "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY" -H "Metadata-Flavor: Google"

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

For example, the following command gets the current ETag value for the
tags instance metadata key.

  user@myinst:~$ curl -v "http://metadata.google.internal/computeMetadata/v1/instance/tags" -H "Metadata-Flavor: Google"

The output is similar to the following:

* About to connect() to metadata port 80 (#0)
* Trying 169.254.169.254... connected
* Connected to metadata (169.254.169.254) port 80 (#0)
> GET /computeMetadata/v1/instance/tags HTTP/1.1
> User-Agent: curl/7.19.7 (x86_64-pc-linux-gnu) libcurl/7.19.7 OpenSSL/0.9.8k zlib/1.2.3.3 libidn/1.15
> Host: metadata
> Accept: */*
>
< HTTP/1.1 200 OK
< Content-Type: application/text
< ETag: 411261ca6c9e654e
< Date: Wed, 13 Feb 2013 22:43:45 GMT
< Server: Metadata Server for VM
< Content-Length: 26
< X-XSS-Protection: 1; mode=block
< X-Frame-Options: SAMEORIGIN
<
http-server
db-client

You can then use that ETag value with the curl tool
command in your wait-for-change request. To use the ETag value for the
wait-for-change request of instance or project metadata, run the
following command:

  curl "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY?wait_for_change=true&last_etag=ETAG" -H "Metadata-Flavor: Google"

Replace the following:

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

ETAG: the ETag value for the metadata key.

In this example, the following command uses the ETag value for the
tags key and queries for the instance metadata entry.

  user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/tags?wait_for_change=true&last_etag=411261ca6c9e654e" -H "Metadata-Flavor: Google"

The metadata server matches your specified ETag value, and if that value
changes, the request returns with the new contents of your metadata key.

 Windows
To get the current ETag value for a metadata key, complete the following
steps:

Connect to your Windows compute instance.

Make a request to that key and print the headers. On Windows, use the
Invoke-WebRequest command.
To get the current ETag for a compute instance or project metadata entry, run
the following command:

  $value = (Invoke-WebRequest -Headers @{'Metadata-Flavor' = 'Google'} `
  -Uri http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY)

$value.Headers.ETag

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

For example, the following command gets the current ETag value for the
tags instance metadata key.

  PS C:>
  $value = (Invoke-WebRequest -Headers @{'Metadata-Flavor' = 'Google'} `
  -Uri http://metadata.google.internal/computeMetadata/v1/instance/tags)

$value.Headers.ETag

The output is similar to the following:

  * About to connect() to metadata port 80 (#0)
  * Trying 169.254.169.254... connected
  * Connected to metadata (169.254.169.254) port 80 (#0)
  > GET /computeMetadata/v1/instance/tags HTTP/1.1
  > User-Agent: curl/7.19.7 (x86_64-pc-linux-gnu) libcurl/7.19.7 OpenSSL/0.9.8k zlib/1.2.3.3 libidn/1.15
  > Host: metadata
  > Accept: /
  >
  < HTTP/1.1 200 OK
  < Content-Type: application/text
  < ETag: 411261ca6c9e654e
  < Date: Wed, 13 Feb 2013 22:43:45 GMT
  < Server: Metadata Server for VM
  < Content-Length: 26
  < X-XSS-Protection: 1; mode=block
  < X-Frame-Options: SAMEORIGIN
  <
  http-server
  db-client

You can then use that ETag value in your wait-for-change request. To
use the ETag value for the wait-for-change request of instance or
project metadata, run the following command:

  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
          -Uri "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY?wait_for_change=true&last_etag=ETAG")
  $value

Replace the following:

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

ETAG: the ETag value for the metadata key.

In this example, the following command uses the ETag value for the
tags key and queries for the instance metadata entry.

  PS C:>
  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
            -Uri "http://metadata.google.internal/computeMetadata/v1/instance/tags?wait_for_change=true&last_etag=411261ca6c9e654e")
  $value

The metadata server matches your specified ETag value, and if that value
changes, the request returns with the new contents of your metadata key.

 Python
The following Python sample shows how to programmatically watch the
metadata server for changes.

This sample sets the initial ETag to 0. The metadata server doesn't
return a response with 0 as the ETag value. When 0 is specified as the
last ETag in a request, the metadata server responds with the current value
and ETag. This saves a bit of the code needed to get the initial value and
ETag.

last_etag = "0"

while True:
    r = requests.get(
        url,
        params={"last_etag": last_etag, "wait_for_change": True},
        headers=METADATA_HEADERS,
    )

    # During maintenance the service can return a 503, so these should
    # be retried.
    if r.status_code == 503:
        time.sleep(1)
        continue
    r.raise_for_status()

    last_etag = r.headers["etag"]

Set timeouts

If you would like your wait-for-change request to time out after a certain
number of seconds, you can set the timeout_sec parameter. The timeout_sec
parameter limits the wait time of your request to the number of seconds you specified,
and when the request reaches that limit, it
returns the current contents of the metadata key.

When you set the timeout_sec parameter, the request always returns after the
specified number of seconds, whether or not the metadata value has actually
changed. It is only possible to set an integer value for your timeout.

 Linux

Connect to your Linux compute instance.

From your Linux compute instance, use the curl tool
to make a query. To perform a wait-for-change request with a time out
value for a compute instance or project metadata entry, run the following
command:

  curl "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY?wait_for_change=true&timeout_sec=TIMEOUT" -H "Metadata-Flavor: Google"

Replace the following:

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

TIMEOUT: the time out value.

For example, the following command performs a wait-for-change request that
is set to time out after 360 seconds:

  user@myinst:~$ curl "http://metadata.google.internal/computeMetadata/v1/instance/tags?wait_for_change=true&timeout_sec=360" -H "Metadata-Flavor: Google"

 Windows

Connect to your Windows compute instance.

From your Windows compute instance, use the
Invoke-RestMethod command to make a query.
To perform a wait-for-change request with a time out value for a compute
instance or project metadata entry, run the following command:

  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
          -Uri "http://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY?wait_for_change=true&timeout_sec=TIMEOUT")
  $value

Replace the following:

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

TIMEOUT: the time out value.

For example, the following command performs a wait-for-change request that
is set to time out after 360 seconds:

  PS C:>
  $value = (Invoke-RestMethod -Headers @{'Metadata-Flavor' = 'Google'}
            -Uri "http://metadata.google.internal/computeMetadata/v1/instance/tags?wait_for_change=true&timeout_sec=360")
  $value

Query metadata by using the HTTPS metadata server endpoint

The HTTPS metadata server endpoint (https://metadata.google.internal/computeMetadata/v1) provides added
security for transmission of information between the metadata server and the compute instance.

To use the HTTPS metadata server endpoint, the compute instance must meet the following
requirements:

The guest environment must be
running on the compute instance.

The disable-https-mds-setup metadata key for the compute instance must be
set to FALSE.

The compute instance must be a Shielded VM. This is because the HTTPS
metadata server requires the use of Unified Extensible
Firmware Interface (UEFI) and Virtual Trusted Platform Module (vTPM) for
verifying certificates.

For an overview of how queries to the HTTPS metadata server endpoint are
handled, see
HTTPS metadata server endpoint.
You can perform all the same queries to the metadata server whether you use the
HTTPS or the HTTP endpoint. However, to call the HTTPS endpoint you
must specify the path to the client identity certificates and in some cases the
root certificate.

The following commands demonstrate how to query the metadata server by using the
HTTPS endpoint.

 Linux

Connect to your Linux compute instance.

From your Linux compute instance, use the
curl tool to make a query and
specify the client identity certificate. Optionally, you can also specify
the root certificate.

curl "https://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY" \
  -E CLIENT_CERTIFICATE \
  [--cacert ROOT_CERTIFICATE] \
  -H "Metadata-Flavor: Google"

Replace the following:

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

CLIENT_CERTIFICATE: the path to the
client identity certificate: /run/google-mds-mtls/client.key.

Optional: ROOT_CERTIFICATE: the path to the
root certificate: /run/google-mds-mtls/root.crt. You must specify this
value if the root certificate isn't added to the OS trust store.

For example, to query the boot image for a compute instance, run the following
query:

user@myinst:~$
curl "https://metadata.google.internal/computeMetadata/v1/instance/image" \
  -E /run/google-mds-mtls/client.key \
  -H "Metadata-Flavor: Google"

The output is similar to the following:

projects/rhel-cloud/global/images/rhel-8-v20210122

If you see an error message, review the
troubleshooting documentation.

 Windows

Connect to your Windows compute instance.

Get the client identity certificate
by using one of the following commands:

$cert = Get-PfxCertificate -FilePath "C:\ProgramData\Google\Compute Engine\mds-mtls-client.key.pfx"

$cert = Get-ChildItem Cert:\LocalMachine\My | Where-Object { $_.Issuer -like "google.internal" }

From your Windows compute instance, use the
Invoke-RestMethod command and specify the client identity
certificate to make a query.

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} -Certificate CLIENT_CERTIFICATE `
          -Uri "https://metadata.google.internal/computeMetadata/v1/PATH_TO_METADATA_ENTRY")
$value

Replace the following:

CLIENT_CERTIFICATE: the path to the
client identity certificate
on the compute instance. This is the $cert variable that is set in the previous step.

  Replace the PATH_TO_METADATA_ENTRY with the path to
  the VM instance or project metadata key for which you want to query the value.
  If the key is in a sub-directory of the instance or project directory, ensure
  to also include the sub-directory. For example:

    To view the project-id metadata key, which is stored in
    project metadata, specify project/project-id.

    To view the image metadata key, which is stored in VM instance
    metadata, specify instance/image.

    To view the enable-oslogin which can be stored in the
    attributes sub-directory of either project or VM instance metadata,
    specify either project/attributes/enable-oslogin or
    instance/attributes/enable-oslogin depending on your use case.

For example, to query the boot image for a Windows server 2019 instance, run
the following query:

PS C:\>
$value = (Invoke-RestMethod `
          -Headers @{'Metadata-Flavor' = 'Google'} -Certificate $cert `
          -Uri "https://metadata.google.internal/computeMetadata/v1/instance/image")
$value

The output is similar to the following:

projects/windows-cloud/global/images/windows-server-2019-dc-v20210112

Limitations

Any requests that contain the header X-Forwarded-For are
automatically rejected by the metadata server. This header generally
indicates that the request was proxied and might not be a request made by an
authorized user. For security reasons, all such requests are rejected.

When you use the curl command to retrieve metadata from the server, note that
some encoded characters aren't supported in the request path.
Encoded characters are only supported in the query path.

For example, the following request might not work:

curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/123456789-compute%40developer.gserviceaccount.com/?query_path=https%3A%2F%2Flocalhost%3A8200%2Fexample%2Fquery&another_param=true" -H "Metadata-Flavor: Google"

For this request to work, you must replace the unsupported encoded character
in the request path (%40) with the equivalent accepted value (@).

curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/1234567898-compute@developer.gserviceaccount.com/?query_path=https%3A%2F%2Flocalhost%3A8200%2Fexample%2Fquery&another_param=true" -H "Metadata-Flavor: Google"

The following table summarises the encoded characters that aren't supported in
a request path.

Encoded character
Accepted value

%21

!

%24

$

%27

'

%28

(

%29

)

%2A

*

%2C

,

%40

@

Status codes

When you make a request to the metadata server, the metadata server returns
standard HTTP status codes to indicate success or failure. Sometimes, network
conditions or host events can cause the metadata server to fail your request and
return an error code. In these cases, you should design your application to be
fault-tolerant and to be able to recognize and handle these errors.

For a detailed list of status codes that can be returned, see
Troubleshoot server codes.

View the custom metadata for your compute instances

You can view the custom metadata values for your Compute Engine instances in one of
the following ways:

View project metadata

View zonal metadata

View instance metadata

View project metadata

To view custom metadata that applies to all compute instances in your project, use one
of the following methods.

 Console

In the Google Cloud console, go to the Metadata page.
Go to the Metadata page

On the Metadata page, you see a list of all custom project metadata
entries for your project.

 gcloud
Use the
gcloud compute project-info describe command
to query project metadata:

gcloud compute project-info describe --flatten="commonInstanceMetadata[]"

The output is similar to the following:

---
fingerprint: HcSFdS_1_1I=
items:
- key: ssh-keys
  value: USERNAME:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDWZ...
kind: compute#metadata

 REST
To query project metadata, create a GET request to the
project.get method.

Replace PROJECT_ID with your project ID.

GET https://compute.googleapis.com/compute/v1/projects/PROJECT_ID

The output is similar to the following:

"kind": "compute#project",
"id": "XXXXXXX",
"creationTimestamp": "2018-12-10T08:34:33.616-08:00",
"name": "YOUR_PROJECT",
"commonInstanceMetadata": {
  "kind": "compute#metadata",
  "fingerprint": "XXXXXCdg=",
  "items": [
    {
      "key": "enable-guest-attributes",
      "value": "TRUE"
    },
    {
      "key": "enable-os-inventory",
      "value": "true"
    },
    {
      "key": "enable-osconfig",
      "value": "TRUE"
    },
    {
      "key": "enable-oslogin",
      "value": "TRUE"
    },
    {
      "key": "sshKeys",
      "value": "XXXXX"
    }
  ]
}, ...

View zonal metadata

To view custom metadata that applies to all compute instances in a specific zone in
a project, use one of the following methods.

 gcloud
To query the custom zonal metadata, use the
gcloud compute project-zonal-metadata describe command.

gcloud compute project-zonal-metadata describe \
    --zone=ZONE \
    --project=PROJECT_ID

Replace the following:

PROJECT_ID: your project ID

ZONE: the zone for which you want to view the
zonal metadata.

The output is similar to the following:

{
  "fingerprint": "VlRIl8dx9vk=",
  "metadata": {
    items: {
      "key-1": "value-1",
      "key-2": "value-2"
    }
  }
}

 REST
To query the custom zonal metadata, make a GET request to the
instanceSettings().get method

GET https://compute.googleapis.com/compute/v1/projects/PROJECT_ID/zones/ZONE/instanceSettings

Replace the following:

PROJECT_ID: your project ID

ZONE: the zone for which you want to view the
zonal metadata.

The output is similar to the following:

{
  "fingerprint": "VlRIl8dx9vk=",
  "metadata": {
    items: {
      "key-1": "value-1",
      "key-2": "value-2"
    }
  }
}

View instance metadata

To view metadata that applies to a single compute instance in your project, use one of
the following methods.

 Console

In the Google Cloud console, go to the VM instances page.
Go to VM instances

Click the name of the compute instance for which you want to view metadata.

SSH keys for this VM. In the Security and access section,
view the SSH keys field.

A value of None indicates there are no SSH keys stored in instance
metadata.

Any other value indicates that there are SSH keys stored in instance
metadata.

SSH keys for a project. In the Security and access section,
view the Block project-wide SSH keys field.

A value of On indicates that the value of the metadata key
block-project-ssh-keys is TRUE in instance metadata.

A value of Off indicates that the value of the metadata key
block-project-ssh-keys is FALSE, or that the key isn't set.

All other custom metadata. View the Custom metadata section.
You see all custom metadata keys and values, other than SSH key
metadata.

 gcloud
Use the
gcloud compute instances describe command
to query instance metadata:

gcloud compute instances describe INSTANCE_NAME --flatten="metadata[]"

Replace INSTANCE_NAME with the name of the compute instance that you want to
find metadata for.

The output is similar to the following:

---
fingerprint: MTgTJ5m-Cjs=
items:
- key: enable-oslogin
  value: 'true'
kind: compute#metadata

 REST
To query metadata for a specific compute instance, send a GET request to the
instances.get method.

GET https://compute.googleapis.com/compute/v1/projects/PROJECT_ID/zones/ZONE/instances/INSTANCE_NAME

The output is similar to the following:

......
"metadata": {
"kind": "compute#metadata",
"fingerprint": "XXXXXXVo=",
"items": [
  {
    "key": "enable-oslogin",
    "value": "true"
  }
]
},....

Replace the following:

PROJECT_ID: your project ID

ZONE: the zone where the compute instance is located

INSTANCE_NAME: the name of the compute instance

What's next

Learn more about VM metadata.

Learn how to set custom metadata.

Learn how to set and query guest attributes.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-08-26 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-08-26 UTC."],[],[]]
