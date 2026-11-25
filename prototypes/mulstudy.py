"""Fit leather, bone and linen to the retail Mul in each map pose."""
import argparse
from functools import lru_cache
from math import cos, exp, sin, pi
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw

from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas
from dsloader import art, classoutfits as co

MODEL = 2093
PAD = 8
ROLES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
# Position of the matching human cel in the Mul cel. Combat cels have
# different bounding boxes when the striking hand travels above the head.
REGISTER = ((1, 1), (0, 0), (0, 0), (1, 1), (0, 1), (1, 1), (0, 1), (0, 0), (0, 0), (0, 0),
            (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, -7), (0, -1), (-7, 1), (0, -3), (0, -7),
            (-9, 0), (-5, -7), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 0))

# Per-row limits on the bald scalp, ear and jaw. Origins move separately
# from the shoulder in the backswing, recoil and bow poses.
FRONT = ((2, 4), (1, 5), (0, 6), (0, 6), (0, 6), (0, 6), (1, 6), (2, 5))
BACK = ((1, 3), (0, 4), (0, 5), (0, 5), (0, 5), (0, 4), (1, 4))
SIDE = ((2, 4), (1, 5), (0, 5), (0, 6), (1, 6), (2, 5))
HEADS = (
    (8, 0, FRONT), (9, 0, BACK), (5, 0, SIDE), (7, 0, FRONT), (6, 0, FRONT), (7, 0, FRONT),
    (7, 0, FRONT), (4, 0, BACK), (5, 0, BACK), (5, 0, BACK), (5, 0, BACK), (7, 0, SIDE),
    (10, 0, SIDE), (6, 0, SIDE), (9, 0, SIDE),
    (6, 2, ((2, 4), (1, 5), (0, 5), (0, 6), (1, 5), (2, 5))),
    (9, 0, FRONT), (3, 4, ((3, 5), (2, 6), (1, 6), (1, 6), (0, 6), (1, 5), (2, 4))),
    (4, 0, BACK), (2, 0, BACK), (4, 0, BACK),
    (6, 0, ((1, 4), (0, 5), (0, 5), (0, 5), (0, 5), (1, 4))),
    (11, 0, SIDE), (11, 0, SIDE), (5, 0, ((3, 5), (1, 6), (0, 8), (0, 8), (1, 8), (3, 6))),
    (6, 3, BACK), (5, 3, ((1, 4), (0, 5), (0, 5), (0, 5), (0, 5), (1, 4))),
    (1, 3, ((4, 7), (2, 6), (1, 6), (1, 6), (0, 6), (0, 5), (0, 4))),
    (5, 0, ((3, 7), (2, 8), (1, 9), (1, 9), (0, 10), (1, 9), (2, 8))),
)
# The original orange skin is lit differently from the human reference.
# Carry the depth of each reconstructed muscle plane into the Mul's ramp.
SKIN = {254: 129, 128: 129, 129: 129, 134: 135, 133: 135, 132: 136, 131: 136, 130: 137, 144: 138,
        145: 139, 146: 140, 147: 141, 148: 142, 149: 143, 150: 143, 151: 151, 152: 152, 153: 153}
NATIVE_LIGHT = {*range(135, 144), 149, 151, 152, 153}
DARK = {128, 129, 254}


def head_pixels(pose, w, h):
    left, top, spans = HEADS[pose]
    pixels = {(left+x, top+y) for y, (a, b) in enumerate(spans) for x in range(a, b+1)}
    if pose == 28:
        return {(w-1-x, h-1-y) for x, y in pixels}
    # These corners lie on the harness or the raised wrist, outside the jaw.
    outside = {8: {(5, 5), (9, 6)}, 10: {(7, 6)}, 23: {(13, 5)}, 26: {(5, 7)}}
    return pixels - outside.get(pose, set())


