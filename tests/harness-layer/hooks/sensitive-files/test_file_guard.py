"""End-to-end subprocess tests for file_guard.py (Read/Edit/Write/MultiEdit/Grep).

Contract under test: a PreToolUse call whose target matches the sensitive-files
catalog is denied (exit 2, three stderr lines carrying `Blocked:`, the matched
path, the category label, and the standing policy) before the tool ever runs,
BECAUSE blocking only Read would leave Edit/Write/MultiEdit free to tamper with
or overwrite the same secret file, and a `.env` denial is only actionable if it
names a template the agent can actually read. Everything the guard does not
recognize -- an unmatched tool, a non-string field, malformed/empty stdin --
must fail open (exit 0, no stderr), because a guard that wedges an unrelated
tool call is worse than the risk it defends against.

Every test launches the real script through the shared `run_hook` fixture
(the ONE launcher; see HOOK-TESTING.md), so this exercises the exact
`uv run --script` invocation Claude Code uses. Parallel-safe: every fixture is
tmp_path-scoped and nothing depends on order or shared state. No test ever
writes a secret VALUE -- the guard matches names/paths, never contents.
"""

import json
import subprocess

import pytest

SCRIPT = "sensitive-files/file_guard.py"


def file_payload(tool_name: str, file_path) -> str:
    return json.dumps({"tool_name": tool_name, "tool_input": {"file_path": str(file_path)}})


def grep_payload(*, path=None, glob=None) -> str:
    tool_input = {}
    if path is not None:
        tool_input["path"] = str(path)
    if glob is not None:
        tool_input["glob"] = glob
    return json.dumps({"tool_name": "Grep", "tool_input": tool_input})


def assert_denied(
    res: subprocess.CompletedProcess, path_fragment: str, category_label: str
) -> None:
    """Every deny must be agent-actionable: what was blocked, its category, and
    the standing policy -- not just a bare exit code (AC1)."""
    assert res.returncode == 2
    assert "Blocked:" in res.stderr
    assert path_fragment in res.stderr
    assert category_label in res.stderr
    assert "never read, print, copy, or modify secret-bearing files" in res.stderr


def assert_allowed(res: subprocess.CompletedProcess) -> None:
    assert res.returncode == 0
    assert res.stderr == ""


# --- Per-tool block cases (AC1) -------------------------------------------------


@pytest.mark.parametrize("tool_name", ["Read", "Edit", "Write", "MultiEdit"])
def test_denies_cataloged_file_per_tool(run_hook, tool_name):
    """Blocking only Read would leave Edit/Write/MultiEdit free to tamper with
    or overwrite the same secret file -- every file-scoped tool shares one
    catalog and must be denied identically."""
    res = run_hook(SCRIPT, file_payload(tool_name, "/home/u/.ssh/id_rsa"))
    assert_denied(res, "/home/u/.ssh/id_rsa", "SSH & auth keys")


def test_denies_one_sample_per_catalog_category(run_hook):
    """A category missing from the file guard's own coverage is a full leak of
    that category through Read/Edit/Write/MultiEdit, not just a theoretical
    engine gap -- so every category is exercised through the real script, not
    only through match_path directly."""
    samples = [
        ("/proj/.env", "Environment files"),
        ("/home/u/.ssh/config", "SSH & auth keys"),
        ("/tmp/server.pem", "Certificates & private keys"),
        ("/home/u/.aws/credentials", "Cloud provider credentials"),
        ("/home/u/.npmrc", "Package-manager credentials"),
        ("/home/u/.git-credentials", "VCS & tool credentials"),
        ("/proj/terraform.tfstate", "CI/CD & IaC secrets"),
        ("/proj/secrets.yml", "Framework & app secrets"),
        ("/home/u/.pgpass", "Database credentials & data"),
        ("/home/u/.zsh_history", "Shell & REPL history"),
        ("/home/u/logins.json", "Browser & OS credential stores"),
        ("/tmp/service.keytab", "Kerberos"),
        ("/home/u/wallet.dat", "Crypto wallets"),
        ("/home/u/.claude.json", "AI-tool auth"),
    ]
    for path, label in samples:
        res = run_hook(SCRIPT, file_payload("Read", path))
        assert_denied(res, path, label)


# --- `.env` redirect message (AC2) ----------------------------------------------


def test_env_denial_names_template_next_to_target(run_hook, tmp_path):
    """The redirect must point at a file the agent can actually read: a
    template sitting right next to the target `.env` is the most concrete
    alternative, so it must be named exactly."""
    (tmp_path / ".env.example").write_text("")
    target = tmp_path / ".env"
    res = run_hook(
        SCRIPT,
        file_payload("Read", target),
        env_overrides={"CLAUDE_PROJECT_DIR": str(tmp_path)},
    )
    assert res.returncode == 2
    assert str(tmp_path / ".env.example") in res.stderr


def test_env_denial_falls_back_to_project_root_template(run_hook, tmp_path):
    """When no template sits beside the target, the project-root template is
    still a concrete, readable alternative -- the redirect must not go silent
    just because the file lives in a subdirectory."""
    root = tmp_path / "root"
    root.mkdir()
    sub = tmp_path / "sub"
    sub.mkdir()
    (root / ".env.sample").write_text("")
    target = sub / ".env"
    res = run_hook(
        SCRIPT,
        file_payload("Read", target),
        env_overrides={"CLAUDE_PROJECT_DIR": str(root)},
    )
    assert res.returncode == 2
    assert str(root / ".env.sample") in res.stderr


