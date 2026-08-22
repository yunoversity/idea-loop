# Playbook changelog

Every approved edit to `.claude/agents/*.md`, so self-improvement drift stays
auditable and reversible. Entries added by the chief-of-staff at meeting retros,
only after Anthony approves.

<!-- ## YYYY-MM-DD
- file: .claude/agents/….md
- change: what changed, in one line
- evidence: why (what the week showed)
-->

## 2026-08-22
- file: .claude/agents/chief-of-staff.md, CLAUDE.md, templates/meeting-pack.md
- change: added pre-meeting workflow review with low-risk-implement / needs-Anthony rubric (Anthony's explicit instruction, live session)
- evidence: Anthony directed the CoS to improve workflows ahead of meetings, implementing low-risk items autonomously

## 2026-08-22
- file: .claude/agents/intake.md
- change: model pinned to haiku (mechanical extraction work)
- evidence: first low-risk implementation under the new rubric — extraction needs no frontier reasoning; rollback = remove the `model:` line

## 2026-08-22
- file: cloud routine "Iris — daily dashboard refresh"
- change: model sonnet-5 → haiku-4.5 (runs a script and republishes an artifact)
- evidence: purely mechanical run; verified by test-firing after the change; rollback = set model back to claude-sonnet-5

## 2026-08-22
- file: .claude/agents/{rapid-prototyper,ui-designer,test-writer-fixer,experiment-tracker,ux-researcher}.md
- change: five approved hires reviewed (no malicious content) and onboarded with misalignments corrected — see hiring/ONBOARDING.md for the full findings
- evidence: Anthony's explicit instruction (review, resolve, onboard; Telegram only for major risks — none found); rollback = delete the five files

## 2026-08-22
- files: all agent playbooks, scripts/, CLAUDE.md, templates/sprint.md, .claude/commands/build.md, cloud routines
- change: coordination overhaul (Anthony-approved P1-P5): queue.md as single priority source rendered by digest+dashboard; Echo inbox-intake cloud routine every 3h (haiku); sprint.md ledger with Hephaestus as captain, hour-24 checkpoint, escalations/ Telegram alert; /build command starting the 48h SLA with per-MVP repos; daemon reads queue/pack/sprint and resets thread on each new pack; pantheon names adopted (Iris, Echo, Socrates, Athena, Hephaestus, Apollo, Argus, Metis, Psyche)
- evidence: architecture critique session with Anthony; P6 (incremental packs) declined; rollback = git revert of this commit + delete the two routine changes
