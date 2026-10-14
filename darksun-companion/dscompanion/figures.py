"""The elves' ears and the half-elves' own figures, on the party's map pictures (sprites.py), made
from the game's own pictures each time the Loader writes its copy of SEGOBJEX (nothing of the
game's is kept here: only how to change its pictures).

Elves: pointed ears, 2 pixels wide and 3 rows tall, salmon inside (LIT) with a rose rim and a rose
tip leaning a pixel out (RIM). From the front they stand two rows above the eyes, beside the head;
from behind, at the eyes; from the side, the near ear on the hair behind the face. They are drawn
over what the figure wears only where it left the picture as it was (a shield or a raised weapon
hides them). Poses the
body can't be read from (lunges, the bow, hit, dead) have them set by hand (EAR_PLAN).

The half-elf man: the elf man's figure, a column wider below the neck (between the elf's build
and the human's), in his own colours (golden hair, a linen shirt, a leather jerkin, green trousers,
brown boots: each part's colours the elf's shading in ramps of the party's palette, dark to light),
dark eyes, a linen V at the neck, a belt with a buckle, his hair short at the nape, small ears.

The half-elf woman: the human woman's figure in her half-elf colours (halfelf.recolour: golden
hair, a purple cloak, red boots), a column slimmer below the neck, her long hair put up in a bun on
her crown (the hair beside her face and down her back taken away, and what was under it drawn:
her neck, her cloak), and the elves' ears beside the top of her head. Her fights' poses by hand
(WOMAN_FIGHTS)."""

import collections
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

from . import halfelf, spritegear as sg, spriteparts as sp

Rows = sg.Rows
ELF_MAN, ELF_WOMAN, HUMAN_WOMAN = 2061, 2059, 2099  # (models: their walking pictures)
ELVES = (ELF_MAN, ELF_WOMAN)
LIT, RIM = 148, 145
# Every hair colour of the elves' (with the darker browns their hair shares with skin)
HAIRS = frozenset((44, 45, 64, 65, 128, 129, 134, 135, 136, 137, 138, 179, 180, 181, 182, 200, 201))
EYE = 77  # (the side view's eye)

# The elves' ears by hand, for the poses that need it: (model, combat, frame) -> each ear's inner
# base pixel (in the frame's own coordinates), the way it points (-1 left, 1 right) and, lying
# head down, 1 (it points down)
EAR_PLAN: Dict[Tuple[int, bool, int], List[Tuple[int, ...]]] = {
    (ELF_MAN, True, 0): [(5, 11, -1)],  # (lunging: his raised hand over the other ear)
    (ELF_MAN, True, 2): [(10, 4, -1), (18, 4, 1)],  # (his arm over his head)
    (ELF_MAN, True, 4): [(2, 12, -1)],  # (from behind: his raised arm over the other ear)
    (ELF_MAN, True, 6): [(13, 8, -1), (18, 8, 1)],  # (lunging, his face turned to the viewer)
    (ELF_MAN, True, 8): [(10, 4, -1)],  # (from the side, no eye drawn)
    (ELF_MAN, True, 10): [(1, 7, -1), (9, 7, 1)],  # (from behind, drawing the bow)
    (ELF_MAN, True, 11): [(5, 4, -1), (11, 4, 1)],  # (turned to the viewer, the bow drawn)
    (ELF_MAN, True, 12): [(4, 2, -1), (11, 2, 1)],  # (hit)
    (ELF_MAN, True, 13): [(5, 22, -1, 1), (13, 22, 1, 1)],  # (dead, lying head down)
    (ELF_WOMAN, True, 0): [(5, 10, -1)],
    (ELF_WOMAN, True, 1): [(6, 5, -1), (17, 5, 1)],  # (head down, an arm out: above it)
    (ELF_WOMAN, True, 2): [(12, 4, -1), (21, 4, 1)],
    (ELF_WOMAN, True, 4): [(2, 13, -1)],
    (ELF_WOMAN, True, 6): [(9, 9, -1), (14, 9, 1)],
    (ELF_WOMAN, True, 10): [(1, 7, -1), (9, 7, 1)],
    (ELF_WOMAN, True, 11): [(5, 4, -1), (11, 4, 1)],
    (ELF_WOMAN, True, 12): [(0, 5, -1)],  # (hit, her head thrown back: the near side only)
    (ELF_WOMAN, True, 13): [(0, 16, -1, 1), (11, 16, 1, 1)],
}


# How a half-elf's frame differs in shape from the game's it is made from: from row Y down, past
# column X, a column put in (1) or taken out (-1)
Cut = Tuple[int, int, int]
GOLDEN_HAIR = frozenset((179, 180, 181, 182, 200, 65))  # (the half-elves' own)


def mover(cut: Optional[Cut]) -> Callable[[int, int], int]:
    """Where a pixel (x, y) of the game's frame is across the half-elf's made from it with CUT."""
    def at(x: int, y: int) -> int:
        if cut is None or y < cut[0] or x <= cut[1]:
            return x
        return x + cut[2]
    return at