# The neck opening is wider than the face itself. Each row gives the
# height and span of the exposed clavicles, then the tip of the opening.
# Traces are in native cel coordinates (feet down for the fallen cel).
# In profile the throat moves forward of the shoulder; on recoil it lies
# behind the projected chin. The nape needs a shallower opening.
NECKLINES = (
    (5, 6, 16, 11, 11), (5, 8, 16, 11, 9), (3, 4, 12, 7, 9),
    (5, 5, 15, 10, 11), (5, 4, 14, 9, 11), (4, 5, 15, 10, 10),
    (5, 5, 15, 10, 11), (5, 3, 11, 7, 9), (5, 3, 12, 7, 9),
    (5, 4, 12, 8, 9), (5, 4, 12, 8, 9), (3, 6, 14, 9, 9),
    (3, 8, 17, 11, 9), (3, 5, 13, 8, 9), (3, 7, 16, 10, 9),
    (6, 5, 13, 9, 12), (5, 7, 17, 12, 10), (7, 3, 12, 8, 14),
    (5, 3, 11, 6, 9), (5, 1, 9, 6, 9), (5, 3, 11, 8, 9),
    (4, 5, 13, 9, 10), (3, 9, 18, 13, 9), (3, 9, 18, 13, 10),
    (4, 4, 14, 8, 11), (8, 5, 13, 9, 13), (7, 3, 12, 8, 13),
    (7, 0, 10, 7, 13), (5, 5, 16, 10, 11),
)


def neckline_pixels(pose, width, height):
    top, left, right, tip_x, bottom = NECKLINES[pose]
    pixels = set()
    for y in range(top, bottom + 1):
        depth = (y-top) / (bottom-top)
        start = round(left + depth*(tip_x-left))
        end = round(right + depth*(tip_x-right))
        for x in range(start, end + 1):
            pixels.add((width-1-x, height-1-y) if pose == 28 else (x, y))
    return pixels


def collar_opening(pose, w, h):
    """Keep the chin and throat open; the broad shoulders sit beside them."""
    left, top, spans = HEADS[pose]
    chin = top+len(spans)-1
    jaw = left+sum(spans[-1])/2
    opening = set()
    for px, py in neckline_pixels(pose, w, h):
        x, y = (w-1-px, h-1-py) if pose == 28 else (px, py)
        below = y-chin
        if below <= 0 or below <= 3 and abs(x-jaw) <= 3.5-below*.65:
            opening.add((px, py))
    return opening


@lru_cache(maxsize=2)
def body_chunk(combat):
    tag = "combat" if combat else "walk"
    with ZipFile(Path(co.__file__).with_name("human_outfit_layers.zip")) as archive:
        return archive.read(f"Study/{tag}-body")


# Each cut was traced on the unpadded Mul body. The four cross-sections
# (row, left, right) locate the shoulder, ribs, girdle and hanging hem.
# The last number lifts one corner of the hem as the near knee advances.
ROBE_CUTS = (
    ((5, 4, 18), (9, 4, 17), (14, 7, 14), (23, 5, 17), 2),
    ((6, 5, 16), (10, 5, 16), (14, 7, 14), (23, 5, 17), -2),
    ((4, 3, 8), (9, 1, 8), (15, 2, 8), (23, -1, 10), 2),
    ((5, 3, 17), (9, 4, 16), (14, 5, 13), (22, 4, 15), 2),
    ((5, 3, 16), (9, 3, 15), (14, 5, 12), (22, 4, 14), -2),
    ((4, 4, 15), (9, 3, 15), (13, 5, 13), (22, 4, 15), -1),
    ((5, 3, 16), (9, 4, 15), (14, 5, 13), (22, 4, 14), 2),
    ((6, 1, 12), (9, 2, 12), (14, 4, 10), (22, 2, 12), 2),
    ((5, 1, 12), (9, 2, 13), (14, 4, 10), (23, 2, 12), 2),
    ((6, 2, 13), (9, 3, 13), (14, 5, 11), (22, 3, 13), -1),
    ((5, 3, 13), (9, 3, 13), (14, 5, 11), (23, 3, 13), -2),
    ((4, 5, 10), (9, 3, 10), (15, 3, 8), (22, -1, 9), 2),
    ((4, 8, 13), (9, 5, 12), (15, 5, 10), (22, 0, 13), -2),
    ((4, 4, 9), (9, 2, 10), (15, 2, 7), (22, -2, 8), 2),
    ((3, 6, 12), (8, 4, 12), (15, 4, 9), (22, 0, 13), 3),
    ((7, 5, 11), (11, 3, 11), (15, 3, 9), (23, 0, 13), 2),
    ((5, 7, 17), (9, 7, 17), (12, 7, 16), (16, 5, 17), 1),
    ((7, 8, 13), (10, 8, 14), (13, 8, 14), (17, 4, 15), -2),
    ((6, 3, 9), (10, 2, 10), (14, 2, 8), (23, 0, 11), -2),
    ((6, 4, 10), (9, 3, 10), (14, 4, 11), (22, 2, 14), -2),
    ((5, 5, 10), (9, 6, 12), (14, 6, 13), (22, 4, 16), -2),
    ((5, 5, 15), (10, 5, 13), (15, 6, 14), (23, 5, 16), 2),
    ((5, 7, 15), (9, 6, 13), (14, 4, 11), (22, 0, 12), 3),
    ((5, 7, 15), (9, 4, 12), (13, 4, 11), (20, 0, 12), 2),
    ((5, 5, 11), (10, 5, 10), (15, 4, 10), (23, 1, 12), 2),
    ((8, 7, 11), (12, 5, 12), (17, 6, 10), (25, 4, 14), -2),
    ((8, 4, 13), (13, 4, 12), (18, 6, 12), (26, 5, 15), 1),
    ((6, 6, 11), (9, 5, 12), (11, 5, 13), (16, 5, 16), 3),
    ((6, 2, 16), (10, 4, 15), (13, 5, 13), (18, 3, 14), 1),
)

