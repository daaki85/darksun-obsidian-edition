"""Prototype, not part of the Ledger: every picture outfits.py makes, checked by rule, so the
ones worth a look are found without reading 1,500 pictures by eye (13 figures, 4 outfits, 29
frames). Each fault is counted in pixels and weighed; the worst frames are listed and drawn large
beside the figure's own picture.

    python3 prototypes/outfitcheck.py GAME_DIR OUT_DIR [HOW_MANY]

writes OUT_DIR/check.txt (every frame with a fault, worst first), OUT_DIR/check.png (the worst
HOW_MANY, default 40: the figure's own picture, then the outfit) and prints the totals by fault.

The faults:
  speck    a pixel in one of the outfit's shades with none of that garment round it
  hole     a pixel left as it was, ringed by the cloak
  scrap    a piece of the picture apart from the figure
  face     skin of the face (in the head's box, below the brow) in a garment's shade
  covered  far less skin showing than in the figure's other frames of that view (a face or
           hands taken for clothes)
  bare     skin showing where the clothes cover it, well past what the figure's other frames
           of that view show
  no cloak the outfit has a cloak and the frame shows next to none (the hit frame aside)
  flicker  the cloak's size jumping from one frame of a walk or a blow to the next, more than
           the person's own cloak does
"""

import collections
import os
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import outfits as O  # noqa: E402

WEIGHT = {"face": 4, "speck": 2, "hole": 3, "scrap": 1, "bare": 0.5, "covered": 1, "no cloak": 30, "flicker": 20}
CYCLES = [(0, (3, 4, 5, 6)), (0, (7, 8, 9, 10)), (0, (11, 12, 13, 14)), (1, (0, 1, 2)), (1, (3, 4, 5)), (1, (6, 7, 8))]


def garments(o: O.Outfit) -> List[frozenset]:
    return [frozenset(r) for r in (o.cloak, o.torso, o.sleeves, o.legs, o.boots) if r]


def frame_faults(rows: O.Rows, own: O.Rows, o: O.Outfit, p) -> Tuple[Dict[str, int], int, float]:
    """A dressed frame's faults, its cloak's size and how much of the figure's skin still shows."""
    P = O.PAD
    h, w = len(rows), len(rows[0])
    sets = garments(o)
    cloak = frozenset(o.cloak or ())

    def was(x, y):
        return own[y - P][x - P] if 0 <= y - P < len(own) and 0 <= x - P < len(own[0]) else None
    out = collections.Counter()
    area = 0
    for y in range(h):
        for x in range(w):
            c = rows[y][x]
            if c is None:
                continue
            near = [rows[y + b][x + a] for a in (-1, 0, 1) for b in (-1, 0, 1)
                    if (a or b) and 0 <= y + b < h and 0 <= x + a < w]
            if c != was(x, y):
                if any(c in s for s in sets) and was(x, y) in O.SKINC and p.head and p.shoulders and p.head.brow < y - P < p.shoulders[0] \
                        and p.head.left <= x - P <= p.head.right and (x - P, y - P) not in p.hair and not (
                            o.hood and (p.facing == O.sp.BACK or (p.facing == O.sp.SIDE and x - P <= (p.head.left + p.head.right) / 2))):
                    out["face"] += 1
                if c in cloak:
                    area += 1
                mine = [s for s in sets if c in s]
                before = was(x, y)  # (the figure's own clothes in other colours keep their own detail)
                if mine and (before is None or before in O.SKINC) and not any(n in s for n in near for s in mine):
                    out["speck"] += 1
            elif cloak and c not in cloak and c != 254 and sum(n in cloak for n in near) >= 7:
                out["hole"] += 1
    pieces = O.comps(O.sil(rows))
    if pieces:
        main = max(pieces, key=len)
        out["scrap"] += sum(len(c) for c in pieces if c is not main)
    skin_was = sum(c in O.SKINC for r in own for c in r)
    skin_now = sum(c in O.SKINC for r in rows for c in r)
    return out, area, skin_now / max(1, skin_was)


