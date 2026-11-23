"""Hood panels in native pixels, anchored to the head in each pose."""

from elfoutfits import RAMPS as ELF_FABRICS

# A continuous turned rim opens at the cheeks. The rear panel ends in a
# folded point above the free hair. A dot leaves the underlying pixel alone.
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


def human_woman(rows, paint, regions, cloak, head, base, pose):
    top = len(paint) - len(rows)
    left = (len(paint[0]) - len(rows[0])) // 2
    panel, ox, oy = PANELS[pose]
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
            dy, dx = sy - oy, sx - ox
            if not (0 <= dy < len(panel) and 0 <= dx < len(panel[dy])):
                continue
            mark = panel[dy][dx]
            if mark == "." or regions[y][x]:
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
    ramp = next(ramp for name, ramp in ELF_FABRICS.items() if name in role.split("/"))
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