# Near forearms that cross the linen, traced from elbow to wrist on the
# source (centre line and thickness). The garment turns under the sleeve.
CROSSING_ARMS = {
    2: ((2, 10), (5, 14), (11, 15), 3), 11: ((4, 10), (5, 13), (11, 14), 3),
    12: ((7, 8), (6, 10), (5, 14), 3), 13: ((4, 9), (3, 12), (5, 16), 3),
    14: ((5, 9), (7, 12), (15, 13), 3), 15: ((4, 10), (3, 14), (5, 17), 3),
    17: ((12, 10), (10, 13), (3, 17), 3), 18: ((11, 7), (10, 9), (7, 11), 2),
    19: ((4, 8), (4, 11), (1, 13), 2), 20: ((8, 7), (5, 8), (1, 8), 2),
    22: ((13, 7), (16, 9), (21, 10), 3), 23: ((14, 7), (15, 11), (18, 13), 3),
    24: ((6, 9), (6, 12), (11, 15), 3), 25: ((12, 10), (11, 12), (10, 14), 2),
    26: ((2, 8), (3, 10), (5, 11), 3), 27: ((3, 9), (2, 12), (4, 14), 3),
}


@lru_cache(maxsize=2)
def linen_grain(game):
    return reference_folds(game)["linen"]


# Warm middle tones keep broad lit planes ivory on arena sand. The old
# high-contrast brown/white trim is confined to the belt and turned hem.
MUL_LINEN = (208, 204, 207, 205, 194, 206, 120, 61, 123, 199, 125, 62, 155, 63)


