> ## Documentation Index
> Fetch the complete documentation index at: https://docs.z.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Errors

When calling the API, the response code consists of two parts: the outer layer is the HTTP status code, and the inner layer is the business error code defined by Z.AI in the response body, which provides a more detailed error description.

| Error Codes | ​HTTP Status Code | Error messege                                                                                                                                                                                                                              |
| :---------- | :---------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -           | 500               | Internal Error                                                                                                                                                                                                                             |
| 1000        | 401               | Authentication Failed                                                                                                                                                                                                                      |
| 1001        | 401               | Authentication parameter not received in Header, unable to authenticate                                                                                                                                                                    |
| 1003        | 401               | Authentication Token expired, please regenerate/obtain                                                                                                                                                                                     |
| 1005        | 401               | Need Two-Factor Authentication                                                                                                                                                                                                             |
| 1113        | 429               | Insufficient balance or no resource package. Please recharge.                                                                                                                                                                              |
| 1200        | 500               | API Call Error                                                                                                                                                                                                                             |
| 1210        | 400               | Invalid API parameter, please check the documentation.                                                                                                                                                                                     |
| 1211        | 400               | Unknown Model, please check the model code.                                                                                                                                                                                                |
| 1212        | 400               | Current model does not support `${method}` call method                                                                                                                                                                                     |
| 1213        | 400               | Parameter `${field}` was not received.                                                                                                                                                                                                     |
| 1214        | 400               | Parameter `${field}` is invalid. Please check the documentation.                                                                                                                                                                           |
| 1215        | 400               | `${field1}` and `${field2}` cannot be set simultaneously, please check the documentation                                                                                                                                                   |
| 1220        | 403               | You do not have permission to access \${API_name}                                                                                                                                                                                          |
| 1221        | 400               | API `${API_name}` has been taken offline                                                                                                                                                                                                   |
| 1222        | 400               | API `${API_name}` does not exist                                                                                                                                                                                                           |
| 1230        | 500               | API call process error                                                                                                                                                                                                                     |
| 1234        | 500               | Network error, error id: `${error_id}`, please try again later                                                                                                                                                                             |
| 1261        | 400               | Prompt too long                                                                                                                                                                                                                            |
| 1301        | 400               | System detected potentially unsafe or sensitive content in input or generation. Please avoid using prompts that may generate sensitive content. Thank you for your cooperation.                                                            |
| 1302        | 429               | Rate limit reached for requests                                                                                                                                                                                                            |
| 1305        | 429               | The service may be temporarily overloaded, please try again later                                                                                                                                                                          |
| 1308        | 429               | Usage limit reached for `{number}` `{unit}`. Your limit will reset at `{next_flush_time}`                                                                                                                                                  |
| 1309        | 429               | Your GLM Coding Plan package has expired and is temporarily unavailable. You can resume using it after renewing the subscription on the official website. [https://z.ai/subscribe。](https://z.ai/subscribe。)                               |
| 1310        | 429               | Weekly/Monthly Limit Exhausted. Your limit will reset at `{next_flush_time}`                                                                                                                                                               |
| 1311        | 429               | Your current subscription plan does not yet include access to `${model_name}`                                                                                                                                                              |
| 1313        | 429               | Your account's current usage pattern does not comply with the Fair Usage Policy, and your request frequency has been limited. For details, please refer to the Subscription Service Agreement. To restore access, please submit a request. |
| 1314        | 429               | Your enterprise package has expired. Please contact your enterprise administrator.                                                                                                                                                         |
| 1315        | 429               | This API Key is limited to enterprise coding package scenarios. Please go to the official website to replace the API Key of the corresponding product type.                                                                                |
| 1316        | 429               | Usage limit reached for the past 5 hours. Insufficient balance for extra usage. Resets at `{next_flush_time}`.                                                                                                                             |
| 1317        | 429               | Usage limit reached for the past 7 days. Insufficient balance for extra usage. Resets at `{next_flush_time}`.                                                                                                                              |
| 1318        | 429               | Usage limit reached for the past 5 hours. Extra usage is not available due to monthly spend limit. Resets at `{next_flush_time}`.                                                                                                          |
| 1319        | 429               | Usage limit reached for the past 7 days. Extra usage is not available due to monthly spend limit. Resets at `{next_flush_time}`.                                                                                                           |
| 1320        | 429               | Usage limit reached for the past 5 hours. Extra usage is not available due to monthly spend limit. Resets at `{next_flush_time}`.                                                                                                          |
| 1321        | 429               | Usage limit reached for the past 7 days. Extra usage is not available due to monthly spend limit. Resets at `{next_flush_time}`.                                                                                                           |

## Error Shapes

Errors are always returned as JSON, with a top-level error object that includes a `code` and `message` value.

```json theme={null}
{
  "error": {
    "code": "1214",
    "message": "Parameter `${field}` is invalid. Please check the documentation."
  }
}
```

## Error Example

The following is the response message of a curl request, where 401 is the HTTP status code and 1001 is the business error code.

```
* We are completely uploaded and fine
< HTTP/2 401
< date: Wed, 20 Mar 2024 03:06:05 GMT
< content-type: application/json
< set-cookie: acw_tc=76b20****a0e42;path=/;HttpOnly;Max-Age=1800
< server: nginx/1.21.6
< vary: Origin
< vary: Access-Control-Request-Method
< vary: Access-Control-Request-Headers
<
* Connection #0 to host open.z.ai left intact
{"error":{"code":"1001","message":"Authentication parameter not received in Header, unable to authenticate"}}
```

> **Note**: When using streaming (SSE) calls, if the API terminates abnormally during inference, the above error codes will not be returned. Instead, the reason for the exception will be provided in the `finish_reason` parameter of the response body. For details, please refer to the description of the `finish_reason` parameter.
