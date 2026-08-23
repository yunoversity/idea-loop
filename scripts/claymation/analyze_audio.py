#!/usr/bin/env python3
"""Analyze a music clip into a beatmap for the claymation visualizer.

Usage:
    python3 scripts/claymation/analyze_audio.py song.mp3 -o beatmap.json
    python3 scripts/claymation/analyze_audio.py song.mp3 --bpm-hint 120

Output (beatmap.json):
    duration, bpm, beats[], downbeats[], phrases[] (every 4 downbeats — the
    default cut grid), peak_downbeat, and sections[] with per-section
    energy/brightness, low/mid/high band energies, onset density, and an
    intensity label (low|mid|high). See references/edit-craft.md for how the
    script maps these to cuts and squish.

Requires: pip install librosa soundfile
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clip", help="music file (mp3/wav/m4a/...)")
    ap.add_argument("-o", "--out", default="beatmap.json")
    ap.add_argument("--bpm-hint", type=float, default=None,
                    help="nudge the tempo tracker (fixes halved/doubled BPM)")
    ap.add_argument("--bars", type=int, default=4,
                    help="beats per bar for downbeat grid (default 4)")
    args = ap.parse_args()

    try:
        import librosa
        import numpy as np
    except ImportError:
        print("Missing deps — run: pip install librosa soundfile", file=sys.stderr)
        return 1

    clip = Path(args.clip)
    if not clip.exists():
        print(f"No such file: {clip}", file=sys.stderr)
        return 1

    y, sr = librosa.load(str(clip), sr=22050, mono=True)
    duration = float(len(y) / sr)

    kwargs = {"start_bpm": args.bpm_hint} if args.bpm_hint else {}
    tempo, beat_times = librosa.beat.beat_track(y=y, sr=sr, units="time", **kwargs)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_times = [float(t) for t in beat_times]
    if len(beat_times) < args.bars * 2:
        print("Too few beats detected — clip too short or beat tracking failed.",
              file=sys.stderr)
        return 1

    # Downbeats: pick the bar phase whose beats carry the most onset energy.
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    times = librosa.times_like(onset_env, sr=sr)

    def strength_at(t: float) -> float:
        return float(onset_env[np.argmin(np.abs(times - t))])

    phases = [sum(strength_at(t) for t in beat_times[p::args.bars])
              for p in range(args.bars)]
    phase = int(np.argmax(phases))
    downbeats = beat_times[phase::args.bars]
    peak_downbeat = max(downbeats, key=strength_at)

    # Sections: agglomerative segmentation on beat-synced MFCCs, boundaries
    # snapped to downbeats. Aim for a scene every ~12s, clamped to 3..12.
    n_sections = int(np.clip(round(duration / 12), 3, 12))
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    beat_frames = librosa.time_to_frames(beat_times, sr=sr)
    beat_frames = np.clip(beat_frames, 0, mfcc.shape[1] - 1)
    sync = librosa.util.sync(mfcc, beat_frames)
    n_sections = min(n_sections, sync.shape[1])
    bounds = librosa.segment.agglomerative(sync, n_sections)
    bound_times = [beat_times[i] for i in bounds if i < len(beat_times)]

    def snap(t: float) -> float:
        return min(downbeats, key=lambda d: abs(d - t))

    edges = sorted(set([0.0] + [snap(t) for t in bound_times] + [duration]))
    edges = [e for i, e in enumerate(edges)
             if i == 0 or e - edges[i - 1] > 2.0] or [0.0, duration]
    if edges[-1] != duration:
        edges.append(duration)

    rms = librosa.feature.rms(y=y)[0]
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rms_t = librosa.times_like(rms, sr=sr)

    # Frequency-band envelopes (same hop as rms, so rms_t indexes them too):
    # low = kick/bass -> squash amplitude, mid = melody -> color/morph pace,
    # high = hats/texture -> jiggle frequency (edit-craft.md §5).
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    band_env = {name: S[(freqs >= lo) & (freqs < hi)].mean(axis=0)
                for name, (lo, hi) in
                {"low": (20, 150), "mid": (150, 2000),
                 "high": (4000, sr / 2)}.items()}
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")

    def band_mean(sig, start, end):
        mask = (rms_t >= start) & (rms_t < end)
        return float(np.mean(sig[mask])) if mask.any() else 0.0

    raw = [{"start": round(s, 3), "end": round(e, 3),
            "energy": band_mean(rms, s, e),
            "brightness": band_mean(cent, s, e),
            "bands": {n: band_mean(env[: len(rms_t)], s, e)
                      for n, env in band_env.items()}}
           for s, e in zip(edges[:-1], edges[1:])]
    emax = max((s["energy"] for s in raw), default=1.0) or 1.0
    cmax = max((s["brightness"] for s in raw), default=1.0) or 1.0
    for name in band_env:
        bmax = max((s["bands"][name] for s in raw), default=1.0) or 1.0
        for s in raw:
            s["bands"][name] = round(s["bands"][name] / bmax, 3)
    for i, s in enumerate(raw):
        s["index"] = i
        s["energy"] = round(s["energy"] / emax, 3)
        s["brightness"] = round(s["brightness"] / cmax, 3)
        s["intensity"] = ("high" if s["energy"] > 0.75
                          else "mid" if s["energy"] > 0.4 else "low")
        s["beats"] = len([b for b in beat_times if s["start"] <= b < s["end"]])
        span = max(s["end"] - s["start"], 0.001)
        s["onset_density"] = round(
            len([o for o in onsets if s["start"] <= o < s["end"]]) / span, 2)

    beatmap = {
        "source": str(clip),
        "duration": round(duration, 3),
        "bpm": round(tempo, 2),
        "beats_per_bar": args.bars,
        "beats": [round(t, 3) for t in beat_times],
        "downbeats": [round(t, 3) for t in downbeats],
        "phrases": [round(t, 3) for t in downbeats[::4]],
        "peak_downbeat": round(peak_downbeat, 3),
        "sections": raw,
    }
    Path(args.out).write_text(json.dumps(beatmap, indent=2))
    print(f"{clip.name}: {tempo:.1f} BPM, {duration:.1f}s, "
          f"{len(downbeats)} downbeats, {len(raw)} sections -> {args.out}")
    if tempo < 70 or tempo > 180:
        print("BPM looks halved/doubled — consider --bpm-hint.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
