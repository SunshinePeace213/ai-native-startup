# Acceptance Criteria: Multi-Layer Review Pipeline for /build

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.
>
> NOTE: these artifacts are prompt/Markdown + TOML — there is no app build/typecheck. Validation is
> **structural** (existence, valid TOML/frontmatter, required sections, ordering) plus a human
> read-through. All commands run from the worktree root.

## Acceptance Criteria

- **AC1 — Worktree-first bootstrap.** `/build` enters the worktree (from the
  `[worktree]` arg, else autodiscovered via `.claude/worktrees/*/specs/<plan>/spec.md`)
  **before** it resolves `spec.md`; the `## Tracking` issue `#N` is the source of truth,
  never re-derived from the mangled local branch. Observable: in `build.md` the
  worktree step precedes the spec-resolution step.
- **AC2 — Draft PR early + ready at end.** Right after entering the worktree, `/build`
  opens a **draft** PR on the convention branch (`Closes #N`) seeded with the 7-item
  Build-Status checklist, and marks it **ready** (`gh pr ready`) only after the final
  Codex verdict. Graceful-skip language is present for no-`gh` / no-issue.
- **AC3 — Tailored code-simplifier agent.** `.claude/agents/code-simplifier.md` exists
  with valid frontmatter and covers Python, TS/Next.js/React, and the Markdown harness
  layer, including the explicit semantics-preservation guardrail for prompt files, and
  references AGENTS.md. `/build` runs it as the internal-check phase, commits, and ticks
  **Internal check**.
- **AC4 — Claude code-review skill (AGENTS.md-targeted).** `.claude/skills/claude-code-review/SKILL.md`
  exists with valid frontmatter and the ported pipeline (eligibility → 5 Sonnet lenses →
  Haiku 0–100 confidence → keep ≥80), checks **AGENTS.md** (not CLAUDE.md), targets
  `git diff origin/main...HEAD`, and outputs both a PR comment and the ≥80 findings.
- **AC5 — Six Codex review subagents + orchestrator.** Exactly 6 valid
  `.codex/agents/*.toml` files exist (each with `name`/`description`/`developer_instructions`,
  `sandbox_mode = "read-only"`), and the upgraded `implementation-review` skill spawns
  them (or runs the 6 lenses as sequential passes if headless spawn is unavailable) plus
  runs the plan's Validation Commands and plan-adherence.
- **AC6 — One committed report; Claude reads the file.** Each Codex round writes ONE
  consolidated report to `specs/<plan>/reviews/codex-impl-review-round-N.md`
  (verdict header + `Validation:` block + grouped findings); `/build` commits it and
  reads the verdict from that file (not stdout), relays it to the PR, ticks
  **Codex review R{N}**; the loop is capped at **2** rounds.
- **AC7 — Per-checkpoint, trailer-free commits.** `build.md` specifies one conventional
  `Refs #N` commit (no `Co-Authored-By` trailer) after impl, internal-check,
  Claude-review fixes, each Codex report, and each fix round, with scoped `git add`.
- **AC8 — Command structure + guards intact.** `build.md` contains the 7-item
  Build-Status checklist, the three new phases, the draft-PR + ready steps, and retains
  every existing guard (never merge, never push to `main`, graceful-skip) and the legacy
  `plan.md` fallback.
- **AC9 — Structural validity.** Every new/changed file parses: all 6 TOMLs are valid
  with required keys; the skill and agent have `name` + `description` frontmatter; the
  required sections/markers are present.
- **AC10 — Scope preserved.** No out-of-scope file changed: `git diff origin/main...HEAD`
  touches none of `/plan-w-team.md`, `/ship.md`, `.agents/skills/spec-review/`, or
  `specs/_templates/`.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- Count the Codex subagents — verifies **AC5**. A pass prints `6`:
  - `ls .codex/agents/*.toml | wc -l | tr -d ' '`

- Validate every subagent TOML + required keys + read-only sandbox — verifies
  **AC5, AC9**. A pass prints `all TOMLs valid with required keys + read-only`:
  ```
  uv run python - <<'PY'
  import tomllib, glob
  req = {"name", "description", "developer_instructions"}
  files = sorted(glob.glob(".codex/agents/*.toml"))
  assert len(files) == 6, f"expected 6, found {len(files)}"
  problems = []
  for f in files:
      with open(f, "rb") as fh:
          data = tomllib.load(fh)          # load each TOML once
      missing = req - data.keys()
      if missing:
          problems.append((f, f"missing keys: {sorted(missing)}"))
      if data.get("sandbox_mode") != "read-only":
          problems.append((f, f'sandbox_mode={data.get("sandbox_mode")!r} (want "read-only")'))
  assert not problems, f"invalid TOMLs: {problems}"
  print("all TOMLs valid with required keys + read-only")
  PY
  ```

- Skill + agent frontmatter present — verifies **AC3, AC4, AC9**. A pass prints `OK`
  for both files:
  ```
  for f in .claude/skills/claude-code-review/SKILL.md .claude/agents/code-simplifier.md; do
    { head -1 "$f" | grep -q '^---$'; } && grep -q '^name:' "$f" && grep -q '^description:' "$f" \
      && echo "OK $f" || echo "BAD $f"
  done
  ```

