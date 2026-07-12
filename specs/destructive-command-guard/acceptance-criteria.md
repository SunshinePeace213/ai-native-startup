# Acceptance Criteria: Destructive-Command Guard Hook

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — Every recursive-force delete spelling (`rm -rf x`, `rm -fr x`, `rm -r -f x`, `rm --recursive --force x`, `sudo rm -rf x`, and a compound-command variant) exits 2 with stderr containing `BLOCKED (Destructive File Operations/rm-recursive-force)` and the `mv <target> ~/.Trash/` fix hint; `rm file.txt` and `rm -f single.txt` exit 0 silently.
- **AC2** — Every deny-tier rule in spec.md's rule table has at least one fixture command that exits 2 with `BLOCKED (<its category>/<its rule_id>)`, a `Why:` line, and a `Fix:` line on stderr — including the protected-root normalization forms (`rm -r /etc`, `rm -r /etc/`, `rm -R ~/`, `rm -r $HOME` blocked; `rm -r ./etc`, `rm -r /etc/nginx` allowed) and BOTH fork-bomb forms (`:(){ :|:& };:` and `f(){ f | f & }; f`).
- **AC3** — Every ask-tier rule in spec.md's rule table (chmod-777-recursive, pipe-to-shell, profile-write, ld-preload, git-force-push, git-hard-reset, git-clean-force, git-history-rewrite, git-remote-delete) has at least one positive fixture that exits 0 and prints JSON to stdout with `hookSpecificOutput.permissionDecision == "ask"` and a `permissionDecisionReason` naming that rule's category.
- **AC4** — A benign matrix of at least 12 commands (`ls -la`, `git status`, `uv run pytest`, `bun install`, `rm file.txt`, `dd if=/dev/zero of=./f bs=1M count=10`, `echo hi > /dev/null`, `chmod 755 script.sh`, `export FOO=bar`, `mkdir -p a/b`, `f(){ echo hi; }; f`, `head -c 100 /dev/zero`) all exit 0 with no stdout decision and no `BLOCKED` on stderr.
- **AC5** — Fail-open contract: empty stdin, malformed JSON, `tool_name != "Bash"`, and a missing/non-string `command` each exit 0 with no decision output.
- **AC6** — Deny precedence: a command matching both tiers (`git reset --hard && rm -rf /`) exits 2 (no ask JSON).
- **AC7** — `.claude/settings.json` binds `destructive-guard/block_destructive.py` under `PreToolUse` → `Bash`, and `test_wiring.py`'s `EXPECTED_BINDINGS` pins that row; all wiring tests pass.
- **AC8** — The per-feature suite passes in default parallel mode: `uv run pytest tests/harness-layer/hooks/destructive-guard`.
- **AC9** — HARNESS-LAYER.md documents the guard (deny/ask tiers, no agent bypass, `!` prefix relief valve), HOOK-TESTING.md carries the command-guard exception to the `file:line rule` exit-2 contract, and the AGENTS.md hooks bullet mentions the guard.
- **AC10** — The full suite passes from the repo root: `uv run pytest`.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `uv run pytest tests/harness-layer/hooks/destructive-guard` — verifies AC1–AC6, AC8. A pass is zero failures with the deny/allow/ask/fail-open parametrized matrices all green.
- `uv run pytest tests/harness-layer/hooks/test_wiring.py` — verifies AC7. A pass means the bindings Counter matches exactly (no missing, no duplicate registration).
- `uv run pytest` — verifies AC10. Full-suite green from the repo root.
- `echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/x"}}' | uv run --script .claude/hooks/destructive-guard/block_destructive.py; echo "exit=$?"` — smoke-checks AC1: prints the `BLOCKED (Destructive File Operations/rm-recursive-force)` block with `Why:`/`Fix:` lines to stderr and `exit=2`.
- `echo '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | uv run --script .claude/hooks/destructive-guard/block_destructive.py; echo "exit=$?"` — smoke-checks AC3: stdout is the `permissionDecision: "ask"` JSON and `exit=0`.
- `echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | uv run --script .claude/hooks/destructive-guard/block_destructive.py; echo "exit=$?"` — smoke-checks AC4: no output, `exit=0`.
- `echo 'not json' | uv run --script .claude/hooks/destructive-guard/block_destructive.py; echo "exit=$?"` — smoke-checks AC5: fail-open, `exit=0`.
- `grep -n "destructive-guard" HARNESS-LAYER.md AGENTS.md HOOK-TESTING.md` — verifies AC9: all three files mention the guard (HOOK-TESTING.md via the command-guard exception).
