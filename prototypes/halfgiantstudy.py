"""Render an art study on the two retail half-giants. Run with GAME_DIR OUTPUT_DIR."""
import argparse
import math
from pathlib import Path

from PIL import Image

from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas

MODELS = (2072, 2074)
ROLES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
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
LINEN = (208, 204, 207, 205, 92, 194, 206, 97, 121, 61, 199, 123, 125, 62, 63)
BONE = (207, 205, 194, 206, 121, 199, 62, 63)
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
         (19, 12), (17, 11), (9, 11), (10, 16), (8, 16), (15, 9), (18, 11))


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


def garment(role, u, t, lower, profile, rear, texture):
    """Work from the cloth grain, with the warp running shoulder to hip."""
    wrap = 1 - abs(2*u-0.85)
    grain = math.floor(u*(9 if profile else 15))
    height = math.floor(t*12)
    relief = texture[height % 8][grain % 8]
    fold = math.sin(grain*1.24 + 2.1*t + (0.8 if rear else 0) + 0.9*u*t)
    if role == "Cleric" and not lower:
        fold = math.cos(10*t-5*u) * (0.7+0.3*u)
    shade = 5.8 + 3*wrap + 2.2*fold + 0.7*relief
    # A lapped edge catches the light above the darker return. It bends
    # with the wearer, so the highlight travels with the same piece of hide.
    if role == "Cleric":
        shade += 1.4*fold + 0.4*relief
        # The cream changes to warm brown where the pleat turns away from
        # the shoulder. Leave the outer fold light enough to read on sand.
        if not lower:
            gather = t - (.70 - .46*u + .12*math.sin(4*u))
            if -.07 < gather < .11:
                shade += 3 if gather < 0 else -3.5
        if lower:
            pleat = u - (0.32 + 0.16*t*t)
            if abs(pleat) < .055:
                shade += 3.5 if pleat < 0 else -4
    else:
        shade += 1.2*fold + 0.45*relief
    if min(u, 1-u) < 0.08:
        shade -= 3
    if lower:
        hem = 0.43 if role == "Gladiator" else 0.55 if role == "Fighter" else 1
        if role == "Gladiator" and (rear or profile):
            hem -= .13
        hem += 0.08*math.sin(u*5.5+0.6) - (0.1 if profile else 0)*u
        if t > hem:
            return None
        if t < 0.09+0.08*math.sin(u*2.8):
            if role == "Fighter":
                # The lower welt of the jerkin sits over a dark sword belt.
                if .28 < u < .41:
                    return 168 if t < .07 else 95
                return pigment(RAMPS["hide"], (11 if t < .045 else 2)+2*wrap+relief*.45)
            return pigment(RAMPS["hide"], 3+4*wrap+relief)
        if t > hem-0.09:
            shade -= 3
        if role == "Cleric" and t > 0.70 and u > 0.69:
            shade -= 2.2
        if role != "Cleric":
            lap = u-(.62-.44*t)
            if -.08 < lap < .10:
                shade += 5 if lap < 0 else -4
            if hem-.16 < t <= hem-.08 and .09 < u < .60:
                shade += 3
        if role == "Gladiator":
            shade += 1.8*math.cos(grain*1.1-t*2)
        return pigment(LINEN if role == "Cleric" else RAMPS["hide"], shade)
    neckline = (0.15 if rear else 0.30)*(1-abs(2*u-1))
    if t < neckline:
        return None
    if role == "Gladiator":
        center = (0.80-0.66*t) if rear else (0.18+0.66*t)
        distance = u-center
        half_width = .065 if rear else .105 if profile else .10
        if abs(distance) > half_width:
            return None
        return pigment(RAMPS["hide"], (11 if distance < -.035 else 3)+.65*relief)
    if role == "Fighter" and t < 0.22 and (u < 0.23 or u > 0.80):
        return pigment(BONE, 2+2.8*(1-t/.22)+0.45*relief)
    if role == "Fighter":
        seam = t - (.70 - .42*u + .09*u*u)
        if -.10 < seam < .08:
            return pigment(RAMPS["hide"], (12 if seam < -.01 else 2)+wrap+.5*relief)
        if .12 < u < .25 and t < .63:
            shade += 2.5
        lip = u - (.22 + .15*t*t)
        if -.065 < lip < .045 and .28 < t < .88:
            shade += 4 if lip < 0 else -4
    return pigment(LINEN if role == "Cleric" else RAMPS["hide"], shade)


