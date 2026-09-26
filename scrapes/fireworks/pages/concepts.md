> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Concepts

> This document outlines basic Fireworks AI concepts.

This page outlines core Fireworks resources and ideas. For definitions of technical terms (inference, LoRA, token, and many others), see the [**Glossary**](/getting-started/glossary).

## Resources

### Account

Your account is the top-level resource under which other resources are located. Quotas and billing are enforced at the account level, so usage for all users in an account contribute to the same quotas and bill.

* For developer accounts, the account ID is auto-generated from the email address used to sign up.
* Enterprise accounts can optionally choose a custom, unique account ID.

### User

A user is an email address associated with an account. Each user is assigned a role (such as Admin, User, Contributor, or Inference User) that determines their level of access to resources within the account.

### Models and model types

A model is a set of model weights and metadata associated with the model. Each model has a [**globally unique name**](/getting-started/concepts#resource-names-and-ids) of the form `accounts/<ACCOUNT_ID>/models/<MODEL_ID>`. There are two types of models:

**Base models:** A base model consists of the full set of model weights, including models pre-trained from scratch and full-parameter fine-tunes.

* Fireworks has a library of common base models that can be used for [**serverless inference**](/models/overview#serverless-inference) as well as [**dedicated deployments**](/models/overview#dedicated-deployments). Model IDs for these models are pre-populated. For example, `llama-v3p1-70b-instruct` is the model ID for the Llama 3.1 70B model that Fireworks provides. The ID for each model can be found on its page ([**example**](https://app.fireworks.ai/models/fireworks/qwen3-coder-480b-a35b-instruct))
* Users can also [upload their own](/models/uploading-custom-models) custom base models and specify model IDs.

**LoRA (low-rank adaptation) addons:** A LoRA addon is a small, trained model that significantly reduces the amount of memory required to deploy compared to a fully trained model. Fireworks supports [**training**](/fine-tuning/finetuning-intro), [**uploading**](/models/uploading-custom-models#importing-trained-models), and [**serving**](/fine-tuning/fine-tuning-models#deploying-a-trained-model) LoRA addons. LoRA addons must be deployed on a dedicated deployment for its corresponding base model. Model IDs for LoRAs can be either auto-generated or user-specified.

#### A Note on API Model Metadata

When retrieving model details via the API, a model may be listed with both `supportsServerless: true` and `supportsLora: true`. This indicates that the base model is available for serverless inference, AND that the model architecture supports training with LoRA.

However, these two features are mutually exclusive in deployment. The `supportsServerless` flag applies **only** to the base model. A LoRA addon trained from that base model **cannot** be deployed serverlessly and requires a dedicated (on-demand) deployment.

### Deployments and deployment types

A model must be deployed before it can be used for inference. A deployment is a collection (one or more) model servers that host one base model and optionally one or more LoRA addons.

Fireworks supports two types of deployments:

* **Serverless deployments:** Fireworks hosts popular base models on shared "serverless" deployments. Users pay-per-token to query these models and do not need to configure GPUs. See our [Quickstart - Serverless](/getting-started/quickstart) guide to get started.
* **Dedicated deployments:** Dedicated deployments enable users to configure private deployments with a wide array of hardware (see [on-demand deployments guide](/guides/ondemand-deployments)). Dedicated deployments give users performance guarantees and the most flexibility and control over what models can be deployed. Both LoRA addons and base models can be deployed to dedicated deployments. Dedicated deployments are billed by a GPU-second basis (see [**pricing**](https://fireworks.ai/pricing#ondemand) page).

See the [**Querying text models guide**](/guides/querying-text-models) for a comprehensive overview of making LLM inference.

### Deployed model

Users can specify a model to query for inference using the model name and deployment name. Alternatively, users can refer to a "deployed model" name that refers to a unique instance of a base model or LoRA addon that is loaded into a deployment. See [On-demand deployments](/guides/ondemand-deployments) guide for more.

### Dataset

A dataset is an immutable set of training examples that can be used to train a model.

<h3 id="training-job">
  Training job
</h3>

A training job is an offline training job that uses a dataset to train a LoRA addon model.

## Resource names and IDs

A resource name is a globally unique identifier of a resource. The format of a name also identifies the type and hierarchy of the resource, for example:

Resource IDs must satisfy the following constraints:

* Between 1 and 63 characters (inclusive)
* Consists of a-z, 0-9, and hyphen (-)
* Does not begin or end with a hyphen (-)
* Does not begin with a digit

## Control plane and data plane

The Fireworks API can be split into a control plane and a data plane.

* The **control plane** consists of APIs used for managing the lifecycle of resources. This
  includes your account, models, and deployments.
* The **data plane** consists of the APIs used for inference and the backend services that power
  them.

## Interfaces

Users can interact with Fireworks through one of many interfaces:

* The **web app** at [https://app.fireworks.ai](https://app.fireworks.ai)
* The [`firectl`](/tools-sdks/firectl/firectl) CLI
* [OpenAI compatible API](/tools-sdks/openai-compatibility)
* [Anthropic compatible API](/tools-sdks/anthropic-compatibility)
* [Python SDK](/tools-sdks/python-sdk)
