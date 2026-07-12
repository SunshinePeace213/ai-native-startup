# Decisions: Sensitive File Guard — block agent access to secret-bearing files

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

A new PreToolUse hook family `.claude/hooks/sensitive-files/` denies agent access to
secret-bearing files across a comprehensive catalog, on both the file tools
(`Read|Grep|Edit|Write|MultiEdit`) and `Bash` (the Bash guard also registered for
Codex). Denials are exit-2 + stderr with category-specific redirects — `.env` points
at the repo's template file when one exists. The only escape hatch is the fixed
template allowlist; everything that isn't a confirmed match fails open. All four
user-facing decisions were grilled and the recommended option accepted each time
(accept-all path); implementation-level calls are recorded as assumptions below.

## Resolved Decisions

- **Q (D1):** Which tool calls should the guard cover?
  - **A:** `Read`, `Grep`, `Bash`, plus `Edit`/`Write`/`MultiEdit`.
  - **Why:** Read-side blocking alone leaves credential *tampering* open (appending
    to `authorized_keys`, planting tokens in `.npmrc`, overwriting the user's
    `.env`). Same catalog, one extra matcher block. Rules out the read-only and
    Read+Bash-only variants.

- **Q (D2):** How broad should the blocked-file catalog be?
  - **A:** Comprehensive — every category below. Ambiguous files deny with an "ask
    the user" message rather than pass.
  - **Why:** The user explicitly asked "what sensitive files should be blocked —
    any missing?"; a blocked-with-guidance false positive is recoverable, a leaked
    secret is not. The definitive catalog (build source of truth):

    | Category | Basename patterns | Path fragments |
    | --- | --- | --- |
    | Environment files | `.env`, `.env.*`, `*.env`, `.envrc`, `.flaskenv` | — |
    | SSH & auth keys | `id_rsa*`, `id_dsa*`, `id_ecdsa*`, `id_ed25519*`, `*.ppk` | `/.ssh/` |
    | Certificates & private keys | `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.asc`, `*.gpg`, `*.pgp` | `/.gnupg/`, `/letsencrypt/live/` |
    | Cloud provider credentials | `service-account*.json`, `serviceaccount*.json`, `serviceAccountKey.json` | `/.aws/`, `/.azure/`, `/.config/gcloud/`, `/.kube/`, `/.docker/config.json`, `/.oci/`, `/.aliyun/`, `/.config/doctl/`, `/.fly/` |
    | Package-manager credentials | `.npmrc`, `.yarnrc.yml`, `.pypirc`, `.netrc`, `_netrc` | `/.gem/credentials`, `/.cargo/credentials`, `/.m2/settings.xml`, `/.gradle/gradle.properties`, `/.composer/auth.json`, `/.bundle/config`, `/.config/pip/pip.conf`, `/.nuget/nuget.config` |
    | VCS & tool credentials | `.git-credentials` | `/.config/gh/hosts.yml`, `/.config/glab-cli/`, `/.svn/auth/` |
    | CI/CD & IaC secrets | `.vault-token`, `.terraformrc`, `terraform.rc`, `*.tfstate`, `*.tfstate.*`, `*.tfvars`, `*.tfvars.json`, `.secrets`, `.vault_pass*` | `/.circleci/cli.yml` |
    | Framework & app secrets | `master.key`, `credentials.yml.enc`, `secrets.yml`, `secrets.yaml`, `secrets.json`, `secrets.toml`, `local_settings.py` | — |
    | Database credentials & data | `.pgpass`, `.my.cnf`, `.mylogin.cnf`, `*.sqlite`, `*.sqlite3`, `*.db` | — |
    | Shell & REPL history | `.bash_history`, `.zsh_history`, `.sh_history`, `.psql_history`, `.mysql_history`, `.rediscli_history`, `.sqlite_history`, `.node_repl_history`, `.python_history` | — |
    | Browser & OS credential stores | `logins.json`, `key3.db`, `key4.db`, `*.kdbx`, `*.keychain`, `*.keychain-db` | `/login data`, `/cookies`, `/etc/shadow`, `/etc/gshadow` |
    | Kerberos | `*.keytab`, `krb5cc*` | — |
    | Crypto wallets | `wallet.dat`, `*.wallet`, `UTC--*` | — |
    | AI-tool auth | `.claude.json` | `/.claude/.credentials.json`, `/.codex/auth.json` |

    All matching is case-insensitive; fragments are slash-bounded (`/.aws/` never
    matches `/.awsome/`). Rules out the core-credentials-only tier.

- **Q (D3):** What escape hatch should exist for false positives?
  - **A:** Template allowlist only: `.env.example`, `.env.sample`, `.env.template`,
    `.env.dist`, `example.env`, `sample.env`, `template.env`. No env-var bypass, no
    project allowlist file.
  - **Why:** Simplest possible surface; a bypass knob is itself an injection
    target. Loosening the guard is a deliberate code change to the catalog. Rules
    out the env-var and config-file variants.

