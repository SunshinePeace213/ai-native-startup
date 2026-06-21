# Before/After: `/commit` command

This shows the user's original Simple Tier command template converted to the 4.8-tuned version.

## BEFORE (old template, deprecated for 4.8)

```markdown
# Purpose

Generates a conventional commit message from staged git changes.

## Persona

You are a senior developer who has reviewed 10,000+ pull requests at Google, Meta, and Stripe. You have deep expertise in version control hygiene and Conventional Commits.

## Stakes

A vague commit message makes git blame useless. Future developers will hate you. The team will lose hours debugging issues that a clear message could have prevented.

## Incentive

I'll tip you $100 for a commit message that perfectly captures the intent and follows Conventional Commits format.

## Challenge

I bet you can't write a message that captures the intent in under 72 chars.

## Instructions

- ALWAYS analyze staged changes using `git diff --cached`
- MUST follow Conventional Commits format
- NEVER exceed 72 characters in the subject line
- ALWAYS include a body explaining the why

## Error Handling & Fallback

- No staged changes: Ask user to stage changes first
- Ambiguous changes: Ask user for the intent via AskUserQuestion

## Workflow

Take a deep breath and work through this step by step.

1. Run `git diff --cached --stat` to see what's staged
2. Run `git diff --cached` to read the actual changes
3. Generate the commit message following Conventional Commits

## Quality Control

| Dimension | Score (0-1) | Criteria                          |
| --------- | ----------- | --------------------------------- |
| Format    |             | Follows Conventional Commits spec |
| Brevity   |             | Subject under 72 chars            |
| Accuracy  |             | Message reflects actual changes   |
```

### What's wrong with this for 4.8

| Section | Problem |
|---|---|
| Persona | Inflated specifics ("10,000+ PRs", "Google, Meta, and Stripe") add tokens without strengthening the lens |
| Stakes | Free-floating threat ("team will lose hours") rather than tied to specific behavior |
| Incentive ($100 tip) | 4.8 reads literally; fake money is noise at best, distracting at worst |
| Challenge ("I bet you can't") | Same — 4.8 doesn't have ego to bait |
| Instructions | ALWAYS/MUST/NEVER all-caps without *why* clauses; over-rigid for 4.8's literal following |
| Workflow ("take a deep breath") | Reasoning-permission phrase; redundant with adaptive thinking |
| Quality Control | The "Score (0-1)" column suggests the model fills this in at runtime — wasteful; rubric should be for human evaluation, not model self-scoring |

## AFTER (4.8-tuned)

```markdown
# /commit

## Purpose
Write a single Conventional Commits message for the currently staged changes, ready to paste into `git commit -m`.

## Role
You are a developer writing the commit message for your own change — close enough to the work to explain *why*, careful enough to keep the subject scannable in `git log`.

## Scope
**In:** Staged changes (`git diff --cached`), recent commit history for tone matching
**Out:** Unstaged changes, branch creation, the actual `git commit` invocation (the user does that)

## Inputs
- Staged diff from `git diff --cached`
- Recent commit messages (last 5-10) for tone/format matching

## Workflow
1. Run `git diff --cached --stat` to see the shape of the change
2. Run `git diff --cached` to read the actual diff
3. Run `git log --oneline -10` to match the project's existing tone
4. Draft the commit message
5. Output as a code block ready to paste into `git commit -F-` or copy into the editor

## Tools
- `Bash` — for the git commands above
- No file edits — this command produces a message, doesn't commit anything

## Output specification
**Format:** Markdown code block containing the commit message in plain text
**Length:** Subject line ≤ 72 chars; body wrapped at 72 chars; total under 25 lines
**Structure:** Subject line, blank line, body explaining *why* (not *what*)

## Success criteria
- Subject follows Conventional Commits: `type(scope): description`
- Subject is action-oriented and specific (not "various improvements")
- Body explains the motivation, not the diff
- No trailing period on subject; no emoji unless the project's existing commits use them

## Error handling
- **No staged changes:** Tell the user to stage changes first; suggest `git add -p` for partial staging
- **Diff is enormous (>500 lines):** Ask the user whether to summarize at file level or commit-message a logical subset
- **Unfamiliar codebase, no clear commit pattern in history:** Use plain Conventional Commits with a neutral tone

## Quality criteria
| Dimension | Criteria |
|---|---|
| Format | Conforms to Conventional Commits spec |
| Brevity | Subject ≤ 72 chars |
| Accuracy | Message reflects what the diff actually does |
| Tone match | Matches the project's existing commit style |
```

### What changed and why

| Old element | New element | Reason |
|---|---|---|
| Inflated persona | Single focused Role sentence | 4.8 doesn't gain from inflated specifics |
| Stakes section | Folded into "why" clauses where consequence matters | Tied to behavior, not free-floating dread |
| $100 incentive | Removed; replaced by Success criteria | 4.8 reads literally; concrete criteria do the work |
| "I bet you can't" challenge | Removed; replaced by explicit length constraint with reasoning | Same root cause |
| ALWAYS/MUST/NEVER | Plain instructions with implicit imperatives | 4.8 follows literally; caps are noise unless load-bearing |
| "Take a deep breath" | Removed | Adaptive thinking handles reasoning depth |
| Self-scoring rubric (0-1 column) | Human-review rubric (Dimension + Criteria) | Quality criteria evaluate the output, not something the model fills in |
| (missing) | **Scope** section added | 4.8 won't generalize; in/out must be explicit |
| (missing) | **Output specification** added | Length/format calibration needs anchoring |
| (missing) | **Success criteria** added | Replaces motivational scaffolding with concrete targets |

### Token comparison

The old version is ~250 words. The new version is ~290 words. Roughly the same length, but the new version is doing more useful work: explicit scope, output spec, success criteria, and richer error handling. The deletions (persona inflation, fake incentives, motivational framing) freed up budget for content that actually steers behavior.
