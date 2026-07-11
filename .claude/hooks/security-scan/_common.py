"""Scanner engine + shared helpers for the security-scan hooks in this directory.

Plain importable module -- the sibling hook scripts do ``import _common``
(Python puts the running script's directory on ``sys.path``). Self-contained:
the fail-open plumbing helpers are copied/adapted from the auto-format
``_common.py`` rather than imported across directories. Stdlib only.

Everything here fails open: a hook built on these helpers must never wedge an
edit or a turn over plumbing. Exit 2 belongs only to a confirmed secret
finding, and that decision stays in the hooks themselves.
"""

import contextlib
import json
import os
import re
import select
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

VENDORED_DIRS = {"node_modules", ".venv", "dist"}
DIAGNOSTIC_CAP = 10
STDIN_TIMEOUT = 5.0

# Scanning limits.
MAX_SCAN_BYTES = 1024 * 1024  # 1 MiB: scan only the first MiB of a file
BINARY_SNIFF_BYTES = 8192  # a null byte in the first 8 KiB means "binary, skip"

# Session-state layout.
STATE_SUBDIR = (".claude", ".security-scan")
STATE_MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # prune state files older than 7 days


# --- Fail-open plumbing (mirrored from auto-format/_common.py) ----------------


def note(msg: str, hook: str | None = None) -> None:
    """One-line stderr note prefixed with the hook name.

    Default prefix is the running script's stem (e.g. ``post_write_scan``), so
    hooks need no configuration; pass ``hook`` to override.
    """
    prefix = hook or Path(sys.argv[0]).stem or "security-scan"
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
            note(f"no payload on stdin after {STDIN_TIMEOUT:g}s; skipping (fail-open)")
            return None
        raw = stdin.read()
    except Exception as exc:  # noqa: BLE001
        note(f"could not read stdin ({exc}); skipping (fail-open)")
        return None
    if not raw or not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except ValueError:
        return None  # malformed payload is an expected fail-open case
    return payload if isinstance(payload, dict) else None


def read_file_path() -> str | None:
    """``tool_input.file_path`` from the stdin payload; None unless a non-empty string."""
    payload = read_payload()
    if payload is None:
        return None
    tool_input = payload.get("tool_input")
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    return file_path if isinstance(file_path, str) and file_path.strip() else None


def resolve_root() -> Path:
    """Project root: ``$CLAUDE_PROJECT_DIR`` when it is a directory, else script-relative.

    The hooks live at ``<root>/.claude/hooks/security-scan/``, so the fallback
    is three directories above this file's own directory.
    """
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if env_dir:
        path = Path(env_dir).expanduser()
        if path.is_dir():
            return path.resolve()
    return Path(__file__).resolve().parents[3]


def is_vendored(file_path: Path | str, root: Path) -> bool:
    """True when ``file_path`` sits under node_modules/.venv/dist INSIDE ``root``.

    Matched on the path relative to the project root so an ancestor directory
    named e.g. ``dist`` outside the repo can't skip every file; paths outside
    the root are never vendored.
    """
    try:
        rel_parts = Path(file_path).resolve().relative_to(Path(root).resolve()).parts
    except ValueError:
        return False  # outside the project: not ours to skip
    return bool(VENDORED_DIRS.intersection(rel_parts))


def format_diagnostics(lines: list[str], cap: int = DIAGNOSTIC_CAP) -> str:
    """Join ``file:line rule message`` lines, capped at ``cap`` plus an "and N more" tail."""
    shown = list(lines[:cap])
    extra = len(lines) - cap
    if extra > 0:
        shown.append(f"... and {extra} more")
    return "\n".join(shown)


# --- Rule tables --------------------------------------------------------------


@dataclass(frozen=True)
class Rule:
    """A single detection rule. ``severity`` is "block" (secret) or "warn" (vuln).

    For secret rules the placeholder heuristics run on the matched value: the
    ``val`` named group when the pattern defines one, else the whole match.
    """

    rule_id: str
    severity: str
    pattern: re.Pattern
    message: str