- **Q (D4):** Register for Codex sessions too?
  - **A:** Yes — `bash_guard.py` joins `.codex/hooks.json` PreToolUse `Bash`,
    exactly as `block_attribution.py` does today.
  - **Why:** Codex file reads go through shell commands, so the Bash guard is the
    high-value surface there; `apply_patch` (Edit/Write alias) interception is a
    follow-up (see below). Rules out Claude-Code-only scope.

- **Q (D5):** Deny mechanism — exit-2/stderr vs the JSON `{approved: false}` return
  documented in the KB hooks reference?
  - **A:** Exit 2 + stderr.
  - **Why:** Conflict surfaced, not averaged (engineering rule 7): the KB
    `hooks.md` reference describes a `.claude/hooks.json` config format with
    camelCase payloads and stdout-JSON returns, which contradicts both the KB
    hooks-guide recipe (settings.json matchers, `tool_input.file_path`, exit 2)
    and every working hook in this repo. The in-repo precedent is the more tested
    pattern here; `hooks.md` is flagged for a `/kb` refresh (follow-up F3).

- **Q (D6):** New family vs extending `security-scan/`?
  - **A:** New sibling family `sensitive-files/`.
  - **Why:** Different concern (read-side access control vs write-side content
    scanning), and the per-feature restructure convention keeps families
    self-contained with copied plumbing, never cross-imports.

- **Q (D7):** Bash matching — shlex tokenization vs raw-string regex?
  - **A:** Raw-string regex with token boundaries, allowlist applied to the matched
    token's basename.
  - **Why:** Catches paths inside quotes, `$HOME` interpolations, and interpreter
    one-liners that tokenization misses; `block_attribution.py` precedent. Cost:
    prose mentions can false-positive (accepted, A6).

## Assumptions

- **A1** — Family/dir name `sensitive-files`; scripts `file_guard.py`,
  `bash_guard.py`. Invalidated only by a naming-convention objection at review.
- **A2** — Priority P1 (security guardrail, no data-loss incident pending).
- **A3** — `Glob` tool stays unguarded: it returns filenames, never contents.
  Invalidated if Glob ever returns content previews.
- **A4** — `NotebookEdit` stays unguarded: notebooks aren't in any catalog
  category. Invalidated if a secret-bearing `.ipynb` pattern emerges.
- **A5** — Grep over a directory (no direct sensitive target) is allowed; ripgrep
  skips gitignored files by default, which is the usual state of `.env`.
  Invalidated for repos that commit secrets or pass ignore-overriding flags.
- **A6** — Bash prose false positives (e.g. `echo "create your .env"`) are
  acceptable: the denial message tells the agent to rephrase or ask the user.
- **A7** — The three-line denial message format (Blocked / guidance / policy) is
  enough for the agent to self-correct; no JSON payload needed.
- **A8** — `~/.claude/` is NOT blocked wholesale (agents legitimately read
  `~/.claude/CLAUDE.md`); only `.claude/.credentials.json` and `~/.claude.json`
  are cataloged.

## Open Questions / Out of Scope

- **Out of scope:** PostToolUse output redaction of secret values (follow-up F1).
- **Out of scope:** Codex `apply_patch` (Edit/Write alias) interception — feasible
  per the Codex hooks KB doc (follow-up F2).
- **Out of scope:** sandbox-grade Bash containment; obfuscated or glob-dodge
  payloads can evade text matching.
- **Out of scope:** `permissions.deny` rules alongside the hook (single source of
  truth; settings.md KB documents the rejected alternative).
- **Out of scope (considered, excluded as too noisy or too generic):** `.mcp.json`
  (legit project file; write-side scanner catches literal secrets), `.gitconfig`,
  `.git/config`, `appsettings.*.json`, `*.sql` dumps, `.condarc`, Jenkins
  `credentials.xml`, bare `credentials`/`credentials.json`, `clouds.yaml`.
- **Follow-ups checklist** (advisories & deferred work — feeds a future plan):
  - [ ] **F1** — PostToolUse redaction pass over tool output.
  - [ ] **F2** — Codex `apply_patch` Edit/Write guard in `.codex/hooks.json`.
  - [ ] **F3** — `/kb` refresh of `ai-docs/anthropic/hooks.md` (config-format
    section diverges from hooks-guide and repo practice).

## KB References

- `ai-docs/anthropic/hooks.md` (fetched 2026-07-05) — PreToolUse event semantics,
  matcher availability, lifecycle; its config-format section conflicts with repo
  practice (see D5).
- `ai-docs/anthropic/hooks-guide.md` (fetched 2026-07-05) — the "Block edits to
  protected files" recipe: PreToolUse + protected patterns + exit 2 + stderr,
  `tool_input.file_path`, settings.json `matcher` registration.
- `ai-docs/anthropic/settings.md` (fetched 2026-07-06) — hooks registration in
  settings scopes; `permissions.deny` `Read(./.env)` alternative (rejected, D5/
  spec Solution Approach).
- `ai-docs/openai/codex/hooks.md` (fetched 2026-07-05) — `.codex/hooks.json`
  layering, PreToolUse `matcher` regex on tool name (`Bash`; `apply_patch` with
  `Edit`/`Write` aliases → follow-up F2).
