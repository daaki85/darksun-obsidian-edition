"""STORE and RECALL on the character creation screen (DSCLOG's PROBE_RS_CLICK), as Baldur's Gate has
them: STORE keeps the roll on screen, RECALL brings it back however many times the die has been
rolled since.

The buttons are the game's carved stone ones (as EXIT and DONE), lettered from its own: S from
SAVE, A from LOAD, O and R from DROP, E, L and T from DELETE; C, which no button has, is drawn in
the same carving (C_SHAPE). STORE is 52 wide, RECALL as DELETE (62). They go
in the Loader's copy of RESOURCE.GFF (icons.write_resources), the buttons (BUTN, copies of SAVE's)
and the creation screen's window (WIND 3011) with the two of them under the hit points and PSP.
"""

import struct
from typing import Dict, List, Optional, Tuple

from . import gff
from .art import decode_frame
from .weaponpages import BUTN_SIZE, ITEM_AT, ITEM_SIZE, WIND_COUNT, _button, _encode, _items

CREATION = 3011  # the creation screen's window
STORE, RECALL = 0x8A0, 0x8A1  # (the buttons' ids, past the kit page's)
SAVE, EXIT, LOAD, DROP, DELETE = 2057, 2058, 6031, 6039, 2097  # the game's carved buttons
STORE_WIDTH, RECALL_WIDTH = 52, 62
STORE_AT, RECALL_AT = (88, 185), (144, 185)  # (under the hit points and PSP, clear of DONE)
FRAMES = (0, 1, 0)  # as it is, pressed, and as it is again (the game's third differs from button
# to button, out of use or lit, and these are never out of use)

Rows = List[List[Optional[int]]]
# Each letter: the button it is taken from, and which of its letters (0 first); each button's
# word (SAVE's and LOAD's letters touch, and are cut where the ink is thinnest)
LETTERS = {"S": (SAVE, 0), "A": (LOAD, 2), "E": (DELETE, 1), "T": (DELETE, 4), "O": (DROP, 2),
           "R": (DROP, 1), "L": (DELETE, 2)}
# C, which no button has: O's curve on the left, its top and bottom ending in a short carved
# stroke (as E's arms end), from row C_TOP of the button
C_TOP = 3
C_SHAPE = ("..HHHHS",
           ".HMS.MS",
           "HMS....",
           "HMS....",
           "HMS....",
           ".HMS.HS",
           ".SMMMMS",
           "..SSSS.")
WORDS = {SAVE: "SAVE", LOAD: "LOAD", DROP: "DROP", DELETE: "DELETE", EXIT: "EXIT"}


def _face(rows: Rows) -> int:
    """The button's plain face: the commonest colour inside its bevel."""
    counts: Dict[int, int] = {}
    for r in rows[2:-2]:
        for p in r[2:-2]:
            if p is not None:
                counts[p] = counts.get(p, 0) + 1
    return max(counts, key=counts.get)


def _letters(rows: Rows, count: int = 0) -> List[Tuple[int, int]]:
    """The (first, past-the-last) columns of each letter carved in ROWS: runs of columns with
    anything but the face between the bevels; with COUNT, runs holding letters that touch are
    cut where the ink is thinnest, until there are COUNT."""
    face = _face(rows)
    h, w = len(rows), len(rows[0])
    ink = [sum(rows[y][x] not in (face, None) for y in range(3, h - 3)) for x in range(w)]
    inked = [n > 0 for n in ink]
    runs, start = [], None
    for x in range(3, w - 3):
        if inked[x] and start is None:
            start = x
        elif not inked[x] and start is not None:
            runs.append((start, x))
            start = None
    if start is not None:
        runs.append((start, w - 3))
    while count and 0 < len(runs) < count:  # (the widest run cut at its thinnest middle column)
        a, b = max(runs, key=lambda r: r[1] - r[0])
        letters = round((b - a) * count / sum(r[1] - r[0] for r in runs))
        mid = a + (b - a) // max(letters, 2)
        cut = min(range(mid - 2, mid + 3), key=lambda x: ink[x])
        i = runs.index((a, b))
        runs[i:i + 1] = [(a, cut), (cut + 1, b)]
    return runs


