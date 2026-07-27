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
CODEX_HOOKS = REPO_ROOT / ".codex" / "hooks.json"
HOOKS_MD = REPO_ROOT / ".claude" / "rules" / "harness-layer" / "hooks.md"

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
        ("sensitive-files/bash_guard.py", "PreToolUse", ("Bash",)): 1,
        (
            "sensitive-files/file_guard.py",
            "PreToolUse",
            ("Edit", "Grep", "MultiEdit", "Read", "Write"),
        ): 1,
    }
)

# Where each entrypoint stands on Codex parity. Values: "mirrored",
# "not-applicable", or "blocked-<reason>". The three not-applicable hooks are
# Claude-only surfaces: the spec gate rides a Claude slash-command, and the
# worktree pair answers Claude-only WorktreeCreate/WorktreeRemove events.
CODEX_DISPOSITIONS = {
    "block_attribution.py": "mirrored",
    "destructive-guard/block_destructive.py": "mirrored",
    "auto-format/js_ts.py": "mirrored",
    "auto-format/data.py": "mirrored",
    "auto-format/markdown.py": "mirrored",
    "auto-format/python.py": "mirrored",
    "security-scan/post_write_scan.py": "mirrored",
    "security-scan/track_bash_writes.py": "mirrored",
    "security-scan/session_baseline.py": "mirrored",
    "security-scan/stop_sweep.py": "mirrored",
    "sensitive-files/bash_guard.py": "mirrored",
    "sensitive-files/file_guard.py": "mirrored",
    "check_spec_completeness.py": "not-applicable",
    "worktree/worktree_create.py": "not-applicable",
    "worktree/worktree_remove.py": "not-applicable",
}

CODEX_EXPECTED_BINDINGS = Counter(
    {
        ("block_attribution.py", "PreToolUse", ("Bash",)): 1,
        ("destructive-guard/block_destructive.py", "PreToolUse", ("Bash",)): 1,
        ("sensitive-files/bash_guard.py", "PreToolUse", ("Bash",)): 1,
        ("sensitive-files/file_guard.py", "PreToolUse", ("apply_patch",)): 1,
        ("auto-format/js_ts.py", "PostToolUse", ("apply_patch",)): 1,
        ("auto-format/data.py", "PostToolUse", ("apply_patch",)): 1,
        ("auto-format/markdown.py", "PostToolUse", ("apply_patch",)): 1,
        ("auto-format/python.py", "PostToolUse", ("apply_patch",)): 1,
        ("security-scan/post_write_scan.py", "PostToolUse", ("apply_patch",)): 1,
        ("security-scan/track_bash_writes.py", "PostToolUse", ("Bash",)): 1,
        ("security-scan/session_baseline.py", "SessionStart", ()): 1,
        ("security-scan/stop_sweep.py", "Stop", ()): 1,
        ("security-scan/stop_sweep.py", "SubagentStop", ()): 1,
    }
)

# Six entries, not five: stop_sweep.py is bound to BOTH Stop and SubagentStop,
# so the four 60s formatters plus two 120s sweeps make six timeout-carrying
# entries across five distinct scripts.
CODEX_EXPECTED_TIMEOUTS = {
    ("auto-format/js_ts.py", "PostToolUse", ("apply_patch",)): 60,
    ("auto-format/data.py", "PostToolUse", ("apply_patch",)): 60,
    ("auto-format/markdown.py", "PostToolUse", ("apply_patch",)): 60,
    ("auto-format/python.py", "PostToolUse", ("apply_patch",)): 60,
    ("security-scan/stop_sweep.py", "Stop", ()): 120,
    ("security-scan/stop_sweep.py", "SubagentStop", ()): 120,
}

# The one env prefix the plan sanctions: it switches block_destructive.py's ask
# tier to a hard deny, because Codex has no per-call approval prompt.
CODEX_ENV_PREFIX = "HARNESS_HOOK_HOST=codex "


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


def codex_entries() -> list[tuple[tuple[str, str, tuple], dict]]:
    """Flatten .codex/hooks.json into ((script, event, normalized matcher), hook)
    rows -- the same identity EXPECTED_BINDINGS uses for the Claude side."""
    codex_config = json.loads(CODEX_HOOKS.read_text())["hooks"]
    return [
        ((script_of(hook["command"]), event, normalized(block.get("matcher"))), hook)
        for event, blocks in codex_config.items()
        for block in blocks
        for hook in block["hooks"]
    ]


def test_codex_event_names_are_known():
    """Codex reads its own config; an invented event name binds nothing and
    silently drops a guard that Claude sessions still enforce."""
    assert set(json.loads(CODEX_HOOKS.read_text())["hooks"]) <= ALLOWED_EVENTS


def test_codex_bindings_match_the_expected_matrix():
    """.codex/hooks.json is a second production integration point, invisible to
    every settings.json check above. Pinning it as a Counter means dropping,
    adding, duplicating, or re-matching an entry fails here rather than leaving
    Codex sessions quietly unguarded."""
    actual = Counter(key for key, _hook in codex_entries())
    assert actual == CODEX_EXPECTED_BINDINGS


