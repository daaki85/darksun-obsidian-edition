"""PAGE 1 to PAGE 4 buttons in the save/load window (DSCLOG's PROBE_SAVE_PAGE).

The game's save/load window (WIND 3009 in RESOURCE.GFF) shows ten saves. DSCLOG shows them on
four pages (the game's own SAVE01.SAV to SAVE10.SAV, then SAVB, SAVC and SAVD01.SAV to 10.SAV),
for PgUp and PgDn or a click on PAGE 1 to PAGE 4.
The buttons are the game's kind: a button (BUTN) placed in the window, under EXIT, and its four
pictures (ICON: as it is, the pointer over it, out of use, pressed) made from EXIT's, its letters
taken away and the page's put in, in the game's text font (FONT 100: the buttons' own carved
letters have no P, G or digits) and in EXIT's letters' colours. They go in the Loader's copy of
RESOURCE.GFF (icons.write_resources); the page shown is out of use (DSCLOG).
"""

import struct
from typing import Dict, List, Optional, Tuple

from . import gff
from .art import FONT_INK, FONT_SHADOW, Font, decode_frame

WINDOW = 3009  # the save/load window
EXIT = 0x80A  # its EXIT button, whose pictures the new ones are made from
PAGES = ((0x815, "PAGE 1", 70), (0x816, "PAGE 2", 90), (0x817, "PAGE 3", 110),  # (id, text, y):
         (0x818, "PAGE 4", 130))  # under EXIT (y 50), 20 apart as LOAD/SAVE (30) and EXIT are
BUTTON_X = 231
FONT_ID = 100
WIND_COUNT = 243  # the window's word: how many items it has
ITEM_SIZE = 30  # an item, from 105h: room for its chunk's address (the game's), its type, id, x,
                # y, then nothing
TEXT_TOP = 2  # the font's top row (its letters a row lower, as EXIT's: rows 3 to 10)
# each picture's colours (stone, letters, letters' shadow), its stone inside the frame (rows,
# columns: first and last) and how far its letters are moved down (pressed: up a row, as EXIT's)
LOOKS = ((24, 28, 20, (2, 12), (2, 41), 0), (27, 31, 24, (2, 12), (2, 41), 0),
         (24, 27, 22, (2, 12), (2, 41), 0), (24, 28, 20, (2, 11), (2, 40), -1))

Rows = List[List[Optional[int]]]


def encode_frames(frames: List[Rows]) -> bytes:
    """A picture chunk of several frames, as the game's own: its size, how many, each one's
    offset, then each (as icons.encode)."""
    from .icons import encode
    bodies = [encode(rows)[10:] for rows in frames]  # (each without the one-frame head)
    head = 4 + 2 + 4 * len(bodies)
    offsets, at = [], head
    for body in bodies:
        offsets.append(at)
        at += len(body)
    return struct.pack(f"<IH{len(bodies)}I", at, len(bodies), *offsets) + b"".join(bodies)


def button_pictures(exit_icon: bytes, font: Font, text: str) -> List[Rows]:
    """EXIT's four pictures with TEXT for its letters."""
    count = struct.unpack_from("<H", exit_icon, 4)[0]
    width = sum(font.glyph(ch)[0] for ch in text)
    out = []
    for f in range(min(count, len(LOOKS))):
        _, _, rows = decode_frame(exit_icon, f)
        rows = [list(r) for r in rows]
        stone, ink, shadow, (top, bottom), (left, right), push = LOOKS[f]
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                rows[y][x] = stone
        x0 = left + (right - left + 1 - width) // 2
        colours = {FONT_INK: ink, FONT_SHADOW: shadow}
        for ch in text:
            gw, data = font.glyph(ch)
            for gy in range(font.height):
                y = TEXT_TOP + push + gy
                for gx in range(gw):
                    c = colours.get(data[gy * gw + gx])
                    if c is not None and top <= y <= bottom and left <= x0 + gx <= right:
                        rows[y][x0 + gx] = c
            x0 += gw
        out.append(rows)
    return out


def _button(exit_button: bytes, new_id: int) -> bytes:
    """EXIT's button chunk for button NEW_ID (its id, and its pictures', changed)."""
    return exit_button.replace(struct.pack("<I", EXIT), struct.pack("<I", new_id))


def window_with_buttons(window: bytes) -> bytes:
    """The window with the two buttons put in after its items (unchanged if they are there)."""
    if any(struct.pack("<I", cid) in window for cid, _, _ in PAGES):
        return window
    items = b"".join(bytes(4) + b"BUTN" + struct.pack("<IHH", cid, BUTTON_X, y) + bytes(ITEM_SIZE - 16)
                     for cid, _, y in PAGES)
    out = bytearray(window + items)
    struct.pack_into("<I", out, 4, len(out))
    struct.pack_into("<H", out, WIND_COUNT, struct.unpack_from("<H", window, WIND_COUNT)[0] + len(PAGES))
    return bytes(out)


def chunks(resource: gff.Chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of RESOURCE.GFF: the window with the buttons, and theirs."""
    font = Font(resource[("FONT", FONT_ID)])
    exit_icon, exit_button = resource[("ICON", EXIT)], resource[("BUTN", EXIT)]
    added = {("WIND", WINDOW): window_with_buttons(resource[("WIND", WINDOW)])}
    for cid, text, _ in PAGES:
        added[("ICON", cid)] = encode_frames(button_pictures(exit_icon, font, text))
        added[("BUTN", cid)] = _button(exit_button, cid)
    return added
