"""Prototype, not part of the Ledger: the bench corrections by hand are made at without the
review page: a figure's frames drawn large with their pixels numbered, a frame's colour numbers,
and the faulty pixels outfitcheck.py finds, each with a corrections file of one's own laid on.

    python3 prototypes/outfitbench.py GAME_DIR view OUT.png OUTFIT FIGURE [FRAMES] [--fixes FILE] [--zoom N] [--compare]
    python3 prototypes/outfitbench.py GAME_DIR grid OUTFIT FIGURE FRAME [--fixes FILE]
    python3 prototypes/outfitbench.py GAME_DIR faults OUTFIT FIGURE [--fixes FILE]
    python3 prototypes/outfitbench.py GAME_DIR palette OUTFIT

OUTFIT is Warrior, Thief, Priest or Mage; FIGURE as the sheets name it ("half-elf man"); FRAMES
as "w0-14,f0-13" (w walking, f fighting; default all 29); FRAME as "walk 12" or "fight 3".
view: each frame as corrected, on the sand, ruled every 5 pixels of the figure's own frame (the
numbers along the top and left are its x and y: what a correction is written in); --compare adds
the figure's own picture before it and the picture as the rules drew it after. grid: the colour
numbers of one frame as corrected, a corrected pixel marked *. faults: the faulty pixels, frame
by frame. palette: the outfit's shades by garment, dark to light, with their colours.
--fixes FILE: that corrections file in place of prototypes/outfit_fixes.txt.
"""

import os
import sys
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import outfitcheck as C  # noqa: E402
import outfitfixes as F  # noqa: E402
import outfits as O  # noqa: E402

CW, CH, BASE = 68, 64, 58


def frames_of(text: str) -> List[Tuple[int, int]]:
    out = []
    for part in text.split(","):
        cb, span = int(part[0] == "f"), part[1:]
        a, _, b = span.partition("-")
        out += [(cb, f) for f in range(int(a), int(b or a) + 1)]
    return out


def find(game: O.Game, outfit: str, figure: str):
    npc = next((n for n, o in O.OUTFITS.items() if o.name.lower() == outfit.lower()), None)
    key = next((k for k, name in O.FIGURES if name == figure), None)
    if npc is None or key is None:
        raise SystemExit(f"no outfit {outfit!r} or figure {figure!r}: outfits {[o.name for o in O.OUTFITS.values()]}, "
                         f"figures {[n for _, n in O.FIGURES]}")
    return npc, key


