"""Wake of the Ravager's talk portraits at Shattered Lands' size (the owner's ask, 2026-11-27).

Shattered Lands shows a speaker as a 32 by 32 face in a 48 by 47 stone frame, the frame at (8, 6) of its
talk window (WIND 3007: the frame BUTN 2090 at (8, 6), the face drawn at (16, 13) by 7DEDFh, the text box
EBOX 4002 at (58, 6), the window 318 by 58). The sequel's faces are 72 by 72 with their frame drawn in
(GPLDATA.GFF's PORT chunks, the face 56 by 58 at (8, 7)), drawn at (0, 0) by 88E67h, so its talk window
(WIND 12500) is 72 high and its text box (EBOX 12400) starts at x 75; with no speaker in a fight (the XP
at its end) an empty frame is drawn there (BMP 12000's frame 1, 73 by 73, a grey wash in it).

The Loader's copies make them Shattered Lands':
  * GPLDAT2.GFF: each PORT 48 by 46, the frame cut down from the face's own (its corners kept, the middle
    of each side left out: `frame`) round the face made 32 by 32 (`smaller`) at (8, 7);
  * RESOURC2.GFF: BMP 12000 the same frame, empty (frame 0, under the shop's face) and round its grey wash
    made 32 by 32 (frame 1), and WIND 12500 58 high with its text box at x 58 (Shattered Lands' WIND 3007);
  * DSUNLOG2.EXE: 88E67h draws the face (or the empty frame) at (8, 6) (PATCHES).
So a talk box is Shattered Lands' to the pixel: the frame at (8, 6), the face at (16, 13), the text from x
58, the window 58 high. The shop screen's corner (the same routine) has the smaller face and frame in the
middle of the big one's place.

The frame is the sequel's own art (Shattered Lands' drawing enlarged), so Shattered Lands' interface
(ravui) on or off it looks the same. SKIP ("small_portraits", RAV_SKIP's control) leaves all of it out."""

import struct
from typing import List, Optional, Sequence, Tuple

from . import art, gff
from .gamepatch import Patch

SKIP = "small_portraits"

FACE = 32  # (Shattered Lands' face, square)
LEFT, TOP, RIGHT, BOTTOM = 8, 7, 8, 7  # (the frame's sides round the face, in the sequel's PORT as here)
WIDTH, HEIGHT = LEFT + FACE + RIGHT, TOP + FACE + BOTTOM  # (48 by 46)
AT_X, AT_Y = 8, 6  # (where the talk window draws it: Shattered Lands' frame's place)

TALK_WINDOW = 12500  # (the sequel's talk window: Shattered Lands' WIND 3007)
TALK_HEIGHT = 58  # (WIND 3007's)
TEXT_X = 58  # (EBOX 4002's place in WIND 3007)
TEXT_BOX = 12400
WIND_HEIGHT = 0xC0  # (a window's height, a word, in its head)
WIND_COUNT, ITEM_AT, ITEM_SIZE = 243, 0x105, 30  # (weaponpages': its places, 30 bytes each)
EMPTY_FRAME = ("BMP ", 12000)  # (two frames: 0 the frame alone, 1 with a grey wash in it)
PALETTE = ("PAL ", 1000)

