Home

          Documentation

          AI and ML

          Gemini Enterprise Agent Platform

          Models

    Send feedback

      Create a context cache

      Stay organized with collections

      Save and categorize content based on your preferences.

You must create a context cache before you can use it. The context cache you
create contains a large amount of data that you can use in multiple requests to
a Gemini model. The cached content is stored in the region where you make the
request to create the cache.

Cached content can be any of the MIME types supported by Gemini multimodal
models. For example, you can cache a large amount of text, audio, or video. You
can specify more than one file to cache. For more information, see the following
media requirements:

Image requirements

Video requirements

Audio requirements

You specify the content to cache using a blob, text, or a path to a file that's
stored in a Cloud Storage bucket. If the size of the content you're caching
is greater than 10 MB, then you must specify it using the URI of a file that's
stored in a Cloud Storage bucket. For instructions on how to create a
Cloud Storage bucket to host your file, see
Create buckets.

Cached content has a finite lifespan. The default expiration time of a context
cache is 60 minutes after it's created. If you want a different expiration time,
you can specify it using the ttl or the expire_time
property when you create a context cache. You can also update the expiration
time for an unexpired context cache. For information about how to specify
ttl and expire_time, see
Update the expiration time.

After a context cache expires, it's no longer available. If you want to
reference the content in an expired context cache in future prompt requests,
then you need to recreate the context cache.

Location support

Context caching isn't supported in the Sydney, Australia
(australia-southeast1) region.

Context caching supports the
global endpoint.

Encryption key support

Context caching supports Customer-Managed Encryption Keys (CMEKs), allowing you
to control the encryption of your cached data and protect your sensitive
information with encryption keys that you manage and own. This provides an
additional layer of security and compliance.

Refer to
the example for more details.

CMEK isn't supported when using the global endpoint.

Access Transparency support

Context caching supports Access Transparency.

Create context cache example

The following examples show how to create a context cache.

  Python

      Install

pip install --upgrade google-genai

          To learn more, see the

          SDK reference documentation.

Set environment variables to use the Google Gen AI SDK with Vertex AI:

# Replace the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` values
# with appropriate values for your project.
export GOOGLE_CLOUD_PROJECT=GOOGLE_CLOUD_PROJECT
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_ENTERPRISE=True

from google import genai
from google.genai.types import Content, CreateCachedContentConfig, HttpOptions, Part

client = genai.Client(http_options=HttpOptions(api_version="v1"))

system_instruction = """
You are an expert researcher. You always stick to the facts in the sources provided, and never make up new facts.
Now look at these research papers, and answer the following questions.
"""

contents = [
    Content(
        role="user",
        parts=[
            Part.from_uri(
                file_uri="gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf",
                mime_type="application/pdf",
            ),
            Part.from_uri(
                file_uri="gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf",
                mime_type="application/pdf",
            ),
        ],
    )
]

content_cache = client.caches.create(
    model="gemini-3.5-flash",
    config=CreateCachedContentConfig(
        contents=contents,
        system_instruction=system_instruction,
        # (Optional) For enhanced security, the content cache can be encrypted using a Cloud KMS key
        # kms_key_name = "projects/.../locations/.../keyRings/.../cryptoKeys/..."
        display_name="example-cache",
        ttl="86400s",
    ),
)

print(content_cache.name)
print(content_cache.usage_metadata)
# Example response:
#   projects/111111111111/locations/.../cachedContents/1111111111111111111
#   CachedContentUsageMetadata(audio_duration_seconds=None, image_count=167,
#       text_count=153, total_token_count=43130, video_duration_seconds=None)

  Go

      Learn how to install or update the Go.

          To learn more, see the

          SDK reference documentation.

Set environment variables to use the Google Gen AI SDK with Vertex AI:

# Replace the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` values
# with appropriate values for your project.
export GOOGLE_CLOUD_PROJECT=GOOGLE_CLOUD_PROJECT
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_ENTERPRISE=True

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"time"

	genai "google.golang.org/genai"
)

