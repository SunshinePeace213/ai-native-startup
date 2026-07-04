# Anti-Patterns & Pre-Ship Checklist

Scan every draft for these before shipping. If the user explicitly wants one,
explain the cost once and comply only if they confirm.

## What to cut from a body

The body is a recurring per-turn cost once loaded. Cut anything that wouldn't
change the output if deleted.

- **Stating the obvious.** "Read the file carefully", "use clear names",
  "handle edge cases", "be thorough" — Claude does this by default. Keep only
  what pushes it *out* of its defaults: domain facts, constraints, formats.
- **Railroading.** A rigid step list handles the cases the author imagined and
  breaks on the rest. Give the goal and the constraints; let the model find
  the path. Exception: genuinely order-dependent or irreversible operations —
  there, be exact.
- **Re-teaching tools.** "Use the Edit tool to change files" is noise. Name a
  tool only when the choice is load-bearing.
- **Prompting theatrics.** Fake incentives ("I'll tip $100"), competitive
  framing, inflated personas ("10,000+ PRs reviewed"), vague stakes, "think
  step by step" / "think harder", forced progress-update cadences, and
  all-caps MUST/NEVER without a reason — current models read these literally;
  they add tokens, not behavior. State the constraint and its *why* instead.
- **Unspecified output shape.** "Provide a thorough analysis" is unanchored.
  When shape matters, give length, structure, or a schema; to reduce
  verbosity, one positive example of the right concision beats "don't
  over-explain".
- **Offering too many options.** "Use pypdf or pdfplumber or PyMuPDF or…" —
  give one default with an escape hatch.
- **Time-sensitive content.** "Before August, use the old API" rots in place.
  Keep a collapsed "old patterns" note if history matters at all.
- **Structural smells:** an unbroken 500+ line body (split to `references/`),
  nested references (`SKILL.md → a.md → b.md` gets partially read), Windows
  path separators, unqualified MCP tool names (use `Server:tool`), angle
  brackets in the description.

## BAD → GOOD descriptions

| BAD | GOOD |
|---|---|
| `A helpful skill for PostgreSQL migrations.` | `Drafts safe, reversible PostgreSQL migrations following the project's conventions. Use when the user adds/drops a column, changes a constraint, backfills data, or mentions "migration" or "alter table" — even without naming a migration.` |
| `I help you make plans for your projects.` | `Creates a concise engineering implementation plan from the user's requirements and saves it to the specs directory. Use when the user asks to "plan", "spec out", or "write an implementation plan".` |
| `The build command. Builds things.` | `Implements an existing plan file in the codebase. Use when the user says "build the plan", "implement this spec", or passes a path to a plan to execute.` |
| `Commits and manages all your git work and branches and remotes and tags.` | `Stages and commits the current changes with a generated message. Use when the user asks to "commit" or "save my changes". Not for pushing or PRs — use commit-push-pr.` |

The shift each time: vague summary → third person, front-loaded, the user's
real phrasings, slightly pushy, and a boundary that routes to a sibling.

## Triggering fixes

**Under-triggering:** the description is missing the words users actually
type — add the real phrasings; check `disable-model-invocation` isn't set;
check `/doctor` for truncation (many artifacts → descriptions get cut; a
longer description does not trigger better).

**Over-triggering:** make the description specific and add a "Not for…"
boundary; side effects → `disable-model-invocation: true`; two artifacts
competing → sharpen both so their trigger sets don't overlap.

## Useful patterns

- **Setup config.** A skill needing per-installation context (a Grafana URL,
  an account id, a Slack channel) reads `${CLAUDE_SKILL_DIR}/config.json`; if
  absent, ask the user, write it, proceed. Skip for pure transforms or when
  the info lives in the codebase.
- **State across runs.** Append-only logs or a small JSON cache let a runbook
  skill improve over time (log each run, read the last few at startup). Store
  outside the skill directory — it may be wiped on upgrade. Skip for
  stateless skills.
- **Gotchas section.** The highest-signal section in a mature skill: specific
  things that bit someone and aren't in any doc. Flat bullets, one or two
  sentences each. Skip it for brand-new skills; add the first entry the first
  time something breaks.

## Pre-ship checklist

Any failure → fix, then reread the whole draft fresh.

- [ ] Decision gate applied — this is the right artifact (command / skill /
      subagent) in the right location, and no same-name duplicate exists
- [ ] `description` is a trigger document: third person, front-loaded, real
      user phrasings, within caps, no angle brackets
- [ ] `when_to_use` is non-redundant (gate/routing) or omitted
- [ ] Skills: directory name is lowercase-hyphen and `name` matches it;
      commands: `argument-hint` present when args are taken, Variables
      ordered dynamic-first
- [ ] Body under 500 lines; nothing states what Claude already does; goal +
      constraints rather than a script (unless order is load-bearing)
- [ ] References one level deep; files over ~300 lines have a ToC; bundled
      paths via `${CLAUDE_SKILL_DIR}`; forward slashes; MCP tools qualified
- [ ] Side-effecting artifacts set `disable-model-invocation: true`;
      `allowed-tools` covers any injection blocks; `model` is an alias
- [ ] Tooling in examples matches AGENTS.md (uv, bun)
- [ ] `scripts/validate.py` passes; for distribution, `quick_validate` passes
      on the strict packaging surface
