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
  assert, clause-exact: `Staffer:` Mira; `Reads:` `intake-standards.md`; `First write:` the
  session-scoped marker `projects/<client>/.intake-in-progress.${CLAUDE_SESSION_ID}`;
  `Writes:` `projects/<client>/intake.md`; `DoR gate:` `intake.md` complete per
  `definition-of-ready.md`; `Refusal:` states refuse and names `intake.md`; `Commit:` states
  all three of `docs(<client>)`, `Refs #`, and the engagement branch. The command body
  asserts an idempotent never-clobber scaffold from `_template` and never touches another
  session's markers (no sweep clause anywhere). The marker pattern
  `projects/*/.intake-in-progress.*` is gitignored.
- **AC8** — `check_intake_readiness.py` scopes to its own session: it matches stdin's
  `session_id` against the marker suffix, exits 2 with per-section stderr diagnostics while
  any **own-session** marked client's `intake.md` is incomplete/missing — a
  **platform-bounded** block (Claude Code overrides after 8 consecutive Stop-hook blocks;
  the hook ignores `stop_hook_active`, never fakes success, and the rungs' DoR refusals
  catch an escaped incomplete intake) — exits 2 with a clear
  message when no own-session marker exists, exits 0 only when every own-marked client is
  complete — **leaving markers in place**: the hook never deletes any marker, so success is
  idempotently re-provable across repeated Stop firings. `_`-prefixed folders are never
  valid; fail-open (exit 0) on malformed stdin/plumbing errors. The session-independence
  regression proves session A (complete client A) exits 0 while session B's incomplete
  client-B marker exists — neither releasing nor stranding the other — and session B still
  exits 2 on its own marker; the same-client test proves two concurrent sessions marking one
  client each gate on their own distinct marker; the re-run regression proves intaking an
  already-complete client leaves the new session's marker in place; the deletion regression
  proves no code path deletes any marker; the cross-hook continuation regression proves two
  successive firings after completion both exit 0 (modeling another parallel Stop hook
  blocking once in between); the block-consistency regression proves an incomplete intake
  yields exit 2 on every firing, including with `stop_hook_active: true`. The hook's
  required-section tuple matches
  `definition-of-ready.md`'s checklist headings (sync test). All hook tests and the wiring
  pin pass.
- **AC9** — The four ladder commands exist under `/soriza-design:*`, and each carries a
  `## Rung Contract` block whose fields assert the exact chain — brief: Elias,
  reads `intake.md`, writes `brief.md`; sitemap: Ivo, reads `brief.md`, writes
  `sitemap-ia.md`; wireframe: Juno, reads `sitemap-ia.md`, writes into `wireframes/`;
  section-briefs: Lior, **reads `wireframes/`** (plus `decision-log.md` change requests, with
  `sitemap-ia.md` as inventory source), writes into `section-briefs/`. Per rung, clause-exact:
  `DoR gate:` names that rung's exact gated predecessor artifact (intake.md / brief.md /
  sitemap-ia.md / wireframes/); `Refusal:` states refuse **and** names that same missing
  artifact; `Commit:` states all three of `docs(<client>)`, `Refs #`, and the engagement
  branch.
- **AC10** — `wireframe.md`'s contract block carries, as parsed fields: `Format:` asserting
  lo-fi grayscale, self-contained, **no external dependencies**, and one page per screen in
  `wireframes/`; `Publish:` asserting best-effort (never blocks) and **all three** locked
  delivery modes (org share / consented public link / the HTML file itself) recorded in
  `decision-log.md`; `Reactions:` asserting copy-as-prompt reactions appended to
  `decision-log.md` as structured change requests. `section-briefs.md`'s contract block
  carries, as parsed fields: `Inventory:` asserting inline loop by default and parallel
  fan-out only for large inventories; `Copy:` asserting draft copy (slogan/headline/body)
  held to `copywriting.md`; a `Packet:` field listing brief + sitemap-ia + wireframes +
  section briefs + typography-direction page + asset checklist + decision log; and
  `Sign-off:` Vera before hand-off.
- **AC11** — `.claude/rules/soriza-design/git-lane.md` exists, `projects/**`-scoped, and
  asserts clause-level: the engagement issue/branch model (`docs/<N>-<client>` via
  `gh issue develop`); per-rung commits (`📝 docs(<client>)` + `Refs #N`); PRs at **exactly
  two gate points**, stated as exactly two one-line `- Gate:` bullets whose normalized
  {gate name → reference keyword} set equals exactly {"brief approved" → `Refs #N`,
  "packet hand-off" → `Closes #N`} — extra gate bullets, missing pairs, bullets carrying
  both keywords, or swapped semantics all fail; an explicit no-PR-per-deliverable clause;
  and the evidence swap sentence (DoR checklist + decision-log entry + client sign-off
  **replace** Test Evidence in `projects/**` PRs).
- **AC12** — Every child issue #44–#48 is closed by its own merged PR (one pipeline run per
  child); epic #43's checklist is fully ticked.

