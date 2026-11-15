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
  * the hit frame (12), which the game's people don't have, is the figure's own, with the human
    woman's cloak as she reels; the dead frame (13) is the figure's own corpse in the outfit's
    colours, a cloak spread on the ground under it;
  * the half-elves' figures are the Loader's own (figures.py makes them from the elf man's and
    the human woman's pictures): they are made here the same way and dressed like the rest, and
    the elves keep the pointed ears the Loader draws.

The pictures are judged and finished with three tools beside this one: outfitfixes.py (corrections
by hand to single frames, kept as text and laid on each time the pictures are made), outfitcheck.py (every frame checked by rule, the worst listed and drawn large) and outfitreview.py (a page where they move as in the
game, to mark the frames that look wrong).

Nothing of the game's is in the repository: the pictures are read from the player's install.

    python3 prototypes/outfits.py GAME_DIR OUT_DIR [NPC ...]

writes OUT_DIR/outfit_<npc>.png for each (default: 1252 warrior, 630 thief, 1563 priest, 724
mage) on the thirteen figures (the half-elves' the Loader's own: figures.py), each frame drawn where the game would put it (its picture's anchor,
the bottom middle of the figure's own picture).
"""

import collections
import math
import os
import struct
import sys
from typing import Dict, FrozenSet, List, NamedTuple, Optional, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "obsidian-edition"))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import art, figures, gff, halfelf, spritegear as sg, spriteparts as sp  # noqa: E402
import outfitfixes  # noqa: E402

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
HALF_ELF_MAN, HALF_ELF_WOMAN = "half-elf man", "half-elf woman"  # (figures of the Loader's own: figures.py)


class Figure:
    """One of the party's figures: one of the game's models, or a half-elf's, which the Loader
    makes from the elf man's or the human woman's pictures (figures.py)."""

    def __init__(self, game: "Game", key):
        self.game, self.key = game, key
        self.maker = None
        if key in (HALF_ELF_MAN, HALF_ELF_WOMAN):
            self.model = figures.ELF_MAN if key == HALF_ELF_MAN else figures.HUMAN_WOMAN
            made = figures.HalfElfMan if key == HALF_ELF_MAN else figures.HalfElfWoman
            self.maker = made([game.fr(self.model, f) for f in range(15)], [game.fr(self.model + 1, f) for f in range(14)])
            self.hair = figures.GOLDEN_HAIR
            self.cloak = frozenset(getattr(self.maker, "cloak", ()))  # (her own cloak's colours)
            self.sure_bands = True
        else:
            self.model = key
            self.hair = sp.MODELS[key][2]
            self.cloak = frozenset(WOMAN_CLOAK) if key == sg.CLOAK_MODEL else frozenset()
            self.sure_bands = sp.MODELS[key][1] <= frozenset(BANDS) | {43}  # (not the half-giants' greys, their clothes' too)
        self._rows: Dict[Tuple[int, int], Rows] = {}
        self._parts: Dict[Tuple[int, int], object] = {}
        shades = sorted(self.cloak, key=light)  # (its own cloak's shades, dark to light: 0 to 1)
        self.cloak_shade = {c: i / max(1, len(shades) - 1) for i, c in enumerate(shades)}

    def rows(self, cb: int, f: int) -> Rows:
        if (cb, f) not in self._rows:
            self._rows[(cb, f)] = self.maker.frame(f, bool(cb)) if self.maker else self.game.fr(self.model + cb, f)
        return self._rows[(cb, f)]

    def parts(self, cb: int, f: int):
        if (cb, f) not in self._parts:
            rows = self.rows(cb, f)
            p = figures.own(self.maker, f, bool(cb), rows, self.model).parts if self.maker else sp.parts(rows, self.model, f, bool(cb))
            p = shouldered(p, rows, self.model)
            if cb and f == 11:
                p = self.turned(p, rows)
            self._parts[(cb, f)] = p
        return self._parts[(cb, f)]

    def turned(self, p, rows: Rows):
        """The parts of fighting frame 11 (the bow drawn "from the side": the figure is turned to
        the viewer, and spriteparts takes the bow's tip for the head). The head is the top of the
        picture without the bow's colours, as wide as the figure's head standing; the shoulders the row at
        its foot; the waist as spriteparts puts it; seen from the front."""
        body = [[None if c in BOW else c for c in r] for r in rows]  # (without the bow's golden browns)
        ys = [y for y, r in enumerate(body) if sum(c is not None for c in r) >= 2]
        stand = self.parts(0, 0)
        if not ys or not stand.head:
            return p
        top = ys[0]
        xs = [x for y in range(top, min(top + 3, len(body))) for x, c in enumerate(body[y]) if c is not None]
        mid = sorted(xs)[len(xs) // 2]
        half = (stand.head.right - stand.head.left) / 2
        left, right = int(round(mid - half)), int(round(mid + half))
        neck = min(len(body) - 1, top + sp.HEAD_ROWS[self.model][0])
        row = [x for x, c in enumerate(body[neck]) if c is not None] or [left, right]
        hair = {(x, y) for y in range(top, neck) for x in range(max(0, left - 1), min(len(body[0]), right + 2))
                if rows[y][x] in self.hair and rows[y][x] not in SKINC and abs(x - mid) <= half + 1}
        return p._replace(facing=sp.FRONT, head=sp.Head(top, left, right, top + stand.head.brow - stand.head.top),
                          hair=hair, shoulders=(neck, min(row), max(row)),
                          waist=neck + round((p.bottom - neck) * 0.42))

    def bands(self, cb: int, f: int) -> Set[Cell]:
        """The wristbands' pixels."""
        rows = self.rows(cb, f)
        if not self.maker:
            colours = sp.MODELS[self.model][1]
            return {(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c in colours}
        if hasattr(self.maker, "bands"):
            return set(self.maker.bands.get((bool(cb), f), ()))
        at = figures.mover(self.maker.cuts.get((bool(cb), f)))
        colours = sp.MODELS[self.model][1]
        return {(at(x, y), y) for y, r in enumerate(self.game.fr(self.model + cb, f)) for x, c in enumerate(r) if c in colours}



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
    kilt: float = 0  # the leggings stop this far from the waist to the feet (0: they go all the way)
    harness: bool = False  # black inside the clothes stays black (straps), and boots a figure has stay as they are


OUTFITS: Dict[int, Outfit] = {o.npc: o for o in (
    Outfit("Warrior", 1252, None, frozenset(), False, False,  # (a leather jerkin and kilt, bare arms and shins)
           (204, 129, 128, 205, 180), None, 0, (204, 129, 128, 205, 180), (204, 129, 128, 205), True, 0.45, True),
    Outfit("Thief", 630, (69, 188, 53, 189, 54, 190, 55), frozenset((53, 54, 55, 56, 188, 189, 190, 191)), True, False,
           (69, 210, 49, 24, 50), None, 0, (69, 210, 70, 194, 50), (69, 48, 210, 49), True),
    Outfit("Priest", 1563, (129, 202, 195, 163, 76, 32, 77),
           frozenset((202, 163, 32, 77, 164, 195, 76, 137, 136, 44)), False, True,
           (129, 202, 195, 163, 32, 77), (129, 202, 195, 163, 32, 77), 0, (129, 202, 195, 163), (69, 210, 194, 213), True),
    Outfit("Mage", 724, (158, 159, 38, 160, 71, 161), frozenset((158, 159, 38, 39, 160, 161, 71, 40, 70)), False, False,
           (129, 128, 205, 180, 201), (158, 159, 38, 160, 71, 161), 0, (188, 53, 189, 54, 55, 56),
           (204, 129, 134, 136, 138), True),
)}


class Game:
    def __init__(self, game_dir: str, fixes: Optional[dict] = None):
        self.fixes = outfitfixes.read() if fixes is None else fixes  # (corrections by hand)
        self.stale: Dict[tuple, list] = {}  # (those left off: the rules changed under them)
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
        self._bow: Dict[object, Set[int]] = {}
        self._figs: Dict[object, Figure] = {}

    def fig(self, key) -> Figure:
        if key not in self._figs:
            self._figs[key] = Figure(self, key)
        return self._figs[key]

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
            inner: Set[Cell] = set()
            grow = True
            while grow:  # (its shadowed inside and fold lines: dark, past the man's outline; holes over him)
                grow = False
                for q, c in cols.items():
                    if q in cells or c not in DARK:
                        continue
                    n = sum((q[0] + a, q[1] + b_) in cells for a, b_ in near8)
                    if n >= (1 if man(q) is None else 5):
                        cells.add(q)
                        if man(q) is None:
                            inner.add(q)
                        grow = True
            # (drawn as cloth, not as holes: the shadowed inside in the cloak's second shade, black in its darkest)
            layer = {q: o.cloak[1] if q in inner else o.cloak[0] if cols[q] == 254 else cols[q] for q in cells}
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
            pm = self.fig(MAN).parts(cb, f)
            drop = set()
            if pm.facing in (sp.FRONT, sp.SIDE) and pm.head and pm.shoulders and pm.waist is not None:
                # (a sleeve down the forearm lies where the man's arm is, not the figure's: the
                # figure's own arm takes the sleeve's colours instead)
                far = 0.6 * max(4, pm.waist - pm.shoulders[0])
                drop = {q for q, d in self.arms(human, pm, keep_out(human, pm, self.fig(MAN).hair)).items() if d <= far}
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

    def arms(self, own: Rows, p, keep: Set[Cell], wrists: Set[Cell] = frozenset(), sure: bool = False) -> Dict[Cell, float]:
        """The arms: each pixel of the picture along the line from a hand to its shoulder (within
        two pixels of it, three on a half-giant; not the head, nor the middle of the chest seen
        from the front or behind), and how far up the arm from the hand it is (to 2: the hand).
        A hand is where spriteparts finds one, or just past a wristband it finds none at."""
        sy, sa, sb = p.shoulders
        side = p.facing == sp.SIDE
        cx = (p.head.left + p.head.right) / 2
        core = 0.3 * (sb - sa)
        wide = 2.0 if sb - sa < 22 else 3.0
        band = set(wrists) if sure else {(x, y) for y, r in enumerate(own) for x, c in enumerate(r) if c in BANDS}
        chest = {}  # (each row's run through the body's middle: its middle three fifths are the chest)
        for y in range(sy, p.waist + 1):
            run = sg._torso_run(own, y, cx, sa, sb)
            if run and run[1] - run[0] >= 0.4 * (sb - sa):
                chest[y] = ((run[0] + run[1]) / 2, 0.3 * (run[1] - run[0]))

        def middle(x, y):
            return not side and ((y >= sy and abs(x - cx) <= core) or (y in chest and abs(x - chest[y][0]) <= chest[y][1]))

        def shoulder(x):
            return ((sa + sb) / 2, sy + 1) if side else ((sa + 1) if x < cx else (sb - 1), sy + 1)
        starts = []  # (a hand's pixel, and how far up the arm it already is)
        for hx, hy in p.hands.values():
            near = sorted((abs(a) + abs(b), (hx + a, hy + b)) for a in range(-2, 3) for b in range(-2, 3)
                          if 0 <= hy + b < len(own) and 0 <= hx + a < len(own[0]) and own[hy + b][hx + a] in SKINC
                          and (hx + a, hy + b) not in keep)
            if near:
                starts.append((near[0][1], 0.0))
        for comp in comps(band):  # (a wristband with no hand found by it: the hand is past it from the shoulder)
            bx, by = sorted(comp)[len(comp) // 2]
            if not any(abs(bx - x) <= 4 and abs(by - y) <= 4 for (x, y), _ in starts):
                ax, ay = shoulder(bx)
                d = math.hypot(bx - ax, by - ay) or 1.0
                starts.append(((bx + (bx - ax) * 2 / d, by + (by - ay) * 2 / d), 0.0))
        out: Dict[Cell, float] = {}
        for (hx, hy), d0 in starts:
            ax, ay = shoulder(hx)
            length = math.hypot(ax - hx, ay - hy) or 1.0
            ux, uy = (ax - hx) / length, (ay - hy) / length
            for y, r in enumerate(own):
                for x, c in enumerate(r):
                    if c is None or (x, y) in keep or middle(x, y):
                        continue
                    t = (x - hx) * ux + (y - hy) * uy  # (along the arm, from the hand)
                    off = abs((x - hx) * uy - (y - hy) * ux)
                    if -3 <= t <= length and off <= wide and (t >= 0 or math.hypot(x - hx, y - hy) <= 3):
                        d = d0 + max(0.0, t)
                        if d < out.get((x, y), 99):
                            out[(x, y)] = d
        return out

    def bow(self, fig: Figure, own: Rows, p) -> Set[Cell]:
        """The bow in a bow frame: the colours the figure's walking frames don't have, and its golden
        browns in thin pieces (a line a pixel or two wide), not hair."""
        if fig.key not in self._bow:
            walking = {c for f in range(15) for r in fig.rows(0, f) for c in r if c is not None}
            self._bow[fig.key] = {c for f in sp.BOW_FRAMES for r in fig.rows(1, f) for c in r if c is not None} - walking
        out = {(x, y) for y, r in enumerate(own) for x, c in enumerate(r) if c in self._bow[fig.key]}
        gold = {(x, y) for y, r in enumerate(own) for x, c in enumerate(r) if c in BOW}
        for comp in comps(gold):
            near = sum((x + a, y + b) in comp for x, y in comp for a in (-1, 0, 1) for b in (-1, 0, 1)) / len(comp) - 1
            if len(comp) >= 5 and len(comp & p.hair) * 3 < len(comp) and near <= 4.5:
                out |= comp
        return out

    def clothe(self, own: Rows, fig: Figure, p, o: Outfit, wrists: Set[Cell], bow: Set[Cell] = frozenset()) -> Tuple[Rows, Dict[Cell, str]]:
        """The figure's frame in the outfit's clothes (not its cloak), and what each pixel is:
        head, hand, arm, torso, leg, boot, cloak (the woman's own)."""
        rows = [list(r) for r in own]
        what: Dict[Cell, str] = {}
        if not (p.head and p.shoulders and p.waist is not None):
            return rows, what
        sy, waist, bottom = p.shoulders[0], p.waist, p.bottom
        keep = keep_out(own, p, fig.hair)
        hair = fig.hair
        arm = self.arms(own, p, keep, wrists, fig.sure_bands)
        boot_h = max(2, int(round(0.2 * (bottom - waist))))
        for y, r in enumerate(own):
            for x, c in enumerate(r):
                if c is None:
                    continue
                q = (x, y)
                if c in fig.cloak and not (fig.sure_bands and q in wrists):
                    rows[y][x] = shade(fig.cloak_shade[c], o.cloak or o.torso)
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
                if fig.sure_bands and q in wrists:
                    rows[y][x] = BANDS.get(c, 212)
                    what[q] = "hand"
                    continue
                skin = c in SKINC
                if q in arm and (skin or o.sleeves):
                    if skin and arm[q] <= 2:
                        what[q] = "hand"
                    elif not o.sleeves:
                        what[q] = "forearm"
                    else:  # (a sleeve to the wrist, over the figure's own sleeve too)
                        what[q] = "arm"
                        if c != 254:
                            rows[y][x] = tone(c, o.sleeves)
                        elif not edge(own, x, y):
                            rows[y][x] = o.sleeves[0]
                    continue
                low = y > bottom - boot_h
                if low or (not skin and y > waist + 0.45 * (bottom - waist)):
                    what[q] = "boot"
                    if o.boots and c != 254 and (skin and o.cover if o.harness else not skin or o.cover):
                        rows[y][x] = tone(c, o.boots)
                elif y <= waist:
                    what[q] = "torso"
                    if c == 254:
                        if o.cover and not o.harness and not edge(own, x, y):
                            rows[y][x] = o.torso[0]  # (black inside the garment: its darkest shade)
                    elif not skin or o.cover:
                        rows[y][x] = tone(c, o.torso)
                else:
                    what[q] = "leg"
                    if o.kilt and y > waist + o.kilt * (bottom - waist):
                        pass  # (below the kilt: the figure's own legs)
                    elif c == 254:
                        if o.cover and o.legs and not o.harness and not edge(own, x, y):
                            rows[y][x] = o.legs[0]
                    elif o.legs and (not skin or o.cover):
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

    def hood(self, out: Rows, own: Rows, p, o: Outfit, fig: Figure, bow: Set[Cell]) -> None:
        """A hood worn up: the figure's hair (all of it, wherever it hangs) and crown in the
        cloak's shades (lit from the left), black among them the darkest; a pixel fuller round the
        head; from the front down beside the face to the shoulders, where a yoke joins it to the
        cloak; the face left."""
        ramp = o.cloak
        h, neck = p.head, p.shoulders[0]
        mid = (h.left + h.right) / 2
        brow = max(h.brow, h.top + int(0.35 * (neck - h.top)))  # (a bald head's brow: a third down it)
        hairc = fig.hair - SKINC
        cells = set()
        for y, r in enumerate(own):
            for x, c in enumerate(r):
                if c is None or (x, y) in bow:
                    continue
                box = y < neck and h.left - 1 <= x <= h.right + 1
                if (x, y) in p.hair:
                    cells.add((x, y))
                elif box and (p.facing == sp.BACK or y <= brow or (p.facing == sp.SIDE and x <= mid)
                              or (c not in SKINC and y <= brow + 1)):
                    cells.add((x, y))
        grow = list(cells)  # (the hair spriteparts didn't take for hair: hair-coloured, touching the hood)
        while grow:
            x, y = grow.pop()
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    n = (x + a, y + b)
                    if n not in cells and n not in bow and 0 <= n[1] < len(own) and 0 <= n[0] < len(own[0]) \
                            and own[n[1]][n[0]] in hairc:
                        cells.add(n)
                        grow.append(n)
        rim = set()
        for x, y in cells:
            if y < neck:
                for a, b in ((-1, 0), (1, 0), (0, -1)):
                    n = (x + a, y + b)
                    if not (0 <= n[1] < len(own) and 0 <= n[0] < len(own[0])) or own[n[1]][n[0]] is None:
                        rim.add(n)
        if p.facing == sp.FRONT:
            rim |= {(x, y) for y in range(brow, neck) for x in (h.left - 1, h.right + 1)}  # (beside the face)
            sa, sb = p.shoulders[1], p.shoulders[2]
            cells |= {(x, y) for y in (neck, neck + 1) for x in range(sa + 1, sb) if abs(x - mid) >= 2
                      and 0 <= y < len(own) and 0 <= x < len(own[0]) and own[y][x] is not None
                      and own[y][x] not in SKINC}  # (the yoke, on the clothes at the shoulders)
        width = max(1, h.right - h.left + 2)
        height = max(1, neck - h.top + 1)
        for x, y in cells | rim:
            t = 0.8 - 0.55 * (x - h.left + 1) / width - 0.15 * (y - h.top + 1) / height
            if (x, y) in rim:
                t -= 0.15
            c = own[y][x] if 0 <= y < len(own) and 0 <= x < len(own[0]) else None
            if c == 254 and (x, y) not in rim:
                t = 0
            if 0 <= y + PAD < len(out) and 0 <= x + PAD < len(out[0]):
                out[y + PAD][x + PAD] = ramp[max(0, min(len(ramp) - 1, int(t * (len(ramp) - 1) + 0.5)))]

    def front_cloak(self, out: Rows, p, o: Outfit, laid: Set[Cell]) -> None:
        """An open cloak seen from the front, drawn on the figure itself so that it is the same
        from frame to frame: it hangs behind the body from the shoulders to three fifths of the
        way from the waist to the feet, inside the shoulders at the top and two pixels past them at
        the scalloped hem; wherever the picture is empty within it is cloak: its left edge lit, its right
        edge mid, its inside the cloak's second shade with a fold every fourth pixel, its hem the darkest."""
        ramp, n = o.cloak, len(o.cloak)
        sy, sa, sb = p.shoulders
        hem = p.waist + int(round(0.6 * (p.bottom - p.waist)))
        for y in range(sy + 1, hem + 1):
            flare = (3 * (y - sy)) // max(1, hem - sy) - 1  # (inside the shoulders at the top, two past them at the hem)
            left, right = sa - flare, sb + flare
            Y = y + PAD
            for x in range(left, right + 1):
                X = x + PAD
                if y == hem and (x - left) % 4 == 2:
                    continue  # (the hem scalloped)
                if 0 <= Y < len(out) and 0 <= X < len(out[0]) and out[Y][X] is None:
                    if x == left:
                        c = ramp[n - 2]
                    elif x == left + 1:
                        c = ramp[max(1, n - 3)]
                    elif x == right:
                        c = ramp[2]
                    elif y >= hem - 1:
                        c = ramp[0]
                    else:
                        c = ramp[2] if (x - left) % 4 == 3 else ramp[1]  # (a fold every fourth pixel)
                    out[Y][X] = c
                    laid.add((X, Y))

    def dress(self, key, o: Outfit, cb: int, f: int) -> Tuple[Rows, int, int]:
        """A figure's frame in the outfit, and where its first pixel is in the figure's own frame."""
        fig = self.fig(key)
        own, p = fig.rows(cb, f), fig.parts(cb, f)
        bow = self.bow(fig, own, p) if cb and f in sp.BOW_FRAMES else frozenset()
        rows, what = self.clothe(own, fig, p, o, fig.bands(cb, f), bow)
        h, w = len(rows), len(rows[0])
        out: Rows = [[None] * (w + 2 * PAD) for _ in range(PAD)] + \
            [[None] * PAD + r + [None] * PAD for r in rows] + [[None] * (w + 2 * PAD) for _ in range(PAD)]
        laid: Set[Cell] = set()
        mt = marks(p, own, fig.cloak)
        hit = bool(cb) and f == 12  # (the game's people have no hit frame: the human woman's cloak, as she reels)
        src = sg.CLOAK_MODEL if hit else MAN
        ms = marks(self.fig(src).parts(cb, f), self.fig(src).rows(cb, f), self.fig(src).cloak)
        if o.cloak and not o.closed and not fig.cloak and p.facing == sp.FRONT and p.shoulders and p.waist is not None:
            self.front_cloak(out, p, o, laid)
        elif o.cloak and mt and ms and (not fig.cloak or o.closed):
            neck = mt["neck"]
            sa, sb = p.shoulders[1], p.shoulders[2]
            layer = self.her_cloak(cb, f) if hit else self.cloak_layer(o, cb, f)
            placed = self.warp(layer, o.cloak, ms, mt, self.scale(key) / self.scale(src), w, h)
            for q, c in list(placed.items()):  # (a shade alone among others, left by the resampling: its neighbours')
                near = [placed[n] for n in ((q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)) if n in placed]
                if len(near) >= 3 and c not in near:
                    placed[q] = collections.Counter(near).most_common(1)[0][0]
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
                laid.add((x + PAD, y + PAD))
        if p.facing == sp.SIDE:  # (sand between the cloak and the back, up to four pixels: cloak)
            for Y, r in enumerate(out):
                for X in range(len(r) - 2):
                    if (X, Y) in laid and r[X + 1] is None:
                        n = 1
                        while X + n + 1 < len(r) and r[X + n + 1] is None and n < 5:
                            n += 1
                        if n <= 4 and X + n + 1 < len(r) and r[X + n + 1] is not None:
                            for k in range(1, n + 1):
                                r[X + k] = r[X]
                                laid.add((X + k, Y))
        for _ in range(2):  # (a line of the cloak with nothing above or below it: its lit edge left over)
            for X, Y in list(laid):
                if not any(out[Y + b][X + a] is not None for b in (-1, 1) for a in (-1, 0, 1)
                           if 0 <= Y + b < len(out) and 0 <= X + a < len(out[0])):
                    out[Y][X] = None
                    laid.discard((X, Y))
        if o.closed and p.facing == sp.FRONT and p.waist is not None:
            self.skirt(out, what, p, o)
        pieces = comps(sil(out))  # (a piece of the cloak apart from the figure: gone)
        for comp in pieces:
            if comp is not max(pieces, key=len) and comp <= laid:
                for x, y in comp:
                    out[y][x] = None
        if o.cloak and o.hood and p.head and p.shoulders:
            self.hood(out, own, p, o, fig, bow)
        return (tidy(out, 4) if o.hood else self.ears(tidy(out, 4), fig, cb, f)), -PAD, -PAD

    @staticmethod
    def skirt(out: Rows, what: Dict[Cell, str], p, o: Outfit) -> None:
        """A robe closed over the legs, seen from the front: from the waist three fifths of the
        way to the feet, the gap between the legs and a pixel each side of them in the robe's
        middle shades, a fold every third pixel, lighter to the left, a dark hem."""
        ramp, n = o.cloak, len(o.cloak)
        foot = p.waist + int(round(0.6 * (p.bottom - p.waist)))
        cx = (p.head.left + p.head.right) / 2
        for y in range(p.waist + 1, foot + 1):
            xs = [x for (x, yy), k in what.items() if yy == y and k in ("leg", "torso")]
            if not xs:
                continue
            for x in range(min(xs) - 1, max(xs) + 2):
                X, Y = x + PAD, y + PAD
                if 0 <= X < len(out[0]) and out[Y][X] is None:
                    t = n // 2 + (1 if x < cx - 2 else 0) - (1 if (x - int(cx)) % 3 == 0 else 0)
                    out[Y][X] = ramp[1] if y == foot else ramp[max(1, min(n - 1, t))]

    @staticmethod
    def ears(out: Rows, fig: Figure, cb: int, f: int) -> Rows:
        """The elves' pointed ears, as the Loader draws them over what an elf wears (figures.py)."""
        if fig.key in figures.ELVES:
            return figures.ears_over(out, fig.rows(cb, f), fig.key, f, bool(cb), PAD)
        return out

    def size(self, key) -> Tuple[int, int]:
        """The figure's height and width standing in front view (without a cloak of its own)."""
        fig = self.fig(key)
        rows = [[None if p in fig.cloak else p for p in r] for r in fig.rows(0, 0)]
        cells = sil(rows)
        xs, ys = [x for x, _ in cells], [y for _, y in cells]
        return max(ys) - min(ys) + 1, max(xs) - min(xs) + 1

    def scale(self, key) -> float:
        """How much smaller the man is than the figure, sideways: the mean of the height and width ratios."""
        (hm, wm), (ht, wt) = self.size(MAN), self.size(key)
        return (hm / ht + wm / wt) / 2

    def dead(self, key, o: Outfit) -> Tuple[Rows, int, int]:
        """MODEL's dead frame (lying feet up the picture, head down it) in the outfit's colours:
        its own clothes in the tunic's; the raised legs in the leggings' and boots'; where the
        clothes cover the skin, the chest too, and for sleeves the arms as far as the wristbands;
        the face, hands and hair kept. A cloak lies spread under the body from the legs down,
        lit from the left, its folds running down it, a dark edge to the right and below."""
        fig = self.fig(key)
        h, hair, model = fig.rows(1, 13), fig.hair, fig.model
        cells = sil(h)
        ys = sorted(y for _, y in cells)
        top, bottom = ys[0], ys[-1]
        cut = ys[len(ys) // 3]  # (the raised legs above it)
        feet = top + max(2, int(round(0.1 * (bottom - top))))
        head = bottom - sp.HEAD_ROWS[model][0]  # (the head below it)
        xs = [x for x, y in cells if cut <= y <= head]
        mid, half = (min(xs) + max(xs)) / 2, (max(xs) - min(xs)) / 2
        wrists = fig.bands(1, 13)
        out = [list(r) for r in h]
        for y, r in enumerate(h):
            for x, c in enumerate(r):
                if c is None or c == 254:
                    continue
                if c in hair and y >= cut:
                    if o.hood and o.cloak and c not in SKINC:
                        out[y][x] = shade(min(1.0, light(c) * 1.4), o.cloak)  # (the hood, fallen with them)
                    continue
                skin = c in SKINC
                if (x, y) in wrists:
                    if fig.sure_bands:
                        out[y][x] = BANDS.get(c, 212)
                elif c in fig.cloak:
                    out[y][x] = shade(fig.cloak_shade[c], o.cloak or o.torso)
                elif y < cut:
                    ramp = o.boots if y <= feet else o.legs
                    if ramp and (not skin or (o.cover and y > feet)):
                        out[y][x] = tone(c, ramp)
                elif not skin:
                    out[y][x] = tone(c, o.torso)
                elif o.cover and y <= head and not any(abs(x - a) <= 1 and abs(y - b) <= 1 for a, b in wrists):
                    if abs(x - mid) <= 0.45 * half:
                        out[y][x] = tone(c, o.torso)
                    elif o.sleeves and not o.sleeve_from:
                        out[y][x] = tone(c, o.sleeves)
        P = PAD
        w = len(h[0])
        big: Rows = [[None] * (w + 2 * P) for _ in range(P)] + \
            [[None] * P + r + [None] * P for r in out] + [[None] * (w + 2 * P) for _ in range(P)]
        if not o.cloak or fig.cloak:
            return self.ears(big, fig, 1, 13), -P, -P
        # The cloak, tied at the neck, lies under the body fanned out toward the feet (up the picture):
        # no wider than the shoulders at the neck, five or six pixels past the body each side at the
        # hips and a little beyond, shifted a little to the left; lighter to the left, its folds
        # running from the neck, a shadow where the body lies on it, its right edge dark.
        ramp, n = o.cloak, len(o.cloak)
        big_one = (bottom - top) / 24.0
        stand = fig.parts(0, 0)
        neck_half = ((stand.head.right - stand.head.left) / 2 + 2) if stand.head else 5
        hip_half = neck_half + 5 * max(0.8, big_one)
        first = max(top, cut - 2)
        cloth = {}
        for y in range(first, head + 1):
            k = (head - y) / max(1, head - first)  # (0 at the neck, 1 at the hem)
            hw = neck_half + (hip_half - neck_half) * min(1.0, k * 1.3)
            cx = mid - 1.5 * k
            for x in range(int(round(cx - hw)), int(round(cx + hw)) + 1):
                if y == first and (x - int(cx)) % 4 == 0:
                    continue  # (the hem uneven)
                if (x, y) not in cells:
                    cloth[(x, y)] = (cx, hw)
        for (x, y), (cx, hw) in cloth.items():
            u = (x - cx) / max(1.0, hw)
            t = n // 2 + (1 if u < -0.33 else -1 if u > 0.33 else 0)
            if any(abs(x - (cx + j * hw / 3)) < 0.5 for j in (-2, -1, 1, 2)):
                t = 1  # (a fold, from the neck)
            if (x - 1, y) in cells or (x, y - 1) in cells:
                t = 0  # (the body's shadow on it)
            elif (x + 1, y) not in cloth and (x + 1, y) not in cells:
                t = 1
            elif (x - 1, y) not in cloth and (x - 1, y) not in cells:
                t = min(n - 2, t + 1)
            big[y + P][x + P] = ramp[max(0, min(n - 1, t))]
        return self.ears(big, fig, 1, 13), -P, -P

    def full(self, key, npc: int, fixed: bool = True) -> Tuple[List, List]:
        """Every picture of a figure in NPC's outfit, each (rows, x, y, the figure's own frame it
        stands in): 15 walking; 14 fighting (13 dead). FIXED: with the corrections made by hand
        (outfitfixes.py) laid on."""
        o, fig = OUTFITS[npc], self.fig(key)
        walk = [(*self.dress(key, o, 0, f), fig.rows(0, f)) for f in range(15)]
        fight = [(*self.dress(key, o, 1, f), fig.rows(1, f)) for f in range(13)]
        fight.append((*self.dead(key, o), fig.rows(1, 13)))
        name = dict(FIGURES).get(key, str(key))
        for cb, frames in ((0, walk), (1, fight)):
            for f, (rows, ox, _, _) in enumerate(frames):
                fix = self.fixes.get((o.name, name, cb, f))
                if fix and fixed:
                    stale = outfitfixes.apply(rows, -ox, fix, self.palette)
                    if stale:
                        self.stale[(o.name, name, cb, f)] = stale
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


def keep_out(own: Rows, p, hair: FrozenSet[int]) -> Set[Cell]:
    """What clothes never recolour: the head (its box down to the shoulders), the hair, and the
    dark strands among the hair (black, or one of the hair's own colours, with two hair pixels
    by it): not the body under long hair."""
    out = set(p.hair)
    if p.head and p.shoulders:
        h, neck = p.head, p.shoulders[0]
        out |= {(x, y) for y in range(h.top, neck) for x in range(h.left, h.right + 1)}
    for _ in range(2):
        among = set()
        for y, row in enumerate(own):
            for x, c in enumerate(row):
                if c is not None and (x, y) not in out and (c == 254 or (c in hair and c not in SKINC)) and \
                        sum((x + a, y + b) in p.hair for a in (-1, 0, 1) for b in (-1, 0, 1)) >= 2:
                    among.add((x, y))
        out |= among
    return out


def shouldered(p, rows: Rows, model: int):
    """Parts with the shoulders, where spriteparts finds none (the half-giants shooting, from
    behind), put at the foot of the head, as wide as the picture's row there."""
    if p.head and not p.shoulders and p.facing:
        y = min(len(rows) - 1, p.head.top + sp.HEAD_ROWS[model][(sp.FRONT, sp.BACK, sp.SIDE).index(p.facing)])
        xs = [x for x, c in enumerate(rows[y]) if c is not None]
        if xs:
            p = p._replace(shoulders=(y, min(xs), max(xs)))
    return p


def marks(p, rows: Rows, cloak: FrozenSet[int] = frozenset()) -> Optional[dict]:
    """A figure's landmarks from its parts: the crown, neck, waist and feet, and where a cloak
    hangs from across it: its middle, or from the side (facing right) its back, the picture's
    left edge between the shoulders and the waist (a cloak of its own, CLOAK's colours, aside)."""
    if not (p.head and p.shoulders and p.waist is not None):
        return None
    sy, sa, sb = p.shoulders
    cx = (p.head.left + p.head.right) / 2
    if p.facing == sp.SIDE:
        lefts = []
        for y in range(sy + 1, p.waist + 1):
            xs = [x for x, c in enumerate(rows[y]) if c is not None and c not in cloak and (x, y) not in p.hair] if y < len(rows) else []
            if xs:
                lefts.append(min(xs))
        cx = sorted(lefts)[len(lefts) // 2] if lefts else (sa + sb) / 2
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


def shade(t: float, ramp: Tuple[int, ...]) -> int:
    """A cloak's shade T (0 its darkest, 1 its lightest) in RAMP: never RAMP's darkest, its fold lines'."""
    return ramp[max(1, min(len(ramp) - 1, int(t * (len(ramp) - 1) + 0.5)))]


def tone(c: int, ramp: Tuple[int, ...], cloth: bool = False) -> int:
    """C's shade in RAMP: skin's range of tones, or cloth's, spread over it; black stays black."""
    if c == 254:
        return 254
    t = light(c) * 1.6 if cloth or c not in SKINC else (light(c) - 0.14) / 0.5
    return ramp[max(0, min(len(ramp) - 1, int(t * (len(ramp) - 1) + 0.5)))]


FIGURES = [(2095, "human man"), (2099, "human woman"), (HALF_ELF_MAN, HALF_ELF_MAN), (HALF_ELF_WOMAN, HALF_ELF_WOMAN),
           (2061, "elf man"), (2059, "elf woman"),
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
            rows, ox, oy, own = (walk, fight)[cb][f]
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
