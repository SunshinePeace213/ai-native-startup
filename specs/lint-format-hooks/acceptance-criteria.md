# Acceptance Criteria: lint-format-hooks

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — Dev-tool manifests and configs exist and are valid: `package.json` lists
  `prettier` and `markdownlint-cli2` as devDependencies; `pyproject.toml` declares `ruff` as
  a dev dependency and carries `[tool.ruff]` (`line-length = 100`, `target-version = "py312"`)
  and `[tool.ruff.lint] select = ["E","F","I","UP","B","SIM"]`; `.prettierrc.json`,
  `.prettierignore` (excludes `*.md`), and `.markdownlint.jsonc` (disables MD013/MD033/MD041)
  are present and parse; `bun.lock` and `uv.lock` exist.
- **AC2** — `install_deps.py` installs the declared tools idempotently: a first run makes
  `prettier`, `markdownlint-cli2`, and `ruff` resolvable in the working directory; a second
  run succeeds as a no-op; both runs exit 0 and never crash the caller. If a declared tool is
  missing it prints a warning rather than mutating a manifest.
- **AC3** — `lint.py` auto-fixes by extension and never blocks: fed a `PostToolUse` stdin
  payload naming a `.ts` file, it rewrites it to Prettier style (double quotes, ≤100 width);
  a `.py` file is `ruff format` + `ruff check --fix`ed; a `.md` file is markdownlint-fixed
  under the lenient config; an unknown extension is a silent no-op; a missing tool yields a
  stderr note; **every** invocation exits 0 (never 2).
- **AC4** — The lint hook is registered and the existing one is preserved: `.claude/settings.local.json`
  is valid JSON, contains a `PostToolUse` entry with matcher `Write|Edit|MultiEdit` invoking
  `lint.py`, and still contains the original `PreToolUse` Bash `block-coauthor-trailer.sh` hook
  and `enabledPlugins`. No `WorktreeCreate` hook is registered: the official worktrees doc
  (`ai-docs/anthropic/worktrees.md`) states a `WorktreeCreate` hook **replaces** git's default
  worktree creation, so install is owned by `/meta-install` (+ warn-and-skip), not a hook.
- **AC5** — `/meta-install` exists as `.claude/commands/meta-install.md` with YAML frontmatter
  (a `description`) and a body that runs the installer / `bun install` + `uv sync`. This is the
  install path for both a first contributor checkout and a fresh worktree.
