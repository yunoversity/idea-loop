# Edit Craft — Sync & Cutting Rules

Distilled from how good AMV editors and electronic-music visualizer artists
(Milkdrop/TouchDesigner lineage) actually work. These rules govern the shot
script (Phase 2), the motion prompts (Phase 4), and the EDL (Phase 5).

## 1. The sync hierarchy — not every beat is a cut

Sync operates on layers, biggest to smallest. Assign each layer a different
visual device instead of spending cuts on everything:

| Musical layer | Visual device |
|---|---|
| Structure (verse/build/drop) | Scene change: new arrangement, palette accent, energy state |
| Phrase (4 bars) | The **cut grid**. Default one cut per phrase or per bar — cuts land here |
| Bar (downbeat) | **Action sync inside the shot**: the squash impact, the landing, the splat |
| Beat | Bounce cycles, camera pulse |
| Subdivision (hats/texture) | Idle jiggle frequency, surface shimmer |

Machine-gunning a cut on every beat is the #1 amateur tell. Beats between
cuts are hit by motion *inside* the running shot — that's what the squish
grammar is for. `beatmap.json` provides `phrases` (every 4 downbeats) as the
default cut grid.

## 2. Cut economy and dynamic range

- **Vary shot length with energy**: low sections cut every 2+ bars, mid every
  1–2 bars, and only the last build before the drop earns beat-rate cutting.
- **Accelerate into the drop**: halve shot length each phrase of a riser
  (4 bars → 2 → 1 → beat-rate), then either slam to the longest shot of the
  video on the drop (the splat-reform hero) or keep the peak rate — never
  drift between the two.
- **Breathers are mandatory**: after the drop, at least one 2-bar+ shot.
  Constant intensity reads as noise; contrast is what makes the drop hit.
- Something always moves (idle jiggle at minimum), but maximum squish
  amplitude appears exactly once, at `peak_downbeat`. Spend your dynamic
  range like money.

## 3. Motion leads the beat (anticipation)

Impacts feel synced when they land ON the beat, which means the movement
starts BEFORE it. Clay grammar: wind-up (stretch tall / crouch) on the
"and" before the beat → impact squash exactly on the beat → 2–3 settle
bounces after.

- Phase 4: every motion prompt for an impact shot describes the wind-up
  explicitly ("stretches upward, then slams into a full squash").
- Phase 5: choose each shot's `in` trim so the generated impact frame lands
  on the shot's first internal downbeat — scrub the clip, find the impact,
  set `in = impact_time_in_clip - (first_downbeat - shot_start)`. This trim
  decision IS the sync; never default `in` to 0 for impact shots.

## 4. Continuity across cuts (flow)

Cuts feel clean when the eye doesn't have to relocate:

- **Screen direction**: a character exiting frame-right enters the next shot
  frame-left. Record it as `motion_dir` per shot and check adjacent pairs.
- **Match cuts on shape**: cut from sphere to sphere, tower to tower — or use
  the `morph` cue so the outgoing shape becomes the incoming one.
- **Eye-trace**: keep the subject in roughly the same frame region across a
  cut, or move it deliberately along the motion direction. Note framing in
  the still prompt ("subject left third") rather than always centering.
- Hard cuts are the default transition, full stop. Crossfades only in
  intro/outro/breakdown; never during rhythmic sections.

## 5. Frequency-band mapping (visualizer discipline)

Map bands to parameters, and keep at most 2–3 live mappings per section —
everything-reacts-to-everything is mud. Per-section `bands` and
`onset_density` come from `beatmap.json`:

| Band | Maps to |
|---|---|
| Low (kick/bass) | Squash amplitude, punch-in strength |
| Mid (melody/vocal) | Color accent within palette, vertical motion, morph pace |
| High (hats/texture) | Jiggle frequency, fine surface detail |

React fast, decay slow: impacts are instant, settles take 2–3 bounces.
Instant on/off flicker reads as strobing, not rhythm. In slow or vocal
sections, sync to the melody/vocal line instead of the kick — beat-hitting a
ballad section is the visualizer equivalent of machine-gun cuts.

## 6. Effects budget

- **Impact flashes** (1-frame white, EDL `flashes`): at most 3–4 in the whole
  video, on the biggest low-band hits only — always including
  `peak_downbeat`. More than that cheapens all of them.
- **Punch-ins** (EDL `punch`, a slow 3–6% push): high-energy shots only, and
  not on two adjacent shots — alternation is what keeps it alive.
- Loop motion in bar-length cycles (1/2/4 bars) so even uncut stretches feel
  locked to the grid.

## 7. The two QC screenings

Run both before delivering, in this order:

1. **Mute test** — watch with sound off. Does the edit still flow (shot
   variety, direction continuity, visible arc toward one climax)? If the
   video only works with audio, the cutting is carrying nothing.
2. **Sync test** — audio on, watching only for lag: every impact within one
   frame of its beat, no cut landing "almost" on a downbeat. Almost-synced
   is worse than unsynced; fix the trim, not the script.
