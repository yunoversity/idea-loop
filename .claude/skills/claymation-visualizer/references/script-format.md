# Shot Script Format

Two artifacts, same content: `script.md` (for humans) and `script.json` (drives
generation and the edit). Timecodes always come from `beatmap.json` downbeats —
never rounded by hand.

## script.json schema

```json
{
  "project": "viz-neon-sunrise",
  "source_audio": "source/neon-sunrise.mp3",
  "style_block": "<the frozen style block, verbatim>",
  "characters": {
    "BLOB": "BLOB — a fist-sized terracotta-orange clay sphere with two white googly eyes and a thumbprint dent on its left side."
  },
  "shots": [
    {
      "id": "shot-01",
      "section": 0,
      "start": 0.0,
      "end": 4.31,
      "cast": ["BLOB"],
      "still_prompt": "<style block> + <cast lines> + framing: BLOB centered on the paper sweep, tabletop level, lots of negative space.",
      "motion_prompt": "<style block> + BLOB idle-jiggles like gelatin, breathing slowly, one lazy blink. Subtle, low energy, no displacement.",
      "squish_cue": "jiggle",
      "energy": "low"
    }
  ]
}
```

## Rules

- `start`/`end` are exact downbeat times from the beatmap. A shot spans a whole
  number of bars (typically 1–2 bars; 2–8 seconds at most tempos).
- Every shot's `motion_prompt` names a squish cue from the style bible grammar
  and ties it to the beat ("squashes hard on each downbeat, four times").
- `energy` copies the section's intensity from beatmap.json and must match the
  cue: low→jiggle/morph, mid→bounce, high→full-squash, the drop→splat-reform.
- The biggest downbeat of the track (highest onset strength) gets the
  `splat-reform` hero shot. Find it before writing anything else and build the
  script's arc toward it.
- Cast is limited to the character sheet. A new character mid-script is a
  consistency bug, not creativity.

## script.md

Same shots as a table for Anthony's review:

| # | Time | Bars | Cast | Cue | What happens |
|---|---|---|---|---|---|
| 01 | 0:00.0–0:04.3 | 1–2 | BLOB | jiggle | BLOB breathes on empty sweep |
| 02 | 0:04.3–0:08.6 | 3–4 | BLOB, WORM | bounce | WORM inchworms in, both bounce on beats |

Under the table, note the arc in two sentences (where it builds, where the
splat-reform lands) so the script is reviewable without reading JSON.
