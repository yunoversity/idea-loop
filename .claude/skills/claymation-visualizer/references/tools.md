# Tool Stack & Connections

What to connect for best results, in priority order. House rule applies: keys
live in `.env` (gitignored), and any *new* paid signup is Anthony's decision —
the pipeline degrades gracefully to the prompt-pack fallback without keys.

## 1. Generation gateway (the one connection that matters most)

Use a model aggregator so one API key covers stills + video, and models can be
swapped per shot without new integrations:

- **fal.ai** (recommended): fastest inference, strong video catalog (Kling 2.5
  Turbo, Veo, Wan 2.2, Hailuo 02, Flux image models). Key as `FAL_KEY` in
  `.env`; plain HTTPS API (`https://fal.run/<model>`), and fal ships an MCP
  server if we want tool-native access (`claude mcp add` it — verify the
  current package name in fal's docs before installing).
- **Replicate** (alternate): broadest catalog, same shape. `REPLICATE_API_TOKEN`.

Direct-to-vendor (Runway API, Luma API) only if a specific model earns it —
each is another account, key, and billing surface.

## 2. Model choices per phase

| Phase | First choice | Why | Backup |
|---|---|---|---|
| Keyframe stills | **Flux 1.1 Pro w/ style reference** (via gateway) | Style-reference input keeps the clay look locked across shots | Ideogram; Midjourney (manual, has omni-reference) |
| Still consistency edits | **Gemini image editing ("Nano Banana")** | Best at "same character, new pose" edits — regenerates a drifted shot without re-rolling style | Flux Redux |
| Image-to-video | **Kling 2.5** | Best squash-and-stretch physics of the current crop; obeys "squashes on the beat" motion prompts | Veo 3.1 (prompt adherence; disable native audio), Runway Gen-4 Turbo (best style refs), Hailuo 02 |

## 3. Audio analysis — local and free

- **librosa** + **ffmpeg** (what `scripts/claymation/analyze_audio.py` uses):
  `pip install librosa soundfile`. Good beats, tempo, energy, sections.
- If downbeat detection proves weak on real tracks: **madmom** (RNN downbeat
  tracker) is the upgrade. Don't start there; librosa + the `--bpm-hint` flag
  covers most clips.

## 4. Editing / assembly

- **ffmpeg via `scripts/claymation/assemble.py`** — the deterministic default.
  Beat-snapped hard cuts, 12fps clay cadence, audio mux. An agent can drive it
  end-to-end with zero accounts. Always run this first; everything below is a
  polish layer on top of its output.
- **Remotion** — when we want programmatic motion graphics (beat-driven zoom
  pulses, wobble titles): the edit is React code, so the agent *writes* the
  edit and it renders deterministically. Best agent-native "AI editor".
- **Descript** — best human-polish AI editor for this workflow because it is
  script-driven: our script.md maps 1:1 onto its timeline; good for titles,
  cleanup, social crops.
- **Runway** — if we're already generating there, its timeline keeps
  generate→edit in one place.
- **Shotstack / JSON2Video** — cloud render from a JSON timeline (basically
  hosted edl.json) if we ever need this to run with no local ffmpeg.

## 5. Claude-side skills that pair well

- **canvas-design** — style-frame explorations / poster of the character sheet
  before spending video credits.
- **Artifact publish** — ship the contact sheet + script as a review page so
  Anthony can approve shots from his phone.

## Cost sanity

A 60s video at ~12 shots ≈ 12 stills + 12×5s video generations. On fal, budget
roughly a few dollars per full iteration — cheap enough to iterate the failing
shots, not cheap enough to regenerate the whole reel casually. QC stills
(Phase 3) before animating; that's where the money is saved.
