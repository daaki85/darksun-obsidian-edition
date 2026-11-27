"""Paint the anatomical planes exposed by the half-elves’ changed builds and hair."""

from limbstrokes import quiet_highlights

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


# With the bun lifted, the woman's scapula and spine show where the human's
# long hair used to fall. The near shoulder rises and falls across the walk.
BACK_RIBS = {1: (7, 8), 7: (6, 8), 8: (7, 8), 9: (8, 8), 10: (7, 8)}


def female_back(pose, body, pad):
    if pose not in BACK_RIBS:
        return []
    cx, cy = BACK_RIBS[pose]
    changes = []
    for dx, dy, shade in ((0, 0, 145), (1, 0, 144), (0, 1, 144),
                          (1, 1, 145), (2, 2, 144), (3, 2, 133),
                          (3, 3, 134), (2, 4, 133)):
        x, y = pad+cx+dx, pad+cy+dy
        old = body[y][x]
        if old in (130, 131, 132):
            changes.append((x, y, old, shade))
    return changes


# Centres of the near deltoid, lower ribs, iliac crest and weight-bearing
# thigh, in each native half-elf cel. The two figures widen/narrow different
# pixels below the shoulder, and do not share the same front leg on each step.
WOMAN_PLANES = (
    (3,7, 8,11, 6,14, 5,18), (5,8, 10,11, 7,14, 6,18), (3,7, 5,11, 4,14, 3,18),
    (3,7, 8,11, 5,14, 5,18), (5,7, 10,10, 8,13, 10,17),
    (3,7, 9,11, 7,14, 6,18), (3,7, 8,10, 6,13, 5,17),
    (4,8, 8,11, 7,15, 6,19), (5,8, 9,11, 8,15, 8,19),
    (6,8, 10,11, 9,15, 8,19), (6,8, 9,11, 7,15, 10,19),
    (6,8, 8,11, 6,14, 7,18), (8,8, 10,11, 8,14, 12,17),
    (11,8, 12,12, 10,15, 10,18), (8,8, 9,11, 7,14, 7,18),
    (6,15, 9,18, 7,22, 6,26), (9,10, 12,12, 10,14, 8,18),
    (13,8, 15,10, 13,13, 12,16), (3,10, 7,14, 4,17, 8,21),
    (4,16, 8,19, 7,22, 5,26), (10,8, 15,11, 15,14, 19,17),
    (11,14, 15,18, 14,22, 14,26), (12,9, 14,12, 11,16, 8,19),
    (11,7, 13,10, 11,13, 8,17), (7,8, 7,11, 6,14, 4,18),
    (4,10, 7,13, 6,16, 5,19), (5,10, 9,13, 8,17, 8,21),
    (2,8, 7,11, 7,14, 4,17), (6,11, 9,8, 9,6, 7,4),
)
MAN_PLANES = (
    (3,7, 9,11, 6,14, 5,18), (4,8, 10,11, 7,14, 12,19), (2,8, 5,11, 4,14, 3,18),
    (2,7, 8,11, 5,14, 4,18), (4,7, 9,10, 6,13, 9,17),
    (3,7, 9,10, 6,13, 9,17), (2,7, 8,10, 5,13, 4,17),
    (2,8, 7,11, 5,14, 4,18), (1,8, 5,11, 3,14, 2,18),
    (2,8, 7,11, 5,14, 9,18), (4,8, 8,11, 6,14, 10,18),
    (1,8, 4,11, 3,14, 4,18), (5,8, 6,11, 5,14, 9,17),
    (3,8, 5,12, 4,15, 6,18), (4,8, 7,11, 5,14, 5,18),
    (5,15, 8,18, 5,22, 4,26), (10,9, 13,10, 10,12, 8,15),
    (12,8, 16,10, 14,12, 12,15), (3,10, 7,13, 4,17, 8,21),
    (5,16, 9,19, 8,22, 12,26), (14,8, 17,10, 15,13, 14,16),
    (11,14, 16,18, 15,21, 15,25), (6,9, 8,12, 6,15, 4,18),
    (6,7, 7,10, 5,12, 3,16), (5,8, 8,11, 6,14, 5,18),
    (4,11, 7,14, 5,17, 4,20), (6,10, 8,14, 8,17, 7,21),
    (3,7, 9,11, 6,14, 5,18), (7,16, 9,13, 10,10, 12,6),
)

