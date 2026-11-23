"""Class outfit layers registered to the human and dwarf map poses.

Each archive has walk and combat chunks per class. The woman's outfits layer
over a shared redrawn base. In each layer a transparent edit keeps the pixel
underneath, 255 clears it, and any other value paints it.
The matching region chunk assigns equipment ownership. The cloak chunk stores
its fold values from 1 (dark) to 6 (light) for recolouring on equip. The shared
head mask keeps back gear behind the face and hair.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import NamedTuple
from zipfile import ZipFile

from . import art, game, kitpages

# A figure is eligible only when both pose sheets match the hand-registered artwork.
MODELS = {300: 2095, 301: 2099, 302: 2055, 303: 2053}
SOURCE = {
    2053: "91c133abf78323f5b0b83a9f706b8750d99e6e9efe97a54c984c40e55539efb3",
    2054: "aaadd31defbf1b021812b47bb38cd37d8b0f7c97871a760e0a5e842b3d536f6f",
    2055: "80d16c5f0bdc4b75fa5c960771731c32d9777477b7218d57a32af2027dba1bf6",
    2056: "088895b889a46c91bf1117c294e0b1748d26082687f121c565bdf622069db045",
    2095: "b0f5fd9b7f07fe8deb1b106bc786ca067930a467a8b338ed5d3cd96f25d9492f",
    2096: "e787121b4d79e554dd071da1fe8db9a93c25cfeb344fc69b22022fb456163723",
    2099: "92b22183387db3382e56f31747a1e40af7393af6baa8ffa07a82bd9c22cf8481",
    2100: "8f04f1e42fe2e2a9cdc301fc1590ab016a0f62fd057b0e93b63364397537e337",
}
CLASSES = ("", "Priest", "Druid", "Warrior", "Gladiator", "Mage", "Psionicist", "Ranger", "Thief")
CHEST, ARMS, LEGS, LEFT_FOOT, RIGHT_FOOT, FOREARM, BOW = 1, 2, 4, 8, 16, 32, 64


# Crown, brow bounds and row, shoulder row and bounds, and waist.
LANDMARKS = (
    (0, 7, 13, 2, 6, 3, 16, 14), (0, 9, 14, 2, 7, 6, 15, 14),
    (0, 4, 10, 3, 8, 2, 6, 15), (0, 6, 12, 2, 6, 3, 15, 13),
    (0, 6, 12, 2, 6, 4, 15, 13), (0, 6, 12, 2, 6, 3, 14, 13),
    (0, 7, 13, 2, 6, 4, 15, 13), (0, 4, 9, 2, 7, 2, 11, 14),
    (0, 5, 10, 2, 7, 3, 12, 15), (0, 5, 10, 2, 7, 3, 12, 14),
    (0, 5, 10, 2, 7, 3, 13, 15), (0, 6, 12, 3, 8, 4, 8, 15),
    (0, 9, 15, 3, 8, 7, 11, 15), (0, 5, 11, 3, 8, 4, 8, 14),
    (0, 8, 14, 3, 8, 6, 10, 15), (9, 5, 11, 11, 16, 5, 10, 23),
    (0, 9, 15, 3, 8, 8, 16, 12), (4, 11, 20, 6, 8, 14, 19, 12),
    (3, 4, 9, 5, 11, 3, 10, 18), (7, 2, 7, 9, 14, 4, 10, 21),
    (0, 13, 18, 2, 7, 11, 18, 14), (7, 11, 16, 9, 14, 9, 18, 21),
    (1, 10, 16, 4, 8, 7, 14, 15), (0, 11, 16, 2, 6, 7, 14, 12),
    (0, 5, 12, 2, 7, 5, 10, 15), (3, 6, 11, 5, 10, 6, 11, 18),
    (3, 5, 10, 5, 9, 4, 12, 17), (3, 1, 8, 5, 7, 3, 10, 12),
)

# Centres of the off-hand forearm, in the source picture's coordinate system.
# The far arm is hidden in a few views. Its shield is drawn behind the figure.
WALK_SHIELDS = (
    (18, 11), (1, 11), (9, 12),
    (17, 11), (16, 10), (17, 9), (18, 12),
    (1, 10), (2, 8), (1, 10), (1, 12),
    (9, 12), (5, 12), (8, 10), (11, 11),
)
FIGHT_SHIELDS = (
    (5, 22), (20, 16), (10, 1), (3, 13), (2, 18), (11, 8),
    (23, 18), (7, 10), (4, 3), None, None, None, (16, 1), None,
)
# The right hand can disappear from the automatic wristband search when it
# crosses the head or torso. These are the actual grips in the melee/hit art.
FIGHT_GRIPS = (
    (15, 8), (2, 4), (10, 16), (11, 10), (10, 9), (14, 12),
    (7, 9), (22, 11), (17, 14), None, None, None, (3, 14), None,
)


# Centres of the woman's supporting wrist, including the reconstructed arm
# that swings underneath the cloak in the rear walk.
WOMAN_WALK_SHIELDS = (
    (15, 11), (4, 13), (8, 12), (13, 10), (16, 8), (15, 10), (13, 13),
    (3, 9), (4, 9), (4, 13), (4, 12), (11, 14), (6, 13), (15, 12), (13, 14),
)
WOMAN_FIGHT_SHIELDS = (
    (8, 22), (19, 18), (10, 1), (3, 13), (2, 21), (10, 8),
    (22, 18), (13, 10), (7, 5), None, None, None, (11, 3), None,
)
WOMAN_FIGHT_GRIPS = (
    (16, 9), (2, 7), (11, 16), (11, 12), (10, 11), (14, 11),
    (7, 10), (24, 11), (20, 11), None, None, None, (3, 16), None,
)


# The two dwarves share the limb registration except for the first forward strike.
DWARF_WALK_SHIELDS = (
    (18, 9), (2, 10), (8, 11), (17, 9), (16, 7), (15, 8), (17, 10),
    (2, 9), (2, 8), (1, 9), (1, 11), (6, 11), (4, 10), (4, 10), (9, 10),
)
DWARF_FIGHT_SHIELDS = (
    (3, 13), (15, 11), (4, 2), (3, 8), (2, 11), (3, 7), (16, 10), (8, 9), (4, 5),
    None, None, None, (15, 2), None,
)
DWARF_FIGHT_GRIPS = (
    (12, 1), (2, 3), (3, 14), (11, 9), (10, 3), (7, 11), (2, 5), (21, 8), (16, 11),
    None, None, None, (2, 13), None,
)


def supports(chunks, model):
    return all(sha256(chunks.get(("BMP ", picture), b"")).hexdigest() == SOURCE[picture]
               for picture in (model, model + 1))


DWARF_ROLES = {
    (1,): "Cleric", (3,): "Fighter", (4,): "Gladiator", (6,): "Psionicist", (8,): "Thief",
    (1, 3): "Cleric/Fighter", (1, 6): "Cleric/Psionicist", (3, 6): "Fighter/Psionicist",
    (3, 8): "Fighter/Thief", (6, 8): "Psionicist/Thief",
    (1, 3, 6): "Cleric/Fighter/Psionicist", (3, 6, 8): "Fighter/Psionicist/Thief",
}
DWARVES = (2053, 2055)


def for_sheet(sheet, model=None):
    if len(sheet) <= game.SHEET_CLASSES:
        return None
    race = sheet[game.SHEET_RACE]
    if race == game.DWARF and (model is None or model in DWARVES):
        slots = sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]
        if len(slots) < 3:
            return None
        return DWARF_ROLES.get(tuple(sorted(kitpages.CREATION_CLASS.get(c, 0) for c in slots if c)))
    if race == game.HUMAN and (model is None or model in (2095, 2099)):
        group = kitpages.CREATION_CLASS.get(sheet[game.SHEET_CLASSES])
        return CLASSES[group] if group else None
    return None


class Frame(NamedTuple):
    image: list
    regions: dict
    cloak: tuple = ()  # (native x, y, fold shade from 0 to 5)
    head: tuple = ()  # foreground face and locks, in native coordinates

    def canvas(self, source, pad):
        """Apply authored pixels to the matching pose read from the player's install."""
        width, height = len(source[0]), len(source)
        margin = (len(self.image[0]) - width) // 2
        above = len(self.image) - height
        result = [[None] * (width + 2 * pad) for _ in range(height + pad)]
        for y, row in enumerate(source, pad):
            result[y][pad:pad + width] = row
        for y, row in enumerate(self.image, pad - above):
            for x, paint in enumerate(row, pad - margin):
                if paint is not None:
                    result[y][x] = None if paint == 255 else paint
        return result


