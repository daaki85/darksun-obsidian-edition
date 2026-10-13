"""Prototype, not part of the Ledger: class outfits for the party's figures from the game's own
people.

Many of the game's people (SEGOBJEX's 15-frame figures) are the party's human man (picture 2095)
redrawn in other clothes, frame for frame: robes, hooded cloaks, leather. This takes one of them
and makes a full set of party pictures (15 walking, 14 fighting) for any of the party's figures:

  * the weapon it carries erased (blade greys, or the colours given, outside the man's outline;
    the blade followed where it crosses the body; the body under it filled from its neighbours);
  * the hit frame (12), which the game's people don't have: their front standing frame;
  * the dead frame (13): the figure's own corpse repainted in the outfit's colours, its cloak or
    robe spread on the ground round it;
  * another figure (woman, elf, dwarf, half-giant, mul, halfling): the clothes alone (what differs
    from the man) stretched frame by frame from the man's landmarks to the figure's (head, neck,
    waist and feet, spriteparts.py), over the figure's own picture; in the head and just below the
    neck only the outfit's cloth (a hood), so each keeps their own face, hair and beard.

Nothing of the game's is in the repository: the pictures are read from the player's install.

    python3 prototypes/outfits.py GAME_DIR OUT_DIR [NPC ...]

writes OUT_DIR/outfit_<npc>.png for each (default: 1252 warrior, 630 thief, 1563 priest, 724
mage) on seven figures, each frame drawn where the game would put it (its picture's anchor, the
bottom middle of the figure's own picture).
"""

import collections
import os
import struct
import sys
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion import art, gff, spritegear as sg, spriteparts as sp  # noqa: E402

