"""Class outfit layers registered to the human, dwarf, elf and half-elf map poses.

Each archive has walk and combat chunks per class. The woman's outfits layer
over a shared redrawn base. In each layer a transparent edit keeps the pixel
underneath, 255 clears it, and any other value paints it.
The matching region chunk assigns equipment ownership. The cloak chunk stores
its fold values from 1 (dark) to 6 (light) for recolouring on equip. The shared
head mask keeps back gear behind the face and hair.
"""
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from typing import NamedTuple, Optional
from zipfile import ZipFile

from . import art, dwarfarmordye, elfarmordye, elfclericplate, game, halfelf, halfelfgarments, humanarmordye, humanpriestplate, kitpages

# A figure is eligible only when both pose sheets match the hand-registered artwork.
MODELS = {300: 2095, 301: 2099, 302: 2055, 303: 2053, 304: 2061, 305: 2059}
# The original six have separate review tools and archives. These five use
# masks exported directly in native coordinates from their approved drawings.
FITTED_MODELS = {308: 2072, 309: 2074, 310: 2068, 311: 2070, 312: 2093}
MAP_OUTFITS = {**MODELS, **FITTED_MODELS}
FITTED_ARCHIVES = {2072: ("halfgiant", 5), 2074: ("halfgiant", 5),
                   2068: ("halfling", 4), 2070: ("halfling", 4), 2093: ("mul", 8)}
SOURCE = {
    2068: "6df83a97e55af63bada4e6cdb963c9e02d66eb05e919fd9faf6afb8a9a3af3a4",
    2069: "9fc3f6a952b0a199c0388c23c0bb92e6aba92e5dc29b64e0d4340749f8002636",
    2070: "096a612bf8b304d959c186ec226ee0318f36d8d154d59cb09a7e47b4e5b028e2",
    2071: "dcc69499dad7283917778f7a4a1c3ae3671a10755bcf3bedba6255b18fdaa348",
    2072: "acd78bb139e2b3acbfac3333bc2771fcce15cb78d2e79f1852f7e862782d7127",
    2073: "777b9fae44202dbf035fd360c9137f2834a0fdd93cd51671bbf8a7b33b4cc4ce",
    2074: "9d8066748b7d924802e77233e91772111cb22c6d01c82ded2dc93369688907bb",
    2075: "4b8d88720e4eeb0703195d237045ad652a8ee67b7d6d56ed26a39a98e9d816de",
    2093: "e18b818ec304b53448f04a45c547d9cb3fb3bcd2baa6e8b3c3f42c950ece341f",
    2094: "6910363ddda1175f61c6cb6acf494c53fe4cea2a76e748a3f5f1b9a96c2189f6",
    2053: "91c133abf78323f5b0b83a9f706b8750d99e6e9efe97a54c984c40e55539efb3",
    2054: "aaadd31defbf1b021812b47bb38cd37d8b0f7c97871a760e0a5e842b3d536f6f",
    2055: "80d16c5f0bdc4b75fa5c960771731c32d9777477b7218d57a32af2027dba1bf6",
    2056: "088895b889a46c91bf1117c294e0b1748d26082687f121c565bdf622069db045",
    2059: "a8991e16fbe5394117e4ccfd5ec2297126ea3007151c30a309dd4ef02cf6c103",
    2060: "8728f7590c10ce77873689d0612216c911e438500fa45dd0a2f702df075a4af0",
    2061: "f395ce3621fc59a7dd3f559a0419554fc05f4b30500ac860fda10dc4d9102013",
    2062: "6a2949b3fc70fd3f0325b806b8f08e6908175bb28de6e819647991ef1e0af713",
    2095: "b0f5fd9b7f07fe8deb1b106bc786ca067930a467a8b338ed5d3cd96f25d9492f",
    2096: "e787121b4d79e554dd071da1fe8db9a93c25cfeb344fc69b22022fb456163723",
    2099: "92b22183387db3382e56f31747a1e40af7393af6baa8ffa07a82bd9c22cf8481",
    2100: "8f04f1e42fe2e2a9cdc301fc1590ab016a0f62fd057b0e93b63364397537e337",
}
HALF_ELF_SOURCES = {halfelf.MAN: 2061, halfelf.WOMAN: 2099}
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


