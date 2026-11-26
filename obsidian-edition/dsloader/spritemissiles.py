"""Shoulder and hip registration for missile gear on the Shattered Lands figures."""

from . import spriteparts as sp


# Native y/left/right of the shoulder and y of the belt. In these three
# drawings the raised bow or its arm often projects above the actual crown.
SHOOTING = {
    2095: ((7,5,10,15), (10,6,11,18), (9,4,12,17)),
    2099: ((7,3,9,15), (10,3,10,16), (10,4,12,16)),
    2055: ((6,3,10,12), (9,3,10,15), (9,5,13,15)),
    2053: ((6,3,10,12), (9,3,10,15), (9,5,13,15)),
    2061: ((7,4,11,14), (10,3,10,17), (10,4,12,18)),
    2059: ((7,3,10,14), (10,3,10,17), (10,4,12,18)),
    2072: ((10,7,15,21), (14,8,15,24), (15,9,24,26)),
    2074: ((11,7,15,22), (14,8,15,24), (15,9,24,26)),
    2068: ((6,3,9,11), (9,3,9,15), (9,5,13,15)),
    2070: ((7,6,12,12), (9,5,11,15), (9,6,14,15)),
    2093: ((5,5,11,15), (8,7,11,17), (8,4,13,18)),
    2097: ((10,8,16,18), (10,4,11,18), (12,10,20,22)),
}

# The feet point up the screen in the last combat picture. Each span sits
# on the exposed back in the native cel; the second row is its raised hip.
FALLEN = {2095:(12,5,13,6), 2099:(11,5,13,5), 2055:(9,3,10,4), 2053:(9,3,10,4),
          2061:(16,7,14,8), 2059:(11,6,12,5), 2072:(17,6,18,8), 2074:(17,7,19,8),
          2068:(9,3,10,4), 2070:(9,3,11,4), 2093:(12,5,14,6), 2097:(11,8,17,6)}

# Pigments exclusive to the three retail shooting cels, including fine
# string/grip pixels. Golden wood also occurs in hair and chitin: only its
# thin connected arcs are foreground.
BOW_HIGHLIGHTS = {2095:(49,), 2099:(48,163), 2055:(23,), 2061:(151,), 2072:(23,29,48),
                  2068:(19,29,74,174), 2093:(149,), 2097:(128,)}


# The original woman's cloak extends left of her actual moving shoulder in
# profile. Short tunics expose the gap if an item is fastened to that cloth.
WOMAN_PROFILE = {2: (8,4,8), 11: (8,6,12), 12: (8,8,14), 13: (8,10,15), 14: (8,7,12)}


def shot(parts, model, frame, own):
    y, left, right, waist = SHOOTING[model][frame-9]
    if own:
        left, right = own.at(left,y), own.at(right,y)
    # The figure turns sideways to take the front shot and opens its chest
    # toward the viewer to shoot across the screen. Fit gear to the torso.
    facing = (sp.SIDE, sp.BACK, sp.FRONT)[frame-9]
    return parts._replace(shoulders=(y,left,right), waist=waist, facing=facing)


def native_bow(rows, model, frame, own):
    source = own.source if own else rows
    extra = BOW_HIGHLIGHTS.get(model, ())
    keep = {(x,y) for y,row in enumerate(source) for x,c in enumerate(row) if c in extra}
    wood = {(x,y) for y,row in enumerate(source) for x,c in enumerate(row) if c in (179,180,181,182,183)}
    hair = sp.parts(source, model, frame, True).hair
    while wood:
        group = {wood.pop()}
        queue = list(group)
        contacts = 0
        while queue:
            x, y = queue.pop()
            for a in (-1,0,1):
                for b in (-1,0,1):
                    if not (a or b):
                        continue
                    neighbor = x+a, y+b
                    if neighbor in wood:
                        wood.remove(neighbor)
                        group.add(neighbor)
                        queue.append(neighbor)
                    if neighbor in group:
                        contacts += 1
        if len(group) >= 5 and contacts <= 4.5*len(group) and 3*len(group & hair) < len(group):
            keep.update(group)
    if own:
        keep = {(nx,y) for x,y in keep for nx in range(own.at(x,y), own.at(x+1,y))}
    return keep
