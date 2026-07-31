# Decisions: studio-layer — design-delivery studio through signed handoff

> The interview record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle
> tracking and the Codex review record live in spec.md, NOT here; this file is the
> immutable decision history.
>
> Decisions 1–15 are transcribed verbatim from
> [discovery/decisions-draft.md](./discovery/decisions-draft.md), the locked ledger from
> `/harness-layer:harness-interview`. Decisions 16–18 were resolved from the codebase during
> planning, not asked. The discovery pages (`unknowns.html`, `brainstorm.html`,
> `interview.html`) are referenced, never copied.

## Summary

Build a design-delivery studio layer under the `studio-layer` namespace: eight phase
commands (`/studio-layer:p0-intake` … `p7-retro`) run by the main session as principal,
nine role agent files it spawns directly, and client project data in a gitignored
`clients/<client>/<project>/` inside this repo so path-scoped rules and command-scoped
hooks resolve while nothing client-owned enters git history. This plan builds brainstorm
cards 01–09 — the namespace, the roster, the forked discovery loop, the client-artifact
rule, the eight commands, the cold-designer test, the sign-off hook, the design-QA verifier,
and the revision counter. Cards 10–12 (lesson graduation, the design KB, the first real
project run) are follow-on plans. Every acceptance criterion lands as a mechanism: a Stop
hook per hard gate, a check script per countable claim, a verifier agent for the judgment
calls.

## Resolved Decisions

- **Q:** Where does client project data live?
  - **A:** `clients/<client>/<project>/` inside this repo, gitignored.
  - **Why:** Path-scoped rules (`paths: clients/**`) and command-frontmatter hooks resolve
    against `CLAUDE_PROJECT_DIR`; a sibling repo puts client files outside that root, so no
    studio rule would load and no hook would see a sign-off file. Gitignoring keeps NDA'd
    material out of the harness repo's permanent history. Rules out the sibling-repo layout
    and a tracked `clients/`.

- **Q:** What is the layer called, and where does the Soriza brand live?
  - **A:** Namespace `studio-layer`, plus `.claude/rules/studio-layer/studio-identity.md`
    carrying the studio name, voice, letterhead, and sign-off block that every client-facing
    document inherits. Soriza is an AI startup providing website design, software
    development, and agentic-layer services.
  - **Why:** `harness-layer` set the precedent of naming a function, not an owner. A
    namespace rename later touches every command path, every `paths:` rule, every agent
    name, and every test that reads them; a brand in a deliverable costs nothing to change.
    Rules out `soriza-layer` and `soriza-studio`.

- **Q:** How many of the twelve brainstorm cards land in this plan?
  - **A:** Cards 01–09. Cards 10, 11, and 12 become follow-on plans.
  - **Why:** 01–09 is the whole scaffolding in one diff CI can gate. Card 12 is a usage run
    on a real brief, not a diff — it cannot be an acceptance criterion of a prompt-file PR,
    and card 11's KB mirrors depend on card 12's prototype-tool answer.

- **Q:** Where does the client-interview cookbook come from?
  - **A:** Fork `harness-interview.md`'s round mechanics into the P1 phase command, swapping
    the thirteen harness dimensions for client ones.
  - **Why:** The mechanics worth reusing are in `harness-interview.md:32-42` — the coverage
    ledger, one round at a time ordered by blast radius, and the bounded stop condition. The
    `grilling` skill is ten lines and carries none of it. The two ledgers share no rows, so
    the fork cannot drift in a way that matters.

- **Q:** Eight phase commands, or one command taking the phase as an argument?
  - **A:** Eight: `/studio-layer:p0-intake` through `/studio-layer:p7-retro`.
  - **Why:** A Stop hook that must run inside one command registers in that command's
    frontmatter (`harness-plan.md:8-12`, named as the spec-gate pattern in `hooks.md:36`).
    One parameterized command could only register the sign-off hook for every phase at once,
    firing it on soft gates too — which is the thing card 07 exists to prevent.

- **Q:** Do the nine roles get agent files, or live in spawn prompts?
  - **A:** Nine agent files under `.claude/agents/studio-layer/`. The principal is the main
    session and gets no file.
  - **Why:** `orchestration.md` — spawning a teammate from an existing subagent type reuses
    that definition's `tools` and `model`. It is the only shape where the roster's stamps are
    load-bearing rather than prose, and `test_model_drift.py:111` reads exactly that
    frontmatter. Inline spawn prompts leave every stamp a suggestion CI cannot check.