# Adjacent steps of the same skin ramp describe a round shoulder, the turn
# of the near ribs and the light down the leg. The back carries a shorter,
# oblique scapula, and the edge-on chest has just a two-pixel turning plane.
PINKS = (134, 133, 132, 131, 130, 144, 145, 146, 147, 148, 149, 150, 151)
SHOULDER = ((0,0,2), (1,0,2), (-1,1,1), (0,1,2), (1,1,1), (1,2,-1), (2,2,-2))
RIBS = {
    "front": ((-2,0,1), (-1,0,2), (0,0,1), (0,1,-2), (1,1,-2), (1,2,-1), (2,2,-2)),
    "back":  ((-2,-1,2), (-1,-1,1), (-1,0,2), (0,0,1), (0,1,-2), (1,2,-2)),
    "side":  ((-1,-1,1), (-1,0,2), (0,0,1), (0,1,-2), (1,1,-2)),
}
HIP_TURN = ((-1,0,1), (0,-1,1), (0,0,2), (1,0,1), (1,1,-1), (2,1,-2))
THIGH = ((0,-1,1), (0,0,2), (0,1,1), (1,0,-1), (1,1,-2), (1,2,-1))



# The cut below the shoulder changes how much of the far arm or bent leg
# shows beside the torso. Short runs turn from the elbow cap into its crease,
# or from the loaded knee under the lifted thigh. Other joints keep the donor.
MAN_JOINTS = {
    1: ((14,8,(133,134)), (14,9,(130,132)), (15,10,(144,133)), (16,11,(132,)),
        (10,17,(147,149,147)), (11,18,(131,146))),
    7: ((11,8,(132,)), (11,9,(130,133)), (12,10,(132,)), (9,17,(147,))),
    8: ((10,11,(146,)), (10,12,(132,145)), (6,19,(146,147))),
    9: ((11,9,(133,131)), (12,10,(132,130)), (13,11,(132,)), (8,17,(147,148))),
    10: ((9,17,(147,148)), (9,18,(130,146)), (5,19,(146,))),
    11: ((3,11,(132,133)), (3,12,(131,133)), (3,18,(147,148))),
    12: ((2,10,(147,145)), (3,11,(130,)), (9,17,(147,148)),
         (9,19,(147,146)), (10,20,(132,))),
    13: ((3,9,(148,146,145)), (2,10,(147,146)), (4,11,(130,)),
         (4,12,(147,145)), (4,17,(147,149,147)), (3,18,(146,147,145)),
         (5,19,(144,)), (4,20,(146,148,146))),
    14: ((10,10,(147,146)), (10,11,(144,146)), (4,17,(147,148))),
    18: ((3,12,(148,147)), (7,20,(147,148)), (8,21,(145,147))),
    21: ((22,16,(147,146)), (23,17,(148,145)), (20,23,(147,145))),
    22: ((13,9,(147,144)), (14,10,(145,147)), (16,11,(131,)),
         (8,17,(147,145))),
}
WOMAN_JOINTS = {
    1: ((13,9,(145,147)), (14,10,(144,)), (14,11,(131,)), (14,12,(145,)),
        (11,18,(146,145)), (11,19,(144,130))),
    7: ((12,10,(131,145)), (12,11,(147,144)), (12,12,(145,130)),
        (10,17,(145,)), (10,18,(131,))),
    8: ((14,10,(146,)), (14,11,(144,)), (14,12,(131,)), (11,18,(144,))),
    9: ((15,10,(146,)), (15,11,(132,)), (14,12,(145,130)),
        (11,18,(147,145)), (11,19,(131,133))),
    10: ((14,9,(146,)), (14,10,(132,)), (14,11,(145,)), (10,18,(146,))),
    12: ((5,10,(147,145)), (5,11,(146,131)), (5,12,(144,)),
         (12,17,(146,)), (12,18,(145,))),
    13: ((9,10,(146,148)), (9,11,(144,)), (10,12,(130,146)),
         (11,17,(145,133)), (11,18,(132,))),
    14: ((11,11,(147,145)), (11,12,(144,146)), (10,18,(132,))),
    18: ((3,20,(146,148)), (3,21,(130,)), (7,21,(145,147))),
    21: ((19,16,(147,145)), (20,17,(145,)), (15,22,(130,131,132))),
    22: ((18,9,(145,146)), (19,10,(146,145)), (20,11,(131,)),
         (9,17,(145,)), (9,18,(131,))),
}

