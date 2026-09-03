> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# How to Fix Repeated Tool Calls

> Check the tool_calls message layout, detect repeated tool calls on the client side, and use system prompt reminders to stop the model from repeating the same tool call.

When using tool calls (`tool_calls`), the model may issue multiple consecutive tool calls based on the context.

If you find that the model repeatedly calls **the same tool**, each call uses exactly the same `function.name` and `function.arguments`, and the tool result does not provide new useful information, you can treat it as a repeated tool call.

## Check the Message Layout

When handling this issue, we recommend checking the message layout first:

1. When the Kimi API returns `finish_reason=tool_calls`, make sure the returned `choice.message` has been added to the `messages` list as is.
2. Make sure each `tool_call` has a corresponding message with `role=tool`.
3. Make sure the `tool_call_id` in the `role=tool` message exactly matches the corresponding `tool_call.id`.
4. If you use streaming output with `stream=True`, make sure the streamed `tool_calls` chunks have been assembled correctly, especially the `function.arguments` field.

## Client-Side Repeated-Call Detection

If the message layout is correct but the model still repeatedly calls the same tool with the same arguments, you can add repeated-call detection on the client side and append a reminder to the system prompt in the next request.

When the same tool and the same arguments are repeated 3 consecutive times, you can append:

```text theme={null}
<system-reminder>
You are repeating the exact same tool call with identical parameters. Please carefully analyze the previous result. If the task is not yet complete, try a different method or parameters instead of repeating the same call.
</system-reminder>
```

When the repeated call reaches 5 consecutive times, you can append a stronger reminder that includes the tool name, repeat count, and arguments:

```text theme={null}
<system-reminder>
You have repeatedly called the same tool with identical parameters many times.
Repeated tool call detected:
- tool: {tool_name}
- repeated_times: {repeat_count}
- arguments: {tool_arguments}
The previous repeated calls did not make progress. Do not call this exact same tool with the exact same arguments again.
Carefully inspect the latest tool result and choose a different next action, different parameters, or finish the task if enough evidence has been gathered.
</system-reminder>
```

If the same tool and the same arguments are repeated 8 consecutive times, we recommend appending the stronger reminder again.

Note: `<system-reminder>` is only an example prompt, not a special field of the Kimi API. You can merge it into the next `role=system` message, or write it into the system prompt based on your own message management logic. To avoid false positives, we recommend triggering this reminder only when the same tool, the same arguments, consecutive repetition, and no new progress from the tool result are all true.