# Secret rules -- severity "block". Each regex is tuned for high precision so a
# blocking match is almost always a real credential. Order is deterministic.
SECRET_RULES: list[Rule] = [
    Rule(
        "aws-access-key",
        "block",
        re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
        "AWS access key ID",
    ),
    Rule(
        "github-token",
        "block",
        re.compile(r"\b(?:gh[opusr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50,255})\b"),
        "GitHub token",
    ),
    Rule(
        "slack-token",
        "block",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,200}\b"),
        "Slack token",
    ),
    Rule(
        "anthropic-key",
        "block",
        re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,200}"),
        "Anthropic API key",
    ),
    Rule(
        "openai-project-key",
        "block",
        re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,200}"),
        "OpenAI project key",
    ),
    Rule(
        "openai-key",
        "block",
        re.compile(r"\bsk-[A-Za-z0-9]{40,200}\b"),
        "OpenAI API key",
    ),
    Rule(
        "google-api-key",
        "block",
        re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
        "Google API key",
    ),
    Rule(
        "private-key",
        "block",
        re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
        "PEM private key block",
    ),
    Rule(
        "jwt",
        "block",
        re.compile(
            r"\beyJ[A-Za-z0-9_-]{10,2000}\.eyJ[A-Za-z0-9_-]{10,2000}\.[A-Za-z0-9_-]{10,2000}\b"
        ),
        "JWT credential",
    ),
    Rule(
        "connection-string",
        "block",
        re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s:/@]+:(?P<val>[^\s:/@]+)@[^\s/]+"),
        "connection-string credential",
    ),
    Rule(
        "hardcoded-credential",
        "block",
        re.compile(
            r"""(?i)[A-Za-z0-9_]*(?:api_?key|secret|token|password)[A-Za-z0-9_]*"""
            r"""\s*[:=]\s*(?P<q>['"`])(?P<val>[^'"`\n]{8,})(?P=q)"""
        ),
        "hardcoded credential assignment",
    ),
]

# Vulnerability rules -- severity "warn". These match code *shapes*, not values,
# so the placeholder heuristics never apply to them.
VULN_RULES: list[Rule] = [
    Rule(
        "subprocess-shell-true",
        "warn",
        # subprocess.<call>( with shell=True AND an interpolation signal on the line.
        re.compile(
            r"subprocess\.\w+\("
            r"(?=.*shell\s*=\s*True)"
            r"(?=.*(?:f['\"]|\.format\(|%[\s(sd]|['\"]\s*\+|\+\s*['\"]|\+\s*\w))"
        ),
        "subprocess with shell=True and string interpolation",
    ),
    Rule(
        "pickle-load",
        "warn",
        re.compile(r"\bpickle\.loads?\("),
        "pickle.load deserializes untrusted data",
    ),
    Rule(
        "yaml-unsafe-load",
        "warn",
        re.compile(r"\byaml\.load\((?!.*(?:SafeLoader|CSafeLoader|safe_load))"),
        "yaml.load without SafeLoader",
    ),
    Rule(
        "sql-string-build",
        "warn",
        # .execute[many]( whose argument is an f-string / concat / % / .format().
        re.compile(
            r"\.execute(?:many)?\("
            r"(?=.*(?:f['\"]|\.format\(|['\"]\s*\+|\+\s*f?['\"]|['\"]\s*%\s*[\(\w]))"
        ),
        "SQL executed on an interpolated string",
    ),
    Rule(
        "eval-exec",
        "warn",
        # Bare eval(/exec( (not a .method call) on a non-literal argument.
        re.compile(r"(?<![.\w])(?:eval|exec)\(\s*(?!['\"`)])"),
        "eval/exec on a non-literal argument",
    ),
    Rule(
        "inner-html",
        "warn",
        re.compile(r"\.innerHTML\s*=(?!=)"),
        "innerHTML assignment (XSS risk)",
    ),
    Rule(
        "document-write",
        "warn",
        re.compile(r"\bdocument\.write(?:ln)?\("),
        "document.write (XSS risk)",
    ),
    Rule(
        "dangerously-set-inner-html",
        "warn",
        re.compile(r"dangerouslySetInnerHTML"),
        "dangerouslySetInnerHTML (XSS risk)",
    ),
    Rule(
        "child-process-exec",
        "warn",
        re.compile(r"\b(?:child_process\.)?exec(?:Sync)?\(\s*`"),
        "child_process.exec with a template literal",
    ),
]

ALL_RULES: list[Rule] = SECRET_RULES + VULN_RULES

