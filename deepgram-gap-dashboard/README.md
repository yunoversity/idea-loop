# Aura-2 Gap Dashboard

Static site: problem-statement header, interactive coverage heatmap (any X × Y of accent, gender, age, use case, tone), 1–5 gap scoring (market demand, enterprise fit, difficulty to source), stack-ranked gaps, and a Deepgram TTS speech lab.

```bash
python3 serve.py                          # browser-key mode, http://127.0.0.1:8770
DEEPGRAM_API_KEY=... python3 serve.py     # key stays server-side (proxy at /api/speak)
```

- Data: `data/voices.js` (41 English Aura-2 voices, catalog snapshot 2026-10-05).
- Source material: Drive folder `deepgram-casestudy` (problem statement, gap definition G1).
- Scores and weights persist in the browser's localStorage. The scoring formula is in the page footnote.
- "Illustrative scores" are placeholders, not research. Accent/use-case/tone values marked "not in catalog" are hypotheses.
