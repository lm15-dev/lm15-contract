> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Flagship Model Kimi K3 Pricing

> Review Kimi K3 flagship model pricing for input, output, and cache-hit tokens, along with billing notes.

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

## Product Pricing

**Explanation: Prices exclude applicable taxes. Specific tax obligations are subject to local tax regulations and will be calculated at checkout based on your jurisdiction.**

<DocTable
  columns={[
{ title: "Model", width: "24%" },
{ title: "Unit", width: "12%" },
{ title: "Input Price (Cache Hit)", width: "16%" },
{ title: "Input Price (Cache Miss)", width: "16%" },
{ title: "Output Price", width: "14%" },
{ title: "Context Window", width: "18%" },
]}
  rows={[
["kimi-k3", "1M tokens", <>{"$"}0.30</>, <>{"$"}3.00</>, <>{"$"}15.00</>, "1,048,576 tokens"],
]}
/>

Here, 1M = 1,000,000. The prices in the table represent the cost per 1M tokens consumed.

## Model Description

<Warning>
  The web search (`web_search`) is currently being updated. We do not recommend using this functionality in the near term. This documentation is outdated; please follow subsequent content updates.
</Warning>

* Kimi K3 is Kimi's flagship model for long-horizon coding and end-to-end knowledge work, with a 1M-token context window and industry-leading intelligence. See [Introducing Kimi K3](/docs/guide/kimi-k3-quickstart).
* Always reasons and supports configuring its reasoning effort with the top-level `reasoning_effort` request field (`low` / `high` / `max`, default `max`). See [Reasoning Effort](/docs/guide/use-reasoning-effort).
* Supports [automatic context caching](/docs/guide/use-context-caching-feature-of-kimi-api), [ToolCalls](/docs/guide/use-kimi-api-to-complete-tool-calls), [JSON Mode](/docs/guide/use-json-mode-feature-of-kimi-api), [structured output (`response_format` / JSON Schema)](/docs/guide/response_format), [Partial Mode](/docs/guide/use-partial-mode-feature-of-kimi-api), [internet search](/docs/guide/use-web-search), and more
* New API capabilities in K3: [tool choice constraints (`tool_choice`)](/docs/guide/use-tool-choice) and [dynamically loaded tools](/docs/guide/use-dynamic-tool-loading) — see [Kimi K3 API Tool Calling Best Practices](/docs/guide/kimi-k3-tool-calling-best-practice) for combined usage
