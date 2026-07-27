"""Contract tests for the auto-format hooks' shared helper module.

_common.py is the plumbing every format/worktree hook stands on, so its
contract IS the fail-open policy: payload parsing must yield the raw dict
only for a well-formed payload and silently yield None for every broken
input (a hook that crashed or hung on garbage stdin would wedge every
edit); ``target()`` turns that payload into every edited path worth
formatting, guarded per path; vendored matching is on the ROOT-RELATIVE
path so a directory name outside the repo can never suppress formatting
inside it; the diagnostics cap keeps exit-2 feedback short enough for the
agent to act on; and run() must make a missing formatter binary
distinguishable so hooks can point at the meta-install skill instead of
raising or falsely exiting 2.

The module is loaded through the shared ``load_hook_module`` fixture (as
``fmt``), never via sys.path -- two families' `_common` must not collide.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="module")
def fmt(load_hook_module):
    return load_hook_module("auto-format/_common.py")


@pytest.fixture
def stdin_from(monkeypatch, tmp_path):
    """Route text to sys.stdin through a real file so select() sees a real fd."""
    handles = []

    def _feed(text: str) -> None:
        source = tmp_path / f"stdin{len(handles)}.txt"
        source.write_text(text)
        handle = source.open()
        handles.append(handle)
        monkeypatch.setattr(sys, "stdin", handle)

    yield _feed
    for handle in handles:
        handle.close()


# --- Payload parsing: fail-open on everything broken --------------------------


def test_read_payload_returns_raw_dict(stdin_from, fmt):
    """The worktree hooks read their own field names (worktreeName/name), so
    the parsed payload must be exposed raw, not only tool_input.file_path."""
    stdin_from(json.dumps({"worktreeName": "wt-1"}))
    assert fmt.read_payload() == {"worktreeName": "wt-1"}


def test_empty_stdin_yields_none(stdin_from, fmt):
    """Fail-open: no payload means nothing to format, never an error."""
    stdin_from("")
    assert fmt.read_payload() is None


def test_malformed_json_yields_none(stdin_from, fmt):
    """Fail-open: garbage stdin is a harness bug, not the hook's problem."""
    stdin_from("not json {")
    assert fmt.read_payload() is None


def test_tty_stdin_yields_none(monkeypatch, fmt):
    """A human running the script by hand must not hang it waiting on stdin."""

    class TTYStdin:
        closed = False

        def isatty(self) -> bool:
            return True

    monkeypatch.setattr(sys, "stdin", TTYStdin())
    assert fmt.read_payload() is None


# --- target(): every edited path, guarded per path and paired with the root --


def test_target_returns_empty_list_when_nothing_to_format(stdin_from, fmt):
    """No payload means nothing to format -- an empty list, not None, so a
    formatter can loop over the result unconditionally."""
    stdin_from("")
    assert fmt.target({".py"}) == []


def test_target_pairs_every_matching_path_with_the_root(monkeypatch, stdin_from, tmp_path, fmt):
    """A two-file apply_patch envelope must yield one pair per matching
    path, in envelope order, each carrying the same project root -- this is
    what lets a formatter process every edited path, not just the first."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    a, b = tmp_path / "a.py", tmp_path / "b.py"
    a.write_text("x = 1\n")
    b.write_text("y = 2\n")
    envelope = f"*** Begin Patch\n*** Add File: {a}\n*** Add File: {b}\n*** End Patch\n"
    stdin_from(json.dumps({"tool_name": "apply_patch", "tool_input": {"command": envelope}}))
    assert fmt.target({".py"}) == [(a, tmp_path.resolve()), (b, tmp_path.resolve())]


def test_target_drops_non_matching_extension_but_keeps_the_rest(
    monkeypatch, stdin_from, tmp_path, fmt
):
    """Extension filtering applies PER PATH, not to the whole envelope: one
    non-matching sibling must not suppress a matching file."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    py, txt = tmp_path / "a.py", tmp_path / "notes.txt"
    py.write_text("x = 1\n")
    txt.write_text("hello\n")
    envelope = f"*** Begin Patch\n*** Add File: {txt}\n*** Add File: {py}\n*** End Patch\n"
    stdin_from(json.dumps({"tool_name": "apply_patch", "tool_input": {"command": envelope}}))
    assert fmt.target({".py"}) == [(py, tmp_path.resolve())]


def test_target_drops_renamed_away_path_but_keeps_the_new_one(
    monkeypatch, stdin_from, tmp_path, fmt
):
    """A rename's OLD path no longer exists on disk once apply_patch has run
    -- the deleted-file guard must drop it while keeping the NEW path, which
    is what lets a rename fall out of the ordinary loop with no special case."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    old, new = tmp_path / "a.py", tmp_path / "b.py"
    new.write_text("y = 2\n")  # only the new path exists; apply_patch already moved it
    envelope = f"*** Begin Patch\n*** Update File: {old}\n*** Move to: {new}\n*** End Patch\n"
    stdin_from(json.dumps({"tool_name": "apply_patch", "tool_input": {"command": envelope}}))
    assert fmt.target({".py"}) == [(new, tmp_path.resolve())]


# --- Project-root resolution --------------------------------------------------


def test_resolve_root_prefers_env_var(monkeypatch, tmp_path, fmt):
    """Claude Code sets $CLAUDE_PROJECT_DIR; hooks must format against the
    session's project, not wherever the script file happens to live."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    assert fmt.resolve_root() == tmp_path.resolve()


