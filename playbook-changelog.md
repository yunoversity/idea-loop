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
