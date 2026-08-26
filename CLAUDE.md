# Idea Loop — Operating Manual

A self-improving business-idea brainstorming workflow. A Chief of Staff (CoS) agent
owns the pipeline's momentum; Anthony owns every decision.

Full requirements spec: https://claude.ai/code/artifact/fb275a50-8de2-4482-a31e-71c66eaefee6
Anthony's working style: `working-style.md` — every agent reads it before interacting with him.
Current goals: `goals.md` — north star: 3–5 validation-ready PRDs by 2026-09-22,
~5 Anthony-hours/week, sprint shortlist, escalate-and-replan on drift.

## Prime directive

This system exists to OPEN UP idea exploration, not to filter it. Rigor is applied
at graduation and validation — never at capture. Capture must never bounce: a
two-word fragment is a valid capture.

## Autonomy rule (applies to every agent, every session)

**Prep-only between meetings.** Agents may read, analyze, draft, and queue at any
time. Agents may NOT change facts without Anthony: no pipeline stage transitions,
no parking, no playbook edits. Anthony arrives to prepared work, never to changed
state. The only exceptions are explicit commands from Anthony (e.g. /graduate, /park)
and the **low-risk workflow-improvement carve-out**: during the pre-meeting review,
the CoS may implement workflow changes that pass the low-risk rubric in its playbook
(reversible, no judgment-behavior change, no data/state touch, no new spend), each
committed separately and logged in playbook-changelog.md. The CoS also holds a
standing **workforce-upkeep grant** (Anthony, 2026-08-22): continuous playbook
maintenance to improve performance and coordination of existing abilities —
sharpening roles, tightening handoffs, propagating Anthony's decisions — but never
changing team structure, decision rights, autonomy, or tool access without him.
Everything else goes on the meeting agenda with potential impact. Pipeline data and
the prime directive are never in scope.

## Pipeline

captured → exploring → graduated → validation-ready → mvp (future)
Plus: **parked** — reachable from any stage, never deletable, always revivable.
Parking requires a written reason AND revival criteria. Parked items get a fresh
look monthly at the staff meeting.

Stage lives in each painpoint file's frontmatter (`status:`). One file per
painpoint in `painpoints/`, named `pp-YYYY-MM-DD-<slug>.md`, from
`templates/painpoint.md`.

## The staff

| Name | Agent (.claude/agents/) | Job |
|---|---|---|
| **Iris** | chief-of-staff | Pipeline bookkeeping, meetings, nominations, judgment calls; emits `queue.md` (the single priority source) |
| **Echo** | intake | Extract structure from free-form dumps (sessions + `inbox/`, processed by cloud routine every 3h); never evaluates merit |
| **Socrates** | brainstorm-assistant | The questioner, both directions: non-leading brainstorms with Anthony + interview kits and synthesis for his real-user conversations |
| **Athena** | prd-author | Problem science: root-cause PRD at graduation, then experiment design and readouts against its assumptions register (readouts need Argus co-sign) |
| **Hephaestus** | rapid-prototyper | Sprint captain: Anthony-approved PRD → deployed, credibly-designed MVP in 48h via `sprint.md`; never self-initiates |
| **Argus** | test-writer-fixer | Independent verification: critical-path tests during builds + co-signs every experiment readout; never self-triggers |

Consolidated 2026-08-22 (Anthony's approval): Apollo→Hephaestus, Metis→Athena,
Psyche→Socrates. Rehire trigger: if validation feedback is about polish/jank
rather than the idea, Iris proposes a dedicated designer rehire at the next
meeting. Retired playbooks recoverable from git history.

Hiring history and review findings: `hiring/ONBOARDING.md`.

## Commands

- `/capture <dump>` — ingest a free-form painpoint dump (also processes `inbox/`)
- `/brainstorm <painpoint-id>` — open a brainstorming session
- `/meeting` — convene a staff meeting (uses the latest pack in `meetings/` if present)
- `/graduate <painpoint-id>` — Anthony's graduation decision; triggers the PRD deep dive
- `/park <painpoint-id>` — park with reason + revival criteria (CoS drafts, Anthony confirms)
- `/build <prd-id>` — Anthony approves a PRD for build: starts the 48h SLA clock,
  creates `sprint.md`, scaffolds `~/Projects/mvp-<slug>` (MVPs never live in this repo)

## Coordination surfaces

- `queue.md` — Iris's prioritized open questions; the dashboard renders it verbatim
- `sprint.md` — live build task ledger (from `templates/sprint.md`); Hephaestus captains it
- `escalations/` — sprint SLA risk flags. (No auto-alert since 2026-08-25 — the
  Telegram notifier was removed with the rest of the bot; Anthony reviews these in
  sessions and meetings.)

## Self-improvement

1. **Playbook retros** — every meeting ends with the CoS proposing concrete diffs to
   `.claude/agents/*.md`. Anthony approves at the meeting. Every applied change gets
   a dated entry in `playbook-changelog.md` (what changed, why, evidence).
2. **Taste profile** — every graduate/park/revive decision appends Anthony's stated
   reason to `taste-profile.md`. Agents use it for ORDERING AND EMPHASIS ONLY —
   it must never suppress an idea before Anthony sees it.

## Cadence & executors (America/Chicago)

- Dashboard — rebuilt (`scripts/build_dashboard.py`) and republished by a cloud routine
  to the Idea Loop Dashboard artifact on every push to main (GitHub-App webhook) plus
  a daily 7:45 AM safety-net run:
  https://claude.ai/code/artifact/52faa5a2-a3cf-47c5-b5dd-963c1543149a
- **Staff meetings: no scheduled cadence** (Anthony cancelled all scheduled staff
  meetings and morning reminders, 2026-08-25). `/meeting` remains available purely
  on demand — when convened without a pack in `meetings/`, the CoS builds one at
  the start of the session. Nothing prompts or summons Anthony.
- **Telegram/Iris bot removed entirely 2026-08-25 at Anthony's request** (daily
  digest, /interviewme, Mac daemon, escalation alerts, meeting summons — all
  workflows and scripts deleted; recoverable from git history if ever revived).
  Iris the CoS agent still runs inside Claude Code sessions; she just has no
  messaging channel to Anthony.

**Sync discipline (required because executors share state via GitHub):**
- Start every session with `git pull` — cloud executors (intake, dashboard) share
  state via main.
- Commit and push at the end of any session that changes pipeline state; the cloud
  can only see what's on main.

## House rules

- Secrets live in `.env` (gitignored). Never commit tokens.
- Frontmatter is the source of truth for pipeline state; the dashboard is a
  rendering of it, never an input.
- Dates in files are absolute (YYYY-MM-DD), never "yesterday".