def test_resolve_root_falls_back_to_script_location(monkeypatch, fmt):
    """Without the env var (manual runs, tests) the root derives from the
    module's own home: <root>/.claude/hooks/auto-format/_common.py."""
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    assert fmt.resolve_root() == REPO_ROOT


def test_resolve_root_ignores_env_var_that_is_not_a_directory(monkeypatch, tmp_path, fmt):
    """A stale or bogus env value must degrade to the fallback, not hand
    formatters a cwd they cannot run in."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path / "gone"))
    assert fmt.resolve_root() == REPO_ROOT


# --- Vendored-path skip: root-relative, never beyond the repo ----------------


def test_vendored_dirs_inside_root_are_skipped(tmp_path, fmt):
    """Formatting third-party or generated trees creates diff noise for code
    nobody owns; each vendored dir name must skip when under the root."""
    for vendored in ("node_modules", ".venv", "dist"):
        assert fmt.is_vendored(tmp_path / vendored / "pkg" / "f.js", tmp_path)


def test_root_ancestor_named_dist_does_not_skip(tmp_path, fmt):
    """The check is on the ROOT-RELATIVE path: a repo that itself lives under
    a directory named dist must still have its files formatted (the retired
    lint.py encoded exactly this trap)."""
    root = tmp_path / "dist" / "repo"
    assert fmt.is_vendored(root / "src" / "app.py", root) is False


def test_file_outside_root_is_never_vendored(tmp_path, fmt):
    """Paths outside the project (scratch files) are not ours to classify;
    the vendored skip must not apply to them even under a dist/ segment."""
    root = tmp_path / "repo"
    outside = tmp_path / "elsewhere" / "dist" / "f.py"
    assert fmt.is_vendored(outside, root) is False


def test_normal_in_repo_path_is_not_vendored(tmp_path, fmt):
    """The 99% case: ordinary project files must reach the formatter."""
    assert fmt.is_vendored(tmp_path / "src" / "main.py", tmp_path) is False


# --- Diagnostic capping: short enough to act on, count never lost ------------


def test_diagnostics_cap_at_ten_with_tail(fmt):
    """Exit-2 stderr is fed straight back to the agent; past ten lines more
    detail hurts more than it helps, but the total count must survive."""
    lines = [f"f.py:{i} E501 line too long" for i in range(1, 15)]
    out = fmt.format_diagnostics(lines).splitlines()
    assert len(out) == 11
    assert out[:10] == lines[:10]
    assert out[10] == "... and 4 more"


def test_diagnostics_at_or_under_cap_have_no_tail(fmt):
    """A tail on a short list would misreport the error count."""
    lines = [f"f.py:{i} E501 x" for i in range(1, 11)]  # exactly the cap
    assert fmt.format_diagnostics(lines) == "\n".join(lines)


# --- run(): never raises, missing binary is a distinct signal ----------------


def test_run_missing_binary_returns_none(fmt):
    """None is the meta-install signal: hooks translate it into a note naming
    the meta-install skill instead of a traceback or a false exit 2."""
    assert fmt.run(["auto-format-no-such-binary-xyz"]) is None


def test_run_returns_exit_code_and_streams(fmt):
    """Hooks read the formatter's own exit code and streams to decide between
    success, real lint errors, and infrastructure failure."""
    code, out, err = fmt.run(
        [
            sys.executable,
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)",
        ]
    )
    assert (code, out.strip(), err.strip()) == (3, "out", "err")


def test_run_strips_color_forcing_env(monkeypatch, fmt):
    """Exit-2 diagnostics are fed to the agent as text: a session that forces
    ANSI color (FORCE_COLOR) must not leak escape codes into captured output."""
    monkeypatch.setenv("FORCE_COLOR", "3")
    probe = "import os; print(os.environ.get('FORCE_COLOR'), os.environ.get('NO_COLOR'))"
    code, out, _ = fmt.run([sys.executable, "-c", probe])
    assert (code, out.strip()) == (0, "None 1")


# --- note(): every stderr line says which hook is talking --------------------


def test_note_prefixes_hook_name(capsys, monkeypatch, fmt):
    """Four hooks share one stderr channel; the prefix says who is talking.
    The default derives from the running script so hooks need no config."""
    fmt.note("hello", hook="markdown")
    monkeypatch.setattr(sys, "argv", ["/repo/.claude/hooks/auto-format/js_ts.py"])
    fmt.note("world")
    err = capsys.readouterr().err.splitlines()
    assert err == ["[markdown] hello", "[js_ts] world"]
