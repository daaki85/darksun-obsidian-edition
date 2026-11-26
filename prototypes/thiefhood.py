"""Hood panels in native pixels, anchored to the head in each pose."""

from elfoutfits import RAMPS as ELF_FABRICS
from multiclasscolor import hood_class

# A continuous turned rim opens at the cheeks. The rear crown folds
# into a longer panel at the nape. A dot leaves the underlying pixel alone.
FRONT = (
    "...23332...", "..2455432..", ".235322231.", ".2431...131",
    "2341.....21", "231......12", "231......12", ".32......1.",
)
BACK = (
    "...2332...", "..345432..", ".34343332.", "2342343321",
    "2321234321", ".232123321", ".22321121.", "..233221..", "...2311...", "....21....",
)
SIDE = (
    "...23332..", "..34554321", ".234433221", ".23332211.",
    "2322321...", "232231....", "23121.....", "2321......", ".21.......",
)
WINDSWEPT = (
    "....233321...", "...34544321..", "..3432343321.", ".24323232321.",
    ".23222322121.", "23211...1121.", "231.......21.", ".21.......1..",
    ".21..........",
)
FALL = (
    "...2321....", "..3443321..", ".345433321.", "23332233221",
    ".232112321.", "..2222311..", "....211....",
)
# Upper-left corner in native picture coordinates (idle, walk, then combat).
PANELS = (
    (FRONT, 3, -1), (BACK, 5, -1), (SIDE, 0, -1),
    (FRONT, 3, -1), (FRONT, 5, -1), (FRONT, 4, -1), (FRONT, 3, -1),
    (BACK, 4, -1), (BACK, 5, -1), (BACK, 6, -1), (BACK, 5, -1),
    (SIDE, 4, -1), (SIDE, 7, -1), (SIDE, 9, -1), (SIDE, 5, -1),
    (FRONT, 6, 8), (WINDSWEPT, 4, -1), (FRONT, 11, 0),
    (SIDE, 2, 2), (BACK, 2, 8), (BACK, 9, -1),
    (FRONT, 10, 6), (SIDE, 11, 0), (SIDE, 11, 0),
    (FRONT, 4, -1), (SIDE, 1, 2), (FRONT, 3, 2),
    (SIDE, 0, 2), (FALL, 2, 10),
)
SLATE = (17, 19, 21, 24, 26, 28)


OLD_SLATE = frozenset((*range(17, 32), 48, 49, 50, 208))


# Secondary panels in native coordinates. The eight rear-facing drawings
# need a nape fold that follows the shoulders all the way onto the cloak.
# The strike and recoil instead close the crown above the moving head.
SEAMS = {
    1: (7, ((7, "232321"), (7, "342321"), (7, "323221"), (7, "23421"), (7, "2321"), (8, "321"))),
    7: (7, ((6, "232321"), (6, "342321"), (6, "323221"), (6, "23421"), (7, "321"), (8, "21"))),
    8: (6, ((6, "2323321"), (6, "3432321"), (5, "234232321"), (5, "23234321"),
            (6, "2323321"), (8, "2321"), (9, "321"))),
    9: (6, ((7, "23234321"), (7, "23423321"), (7, "22343221"), (8, "232321"),
            (9, "23421"), (10, "321"))),
    10: (7, ((7, "2323321"), (6, "23432321"), (6, "23234321"), (7, "2323321"), (8, "23221"))),
    18: (7, ((8, "21"), (7, "321"), (5, "2321"), (2, "234321"), (2, "32321"),
             (2, "23221"), (3, "23421"), (4, "321"))),
    19: (15, ((6, "23221"), (2, "23432321"), (2, "23234321"), (3, "2323321"),
              (5, "23421"), (5, "321"))),
    20: (2, ((17, "2321"), (17, "23321"), (17, "234321"), (16, "2323321"),
             (16, "232321"), (16, "23421"), (17, "321"))),
    16: (0, ((14, "21"), (14, "321"), (14, "2321"), (14, "2321"), (14, "321"), (15, "21"))),
    27: (0, ((4, "23321"), (3, "343321"), (3, "323221"))),
}


def human_woman(rows, paint, regions, cloak, head, base, pose):
    top = len(paint) - len(rows)
    left = (len(paint[0]) - len(rows[0])) // 2
    panel, ox, oy = PANELS[pose]
    stitches = {(ox + x, oy + y): mark for y, strip in enumerate(panel)
                for x, mark in enumerate(strip) if mark != "."}
    if pose in SEAMS:
        start_y, strips = SEAMS[pose]
        for dy, (start_x, strip) in enumerate(strips):
            stitches.update(((start_x + dx, start_y + dy), mark) for dx, mark in enumerate(strip))
    for y, row in enumerate(paint):
        for x, old in enumerate(row):
            sx, sy = x - left, y - top
            inside = 0 <= sy < len(rows) and 0 <= sx < len(rows[0])
            under = base[y][x]
            if under is None and inside:
                under = rows[sy][sx]
            # Previously the entire hair mask was repainted slate. Restore
            # its loose ends; the new hood has its own silhouette.
            old_cloth = old in OLD_SLATE
            if head[y][x] is not None:
                if not old_cloth:
                    continue  # native face, including black eyes and mouth
                row[x] = None
                cloak[y][x] = None
            mark = stitches.get((sx, sy))
            if mark is None or regions[y][x]:
                continue
            if head[y][x] is None and not old_cloth and under not in (None, 255):
                continue  # the hand and weapon pass in front
            rank = int(mark)
            row[x] = SLATE[rank]
            cloak[y][x] = rank + 1


# Side idle and the four profile steps. The small folded crown projects
# above and behind the hair; its turned seam runs down towards the nape.
ELF_CROWNS = {
    2059: {2: 4, 11: 5, 12: 9, 13: 5, 14: 6},
    2061: {2: 4, 11: 3, 12: 7, 13: 5, 14: 7},
}
ELF_PANEL = ("..23321.", ".3432321", "2322321.", "23121...", ".211....")


def elf_profile(model, role, pose, rows, paint, folds):
    anchor = ELF_CROWNS[model][pose]
    left = (len(paint[0]) - len(rows[0])) // 2
    top = len(paint) - len(rows)
    # Use the same primary garment as the original multicolored outfit.
    ramp = ELF_FABRICS[hood_class(role) if "/" in role else "Thief"]
    for dy, strip in enumerate(ELF_PANEL):
        y = dy - 1
        for dx, mark in enumerate(strip):
            x = anchor - 3 + dx
            if mark == ".":
                continue
            px, py = x + left, y + top
            on_body = y >= 0 and 0 <= x < len(rows[y]) and rows[y][x] is not None
            if on_body and folds[py][px] is None:
                continue  # Keep the original face opening and ear.
            rank = int(mark)
            paint[py][px] = ramp[rank]
            folds[py][px] = rank + 1

    # Three warm pixels enclosed between the crown and the turned brim,
    # and one at the rear of the same fold. The ear below stays in front.
    if model == 2059 and pose == 13:
        for x, y, rank in ((6, 1, 2), (7, 1, 2), (8, 1, 1), (4, 2, 2)):
            paint[top + y][left + x] = ramp[rank]
            folds[top + y][left + x] = rank + 1
