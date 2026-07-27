# Implementation Notes: codex-hooks-sync

> Chronological dev log for [spec.md](./spec.md), created from this template at
> `/harness-layer:harness-build` implement start and appended by both
> `/harness-layer:harness-build` and `/harness-layer:harness-review` as the work
> proceeds.
>
> Boundary: per-plan phases, hand-offs, deviations, fixes, and lessons live here.
> Cross-plan one-liners go to `.claude/rules/development-log.md` instead.

## Log

- **2026-07-27 · build start** — Plan resolved to `specs/codex-hooks-sync/`, issue #62,
  worktree `.claude/worktrees/codex-hooks-sync`, review profile `kb-grounded`. Board created with
  9 tasks across 3 phases; T1 (`edited-paths`) is a hard barrier before T2–T5.

## Acceptance Evidence

AC19/AC20. Produced by a real `codex exec` run of `scripts/codex-hook-probe.sh` — not a pytest run.
Every hook fails open, so only a positively observed block counts: each case greps the session output
for that hook's own evidence string and fails when it is absent.

- **Probe:** `scripts/codex-hook-probe.sh` (executable, deliberately outside `.claude/hooks/`)
- **Codex CLI:** `codex-cli 0.145.0`
- **Model / effort:** `gpt-5.6-luna` / `low`
- **Date:** 2026-07-27
- **Result:** `bash scripts/codex-hook-probe.sh` → exit 0, **9 passed, 0 failed**. Run three times
  back to back with the same result and no leftover scratch dir, temp repo, or session-state file —
  re-running is idempotent.

### One line per mirrored hook

| Mirrored entrypoint | Trigger driven | Observed | Verdict |
| --- | --- | --- | --- |
| `block_attribution.py` | `git log -1 --format='<Claude trailer>'` | `PreToolUse Blocked` + `[block_attribution] Blocked: this git/gh command contains a 'Co-Authored-By: Claude ...' trailer` | **PASS** |
| `destructive-guard/block_destructive.py` (deny tier) | recursive force delete of a scratch dir | `PreToolUse Blocked` + `BLOCKED (Destructive File Operations/rm-recursive-force)`; target still on disk | **PASS** |
| `destructive-guard/block_destructive.py` (ask tier → deny) | `chmod -R 777 junkdir` | `PreToolUse Blocked` + `BLOCKED (Dangerous Permission Changes/chmod-777-recursive)` + the host-neutral Codex fix line, no `permissionDecision` anywhere; target not world-writable | **PASS** |
| `sensitive-files/bash_guard.py` | Bash read of a cataloged env file | `PreToolUse Blocked` + `Blocked: '.env' matches sensitive category 'Environment files'` | **PASS** |
| `sensitive-files/file_guard.py` (`*** Add File:`) | `apply_patch` creating a cataloged env file | `PreToolUse Blocked` naming the absolute target; file never created | **PASS** |
| `sensitive-files/file_guard.py` (`*** Move to:`) | `apply_patch` renaming `notes.md` onto a cataloged env file | `PreToolUse Blocked` on the **rename target**, not the innocuous source; `notes.md` still in place and the target never created | **PASS** |
| `security-scan/post_write_scan.py` | `apply_patch` writing a runtime-assembled AWS-key fixture | `PostToolUse Blocked` + `creds.txt:1 aws-access-key AWS access key ID` | **PASS** |
| `auto-format/python.py` | `apply_patch` writing `x=1` plus an undefined name | `PostToolUse Blocked` + `unformatted_probe.py:2:7: F821 Undefined name`; `x=1` rewritten to `x = 1` on disk | **PASS** |
| `auto-format/js_ts.py`, `auto-format/data.py`, `auto-format/markdown.py` | no separate session | asserted `saw 5` PostToolUse/apply_patch launches — the four formatters plus the scanner — so each received the envelope and self-filtered on extension rather than never running | **PASS (launch observed)** |
| `security-scan/track_bash_writes.py` | benign Bash command | `hook: PostToolUse` on the Bash event; `tracked` populated in the session state file | **PASS** |
| `security-scan/session_baseline.py` | session start | `hook: SessionStart` in every session; `baseline` / `last_head` written to session state | **PASS** |
| `security-scan/stop_sweep.py` | end of turn | `hook: Stop` in every session, and `hook: Stop Blocked` in the post-write-scan session where the planted secret survived to the sweep | **PASS** |

