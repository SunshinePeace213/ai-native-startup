# Plan: Create `meta-agent` — the team standard for authoring Claude Code subagents

## Task Description

Create a new, standalone Claude Code **skill** named `meta-agent` at `.claude/skills/meta-agent/` that is the team's canonical standard *and* guided workflow for authoring Claude Code **subagents** (`.claude/agents/*.md`). It plays the same role for subagents that the existing `meta-skill` plays for skills and `meta-commands` plays for slash commands — completing a three-peer trilogy of lean authoring skills.

The existing `.claude/agents/meta-agent.md` is outdated: its frontmatter covers only `name`, `description`, `tools`, `color`, `model`, and its body uses a stale `Purpose / Instructions / Workflow / Report` template. It predates the current 17-field subagent frontmatter surface (`disallowedTools`, `permissionMode`, `effort`, `memory`, `skills`, `mcpServers`, `hooks`, `isolation`, `background`, `maxTurns`, `initialPrompt`, …) and the Opus 4.8 authoring guidance. It is **retired** as part of this change.

All knowledge content is **authored fresh** from the live documentation (decision below). `prompt-architect` is expired and is **not** used as a source. The new skill is fully self-contained: it does **not** reference `meta-skill`'s or `prompt-architect`'s internal files at runtime.

**Task type:** feature (new skill) + small chore (retire old agent). **Complexity:** medium.

## Objective

A working `.claude/skills/meta-agent/` skill that:

- Triggers reliably on subagent-authoring requests ("create a new subagent", "make an agent that…", "build a subagent for…", "fix this agent's frontmatter", "why isn't my agent triggering").
- Has a `SKILL.md` body under 500 lines (target ~150–250) that reads as a *standard + workflow*, not a tutorial.
- Documents **every** subagent frontmatter field in a dedicated reference, each with: required/optional, allowed values/constraints, what it controls, and when an authoring agent should set it.
- Carries the current subagent **body skeleton**, the **five common shapes**, **4.8 authoring principles** scoped to subagents, and an **anti-patterns + pre-ship checklist** reference.
- Ships a fresh, **lightweight** frontmatter validator (`scripts/validate_agent.py`) plus an inline "test with realistic delegation prompts vs baseline" step in the workflow — no heavy eval/grade/benchmark machinery.
- Replaces the old `.claude/agents/meta-agent.md`, whose file is moved to `~/.Trash/` (per AGENTS.md safe-delete).

## Problem Statement

The team has a clean, maintainable standard for authoring **skills** (`meta-skill`) and **commands** (`meta-commands`), but its standard for authoring **subagents** is the stale `.claude/agents/meta-agent.md`. That file (a) documents a tiny, outdated slice of the frontmatter surface, (b) uses a body template that doesn't match how good subagents are written today, and (c) predates the Opus 4.8 guidance where `effort` is the dominant capability lever and subagents are the one artifact where you set it in frontmatter.

There is no single, lean, trustworthy "this is how we build subagents" artifact. The valuable subagent material that exists elsewhere lives inside `prompt-architect`, which is expired and explicitly out of bounds as a source. The result: people either copy the outdated agent template or improvise.

## Solution Approach

Build `meta-agent` as a standalone skill whose value is **standards + a guided workflow**, kept small through progressive disclosure — mirroring `meta-skill`'s proven shape but lighter:

- **Lean `SKILL.md` body** = the authoring workflow (capture intent → choose form/frontmatter → draft body → write file → validate → test vs baseline → iterate) plus explicit "read this when…" pointers into references. No prose that restates what Claude already does.
- **`references/` authored fresh** from the live sources studied during planning:
  - `code.claude.com/docs/en/sub-agents` (authoritative: all 17 frontmatter fields, scopes/precedence, tool inheritance, model resolution, memory, skills preload, hooks, fork, nested subagents, the tools unavailable to subagents).
  - `github.com/shanraisshan/claude-code-best-practice/.../claude-subagents.md` (field-by-field best-practice usage; "use proactively" in descriptions; least-privilege tools).
  - Opus 4.8 prompting guidance (effort as the dominant lever; thinking off by default; literal instruction-following; conservative subagent spawning; direct tone) — distilled to only the deltas that matter for subagents.
