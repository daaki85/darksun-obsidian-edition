"""Finish the short halfling and Mul harnesses within their existing pose cuts."""

# Translate the authored hide and bronze ramps to colours which remain distinct
# in the map palette. The old bronze shoulder and kilt stitches are leather now.
OILED = {208: 208, 88: 208, 204: 204, 89: 129, 90: 129, 207: 204,
         91: 204, 92: 207, 93: 195, 94: 207, 95: 205, 96: 205,
         97: 205, 98: 194, 99: 205, 100: 194,
         168: 205, 169: 205, 170: 205, 171: 194}


# The shared suit fitter keeps a class-coloured strip around the waist.
# Include the new hide midtones, as well as its separately encoded shadow.
BINDING = frozenset(OILED.values()) | {89}


def dress(garment, body, shoulder, buckle, flap, facing=1):
    sx, sy = shoulder
    bx, by = buckle
    (waist_x, _), (tip_x, tip_y) = flap
    leather = {(x, y): c for y, row in enumerate(garment) for x, c in enumerate(row)
               if c in OILED and c != body[y][x]}
    for (x, y), source in leather.items():
        shade = OILED[source]
        height = (y-by)*facing
        if height < -1:
            # At the far edge of the baldric a narrow contact shadow rests
            # on the moving ribcage. Its near edge keeps the rolled highlight.
            along = min(1, max(0, (y-sy)/(by-sy)))
            strap = sx+(bx-sx)*along
            if (x-strap)*facing > .3 and abs(x-strap) <= 2 and (x+facing, y) not in leather:
                shade = 208
        elif height > 0:
            # A folded hide flap ends against the thigh. Its return edge is
            # darker than the narrow glancing reflection on the uphill fold.
            along = (y-by)/(tip_y-by)
            seam = (x-(waist_x+(tip_x-waist_x)*along))*facing
            if -.95 <= seam < .0:
                shade = 194 if .15 < along < .47 else 205
            elif 0 <= seam < 1.05:
                shade = 208 if along < .72 else 204
            if (x, y+facing) not in leather and (x-facing, y) in leather:
                shade = 204 if shade in (194, 205) else 208
        if shade == 129:
            # This hide index maps to dark brown when drawn. It remains
            # distinct from skin shadow 129 in the authored equipment mask.
            shade = 89
        elif shade == body[y][x]:
            shade = 204 if shade != 204 else 207
        garment[y][x] = shade

    # The strap finishes in one bronze buckle. When the forearm passes
    # directly in front, it can cover most or all of the hardware.
    for point in ((bx, by), (bx, by-facing), (bx-facing, by), (bx+facing, by)):
        if point in leather:
            x, y = point
            garment[y][x] = 169
            break
