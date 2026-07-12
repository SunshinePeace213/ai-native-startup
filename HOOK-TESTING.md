# Hook Testing

Rules for the hook test suite in `tests/harness-layer/hooks/`.

- **One launcher**: run every hook through the shared `run_hook` fixture (root
  `conftest.py`), addressing the script relative to `.claude/hooks/` (e.g.
  `"auto-format/python.py"`). Never spawn `uv run --script` from a test file.
- **Env via knobs**: the launcher's base env is git-isolated (host git config shut
  out, `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` scrubbed). Express intent with
  `env_overrides=` / `unset_env=`; never hand-build an `os.environ` copy.
- **In-process imports**: load hook modules with the `load_hook_module` fixture.
  Never `sys.path.insert` or a bare `import _common` — the families' `_common`
  names collide in `sys.modules`.
- **Contract tests per feature dir**: `tests/harness-layer/hooks/<feature>/` mirrors
  `.claude/hooks/<feature>/`. Test block AND allow paths; malformed or empty stdin
  must fail open (exit 0). Exit 2 is reserved for agent-fixable findings and must
  carry `file:line rule` diagnostics on stderr.
- **Wiring is tested**: every executable hook (PEP 723 `# /// script` marker or
  shebang) must be registered — in `settings.json` or a command-frontmatter
  registrar — and bound in `test_wiring.py`'s `EXPECTED_BINDINGS`. Adding, moving,
  or re-matching a hook means updating that matrix in the same change.
- **Secret-shaped fixtures**: assemble them at runtime from fragments; never commit
  a matchable literal (the security scanner and GitHub push protection both read
  this repo).
- **Timeouts**: the launcher's subprocess timeout is 45s, under pytest's global
  60s. Raise neither; mark a known-slow test `@pytest.mark.timeout(120)`.
- **Docstrings encode intent**: every test states WHY the behavior matters, not
  just what it does.
