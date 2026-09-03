> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Coding Model Kimi K2.7 Code Pricing

> Review Kimi K2.7 Code and high-speed model pricing for input, output, and cache-hit tokens, along with billing notes.

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
["kimi-k2.7-code", "1M tokens", <>{"$"}0.19</>, <>{"$"}0.95</>, <>{"$"}4.00</>, "262,144 tokens"],
["kimi-k2.7-code-highspeed", "1M tokens", <>{"$"}0.38</>, <>{"$"}1.90</>, <>{"$"}8.00</>, "262,144 tokens"],
]}
/>

Here, 1M = 1,000,000. The prices in the table represent the cost per 1M tokens consumed.

## Model Description

* Kimi K2.7 Code is a coding-focused model that completes programming tasks with higher success rates in long contexts. It supports text, image, and video input, thinking mode, dialogue, and agent tasks.
* Kimi K2.7 Code HighSpeed is the high-speed version of Kimi K2.7 Code, the same model as Kimi K2.7 Code, but with an output speed of approximately 180 Tokens/s and up to 260 Tokens/s in short context scenarios, delivering a more extreme coding experience.
* Context length 256k, supports long thinking and deep reasoning.
* Supports automatic context caching functionality, [ToolCalls](/docs/guide/use-kimi-api-to-complete-tool-calls), [JSON Mode](/docs/guide/use-json-mode-feature-of-kimi-api), [Partial Mode](/docs/guide/use-partial-mode-feature-of-kimi-api).
