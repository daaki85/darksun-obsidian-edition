"""Prototype, not part of the Ledger: class outfits for the party's figures, from the clothes of
the game's own people.

Four of the game's people (SEGOBJEX's 15-frame figures) are the party's human man (picture 2095)
redrawn in other clothes, frame for frame: a warrior in leather (1252), a thief in a hooded green
cloak (630), a priest in a red robe (1563), a mage in a blue cloak (724). Each is an outfit here,
and every party figure can wear it, in all its pictures (15 walking, 14 fighting):

  * the figure's own picture is the base, pixel for pixel, so each keeps its build, face, hair and
    the artist's shading. Its clothes, and the skin the outfit covers, take the outfit's colours
    shade for shade, by the part of the body they are on: tunic, sleeves (the arms are followed
    from the hands), leggings, boots;
  * the cloak is the person's own, as the artist drew it swinging in that frame (the weapon the
    person carries erased first), laid on the figure by its landmarks (head, neck, waist, feet:
    spriteparts.py). On a body of another size it is not stretched pixel by pixel (which doubles
    its fold lines into stripes): its shading is resampled and drawn again in the cloak's own
    shades. From behind it covers the back, under the hair; from the front it hangs behind the
    body (a robe closes over it); from the side it covers the back half;
  * the human woman's own cloak (the game draws her in one) takes the outfit's colours instead;
  * a hood worn up (the thief's) is the figure's own hair and crown in the cloak's shades, a
    pixel fuller, the face left;
  * the hit frame (12), which the game's people don't have, is the figure's own, the cloak that of
    the person standing; the dead frame (13) is the figure's own corpse in the outfit's colours,
    a cloak spread on the ground round it.

Nothing of the game's is in the repository: the pictures are read from the player's install.

    python3 prototypes/outfits.py GAME_DIR OUT_DIR [NPC ...]

writes OUT_DIR/outfit_<npc>.png for each (default: 1252 warrior, 630 thief, 1563 priest, 724
mage) on the eleven figures, each frame drawn where the game would put it (its picture's anchor,
the bottom middle of the figure's own picture).
"""

import collections
import math
import os
import struct
import sys
from typing import Dict, FrozenSet, List, NamedTuple, Optional, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "obsidian-edition"))

from dsloader import art, gff, spritegear as sg, spriteparts as sp  # noqa: E402

Rows = List[List[Optional[int]]]
Cell = Tuple[int, int]
MAN = 2095
BLADE = {214, 46, 212, 78}
STAFF = set(range(128, 142)) | {181, 182, 212, 213, 214}  # (724's staff: wood browns, bone greys)
EXTRA = {724: STAFF}
SKINC = set(range(128, 154))
WOMAN_CLOAK = {53, 54, 55, 56, 188, 189, 190, 191, 42}
BANDS = {249: 214, 250: 212}  # (the green wristbands steel, on every class)
DARK = {254, 69, 129, 158}  # (a cloak's fold lines)
BOW = {179, 180, 181, 182, 183}
PAD = 8


class Outfit(NamedTuple):
    """A class's clothes. Each ramp is palette colours, dark to light."""
    name: str
    npc: int  # the person whose clothes they are
    cloak: Optional[Tuple[int, ...]]
    cloak_src: FrozenSet[int]  # the cloak's colours in the person's pictures
    hood: bool  # worn up
    closed: bool  # the cloak closes over the body in front (a robe)
    torso: Tuple[int, ...]
    sleeves: Optional[Tuple[int, ...]]
    sleeve_from: float  # how far up the arm from the hand the sleeve starts (0: at the wrist)
    legs: Optional[Tuple[int, ...]]
    boots: Optional[Tuple[int, ...]]
    cover: bool  # the clothes cover the skin too (else only the figure's own clothes change)


OUTFITS: Dict[int, Outfit] = {o.npc: o for o in (
    Outfit("Warrior", 1252, None, frozenset(), False, False,
           (204, 207, 205, 180, 201), None, 0, (204, 207, 205, 180, 201), (204, 207, 205, 194), False),
    Outfit("Thief", 630, (69, 188, 53, 189, 54, 190, 55), frozenset((53, 54, 55, 56, 188, 189, 190, 191)), True, False,
           (158, 69, 210, 49, 24, 50), None, 0, (158, 69, 210, 70, 194, 50), (69, 48, 210, 49), True),
    Outfit("Priest", 1563, (129, 202, 195, 163, 76, 32, 77, 164),
           frozenset((202, 163, 32, 77, 164, 195, 76, 137, 136, 44)), False, True,
           (129, 202, 195, 163, 32, 77), (129, 202, 195, 163, 32, 77), 0, (129, 202, 195, 163), (69, 210, 194, 213), True),
    Outfit("Mage", 724, (158, 159, 38, 160, 71, 161), frozenset((158, 159, 38, 39, 160, 161, 71, 40, 70)), False, False,
           (129, 128, 205, 180, 201, 200), (158, 159, 38, 160, 71, 161), 0, (188, 53, 189, 54, 55, 56),
           (204, 129, 134, 136, 138), True),
)}