# Swinging grip and supporting wrist, in each retail combat drawing.
# The far forearm sits behind the torso in the side thrust.
ELF_MELEE_HANDS = {
    2059: {0: ((14, 8), (6, 21)), 1: ((1, 7), (19, 18)), 2: ((11, 16), (10, 1)),
           3: ((16, 8), (9, 8)), 4: ((11, 11), (2, 21)), 5: ((13, 13), (10, 8)),
           6: ((4, 10), (19, 19)), 7: ((21, 10), (8, 8)), 8: ((16, 12), (2, 5)),
           12: ((4, 18), (10, 2))},
    2061: {0: ((14, 9), (6, 22)), 1: ((1, 4), (19, 15)), 2: ((10, 16), (8, 1)),
           3: ((10, 12), (3, 10)), 4: ((11, 10), (2, 21)), 5: ((13, 13), (10, 8)),
           6: ((8, 10), (23, 18)), 7: ((21, 11), (6, 9)), 8: ((16, 12), (2, 5)),
           12: ((0, 14), (15, 11))},
}


# Shoulder row and visible left/right edges, traced on the half-elf torso.
# The quiver stays on this line even when a raised wrist widens the stock pose.
HALF_ELF_SHOULDERS = {
    2061: ((7, 3, 13), (7, 6, 15), (8, 2, 8), (7, 2, 12), (7, 3, 12), (7, 3, 12), (7, 3, 12),
           (7, 2, 11), (7, 1, 9), (7, 3, 12), (7, 4, 13), (8, 1, 6), (8, 5, 10),
           (8, 3, 8), (8, 4, 11), (15, 5, 12), (8, 9, 17), (8, 12, 20), (10, 3, 11),
           (15, 4, 11), (8, 13, 20), (14, 11, 18), (10, 7, 13), (7, 7, 12),
           (7, 5, 11), (10, 3, 9), (10, 5, 12), (7, 3, 12)),
    2099: ((7, 2, 13), (7, 5, 14), (8, 2, 8), (7, 2, 13), (7, 5, 14), (7, 3, 14), (7, 3, 12),
           (7, 4, 12), (7, 5, 13), (7, 6, 14), (7, 5, 13), (8, 5, 11), (8, 6, 12),
           (8, 9, 14), (8, 6, 12), (15, 4, 12), (9, 10, 16), (8, 12, 19), (10, 3, 9),
           (15, 5, 12), (8, 12, 20), (14, 11, 18), (10, 10, 17), (7, 11, 17),
           (7, 3, 10), (10, 3, 9), (9, 7, 12), (7, 4, 11)),
}

# The retail woman's cloak hid this hand. The half-elf study restores it.
HALF_ELF_WOMAN_REAR_HAND = {1: (14, 15), 7: (13, 14), 8: (15, 14),
                            9: (15, 12), 10: (14, 11)}


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
ELVES = (2059, 2061)
_ELF_CLASSES = {1: "Cleric", 3: "Fighter", 4: "Gladiator", 5: "Preserver",
                6: "Psionicist", 7: "Ranger", 8: "Thief"}
ELF_ROLES = {combo: "/".join(_ELF_CLASSES[c] for c in combo)
             for size in (1, 2, 3) for combo in combinations(_ELF_CLASSES, size)
             if size == 1 or (4 not in combo and not {3, 7}.issubset(combo))}


_CLASS_IDS = {"Cleric": 1, "Druid": 2, "Fighter": 3, "Gladiator": 4,
              "Preserver": 5, "Psionicist": 6, "Ranger": 7, "Thief": 8}


