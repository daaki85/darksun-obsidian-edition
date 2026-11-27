"""Render an art study on the two retail half-giants. Run with GAME_DIR OUTPUT_DIR."""
import argparse
import math
from pathlib import Path

from PIL import Image

from halfgiantfit import RANGER_CLOAK, REAR_FOLD_GUIDES, SLEEVES, WOMAN_TEAL_HEM, fitted_panels, stamp
from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas
from shoulderscale import jerkin_facing, shoulder_paint

MODELS = (2072, 2074)
ROLES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric", "Psionicist", "Ranger")
PAIRS = ("Cleric/Fighter", "Cleric/Psionicist", "Cleric/Ranger",
         "Fighter/Psionicist", "Psionicist/Ranger")
# Outline of the garment laid open on the pose: shoulder, waist and knee.
# Each entry is (left x, left y, right x, right y). The final edge follows
# the nearer knee, including the crouch, recoil and upside-down fall.
CUTS = (
    ((7, 9, 25, 10), (10, 20, 22, 21), (7, 32, 23, 30)),
    ((9, 10, 22, 10), (10, 20, 21, 20), (8, 31, 24, 32)),
    ((3, 8, 12, 10), (4, 20, 12, 20), (1, 32, 15, 29)),
    ((5, 9, 23, 10), (8, 19, 20, 20), (6, 32, 19, 29)),
    ((6, 9, 23, 9), (8, 19, 19, 20), (8, 28, 20, 31)),
    ((4, 9, 22, 10), (7, 19, 19, 20), (7, 29, 19, 32)),
    ((4, 9, 21, 10), (6, 19, 18, 20), (5, 32, 19, 29)),
    ((4, 10, 18, 10), (6, 20, 16, 20), (6, 31, 16, 29)),
    ((3, 10, 17, 10), (5, 20, 15, 20), (6, 32, 15, 30)),
    ((5, 10, 19, 10), (7, 20, 17, 20), (7, 30, 17, 32)),
    ((7, 10, 20, 10), (8, 20, 19, 20), (8, 30, 17, 33)),
    ((6, 9, 15, 10), (4, 20, 12, 20), (1, 31, 15, 29)),
    ((13, 8, 20, 9), (8, 19, 15, 20), (2, 31, 19, 33)),
    ((5, 9, 13, 10), (3, 21, 10, 22), (1, 32, 12, 30)),
    ((8, 9, 18, 10), (7, 20, 15, 20), (2, 32, 18, 29)),
    ((7, 12, 15, 11), (7, 21, 15, 21), (2, 33, 16, 30)),
    ((10, 11, 24, 11), (11, 17, 22, 18), (8, 24, 23, 23)),
    ((12, 14, 20, 12), (12, 19, 20, 16), (8, 25, 23, 21)),
    ((6, 10, 14, 10), (4, 20, 11, 21), (0, 30, 15, 31)),
    ((4, 9, 12, 10), (6, 21, 14, 21), (4, 31, 17, 32)),
    ((8, 10, 15, 10), (9, 21, 17, 20), (8, 31, 20, 31)),
    ((8, 9, 23, 8), (10, 20, 21, 20), (12, 32, 22, 28)),
    ((13, 10, 21, 11), (8, 19, 15, 20), (2, 31, 18, 28)),
    ((12, 7, 21, 9), (6, 14, 15, 17), (2, 25, 15, 23)),
    ((7, 9, 15, 11), (6, 20, 14, 21), (4, 31, 17, 30)),
    ((8, 13, 15, 14), (7, 24, 13, 24), (5, 34, 20, 34)),
    ((9, 15, 24, 16), (10, 25, 21, 26), (11, 36, 24, 33)),
    ((7, 18, 17, 10), (11, 21, 19, 14), (15, 29, 25, 19)),
    ((4, 9, 20, 9), (6, 19, 16, 20), (3, 25, 18, 25)),
)
# Registration of her lower body against his in the native cel. The fallen
# pose is painted upside up with both axes reversed, then returned to its cel.
FEMALE_OFFSETS = (
    (-1, 1), (0, 0), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (-1, 0), (0, 0), (0, 0),
    (0, 0), (0, 1), (0, 1), (0, 1), (0, 1), (0, 0), (0, 4), (0, 1), (0, 0), (0, 0),
    (0, 0), (0, 1), (0, 0), (0, 0), (0, 1), (0, 0), (0, 0), (0, 1), (0, 2),
)
REAR = {1, 7, 8, 9, 10, 18, 19, 20, 25, 28}
PROFILE = {2, 11, 12, 13, 14, 22, 23, 24}
# Foreground arm, from deltoid to elbow to wrist, in the turned poses.
# Shoulder fittings stop above this arm; short sleeves end at the deltoid.
ARMS = {
    2: ((9, 12), (10, 17), (15, 20)), 11: ((12, 12), (12, 17), (15, 20)),
    12: ((15, 11), (12, 15), (9, 18)), 13: ((8, 11), (4, 15), (3, 19)),
    14: ((16, 12), (17, 16), (22, 17)), 15: ((6, 14), (4, 18), (4, 20)),
    17: ((18, 16), (14, 19), (8, 21)), 18: ((12, 12), (10, 15), (14, 15)),
    19: ((9, 12), (8, 16), (5, 18)), 20: ((13, 12), (15, 16), (13, 18)),
    22: ((20, 13), (23, 15), (28, 15)), 23: ((18, 11), (19, 14), (22, 16)),
    24: ((9, 12), (10, 16), (14, 19)), 25: ((10, 16), (10, 19), (13, 18)),
    27: ((4, 17), (2, 19), (5, 22)),
}
# Shoulder, elbow and wrist in the feet-down retail cel. Follow both arms
# when visible, so that the flexed arm can cross in front of the rib cage.
# A profile with a wholly hidden far arm has just one contour to shade.
ARM_CENTRES = (
    (((8, 10), (4, 13), (2, 18)), ((24, 10), (27, 14), (28, 18))),
    (((10, 11), (7, 12), (4, 16)), ((21, 10), (24, 13), (24, 16))),
    (((8, 10), (10, 15), (14, 19)),),
    (((6, 10), (3, 13), (2, 18)), ((21, 10), (24, 13), (26, 18))),
    (((6, 10), (3, 14), (2, 19)), ((21, 9), (23, 12), (24, 16))),
    (((5, 9), (3, 13), (2, 18)), ((21, 9), (23, 12), (24, 16))),
    (((5, 10), (3, 12), (2, 16)), ((20, 10), (22, 14), (24, 19))),
    (((5, 11), (3, 14), (3, 17)), ((17, 11), (18, 14), (19, 17))),
    (((5, 10), (3, 12), (2, 15)), ((16, 11), (19, 13), (21, 18))),
    (((6, 11), (3, 14), (2, 17)), ((18, 10), (19, 13), (19, 16))),
    (((9, 10), (5, 14), (2, 20)), ((18, 10), (20, 12), (20, 14))),
    (((11, 11), (12, 16), (15, 20)),),
    (((15, 10), (13, 13), (9, 16)), ((18, 9), (20, 11), (22, 11))),
    (((9, 11), (7, 15), (5, 18)), ((11, 10), (13, 12), (15, 14))),
    (((14, 11), (16, 15), (20, 18)),),
    (((7, 12), (5, 16), (4, 20)), ((13, 10), (15, 7), (18, 4))),
    (((12, 10), (9, 7), (6, 6)), ((23, 12), (26, 17), (29, 23))),
    (((18, 14), (15, 18), (9, 21)), ((15, 7), (11, 4), (6, 2))),
    (((12, 11), (11, 14), (15, 15)),),
    (((6, 10), (6, 14), (4, 18)), ((10, 8), (12, 7), (13, 5))),
    (((13, 11), (14, 15), (13, 17)), ((8, 11), (5, 11), (2, 11))),
    (((10, 10), (8, 6), (4, 8)), ((22, 10), (25, 14), (28, 18))),
    (((18, 11), (22, 14), (27, 15)),),
    (((18, 10), (19, 14), (23, 17)), ((12, 7), (10, 5), (8, 4))),
    (((9, 12), (11, 16), (15, 19)),),
    (((10, 15), (11, 18), (14, 18)),),
    (((11, 15), (8, 13), (3, 14)), ((21, 13), (25, 14), (29, 14))),
    (((4, 16), (2, 18), (3, 21)), ((13, 7), (17, 4), (22, 2))),
    (((7, 11), (4, 12), (2, 13)), ((18, 10), (20, 11), (22, 13))),
)

