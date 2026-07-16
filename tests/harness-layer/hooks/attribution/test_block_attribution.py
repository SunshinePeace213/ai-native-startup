"""Block/allow matrix for the PreToolUse attribution guard.

The repo policy (.claude/rules/git-workflow.md) forbids Claude attribution in commit
and PR messages. These tests encode the guard's contract: git/gh commands that
carry any default Claude attribution form are denied (exit 2, corrective
stderr), while everything else — clean commits, non-Claude co-authors, non-git
commands that merely mention the strings, non-Bash payloads, and garbage input
— passes untouched (exit 0). The allow cases matter as much as the block cases:
false positives were the defect that forced the old shell hook's replacement,
and fail-open behavior keeps a buggy guard from wedging every Bash call.
"""

import json
import subprocess

SCRIPT = "block_attribution.py"


def bash_payload(command: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def assert_blocked(proc: subprocess.CompletedProcess) -> None:
    """A block must exit 2 AND tell Claude the policy source and the fix."""
    assert proc.returncode == 2
    assert ".claude/rules/git-workflow.md" in proc.stderr
    assert "remove the attribution line" in proc.stderr


# --- Block: every default Claude attribution form, however delivered ---------


def test_blocks_git_commit_with_claude_coauthor_trailer(run_hook):
    """Core policy: the co-author trailer must never reach git history."""
    cmd = 'git commit -m "fix: x\n\nCo-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"'
    assert_blocked(run_hook(SCRIPT, bash_payload(cmd)))


def test_blocks_heredoc_commit_with_claude_opus_coauthor(run_hook):
    """Matching is on the whole command string, so heredoc smuggling — and any
    model name — cannot bypass the policy."""
    cmd = (
        "git commit -F - <<'EOF'\nfeat: y\n\n"
        "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>\nEOF"
    )
    assert_blocked(run_hook(SCRIPT, bash_payload(cmd)))


def test_blocks_lowercase_coauthor_variant(run_hook):
    """Case must not be an evasion route: the policy bans the trailer, not one
    capitalization of it."""
    cmd = 'git commit -m "x\n\nco-authored-by: claude <noreply@anthropic.com>"'
    assert_blocked(run_hook(SCRIPT, bash_payload(cmd)))


def test_blocks_amend_with_claude_session_trailer(run_hook):
    """Claude-Session links are attribution too — amending one in is as much a
    policy violation as a fresh commit."""
    cmd = 'git commit --amend -m "fix: z\n\nClaude-Session: https://claude.ai/code/session_abc"'
    assert_blocked(run_hook(SCRIPT, bash_payload(cmd)))


def test_blocks_gh_pr_body_with_generated_with_footer(run_hook):
    """The PR footer is the third default attribution form; gh commands are in
    scope, not just git."""
    cmd = (
        'gh pr create --title "x" --body "body\n\n'
        '🤖 Generated with [Claude Code](https://claude.com/claude-code)"'
    )
    assert_blocked(run_hook(SCRIPT, bash_payload(cmd)))


def test_blocks_whitespace_wrapped_generated_with_footer(run_hook):
    """Whitespace reflow is not an evasion route: a footer wrapped across lines
    is still attribution."""
    cmd = (
        'gh pr create --title "x" --body "body\n\n'
        '🤖 Generated with\n[Claude Code](https://claude.com/claude-code)"'
    )
    assert_blocked(run_hook(SCRIPT, bash_payload(cmd)))


# --- Allow: the guard must not tax legitimate work ---------------------------


def test_allows_clean_git_commit(run_hook):
    """Ordinary commits are the 99% case; the guard must be invisible to them."""
    proc = run_hook(SCRIPT, bash_payload('git commit -m "🔧 chore(hooks): x"'))
    assert proc.returncode == 0
    assert "[block_attribution]" not in proc.stderr


def test_allows_non_claude_coauthor(run_hook):
    """The policy targets Claude attribution only — crediting a human
    co-author is legitimate git practice."""
    cmd = 'git commit -m "x\n\nCo-Authored-By: Alice <alice@example.com>"'
    proc = run_hook(SCRIPT, bash_payload(cmd))
    assert proc.returncode == 0


def test_allows_coauthor_name_starting_with_claude(run_hook):
    """Prefix names are not Claude: the trailing word boundary protects human
    co-authors whose name merely starts with "Claude"."""
    cmd = 'git commit -m "x\n\nCo-Authored-By: Claudette Rivers <c@example.com>"'
    proc = run_hook(SCRIPT, bash_payload(cmd))
    assert proc.returncode == 0


def test_allows_non_git_command_mentioning_trailer(run_hook):
    """Writing documentation ABOUT the trailer is not attributing a commit:
    the guard inspects only the command string for a git/gh token, unlike the
    old hook's whole-payload grep. No git/gh token in the command, no block."""
    cmd = (
        "cat > docs/policy-notes.md <<'EOF'\nNever add "
        "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>\nEOF"
    )
    proc = run_hook(SCRIPT, bash_payload(cmd))
    assert proc.returncode == 0


def test_allows_payload_with_git_only_outside_command(run_hook):
    """The old whole-payload grep false-blocked when a stray 'git' anywhere in
    the payload JSON (here: the cwd) combined with trailer text in the command.
    The guard reads only tool_input.command, so that false positive is gone."""
    payload = json.dumps(
        {
            "tool_name": "Bash",
            "cwd": "/home/user/git/repo",
            "tool_input": {
                "command": (
                    "cat > notes.md <<'EOF'\nNever add "
                    "Co-Authored-By: Claude <noreply@anthropic.com>\nEOF"
                )
            },
        }
    )
    proc = run_hook(SCRIPT, payload)
    assert proc.returncode == 0


def test_allows_non_bash_payload(run_hook):
    """The guard is scoped to Bash: blocking Write/Edit payloads would break
    unrelated tools for no policy gain."""
    payload = json.dumps(
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/tmp/x.md",
                "content": "Co-Authored-By: Claude <noreply@anthropic.com>",
            },
        }
    )
    proc = run_hook(SCRIPT, payload)
    assert proc.returncode == 0


def test_allows_empty_stdin(run_hook):
    """Fail-open: a guard that exits non-zero on missing input would wedge
    every Bash call whenever the harness sends nothing."""
    proc = run_hook(SCRIPT, "")
    assert proc.returncode == 0


def test_allows_malformed_json(run_hook):
    """Fail-open: garbage input is a harness bug, not a policy violation — the
    guard must never turn it into a blocked tool call."""
    proc = run_hook(SCRIPT, "not json")
    assert proc.returncode == 0
