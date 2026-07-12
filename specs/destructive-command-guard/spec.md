# Spec: Destructive-Command Guard Hook

- **Owner:** @SunshinePeace213
- **Status:** Drafted for Review
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). If round 2 is still changes-requested, the over-cap gate records the exit
       status in ## Codex Verification — approved | accepted-with-unverified-fixes | needs-human. One value only. -->

## Task Description

AI agents in this repo execute shell commands autonomously through the Bash tool. A single destructive command — `rm -rf` on a system or home directory, a disk overwrite (`dd of=/dev/sda`, `mkfs`), a fork bomb, an unbounded resource-exhaustion fill, or a system-state change (`shutdown`, `kill -9 -1`) — can destroy the machine, the Windows host filesystem (this box is WSL2, so `/mnt/c` is the Windows drive), or hours of work. Nothing intercepts these before execution today; the AGENTS.md safe-delete policy (`mv <target> ~/.Trash/` instead of `rm -rf`) is prose-only and unenforced.

Build a `destructive-guard` PreToolUse hook family on the Bash matcher that inspects `tool_input.command` against a flat rule table covering 15 agreed threat categories plus three additions (WSL drive-mount protected roots, user & account manipulation, obfuscated execution). Rules have two severities: **deny** (exit 2 with an agent-readable `BLOCKED / Why / Fix` stderr block) and **ask** (`permissionDecision: "ask"` JSON so the human approves per call). The hook is pure inspection — it never executes anything — and fails open on any plumbing problem.

## Objective

When the build is complete, every deny-tier destructive command issued through the Bash tool is cancelled before execution with a fix hint the agent can act on, every ask-tier command routes to the human for a per-call decision, benign commands pass untouched, and the contract is pinned by passing tests in `tests/harness-layer/hooks/destructive-guard/` plus a wiring-matrix row.

## Non-Goals

- No blocking of commands the user types with the `!` prefix — those never pass through hooks and are the intended human bypass.
- No shell-AST parsing or interpreter emulation — high-precision regex over the raw command string, matching repo precedent (`block_attribution.py`).
- No runtime resource monitoring (cgroups, ulimits, process supervision) — static command inspection only.
- No coverage of non-Bash tools, or of scripts the agent writes to disk and executes indirectly.
- No PowerShell/Windows-native command coverage — WSL bash is the only shell surface here.
- No agent-facing bypass of any kind (no pragma, no inline token, no env kill-switch).
- No changes to the existing `permissions` config or other hook families.

## Problem Statement

The repo already guards *content* the agent writes (security-scan family) and *attribution* in git commands (`block_attribution.py`), but nothing guards against the agent *executing* a destructive command. Autonomous background jobs and parallel builders widen the blast radius: one hallucinated cleanup command can take out the WSL distro or the mounted Windows drive. The risk is asymmetric — a false positive costs one retried tool call, a false negative can cost the machine — so a pre-execution guard is worth building now, before the harness scales to more parallel agents.

## Solution Approach

One new hook family, `.claude/hooks/destructive-guard/`, mirroring the proven security-scan structure:

- **`_common.py`** — importable library (no shebang/PEP 723 marker): a frozen `Rule` dataclass (`rule_id`, `category`, `severity`, `pattern`, `message`, `fix_hint`), the `PROTECTED_ROOTS` / `CRITICAL_FILES` constants, the single flat `RULES` table, fail-open stdin plumbing (mirrored from the family convention), and `evaluate(command) -> (deny_matches, ask_matches)`.
- **`block_destructive.py`** — PEP 723 `uv run --script` entrypoint: parse the payload; only act when `tool_name == "Bash"` and `tool_input.command` is a non-empty string; evaluate all rules; deny matches win — print up to 3 matched rules as `BLOCKED (<Category>/<rule_id>): <message>` + `Why:` + `Fix:` lines to stderr and exit 2; else if ask matches, print `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "..."}}` to stdout and exit 0; else exit 0 silently. Any unexpected exception notes to stderr and exits 0 (fail-open).

A flat rule table (category as per-rule metadata) was chosen over the user's original per-category dict-of-lists: overlapping categories (Disk Overwrite vs Format Operations; System File Overwriting vs Symlink Attacks) otherwise force duplicate rules, and the engine stays category-agnostic. The main alternative considered — `permissions.deny` rules in settings.json — lost because prefix matching cannot catch flag reordering (`rm -fr`, `rm -r -f`), compound commands, or obfuscation, and provides no agent-readable fix hints.

### Rule table (canonical starting set)

The builder implements exactly these rules; every rule gets at least one blocked-fixture and one near-miss-allowed-fixture test. Patterns must use word boundaries and must not be anchored to string start (so `sudo`/`doas`/`env`/`nohup`/`timeout`/`nice` prefixes and compound commands still match).

