"""A ring on the ground under the enemy chosen with Tab in a fight (DSCLOG's RINGS).

DSCLOG draws it in the floor pass, as the shadows, so the figure stands in it: an ellipse at the
marked thing's feet, the ground reddened through RED, which the Loader makes from the area's
palette (each colour's nearest redder one). The Loader marks the chosen one (targeting.py) while
the party is in a fight, among the enemies (the creatures standing on another side than the
party's); when the mark changes, the view is drawn again.

Out of a fight the same rings, in gold (GOLD, through the same table: gold_table), go under
everything that can be used while Alt is held (usable.py, which gives update its table of marks).
The table and its colours have this one owner: in a fight it is the Tab ring's, red, whatever is
held.
"""

import functools
import struct
from typing import Optional

from . import game, shadows

TSR_RINGS_ON, TSR_RING_TAB, TSR_RED = 244, 246, 248  # DSCLOG's header (RING_TAB's and RED's offsets in its far block)
TSR_DAC = 238  # (DAC's offset in its far block, as dust.py)
TSR_FAR_SEG = 142  # (its far block's segment)
TSR_HDR_OFF = 20
THINGS = 520
FIRST, LAST = 16, 223  # the colours the game doesn't animate
RED = (230, 40, 30)
TOWARD = 0.6  # how far toward RED a colour is wanted
HUE_WEIGHT = 2
GOLD = (255, 214, 64)  # the tint of the rings under what can be used (usable.py)
GOLD_TOWARD = 0.55
GOLD_NEARER = 24  # how much nearer GOLD a colour's tinted one must be (clearly golder)
STATUS_DEAD = 5
SIDE_NEUTRAL = 4  # (the arena's Tied-up Prisoner: on no one's side)
# Wake of the Ravager's sides are bits: the party's foes are those whose bit (1 << side) is in this mask,
# as the game itself colours the figure under the pointer (21112h: "test ax,0F80h", sides 7-11, the
# Draxans' 7) and picks targets; the street's other people (sides 1-6) aren't. None: Shattered Lands'
# rule (another side than the leader's, not the neutral one). ravlog sets it.
HOSTILE_SIDES: Optional[int] = None
CHOSEN = 2  # (DSCLOG's ring kind: three pixels thick, reddened three times)
OFF, ONLY_CHOSEN = "off", "chosen"  # the Options tab's choice of rings


def mode(settings: dict) -> str:
    """The ring to draw, as saved (the chosen enemy's unless switched off; an older "all", under
    every enemy, is the chosen one's now)."""
    return OFF if settings.get("rings", ONLY_CHOSEN) == OFF else ONLY_CHOSEN


@functools.lru_cache(maxsize=8)  # (the same palette, the same table: worked out once)
def red_table(dac: bytes, first: int = FIRST, last: int = LAST) -> bytes:
    """Each colour's redder one among the palette's (0: none redder enough). DAC: 0-63 values;
    FIRST to LAST the colours taken and given (the sequel's: ravlog.RED_FIRST, RED_LAST)."""
    pal = [tuple(min(255, dac[i * 3 + k] * 4) for k in range(3)) for i in range(256)]
    out = bytearray(256)
    for i in range(first, last + 1):
        c = pal[i]
        want = tuple(v + (r - v) * TOWARD for v, r in zip(c, RED))
        best, score = 0, None
        for j in range(first, last + 1):
            p = pal[j]
            if j == i or p[0] - (p[1] + p[2]) / 2 <= c[0] - (c[1] + c[2]) / 2 + 8:
                continue  # (redder, clearly)
            d = sum((a - b) ** 2 for a, b in zip(p, want))
            d += HUE_WEIGHT * (((p[0] - p[1]) - (want[0] - want[1])) ** 2)
            if score is None or d < score:
                best, score = j, d
        out[i] = best
    return bytes(out)


