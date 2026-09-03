> ## Documentation Index
> Fetch the complete documentation index at: https://docs.z.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Overview

<Info>
  Z.AI offers a variety of models and agents to meet the needs of different scenarios. Choosing the right model can help you complete tasks more efficiently.
</Info>

## Latest Models

<CardGroup cols={2}>
  <Card title="GLM-5.3" icon="book-open" href="/guides/llm/glm-5.3">
    **Flagship Model**

    * Open-source SOTA coding capabilities, emerging cybersecurity capabilities.
  </Card>

  <Card title="GLM-5.3-Flash" icon="eyes" href="/guides/vlm/glm-5.3-flash">
    **Native Multimodal Model**

    * Matching Claude Opus 4.8 in intelligence score at just 1/40 the price.
  </Card>
</CardGroup>

## Featured Models

The following are Z.ai’s core models, covering a comprehensive range of use cases, including text generation, multimodal understanding, OCR, speech recognition, speech synthesis, and vector retrieval.

| Model         | Strength                                                                                                                | Language          | Context | Resource                                                                                                  |
| :------------ | :---------------------------------------------------------------------------------------------------------------------- | :---------------- | :------ | :-------------------------------------------------------------------------------------------------------- |
| GLM-5.3-Flash | Delivering frontier intelligence at radically lower cost                                                                | English & Chinese | 1M      | [Guide](/guides/vlm/glm-5.3-flash)<br /><br />[API Reference](/api-reference/llm/chat-completion)         |
| GLM-5.3       | Claude Fable 5-level coding and agent capabilities <br /> Stronger in long-horizon, complex tasks                       | English & Chinese | 1M      | [Guide](/guides/llm/glm-5.3)<br /><br />[API Reference](/api-reference/llm/chat-completion)               |
| GLM-5.2       | Open-source SOTA coding, from generation to delivery                                                                    | English & Chinese | 1M      | [Guide](/guides/llm/glm-5.2)<br /><br />[API Reference](/api-reference/llm/chat-completion)               |
| GLM-OCR       | Document Parsing<br />Information Extraction                                                                            | Multiple          | /       | [Guide](/guides/vlm/glm-ocr)<br /><br />[API Reference](/api-reference/tools/layout-parsing)              |
| GLM-ASR-2512  | CER as low as 0.0717<br />- Support user-defined vocabularies<br />- Support multiple mainstream languages and dialects | English & Chinese | /       | [Guide](/guides/audio/glm-asr-2512)<br /><br />[API Reference](/api-reference/audio/audio-transcriptions) |

<Tip>
  If you need to get pricing information, please go directly to [Pricing](/guides/overview/pricing).
</Tip>

