> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# BatchJob Pricing

> Review Kimi BatchJob pricing for input, output, and cache-hit tokens, along with billing notes.

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

Batch API inference costs are **60%** of the standard model price, ideal for large-scale tasks with low real-time requirements.

<DocTable
  columns={[
{ title: "Model", width: "20%" },
{ title: "Unit", width: "14%" },
{ title: "Input Price (Cache Hit)", width: "20%" },
{ title: "Input Price (Cache Miss)", width: "20%" },
{ title: "Output Price", width: "13%" },
{ title: "Context Window", width: "13%" },
]}
  rows={[
["kimi-k2.7-code (Batch)", "1M tokens", "$0.114", "$0.57", "$2.40", "262,144 tokens"],
["kimi-k2.6 (Batch)", "1M tokens", "$0.10", "$0.57", "$2.40", "262,144 tokens"],
]}
/>

Here, 1M = 1,000,000. The prices in the table represent the cost per 1M tokens consumed.

## Notes

* Batch API supports `kimi-k2.7-code` and `kimi-k2.6` models
* Batch API is not subject to real-time concurrency limits, ideal for bulk tasks
* Tasks must complete within the specified `completion_window`, otherwise they expire
* See the [Batch API Guide](/docs/guide/use-batch-api) for detailed usage instructions
