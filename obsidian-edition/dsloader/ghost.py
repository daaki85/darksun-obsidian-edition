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
TSR_DAC = 238  # (DSCLOG's copy of the palette: the offset of DAC in its far block, 768 values of 0-63)
TSR_FAR_SEG = 142  # (its far block's segment)
TSR_HDR_OFF = 20
REP_COUNT = 32
GH_BLEND, GH_REP = 0, REP_COUNT * 256
GH_TAB = GH_REP + 256
GH_CHANGED = GH_TAB + 79  # (1 once GHOST_TAB is written anew: DSCLOG's GHOST_UNION draws the whole view)
THINGS = 520
FIRST, LAST = 16, 223  # (the colours the game doesn't animate: as DSCLOG's DARK)
MADE_KEPT = 8  # (the tables kept, by KEY: the areas lately in)


CYCLED = (range(1, 16), range(240, 249))  # (the colours the game's cycler turns: fire, water)


def key(dac: bytes, cycled=CYCLED) -> bytes:
    """What the tables are kept by: every colour of the palette but those the game cycles (CYCLED; the
    blend reads any colour under a figure, and 224-239 change from area to area)."""
    out = set(c for r in cycled for c in r)
    return b"".join(dac[i * 3:i * 3 + 3] for i in range(256) if i not in out)
INVISIBLE, DETECT_INVISIBILITY = 23, 15  # (the game's effect numbers)
PARTY = range(game.PARTY_SIZE)

Colour = Tuple[int, int, int]


def palette_colours(dac: bytes) -> List[Colour]:
    """The 256 colours of a VGA palette (768 values, 0-63 each)."""
    return [tuple(dac[i * 3:i * 3 + 3]) for i in range(256)]


def representatives(colours: Sequence[Colour], count: int = REP_COUNT, first: int = FIRST,
                    last: int = LAST) -> List[Colour]:
    """COUNT colours standing for the palette's FIRST-LAST: its colours cut into that many boxes,
    each time the box with the widest spread of one of red, green and blue cut at its middle
    colour; each box's mean."""
    boxes = [sorted(set(colours[first:last + 1]))]
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


def tables(dac: bytes, first: int = FIRST, last: int = LAST) -> Tuple[bytes, bytes]:
    """(BLEND, REP) for a palette, its figures' colours and the blends among FIRST to LAST (the colours the game
    doesn't animate)."""
    colours = palette_colours(dac)
    reps = representatives(colours, REP_COUNT, first, last)
    among = list(range(first, last + 1))
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


