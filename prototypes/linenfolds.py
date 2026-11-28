"""Pose guides for the human Priest and the cream skirts in the SL figures."""

from statistics import mean

# X coordinates of the Priest's lit fold where it leaves the shoulder, crosses
# the waist and turns at the hem. The thrown skirt changes direction on impact.
PRIEST_FOLD = (
    (6,7,4), (8,8,7), (3,2,0), (6,6,4), (7,9,5), (4,7,9), (7,5,7),
    (4,2,6), (2,4,5), (6,3,8), (5,5,7), (7,2,-1), (8,4,6), (6,1,-1),
    (7,3,0), (4,2,4), (8,9,11), (21,18,15), (2,4,1), (6,6,3),
    (17,18,15), (14,11,14), (2,2,5), (3,4,1), (4,5,3), (6,8,5),
    (6,4,7), (7,7,9), (6,5,3),
)
LINEN = (208, 204, 207, 205, 194, 206, 61, 199, 62, 63)
# A short set of discrete value planes keeps the raised linen warm in Ravager.
VALUE = {**dict(zip(LINEN, (0,1,2,3,4,5,6,7,8,9))), 155:8, 197:5, 212:5,
         213:6, 214:7, 215:8}


def priest(cloth, pose, waist):
    cloth = {p: VALUE[ink] for p, ink in cloth.items() if ink in VALUE}
    if not cloth:
        return {}
    top = min(y for x, y in cloth)
    hem = max(y for x, y in cloth)
    waist = max(top+1, min(hem-1, waist if waist is not None else (top+hem)//2))
    shoulder, hip, tip = PRIEST_FOLD[pose]
    edits = {}
    for (x, y), shade in cloth.items():
        if y <= waist:
            ridge = shoulder + (hip-shoulder)*(y-top)/(waist-top)
        else:
            ridge = hip + (tip-hip)*(y-waist)/max(1,hem-waist)
        distance = x-ridge
        neighbours = [cloth[u, v] for u in range(x-1, x+2) for v in range(y-2, y+3) if (u, v) in cloth]
        tone = .75*mean(neighbours) + .25*shade
        if -.9 <= distance <= .65:
            tone = 7 if y<hem-1 else 6
        elif -2 <= distance < -.9:
            tone = max(6,tone)
        elif .65 < distance <= 1.85:
            tone = min(2,tone)
        elif tone > 5.3:
            tone = 7
        elif 3.4 <= tone <= 5.3:
            tone = 5
        if shade <= 2 and ((x+1,y) not in cloth or (x, y+1) not in cloth):
            tone = min(tone,shade+1)
        edits[x, y] = LINEN[max(0,min(9,round(tone)))]
    return edits


def skirt(cloth, legs, waist, slender):
    """Pull a narrow crease away from the waist as the fitted hem swings."""
    panel = {p: v for p, v in cloth.items() if p in legs and v in VALUE}
    if not panel:
        return {}
    top = min(y for x, y in panel)
    hem = max(y for x, y in panel)
    top = max(top, waist if waist is not None else top)
    if hem <= top:
        return {}
    def middle(y, fraction):
        xs = sorted(x for x,v in panel if abs(v-y)<=2)
        return xs[round((len(xs)-1)*fraction)] if xs else None
    hip, toe = middle(top,.63), middle(hem,.40)
    if hip is None or toe is None:
        return {}
    edits = {}
    for (x, y), ink in panel.items():
        if y < top:
            continue
        axis = hip+(toe-hip)*(y-top)/(hem-top)
        if x==round(axis):
            edits[x, y] = LINEN[min(VALUE[ink],2 if slender else 3)]
        elif slender and x==round(axis)-1 and VALUE[ink]>=5:
            edits[x, y] = 199
    return edits
