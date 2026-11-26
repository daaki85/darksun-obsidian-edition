"""Names floating over figures on the map (DSCLOG's LABELS): a spell's name over its caster as it
is cast (DSCLOG's CAST_SITE, the dice log's KIND_CAST), "Miss" over whom an attack missed, and
"Armor: 7 left" over a creature whose spell has used a charge (the dice log's charge lines).

The Loader draws each in the game's font, its ink with a dark edge round it, as two one-bit masks
(ROW bytes a row, bit 0 of the first byte the leftmost pixel) into one of DSCLOG's SLOTS in its
tail (its segment the header's TSR_TAIL_SEG, the slots' offset there TSR_LABELS); DSCLOG places it over the figure's feet and puts it on the screen again as
the game draws there. A label stays SHOW_FOR seconds; a new one takes the slot of one over the same
figure, else a free one, else the oldest; but a charge used (PRIORITY, CHARGE_FOR seconds) is
never replaced by a "Miss" or a spell's name while it shows. A slot is written with its number 0 first, so DSCLOG
never puts a half-written one, then a new number for the new label.

The same slots carry the names of things that can be used while Alt is held (usable.py; Labels.names):
standing labels of the lowest priority, which take free slots only; and, in a fight, the chance to
hit over the enemy under the pointer (hover.py; Labels.hover), one standing label lower still.
"""

import struct
from typing import List, Optional, Tuple

from . import combatlog

TSR_TAIL_SEG, TSR_LABELS = 1834, 1838  # DSCLOG's header: its tail's segment, LBL_SLOTS's offset there
SLOTS = 4               # (DSCLOG's LBL_SLOTS)
ROW = 16                # (LBL_ROW) bytes a mask's row
WIDTH_MOST = ROW * 8
HEIGHT_MOST = 11        # (LBL_H_MOST)
MASK = ROW * HEIGHT_MOST
SIZE = 8 + 2 * MASK     # (LBL_SIZE)
SHOW_FOR = 1.5          # seconds a label stays
NAME, NAME_FOR = -1, 1.0  # a usable thing's name (usable.py): its priority, the least; seconds it outlasts its last asking
HOVER, HOVER_FOR = -2, 1.0  # the chance to hit over the enemy under the pointer (hover.py): the least of all; seconds it outlasts its last asking
CHARGE_FOR = 3.0        # ... a charge used ("Armor: 7 left"), which no "Miss" or spell's name replaces
UP = 34                 # its bottom row this far above the figure's feet: over a man's head
SPELL_INK = (255, 220, 90)
MISS_INK = (225, 225, 225)
CHARGE_INK = (150, 200, 255)  # (an effect's charge used: "Armor: 7 left")
EDGE = (12, 8, 4)
MISS = "Miss"
# (words shortened, in turn, until a spell's name fits WIDTH_MOST)
SHORTER = (("Conjure ", ""), ("Elemental", "Elem."), ("Protection", "Prot."), ("Prot'n", "Prot."),
           ("Blindness or Deafness", "Blind/Deaf"), ("Resistance", "Resist."), ("Invulnerability", "Invuln."),
           ("Normal ", ""), ("Paralysis", "Paral."), ("Lightning", "Lightn."))

Masks = Tuple[int, int, bytes, bytes]   # width, height, the ink's mask, the edge's


def width(font, text: str) -> int:
    return sum(font.glyph(c)[0] for c in text) + 2


def fit(font, text: str) -> str:
    """TEXT, shortened if need be to fit WIDTH_MOST: words first, then letters off its end."""
    for old, new in SHORTER:
        if width(font, text) <= WIDTH_MOST:
            break
        text = text.replace(old, new)
    while width(font, text) > WIDTH_MOST and len(text) > 1:
        text = text[:-2].rstrip() + "."
    return text