def _glyph(resource: gff.Chunks, letter: str, frame: int) -> Tuple[Rows, int]:
    """LETTER as carved on frame FRAME of a game button: its columns (the face where it has none,
    as None) and the face it was carved on."""
    if letter == "C":  # (drawn in O's carving: its highlight, middle and shadow on that frame)
        o, face = _glyph(resource, "O", frame)
        tones = {"H": o[3][2], "M": o[4][2], "S": o[3][5]}
        rows = [list(r[:1]) * len(C_SHAPE[0]) for r in o]  # (the bevel rows as O's)
        for y, line in enumerate(C_SHAPE, start=C_TOP):
            rows[y] = [tones.get(ch) for ch in line]
        for y in range(2, len(rows) - 2):
            if not C_TOP <= y < C_TOP + len(C_SHAPE):
                rows[y] = [None] * len(C_SHAPE[0])
        return rows, face
    source, index = LETTERS[letter]
    icon = resource[("ICON", source)]
    frames, = struct.unpack_from("<H", icon, 4)
    _, _, rows = decode_frame(icon, frame if frame < frames else 0)  # (DROP has no lit frame)
    face = _face(rows)
    a, b = _letters(rows, len(WORDS[source]))[index]
    return [[None if p == face else p for p in r[a:b]] for r in rows], face


def picture(resource: gff.Chunks, text: str, width: int, frame: int) -> Rows:
    """TEXT carved on a blank button WIDTH wide (frame FRAME of the game's: the bevel and face
    of DELETE's, which is the widest, cut to WIDTH)."""
    _, _, wide = decode_frame(resource[("ICON", DELETE)], frame)
    face = _face(wide)
    h = len(wide)
    blank = [[face if 2 <= x < width - 2 and 2 <= y < h - 2 else None for x in range(width)] for y in range(h)]
    for y in range(h):  # the bevel: DELETE's left part, and its right edge
        for x in range(width):
            if not (2 <= x < width - 2 and 2 <= y < h - 2):
                src = x if x < width - 2 else len(wide[0]) - (width - x)
                blank[y][x] = wide[y][src]
    glyphs = [_glyph(resource, ch, frame)[0] for ch in text]
    gap = 1
    total = sum(len(g[0]) for g in glyphs) + gap * (len(glyphs) - 1)
    x0 = (width - total) // 2
    for g in glyphs:
        for y, r in enumerate(g):
            if not 2 <= y < h - 2:  # (the letters only, not their button's bevel)
                continue
            for dx, p in enumerate(r):
                if p is not None and 0 <= x0 + dx < width:
                    blank[y][x0 + dx] = p
        x0 += len(g[0]) + gap
    return blank


def chunks(resource: gff.Chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of RESOURCE.GFF: STORE's and RECALL's pictures and buttons, and the
    creation screen's window with both."""
    if any(k not in resource for k in (("WIND", CREATION), ("BUTN", SAVE), ("ICON", DELETE))):
        return {}
    added: Dict[Tuple[str, int], bytes] = {}
    for cid, text, width in ((STORE, "STORE", STORE_WIDTH), (RECALL, "RECALL", RECALL_WIDTH)):
        added[("ICON", cid)] = _encode([picture(resource, text, width, f) for f in FRAMES])
        button = bytearray(_button(resource[("BUTN", SAVE)], SAVE, cid))
        struct.pack_into("<HH", button, BUTN_SIZE, width, 15)
        added[("BUTN", cid)] = bytes(button)
    added[("WIND", CREATION)] = with_buttons(resource[("WIND", CREATION)])
    return added


def with_buttons(window: bytes) -> bytes:
    """The creation screen's window with STORE and RECALL after its own items (its name box
    among them, kept as it is); unchanged if they are in it."""
    if any(cid in (STORE, RECALL) for cid, _, _ in _items(window)):
        return window
    count, = struct.unpack_from("<H", window, WIND_COUNT)
    end = ITEM_AT + ITEM_SIZE * count
    body = b"".join(bytes(4) + b"BUTN" + struct.pack("<IHH", cid, x, y) + bytes(ITEM_SIZE - 16)
                    for cid, (x, y) in ((STORE, STORE_AT), (RECALL, RECALL_AT)))
    out = bytearray(window[:end] + body + window[end:])
    struct.pack_into("<I", out, 4, len(out))
    struct.pack_into("<H", out, WIND_COUNT, count + 2)
    return bytes(out)
