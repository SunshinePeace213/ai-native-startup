---
paths:
  - "clients/**/*"
---

# Studio Identity

The Soriza brand that every client-facing document under `clients/` wears. One file,
so rebranding costs an edit here rather than a hunt across every phase's output.

## Studio

Soriza is an AI-native studio selling three things: website design, software
development, and agentic-layer builds. Every client engagement runs through the
`studio-layer` phases and stops at a signed design handoff — Soriza designs and
specs; it does not develop from the handoff itself.

## Voice

Write to the client the way a principal designer talks in a working session: direct,
warm, and specific — never templated agency copy. Name the actual component, screen,
or decision instead of a generic placeholder. Ask one clear question at a time. State
trade-offs plainly ("this option ships faster, that one reads more premium") instead
of hedging. No filler enthusiasm, no jargon the client didn't bring themselves.

## Letterhead

Every client-facing document opens with:

```markdown
# Soriza — <Document Title>

**Client:** <Client> · **Project:** <Project> · **Phase:** <P0–P7 name>
**Date:** <YYYY-MM-DD>
```

## Sign-off block

Every document that closes a hard gate carries the sign-off shape from spec.md
`## Interfaces & Contracts` → "Sign-off document": an `Approver` name and role, a
`Date`, and an artifact table of `Artifact` / `SHA-256` rows — one row per approved
file, the hash of its current content. Approver and Date must both be filled; a
blank or placeholder value is the same as no signature.
