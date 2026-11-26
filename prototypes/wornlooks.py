"""Prototype, not part of the Ledger: the party's figures by what they wear, as Baldur's Gate does
it, sketched on one figure (the human man) to be looked at before anything goes into the Loader.

The Loader already dresses the party by its gear (dsloader/spritegear.py), but only recolours the
clothes a figure already has: it never covers skin, so a bare-chested man in scale armour is still
bare-chested, and nothing changes the figure's outline. The class drafts (classdesign.py) showed
that the outline and the mass of colour are what read at the game's size. So each weight of armour
here gets a shape of its own, in the material colours spritegear already uses:

  Robe            (the Ashen and Veiled Robes) a closed robe to the ankles all round, sleeves to the
                  wrist, a sash at the waist
  Leather         a jerkin over the chest and leggings, the arms bare, a belt
  Bone scale      (ring, brigandine, scale: bone on Athas) the chest and legs in bone scales, a
                  guard on each shoulder past the shoulder line, a skirt of bone flaps at the hips,
                  and the Bone Helm: a cap over the crown with a rim at the brow
  Chain           (the rare metal armour) a mail shirt with sleeves to the wrist, mail leggings and
                  a mail hood (coif) over the head, the face left
  Cloak and hood  a cloak (the game's thief's, as the artist drew it swinging) in leather browns,
                  its hood up, over the leather

    python3 prototypes/wornlooks.py GAME_DIR OUT.png ["FIGURE"]

writes the figure's own pictures (top), the Loader's drawing of leather and of bone scale today
(spritegear.armed, for comparison), and each look under them, ten frames each.
"""

import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import classfigures as C  # noqa: E402
import outfits as O  # noqa: E402

sg, sp, PAD = O.sg, O.sp, O.PAD

LEATHER = (129, 204, 207, 205, 194, 206)
BONE = sg.BONE_SHADES  # (207, 194, 206, 213, 214, 215)
BONE_DARK = 205
CHAIN = (254,) + sg.CHAIN_SHADES  # (209 .. 214, black for the coif's inside)
ASH = (210, 211, 212, 213, 214, 215)  # (ash grey cloth, lit)
SASH = (129, 202, 195)
CLOAK = (254, 129, 204, 207, 205, 194, 206)
THIEF_CLOAK = O.OUTFITS[630].cloak_src

LOOKS = {
    "Robe": O.Outfit("Robe", 9001, None, frozenset(), False, False,
                     ASH, ASH, 0, ASH, (69, 210, 194, 213), True),
    "Leather": O.Outfit("Leather", 9002, None, frozenset(), False, False,
                        LEATHER, None, 0, LEATHER, LEATHER[:4], True),
    "Bone scale": O.Outfit("Bone scale", 9003, None, frozenset(), False, False,
                           BONE, None, 0, BONE, LEATHER[:4], True),
    "Chain": O.Outfit("Chain", 9004, None, frozenset(), False, False,
                      sg.CHAIN_SHADES, sg.CHAIN_SHADES, 0, sg.CHAIN_SHADES, (254, 208, 209), True),
    "Cloak and hood": O.Outfit("Cloak and hood", 630, CLOAK, THIEF_CLOAK, True, False,
                               LEATHER, None, 0, LEATHER, LEATHER[:4], True),
}
for _k, _o in LOOKS.items():
    O.OUTFITS[_o.npc] = _o
C.DETAILS.update({
    "Robe": C.Detail(None, None, None),
    "Leather": C.Detail((254, 204), 213, None),
    "Bone scale": C.Detail((254, 204), 213, None),
    "Chain": C.Detail((254, 204), 213, None),
    "Cloak and hood": C.Detail((254, 204), 213, None),
})
PATTERN = {"Bone scale": sg.SCALES, "Chain": sg.CHAIN}


