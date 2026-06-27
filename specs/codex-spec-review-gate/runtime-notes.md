# Codex Runtime Notes (Task 1 — verify-codex-runtime)

Empirically verified against **Codex CLI 0.142.3** (`codex-cli 0.142.3`, bin `/Users/ringo/.local/bin/codex`),
running from the worktree `/Users/ringo/Desktop/ai-native-startup/.claude/worktrees/codex-spec-review-gate`.
Default model is `gpt-5.5` (high reasoning), auth = chatgpt. All probes below were run and observed;
nothing here is assumed. Throwaway probe skill + scratch files were cleaned up via `mv … ~/.Trash/`.

Tasks 2–4 should copy the command templates verbatim, substituting `<SPEC_PATH>` and `<REPO_ROOT>`.

---

## 1. Discovery Path (A1) — RESOLVED: repo-level `.agents/skills/` WORKS. No fallback needed.

**Verified path:** `.agents/skills/<name>/SKILL.md` at the repo root **is genuinely auto-discovered
and injected** by Codex 0.142.3 when `codex exec` runs with its working root at/under that repo.
So the canonical, version-controlled path the plan wants —
`.agents/skills/spec-review/SKILL.md` — is correct. **No user-level fallback / no LOUD flag required.**

**How it was proven (not inferred):** a throwaway probe skill was created at
`.agents/skills/zzz-probe/SKILL.md` (name `zzz-probe`; sentinel `SENTINEL_ZZZPROBE_K7M2Q9X` placed
ONLY in the skill body, never in any prompt). Then Codex was asked — *without permission to read any
files* — to list its injected skills:

```bash
codex exec -C "$REPO_ROOT" -s read-only \
  "Do NOT read any files. Answer from your injected context only: list every Skill currently available to you and the directory each was loaded from. If no skills were injected into your context, say exactly: NO_INJECTED_SKILLS"
```

Codex listed, from injected context alone:

```
- imagegen:        /Users/ringo/.codex/skills/.system/imagegen
- openai-docs:     /Users/ringo/.codex/skills/.system/openai-docs
- plugin-creator:  /Users/ringo/.codex/skills/.system/plugin-creator
- skill-creator:   /Users/ringo/.codex/skills/.system/skill-creator
- skill-installer: /Users/ringo/.codex/skills/.system/skill-installer
- zzz-probe:       /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/codex-spec-review-gate/.agents/skills/zzz-probe
```

The repo-level `zzz-probe` appears in the injected registry → genuine discovery (not the model guessing
a conventional path). After `mv .agents/skills/zzz-probe ~/.Trash/…`, a re-check confirmed the same
prompt now answers `NO` — the skill disappeared from the registry. Both user-level
`~/.codex/skills/<name>/` AND repo-level `.agents/skills/<name>/` are injected.

**Constraints to honor in the loop:**
- Discovery is keyed to the **working root**. The `.agents/skills/` dir must be reachable from the cwd
  (Codex scans from cwd up to the repo root). Always pass `-C "<REPO_ROOT>"` (or run from the repo root)
  so the repo's `.agents/skills/spec-review` is discovered. Running `codex exec` from an unrelated cwd
  will NOT find it.
- The skill dir lives at the repo root: `<REPO_ROOT>/.agents/skills/spec-review/SKILL.md`.
- `codex exec` has **no `--skill` flag**; skills are auto-injected and invoked by naming them in the
  prompt (see §3).

---

## 2. Write Flag (A2) — RESOLVED: `-s workspace-write` (default already grants it via ancestor trust)

**Exact minimal flag for guaranteed, config-independent writes:** `-s workspace-write`.

Writable roots under that mode are `[workdir, /tmp, $TMPDIR]`, where `workdir` is the `-C` directory.
So a `plan.md` inside the worktree is writable. **No `~/.codex/config.toml` edit is needed**, and the
`--dangerously-bypass-approvals-and-sandbox` last resort was NOT required.

**Two valid answers, recorded honestly:**
- **Default exec (no sandbox flag) already writes.** Because `[projects."/Users/ringo"]` is
  `trust_level = "trusted"` and the worktree is a descendant, ancestor trust applies and exec auto-selects
  `sandbox: workspace-write`. Proven below.
- **Explicit `-s workspace-write`** forces the same mode regardless of trust config — recommended for the
  loop so write capability never silently depends on `config.toml` state.

**Test commands + proof it wrote:**

