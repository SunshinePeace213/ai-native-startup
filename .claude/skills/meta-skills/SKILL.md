---
name: meta-skills
description: The team standard and guided workflow for authoring Claude Code Skills and slash commands. Use when the user wants to create a new skill or slash command, turn a workflow or prompt into a reusable skill or /command, fix a skill or command that isn't triggering or fires too often, run evals or benchmark a skill against baseline, optimize a description for triggering accuracy, modernize an older skill for the current model generation, or package a skill for distribution. Also use when the user describes a repeatable workflow worth capturing, even if they never say "skill" or "command". Covers choosing between a skill, a slash command, or a subagent. Not for authoring subagents — use meta-agent.
---

# Meta-Skills: Authoring Skills and Commands

The **standard** for what a good skill looks like and the **workflow** for
producing one. The standard lives in `references/`; this body is the loop that
applies it. Read each reference at the phase that needs it — don't preload them.

## Operating principle

A skill is a **trigger plus a body that loads on demand**. The `description`
decides whether it ever fires; the body is what the model reads once it does.
Those are two separate problems, and each has its own way of being wrong.

Writing the body is **subtraction**. A subagent stamps one model and is written
for it — a skill loads into whatever model runs the session, so it has to
survive every Claude 5 reader. They already self-verify, self-correct, pace
their own updates, and calibrate length to the task. Instructing those behaviors
compounds with them and degrades the result. Write the contract, then cut every
line any reader already honors.

Three rules carry the rest:

- **The description is the whole routing interface.** It earns its place
  unconditionally; every line of the body has to.
- **Capability and depth are frontmatter.** `model` buys knowing, `effort` buys
  trying. Neither comes from prose.
- **Guarantees are harness, not prose.** If something *must* happen, reach for a
  hook or a permission rule. An instruction is a preference.

## Skill, command, or subagent?

Settle this before writing anything.

- A **slash command** is a reusable prompt the user invokes by name (`/review`,
  `/commit`) — a flat file at `.claude/commands/<name>.md`.
- A **skill** is knowledge or capability Claude reaches for on its own, or any
  command that needs bundled material — `.claude/skills/<name>/SKILL.md` with
  optional `references/`, `scripts/`, `assets/`, `evals/`.
- A **subagent** does delegated, context-isolated work and returns a summary.
  Different artifact — route to the **meta-agent** skill.

Commands *are* skills in current Claude Code: both produce `/name`, run
identically, and take the same frontmatter. So the first two are a layout choice:

- **Flat command** when the user drives it by typing `/name`, it's a single
  prompt, and it needs no supporting files.
- **Skill directory** when Claude should auto-trigger it, or it needs
  `references/`, `scripts/`, or an eval suite.
- **Never ship both names** — a same-name skill silently beats the flat command.
- Either form with side effects (`/commit`, `/deploy`, `/send-*`) gets
  `disable-model-invocation: true`, so only the user can fire it.

## References — load each when its phase arrives

| Read | When |
| --- | --- |
| `references/frontmatter.md` | Choosing and validating frontmatter; char caps; writing the `description` |
| `references/model-tuning.md` | After the body exists — the union subtraction pass, and when to stamp `model`/`effort` |
| `references/anti-patterns.md` | Scanning a draft; fixing a trigger that misfires; the pre-ship checklist |
| `references/command-format.md` | Writing a slash command — the house template and injection |
| `references/verification-loops.md` | The skill *is* a check on other work, or needs one embedded |
| `references/evaluation.md` | Running evals, reading a benchmark, tuning the description |
| `references/schemas.md` | The JSON shapes for evals, grading, and benchmarks |
| `agents/grader.md`, `analyzer.md`, `comparator.md` | Prompts for the grading, analysis, and blind-comparison subagents |

## The workflow

Phases, not a railroad. Skip what doesn't apply; loop back when a later phase
exposes a gap. Figure out where the user already is and start there — a draft in
hand means going straight to the eval loop, and "just vibe with me" means skip
the evals entirely.

1. **Capture intent** — what the skill enables, the contexts and phrasings that
   should route to it, the output shape, and whether the output is objectively
   checkable (file transforms and code generation are; writing voice and design
   aren't). The conversation may already hold the workflow being captured —
   extract the tools, the sequence, and the corrections, and confirm.
2. **Route** — skill, command, or subagent, per the gate above.
3. **Interview and research** — edge cases, formats, example files, success
   criteria, dependencies. Read one or two nearby skills for conventions to match.
4. **Write the frontmatter** — read `references/frontmatter.md`. `name` matches
   the directory; `description` is the trigger document and carries the real
   user vocabulary.
5. **Write the body** — the goal and its constraints, in imperative form. Give
   the reasoning behind a constraint so the model handles the cases the letter
   of the rule doesn't cover. Keep it under 500 lines; past that, split into
   `references/<topic>.md` one level deep and point at each with a clear "read
   this when". Reference bundled files as `${CLAUDE_SKILL_DIR}/...`.
6. **Subtract** — read `references/model-tuning.md` and cut what every reader
   already does. Expect the draft to get shorter.
7. **Validate and lint**:

   ```bash
   uv run --with pyyaml python -m scripts.eval <skill-dir> --lint
   ```

   Every `FAIL` is a fix. A `WARN` is a line to reread with intent in mind —
   these files are the one place the flagged phrasings legitimately appear, so
   judge each on its merits.
8. **Evaluate** — read `references/evaluation.md`. Write two or three realistic
   test prompts into `evals/evals.json`, confirm them with the user, then run
   the layers. Commands skip this unless their output is gradeable; the test
   there is simpler — would Claude fire it on the phrasings users type, and does
   invoking it beat typing the request by hand?

## Modernizing an existing skill

Skills written for earlier models are usually too prescriptive, and on Claude 5
readers the excess costs quality rather than just tokens. Audit by deletion:
read the body against `references/model-tuning.md` and
`references/anti-patterns.md`, cut every line a current reader already honors,
then re-lint. Expect the file to get substantially shorter; if it didn't, the
pass wasn't done.

Where the skill has evals, snapshot it first so the baseline is the version
you're trying to beat.

## Package

Only for distribution:

```bash
uv run --with pyyaml python -m scripts.quick_validate <skill-dir>   # "Skill is valid!"
uv run --with pyyaml python -m scripts.package_skill <skill-dir> dist/
```

`quick_validate` enforces the stricter public Agent-Skills surface —
`name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`.
The Claude Code-only fields are fine in-repo and stripped on the way out. Clear
the checklist below first. The `.skill` goes to `dist/` or straight to the user,
never into a workspace.

## Pre-ship checklist

- [ ] Right artifact, right location, no same-name duplicate
- [ ] `description` is a trigger document: third person, front-loaded, the real
      phrasings, within caps, no angle brackets
- [ ] Body carries goal and constraints rather than a script, unless order is
      load-bearing
- [ ] Ran the subtraction pass from `references/model-tuning.md`
- [ ] References one level deep; bundled paths via `${CLAUDE_SKILL_DIR}`;
      forward slashes; MCP tools qualified `Server:tool`
- [ ] Side-effecting artifacts set `disable-model-invocation: true`
- [ ] `model` an alias if stamped at all; `effort` only where quality needs it
- [ ] `scripts.eval --lint` clean, and `evals/` committed if the skill has them
