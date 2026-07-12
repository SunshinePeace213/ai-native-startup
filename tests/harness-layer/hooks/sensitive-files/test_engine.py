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

import sys

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


def test_command_text_matches_relative_dotdir_fragment(eng):
    """A plain relative path is not obfuscation (CX1-2): a fragment-only rule
    (`/.aws/`, `/.docker/config.json`) must match its token-start relative form,
    so `cat .aws/credentials` denies like the absolute path does."""
    token, rule = eng.match_command_text("cat .aws/credentials")
    assert token == ".aws/"
    assert rule.category_id == "cloud"
    assert eng.match_command_text("cat .docker/config.json")[1].category_id == "cloud"


def test_command_text_relative_fragment_anchors_to_token_start(eng):
    """The relative branch must anchor to a command-token start, or it would
    false-positive on any word ending in the fragment: `data.aws/file` (token
    begins `data.`) must NOT match `/.aws/`, mirroring the `/.awsome/` negative."""
    assert eng.match_command_text("cat data.aws/file") is None


# --- Grep glob matching (CX1-1) -----------------------------------------------

GLOB_DENY = [".env*", "**/.env*", "secrets.*", "id_rsa*", "id_rsa.pub"]
GLOB_ALLOW = [
    "*.py",
    "**/*.md",
    "*",
    "src/**",
    ".env.example",
    "README*",
    "package.json",
    "*.tfstate",  # a bare `*.<ext>` stays allowed even for a cataloged extension
]


@pytest.mark.parametrize("glob", GLOB_DENY)
def test_match_glob_denies_catalog_targeting_globs(eng, glob):
    """A `glob` is a selection pattern, not a path: `match_command_text`'s
    literal-token grammar can't see that `.env*` selects `.env`, so these
    exited 0 before (AC2 bypass). A glob clearly targeting a cataloged basename
    family -- via a trailing-wildcard prefix (`.env*`), a suffix wildcard on a
    literal stem (`secrets.*`), or a literal cataloged name (`id_rsa.pub`) --
    must match."""
    assert eng.match_glob(glob) is not None


@pytest.mark.parametrize("glob", GLOB_ALLOW)
def test_match_glob_allows_broad_and_template_globs(eng, glob):
    """The conservative boundary: a glob whose basename opens with a wildcard has
    no catalog-shaped literal segment (`*.py`, `**/*.md`, `*`, `src/**`, and even
    `*.tfstate` on a cataloged extension) and is ordinary search; a literal
    non-cataloged name (`README*`, `package.json`) and the D3 template
    `.env.example` are safe. Denying any of these would make Grep unusable or
    push the agent around the guard."""
    assert eng.match_glob(glob) is None


def test_match_glob_reports_the_targeted_category(eng):
    """The denial routes on the returned rule, so a `.env`-family glob must carry
    the env category (not merely "some match")."""
    assert eng.match_glob(".env*").category_id == "env"
    assert eng.match_glob("id_rsa*").category_id == "ssh"


@pytest.mark.parametrize("value", [None, "", "   ", 123, [".env*"], {}])
def test_match_glob_never_raises_on_weird_input(eng, value):
    """Same fail-open contract as the other matchers: non-string or empty input
    returns None, never raises."""
    assert eng.match_glob(value) is None


# --- Grep glob matching: character classes (CX2-1) ----------------------------
#
# ripgrep expands fnmatch character classes as ordinary glob syntax -- not
# obfuscation -- so a class glob that selects a cataloged name must deny like its
# `*`/`?` cousin. The old witness heuristic substituted only `*`/`?`, leaving
# `[...]` intact, so every one of these exited 0 (AC2 bypass). None of these
# basename segments opens with a wildcard, so they sit OUTSIDE the documented
# broad-glob allow boundary. No secret VALUE appears -- these are names only.

GLOB_CLASS_DENY = [
    ".env[.]local",  # -> `.env.*` ([.] is exactly a dot, selecting `.env.local`)
    "id_r[s]a[0-9]*",  # -> `id_rsa*`
    "service-[a]ccount[0-9]*.json",  # -> `service-account*.json`
    ".env[!x]local",  # negated class includes `.`, so it still selects `.env.local`
    ".env.examp[l]e",  # -> `.env.*`; NOT the `.env.example` template literal
    "id_[r]sa",  # -> `id_rsa*` (no trailing wildcard; still a cataloged name)
]