class Game:
    def __init__(self, game_dir: str):
        def load(name):
            path = art._find(game_dir, name)
            if not path:
                raise SystemExit(f"no {name} in {game_dir}")
            with open(path, "rb") as f:
                return gff.read_gff(f.read())
        self.chunks = load("SEGOBJEX.GFF")
        self.palette = art.palette_colours(load("GPLDATA.GFF")[("PAL ", art.PORTRAIT_PALETTE)])
        sg.set_palette(self.palette)
        self._frames: Dict[Tuple[int, int], Rows] = {}
        self._align: Dict[Tuple[int, int, int, int], Tuple[int, int]] = {}
        self._erased: Dict[Tuple[int, int, int], Tuple[Rows, Set]] = {}
        self._layer: Dict[Tuple[int, int, int], Dict[Cell, int]] = {}
        self._bow: Dict[int, Set[int]] = {}

    def fr(self, pic: int, f: int) -> Rows:
        if (pic, f) not in self._frames:
            self._frames[(pic, f)] = art.decode_frame(self.chunks[("BMP ", pic)], f)[2]
        return self._frames[(pic, f)]

    def count(self, pic: int) -> int:
        return struct.unpack_from("<H", self.chunks[("BMP ", pic)], 4)[0]

    def align(self, a_pic: int, b_pic: int, f: int) -> Tuple[int, int]:
        """(dx, dy): B's pixel (x, y) is A's (x + dx, y + dy), where their outlines overlap most."""
        key = (a_pic, b_pic, f, 0)
        if key not in self._align:
            A, B = sil(self.fr(a_pic, f)), sil(self.fr(b_pic, f))
            best = max(((len({(x + dx, y + dy) for x, y in B} & A), dx, dy)
                        for dx in range(-12, 13) for dy in range(-12, 13)))
            self._align[key] = (best[1], best[2])
        return self._align[key]

    # the weapon erased --------------------------------------------------------------------------

    def erased(self, npc: int, cb: int, f: int) -> Tuple[Rows, Set]:
        """NPC's frame (walking, or fighting: CB) without its weapon, and the pixels taken."""
        key = (npc, cb, f)
        if key in self._erased:
            return self._erased[key]
        human, rows0 = self.fr(MAN + cb, f), self.fr(npc + cb, f)
        dx, dy = self.align(MAN + cb, npc + cb, f)
        A = sil(human)
        cols = {(x, y): p for y, r in enumerate(rows0) for x, p in enumerate(r) if p is not None}
        outside = {q for q in cols if (q[0] + dx, q[1] + dy) not in A}
        wset = BLADE | EXTRA.get(npc, set())
        gone: Set = set()
        for comp in comps({q for q in outside if cols[q] in wset}):
            if len(comp) >= 3 or any(cols[q] in (46, 214) for q in comp):
                gone |= comp
        grow = True
        while grow:  # (the blade where it crosses the body)
            grow = False
            for (x, y), p in cols.items():
                if (x, y) not in gone and p in BLADE and any((x + a, y + b) in gone for a in (-1, 0, 1) for b in (-1, 0, 1)):
                    gone.add((x, y))
                    grow = True
        rows = [list(r) for r in rows0]
        under = []
        for x, y in gone:
            if (x + dx, y + dy) in A:
                under.append((x, y))
            rows[y][x] = None
        todo = set(under)
        while todo:  # (the body under it, from its neighbours)
            done = set()
            for x, y in todo:
                near = [rows[y + b][x + a] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))
                        if 0 <= y + b < len(rows) and 0 <= x + a < len(rows[0]) and rows[y + b][x + a] is not None
                        and (x + a, y + b) not in todo]
                if near:
                    rows[y][x] = collections.Counter(near).most_common(1)[0][0]
                    done.add((x, y))
            if not done:
                break
            todo -= done
        tidy(rows, 4)  # (the weapon's trail)
        self._erased[key] = (rows, gone)
        return rows, gone

    # the cloak ----------------------------------------------------------------------------------

    def cloak_layer(self, o: Outfit, cb: int, f: int) -> Dict[Cell, int]:
        """The person's cloak alone in one frame, in the man's frame's place: its colours where
        they aren't the man's own, and the dark fold lines among them."""
        key = (o.npc, cb, f)
        if key not in self._layer:
            human = self.fr(MAN + cb, f)
            b, _ = self.erased(o.npc, cb, f)
            dx, dy = self.align(MAN + cb, o.npc + cb, f)
            cols = {(X + dx, Y + dy): q for Y, r in enumerate(b) for X, q in enumerate(r) if q is not None}

            def man(q):
                return human[q[1]][q[0]] if 0 <= q[1] < len(human) and 0 <= q[0] < len(human[0]) else None
            cand = {q for q, c in cols.items() if c in o.cloak_src and man(q) != c}
            core = {q for q in cand if light(cols[q]) < 0.34}  # (its light shades alone are a weapon's trail)
            cand = {q for q in cand if q in core or any((q[0] + a, q[1] + b_) in core for a in range(-2, 3) for b_ in range(-2, 3))}
            cells = set()
            for comp in comps(cand):
                if len(comp) >= 6:
                    cells |= comp
            near8 = [(a, b_) for a in (-1, 0, 1) for b_ in (-1, 0, 1) if a or b_]
            grow = True
            while grow:  # (its shadowed inside and fold lines: dark, past the man's outline; holes over him)
                grow = False
                for q, c in cols.items():
                    if q in cells or c not in DARK:
                        continue
                    n = sum((q[0] + a, q[1] + b_) in cells for a, b_ in near8)
                    if n >= (1 if man(q) is None else 5):
                        cells.add(q)
                        grow = True
            layer = {q: cols[q] for q in cells}
            for _ in range(3):  # (holes: where the weapon was, or a pixel the man has too)
                xs, ys = [x for x, _ in layer], [y for _, y in layer]
                add = {}
                for y in range(min(ys), max(ys) + 1):
                    for x in range(min(xs), max(xs) + 1):
                        if (x, y) not in layer:
                            near = [layer[(x + a, y + b_)] for a, b_ in near8 if (x + a, y + b_) in layer]
                            if len(near) >= 5:
                                add[(x, y)] = collections.Counter(near).most_common(1)[0][0]
                if not add:
                    break
                layer.update(add)
            pm = parts(human, MAN, f, bool(cb))
            drop = set()
            if pm.facing in (sp.FRONT, sp.SIDE) and pm.head and pm.shoulders and pm.waist is not None:
                # (a sleeve down the forearm lies where the man's arm is, not the figure's: the
                # figure's own arm takes the sleeve's colours instead)
                far = 0.6 * max(4, pm.waist - pm.shoulders[0])
                drop = {q for q, d in self.arms(human, pm, sg._keep_out(human, pm)).items() if d <= far}
            if cb and f in sp.BOW_FRAMES:  # (the person's bow, drawn in the cloak's colours, where the man's is)
                drop |= {(x + a, y) for y, r in enumerate(human) for x, c in enumerate(r) if c in BOW
                         for a in (-2, -1, 0, 1, 2)}
            if drop:  # (and the sleeve's lit edge beside the arm; not the cloak's dark inside)
                gone = {q for q in layer if q in drop or (layer[q] not in DARK and any(
                    (q[0] + a, q[1] + b_) in drop for a in (-1, 0, 1) for b_ in (-1, 0, 1)))}
                rest = set(layer) - gone
                layer = {q: layer[q] for comp in comps(rest) if len(comp) >= 10 for q in comp}
            self._layer[key] = layer
        return self._layer[key]

    def her_cloak(self, cb: int, f: int) -> Dict[Cell, int]:
        """The human woman's own cloak in one of her frames, its fold lines with it."""
        rows = self.fr(sg.CLOAK_MODEL + cb, f)
        cloak = {(x, y): c for y, r in enumerate(rows) for x, c in enumerate(r) if c in WOMAN_CLOAK}
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c == 254 and sum((x + a, y + b) in cloak for a in (-1, 0, 1) for b in (-1, 0, 1)) >= 3:
                    cloak[(x, y)] = 254
        return cloak

    def warp(self, layer: Dict[Cell, int], ramp: Tuple[int, ...], ms: dict, mt: dict, k: float,
             w: int, h: int) -> Dict[Cell, int]:
        """LAYER (in the man's frame) laid on a figure's frame of W by H by their landmarks: each
        pixel of the figure's picture (and PAD round it) takes the cloak's shade at the same place,
        blended from the four pixels round it and drawn in the nearest of RAMP's shades."""
        lum = {q: (0.0 if c == 254 else light(c)) for q, c in layer.items()}
        shades = [(light(c), c) for c in ramp]
        out: Dict[Cell, int] = {}
        snap_x = abs(k - 1) < 0.05
        for y in range(-PAD, h + PAD):
            sy = _pw(y, ms, mt)
            if abs(_pw(y + 1, ms, mt) - sy - 1) < 0.08:
                sy = round(sy)
            y0 = math.floor(sy)
            fy = sy - y0
            for x in range(-PAD, w + PAD):
                sx = ms["cx"] + (x - mt["cx"]) * k
                if snap_x:
                    sx = math.floor(sx + 0.5)
                x0 = math.floor(sx)
                fx = sx - x0
                m = v = 0.0
                exact = None
                for a, b, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
                    q = (x0 + a, y0 + b)
                    if wt > 0 and q in layer:
                        m += wt
                        v += wt * lum[q]
                        if wt > 0.999:
                            exact = q
                if m < 0.5:
                    continue
                if exact is not None:
                    c = layer[exact]
                    out[(x, y)] = c if c in ramp or c == 254 else min(shades, key=lambda s: abs(s[0] - lum[exact]))[1]
                    continue
                v /= m
                out[(x, y)] = 254 if v < 0.02 else min(shades, key=lambda s: abs(s[0] - v))[1]
        return out

    # the clothes --------------------------------------------------------------------------------

    def arms(self, own: Rows, p, keep: Set[Cell], bands: FrozenSet[int] = frozenset()) -> Dict[Cell, int]:
        """The arms' skin: each pixel reached from a hand through skin, and how far along."""
        sy, sa, sb = p.shoulders
        side = p.facing == sp.SIDE
        reach = max(4, p.waist - sy) * (1 if side else 1.5)
        cx = (p.head.left + p.head.right) / 2
        core = 0.3 * (sb - sa)  # (the chest and thighs between the arms, seen from the front or behind)
        out: Dict[Cell, int] = {}

        chest = {}  # (each row's run through the body's middle: its middle three fifths are the chest)
        for y in range(sy, p.waist + 1):
            run = sg._torso_run(own, y, cx, sa, sb)
            if run and run[1] - run[0] >= 0.4 * (sb - sa):
                chest[y] = ((run[0] + run[1]) / 2, 0.3 * (run[1] - run[0]))

        def skin(q):
            x, y = q
            if not (0 <= y < len(own) and 0 <= x < len(own[0]) and (own[y][x] in SKINC or own[y][x] in BANDS)) or q in keep:
                return False
            if side:
                return y >= sy
            return not (y >= sy and abs(x - cx) <= core) and not (y in chest and abs(x - chest[y][0]) <= chest[y][1])
        starts = []
        for hx, hy in p.hands.values():
            near = sorted((abs(a) + abs(b), (hx + a, hy + b)) for a in range(-2, 3) for b in range(-2, 3) if skin((hx + a, hy + b)))
            if near:
                starts.append(near[0][1])
        # (and from the green wristbands, where a hand isn't found: an arm flung out in a blow)
        starts += [(x, y) for y, r in enumerate(own) for x, c in enumerate(r) if c in BANDS and skin((x, y))]
        for start in starts:
            todo = collections.deque([(start, 0)])
            seen = {start}
            while todo:
                q, d = todo.popleft()
                if d < out.get(q, 99):
                    out[q] = d
                if d >= reach:
                    continue
                for a in (-1, 0, 1):
                    for b in (-1, 0, 1):
                        n = (q[0] + a, q[1] + b)
                        if n not in seen and (skin(n) or (d < 4 and n not in keep and 0 <= n[1] < len(own)
                                                          and 0 <= n[0] < len(own[0]) and own[n[1]][n[0]] in bands)):
                            seen.add(n)
                            todo.append((n, d + 1))
        return out

    def bow(self, model: int, own: Rows, p) -> Set[Cell]:
        """The bow in a bow frame: the colours MODEL's walking frames don't have, and its golden
        browns in thin pieces (a line a pixel or two wide), not hair."""
        if model not in self._bow:
            walking = {c for f in range(15) for r in self.fr(model, f) for c in r if c is not None}
            self._bow[model] = {c for f in sp.BOW_FRAMES for r in self.fr(model + 1, f) for c in r if c is not None} - walking
        out = {(x, y) for y, r in enumerate(own) for x, c in enumerate(r) if c in self._bow[model]}
        gold = {(x, y) for y, r in enumerate(own) for x, c in enumerate(r) if c in BOW}
        for comp in comps(gold):
            near = sum((x + a, y + b) in comp for x, y in comp for a in (-1, 0, 1) for b in (-1, 0, 1)) / len(comp) - 1
            if len(comp) >= 5 and len(comp & p.hair) * 3 < len(comp) and near <= 4.5:
                out |= comp
        return out

    def clothe(self, own: Rows, model: int, p, o: Outfit, bow: Set[Cell] = frozenset()) -> Tuple[Rows, Dict[Cell, str]]:
        """The figure's frame in the outfit's clothes (not its cloak), and what each pixel is:
        head, hand, arm, torso, leg, boot, cloak (the woman's own)."""
        rows = [list(r) for r in own]
        what: Dict[Cell, str] = {}
        if not (p.head and p.shoulders and p.waist is not None):
            return rows, what
        sy, waist, bottom = p.shoulders[0], p.waist, p.bottom
        keep = sg._keep_out(own, p)
        bands, hair = sp.MODELS[model][1], sp.MODELS[model][2]
        arm = self.arms(own, p, keep, bands)
        reach = max(4, waist - sy)
        boot_h = max(2, int(round(0.2 * (bottom - waist))))
        for y, r in enumerate(own):
            for x, c in enumerate(r):
                if c is None:
                    continue
                q = (x, y)
                if model == sg.CLOAK_MODEL and c in WOMAN_CLOAK:
                    rows[y][x] = tone(c, o.cloak or o.torso, cloth=True)
                    what[q] = "cloak"
                    continue
                if q in bow:
                    what[q] = "head"
                    continue
                if q in keep:
                    what[q] = "head"
                    if hair and y >= sy - 1 and c not in SKINC and c not in hair and c != 254 and q not in p.hair:
                        rows[y][x] = tone(c, o.torso)  # (a collar)
                    continue
                if c in bands and c in BANDS:
                    rows[y][x] = BANDS[c]
                    what[q] = "hand"
                    continue
                skin = c in SKINC
                if skin and q in arm:
                    if arm[q] <= 2:
                        what[q] = "hand"
                    elif not o.sleeves or arm[q] < o.sleeve_from * reach:
                        what[q] = "forearm"
                    else:
                        what[q] = "arm"
                        rows[y][x] = tone(c, o.sleeves)
                    continue
                low = y > bottom - boot_h
                if low or (not skin and y > waist + 0.45 * (bottom - waist)):
                    what[q] = "boot"
                    if o.boots and c != 254 and (not skin or o.cover):
                        rows[y][x] = tone(c, o.boots)
                elif y <= waist:
                    what[q] = "torso"
                    if c != 254 and (not skin or o.cover):
                        rows[y][x] = tone(c, o.torso)
                else:
                    what[q] = "leg"
                    if o.legs and c != 254 and (not skin or o.cover):
                        rows[y][x] = tone(c, o.legs)
        if p.facing != sp.SIDE:
            # (skin taken for the chest or a leg, but apart from them: an arm the hand wasn't found on)
            cx, core = (p.head.left + p.head.right) / 2, 0.3 * (p.shoulders[2] - p.shoulders[1])
            for part in ("torso", "leg"):
                cells = {q for q, k in what.items() if k == part and own[q[1]][q[0]] != 254}
                pieces = comps4(cells)
                most = max((len(c) for c in pieces), default=0)
                for comp in pieces:
                    if len(comp) < most and not any(abs(x - cx) <= core + 1 for x, _ in comp) and \
                            sum(own[y][x] in SKINC for x, y in comp) * 2 > len(comp):
                        for x, y in comp:
                            what[(x, y)] = "forearm"
                            rows[y][x] = own[y][x]
        return rows, what

    def hood(self, out: Rows, own: Rows, p, o: Outfit) -> None:
        """A hood worn up: the figure's hair and crown in the cloak's shades (lit from the left),
        a pixel fuller round the head, the face left."""
        ramp = o.cloak
        h, neck = p.head, p.shoulders[0]
        mid = (h.left + h.right) / 2
        cells = set()
        for y, r in enumerate(own):
            for x, c in enumerate(r):
                if c is None:
                    continue
                box = y < neck and h.left - 1 <= x <= h.right + 1
                if (x, y) in p.hair:
                    cells.add((x, y))
                elif box and (p.facing == sp.BACK or y <= h.brow or (p.facing == sp.SIDE and x <= mid)
                              or (c not in SKINC and y <= h.brow + 1)):
                    cells.add((x, y))
        rim = set()
        for x, y in cells:
            if y < neck:
                for a, b in ((-1, 0), (1, 0), (0, -1)):
                    n = (x + a, y + b)
                    if not (0 <= n[1] < len(own) and 0 <= n[0] < len(own[0])) or own[n[1]][n[0]] is None:
                        rim.add(n)
        width = max(1, h.right - h.left + 2)
        height = max(1, neck - h.top + 1)
        for x, y in cells | rim:
            t = 0.8 - 0.55 * (x - h.left + 1) / width - 0.15 * (y - h.top + 1) / height
            if (x, y) in rim:
                t -= 0.15
            c = own[y][x] if 0 <= y < len(own) and 0 <= x < len(own[0]) else None
            if c == 254 and (x, y) not in rim:
                continue
            if 0 <= y + PAD < len(out) and 0 <= x + PAD < len(out[0]):
                out[y + PAD][x + PAD] = ramp[max(0, min(len(ramp) - 1, int(t * (len(ramp) - 1) + 0.5)))]

    def dress(self, model: int, o: Outfit, cb: int, f: int) -> Tuple[Rows, int, int]:
        """MODEL's frame in the outfit, and where its first pixel is in MODEL's own frame."""
        own = self.fr(model + cb, f)
        p = parts(own, model, f, bool(cb))
        rows, what = self.clothe(own, model, p, o, self.bow(model, own, p) if cb and f in sp.BOW_FRAMES else frozenset())
        h, w = len(rows), len(rows[0])
        out: Rows = [[None] * (w + 2 * PAD) for _ in range(PAD)] + \
            [[None] * PAD + r + [None] * PAD for r in rows] + [[None] * (w + 2 * PAD) for _ in range(PAD)]
        mt = marks(own, model, f, bool(cb))
        hit = bool(cb) and f == 12  # (the game's people have no hit frame: the human woman's cloak, as she reels)
        src = sg.CLOAK_MODEL if hit else MAN
        ms = marks(self.fr(src + cb, f), src, f, bool(cb))
        if o.cloak and mt and ms and (model != sg.CLOAK_MODEL or o.closed):
            neck = mt["neck"]
            sa, sb = p.shoulders[1], p.shoulders[2]
            layer = self.her_cloak(cb, f) if hit else self.cloak_layer(o, cb, f)
            placed = self.warp(layer, o.cloak, ms, mt, self.scale(model) / self.scale(src), w, h)
            for (x, y), c in placed.items():
                if y < neck - (0 if o.hood or p.facing == sp.FRONT else 2):
                    continue  # (a hood worn down lies at the nape)
                inside = 0 <= y < h and 0 <= x < w
                if inside and rows[y][x] is not None:
                    part = what.get((x, y))
                    if part in ("head", "hand", "boot", "cloak"):
                        continue
                    if p.facing == sp.BACK:
                        over = y >= neck - 1
                    elif p.facing == sp.FRONT:  # (a robe closes; a cloak lies on the shoulders and arms)
                        over = y >= neck and part != "forearm" and (
                            o.closed or (part != "leg" and abs(x - mt["cx"]) > 0.24 * (sb - sa)))
                    else:
                        over = y >= neck and (o.closed or (x <= (sa + sb) / 2 + 1 and part != "leg"))
                    if not over:
                        continue
                out[y + PAD][x + PAD] = c
        if o.cloak and o.hood and p.head and p.shoulders:
            self.hood(out, own, p, o)
        return tidy(out, 4), -PAD, -PAD

    def size(self, model: int) -> Tuple[int, int]:
        """The figure's height and width standing in front view (without the woman's cloak)."""
        rows = [[None if p in WOMAN_CLOAK and model == sg.CLOAK_MODEL else p for p in r] for r in self.fr(model, 0)]
        cells = sil(rows)
        xs, ys = [x for x, _ in cells], [y for _, y in cells]
        return max(ys) - min(ys) + 1, max(xs) - min(xs) + 1

    def scale(self, model: int) -> float:
        """How much smaller the man is than MODEL, sideways: the mean of the height and width ratios."""
        (hm, wm), (ht, wt) = self.size(MAN), self.size(model)
        return (hm / ht + wm / wt) / 2

    def dead(self, model: int, o: Outfit) -> Tuple[Rows, int, int]:
        """MODEL's dead frame (lying feet up the picture, head down it) in the outfit's colours:
        its own clothes in the tunic's; the raised legs in the leggings' and boots'; where the
        clothes cover the skin, the chest too, and for sleeves the arms as far as the wristbands;
        the face, hands and hair kept. A cloak lies spread under the body from the legs down,
        lit from the left, its folds running down it, a dark edge to the right and below."""
        h = self.fr(model + 1, 13)
        bands, hair = sp.MODELS[model][1], sp.MODELS[model][2]
        cells = sil(h)
        ys = sorted(y for _, y in cells)
        top, bottom = ys[0], ys[-1]
        cut = ys[len(ys) // 3]  # (the raised legs above it)
        head = bottom - sp.HEAD_ROWS[model][0]  # (the head below it)
        xs = [x for x, y in cells if cut <= y <= head]
        mid, half = (min(xs) + max(xs)) / 2, (max(xs) - min(xs)) / 2
        wrists = {(x, y) for x, y in cells if h[y][x] in bands}
        out = [list(r) for r in h]
        for y, r in enumerate(h):
            for x, c in enumerate(r):
                if c is None or c == 254 or (c in hair and y >= cut):
                    continue
                skin = c in SKINC
                if model == sg.CLOAK_MODEL and c in WOMAN_CLOAK:
                    out[y][x] = tone(c, o.cloak or o.torso, cloth=True)
                elif c in BANDS:
                    out[y][x] = BANDS[c]
                elif c in bands:
                    continue
                elif y < cut:
                    ramp = o.boots if y <= top + 2 else o.legs
                    if ramp and (not skin or (o.cover and y > top + 2)):
                        out[y][x] = tone(c, ramp)
                elif not skin:
                    out[y][x] = tone(c, o.torso)
                elif o.cover and y <= head and not any(abs(x - a) <= 3 and abs(y - b) <= 3 for a, b in wrists):
                    if abs(x - mid) <= 0.45 * half:
                        out[y][x] = tone(c, o.torso)
                    elif o.sleeves and not o.sleeve_from:
                        out[y][x] = tone(c, o.sleeves)
        P = PAD
        w = len(h[0])
        big: Rows = [[None] * (w + 2 * P) for _ in range(P)] + \
            [[None] * P + r + [None] * P for r in out] + [[None] * (w + 2 * P) for _ in range(P)]
        if not o.cloak or model == sg.CLOAK_MODEL:
            return big, -P, -P
        ramp, n = o.cloak, len(o.cloak)
        span = {}
        for y in range(cut + 1, bottom + 1):
            row = [x for x, yy in cells if yy == y]
            if row:
                span[y] = (min(row), max(row))
        cloth = set()
        length = max(1, bottom - cut)
        for y, (l, r) in span.items():
            e = 2 + min(2, int(3 * (y - cut) / length))
            cloth |= {(x, y) for x in range(l - e, r + e + 1)}
        l, r = span[bottom]
        for k in (1, 2):  # (rounded off below the head)
            cloth |= {(x, bottom + k) for x in range(l - 3 + 2 * k, r + 4 - 2 * k)}
        cloth -= cells
        for x, y in cloth:
            t = n // 2 + (1 if x < mid - half * 0.4 else -1 if x > mid + half * 0.4 else 0)
            if (x + (y - cut) // 3) % 4 == 0:
                t -= 1  # (a fold)
            if (x + 1, y) not in cloth | cells or (x, y + 1) not in cloth | cells:
                t = 0
            elif (x - 1, y) not in cloth | cells or (x, y - 1) not in cloth | cells:
                t = min(t, 1)
            big[y + P][x + P] = ramp[max(0, min(n - 1, t))]
        return big, -P, -P

    def full(self, model: int, npc: int) -> Tuple[List, List]:
        """Every picture of MODEL in NPC's outfit, each (rows, x, y, the frame it stands in):
        15 walking; 14 fighting (13 dead)."""
        o = OUTFITS[npc]
        walk = [(*self.dress(model, o, 0, f), (model, f)) for f in range(15)]
        fight = [(*self.dress(model, o, 1, f), (model + 1, f)) for f in range(13)]
        fight.append((*self.dead(model, o), (model + 1, 13)))
        return walk, fight


def sil(rows: Rows) -> Set[Tuple[int, int]]:
    return {(x, y) for y, r in enumerate(rows) for x, p in enumerate(r) if p is not None}


def comps(cells) -> List[Set]:
    cells, out = set(cells), []
    while cells:
        stack = [cells.pop()]
        comp = set(stack)
        while stack:
            x, y = stack.pop()
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    q = (x + a, y + b)
                    if q in cells:
                        cells.remove(q)
                        comp.add(q)
                        stack.append(q)
        out.append(comp)
    return out


def comps4(cells) -> List[Set]:
    """The pieces of CELLS joined edge to edge."""
    cells, out = set(cells), []
    while cells:
        stack = [cells.pop()]
        comp = set(stack)
        while stack:
            x, y = stack.pop()
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in cells:
                    cells.remove(q)
                    comp.add(q)
                    stack.append(q)
        out.append(comp)
    return out


def tidy(rows: Rows, most: int) -> Rows:
    """Bits of MOST pixels or fewer floating free of the figure: gone."""
    parts = comps(sil(rows))
    if parts:
        main = max(parts, key=len)
        for comp in parts:
            if comp is not main and len(comp) <= most:
                for x, y in comp:
                    rows[y][x] = None
    return rows


def fill_holes(rows: Rows) -> None:
    """Empty pixels with three or four filled neighbours (where a cloak came off): their
    commonest neighbour."""
    for _ in range(2):
        add = []
        for y in range(1, len(rows) - 1):
            for x in range(1, len(rows[0]) - 1):
                if rows[y][x] is None:
                    near = [rows[y + b][x + a] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if rows[y + b][x + a] is not None]
                    if len(near) >= 3:
                        add.append((x, y, collections.Counter(near).most_common(1)[0][0]))
        for x, y, c in add:
            rows[y][x] = c


def light(p: int) -> float:
    return sg._LIGHT.get(p, 0.5)


def edge(rows: Rows, x: int, y: int) -> bool:
    return rows[y][x] == 254 and any(
        not (0 <= y + b < len(rows) and 0 <= x + a < len(rows[0])) or rows[y + b][x + a] is None
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def parts(rows: Rows, model: int, f: int, combat: bool):
    """spriteparts' parts, the shoulders where it finds none (the half-giants shooting, from
    behind) put at the foot of the head, as wide as the picture's row there."""
    p = sp.parts(rows, model, f, combat)
    if p.head and not p.shoulders and p.facing:
        y = min(len(rows) - 1, p.head.top + sp.HEAD_ROWS[model][(sp.FRONT, sp.BACK, sp.SIDE).index(p.facing)])
        xs = [x for x, c in enumerate(rows[y]) if c is not None]
        if xs:
            p = p._replace(shoulders=(y, min(xs), max(xs)))
    return p


def marks(rows: Rows, model: int, f: int, combat: bool) -> Optional[dict]:
    p = parts(rows, model, f, combat)
    if not (p.head and p.shoulders and p.waist is not None):
        return None
    sy, sa, sb = p.shoulders
    cx = (p.head.left + p.head.right) / 2 if p.facing != sp.SIDE else (sa + sb) / 2
    return dict(top=p.head.top, neck=sy, waist=p.waist, bottom=p.bottom, cx=cx,
                headw=max(1, p.head.right - p.head.left), shw=max(1, sb - sa))


def _pw(y: float, src: dict, dst: dict) -> float:
    """Row Y of DST's figure, as the row of SRC's at the same place between their landmarks."""
    pts = [(dst[k], src[k]) for k in ("top", "neck", "waist", "bottom")]
    a, b = (pts[0], pts[1]) if y <= pts[0][0] else (pts[-2], pts[-1])
    for i in range(3):
        if pts[i][0] <= y <= pts[i + 1][0]:
            a, b = pts[i], pts[i + 1]
            break
    if b[0] == a[0]:
        return a[1]
    return a[1] + (y - a[0]) * (b[1] - a[1]) / (b[0] - a[0])


def tone(c: int, ramp: Tuple[int, ...], cloth: bool = False) -> int:
    """C's shade in RAMP: skin's range of tones, or cloth's, spread over it; black stays black."""
    if c == 254:
        return 254
    t = light(c) * 1.6 if cloth or c not in SKINC else (light(c) - 0.14) / 0.5
    return ramp[max(0, min(len(ramp) - 1, int(t * (len(ramp) - 1) + 0.5)))]


FIGURES = [(2095, "human man"), (2099, "human woman"), (2061, "elf man"), (2059, "elf woman"),
           (2055, "dwarf man"), (2053, "dwarf woman"), (2072, "half-giant man"), (2074, "half-giant woman"),
           (2093, "mul"), (2068, "halfling man"), (2070, "halfling woman")]
COLUMNS = [("front", 0, 0), ("back", 0, 1), ("side", 0, 2), ("walk", 0, 3), ("walk", 0, 7), ("walk", 0, 11),
           ("attack", 1, 0), ("attack", 1, 3), ("attack", 1, 6), ("bow", 1, 9), ("hit", 1, 12), ("dead", 1, 13)]


def sheet(game: Game, npc: int, path: str) -> None:
    """One outfit on each figure, each picture where the game draws it: its frame's anchor (the
    bottom middle of the figure's own picture) on the cell's baseline."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    CW, CH, BASE, Z, LW, TOP = 52, 60, 54, 3, 170, 52
    ink, ground = (40, 24, 12), (196, 150, 104)
    img = Image.new("RGB", (LW + len(COLUMNS) * CW * Z, TOP + len(FIGURES) * CH * Z), ground)
    d = ImageDraw.Draw(img)
    o = OUTFITS[npc]
    d.text((8, 6), f"{o.name}: the clothes of the game's own {o.name.lower()} ({npc}) on each party figure", fill=ink, font=font)
    for ci, (name, _, _) in enumerate(COLUMNS):
        d.text((LW + ci * CW * Z + CW * Z // 2 - 20, 30), name, fill=ink, font=font)
    for mi, (model, label) in enumerate(FIGURES):
        walk, fight = game.full(model, npc)
        tile = Image.new("RGB", (len(COLUMNS) * CW, CH), ground)
        for ci, (_, cb, f) in enumerate(COLUMNS):
            rows, ox, oy, (pic, base_f) = (walk, fight)[cb][f]
            own = game.fr(pic, base_f)
            bx, by = ci * CW + CW // 2 - len(own[0]) // 2, BASE - len(own)
            for y, r in enumerate(rows):
                for x, p in enumerate(r):
                    X, Y = bx + ox + x, by + oy + y
                    if p is not None and 0 <= X < tile.width and 0 <= Y < CH:
                        tile.putpixel((X, Y), game.palette[p])
        img.paste(tile.resize((tile.width * Z, CH * Z), Image.NEAREST), (LW, TOP + mi * CH * Z))
        d.text((8, TOP + mi * CH * Z + CH * Z // 2 - 8), label, fill=ink, font=font)
    img.save(path, optimize=True)


def main(argv: List[str]) -> None:
    if len(argv) < 2:
        raise SystemExit(__doc__)
    game = Game(argv[0])
    os.makedirs(argv[1], exist_ok=True)
    for npc in [int(a) for a in argv[2:]] or list(OUTFITS):
        path = os.path.join(argv[1], f"outfit_{npc}.png")
        sheet(game, npc, path)
        print(path)


if __name__ == "__main__":
    main(sys.argv[1:])
