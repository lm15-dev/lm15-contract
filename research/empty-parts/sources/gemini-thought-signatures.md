> ## AI Agent Context
> Get the complete documentation index at: https://aistudio.google.com/llms.txt
> Use this file to discover all available pages.
> For the full documentation in a single file, fetch: https://aistudio.google.com/llms-full.txt

# Thought signatures

The Interactions API makes it easier to work with thought signatures because it
manages reasoning at the API level. To learn more about configuring model
thinking, managing stateless thought steps, and viewing summaries, see the
[Gemini thinking](/docs/thinking#signatures) guide.

When you use the Interactions API, you don't need to manually extract or pass
signatures on individual content parts. The API simplifies signature
management in two key ways:

* **Automatic state management:** In stateful mode (`store: true`), the server
  manages conversation context automatically. It stores and passes thought
  signatures between turns so you don't have to track them.
* **Dedicated thought steps:** In stateless mode, internal reasoning is
  isolated into dedicated `thought` steps in the `steps` array. Signatures stay
  cleanly inside these steps instead of attaching to user inputs, model text
  outputs, or function calls.

