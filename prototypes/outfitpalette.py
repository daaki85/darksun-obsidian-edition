"""Fit steady material colours to the existing registered art.

Run after exporting the garment and equipment archives:
    python prototypes/outfitpalette.py GAME_DIR

The sparse material layers use the same registration as the outfit. They derive
from the original paint so another export starts from the same brush strokes.
"""
import argparse
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from dsloader import art, classoutfits as co, spritegear, sprites
import linenfolds
from outfits import Game
from halfgiantstudy import reference_folds, study_rows


# Keep separate leather ridges where 94/95, 96/97 and 99/100 used to collapse.
# The dark ramp is for the jerkin itself. Cuffs and hilts have their own masks.
JERKIN = (17, 129, 17, 204, 209, 207, 209, 205, 210, 196, 194, 201, 168, 169, 170)
RIDGES = {92: (91, 205), 95: (94, 196), 97: (96, 201), 100: (99, 169), 101: (100, 171)}
JERKIN_MODELS = {*co.ELVES, *co.HALF_ELF_SOURCES, *co.DWARVES, 2068, 2070, 2074, 2093}
TEAL = {69: (69, 69), 70: (69, 69), 71: (70, 69), 40: (71, 70),
        72: (71, 70), 73: (72, 71)}
LINEN = {205: (207, 204), 194: (205, 207), 206: (194, 205), 120: (206, 194),
         121: (206, 194), 61: (206, 194), 123: (61, 206), 199: (61, 206),
         125: (199, 61), 62: (199, 61), 63: (62, 199), 155: (199, 61)}
NEIGHBOURS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def surface(frame):
    cloth = set(frame.regions[co.CHEST]) | set(frame.regions[co.LEGS]) | set(frame.regions[co.ARMS])
    for bit in (co.FOREARM, co.BOW, co.LEFT_FOOT, co.RIGHT_FOOT):
        cloth.difference_update(frame.regions[bit])
    return cloth.difference(frame.head)


def shadow(pigments, ramp, pose):
    rank = {ink: i for i, ink in enumerate(ramp)}
    # The outside edge bends with the cut in each row. Leave the lit half of
    # the garment and the narrow glints on the folds in the shadow intact.
    rows = defaultdict(list)
    for (x, y), ink in pigments.items():
        if ink in ramp or ink in (208, 204, 207, 17):
            rows[y].append(x)
    result = {}
    for y, xs in rows.items():
        near = [rows[k] for k in (y-1, y, y+1) if k in rows]
        left = sum(min(row) for row in near) / len(near)
        right = sum(max(row) for row in near) / len(near)
        if right-left < 3:
            continue
        for x in xs:
            ink = pigments[x, y]
            if ink not in ramp:
                continue
            turn = (x-left)/(right-left)
            if pose == 28:
                turn = 1-turn
            if turn >= .53:
                result[x, y] = ramp[ink][int(turn >= .75)]
    # Keep the original high point when shading would turn a textured 2×2
    # fold into a single ink. Each restored stroke belongs to the native weave.
    for x, y in sorted(pigments, key=lambda pt: (pt[1], pt[0])):
        square = ((x, y), (x+1, y), (x, y+1), (x+1, y+1))
        if any(pt not in pigments for pt in square):
            continue
        inks = {result.get(pt, pigments[pt]) for pt in square}
        if len(inks) == 1:
            changed = [pt for pt in square if pt in result and result[pt] != pigments[pt]]
            if changed and len({pigments[pt] for pt in square}) > 1:
                peak = max(changed, key=lambda pt: rank[pigments[pt]])
                del result[peak]
    return result


def leather(pigments, dark_jerkin):
    changes = {}
    for (x, y), ink in pigments.items():
        if dark_jerkin and 88 <= ink <= 102:
            changes[x, y] = JERKIN[ink-88]
        elif ink in RIDGES:
            lower, highlight = RIDGES[ink]
            if any(pigments.get((x+a, y+b)) == lower for a, b in NEIGHBOURS):
                changes[x, y] = highlight
    return changes


def quieter_teal(cloth, model):
    lower = {71:70, 40:71, 72:40, 73:72}
    if model in (2095, 2099):
        lower[72] = 71  # Keep the two central ribs on the fitted human wrap teal.
    edits = {p:lower[ink] for p,ink in cloth.items() if ink in lower}
    # Keep one glint on a joined pair or longer run of the brightest weave.
    lights = {p for p,ink in cloth.items() if ink == 73}
    while lights:
        run = {lights.pop()}
        more = list(run)
        while more:
            x,y = more.pop()
            neighbours = {(x+i,y+j) for i in (-1,0,1) for j in (-1,0,1)} & lights
            lights.difference_update(neighbours)
            run.update(neighbours)
            more.extend(neighbours)
        if len(run)>1:
            del edits[min(run, key=lambda p:(p[1],p[0]))]
    return edits


