"""Whirlwind's picture on the ground: a funnel of dust, drawn here (nothing from the game but its
palette), for the Loader's copy of SEGOBJEX.GFF.

The game draws its map at an angle: a circle on the ground is twice as wide as it is deep (a
figure's selection ring), while figures stand upright at their full height. So the funnel is a
stack of such ground ellipses, wide at the top and narrowing to a foot on the sand: the swirl's
bands wrap around its front, its back half sparse and darker (a hollow funnel of dust you can see
into), a soft swirl at its mouth, and a ring of dust kicked up on the ground around it, at the
edge of the spell's area (FOOT). FRAMES of it turn the bands a quarter round each.

Its colours are a ramp of greyish browns (dust, against the orange sand), each the nearest of
the game's colours that no region changes, the game doesn't cycle and that isn't bright
(wotrart.stable_colours).
OBJECT and PICTURE: its object (a copy of Sand Storm's, 8403, its picture and its anchor, the
funnel's foot, changed) and picture numbers in the copy; DSCLOG's NS_SETUP puts the object in
Whirlwind's ground entry (AREA_NEW) once the game has the copy (NS_OBJECTS)."""

import colorsys
import math
import random
import struct
from typing import Dict, List, Optional, Sequence, Tuple

from . import gff, icons

OBJECT, PICTURE = 8433, 2652
SAND_STORM = 8403  # (the object it is a copy of)
FRAMES = 4
GROUND = 0.5  # a ground circle's depth for its width, as the game draws it
HEIGHT, TOP, BOTTOM = 76, 27, 4  # the funnel's height, its mouth's and its foot's half widths
FOOT = (36, 18)  # the dust ring's half width and half depth on the ground: the spell's area
SEED = 5
RAMP = ((58, 50, 46), (84, 74, 66), (110, 98, 88), (136, 124, 112), (160, 148, 134), (186, 176, 162),
        (212, 204, 192))
MOST_SATURATED = 0.35
CYCLED = set(range(240, 256)) | set(icons.WATER)  # (colours the game turns: fire's, water's)
ANCHOR = 2  # (an object's two words, x and y: its picture's point that stands on its place)


def ramp(stable: Sequence[Tuple[int, Tuple[int, int, int]]]) -> List[int]:
    """RAMP as the nearest of STABLE's colours (palette number, colour) that aren't bright."""
    dull = [(i, rgb) for i, rgb in stable if i not in CYCLED
            and colorsys.rgb_to_hsv(*[v / 255 for v in rgb])[1] < MOST_SATURATED]
    return [min(dull, key=lambda e: sum((a - b) ** 2 for a, b in zip(e[1], want)))[0] for want in RAMP]


def frame(colours: Sequence[int], turn: int) -> Tuple[List[List[Optional[int]]], Tuple[int, int]]:
    """Frame TURN (0 to FRAMES - 1) as rows of COLOURS' numbers (None clear), and its anchor."""
    rnd = random.Random(SEED * 13 + turn)
    width = max(TOP * 2 + 10, FOOT[0] * 2 + 6)
    height = HEIGHT + int(TOP * GROUND) + FOOT[1] + 6
    base = height - FOOT[1] - 3
    points = []
    for _ in range(260):  # the dust kicked up on the ground, at the area's edge
        a = rnd.random() * 2 * math.pi
        out = 0.75 + 0.25 * rnd.random()
        x, y = width / 2 + math.cos(a) * FOOT[0] * out, base + math.sin(a) * FOOT[1] * out
        if rnd.random() < 0.55 + 0.35 * math.sin(a * 3 + turn * math.pi / 2):
            points.append((y - 2000, x, y, colours[rnd.choice((0, 1, 1, 2, 2, 3))]))
    for up in range(HEIGHT):  # the funnel, a ground ellipse at each height
        t = up / (HEIGHT - 1)
        r = BOTTOM + (TOP - BOTTOM) * t ** 1.7
        cx, cy = width / 2 + math.sin(t * 2.4 + 0.5) * 2.5 * (1 - t), base - up
        n = int(2 * math.pi * r * 1.7) + 8
        for j in range(n):
            a = 2 * math.pi * j / n
            x, y = cx + r * math.cos(a), cy + r * GROUND * math.sin(a)
            front = math.sin(a) > 0
            band = math.sin(a * 2 - up * 0.2 + turn * math.pi / 2)
            if rnd.random() > (0.5 if front else 0.16) + 0.3 * (band > 0.35) + 0.15 * abs(math.cos(a)) ** 3:
                continue
            lit = (0.5 + 0.35 * (band * 0.5 + 0.5) - 0.125 * math.cos(a)) * (1.0 if front else 0.75) * (0.8 + 0.25 * t)
            points.append((y if front else y - 1000, x, y, colours[max(0, min(6, int(lit * 6.99)))]))
    top = base - (HEIGHT - 1)
    for _ in range(int(TOP * TOP * 1.1)):  # the mouth: a soft swirl
        a, out = rnd.random() * 2 * math.pi, math.sqrt(rnd.random()) * TOP * 0.82
        swirl = math.sin(a * 2 + out * 0.35 - turn * math.pi / 2)
        if rnd.random() < 0.45 + 0.3 * swirl:
            x, y = width / 2 + math.cos(a) * out, top + math.sin(a) * out * GROUND
            points.append((y - 1500, x, y, colours[1 + int(out / TOP * 3 + (swirl > 0))]))
    rows: List[List[Optional[int]]] = [[None] * width for _ in range(height)]
    for _, x, y, c in sorted(points):
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < width and 0 <= yi < height:
            rows[yi][xi] = c
    return rows, (width // 2, base)


def encode_frames(frames: Sequence[List[List[Optional[int]]]]) -> bytes:
    """A picture chunk of FRAMES (icons.encode's packing, a frame's offset each)."""
    bodies = [icons.encode(rows)[10:] for rows in frames]
    head = 4 + 2 + 4 * len(bodies)
    offsets, at = [], head
    for body in bodies:
        offsets.append(at)
        at += len(body)
    return struct.pack("<IH", at, len(bodies)) + struct.pack(f"<{len(bodies)}I", *offsets) + b"".join(bodies)


def chunks(sl_chunks: gff.Chunks, stable) -> Dict[Tuple[str, int], bytes]:
    """OBJECT and PICTURE for the copy (SL_CHUNKS the game's; STABLE its stable colours)."""
    colours = ramp(stable)
    made = [frame(colours, turn) for turn in range(FRAMES)]
    record = bytearray(sl_chunks[("OJFF", SAND_STORM)])
    struct.pack_into("<H", record, icons.OJFF_ICON, PICTURE)
    struct.pack_into("<hh", record, ANCHOR, *made[0][1])
    return {("OJFF", OBJECT): bytes(record), ("BMP ", PICTURE): encode_frames([rows for rows, _ in made])}
