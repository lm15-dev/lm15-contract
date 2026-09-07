Home

          Documentation

          AI and ML

          Gemini Enterprise Agent Platform

          Models

    Send feedback

      Using OpenAI libraries with Gemini Enterprise Agent Platform

      Stay organized with collections

      Save and categorize content based on your preferences.

To see an example of using the Chat Completions API,
      run the "Call Gemini with the OpenAI Library" notebook in one of the following
      environments:

Open in Colab

         |

Open in Colab Enterprise

         |

Open
in Agent Platform Workbench

         |

View on GitHub

The Chat Completions API works as an Open AI-compatible endpoint, designed to
make it easier to interface with Gemini on Gemini Enterprise Agent Platform by
using the OpenAI libraries for Python and REST. If you're already using the
OpenAI libraries, you can use this API as a low-cost way to switch between
calling OpenAI models and Agent Platform hosted models to compare
output, cost, and scalability, without changing your existing code.
If you aren't already using the OpenAI libraries, we recommend that you
use the Google Gen AI SDK.
To migrate your existing OpenAI SDK code to use the Google Gen AI SDK, see
Migrate from OpenAI SDK to Google Gen AI SDK.

Supported models

The Chat Completions API supports both Gemini models and select
self-deployed models from Model Garden.

Gemini models

The following models provide support for the Chat Completions API:

  Click to expand supported models

            Gemini 3.8 Flash

            Gemini 3.7 Flash

            Gemini 3.6 Flash

            Gemini 3.5 Flash-Lite

            Gemini 3.5 Flash

            Gemini 3.1 Pro

            preview

            Gemini 3.1 Flash-Lite

            Gemini 3 Flash

            preview

            Gemini 2.5 Pro

            Gemini 2.5 Flash

Self-deployed models from Model Garden

The
Hugging Face Text Generation Interface (HF TGI)
and
Agent Platform Model Garden prebuilt vLLM
containers support the Chat Completions API. However,
not every model deployed to these containers supports the Chat Completions API.
The following table includes the most popular supported models by container:

        HF TGI

        vLLM

          gemma-2-9b-it

          gemma-2-27b-it

          Meta-Llama-3.1-8B-Instruct

          Meta-Llama-3-8B-Instruct

          Mistral-7B-Instruct-v0.3

          Mistral-Nemo-Instruct-2407

          Gemma

          Llama 2

          Llama 3

          Mistral-7B

          Mistral Nemo

Supported parameters

For Google models, the Chat Completions API supports the following OpenAI
parameters. For a description of each parameter, see OpenAI's documentation on
Creating chat completions.
Parameter support for third-party models varies by model. To see which parameters
are supported, consult the model's documentation.

    messages

        System message

        User message: The text and
          image_url types are supported. The
            image_url type supports images stored in a
            Cloud Storage URI or a base64 encoding in the form
            "data:<MIME-TYPE>;base64,<BASE64-ENCODED-BYTES>". To
            learn how to create a Cloud Storage bucket and upload a file to it,
            see
            Discover object storage.

        Assistant message

        Tool message

        Function message: This field is deprecated, but supported for backwards compatibility.

    model

    detail
    For models older than Gemini 3, the detail field must be consistent across all messages
    and contents (it is request-level). For Gemini 3 and onwards, this corresponds to a part-level
    `media_resolution`. For more information, see
    Media Resolution.

    max_completion_tokens
    Alias for max_tokens.

    modalities
    Supports audio, image, and text.

    max_tokens

    n

    frequency_penalty

    presence_penalty

    reasoning_effort

      Configures how much time and how many tokens are used on a response.

        low: 1024

        medium: 8192

        high: 24576

      As no thoughts are included in the response, only one of
      reasoning_effort or extra_body.google.thinking_config
      may be specified.

    response_format

        json_object: Interpreted as passing "application/json" to the
            Gemini API.

        json_schema.

        Fully recursive schemas are not supported. additional_properties
        is supported.

        text: Interpreted as passing "text/plain" to the Gemini
            API.

        Any other MIME type is passed as is to the model, such as passing
            "application/json" directly.

    seed
    Corresponds to GenerationConfig.seed.

    stop

    stream

    temperature

    top_p

    tools

        type

        function

              name

              description

              parameters: Specify parameters by using the
                OpenAPI specification.
                This differs from the OpenAI parameters field, which is
                described as a JSON Schema object. To learn about keyword
                differences between OpenAPI and JSON Schema, see the
                OpenAPI guide.

    tool_choice

        none

        auto

        required: Corresponds to the mode ANY in the
            FunctionCallingConfig.

        validated: Corresponds to the mode VALIDATED
            in the FunctionCallingConfig. This is Google-specific.

    web_search_options
    Corresponds to the GoogleSearch tool. No sub-options are
    supported.

    function_call
    This field is deprecated, but supported for backwards
    compatibility.

    functions
    This field is deprecated, but supported for backwards
    compatibility.

