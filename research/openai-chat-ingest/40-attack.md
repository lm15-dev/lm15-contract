# Attack — lenses on MAP-12

Self-review by the drafting agent, 2026-09-08. **Labelled as such: a
second agent was not available in session** (`playbooks/design-pass.md`
step 7). The independent review should redo this page.

## Cold learner
"I called it with my litellm kwargs and it said `n` is unsupported." —
Correct and intended; the message says to fan out in the caller. Risk: the
learner reads "unsupported" as "lm15 can't do multiple samples". Mitigation
is the message text, which names the reason. Not pinned (messages never
are).

## Library author on top (DSPy)
Needs `from_call(model, messages, **kwargs)`. Builds `{"model":..,
"messages":.., **kwargs}` and calls the function — one line. Sends
`parallel_tool_calls` without `tool_choice`: handled (a ToolChoice at mode
`auto` is created). Sends a pydantic class as `response_format`: NOT JSON;
DSPy must render it to the `json_schema` object first (litellm does the
same). Stated in the DSPy PR, not lm15's concern.

## Port implementer
Rust: the verdict registry is data; the block-type `match` needs an
explicit `_ => refuse` arm. The preset-conditioned rows mean the decoder
takes the resolved compat, exactly as the encoder does — no new type. The
118-body round trip gives the port a differential oracle for free.

## Cost accountant
Nothing here spends. The one place money could leak is a foreign
reasoning spelling forwarded and ignored (hidden reasoning tokens billed);
that is the refusal in rule 1.

## Provider-switcher mid-conversation
Ingests a DeepSeek transcript (with `reasoning_content` on assistant rows)
under the DeepSeek preset, gets ThinkingParts, sends to Anthropic: the
Anthropic adapter replays unsigned thinking as text (decision G). Works;
the thinking is visible, not lost. Ingests it under the OpenAI preset by
mistake: `reasoning_content` on HISTORY rows still reads (it is a typed
field, read on every preset); a top-level `thinking` knob would refuse.
Consistent: content is content, knobs are per-dialect.

## Where this could be wrong
- The `default` bucket assumes the wire default never changes. If OpenAI
  flips a default (e.g. `strict` defaulting to true), a body with
  `strict: false` would carry information. The registry row would then
  move to `map`/`refuse` with a `changes/` entry; the scrape re-check date
  is the guard.
- Guessing a URL image's media type from its extension is a heuristic
  (the only one in the rule). It is applied to a field the wire does not
  carry at all, and the alternative (always the default) is worse; a
  wrong guess changes nothing on the chat wire (which sends the URL) and
  matters only when the Request is re-targeted at a dialect that needs
  the type.
