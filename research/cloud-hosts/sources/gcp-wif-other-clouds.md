Home

          Documentation

          Security

          IAM

          Identity and Access Management (IAM)

          Guides

    Send feedback

      Configure Workload Identity Federation with AWS or Azure VMs

      Stay organized with collections

      Save and categorize content based on your preferences.

This guide describes how to use Workload Identity Federation to let AWS and
Azure VM workloads authenticate to Google Cloud without a service account key.

If you use Amazon Elastic Kubernetes Service (Amazon EKS) or Azure Kubernetes
Service (AKS), see Configure Workload Identity Federation with Kubernetes
to learn how to configure Workload Identity Federation for your clusters. This
page covers only configuring Workload Identity Federation for AWS and Azure
VMs.

By using Workload Identity Federation, workloads that run on AWS EC2 and
Azure VMs can exchange their environment-specific credentials for short-lived
Google Cloud Security Token Service tokens.

Environment-specific credentials include the following:

AWS EC2 instances can use instance profiles to request
temporary credentials.

Azure VMs can use managed identities
to obtain Azure access tokens.

By setting up Workload Identity Federation, you can let these workloads
exchange these environment-specific credentials against short-lived
Google Cloud credentials. Workloads can use these short-lived credentials
to access Google Cloud APIs.

Before you begin

Set up authentication.

Important: New Amazon EC2 instances use IMDSv2.
If your instance uses IMDSv2, you must follow the gcloud CLI
instructions instead of the Google Cloud console instructions. To learn
more, see Amazon EC2 Instance Metadata Service (IMDSv2) by default.

      Select the tab for how you plan to use the samples on this page:

        Console

        When you use the Google Cloud console to access Google Cloud services and
        APIs, you don't need to set up authentication.

        gcloud

    In the Google Cloud console, activate Cloud Shell.

    Activate Cloud Shell

      At the bottom of the Google Cloud console, a
      Cloud Shell
      session starts and displays a command-line prompt. Cloud Shell is a shell environment
      with the Google Cloud CLI
      already installed and with values already set for
      your current project. It can take a few seconds for the session to initialize.

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

      Set up ADC for a local development environment
    in the Google Cloud authentication documentation.

Prepare your external identity provider

You only need to perform these steps once for each Microsoft Entra ID tenant or
AWS account.

 AWS
Google Cloud supports two mechanisms for federating with AWS workloads:

AWS outbound identity federation: AWS acts as an OpenID Connect (OIDC) identity provider (IdP) and issues short-lived JSON Web Tokens (JWTs) to your workloads.

If you're using AWS outbound identity federation, to set up Workload Identity Federation, first follow the instructions in the AWS Identity and Access Management User Guide to configure permissions and obtain your account's OIDC issuer URL. Then, follow the instructions in Configure Workload Identity Federation with other providers (OIDC) to set up your pool, provider, and credential configuration.

AWS IAM Credentials: Your workloads use AWS temporary security credentials (IAM roles or instance profiles), and Google Cloud verifies them using the AWS GetCallerIdentity API. You don't need to make any configuration changes in your AWS account for this option.

The remainder of this page describes how to configure federation using the AWS IAM Credentials mechanism.

After you configure a workload identity pool to trust your
AWS account, you can let AWS users
and AWS roles
use permanent or temporary AWS security credentials to obtain
short-lived Google Cloud credentials.

 Azure
You must create a new Microsoft Entra ID application
in your Microsoft Entra ID tenant and configure it so that it can be used for
Workload Identity Federation.

After you configure a workload identity pool to trust the
application, Azure users and service principals can request access tokens
for this application and exchange these access tokens against
short-lived Google Cloud credentials.

To create the application, do the following:

Create a Microsoft Entra ID application and service principal.

Set an Application ID URI for the application.
You can use the default Application ID URI
(APPID) or specify a custom URI.

You need the Application ID URI later when you configure the workload
identity pool provider.

To let an application obtain access tokens for the Microsoft Entra ID application,
you can use managed identities:

Create a managed identity.
Note the Object ID of the managed identity. You need it later when
you configure impersonation.

Assign the managed identity
to a virtual machine or another resource that runs your application.

Note: If you use Azure's default settings, the new application grants
all users in the Microsoft Entra ID tenant permission to obtain access tokens.
Use app role assignments
to restrict which identities can obtain access tokens for the application.

Configure Workload Identity Federation

You only need to perform these steps once per AWS account or
Microsoft Entra ID tenant. You can then use the same workload identity
pool and provider for multiple workloads and across multiple Google Cloud projects.

To start configuring Workload Identity Federation, do the following:

      In the Google Cloud console, on the project selector page,
        select or create a Google Cloud project.

  Roles required to select or create a project

      Select a project: Selecting a project doesn't require a specific
      IAM role—you can select any project that you've been
      granted a role on.

      Create a project: To create a project, you need the Project Creator role
      (roles/resourcemanager.projectCreator), which contains the
      resourcemanager.projects.create permission. Learn how to grant
      roles.

      Go to project selector

It's best to
use a dedicated project to manage workload identity pools and providers.

      Verify that billing is enabled for your Google Cloud project.

              Enable the IAM, Resource Manager, Service Account Credentials, and Security Token Service APIs.

