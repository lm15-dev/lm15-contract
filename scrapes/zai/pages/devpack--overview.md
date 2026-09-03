> ## Documentation Index
> Fetch the complete documentation index at: https://docs.z.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Overview

The GLM Coding Plan is a subscription package designed specifically for AI-powered coding.

## Usage

The plan can be applied to coding tools such as Claude Code, Cline, and OpenCode, covering a wide range of development scenarios:

<AccordionGroup>
  <Accordion title="Natural Language Programming">
    Describe requirements in plain language to automatically generate plans, write code, debug issues, and ensure smooth execution.
  </Accordion>

  <Accordion title="Intelligent Code Completion">
    Get real-time, context-aware completion suggestions that reduce manual typing and significantly improve productivity.
  </Accordion>

  <Accordion title="Code Debugging & Repair">
    Input error messages or descriptions to automatically analyze your codebase, locate problems, and provide fixes.
  </Accordion>

  <Accordion title="Codebase Q&A">
    Ask questions about your team’s codebase anytime, maintain global understanding, and receive precise answers with external data integration.
  </Accordion>

  <Accordion title="Automated Task Handling">
    Automatically fix lint issues, resolve merge conflicts, and generate release notes—allowing developers to stay focused on core logic.
  </Accordion>
</AccordionGroup>

## Advantages

* **Access to high-intelligence Coding Model:** Upon release, the GLM series achieved SOTA performance among open-source models in reasoning, coding, and agent capabilities, delivering outstanding results in tool use and complex task execution.
* **Works with Multiple Tools:** Beyond Claude Code, it also supports Cline, OpenCode, and some <a href="https://docs.z.ai/devpack/tool/others#step-1-supported-tools">specific tools</a>, giving you flexibility across development workflows.
* **Generous Usage at a Fair Price:** Get higher call limits than standard plans. Starting at just 18 USD per month, with Pro and Max plans designed for high-frequency, complex projects.
* **Expanded Capabilities:** All plans support Vision Understanding, Web Search MCP， Web Reader MCP and Zread MCP helping you tackle a wider range of development tasks.

## Benefits

### Supported Models

* All plans support **GLM-5.3**, GLM-5.3-Flash.
* Requests for GLM-5.2/GLM-5.1 will be automatically routed to GLM-5.3, requests for GLM-4.7 will automatically be routed to GLM-5.3-Flash.

### Usage Instruction

<Warning>
  For information on Team Plan usage limits, please visit [Team Plan Benefits](/devpack/teamplan).
</Warning>

#### Usage Credit Allowance

Each plan is subject to both a 5-hour usage limit and a weekly usage limit.

| Plan Type | 5-Hour Credits | Weekly Credits |
| :-------: | :------------: | :------------: |
|    Lite   |      2,000     |     10,000     |
|    Pro    |     12,000     |     60,000     |
|    Max    |     28,000     |     140,000    |

**Credit Reset Rules**

* **5-hour credits**: Dynamically refreshed; credit quota resets 5 hours after consumption.
* **Weekly credits**: Activated upon subscription; resets every 7 days.

#### Credit Calculation

* Model credit usage = (Input tokens × Input multiplier + Cached Input tokens × Cached Input multiplier + Output tokens × Output multiplier) / 10,000
* MCP tool credit usage = Number of calls × Output multiplier

