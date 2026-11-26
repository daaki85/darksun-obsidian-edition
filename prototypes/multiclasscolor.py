"""Shattered Lands palette steps for fitted multiclass hoods and shoulder scales."""

# The mids include alternating warm/cool threads. Keep the recessed face rim
# darker than the crown, even on linen. Auxiliary slates occur on half-elves.
SLATE = (208, 17, 18, 19, 20, 21, 22, 49, 23, 24, 25, 50, 26, 27, 28, 29)
LEAF = (208, 17, 69, 188, 53, 189, 225, 54, 226, 55, 227, 55, 56, 227, 56, 57)
HOOD_RAMPS = {
    "Cleric": (208, 207, 204, 205, 194, 206, 118, 120, 121, 61, 122, 123, 199, 125, 62, 155),
    "Druid": LEAF,
    "Preserver": (208, 17, 174, 112, 175, 113, 58, 74, 115, 59, 117, 60, 118, 239, 232, 233),
    "Ranger": LEAF,
    "Fighter": (208, 88, 204, 89, 90, 207, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100),
    "Psionicist": (208, 17, 69, 18, 69, 70, 210, 70, 211, 71, 40, 71, 72, 40, 72, 73),
}


def hood_class(role):
    members = role.split("/")
    return next(name for name in HOOD_RAMPS if name in members)


HOOD_DYES = {name: dict(zip(SLATE, ramp, strict=True)) for name, ramp in HOOD_RAMPS.items()}
for dye in HOOD_DYES.values():
    for extra, shade in ((48, 20), (30, 28), (31, 29)):
        dye[extra] = dye[shade]

# The green reflection lives on the underside. Reserve bone for the narrow
# upward-facing ridge so an edge-on scale still reads against the leaf cloth.
LEAF_BONE = (208, 207, 188, 53, 54, 55, 56, 169, 199, 62)


def dye_fitted_hoods(outfits, points):
    """Recolor visible hood fabric after caps, hands, sashes and hair overlap it."""
    thief, body = outfits["Thief"], outfits["Body base"]
    cloth = [(x, y, thief[y][x]) for x, y in points
             if 0 <= y < len(thief) and 0 <= x < len(thief[y]) and thief[y][x] != body[y][x]]
    dressed = dict(outfits)
    for name, rows in outfits.items():
        if "/" in name and "Thief" in name:
            dye = HOOD_DYES[hood_class(name)]
            result = [row[:] for row in rows]
            for x, y, color in cloth:
                if color in dye and rows[y][x] == color:
                    result[y][x] = dye[color]
            dressed[name] = result
    return dressed