def mover_back(cut: Optional[Cut]) -> Callable[[int, int], int]:
    """Where a pixel (x, y) of the half-elf's made with CUT is across the game's frame."""
    def back(x: int, y: int) -> int:
        if cut is None or y < cut[0]:
            return x
        if cut[2] > 0:
            return x if x <= cut[1] else x - 1  # (the column put in: a copy of the one before)
        return x if x < cut[1] else x + 1
    return back


def moved(parts: sp.Parts, cut: Optional[Cut], rows: Rows) -> sp.Parts:
    """The PARTS of the game's frame a half-elf's ROWS were made from, where they are on ROWS
    (CUT): what the gear is drawn by (spritegear.armed), as ROWS' own can't be read (their hands
    and hair in other colours). Their hair: only what is still there (golden)."""
    at = mover(cut)
    hair = {(at(x, y), y) for x, y in parts.hair}
    hair = {(x, y) for x, y in hair if 0 <= y < len(rows) and 0 <= x < len(rows[y]) and rows[y][x] in GOLDEN_HAIR}
    out = parts._replace(hair=hair, hands={k: (at(x, y), y) for k, (x, y) in parts.hands.items()},
                         feet=[(y, at(a, y), at(b, y)) for y, a, b in parts.feet])
    if parts.shoulders:
        sy, a, b = parts.shoulders
        out = out._replace(shoulders=(sy, at(a, sy), at(b, sy)))
    return out


def own(maker, f: int, combat: bool, rows: Rows, model: int) -> sg.Own:
    """What the gear needs of frame F of a half-elf's (ROWS, made by MAKER from MODEL's): its
    parts, the game's frame, and its clothes and cloak (HalfElfMan.clothes, HalfElfWoman)."""
    src = maker.own[combat][f]
    cut = maker.cuts.get((combat, f))
    src_parts = sp.parts(src, model, f, combat)
    at = mover(cut)
    clothing = set(sg.CLOTHES.get(model, ()))
    dressed = getattr(maker, "worn", {}).get((combat, f))  # (his clothes, by part)
    if dressed is None:  # (where the game's frame has clothing)
        dressed = {(x, y) for y, r in enumerate(src) for x, c in enumerate(r) if c in clothing}
    worn = set()  # (there on the half-elf's: the column put in too)
    for x, y in dressed:
        worn.add((at(x, y), y))
        if cut is not None and cut[2] > 0 and y >= cut[0] and x == cut[1]:
            worn.add((x + 1, y))
    bands = frozenset(maker.bands.get((combat, f), ())) if hasattr(maker, "bands") else frozenset()
    return sg.Own(moved(src_parts, cut, rows), src, src_parts, at, getattr(maker, "clothes", None),
                  getattr(maker, "cloak", frozenset()), bands, frozenset(worn), mover_back(cut))


def put(rows: Rows, x: int, y: int, c: Optional[int]) -> None:
    if 0 <= y < len(rows) and 0 <= x < len(rows[y]):
        rows[y][x] = c


def ear_shape(x: int, y: int, d: int, v: int = -1) -> List[Tuple[int, int, int]]:
    """An ear whose inner base is at (X, Y), pointing D sideways and V up (-1) or down (1): tip first."""
    return [(x + 2 * d, y + 2 * v, RIM), (x, y + v, LIT), (x + d, y + v, RIM), (x, y, LIT), (x + d, y, RIM)]


def _edge(rows: Rows, y: int, d: int) -> Optional[int]:
    xs = [x for x, c in enumerate(rows[y]) if c is not None] if 0 <= y < len(rows) else []
    return (min(xs) if d < 0 else max(xs)) if xs else None


def ear_plan(rows: Rows, model: int, frame: int, combat: bool) -> List[Tuple[int, ...]]:
    """Where an elf's ears go on the game's picture ROWS: by hand (EAR_PLAN), or read from the
    figure's parts; none where they can't be."""
    if (model, combat, frame) in EAR_PLAN:
        return EAR_PLAN[(model, combat, frame)]
    try:
        p = sp.parts(rows, model, frame, combat)
    except (ValueError, IndexError, TypeError, KeyError):
        return []
    if p.facing in (sp.FRONT, sp.BACK) and p.shoulders:
        y = p.shoulders[0] - 3 - (2 if p.facing == sp.FRONT else 0)  # (in front, raised two rows)
        if y - 2 < 0:
            return []
        plan = []
        for d in (-1, 1):
            if model == ELF_WOMAN:  # (her hair: against it on the row above the base)
                e = _edge(rows, y - 1, d)
            else:  # (his head's sides, clear of collar and arms)
                es = [e for e in (_edge(rows, yy, d) for yy in (y - 2, y - 1)) if e is not None]
                e = (min if d < 0 else max)(es) if es else None
            if e is None:
                return []
            plan.append((e + d, y, d))
        return plan
    if p.facing == sp.SIDE and p.head:
        eye = next(((yy, x) for yy in range(len(rows)) for x, c in enumerate(rows[yy]) if c == EYE), None)
        if eye is None or eye[0] < 3:
            return []
        d = -1 if eye[1] > (p.head.left + p.head.right) / 2 else 1  # (the ear behind the face)
        r, fx = rows[eye[0] - 1], eye[1]  # (the face: back from the eye to the hair)
        while 0 <= fx + d < len(r) and r[fx + d] is not None and r[fx + d] not in HAIRS:
            fx += d
        return [(fx + 2 * d, eye[0], d)]
    return []


