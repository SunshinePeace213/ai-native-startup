"""Catalog engine + shared helpers for the sensitive-files guards in this directory.

Plain importable module -- the sibling hook scripts (``file_guard.py``,
``bash_guard.py``) do ``import _common`` (Python puts the running script's
directory on ``sys.path``). Self-contained: the fail-open plumbing helpers are
copied/adapted from the ``security-scan`` family rather than imported across
directories (families never cross-import). Stdlib only.

Everything here fails open: a guard built on these helpers must never wedge a
tool call over plumbing. The engine functions (``match_path``,
``match_command_text``) never raise on weird input -- they return "no match"
(``None``) instead. Exit 2 belongs only to a confirmed catalog match, and that
decision stays in the guard scripts themselves.

The catalog is the decisions.md D2 table encoded as data. Two matcher kinds:

* **basename** -- an fnmatch-style pattern (``.env``, ``*.pem``, ``id_rsa*``)
  matched case-insensitively against a path's basename;
* **fragment** -- a slash-bounded substring of the normalized absolute path
  (``/.ssh/``, ``/etc/shadow``) so ``/.aws/`` never matches ``/.awsome/``.

Everything is compiled once at import.
"""

import fnmatch
import json
import os
import re
import select
import sys
from dataclasses import dataclass
from pathlib import Path

STDIN_TIMEOUT = 5.0


# --- Fail-open plumbing (mirrored from security-scan/_common.py) ---------------


def note(msg: str, hook: str | None = None) -> None:
    """One-line stderr note prefixed with the hook name.

    Default prefix is the running script's stem (e.g. ``file_guard``), so hooks
    need no configuration; pass ``hook`` to override.
    """
    prefix = hook or Path(sys.argv[0]).stem or "sensitive-files"
    print(f"[{prefix}] {msg}", file=sys.stderr)


def read_payload() -> dict | None:
    """Parse the hook payload JSON from stdin; None on any problem (fail-open).

    Bounded wait: a TTY, empty, unreadable, malformed, or timed-out stdin
    yields None. Expected no-payload cases stay silent; unexpected I/O errors
    and timeouts are noted to stderr.
    """
    try:
        stdin = sys.stdin
        if stdin is None or stdin.closed or stdin.isatty():
            return None
        ready, _, _ = select.select([stdin], [], [], STDIN_TIMEOUT)
        if not ready:
            note(f"no payload on stdin after {STDIN_TIMEOUT:g}s; allowing (fail-open)")
            return None
        raw = stdin.read()
    except Exception as exc:  # noqa: BLE001
        note(f"could not read stdin ({exc}); allowing (fail-open)")
        return None
    if not raw or not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except ValueError:
        return None  # malformed payload is an expected fail-open case
    return payload if isinstance(payload, dict) else None


def resolve_root() -> Path:
    """Project root: ``$CLAUDE_PROJECT_DIR`` when it is a directory, else script-relative.

    The hooks live at ``<root>/.claude/hooks/sensitive-files/``, so the fallback
    is three directories above this file's own directory.
    """
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if env_dir:
        path = Path(env_dir).expanduser()
        if path.is_dir():
            return path.resolve()
    return Path(__file__).resolve().parents[3]


# --- Template allowlist (decisions.md D3) -------------------------------------
#
# The ONLY escape hatch, and it exempts BASENAME rules only. A template name
# still DENIES when it sits inside a cataloged directory (a path-fragment match,
# e.g. ~/.aws/.env.example) or when its realpath is a live secret (a
# template-named symlink to a real .env). No env-var bypass and no project
# allowlist file exist by design.

TEMPLATE_ALLOWLIST: tuple[str, ...] = (
    ".env.example",
    ".env.sample",
    ".env.template",
    ".env.dist",
    "example.env",
    "sample.env",
    "template.env",
)
_ALLOWLIST_SET = frozenset(name.lower() for name in TEMPLATE_ALLOWLIST)


def is_allowlisted(basename: str) -> bool:
    """True when ``basename`` is one of the D3 template names (case-insensitive)."""
    return isinstance(basename, str) and basename.lower() in _ALLOWLIST_SET


