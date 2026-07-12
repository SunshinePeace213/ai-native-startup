"""Unit tests for the sensitive-files catalog engine
(`.claude/hooks/sensitive-files/_common.py`).

Contract under test: every decisions.md D2 category is reachable and denied by
name/path (`match_path`) and by command text (`match_command_text`); the D3
template allowlist is the only escape hatch and never exempts a file that lives
inside a secret directory; path normalization (tilde, relative/traversal,
symlink-via-realpath) defeats the dodges in the spec's Edge Cases; command-text
token boundaries deny the shell-operator cases while sparing ordinary commands;
and every engine function fails open (returns "no match") on weird input instead
of raising, because a guard must never wedge a tool call over plumbing.

The engine is loaded through the shared ``load_hook_module`` fixture (as ``eng``)
-- NOT ``import _common`` -- so it can never collide in ``sys.modules`` with the
other families' own ``_common`` when the whole suite runs under ``-n auto``.

Every fixture is a bare FILENAME or path; no secret VALUE is ever written -- the
guard matches names, never contents, so a secret literal would be pointless here
(and the security scanner + GitHub push protection both read this file).
"""

import pytest

# --- D3 template allowlist (spec-locked) --------------------------------------
ALLOWLIST_NAMES = [
    ".env.example",
    ".env.sample",
    ".env.template",
    ".env.dist",
    "example.env",
    "sample.env",
    "template.env",
]

# One (or more) blocked sample per D2 category, using names that do NOT collide
# with another category's wildcard, so the asserted category_id is unambiguous.
# Both matcher kinds (basename + fragment) are exercised where a category has both.
CATEGORY_SAMPLES = [
    ("/proj/.env", "env"),
    ("/proj/.envrc", "env"),
    ("/home/u/id_ed25519", "ssh"),
    ("/home/u/.ssh/config", "ssh"),
    ("/tmp/server.pem", "certs"),
    ("/home/u/.gnupg/pubring.kbx", "certs"),
    ("/tmp/service-account-key.json", "cloud"),
    ("/home/u/.aws/credentials", "cloud"),
    ("/home/u/.npmrc", "pkg"),
    ("/home/u/.m2/settings.xml", "pkg"),
    ("/home/u/.git-credentials", "vcs"),
    ("/home/u/.config/gh/hosts.yml", "vcs"),
    ("/proj/terraform.tfstate", "cicd"),
    ("/home/u/.circleci/cli.yml", "cicd"),
    ("/proj/config/secrets.yml", "framework"),
    ("/home/u/.pgpass", "database"),
    ("/data/app.sqlite3", "database"),
    ("/home/u/.zsh_history", "history"),
    ("/home/u/logins.json", "browser"),
    ("/etc/shadow", "browser"),
    ("/tmp/service.keytab", "kerberos"),
    ("/home/u/wallet.dat", "wallet"),
    ("/home/u/.claude.json", "ai"),
    ("/home/u/.codex/auth.json", "ai"),
]


@pytest.fixture(scope="module")
def eng(load_hook_module):
    return load_hook_module("sensitive-files/_common.py")


# --- Catalog coverage: every category is denied by name -----------------------


@pytest.mark.parametrize("path,expected", CATEGORY_SAMPLES)
def test_catalog_category_is_denied_by_path(eng, path, expected):
    """A leak from any one category is unrecoverable, so each must match -- and
    with the right label so the denial message points the agent at the right fix."""
    rule = eng.match_path(path)
    assert rule is not None, path
    assert rule.category_id == expected


def test_every_category_has_at_least_one_sample():
    """Guards this test file itself: if a category were dropped from the sample
    matrix the coverage claim would silently weaken."""
    catalog_ids = {
        "env", "ssh", "certs", "cloud", "pkg", "vcs", "cicd",
        "framework", "database", "history", "browser", "kerberos", "wallet", "ai",
    }  # fmt: skip
    assert {cid for _p, cid in CATEGORY_SAMPLES} == catalog_ids


# --- Allowlist: the only escape hatch -----------------------------------------


@pytest.mark.parametrize("name", ALLOWLIST_NAMES)
def test_allowlist_template_passes(eng, name):
    """Template files carry no live secret; blocking them would train the agent
    to route around the guard, so every D3 name must pass even though `.env.*`
    / `*.env` would otherwise match it."""
    assert eng.match_path(f"/proj/{name}") is None


