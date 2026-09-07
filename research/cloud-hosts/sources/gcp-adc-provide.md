Home

          Documentation

          Developer tools

          Google Cloud SDK

          Authentication

          Guides

    Send feedback

      Set up Application Default Credentials

      Stay organized with collections

      Save and categorize content based on your preferences.

How you set up Application Default Credentials (ADC) for use by Cloud Client Libraries,
Google API Client Libraries, and the REST and RPC APIs depends on the environment
where your code is running.

For information about where ADC looks for credentials and in what order, see
How Application Default Credentials works.

If you are using API keys, then you don't need to set up ADC. For more
information, see Use API keys to access APIs.

Provide credentials to ADC

Select the environment where your code is running:

Local development environment

Resource with an attached service account

Containerized environment

On-premises or another cloud provider

Cloud-based development environment

The gcloud CLI and ADC

You can provide credentials to ADC by using the
gcloud auth application-default login command. This makes
credentials available to the Cloud Client Libraries and Google API Client Libraries.

The gcloud CLI itself doesn't use ADC to access Google Cloud
resources. To learn how to provide credentials to the gcloud CLI, see
Authentication for the gcloud CLI.

What's next

Learn more about how ADC finds credentials.

Authenticate for using Cloud Client Libraries.

Authenticate for using REST.

Explore authentication methods.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-08-26 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-08-26 UTC."],[],[]]