# --- Command-text token boundaries --------------------------------------------
#
# In a Bash command a cataloged basename is only a match when it stands as its
# own shell token. Boundary chars (both sides): whitespace, quotes, and the
# shell control/redirection delimiters ``| & ; : , < > ( ) `` and backtick.
# The LEFT side additionally accepts ``/`` (path separator) and ``=`` (env
# assignment) so ``cat $HOME/.ssh/id_rsa`` and ``FOO=.env`` match; the RIGHT side
# does not, so ``.env`` inside ``.envrc`` or a longer name never matches.

_BOUNDARY = r"""\s'"|&;:,<>()`"""
_LEFT = rf"(?:^|(?<=[{_BOUNDARY}/=]))"
_RIGHT = rf"(?=[{_BOUNDARY}]|$)"
_NON_BOUNDARY = rf"[^{_BOUNDARY}/]"  # what an fnmatch '*' may span inside one token
# Left boundary for the RELATIVE form of a path fragment in command text: a
# command-token start (start-of-string / whitespace / quote / '=' / shell
# operator) but NOT a preceding '/'. A slash before the fragment is the absolute
# case, kept in the fragment's own leading-'/' branch, so `data.aws/file` (token
# starting `data.`) never matches the `/.aws/` fragment.
_LEFT_REL = rf"(?:^|(?<=[{_BOUNDARY}=]))"


def _fragment_regex(fragment: str) -> str:
    """Regex source for a path fragment, slash-bounded on the right.

    A fragment already opens with ``/`` (its own left boundary). One that ends
    with ``/`` (a directory, e.g. ``/.ssh/``) is self-bounded. One that ends at a
    filename (e.g. ``/etc/shadow``) gets a right lookahead so ``/etc/shadowy``
    can never match.
    """
    core = re.escape(fragment)
    if fragment.endswith("/"):
        return core
    return core + rf"(?=/|$|[{_BOUNDARY}])"


def _cmd_fragment_regex(fragment: str) -> str:
    """Command-text form of a path fragment.

    Matches the absolute form exactly as ``_fragment_regex`` does AND -- for home
    dot-directory fragments (those starting with ``/.``) -- the token-start
    relative form, so an ordinary relative reference like ``cat .aws/credentials``
    is denied just like ``/home/u/.aws/credentials`` (CX1-2). The relative left
    boundary is a command-token start, not a path ``/``, so ``data.aws/file`` is
    left in the absolute branch and never matches; the fragment's own trailing
    ``/`` (or the right lookahead) preserves the ``/.awsome/`` negative. System
    fragments that do NOT start with ``/.`` (``/etc/shadow``, ``/cookies``,
    ``/letsencrypt/live/``) keep the absolute-only form: their relative spellings
    are not meaningful sensitive paths and would only add false positives.
    """
    right = "" if fragment.endswith("/") else rf"(?=/|$|[{_BOUNDARY}])"
    absolute = re.escape(fragment) + right
    if fragment.startswith("/."):
        relative = _LEFT_REL + re.escape(fragment[1:]) + right
        return f"(?:{absolute}|{relative})"
    return absolute


def _cmd_basename_regex(pattern: str) -> str:
    """Translate an fnmatch basename pattern to a token-scoped regex source.

    ``*`` spans a run of non-boundary, non-slash chars and ``?`` one such char,
    so a wildcard stays inside a single shell token / path segment.
    """
    out = []
    for ch in pattern:
        if ch == "*":
            out.append(_NON_BOUNDARY + "*")
        elif ch == "?":
            out.append(_NON_BOUNDARY)
        else:
            out.append(re.escape(ch))
    return "".join(out)


# --- The catalog (decisions.md D2) --------------------------------------------


