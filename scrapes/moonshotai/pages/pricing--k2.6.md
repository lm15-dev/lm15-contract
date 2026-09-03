> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Kimi K2.6 Model Pricing

> Review Kimi K2.6 pricing for input, output, and cache-hit tokens, along with billing notes.

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
["kimi-k2.6", "1M tokens", <>{"$"}0.16</>, <>{"$"}0.95</>, <>{"$"}4.00</>, "262,144 tokens"],
]}
/>

Here, 1M = 1,000,000. The prices in the table represent the cost per 1M tokens consumed.

## Model Description

<Warning>
  The web search (`web_search`) is currently being updated. We do not recommend using this functionality in the near term. This documentation is outdated; please follow subsequent content updates.
</Warning>

* Kimi K2.6 is a general-purpose model with stable long-horizon coding, instruction-following, and self-correction capabilities. It supports text, image, and video input, thinking and non-thinking modes, and dialogue and Agent tasks.
* Context length 256k, supports long thinking and deep reasoning.
* Supports automatic context caching functionality, [ToolCalls](/docs/guide/use-kimi-api-to-complete-tool-calls), [JSON Mode](/docs/guide/use-json-mode-feature-of-kimi-api), [Partial Mode](/docs/guide/use-partial-mode-feature-of-kimi-api), and [internet search functionality](/docs/guide/use-web-search).
