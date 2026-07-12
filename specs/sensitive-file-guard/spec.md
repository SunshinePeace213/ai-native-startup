# Spec: Sensitive File Guard — block agent access to secret-bearing files

- **Owner:** @SunshinePeace213
- **Status:** Approved
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). If round 2 is still changes-requested, the over-cap gate records the exit
       status in ## Codex Verification — approved | accepted-with-unverified-fixes | needs-human. One value only. -->

## Task Description

Build a PreToolUse hook family that prevents the agent from reading or modifying
secret-bearing files — `.env` files, SSH and authentication keys, certificates and
private keys, cloud provider credentials, package-manager credentials, VCS and tool
tokens, CI/CD and IaC secrets, framework secret files, database credential and data
files, shell history, browser credential stores, Kerberos keytabs, crypto wallets,
`/etc/shadow`, and AI-tool auth files.

Two guard scripts share one pattern catalog:

- `file_guard.py` — PreToolUse matcher `Read|Grep|Edit|Write|MultiEdit`: denies any
  call whose target path matches the catalog, after tilde-expansion, relative-path
  normalization, and symlink resolution.
- `bash_guard.py` — PreToolUse matcher `Bash` (registered for both Claude Code and
  Codex): denies any command whose text references a cataloged sensitive path.

A denial is agent-actionable: it names the matched category, states the policy, and
redirects — a `.env` denial points at the repo's `.env.example` / `.env.sample` /
`.env.template` / `.env.dist` when one exists ("read that instead for variable
names"), otherwise "ask the user for the specific values". Safe template files always
pass. Everything else fails open per the repo hook contract (exit 0; exit 2 only on a
confirmed match).

This is the read-side complement to the existing `security-scan/` family, which
guards the write side (secrets the agent writes out).

## Objective

Any Read/Grep/Edit/Write/MultiEdit/Bash tool call that targets a cataloged
sensitive file is denied with exit 2 and a category-specific redirect message before
the tool runs; template files and ordinary files pass untouched; all plumbing
failures fail open — proven by a green `uv run pytest` including a new
`tests/harness-layer/hooks/sensitive-files/` suite and an updated wiring matrix.

## Non-Goals

- **Not a sandbox.** The Bash guard is best-effort text matching; obfuscated
  payloads (base64 wrappers, interpreter escapes, glob dodges like `cat .en?`) can
  evade it. Defense in depth, not containment.
- **No output redaction.** Scanning/redacting secret values in tool *output*
  (PostToolUse) is a recorded follow-up, not part of this plan.
- **No Codex read-tool coverage.** Codex parity is the Bash guard only this round
  (Codex file reads go through shell, so this covers more than it appears;
  `apply_patch` Edit/Write interception is a recorded follow-up).
- **No `permissions.deny` duplication.** The hook is the single source of truth for
  the catalog (see Solution Approach for why the deny-rules alternative lost).
- **No secret-value detection.** The guard matches file *names/paths*, never file
  contents — content scanning stays in `security-scan/`.

## Problem Statement

Agents in this repo can read any file the user can. A prompt-injected or over-eager
agent can pull live secrets into context — where they can be summarized, logged, or
leaked into files it later writes — or tamper with credential files (append a key to
`~/.ssh/authorized_keys`, plant a token in `.npmrc`, overwrite the user's `.env`).
The existing hooks only scan content the agent *writes*; nothing stops a secret from
being *read* in the first place. Blocking at PreToolUse closes the gap at the moment
of access and teaches the agent the correct alternative (templates, or asking the
user) via the denial message.

## Solution Approach

A new self-contained hook family `.claude/hooks/sensitive-files/` mirroring the
`security-scan/` family layout: an importable `_common.py` engine (stdlib-only,
fail-open plumbing copied/adapted from the sibling families) plus two thin hook
scripts. The engine owns:

1. **The catalog** — a data table of rules `(category id, human label, guidance
   message, matcher kind, pattern)`. Two matcher kinds:
   - **basename** patterns (fnmatch-style, case-insensitive) — e.g. `.env`,
     `.env.*`, `*.pem`, `id_rsa*`, `*.tfstate`, `.pgpass`;
   - **path-fragment** patterns (case-insensitive substring on the normalized
     absolute path, slash-bounded so `/.aws/` never matches `/.awsome/`) — e.g.
     `/.ssh/`, `/.aws/`, `/.config/gcloud/`, `/etc/shadow`.
   The full category → pattern table is in
   [decisions.md](./decisions.md) `## Resolved Decisions` (D2) and is the build's
   source of truth.
2. **The allowlist** — template basenames that always pass: `.env.example`,
   `.env.sample`, `.env.template`, `.env.dist`, `example.env`, `sample.env`,
   `template.env`. Checked before any deny.
3. **Path normalization** — `expanduser` → absolutize against cwd → `normpath`;
   check BOTH the normalized path and its `os.path.realpath` (a symlink pointing at
   a sensitive file is caught; a symlink named like a template that resolves to a
   real secret is caught too).
4. **Command-text matching** — one compiled alternation regex built from the same
   catalog: basename patterns get token boundaries — before: start of string,
   whitespace, quote, `/`, `=`, or any shell operator; after: end of string,
   whitespace, quote, or any shell control/redirection delimiter (`|`, `&`, `;`,
   `<`, `>`, `(`, `)`, `:`, `,`, backtick, and newline) — so `cat .env|base64`,
   `cat .env&&echo done`, `cat .env>copy`, and multiline commands are all denied;
   fragments are searched directly.
   The matched token's basename is run through the allowlist before denying, so
   `cat .env.example` passes while `cat .env` is denied. Raw-string matching (not
   shlex) follows the `block_attribution.py` precedent and catches paths inside
   quotes and interpreter one-liners.
5. **The denial message** — 3 stderr lines: `Blocked: '<path>' matches sensitive
   category '<label>'`; the category guidance (for env files: the concrete template
   redirect, detected by scanning the target's directory and the project root for
   the first existing allowlist file); the standing policy line ("never read,
   print, copy, or modify secret-bearing files; ask the user when a value is
   needed"). Exit 2 feeds it back to the agent.

**Deny mechanism:** exit 2 + stderr, matching the in-repo precedent
(`block_attribution.py`, HARNESS-LAYER.md) and the KB hooks-guide protect-files
recipe. Payload fields are the snake_case form the working hooks use:
`tool_input.file_path` (Read/Edit/Write/MultiEdit), `tool_input.path` and
`tool_input.glob` (Grep — `glob` goes through the command-text matcher),
`tool_input.command` (Bash).

**Alternative considered and rejected:** native `permissions.deny` rules
(`Read(./.env)`, `Read(./secrets/**)` — settings.md KB). They produce generic
denials with no redirect guidance, cannot inspect Bash command text, and would split
the catalog across two mechanisms. The hook keeps one catalog, one message style,
and full testability under the existing hook-test framework.

## Requirements & Decisions

- **Tool scope: Read+Grep+Bash plus Edit/Write/MultiEdit** — read-side blocking plus
  tamper/overwrite protection for the same files; one catalog, two matcher blocks.
  (Grilled, locked.)
- **Comprehensive catalog** — all categories listed in Task Description, including
  the noisier ones (DB data files, shell history, wallets); ambiguous matches deny
  with an "ask the user" message rather than pass silently. (Grilled, locked.)
- **Template allowlist is the only escape hatch** — no env-var bypass, no config
  file; loosening the guard means editing the catalog in `_common.py`. (Grilled,
  locked.)
- **Codex parity via the Bash guard only** — `bash_guard.py` joins
  `.codex/hooks.json` exactly as `block_attribution.py` does. (Grilled, locked.)
- **Fail-open everywhere except a confirmed match** — malformed/empty/TTY stdin,
  missing fields, unexpected exceptions → exit 0; exit 2 is reserved for a
  confirmed catalog match with diagnostics on stderr. (Repo hook contract.)

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #26
- **Branch:** feat/26-sensitive-file-guard
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/sensitive-file-guard
- **Review profile:** kb-grounded
- **PR:** <#M — filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

- `.claude/hooks/security-scan/_common.py` — the fail-open plumbing (`note`,
  `read_payload`, stdin timeout, exception wrapper) to copy/adapt; families stay
  self-contained, never cross-import
- `.claude/hooks/block_attribution.py` — the PreToolUse deny precedent: exit 2 +
  stderr, raw-string regex, fail-open posture
- `.claude/settings.json` — register both guards (join the existing PreToolUse
  `Bash` matcher block; add one new `Read|Grep|Edit|Write|MultiEdit` block)
- `.codex/hooks.json` — register `bash_guard.py` in the existing PreToolUse `Bash`
  block (same `$(git rev-parse --show-toplevel)` command form + `statusMessage`)
- `tests/harness-layer/hooks/conftest.py` — the shared `run_hook` launcher and
  `load_hook_module` fixture every test must use
- `tests/harness-layer/hooks/test_wiring.py` — `EXPECTED_BINDINGS` matrix to extend
  with the two new registrations
- `HARNESS-LAYER.md` — add the "Sensitive File Guard (PreToolUse)" section and the
  Files-tree entries
- `HOOK-TESTING.md` — the test-suite rules the new suite must follow

### New Files

- `.claude/hooks/sensitive-files/_common.py` — catalog, allowlist, normalization,
  command-text matcher, denial-message builder, fail-open plumbing
- `.claude/hooks/sensitive-files/file_guard.py` — PreToolUse guard for
  `Read|Grep|Edit|Write|MultiEdit`
- `.claude/hooks/sensitive-files/bash_guard.py` — PreToolUse guard for `Bash`
- `tests/harness-layer/hooks/sensitive-files/test_engine.py` — catalog/allowlist/
  normalization unit tests (in-process via `load_hook_module`)
- `tests/harness-layer/hooks/sensitive-files/test_file_guard.py` — e2e block/allow/
  fail-open tests via `run_hook`
- `tests/harness-layer/hooks/sensitive-files/test_bash_guard.py` — e2e command
  corpus tests via `run_hook`

## Edge Cases

- **Relative and traversal paths** — `file_path: "../../.env"` normalizes to an
  absolute path whose basename matches → deny.
- **Tilde paths** — `~/.aws/credentials` expands before matching → deny.
- **Symlink dodge** — Read of `notes.txt` that is a symlink to `.env`: realpath
  check catches it → deny. A symlink *named* `.env.example` resolving to a real
  `.env` is also denied (allowlist applies only when the realpath is safe too).
- **Template read** — `.env.example` (and the other allowlist names) → exit 0, even
  though `.env.*` would otherwise match.
- **`.env` deny message** — names the template that actually exists next to the
  target or at the project root; if none exists, says "no template found — ask the
  user for the variable names/values you need".
- **Grep without a direct target** — `path` absent or a directory → allow (no
  direct sensitive target; ripgrep skips gitignored files by default, which is the
  usual state of `.env` — residual risk recorded in decisions.md). A `glob` or
  `path` value naming a cataloged file → deny.
- **Bash boundary cases** — `cat .env`, `cp .env /tmp/x`, `source .env`,
  `base64 .env`, `grep KEY .env`, `python -c "open('.env')"`,
  `cat $HOME/.ssh/id_rsa` all deny; shell operators directly after the path deny
  too: `cat .env|base64`, `cat .env&&echo done`, `cat .env>copy`, and a
  multiline command with `cat .env` on its own line. `cat .env.example`,
  `ls -la`, `git status` all pass. `/.awsome/file` does not match the `/.aws/`
  fragment.
- **Bash false positive** — a command merely *mentioning* a cataloged name in
  prose (e.g. `echo "create your .env"`) is denied; the message tells the agent to
  rephrase or ask the user. Accepted tradeoff (decisions.md).
- **Empty/malformed input** — empty stdin, non-JSON stdin, TTY stdin, stdin
  timeout, missing `tool_name`/`tool_input`, non-string paths → exit 0, silent or
  one stderr note; never exit 1, never exit 2.
- **Unexpected exception** — top-level wrapper notes to stderr and exits 0
  (`block_attribution.py` posture).
- **Concurrency / idempotency** — both guards are stateless (no session state, no
  filesystem writes), so parallel tool calls and re-runs are trivially safe.
- **Large inputs** — command strings and paths are matched with compiled regexes;
  no file contents are ever opened, so oversized files cost nothing.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Opening or reading target file *contents* in the guard (name/path matching only)
- Adding a bypass env var, config file, or extra allowlist entries beyond the
  locked template set
- Cross-importing another family's `_common.py` instead of copying the plumbing
- Registering a duplicate PreToolUse `Bash` matcher block instead of joining the
  existing one
- Committing a secret-shaped literal in test fixtures (filenames only — the guard
  never needs secret content)

## Notes

- Stdlib only — no new dependencies (`uv add` not needed).
- PreToolUse hooks fire for subagent tool calls too, so the guard covers the whole
  team, not just the lead session.
- Hook scripts follow the family convention: PEP 723 `# /// script` header,
  `requires-python = ">=3.12"`, run via `uv run --script`.
- Follow-ups recorded in decisions.md: PostToolUse output redaction; Codex
  `apply_patch` (Edit/Write) interception; `/kb` refresh of `hooks.md` (its config
  section diverges from the hooks-guide and repo practice).

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** approved at round 3 (rounds 1–2 changes-requested and fixed; the
  user-approved over-cap delta round verified the round-2 fix)
- **Rejected findings:** none — both blocking findings were applied; the round-2
  advisory (per-rule compiled command patterns) is recorded as follow-up F4 in
  decisions.md rather than applied in this plan

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```text
specs/sensitive-file-guard/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/sensitive-file-guard/ and are saved in the repository
- [x] Codex has reviewed the spec and Status reflects the outcome