@dataclass(frozen=True)
class Rule:
    """One catalog pattern. ``kind`` is "basename" or "fragment".

    ``guidance`` is the per-category redirect line for the denial message
    (the ``env`` category overrides it with a live template lookup).
    ``path_re`` is the compiled matcher against a normalized absolute PATH:
    fnmatch-on-basename for basenames, a slash-bounded substring for fragments.
    ``cmd_re`` (fragments only) is the COMMAND-TEXT matcher -- it additionally
    accepts the token-start relative form (``.aws/`` as well as ``/.aws/``).
    """

    category_id: str
    label: str
    guidance: str
    kind: str
    pattern: str
    path_re: re.Pattern
    cmd_re: re.Pattern | None = None


# Each entry: (id, label, guidance, [basename patterns], [path fragments]).
# The guidance line names the safe alternative; the env category's is computed.
_CATALOG: list[tuple] = [
    (
        "env",
        "Environment files",
        "",  # computed: names the template that exists, else "ask the user".
        [".env", ".env.*", "*.env", ".envrc", ".flaskenv"],
        [],
    ),
    (
        "ssh",
        "SSH & auth keys",
        "SSH/auth key: never read key material; ask the user to run the command that needs it.",
        ["id_rsa*", "id_dsa*", "id_ecdsa*", "id_ed25519*", "*.ppk"],
        ["/.ssh/"],
    ),
    (
        "certs",
        "Certificates & private keys",
        "Certificate/private key: ask the user for the value or to run the tool that consumes it.",
        ["*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore", "*.asc", "*.gpg", "*.pgp"],
        ["/.gnupg/", "/letsencrypt/live/"],
    ),
    (
        "cloud",
        "Cloud provider credentials",
        "Cloud credential: use the provider CLI/SDK via the user; never read the raw file.",
        ["service-account*.json", "serviceaccount*.json", "serviceAccountKey.json"],
        [
            "/.aws/",
            "/.azure/",
            "/.config/gcloud/",
            "/.kube/",
            "/.docker/config.json",
            "/.oci/",
            "/.aliyun/",
            "/.config/doctl/",
            "/.fly/",
        ],
    ),
    (
        "pkg",
        "Package-manager credentials",
        "Package-manager credential: ask the user to run the authenticated command.",
        [".npmrc", ".yarnrc.yml", ".pypirc", ".netrc", "_netrc"],
        [
            "/.gem/credentials",
            "/.cargo/credentials",
            "/.m2/settings.xml",
            "/.gradle/gradle.properties",
            "/.composer/auth.json",
            "/.bundle/config",
            "/.config/pip/pip.conf",
            "/.nuget/nuget.config",
        ],
    ),
    (
        "vcs",
        "VCS & tool credentials",
        "VCS/tool credential: ask the user to run the authenticated command.",
        [".git-credentials"],
        ["/.config/gh/hosts.yml", "/.config/glab-cli/", "/.svn/auth/"],
    ),
    (
        "cicd",
        "CI/CD & IaC secrets",
        "CI/CD or IaC secret: ask the user for the value; never read the secret/state file.",
        [
            ".vault-token",
            ".terraformrc",
            "terraform.rc",
            "*.tfstate",
            "*.tfstate.*",
            "*.tfvars",
            "*.tfvars.json",
            ".secrets",
            ".vault_pass*",
        ],
        ["/.circleci/cli.yml"],
    ),
    (
        "framework",
        "Framework & app secrets",
        "Framework/app secret: ask the user for the specific value; never read the secret file.",
        [
            "master.key",
            "credentials.yml.enc",
            "secrets.yml",
            "secrets.yaml",
            "secrets.json",
            "secrets.toml",
            "local_settings.py",
        ],
        [],
    ),
    (
        "database",
        "Database credentials & data",
        "Database credential/data file: ask the user for connection details; never read the file.",
        [".pgpass", ".my.cnf", ".mylogin.cnf", "*.sqlite", "*.sqlite3", "*.db"],
        [],
    ),
    (
        "history",
        "Shell & REPL history",
        "Shell/REPL history may hold secrets: ask the user for the specific command or value.",
        [
            ".bash_history",
            ".zsh_history",
            ".sh_history",
            ".psql_history",
            ".mysql_history",
            ".rediscli_history",
            ".sqlite_history",
            ".node_repl_history",
            ".python_history",
        ],
        [],
    ),
    (
        "browser",
        "Browser & OS credential stores",
        "Browser/OS credential store: never read it; ask the user for the specific value.",
        ["logins.json", "key3.db", "key4.db", "*.kdbx", "*.keychain", "*.keychain-db"],
        ["/login data", "/cookies", "/etc/shadow", "/etc/gshadow"],
    ),
    (
        "kerberos",
        "Kerberos",
        "Kerberos credential: never read it; ask the user to run the authenticated command.",
        ["*.keytab", "krb5cc*"],
        [],
    ),
    (
        "wallet",
        "Crypto wallets",
        "Crypto wallet: never read wallet material; ask the user.",
        ["wallet.dat", "*.wallet", "UTC--*"],
        [],
    ),
    (
        "ai",
        "AI-tool auth",
        "AI-tool auth file: never read it; ask the user for what you need.",
        [".claude.json"],
        ["/.claude/.credentials.json", "/.codex/auth.json"],
    ),
]