def ears_over(dressed: Rows, rows: Rows, model: int, frame: int, combat: bool, pad: int) -> Rows:
    """An elf's ears on DRESSED (ROWS, the game's picture, padded by PAD and dressed: spritegear),
    where what is worn left it as it was."""
    for ear in ear_plan(rows, model, frame, combat):
        for a, b, c in ear_shape(ear[0] + pad, ear[1] + pad, *ear[2:]):
            if not (0 <= b < len(dressed) and 0 <= a < len(dressed[b])):
                continue
            y, x = b - pad, a - pad
            own = rows[y][x] if 0 <= y < len(rows) and 0 <= x < len(rows[y]) else None
            if dressed[b][a] is None or dressed[b][a] == own:
                dressed[b][a] = c
    return dressed


# ---------------------------------------------------------------- the half-elf man (on the elf man)

LEATHER = [204, 207, 205, 157, 201, 168]
LINEN = [207, 205, 201, 168, 169, 171]
GREEN = [188, 53, 189, 54, 190, 55]
GOLDEN = [179, 180, 181, 200, 182, 65]
BOOTS = [204, 203, 207, 205, 201]
MAN_RAMPS = {"hair": GOLDEN, "jerkin": LEATHER, "sleeve": LINEN, "legs": GREEN, "boots": BOOTS}
MAN_BANDS = {250: 207, 249: 205}  # (his wristbands leather)
WORN = ("jerkin", "sleeve", "legs", "boots")  # (the parts of him armour is drawn on)
SKIN = frozenset(range(128, 154))
BOW = frozenset((179, 180, 181, 182, 183))  # (kept as it is, below the shoulders in a fight)
BLUE_EYES = frozenset((158, 159, 38, 160, 24, 29))
DARK_EYE = 129
CUT = frozenset((179, 180, 181, 200, 182, 65, 136, 138, 137, 135, 128))  # (his hair, cut at the nape)
NAPE = (129, 146, 148, 146, 129)
COLLAR = (168, 169, 171, 169, 168)
BUCKLE = 167


def _light(c: int) -> float:
    return sg._LIGHT[c]


def _zones(rows: Rows, frame: int, combat: bool) -> Tuple[Dict[Tuple[int, int], str], sp.Parts]:
    """Each pixel of the elf man's picture: the part of him it is."""
    p = sp.parts(rows, ELF_MAN, frame, combat)
    sy, sa, sb = p.shoulders
    mid = (p.head.left + p.head.right) / 2 if p.facing != sp.SIDE else (sa + sb) / 2
    hair = set(sp.MODELS[ELF_MAN][2]) | {179}
    z = {}
    for y, r in enumerate(rows):
        run = sg._torso_run(rows, y, mid, sa, sb) if sy <= y <= p.waist else None
        for x, c in enumerate(r):
            if c is None:
                continue
            if c in MAN_BANDS:
                k = "bracer"
            elif combat and c in BOW and y >= sy:
                k = "bow"
            elif y < sy:
                k = "hair" if c in hair else "skin" if c in SKIN else "O" if c == 254 else \
                    "sleeve" if y >= p.head.brow + 3 else "headother"
            elif c in SKIN:
                k = "skin"
            elif c == 254:
                k = "O"
            elif y >= p.bottom - 5 and y > p.waist + 2:
                k = "boots"
            elif y > p.waist:
                k = "legs"
            elif run and run[0] <= x <= run[1] and y > sy + 1:
                k = "jerkin"
            else:
                k = "sleeve"
            z[(x, y)] = k
    return z, p


