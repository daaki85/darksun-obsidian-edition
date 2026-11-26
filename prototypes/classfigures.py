"""Prototype, not part of the Ledger: a figure for each class, made the way the Loader makes the
half-elves' (obsidian-edition/dsloader/figures.py), with the class in the race's place.

The half-elf man is the elf man's pictures redrawn: each part of him (hair, jerkin, sleeve, legs,
boots) has its own colours, and every colour the elf has in that part becomes one colour of the
part's ramp, the same in every frame; the artist's dither is kept; a linen V at the neck and a
belt with a buckle are drawn on. This does the same for a class, on any of the party's figures:

  * the parts are outfits.py's reading of the figure (chest, arm, leg, boot; outfitparts.py
    draws it), each part of each class with a ramp of its own;
  * a part's colours are counted over the figure's first seven walking frames and spread over
    the ramp by their brightness, darkest to lightest: a colour of the figure's is the same
    colour of the outfit wherever and whenever it is drawn, so nothing shimmers from frame to
    frame (outfits.py picks each pixel's shade by its brightness alone);
  * where two neighbours of a part differed in the figure's own picture and came out alike, the
    second is a shade lighter or darker, as it was (the dither kept);
  * each class has its details, drawn on the figure: a belt at the waist with a buckle (in front,
    seen from the front; at the front edge, from the side), and a collar at the neck from the
    front;
  * the cloak, hood, robe and the rest are outfits.py's.

    python3 prototypes/classfigures.py GAME_DIR OUT_DIR

writes OUT_DIR/class_<class>.png (the thirteen figures, as outfits.py's sheets) and
OUT_DIR/class_vs_outfit.png (three figures in each class: the game's own, outfits.py's, this).
Corrections by hand are not laid on: they were made on outfits.py's pictures.
"""

import collections
import os
import sys
from typing import Dict, List, NamedTuple, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import outfits as O  # noqa: E402

sg, sp = O.sg, O.sp


class Detail(NamedTuple):
    belt: Optional[Tuple[int, int]]  # its two shades, alternating along it
    buckle: Optional[int]
    collar: Optional[Tuple[int, int, int]]  # the V at the neck: its left, its right, its point


DETAILS: Dict[str, Detail] = {
    "Warrior": Detail((254, 208), 213, None),  # (a black strap, a steel buckle)
    "Thief": Detail((204, 207), 205, None),  # (a leather belt)
    "Priest": Detail(None, None, (169, 168, 171)),  # (a gold collar; a sash read as a dashed line)
    "Mage": Detail((204, 207), 167, (169, 168, 171)),  # (a leather belt, a gold buckle, a linen collar)
}
PART_RAMP = {"torso": "torso", "arm": "sleeves", "leg": "legs", "boot": "boots"}


