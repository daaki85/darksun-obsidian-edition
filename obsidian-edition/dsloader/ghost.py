"""See-through figures (DSCLOG's GHOST): a party member hidden in shadows and unheard, and anyone
invisible, drawn half see-through on the map, each pixel the colour halfway between the figure's
and what is under it.

DSCLOG draws them itself, in the place of the game's call that draws a thing's picture (PROBE_GHOST,
gamepatch's "ghost"): a party member whose STEALTH bit is set (stealth.py), or a thing marked in
GHOST_TAB, which the Loader keeps here: a creature with the game's Invisible effect (23: the
Invisibility spells, a psurlon's Superior Invisibility), a party member always, an enemy only while
no party member has Detect Invisibility (15: the spell, or Shadowseeker readied), as then the party
sees it. (The game draws an invisible creature as any other; its only rules for it are numbers: -4
to hit it and +4 to its saves for one who can't see it.)

DSCLOG's block in upper memory (its header's GHOST_SEG) holds what it blends with, made here from
the palette as it is (DSCLOG's copy, made again with DARK as the area changes: shadows.py):
  * REP (GH_REP): each of the palette's colours to one of REP_COUNT, the figure's colours chosen
    by cutting the palette's (the ones the game doesn't animate) into that many boxes;
  * BLEND (GH_BLEND): for each of those, a row of 256, the palette's colour nearest the halfway
    mix of it and each of the palette's.
Made in a thread (about 0.2 s of Python), and kept for the next time by the palette's colours
16-223 (KEY), the ones the game never cycles: DSCLOG's copy of the palette changes every 30 s where
fire or water cycle theirs (shadows.py's DARK made again), and keyed on all of it the tables were
made again each time, kept for good (about 13 KB each), and DSCLOG drew the figures solid
(GHOST_ON 0) for the moment it took. The last MADE_KEPT are kept. DSCLOG draws figures as ever
(GHOST_ON 0) until the first are written, and while those for a new area's palette are made.
"""

import struct
import threading
from collections import OrderedDict
from typing import Dict, List, Optional, Sequence, Tuple

from . import game

TSR_GHOST_SEG, TSR_GHOST_ON = 1826, 1828  # in DSCLOG's header
TSR_DAC = 238  # (DSCLOG's copy of the palette: the offset of DAC, 768 values of 0-63)
TSR_HDR_OFF = 20
REP_COUNT = 32
GH_BLEND, GH_REP = 0, REP_COUNT * 256
GH_TAB = GH_REP + 256
THINGS = 520
FIRST, LAST = 16, 223  # (the colours the game doesn't animate: as DSCLOG's DARK)
MADE_KEPT = 8  # (the tables kept, by KEY: the areas lately in)


def key(dac: bytes) -> bytes:
    """What the tables are kept by: the palette's colours FIRST-LAST, which the game never cycles."""
    return dac[FIRST * 3:(LAST + 1) * 3]
INVISIBLE, DETECT_INVISIBILITY = 23, 15  # (the game's effect numbers)
PARTY = range(game.PARTY_SIZE)

Colour = Tuple[int, int, int]


def palette_colours(dac: bytes) -> List[Colour]:
    """The 256 colours of a VGA palette (768 values, 0-63 each)."""
    return [tuple(dac[i * 3:i * 3 + 3]) for i in range(256)]


def representatives(colours: Sequence[Colour], count: int = REP_COUNT) -> List[Colour]:
    """COUNT colours standing for the palette's FIRST-LAST: its colours cut into that many boxes,
    each time the box with the widest spread of one of red, green and blue cut at its middle
    colour; each box's mean."""
    boxes = [sorted(set(colours[FIRST:LAST + 1]))]
    while len(boxes) < count:
        best, axis, spread = None, 0, -1
        for i, box in enumerate(boxes):
            if len(box) < 2:
                continue
            for a in range(3):
                values = [c[a] for c in box]
                if max(values) - min(values) > spread:
                    best, axis, spread = i, a, max(values) - min(values)
        if best is None:
            break
        box = sorted(boxes.pop(best), key=lambda c: c[axis])
        half = len(box) // 2
        boxes += [box[:half], box[half:]]
    out = [tuple(sum(c[a] for c in box) / len(box) for a in range(3)) for box in boxes]
    while len(out) < count:
        out.append(out[-1])
    return out


