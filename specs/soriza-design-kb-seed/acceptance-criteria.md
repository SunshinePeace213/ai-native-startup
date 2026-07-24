# Acceptance Criteria: Seed the design KB group + worktree availability (child #44 of epic #43)

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here. Epic traceability: AC1
> realizes epic AC2's pre-merge half; AC2–AC5 realize epic AC3; AC6 keeps the PR surface
> exact. Epic AC2's worktree-receives-mirrors half is verified by the epic's own
> `validate-all` after the post-merge hydration.

## Acceptance Criteria

- **AC1** — `.worktreeinclude` contains the single pattern line `ai-docs/*` with one comment
  line directly above it; the pre-existing lines are unchanged. Under the WorktreeCreate
  hook's exact matching semantics (`fnmatch` of each pattern against the relative path or
  basename of every untracked-and-ignored file), the pattern matches every `ai-docs/` file
  reported by `git ls-files -oi --exclude-standard` in this worktree.
- **AC2** — `ai-docs/sources.yaml` carries a `design` group with exactly five entries
  matching the spec's identity table (one w3.org, one web.dev/learn/design, exactly two
  `nngroup.com/articles/` with one containing `homepage`, one fonts.google.com/knowledge) —
  each with a canonical `url`, a `file` under `design/`, and a non-null `fetched` date, and
  each mirror file existing on disk with frontmatter (`source:` matching the manifest url,
  `fetched:` matching the manifest date) and a `> **In here:**` line. Provenance is
  observable: decisions.md's `### Build addendum — kb run record` carries exactly one
  `- OK <file> <canonical url>` line per registered source. The only permitted identity
  deviation is the WCAG quickref swapped to the locked fallback
  `https://www.w3.org/TR/WCAG22/`, carried by a FAIL/swap line naming the original URL
  (the failed provisional entry is deleted from the manifest first, so the group still
  holds exactly five fully-fetched entries); the web.dev, fonts.google.com, and NN/g
  identities are unconditional — their fetch failure is a build stop, never a swap. A
  mirror without its OK record, a WCAG deviation without its swap line, or any other
  identity deviation — fails.
- **AC3** — The `anthropic` group carries exactly one entry whose url contains
  `code.claude.com/docs/en/memory`, with a `file` under `anthropic/`, a non-null `fetched`
  date, and its mirror on disk with matching frontmatter.
- **AC4** — `ai-docs/index.md` exists in this worktree and lists all six new files (the five
  `design/` mirrors and the memory mirror).
- **AC5** — Manifest hygiene: total entry count ≤ 40 (expected 32) and no two entries share
  a canonical url.
- **AC6** — The change surface vs `origin/main` outside `specs/` — measured against the
  working tree, so the check passes identically before or after the build's commit — is
  exactly `.worktreeinclude` and `ai-docs/sources.yaml`, with no stray untracked non-ignored
  files; git tracks nothing else under `ai-docs/` (mirrors and `ai-docs/index.md` remain
  gitignored, never force-added).

## Validation Commands

Run these to prove the criteria above — from the worktree root
(`/Users/ringo/Desktop/ai-native-startup/.claude/worktrees/soriza-design-kb-seed`), after the
build tasks complete. Assertion scripts exit non-zero on any failure. The yaml-parsing
scripts carry their dependency inline (`uv run --with pyyaml`) — the project env has no
PyYAML; the stdlib-only scripts run with plain `uv run python`.

- `uv run python -c "
  from pathlib import Path
  import subprocess
  lines = Path('.worktreeinclude').read_text().splitlines()
  idx = [i for i, l in enumerate(lines) if l.strip() == 'ai-docs/*']
  assert len(idx) == 1, 'expected exactly one ai-docs/* line, got %d' % len(idx)
  i = idx[0]
  assert i > 0 and lines[i-1].strip().startswith('#'), 'no comment line directly above ai-docs/*'
  baseline = subprocess.run(['git','show','origin/main:.worktreeinclude'],
                            capture_output=True, text=True, check=True).stdout.splitlines()
  rest = lines[:i-1] + lines[i+1:]
  assert rest == baseline, 'pre-existing lines changed: %r != baseline %r' % (rest, baseline)
  print('AC1 ok: one pattern, comment above, baseline preserved')"` — verifies AC1 (exactly
  one `ai-docs/*` line, a comment directly above it, and every other line byte-equal to the
  `origin/main` baseline — duplicates, edits, or extra patterns all fail).