@lru_cache(maxsize=32)
def frames(role, combat, model=2095):
    tag = "combat" if combat else "walk"
    filename = "woman_outfit_layers.zip" if model == 2099 else "human_outfit_layers.zip"
    dwarf = model in DWARVES
    if dwarf:
        filename = "dwarf_outfit_layers.zip"
    prefix = f"{model}/{role}" if dwarf else role
    with ZipFile(Path(__file__).with_name(filename)) as archive:
        base = archive.read(f"Base/{tag}") if model == 2099 else None
        if dwarf:
            heads = archive.read(f"{prefix}/{tag}-head")
        else:
            heads = archive.read(f"Base/{tag}-head") if model == 2099 else None
        pictures = archive.read(f"{prefix}/{tag}")
        cloaks = archive.read(f"{prefix}/{tag}-cloak")
        masks = archive.read(f"{prefix}/{tag}-regions")
    poses = []
    for f in range(14 if combat else 15):
        image = art.decode_frame(pictures, f)[2]
        if base is not None:
            # Both edits use the same registration. Preserve clear (255) edits
            # here so the final canvas can erase the stock cloak underneath.
            body = art.decode_frame(base, f)[2]
            image = [[under if over is None else over for under, over in zip(body_row, outfit_row)]
                     for body_row, outfit_row in zip(body, image)]
        mask = art.decode_frame(masks, f)[2]
        regions = {bit: [] for bit in (CHEST, ARMS, LEGS, LEFT_FOOT, RIGHT_FOOT, FOREARM, BOW)}
        # Frame 13 has extra transparent columns for the swept priest hem.
        left = 8 if model == 2095 and not combat and f == 13 else 6
        top = 6
        if dwarf:
            left = top = 4
        for y, row in enumerate(mask):
            for x, bits in enumerate(row):
                if bits:
                    for bit in regions:
                        if bits & bit:
                            regions[bit].append((x - left, y - top))
        folds = tuple((x - left, y - top, shade - 1)
                      for y, row in enumerate(art.decode_frame(cloaks, f)[2])
                      for x, shade in enumerate(row) if shade is not None)
        head = ()
        if heads is not None:
            head = tuple((x - left, y - top)
                         for y, row in enumerate(art.decode_frame(heads, f)[2])
                         for x, pixel in enumerate(row) if pixel is not None)
        poses.append(Frame(image, regions, folds, head))
    return tuple(poses)
