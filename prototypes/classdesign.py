"""Prototype, not part of the Ledger: a first design for each class, drafted on one figure (the
human man), to be looked at before any is carried to the other figures.

classfigures.py redrew the figures the way the half-elf was coloured and came out much as
outfits.py does; what made the half-elf a figure of its own was its design (the haircut, the
jerkin, the ears). So each class here has features drawn on the figure, by rule, placed by
outfitparts.py's reading of it:

  Warrior  the game's own warrior: the black harness kept, hip flaps of red-brown leather with a
           dark hem, a bone guard on one shoulder, leather bracers for the wristbands
  Thief    the hooded green cloak, a dark tunic and leggings, a belt with a pouch at the hip,
           the forearms wound with dark wrappings
  Priest   a red robe to the ankles all round (the legs under it, only the feet below), a pale
           stole down its front, a gold circlet at the brow
  Mage     the blue cloak, an ochre tunic with a skirt to the knee over green leggings, a belt
           with a gold buckle, a pale collar

    python3 prototypes/classdesign.py GAME_DIR OUT.png ["FIGURE"]

writes the figure's own pictures (top) and the four designs under them, ten frames each.
"""

import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import classfigures as C  # noqa: E402
import outfits as O  # noqa: E402

sg, sp, PAD = O.sg, O.sp, O.PAD
GOLD, PALE, BONE = (167, 169, 171), (206, 213, 215), (194, 206, 213, 215)
FLAP = (129, 128, 135, 137, 139)  # (the game's warrior's red-brown leather)
C.DETAILS["Warrior"] = C.Detail(None, None, None)
C.DETAILS["Thief"] = C.Detail((204, 207), None, None)
C.DETAILS["Priest"] = C.Detail(None, None, None)
C.DETAILS["Mage"] = C.Detail((204, 207), 167, (169, 168, 171))


