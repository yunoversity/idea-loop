(() => {
"use strict";
const V = window.DG_VOICES;
const $ = (s) => document.querySelector(s);
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
};

/* ---------- dimensions ---------- */
const TONES = ["calm", "warm", "professional", "energetic", "empathetic", "confident", "friendly", "trustworthy"];
const byFreq = (get) => {
  const m = new Map();
  V.forEach((v) => get(v).forEach((x) => m.set(x, (m.get(x) || 0) + 1)));
  return [...m.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map((e) => e[0]);
};
const DIMS = {
  accent: { label: "Accent", get: (v) => [v.accent], observed: byFreq((v) => [v.accent]), candidates: ["Indian", "Irish", "Canadian", "South African"] },
  gender: { label: "Gender", get: (v) => [v.gender === "F" ? "Women" : "Men"], observed: ["Women", "Men"], candidates: [] },
  age: { label: "Age band", get: (v) => [v.age], observed: ["Young Adult", "Adult", "Mature"], candidates: [] },
  usecase: { label: "Use case", get: (v) => v.use_cases.map(cap), observed: byFreq((v) => v.use_cases.map(cap)), candidates: ["Healthcare", "E-learning", "Assistive tech"] },
  tone: { label: "Tone", get: (v) => v.tags.filter((t) => TONES.includes(t)).map(cap), observed: TONES.map(cap), candidates: ["Authoritative", "Playful"] },
};
const valuesOf = (d) => [...DIMS[d].observed, ...DIMS[d].candidates];
const isCandidate = (d, val) => DIMS[d].candidates.includes(val);

const PRESETS = [
  ["accent", "gender", "Accent × Gender"],
  ["accent", "age", "Accent × Age"],
  ["gender", "age", "Gender × Age"],
  ["usecase", "accent", "Use case × Accent"],
  ["usecase", "gender", "Use case × Gender"],
  ["tone", "gender", "Tone × Gender"],
  ["usecase", "tone", "Use case × Tone"],
];

/* ---------- state ---------- */
const state = {
  x: "accent", y: "gender", color: "count", thresh: 0, sel: null, showAll: false, tab: "accent",
  w: store.get("dg.w", { d: 40, e: 35, s: 25 }),
  scores: store.get("dg.scores", {}),
};
const MULT = { 0: 1, 1: 0.6, 2: 0.3 };
const CRIT = [["d", "Market demand"], ["e", "Enterprise fit"], ["h", "Difficulty to source"]];
const getScore = (dim, val, k) => (state.scores[dim] && state.scores[dim][val] && state.scores[dim][val][k]) || 3;
const isScored = (dim, val) => !!(state.scores[dim] && state.scores[dim][val]);

/* ---------- scoring ---------- */
function score(xd, x, yd, y, count) {
  const avg = (k) => (getScore(xd, x, k) + getScore(yd, y, k)) / 2;
  const D = avg("d"), E = avg("e"), S = 6 - avg("h");
  const { d, e, s } = state.w;
  const tot = d + e + s || 1;
  const base = (d * D + e * E + s * S) / tot;
  const priority = ((base - 1) / 4) * 100;
  const mult = MULT[count] ?? 0;
  return { D, E, S, base, priority, mult, composite: priority * mult };
}

/* ---------- matrix ---------- */
function matrix() {
  const xs = valuesOf(state.x), ys = valuesOf(state.y);
  const cells = [];
  for (const y of ys) for (const x of xs) {
    const voices = V.filter((v) => DIMS[state.x].get(v).includes(x) && DIMS[state.y].get(v).includes(y));
    cells.push({ x, y, voices, count: voices.length });
  }
  return { xs, ys, cells };
}

/* ---------- headline stats ---------- */
function renderStats() {
  const n = V.length;
  const am = V.filter((v) => v.accent === "American").length;
  const cellsAll = new Set(); V.forEach((v) => cellsAll.add(`${v.accent}|${v.gender}|${v.age}`));
  const accents = [...new Set(V.map((v) => v.accent))];
  const total = accents.length * 2 * 3, empty = total - cellsAll.size;
  const oneLabel = V.filter((v) => v.use_cases.length === 1).length;
  const tiles = [
    [n, "English Aura-2 voices", `snapshot ${window.DG_SNAPSHOT}`],
    [`${Math.round((am / n) * 100)}%`, "are American", `${am} of ${n}`],
    [`${empty} of ${total}`, "accent × gender × age cells are empty", "empty ≠ wanted"],
    [`${oneLabel} of ${n}`, "voices have a single use-case label", "no label names an industry"],
  ];
  $("#stats").innerHTML = tiles.map((t) => `<div class="stat"><div class="big">${t[0]}</div><div>${t[1]}</div><div class="small">${t[2]}</div></div>`).join("");
}

/* ---------- heatmap ---------- */
const COUNT_CLASS = (c) => (c === 0 ? "c0" : c === 1 ? "c1" : c === 2 ? "c2" : c <= 4 ? "c3" : c <= 9 ? "c4" : "c5");
function renderControls() {
  const opts = Object.entries(DIMS).map(([k, d]) => `<option value="${k}">${d.label}</option>`).join("");
  $("#xDim").innerHTML = opts; $("#yDim").innerHTML = opts;
  $("#presets").innerHTML = PRESETS.map((p, i) => `<button class="chip" data-i="${i}">${p[2]}</button>`).join("");
}
function syncControls() {
  $("#xDim").value = state.x; $("#yDim").value = state.y;
  document.querySelectorAll("#presets .chip").forEach((b) => {
    const p = PRESETS[b.dataset.i];
    b.classList.toggle("on", p[0] === state.x && p[1] === state.y);
  });
  document.querySelectorAll("#colorBy button").forEach((b) => {
    const on = b.dataset.v === state.color; b.classList.toggle("on", on); b.setAttribute("aria-pressed", on);
  });
}
function render() {
  syncControls();
  const m = matrix();
  const gapCells = m.cells.filter((c) => c.count <= state.thresh);
  const scored = m.cells.map((c) => ({ ...c, s: score(state.x, c.x, state.y, c.y, c.count) }));
  const maxComp = Math.max(1, ...scored.filter((c) => c.count <= state.thresh).map((c) => c.s.composite));

  let html = `<div class="hm" style="--cols:${m.xs.length}">`;
  html += `<div class="corner">${DIMS[state.y].label} ↓ · ${DIMS[state.x].label} →</div>`;
  html += m.xs.map((x) => `<div class="colh${isCandidate(state.x, x) ? " cand" : ""}" role="columnheader">${x}</div>`).join("");
  m.ys.forEach((y) => {
    html += `<div class="rowh${isCandidate(state.y, y) ? " cand" : ""}" role="rowheader">${y}</div>`;
    m.xs.forEach((x) => {
      const c = scored.find((q) => q.x === x && q.y === y);
      const isGap = c.count <= state.thresh;
      let cls;
      if (state.color === "score") {
        cls = isGap ? `s${Math.min(5, 1 + Math.floor((c.s.composite / maxComp) * 4.999))}` : "sx";
      } else cls = COUNT_CLASS(c.count);
      const sel = state.sel && state.sel.x === x && state.sel.y === y ? " sel" : "";
      const label = state.color === "score" && isGap ? Math.round(c.s.composite) : c.count;
      html += `<button class="cell ${cls}${isGap ? " gap" : ""}${sel}" data-x="${x}" data-y="${y}" aria-label="${x}, ${y}: ${c.count} voices${isGap ? ", candidate gap" : ""}">${label}</button>`;
    });
  });
  $("#heat").innerHTML = html + "</div>";

  $("#legend").innerHTML = state.color === "count"
    ? `<span class="lg"><i class="sw c0 gap"></i>0 (empty)</span><span class="lg"><i class="sw c1"></i>1</span><span class="lg"><i class="sw c2"></i>2</span><span class="lg"><i class="sw c3"></i>3–4</span><span class="lg"><i class="sw c4"></i>5–9</span><span class="lg"><i class="sw c5"></i>10+</span><span class="lg dim">Hatched = candidate gap at your threshold</span>`
    : `<span class="lg"><i class="sw s1"></i>Lower priority</span><span class="lg"><i class="sw s3"></i></span><span class="lg"><i class="sw s5"></i>Higher priority</span><span class="lg"><i class="sw sx"></i>Not a gap (covered)</span><span class="lg dim">Number = composite score (0–100)</span>`;
  const hasCand = DIMS[state.x].candidates.length || DIMS[state.y].candidates.length;
  $("#viewNote").textContent = `${gapCells.length} of ${m.cells.length} cells are candidate gaps in this view.` + (hasCand ? " Italic headers are values not in the catalog yet: hypotheses to score." : "");
  renderRank(scored);
  renderDetail();
}

/* ---------- details ---------- */
let player = null;
function playUrl(url, btn) {
  if (player) { player.pause(); }
  player = new Audio(url);
  btn.classList.add("playing");
  player.addEventListener("ended", () => btn.classList.remove("playing"));
  player.addEventListener("error", () => { btn.classList.remove("playing"); btn.textContent = "Unavailable"; });
  player.play().catch(() => { btn.classList.remove("playing"); btn.textContent = "Unavailable"; });
}
function voiceRow(v) {
  return `<li class="vrow"><div><b>${v.display_name || cap(v.name)}</b> <span class="muted">${v.accent} · ${v.age} · ${v.gender === "F" ? "W" : "M"}</span><div class="tags">${v.tags.filter((t) => t !== "feminine" && t !== "masculine").slice(0, 4).join(" · ")} — ${v.use_cases.join(", ")}</div></div>
  <div class="vbtns"><button class="btn small" data-play="${v.sample_url}">▶ Sample</button><button class="btn small ghost" data-lab="${v.canonical_name}">Use in lab</button></div></li>`;
}
function nearest(xd, x, yd, y) {
  return V.map((v) => ({ v, m: (DIMS[xd].get(v).includes(x) ? 1 : 0) + (DIMS[yd].get(v).includes(y) ? 1 : 0) }))
    .filter((o) => o.m > 0).sort((a, b) => b.m - a.m).slice(0, 3).map((o) => o.v);
}
function renderDetail() {
  const box = $("#detail");
  if (!state.sel) return;
  const { x, y } = state.sel;
  const m = matrix(); const c = m.cells.find((q) => q.x === x && q.y === y);
  if (!c) { state.sel = null; return; }
  const s = score(state.x, x, state.y, y, c.count);
  let body = `<h3>${x} · ${y}</h3><p class="muted">${DIMS[state.x].label} × ${DIMS[state.y].label} · ${c.count} voice${c.count === 1 ? "" : "s"}</p>`;
  if (c.count) body += `<ul class="vlist">${c.voices.map(voiceRow).join("")}</ul>`;
  else {
    const near = nearest(state.x, x, state.y, y);
    body += `<p>No voice sits in this cell. That makes it a <b>candidate</b> gap. Check whether someone wants it, and whether a nearby voice already serves it:</p>`;
    body += near.length ? `<ul class="vlist">${near.map(voiceRow).join("")}</ul>` : `<p class="muted">No existing voice matches either value.</p>`;
  }
  if (c.count <= 2) body += `<p class="muted small">Composite if treated as a gap: <b>${s.composite.toFixed(0)}</b> / 100</p>`;
  box.innerHTML = body;
}

/* ---------- ranking ---------- */
function renderRank(scored) {
  const gaps = scored.filter((c) => c.count <= state.thresh).sort((a, b) => b.s.composite - a.s.composite || a.count - b.count || (a.x + a.y).localeCompare(b.x + b.y));
  $("#rankMeta").textContent = `${gaps.length} candidates · ${DIMS[state.x].label} × ${DIMS[state.y].label}`;
  const list = state.showAll ? gaps : gaps.slice(0, 10);
  const defaults = (g) => [[state.x, g.x], [state.y, g.y]].filter(([d, v]) => !isScored(d, v)).length;
  $("#rankList").innerHTML = list.map((g, i) => {
    const nd = defaults(g);
    return `<li class="rk"><span class="pos">${i + 1}</span>
    <div class="rk-main"><div class="rk-title">${g.x} <span class="x">×</span> ${g.y}${g.count ? ` <span class="pill">${g.count} voice${g.count > 1 ? "s" : ""}</span>` : ""}${isCandidate(state.x, g.x) || isCandidate(state.y, g.y) ? ' <span class="pill hyp">not in catalog</span>' : ""}</div>
    <div class="bar"><i style="width:${Math.max(2, g.s.composite)}%"></i></div>
    <div class="comps"><span>Demand ${g.s.D.toFixed(1)}</span><span>Enterprise fit ${g.s.E.toFixed(1)}</span><span>Ease ${g.s.S.toFixed(1)}</span><span>×${g.s.mult.toFixed(2)} coverage</span>${nd ? `<span class="warn">${nd} default input${nd > 1 ? "s" : ""}</span>` : ""}</div></div>
    <div class="rk-score"><b>${g.s.composite.toFixed(0)}</b><small>/100</small></div>
    <button class="btn small" data-hear="${g.x}|${g.y}">Hear nearest</button></li>`;
  }).join("") || `<li class="muted">No cells meet the gap threshold in this view.</li>`;
  const more = $("#moreRank"); more.hidden = gaps.length <= 10; more.textContent = state.showAll ? "Show top 10" : `Show all ${gaps.length}`;
  renderWorked(gaps[0]);
}
function renderWorked(g) {
  const w = $("#worked");
  if (!g) { w.innerHTML = ""; return; }
  const s = g.s, { d, e, s: ws } = state.w;
  w.innerHTML = `<b>Worked example, top gap: ${g.x} × ${g.y}</b><br>
  D = ${s.D.toFixed(2)}, E = ${s.E.toFixed(2)}, S = ${s.S.toFixed(2)} (from H = ${(6 - s.S).toFixed(2)})<br>
  Base = (${d}×${s.D.toFixed(2)} + ${e}×${s.E.toFixed(2)} + ${ws}×${s.S.toFixed(2)}) / ${d + e + ws} = ${s.base.toFixed(2)}<br>
  Priority = (${s.base.toFixed(2)} − 1) / 4 × 100 = ${s.priority.toFixed(1)}<br>
  Composite = ${s.priority.toFixed(1)} × ${s.mult.toFixed(2)} = <b>${s.composite.toFixed(1)}</b>`;
}

/* ---------- scoring UI ---------- */
function renderWeights() {
  const names = { d: "Market demand", e: "Enterprise fit", s: "Ease of sourcing" };
  $("#weights").innerHTML = `<span class="lbl">Criteria weights (multipliers)</span>` + Object.keys(names).map((k) =>
    `<label class="field w">${names[k]} <input type="number" min="0" max="100" step="5" value="${state.w[k]}" data-w="${k}"></label>`).join("") +
    `<span class="muted small" id="wsum"></span>`;
  const t = state.w.d + state.w.e + state.w.s;
  $("#wsum").textContent = `Normalized to ${t || 0} total`;
}
function renderTabs() {
  $("#dimTabs").innerHTML = Object.entries(DIMS).map(([k, d]) => `<button role="tab" class="tab${k === state.tab ? " on" : ""}" aria-selected="${k === state.tab}" data-tab="${k}">${d.label}</button>`).join("");
}
function renderScoreRows() {
  const dim = state.tab;
  const head = `<div class="sr head"><span>Value</span>${CRIT.map((c) => `<span>${c[1]}<small>${c[0] === "h" ? "1 easy – 5 hard" : "1 low – 5 high"}</small></span>`).join("")}</div>`;
  $("#scoreRows").innerHTML = head + valuesOf(dim).map((val) => {
    const cnt = V.filter((v) => DIMS[dim].get(v).includes(val)).length;
    return `<div class="sr"><span class="val">${val}<small>${isCandidate(dim, val) ? "not in catalog" : cnt + " voice" + (cnt === 1 ? "" : "s")}</small></span>` +
      CRIT.map(([k]) => `<label class="rng"><input type="range" min="1" max="5" step="1" value="${getScore(dim, val, k)}" data-dim="${dim}" data-val="${val}" data-k="${k}" aria-label="${CRIT.find((c) => c[0] === k)[1]} for ${val}"><output>${getScore(dim, val, k)}</output></label>`).join("") + `</div>`;
  }).join("");
}
const ILLUSTRATIVE = {
  accent: { Indian: [5, 4, 3], Irish: [2, 2, 3], Canadian: [3, 3, 2], "South African": [2, 2, 4], American: [3, 3, 1], British: [4, 4, 2], Australian: [3, 3, 2], Filipino: [4, 4, 3] },
  usecase: { Healthcare: [5, 5, 3], "E-learning": [3, 3, 2], "Assistive tech": [4, 4, 4], "Customer service": [5, 5, 1], IVR: [4, 5, 1] },
  age: { Mature: [4, 4, 4], "Young Adult": [3, 3, 2] },
  tone: { Empathetic: [5, 5, 2], Calm: [4, 5, 2], Authoritative: [3, 4, 3], Playful: [2, 1, 2] },
};
function loadIllustrative() {
  state.scores = {};
  for (const [dim, o] of Object.entries(ILLUSTRATIVE)) { state.scores[dim] = {}; for (const [val, a] of Object.entries(o)) state.scores[dim][val] = { d: a[0], e: a[1], h: a[2] }; }
  persist();
}
const persist = () => { store.set("dg.scores", state.scores); store.set("dg.w", state.w); };

/* ---------- speech lab ---------- */
const PROMPTS = {
  "Customer service": "Thanks for calling Northwind. I can help with billing, orders, or account changes. What can I do for you today?",
  IVR: "Welcome. For sales, press one. For support, press two. To hear these options again, press star.",
  Healthcare: "Hello, this is a reminder from Riverside Clinic. You have an appointment tomorrow at 9:30 in the morning. Please reply to confirm, or call us if you need to reschedule.",
  Storytelling: "The lighthouse had been dark for a hundred years. Then, one foggy evening, a single lantern flickered to life at the top of the stairs.",
  Advertising: "Fresh. Fast. Fully charged. Meet the all-new Aurora, the phone that keeps up with you.",
  Interview: "Thanks so much for joining me today. Let's start at the beginning: what first drew you to this work?",
  "E-learning": "In this lesson, we'll look at how a loan's interest is calculated. Take your time, and pause whenever you need.",
  "Assistive tech": "You have three new messages. The first is from Maria, sent at noon. Would you like me to read it?",
  Informative: "Today's forecast calls for light rain in the morning, clearing by afternoon, with a high of sixty-four degrees.",
  "Casual chat": "Oh, hey! I was just about to message you. Did you see the game last night?",
};
const promptFor = (uc) => PROMPTS[uc] || PROMPTS[cap(uc || "")] || "Hi there, thanks for stopping by. How can I help you today?";
let apiMode = "key"; // "proxy" when serve.py holds the key

function renderLab() {
  $("#labVoice").innerHTML = V.map((v) => `<option value="${v.canonical_name}">${v.display_name || cap(v.name)} — ${v.accent}, ${v.age}, ${v.gender === "F" ? "W" : "M"}</option>`).join("");
  $("#promptChips").innerHTML = Object.keys(PROMPTS).map((k) => `<button class="chip" data-prompt="${k}">${k}</button>`).join("");
  $("#labText").value = PROMPTS["Customer service"];
  updateLab();
  try { const k = sessionStorage.getItem("dg.key"); if (k) { $("#apiKey").value = k; $("#rememberKey").checked = true; } } catch { /* ignore */ }
}
const curVoice = () => V.find((v) => v.canonical_name === $("#labVoice").value);
function updateLab() {
  const v = curVoice();
  $("#labMeta").innerHTML = `<span class="pill">${v.accent}</span><span class="pill">${v.age}</span>` + v.tags.map((t) => `<span class="pill soft">${t}</span>`).join("") + v.use_cases.map((t) => `<span class="pill use">${t}</span>`).join("");
  $("#charCount").textContent = `${$("#labText").value.length} / 2000`;
}
function setStatus(msg, bad) { const s = $("#labStatus"); s.textContent = msg; s.classList.toggle("bad", !!bad); }
async function detectProxy() {
  try {
    const r = await fetch("api/config", { cache: "no-store" });
    if (r.ok && (await r.json()).proxy) { apiMode = "proxy"; $("#keyBox").hidden = true; $("#apiMode").textContent = "Connected through the local server. The API key is held server-side."; return; }
  } catch { /* static hosting */ }
  $("#apiMode").textContent = "Paste your Deepgram API key to generate custom speech. Catalog samples work without one.";
}
async function generate() {
  const text = $("#labText").value.trim();
  if (!text) { setStatus("Write a prompt first.", true); return; }
  const model = $("#labVoice").value;
  const key = $("#apiKey").value.trim();
  if (apiMode === "key" && !key) { setStatus("Add your Deepgram API key to the right, or use the catalog sample.", true); return; }
  try { if ($("#rememberKey").checked) sessionStorage.setItem("dg.key", key); else sessionStorage.removeItem("dg.key"); } catch { /* ignore */ }
  const btn = $("#gen"); btn.disabled = true; setStatus("Generating…");
  try {
    const res = apiMode === "proxy"
      ? await fetch("api/speak", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, model }) })
      : await fetch(`https://api.deepgram.com/v1/speak?model=${encodeURIComponent(model)}&encoding=mp3`, { method: "POST", headers: { Authorization: `Token ${key}`, "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
    if (!res.ok) {
      let detail = ""; try { detail = (await res.json()).err_msg || ""; } catch { /* not json */ }
      throw new Error(res.status === 401 || res.status === 403 ? "Deepgram rejected the key (check it and its permissions)." : `Deepgram returned ${res.status}. ${detail}`);
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const p = $("#player"); p.src = url; p.hidden = false; p.play().catch(() => {});
    const dl = $("#dl"); dl.href = url; dl.hidden = false; dl.download = `${model}.mp3`;
    setStatus(`Done: ${model}, ${text.length} characters.`);
  } catch (e) {
    setStatus(e instanceof TypeError ? "Couldn’t reach Deepgram from the browser (network or CORS). Run python3 serve.py with DEEPGRAM_API_KEY set to route through a local server." : e.message, true);
  } finally { btn.disabled = false; }
}
function toLab(canonical, prompt) {
  $("#labVoice").value = canonical;
  if (prompt) $("#labText").value = prompt;
  updateLab();
  $("#lab").scrollIntoView({ behavior: "smooth" });
}

/* ---------- events ---------- */
function setView(x, y) { if (x === y) return; state.x = x; state.y = y; state.sel = null; render(); }
document.addEventListener("click", (e) => {
  const t = e.target.closest("button, a"); if (!t) return;
  if (t.matches(".cell")) { state.sel = { x: t.dataset.x, y: t.dataset.y }; render(); }
  else if (t.dataset.i !== undefined && t.matches("#presets .chip")) { const p = PRESETS[t.dataset.i]; setView(p[0], p[1]); }
  else if (t.id === "swap") setView(state.y, state.x);
  else if (t.closest("#colorBy")) { state.color = t.dataset.v; render(); }
  else if (t.dataset.play) playUrl(t.dataset.play, t);
  else if (t.dataset.lab) toLab(t.dataset.lab);
  else if (t.dataset.hear) {
    const [x, y] = t.dataset.hear.split("|");
    const near = nearest(state.x, x, state.y, y)[0] || V[0];
    const uc = [[state.x, x], [state.y, y]].find(([d]) => d === "usecase");
    toLab(near.canonical_name, promptFor(uc ? uc[1] : near.use_cases[0]));
  }
  else if (t.id === "moreRank") { state.showAll = !state.showAll; render(); }
  else if (t.dataset.tab) { state.tab = t.dataset.tab; renderTabs(); renderScoreRows(); }
  else if (t.id === "illus") { loadIllustrative(); renderScoreRows(); render(); }
  else if (t.id === "resetScores") { state.scores = {}; persist(); renderScoreRows(); render(); }
  else if (t.dataset.prompt) { $("#labText").value = PROMPTS[t.dataset.prompt]; updateLab(); }
  else if (t.id === "gen") generate();
  else if (t.id === "sample") { const v = curVoice(); playUrl(v.sample_url, t); }
});
document.addEventListener("input", (e) => {
  const t = e.target;
  if (t.matches("input[type=range][data-k]")) {
    const { dim, val, k } = t.dataset;
    state.scores[dim] = state.scores[dim] || {};
    // First touch seeds the other two criteria at the default so a partial entry is complete.
    state.scores[dim][val] = state.scores[dim][val] || { d: 3, e: 3, h: 3 };
    state.scores[dim][val][k] = +t.value;
    t.nextElementSibling.textContent = t.value;
    persist(); render();
  } else if (t.matches("input[data-w]")) {
    state.w[t.dataset.w] = Math.max(0, Math.min(100, +t.value || 0));
    $("#wsum").textContent = `Normalized to ${state.w.d + state.w.e + state.w.s} total`;
    persist(); render();
  } else if (t.id === "labText") updateLab();
});
$("#xDim").addEventListener("change", (e) => { if (e.target.value === state.y) setView(state.y, state.x); else setView(e.target.value, state.y); });
$("#yDim").addEventListener("change", (e) => { if (e.target.value === state.x) setView(state.y, state.x); else setView(state.x, e.target.value); });
$("#thresh").addEventListener("change", (e) => { state.thresh = +e.target.value; render(); });
$("#labVoice").addEventListener("change", updateLab);

/* ---------- boot ---------- */
renderStats(); renderControls(); renderWeights(); renderTabs(); renderScoreRows(); renderLab(); render(); detectProxy();
})();