class HalfElfMan:
    """The half-elf man's pictures, made from the elf man's (WALK, FIGHT: each a list of frames).
    His colours: each part's colours in the first 7 walking frames, by their brightness, spread
    over its ramp (a colour no first frame has: the nearest in brightness that one has)."""

    def __init__(self, walk: Sequence[Rows], fight: Sequence[Rows]):
        self.own = {False: walk, True: fight}
        self.cuts: Dict[Tuple[bool, int], Optional[Cut]] = {}
        self.worn: Dict[Tuple[bool, int], Set[Tuple[int, int]]] = {}  # (his clothes in each frame: for armour)
        self.colours: Dict[str, Set[int]] = collections.defaultdict(set)
        self.most: collections.Counter = collections.Counter()
        for f in range(min(7, len(walk))):
            for (x, y), k in _zones(walk[f], f, False)[0].items():
                self.colours[k].add(walk[f][y][x])
                self.most[(walk[f][y][x], k)] += 1
        self.map: Dict[str, Dict[int, int]] = {}
        for k, ramp in MAN_RAMPS.items():
            cs = sorted(self.colours[k], key=_light)
            self.map[k] = {c: ramp[min(len(ramp) - 1, int(i * len(ramp) / max(1, len(cs))))] for i, c in enumerate(cs)}
        # His clothes, for armour (spritegear.draw_armour): the ramps of the parts of him the
        # elf's clothes are in, dark to light
        elf = set(sg.CLOTHES.get(ELF_MAN, ()))
        worn = {c for k in WORN if self.colours[k] & elf for c in MAN_RAMPS[k]}
        self.clothes = (254,) + tuple(sorted(worn - {254}, key=_light))

    def _mapped(self, k: str, c: int) -> int:
        if c in self.map[k]:
            return self.map[k][c]
        return self.map[k][min(self.map[k], key=lambda o: abs(_light(o) - _light(c)))]

    def frames(self, combat: bool) -> List[Rows]:
        return [self.frame(f, combat) for f in range(len(self.own[combat]))]

    def frame(self, f: int, combat: bool) -> Rows:
        src = self.own[combat][f]
        try:
            p = sp.parts(src, ELF_MAN, f, combat)
            p.shoulders[0]
        except (ValueError, IndexError, TypeError, KeyError):
            self.cuts[(combat, f)] = None  # (a column more at the right: nothing moves)
            return self._lying(f, combat)
        self.cuts[(combat, f)] = (p.shoulders[0], self._middle(p), 1)
        rows, p = self._recolour(src, f, combat)
        rows = self._widen(rows, p)
        self._polish(rows, p)
        self._haircut(rows, p, f, combat, src)
        return rows

    def _recolour(self, src: Rows, f: int, combat: bool) -> Tuple[Rows, sp.Parts]:
        rows = [list(r) for r in src]
        z, p = _zones(src, f, combat)
        hair = set(sp.MODELS[ELF_MAN][2]) | {179}
        self.worn[(combat, f)] = {xy for xy, k in z.items() if k in WORN and src[xy[1]][xy[0]] not in hair}
        for (x, y), k in z.items():
            c = rows[y][x]
            if k in self.map:
                rows[y][x] = self._mapped(k, c)
            elif k == "bracer":
                rows[y][x] = MAN_BANDS[c]
            elif k == "headother" and c != 254 and c in self.colours["hair"]:
                rows[y][x] = self.map["hair"].get(c, c)
        for k, ramp in MAN_RAMPS.items():  # (the artist's dither kept: neighbours alike in his
            for y in range(len(rows)):  # colours, unlike in the elf's, a tone apart)
                for x in range(1, len(rows[y])):
                    if z.get((x, y)) != k or z.get((x - 1, y)) != k:
                        continue
                    a, b = rows[y][x - 1], rows[y][x]
                    if a == b and src[y][x] != src[y][x - 1] and b in ramp:
                        i = ramp.index(b)
                        j = i + 1 if _light(src[y][x]) > _light(src[y][x - 1]) else i - 1
                        if 0 <= j < len(ramp):
                            rows[y][x] = ramp[j]
        return rows, p

    @staticmethod
    def _middle(p: sp.Parts) -> int:
        return int(round((p.head.left + p.head.right) / 2 if p.facing != sp.SIDE else (p.shoulders[1] + p.shoulders[2]) / 2))

    def _widen(self, rows: Rows, p: sp.Parts) -> Rows:
        """A column more through the body, below the neck, at its middle."""
        sy, cx = p.shoulders[0], self._middle(p)
        return [r[:cx + 1] + [r[cx]] + r[cx + 1:] if y >= sy else r + [None] for y, r in enumerate(rows)]

    def _polish(self, rows: Rows, p: sp.Parts) -> None:
        sy, sa, sb = p.shoulders
        cx = self._middle(p)
        at = lambda x, y: x + (x > cx) if y >= sy else x  # (past the widened column)
        for y in range(max(0, p.head.top), sy):  # (dark eyes)
            for x, c in enumerate(rows[y]):
                if c in BLUE_EYES:
                    rows[y][x] = DARK_EYE
        mid = (p.head.left + p.head.right) / 2 if p.facing != sp.SIDE else None
        if p.facing == sp.FRONT:  # (a linen V at the neck)
            for dy, xs in ((0, (-1, 0, 1)), (1, (0,)), (2, (0,))):
                for dx in xs:
                    y = sy - 1 + dy
                    x = at(int(round(mid)), y) + dx
                    if 0 <= y < len(rows) and 0 <= x < len(rows[y]) and rows[y][x] not in (None, 254) and rows[y][x] not in SKIN:
                        rows[y][x] = (169 if dx <= 0 else 168) if dy == 0 else 171 if dy == 1 else 169
        y = p.waist - 1  # (a belt, its buckle in front)
        run = sg._torso_run(rows, y, at(int(round(mid)) if mid else cx, y), at(sa, y), at(sb, y)) if 0 <= y < len(rows) else None
        if run:
            a, b = run
            for x in range(a, b + 1):
                if rows[y][x] not in SKIN and rows[y][x] is not None:
                    rows[y][x] = (204, 207)[x % 2] if x not in (a, b) else 204
            if p.facing == sp.FRONT:
                rows[y][at(int(round(mid)), y)] = BUCKLE
            elif p.facing == sp.SIDE:
                rows[y][b - 1] = BUCKLE

    def _haircut(self, rows: Rows, p: sp.Parts, f: int, combat: bool, src: Rows) -> None:
        """His hair short at the nape (walking away and to the side), and his small ears where
        the elf's go: a base and a tip a pixel out and up (from behind, a point)."""
        plan = ear_plan(src, ELF_MAN, f, combat)
        top, sy = p.head.top, p.shoulders[0]
        cx = (p.head.left + p.head.right) // 2
        if p.facing == sp.BACK and not combat:
            for y in range(top + 5, sy):
                for x, c in enumerate(rows[y]):
                    if c in CUT:
                        rows[y][x] = (NAPE if y < sy - 1 else COLLAR)[min(4, abs(x - cx))]
        elif p.facing == sp.SIDE and not combat and plan:
            d = plan[0][2]  # (the back of his head that way)
            for y in range(top + 5, sy):
                for x, c in enumerate(rows[y]):
                    if c in CUT and (x <= p.head.left + 3 if d < 0 else x >= p.head.right - 3):
                        rows[y][x] = None
        for ear in plan:
            x, y, d = ear[:3]
            v = ear[3] if len(ear) > 3 else -1
            if p.facing == sp.BACK:
                put(rows, x, y - 1 if v < 0 else y + 1, 145)
            elif p.facing == sp.SIDE and len(plan) == 1:
                put(rows, x, y + v, 146)
                put(rows, x - d, y + 2 * v, 144)
            else:
                put(rows, x, y - v, 146 if d < 0 else 145)
                put(rows, x + d, y, 144)

    def _lying(self, f: int, combat: bool) -> Rows:
        """A pose his parts can't be read from (dead): each colour the part it most often is."""
        rows = [list(r) for r in self.own[combat][f]]
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c is None:
                    continue
                ks = [(n, k) for (cc, k), n in self.most.items() if cc == c]
                k = max(ks)[1] if ks else None
                if k in WORN:
                    self.worn.setdefault((combat, f), set()).add((x, y))
                if k in self.map:
                    rows[y][x] = self.map[k][c]
                elif k == "bracer":
                    rows[y][x] = MAN_BANDS[c]
                elif c in BLUE_EYES and y > len(rows) * 2 // 3:
                    rows[y][x] = DARK_EYE
        for x, y, d, v in (e for e in EAR_PLAN.get((ELF_MAN, combat, f), []) if len(e) == 4):
            put(rows, x, y - v, 146 if d < 0 else 145)
            put(rows, x + d, y, 144)
        return [r + [None] for r in rows]


