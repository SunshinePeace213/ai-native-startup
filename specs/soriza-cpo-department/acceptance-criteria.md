# Acceptance Criteria: Soriza design department — slice 1 (soriza-design)

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here. Epic-level: AC2–AC11 are
> verified child by child as each ships, then all together on `main` by `validate-all`.
> Rung-prompt *runtime* behavior is validated at three layers: structural assertions below,
> each child's harness-review, and the pilot's first intake (gaps land in
> `soriza-design/lessons.md`).

## Acceptance Criteria

- **AC1** — The epic planning docs (`specs/soriza-cpo-department/` including discovery/ and
  artifacts/) are merged to `main` via a docs PR referencing #43, before any child pipeline
  starts.
- **AC2** — `.worktreeinclude` contains an `ai-docs/*` pattern, and a freshly created worktree
  receives the cached mirrors (untracked-and-ignored files under `ai-docs/`).
- **AC3** — `ai-docs/sources.yaml` carries a `design` group with five entries (WCAG 2.2
  quickref, web.dev Learn Design, NN/g homepage cornerstone, NN/g writing-for-the-web, Google
  Fonts Knowledge) plus an `anthropic` entry for the memory docs page — each with a canonical
  `url`, a `file` under its group folder, and a non-null `fetched` date; `ai-docs/index.md`
  lists them; no mirror was hand-authored.
- **AC4** — `projects/_template/` contains exactly the client scaffold: `intake.md`,
  `brief.md`, `sitemap-ia.md`, `asset-checklist.md`, `decision-log.md`, `wireframes/README.md`,
  `section-briefs/README.md`, and `section-briefs/_library/` with exactly nine skeletons
  (header-navigation, hero, logo-tape, features-solutions, testimonials, pricing-plans,
  content-blog, footer, cta-band) — every skeleton carrying both a "One job" and a "One desired
  action" field. No extra or missing files.
- **AC5** — `.claude/rules/soriza-design/` holds `client-communication.md`,
  `intake-standards.md`, `definition-of-ready.md`, `brief-format.md`, `section-anatomy.md`,
  `copywriting.md`, and `lessons.md`, each with `paths:` frontmatter scoping to
  `projects/**/*`, each with real starter content (no TBD/stub markers); `lessons.md` follows
  the development-log.md contract.
- **AC6** — `.claude/rules/soriza/roster.md` has one table row per staffer — Vera, Mira, Elias,
  Ivo, Juno, Lior — each row filling all four columns (name, position, deliverable owned,
  status); `AGENTS.md` points to the roster and the rules family and carries a `projects/`
  structure row; the set of root-level markdown files is unchanged (no new root memory file).
- **AC7** — `/soriza-design:intake` exists with `disable-model-invocation: true` and the Stop
  hook registered in its frontmatter, and carries a `## Rung Contract` block whose fields
  assert: `Staffer:` Mira; `First write:` the per-client marker
  `projects/<client>/.intake-in-progress` (plus the sweep of markers on already-complete
  clients); `Writes:` `projects/<client>/intake.md`; an idempotent never-clobber scaffold from
  `_template`; `Refusal:` and `Commit:` clauses. The marker pattern
  `projects/*/.intake-in-progress` is gitignored.
- **AC8** — `check_intake_readiness.py` blocks until **every** marked client's `intake.md` is
  complete: exit 2 with per-section stderr diagnostics on any incomplete/missing marked
  `intake.md`; exit 2 with a clear message when no marker exists; `_`-prefixed folders are
  never valid; exit 0 only when all marked clients are complete; fail-open (exit 0) on
  malformed stdin/plumbing errors. The cross-client regression test proves a complete client A
  cannot release an incomplete marked client B, and the two-marker test covers concurrent
  intakes. The hook's required-section tuple matches `definition-of-ready.md`'s checklist
  headings (sync test). All hook tests and the wiring pin pass.
