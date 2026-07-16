#!/usr/bin/env bash
# Consolidated acceptance-criteria validator for the c-suite CPO department.
#
# One check_ac<N> function per AC (AC1..AC13), mirroring the per-AC checks in
# acceptance-criteria.md "## Validation Commands" verbatim, except where
# decisions.md "## Locked Boundaries" records a user-approved amendment
# (AC7's skill validator call, AC8's per-file agent validator loop). Each
# function is independent — one AC failing never blocks another from
# running. Exits non-zero if any AC fails.
set -u

cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

# ---------------------------------------------------------------------------
# Shared helper: assert every knowledge skill's frontmatter blocks
# auto-invocation (autoInvoke: false, or the legacy disable-model-invocation:
# true fallback). Called independently from both check_ac2 and check_ac7.
# ---------------------------------------------------------------------------
skills_block_autoinvoke() {
  local fail=0
  frontmatter() { awk 'NR==1 && $0=="---"{next} /^---$/{exit} {print}' "$1"; }
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
# AC4 — cpo-prd.md: verdict-source/gate control-flow markers + mode trails.
# ---------------------------------------------------------------------------
check_ac4() {
  local fail=0
  local p=.claude/commands/c-suite/cpo-prd.md
  for marker in "Automatic rounds: 1, 2" "Verdict source: report file only" "Silence: not approval" "Round 2 options: final-delta-round | accept-with-noted-gaps | needs-human" "Round 3 options: accept-with-noted-gaps | needs-human" "<!-- prd-review-round-N -->" "Real trail: issue=existing; comments=upsert review digest; labels=needs-human only; commit=Refs #N; push=engagement branch; PR=none" "Fixture trail: issue=none; comments=none; labels=none; commit=current branch + recorded SHA; push=none; PR=none"; do
    grep -Fq "$marker" "$p" || { echo "FAIL PRD contract: $marker"; fail=1; }
  done
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

  frontmatter() { awk 'NR==1 && $0=="---"{next} /^---$/{exit} {print}' "$1"; }
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
# AC9 — prd-review skill mirrors the spec-review contract.
# ---------------------------------------------------------------------------
check_ac9() {
  local p=.agents/skills/prd-review/SKILL.md
  if head -1 "$p" >/dev/null && grep -q "Verdict: approved" "$p" && grep -q "codex-prd-review-round" "$p" && grep -q "Issue-comment digest" "$p" && grep -qi "never call" "$p"; then
    echo "PASS"
    return 0
  fi
  echo "FAIL AC9 prd-review skill contract"
  return 1
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
# Behavioral: headless negative test — a malformed slug STOPs with zero
# products/ side effects. Guarded so any stray folder is trashed, never
# rm -rf'd.
# ---------------------------------------------------------------------------
check_ac12() {
  local p=.claude/commands/c-suite/cpo-intake.md
  local fail=0

  grep -q '\^\[a-z0-9\]\[a-z0-9-\]{0,38}\[a-z0-9\]\$' "$p" || { echo "FAIL AC12 slug regex"; fail=1; }
  grep -q "_example-" "$p" || { echo "FAIL AC12 _example- fixture exception"; fail=1; }

  local before="$TMP_DIR/ac12-before.txt" after="$TMP_DIR/ac12-after.txt" outfile="$TMP_DIR/ac12-output.jsonl"
  ls products/ 2>/dev/null | sort > "$before"

  local rc=0
  timeout 180 claude -p '/c-suite:cpo-intake bad_slug!! test request' --output-format stream-json --max-turns 25 > "$outfile" 2>&1 || rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "FAIL AC12 headless invocation errored (exit $rc)"
    fail=1
  fi

  ls products/ 2>/dev/null | sort > "$after"
  local new_entries
  new_entries=$(comm -13 "$before" "$after")
  if [ -n "$new_entries" ]; then
    echo "FAIL AC12 products/ gained an entry: $new_entries"
    fail=1
    mkdir -p "$HOME/.Trash"
    while IFS= read -r entry; do
      [ -n "$entry" ] && mv "products/$entry" "$HOME/.Trash/" 2>/dev/null
    done <<< "$new_entries"
  fi

  local reply
  reply=$(jq -r 'select(.type=="result") | .result' "$outfile" 2>/dev/null)
  if printf '%s' "$reply" | grep -qi "stop" || printf '%s' "$reply" | grep -q '\[a-z0-9\]\[a-z0-9-\]'; then
    :
  else
    echo "FAIL AC12 reply missing STOP / slug-rule mention"
    fail=1
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