**Protected roots** (constant): `/`, `/bin`, `/boot`, `/dev`, `/etc`, `/home`, `/lib`, `/lib32`, `/lib64`, `/opt`, `/proc`, `/root`, `/sbin`, `/srv`, `/sys`, `/usr`, `/var`, `/mnt/<single-letter>` (WSL Windows drive mounts), `~`, `$HOME` (also quoted `"$HOME"` and braced `${HOME}`). **Normalization rule:** a target matches a protected root when it is the bare root, the root with a single trailing slash, or the root with trailing `/*` — e.g. `/etc`, `/etc/`, and `/etc/*` all match; `~`, `~/`, `$HOME`, and `$HOME/` all match. A deeper sub-path (`/etc/nginx`, `~/projects`) is deliberately NOT a protected-root match — the universal `rm-recursive-force` rule already covers all `-rf` forms there, and root-targeting rules stay high-precision. `/tmp` is deliberately NOT a protected root (see decisions.md).

**Critical files** (constant): `/etc/passwd`, `/etc/shadow`, `/etc/group`, `/etc/sudoers` (+ `/etc/sudoers.d/*`), `/etc/fstab`, `/etc/hosts`, `/etc/ssh/sshd_config`, `/etc/cron*`, `/boot/*`.

| rule_id | Category | Severity | Blocks (examples) |
| --- | --- | --- | --- |
| rm-recursive-force | Destructive File Operations | deny | any `rm` with recursive+force in any spelling/order: `rm -rf x`, `rm -fr x`, `rm -r -f x`, `rm --recursive --force x`. Fix hint: `mv <target> ~/.Trash/` (AGENTS.md policy) |
| rm-recursive-protected | Destructive File Operations | deny | `rm -r`/`-R` (even without `-f`) targeting a protected root per the normalization rule: `rm -r /etc`, `rm -r /etc/`, `rm -R ~/`, `rm -r $HOME`. Near-miss allowed: `rm -r ./etc`, `rm -r /etc/nginx` |
| find-delete-protected | Destructive File Operations | deny | `find <protected-root> … -delete` or `-exec rm` |
| mv-protected-root | Destructive File Operations | deny | `mv` whose source is a bare protected root (`mv /etc /tmp/x`) or whose destination is `/dev/null` |
| dd-to-block-device | Disk Overwrite Operations | deny | `dd … of=/dev/sdX\|hdX\|vdX\|nvme…\|mmcblk…\|xvdX` |
| redirect-to-block-device | Disk Overwrite Operations | deny | shell redirect onto a raw block device: `> /dev/sda` (never matches `/dev/null`/`/dev/stdout`) |
| shred-device | Disk Overwrite Operations | deny | `shred` targeting `/dev/*` |
| mkfs | Format Operations | deny | any `mkfs` / `mkfs.*` invocation |
| wipe-partition | Format Operations | deny | `wipefs`, `blkdiscard`, `sgdisk -Z`/`--zap-all` |
| fork-bomb | Fork Bombs & Resource Exhaustion | deny | exactly two forms: (a) the classic literal `:(){ :\|:& };:` tolerant of arbitrary whitespace; (b) a function definition whose body pipes the function name into itself AND backgrounds it — regex semantics `(\w+\|:)\s*\(\s*\)\s*\{[^}]*\1\s*\|\s*\1[^}]*&[^}]*\}`. Near-miss allowed: ordinary function defs (`f(){ echo hi; }; f`) and recursion without both `\|` and `&` |
| unbounded-fill | Fork Bombs & Resource Exhaustion | deny | `cat /dev/zero >`, `yes >` a file/device, `dd if=/dev/zero\|/dev/urandom` with NO `count=` bound writing anywhere but `/dev/null` |
| memory-exhaust | Fork Bombs & Resource Exhaustion | deny | exactly two forms: (a) `tail` reading `/dev/zero` with any flag order (`tail /dev/zero`, `tail -f /dev/zero`); (b) command substitution capturing an unbounded generator — `$(cat /dev/zero)`, `$(yes)`, and backtick equivalents. Near-miss allowed: `head -c 100 /dev/zero`, `yes \| head -5` |
| chmod-recursive-protected | Dangerous Permission Changes | deny | `chmod -R` on a protected root (`chmod -R 777 /`) |
| chown-recursive-protected | Dangerous Permission Changes | deny | `chown -R` on a protected root |
| chmod-777-recursive | Dangerous Permission Changes | ask | `chmod -R 777` on any non-protected target — occasionally intended, world-writable is usually a mistake |
| overwrite-critical-file | System File Overwriting | deny | `>`/`>>`/`tee` onto a critical file (`> /etc/passwd`, `tee /etc/sudoers`) |
| truncate-critical-file | System File Overwriting | deny | `truncate` on a critical file |
| kill-all | Critical Process Termination | deny | `kill`/`killall`/`pkill` with `-9`/`-KILL` aimed at `-1`, PID 1, `init`, or `systemd` |
| pipe-to-shell | Remote Code Execution | ask | `curl\|wget … \| sh\|bash\|zsh`, `sh <(curl …)`, `bash -c "$(curl …)"`, `eval "$(curl …)"` |
| obfuscated-exec | Remote Code Execution | deny | `base64 -d\|--decode … \| sh\|bash`, `xxd -r … \| sh` — decode-then-execute has no legitimate agent use |
| profile-write | Environment Manipulation | ask | `>`/`>>`/`tee` onto `~/.bashrc`, `~/.profile`, `~/.bash_profile`, `~/.zshrc`, `/etc/profile`, `/etc/environment`, `/etc/bash.bashrc` |
| ld-preload | Environment Manipulation | ask | `LD_PRELOAD=` assignment injecting a `.so` into a command |
| crontab-wipe | Cron & Scheduled Tasks | deny | `crontab -r` (irreversibly wipes the user's crontab) |
| cron-write | Cron & Scheduled Tasks | deny | writes/redirects into `/etc/cron*` |
| firewall-flush | Network Manipulation | deny | `iptables -F`/`--flush`, `nft flush ruleset`, `ufw disable` |
| iface-down | Network Manipulation | deny | `ip link set <dev> down`, `ifconfig <dev> down` |
| history-wipe | History & Log Manipulation | deny | `history -c`; `rm`/`truncate`/`>` on `~/.bash_history`, `~/.zsh_history` |
| log-wipe | History & Log Manipulation | deny | `rm`/`truncate`/`>` on `/var/log/*` |
| power-state | Kernel & System Operations | deny | `shutdown`, `reboot`, `halt`, `poweroff`, `init 0\|6`, `telinit 0\|6`, `systemctl poweroff\|reboot\|halt\|suspend\|hibernate` |
| kernel-modules | Kernel & System Operations | deny | `insmod`, `rmmod`, `modprobe -r` |
| kernel-mem | Kernel & System Operations | deny | writes to `/dev/mem`, `/dev/kmem`; `sysctl -w`; redirects into `/proc/sys/*` |
| symlink-critical | Symbolic Link Attacks | deny | `ln -s`/`-sf` placing or pointing a link at a critical file or `/dev/null` over a critical path |
| git-force-push | Git Security | ask | `git push --force`/`-f` (including `--force-with-lease`) |
| git-hard-reset | Git Security | ask | `git reset --hard` |
| git-clean-force | Git Security | ask | `git clean -f` and combinations (`-fd`, `-fdx`) |
| git-history-rewrite | Git Security | ask | `git filter-branch`, `git filter-repo` |
| git-remote-delete | Git Security | ask | `git push <remote> --delete <branch>`, `git push <remote> :<branch>` |
| account-destroy | User & Account Manipulation | deny | `userdel`, `groupdel`, `passwd root`, `passwd -d`, `usermod -L root` |

### Message contract (agent-readable, locked by grilling)

Deny (stderr, exit 2) — up to 3 matched rules, each:

```text
[destructive-guard] BLOCKED (<Category>/<rule_id>): <message>
Why: <one-line danger explanation>
Fix: <safe alternative, or "ask the user to run it themselves via the ! prefix">
```

The `<Category>/<rule_id>` header is the diagnostic locator. HOOK-TESTING.md's exit-2 contract demands `file:line rule` — that shape fits file-scanning hooks, but a command guard inspects a command string, which has no file or line. Task 3 codifies the command-guard exception in HOOK-TESTING.md: command-inspection hooks carry `(<Category>/<rule_id>)` in place of `file:line rule`. (`block_attribution.py` already exits 2 without `file:line`; this amendment legitimizes the existing precedent rather than inventing a new one.)

Ask (stdout JSON, exit 0):

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
 "permissionDecisionReason": "[destructive-guard] <Category>: <message> — approve only if intended."}}
