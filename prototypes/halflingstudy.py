"""First three halfling outfits. Run with the retail game directory and gallery directory."""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas

MODELS = (2068, 2070)
ROLES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
# Shoulder and hip centres, left and right hem corners and woman's registration.
# Coordinates follow the retail man's cel. Fallen is authored feet-down.
CUT = (
    ((10, 5), (10, 11), (5, 17), (15, 16), (-1, 1)),
    ((10, 5), (10, 11), (5, 16), (15, 18), (0, 1)),
    ((6, 6), (4, 11), (1, 17), (9, 15), (2, 0)),
    ((9, 5), (9, 11), (4, 18), (14, 16), (1, 1)),
    ((9, 5), (9, 10), (4, 14), (13, 17), (0, 1)),
    ((9, 5), (9, 11), (4, 16), (13, 18), (0, 1)),
    ((10, 5), (10, 10), (5, 17), (14, 15), (0, 1)),
    ((6, 5), (6, 11), (2, 17), (11, 16), (1, 1)),
    ((6, 5), (6, 11), (1, 18), (11, 15), (0, 1)),
    ((7, 5), (7, 11), (3, 15), (12, 17), (0, 1)),
    ((8, 5), (7, 11), (3, 15), (12, 18), (0, 1)),
    ((4, 6), (3, 10), (0, 17), (7, 14), (3, 0)),
    ((9, 6), (7, 11), (1, 16), (12, 18), (0, 0)),
    ((5, 6), (3, 11), (0, 15), (6, 17), (2, 0)),
    ((9, 5), (7, 11), (3, 16), (12, 15), (0, 0)),
    ((7, 8), (6, 14), (0, 19), (11, 17), (4, 0)),
    ((12, 6), (10, 10), (6, 15), (13, 13), (0, 5)),
    ((11, 8), (12, 12), (6, 17), (15, 14), (0, 0)),
    ((6, 5), (5, 11), (0, 16), (11, 18), (3, 0)),
    ((7, 6), (8, 11), (2, 17), (14, 17), (0, 0)),
    ((9, 6), (10, 11), (3, 17), (15, 17), (0, 0)),
    ((8, 5), (10, 11), (5, 17), (16, 15), (2, 0)),
    ((12, 5), (8, 10), (2, 16), (12, 13), (0, 1)),
    ((10, 4), (7, 8), (1, 15), (11, 11), (0, 2)),
    ((6, 6), (6, 11), (0, 18), (11, 16), (3, 1)),
    ((6, 9), (6, 15), (1, 20), (11, 21), (2, 0)),
    ((9, 9), (10, 15), (5, 21), (16, 19), (1, 0)),
    ((8, 8), (10, 11), (6, 17), (15, 13), (0, 2)),
    ((7, 7), (7, 11), (2, 15), (12, 15), (0, 1)),
)
REAR = {1, 7, 8, 9, 10, 18, 19, 20, 25, 28}
PROFILE = {2, 11, 12, 13, 14, 22, 23, 24}
OCHRE = {64, 65, 140, 141, 142, 143, 157, 168, 179, 180, 181, 182, 183, 184, 200, 201}
SHORTS = {17, 18, 19, 20, 21, 22, 23, 48, 49, 50, 51, 52, 58, 74, 159, 174}
DARK = {128, 129, 208, 209, 210, 254}
BANDS = {43, 249, 250}

