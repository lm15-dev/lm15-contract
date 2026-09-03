> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Best Practices for Benchmarking

> Run reproducible Kimi model benchmarks with recommended parameters, sample counts, streaming requests, and retry strategies.

Benchmarking is an **engineering task** that needs stability and reproducibility. You'll be calling the model thousands of times; even tiny drifts in system setup or network latency can compromise result accuracy. Here's what we've learned to keep things reproducible and trustworthy.

**Quick notes**

* For any **unlisted** or **closed-source** benchmark:  set`temperature = 1.0`, `stream = true`, `top_p = 0.95`
* **Reasoning benchmarks**: `max_tokens = 128k`, and run at least **500–1000 samples** to get low variance (e.g. `AIME 2025`: 32 runs -> 30 × 32 = 960 questions)
* **Coding benchmarks**: `max_tokens = 256k`
* **Agentic task benchmarks:**
  * For multi-hop search: `max_tokens = 256k` + context management
  * Others: `max_tokens ≥ 16k–64k`

## K2.6 Models Benchmark Recommended Settings

<div style={{ overflowX: 'auto' }}>
  <table style={{ minWidth: '900px' }}>
    <thead>
      <tr>
        <th style={{ whiteSpace: 'nowrap' }}>Benchmark Category</th>
        <th style={{ whiteSpace: 'nowrap' }}>Benchmark</th>
        <th style={{ whiteSpace: 'nowrap' }}>Temperature</th>
        <th style={{ whiteSpace: 'nowrap' }}>Recommended max tokens</th>
        <th style={{ whiteSpace: 'nowrap' }}>Recommended runs</th>
        <th style={{ whiteSpace: 'nowrap' }}>Top-p</th>
        <th style={{ whiteSpace: 'nowrap' }}>Others (e.g. test log)</th>
      </tr>
    </thead>

    <tbody>
      <tr>
        <td rowSpan="7">Multi-modal</td>
        <td>MMMU-Pro</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>3</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>MMMU-Pro w/ python</td>
        <td>1.0</td>
        <td>per step tokens = 64k;<br />total max tokens = 256k</td>
        <td>3</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 50<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>CharXiv (RQ)</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>3</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>CharXiv (RQ) w/ python</td>
        <td>1.0</td>
        <td>per step tokens = 64k;<br />total max tokens = 256k</td>
        <td>3</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 50<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>MathVision</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>3</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>MathVision w/ python</td>
        <td>1.0</td>
        <td>per step tokens = 64k;<br />total max tokens = 256k</td>
        <td>3</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 50<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>V\* w/ python</td>
        <td>1.0</td>
        <td>per step tokens = 64k;<br />total max tokens = 256k</td>
        <td>3</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 50<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td rowSpan="8">Agent</td>
        <td>HLE-Full w/ tools</td>
        <td>1.0</td>
        <td>per step tokens = 48k;<br />total max tokens = 256k</td>
        <td>1</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>BrowseComp</td>
        <td>1.0</td>
        <td>per step tokens = 48k;<br />total max tokens = 256k</td>
        <td>1</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>DeepSearchQA</td>
        <td>1.0</td>
        <td>per step tokens = 48k;<br />total max tokens = 256k</td>
        <td>1</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>WideSearch</td>
        <td>1.0</td>
        <td>per step tokens = 48k;<br />total max tokens = 256k</td>
        <td>4</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>Toolathlon</td>
        <td>1.0</td>
        <td>per step tokens = 48k;<br />total max tokens = 256k</td>
        <td>4</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>MCPMark</td>
        <td>1.0</td>
        <td>per step tokens = 48k;<br />total max tokens = 256k</td>
        <td>4</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>Claw Eval</td>
        <td>1.0</td>
        <td>per step tokens = 48k;<br />total max tokens = 256k</td>
        <td>4</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>APEX-Agents</td>
        <td>1.0</td>
        <td>per step tokens = 48k;<br />total max tokens = 256k</td>
        <td>4</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td rowSpan="7">Coding</td>
        <td>Terminal-Bench 2.0 (Terminus-2)</td>
        <td>1.0</td>
        <td>max tokens = 256k</td>
        <td>3</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>SWE-Bench Pro</td>
        <td>1.0</td>
        <td>per step tokens = 32k;<br />total max tokens = 256k</td>
        <td>5</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>SWE-Bench Multilingual</td>
        <td>1.0</td>
        <td>per step tokens = 32k;<br />total max tokens = 256k</td>
        <td>5</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>SWE-Bench Verified</td>
        <td>1.0</td>
        <td>per step tokens = 32k;<br />total max tokens = 256k</td>
        <td>5</td>
        <td>top\_p=0.95</td>
        <td>Recommended max steps = 300<br />thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>SciCode</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>4</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>OJBench (python)</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>8</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>LiveCodeBench (v6)</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>1</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td rowSpan="3">Math</td>
        <td>AIME 2026</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>32</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>HMMT 2026 (Feb)</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>32</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>IMO-AnswerBench</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>4</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td rowSpan="2">Knowledge</td>
        <td>HLE-Full</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>1</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>

      <tr>
        <td>GPQA-Diamond</td>
        <td>1.0</td>
        <td>max tokens = 96k</td>
        <td>8</td>
        <td>top\_p=0.95</td>
        <td>thinking={`{"type": "enabled"}`}</td>
      </tr>
    </tbody>
  </table>