class DesignGame(C.ClassGame):
    def dress(self, key, o, cb, f):
        out, ox, oy = super().dress(key, o, cb, f)
        fig = self.fig(key)
        own, p = fig.rows(cb, f), fig.parts(cb, f)
        if not (p.head and p.shoulders and p.waist is not None and p.facing):
            return out, ox, oy
        _, what = O.Game.clothe(self, own, fig, p, o, fig.bands(cb, f))
        draw = getattr(self, o.name.lower())
        draw(out, own, what, p)
        return out, ox, oy

    # shared pieces ------------------------------------------------------------------------------

    @staticmethod
    def put(out, x, y, c):
        if 0 <= y + PAD < len(out) and 0 <= x + PAD < len(out[0]):
            out[y + PAD][x + PAD] = c

    @staticmethod
    def at(out, x, y):
        return out[y + PAD][x + PAD] if 0 <= y + PAD < len(out) and 0 <= x + PAD < len(out[0]) else None

    def gown(self, out, what, p, ramp, reach: float, hem: int) -> None:
        """A skirt from the waist REACH of the way to the feet, all round: the legs within it and
        the gap between them in RAMP (a fold every fourth pixel below the hips, lighter to the left), a pixel
        past the legs each side, its last row HEM."""
        if p.facing == sp.BACK:
            return  # (from behind the cloak hangs over it)
        n = len(ramp)
        foot = p.waist + int(round(reach * (p.bottom - p.waist)))
        cx = (p.shoulders[1] + p.shoulders[2]) / 2
        for y in range(p.waist + 1, foot + 1):
            xs = [x for (x, yy), k in what.items() if yy == y and k in ("leg", "torso", "boot")]
            if not xs:
                continue
            for x in range(min(xs) - 1, max(xs) + 2):
                was = self.at(out, x, y)
                part = what.get((x, y))
                if was is not None and part not in ("leg", "torso", "boot", None):
                    continue  # (a hand or an arm before the skirt)
                t = n // 2 + (1 if x < cx - 1 else 0) - (1 if (x - int(cx)) % 4 == 0 and y > p.waist + 2 else 0)
                self.put(out, x, y, hem if y == foot else ramp[max(1, min(n - 1, t))])

    # the designs --------------------------------------------------------------------------------

    def warrior(self, out, own, what, p) -> None:
        sy, sa, sb = p.shoulders
        top = p.waist + 1
        low = p.waist + max(3, int(round(0.4 * (p.bottom - p.waist))))
        for (x, y), k in what.items():  # (the hip flaps: the thighs' top in red-brown leather, a dark hem)
            if k == "leg" and top <= y <= low and own[y][x] != 254:
                self.put(out, x, y, 129 if y == low else O.tone(own[y][x], FLAP))
            elif k == "hand" and own[y][x] not in O.SKINC:
                self.put(out, x, y, 205 if O.light(own[y][x]) > 0.3 else 204)  # (leather bracers)
        if p.facing == sp.SIDE:
            xs = [sa + (sb - sa) // 2 - 1, sa + (sb - sa) // 2, sa + (sb - sa) // 2 + 1]
        else:  # (on his right shoulder: the viewer's left from the front, right from behind)
            xs = [sa + 1, sa + 2, sa + 3] if p.facing == sp.FRONT else [sb - 3, sb - 2, sb - 1]
        for i, x in enumerate(xs):  # (a bone guard on one shoulder)
            if self.at(out, x, sy) is not None:
                self.put(out, x, sy, BONE[3 - i if p.facing != sp.FRONT else i + 1])
            if self.at(out, x, sy + 1) is not None:
                self.put(out, x, sy + 1, BONE[0] if i != 1 else BONE[1])

    def thief(self, out, own, what, p) -> None:
        for (x, y), k in what.items():  # (the forearms wound with dark wrappings: every other row)
            if k == "forearm" and own[y][x] in O.SKINC and (y + x // 3) % 2 == 0:
                self.put(out, x, y, 210 if O.light(own[y][x]) > 0.45 else 69)
        y = p.waist  # (a pouch at the hip, under the belt)
        xs = sorted(x for (x, yy), k in what.items() if yy == y and k in ("torso", "leg"))
        if len(xs) >= 4:
            x = xs[-2] if p.facing != sp.BACK else xs[1]
            for dx, dy, c in ((0, 0, 205), (-1, 0, 207), (0, 1, 207), (-1, 1, 204)):
                if self.at(out, x + dx, y + dy) is not None:
                    self.put(out, x + dx, y + dy, c)

    def priest(self, out, own, what, p) -> None:
        o = O.OUTFITS[1563]
        self.gown(out, what, p, o.cloak, 0.82, o.cloak[1])
        sy, sa, sb = p.shoulders
        h = p.head
        mid = int(round((h.left + h.right) / 2))
        foot = p.waist + int(round(0.82 * (p.bottom - p.waist)))
        if p.facing == sp.FRONT:  # (a pale stole down the front, from the neck to the hem)
            for y in range(sy, foot):
                for x, c in ((mid, PALE[1]),):
                    if self.at(out, x, y) is not None and what.get((x, y)) not in ("hand", "forearm", "head"):
                        self.put(out, x, y, c)
        elif p.facing == sp.SIDE:
            for y in range(sy + 1, foot):
                xs = [x for x in range(sa, sb + 2) if self.at(out, x, y) is not None and what.get((x, y)) not in ("hand", "forearm", "head")]
                if xs:
                    self.put(out, max(xs), y, PALE[0])
        for x in range(h.left, h.right + 1):  # (a gold circlet at the brow)
            if own[h.brow][x] is not None if 0 <= x < len(own[0]) else False:
                if p.facing == sp.SIDE and x < mid:
                    continue
                self.put(out, x, h.brow, GOLD[1] if (x - h.left) % 2 else GOLD[2])

    def mage(self, out, own, what, p) -> None:
        o = O.OUTFITS[724]
        self.gown(out, what, p, o.torso, 0.45, o.torso[1])


def main(argv: List[str]) -> None:
    from PIL import Image, ImageDraw, ImageFont
    if len(argv) < 2:
        raise SystemExit(__doc__)
    game = DesignGame(argv[0])
    figure = argv[2] if len(argv) > 2 else "human man"
    key = next(k for k, n in O.FIGURES if n == figure)
    cols = [(0, 0), (0, 1), (0, 2), (0, 4), (0, 8), (0, 12), (1, 1), (1, 4), (1, 7), (1, 12)]
    names = ["front", "back", "side", "walk", "walk", "walk", "attack", "attack", "attack", "hit"]
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    ink, ground = (40, 24, 12), (196, 150, 104)
    Z, CW, CH, BASE, LW, TOP = 4, 44, 56, 50, 110, 30
    rows_ = ["the game's own"] + [o.name for o in O.OUTFITS.values()]
    img = Image.new("RGB", (LW + len(cols) * CW * Z, TOP + len(rows_) * CH * Z), ground)
    d = ImageDraw.Draw(img)
    for ci, n in enumerate(names):
        d.text((LW + ci * CW * Z + CW * Z // 2 - 20, 8), n, fill=ink, font=font)
    fig = game.fig(key)
    for ri, label in enumerate(rows_):
        tile = Image.new("RGB", (len(cols) * CW, CH), ground)
        full = None if ri == 0 else game.full(key, list(O.OUTFITS)[ri - 1])
        for ci, (cb, f) in enumerate(cols):
            own = fig.rows(cb, f)
            rows, ox, oy = (own, 0, 0) if full is None else full[cb][f][:3]
            bx, by = ci * CW + CW // 2 - len(own[0]) // 2 + ox, BASE - len(own) + oy
            for y, r in enumerate(rows):
                for x, c in enumerate(r):
                    if c is not None and 0 <= bx + x < tile.width and 0 <= by + y < CH:
                        tile.putpixel((bx + x, by + y), game.palette[c])
        img.paste(tile.resize((tile.width * Z, CH * Z), Image.NEAREST), (LW, TOP + ri * CH * Z))
        d.text((6, TOP + ri * CH * Z + CH * Z // 2 - 8), label, fill=ink, font=font)
    img.save(argv[1], optimize=True)
    print(argv[1], img.size)


if __name__ == "__main__":
    main(sys.argv[1:])
