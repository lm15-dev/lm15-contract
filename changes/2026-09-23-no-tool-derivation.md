# A tool is written out, in every language

**DECIDED 2026-09-23 by the maintainer ("Do it all now. Go.").** No SDK derives a
tool from a function. Applies before 1.0.

## Rule

A function tool is data: a name, an optional description, and a JSON Schema for
its inputs, written out by the user (`FunctionTool` in each language's spelling).
No SDK reads one off a function signature, type hints, doc comments or a macro.
A request holds only tools; an SDK that can recognise a function or callable
passed where a tool belongs refuses it, and names the fix (write the
`FunctionTool`, keep the function to run when the model calls it). SDKs still
never execute tools.

## Why

- **The same everywhere.** TypeScript, Rust and Go cannot read a function's input
  types while a program runs. Derivation existed in two of six languages (Python
  `tool(fn)` since 2026-06-11, Julia `@tool`), so "learn it once, use it in any
  language" did not hold for tools, and the shared documentation had to explain
  tools per language.
- **It had drifted.** Python and Julia derived different schemas from the same
  function (Julia added `"additionalProperties": false`).
- **It is a convenience with opinions** (docstring styles, type mapping, strict or
  open schemas). That belongs to the library built on lm15, which can make those
  choices once for all the languages it supports.

## What changed

- Python: removed `tool`, `derive_tool`, `ToolConfig`, `ToolDerivation`,
  `DerivedParam`, `ToolDerivationError` and `lm15.tools`. A function in
  `Request.tools` / `LiveConfig.tools` is refused with the fix named.
- Julia: removed `@tool`, `tool`, `ToolBinding`, `tool_arguments`,
  `execute_tool`, `tool_schema`, `tool_decode` and `ToolInputError`. Result-side
  helpers (`tool_value`, `tool_content`, `array_content`, `table_content`) remain:
  they turn a function's result into tool-result content, which is not derivation.
  A function in `tools` is refused with the fix named.
- TypeScript, Go, Rust, R: unchanged (they never derived tools).
- Consumers: DSPy maps `ToolDerivationError` in `dspy/clients/errors.py`; that
  mapping is removed with this change. The published DSPy 3.4.0b1 vendors
  lm15 1.0.0a1 and keeps its own copy.

No wire change and no fixture change: a derived tool and the same tool written
out were already identical on the wire.

## Supersedes

`playbooks/api-family.md` § Tools ("Python: `tool(fn)` derives schema") and the
parity ledger row for `lm15.tool` / `derive_tool`; the Python proposal
`docs/router-portability.md` Part 2 is withdrawn.