def _build_rules() -> list[Rule]:
    rules: list[Rule] = []
    for category_id, label, guidance, basenames, fragments in _CATALOG:
        for pattern in basenames:
            path_re = re.compile(fnmatch.translate(pattern), re.IGNORECASE)
            rules.append(Rule(category_id, label, guidance, "basename", pattern, path_re))
        for pattern in fragments:
            path_re = re.compile(_fragment_regex(pattern), re.IGNORECASE)
            cmd_re = re.compile(_cmd_fragment_regex(pattern), re.IGNORECASE)
            rules.append(Rule(category_id, label, guidance, "fragment", pattern, path_re, cmd_re))
    return rules


_RULES: list[Rule] = _build_rules()
_BASENAME_RULES: list[Rule] = [r for r in _RULES if r.kind == "basename"]
_FRAGMENT_RULES: list[Rule] = [r for r in _RULES if r.kind == "fragment"]

# When a name matches both a literal and a wildcard rule (e.g. master.key hits
# both `master.key` framework and `*.key` certs, key3.db hits both `key3.db`
# browser and `*.db` database), prefer the literal for a precise category label.
# The deny is identical either way; a stable sort keeps table order within a group.
_BASENAME_RULES.sort(key=lambda r: "*" in r.pattern or "?" in r.pattern)

# One compiled alternation over the whole catalog for command-text scanning:
# the basename branch is token-bounded; the fragment branch is searched directly.
# The two named groups (bn / fr) tell the two branches apart; the exact rule is
# then recovered by re-testing the matched token against the per-kind rule list.
_bn_alt = "|".join(_cmd_basename_regex(r.pattern) for r in _BASENAME_RULES)
_fr_alt = "|".join(_cmd_fragment_regex(r.pattern) for r in _FRAGMENT_RULES)
_COMMAND_REGEX = re.compile(
    rf"{_LEFT}(?P<bn>{_bn_alt}){_RIGHT}|(?P<fr>{_fr_alt})",
    re.IGNORECASE,
)


# --- Path normalization + matching --------------------------------------------


def normalize_path(path: str) -> tuple[str, str]:
    """Return ``(normalized_abs, realpath)`` for a raw path string; never raises.

    ``expanduser`` -> absolutize against cwd (``abspath`` also ``normpath``s) ->
    ``realpath`` (resolves symlinks). The realpath is what catches a symlink that
    points at a secret; both forms are checked by ``match_path``.
    """
    expanded = os.path.expanduser(path)
    normalized = os.path.abspath(expanded)
    try:
        real = os.path.realpath(normalized)
    except OSError:
        real = normalized
    return normalized, real


def _match_single_path(abs_path: str) -> Rule | None:
    """Match one absolute path form. Fragments (directory membership) are checked
    first and are never allowlist-exempt; a basename is exempt only when it is a
    D3 template."""
    for rule in _FRAGMENT_RULES:
        if rule.path_re.search(abs_path):
            return rule
    base = os.path.basename(abs_path)
    if is_allowlisted(base):
        return None
    for rule in _BASENAME_RULES:
        if rule.path_re.match(base):
            return rule
    return None


