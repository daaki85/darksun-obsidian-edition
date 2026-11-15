"""Prototype, not part of the Ledger: a page to judge outfits.py's pictures on, as they are seen
in the game: moving, small, on the ground's colours. One file, opened in a browser; nothing is
sent anywhere.

    python3 prototypes/outfitreview.py GAME_DIR OUT.html

Every figure in every outfit walks, fights, shoots, is hit and dies, at the game's size or
enlarged. Click one to see all 29 of its frames beside the figure's own; click a frame to open it:

  * mark it as wrong and say why. The marks are listed as text to copy back, each naming its
    outfit, figure and frame: for faults that want a rule mended in outfits.py;
  * or correct it by hand: paint its pixels, enlarged, in the outfit's own shades or the
    figure's own colours (right-click takes the colour under the pointer), seeing it at the
    game's size as you go. The corrections are listed as the text of prototypes/outfit_fixes.txt
    (outfitfixes.py), to copy or save there: the page opens with that file's corrections laid on,
    so it edits the whole file. One the rules have since changed under is shown as stale, to keep
    or drop.

Marks and corrections are kept in the browser between visits.

The page holds the game's pictures: it is for the player's own use and is never committed.
"""

import base64
import io
import json
import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import outfits as O  # noqa: E402

CW, CH, BASE = 68, 64, 58


