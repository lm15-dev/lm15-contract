# Request access to models

Access to all Amazon Bedrock foundation models is enabled by default with the correct AWS Marketplace permissions. To get started, simply select a model from the model catalog in the Amazon Bedrock console and open it in the playground or invoke the model using the [InvokeModel](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html) or [Converse](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) API operations. For information about the different models supported in Amazon Bedrock, see [Amazon Bedrock foundation model information](https://docs.aws.amazon.com/bedrock/latest/userguide/foundation-models-reference.html). For information about model pricing, see [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/).

Access to all Amazon Bedrock foundation models is enabled by default with the correct AWS Marketplace permissions in all commercial AWS Regions. For programmatic access to third-party models, see [Manage model access using SDK and CLI](#model-access-modify).

**Understanding automatic model access**
When you invoke a third-party model for the first time in your account, Amazon Bedrock automatically initiates the subscription process in the background. During this setup period (up to 15 minutes), your API calls may succeed temporarily while the subscription is being finalized. If any prerequisites are missing, the subscription attempt fails and subsequent API calls will return `AccessDeniedException`. After granting the necessary permissions, it may take up to 2 minutes for the subscription to complete. During this time, API calls may continue to return `AccessDeniedException`. Once the subscription is complete, all subsequent invocations will succeed. To avoid this entirely, verify all prerequisites before invoking models in production.
**Prerequisites for successful model access:**
**AWS Marketplace permissions**: Your IAM role must have `aws-marketplace:Subscribe`, `aws-marketplace:Unsubscribe`, and `aws-marketplace:ViewSubscriptions` permissions. See [Grant IAM permissions to request access to Amazon Bedrock foundation models with a product ID](#model-access-permissions) for details.
**Anthropic models**: For Anthropic models, you must complete the First Time Use (FTU) form before invoking the model. This requirement does not apply to Anthropic models accessed through the `bedrock-mantle` endpoint.
**Valid payment method**: Your AWS account must have a valid payment method configured for AWS Marketplace purchases.

**Note**
Anthropic requires first-time customers to submit use case details before invoking a model once per account or once at the organization's management account. This requirement does not apply to Anthropic models accessed through the `bedrock-mantle` endpoint. You can submit use case details by selecting an Anthropic model from the model catalog in the Amazon Bedrock console or calling the `PutUseCaseForModelAccess` API command. Access to the model is granted immediately after use case details are successfully submitted. The form submission at the root account will be inherited by other accounts in the same AWS Organization.
The use case form requires a description of your intended use and a website URL. If you are an individual developer or student without a company website, you can provide a personal portfolio, GitHub profile, or project URL that describes your use case.

**Note**
For 3P models, by invoking/using the model for the first time you are agreeing to the applicable End User License Agreement. For more information, see [AWS Service Terms](https://aws.amazon.com/service-terms/) and [Serverless Third-Party Model License Agreements](https://aws.amazon.com/legal/bedrock/third-party-models/).
Organizations that need to review and agree to EULA before allowing model usage should:
Initially block model access using Service Control Policies (SCP) or IAM policies
Review the EULA terms
Enable model access through SCP/IAM policies only if you agree to the EULA terms

**Topics**
+ [Grant IAM permissions to request access to Amazon Bedrock foundation models with a product ID](#model-access-permissions)
+ [Manage model access using SDK and CLI](#model-access-modify)
+ [Access Amazon Bedrock foundation models in AWS GovCloud (US)](#model-access-govcloud)

## Grant IAM permissions to request access to Amazon Bedrock foundation models with a product ID

You can manage model access permissions by creating custom IAM policies. To modify access to Amazon Bedrock foundation models, you first need to attach an identity-based IAM policy with the following [AWS Marketplace actions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplace.html#awsmarketplace-actions-as-permissions) to the IAM role that allows access to Amazon Bedrock.

When you first invoke an Amazon Bedrock serverless model served from AWS Marketplace in an account, Bedrock attempts to automatically enable the model for your account. For this auto-enablement to work, AWS Marketplace permissions are required.

If you can’t assume AWS Marketplace permission, someone with AWS Marketplace permissions must enable the model for the account as a one-time step (either manually or through auto-enablement). After the model is enabled, you can invoke the model without needing AWS Marketplace permissions. Users don't need AWS Marketplace subscription permissions to invoke models after they've been enabled. These permissions are only required the first time a model is being used in an account.

Access to Amazon Bedrock serverless foundation models with a product ID is controlled by the following IAM actions:

| IAM action | Description | Applies to which models |
| --- | --- | --- |
| aws-marketplace:Subscribe | Allows an IAM entity to subscribe to AWS Marketplace products, including Amazon Bedrock foundation models. | Only Amazon Bedrock serverless models that have a product ID in AWS Marketplace. |
| aws-marketplace:Unsubscribe | Allows an IAM identity to unsubscribe from AWS Marketplace products, including Amazon Bedrock foundation models. | Only Amazon Bedrock serverless models that have a product ID in AWS Marketplace. |
| aws-marketplace:ViewSubscriptions | Allows an IAM identity to return a list of AWS Marketplace products, including Amazon Bedrock foundation models. | Only Amazon Bedrock serverless models that have a product ID in AWS Marketplace. |

**Note**
For the `aws-marketplace:Subscribe` action only, you can use the `aws-marketplace:ProductId` [condition key](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplace.html#awsmarketplace-policy-keys) to restrict subscription to specific models.

**For an IAM identity to request access to models with a product ID**
The identity must have a policy attached that allows `aws-marketplace:Subscribe`.

**Note**
If an identity has already subscribed to a model in one AWS Region, the model becomes available for the identity to request access in all AWS Regions in which the model is available, even if `aws-marketplace:Subscribe` is denied for other Regions.

For information on creating the policy, see [Quickstart](getting-started.md).

For the `aws-marketplace:Subscribe` action only, you can use the `aws-marketplace:ProductId` [condition key](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplace.html#awsmarketplace-policy-keys) to restrict subscription to specific models.

**Note**
Models from the following providers aren't sold through AWS Marketplace and don't have product keys, so you can't scope the `aws-marketplace` actions to them:
Amazon
DeepSeek
Mistral AI
Meta
Qwen
OpenAI
You can, however, prevent the usage of these models by denying Amazon Bedrock actions and specifying these model IDs in the `Resource` field. For an example, see [Prevent an identity from using a model after access has already been granted](#model-access-prevent-usage).

Select a section to see IAM policy examples for a specific use case:

**Topics**
+ [Prevent an identity from requesting access to a model with a product ID](#model-access-prevent-subscription)
+ [Prevent an identity from using a model after access has already been granted](#model-access-prevent-usage)

### Prevent an identity from requesting access to a model with a product ID

To prevent an IAM entity from requesting access to a specific model that has a product ID, attach an IAM policy to the user that denies the `aws-marketplace:Subscribe` action and scope the `Condition` field to the product ID of the model.

For example, you can attach the following policy to an identity to prevent it from subscribing to the Anthropic Claude 3.5 Sonnet model:

------
#### [ JSON ]

****

```
{
    "Version":"2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": [
                "aws-marketplace:Subscribe"
            ],
            "Resource": "*",
            "Condition": {
                "ForAnyValue:StringEquals": {
                    "aws-marketplace:ProductId": [
                        "prod-m5ilt4siql27k"
                    ]
                }
            }
        }
    ]
}
```

------

**Note**
Denying `aws-marketplace:Subscribe` alone will **not** block the first model invocation, because Amazon Bedrock **auto-initiates** the subscription in the background.
To **block model access from the start**, apply **Deny policies on `bedrock:InvokeModel`** at the **Organization (SCP) or Account (IAM) level**.

**Note**
With this policy, the IAM entity will have access to any newly added models by default.
If the identity has already subscribed to the model in at least one Region, this policy doesn't prevent access in other Regions. Instead, you can prevent its usage by seeing the example in [Prevent an identity from using a model after access has already been granted](#model-access-prevent-usage).

### Prevent an identity from using a model after access has already been granted

If an IAM identity has already been granted access to a model, you can prevent usage of the model by denying all Amazon Bedrock actions and scoping the `Resource` field to the ARN of the foundation model.

For example, you can attach the following policy to an identity to prevent it from using the Anthropic Claude 3.5 Sonnet model in all AWS Regions:

------
#### [ JSON ]

****

```
{
    "Version":"2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": [
                "bedrock:*"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
            ]
        }
    ]
}
```

------

## Manage model access using SDK and CLI

Model access can be managed using SDK in addition to invoking the model. Below steps can be used to create/delete model access as well as check if access already exists or not. Note this is applicable only for third-party models.

**Important**
By invoking or using a third-party model, you are implicitly agreeing to the applicable End User License Agreement (EULA). For more information, see [Serverless Third-Party Model License Agreements](https://aws.amazon.com/legal/bedrock/third-party-models/).

Follow these steps to manage model access programmatically:
+ [Prerequisites](#model-access-sdk-prerequisites)
+ [Step 1: List foundation model agreement offers](#model-access-sdk-step1)
+ [Step 2: [Required one-time for Anthropic models only] Put use case for first-time user](#model-access-sdk-step2)
+ [Step 3: Create foundation model agreement](#model-access-sdk-step3)
+ [Step 4: Get foundation model availability](#model-access-sdk-step4)
+ [[Optional] Step 5: Delete foundation model agreement](#model-access-sdk-step5)

### Prerequisites

+ Attach the [AmazonBedrockFullAccess](aws-managed-policy/latest/reference/AmazonBedrockFullAccess.html) policy to the IAM user/role used for the SDK/CLI.
+ Bedrock SDK Setup: [Set up the AWS SDK for Amazon Bedrock](bedrock/latest/userguide/sdk-general-information-section.html)

  Note: Below instructions use python3 for the examples
+ If you are using the AWS CLI, these commands require AWS CLI version 2.27.42 or later. Run `aws --version` to check your version and [update if needed](cli/latest/userguide/getting-started-install.html).
+ Note the modelId of the model for which the access needs to be managed.

### Step 1: List foundation model agreement offers

Use this API to get the agreement offers for a particular model. This will provide the offerToken used to create model access in next steps.

Documentation
+ API: [ListFoundationModelAgreementOffers](bedrock/latest/APIReference/API_ListFoundationModelAgreementOffers.html)
+ CLI Documentation: [list-foundation-model-agreement-offers](cli/latest/reference/bedrock/list-foundation-model-agreement-offers.html)

------
#### [ AWS CLI ]

```
aws bedrock list-foundation-model-agreement-offers --model-id
```

------
#### [ Python ]

```
# Placeholder for modelId
model_id = ""
# Placeholder for offerId
offer_id = ""
try:
    # offerType= "ALL" means both public and private offers, if offerType isn't defined, the default would be "PUBLIC"
    model_agreement_offers_response = bedrock_client.list_foundation_model_agreement_offers(modelId=model_id,offerType="ALL")
    print(model_agreement_offers_response)
except ClientError as e:
    print(f"Failed to list foundation model offers for modelId: {model_id} due to the following error: {e}")
```

------

### Step 2: [Required one-time for Anthropic models only] Put use case for first-time user

Used to put the first-time user use-case form required only for Anthropic models. This is a pre-requisite for gaining access to Anthropic models in the account. This API is only required one time per account or per AWS organization across all commercial regions, with the exception of opt-in regions where this form needs to be filled again. This requirement does not apply to Anthropic models accessed through the `bedrock-mantle` endpoint.

Documentation
+ API: [PutUseCaseForModelAccess](bedrock/latest/APIReference/API_PutUseCaseForModelAccess.html)
+ CLI Documentation: [put-use-case-for-model-access](cli/latest/reference/bedrock/put-use-case-for-model-access.html)

------
#### [ AWS CLI ]

```
aws bedrock put-use-case-for-model-access \
  --form-data
```

------
#### [ Python ]

```
# Placeholder for form data, replace the names
COMPANY_NAME = ""
COMPANY_WEBSITE = ""
INTENDED_USERS = "1" #for external users
INDUSTRY_OPTION = ""
OTHER_INDUSTRY_OPTION = ""
USE_CASES = ""
form_data = {
    "companyName": COMPANY_NAME,
    "companyWebsite": COMPANY_WEBSITE,
    "intendedUsers": INTENDED_USERS,
    "industryOption": INDUSTRY_OPTION,
    "otherIndustryOption": OTHER_INDUSTRY_OPTION,
    "useCases": USE_CASES
}
form_data_json = json.dumps(form_data)
model_access_response = bedrock_client.put_use_case_for_model_access(formData=form_data_json)
```

------

For CLI, the form data is base64 encoded json of the form below.

```
{
    "companyName": COMPANY_NAME,
    "companyWebsite": COMPANY_WEBSITE,
    "intendedUsers": INTENDED_USERS,
    "industryOption": INDUSTRY_OPTION,
    "otherIndustryOption": OTHER_INDUSTRY_OPTION,
    "useCases": USE_CASES
}
```
+ COMPANY\_NAME: String with maximum length of 128
+ COMPANY\_WEBSITE: String with a maximum length of 128
+ INTENDED USERS: Either 0, 1 or 2. 0: Internal, 1: External, 2: Internal\_and\_External
+ INDUSTRY\_OPTION: String with maximum length of 128
+ OTHER\_INDUSTRY\_OPTION: String with maximum length of 128
+ USE\_CASES: String with maximum length of 8192

### Step 3: Create foundation model agreement

Used to create agreement (access) for the foundation model. Use the offer token and modelId from above.

Documentation
+ API: [CreateFoundationModelAgreement](bedrock/latest/APIReference/API_CreateFoundationModelAgreement.html)
+ CLI Documentation: [create-foundation-model-agreement](cli/latest/reference/bedrock/create-foundation-model-agreement.html)

------
#### [ AWS CLI ]

```
aws bedrock create-foundation-model-agreement \
  --model-id  \
  --offer-token
```

------
#### [ Python ]

```
offer_token= ''

for agreement_offer in model_agreement_offers_response['offers']:
    if  agreement_offer['offerId'] == offer_id:

            offer_token = agreement_offer['offerToken']
            print(f"offer token found. Offer token is {offer_token}")
            break

if(not offer_token):
    print(f"Offer token for  modelId: {model_id} is not found")

foundation_model_agreement_reponse = bedrock_client.create_foundation_model_agreement(offerToken= offer_token , modelId= model_id)
```

------

### Step 4: Get foundation model availability

Used to check if the foundation model currently has access or not. Use the modelId from above.

Documentation
+ API: [GetFoundationModelAvailability](bedrock/latest/APIReference/API_GetFoundationModelAvailability.html)
+ CLI Documentation: [get-foundation-model-availability](cli/latest/reference/bedrock/get-foundation-model-availability.html)

------
#### [ AWS CLI ]

```
aws bedrock get-foundation-model-availability \
  --model-id
```

------
#### [ Python ]

```
model_availability_response = bedrock_client.get_foundation_model_availability(modelId=model_id)
```

------

**Expected response**
`agreementAvailability` - `AVAILABLE` if access exists, `NOT_AVAILABLE` is access does not exist.

```
{
  "modelId": "anthropic.claude-sonnet-4-20250514-v1:0",
  "agreementAvailability": {
    "status": "AVAILABLE"
  },
  "authorizationStatus": "AUTHORIZED",
  "entitlementAvailability": "AVAILABLE",
  "regionAvailability": "AVAILABLE"
}
```

### [Optional] Step 5: Delete foundation model agreement

Used to delete foundation model agreement (access). Use the modelId from above.

**Note**
Deleting model access is not enough for blocking access in the future since invoking the model will create the access again. To make sure access is not created again, apply restrictive deny IAM policies for the model.

Documentation
+ API: [DeleteFoundationModelAgreement](bedrock/latest/APIReference/API_DeleteFoundationModelAgreement.html)
+ CLI Documentation: [delete-foundation-model-agreement](cli/latest/reference/bedrock/delete-foundation-model-agreement.html)

------
#### [ AWS CLI ]

```
aws bedrock delete-foundation-model-agreement \
  --model-id
```

------
#### [ Python ]

```
delete_foundation_model_agreement_reponse = bedrock_client.delete_foundation_model_agreement(modelId= model_id)
```

------

## Access Amazon Bedrock foundation models in AWS GovCloud (US)

AWS GovCloud (US) accounts are linked on a one-to-one basis with standard AWS commercial accounts. This linked commercial account is used for billing, service access, support purposes, and access to Amazon Bedrock Model Marketplace. For more information about the relationship between GovCloud and commercial accounts, see [Standard account linking in AWS GovCloud (US)](govcloud-us/latest/UserGuide/getting-started-standard-account-linking.html).

For third-party models, model access needs to be enabled in both the linked AWS commercial account in addition the AWS GovCloud account. For models provided by Amazon Bedrock, model access only needs to be enabled in the GovCloud account. This is a manual process.

### Enabling model access for AWS GovCloud in linked AWS commercial account (only for third-party models)

Model access can be enabled in an AWS commercial account using 2 ways:

1. Invoke the required model for AWS commercial account in `us-east-1` or `us-west-2` region.

1. Programmatically enable access to the model using SDK/CLI for AWS commercial account in `us-east-1` or `us-west-2` region. This can be done by following the steps described in the previous sections.

### Enabling model access for AWS GovCloud account

In AWS GovCloud (US), you use the **Model access** page in the Amazon Bedrock console in the `us-gov-west-1` region to enable foundation models as described below:

1. Make sure you have [permissions to request model access](bedrock/latest/userguide/model-access.html#model-access-permissions) to request access, or modify access, to Amazon Bedrock foundation models. It is recommended to attach the [AmazonBedrockFullAccess](aws-managed-policy/latest/reference/AmazonBedrockFullAccess.html) policy to the user/role being used.

1. Sign into the Amazon Bedrock console in the `us-gov-west-1` region at [https://console.aws.amazon.com/bedrock/](https://console.aws.amazon.com/bedrock/).

1. In the left navigation pane, under **Bedrock configurations**, choose **Model access**.

1. On the **Model access** page, choose **Modify model access**.

1. Select the models that you want the account to have access to and unselect the models that you don't want the account to have access to. You have the following options:

   1. Be sure to review the **End User License Agreement (EULA)** for terms and conditions of using a model before requesting access to it.

   1. Select the check box next to an individual model to check or uncheck it.

   1. Select the top check box to check or uncheck all models.

   1. Select how the models are grouped and then check or uncheck all the models in a group by selecting the check box next to the group. For example, you can choose to **Group by provider** and then select the check box next to **Cohere** to check or uncheck all Cohere models.

1. Choose **Next**.

1. If you add access to Anthropic models, you must describe your use case details. Choose **Submit use case details**, fill out the form, and then select **Submit form**. Notification of access is granted or denied based on your answers when completing the form for the provider.

1. Review the access changes you're making, and then read the **Terms**.

1. If you agree with the terms, choose **Submit**. The changes can take several minutes to be reflected in the console.

1. If your request is successful, the **Access status** changes to **Access granted** or **Available to request**.
