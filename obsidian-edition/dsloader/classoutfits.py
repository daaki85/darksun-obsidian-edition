"""Human male class artwork and equipment masks, registered to the original 2095/2096 poses."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import NamedTuple
from zipfile import ZipFile

from . import art, game, kitpages

# The masks and grip coordinates are specific to these two source pictures.
SOURCE = {
    2095: "b0f5fd9b7f07fe8deb1b106bc786ca067930a467a8b338ed5d3cd96f25d9492f",
    2096: "e787121b4d79e554dd071da1fe8db9a93c25cfeb344fc69b22022fb456163723",
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


def supports(chunks):
    return all(sha256(chunks.get(("BMP ", picture), b"")).hexdigest() == digest
               for picture, digest in SOURCE.items())


def for_sheet(sheet):
    if len(sheet) <= game.SHEET_CLASSES or sheet[game.SHEET_RACE] != game.HUMAN:
        return None
    group = kitpages.CREATION_CLASS.get(sheet[game.SHEET_CLASSES])
    return CLASSES[group] if group else None


class Frame(NamedTuple):
    image: list
    regions: dict
    cloak: tuple = ()  # (native x, y, fold shade from 0 to 5)

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


@lru_cache(maxsize=16)
def frames(role, combat):
    tag = "combat" if combat else "walk"
    with ZipFile(Path(__file__).with_name("human_outfit_layers.zip")) as archive:
        pictures = archive.read(f"{role}/{tag}")
        cloaks = archive.read(f"{role}/{tag}-cloak")
        masks = archive.read(f"{role}/{tag}-regions")
    poses = []
    for f in range(14 if combat else 15):
        image = art.decode_frame(pictures, f)[2]
        mask = art.decode_frame(masks, f)[2]
        regions = {bit: [] for bit in (CHEST, ARMS, LEGS, LEFT_FOOT, RIGHT_FOOT, FOREARM, BOW)}
        # Frame 13 has extra transparent columns for the swept priest hem.
        left = 8 if not combat and f == 13 else 6
        top = 6
        for y, row in enumerate(mask):
            for x, bits in enumerate(row):
                if bits:
                    for bit in regions:
                        if bits & bit:
                            regions[bit].append((x - left, y - top))
        folds = tuple((x - left, y - top, shade - 1)
                      for y, row in enumerate(art.decode_frame(cloaks, f)[2])
                      for x, shade in enumerate(row) if shade is not None)
        poses.append(Frame(image, regions, folds))
    return tuple(poses)