# Centres of the close-fitting guard on the visible upper arm. In the
# low front strike and recoil the arm turns across the face.
SHOULDER = (
    (5, 6), (14, 6), (4, 7), (4, 6), (4, 6), (3, 6), (5, 6), (10, 6), (10, 6), (11, 6),
    (11, 6), (3, 6), (8, 6), (4, 6), (7, 6), (4, 8), (8, 6), (13, 9), (8, 6), (8, 7),
    (10, 7), (5, 6), (10, 5), (9, 5), (5, 6), (6, 10), (5, 8), (10, 7), (10, 8),
)
# Scanlines of the native head, including the last skin pixel at the jaw.
# Origins follow the head, independently of the shoulder and the raised hand.
# The retail walk reuses three heads. Crossed arms and tilted combat heads
# have their own contours. The fallen cel is traced in the same feet-down
# orientation as CUT. Each span includes both endpoints.
FRONT_HEAD = ((3, 7), (1, 8), (1, 9), (0, 10), (1, 8), (2, 7), (3, 7))
REAR_HEAD = ((2, 6), (1, 7), (0, 7), (1, 8), (0, 8), (2, 6))
SIDE_HEAD = ((3, 7), (2, 8), (1, 7), (1, 8), (0, 8), (4, 7))
HEADS = (
    (5, 0, FRONT_HEAD), (6, 0, REAR_HEAD), (3, 0, SIDE_HEAD),
    (4, 0, FRONT_HEAD), (4, 0, FRONT_HEAD), (4, 0, FRONT_HEAD), (5, 0, FRONT_HEAD),
    (2, 0, REAR_HEAD), (2, 0, REAR_HEAD), (3, 0, REAR_HEAD), (3, 0, REAR_HEAD),
    (2, 0, SIDE_HEAD), (7, 0, SIDE_HEAD), (3, 0, SIDE_HEAD), (6, 0, SIDE_HEAD),
    (3, 2, ((3, 6), (1, 6), (1, 6), (0, 6), (0, 6), (2, 6))),
    (6, 0, (*FRONT_HEAD[:5], (4, 8), (5, 7))),
    (3, 4, ((2, 6), (1, 7), (0, 7), (0, 8), (1, 8), (2, 7), (3, 5))),
    (2, 0, REAR_HEAD),
    (1, 0, ((2, 6), (1, 7), (0, 7), (1, 7), (1, 7), (2, 7))),
    (2, 0, REAR_HEAD),
    (4, 0, ((1, 6), (0, 7), (1, 7), (0, 7), (0, 6), (3, 5))),
    (10, 0, ((2, 6), (1, 7), (0, 6), (1, 7), (5, 6))),
    (9, 0, ((2, 6), (1, 7), (1, 6), (1, 7), (4, 6))),
    (4, 0, ((3, 6), (1, 7), (1, 8), (0, 8), (2, 6), (2, 6))),
    (1, 3, ((2, 6), (1, 7), (0, 7), (0, 8), (0, 8), (2, 7))),
    (4, 3, ((1, 6), (0, 7), (0, 7), (3, 6), (3, 6))),
    (0, 3, ((3, 5), (2, 6), (1, 6), (0, 7), (0, 7), (0, 7), (1, 7))),
    (4, 0, ((2, 5), (1, 7), (1, 8), (0, 8), (0, 8), (1, 7), (2, 6))),
)


def head_pixels(pose):
    left, top, spans = HEADS[pose]
    return {(left+x, top+y) for y, (lo, hi) in enumerate(spans) for x in range(lo, hi+1)}


# Radii of the actual bow are only a pixel or two. Gold also paints
# the man's hide top, so identify the shaft by its path through the cel.
BOW_ARCS = {
    24: ((3, 16, 16), (4, 16, 16), (5, 16, 16), (6, 16, 16), (7, 15, 16), (8, 15, 16),
         (9, 14, 15), (10, 13, 15), (11, 12, 14), (12, 12, 13), (13, 10, 11),
         (14, 2, 3), (14, 9, 11), (15, 4, 9)),
    25: ((0, 9, 12), (1, 8, 14), (2, 5, 5), (2, 14, 15)),
    26: ((0, 15, 15), (1, 15, 16), (2, 16, 17), (3, 17, 18), (4, 18, 19), (5, 19, 20),
         (6, 19, 20), (9, 18, 18), (10, 19, 19), (11, 18, 19), (12, 17, 18),
         (13, 16, 17), (14, 15, 16)),
}


BONE = (207, 205, 206, 121, 199, 62)
BRONZE = (88, 90, 93, 96, 168, 169)