def match_path(path: object) -> Rule | None:
    """The matched catalog rule for a file path, or None. Never raises.

    Both the normalized path and its realpath are checked, so a symlink to a
    secret is caught; a symlink NAMED like a template that resolves to a real
    secret is caught too (the allowlist exempts a form only when that form's own
    basename is a template).
    """
    if not isinstance(path, str) or not path.strip():
        return None
    try:
        normalized, real = normalize_path(path)
        candidates = (normalized,) if real == normalized else (normalized, real)
        for candidate in candidates:
            rule = _match_single_path(candidate)
            if rule is not None:
                return rule
    except Exception as exc:  # noqa: BLE001
        note(f"match_path failed for {path!r} ({exc}); allowing (fail-open)")
        return None
    return None


def _basename_rule_for(token: str) -> Rule | None:
    for rule in _BASENAME_RULES:
        if rule.path_re.match(token):
            return rule
    return None


def _fragment_rule_for(token: str) -> Rule | None:
    # cmd_re (not path_re) so the relative token form (`.aws/`) re-identifies its
    # rule as well as the absolute form (`/.aws/`) does.
    for rule in _FRAGMENT_RULES:
        if rule.cmd_re.search(token):
            return rule
    return None


def match_command_text(command: object) -> tuple[str, Rule] | None:
    """First ``(matched_token, rule)`` a Bash command references, or None. Never raises.

    Scans left to right; a token whose basename is a D3 template is skipped (so
    ``cat .env.example`` passes while ``cat .env`` is denied). Raw-string
    matching -- not shlex -- so paths inside quotes and interpreter one-liners
    (``python -c "open('.env')"``) are caught.
    """
    if not isinstance(command, str) or not command.strip():
        return None
    try:
        for m in _COMMAND_REGEX.finditer(command):
            token = m.group("bn")
            if token is not None:
                if is_allowlisted(token):
                    continue
                rule = _basename_rule_for(token)
            else:
                token = m.group("fr")
                rule = _fragment_rule_for(token)
            if rule is not None:
                return token, rule
    except Exception as exc:  # noqa: BLE001
        note(f"match_command_text failed ({exc}); allowing (fail-open)")
        return None
    return None


# --- Grep glob matching -------------------------------------------------------


def _glob_basename(pattern: str) -> str:
    """Last path segment of a Grep glob (``**/.env*`` -> ``.env*``)."""
    return pattern.rsplit("/", 1)[-1]


def _literal_prefix(segment: str) -> str:
    """Leading run of literal chars before the first fnmatch metacharacter.

    ``.env*`` -> ``.env``; ``secrets.*`` -> ``secrets.``; a segment that opens
    with a wildcard (``*.py``, ``*``, ``**``) has an EMPTY literal prefix.
    """
    out: list[str] = []
    for ch in segment:
        if ch in "*?[":
            break
        out.append(ch)
    return "".join(out)


def _rewrite_char_classes(segment: str) -> str:
    """Replace every fnmatch character class in a glob segment with ``?``.

    A class matches exactly one character, so ``?`` (any single char) matches a
    SUPERSET of the class's strings (``.env[.]local`` -> ``.env?local``,
    ``[a-z]*.py`` -> ``?*.py``, negated ``.env[!x]local`` -> ``.env?local``).
    Running the overlap check on this superset is conservative: any file the
    original glob selects the rewrite selects too, so a deny can only over-block
    (acceptable, security-first), never under-block (CX2-1: ripgrep expands
    character classes as ordinary glob syntax, not obfuscation, so a class glob
    that selects a cataloged name must deny like its ``*``/``?`` cousin). Classes
    are parsed exactly as ``fnmatch.translate`` does -- ``!`` negation and a
    leading ``]`` as a class member (``[]]``) -- so ``]`` and backslashes inside a
    class do not fool it. An UNCLOSED ``[`` is left as a literal ``[`` -- an
    fnmatch-compatible fallback (Python ``fnmatch`` also reads a lone ``[``
    literally) and superset-safe for us; ripgrep, by contrast, REJECTS such a glob
    as an invalid character class (``rg --glob '[env.local'`` errors), so it
    selects nothing, which makes treating it as a literal harmlessly conservative.
    """
    out: list[str] = []
    i, n = 0, len(segment)
    while i < n:
        ch = segment[i]
        if ch != "[":
            out.append(ch)
            i += 1
            continue
        j = i + 1
        if j < n and segment[j] == "!":  # negation marker
            j += 1
        if j < n and segment[j] == "]":  # a ']' right after '['/'[!' is a member
            j += 1
        while j < n and segment[j] != "]":
            j += 1
        if j >= n:  # no closing ']': fnmatch treats the '[' as a literal
            out.append("[")
            i += 1
        else:  # a closed class matches one char -> one '?'
            out.append("?")
            i = j + 1
    return "".join(out)