- **Q:** Hybrid agent names (`art-director-elena-ferraro`) or plain function names?
  - **A:** Plain function names, layer-prefixed: `studio-art-director`, `studio-discovery-lead`,
    and so on. The person opens the body.
  - **Why:** Resolved from the code, not asked. Claude routes off `name` + `description`;
    `name` must be unique tree-wide. The unknowns pass locked personas out of routing, and a
    hybrid name puts the persona back into the routing document. The layer prefix satisfies
    tree-wide uniqueness.

- **Q:** Where does the question bank live, and what makes it fail?
  - **A:** A skill the client-facing roles **invoke** via the Skill tool, plus a check script
    that re-derives the dimension list from the skill's own question list and fails when the
    discovery notes leave one unanswered without an explicit "N/A, because".
  - **Why:** `skills:` frontmatter is not applied to teammates, so preloading would silently
    no-op in the architecture this plan locks. Invocation works for both spawn shapes. The
    check script is what turns the bank from prose into a mechanism, per the plan's own
    acceptance bar; re-deriving rather than hard-coding follows the drift tier rule.

- **Q:** Is the P2 project brief a PRD?
  - **A:** No. The brief is the client agreement — goals, audience, scope, constraints,
    success. The P6 handoff pack (tokens, states, breakpoints, copy deck, assets) is what a
    builder consumes.
  - **Why:** This repo already owns the converter: `/harness-layer:harness-plan` turns intent
    into `spec.md`. A studio PRD would duplicate that spec with no mechanism keeping the two
    in sync, and would pull the layer across the line it was scoped to stop at.

- **Q:** One sign-off hook, or one per hard gate?
  - **A:** One `check_gate_signoff.py`, with the phase passed as an argument in each
    command's frontmatter registration (`… check_gate_signoff.py p2`). Four registrations:
    P2, P3, P4, P6.
  - **Why:** `check_spec_completeness.py` infers its target from the newest-modified plan
    folder, which is safe there because a run touches one plan. A client project holds all
    eight phase folders at once, so mtime inference would gate the wrong phase. One script
    means one test file and no drift between four near-identical copies.

- **Q:** Does the cold-designer diff block P2 or advise it?
  - **A:** Advisory list, with the triage document as what the gate requires. The teammate's
    section plan and its diff against the signed sitemap land as a document; the principal
    triages every row as "brief unclear, amend it" or "acceptable variance, because…", and
    the P2 sign-off hook blocks on the triage document existing with no untriaged row.
  - **Why:** Two competent designers given one brief produce different section plans — that
    is what "directions, not versions" says elsewhere in the same brief. A zero-diff gate
    would never open, and the principal would start deleting rows to pass it. Gating the
    triage document makes the mechanism real without demanding an impossible diff.

- **Q:** What palette do client-facing pages use before a direction is picked at P4?
  - **A:** The Soriza studio default through P0–P3; the picked direction's tokens from P4
    onward. The client-artifacts rule names the palette's *source* per phase rather than
    locking a hex table.
  - **Why:** The reason to fork `artifacts.md` at all is that a client mockup should not wear
    our pipeline colors. Borrowing Warm Neutral would make every client's early deliverables
    identical to our internal pages, with no trigger for "tailor later" ever firing.

- **Q:** Are contrast, focus visibility, and tap targets computed or asserted?
  - **A:** Computed. The check script reads the handoff's token table, computes the WCAG ratio
    for every declared foreground/background pair, and checks specced tap targets against the
    minimum. The design-QA agent judges focus order, whether each state makes sense, and
    whether the error copy says anything useful.
  - **Why:** `meta-agent/SKILL.md:46` — guarantees are harness, not prose. Arithmetic on hex
    values is the least reliable thing a model does; judgment about whether an empty state
    earns its copy is the least reliable thing a script does. Neither is trusted for the
    other's job.

- **Q:** What shape is a change order?
  - **A:** A client-facing document at `clients/<client>/<project>/change-orders/<n>.md` —
    what is requested, what it costs in rounds and time, and a signature block. The revision
    log row references it; the signed brief is amended by reference and never re-signed.
  - **Why:** The P2 sign-off records the hash of what was approved and the revision count
    re-derives its allowance from that same brief. Re-signing the brief per request would
    invalidate the recorded hash and destroy the count's baseline.

