# WARM PATH — kill the treadmill, one real step a day

Idea-loop hackathon · Demo C · pp-24 (cold-apply fatigue)
Constraint set C: **no message content at all.** Goal: make real outreach the lowest-friction next action of the day.

---

## The pain, in the pilots' words

- Cold applying "feels like progress without results" — the treadmill wins every tired evening
- Coffee chats are rare not because outreach fails, but because it rarely happens
- Burnout math: disengaging day job + search = no energy for the high-courage channel

---

## The root cause this demo attacks

**Emotional asymmetry (R4).** The false-progress channel wins because it's always the easier next step. Warm Path doesn't make outreach better — it makes it *smaller*: one warm, timely, pre-justified step per day.

---

## What it is

You import your own contacts (your export, your memory — nothing scraped). Warm Path maintains:

- **Warmth ranking:** your list ordered by relationship warmth × freshness of common ground
- **Why-now hooks:** "Maya just posted about their platform migration — this week, not next month"
- **The Daily Two:** each morning, two names max, each with its hook and history
- **Progress that's real:** streaks count conversations started, not applications fired into the void

**It never writes, never sends, never scrapes. It decides nothing — it sequences.**

---

## Demo walkthrough (storyboard — nothing built)

1. Kevin imports 60 contacts from his own address book export + memory prompts
2. Morning card: "Today: Priya (ex-teammate, just changed companies — congratulate) and Sam (met at PyCon, his talk got posted this week)"
3. Kevin marks Priya "reached out" — the card logs it and schedules the follow-up nudge
4. Friday view: 8 real outreaches this week vs. his old 0 — and 2 coffee chats booked

---

## Why this preserves genuineness

- The message is 100% the human's — the tool never sees it
- Timeliness is itself a genuineness signal ("saw your post this week" beats "hope this finds you well")
- Small daily asks lower the courage threshold — R4 attacked at the behavioral root

---

## Assumptions tested (Athena) · verification (Argus)

- **A2 (bottleneck):** THE decisive test — if sequencing alone lifts outreach volume, the block was activation energy, not craft
- **A6 (workflow fit):** unprompted use ≥3 days in week 1
- **A5 (conversion):** chats booked per 10 outreaches vs. near-zero baseline
- Argus gate: "reached out" self-reports need spot-verification against actual sent messages

---

## 48-hour build shape (Hephaestus — feasibility only)

- Hour 0–4: deployed app with contact import (CSV/manual) + local storage
- Hour 4–24: warmth ranking heuristic + Daily Two view; hook capture is MANUAL at MVP (user pastes the trigger they saw) — automated hook detection is post-validation
- Hour 24–40: streaks, follow-up nudges; Argus tests on the ranking logic
- Hour 40–48: pilot-ready; instrumentation = daily opens, outreaches marked, chats booked
- Honest risk: manual hooks may be the feature users skip — watch it specifically

---

## Risks & open questions (Iris)

- Attacks behavior, not skill: pairs naturally with A or B later — but tonight it competes alone
- Manual hook entry at MVP undercuts the "why-now" magic; automated hooks without scraping is an unsolved design question
- Habit products live or die in week 2 — a 1-week pilot window may flatter it
- Contact import UX is the whole first impression; a tedious import loses both pilots by hour 1

---

## Evaluate this demo on

1. Did the Daily Two actually happen on your hardest workday?
2. Does progress-that's-real beat the cold-apply dopamine?
3. Would you still want A or B once this exists — or is sequencing the whole game?
