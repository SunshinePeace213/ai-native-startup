"""Contract tests for the command-eval runner.

The runner is what makes the studio commands' eval suite executable rather than prose,
so what has to hold is that it stages a project the commands can actually run in, grades
a mechanical assertion by running it, and reports the three exit codes the pipeline reads.
The token-spending path never runs here: `claude_headless` is stubbed, so every run below
is free. Fixtures live under tmp_path so the suite stays parallel-safe.
"""

import importlib.util
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / ".claude" / "scripts" / "studio-layer" / "run_command_evals.py"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands" / "studio-layer"

spec = importlib.util.spec_from_file_location("run_command_evals", SCRIPT)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

CASE = {
    "id": 0,
    "name": "writes-the-note",
    "prompt": "/studio-layer:p1-discovery acme/site",
    "assertions": [
        {"id": "a1", "text": "the note exists", "check": "test -f produced.md"},
        {"id": "a2", "text": "the note reads as a written statement"},
    ],
}


def write_suite(commands_dir: Path, cases: list[dict], skill_name: str = "studio-layer-commands"):
    path = commands_dir / "evals" / "evals.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"skill_name": skill_name, "evals": cases}), encoding="utf-8")
    return path


def fake_namespace(tmp_path: Path) -> Path:
    """A minimal project carrying everything the runner stages, and nothing else."""
    claude = tmp_path / ".claude"
    for kind in runner.STAGED_NAMESPACE_DIRS:
        target = claude / kind / "studio-layer"
        target.mkdir(parents=True)
        (target / "marker.md").write_text(kind, encoding="utf-8")
    (claude / "hooks").mkdir(parents=True)
    (claude / "hooks" / "check_gate_signoff.py").write_text("# gate", encoding="utf-8")
    return claude / "commands" / "studio-layer"


def stub_claude(produce: str | None = "produced.md", verdict: bool = True):
    """Stand in for `claude -p`: writes one file, then answers as the judge."""

    def _stub(prompt, cwd, timeout, model, permission_mode):
        if "Grade each assertion" in prompt:
            return {
                "result": json.dumps(
                    {"verdicts": [{"id": "a2", "passed": verdict, "evidence": "stubbed"}]}
                )
            }
        if produce:
            (Path(cwd) / produce).write_text("a written statement", encoding="utf-8")
        return {"result": "done"}

    return _stub


# --- staging -------------------------------------------------------------------------


def test_staging_carries_the_whole_studio_namespace(tmp_path):
    """A command that resolves without its roles, rules, and check scripts is not the
    command under test -- the eval would measure a bare model instead."""
    root = tmp_path / "scratch"
    root.mkdir()
    runner.stage_project(COMMANDS_DIR, root)

    for kind in ("commands", "agents", "skills", "rules", "scripts"):
        staged = root / ".claude" / kind / "studio-layer"
        assert staged.is_dir(), f"{kind}/studio-layer was not staged"
        assert any(staged.rglob("*")), f"{kind}/studio-layer staged empty"
    assert (root / ".claude" / "commands" / "studio-layer" / "p2-definition.md").is_file()


def test_staging_carries_the_sign_off_hook_from_outside_the_namespace(tmp_path):
    """The hook is not part of the studio namespace, so nothing else would bring it --
    and without it the hard-gate commands would be evaluated with their gate absent."""
    root = tmp_path / "scratch"
    root.mkdir()
    runner.stage_project(COMMANDS_DIR, root)

    assert (root / ".claude" / "hooks" / "check_gate_signoff.py").is_file()


def test_p2_registered_hook_path_resolves_inside_the_scratch_project(tmp_path):
    """P2 registers its gate at "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py.
    Resolving that literal registration against the scratch root is what proves the staged
    project satisfies it -- a staged copy at some other path would gate nothing."""
    root = tmp_path / "scratch"
    root.mkdir()
    runner.stage_project(COMMANDS_DIR, root)

    frontmatter = (COMMANDS_DIR / "p2-definition.md").read_text(encoding="utf-8").split("---")[1]
    registration = re.search(r"command:\s*(.+)", frontmatter).group(1).strip()
    declared = registration.split("--script", 1)[1].split()[0].replace('"', "")
    resolved = Path(declared.replace("$CLAUDE_PROJECT_DIR", str(root)))

    assert resolved.is_file(), f"P2's registered hook {declared} does not exist in {root}"
    assert resolved.is_relative_to(root), "the gate resolved outside the throwaway project"


def test_staging_refuses_a_namespace_missing_a_directory(tmp_path):
    """Staging four of the five directories would run the command with part of its
    machinery silently absent, which is exactly the failure the full stage prevents."""
    commands_dir = fake_namespace(tmp_path)
    (tmp_path / ".claude" / "agents" / "studio-layer" / "marker.md").unlink()
    (tmp_path / ".claude" / "agents" / "studio-layer").rmdir()

    with pytest.raises(runner.SuiteError, match="agents"):
        runner.stage_project(commands_dir, tmp_path / "scratch")


def test_staging_refuses_a_namespace_missing_the_hook(tmp_path):
    """Same reason, for the one staged file that lives outside the namespace."""
    commands_dir = fake_namespace(tmp_path)
    (tmp_path / ".claude" / "hooks" / "check_gate_signoff.py").unlink()

    with pytest.raises(runner.SuiteError, match="check_gate_signoff"):
        runner.stage_project(commands_dir, tmp_path / "scratch")