Rows = List[List[Optional[int]]]
MAN = 2095
BLADE = {214, 46, 212, 78}
STAFF = set(range(128, 142)) | {181, 182, 212, 213, 214}  # (724's staff: wood browns, bone greys)
EXTRA = {724: STAFF}
HAIRC = {23, 29, 48, 50, 69, 70, 194, 210, 212, 213}
SKINC = set(range(128, 154))
WOMAN_CLOAK = {53, 54, 55, 56, 188, 189, 190, 191, 42}
BANDS = {249: 214, 250: 212}  # (the green wristbands steel, on every class)
LEATHER = (204, 207, 205, 194, 206)
# Outfits restyled: the colours of the figure's own clothes under it, and (the warrior's) its
# leather, which the artist drew in skin-like browns, in leather's
STYLE = {1252: {"tunic": (208, 209, 210, 211), "leather": LEATHER}}


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
        self._cloth: Dict[int, Set[int]] = {}
        self._base: Dict[int, Optional[int]] = {}  # (the outfit's commonest cloth colour)
        self._ramps: Dict[int, dict] = {}

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

    def outfit(self, npc: int, cb: int, f: int) -> Dict[Tuple[int, int], int]:
        """The clothes alone, in the man's frame's place: what differs from him."""
        human = self.fr(MAN + cb, f)
        b, _ = self.erased(npc, cb, f)
        dx, dy = self.align(MAN + cb, npc + cb, f)
        lay = {}
        for Y, r in enumerate(b):
            for X, q in enumerate(r):
                if q is None:
                    continue
                x, y = X + dx, Y + dy
                p = human[y][x] if 0 <= y < len(human) and 0 <= x < len(human[0]) else None
                if p != q:
                    lay[(x, y)] = q
        return lay

    def cloth(self, npc: int) -> Set[int]:
        """The outfit's cloth colours: what it puts over the man's torso and past his outline."""
        if npc not in self._cloth:
            cnt = collections.Counter()
            for f in range(15):
                lay = self.outfit(npc, 0, f)
                m = marks(self.fr(MAN, f), MAN, f, False)
                if not m:
                    continue
                A = sil(self.fr(MAN, f))
                for (x, y), q in lay.items():
                    if q not in SKINC and ((x, y) not in A or m["neck"] <= y <= m["waist"]):
                        cnt[q] += 1
            tot = sum(cnt.values())
            self._cloth[npc] = {q for q, n in cnt.items() if n >= 0.02 * tot}
            self._base[npc] = next((q for q, _ in cnt.most_common() if q != 254), None)
        return self._cloth[npc]

    def ramps(self, npc: int) -> dict:
        """The person's colours over each part of the man, dark to light, and whether a cloak
        or robe hangs past his outline."""
        if npc in self._ramps:
            return self._ramps[npc]
        got = {k: collections.Counter() for k in ("head", "torso", "arms", "legs", "feet", "outside")}
        for f in range(15):
            h = self.fr(MAN, f)
            b, _ = self.erased(npc, 0, f)
            dx, dy = self.align(MAN, npc, f)
            p = sp.parts(h, MAN, f, False)
            if not (p.head and p.shoulders and p.waist):
                continue
            sy, sa, sb = p.shoulders
            mid = (p.head.left + p.head.right) / 2 if p.facing != sp.SIDE else (sa + sb) / 2
            A = sil(h)
            for y, r in enumerate(h):
                run = sg._torso_run(h, y, mid, sa, sb) if sy <= y <= p.waist else None
                for x, c in enumerate(r):
                    if c is None:
                        continue
                    X, Y = x - dx, y - dy
                    q = b[Y][X] if 0 <= Y < len(b) and 0 <= X < len(b[0]) else None
                    if q is None or q == 254:
                        continue
                    part = ("head" if y < sy else "torso" if run and run[0] <= x <= run[1] else
                            "arms" if y <= p.waist else "feet" if y >= p.bottom - 2 else "legs")
                    got[part][q] += 1
            for y, r in enumerate(b):
                for x, q in enumerate(r):
                    if q is not None and q != 254 and (x + dx, y + dy) not in A:
                        got["outside"][q] += 1
        out = {k: (sorted((q for q, _ in cnt.most_common(6)), key=light) or None) for k, cnt in got.items()}
        for k in ("legs", "feet"):  # (cloth only; bare where skin is most of it)
            cloth = collections.Counter({q: n for q, n in got[k].items() if q not in SKINC})
            out[k + " bare"] = sum(cloth.values()) * 2 < sum(got[k].values())
            out[k] = sorted((q for q, _ in cloth.most_common(5)), key=light) or None
        out["cloak"] = sum(got["outside"].values()) > 300
        self._ramps[npc] = out
        return out

    # a figure in the outfit ----------------------------------------------------------------------

    def dress(self, model: int, npc: int, cb: int, f: int) -> Tuple[Rows, int, int]:
        """MODEL's frame in NPC's clothes, and where its first pixel is in MODEL's own frame."""
        style = STYLE.get(npc, {})
        if model == MAN:
            dx, dy = self.align(MAN + cb, npc + cb, f)
            rows = [list(r) for r in self.erased(npc, cb, f)[0]]
            lay = self.outfit(npc, cb, f)
            for Y, r in enumerate(rows):
                for X, p in enumerate(r):
                    if (X + dx, Y + dy) in lay:
                        r[X] = restyle(p, style)
                    if p in BANDS:
                        r[X] = BANDS[p]
            return rows, dx, dy
        R = self.ramps(npc)
        tgt = self.own_clothes(model, cb, f, R, style)
        man = self.fr(MAN + cb, f)
        lay = self.outfit(npc, cb, f)
        ms, mt = marks(man, MAN, f, bool(cb)), marks(self.fr(model + cb, f), model, f, bool(cb))
        P = 6
        W, H = len(tgt[0]) + 2 * P, len(tgt) + 2 * P
        out: Rows = [[None] * W for _ in range(H)]
        for y, r in enumerate(tgt):
            for x, p in enumerate(r):
                out[y + P][x + P] = p
        if ms and mt:
            cl = self.cloth(npc)
            k = self.scale(model)
            shift = self.shifts(man, tgt, ms, mt, k)
            for Y in range(H):
                y = Y - P
                rs = int(round(_pw(y, ms, mt)))
                head = y < mt["neck"]
                t = shift(y)
                last = None
                for X in range(W):
                    x = X - P
                    sx = int(round(ms["cx"] + (x - mt["cx"]) * k + t))
                    q = lay.get((sx, rs))
                    again, last = sx == last, sx
                    if q is None:
                        continue
                    if again and q in cl and q != 254 and self._base.get(npc) is not None:
                        q = self._base[npc]  # (a column drawn twice: the cloth's base, folds stay thin)
                    if (head or y <= mt["neck"] + 4) and q not in cl and q != 254:
                        continue  # (their own face, hair and beard)
                    if head and q == 254 and 0 <= y < len(tgt) and 0 <= x < len(tgt[0]) and tgt[y][x] is not None:
                        continue
                    out[Y][X] = restyle(q, style)
        fill_holes(out)
        for r in out:
            for x, p in enumerate(r):
                if p in BANDS:
                    r[x] = BANDS[p]
        return tidy(out, 6), -P, -P

    def bow_colours(self, model: int) -> Set[int]:
        """The bow's colours in MODEL's bow frames: those its walking frames don't have."""
        walking = {p for f in range(15) for r in self.fr(model, f) for p in r if p is not None}
        return {p for f in sp.BOW_FRAMES for r in self.fr(model + 1, f) for p in r if p is not None} - walking

    def own_clothes(self, model: int, cb: int, f: int, R: dict, style: dict) -> Rows:
        """MODEL's frame with its own clothes in the outfit's: below the neck, what is not skin,
        nor a colour of the head (hair, beard), nor the outline, in the outfit's torso colours (the
        warrior's dark tunic), the feet in its boots'; the woman's cloak off under the outfit's
        own, else a mantle in its tunic's colours."""
        rows = [list(r) for r in self.fr(model + cb, f)]
        tunic = style.get("tunic") or [q for q in (R["torso"] or []) if q not in SKINC] or None
        if model == sg.CLOAK_MODEL:  # (her cloak off under the outfit's; else a mantle in its tunic)
            for r in rows:
                for x, p in enumerate(r):
                    if p in WOMAN_CLOAK:
                        r[x] = None if R["cloak"] or not tunic else by_light(p, tunic)
            fill_holes(rows)
        m = marks(self.fr(model + cb, f), model, f, bool(cb))
        if not m:
            return rows
        head = {p for r in rows[:max(1, m["neck"] - 2)] for p in r if p is not None}  # (not the collar)
        if cb and f in sp.BOW_FRAMES:
            head |= self.bow_colours(model)
        feet = None if R["feet bare"] else R["feet"]
        for y in range(m["neck"], len(rows)):
            for x, p in enumerate(rows[y]):
                if p is None or p in SKINC or p in head or p in BANDS or edge(rows, x, y):
                    continue
                ramp = feet if y >= m["bottom"] - 2 and feet else tunic
                if ramp:
                    rows[y][x] = by_light(p, ramp)
        return rows

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

    @staticmethod
    def shifts(man: Rows, tgt: Rows, ms: dict, mt: dict, k: float):
        """Where the man's outline lies best on the figure's, above the waist and below it: a
        sideways shift for each row (the two blended over the waist's rows)."""
        A = sil(man)
        T = sil(tgt)

        def best(rows):
            cells = [(x, y) for x, y in T if y in rows]
            if not cells:
                return 0
            def score(t):
                hit = 0
                for x, y in cells:
                    if (int(round(ms["cx"] + (x - mt["cx"]) * k + t)), int(round(_pw(y, ms, mt)))) in A:
                        hit += 1
                return hit
            return max(range(-6, 7), key=lambda t: (score(t), -abs(t)))
        w = mt["waist"]
        up, down = best(range(mt["top"], w + 1)), best(range(w + 1, mt["bottom"] + 1))

        def shift(y):
            if y <= w - 1:
                return up
            if y >= w + 2:
                return down
            return up + (down - up) * (y - w + 1) / 3
        return shift

    def dead(self, model: int, npc: int) -> Tuple[Rows, int, int]:
        """MODEL's dead frame in the outfit's colours: its own skin and hair kept; its clothes in
        the torso's; the raised legs in the leggings' and boots'; the man by his parts as he lies
        (boots up top, legs, torso, the head at the bottom). A cloak or robe spread a little round
        the body, edged in its darkest tone."""
        R = self.ramps(npc)
        h = self.fr(model + 1, 13)
        H = len(h)
        hair = sp.MODELS.get(model, ("", frozenset(), frozenset()))[2]
        cells = sil(h)
        ys = sorted(y for _, y in cells)
        top = ys[0]
        cut = 7 if model == MAN else ys[len(ys) // 3]  # (the raised legs above it)
        bare = R["legs bare"] or not R["legs"]
        out = [list(r) for r in h]
        for y, r in enumerate(h):
            for x, c in enumerate(r):
                if c is None or edge(h, x, y):
                    continue
                if model == MAN:
                    part = ("feet" if y <= 2 else "head" if y >= H - 6 and c in HAIRC else
                            ("legs" if y < 9 else None) if c in SKINC else "torso")
                elif c in hair and y >= cut:
                    part = None  # (their own hair)
                elif y < cut:
                    part = ("feet" if y <= top + 1 else "legs") if c in SKINC else None
                else:
                    part = None if c in SKINC else "torso"
                if part in ("legs", "feet") and bare:
                    continue
                if part and R[part]:
                    out[y][x] = by_light(c, R[part])
        if not (R["cloak"] and R["outside"]):
            return out, 0, 0
        P = 2
        big: Rows = [[None] * (len(h[0]) + 2 * P) for _ in range(P)] + \
            [[None] * P + r + [None] * P for r in out] + [[None] * (len(h[0]) + 2 * P) for _ in range(P)]
        body = {(x + P, y + P) for x, y in cells}
        ramp = R["outside"]
        add = {}
        for x, y in body:
            if y < cut + P:
                continue
            for a, b in ((-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 2)):  # (a little, and more below)
                q = (x + a, y + b)
                if q not in body and 0 <= q[1] < len(big) and 0 <= q[0] < len(big[0]):
                    add[q] = ramp[min(len(ramp) - 1, 1 + (q[0] + q[1]) % 2)]
        for (x, y), c in add.items():
            big[y][x] = c
        for x, y in list(add):  # (the cloth's edge, in its darkest tone)
            if any((x + a, y + b) not in add and (x + a, y + b) not in body for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                big[y][x] = ramp[0]
        return big, -P, -P

    def full(self, model: int, npc: int) -> Tuple[List, List]:
        """Every picture of MODEL in NPC's clothes, each (rows, x, y, the frame it stands in):
        15 walking; 14 fighting (12 hit: the standing front frame; 13 dead)."""
        walk = [(*self.dress(model, npc, 0, f), (model, f)) for f in range(15)]
        n = self.count(npc + 1)
        fight = [(*self.dress(model, npc, 1, f), (model + 1, f)) for f in range(min(n, 12))]
        fight.append(walk[0])
        fight.append((*self.dead(model, npc), (model + 1, 13)))
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


def extents(rows: Rows) -> Dict[int, Tuple[int, int]]:
    """Each row's leftmost and rightmost pixel, smoothed (the median of five rows)."""
    raw = {}
    for y, r in enumerate(rows):
        xs = [x for x, p in enumerate(r) if p is not None]
        if xs:
            raw[y] = (min(xs), max(xs))
    out = {}
    for y in raw:
        near = [raw[k] for k in range(y - 2, y + 3) if k in raw]
        out[y] = (sorted(a for a, _ in near)[len(near) // 2], sorted(b for _, b in near)[len(near) // 2])
    return out


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


def restyle(p: Optional[int], style: dict) -> Optional[int]:
    """An outfit's colour as its STYLE has it: skin-like browns in leather's."""
    if p is not None and style.get("leather") and p in SKINC:
        return by_light(p, style["leather"])
    return p


def light(p: int) -> float:
    return sg._LIGHT.get(p, 0.5)


def by_light(p: int, ramp: List[int]) -> int:
    if p == 254:
        return ramp[0]
    t = min(1.0, light(p) * 1.6)
    return ramp[max(0, min(len(ramp) - 1, int(t * (len(ramp) - 1) + 0.5)))]


def edge(rows: Rows, x: int, y: int) -> bool:
    return rows[y][x] == 254 and any(
        not (0 <= y + b < len(rows) and 0 <= x + a < len(rows[0])) or rows[y + b][x + a] is None
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def marks(rows: Rows, model: int, f: int, combat: bool) -> Optional[dict]:
    p = sp.parts(rows, model, f, combat)
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


OUTFITS = {1252: "Warrior (1252)", 630: "Thief (630)", 1563: "Priest (1563)", 724: "Mage (724)"}
FIGURES = [(2095, "human man"), (2099, "human woman"), (2061, "elf man"), (2055, "dwarf man"),
           (2072, "half-giant man"), (2093, "mul"), (2068, "halfling man")]
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
    CW, CH, BASE, Z, LW, TOP = 52, 64, 54, 3, 150, 52
    ink, ground = (40, 24, 12), (196, 150, 104)
    img = Image.new("RGB", (LW + len(COLUMNS) * CW * Z, TOP + len(FIGURES) * CH * Z), ground)
    d = ImageDraw.Draw(img)
    d.text((8, 6), OUTFITS.get(npc, str(npc)) + ": the game's own art, weapon erased, fitted to each party figure",
           fill=ink, font=font)
    for ci, (name, _, _) in enumerate(COLUMNS):
        d.text((LW + ci * CW * Z + CW * Z // 2 - 20, 30), name, fill=ink, font=font)
    for mi, (model, label) in enumerate(FIGURES):
        walk, fight = game.full(model, npc)
        tile = Image.new("RGB", (len(COLUMNS) * CW, CH), ground)
        for ci, (_, cb, f) in enumerate(COLUMNS):
            if f >= len((walk, fight)[cb]):
                continue
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