## Validation Commands

Run these to prove the criteria above (from the repo root, on `main`, after all child PRs
merge — each child also runs its own subset at its build). Assertion scripts exit non-zero on
any failure.

- `uv run python -c "
  import json, subprocess
  def q(args): return json.loads(subprocess.run(['gh']+args,capture_output=True,text=True,check=True).stdout)
  pr = q(['pr','view','49','--json','state,body,mergedAt,baseRefName,mergeCommit'])
  assert pr['state'] == 'MERGED' and pr['baseRefName'] == 'main' and pr['mergedAt'], pr
  assert '#43' in pr['body'], 'epic docs PR does not reference #43'
  epic = pr['mergeCommit']['oid']
  for n in ['44','45','46','47','48']:
      for c in q(['issue','view',n,'--json','closedByPullRequestsReferences'])['closedByPullRequestsReferences']:
          head = q(['pr','view',str(c['number']),'--json','headRefOid'])['headRefOid']
          st = q(['api','repos/{owner}/{repo}/compare/%s...%s' % (epic, head)])['status']
          assert st in ('ahead','identical'), 'child PR #%s branch does not contain the epic docs merge (status %s) — its pipeline started before the docs landed' % (c['number'], st)
  print('AC1 ok')"` — verifies AC1 (PR #49 merged to main referencing #43, and every child PR's branch descends from that merge commit — child worktrees branch fresh from origin/main at plan start, so ancestry proves the pipeline started after the docs landed).
- `grep -n "ai-docs" .worktreeinclude` — verifies AC2 (pattern present). Full check: create a scratch worktree (`EnterWorktree` or `git worktree add` + the WorktreeCreate hook) and assert `ai-docs/anthropic/*.md` exists inside it.
- `uv run python -c "
  import yaml
  m = yaml.safe_load(open('ai-docs/sources.yaml'))
  d = m.get('design', [])
  assert len(d) == 5 and all(e['fetched'] and e['file'].startswith('design/') for e in d), d
  urls = [e['url'] for e in d]
  for marker in ['w3.org/WAI/WCAG22/quickref','web.dev/learn/design','fonts.google.com/knowledge']:
      assert sum(marker in u for u in urls) == 1, 'missing/duplicate source: ' + marker
  assert sum('nngroup.com/articles/' in u for u in urls) == 2, 'expected exactly the two NN/g articles'
  assert any('nngroup.com' in u and 'homepage' in u for u in urls), 'NN/g homepage cornerstone missing'
  idx = open('ai-docs/index.md').read()
  for e in d:
      assert e['file'] in idx, 'index.md missing entry for ' + e['file']
  mem = [e for e in m['anthropic'] if 'code.claude.com/docs/en/memory' in e['url']]
  assert len(mem) == 1 and mem[0]['fetched'] and mem[0]['file'].startswith('anthropic/'), mem
  assert mem[0]['file'] in idx, 'index.md missing entry for ' + mem[0]['file']
  print('AC3 ok')"` — verifies AC3 (exact source identities + index entries; adjust a URL marker only if #44 recorded a documented same-topic swap).
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
  rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in text.splitlines() if l.strip().startswith('|')]
  body = [r for r in rows if r and r[0] and not set(''.join(r)) <= set('-: ') and r[0] not in ('Name','Staffer')]
  for who in ['Vera','Mira','Elias','Ivo','Juno','Lior']:
      mine = [r for r in body if r[0] == who]
      assert len(mine) == 1, who + ': expected exactly one roster row keyed by name'
      assert len(mine[0]) >= 4 and all(mine[0][:4]), who + ': all four columns must be non-empty'
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
  assert 'Mira' in fields['Staffer']
  assert 'intake-standards' in fields['Reads'], 'Reads must name intake-standards.md'
  assert '.intake-in-progress.' in fields['First write'] and 'CLAUDE_SESSION_ID' in fields['First write'], 'marker not session-scoped'
  assert 'intake.md' in fields['Writes']
  assert 'intake.md' in fields['DoR gate'] and 'definition-of-ready' in fields['DoR gate'], 'DoR gate must name intake.md + definition-of-ready.md'
  assert re.search(r'refuse', fields['Refusal'], re.I) and 'intake.md' in fields['Refusal'], 'Refusal must refuse AND name intake.md'
  for clause in ['docs(', 'Refs #', 'engagement branch']:
      assert clause in fields['Commit'], 'Commit missing clause ' + clause
  assert re.search(r'never clobber|existing|idempotent', text, re.I), 'no idempotence clause'
  assert 'sweep' not in text.lower(), 'sweep clause present — no process may touch other sessions markers'
  ignored = subprocess.run(['git','check-ignore','projects/x/.intake-in-progress.abc123'],capture_output=True).returncode == 0
  assert ignored, 'marker pattern not gitignored'
  print('AC7 ok')"` — verifies AC7 (clause-exact contract fields; no sweep).
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
      assert src in f['DoR gate'], name + ': DoR gate does not name the exact predecessor artifact'
      assert re.search(r'refuse', f['Refusal'], re.I) and src in f['Refusal'], name + ': refusal must refuse AND name the missing artifact'
      for clause in ['docs(', 'Refs #', 'engagement branch']:
          assert clause in f['Commit'], '%s: Commit missing clause %s' % (name, clause)
  f = contract('section-briefs')
  assert 'sitemap-ia.md' in f['Reads'] and 'decision-log' in f['Reads'], 'section-briefs: inventory/change-request inputs missing'
  print('AC9 ok')"` — verifies AC9 (exact chain; DoR/refusal/commit clause-exact per rung).
- `uv run python -c "
  from pathlib import Path
  import re
  def contract(name):
      text = Path('.claude/commands/soriza-design/%s.md' % name).read_text()
      block = re.search(r'## Rung Contract\n(.*?)(\n## |\Z)', text, re.S)
      return text, dict(re.findall(r'\*{0,2}([A-Z][\w -]+)\*{0,2}:\s*(.+)', block.group(1)))
  w, wf = contract('wireframe')
  for req in ['Format','Publish','Reactions']:
      assert req in wf, 'wireframe: missing field ' + req
  for clause in ['grayscale','self-contained','no external dependencies','one page per screen']:
      assert clause in wf['Format'], 'wireframe Format missing: ' + clause
  for clause in ['best-effort','never block','org share','consent','public link','HTML file','decision-log']:
      assert clause in wf['Publish'], 'wireframe Publish missing: ' + clause
  for clause in ['copy-as-prompt','decision-log','change request']:
      assert clause in wf['Reactions'], 'wireframe Reactions missing: ' + clause
  s, sf = contract('section-briefs')
  for req in ['Inventory','Copy','Packet','Sign-off']:
      assert req in sf, 'section-briefs: missing field ' + req
  for clause in ['inline','fan-out','large']:
      assert clause in sf['Inventory'], 'section-briefs Inventory missing: ' + clause
  for clause in ['slogan','headline','body','copywriting']:
      assert clause in sf['Copy'], 'section-briefs Copy missing: ' + clause
  for item in ['brief','sitemap-ia','wireframes','typography','asset','decision log']:
      assert item in sf['Packet'], 'Packet missing: ' + item
  assert 'Vera' in sf['Sign-off']
  print('AC10 ok')"` — verifies AC10 (format, delivery modes, reactions, inventory, copy, packet, sign-off — all parsed fields).
- `uv run python -c "
  from pathlib import Path
  import re
  text = Path('.claude/rules/soriza-design/git-lane.md').read_text()
  assert re.search(r'paths:\s*\n?\s*-?\s*.projects/\*\*', text), 'no paths scope'
  for needle in ['docs/<N>-<client>','gh issue develop','docs(<client>)','Refs #N']:
      assert needle in text, 'git-lane.md missing: ' + needle
  lines = text.splitlines()
  gates = [l for l in lines if l.strip().startswith('- Gate:')]
  assert len(gates) == 2, 'expected exactly two - Gate: bullets, got %d' % len(gates)
  norm = set()
  for l in gates:
      assert not ('Refs #' in l and 'Closes #' in l), 'gate bullet carries both reference keywords'
      name = 'brief approved' if 'brief approved' in l else ('packet hand-off' if 'packet hand-off' in l else '?')
      ref = 'Refs' if 'Refs #' in l else ('Closes' if 'Closes #' in l else '?')
      norm.add((name, ref))
  assert norm == {('brief approved','Refs'), ('packet hand-off','Closes')}, norm
  assert re.search(r'(replace|instead of).{0,60}Test Evidence|Test Evidence.{0,60}(replaced|swap)', text, re.S), 'no evidence-swap clause'
  for needle in ['DoR checklist','decision-log','sign-off']:
      assert needle in text, 'evidence swap incomplete: ' + needle
  assert re.search(r'(no|never).{0,40}PR.{0,40}(per|each).{0,20}(draft|deliverable)|only.{0,30}gate', text, re.I|re.S), 'PR-per-deliverable not excluded'
  print('AC11 ok')"` — verifies AC11 (both gate points, swap clause, exclusion).
- `uv run python -c "
  import json, re, subprocess
  def q(args): return json.loads(subprocess.run(['gh']+args,capture_output=True,text=True,check=True).stdout)
  body = q(['issue','view','43','--json','body'])['body']
  for n in ['44','45','46','47','48']:
      assert re.search(r'- \[x\] #%s\b' % n, body), 'epic checkbox for #%s not ticked' % n
      ch = q(['issue','view',n,'--json','state,closedByPullRequestsReferences'])
      assert ch['state'] == 'CLOSED', '#%s is not closed' % n
      assert len(ch['closedByPullRequestsReferences']) >= 1, '#%s has no closing PR' % n
  print('AC12 ok')"` — verifies AC12 (hard assertions: all five checkboxes ticked, every child CLOSED with ≥1 closing PR).
