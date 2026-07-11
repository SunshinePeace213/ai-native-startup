"""Unit tests for the security-scan engine (`.claude/hooks/security-scan/_common.py`).

Contract under test: secret rules are high-precision blockers (a positive AND a
negative per rule), vuln rules are code-shape warnings (a positive AND a negative
per rule), suppression works via pragma and every placeholder-heuristic class,
and the guards + session-state helpers fail open exactly as the hooks require.

The engine module is loaded under a unique name (`security_scan_common`) via
importlib -- NOT `import _common` -- so it can never collide in `sys.modules`
with the auto-format hooks' own `_common` when both suites run under `-n auto`.

CRITICAL: no committed line here may itself match a secret rule (the hook family
this enables, and GitHub push protection, would flag this file). Every
secret-shaped fixture is assembled from pieces at runtime; the on-disk source
never contains a matchable literal.
"""

import importlib.util
import os
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / ".claude" / "hooks" / "security-scan" / "_common.py"
_spec = importlib.util.spec_from_file_location("security_scan_common", MODULE_PATH)
sec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sec)

Q = '"'  # a double quote, so no fixture writes a bare quoted literal in source


@pytest.fixture
def scan(tmp_path):
    """Write ``text`` to a real file under an isolated root and return its findings."""

    def _scan(text: str, name: str = "sample.py", root: Path | None = None):
        root = root or tmp_path
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        return sec.scan_file(target, root)

    return _scan


def rule_ids(findings) -> set[str]:
    return {f.rule for f in findings}


def kv(name: str, value: str) -> str:
    """A ``name = "value"`` assignment assembled from pieces (never a raw literal)."""
    return name + " = " + Q + value + Q


# --- Secret rules: one positive + one negative each ---------------------------
# Each POSITIVE value is assembled from fragments and deliberately varied so it
# never trips a placeholder heuristic; each NEGATIVE is a near-miss that must NOT
# fire the rule.


def test_aws_access_key(scan):
    assert "aws-access-key" in rule_ids(scan(kv("x", "AKIA" + "IOSFODNN7REALKEY")))
    assert "aws-access-key" not in rule_ids(scan(kv("region", "AKIA" + "SHORT")))


def test_github_token(scan):
    assert "github-token" in rule_ids(scan(kv("x", "ghp_" + ("aB3" * 12))))
    assert "github-token" not in rule_ids(scan(kv("x", "ghp_" + "tooShort")))


def test_slack_token(scan):
    assert "slack-token" in rule_ids(scan(kv("x", "xoxb-" + "2401302150-aBcDeFgHiJkLmN")))
    # "xoxz-" is not a valid subtype (rule matches only xox[baprs]-).
    assert "slack-token" not in rule_ids(scan(kv("x", "xoxz-" + "2401302150-aBcDeFgHiJ")))


def test_anthropic_key(scan):
    assert "anthropic-key" in rule_ids(scan(kv("x", "sk-ant-" + "aB3cD4eF5gH6iJ7kL8mN")))
    assert "anthropic-key" not in rule_ids(scan(kv("x", "sk-ant-" + "short")))


def test_openai_project_key(scan):
    assert "openai-project-key" in rule_ids(scan(kv("x", "sk-proj-" + "aB3cD4eF5gH6iJ7kL8mN")))
    assert "openai-project-key" not in rule_ids(scan(kv("x", "sk-proj-" + "short")))


def test_openai_key(scan):
    assert "openai-key" in rule_ids(scan(kv("x", "sk-" + ("aB3cD4eF5g" * 5)[:48])))
    assert "openai-key" not in rule_ids(scan(kv("x", "sk-" + "tooShortKey")))


def test_google_api_key(scan):
    assert "google-api-key" in rule_ids(scan(kv("x", "AIza" + ("bC3dE4fG5h" * 4)[:35])))
    assert "google-api-key" not in rule_ids(scan(kv("x", "AIza" + "tooShort")))


def test_private_key_block(scan):
    header = "-----BEGIN RSA PRIVATE KEY" + "-----"  # split so source has no full match
    assert "private-key" in rule_ids(scan(header))
    assert "private-key" not in rule_ids(scan("-----BEGIN CERTIFICATE" + "-----"))


def test_jwt(scan):
    token = "eyJ" + "hbGciOiJIUzI1" + "." + "eyJ" + "zdWIiOiJhbGce" + "." + "SflKxwRJSMeKKF2Q"
    assert "jwt" in rule_ids(scan(kv("x", token)))
    two_part = "eyJ" + "hbGciOiJIUzI1" + "." + "eyJ" + "zdWIiOiJhbGce"  # only two segments
    assert "jwt" not in rule_ids(scan(kv("x", two_part)))


def test_connection_string(scan):
    dsn = "postgres://" + "dbuser" + ":" + "s3cretPW" + "@localhost:5432/app"
    assert "connection-string" in rule_ids(scan(kv("dsn", dsn)))
    # No user:password@ credentials -> a plain URL must not fire.
    assert "connection-string" not in rule_ids(scan(kv("url", "https://" + "example.com/app")))


