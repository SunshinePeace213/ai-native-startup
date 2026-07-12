# Decisions: Destructive-Command Guard Hook

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

A `destructive-guard` PreToolUse hook family on the Bash matcher blocks destructive shell commands before execution. Scope is the user's 15-category `DANGEROUS_PATTERNS` taxonomy plus three additions (WSL `/mnt/<drive>` protected roots, user & account manipulation, obfuscated execution), implemented as one flat rule table where category is per-rule metadata. All recursive-force deletes are denied outright, enforcing the existing AGENTS.md trash policy. Severity is two-tier: unambiguous destruction hard-denies with an agent-readable `BLOCKED / Why / Fix` stderr block (exit 2); context-legitimate patterns (Git Security, `curl | bash`) escalate to the human via `permissionDecision: "ask"`. There is no agent-facing bypass.

## Resolved Decisions

- **Q:** Which destructive-command categories should the guard cover?
  - **A:** The user's 15 categories (Destructive File Operations, Disk Overwrite, Fork Bombs & Resource Exhaustion, Dangerous Permission Changes, System File Overwriting, Format Operations, Critical Process Termination, Remote Code Execution, Environment Manipulation, Cron & Scheduled Tasks, Network Manipulation, History & Log Manipulation, Kernel & System Operations, Symbolic Link Attacks, Git Security) plus three additions accepted during grilling: WSL Windows-drive mounts (`/mnt/c` …) as protected roots, User & Account Manipulation (`userdel`, `passwd root`), and obfuscated execution (`base64 -d | sh`).
  - **Why:** The user supplied the taxonomy as their prior design and asked for a gap/overlap review; the additions close real holes on this WSL2 machine and against trivial rule dodging.
