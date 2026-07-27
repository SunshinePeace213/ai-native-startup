"""Cross-family contract for `edited_paths()` -- the one path primitive.

Three hook families need it and cannot import each other (a family `_common`
is only importable from its own directory), so the function is copied three
times. Copies drift; this file is what makes drift impossible: ONE corpus runs
through all three modules, so a fix or a regression in one copy and not the
others fails here.

What the corpus encodes:

* Shape-branching, not a host flag -- a flag typo would silently route a Codex
  payload down the Claude branch, returning [] and skipping every scan and
  guard behind it. The payload already says which shape it is.
* Both halves of a rename. `*** Update File:` alone would let an agent move a
  file ONTO a cataloged sensitive path unchallenged, and would hand a formatter
  a path that no longer exists.
* Directive position. A patch body is attacker-influenced text; a body line
  reading `+*** Add File: /etc/passwd` must never be read as a directive, and a
  real directive must never be maskable by one.
* Fail-open everywhere -- these hooks must never wedge an edit over plumbing.

`hook_host()` rides along here (same `-k edited_paths` selection) because it is
the other half of the host-adaptation primitive.
"""

import pytest

MODULES = (
    "auto-format/_common.py",
    "security-scan/_common.py",
    "sensitive-files/_common.py",
)

CWD = "/repo/workspace"


def envelope(*lines: str) -> str:
    """An apply_patch envelope as Codex sends it: one string, directives at column 0."""
    return "\n".join(("*** Begin Patch", *lines, "*** End Patch")) + "\n"


def patch_payload(command: str, cwd: str | None = CWD) -> dict:
    payload = {"tool_name": "apply_patch", "tool_input": {"command": command}}
    if cwd is not None:
        payload["cwd"] = cwd
    return payload


def oversized_envelope() -> str:
    """An envelope whose second directive sits past the 64 KB scan cap."""
    filler = ("+" + "x" * 79 + "\n") * 900  # ~72 KB of diff body
    return envelope("*** Add File: /repo/first.py", filler, "*** Add File: /repo/last.py")


# (id, payload, expected paths) -- the AC10 corpus, verbatim.
CORPUS = [
    (
        "claude_file_path",
        {"tool_name": "Edit", "tool_input": {"file_path": "/repo/src/app.py"}},
        ["/repo/src/app.py"],
    ),
    ("add", patch_payload(envelope("*** Add File: /repo/new.py")), ["/repo/new.py"]),
    ("update", patch_payload(envelope("*** Update File: /repo/old.py")), ["/repo/old.py"]),
    ("delete", patch_payload(envelope("*** Delete File: /repo/gone.py")), ["/repo/gone.py"]),
    (
        "rename_yields_both_paths",
        patch_payload(envelope("*** Update File: /repo/a.py", "*** Move to: /repo/b.py")),
        ["/repo/a.py", "/repo/b.py"],
    ),
    (
        "two_adds_in_order",
        patch_payload(
            envelope("*** Add File: /repo/one.py", "+alpha", "*** Add File: /repo/two.py", "+beta")
        ),
        ["/repo/one.py", "/repo/two.py"],
    ),
    (
        "all_four_directives_in_order",
        patch_payload(
            envelope(
                "*** Add File: /repo/added.py",
                "+alpha",
                "*** Update File: /repo/updated.py",
                "@@",
                "-two",
                "+TWO",
                "*** Move to: /repo/moved.py",
                "*** Delete File: /repo/deleted.py",
            )
        ),
        ["/repo/added.py", "/repo/updated.py", "/repo/moved.py", "/repo/deleted.py"],
    ),
    (
        "relative_resolves_against_payload_cwd",
        patch_payload(envelope("*** Add File: src/app.py")),
        [f"{CWD}/src/app.py"],
    ),
    (
        "relative_without_cwd_stays_relative",
        patch_payload(envelope("*** Add File: src/app.py"), cwd=None),
        ["src/app.py"],
    ),
    (
        "directive_text_in_diff_body_is_not_a_directive",
        patch_payload(
            envelope(
                "*** Update File: /repo/real.py",
                "@@",
                "-old",
                "+*** Add File: /repo/injected.py",
                " *** Delete File: /repo/masked.py",
                "-*** Move to: /repo/sneaky.py",
            )
        ),
        ["/repo/real.py"],
    ),
    (
        "oversized_envelope_scans_the_prefix",
        patch_payload(oversized_envelope()),
        ["/repo/first.py"],
    ),
    ("no_envelope", patch_payload(""), []),
    ("not_an_envelope", patch_payload("echo hello"), []),
    ("truncated_envelope", patch_payload("*** Begin Patch\n*** Add Fi"), []),
    ("empty_path", patch_payload(envelope("*** Add File:")), []),
    ("missing_command", {"tool_name": "apply_patch", "tool_input": {}}, []),
    ("missing_tool_input", {"tool_name": "Edit"}, []),
    ("tool_input_not_a_dict", {"tool_name": "Edit", "tool_input": "/repo/app.py"}, []),
    ("blank_file_path", {"tool_name": "Edit", "tool_input": {"file_path": "   "}}, []),
    ("bash_payload", {"tool_name": "Bash", "tool_input": {"command": "ls"}}, []),
    ("none_payload", None, []),
]


@pytest.fixture(params=MODULES, ids=lambda path: path.split("/")[0])
def common(request, load_hook_module):
    """Each family's `_common`, loaded in-process under a collision-free name."""
    return load_hook_module(request.param)


@pytest.mark.parametrize(
    ("payload", "expected"),
    [(payload, expected) for _, payload, expected in CORPUS],
    ids=[case_id for case_id, _, _ in CORPUS],
)
def test_edited_paths_contract(common, payload, expected):
    """One corpus, three copies: every family must agree on which files a
    payload writes, or the guard/formatter behind one of them silently sees a
    different set of files than the others."""
    assert common.edited_paths(payload) == expected


def test_edited_paths_never_raises_on_hostile_input(common):
    """A hook that raised here would wedge the edit it was inspecting; every
    caller relies on [] as the universal "nothing to do" answer."""
    for payload in ([], "string", 42, {"tool_input": None}, {"tool_input": {"file_path": None}}):
        assert common.edited_paths(payload) == []


def test_hook_host_defaults_to_claude(monkeypatch, load_hook_module):
    """Claude Code sets no host variable, so the unset case must keep Claude's
    ask tier -- a wrong default would turn nine ask rules into denies in Claude."""
    guard = load_hook_module("destructive-guard/_common.py")
    monkeypatch.delenv("HARNESS_HOOK_HOST", raising=False)
    assert guard.hook_host() == "claude"


def test_hook_host_reads_the_registration_variable(monkeypatch, load_hook_module):
    """`.codex/hooks.json` is the only thing that sets it; Codex cannot honour an
    "ask", so the host must be detectable to convert those rules to denies."""
    guard = load_hook_module("destructive-guard/_common.py")
    monkeypatch.setenv("HARNESS_HOOK_HOST", " Codex \n")
    assert guard.hook_host() == "codex"
