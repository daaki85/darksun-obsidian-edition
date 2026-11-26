"""Paint the exposed anatomical planes on the widened male half-elf."""

# Spaces preserve the underpainting. The short strokes follow the near rib,
# shoulder blade, hip and knee. Light falls from the upper left on the map.
SKIN = dict(zip("abcdefghi", (134, 133, 132, 131, 130, 144, 145, 146, 147)))
CHEST = {
    "front": (" gh        ", "  hig   f", "   feecd", "     bd", "    de"),
    "back":  (" ghg   f", "  hig ef", "   gedb", "    ecb", "    dc"),
    "side":  (" gf ", "  hg", "  ed", " de", "  c"),
    "reach": ("  gf", " hge", " ed", " dc"),
    "twist": ("  g", " gh", " ef", " db"),
}
HIP = {
    "front": ("    de", "  ghe  c", "  hgf ec", "  fe bd", "  e"),
    "back":  ("    be", "  fgde", " ghf ce", " ge   f", " e"),
    "side":  (" de", " ghf", " hge", "  eb"),
}
KNEE = {
    "front": (" g", " h", "ed", " c"),
    "back":  (" f", "ed", " d", " g"),
    "side":  (" g", " hg", " ec", " d"),
}
# Chest, hip and the near knee, traced independently in the widened native
# cels. Some strikes leave only a narrow wedge of the ribs behind the elbow.
# The fallen cel is painted upright, then returned to its native orientation.
POSES = (
    ("front", 3, 7, "front", 4, 12, 3, 18),   # front idle
    ("back", 5, 7, "back", 4, 13, 11, 19),    # rear idle
    ("side", 1, 7, "side", 2, 13, 1, 18),    # profile idle
    ("front", 2, 7, "front", 3, 12, 2, 18),
    ("front", 3, 7, "front", 4, 11, 8, 18),
    ("front", 3, 7, "front", 4, 12, 9, 18),
    ("front", 2, 7, "front", 3, 11, 2, 17),
    ("back", 2, 7, "back", 2, 13, 2, 18),
    ("back", 0, 7, "back", 0, 13, 0, 18),
    ("back", 2, 7, "back", 2, 13, 8, 19),
    ("back", 3, 7, "back", 3, 13, 8, 19),
    ("side", 0, 7, "side", 2, 13, 2, 18),
    ("side", 5, 7, "side", 4, 12, 9, 17),
    ("side", 3, 6, "side", 3, 15, 4, 19),
    ("side", 4, 7, "side", 4, 12, 3, 17),
    ("reach", 5, 15, "side", 4, 21, 2, 26),   # front strikes
    ("reach", 9, 8, "front", 7, 9, 6, 13),
    ("twist", 13, 8, "side", 12, 10, 11, 13),
    ("twist", 2, 10, "back", 1, 16, 7, 21),   # rear strikes
    ("back", 4, 16, "back", 4, 21, 11, 26),
    ("twist", 17, 7, "back", 12, 12, 20, 17),
    ("reach", 13, 14, "side", 13, 18, 13, 24),  # profile strikes
    ("reach", 6, 9, "side", 4, 13, 2, 17),
    ("reach", 5, 6, "side", 3, 10, 1, 14),
    ("twist", 4, 7, "side", 4, 12, 3, 18),    # bow, recoil and fall
    ("twist", 3, 10, "back", 3, 16, 8, 21),
    ("reach", 6, 10, "side", 6, 15, 6, 21),
    ("front", 3, 7, "front", 4, 12, 3, 18),
    ("back", 5, 7, "back", 4, 13, 10, 19),
)


def paint(pose, body, pad, source, back, protected, original_skin):
    chest, cx, cy, hip, hx, hy, kx, ky = POSES[pose]
    changes = []
    for x0, y0, strokes in ((cx, cy, CHEST[chest]), (hx, hy, HIP[hip]), (kx, ky, KNEE[hip])):
        for dy, strip in enumerate(strokes):
            y = y0 + dy
            if pose == 28:
                y = len(source) - 1 - y
            for dx, ink in enumerate(strip):
                if ink == " ":
                    continue
                x = x0 + dx
                sx = back(x, y)
                if not (0 <= y < len(source) and 0 <= sx < len(source[y])):
                    continue
                if (sx, y) in protected or source[y][sx] in original_skin:
                    continue
                old = body[y+pad][x+pad]
                if old in SKIN.values() and old != SKIN[ink]:
                    changes.append((x+pad, y+pad, old, SKIN[ink]))
    return changes
