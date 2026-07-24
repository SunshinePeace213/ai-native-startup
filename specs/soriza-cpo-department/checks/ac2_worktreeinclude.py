# /// script
# requires-python = ">=3.11"
# ///
"""AC2 — .worktreeinclude carries an ai-docs pattern so fresh worktrees receive
the cached mirrors. Full check beyond this script: create a scratch worktree
(EnterWorktree or git worktree add + the WorktreeCreate hook) from the hydrated
main checkout and assert ai-docs/anthropic/*.md exists inside it."""

from pathlib import Path

text = Path(".worktreeinclude").read_text()
assert any(line.strip().startswith("ai-docs/") for line in text.splitlines()), (
    "no ai-docs/* pattern in .worktreeinclude"
)
print("AC2 ok")
