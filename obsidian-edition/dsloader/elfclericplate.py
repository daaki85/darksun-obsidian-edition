"""Plate panel of the elf woman's Cleric robe, in the native pose coordinates."""

from . import classoutfits as co


# Three cross-sections (row, left, right) across the upper ribs, fullest
# chest, and the short return above the belt. Coordinates are in screen
# order. The final cel is feet-up, so its sections run from belt to collar.
# Each pose has its own cut beneath the moving hair, elbow and robe collar.
SECTIONS = (
    ((10, 6, 9), (12, 5, 10), (15, 5, 8)),    # front, rear and profile idle
    ((10, 8, 10), (12, 6, 11), (14, 7, 9)),
    ((8, 5, 6), (10, 3, 5), (12, 3, 4)),
    ((11, 5, 8), (13, 3, 8), (16, 3, 6)),     # toward the camera
    ((8, 8, 11), (10, 6, 11), (12, 5, 9)),
    ((8, 4, 8), (10, 4, 9), (12, 5, 8)),
    ((8, 4, 7), (10, 3, 8), (12, 3, 6)),
    ((8, 4, 8), (10, 3, 8), (13, 3, 7)),      # away
    ((10, 4, 6), (12, 1, 6), (14, 1, 4)),
    ((10, 7, 9), (12, 4, 8), (14, 3, 6)),
    ((11, 6, 9), (13, 5, 9), (15, 5, 7)),
    ((8, 4, 5), (10, 3, 5), (12, 3, 4)),      # across
    ((8, 11, 12), (10, 9, 11), (12, 8, 10)),
    ((8, 6, 7), (10, 5, 7), (12, 4, 6)),
    ((8, 6, 7), (10, 5, 7), (12, 4, 6)),
    ((16, 6, 9), (18, 4, 8), (20, 2, 5)),     # front strikes: the third is nearly horizontal
    ((12, 10, 13), (13, 8, 13), (15, 8, 10)),
    ((8, 19, 21), (9, 16, 20), (11, 14, 17)),
    ((10, 10, 13), (12, 9, 14), (14, 9, 11)), # rear strikes
    ((17, 10, 12), (19, 9, 13), (22, 7, 9)),
    ((9, 14, 17), (11, 14, 19), (13, 16, 18)),
    ((16, 11, 13), (18, 10, 13), (20, 10, 12)), # profile strikes
    ((8, 6, 8), (10, 6, 9), (12, 5, 7)),
    ((9, 5, 6), (10, 4, 6), (12, 3, 5)),
    ((8, 6, 7), (10, 4, 7), (12, 4, 6)),      # bow draw, lift and release
    ((11, 6, 7), (13, 4, 7), (15, 4, 6)),
    ((11, 9, 11), (13, 7, 12), (16, 6, 9)),
    ((11, 5, 8), (12, 5, 10), (14, 5, 8)),    # recoil and fall
    ((6, 8, 10), (8, 8, 12), (9, 10, 13)),
)

# Fixed linen values in this model's robe, including warm shadows and cool
# seam lights. A teal sash, leather sword belt, plum lining and bone toggle
# crossing the panel keep their native color.
LINEN = frozenset((61, 62, 63, 92, 95, 97, 118, 119, 120, 121, 122, 123, 124, 125, 126,
                   155, 194, 199, 204, 205, 206, 207, 208, 214, 215))


def cells(frame, pose, bit):
    if bit != co.CHEST:
        # Her sleeves end above the exposed forearms; her skirt is linen
        # down to its hem. The visible cuffs and calves have their own fits.
        return ()
    top, middle, bottom = SECTIONS[pose]
    shape = set()
    for (y0, left0, right0), (y1, left1, right1) in ((top, middle), (middle, bottom)):
        for y in range(y0, y1+1):
            t = (y-y0)/(y1-y0)
            left = round(left0 + (left1-left0)*t)
            right = round(right0 + (right1-right0)*t)
            shape.update((x, y) for x in range(left, right+1))
    return tuple((x, y) for x, y in frame.regions[bit] if (x, y) in shape
                 and frame.image[y+4][x+4] in LINEN)