def test_allowlist_does_not_exempt_a_file_inside_a_secret_dir(eng):
    """The allowlist exempts a basename, never directory membership: a
    template-named file sitting inside ~/.aws is still a read of that dir and
    must be denied."""
    rule = eng.match_path("/home/u/.aws/.env.example")
    assert rule is not None
    assert rule.category_id == "cloud"


# --- Path normalization: defeats the dodges (AC5) -----------------------------


def test_tilde_path_expands_before_matching(eng, monkeypatch, tmp_path):
    """`~/.aws/credentials` is the canonical secret; if the guard matched the raw
    string it would miss the expanded path."""
    monkeypatch.setenv("HOME", str(tmp_path))
    rule = eng.match_path("~/.aws/credentials")
    assert rule is not None
    assert rule.category_id == "cloud"


def test_relative_traversal_path_normalizes_and_matches(eng):
    """A relative/`..` path is a trivial evasion; normalization must land on the
    real basename before matching."""
    rule = eng.match_path("../../.env")
    assert rule is not None
    assert rule.category_id == "env"


def test_symlink_to_secret_is_denied_via_realpath(eng, tmp_path):
    """A symlink named `notes.txt` pointing at `.env` reads the secret; only the
    realpath check catches it."""
    secret = tmp_path / ".env"
    secret.write_text("")  # filename only -- no secret content
    link = tmp_path / "notes.txt"
    link.symlink_to(secret)
    rule = eng.match_path(str(link))
    assert rule is not None
    assert rule.category_id == "env"


def test_symlink_named_like_template_to_secret_is_denied(eng, tmp_path):
    """The allowlist must not become an evasion: a symlink NAMED `.env.example`
    that resolves to a real `.env` is still a secret read (allowlist applies only
    when the realpath is safe too)."""
    secret = tmp_path / ".env"
    secret.write_text("")
    link = tmp_path / ".env.example"
    link.symlink_to(secret)
    rule = eng.match_path(str(link))
    assert rule is not None
    assert rule.category_id == "env"


def test_plain_template_file_is_allowed(eng, tmp_path):
    """The mirror of the case above: a real (non-symlink) `.env.example` is safe
    and must pass, or templates become unreadable."""
    (tmp_path / ".env.example").write_text("")
    assert eng.match_path(str(tmp_path / ".env.example")) is None


# --- Fragment boundaries + case-insensitivity ---------------------------------


def test_fragment_is_slash_bounded(eng):
    """`/.aws/` must match a real `.aws` dir but not `.awsome`, or the guard
    would false-positive on unrelated paths (spec Edge Case)."""
    assert eng.match_path("/home/u/.awsome/config") is None
    assert eng.match_path("/home/u/.aws/config") is not None


def test_bare_secret_dir_path_is_allowed(eng):
    """The `/.ssh/` fragment guards files *inside* .ssh; the bare directory path
    (a Grep target, never a readable file) is allowed -- matching the spec's
    grep-over-directory rule."""
    assert eng.match_path("/home/u/.ssh") is None
    assert eng.match_path("/home/u/.ssh/id_rsa") is not None


def test_matching_is_case_insensitive(eng):
    """Case is not a security boundary: an upper/mixed-case name or command must
    match exactly as the lower-case form does."""
    assert eng.match_path("/proj/.ENV").category_id == "env"
    assert eng.match_path("/home/U/.SSH/config").category_id == "ssh"
    assert eng.match_command_text("CAT .ENV")[1].category_id == "env"


@pytest.mark.parametrize(
    "path",
    ["/proj/main.py", "/proj/README.md", "/proj/src/app.ts", "/proj/data/notes.md"],
)
def test_ordinary_files_are_allowed(eng, path):
    """Over-blocking ordinary project files would make the guard unusable, so
    non-cataloged names must pass untouched."""
    assert eng.match_path(path) is None


# --- Command-text matching (AC4 engine half) ----------------------------------

DENY_COMMANDS = [
    "cat .env",
    "cp .env /tmp/x",
    "source .env",
    "grep KEY .env",
    "python -c \"open('.env')\"",
    "cat $HOME/.ssh/id_rsa",
    "base64 .env",
    "cat .env|base64",
    "cat .env&&echo done",
    "cat .env>copy",
    "echo start\ncat .env\necho done",
]

