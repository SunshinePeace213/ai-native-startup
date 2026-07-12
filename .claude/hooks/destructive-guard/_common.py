"""Guard engine + shared helpers for the destructive-guard hook in this directory.

Plain importable module -- the sibling entrypoint does ``import _common``
(Python puts the running script's directory on ``sys.path``). Stdlib only, no
shebang and no PEP 723 marker: this is a library, not an entrypoint.

The engine is pure inspection: it compiles a flat table of high-precision
regexes and reports which ones a Bash command string matches. It never
executes, shells out, or writes anything. Everything fails open -- the
plumbing helpers below yield ``None`` on any stdin trouble so the guard can
never wedge an unrelated tool call. The exit-2 deny decision lives in the
entrypoint, not here.

Rules carry two severities: ``deny`` (the command is cancelled, exit 2 with an
agent-readable BLOCKED/Why/Fix block) and ``ask`` (the human is asked to
approve per call via ``permissionDecision: "ask"``). Patterns use word
boundaries and are never anchored to string start, so wrapper prefixes
(``sudo``, ``env X=1``, ``nohup``, ``timeout``) and compound commands
(``cd / && rm -rf *``) still match.
"""

import json
import re
import select
import sys
from dataclasses import dataclass
from pathlib import Path

STDIN_TIMEOUT = 5.0


# --- Fail-open plumbing (mirrored from security-scan/_common.py) ---------------


def note(msg: str, hook: str | None = None) -> None:
    """One-line stderr note prefixed with the hook name.

    Default prefix is the running script's stem (e.g. ``block_destructive``),
    so hooks need no configuration; pass ``hook`` to override.
    """
    prefix = hook or Path(sys.argv[0]).stem or "destructive-guard"
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


# --- Rule dataclass ------------------------------------------------------------


@dataclass(frozen=True)
class Rule:
    """A single detection rule.

    ``severity`` is "deny" (cancel + exit 2) or "ask" (route to the human).
    ``message`` names what tripped (shown in both the BLOCKED header and the
    ask reason); ``why`` is the one-line danger explanation on the Why: line;
    ``fix_hint`` is the safe alternative on the Fix: line.
    """

    rule_id: str
    category: str
    severity: str
    pattern: re.Pattern
    message: str
    why: str
    fix_hint: str


# --- Protected roots & critical files (constants) ------------------------------

# Human-facing reference of the protected roots; the regex below encodes the
# same set plus the normalization rule. ``/mnt/<letter>`` are the WSL Windows
# drive mounts. ``/tmp`` is deliberately NOT here (see decisions.md).
PROTECTED_ROOTS = (
    "/", "/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/lib32", "/lib64",
    "/opt", "/proc", "/root", "/sbin", "/srv", "/sys", "/usr", "/var",
    "/mnt/<drive-letter>", "~", "$HOME (also \"$HOME\" and ${HOME})",
)  # fmt: skip

# Critical system files; the regex below encodes the same set (with the
# ``sudoers.d/*``, ``cron*`` and ``/boot/*`` wildcards).
CRITICAL_FILES = (
    "/etc/passwd", "/etc/shadow", "/etc/group", "/etc/sudoers", "/etc/sudoers.d/*",
    "/etc/fstab", "/etc/hosts", "/etc/ssh/sshd_config", "/etc/cron*", "/boot/*",
)  # fmt: skip

# Single-component roots under "/" (longest first so /lib64 wins over /lib).
_NAMED_ROOTS = (
    "bin", "boot", "dev", "etc", "home", "lib64", "lib32", "lib",
    "opt", "proc", "root", "sbin", "srv", "sys", "usr", "var",
)  # fmt: skip

