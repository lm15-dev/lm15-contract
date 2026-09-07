Home

          Documentation

          AI and ML

          Gemini Enterprise Agent Platform

    Send feedback

      Generate content with the Gemini API

      Stay organized with collections

      Save and categorize content based on your preferences.

Use generateContent or streamGenerateContent to generate content with
Gemini.

The Gemini model family includes models that work with multimodal
prompt requests. The term multimodal indicates that you can use more than one
modality, or type of input, in a prompt. Models that aren't multimodal accept
prompts only with text. Modalities can include text, audio, video, and more.

Get started

To get started generating content with Gemini, do the following:

Create a Google Cloud
account.

Review this document to learn about the Gemini model
request body, parameters, and
response body. To see some sample requests,
see Examples.

To learn how to send a request to the Gemini API by using
a programming language SDK or the REST API, see the Gemini API
quickstart.

Supported models

All Gemini models support content generation.

Note: Adding a lot of images to a request increases response latency.
Parameter list

See examples for implementation details.

Request body

{
  "cachedContent": string,
  "contents": [
    {
      "role": string,
      "parts": [
        {
          // Union field data can be only one of the following:
          "text": string,
          "inlineData": {
            "mimeType": string,
            "data": string
          },
          "fileData": {
            "mimeType": string,
            "fileUri": string
          },
          // End of list of possible types for union field data.

          "thought": boolean,
          "thoughtSignature": string,
          "videoMetadata": {
            "startOffset": {
              "seconds": integer,
              "nanos": integer
            },
            "endOffset": {
              "seconds": integer,
              "nanos": integer
            },
            "fps": double
          },
          "mediaProcessing": string,
          "mediaResolution": MediaResolution
        }
      ]
    }
  ],
  "systemInstruction": {
    "role": string,
    "parts": [
      {
        "text": string
      }
    ]
  },
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": string,
          "description": string,
          "parameters": {
            object (OpenAPI Object Schema)
          }
        }
      ]
    }
  ],
  "safetySettings": [
    {
      "category": enum (HarmCategory),
      "threshold": enum (HarmBlockThreshold)
    }
  ],
  "generationConfig": {
    "temperature": number,
    "topP": number,
    "topK": number,
    "candidateCount": integer,
    "maxOutputTokens": integer,
    "presencePenalty": float,
    "frequencyPenalty": float,
    "stopSequences": [
      string
    ],
    "responseMimeType": string,
    "responseSchema": schema,
    "seed": integer,
    "responseLogprobs": boolean,
    "logprobs": integer,
    "audioTimestamp": boolean,
    "thinkingConfig": {
      "thinkingBudget": integer,
      "thinkingLevel": enum
    },
    "mediaProcessing": string,
    "mediaResolution": MediaResolution
  },
  "labels": {
    string: string
  }
}

The request body contains data with the following parameters:

    Parameters

    cachedContent
	 Optional:
    string
The name of the cached content used as context to
    serve the prediction. Format:
    projects/{project}/locations/{location}/cachedContents/{cachedContent}

    contents

    Required: Content

    The content of the current conversation with the model.
For single-turn queries, this is a single instance. For multi-turn queries, this is a repeated field that contains conversation history and the latest request.

    systemInstruction

    Optional: Content
Instructions for the model to steer it toward better performance. For example, "Answer as concisely as possible" or "Don't use technical terms in your response".
The text strings count toward the token limit.
The role field of systemInstruction is ignored and doesn't affect the performance of the model.
Note: Only text should be used in parts and content in each part should be in a separate paragraph.

    tools

    Optional. A piece of code that enables the system to interact with
      external systems to perform an action, or set of actions, outside of
      knowledge and scope of the model. See
      Function calling.

    toolConfig

    Optional. See Function calling.

    safetySettings

    Optional: SafetySetting
Per request settings for blocking unsafe content.
Enforced on GenerateContentResponse.candidates.

    generationConfig

    Optional: GenerationConfig
Generation configuration settings.

    labels

    Optional: string
Metadata that you can add to the API call in the format of key-value pairs.

contents

The base structured data type containing multi-part content of a message.

This class consists of two main properties: role and parts. The role
property denotes the individual producing the content, while the parts
property contains multiple elements, each representing a segment of data within
a message.

    Parameters

    role

    string