</div>

## API Recommendations & Notes

* **Use the official API:** some 3rd-party endpoints show noticeable accuracy drift.
* Use the recommended models for testing
  * For K2.6: use **`kimi-k2.6`** for testing
* **Must set:** `stream = true`
  * Non-streaming mode can lead to random mid-connection interruptions that are hard to control.
* **Current API default settings:**
  * Kimi K2.6:
    * default max\_tokens = 32768
    * default thinking = `{"type": "enabled", "keep": null}`
    * default temperature = 1.0
    * default top\_p = 0.95
    * default n = 1
    * default presence\_penalty = 0.0
    * default frequency\_penalty = 0.0
* **Timeouts:**
  * With `stream = false`, `api.moonshot.ai` timeout = **2 hours**, but some ISPs may terminate earlier.
  * So again we recommend you to set `stream = true`
* **Concurrency:**
  * Keep concurrency low to avoid rate limiting
* **Retry logic** is not optional:
  * handle overloaded
  * handle unexpected finish reason due to random server issues
  * handle errors due to complicated network issues

## FAQ

**Q1. Is the temperature setting consistent across models?**

**A.** No. Different model families use different recommended temperatures:

* k2.6 model: temperature = 1.0

**Q2. Why use stream = true?**

**A.** Long outputs can take minutes. Idle TCP connections may be terminated by firewalls, load balancers, or NAT gateways. **Streaming keeps the connection alive** and significantly improves reliability. In production, requests with stream = false fail far more often than with stream = true.

**Q3. How much concurrency should I use?**

**A.** Your API account has specific rate limits (see [Recharge and Rate Limits](/docs/pricing/limits)). Start low. If you hit **HTTP 429** (rate limit), your concurrency is too high. **Accuracy > speed,** so tune concurrency to stay within limits.

**Q5. Why should I add retry?**

**A.** Even with streaming, requests can fail due to transient network issues. **Retry** on temporary faults (network jitter, server overload, rate limiting) to avoid avoidable failures.

**Q6. Why should multi-turn or multi-step tasks include full context and reasoning?**

**A.** The model needs full context to stay logically consistent. Without previous reasoning steps, later turns can go off track or produce incomplete answers.

## Contact Us

Hit any issues? Drop us an email at [**api-service@moonshot.ai**](mailto:api-service@moonshot.ai) with your logs. We'll take a look!
