> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Model Parameter Reference

> Compare default values, supported ranges, and constraints for Chat Completions API parameters across Kimi model families.

export const DocTable = ({columns = [], rows = []}) => {
  return <div className="doc-table-wrap">
      <table className="doc-table">
        {columns.length > 0 ? <colgroup>
            {columns.map((column, index) => <col key={index} style={column.width ? {
    width: column.width
  } : undefined} />)}
          </colgroup> : null}
        <thead>
          <tr>
            {columns.map((column, index) => <th key={index}>{column.title}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => <tr key={rowIndex}>
              {row.map((cell, cellIndex) => <td key={cellIndex}>{cell}</td>)}
            </tr>)}
        </tbody>
      </table>
    </div>;
};

Different model families have different defaults and constraints for Chat Completions API parameters. For the full model list, see the [Model List](/docs/models).

## Parameter Comparison

<DocTable
  columns={[
{ title: "Parameter", width: "25%" },
{ title: "kimi-k3", width: "25%" },
{ title: "kimi-k2.7-code series", width: "25%" },
{ title: "kimi-k2.6", width: "25%" },
]}
  rows={[
[<code>temperature</code>, <strong>Cannot be modified</strong>, <strong>Cannot be modified</strong>, <strong>Cannot be modified</strong>],
[<code>top_p</code>, <>0.95 <strong>Cannot be modified</strong></>, <>0.95 <strong>Cannot be modified</strong></>, <>0.95 <strong>Cannot be modified</strong></>],
[<code>n</code>, <>1 <strong>Cannot be modified</strong></>, <>1 <strong>Cannot be modified</strong></>, <>1 <strong>Cannot be modified</strong></>],
[<code>presence_penalty</code>, <>0 <strong>Cannot be modified</strong></>, <>0 <strong>Cannot be modified</strong></>, <>0 <strong>Cannot be modified</strong></>],
[<code>frequency_penalty</code>, <>0 <strong>Cannot be modified</strong></>, <>0 <strong>Cannot be modified</strong></>, <>0 <strong>Cannot be modified</strong></>],
[<>Reasoning control</>, <code>reasoning_effort</code>, <code>thinking</code>, <code>thinking</code>],
]}
/>

<Note>
  When `temperature` is close to 0, `n` can only be 1. Otherwise, the API returns `invalid_request_error`.
</Note>

## Model Parameter Differences

When switching models, you need to look beyond the `model` field — models differ in which request parameters they support and what defaults they use:

| Parameter                                | `kimi-k3`                                      | `kimi-k2.7-code`                                                                      | `kimi-k2.6`                                                                              |
| ---------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Context window                           | 1M tokens                                      | 256K tokens                                                                           | 256K tokens                                                                              |
| `thinking`                               | —                                              | May be omitted; if set explicitly, only `{"type":"enabled","keep":"all"}` is accepted | `{"type":"enabled"}` (default), `{"type":"disabled"}`, `{"type":"enabled","keep":"all"}` |
| `reasoning_effort`                       | `"low"` / `"high"` / `"max"` (default `"max"`) | Not supported                                                                         | Not supported                                                                            |
| `tool_choice`                            | `auto` / `none` / `required`                   | `required` not supported                                                              | `required` not supported                                                                 |
| `temperature`                            | Fixed at `1.0`                                 | Fixed at `1.0`                                                                        | `1.0` thinking / `0.6` non-thinking                                                      |
| `top_p`                                  | Fixed at `0.95`                                | Fixed at `0.95`                                                                       | Fixed at `0.95`                                                                          |
| `n`                                      | Fixed at `1`                                   | Fixed at `1`                                                                          | Fixed at `1`                                                                             |
| `presence_penalty` / `frequency_penalty` | Fixed at `0`                                   | Fixed at `0`                                                                          | Fixed at `0`                                                                             |

<Note>
  "Fixed" means the parameter cannot be modified: passing any other value returns an error, so do not pass it explicitly.
</Note>

### `thinking`

`thinking` is a K2.x-only request parameter:

* `kimi-k2.6`: supports `{"type": "enabled"}` (default), `{"type": "disabled"}`, and `{"type": "enabled", "keep": "all"}`.
* `kimi-k2.7-code`: thinking is on by default and only `{"type": "enabled", "keep": "all"}` is accepted; any other configuration returns an error. When switching from `kimi-k2.6`, you must pass back the historical `reasoning_content` in `messages` as required by Preserved Thinking.