# Quote handling. Bash concatenates adjacent quoted and unquoted fragments into
# ONE word and strips the quotes before running the command; this scanner sees
# the raw string. evaluate() reproduces that by removing every ' and " up front
# (see _strip_quotes), so the patterns below scan a de-quoted copy and use STRICT
# word boundaries -- a quote is never treated as a word boundary here.
#   _OB  -- an OPTION-token boundary: the flag is preceded by whitespace or the
#           start of the (de-quoted) string. Zero-width, so it never widens a
#           filename match (a hyphen inside "my-report" is preceded by a letter,
#           not whitespace, so it still isn't read as a flag) but a real ` -rf`
#           token -- including one that was `-'r'f` before de-quoting -- is.
_OB = r"(?<!\S)"

# A protected-root TARGET, per the normalization rule: the bare root, the root
# with a single trailing slash, or the root with a trailing /* -- but NOT a
# deeper sub-path. Two branches: named roots / mnt / home variants (which take
# an optional trailing "/" or "/*"), and the bare filesystem root "/" (whose
# "/" + trailing-slash + "/*" forms collapse to "/" or "/*"). Each branch
# carries its own leading lookbehind (reject "./etc", "/home/x/etc") and
# trailing lookahead (reject "/etc/nginx", "~/projects", "$HOMEDIR"). Quotes are
# already stripped before matching, so no quote-tolerance is baked in here.
_PROTECTED_ROOT = (
    r"(?:"
    r"(?<![\w./~-])(?:/mnt/[A-Za-z]|/(?:" + "|".join(_NAMED_ROOTS) + r")"
    r"|~|\$\{HOME\}|\$HOME)(?:/\*|/)?(?![\w*./-])"
    r"|(?<![\w./~-])/\*?(?![\w*./-])"
    r")"
)

# A critical-file TARGET. Fixed names plus the sudoers.d/cron/boot wildcards. A
# leading (?<![\w./~-]) rejects a longer host path (`x/etc/passwd`, `./etc/hosts`)
# so only the real file matches -- quotes are already stripped, so a de-quoted
# `truncate x/etc/passwd` correctly falls through. Each FIXED literal ends in
# (?![\w.-]) so a suffix like ".bak" does NOT match (`/etc/passwd.bak` is not the
# real file); the intentional cron*/sudoers.d/boot wildcards are left open so
# they still match their sub-paths.
_CRITICAL_FILE = (
    r"(?<![\w./~-])(?:"
    r"/etc/(?:"
    r"(?:passwd|shadow|group|fstab|hosts|ssh/sshd_config)(?![\w.-])"
    r"|sudoers(?:\.d(?:/[^\s;&|]+)?)?(?![\w.-])"
    r"|cron[^\s;&|]*"
    r")"
    r"|/boot/[^\s;&|]+"
    r")"
)

# Home-directory prefix (bare tilde, $HOME, ${HOME}) for profile/history paths.
_HOME = r"(?:~|\$\{HOME\}|\$HOME)"

# A raw block / disk device node (never /dev/null, /dev/zero, ... -- those are
# not block devices, so device rules built on this can't match them).
_BLOCKDEV = (
    r"/dev/(?:sd[a-z]+\d*|hd[a-z]+\d*|vd[a-z]+\d*|xvd[a-z]+\d*"
    r"|nvme\d+n\d+(?:p\d+)?|mmcblk\d+(?:p\d+)?)\b"
)

# Scanning fragments. _SEG stays inside one command segment (stops at ; & |);
# _PIPE may cross a pipe (for the pipe-to-shell / decode-then-exec rules whose
# whole point is a "| sh" stage); _SEGG is the greedy form for the whole-segment
# negative lookaheads in the unbounded dd rule.
_SEG = r"[^;&|\n]*?"
_PIPE = r"[^;\n]*?"
_SEGG = r"[^;&|\n]*"

# A redirect (>, >>) or a tee writing into the TARGET that follows. The tee
# branch spans one command segment up to that target; because (?:A|B)C matches
# the same language as AC|BC, appending a TARGET yields "> TARGET" or
# "tee ... TARGET" -- the shape the write rules below share.
_REDIR_OR_TEE = r"(?:>{1,2}\s*|(?<!\S)tee\b" + _SEG + r")"

