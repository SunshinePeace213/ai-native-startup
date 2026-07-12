"""Wiring tests: a hook that passes its contract tests but never fires is dead.

.claude/settings.json is the hooks' production integration point, so these
tests pin it semantically -- as a Counter of (script, event, normalized
matcher) bindings -- which catches a wrong matcher, a typo'd path, a dropped
event, or a duplicate registration, while surviving reformatting and
reordering. Every executable entrypoint under .claude/hooks/ (identified by
its PEP 723 '# /// script' marker or a shebang; _common.py libraries carry
neither) must be claimed by settings.json OR by a command-scoped registrar
under .claude/commands/ (the spec gate rides /harness-layer:harness-plan, not
global settings -- registering it globally would gate every session). Out of
scope on purpose: settings.local.json (personal, untracked) and hooks shipped
by external plugins (not this repo's contract).
"""

import json
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS_ROOT = REPO_ROOT / ".claude" / "hooks"
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"

ALLOWED_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "UserPromptSubmit",
    "Notification",
    "Stop",
    "SubagentStop",
    "SessionStart",
    "SessionEnd",
    "PreCompact",
    "WorktreeCreate",
    "WorktreeRemove",
}

HOOK_PATH_RE = re.compile(r"\.claude/hooks/([^\s\"')]+)")

FORMAT_MATCHER = ("Edit", "MultiEdit", "Write")

EXPECTED_BINDINGS = Counter(
    {
        ("block_attribution.py", "PreToolUse", ("Bash",)): 1,
        ("destructive-guard/block_destructive.py", "PreToolUse", ("Bash",)): 1,
        ("auto-format/js_ts.py", "PostToolUse", FORMAT_MATCHER): 1,
        ("auto-format/data.py", "PostToolUse", FORMAT_MATCHER): 1,
        ("auto-format/markdown.py", "PostToolUse", FORMAT_MATCHER): 1,
        ("auto-format/python.py", "PostToolUse", FORMAT_MATCHER): 1,
        ("security-scan/post_write_scan.py", "PostToolUse", FORMAT_MATCHER): 1,
        ("security-scan/track_bash_writes.py", "PostToolUse", ("Bash",)): 1,
        ("security-scan/track_bash_writes.py", "PostToolUseFailure", ("Bash",)): 1,
        ("security-scan/session_baseline.py", "SessionStart", ()): 1,
        ("security-scan/stop_sweep.py", "Stop", ()): 1,
        ("security-scan/stop_sweep.py", "SubagentStop", ()): 1,
        ("worktree/worktree_create.py", "WorktreeCreate", ()): 1,
        ("worktree/worktree_remove.py", "WorktreeRemove", ()): 1,
    }
)


def hooks_config() -> dict:
    return json.loads(SETTINGS.read_text())["hooks"]


def normalized(matcher: str | None) -> tuple:
    """Order-insensitive matcher identity: 'Write|Edit' == 'Edit|Write'."""
    return tuple(sorted(matcher.split("|"))) if matcher else ()


def registered_commands() -> list[tuple[str, str, tuple]]:
    """Flatten settings.json into (command, event, normalized matcher) rows."""
    return [
        (hook["command"], event, normalized(block.get("matcher")))
        for event, blocks in hooks_config().items()
        for block in blocks
        for hook in block["hooks"]
    ]


def script_of(command: str) -> str:
    """The hooks-relative script path a command runs ('' if none)."""
    match = HOOK_PATH_RE.search(command)
    return match.group(1) if match else ""


def test_event_names_are_known():
    """A typo'd or invented event name registers nothing and fails silently."""
    assert set(hooks_config()) <= ALLOWED_EVENTS


def test_registered_bindings_match_the_expected_matrix():
    """The full contract in one comparison: every hook on its intended event
    and matcher, no duplicates (Counter, not set), nothing extra or missing."""
    actual = Counter(
        (script_of(command), event, matcher)
        for command, event, matcher in registered_commands()
        if script_of(command)
    )
    assert actual == EXPECTED_BINDINGS


def test_registered_commands_are_uv_script_shaped_and_safe():
    """Every repo-local hook is launched via `uv run --script` on a real file
    under .claude/hooks -- no traversal, no stale paths."""
    for command, _event, _matcher in registered_commands():
        script = script_of(command)
        if not script:
            continue
        assert command.startswith("uv run --script "), command
        assert ".." not in script, command
        assert (HOOKS_ROOT / script).is_file(), command


def command_scoped_scripts() -> set[str]:
    """Hook scripts referenced by command-frontmatter registrars."""
    return {
        match for md in COMMANDS_DIR.rglob("*.md") for match in HOOK_PATH_RE.findall(md.read_text())
    }


def entrypoints() -> set[str]:
    """Executable hook scripts: PEP 723 marker or shebang. _common.py modules
    are libraries and carry neither."""
    found = set()
    for path in HOOKS_ROOT.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        head = path.read_text(errors="replace")[:512]
        if "# /// script" in head or head.startswith("#!"):
            found.add(str(path.relative_to(HOOKS_ROOT)))
    return found


def test_every_entrypoint_is_claimed_by_a_registration_surface():
    """An executable hook nobody registers is dead code that still looks
    alive -- exactly the drift that hid the spec gate's registration."""
    claimed = {script_of(cmd) for cmd, _e, _m in registered_commands()} | command_scoped_scripts()
    unclaimed = entrypoints() - claimed
    assert not unclaimed, f"hooks with no registration surface: {sorted(unclaimed)}"


def test_command_scoped_references_point_at_real_files():
    """A registrar naming a moved/renamed hook fails at session time, not CI
    time -- unless this pins it."""
    for script in command_scoped_scripts():
        assert (HOOKS_ROOT / script).is_file(), script