def cleric_robe(game, pose, body, protected, arm):
    shoulder, ribs, waist, hem, lift = ROBE_CUTS[pose]
    height, width = len(body), len(body[0]) - 2*PAD
    # A crossing arm hides the last sliver of sleeve in these poses.
    # Expose the skin there so an isolated linen fleck cannot sit at the jaw.
    sleeve_tips = {12: ((5, 9),), 19: ((3, 8),), 24: ((5, 7), (5, 8)),
                   25: ((12, 13),), 26: ((4, 9),)}
    protected = protected.union(sleeve_tips.get(pose, ()))
    result = [row[:] for row in body]
    grain = linen_grain(game)
    side = pose in (2, 11, 12, 13, 14, 15, 22, 23, 24)
    rear = pose in (1, 7, 8, 9, 10, 18, 19, 20, 25)
    train = {2: 2, 11: 3, 12: 5, 13: 4, 14: 2, 22: 3, 23: 4, 24: 2}.get(pose, 0)
    cuts = (shoulder, ribs, waist, hem)
    for start, end in zip(cuts, cuts[1:]):
        for y in range(start[0], end[0] + (end == hem)):
            t = (y-start[0]) / (end[0]-start[0])
            left = round(start[1] + t*(end[1]-start[1]))
            right = round(start[2] + t*(end[2]-start[2]))
            # Trace the free back fold independently of the trouser leg.
            # It trails on the outward stride and gathers closer on return.
            if train and y > ribs[0]:
                turn = min(1, (y-ribs[0]) / max(1, hem[0]-ribs[0]-3))
                left -= round(train*turn)
            if y > waist[0]+1:
                flare = (y-waist[0])/(hem[0]-waist[0])
                left -= round(2*flare)
                right += round(1.5*flare)
            for x in range(left, right+1):
                u = (x-left)/(right-left)
                # One knee pushes the corner up; two offset folds describe
                # the volume over the thighs, including the space between them.
                bottom = hem[0] - round(max(0, lift)*u + max(0, -lift)*(1-u)
                                        + 1.9*abs(2*u-1)**3)
                if train:
                    bottom += round((1-u)*1.5)
                if pose == 5 and x < waist[1] and y >= waist[0] and y <= waist[0]+3:
                    continue
                if y > bottom:
                    continue
                px, py = (width-1-x, height-1-y) if pose == 28 else (x, y)
                if not 0 <= px+PAD < len(body[py]):
                    continue
                skin = body[py][px+PAD]
                if ((px, py) in protected or (y <= waist[0] and skin is None and not (train and y >= waist[0]-2))
                        or (skin is not None and 0 <= px < width and arm.getpixel((px, py)))):
                    continue
                relief = grain[(y-waist[0]) % 8][(x-waist[1]) % 8]
                shade = 9.1 + .9*relief - 3.5*u + .8*sin(pi*u)
                if y < waist[0]:
                    # A shallow back yoke and diagonal front overlap leave the
                    # neck open. In profile only the near lapel is visible.
                    depth = (y-shoulder[0])/(waist[0]-shoulder[0])
                    if rear:
                        seam_y = shoulder[0] + 1 + round(2*sin(pi*u))
                        if y == seam_y:
                            shade -= 2.4
                    else:
                        seam = .76 - .65*depth
                        distance = (u-seam)*(right-left)
                        if abs(distance) < .68:
                            shade -= 3.3
                        elif .68 <= distance < 1.7:
                            shade += 2.1
                    shade += 1.5*(1-depth) - 1.3*exp(-.7*(y-waist[0]+1)**2)
                else:
                    drop = (y-waist[0])/(hem[0]-waist[0])
                    fold = (.41 if side else .53) + (.22 if lift > 0 else -.23)*drop
                    dist = (u-fold)*(right-left)
                    shade += 3.2*exp(-.45*(dist+1.7)**2) - 4.5*exp(-.65*dist**2)
                    # Light across the near knee, then a narrow turned
                    # lining on the opposite side. Both follow the lifted hem.
                    return_fold = (u-(.19+.11*drop if lift > 0 else .82-.10*drop))*(right-left)
                    shade += 2.0*exp(-.45*(return_fold+1.2)**2)-3.2*exp(-.8*return_fold**2)
                belt_y = waist[0] - int(u > .72)
                if y == belt_y:
                    color = 94 if u < .55 else 90
                else:
                    if y == bottom:
                        shade -= 4.8
                    elif y == bottom-1:
                        shade += 1.7*sin(pi*u)
                    if x == right:
                        shade -= 3.8
                    if x == left:
                        shade -= 1.8
                    color = MUL_LINEN[max(0, min(len(MUL_LINEN)-1, round(shade)))]
                result[py][px+PAD] = color
    return result


# The near shoulder cap and the free corner of the battle kilt, in the
# native cel. The arm turns to the other side of the spine in rear views.
# The fallen cel is authored upright, like the robe.
HIDE_POINTS = (
    (5, 8, 8, 21), (15, 8, 15, 20), (3, 7, 2, 20),
    (4, 8, 6, 21), (4, 8, 10, 19), (5, 7, 12, 20), (4, 8, 7, 19),
    (11, 8, 4, 20), (11, 7, 4, 20), (12, 8, 10, 20), (12, 7, 11, 20),
    (5, 7, 4, 20), (8, 6, 10, 19), (4, 6, 4, 21), (7, 6, 7, 20),
    (6, 9, 5, 20), (8, 8, 8, 16), (12, 9, 13, 16),
    (9, 8, 7, 19), (9, 8, 10, 19), (10, 7, 13, 20),
    (6, 7, 10, 20), (9, 7, 6, 19), (9, 7, 5, 17),
    (5, 7, 5, 20), (10, 10, 10, 22), (5, 10, 8, 23),
    (10, 8, 10, 15), (4, 9, 7, 17),
)
BONE = (88, 204, 205, 194, 206, 61, 199, 125, 62, 155)
JERKIN = (208, 88, 204, 89, 90, 207, 91, 205, 92, 93, 94, 95, 96, 97, 98)
BRONZE = (88, 89, 90, 94, 95, 168, 169, 170, 171)


def material_color(ramp, level):
    return ramp[max(0, min(len(ramp)-1, round(level)))]