The identity of the entity that
      creates the message. The following values are supported:

      user: This indicates that the message is sent by a real person, typically a user-generated message.

      model: This indicates that the message is generated by the model.

    The model value is used to insert messages from the model into the conversation during multi-turn conversations.

    parts

    Part
A list of ordered parts that make up
      a single message. Different parts may have different
      IANA MIME types.

      For limits on the inputs, such as the maximum number of tokens or
      the number of images, see the model specifications on the
      Google models
      page.

      To compute the number of tokens in your request, see
      Get token count.

parts

A data type containing media that is part of a multi-part Content message.

    Parameters

    text

    Optional: string
A text prompt or code snippet.

    inlineData

    Optional: Blob
Inline data in raw bytes.

    fileData

    Optional: fileData
Data stored in a file.

    functionCall

      Optional: FunctionCall.
It contains a string
        representing the FunctionDeclaration.name field and
        a structured JSON object containing any parameters for the
        function call predicted by the model.

      See Function calling.

    functionResponse

      Optional: FunctionResponse.
The result output of
        a FunctionCall that contains a string representing
        the FunctionDeclaration.name field and a structured JSON
        object containing any output from the function call. It is used as
        context to the model.

     See Function calling.

    thought

    Optional: boolean
Indicates whether the part represents the model's thought process or reasoning.

    thoughtSignature

    Optional: string (bytes format)
An opaque signature for the thought so it can be reused in subsequent requests. A base64-encoded string.

    videoMetadata

      Optional: VideoMetadata

        For video input, the start and end offset of the video in Duration
        format, and the frame rate of the video . For example, to specify a 10
        second clip starting at 1:00 with a frame rate of 10 frames per second,
        set the following:

          "startOffset": { "seconds": 60 }

          "endOffset": { "seconds": 70 }

          "fps": 10.0

        The metadata should only be specified while the video data is presented
        in inlineData or fileData.

    mediaProcessing

      Optional: string

       How the model processes this media part. When set to
       AGENTIC, uses model-driven dynamic video navigation. When
       set to STATIC, uses fixed-rate frame extraction.

        Only supported for 3.5 and higher versioned Gemini models. If
        set for a request using an unsupported model, falls back to
        STATIC.

       Supported values: AGENTIC, STATIC.

    mediaResolution

      Optional: MediaResolution

       Per-part media resolution for the input media. Controls how input media is processed. If specified, this overrides the mediaResolution setting in generationConfig.
       LOW reduces tokens per image/video, possibly losing detail
       but allowing longer videos in context. Supported values: HIGH, MEDIUM, LOW.

blob

Content blob. If possible send as text rather than raw bytes.

    Parameters

    mimeType

      string

The media type of the file specified in the data or fileUri
fields. Acceptable values include the following:

  Click to expand MIME types

    application/pdf

    audio/mpeg

    audio/mp3

    audio/wav

    image/png

    image/jpeg

    image/webp

    text/plain

    video/mov

    video/mpeg

    video/mp4

    video/mpg

    video/avi

    video/wmv

    video/mpegps

    video/flv

        For more information, see Gemini
        audio and
        video requirements.

        Text files must be UTF-8 encoded. The contents of the text file count
        toward the token limit.

      There is no limit on image resolution.

    data

      bytes

The base64 encoding of the image, PDF, or video
to include inline in the prompt. When including media inline, you must also specify the media
type (mimeType) of the data.

      Size limit: 7 MB for images

FileData

URI or web-URL data.

    Parameters

    mimeType

    string
IANA MIME type of the data.

    fileUri

    string

The URI or URL of the file to include in the prompt. Acceptable values include the following:

  Cloud Storage bucket URI: The object must either be publicly readable or reside in
    the same Google Cloud project that's sending the request.

  HTTP URL: The file URL must be publicly readable. You can specify one video file, one
    audio file, and up to 10 image files per request. Audio files, video files, and documents can't
    exceed 15 MB.

  YouTube video URL:The YouTube video must be either owned by the account that you used
    to sign in to the Google Cloud console or be public. Only one YouTube video URL is supported per
    request.

When specifying a fileURI, you must also specify the media type
  (mimeType) of the file. If VPC Service Controls is enabled, specifying a media file
  URL for fileURI is not supported.

functionCall

