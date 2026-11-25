"""Fit and review the six single-class Mul studies on retail terrain."""
import argparse
from math import cos
from pathlib import Path

from PIL import Image, ImageDraw

import mulfront
import mulstudy as fit
from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas


NEW = ("Druid", "Psionicist", "Thief")
REAR = {1, 7, 8, 9, 10, 18, 19, 20, 25}
PROFILE = {2, 11, 12, 13, 14, 15, 22, 23, 26}
TEAL = (17, 69, 70, 71, 40, 72, 73)
MOSS = (208, 69, 188, 53, 189, 54, 226, 55, 227)
# Trace the pleat over the leading thigh and both free corners on the retail
# figure. A short mantle breaks above the hip; the slate fall clears the calf.
# Coordinates are (near thigh x, y, mantle tip x, y, cloak tip x, y).
CUT = (
    (8, 19, 5, 16, 4, 21), (15, 19, 15, 17, 17, 23), (3, 19, 0, 16, -2, 21),
    (7, 19, 4, 16, 3, 21), (11, 19, 4, 15, 3, 20), (12, 19, 4, 16, 3, 20),
    (7, 19, 4, 15, 3, 21), (5, 19, 10, 17, 12, 22), (5, 19, 10, 17, 11, 23),
    (10, 19, 12, 17, 13, 21), (11, 19, 12, 18, 14, 22),
    (5, 19, 0, 16, -2, 20), (10, 19, -1, 15, -4, 18), (5, 20, -2, 16, -4, 19),
    (7, 19, 1, 17, -1, 21), (6, 19, 0, 17, -2, 20), (8, 15, 6, 13, 4, 16),
    (8, 16, 16, 13, 19, 15), (8, 18, 9, 17, 11, 21), (10, 18, 12, 17, 14, 20),
    (13, 19, 14, 16, 16, 20), (10, 19, 4, 16, 2, 20), (6, 18, 0, 15, -3, 18),
    (6, 16, 0, 14, -2, 17), (6, 19, 2, 16, 0, 20), (10, 21, 12, 20, 14, 24),
    (8, 22, 3, 18, 0, 22), (9, 14, 16, 9, 19, 10), (7, 16, 4, 15, 2, 18),
)
SIDE_FALL = PROFILE | {17, 21, 24, 27}
SLATE = RAMPS["slate"]


def shade(ramp, light):
    return ramp[max(0, min(len(ramp)-1, round(light)))]


def panel(points):
    left = min(x for x, y in points)
    top = min(y for x, y in points)
    width = max(x for x, y in points)-left+1
    height = max(y for x, y in points)-top+1
    mask = Image.new("1", (width, height))
    ImageDraw.Draw(mask).polygon([(x-left, y-top) for x, y in points], fill=1)
    return {(x+left, y+top) for y in range(height) for x in range(width) if mask.getpixel((x, y))}


