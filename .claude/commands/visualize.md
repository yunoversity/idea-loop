---
description: Make a claymation music visualizer from a music clip (script → generate → beat-synced edit)
---

Use the **claymation-visualizer** skill (.claude/skills/claymation-visualizer/SKILL.md)
to turn the given music clip into a claymation visualizer video. Follow its
phases in order: beatmap → brief + shot script → keyframe stills → animate →
assemble → QC. Read the style bible before writing any prompt; the frozen
style block and squish grammar are non-negotiable. If no generation API keys
are configured in .env, stop after the script phase and deliver the prompt
pack — never sign up for new services without Anthony.

Input (path to music clip, plus any vibe notes):
$ARGUMENTS