def _roles(names):
    return {tuple(_CLASS_IDS[part] for part in name.split("/")): name for name in names.split()}


# Half-elves share the elf combinations and have eleven additional Druid builds.
HALF_ELF_ROLES = {**ELF_ROLES, **_roles(
    "Druid Druid/Fighter Druid/Preserver Druid/Psionicist Druid/Thief "
    "Druid/Fighter/Preserver Druid/Fighter/Psionicist Druid/Fighter/Thief "
    "Druid/Preserver/Psionicist Druid/Preserver/Thief Druid/Psionicist/Thief")}
HALF_GIANT_ROLES = _roles(
    "Cleric Fighter Gladiator Psionicist Ranger Cleric/Fighter Cleric/Psionicist Cleric/Ranger "
    "Fighter/Psionicist Psionicist/Ranger")
HALFLING_ROLES = _roles(
    "Cleric Druid Fighter Gladiator Psionicist Ranger Thief Cleric/Thief Druid/Thief Ranger/Thief "
    "Cleric/Ranger Cleric/Fighter Cleric/Psionicist Druid/Fighter Druid/Psionicist Fighter/Psionicist "
    "Fighter/Thief Psionicist/Ranger Psionicist/Thief Fighter/Psionicist/Thief Psionicist/Ranger/Thief")
MUL_ROLES = _roles(
    "Cleric Druid Fighter Gladiator Psionicist Thief Cleric/Thief Cleric/Fighter Cleric/Psionicist "
    "Druid/Thief Druid/Fighter Druid/Psionicist Fighter/Psionicist Fighter/Thief Psionicist/Thief "
    "Cleric/Fighter/Thief Druid/Fighter/Thief Fighter/Psionicist/Thief")
FITTED_ROLES = {kitpages.HALF_GIANT: HALF_GIANT_ROLES, kitpages.HALFLING: HALFLING_ROLES,
                kitpages.MUL: MUL_ROLES}
FITTED_RACES = {2072: kitpages.HALF_GIANT, 2074: kitpages.HALF_GIANT, 2068: kitpages.HALFLING,
                2070: kitpages.HALFLING, 2093: kitpages.MUL}



def for_sheet(sheet, model=None):
    if len(sheet) <= game.SHEET_CLASSES:
        return None
    race = sheet[game.SHEET_RACE]
    roles = None
    if model in FITTED_RACES or (model is None and race in FITTED_ROLES):
        if model is not None and race != FITTED_RACES[model]:
            return None
        roles = FITTED_ROLES[race]
    elif model in HALF_ELF_SOURCES or (model is None and race == kitpages.HALF_ELF):
        if race != kitpages.HALF_ELF:
            return None
        roles = HALF_ELF_ROLES
    elif race == game.ELF and (model is None or model in ELVES):
        roles = ELF_ROLES
    elif race == game.DWARF and (model is None or model in DWARVES):
        roles = DWARF_ROLES
    if roles is not None:
        slots = sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]
        if len(slots) < 3:
            return None
        return roles.get(tuple(sorted(kitpages.CREATION_CLASS.get(c, 0) for c in slots if c)))
    if race == game.HUMAN and (model is None or model in (2095, 2099)):
        group = kitpages.CREATION_CLASS.get(sheet[game.SHEET_CLASSES])
        return CLASSES[group] if group else None
    return None


