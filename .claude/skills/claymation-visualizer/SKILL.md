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

Then write the shot script per `references/script-format.md`:
- One shot per section slice; shots are 2–8s and **start and end on downbeats**.
- Each shot gets: timecodes, a still prompt (style block + character + framing),
  a motion prompt (what squishes, when, how hard — mapped to that section's
  energy), and a squish cue (`full-squash` on downbeats for high energy,
  `jiggle` for low).
- Escalate playfulness with energy: low energy = idle wobble and slow morphs;
  peak energy = shapes trampolining, merging, splattering and reforming.

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
~1s more than the shot's script duration (trim margin). Kling and Veo handle
squash-and-stretch physics best; see tools.md. Save as `clips/shot-NN.mp4`.

**Zero-key fallback:** if no `FAL_KEY`/`REPLICATE_API_TOKEN` is in `.env`, stop
here and deliver the *prompt pack*: brief.md + script.md with every still and
motion prompt ready to paste into a web UI. Do not sign up for anything — new
spend is Anthony's call.

## Phase 5 — Assemble

Build `edl.json` (schema in `scripts/claymation/assemble.py` docstring): each
shot's file, its trim-in point, and its script timecodes — snapped to actual
beatmap downbeats, not to rounded numbers. Then:

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
failure), character drift, dead shots with no squish. Regenerate only the
failing shots (Phase 3→4 for just those), rebuild, and deliver
`out/visualizer.mp4`. For a human polish pass (titles, grade, captions), hand
the clips + script.md to an AI editor per tools.md — the script maps 1:1 onto
a Descript/Runway timeline.