- **Q:** Per-category dicts of patterns (the user's original `DANGEROUS_PATTERNS` shape) or one flat rule table?
  - **A:** One flat table; category is metadata on each rule.
  - **Why:** Overlapping categories (Disk Overwrite vs Format Operations; System File Overwriting vs Symbolic Link Attacks) would force duplicate rules across dicts; a flat table keeps the engine category-agnostic and matches the proven security-scan family structure. Categories survive as the label in every error message.
- **Q:** How strict on recursive-force deletes?
  - **A:** Block ALL `rm` recursive-force spellings regardless of target; fix hint = `mv <target> ~/.Trash/`.
  - **Why:** AGENTS.md already forbids `rm -rf` in prose; the hook enforces the written policy mechanically. Rules out target-based allowlisting for `rm -rf` and the ask-tier middle path for scoped deletes.
- **Q:** Hard-deny everything, or a second tier for context-legitimate patterns?
  - **A:** Two-tier — deny (exit 2 + stderr Why/Fix) and ask (`permissionDecision: "ask"` JSON); Git Security and `curl | bash` live in the ask tier; deny wins when both match.
  - **Why:** Single-tier deny mis-blocks legitimate git recoveries and installer scripts; the ask tier keeps the human in the loop per call without weakening the deny tier. Each rule declares its severity in the table.
- **Q:** Any bypass mechanism?
  - **A:** None agent-facing — no pragma, no inline token, no env kill-switch.
  - **Why:** Anything the agent can type into the command string defeats the guard (unlike security-scan's write-time pragma, which reviews content, not actions). Humans already have the `!` prefix (never passes through hooks) and the ask tier.
- **Q:** What must error messages look like?
  - **A:** Agent-readable and actionable: `[destructive-guard] BLOCKED (<Category>/<rule_id>): <message>` + `Why:` + `Fix:` per matched rule (max 3) on stderr; ask-tier reasons name the category and end "approve only if intended."
  - **Why:** Explicit user requirement — the agent must understand what was blocked and what to do instead, so it self-corrects rather than retrying blindly. The `<Category>/<rule_id>` locator (added reconciling Codex round 1) stands in for HOOK-TESTING.md's `file:line rule` shape, which cannot apply to command inspection; Task 3 codifies that exception in HOOK-TESTING.md.

## Assumptions

- Git ask-tier includes `--force-with-lease` alongside `--force`/`-f` — safer to ask on both; invalidated if force-with-lease pushes become a routine workflow needing zero friction.
- Naive whole-string regex scanning is acceptable: a command merely *mentioning* a pattern (`echo "never run rm -rf /"`) gets blocked. Repo precedent (`block_attribution.py`) accepts the same tradeoff; invalidated if false positives become frequent in practice.
- Only the Bash tool's `command` string is guarded; scripts written to disk and executed indirectly are out of reach (noted as residual risk, not a target).
- `/tmp` is NOT a protected root — recursive deletes there still trip the universal `rm -rf` rule, but `find /tmp -delete` passes; invalidated if /tmp abuse shows up.
- `alias rm=…` inside a single Bash tool call is NOT blocked — each tool call is a fresh shell, so a non-persisted alias is inert; only persistent sabotage (profile writes) is in the Environment Manipulation scope.
- Environment Manipulation ask-tier scope is profile/`/etc/environment` writes and `LD_PRELOAD` injection only — ordinary `export FOO=bar` must never match.
- Issue priority P1, type `feat`, plan name `destructive-command-guard` (accepted at sign-off).

### Accepted regex-precision limitations (Codex impl-review rounds 2–3, user-approved at the over-cap gate)

These are direct consequences of the "no shell-AST parsing / high-precision regex over the raw command string" non-goal; the command is normalized only for syntactic quoting, not fully interpreted. Accepted rather than chased into interpreter emulation:

- **Quote normalization is quote-state-aware, not a full shell parser.** A single left-to-right pass drops syntactic single/double quotes, keeps an opposite-type quote as a literal, and neutralizes redirect/pipe/separator operators (`<>|&;`) that appear *inside* quotes; command substitution (`$(…)`, backticks) stays active inside double quotes. This catches the realistic quoted-evasion forms (`rm "-rf"`, `rm -'r'f`, `mv /"etc"`, `dd of=/dev/"sda"`) while leaving benign quoted literals alone. Backslash escaping (`rm -rf\ x`) and nested command substitution are out of scope.
- **`mv <src> /dev/null` followed by a shell redirection or a space-comment** (`mv f /dev/null 2>err`, `mv f /dev/null </in`, `mv f /dev/null # x`) is a known false negative: the `/dev/null` destination is anchored to the end of its command segment to keep the matcher linear-time (a prior redirect-aware tail caused catastrophic backtracking that could hang the hook). Plain `mv <src> /dev/null` is still denied; the redirect-suffixed forms are exotic and out of scope.
- **A path immediately preceded by a substitution closer** (`${...}`, `$(...)`, backticks) is treated as beginning at an argument boundary and matched conservatively — so `$(cmd)/etc/passwd` is denied even when the substitution is non-empty (a deliberate false positive in the safe direction, matching the empty-expansion danger case).

## Open Questions / Out of Scope

- **Out of scope:** commands the user runs with the `!` prefix (hooks never see them; intended human bypass).
- **Out of scope:** shell-AST parsing / interpreter emulation — regex over the command string only.
- **Out of scope:** runtime resource monitoring (cgroups, ulimits) — static inspection only.
- **Out of scope:** non-Bash tools; PowerShell/Windows-native commands.
- **Out of scope:** changes to `permissions` config or other hook families.
- **Open question (follow-ups, future plan):** container/VM destruction rules (`docker system prune -af --volumes`, `docker rm -f $(docker ps -aq)`), database drops (`DROP DATABASE`, `dropdb`), `journalctl --vacuum-*`, `git branch -D` / `git stash clear` — owner: @SunshinePeace213, revisit after the guard has field time.

### Follow-ups (Codex advisories — recorded, not fixed in this run)

- [ ] Round 1: the claim that `!`-prefixed user commands bypass hooks is not grounded by a cached KB doc — `/kb add` the official interactive-mode page and cite it here.

## KB References

- `ai-docs/anthropic/hooks-guide.md` (fetched 2026-07-05) — PreToolUse exit-code semantics (exit 2 = deny with stderr fed back to Claude; exit 0 = no decision), `permissionDecision` allow/deny/ask JSON, multi-hook merge order (most restrictive wins), "don't mix exit 2 with JSON output".
- `ai-docs/anthropic/hooks.md` (fetched 2026-07-05) — PreToolUse event schema and matcher fields; consulted for the event surface.
- **Conflict surfaced:** the two docs disagree on exit-code semantics — hooks.md's exit-code table (documenting the newer `hooks.json` config format, which this repo does not use) says exit 2 = "validation error, execution continues", while hooks-guide.md says exit 2 = block. This plan follows hooks-guide.md because it matches the repo's production-proven behavior (`block_attribution.py` denies via exit 2 today) and the repo's settings.json wiring format. Flagged for cleanup at the next `/harness-layer:kb` sync.
- No gap-fill was needed; both docs are 7 days old (< 30-day staleness threshold).
