#!/usr/bin/env bash
# Consolidated acceptance-criteria validator for the c-suite CPO department.
#
# One check_ac<N> function per AC (AC1..AC13), mirroring the per-AC checks in
# acceptance-criteria.md "## Validation Commands" verbatim, except where
# decisions.md "## Locked Boundaries" records a user-approved amendment. Four
# amendments are encoded here:
#   - AC7  — skill validation via the meta-skills authoring validator.
#   - AC8  — per-file agent validator loop.
#   - AC12 — zero-side-effect proof standard plus round-3 fail-closed snapshots,
#            typed NUL-safe untracked manifests, and complete reply assertions.
#   - AC4/AC9 — structural validation bar plus round-3 exact physical-line,
#            unique, bounded-section, and strict-order assertions.
# (AC13's run-log sha= is the deliverable commit per the two-commit protocol;
# the AC13 check itself is unchanged.) Each function is independent — one AC
# failing never blocks another from running. Exits non-zero if any AC fails.
set -u

cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

TMP_DIR="$(mktemp -d)"
# Safe-delete cleanup (AGENTS.md: never rm -rf). Move TMP_DIR into ~/.Trash
# under a unique name; preserve the script's exit status and surface any
# cleanup failure on stderr without changing the exit code.
cleanup() {
  local status=$?
  mkdir -p "$HOME/.Trash" 2>/dev/null || echo "cleanup: mkdir $HOME/.Trash failed" >&2
  mv "$TMP_DIR" "$HOME/.Trash/$(basename "$TMP_DIR").$$" 2>/dev/null \
    || echo "cleanup: failed to move $TMP_DIR to $HOME/.Trash" >&2
  return $status
}
trap cleanup EXIT

# Print a file's YAML frontmatter body (between the opening/closing --- lines).
frontmatter() { awk 'NR==1 && $0=="---"{next} /^---$/{exit} {print}' "$1"; }

# Print a markdown section: the "## <heading>" line (matched by prefix, so a
# trailing qualifier like "(short)" still resolves) through the line before the
# next heading of equal or higher level. Args: <file> <heading-text-without-##>.
section() {
  awk -v h="## $2" 'BEGIN{n=length(h)}
    !infl && substr($0,1,n)==h {infl=1; print; next}
    infl && /^#{1,2} / {exit}
    infl {print}
  ' "$1"
}

exact_line_count() {
  awk -v wanted="$2" '$0 == wanted {count++} END {print count+0}' "$1"
}

exact_line_number() {
  awk -v wanted="$2" '$0 == wanted {print NR}' "$1"
}

fixed_count() {
  awk -v wanted="$2" '
    BEGIN {n=length(wanted)}
    {
      rest=$0
      while (n && (at=index(rest,wanted))) {
        count++
        rest=substr(rest,at+n)
      }
    }
    END {print count+0}
  ' "$1"
}

# ---------------------------------------------------------------------------
# Shared helper: assert every knowledge skill's frontmatter blocks
# auto-invocation (autoInvoke: false, or the legacy disable-model-invocation:
# true fallback). Called independently from both check_ac2 and check_ac7.
# ---------------------------------------------------------------------------
skills_block_autoinvoke() {
  local fail=0
  for s in cpo-question-bank cpo-prd-standard cpo-design-standard; do
    p=".claude/skills/$s/SKILL.md"
    frontmatter "$p" | grep -Eq '^autoInvoke: *false$|^disable-model-invocation: *true$' || { echo "FAIL $s auto-invocation"; fail=1; }
  done
  return $fail
}

# ---------------------------------------------------------------------------
# AC1 — three stage commands: frontmatter + house sections + skill ref.
# ---------------------------------------------------------------------------
check_ac1() {
  local fail=0
  for f in cpo-intake cpo-prd cpo-brief; do
    p=".claude/commands/c-suite/$f.md"
    head -8 "$p" | grep -q "description:" || { echo "FAIL $f description"; fail=1; }
    head -8 "$p" | grep -q "argument-hint:" || { echo "FAIL $f argument-hint"; fail=1; }
    grep -q "^# " "$p" || { echo "FAIL $f purpose"; fail=1; }
    for s in "## Variables" "## Instructions" "## Workflow"; do
      grep -q "^$s" "$p" || { echo "FAIL $f $s"; fail=1; }
    done
    grep -Eq "cpo-(question-bank|prd-standard|design-standard)" "$p" || { echo "FAIL $f skill-ref"; fail=1; }
  done
  [ $fail -eq 0 ] && echo "checked"
  return $fail
}

