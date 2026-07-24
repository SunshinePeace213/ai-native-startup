"""Contract tests for the spec-completeness Stop gate (check_spec_completeness.py).

The gate is command-scoped (registered by /harness-layer:harness-plan, NOT in
settings.json), so it must never fire outside a planning run -- a root with no
specs/ dir passes silently. It is ALSO session-scoped: it resolves the invoking
session's root from the Stop payload's `cwd` and gates only the NEWEST plan
folder under THAT root's specs/ -- never another worktree's. A concurrent
planning session in a different root can neither steal nor mask the target
(regression-tested both directions below); scanning across every worktree's
specs/ was the soriza wrong-target defect class this rework removes. _templates
and discovery-only chain folders are excluded. Exit 2 must name exactly what is
missing -- file or '## section' -- because stderr is the agent's only repair
instruction. Complete plans are built from the hook's own REQUIRED_SECTIONS via
load_hook_module, so a rule change cannot silently diverge from the tests.
Malformed/empty stdin and a cwd outside any git repo fail open (exit 0), never
crash.
"""

import json
import os
from pathlib import Path

import pytest


def payload(cwd: Path) -> str:
    """A Stop payload carrying the session's cwd -- the field the gate reads to
    resolve its root."""
    return json.dumps({"stop_hook_active": False, "cwd": str(cwd)})


@pytest.fixture
def sections(load_hook_module):
    return load_hook_module("check_spec_completeness.py").REQUIRED_SECTIONS


def write_plan(specs: Path, name: str, sections: dict) -> Path:
    """A plan folder whose four files carry every required section."""
    folder = specs / name
    folder.mkdir(parents=True)
    for fname, secs in sections.items():
        body = "\n\n".join(f"## {sec}\n\ncontent" for sec in secs)
        (folder / fname).write_text(f"# {name}\n\n{body}\n")
    return folder


def set_mtime(folder: Path, epoch: float) -> None:
    os.utime(folder, (epoch, epoch))


def gate(run_hook, root: Path):
    """Run the hook as a session rooted at `root`: `root` is a real directory
    outside any git repo (pytest tmp), so the gate's git-toplevel step fails and
    it falls to the stdin cwd itself -- making `root` the gated root."""
    return run_hook("check_spec_completeness.py", payload(root))


def test_no_specs_dir_allows_stop(tmp_path, run_hook):
    """Command-scoped or not, a session whose root has no specs/ has nothing to
    gate -- the hook must be invisible there."""
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_underscore_and_discovery_only_folders_block_as_no_plan(tmp_path, run_hook):
    """_templates is scaffolding and a folder holding only discovery/ pages is
    a pre-plan chain still in progress — neither is a plan: a planning run that
    produced no spec files must not be allowed to end, and discovery pages must
    never be gated as a spec."""
    (tmp_path / "specs" / "_templates").mkdir(parents=True)
    discovery = tmp_path / "specs" / "some-chain" / "discovery"
    discovery.mkdir(parents=True)
    (discovery / "page.html").write_text("<p>mock</p>")
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "no plan folder found" in proc.stderr


def test_newer_discovery_only_folder_does_not_mask_the_plan(tmp_path, run_hook, sections):
    """A parallel chain's discovery-only folder can be newer than the plan
    being drafted; picking it as "newest" would gate HTML pages as a spec and
    block every planning run — the newest folder with spec files must win."""
    specs = tmp_path / "specs"
    plan = write_plan(specs, "the-plan", sections)
    discovery = specs / "newer-chain" / "discovery"
    discovery.mkdir(parents=True)
    (discovery / "page.html").write_text("<p>mock</p>")
    set_mtime(plan, 1_000_000_000)
    set_mtime(specs / "newer-chain", 2_000_000_000)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0


def test_plan_folder_with_discovery_pages_is_gated_normally(tmp_path, run_hook, sections):
    """After the chain, discovery/ lives INSIDE the plan folder; its presence
    must not exempt a folder that already has spec files from the completeness
    gate, or an incomplete post-chain plan would slip through."""
    folder = write_plan(tmp_path / "specs", "my-plan", sections)
    (folder / "discovery").mkdir()
    (folder / "discovery" / "interview.html").write_text("<p>page</p>")
    (folder / "tasks.md").unlink()
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "MISSING FILE: tasks.md" in proc.stderr


