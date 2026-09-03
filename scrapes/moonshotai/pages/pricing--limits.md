> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Recharge and Rate Limiting

> Review Kimi Open Platform recharge requirements, account tiers, RPM, TPM, and TPD limits, and options for requesting higher capacity.

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

To ensure fair distribution of resources and prevent malicious attacks, we currently apply rate limits based on the cumulative recharge amount of each account. The specific limits are shown in the table below.

* To prevent abuse, you need to recharge at least \$1 to start using, and when your cumulative recharge reaches \$5, you will receive a \$5 voucher.

<DocTable
  columns={[
{ title: "User Level", width: "14%" },
{ title: "Cumulative Recharge Amount", width: "18%" },
{ title: "Concurrency", width: "12%" },
{ title: "RPM", width: "12%" },
{ title: "TPM", width: "22%" },
{ title: "TPD", width: "22%" },
]}
  rows={[
["Tier0", <>{"$"}1</>, "1", "3", "500,000", "1,500,000"],
["Tier1", <>{"$"}10</>, "15", "100", "2,000,000", "Unlimited"],
["Tier2", <>{"$"}20</>, "40", "100", "3,000,000", "Unlimited"],
["Tier3", <>{"$"}100</>, "50", "200", "3,000,000", "Unlimited"],
["Tier4", <>{"$"}1,000</>, "60", "200", "4,000,000", "Unlimited"],
["Tier5", <>{"$"}3,000</>, "100", "300", "5,000,000", "Unlimited"],
]}
/>

## Explanation of Rate Limits Concepts

* Concurrency: The maximum number of requests from you that we can process at the same time.
* RPM: Requests per minute, which means the maximum number of requests you can send to us in one minute.
* TPM: Tokens per minute, which means the maximum number of tokens you can interact with us in one minute.
* TPD: Tokens per day, which means the maximum number of tokens you can interact with us in one day.

For more details, please refer to the [Rate Limits](/docs/introduction#rate-limits) section.

## Why Do We Implement Rate Limits?

Rate limits are a common practice for API interfaces, and there are several reasons for it:

* They help prevent abuse or misuse of the API. For example, malicious actors might try to overwhelm the API with a large number of requests, attempting to overload it or cause service disruptions. By setting rate limits, we can guard against such behavior.
* Rate limits ensure fair access to the API for everyone. If one person or organization sends too many requests, it could slow down the API for everyone else. By limiting the number of requests a single user can send, we ensure that as many people as possible can use the API without experiencing slowdowns.
* Rate limits help us manage the overall load on our cluster. A sudden surge in requests to the API could put pressure on the servers and lead to performance issues. By setting rate limits, we can maintain a smooth and consistent experience for all users.

## Special Notes

* We will do our best to ensure normal usage for users, but when the cluster load reaches its capacity limit, we may take temporary measures to adjust the rate limits.
* Vouchers do not count towards the cumulative recharge total.
* When the system detects abnormal activity on an account, a risk-control rate-limiting policy is triggered. Once triggered, the restriction cannot be lifted.
