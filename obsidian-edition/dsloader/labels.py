"""Names floating over figures on the map (DSCLOG's LABELS): a spell's name over its caster as it
is cast (DSCLOG's CAST_SITE, the dice log's KIND_CAST), "Miss" over whom an attack missed, and
"Armor: 7 left" over a creature whose spell has used a charge (the dice log's charge lines).

The Loader draws each in the game's font, its ink with a dark edge round it, as two one-bit masks
(ROW bytes a row, bit 0 of the first byte the leftmost pixel) into one of DSCLOG's SLOTS in its
header (TSR_LABELS); DSCLOG places it over the figure's feet and puts it on the screen again as
the game draws there. A label stays SHOW_FOR seconds; a new one takes the slot of one over the same
figure, else a free one, else the oldest. A slot is written with its number 0 first, so DSCLOG
never puts a half-written one, then a new number for the new label.
"""

import struct
from typing import List, Optional, Tuple

from . import combatlog

TSR_LABELS = 374        # DSCLOG's header: LBL_SLOTS
SLOTS = 2               # (DSCLOG's LBL_SLOTS)
ROW = 16                # (LBL_ROW) bytes a mask's row
WIDTH_MOST = ROW * 8
HEIGHT_MOST = 11        # (LBL_H_MOST)
MASK = ROW * HEIGHT_MOST
SIZE = 8 + 2 * MASK     # (LBL_SIZE)
SHOW_FOR = 1.5          # seconds a label stays
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
        self._slots: List[Optional[Tuple[float, int, str]]] = [None] * SLOTS  # (until, thing, text)

    def show(self, guest, tsr_hdr: Optional[int], thing: Optional[int], text: str, colour, now: float) -> None:
        """TEXT over map thing THING (a combatant) for SHOW_FOR seconds, in COLOUR (0-255 a channel)."""
        if not self.on or self.font is None or tsr_hdr is None or thing is None or thing < 0 or not text:
            return
        same = next((n for n, s in enumerate(self._slots) if s and s[1] == thing), None)
        if same is not None and self._slots[same][2] == text:
            self._slots[same] = (now + SHOW_FOR, thing, text)  # (shown already: kept longer)
            return
        free = next((n for n, s in enumerate(self._slots) if s is None), None)
        n = same if same is not None else free if free is not None else \
            min(range(SLOTS), key=lambda k: self._slots[k][0])
        dac = _dac(guest, tsr_hdr)
        self._number = self._number % 255 + 1
        at = tsr_hdr + TSR_LABELS + n * SIZE
        guest.write(at, b"\0")
        data = slot_bytes(self._number, thing, masks(self.font, text), combatlog.nearest(dac, colour),
                          combatlog.nearest(dac, EDGE))
        guest.write(at + 1, data[1:])
        guest.write(at, data[:1])
        self._slots[n] = (now + SHOW_FOR, thing, text)

    def tick(self, guest, tsr_hdr: Optional[int], now: float) -> None:
        """Labels whose time is up taken off (all of them, switched off)."""
        if tsr_hdr is None:
            return
        for n, s in enumerate(self._slots):
            if s is not None and (now >= s[0] or not self.on):
                guest.write(tsr_hdr + TSR_LABELS + n * SIZE, b"\0")
                self._slots[n] = None


def _dac(guest, tsr_hdr: int) -> bytes:
    base = tsr_hdr - struct.unpack("<H", guest.read(tsr_hdr + combatlog.TSR_HDR_OFF, 2))[0]
    dac_off, = struct.unpack("<H", guest.read(tsr_hdr + combatlog.TSR_DAC, 2))
    return guest.read(base + dac_off, 768)
