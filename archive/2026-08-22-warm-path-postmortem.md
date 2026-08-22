# Post-mortem — Warm Path MVP

Held 2026-08-22, Iris and Anthony. Build lifetime: ~2 hours from `/build` to
archive. Nothing deleted; repo, deployment, and tests remain intact.

## What happened

Anthony showed Warm Path to real people and got a **weak reaction** — no pull,
polite interest at best. The only written feedback before that was friction
with manual contact entry (fixed same day with LinkedIn export import). The
concept never earned a pilot week.

## Root cause — Anthony's read

1. **Cold-start cost too high.** Import the file, name your employers, add
   hooks — a pile of setup before the first card has any value. People bounce
   before they ever see the product work.
2. **It doesn't solve the hard part.** Warm Path answered *who* and *when* and
   deliberately refused to touch *what to say*. That refusal was the design
   thesis. Real reactions say the "what to say" is where the pain actually
   lives — the part we routed around is the product.

## What Iris got wrong

- **I recommended C-first on a sequencing argument** ("does outreach happen at
  all?") and treated the who/when layer as the decisive unknown. The weak
  reaction suggests the funnel layers aren't independent: nobody wants a
  who/when tool *by itself*, so testing that layer alone couldn't produce
  enthusiasm regardless of execution quality.
- **I optimized the experiment, not the product.** C was the cleanest test.
  Clean tests of an offer nobody wants still return "no."
- **The hour-0.75 delivery flattered us.** I flagged it as a warning at the
  time; it was actually the tell. Scope that cheap should have prompted "why is
  this so easy to build?" — the answer is that it doesn't do the hard thing.

## What went right (keep these)

- The 48h machine works: PRD → deployed, tested, instrumented product in under
  an hour of wall-clock build time.
- Argus's independence paid for itself — the deck-refill bug was a spec
  violation caught by using the product, not reading it.
- Total cost of learning this: one afternoon and zero dollars. Archiving
  without sunk-cost argument is the system working.
- Honest artifacts throughout: published gaps, labeled guesses, no invented
  evidence.

## Decisions

- **Warm Path MVP: archived.** No agent resumes work without Anthony's explicit
  instruction.
- **pp-24: parked**, with revival criteria (below). The problem is real and
  well-evidenced; the solution shape was wrong and the next attempt needs
  evidence, not another build.
- **New standing rule (Anthony): cold-start under 60 seconds.** Any future MVP
  must deliver visible value within a minute, with zero setup, or it does not
  ship. Propagated into Hephaestus's playbook.

## Revival criteria for pp-24

Any ONE of these reopens it:
1. A hunter unprompted asks for help with *what to say* (not who/when) —
   confirms the pain lives in the message, and points at Dossier or Red Pen.
2. The A3 desk test passes (≥7 of 10 real targets yield genuine value-add
   research material) AND a hunter says they'd use a research brief on their
   hardest day.
3. Someone shows a workaround they built themselves for outreach research —
   the strongest possible demand signal.
4. Anthony's own search makes the pain acute enough that he wants the tool for
   himself, this week.

## Open question Iris still has

Was the weak reaction about *this product* or about *being shown a tool at all*?
A person reacting to a demo is not the same as a person in the middle of a
draining search at 9pm. Worth remembering before concluding the underlying
painpoint is weak — the parking record says the problem stays credible.

— Iris