# Suppression.
PRAGMA = re.compile(r"security-scan:\s*allow", re.IGNORECASE)
PLACEHOLDER_TOKENS = (
    "example",
    "sample",
    "placeholder",
    "changeme",
    "your",
    "dummy",
    "fake",
    "xxx",
    "redacted",
)
_ANGLE_TEMPLATE = re.compile(r"<[^>]+>")


# --- Scanning -----------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """One rule match: file path, 1-based line, rule id, severity, short message."""

    file: str
    line: int
    rule: str
    severity: str
    message: str


def finding_line(finding: Finding) -> str:
    """A single ``file:line rule message`` diagnostic line for the agent."""
    return f"{finding.file}:{finding.line} {finding.rule} {finding.message}"


def is_placeholder(value: str) -> bool:
    """True when a matched secret value is an obvious non-secret placeholder.

    Applies to secret values only (vuln rules match code shapes, not values).
    """
    if not value:
        return True
    low = value.lower()
    if any(token in low for token in PLACEHOLDER_TOKENS):
        return True
    if _ANGLE_TEMPLATE.search(value):
        return True
    stripped = value.strip()
    return bool(stripped) and len(set(stripped)) == 1  # all-same-character


def _match_value(rule: Rule, match: re.Match) -> str:
    return match.group("val") if "val" in rule.pattern.groupindex else match.group(0)


def _scan_line(
    line: str, prev_line: str | None, lineno: int, file_str: str, findings: list[Finding]
) -> None:
    # An inline pragma on the flagged line or the line immediately above suppresses it.
    if PRAGMA.search(line) or (prev_line is not None and PRAGMA.search(prev_line)):
        return
    for rule in ALL_RULES:
        match = rule.pattern.search(line)
        if match is None:
            continue
        if rule.severity == "block" and is_placeholder(_match_value(rule, match)):
            continue
        findings.append(Finding(file_str, lineno, rule.rule_id, rule.severity, rule.message))


def scan_file(path: Path | str, root: Path | str) -> list[Finding]:
    """Scan ``path`` for secret/vuln findings. Never raises; fails open to ``[]``.

    Guards, in order: vendored dirs are skipped silently; a missing file is
    skipped with a note; a binary file (null byte in the first 8 KiB) is
    skipped silently; a file over 1 MiB is scanned to the first MiB with a
    truncation note; decode errors are replaced so weird content never raises.
    Findings are ordered by line, then by rule-table order within a line.
    """
    path = Path(path)
    root = Path(root)
    if is_vendored(path, root):
        return []
    if not path.is_file():
        note(f"{path} no longer exists; skipping")
        return []
    try:
        with open(path, "rb") as handle:
            data = handle.read(MAX_SCAN_BYTES + 1)
    except OSError as exc:
        note(f"could not read {path} ({exc}); skipping")
        return []
    if b"\x00" in data[:BINARY_SNIFF_BYTES]:
        return []  # binary file: skip silently
    if len(data) > MAX_SCAN_BYTES:
        data = data[:MAX_SCAN_BYTES]
        note(f"{path} exceeds 1 MiB; scanning first 1 MiB only")
    text = data.decode("utf-8", errors="replace")
    file_str = str(path)
    findings: list[Finding] = []
    prev_line: str | None = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        _scan_line(line, prev_line, lineno, file_str, findings)
        prev_line = line
    return findings


# --- Session state ------------------------------------------------------------


def _state_dir(root: Path | str) -> Path:
    return Path(root).joinpath(*STATE_SUBDIR)


