"""Contract tests for the auto-format hooks' shared helper module.

_common.py is the plumbing every format/worktree hook stands on, so its
contract IS the fail-open policy: payload parsing must yield a file path
only for a well-formed payload and silently yield None for every broken
input (a hook that crashed or hung on garbage stdin would wedge every
edit); vendored matching is on the ROOT-RELATIVE path so a directory name
outside the repo can never suppress formatting inside it; the diagnostics
cap keeps exit-2 feedback short enough for the agent to act on; and run()
must make a missing formatter binary distinguishable so hooks can point at
the meta-install skill instead of raising or falsely exiting 2.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "hooks" / "auto-format"))

import _common  # noqa: E402


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


# --- Payload parsing: one good shape in, None for everything broken ----------


def test_good_payload_yields_file_path(stdin_from):
    """The shape the harness actually sends (snake_case, proven in-repo by
    block_attribution.py) must round-trip to the edited file's path."""
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "/tmp/example.py"}})
    stdin_from(payload)
    assert _common.read_file_path() == "/tmp/example.py"


def test_empty_stdin_yields_none(stdin_from):
    """Fail-open: no payload means nothing to format, never an error."""
    stdin_from("")
    assert _common.read_file_path() is None


def test_malformed_json_yields_none(stdin_from):
    """Fail-open: garbage stdin is a harness bug, not the hook's problem."""
    stdin_from("not json {")
    assert _common.read_file_path() is None


def test_tty_stdin_yields_none(monkeypatch):
    """A human running the script by hand must not hang it waiting on stdin."""

    class TTYStdin:
        closed = False

        def isatty(self) -> bool:
            return True

    monkeypatch.setattr(sys, "stdin", TTYStdin())
    assert _common.read_file_path() is None


def test_payload_without_file_path_yields_none(stdin_from):
    """A payload with no file to format (e.g. Bash-shaped) must bow out."""
    stdin_from(json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}}))
    assert _common.read_file_path() is None
    stdin_from(json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "   "}}))
    assert _common.read_file_path() is None


def test_read_payload_returns_raw_dict(stdin_from):
    """The worktree hooks read their own field names (worktreeName/name), so
    the parsed payload must be exposed raw, not only tool_input.file_path."""
    stdin_from(json.dumps({"worktreeName": "wt-1"}))
    assert _common.read_payload() == {"worktreeName": "wt-1"}


# --- Project-root resolution --------------------------------------------------


def test_resolve_root_prefers_env_var(monkeypatch, tmp_path):
    """Claude Code sets $CLAUDE_PROJECT_DIR; hooks must format against the
    session's project, not wherever the script file happens to live."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    assert _common.resolve_root() == tmp_path.resolve()


def test_resolve_root_falls_back_to_script_location(monkeypatch):
    """Without the env var (manual runs, tests) the root derives from the
    module's own home: <root>/.claude/hooks/auto-format/_common.py."""
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    assert _common.resolve_root() == REPO_ROOT


def test_resolve_root_ignores_env_var_that_is_not_a_directory(monkeypatch, tmp_path):
    """A stale or bogus env value must degrade to the fallback, not hand
    formatters a cwd they cannot run in."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path / "gone"))
    assert _common.resolve_root() == REPO_ROOT


# --- Vendored-path skip: root-relative, never beyond the repo ----------------


def test_vendored_dirs_inside_root_are_skipped(tmp_path):
    """Formatting third-party or generated trees creates diff noise for code
    nobody owns; each vendored dir name must skip when under the root."""
    for vendored in ("node_modules", ".venv", "dist"):
        assert _common.is_vendored(tmp_path / vendored / "pkg" / "f.js", tmp_path)


def test_root_ancestor_named_dist_does_not_skip(tmp_path):
    """The check is on the ROOT-RELATIVE path: a repo that itself lives under
    a directory named dist must still have its files formatted (the retired
    lint.py encoded exactly this trap)."""
    root = tmp_path / "dist" / "repo"
    assert _common.is_vendored(root / "src" / "app.py", root) is False


def test_file_outside_root_is_never_vendored(tmp_path):
    """Paths outside the project (scratch files) are not ours to classify;
    the vendored skip must not apply to them even under a dist/ segment."""
    root = tmp_path / "repo"
    outside = tmp_path / "elsewhere" / "dist" / "f.py"
    assert _common.is_vendored(outside, root) is False


def test_normal_in_repo_path_is_not_vendored(tmp_path):
    """The 99% case: ordinary project files must reach the formatter."""
    assert _common.is_vendored(tmp_path / "src" / "main.py", tmp_path) is False


# --- Diagnostic capping: short enough to act on, count never lost ------------


def test_diagnostics_cap_at_ten_with_tail():
    """Exit-2 stderr is fed straight back to the agent; past ten lines more
    detail hurts more than it helps, but the total count must survive."""
    lines = [f"f.py:{i} E501 line too long" for i in range(1, 15)]
    out = _common.format_diagnostics(lines).splitlines()
    assert len(out) == 11
    assert out[:10] == lines[:10]
    assert out[10] == "... and 4 more"


def test_diagnostics_at_or_under_cap_have_no_tail():
    """A tail on a short list would misreport the error count."""
    lines = [f"f.py:{i} E501 x" for i in range(1, 11)]  # exactly the cap
    assert _common.format_diagnostics(lines) == "\n".join(lines)


# --- run(): never raises, missing binary is a distinct signal ----------------


def test_run_missing_binary_returns_none():
    """None is the meta-install signal: hooks translate it into a note naming
    the meta-install skill instead of a traceback or a false exit 2."""
    assert _common.run(["auto-format-no-such-binary-xyz"]) is None


def test_run_returns_exit_code_and_streams():
    """Hooks read the formatter's own exit code and streams to decide between
    success, real lint errors, and infrastructure failure."""
    code, out, err = _common.run(
        [
            sys.executable,
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)",
        ]
    )
    assert (code, out.strip(), err.strip()) == (3, "out", "err")


def test_run_strips_color_forcing_env(monkeypatch):
    """Exit-2 diagnostics are fed to the agent as text: a session that forces
    ANSI color (FORCE_COLOR) must not leak escape codes into captured output."""
    monkeypatch.setenv("FORCE_COLOR", "3")
    probe = "import os; print(os.environ.get('FORCE_COLOR'), os.environ.get('NO_COLOR'))"
    code, out, _ = _common.run([sys.executable, "-c", probe])
    assert (code, out.strip()) == (0, "None 1")


# --- note(): every stderr line says which hook is talking --------------------


def test_note_prefixes_hook_name(capsys, monkeypatch):
    """Four hooks share one stderr channel; the prefix says who is talking.
    The default derives from the running script so hooks need no config."""
    _common.note("hello", hook="markdown")
    monkeypatch.setattr(sys, "argv", ["/repo/.claude/hooks/auto-format/js_ts.py"])
    _common.note("world")
    err = capsys.readouterr().err.splitlines()
    assert err == ["[markdown] hello", "[js_ts] world"]