- **Self-contained.** `meta-agent`'s references duplicate only the *small, subagent-relevant* slice of 4.8 principles rather than pointing at `meta-skill`'s files. No cross-skill runtime dependency.
- **Lightweight apparatus.** A fresh `scripts/validate_agent.py` (stdlib + PyYAML via `uv run --with pyyaml`) that validates an agent file's frontmatter against the documented field surface, plus an inline workflow step to test the generated agent with 2–3 realistic delegation prompts against a no-agent baseline. No `eval-viewer/`, `grader.md`, `benchmark`, or `package` scripts.
- **Clean cutover.** Move `.claude/agents/meta-agent.md` to `~/.Trash/`. Because the agent type `meta-agent` is *defined by* that file, retiring it also removes the old auto-trigger — so the new skill cleanly owns subagent-authoring requests with **no trigger collision** (nothing else needs editing).

## Relevant Files

Use these files to complete the task:

- `.claude/agents/meta-agent.md` — **the outdated agent to retire.** Read it once for any framing worth preserving, then move the file to `~/.Trash/`. Do **not** carry its `Purpose/Instructions/Workflow/Report` body template forward.
- `.claude/skills/meta-skill/SKILL.md` — **structural sibling to mirror** (lean body + "read each reference when its phase arrives" table + a Gotchas section). Match its *shape and tone*, not its skills-specific content.
- `.claude/skills/meta-skill/references/frontmatter.md` — **format model** for how to document a frontmatter field surface (the per-field table: Field / Req / Type-constraints / Controls / Set-it-when). Reuse the *layout*, author subagent content fresh.
- `.claude/skills/meta-skill/scripts/quick_validate.py` — **invocation-pattern model** for the validator (run from the skill dir via `uv run --with pyyaml python …`). Write a new agent-specific validator; do not reuse skill validation logic.
- `specs/meta-skill-rebuild.md` — the precedent plan for this exact kind of work; follow its rigor (acceptance criteria, validation commands, cutover discipline).
- `AGENTS.md` — tooling rules that govern execution: Python via `uv` (never `python`/`pip`); JS via `bun`; rich panels full width; **safe-delete via `mv … ~/.Trash/`, never `rm -rf`**.

### Live source docs (cite at the top of each reference)

- `https://code.claude.com/docs/en/sub-agents`
- `https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-subagents.md`
- Opus 4.8 prompting guidance (`platform.claude.com` prompt-engineering page for Opus 4.8).

### New Files

- `.claude/skills/meta-agent/SKILL.md` — lean frontmatter + workflow body.
- `.claude/skills/meta-agent/references/frontmatter.md` — **centerpiece**: every subagent frontmatter field documented.
- `.claude/skills/meta-agent/references/body-structure.md` — the system-prompt body skeleton + the five common shapes + one fuller worked example.
- `.claude/skills/meta-agent/references/authoring-principles.md` — subagent-scoped Opus 4.8 authoring principles.
- `.claude/skills/meta-agent/references/anti-patterns.md` — subagent anti-patterns + bad→good descriptions + a pre-ship checklist.
- `.claude/skills/meta-agent/scripts/validate_agent.py` — fresh lightweight frontmatter validator.

## Implementation Phases

### Phase 1: Foundation
Cutover and scaffold. Move the old `.claude/agents/meta-agent.md` to `~/.Trash/` and create the new skeleton (`.claude/skills/meta-agent/{references,scripts}`). Confirm the agent type `meta-agent` is gone (so the new skill has no auto-trigger competitor).

### Phase 2: Core Implementation
Two independent streams run in parallel: (a) author the four fresh knowledge references from the live docs; (b) write the lightweight `scripts/validate_agent.py`. Once both exist, write the lean `SKILL.md` (frontmatter + workflow body) that points into them.