def flip(rows):
    return [r[::-1] for r in rows[::-1]]


def dye(ramp, shade):
    return ramp[max(0, min(len(ramp)-1, round(shade)))]


def pixels(vertices):
    # Work outside the native bounding box for cloth that swings past a leg.
    im = Image.new("1", (48, 40))
    ImageDraw.Draw(im).polygon([(x+5, y) for x, y in vertices], fill=1)
    return {(x-5, y) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))}


def garment_masks(ref, native, twin, pose, dx, dy, half):
    (sx, sy), (hx, hy), _, _, offset = CUT[pose]
    # The retail figures share their gait. His orange hide and blue shorts
    # separate the trunk and thighs even where her costume uses skin shadows.
    top, legs, bands = set(), set(), set()
    w, h = len(native[0]), len(native)
    for y, row in enumerate(ref):
        t = min(1, max(0, (y-sy)/max(1, hy-sy)))
        center = sx+(hx-sx)*t
        for x, c in enumerate(row):
            if c is None:
                continue
            raised = (pose == 17 and 5 <= y <= 10 and x >= 11 or
                      pose == 27 and 5 <= y <= 8 and x >= 7 or
                      pose == 28 and 4 <= y <= 8 and x <= 5 or
                      pose == 24 and 4 <= y <= 5 and 3 <= x <= 5 or
                      pose == 26 and y in (7, 8) and x >= 8)
            if (raised or sy <= y <= hy+1 and abs(x-center) <= half+2) and c in OCHRE:
                top.add((x, y))
            if y >= hy-2 and c in SHORTS and (y >= hy or abs(x-hx) <= half):
                legs.add((x, y))
    for y in range(sy, hy+1):
        xx = [x for x, yy in top if yy == y]
        if len(xx) >= 2:
            for x in range(min(xx)+1, max(xx)):
                if ref[y][x] in DARK and (pose not in PROFILE or ref[y][x] != 254):
                    top.add((x, y))
    # Keep a crossing wrist out of the reconstructed thigh. Its bright
    # bracelet seeds the small ring of metal and leather around it.
    for y, row in enumerate(native):
        for x, c in enumerate(row):
            fx, fy = x-dx+offset[0], y-dy+offset[1]
            if pose == 28:
                fx, fy = len(twin[0])-1-fx, len(twin)-1-fy
            female_band = 0 <= fy < len(twin) and 0 <= fx < len(twin[0]) and twin[fy][fx] in BANDS
            if c in BANDS or female_band:
                for yy in range(max(0, y-1), min(h, y+2)):
                    for xx in range(max(0, x-2), min(w, x+3)):
                        if native[yy][xx] in BANDS | SHORTS | {64, 65, 179, 180, 181, 182, 201, 194, 205, 208, 209, 210, 211, 254}:
                            bands.add((xx-dx, yy-dy))
    for x, y in list(legs):
        if (x, y) in bands:
            legs.discard((x, y))
            continue
        for xx in (x-1, x+1):
            if 0 <= xx < len(ref[y]) and ref[y][xx] in DARK and (xx, y) not in bands:
                legs.add((xx, y))
    # Rebuild each thigh across its own contiguous run. The near knee
    # and far knee follow different lines when the legs cross in profile.
    thigh_light = {}
    for y, row in enumerate(ref):
        xx = sorted(x for x, yy in legs if yy == y)
        for x in xx:
            l = r = x
            while l > 0 and (l-1, y) in legs:
                l -= 1
            while r+1 < len(row) and (r+1, y) in legs:
                r += 1
            thigh_light[x, y] = (x-l+.5)/(r-l+1)
    return top, legs, bands, thigh_light


# Highlights surviving on the outer edge of his retail cuffs. Trace these
# in the native cel because the same ochres also paint hair and the bow.
MALE_CUFF_TIPS = {1: ((1, 9), (2, 10)), 2: ((11, 11),), 3: ((18, 10),),
                  7: ((13, 8),), 10: ((0, 13),), 27: ((0, 10),)}