@functools.lru_cache(maxsize=8)
def gold_table(dac: bytes) -> bytes:
    """Each colour's golder one among the palette's (0: none clearly nearer GOLD), as red_table."""
    pal = [tuple(min(255, dac[i * 3 + k] * 4) for k in range(3)) for i in range(256)]
    far = lambda p: sum((a - b) ** 2 for a, b in zip(p, GOLD)) ** 0.5
    out = bytearray(256)
    for i in range(FIRST, LAST + 1):
        c = pal[i]
        want = tuple(v + (t - v) * GOLD_TOWARD for v, t in zip(c, GOLD))
        best, score = 0, None
        for j in range(FIRST, LAST + 1):
            p = pal[j]
            if j == i or far(p) > far(c) - GOLD_NEARER:
                continue
            d = sum((a - b) ** 2 for a, b in zip(p, want))
            if score is None or d < score:
                best, score = j, d
        out[i] = best
    return bytes(out)


def enemies(gd) -> list:
    """The things (combatants) standing on another side than the party's leader (not a neutral
    one's), in a fight; in the sequel those on a side in HOSTILE_SIDES."""
    if not gd.in_combat():
        return []
    leader = gd.creature(0)
    if len(leader) < game.CREATURE_SIZE:
        return []
    out = []
    for combatant, index in sorted(gd.combatants().items()):
        if combatant >= THINGS or index < game.PARTY_SIZE:
            continue
        rec = gd.creature(index)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME]:
            continue
        hp = struct.unpack_from("<h", rec, 0)[0]
        side = rec[game.CREATURE_SIDE]
        if HOSTILE_SIDES is not None:
            foe = side < 16 and bool(HOSTILE_SIDES >> side & 1)
        else:
            foe = side not in (leader[game.CREATURE_SIDE], SIDE_NEUTRAL)
        if hp > 0 and rec[game.CREATURE_STATUS] != STATUS_DEAD and foe:
            out.append(combatant)
    return out


def ring_table(chosen: Optional[int]) -> bytes:
    out = bytearray(THINGS)
    if chosen is not None and 0 <= chosen < THINGS:
        out[chosen] = CHOSEN
    return bytes(out)


class Rings:
    def __init__(self):
        self._palettes = -1
        self._table: Optional[bytes] = None
        self._on: Optional[bool] = None
        self._tint = None

    def update(self, gd, tsr_hdr: int, on: bool, palettes: int, chosen: Optional[int] = None,
               marks: Optional[bytes] = None) -> list:
        """Keep DSCLOG's ring up under the enemy chosen (ON: the Options tab's ring), or, out of a
        fight, its rings under MARKS (usable.py's table of what can be used, None when not held),
        those in gold. Returns the enemies."""
        guest = gd.guest
        marked = enemies(gd)
        if marks is not None and (marked or gd.in_combat()):
            marks = None  # (a fight: the table is the Tab ring's)
        on = on or marks is not None
        tint = red_table if marks is None else gold_table
        far = struct.unpack("<H", guest.read(tsr_hdr + TSR_FAR_SEG, 2))[0] * 16
        tab_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_RING_TAB, 2))
        if not on:
            if self._on is not False:
                guest.write(tsr_hdr + TSR_RINGS_ON, struct.pack("<H", 0))
                if self._table and any(self._table):
                    guest.write(far + tab_off, bytes(THINGS))  # (none left for the next time they are on)
                    shadows.redraw(gd, tsr_hdr)
            self._on, self._table, self._palettes = False, None, -1
            return marked
        fresh = bool((palettes != self._palettes or tint is not self._tint) and palettes)
        if fresh:
            red_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_RED, 2))
            dac_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_DAC, 2))
            guest.write(far + red_off, tint(guest.read(far + dac_off, 768)))
            if tint is not self._tint and self._table and any(self._table):
                self._table = None  # (rings in the other tint: the view drawn again)
        table = marks if marks is not None else ring_table(chosen if chosen in marked else None)
        if table != self._table:
            guest.write(far + tab_off, table)
            self._table = table
            shadows.redraw(gd, tsr_hdr)
        if fresh:  # (on only once the table and its colours are these)
            guest.write(tsr_hdr + TSR_RINGS_ON, struct.pack("<H", 1))
            self._palettes, self._on, self._tint = palettes, True, tint
        return marked