# Druid mantle outlines traced clockwise on the native cels. The first
# point is on the loaded shoulder. The last corners describe the free
# return; the arm and exposed throat are composited in front separately.
MANTLES = (
    # Idle, front / rear / side.
    ((5,7), (8,6), (15,6), (17,7), (17,9), (14,11), (11,12), (8,15), (6,14), (4,10)),
    ((6,8), (10,6), (15,7), (16,9), (15,13), (13,15), (10,13), (7,13), (5,10)),
    ((4,6), (6,6), (7,8), (7,11), (5,12), (2,14), (1,15), (-1,14), (1,9)),
    # Front walk.
    ((4,7), (7,6), (14,6), (16,7), (16,10), (13,11), (10,12), (7,15), (5,14), (3,10)),
    ((4,7), (7,6), (14,6), (16,8), (14,10), (10,12), (7,14), (5,13), (4,11), (3,9)),
    ((5,6), (8,5), (14,5), (15,7), (14,10), (11,11), (8,14), (6,13), (5,11), (5,9)),
    ((4,7), (7,6), (13,6), (15,8), (15,10), (11,11), (8,15), (6,14), (4,11), (3,9)),
    # Rear walk.
    ((3,8), (6,6), (10,7), (11,9), (10,13), (9,15), (6,13), (3,13), (2,10)),
    ((3,7), (6,5), (10,6), (12,8), (11,12), (9,15), (6,13), (3,12), (2,9)),
    ((4,8), (7,6), (11,7), (13,9), (13,12), (11,14), (8,13), (5,14), (3,10)),
    ((5,7), (8,5), (12,7), (13,9), (12,13), (10,14), (8,13), (5,14), (4,10)),
    # Side walk.
    ((6,6), (8,6), (9,8), (8,11), (6,12), (2,15), (0,15), (1,12), (3,8)),
    ((9,5), (11,5), (12,7), (10,10), (7,12), (3,13), (-1,15), (0,12), (5,8)),
    ((6,5), (8,5), (9,7), (8,10), (5,12), (1,14), (-2,15), (0,11), (3,7)),
    ((8,5), (10,5), (11,7), (10,10), (7,12), (4,15), (1,16), (2,12), (4,8)),
    # Front strikes.
    ((6,8), (9,8), (10,10), (9,13), (6,14), (3,15), (0,16), (1,12), (3,9)),
    ((8,7), (11,6), (15,6), (17,8), (16,10), (13,10), (9,13), (7,12), (7,9)),
    ((12,7), (13,8), (15,10), (16,12), (15,13), (13,13), (10,13), (9,11), (10,9)),
    # Rear strikes.
    ((3,8), (6,7), (9,7), (10,9), (9,12), (8,15), (6,13), (3,14), (2,11)),
    ((4,8), (6,6), (9,7), (10,9), (11,12), (12,14), (8,13), (5,14), (3,11)),
    ((6,7), (8,5), (10,6), (11,8), (12,11), (14,14), (10,13), (7,13), (6,10)),
    # Side strikes.
    ((6,7), (9,6), (13,6), (14,8), (12,11), (9,12), (5,15), (3,14), (4,10)),
    ((8,6), (12,6), (13,7), (11,10), (8,12), (4,14), (2,15), (0,15), (1,12), (4,8)),
    ((8,6), (11,5), (13,7), (10,9), (8,11), (4,13), (2,14), (0,14), (1,11), (4,8)),
    # Bow, front / rear / side, then hit and fallen.
    ((5,6), (8,6), (10,8), (10,10), (8,12), (5,14), (3,15), (2,14), (3,10)),
    ((7,10), (9,8), (11,9), (12,12), (12,15), (11,18), (8,16), (5,16), (5,13)),
    ((5,10), (8,8), (11,9), (13,11), (11,14), (8,15), (5,18), (3,17), (3,16), (4,12)),
    ((10,3), (11,3), (12,5), (13,6), (15,7), (16,8), (14,9), (11,10), (8,11), (7,9), (8,5)),
    ((4,8), (7,7), (14,7), (16,9), (14,11), (11,13), (7,12), (4,13), (3,10)),
)