def leather_outfits(game, pose, body, keep, arm):
    glad, fighter = ([row[:] for row in body] for _ in range(2))
    h, w = len(body), len(body[0])-2*PAD
    (sy, sl, sr), (ry, rl, rr), (wy, wl, wr), _, _ = ROBE_CUTS[pose]
    gx, gy, knee, hem = HIDE_POINTS[pose]
    profile = pose in (2, 11, 12, 13, 14, 15, 22, 23, 24)
    # The far end of the baldric is sewn into the opposite side of the
    # belt. The jerkin has a separate breast, side seam and overlapping tabs.
    anchor = wl+1 if gx > (sl+sr)/2 else wr-1
    hide = RAMPS["hide"]
    grain = linen_grain(game)
    for y in range(sy, hem+1):
        if y <= ry:
            t = (y-sy)/max(1, ry-sy)
            lo = sl+1+(rl-sl)*t
            hi = sr-1+(rr-sr)*t
        else:
            t = min(1, (y-ry)/max(1, wy-ry))
            lo = rl+1+(wl-rl-1)*t
            hi = rr-1+(wr-rr+1)*t
        depth = (y-gy)/max(1, wy-gy)
        strap = gx+(anchor-gx)*min(1, max(0, depth))
        for x in range(min(sl, rl, wl, gx, knee)-3, max(sr, rr, wr, gx, knee)+4):
            px, py = (w-1-x, h-1-y) if pose == 28 else (x, y)
            if not (0 <= py < h and 0 <= px+PAD < len(body[py])) or (px, py) in keep:
                continue
            u = px+PAD
            skin = body[py][u]
            if skin is not None and 0 <= px < w and arm.getpixel((px, py)):
                continue
            across = (x-lo)/max(1, hi-lo)
            weave = grain[(y-wy)%8][(x-wl)%8]
            relief = (game.palette[skin][0]-125)/62 if skin is not None else -.8
            tone = 6.8 + .65*weave + relief - 2.6*across
            if y < wy and skin is not None:
                if lo-1 <= x <= hi+1:
                    # The shaded facing meets the side under the armhole.
                    seam = x-(lo+.72*(hi-lo)) - .55*sin(depth*pi)
                    shade = tone+1.7*sin(pi*across)-3.3*exp(-seam**2)
                    # The near facing turns over the ribs, leaving a light
                    # cut edge beside the inset seam even in the side stride.
                    rim = x-lo
                    shade += 3.2*exp(-.9*(rim-.6)**2) - 1.8*exp(-(rim-2)**2)
                    fighter[py][u] = material_color(JERKIN, shade-1.6)
                    # Two short bindings attach the pauldron to the jerkin.
                    lacing = x - (gx+(strap-gx)*.75)
                    if y in (gy+2, gy+4) and abs(lacing) <= 1 and y < wy-1:
                        fighter[py][u] = 199 if lacing < .1 else 94
                dist = x-strap
                if abs(dist) <= (1.45 if profile else 1.85):
                    glad[py][u] = material_color(hide, 4.8+.6*weave+relief+2.8*(dist < -.35)-2*(dist > .65))
            # The bevel of the bone scale continues inward from the
            # pauldron onto its leather backing. It ends at the armhole.
            if skin is not None and gy <= y <= gy+3:
                inward = 1 if gx < (sl+sr)/2 else -1
                joint = (x-gx)*inward
                ridge = 1 + (y-gy)*.65
                if 0 <= joint <= 4 and abs(joint-ridge) <= 1.1:
                    fighter[py][u] = material_color(BONE, 6.9+.5*weave-1.15*(y-gy)-1.3*(joint>ridge))
            # Each upper arm rolls out from beneath a short guard. Its
            # highlight follows the dome; a dark lower lip touches the strap.
            cx = abs(x-gx)
            gyoff = y-gy
            if skin is not None and cx <= (3 if profile else 2) and -2 <= gyoff <= 1 and cx+abs(gyoff) <= (4 if profile else 3):
                dome = 7.0 - .9*cx - 1.1*gyoff + .35*weave
                fighter[py][u] = material_color(BONE, dome-2.7*(gyoff == 1))
                if gyoff == 1 and x > gx-1:
                    fighter[py][u] = 205
                if gyoff == 0 and (x-gx) in (-2, -1):
                    fighter[py][u] = 199
                if cx < 2 or gyoff == 0:
                    glad[py][u] = material_color(BRONZE, dome-2.5*(gyoff == 1))
            if y < wy-1:
                continue
            drop = (y-wy)/max(1, hem-wy)
            # The high hip is fitted. Below it the leather clears the gap
            # between the legs and turns towards the advancing knee.
            left = round(wl + (knee-3-wl)*max(drop, 0))
            right = round(wr + (knee+3-wr)*max(drop, 0))
            if profile and wy+1 <= y < hem-1 and wl-2 <= x < left:
                back_edge = wl-round(2*(y-wy)/max(1, hem-wy))
                if x >= back_edge and y <= hem-1:
                    fighter[py][u] = material_color(hide, 6.1+.9*weave+2.7*(x == back_edge+1))
            # A separate leather side tab hangs from the hip behind the
            # leading leg. It pivots from the girdle, clear of the bare knee.
            if not profile and pose not in (5, 6) and wy < y < hem-1:
                far = wr if knee < (wl+wr)/2 else wl
                sign = 1 if far == wr else -1
                edge = far + sign*round(1.7*drop)
                if 0 <= (edge-x)*sign <= 2 and (x != edge or y < hem-2):
                    fighter[py][u] = material_color(hide, 5.8+.65*weave+3*(x == edge-sign))
            if not left <= x <= right or y < wy and skin is None:
                continue
            lap = x-(knee+(anchor-knee)*(1-drop))
            lower = hem-round(min(3, .34*abs(x-knee))) - int(x == left or x == right)
            if y > lower:
                continue
            if y <= wy:
                belt = 169 if x == anchor and y == wy-1 else 89 if y == wy else 92
                glad[py][u] = belt
                fighter[py][u] = 199 if x == anchor and y == wy-1 else belt
                continue
            shade = 8.0+.85*weave-3.4*exp(-lap**2)+3.7*exp(-(lap+1.2)**2)
            shade -= 2.7*(y == lower) + 2*(x == right)
            # The lit ridge on the flap breaks the russet-on-copper edge.
            glad[py][u] = material_color(hide, shade+.9)
            if -.95 <= lap < .15 and y < lower:
                glad[py][u] = 95 if y == wy+1 else 168
            # Short skirt tabs over the far thigh distinguish the jerkin
            # from the Gladiator's single, longer lapped kilt.
            tab = x-(wl+.32*(wr-wl)+.35*(knee-anchor)*drop)
            if y < lower-1 or abs(tab) < 1.15:
                fighter[py][u] = material_color(JERKIN, shade-2.7+2.0*cos(tab*1.3))
                if abs(tab) < .85 and y <= wy+2:
                    fighter[py][u] = 199 if y == wy+1 else 205
    for x, y in {4: ((8, 19),), 19: ((9, 18),), 20: ((11, 18),)}.get(pose, ()):
        garment = glad if pose == 4 else fighter
        garment[y][x+PAD] = 90
    return {"Gladiator": glad, "Fighter": fighter}


