"""Contract tests for the JS/TS format hook (js_ts.py).

The exit-code contract is the product: exit 2 with ``file:line rule
message`` diagnostics ONLY for genuine unfixable ESLint errors, exit 0
with the file autofixed (ESLint --fix + Prettier --write) for everything
healthy, and exit 0 untouched for every plumbing problem -- wrong
extension, vendored path, missing file, garbage stdin, missing binaries.
Out-of-repo files get their own test because ESLint silently ignores
anything outside its base path ("File ignored because outside of base
path") -- without the fallback, scratchpad edits would never be formatted.
"""

# eslint-fixable (no-extra-boolean-cast) + prettier-fixable (quotes, semicolons)
FIXABLE_TS = "const flag = 'x'\nexport default !!flag ? 1 : 2\n"


def test_fixable_file_is_formatted_in_place(linter_root, run_hook, edit_payload, project_env):
    """Both stages must land: ESLint autofix (the !! cast) and Prettier style
    (double quotes, semicolons) -- the agent's edit is normalized for free."""
    fixture = linter_root / "src.ts"
    fixture.write_text(FIXABLE_TS)
    proc = run_hook(
        "auto-format/js_ts.py", edit_payload(fixture), env_overrides=project_env(linter_root)
    )
    content = fixture.read_text()
    assert proc.returncode == 0
    assert "!!" not in content  # eslint no-extra-boolean-cast fix applied
    assert 'const flag = "x";' in content  # prettier quotes + semicolons applied


def test_unfixable_error_exits_2_with_rule_and_location(
    linter_root, run_hook, edit_payload, project_env
):
    """An error --fix cannot solve is the agent's to fix: stderr must carry
    the rule id and a file:line locator it can navigate to."""
    fixture = linter_root / "bad.ts"
    fixture.write_text("const unused = 1\nexport default 2\n")
    proc = run_hook(
        "auto-format/js_ts.py", edit_payload(fixture), env_overrides=project_env(linter_root)
    )
    assert proc.returncode == 2
    assert "@typescript-eslint/no-unused-vars" in proc.stderr
    assert "bad.ts:1" in proc.stderr


def test_out_of_repo_file_is_still_formatted(
    linter_root, run_hook, edit_payload, project_env, tmp_path
):
    """Scratch files outside the project are outside ESLint's base path and
    would be silently skipped; the hook must lint them from their own
    directory with the project config instead."""
    fixture = tmp_path / "outside" / "scratch.ts"
    fixture.parent.mkdir()
    fixture.write_text(FIXABLE_TS)
    proc = run_hook(
        "auto-format/js_ts.py", edit_payload(fixture), env_overrides=project_env(linter_root)
    )
    assert proc.returncode == 0
    assert "!!" not in fixture.read_text()


def test_vendored_path_is_untouched(linter_root, run_hook, edit_payload, project_env):
    """Generated/vendored trees are nobody's edit: a file under dist/ must be
    left byte-identical even though its content would otherwise lint."""
    fixture = linter_root / "dist" / "gen.ts"
    fixture.parent.mkdir()
    fixture.write_text("const bad = 'keep me broken'\n")
    proc = run_hook(
        "auto-format/js_ts.py", edit_payload(fixture), env_overrides=project_env(linter_root)
    )
    assert proc.returncode == 0
    assert fixture.read_text() == "const bad = 'keep me broken'\n"


def test_non_matching_extension_is_ignored(linter_root, run_hook, edit_payload, project_env):
    """The settings.json matcher is tool-name only, so extension filtering is
    this hook's job -- a .txt edit must pass through untouched."""
    fixture = linter_root / "notes.txt"
    fixture.write_text(FIXABLE_TS)
    proc = run_hook(
        "auto-format/js_ts.py", edit_payload(fixture), env_overrides=project_env(linter_root)
    )
    assert proc.returncode == 0
    assert fixture.read_text() == FIXABLE_TS


def test_malformed_stdin_fails_open(linter_root, run_hook, project_env):
    """Garbage stdin is a harness bug, not a lint error -- never exit 2."""
    proc = run_hook("auto-format/js_ts.py", "not json {", env_overrides=project_env(linter_root))
    assert proc.returncode == 0


def test_missing_binaries_note_meta_install(tmp_path, run_hook, edit_payload, project_env):
    """A fresh clone has no node_modules: the hook must skip with a note
    naming the meta-install skill so the agent knows the actual fix."""
    bare = tmp_path / "bare"
    bare.mkdir()
    fixture = bare / "x.ts"
    fixture.write_text(FIXABLE_TS)
    proc = run_hook("auto-format/js_ts.py", edit_payload(fixture), env_overrides=project_env(bare))
    assert proc.returncode == 0
    assert "meta-install" in proc.stderr
    assert fixture.read_text() == FIXABLE_TS


def test_missing_file_fails_open_with_note(linter_root, run_hook, edit_payload, project_env):
    """A file deleted between edit and hook is a race, not an error."""
    proc = run_hook(
        "auto-format/js_ts.py",
        edit_payload(linter_root / "ghost.ts"),
        env_overrides=project_env(linter_root),
    )
    assert proc.returncode == 0
    assert "no longer exists" in proc.stderr