- **Q:** How does P1 actually run its rounds, and who conducts them?
  - **A:** Page-first, like this interview: each round publishes an interactive artifact
    carrying visual references, style examples, and option chips for the client to react to,
    with a copy-as-prompt block returning their answers. The principal conducts every
    client-facing round; `studio-discovery-lead` (Priya) authors the question set from the
    bank before each round and turns the answers into written statements and glossary entries
    after.
  - **Why:** A client gives far more when reacting to something visual than when answering
    prose. It also routes around a hard limit: `AskUserQuestion` is one of six tools that
    never work in a subagent, so no spawned role can ask the client anything. Only the
    principal's session can drive an interactive round.

- **Q:** Where do the four check scripts live?
  - **A:** `.claude/scripts/studio-layer/`. Resolved from the code during planning, not asked.
  - **Why:** `test_wiring.py::test_every_entrypoint_is_claimed_by_a_registration_surface`
    treats any PEP 723 or shebang file under `.claude/hooks/` as a hook entrypoint requiring a
    registration surface, and `test_dispositions_cover_every_entrypoint` requires a Codex
    verdict for each. A command-invoked check script has neither, so putting it there would
    turn the wiring suite red. A `scripts/` folder inside the question-bank skill (the
    `meta-agent/scripts/validate_agent.py` precedent) was the alternative; it loses because
    three of the four scripts serve commands, not that skill. `.claude/scripts/` is swept by
    no existing test collector.

- **Q:** How does a hook taking an argument get tested, given `run_hook` passes no argv?
  - **A:** Extend the shared fixture with `args: tuple = ()`, appended after the script path.
  - **Why:** `hooks.md` requires every hook test to launch through `run_hook` and forbids
    hand-built environments or bespoke launchers, but the fixture as written runs
    `uv run --script <path>` with nothing after it — no existing hook takes an argument. A
    per-feature launcher would be exactly the drift the shared fixture exists to prevent, so
    the fixture grows the parameter. Existing call sites pass no `args` and are unaffected.

- **Q:** Do any roles run as agent-team teammates?
  - **A:** No. Every role is a subagent, and each denies the `Agent` tool. Revised at Codex
    round 1 (R1-F7 through R1-F10).
  - **Why:** The draft kept one teammate for P2's cold-designer check, on the reasoning that a
    teammate does not inherit the lead's conversation history. That property is not special to
    teammates — a subagent gets its own context window and inherits no conversation history
    either, so the teammate bought nothing while adding the experimental agent-teams
    dependency. It also cost correctness: teammate reuse of a subagent definition covers
    `tools` and `model`, not `effort`, so the roster's effort stamps — the very thing the
    drift test pins — would silently stop applying. One spawn shape removes a dependency,
    removes a contradiction between "P2 is the only teammate" and "P4 is the clear teammate
    case", and keeps every stamp load-bearing. Subagents inherit the `Agent` tool by default,
    so `disallowedTools: Agent` on each role is what makes "one level deep" a property rather
    than a sentence.

- **Q:** Do the check scripts go to Codex, given they are parser and arithmetic work?
  - **A:** No — `opus` at `high`, like the rest of the build.
  - **Why:** `model-selection.md` routes parsers and matchers to `gpt-5.6-sol`, but
    `/harness-layer:harness-build` has no Codex implementation path; Codex enters this
    pipeline at review. A task stamped to a provider the build stage cannot invoke is not a
    step that can run as written. The Codex gate still judges the result, so the
    cross-provider check survives.

## Assumptions

- The sign-off SHA is a content hash of the approved artifact, not a git SHA — `clients/`
  is gitignored, so no commit object exists. Invalidated if client work later moves to its
  own git repo inside `clients/`.
- Every role runs as a **subagent**, one level deep, with `disallowedTools: Agent`. Each body
  restates what it needs and invokes the question bank through the `Skill` tool. Invalidated
  if a phase turns out to need roles talking to each other — that would require first
  re-deriving how a teammate's effort is set, since it does not come from the agent file.
- The question-bank skill does **not** carry `disable-model-invocation: true` — that flag
  makes a skill user-invocable only, which would put it out of reach of the very roles meant
  to invoke it.
- Studio rules are all path-scoped to `clients/**`, so none of them load during ordinary
  harness work and none count against the ~250-line always-loaded budget in
  `memory-series.md:28-37`.
- Card 02's "no new test code" is wrong and the plan corrects it: `_claude_declarations()`
  sweeps `.claude/{agents,commands,skills}` frontmatter and never opens `.claude/rules/`, so
  a new drift test must re-derive each role's stamp from `roster.md` and compare it to the
  agent file. Existing drift tests only check that a stamp appears somewhere in
  `model-selection.md`. **Verified this run** at `tests/harness-layer/test_model_drift.py:111-119`.