def fitted_rows(game, pose):
    cb, f = divmod(pose, 15)
    native, human = game.fr(MODEL+cb, f), game.fr(2095+cb, f)
    bare = co.Frame(art.decode_frame(body_chunk(cb), f)[2], {}).canvas(human, PAD)
    dx, dy = REGISTER[pose]
    w, h = len(native[0]), len(native)
    head = head_pixels(pose, w, h)
    fig = game.fig(MODEL)
    parts = fig.parts(cb, f)
    bow = game.bow(fig, native, parts) if pose in (24, 25, 26) else set()
    original = [[None]*PAD+list(r)+[None]*PAD for r in native]
    body = [r[:] for r in original]
    keep = head | bow
    for y, row in enumerate(native):
        for x, c in enumerate(row):
            if c is None or c in NATIVE_LIGHT or (x, y) in keep:
                continue
            u, v = x-dx+PAD, y-dy+PAD
            donor = bare[v][u] if 0 <= v < len(bare) and 0 <= u < len(bare[0]) else None
            # Keep the outline of the trailing foot where it meets the floor.
            if c in DARK and (y == h-1 or (y >= h-3 and native[y+1][x] is None)):
                body[y][x+PAD] = 129
                continue
            if donor in SKIN:
                body[y][x+PAD] = SKIN[donor]
                continue
            # The Mul has an extra row of muscle along parts of his arms
            # and calves. Follow the nearest lit skin inside the same limb.
            samples = [bare[v+j][u+i] for i, j in ((0, -1), (-1, 0), (1, 0), (0, 1))
                       if 0 <= v+j < len(bare) and 0 <= u+i < len(bare[0]) and bare[v+j][u+i] in SKIN]
            edge = x == w-1 or row[x+1] is None or y == h-1 or native[y+1][x] is None
            body[y][x+PAD] = 129 if edge else SKIN[samples[0]] if samples else 135
    # Restore the dressed figure’s open neckline from the cleaned skin.
    # Extending the retail head mask here would bring back harness pixels.
    keep.update(collar_opening(pose, w, h))
    # The near hand crosses the hip at side step two, and the draw hand
    # overlaps the tunic in the front bow. Keep those knuckles on top.
    for hx, hy in parts.hands.values():
        for ix, iy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            x, y = hx+ix, hy+iy
            if 0 <= x < w and 0 <= y < h and native[y][x] is not None:
                keep.add((x, y))
    # At a crossed arm the cloth must pass behind the forearm as well as
    # behind the fingertips. The Fighter guard can still cover the upper arm.
    arm = Image.new("1", (w, h))
    if pose in CROSSING_ARMS:
        elbow, bend, wrist, thickness = CROSSING_ARMS[pose]
        ImageDraw.Draw(arm).line((elbow, bend, wrist), fill=1, width=thickness)
    # Sculpt the reconstructed skin under the old harness and shorts.
    # Stay inside the native copper silhouette; the original exposed muscles
    # and the face supply the light direction and keep their painted pixels.
    _, (ry, rl, rr), (wy, wl, wr), _, _ = ROBE_CUTS[pose]
    skin_ramp = (129, 135, 136, 137, 138, 139, 140, 141, 142, 143, 151, 152, 153)
    for py, row in enumerate(native):
        for px, original_tone in enumerate(row):
            x, y = (w-1-px, h-1-py) if pose == 28 else (px, py)
            c = body[py][px+PAD]
            if original_tone is None or original_tone in NATIVE_LIGHT or (px, py) in keep or arm.getpixel((px, py)):
                continue
            if c not in skin_ramp or c == 129 or not ry <= y < wy+4:
                continue
            t = min(1, (y-ry)/max(1, wy-ry))
            left, right = rl+(wl-rl)*t, rr+(wr-rr)*t
            if not left < x < right:
                continue
            across = (x-left)/(right-left)
            plane = 1.65*exp(-12*(across-.28)**2)-1.5*exp(-18*(across-.81)**2)
            body[py][px+PAD] = material_color(skin_ramp, skin_ramp.index(c)+plane)
    out = {"Original": original, "Body base": body}
    out.update(leather_outfits(game, pose, body, keep, arm))
    out["Cleric"] = cleric_robe(game, pose, body, keep, arm)
    return out


