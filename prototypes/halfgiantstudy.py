"""Render an art study on the two retail half-giants. Run with GAME_DIR OUTPUT_DIR."""
import argparse
import math
from pathlib import Path

from PIL import Image

from halfgiantfit import RANGER_CLOAK, REAR_FOLD_GUIDES, SLEEVES, fitted_panels, stamp
from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas

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
# Center and radii of the face/hair in the folded poses where the jaw
# overlaps the chest. Upright poses keep the native jaw above the neckline.
LOW_HEAD = {16: (16, 8, 5, 5), 17: (12, 12, 5, 5), 23: (21, 6, 4, 5),
            27: (7, 13, 5, 6), 28: (12, 6, 5, 5)}
SKIN = (129, 134, 133, 132, 131, 130, 144, 145, 146, 147, 148, 149, 151)
TEAL = (208, 69, 69, 70, 70, 71, 71, 40, 72, 73)
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


# Woman's shoulder pin in the fitted pose, traced from the visible upper
# arm. The third coordinate is the direction the lower lip rolls. Hair and
# the raised wrist hide the plate in the second rear strike.
WOMAN_GUARD = (
    (7, 9, -1), (23, 10, 1), (8, 11, 0), (6, 9, -1), (5, 11, -1),
    (6, 9, -1), (6, 9, -1), (18, 10, 1), (17, 10, 1), (19, 10, 1),
    (20, 10, 1), (11, 11, 0), (13, 10, -1), (7, 11, -1), (15, 11, 1),
    (7, 12, -1), (10, 7, -1), None, (10, 12, -1), (10, 10, 1),
    (11, 12, 1), (7, 9, -1), (18, 10, 1), (19, 9, 1), (9, 11, 1),
    (8, 16, 0), (8, 13, -1), (13, 8, 1), (20, 10, 1),
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
    # Upper light crosses the shoulder blades. Below them two narrow
    # troughs frame the broad lit face of the hanging cloth.
    shade = 7.5 - 3.3*abs(u-.30) + 1.4*math.cos(4*u+depth)
    for crease, bend in ((.28, -.12), (.73, .09)):
        dist = (u-crease-bend*loft)*(end-start)
        shade -= 4.1*math.exp(-.48*dist*dist)
        shade += 2.3*math.exp(-.37*(dist+1.7)**2)
    across = round(x-start)
    grain = texture[round(y-neck) % 8][across % 8]
    return shade + .68*grain


def dress(pieces, source, model, pose, dx, dy, bow, texture, visible):
    """Lay the pattern on the cleaned cel, then bring the near arm and hair forward."""
    female = model == 2074
    top, wrap, jerkin, robe, arm, hair, sleeve, belt = fitted_panels(pose, female)
    body = pieces["Body base"]
    shoulder, _, _ = CUTS[pose]
    guard = GUARD[pose]
    if female:
        fit = WOMAN_GUARD[pose]
        guard = fit[:2] if fit else None
    # A compact, sloped cap cups the upper arm. Its downturned lip is on
    # the outer side and the inboard end hides the start of the strap.
    outside = 1 if pose in REAR or pose in (17, 22, 23) else -1
    cap = {}
    if female and guard:
        gx, gy, lean = WOMAN_GUARD[pose]
        if pose != 19:
            # A short highlight over the deltoid, then the half-tone and
            # narrow shadow lip. Rotate the lip as the upper arm swings.
            for depth, strip in enumerate(("56", "4574", "234", "12")):
                left = gx - len(strip)//2 + (lean if depth >= 2 else 0)
                for col, shade in enumerate(strip):
                    cap[left+col, gy+depth-1] = int(shade)
    elif guard:
        gx, gy = guard
        for depth, (start, end) in enumerate(((-1, 1), (-2, 2), (-1, 2), (1, 2))):
            for side in range(start, end+1):
                x, y = gx+outside*side, gy+depth-1
                cap[x, y] = 6-depth*1.4-.5*side
    locks_start, locks = PROFILE_LOCKS.get(pose, (0, ())) if female else (0, ())
    rib_span = row_limits(top)
    cloak = stamp(RANGER_CLOAK[pose])
    cloak_span = row_limits(cloak)
    for role in ROLES[2:]:
        skirt = robe if role == "Cleric" else jerkin if role == "Fighter" else wrap
        skirt_span = row_limits(skirt)
        hem = {}
        for x, y in skirt:
            hem[x] = max(hem.get(x, y), y)
        colors = LINEN if role == "Cleric" else RAMPS["hide"]
        shoulder_piece = {"Cleric": sleeve, "Fighter": cap.keys(), "Gladiator": cap.keys(),
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
            if (point in hair and not under_lock and not on_guard) or (sx-5, sy) in bow:
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
                        shade = 6.8 + 2.8*math.cos(fold) + .65*grain - 1.4*u
                    if (x,y+1) not in cloak or (x+1,y) not in cloak:
                        shade -= 3.1
                    if visible is not None:
                        visible["cloak"].add(point)
                    pieces[role][sy][sx] = pigment(RAMPS["leaf"], shade)
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
                    color = pigment(TEAL, .56*shade+.45)
                if y-edge < 1.5:
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
                color = pigment(RAMPS["hide"], (10 if dist < -.20 else 3)+.45*grain)
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
                    color = pigment(TEAL, .55*shade+turn+.5)
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


def bone_caps(robe, visible_sleeve, pose, dx, dy):
    # The sleeve patterns turn with each upper arm. A short domed plate
    # sits inside each sleeve, with its lower rim above the linen cuff.
    for sleeve in SLEEVES[pose]:
        spans = row_limits(stamp(sleeve))
        crown = min(spans)
        for depth, width in enumerate((3, 5, 5, 3), start=1):
            y = crown + depth
            left, right = spans[y]
            center = (left+right)//2
            for x in range(center-width//2, center+width//2+1):
                if (x, y) not in visible_sleeve:
                    continue
                across = x-center
                shade = 6 - abs(across) - (across > 0) - (depth == 3)
                if depth == 4:
                    shade = 1 if across < 0 else 0
                robe[y+dy][x+dx] = BONE[shade]


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
                out[y+dy][x+dx] = TEAL_BONE[int(relief + .5)]
        if accent == "Fighter":
            bone_caps(out, visible["sleeve"], pose, dx, dy)
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


def study_rows(game, model, pose, texture, *, pairs=False):
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
                foot = sandal(x, y, soles, across)
                # In these two crossing profile steps the back foot lies
                # directly beside the planted shin. Only its toes take a sole.
                if (pose == 11 and x <= 6 and 29 <= y <= 32
                        or pose == 13 and x >= 4 and 28 <= y <= 32):
                    foot = None
                pieces["Body base"][sy][sx] = body
                for role in ROLES[2:]:
                    pieces[role][sy][sx] = body if foot is None else foot
    if pose in NAPE:
        clean_nape(pieces, model, pose, margin)
    visible = ({"Cleric": set(), "Fighter": set(), "cloak": set(), "sleeve": set(), "guard": {}}
               if pairs else None)
    dress(pieces, source, model, pose, dx, dy, bow, texture, visible)
    if pairs:
        dress_pairs(pieces, visible, model, pose, dx, dy)
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
