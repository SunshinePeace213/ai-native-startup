<!--
EXAMPLE: skill-example-format-error
Artifact type: skill (directory format)
Thariq category: 3 (Library & API Reference) + light Tip-8 script bundling
Demonstrates: Tips 1 (lean), 2 (Gotchas), 3 (progressive disclosure), 4 (goal+constraints), 6 (pushy description), 8 (bundled script)
Why "good": description names specific user phrasings; body refers to references/python-tracebacks.md for detail instead of inlining; Gotchas captures Python 3.12+ behavior changes; bundles a script rather than re-deriving extraction logic.

NOT installed as a real skill. Illustrative-but-functional — would work if copied to .claude/skills/format-error/.
-->
---
name: format-error
description: |
  Format Python tracebacks (and bare exception strings) into structured error reports
  showing the failing call, the immediate cause, and a probable fix direction.
  Use when the user pastes a traceback, says "what's going wrong here", "this error
  doesn't make sense", "format this error", or shares a stack trace and asks for
  help diagnosing. Also use proactively when an error appears in test/CI output
  the user is working through.
allowed-tools: Read, Grep, Bash(python3 *)
---

# Format Error

Turns Python tracebacks into structured reports — the failing call, the proximate cause, and a probable fix direction. Reduces the time between "here's a traceback" and "here's where to look."

## When this skill applies

- User pastes a multi-line traceback
- User shows a bare exception (`KeyError: 'config'`)
- Test output in conversation shows a failing assertion with stack
- User asks "what's going wrong with this error"

If the error is from a language other than Python, decline and suggest searching for the relevant library docs instead.

## Gotchas

- Python 3.11+ tracebacks include `^^^^` markers under the failing expression — preserve these in the output; they're load-bearing for diagnosis.
- `KeyError` exceptions stringify the key with quotes (`KeyError: 'foo'`) — strip the quotes when matching against likely dict structures.
- Pytest tracebacks use `>` markers for the failing line; these aren't part of Python's standard format and need to be stripped before parsing.
- Tracebacks from async code show the awaiter twice (once in the calling coroutine, once in the event loop) — collapse these in the report.

## Workflow

Goal: produce a structured error report. Constraints:

- Output a 3-section report: **Failing call** (file:line + 1-line context), **Cause** (the exception type + message in plain English), **Fix direction** (one paragraph: most likely cause + where to look)
- If the traceback is < 5 lines, just paraphrase the cause; the structured format is overhead
- If the traceback spans > 100 lines (common with deep frameworks), summarize the user's-code portion only — frame frames aren't actionable

Use `scripts/extract_frames.py` to parse the traceback rather than parsing inline (avoids per-invocation re-derivation; see Tip 8).

For Python-specific exception semantics (what `__init_subclass__` errors mean, what `RecursionError` actually signals about the call graph), read `references/python-tracebacks.md`.

## Output specification

```markdown
## Failing call
`{file}:{line}` — {one-line context}

## Cause
{exception type}: {plain-English version of the message}

## Fix direction
{2-3 sentence paragraph: most likely cause, where to look}
```

## Reference files

- `references/python-tracebacks.md` — exception semantics not obvious from the docs

## Bundled scripts

- `scripts/extract_frames.py` — parses a traceback into structured frames; used in the workflow above