def sheet_tile(sheet, pose, role):
    x = 8 + (pose % 2)*558 + ROLES.index(role)*110
    y = 76 + (pose//2)*137
    return sheet.crop((x, y, x+108, y+102)).resize((54, 51), Image.Resampling.NEAREST)


def neckline_comparison(game, previous, current):
    poses = (0, 12, 16, 17, 24, 26)
    page = Image.new("RGB", (790, 80 + 104*len(poses)), dwarf.PAPER)
    label(page, (12, 8), "Mul Cleric   /   face and neckline", 21)
    columns = ((current, "Original", "Retail Mul"), (current, "Body base", "Cleaned body"),
               (previous, "Cleric", "Previous collar"), (current, "Cleric", "Open collar"))
    for j, (_, _, caption) in enumerate(columns):
        label(page, (156 + 166*j, 45), caption, 16)
    for i, pose in enumerate(poses):
        native = game.fr(MODEL + pose//15, pose % 15)
        left, top, _ = HEADS[pose]
        x = (54-len(native[0]))//2 + left - 4
        y = 51-2-len(native) + top - 1
        row = 75 + 104*i
        label(page, (12, row+24), f"{pose:02}", 13)
        label(page, (12, row+43), dwarf.NAMES[pose], 13)
        for j, (sheet, role, _) in enumerate(columns):
            tile = sheet_tile(sheet, pose, role)
            close = tile.crop((x, y, x+17, y+15))
            col = 123 + j*166
            page.paste(close.resize((102, 90), Image.Resampling.NEAREST), (col, row))
            page.paste(tile, (col+104, row+39))
    return page


def cleric_comparison(game, pose, rows, sand, previous_sheet):
    before = sheet_tile(previous_sheet, pose, "Cleric")
    cb, f = divmod(pose, 15)
    npc = 1563 + cb
    caption = "Retail Priest"
    if f >= game.count(npc):
        npc, f = 1563, 0
        caption += " (idle)"
    def tile(pixels):
        return elf.placed_tile(game, pixels, sand, 1, 0, 0, 0)

    samples = (("Mul body", tile(rows["Body base"])), ("Previous robe", before),
               ("Refitted robe", tile(rows["Cleric"])), (caption, tile(game.fr(npc, f))))
    page = Image.new("RGB", (736, 276), dwarf.PAPER)
    label(page, (12, 7), "Mul Cleric fitting", 20)
    label(page, (724, 8), f"{pose:02}   {dwarf.NAMES[pose]}", 16, "ra")
    for j, (name, sample) in enumerate(samples):
        x = 16 + j*182
        label(page, (x+81, 35), name, 15, "ma")
        page.paste(sample.resize((162, 153), Image.Resampling.NEAREST), (x, 58))
        page.paste(sample, (x+54, 216))
    return page


def render(game_dir, output, previous_sheet=None, previous_neckline=None):
    atlas = Atlas(game_dir)
    game = atlas.game
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    paving = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB")
    paving = paving.crop((158, 21, 212, 72))
    frames = []
    comparisons = []
    before = Image.open(previous_sheet).convert("RGB") if previous_sheet else None
    sheet = Image.new("RGB", (2*5*110+28, 15*137+44), dwarf.PAPER)
    label(sheet, (12, 7), "Mul fittings   /   all 29 map poses", 20)
    references = ((1252, "Retail Warrior"), (1563, "Retail Priest"),
                  ("Gladiator", "Human Gladiator"), ("Warrior", "Human Warrior"),
                  ("Priest", "Human Priest"))
    for pose, name in enumerate(dwarf.NAMES):
        rows = fitted_rows(game, pose)
        page = Image.new("RGB", (846, 468), dwarf.PAPER)
        label(page, (12, 8), "Mul   /   revised fittings", 21)
        label(page, (832, 9), f"{pose:02}   {name}", 17, "ra")
        for j, role in enumerate(ROLES):
            x = 8+j*167
            label(page, (x+81, 43), role, 15, "ma")
            tile = elf.placed_tile(game, rows[role], sand, 1, 0, 0, 0)
            page.paste(tile.resize((162, 153), Image.Resampling.NEAREST), (x, 65))
            page.paste(tile, (x+25, 224))
            page.paste(elf.placed_tile(game, rows[role], paving, 1, 0, 0, 0), (x+83, 224))
            sx = 8 + pose % 2*558 + j*110
            sy = 43 + pose//2*137
            if j == 0:
                label(sheet, (sx, sy), f"{pose:02}   {name}", 14)
            label(sheet, (sx, sy+17), role, 12)
            sheet.paste(tile.resize((108, 102), Image.Resampling.NEAREST), (sx, sy+33))
        label(page, (12, 287), "Retail and human references", 17)
        for j, (reference, caption) in enumerate(references):
            x = 8+j*167
            if isinstance(reference, int):
                cb, f = divmod(pose, 15)
                pic = reference+cb
                if f >= game.count(pic):
                    pic, f = reference, 0
                    caption += " (idle)"
                ref = game.fr(pic, f)
                large = elf.placed_tile(game, ref, sand, 2, 0, 0, 0)
                small = elf.placed_tile(game, ref, paving, 1, 0, 0, 0)
            else:
                atlas.floor = sand
                large = atlas.tile(300, pose, reference, "Class colors", 2)
                atlas.floor = paving
                small = atlas.tile(300, pose, reference, "Class colors", 1)
            label(page, (x+81, 320), caption, 14, "ma")
            page.paste(large, (x, 348))
            page.paste(small, (x+109, 399))
        frames.append(page)
        if before is not None:
            comparisons.append(cleric_comparison(game, pose, rows, sand, before))
    output.mkdir(parents=True, exist_ok=True)
    loop(frames, output/"mul-study.gif")
    sheet.save(output/"mul-poses.png")
    if previous_neckline:
        with Image.open(previous_neckline) as old:
            neckline_comparison(game, old, sheet).save(output/"mul-neckline.png")
    if comparisons:
        loop(comparisons, output/"mul-cleric-fitting.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-sheet", type=Path, help="mul-poses.png from 61f043d for the fitting comparison")
    parser.add_argument("--previous-neckline", type=Path, help="mul-poses.png from cab055c for the collar close-up")
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_sheet, args.previous_neckline)
