"""E2E block/allow/fail-open matrix for the Bash command-text guard
(`.claude/hooks/sensitive-files/bash_guard.py`).

Contract under test: any Bash command whose text references a cataloged
sensitive path is denied (exit 2, three-line stderr diagnostic naming the
matched token, its category label, and the standing policy), no matter how
the reference is delivered -- direct argument, shell-operator neighbor,
multiline continuation, or interpreter one-liner. Everyday commands and the
D3 template allowlist must stay untouched (exit 0, silent), and the fail-open
contract from decisions.md must hold for every kind of broken/foreign input:
never exit 1, and exit 2 is reserved for a confirmed catalog match.

Every fixture is a bare command string; no secret VALUE ever appears, only
filenames -- the guard matches command text, never file contents.
"""

import json

SCRIPT = "sensitive-files/bash_guard.py"


def bash_payload(command: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def assert_blocked(proc, token: str, label: str) -> None:
    """A block must exit 2 and hand the agent the matched token, its category
    label, and the standing policy line -- not just a bare non-zero exit."""
    assert proc.returncode == 2
    assert "Blocked:" in proc.stderr
    assert token in proc.stderr
    assert label in proc.stderr
    assert "ask the user when a value is needed" in proc.stderr


def assert_allowed(proc) -> None:
    """An allow must exit 0 with no deny output, so the guard stays invisible
    to everyday commands."""
    assert proc.returncode == 0
    assert "Blocked:" not in proc.stderr


# --- Deny: the spec Edge-Cases corpus, direct reference ----------------------


def test_denies_cat_env(run_hook):
    """The canonical case: reading a live .env leaks every secret it holds."""
    proc = run_hook(SCRIPT, bash_payload("cat .env"))
    assert_blocked(proc, ".env", "Environment files")


def test_denies_cp_env_to_tmp(run_hook):
    """Copying is as much an exfiltration route as reading -- the guard must
    catch the file as any command argument, not just after `cat`."""
    proc = run_hook(SCRIPT, bash_payload("cp .env /tmp/x"))
    assert_blocked(proc, ".env", "Environment files")


def test_denies_source_env(run_hook):
    """`source` loads .env into the current shell's environment -- a distinct
    but equally sensitive access pattern from a plain read."""
    proc = run_hook(SCRIPT, bash_payload("source .env"))
    assert_blocked(proc, ".env", "Environment files")


def test_denies_grep_over_env(run_hook):
    """Grepping a live .env for a key name still exposes the value in output."""
    proc = run_hook(SCRIPT, bash_payload("grep KEY .env"))
    assert_blocked(proc, ".env", "Environment files")


def test_denies_python_one_liner_opening_env(run_hook):
    """Raw-string matching (not shlex) must reach into an interpreter
    one-liner's quoted argument, the classic guard-dodge shape."""
    proc = run_hook(SCRIPT, bash_payload("python -c \"open('.env')\""))
    assert_blocked(proc, ".env", "Environment files")


def test_denies_cat_home_ssh_id_rsa(run_hook):
    """`$HOME/.ssh/id_rsa` is caught by the `/.ssh/` directory fragment before
    the `id_rsa` basename token is even reached -- proving fragment matching
    works inside an unexpanded shell variable path, not just a literal one."""
    proc = run_hook(SCRIPT, bash_payload("cat $HOME/.ssh/id_rsa"))
    assert_blocked(proc, "/.ssh/", "SSH & auth keys")


def test_denies_base64_env(run_hook):
    """Base64-wrapping is a common obfuscation attempt for exfiltrating a
    secret through a text channel; the bare filename argument still matches."""
    proc = run_hook(SCRIPT, bash_payload("base64 .env"))
    assert_blocked(proc, ".env", "Environment files")


# --- Deny: shell-operator boundary cases -------------------------------------


def test_denies_env_piped_to_base64(run_hook):
    """A shell operator directly after the path (no whitespace) must not break
    the right-side token boundary: `cat .env|base64` is still a read of .env."""
    proc = run_hook(SCRIPT, bash_payload("cat .env|base64"))
    assert_blocked(proc, ".env", "Environment files")


def test_denies_env_chained_with_and_and(run_hook):
    """Same boundary case with `&&`: the guard must not require whitespace
    before the operator to recognize the token ends there."""
    proc = run_hook(SCRIPT, bash_payload("cat .env&&echo done"))
    assert_blocked(proc, ".env", "Environment files")


def test_denies_env_redirected_to_copy(run_hook):
    """Same boundary case with `>`: a redirect glued to the path is still a
    read-then-copy of the secret file."""
    proc = run_hook(SCRIPT, bash_payload("cat .env>copy"))
    assert_blocked(proc, ".env", "Environment files")


def test_denies_multiline_command_with_env_on_its_own_line(run_hook):
    """A multi-statement command block must be scanned as a whole -- a
    sensitive reference buried on an inner line is not a safe dodge."""
    cmd = "echo start\ncat .env\necho done"
    proc = run_hook(SCRIPT, bash_payload(cmd))
    assert_blocked(proc, ".env", "Environment files")


# --- Deny: accepted false-positive tradeoff (A6) -----------------------------


def test_denies_prose_mention_of_env_as_accepted_tradeoff(run_hook):
    """`echo "create your .env"` merely mentions the filename in prose, but
    the guard has no way to distinguish that from a real reference without a
    much heavier parser -- decisions.md accepts this false positive rather
    than risk missing a real one. This test pins that intentional tradeoff:
    if it ever starts passing, the matcher's boundary rules loosened
    unexpectedly and prose sentences may not be the only new gap."""
    proc = run_hook(SCRIPT, bash_payload('echo "create your .env"'))
    assert_blocked(proc, ".env", "Environment files")


# --- Allow: everyday commands and the template allowlist ---------------------


def test_allows_cat_env_example(run_hook):
    """The D3 template allowlist is the only escape hatch: `.env.example`
    carries no live secret and must stay readable."""
    proc = run_hook(SCRIPT, bash_payload("cat .env.example"))
    assert_allowed(proc)


def test_allows_ls(run_hook):
    """A guard that taxes routine directory listing is unusable."""
    proc = run_hook(SCRIPT, bash_payload("ls -la"))
    assert_allowed(proc)


def test_allows_git_status(run_hook):
    """Ordinary VCS commands are the overwhelming common case and must be
    invisible to this guard."""
    proc = run_hook(SCRIPT, bash_payload("git status"))
    assert_allowed(proc)


def test_allows_awsome_directory_as_fragment_boundary_negative(run_hook):
    """`/.awsome/` must not match the `/.aws/` cloud-credential fragment --
    the slash-bounded boundary is what keeps the guard from false-positiving
    on any path that merely starts with the same letters."""
    proc = run_hook(SCRIPT, bash_payload("cat /.awsome/file"))
    assert_allowed(proc)


# --- Fail-open contract -------------------------------------------------------


def test_allows_empty_stdin(run_hook):
    """Fail-open: no payload at all must never wedge a Bash call."""
    proc = run_hook(SCRIPT, "")
    assert proc.returncode == 0


def test_allows_non_json_stdin(run_hook):
    """Fail-open: garbage input is a harness bug, not a policy violation."""
    proc = run_hook(SCRIPT, "not json")
    assert proc.returncode == 0


def test_allows_missing_tool_name_and_tool_input(run_hook):
    """Fail-open: a payload shape the guard has never seen must not crash
    into a deny -- an empty object has neither field."""
    proc = run_hook(SCRIPT, "{}")
    assert proc.returncode == 0


def test_allows_non_string_command(run_hook):
    """Fail-open: a non-string `command` (e.g. a stray number) must not reach
    the regex matcher and must not raise."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": 123}})
    proc = run_hook(SCRIPT, payload)
    assert proc.returncode == 0


def test_allows_non_bash_tool_name(run_hook):
    """The guard is scoped to Bash: a Read payload carrying the same sensitive
    filename must pass through untouched -- that is file_guard's job."""
    payload = json.dumps({"tool_name": "Read", "tool_input": {"file_path": ".env"}})
    proc = run_hook(SCRIPT, payload)
    assert proc.returncode == 0


def test_allows_missing_command_key(run_hook):
    """Fail-open: a Bash payload whose tool_input has no `command` key at all
    (not even null) must not raise on the missing key."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {}})
    proc = run_hook(SCRIPT, payload)
    assert proc.returncode == 0


def test_allows_non_dict_tool_input(run_hook):
    """Fail-open: a malformed payload where `tool_input` itself is not an
    object must not raise when the guard tries to read `command` from it."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": "not-a-dict"})
    proc = run_hook(SCRIPT, payload)
    assert proc.returncode == 0