### Phase 3: Integration & Polish
Validate the artifact: run `validate_agent.py` against a generated sample agent and against the worked example; confirm `SKILL.md` body < 500 lines and references one level deep; confirm `description` + `when_to_use` ≤ 1,536 chars; smoke-test triggering with 2–3 realistic prompts; confirm the old agent is in `~/.Trash/` and absent from `.claude/agents/`. Produce a short pass/fail report.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members to do the building, validating, and testing.
  - Your job is high-level direction, not building.
  - Validate all work is on track and the team is converging on the plan.
  - Coordinate via the Task* tools.
- Take note of the session id of each team member so you can resume them.

> Note: `.claude/agents/team/` does not exist in this repo, and the only project agent (`meta-agent`) is being retired by this plan, so all team members use the `general-purpose` agent type.

### Team Members

- Builder
  - Name: `builder-references`
  - Role: Authors the four fresh knowledge references (`frontmatter.md`, `body-structure.md`, `authoring-principles.md`, `anti-patterns.md`) from the live docs. Owns accuracy of every documented frontmatter field and the 4.8 distillation.
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `builder-core`
  - Role: Performs the cutover (Trash old agent, scaffold new dir), writes the lightweight `scripts/validate_agent.py`, and writes the lean `SKILL.md` once references and validator exist.
  - Agent Type: `general-purpose`
  - Resume: true
- Validator
  - Name: `validator-qa`
  - Role: Runs the validator, checks frontmatter/structure/size, smoke-tests triggering, confirms the old agent was safely trashed. Reports pass/fail against acceptance criteria.
  - Agent Type: `general-purpose`
  - Resume: false

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

### 1. Cutover and scaffold
- **Task ID**: cutover-scaffold
- **Depends On**: none
- **Assigned To**: builder-core
- **Agent Type**: general-purpose
- **Parallel**: false
- Read the current `.claude/agents/meta-agent.md` once for any framing worth preserving (then discard the rest of the template).
- Move the old agent to Trash: `mv .claude/agents/meta-agent.md ~/.Trash/meta-agent-old-$(date +%s).md` (per AGENTS.md — never `rm -rf`).
- Create the new skeleton: `mkdir -p .claude/skills/meta-agent/references .claude/skills/meta-agent/scripts`.
- Confirm `.claude/agents/meta-agent.md` no longer exists, so the agent type `meta-agent` is no longer registered (no auto-trigger competitor for the new skill).

### 2. Author fresh knowledge references
- **Task ID**: author-references
- **Depends On**: cutover-scaffold
- **Assigned To**: builder-references
- **Agent Type**: general-purpose
- **Parallel**: true
- Author `references/frontmatter.md` documenting **every** subagent frontmatter field. At minimum: `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt` (and note `prompt` as the `--agents`/CLI equivalent of the markdown body). For each: required/optional, type/allowed values, what it controls, and "when an authoring agent should set it." Include these load-bearing rules from the live docs:
  - `name`: lowercase letters + hyphens, unique across the whole agents tree, filename need-not-match; hooks receive it as `agent_type`.
  - `description` is the trigger: name specific phrasings/contexts; "use proactively" / `PROACTIVELY` encourages auto-delegation.
  - **Tool inheritance:** omitting `tools` inherits all; `disallowedTools` is applied first, then `tools` resolves against the remainder; MCP patterns (`mcp__server`, `mcp__server__*`, `mcp__*`); `Agent(agent_type)` allowlist (only for a main-thread `--agent`); the tools **unavailable to subagents** (`AskUserQuestion`, `EnterPlanMode`, `ExitPlanMode` unless `permissionMode: plan`, `ScheduleWakeup`, `WaitForMcpServers`).
  - `model`: `sonnet`/`opus`/`haiku`/`fable`/full-id/`inherit` (default `inherit`) + the 4-step resolution order.
  - `effort`: `low|medium|high|xhigh|max`; **the dominant 4.8 lever and the one artifact where you set it in frontmatter**.
  - `memory`: `user`/`project`/`local`, auto-enables Read/Write/Edit, injects first 200 lines/25KB of `MEMORY.md`.
  - `skills` preloads full skill content; cannot preload `disable-model-invocation: true` skills.
  - `permissionMode` table + parent-precedence rules; `isolation: worktree`; `background`; `maxTurns`; `initialPrompt`; `color`.
  - **Plugin caveat:** `hooks`, `mcpServers`, `permissionMode` are ignored for plugin subagents.
