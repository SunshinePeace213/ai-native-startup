# Issue body skeletons

Agent-facing markdown skeletons for creating issues from the CLI. GitHub issue
**forms** (`.github/ISSUE_TEMPLATE/*.yml`) cannot be submitted via `gh`, so
`/harness-layer:harness-plan` fills the matching skeleton here and runs
`gh issue create --body-file <skeleton>`.

**Sync rule:** each skeleton's `##` headings must match its form's field labels
one-to-one. When you add, remove, or rename a field in a `.github/ISSUE_TEMPLATE/*.yml`
form, update the paired skeleton in the same change — and vice versa.

| Skeleton | Form |
| --- | --- |
| `feature.md` | `.github/ISSUE_TEMPLATE/feature.yml` |
| `bug.md` | `.github/ISSUE_TEMPLATE/bug.yml` |
| `chore.md` | `.github/ISSUE_TEMPLATE/chore.yml` |
| `epic.md` | `.github/ISSUE_TEMPLATE/epic.yml` |
