# RED PEN — the genuineness critic that never writes a word

Idea-loop hackathon · Demo B · pp-24 (cold-apply fatigue)
Constraint set B: **user writes first; AI only critiques.** Goal: raise the genuineness of messages hunters already write.

---

## The pain, in the pilots' words

- AI-templated messages backfire — hiring managers smell the template
- Hand-written messages work but each one is a small act of courage with no feedback loop
- You never learn WHY a message got ignored

---

## The root cause this demo attacks

**Costly-signal economics (R1), from the defense side.** If effort is the currency, the fatal failure is a message that *reads* cheaper than it was. Red Pen detects the tells — before the recipient does.

---

## What it is

Paste your draft (plus one line: who it's for). Red Pen returns margin notes, never rewrites:

- **Template tells:** "this sentence appears in ten thousand LinkedIn messages"
- **Ask-vs-interest meter:** flags every implicit request; is there any gift here?
- **Common-ground check:** "you never mention anything specific about THEM"
- **Research prompts:** "before sending — what did they ship last quarter? One specific reference would transform this"
- House rules honored: admiration capped at one sentence, no naming the prospect's problems, probing questions over asks

**It refuses to write. The red pen is the whole product.**

---

## Demo walkthrough (storyboard — nothing built)

1. Anthony pastes a real draft to a former colleague's new manager
2. Three margin flags: opening line = template tell; paragraph 2 contains a hidden ask; zero specific references to the recipient
3. One research prompt: "she gave a podcast interview last month — listen to 10 minutes"
4. Anthony revises — the diff view shows his own words improving, not AI words replacing his

---

## Why the output reads as genuine

- Nothing is generated, so nothing CAN read as templated
- The human's voice stays fully intact — the tool only removes the fake-sounding parts
- Teaches the skill permanently: after 20 critiques, the hunter internalizes the red pen

---

## Assumptions tested (Athena) · verification (Argus)

- **A1 (reception, via quality delta):** blind judges rate before/after drafts — majority prefer "after" without knowing which is which
- **A2 (bottleneck location):** if critiqued messages still don't get SENT more often, the block is courage, not craft — decisive evidence
- Argus gate: judge pool can't be only Anthony's friends; before/after order randomized

---

## 48-hour build shape (Hephaestus — feasibility only)

- Hour 0–4: paste-box app deployed; critique schema fixed
- Hour 4–24: critique engine tuned on the genuine-mechanics list + Anthony's outreach style rules
- Hour 24–40: calibration on real past messages from both pilots (with their permission); Argus tests
- Hour 40–48: pilot-ready; instrumentation = drafts in, revisions made, sends logged
- Honest risk: critique quality is the entire product — a generic critique kills trust in one use

---

## Risks & open questions (Iris)

- Smallest surface of the three demos — lowest build risk, but also lowest ceiling: it improves messages that get written, does nothing for the hunter who writes none
- Depends on the user already having a target and a reason — no help with WHO or WHEN
- Emotional exposure stays fully with the user (may be exactly right — or the reason it goes unused)

---

## Evaluate this demo on

1. Would a harsh critique make you send MORE messages or fewer?
2. Does refusing to write feel principled — or just unhelpful?
3. Is the teach-the-skill effect worth more than per-message help?