A predicted functionCall returned from the model that contains a string
representing the functionDeclaration.name and a structured JSON object
containing the parameters and their values.

    Parameters

    name

    string
The name of the function to call.

    args

      Struct
The function parameters and values in
        JSON object format.

      See Function calling
        for parameter details.

functionResponse

The resulting output from a FunctionCall that contains a string representing the
FunctionDeclaration.name. Also contains a structured JSON object with the
output from the function (and uses it as context for the model). This should contain the
result of a FunctionCall made based on model prediction.

    Parameters

    name

    string
The name of the function to call.

    response

    Struct
The function response in JSON object format.

videoMetadata

Metadata describing the input video content.

    Parameters

    startOffset

      Optional: google.protobuf.Duration

      The start offset of the video.

    endOffset

      Optional: google.protobuf.Duration

      The end offset of the video.

    fps

      Optional: double

        The frame rate of the video sent to the model. Defaults to
        1.0 if not specified. The minimum accepted value is as low
        as, but not including, 0.0. The maximum value is
        24.0.

safetySetting

Safety settings.

    Parameters

    category

    Optional: HarmCategory

The safety category to configure a threshold for. Acceptable values include the following:

  Click to expand safety categories

    HARM_CATEGORY_SEXUALLY_EXPLICIT

    HARM_CATEGORY_HATE_SPEECH

    HARM_CATEGORY_HARASSMENT

    HARM_CATEGORY_DANGEROUS_CONTENT

    threshold

    Optional: HarmBlockThreshold
The threshold for blocking responses that could belong to the specified safety category based on probability.

        OFF

        BLOCK_NONE

        BLOCK_LOW_AND_ABOVE

        BLOCK_MEDIUM_AND_ABOVE

        BLOCK_ONLY_HIGH

    method

    Optional: HarmBlockMethod
Specify if the threshold is used for probability or severity score. If not specified, the threshold is used for probability score.

harmCategory

Harm categories that block content.

    Parameters

    HARM_CATEGORY_UNSPECIFIED

    The harm category is unspecified.

    HARM_CATEGORY_HATE_SPEECH

    The harm category is hate speech.

    HARM_CATEGORY_DANGEROUS_CONTENT

    The harm category is dangerous content.

    HARM_CATEGORY_HARASSMENT

    The harm category is harassment.

    HARM_CATEGORY_SEXUALLY_EXPLICIT

    The harm category is sexually explicit content.

harmBlockThreshold

Probability thresholds levels used to block a response.

    Parameters

    HARM_BLOCK_THRESHOLD_UNSPECIFIED

    Unspecified harm block threshold.

    BLOCK_LOW_AND_ABOVE

    Block low threshold and higher (i.e. block more).

    BLOCK_MEDIUM_AND_ABOVE

    Block medium threshold and higher.

    BLOCK_ONLY_HIGH

    Block only high threshold (i.e. block less).

    BLOCK_NONE

    Block none.

    OFF

    Switches off safety if all categories are turned OFF

harmBlockMethod

A probability threshold that blocks a response based on a combination of
probability and severity.

    Parameters

    HARM_BLOCK_METHOD_UNSPECIFIED

    The harm block method is unspecified.

    SEVERITY

    The harm block method uses both probability and severity scores.

    PROBABILITY

    The harm block method uses the probability score.

generationConfig

Configuration settings used when generating the prompt.

    Parameters

    temperature

      Optional: float

      The range of values and default value is specific for each model.
        See the temperature ranges and
        default values list.

The temperature is used for sampling during response generation, which occurs when topP
and topK are applied. Temperature controls the degree of randomness in token selection.
Lower temperatures are good for prompts that require a less open-ended or creative response, while
higher temperatures can lead to more diverse or creative results. A temperature of 0
means that the highest probability tokens are always selected. In this case, responses for a given
prompt are mostly deterministic, but a small amount of variation is still possible.

If the model returns a response that's too generic, too short, or the model gives a fallback
response, try increasing the temperature. If the model enters infinite generation, increasing the
temperature to at least 0.1 may lead to improved results.
 1.0 is the
recommended starting value for temperature.

        Range for Gemini 3 models versions 3.5 Flash and lower: 0.0 - 2.0 (default: 1.0)

        Warning: Sampling parameters (temperature, topP, and topK) are deprecated for all Gemini 3 models. It is recommended to omit these parameters and let the model manage sampling automatically.

      For more information, see
        Content generation parameters.

    topP

    Optional: float