- Author `references/body-structure.md`: the body **is** the system prompt (subagent sees only its prompt + delegation message → restate any rule it depends on). Document the skeleton (Role line → `## When to invoke` with a "Not for" boundary → `## Inputs` → `## Process` → `## Success looks like` → `## Output` → `## Edge cases`; 2–3 header levels max), the **five common shapes** (read-only researcher; memory specialist; restricted executor w/ PreToolUse hook; skill-augmented specialist; hook-enforced workflow w/ verification), and **one fuller worked example** written to the skeleton.
- Author `references/authoring-principles.md`: the subagent-relevant 4.8 deltas only — effort as the dominant lever (and per-agent guidance: `xhigh` hard coding/agentic, `high` reasoning-sensitive default, `low`/`medium` scoped helpers); thinking off by default (drop "think harder"/"take a deep breath"); literal instruction-following (state in/out scope); conservative subagent spawning (be explicit when fan-out is wanted); lean focused body; least-privilege tools; description-as-trigger; memory only when knowledge compounds.
- Author `references/anti-patterns.md`: subagent anti-patterns (too many tools, vague description, bloated persona, capital-letter MUSTs without a *why*, memory for one-shot work, forced progress-update cadence, "think harder" prose), bad→good `description` examples, and a concrete pre-ship checklist.
- Keep each reference tight and example-driven; cite the live doc URLs at the top of each file. Match repo tooling in any examples (`uv`, `bun`).

