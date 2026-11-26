"""Native dwarf garment details left visible when the armor material is dyed."""

from . import classoutfits as co


# When the usual strap disappears under an arm, follow the exposed woven edge
# of the teal wrap or the leather turn where the baldric meets guard or belt.
OCCLUDED_TRIM = {
    ("Psionicist", 13): ((4, 6), (5, 6), (5, 7)),
    ("Psionicist", 17): ((11, 9), (12, 10), (11, 11), (11, 12)),
    ("Gladiator", 13): ((5, 5), (5, 6), (6, 7)),
    ("Gladiator", 16): ((9, 8), (8, 10), (9, 10)),
    ("Gladiator", 21): ((8, 9), (7, 11), (8, 11)),
}


def protected(frame, role, pose, model):
    combat, index = divmod(pose, 15)
    parent_role = "Thief" if role == "Psionicist/Thief" else role.split("/")[0]
    chest = set(frame.regions[co.CHEST])
    legs = set(frame.regions[co.LEGS])
    arms = set(frame.regions[co.ARMS])
    keep = set(OCCLUDED_TRIM.get((role, pose), ()))

    # Arm armor dyes the face and shadow of the guard. Its small bone or bronze
    # crest and the belt toggle retain the colors that distinguish the two kits.
    keep.update((x, y) for x, y in arms if frame.image[y + 4][x + 4] in (155, 168, 186, 199))
    keep.update((x, y) for x, y in legs if frame.image[y + 4][x + 4] == 169)

    if parent_role in ("Fighter", "Psionicist"):
        # The Gladiator's authored cross-body strap traces the same shoulder-to-
        # hip line as the Fighter baldric and single Psionicist's woven band.
        strap = co.frames("Gladiator", combat, model)[index].regions[co.CHEST]
        keep.update(chest.intersection(strap))
    elif parent_role == "Gladiator":
        # A leather edge stays visible where the narrow strap crosses the bare chest.
        keep.update((x, y) for x, y in chest if (x - 1, y) not in chest and (x + 1, y) in chest)
    elif parent_role == "Cleric":
        # Retain the linen binding along the actual hem, including the overturned fall.
        dy = -1 if pose == 28 else 1
        keep.update((x, y) for x, y in legs if (x, y + dy) not in legs)

    # In the man's first wind-up the raised arm hides the usual cross-body
    # line. The kilt's turned leather hem and the near teal fold still show.
    if model == 2055 and pose == 15:
        if role == "Gladiator":
            keep.update(((3, 17), (4, 17), (5, 17)))
        elif role == "Psionicist":
            keep.update(((4, 8), (4, 9), (3, 9), (2, 10)))

    if role != parent_role:
        # The actual differences contain the second class's shoulder, cowl or sash.
        # The shoulder crest is already reserved above; the guard face can take dye.
        parent = co.frames(parent_role, combat, model)[index]
        keep.update((x, y) for x, y in chest | legs
                    if frame.image[y + 4][x + 4] != parent.image[y + 4][x + 4])
    return keep
