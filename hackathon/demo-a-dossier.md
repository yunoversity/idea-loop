# DOSSIER — the research engine that makes them feel heard

Idea-loop hackathon · Demo A · pp-24 (cold-apply fatigue)
Constraint set A: **AI never touches the message.** Goal: maximize "feel heard" value-add from ToS-clean research.

---

## The pain, in the pilots' words

- Cold applying "feels like progress without results"
- Coffee chats are rare; asks arrive without value
- Hand-crafted outreach works — but the research per contact doesn't scale
- All of it stacked on a day job they're disengaged from, with burnout looming

---

## The root cause this demo attacks

**Research friction (R2).** The legitimate cost of genuine outreach — learning enough about a person to say something that matters — has no scaffolding. Dossier pays that cost for you, so your attention goes into the message, not the digging.

---

## What it is

You name a target (and paste any links you already have — their blog, talk, GitHub, company page). Dossier returns a one-page brief:

- **Their world:** recent work, public writing, talks, launches
- **Common ground candidates:** where your paths, stacks, or interests genuinely overlap
- **Three value-add angles**, one per mode: something delightful to share · something that shows you actually saw their work · something that makes their week easier
- **Two conversation-starter questions** (interest, never an ask)

**You write the message. Every word. The tool guarantees it has something real to say.**

---

## Demo walkthrough (storyboard — nothing built)

1. Kevin pastes "Jane Doe, Eng Manager @ Acme" + her conference talk link
2. 90 seconds later: the one-page brief, with her recent talk's core argument summarized and one overlap flagged ("you both migrated off k8s — she wrote about the pain")
3. Kevin writes 4 sentences himself, referencing the talk, asking one genuine question
4. Side panel: the three value-add angles he *didn't* use, saved for the follow-up

---

## Why the output reads as genuine

- The message is human because it IS human — zero generated prose
- Common connection area comes from real overlap, surfaced not invented
- Interest-not-ask enforced by what the brief supplies: questions, not requests
- The costly signal survives: the sender still spends attention — just on the right part

---

## Assumptions tested (Athena) · verification (Argus)

- **A3 (fuel exists):** ≥7 of 10 real targets yield a usable angle — *desk-testable before any build*
- **A4 (value-add producible):** blind readers judge briefed messages "genuine + valuable"
- **A1 (reception):** pilot messages vs. their own baseline response rate
- Argus gate: thresholds committed before pilots send anything

---

## 48-hour build shape (Hephaestus — feasibility only)

- Hour 0–4: single-page app deployed; input form + brief template
- Hour 4–24: research assembly from user-supplied links + permitted public sources; three-angle generator
- Hour 24–40: brief quality pass on 10 real targets; Argus smoke tests
- Hour 40–48: pilot-ready with instrumentation (briefs generated, messages sent, replies logged)
- Honest risk: brief quality varies with target's public footprint — degrade gracefully, never pad

---

## Risks & open questions (Iris)

- **A3 is still untested** — the afternoon desk test should precede any build vote
- Quiet targets (no public work) may return thin briefs: does the tool say "not enough signal" honestly?
- Pilot warmth bias: Strong reception labels need an arms-length tester
- Scope creep magnet: "just also draft the message" requests must be refused — that's Demo B's experiment, not this one

---

## Evaluate this demo on

1. Would YOU use it tomorrow for a real target?
2. Does the brief make the recipient feel heard — or just researched?
3. Is "human writes every word" a feature or a friction?