def thief_cape(pose):
    (sy, sl, sr), (ry, rl, rr), (wy, wl, wr), _, _ = fit.ROBE_CUTS[pose]
    knee, _, _, _, tx, ty = CUT[pose]
    hip = (wl+wr)//2
    if pose in SIDE_FALL:
        sign = 1 if tx > hip else -1
        shoulder = sr if sign == 1 else sl
        flank = wr if sign == 1 else wl
        points = ((shoulder-sign, sy+1), ((shoulder+tx)//2, (sy+ty)//2-1),
                  (tx, ty-1), (tx, ty), (tx-sign*2, ty), (flank, wy+3), (hip, wy), (hip, ry+1))
    elif pose in REAR:
        points = ((sl+1, sy+1), (sr-1, sy), (rr, ry+1), (tx-1, wy+1),
                  (tx, ty), (tx-2, ty+1), (hip, ty-1), (min(wl-1, knee-1), ty-3), (rl+1, ry+1))
    else:
        points = ((sl+1, sy+1), (sl+3, sy+2), (hip, ry+1), (wr-1, wy-2), (wl+2, wy),
                  (wl+1, ty-2), (tx, ty+1), (tx-1, ty), (rl, ry+2))
    cloth = panel(points)
    if pose in REAR:
        free = min(wl-3, knee-3)
        throw = 2 if knee <= hip else 4
        cloth |= panel(((sl+1, sy+2), (rl+1, ry), (free-3, ty-3),
                        (free, ty-2), (wl+1, ty-4), (hip, ty),
                        (tx, ty+1), (tx+throw, ty-2), (rr-1, ry)))
    elif pose not in SIDE_FALL:
        cloth |= panel(((sr-2, sy), (sr, sy+2), (rr-1, ry+1),
                        (wr+1, ty-1), (wr-1, ty-2), (hip, ry+2), (sl+2, sy+2), (hip, ry)))
    if pose == 6:
        cloth -= {(x, y) for x, y in cloth if x >= wr and y >= ry+2}
    if pose == 15:
        cloth.discard((1, 12))
    cloth.update({4: ((5, 20),), 8: ((6, 22),), 11: ((2, 19), (1, 20)),
                  10: ((2, 13),), 19: ((3, 13),)}.get(pose, ()))
    return cloth


# The outer shoulder rolls forward and back under the cape in profile.
# Trace its turn down to the rear armhole before releasing the loose hem.
PROFILE_YOKE = {
    2: ((4, 5), (2, 6), (0, 9), (1, 12), (4, 10), (5, 7)),
    11: ((6, 5), (4, 6), (2, 9), (2, 12), (5, 10), (7, 7)),
    12: ((10, 4), (7, 6), (4, 9), (4, 12), (7, 10), (10, 7)),
    13: ((6, 4), (3, 6), (1, 9), (1, 12), (4, 10), (6, 7)),
    14: ((8, 4), (5, 5), (3, 7), (3, 11), (6, 10), (8, 7)),
}


def thief_hood(pose):
    """Round crown, open cheeks, and a trailing nape around the Mul's own head."""
    left, top, spans = fit.HEADS[pose]
    shell = set()
    sy, sl, sr = fit.ROBE_CUTS[pose][0]
    for y, (a, b) in enumerate(spans):
        # Keep the original crown height. Turn the rim behind the temple
        # instead of running a second contour around the whole face.
        lo = left+a-int(1 <= y <= 4)
        hi = left+b+int(1 <= y <= 2)
        for x in range(lo, hi+1):
            if (pose in REAR or y < 2 or
                    (y == 2 and (x <= left+a or (pose not in PROFILE and x >= left+b))) or
                    x < left+a or (pose not in PROFILE and x > left+b)):
                shell.add((x, top+y))
    if pose in REAR:
        # The hood lining falls over the far shoulder blade. Its shadow
        # overlaps the back of the cloak even on the shortest rear stride.
        last = top+len(spans)-1
        shell |= panel(((left, top+3), (left+5, top+3), (left+5, last),
                        (sr-2, sy+3), (left+3, sy+5), (left+1, last+1)))
    else:
        near = left-1
        if pose not in (17, 27):
            shell |= panel(((near, top+2), (left+1, top+2), (left, top+4),
                            (sl+1, sy+3), (sl, sy+2), (near, top+4)))
        if pose not in PROFILE:
            far = left+max(b for _, b in spans)
            if pose in (17, 27):
                shell |= panel(((far, top+2), (far+1, top+3), (sr-1, sy+3),
                                (sr-2, sy+3), (far, top+4)))
            else:
                shell.add((far+1, top+3))
    if pose not in REAR and pose != 17:
        # The cowl sits outside the bald scalp. Trace its turned-back lip
        # down the temple and into the shoulder. Leave the cheek opening.
        for k, (a, b) in enumerate(spans):
            if 1 <= k <= 5:
                shell.add((left+a-2, top+k))
                shell.add((left+a-1, top+k))
                if pose not in PROFILE:
                    shell.add((left+b+1, top+k))
                    if 2 <= k <= 4:
                        shell.add((left+b+2, top+k))
    if pose == 18:
        shell.add((9, 7))
    if pose == 24:
        shell.discard((12, 5))
    if pose == 28:
        shell.add((15, 3))
    return shell


def draw(game, pose, swatches):
    rows = fit.fitted_rows(game, pose)
    body = rows["Body base"]
    h, w = len(body), len(body[0])-2*fit.PAD
    cb, f = divmod(pose, 15)
    figure = game.fig(fit.MODEL)
    parts = figure.parts(cb, f)
    raw = game.fr(fit.MODEL+cb, f)
    bow = game.bow(figure, raw, parts) if pose in (24, 25, 26) else set()
    limbs = {(hx+dx, hy+dy) for hx, hy in parts.hands.values()
             for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))}
    limbs.update(fit.ARM_EDGES.get(pose, ()))
    if pose in fit.CROSSING_ARMS:
        elbow, bend, wrist, thickness = fit.CROSSING_ARMS[pose]
        arm = Image.new("1", (w, h))
        ImageDraw.Draw(arm).line((elbow, bend, wrist), fill=1, width=thickness)
        limbs.update((x, y) for y in range(h) for x in range(w) if arm.getpixel((x, y)))
    protected = fit.head_pixels(pose, w, h) | fit.collar_opening(pose, w, h)
    shoulder, ribs, waist, _, _ = fit.ROBE_CUTS[pose]
    sy, sl, sr = shoulder
    ry, rl, rr = ribs
    wy, wl, wr = waist
    knee, knee_y, _, _, cx, cy = CUT[pose]
    hip = (wl+wr)/2
    # Armholes turn inside the deltoids. Trace a separate waist and thigh
    # for the short tunic so the stride can lift one skirt flap at a time.
    torso = panel(((sl+2, sy+1), (sr-2, sy+1), (rr-1, ry+1), (wr, wy),
                   (wl, wy+1), (rl+1, ry+1)))
    skirt = panel(((wl, wy-1), (wr, wy-1), (wr+1, knee_y-2),
                   (knee+1, knee_y), (knee-1, knee_y), (wl-1, knee_y-2)))
    # At front step four the off hand passes the hip. Pull the far corner
    # in against the thigh to leave open air beneath the elbow.
    if pose == 6:
        skirt.discard((14, 16))
        skirt.discard((14, 17))
    # One continuous fall across the hips. The front flap follows the
    # weight-bearing thigh and the hem curves up over the swinging leg.
    wrap_flap = panel(((wl, wy-1), (wr, wy), (wr, wy+2),
                       (knee+1, knee_y), (knee-2, knee_y-1), (wl, wy+2)))
    ochre_flap = skirt | panel(((wl, wy+1), (wr-1, wy+1),
                                (knee+1, knee_y+1), (knee-1, knee_y+1),
                                (knee-2, knee_y-1)))
    if pose == 24:
        ochre_flap.discard((9, 18))
    if pose == 5:
        ochre_flap.difference_update(((4, 15), (4, 16)))
    if pose == 6:
        ochre_flap.add((10, 19))
    mantle = panel(MANTLES[pose])
    # The lower lip meets the kilt on these front steps. Keep the short
    # curve continuous where the two pixel-stepped diagonals meet.
    mantle.update({0: ((12, 12), (13, 12)), 3: ((11, 12), (12, 12)),
                   4: ((11, 12),), 6: ((11, 12),)}.get(pose, ()))
    scapula, shoulder_y = MANTLES[pose][0]
    front_lapel = pose in (0, 3, 4, 5, 6, 16, 21, 28)
    clasp = (sl+3, ry) if front_lapel else None
    cloak = thief_cape(pose)
    yoke = panel(PROFILE_YOKE[pose]) if pose in PROFILE_YOKE else set()
    cloak.update(yoke)
    # Carry the slate from the cowl onto the near shoulder in the profile
    # walk. The arm rotates in front of this facing; the hem swings behind.
    facing = set()
    if pose in PROFILE_YOKE:
        facing = panel(((sl-1, sy+1), (sl+1, sy), (sl+2, sy+2),
                        (rr-1, ry+1), (rr-2, ry+3), (rl, ry+1)))
        cloak.update(facing)
    # The bow arm crosses the centre of the wrap. Trace the exposed ribs
    # on either side and carry the same diagonal down behind the forearm.
    bow_wrap = set()
    if pose in (24, 25, 26):
        bow_wrap = panel(((sl-1, sy+1), (sr-1, sy+2), (rr+1, ry),
                          (wr, wy), (wl, wy), (rl-1, ry+1)))
    armhole = torso | yoke | facing
    # Continue the lining on the far ribs in the two outward strikes,
    # below the reaching arm, and on the back edge of the side idle.
    lining = {
        2: ((1, 13), (1, 14), (1, 15)),
        19: ((11, 12),),
        22: ((6, 10), (5, 11), (4, 12), (5, 12), (4, 13), (4, 14)),
        23: ((6, 8), (5, 9), (6, 9), (4, 10), (4, 11), (3, 11), (3, 12)),
        25: ((11, 17),),
        26: ((4, 14), (5, 17), (5, 18)),
        27: ((12, 9), (13, 9), (14, 9)),
    }.get(pose, ())
    hood = thief_hood(pose)
    face = fit.head_pixels(pose, w, h)
    hx, hy, spans = fit.HEADS[pose]
    out = {name: [row[:] for row in body] for name in NEW}
    for py in range(h):
        for px in range(-fit.PAD, w+fit.PAD):
            x, y = (w-1-px, h-1-py) if pose == 28 else (px, py)
            point = px, py
            i = px+fit.PAD
            skin = body[py][i]
            if point in bow or (skin is not None and point in limbs):
                continue
            grain = swatches["slate"][(y-wy) % 8][(x-wl) % 8]
            depth = (y-sy)/(wy-sy)
            axis = (sl+sr)/2 + (hip-(sl+sr)/2)*min(max(depth, 0), 1)
            offset = x-axis
            # Carry the light on the native pecs, scapula and lifted knee
            # into close-fitting cloth. Free cloth has its own fold shading.
            light = 0 if skin is None else (game.palette[skin][0]-149)/56
            if point not in protected:
                # Front bow is almost edge-on. The far seam is visible just
                # outside the bent elbow for three rows before it meets the hip.
                if pose == 24 and x == 4 and 9 <= y <= 11:
                    out["Psionicist"][py][i] = shade(TEAL, 2.6+.28*grain)
                if (x, y) in ochre_flap and y >= wy-1:
                    # Lapped hide spans the space between the thighs.
                    # Turn the free edge up over the advancing leg.
                    across_hip = (x-hip)/max(2, (wr-wl)/2)
                    lap = x-knee-.45*(knee_y-y)
                    light_hide = 6.2+.47*grain-.73*abs(across_hip)-2.3*(0 <= lap < 1.4)
                    light_hide += 2.4*(-1.35 <= lap < 0)
                    if (x, y+1) not in ochre_flap:
                        light_hide -= 1.8
                    out["Druid"][py][i] = shade(RAMPS["ochre"], light_hide)
                if (x, y) in wrap_flap and y > wy:
                    diagonal = x-knee-.42*(knee_y-y)
                    fold = 3.9+.36*grain+1.15*cos(diagonal*1.22)
                    if (x, y+1) not in wrap_flap:
                        fold -= 1.5
                    out["Psionicist"][py][i] = shade(TEAL, fold)
                if skin is not None and (x, y) in bow_wrap and (x, y) not in torso:
                    turn = (x-axis)/max(2, (rr-rl)/2)
                    out["Psionicist"][py][i] = shade(TEAL, 3.6+.74*light+.32*grain-.7*abs(turn))
                if skin is not None and ((x, y) in torso or (x, y) in skirt):
                    u = offset/max(2, (wr-wl)/2)
                    belt = wy - round(.7*u) - int(.55 < abs(u) < 1.2)
                    relief = .55*grain + light
                    hides = RAMPS["hide"]
                    out["Thief"][py][i] = shade(hides, 6.3+relief-2.1*abs(u+.22))
                    wrap = y-ry + .40*offset
                    teal = 3.4 + .74*light + .28*grain - .85*abs(u+.25)
                    teal += .7*cos(1.12*wrap)
                    # One shoulder bears the wrap. Its upper edge crosses
                    # the ribs on the way to the opposite hip. The belt
                    # holds a short overlapping flap against the near thigh.
                    side = -1 if pose in REAR else 1
                    across = max(-1, min(1, side*u))
                    edge = sy+1+round((1+across)*.42*(wy-sy))
                    if pose in SIDE_FALL:
                        edge = sy+1+round((1+across)*.20*(wy-sy))
                    if (x, y) in bow_wrap:
                        edge = min(edge, sy+2)
                    if y <= wy:
                        edge -= 2
                    if y >= edge and y <= wy:
                        if y == edge:
                            teal += .7
                        out["Psionicist"][py][i] = shade(TEAL, teal)
                    if y == belt:
                        buckle = 96 if abs(x-knee) < 1 else 90
                        for role in NEW:
                            out[role][py][i] = buckle
                if (x, y) in mantle and (skin is not None or y > shoulder_y):
                    # The gathered upper cloth follows the Mul's shoulder
                    # light. Below the shoulder a curved crease opens out
                    # towards the swinging hip and casts a shadow on the kilt.
                    fall = max(0, y-shoulder_y)
                    fold = x-scapula-(hip-scapula)*min(1, fall/max(1, wy-shoulder_y))
                    ridge = cos(1.18*fold+.35*cos(fall*.5))
                    level = 4.6+1.20*ridge+.33*grain
                    level += .80*light*max(0, 1-fall/6)
                    if (x, y+1) not in mantle:
                        level -= 2.5
                    elif (x-1, y) not in mantle:
                        level += .65
                    elif (x+1, y) not in mantle:
                        level -= 1.35
                    if front_lapel:
                        # Turn one lapel over the other. Its fastening rests
                        # on the chest and the lower leaf crosses the belt.
                        clasp_x, clasp_y = clasp
                        seam = x-clasp_x+.40*(y-clasp_y)
                        if y >= clasp_y:
                            level += 1.45*max(0, 1-abs(seam+1)) - 1.9*max(0, 1-abs(seam))
                    out["Druid"][py][i] = 168 if (x, y) == clasp and skin is not None else shade(MOSS, level)
                if (x, y) in cloak:
                    # The front of the armhole eclipses the trailing cloak.
                    # Along the far back the lining continues over the ribs.
                    behind_arm = skin is not None and y <= wy and (x, y) not in armhole
                    if not behind_arm or (y <= ry and sl <= x <= sr) or (x, y) in lining:
                        along = min(1, max(0, (y-sy)/(cy-sy)))
                        ridge = (sl+sr)*.5 + (cx+1-(sl+sr)*.5)*along
                        dist = x-ridge
                        fold_width = max(3, abs(wr-wl)*.64)
                        fall = .53 + .19*cos(3.4*dist/fold_width-.75*along) + .045*grain
                        if pose in REAR:
                            seam = dist+2.2-.6*cos(along*4)
                            fall += .20*max(0, 1-abs(seam+1.3)) - .32*max(0, 1-abs(seam)/1.4)
                            if y < wy:
                                fall += .06*(1-abs(offset)/(wr-wl+1))
                        fold = dist*.95 + .85*cos(along*3.4)
                        fall += .13*cos(fold) - .08 + .021*grain
                        if y < ry+1 and skin is not None:
                            fall += .06*light
                        if (x+1, y) not in cloak or (x, y+1) not in cloak:
                            fall -= .20
                        out["Thief"][py][i] = shade(SLATE, fall*(len(SLATE)-1))
            if (x, y) in hood:
                # Leave the eye, ear, cheek and jaw exactly as drawn on the
                # clean head, including the low face on the second strike.
                if pose not in REAR and y-hy >= 3 and skin is not None and point in face:
                    continue
                k = min(len(spans)-1, max(0, y-hy))
                a, b = spans[k]
                across = (x-hx-a)/max(1, b-a)
                light = 9.8 - 7*abs(across-.33) - .38*k + .50*grain
                if pose in REAR:
                    # Shade the crown around the skull; break the highlight
                    # where it rolls down into the overhanging back panel.
                    light += 1.5*cos(5.5*across+.42*k)-2.1*across
                if k >= 3:
                    # The cowl turns onto the shoulder outside the crown's
                    # width. Shade the roll locally where it meets the cape.
                    light = 6.9 + .65*grain + 1.15*((x-1, y) not in hood)
                    if pose in REAR:
                        # Turn the hanging cowl over the upper back. The
                        # shadow and adjacent lit seam travel with its tip.
                        turn = y - (sy+2.5-.42*abs(x-hx-3))
                        light += 2.1*max(0, 1-abs(turn+1)) - 4.5*max(0, 1-abs(turn)/1.6)
                if (x, y+1) not in hood or (x+1, y) not in hood:
                    light -= 1.8
                out["Thief"][py][i] = shade(RAMPS["slate"], light)
    if pose in mulfront.FRONT or pose in mulfront.TURNS:
        out.update(mulfront.dress(pose, body, protected, limbs, bow, hood))
    return rows | out