def test_collect_outputs_keeps_what_the_run_wrote_and_drops_the_staged_namespace(tmp_path):
    """The judge grades the produced files. Handing it the staged commands and rules too
    would let it grade the harness we shipped rather than the run's own output."""
    root = tmp_path / "scratch"
    root.mkdir()
    runner.stage_project(COMMANDS_DIR, root)
    (root / "clients" / "acme" / "site" / "discovery").mkdir(parents=True)
    (root / "clients" / "acme" / "site" / "discovery" / "notes.md").write_text("x", "utf-8")

    produced = runner.collect_outputs(root, tmp_path / "outputs")

    assert produced == [Path("clients/acme/site/discovery/notes.md")]


# --- grading -------------------------------------------------------------------------


def test_check_carrying_assertions_are_graded_by_running_them(tmp_path):
    """A `check` is the reproducible half of the suite: its verdict must come from the
    command's exit status against the real outputs, never from a judge reading prose."""
    (tmp_path / "produced.md").write_text("here", encoding="utf-8")
    assertions = [
        {"id": "a1", "text": "the file exists", "check": "test -f produced.md"},
        {"id": "a2", "text": "the other file exists", "check": "test -f absent.md"},
    ]

    graded = runner.run_checks(assertions, tmp_path)

    assert graded["a1"]["passed"] is True
    assert graded["a2"]["passed"] is False
    assert "exited 1" in graded["a2"]["evidence"]


def test_assertions_without_a_check_are_left_for_the_judge(tmp_path):
    """run_checks must not silently pass an ungraded assertion -- an assertion nobody
    grades would inflate the pass rate the whole runner exists to report."""
    graded = runner.run_checks([{"id": "a2", "text": "reads well"}], tmp_path)

    assert graded == {}


# --- exit codes ----------------------------------------------------------------------


def test_lint_exits_zero_on_the_committed_suite():
    """--lint is the free, CI-safe half of AC16; it must clear on the shipped suite."""
    assert runner.main([str(COMMANDS_DIR), "--lint"]) == 0


def test_every_case_clearing_its_rate_exits_zero(tmp_path, monkeypatch):
    """Exit 0 is the runner's claim that the commands behaved on every graded run."""
    commands_dir = fake_namespace(tmp_path)
    write_suite(commands_dir, [CASE])
    monkeypatch.setattr(runner, "claude_headless", stub_claude())

    code = runner.main([str(commands_dir), "-k", "2", "--yes", "--workspace", str(tmp_path / "ws")])

    assert code == 0
    grading = json.loads((tmp_path / "ws" / "eval-0" / "run-1" / "grading.json").read_text())
    assert grading["summary"]["pass_rate"] == 1.0


def test_a_case_short_of_its_rate_exits_one(tmp_path, monkeypatch):
    """Exit 1 is a graded failure -- the command ran and its output missed the bar. It has
    to stay distinct from exit 2 so a broken suite is never read as a failing command."""
    commands_dir = fake_namespace(tmp_path)
    write_suite(commands_dir, [CASE])
    monkeypatch.setattr(runner, "claude_headless", stub_claude(produce=None))

    code = runner.main([str(commands_dir), "-k", "2", "--yes", "--workspace", str(tmp_path / "ws")])

    assert code == 1
    grading = json.loads((tmp_path / "ws" / "eval-0" / "run-1" / "grading.json").read_text())
    assert grading["expectations"][0]["passed"] is False


def test_a_recorded_pass_rate_below_one_tolerates_a_failed_assertion(tmp_path, monkeypatch):
    """A case records the rate it must clear, so prose that is right most of the time can
    pass while the default stays every assertion on every run."""
    commands_dir = fake_namespace(tmp_path)
    write_suite(commands_dir, [{**CASE, "pass_rate": 0.5}])
    monkeypatch.setattr(runner, "claude_headless", stub_claude(produce=None))

    code = runner.main([str(commands_dir), "-k", "2", "--yes", "--workspace", str(tmp_path / "ws")])

    assert code == 0


def test_a_missing_suite_exits_two(tmp_path):
    """Exit 2 says the runner could not grade at all. Reporting a missing suite as 1
    would read as commands that misbehaved."""
    commands_dir = fake_namespace(tmp_path)

    assert runner.main([str(commands_dir), "--lint"]) == 2


def test_unparseable_json_exits_two(tmp_path):
    """Same distinction, for a suite that exists but cannot be read."""
    commands_dir = fake_namespace(tmp_path)
    path = commands_dir / "evals" / "evals.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")

    assert runner.main([str(commands_dir), "--lint"]) == 2


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ({"prompt": "write some discovery notes"}, "slash command"),
        ({"assertions": []}, "no assertions"),
        ({"pass_rate": 1.5}, "pass_rate"),
        ({"name": ""}, "missing 'name'"),
    ],
)
def test_lint_rejects_a_case_that_could_not_produce_a_rate(tmp_path, mutation, expected):
    """Each of these makes the suite unrunnable or its rate meaningless, and --lint is the
    only place they are caught before a run spends tokens discovering it."""
    commands_dir = fake_namespace(tmp_path)
    write_suite(commands_dir, [{**CASE, **mutation}])

    problems = runner.validate(
        json.loads((commands_dir / "evals" / "evals.json").read_text()),
        commands_dir / "evals" / "evals.json",
    )

    assert any(expected in problem for problem in problems), problems
    assert runner.main([str(commands_dir), "--lint"]) == 2


def test_a_dry_run_spends_nothing(tmp_path, monkeypatch):
    """Without --yes the runner must not invoke claude: the plan's own guardrail is that
    evals are manual and deliberate, so the default has to be free."""
    commands_dir = fake_namespace(tmp_path)
    write_suite(commands_dir, [CASE])

    def explode(*args, **kwargs):
        raise AssertionError("a dry run must not call claude")

    monkeypatch.setattr(runner, "claude_headless", explode)

    assert runner.main([str(commands_dir), "-k", "2"]) == 0