Roles required to enable APIs

          To enable APIs, you need the serviceusage.services.enable permission. If you
          created the project, then you likely already have this permission through the
          Owner role (roles/owner). Otherwise, you can get this permission through the
          Service Usage Admin role (roles/serviceusage.serviceUsageAdmin).
          Learn how to grant roles.

Enable the APIs

Define an attribute mapping and condition

The environment-specific credentials of your AWS or Azure workload contain multiple attributes,
and you must decide which attribute you want to use as subject identifier
(google.subject) in Google Cloud.

Google Cloud uses the subject identifier in Cloud Audit Logs and in
principal identifiers to uniquely identify
an AWS or Azure user or role.

Optionally, you can map additional attributes.
You can then refer to these additional attributes when granting access to
resources.

 AWS
Your attribute mapping can use the
response fields for GetCallerIdentity
as source attributes. These fields include the following:

account: the AWS account number.

arn: the AWS ARN of the external entity.

userid: the unique identifier of the calling entity.

If your application runs on an Amazon Elastic Compute Cloud (EC2) instance with an attached role,
you can use the following attribute mapping:

google.subject=assertion.arn
attribute.account=assertion.account
attribute.aws_role=assertion.arn.extract('assumed-role/{role_name}/')
attribute.aws_ec2_instance=assertion.arn.extract('assumed-role/{role_and_session}').extract('/{session}')

The mapping does the following:

Uses the ARN as subject identifier—for example:
"arn:aws:sts::000000000000:assumed-role/ec2-my-role/i-00000000000000000

Introduces a custom attribute account and assigns it the AWS account
ID

Introduces a custom attribute aws_role and assigns it the AWS role
name—for example: ec2-my-role

Introduces a custom attribute aws_ec2_instance and assigns it the EC2
instance ID—for example: i-00000000000000000

Using this mapping, you can grant access to:

A specific EC2 instance:

principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.aws_ec2_instance/EC2_INSTANCE_ID

All users and instances in a role:

principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.aws_role/ROLE_NAME

 Azure
Your attribute mappings can use the
claims embedded in Azure access tokens,
including custom claims, as source attributes.
In most cases, it's best to use the sub claim as subject identifier:

google.subject=assertion.sub

When the sub claim surpasses the 127-character limit for google.subject,
we recommend that you use the extract function
to derive a subject identifier—for example:

google.subject=assertion.sub.extract('/eid1/c/pub/t/{sub_claim}')

For an access token issued to a managed identity,
the sub claim contains the Object ID of the managed identity. If you use
a different claim, make sure that the claim is unique and can't be reassigned.

If you're unsure about the list of claims you can reference, do the following:

Connect to an Azure VM that has an assigned managed identity.

Obtain an access token from the Azure Instance Metadata Service (IMDS):

Bash

curl \
  "http://169.254.169.254/metadata/identity/oauth2/token?resource=APP_ID_URI&api-version=2018-02-01" \
  -H "Metadata: true" | jq -r .access_token

This command uses the jq tool.
jq is available by default in Cloud Shell.

PowerShell

$SubjectTokenType = "urn:ietf:params:oauth:token-type:jwt"
$SubjectToken = (Invoke-RestMethod `
  -Uri "http://169.254.169.254/metadata/identity/oauth2/token?resource=APP_ID_URI&api-version=2018-02-01" `
  -Headers @{Metadata="true"}).access_token
Write-Host $SubjectToken

Replace APP_ID_URI with the Application ID URI
of the application that you've configured for Workload Identity Federation.

In a web browser, go to https://jwt.ms/ and
paste the access token into the field.

Click Claims to view the list of claims embedded in the access token.

For service identities, it's typically not necessary to create a mapping
for google.groups or any custom attributes.

Optionally, define an attribute condition. Attribute conditions
are CEL expressions that can check assertion attributes and target attributes.
If the attribute condition evaluates to true for a given credential, the
credential is accepted. Otherwise, the credential is rejected.

 AWS
You can use an attribute condition to restrict which IAM users and roles
can use Workload Identity Federation to obtain short-lived Google Cloud
tokens.

For example, the following condition restricts access to AWS roles and
disallows other IAM identifiers:

assertion.arn.startsWith('arn:aws:sts::AWS_ACCOUNT_ID:assumed-role/')

 Azure
You can use an attribute condition to restrict which users and service principals
can use Workload Identity Federation to obtain short-lived Google Cloud
tokens. Alternatively, you can configure your Microsoft Entra ID
application to use
app role assignments.

Create the workload identity pool and provider

  Required roles

      To get the permissions that
      you need to configure Workload Identity Federation,

      ask your administrator to grant you the
    following IAM roles on the project:

            Workload Identity Pool Admin  (roles/iam.workloadIdentityPoolAdmin)

            Service Account Admin  (roles/iam.serviceAccountAdmin)

  For more information about granting roles, see Manage access to projects, folders, and organizations.

        You might also be able to get
        the required permissions through custom
        roles or other predefined
        roles.

Alternatively, the IAM Owner (roles/owner) basic role also
includes permissions to configure identity federation.

You should not grant basic roles in a production environment, but you can grant them in a
development or test environment.