### Environment finding — a worktree's `.codex/` is never the layer that runs

The first probe design drove `codex exec` from inside this worktree and **7 of 8 cases failed**.
Cause: Codex resolves the project `.codex/` layer to the **main repository root**, so from
`.claude/worktrees/codex-hooks-sync` it loaded the main checkout's `.codex/hooks.json` — the pre-merge
file with only 2 bindings. Exactly those two hooks fired; the 11 new ones silently did not. Two
further constraints surfaced the same way:

- A project path Codex has not recorded as trusted gets `sandbox: read-only` **and** no project hook
  layer at all. Passing `-s workspace-write` explicitly restores both.
- `-c projects."<path>".trust_level="trusted"` does not grant that trust, and a path containing dots
  is mishandled by the `-c` dotted-path parser — hence the dot-free `mktemp` template.

The probe therefore builds a throwaway git repo under `$TMPDIR` (a real `.git` directory, dot-free
path) holding copies of `.claude/hooks/` and `.codex/`, plus `pyproject.toml` / `uv.lock` and a
symlink to this checkout's `.venv` so `auto-format/python.py` finds ruff. A **preflight case**
asserts the 13-binding layer is live — 3 PreToolUse/Bash launches plus SessionStart, PostToolUse and
Stop — and aborts before burning further sessions if it is not. Without it a single environmental
fault reads as eight hook failures.

Two behaviours worth recording from the same runs: Codex accepts the `HARNESS_HOOK_HOST=codex` env
prefix on a registered `command` (the ask-tier case proves the variable reached the hook), and its
built-in exec policy rejects `rm -f`-style commands independently of the hooks — visible only when
the guard is absent, and harmless once it is registered.

### Raw output