# 88E67h (Shattered Lands' 7DEDFh) draws the face at (di, [bp-2]): "xor di,di / mov word [bp-2],0" its place,
# 0EEh and 6 on the shop screen (while es:[3Ch] of selector 3A0h is set, 88EBFh), and the empty frame at (0, 0)
# by pushes of its own. Made: the local word made 0 as it is made ("sub sp,2" a "push 0"), the place (8, 6)
# (its low byte), the empty frame through the face's pushes (its frame 1 kept); in the shop the face (SHOP_X,
# SHOP_Y), the middle of the sequel's 73 by 73 place, and the frame the shop draws first (90957h, BMP 12000
# at (0EEh, 6)) there too.
SHOP_X, SHOP_Y = 0xEE + (73 - WIDTH) // 2, 6 + (73 - HEIGHT) // 2  # (250, 19)
PATCHES: Tuple[Patch, ...] = (
    Patch("small_portraits_local", 0x88E6A, bytes.fromhex("83ec02"), bytes.fromhex("6a0090")),
    Patch("small_portraits_at", 0x88E72, bytes.fromhex("33ffc746fe0000"), bytes((0xBF, AT_X, 0, 0xC6, 0x46, 0xFE, AT_Y))),
    Patch("small_portraits_empty", 0x88ED7, bytes.fromhex("666a00"), bytes.fromhex("eb0c90")),  # (to 88EE5h)
    Patch("small_portraits_shop", 0x88EBF, bytes.fromhex("bfee00c746fe0600"),
          bytes((0xBF, SHOP_X, 0, 0xC7, 0x46, 0xFE, SHOP_Y, 0))),
    Patch("small_portraits_shop_frame", 0x90957, bytes.fromhex("666a0666680100ee00"),
          bytes((0x66, 0x6A, SHOP_Y, 0x66, 0x68, 1, 0, SHOP_X, 0))),
)
PATCH_NAMES = frozenset(p.name for p in PATCHES)

Rows = List[List[int]]


def _rows(chunk: bytes) -> Rows:
    from . import wotrart
    return wotrart.decode_plnr(chunk)


def _hole(rows: Rows) -> Tuple[int, int, int, int]:
    """The face's square in a sequel PORT's ROWS: (x, y, side), the frame's sides cut off and the larger
    way trimmed even on both ends."""
    h, w = len(rows), len(rows[0])
    fw, fh = w - LEFT - RIGHT, h - TOP - BOTTOM
    side = min(fw, fh)
    return LEFT + (fw - side) // 2, TOP + (fh - side) // 2, side, side


def frame(rows: Rows) -> Rows:
    """The frame of a sequel PORT's ROWS cut down to WIDTH by HEIGHT: its left half and top half kept, the
    rest from the right and bottom ends; the face's place 0 (clear)."""
    h, w = len(rows), len(rows[0])
    half_w, half_h = WIDTH // 2, HEIGHT // 2
    out = []
    for y in range(HEIGHT):
        sy = y if y < half_h else y + h - HEIGHT
        out.append([rows[sy][x if x < half_w else x + w - WIDTH] for x in range(WIDTH)])
    for y in range(TOP, TOP + FACE):
        out[y][LEFT:LEFT + FACE] = [0] * FACE
    return out


