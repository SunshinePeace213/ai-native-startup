# Decisions: Migrate /grilling into /plan-w-team

Decision log for the requirement-gathering work that produced `plan.md` in this
folder. Source of truth for WHY the plan is shaped the way it is.

## Summary

`/plan-w-team` currently jumps straight from `USER_PROMPT` to a written spec with
no requirement-gathering step, so the plan is built on assumptions. We will inline
the `/grilling` interview as a new phase that runs *before* design, driven by the
`AskUserQuestion` tool (one question at a time, recommended answer first, "Other"
for free input), looping until a coverage ledger is clear and the user signs off.
Output moves to a per-plan folder `specs/<plan-name>/` holding two files:
`plan.md` (the implementation plan) and `decisions.md` (this log). The standalone
`/grilling` skill is left functionally intact; only its description is corrected.

## Resolved Decisions

### Integration approach
- **Question:** How should grilling be wired into plan-w-team?
- **Answer:** Inline grilling as a new phase inside `plan-w-team.md`.
- **Rationale:** Recommended option. Deterministic — the phase always runs and
  does not depend on the model choosing to invoke another skill. Sidesteps the
  `disable-model-invocation` constraint entirely (a command containing the
  behavior is just following instructions, not invoking the skill).

### Standalone /grilling skill flag + description
- **Question:** What to do with the standalone skill's `disable-model-invocation`
  flag and its description?
- **Answer:** Keep `disable-model-invocation: true`; fix the description.
- **Rationale:** Recommended option. A relentless interview is high-friction and
  should only start on an explicit `/grilling`, never auto-fire. The current
  description advertises "grill trigger phrases" (auto-trigger) which the flag
  forbids — a standing contradiction. Remove the dead auto-trigger clause.

### AskUserQuestion cadence
- **Question:** What cadence should the grilling phase use?
- **Answer:** One question per AskUserQuestion call.
- **Rationale:** Recommended option. Honors grilling's core "one at a time" tenet
  (multiple questions at once is bewildering). Each question carries 2-4 concrete
  options with the recommended answer first ("(Recommended)"); the tool's
  automatic "Other" choice covers free-form input.

### Additional features to build
- **Question:** Which additional grilling features should we build in?
- **Answer:** All four selected.
- **Rationale:** (1) Coverage dimensions + open-questions ledger give the loop a
  real termination condition ("until everything is discussed"). (2) Decision log
  written to its own file gives requirement to decision to plan traceability.
  (3) Accept-all-recommendations escape hatch prevents over-grilling and keeps
  the user in control. (4) Final confirmation checkpoint replays all decisions
  for sign-off before the spec is written.

### Output folder
- **Question:** Where should the plan be written?
- **Answer:** A per-plan folder, `specs/<plan-name>/`.
- **Rationale:** User requirement. Replaces the old flat `specs/<name-of-plan>.md`.

### Decision log file
- **Question:** Where does the grilling record live?
- **Answer:** Its own file in the per-plan folder, storing everything.
- **Rationale:** User requirement. Separates the durable decision record from the
  implementation plan.

### Filenames
- **Question:** What to name the two files in `specs/<plan-name>/`?
- **Answer:** `plan.md` (implementation plan) and `decisions.md` (this log).
- **Rationale:** The folder already carries the topic, so the files are
  role-named and predictable. Alternatives offered: `spec.md`, `decision-log.md`,
  `requirements.md`. `plan.md` + `decisions.md` chosen unless overridden.

### /build invocation
- **Question:** How should `/build` be invoked and what should it read?
- **Answer:** Accept a **feature name** (a folder under `specs/`) as well as a
  direct path; read **both** `plan.md` and `decisions.md` from the per-plan
  folder.
- **Rationale:** User requirement (`/build grilling-into-plan-w-team`). The
  decision log holds binding constraints (locked decisions, assumptions,
  out-of-scope), so the builder must read it, not just the plan. Feature-name form
  is the ergonomic default; direct paths and legacy flat specs stay supported for
  back-compat. Resolution order and the new `build.md` body are spec'd in `plan.md`
  section C.

## Assumptions

- **`specs/` not `spec/`.** The user wrote `spec/{name}/`; the existing directory
  is `specs/` (holds `meta-agent-skill.md` etc.). Assuming `specs/` to stay
  consistent. Revisit if a new top-level `spec/` is actually wanted.
- **AskUserQuestion is already available to plan-w-team.** Its frontmatter uses
  `disallowed-tools: Task, EnterPlanMode` (no `allowed-tools` allowlist), so
  AskUserQuestion is permitted. No frontmatter tool change is needed; we must
  only avoid adding an `allowed-tools` allowlist that would exclude it.
- **Adaptive depth is in scope.** The grilling phase scales effort to complexity
  (light for simple chores, deep for complex features) so trivial tasks are not
  over-interrogated. Bundled into feature #1, not treated as separate.

## Open Questions / Out of Scope

- **Standalone /grilling body upgrade (CONFIRM):** The decisions scoped the
  standalone skill change to description-only. Whether to *also* upgrade the
  standalone skill's body to use AskUserQuestion + the new features (for parity
  with the inlined phase) is deferred. Default: leave the standalone body as
  prose; only fix the description. Flag if you want parity instead.
- **meta-skill-family audit (added at user request):** Invoked all three
  authoring skills via the Skill tool and grepped each `SKILL.md` for injection
  tokens. `meta-skill` and `meta-agent` load clean; **`meta-commands` fails to
  load** because its body documents the `bang-backtick` injection syntax with
  live tokens (lines 51/128/129/131), which the loader executes at load time.
  Findings + fix are now in `plan.md` (Incident Report). Treated as a separate,
  parallel change — does not block the grilling migration.
- **Out of scope:** Changing `plan-w-team`'s own `disable-model-invocation` (it
  writes files, so the house standard would suggest `true`, but the user did not
  request it — noted, not changed).
- **`/build` updated (added at user request):** `/build` now accepts a feature
  name (`/build grilling-into-plan-w-team` → `specs/grilling-into-plan-w-team/`)
  and reads both `plan.md` and `decisions.md`, treating the decision log as binding
  context during the build. Direct paths and legacy flat specs still resolve.
  Spec'd in `plan.md` section C.