- **AC9** — The four ladder commands exist under `/soriza-design:*`, and each carries a
  `## Rung Contract` block whose fields assert the exact chain — brief: Elias,
  reads `intake.md`, writes `brief.md`; sitemap: Ivo, reads `brief.md`, writes
  `sitemap-ia.md`; wireframe: Juno, reads `sitemap-ia.md`, writes into `wireframes/`;
  section-briefs: Lior, **reads `wireframes/`** (plus `decision-log.md` change requests, with
  `sitemap-ia.md` as inventory source), writes into `section-briefs/` — plus a `DoR gate:`
  field naming the gated predecessor artifact, a `Refusal:` field (refuse and name what's
  missing), and a `Commit:` field (per-rung commit on the engagement branch).
- **AC10** — `wireframe.md`'s contract block additionally asserts: lo-fi grayscale,
  self-contained HTML with **no external dependencies**, one page per screen in
  `projects/<client>/wireframes/`; `Publish:` best-effort (never blocks) and **all three**
  locked delivery modes (org share / consented public link / the HTML file itself) recorded in
  `decision-log.md`; copy-as-prompt reactions appended to `decision-log.md` as structured
  change requests. `section-briefs.md`'s contract block additionally asserts: inline inventory
  loop, parallel fan-out only for large inventories, draft copy (slogan/headline/body) held to
  `copywriting.md`, and a `Packet:` field listing brief + sitemap-ia + wireframes + section
  briefs + typography-direction page + asset checklist + decision log, with `Sign-off:` Vera
  before hand-off.
- **AC11** — `.claude/rules/soriza-design/git-lane.md` exists, `projects/**`-scoped, and
  asserts clause-level: the engagement issue/branch model (`docs/<N>-<client>` via
  `gh issue develop`); per-rung commits (`📝 docs(<client>)` + `Refs #N`); PRs at **exactly
  two gate points** — "brief approved" (`Refs #N`) and "packet hand-off" (`Closes #N`) — and
  no PR-per-deliverable; and the evidence swap sentence (DoR checklist + decision-log entry +
  client sign-off **replace** Test Evidence in `projects/**` PRs).
- **AC12** — Every child issue #44–#48 is closed by its own merged PR (one pipeline run per
  child); epic #43's checklist is fully ticked.

## Validation Commands

Run these to prove the criteria above (from the repo root, on `main`, after all child PRs
merge — each child also runs its own subset at its build). Assertion scripts exit non-zero on
any failure.

- `git log --oneline origin/main -- specs/soriza-cpo-department/ | head -3` — verifies AC1. Non-empty after the epic docs PR merges.
- `grep -n "ai-docs" .worktreeinclude` — verifies AC2 (pattern present). Full check: create a scratch worktree (`EnterWorktree` or `git worktree add` + the WorktreeCreate hook) and assert `ai-docs/anthropic/*.md` exists inside it.
- `uv run python -c "
  import yaml
  m = yaml.safe_load(open('ai-docs/sources.yaml'))
  d = m.get('design', [])
  assert len(d) == 5 and all(e['fetched'] and e['file'].startswith('design/') for e in d), d
  assert any('code.claude.com/docs/en/memory' in e['url'] for e in m['anthropic'])
  print('AC3 ok')"` — verifies AC3.
- `uv run python -c "
  from pathlib import Path
  t = Path('projects/_template')
  files = sorted(str(p.relative_to(t)) for p in t.rglob('*') if p.is_file())
  lib = ['section-briefs/_library/%s.md' % n for n in
         ['content-blog','cta-band','features-solutions','footer','header-navigation',
          'hero','logo-tape','pricing-plans','testimonials']]
  expected = sorted(['intake.md','brief.md','sitemap-ia.md','asset-checklist.md',
                     'decision-log.md','wireframes/README.md','section-briefs/README.md'] + lib)
  assert files == expected, (files, expected)
  for s in lib:
      text = (t / s).read_text()
      assert 'One job' in text and 'One desired action' in text, s
  print('AC4 ok')"` — verifies AC4 (exact file set + both fields in all nine skeletons).