```bash
# (a) default sandbox — no flag:
codex exec -C "$REPO_ROOT" \
  "Append a single line containing exactly WRITE_TEST_OK_9Z3 to the file specs/codex-spec-review-gate/.codex-write-test.txt (create it if it does not exist) using a shell command, then stop."
#   -> run banner showed: sandbox: workspace-write [workdir, /tmp, $TMPDIR]
#   -> cat of the file returned: WRITE_TEST_OK_9Z3   (write landed)

# (b) explicit flag:
codex exec -C "$REPO_ROOT" -s workspace-write \
  "Append a single line containing exactly WRITE_TEST_OK_EXPLICIT to the file specs/codex-spec-review-gate/.codex-write-test2.txt (create if missing) using a shell command, then stop."
#   -> cat of the file returned: WRITE_TEST_OK_EXPLICIT   (write landed)
```

Both scratch files were moved to `~/.Trash/` after verification.

**Notes / gotchas (fail-loud):**
- `--full-auto` and `-a/--ask-for-approval` are **top-level flags only — they do NOT exist on
  `codex exec`** (passing `-a` to exec errors: `unexpected argument '-a' found`). Do not put them in the
  loop's `codex exec` invocation.
- `codex exec` runs non-interactively and the banner shows `approval: never` by default, so a
  workspace-write run does not hang on an approval prompt. No extra approval flag is needed.

---

## 3. Invocation Syntax (A3) — RESOLVED: name the skill in the prompt; both forms trigger

Two phrasings were tested against the probe and **both reliably triggered** it (sentinel emitted):

- Natural-language form (recommended for the loop):
  `Use the zzz-probe skill and follow its instructions exactly.` → sentinel emitted.
- `$`-token form (skill-creator's documented explicit token):
  `Use $zzz-probe and follow its instructions exactly.` → sentinel emitted.

When triggered, Codex reads the skill's SKILL.md body and executes its instructions. (For the probe it
ran a `sed`/`wc` to load the body then printed the sentinel; for `spec-review` the body's output contract
will drive it to append findings.)

**Copy-paste invocation template for the review loop (Tasks 3 & 4):**

```bash
codex exec -C "<REPO_ROOT>" -s workspace-write \
  "Use the spec-review skill to review the plan-w-team implementation spec at <SPEC_PATH>. Follow the skill's output contract exactly: append your per-round verdict and findings ONLY under the '## Codex Findings' section of that file, and edit nothing else in the file."
```

- `<REPO_ROOT>` = the repo/worktree root that contains `.agents/skills/spec-review/` (so the skill is
  discoverable). When `plan-w-team` already runs from the repo cwd, `-C "$(pwd)"` is the safe value.
- `<SPEC_PATH>` = path to the spec's `plan.md` (the skill should also read the sibling `decisions.md`).
- Optional: add `-o <lastmsg.txt>` to capture Codex's final message, and `-m <alias>` to override the
  model. The verdict is then read **from the file** (not stdout):
  `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' "<SPEC_PATH>"`
  (the header uses a literal em-dash `—`, U+2014).
- Reminder: the **skill's own `description`** must not contain `<` or `>` (quick_validate rejects angle
  brackets). This runtime-notes file may use them freely; the SKILL.md frontmatter may not.

---

## 4. `.skill-lock.json` Note — ABSENT. Do not create.

`.skill-lock.json` does **not** exist in the worktree repo root
(`ls .skill-lock.json` → `No such file or directory (os error 2)`). The plan/AGENTS notes assumed a
pre-existing `.skill-lock.json` to inspect — **there is none here.** Do NOT create one and do not block on
it. There is nothing to inspect, modify, or carry forward. (Codex's own skill state lives under
`~/.codex/`, e.g. `~/.codex/state_5.sqlite`, not in a repo-root lock file.)

---

## Quick reference for downstream tasks

| Need | Answer |
|------|--------|
| Skill path | `<REPO_ROOT>/.agents/skills/spec-review/SKILL.md` (repo-level, discovered) |
| Discovery works? | Yes — repo-level `.agents/skills` is auto-injected; no fallback/flag needed |
| Run-root flag | `-C "<REPO_ROOT>"` so the skill is in scope |
| Write flag | `-s workspace-write` (default already resolves to this via ancestor trust) |
| Invoke | `"Use the spec-review skill to review the plan at <SPEC_PATH> …"` (or `$spec-review`) |
| Validator | `python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" <skill_dir>` |
| `.skill-lock.json` | Absent — do not create |