def test_complete_plan_allows_stop(tmp_path, run_hook, sections):
    """All four files present with every required section: the gate opens."""
    write_plan(tmp_path / "specs", "my-plan", sections)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_missing_file_blocks_naming_it(tmp_path, run_hook, sections):
    """A absent spec file is named outright so the agent knows what to write."""
    folder = write_plan(tmp_path / "specs", "my-plan", sections)
    (folder / "tasks.md").unlink()
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "MISSING FILE: tasks.md" in proc.stderr
    assert "compare against specs/_templates/" in proc.stderr


def test_missing_section_blocks_naming_file_and_heading(tmp_path, run_hook, sections):
    """A gutted section is named as file + '## heading' -- the exact repair."""
    folder = write_plan(tmp_path / "specs", "my-plan", sections)
    spec = folder / "spec.md"
    spec.write_text(spec.read_text().replace("## Red Flags", "## Renamed"))
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "spec.md: missing section '## Red Flags'" in proc.stderr
    # exit-2 blocking must not be mixed with structured stdout (hooks-guide contract)
    assert proc.stdout == ""


def test_newest_plan_folder_is_the_gated_one(tmp_path, run_hook, sections):
    """Only the plan being drafted NOW is gated: an old complete plan must not
    mask a fresh incomplete one, and vice versa the old one is never re-gated."""
    specs = tmp_path / "specs"
    old = write_plan(specs, "old-complete", sections)
    fresh = write_plan(specs, "fresh-incomplete", sections)
    (fresh / "decisions.md").unlink()
    set_mtime(old, 1_000_000_000)
    set_mtime(fresh, 2_000_000_000)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "fresh-incomplete" in proc.stderr


# --- Session-scoping / concurrency regression tests -------------------------
# Two roots stand in for two concurrent planning sessions in different
# worktrees. Only the session root is passed as the payload cwd; the foreign
# root must never influence the verdict. These replace the former
# `test_worktree_specs_are_discovered` /
# `test_no_main_specs_dir_skips_even_with_worktree_specs`, which pinned the now
# deleted cross-worktree scan.


def two_roots(tmp_path: Path) -> tuple[Path, Path]:
    """A session root and a foreign root, each a self-contained tree outside any
    git repo so each resolves to itself via the stdin-cwd fallback."""
    session = tmp_path / "session"
    foreign = tmp_path / "foreign"
    session.mkdir()
    foreign.mkdir()
    return session, foreign


def test_foreign_root_complete_plan_never_opens_the_session_gate(tmp_path, run_hook, sections):
    """(a) Session root's plan is incomplete while a foreign root carries a
    complete, NEWER plan. A cross-root scan would pick the foreign complete plan
    and wrongly open the gate; session-scoped, the session's own incomplete plan
    is gated -- exit 2 naming the session's folder, foreign never mentioned."""
    session, foreign = two_roots(tmp_path)
    sess_plan = write_plan(session / "specs", "session-plan", sections)
    (sess_plan / "acceptance-criteria.md").unlink()
    foreign_plan = write_plan(foreign / "specs", "foreign-plan", sections)
    set_mtime(sess_plan, 1_000_000_000)
    set_mtime(foreign_plan, 2_000_000_000)  # newer -- would win a cross-root scan
    proc = gate(run_hook, session)
    assert proc.returncode == 2
    assert "session-plan" in proc.stderr
    assert "MISSING FILE: acceptance-criteria.md" in proc.stderr
    assert "foreign-plan" not in proc.stderr


def test_foreign_root_incomplete_plan_never_blocks_the_session(tmp_path, run_hook, sections):
    """(b) The opposite direction: the session's plan is complete while a
    foreign root carries an incomplete, NEWER plan. A cross-root scan would pick
    the foreign incomplete plan and wrongly block; session-scoped, the session's
    complete plan opens the gate -- exit 0."""
    session, foreign = two_roots(tmp_path)
    sess_plan = write_plan(session / "specs", "session-plan", sections)
    foreign_plan = write_plan(foreign / "specs", "foreign-plan", sections)
    (foreign_plan / "spec.md").unlink()
    set_mtime(sess_plan, 1_000_000_000)
    set_mtime(foreign_plan, 2_000_000_000)  # newer -- would win a cross-root scan
    proc = gate(run_hook, session)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_mtime_decoy_in_foreign_root_never_changes_the_selection(tmp_path, run_hook, sections):
    """(c) The session root itself holds an older complete plan and a newer
    incomplete plan; a foreign root holds a decoy that is newer than BOTH and
    complete. The selection must stay the session's own newest folder
    (within-root mtime still wins) and never jump to the foreign decoy -- exit 2
    naming the session's incomplete plan, proving the foreign mtime was ignored."""
    session, foreign = two_roots(tmp_path)
    old = write_plan(session / "specs", "session-old-complete", sections)
    target = write_plan(session / "specs", "session-new-incomplete", sections)
    (target / "decisions.md").unlink()
    decoy = write_plan(foreign / "specs", "foreign-decoy-complete", sections)
    set_mtime(old, 1_000_000_000)
    set_mtime(target, 2_000_000_000)
    set_mtime(decoy, 3_000_000_000)  # newest of all -- must be invisible
    proc = gate(run_hook, session)
    assert proc.returncode == 2
    assert "session-new-incomplete" in proc.stderr
    assert "foreign-decoy-complete" not in proc.stderr
    assert "session-old-complete" not in proc.stderr


