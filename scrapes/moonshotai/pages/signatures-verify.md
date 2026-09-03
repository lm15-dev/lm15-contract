> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Verify Request Signature

> Verify a request signature to prove that a request was handled by the Kimi API for the specified model, rather than routed elsewhere.

Request Signature lets you prove that a request actually reached the Kimi API itself, rather than being forwarded elsewhere or served by a different model through an intermediary. Anyone holding the nonce, timestamp, model, and signature can use this endpoint to verify that the Kimi API accepted the request for the specified model at that time — for example, to show users or third parties that a service is backed by the official Kimi API, to check that a proxy has not substituted the model, or for auditing and dispute resolution.

When calling the [Chat Completions](/docs/api/chat), [Responses](/docs/api/responses), or [Messages](/docs/api/messages) API, send a random nonce (a UUID v4 is recommended) in the `X-Msh-Request-Nonce` request header. The response then carries `Msh-Request-Timestamp` (the Unix millisecond timestamp at which the Kimi API accepted the request) and `Msh-Request-Signature` (a signature token prefixed with `reqsigv1_`), for both streaming and non-streaming requests. Submit the nonce, timestamp, the request's `model`, and the signature to this endpoint; it returns `valid: true` when the signature matches all three exactly, and `valid: false` otherwise.

The signature only proves that the Kimi API accepted this nonce and request model at that time; it does not prove that the request ultimately succeeded or that the response is complete. The server does not record nonces, so replaying the same parameters still returns `valid: true` — replay protection and validity windows are the caller's responsibility.

<Accordion title="Example">
  <CodeGroup>
    ```python python expandable theme={null}
    import os
    import uuid

    import requests
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"],
        base_url="https://api.moonshot.ai/v1",
    )

    nonce: str = str(uuid.uuid4())
    model: str = "kimi-k2.7-code"

    # 1. Call the model endpoint with X-Msh-Request-Nonce and read the response headers
    raw = client.chat.completions.with_raw_response.create(
        model=model,
        messages=[{"role": "user", "content": "Hello"}],
        extra_headers={"X-Msh-Request-Nonce": nonce},
    )
    timestamp: int = int(raw.headers["Msh-Request-Timestamp"])
    signature: str = raw.headers["Msh-Request-Signature"]

    # 2. Verify the signature
    verify = requests.post(
        "https://api.moonshot.ai/v1/signatures/verify",
        headers={
            "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "nonce": nonce,
            "timestamp": timestamp,
            "model": model,
            "signature": signature,
        },
    )
    print(verify.json())  # {"valid": true}
    ```

    ```bash curl expandable theme={null}
    NONCE="$(uuidgen)"
    MODEL="kimi-k2.7-code"

    # 1. Call the model endpoint with X-Msh-Request-Nonce and save the response headers
    curl -sS -D response.headers -o response.json \
      https://api.moonshot.ai/v1/chat/completions \
      -H "Authorization: Bearer $MOONSHOT_API_KEY" \
      -H "Content-Type: application/json" \
      -H "X-Msh-Request-Nonce: $NONCE" \
      -d "{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello\"}]}"

    TIMESTAMP="$(awk -F': ' 'tolower($1)=="msh-request-timestamp" {gsub("\\r", "", $2); print $2}' response.headers)"
    SIGNATURE="$(awk -F': ' 'tolower($1)=="msh-request-signature" {gsub("\\r", "", $2); print $2}' response.headers)"

    # 2. Verify the signature
    curl -sS https://api.moonshot.ai/v1/signatures/verify \
      -H "Authorization: Bearer $MOONSHOT_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"nonce\": \"$NONCE\", \"timestamp\": $TIMESTAMP, \"model\": \"$MODEL\", \"signature\": \"$SIGNATURE\"}"
    ```

    ```javascript node.js expandable theme={null}
    const { randomUUID } = require("crypto");
    const OpenAI = require("openai");

    const apiKey = process.env.MOONSHOT_API_KEY;
    const client = new OpenAI({
        apiKey,
        baseURL: "https://api.moonshot.ai/v1",
    });

    async function main() {
        const nonce = randomUUID();
        const model = "kimi-k2.7-code";

        // 1. Call the model endpoint with X-Msh-Request-Nonce and read the response headers
        const { response } = await client.chat.completions
            .create(
                { model, messages: [{ role: "user", content: "Hello" }] },
                { headers: { "X-Msh-Request-Nonce": nonce } },
            )
            .withResponse();
        const timestamp = Number(response.headers.get("Msh-Request-Timestamp"));
        const signature = response.headers.get("Msh-Request-Signature");

        // 2. Verify the signature
        const verify = await fetch("https://api.moonshot.ai/v1/signatures/verify", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${apiKey}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ nonce, timestamp, model, signature }),
        });
        console.log(await verify.json()); // { valid: true }
    }

    main();
    ```
  </CodeGroup>