// createContentCache shows how to create a content cache with an expiration parameter.
func createContentCache(w io.Writer) (string, error) {
	ctx := context.Background()

	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		HTTPOptions: genai.HTTPOptions{APIVersion: "v1"},
	})
	if err != nil {
		return "", fmt.Errorf("failed to create genai client: %w", err)
	}

	modelName := "gemini-2.5-flash"

	systemInstruction := "You are an expert researcher. You always stick to the facts " +
		"in the sources provided, and never make up new facts. " +
		"Now look at these research papers, and answer the following questions."

	cacheContents := []*genai.Content{
		{
			Parts: []*genai.Part{
				{FileData: &genai.FileData{
					FileURI:  "gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf",
					MIMEType: "application/pdf",
				}},
				{FileData: &genai.FileData{
					FileURI:  "gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf",
					MIMEType: "application/pdf",
				}},
			},
			Role: genai.RoleUser,
		},
	}
	config := &genai.CreateCachedContentConfig{
		Contents: cacheContents,
		SystemInstruction: &genai.Content{
			Parts: []*genai.Part{
				{Text: systemInstruction},
			},
		},
		DisplayName: "example-cache",
		TTL:         time.Duration(time.Duration.Seconds(86400)),
	}

	res, err := client.Caches.Create(ctx, modelName, config)
	if err != nil {
		return "", fmt.Errorf("failed to create content cache: %w", err)
	}

	cachedContent, err := json.MarshalIndent(res, "", "  ")
	if err != nil {
		return "", fmt.Errorf("failed to marshal cache info: %w", err)
	}

	// See the documentation: https://pkg.go.dev/google.golang.org/genai#CachedContent
	fmt.Fprintln(w, string(cachedContent))

	// Example response:
	// {
	//   "name": "projects/111111111111/locations/us-central1/cachedContents/1111111111111111111",
	//   "displayName": "example-cache",
	//   "model": "projects/111111111111/locations/us-central1/publishers/google/models/gemini-2.5-flash",
	//   "createTime": "2025-02-18T15:05:08.29468Z",
	//   "updateTime": "2025-02-18T15:05:08.29468Z",
	//   "expireTime": "2025-02-19T15:05:08.280828Z",
	//   "usageMetadata": {
	//     "imageCount": 167,
	//     "textCount": 153,
	//     "totalTokenCount": 43125
	//   }
	// }

	return res.Name, nil
}

  Java

      Learn how to install or update the Java.

          To learn more, see the

          SDK reference documentation.

Set environment variables to use the Google Gen AI SDK with Vertex AI:

# Replace the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` values
# with appropriate values for your project.
export GOOGLE_CLOUD_PROJECT=GOOGLE_CLOUD_PROJECT
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_ENTERPRISE=True

import com.google.genai.Client;
import com.google.genai.types.CachedContent;
import com.google.genai.types.Content;
import com.google.genai.types.CreateCachedContentConfig;
import com.google.genai.types.HttpOptions;
import com.google.genai.types.Part;
import java.time.Duration;
import java.util.Optional;

public class ContentCacheCreateWithTextGcsPdf {

  public static void main(String[] args) {
    // TODO(developer): Replace these variables before running the sample.
    String modelId = "gemini-2.5-flash";
    contentCacheCreateWithTextGcsPdf(modelId);
  }

  // Creates a cached content using text and gcs pdfs files
  public static Optional<String> contentCacheCreateWithTextGcsPdf(String modelId) {
    // Initialize client that will be used to send requests. This client only needs to be created
    // once, and can be reused for multiple requests.
    try (Client client =
        Client.builder()
            .location("global")
            .vertexAI(true)
            .httpOptions(HttpOptions.builder().apiVersion("v1").build())
            .build()) {

      // Set the system instruction
      Content systemInstruction =
          Content.fromParts(
              Part.fromText(
                  "You are an expert researcher. You always stick to the facts"
                      + " in the sources provided, and never make up new facts.\n"
                      + "Now look at these research papers, and answer the following questions."));

      // Set pdf files
      Content contents =
          Content.fromParts(
              Part.fromUri(
                  "gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf", "application/pdf"),
              Part.fromUri(
                  "gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf", "application/pdf"));

      // Configuration for cached content using pdfs files and text
      CreateCachedContentConfig config =
          CreateCachedContentConfig.builder()
              .systemInstruction(systemInstruction)
              .contents(contents)
              .displayName("example-cache")
              .ttl(Duration.ofSeconds(86400))
              .build();

      CachedContent cachedContent = client.caches.create(modelId, config);
      cachedContent.name().ifPresent(System.out::println);
      cachedContent.usageMetadata().ifPresent(System.out::println);
      // Example response:
      // projects/111111111111/locations/global/cachedContents/1111111111111111111
      // CachedContentUsageMetadata{audioDurationSeconds=Optional.empty, imageCount=Optional[167],
      // textCount=Optional[153], totalTokenCount=Optional[43125],
      // videoDurationSeconds=Optional.empty}
      return cachedContent.name();
    }
  }
}

  Node.js

      Install