- **AC6** — End to end: editing a `.ts`, `.py`, and `.md` file via Write/Edit in a session
  rooted at this repo results in each being auto-formatted with no turn blocked; the linter's
  behavior on a fresh worktree before `/meta-install` has run is warn-and-skip (edit still succeeds).

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `test -f package.json && test -f pyproject.toml && test -f bun.lock && test -f uv.lock && test -f .prettierrc.json && test -f .prettierignore && test -f .markdownlint.jsonc && echo FILES_OK` — verifies **AC1** (all files exist). Pass = prints `FILES_OK`.
- `uv run --no-project python -c "import json; dd=json.load(open('package.json')).get('devDependencies',{}); assert 'prettier' in dd and 'markdownlint-cli2' in dd, dd; print('PKG_OK')"` — verifies **AC1** (package.json declares both JS tools as devDependencies). Pass = prints `PKG_OK`.
- `uv run --no-project python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); r=d['tool']['ruff']; assert r['line-length']==100 and r['target-version']=='py312', r; assert {'E','F','I','UP','B','SIM'} <= set(r['lint']['select']), r['lint']['select']; dev=d.get('dependency-groups',{}).get('dev',[]) + d.get('tool',{}).get('uv',{}).get('dev-dependencies',[]); assert any('ruff' in x for x in dev), dev; print('RUFF_OK')"` — verifies **AC1** (ruff is a dev dep and `[tool.ruff]` values match the spec). Pass = prints `RUFF_OK`.
- `uv run --no-project python -c "import json; d=json.load(open('.prettierrc.json')); assert d['printWidth']==100 and d['singleQuote'] is False and d['trailingComma']=='all' and d['tabWidth']==2 and d['semi'] is True, d; print('PRETTIER_OK')"` — verifies **AC1** (Prettier options match the spec, incl. double quotes). Pass = prints `PRETTIER_OK`.
- `grep -qxF '*.md' .prettierignore && echo IGNORE_OK` — verifies **AC1** (Prettier ignores Markdown). Pass = prints `IGNORE_OK`.
- `grep -Eq '"MD013"[[:space:]]*:[[:space:]]*false' .markdownlint.jsonc && grep -Eq '"MD033"[[:space:]]*:[[:space:]]*false' .markdownlint.jsonc && grep -Eq '"MD041"[[:space:]]*:[[:space:]]*false' .markdownlint.jsonc && echo MDLINT_OK` — verifies **AC1** (lenient markdownlint disables MD013/MD033/MD041). Pass = prints `MDLINT_OK`.
- `uv run --script .claude/hooks/install_deps.py && uv run --script .claude/hooks/install_deps.py && echo IDEMPOTENT_OK` — verifies **AC2** (installs, then no-ops). Pass = both runs exit 0, prints `IDEMPOTENT_OK`.
- `printf '{"tool_name":"Write","tool_input":{"file_path":"/tmp/acc.ts"}}' > /tmp/in.json; printf 'const x={a:1,b:2}\n' > /tmp/acc.ts; uv run --script .claude/hooks/lint.py < /tmp/in.json; echo "exit=$?"; cat /tmp/acc.ts` — verifies **AC3** (TS formatted, exit 0). Pass = file reformatted with double quotes, `exit=0`.
- `printf '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/acc.py"}}' > /tmp/inpy.json; printf "x = {'a':1}\n" > /tmp/acc.py; uv run --script .claude/hooks/lint.py < /tmp/inpy.json; echo "exit=$?"; cat /tmp/acc.py` — verifies **AC3** (Python ruff-formatted, exit 0). Pass = double-quoted/normalized, `exit=0`.
- `printf '{"tool_name":"Write","tool_input":{"file_path":"/tmp/acc.md"}}' > /tmp/inmd.json; printf '#   Title  \n\n\n- a\n' > /tmp/acc.md; uv run --script .claude/hooks/lint.py < /tmp/inmd.json; echo "exit=$?"` — verifies **AC3** (Markdown fixed, exit 0). Pass = `exit=0`, trailing spaces/blank lines fixed.
- `printf '{"tool_name":"Write","tool_input":{"file_path":"/tmp/acc.xyz"}}' | uv run --script .claude/hooks/lint.py; echo "exit=$?"` — verifies **AC3** (unknown ext no-op). Pass = `exit=0`, no error.
- `uv run --no-project python -c "import json; h=json.load(open('.claude/settings.local.json'))['hooks']; assert any(e.get('matcher')=='Write|Edit|MultiEdit' and any('lint.py' in x['command'] for x in e['hooks']) for e in h['PostToolUse']); assert 'WorktreeCreate' not in h, 'WorktreeCreate must not be registered (it replaces git worktree creation)'; assert any('block-coauthor' in x['command'] for e in h['PreToolUse'] for x in e['hooks']); print('HOOKS_OK')"` — verifies **AC4** (PostToolUse matcher + lint.py, no WorktreeCreate hook, and the original PreToolUse hook preserved). Pass = prints `HOOKS_OK`.
- `test -f .claude/commands/meta-install.md && grep -q 'description:' .claude/commands/meta-install.md && grep -Eq 'install|uv sync|bun install' .claude/commands/meta-install.md && echo META_OK` — verifies **AC5**. Pass = prints `META_OK`.
- Manual **AC6**: in a session rooted at this repo, edit a `.ts`, `.py`, and `.md` file and confirm each is auto-formatted and no turn is blocked; in a fresh worktree with no install, confirm an edit still completes (warn-and-skip). Pass = formatting applied where tools exist; edits never blocked.