def test_no_session_specs_dir_skips_even_with_foreign_specs(tmp_path, run_hook, sections):
    """The session root's own specs/ is the gate's on-switch: without it the
    hook exits 0 even though a foreign root carries a (newer, incomplete) plan --
    replaces the old worktree-scoped on-switch test; the scope is now per-root."""
    session, foreign = two_roots(tmp_path)
    foreign_plan = write_plan(foreign / "specs", "foreign-plan", sections)
    (foreign_plan / "spec.md").unlink()
    proc = gate(run_hook, session)  # session has no specs/ at all
    assert proc.returncode == 0
    assert proc.stderr == ""


# --- Fail-open on plumbing --------------------------------------------------


def test_malformed_stdin_fails_open(tmp_path, run_hook):
    """(d) Garbage on stdin is plumbing noise, not an agent-fixable finding: the
    gate degrades down the fallback chain (here to a specs-less process cwd) and
    exits 0 without a traceback -- never crash, never exit 2 on plumbing."""
    proc = run_hook("check_spec_completeness.py", "not json {{{", cwd=tmp_path)
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr


def test_empty_stdin_fails_open(tmp_path, run_hook):
    """Empty stdin (no payload) is the same plumbing case as malformed input:
    fall back without crashing, exit 0."""
    proc = run_hook("check_spec_completeness.py", "", cwd=tmp_path)
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr


def test_cwd_outside_git_repo_uses_cwd_and_exits_when_no_specs(tmp_path, run_hook):
    """A stdin cwd that exists but is outside any git repo: git rev-parse fails,
    so the cwd path itself serves as the root; with no specs/ there the gate
    exits 0 -- the documented outside-git edge, resolved without crashing."""
    outside = tmp_path / "outside"
    outside.mkdir()
    proc = gate(run_hook, outside)
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert "Traceback" not in proc.stderr


# --- Validation-command lint ------------------------------------------------
# The lint runs only AFTER the required-sections check passes (a missing
# ## Validation Commands section is already blocked there). It parses the
# section's command bullets -- skipping the stage-tag legend definitions and
# intro prose -- and enforces the block/warn split from spec.md: structure
# (stage tag, committed-check invocation, plan-time path present) blocks;
# later-stage paths not yet created and absolute-promise wording warn only.

# Header + the three stage-tag legend bullets + intro prose, mirroring the real
# acceptance-criteria.md. The legend bullets and prose MUST be ignored by the
# lint; only the command bullets appended after are linted.
VALIDATION_HEADER = (
    "## Validation Commands\n\n"
    "Validation logic lives in committed check scripts -- this prose is not a bullet.\n\n"
    "- `[plan-time]` — runnable against the spec folder alone, before any build.\n"
    "- `[child-build-time]` — runnable once the build produced its changes.\n"
    "- `[post-merge]` — runnable only after dependent work merged.\n\n"
)


def write_ac_validation(folder: Path, bullets: list[str]) -> None:
    """Overwrite acceptance-criteria.md keeping the two required sections, with a
    Validation Commands section carrying the legend, prose, and `bullets`."""
    text = (
        "# plan\n\n## Acceptance Criteria\n\n- **AC1** — an observable outcome\n\n"
        + VALIDATION_HEADER
        + "\n".join(bullets)
        + "\n"
    )
    (folder / "acceptance-criteria.md").write_text(text)


def create_check(root: Path, relpath: str) -> None:
    """A committed check file at a root-relative path (as a bullet would name)."""
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# check\n")