You now have collected all of the information that you need to create a workload identity
pool and provider:

 Console

In the Google Cloud console, go to the New workload provider and pool
page.

Go to New workload provider and pool

In the Create an identity pool section, enter the following:

Name: Name for the pool. The name is also used as the pool ID.
You can't change the pool ID later.

Description: Text that describes the purpose of the pool.

Click Continue.

Configure provider settings:

 AWS
Configure the following provider settings:

Select a provider: AWS.

Provider name: the name for the provider. The name is also used
as the provider ID. You cannot change the provider ID later.

 Azure
Configure the following provider settings:

Select a provider: OpenID Connect (OIDC).

Provider name: Name for the provider. The name is also used
as the provider ID. You cannot change the provider ID later.

Issuer URL: https://sts.windows.net/TENANT_ID.
Replace TENANT_ID with the tenant ID
(GUID) of your Microsoft Entra ID tenant.

Allowed audiences: Application ID URI that you used when
you registered the application in Microsoft Entra ID.

Click Continue.

In the Configure provider attributes section, add
the attribute mappings that you've identified previously.

In the Attribute conditions section, enter the
attribute condition
that you identified previously. Leave the field blank if you don't have
an attribute condition.

Click Save to create the workload identity pool and provider.

 gcloud

Create a new workload identity pool:

gcloud iam workload-identity-pools create POOL_ID \
    --location="global" \
    --description="DESCRIPTION" \
    --display-name="DISPLAY_NAME"

Replace the following:

POOL_ID: the unique ID for the pool.

DISPLAY_NAME: the name of the pool.

DESCRIPTION: the description of the pool. This description
appears when granting access to pool identities.

Add a workload identity pool provider:

 AWS
To create the workload identity pool provider for AWS, execute the
following command:

gcloud iam workload-identity-pools providers create-aws PROVIDER_ID \
  --location="global" \
  --workload-identity-pool="POOL_ID" \
  --account-id="ACCOUNT_ID" \
  --attribute-mapping="MAPPINGS" \
  --attribute-condition="CONDITIONS"

Replace the following:

PROVIDER_ID: the unique ID for the provider.

POOL_ID: the ID of the pool.

ACCOUNT_ID: the 12-digit number
that identifies your AWS account.

MAPPINGS: Comma-separated list of attribute mappings that you've identified previously.

CONDITIONS: Attribute condition that you've identified previously.
Remove the parameter if you don't have an attribute condition.

Example:

gcloud iam workload-identity-pools providers create-aws example-provider \
  --location="global" \
  --workload-identity-pool="pool-1" \
  --account-id="123456789000" \
  --attribute-mapping="google.subject=assertion.arn"

 Azure
To create the workload identity pool provider for Azure, execute the
following command:

gcloud iam workload-identity-pools providers create-oidc PROVIDER_ID \
    --location="global" \
    --workload-identity-pool="POOL_ID" \
    --issuer-uri="ISSUER_URI" \
    --allowed-audiences="APPLICATION_ID_URI" \
    --attribute-mapping="MAPPINGS" \
    --attribute-condition="CONDITIONS"

Replace the following:

PROVIDER_ID: The unique ID for the provider.

POOL_ID: The ID of the pool.

ISSUER_URI: The tenant ID
(GUID) of your Microsoft Entra ID tenant, sometimes formatted as
https://sts.windows.net/TENANT_ID. The
issuer URI can vary, and to find your issuer URI, you can debug
your JWT using JWT.io.

APPLICATION_ID_URI: Application ID
URI that you used when you registered the application
in Microsoft Entra ID.

MAPPINGS: The comma-separated list of
attribute mappings that you
previously identified.

CONDITIONS: (Optional) The attribute condition
that you previously identified.

Example:

gcloud iam workload-identity-pools providers create-oidc example-provider \
    --location="global" \
    --workload-identity-pool="pool-1" \
    --issuer-uri="https://sts.windows.net/00000000-1111-2222-3333-444444444444" \
    --allowed-audiences="api://my-app" \
    --attribute-mapping="google.subject=assertion.sub,google.groups=assertion.groups"

Note: The prefix gcp- is reserved and can't be used in a pool or provider ID.
Authenticate a workload

You must perform these steps once per workload.

Allow your external workload to access Google Cloud resources

To provide your workload with access to Google Cloud resources, we
recommend that you grant direct resource access to the principal. In this case,
the principal is the federated user. Some Google Cloud products have
Google Cloud API limitations.
If your workload calls an API endpoint that has a limitation, you can instead
use service account impersonation. In this case, the principal is the
Google Cloud service account, which acts as the identity. You grant access
to the service account on the resource.

Direct resource access
You can grant access to a federated identity directly on resources by using
the Google Cloud console or the gcloud CLI.

Console
To use the Google Cloud console to grant IAM roles
directly on a resource, you must go to the resource's page, and then
grant the role. The following example shows you how to go
to the Cloud Storage page and grant the role Storage Object Viewer
(roles/storage.objectViewer) to a federated identity directly on a
Cloud Storage bucket.

In the Google Cloud console, go to the Cloud Storage Buckets page.

Go to Buckets

In the list of buckets, click the name of the bucket for which you
want to grant the role.

