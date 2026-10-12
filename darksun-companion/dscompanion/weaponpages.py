"""The weapon pages of the character creation panel (weapon specialization; DSCLOG's PROBE_WP_*).

The creation screen's panel shows the psionic disciplines (WIND 3012 in RESOURCE.GFF) or, for a
cleric, druid or ranger, the clerical spheres (WIND 3013), each a column of rows to mark and a
button under them that changes between the two. With weapon specialization, a fighter, gladiator
or ranger also chooses a weapon kind there: four more windows like the spheres', four kinds each
(specialize.KINDS, in order), their button MORE SPECS, the last's VIEW PSIONICS. The windows a
warrior is shown (3018 for the disciplines, 3019 for the spheres) have WEAPON SPEC in place of
VIEW SPHERES or VIEW PSIONICS.

The rows' and buttons' pictures (ICON, three frames: as they are, out of use, marked) are made in
the game's small carved letters, taken from its own rows (CLERIC, P-KINESIS and the rest); the
game has no X or Q in them, so those two are drawn here in the same hand. They go in the
Ledger's copy of RESOURCE.GFF (icons.write_resources), with the buttons (BUTN, copies of the
spheres') and the windows.
"""

import struct
from typing import Dict, List, Optional, Tuple

from . import gff, specialize
from .art import decode_frame

DISCIPLINES, SPHERES = 3012, 3013  # the game's windows
PAGES = (3014, 3015, 3016, 3017)  # the weapon pages
WARRIOR_DISCIPLINES, WARRIOR_SPHERES = 3018, 3019
PICKER = 3021  # the level-up window (like the psionicists', 17501)
PSIONIC_PICKER = 17501
PICK_FIRST = 0x860  # its slots, 0x860 + kind
PICK_COUNT_BUTTON, PICK_EXIT = 0x2C37, 0x4396  # (the psionicists' window's: picks left, EXIT)
# The level-up window: each kind a slot with a weapon's picture (the game's inventory picture of
# one of that kind: PICTURES, objects in SEGOBJEX.GFF), six to a row, the window bigger than
# the psionicists' (its marble, PSIONIC_BACKGROUND, carried on) and its two lines under the slots
# (DSCLOG's PROBE_PK_TITLE: PICK_TITLE_Y). A slot is three pictures: as it is, lit (its edge
# near-white, the pointer on it), and out of use (the weapon a grey shape).
PICK_SLOT, PICK_PITCH, PICK_COLUMNS, PICK_TOP = 32, 34, 6, 7
PICK_WIDTH, PICK_HEIGHT = 214, 156
PICK_COUNT_GAP = 28  # (the picks left, a number centred in its 42-wide button, this far before EXIT)
PICK_TITLE_Y = PICK_TOP + 3 * PICK_PITCH + 3
PICK_BACKGROUND, PSIONIC_BACKGROUND = 3022, 17001  # (BMP chunks)
WIND_WIDTH, WIND_HEIGHT, WIND_BACKGROUND = 0xBE, 0xC0, 0xC2
BUTN_SIZE = 0x28  # a button's width and height
PICTURES = (1014, 1185, 2504, 2427, 2506, 1183, 2508, 2510, 1019, 2512, 1011, 1188, 1010, 1017, 1015, 1016)
POLEARM, POLEARM_SIZE = 9, 26  # (its picture, 36 pixels square, made smaller)
# the interface's blue-greys, which no region's palette changes (17-31): the slot's face, its
# dark top and left, light bottom and right, its lit edge, and a weapon out of use
SLOT_FACE, SLOT_DARK, SLOT_LIGHT, SLOT_LIT, SLOT_OUT = 19, 17, 24, 31, 22
MARBLE_LIGHT, MARBLE_DARK = 212, 208  # (the marble's own bevel)
ROW_FIRST = 0x840  # the 16 kinds' rows, 0x840 + kind (after the dialogue window's and others', 81Ch-833h)
MORE, BACK, VIEW = 0x850, 0x851, 0x852  # MORE SPECS, VIEW PSIONICS, WEAPON SPEC
ROW_TEMPLATE, TOGGLE_TEMPLATE = 0x7FA, 0x7FF  # (AIR's row and VIEW PSIONICS's button)
SPHERE_TOGGLE, DISCIPLINE_TOGGLE = 0x7FF, 0x7FE
WIND_COUNT, ITEM_AT, ITEM_SIZE = 243, 0x105, 30
ROW_PAD = 10  # a row's letters start this far in (the mark goes before them)
HEIGHT = 7