def test_env_denial_with_no_template_tells_agent_to_ask(run_hook, tmp_path):
    """With no template anywhere, naming a nonexistent file would send the
    agent down a dead end -- the message must fall back to asking the user
    for the variable names/values instead."""
    root = tmp_path / "root"
    root.mkdir()
    sub = tmp_path / "sub"
    sub.mkdir()
    target = sub / ".env"
    res = run_hook(
        SCRIPT,
        file_payload("Read", target),
        env_overrides={"CLAUDE_PROJECT_DIR": str(root)},
    )
    assert res.returncode == 2
    assert "no template found" in res.stderr
    assert "ask the user" in res.stderr


# --- Allow paths (AC3) -----------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        ".env.example",
        ".env.sample",
        ".env.template",
        ".env.dist",
        "example.env",
        "sample.env",
        "template.env",
    ],
)
def test_allowlist_template_passes(run_hook, name):
    """Blocking the templates would train the agent to route around the guard
    instead of using the safe alternative its own denial message recommends."""
    res = run_hook(SCRIPT, file_payload("Read", f"/proj/{name}"))
    assert_allowed(res)


def test_ordinary_file_passes(run_hook):
    """Over-blocking ordinary project files would make the guard unusable."""
    res = run_hook(SCRIPT, file_payload("Read", "/proj/src/app.py"))
    assert_allowed(res)


# --- Grep: direct target vs directory (AC2, AC3) --------------------------------


def test_grep_path_direct_target_denies(run_hook):
    """A Grep `path` naming a cataloged file is as targeted a read as Read
    itself -- ripgrep would still open that one file."""
    res = run_hook(SCRIPT, grep_payload(path="/home/u/.aws/credentials"))
    assert_denied(res, "/home/u/.aws/credentials", "Cloud provider credentials")


def test_grep_glob_direct_target_denies(run_hook):
    """A `glob` naming a cataloged file is text-matched, not path-matched --
    a glob is a pattern/token, not always a full filesystem path -- but still
    denies the same as a direct path would."""
    res = run_hook(SCRIPT, grep_payload(glob=".env"))
    assert res.returncode == 2
    assert "Blocked:" in res.stderr
    assert ".env" in res.stderr


def test_grep_directory_path_allows(run_hook, tmp_path):
    """Grep over a directory has no direct sensitive target; denying it would
    block ordinary codebase search (spec Edge Case)."""
    res = run_hook(SCRIPT, grep_payload(path=str(tmp_path)))
    assert_allowed(res)


def test_grep_no_path_or_glob_allows(run_hook):
    """A Grep call with neither field has nothing to match against."""
    res = run_hook(SCRIPT, grep_payload())
    assert_allowed(res)


# --- Symlink dodge (AC5) ----------------------------------------------------------


def test_symlink_to_secret_denies(run_hook, tmp_path):
    """A symlink named innocuously but resolving to a real secret must still
    deny -- only the realpath check inside match_path catches it, and that
    check must survive the full script, not just the engine function."""
    secret = tmp_path / ".env"
    secret.write_text("")  # filename only -- no secret value is ever written
    link = tmp_path / "notes.txt"
    link.symlink_to(secret)
    res = run_hook(SCRIPT, file_payload("Read", link))
    assert res.returncode == 2
    assert "Blocked:" in res.stderr
    assert str(link) in res.stderr


# --- Fail-open contract (AC6) ------------------------------------------------------
#
# A real TTY and empty/malformed stdin all drive the identical `read_payload()
# is None` branch inside file_guard.py -- the script itself has no separate
# code path for "why" the payload was unreadable, so the cases below already
# exercise the guard's own fail-open logic for all three. (A literal terminal
# cannot be simulated through the shared `run_hook` launcher, which always
# pipes text; see hand-off notes for the corresponding engine-level gap.)


@pytest.mark.parametrize(
    "stdin_text",
    ["", "not json", "{ not valid json", "null", "[]", '"just a string"'],
)
def test_malformed_or_empty_stdin_fails_open(run_hook, stdin_text):
    """A harness bug or a manual test run must never wedge a tool call --
    exit 0, no denial output, whatever the garbage on stdin looks like."""
    res = run_hook(SCRIPT, stdin_text)
    assert_allowed(res)


def test_unknown_tool_is_ignored(run_hook):
    """This guard only examines Read/Edit/Write/MultiEdit/Grep; a Bash command
    referencing the same path is bash_guard.py's job, not this script's."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "cat .env"}})
    res = run_hook(SCRIPT, payload)
    assert_allowed(res)


def test_unmatched_tool_with_file_path_shaped_input_is_ignored(run_hook):
    """A tool outside the matcher set must be ignored even if its tool_input
    happens to carry a file_path-shaped field naming a secret."""
    payload = json.dumps({"tool_name": "Glob", "tool_input": {"file_path": "/proj/.env"}})
    res = run_hook(SCRIPT, payload)
    assert_allowed(res)


@pytest.mark.parametrize(
    "tool_input",
    [{}, {"file_path": None}, {"file_path": 123}, {"file_path": "   "}],
)
def test_missing_or_non_string_file_path_fails_open(run_hook, tool_input):
    """A malformed or absent file_path must never raise or deny -- it simply
    has nothing to match."""
    payload = json.dumps({"tool_name": "Read", "tool_input": tool_input})
    res = run_hook(SCRIPT, payload)
    assert_allowed(res)


def test_tool_input_not_a_dict_fails_open(run_hook):
    """A payload whose tool_input is not even a dict (harness bug or hand-built
    test input) must not raise."""
    payload = json.dumps({"tool_name": "Read", "tool_input": "not-a-dict"})
    res = run_hook(SCRIPT, payload)
    assert_allowed(res)


def test_grep_non_string_path_and_glob_fail_open(run_hook):
    payload = json.dumps({"tool_name": "Grep", "tool_input": {"path": 1, "glob": 2}})
    res = run_hook(SCRIPT, payload)
    assert_allowed(res)
