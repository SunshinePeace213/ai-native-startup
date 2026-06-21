# Hooks: Deterministic Verification for Artifacts

Hooks are shell commands, prompts, or subagents firing at lifecycle points to enforce rules or verify state. The right answer when correctness needs **deterministic** behavior — not dependent on the model choosing well.

Reference: https://code.claude.com/docs/en/hooks-guide

## When to add hooks

Add hooks when artifact correctness depends on something that:

- **Must always happen** regardless of model memory (linting, audit logging, secrets scanning)
- **Must never happen** regardless of model belief (no `.env` edits, no `rm -rf`, no writes to protected paths)
- **Requires verification against actual state** (tests passing, build green) before "done"

Don't use hooks for guidance the model can follow reliably. Hooks have overhead — processes, JSON parsing, context cost. Use when determinism matters.

## Hook types

Pick the simplest that does the job. Start `command`; escalate as needed.

| Type | When | Cost |
|---|---|---|
| `command` | Deterministic check, exit code sufficient (regex, file existence, lint) | Fast |
| `http` | Same as command, logic in a web service | Network latency |
| `mcp_tool` | Verification exposed by connected MCP server | Depends on server |
| `prompt` | Single LLM judgment call (no tool access) | One Haiku call by default |
| `agent` | Verification needs tool access, multi-step reasoning | Full subagent (most expensive) |

## Where to define

| Location | Scope | When |
|---|---|---|
| `~/.claude/settings.json` | All your projects | Personal preferences |
| `.claude/settings.json` | Single project, VC | Team-shared policies |
| `.claude/settings.local.json` | Single project, gitignored | Personal hooks within shared project |
| **Skill/Subagent frontmatter `hooks:`** | While artifact active | **Default for prompt-architect-built artifacts** |
| Plugin `hooks/hooks.json` | When plugin enabled | Redistributed plugins |

For artifacts created by prompt-architect, frontmatter is usually the right place — hooks travel with the artifact and only fire while it's active (Thariq Tip 9).

## Events most relevant for artifact verification

| Event | Fires when | Common use |
|---|---|---|
| `PreToolUse` | Before tool call | Block unsafe commands; validate inputs |
| `PostToolUse` | After tool call succeeds | Lint edited files; run tests |
| `Stop` | Artifact's main work finishes | Verify task complete |
| `SubagentStop` | Subagent finishes | Validate subagent returned expected output |
| `UserPromptSubmit` | Before Claude processes prompt | Inject context, route by prompt type |
| `SessionStart` | Session begins/resumes | Load env, restore state |

`matcher` field narrows when the event fires. For `PreToolUse`/`PostToolUse`, matcher is a tool name pattern (`Bash`, `Edit|Write`, `mcp__.*`).

## Common patterns

### Pattern 1 — Lint after every edit (skill)

```yaml
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "npx prettier --write \"$CLAUDE_PROJECT_DIR\""
```

### Pattern 2 — Block writes to protected files (subagent)

```yaml
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
```

With `protect-files.sh` exiting 2 when target matches `.env`, `package-lock.json`, `.git/`, etc.

### Pattern 3 — Verify tests before finishing (skill)

```yaml
hooks:
  Stop:
    - hooks:
        - type: prompt
          prompt: "Check if all requested tasks complete and tests passing. If not, respond {\"ok\": false, \"reason\": \"what remains\"}."
```

### Pattern 4 — Audit-log Bash commands (subagent)

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "jq -r '.tool_input.command' >> ~/claude-deploy-audit.log"
```

### Pattern 5 — Block dangerous commands (`/careful` style)

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: |
            INPUT=$(cat)
            CMD=$(echo "$INPUT" | jq -r '.tool_input.command')
            if echo "$CMD" | grep -qE '\brm -rf /\b'; then
              echo "Blocked: rm -rf / is not permitted" >&2
              exit 2
            fi
            exit 0
```

### Pattern 6 — Re-inject context after compaction

```yaml
hooks:
  SessionStart:
    - matcher: "compact"
      hooks:
        - type: command
          command: "echo 'Reminder: use docs/STYLE.md conventions. Run lint before done.'"
```

## Hook script anatomy

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -qE 'dangerous-pattern'; then
  echo "Blocked: explanation goes to stderr for Claude" >&2
  exit 2
fi

exit 0
```

### Exit codes

- **0** — no objection, action proceeds
- **2** — action blocked, stderr sent to Claude as feedback
- **Any other non-zero** — action proceeds, stderr logged as hook error

### Structured JSON output (more control)

Exit 0 and write JSON for richer responses:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use rg instead of grep"
  }
}
```

## Decision check during artifact design

1. **Hard requirement that doesn't depend on model behavior?** → Yes: add a hook.
2. **Verification against actual state needed (tests, lint, file presence)?** → Yes: `Stop` or `PostToolUse` hook.
3. **Tool calls that should never happen?** → Yes: `PreToolUse` deny logic. (Cheaper alternative: `tools` allowlist in frontmatter.)
4. **Ships to others where you can't trust enforcement is manual?** → Yes: hooks more important.

Three or more yes → add hooks. Zero yes → skip.

## Anti-patterns

- **Don't use hooks for what the model handles reliably.** Asking "always run prettier" works; a hook makes it deterministic *if* you actually need that guarantee.
- **Don't make hooks the user's only defense.** Scripts get deleted, settings get missed. Combine hooks with clear instructions.
- **Don't write complex branching in hook scripts.** Significant decision-making belongs in a skill, not a hook.
- **Don't forget the `stop_hook_active` guard.** Stop hooks that always return non-zero loop indefinitely. Check `stop_hook_active` from input JSON and exit 0 if true.

## When prompt-architect should suggest hooks

Phase 1 (DESIGN) and Phase 3 (REVIEW) — surface the hooks question explicitly when:

- Artifact involves writes/edits → suggest `PostToolUse` linter
- Artifact runs Bash → suggest `PreToolUse` deny rules
- Long-running workflow ends with "done" → suggest `Stop` verification
- Will be shared with a team → suggest audit logging

Phrase: *"Would you like a hook to [specific behavior]? This makes [enforcement] deterministic rather than relying on the model."*

Don't add hooks silently. They're code that runs on the user's machine.