# Recursive-flag and force-flag detectors. Each requires a real option token
# (``_OB`` -- preceded by whitespace or start, so a filename like "my-report" is
# never read as a flag) and matches combined clusters in any order: ``-rf``,
# ``-fr``, ``-vrf``, ``-r`` / ``-R``, and the long ``--recursive`` / ``--force``.
_REC = _OB + r"(?:--recursive|-[A-Za-z]*[rR][A-Za-z]*)\b"
_FORCE = _OB + r"(?:--force|-[A-Za-z]*f[A-Za-z]*)\b"
_REC_R = _OB + r"(?:--recursive|-[A-Za-z]*R[A-Za-z]*)\b"  # chmod/chown use -R

# Fork-bomb: the two authoritative patterns from spec.md, combined so B's
# ``(\w+)`` is capture group 1 (A defines no groups) and its ``\1`` backrefs
# resolve. (a) classic colon form; (b) generalized named form requiring the
# self-pipe and the background ``&``.
_FORK_A = r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"
_FORK_B = r"\b(\w+)\s*\(\s*\)\s*\{[^}]*\b\1\b\s*\|\s*\b\1\b[^}]*&[^}]*\}"


# --- The rule table ------------------------------------------------------------
#
# One flat, ordered table; the category is per-rule metadata. evaluate()
# preserves this order. Deny rules are cancelled outright; ask rules route to
# the human. Deny wins over ask when a single command trips both.