def _globs_intersect(glob: str, rule: str) -> bool:
    """True iff some filename matches both fnmatch patterns (case-insensitive).

    Both sides use ``*`` (any run), ``?`` (one char), and literals only -- the
    caller has rewritten the glob's character classes to ``?`` and the catalog's
    basename rules use only ``*``. Standard two-pattern intersection, computed as
    an ITERATIVE table DP (``dp[i][j]`` = can ``glob[i:]`` and ``rule[j:]`` match a
    common tail?), filled from the end backward so each cell reads only
    already-computed neighbours. Exact (never claims a false overlap) and complete
    (finds a shared name whenever one exists), verified against brute-force
    enumeration. Iterative on purpose: an earlier recursive version raised
    ``RecursionError`` on an over-long user glob (e.g. ``.env`` + 1000 ``*``) and,
    via the caller's broad ``except``, failed the guard OPEN -- a table has no such
    limit. O(len(glob) * len(rule)) time and space.
    """
    a, b = glob.lower(), rule.lower()
    la, lb = len(a), len(b)
    dp = [[False] * (lb + 1) for _ in range(la + 1)]
    dp[la][lb] = True  # both patterns exhausted -> the empty string matches both
    for i in range(la, -1, -1):
        for j in range(lb, -1, -1):
            if i == la and j == lb:
                continue
            if i < la and a[i] == "*":  # '*' = empty, or absorb the char b emits
                dp[i][j] = dp[i + 1][j] or (j < lb and dp[i][j + 1])
            elif j < lb and b[j] == "*":
                dp[i][j] = dp[i][j + 1] or (i < la and dp[i + 1][j])
            elif i < la and j < lb and (a[i] == "?" or b[j] == "?" or a[i] == b[j]):
                dp[i][j] = dp[i + 1][j + 1]
            # else: dp[i][j] stays False (a required literal/char cannot be matched)
    return dp[0][0]


