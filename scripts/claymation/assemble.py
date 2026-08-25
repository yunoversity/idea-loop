#!/usr/bin/env python3
"""Assemble generated shots into the final beat-synced claymation video.

Usage:
    python3 scripts/claymation/assemble.py edl.json
    python3 scripts/claymation/assemble.py edl.json --contact-sheet

edl.json schema (paths relative to the edl file's directory):
{
  "audio": "source/song.mp3",
  "output": "out/visualizer.mp4",
  "width": 1920, "height": 1080,      // optional, default 1920x1080
  "fps": 12,                          // clay cadence; 12 is the look
  "flashes": [14.03],                 // optional: 1-frame white impact
                                      // flashes at these timeline times.
                                      // Budget: 3-4 max, biggest low-band
                                      // hits only (edit-craft.md §6)
  "shots": [
    {"file": "clips/shot-01.mp4",
     "start": 0.0,  "end": 4.31,      // timeline placement (from script.json)
     "in": 0.5,                       // trim-in inside the source clip: set
                                      // so the impact frame lands on the
                                      // shot's first downbeat (§3), not 0
     "punch": 0.05}                   // optional slow push-in (3-6%);
                                      // high-energy shots only, never two
                                      // adjacent shots (§6)
  ]
}

Each shot is trimmed to (end - start) seconds, conformed to a shared
size/fps/pixel format, hard-cut concatenated in order, then the original
track is muxed on top. Shots must be contiguous (each start == previous end);
gaps abort with an error because they would drift every later cut off-beat.

Requires: ffmpeg on PATH.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n  {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("edl", help="edit decision list JSON")
    ap.add_argument("--contact-sheet", action="store_true",
                    help="also render qc/contact-sheet.png (one frame per shot)")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH")

    edl_path = Path(args.edl).resolve()
    edl = json.loads(edl_path.read_text())
    base = edl_path.parent
    fps = int(edl.get("fps", 12))
    w, h = int(edl.get("width", 1920)), int(edl.get("height", 1080))
    audio = base / edl["audio"]
    output = base / edl.get("output", "out/visualizer.mp4")
    output.parent.mkdir(parents=True, exist_ok=True)
    shots = edl["shots"]
    if not shots:
        sys.exit("edl has no shots")

    for prev, cur in zip(shots, shots[1:]):
        if abs(prev["end"] - cur["start"]) > 0.001:
            sys.exit(f"Timeline gap/overlap between {prev['file']} and "
                     f"{cur['file']} ({prev['end']} vs {cur['start']}) — "
                     "shots must be contiguous so cuts stay on the beat grid.")

    conform = (f"fps={fps},scale={w}:{h}:force_original_aspect_ratio=increase,"
               f"crop={w}:{h},setsar=1,format=yuv420p")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        parts = []
        for i, s in enumerate(shots):
            src = base / s["file"]
            if not src.exists():
                sys.exit(f"Missing shot file: {src}")
            dur = s["end"] - s["start"]
            if dur <= 0:
                sys.exit(f"Non-positive duration for {s['file']}")
            part = td / f"part-{i:02d}.mp4"
            vf = conform
            punch = float(s.get("punch", 0.0))
            if punch > 0:
                nframes = max(int(dur * fps), 1)
                vf += (f",zoompan=z='min(1+{punch}*on/{nframes},{1 + punch})'"
                       f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                       f":d=1:s={w}x{h}:fps={fps}")
            run(["ffmpeg", "-y", "-ss", str(s.get("in", 0.0)), "-i", str(src),
                 "-t", f"{dur:.3f}", "-an", "-vf", vf,
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 str(part)])
            parts.append(part)

        concat_list = td / "concat.txt"
        concat_list.write_text(
            "".join(f"file '{p}'\n" for p in parts))
        silent = td / "silent.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
             str(concat_list), "-c", "copy", str(silent)])

        flashes = [t - shots[0]["start"] for t in edl.get("flashes", [])]
        if flashes:
            flash_dur = 1.0 / fps + 0.005  # one frame
            chain = ",".join(
                "drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:thickness=fill"
                f":enable='between(t,{t:.3f},{t + flash_dur:.3f})'"
                for t in flashes)
            flashed = td / "flashed.mp4"
            run(["ffmpeg", "-y", "-i", str(silent), "-vf", chain,
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 str(flashed)])
            silent = flashed

        run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio),
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-shortest", str(output)])

        if args.contact_sheet:
            qc = base / "qc"
            qc.mkdir(exist_ok=True)
            thumbs = []
            for i, (s, part) in enumerate(zip(shots, parts)):
                thumb = td / f"thumb-{i:02d}.png"
                mid = (s["end"] - s["start"]) / 2
                run(["ffmpeg", "-y", "-ss", f"{mid:.3f}", "-i", str(part),
                     "-frames:v", "1", "-vf", "scale=480:-1", str(thumb)])
                thumbs.append(thumb)
            cols = min(4, len(thumbs))
            rows = -(-len(thumbs) // cols)
            inputs = []
            for t in thumbs:
                inputs += ["-i", str(t)]
            if len(thumbs) == 1:
                shutil.copy(thumbs[0], qc / "contact-sheet.png")
            else:
                layout = "|".join(
                    f"{'+'.join(['w0'] * (i % cols)) or '0'}_"
                    f"{'+'.join(['h0'] * (i // cols)) or '0'}"
                    for i in range(len(thumbs)))
                run(["ffmpeg", "-y", *inputs, "-filter_complex",
                     f"xstack=inputs={len(thumbs)}:layout={layout}:fill=black",
                     str(qc / "contact-sheet.png")])
            print(f"contact sheet -> {qc / 'contact-sheet.png'} "
                  f"({cols}x{rows})")

    total = shots[-1]["end"] - shots[0]["start"]
    print(f"{len(shots)} shots, {total:.1f}s @ {fps}fps -> {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
