---
name: claymation-visualizer
description: >
  Turn a music clip into a claymation music visualizer video. Agentic pipeline:
  analyze the audio for beats/energy, write a beat-synced shot script, generate
  consistent squishy clay shots (keyframe stills → image-to-video), then edit
  everything together against the beatmap. Use when Anthony provides a music
  file and asks for a visualizer, claymation video, or music video.
---

# Claymation Music Visualizer

Input: a music clip (mp3/wav/m4a) + optional vibe notes.
Output: a beat-synced claymation video with the original track as audio.

Two hard constraints drive every phase:

1. **Consistent squish.** Every shot obeys the same clay physics and the same
   visual style. Consistency comes from process (keyframe-first, verbatim style
   block, character sheet), not from hoping the model stays on-model.
   Read `references/style-bible.md` before writing a single prompt.
2. **Script before edit.** The shot script is the contract. It is written
   against the beatmap *before* any generation, and the final edit is assembled
   *from* it. Nothing is generated that isn't in the script; nothing lands on
   the timeline off-beat.
3. **Sync is layered, not literal.** Cuts live on the phrase/bar grid; beats
   between cuts are hit by squish *inside* the running shot; texture rides the
   hats. Read `references/edit-craft.md` (AMV + visualizer craft) before
   writing the script — it governs cut rate, anticipation, continuity, and
   the effects budget.

Tool/model recommendations and API setup: `references/tools.md`.
Script format and worked example: `references/script-format.md`.

## Workspace

Media never lives in this repo (house rule). Create a project workspace:

```
~/Projects/viz-<slug>/
  source/<clip>          # the input music file
  beatmap.json           # phase 1 output
  brief.md               # creative brief + this video's style bible instance
  script.md              # human-readable shot script
  script.json            # machine-readable shot list (drives generation + edit)
  stills/shot-NN.png     # phase 3 keyframes
  clips/shot-NN.mp4      # phase 4 animated shots
  edl.json               # edit decision list (drives assemble.py)
  out/visualizer.mp4     # final render
  qc/contact-sheet.png   # QC montage
```

## Phase 1 — Analyze the audio

```
python3 scripts/claymation/analyze_audio.py <clip> -o ~/Projects/viz-<slug>/beatmap.json
```

Produces tempo, beat/downbeat times, and energy-labeled sections. Sections are
the video's scenes; downbeats are the cut grid. Sanity-check the BPM (halved or
doubled tempo is the classic failure — if cuts would land every 0.25s or every
4s, re-run with `--bpm-hint`).

## Phase 2 — Brief + script

Write `brief.md`: one paragraph of concept (what shapes/characters, what world),
the **frozen style block** (copy the template from the style bible, fill in
palette and materials, then never edit it again), and a character sheet (2–4
recurring shapes, each with a one-line description reused verbatim in prompts).

Then write the shot script per `references/script-format.md`, applying
edit-craft.md:
- **Cut grid**: cuts land on `phrases`/`downbeats` from the beatmap — every
  2+ bars in low sections, 1–2 bars mid, beat-rate only in the final build.
  Shots always **start and end on the grid**. Beats between cuts are expressed
  by squish inside the shot, never by more cuts.
- Each shot gets: timecodes, a still prompt (style block + character +
  framing), a motion prompt (what squishes, when, how hard — with the wind-up
  *before* each impact spelled out, mapped to the section's `bands`:
  low→squash amplitude, mid→color/morph pace, high→jiggle frequency), a
  squish cue, and a `motion_dir` for screen-direction continuity with its
  neighbors.
- **Arc**: accelerate cut rate into the drop, place the one `splat-reform`
  hero at `peak_downbeat`, then a 2-bar+ breather shot. Escalate playfulness
  with energy: low = idle wobble and slow morphs; peak = shapes trampolining,
  merging, splattering and reforming.

Show Anthony the script before spending generation credits if he's present;
if running autonomously, proceed but keep the script as the reviewable record.

## Phase 3 — Keyframe stills

For each shot, generate one still (the first frame) with an image model, using
the frozen style block verbatim + the character sheet lines + the shot's
framing. Reuse the same seed family / style reference across all shots (see
tools.md for per-provider mechanics). Reject and re-roll any still that breaks
palette, material, or character design — it is 10x cheaper to fix consistency
here than after animation.

## Phase 4 — Animate

For each still, run image-to-video with the shot's motion prompt. Request
~1s more than the shot's script duration (trim margin — you will need it to
place the impact, see Phase 5). Motion prompts describe the anticipation
explicitly ("stretches tall, then slams into a full squash") and loop in
bar-length cycles so uncut stretches stay locked to the grid. Kling and Veo
handle squash-and-stretch physics best; see tools.md. Save as
`clips/shot-NN.mp4`.

**Zero-key fallback:** if no `FAL_KEY`/`REPLICATE_API_TOKEN` is in `.env`, stop
here and deliver the *prompt pack*: brief.md + script.md with every still and
motion prompt ready to paste into a web UI. Do not sign up for anything — new
spend is Anthony's call.

## Phase 5 — Assemble

Build `edl.json` (schema in `scripts/claymation/assemble.py` docstring): each
shot's file, its trim-in point, and its script timecodes — snapped to actual
beatmap downbeats, not to rounded numbers. Two craft steps here:

- **Trim for impact**: for impact shots, scrub the clip, find the frame where
  the squash lands, and set `in` so that frame falls on the shot's first
  internal downbeat. This trim IS the sync; `in: 0` is only for jiggle shots.
- **Effects budget**: `punch` (3–6% push-in) on high-energy shots only, never
  two adjacent; `flashes` on at most 3–4 of the biggest low-band hits,
  always including `peak_downbeat`.

Then:

```
python3 scripts/claymation/assemble.py ~/Projects/viz-<slug>/edl.json
```

The assembler trims each clip, renders at 12fps (stop-motion cadence — this is
what makes AI video read as claymation instead of CGI), hard-cuts on the
downbeat grid, concatenates, and muxes the original track. Cuts must land
within one frame (~83ms at 12fps) of a downbeat.

## Phase 6 — QC and iterate

Extract a frame per shot into a contact sheet (`ffmpeg` thumbnail per clip,
tile with the montage step in assemble.py `--contact-sheet`). Check against the
style bible: palette drift, material drift (clay → rubber/CGI is the common
failure), character drift, dead shots with no squish. Then run both edit-craft
screenings: the **mute test** (does the cut flow carry without audio?) and the
**sync test** (every impact within one frame of its beat — almost-synced is
worse than unsynced; fix the `in` trim). Regenerate only the failing shots
(Phase 3→4 for just those), rebuild, and deliver `out/visualizer.mp4`. For a human polish pass (titles, grade, captions), hand
the clips + script.md to an AI editor per tools.md — the script maps 1:1 onto
a Descript/Runway timeline.