See [Thinking Mode](/docs/guide/use-thinking-models).

### `reasoning_effort`

K3 always reasons with Preserved Thinking enabled. Configure its reasoning effort with the top-level `reasoning_effort` request field, which supports `"low"`, `"high"`, and `"max"` (default `"max"`). See [Reasoning Effort](/docs/guide/use-reasoning-effort).

<Warning>
  Switching levels invalidates prefix-cache hits. Decide on the `effort` level before the conversation starts and avoid switching it mid-session.
</Warning>

### `tool_choice`

`kimi-k3` supports `auto` / `none` / `required`. `kimi-k2.6` and `kimi-k2.7-code` do not support `required` and return an error if it is passed. See [Tool Choice](/docs/guide/use-tool-choice).

### `temperature`

* `kimi-k2.6`: fixed at `1.0` in thinking mode and `0.6` in non-thinking mode; other values return an error.
* `kimi-k2.7-code`: fixed at `1.0`; other values return an error.
* `kimi-k3`: fixed at `1.0`; other values return an error.

Do not pass `temperature` explicitly when calling these models.

`kimi-k2.7-code-highspeed` is the same model as `kimi-k2.7-code` with identical parameter constraints; only the output speed differs.

### FAQ

**Switching from `kimi-k2.6` to `kimi-k3` — do I need to change my code?**

Replace `model` with `kimi-k3` and remove the K2.x `thinking` configuration. To set the reasoning effort explicitly, use top-level `reasoning_effort`. In multi-turn conversations and tool calls, pass the complete assistant message returned by the API back to `messages` as-is, including any `reasoning_content`.

**Switching from `kimi-k2.7-code` to `kimi-k3` — do I need to change my code?**

Replace `model` and continue passing complete assistant messages back as-is. To set the reasoning effort explicitly, use top-level `reasoning_effort`.

**My code uses OpenAI's `reasoning_effort` — do I need to change it for `kimi-k3`?**

No. K3 supports top-level `reasoning_effort` with `"low"`, `"high"`, and `"max"` as accepted values and `"max"` as the default.

**Can I use `tool_choice: "required"` on `kimi-k2.6` or `kimi-k2.7-code`?**

No. These models do not support `required` and return an error if it is passed; only `kimi-k3` supports it.

## Kimi K2.7 Code series — thinking Parameter

The `kimi-k2.7-code` series includes `kimi-k2.7-code` and its high-speed variant `kimi-k2.7-code-highspeed`; the two are the same model with identical parameter constraints (including the table above and the `thinking` behavior) and differ only in output speed (referred to collectively as `kimi-k2.7-code` below).

`kimi-k2.7-code` is code-focused, and all parameter constraints except `thinking` are identical to `kimi-k2.6`. Unlike `kimi-k2.6`, its **thinking is always on and cannot be disabled** (passing `{"type": "disabled"}` errors), and **Preserved Thinking is always on** (`thinking.keep` is treated as `"all"` whether omitted or set to `"all"`; any other invalid value errors). So you do not need to pass the `thinking` parameter — just switch the `model`, and the model always emits `reasoning_content`. For details, see [Using Thinking Mode](/docs/guide/use-thinking-models).

## Kimi K2.6 — thinking Parameter

Kimi K2.6 supports the `thinking` parameter to control whether deep thinking is enabled. Accepts `{"type": "enabled"}` or `{"type": "disabled"}`.

Since the OpenAI SDK doesn't have a native `thinking` parameter, use `extra_body`:

<CodeGroup>
  ```python Python theme={null}
  completion = client.chat.completions.create(
      model="kimi-k2.6",
      messages=[
          {"role": "user", "content": "Hello"}
      ],
      extra_body={
          "thinking": {"type": "disabled"}
      },
      max_tokens=1024*32,
  )
  ```

  ```bash cURL theme={null}
  curl https://api.moonshot.ai/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $MOONSHOT_API_KEY" \
    -d '{
      "model": "kimi-k2.6",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "thinking": {"type": "disabled"}
    }'
  ```
</CodeGroup>