# Center and radii of the face/hair in the folded poses where the jaw
# overlaps the chest. Upright poses keep the native jaw above the neckline.
LOW_HEAD = {16: (16, 8, 5, 5), 17: (12, 12, 5, 5), 23: (21, 6, 4, 5),
            27: (7, 13, 5, 6), 28: (12, 6, 5, 5)}
SKIN = (129, 134, 133, 132, 131, 130, 144, 145, 146, 147, 148, 149, 151)
TEAL = (208, 69, 69, 70, 70, 71, 71, 40, 72, 73)
# These folds use fixed map colours. Regional leaf and hide midtones
# converge when the Loader prepares costumes for the desert palette.
CLOAK_LEAF = (208, 17, 188, 189, 53, 54, 55, 56, 57)
WRAP_TEAL = (208, 69, 70, 71, 40, 72, 73)
GLADIATOR_HIDE = (208, 204, 203, 207, 195, 179, 205, 196, 201, 168, 169)
LINEN = (208, 204, 207, 205, 92, 194, 206, 97, 121, 61, 199, 123, 125, 62, 63)
BONE = (207, 205, 194, 206, 121, 199, 62, 63)
TEAL_BONE = (208, 69, 70, 71, 40, 72, 73, 199)
BRONZE = (88, 90, 93, 95, 98, 100, 168, 169, 170)
STOCK = {16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 48, 49, 50, 51, 52, 194,
         202, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 254}


# The raised wrist can be higher than the forehead. Keep scalp shading
# intact while removing the metal cuffs on these parts of the silhouette.
HIGH_CUFF = {15: (16, 0, 20, 6), 16: (3, 4, 9, 10), 17: (5, 0, 10, 5),
             19: (12, 2, 16, 8), 21: (1, 4, 8, 9), 23: (1, 3, 8, 8),
             26: (0, 11, 6, 17), 27: (19, 0, 24, 5)}
# Outer point of the working shoulder. The cap flattens around the
# deltoid, turning edge-on in profile. The far shoulder is occluded on 17.
GUARD = ((8, 10), (21, 11), (8, 11), (7, 10), (7, 10), (6, 10), (6, 10), (16, 11),
         (15, 11), (17, 11), (19, 11), (12, 11), (15, 10), (9, 11), (16, 11),
         (7, 14), (10, 10), None, (12, 12), (11, 11), (14, 12), (8, 10),
         (19, 12), (17, 11), (9, 11), (10, 16), (9, 12), (15, 9), (18, 11))


# Anchor of the woman's Gladiator strap on the upper arm in each pose.
WOMAN_GUARD = (
    (7, 9), (23, 10), (8, 11), (6, 9), (5, 11),
    (6, 9), (6, 9), (18, 10), (17, 10), (19, 10),
    (20, 10), (11, 11), (13, 10), (7, 11), (15, 11),
    (7, 12), (10, 7), None, (10, 12), (10, 10),
    (11, 12), (7, 9), (18, 10), (19, 9), (9, 11),
    (8, 16), (8, 13), (13, 8), (20, 10),
)

# Midpoint of each sole on its last visible scanline, in the same upright
# coordinates as CUTS. Trace the lifted foot separately from the planted one.
SOLES = (
    ((7, 39), (20, 34)), ((9, 33), (22, 38)), ((4, 39), (14, 31)),
    ((8, 38), (17, 31)), ((8, 30), (17, 38)), ((9, 32), (18, 38)),
    ((8, 38), (16, 30)), ((7, 37), (14, 32)), ((8, 40), (13, 30)),
    ((8, 32), (15, 37)), ((10, 30), (15, 40)), ((4, 37), (10, 33)),
    ((4, 33), (19, 37)), ((1, 32), (7, 39)), ((4, 37), (18, 31)),
    ((2, 40), (14, 35)), ((9, 31), (22, 25)), ((7, 29), (22, 22)),
    ((2, 31), (15, 37)), ((5, 33), (18, 37)), ((9, 33), (23, 37)),
    ((14, 40), (23, 32)), ((2, 37), (13, 30)), ((2, 32), (12, 26)),
    ((6, 38), (17, 33)), ((6, 35), (19, 41)), ((14, 46), (24, 38)),
    ((16, 33), (26, 25)), ((3, 28), (17, 28)),
)