Select the Permissions tab near the top of the page.

Click the add_box
Grant access button.

The Add principals dialog appears.

In the New principals field, enter one or more identities
that need access to your bucket.

 By subject

principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/subject/SUBJECT

Replace the following:

PROJECT_NUMBER: the project
number

POOL_ID: the workload
pool ID

SUBJECT: the individual
subject mapped from your IdP—for example,
administrator@example.com

 By group

principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/group/GROUP

Replace the following:

PROJECT_NUMBER: the project
number

WORKLOAD_POOL_ID: the workload
pool ID

GROUP: the group
mapped from your IdP—for example:
administrator-group@example.com

 By attribute

principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.ATTRIBUTE_NAME/ATTRIBUTE_VALUE

Replace the following:

PROJECT_NUMBER: the project
number

WORKLOAD_POOL_ID: the workload
pool ID

ATTRIBUTE_NAME: one of the
attributes that was mapped from your IdP

ATTRIBUTE_VALUE: the value
of the attribute

Select a role (or roles) from the Select a role drop-down menu.
The roles you select appear in the pane with a short description of
the permissions they grant.

Click Save.

 gcloud
To use the gcloud CLI to grant IAM roles on a
resource in a project, do the following:

Obtain the project number of the project in which the resource
is defined.

gcloud projects describe $(gcloud config get-value core/project) --format=value\(projectNumber\)

Grant access to the resource.

    To use the gcloud CLI to grant the role Storage Object Viewer
    (roles/storage.objectViewer) to external identities that meet certain criteria,
    run the following command.

  By subject

gcloud storage buckets add-iam-policy-binding BUCKET_ID \
    --role=roles/storage.objectViewer \
    --member="principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/subject/SUBJECT"

  By group

gcloud storage buckets add-iam-policy-binding BUCKET_ID \
    --role=roles/storage.objectViewer \
    --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/group/GROUP"

  By attribute

gcloud storage buckets add-iam-policy-binding BUCKET_ID \
    --role=roles/storage.objectViewer \
    --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.ATTRIBUTE_NAME/ATTRIBUTE_VALUE"

Replace the following:

BUCKET_ID:
the bucket on which to grant access

PROJECT_NUMBER: the project number.
of the project that contains the workload identity pool

POOL_ID: the pool ID of the workload identity pool

SUBJECT: the expected value for the attribute that
you've mapped
to google.subject

GROUP: the expected value for the attribute that
you've mapped
to google.groups

ATTRIBUTE_NAME: the name of a custom attribute in
your attribute mapping

ATTRIBUTE_VALUE: the value of the custom attribute in your attribute mapping

You can grant roles on any Google Cloud resource that supports
IAM allow policies.

Note: You must use the project number, not the project ID, in the
member identifier.

Service account impersonation

To create a service account for the external workload, do the following:

              Enable the IAM, Security Token Service, and Service Account Credentials APIs.

Roles required to enable APIs

          To enable APIs, you need the serviceusage.services.enable permission. If you
          created the project, then you likely already have this permission through the
          Owner role (roles/owner). Otherwise, you can get this permission through the
          Service Usage Admin role (roles/serviceusage.serviceUsageAdmin).
          Learn how to grant roles.

Enable the APIs

Create a service account
that represents the workload. We recommend that you use a dedicated service account for each workload.
The service account doesn't need to be in the same project as the
workload identity pool, but you must refer to the project that
contains the service account.

Grant the service account access
to resources that you want external identities to access.

To let the federated identity impersonate the service account, do the
following:

Console
To use the Google Cloud console to grant IAM roles
to a federated identity with service account, do the following:

Service Account in the same project

To grant access using service account impersonation for a
service account in the same project, do the following:

Go to the Workload Identity Pools page.

Go to Workload Identity Pools

Select Grant access.

In the Grant access to service account dialog, select
Grant access using Service Account impersonation.

In the Service accounts list, select the
service account for the external identities to impersonate,
and do the following:

To choose which identities in the pool can impersonate the
service account, perform one of the following actions:

To allow only specific identities of the workload
identity pool to impersonate the service account, select
Only identities matching the filter.

In the Attribute name list, select the attribute
that you want to filter on.

In the Attribute value field, enter the expected
value of the attribute; for example, if you use an
attribute mapping google.subject=assertion.sub, set
Attribute name to subject and Attribute value
to the value of the sub claim in tokens that are
issued by your external identity provider.

To save the configuration, click Save and then
Dismiss.

Service account in a different project
Note: Service accounts from different projects won't appear in the
"CONNECTED SERVICE ACCOUNTS" section of your Workload Identity Pool.
To grant access using service account impersonation for a
service account in a different project, do the following:

Go to the Service Accounts page.

Go to Service Accounts

Select the service account that you want to impersonate.

Click Manage access.

Click Add principal.

In the New principal field, enter one of the following
principal identifiers
for the identities in your pool that will impersonate the
service account.

 By subject

principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/subject/SUBJECT

Replace the following:

PROJECT_NUMBER: the project
number

POOL_ID: the workload
pool ID

SUBJECT: the individual
subject mapped from your IdP—for example,
administrator@example.com

 By group

principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/group/GROUP

Replace the following:

PROJECT_NUMBER: the project
number

WORKLOAD_POOL_ID: the workload
pool ID

GROUP: the group
mapped from your IdP—for example:
administrator-group@example.com

 By attribute

principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.ATTRIBUTE_NAME/ATTRIBUTE_VALUE

Replace the following:

PROJECT_NUMBER: the project
number

WORKLOAD_POOL_ID: the workload
pool ID

ATTRIBUTE_NAME: one of the
attributes that was mapped from your IdP

ATTRIBUTE_VALUE: the value
of the attribute

By pool

principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/*

Replace the following:

PROJECT_NUMBER: the project
number

WORKLOAD_POOL_ID: the workload
pool ID

In Select a role, select the Workload Identity User
role (roles/iam.workloadIdentityUser).

To save the configuration, click Save.

gcloud

    To grant the Workload Identity User role (roles/iam.workloadIdentityUser)
    to a federated principal or principal set, run the following
    command. To learn more about Workload Identity Federation principal
    identifiers, see Principal types.

  By subject

gcloud iam service-accounts add-iam-policy-binding SERVICE_ACCOUNT_EMAIL \
    --role=roles/iam.workloadIdentityUser \
    --member="principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/subject/SUBJECT"

  By group

gcloud iam service-accounts add-iam-policy-binding SERVICE_ACCOUNT_EMAIL \
    --role=roles/iam.workloadIdentityUser \
    --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/group/GROUP"

  By attribute

gcloud iam service-accounts add-iam-policy-binding SERVICE_ACCOUNT_EMAIL \
    --role=roles/iam.workloadIdentityUser \
    --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.ATTRIBUTE_NAME/ATTRIBUTE_VALUE"

Replace the following:

SERVICE_ACCOUNT_EMAIL:
the email address of the service account

PROJECT_NUMBER: the project number.
of the project that contains the workload identity pool

POOL_ID: the pool ID of the workload identity pool

SUBJECT: the expected value for the attribute that
you've mapped
to google.subject

GROUP: the expected value for the attribute that
you've mapped
to google.groups

ATTRIBUTE_NAME: the name of a custom attribute in
your attribute mapping

ATTRIBUTE_VALUE: the value of the custom attribute in your attribute mapping

Note: You must use the project number, not the project ID, in the
member identifier.

Download or create a credential configuration

The Cloud Client Libraries, the
gcloud CLI, and Terraform, can automatically obtain external
credentials, and use these credentials to impersonate a service account. To
let libraries and tools complete this process, you have to provide a credential
configuration file. This file defines the following:

Where to obtain external credentials from

Which workload identity pool and provider to use

Which service account to impersonate

Note: Unlike a service account key,
a credential configuration file doesn't contain a private key and doesn't need
to be kept confidential. Details about the credential configuration file are
available at https://google.aip.dev/auth/4117.
To create a credential configuration file, do the following:

 Console
To download a credential configuration file in the Google Cloud console,
do the following:

In the Google Cloud console, go to the Workload Identity Pools
page.

Go to Workload Identity Pools

Find the workload identity pool for the IdP that you want
to use and click it.

If you chose to use direct resource access, do the following:

Click Grant access.

Select Grant access using federated identities (Recommended).

Click Download.

Continue with instructions to Configure your application dialog,
later in this procedure.

If you chose to use service account impersonation, do the following:

Select Connected service accounts.

Find the service account you want to use and click
file_download Download.

Continue with instructions to Configure your application dialog,
later in this procedure.

In the Configure your application dialog, select the provider that
contains the external identities.

Provide the following additional settings:

 AWS
No additional settings required.

 Azure
Application ID URL: Application ID URI of the Azure application

Select file_download Download config
to download the credential configuration file, then click Dismiss.

If you want to use the Security Token Service regional endpoints—for example,
https://sts.us-central1.rep.googleapis.com, refer to
Using regional Security Token Service endpoints for better reliability.

 gcloud
To create a credential configuration file by using
gcloud iam workload-identity-pools create-cred-config,
do the following:

 AWS
To create a credential configuration file that lets the library obtain
an access token from EC2 instance metadata, do the following:

gcloud iam workload-identity-pools create-cred-config \
    projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID \
    --service-account=SERVICE_ACCOUNT_EMAIL \
    --service-account-token-lifetime-seconds=SERVICE_ACCOUNT_TOKEN_LIFETIME \
    --aws \
    --sts-location=REGION \
    --output-file=FILEPATH.json

Replace the following:

PROJECT_NUMBER: The project number of the
  project that contains the workload identity pool

POOL_ID: The ID of the workload identity
  pool.

PROVIDER_ID: The ID of the workload
  identity pool provider.

SERVICE_ACCOUNT_EMAIL: If you use service
  account impersonation, replace with the email address
  of the service account. Omit this flag if you don't use
  service account impersonation.

SERVICE_ACCOUNT_TOKEN_LIFETIME: If you use
  service account impersonation, replace with the lifetime
  of the service account access token, in seconds; this defaults to
  one hour when not provided. Omit this flag if you don't use
  service account impersonation. To specify a lifetime longer than
  one hour, you must configure the
  constraints/iam.allowServiceAccountCredentialLifetimeExtension
  organizational policy constraint.

FILEPATH: The file to save configuration
  to.

REGION: Optional. Specify the region of the
  regional Security Token Service endpoints,
  if they are available.

If you use
AWS IMDSv2,
an additional flag --enable-imdsv2 needs to be added to the
gcloud iam workload-identity-pools create-cred-config
command:

gcloud iam workload-identity-pools create-cred-config \
    projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID \
    --service-account=SERVICE_ACCOUNT_EMAIL \
    --aws \
    --enable-imdsv2 \
    --sts-location=REGION \
    --output-file=FILEPATH.json

If using the AWS metadata server isn't an option, you can provide AWS
security credentials through the following AWS environment variables:

AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY

Either of AWS_REGION or AWS_DEFAULT_REGION

Optional: AWS_SESSION_TOKEN

The gcloud CLI and libraries use these AWS environment
variables when the AWS metadata server is unavailable.

 Azure
Create a credential configuration file that lets the library obtain
an access token from the Azure Instance Metadata Service (IMDS):

gcloud iam workload-identity-pools create-cred-config \
    projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID \
    --service-account=SERVICE_ACCOUNT_EMAIL \
    --service-account-token-lifetime-seconds=SERVICE_ACCOUNT_TOKEN_LIFETIME \
    --azure \
    --app-id-uri APPLICATION_ID_URI \
    --sts-location=REGION \
    --output-file=FILEPATH.json

Replace the following:

PROJECT_NUMBER: The project number of the
  project that contains the workload identity pool.

POOL_ID: The ID of the workload identity
  pool.

PROVIDER_ID: The ID of the workload
  identity pool provider.

SERVICE_ACCOUNT_EMAIL: If you use service
  account impersonation, replace with the email address
  of the service account. Omit this flag if you don't use
  service account impersonation.

APPLICATION_ID_URI: The Application ID
  URI of the Azure application.

SERVICE_ACCOUNT_TOKEN_LIFETIME: If you use
  service account impersonation,lifetime of the service account
  access token, in seconds; this defaults to one hour when not
  provided. Omit this flag if you don't use service account
  impersonation. To specify a lifetime longer than one hour, you
  must configure the
  constraints/iam.allowServiceAccountCredentialLifetimeExtension
  organizational policy constraint.

FILEPATH: The file to save configuration
  to.

REGION: Optional. Specify the region of the
  regional Security Token Service endpoints,
  if they are available.

Use the credential configuration to access Google Cloud

To let tools and client libraries use your credential configuration, do the
following in your AWS or Azure environment:

Initialize an environment variable GOOGLE_APPLICATION_CREDENTIALS and point
it to the credential configuration file:

Bash

  export GOOGLE_APPLICATION_CREDENTIALS=`pwd`/FILEPATH.json

  where FILEPATH is the relative path to the
  credential configuration file.

PowerShell

  $env:GOOGLE_APPLICATION_CREDENTIALS = Resolve-Path 'FILEPATH.json'

  where FILEPATH is the relative path to the
  credential configuration file.

Use a client library or tool that supports Workload Identity Federation
and can find credentials automatically:

 C++
The
Google Cloud Client Libraries for C++
support Workload Identity Federation since version
v2.6.0.
To use Workload Identity Federation, you must build the client libraries
with version 1.36.0 or later of gRPC.

 Go
Client libraries for Go support Workload Identity Federation if they use version
v0.0.0-20210218202405-ba52d332ba99 or later of the golang.org/x/oauth2 module.

To check which version of this module your client library uses, run the
following commands:

cd $GOPATH/src/cloud.google.com/go
go list -m golang.org/x/oauth2

 Java
Client libraries for Java support Workload Identity Federation if they use version 0.24.0
or later of the
com.google.auth:google-auth-library-oauth2-http artifact.

To check which version of this artifact your client library uses, run the
following Maven command in your application directory:

mvn dependency:list -DincludeArtifactIds=google-auth-library-oauth2-http

 Node.js
Client libraries for Node.js support Workload Identity Federation if they use version
7.0.2 or later of the
google-auth-library package.

To check which version of this package your client library uses, run the
following command in your application directory:

npm list google-auth-library

When you create a GoogleAuth object, you can specify a project ID, or you can
allow GoogleAuth to find the project ID automatically. To find the project ID
automatically, the service account in the configuration file must have the
Browser role (roles/browser), or a role with equivalent permissions, on your
project. For details, see the
README for the google-auth-library package.

 Python
Client libraries for Python support Workload Identity Federation if they use version
1.27.0 or later of the
google-auth package.

To check which version of this package your client library uses, run the
following command in the environment where the package is installed:

pip show google-auth

To specify a project ID for the authentication client, you can set the
GOOGLE_CLOUD_PROJECT environment variable, or you can allow the client to find
the project ID automatically. To find the project ID automatically, the service
account in the configuration file must have the Browser role (roles/browser),
or a role with equivalent permissions, on your project. For details, see the
user guide for the google-auth package.

 gcloud
To authenticate using Workload Identity Federation, use the
gcloud auth login command:

gcloud auth login --cred-file=FILEPATH.json

Replace FILEPATH with the path to the
credential configuration file.

Support for Workload Identity Federation in gcloud CLI is available in
version 363.0.0 and later versions of the gcloud CLI.

 Terraform
The Google Cloud provider
supports Workload Identity Federation if you use version 3.61.0 or later:

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 3.61.0"
    }
  }
}

 bq

To authenticate using Workload Identity Federation, use the
gcloud auth login command, as follows:

gcloud auth login --cred-file=FILEPATH.json

Replace FILEPATH with the path to the
credential configuration file.

Support for Workload Identity Federation in bq is available in
version 390.0.0 and later versions of the gcloud CLI.

If you can't use a client library that supports
Workload Identity Federation, you can authenticate programmatically by
using the REST API.

Advanced scenarios

Authenticate a workload using the REST API

If you can't use the client libraries, you can follow these steps to let
an external workload obtain a short-lived access token by using the REST API:

Obtain credentials from your external IdP:

 AWS
Create a JSON document that contains the information that you would normally
include in a request to the AWS GetCallerIdentity()
endpoint, including a valid request signature.

Workload Identity Federation refers to this JSON document as a
GetCallerIdentity token. The token lets Workload Identity Federation
verify the identity without revealing the AWS secret access key.

A GetCallerIdentity token looks similar to the following:

{
  "url": "https://sts.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15",
  "method": "POST",
  "headers": [
    {
      "key": "Authorization",
      "value" : "AWS4-HMAC-SHA256 Credential=AKIASOZTBDV4D7ABCDEDF/20200228/us-east-1/sts/aws4_request, SignedHeaders=host;x-amz-date,Signature=abcedefdfedfd"
    },
    {
      "key": "host",
      "value": "sts.amazonaws.com"
    },
    {
      "key": "x-amz-date",
      "value": "20200228T225005Z"
    },
    {
      "key": "x-goog-cloud-target-resource",
      "value": "//iam.googleapis.com/projects/12345678/locations/global/workloadIdentityPools/my-pool/providers/my-aws-provider"
    },
    {
      "key": "x-amz-security-token",
      "value": "GizFWJTqYX...xJ55YoJ8E9HNU="
    }
  ]
}

The token contains the following fields:

url: The URL of the AWS STS endpoint for GetCallerIdentity(),
with the body of a standard GetCallerIdentity() request appended
as query parameters. For example,
https://sts.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15.
We recommend that you use regional STS endpoints and design a reliable infrastructure for your workloads.
For more information, see Regional AWS STS endpoints.

method: The HTTP request method: POST.

headers: The HTTP request headers, which must include:

Authorization: The request signature.

host: The hostname of the url field; for example,
sts.amazonaws.com.

x-amz-date: The time you will send the request, formatted as an
ISO 8601 Basic
string. This value is typically set to the current time and is
used to help prevent replay attacks.

x-goog-cloud-target-resource: The full resource name of the
IdP without a https: prefix. For example:

//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID

x-amz-security-token: Session token. Only required if you are
using temporary security credentials.

The following example creates a URL-encoded GetCallerIdentity token.
Extract the URL-encoded token for later use. It also creates a
human-readable token just for your reference:

import json
import urllib

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

def create_token_aws(project_number: str, pool_id: str, provider_id: str) -> None:
    # Prepare a GetCallerIdentity request.
    request = AWSRequest(
        method="POST",
        url="https://sts.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15",
        headers={
            "Host": "sts.amazonaws.com",
            "x-goog-cloud-target-resource": f"//iam.googleapis.com/projects/{project_number}/locations/global/workloadIdentityPools/{pool_id}/providers/{provider_id}",
        },
    )

    # Set the session credentials and Sign the request.
    # get_credentials loads the required credentials as environment variables.
    # Refer:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    SigV4Auth(boto3.Session().get_credentials(), "sts", "us-east-1").add_auth(request)

    # Create token from signed request.
    token = {"url": request.url, "method": request.method, "headers": []}
    for key, value in request.headers.items():
        token["headers"].append({"key": key, "value": value})

    # The token lets workload identity federation verify the identity without revealing the AWS secret access key.
    print("Token:\n%s" % json.dumps(token, indent=2, sort_keys=True))
    print("URL encoded token:\n%s" % urllib.parse.quote(json.dumps(token)))

def main() -> None:
    # TODO(Developer): Replace the below credentials.
    # project_number: Google Project number (not the project id)
    project_number = "my-project-number"
    pool_id = "my-pool-id"
    provider_id = "my-provider-id"

    create_token_aws(project_number, pool_id, provider_id)

if __name__ == "__main__":
    main()

Initialize the following variables:

Bash

SUBJECT_TOKEN_TYPE="urn:ietf:params:aws:token-type:aws4_request"
SUBJECT_TOKEN=TOKEN

PowerShell

$SubjectTokenType = "urn:ietf:params:aws:token-type:aws4_request"
$SubjectToken = "TOKEN"

Where TOKEN is the URL encoded
GetCallerIdentity token that was generated by the script.

 Azure
Connect to an Azure VM that has an assigned managed identity
and obtain an access token
from the Azure Instance Metadata Service (IMDS):

Bash

SUBJECT_TOKEN_TYPE="urn:ietf:params:oauth:token-type:jwt"
SUBJECT_TOKEN=$(curl \
  "http://169.254.169.254/metadata/identity/oauth2/token?resource=APP_ID_URI&api-version=2018-02-01" \
  -H "Metadata: true" | jq -r .access_token)
echo $SUBJECT_TOKEN

This command uses the jq tool.
jq is available by default in Cloud Shell.

PowerShell

$SubjectTokenType = "urn:ietf:params:oauth:token-type:jwt"
$SubjectToken = (Invoke-RestMethod `
  -Uri "http://169.254.169.254/metadata/identity/oauth2/token?resource=APP_ID_URI&api-version=2018-02-01" `
  -Headers @{Metadata="true"}).access_token
Write-Host $SubjectToken

Where APP_ID_URI is the Application ID URI
of the application that you've
configured for Workload Identity Federation.

Use the Security Token Service API to exchange the credential against
a short-lived access token:

Bash

STS_TOKEN=$(curl https://sts.googleapis.com/v1/token \
    --data-urlencode "audience=//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID" \
    --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
    --data-urlencode "requested_token_type=urn:ietf:params:oauth:token-type:access_token" \
    --data-urlencode "scope=https://www.googleapis.com/auth/cloud-platform" \
    --data-urlencode "subject_token_type=$SUBJECT_TOKEN_TYPE" \
    --data-urlencode "subject_token=$SUBJECT_TOKEN" | jq -r .access_token)
echo $STS_TOKEN

PowerShell

[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
$StsToken = (Invoke-RestMethod `
    -Method POST `
    -Uri "https://sts.googleapis.com/v1/token" `
    -ContentType "application/json" `
    -Body (@{
        "audience"           = "//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID"
        "grantType"          = "urn:ietf:params:oauth:grant-type:token-exchange"
        "requestedTokenType" = "urn:ietf:params:oauth:token-type:access_token"
        "scope"              = "https://www.googleapis.com/auth/cloud-platform"
        "subjectTokenType"   = $SubjectTokenType
        "subjectToken"       = $SubjectToken
    } | ConvertTo-Json)).access_token
Write-Host $StsToken

Replace the following values:

PROJECT_NUMBER: Project number of the project
that contains the workload identity pool

POOL_ID: ID of the workload identity pool

PROVIDER_ID: ID of the workload identity pool provider

To use regional Security Token Service endpoints, replace https://sts.googleapis.com/v1/token with the following:

 https://sts.REGION.rep.googleapis.com/v1/token

Replace REGION with a
Google Cloud location,
for example, us-central1 or europe-west4.

Note: The audience must not include a https: scheme.

If you use service account impersonation, use the token from the
Security Token Service to invoke the generateAccessToken method
of the IAM Service Account Credentials API
to obtain an access token.

Tokens for Cloud Run services

When accessing a Cloud Run service, you must use an ID token.

Bash

TOKEN=$(curl -0 -X POST https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/SERVICE_ACCOUNT_EMAIL:generateIdToken \
    -H "Content-Type: text/json; charset=utf-8" \
    -H "Authorization: Bearer $STS_TOKEN" \
    -d @- <<EOF | jq -r .token
    {
        "audience": "SERVICE_URL"
    }
EOF
)
echo $TOKEN

PowerShell

$Token = (Invoke-RestMethod `
    -Method POST `
    -Uri "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/SERVICE_ACCOUNT_EMAIL:generateIdToken" `
    -Headers @{ "Authorization" = "Bearer $StsToken" } `
    -ContentType "application/json" `
    -Body (@{
        "audience" = "SERVICE_URL"
    } | ConvertTo-Json)).token
Write-Host $Token

  Replace the following:

      SERVICE_ACCOUNT_EMAIL: the email address
      of the service account.

      SERVICE_URL: the URL of the service—for example, https://my-service-12345-us-central1.run.app. You can also set it to your custom service endpoint. For more information, see
      Understanding custom audiences.

Tokens for other platforms

When accessing another service, you must use an access token.

Bash

TOKEN=$(curl -0 -X POST https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/SERVICE_ACCOUNT_EMAIL:generateAccessToken \
    -H "Content-Type: text/json; charset=utf-8" \
    -H "Authorization: Bearer $STS_TOKEN" \
    -d @- <<EOF | jq -r .accessToken
    {
        "scope": [ "https://www.googleapis.com/auth/cloud-platform" ]
    }
EOF
)
echo $TOKEN

PowerShell

$Token = (Invoke-RestMethod `
    -Method POST `
    -Uri "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/SERVICE_ACCOUNT_EMAIL:generateAccessToken" `
    -Headers @{ "Authorization" = "Bearer $StsToken" } `
    -ContentType "application/json" `
    -Body (@{
        "scope" = , "https://www.googleapis.com/auth/cloud-platform"
    } | ConvertTo-Json)).accessToken
Write-Host $Token

  Replace the following:

      SERVICE_ACCOUNT_EMAIL: the email address
      of the service account.

What's next

Read more about Workload Identity Federation.

Learn about best practices for using Workload Identity Federation.

See how you can manage workload identity pools and providers.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-08-28 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-08-28 UTC."],[],[]]
