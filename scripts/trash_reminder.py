#!/usr/bin/env python3
"""Weekly SMS reminder: next trash pickup for the house, Trash vs. Trash + Recycling.

Runs Thursdays 6 PM America/Chicago via .github/workflows/trash-reminder.yml.
Schedule data comes from Austin Resource Recovery's ReCollect API (the backend of
austintexas.gov's "My Schedule" tool). Stdlib only.

Transports, tried in order — the first one with its env vars set wins:
  1. Twilio        TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM
  2. Textbelt      TEXTBELT_KEY
  3. Email-to-SMS  SMTP_HOST, SMTP_USER, SMTP_PASS, TRASH_SMS_EMAIL
                   (SMTP_PORT optional, default 587; e.g. Gmail + number@vtext.com)
Recipient number: TRASH_SMS_TO (E.164, e.g. +15125551234) — used by Twilio/Textbelt.

Google Voice is NOT supported: it has no public API for sending SMS.

Usage: trash_reminder.py [--dry-run]   (--dry-run: print the message, send nothing)
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Chicago")
ADDRESS = os.environ.get("TRASH_ADDRESS", "2111 Greenwood Ave, Austin, TX 78723")
RECOLLECT = "https://api.recollect.net/api"
AREA = os.environ.get("RECOLLECT_AREA", "Austin")


def load_env():
    env_path = REPO / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "idea-loop-trash-reminder"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def find_place():
    """Resolve the street address to a ReCollect place id (env override wins)."""
    if os.environ.get("RECOLLECT_PLACE_ID"):
        return os.environ["RECOLLECT_PLACE_ID"], os.environ.get("RECOLLECT_SERVICE_ID", "waste")
    service = os.environ.get("RECOLLECT_SERVICE_ID", "waste")
    q = urllib.parse.quote(ADDRESS.split(",")[0])  # street part matches best
    data = get_json(f"{RECOLLECT}/areas/{AREA}/services/{service}/address-suggest?q={q}&locale=en-US")
    suggestions = data.get("suggestions", data) if isinstance(data, dict) else data
    if not suggestions:
        raise SystemExit(f"ReCollect returned no match for {ADDRESS!r}: {json.dumps(data)[:500]}")
    hit = suggestions[0]
    place_id = hit.get("place_id") or hit.get("id")
    if not place_id:
        raise SystemExit(f"No place id in ReCollect suggestion: {json.dumps(hit)[:500]}")
    print(f"Matched address: {hit.get('name', '?')} (place {place_id})")
    return place_id, str(hit.get("service_id") or service)


def flag_names(event):
    names = set()
    for flag in event.get("flags", []):
        for key in ("name", "subject", "event_type", "id"):
            v = flag.get(key)
            if isinstance(v, str):
                names.add(v.lower())
    return names


def next_pickup(place_id, service):
    """Return (date, has_recycling) for the next garbage day, scanning 10 days out."""
    today = datetime.now(TZ).date()
    url = (f"{RECOLLECT}/places/{place_id}/services/{service}/events"
           f"?nomerge=1&hide=reminder_only&after={today - timedelta(days=1)}"
           f"&before={today + timedelta(days=10)}&locale=en-US")
    data = get_json(url)
    events = data.get("events", data) if isinstance(data, dict) else data
    by_day = {}
    for ev in events or []:
        day = ev.get("day")
        if not day:
            continue
        by_day.setdefault(day, set()).update(flag_names(ev))
    for day in sorted(by_day):
        print(f"  {day}: {sorted(by_day[day])}")
    for day in sorted(by_day):
        d = date.fromisoformat(day)
        names = by_day[day]
        if d >= today and any("garbage" in n or "trash" in n for n in names):
            return d, any("recycl" in n for n in names)
    raise SystemExit(f"No garbage pickup found in the next 10 days. Raw events: {json.dumps(events)[:800]}")


def compose(pickup_day, has_recycling):
    what = "Trash AND Recycling" if has_recycling else "Trash only (no recycling this week)"
    day_str = pickup_day.strftime("%A, %b %-d")
    return (f"Trash reminder for {ADDRESS.split(',')[0]}: next pickup is {day_str}. "
            f"This week: {what}. Please have the bins out the night before!")


def send_twilio(msg):
    sid = os.environ["TWILIO_ACCOUNT_SID"].strip()
    token = os.environ["TWILIO_AUTH_TOKEN"].strip()
    body = urllib.parse.urlencode({
        "To": os.environ["TRASH_SMS_TO"].strip(), "From": os.environ["TWILIO_FROM"].strip(),
        "Body": msg,
    }).encode()
    req = urllib.request.Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json", data=body)
    import base64
    creds = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req.add_header("Authorization", f"Basic {creds}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"Twilio: sent ({resp.status})")
    except urllib.error.HTTPError as e:
        import re as _re
        # Redact phone digits: these logs are public on this repo.
        detail = _re.sub(r"\+?\d{7,}", "[number]", e.read().decode(errors="replace")[:600])
        hint = (" — check TWILIO_ACCOUNT_SID (starts with AC) and TWILIO_AUTH_TOKEN "
                "(the Auth Token on the Console home, not an API key)") if e.code == 401 else ""
        raise SystemExit(f"Twilio send failed (HTTP {e.code}){hint}: {detail}")


def send_textbelt(msg):
    body = urllib.parse.urlencode({
        "phone": os.environ["TRASH_SMS_TO"], "message": msg, "key": os.environ["TEXTBELT_KEY"],
    }).encode()
    with urllib.request.urlopen("https://textbelt.com/text", data=body, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    if not result.get("success"):
        raise SystemExit(f"Textbelt send failed: {result}")
    print(f"Textbelt: sent (quota remaining: {result.get('quotaRemaining')})")


def send_email_sms(msg):
    import smtplib
    from email.message import EmailMessage
    m = EmailMessage()
    m["From"] = os.environ["SMTP_USER"]
    m["To"] = os.environ["TRASH_SMS_EMAIL"]
    m.set_content(msg)
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587"))) as s:
        s.starttls()
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        s.send_message(m)
    print(f"Email-to-SMS: sent to {os.environ['TRASH_SMS_EMAIL']}")


TRANSPORTS = [
    ("Twilio", ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM", "TRASH_SMS_TO"), send_twilio),
    ("Textbelt", ("TEXTBELT_KEY", "TRASH_SMS_TO"), send_textbelt),
    ("Email-to-SMS", ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "TRASH_SMS_EMAIL"), send_email_sms),
]


def main():
    load_env()
    dry_run = "--dry-run" in sys.argv

    # Scheduled runs fire at two UTC times to cover CDT/CST; only the one that is
    # actually Thursday 6 PM in Chicago proceeds. Manual dispatch skips the guard.
    if os.environ.get("GITHUB_EVENT_NAME") == "schedule":
        now = datetime.now(TZ)
        if not (now.weekday() == 3 and now.hour == 18):
            print(f"Not Thursday 6 PM in Chicago ({now:%a %H:%M}); skipping.")
            return

    place_id, service = find_place()
    pickup_day, has_recycling = next_pickup(place_id, service)
    msg = compose(pickup_day, has_recycling)
    print(f"Message: {msg}")

    if dry_run:
        print("Dry run — nothing sent.")
        return
    for name, keys, sender in TRANSPORTS:
        if all(os.environ.get(k) for k in keys):
            print(f"Sending via {name}...")
            sender(msg)
            return
    raise SystemExit("No SMS transport configured — set Twilio, Textbelt, or SMTP secrets "
                     "(see docstring). Message NOT sent.")


if __name__ == "__main__":
    main()