# The game's labels and what they say, to take letters from: each run of columns with ink is a
# letter where the counts agree; CUTS takes the rest from where letters touch (icon, first and
# past-the-last column, letter)
LABELS = {0x7D2: "CLERIC", 0x7D3: "DRUID", 0x7D4: "FIGHTER", 0x7D7: "PSIONICIST", 0x7D8: "RANGER",
          0x7D9: "THIEF", 0x7FA: "AIR", 0x7FB: "EARTH", 0x7FC: "FIRE", 0x7FE: "VIEW SPHERES",
          0x7FF: "VIEW PSIONICS"}
CUTS = ((0x7F6, 20, 28, "K"), (0x7F7, 20, 31, "M"), (0x7F7, 56, 64, "B"), (0x7F8, 79, 88, "Y"))
DRAWN = {
    "X": ("###..###",
          ".##...#.",
          "..##.#..",
          "...##...",
          "..#.##..",
          ".#...##.",
          "###..###"),
    "Q": (".#####..",
          "##...##.",
          "##...##.",
          "##...##.",
          "##.#.##.",
          "##..##..",
          ".####.##"),
}
GAP, SPACE = 1, 4  # columns between letters, and for a space

Glyph = List[List[bool]]
Rows = List[List[Optional[int]]]


def _ink(chunk: bytes) -> Glyph:
    _, _, rows = decode_frame(chunk, 0)
    return [[p is not None for p in r] for r in rows]


def _runs(ink: Glyph) -> List[Tuple[int, int]]:
    width = len(ink[0]) if ink else 0
    cols = [any(r[x] for r in ink) for x in range(width)]
    out, x = [], 0
    while x < width:
        if cols[x]:
            start = x
            while x < width and cols[x]:
                x += 1
            out.append((start, x))
        else:
            x += 1
    return out


def glyphs(resource: gff.Chunks) -> Dict[str, Glyph]:
    """Each letter's ink, HEIGHT rows."""
    out: Dict[str, Glyph] = {}
    for cid, text in LABELS.items():
        ink = _ink(resource[("ICON", cid)])
        letters = text.replace(" ", "")
        runs = _runs(ink)
        if len(runs) == len(letters):
            for (a, b), ch in zip(runs, letters):
                out.setdefault(ch, [r[a:b] for r in ink])
    for cid, a, b, ch in CUTS:
        ink = _ink(resource[("ICON", cid)])
        cut = [r[a:b] for r in ink]
        inked = [x for x in range(b - a) if any(r[x] for r in cut)]
        out.setdefault(ch, [r[inked[0]:inked[-1] + 1] for r in cut])
    for ch, art in DRAWN.items():
        out[ch] = [[c == "#" for c in line] for line in art]
    return out


def label(font: Dict[str, Glyph], text: str, pad: int, colour: int) -> Rows:
    """TEXT in the carved letters, PAD columns in, in COLOUR."""
    rows: Rows = [[None] * pad for _ in range(HEIGHT)]
    for i, ch in enumerate(text):
        if ch == " ":
            for r in rows:
                r.extend([None] * SPACE)
            continue
        if i and text[i - 1] != " ":
            for r in rows:
                r.extend([None] * GAP)
        g = font[ch]
        for y in range(HEIGHT):
            rows[y].extend(colour if on else None for on in g[y])
    return rows


def _colours(chunk: bytes) -> List[int]:
    """The ink's colour in each frame of a label."""
    count, = struct.unpack_from("<H", chunk, 4)
    out = []
    for f in range(count):
        _, _, rows = decode_frame(chunk, f)
        out.append(next(p for r in rows for p in r if p is not None))
    return out


def picture(font: Dict[str, Glyph], text: str, pad: int, colours: List[int]) -> bytes:
    from .savepages import encode_frames
    return encode_frames([label(font, text, pad, c) for c in colours])


def _encode(frames: List[Rows]) -> bytes:
    from .savepages import encode_frames
    return encode_frames(frames)


def _button(template: bytes, template_id: int, new_id: int) -> bytes:
    return template.replace(struct.pack("<I", template_id), struct.pack("<I", new_id))


def _window(template: bytes, wid: int, items: List[Tuple[int, int, int]]) -> bytes:
    """A window like TEMPLATE (its frame and place), its own id WID, with these buttons (id, x, y)."""
    head = bytearray(template[:ITEM_AT])
    struct.pack_into("<I", head, 8, wid)
    body = b"".join(bytes(4) + b"BUTN" + struct.pack("<IHH", cid, x, y) + bytes(ITEM_SIZE - 16)
                    for cid, x, y in items)
    out = bytearray(bytes(head) + body + template[ITEM_AT + ITEM_SIZE * struct.unpack_from("<H", template, WIND_COUNT)[0]:])
    struct.pack_into("<I", out, 4, len(out))
    struct.pack_into("<H", out, WIND_COUNT, len(items))
    return bytes(out)