def fit_comparison(game, pose, rows, sand, previous):
    roles = fit.ROLES + NEW
    page = Image.new("RGB", (810, 524), dwarf.PAPER)
    label(page, (12, 7), "Mul outfit fit", 20)
    label(page, (797, 8), f"{pose:02}   {dwarf.NAMES[pose]}", 16, "ra")
    for col, role in enumerate(("Body base",) + NEW):
        left = 91 + col*179
        label(page, (left+80, 42), role, 16, "ma")
        # Read the earlier render directly from the lossless full-pose
        # sheet. Both tiles have the same floor origin and native scale.
        x = 123 + roles.index(role)*110
        y = 44 + 105*pose
        old = previous.crop((x, y, x+108, y+102)).resize((54, 51), Image.Resampling.NEAREST)
        new = elf.placed_tile(game, rows[role], sand, 1, 0, 0, 0)
        for line, tile in enumerate((old, new)):
            top = 66+line*228
            page.paste(tile.crop((7, 8, 47, 51)).resize(
                (160, 172), Image.Resampling.NEAREST), (left, top))
            page.paste(tile, (left+53, top+174))
    label(page, (12, 147), "Previous", 15)
    label(page, (12, 375), "Refitted", 15)
    return page


def render(game_dir, output, previous_sheet=None):
    atlas = Atlas(game_dir)
    game = atlas.game
    swatches = reference_folds(game)
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    paving = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")
                        ).convert("RGB").crop((158, 21, 212, 72))
    roles = fit.ROLES + NEW
    sheet = Image.new("RGB", (126+110*len(roles), 48+105*29), dwarf.PAPER)
    label(sheet, (12, 9), "Mul poses", 18)
    for j, role in enumerate(roles):
        label(sheet, (177+j*110, 12), role, 15, "ma")
    frames = []
    comparisons = []
    previous = Image.open(previous_sheet).convert("RGB") if previous_sheet else None
    for pose, name in enumerate(dwarf.NAMES):
        rows = draw(game, pose, swatches)
        y = 44+105*pose
        label(sheet, (10, y+27), f"{pose:02}", 14)
        label(sheet, (10, y+49), name, 13)
        for j, role in enumerate(roles):
            tile = elf.placed_tile(game, rows[role], sand, 2, 0, 0, 0)
            sheet.paste(tile, (123+j*110, y))
        page = Image.new("RGB", (820, 463), dwarf.PAPER)
        label(page, (12, 8), "Mul single classes", 20)
        label(page, (807, 8), f"{pose:02}   {name}", 16, "ra")
        for j, role in enumerate(("Original",)+NEW):
            x = 22+203*j
            label(page, (x+81, 41), "Retail Mul" if j == 0 else role, 16, "ma")
            page.paste(elf.placed_tile(game, rows[role], sand, 3, 0, 0, 0), (x, 65))
            for k, floor in enumerate((sand, paving)):
                page.paste(elf.placed_tile(game, rows[role], floor, 1, 0, 0, 0), (x+25+58*k, 225))
        label(page, (12, 286), "Retail figures and approved human outfits", 16)
        for j, (ref, caption) in enumerate(((1252, "Retail Warrior"), ("Druid", "Human Druid"),
                                            ("Psionicist", "Human Psionicist"), (724, "Retail Mage"),
                                            (630, "Retail Thief"))):
            x = 8+j*163
            if isinstance(ref, int):
                cb, f = divmod(pose, 15)
                pic = ref+cb
                if f >= game.count(pic):
                    pic, f = ref, 0
                    caption += " (idle)"
                sample = game.fr(pic, f)
                large = elf.placed_tile(game, sample, sand, 2, 0, 0, 0)
                small = elf.placed_tile(game, sample, paving, 1, 0, 0, 0)
            else:
                atlas.floor = sand
                large = atlas.tile(300, pose, ref, "Class colors", 2)
                atlas.floor = paving
                small = atlas.tile(300, pose, ref, "Class colors", 1)
            label(page, (x+80, 316), caption, 14, "ma")
            page.paste(large, (x, 344))
            page.paste(small, (x+108, 395))
        frames.append(page)
        if previous is not None:
            comparisons.append(fit_comparison(game, pose, rows, sand, previous))
    output.mkdir(parents=True, exist_ok=True)
    sheet.save(output/"mul-singles-poses.png")
    loop(frames, output/"mul-singles.gif")
    if comparisons:
        loop(comparisons, output/"mul-singles-fit.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-sheet", type=Path, help="mul-singles-poses.png from a42a969")
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_sheet)
