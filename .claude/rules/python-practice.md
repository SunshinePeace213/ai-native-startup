---
paths:
  - "**/*.py"
  - "**/*.pyi"
  - "pyproject.toml"
---

# Python Practice

Conventions for any Python work in this repo — general runtime and testing. This rule is
path-scoped, so it loads automatically whenever a Python file is open.

## General

- **Runtime**: always `uv` (Astral) — `uv run`, `uv sync`, `uv add`. Never raw `python`,
  `pip`, or a hand-activated venv.
- **Rich panels**: always full-width.

## Testing

The plugins are already wired in `pyproject.toml` — don't reinvent what they provide. The
common case needs no flags.

- **Run the suite**: `uv run pytest` from the repo root. That alone runs `tests/` in
  parallel (`-n auto`, pytest-xdist), with pytest-sugar output and a 60s per-test timeout
  (pytest-timeout). Reach for a flag only when a case below calls for one.
- **Foucs one feature**: Do not run full suite during development. 
  Focus on requirements of the task. Run the full suite before hand off. 
- **Debug one test**: `uv run pytest <file>::<test> -n 0` — `-n 0` disables workers so
  `-s`, breakpoints, and ordered output work.
- **Coverage**: `uv run pytest --cov=<path> --cov-report=term-missing` (pytest-cov) —
  measures in-process code only; code exercised via subprocess (e.g. the hooks) reports 0%.
- **Mocking**: use the `mocker` fixture (pytest-mock; patches auto-undo at teardown) or
  built-in `monkeypatch`; never import `unittest.mock` directly.
- **Parallel-safe**: isolate all state per test (`tmp_path`, `monkeypatch`); never rely on
  test order, shared globals, or fixed paths/ports.
- **Timeouts**: a hung test is killed at 60s; mark a known-slow test
  `@pytest.mark.timeout(120)` — never raise the global value.
- **No flake-retry plugins**: a failing test fails the run — fix it, don't auto-rerun it.
- **UI**: the sugar theme lives in `pytest-sugar.conf` (repo root, loaded from cwd);
  `-p no:sugar` for plain output. The live bar renders only on a TTY — non-TTY runs
  (agents, CI) fall back to plain dots, which is correct for log parsing.