def body_planes(pose, body, pad, female, facing, changes, protected, head_and_bow):
    anchors = (WOMAN_PLANES if female else MAN_PLANES)[pose]
    final = {(x,y): shade for x,y,_,shade in changes}
    old_shades = final.copy()
    for i, stroke in enumerate((SHOULDER, RIBS[facing or "back"], HIP_TURN, THIGH)):
        cx, cy = anchors[2*i:2*i+2]
        for dx, dy, shift in stroke:
            x, y = cx+dx, cy+(-dy if pose == 28 else dy)
            if (x, y) in protected:
                continue
            px, py = x+pad, y+pad
            if not (0 <= py < len(body) and 0 <= px < len(body[py])):
                continue
            shade = old_shades.get((px,py), body[py][px])
            if shade in PINKS:
                # The retail contours and hottest glints are already drawn.
                if shade == 134 or shade >= 149:
                    continue
                target = max(0, min(len(PINKS)-1, PINKS.index(shade)+shift))
                final[px,py] = PINKS[target]
    joints = WOMAN_JOINTS if female else MAN_JOINTS
    for left, y, tones in joints.get(pose, ()):
        for x, shade in enumerate(tones, left):
            py, px = y+pad, x+pad
            native = body[py][px]
            if (x, y) not in head_and_bow and native in PINKS:
                final[px,py] = shade
    # Painting the half-elf's own ribs and joints can leave an isolated
    # highlight even when the parent skin was quiet. Keep continuous ridges.
    guarded = {(x+pad, y+pad) for x,y in protected}
    quiet_highlights(body, PINKS, guarded, final)
    return [(x,y,body[y][x],shade) for (x,y),shade in final.items() if body[y][x] != shade]


GLADIATOR_LEATHER = {129, 194, 195, 203, 204, 205, 207, 208}


def leather_contact(pose, body, outfit, pad, female, protected):
    # Read the actual material next to the fitted skin. A diagonal harness
    # passes in front of the ribs; the skirt casts a narrower shadow down
    # the thigh. A swinging wrist in front of either stays lit.
    anchors = (WOMAN_PLANES if female else MAN_PLANES)[pose]
    _, sy, rx, ry, hx, hy, _, ty = anchors
    dy = -1 if pose == 28 else 1
    for cx, cy, width, height in ((rx, ry, 3, abs(ry-sy)+1), (hx, hy, 4, abs(ty-hy)+1)):
        for y in range(cy-height, cy+height+1):
            py = y+pad
            if not 1 <= py < len(body)-1:
                continue
            for x in range(cx-width, cx+width+1):
                px = x+pad
                if (x, y) in protected or not 1 <= px < len(body[py])-1:
                    continue
                shade = body[py][px]
                if shade not in PINKS[3:] or outfit[py][px] != shade:
                    continue
                above = outfit[py-dy][px]
                if above != body[py-dy][px] and above in GLADIATOR_LEATHER:
                    outfit[py][px] = PINKS[PINKS.index(shade)-2]