If specified, nucleus sampling is used.

    Top-P changes how the model selects tokens for output. Tokens are selected from the most (see top-K) to least probable until the sum of their probabilities equals the top-P value. For example, if tokens A, B, and C have a probability of 0.3, 0.2, and 0.1 and the top-P value is 0.5, then the model will select either A or B as the next token by using temperature and excludes C as a candidate.
Specify a lower value for less random responses and a higher value for more random responses.

  Range: 0.0 - 1.0

    topK

    Optional: float
Specifies the top-k sampling
      threshold. The model considers only the top k most probable tokens for
      the next token. This can be useful for generating more coherent and
      less random text. For example, a `topK` of 40 means the model will choose
      the next word from the 40 most likely words.

    candidateCount

    Optional: int

The number of response variations to return. For each request, you're charged for the
output tokens of all candidates, but are only charged once for the input tokens.

Specifying multiple candidates is a Preview feature that works with generateContent
(streamGenerateContent is not supported).

    maxOutputTokens

    Optional: int

Maximum number of tokens that can be generated in the response. A token is
approximately four characters. 100 tokens correspond to roughly 60-80 words.

Specify a lower value for shorter responses and a higher value for potentially longer
responses.

    For more information, see
    Content generation parameters.

    stopSequences

    Optional: List[string]

Specifies a list of strings that tells the model to stop generating text if one
of the strings is encountered in the response. If a string appears multiple
times in the response, then the response is truncated where it's first encountered.
The strings are case-sensitive.

For example, if the following is the returned response when stopSequences isn't specified:
 public
static string reverse(string myString)

Then the returned response with stopSequences set to ["Str",
  "reverse"] is:

public static string

Maximum 5 items in the list.

    For more information, see
    Content generation parameters.

    presencePenalty

    Optional: float
Positive penalties.
Positive values penalize tokens that already appear in the generated text, increasing the probability of generating more diverse content.
The maximum value for presencePenalty is up to, but not including, 2.0. Its minimum value is -2.0.

    frequencyPenalty

    Optional: float
Positive values penalize tokens that repeatedly appear in the generated text, decreasing the probability of repeating content.
This maximum value for frequencyPenalty is up to, but not including, 2.0. Its minimum value is -2.0.

    responseMimeType

    Optional: string (enum)

    The output response MIME type of
    the generated candidate text.
The following MIME types are
    supported:

    application/json: JSON response in the candidates.

    text/plain (default): Plain text output.

    text/x.enum: For classification tasks, output an enum value
    as defined in the response schema.

    Specify the appropriate response type to avoid unintended behaviors. For
    example, if you require a JSON-formatted response, specify
    application/json and not text/plain.

    text/plain isn't supported for use with
    responseSchema.

        Caution: Setting responseMimeType to
        application/json (JSON mode) without specifying a
        responseSchema acts only
        as a strong hint to the model and doesn't ensure 100% valid JSON.
        Because JSON mode lacks strict schema enforcement, type checking, and
        relationship constraints, complex payloads can occasionally result in
        trailing characters or malformed outputs.

        To ensure 100% valid JSON objects, requests must include both
        a responseSchema and responseMimeType:
        "application/json". As a best practice, if your use case prevents
        you from pre-defining a schema, implement a client-side JSON validator
        with a retry mechanism.

    responseSchema

    Optional: schema

      The schema that generated candidate text must follow. For more
      information, see Control
      generated output.

      To use this parameter, you must specify a supported MIME type other
      than text/plain for the responseMimeType
      parameter.

      To ensure 100% valid JSON objects, requests must include both a
      responseSchema and responseMimeType set to
      application/json.

    seed

    Optional: int

When seed is fixed to a specific value, the model makes a best effort to provide
the same response for repeated requests. Deterministic output isn't guaranteed.
Also, changing the model or parameter settings, such as the temperature, can
cause variations in the response even when you use the same seed value. By
default, a random seed value is used.

    responseLogprobs

    Optional: boolean

      If true, returns the log probabilities of the tokens that were chosen
      by the model at each step. By default, this parameter is set to
      false.

        Warning: The responseLogprobs parameter is deprecated for Gemini 3.x models and will soon be completely deprecated.

    logprobs

    Optional: int

