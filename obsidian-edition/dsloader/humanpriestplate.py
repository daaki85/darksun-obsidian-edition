"""Metal visible above the woman Priest's original linen skirt, in native pose coordinates."""

from . import classoutfits as co

# First row, then inclusive runs across the visible breast or back plate. The
# archive's torso mask supplies the inner contours at the hair, hands and bow.
# Keep linen above the collar opening and at the waist as the body pitches.
_CUIRASS = (
    (9, ((4, 11), (4, 12), (4, 12), (5, 10), (7, 9))),       # front idle
    (10, ((12, 12), (12, 12), (12, 12))),                     # rear, beside hair
    (9, ((7, 8), (6, 9), (3, 8), (3, 6), (5, 5))),           # profile
    (9, ((4, 11), (4, 12), (4, 11), (5, 10), (7, 8))),       # front walk
    (9, ((6, 12), (6, 12), (7, 12), (8, 11))),
    (9, ((5, 12), (5, 13), (6, 12), (8, 10))),
    (9, ((4, 10), (4, 11), (5, 11), (7, 9))),
    (10, ((11, 11), (11, 11), (11, 11))),                     # rear walk
    (10, ((12, 12), (12, 12), (12, 12))),
    (11, ((13, 14), (13, 13))),
    (12, ((11, 12),)),                                         # nearly covered
    (9, ((11, 12), (9, 12), (7, 11), (7, 8))),                # side walk
    (9, ((11, 13), (10, 13), (10, 13), (9, 13), (10, 12))),
    (9, ((14, 16), (13, 16), (13, 16), (13, 16), (14, 15))),
    (9, ((12, 13), (11, 14), (10, 14), (8, 11), (9, 10))),
    (17, ((11, 14), (10, 13), (9, 14), (8, 13), (9, 12), (10, 11))),  # bent strikes
    (11, ((10, 14), (9, 15), (10, 13))),
    (10, ((14, 19), (14, 18))),
    (14, ((8, 10), (8, 9), (7, 9))),
    (18, ((10, 11), (10, 10), (10, 10))),
    (9, ((12, 14), (13, 16), (14, 17), (16, 17))),
    (16, ((13, 17), (12, 18), (12, 18), (13, 17), (14, 16))),
    (12, ((16, 18), (12, 16), (13, 15))),
    (10, ((16, 17), (15, 16), (15, 15))),
    (10, ((9, 12), (8, 12), (7, 8), (6, 7))),                # bow, near arm across breast
    (13, ((9, 9), (5, 9), (6, 8))),
    (12, ((5, 9), (5, 13), (6, 12), (8, 10))),
    (10, ((9, 10), (8, 11), (5, 11), (6, 11), (7, 9))),     # recoil
    (7, ((9, 12), (9, 12))),                                  # inverted torso behind hair
)

# The point of the original V collar dips below the shoulder line in front.
_COLLAR = {0: (7, 9), 3: (7, 9), 4: (9, 9), 5: (8, 9), 6: (7, 9)}


def cells(frame, pose, bit):
    """Fitted plate pixels for one equipment region; the robe hides her greaves."""
    if bit == co.LEGS:  # The entire lower-garment region is the swinging skirt.
        return ()
    if bit == co.ARMS:  # Original ochre wristbindings, allowing the knuckles to show below.
        return tuple((x, y) for x, y in frame.regions[bit]
                     if frame.image[y + 6][x + 6] in (168, 205))
    top, runs = _CUIRASS[pose]
    point = _COLLAR.get(pose)
    return tuple((x, y) for x, y in frame.regions[bit]
                 if top <= y < top + len(runs) and runs[y - top][0] <= x <= runs[y - top][1]
                 and (x, y) != point)