<Tip>
  You can view the number of tokens consumed under each pricing type and the number of tool calls on the [Charge Type](https://z.ai/manage-apikey/billing) page.
</Tip>

<table>
  <thead>
    <tr>
      <th style={{ textAlign: "left" }}>Product Type</th>
      <th style={{ textAlign: "left" }}>Product</th>
      <th style={{ textAlign: "left" }}>Input Multiplier</th>
      <th style={{ textAlign: "left" }}>Cached Input Multiplier</th>
      <th style={{ textAlign: "left" }}>Output Multiplier</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td rowSpan={2} style={{ textAlign: "left" }}>Model</td>
      <td className="!pl-3" style={{ textAlign: "left" }}>GLM-5.3</td>
      <td style={{ textAlign: "left" }}>6.9</td>
      <td style={{ textAlign: "left" }}>1.7</td>
      <td style={{ textAlign: "left" }}>24</td>
    </tr>

    <tr>
      <td className="!pl-3" style={{ textAlign: "left" }}>GLM-5.3-Flash\
      (Including MCP for visual understanding)</td>
      <td style={{ textAlign: "left" }}>2.3</td>
      <td style={{ textAlign: "left" }}>0.56</td>
      <td style={{ textAlign: "left" }}>8</td>
    </tr>

    <tr>
      <td rowSpan={3} style={{ textAlign: "left" }}>MCP Server</td>
      <td className="!pl-3" style={{ textAlign: "left" }}>Web Search</td>
      <td style={{ textAlign: "left" }}>—</td>
      <td style={{ textAlign: "left" }}>—</td>
      <td style={{ textAlign: "left" }}>1.2</td>
    </tr>

    <tr>
      <td className="!pl-3" style={{ textAlign: "left" }}>Web Reader</td>
      <td style={{ textAlign: "left" }}>—</td>
      <td style={{ textAlign: "left" }}>—</td>
      <td style={{ textAlign: "left" }}>1.2</td>
    </tr>

    <tr>
      <td className="!pl-3" style={{ textAlign: "left" }}>Zread</td>
      <td style={{ textAlign: "left" }}>—</td>
      <td style={{ textAlign: "left" }}>—</td>
      <td style={{ textAlign: "left" }}>1.2</td>
    </tr>
  </tbody>
</table>

**During off-peak hours, model usage is charged at 50% of the standard credit rate**.

<Info>
  **Peak hours**: Monday to Friday, 14:00–18:00 Singapore Standard Time (UTC+8).
</Info>

#### Estimated Token Allowance

Token usage varies depending on the cache hit rate, as shown below:

| Cache Hit Rate |     Model     | Lite <br />(M Tokens/week) | Pro <br />(M Tokens/week) | Max <br />(M Tokens/week) |
| :------------: | :-----------: | :------------------------: | :-----------------------: | :-----------------------: |
|       95%      |    GLM‑5.3    |            48–97           |          290–580          |         676–1,352         |
|       95%      | GLM‑5.3‑Flash |           146～292          |         877–1,755         |        2,047–4,095        |
|       96%      |    GLM‑5.3    |            50–99           |          297–595          |         694–1,387         |
|       96%      | GLM‑5.3‑Flash |           150–300          |         900–1,801         |        2,101–4,202        |
|       98%      |    GLM‑5.3    |           52–104           |          313–627          |         731–1,463         |
|       98%      | GLM‑5.3‑Flash |           158–317          |         950–1,900         |        2,217–4,433        |

**How the Range Is Calculated**

* Maximum token allowance: All usage occurs during off-peak hours and is charged at 0.5× the standard credit rate.
* Minimum token allowance: All usage occurs during peak hours and is charged at 1× the standard credit rate.

**By fully utilizing the off-peak discounts, you can save up to 92% compared with pay-as-you-go calls to the GLM-5.3 standard API**

### Exclusive MCP Access

<CardGroup cols={2}>
  <Card title="Vision Understanding" icon="eye" href="/devpack/mcp/vision-mcp-server" />

  <Card title="Web Search" icon="globe" href="/devpack/mcp/search-mcp-server" />

  <Card title="Web Reader" icon="book-open" href="/devpack/mcp/reader-mcp-server" />

  <Card title="Zread" icon="github" href="/devpack/mcp/zread-mcp-server" />
</CardGroup>

## Next Steps

<CardGroup cols={3}>
  <Card title="Quick Start" color="#ffffff" icon="rocket" href="/devpack/quick-start">
    Get up and running in minutes — from subscribing to the plan to using it in your coding tools.
  </Card>

  <Card title="Usage Policy" color="#ffffff" icon="shield-keyhole" href="/devpack/usage-policy">
    Learn about account usage rules, rate limits, refund policies, and other important guidelines.
  </Card>

  <Card title="FAQ" color="#ffffff" icon="comments-question" href="/devpack/faq">
    Find answers to common questions about subscriptions, promotions, and using the plan.
  </Card>
</CardGroup>