def smaller(rows: Rows, x0: int, y0: int, side: int, palette: Optional[Sequence[Tuple[int, int, int]]]) -> Rows:
    """ROWS' square (X0, Y0, SIDE) made FACE by FACE: each pixel the one of its patch nearest the patch's mean
    colour in PALETTE (the patch's middle one without it), so the face keeps its own colours."""
    out = []
    for y in range(FACE):
        ya, yb = y0 + y * side // FACE, y0 + max((y + 1) * side // FACE, y * side // FACE + 1)
        row = []
        for x in range(FACE):
            xa, xb = x0 + x * side // FACE, x0 + max((x + 1) * side // FACE, x * side // FACE + 1)
            patch = [rows[py][px] for py in range(ya, yb) for px in range(xa, xb)]
            if palette is None or len(patch) == 1:
                row.append(patch[len(patch) // 2])
                continue
            cols = [palette[p] for p in patch]
            mean = [sum(c[i] for c in cols) / len(cols) for i in range(3)]
            row.append(min(patch, key=lambda p: sum((a - b) ** 2 for a, b in zip(palette[p], mean))))
        out.append(row)
    return out


def portrait(chunk: bytes, border: Rows, palette=None) -> bytes:
    """A sequel PORT chunk made Shattered Lands' size: BORDER (`frame`) round its face made FACE square."""
    rows = _rows(chunk)
    x0, y0, side, _ = _hole(rows)
    face = smaller(rows, x0, y0, side, palette)
    out = [list(r) for r in border]
    for y in range(FACE):
        out[TOP + y][LEFT:LEFT + FACE] = face[y]
    return art.plnr_frames([out])


def _sized(chunk: bytes) -> Tuple[int, int]:
    offset, = struct.unpack_from("<I", chunk, 6)
    return struct.unpack_from("<HH", chunk, offset)


def script_chunks(scripts: gff.Chunks, palette=None) -> gff.Chunks:
    """GPLDATA.GFF's PORT chunks made smaller (`portrait`), the frame the first face's (PORT 1, else the
    first); none if the faces aren't the sequel's (72 or so square) or one isn't in the PLNR form."""
    faces = sorted(k for k in scripts if k[0] == "PORT")
    if not faces:
        return {}
    first = ("PORT", 1) if ("PORT", 1) in faces else faces[0]
    try:
        border = frame(_rows(scripts[first]))
        out = {}
        for key in faces:
            w, h = _sized(scripts[key])
            if w <= WIDTH or h <= HEIGHT:
                return {}  # (already small: Shattered Lands' or a copy made before)
            out[key] = portrait(scripts[key], border, palette)
        return out
    except (ValueError, IndexError, struct.error):
        return {}


def _frame_rows(chunk: bytes, index: int) -> Rows:
    """Frame INDEX of a PLNR picture chunk (wotrart.decode_plnr reads the first)."""
    offset, = struct.unpack_from("<I", chunk, 6 + 4 * index)
    return _rows(chunk[:6] + struct.pack("<I", offset) + chunk[10:])


def empty_frame(resource: gff.Chunks, scripts: gff.Chunks, palette=None) -> Optional[bytes]:
    """BMP 12000's chunk made smaller: its frame 0 the faces' frame (`frame` of PORT 1) with nothing in it
    (the shop draws it under the face), its frame 1 the same frame round the game's frame 1's grey wash
    made FACE square (what the talk window shows for no speaker: the end of a fight's XP)."""
    key = ("PORT", 1)
    if key not in scripts or EMPTY_FRAME not in resource:
        return None
    try:
        border = frame(_rows(scripts[key]))
        game = resource[EMPTY_FRAME]
        if struct.unpack_from("<H", game, 4)[0] < 2:
            return None
        clear, washed = _frame_rows(game, 0), _frame_rows(game, 1)
        inside = [(x, y) for y, r in enumerate(clear) for x, p in enumerate(r) if p == 0
                  and 4 < x < len(r) - 4 and 4 < y < len(clear) - 4]
        x0, y0 = min(x for x, _ in inside), min(y for _, y in inside)
        side = min(max(x for x, _ in inside) - x0, max(y for _, y in inside) - y0) + 1
        wash = smaller(washed, x0, y0, side, palette)
        full = [list(r) for r in border]
        for y in range(FACE):
            full[TOP + y][LEFT:LEFT + FACE] = wash[y]
        return art.plnr_frames([border, full])
    except (ValueError, IndexError, struct.error):
        return None


def talk_window(window: bytes) -> bytes:
    """WIND 12500 as Shattered Lands' WIND 3007: TALK_HEIGHT high, its text box (EBOX TEXT_BOX) at TEXT_X."""
    out = bytearray(window)
    struct.pack_into("<H", out, WIND_HEIGHT, TALK_HEIGHT)
    count, = struct.unpack_from("<H", out, WIND_COUNT)
    for i in range(count):
        at = ITEM_AT + i * ITEM_SIZE
        if out[at + 4:at + 8] == b"EBOX" and struct.unpack_from("<I", out, at + 8)[0] == TEXT_BOX:
            struct.pack_into("<H", out, at + 12, TEXT_X)
    return bytes(out)


def resource_chunks(resource: gff.Chunks, scripts: Optional[gff.Chunks]) -> gff.Chunks:
    """RESOURCE.GFF's chunks: the talk window (`talk_window`) and the empty frame (`empty_frame`, its frame
    from SCRIPTS, the game's GPLDATA.GFF); none if either is missing."""
    key = ("WIND", TALK_WINDOW)
    if key not in resource or not scripts or EMPTY_FRAME not in resource:
        return {}
    palette = art.palette_colours(resource[PALETTE]) if PALETTE in resource else None
    empty = empty_frame(resource, scripts, palette)
    if empty is None:
        return {}
    window = resource[key]
    if struct.unpack_from("<H", window, WIND_HEIGHT)[0] != 72:
        return {}  # (not the GOG release's window)
    return {key: talk_window(window), EMPTY_FRAME: empty}