Returns the log probabilities of the top candidate tokens at each generation step. The model's
chosen token might not be the same as the top candidate token at each step. Specify the number of
candidates to return by using an integer value in the range of 1-20.

      You must enable
        responseLogprobs to use
         this parameter.

        Warning: The logprobs parameter is deprecated for Gemini 3.x models and will soon be completely deprecated.

    audioTimestamp

    Optional: boolean

    Enables timestamp understanding for audio-only files.

    This is a preview feature.

      thinkingConfig

      Optional: object

      Configuration for the model's thinking process for Gemini 2.5 and higher models.

      The thinkingConfig object contains the following fields:

        thinkingBudget: integer. By default, the model automatically controls how much it thinks up to a maximum of 8,192 tokens.

        thinkingLevel: enum. Controls the amount of internal reasoning the model performs before generating a response. Higher levels may improve quality on complex tasks but increase latency and cost. Supported values are MINIMAL, LOW, MEDIUM, and HIGH (support varies by model).

      mediaResolution

      Optional: MediaResolution

      Controls how input media is processed. LOW reduces tokens per image/video, possibly losing detail but allowing longer videos in context. Supported values: HIGH, MEDIUM, LOW.

Response body

{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": string
          }
        ]
      },
      "finishReason": enum (FinishReason),
      "safetyRatings": [
        {
          "category": enum (HarmCategory),
          "probability": enum (HarmProbability),
          "blocked": boolean
        }
      ],
      "citationMetadata": {
        "citations": [
          {
            "startIndex": integer,
            "endIndex": integer,
            "uri": string,
            "title": string,
            "license": string,
            "publicationDate": {
              "year": integer,
              "month": integer,
              "day": integer
            }
          }
        ]
      },
      "avgLogprobs": double,
      "logprobsResult": {
        "topCandidates": [
          {
            "candidates": [
              {
                "token": string,
                "logProbability": float
              }
            ]
          }
        ],
        "chosenCandidates": [
          {
            "token": string,
            "logProbability": float
          }
        ]
      }
    }
  ],
  "usageMetadata": {
    "promptTokenCount": integer,
    "candidatesTokenCount": integer,
    "totalTokenCount": integer
  },
  "modelVersion": string
}

    Response element
    Description

    modelVersion
    The model and version used for generation. For example:
      gemini-3.5-flash.

    text
    The generated text.

    finishReason

      The reason why the model stopped generating tokens. If empty, the model
      has not stopped generating the tokens. Because the response uses the
      prompt for context, it's not possible to change the behavior of how the
      model stops generating tokens.

        FINISH_REASON_STOP:    Natural stop point of the model or provided stop sequence.

        FINISH_REASON_MAX_TOKENS:  The maximum number of tokens as specified in the request was reached.

        FINISH_REASON_SAFETY:  Token generation was stopped because the response was flagged for safety reasons. Note that Candidate.content is empty if content filters block the output.

        FINISH_REASON_RECITATION:  The token generation was stopped because the response was flagged for unauthorized citations.

        FINISH_REASON_BLOCKLIST: Token generation was stopped because the response includes blocked terms.

        FINISH_REASON_PROHIBITED_CONTENT: Token generation was stopped because the response was flagged for prohibited content, such as child sexual abuse material (CSAM).

        FINISH_REASON_IMAGE_PROHIBITED_CONTENT: Token generation was stopped because the image provided in the prompt was flagged for prohibited content.

        FINISH_REASON_NO_IMAGE: Token generation was stopped because an image was expected in the prompt, but none was provided.

        FINISH_REASON_SPII: Token generation was stopped because the response was flagged for sensitive personally identifiable information (SPII).

        FINISH_REASON_MALFORMED_FUNCTION_CALL: Candidates were blocked because of malformed and unparsable function call.

        FINISH_REASON_OTHER:   All other reasons that stopped the token

        FINISH_REASON_UNSPECIFIED: The finish reason is unspecified.

    category

The safety category to configure a threshold for. Acceptable values include the following:

  Click to expand safety categories

    HARM_CATEGORY_SEXUALLY_EXPLICIT

    HARM_CATEGORY_HATE_SPEECH

    HARM_CATEGORY_HARASSMENT

    HARM_CATEGORY_DANGEROUS_CONTENT

    probability

      The harm probability levels in the content.

        HARM_PROBABILITY_UNSPECIFIED

        NEGLIGIBLE

        LOW

        MEDIUM

        HIGH

    blocked

      A boolean flag associated with a safety attribute that indicates if the
      model's input or output was blocked.

    startIndex