def strip(game: O.Game, frames: List) -> str:
    """29 frames side by side (15 walking, 14 fighting), each on its anchor: a PNG as a data URI."""
    from PIL import Image
    img = Image.new("RGBA", (CW * len(frames), CH), (0, 0, 0, 0))
    for i, (rows, ox, oy, own) in enumerate(frames):
        bx, by = i * CW + CW // 2 - len(own[0]) // 2 + ox, BASE - len(own) + oy
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c is not None and i * CW <= bx + x < (i + 1) * CW and 0 <= by + y < CH:
                    img.putpixel((bx + x, by + y), game.palette[c] + (255,))
    out = io.BytesIO()
    img.save(out, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


def main(argv: List[str]) -> None:
    if len(argv) < 2:
        raise SystemExit(__doc__)
    game = O.Game(argv[0])
    names = [name for _, name in O.FIGURES]
    data = {"cw": CW, "ch": CH, "base": BASE, "figures": names, "outfits": ["Own"] + [o.name for o in O.OUTFITS.values()],
            "strips": {}, "sizes": {}, "palette": ["#%02x%02x%02x" % c for c in game.palette],
            "ramps": {o.name: {k: list(v) for k, v in (("cloak", o.cloak), ("tunic", o.torso), ("sleeves", o.sleeves),
                                                       ("leggings", o.legs), ("boots", o.boots)) if v}
                      for o in O.OUTFITS.values()},
            "fixes": {f"{outfit}/{figure}/{O.outfitfixes.frame_name(cb, f)}":
                      {f"{x},{y}": [a, b] for (x, y), (a, b) in fix.items()}
                      for (outfit, figure, cb, f), fix in game.fixes.items() if fix},
            "head": O.outfitfixes.HEAD}
    for key, name in O.FIGURES:
        fig = game.fig(key)
        own = [(fig.rows(cb, f), 0, 0, fig.rows(cb, f)) for cb, n in ((0, 15), (1, 14)) for f in range(n)]
        data["strips"]["Own/" + name] = strip(game, own)
        data["sizes"][name] = [[len(rows[0]), len(rows)] for rows, _, _, _ in own]
        for npc, o in O.OUTFITS.items():
            walk, fight = game.full(key, npc, fixed=False)  # (the page lays the corrections on itself)
            data["strips"][o.name + "/" + name] = strip(game, walk + fight)
    with open(argv[1], "w") as out:
        out.write(PAGE.replace("/*DATA*/", json.dumps(data)))
    print(argv[1])


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Outfit review</title>
<style>
:root { --bg: #1d1a17; --panel: #2a2622; --ink: #ece4d8; --dim: #a59a8a; --line: #4a4238; --mark: #e0533d; --fix: #e8b84a; --ground: #c4966a; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 14px/1.45 system-ui, sans-serif; }
header { position: sticky; top: 0; z-index: 3; background: var(--panel); border-bottom: 1px solid var(--line); padding: 10px 16px;
  display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; }
h1 { font-size: 16px; margin: 0 8px 0 0; }
h2 { font-size: 15px; margin: 18px 0 8px; }
label { color: var(--dim); display: inline-flex; gap: 6px; align-items: center; }
select, button, input[type=text] { background: #17140f; color: var(--ink); border: 1px solid var(--line); border-radius: 4px; padding: 4px 8px; font: inherit; }
button { cursor: pointer; }
main { padding: 16px; }
.wrap { overflow-x: auto; }
table { border-collapse: collapse; }
th { color: var(--dim); font-weight: 500; text-align: left; padding: 4px 10px; white-space: nowrap; }
td { padding: 3px; }
canvas { display: block; background: var(--ground); image-rendering: pixelated; border: 2px solid transparent; border-radius: 3px; }
#grid canvas, .fr canvas:first-child { cursor: pointer; }
td.fixed canvas { border-color: var(--fix); border-style: dashed; }
td.has canvas { border-color: var(--mark); }
td.sel canvas { border-color: var(--ink); border-style: solid; }
.box { margin-top: 18px; background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px; }
.box h2 { margin-top: 0; }
.frames { display: flex; flex-wrap: wrap; gap: 6px; }
.fr { text-align: center; color: var(--dim); font-size: 11px; }
.fr.fixed canvas:first-child { border-color: var(--fix); border-style: dashed; }
.fr.marked canvas:first-child { border-color: var(--mark); }
.fr.open canvas:first-child { border-color: var(--ink); border-style: solid; }
.fr.marked { color: var(--mark); }
#edit { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start; }
#big { cursor: crosshair; touch-action: none; }
.side { flex: 1; min-width: 260px; }
.sw { display: flex; flex-wrap: wrap; gap: 3px; margin: 2px 0 8px; align-items: center; }
.sw span.name { color: var(--dim); width: 74px; font-size: 12px; }
.sw button { width: 22px; height: 22px; padding: 0; border-radius: 3px; border: 2px solid #0008; }
.sw button.on { border-color: var(--ink); outline: 1px solid #000; }
.tool { padding: 2px 8px !important; width: auto !important; height: 22px !important; font-size: 12px; }
.small { display: flex; gap: 10px; align-items: flex-end; margin: 8px 0; }
.small div { color: var(--dim); font-size: 11px; text-align: center; }
.note { display: flex; gap: 8px; margin: 8px 0; align-items: center; }
.note input { flex: 1; min-width: 120px; }
.stale { color: var(--fix); margin: 8px 0; }
textarea { width: 100%; height: 130px; background: #17140f; color: var(--ink); border: 1px solid var(--line); border-radius: 4px; padding: 8px; font: 12px/1.4 ui-monospace, monospace; }
.hint { color: var(--dim); margin: 6px 0; }
</style></head><body>
<header>
  <h1>Outfit review</h1>
  <label>Showing <select id="scene"></select></label>
  <label>Size <select id="zoom"><option>1</option><option>2</option><option selected>3</option><option>4</option></select></label>
  <label>Speed <select id="fps"><option value="4">slow</option><option value="8" selected>game</option><option value="0">stopped</option></select></label>
  <label>Ground <select id="ground"><option value="#c4966a">sand</option><option value="#6b5a48">rock</option><option value="#3c3a36">stone</option><option value="#4d6a3a">scrub</option></select></label>
</header>
<main>
<p class="hint">Click a figure to see every frame beside its own picture, then a frame to open it: mark it as wrong, or correct its pixels by hand.
A red border is a marked frame, a dashed gold one a frame corrected by hand.</p>
<div class="wrap"><table id="grid"></table></div>
<div id="detail" class="box" hidden></div>
<div id="editor" class="box" hidden></div>
<h2>Marked frames <span class="hint">(faults to mend in the rules: copy this back to Claude)</span></h2>
<textarea id="list" readonly></textarea>
<p><button id="copy">Copy the marks</button> <button id="clear">Clear all marks</button> <span id="said" class="hint"></span></p>
<h2>Corrections by hand <span class="hint">(the whole of prototypes/outfit_fixes.txt: copy or save it there)</span></h2>
<textarea id="fixes" readonly></textarea>
<p><button id="copyfix">Copy the corrections</button> <button id="savefix">Save as outfit_fixes.txt</button>
<button id="resetfix">Back to the file's corrections</button> <span id="saidfix" class="hint"></span></p>
</main>
<script>
const D = /*DATA*/;
const SCENES = {"Walking toward": [3,4,5,6], "Walking away": [7,8,9,10], "Walking sideways": [11,12,13,14],
  "Standing (front, back, side)": [0,0,0,1,1,1,2,2,2], "Attack toward": [15,16,17,17], "Attack away": [18,19,20,20],
  "Attack sideways": [21,22,23,23], "Bow (front, back, side)": [24,24,24,25,25,25,26,26,26], "Hit, then dead": [15,27,27,28,28,28,28]};
const NAME = f => f < 15 ? "walk " + f : "fight " + (f - 15);
const FRAME = name => +name.split(" ")[1] + (name.startsWith("fight") ? 15 : 0);
const $ = id => document.getElementById(id);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const store = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) || d; } catch (e) { return d; } };
let marks = load("outfit-marks", {});
// corrections: {"Outfit/figure/walk 3": {"x,y": [before, after]}} (palette numbers, null no pixel)
const STAMP = JSON.stringify(D.fixes);
const saved = load("outfit-edits", null);
let edits = saved && saved.stamp === STAMP ? saved.edits : JSON.parse(STAMP);
const saveEdits = () => store("outfit-edits", {stamp: STAMP, edits});
const RGB = {};  // "#rrggbb" -> the first palette number with that colour
D.palette.forEach((c, i) => { if (!(c in RGB)) RGB[c] = i; });
const same = (a, b) => a === b || (a != null && b != null && D.palette[a] === D.palette[b]);
const imgs = {}, raw = {}, shown = {}, stale = {};
let waiting = 0;
for (const k in D.strips) { const i = new Image(); waiting++; i.onload = () => { if (!--waiting) start(); }; i.src = D.strips[k]; imgs[k] = i; }
for (const s in SCENES) $("scene").add(new Option(s));
const cells = [];
let picked = null, opened = null, tick = 0, tool = null;

function origin(fig, f) { const [w, h] = D.sizes[fig][f]; return [Math.floor(D.cw / 2) - Math.floor(w / 2), D.base - h]; }
function rawAt(key, f, x, y) {  // the palette number the rules drew at a pixel of the figure's own frame
  const [ox, oy] = origin(key.split("/")[1], f), X = f * D.cw + ox + x, Y = oy + y, d = raw[key];
  if (X < f * D.cw || X >= (f + 1) * D.cw || Y < 0 || Y >= D.ch) return undefined;
  const i = (Y * d.width + X) * 4;
  if (d.data[i + 3] === 0) return null;
  return RGB["#" + [d.data[i], d.data[i + 1], d.data[i + 2]].map(v => v.toString(16).padStart(2, "0")).join("")];
}
function rebuild(key) {  // the strip with its corrections laid on; those the rules changed under are stale
  const cv = shown[key] || (shown[key] = el("canvas")), c = cv.getContext("2d");
  cv.width = raw[key].width; cv.height = raw[key].height; c.putImageData(raw[key], 0, 0);
  for (const id in edits) {
    if (!id.startsWith(key + "/")) continue;
    const f = FRAME(id.split("/")[2]), [ox, oy] = origin(key.split("/")[1], f);
    stale[id] = [];
    for (const at in edits[id]) {
      const [x, y] = at.split(",").map(Number), [before, after] = edits[id][at], now = rawAt(key, f, x, y);
      if (now === undefined || !(same(now, before) || same(now, after))) { stale[id].push(at); continue; }
      c.clearRect(f * D.cw + ox + x, oy + y, 1, 1);
      if (after != null) { c.fillStyle = D.palette[after]; c.fillRect(f * D.cw + ox + x, oy + y, 1, 1); }
    }
  }
}
function draw(cv, key, f, z) {
  cv.width = D.cw * z; cv.height = D.ch * z;
  const c = cv.getContext("2d"); c.imageSmoothingEnabled = false;
  c.drawImage(shown[key], f * D.cw, 0, D.cw, D.ch, 0, 0, D.cw * z, D.ch * z);
}
function build() {
  const t = $("grid"); t.innerHTML = "";
  const head = t.insertRow(); head.appendChild(el("th"));
  for (const o of D.outfits) head.appendChild(el("th", "", o));
  for (const fig of D.figures) {
    const r = t.insertRow(); r.appendChild(el("th", "", fig));
    for (const o of D.outfits) {
      const td = r.insertCell(), cv = el("canvas"), key = o + "/" + fig;
      td.appendChild(cv); cells.push({td, cv, key});
      td.onclick = () => { picked = key; opened = null; detail(); editor(); flagCells(); };
    }
  }
}
const any = (set, key) => Object.keys(set).some(m => m.startsWith(key + "/") && (set === marks || Object.keys(set[m]).length));
function flagCells() {
  for (const c of cells) {
    c.td.classList.toggle("sel", c.key === picked);
    c.td.classList.toggle("has", any(marks, c.key));
    c.td.classList.toggle("fixed", any(edits, c.key));
  }
}
function frame() {
  const seq = SCENES[$("scene").value], z = +$("zoom").value;
  for (const c of cells) draw(c.cv, c.key, seq[tick % seq.length], z);
}
let timer = null;
function run() {
  clearInterval(timer); frame();
  const fps = +$("fps").value;
  if (fps) timer = setInterval(() => { tick++; frame(); }, 1000 / fps);
}
function detail() {
  const d = $("detail"); d.hidden = !picked; if (!picked) return;
  const [o, fig] = picked.split("/");
  d.innerHTML = "";
  d.appendChild(el("h2", "", o + ", " + fig + (o === "Own" ? " (the figure's own pictures)" : ": the outfit above, the figure's own below. Click a frame to open it.")));
  const box = d.appendChild(el("div", "frames"));
  for (let f = 0; f < 29; f++) {
    const b = box.appendChild(el("div", "fr")), a = b.appendChild(el("canvas")), id = picked + "/" + NAME(f);
    draw(a, picked, f, 3);
    if (o !== "Own") { draw(b.appendChild(el("canvas")), "Own/" + fig, f, 3); a.onclick = () => { opened = f; tool = null; detail(); editor(); }; }
    b.appendChild(el("div", "", NAME(f)));
    b.classList.toggle("marked", id in marks);
    b.classList.toggle("fixed", !!edits[id] && Object.keys(edits[id]).length > 0);
    b.classList.toggle("open", f === opened);
  }
}
function editor() {
  const e = $("editor"); e.hidden = opened == null || !picked; if (e.hidden) return;
  const [o, fig] = picked.split("/"), f = opened, id = picked + "/" + NAME(f), Z = 9;
  e.innerHTML = "";
  e.appendChild(el("h2", "", o + ", " + fig + ", " + NAME(f)));
  const row = e.appendChild(el("div")); row.id = "edit";
  const big = row.appendChild(el("canvas")); big.id = "big";
  const side = row.appendChild(el("div", "side"));
  // the colours to paint with: the outfit's shades by garment, then the figure's own in this frame
  const groups = Object.entries(D.ramps[o]).map(([k, v]) => [k, v]);
  const own = new Set();
  for (let y = -12; y < D.ch; y++) for (let x = -34; x < D.cw; x++) { const c = rawAt("Own/" + fig, f, x, y); if (c != null) own.add(c); }
  groups.push(["figure's own", [...own].sort((a, b) => a - b)]);
  const buttons = [];
  const choose = t => { tool = t; for (const [b, v] of buttons) b.classList.toggle("on", v === tool); };
  for (const [name, list] of groups) {
    const line = side.appendChild(el("div", "sw")); line.appendChild(el("span", "name", name));
    for (const c of list) { const b = line.appendChild(el("button")); b.style.background = D.palette[c]; b.title = "colour " + c; b.onclick = () => choose(c); buttons.push([b, c]); }
  }
  const line = side.appendChild(el("div", "sw")); line.appendChild(el("span", "name", "tools"));
  for (const [text, v, tip] of [["no pixel", "erase", "take the pixel away"], ["as the rules drew it", "undo", "take the correction off a pixel"]]) {
    const b = line.appendChild(el("button", "tool", text)); b.title = tip; b.onclick = () => choose(v); buttons.push([b, v]);
  }
  choose(tool == null ? groups[0][1][Math.min(2, groups[0][1].length - 1)] : tool);
  side.appendChild(el("div", "hint", "Paint with the left button (drag for more). Right-click takes the colour under the pointer."));
  const small = side.appendChild(el("div", "small")), views = [];
  for (const [key, z, text] of [[picked, 1, "game size"], [picked, 3, "corrected"], ["raw", 3, "as the rules drew it"], ["Own/" + fig, 3, "the figure's own"]]) {
    const b = small.appendChild(el("div")), cv = b.appendChild(el("canvas")); b.appendChild(el("div", "", text)); views.push([cv, key, z]);
  }
  const warn = side.appendChild(el("div", "stale"));
  const marked = side.appendChild(el("div", "note"));
  const mb = marked.appendChild(el("button")), note = marked.appendChild(el("input")); note.type = "text"; note.placeholder = "what is wrong? (for a fault to mend in the rules)";
  const drop = side.appendChild(el("button", "", "Take this frame's corrections off"));
  function paint() {
    rebuild(picked);
    big.width = D.cw * Z; big.height = D.ch * Z;
    const c = big.getContext("2d"); c.imageSmoothingEnabled = false;
    c.drawImage(shown[picked], f * D.cw, 0, D.cw, D.ch, 0, 0, D.cw * Z, D.ch * Z);
    c.strokeStyle = "#0002"; c.lineWidth = 1; c.beginPath();
    for (let x = 0; x <= D.cw; x++) { c.moveTo(x * Z + .5, 0); c.lineTo(x * Z + .5, D.ch * Z); }
    for (let y = 0; y <= D.ch; y++) { c.moveTo(0, y * Z + .5); c.lineTo(D.cw * Z, y * Z + .5); }
    c.stroke();
    const [ox, oy] = origin(fig, f);
    c.strokeStyle = "#e8b84a"; c.lineWidth = 2;  // the corrected pixels, outlined
    for (const at in edits[id] || {}) { const [x, y] = at.split(",").map(Number); c.strokeRect((ox + x) * Z + 1, (oy + y) * Z + 1, Z - 2, Z - 2); }
    for (const [cv, key, z] of views) {
      if (key === "raw") { cv.width = D.cw * z; cv.height = D.ch * z; const t = el("canvas"); t.width = raw[picked].width; t.height = D.ch; t.getContext("2d").putImageData(raw[picked], 0, 0);
        const g = cv.getContext("2d"); g.imageSmoothingEnabled = false; g.drawImage(t, f * D.cw, 0, D.cw, D.ch, 0, 0, D.cw * z, D.ch * z); }
      else draw(cv, key, f, z);
    }
    const s = stale[id] || [];
    warn.innerHTML = "";
    if (s.length) {
      warn.appendChild(el("span", "", s.length + " correction" + (s.length > 1 ? "s" : "") + " here no longer fit: the rules now draw something else under them. "));
      const k = warn.appendChild(el("button", "", "Lay them on anyway")), x = warn.appendChild(el("button", "", "Drop them"));
      k.onclick = () => { for (const at of s) { const [px, py] = at.split(",").map(Number); edits[id][at][0] = rawAt(picked, f, px, py) ?? null; } changed(); };
      x.onclick = () => { for (const at of s) delete edits[id][at]; changed(); };
    }
    mb.textContent = id in marks ? "Unmark" : "Mark this frame as wrong";
    note.hidden = !(id in marks); note.value = marks[id] || "";
    drop.hidden = !(edits[id] && Object.keys(edits[id]).length);
  }
  function changed() {
    if (edits[id] && !Object.keys(edits[id]).length) delete edits[id];
    saveEdits(); paint(); detail(); flagCells(); frame(); fixes();
  }
  function at(ev) {
    const r = big.getBoundingClientRect(), [ox, oy] = origin(fig, f);
    return [Math.floor((ev.clientX - r.left) * big.width / r.width / Z) - ox, Math.floor((ev.clientY - r.top) * big.height / r.height / Z) - oy];
  }
  function put(ev) {
    const [x, y] = at(ev), now = rawAt(picked, f, x, y), k = x + "," + y;
    if (now === undefined) return;
    const fix = edits[id] || (edits[id] = {});
    const want = tool === "erase" ? null : tool;
    if (tool === "undo" || same(now, want)) delete fix[k]; else fix[k] = [now, want];
    changed();
  }
  let down = false;
  big.onpointerdown = ev => { if (ev.button === 0) { down = true; big.setPointerCapture(ev.pointerId); put(ev); } };
  big.onpointermove = ev => { if (down) put(ev); };
  big.onpointerup = () => { down = false; };
  big.oncontextmenu = ev => {
    ev.preventDefault();
    const [x, y] = at(ev), k = x + "," + y, fix = (edits[id] || {})[k], c = fix && !(stale[id] || []).includes(k) ? fix[1] : rawAt(picked, f, x, y);
    if (c === null) choose("erase"); else if (c !== undefined) {
      if (!buttons.some(([, v]) => v === c)) { const b = line.appendChild(el("button")); b.style.background = D.palette[c]; b.title = "colour " + c; b.onclick = () => choose(c); buttons.push([b, c]); }
      choose(c);
    }
  };
  mb.onclick = () => { if (id in marks) delete marks[id]; else marks[id] = ""; store("outfit-marks", marks); paint(); detail(); flagCells(); list(); };
  note.oninput = () => { marks[id] = note.value; store("outfit-marks", marks); list(); };
  drop.onclick = () => { delete edits[id]; changed(); };
  paint();
}
function list() {
  $("list").value = Object.keys(marks).sort().map(id => id.split("/").join(" / ") + (marks[id] ? ": " + marks[id] : "")).join("\n");
}
function fixes() {
  const show = c => c == null ? "." : String(c), out = [D.head];
  const order = id => { const [o, fig, fr] = id.split("/"); return [o, fig, +fr.startsWith("fight"), +fr.split(" ")[1]]; };
  const ids = Object.keys(edits).filter(id => Object.keys(edits[id]).length).sort((a, b) => { const x = order(a), y = order(b);
    for (let i = 0; i < 4; i++) if (x[i] !== y[i]) return x[i] < y[i] ? -1 : 1; return 0; });
  for (const id of ids) {
    out.push(id.split("/").join(" / "));
    const px = Object.keys(edits[id]).map(k => k.split(",").map(Number)).sort((a, b) => a[1] - b[1] || a[0] - b[0]);
    for (const [x, y] of px) { const [a, b] = edits[id][x + "," + y]; out.push("  " + x + "," + y + ": " + show(a) + " > " + show(b)); }
    out.push("");
  }
  $("fixes").value = out.join("\n");
}
async function copy(area, said) {
  $(area).select();
  try { await navigator.clipboard.writeText($(area).value); $(said).textContent = "Copied."; }
  catch (e) { document.execCommand("copy"); $(said).textContent = "Copied (or press Ctrl+C)."; }
}
function start() {
  for (const k in imgs) { const t = el("canvas"); t.width = imgs[k].width; t.height = imgs[k].height; const c = t.getContext("2d"); c.drawImage(imgs[k], 0, 0); raw[k] = c.getImageData(0, 0, t.width, t.height); }
  for (const k in imgs) rebuild(k);
  build(); flagCells(); list(); fixes(); run();
  for (const id of ["scene", "zoom", "fps"]) $(id).onchange = () => { tick = 0; run(); };
  $("ground").onchange = () => document.documentElement.style.setProperty("--ground", $("ground").value);
  $("copy").onclick = () => copy("list", "said");
  $("copyfix").onclick = () => copy("fixes", "saidfix");
  $("savefix").onclick = () => { const a = el("a"); a.href = URL.createObjectURL(new Blob([$("fixes").value], {type: "text/plain"})); a.download = "outfit_fixes.txt"; a.click(); };
  $("clear").onclick = () => { if (confirm("Clear every mark?")) { marks = {}; store("outfit-marks", marks); detail(); editor(); flagCells(); list(); } };
  $("resetfix").onclick = () => { if (confirm("Put back the corrections the page came with, losing those made here since?")) {
    edits = JSON.parse(STAMP); saveEdits(); for (const k in imgs) rebuild(k); detail(); editor(); flagCells(); frame(); fixes(); } };
}
</script></body></html>
"""


if __name__ == "__main__":
    main(sys.argv[1:])