def masks(font, text: str) -> Masks:
    """TEXT in FONT's ink, a pixel's border round it, a dark edge on the border next to the ink."""
    text = fit(font, text)
    w, h = width(font, text), min(font.height + 2, HEIGHT_MOST)
    ink = [[False] * w for _ in range(h)]
    x = 1
    for c in text:
        gw, data = font.glyph(c)
        for gy in range(min(font.height, h - 2)):
            for gx in range(gw):
                if data[gy * gw + gx] == combatlog.FONT_INK:
                    ink[gy + 1][x + gx] = True
        x += gw
    edge = [[not ink[y][x] and any(ink[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                                   if 0 <= y + dy < h and 0 <= x + dx < w)
             for x in range(w)] for y in range(h)]
    return w, h, _bits(ink), _bits(edge)


def _bits(rows: List[List[bool]]) -> bytes:
    out = bytearray(MASK)
    for y, row in enumerate(rows):
        for x, on in enumerate(row):
            if on:
                out[y * ROW + x // 8] |= 1 << (x % 8)
    return bytes(out)


def slot_bytes(number: int, thing: int, m: Masks, ink: int, edge: int, up: int = UP) -> bytes:
    w, h, ink_mask, edge_mask = m
    return struct.pack("<BBBBBBH", number, w, h, up, ink, edge, thing) + ink_mask + edge_mask


class Labels:
    def __init__(self):
        self.on = True
        self.font = None
        self._number = 0
        # (until, thing, text, priority)
        self._slots: List[Optional[Tuple[float, int, str, int]]] = [None] * SLOTS
        self._stale = False  # a label was taken off or changed since took_off() was last asked
        self._swept = False  # the slots another Loader left filled have been emptied (tick)

    def attached(self) -> None:
        """A game newly attached: none of its slots is this Loader's yet."""
        self._slots = [None] * SLOTS
        self._swept = False

    def took_off(self) -> bool:
        """Whether a label has been taken off, moved or reworded since the last asking. DSCLOG has
        the game draw the label's old place again, but in a still scene (a fight, nobody moving)
        that showed for one frame and the label was back on the screen until something else drew
        the view (seen with "Miss" and the pointer's chance alike, 2026-11-18), so the dice log
        then has the whole view drawn again (shadows.redraw)."""
        stale, self._stale = self._stale, False
        return stale

    def _clear(self, guest, tsr_hdr: int, n: int) -> None:
        guest.write(slots_at(guest, tsr_hdr) + n * SIZE, b"\0")
        self._slots[n] = None
        self._stale = True

    def show(self, guest, tsr_hdr: Optional[int], thing: Optional[int], text: str, colour, now: float,
             priority: int = 0) -> None:
        """TEXT over map thing THING (a combatant) for SHOW_FOR seconds (CHARGE_FOR with PRIORITY 1),
        in COLOUR (0-255 a channel). A label of lower priority than one showing over the same figure,
        or than both shown when no slot is free, is left out."""
        if not self.on or self.font is None or tsr_hdr is None or thing is None or thing < 0 or not text:
            return
        hold = CHARGE_FOR if priority else SHOW_FOR
        same = next((n for n, s in enumerate(self._slots) if s and s[1] == thing), None)
        if same is not None and self._slots[same][2] == text:
            self._slots[same] = (now + hold, thing, text, priority)  # (shown already: kept longer)
            return
        if same is not None and self._slots[same][3] > priority:
            return  # (a charge used still showing over this figure)
        free = next((n for n, s in enumerate(self._slots) if s is None), None)
        if same is None and free is None:
            n = min(range(SLOTS), key=lambda k: (self._slots[k][3], self._slots[k][0]))
            if self._slots[n][3] > priority:
                return
        n = same if same is not None else free if free is not None else n
        self._put(guest, tsr_hdr, n, thing, text, colour, now + hold, priority, UP)

    def _put(self, guest, tsr_hdr: int, n: int, thing: int, text: str, colour, until: float, priority: int,
             up: int) -> None:
        """Slot N written: its number 0 first, the new one last."""
        dac = _dac(guest, tsr_hdr)
        self._number = self._number % 255 + 1
        at = slots_at(guest, tsr_hdr) + n * SIZE
        self._stale = self._stale or self._slots[n] is not None
        guest.write(at, b"\0")
        data = slot_bytes(self._number, thing, masks(self.font, text), combatlog.nearest(dac, colour),
                          combatlog.nearest(dac, EDGE), up)
        guest.write(at + 1, data[1:])
        guest.write(at, data[:1])
        self._slots[n] = (until, thing, text, priority)

    def names(self, guest, tsr_hdr: Optional[int], wanted, now: float) -> None:
        """The standing names of things that can be used (usable.py): WANTED, (thing, text, colour,
        how far above its feet) each, the first the most wanted, kept up while asked for (NAME_FOR
        seconds past the last asking) and taken off when no longer among them. They are the least of
        the labels (priority NAME): one takes a free slot only, never another label's nor another
        name's, and gives its own up to any "Miss", spell's name or charge. Shown whether or not
        the floating names are switched on (ON is theirs)."""
        if tsr_hdr is None:
            return
        keep = {(thing, text) for thing, text, _, _ in wanted}
        for n, s in enumerate(self._slots):
            if s is not None and s[3] == NAME and (s[1], s[2]) not in keep:
                self._clear(guest, tsr_hdr, n)
        if self.font is None:
            return
        for thing, text, colour, up in wanted:
            same = next((n for n, s in enumerate(self._slots) if s and s[1] == thing), None)
            if same is not None:
                if self._slots[same][3] == NAME:
                    self._slots[same] = (now + NAME_FOR, thing, text, NAME)
                continue  # (or another label over it: left)
            free = next((n for n, s in enumerate(self._slots) if s is None), None)
            if free is not None and text:
                self._put(guest, tsr_hdr, free, thing, text, colour, now + NAME_FOR, NAME, up)

    def hover(self, guest, tsr_hdr: Optional[int], thing: Optional[int], text: str, colour, now: float,
              up: int = UP) -> None:
        """The chance to hit over the enemy under the pointer (hover.py): TEXT over map thing THING
        while asked for (HOVER_FOR seconds past the last asking), one label at most; THING None
        takes it off. It is the least of the labels (priority HOVER): it takes a free slot only
        and waits while anything else shows over its figure, and show() gives its slot to a
        "Miss", a spell's name or a charge over that figure, or to any of them when no slot is
        free. The same text asked for again only keeps it up (nothing written: no flicker). Shown
        whether or not the floating names are switched on."""
        if tsr_hdr is None:
            return
        mine = next((n for n, s in enumerate(self._slots) if s is not None and s[3] == HOVER), None)
        other = thing is not None and any(s is not None and s[1] == thing and s[3] != HOVER for s in self._slots)
        if thing is None or not text or self.font is None or other:
            if mine is not None:
                self._clear(guest, tsr_hdr, mine)
            return
        if mine is not None and self._slots[mine][1:3] == (thing, text):
            self._slots[mine] = (now + HOVER_FOR, thing, text, HOVER)
            return
        n = mine if mine is not None else next((k for k, s in enumerate(self._slots) if s is None), None)
        if n is not None:
            self._put(guest, tsr_hdr, n, thing, text, colour, now + HOVER_FOR, HOVER, up)

    def tick(self, guest, tsr_hdr: Optional[int], now: float) -> None:
        """Labels whose time is up taken off (all of them but usable things' names and the
        pointer's chance to hit, switched off)."""
        if tsr_hdr is None:
            return
        if not self._swept:
            # (a Loader stopped with a label up left it in its slot for good: the pointer's chance
            # stands as long as the pointer rests, so a restarted dice log met one, 2026-11-18)
            self._swept = True
            for n, s in enumerate(self._slots):
                if s is None and guest.read(slots_at(guest, tsr_hdr) + n * SIZE, 1)[0]:
                    self._clear(guest, tsr_hdr, n)
        for n, s in enumerate(self._slots):
            if s is not None and (now >= s[0] or (not self.on and s[3] >= 0)):
                self._clear(guest, tsr_hdr, n)


def slots_at(guest, tsr_hdr: int) -> int:
    """Where DSCLOG's LBL_SLOTS are (a linear address): in its tail, TSR_TAIL_SEG:TSR_LABELS."""
    seg, _, off = struct.unpack("<HHH", guest.read(tsr_hdr + TSR_TAIL_SEG, 6))
    return seg * 16 + off


def _dac(guest, tsr_hdr: int) -> bytes:
    return combatlog.tsr_dac(guest, tsr_hdr)