def check(game: O.Game) -> List[Tuple[float, str, object, int, int, Dict[str, int]]]:
    found = []
    for npc, o in O.OUTFITS.items():
        person = {}  # (the person's own cloak, frame by frame: how much it changes by itself)
        if o.cloak:
            for cb in (0, 1):
                for f in range(15 if not cb else 12):
                    person[(cb, f)] = len(game.cloak_layer(o, cb, f))
        for key, name in O.FIGURES:
            fig = game.fig(key)
            walk, fight = game.full(key, npc)
            got = {}
            for cb, frames in ((0, walk), (1, fight)):
                for f, (rows, _, _, own) in enumerate(frames):
                    got[(cb, f)] = frame_faults(rows, own, o, fig.parts(cb, f))
            faults = {k: collections.Counter(v[0]) for k, v in got.items()}
            if True:  # (bare, covered: against the figure's other frames of the same view)
                views = collections.defaultdict(list)
                for (cb, f), v in got.items():
                    facing = fig.parts(cb, f).facing
                    if facing and not (cb and f >= 12):
                        views[facing].append(((cb, f), v[2]))
                for group in views.values():
                    mid = sorted(r for _, r in group)[len(group) // 2]
                    for k, r in group:
                        if r > mid + 0.35:
                            faults[k]["bare"] = int(100 * (r - mid))
                        elif fig.parts(*k).facing != O.sp.BACK and (r < mid - 0.3 or (r < 0.05 and mid > 0.05)):  # (a cloak covers a back)
                            faults[k]["covered"] = int(100 * (mid - r))
            if o.cloak and not fig.cloak:
                for (cb, f), v in got.items():
                    if not (cb and f >= 12) and v[1] < 8:
                        faults[(cb, f)]["no cloak"] = 1
                for cb, cycle in CYCLES:
                    for a, b in zip(cycle, cycle[1:]):
                        mine = max(got[(cb, a)][1], got[(cb, b)][1]) / max(1, min(got[(cb, a)][1], got[(cb, b)][1]))
                        theirs = max(person[(cb, a)], person[(cb, b)]) / max(1, min(person[(cb, a)], person[(cb, b)]))
                        if mine > 1.6 * theirs and abs(got[(cb, a)][1] - got[(cb, b)][1]) > 25:
                            faults[(cb, b)]["flicker"] = 1
            for (cb, f), c in faults.items():
                score = sum(WEIGHT[k] * n for k, n in c.items())
                if score:
                    found.append((score, o.name, key, cb, f, dict(c)))
    found.sort(key=lambda t: -t[0])
    return found


def label(key) -> str:
    return dict(O.FIGURES)[key]


def picture(game: O.Game, found: List, path: str) -> None:
    from PIL import Image, ImageDraw
    Z, CW, CH, BASE, PER = 6, 110, 74, 60, 5
    rows_n = (len(found) + PER - 1) // PER
    img = Image.new("RGB", (PER * CW * Z, rows_n * CH * Z), (196, 150, 104))
    small = Image.new("RGB", (PER * CW, rows_n * CH), (196, 150, 104))
    npcs = {o.name: n for n, o in O.OUTFITS.items()}
    for i, (_, outfit, key, cb, f, _) in enumerate(found):
        ox0, oy0 = (i % PER) * CW, (i // PER) * CH
        rows, ox, oy, own = game.full(key, npcs[outfit])[cb][f]
        for k, (pic, dx, dy) in enumerate(((own, 0, 0), (rows, ox, oy))):
            bx, by = ox0 + 28 + k * 54 - len(own[0]) // 2 + dx, oy0 + BASE - len(own) + dy
            for y, r in enumerate(pic):
                for x, c in enumerate(r):
                    if c is not None and 0 <= bx + x < small.width and 0 <= by + y < small.height:
                        small.putpixel((bx + x, by + y), game.palette[c])
    img.paste(small.resize(img.size, Image.NEAREST))
    d = ImageDraw.Draw(img)
    for i, (score, outfit, key, cb, f, c) in enumerate(found):
        x, y = (i % PER) * CW * Z + 6, (i // PER) * CH * Z + 4
        d.text((x, y), f"{i + 1}. {outfit}, {label(key)}, {'fight' if cb else 'walk'} {f}", fill=(40, 24, 12))
        d.text((x, y + 12), ", ".join(f"{k} {n}" for k, n in c.items()), fill=(120, 20, 20))
    img.save(path, optimize=True)


def main(argv: List[str]) -> None:
    if len(argv) < 2:
        raise SystemExit(__doc__)
    game = O.Game(argv[0])
    os.makedirs(argv[1], exist_ok=True)
    found = check(game)
    with open(os.path.join(argv[1], "check.txt"), "w") as out:
        for score, outfit, key, cb, f, c in found:
            out.write(f"{score:6.1f}  {outfit:8} {label(key):17} {'fight' if cb else 'walk':5} {f:2}  "
                      + ", ".join(f"{k} {n}" for k, n in c.items()) + "\n")
    total = collections.Counter()
    for _, _, _, _, _, c in found:
        for k, n in c.items():
            total[k] += n
    frames = len(O.OUTFITS) * len(O.FIGURES) * 29
    print(f"{len(found)} of {frames} frames with a fault; " + ", ".join(f"{k} {n}" for k, n in total.most_common()))
    picture(game, found[:int(argv[2]) if len(argv) > 2 else 40], os.path.join(argv[1], "check.png"))


if __name__ == "__main__":
    main(sys.argv[1:])
