"""Where a party member can still walk this turn, marked on the floor in a fight (DSCLOG's SQUARES).

The Loader works the squares out by the game's own rules and DSCLOG draws them: a small cross
on each, in the floor pass (as the shadows and the rings, so figures and walls stand on them),
the ground lightened through LIGHT (dust.py's table, made from the area's palette) and what
isn't ground to the dust (stone) darkened through DARK (the shadows' table, DSCLOG's own).

The game's rules (DSUN.EXE; HOW-THE-GAME-WORKS.md has them in words):
- a creature starts its round with Move x 10 points (doubled hasted, halved slowed), a word a
  creature at 37BD:022Bh; a step costs 10 straight and 14 diagonally (DS:055Ch);
- it may step while bit 0 of its turn's flags (37BD:01D5h) is set, whatever the step costs: with
  under 10 left after a step the points are zeroed and the bit cleared (59106h). So a square is
  in reach when a square beside it is reached with 10 points or more to spare;
- a square bars the way when its byte on the live walk map (far pointer DS:0556h, 128 x 98) has
  bit 40h: walls, shut doors, things, and every figure, the party's own too (197CCh); a diagonal
  step needs only the square stepped into free (0E711h: corners are cut).

The marks are what one click reaches: the game's route to a click takes its diagonal steps
first and its straight ones after, so the step begun with 10 to 13 points is a straight one (and
the points must cover it) unless the whole way is diagonal. Round a figure or a wall the game's
route follows its edge and can be longer than the shortest way the marks go by: there a far
marked square may take two clicks (F10 takes a move back).
"""

import heapq
import struct
from typing import Dict, Optional, Set, Tuple

from . import dust, game, shadows

TSR_SQUARES_ON = 1890  # DSCLOG's header: marks on
PSP_BYTES, SQ_MAP_PSP = 0x100, 0x5C  # SQ_MAP: in DSCLOG's PSP (the 100h bytes before its header), at 5Ch
TSR_FAR_SEG, TSR_LIGHT, TSR_DAC = 142, 236, 238  # (LIGHT's and DAC's offsets in its far block)
WALK_MAP, MAP_W, MAP_H = 0x0556, 128, 98  # DS: far pointer to the live walk map, a byte a square
BARRED = 0x40  # a square's bit: nothing walks into it
POINTS_SEG, POINTS_OFF, FLAGS_OFF = 0x37BD, 0x22B, 0x1D5  # a word a creature: movement, the turn's flags
CAN_WALK = 1  # (the flags' bit 0)
STRAIGHT, DIAGONAL = 10, 14
POSITIONS, POSITION_SIZE = game.POSITIONS, 32  # DS: each map thing's feet (x, y), a record each (the sequel's: ravlog)
LIGHT_FIRST, LIGHT_LAST = dust.FIRST, dust.LAST  # the colours LIGHT takes and gives (the sequel's: ravlog)
LIGHT_LEAST, LIGHT_LIGHTER = 0.4, dust.LIGHTER  # (dust.light_table's: the sequel's darker dirt, ravlog's DUST_LEAST and
                                                #  DUST_LIGHTER)
SIDE = 32  # the bitmap: SIDE x SIDE squares, a bit each (DSCLOG's SQ_SIDE)
MAP_BYTES = 2 + SIDE * SIDE // 8  # its origin (column, row), then SIDE // 8 bytes a row
STEPS = ((0, -1, STRAIGHT), (1, -1, DIAGONAL), (1, 0, STRAIGHT), (1, 1, DIAGONAL),
         (0, 1, STRAIGHT), (-1, 1, DIAGONAL), (-1, 0, STRAIGHT), (-1, -1, DIAGONAL))


def costs(walk_map: bytes, col: int, row: int, points: int) -> Dict[Tuple[int, int], int]:
    """What the shortest way to each square within POINTS of (COL, ROW) costs, on WALK_MAP."""
    best = {(col, row): 0}
    heap = [(0, col, row)]
    while heap:
        cost, x, y = heapq.heappop(heap)
        if cost > best[(x, y)]:
            continue
        for dx, dy, step in STEPS:
            nx, ny = x + dx, y + dy
            if cost + step > points or not free(walk_map, nx, ny):
                continue
            if cost + step < best.get((nx, ny), 1 << 30):
                best[(nx, ny)] = cost + step
                heapq.heappush(heap, (cost + step, nx, ny))
    return best


def free(walk_map: bytes, col: int, row: int) -> bool:
    return 0 <= col < MAP_W and 0 <= row < MAP_H and not walk_map[row * MAP_W + col] & BARRED


