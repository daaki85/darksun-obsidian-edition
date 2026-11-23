"""Check registered human and dwarf outfits against the player's installed figures.

    python prototypes/check_class_frames.py GAME_DIR
"""

import argparse

import outfits
from dsloader import art, classoutfits as co, game, spritegear as sg, sprites


def connected(cells):
    """Check an eight-connected silhouette, including diagonals at a wrist."""
    remaining = set(cells)
    if not remaining:
        return False
    visit = [remaining.pop()]
    while visit:
        x, y = visit.pop()
        for nx in range(x - 1, x + 2):
            for ny in range(y - 1, y + 2):
                if (nx, ny) in remaining:
                    remaining.remove((nx, ny))
                    visit.append((nx, ny))
    return not remaining


def visible(rows, side, top):
    return {(x - side, y - top): c for y, row in enumerate(rows)
            for x, c in enumerate(row) if c is not None}


def check(source):
    boot = {"boots": (game.SPEED_BOOTS_TYPE, 5, sg.MAGIC, 0)}
    mixed = dict(boot, cloak=(65, 5), left=(4, 0), right=(45, 4), helm=(game.BONE_HELM_TYPE, 1))
    kits = (
        ("empty", {}, ()), ("boots", boot, ()), ("cloak", {"cloak": (65, 5)}, ()),
        ("shield", {"left": (4, 0)}, ()), ("sword", {"right": (45, 4)}, ()),
        ("bow", {"missile": (1, 0), "ammo": (62, 0)}, ()), ("plate", {}, (88,)),
        ("magic plate", {}, (88 | sg.MAGIC_ARMOUR,)), ("mixed", mixed, (88, 25, 26)),
    )
    pictures = sprites.Pictures(source.chunks)
    for obj, model in co.MODELS.items():
        if not pictures.supports_outfits(obj, model):
            raise ValueError(f"Figure {obj} does not match the registered picture pair for {model}")
        roles = co.DWARF_ROLES.values() if model in co.DWARVES else co.CLASSES[1:]
        count = 0
        for combat in (False, True):
            side, top = sprites.room(combat)
            native = pictures.own(model + combat)
            templates = [sg.cloak_template(rows, sg.CLOAK_MODEL, f, combat)
                         for f, rows in enumerate(pictures.own(sg.CLOAK_MODEL + combat))]
            for role in roles:
                poses = co.frames(role, combat, model)
                baseline = []
                for name, gear, armour in kits:
                    chunk = pictures.build(obj, combat, gear, armour, role=role)
                    assert len(chunk) <= pictures.room(obj, combat), (obj, role, name, "capacity")
                    if name == "empty":
                        original = chunk
                    for f, pose in enumerate(poses):
                        case = (obj, role, combat, f, name)
                        actual = visible(art.decode_frame(chunk, f)[2], side, top)
                        reference = sg.armed(native[f], model, f, combat, gear, 32, armour,
                                             templates[f], costume=pose)
                        # The sparkle pattern depends on canvas coordinates. Compare occupancy here.
                        assert actual.keys() == visible(reference, 32, 32).keys(), (case, "frame clipped or shifted")
                        assert connected(actual), (case, "detached pixels")
                        assert all(actual[x, y] == native[f][y][x] for x, y in pose.regions[co.BOW]), (case, "bow")
                        if name == "empty":
                            baseline.append(actual)
                        elif name == "boots":
                            for bit in (co.LEFT_FOOT, co.RIGHT_FOOT):
                                foot = pose.regions[bit]
                                assert not foot or any(actual[p] != baseline[f][p] for p in foot), (case, bit)
                        elif name == "cloak":
                            ramp = sg.CLOAK_COLOURS[65]
                            assert all(actual[x, y] == ramp[tone] for x, y, tone in pose.cloak), (case, "cloak")
                        elif name in ("plate", "magic plate"):
                            changed = {p for p in actual.keys() | baseline[f].keys()
                                       if actual.get(p) != baseline[f].get(p)}
                            assert changed <= set(pose.regions[co.CHEST]), (case, "armor spill")
                        count += 1
                assert pictures.build(obj, combat, {}, (), role=role) == original, (obj, role, "removal")
        print(f"Figure {obj} (model {model}): {count} renders checked")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir")
    check(outfits.Game(parser.parse_args().game_dir))