class ClassGame(O.Game):
    """outfits.py's pictures with each part's colours mapped once for the figure, as the half-elf's."""

    def __init__(self, game_dir: str):
        super().__init__(game_dir, {})
        self._maps: Dict[Tuple[object, str], Dict[Tuple[str, int], int]] = {}

    def colour_map(self, fig: O.Figure, o: O.Outfit) -> Dict[Tuple[str, int], int]:
        """(part, the figure's colour) -> the outfit's: the part's colours in the first seven
        walking frames, by their brightness, spread over the part's ramp."""
        key = (fig.key, o.name)
        if key not in self._maps:
            seen: Dict[str, set] = collections.defaultdict(set)
            for f in range(7):
                own, p = fig.rows(0, f), fig.parts(0, f)
                if not (p.head and p.shoulders and p.waist is not None):
                    continue
                rows, what = O.Game.clothe(self, own, fig, p, o, fig.bands(0, f))
                for (x, y), k in what.items():
                    if k in PART_RAMP and own[y][x] != 254 and rows[y][x] != own[y][x]:
                        seen[k].add(own[y][x])
            out = {}
            for k, colours in seen.items():
                ramp = getattr(o, PART_RAMP[k])
                cs = sorted(colours, key=O.light)
                for i, c in enumerate(cs):
                    out[(k, c)] = ramp[min(len(ramp) - 1, int(i * len(ramp) / max(1, len(cs))))]
            self._maps[key] = out
        return self._maps[key]

    def clothe(self, own, fig, p, o, wrists, bow=frozenset()):
        rows, what = super().clothe(own, fig, p, o, wrists, bow)
        if not (p.head and p.shoulders and p.waist is not None):
            return rows, what
        cmap = self.colour_map(fig, o)
        mine = {}
        for (x, y), k in what.items():
            c = own[y][x]
            if k in PART_RAMP and c != 254 and rows[y][x] != c:
                ramp = getattr(o, PART_RAMP[k])
                if (k, c) not in cmap:  # (a colour the first frames didn't have: the nearest that they had)
                    known = [d for (kk, d) in cmap if kk == k]
                    cmap[(k, c)] = cmap[(k, min(known, key=lambda d: abs(O.light(d) - O.light(c))))] if known else rows[y][x]
                rows[y][x] = cmap[(k, c)]
                mine[(x, y)] = (k, ramp)
        for (x, y), (k, ramp) in mine.items():  # (the artist's dither kept: neighbours alike here, unlike in his)
            if (x - 1, y) in mine and mine[(x - 1, y)][0] == k and rows[y][x] == rows[y][x - 1] \
                    and own[y][x] != own[y][x - 1] and rows[y][x] in ramp:
                i = ramp.index(rows[y][x])
                j = i + 1 if O.light(own[y][x]) > O.light(own[y][x - 1]) else i - 1
                if 0 <= j < len(ramp):
                    rows[y][x] = ramp[j]
        self.details(rows, own, what, p, o)
        return rows, what

    @staticmethod
    def details(rows, own, what, p, o: O.Outfit) -> None:
        """The class's belt and buckle at the waist, and its collar at the neck from the front."""
        d = DETAILS[o.name]
        sy, sa, sb = p.shoulders
        mid = (p.head.left + p.head.right) / 2 if p.facing != sp.SIDE else (sa + sb) / 2
        y = p.waist - 1
        run = sg._torso_run(own, y, mid, sa, sb) if 0 <= y < len(own) else None
        if d.belt and run:
            cells = [x for x in range(run[0], run[1] + 1) if what.get((x, y)) == "torso"]
            for x in cells:
                rows[y][x] = d.belt[0] if x in (cells[0], cells[-1]) else d.belt[x % 2]
            if d.buckle is not None and len(cells) >= 3:
                if p.facing == sp.FRONT and int(round(mid)) in cells:
                    rows[y][int(round(mid))] = d.buckle
                elif p.facing == sp.SIDE:
                    rows[y][cells[-2]] = d.buckle
        if d.collar and p.facing == sp.FRONT:
            cx = int(round(mid))
            for dy, xs in ((0, (-1, 0, 1)), (1, (0,))):
                for dx in xs:
                    q = (cx + dx, sy + dy)
                    if what.get(q) == "torso":
                        rows[q[1]][q[0]] = d.collar[2] if dy else d.collar[0 if dx <= 0 else 1]


def main(argv: List[str]) -> None:
    from PIL import Image, ImageDraw, ImageFont
    if len(argv) < 2:
        raise SystemExit(__doc__)
    game, plain = ClassGame(argv[0]), O.Game(argv[0], {})
    os.makedirs(argv[1], exist_ok=True)
    for npc, o in O.OUTFITS.items():
        path = os.path.join(argv[1], f"class_{o.name.lower()}.png")
        O.sheet(game, npc, path)
        print(path)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    ink, ground = (40, 24, 12), (196, 150, 104)
    who = [(2095, "human man"), (2059, "elf woman"), (2093, "mul")]
    cols = [(0, 0), (0, 1), (0, 2), (0, 4), (0, 12), (1, 1)]
    Z, CW, CH, BASE = 5, 46, 58, 52
    img = Image.new("RGB", (170 + len(who) * len(cols) * CW * Z, 40 + len(O.OUTFITS) * 3 * CH * Z), ground)
    d = ImageDraw.Draw(img)
    for wi, (_, label) in enumerate(who):
        d.text((170 + wi * len(cols) * CW * Z + 8, 10), label + ": front, back, side, two walking, an attack", fill=ink, font=font)
    for i, (npc, o) in enumerate(O.OUTFITS.items()):
        for k, kind in enumerate(("the game's own", "outfits.py", "as the half-elf")):
            y0 = 40 + (i * 3 + k) * CH * Z
            d.text((8, y0 + CH * Z // 2 - 16), o.name, fill=ink, font=font)
            d.text((8, y0 + CH * Z // 2 + 2), kind, fill=ink, font=font)
            tile = Image.new("RGB", (len(who) * len(cols) * CW, CH), ground)
            for wi, (key, _) in enumerate(who):
                full = (plain, plain, game)[k].full(key, npc)
                for ci, (cb, f) in enumerate(cols):
                    rows, ox, oy, own = full[cb][f]
                    if k == 0:
                        rows, ox, oy = own, 0, 0
                    bx, by = (wi * len(cols) + ci) * CW + CW // 2 - len(own[0]) // 2 + ox, BASE - len(own) + oy
                    for y, r in enumerate(rows):
                        for x, c in enumerate(r):
                            if c is not None and 0 <= bx + x < tile.width and 0 <= by + y < CH:
                                tile.putpixel((bx + x, by + y), game.palette[c])
            img.paste(tile.resize((tile.width * Z, CH * Z), Image.NEAREST), (170, y0))
    path = os.path.join(argv[1], "class_vs_outfit.png")
    img.save(path, optimize=True)
    print(path)


if __name__ == "__main__":
    main(sys.argv[1:])