def view(game: O.Game, path: str, outfit: str, figure: str, frames: List[Tuple[int, int]], zoom: int, compare: bool) -> None:
    from PIL import Image, ImageDraw
    npc, key = find(game, outfit, figure)
    fixed, plain = game.full(key, npc), game.full(key, npc, fixed=False)
    kinds = 3 if compare else 1
    # (the cells no bigger than what is drawn in them: the pictures' reach round their anchor)
    reach = [0, 0, 0, 0]
    for cb, f in frames:
        for rows, ox, oy, own in (fixed[cb][f], plain[cb][f]):
            for y, r in enumerate(rows):
                for x, c in enumerate(r):
                    if c is not None:
                        ax, ay = x + ox - len(own[0]) // 2, len(own) - (y + oy)
                        reach = [min(reach[0], ax), max(reach[1], ax), max(reach[2], ay), min(reach[3], ay)]
    global CW, CH, BASE
    CW, CH, BASE = 2 * max(-reach[0], reach[1]) + 8, reach[2] - reach[3] + 8, reach[2] + 3
    per = max(1, min(len(frames), 2000 // (CW * zoom * kinds)))
    lines = (len(frames) + per - 1) // per
    TOP = 14
    small = Image.new("RGB", (per * kinds * CW, lines * CH), (196, 150, 104))
    cells = []
    for i, (cb, f) in enumerate(frames):
        rows, ox, oy, own = fixed[cb][f]
        raw = plain[cb][f][0]
        pics = [(own, 0, 0), (rows, ox, oy), (raw, ox, oy)] if compare else [(rows, ox, oy)]
        for k, (pic, dx, dy) in enumerate(pics):
            cx, cy = ((i % per) * kinds + k) * CW, (i // per) * CH
            bx, by = cx + CW // 2 - len(own[0]) // 2, cy + BASE - len(own)
            for y, r in enumerate(pic):
                for x, c in enumerate(r):
                    X, Y = bx + dx + x, by + dy + y
                    if c is not None and cx <= X < cx + CW and cy <= Y < cy + CH:
                        small.putpixel((X, Y), game.palette[c])
            cells.append((cx, cy, bx, by, cb, f, ("own", "corrected", "rules")[k] if compare else ""))
    img = Image.new("RGB", (small.width * zoom, lines * (CH * zoom + TOP)), (40, 30, 22))
    for line in range(lines):
        band = small.crop((0, line * CH, small.width, (line + 1) * CH)).resize((small.width * zoom, CH * zoom), Image.NEAREST)
        img.paste(band, (0, line * (CH * zoom + TOP) + TOP))
    d = ImageDraw.Draw(img)
    for cx, cy, bx, by, cb, f, kind in cells:
        X0, Y0 = cx * zoom, (cy // CH) * (CH * zoom + TOP) + TOP
        d.text((X0 + 3, Y0 - TOP + 1), f"{F.frame_name(cb, f)} {kind}", fill=(240, 230, 210))
        d.rectangle((X0, Y0, X0 + CW * zoom - 1, Y0 + CH * zoom - 1), outline=(40, 30, 22))
        if zoom >= 5:  # (ruled every 5 pixels of the figure's own frame)
            for x in range(-((bx - cx) // 5) * 5, CW - (bx - cx), 5):
                px = X0 + (bx - cx + x) * zoom
                d.line((px, Y0, px, Y0 + CH * zoom), fill=(150, 112, 78))
                d.text((px + 1, Y0 + 1), str(x), fill=(90, 60, 30))
            for y in range(-((by - cy) // 5) * 5, CH - (by - cy), 5):
                py = Y0 + (by - cy + y) * zoom
                d.line((X0, py, X0 + CW * zoom, py), fill=(150, 112, 78))
                d.text((X0 + 1, py + 1), str(y), fill=(90, 60, 30))
    img.save(path)
    print(path, img.size)


def grid(game: O.Game, outfit: str, figure: str, frame: str) -> None:
    npc, key = find(game, outfit, figure)
    kind, f = frame.split()
    cb = int(kind == "fight")
    rows, ox, oy, own = game.full(key, npc)[cb][int(f)]
    fix = game.fixes.get((O.OUTFITS[npc].name, figure, cb, int(f)), {})
    print(f"{O.OUTFITS[npc].name} / {figure} / {frame}: the figure's own frame is {len(own[0])} wide, {len(own)} tall; * a corrected pixel")
    cols = [x for x in range(len(rows[0])) if any(r[x] is not None for r in rows)]
    xs = range(max(0, min(cols) - 2), min(len(rows[0]), max(cols) + 3))
    print("   y\\x" + "".join(f"{x + ox:4} " for x in xs))
    for y, r in enumerate(rows):
        if any(c is not None for c in r) or any((x + ox, y + oy) in fix for x in xs):
            print(f"{y + oy:6}" + "".join(("   ." if r[x] is None else f"{r[x]:4}") + ("*" if (x + ox, y + oy) in fix else " ") for x in xs))


def faults(game: O.Game, outfit: str, figure: str) -> None:
    npc, key = find(game, outfit, figure)
    o, fig = O.OUTFITS[npc], game.fig(key)
    walk, fight = game.full(key, npc)
    for cb, frames in ((0, walk), (1, fight)):
        for f, (rows, _, _, own) in enumerate(frames):
            where: list = []
            C.frame_faults(rows, own, o, fig.parts(cb, f), where)
            stale = game.stale.get((o.name, figure, cb, f))
            if where or stale:
                by = {}
                for kind, x, y in where:
                    by.setdefault(kind, []).append(f"{x},{y}")
                print(f"{F.frame_name(cb, f):9}" + "; ".join(f"{k}: {' '.join(v)}" for k, v in by.items())
                      + (f"; STALE corrections: {' '.join(f'{x},{y}' for x, y in stale)}" if stale else ""))


def palette(game: O.Game, outfit: str) -> None:
    o = next(o for o in O.OUTFITS.values() if o.name.lower() == outfit.lower())
    for name, ramp in (("cloak", o.cloak), ("tunic", o.torso), ("sleeves", o.sleeves), ("leggings", o.legs), ("boots", o.boots)):
        if ramp:
            print(f"{name:9}" + "  ".join(f"{c} #{'%02x%02x%02x' % game.palette[c]}" for c in ramp))
    print("black (outlines, deep shadow) 254; skin 128-153 (129 darkest brown ... 151 lightest)")


def main(argv: List[str]) -> None:
    opts = {}
    args = []
    it = iter(argv)
    for a in it:
        if a in ("--fixes", "--zoom"):
            opts[a] = next(it)
        elif a == "--compare":
            opts[a] = True
        else:
            args.append(a)
    if len(args) < 3:
        raise SystemExit(__doc__)
    game = O.Game(args[0], F.read(opts["--fixes"]) if "--fixes" in opts else None)
    if args[1] == "view":
        view(game, args[2], args[3], args[4], frames_of(args[5] if len(args) > 5 else "w0-14,f0-13"),
             int(opts.get("--zoom", 6)), bool(opts.get("--compare")))
    elif args[1] == "grid":
        grid(game, args[2], args[3], args[4])
    elif args[1] == "faults":
        faults(game, args[2], args[3])
    elif args[1] == "palette":
        palette(game, args[2])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