- `uv run python -c "
  from fnmatch import fnmatch
  from pathlib import Path
  import subprocess
  pats = [l.strip() for l in Path('.worktreeinclude').read_text().splitlines()
          if l.strip() and not l.strip().startswith('#')]
  files = subprocess.run(['git','ls-files','-oi','--exclude-standard'],
                         capture_output=True, text=True, check=True).stdout.splitlines()
  kb = [f.strip() for f in files if f.strip().startswith('ai-docs/')]
  assert kb, 'no gitignored ai-docs files on disk to test against — run the kb tasks first'
  missed = [f for f in kb if not any(fnmatch(f, p.lstrip('/')) or fnmatch(Path(f).name, p) for p in pats)]
  assert not missed, missed
  print('AC1 ok: %d KB files matched by the include patterns' % len(kb))"` — verifies AC1
  (the hook's exact matching semantics, simulated in-place; mirrors must exist first).
- `uv run --with pyyaml python -c "
  import yaml
  m = yaml.safe_load(open('ai-docs/sources.yaml'))
  d = m.get('design', [])
  assert len(d) == 5 and all(e['fetched'] and e['file'].startswith('design/') for e in d), d
  urls = [e['url'] for e in d]
  for marker in ['w3.org', 'web.dev/learn/design', 'fonts.google.com/knowledge']:
      assert sum(marker in u for u in urls) == 1, 'missing/duplicate source: ' + marker
  assert sum('nngroup.com/articles/' in u for u in urls) == 2, 'expected exactly two NN/g articles'
  assert any('nngroup.com' in u and 'homepage' in u for u in urls), 'NN/g homepage cornerstone missing'
  mem = [e for e in m['anthropic'] if 'code.claude.com/docs/en/memory' in e['url']]
  assert len(mem) == 1 and mem[0]['fetched'] and mem[0]['file'].startswith('anthropic/'), mem
  idx = open('ai-docs/index.md').read()
  for e in d + mem:
      assert e['file'] in idx, 'index.md missing entry for ' + e['file']
  print('AC2/AC3/AC4 ok')"` — verifies AC2 + AC3 + AC4 (source identities, groups, fetched
  dates, index rows; the epic-level check additionally pins `w3.org/WAI/WCAG22/quickref` —
  keep that identity unless a documented swap says otherwise).
- `uv run --with pyyaml python -c "
  import yaml
  from pathlib import Path
  m = yaml.safe_load(open('ai-docs/sources.yaml'))
  new = m.get('design', []) + [e for e in m['anthropic'] if 'code.claude.com/docs/en/memory' in e['url']]
  assert len(new) == 6, [e['url'] for e in new]
  for e in new:
      text = (Path('ai-docs') / e['file']).read_text()
      head = text[:400]
      assert head.startswith('---'), e['file'] + ': no frontmatter'
      assert 'source: ' + e['url'] in head, e['file'] + ': frontmatter source != manifest url'
      assert 'fetched: ' + str(e['fetched']) in head, e['file'] + ': frontmatter fetched != manifest date'
      assert '> **In here:**' in text, e['file'] + ': no In-here line'
  print('AC2/AC3 mirror integrity ok')"` — verifies AC2 + AC3 (mirrors exist, frontmatter
  agrees with the manifest — a fetched mirror, not a hand-authored file).
- `uv run --with pyyaml python -c "
  import yaml
  from pathlib import Path
  m = yaml.safe_load(open('ai-docs/sources.yaml'))
  new = m.get('design', []) + [e for e in m['anthropic'] if 'code.claude.com/docs/en/memory' in e['url']]
  dec = Path('specs/soriza-design-kb-seed/decisions.md').read_text()
  parts = dec.split('### Build addendum — kb run record', 1)
  assert len(parts) == 2, 'decisions.md missing the build addendum section'
  record = parts[1].split('\n## ', 1)[0]
  lines = [l.strip() for l in record.splitlines()]
  for e in new:
      ok = [l for l in lines if l.startswith('- OK') and e['file'] in l and e['url'] in l]
      assert len(ok) == 1, 'expected exactly one OK record line for %s, got %d' % (e['file'], len(ok))
  urls = [e['url'] for e in m.get('design', [])]
  for fixed in ['web.dev/learn/design', 'fonts.google.com/knowledge']:
      assert sum(fixed in u for u in urls) == 1, 'unconditional identity missing (its failure stops the build, never swaps): ' + fixed
  if not any('w3.org/WAI/WCAG22/quickref' in u for u in urls):
      assert any('w3.org/TR/WCAG22' in u for u in urls), 'WCAG identity missing and substitute is not the locked fallback'
      swap = [l for l in lines if l.startswith('- FAIL') and 'w3.org/WAI/WCAG22/quickref' in l and 'w3.org/TR/WCAG22' in l]
      assert len(swap) == 1, 'WCAG substitution without exactly one recorded FAIL/swap line'
  print('AC2 provenance ok')"` — verifies AC2 (every registered source has exactly one OK
  record in the build addendum; web.dev and fonts.google identities are unconditional; the
  only permitted deviation is WCAG quickref → the locked `w3.org/TR/WCAG22` fallback, which
  must carry exactly one FAIL/swap line naming both the original and substitute URLs).
- `uv run --with pyyaml python -c "
  import yaml
  m = yaml.safe_load(open('ai-docs/sources.yaml'))
  entries = [e for g in m.values() for e in g]
  urls = [e['url'] for e in entries]
  assert len(entries) <= 40, 'over the manifest cap: %d' % len(entries)
  assert len(set(urls)) == len(urls), 'duplicate canonical URLs in the manifest'
  print('AC5 ok: %d entries' % len(entries))"` — verifies AC5.
- `test "$(git ls-files ai-docs/)" = "ai-docs/sources.yaml" && echo "AC6 tracked-surface ok"` —
  verifies AC6 (the manifest is the only tracked file under `ai-docs/`).
- `git check-ignore -q ai-docs/index.md && echo "AC6 ignore ok"` — verifies AC6 (the
  regenerated index stays ignored).
- `uv run python -c "
  import subprocess
  diff = subprocess.run(['git','diff','--name-only','origin/main','--',':!specs'],
                        capture_output=True, text=True, check=True).stdout.split()
  assert sorted(diff) == ['.worktreeinclude', 'ai-docs/sources.yaml'], diff
  stray = subprocess.run(['git','ls-files','-o','--exclude-standard','--',':!specs'],
                         capture_output=True, text=True, check=True).stdout.split()
  assert not stray, 'stray untracked non-ignored files: %r' % stray
  print('AC6 exact-surface ok')"` — verifies AC6 sequence-independently: `git diff` against
  `origin/main` with no second rev measures the working tree (staged + unstaged + committed
  alike), so the assertion holds whether the build has committed yet or not; the `ls-files -o`
  check fails on any stray untracked non-ignored file outside `specs/`.
