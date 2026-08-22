#!/usr/bin/env python3
"""Build the Idea Loop dashboard: a static, self-contained HTML page rendering
the pipeline board, KPI strip, and the top 3 open questions to brainstorm next.

Reads painpoints/*.md and prd/*.md; writes dashboard/index.html.
The page is published as a claude.ai Artifact; this script only generates it.
Stdlib only.
"""
import html
import re
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "dashboard" / "index.html"
STAGES = ["captured", "exploring", "graduated", "validation-ready", "mvp", "parked"]
STALE_DAYS = 14


def parse_painpoint(f):
    text = f.read_text()
    fm = dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", text.split("---")[1], re.M)) if text.startswith("---") else {}
    title_m = re.search(r"^# (.+)$", text, re.M)
    dates = re.findall(r"^(\d{4}-\d{2}-\d{2})", re.search(r"## Log\n(.*)\Z", text, re.S).group(1) if "## Log" in text else "", re.M)
    last = max(dates) if dates else fm.get("captured", "")
    qs = []
    sec = re.search(r"## Open questions\n(.*?)(\n## |\Z)", text, re.S)
    if sec:
        for line in sec.group(1).splitlines():
            if line.strip().startswith("- [ ]"):
                qs.append(line.strip()[5:].strip())
    intensity = fm.get("intensity", "null")
    return {
        "id": f.stem,
        "title": title_m.group(1).strip() if title_m else f.stem,
        "persona": fm.get("persona", "").strip('"'),
        "status": fm.get("status", "captured"),
        "intensity": int(intensity) if intensity.isdigit() else 0,
        "last": last,
        "questions": qs,
        "parked_reason": fm.get("parked_reason", "null"),
        "revival": fm.get("revival_criteria", "null"),
    }


def days_ago(iso):
    try:
        y, m, d = map(int, iso.split("-"))
        return (date.today() - date(y, m, d)).days
    except ValueError:
        return None


def dots(n):
    return '<span class="dots" title="intensity {}/5">{}</span>'.format(
        n, "".join('<i class="on"></i>' if i < n else "<i></i>" for i in range(5)))


def build():
    pps = sorted((parse_painpoint(f) for f in (REPO / "painpoints").glob("pp-*.md")),
                 key=lambda p: (-p["intensity"], p["id"]))
    prds = sorted((REPO / "prd").glob("*.md"))
    today = date.today().isoformat()

    # top 3 questions: promising ideas first (blocking, then intensity)
    cand = []
    for p in pps:
        if p["status"] == "parked":
            continue
        for q in p["questions"]:
            cand.append((("(blocking)" in q), p["intensity"], p, q))
    cand.sort(key=lambda t: (-t[0], -t[1], t[2]["id"]))
    top_q, seen = [], set()
    for t in cand:  # spread across distinct painpoints
        if t[2]["id"] not in seen:
            top_q.append(t)
            seen.add(t[2]["id"])
        if len(top_q) == 3:
            break

    open_q_total = len(cand)
    stale = [p for p in pps if p["status"] not in ("parked",) and (days_ago(p["last"]) or 0) >= STALE_DAYS]

    kpis = "".join(f'<div class="kpi"><div class="n">{v}</div><div class="l">{k}</div></div>' for k, v in [
        ("painpoints", len(pps)),
        ("PRDs", len(prds)),
        ("open questions", open_q_total),
        ("stale &ge;14d", len(stale)),
    ])

    qcards = ""
    for blocking, _, p, q in top_q:
        qtxt = html.escape(re.sub(r"\s*\(blocking\)", "", q))
        tag = '<span class="chip block">blocking</span>' if blocking else ""
        qcards += f'''<div class="qcard">
  <div class="qtext">{qtxt}</div>
  <div class="qmeta">{dots(p["intensity"])} <span class="pp">{html.escape(p["title"])}</span> · {html.escape(p["persona"])} {tag}</div>
  <div class="qhint">/brainstorm {p["id"].replace("pp-", "")[11:13] or p["id"]}</div>
</div>'''
    if not qcards:
        qcards = '<div class="empty">No open questions — the pipeline is fully fed.</div>'

    cols = ""
    for stage in STAGES:
        items = [p for p in pps if p["status"] == stage]
        if stage == "mvp" and not items:
            continue
        cards = ""
        for p in items:
            d = days_ago(p["last"])
            when = "today" if d == 0 else (f"{d}d ago" if d is not None else "—")
            stale_chip = f'<span class="chip stale">stale {d}d</span>' if d is not None and d >= STALE_DAYS else ""
            parked_note = f'<div class="revive">revive if: {html.escape(p["revival"])}</div>' if stage == "parked" and p["revival"] not in ("null", "") else ""
            cards += f'''<div class="card">
  <div class="ct">{html.escape(p["title"])}</div>
  <div class="cm">{html.escape(p["persona"])}</div>
  <div class="cf">{dots(p["intensity"])}<span class="when">{when}</span>{stale_chip}</div>
  {parked_note}
</div>'''
        if not cards:
            cards = '<div class="empty">—</div>'
        cols += f'''<div class="col"><div class="colh">{stage} <span class="count">{len(items)}</span></div>{cards}</div>'''

    page = TEMPLATE.replace("__DATE__", today).replace("__KPIS__", kpis) \
                   .replace("__QCARDS__", qcards).replace("__COLS__", cols)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page)
    print(f"dashboard/index.html built: {len(pps)} painpoints, {len(prds)} PRDs, top {len(top_q)} questions.")


