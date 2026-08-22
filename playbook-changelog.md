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

## 2026-08-22
- files: .claude/agents/ (consolidation), templates/sprint.md, CLAUDE.md
- change: team consolidated to 5 under Iris (Anthony's approval after Q&A): Psyche→Socrates (user research), Metis→Athena (experiments; readouts now require Argus co-sign), Apollo→Hephaestus (design pass). Argus kept independent deliberately (builder never grades own work). Designer-rehire trigger added to Iris's staffing watch.
- evidence: Anthony's consolidation directive (max 5 agents); rollback = git revert (retired playbooks in history)

## 2026-08-22
- files: .claude/agents/chief-of-staff.md, CLAUDE.md, cloud routine "daily staff meeting pack"
- change: standing workforce-upkeep grant — Iris continuously maintains agent playbooks (sharpen roles, tighten handoffs, dedupe, propagate Anthony's decisions, refine methods from retro evidence), one commit + changelog entry each. Boundary: no hire/fire/merge/split, no decision-rights changes, no autonomy or tool-access expansion — those remain Anthony's, proposed via pack section 7.
- evidence: Anthony's explicit instruction ("regularly update the agents and their files... under the improving the workforce abilities that already exist"); rollback = git revert

## 2026-08-22
- file: .claude/agents/chief-of-staff.md
- change: standing callout authority — Iris may immediately call out bad ideas or effort-not-worth-it to Anthony or any subagent when reasoning is very strong; candor not veto; capture stays protected by the prime directive
- evidence: Anthony's explicit grant in live session; rollback = git revert

## 2026-08-22
- files: .claude/agents/rapid-prototyper.md, painpoints/pp-24, taste-profile.md, archive/, meetings/sprints/
- change: Warm Path MVP archived and pp-24 parked after post-mortem; Anthony's new standing cold-start rule (visible value in <60s, zero setup) propagated into Hephaestus's playbook; three taste-profile patterns distilled (judges by pull not politeness; values solving the hard part; setup cost is disqualifying)
- evidence: post-mortem with Anthony 2026-08-22 — weak reaction from real people; root causes cold-start cost and avoiding the "what to say" problem; rollback = git revert (nothing deleted, MVP repo intact)
