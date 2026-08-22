#!/usr/bin/env python3
"""Fetch new Telegram messages from Anthony; handle commands, file the rest to inbox/.

Commands answered directly (no Claude session needed):
  /help      — list commands
  /status    — pipeline counts by stage
  /questions — resend the current top open questions (digest logic)

Any other message is written to inbox/ for the intake agent and acknowledged.
Only messages from TELEGRAM_CHAT_ID are accepted. Offset persists in
.telegram_offset so each run is incremental. Stdlib only.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OFFSET_FILE = REPO / ".telegram_offset"

sys.path.insert(0, str(REPO / "scripts"))
from telegram_digest import load_env, open_questions, send, DIGEST_MAX  # noqa: E402

HELP_TEXT = """Here's what I can do here (I check messages every ~30 minutes, so replies aren't instant):

/status — where every idea stands in the pipeline
/questions — the current top open questions, resent on demand
/interviewme — I interview you: one open question at a time, from the most promising ideas
/new — start a fresh conversation thread
/help — this list

Anything else you send me becomes pipeline input automatically: new painpoints get filed for intake, and replies to my questions get attached to their idea. For live work — brainstorming, staff meetings, graduations — open Claude Code in ~/Projects/idea-loop and use /capture, /brainstorm, /meeting, /graduate, /park."""


def status_text():
    stages = {}
    for f in sorted((REPO / "painpoints").glob("pp-*.md")):
        m = re.search(r"^status:\s*(\S+)", f.read_text(), re.M)
        stages.setdefault(m.group(1) if m else "unknown", []).append(f.stem)
    if not stages:
        return "Pipeline is empty — send me a painpoint dump to get started."
    order = ["captured", "exploring", "graduated", "validation-ready", "mvp", "parked", "unknown"]
    lines = ["Pipeline status:"]
    for s in order:
        if s in stages:
            lines.append(f"• {s}: {len(stages[s])}")
    total = sum(len(v) for v in stages.values())
    lines.append(f"Total: {total} painpoints.")
    return "\n".join(lines)


def questions_text():
    qs = sorted(open_questions(), key=lambda q: (not q[0], q[1]))[:DIGEST_MAX]
    if not qs:
        return "No open questions right now."
    lines = ["Top open questions:"]
    for i, (blocking, pid, title, body) in enumerate(qs, 1):
        tag = " [blocking]" if blocking else ""
        clean = re.sub(r"\s*\(blocking\)", "", body)
        lines.append(f"\n{i}. ({title}){tag}\n{clean}")
    return "\n".join(lines)


def main():
    load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        sys.exit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=0&offset={offset}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        updates = json.load(resp).get("result", [])

    filed = 0
    for u in updates:
        offset = max(offset, u["update_id"] + 1)
        msg = u.get("message") or {}
        if str(msg.get("chat", {}).get("id")) != str(chat_id):
            continue
        text = msg.get("text")
        if not text:
            continue

        cmd = text.strip().split()[0].lower() if text.strip() else ""
        if cmd in ("/help", "/start"):
            send(token, chat_id, HELP_TEXT)
            continue
        if cmd == "/status":
            send(token, chat_id, status_text())
            continue
        if cmd == "/questions":
            send(token, chat_id, questions_text())
            continue

        ts = datetime.fromtimestamp(msg["date"], tz=timezone.utc)
        name = ts.strftime("%Y-%m-%d-%H%M%S") + f"-{msg['message_id']}.md"
        reply = msg.get("reply_to_message", {}).get("text")
        body = f"# Telegram message · {ts.isoformat()}\n\n"
        if reply:
            body += f"> In reply to:\n> {reply}\n\n"
        body += text + "\n"
        (REPO / "inbox" / name).write_text(body)
        filed += 1

    if filed:
        send(token, chat_id, f"Filed {filed} message{'s' if filed > 1 else ''} for intake ✓ — I'll fold it into the pipeline and bring back questions in the daily digest.")

    OFFSET_FILE.write_text(str(offset))
    print(f"{filed} message(s) filed to inbox/.")


if __name__ == "__main__":
    main()