def _nearest(colour, colours: Sequence[Colour], among: Sequence[int]) -> int:
    r, g, b = colour
    best, found = None, among[0]
    for i in among:
        cr, cg, cb = colours[i]
        d = (cr - r) ** 2 + (cg - g) ** 2 + (cb - b) ** 2
        if best is None or d < best:
            best, found = d, i
            if d == 0:
                break
    return found


def tables(dac: bytes) -> Tuple[bytes, bytes]:
    """(BLEND, REP) for a palette."""
    colours = palette_colours(dac)
    reps = representatives(colours)
    among = list(range(FIRST, LAST + 1))
    rep = bytes(min(range(REP_COUNT), key=lambda r: sum((colours[c][a] - reps[r][a]) ** 2 for a in range(3)))
                for c in range(256))
    blend = bytearray(REP_COUNT * 256)
    cache: Dict[Tuple[int, int, int], int] = {}
    for r, (rr, rg, rb) in enumerate(reps):
        for c, (cr, cg, cb) in enumerate(colours):
            mix = (round((rr + cr) / 2), round((rg + cg) / 2), round((rb + cb) / 2))
            if mix not in cache:
                cache[mix] = _nearest(mix, colours, among)
            blend[r * 256 + c] = cache[mix]
    return bytes(blend), rep


def ghost_table(effects: Sequence[game.Effect]) -> bytes:
    """GHOST_TAB: a bit for each thing (N: byte N // 8, bit N % 8) drawn see-through for being
    invisible: a party member always, anyone else while no party member detects invisibility."""
    invisible = {e.owner for e in effects if e.id == INVISIBLE and 0 <= e.owner < THINGS}
    detecting = any(e.id == DETECT_INVISIBILITY and e.owner in PARTY for e in effects)
    out = bytearray((THINGS + 7) // 8)
    for thing in invisible:
        if thing in PARTY or not detecting:
            out[thing // 8] |= 1 << thing % 8
    return bytes(out)


class Ghosts:
    """Keeps DSCLOG's see-through figures' tables up (update, from the dice log's pass)."""

    def __init__(self):
        self._palettes = -1
        self._made: "OrderedDict[bytes, Tuple[bytes, bytes]]" = OrderedDict()  # (by key(): MADE_KEPT)
        self._making: Optional[bytes] = None
        self._lock = threading.Lock()
        self._dac: Optional[bytes] = None
        self._written: Optional[bytes] = None
        self._table: Optional[bytes] = None
        self._on: Optional[bool] = None

    def _make(self, dac: bytes) -> None:
        made = tables(dac)
        with self._lock:
            self._made[key(dac)] = made
            while len(self._made) > MADE_KEPT:
                self._made.popitem(last=False)
            self._making = None

    def update(self, gd, tsr_hdr: int, on: bool, palettes: int, redraw) -> None:
        """ON: the see-through figures drawn (the stealth rule's or anyone's invisibility); PALETTES
        DSCLOG's count of palettes read (shadows.Shadows.palettes); REDRAW has the view drawn again."""
        guest = gd.guest
        seg, = struct.unpack("<H", guest.read(tsr_hdr + TSR_GHOST_SEG, 2))
        if not seg:
            return  # (no block: no upper memory to spare)
        if not on:
            if self._on:
                guest.write(tsr_hdr + TSR_GHOST_ON, struct.pack("<H", 0))
                redraw()
            self._on, self._written, self._palettes = False, None, -1
            return
        if palettes != self._palettes and palettes:
            base = tsr_hdr - struct.unpack("<H", guest.read(tsr_hdr + TSR_HDR_OFF, 2))[0]
            dac_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_DAC, 2))
            self._dac = guest.read(base + dac_off, 768)
            self._palettes = palettes
        if self._dac is not None and key(self._dac) != self._written:
            wanted = key(self._dac)
            with self._lock:
                made = self._made.get(wanted)
                if made is not None:
                    self._made.move_to_end(wanted)
                start = made is None and self._making != wanted
                if start:
                    self._making = wanted
            if start:
                guest.write(tsr_hdr + TSR_GHOST_ON, struct.pack("<H", 0))  # (till they are made)
                threading.Thread(target=self._make, args=(self._dac,), daemon=True).start()
            if made is not None:
                blend, rep = made
                guest.write(seg * 16 + GH_BLEND, blend)
                guest.write(seg * 16 + GH_REP, rep)
                guest.write(tsr_hdr + TSR_GHOST_ON, struct.pack("<H", 1))
                self._written, self._on = wanted, True
                redraw()
        table = ghost_table(gd.effects())
        if table != self._table:
            guest.write(seg * 16 + GH_TAB, table)
            self._table = table
            redraw()