### 3. Build the lightweight validator
- **Task ID**: build-validator
- **Depends On**: cutover-scaffold
- **Assigned To**: builder-core
- **Agent Type**: general-purpose
- **Parallel**: true
- Write `scripts/validate_agent.py` (stdlib; parse YAML via `uv run --with pyyaml`). It takes a path to a `.claude/agents/<name>.md` file and validates frontmatter against the documented surface:
  - Required `name` and `description` present and non-empty.
  - `name` is lowercase letters + hyphens only.
  - `model` (if set) is in `{sonnet, opus, haiku, fable, inherit}` or matches a full-id pattern (e.g. `claude-opus-4-8`).
  - `effort` (if set) ∈ `{low, medium, high, xhigh, max}`; `permissionMode` ∈ the documented set; `color` ∈ the documented set; `memory` ∈ `{user, project, local}`; `background`/`isolation` valid.
  - `tools`/`disallowedTools` entries look like real tool names or MCP patterns; warn (don't fail) on unrecognized names.
  - Warn when `hooks`/`mcpServers`/`permissionMode` are set (ignored if the agent is loaded from a plugin).
  - Frontmatter is real YAML between `---` markers (not fenced in a code block).
- Print clear `PASS` / per-issue diagnostics; exit non-zero on any hard failure. Keep it small (target < ~120 lines). Any console formatting uses full-width panels per AGENTS.md (plain stdout is fine — no `rich` dependency required).
- Self-test it against the worked example in `references/body-structure.md` (extract to a temp file under `$CLAUDE_JOB_DIR/tmp`) to confirm it runs.

### 4. Write the lean SKILL.md
- **Task ID**: write-skill-md
- **Depends On**: author-references, build-validator
- **Assigned To**: builder-core
- **Agent Type**: general-purpose
- **Parallel**: false
- Write frontmatter:
  - `name: meta-agent` (also the directory name).
  - A front-loaded, third-person, slightly pushy `description` naming concrete trigger phrasings: "create a new subagent", "make an agent that…", "build a subagent for…", "update/fix an agent's frontmatter", "why isn't my agent triggering / being delegated to", "turn this repeated delegation into a reusable subagent". Note it fires even when the intent is buried in a longer request.
  - `when_to_use` carrying routing context + a **negative boundary**: "Not for authoring Skills (use meta-skill) or slash commands (use meta-commands)."
  - Keep `description` ≤ 1,024 chars (plain text, no `<`/`>`) and `description` + `when_to_use` ≤ 1,536 chars combined.
- Write the workflow body (goals + constraints, not a rigid script): **Capture intent → Choose form & frontmatter → Draft the body → Write the file (`.claude/agents/<name>.md`) → Validate → Test vs baseline → Iterate**. Add a "read this reference when its phase arrives" table pointing at `references/frontmatter.md`, `references/body-structure.md`, `references/authoring-principles.md`, `references/anti-patterns.md`, and at `scripts/validate_agent.py` (with its exact `uv run --with pyyaml` invocation). Add a short Gotchas section.
- Apply the principles to the skill's own prose: no obvious-stating, no `$100 tip`/"think harder", no forced progress cadence. Keep body < 500 lines (target ~150–250).

### 5. Validate, smoke-test, and report
- **Task ID**: validate-all
- **Depends On**: cutover-scaffold, author-references, build-validator, write-skill-md
- **Assigned To**: validator-qa
- **Agent Type**: general-purpose
- **Parallel**: false
- Run the Validation Commands below; capture output.
- Confirm `SKILL.md` body < 500 lines, references one level deep, and `description` + `when_to_use` ≤ 1,536 chars (no `<`/`>` in `description`).
- Confirm `references/frontmatter.md` covers every field listed in Task 2.
- Run `validate_agent.py` against a freshly generated sample agent (write a small valid agent to `$CLAUDE_JOB_DIR/tmp`, validate it → PASS) and against a deliberately malformed one (→ non-zero exit). This proves the gate works.
- **Trigger smoke-test:** for 2–3 realistic prompts ("create a subagent that runs the test suite and reports failures", "make a read-only code-review agent"), verify `meta-agent` is the selected skill and that a skill-creation prompt instead routes to `meta-skill` (boundary holds).
- Confirm old agent is absent from `.claude/agents/` and present in `~/.Trash/`.
- Report pass/fail per acceptance criterion; surface anything skipped (fail loud).

## Acceptance Criteria

- `.claude/skills/meta-agent/SKILL.md` exists with frontmatter `name: meta-agent` and a valid, parseable YAML header.
- `SKILL.md` body is < 500 lines and reads as a standard + workflow (not a tutorial that restates the obvious).
- `description` ≤ 1,024 chars with no `<`/`>`; `description` + `when_to_use` ≤ 1,536 chars combined; `description` is third-person, front-loaded, names concrete trigger phrases, and `when_to_use` carries the "not for skills/commands" boundary.
- `references/frontmatter.md` documents **every** subagent frontmatter field (the 16 listed + the `prompt`/CLI note), each with required/optional, constraints, what it controls, and when to set it — including tool-inheritance order, tools unavailable to subagents, model resolution, the `effort` lever, memory behavior, and the plugin-ignored-fields caveat.
- `references/body-structure.md`, `references/authoring-principles.md`, and `references/anti-patterns.md` exist, are tight, and cite the live docs.
- `scripts/validate_agent.py` exists, runs via `uv run --with pyyaml`, PASSes a valid sample agent, and exits non-zero on a malformed one.
- No heavy apparatus present (no `eval-viewer/`, `grader.md`, `benchmark`, or `package` scripts) — the skill stays lightweight.
- All references are exactly one level deep from `SKILL.md`.
- Old agent (`.claude/agents/meta-agent.md`) is moved to `~/.Trash/` and no longer in `.claude/agents/`.
- The skill is self-contained: no runtime references to `meta-skill`'s or `prompt-architect`'s internal files.
- **Trigger smoke test passes:** subagent-authoring prompts select `meta-agent`; a skill-authoring prompt selects `meta-skill` (boundary holds).

## Validation Commands

Execute these commands to validate the task is complete:

- `test -f .claude/skills/meta-agent/SKILL.md && echo OK` — new SKILL.md exists.
- `wc -l .claude/skills/meta-agent/SKILL.md` — confirm body < 500 lines.
- `head -25 .claude/skills/meta-agent/SKILL.md` — confirm frontmatter (`name: meta-agent`, description present, no `<`/`>`).
- `uv run --with pyyaml python -c "import yaml; d=open('.claude/skills/meta-agent/SKILL.md').read().split('---')[1]; print(yaml.safe_load(d).keys())"` — frontmatter parses as valid YAML.
- `find .claude/skills/meta-agent/references -maxdepth 1 -name '*.md'` — references exist and are one level deep.
- `ls .claude/skills/meta-agent/references/frontmatter.md .claude/skills/meta-agent/references/body-structure.md .claude/skills/meta-agent/references/authoring-principles.md .claude/skills/meta-agent/references/anti-patterns.md` — all four knowledge refs present.
- `cd .claude/skills/meta-agent && printf -- '---\nname: sample-agent\ndescription: A valid sample agent for validator self-test. Use proactively to test.\ntools: Read, Grep\nmodel: inherit\n---\n\nYou are a sample agent.\n' > "$CLAUDE_JOB_DIR/tmp/sample-agent.md" && uv run --with pyyaml python scripts/validate_agent.py "$CLAUDE_JOB_DIR/tmp/sample-agent.md"` — validator PASSes a valid agent.
- `cd .claude/skills/meta-agent && printf -- '---\nname: Bad_Name\ndescription:\nmodel: gpt-4\n---\nbody\n' > "$CLAUDE_JOB_DIR/tmp/bad-agent.md"; uv run --with pyyaml python scripts/validate_agent.py "$CLAUDE_JOB_DIR/tmp/bad-agent.md"; echo "exit=$?"` — validator FAILS a malformed agent (non-zero exit).
- `ls .claude/skills/meta-agent/eval-viewer .claude/skills/meta-agent/agents 2>&1` — must report "No such file" (no heavy apparatus).
- `test ! -f .claude/agents/meta-agent.md && echo "old agent retired"` — old agent absent.
- `ls ~/.Trash/ | grep meta-agent-old` — old agent present in Trash.
- `awk 'NR>1 && /^---/{exit} NR>1{print}' .claude/skills/meta-agent/SKILL.md | wc -c` — sanity-check frontmatter size toward the 1,536-char listing budget.

## Notes

- **Tooling (AGENTS.md):** Python via `uv` only; never `python`/`pip`. JS via `bun`. Rich panels full width. Safe-delete via `mv … ~/.Trash/` — never `rm -rf`. No new dependencies beyond `PyYAML`, supplied at runtime via `uv run --with pyyaml`.
- **Why a separate skill, not merged into `meta-skill`:** subagents have a distinct ~17-field frontmatter surface and distinct trigger vocabulary ("create an agent" vs "create a skill"). Merging would dilute triggering for both and grow one skill back toward the prompt-architect bloat the team is escaping. Three lean peers (`meta-skill`, `meta-commands`, `meta-agent`) is the maintainable shape.
- **Why a skill, not an agent (decision rationale):** the artifact's job is a knowledge-heavy *standard + guided workflow* that iterates in the main conversation and benefits from progressive disclosure (lean body + on-demand `references/`). The live docs themselves point to Skills for "reusable prompts or workflows that run in the main conversation context." A subagent body can't do progressive disclosure cleanly without re-creating the single-giant-file bloat. Claude Code's built-in `/agents` "Generate with Claude" already covers ad-hoc delegated generation; the differentiated value the team wants is the standard, which is skill-shaped.
- **No trigger collision to manage:** the agent type `meta-agent` exists only because of `.claude/agents/meta-agent.md`. Retiring that file removes the type, so the new skill owns subagent-authoring triggers with nothing else to edit (unlike the `meta-skill`/`prompt-architect` case, which needed `disable-model-invocation`).
- **Knowledge provenance:** all references authored fresh from `code.claude.com/docs/en/sub-agents`, the shanraisshan best-practice `claude-subagents.md`, and the Opus 4.8 prompting guidance. `prompt-architect` is expired and is **not** a source.
- **Decisions locked during planning (via grilling):** (1) form factor = standalone **skill**; (2) old `.claude/agents/meta-agent.md` = **retire to `~/.Trash`**; (3) knowledge = **authored fresh**, no prompt-architect; (4) apparatus = **lightweight** (fresh validator + inline test step), no full eval/grade/benchmark/package machinery.
