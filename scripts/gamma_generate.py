#!/usr/bin/env python3
"""Generate Gamma presentations from markdown decks via the Gamma Generate API.

Usage:
  python3 scripts/gamma_generate.py hackathon/demo-a-dossier.md [more.md ...]

Reads GAMMA_API_KEY from .env. textMode=preserve keeps our slide content
verbatim; '---' separators become card breaks (cardSplit=inputTextBreaks).
Polls every 5s until each deck completes; prints the gamma URL per deck.
Stdlib only.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://public-api.gamma.app/v1.0"

sys.path.insert(0, str(REPO / "scripts"))
from telegram_digest import load_env  # noqa: E402


def api(method, path, key, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body else None,
        headers={"X-API-KEY": key, "Content-Type": "application/json",
                 "Accept": "application/json",
                 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) idea-loop/1.0"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        sys.exit(f"Gamma API {e.code} on {method} {path}: {detail}")


def generate(key, md_path):
    text = Path(md_path).read_text()
    title = text.splitlines()[0].lstrip("# ").strip()
    gen = api("POST", "/generations", key, {
        "inputText": text,
        "textMode": "preserve",
        "format": "presentation",
        "cardSplit": "inputTextBreaks",
        "title": title,
    })
    gid = gen.get("generationId") or gen.get("id")
    if not gid:
        sys.exit(f"No generation id in response: {json.dumps(gen)[:300]}")
    print(f"  submitted ({gid}) …", flush=True)
    while True:
        time.sleep(5)
        status = api("GET", f"/generations/{gid}", key)
        state = status.get("status")
        if state == "completed":
            creds = status.get("credits", {})
            print(f"  DONE: {status.get('gammaUrl')}  (credits left: {creds.get('remaining', '?')})")
            return status.get("gammaUrl")
        if state == "failed":
            sys.exit(f"  generation failed: {json.dumps(status)[:300]}")
        print(f"  {state} …", flush=True)


def main():
    load_env()
    key = os.environ.get("GAMMA_API_KEY")
    if not key:
        sys.exit("GAMMA_API_KEY not set in .env")
    files = sys.argv[1:]
    if not files:
        sys.exit("usage: gamma_generate.py <deck.md> [more.md ...]")
    urls = {}
    for f in files:
        print(f"{f}:")
        urls[f] = generate(key, f)
    print("\nAll decks:")
    for f, u in urls.items():
        print(f"  {Path(f).stem}: {u}")


if __name__ == "__main__":
    main()