RULES: list[Rule] = [
    # --- Destructive File Operations ---
    Rule(
        "rm-recursive-force",
        "Destructive File Operations",
        "deny",
        re.compile(r"\brm\b(?=" + _SEG + _REC + r")(?=" + _SEG + _FORCE + r")"),
        "recursive force delete (rm -r + -f, any spelling)",
        "rm -rf permanently erases directories and their contents with no undo, "
        "and one bad path can wipe the working tree or the WSL/Windows drive.",
        "mv <target> ~/.Trash/  (AGENTS.md safe-delete policy)",
    ),
    Rule(
        "rm-recursive-protected",
        "Destructive File Operations",
        "deny",
        re.compile(r"\brm\b(?=" + _SEG + _REC + r")(?=" + _SEG + _PROTECTED_ROOT + r")"),
        "recursive delete targeting a protected system/home root",
        "a recursive rm on a root like /, /etc, ~ or a /mnt drive mount can "
        "destroy the OS, your home directory, or the Windows filesystem.",
        "mv <target> ~/.Trash/, or scope the delete to a specific sub-path you own.",
    ),
    Rule(
        "find-delete-protected",
        "Destructive File Operations",
        "deny",
        re.compile(
            r"\bfind\b(?=" + _SEG + _PROTECTED_ROOT + r")"
            r"(?=" + _SEG + r"(?:-delete\b|-exec\b" + _SEG + r"\brm\b))"
        ),
        "find -delete / -exec rm rooted at a protected system/home root",
        "find walks the whole tree under a protected root and deletes every "
        "match, so a loose predicate erases far more than intended.",
        "Point find at a specific sub-directory you own, or list matches first "
        "(drop -delete) and remove them deliberately.",
    ),
    Rule(
        "mv-protected-root",
        "Destructive File Operations",
        "deny",
        re.compile(
            r"\bmv\b(?:(?:\s+-{1,2}\S+)*\s+" + _PROTECTED_ROOT + r"(?=\s)"
            # /dev/null must be the final destination: after it, only trailing
            # redirections (`2>/tmp/err`) and/or a `# comment` may precede the
            # segment end -- another positional arg means /dev/null was a source.
            r"|" + _SEG + _OB + r"/dev/null\b"
            r"(?:\s*\d*>>?&?\s*[^\s;&|#]*)*\s*(?:#[^\n]*)?(?=[;&|\n]|$))"
        ),
        "mv of a protected root, or mv into /dev/null (a silent delete)",
        "moving a protected root relocates the whole system/home tree, and "
        "moving into /dev/null discards the source entirely.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- Disk Overwrite Operations ---
    Rule(
        "dd-to-block-device",
        "Disk Overwrite Operations",
        "deny",
        re.compile(r"\bdd\b" + _SEG + r"(?<!\S)of=" + _BLOCKDEV),
        "dd writing directly to a raw block device (of=/dev/sdX ...)",
        "dd onto a disk device overwrites partitions and filesystems in place, "
        "regardless of count=, and is unrecoverable.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    Rule(
        "redirect-to-block-device",
        "Disk Overwrite Operations",
        "deny",
        re.compile(r">{1,2}\s*" + _BLOCKDEV),
        "shell redirect onto a raw block device (> /dev/sdX)",
        "redirecting output onto a disk device corrupts its partition table "
        "and filesystems; /dev/null and /dev/stdout are never affected.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    Rule(
        "shred-device",
        "Disk Overwrite Operations",
        "deny",
        re.compile(r"\bshred\b" + _SEG + _OB + r"/dev/(?!null\b|std(?:out|in|err)\b)[A-Za-z]"),
        "shred targeting a /dev device node",
        "shred overwrites a device repeatedly to make its data unrecoverable, "
        "destroying whatever disk or partition it names.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- Format Operations ---
    Rule(
        "mkfs",
        "Format Operations",
        "deny",
        re.compile(r"\bmkfs(?:\.[\w-]+)?\b"),
        "mkfs filesystem creation",
        "mkfs lays a fresh filesystem over its target, erasing every existing "
        "partition and file on it.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    Rule(
        "wipe-partition",
        "Format Operations",
        "deny",
        re.compile(
            r"(?:\bwipefs\b|\bblkdiscard\b"
            r"|\bsgdisk\b" + _SEG + r"(?:" + _OB + r"-Z\b|--zap-all\b))"
        ),
        "partition/signature wipe (wipefs, blkdiscard, sgdisk -Z)",
        "these erase partition tables or discard every block on a device, "
        "making its data unrecoverable.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- Fork Bombs & Resource Exhaustion ---
    Rule(
        "fork-bomb",
        "Fork Bombs & Resource Exhaustion",
        "deny",
        re.compile(r"(?:" + _FORK_A + r"|" + _FORK_B + r")"),
        "fork bomb (self-replicating function that pipes into itself in the background)",
        "a fork bomb spawns processes exponentially until the machine runs out "
        "of PIDs and memory and must be power-cycled.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    Rule(
        "unbounded-fill",
        "Fork Bombs & Resource Exhaustion",
        "deny",
        re.compile(
            r"(?:"
            r"\bcat\b"
            + _SEG
            + _OB
            + r"/dev/(?:zero|urandom|random)\b"
            + _SEG
            + r">{1,2}(?!\s*/dev/null\b)(?!\s*/dev/stdout\b)\s*"
            r"|\byes\b" + _SEG + r">{1,2}(?!\s*/dev/null\b)(?!\s*/dev/stdout\b)\s*"
            r"|\bdd\b(?!"
            + _SEGG
            + r"\bcount=)(?!"
            + _SEGG
            + r"\bof=/dev/null\b)"
            + _SEG
            + r"\bif=/dev/(?:zero|urandom|random)\b"
            r")"
        ),
        "unbounded write from an infinite source (fills the disk)",
        "cat/yes/dd streaming an endless source into a file or device fills the "
        "filesystem until the machine is unusable; a count= or /dev/null target is fine.",
        "Bound the write (add count= to dd) or redirect to /dev/null.",
    ),
    Rule(
        "memory-exhaust",
        "Fork Bombs & Resource Exhaustion",
        "deny",
        re.compile(
            r"(?:"
            r"\btail\b" + _SEG + _OB + r"/dev/zero\b"
            r"|\$\(\s*cat\b[^)]*?/dev/(?:zero|urandom|random)\b"
            r"|\$\(\s*yes\s*\)"
            r"|`\s*cat\b[^`]*?/dev/(?:zero|urandom|random)\b"
            r"|`\s*yes\s*`"
            r")"
        ),
        "unbounded read into memory (tail /dev/zero, $(yes), $(cat /dev/zero))",
        "reading an infinite generator into a buffer or command substitution "
        "grows memory without limit until the process (or box) is OOM-killed.",
        "Bound the read (head -c N) instead of capturing an endless stream.",
    ),
    # --- Dangerous Permission Changes ---
    Rule(
        "chmod-recursive-protected",
        "Dangerous Permission Changes",
        "deny",
        re.compile(r"\bchmod\b(?=" + _SEG + _REC_R + r")(?=" + _SEG + _PROTECTED_ROOT + r")"),
        "recursive chmod on a protected system/home root",
        "recursively re-permissioning a root like / breaks the OS (sudo, ssh, "
        "and services stop trusting their files) and is hard to undo.",
        "Scope the chmod to the specific directory that actually needs it.",
    ),
    Rule(
        "chown-recursive-protected",
        "Dangerous Permission Changes",
        "deny",
        re.compile(r"\bchown\b(?=" + _SEG + _REC_R + r")(?=" + _SEG + _PROTECTED_ROOT + r")"),
        "recursive chown on a protected system/home root",
        "recursively re-owning a root like / hands system files to the wrong "
        "user and breaks privileged services and login.",
        "Scope the chown to the specific directory that actually needs it.",
    ),
    Rule(
        "chmod-777-recursive",
        "Dangerous Permission Changes",
        "ask",
        re.compile(r"\bchmod\b(?=" + _SEG + _REC_R + r")(?=" + _SEG + r"(?<!\d)0?777\b)"),
        "recursive chmod 777 (world-writable) on a non-protected target",
        "0777 makes every file world-writable, which is almost always a "
        "security mistake rather than the intent.",
        "Use the least-privilege mode the task needs (e.g. 755 for dirs, 644 "
        "for files); approve only if world-writable is truly intended.",
    ),
    # --- System File Overwriting ---
    Rule(
        "overwrite-critical-file",
        "System File Overwriting",
        "deny",
        re.compile(_REDIR_OR_TEE + _CRITICAL_FILE),
        "redirect or tee onto a critical system file",
        "clobbering files like /etc/passwd, /etc/sudoers or /etc/fstab can lock "
        "you out, break boot, or grant unintended privileges.",
        "Edit the file with the Write/Edit tool, or ask the user to run it via the ! prefix.",
    ),
    Rule(
        "truncate-critical-file",
        "System File Overwriting",
        "deny",
        re.compile(r"\btruncate\b" + _SEG + _CRITICAL_FILE),
        "truncate on a critical system file",
        "truncating /etc/passwd, /etc/fstab, sshd_config and the like blanks "
        "essential system state and can break login or boot.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- Critical Process Termination ---
    Rule(
        "kill-all",
        "Critical Process Termination",
        "deny",
        re.compile(
            r"\b(?:kill|killall|pkill)\b"
            r"(?=" + _SEG + r"(?:" + _OB + r"-9\b|" + _OB + r"-(?:KILL|SIGKILL)\b"
            r"|" + _OB + r"-s\s+(?:KILL|SIGKILL|9)\b))"
            r"(?=" + _SEG + r"(?:" + _OB + r"-1\b|(?<![\w./-])1\b|\binit\b|\bsystemd\b))"
        ),
        "SIGKILL aimed at every process or at PID 1 / init / systemd",
        "kill -9 -1 or killing PID 1 takes down every process or the init "
        "system, hard-crashing the session or the machine.",
        "Target the specific PID you mean, and prefer the default signal over -9.",
    ),
    # --- Remote Code Execution ---
    Rule(
        "pipe-to-shell",
        "Remote Code Execution",
        "ask",
        re.compile(
            r"(?:"
            r"\b(?:curl|wget)\b" + _PIPE + r"\|\s*(?:sudo\s+)?(?:sh|bash|zsh|dash|ksh)\b"
            r"|\b(?:sh|bash|zsh|dash|ksh)\b" + _PIPE + r"<\(\s*(?:curl|wget)\b"
            r"|\b(?:sh|bash|zsh|dash|ksh|eval)\b" + _PIPE + r"\$\(\s*(?:curl|wget)\b"
            r")"
        ),
        "piping a downloaded script straight into a shell (curl | bash)",
        "executing remote content unread runs whatever the server sends -- a "
        "compromised or wrong URL runs arbitrary code with your privileges.",
        "Download to a file, read it, then run it; approve only if you trust the source.",
    ),
    Rule(
        "obfuscated-exec",
        "Remote Code Execution",
        "deny",
        re.compile(
            r"(?:\bbase64\b" + _PIPE + r"(?:-d\b|--decode\b)"
            r"|\bxxd\b"
            + _PIPE
            + r"(?:-r\b|--revert\b))"
            + _PIPE
            + r"\|\s*(?:sudo\s+)?(?:sh|bash|zsh|dash|ksh)\b"
        ),
        "decode-then-execute (base64 -d | sh, xxd -r | sh)",
        "decoding a blob and piping it into a shell hides what will run and has "
        "no legitimate agent use.",
        "If you need to run a script, write its readable source with the Write tool first.",
    ),
    # --- Environment Manipulation ---
    Rule(
        "profile-write",
        "Environment Manipulation",
        "ask",
        re.compile(
            _REDIR_OR_TEE + r"(?:" + _HOME + r"/\.(?:bashrc|bash_profile|profile|zshrc)"
            r"|/etc/(?:profile|environment|bash\.bashrc))(?![\w.-])"
        ),
        "write into a shell profile / environment file",
        "profile writes persist across every future shell, so a bad line can "
        "sabotage or hijack later sessions.",
        "Set what you need for this call inline; approve only if a persistent change is intended.",
    ),
    Rule(
        "ld-preload",
        "Environment Manipulation",
        "ask",
        re.compile(r"\bLD_PRELOAD\s*=\s*\S*\.so\b"),
        "LD_PRELOAD injection of a shared object into a command",
        "LD_PRELOAD forces a .so into the process, letting it override libc "
        "functions -- a classic code-injection / rootkit vector.",
        "Run the command without LD_PRELOAD; approve only if the preload is deliberate.",
    ),
    # --- Cron & Scheduled Tasks ---
    Rule(
        "crontab-wipe",
        "Cron & Scheduled Tasks",
        "deny",
        re.compile(r"\bcrontab\b" + _SEG + _OB + r"-[A-Za-z]*r[A-Za-z]*\b"),
        "crontab -r (wipes the user's crontab)",
        "crontab -r deletes the entire crontab with no confirmation and no undo.",
        "Back up with `crontab -l` first, or edit with `crontab -e`.",
    ),
    Rule(
        "cron-write",
        "Cron & Scheduled Tasks",
        "deny",
        re.compile(_REDIR_OR_TEE + r"/etc/cron[^\s;&|]*"),
        "redirect or tee into /etc/cron*",
        "writing system cron files installs or clobbers scheduled jobs that run "
        "as root, a persistence and privilege vector.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- Network Manipulation ---
    Rule(
        "firewall-flush",
        "Network Manipulation",
        "deny",
        re.compile(
            r"(?:\biptables\b" + _SEG + r"(?:" + _OB + r"-F\b|--flush\b)"
            r"|\bnft\b" + _SEG + r"flush\s+ruleset\b"
            r"|\bufw\b" + _SEG + r"disable\b)"
        ),
        "flushing/disabling the firewall (iptables -F, nft flush ruleset, ufw disable)",
        "dropping all firewall rules exposes every listening service to the network at once.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    Rule(
        "iface-down",
        "Network Manipulation",
        "deny",
        re.compile(
            r"(?:\bip\b" + _SEG + r"\blink\b" + _SEG + r"\bset\b" + _SEG + r"\bdown\b"
            r"|\bifconfig\b" + _SEG + r"\bdown\b)"
        ),
        "bringing a network interface down",
        "taking an interface down can cut the box off the network -- including "
        "the connection you are working over.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- History & Log Manipulation ---
    Rule(
        "history-wipe",
        "History & Log Manipulation",
        "deny",
        re.compile(
            r"(?:\bhistory\b" + _SEG + _OB + r"-c\b"
            r"|\b(?:rm|truncate)\b" + _SEG + _HOME + r"/\.(?:bash_history|zsh_history)(?![\w.-])"
            r"|>{1,2}\s*" + _HOME + r"/\.(?:bash_history|zsh_history)(?![\w.-]))"
        ),
        "wiping shell history",
        "clearing history erases the record of what was run, which destroys an "
        "audit trail and is rarely a legitimate build step.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    Rule(
        "log-wipe",
        "History & Log Manipulation",
        "deny",
        re.compile(
            r"(?:\b(?:rm|truncate)\b" + _SEG + r"(?<!\S)/var/log(?:/[^\s;&|]*)?\b"
            r"|>{1,2}\s*/var/log/[^\s;&|]+)"
        ),
        "deleting or truncating /var/log",
        "wiping system logs destroys diagnostic and audit records and can hide other damage.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- Kernel & System Operations ---
    Rule(
        "power-state",
        "Kernel & System Operations",
        "deny",
        re.compile(
            r"(?:\b(?:shutdown|reboot|poweroff|halt)\b"
            r"|\b(?:init|telinit)\b\s+[06]\b"
            r"|\bsystemctl\b" + _SEG + r"\b(?:poweroff|reboot|halt|suspend|hibernate)\b)"
        ),
        "power-state change (shutdown, reboot, halt, poweroff, suspend)",
        "these stop or restart the machine, killing the session and every running job immediately.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    Rule(
        "kernel-modules",
        "Kernel & System Operations",
        "deny",
        re.compile(
            r"(?:\b(?:insmod|rmmod)\b|\bmodprobe\b" + _SEG + r"(?:" + _OB + r"-r\b|--remove\b))"
        ),
        "loading/unloading a kernel module (insmod, rmmod, modprobe -r)",
        "changing kernel modules alters the running kernel and can crash or "
        "compromise the whole system.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    Rule(
        "kernel-mem",
        "Kernel & System Operations",
        "deny",
        re.compile(
            r"(?:>{1,2}\s*/dev/k?mem\b|\bof=/dev/k?mem\b"
            r"|\bsysctl\b" + _SEG + _OB + r"-w\b"
            r"|>{1,2}\s*/proc/sys/[^\s;&|]+)"
        ),
        "writing kernel memory / tunables (/dev/mem, sysctl -w, /proc/sys/*)",
        "writing raw kernel memory or live tunables can corrupt kernel state "
        "and destabilize or compromise the system.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- Symbolic Link Attacks ---
    Rule(
        "symlink-critical",
        "Symbolic Link Attacks",
        "deny",
        re.compile(
            r"\bln\b(?=" + _SEG + _OB + r"-[A-Za-z]*s[A-Za-z]*\b)"
            r"(?=" + _SEG + _CRITICAL_FILE + r")"
        ),
        "symlink involving a critical system file",
        "creating or repointing a link at a file like /etc/passwd or "
        "/etc/sudoers can redirect trusted reads/writes to attacker content.",
        "ask the user to run it themselves via the ! prefix.",
    ),
    # --- Git Security ---
    Rule(
        "git-force-push",
        "Git Security",
        "ask",
        re.compile(
            r"\bgit\b"
            + _SEG
            + r"\bpush\b"
            + _SEG
            + r"(?:--force(?:-with-lease)?\b|"
            + _OB
            + r"-[A-Za-z]*f[A-Za-z]*\b)"
        ),
        "git push --force / -f (including --force-with-lease)",
        "a force push overwrites remote history and can discard teammates' "
        "commits that aren't in your local branch.",
        "Prefer a normal push; approve only if rewriting the remote branch is intended.",
    ),
    Rule(
        "git-hard-reset",
        "Git Security",
        "ask",
        re.compile(r"\bgit\b" + _SEG + r"\breset\b" + _SEG + r"--hard\b"),
        "git reset --hard (discards uncommitted work)",
        "--hard throws away all uncommitted changes in the working tree and "
        "index with no recovery.",
        "Stash or commit first; approve only if discarding local changes is intended.",
    ),
    Rule(
        "git-clean-force",
        "Git Security",
        "ask",
        re.compile(
            r"\bgit\b"
            + _SEG
            + r"\bclean\b"
            + _SEG
            + r"(?:--force\b|"
            + _OB
            + r"-[A-Za-z]*f[A-Za-z]*\b)"
        ),
        "git clean -f (deletes untracked files)",
        "git clean -f permanently removes untracked files; with -x it also "
        "removes ignored files like build output and local config.",
        "Preview with `git clean -n` first; approve only if the deletion is intended.",
    ),
    Rule(
        "git-history-rewrite",
        "Git Security",
        "ask",
        re.compile(r"\bgit\b" + _SEG + r"\bfilter-(?:branch|repo)\b"),
        "git history rewrite (filter-branch / filter-repo)",
        "rewriting history changes every commit id and can corrupt or diverge "
        "the repo for everyone who has pulled it.",
        "approve only if a full history rewrite is intended.",
    ),
    Rule(
        "git-remote-delete",
        "Git Security",
        "ask",
        re.compile(
            r"\bgit\b" + _SEG + r"\bpush\b" + _SEG + r"(?:--delete\b|" + _OB + r"-d\b|\s:[\w./-]+)"
        ),
        "git push deleting a remote branch",
        "pushing a delete (--delete or :branch) removes the branch on the remote for everyone.",
        "approve only if deleting the remote branch is intended.",
    ),
    # --- User & Account Manipulation ---
    Rule(
        "account-destroy",
        "User & Account Manipulation",
        "deny",
        re.compile(
            r"(?:\b(?:userdel|groupdel)\b"
            r"|\bpasswd\b" + _SEG + r"(?:\broot\b|" + _OB + r"-d\b|" + _OB + r"--delete\b)"
            r"|\busermod\b(?=" + _SEG + r"(?:" + _OB + r"-L\b|--lock\b))(?=" + _SEG + r"\broot\b))"
        ),
        "user/account manipulation (userdel, groupdel, passwd root, usermod -L root)",
        "deleting accounts or changing/locking the root password can lock "
        "everyone out of the system.",
        "ask the user to run it themselves via the ! prefix.",
    ),
]


# --- Evaluation ----------------------------------------------------------------


def _strip_quotes(command: str) -> str:
    """Drop shell quote characters so quoted/fragmented spellings scan like bare ones.

    Bash concatenates adjacent quoted and unquoted fragments into ONE word and
    strips the quotes before running the command, so ``rm -'r'f x`` runs as
    ``rm -rf x`` and ``rm x"-rf" y`` runs as ``rm x-rf y``. This scanner sees the
    raw string; removing every ``'`` and ``"`` reproduces Bash's in-word quote
    removal closely enough that the strict-boundary patterns above then read the
    same tokens Bash would. Pure string work -- it never shells out or executes.
    """
    return command.replace("'", "").replace('"', "")


def evaluate(command: str) -> tuple[list[Rule], list[Rule]]:
    """Return ``(deny_matches, ask_matches)`` for ``command``, in rule-table order.

    The command is de-quoted first (see ``_strip_quotes``) so both tiers scan the
    same shell-word-normalized copy. Pure inspection: every rule whose pattern is
    found in that copy is collected into the list for its severity. Order is
    preserved so the entrypoint reports the highest-priority (earliest) matches first.
    """
    command = _strip_quotes(command)
    deny_matches: list[Rule] = []
    ask_matches: list[Rule] = []
    for rule in RULES:
        if rule.pattern.search(command):
            (deny_matches if rule.severity == "deny" else ask_matches).append(rule)
    return deny_matches, ask_matches