TEMPLATE = """<meta charset="utf-8">
<title>Idea Loop Dashboard</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {
    --bg:#F7F9F8; --surface:#EFF3F1; --card:#FFFFFF; --ink:#1A2422; --muted:#5C6B67;
    --line:#D5DEDA; --accent:#0E7268; --accent-ink:#0A5950; --warn:#A87B1E; --warn-bg:#F5EBD4;
  }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
    --bg:#101817; --surface:#17211F; --card:#16201E; --ink:#E8EDEA; --muted:#93A29D;
    --line:#2A3835; --accent:#3FBDAF; --accent-ink:#5ED2C5; --warn:#D3A73E; --warn-bg:#2E2712;
  }}
  :root[data-theme="dark"] {
    --bg:#101817; --surface:#17211F; --card:#16201E; --ink:#E8EDEA; --muted:#93A29D;
    --line:#2A3835; --accent:#3FBDAF; --accent-ink:#5ED2C5; --warn:#D3A73E; --warn-bg:#2E2712;
  }
  body { background:var(--bg); color:var(--ink); font-family:"Archivo","Helvetica Neue",sans-serif;
         margin:0; padding:2rem 1.25rem 3rem; }
  .wrap { max-width:1200px; margin:0 auto; }
  header { display:flex; flex-wrap:wrap; align-items:baseline; gap:0.75rem 1.25rem; margin-bottom:1.5rem; }
  h1 { font-size:1.5rem; font-weight:700; letter-spacing:-0.01em; margin:0; }
  .gen { font-family:"IBM Plex Mono",monospace; font-size:0.72rem; color:var(--muted); }
  .kpis { display:flex; flex-wrap:wrap; gap:0.75rem; margin-bottom:1.75rem; }
  .kpi { background:var(--card); border:1px solid var(--line); border-radius:6px;
         padding:0.7rem 1.1rem; min-width:7.5rem; }
  .kpi .n { font-size:1.55rem; font-weight:700; font-variant-numeric:tabular-nums; }
  .kpi .l { font-family:"IBM Plex Mono",monospace; font-size:0.68rem; letter-spacing:0.08em;
            text-transform:uppercase; color:var(--muted); margin-top:0.15rem; }
  h2 { font-size:0.95rem; font-weight:600; margin:0 0 0.75rem; display:flex; gap:0.6rem; align-items:baseline; }
  h2 .sub { font-family:"IBM Plex Mono",monospace; font-size:0.68rem; font-weight:400; color:var(--muted); }
  .qgrid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:0.75rem; margin-bottom:2rem; }
  .qcard { background:var(--card); border:1px solid var(--line); border-left:3px solid var(--accent);
           border-radius:6px; padding:0.85rem 1rem; display:flex; flex-direction:column; gap:0.5rem; }
  .qtext { font-size:0.95rem; line-height:1.45; }
  .qmeta { font-size:0.78rem; color:var(--muted); display:flex; flex-wrap:wrap; gap:0.45rem; align-items:center; }
  .qmeta .pp { color:var(--accent-ink); font-weight:600; }
  .qhint { font-family:"IBM Plex Mono",monospace; font-size:0.7rem; color:var(--muted); }
  .board { display:flex; gap:0.75rem; overflow-x:auto; padding-bottom:0.75rem; }
  .col { background:var(--surface); border:1px solid var(--line); border-radius:8px;
         padding:0.75rem; min-width:250px; flex:1 0 250px; }
  .colh { font-family:"IBM Plex Mono",monospace; font-size:0.72rem; letter-spacing:0.1em;
          text-transform:uppercase; color:var(--accent-ink); margin-bottom:0.7rem;
          display:flex; justify-content:space-between; }
  .colh .count { color:var(--muted); }
  .card { background:var(--card); border:1px solid var(--line); border-radius:6px;
          padding:0.65rem 0.8rem; margin-bottom:0.6rem; }
  .ct { font-size:0.87rem; font-weight:600; line-height:1.35; }
  .cm { font-size:0.75rem; color:var(--muted); margin-top:0.2rem; }
  .cf { display:flex; align-items:center; gap:0.6rem; margin-top:0.5rem; }
  .when { font-family:"IBM Plex Mono",monospace; font-size:0.68rem; color:var(--muted); }
  .dots i { display:inline-block; width:7px; height:7px; border-radius:50%;
            background:var(--line); margin-right:2px; }
  .dots i.on { background:var(--accent); }
  .chip { font-family:"IBM Plex Mono",monospace; font-size:0.62rem; padding:0.1rem 0.4rem;
          border-radius:3px; letter-spacing:0.05em; }
  .chip.stale { background:var(--warn-bg); color:var(--warn); }
  .chip.block { background:var(--warn-bg); color:var(--warn); }
  .revive { font-size:0.72rem; color:var(--warn); margin-top:0.4rem; }
  .empty { color:var(--muted); font-size:0.8rem; padding:0.4rem 0.2rem; }
</style>
<div class="wrap">
  <header><h1>Idea Loop Dashboard</h1><span class="gen">generated __DATE__ · refreshed daily</span></header>
  <div class="kpis">__KPIS__</div>
  <h2>Brainstorm next <span class="sub">top open questions from the most promising painpoints</span></h2>
  <div class="qgrid">__QCARDS__</div>
  <h2>Pipeline</h2>
  <div class="board">__COLS__</div>
</div>
"""

if __name__ == "__main__":
    build()
