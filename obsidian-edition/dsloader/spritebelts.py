"""Fit a belt to the waist of a registered pose, underneath foreground cloth and limbs."""

from functools import lru_cache

from . import classoutfits as co


@lru_cache(maxsize=1024)
def waist(layer, combat, frame):
    """The waist on the basic jerkin. Every outfit on this figure uses the same hips."""
    role = "Warrior" if layer in (2095, 2099) else "Fighter"
    fit = co.frames(role, combat, layer)[frame]
    if fit.belt is not None:
        return fit.belt
    legs = fit.regions[co.LEGS]
    if not legs:
        return ()
    # The original human man's and elves' buckles sit on the last jerkin row;
    # the dwarves and both human-woman based figures put them on the first kilt row.
    down = -1 if combat and frame == 13 else 1
    seam = min(down * y for x, y in legs) * down
    y = seam - down if layer in (2095, 2059, 2061, 306) else seam
    around = [x for x, yy in legs if yy == seam]
    if y != seam:
        around += [x for x, yy in fit.regions[co.CHEST] if yy == y]
    return tuple((x, y) for x in range(min(around), max(around) + 1))


def visible(layer, combat, frame, costume, rows, parts, stock_cloak):
    """Clip the fitted line to this outfit, including the actual bare and fallen poses."""
    if costume is not None and costume.belt is not None:
        return costume.belt
    points = waist(layer, combat, frame)
    if costume:
        cloth = set(costume.regions[co.CHEST]) | set(costume.regions[co.LEGS])
        covered = set(costume.head) | set(costume.regions[co.FOREARM]) | set(costume.regions[co.BOW])
        if costume.native_cloak:
            covered.update((x, y) for x, y, _ in costume.cloak)
        return [(x, y) for x, y in points if (x, y) in cloth and (x, y) not in covered]

    # The stock woman's green cloak and her half-elf daughter's purple cloak
    # hide both the girdle and its fastening when seen from the back.
    pose = 15 * combat + frame
    if layer in (2099, 307) and pose in (1, 7, 8, 9, 10, 18, 19, 20, 25):
        return []
    skip = set(parts.hair)
    for hx, hy in parts.hands.values():
        skip.update((x, y) for y in range(hy - 2, hy + 2) for x in range(hx - 1, hx + 2))
    return [(x, y) for x, y in points if 0 <= y < len(rows) and 0 <= x < len(rows[y])
            and rows[y][x] not in (None, 254) and rows[y][x] not in stock_cloak
            and (x, y) not in skip]