@pytest.mark.parametrize("glob", GLOB_CLASS_DENY)
def test_match_glob_denies_character_class_targeting_globs(eng, glob):
    """A character class is rewritten to `?` (a superset: a class matches one
    char, `?` matches any) and then intersected with each prefix-anchored catalog
    rule, so a class glob that can select a cataloged file is denied like the
    equivalent wildcard glob."""
    assert eng.match_glob(glob) is not None


def test_match_glob_negated_class_denies_via_dot_member(eng):
    """`[!x]` matches any char except `x` -- including `.` -- so `.env[!x]local`
    still selects `.env.local`; the `?` superset rewrite preserves that."""
    assert eng.match_glob(".env[!x]local").category_id == "env"


def test_match_glob_class_template_lookalike_is_not_allowlisted(eng):
    """The D3 allowlist is an EXACT-name exemption, checked before the class
    rewrite: `.env.examp[l]e` is not the literal `.env.example`, so it is not
    exempt, and its `.env.examp?e` superset overlaps `.env.*` -> deny. The real
    template still passes."""
    assert eng.match_glob(".env.examp[l]e") is not None
    assert eng.match_glob(".env.example") is None


GLOB_CLASS_ALLOW = [
    "[a-z]*.py",  # opens with a class -> `?*.py` -> wildcard-opening -> allow
    "README[0-9].md",  # literal prefix `README`, no cataloged family overlaps it
    "[env.local",  # unclosed `[`: fnmatch reads it literally; ripgrep rejects it as invalid
    "src/**/[Tt]est*.go",  # broad code search, no catalog overlap
]


@pytest.mark.parametrize("glob", GLOB_CLASS_ALLOW)
def test_match_glob_allows_class_globs_without_catalog_overlap(eng, glob):
    """The allow boundary is unchanged: a class that OPENS the segment leaves an
    empty literal prefix (broad search), and a literal-prefix glob whose family no
    catalog rule shares stays allowed. An unclosed `[` is treated as a literal
    here (fnmatch-compatible); ripgrep instead rejects such a glob as an invalid
    character class, so it selects nothing either way."""
    assert eng.match_glob(glob) is None


# --- Grep glob matching: suffix-anchored targeting + no-regression (CX3-1) -----
#
# A class/`?` glob with a literal prefix and NO `*` after class rewrite is a
# length-bounded, narrow targeter: `secret.pe?` selects exactly the `secret.pe`+1
# names, one of which (`secret.pem`) a suffix rule (`*.pem`) covers. Round 2 ran
# only an x-filled witness for `*`-opening rules and skipped the intersection, so
# each of these exited 0 -- a live bypass -- and the reverse-fnmatch removal also
# regressed `x.?nv` (which selects `x.env`) from deny back to allow. Names only,
# no secret VALUE.

GLOB_SUFFIX_DENY = [
    ("secret.pe[m]", "certs"),  # -> secret.pe? selects secret.pem (*.pem)
    ("foo.ke[y]", "certs"),  # -> foo.ke? selects foo.key (*.key)
    ("state.tfstat[e]", "cicd"),  # -> state.tfstat? selects state.tfstate (*.tfstate)
    ("vars.tfvar[s]", "cicd"),  # -> vars.tfvar? selects vars.tfvars (*.tfvars)
    ("x.?nv", "env"),  # -> x.?nv selects x.env (*.env); round-2 no-regression
]


@pytest.mark.parametrize("glob,expected", GLOB_SUFFIX_DENY)
def test_match_glob_denies_bounded_suffix_targeting_globs(eng, glob, expected):
    """A length-bounded class/`?` glob (no `*` after rewrite) is intersected
    against suffix-anchored (`*`-opening) rules too, so a glob that can select a
    cataloged file is denied even when the covering rule opens with `*` -- and
    with the covering rule's category so the redirect is right."""
    rule = eng.match_glob(glob)
    assert rule is not None, glob
    assert rule.category_id == expected


GLOB_SUFFIX_ALLOW = ["*.pem", "*.key", "*.tfstate", "*.tfvars", "*.env", "README*"]


@pytest.mark.parametrize("glob", GLOB_SUFFIX_ALLOW)
def test_match_glob_allows_bare_suffix_and_prefix_star_globs(eng, glob):
    """The preserved allow boundary the new suffix-rule intersection must not
    cross: a bare suffix glob (`*.pem`) opens with `*` (empty literal prefix ->
    broad search), and `README*` reduces to `README`, which has no cataloged-suffix
    overlap. Denying either would break Grep over a whole extension."""
    assert eng.match_glob(glob) is None


# --- Grep glob matching: trailing-star suffix targeting (CX4-1) ---------------


