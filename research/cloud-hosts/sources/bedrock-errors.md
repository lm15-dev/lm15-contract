# Common Error Types

This section lists common error types that this AWS service may return. Not all services return all error types listed here. For errors specific to an API action for this service, see the topic for that API action.

 **AccessDeniedException**
You don't have permission to perform this action. Verify that your IAM policy includes the required permissions.
HTTP Status Code: 403

 **ExpiredTokenException**
The security token included in the request has expired. Request a new security token and try again.
HTTP Status Code: 403

 **IncompleteSignature**
The request signature doesn't conform to AWS standards. Verify that you're using valid AWS credentials and that your request is properly formatted. If you're using an SDK, ensure it's up to date.
HTTP Status Code: 403

 **InternalFailure**
The request can't be processed right now because of an internal server issue. Try again later. If the problem persists, contact AWS Support.
HTTP Status Code: 500

 **MalformedHttpRequestException**
The request body can't be processed. This typically happens when the request body can't be decompressed using the specified content encoding algorithm. Verify that the content encoding header matches the compression format used.
HTTP Status Code: 400

 **NotAuthorized**
You don't have permissions to perform this action. Verify that your IAM policy includes the required permissions.
HTTP Status Code: 401

 **OptInRequired**
Your AWS account needs a subscription for this service. Verify that you've enabled the service in your account.
HTTP Status Code: 403

 **RequestAbortedException**
The request was aborted before a response could be returned. This typically happens when the client closes the connection.
HTTP Status Code: 400

 **RequestEntityTooLargeException**
The request entity is too large. Reduce the size of the request body and try again.
HTTP Status Code: 413

 **RequestTimeoutException**
The request timed out. The server didn't receive the complete request within the expected time frame. Try again.
HTTP Status Code: 408

 **ServiceUnavailable**
The service is temporarily unavailable. Try again later.
HTTP Status Code: 503

 **ThrottlingException**
Your request rate is too high. The AWS SDKs automatically retry requests that receive this exception. Reduce the frequency of requests.
HTTP Status Code: 400

 **UnknownOperationException**
The action or operation isn't recognized. Verify that the action name is spelled correctly and that it's supported by the API version you're using.
HTTP Status Code: 404

 **UnrecognizedClientException**
The X.509 certificate or AWS access key ID you provided doesn't exist in our records. Verify that you're using valid credentials and that they haven't expired.
HTTP Status Code: 403

 **ValidationError**
The input doesn't meet the required format or constraints. Check that all required parameters are included and that values are valid.
HTTP Status Code: 400