- `uv run python -c "
  from pathlib import Path
  import re
  fam = Path('.claude/rules/soriza-design')
  names = ['client-communication','intake-standards','definition-of-ready','brief-format',
           'section-anatomy','copywriting','lessons']
  for n in names:
      text = (fam / (n + '.md')).read_text()
      assert re.search(r'paths:\s*\n?\s*-?\s*.projects/\*\*', text), n + ': no paths scope'
      assert len(text.splitlines()) >= 15, n + ': suspiciously thin'
      assert not re.search(r'TBD|TODO|fill me|placeholder', text, re.I), n + ': stub marker'
  print('AC5 ok')"` — verifies AC5.
- `uv run python -c "
  from pathlib import Path
  import subprocess
  text = Path('.claude/rules/soriza/roster.md').read_text()
  for who in ['Vera','Mira','Elias','Ivo','Juno','Lior']:
      row = [l for l in text.splitlines() if l.strip().startswith('|') and who in l]
      assert row and row[0].count('|') >= 5, who + ': missing row or column'
  agents = Path('AGENTS.md').read_text()
  assert 'soriza/roster.md' in agents and 'soriza-design' in agents and 'projects/' in agents
  root_md = sorted(p for p in subprocess.run(['git','ls-files','*.md'],capture_output=True,text=True).stdout.splitlines() if '/' not in p)
  assert root_md == ['AGENTS.md','CLAUDE.md'], root_md
  print('AC6 ok')"` — verifies AC6 (adjust the expected root-md list only if `main` already tracks another root file at merge time).
- `uv run python -c "
  from pathlib import Path
  import re, subprocess
  text = Path('.claude/commands/soriza-design/intake.md').read_text()
  assert 'disable-model-invocation: true' in text and 'check_intake_readiness.py' in text and 'Stop' in text.split('---')[1]
  block = re.search(r'## Rung Contract\n(.*?)(\n## |\Z)', text, re.S)
  assert block, 'no ## Rung Contract block'
  fields = dict(re.findall(r'\*{0,2}(Staffer|Reads|Writes|First write|DoR gate|Refusal|Commit)\*{0,2}:\s*(.+)', block.group(1)))
  assert set(fields) == {'Staffer','Reads','Writes','First write','DoR gate','Refusal','Commit'}, fields
  assert 'Mira' in fields['Staffer'] and '.intake-in-progress' in fields['First write']
  assert 'intake.md' in fields['Writes']
  assert re.search(r'never clobber|existing|idempotent', text, re.I), 'no idempotence clause'
  assert 'sweep' in text.lower(), 'no stale-marker sweep clause'
  ignored = subprocess.run(['git','check-ignore','projects/x/.intake-in-progress'],capture_output=True).returncode == 0
  assert ignored, 'marker pattern not gitignored'
  print('AC7 ok')"` — verifies AC7 (field-level contract, not keywords).
- `uv run pytest tests/harness-layer/hooks/ -k "intake or wiring"` — verifies AC8 (contract,
  fail-open, doctrine-sync, cross-client regression, wiring pin). All green.