def study_rows(game, model, pose, texture):
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
    # The ankle-length linen opens behind the knee on the long profile
    # steps. Hide panels stop at the thigh and stay close to the leg.
    trail = {2: 2, 11: 3, 12: 5, 13: 2, 14: 4, 22: 3, 23: 2, 24: 2}.get(pose, 0)
    linen_knee = (knee[0]-trail, knee[1]+1, knee[2], knee[3]+1)
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
                    paint = None
                    if not near_arm:
                        if in_top:
                            paint = garment(role, u, t, False, pose in PROFILE, pose in REAR, texture)

                        else:
                            cu, ch = fabric_coords(x, y, waist, linen_knee) if role == "Cleric" else (v, h)
                            if 0 <= cu <= 1 and ch >= 0:
                                paint = garment(role, cu, ch, True, pose in PROFILE, pose in REAR, texture)
                    if GUARD[pose] and role in ("Fighter", "Gladiator"):
                        gx, gy = GUARD[pose]
                        fx, fy = x-gx, y-gy
                        if (fx/3.1)**2+((fy-.45)/1.95)**2 < 1 and c not in (179, 180, 181):
                            material = BONE if role == "Fighter" else BRONZE
                            paint = pigment(material, 4.5-1.35*fy-.58*fx+(fx+fy) % 2)
                    # Only the edge of the folded hip projects behind the
                    # crossing forearm on the last front strike.
                    if pose == 17 and 17 <= y <= 22 and x >= 19 and not near_arm:
                        ramp = RAMPS["linen" if role == "Cleric" else "hide"]
                        paint = pigment(ramp, 8+.7*(20-x)+texture[y % 8][x % 8])
                    # On the tucked front strike the far toes turn up
                    # against the hip. They cross in front of the short wrap.
                    if paint is None or (pose == 17 and x >= 20 and y >= 21
                                         and foot is not None and role != "Cleric"):
                        paint = foot
                    pieces[role][sy][sx] = body if paint is None else paint
    # Bridge the panel between the thighs. Extend the cloth only inside the
    # hem, so the native stride shows through again below the knees.
    for sy, row in enumerate(source):
        y = sy-dy
        if y < min(waist[1], waist[3]) or y > max(linen_knee[1], linen_knee[3])+2:
            continue
        for sx, c in enumerate(row):
            if c is not None:
                continue
            v, h = fabric_coords(sx-dx, y, waist, knee)
            for role in ROLES[2:]:
                cu, ch = fabric_coords(sx-dx, y, waist, linen_knee) if role == "Cleric" else (v, h)
                if 0 <= cu <= 1 and ch >= 0:
                    pieces[role][sy][sx] = garment(
                        role, cu, ch, True, pose in PROFILE, pose in REAR, texture)
    return {"Original": original, **{role: upright(rows) if reverse else rows for role, rows in pieces.items()}}


def render(game_dir, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    texture = reference_folds(game)["linen"]
    floor = Image.open(TERRAIN).convert("RGB").crop((45, 144, 99, 195))
    atlas.floor = floor
    frames = []
    sheets = {model: Image.new("RGB", (3*5*108, 10*148), dwarf.PAPER) for model in MODELS}
    output.mkdir(parents=True, exist_ok=True)
    for pose, name in enumerate(dwarf.NAMES):
        page = Image.new("RGB", (678, 522), dwarf.PAPER)
        label(page, (12, 7), "Half-giant outfit study", 19)
        label(page, (666, 10), f"{pose:02}   {name}", 14, "ra")
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
                px = (pose % 3*5+j)*108
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