class WornGame(C.ClassGame):
    def dress(self, key, o, cb, f):
        out, ox, oy = super().dress(key, o, cb, f)
        fig = self.fig(key)
        own, p = fig.rows(cb, f), fig.parts(cb, f)
        if not (p.head and p.shoulders and p.waist is not None and p.facing):
            return out, ox, oy
        _, what = O.Game.clothe(self, own, fig, p, o, fig.bands(cb, f))
        if o.name in PATTERN:
            self.pattern(out, own, what, LOOKS[o.name].torso, PATTERN[o.name])
        if o.name == "Robe":
            self.gown(out, what, p, ASH, 0.76, ASH[0], bool(cb) and f == 12)
            self.sash(out, own, what, p)
        elif o.name == "Bone scale":
            self.flaps(out, own, what, p)
            self.guards(out, p)
            self.helm(out, own, p)
        elif o.name == "Cloak and hood" and p.facing == sp.SIDE:
            base, _, _ = super().dress(key, LOOKS["Leather"], cb, f)
            self.thicken(out, base, p)
        elif o.name == "Chain":  # (the coif: outfits.py's hood, in mail)
            bow = self.bow(fig, own, p) if cb and f in sp.BOW_FRAMES else frozenset()
            self.hood(out, own, p, o._replace(cloak=CHAIN), fig, bow)
        return out, ox, oy

    # pieces -------------------------------------------------------------------------------------

    @staticmethod
    def put(out, x, y, c):
        if 0 <= y + PAD < len(out) and 0 <= x + PAD < len(out[0]):
            out[y + PAD][x + PAD] = c

    @staticmethod
    def at(out, x, y):
        return out[y + PAD][x + PAD] if 0 <= y + PAD < len(out) and 0 <= x + PAD < len(out[0]) else None

    def pattern(self, out, own, what, ramp, pattern) -> None:
        """The armour's weave or scales on its lighter shades (spritegear's own pattern)."""
        top = len(ramp) - 1
        for (x, y), k in what.items():
            c = self.at(out, x, y)
            if k in ("torso", "leg", "arm") and c in ramp:
                self.put(out, x, y, ramp[sg._pattern(pattern, x, y, ramp.index(c), top)])

    def gown(self, out, what, p, ramp, reach: float, hem: int, hit: bool = False) -> None:
        """A skirt from the waist REACH of the way to the feet, all round (from behind too), the
        feet showing below it: the legs within it and the gap between them in RAMP, folds on its
        lower part only, its last row HEM, broken by the ramp's darker shade and pulled in a pixel at
        each end (a soft hem, not a box's edge). It flares from the hips a pixel every fourth row,
        no wider: a leg striding past it shows below it as itself. From the side it flares only in
        front; at the back it falls nearly straight. HIT (the reeling frame, the body bent
        across): only the legs' own pixels, no skirt drawn round them."""
        n = len(ramp)
        foot = p.waist + int(round(reach * (p.bottom - p.waist)))
        hips = sorted(x for (x, yy), k in what.items() if yy == p.waist and k in ("torso", "leg"))
        if not hips:
            return
        cx = (hips[0] + hips[-1]) / 2
        half0 = (hips[-1] - hips[0]) / 2 + 1
        back = self.back_side(p) if p.facing == sp.SIDE else 0
        last = None
        for y in range(p.waist + 1, foot + 1):
            xs = [x for (x, yy), k in what.items() if yy == y and k in ("leg", "torso", "boot")]
            if not xs:
                continue
            grow = (y - p.waist) / 4
            half = half0 + grow
            lo, hi = max(min(xs) - 1, int(cx - half)), min(max(xs) + 1, int(cx + half + 0.5))
            if p.facing == sp.SIDE:  # (from the hips, the front flaring, the back nearly straight)
                lo = int(cx - half0 - (grow / 3 if back < 0 else grow))
                hi = int(cx + half0 + (grow / 3 if back > 0 else grow) + 0.5)
            if last is not None and not hit:  # (never narrower than the row above: no notches in its sides)
                lo, hi = min(lo, last[0]), max(hi, last[1])
            last = (lo, hi)
            if y == foot and hi - lo > 3:
                lo, hi = lo + 1, hi - 1  # (the hem's corners rounded)
            third = p.waist + (foot - p.waist) // 3
            for x in range(lo, hi + 1):
                was = self.at(out, x, y)
                part = what.get((x, y))
                if was is not None and part not in ("leg", "torso", "boot", None):
                    continue  # (a hand or an arm before the skirt)
                if hit and part not in ("leg", "torso", "boot"):
                    continue
                fold = (x - int(cx)) % 4 == 0 and y > third
                t = n // 2 + (1 if x < cx - 1 else 0) - (1 if fold else 0)
                if y == foot:
                    c = hem if x % 2 or x in (lo, hi) else ramp[max(1, min(n - 1, t - 1))]
                else:
                    c = ramp[max(1, min(n - 1, t))]
                self.put(out, x, y, c)

    @staticmethod
    def back_side(p) -> int:
        """From the side, which way the back is: the game's side frames all face right (it
        mirrors them for the left), so the back is to the left: -1. (Reading it from where the hair
        hangs failed: the half-giant's long hair reads as in front.)"""
        return -1

    def thicken(self, out, base, p) -> None:
        """From the side, the cloak a little fuller behind the back: past its back edge, one pixel
        more below the shoulders and two in the middle of its fall, in its edge's colour."""
        laid = {(x, y) for y, r in enumerate(out) for x, c in enumerate(r)
                if c is not None and (y >= len(base) or x >= len(base[y]) or base[y][x] != c)}
        if not laid:
            return
        back = self.back_side(p)
        ys = sorted({y for _, y in laid})
        neck = p.shoulders[0] + PAD
        rows = [y for y in ys if y > neck + 1]
        if not rows:
            return
        top, bottom = rows[0], rows[-1]
        for y in rows[:-1]:
            xs = [x for x, yy in laid if yy == y]
            edge = min(xs) if back < 0 else max(xs)
            mid = (top + bottom) / 2
            more = 2 if abs(y - mid) < (bottom - top) / 4 else 1
            for k in range(1, more + 1):
                x = edge + back * k
                if 0 <= x < len(out[y]) and out[y][x] is None:
                    out[y][x] = out[y][edge]

    def sash(self, out, own, what, p) -> None:
        """A red sash at the waist, two rows, its end hanging at the side from the front."""
        for dy in (-1, 0):
            y = p.waist + dy
            xs = sorted(x for (x, yy), k in what.items() if yy == y and k in ("torso", "leg"))
            for x in xs:
                self.put(out, x, y, SASH[0] if x in (xs[0], xs[-1]) else SASH[1 + (dy + 1)])
        if p.facing == sp.FRONT:
            xs = sorted(x for (x, yy), k in what.items() if yy == p.waist and k in ("torso", "leg"))
            if xs:
                x = xs[len(xs) * 2 // 3]
                for y in range(p.waist + 1, p.waist + 5):
                    self.put(out, x, y, SASH[1] if y % 2 else SASH[2])

    def flaps(self, out, own, what, p) -> None:
        """A skirt of bone flaps at the hips: the top of the legs and a pixel past them each side,
        split every third pixel, a dark hem."""
        top, low = p.waist + 1, p.waist + max(3, int(round(0.38 * (p.bottom - p.waist))))
        for y in range(top, low + 1):
            xs = [x for (x, yy), k in what.items() if yy == y and k in ("leg", "torso")]
            if not xs:
                continue
            for x in range(min(xs) - 1, max(xs) + 2):
                if self.at(out, x, y) is not None and what.get((x, y)) not in ("leg", "torso", None):
                    continue
                split = (x - min(xs)) % 3 == 2
                self.put(out, x, y, BONE_DARK if y == low or split else BONE[3 if y == top else 2])

    def guards(self, out, p) -> None:
        """A bone guard on each shoulder, out past the shoulder line (the outline changes): three
        rows, the top lit, a dark lower edge; from the side one guard on the near shoulder."""
        sy, sa, sb = p.shoulders
        gw = max(3, min(8, int(round(0.3 * (sb - sa)))))  # (the guard's width: by the figure's shoulders)
        over = max(1, gw // 3)  # (how far past the shoulder line)
        rows = 3 if gw < 5 else 4
        if p.facing == sp.SIDE:
            mid = (sa + sb) // 2
            spans = [(mid - gw // 2, mid - gw // 2 + gw)]
        else:
            spans = [(sa - over, sa - over + gw), (sb + over - gw, sb + over)]
        shades = (BONE[4], BONE[3], BONE[2], BONE[1])[:rows]
        for a, b in spans:  # (rounded: the top row a pixel in each end, the outer end of each row darker)
            outer = a if a < (sa + sb) / 2 else b
            for i, c in enumerate(shades):
                dy = i - 1
                y = sy + dy
                lo, hi = (a + 1, b - 1) if dy == -1 else (a, b)
                if i == rows - 1 and rows > 3:
                    lo, hi = (a + 1, b) if outer == b else (a, b - 1)  # (the lower edge tucked in)
                for x in range(lo, hi + 1):
                    self.put(out, x, y, BONE_DARK if x == outer and dy >= 0 and p.facing != sp.SIDE else c)

    def helm(self, out, own, p) -> None:
        """The Bone Helm: the crown above the brow in bone, rounded at the top, and a darker rim
        at the brow."""
        h = p.head
        brow = max(h.brow, h.top + 2)
        for y in range(h.top, brow + 1):
            xs = [x for x in range(h.left - 1, h.right + 2)
                  if 0 <= y < len(own) and 0 <= x < len(own[0]) and own[y][x] is not None]
            if not xs:
                continue
            a, b = min(xs), max(xs)
            if y == h.top:
                a, b = a + 1, b - 1  # (the crown rounded)
            for x in range(a, b + 1):
                if y == brow:
                    c = BONE[1]  # (the rim at the brow, no wider than the head: not a hat's brim)
                elif x == a or y == h.top:
                    c = BONE[4] if x != a else BONE[1]
                elif x == b:
                    c = BONE[1]
                else:
                    c = BONE[3] if (x - a) % 3 else BONE[5]
                self.put(out, x, y, c)


def main(argv: List[str]) -> None:
    from PIL import Image, ImageDraw, ImageFont
    if len(argv) < 2:
        raise SystemExit(__doc__)
    game = WornGame(argv[0])
    figure = argv[2] if len(argv) > 2 else "human man"
    key = next(k for k, n in O.FIGURES if n == figure)
    cols = [(0, 0), (0, 1), (0, 2), (0, 4), (0, 8), (0, 12), (1, 1), (1, 4), (1, 7), (1, 12)]
    names = ["front", "back", "side", "walk", "walk", "walk", "attack", "attack", "attack", "hit"]
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    ink, ground = (40, 24, 12), (196, 150, 104)
    Z, CW, CH, BASE, LW, TOP = 4, 44, 56, 50, 200, 30
    now = {"Loader now: leather": (6, 7, 8), "Loader now: bone scale": (15, 55, 56)}
    rows_ = ["nothing worn"] + list(now) + list(LOOKS)
    img = Image.new("RGB", (LW + len(cols) * CW * Z, TOP + len(rows_) * CH * Z), ground)
    d = ImageDraw.Draw(img)
    for ci, n in enumerate(names):
        d.text((LW + ci * CW * Z + CW * Z // 2 - 20, 8), n, fill=ink, font=font)
    fig = game.fig(key)
    for ri, label in enumerate(rows_):
        tile = Image.new("RGB", (len(cols) * CW, CH), ground)
        full = game.full(key, LOOKS[label].npc, fixed=False) if label in LOOKS else None
        for ci, (cb, f) in enumerate(cols):
            own = fig.rows(cb, f)
            rows, ox, oy = (own, 0, 0) if full is None else full[cb][f][:3]
            if label in now and isinstance(key, int):  # (the Loader's own drawing of that armour, for comparison;
                # a half-elf is a figure of the Loader's own, drawn by figures.py, not here)
                rows, ox, oy = sg.armed(own, key, f, bool(cb), {}, 10, now[label]), -10, -10
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