def reach(walk_map: bytes, col: int, row: int, points: int) -> Set[Tuple[int, int]]:
    """The squares a figure on (COL, ROW) with POINTS movement points walks to at a click, on the
    walk map WALK_MAP (its own square not among them): those whose shortest way costs no more
    than the points, and the squares of a clear diagonal run the last step of which is begun with
    10 or more (a run of diagonal steps alone is the one way the game spends its last step so)."""
    if points < STRAIGHT:
        return set()
    out = set(costs(walk_map, col, row, points))
    out.discard((col, row))
    for dx, dy, step in STEPS:
        if step != DIAGONAL:
            continue
        x, y, left = col + dx, row + dy, points
        while left >= STRAIGHT and free(walk_map, x, y):
            out.add((x, y))
            x, y, left = x + dx, y + dy, left - DIAGONAL
    return out


def bitmap(squares: Set[Tuple[int, int]], col: int, row: int) -> bytes:
    """DSCLOG's SQ_MAP: SIDE x SIDE squares round (COL, ROW), a bit for each of SQUARES in it."""
    left = max(0, min(MAP_W - SIDE, col - SIDE // 2))
    top = max(0, min(MAP_H - SIDE, row - SIDE // 2))
    out = bytearray(MAP_BYTES)
    out[0], out[1] = left, top
    for x, y in squares:
        if left <= x < left + SIDE and top <= y < top + SIDE:
            bit = (y - top) * SIDE + x - left
            out[2 + bit // 8] |= 1 << bit % 8
    return bytes(out)


def mover(gd) -> Optional[Tuple[int, int, int]]:
    """(column, row, points) of the party member whose turn it is in a fight, its points 0 when
    it can't walk; None out of a fight or in another's turn."""
    if not gd.in_combat():
        return None
    turn = gd.whose_turn()
    if turn is None or turn >= game.PARTY_SIZE:
        return None
    creature = gd.combatant_creature(turn)
    if creature is None:
        return None
    x, y = struct.unpack("<HH", gd.guest.read(gd.ds * 16 + POSITIONS + turn * POSITION_SIZE, 4))
    at = (gd.load_seg + POINTS_SEG) * 16 + creature * 2
    points, = struct.unpack("<h", gd.guest.read(at + POINTS_OFF, 2))
    flags, = struct.unpack("<H", gd.guest.read(at + FLAGS_OFF, 2))
    return x >> 4, y >> 4, points if flags & CAN_WALK else 0


def walk_map(gd) -> bytes:
    off, seg = struct.unpack("<HH", gd.guest.read(gd.ds * 16 + WALK_MAP, 4))
    if not (off or seg):
        return b""
    return gd.guest.read(seg * 16 + off, MAP_W * MAP_H)


class Squares:
    def __init__(self):
        self._palettes = -1
        self._map: Optional[bytes] = None  # SQ_MAP as written
        self._on: Optional[bool] = None
        self._seen: Optional[Tuple[int, int, int]] = None  # the member's square and points at the last look

    def update(self, gd, tsr_hdr: int, on: bool, palettes: int) -> None:
        """Keep DSCLOG's marks up: the squares in reach of the party member whose turn it is.
        PALETTES: shadows.Shadows.palettes (LIGHT made again when it counts)."""
        guest = gd.guest
        who = mover(gd) if on else None
        grid = walk_map(gd) if who else b""
        if not who or len(grid) < MAP_W * MAP_H:
            if self._on is None:  # (a DSCLOG just met: marks left on by another Loader?)
                self._on = guest.read(tsr_hdr + TSR_SQUARES_ON, 2) != b"\0\0"
            if self._on:
                guest.write(tsr_hdr + TSR_SQUARES_ON, struct.pack("<H", 0))
                self._on, self._map, self._seen = False, None, None
                shadows.redraw(gd, tsr_hdr)  # (the marks gone at once)
            return
        if palettes != self._palettes and palettes:
            far = struct.unpack("<H", guest.read(tsr_hdr + TSR_FAR_SEG, 2))[0] * 16
            light_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_LIGHT, 2))  # (apart: the sequel's
            dac_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_DAC, 2))        #  aren't side by side)
            dac = guest.read(far + dac_off, 768)
            guest.write(far + light_off, dust.light_table(dac, LIGHT_FIRST, LIGHT_LAST, LIGHT_LEAST, LIGHT_LIGHTER))
            self._palettes = palettes
        if who != self._seen and self._on:
            self._seen = who  # (walking: the marks stay as they were until the member stands, as
            return  # each change has the whole view drawn again, which slows the walk)
        self._seen = who
        col, row, points = who
        table = bitmap(reach(grid, col, row, points), col, row)
        if table == self._map and self._on:
            return
        guest.write(tsr_hdr + TSR_SQUARES_ON, struct.pack("<H", 0))  # (never a half-written map drawn)
        guest.write(tsr_hdr - PSP_BYTES + SQ_MAP_PSP, table)
        guest.write(tsr_hdr + TSR_SQUARES_ON, struct.pack("<H", 1))
        self._map, self._on = table, True
        shadows.redraw(gd, tsr_hdr)