- "Self-improving" question bank means write-back **between** projects, not within a run — a
  loaded skill is static for that session. The write-back mechanism is card 10's retro
  graduation, deferred to a follow-on plan; v1 ships the bank and the improvement loop
  arrives later.
- The contrast thresholds ship as **Soriza project thresholds**, not as a WCAG conformance
  claim: 4.5:1 for normal text, 3:1 for large text and UI components, and a 24×24 CSS px
  minimum target. They are taken from WCAG 2.2 as commonly published, but card 11 — which
  would mirror the specification into the KB — is explicitly out of scope, so nothing in this
  repo can cite the source yet. The script names them project thresholds and the QA report
  says the same; when card 11 lands, the constants gain a citation and may change. Claiming
  conformance to a specification the repo has not mirrored would be the kind of unfalsifiable
  assertion this plan exists to remove. Invalidated if card 11's mirror shows a different
  value.
- The plan folder keeps the chain slug `cpo-layer` rather than being renamed to
  `studio-layer`. Discovery is already committed under it and the prompt names that path
  twice; the naming decision governs the harness namespace, not the plan folder. Invalidated
  if the folder name later confuses the `specs/index.md` catalog.

## KB References

The `claude-code-guide` cross-check subagent was denied permission this run, so every claim
below was verified by reading the cached mirrors directly. Line numbers are from the mirrors
as fetched. No conflicts were found and no gap-fill was needed; nothing in the plan depends
on an unmirrored page.