<AccordionGroup>
  <Accordion title="Other Models, Agents and Tools">
    To help you find the best fit for your use case, we've created a table outlining the core features and strengths of each model in the Z.AI family.

    ### Text Models

    Our model matrix includes text models with built-in reasoning capabilities, as well as vision-language models (VLMs) that extend the same reasoning power to multimodal understanding.

    | Model               | Strength                                                                                                                        | Language          | Context | Resource                                                                                                |
    | :------------------ | :------------------------------------------------------------------------------------------------------------------------------ | :---------------- | :------ | :------------------------------------------------------------------------------------------------------ |
    | GLM-5.1             | Coding proficiency aligned with Opus 4.6<br />Ability to work independently and consistently for up to 8 hours on a single task | English & Chinese | 200K    | [Guide](/guides/llm/glm-5.1)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-5               | Agentic Long-Term Planning and Execution<br />Backend refactoring and in-depth debugging                                        | English & Chinese | 200K    | [Guide](/guides/llm/glm-5)<br /><br />[API Reference](/api-reference/llm/chat-completion)               |
    | GLM-4.7             | SOTA Performance<br />Optimized Agentic Coding                                                                                  | English & Chinese | 200K    | [Guide](/guides/llm/glm-4.7)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-4.7-FlashX      | Optimized Agentic Coding<br />Lightweight & High-Speed                                                                          | English & Chinese | 200K    | [Guide](/guides/llm/glm-4.7)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-4.6             | Strong Coding<br />More Versatile                                                                                               | English & Chinese | 200K    | [Guide](/guides/llm/glm-4.6)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-4.5             | Strong Reasoning<br />More Versatile                                                                                            | English & Chinese | 128K    | [Guide](/guides/llm/glm-4.5)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-4.5-X           | Good Performance<br />Ultra-Fast Response                                                                                       | English & Chinese | 128K    | [Guide](/guides/llm/glm-4.5)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-4.5-Air         | Cost-Effective<br />High Performance                                                                                            | English & Chinese | 128K    | [Guide](/guides/llm/glm-4.5)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-4.5-AirX        | Lightweight<br />Ultra-Fast Response                                                                                            | English & Chinese | 128K    | [Guide](/guides/llm/glm-4.5)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-4-32B-0414-128K | High intelligence at <br />unmatched cost-efficiency                                                                            | English & Chinese | 128K    | [Guide](/guides/llm/glm-4-32b-0414-128k)<br /><br />[API Reference](/api-reference/llm/chat-completion) |
    | GLM-4.7-Flash       | Free, Lightweight                                                                                                               | English & Chinese | 200K    | [Guide](/guides/llm/glm-4.7)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |
    | GLM-4.5-Flash       | Free, Lightweight                                                                                                               | English & Chinese | 200K    | [Guide](/guides/llm/glm-4.5)<br /><br />[API Reference](/api-reference/llm/chat-completion)             |

    ### Vision Models

    Visual models process images or videos for recognition and analysis.

    | Model                      | Strength                                                       | Language          | Context | Resource                                                                                                                    |
    | :------------------------- | :------------------------------------------------------------- | :---------------- | :------ | :-------------------------------------------------------------------------------------------------------------------------- |
    | AutoGLM-Phone-Multilingual | Phone Agent<br />Automated Mobile Task Execution               | English & Chinese | /       | [Guide](/guides/vlm/autoglm-phone-multilingual)<br /><br />[API Reference](/api-reference/llm/chat-completion#vision-model) |
    | GLM-4.6V                   | Native Function Call Support<br />Thinking Mode Switch Support | English & Chinese | 128K    | [Guide](/guides/vlm/glm-4.6v)<br /><br />[API Reference](/api-reference/llm/chat-completion)                                |
    | GLM-4.6V-FlashX            | Lightweight & High-Speed                                       | English & Chinese | 128K    | [Guide](/guides/vlm/glm-4.6v)<br /><br />[API Reference](/api-reference/llm/chat-completion)                                |
    | GLM-4.5V                   | Multimodal<br />Flexible Reasoning                             | English & Chinese | 64K     | [Guide](/guides/vlm/glm-4.5v)<br /><br />[API Reference](/api-reference/llm/chat-completion)                                |
    | GLM-4.6V-Flash             | Free, Native Function Call Support                             | English & Chinese | 128K    | [Guide](/guides/vlm/glm-4.6v)<br /><br />[API Reference](/api-reference/llm/chat-completion)                                |

    ### Built-in Tools

    A suite of built-in tools designed to streamline workflows and boost productivity.

    | Tool       | Capability                                                                                                                |
    | :--------- | :------------------------------------------------------------------------------------------------------------------------ |
    | Web Search | Provide real-time, concise, direct answers<br />Accurately parse complex HTML and converts it into clean Markdown or JSON |

    ### Image Generation Models

    Image Generation Models learn from massive image data to automatically generate high-quality images from text.

    | Model     | Strength                                                                                                    | Language          | Resolution           | Resource                                                                                         |
    | :-------- | :---------------------------------------------------------------------------------------------------------- | :---------------- | :------------------- | :----------------------------------------------------------------------------------------------- |
    | GLM-Image | Stronger in complex instruction and knowledge-intensive scenarios<br />- Open-source SOTA in text rendering | English & Chinese | multiple resolutions | [Guide](/guides/image/glm-image)<br /><br />[API Reference](/api-reference/image/generate-image) |
    | CogView-4 | High-quality image generation<br />Rich in detail                                                           | English & Chinese | multiple resolutions | [Guide](/guides/image/cogview-4)<br /><br />[API Reference](/api-reference/image/generate-image) |

    ### Video Generation Models

    Video Generation Models turn text, images, or clips into dynamic video content, accelerating creativity for film, virtual avatars, animation, and marketing.

    | Model       | Strength                                                                              | Language          | Resolution           | Resource                                                                                           |
    | :---------- | :------------------------------------------------------------------------------------ | :---------------- | :------------------- | :------------------------------------------------------------------------------------------------- |
    | CogVideoX-3 | Significant improvements in image quality, stability, and physical realism simulation | English & Chinese | multiple resolutions | [Guide](/guides/video/cogvideox-3)<br /><br />[API Reference](/api-reference/video/generate-video) |

    ### Agents

    A set of ready-made agents empower users to create and communicate effortlessly.

    | Tool                                    | Capability                                                                 | Resource                      |
    | :-------------------------------------- | :------------------------------------------------------------------------- | :---------------------------- |
    | GLM Slide/Poster Agent(beta)            | Combine content generation with professional design                        | [Guide](/guides/agents/slide) |
    | General-Purpose Translation             | Support 40+ languages, flexible strategies, and terminology customization  | [Guide](/guides/agents/slide) |
    | Popular Special Effects Video Templates | Special effects video templates like French\_Kiss, BodyShake, and Sexy\_Me | [Guide](/guides/agents/slide) |
  </Accordion>
</AccordionGroup>