def match_glob(pattern: object) -> Rule | None:
    """The catalog rule a Grep ``glob`` can select a cataloged file for, or None.

    Conservative by design (CX1-1): a ``glob`` is a selection PATTERN, not a path,
    so ``match_command_text``'s literal-token grammar cannot see that ``.env*`` or
    ``secrets.*`` select cataloged files. This matcher denies a glob only when it
    clearly targets a cataloged BASENAME family. A glob whose basename segment
    opens with a wildcard -- ``*.py``, ``**/*.md``, ``*``, ``src/**``, and (after
    character classes are rewritten to ``?``) ``[a-z]*.py`` -- has no
    catalog-shaped literal segment and always passes, matching the spec's "Grep
    over a directory is allowed" posture (A5); a glob that is exactly a D3
    template name (``.env.example``) passes too. That allow boundary is unchanged.

    Otherwise the glob's basename (character classes rewritten to ``?`` and runs
    of ``*`` collapsed to one -- together a superset of what it selects) is tested
    against each catalog basename rule three ways: (a) a concrete instance of the
    glob -- its wildcards filled with a filler char -- is itself a cataloged name
    (catches ``bar.env`` -> ``*.env`` while leaving ``README*`` alone, whose filled
    instance ends in the filler, not ``.env``); (b) for a PREFIX-anchored rule (one
    that does not open with ``*``) the glob's strings and the rule's strings
    intersect via ``_globs_intersect`` (catches ``.env[.]local`` -> ``.env.*``,
    ``id_r[s]a[0-9]*`` -> ``id_rsa*``, ``service-[a]ccount[0-9]*.json`` ->
    ``service-account*.json``); and (c) for a SUFFIX-anchored rule (one opening
    with ``*``, e.g. ``*.pem``/``*.env``), the intersection after removing every
    ``*`` from the rewritten glob. Removing ``*`` is sound because each star can
    match the empty string: every name selected by the star-free core is also
    selected by the original glob. It catches trailing-star targeting such as
    ``secret.pe?*`` -> core ``secret.pe?`` -> ``*.pem`` (CX4-1), while the empty
    literal-prefix return still allows broad suffix globs (``*.pem``), and cores
    without catalog overlap (``README*`` -> ``README``) stay allowed. Never
    raises: weird input yields None (fail-open).

    Directory-fragment targeting via a glob (e.g. ``.ssh/*``) is out of scope
    here: like a bare Grep directory target it follows the allow posture, and a
    Grep ``path`` naming such a file still routes through ``match_path``.
    """
    if not isinstance(pattern, str) or not pattern.strip():
        return None
    try:
        segment = _glob_basename(pattern.strip())
        if is_allowlisted(segment):  # exact D3 template name (before any rewrite)
            return None
        segment = _rewrite_char_classes(segment)
        segment = re.sub(r"\*+", "*", segment)  # collapse '*' runs (identical; shrinks the DP)
        if not _literal_prefix(segment):
            return None  # opens with a wildcard -> broad search -> allow
        seg_lower = segment.lower()
        core = seg_lower.replace("*", "")
        witness = segment.replace("*", "x").replace("?", "x")
        for rule in _BASENAME_RULES:
            if rule.path_re.match(witness):
                return rule
            if rule.pattern.startswith("*"):
                # A star can be empty, so every core match is a real glob match.
                # The empty-prefix return above preserves the broad-glob boundary.
                if _globs_intersect(core, rule.pattern):
                    return rule
            elif _globs_intersect(seg_lower, rule.pattern):
                return rule
    except Exception as exc:  # noqa: BLE001
        note(f"match_glob failed for {pattern!r} ({exc}); allowing (fail-open)")
        return None
    return None


# --- Denial message -----------------------------------------------------------

POLICY_LINE = (
    "Policy: never read, print, copy, or modify secret-bearing files; "
    "ask the user when a value is needed."
)
_NO_TEMPLATE = "no template found -- ask the user for the variable names/values you need"


def _find_env_template(path_or_token: str) -> str | None:
    """First existing D3 template in the target's directory, then the project root."""
    try:
        target = os.path.abspath(os.path.expanduser(path_or_token))
        target_dir = os.path.dirname(target)
    except Exception:  # noqa: BLE001
        target_dir = ""
    root = str(resolve_root())
    search_dirs = [d for d in (target_dir, root) if d]
    for directory in dict.fromkeys(search_dirs):  # dedupe, keep order
        for name in TEMPLATE_ALLOWLIST:
            candidate = os.path.join(directory, name)
            try:
                if os.path.isfile(candidate):
                    return candidate
            except OSError:
                continue
    return None


def _guidance_for(path_or_token: str, rule: Rule) -> str:
    if rule.category_id == "env":
        template = _find_env_template(path_or_token)
        if template:
            return f"Read '{template}' instead for the variable names."
        return _NO_TEMPLATE
    return rule.guidance


def denial_lines(path_or_token: str, rule: Rule) -> list[str]:
    """The three stderr lines the guards print on a confirmed match.

    Line 1 names the blocked path/token and its category; line 2 is the
    category redirect (a concrete ``.env`` template when one exists); line 3 is
    the standing policy. Exit 2 in the guard feeds these back to the agent.
    """
    blocked = f"Blocked: '{path_or_token}' matches sensitive category '{rule.label}'"
    return [blocked, _guidance_for(path_or_token, rule), POLICY_LINE]