def _items(window: bytes) -> List[Tuple[int, int, int]]:
    count, = struct.unpack_from("<H", window, WIND_COUNT)
    return [struct.unpack_from("<IHH", window, ITEM_AT + i * ITEM_SIZE + 8) for i in range(count)]


SHORT = {"long sword": "LNG SWORD", "short sword": "SHRT SWORD", "quarterstaff": "QTR STAFF",
         "staff sling": "STF SLING"}  # (rows the panel is too narrow for)


def page_text(kind: int) -> str:
    name = specialize.KINDS[kind]
    return SHORT.get(name, name.upper())


def chunks(resource: gff.Chunks, objects: Optional[gff.Chunks] = None) -> Dict[Tuple[str, int], bytes]:
    """For the Ledger's copy of RESOURCE.GFF: the weapon pages, the warriors' windows, and their
    rows' and buttons' pictures and buttons; and the level-up window (its weapons' pictures from
    OBJECTS, SEGOBJEX.GFF's chunks with the Ledger's own items)."""
    font = glyphs(resource)
    row_colours = _colours(resource[("ICON", ROW_TEMPLATE)])
    toggle_colours = _colours(resource[("ICON", TOGGLE_TEMPLATE)])
    row_button, toggle_button = resource[("BUTN", ROW_TEMPLATE)], resource[("BUTN", TOGGLE_TEMPLATE)]
    added: Dict[Tuple[str, int], bytes] = {}
    for kind in range(len(specialize.KINDS)):
        cid = ROW_FIRST + kind
        added[("ICON", cid)] = picture(font, page_text(kind), ROW_PAD, row_colours)
        added[("BUTN", cid)] = _button(row_button, ROW_TEMPLATE, cid)
    for cid, text in ((MORE, "MORE SPECS"), (BACK, "VIEW PSIONICS"), (VIEW, "WEAPON SPEC")):
        added[("ICON", cid)] = picture(font, text, 0, toggle_colours)
        added[("BUTN", cid)] = _button(toggle_button, TOGGLE_TEMPLATE, cid)
    spheres = resource[("WIND", SPHERES)]
    sphere_items = _items(spheres)  # (four rows, then the button)
    rows_at = [(x, y) for _, x, y in sphere_items[:4]]
    toggle_at = sphere_items[4][1:]
    for page, wid in enumerate(PAGES):
        items = [(ROW_FIRST + page * specialize.PAGE_SIZE + r, x, y) for r, (x, y) in enumerate(rows_at)]
        items.append((MORE if page < len(PAGES) - 1 else BACK, *toggle_at))
        added[("WIND", wid)] = _window(spheres, wid, items)
    added[("WIND", WARRIOR_SPHERES)] = _window(
        spheres, WARRIOR_SPHERES, [(VIEW if c == SPHERE_TOGGLE else c, x, y) for c, x, y in sphere_items])
    disciplines = resource[("WIND", DISCIPLINES)]
    added[("WIND", WARRIOR_DISCIPLINES)] = _window(
        disciplines, WARRIOR_DISCIPLINES, [(VIEW if c == DISCIPLINE_TOGGLE else c, x, y) for c, x, y in _items(disciplines)])
    added.update(picker(resource, objects or {}, row_button))
    return added


def _trim(rows: Rows) -> Rows:
    """ROWS without the clear rows and columns round them."""
    ys = [y for y, r in enumerate(rows) if any(p is not None for p in r)]
    xs = [x for x in range(len(rows[0])) if any(r[x] is not None for r in rows)] if rows else []
    if not ys or not xs:
        return [[None]]
    return [r[min(xs):max(xs) + 1] for r in rows[min(ys):max(ys) + 1]]