class Frame(NamedTuple):
    image: list
    regions: dict
    cloak: tuple = ()  # (native x, y, fold shade from 0 to 5)
    head: tuple = ()  # foreground face and locks, in native coordinates
    armor_trim: frozenset = frozenset()  # native pixels that keep their material and class color
    native_cloak: bool = False  # this outfit includes cloth for a cloak dye to follow
    equipped_cape: tuple = ()  # native (x, y, original cloth color) on a separately donned cape
    belt: Optional[tuple] = None  # authored native waist, empty when the garment hides it
    plate_regions: Optional[dict] = None  # fitted steel visible over long clerical robes

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
    fitted = FITTED_ARCHIVES.get(model)
    half_elf_layers = model in HALF_ELF_SOURCES and role not in ("Fighter", "Preserver")
    by_model = fitted is not None or model in DWARVES + ELVES or model in HALF_ELF_SOURCES
    if fitted:
        filename = f"{fitted[0]}_outfit_layers.zip"
    elif model in HALF_ELF_SOURCES:
        filename = "halfelf_outfit_layers.zip"
    elif model in ELVES:
        filename = "elf_outfit_layers.zip"
    elif model in DWARVES:
        filename = "dwarf_outfit_layers.zip"
    prefix = f"{model}/{role}" if by_model else role
    with ZipFile(Path(__file__).with_name(filename)) as archive:
        base = archive.read(f"Base/{tag}") if model == 2099 else None
        if by_model:
            heads = archive.read(f"{prefix}/{tag}-head")
        else:
            heads = archive.read(f"Base/{tag}-head") if model == 2099 else None
        pictures = archive.read(f"{prefix}/{tag}")
        dye = f"{prefix}/{tag}-dye"
        try:
            cloaks = archive.read(dye)
        except KeyError:
            cloaks = archive.read(f"{prefix}/{tag}-cloak")
        masks = archive.read(f"{prefix}/{tag}-regions")
        belts = archive.read(f"{prefix}/{tag}-belt") if fitted or half_elf_layers else None
        trims = archive.read(f"{prefix}/{tag}-trim") if half_elf_layers else None
        cape_entry = f"{prefix}/{tag}-cape"
        capes = archive.read(cape_entry) if (fitted or model in HALF_ELF_SOURCES) and cape_entry in archive.namelist() else None
    # The archive also stores the drape of a separately equipped cloak for
    # bare-backed kits. Only real cloth can supply its own underlying texture.
    members = set(role.split("/"))
    if half_elf_layers:
        garment = halfelfgarments.garment(role)
        native_cloak = garment in halfelfgarments.CLOAKED
    elif model == 2093:
        native_cloak = role.startswith("Druid") or ("Thief" in members and "Cleric" not in members)
    elif model in (2068, 2070):
        native_cloak = bool(members & {"Druid", "Ranger"}) or ("Thief" in members and "Cleric" not in members)
    elif model in DWARVES:
        native_cloak = "Cleric" in members or role in ("Thief", "Psionicist/Thief")
    else:
        native_cloak = bool(members.intersection(("Thief", "Mage", "Preserver", "Ranger", "Druid")))
    # A wrap, jerkin or short tippet has no full back panel to dye. For a
    # separate outer cloak, take the unhooded drape cut for the same body.
    mantle = ()
    if (model in (2095, 2099) and role == "Psionicist") or (model == 2095 and role == "Druid"):
        mantle = frames("Mage", combat, model)
    elif model in HALF_ELF_SOURCES and role == "Fighter":
        mantle = frames("Preserver", combat, model)
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
        if by_model:
            left = top = 4
        if fitted:
            left, top = fitted[1], 0
        elif model in HALF_ELF_SOURCES:
            left = top = 10
        for y, row in enumerate(mask):
            for x, bits in enumerate(row):
                if bits:
                    for bit in regions:
                        if bits & bit:
                            regions[bit].append((x - left, y - top))
        dye_rows = art.decode_frame(cloaks, f)[2]
        dye_left = left + (len(dye_rows[0]) - len(mask[0])) // 2
        folds = tuple((x - dye_left, y - top, shade - 1)
                      for y, row in enumerate(dye_rows)
                      for x, shade in enumerate(row) if shade is not None)
        head = ()
        if heads is not None:
            head = tuple((x - left, y - top)
                         for y, row in enumerate(art.decode_frame(heads, f)[2])
                         for x, pixel in enumerate(row) if pixel is not None)
        frame = Frame(image, regions, folds, head, native_cloak=native_cloak)
        pose = f + 15 * combat
        cape = ()
        if capes is not None:
            cape = tuple((x-left, y-top, c) for y, row in enumerate(art.decode_frame(capes, f)[2])
                         for x, c in enumerate(row) if c is not None)
        if belts is not None:
            waist = tuple((x-left, y-top) for y, row in enumerate(art.decode_frame(belts, f)[2])
                          for x, c in enumerate(row) if c is not None)
            trim = (frozenset((x-left, y-top) for y, row in enumerate(art.decode_frame(trims, f)[2])
                              for x, c in enumerate(row) if c is not None) if trims else frozenset())
            plate = None
            if half_elf_layers and garment == "Cleric":
                # The long linen hangs in front of the shin guards. Only steel
                # on the torso, sleeves and genuinely exposed calves can show.
                plate = {bit: tuple(p for p in regions[bit] if p not in trim)
                         for bit in (CHEST, ARMS)}
                plate[LEGS] = ()
            poses.append(frame._replace(belt=waist, equipped_cape=cape, armor_trim=trim, plate_regions=plate))
            continue
        if model in HALF_ELF_SOURCES:
            trim = set()
            if role == "Fighter":
                # Keep the bone shoulder plates and ochre fastenings. In the
                # bent strike the cap is hidden; the jerkin still has its belt.
                for bit in (CHEST, ARMS, LEGS):
                    for x, y in regions[bit]:
                        if image[y + top][x + left] in (61, 62, 63, 155, 168, 169, 199):
                            trim.add((x, y))
                legs = set(regions[LEGS])
                trim.update((x, y) for x, y in regions[CHEST] if (x, y + 1) in legs)
            # The half-elf Preserver's mantle is outside the equipment regions.
        elif model in DWARVES:
            trim = dwarfarmordye.protected(frame, role, pose, model)
        elif model in ELVES:
            trim = elfarmordye.protected(frame, role, pose, model)
        else:
            landmark = LANDMARKS[pose] if model == 2095 and pose < len(LANDMARKS) else None
            trim = humanarmordye.protected(frame, role, pose, model, landmark)
        if mantle and not cape:
            donor = mantle[f]
            # Both outfits have native coordinates, including the wider side step.
            foreground = {point for bit in (ARMS, FOREARM, BOW, LEFT_FOOT, RIGHT_FOOT)
                          for point in regions[bit]}
            if model != 2095:
                foreground.update(head)
            fabric = {(x, y): donor.image[y + top][x + left] for x, y, _ in donor.cloak
                      if (x, y) not in foreground and donor.image[y + top][x + left] not in (None, 255)}
            # A few isolated mantle pixels belong to the Mage's layered tunic.
            # On the open teal wrap they would look like flecks along the calf.
            cape = tuple((x, y, shade) for (x, y), shade in fabric.items()
                         if any((x + dx, y + dy) in fabric for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                                if dx or dy))
        plate = None
        if model == 2099 and role == "Priest":
            plate = {bit: humanpriestplate.cells(frame, pose, bit) for bit in (CHEST, ARMS, LEGS)}
        elif model == 2059 and "Cleric" in members:
            plate = {bit: elfclericplate.cells(frame, pose, bit) for bit in (CHEST, ARMS, LEGS)}
        if plate is not None:
            # The Priest's fitted cuirass and wristbands are traced under the
            # collar and hair. Her broader cloth-dye trim also includes metal.
            foreground = set(frame.head) | set(regions[BOW])
            if native_cloak:
                foreground.update((x, y) for x, y, _ in folds)
            for bit, cells in plate.items():
                keep = foreground if model == 2099 else foreground | trim
                plate[bit] = tuple(point for point in cells if point not in keep)
        poses.append(frame._replace(armor_trim=frozenset(trim), equipped_cape=cape, plate_regions=plate))
    return tuple(poses)