npm install @google/genai

        To learn more, see the

          SDK reference documentation.

Set environment variables to use the Google Gen AI SDK with Vertex AI:

# Replace the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` values
# with appropriate values for your project.
export GOOGLE_CLOUD_PROJECT=GOOGLE_CLOUD_PROJECT
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_ENTERPRISE=True

const {GoogleGenAI} = require('@google/genai');

const GOOGLE_CLOUD_PROJECT = process.env.GOOGLE_CLOUD_PROJECT;
const GOOGLE_CLOUD_LOCATION = process.env.GOOGLE_CLOUD_LOCATION || 'global';
async function generateContentCache(
  projectId = GOOGLE_CLOUD_PROJECT,
  location = GOOGLE_CLOUD_LOCATION
) {
  const client = new GoogleGenAI({
    vertexai: true,
    project: projectId,
    location: location,
    httpOptions: {
      apiVersion: 'v1',
    },
  });

  const systemInstruction = `
  You are an expert researcher. You always stick to the facts in the sources provided, and never make up new facts.
  Now look at these research papers, and answer the following questions.
  `;

  const contents = [
    {
      role: 'user',
      parts: [
        {
          fileData: {
            fileUri:
              'gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf',
            mimeType: 'application/pdf',
          },
        },
        {
          fileData: {
            fileUri: 'gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf',
            mimeType: 'application/pdf',
          },
        },
      ],
    },
  ];

  const contentCache = await client.caches.create({
    model: 'gemini-2.5-flash',
    config: {
      contents: contents,
      systemInstruction: systemInstruction,
      displayName: 'example-cache',
      ttl: '86400s',
    },
  });

  console.log(contentCache);
  console.log(contentCache.name);

  // Example response:
  //  projects/111111111111/locations/us-central1/cachedContents/1111111111111111111
  //  CachedContentUsageMetadata(audio_duration_seconds=None, image_count=167,
  //  text_count=153, total_token_count=43130, video_duration_seconds=None)

  return contentCache.name;
}

  REST

  You can use REST to create a context cache by using the Agent Platform API to send a
  POST request to the publisher model endpoint. The following example shows
  how to create a context cache using a file stored in a Cloud Storage
  bucket.

  Before using any of the request data,
  make the following replacements:

  PROJECT_ID:
Your project ID.

  LOCATION: The region to process the request and where the cached content is stored.
    For a list of supported regions, see Available regions.

  CACHE_DISPLAY_NAME: A
    meaningful display name to describe and to help you identify each context
    cache.

  MIME_TYPE: The MIME type of the content to cache.

  CONTENT_TO_CACHE_URI: The Cloud Storage URI of the content to cache.

  MODEL_ID: The model to use for caching.

  HTTP method and URL:

POST https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/cachedContents

  Request JSON body:

{
  "model": "projects/PROJECT_ID/locations/LOCATION/publishers/google/models/MODEL_ID",
  "displayName": "CACHE_DISPLAY_NAME",
  "contents": [{
    "role": "user",
      "parts": [{
        "fileData": {
          "mimeType": "MIME_TYPE",
          "fileUri": "CONTENT_TO_CACHE_URI"
        }
      }]
  },
  {
    "role": "model",
      "parts": [{
        "text": "This is sample text to demonstrate explicit caching."
      }]
  }]
}

To send your request, choose one of these options:

  curl

      Note:

          The following command assumes that you have logged in to
          the gcloud CLI with your user account by running
          gcloud init
          or
          gcloud auth login

            , or by using Cloud Shell,
            which automatically logs you into the gcloud CLI
            .
          You can check the currently active account by running
          gcloud auth list.

      Save the request body in a file named request.json,
      and execute the following command:

curl -X POST \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d @request.json \
     "https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/cachedContents"

  PowerShell

      Note:

          The following command assumes that you have logged in to
          the gcloud CLI with your user account by running
          gcloud init
          or
          gcloud auth login
            .
          You can check the currently active account by running
          gcloud auth list.

      Save the request body in a file named request.json,
      and execute the following command:

$cred = gcloud auth print-access-token
$headers = @{ "Authorization" = "Bearer $cred" }