ALLOW_COMMANDS = [
    "cat .env.example",
    "ls -la",
    "git status",
    "echo hello world",
    "cat /home/u/.awsome/config",
]


@pytest.mark.parametrize("command", DENY_COMMANDS)
def test_command_text_denies_corpus(eng, command):
    """Each is a real read/copy of a secret, including the shell-operator and
    multiline boundary cases the token grammar exists to catch."""
    assert eng.match_command_text(command) is not None


@pytest.mark.parametrize("command", ALLOW_COMMANDS)
def test_command_text_allows_corpus(eng, command):
    """Denying these would wedge everyday shell use; the `.awsome` case proves the
    fragment boundary holds inside a command too."""
    assert eng.match_command_text(command) is None


def test_command_text_returns_token_and_rule(eng):
    """Consumers show the matched token in the denial and route on the rule; both
    must be returned."""
    token, rule = eng.match_command_text("cat .env")
    assert token == ".env"
    assert rule.category_id == "env"


def test_command_allowlist_token_passes_but_a_real_secret_still_denies(eng):
    """The allowlist is applied to the matched token's basename, so a template
    token passes -- but a real `.env` elsewhere on the same line is still denied."""
    assert eng.match_command_text("cat .env.example") is None
    token, _rule = eng.match_command_text("cat .env.example .env")
    assert token == ".env"


# --- Denial message builder ---------------------------------------------------


def test_denial_lines_shape_for_non_env(eng):
    """The three lines carry the diagnostics the agent needs: what was blocked,
    which category, and the standing policy."""
    rule = eng.match_path("/home/u/id_rsa")
    lines = eng.denial_lines("/home/u/id_rsa", rule)
    assert len(lines) == 3
    assert lines[0].startswith("Blocked:")
    assert "/home/u/id_rsa" in lines[0]
    assert rule.label in lines[0]
    assert "never read, print, copy, or modify secret-bearing files" in lines[2]


def test_denial_lines_env_names_the_template_next_to_the_target(eng, tmp_path, monkeypatch):
    """An `.env` denial is only actionable if it names the template that actually
    exists next to the target -- so the agent reads that instead."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    (tmp_path / ".env.example").write_text("")
    target = str(tmp_path / ".env")
    rule = eng.match_path(target)
    lines = eng.denial_lines(target, rule)
    assert ".env.example" in lines[1]


def test_denial_lines_env_falls_back_to_project_root(eng, tmp_path, monkeypatch):
    """When no template sits beside the target, the project-root scan still finds
    one -- the redirect should not go silent just because the file is elsewhere."""
    root = tmp_path / "root"
    root.mkdir()
    proj = tmp_path / "proj"
    proj.mkdir()
    (root / ".env.sample").write_text("")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(root))
    target = str(proj / ".env")
    rule = eng.match_path(target)
    lines = eng.denial_lines(target, rule)
    assert ".env.sample" in lines[1]


def test_denial_lines_env_no_template_tells_agent_to_ask(eng, tmp_path, monkeypatch):
    """With no template anywhere, the message must fall back to asking the user
    rather than naming a file that does not exist."""
    root = tmp_path / "root"
    root.mkdir()
    proj = tmp_path / "proj"
    proj.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(root))
    target = str(proj / ".env")
    rule = eng.match_path(target)
    lines = eng.denial_lines(target, rule)
    assert "no template found" in lines[1]
    assert "ask the user" in lines[1]


# --- Fail-open contract (AC6 engine half) -------------------------------------


@pytest.mark.parametrize("value", [None, "", "   ", 123, b"/x/.env", ["/x/.env"], {}])
def test_match_path_never_raises_on_weird_input(eng, value):
    """A non-string or empty path must return None, never raise -- the guard
    fails open on malformed payloads."""
    assert eng.match_path(value) is None


@pytest.mark.parametrize("value", [None, "", "   ", 123, b"cat .env", ["cat .env"], {}])
def test_match_command_text_never_raises_on_weird_input(eng, value):
    """Same fail-open contract for the command matcher."""
    assert eng.match_command_text(value) is None
