> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Structured outputs

> Use JSON mode to get structured outputs from supported chat models.

Standard chat models return plain text, which is hard to parse if your app needs to read specific fields from the response.

Supported models can return JSON that conforms to any schema you supply, so you can read the output directly in code without retries or fragile parsing. Pass the schema in the `response_format` key on the chat completions request.

## Supported models

For the current list of models that support structured outputs, see the [serverless](/docs/serverless/models) and [dedicated model inference](/docs/dedicated-endpoints/models) catalogs.

## Basic example

Pass a transcript of a voice note to a model and ask it to return a summary in this shape:

```json JSON theme={null}
{
  "title": "A title for the voice note",
  "summary": "A short one-sentence summary of the voice note",
  "actionItems": ["Action item 1", "Action item 2"]
}
```

To enforce the structure, give the model a [JSON Schema](https://json-schema.org/). Writing JSON Schema by hand is tedious, so use a helper library: Pydantic in Python, Zod in TypeScript.

Include the schema in the system prompt and pass it via the `response_format` key:

<CodeGroup>
  ```python Python theme={null}
  import json
  import together
  from pydantic import BaseModel, Field

  client = together.Together()


  ## Define the schema for the output
  class VoiceNote(BaseModel):
      title: str = Field(description="A title for the voice note")
      summary: str = Field(
          description="A short one sentence summary of the voice note."
      )
      actionItems: list[str] = Field(
          description="A list of action items from the voice note"
      )


  def main():
      transcript = (
          "Good morning! It's 7:00 AM, and I'm just waking up. Today is going to be a busy day, "
          "so let's get started. First, I need to make a quick breakfast. I think I'll have some "
          "scrambled eggs and toast with a cup of coffee. While I'm cooking, I'll also check my "
          "emails to see if there's anything urgent."
      )

      # Call the LLM with the JSON schema
      extract = client.chat.completions.create(
          messages=[
              {
                  "role": "system",
                  "content": f"The following is a voice message transcript. Only answer in JSON and follow this schema {json.dumps(VoiceNote.model_json_schema())}.",
              },
              {
                  "role": "user",
                  "content": transcript,
              },
          ],
          model="Qwen/Qwen3.5-9B",
          reasoning={"enabled": False},
          response_format={
              "type": "json_schema",
              "json_schema": {
                  "name": "voice_note",
                  "schema": VoiceNote.model_json_schema(),
              },
          },
      )

      output = json.loads(extract.choices[0].message.content)
      print(json.dumps(output, indent=2))
      return output


  main()
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";
  import { z } from "zod";

  const together = new Together();

  // Define the schema for the output data
  const voiceNoteSchema = z.object({
    title: z.string().describe("A title for the voice note"),
    summary: z
      .string()
      .describe("A short one sentence summary of the voice note."),
    actionItems: z
      .array(z.string())
      .describe("A list of action items from the voice note"),
  });
  const jsonSchema = z.toJSONSchema(voiceNoteSchema);

  async function main() {
    const transcript =
      "Good morning! It's 7:00 AM, and I'm just waking up. Today is going to be a busy day, so let's get started. First, I need to make a quick breakfast. I think I'll have some scrambled eggs and toast with a cup of coffee. While I'm cooking, I'll also check my emails to see if there's anything urgent.";
    const extract = await together.chat.completions.create({
      messages: [
        {
          role: "system",
          content: `The following is a voice message transcript. Only answer in JSON and follow this schema ${JSON.stringify(jsonSchema)}.`,
        },
        {
          role: "user",
          content: transcript,
        },
      ],
      model: "Qwen/Qwen3.5-9B",
      reasoning: { enabled: false },
      response_format: {
        type: "json_schema",
        json_schema: {
          name: "voice_note",
          schema: jsonSchema,
        },
      },
    });

    if (extract?.choices?.[0]?.message?.content) {
      const output = JSON.parse(extract?.choices?.[0]?.message?.content);
      console.log(output);
      return output;
    }
    return "No output.";
  }

  main();
  ```

  ```bash cURL theme={null}
  curl -X POST https://api.together.ai/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOGETHER_API_KEY" \
    -d '{
    "messages": [
      {
        "role": "system",
        "content": "The following is a voice message transcript. Only answer in JSON."
      },
      {
        "role": "user",
        "content": "Good morning! It'"'"'s 7:00 AM, and I'"'"'m just waking up. Today is going to be a busy day, so let'"'"'s get started. First, I need to make a quick breakfast. I think I'"'"'ll have some scrambled eggs and toast with a cup of coffee. While I'"'"'m cooking, I'"'"'ll also check my emails to see if there'"'"'s anything urgent."
      }
    ],
    "model": "Qwen/Qwen3.5-9B",
    "reasoning": {"enabled": false},
    "response_format": {
      "type": "json_schema",
      "json_schema": {
        "name": "voice_note",
        "schema": {
          "properties": {
            "title": {
              "description": "A title for the voice note",
              "title": "Title",
              "type": "string"
            },
            "summary": {
              "description": "A short one sentence summary of the voice note.",
              "title": "Summary",
              "type": "string"
            },
            "actionItems": {
              "description": "A list of action items from the voice note",
              "items": { "type": "string" },
              "title": "Actionitems",
              "type": "array"
            }
          },
          "required": ["title", "summary", "actionItems"],
          "title": "VoiceNote",
          "type": "object"
        }
      }
    }
  }'
  ```
</CodeGroup>

The model responds with output that matches the schema:

```json JSON theme={null}
{
  "title": "Morning Routine",
  "summary": "Starting the day with a quick breakfast and checking emails",
  "actionItems": [
    "Cook scrambled eggs and toast",
    "Brew a cup of coffee",
    "Check emails for urgent messages"
  ]
}
```

### Prompt the model

Always tell the model to respond **only in JSON** and include a plain-text copy of the schema in the prompt (as a system prompt or a user message). Send this instruction *in addition* to passing the schema via the `response_format` parameter.

The combination of an explicit "respond in JSON" direction, the schema text in the prompt, and the `response_format` setting produces consistent, valid JSON every time.

## Regex example

Every model that supports JSON mode also supports regex mode. The example below uses regex to constrain a sentiment classification to one of three labels.

<CodeGroup>
  ```python Python theme={null}
  import together

  client = together.Together()

  completion = client.chat.completions.create(
      model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
      messages=[
          {
              "role": "system",
              "content": "You are an AI-powered expert specializing in classifying sentiment. You will be provided with a text, and your task is to classify its sentiment as positive, neutral, or negative.",
          },
          {"role": "user", "content": "Wow. I loved the movie!"},
      ],
      response_format={
          "type": "regex",
          "pattern": "(positive|neutral|negative)",
      },
  )

  print(completion.choices[0].message.content)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";
  const together = new Together();

  async function main() {
    const completion = await together.chat.completions.create({
      model: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
      temperature: 0.2,
      max_tokens: 10,
      messages: [
        {
          role: "system",
          content:
            "You are an AI-powered expert specializing in classifying sentiment. You will be provided with a text, and your task is to classify its sentiment as positive, neutral, or negative.",
        },
        {
          role: "user",
          content: "Wow. I loved the movie!",
        },
      ],
      response_format: {
        type: "regex",
        // @ts-ignore
        pattern: "(positive|neutral|negative)",
      },
    });

    console.log(completion?.choices[0]?.message?.content);
  }

  main();
  ```

  ```bash cURL theme={null}
  curl https://api.together.ai/v1/chat/completions \
    -H "Authorization: Bearer $TOGETHER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
      "messages": [
        {
          "role": "user",
          "content": "Return only an email address for Alan Turing at Enigma. End with .com and newline."
        }
      ],
      "stop": ["\n"],
      "response_format": {
        "type": "regex",
        "pattern": "\\w+@\\w+\\.com\\n"
      },
      "temperature": 0.0,
      "max_tokens": 50
    }'
  ```
</CodeGroup>

<Note>
  Structured outputs work with reasoning models too. See [Structured outputs with reasoning models](/docs/inference/chat/reasoning#structured-outputs-with-reasoning-models) on the reasoning page.

  You can also combine structured outputs with vision models to extract typed data from images. See [Structured extraction with vision models](/docs/inference/vision/structured-extraction) on the vision page.
</Note>

## Troubleshooting

If your generated JSON gets cut off, contains stray characters, or fails to parse, the cause is usually one of two things.

**Token limits:** The model can run out of output budget mid-structure. Check the `max_tokens` you're sending against the model's ceiling, and watch for a `finish_reason` of `length` in the response. If the model truncates, the JSON is incomplete (unterminated strings, missing closing brackets) regardless of how good your schema is. Either raise `max_tokens` or simplify the schema.

**Malformed example JSON:** If your prompt includes an example JSON object, the model follows the example exactly, syntax errors and all. Validate any JSON you embed in prompts before using it. Common symptoms of a bad example: unterminated strings, repeated newlines, repeated keys, or output that stops abruptly with `finish_reason: stop`.

## Test schemas in the Together playground

Test variations on your schema and prompts in the [Together model playground](https://api.together.ai/playground/chat/moonshotai/Kimi-K3):

Open the **Response format** dropdown in the right sidebar, choose JSON, select **Add schema**, then paste in your schema.
