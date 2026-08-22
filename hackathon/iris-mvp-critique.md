# Iris critique — Warm Path MVP as delivered (2026-08-22)

Reviewed the built product, not the pitch. Direct but constructive, per
working-style.md.

## What the team got right

- **The cap survived contact with code.** Argus caught the deck refilling after
  both cards were spent — which would have turned the anti-treadmill product
  into a treadmill. Found by actually using the thing, not by reading it. That
  catch alone justifies keeping verification independent of the builder.
- **The hard rules are structural, not aspirational.** There is no generation
  code and no network call in the repo. "Never writes, never sends, never
  scrapes" isn't a promise in the footer — it's the absence of capability.
- **The hook mechanic is the right bet.** A fresh hook on an acquaintance
  outranking a close friend with no reason is the product's whole thesis
  (timeliness = attention = the costly signal), and it's implemented exactly
  that way.
- **Honest gaps are published, not buried** — manual hooks, single-browser,
  guessed weights, untested DOM layer. That's the standard I want on every
  build.

## Where I'd push back

1. **Delivered at hour 0.75 of 48 — treat that as a warning, not a trophy.**
   The scope was thin enough to build in an afternoon, which means the SLA was
   never tested. Do not conclude from this that 48 hours is comfortable; the
   next build (Dossier) has real research plumbing and will use the window.
2. **"Two a day" is now enforced but unproven as a value.** It may read as
   paternalistic to a motivated user on a good day. Watch for pilots wanting a
   third card — that's a finding, not a feature request to reflexively grant.
3. **Snooze spends a card.** Deliberate (otherwise you can skip-scroll your list),
   but it's the most likely source of pilot frustration. Instrument it: if
   snooze rate is high, the ranking is wrong, not the user.
4. **The baseline is self-reported and entered after the fact** — pilots will
   flatter themselves or lowball. Athena should have both pilots write their
   baseline down *before* opening the app tomorrow. Otherwise A2's headline
   number is soft.
5. **No arms-length tester yet.** Both pilots are close to Anthony. A2/A6
   (behavior) survive that bias reasonably; anything about reception does not.

## Callout (standing authority)

**None against the build.** One against a plausible next move: do not add a
"draft the message for me" button when pilots ask for it — and they will, in
week one. That request is the single fastest way to convert this product into
the templated-outreach problem it was built to route around. If message help is
wanted, it arrives as Red Pen's critique surface, never as generation.

## Recommended next steps

1. **Tonight/tomorrow:** both pilots record their honest pre-Warm-Path weekly
   outreach baseline in writing, then load 15–30 real contacts.
2. **Days 1–7:** use it. No reminders from me after day 2 — silence is data
   for A6.
3. **Day 7:** export JSON → Athena drafts the readout → Argus co-signs → decision.
4. **In parallel (free, no build):** the A3 desk test for Dossier — 10 real
   targets, count usable research material. If it passes, Dossier is the second
   build and Red Pen's rules fold into it.
5. **Recruit one arms-length tester** this week, before reception claims matter.

— Iris
