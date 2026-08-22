# Hiring: approved 2026-08-22 — onboarding owed by the Chief of Staff

Anthony approved hiring these five agents (source: contains-studio/agents on
GitHub, fetched verbatim into this directory):

| Agent | Role on our team |
|---|---|
| rapid-prototyper | **Build anchor**: turns an approved PRD into a deployed MVP inside the 48h SLA |
| ui-designer | Fast credible design pass before/during the build |
| test-writer-fixer | Smoke coverage on the MVP's critical path |
| experiment-tracker | Instruments each MVP against its PRD's assumptions register; reads validation results (fills the validation-designer role) |
| ux-researcher | Designs user conversations and synthesizes feedback once validation contact starts |

## Onboarding checklist (CoS executes at the next staff meeting)

For each hire, create `.claude/agents/<name>.md` by ADAPTING the file here — do
not copy blindly:

1. Keep the expertise and working style; strip the upstream examples block if
   verbose.
2. Subordinate to our operating manual: prepend a paragraph binding the agent to
   CLAUDE.md (prime directive, autonomy rule — build agents act only on an
   explicitly approved PRD, never self-initiate builds), goals.md (48h SLA), and
   the sync discipline (pull before work, push after).
3. Wire pipeline touchpoints: builds start from `prd/<id>.md` when Anthony
   approves; MVP work logs to the painpoint's `## Log`; experiment-tracker reads
   the PRD's assumptions register.
4. Assign a model per the cost rubric (mechanical work → haiku; design/build
   judgment → default).
5. Register each hire in CLAUDE.md's staff table and log the onboarding in
   playbook-changelog.md.
6. Delete this directory's file for each agent once onboarded.

## Staffing risk to monitor (flag in packs if the 48h SLA is threatened)

Anthony passed on frontend-developer, backend-architect, and devops-automator:
rapid-prototyper carries the full stack AND deployment alone. If an MVP build
strains this (deploy friction, backend complexity), bring a re-hire proposal to
the meeting with impact estimate — do not hire unilaterally.