def _smaller(rows: Rows, size: int) -> Rows:
    """ROWS made SIZE pixels square, a pixel taken for each (the same step both ways, so that a
    diagonal stays unbroken)."""
    h, w = len(rows), len(rows[0])
    return [[rows[y * h // size][x * w // size] for x in range(size)] for y in range(size)]


def weapon_picture(objects: gff.Chunks, kind: int) -> Rows:
    """Kind KIND's weapon, as the game draws it in the inventory, trimmed (none if missing)."""
    from .icons import OJFF_ICON, decode
    ojff = objects.get(("OJFF", PICTURES[kind]))
    if not ojff:
        return [[None]]
    bmp = objects.get(("BMP ", struct.unpack_from("<H", ojff, OJFF_ICON)[0]))
    if not bmp:
        return [[None]]
    rows = _trim(decode(bmp))
    if kind == POLEARM and max(len(rows), len(rows[0])) > PICK_SLOT - 4:
        rows = _smaller(rows, POLEARM_SIZE)
    return rows


def slot(weapon: Rows, state: int) -> Rows:
    """A slot with WEAPON in its middle: STATE 0 as it is, 1 lit, 2 out of use (the frames of a
    button's picture, in the game's order)."""
    n = PICK_SLOT
    rows: Rows = [[SLOT_FACE] * n for _ in range(n)]
    for i in range(n):
        for (x, y) in ((i, 0), (0, i)):
            rows[y][x] = SLOT_DARK
        for (x, y) in ((i, n - 1), (n - 1, i)):
            rows[y][x] = SLOT_LIGHT
    if state == 1:
        for i in range(n):
            rows[0][i] = rows[n - 1][i] = rows[i][0] = rows[i][n - 1] = SLOT_LIT
    h, w = len(weapon), len(weapon[0])
    top, left = (n - h) // 2, (n - w) // 2
    for y, r in enumerate(weapon):
        for x, p in enumerate(r):
            if p is not None and 0 <= top + y < n and 0 <= left + x < n:
                rows[top + y][left + x] = SLOT_OUT if state == 2 else p
    return rows


def background(resource: gff.Chunks) -> Rows:
    """The picker's marble, the psionicists' carried on to its size (inside their bevel, each
    band of it shifted so the copies don't line up), in the same bevel."""
    _, _, marble = decode_frame(resource[("BMP ", PSIONIC_BACKGROUND)])
    marble = [r[3:-3] for r in marble[3:-3]]
    mh, mw = len(marble), len(marble[0])
    w, h = PICK_WIDTH, PICK_HEIGHT
    rows: Rows = [[marble[(y + 37 * (x // mw)) % mh][(x + 53 * (y // mh)) % mw] for x in range(w)]
                  for y in range(h)]
    for x in range(w):
        rows[0][x] = rows[1][x] = MARBLE_LIGHT
        rows[h - 1][x] = rows[h - 2][x] = MARBLE_DARK
    for y in range(h):
        rows[y][0] = rows[y][1] = MARBLE_LIGHT
        rows[y][w - 1] = rows[y][w - 2] = MARBLE_DARK
    return rows


def picker(resource: gff.Chunks, objects: gff.Chunks, row_button: bytes) -> Dict[Tuple[str, int], bytes]:
    """The level-up window (PICKER): its marble, a slot for each kind, picks left and EXIT."""
    added: Dict[Tuple[str, int], bytes] = {}
    psionic = resource[("WIND", PSIONIC_PICKER)]
    keep = {c: (x, y) for c, x, y in _items(psionic) if c in (PICK_COUNT_BUTTON, PICK_EXIT)}
    left = (PICK_WIDTH - PICK_COLUMNS * PICK_PITCH + (PICK_PITCH - PICK_SLOT)) // 2
    items = []
    for kind in range(len(specialize.KINDS)):
        cid = PICK_FIRST + kind
        weapon = weapon_picture(objects, kind)
        added[("ICON", cid)] = _encode([slot(weapon, state) for state in range(3)])
        button = bytearray(_button(row_button, ROW_TEMPLATE, cid))
        struct.pack_into("<HH", button, BUTN_SIZE, PICK_SLOT, PICK_SLOT)
        added[("BUTN", cid)] = bytes(button)
        items.append((cid, left + PICK_PITCH * (kind % PICK_COLUMNS), PICK_TOP + PICK_PITCH * (kind // PICK_COLUMNS)))
    exit_x, exit_y = keep[PICK_EXIT]
    dx, dy = PICK_WIDTH - 159, PICK_HEIGHT - 113  # (the psionicists' window's size)
    exit_x, exit_y = exit_x + dx, exit_y + dy  # (its corner, as theirs; the picks left just before)
    items += [(PICK_COUNT_BUTTON, exit_x - PICK_COUNT_GAP, exit_y), (PICK_EXIT, exit_x, exit_y)]
    window = bytearray(_window(psionic, PICKER, items))
    struct.pack_into("<HHH", window, WIND_WIDTH, PICK_WIDTH, PICK_HEIGHT, PICK_BACKGROUND)
    added[("WIND", PICKER)] = bytes(window)
    added[("BMP ", PICK_BACKGROUND)] = _encode([background(resource)])
    return added
