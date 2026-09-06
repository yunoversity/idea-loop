# Claymation Style Bible

The consistency system. Every video gets its own *instance* of this (in
`brief.md`), but the physics grammar below is fixed — it's what makes the work
recognizably ours.

## The frozen style block

Every still prompt and every motion prompt includes this paragraph **verbatim**
(fill the two brackets once per project, then freeze):

> Handmade claymation stop-motion, plasticine with visible fingerprints and
> tool marks, matte clay surface with subtle sheen, tabletop diorama set,
> soft studio key light with gentle fill, shallow depth of field, 35mm look,
> palette strictly limited to [5 named colors], background of [set material,
> e.g. "butter-yellow paper sweep"]. Everything soft-edged and rounded,
> nothing glossy, nothing photoreal, no CGI smoothness.

Rules:
- **Never paraphrase it.** Prompt drift is style drift. Copy-paste only.
- Max 5 palette colors, named concretely ("terracotta orange", not "warm").
- One set material for the whole video. Scene variety comes from character
  arrangement and camera, not from new worlds.

## Squish grammar (the physics law)

Clay in this house obeys cartoon physics with conserved volume:

| Cue | What happens | When |
|---|---|---|
| `full-squash` | Squash to ~70% height, bulge ~130% wide, rebound overshoot to ~110% tall, settle in 2–3 bounces | Downbeats in high-energy sections |
| `bounce` | Land-squash-launch cycle, one cycle per beat | Mid-energy, rhythmic sections |
| `jiggle` | Whole-body gelatin wobble, no displacement | Offbeats, low-energy sections, held notes |
| `morph` | One shape kneads itself into another over 1–2 beats, never a hard transform | Section transitions |
| `splat-reform` | Shape splats flat against ground/camera, then reassembles | Drops, biggest downbeat of the track |

- Volume is conserved: whatever squashes down bulges out. This single rule is
  most of what makes squish read as clay.
- Gravity is slightly too strong and everything is slightly too bouncy.
- Nothing moves rigidly. Even "still" shapes breathe (idle jiggle).

## Playfulness rules

- Shapes are simple and friendly: blobs, worms, stacked spheres, wobbly towers.
  Googly eyes and stubby limbs allowed; realistic anatomy is not.
- Prefer morphs over cuts *within* a section; cuts belong on downbeats
  *between* shots.
- No hard edges, no menace, no photorealism. If a frame could be mistaken for
  render-farm CGI, it fails QC.

## Character sheet

2–4 recurring characters, each with a one-line spec reused verbatim, e.g.:

> BLOB — a fist-sized terracotta-orange clay sphere with two white googly eyes
> and a thumbprint dent on its left side.

The dent/asymmetry detail matters: a deliberate imperfection is the easiest
thing for image models to keep consistent and for QC to check.

## QC checklist (per shot)

1. Palette: only the 5 frozen colors present?
2. Material: still matte plasticine with fingerprints (not rubber, not glossy CGI)?
3. Characters: match their sheet lines, imperfections included?
4. Physics: volume conserved during squash? At least one squish cue visible?
5. Cadence: does motion read as stop-motion at 12fps (assembler enforces this)?
