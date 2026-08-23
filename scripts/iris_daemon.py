#!/usr/bin/env python3
"""Iris live: long-polls Telegram and answers Anthony conversationally via
headless Claude Code running against this repo.

Two modes:
- NORMAL — Claude is read-only. She discusses the pipeline; the script does the
  writing (every non-command message is filed to inbox/ and pushed).
- MEETING — opened by /meeting, closed by /endmeeting. The staff meeting is the
  sanctioned venue for state changes with Anthony present, so Claude may write
  the files a meeting produces: minutes, queue.md, taste-profile.md, and
  painpoint frontmatter for decisions he makes explicitly in the conversation.
  She still cannot decide anything, change decision rights, or start a build.

Commands: /help /status /questions answered by script; /new resets the thread;
/meeting and /endmeeting bracket a live meeting; /interviewme runs the interview.
Only TELEGRAM_CHAT_ID is accepted. Shares .telegram_offset with the manual
Actions poll fallback.

Run under launchd (see scripts/com.iris.daemon.plist) or by hand:
  python3 scripts/iris_daemon.py
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OFFSET_FILE = REPO / ".telegram_offset"
SESSION_FILE = REPO / ".iris_session"
CLAUDE = os.path.expanduser("~/.local/bin/claude")
CLAUDE_TIMEOUT = 240

sys.path.insert(0, str(REPO / "scripts"))
from telegram_digest import load_env, send  # noqa: E402
from telegram_poll import HELP_TEXT, status_text, questions_text  # noqa: E402

READ_ONLY_TOOLS = "Read,Glob,Grep,Bash(git log:*),Bash(git status)"

# Meeting mode: the staff meeting is the sanctioned venue for state changes with
# Anthony present and deciding in real time, so Iris may write here — but only
# the files a meeting legitimately produces, and only while a meeting is open.
MEETING_TOOLS = ",".join([
    "Read", "Glob", "Grep", "Write", "Edit",
    "Bash(git pull)", "Bash(git add:*)", "Bash(git commit:*)", "Bash(git push)",
    "Bash(git status)", "Bash(git log:*)", "Bash(git diff:*)",
    "Bash(python3 scripts/build_dashboard.py)",
])
MEETING_FLAG = REPO / ".iris_meeting"

MEETING_SYSTEM = (
    "You are Iris, running Anthony's staff meeting live over Telegram. He is "
    "present and deciding in real time — this is the sanctioned venue for state "
    "changes, so you MAY write files here. Follow .claude/agents/chief-of-staff.md "
    "and working-style.md exactly.\n\n"
    "MEETING CONDUCT: work the agenda ONE item at a time and wait for his answer "
    "before moving on — never dump the whole pack in one message. Headline first, "
    "detail only if he asks. Keep each message under ~1200 characters. When you "
    "need a decision, ask for it plainly and state your recommendation with the "
    "reason. Track where you are in the agenda across messages.\n\n"
    "AGENDA: (1) scoreboard vs goals.md, (2) pipeline review + stale flags, "
    "(3) graduation nominations — scored, he decides, (4) parking proposals, "
    "(5) open-question triage + refresh queue.md, (6) retro, (7) workflow items.\n\n"
    "WHAT YOU MAY WRITE during the meeting: meetings/<today>.md (minutes, including "
    "his decisions and stated reasons), queue.md, taste-profile.md (his own words "
    "only), and painpoint frontmatter ONLY for decisions he explicitly makes in "
    "this conversation (status, parked_reason, revival_criteria). Commit and push "
    "after each decision so nothing is lost if the chat drops.\n\n"
    "WHAT YOU MAY NOT DO: decide anything yourself, change CLAUDE.md's prime "
    "directive or autonomy rule, alter decision rights, hire/fire/merge agents, "
    "approve spend, or start a build. Graduation and /build remain his explicit "
    "calls, and a /build must still be run from a Claude Code session.\n\n"
    "Telegram formatting: plain text, no markdown headers or tables."
)

IRIS_SYSTEM = (
    "You are Iris, Anthony's Chief of Staff for his idea-loop pipeline, chatting "
    "with him over Telegram. Follow CLAUDE.md and .claude/agents/chief-of-staff.md. "
    "Before answering, read working-style.md (how Anthony wants to be worked with — "
    "follow it exactly: headline-first messages, one sharp question at a time, direct "
    "but constructive), queue.md (current priorities), goals.md (the scoreboard "
    "targets), the most recent pack in meetings/, and sprint.md if a build is live — "
    "your answers must reflect the pipeline's actual current state. "
    "You are READ-ONLY in this channel: discuss painpoints, answer questions, help "
    "him think — but you cannot change files here. If he dumps a new idea or "
    "painpoint, tell him it's been filed for intake automatically (the daemon does "
    "that) and engage with the substance. If he asks for state changes (graduate, "
    "park, playbook edits), explain those happen in a Claude Code session or at the "
    "staff meeting (/meeting). Telegram formatting: plain text only, no markdown "
    "headers or tables, keep replies under 3000 characters, be conversational and "
    "concise — this is a chat, not a report."
)


INTERVIEW_PROMPT = (
    "Anthony just sent the InterviewMe command. Interview him to close open "
    "questions in the pipeline: scan painpoints/*.md for unchecked '- [ ]' items "
    "under '## Open questions', prioritize blocking questions and high-intensity "
    "painpoints, and ask him exactly ONE question now — conversationally, naming "
    "which painpoint it's for. His answers will arrive as normal messages in this "
    "same thread: after each answer, briefly dig deeper if the answer is thin "
    "(open-ended follow-ups only, never leading), then move to the next most "
    "valuable question. One question per message, always. Keep the interview going "
    "until he changes the subject or the questions run out. His answers are filed "
    "to inbox/ automatically — you don't need to record them."
)


def log(msg):
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}", flush=True)


def git(*args, timeout=60):
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, timeout=timeout)


def file_to_inbox(msg, text):
    ts = datetime.fromtimestamp(msg["date"], tz=timezone.utc)
    name = ts.strftime("%Y-%m-%d-%H%M%S") + f"-{msg['message_id']}.md"
    reply = msg.get("reply_to_message", {}).get("text")
    body = f"# Telegram message · {ts.isoformat()}\n\n"
    if msg.get("voice") or msg.get("audio"):
        body += "*(voice note, transcribed locally)*\n\n"
    if reply:
        body += f"> In reply to:\n> {reply}\n\n"
    body += text + "\n"
    (REPO / "inbox" / name).write_text(body)
    git("add", "inbox")
    if git("diff", "--cached", "--quiet").returncode != 0:
        git("commit", "-q", "-m", "inbox: telegram message via iris daemon")
        git("push", "-q")


PACK_MARKER = REPO / ".iris_session_pack"
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
_whisper = None


def transcribe(token, file_id):
    """Download a Telegram voice note and transcribe it locally (faster-whisper).
    First call downloads the model (~75MB for 'base') to the HF cache."""
    global _whisper
    import tempfile
    with urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}", timeout=30) as r:
        path = json.load(r)["result"]["file_path"]
    with urllib.request.urlopen(
            f"https://api.telegram.org/file/bot{token}/{path}", timeout=60) as r:
        audio = r.read()
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    with tempfile.NamedTemporaryFile(suffix=".oga", delete=False) as f:
        f.write(audio)
        tmp = f.name
    try:
        segments, _info = _whisper.transcribe(tmp, vad_filter=True)
        return " ".join(s.text.strip() for s in segments).strip()
    finally:
        os.unlink(tmp)


def _reset_thread_on_new_pack():
    """New meeting pack => fresh conversation thread, so stale context dies daily."""
    packs = sorted(p.name for p in (REPO / "meetings").glob("*.md"))
    newest = packs[-1] if packs else ""
    seen = PACK_MARKER.read_text().strip() if PACK_MARKER.exists() else ""
    if newest and newest != seen:
        SESSION_FILE.unlink(missing_ok=True)
        PACK_MARKER.write_text(newest)


def ask_iris(text, meeting=False):
    git("pull", "-q")
    if not meeting:
        _reset_thread_on_new_pack()
    cmd = [CLAUDE, "-p", text, "--output-format", "json",
           "--allowedTools", MEETING_TOOLS if meeting else READ_ONLY_TOOLS,
           "--append-system-prompt", MEETING_SYSTEM if meeting else IRIS_SYSTEM]
    resumed = SESSION_FILE.exists()
    if resumed:
        cmd += ["--resume", SESSION_FILE.read_text().strip()]
    env = dict(os.environ)
    env["PATH"] = os.path.expanduser("~/.local/bin") + ":/usr/local/bin:/usr/bin:/bin"
    try:
        out = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True,
                             timeout=CLAUDE_TIMEOUT, env=env)
    except subprocess.TimeoutExpired:
        return "That one took me too long to think about — try asking a smaller piece of it."
    if out.returncode != 0:
        if resumed:  # stale session id is the usual culprit; retry fresh once
            SESSION_FILE.unlink(missing_ok=True)
            return ask_iris(text, meeting)
        log(f"claude error: {out.stderr[:500]}")
        return "I hit an error thinking that through. It's logged — try again in a minute."
    try:
        data = json.loads(out.stdout)
        result = data.get("result") or ""
        if data.get("is_error") or "authentication_error" in result or "Failed to authenticate" in result:
            log(f"claude auth/api error: {result[:300]}")
            if "401" in result or "authenticate" in result.lower():
                return ("I can't think right now — my Claude sign-in on your Mac is invalid. "
                        "Fix: open the Terminal app, run `claude`, complete the browser login, then quit it. "
                        "I'll work instantly after that. (Commands like /status and /questions still work meanwhile.)")
            return f"My thinking engine returned an error: {result[:500]}"
        if data.get("session_id"):
            SESSION_FILE.write_text(data["session_id"])
        return result or "…(I came back empty — try rephrasing?)"
    except json.JSONDecodeError:
        return out.stdout[:3000] or "Empty reply — worth checking iris_daemon.log."


def send_chunked(token, chat_id, text):
    for i in range(0, len(text), 4000):
        send(token, chat_id, text[i:i + 4000])


def typing(token, chat_id):
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendChatAction",
            data=json.dumps({"chat_id": chat_id, "action": "typing"}).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except OSError:
        pass


def handle(token, chat_id, msg, text):
    cmd = text.strip().split()[0].lower() if text.strip() else ""
    if cmd in ("/help", "/start"):
        return HELP_TEXT + "\n\nI'm live right now, so you can also just talk to me — ask about any painpoint, think out loud, or dump a new idea."
    if cmd == "/status":
        return status_text()
    if cmd == "/questions":
        return questions_text()
    if cmd == "/new":
        SESSION_FILE.unlink(missing_ok=True)
        return "Fresh thread started — what's on your mind?"
    if cmd in ("/interviewme", "interviewme"):
        typing(token, chat_id)
        return ask_iris(INTERVIEW_PROMPT)
    # Claude Code commands sent here by muscle memory: explain, don't choke.
    if cmd in ("/meeting", "meeting"):
        MEETING_FLAG.write_text(datetime.now().isoformat())
        SESSION_FILE.unlink(missing_ok=True)  # fresh thread for the meeting
        typing(token, chat_id)
        return ask_iris(
            "Anthony has convened the staff meeting over Telegram. Open it: read "
            "goals.md, working-style.md, your playbook, every painpoint, queue.md, "
            "the newest pack in meetings/ if one exists, and taste-profile.md. "
            "Then start the meeting — propose a length, give the scoreboard, and "
            "begin agenda item 1. ONE item, then wait for him.", meeting=True)
    if cmd in ("/endmeeting", "endmeeting"):
        was_open = MEETING_FLAG.exists()
        MEETING_FLAG.unlink(missing_ok=True)
        if not was_open:
            return "No meeting was open."
        reply = ask_iris(
            "Anthony has ended the staff meeting. Finalize: write the minutes to "
            "meetings/<today>.md with every decision and his stated reason, append "
            "decisions to taste-profile.md, refresh queue.md, commit and push. Then "
            "reply with a short summary of what was decided and what happens next.",
            meeting=True)
        SESSION_FILE.unlink(missing_ok=True)
        return reply

    session_cmds = {
        "/brainstorm": "run a brainstorming session",
        "/capture": "file a painpoint (though you can just dump it here — I file it automatically)",
        "/graduate": "graduate a painpoint to a PRD",
        "/park": "park a painpoint",
        "/build": "approve a PRD for build and start the 48h clock",
    }
    if cmd in session_cmds:
        return (f"{cmd} runs in a Claude Code session, not here — it changes pipeline state, "
                f"which I can't do over Telegram by design.\n\n"
                f"Open Claude Code in ~/Projects/idea-loop and run {cmd} there to {session_cmds[cmd]}.\n\n"
                f"What I can do here: /status, /questions, /interviewme, and talking through anything "
                f"on your mind — send it and I'll file it.")
    typing(token, chat_id)
    if MEETING_FLAG.exists():
        return ask_iris(text, meeting=True)  # meeting turns are minutes, not inbox
    file_to_inbox(msg, text)
    return ask_iris(text)


def main():
    load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        sys.exit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")
    log("Iris daemon up; long-polling Telegram.")
    offset = int(OFFSET_FILE.read_text()) if OFFSET_FILE.exists() else 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=50&offset={offset}"
            with urllib.request.urlopen(url, timeout=70) as resp:
                updates = json.load(resp).get("result", [])
        except OSError as e:
            log(f"poll error, backing off: {e}")
            time.sleep(15)
            continue
        for u in updates:
            offset = max(offset, u["update_id"] + 1)
            OFFSET_FILE.write_text(str(offset))
            msg = u.get("message") or {}
            if str(msg.get("chat", {}).get("id")) != str(chat_id):
                continue
            text = msg.get("text")
            voice = msg.get("voice") or msg.get("audio")
            if not text and not voice:
                continue
            try:
                if voice:
                    typing(token, chat_id)
                    text = transcribe(token, voice["file_id"])
                    if not text:
                        send(token, chat_id, "I got the voice note but couldn't make out any words — mind trying again?")
                        continue
                    log(f"voice ({voice.get('duration', '?')}s): {text[:80]!r}")
                    send(token, chat_id, f"🎙️ Heard: “{text[:400]}”")
                    msg = dict(msg)
                    msg["text"] = text
                else:
                    log(f"msg: {text[:80]!r}")
                reply = handle(token, chat_id, msg, text)
                send_chunked(token, chat_id, reply)
            except Exception as e:  # keep the daemon alive no matter what
                log(f"handler error: {e}")


if __name__ == "__main__":
    main()