@pytest.mark.parametrize(
    "glob,expected",
    [
        ("secret.pe[m]*", "certs"),
        ("secret.pem*", "certs"),
        ("foo*bar.pem", "certs"),
        ("state.tfstat[e]*", "cicd"),
    ],
)
def test_match_glob_denies_trailing_star_suffix_targeting_globs(eng, glob, expected):
    """CX4-1: a trailing star must not disable suffix-rule targeting detection;
    removing stars leaves a core that is genuinely selectable because every star
    can match empty, and the returned category must identify the covering rule."""
    rule = eng.match_glob(glob)
    assert rule is not None, glob
    assert rule.category_id == expected


@pytest.mark.parametrize("glob", ["README*", "x*"])
def test_match_glob_allows_trailing_star_without_suffix_overlap(eng, glob):
    """CX4-1 must preserve the locked allow boundary: star removal leaves cores
    with no cataloged suffix overlap, so these ordinary prefix searches stay
    allowed even though trailing stars now participate in suffix detection."""
    assert eng.match_glob(glob) is None


@pytest.mark.parametrize(
    "glob,expected",
    [("secret.p*m*", "certs"), ("sec*ret.pe[m]*", "certs")],
)
def test_match_glob_denies_internal_star_suffix_targeting_globs(eng, glob, expected):
    """CX5-1: internal stars must retain their exact intersection semantics;
    only the terminal star is the broad-search marker removed from the core."""
    rule = eng.match_glob(glob)
    assert rule is not None, glob
    assert rule.category_id == expected


def test_match_glob_allows_partial_suffix_before_broad_tail(eng):
    """CX5-1 locks the broad-tail boundary: removing only the terminal star from
    `secret.pe*` leaves `secret.pe`, which cannot overlap the cataloged `*.pem`."""
    assert eng.match_glob("secret.pe*") is None


# --- Grep glob matching: both-ends rule targeting (CX6-1) ---------------------


@pytest.mark.parametrize("glob", ["terraform.*state.backup*", "prod*.tfstate.old"])
def test_match_glob_denies_signaled_both_ends_targeting_globs(eng, glob):
    """CX6-1: literals that carry a three-character `.tfstate.` family signal
    enable exact intersection with internal stars intact, so constrained state
    targeters deny as cicd instead of losing their internal-star semantics."""
    rule = eng.match_glob(glob)
    assert rule is not None, glob
    assert rule.category_id == "cicd"


@pytest.mark.parametrize(
    "glob", ["prod.t[f]s[t]a[t]e.backup*", "terraform.tf[s]tate.backup*"]
)
def test_match_glob_denies_singleton_class_both_ends_targeters(eng, glob):
    """CX7-1: singleton classes are exact literals, not obfuscation, so their
    characters contribute to the family signal and intersecting targets deny."""
    rule = eng.match_glob(glob)
    assert rule is not None, glob
    assert rule.category_id == "cicd"


# --- Grep glob matching: over-long globs don't fail the DP open (CX3-2) --------
#
# `_globs_intersect` is an iterative table DP, so an over-long user glob can't
# raise RecursionError and (via the caller's broad except) fail the guard open.


def test_globs_intersect_handles_long_glob_without_recursion(eng):
    """A `.env`+1000-`*` glob would blow a recursive intersection's stack; the
    iterative DP returns a plain bool. `.env`+N-`*` is semantically `.env*`, which
    shares `.env` with the catalog's `.env` rule -> True."""
    assert eng._globs_intersect(".env" + "*" * 1000, ".env") is True


def test_match_glob_denies_unbounded_env_glob(eng):
    """`.env` + 1000 `*` collapses to `.env*` and selects `.env`; the guard must
    deny it (as env), not fail open on a recursion limit."""
    rule = eng.match_glob(".env" + "*" * 1000)
    assert rule is not None
    assert rule.category_id == "env"


def test_match_glob_allows_long_innocent_glob(eng):
    """The mirror: an equally long glob with no catalog overlap still passes --
    proof the DP doesn't crash either way, only denies real targeting."""
    assert eng.match_glob("a" + "*" * 1000 + ".py") is None


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


def test_tty_stdin_yields_none(eng, monkeypatch):
    """A human running a guard by hand must not hang it waiting on stdin. The
    TTY branch is the only read_payload fail-open path run_hook can't exercise
    in-process (a subprocess pipe is never a TTY), so it lives here."""

    class TTYStdin:
        closed = False

        def isatty(self) -> bool:
            return True

    monkeypatch.setattr(sys, "stdin", TTYStdin())
    assert eng.read_payload() is None