def ghost_table(effects: Sequence[game.Effect], invisible_id: int = INVISIBLE, detect_id: int = DETECT_INVISIBILITY,
                things: int = THINGS) -> bytes:
    """GHOST_TAB: a bit for each thing (N: byte N // 8, bit N % 8) drawn see-through for being
    invisible: a party member always, anyone else while no party member detects invisibility (the
    sequel's: INVISIBLE_ID 53, DETECT_ID 25)."""
    invisible = {e.owner for e in effects if e.id == invisible_id and 0 <= e.owner < things}
    detecting = any(e.id == detect_id and e.owner in PARTY for e in effects)
    out = bytearray((THINGS + 7) // 8)
    for thing in invisible:
        if thing in PARTY or not detecting:
            out[thing // 8] |= 1 << thing % 8
    return bytes(out)


class Ghosts:
    """Keeps DSCLOG's see-through figures' tables up (update, from the dice log's pass). The sequel's
    (ravlog.RavGhosts) has its own colours, effects and places for the tables (DSCLOG2's far block)."""
    TSR_ON = TSR_GHOST_ON
    FIRST, LAST, CYCLED = FIRST, LAST, CYCLED
    INVISIBLE, DETECT = INVISIBLE, DETECT_INVISIBILITY

    def places(self, guest, tsr_hdr: int) -> Optional[Tuple[int, int, int]]:
        """Where BLEND, REP and GHOST_TAB go (GH_CHANGED at GHOST_TAB + 79), None with no block."""
        seg, = struct.unpack("<H", guest.read(tsr_hdr + TSR_GHOST_SEG, 2))
        return (seg * 16 + GH_BLEND, seg * 16 + GH_REP, seg * 16 + GH_TAB) if seg else None

    def key(self, dac: bytes) -> bytes:
        return key(dac, self.CYCLED)

    def __init__(self):
        self._palettes = -1
        self._made: "OrderedDict[bytes, Tuple[bytes, bytes]]" = OrderedDict()  # (by key(): MADE_KEPT)
        self._making: Optional[bytes] = None
        self._lock = threading.Lock()
        self._dac: Optional[bytes] = None
        self._written: Optional[bytes] = None
        self._table: Optional[bytes] = None
        self._on: Optional[bool] = None
        self._off = False  # (GHOST_ON put to 0 while tables are made, not on again yet)
        self._worker: Optional[threading.Thread] = None  # (the last thread started to make tables: the tests join it)
        self._failed: set = set()  # (palettes whose tables couldn't be made)

    def effects(self, gd) -> Sequence[game.Effect]:
        return gd.effects()

    def _make(self, dac: bytes) -> None:
        made = None
        try:
            made = tables(dac, self.FIRST, self.LAST)
        except Exception:  # (a palette read wrong: not made, and not tried again)
            pass
        finally:  # (a build that fails never leaves its mark: the palette not taken as being made for good)
            with self._lock:
                if made is not None:
                    self._made[self.key(dac)] = made
                    while len(self._made) > MADE_KEPT:
                        self._made.popitem(last=False)
                else:
                    self._failed.add(self.key(dac))  # (not started again and again, each pass)
                if self._making == self.key(dac):  # (its own mark only: another palette's may be being made)
                    self._making = None

    def update(self, gd, tsr_hdr: int, on: bool, palettes: int, redraw) -> None:
        """ON: the see-through figures drawn (the stealth rule's or anyone's invisibility); PALETTES
        DSCLOG's count of palettes read (shadows.Shadows.palettes); REDRAW has the view drawn again."""
        guest = gd.guest
        at = self.places(guest, tsr_hdr)
        if at is None:
            return  # (no block: no upper memory to spare)
        blend_at, rep_at, tab_at = at
        if not on:
            if self._on:
                guest.write(tsr_hdr + self.TSR_ON, struct.pack("<H", 0))
                redraw()
            self._on, self._written, self._palettes = False, None, -1
            return
        if palettes != self._palettes and palettes:
            far = struct.unpack("<H", guest.read(tsr_hdr + TSR_FAR_SEG, 2))[0] * 16
            dac_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_DAC, 2))
            dac = guest.read(far + dac_off, 768)
            if len(dac) == 768:  # (a short read: looked at again next pass)
                self._dac = dac
                self._palettes = palettes
        if self._dac is not None and self.key(self._dac) != self._written:
            wanted = self.key(self._dac)
            with self._lock:
                made = self._made.get(wanted)
                if made is not None:
                    self._made.move_to_end(wanted)
                start = made is None and self._making != wanted and wanted not in self._failed
            if start:
                guest.write(tsr_hdr + self.TSR_ON, struct.pack("<H", 0))  # (till they are made)
                self._off = True
                with self._lock:  # (only once the write is made: marked first, a refused write
                    self._making = wanted  # left them marked as being made, and never made)
                self._worker = threading.Thread(target=self._make, args=(self._dac,), daemon=True)
                self._worker.start()
            if made is not None:
                blend, rep = made
                guest.write(blend_at, blend)
                guest.write(rep_at, rep)
                guest.write(tsr_hdr + self.TSR_ON, struct.pack("<H", 1))
                self._written, self._on, self._off = wanted, True, False
                redraw()
        elif self._off and self._dac is not None:  # (the palette back to the written one before
            guest.write(tsr_hdr + self.TSR_ON, struct.pack("<H", 1))  # the other was made: on again)
            self._off = False
            redraw()
        table = ghost_table(self.effects(gd), self.INVISIBLE, self.DETECT)
        if table != self._table:
            guest.write(tab_at, table)
            guest.write(tab_at + (GH_CHANGED - GH_TAB), b"\x01")  # (drawn again in the enemies' turns too)
            self._table = table
            redraw()