```

## Requirements & Decisions

- **Block ALL recursive-force deletes, any spelling** — enforces the existing AGENTS.md safe-delete policy mechanically; the fix hint points to `mv <target> ~/.Trash/`.
- **Two-tier severity** — unambiguous destruction hard-denies (exit 2 + stderr fed to the agent); context-legitimate patterns (Git Security, `curl | bash`) emit `permissionDecision: "ask"` so the human decides per call. Deny always wins over ask when both match one command.
- **No agent-facing bypass** — a bypass typable into the command string defeats the guard; the human's `!` prefix and the ask tier are the only relief valves.
- **One flat rule table, category as metadata** — kills duplicate rules across overlapping categories and keeps the engine category-agnostic; every rule carries an agent-readable message + fix hint.
- **Fail-open, stateless, stdlib-only** — plumbing problems must never wedge an unrelated tool call (exit 0); the guard inspects, it never executes or shells out.

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #25
- **Branch:** feat/25-destructive-command-guard
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/destructive-command-guard
- **Review profile:** kb-grounded
- **PR:** <#M — filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

- `.claude/hooks/block_attribution.py` — the direct precedent: PreToolUse Bash guard with fail-open stdin plumbing and exit-2 deny; copy its plumbing posture.
- `.claude/hooks/security-scan/_common.py` — the family pattern to mirror: frozen `Rule` dataclass, flat rule table, `note()` stderr convention, fail-open helpers.
- `.claude/settings.json` — gains the new hook command in the existing `PreToolUse` → `Bash` matcher block.
- `tests/harness-layer/hooks/test_wiring.py` — `EXPECTED_BINDINGS` gains the `("destructive-guard/block_destructive.py", "PreToolUse", ("Bash",)): 1` row.
- `tests/harness-layer/hooks/conftest.py` — provides the shared `run_hook` launcher and `load_hook_module` fixture the tests must use (HOOK-TESTING.md).
- `HOOK-TESTING.md` — the exit-2 diagnostics rule gains the command-guard exception: command-inspection hooks carry `(<Category>/<rule_id>)` instead of `file:line rule`.
- `HARNESS-LAYER.md` — gains a short destructive-guard section (behavior, severities, no-bypass, `!` prefix relief valve).
- `AGENTS.md` — the Harness Development hooks bullet gains a half-line mention of the guard.

### New Files

- `.claude/hooks/destructive-guard/_common.py` — Rule dataclass, constants, RULES table, plumbing, `evaluate()`.
- `.claude/hooks/destructive-guard/block_destructive.py` — PEP 723 entrypoint wiring evaluate() to the deny/ask/silent output paths.
- `tests/harness-layer/hooks/destructive-guard/test_block_destructive.py` — contract tests: per-category blocked fixtures, near-miss allowed fixtures, ask-tier JSON, fail-open, precedence.

## Edge Cases

- **Empty, malformed, or absent stdin payload** → exit 0 silently (fail-open); unexpected I/O errors note to stderr, still exit 0.
- **`tool_name != "Bash"` or missing/non-string `command`** → exit 0, no output.
- **Compound commands** (`cd / && rm -rf *`, `;`, `||`, pipes) → whole-string scan catches embedded segments; patterns are never anchored to string start.
- **Wrapper prefixes** (`sudo`, `doas`, `env X=1`, `nohup`, `timeout 5`, `nice`, `xargs`) → still match via word-boundary patterns.
- **`/dev/null` / `/dev/stdout` redirects** → never match device or fill rules.
- **Bounded `dd`** (`dd if=/dev/zero of=./fixture bs=1M count=10`) → allowed; `dd` onto a block device denied regardless of `count=`.
- **Command merely *mentioning* a pattern in prose** (`echo "never run rm -rf /"`) → blocked; accepted precision tradeoff (same posture as `block_attribution.py`), the fix hint tells the agent to use the Write tool for content.
- **Deny + ask both matching one command** (`git reset --hard && rm -rf /`) → deny wins, exit 2.
- **Oversized command string** → scan the first 64 KB and note truncation to stderr; never raise.
- **Concurrent tool calls / parallel sessions** → guard is stateless (no state files), so parallel-safe by construction.
- **`uv` unavailable or hook crashes at spawn** → Claude Code treats a non-2 failure as non-blocking and the action proceeds (KB: hooks-guide); the guard is defense-in-depth, not a sandbox — record as residual risk, do not fight it.

## Red Flags

<anti-patterns signalling the plan is being skipped or scope is drifting. Keep these standing examples; add task-specific ones:>

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Adding any agent-usable bypass (pragma, inline token, env var read from the command string)
- The guard executing or shelling out to anything — it must be pure inspection, stdlib-only
- Loosening a pattern until benign dev commands (`uv run pytest`, `bun install`, `git status`) get blocked
- Committing a rule without both a blocked fixture and a near-miss allowed fixture
- Raising the global pytest timeout to accommodate a slow test

## Notes

- No new dependencies — stdlib only, per the hook-family convention.
- The rule table is intentionally the canonical starting set, not a ceiling: follow-up rules (e.g. `docker system prune -af --volumes`, `DROP DATABASE`, `crontab` edits beyond `-r`) go through a future plan, listed in decisions.md follow-ups.
- The two KB docs disagree on exit-code semantics (see decisions.md `## KB References`); this spec follows hooks-guide.md + the repo's production-proven behavior.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** <approved at round N | accepted-with-unverified-fixes | needs-human>
- **Rejected findings:** <any Codex finding Claude chose not to act on, each with a one-line rationale; "none" if all warranted findings were applied>

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```text
specs/destructive-command-guard/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/destructive-command-guard/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
