"""Foreground pixels for a belt-carried weapon, in the equipped picture's coordinates."""

from . import classoutfits as co, halfelf, spritebelts, spritegrips, spriteparts as sp


def _retail_cape(rows, model, frame, combat, own):
    """The green retail cloak and its dark lining, through the half-elf's narrower cut."""
    from .spritegear import CLOAK_MODEL, cloak_template

    if model != CLOAK_MODEL:
        return set()
    source = own.source if own else rows
    template = cloak_template(source, model, frame, combat)
    if not template:
        return set()
    pixels = template[1]
    if combat and frame == sp.DEAD_FRAME:
        pixels = {(len(source[0])-1-x, len(source)-1-y) for x, y in pixels}
    if own:
        return {(nx, y) for x, y in pixels for nx in range(own.at(x, y), own.at(x+1, y))
                if (nx, y) not in own.not_cloak and 0 <= nx < len(rows[y]) and rows[y][nx] is not None}
    return set(pixels)


def _profile(cape, layer, rows, frame, combat, pad):
    """Keep the flap over the near hip; the freely trailing train passes behind the sheath."""
    if not cape or layer not in (*co.MAP_OUTFITS.values(), *co.HALF_ELF_SOURCES):
        return cape
    waist = spritebelts.waist(layer, combat, frame)
    if not waist:
        return cape
    # Follow the turned hip and thigh on the same pose's short garment. The
    # original woman's stock silhouette includes the cloak itself, so it cannot
    # tell us where the back edge of her hip lies underneath the hanging fabric.
    role = "Fighter" if layer in co.HALF_ELF_SOURCES else "Gladiator"
    under = co.frames(role, combat, layer)[frame].canvas(rows, pad)
    back = min(x for x, y in waist)
    belt_y = min(y for x, y in waist)
    near = set()
    for x, y in cape:
        X, Y = x+pad, y+pad
        if not (0 <= Y < len(under) and 0 <= X < len(under[Y])):
            continue
        if under[Y][X] is not None and (y < belt_y or x >= back):
            near.add((x, y))
    return near


def visible(rows, model, frame, combat, own, costume, parts, pad, fabric=()):
    """Return padded pixels in front of the sheath. FABRIC is the actual equipped cape paint."""
    drawn = costume.canvas(rows, pad) if costume else None
    def pigment(x, y):
        if drawn is not None:
            X, Y = x+pad, y+pad
            return drawn[Y][X] if 0 <= Y < len(drawn) and 0 <= X < len(drawn[Y]) else None
        return rows[y][x] if 0 <= y < len(rows) and 0 <= x < len(rows[y]) else None

    foreground = set(parts.hair)
    if costume:
        foreground.update(costume.head)
        foreground.update(costume.regions[co.FOREARM])
        cape = {(x, y) for x, y, _ in costume.cloak if pigment(x, y) is not None} if costume.native_cloak else set()
    else:
        cape = _retail_cape(rows, model, frame, combat, own)

    # A separate outer garment may be longer than the class's attached
    # mantle. Its painter knows exactly where the worn cloth stopped at a
    # cuff or strand of hair. Virtual cloak templates do not cover bare hips.
    cape.update((X-pad, Y-pad) for X, Y in fabric)
    if parts.facing == sp.SIDE:
        layer = (halfelf.MAN if model == 2061 else halfelf.WOMAN) if own else model
        cape = _profile(cape, layer, rows, frame, combat, pad)

    hands = spritegrips.positioned(rows, model, frame, combat, own, parts.hands)
    # The author's foreground mask owns the cuffs. Endpoint registration
    # picks up the actual finger pixels extending past them, including the
    # stock figure's hands where no class-layer mask exists.
    for hx, hy in hands.values():
        for y in range(hy-2, hy+3):
            for x in range(hx-2, hx+3):
                p = pigment(x, y)
                if p is None or (x-hx)**2+(y-hy)**2 > 6:
                    continue
                skin = 128 <= p <= 153 or model == sp.KREEN and p in (179, 180, 181, 182, 183, 201)
                if skin or p in sp.MODELS[model][1]:
                    foreground.add((x, y))
    return {(x+pad, y+pad) for x, y in foreground | cape}