# Last locks visible over her near shoulder. Retail uses the same charcoal
# indices for hair shadow and metal. Protect these native scanlines before
# replacing the harness or outlining the body. Coordinates are hers.
PROFILE_LOCKS = {
    2: (9, ((4, 10), (3, 6), (3, 5), (3, 4), (3, 3), (3, 3))),
    11: (9, ((4, 12), (4, 9), (3, 8), (3, 7), (4, 6))),
    12: (8, ((5, 17), (6, 15), (7, 11), (8, 9), (8, 8))),
    13: (9, ((3, 11), (3, 6), (2, 5), (2, 3))),
    14: (9, ((4, 15), (5, 14), (7, 13), (8, 11))),
}


def sandal(x, y, soles, across):
    for toe, bottom in soles:
        rise = bottom - y
        offset = x - toe
        if not (0 <= rise <= 4 and abs(offset) <= 4):
            continue
        if rise == 0:
            return 88
        # Hide sole, an open instep, and a slanted ankle tie.
        if rise == 1 or rise == 3 + (offset >= 0):
            return 95 if across < .48 and rise > 1 else 90
    return None


def mix(a, b, t):
    return a + (b - a) * t


def section(cut, u):
    a, b, c, d = cut
    return mix(a, c, u), mix(b, d, u)


def fabric_coords(x, y, top, bottom):
    """Inverse ruled quadrilateral, including the sloping edges of a bent torso."""
    def projected(u):
        ax, ay = section(top, u)
        bx, by = section(bottom, u)
        t = (y-ay) / max(1, by-ay)
        return mix(ax, bx, t), t

    left, lt = projected(0)
    right, rt = projected(1)
    if x < left or x > right:
        return (-1, lt) if x < left else (2, rt)
    lo, hi = 0.0, 1.0
    for _ in range(6):
        mid = (lo+hi)*0.5
        if projected(mid)[0] < x:
            lo = mid
        else:
            hi = mid
    u = (lo+hi)*0.5
    return u, projected(u)[1]


