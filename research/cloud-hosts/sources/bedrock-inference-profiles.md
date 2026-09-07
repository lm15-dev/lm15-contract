# Supported Regions and models for inference profiles

For a list of Region codes and endpoints supported in Amazon Bedrock, see [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html#bedrock_region). This topic describes predefined inference profiles that you can use and the Regions and models that support application inference profiles.

**Note**
Looking for inference profile IDs for a specific model? Each model's inference profile IDs and Regional availability are now documented on the model's detail page. Visit [models at a glance](model-cards.md) and choose the model you are interested in.

**Topics**
+ [Supported cross-Region inference profiles](#inference-profiles-support-system)
+ [Supported Regions and models for application inference profiles](#inference-profiles-support-user)

## Supported cross-Region inference profiles

You can carry out [cross-Region inference](cross-region-inference.md) with cross-Region (system-defined) inference profiles. With cross-Region inference, you can distribute traffic across multiple AWS Regions by using compute in each of those Regions.

Cross-Region (system-defined) inference profiles are named after the model that they support and defined by the Regions that they support. To understand how a cross-Region inference profile handles your requests, review the following definitions:
+ **Source Region** – The Region from which you make the API request that specifies the inference profile.
+ **Destination Region** – A Region to which the Amazon Bedrock service can route the request from your source Region.

When you invoke a cross-Region inference profile in Amazon Bedrock, your request originates from a source Region and is automatically routed to one of the destination Regions defined in that profile, optimizing for performance. The destination Regions for Global cross-Region inference profiles include all commercial Regions.

**Note**
The destination Regions in a cross-Region inference profile can include *opt-in Regions*, which are Regions that you must explicitly enable at AWS account or Organization level. To learn more, see [Enable or disable AWS Regions in your account](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-regions.html). When using a cross-Region inference profile, your inference request can be routed to any of the destination Regions in the profile, even if you did not opt-in to such Regions in your account. Your input prompts and output results may be stored in the opt-in Regions for abuse detection purposes.

Service Control Policies (SCPs) and AWS Identity and Access Management (IAM) policies work together to control where cross-Region inference is allowed. Using SCPs, you can control which Regions Amazon Bedrock can use for inference, and using IAM policies, you can define which users or roles have permission to run inference. If any destination Region in a cross-Region inference profile is blocked in your SCPs, the request will fail even if other Regions remain allowed. To ensure efficient operation with cross-Region inference, you can update your SCPs and IAM policies to allow all required Amazon Bedrock inference actions (for example, `bedrock:InvokeModel*` or `bedrock:CreateModelInvocationJob`) in all destination Regions included in your chosen inference profile. To learn more, see [Enabling Amazon Bedrock cross-Region inference in multi-account environments.](https://aws.amazon.com/blogs/machine-learning/enable-amazon-bedrock-cross-region-inference-in-multi-account-environments/)

**Note**
Some inference profiles route to different destination Regions depending on the source Region from which you call it. For example, if you call `us.anthropic.claude-3-haiku-20240307-v1:0` from US East (Ohio), it can route requests to `us-east-1`, `us-east-2`, or `us-west-2`, but if you call it from US West (Oregon), it can route requests to only `us-east-1` and `us-west-2`.

To check the source and destination Regions for an inference profile, you can do one of the following:
+ Expand the corresponding section in the [list of supported cross-Region inference profiles](#inference-profiles-support).
+ Send a [GetInferenceProfile](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_GetInferenceProfile.html) request with an [Amazon Bedrock control plane endpoint](https://docs.aws.amazon.com/general/latest/gr/bedrock.html#br-cp) from a source Region and specify the Amazon Resource Name (ARN) or ID of the inference profile in the `inferenceProfileIdentifier` field. The `models` field in the response maps to a list of model ARNs, in which you can identify each destination Region.

**Note**
Global cross-Region inference profile for a specific model can change over time as AWS adds more commercial Regions where your requests can be processed. However, if an inference profile is tied to a geography (such as US, EU, or APAC), its destination Region list will never change. AWS might create new inference profiles that incorporate new Regions. You can update your systems to use these inference profiles by changing the IDs in your setup to the new ones.
The Global cross-Region inference profile is currently only supported on Anthropic Claude Sonnet 4 model for the following source Regions: US West (Oregon), US East (N. Virginia), US East (Ohio), Europe (Ireland), and Asia Pacific (Tokyo). The destination Regions for Global inference profile include all commercial AWS Regions.

**Important**
Each model's cross-Region inference profile IDs, supported source Regions, destination Regions, and Geo scope (Global, US, or EU) are documented on the model's detail page. To find this information, visit [models at a glance](model-cards.md) and choose the model you are interested in. On the model page, look for the *Regional availability* table — it shows which Regions support In-Region, Geo, and Global inference profiles, and the *Inference profile IDs* section lists the exact IDs to use in API calls.
If you need to compare data residency options across multiple models for compliance planning, review the Regional availability table on each model's page to confirm that your chosen model's inference profile routes requests only to Regions that meet your requirements.

## Supported Regions and models for application inference profiles

Application inference profiles can be created for supported models in the following AWS Regions:
+ af-south-1
+ ap-east-2
+ ap-northeast-1
+ ap-northeast-2
+ ap-northeast-3
+ ap-south-1
+ ap-south-2
+ ap-southeast-1
+ ap-southeast-2
+ ap-southeast-3
+ ap-southeast-4
+ ap-southeast-5
+ ap-southeast-6
+ ap-southeast-7
+ ca-central-1
+ ca-west-1
+ eu-central-1
+ eu-central-2
+ eu-north-1
+ eu-south-1
+ eu-south-2
+ eu-west-1
+ eu-west-2
+ eu-west-3
+ il-central-1
+ me-central-1
+ me-south-1
+ mx-central-1
+ sa-east-1
+ us-east-1
+ us-east-2
+ us-gov-east-1
+ us-gov-west-1
+ us-west-1
+ us-west-2

Application inference profiles can be created from most models supported in Amazon Bedrock. Some models, such as embedding models, do not support inference profiles. To check if a specific model supports inference profiles, see [models at a glance](model-cards.md).