def rows_for(game, model, pose, swatch):
    cb, f = divmod(pose, 15)
    hands = game.fig(model).parts(cb, f).hands.values() if pose != 28 else ()
    ref = game.fr(2068+cb, f)
    native = game.fr(model+cb, f)
    if pose == 28:
        ref, native = flip(ref), flip(native)
    (sx, sy), (hx, hy), left, right, offset = CUT[pose]
    dx, dy = offset if model == 2070 else (0, 0)
    guard_x, guard_y = SHOULDER[pose]
    bow = {(x+dx, y+dy) for y, l, r in BOW_ARCS.get(pose, ()) for x in range(l, r+1)}
    if pose == 24 and model == 2070:
        bow.add((6, 16))  # Her hair trails back and the lower bow tip shifts a pixel.
    w, h = len(native[0]), len(native)
    original = [[None]*4+list(row)+[None]*4 for row in native]
    rows = {k: [r[:] for r in original] for k in ROLES}
    half = 3 if pose in PROFILE else 4
    top, legs, bands, thigh_light = garment_masks(ref, native, game.fr(2070+cb, f), pose, dx, dy, half)
    if model == 2068:
        bands.update(MALE_CUFF_TIPS.get(pose, ()))
    belt_l, belt_r = (hx-half+1, hy), (hx+half-1, hy)
    hem = (left, (left[0]+2, left[1]+1), (hx, (left[1]+right[1])//2-1),
           (right[0]-1, right[1]+1), right)
    # In front and rear views the near knee pushes the linen sideways.
    # The middle of the hem spans the stride, with one low point over the
    # weight-bearing side and no upward cut between the thighs.
    broad_robe = pose in (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 15, 16, 18, 19, 20, 21, 25, 26)
    if broad_robe:
        lx, ly = left
        rx, ry = right
        hem = ((lx, ly), (lx+2, ly+1), (hx, (ly+ry+1)//2+1),
               (rx-2, ry+1), (rx, ry))
    robe = pixels((belt_l, belt_r, *reversed(hem)))
    # Short leather overlaps the front of the thighs. Keep the gap between
    # the moving legs and the contrasting arc of linen on the long robe.
    wrap = pixels((belt_l, belt_r, (hx+half, hy+3), (hx+1, hy+2),
                   (hx-2, hy+4), (hx-half, hy+3)))
    if pose == 22:
        robe.add((10, 14))  # Linen turns over the extended knee.
        wrap.update(((8, 13), (7, 14)))
    # The leather jerkin extends past the wrap. Its two tabs travel toward
    # the respective knees and open at the front of the advancing thigh.
    outer_left = max(hx-half-2, left[0]+1)
    outer_right = min(hx+half+2, right[0])
    jerkin = pixels((belt_l, belt_r, (outer_right, min(hy+6, right[1])),
                     (hx+1, hy+3), (hx, hy+2), (hx-2, hy+5),
                     (outer_left, min(hy+6, left[1]))))
    if pose == 12:
        jerkin.add((11, 17))
    if pose == 22:
        jerkin.add((8, 13))
    head = head_pixels(pose)
    # Leave a sliver of cleaned neck beneath the jaw. It follows the
    # underside of the head, even when the striking torso bends sideways.
    neckline = {(x, y+1) for x, y in head} - head
    # The stock hide rises above the usual torso cut in these frames.
    # Clean its upper edge before exposing the neck under the new collar.
    if pose in (2, 3, 4, 5, 11, 16, 22):
        top.update((x, y) for x, y in neckline
                   if 0 <= y < len(ref) and 0 <= x < len(ref[y]) and ref[y][x] in OCHRE)
    head_hair = set()
    if model == 2070:
        for x in range(w):
            for y in range(min(h, hy+dy+1)):
                c = native[y][x]
                if c in {179, 180, 181, 182, 183, 184, 200, 201} and (x, y) not in bow:
                    head_hair.add((x-dx, y-dy))
                    if y and native[y-1][x] in DARK:
                        head_hair.add((x-dx, y-1-dy))
    for ny in range(h):
        y = ny-dy
        for nx in range(-4, w+4):
            x = nx-dx
            point = x, y
            c = native[ny][nx] if 0 <= nx < w else None
            if point in head or point in head_hair or (nx, ny) in bow:
                continue
            trunk = point in top
            thigh = point in legs
            wrist = point in bands
            if y < sy and not wrist and not trunk and abs(x-guard_x) > 2:
                continue
            center = sx+(hx-sx)*max(0, min(1, (y-sy)/max(1, hy-sy)))
            u = (x-center)/half
            depth = (y-sy)/max(1, hy-sy)
            body = c
            if (model == 2070 and hy+2 <= y <= hy+6 and c in DARK and abs(x-hx) <= half
                    and pose != 13 and 0 <= x < len(ref[0]) and y < len(ref) and ref[y][x] is None):
                body = None  # Open the small gap between her thighs under the loincloth.
            if c is not None and (trunk or thigh or wrist):
                if wrist:
                    body = (134, 132, 130, 145)[(x+2*y) % 4]
                elif trunk:
                    body = elf.torso_skin(u, depth, pose in REAR, pose in PROFILE)
                    if model == 2070 and pose not in REAR | PROFILE and .18 < depth < .58:
                        body = 145 if abs(u) > .23 and depth < .45 else 132
                else:
                    side = thigh_light[point]
                    body = elf.leg_skin(side, (y-hy)/max(1, h-dy-hy), pose in REAR)
                if nx+1 >= w or native[ny][nx+1] is None:
                    body = 129
            for role in ROLES[1:]:
                rows[role][ny][nx+4] = body
            grip = any(abs(nx-gx) <= 1 and abs(ny-gy) <= 1 for gx, gy in hands)
            if point in neckline or wrist or (grip and c is not None and not (trunk or thigh)):
                continue
            behind = c is None or trunk or thigh or y >= hy+2 and abs(x-hx) <= half+1
            grain = swatch[(y-hy) % 8][(x-hx) % 8]
            shade = 7.4-3*abs(u+.28)+.65*grain
            # A narrow opening under the jaw leaves the neck and face
            # clear. In front the hide and linen cover both sides of it.
            bib = (pose in (0, 3, 4, 5, 6, 21, 26) and .14 < depth < 1 and
                   abs(u) < .88 and depth > .29-.18*abs(u))
            back_seam = pose in PROFILE and .25 < depth < 1 and -1.05 < u < -.51
            if (trunk or bib or back_seam) and c is not None:
                rows['Fighter'][ny][nx+4] = dye(RAMPS['hide'], shade+2.4*math.cos(u*4-depth)+2.6*(u < -.2))
                rows['Cleric'][ny][nx+4] = dye(RAMPS['linen'], shade+1.9*math.cos(u*7-depth))
                along = max(0, min(1, (y-guard_y)/max(1, hy-guard_y)))
                strap = guard_x+(hx+(2 if guard_x < sx else -2)-guard_x)*along
                if abs(x-strap) <= 1.05:
                    strap_light = 8.5 if x < strap else 3.6
                    rows['Gladiator'][ny][nx+4] = dye(RAMPS['hide'], strap_light+.45*grain)
            cap_y = y-guard_y
            cap_x = x-guard_x
            if c is not None and (cap_y == 0 and abs(cap_x) <= 1 or
                                  cap_y == 1 and abs(cap_x) <= 2 or cap_y == 2 and abs(cap_x) <= 1):
                # On the turn the high side catches one light, above a
                # darkened lower rim and the skin of the arm.
                cap_shade = 4.6-1.45*cap_y-.56*abs(cap_x)-.48*cap_x
                rows['Cleric'][ny][nx+4] = dye(RAMPS['linen'], 5+1.2*cap_shade+.45*grain)
                rows['Fighter'][ny][nx+4] = dye(BONE, cap_shade)
                rows['Gladiator'][ny][nx+4] = dye(BRONZE, cap_shade)
            for role, panel in (('Gladiator', wrap), ('Fighter', jerkin), ('Cleric', robe)):
                if point not in panel or not behind:
                    continue
                if c is None and ((pose == 6 and x >= 14 and y <= 14)
                                  or (pose == 10 and x <= 3 and y <= 15)):
                    continue
                ramp = RAMPS['linen' if role == 'Cleric' else 'hide']
                fall = (y-hy)/max(1, (left[1]+right[1])*.5-hy)
                span = half+fall*(right[0]-left[0]-2*half)*.5
                fold = math.cos(6*(x-hx)/max(1, span)+.8*fall)
                if role == 'Cleric' and (x, y+1) not in panel and x < hx:
                    fold += .8
                light = 7+2.6*fold+.65*grain-2*((x, y+1) not in panel)
                if role == 'Fighter':
                    # A cut between the two hip flaps exposes the underlying
                    # body at the hem. The raised outside edge catches the light.
                    if y > hy+1 and pose != 22 and abs(x-hx-.25*(y-hy)) < .85:
                        continue
                    light += 2*math.cos((x-hx)*.9)+2*(x == hx-half+1)
                elif role == 'Cleric' and broad_robe:
                    # A broad lit apron turns over the knee. The deepest
                    # fold drifts toward the side seam as it drops, and
                    # the curved hem carries light across the middle.
                    near = -1 if left[1] < right[1] else 1
                    crease = hx+near*(1.2+2.3*fall)
                    dist = x-crease
                    light = (9.5+.71*grain-3.0*abs(x-hx)/max(1, span)
                             -4.7*math.exp(-.75*dist*dist)
                             +1.5*math.exp(-.52*(dist+1.5)**2))
                    if (x+1, y) not in panel:
                        light -= 2.5
                    if (x, y+1) not in panel:
                        light += .7 if abs(x-hx) < half else -1.3
                elif role == 'Cleric':
                    light += 1.3*fold - 1.3*((x+1, y) not in panel)
                elif role == 'Gladiator':
                    # The overlapped hide is warm on its turned edge; a dark
                    # lap line runs from the belt over the forward thigh.
                    lap = x-hx+.62*(y-hy)
                    light += 2.6 if -.8 < lap < .4 else -2.2 if .4 <= lap < 1.4 else .7
                color = dye(ramp, light)
                if y == hy:
                    color = dye(RAMPS['hide'], 4+.55*grain)
                rows[role][ny][nx+4] = color
    return {role: flip(r) if pose == 28 else r for role, r in rows.items()}


def check_uncovered_head(game, model, pose, outfits):
    cb, frame = divmod(pose, 15)
    native = game.fr(model+cb, frame)
    dx, dy = CUT[pose][-1] if model == 2070 else (0, 0)
    for x, y in head_pixels(pose):
        x, y = x+dx, y+dy
        if pose == 28:
            x, y = len(native[0])-1-x, len(native)-1-y
        expected = native[y][x]
        for role in ("Body base", "Gladiator", "Fighter", "Cleric"):
            if outfits[role][y][x+4] != expected:
                raise ValueError(f"{model} {role}, pose {pose}: changed head pixel at {(x, y)}")


def material_sheet(game, swatch, sand):
    """Match the retail garment and both proposals on one ground line per row."""
    result = Image.new("RGB", (900, 660), dwarf.PAPER)
    label(result, (12, 6), "Halfling material comparison", 20)
    for side, pose in enumerate((0, 12)):
        left = 96 + side * 399
        label(result, (left + 182, 38), dwarf.NAMES[pose], 15, "ma")
        dressed = [rows_for(game, model, pose, swatch) for model in MODELS]
        for j, caption in enumerate(("Retail reference", "Halfling man", "Halfling woman")):
            label(result, (left + 64 + j*129, 65), caption, 13, "ma")
        for i, (role, npc, reference) in enumerate((
            ("Gladiator", 1252, "Warrior"), ("Fighter", 1252, "Warrior"), ("Cleric", 1563, "Priest")
        )):
            y = 88 + i*190
            if side == 0:
                label(result, (10, y+58), role, 14)
                label(result, (10, y+82), "Ref. "+reference, 11)
            for j, rows in enumerate((game.fr(npc, pose), dressed[0][role], dressed[1][role])):
                tile = elf.placed_tile(game, rows, sand, 1, 0, 0, 0).crop((6, 4, 48, 51))
                x = left + j*129
                result.paste(tile.resize((126, 141), Image.Resampling.NEAREST), (x, y))
                result.paste(tile, (x+42, y+142))
    return result


def render(game_dir, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    swatch = reference_folds(game)["linen"]
    sand = Image.open(TERRAIN).convert("RGB").crop((45, 144, 87, 181))
    stone = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")
                       ).convert("RGB").crop((170, 35, 212, 72))
    npc_sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    npc_stone = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")
                           ).convert("RGB").crop((164, 21, 218, 72))
    frames = []
    sheets = {m: Image.new("RGB", (3*5*85, 10*118), dwarf.PAPER) for m in MODELS}
    output.mkdir(parents=True, exist_ok=True)
    for pose, name in enumerate(dwarf.NAMES):
        page = Image.new("RGB", (646, 484), dwarf.PAPER)
        label(page, (12, 7), "Halfling outfit study", 19)
        label(page, (632, 9), f"{pose:02}   {name}", 14, "ra")
        for i, model in enumerate(MODELS):
            rows = rows_for(game, model, pose, swatch)
            check_uncovered_head(game, model, pose, rows)
            y = 61+i*141
            label(page, (10, y+35), ("Man", "Woman")[i], 13)
            for j, role in enumerate(ROLES):
                x = 75+j*112
                if i == 0:
                    label(page, (x+42, 36), role, 13, "ma")
                tile = elf.placed_tile(game, rows[role], sand, 2, 0, 0, 0)
                page.paste(tile, (x, y))
                page.paste(elf.placed_tile(game, rows[role], stone, 1, 0, 0, 0), (x+21, y+78))
                sx = (pose % 3*5+j)*85
                sy = pose//3*118
                if j == 0:
                    label(sheets[model], (sx+3, sy+1), f"{pose:02}   {name}", 13)
                label(sheets[model], (sx+3, sy+21), role, 11)
                sheets[model].paste(tile, (sx, sy+39))
        # Use a taller crop of the same terrain for the taller NPCs. The
        # bottom two rows of each tile are the same ground at both scales.
        label(page, (12, 330), "Retail figures and approved human outfit", 14)
        for j, (npc, caption) in enumerate(((1252, "Warrior"), (1563, "Priest"), (630, "Thief"))):
            pic = npc+pose//15
            frame = pose % 15
            if frame >= game.count(pic):
                pic, frame = npc, 0
                caption += " (idle)"
            ref = game.fr(pic, frame)
            tile = elf.placed_tile(game, ref, npc_sand, 2, 0, 0, 0)
            x = 12+j*159
            page.paste(tile, (x, 370))
            page.paste(elf.placed_tile(game, ref, npc_stone, 1, 0, 0, 0), (x+103, 421))
            label(page, (x, 347), caption, 13)
        atlas.floor = npc_sand
        human = atlas.tile(300, pose, "Gladiator", "Class colors", 1)
        label(page, (489, 347), "Human Gladiator", 13)
        page.paste(human.resize((2*human.width, 2*human.height), Image.Resampling.NEAREST),
                   (489, 472-2*human.height))
        atlas.floor = npc_stone
        page.paste(atlas.tile(300, pose, "Gladiator", "Class colors", 1), (592, 472-human.height))
        frames.append(page)
    loop(frames, output/"halfling-study.gif")
    material_sheet(game, swatch, npc_sand).save(output/"halfling-materials.png")
    for model, sheet in sheets.items():
        sex = "man" if model == 2068 else "woman"
        sheet.save(output/f"halfling-{sex}-poses.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