An integer that specifies where a citation starts in the content. The
startIndex is in bytes and calculated from the response encoded in UTF-8.

    endIndex

An integer that specifies where a citation ends in the content. The
endIndex is in bytes and calculated from the response encoded in UTF-8.

    url

The URL of a citation source. Examples of a URL source might be a news website or
a GitHub repository.

    title

The title of a citation source. Examples of source titles might be that of a
news article or a book.

    license

The license associated with a citation.

    publicationDate

The date a citation was published. Its valid formats are
YYYY, YYYY-MM, and YYYY-MM-DD.

    avgLogprobs
    Average log probability of the candidate.

    logprobsResult
    Returns the top candidate tokens (topCandidates) and the
     actual chosen tokens (chosenCandidates) at each step.

    token
    Generative AI models break down text data into tokens for processing,
    which can be characters, words, or phrases.

    logProbability
    A log probability value that indicates the model's confidence for a
    particular token.

    promptTokenCount
    Number of tokens in the request.

    candidatesTokenCount
    Number of tokens in the response(s).

    totalTokenCount
    Number of tokens in the request and response(s).

Note: For billing purposes, tokens consumed by document inputs to
Gemini 3 and later models are counted as image tokens.
Examples

The following examples show how to generate content using Gemini models.

Text Generation

Generate a text response from a text input.

 Google Gen AI SDK for Python

from google import genai
from google.genai.types import HttpOptions

client = genai.Client(http_options=HttpOptions(api_version="v1"))
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="How does AI work?",
)
print(response.text)
# Example response:
# Okay, let's break down how AI works. It's a broad field, so I'll focus on the ...
#
# Here's a simplified overview:
# ...

 Python (OpenAI)
You can call the Inference API by using the OpenAI library. For more information, see

Call Agent Platform models by using the OpenAI library.

from google.auth import default
import google.auth.transport.requests

import openai

# TODO(developer): Update and un-comment below lines
# project_id = "PROJECT_ID"
# location = "us-central1"

# Programmatically get an access token
credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
credentials.refresh(google.auth.transport.requests.Request())

# OpenAI Client
client = openai.OpenAI(
    base_url=f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/endpoints/openapi",
    api_key=credentials.token,
)

response = client.chat.completions.create(
    model="google/gemini-2.0-flash-001",
    messages=[{"role": "user", "content": "Why is the sky blue?"}],
)

print(response)

 Go

import (
	"context"
	"fmt"
	"io"

	"google.golang.org/genai"
)

// generateWithText shows how to generate text using a text prompt.
func generateWithText(w io.Writer) error {
	ctx := context.Background()

	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		HTTPOptions: genai.HTTPOptions{APIVersion: "v1"},
	})
	if err != nil {
		return fmt.Errorf("failed to create genai client: %w", err)
	}

	resp, err := client.Models.GenerateContent(ctx,
		"gemini-2.5-flash",
		genai.Text("How does AI work?"),
		nil,
	)
	if err != nil {
		return fmt.Errorf("failed to generate content: %w", err)
	}

	respText := resp.Text()

	fmt.Fprintln(w, respText)
	// Example response:
	// That's a great question! Understanding how AI works can feel like ...
	// ...
	// **1. The Foundation: Data and Algorithms**
	// ...

	return nil
}

Using multimodal prompt

Generate a text response from a multimodal input, such as text and an image.

 Google Gen AI SDK for Python

from google import genai
from google.genai.types import HttpOptions, Part

client = genai.Client(http_options=HttpOptions(api_version="v1"))
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=[
        "What is shown in this image?",
        Part.from_uri(
            file_uri="gs://cloud-samples-data/generative-ai/image/scones.jpg",
            mime_type="image/jpeg",
        ),
    ],
)
print(response.text)
# Example response:
# The image shows a flat lay of blueberry scones arranged on parchment paper. There are ...

 Python (OpenAI)
You can call the Inference API by using the OpenAI library. For more information, see

Call Agent Platform models by using the OpenAI library.