# --------------------------------------------------------- the half-elf woman (on the human woman)

HAIR = frozenset((179, 180, 181, 182, 200, 65))  # (her golden hair, as halfelf.recolour has it)
BUN = (181, 65, 200)
NECK = (133, 146, 148, 146, 133)
CLOAK = frozenset((174, 175, 176, 177))
DARK_HAIR = frozenset((254, 128, 129))  # (her hair's shadow: black and the human's dark browns)
# Her fights by hand: frame -> (the part of the picture round her head (x0, y0, x1, y1), the hair
# kept there (her skull), the bun's first pixel (a row of three), her ears (x, y, d))
WOMAN_FIGHTS: Dict[int, Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int], Tuple[int, int], List[Tuple[int, int, int]]]] = {
    0: ((0, 8, 14, 17), (7, 8, 13, 13), (10, 8), [(6, 12, -1)]),  # (lunging: her hand over the other ear)
    1: ((0, 0, 19, 8), (8, 4, 14, 8), (10, 3), [(7, 6, -1), (15, 6, 1)]),  # (her hair flung up)
    2: ((8, 1, 22, 9), (11, 2, 18, 9), (14, 1), [(10, 4, -1), (19, 4, 1)]),
    3: ((0, 3, 13, 15), (4, 3, 10, 7), (6, 2), [(3, 6, -1)]),  # (from behind: her hand over the other)
    4: ((0, 8, 9, 21), (3, 9, 9, 14), (5, 8), [(2, 13, -1)]),
    5: ((10, 0, 23, 9), (11, 0, 17, 5), (13, 0), [(10, 4, -1)]),
    6: ((9, 6, 18, 12), (11, 7, 16, 10), (12, 6), [(12, 10, -1)]),  # (from the side: the near ear)
    7: ((6, 0, 20, 9), (12, 1, 19, 7), (12, 0), [(14, 5, -1)]),
    8: ((10, 0, 20, 10), (13, 0, 19, 5), (12, 0), [(15, 4, -1)]),
    9: ((0, 0, 7, 12), (4, 0, 12, 4), (8, 0), [(4, 2, -1), (13, 2, 1)]),
    10: ((0, 3, 10, 13), (3, 3, 9, 7), (4, 2), [(2, 6, -1), (10, 6, 1)]),
    11: ((0, 3, 12, 15), (4, 3, 10, 6), (6, 2), [(3, 5, -1), (11, 5, 1)]),
    12: ((0, 0, 8, 10), (1, 0, 8, 5), (5, 0), [(2, 4, -1)]),  # (hit, her head thrown back)
}
DEAD = 13  # (lying head down: her hair is the human's dark brown here, which recolour misses)
DEAD_HAIR = {129: 180, 128: 181, 134: 181, 136: 182, 138: 65, 179: 200, 180: 182}


