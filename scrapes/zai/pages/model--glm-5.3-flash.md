> ## Documentation Index
> Fetch the complete documentation index at: https://docs.z.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# GLM-5.3-Flash

<Tip>
  GLM-5.3-Flash is now fully available on the [GLM Coding Plan](https://z.ai/subscribe). With native multimodal capabilities and 3× the quota, it delivers a smoother and more cost-effective coding experience.
</Tip>

## Model Overview

GLM-5.3-Flash is the first native multimodal model in the GLM-5 series, delivering stronger intelligence than GLM-5.2 at an exceptionally low cost.

* **Highly Efficient Hybrid Architecture**

GLM-5.3-Flash has 320B total parameters with 18B activated. As the first open-source frontier model to combine sparse and linear attention, it significantly cuts computation and serving costs while preserving long-context quality — reducing attention computation and KV cache by 3.01× and 4.44× versus GLM-5.3.

* **Native Multimodal Visual Coding**

Visual capabilities are built into the coding loop: the model observes interfaces, rendered results, and interaction feedback to continuously test and improve its work. It coordinates tasks across code, browsers, and GUIs — from frontend and game development to Blender 3D scenes and real-world operation via BUA and CUA.

* **A Professional Work Partner Beyond Coding**

Beyond coding, GLM-5.3-Flash supports professional workflows such as Office tasks, financial research, and document processing. It autonomously breaks down goals, invokes tools, and reviews outputs — from research and analysis to finished PPTX, PDF, DOCX, and XLSX deliverables.

[↗ blog](https://z.ai/blog/glm-5.3-flash)

<CardGroup cols={4}>
  <Card title="Input Modality" icon="arrow-down-right" color="#ffffff">
    Video / Image / Text / File
  </Card>

  <Card title="Output Modality" icon="arrow-down-left" color="#ffffff">
    Text
  </Card>

  <Card title="Context Length" icon="arrow-down-arrow-up" color="#ffffff">
    1M
  </Card>

  <Card title="Maximum Output Tokens" icon="maximize" color="#ffffff">
    128K
  </Card>
</CardGroup>

## How to Use

#### **Model API**

* **Model Code**：`glm-5.3-flash`
* **API Documentation**：[Chat Completion API](https://docs.z.ai/api-reference/introduction)
* **Parameter Settings**：Text parameters are consistent with GLM-5.3, with support for a 1M-token context window.
* **Image Parameters**：Add a content block with `type: image_url` to` messages[].content[]`, and pass the image URL (recommended) or a Base64 Data URL through `image_url.url`. Multiple images can be added by including multiple `image_url` content blocks.
* **Recommended Settings**： `temperature: 1`, `top_p: 0.95`, and `reasoning_effort: max`. `thinking.type` only supports `enabled`; we recommend setting `thinking.clear_thinking: false`. For streaming requests, we recommend enabling both stream: true and `tool_stream: true`.

#### **GLM Coding Plan**

* Now fully available, GLM-5.3-Flash can be used with your preferred tools, with 3× the available quota compared with GLM-5.3.\\
* The new GLM Coding Plan adopts a points-based quota system with transparent usage limits. Model calls made during off-peak hours, including all day on weekends, consume only 50% of the standard points.\
  Subscribe now: [Personal Plan](https://z.ai/subscribe?plantype=individual)、[Team Plan](https://z.ai/subscribe?plantype=team)

## Capabilities

* [Thinking Mode](https://docs.z.ai/guides/capabilities/thinking-mode): Provides multiple thinking modes to address different task requirements. `thinking.type` only supports `enabled`; thinking cannot be disabled.
* [Streaming Output](https://docs.z.ai/guides/capabilities/stream-tool): Supports real-time streaming responses for an enhanced user interaction experience.
* [Function Calling](https://docs.z.ai/guides/capabilities/function-calling): Provides powerful tool-calling capabilities and supports integration with a wide range of external tools.
* [Context Caching](https://docs.z.ai/guides/capabilities/cache): Uses an intelligent caching mechanism to optimize long-conversation performance.
* [Structured Output](https://docs.z.ai/guides/capabilities/struct-output): Supports structured output formats such as JSON for seamless system integration.
* **Visual Understanding**: Native multimodal input supporting images, videos, and files.

## Best Practices

<AccordionGroup>
  <Accordion title="Vision-Driven UI Coding: From Reference Assets to a Complete Application">
    GLM-5.3-Flash can directly transform screenshots, multiple page images, website URLs, or screen recordings into polished, functional applications. It goes beyond reproducing colors and layouts by understanding page relationships, shared components, design systems, interaction states, and animation logic, enabling an end-to-end workflow from visual analysis to a complete frontend project.

    **Recommended Approach**:
    Provide a set of page screenshots from the same product, or a website with complex animations, and have the model create a high-fidelity reproduction:

    > Based on the page screenshots I provide, fully recreate this product using Next.js and TypeScript. First analyze the design system, page relationships, shared components, navigation structure, interaction states, and animation logic, then build a fully functional project. After implementation, launch the project and compare screenshots of each page against the reference images. Continuously refine differences in layout, typography, spacing, colors, image cropping, and interactions. Finally, explain which pages have been covered, how to run the project, and any remaining discrepancies.
  </Accordion>

  <Accordion title="Office Deliverables: From Content Organization to Visual Validation">
    GLM-5.3-Flash's Office capabilities go beyond content generation to simultaneously handle information structure, visual styling, charts, image cropping, and page layout. Whether creating PPTX, PDF, DOCX, or XLSX files from scratch or reproducing existing files and reference images, it can proactively identify issues such as overflow, misalignment, overlapping elements, and inconsistent styling through rendering and visual inspection.

    **Recommended Approach**:
    Select a real presentation or reporting task, clearly specify the audience, page count, content structure, and visual style, and have the model deliver a ready-to-use file:

    > Using the materials in the current directory, create a 15-page business presentation for management. First extract the key conclusions and narrative structure, then create editable charts, page layouts, image selections, and speaker notes. Do not fabricate any business data; cite the source for all referenced information. After completion, render and inspect each page, fixing text overflow, image cropping, element overlap, alignment issues, and visual inconsistencies. Finally, deliver the PPTX and PDF, and explain what has been verified and what risks remain uncovered.
  </Accordion>

  <Accordion title="Financial Professional Workflows: From Research Traceability to Models and Reports">
    GLM-5.3-Flash covers the complete workflow from financial research and analysis to valuation modeling and report generation. It can integrate information from multiple sources, retain the supporting evidence for key conclusions, distinguish disclosed facts from analytical assumptions and derived results, and translate research insights into auditable financial models and formal reports.

    **Recommended Approach**:
    Select a listed company that has just released its latest financial results, and provide its announcements, financial statements, and an existing model:

    > Based on the company's latest financial statements, announcements, and verifiable public information, conduct a comprehensive earnings analysis. Break down revenue, profit, cash flow, business segments, and key operating metrics, clearly distinguishing between company disclosures, analytical assumptions, and your own conclusions. Update the earnings forecast and valuation model, and verify the consistency of the three financial statements, formula references, and accounting definitions. Finally, deliver a PDF research report with source citations and an editable, formula-driven Excel model, and list the key risks and unverified information.
  </Accordion>

  <Accordion title="Video Understanding and Editing: From Long-Form Footage to Publish-Ready Videos">
    In an Agent environment, GLM-5.3-Flash can simultaneously understand visuals, speech, subtitles, relationships between people, and timelines, reorganizing long-form videos or multiple pieces of footage into coherent content. It can also leverage name tags, on-screen appearances, and contextual cues to continuously identify different speakers, handling tasks such as speaker attribution, story structuring, and visual matching that are difficult to accomplish with ASR alone, significantly improving the efficiency of video editing Agents.

    **Recommended Approach**:
    Provide a set of interview, event, or product footage and have the model complete the editing, subtitles, and final quality checks:

    > Edit the videos in the footage directory into a 90-second product launch recap. First create a media inventory, identify people, events, key statements, and usable shots, then design the pacing of the opening, main section, and ending. Distinguish between speakers and generate accurate subtitles, ensuring that the visuals correspond to the spoken content. After completing the editing, music, transitions, and basic color grading, check for typos, speaker attribution, audio-video synchronization, black frames, and duplicate shots. Finally, output the MP4, SRT, and editing notes.
  </Accordion>

  <Accordion title="3D Scene Creation: From a Single Description to a Complete Blender Project">
    GLM-5.3-Flash can transform spatial requirements, visual styles, and functional constraints into editable Blender projects, and continuously develop them from blockout to assets, materials, lighting, camera setup, and final rendering. More importantly, it can repeatedly render from fixed camera positions, inspect the actual visuals, identify issues, and iterate, rather than merely generating a modeling script.

    **Recommended Approach**:
    Provide a complete scene task that specifies spatial planning, design style, and delivery requirements:

    > Create a complete, editable Blender scene in the current directory depicting a restaurant and bar located on a high floor in a city. First define the artistic direction, spatial layout, asset list, and fixed camera shots, then build the blockout and render previews as early as possible. Perform at least four rounds of "build → fixed-camera render → inspect → refine → re-render," focusing on spatial scale, circulation, materials, lighting, mesh intersections, and camera composition. Finally, reopen the project from a clean environment and render the main shot. Deliver the .blend file, final images, and reproduction instructions.
  </Accordion>

  <Accordion title="Game Development: From Gameplay Rules to a Fully Playable Loop">
    GLM-5.3-Flash can extract visual language, core mechanics, state machines, and win/loss conditions from reference images and gameplay descriptions, efficiently adapt them to professional cross-platform game engines such as Godot, and implement them as genuinely playable game prototypes. Rather than simply generating scenes, it is better suited to testing whether movement, collisions, AI, scoring, levels, results, and save systems form a complete gameplay loop.

    **Recommended Approach**:
    Use your own or properly licensed assets and choose a focused, time-bounded Godot game task:

    > Using the properly licensed assets in the current directory, develop a playable cooperative cooking game prototype with Godot 4. First review the gameplay specifications, asset mappings, and reference screenshots, then implement character movement, item pickup, food preparation, serving, scoring, countdown timers, and the results flow according to milestones. Run tests after each stage and compare the result against the reference images using the same map and camera positions. Finally, ensure that a complete game session can run from start to finish, and deliver the Web build, test logs, runtime instructions, and a list of incomplete items.
  </Accordion>

  <Accordion title="Computer Use Closed Loop: Operating, Testing, and Refining in Real Interfaces">
    GLM-5.3-Flash can visually understand software interfaces and perform clicks, text input, decision-making, and continuous actions even when structured APIs are unavailable. It can test games and websites, observe existing applications, reproduce key functionality, and then operate the reproduced version to identify discrepancies, forming a closed loop of "observe → implement → use → refine."

    **Recommended Approach**:
    Select a local application or web product, enable `/goal` mode, and have the model reproduce it while using it:

    > `/goal` Use Computer Use to inspect the currently open application, identify its page structure, core functionality, primary user flows, and interaction feedback, and recreate a functional version in the current directory. After completion, operate both the original application and the recreated version, comparing their layouts, functionality, state changes, and interaction paths. Record the differences and continuously improve the implementation. Finally, complete all major workflows except login, and provide the verification results, remaining discrepancies, and instructions for running the application.
  </Accordion>

  <Accordion title="CAD Visual Reproduction: From Design Blueprints to Editable 3D Models">
    GLM-5.3-Flash can understand the main structure, hole positions, fillets, chamfers, surfaces, and assembly relationships from part photographs, sketches, or CAD blueprints, and generate parametric 3D models using code-based tools such as build123d. After generating the model, it can render multiple views, continuously compare them against the reference images, refine discrepancies, and deliver editable project assets for further development.

    **Recommended Approach**:
    Select a mechanical part with a clear structure and multiple recognizable features, and provide dimensional or proportional references:

    > Based on the part blueprint and multi-angle reference images I provide, use build123d to write parametric code that recreates the part. First identify the main structure, key dimensions, hole positions, fillets, chamfers, and symmetry relationships, and list assumptions for any dimensions that cannot be determined with certainty. After completion, render the model from angles matching the reference images and compare the proportions and structural differences item by item, continuously refining the model. Finally, deliver the Python source code, STEP file, STL file, dimensional specifications, and an interactive viewing page.
  </Accordion>
</AccordionGroup>

## Key Advancements

GLM-5.3-Flash incorporates several architectural improvements over GLM-5. For the first time, we introduce a hybrid architecture combining sparse and linear attention, sharply reducing long-context serving costs while preserving precise long-context capabilities. It also adopts Manifold-Constrained Hyper-Connections (mHC) to further improve scaling efficiency. Combined with our latest 30T-token multimodal pre-training corpus, these changes let GLM-5.3-Flash produce more intelligence with less compute.

Before release, we tested GLM-5.3-Flash anonymously as ox-alpha on OpenCode and OpenRouter to gather user feedback. It quickly became the most popular model of the week — with all of this traffic served on Chinese AI chips.

#### Competitive Performance at Flash Cost

GLM-5.3-Flash pushes the Pareto frontier of the Artificial Analysis Intelligence Index v4.1.1, scoring 57 at just \$0.045 per task (discounted) — a level of intelligence previously only available at roughly 10× the cost. This makes it a highly competitive default choice for a broad range of workloads.

![](https://cloud-document-converter.oss-cn-beijing.aliyuncs.com/feishu2md/20260826/1787756367779-b9g6ji.png)

Across six coding and agentic benchmarks, GLM-5.3-Flash consistently outperforms GLM-5.2, often by a wide margin — 63.4 vs. 46.2 on DeepSWE v1.1 and 48.8 vs. 26.2 on AutomationBench — while approaching Claude Opus 4.8 overall.This holds on our in-house coding evaluation as well: on Z.ai Code Bench v1.0 (run on Claude Code 2.1.207), GLM-5.3-Flash clearly outperforms GLM-5.2 at every effort level, and at max effort nearly matches Claude Opus 4.8 (29.0 vs. 29.5).

![](https://cloud-document-converter.oss-cn-beijing.aliyuncs.com/feishu2md/20260826/1787756174815-hakryv.png)

#### Architecture for Extreme Efficiency

![](https://cloud-document-converter.oss-cn-beijing.aliyuncs.com/feishu2md/20260826/1787756367780-5fet8o.png)

Compared with the GLM-4.5 series, GLM-5.3-Flash is specifically designed for ultra-low-cost inference. Despite a similar total parameter count (320B vs. 355B), it nearly halves both the activated parameter count (18B vs. 32B) and the number of layers (45 vs. 92).

To minimize attention costs in long-context scenarios, we use a hybrid architecture combining linear and sparse attention. Linear attention captures local dependencies through state modeling, while sparse attention retrieves relevant global context through a lightweight indexer. To further reduce the latency and memory overhead of the indexer at a 1M-token context length, we introduce IndexPool, which compresses four indexer key vectors into one through weighted pooling.

To illustrate the efficiency of our architecture, we compare the per-token compute and KV cache size of GLM-5.3-Flash against GLM-5.3 and two recent open models DeepSeek-V4-Flash and Kimi-K3. For a fair comparison among different scales, we calculate the attention compute per head per layer and average KV cache size per layer (BF16). Compared with GLM-5.3, GLM-5.3-Flash reduces the attention compute and KV cache size by factors of 3.0x and 4.4x. GLM-5.3-Flash has the lowest attention compute among all models compared. The KV cache size is still slightly larger than Kimi-K3 and DeepSeek-V4-Flash, leaving further room for improvement.

The overall architecture improvements, combined with optimized pre-training corpus, enable GLM-5.3-Flash to produce more intelligence with less compute. In the table below we show the evaluation results of the base model of GLM-5.3-Flash, comparing with our previous base models and DeepSeek-V4-Flash-Base. The results show that GLM-5.3-Flash-Base outperforms GLM-4.5-Base overall and remains competitive with GLM-5-Base across most benchmarks.

#### Visual Intelligence in the Coding Loop

Visual coding is not just about processing images. It expands the boundary of what coding can reach. For tasks such as frontend development, game development, and 3D simulation, the final output is not code alone, but an interface, an interaction, or a world experienced by the user. Many failures only surface through rendering, interaction, or playtesting. CUA further extends coding beyond programmable systems into visible and interactive environments. Vision therefore needs to be natively integrated into the model, enabling it to decide when to observe and use visual feedback to guide subsequent actions.

We develop data synthesis pipelines for visual coding, with a focus on self-visual judgment and test-time improvement. The resulting trajectories require the model to interact with environments, inspect its own outputs, and refine them iteratively. For frontend coding, we also explored reinforcement learning with environment feedback and further strengthened GUI judgment through agent-based verification grounded in real user flows. This extends validation beyond functional correctness to the rendered and interactive product.

#### Beyond Coding -- Your Partner at Work

Coding capabilities provide an important foundation for intelligent knowledge work, while visual intelligence extends these capabilities to a broader range of professional tasks. A substantial portion of professional activities involves interpreting heterogeneous visual and structured information, including documents, spreadsheets, presentations, dashboards, interfaces, and meeting artifacts.

Visual intelligence extends the model’s capabilities beyond code-centric environments by enabling it to jointly reason over textual, visual, and structural context. Rather than requiring users to explicitly translate their working environment into textual instructions, the model can directly interpret the artifacts associated with a task and identify relevant information. It can also assess its own outputs against the visual context and intended outcome, enabling more effective self-verification and refinement — including stronger judgments of presentation quality and aesthetics.

#### Serving at Scale on Chinese AI Chips

Over the past week, we have served GLM-5.3-Flash on a large-scale cluster of Chinese AI chips, supported by a high-bandwidth interconnect and a serving stack optimized for the underlying hardware.

To overcome the relatively limited compute and memory capacity of individual chips, we built a dedicated inference engine for this architecture on top of SGLang. Notably, this effort was accelerated by our GLM-5.3-powered infrastructure agent, which assisted engineers in developing and optimizing kernels, diagnosing performance bottlenecks, and improving the serving stack — creating a feedback loop in which the model helped optimize the system serving the model itself.

These chips are primarily constrained by memory capacity and bandwidth, especially when supporting context lengths of up to one million tokens. This calls for aggressive memory optimization, including compute-for-bandwidth and communication-for-bandwidth techniques tailored to the underlying architecture. Our stack combines intra-node tensor parallelism for Linear Attention and the LM head, ReplaySSM, W8A8 quantization, hybrid INT8/FP8/BF16 cache quantization, and Layer Split.

At cluster scale, our production-grade Encode–Prefill–Decode (EPD) disaggregated architecture separates multimodal encoding, prompt prefill, and token-by-token decoding into independently scheduled and scalable worker pools, enabling efficient and reliable serving across tens of thousands of domestically developed accelerators.

Compared with our initial baseline on the same hardware, we achieved a 3× improvement in end-to-end serving performance, reaching hardware efficiency and per-token cost comparable to mainstream NVIDIA GPUs. This demonstrates that Chinese chips can support frontier-model inference efficiently and economically at scale.

#### Conclusion

GLM-5.3-Flash shows that frontier intelligence does not have to come at frontier cost. This is not the result of any single trick, but of three layers working together: an architecture that delivers stronger capability from less compute, a richer multimodal pre-training corpus, and infrastructure co-designed with inference hardware. We are now scaling this recipe to larger models — GLM-5.3-Flash pushes the cost-performance frontier, and the lessons from building it are already shaping our next frontier model.