from google.auth import default
import google.auth.transport.requests

import openai

# TODO(developer): Update and un-comment below lines
# project_id = "PROJECT_ID"
# location = "us-central1"

# Programmatically get an access token
credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
credentials.refresh(google.auth.transport.requests.Request())

# OpenAI Client
client = openai.OpenAI(
    base_url=f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/endpoints/openapi",
    api_key=credentials.token,
)

response = client.chat.completions.create(
    model="google/gemini-2.0-flash-001",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe the following image:"},
                {
                    "type": "image_url",
                    "image_url": "gs://cloud-samples-data/generative-ai/image/scones.jpg",
                },
            ],
        }
    ],
)

print(response)

 Go

import (
	"context"
	"fmt"
	"io"

	genai "google.golang.org/genai"
)

// generateWithTextImage shows how to generate text using both text and image input
func generateWithTextImage(w io.Writer) error {
	ctx := context.Background()

	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		HTTPOptions: genai.HTTPOptions{APIVersion: "v1"},
	})
	if err != nil {
		return fmt.Errorf("failed to create genai client: %w", err)
	}

	modelName := "gemini-2.5-flash"
	contents := []*genai.Content{
		{Parts: []*genai.Part{
			{Text: "What is shown in this image?"},
			{FileData: &genai.FileData{
				// Image source: https://storage.googleapis.com/cloud-samples-data/generative-ai/image/scones.jpg
				FileURI:  "gs://cloud-samples-data/generative-ai/image/scones.jpg",
				MIMEType: "image/jpeg",
			}},
		},
			Role: genai.RoleUser},
	}

	resp, err := client.Models.GenerateContent(ctx, modelName, contents, nil)
	if err != nil {
		return fmt.Errorf("failed to generate content: %w", err)
	}

	respText := resp.Text()

	fmt.Fprintln(w, respText)

	// Example response:
	// The image shows an overhead shot of a rustic, artistic arrangement on a surface that ...

	return nil
}

Streaming text response

Generate a streaming model response from a text input.

 Google Gen AI SDK for Python

from google import genai
from google.genai.types import HttpOptions

client = genai.Client(http_options=HttpOptions(api_version="v1"))

for chunk in client.models.generate_content_stream(
    model="gemini-3.5-flash",
    contents="Why is the sky blue?",
):
    print(chunk.text, end="")
# Example response:
# The
#  sky appears blue due to a phenomenon called **Rayleigh scattering**. Here's
#  a breakdown of why:
# ...

 Python (OpenAI)
You can call the Inference API by using the OpenAI library. For more information, see

Call Agent Platform models by using the OpenAI library.

from google.auth import default
import google.auth.transport.requests

import openai

# TODO(developer): Update and un-comment below lines
# project_id = "PROJECT_ID"
# location = "us-central1"

# Programmatically get an access token
credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
credentials.refresh(google.auth.transport.requests.Request())

# OpenAI Client
client = openai.OpenAI(
    base_url=f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/endpoints/openapi",
    api_key=credentials.token,
)

response = client.chat.completions.create(
    model="google/gemini-2.0-flash-001",
    messages=[{"role": "user", "content": "Why is the sky blue?"}],
    stream=True,
)
for chunk in response:
    print(chunk)

 Go

import (
	"context"
	"fmt"
	"io"

	genai "google.golang.org/genai"
)

// generateWithTextStream shows how to generate text stream using a text prompt.
func generateWithTextStream(w io.Writer) error {
	ctx := context.Background()

	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		HTTPOptions: genai.HTTPOptions{APIVersion: "v1"},
	})
	if err != nil {
		return fmt.Errorf("failed to create genai client: %w", err)
	}

	modelName := "gemini-2.5-flash"
	contents := genai.Text("Why is the sky blue?")

	for resp, err := range client.Models.GenerateContentStream(ctx, modelName, contents, nil) {
		if err != nil {
			return fmt.Errorf("failed to generate content: %w", err)
		}

		chunk := resp.Text()

		fmt.Fprintln(w, chunk)
	}

	// Example response:
	// The
	//  sky is blue
	//  because of a phenomenon called **Rayleigh scattering**. Here's the breakdown:
	// ...

	return nil
}

What's next

Learn more about function
calling.

Learn more about
grounding.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-09-02 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-09-02 UTC."],[],[]]