| Doc | Fetched | Grounds |
| --- | --- | --- |
| `ai-docs/anthropic/subagents.md` | 2026-07-21 | `AskUserQuestion` is unavailable to subagents, alongside `EndConversation`, `EnterPlanMode`, `ExitPlanMode`, `ScheduleWakeup`, `WaitForMcpServers` — six tools (l.324–332). Confirms the principal must conduct every client-facing P1 round. |
| `ai-docs/anthropic/subagents.md` | 2026-07-21 | Subdirectories under `.claude/agents/` do not affect identity or invocation; `name` frontmatter is the sole identifier and must be unique tree-wide (l.178–180). Grounds `.claude/agents/studio-layer/` + layer-prefixed names. |
| `ai-docs/anthropic/subagents.md` | 2026-07-21 | `skills:` controls preloading, not access — without it a subagent still invokes skills through the `Skill` tool (l.478); a skill with `disable-model-invocation: true` cannot be preloaded at all (l.480). Grounds the invocable question bank. |
| `ai-docs/anthropic/subagents.md` | 2026-07-21 | `model:` accepts an alias or `inherit`, defaulting to `inherit` (l.300–301). Grounds the roster's per-role alias stamps. |
| `ai-docs/anthropic/agent-teams.md` | 2026-07-21 | "The `skills` and `mcpServers` frontmatter fields in a subagent definition are not applied when that definition runs as a teammate" (l.261). The load-bearing claim behind invoke-don't-preload; every role body must restate what it needs. |
| `ai-docs/anthropic/agent-teams.md` | 2026-07-21 | A teammate is an independent session loading project context but not the lead's conversation history (l.274); a teammate cannot supply consent on the user's behalf (l.268); teams need `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (l.13). Grounds dropping teammates — the isolation is not teammate-specific and the dependency is experimental. Corrected at round 1: these lines do **not** state that a teammate cannot prompt the user, and that claim has been removed. |
| `ai-docs/anthropic/skills.md` | 2026-07-21 | Subdirectories of `.claude/skills/` load (l.109), and **the directory name — not the `name:` field — becomes the command** (l.120); `disable-model-invocation: true` makes a skill user-invocable only (l.166). Grounds naming the directory `studio-client-questions/` to match the skill name, and omitting the flag. |
| `ai-docs/anthropic/hooks.md` | 2026-07-21 | Stop-hook input schema and exit-code semantics behind `check_gate_signoff.py`: exit 2 denies the stop and stderr returns to Claude; `stop_hook_active` is true when Claude is already continuing because of a Stop hook, must be checked "to avoid blocking on a condition that will never resolve", and Claude Code force-ends the turn after 8 consecutive blocks (l.2171). Grounds the re-entry behavior. |
| `ai-docs/anthropic/memory.md` | 2026-07-21 | `paths:` frontmatter scopes a rule so it loads only when the session touches a matching file. Grounds `paths: clients/**` on all three studio rules and the claim that none load during harness work. |
| `ai-docs/anthropic/model-config.md` | 2026-07-28 | Effort levels are model-dependent (l.446). Grounds the roster's effort column against `model-selection.md`'s table. |
| `ai-docs/anthropic/blog/html-artifacts-workflows.md` | 2026-07-21 | The two-way interactive page and copy-as-prompt loop that `client-artifacts.md` inherits. Narrowed at round 1: the four per-phase page-pattern mappings are **project decisions**, not claims this article grounds. |

### Command frontmatter — grounded in the repo's own reference

`ai-docs/anthropic/commands.md` mirrors the *built-in* slash commands only, so the KB has no
page on **custom** slash-command frontmatter. The repo carries its own authority for that
surface, and it is the one the discovery ledger cited all along:

| Reference | Grounds |
| --- | --- |
| `.claude/skills/meta-skills/references/frontmatter.md` | `argument-hint` (l.26), `disable-model-invocation` (l.30), `effort` (l.33), and `hooks` — "YAML hook config (event → matcher → hooks), lifecycle hooks scoped to this artifact only, active while it runs" (l.37). Every command-frontmatter field this plan uses. |
| `.claude/skills/meta-skills/references/command-format.md` | The five-section house template every studio phase command follows. |
| `.claude/skills/meta-skills/evals/evals.json` + `references/evaluation.md` | The eval-suite schema and runner AC16 targets, rather than an invented markdown rubric. |
| `.claude/commands/harness-layer/harness-plan.md:1-13` | A working command-scoped Stop-hook registration in exactly the shape the four gate commands use. |

Round 2 called this a standards violation on the reading that only `ai-docs/` counts. The
fields are grounded — just not in the KB — so `spec-standards.md` #6 was amended in the same
run to accept these checked-in references where the KB has no mirror, and to require saying
so explicitly. Mirroring the official custom-command page via `/harness-layer:kb add` remains
a worthwhile follow-up; it is not a blocker, and `kb-fetcher` was unavailable this session.

### Eval-runner reachability — verified by running it

| Reference | Grounds |
| --- | --- |
| `.claude/skills/meta-skills/scripts/eval.py:142-144` | `skill_dir` is resolved against the **cwd**, and a target with no `SKILL.md` exits 1. Both verified this run by invoking the runner: a repo-root-relative path from the harness directory resolved to `meta-skills/.claude/skills/…` and failed even for a skill that exists, which is why AC16's command uses a harness-relative path inside a `cd` subshell. |
| `.claude/skills/meta-skills/scripts/run_behavior_eval.py:79-89` | The scratch project stages its target into `<root>/.claude/skills/<name>`. A command must live in `.claude/commands/` to resolve as `/studio-layer:<name>`, so no command directory is reachable through this runner — the reason `run_command_evals.py` exists rather than reusing it. |

## Revision Log

- **This run (revision cycle, rounds 3–4).** Self-check before the gate found the AC16 lint
  command could not resolve its target, and that tasks.md still named the `specs/cpo-layer/evals/`
  markdown path round 2 had removed. Codex round 3 then found the commands eval suite had no
  runner at all, the component inventory was only *declared* authoritative, and AC13 contradicted
  its own change-order contract. Round 4 found both round-3 fixes half-done: the inventory was
  signed at P3 but never re-verified at P6, and the new runner omitted the sign-off hook the
  evaluated P2 command registers. All fixed; see the findings ledger.
- **Standards amended.** `spec-standards.md` #2 now requires verifying at draft time that a
  runner a criterion leans on can actually reach its target. Three findings across rounds 2–4
  (R2-F4, R3-F1, R4-F2) shared that single root cause — a named runner that could not resolve,
  stage, or grade what the plan pointed it at.

## Open Questions / Out of Scope

- **Out of scope — Card 10, lesson graduation.** The threshold for promoting a repeated lesson
  into a skill, and whether a client-specific lesson ever leaves that project's folder.
- **Out of scope — Card 11, the design KB.** Mirroring WCAG 2.2, the ARIA Authoring Practices
  Guide, and the platform accessibility guidelines through `kb-fetcher`. Blocked on the P5
  tool answer.
- **Out of scope — Card 12, the first real run.** Which project goes first, and whether run
  one is a paying client or an internal dry run.
- **Out of scope — all development work.** The layer stops at a signed layout handoff.
- **Resolved as a runtime input, not deferred:** which prototype tool P5 drives. Rather than
  leaving it open — which contradicted the plan's own "every decision is locked" claim — the
  P5 command takes the tool as an argument and applies the selection rules in spec.md
  `## Interfaces & Contracts`, recording the choice in the prompt pack. Card 11's KB mirror
  still waits on what the first engagements actually pick.