- `uv run python -c "
  from pathlib import Path
  import re
  def contract(name):
      text = Path('.claude/commands/soriza-design/%s.md' % name).read_text()
      block = re.search(r'## Rung Contract\n(.*?)(\n## |\Z)', text, re.S)
      assert block, name + ': no ## Rung Contract block'
      return dict(re.findall(r'\*{0,2}([A-Z][\w -]+)\*{0,2}:\s*(.+)', block.group(1)))
  chain = {'brief': ('Elias','intake.md','brief.md'),
           'sitemap': ('Ivo','brief.md','sitemap-ia.md'),
           'wireframe': ('Juno','sitemap-ia.md','wireframes/'),
           'section-briefs': ('Lior','wireframes/','section-briefs/')}
  for name, (who, src, dst) in chain.items():
      f = contract(name)
      for req in ['Staffer','Reads','Writes','DoR gate','Refusal','Commit']:
          assert req in f, '%s: missing field %s' % (name, req)
      assert who in f['Staffer'] and src in f['Reads'] and dst in f['Writes'], (name, f)
      assert f['DoR gate'].strip(), name + ': empty DoR gate'
      assert re.search(r'refuse|name.*missing', f['Refusal'], re.I), name + ': weak refusal clause'
      assert re.search(r'engagement branch|docs\(', f['Commit']), name + ': commit not on engagement lane'
  f = contract('section-briefs')
  assert 'sitemap-ia.md' in f['Reads'] and 'decision-log' in f['Reads'], 'section-briefs: inventory/change-request inputs missing'
  print('AC9 ok')"` — verifies AC9 (exact chain, field-level).
- `uv run python -c "
  from pathlib import Path
  import re
  def contract(name):
      text = Path('.claude/commands/soriza-design/%s.md' % name).read_text()
      block = re.search(r'## Rung Contract\n(.*?)(\n## |\Z)', text, re.S)
      return text, dict(re.findall(r'\*{0,2}([A-Z][\w -]+)\*{0,2}:\s*(.+)', block.group(1)))
  w, wf = contract('wireframe')
  assert 'Publish' in wf, 'wireframe: no Publish field'
  for clause in ['best-effort','org share','public link','HTML file']:
      assert clause in wf['Publish'], 'wireframe Publish missing: ' + clause
  for clause in ['grayscale','self-contained','no external dependencies','copy-as-prompt','decision-log']:
      assert clause in w, 'wireframe.md missing: ' + clause
  s, sf = contract('section-briefs')
  assert 'Packet' in sf and 'Sign-off' in sf, 'section-briefs: Packet/Sign-off fields missing'
  for item in ['brief','sitemap-ia','wireframes','typography','asset','decision log']:
      assert item in sf['Packet'], 'Packet missing: ' + item
  assert 'Vera' in sf['Sign-off']
  for clause in ['inline','fan-out','copywriting','slogan','headline']:
      assert clause in s, 'section-briefs.md missing: ' + clause
  print('AC10 ok')"` — verifies AC10 (delivery modes, packet contents, sign-off — field-level).
- `uv run python -c "
  from pathlib import Path
  import re
  text = Path('.claude/rules/soriza-design/git-lane.md').read_text()
  assert re.search(r'paths:\s*\n?\s*-?\s*.projects/\*\*', text), 'no paths scope'
  for needle in ['docs/<N>-<client>','gh issue develop','Refs #','Closes #']:
      assert needle in text, 'git-lane.md missing: ' + needle
  assert 'brief approved' in text and 'packet hand-off' in text, 'gate points not both named'
  assert re.search(r'(replace|instead of).{0,60}Test Evidence|Test Evidence.{0,60}(replaced|swap)', text, re.S), 'no evidence-swap clause'
  for needle in ['DoR checklist','decision-log','sign-off']:
      assert needle in text, 'evidence swap incomplete: ' + needle
  assert re.search(r'(no|never).{0,40}PR.{0,40}(per|each).{0,20}(draft|deliverable)|only.{0,30}gate', text, re.I|re.S), 'PR-per-deliverable not excluded'
  print('AC11 ok')"` — verifies AC11 (both gate points, swap clause, exclusion).
- `gh issue view 43 --json body -q .body | grep -c "\- \[x\] #4"` — verifies AC12 (expect 5); and
  `for n in 44 45 46 47 48; do gh issue view $n --json state,closedByPullRequestsReferences -q '[.state, (.closedByPullRequestsReferences|length)] | @tsv'; done` — every child CLOSED with ≥1 closing PR.