def test_lint_plan_time_present_script_passes(tmp_path, run_hook, sections):
    """A plan-time bullet invoking a committed check that EXISTS today is the
    compliant case: structure holds, the gate opens with no diagnostics."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    create_check(tmp_path, "specs/p/checks/ac1.py")
    write_ac_validation(
        folder, ["- `[plan-time]` `uv run --script specs/p/checks/ac1.py` — verifies AC1."]
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_lint_plan_time_missing_script_blocks(tmp_path, run_hook, sections):
    """A [plan-time] check must be runnable against the spec folder alone; if its
    script is absent the criterion cannot be verified now, so the gate blocks and
    names the missing path -- the soriza 'validation names a check that isn't
    committed' defect this lint exists to catch."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    write_ac_validation(
        folder, ["- `[plan-time]` `uv run --script specs/p/checks/ac1.py` — verifies AC1."]
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "[plan-time] check path does not exist" in proc.stderr
    assert "specs/p/checks/ac1.py" in proc.stderr


def test_lint_absolute_target_blocks(tmp_path, run_hook, sections):
    """An absolute check path discards the gated root, so `(root / path)` would
    resolve to a file anywhere on disk and could smuggle a check that lives
    outside the plan past the gate; a committed check must be repo-relative, so
    an absolute target is a form violation -> block, never a silent pass."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    create_check(tmp_path, "specs/p/checks/ac1.py")
    write_ac_validation(folder, ["- `[plan-time]` `uv run --script /tmp/ac1.py` — verifies AC1."])
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "check path must be repo-relative" in proc.stderr
    assert "/tmp/ac1.py" in proc.stderr


def test_lint_parent_traversal_target_blocks(tmp_path, run_hook, sections):
    """A `..` segment lets a target escape the gated root (e.g. a sibling
    worktree's checks/), defeating the point of validating the plan's OWN
    committed checks; traversal is a form violation -> block, even though the
    resolved file may well exist."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    create_check(tmp_path, "specs/p/checks/ac1.py")
    write_ac_validation(
        folder,
        ["- `[plan-time]` `uv run --script specs/p/checks/../../q/checks/ac1.py` — verifies AC1."],
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "check path must be repo-relative" in proc.stderr


def test_lint_directory_as_script_target_blocks(tmp_path, run_hook, sections):
    """`uv run --script` runs a single file; a directory at the target path is
    not a runnable check, and plain `.exists()` would wrongly bless it. A
    plan-time script must be a regular file present now, so a directory target
    fails the existence rule -> block."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    (tmp_path / "specs" / "p" / "checks" / "ac1.py").mkdir(parents=True)  # a dir, not a file
    write_ac_validation(
        folder, ["- `[plan-time]` `uv run --script specs/p/checks/ac1.py` — verifies AC1."]
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "[plan-time] check path does not exist" in proc.stderr
    assert "specs/p/checks/ac1.py" in proc.stderr


def test_lint_other_plan_script_target_blocks(tmp_path, run_hook, sections):
    """A script target under a DIFFERENT plan's checks/ (here specs/other/) is
    not this plan's committed check even when the file exists; each plan must
    validate its own checks, so a foreign-plan script is a form violation ->
    block naming the required specs/<this-plan>/checks/ location."""
    create_check(tmp_path, "specs/other/checks/ac1.py")  # exists, but wrong plan
    folder = write_plan(tmp_path / "specs", "p", sections)  # newest -> the gated plan
    write_ac_validation(
        folder, ["- `[plan-time]` `uv run --script specs/other/checks/ac1.py` — verifies AC1."]
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "script check must live under specs/p/checks/" in proc.stderr
    assert "specs/other/checks/ac1.py" in proc.stderr


def test_lint_bullet_without_stage_tag_blocks(tmp_path, run_hook, sections):
    """Every command bullet must carry a stage tag so reviewers know the earliest
    point it can pass; an untagged bullet is unrunnable-by-schedule and blocks,
    the bullet text echoed so the agent can fix the exact line."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    write_ac_validation(folder, ["- `uv run pytest tests/harness-layer` — verifies AC1."])
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "no stage tag" in proc.stderr
    assert "uv run pytest tests/harness-layer" in proc.stderr


def test_lint_inline_program_blocks(tmp_path, run_hook, sections):
    """A bullet inlining a program instead of a committed check (`uv run --script`
    or `uv run pytest`) has no reproducible, reviewable artifact -- the core lint
    case: block and name the offending bullet."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    write_ac_validation(folder, ['- `[plan-time]` `python -c "print(1)"` — verifies AC1.'])
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "invokes neither" in proc.stderr
    assert 'python -c "print(1)"' in proc.stderr


def test_lint_pytest_invocation_to_existing_path_passes(tmp_path, run_hook, sections):
    """`uv run pytest <existing path>` is an accepted committed-check form just
    like `uv run --script`; pointed at a path that exists, it opens the gate
    cleanly (pins that pytest bullets are not mistaken for inline programs)."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    (tmp_path / "tests" / "foo").mkdir(parents=True)
    write_ac_validation(
        folder, ["- `[child-build-time]` `uv run pytest tests/foo` — verifies AC1."]
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_lint_later_stage_missing_path_warns_without_blocking(tmp_path, run_hook, sections):
    """A [child-build-time]/[post-merge] path may not exist yet -- the build
    creates it -- so its absence is a WARN, never a block: exit code stays 0 so a
    correctly-scheduled plan is not held hostage to not-yet-built artifacts."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    write_ac_validation(
        folder, ["- `[child-build-time]` `uv run pytest tests/not-built-yet` — verifies AC1."]
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert "WARN:" in proc.stderr
    assert "not present yet" in proc.stderr
    assert "tests/not-built-yet" in proc.stderr


def test_lint_absolute_promise_wording_warns_only(tmp_path, run_hook, sections):
    """Absolute-promise wording in spec.md is a quality smell, not a structural
    defect -- the ledger locks it warn-only: a WARN cites spec.md:line but the
    exit code is unchanged (0 here, since the commands are compliant)."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    create_check(tmp_path, "specs/p/checks/ac1.py")
    write_ac_validation(
        folder, ["- `[plan-time]` `uv run --script specs/p/checks/ac1.py` — verifies AC1."]
    )
    spec = folder / "spec.md"
    spec.write_text(spec.read_text() + "\nThis must never fail and always pass.\n")
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert "WARN:" in proc.stderr
    assert "absolute-promise wording" in proc.stderr
    assert "spec.md:" in proc.stderr


def test_lint_warnings_capped_at_ten(tmp_path, run_hook, sections):
    """A wordy spec must not flood stderr and drown the signal: warnings across
    all warn rules are capped at 10 even when far more lines match."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    create_check(tmp_path, "specs/p/checks/ac1.py")
    write_ac_validation(
        folder, ["- `[plan-time]` `uv run --script specs/p/checks/ac1.py` — verifies AC1."]
    )
    spec = folder / "spec.md"
    flood = "".join(f"\nLine {i}: this is never acceptable.\n" for i in range(15))
    spec.write_text(spec.read_text() + flood)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr.count("WARN:") == 10


def test_lint_legend_and_prose_never_flagged_as_commands(tmp_path, run_hook, sections):
    """The stage-tag legend bullets and the intro prose paragraph are not command
    bullets; the lint must skip them, or every compliant plan (which carries the
    legend verbatim) would be blocked for 'no committed check'."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    create_check(tmp_path, "specs/p/checks/ac1.py")
    write_ac_validation(
        folder, ["- `[plan-time]` `uv run --script specs/p/checks/ac1.py` — verifies AC1."]
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert "no stage tag" not in proc.stderr
    assert "invokes neither" not in proc.stderr


def test_lint_compliant_folder_passes_end_to_end(tmp_path, run_hook, sections):
    """A folder shaped like specs/harness-self-improvement's own
    acceptance-criteria.md -- a present plan-time script plus later-stage pytest
    and script checks that exist -- passes the whole gate with no diagnostics:
    proof the lint does not fire on the format it is meant to bless."""
    folder = write_plan(tmp_path / "specs", "p", sections)
    create_check(tmp_path, "specs/p/checks/ac5_inventory.py")
    create_check(tmp_path, "specs/p/checks/ac4_ci_workflow.py")
    (tmp_path / "tests" / "harness-layer" / "hooks" / "spec-completeness").mkdir(parents=True)
    (tmp_path / "tests" / "harness-layer" / "prompts").mkdir(parents=True)
    write_ac_validation(
        folder,
        [
            "- `[plan-time]` `uv run --script specs/p/checks/ac5_inventory.py` — verifies AC5.",
            "- `[child-build-time]` `uv run pytest tests/harness-layer/hooks/spec-completeness`"
            " — verifies AC1 and AC2.",
            "- `[child-build-time]` `uv run pytest tests/harness-layer/prompts` — verifies AC3.",
            "- `[child-build-time]` `uv run --script specs/p/checks/ac4_ci_workflow.py`"
            " — verifies AC4.",
        ],
    )
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""
