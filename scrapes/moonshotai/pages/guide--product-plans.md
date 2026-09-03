> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Compare with Other Kimi Products

> The Kimi API Open Platform uses pay-as-you-go billing with no subscription plan. It is different from products such as Kimi Membership and Kimi Code — please distinguish between them.

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

<DocTable
  columns={[
{ title: "Product", width: "18%" },
{ title: "Overview", width: "42%" },
{ title: "Billing", width: "40%" },
]}
  rows={[
[
  "Kimi API Open Platform (platform.kimi.ai)",
  "An easy-to-use, stable, and cost-effective LLM API service for developers and enterprises, helping AI applications move quickly from development to deployment and scale.",
  <ul>
    <li>Option 1: pay-as-you-go (create an API key after signing up). See the <a href="/docs/pricing/chat">Pricing</a> page for billing details.</li>
    <li>Option 2: enterprise plans (submit <a href="https://platform.kimi.ai/contact-sales">this form</a> to contact sales).</li>
  </ul>,
],
[
  "Kimi Business",
  <span>An intelligent office solution built for enterprise teams, suitable for small and medium-sized businesses with team collaboration needs. See <a href="https://www.kimi.ai/membership/pricing">this page</a> for details.</span>,
  <span>Annual subscription. Seat requirements and pricing are subject to <a href="https://www.kimi.ai/membership/pricing">this page</a>.</span>,
],
[
  "Kimi Membership",
  <span>Kimi offers four membership subscription tiers, covering personal daily use through heavy professional use. See <a href="https://www.kimi.ai/membership/pricing">this page</a> for details. Note: Kimi Membership currently includes <a href="https://www.kimi.com/code/docs/en/">Kimi Code</a> benefits; the Kimi Code API is independent from the API service on this platform.</span>,
  <span>Monthly or annual subscription. Pricing is subject to <a href="https://www.kimi.ai/membership/pricing">this page</a>.</span>,
],
]}
/>