def waist_edge(pigments, waist):
    if waist is None:
        return {}
    hide = {p for p,v in pigments.items() if 88 <= v <= 102}
    xs = sorted(x for x,y in hide if y==waist)
    if len(xs)<3:
        return {}
    # Stop the narrow warm welt where the near arm interrupts the leather.
    pivot = xs[(len(xs)-1)//3]
    return {(x,y):201 if x==pivot else 205 for x,y in hide
            if pivot-1<=x<=pivot+1 and y==waist+int(x>pivot)}


def giant_hide(pigments, study, single, role, left, top):
    # Compare with the undressed study so the leather and skin can share an ink.
    # On the pair the sash and teal shoulder cap cover part of the original jerkin.
    edits = {}
    original, body = study['Fighter'], study['Body base']
    for (x,y), ink in pigments.items():
        old = original[y+top][x+left]
        if old == body[y+top][x+left] or (role != 'Fighter' and old != ink):
            continue
        ground = single[y+top][x+left]
        if ground in (61, 62, 63, 155, 168, 169, 199):
            continue
        if role != 'Fighter' and ground in spritegear.STEADY and (88 <= old <= 102 or old in (204, 207)):
            edits[x,y] = ground
        if old in range(88,103):
            edits[x,y] = JERKIN[old-88]
        elif old in (204,205,207) and any(
                0<=y+top+b<len(original) and 0<=x+left+a<len(original[0])
                and original[y+top+b][x+left+a] in range(88,103) for a,b in NEIGHBOURS):
            edits[x,y] = 209 if old==205 else 17
    return edits


def material_frames(model, roles, tag, archive, game):
    combat = tag == 'combat'
    source_model = co.HALF_ELF_SOURCES.get(model, model)
    parents = {}
    finished = {}
    giant_linen = reference_folds(game)['linen'] if model == 2072 else None
    wrap_shadows = {}
    body_chunk = archive.read(f'Study/{tag}-body') if model == 2095 else None
    for role, prefix in sorted(roles.items(), key=lambda pair: (pair[0].count('/'), pair[0])):
        raw = archive.read(f'{prefix}/{tag}')
        frames = co.frames(role, combat, model)
        output = []
        count = 0
        for f, frame in enumerate(frames):
            pose = 15*combat + f
            paint = art.decode_frame(raw, f)[2]
            native = game.fr(source_model+combat, f)
            left = (len(paint[0])-len(native[0]))//2
            top = len(paint)-len(native)
            # Half-elf layers are registered to their generated body. Its
            # dimensions can differ from the parent elf or human frame.
            if model in co.HALF_ELF_SOURCES:
                left = top = 10
            cells = surface(frame)
            pigments = {(x, y): paint[y+top][x+left] for x, y in cells
                        if 0 <= y+top < len(paint) and 0 <= x+left < len(paint[0])
                        and paint[y+top][x+left] not in (None, 255)}
            members = role.split('/')
            edits = {}
            # Linen uses 92, 95 and 97 in its own texture. Require a leather
            # ground before picking out a tan ridge, including on mixed outfits.
            hide = {pt: v for pt, v in pigments.items() if 88 <= v <= 102}
            material = {pt: v for pt, v in hide.items() if
                        any(hide.get((pt[0]+a, pt[1]+b)) in (88, 89, 90, 91, 93, 94, 96)
                            for a, b in NEIGHBOURS)}
            if (model, role) not in ((2072, 'Fighter'), (2095, 'Priest'), (2099, 'Priest'), (2099, 'Druid')) and role != 'Gladiator':
                edits.update(leather(material, False))
            if role == 'Fighter' and model in JERKIN_MODELS:
                edits.update(leather(hide, True))
                # The walnut ground in the early fitted panels also uses two
                # fixed browns. Cool its contact edge, leaving the bone fittings.
                for (x, y), ink in pigments.items():
                    if ink in (205, 207) and any((x+a, y+b) in hide for a, b in NEIGHBOURS):
                        edits[x, y] = 209 if ink == 205 else 17
            parts = game.fig(source_model).parts(combat,f)
            if role == 'Fighter' and model in (*co.ELVES, *co.HALF_ELF_SOURCES):
                edits.update(waist_edge(pigments, parts.waist))
            if model == 2072 and role in ('Fighter', 'Fighter/Psionicist'):
                study = study_rows(game, model, pose, giant_linen)
                single = art.decode_frame(archive.read(f'2072/Fighter/{tag}'), f)[2]
                edits.update(giant_hide(pigments, study, single, role, left, top))
            if role in ('Cleric', 'Psionicist'):
                edits.update(shadow(pigments, LINEN if role == 'Cleric' else TEAL, pose))
                cloth = {p:edits.get(p, spritegear.steady_colour(v)) for p,v in pigments.items()}
                if role == 'Psionicist':
                    wrap_shadows[f] = dict(edits)
                    edits.update(quieter_teal(cloth,model))
                else:
                    far = {p:LINEN[v][1] for p,v in cloth.items()
                           if p in edits and pigments[p] in LINEN and edits[p]==LINEN[pigments[p]][1] and v in LINEN}
                    cloth.update(far)
                    edits.update(far)
                    edits.update(linenfolds.skirt(cloth,set(frame.regions[co.LEGS]),parts.waist,
                                                  model in (*co.ELVES,*co.HALF_ELF_SOURCES)))
            if model == 2095 and role == 'Priest':
                bare = art.decode_frame(body_chunk, f)[2]
                offset = (len(bare[0])-len(paint[0]))//2
                linen = {p:spritegear.steady_colour(ink) for p,ink in pigments.items()
                         if 0<=p[0]+left+offset<len(bare[0]) and ink!=bare[p[1]+top][p[0]+left+offset]}
                edits.update(linenfolds.priest(linen,pose,parts.waist))
            # Transfer a parent stroke only where the composite still has the
            # same material and neighbouring brushwork. A sash on top owns its pixels.
            if len(members) > 1:
                for member in members:
                    if member not in ('Fighter', 'Cleric', 'Psionicist'):
                        continue
                    source, parent = parents[member, f]
                    if member == 'Psionicist':
                        teal = {p for p,v in source.items() if v in TEAL}
                        # A narrow sash keeps the earlier accent lighting; only
                        # broad inherited tunics need the lower lit plane.
                        if sum(pigments.get(p)==source[p] for p in teal) < len(teal)*.6:
                            parent = wrap_shadows[f]
                    for (x, y), tone in parent.items():
                        if (x, y) in pigments and pigments[x, y] == source[x, y] and any(
                            (x+a, y+b) in source and pigments.get((x+a, y+b)) == source[x+a, y+b]
                            for a, b in NEIGHBOURS):
                            edits[x, y] = tone
            if len(members) == 1 and role in ('Fighter', 'Cleric', 'Psionicist'):
                parents[role, f] = pigments, edits
            layer = [[None]*len(paint[0]) for _ in paint]
            for (x, y), tone in edits.items():
                if tone != spritegear.steady_colour(pigments[x, y]):
                    assert tone in spritegear.STEADY
                    layer[y+top][x+left] = tone
                    count += 1
            output.append(layer)
        if count:
            finished[f'{prefix}/{tag}-material'] = sprites.encode_frames(output)
    return finished


def export(game_dir, root):
    game = Game(game_dir)
    spritegear.set_palette(list(game.palette))
    for file in sorted(root.glob('*_outfit_layers.zip')):
        with ZipFile(file) as src, TemporaryDirectory(dir=root) as temp:
            roles = defaultdict(dict)
            for name in src.namelist():
                if name.endswith('/walk') and not name.startswith(('Study/', 'Base/')):
                    prefix = name[:-5]
                    parts = prefix.split('/')
                    model = int(parts.pop(0)) if parts[0].isdigit() else 2099 if file.name.startswith('woman_') else 2095
                    roles[model]['/'.join(parts)] = prefix
            output = Path(temp)/file.name
            with ZipFile(output, 'w') as dst:
                for info in src.infolist():
                    if not info.filename.endswith('-material'):
                        dst.writestr(info, src.read(info))
                for model, names in roles.items():
                    for tag in ('walk', 'combat'):
                        for name, chunk in material_frames(model, names, tag, src, game).items():
                            dst.writestr(ZipInfo(name), chunk, compress_type=ZIP_DEFLATED)
            output.replace(file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_dir', type=Path)
    export(parser.parse_args().game_dir, Path(co.__file__).parent)
