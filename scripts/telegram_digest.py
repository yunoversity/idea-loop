#!/usr/bin/env python3
"""Send the daily digest: top open questions across painpoints, to Anthony's Telegram.

Blocking questions outrank non-blocking; ties broken by painpoint staleness (older
last-log-date first). Caps at DIGEST_MAX questions. Stdlib only.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIGEST_MAX = 3


def load_env():
    env_path = REPO / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _painpoint_meta():
    meta = {}
    for f in (REPO / "painpoints").glob("pp-*.md"):
        text = f.read_text()
        m = re.search(r"^# (.+)$", text, re.M)
        meta[f.stem] = m.group(1).strip() if m else f.stem
    return meta


def queue_questions():
    """Yield questions from Iris's queue.md (the single priority source), in order."""
    qf = REPO / "queue.md"
    if not qf.exists():
        return
    meta = _painpoint_meta()
    for line in qf.read_text().splitlines():
        m = re.match(r"- \[ \] \((pp-[\w-]+)\)\s*(.+)", line.strip())
        if m:
            pid, body = m.group(1), m.group(2)
            yield ("(blocking)" in body, pid, meta.get(pid, pid), body)


def open_questions():
    """Yield (blocking, painpoint_id, title, question) for unchecked questions."""
    for f in sorted((REPO / "painpoints").glob("pp-*.md")):
        text = f.read_text()
        m = re.search(r"^# (.+)$", text, re.M)
        title = m.group(1).strip() if m else f.stem
        status = re.search(r"^status:\s*(\S+)", text, re.M)
        if status and status.group(1) == "parked":
            continue
        section = re.search(r"## Open questions\n(.*?)(\n## |\Z)", text, re.S)
        if not section:
            continue
        for line in section.group(1).splitlines():
            q = line.strip()
            if q.startswith("- [ ]"):
                body = q[5:].strip()
                yield ("(blocking)" in body, f.stem, title, body)


def send(token, chat_id, text):
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat_id, "text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        sys.exit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

    qs = list(queue_questions())[:DIGEST_MAX]  # Iris's queue.md is authoritative
    if not qs:  # fallback: raw scan when no queue exists yet
        qs = sorted(open_questions(), key=lambda q: (not q[0], q[1]))[:DIGEST_MAX]
    if not qs:
        text = "Morning. No open questions today — the pipeline is either quiet or well-fed. Dump anything on your mind and I'll take it from there."
    else:
        lines = ["Morning. Top open questions:"]
        for i, (blocking, pid, title, body) in enumerate(qs, 1):
            tag = " [blocking]" if blocking else ""
            clean = re.sub(r"\s*\(blocking\)", "", body)
            lines.append(f"\n{i}. ({title}){tag}\n{clean}")
        lines.append("\nReply to any of these, or dump something new — either way I'll file it.")
        text = "\n".join(lines)

    send(token, chat_id, text)
    print(f"Digest sent: {len(qs)} question(s).")


if __name__ == "__main__":
    main()