def test_hardcoded_credential(scan):
    assert "hardcoded-credential" in rule_ids(scan(kv("access_token", "s3cretValue123")))
    # value under 8 chars is below the credential threshold
    assert "hardcoded-credential" not in rule_ids(scan(kv("token", "short12")))


# --- Vulnerability rules: one positive + one negative each --------------------


def test_subprocess_shell_true(scan):
    assert "subprocess-shell-true" in rule_ids(scan('subprocess.run(f"echo {x}", shell=True)'))
    # shell=True without interpolation, and interpolation without shell=True, are both clean.
    assert "subprocess-shell-true" not in rule_ids(scan('subprocess.run(["echo", x])'))
    assert "subprocess-shell-true" not in rule_ids(scan('subprocess.run("echo hi", shell=True)'))


def test_pickle_load(scan):
    assert "pickle-load" in rule_ids(scan("obj = pickle.loads(blob)"))
    assert "pickle-load" not in rule_ids(scan("obj = json.loads(blob)"))


def test_yaml_unsafe_load(scan):
    assert "yaml-unsafe-load" in rule_ids(scan("cfg = yaml.load(text)"))
    assert "yaml-unsafe-load" not in rule_ids(scan("cfg = yaml.load(text, Loader=yaml.SafeLoader)"))


def test_sql_string_build(scan):
    assert "sql-string-build" in rule_ids(scan('cur.execute(f"SELECT * FROM t WHERE id={i}")'))
    # parameterized execute (%s placeholder, params tuple) is the safe form
    assert "sql-string-build" not in rule_ids(
        scan('cur.execute("SELECT * FROM t WHERE id=%s", (i,))')
    )


def test_eval_exec(scan):
    assert "eval-exec" in rule_ids(scan("result = eval(user_input)"))
    assert "eval-exec" not in rule_ids(scan('result = eval("2 + 2")'))
    # a .eval(...) method call is not the builtin
    assert "eval-exec" not in rule_ids(scan("frame = df.eval(expression_var)"))


def test_inner_html(scan):
    assert "inner-html" in rule_ids(scan("el.innerHTML = userContent;"))
    assert "inner-html" not in rule_ids(scan("if (el.innerHTML == other) {}"))


def test_document_write(scan):
    assert "document-write" in rule_ids(scan("document.write(payload);"))
    assert "document-write" not in rule_ids(scan("logger.write(payload);"))


def test_dangerously_set_inner_html(scan):
    assert "dangerously-set-inner-html" in rule_ids(scan("<div dangerouslySetInnerHTML={h} />"))
    assert "dangerously-set-inner-html" not in rule_ids(scan("<div className={h} />"))


def test_child_process_exec(scan):
    assert "child-process-exec" in rule_ids(scan("exec(`rm -rf ${dir}`);"))
    assert "child-process-exec" not in rule_ids(scan('exec("ls -la");'))


# --- Suppression: pragma on the line and on the line above -------------------


def test_pragma_on_same_line_suppresses(scan):
    line = kv("x", "AKIA" + "IOSFODNN7REALKEY") + "  # security-scan: allow"
    assert scan(line) == []


def test_pragma_on_line_above_suppresses(scan):
    text = "# security-scan: allow\n" + kv("x", "AKIA" + "IOSFODNN7REALKEY")
    assert scan(text) == []


def test_pragma_two_lines_above_does_not_suppress(scan):
    # Pragma only reaches the flagged line or the one immediately above it.
    text = "# security-scan: allow\n" + "y = 1\n" + kv("x", "AKIA" + "IOSFODNN7REALKEY")
    assert "aws-access-key" in rule_ids(scan(text))


# --- Suppression: placeholder heuristics (each class) -------------------------

PLACEHOLDER_WORDS = [
    "example",
    "sample",
    "placeholder",
    "changeme",
    "your",
    "dummy",
    "fake",
    "xxx",
    "redacted",
]


@pytest.mark.parametrize("word", PLACEHOLDER_WORDS)
def test_placeholder_word_class_is_skipped(scan, word):
    # A credential-shaped value containing a placeholder word must never fire.
    value = "Pad" + word + "Val99"  # >= 8 chars, otherwise a real match
    assert scan(kv("api_key", value)) == []


def test_placeholder_angle_bracket_template_is_skipped(scan):
    assert scan(kv("api_key", "<my-real-secret-key>")) == []


def test_placeholder_all_same_character_is_skipped(scan):
    # An all-one-character value is a filler, not a secret.
    assert scan(kv("password", "z" * 16)) == []


def test_non_placeholder_credential_still_fires(scan):
    # Guards against the heuristics being so broad they swallow real secrets.
    assert "hardcoded-credential" in rule_ids(scan(kv("password", "Gh7pQ2wKz9")))