def arm_distance(x, y, points):
    best = 99
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        dx, dy = bx-ax, by-ay
        t = max(0, min(1, ((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
        best = min(best, math.hypot(x-ax-t*dx, y-ay-t*dy))
    return best


def pigment(ramp, level):
    return ramp[max(0, min(len(ramp)-1, round(level)))]


def upright(rows):
    return [r[::-1] for r in rows[::-1]]


def row_limits(panel):
    spans = {}
    for x, y in panel:
        left, right = spans.get(y, (x, x))
        spans[y] = min(left, x), max(right, x)
    return spans


def rear_cloak_color(x, y, pose, texture):
    # Follow the two gathers at the shoulder blades into unequal folds at
    # the hem. Sample in garment coordinates so the grain travels with them.
    (left, right, neck), (hem_left, hem_right, hem) = REAR_FOLD_GUIDES[pose]
    depth = max(0, min(1, (y-neck)/(hem-neck)))
    loft = math.sin(math.pi*depth)
    start = mix(left, hem_left, depth) + 1.3*loft
    end = mix(right, hem_right, depth) - 1.2*loft
    u = (x-start)/max(1, end-start)
    # Upper light crosses the shoulder blades. Three uneven folds divide
    # below the gathers, following the sideways swing toward the hem.
    shade = 7.5 - 3.3*abs(u-.30) + 1.4*math.cos(4*u+depth)
    for crease, bend in ((.28, -.12), (.54, .07), (.79, .09)):
        dist = (u-crease-bend*loft)*(end-start)
        shade -= 4.1*math.exp(-.48*dist*dist)
        shade += 2.3*math.exp(-.37*(dist+1.7)**2)
    across = round(x-start)
    grain = texture[round(y-neck) % 8][across % 8]
    # Narrow ridges beside the troughs stay a distinct value when this
    # outer layer is dyed for a worn cloak or a multiclass lining.
    return .66*(shade + 1.05*grain)


def dress(pieces, source, model, pose, dx, dy, bow, texture, visible):
    """Lay the pattern on the cleaned cel, then bring the near arm and hair forward."""
    female = model == 2074
    top, wrap, jerkin, robe, arm, hair, sleeve, belt = fitted_panels(pose, female)
    body = pieces["Body base"]
    shoulder, _, _ = CUTS[pose]
    guard = (WOMAN_GUARD if female else GUARD)[pose]
    outside = 1 if pose in REAR or pose in (17, 22, 23) else -1
    cap = shoulder_paint(model, pose)
    facing = jerkin_facing(model, pose)
    locks_start, locks = PROFILE_LOCKS.get(pose, (0, ())) if female else (0, ())
    rib_span = row_limits(top)
    cloak = stamp(RANGER_CLOAK[pose])
    cloak_span = row_limits(cloak)
    for role in ROLES[2:]:
        skirt = robe if role == "Cleric" else jerkin if role == "Fighter" else wrap
        if role == "Psionicist" and female and pose in WOMAN_TEAL_HEM:
            skirt = wrap | stamp((*belt, *reversed(WOMAN_TEAL_HEM[pose])))
        skirt_span = row_limits(skirt)
        hem = {}
        for x, y in skirt:
            hem[x] = max(hem.get(x, y), y)
        colors = LINEN if role == "Cleric" else RAMPS["hide"]
        shoulder_piece = {"Cleric": sleeve, "Fighter": cap.keys() | facing.keys(), "Gladiator": cap.keys(),
                          "Psionicist": set(), "Ranger": cloak}[role]
        for x, y in top | skirt | shoulder_piece:
            sx, sy = x+dx, y+dy
            if not (0 <= sy < len(body) and 0 <= sx < len(body[sy])):
                continue
            point = x, y
            c = source[sy][sx]
            # The hair outline encloses some exposed back between the locks.
            # Let the collar cover those skin pixels up to the actual strands.
            under_lock = (point in hair and role == "Ranger" and pose in REAR and point in cloak
                          and body[sy][sx] in (130, 131, 132, 144, 145, 146,
                                               147, 148, 149, 150, 151))
            on_guard = role in ("Gladiator", "Fighter") and point in cap and c is not None
            if on_guard and female:
                on_guard = c in range(130, 154)
            on_facing = role == "Fighter" and point in facing and body[sy][sx] in range(130, 154)
            if (point in hair and not under_lock and not on_guard and not on_facing) or (sx-5, sy) in bow:
                continue
            if 0 <= sy-locks_start < len(locks):
                left, right = locks[sy-locks_start]
                if left <= sx-5 <= right:
                    continue
            if pose in LOW_HEAD:
                cx, cy, rx, ry = LOW_HEAD[pose]
                if ((x-cx)/rx)**2+((y-cy)/ry)**2 <= 1:
                    continue
            if role == "Ranger" and point in cloak:
                # The front panels hang behind both arms. From the back,
                # hair, hands and the bent bow arm cross the cloth.
                exposed = c is None
                if pose in REAR:
                    exposed |= under_lock or point in top or point in sleeve or y >= belt[1][1]-2
                elif pose in PROFILE:
                    back_edge = rib_span.get(y, (belt[0][0],))[0]
                    exposed |= (x <= back_edge+2 and (point in top or point in robe))
                elif point in top:
                    neckline = min(shoulder[1], shoulder[3]) + 3
                    exposed |= y <= neckline or x < rib_span[y][0]+2
                if exposed and (point not in arm or c is None):
                    if pose in REAR:
                        shade = rear_cloak_color(x, y, pose, texture)
                    else:
                        lo, hi = cloak_span[y]
                        u = (x-lo+.5)/(hi-lo+1)
                        depth = (y-shoulder[1])/max(1, belt[1][1]-shoulder[1])
                        fold = 12*u + 1.4*depth + .65*math.sin(depth*2.4)
                        grain = texture[(y-shoulder[1]) % 8][int(16*u) % 8]
                        shade = 4.6 + 2.0*math.cos(fold) + .72*grain - 1.1*u
                    if (x,y+1) not in cloak or (x+1,y) not in cloak:
                        shade -= 2
                    if visible is not None:
                        visible["cloak"].add(point)
                    pieces[role][sy][sx] = pigment(CLOAK_LEAF, shade)
                    continue
            if role == "Cleric" and point in sleeve and c is not None:
                flesh = body[sy][sx]
                relief = SKIN.index(flesh) if flesh in SKIN else 2
                underside = (x, y+1) not in sleeve and (point not in top or point in arm)
                shade = 3.5 + .82*relief + .35*texture[y % 8][x % 8] - 2*underside
                if visible is not None:
                    visible["sleeve"].add(point)
                pieces[role][sy][sx] = pigment(LINEN, shade)
                continue
            if on_facing:
                pieces[role][sy][sx] = facing[point]
                continue
            if on_guard:
                if role == "Fighter" and visible is not None:
                    visible["guard"][point] = cap[point]
                pieces[role][sy][sx] = pigment(BONE if role == "Fighter" else BRONZE, cap[point])
                continue
            if point in arm and c is not None:
                continue
            if point not in top and point not in skirt:
                continue
            if point not in skirt and c is None:
                continue
            if pose == 17 and x >= 20 and y >= 21 and role != "Cleric":
                continue
            left, mid, right = belt
            at = min(1, max(0, (x-left[0])/max(1, right[0]-left[0])))
            edge = mix(left[1], mid[1], 2*at) if at < .5 else mix(mid[1], right[1], 2*at-1)
            lower = y >= round(edge) and point in skirt
            lo, hi = (skirt_span if lower or point not in top else rib_span)[y]
            u = (x-lo+.5)/max(1, hi-lo+1)
            shadow = abs(u-.38)
            grain = texture[(y-mid[1]) % 8][(x-mid[0]) % 8]
            if lower:
                t = (y-edge)/max(1, hem[x]-edge)
                # The free edge turns up at the leading knee. The lap line
                # originates at the hip and fans out into the hanging panel.
                if pose in PROFILE:
                    crease = .69-.22*t
                else:
                    crease = .34+.18*t
                fold = u-crease
                shade = 9-6*shadow + 2.3*math.cos(12*u-2*t)+.75*grain
                if -.075 < fold < .09:
                    shade += 3.2 if fold < 0 else -3.8
                if y == hem[x]:
                    shade -= 3
                if role == "Fighter" and .58 < u < .79 and t > .43:
                    shade -= 3
                color = pigment(colors, shade)
                if role == "Psionicist":
                    # The lower flap continues the wrap below the belt.
                    color = pigment(WRAP_TEAL, .4*shade + .20*grain)
                elif role == "Gladiator":
                    # The overlapping skirt has a turned-under leather edge
                    # against the thigh and a warm welt beside the lap seam.
                    hide = .66*shade - .7
                    if y == hem[x]:
                        # The near lip catches light against the shadowed
                        # thigh and turns underneath toward the far knee.
                        hide = (7.5 if .18 < u < .50 else 1) + .25*grain
                    elif x == hi:
                        hide = 1 + .25*grain
                    elif -.13 < fold < -.04 and y < hem[x]-1:
                        hide += 1.7
                    color = pigment(GLADIATOR_HIDE, hide)
                if y-edge < 1.5:
                    if role == "Gladiator":
                        belt_light = 4.8 + 2.6*(y-edge < .55) - 3*shadow
                        color = pigment(GLADIATOR_HIDE, belt_light + .55*grain)
                    else:
                        belt_light = 5 + 3*(y-edge < .55) - 4*shadow
                        color = pigment(RAMPS["hide"], belt_light+.65*grain)
                    if role == "Fighter" and abs(x-mid[0]+2) < 1:
                        color = 168
            elif role == "Gladiator":
                if guard is None:
                    continue
                # Run the strap from the actual bronze pin, across the
                # convex ribs, to the opposite edge of the shared waistband.
                gx, gy = guard
                t = min(1, max(0, (y-gy)/max(1, edge-gy)))
                end = left[0]+1 if outside == 1 else right[0]-1
                center = mix(gx, end, t) - outside*1.35*math.sin(math.pi*t)
                dist = x-center
                if abs(dist) > (1.0 if pose in PROFILE else 1.25):
                    continue
                # A lit welt on the raised pin-side edge and dark leather
                # beneath it keep the narrow strap distinct on warm skin.
                shade = (7 + 1.6*(t < .26) if dist < -.20 else .8) + .45*grain
                color = pigment(GLADIATOR_HIDE, shade)
            else:
                # Keep the light on the ribcage in the underlying cel.
                # Smooth leather changes plane more slowly than creased linen.
                skin = body[sy][sx]
                relief = SKIN.index(skin)-5 if skin in SKIN else -2
                t = (y-min(shoulder[1], shoulder[3]))/max(1, edge-min(shoulder[1], shoulder[3]))
                shade = 8.5-5*shadow+.53*relief+.68*grain
                seam = t-(.62-.40*u+.14*u*u)
                if -.12 < seam < .075:
                    shade += 3 if seam < -.01 else -3.5
                if role == "Cleric":
                    shade += 1.8*math.cos(11*u-2*t)
                color = pigment(colors, shade)
                if role == "Psionicist":
                    overlap = t - (.87-.72*u+.11*u*u)
                    turn = 2.0 if -.12 < overlap < 0 else -1.5 if 0 <= overlap < .10 else 0
                    # The wrap pulls diagonally toward the sash. A second,
                    # shorter crease starts below the blade, opening toward
                    # the near shoulder as the fitted panel widens.
                    tuck = t - (.20 + .38*u)
                    ridge = 0
                    if .12 < u < .72:
                        if -.11 < tuck < 0:
                            ridge = 1.15
                        elif 0 <= tuck < .12:
                            ridge = -1.05
                    color = pigment(WRAP_TEAL, .38*shade + .80*turn + .26*grain + ridge)
            pieces[role][sy][sx] = color
            if visible is not None and role in visible:
                visible[role].add(point)


# Horizontal swing and drop of the free leather end from its belt loop.
# Feet-down coordinates follow the cloth over the advancing thigh.
BELT_TAB = (
    (-1, 6), (1, 6), (-1, 5),
    (-1, 5), (0, 6), (1, 6), (-1, 5),
    (0, 5), (-1, 5), (1, 6), (2, 6),
    (-1, 5), (-3, 6), (-2, 5), (-2, 6),
    (-2, 6), (-1, 4), (-4, 6),
    (-2, 5), (1, 6), (2, 5),
    (1, 6), (-3, 5), (-2, 5),
    (-2, 6), (1, 6), (1, 5), (3, 4), (-1, 4),
)


def bone_caps(robe, linen, visible_sleeve, pose, dx, dy):
    for sleeve in SLEEVES[pose]:
        outline = stamp(sleeve)
        spans = row_limits(outline)
        crown = min(spans)
        for x, y in outline & visible_sleeve:
            left, right = spans[y]
            depth = y-crown
            # Leave linen around the seam and cuff. The plate follows the
            # widening sleeve and the light already painted on the upper arm.
            if not 1 <= depth <= 4 or not left < x < right:
                continue
            if depth == 4 and (x, y+2) not in outline:
                continue
            cloth = linen[y+dy][x+dx]
            shade = LINEN.index(cloth) * (len(BONE)-1) / (len(LINEN)-1)
            robe[y+dy][x+dx] = pigment(BONE, shade + .5 - .4*(depth-1))


def dress_pairs(pieces, visible, model, pose, dx, dy):
    # Coordinates here are the same feet-down sewing lines used for singles.
    # Only pixels actually laid down by the parent garment can take its trim.
    _, _, _, _, _, _, _, belt = fitted_panels(pose, model == 2074)
    left, middle, right = belt
    cloak = visible["cloak"]
    cloak_floor = {}
    for x, y in stamp(RANGER_CLOAK[pose]):
        cloak_floor[x] = max(y, cloak_floor.get(x, y))
    for pair in PAIRS:
        parent, accent = pair.split("/")
        out = [row[:] for row in pieces[parent]]
        pieces[pair] = out
        if pair == "Fighter/Psionicist":
            for (x, y), relief in visible["guard"].items():
                out[y+dy][x+dx] = TEAL_BONE[relief]
        if accent == "Fighter":
            bone_caps(out, pieces["Cleric"], visible["sleeve"], pose, dx, dy)
        if accent == "Ranger":
            facing = LINEN if parent == "Cleric" else TEAL
            for x, y in cloak:
                sy, sx = y+dy, x+dx
                green = pieces["Ranger"][sy][sx]
                # A turned edge of the lining peeks out at the lifted hem.
                # Preserve the outer shadow contour and the motion of every fold.
                depth = cloak_floor[x]-y
                if 1 <= depth <= 2 and x <= middle[0]+1:
                    relief = RAMPS["leaf"].index(green)/(len(RAMPS["leaf"])-1)
                    out[sy][sx] = pigment(facing, (len(facing)-1)*relief)
                else:
                    out[sy][sx] = green
            if parent == "Cleric" and pose == 24:
                # The swept cloak meets the longer linen hem in side bow.
                out[30+dy][2+dx] = LINEN[3]
            continue

        for x, y in visible[parent]:
            sy, sx = y+dy, x+dx
            u = max(0, min(1, (x-left[0])/max(1, right[0]-left[0])))
            waist = (mix(left[1], middle[1], 2*u) if u < .5
                     else mix(middle[1], right[1], 2*u-1))
            # The belt rides the hips; the teal wrap crosses the lower ribs.
            if accent == "Fighter":
                distance = y-waist+.5+.9*(u-.5)
                # The leather turns down at the hip and overlaps the linen.
                # The existing cloth mask brings crossing hands in front.
                if distance >= 1.9:
                    swing, drop = BELT_TAB[pose]
                    hip = middle[0] + (2 if pose in REAR else -2)
                    t = (distance-1)/(drop-1)
                    across = x - (hip + swing*t)
                    if distance > drop+.5 or abs(across) > (1 if t > .83 else 1.5):
                        continue
                    shade = 6 if across < 0 else 3
                    out[sy][sx] = pigment(RAMPS["hide"], shade + (t < .34) - (t > .83))
                    continue
                if distance < -1.2:
                    continue
                light = 5.7-4*abs(u-.35)+1.4*(distance < -.2)-2*(distance > .95)
                color = pigment(RAMPS["hide"], light)
                if abs(x-middle[0]+2) < 1 and distance < .9:
                    color = 168 if distance < -.1 else 95
            else:
                # In the low front strike the forearm covers the ribs and
                # the tied end of the wrap drops across the foremost hip.
                rise = {17: -2, 20: .7}.get(pose, 2.6)
                distance = y-waist+rise+2.9*(u-.5)
                if not -1.4 <= distance < 1.2:
                    continue
                ground = pieces[parent][sy][sx]
                ramp = LINEN if parent == "Cleric" else RAMPS["hide"]
                relief = ramp.index(ground)/len(ramp) if ground in ramp else .35
                light = 3.3 + 4.3*relief + 1.4*(distance < -.35) - 2*(distance > .65)
                color = pigment(TEAL, light)
            out[sy][sx] = color


# Rear poses reuse the harness just below the scalp. Each entry gives
# its first scanline and native x on the man and woman. The woman's
# longer locks fall on opposite sides of the neck as the shoulder turns.
NAPE = {1: (10, 12, 15), 7: (10, 7, 8), 8: (10, 6, 7), 9: (10, 8, 11),
        10: (10, 11, 11), 18: (10, 6, 6), 19: (10, 8, 9), 20: (10, 14, 14),
        25: (14, 11, 11)}


def clean_nape(pieces, model, pose, margin):
    top, man, woman = NAPE[pose]
    start = woman if model == 2074 else man
    # Keep the deepest shadow immediately under the hair. It tapers into
    # the warm half-light on the trapezius before the garment is drawn.
    for y, shades in ((top, (132, 130, 144, 132, 131, 134, 129, 134)),
                      (top+1, (145, 146, 145, 144, 130, 132, 134, 132))):
        for i, color in enumerate(shades):
            x = margin+start+i
            if x < len(pieces["Body base"][y]) and pieces["Body base"][y][x] in (208, 209, 254):
                for rows in pieces.values():
                    rows[y][x] = color


# Relief painted over the fitted rib cage. Each row runs from the near
# shoulder toward the far shoulder. Dividing at the actual waist lets the
# blade, sternum and flank compress with the strikes. Small broken masses
# leave a half-tone between the highlights and the occlusion shadows.
TORSO_RELIEF = {
    "front": (
        "...++....-...", "..++H+.-..+..", ".+HH++.-.+H+.",
        "..+++.-..++.-", "..--.=-..---.", "...=-+.--..--",
        "..++H+.-..+--", "..+..--....-.", "...--..-..--.",
        "...+H+..-....", "....++..-....",
    ),
    "rear": (
        "...+H+.-.++..", "..+HH+-..+H+.", ".+HH+.-..+++.",
        "..++..=...+--", "..+..-=..+--.", "...-=.-.+--..",
        "..+H+.-..--..", "..++..-..+--.", "....--...++-.",
        "...+H+..-....", "....+..--....",
    ),
    "profile": (
        "..++H+..-....", "..+HH+...--..", "...++..--....",
        "..++..--...+.", "..+..-=..++..", "...-=-..+H+..",
        "..+++-..+--..", "..+.....--...", "..+H+..--....",
        "...++..-.....", ".....--......",
    ),
}
SKIN_RELIEF = {".": 0, "+": 2, "H": 4, "-": -2, "=": -4}


def arm_planes(pose):
    # Cross-sections run from the underside to the key light at upper left.
    # The short undercut ends at the elbow; the smaller forearm light narrows
    # independently toward the wrist, including when the arm is horizontal.
    upper = ((-1, 1, 2), (-3, 2, 4), (-3, 1, 3), (-2, -2, 1))
    lower = ((-2, -1, 2), (-3, 2, 3), (-2, 1, 3), (-1, 0, 1))
    cells = {}
    distance = {}
    for joints in ARM_CENTRES[pose]:
        for segment, ((ax, ay), (bx, by)) in enumerate(zip(joints, joints[1:])):
            dx, dy = bx-ax, by-ay
            length = math.hypot(dx, dy)
            sign = 1 if dx > dy else -1
            for y in range(min(ay, by)-2, max(ay, by)+3):
                for x in range(min(ax, bx)-2, max(ax, bx)+3):
                    t = ((x-ax)*dx+(y-ay)*dy)/(length*length)
                    if not 0 <= t < 1:
                        continue
                    across = sign*((x-ax)*dy-(y-ay)*dx)/length
                    width = 1.85-.6*t if segment else 1.75+.35*math.sin(math.pi*t)
                    if abs(across) > min(width, distance.get((x, y), width)):
                        continue
                    distance[x, y] = abs(across)
                    bank = 0 if across < -.30 else 2 if across > .50 else 1
                    cells[x, y] = (lower if segment else upper)[int(4*t)][bank]
    return cells


def leg_relief(x, y, across, width, waist, soles, rear):
    # Each thigh and knee follows its own sole. A visible gap gives the limb
    # its real width; when the thighs overlap, divide at the two hip centres.
    best = None
    for i, (toe, bottom) in enumerate(soles):
        hip, top = section(waist, (.23, .76)[i])
        depth = (y-top)/max(1, bottom-top)
        if not .12 < depth < .92:
            continue
        center = mix(hip, toe, depth)
        dist = abs(x-center)
        if dist < 4.5 and (best is None or dist < best[0]):
            best = (dist, center, depth)
    if best is None:
        return 0
    _, center, depth = best
    plane = across if width < 9 else .5 + (x-center)/7
    if depth < .48:
        # The quadriceps narrows toward the inside of the knee.
        crest = .24+.30*depth
        if abs(plane-crest) < .14:
            return 3
        if .59 < plane < .84:
            return -2
    elif depth < .65:
        # The knee catches a short light in front and folds into a crease
        # behind. The outside of the joint rolls into the upper calf.
        if .23 < plane < .55 and depth < .57:
            return -2 if rear else 4
        if .47 < plane < .85:
            return -4
    else:
        # A fuller calf gives way to a thin shin/tendon light. End it before
        # the sandal strap; the two feet reach this point on separate beats.
        crest = .32 + .16*(depth-.65)/.27
        if abs(plane-crest) < (.17 if depth < .78 else .12):
            return 4 if depth < .78 else 3
        if .59 < plane < .84 and depth < .86:
            return -3
    return 0


def study_rows(game, model, pose, texture, *, pairs=False, panels=None):
    combat, frame = divmod(pose, 15)
    fig = game.fig(model)
    native = fig.rows(combat, frame)
    # Room beyond the stock cel for the swinging hem. Symmetric margins
    # preserve the original ground anchor in every gallery tile.
    margin = 5
    original = [[None]*margin + list(r) + [None]*margin for r in native]
    reverse = pose == 28
    source = upright(original) if reverse else original
    dx, dy = FEMALE_OFFSETS[pose] if model == 2074 else (0, 0)
    dx += margin
    shoulder, waist, knee = CUTS[pose]
    soles = SOLES[pose]
    if model == 2074 and pose == 27:
        soles = ((16, 34), soles[1])
    bow = game.bow(fig, native, fig.parts(combat, frame)) if 24 <= pose <= 26 else set()
    pieces = {role: [r[:] for r in source] for role in ROLES[1:]}
    locks_start, locks = PROFILE_LOCKS.get(pose, (0, ())) if model == 2074 else (0, ())
    skin_relief = {}
    locks_outline = fitted_panels(pose, model == 2074)[5]
    native_hair = fig.parts(combat, frame).hair
    torso = TORSO_RELIEF["rear" if pose in REAR else "profile" if pose in PROFILE else "front"]
    for sy, row in enumerate(source):
        lock = locks[sy-locks_start] if 0 <= sy-locks_start < len(locks) else None
        # Each contiguous leg/arm has its own light plane; a gap keeps its
        # native width even when the far leg crosses behind the near one.
        runs = []
        for sx, color in enumerate(row):
            if color is None:
                continue
            if sx == 0 or row[sx-1] is None:
                runs.append([sx, sx])
            runs[-1][1] = sx
        for left, right in runs:
            for sx in range(left, right+1):
                x, y = sx-dx, sy-dy
                c = row[sx]
                if lock and lock[0] <= sx-margin <= lock[1]:
                    continue
                u, t = fabric_coords(x, y, shoulder, waist)
                v, h = fabric_coords(x, y, waist, knee)
                in_top = 0 <= u <= 1 and 0 <= t < 1
                in_lower = 0 <= v <= 1 and 0 <= h
                neck = section(shoulder, max(0, min(1, u)))[1]
                cuff = HIGH_CUFF.get(pose)
                raised = cuff and cuff[0] <= x <= cuff[2] and cuff[1] <= y <= cuff[3]
                if (y < neck-1 and not raised) or (sx-margin, sy) in bow:
                    continue
                if pose in LOW_HEAD:
                    cx, cy, rx, ry = LOW_HEAD[pose]
                    if ((x-cx)/rx)**2+((y-cy)/ry)**2 <= 1:
                        continue
                if model == 2074 and y < neck+7 and c in (128, 129, 179, 180, 181):
                    continue
                if in_top and t < 0.17*(1-abs(2*u-1)):
                    continue
                near_arm = pose in ARMS and arm_distance(x, y, ARMS[pose]) <= 1.8
                across = (sx-left+.4)/(right-left+1)
                body = c
                deep = c in (128, 129) and (in_lower or in_top and t > .30)
                if c in STOCK or deep:
                    if in_top and not near_arm:
                        body = elf.torso_skin(2*u-1, t, pose in REAR, pose in PROFILE)
                        if pose not in REAR | PROFILE and model == 2074:
                            bust = min(((u-.30)/.24)**2+((t-.37)/.21)**2,
                                       ((u-.73)/.22)**2+((t-.39)/.20)**2)
                            if bust < 1:
                                body = 146 if t < .38 and u < .75 else 144
                            elif bust < 1.55 and t > .40:
                                body = 132
                    else:
                        ridge = abs(across-0.34)
                        grain = ((sx+2*sy) % 5 == 1)-((sx+sy) % 4 == 0)
                        body = pigment(SKIN, 8.8-16*ridge+grain-1.6*(y > knee[1]))
                # Keep the warm highlight on the upper-left plane. The
                # shadow side and underside meet the sand in a broken outline.
                below = sy+1 == len(source) or source[sy+1][sx] is None
                if sx == right or below:
                    body = 88 if below and (sx == right or across > .45) else 129
                elif sx == left and (c in STOCK or deep):
                    body = 134
                elif right-sx == 1 and body in SKIN:
                    body = SKIN[max(0, SKIN.index(body)-3)]
                if (pose in REAR and in_top and not near_arm and .14 < t < .70
                        and body in SKIN and sx not in (left, right)):
                    # Two scapular planes turn away from the spine, visible
                    # beneath the diagonal strap. Leave the neck and hair free.
                    blade = abs(abs(2*u-1)-(.48-.17*t))
                    if blade < .17:
                        body = SKIN[min(len(SKIN)-1, SKIN.index(body)+2)]
                    elif abs(u-.54) < .07:
                        body = SKIN[max(0, SKIN.index(body)-2)]
                if in_top and not near_arm and body in SKIN and sx not in (left, right):
                    # Reflected light below the ribs rolls into a short flank
                    # shadow. Keep the established outer limb and calf contour.
                    flank = t - (.65 - .26*u)
                    tone = SKIN.index(body)
                    if .28 < u < .81 and 0 <= flank < .12:
                        body = pigment(SKIN, tone - 2)
                    elif .20 < u < .49 and -.12 < flank < 0:
                        body = pigment(SKIN, tone + 1)
                native_point = ((len(native[0])-1-(sx-margin), len(native)-1-sy)
                                if reverse else (sx-margin, sy))
                if (body in SKIN and left < sx < right and not near_arm
                        and (x, y) not in locks_outline and native_point not in native_hair):
                    relief = 0
                    if in_top:
                        relief = SKIN_RELIEF[torso[min(10, int(t*11))][min(12, int(u*13))]]
                    elif y >= min(waist[1], waist[3]):
                        relief = leg_relief(x, y, across, right-left+1, waist, soles, pose in REAR)
                    if relief:
                        skin_relief[sx, sy] = pigment(SKIN, SKIN.index(body)+relief)
                foot = sandal(x, y, soles, across)
                # In these two crossing profile steps the back foot lies
                # directly beside the planted shin. Only its toes take a sole.
                if (pose == 11 and x <= 6 and 29 <= y <= 32
                        or pose == 13 and x >= 4 and 28 <= y <= 32):
                    foot = None
                pieces["Body base"][sy][sx] = body
                for role in ROLES[2:]:
                    pieces[role][sy][sx] = body if foot is None else foot
    # Raised arms and horizontal bow arms can sit above the neckline. Sample
    # them on the completed body so the restored cuffs join the native biceps.
    for (x, y), shift in arm_planes(pose).items():
        sx, sy = x+dx, y+dy
        if not (0 < sy < len(source)-1 and 0 < sx < len(source[sy])-1):
            continue
        old = pieces["Body base"][sy][sx]
        if (not shift or old not in SKIN or (x, y) in locks_outline
                or source[sy][sx-1] is None or source[sy][sx+1] is None):
            continue
        nx, ny = sx-margin, sy
        if reverse:
            nx, ny = len(native[0])-1-nx, len(native)-1-ny
        if (nx, ny) in native_hair or (nx, ny) in bow:
            continue
        if pose in LOW_HEAD:
            cx, cy, rx, ry = LOW_HEAD[pose]
            if ((x-cx)/rx)**2+((y-cy)/ry)**2 <= 1:
                continue
        elif shoulder[0]+1 <= x <= shoulder[2]-1 and y <= min(shoulder[1], shoulder[3]):
            continue
        # The donor already lights exposed upper-arm skin. Use the stronger
        # turn only over a removed retail cuff or a reconstructed shoulder.
        if source[sy][sx] in SKIN and abs(shift) > 1:
            shift += -1 if shift > 0 else 1
        skin_relief[sx, sy] = pigment(SKIN, SKIN.index(old)+shift)
    if pose in NAPE:
        clean_nape(pieces, model, pose, margin)
    visible = ({"Cleric": set(), "Fighter": set(), "cloak": set(), "sleeve": set(), "guard": {}}
               if pairs else None)
    dress(pieces, source, model, pose, dx, dy, bow, texture, visible)
    # The clothes already carry their own approved fold lighting. Apply the
    # anatomical relief only where a cel still exposes the underlying skin.
    light = [(.299*r + .587*g + .114*b) for r, g, b in game.palette]
    gladiator = pieces["Gladiator"]
    for (sx, sy), color in skin_relief.items():
        old_skin = pieces["Body base"][sy][sx]
        # Preserve the small lit plane beside a dark welt when the deeper
        # flank shadow would join its value. The same plane belongs to the
        # undressed torso and travels with it beneath the other outfits.
        if gladiator[sy][sx] == old_skin:
            leather = (gladiator[yy][xx] for xx, yy in
                       ((sx-1, sy), (sx+1, sy), (sx, sy-1), (sx, sy+1))
                       if 0 <= yy < len(gladiator) and 0 <= xx < len(gladiator[yy]))
            if any(p in GLADIATOR_HIDE and abs(light[color]-light[p]) <
                   min(40, abs(light[old_skin]-light[p])) for p in leather):
                continue
        for rows in pieces.values():
            if rows[sy][sx] == old_skin:
                rows[sy][sx] = color
    if pairs:
        dress_pairs(pieces, visible, model, pose, dx, dy)
        if panels is not None:
            panels.update(visible)
    return {"Original": original, **{role: upright(rows) if reverse else rows for role, rows in pieces.items()}}


def render(game_dir, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    texture = reference_folds(game)["linen"]
    floor = Image.open(TERRAIN).convert("RGB").crop((45, 144, 99, 195))
    atlas.floor = floor
    frames = []
    sheets = {model: Image.new("RGB", (3*len(ROLES)*108, 10*148), dwarf.PAPER) for model in MODELS}
    output.mkdir(parents=True, exist_ok=True)
    for pose, name in enumerate(dwarf.NAMES):
        page = Image.new("RGB", (80+119*len(ROLES), 522), dwarf.PAPER)
        label(page, (12, 7), "Half-giant outfit study", 19)
        label(page, (page.width-12, 10), f"{pose:02}   {name}", 14, "ra")
        for j, role in enumerate(ROLES):
            label(page, (80+j*119, 42), role, 14)
        for i, model in enumerate(MODELS):
            rows = study_rows(game, model, pose, texture)
            y = 62+i*155
            label(page, (9, y+58), ("Man", "Woman")[i], 13)
            for j, role in enumerate(ROLES):
                native = elf.placed_tile(game, rows[role], floor, 1, 0, 0, 0)
                tile = native.resize((108, 102), Image.Resampling.NEAREST)
                page.paste(tile, (80+j*119, y))
                page.paste(native, (106+j*119, y+104))
                sheet = sheets[model]
                px = (pose % 3*len(ROLES)+j)*108
                py = pose//3*148
                sheet.paste(tile, (px, py+44))
                if j == 0:
                    label(sheet, (px+3, py+2), f"{pose:02}   {name}", 14)
                label(sheet, (px+3, py+23), role, 12)
        label(page, (10, 395), "Scale references", 13)
        for j, (caption, npc) in enumerate((("Retail Warrior", 1252), ("Retail Priest", 1563))):
            pic = npc+pose//15
            if pose % 15 < game.count(pic):
                rows = game.fr(pic, pose % 15)
            else:
                rows = game.fr(npc, 0)
                caption += " (idle)"
            native = elf.placed_tile(game, rows, floor, 1, 0, 0, 0)
            page.paste(native, (137+142*j, 408))
            label(page, (164+142*j, 466), caption, 13, "ma")
        tile = atlas.tile(300, pose, "Gladiator", "Class colors", 1)
        page.paste(tile, (422, 459-tile.height))
        label(page, (448, 466), "Human Gladiator", 13, "ma")
        for j, role in enumerate(("Psionicist", "Ranger")):
            reference = atlas.tile(300, pose, role, "Class colors", 1)
            x = 555+142*j
            page.paste(reference, (x, 459-reference.height))
            label(page, (x+27, 466), "Human "+role, 13, "ma")
        label(page, (10, 499), "Each half-giant appears at 2× and at game size. References are at game size.", 12)
        frames.append(page)
    loop(frames, output/"half-giant-study.gif")
    for model, sheet in sheets.items():
        sex = "man" if model == 2072 else "woman"
        sheet.save(output/f"half-giant-{sex}-poses.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
