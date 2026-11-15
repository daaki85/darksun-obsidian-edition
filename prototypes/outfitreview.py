"""Prototype, not part of the Ledger: a page to judge outfits.py's pictures on, as they are seen
in the game: moving, small, on the ground's colours. One file, opened in a browser; nothing is
sent anywhere.

    python3 prototypes/outfitreview.py GAME_DIR OUT.html

Every figure in every outfit walks, fights, shoots, is hit and dies, at the game's size or
enlarged. Click one to see all 29 of its frames beside the figure's own; click a frame to mark it
and say what is wrong. The marks are listed as text to copy back (and kept in the browser), each
naming its outfit, figure and frame, so a fault is fixed where it is, in outfits.py's rules or as
a touch by hand, and checked again by outfitcheck.py.

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
    data = {"cw": CW, "ch": CH, "figures": [name for _, name in O.FIGURES],
            "outfits": ["Own"] + [o.name for o in O.OUTFITS.values()], "strips": {}}
    for key, name in O.FIGURES:
        fig = game.fig(key)
        own = [(fig.rows(cb, f), 0, 0, fig.rows(cb, f)) for cb, n in ((0, 15), (1, 14)) for f in range(n)]
        data["strips"]["Own/" + name] = strip(game, own)
        for npc, o in O.OUTFITS.items():
            walk, fight = game.full(key, npc)
            data["strips"][o.name + "/" + name] = strip(game, walk + fight)
    with open(argv[1], "w") as out:
        out.write(PAGE.replace("/*DATA*/", json.dumps(data)))
    print(argv[1])


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Outfit review</title>
<style>
:root { --bg: #1d1a17; --panel: #2a2622; --ink: #ece4d8; --dim: #a59a8a; --line: #4a4238; --mark: #e0533d; --ground: #c4966a; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 14px/1.45 system-ui, sans-serif; }
header { position: sticky; top: 0; z-index: 3; background: var(--panel); border-bottom: 1px solid var(--line); padding: 10px 16px;
  display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; }
h1 { font-size: 16px; margin: 0 8px 0 0; }
label { color: var(--dim); display: inline-flex; gap: 6px; align-items: center; }
select, button, input[type=text] { background: #17140f; color: var(--ink); border: 1px solid var(--line); border-radius: 4px; padding: 4px 8px; font: inherit; }
button { cursor: pointer; }
main { padding: 16px; }
.wrap { overflow-x: auto; }
table { border-collapse: collapse; }
th { color: var(--dim); font-weight: 500; text-align: left; padding: 4px 10px; white-space: nowrap; }
td { padding: 3px; }
canvas { display: block; background: var(--ground); image-rendering: pixelated; border: 2px solid transparent; border-radius: 3px; cursor: pointer; }
td.sel canvas { border-color: var(--ink); }
td.has canvas { border-color: var(--mark); }
#detail { margin-top: 18px; background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px; }
#detail h2 { font-size: 15px; margin: 0 0 8px; }
.frames { display: flex; flex-wrap: wrap; gap: 6px; }
.fr { text-align: center; color: var(--dim); font-size: 11px; }
.fr.marked canvas:first-child { border-color: var(--mark); }
.fr.marked { color: var(--mark); }
.note { display: flex; gap: 8px; margin: 4px 0; align-items: center; }
.note input { flex: 1; min-width: 120px; }
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
<p class="hint">Click a figure to see every frame beside its own picture. Click a frame to mark it, and say what is wrong. Copy the list at the bottom back to Claude.</p>
<div class="wrap"><table id="grid"></table></div>
<div id="detail" hidden></div>
<h2 style="font-size:15px">Marked frames</h2>
<textarea id="list" readonly></textarea>
<p><button id="copy">Copy the list</button> <button id="clear">Clear all marks</button> <span id="said" class="hint"></span></p>
</main>
<script>
const D = /*DATA*/;
const SCENES = {"Walking toward": [3,4,5,6], "Walking away": [7,8,9,10], "Walking sideways": [11,12,13,14],
  "Standing (front, back, side)": [0,0,0,1,1,1,2,2,2], "Attack toward": [15,16,17,17], "Attack away": [18,19,20,20],
  "Attack sideways": [21,22,23,23], "Bow (front, back, side)": [24,24,24,25,25,25,26,26,26], "Hit, then dead": [15,27,27,28,28,28,28]};
const NAME = f => f < 15 ? "walk " + f : "fight " + (f - 15);
const $ = id => document.getElementById(id);
let marks = {};
try { marks = JSON.parse(localStorage.getItem("outfit-marks") || "{}"); } catch (e) {}
const save = () => { try { localStorage.setItem("outfit-marks", JSON.stringify(marks)); } catch (e) {} };
const imgs = {};
let waiting = 0;
for (const k in D.strips) { const i = new Image(); waiting++; i.onload = () => { if (!--waiting) start(); }; i.src = D.strips[k]; imgs[k] = i; }
for (const s in SCENES) $("scene").add(new Option(s));
const cells = [];
let picked = null, tick = 0;
function draw(cv, key, f, z) {
  cv.width = D.cw * z; cv.height = D.ch * z;
  const c = cv.getContext("2d"); c.imageSmoothingEnabled = false;
  c.drawImage(imgs[key], f * D.cw, 0, D.cw, D.ch, 0, 0, D.cw * z, D.ch * z);
}
function build() {
  const t = $("grid"); t.innerHTML = "";
  const head = t.insertRow(); head.appendChild(document.createElement("th"));
  for (const o of D.outfits) { const th = document.createElement("th"); th.textContent = o; head.appendChild(th); }
  for (const fig of D.figures) {
    const r = t.insertRow(); const th = document.createElement("th"); th.textContent = fig; r.appendChild(th);
    for (const o of D.outfits) {
      const td = r.insertCell(), cv = document.createElement("canvas"), key = o + "/" + fig;
      td.appendChild(cv); cells.push({td, cv, key});
      td.onclick = () => { picked = key; detail(); flagCells(); };
    }
  }
}
function flagCells() {
  for (const c of cells) {
    c.td.classList.toggle("sel", c.key === picked);
    c.td.classList.toggle("has", Object.keys(marks).some(m => m.startsWith(c.key + "/")));
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
  d.innerHTML = "<h2></h2><div class='frames' id='fr'></div><div id='notes'></div>";
  d.querySelector("h2").textContent = o + ", " + fig + (o === "Own" ? " (the figure's own pictures)" : ": the outfit above, the figure's own below");
  for (let f = 0; f < 29; f++) {
    const box = document.createElement("div"); box.className = "fr";
    const a = document.createElement("canvas"); draw(a, picked, f, 3); box.appendChild(a);
    if (o !== "Own") { const b = document.createElement("canvas"); draw(b, "Own/" + fig, f, 3); b.style.cursor = "default"; box.appendChild(b); }
    const cap = document.createElement("div"); cap.textContent = NAME(f); box.appendChild(cap);
    const id = picked + "/" + NAME(f);
    box.classList.toggle("marked", id in marks);
    a.onclick = () => { if (id in marks) delete marks[id]; else marks[id] = ""; save(); detail(); flagCells(); list(); };
    $("fr").appendChild(box);
  }
  for (const id of Object.keys(marks).filter(m => m.startsWith(picked + "/"))) {
    const row = document.createElement("div"); row.className = "note";
    const lab = document.createElement("span"); lab.textContent = id.split("/")[2];
    const inp = document.createElement("input"); inp.type = "text"; inp.placeholder = "what is wrong?"; inp.value = marks[id];
    inp.oninput = () => { marks[id] = inp.value; save(); list(); };
    row.append(lab, inp); $("notes").appendChild(row);
  }
}
function list() {
  $("list").value = Object.keys(marks).sort().map(id => id.split("/").join(" / ") + (marks[id] ? ": " + marks[id] : "")).join("\n");
}
function start() {
  build(); flagCells(); list(); run();
  for (const id of ["scene", "zoom", "fps"]) $(id).onchange = () => { tick = 0; run(); };
  $("ground").onchange = () => document.documentElement.style.setProperty("--ground", $("ground").value);
  $("copy").onclick = async () => {
    $("list").select();
    try { await navigator.clipboard.writeText($("list").value); $("said").textContent = "Copied."; }
    catch (e) { document.execCommand("copy"); $("said").textContent = "Copied (or press Ctrl+C)."; }
  };
  $("clear").onclick = () => { if (confirm("Clear every mark?")) { marks = {}; save(); detail(); flagCells(); list(); } };
}
</script></body></html>
"""


if __name__ == "__main__":
    main(sys.argv[1:])