# --- Guards -------------------------------------------------------------------


def test_binary_file_is_skipped(tmp_path):
    target = tmp_path / "blob.bin"
    secret = (kv("x", "AKIA" + "IOSFODNN7REALKEY")).encode()
    target.write_bytes(secret + b"\x00\x01\x02binarydata")
    assert sec.scan_file(target, tmp_path) == []


def test_vendored_dir_is_skipped(tmp_path):
    for vendored in ("node_modules", ".venv", "dist"):
        target = tmp_path / vendored / "pkg" / "code.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(kv("x", "AKIA" + "IOSFODNN7REALKEY"))
        assert sec.scan_file(target, tmp_path) == []


def test_missing_file_is_skipped_with_note(tmp_path, capsys):
    assert sec.scan_file(tmp_path / "gone.py", tmp_path) == []
    assert "no longer exists" in capsys.readouterr().err


def test_oversized_file_scans_only_first_mib(tmp_path, capsys):
    target = tmp_path / "big.py"
    top_secret = kv("x", "AKIA" + "IOSFODNN7REALKEY")
    deep_secret = kv("y", "AKIA" + "IOSFODNN7OTHERKEY"[:16])
    padding = "# pad line\n" * 120000  # comfortably over 1 MiB of filler
    target.write_text(top_secret + "\n" + padding + deep_secret + "\n")
    assert target.stat().st_size > sec.MAX_SCAN_BYTES
    findings = sec.scan_file(target, tmp_path)
    # The line-1 secret is found; the one past 1 MiB is truncated away.
    assert [f.line for f in findings] == [1]
    assert "first 1 MiB only" in capsys.readouterr().err


def test_decode_errors_do_not_raise(tmp_path):
    # Invalid UTF-8 without a null byte must scan (errors="replace"), never raise.
    target = tmp_path / "weird.py"
    target.write_bytes(b"x = 1\n" + b"\xff\xfe not utf-8 \xc3\x28\n")
    assert sec.scan_file(target, tmp_path) == []


# --- Diagnostics + finding formatting ----------------------------------------


def test_finding_line_format(scan):
    findings = scan(kv("x", "AKIA" + "IOSFODNN7REALKEY"), name="cfg.py")
    line = sec.finding_line(findings[0])
    assert line.endswith("aws-access-key AWS access key ID")
    assert ":1 " in line


def test_format_diagnostics_caps_with_tail():
    lines = [f"f.py:{i} r msg" for i in range(1, 15)]
    out = sec.format_diagnostics(lines).splitlines()
    assert len(out) == 11 and out[10] == "... and 4 more"


# --- Session-state helpers ----------------------------------------------------


def test_state_roundtrip(tmp_path):
    state = {"baseline": ["b.py", "a.py"], "tracked": ["t.py"], "last_head": "abc123"}
    sec.save_state(tmp_path, "sess-1", state)
    loaded = sec.load_state(tmp_path, "sess-1")
    assert loaded["baseline"] == ["a.py", "b.py"]  # sorted + deduped on write
    assert loaded["tracked"] == ["t.py"]
    assert loaded["last_head"] == "abc123"


def test_state_dedup_on_write(tmp_path):
    state = {"baseline": ["a", "a", "b"], "tracked": ["x", "x", "x"], "last_head": ""}
    sec.save_state(tmp_path, "sess-2", state)
    loaded = sec.load_state(tmp_path, "sess-2")
    assert loaded["baseline"] == ["a", "b"]
    assert loaded["tracked"] == ["x"]


def test_load_missing_state_is_empty(tmp_path):
    assert sec.load_state(tmp_path, "never-written") == {
        "baseline": [],
        "tracked": [],
        "last_head": "",
    }


def test_load_corrupt_state_is_empty(tmp_path):
    path = sec.state_path(tmp_path, "sess-3")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{ this is not valid json")
    assert sec.load_state(tmp_path, "sess-3") == {"baseline": [], "tracked": [], "last_head": ""}


def test_session_id_is_sanitized_to_one_safe_segment(tmp_path):
    path = sec.state_path(tmp_path, "../../etc/passwd")
    assert path.parent == tmp_path / ".claude" / ".security-scan"
    assert "/" not in path.name and ".." not in path.name


def test_prune_removes_stale_keeps_fresh(tmp_path):
    empty = {"baseline": [], "tracked": [], "last_head": ""}
    sec.save_state(tmp_path, "fresh", empty)
    sec.save_state(tmp_path, "stale", empty)
    fresh_path = sec.state_path(tmp_path, "fresh")
    stale_path = sec.state_path(tmp_path, "stale")
    eight_days_ago = time.time() - 8 * 24 * 60 * 60
    os.utime(stale_path, (eight_days_ago, eight_days_ago))
    sec.prune_stale_states(tmp_path)
    assert fresh_path.exists()
    assert not stale_path.exists()
