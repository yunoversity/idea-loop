# Idea Loop — Operating Manual

A self-improving business-idea brainstorming workflow. A Chief of Staff (CoS) agent
owns the pipeline's momentum; Anthony owns every decision.

Full requirements spec: https://claude.ai/code/artifact/fb275a50-8de2-4482-a31e-71c66eaefee6

## Prime directive

This system exists to OPEN UP idea exploration, not to filter it. Rigor is applied
at graduation and validation — never at capture. Capture must never bounce: a
two-word fragment is a valid capture.

## Autonomy rule (applies to every agent, every session)

**Prep-only between meetings.** Agents may read, analyze, draft, and queue at any
time. Agents may NOT change facts without Anthony: no pipeline stage transitions,
no parking, no playbook edits. Anthony arrives to prepared work, never to changed
state. The only exceptions are explicit commands from Anthony (e.g. /graduate, /park).

## Pipeline

captured → exploring → graduated → validation-ready → mvp (future)
Plus: **parked** — reachable from any stage, never deletable, always revivable.
Parking requires a written reason AND revival criteria. Parked items get a fresh
look monthly at the staff meeting.

Stage lives in each painpoint file's frontmatter (`status:`). One file per
painpoint in `painpoints/`, named `pp-YYYY-MM-DD-<slug>.md`, from
`templates/painpoint.md`.

## The staff

| Agent (.claude/agents/) | Job |
|---|---|
| chief-of-staff | Pipeline bookkeeping, meetings, nominations, judgment calls, digest content |
| intake | Extract structure from free-form dumps (sessions + `inbox/`); never evaluates merit |
| brainstorm-assistant | Open-ended, non-leading questions on `exploring` painpoints |
| prd-author | Root-cause deep dive → PRD in `prd/`, runs only at graduation |

## Commands

- `/capture <dump>` — ingest a free-form painpoint dump (also processes `inbox/`)
- `/brainstorm <painpoint-id>` — open a brainstorming session
- `/meeting` — convene a staff meeting (uses the latest pack in `meetings/` if present)
- `/graduate <painpoint-id>` — Anthony's graduation decision; triggers the PRD deep dive
- `/park <painpoint-id>` — park with reason + revival criteria (CoS drafts, Anthony confirms)

## Self-improvement

1. **Playbook retros** — every meeting ends with the CoS proposing concrete diffs to
   `.claude/agents/*.md`. Anthony approves at the meeting. Every applied change gets
   a dated entry in `playbook-changelog.md` (what changed, why, evidence).
2. **Taste profile** — every graduate/park/revive decision appends Anthony's stated
   reason to `taste-profile.md`. Agents use it for ORDERING AND EMPHASIS ONLY —
   it must never suppress an idea before Anthony sees it.

## Cadence & executors (America/Chicago)

- Daily 8:00 AM — Telegram digest of top ≤3 open questions. Runs in **GitHub Actions**
  (`.github/workflows/telegram-digest.yml`), reading painpoints from the repo's main branch.
- Live conversation — the **Iris daemon** (`scripts/iris_daemon.py`, launchd service
  `com.iris.daemon` on Anthony's Mac) long-polls Telegram: /help /status /questions
  answered by script; other messages are filed to `inbox/` (committed+pushed) AND
  answered conversationally by read-only headless Claude. Iris cannot write via
  Telegram — state changes happen only in Claude Code sessions or meetings.
  When the Mac sleeps, Telegram queues messages (~24h) and the daemon catches up on
  wake; `.github/workflows/telegram-poll.yml` remains as a manual-dispatch fallback.
- Friday 8:00 AM — a scheduled cloud Claude agent builds the weekly meeting pack
  (per the chief-of-staff playbook, sections 1–6 pre-filled, Decisions empty),
  commits it to `meetings/`; a push-triggered Action sends the Telegram summons.
  Anthony convenes with `/meeting`.
- The bot is Iris (@Iris_CoSbot); it only talks to Anthony's chat ID.

**Sync discipline (required because executors share state via GitHub):**
- Start every session with `git pull` — inbox messages and meeting packs arrive via Actions.
- Commit and push at the end of any session that changes pipeline state; the cloud
  can only see what's on main.

## House rules

- Secrets live in `.env` (gitignored). Never commit tokens. The Telegram bot only
  talks to Anthony's chat ID (`TELEGRAM_CHAT_ID` in .env).
- Frontmatter is the source of truth for pipeline state; the dashboard is a
  rendering of it, never an input.
- Dates in files are absolute (YYYY-MM-DD), never "yesterday".