- Claude code-review skill retargets AGENTS.md + keeps the pipeline — verifies **AC4**.
  A pass prints `claude-review OK`:
  ```
  grep -qi "AGENTS.md" .claude/skills/claude-code-review/SKILL.md \
    && grep -qiE "confidence|0-100|≥\s*80|>= ?80|\b80\b" .claude/skills/claude-code-review/SKILL.md \
    && grep -q "origin/main...HEAD" .claude/skills/claude-code-review/SKILL.md \
    && echo "claude-review OK"
  ```

- code-simplifier is multi-language with the prompt guardrail — verifies **AC3**. A pass
  prints `simplifier OK`:
  ```
  grep -qi "Python" .claude/agents/code-simplifier.md \
    && grep -qiE "React|Next" .claude/agents/code-simplifier.md \
    && grep -qi "Markdown" .claude/agents/code-simplifier.md \
    && grep -qiE "preserv|never (weaken|drop)|semantics" .claude/agents/code-simplifier.md \
    && echo "simplifier OK"
  ```

- implementation-review orchestrates + writes the committed report — verifies **AC5,
  AC6**. A pass prints `impl-review OK`:
  ```
  grep -qiE "spawn|subagent" .agents/skills/implementation-review/SKILL.md \
    && grep -q "reviews/codex-impl-review-round" .agents/skills/implementation-review/SKILL.md \
    && grep -qiE "terse|summary" .agents/skills/implementation-review/SKILL.md \
    && echo "impl-review OK"
  ```

- Every committed review target pins the base diff — verifies **AC5, AC6**. The
  `implementation-review` orchestrator skill and all 6 review-subagent TOMLs must name
  `git diff origin/main...HEAD` as the primary review target. A pass prints
  `review-target OK`:
  ```
  target='origin/main...HEAD'
  files=(.agents/skills/implementation-review/SKILL.md .codex/agents/*.toml)
  n=${#files[@]}
  [ "$n" -eq 7 ] || { echo "FAIL: expected 7 review-target files (1 skill + 6 TOMLs), found $n"; exit 1; }
  ok=0
  for f in "${files[@]}"; do
    grep -qF "$target" "$f" && ok=$((ok+1)) || echo "FAIL: $target missing in $f"
  done
  [ "$ok" -eq "$n" ] && echo "review-target OK ($ok/$n pin $target)" || { echo "review-target FAIL"; exit 1; }
  ```

- `build.md` enters the worktree before resolving the spec — verifies **AC1, AC8**. A
  pass prints `worktree-first OK …`:
  ```
  uv run python - <<'PY'
  import re
  lines = open(".claude/commands/build.md").read().splitlines()
  first = lambda pat: next((i for i, l in enumerate(lines) if re.search(pat, l)), None)
  # Anchor to the ACTUAL bootstrap step: the real EnterWorktree(...) call that enters the
  # worktree, and the line that resolves spec.md AS the plan (PLAN = ...spec.md) — NOT the
  # Variables/prose mentions of "worktree"/"autodiscover" or the autodiscover glob.
  wt = first(r"EnterWorktree\(")
  spec = first(r"PLAN\s*=.*spec\.md")
  assert wt is not None, "no real EnterWorktree( call found in build.md"
  assert spec is not None, "no 'PLAN = ...spec.md' resolution step found in build.md"
  assert wt < spec, f"EnterWorktree step (line {wt}) must precede spec resolution (line {spec})"
  print(f"worktree-first OK (EnterWorktree@{wt} < spec-resolution@{spec})")
  PY
  ```

- `build.md` carries the phases, draft/ready, and guards — verifies **AC2, AC8**. A pass
  prints `OK:` for every marker:
  ```
  for s in "Internal check" "Claude code review" "Codex review R1" "Codex review R2" \
           "pr create --draft" "pr ready" "never merge"; do
    grep -qi "$s" .claude/commands/build.md && echo "OK: $s" || echo "MISSING: $s"
  done
  ```

- Commit cadence is trailer-free — verifies **AC7**. A pass prints `commit-policy OK`:
  ```
  grep -qE "Refs #" .claude/commands/build.md \
    && grep -qiE "no .*Co-Authored-By|trailer-free|without .*Co-Authored" .claude/commands/build.md \
    && echo "commit-policy OK"
  ```

- Scope preserved — verifies **AC10**. A pass prints `scope preserved`:
  ```
  git fetch -q origin main 2>/dev/null || true
  if git diff --name-only origin/main...HEAD \
       | grep -E "^(\.claude/commands/(plan-w-team|ship)\.md|\.agents/skills/spec-review/|specs/_templates/)"; then
    echo "SCOPE VIOLATION"; else echo "scope preserved"; fi
  ```

- **Manual (AC8/AC4/AC3):** human read-through of `build.md`, the new skill, the agent,
  and the 6 TOMLs for prompt-quality issues structural checks can't catch — confirm the
  phase prose is unambiguous and every guard reads correctly. Fail loud on anything unclear.