Invoke-WebRequest `
    -Method POST `
    -Headers $headers `
    -ContentType: "application/json; charset=utf-8" `
    -InFile request.json `
    -Uri "https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/cachedContents" | Select-Object -Expand Content

You should receive a JSON response similar to the following:

Response

{
  "name": "projects/PROJECT_NUMBER/locations/us-central1/cachedContents/CACHE_ID",
  "model": "projects/PROJECT_ID/locations/us-central1/publishers/google/models/gemini-3.5-flash",
  "createTime": "2024-06-04T01:11:50.808236Z",
  "updateTime": "2024-06-04T01:11:50.808236Z",
  "expireTime": "2024-06-04T02:11:50.794542Z"
}

Example curl command

LOCATION="us-central1"
MODEL_ID="gemini-3.5-flash"
PROJECT_ID="test-project"
MIME_TYPE="video/mp4"
CACHED_CONTENT_URI="gs://path-to-bucket/video-file-name.mp4"

curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/cachedContents -d \
'{
  "model":"projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL_ID}",
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "fileData": {
            "mimeType": "${MIME_TYPE}",
            "fileUri": "${CACHED_CONTENT_URI}"
          }
        }
      ]
    }
  ]
}'

Create a context cache with CMEK

To implement context caching with CMEKs, create a CMEK by following
the instructions and make sure the
Gemini Enterprise Agent Platform per-product, per-project service account (P4SA) has the
necessary Cloud Key Management Service CryptoKey Encrypter/Decrypter permissions on the key.
This lets you securely create and manage cached content as well as make
other calls like {List, Update, Delete, Get} CachedContent(s) without
repeatedly specifying a KMS key.

  REST

  You can use REST to create a context cache by using the Agent Platform API to send a
  POST request to the publisher model endpoint. The following example shows
  how to create a context cache using a file stored in a Cloud Storage
  bucket.

  Before using any of the request data,
  make the following replacements:

  PROJECT_ID: .

  LOCATION: The region to process the request and where the cached content is stored.
    For a list of supported regions, see Available regions.

  MODEL_ID: gemini-3.5-flash.

  CACHE_DISPLAY_NAME: A
    meaningful display name to describe and to help you identify each context
    cache.

  MIME_TYPE: The MIME type of the content to cache.

  CACHED_CONTENT_URI: The Cloud Storage URI of the content to cache.

  KMS_KEY_NAME: The Cloud KMS key name.

  HTTP method and URL:

POST https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/cachedContents

  Request JSON body:

{
  "model": "projects/PROJECT_ID/locations/LOCATION/publishers/google/models/gemini-3.5-flash",
  "displayName": "CACHE_DISPLAY_NAME",
  "contents": [{
    "role": "user",
      "parts": [{
        "fileData": {
          "mimeType": "MIME_TYPE",
          "fileUri": "CONTENT_TO_CACHE_URI"
        }
      }]}],
    "encryptionSpec": {
      "kmsKeyName": "KMS_KEY_NAME"
    }
}

To send your request, choose one of these options:

  curl

      Note:

          The following command assumes that you have logged in to
          the gcloud CLI with your user account by running
          gcloud init
          or
          gcloud auth login

            , or by using Cloud Shell,
            which automatically logs you into the gcloud CLI
            .
          You can check the currently active account by running
          gcloud auth list.

      Save the request body in a file named request.json,
      and execute the following command:

curl -X POST \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d @request.json \
     "https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/cachedContents"

  PowerShell

      Note:

          The following command assumes that you have logged in to
          the gcloud CLI with your user account by running
          gcloud init
          or
          gcloud auth login
            .
          You can check the currently active account by running
          gcloud auth list.

      Save the request body in a file named request.json,
      and execute the following command:

$cred = gcloud auth print-access-token
$headers = @{ "Authorization" = "Bearer $cred" }

Invoke-WebRequest `
    -Method POST `
    -Headers $headers `
    -ContentType: "application/json; charset=utf-8" `
    -InFile request.json `
    -Uri "https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/cachedContents" | Select-Object -Expand Content

You should receive a JSON response similar to the following:

Response

{
  "name": "projects/PROJECT_NUMBER/locations/us-central1/cachedContents/CACHE_ID",
  "model": "projects/PROJECT_ID/locations/us-central1/publishers/google/models/gemini-3.5-flash",
  "createTime": "2024-06-04T01:11:50.808236Z",
  "updateTime": "2024-06-04T01:11:50.808236Z",
  "expireTime": "2024-06-04T02:11:50.794542Z"
}

Example curl command

LOCATION="us-central1"
MODEL_ID="gemini-3.5-flash"
PROJECT_ID="test-project"
MIME_TYPE="video/mp4"
CACHED_CONTENT_URI="gs://path-to-bucket/video-file-name.mp4"
KMS_KEY_NAME="projects/${PROJECT_ID}/locations/{LOCATION}/keyRings/your-key-ring/cryptoKeys/your-key"

curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/cachedContents -d \
'{

"model": "projects/{PROJECT_ID}}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}",
  "contents" : [
    {
      "role": "user",
      "parts": [
        {
          "file_data": {
            "mime_type":"{MIME_TYPE}",
            "file_uri":"{CACHED_CONTENT_URI}"
          }
        }
      ]
    }
  ],
  "encryption_spec" :
  {
    "kms_key_name":"{KMS_KEY_NAME}"
  }
}'

GenAI SDK for Python

Install

pip install --upgrade google-genai

To learn more, see the SDK reference documentation.

Set environment variables to use the Google Gen AI SDK
with Gemini Enterprise Agent Platform:

# Replace the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` values
# with appropriate values for your project.
export GOOGLE_CLOUD_PROJECT=GOOGLE_CLOUD_PROJECT
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_ENTERPRISE=True

import os
from google import genai
from google.genai.types import Content, CreateCachedContentConfig, HttpOptions, Part

os.environ['GOOGLE_CLOUD_PROJECT'] = 'vertexsdk'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_ENTERPRISE'] = 'True'

client = genai.Client(http_options=HttpOptions(api_version="v1"))

system_instruction = """
You are an expert researcher. You always stick to the facts in the sources provided, and never make up new facts.
Now look at these research papers, and answer the following questions.
"""

contents = [
    Content(
        role="user",
        parts=[
            Part.from_uri(
                file_uri="gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf",
                mime_type="application/pdf",
            ),
            Part.from_uri(
                file_uri="gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf",
                mime_type="application/pdf",
            ),
        ],
    )
]

content_cache = client.caches.create(
    model="gemini-3.5-flash",
    config=CreateCachedContentConfig(
        contents=contents,
        system_instruction=system_instruction,
        display_name="example-cache",
        kms_key_name="projects/vertexsdk/locations/us-central1/keyRings/your-project/cryptoKeys/your-key",
        ttl="86400s",
    ),
)

print(content_cache.name)
print(content_cache.usage_metadata)

GenAI SDK for Go

Learn how to install or update the Google Gen AI SDK for Go.

To learn more, see the SDK reference documentation.

Set environment variables to use the Google Gen AI SDK
with Gemini Enterprise Agent Platform:

import (
    "context"
    "encoding/json"
    "fmt"
    "io"

    genai "google.golang.org/genai"
)

// createContentCache shows how to create a content cache with an expiration parameter.
func createContentCache(w io.Writer) (string, error) {
    ctx := context.Background()

    client, err := genai.NewClient(ctx, &genai.ClientConfig{
        HTTPOptions: genai.HTTPOptions{APIVersion: "v1beta1"},
    })
    if err != nil {
        return "", fmt.Errorf("failed to create genai client: %w", err)
    }

    modelName := "gemini-3.5-flash"

    systemInstruction := "You are an expert researcher. You always stick to the facts " +
        "in the sources provided, and never make up new facts. " +
        "Now look at these research papers, and answer the following questions."

    cacheContents := []*genai.Content{
        {
            Parts: []*genai.Part{
                {FileData: &genai.FileData{
                    FileURI:  "gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf",
                    MIMEType: "application/pdf",
                }},
                {FileData: &genai.FileData{
                    FileURI:  "gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf",
                    MIMEType: "application/pdf",
                }},
            },
            Role: "user",
        },
    }
    config := &genai.CreateCachedContentConfig{
        Contents: cacheContents,
        SystemInstruction: &genai.Content{
            Parts: []*genai.Part{
                {Text: systemInstruction},
            },
        },
        DisplayName: "example-cache",
        KmsKeyName:  "projects/vertexsdk/locations/us-central1/keyRings/your-project/cryptoKeys/your-key",
        TTL:         "86400s",
    }

    res, err := client.Caches.Create(ctx, modelName, config)
    if err != nil {
        return "", fmt.Errorf("failed to create content cache: %w", err)
    }

    cachedContent, err := json.MarshalIndent(res, "", "  ")
    if err != nil {
        return "", fmt.Errorf("failed to marshal cache info: %w", err)
    }

    // See the documentation: https://pkg.go.dev/google.golang.org/genai#CachedContent
    fmt.Fprintln(w, string(cachedContent))

    return res.Name, nil
}

What's next

Learn how to use a context cache.

Learn how to update the expiration time of a context cache.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-09-02 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-09-02 UTC."],[],[]]
