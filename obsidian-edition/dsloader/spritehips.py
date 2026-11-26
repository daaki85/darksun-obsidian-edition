"""Suspension points for weapons worn at the waist, in native walking-picture coordinates."""

# Each cel gives (belt row, screen-left loop, screen-right loop). In profile the
# latter two entries are the near and far loops, and the far rim lies one row
# higher. These belong to the pelvis, even when the tunic, hand or cloak covers
# it. Order: three standing poses, then four front, four rear, four side steps.
_DWARF = (
    (12, 7, 12), (12, 7, 11), (12, 4, 5),
    (12, 7, 11), (11, 7, 11), (11, 7, 11), (11, 8, 12),
    (12, 5, 9), (12, 4, 8), (12, 5, 9), (12, 5, 9),
    (11, 3, 4), (12, 7, 8), (12, 5, 6), (12, 7, 8),
)

_LOOPS = {
    2095: (  # human man
        (14, 6, 13), (14, 8, 14), (15, 3, 5),
        (13, 5, 11), (13, 5, 12), (13, 6, 12), (13, 6, 12),
        (14, 4, 9), (15, 4, 10), (14, 5, 11), (15, 6, 11),
        (15, 4, 6), (15, 6, 8), (14, 4, 5), (15, 6, 8),
    ),
    2099: (  # human woman
        (14, 5, 10), (14, 8, 12), (14, 3, 5),
        (14, 5, 9), (13, 7, 11), (13, 7, 11), (13, 6, 10),
        (14, 7, 11), (14, 8, 12), (14, 9, 13), (14, 8, 12),
        (13, 6, 7), (14, 9, 11), (15, 11, 12), (14, 8, 10),
    ),
    2055: _DWARF,
    2053: _DWARF,
    2061: (  # elf man
        (15, 5, 11), (15, 5, 11), (15, 3, 4),
        (15, 4, 9), (14, 5, 9), (14, 6, 10), (14, 4, 9),
        (15, 4, 8), (15, 2, 6), (15, 4, 8), (15, 5, 9),
        (14, 3, 4), (15, 7, 8), (15, 6, 7), (15, 5, 7),
    ),
    2059: (  # elf woman
        (15, 5, 9), (15, 6, 11), (14, 3, 5),
        (15, 4, 8), (14, 5, 9), (14, 5, 9), (14, 4, 8),
        (15, 4, 8), (15, 2, 6), (15, 4, 8), (16, 5, 9),
        (14, 5, 6), (14, 9, 10), (15, 6, 7), (14, 5, 7),
    ),
    2072: (  # half-giant man
        (21, 11, 20), (21, 11, 20), (21, 6, 9),
        (20, 9, 18), (21, 9, 18), (21, 8, 18), (20, 8, 16),
        (21, 7, 15), (21, 6, 14), (21, 8, 16), (21, 9, 16),
        (22, 6, 8), (21, 9, 12), (22, 6, 8), (21, 9, 12),
    ),
    2074: (  # half-giant woman
        (22, 10, 19), (21, 11, 20), (22, 6, 9),
        (21, 9, 18), (22, 9, 18), (22, 8, 18), (21, 8, 16),
        (21, 6, 14), (21, 6, 14), (21, 8, 16), (21, 9, 16),
        (23, 6, 8), (22, 9, 12), (23, 6, 8), (22, 9, 12),
    ),
    2068: (  # halfling man
        (11, 8, 12), (11, 9, 12), (11, 3, 4),
        (11, 7, 11), (10, 7, 11), (11, 7, 11), (10, 8, 12),
        (11, 4, 8), (11, 4, 8), (11, 5, 9), (11, 5, 8),
        (10, 3, 4), (11, 8, 9), (11, 4, 5), (11, 6, 8),
    ),
    2070: (  # halfling woman
        (12, 7, 11), (12, 9, 12), (11, 5, 6),
        (12, 8, 12), (11, 7, 11), (12, 7, 11), (11, 8, 12),
        (12, 5, 8), (12, 4, 8), (12, 5, 9), (12, 5, 8),
        (10, 5, 6), (11, 7, 8), (11, 4, 5), (11, 6, 7),
    ),
    2093: (  # Mul
        (14, 8, 13), (14, 8, 13), (15, 3, 5),
        (14, 6, 12), (14, 6, 11), (13, 7, 12), (14, 6, 12),
        (14, 5, 9), (14, 5, 9), (14, 6, 10), (14, 6, 10),
        (15, 4, 6), (15, 7, 9), (15, 4, 6), (15, 6, 8),
    ),
    2097: (  # Thri-kreen: the narrow joint between thorax and abdomen
        (16, 11, 17), (19, 8, 12), (19, 17, 19),
        (15, 12, 17), (16, 12, 17), (16, 11, 17), (14, 12, 17),
        (19, 8, 11), (20, 9, 13), (19, 8, 12), (18, 8, 12),
        (17, 16, 18), (19, 15, 17), (18, 16, 18), (15, 17, 19),
    ),
}


def anchor(model, frame, hand, own=None):
    """Return the native right/left hip of a walking cel, including a half-elf's row shift."""
    loops = _LOOPS.get(model)
    if loops is None or not 0 <= frame < len(loops) or hand not in ("left", "right"):
        return None
    y, a, b = loops[frame]
    if frame == 2 or frame >= 11:
        x, y = (a, y) if hand == "right" else (b, y - 1)
    elif frame == 1 or 7 <= frame <= 10:
        x = b if hand == "right" else a
    else:
        x = a if hand == "right" else b
    return (own.at(x, y) if own is not None else x), y


# Right and left hips, in native picture order. The blade falls beside the
# supporting leg; the other loop turns outward with the raised thigh. In
# profile both hilts lead their sheaths as the wearer walks to the right.
_HUMANOID = (
    (104, 75), (77, 105), (123, 114),             # front, rear, profile idle
    (100, 70), (108, 78), (114, 81), (104, 69),   # front steps
    (82, 112), (71, 100), (69, 102), (81, 110),   # rear steps
    (118, 129), (139, 115), (130, 122), (114, 136),
)

# The shorter thigh leaves less clearance between the tip and the foot.
# On the giants the longer weapons can lie closer to the hip in profile.
_SHORT_PROFILE = {2: (130, 120), 11: (126, 135), 12: (142, 122),
                 13: (135, 128), 14: (121, 140)}
_GIANT_PROFILE = {2: (118, 112), 11: (115, 125), 12: (134, 112),
                 13: (126, 118), 14: (111, 131)}

# The thri-kreen carries the belt on the forward part of a low, horizontal
# abdomen. The sheaths lie back along its flank, clear of the walking claws.
_KREEN = (
    (110, 69), (72, 110), (145, 138),
    (106, 66), (112, 73), (117, 76), (108, 65),
    (77, 117), (66, 106), (64, 108), (76, 115),
    (139, 146), (151, 138), (146, 141), (137, 150),
)


def attitude(model, frame, hand):
    """Return the hanging angle for one native walking frame and belt loop."""
    angles = _HUMANOID[frame]
    if model == 2097:
        angles = _KREEN[frame]
    elif model in (2053, 2055, 2068, 2070):
        angles = _SHORT_PROFILE.get(frame, angles)
    elif model in (2072, 2074):
        angles = _GIANT_PROFILE.get(frame, angles)
    return angles[0 if hand == "right" else 1]
