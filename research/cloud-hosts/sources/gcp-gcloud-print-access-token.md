Home

          Documentation

          Developer tools

          Google Cloud SDK

          Reference

    Send feedback

      gcloud auth print-access-token

      Stay organized with collections

      Save and categorize content based on your preferences.

NAME

gcloud auth print-access-token - print an access token for the specified account

SYNOPSIS

gcloud auth print-access-token [ACCOUNT] [--lifetime=LIFETIME] [GCLOUD_WIDE_FLAG …]

DESCRIPTION

Print an access token for the specified account. See RFC6749 for more information
about access tokens.

Note that token itself may not be enough to access some services. If you use the
token with curl or similar tools, you may see permission errors similar to "API
has not been used in project 32555940559 before or it is disabled.". If it
happens, you may need to provide a quota project in the "X-Goog-User-Project"
header. For example,

curl -H "X-Goog-User-Project: your-project" -H "Authorization: Bearer $(gcloud auth print-access-token)" foo.googleapis.com

The identity that granted the token must have the serviceusage.services.use
permission on the provided project. See https://cloud.google.com/apis/docs/system-parameters
for more information.

EXAMPLES

To print access tokens:

gcloud auth print-access-token

POSITIONAL ARGUMENTS

[ACCOUNT]

Account to get the access token for. If not specified, the current active
account will be used.

FLAGS

--lifetime=LIFETIME

Access token lifetime. The default access token lifetime is 3600 seconds, but
you can use this flag to reduce the lifetime or extend it up to 43200 seconds
(12 hours). The org policy constraint
constraints/iam.allowServiceAccountCredentialLifetimeExtension must
be set if you want to extend the lifetime beyond 3600 seconds. Note that this
flag is for service account impersonation only, so it must be used together with
the --impersonate-service-account flag.

GCLOUD WIDE FLAGS

These flags are available to all commands: --access-token-file,
--account, --billing-project,
--configuration,
--flags-file,
--flatten, --format, --help, --impersonate-service-account,
--log-http,
--project, --quiet, --trace-token, --user-output-enabled,
--verbosity.

Run $ gcloud help for details.

NOTES

These variants are also available:

gcloud alpha auth print-access-token

gcloud beta auth print-access-token

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-05-27 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-05-27 UTC."],[],[]]
