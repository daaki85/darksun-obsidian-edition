"""Visible elf garment bindings and class insignia that retain their own dye under armor."""

from . import classoutfits as co


def protected(frame, role, pose, model):
    """Native pixels of the cuffs, hem, sword belt and sash on this specific drawing."""
    chest = set(frame.regions[co.CHEST])
    legs = set(frame.regions[co.LEGS])
    arms = set(frame.regions[co.ARMS])
    garment = chest | legs
    # Elf arm ownership also covers exposed flesh on the swinging foreground arm.
    keep = arms.intersection(frame.regions[co.FOREARM])
    members = role.split("/")
    # The man's four profile walks have two extra paint columns on each side
    # of the region sheet, for the trailing mantle.
    margin = 6 if model == 2061 and 11 <= pose <= 14 else 4
    dy = -1 if pose == 28 else 1  # the fallen sprite lies feet up
    neckline = min((y * dy for x, y in chest), default=0)
    skirt_top = min((y * dy for x, y in legs), default=None)
    for x, y in garment | arms:
        color = frame.image[y + 4][x + margin]
        # Preserve the sewn cap and its worn tip; the remaining jerkin or
        # kilt can take the material dye right up to this join.
        if (x, y) in arms and color in (58, 121, 168, 186, 199, 155, 40, 72, 73):
            keep.add((x, y))
        if (x, y) in garment and color == 169:  # sword-belt buckle
            keep.add((x, y))
        if "Cleric" in members or role == "Psionicist":
            # Keep the native collar at the upper edge of the visible panel.
            # Restrict it to the shoulder so a crossing hand cannot create a
            # new colored line down the middle of the breast.
            if (x, y) in chest and y * dy <= neckline + 2 and (x, y - dy) not in chest:
                keep.add((x, y))
        if "Cleric" in members:
            # The two rows forming the lower robe binding. The edge rises
            # and falls separately in each column as the legs cross.
            if (x, y) in legs and (x, y + dy) not in legs:
                keep.add((x, y))
                if (x, y - dy) in legs:
                    keep.add((x, y - dy))
            # A plum facing on the cream hem remains plum around a steel skirt.
            if "Preserver" in members and (x, y) in legs and color in (174, 175, 58, 74, 113, 59):
                keep.add((x, y))
        if "Psionicist" in members and len(members) > 1:
            # These are the original wrap and its turned end. The teal is
            # exclusive to the sash and matching fitting on these builds.
            if color in (69, 70, 71, 72, 73, 40):
                keep.add((x, y))
        # Follow the waistband across the actual junction of jerkin and skirt.
        # Retain both lips on the leather belt and the single Psionicist wrap.
        if "Fighter" in members or role in ("Psionicist", "Gladiator"):
            if (x, y) in legs and y * dy == skirt_top:
                keep.add((x, y))
            if (x, y) in chest and (x, y + dy) in legs:
                keep.update(((x, y), (x, y + dy)))
    return keep
