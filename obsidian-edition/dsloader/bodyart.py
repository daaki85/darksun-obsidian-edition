"""The dead Tohr-kreen champion's picture (champions.BODY): a Tohr-kreen fallen on its side.

Made from the game's own pictures, in the palette they share: the Tohr-kreen's (its object 292's
picture), a frame of it turned on its side, squashed to lie on the ground as the game's Dead Body
does (object 1101: about half as tall as it is long) and darkened, over the pool of blood from
under the Dead Body's own figure.
"""

import struct
from typing import List, Optional, Tuple

from . import art

Rows = List[List[Optional[int]]]
TOHR_KREEN, DEAD_BODY = 292, 1101  # (the objects whose pictures are used)
FRAME = 8  # the Tohr-kreen's frame laid down (one standing side on, its legs spread)
SQUASH = 0.75  # the height it keeps, lying
DARKEN = 0.7  # (a dead thing's colours)
OJFF_PICTURE = 0x0C


def _picture_of(chunks, obj: int) -> bytes:
    pid, = struct.unpack_from("<H", chunks[("OJFF", obj)], OJFF_PICTURE)
    return chunks[("BMP ", pid)]


def _palette(chunks) -> Optional[List[Tuple[int, int, int]]]:
    """The game's palette, as icons.write_objects has set it (spritegear's), else None (the
    picture undarkened, the Dead Body's whole figure under it)."""
    from . import spritegear
    return list(spritegear._RGB) if len(spritegear._RGB) >= 256 else None


def _nearest(colour, palette, avoid=(0,)) -> int:
    r, g, b = colour
    best, at = None, 0
    for i, (pr, pg, pb) in enumerate(palette):
        if i in avoid:
            continue
        d = (pr - r) ** 2 + (pg - g) ** 2 + (pb - b) ** 2
        if best is None or d < best:
            best, at = d, i
    return at


def _lying(rows: Rows) -> Rows:
    """ROWS turned a quarter (the head to the left) and squashed to SQUASH of their height."""
    h, w = len(rows), len(rows[0]) if rows else 0
    turned = [[rows[h - 1 - y][x] for y in range(h)] for x in range(w)]  # (w rows of h)
    tall = len(turned)
    keep = max(1, int(round(tall * SQUASH)))
    return [turned[min(tall - 1, int(y / SQUASH))] for y in range(keep)]


def _trim(rows: Rows) -> Rows:
    used = [y for y, r in enumerate(rows) if any(v is not None for v in r)]
    if not used:
        return rows
    rows = rows[used[0]:used[-1] + 1]
    cols = [x for x in range(len(rows[0])) if any(r[x] is not None for r in rows)]
    return [r[cols[0]:cols[-1] + 1] for r in rows]


def _is_blade(colour) -> bool:
    """The gythka's bone blades and haft (pale, greyish: a carapace is brown, its eyes green): left
    out, as the weapon is in the body to be taken."""
    r, g, b = colour
    return max(r, g, b) - min(r, g, b) < 40 and max(r, g, b) > 90


def _is_blood(colour) -> bool:
    r, g, b = colour
    return r > 110 and g < 70 and b < 70 and r > 3 * g


def rows(chunks, palette=None) -> Rows:
    """The picture's pixels (palette indexes, None clear)."""
    palette = palette or _palette(chunks)
    kreen_picture = _picture_of(chunks, TOHR_KREEN)
    frames, = struct.unpack_from("<H", kreen_picture, 4)
    _, _, kreen = art.decode_frame(kreen_picture, FRAME if FRAME < frames else 0)
    _, _, body = art.decode_frame(_picture_of(chunks, DEAD_BODY), 0)
    if palette:
        kreen = [[None if v is not None and _is_blade(palette[v]) else v for v in r] for r in kreen]
    lying = _trim(_lying(kreen))
    if palette:
        dark = {}
        for r in lying:
            for x, v in enumerate(r):
                if v is not None and v not in dark:
                    cr, cg, cb = palette[v]
                    dark[v] = _nearest((int(cr * DARKEN), int(cg * DARKEN), int(cb * DARKEN)), palette)
        lying = [[dark.get(v) if v is not None else None for v in r] for r in lying]
    h = max(len(lying), len(body))
    w = max(len(lying[0]), len(body[0]))
    out: Rows = [[None] * w for _ in range(h)]
    # the blood first, centred under it; the body over it
    by, bx = h - len(body), (w - len(body[0])) // 2
    for y, r in enumerate(body):
        for x, v in enumerate(r):
            if v is not None and (palette is None or _is_blood(palette[v])):
                out[by + y][bx + x] = v
    ly, lx = h - len(lying), (w - len(lying[0])) // 2
    for y, r in enumerate(lying):
        for x, v in enumerate(r):
            if v is not None:
                out[ly + y][lx + x] = v
    return out


def picture(chunks) -> bytes:
    """The picture's chunk (one frame, as the game's pictures are)."""
    from . import sprites
    return sprites.encode_frames([rows(chunks)])