```text
codex-hook-probe
codex version : codex-cli 0.145.0
repo root     : /home/ringo/ai-native-startup/.claude/worktrees/codex-hooks-sync
probe repo    : /tmp/codexhookprobeQ5cZsq/repo
model / effort: gpt-5.6-luna / low

=== hook-layer — preflight: .codex/hooks.json is live ===
codex exit 0, session 019fa3b3-3fbc-7fc0-b61d-f1f1d2d8a41c
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | hook: PreToolUse
  | hook: PreToolUse
  | hook: PreToolUse Completed
  | hook: PreToolUse Completed
  | hook: PreToolUse Completed
  | hook: PostToolUse
  | hook: PostToolUse Completed
  | hook: Stop
  | hook: Stop Completed
  ok   all three PreToolUse/Bash hooks launched (saw 3)
  ok   SessionStart fired (security-scan/session_baseline.py)
  ok   PostToolUse/Bash fired (security-scan/track_bash_writes.py)
  ok   Stop fired (security-scan/stop_sweep.py)
PASS  preflight: .codex/hooks.json is live

=== attribution — block_attribution.py ===
codex exit 0, session 019fa3b3-60ef-7811-8ec1-40e20a0f4a78
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | hook: PreToolUse
  | hook: PreToolUse
  | 2026-07-27T13:11:14.660398Z ERROR codex_core::tools::router: error=Command blocked by PreToolUse hook: [block_attribution] Blocked: this git/gh command contains a 'Co-Authored-By: Claude ...' trailer.
  | hook: PreToolUse Blocked
  | hook: PreToolUse Completed
  | hook: PreToolUse Completed
  | hook: Stop
  | hook: Stop Completed
  ok   block_attribution denial on stderr
  ok   Codex reported PreToolUse Blocked
PASS  block_attribution.py

=== destructive-deny — block_destructive.py (deny tier) ===
codex exit 0, session 019fa3b3-8715-7702-9fd0-4052a76cd97a
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | hook: PreToolUse
  | hook: PreToolUse
  | 2026-07-27T13:11:25.615003Z ERROR codex_core::tools::router: error=Command blocked by PreToolUse hook: [destructive-guard] BLOCKED (Destructive File Operations/rm-recursive-force): recursive force delete (rm -r + -f, any spelling)
  | Why: rm -rf permanently erases directories and their contents with no undo, and one bad path can wipe the working tree or the WSL/Windows drive.
  | Fix: mv <target> ~/.Trash/  (AGENTS.md safe-delete policy). Command: rm -rf junkdir
  | hook: PreToolUse Completed
  | hook: PreToolUse Blocked
  | hook: PreToolUse Completed
  | hook: Stop
  | hook: Stop Completed
  ok   deny-tier rule rm-recursive-force fired
  ok   Codex reported PreToolUse Blocked
  ok   target junkdir/ still on disk (command never ran)
PASS  block_destructive.py (deny tier)

=== destructive-ask — block_destructive.py (ask tier → deny) ===
codex exit 0, session 019fa3b3-ab64-7f11-ba43-5492d22c7db9
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | hook: PreToolUse
  | hook: PreToolUse
  | 2026-07-27T13:11:33.597523Z ERROR codex_core::tools::router: error=Command blocked by PreToolUse hook: [destructive-guard] BLOCKED (Dangerous Permission Changes/chmod-777-recursive): recursive chmod 777 (world-writable) on a non-protected target
  | Why: 0777 makes every file world-writable, which is almost always a security mistake rather than the intent.
  | Fix: Use the least-privilege mode the task needs (e.g. 755 for dirs, 644 for files). Ask the user to run this themselves if world-writable is truly needed.. Command: chmod -R 777 junkdir
  | hook: PreToolUse Completed
  | hook: PreToolUse Blocked
  | hook: PreToolUse Completed
  | hook: Stop
  | hook: Stop Completed
  ok   ask-tier rule chmod-777-recursive denied under Codex
  ok   host-neutral Codex fix line surfaced
  ok   no ask JSON leaked to stdout
  ok   Codex reported PreToolUse Blocked
  ok   junkdir/ not world-writable (command never ran)
PASS  block_destructive.py (ask tier → deny)

=== bash-guard — sensitive-files/bash_guard.py ===
codex exit 0, session 019fa3b3-c78d-7d63-a5c7-cf3fc8e31c3e
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | hook: PreToolUse
  | hook: PreToolUse
  | 2026-07-27T13:11:42.095140Z ERROR codex_core::tools::router: error=Command blocked by PreToolUse hook: Blocked: '.env' matches sensitive category 'Environment files'
  | hook: PreToolUse Completed
  | hook: PreToolUse Completed
  | hook: PreToolUse Blocked
  | hook: Stop
  | hook: Stop Completed
  ok   bash_guard denied the sensitive read
  ok   Codex reported PreToolUse Blocked
PASS  sensitive-files/bash_guard.py

=== file-guard-write — sensitive-files/file_guard.py (Add File) ===
codex exit 0, session 019fa3b3-fdf7-7611-928f-502a35f590a2
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | 2026-07-27T13:11:54.398846Z ERROR codex_core::tools::router: error=Command blocked by PreToolUse hook: Blocked: '/tmp/codexhookprobeQ5cZsq/repo/work/.env' matches sensitive category 'Environment files'
  | hook: PreToolUse Blocked
  | hook: Stop
  | hook: Stop Completed
  ok   file_guard denied the apply_patch write target
  ok   Codex reported PreToolUse Blocked
  ok   .env was never created
PASS  sensitive-files/file_guard.py (Add File)

=== file-guard-rename — sensitive-files/file_guard.py (Move to) ===
codex exit 0, session 019fa3b4-1a2b-7d13-b74f-eb3dffd7fa50
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | 2026-07-27T13:12:02.192124Z ERROR codex_core::tools::router: error=Command blocked by PreToolUse hook: Blocked: '/tmp/codexhookprobeQ5cZsq/repo/work/.env' matches sensitive category 'Environment files'
  | hook: PreToolUse Blocked
  | hook: Stop
  | hook: Stop Completed
  ok   file_guard denied the rename target, not the source
  ok   Codex reported PreToolUse Blocked
  ok   notes.md still in place (rename never happened)
  ok   .env was never created
PASS  sensitive-files/file_guard.py (Move to)

=== post-write-scan — security-scan/post_write_scan.py ===
codex exit 0, session 019fa3b4-3a61-7b50-964f-bfd8ded5dd81
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | hook: PreToolUse Completed
  | hook: PostToolUse
  | hook: PostToolUse
  | hook: PostToolUse
  | hook: PostToolUse
  | hook: PostToolUse
  | 2026-07-27T13:12:10.420903Z ERROR codex_core::tools::router: error=/tmp/codexhookprobeQ5cZsq/repo/work/creds.txt:1 aws-access-key AWS access key ID
  | hook: PostToolUse Completed
  | hook: PostToolUse Completed
  | hook: PostToolUse Completed
  | hook: PostToolUse Completed
  | hook: PostToolUse Blocked
  | hook: Stop
  | hook: Stop Blocked
  | hook: Stop
  | hook: Stop Completed
  ok   scanner reported the aws-access-key rule
  ok   scanner named the finding
  ok   creds.txt written (PostToolUse fires after the write)
PASS  security-scan/post_write_scan.py

=== auto-format — auto-format/python.py ===
codex exit 0, session 019fa3b4-5d9d-7063-bec8-d0a44c3d4be1
  | hook: SessionStart
  | hook: SessionStart Completed
  | hook: PreToolUse
  | hook: PreToolUse Completed
  | hook: PostToolUse
  | hook: PostToolUse
  | hook: PostToolUse
  | hook: PostToolUse
  | hook: PostToolUse
  | 2026-07-27T13:12:23.123556Z ERROR codex_core::tools::router: error=work/unformatted_probe.py:2:7: F821 Undefined name `undefined_symbol`
  | hook: PostToolUse Completed
  | hook: PostToolUse Completed
  | hook: PostToolUse Completed
  | hook: PostToolUse Blocked
  | hook: PostToolUse Completed
  | hook: Stop
  | hook: Stop Completed
  ok   all five PostToolUse/apply_patch hooks launched (saw 5)
  ok   ruff check reported F821 on the apply_patch path
  ok   ruff format rewrote 'x=1' to 'x = 1' on disk
PASS  auto-format/python.py

=== session state written by the security-scan family ===
  019fa3b3-3fbc-7fc0-b61d-f1f1d2d8a41c.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": [], "last_head": ""}
  019fa3b3-60ef-7811-8ec1-40e20a0f4a78.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": [], "last_head": ""}
  019fa3b3-8715-7702-9fd0-4052a76cd97a.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": [], "last_head": ""}
  019fa3b3-ab64-7f11-ba43-5492d22c7db9.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": [], "last_head": ""}
  019fa3b3-c78d-7d63-a5c7-cf3fc8e31c3e.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": [], "last_head": ""}
  019fa3b3-fdf7-7611-928f-502a35f590a2.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": [], "last_head": ""}
  019fa3b4-1a2b-7d13-b74f-eb3dffd7fa50.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": [], "last_head": ""}
  019fa3b4-3a61-7b50-964f-bfd8ded5dd81.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": ["/tmp/codexhookprobe
  019fa3b4-5d9d-7063-bec8-d0a44c3d4be1.json: {"baseline": ["/tmp/codexhookprobeQ5cZsq/repo/.claude", "/tmp/codexhookprobeQ5cZsq/repo/.codex", "/tmp/codexhookprobeQ5cZsq/repo/.venv", "/tmp/codexhookprobeQ5cZsq/repo/pyproject.toml", "/tmp/codexhookprobeQ5cZsq/repo/uv.lock", "/tmp/codexhookprobeQ5cZsq/repo/work"], "tracked": ["/tmp/codexhookprobe

=== summary ===
PASS  preflight: .codex/hooks.json is live — hook-layer
PASS  block_attribution.py — attribution
PASS  block_destructive.py (deny tier) — destructive-deny
PASS  block_destructive.py (ask tier → deny) — destructive-ask
PASS  sensitive-files/bash_guard.py — bash-guard
PASS  sensitive-files/file_guard.py (Add File) — file-guard-write
PASS  sensitive-files/file_guard.py (Move to) — file-guard-rename
PASS  security-scan/post_write_scan.py — post-write-scan
PASS  auto-format/python.py — auto-format

9 passed, 0 failed
```
