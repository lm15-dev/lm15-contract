> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Check Balance

> Check the available balance of the current account.

Check your available, voucher, and cash balances on the Kimi Open Platform. When the available balance is less than or equal to 0, you cannot call the inference API.

<Accordion title="Usage Example">
  <CodeGroup>
    ```python python expandable theme={null}
    import os
    import requests

    api_key = os.environ.get("MOONSHOT_API_KEY")
    url = "https://api.moonshot.ai/v1/users/me/balance"

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    print(response.json())
    ```

    ```bash curl expandable theme={null}
    curl https://api.moonshot.ai/v1/users/me/balance \
      -H "Authorization: Bearer $MOONSHOT_API_KEY"
    ```

    ```javascript node.js expandable theme={null}
    const apiKey = process.env.MOONSHOT_API_KEY;

    async function main() {
        const response = await fetch("https://api.moonshot.ai/v1/users/me/balance", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${apiKey}`,
            },
        });
        const data = await response.json();
        console.log(data);
    }

    main();
    ```
  </CodeGroup>
</Accordion>

<Accordion title="Response Fields">
  | Field                    | Type    | Description                                                                                                                                                                   |
  | ------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `code`                   | integer | Response code. 0 indicates success.                                                                                                                                           |
  | `data`                   | object  | Balance data object                                                                                                                                                           |
  | `data.available_balance` | number  | The available balance (unit: USD), including cash balance and voucher balance. When it is less than or equal to 0, the user cannot call the inference API                     |
  | `data.voucher_balance`   | number  | The voucher balance (unit: USD), which cannot be negative                                                                                                                     |
  | `data.cash_balance`      | number  | The cash balance (unit: USD), which can be negative, indicating that the user owes money. When it is negative, `available_balance` is equal to the value of `voucher_balance` |
  | `scode`                  | string  | Status code                                                                                                                                                                   |
  | `status`                 | boolean | Request status                                                                                                                                                                |

  **Response Example**

  ```json theme={null}
  {
      "code": 0,
      "data": {
          "available_balance": 49.58894,
          "voucher_balance": 46.58893,
          "cash_balance": 3.00001
      },
      "scode": "0x0",
      "status": true
  }
  ```
</Accordion>

<Warning>
  When `available_balance` is less than or equal to 0, API requests will return an `exceeded_current_quota_error` error. Please recharge your account or check your voucher validity.
</Warning>

<Note>
  API Keys from `platform.kimi.ai` and `platform.kimi.com` are completely independent. Using a Key from one platform on the other will result in a 401 error. Ensure your endpoint matches the platform where the Key was created.
</Note>


## OpenAPI

````yaml GET /v1/users/me/balance
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
  /v1/users/me/balance:
    get:
      tags:
        - Billing
      summary: Check Balance
      description: >-
        REST API to check your available, voucher, and cash balances on Kimi
        OpenPlatform.
      responses:
        '200':
          description: Balance information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BalanceResponse'
        '401':
          description: Unauthorized - Invalid or missing API key
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
    BalanceResponse:
      type: object
      properties:
        code:
          type: integer
          description: Response code. 0 indicates success.
        data:
          type: object
          properties:
            available_balance:
              type: number
              format: float
              description: >-
                The available balance (unit: USD), including cash balance and
                voucher balance. When it is less than or equal to 0, the user
                cannot call the inference API
              example: 49.58894
            voucher_balance:
              type: number
              format: float
              description: 'The voucher balance (unit: USD), which cannot be negative'
              example: 46.58893
            cash_balance:
              type: number
              format: float
              description: >-
                The cash balance (unit: USD), which can be negative, indicating
                that the user owes money. When it is negative, available_balance
                is equal to the value of voucher_balance
              example: 3.00001
          required:
            - available_balance
            - voucher_balance
            - cash_balance
        scode:
          type: string
          description: Status code
          example: '0x0'
        status:
          type: boolean
          description: Request status
          example: true
      required:
        - code
        - data
        - scode
        - status
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