</Accordion>


## OpenAPI

````yaml POST /v1/signatures/verify
openapi: 3.1.0
info:
  title: Moonshot AI API
  version: 1.0.0
  description: API for Moonshot AI / Kimi large language model services
servers:
  - url: https://api.moonshot.ai
    description: Production
security: []
paths:
  /v1/signatures/verify:
    post:
      tags:
        - Utilities
      summary: Verify Request Signature
      description: >-
        Verifies a request signature returned in the response headers of the
        Chat Completions, Responses, or Messages API, proving that the request
        was handled by the Kimi API for the specified model rather than routed
        elsewhere. Submit the nonce used in the call, the timestamp from the
        response headers, the request's model, and the signature; the endpoint
        returns `valid: true` when the signature matches these three attributes
        exactly, and `valid: false` otherwise.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SignatureVerifyRequest'
      responses:
        '200':
          description: Verification result
          headers:
            Cache-Control:
              description: Always `no-store`; verification results must not be cached.
              schema:
                type: string
                example: no-store
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SignatureVerifyResponse'
        '400':
          description: Bad request - Invalid parameters or missing required fields
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized - Invalid or missing API key
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '429':
          description: Rate limited
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
      security:
        - bearerAuth: []
components:
  schemas:
    SignatureVerifyRequest:
      type: object
      properties:
        nonce:
          type: string
          description: >-
            The nonce sent in the `X-Msh-Request-Nonce` request header of the
            model call, exactly as sent.
          minLength: 1
          example: 7d929748-0ae6-41c2-ab5d-a186498ad721
        timestamp:
          type: integer
          format: int64
          description: >-
            The Unix millisecond timestamp returned in the
            `Msh-Request-Timestamp` response header of the model call.
          minimum: 1
          example: 1786338000123
        model:
          type: string
          description: >-
            The `model` value from the request body of the model call, exactly
            as sent.
          minLength: 1
          example: kimi-k2.7-code
        signature:
          type: string
          description: >-
            The signature token returned in the `Msh-Request-Signature` response
            header of the model call.
          minLength: 1
          example: reqsigv1_<opaque-token>
      required:
        - nonce
        - timestamp
        - model
        - signature
    SignatureVerifyResponse:
      type: object
      properties:
        valid:
          type: boolean
          description: >-
            Whether the signature is valid. `true` means the signature was
            issued by the Kimi API and matches the submitted nonce, timestamp,
            and model exactly; otherwise `false`.
          example: true
      required:
        - valid
    ErrorResponse:
      type: object
      properties:
        error:
          type: object
          properties:
            message:
              type: string
              description: Error message describing what went wrong
            type:
              type: string
              description: Error type
            code:
              type: string
              description: Error code
          required:
            - message
      required:
        - error
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        The Authorization header expects a Bearer token. Use an MOONSHOT_API_KEY
        as the token. This is a server-side secret key. Generate one on the [API
        keys page](https://platform.kimi.ai/console/api-keys) in your dashboard.

````