def _sanitize_session_id(session_id: str) -> str:
    """Reduce a session id to a safe single path segment (no dots, slashes, ..)."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "")
    return safe[:128] or "session"


def _empty_state() -> dict:
    return {"baseline": [], "tracked": [], "last_head": ""}


def _as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def state_path(root: Path | str, session_id: str) -> Path:
    """Absolute path of the JSON state file for ``session_id`` under ``root``."""
    return _state_dir(root) / f"{_sanitize_session_id(session_id)}.json"


def load_state(root: Path | str, session_id: str) -> dict:
    """Load session state; return an empty state on a missing or corrupt file (fail-open)."""
    path = state_path(root, session_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _empty_state()
    if not isinstance(data, dict):
        return _empty_state()
    last_head = data.get("last_head")
    return {
        "baseline": _as_str_list(data.get("baseline")),
        "tracked": _as_str_list(data.get("tracked")),
        "last_head": last_head if isinstance(last_head, str) else "",
    }


def save_state(root: Path | str, session_id: str, state: dict) -> None:
    """Write session state, deduping the sets. Creates the state dir as needed.

    Writes to a temp file then ``os.replace`` -- atomic enough for the
    single-writer-per-session use here.
    """
    path = state_path(root, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    last_head = state.get("last_head")
    payload = {
        "baseline": sorted(set(_as_str_list(state.get("baseline")))),
        "tracked": sorted(set(_as_str_list(state.get("tracked")))),
        "last_head": last_head if isinstance(last_head, str) else "",
    }
    tmp = path.parent / f".{path.name}.{os.getpid()}.tmp"
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    os.replace(tmp, path)


def prune_stale_states(root: Path | str, max_age_seconds: int = STATE_MAX_AGE_SECONDS) -> None:
    """Delete state files whose mtime is older than ``max_age_seconds``. Errors ignored."""
    directory = _state_dir(root)
    if not directory.is_dir():
        return
    cutoff = time.time() - max_age_seconds
    for entry in directory.glob("*.json"):
        with contextlib.suppress(OSError):
            if entry.stat().st_mtime < cutoff:
                entry.unlink()


# --- Git helpers (session_baseline.py / track_bash_writes.py) -----------------
#
# Path convention: every path recorded in session state (``baseline`` and
# ``tracked``) is an absolute filesystem path. ``tool_input.file_path``
# (post_write_scan.py) already arrives absolute from Claude Code and is
# stored as-is. ``git status``/``git diff`` output is root-relative because
# these helpers always invoke git with ``cwd=root``; the functions below
# resolve those relative paths against ``root`` before returning them, so
# both sources land in the same path space for state storage and for the
# stop-sweep to look up later.


def run_git(args: list[str], cwd: Path | str) -> tuple[int, str, str] | None:
    """Run ``git <args>`` in ``cwd``; None when git can't be spawned or times out."""
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=15
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.returncode, proc.stdout, proc.stderr


def parse_porcelain_paths(output: str) -> list[str]:
    """Root-relative paths from ``git status --porcelain`` text.

    Each line is ``XY path`` or, for a rename/copy, ``XY old -> new``; only
    the new path is kept. A path git wrapped in double quotes (unusual
    characters) is unwrapped as-is; escape sequences inside are not decoded
    (not needed for this repo's filenames).
    """
    paths = []
    for line in output.splitlines():
        if len(line) < 4:
            continue
        rest = line[3:]
        if " -> " in rest:
            rest = rest.split(" -> ", 1)[1]
        rest = rest.strip()
        if len(rest) >= 2 and rest[0] == '"' and rest[-1] == '"':
            rest = rest[1:-1]
        if rest:
            paths.append(rest)
    return paths


def git_dirty_paths(root: Path | str) -> list[str] | None:
    """Absolute paths of every dirty (index + worktree) entry under ``root``.

    None means git couldn't be spawned or ``root`` isn't a repo -- a
    fail-open signal distinct from "clean repo", which returns ``[]``.
    """
    res = run_git(["status", "--porcelain"], root)
    if res is None:
        return None
    code, out, _err = res
    if code != 0:
        return None
    root = Path(root)
    return [str(root / rel) for rel in parse_porcelain_paths(out)]


def git_head(root: Path | str) -> str | None:
    """Current HEAD commit sha; None when unborn, unreadable, or no git."""
    res = run_git(["rev-parse", "HEAD"], root)
    if res is None:
        return None
    code, out, _err = res
    if code != 0:
        return None
    head = out.strip()
    return head or None


def git_diff_paths(root: Path | str, old_rev: str, new_rev: str) -> list[str] | None:
    """Absolute paths changed between ``old_rev`` and ``new_rev``; None if the diff fails."""
    res = run_git(["diff", "--name-only", f"{old_rev}..{new_rev}"], root)
    if res is None:
        return None
    code, out, _err = res
    if code != 0:
        return None
    root = Path(root)
    return [str(root / line) for line in out.splitlines() if line.strip()]