def _slim(rows: Rows, sy: int) -> Tuple[Rows, Optional[int]]:
    """A column out below row SY, near the middle: the one whose loss changes the picture least
    (and which it was)."""
    xs = [x for y in range(sy, len(rows)) for x, c in enumerate(rows[y]) if c is not None]
    if not xs:
        return rows, None
    mid = (min(xs) + max(xs)) // 2
    cost = lambda x: sum(rows[y][x] != rows[y][x - 1] for y in range(sy, len(rows)))
    x = min(range(max(1, mid - 3), min(len(rows[0]), mid + 4)), key=lambda x: (cost(x), abs(x - mid)))
    return [r[:x] + r[x + 1:] + [None] if y >= sy else list(r) for y, r in enumerate(rows)], x


def _core(row: List[Optional[int]]) -> Optional[Tuple[int, int]]:
    xs = [x for x, c in enumerate(row) if c is not None and c not in HAIR]
    return (min(xs), max(xs)) if xs else None


def _fill(rows: Rows, x: int, y: int, sy: int, cx: int) -> Optional[int]:
    """What shows where her hair is taken away: nothing past her edge; her neck above the
    shoulders; below them her cloak (its colour from the nearest of it below)."""
    r = rows[y]
    sides = any(c is not None and c not in HAIR for c in r[:x]) and any(c is not None and c not in HAIR for c in r[x + 1:])
    above = y > 0 and rows[y - 1][x] is not None
    below = y + 1 < len(rows) and rows[y + 1][x] is not None and rows[y + 1][x] not in HAIR
    if not sides and not (above and below):
        return None
    if y < sy:
        return NECK[min(4, abs(x - cx))]
    for yy in range(y + 1, len(rows)):
        c = rows[yy][x]
        if c is not None and c not in HAIR:
            return c
    return None


def _cut(rows: Rows, y: int, keep: Callable[[int], bool], sy: int, cx: int) -> None:
    for x, c in enumerate(rows[y]):
        if c in HAIR and not keep(x):
            rows[y][x] = _fill(rows, x, y, sy, cx)


def _plug(rows: Rows, before: Rows) -> None:
    """No holes where hair was taken out of her: a pixel emptied with her figure on both sides of
    it (or three of its four) takes a neighbour's colour, her cloak's or skin's before her hair's."""
    h, w = len(rows), len(rows[0])
    for _ in range(3):
        for y in range(h):
            for x in range(w):
                if rows[y][x] is not None or before[y][x] is None:
                    continue
                n = {k: rows[yy][xx] for k, (xx, yy) in (("l", (x - 1, y)), ("r", (x + 1, y)), ("u", (x, y - 1)), ("d", (x, y + 1)))
                     if 0 <= yy < h and 0 <= xx < w and rows[yy][xx] is not None}
                if ("l" in n and "r" in n) or ("u" in n and "d" in n) or len(n) >= 3:
                    rows[y][x] = next((n[k] for k in "dlru" if k in n and n[k] not in HAIR), next(iter(n.values())))


