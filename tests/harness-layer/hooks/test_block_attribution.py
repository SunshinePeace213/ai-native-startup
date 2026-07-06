"""Block/allow matrix for the PreToolUse attribution guard.

The repo policy (GIT-COMMIT-PR-MESSAGE.md) forbids Claude attribution in commit
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
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / ".claude" / "hooks" / "block_attribution.py"


def run_hook(stdin_text: str) -> subprocess.CompletedProcess:
    """Feed stdin_text to the guard exactly as Claude Code would."""
    return subprocess.run(
        ["uv", "run", "--script", str(SCRIPT)],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=60,
    )


def bash_payload(command: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def assert_blocked(proc: subprocess.CompletedProcess) -> None:
    """A block must exit 2 AND tell Claude the policy source and the fix."""
    assert proc.returncode == 2
    assert "GIT-COMMIT-PR-MESSAGE.md" in proc.stderr
    assert "remove the attribution line" in proc.stderr


# --- Block: every default Claude attribution form, however delivered ---------


def test_blocks_git_commit_with_claude_coauthor_trailer():
    """Core policy: the co-author trailer must never reach git history."""
    cmd = 'git commit -m "fix: x\n\nCo-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"'
    assert_blocked(run_hook(bash_payload(cmd)))


def test_blocks_heredoc_commit_with_claude_opus_coauthor():
    """Matching is on the whole command string, so heredoc smuggling — and any
    model name — cannot bypass the policy."""
    cmd = (
        "git commit -F - <<'EOF'\nfeat: y\n\n"
        "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>\nEOF"
    )
    assert_blocked(run_hook(bash_payload(cmd)))


def test_blocks_lowercase_coauthor_variant():
    """Case must not be an evasion route: the policy bans the trailer, not one
    capitalization of it."""
    cmd = 'git commit -m "x\n\nco-authored-by: claude <noreply@anthropic.com>"'
    assert_blocked(run_hook(bash_payload(cmd)))


def test_blocks_amend_with_claude_session_trailer():
    """Claude-Session links are attribution too — amending one in is as much a
    policy violation as a fresh commit."""
    cmd = 'git commit --amend -m "fix: z\n\nClaude-Session: https://claude.ai/code/session_abc"'
    assert_blocked(run_hook(bash_payload(cmd)))


def test_blocks_gh_pr_body_with_generated_with_footer():
    """The PR footer is the third default attribution form; gh commands are in
    scope, not just git."""
    cmd = (
        'gh pr create --title "x" --body "body\n\n'
        '🤖 Generated with [Claude Code](https://claude.com/claude-code)"'
    )
    assert_blocked(run_hook(bash_payload(cmd)))


# --- Allow: the guard must not tax legitimate work ---------------------------


def test_allows_clean_git_commit():
    """Ordinary commits are the 99% case; the guard must be invisible to them."""
    proc = run_hook(bash_payload('git commit -m "🔧 chore(hooks): x"'))
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_allows_non_claude_coauthor():
    """The policy targets Claude attribution only — crediting a human
    co-author is legitimate git practice."""
    cmd = 'git commit -m "x\n\nCo-Authored-By: Alice <alice@example.com>"'
    proc = run_hook(bash_payload(cmd))
    assert proc.returncode == 0


def test_allows_non_git_command_mentioning_trailer():
    """The old shell hook's false positive: writing documentation ABOUT the
    trailer is not attributing a commit. No git/gh invocation, no block."""
    cmd = (
        "cat > docs/policy-notes.md <<'EOF'\nNever add "
        "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>\nEOF"
    )
    proc = run_hook(bash_payload(cmd))
    assert proc.returncode == 0


def test_allows_non_bash_payload():
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
    proc = run_hook(payload)
    assert proc.returncode == 0


def test_allows_empty_stdin():
    """Fail-open: a guard that exits non-zero on missing input would wedge
    every Bash call whenever the harness sends nothing."""
    proc = run_hook("")
    assert proc.returncode == 0


def test_allows_malformed_json():
    """Fail-open: garbage input is a harness bug, not a policy violation — the
    guard must never turn it into a blocked tool call."""
    proc = run_hook("not json")
    assert proc.returncode == 0
