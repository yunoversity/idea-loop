---
description: Anthony approves a PRD for build — starts the 48h MVP sprint (SLA clock starts NOW)
---

Anthony has explicitly approved the PRD below for build. This is the SLA starting
gun (goals.md: working, deployed MVP within 48 hours).

1. Record the approval: in the painpoint's frontmatter set `status: mvp`, note the
   approval timestamp + Anthony's one-line reason in `## Log` and taste-profile.md.
2. Create the sprint ledger: `sprint.md` at repo root from `templates/sprint.md`,
   filled in (PRD, deadline = now + 48h CT, assumptions under test from the PRD's
   register). If a sprint.md from a previous build exists, archive it to
   `meetings/sprints/<old-id>.md` first.
3. Scaffold the MVP workspace: a NEW local repo at `~/Projects/mvp-<slug>` (git
   init; never build inside idea-loop). Ask Anthony to create the matching private
   GitHub repo when deploy needs it.
4. Hand off to Hephaestus (rapid-prototyper agent) as sprint captain to begin the
   48h cadence. Commit and push idea-loop so the cloud team sees the sprint.

PRD: $ARGUMENTS