def _behind(rows: Rows, before: Rows, skull_bottom: int, skull_x: Tuple[int, int]) -> None:
    """Below her head, where her long hair hung over her back, shoulders and chest: what was under
    it, her neck just under her skull, else her cloak or body carried on from below (its folds) or
    from the side."""
    h = len(rows)
    gone = {(x, y) for y in range(h) for x in range(len(rows[y])) if before[y][x] is not None and rows[y][x] is None}
    for y in range(skull_bottom + 1, h):
        for x in range(len(rows[y])):
            if (x, y) not in gone:
                continue
            if y == skull_bottom + 1:
                if skull_x[0] + 1 <= x <= skull_x[1] - 1:
                    rows[y][x] = NECK[min(4, abs(x - (skull_x[0] + skull_x[1]) // 2))]
                continue
            seen = lambda xx, yy: rows[yy][xx] is not None and rows[yy][xx] not in HAIR and (xx, yy) not in gone
            c = next((rows[yy][x] for yy in range(y + 1, min(h, y + 5)) if seen(x, yy)), None)
            if c is None:
                c = next((rows[y][xx] for dx in range(1, len(rows[y])) for xx in (x - dx, x + dx)
                          if 0 <= xx < len(rows[y]) and seen(xx, y)), None)
            rows[y][x] = c


class HalfElfWoman:
    """The half-elf woman's pictures, made from the human woman's (WALK, FIGHT)."""

    def __init__(self, walk: Sequence[Rows], fight: Sequence[Rows]):
        self.own = {False: walk, True: fight}
        self.cuts: Dict[Tuple[bool, int], Optional[Cut]] = {}
        self.cloak = frozenset(halfelf.CLOAK.values())  # (her own, which a worn cloak recolours)
        self.bands: Dict[Tuple[bool, int], Set[Tuple[int, int]]] = {}  # (her wristbands: in its colours, not it)

    def frames(self, combat: bool) -> List[Rows]:
        return [self.frame(f, combat) for f in range(len(self.own[combat]))]

    def frame(self, f: int, combat: bool) -> Rows:
        if combat:
            return self._dead() if f == DEAD else self._fight(f)
        return self._walk(f)

    def _plain(self, f: int, combat: bool) -> Rows:
        """Her figure in her colours, a column slimmer below the neck."""
        src = self.own[combat][f]
        p = sp.parts(src, HUMAN_WOMAN, f, combat)
        rows = [list(r) for r in halfelf.recolour(src, halfelf.WOMAN)]
        sy = p.shoulders[0] if p.shoulders else 0
        rows, x = _slim(rows, sy)
        self.cuts[(combat, f)] = (sy, x, -1) if x is not None else None
        at = mover(self.cuts[(combat, f)])
        self.bands[(combat, f)] = {(at(bx, by), by) for by, r in enumerate(src) for bx, c in enumerate(r)
                                   if c in halfelf.BANDS and not (x is not None and by >= sy and bx == x)}
        return rows

    def _walk(self, f: int) -> Rows:
        src = self.own[False][f]
        p = sp.parts(src, HUMAN_WOMAN, f, False)
        rows = self._plain(f, False)
        top, sy = p.head.top, p.shoulders[0]
        crown = [x for x, c in enumerate(rows[top]) if c is not None]
        cx = (min(crown) + max(crown)) // 2
        if p.facing in (sp.FRONT, sp.BACK):  # (her crown's top row: the bun)
            rows[top] = [None] * len(rows[top])
            for i, c in enumerate(BUN):
                put(rows, cx - 1 + i, top, c)
        if p.facing == sp.FRONT:
            self._front(rows, top, sy, cx)
        elif p.facing == sp.BACK:
            self._back(rows, top, sy)
        elif p.facing == sp.SIDE:
            self._side(rows, top, sy)
        for y in range(top + 1, min(sy + 1, len(rows) - 1)):  # (no notches left in her head)
            for x in range(1, len(rows[y]) - 1):
                if rows[y][x] is None and rows[y - 1][x] is not None and rows[y + 1][x] is not None \
                        and (rows[y][x - 1] is not None or rows[y][x + 1] is not None):
                    rows[y][x] = rows[y + 1][x]
        self._ears(rows, p.facing, top)
        return rows

    @staticmethod
    def _front(rows: Rows, top: int, sy: int, cx: int) -> None:
        """Her hair kept to a pixel or two past her face; the ears beside the top of her head,
        nothing of her cloak under them, her shoulders a row lower beside her neck."""
        for y, (lo, hi) in ((top + 3, (2, 1)), (top + 4, (1, 1))):
            k = _core(rows[y])
            if k:
                _cut(rows, y, lambda x, a=k[0] - lo, b=k[1] + hi: a <= x <= b, sy, cx)
        for y in range(top + 5, sy):
            k = _core(rows[y])
            if k:
                _cut(rows, y, lambda x, k=k: k[0] <= x <= k[1], sy, cx)

    @staticmethod
    def _back(rows: Rows, top: int, sy: int) -> None:
        """Her neck where her hair hung at her nape, her cloak below; the ears beside her head."""
        hx = [x for x, c in enumerate(rows[top + 4]) if c is not None]
        nx = (min(hx) + max(hx)) // 2
        for y in range(top + 5, sy):
            for x, c in enumerate(rows[y]):
                if c in HAIR:
                    rows[y][x] = NECK[min(4, abs(x - nx))]
        for y in range(top + 5, len(rows)):
            _cut(rows, y, lambda x: False, sy, nx)

    @staticmethod
    def _side(rows: Rows, top: int, sy: int) -> None:
        """Facing right: the bun at the back of her crown, her hair cut behind her neck, the near
        ear on the hair behind her face."""
        x0 = min(x for x, c in enumerate(rows[top]) if c is not None)
        for dx, dy, c in ((-3, 0, 181), (-2, 0, 65), (-1, 0, 200), (-3, 1, 180), (-2, 1, 200), (-2, 2, 179)):
            put(rows, x0 + dx, top + dy, c)

        def face(y: int) -> Optional[int]:
            xs = [x for x, c in enumerate(rows[y]) if c is not None and c not in HAIR and c != 254]
            return min(xs) if xs else None
        fx = face(top + 4)
        for y, back in ((top + 3, 4), (top + 4, 4), (top + 5, 3)):
            f_ = face(y) or fx
            _cut(rows, y, lambda x, f_=f_, back=back: x >= f_ - back, sy, f_)
        for y in range(top + 6, len(rows)):
            f_ = face(y) or fx
            _cut(rows, y, lambda x, f_=f_: x >= f_, sy, f_)

    @staticmethod
    def _ears(rows: Rows, facing: int, top: int) -> None:
        """The elves' ears beside the top of her head: from the front two rows down from it, with
        nothing of her cloak under them past her face (her shoulders a row lower beside her neck);
        from behind a row lower; from the side the near ear on the hair behind her face."""
        if facing == sp.FRONT:
            ey = top + 2
            l, r = _edge(rows, ey - 1, -1), _edge(rows, ey - 1, 1)
            face = [x for x, c in enumerate(rows[top + 4]) if c is not None and 128 <= c <= 153]
            if face:
                fl, fr = min(face), max(face)
                for x in range(len(rows[top + 5])):
                    if rows[top + 5][x] is not None and (x < fl - 1 or x > fr + 2):
                        rows[top + 5][x] = None
            face = [x for x, c in enumerate(rows[ey + 1]) if c is not None and 130 <= c <= 153]
            fl, fr = (min(face), max(face)) if face else (l, r)
            for x0, d in ((l - 1, -1), (r + 1, 1)):
                for a, b, c in ear_shape(x0, ey, d):
                    put(rows, a, b, c)
                for a in (x0, x0 + d):
                    if 0 <= a < len(rows[ey + 1]) and rows[ey + 1][a] is not None and not (fl - 1 <= a <= fr + 2) \
                            and rows[ey + 1][a] not in HAIR:
                        rows[ey + 1][a] = None
        elif facing == sp.BACK:
            ey = top + 3
            l, r = _edge(rows, ey - 1, -1), _edge(rows, ey - 1, 1)
            for x0, d in ((l - 1, -1), (r + 1, 1)):
                for a, b, c in ear_shape(x0, ey, d):
                    put(rows, a, b, c)
                for a in (x0, x0 + d):
                    if 0 <= a < len(rows[ey + 1]) and rows[ey + 1][a] in CLOAK:
                        rows[ey + 1][a] = None
        elif facing == sp.SIDE:
            xs = [x for x, c in enumerate(rows[top + 4]) if c is not None and c not in HAIR and c != 254]
            if xs:
                for a, b, c in ear_shape(min(xs) - 2, top + 3, -1):
                    put(rows, a, b, c)

    def _fight(self, f: int) -> Rows:
        rows = self._plain(f, True)
        if f not in WOMAN_FIGHTS:
            return rows
        (zx0, zy0, zx1, zy1), (kx0, ky0, kx1, ky1), (bx, by), ears = WOMAN_FIGHTS[f]
        before = [list(r) for r in rows]

        def in_hair(x: int, y: int) -> bool:  # (black among her hair only: its shadow)
            for xx, yy in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= yy < len(before) and 0 <= xx < len(before[yy]):
                    c = before[yy][xx]
                    if c is not None and c not in HAIR and c not in DARK_HAIR:
                        return False
            return True
        for y in range(zy0, min(zy1 + 1, len(rows))):
            for x in range(zx0, min(zx1 + 1, len(rows[y]))):
                if kx0 <= x <= kx1 and ky0 <= y <= ky1:
                    continue
                if before[y][x] in HAIR or (before[y][x] in DARK_HAIR and in_hair(x, y)):
                    rows[y][x] = None
        for y in range(zy0, min(zy1 + 1, len(rows))):  # (a pixel between two of hers: hers again)
            for x in range(zx0, min(zx1 + 1, len(rows[y]))):
                if rows[y][x] is None and 0 < y < len(rows) - 1 and rows[y - 1][x] is not None and rows[y + 1][x] is not None:
                    rows[y][x] = rows[y + 1][x]
        _behind(rows, before, ky1, (kx0, kx1))
        _plug(rows, before)
        if by == ky0:  # (no room above her: her crown's top row is the bun)
            rows[by] = [None if c in HAIR else c for c in rows[by]]
        for i, c in enumerate(BUN):
            put(rows, bx + i, by, c)
        for x, y, d in ears:
            for a, b, c in ear_shape(x, y, d):
                put(rows, a, b, c)
        return rows

    def _dead(self) -> Rows:
        """Lying head down: her hair golden, kept to her skull, the bun at her crown (below her),
        her ears pointing down."""
        rows = self._plain(DEAD, True)
        before = [list(r) for r in rows]
        for y in range(11, len(rows)):
            for x, c in enumerate(rows[y]):
                if c in DEAD_HAIR:
                    rows[y][x] = DEAD_HAIR[c]
        for y in range(12, len(rows)):
            for x, c in enumerate(rows[y]):
                if c is not None and not 3 <= x <= 9 and c != 254:
                    rows[y][x] = None
        if len(rows) > 18:
            rows[18] = [None] * len(rows[18])
            for i, c in enumerate(BUN):
                put(rows, 4 + i, 18, c)
        _plug(rows, before)
        for x, y, d in ((2, 15, -1), (10, 15, 1)):
            for a, b, c in ear_shape(x, y, d, 1):
                put(rows, a, b, c)
        return rows
