#!/usr/bin/env python3
"""Fetch new Telegram messages from Anthony and write each to inbox/ for intake.

Only messages from TELEGRAM_CHAT_ID are accepted; everything else is ignored.
Offset is persisted in .telegram_offset (gitignored) so each run is incremental.
Stdlib only. Routing (answer vs. new capture) is the intake agent's job, not this
script's — it just lands raw text in inbox/.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OFFSET_FILE = REPO / ".telegram_offset"


def load_env():
    env_path = REPO / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


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

    written = 0
    for u in updates:
        offset = max(offset, u["update_id"] + 1)
        msg = u.get("message") or {}
        if str(msg.get("chat", {}).get("id")) != str(chat_id):
            continue
        text = msg.get("text")
        if not text:
            continue
        ts = datetime.fromtimestamp(msg["date"], tz=timezone.utc)
        name = ts.strftime("%Y-%m-%d-%H%M%S") + f"-{msg['message_id']}.md"
        reply = msg.get("reply_to_message", {}).get("text")
        body = f"# Telegram message · {ts.isoformat()}\n\n"
        if reply:
            body += f"> In reply to:\n> {reply}\n\n"
        body += text + "\n"
        (REPO / "inbox" / name).write_text(body)
        written += 1

    OFFSET_FILE.write_text(str(offset))
    print(f"{written} message(s) written to inbox/.")


if __name__ == "__main__":
    main()