If you pass any unsupported parameter, it is ignored.

Multimodal input parameters

The Chat Completions API supports select multimodal inputs.

    input_audio

      data: Any URI or valid blob format. We support all blob types,
      including image, audio, and video. Anything supported by
      GenerateContent is supported (HTTP, Cloud Storage, etc.).

      format: OpenAI supports both wav (audio/wav)
      and mp3 (audio/mp3). Using Gemini, all valid MIME
      types are supported.

    image_url

      data: Like input_audio, any URI or valid blob
      format is supported.

      Note that image_url as a URL will default to the image/* MIME-type
      and image_url as blob data can be used as any multimodal input.

      detail: Similar to
      media resolution,
      this determines the maximum tokens per image for the request. Note that while
      OpenAI's field is per-image, Gemini enforces the same detail across
      the request, and passing multiple detail types in one request will throw
      an error.

In general, the data parameter can be a URI or a combination of MIME type and
base64 encoded bytes in the form "data:<MIME-TYPE>;base64,<BASE64-ENCODED-BYTES>".
For a full list of MIME types, see GenerateContent.
For more information on OpenAI's base64 encoding, see their documentation.

For usage, see our multimodal input examples.

Gemini-specific parameters

There are several features supported by Gemini that are not available in OpenAI models.
These features can still be passed in as parameters, but must be contained within an
extra_content or extra_body or they will be ignored.

extra_body features

Include a google field to contain any Gemini-specific
extra_body features.

{
  ...,
  "extra_body": {
     "google": {
       ...,
       // Add extra_body features here.
     }
   }
}

    safety_settings
    This corresponds to the Gemini
      SafetySetting.

    cached_content
    This corresponds to the Gemini
    generateContent.cached_content field.

    thinking_config
    This corresponds to the Gemini
      GenerationConfig.ThinkingConfig.

    thought_tag_marker
    Used to separate a model's thoughts from its responses for models with Thinking available.

    If not specified, no tags will be returned around the model's thoughts. If present, subsequent queries
    will strip the thought tags and mark the thoughts appropriately for context. This helps
    preserve the appropriate context for subsequent queries.

    stream_function_call_arguments
    Streams function call arguments back as segments of JSON. For more information, see

    Streaming function call arguments.

    tools
    Specify tools similar to `GenerateContent`. For more information, see
    Tool.

    media_resolution
    Specify a request-level media resolution similar to `GenerateContent`. For more information, see

    MediaResolution.

extra_content features

extra_content lets you specify Gemini-specific content that shouldn't be ignored.

Include a google field to contain any Gemini-specific
extra_content features.

{
  ...,
  "extra_content": {
     "google": {
       ...,
       // Add extra_content features here.
     }
   }
}

    thought
    This field explicitly marks if a field is a thought and takes precedence
    over thought_tag_marker. It helps distinguish between different
    steps in a thought process, especially in tool use scenarios where intermediate
    steps might be mistaken for final answers. By tagging specific parts of the
    input as thoughts, you can guide the model to treat them as internal
    reasoning rather than user-facing responses.

    thought_signature
    A bytes field that provides a thought signature to validate against
    thoughts returned by the model. This field is distinct from
    thought, which is a boolean field. For more information, see
    Thought signatures.

    parts
    Specific to a Tool message to pass multi-modal function response parts back to the model.
    For more information, see

    FunctionResponsePart and
    Multimodal function response.

What's next

Learn more about
authentication and credentialing
with the OpenAI-compatible syntax.

See examples of calling the
Chat Completions API
with the OpenAI-compatible syntax.

See examples of calling the
Inference API
with the OpenAI-compatible syntax.

See examples of calling the
Function Calling API
with OpenAI-compatible syntax.

Learn more about the Gemini API.

Learn more about migrating to the latest Gemini models.

To migrate your existing OpenAI SDK code to use the Google Gen AI SDK, see
Migrate from OpenAI SDK to Google Gen AI SDK.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-09-03 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-09-03 UTC."],[],[]]