# ---------------------------------------------------------------------------
# AC2 — single canonical prefix on the live slash_commands surface, equal to
# the recorded prefix line; plus every skill blocks auto-invocation.
# ---------------------------------------------------------------------------
check_ac2() {
  local fail=0
  local names actual rec
  names=$(claude -p 'ok' --output-format stream-json --max-turns 1 | jq -r 'select(.type=="system" and .subtype=="init") | .slash_commands[]' | grep -E "^(c-suite:)?cpo-(intake|prd|brief)$" || true)
  if [ -z "$names" ]; then
    echo "FAIL no live command names"
    fail=1
  else
    if [ "$(printf '%s\n' "$names" | sed '/^$/d' | wc -l)" -ne 3 ]; then
      echo "FAIL count"
      fail=1
    fi
    actual=$(printf '%s\n' "$names" | sed -E 's/cpo-(intake|prd|brief)$/cpo-/' | sort -u)
    if [ "$(printf '%s\n' "$actual" | sed '/^$/d' | wc -l)" -ne 1 ]; then
      echo "FAIL mixed prefixes"
      fail=1
    else
      # Reject an empty recorded canonical-prefix extraction BEFORE the
      # equality check.
      rec=$(sed -nE 's/.*Canonical command prefix: *(\/(c-suite:)?cpo-).*/\1/p' .claude/rules/c-suite/cpo-operations.md | head -1)
      if [ -z "$rec" ]; then
        echo "FAIL empty recorded prefix"
        fail=1
      elif [ "/$actual" != "$rec" ]; then
        echo "FAIL recorded-prefix mismatch"
        fail=1
      fi
    fi
  fi

  skills_block_autoinvoke || fail=1

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC3 — cpo-intake.md: resume/ingest/stale markers in order, LIVE + ASYNC.
# ---------------------------------------------------------------------------
check_ac3() {
  local fail=0
  local p=.claude/commands/c-suite/cpo-intake.md

  for marker in "Resume existing engagement" "Ingest returned answers: discovery/client-answers.md" "Late-answer transition: prd -> stale" "Late-answer transition: brief -> stale"; do
    grep -Fq "$marker" "$p" || { echo "FAIL intake control flow: $marker"; fail=1; }
  done

  if [ $fail -eq 0 ]; then
    local resume ingest prd_stale brief_stale
    resume=$(grep -nFm1 "Resume existing engagement" "$p" | cut -d: -f1)
    ingest=$(grep -nFm1 "Ingest returned answers: discovery/client-answers.md" "$p" | cut -d: -f1)
    prd_stale=$(grep -nFm1 "Late-answer transition: prd -> stale" "$p" | cut -d: -f1)
    brief_stale=$(grep -nFm1 "Late-answer transition: brief -> stale" "$p" | cut -d: -f1)
    if ! { [ "$resume" -lt "$ingest" ] && [ "$ingest" -lt "$prd_stale" ] && [ "$ingest" -lt "$brief_stale" ]; }; then
      echo "FAIL intake transition order"
      fail=1
    fi
  fi

  if ! { grep -q "LIVE" "$p" && grep -q "ASYNC" "$p" && grep -qi "send-to-client" "$p"; }; then
    echo "FAIL intake modes"
    fail=1
  fi

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC4 — cpo-prd.md gate contract, section-scoped + order-aware (Locked
# Boundaries: AC4/AC9 structural validation bar). The "## Gate contract"
# section must carry every review-input/output and gate-transition line, in
# order; plus the digest key + trail lines, and prd-gate persistence
# (status.md) and consumption (cpo-brief.md).
# ---------------------------------------------------------------------------
check_ac4() {
  local fail=0
  local p=.claude/commands/c-suite/cpo-prd.md

  # (a) Every canonical Gate-contract physical line occurs exactly once in the
  # file, exactly once in its bounded section, and in strict source order.
  local sec="$TMP_DIR/ac4-gate-contract.txt"
  if ! section "$p" "Gate contract" > "$sec"; then
    echo "FAIL AC4 Gate contract section extraction"
    fail=1
  elif [ ! -s "$sec" ]; then
    echo "FAIL AC4 Gate contract section missing"
    fail=1
  else
    local gate_lines=(
      '`Review input: quoted engagement folder products/<client-slug>/ + round N`'
      '`Verdict source: report file only`'
      '`Silence: not approval`'
      '`Missing verdict: re-run the same round`'
      '`Automatic rounds: 1, 2`'
      '`Round 1: approved -> exit | changes-requested -> PM fix pass -> round 2`'
      '`Round 2: approved -> exit | changes-requested -> over-cap gate`'
      '`Round 2 options: final-delta-round | accept-with-noted-gaps | needs-human`'
      '`Round 3: final — no further round`'
      '`Round 3 options: accept-with-noted-gaps | needs-human`'
      '`Gate ledger: prd-gate=<approved | accepted-with-noted-gaps | needs-human>; gaps under ## PRD gate gaps; reset to none on review restart or stale PRD`'
    )
    local prev=0 ln l file_count section_count
    for l in "${gate_lines[@]}"; do
      file_count=$(exact_line_count "$p" "$l")
      section_count=$(exact_line_count "$sec" "$l")
      if [ "$file_count" -ne 1 ] || [ "$section_count" -ne 1 ]; then
        echo "FAIL AC4 Gate contract exact cardinality/placement: $l"
        fail=1
      else
        ln=$(exact_line_number "$sec" "$l")
        if [ "$ln" -le "$prev" ]; then
          echo "FAIL AC4 Gate contract out of order: $l"
          fail=1
        else
          prev="$ln"
        fi
      fi
    done
  fi

  # (b) Digest key and canonical Trail-contract physical lines.
  local contract_lines=(
    '     engagement-issue comment keyed `<!-- prd-review-round-N -->` — list the issue'"'"'s'
    '`Real trail: issue=existing; comments=upsert review digest; labels=needs-human only; commit=Refs #N; push=engagement branch; PR=none`'
    '`Fixture trail: issue=none; comments=none; labels=none; commit=current branch + recorded SHA; push=none; PR=none`'
  )
  local marker
  for marker in "${contract_lines[@]}"; do
    if [ "$(exact_line_count "$p" "$marker")" -ne 1 ]; then
      echo "FAIL AC4 exact canonical line: $marker"
      fail=1
    fi
  done

  # (c) prd-gate persistence (status template) + consumption (cpo-brief), each
  # asserted as an exact physical line with file-wide cardinality one.
  local status_t=.claude/skills/cpo-question-bank/templates/status.md
  local status_gate='prd-gate: <none | approved | accepted-with-noted-gaps | needs-human>'
  local gaps_heading='## PRD gate gaps'
  local brief_line='  `Brief preflight: prd: done AND (prd-gate=approved + approved verdict report | prd-gate=accepted-with-noted-gaps); none/needs-human never pass`'
  [ "$(exact_line_count "$status_t" "$status_gate")" -eq 1 ] \
    || { echo "FAIL AC4 status.md exact prd-gate line"; fail=1; }
  [ "$(exact_line_count "$status_t" "$gaps_heading")" -eq 1 ] \
    || { echo "FAIL AC4 status.md exact PRD gate gaps heading"; fail=1; }
  [ "$(exact_line_count .claude/commands/c-suite/cpo-brief.md "$brief_line")" -eq 1 ] \
    || { echo "FAIL AC4 cpo-brief exact preflight line"; fail=1; }

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC5 — nine engagement templates + status template's exact contract lines.
# ---------------------------------------------------------------------------
check_ac5() {
  local fail=0
  for t in cpo-question-bank/templates/question-list.md cpo-question-bank/templates/requirements.md cpo-question-bank/templates/status.md cpo-prd-standard/templates/prd.md cpo-design-standard/templates/project-brief.md cpo-design-standard/templates/sitemap-and-flows.md cpo-design-standard/templates/section-briefs.md cpo-design-standard/templates/copy-deck.md cpo-design-standard/templates/brand-inputs.md; do
    test -f ".claude/skills/$t" || { echo "FAIL $t"; fail=1; }
  done

  local p=.claude/skills/cpo-question-bank/templates/status.md
  for marker in "mode:" "issue:" "branch:" "hosting-branch:" "PR:" "intake: <state>" "prd: <state>" "brief: <state>" "intake-run: date=<date>; sha=<sha>; lessons=<result>" "prd-run: date=<date>; sha=<sha>; lessons=<result>" "brief-run: date=<date>; sha=<sha>; lessons=<result>"; do
    grep -Fq "$marker" "$p" || { echo "FAIL status contract: $marker"; fail=1; }
  done

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC6 — three rules files: paths: frontmatter + exact roster rows.
# ---------------------------------------------------------------------------
check_ac6() {
  local fail=0
  for r in roster cpo-operations cpo-lessons; do
    head -5 ".claude/rules/c-suite/$r.md" | grep -q "paths:" || { echo "FAIL $r paths"; fail=1; }
  done

  local p=.claude/rules/c-suite/roster.md
  for row in '^\| *CPO *\| *Sofia Reyes *\| *AI *\| *session *\|' '^\| *PM *\| *Ethan Park *\| *AI *\| *opus *\|' '^\| *UX Researcher *\| *Priya Nair *\| *AI *\| *sonnet *\|' '^\| *UX Designer *\| *Jonas Weber *\| *AI *\| *sonnet *\|' '^\| *UI Designer *\| *Yuki Tanaka *\| *AI *\| *sonnet *\|' '^\| *Design Lead *\| *Daniel Osei *\| *AI *\| *opus *\|' '^\| *Prototype Owner *\| *Human *\| *human *\| *n/a *\|'; do
    grep -Eiq "$row" "$p" || { echo "FAIL roster mapping: $row"; fail=1; }
  done

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC7 — knowledge skills pass validation + block auto-invocation.
#
# Locked Boundaries amendment (decisions.md, user-approved 2026-07-17):
# validate each skill with the meta-skills authoring validator
# (uv run --with pyyaml python .../validate.py <SKILL.md>, one call per
# skill; exit 0 = pass; the WARN about the autoInvoke key is non-fatal) —
# NOT quick_validate.py, whose packaging allow-list rejects every
# auto-invocation-blocking frontmatter key. The auto-invocation grep is kept
# exactly as written in acceptance-criteria.md.
# ---------------------------------------------------------------------------
check_ac7() {
  local fail=0
  for s in cpo-question-bank cpo-prd-standard cpo-design-standard; do
    local log="$TMP_DIR/ac7-$s.log"
    if ! uv run --with pyyaml python .claude/skills/meta-skills/scripts/validate.py ".claude/skills/$s/SKILL.md" >"$log" 2>&1; then
      echo "FAIL $s meta-skills validate.py"
      cat "$log"
      fail=1
    fi
  done

  skills_block_autoinvoke || fail=1

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC8 — five persona agents pass validation, no AskUserQuestion, exact
# skill/model mappings, and every command's required SKILL.md + template
# paths.
#
# Locked Boundaries amendment (decisions.md, user-approved 2026-07-17):
# validate agents with a per-file loop (uv run --with pyyaml python
# .../validate_agent.py <path>, one call per file) — NOT the glob
# single-call. The rest of AC8's checks (AskUserQuestion absence, per-agent
# frontmatter mappings, require_path greps) are kept exactly as written.
# ---------------------------------------------------------------------------
check_ac8() {
  local fail=0

  for f in .claude/agents/cpo/*.md; do
    local log="$TMP_DIR/ac8-validate-$(basename "$f").log"
    if ! uv run --with pyyaml python .claude/skills/meta-agent/scripts/validate_agent.py "$f" >"$log" 2>&1; then
      echo "FAIL agent validate: $f"
      cat "$log"
      fail=1
    fi
  done

  if grep -l "AskUserQuestion" .claude/agents/cpo/*.md >/dev/null 2>&1; then
    echo "FAIL AskUserQuestion present in an agent file"
    fail=1
  fi

  check_agent() {
    local p=".claude/agents/cpo/$1.md" actual
    actual=$(frontmatter "$p" | grep -oE 'cpo-(question-bank|prd-standard|design-standard)' | sort -u | paste -sd, -)
    if [ "$actual" != "$2" ]; then
      echo "FAIL $1 skills: $actual"
      return 1
    fi
    if ! frontmatter "$p" | grep -Eq "^model: *$3$"; then
      echo "FAIL $1 model"
      return 1
    fi
    return 0
  }
  check_agent cpo-pm cpo-design-standard,cpo-prd-standard opus || fail=1
  check_agent cpo-ux-researcher cpo-question-bank sonnet || fail=1
  check_agent cpo-ux-designer cpo-design-standard sonnet || fail=1
  check_agent cpo-ui-designer cpo-design-standard sonnet || fail=1
  check_agent cpo-design-lead cpo-design-standard opus || fail=1

  local prefix='${CLAUDE_PROJECT_DIR}/.claude/skills'
  require_path() {
    grep -Fq "$prefix/$2" ".claude/commands/c-suite/$1.md" || { echo "FAIL $1 path $2"; return 1; }
    return 0
  }
  require_path cpo-intake cpo-question-bank/SKILL.md || fail=1
  for t in question-list requirements status; do
    require_path cpo-intake "cpo-question-bank/templates/$t.md" || fail=1
  done
  require_path cpo-prd cpo-prd-standard/SKILL.md || fail=1
  require_path cpo-prd cpo-prd-standard/templates/prd.md || fail=1
  require_path cpo-brief cpo-design-standard/SKILL.md || fail=1
  for t in project-brief sitemap-and-flows section-briefs copy-deck brand-inputs; do
    require_path cpo-brief "cpo-design-standard/templates/$t.md" || fail=1
  done

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC9 — prd-review skill contract, section-scoped structural assertion (Locked
# Boundaries: AC4/AC9 structural validation bar). Every review input/output
# line is asserted exactly, in its own section where the brief scopes it.
# ---------------------------------------------------------------------------
check_ac9() {
  local fail=0
  local p=.agents/skills/prd-review/SKILL.md

  local inputs="$TMP_DIR/ac9-inputs.txt"
  local output="$TMP_DIR/ac9-output-contract.txt"
  local ret="$TMP_DIR/ac9-return.txt"
  local never="$TMP_DIR/ac9-never-touch.txt"
  local named_sections=(
    "Inputs:$inputs"
    "Output contract:$output"
    "Return to the caller:$ret"
    "Never touch:$never"
  )
  local item heading target
  for item in "${named_sections[@]}"; do
    heading=${item%%:*}
    target=${item#*:}
    if ! section "$p" "$heading" > "$target"; then
      echo "FAIL AC9 section extraction: $heading"
      fail=1
    elif [ ! -s "$target" ]; then
      echo "FAIL AC9 section missing: $heading"
      fail=1
    fi
  done

  # Exact Output-contract physical lines, each unique within its owner.
  local output_lines=(
    'Write your verdict to `products/<client-slug>/prd/reviews/codex-prd-review-round-N.md`,'
    '- `### Round N — Verdict: approved`'
    '- `### Round N — Verdict: changes-requested`'
  )
  local line output_ln output_prev=0
  for line in "${output_lines[@]}"; do
    if [ "$(exact_line_count "$output" "$line")" -ne 1 ]; then
      echo "FAIL AC9 Output contract exact cardinality: $line"
      fail=1
    else
      output_ln=$(exact_line_number "$output" "$line")
      if [ "$output_ln" -le "$output_prev" ]; then
        echo "FAIL AC9 Output contract order: $line"
        fail=1
      else
        output_prev="$output_ln"
      fi
    fi
  done

  # Inputs caller contract: both canonical physical lines occur exactly once
  # inside the bounded Inputs section, in strict canonical order (the injects
  # line before the round-number line).
  local input_lines=(
    'The caller injects both the **engagement folder path** (`products/<client-slug>/`) and the'
    '**round number N** — use both verbatim, never infer either.'
  )
  local input_line input_ln input_prev=0
  for input_line in "${input_lines[@]}"; do
    if [ "$(exact_line_count "$inputs" "$input_line")" -ne 1 ]; then
      echo "FAIL AC9 Inputs caller contract exact cardinality: $input_line"
      fail=1
    else
      input_ln=$(exact_line_number "$inputs" "$input_line")
      if [ "$input_ln" -le "$input_prev" ]; then
        echo "FAIL AC9 Inputs caller contract order: $input_line"
        fail=1
      else
        input_prev="$input_ln"
      fi
    fi
  done

  # Return contract: both exact physical lines are unique and strictly ordered;
  # their required fragments must also be unique within the bounded section.
  local return_line_1='- **Line 1** — the verdict line, verbatim.'
  local return_line_2='- **Line 2** — a one-line count + the report path, e.g. `2 blocking findings — products/<client-slug>/prd/reviews/codex-prd-review-round-2.md` or `no blocking findings — products/<client-slug>/prd/reviews/codex-prd-review-round-1.md`.'
  local return_1_ln return_2_ln frag
  for frag in '**Line 1**' '**Line 2**' 'verdict line, verbatim'; do
    if [ "$(fixed_count "$ret" "$frag")" -ne 1 ]; then
      echo "FAIL AC9 Return unique fragment: $frag"
      fail=1
    fi
  done
  if [ "$(exact_line_count "$ret" "$return_line_1")" -ne 1 ]; then
    echo "FAIL AC9 Return exact Line 1 contract"
    fail=1
  else
    return_1_ln=$(exact_line_number "$ret" "$return_line_1")
  fi
  if [ "$(exact_line_count "$ret" "$return_line_2")" -ne 1 ]; then
    echo "FAIL AC9 Return exact Line 2 contract"
    fail=1
  else
    return_2_ln=$(exact_line_number "$ret" "$return_line_2")
  fi
  if [ -n "${return_1_ln:-}" ] && [ -n "${return_2_ln:-}" ] && [ "$return_1_ln" -ge "$return_2_ln" ]; then
    echo "FAIL AC9 Return contract order"
    fail=1
  fi

  # Preserve the digest and never-call-gh assertions as exact owner lines.
  local digest_line='- **Issue-comment digest (final element of the report).** End with `**Issue-comment digest:**` followed by exactly one short paragraph: the round number, verdict, blocking-finding count + headline issues, and the next action. Draw only on this round'"'"'s findings — add no new claim or recommendation. The orchestrator posts it verbatim to the issue thread; you still never call `gh`.'
  local never_line='- Never call `gh` — the orchestrator relays every verdict.'
  [ "$(exact_line_count "$output" "$digest_line")" -eq 1 ] \
    || { echo "FAIL AC9 exact issue-comment digest contract"; fail=1; }
  [ "$(exact_line_count "$never" "$never_line")" -eq 1 ] \
    || { echo "FAIL AC9 exact never-call-gh contract"; fail=1; }

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC10 — AGENTS.md documents products/ and the c-suite pipeline.
# ---------------------------------------------------------------------------
check_ac10() {
  if grep -q "products/" AGENTS.md && grep -q "c-suite" AGENTS.md; then
    echo "PASS"
    return 0
  fi
  echo "FAIL AC10 AGENTS.md hub pointers"
  return 1
}

# ---------------------------------------------------------------------------
# AC11 — the Bluebird Bakery fixture is complete: locked dimensions, PRD +
# approved review, six design files, wireframes with no external URL, and
# the ledger's done/handed-off state lines.
# ---------------------------------------------------------------------------
check_ac11() {
  local d=products/_example-bluebird-bakery
  local req="$d/discovery/requirements.md"
  local fail=0

  if [ ! -f "$req" ]; then
    echo "FAIL requirements"
    return 1
  fi

  for dim in "business & goals" "audience & users" "brand & voice" "content & assets" "structure & pages" "features & functionality" "integrations & data" "technical & hosting constraints" "budget & timeline" "success metrics" "references & competitors" "legal/compliance"; do
    if [ "$(grep -Fxc -- "- $dim: locked" "$req")" -ne 1 ]; then
      echo "FAIL locked dimension: $dim"
      fail=1
    fi
  done

  if [ ! -f "$d/prd/prd.md" ] || ! grep -q "Verdict: approved" "$d"/prd/reviews/*.md 2>/dev/null; then
    echo "FAIL approved PRD"
    fail=1
  fi

  for x in project-brief sitemap-and-flows section-briefs copy-deck brand-inputs; do
    test -f "$d/design/$x.md" || { echo "FAIL $x"; fail=1; }
  done

  ls "$d"/design/wireframes/*.html >/dev/null 2>&1 || { echo "FAIL wireframes"; fail=1; }

  if grep -rEq "https?://" "$d/design/wireframes" 2>/dev/null; then
    echo "FAIL external-url"
    fail=1
  fi

  for s in "intake: done" "prd: done" "brief: done" "engagement: handed-off"; do
    grep -Fqx "$s" "$d/status.md" || { echo "FAIL state $s"; fail=1; }
  done

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC12 — structural: slug regex + _example- exception in cpo-intake.md.
# Behavioral (Locked Boundaries: AC12 zero-side-effect proof standard): a
# malformed slug STOPs with zero side effects. Prove it by exact before/after
# equality of every in-scope mutable surface — repo-wide git status, tracked
# index/worktree content (binary diff vs HEAD), an untracked path/type/digest
# manifest, all refs, and the worktree list — plus PATH-prepended gh/codex
# fail-stubs whose invocation logs must stay empty. Every capture and comparison
# fails closed. The reply must contain standalone STOP, the complete slug rule,
# AND the offending value. Top-level products/ listing and a
# checked quarantine (never rm -rf'd) remain additional safeguards.
# ---------------------------------------------------------------------------
check_ac12() {
  local p=.claude/commands/c-suite/cpo-intake.md
  local fail=0

  grep -q '\^\[a-z0-9\]\[a-z0-9-\]{0,38}\[a-z0-9\]\$' "$p" || { echo "FAIL AC12 slug regex"; fail=1; }
  grep -q "_example-" "$p" || { echo "FAIL AC12 _example- fixture exception"; fail=1; }

  snapshot_capture_error() {
    echo "FAIL AC12 snapshot capture: $1"
    if [ -f "$2" ] && [ -s "$2" ]; then
      cat "$2" >&2
    fi
    return 1
  }

  capture_untracked_manifest() {
    local pfx="$1"
    local raw="$pfx-untracked-raw.zlist"
    local sorted="$pfx-untracked-sorted.zlist"
    local manifest="$pfx-untracked.bin"
    local err="$pfx-untracked.err"
    local hash_out="$pfx-untracked-hash.txt"
    local target_z="$pfx-untracked-target.z"
    local target_raw="$pfx-untracked-target.raw"
    local path file_type digest target rest

    if ! git ls-files --others --exclude-standard -z > "$raw" 2> "$err"; then
      snapshot_capture_error "untracked manifest" "$err"
      return 1
    fi
    if ! LC_ALL=C sort -z "$raw" > "$sorted" 2> "$err"; then
      snapshot_capture_error "untracked manifest" "$err"
      return 1
    fi
    if ! : > "$manifest"; then
      snapshot_capture_error "untracked manifest" "$err"
      return 1
    fi

    while IFS= read -r -d '' path; do
      if ! file_type=$(LC_ALL=C stat --printf='%F' -- "$path" 2> "$err"); then
        snapshot_capture_error "untracked manifest" "$err"
        return 1
      fi

      case "$file_type" in
        "regular file")
          if [ -L "$path" ] || ! sha256sum -- "$path" > "$hash_out" 2> "$err"; then
            snapshot_capture_error "untracked manifest" "$err"
            return 1
          fi
          if ! IFS=' ' read -r digest rest < "$hash_out" || ! grep -Eq '^[0-9a-f]{64}  ' "$hash_out"; then
            printf 'invalid regular-file digest for %s\n' "$path" > "$err"
            snapshot_capture_error "untracked manifest" "$err"
            return 1
          fi
          digest="content:$digest"
          ;;
        "symbolic link")
          if ! readlink -z -- "$path" > "$target_z" 2> "$err"; then
            snapshot_capture_error "untracked manifest" "$err"
            return 1
          fi
          target=
          if ! IFS= read -r -d '' target < "$target_z"; then
            printf 'unterminated readlink target for %s\n' "$path" > "$err"
            snapshot_capture_error "untracked manifest" "$err"
            return 1
          fi
          if ! printf '%s' "$target" > "$target_raw"; then
            snapshot_capture_error "untracked manifest" "$err"
            return 1
          fi
          if ! sha256sum -- "$target_raw" > "$hash_out" 2> "$err"; then
            snapshot_capture_error "untracked manifest" "$err"
            return 1
          fi
          if ! IFS=' ' read -r digest rest < "$hash_out" || ! grep -Eq '^[0-9a-f]{64}  ' "$hash_out"; then
            printf 'invalid symlink-target digest for %s\n' "$path" > "$err"
            snapshot_capture_error "untracked manifest" "$err"
            return 1
          fi
          digest="target:$digest"
          ;;
        directory)
          digest="type:directory"
          ;;
        *)
          digest="type:$file_type"
          ;;
      esac

      if ! printf '%s\0%s\0%s\0' "$path" "$file_type" "$digest" >> "$manifest"; then
        snapshot_capture_error "untracked manifest" "$err"
        return 1
      fi
    done < "$sorted"
    return 0
  }

  # Snapshot every in-scope mutable surface to files prefixed by $1.
  snapshot_state() {
    local pfx="$1"
    local capture_fail=0
    local err="$pfx-status.err"

    git status --porcelain=v1 --untracked-files=all > "$pfx-status.txt" 2> "$err" \
      || { snapshot_capture_error "git status" "$err"; capture_fail=1; }
    err="$pfx-diff.err"
    git diff HEAD --binary > "$pfx-diff.bin" 2> "$err" \
      || { snapshot_capture_error "tracked diff" "$err"; capture_fail=1; }
    err="$pfx-refs.err"
    git for-each-ref > "$pfx-refs.txt" 2> "$err" \
      || { snapshot_capture_error "refs" "$err"; capture_fail=1; }
    err="$pfx-worktrees.err"
    git worktree list --porcelain > "$pfx-worktrees.txt" 2> "$err" \
      || { snapshot_capture_error "worktree list" "$err"; capture_fail=1; }
    capture_untracked_manifest "$pfx" || capture_fail=1
    return $capture_fail
  }

  # Fail-stubs: any gh/codex call during the negative run logs its invocation.
  local shim="$TMP_DIR/ac12-shim"
  local gh_log="$TMP_DIR/ac12-gh.log" codex_log="$TMP_DIR/ac12-codex.log"
  local can_run=1
  mkdir -p "$shim" || { echo "FAIL AC12 shim setup: mkdir"; fail=1; can_run=0; }
  if ! cat > "$shim/gh" <<EOF
#!/usr/bin/env bash
printf '%s %s\n' "\$0" "\$*" >> "$gh_log"
exit 1
EOF
  then
    echo "FAIL AC12 shim setup: gh"
    fail=1
    can_run=0
  fi
  if ! cat > "$shim/codex" <<EOF
#!/usr/bin/env bash
printf '%s %s\n' "\$0" "\$*" >> "$codex_log"
exit 1
EOF
  then
    echo "FAIL AC12 shim setup: codex"
    fail=1
    can_run=0
  fi
  chmod +x "$shim/gh" "$shim/codex" || { echo "FAIL AC12 shim setup: chmod"; fail=1; can_run=0; }

  local before="$TMP_DIR/ac12-before" after="$TMP_DIR/ac12-after"
  local outfile="$TMP_DIR/ac12-output.jsonl"
  local products_before="$TMP_DIR/ac12-products-before.txt"
  local products_after="$TMP_DIR/ac12-products-after.txt"

  local snapshots_ready=1
  snapshot_state "$before" || { fail=1; snapshots_ready=0; }
  local products_raw="$TMP_DIR/ac12-products-before.raw"
  local products_err="$TMP_DIR/ac12-products-before.err"
  if ! ls products/ > "$products_raw" 2> "$products_err"; then
    snapshot_capture_error "products listing" "$products_err"
    fail=1
    snapshots_ready=0
  elif ! LC_ALL=C sort "$products_raw" > "$products_before" 2> "$products_err"; then
    snapshot_capture_error "products listing" "$products_err"
    fail=1
    snapshots_ready=0
  fi

  local rc=0
  if [ "$snapshots_ready" -eq 1 ] && [ "$can_run" -eq 1 ]; then
    PATH="$shim:$PATH" timeout 180 claude -p '/c-suite:cpo-intake bad_slug!! test request' --output-format stream-json --max-turns 25 > "$outfile" 2>&1 || rc=$?
    if [ "$rc" -ne 0 ]; then
      echo "FAIL AC12 headless invocation errored (exit $rc)"
      fail=1
    fi
  else
    echo "FAIL AC12 headless invocation skipped: incomplete before evidence"
    fail=1
  fi

  local after_ready=1
  snapshot_state "$after" || { fail=1; after_ready=0; }
  products_raw="$TMP_DIR/ac12-products-after.raw"
  products_err="$TMP_DIR/ac12-products-after.err"
  if ! ls products/ > "$products_raw" 2> "$products_err"; then
    snapshot_capture_error "products listing" "$products_err"
    fail=1
    after_ready=0
  elif ! LC_ALL=C sort "$products_raw" > "$products_after" 2> "$products_err"; then
    snapshot_capture_error "products listing" "$products_err"
    fail=1
    after_ready=0
  fi

  # Compare every snapshotted surface; name each that differs.
  compare_surface() {
    local cmp_out="$TMP_DIR/ac12-compare.out"
    local cmp_err="$TMP_DIR/ac12-compare.err"
    local cmp_rc=0
    cmp "$2" "$3" > "$cmp_out" 2> "$cmp_err" || cmp_rc=$?
    if [ "$cmp_rc" -eq 1 ]; then
      echo "FAIL AC12 side effect: $1 differs before/after"
      return 1
    elif [ "$cmp_rc" -ne 0 ]; then
      echo "FAIL AC12 snapshot comparison: $1"
      [ -s "$cmp_err" ] && cat "$cmp_err" >&2
      return 1
    fi
    return 0
  }
  if [ "$snapshots_ready" -eq 1 ] && [ "$after_ready" -eq 1 ]; then
    compare_surface "git status" "$before-status.txt" "$after-status.txt" || fail=1
    compare_surface "tracked diff (git diff HEAD --binary)" "$before-diff.bin" "$after-diff.bin" || fail=1
    compare_surface "refs (git for-each-ref)" "$before-refs.txt" "$after-refs.txt" || fail=1
    compare_surface "worktree list" "$before-worktrees.txt" "$after-worktrees.txt" || fail=1
    compare_surface "untracked manifest" "$before-untracked.bin" "$after-untracked.bin" || fail=1
    compare_surface "products listing" "$products_before" "$products_after" || fail=1
  fi

  # Additional safeguard: top-level products/ listing + checked quarantine.
  local new_entries
  local comm_err="$TMP_DIR/ac12-products-comm.err"
  if [ "$snapshots_ready" -eq 1 ] && [ "$after_ready" -eq 1 ] && ! new_entries=$(comm -13 "$products_before" "$products_after" 2> "$comm_err"); then
    echo "FAIL AC12 snapshot comparison: products entries"
    [ -s "$comm_err" ] && cat "$comm_err" >&2
    fail=1
  elif [ -n "${new_entries:-}" ]; then
    echo "FAIL AC12 products/ gained an entry: $new_entries"
    fail=1
    if ! mkdir -p "$HOME/.Trash"; then
      echo "FAIL AC12 quarantine: mkdir $HOME/.Trash failed"
    else
      while IFS= read -r entry; do
        [ -z "$entry" ] && continue
        if ! mv "products/$entry" "$HOME/.Trash/"; then
          echo "FAIL AC12 quarantine: products/$entry -> $HOME/.Trash/ failed"
        fi
      done <<< "$new_entries"
    fi
  fi

  # No gh/codex may have been invoked.
  if [ -s "$gh_log" ]; then
    echo "FAIL AC12 gh invoked during negative test:"; cat "$gh_log"
    fail=1
  fi
  if [ -s "$codex_log" ]; then
    echo "FAIL AC12 codex invoked during negative test:"; cat "$codex_log"
    fail=1
  fi

  # Reply must contain STOP AND the slug rule AND the offending value.
  local reply_file="$TMP_DIR/ac12-reply.txt"
  local reply_err="$TMP_DIR/ac12-reply.err"
  if ! jq -r 'select(.type=="result") | .result' "$outfile" > "$reply_file" 2> "$reply_err"; then
    echo "FAIL AC12 reply extraction"
    [ -s "$reply_err" ] && cat "$reply_err" >&2
    fail=1
  else
    grep -Eqi '(^|[^[:alnum:]_])stop([^[:alnum:]_]|$)' "$reply_file" \
      || { echo "FAIL AC12 reply missing standalone STOP"; fail=1; }
    grep -Fq -- '^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$' "$reply_file" \
      || { echo "FAIL AC12 reply missing complete slug rule"; fail=1; }
    grep -Fq -- 'bad_slug!!' "$reply_file" \
      || { echo "FAIL AC12 reply missing offending value bad_slug!!"; fail=1; }
  fi

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# AC13 — fixture ledger proves the fixture-mode trail: exact mode/issue/
# branch/PR lines, a non-empty hosting branch, per-stage run-log lines each
# with a non-empty SHA reachable from that branch and a lessons result, plus
# all six real/fixture trail-contract lines across the three commands.
# ---------------------------------------------------------------------------
check_ac13() {
  local d=products/_example-bluebird-bakery
  local p="$d/status.md"
  local fail=0

  for marker in "mode: fixture" "issue: none" "branch: none" "PR: none"; do
    grep -Fqx "$marker" "$p" || { echo "FAIL fixture field: $marker"; fail=1; }
  done

  local branch
  branch=$(sed -n 's/^hosting-branch: //p' "$p" | head -1)
  if [ -z "$branch" ] || [ "$branch" = none ] || ! git show-ref --verify --quiet "refs/heads/$branch"; then
    echo "FAIL hosting branch"
    fail=1
  else
    for stage in intake prd brief; do
      local line sha
      line=$(grep -E "^${stage}-run: date=[^;]+; sha=[0-9a-f]{7,40}; lessons=.+$" "$p" | tail -1)
      if [ -z "$line" ]; then
        echo "FAIL $stage run log"
        fail=1
        continue
      fi
      sha=$(printf '%s\n' "$line" | sed -nE 's/.*; sha=([0-9a-f]{7,40});.*/\1/p')
      if [ -z "$sha" ]; then
        echo "FAIL $stage empty SHA"
        fail=1
        continue
      fi
      git merge-base --is-ancestor "$sha" "$branch" || { echo "FAIL $stage SHA not reachable from $branch"; fail=1; }
    done
  fi

  local fixture='Fixture trail: issue=none; comments=none; labels=none; commit=current branch + recorded SHA; push=none; PR=none'
  for f in cpo-intake cpo-prd cpo-brief; do
    grep -Fq "$fixture" ".claude/commands/c-suite/$f.md" || { echo "FAIL $f fixture trail"; fail=1; }
  done

  grep -Fq 'Real trail: issue=create; comments=none; labels=none; commit=Refs #N; push=engagement branch; PR=none' .claude/commands/c-suite/cpo-intake.md || { echo "FAIL intake real trail"; fail=1; }
  grep -Fq 'Real trail: issue=existing; comments=upsert review digest; labels=needs-human only; commit=Refs #N; push=engagement branch; PR=none' .claude/commands/c-suite/cpo-prd.md || { echo "FAIL prd real trail"; fail=1; }
  grep -Fq 'Real trail: issue=existing; comments=none; labels=none; commit=Refs #N; push=engagement branch; PR=open once' .claude/commands/c-suite/cpo-brief.md || { echo "FAIL brief real trail"; fail=1; }

  [ $fail -eq 0 ] && echo "PASS"
  return $fail
}

# ---------------------------------------------------------------------------
# Run every check, print a per-AC summary, exit non-zero on any failure.
# ---------------------------------------------------------------------------
AC_IDS=(1 2 3 4 5 6 7 8 9 10 11 12 13)
declare -A AC_RESULT
overall_fail=0

for n in "${AC_IDS[@]}"; do
  echo "=== AC${n} ==="
  if "check_ac${n}"; then
    AC_RESULT[$n]="PASS"
  else
    AC_RESULT[$n]="FAIL"
    overall_fail=1
  fi
  echo
done

echo "=== Summary ==="
for n in "${AC_IDS[@]}"; do
  printf 'AC%-3s %s\n' "$n" "${AC_RESULT[$n]}"
done

exit $overall_fail