def test_codex_commands_are_uv_script_shaped_and_safe():
    """Codex runs these commands from an arbitrary cwd, so each must resolve the
    script through the repo root and launch it via uv -- and carry a
    statusMessage, since a silent Codex hook gives the user no reason for a
    denial. Only the sanctioned host-flag prefix may precede the launcher."""
    for (script, _event, _matcher), hook in codex_entries():
        command = hook["command"]
        prefix, launcher, _rest = command.partition("uv run --script ")
        assert launcher, command
        assert prefix in ("", CODEX_ENV_PREFIX), command
        assert "$(git rev-parse --show-toplevel)" in command, command
        assert ".." not in script, command
        assert (HOOKS_ROOT / script).is_file(), command
        assert hook.get("statusMessage"), hook


def test_codex_timeouts_are_pinned_in_both_directions():
    """A formatter or sweep that outruns Codex's default budget is killed
    mid-write; a timeout on a fast guard hides a hang. Comparing the whole
    mapping asserts both presence with the right value and absence everywhere
    else."""
    actual = {key: hook["timeout"] for key, hook in codex_entries() if "timeout" in hook}
    assert actual == CODEX_EXPECTED_TIMEOUTS


def test_dispositions_cover_every_entrypoint():
    """A new hook added with no disposition is the drift this matrix exists to
    stop: it would ship Claude-only by default and nobody would notice. Forcing
    an explicit verdict per entrypoint makes that omission a red suite."""
    assert set(CODEX_DISPOSITIONS) == entrypoints()
    for script, disposition in CODEX_DISPOSITIONS.items():
        assert disposition in ("mirrored", "not-applicable") or disposition.startswith(
            "blocked-"
        ), f"{script}: {disposition}"


def test_dispositions_agree_with_codex_registrations():
    """A disposition that lies about reality is worse than none -- it documents
    a guard as live on Codex when it is not, or hides one that is. Checked both
    ways: every 'mirrored' hook is registered, every other hook is not."""
    registered = Counter(script for (script, _e, _m), _hook in codex_entries())
    for script, disposition in CODEX_DISPOSITIONS.items():
        if disposition == "mirrored":
            assert registered[script] >= 1, (
                f"{script} is mirrored but absent from .codex/hooks.json"
            )
        else:
            assert not registered[script], f"{script} is {disposition} but registered on Codex"


def family_of(script: str) -> str:
    """Map an entrypoint to its hooks.md catalog family: the top-level
    directory (with trailing slash) for a nested script, or the bare filename
    for a family of one -- the catalog is one row per family, not per
    entrypoint."""
    return script.split("/", 1)[0] + "/" if "/" in script else script


CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def hooks_md_rows() -> list[list[str]]:
    """Cell lists for every data row in hooks.md's catalog table, tolerating a
    row with fewer than four cells so a doc regression that drops the Codex
    column is caught by content, not swallowed by the parser. Splits on
    unescaped '|' only -- matcher cells carry escaped pipes like `Write\\|Edit`
    that are literal text, not column separators."""
    lines = HOOKS_MD.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("| Hook "))
    rows = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        stripped = line.strip().strip("|")
        cells = [cell.strip().replace("\\|", "|") for cell in CELL_SPLIT_RE.split(stripped)]
        rows.append(cells)
    return rows


def hooks_md_codex_column() -> dict[str, str]:
    """{family: verdict} from the catalog table's Hook and Codex columns.

    A cell is normalized to its leading verdict word -- 'mirrored (write
    surface only)' still reads as 'mirrored' -- because the parenthetical is a
    caveat for a human reader (only file_guard.py's write surface is mirrored
    under Codex, per spec.md's Non-Goals), not a second verdict the
    family-level implication below needs to distinguish. A row missing its
    Codex cell maps to '' so it matches neither verdict.
    """
    verdict_re = re.compile(r"^(mirrored|not-applicable)\b")
    families = {}
    for cells in hooks_md_rows():
        family = cells[0].strip("`")
        cell = cells[3] if len(cells) >= 4 else ""
        match = verdict_re.match(cell)
        families[family] = match.group(1) if match else cell
    return families


def test_hooks_md_codex_column_matches_family_dispositions():
    """hooks.md's Codex column is the human-facing summary of
    CODEX_DISPOSITIONS; if the two disagree, an agent reading the catalog sees
    a verdict the code doesn't enforce -- the exact drift this task closes.
    Checked as an implication in both directions per family, and a missing
    family row or missing Codex cell fails via the set/verdict comparisons
    below rather than being silently skipped."""
    doc_families = hooks_md_codex_column()
    entrypoint_families: dict[str, list[str]] = {}
    for script, disposition in CODEX_DISPOSITIONS.items():
        entrypoint_families.setdefault(family_of(script), []).append(disposition)

    assert set(doc_families) == set(entrypoint_families), (
        f"hooks.md families {sorted(doc_families)} != code families {sorted(entrypoint_families)}"
    )
    for family, dispositions in entrypoint_families.items():
        cell = doc_families[family]
        all_mirrored = all(d == "mirrored" for d in dispositions)
        none_mirrored = not any(d == "mirrored" for d in dispositions)
        assert (cell == "mirrored") == all_mirrored, (
            f"{family}: hooks.md says {cell!r} but entrypoints are {dispositions}"
        )
        assert (cell == "not-applicable") == none_mirrored, (
            f"{family}: hooks.md says {cell!r} but entrypoints are {dispositions}"
        )
