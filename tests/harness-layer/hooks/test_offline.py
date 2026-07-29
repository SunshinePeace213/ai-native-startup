"""Offline tests: a hook that needs the network is a hook that blocks the agent.

Every hook runs on the critical path of a tool call, and Codex sessions run
sandboxed with `network_access` off. A hook whose PEP 723 header drags in an
uncached dependency would hang or die there -- turning a guard into an outage.
`uv run --offline` proves each entrypoint boots and fails open from cache
alone.

On a genuinely cold uv cache the offline run cannot succeed for reasons that
have nothing to do with this repo, so those runs SKIP: a fresh clone must not
go red environmentally. Coldness is detected from uv's own cache-miss text --
any other failure still fails.
"""

import os
import shutil
import subprocess

import pytest
from test_wiring import HOOKS_ROOT, REPO_ROOT, entrypoints

UV = shutil.which("uv")
assert UV, "uv is required to run the hook tests"

# uv's own wording when --offline hits an uncached package or interpreter.
COLD_CACHE_MARKERS = (
    "not found in the cache",
    "network was disabled",
    "uv is set to offline mode",
)


@pytest.mark.timeout(120)
@pytest.mark.parametrize("script", sorted(entrypoints()))
def test_entrypoint_runs_offline(script: str, tmp_path):
    """Booting with empty stdin exercises the whole cold path -- interpreter
    resolution, dependency install, import, fail-open -- without depending on
    the hook's payload semantics. Exit 0 is the fail-open contract; a nonzero
    exit here means the hook is unusable in a network-less session.

    The project dir points at an empty tmp_path: a hook that inspects the repo
    rather than stdin (check_spec_completeness) would otherwise report on the
    live specs/ tree, turning this cold-boot check into a spec-content check
    that goes red whenever a plan is mid-draft."""
    result = subprocess.run(
        [UV, "run", "--offline", "--script", str(HOOKS_ROOT / script)],
        input="",
        capture_output=True,
        text=True,
        timeout=45,  # under pytest-timeout's ceiling, so the test still reports
        env=os.environ
        | {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "CLAUDE_PROJECT_DIR": str(tmp_path),
        },
        cwd=REPO_ROOT,
    )
    if result.returncode and any(m in result.stderr for m in COLD_CACHE_MARKERS):
        pytest.skip(f"uv cache is cold for {script}: {result.stderr.strip()}")
    assert result.returncode == 0, f"{script} exited {result.returncode}: {result.stderr}"
