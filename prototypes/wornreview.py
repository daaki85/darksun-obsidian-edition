"""Render equipment comparisons through the party picture builder.

python prototypes/wornreview.py GAME_DIR OUTPUT_DIR
"""
import argparse
from functools import lru_cache
from pathlib import Path
import struct

from PIL import Image

from elfreview import TERRAIN, dwarf, elf, label, loop
from dsloader import art, game, icons, robes, spritegear as sg, sprites, worldgear

FIGURES = ("Human man", "Human woman", "Dwarf man", "Dwarf woman", "Elf man", "Elf woman")
# Outfit, retail reference, pose for the comparison plate.
CASES = {
    "Class colors": ("Fighter", 1252, 0),
    "Chest plate": ("Fighter", 1342, 0),
    "Full plate": ("Fighter", 1342, 0),
    "Warden's Plate": ("Fighter", 1342, 15),
    "Ashen Robe": ("Psionicist", 1563, 3),
    "Veiled Robe": ("Psionicist", 724, 3),
    "Cloak": ("Thief", 630, 1),
    "Boots of Speed": ("Fighter", 2099, 9),
    "Chameleon glove": ("Fighter", 1252, 16),
    "Quicksilver glove": ("Fighter", 1252, 16),
    "Bracers": ("Fighter", 1252, 21),
    "Sword and shield": ("Fighter", 1252, 16),
    "Bow and quiver": ("Fighter", 1252, 24),
}
WEAPONS = {
    "Dagger": (17, 3), "Short sword": (game.METAL_SHORT_SWORD_TYPE, 4), "Sword": (63, 4),
    "Club": (18, 0), "Mace": (20, 1), "Pick": (112, 2), "Axe": (22, 4),
    "Great axe": (game.METAL_GREAT_AXE_TYPE, 4), "Polearm": (game.METAL_POLEARM_TYPE, 4),
    "Gythka": (44, 1), "Cahulaks": (21, 1), "Staff": (3, 0), "Shield": (4, 5),
    "Sling": (64, 5), "Staff sling": (0, 5), "Bow": (1, 0), "Chatkcha": (48, 3),
}


class Loadout:
    def __init__(self, equipped):
        self.items = []
        for slot, data in equipped:
            item = bytearray(data)
            item[game.ITEM_SLOT] = game.EQUIP_SLOTS.index(slot)
            self.items.append((len(self.items), item, bytes(game.ITEM_TYPE_SIZE)))

    def _worn(self, member):
        return self.items


def glove(kind, obj):
    rec = bytearray(game.ITEM_SIZE)
    struct.pack_into("<H", rec, 0, -obj & 0xffff)
    struct.pack_into("<H", rec, game.ITEM_TYPE, kind)
    rec[game.ITEM_POWER] = 1
    return rec


class Atlas:
    def __init__(self, game_dir):
        self.game = elf.outfits.Game(game_dir)
        self.pictures = sprites.Pictures(self.game.chunks)
        self.floor = Image.open(TERRAIN).convert("RGB").crop((50, 150, 102, 194))
        catalog = dict(self.game.chunks)
        catalog.update(icons.new_chunks(self.game.chunks))
        named = {
            "Warden's Plate": zip(("chest", "arm", "legs", "head"), worldgear.WARDENS_PLATE),
            "Ashen Robe": [("chest", robes.item(robes.ASHEN))],
            "Veiled Robe": [("chest", robes.item(robes.VEILED))],
            "Boots of Speed": [("foot", worldgear.SPEED_BOOTS)],
            "Elven boots": [("foot", worldgear.ELVEN_BOOTS)],
            "Chameleon glove": [("right hand", glove(37, 30020))],
            "Quicksilver glove": [("right hand", glove(113, 30021))],
        }
        self.gear = {name: sprites.worn(Loadout(items), 0, catalog) for name, items in named.items()}
        self.gear.update({
            "Class colors": ({}, ()), "Chest plate": ({}, (88,)), "Full plate": ({}, (88, 25, 26)),
            "Cloak": ({"cloak": (65, 5)}, ()), "Bracers": ({}, (game.BRACERS_TYPE | sg.MAGIC_ARMOUR,)),
            "Sword and shield": ({"right": (63, 4), "left": (4, 5)}, ()),
            "Bow and quiver": ({"missile": (1, 0), "ammo": (62, 0)}, ()),
        })
        for name, item in WEAPONS.items():
            slot = "left" if name == "Shield" else "missile" if name in ("Bow", "Chatkcha", "Sling", "Staff sling") else "right"
            gear = {slot: item}
            self.gear[name] = gear, ()

    @lru_cache(maxsize=360)
    def sequence(self, obj, combat, role, name):
        gear, arm = self.gear[name]
        chunk = self.pictures.build(obj, combat, gear, arm, role=role)
        return [art.decode_frame(chunk, f)[2] for f in range(14 if combat else 15)]

    def tile(self, obj, pose, role, name, scale):
        combat, f = divmod(pose, 15)
        if obj in range(300, 306):
            if obj < 302 and role == "Fighter":
                role = "Warrior"
            rows = self.sequence(obj, combat, role, name)[f]
            side, top = sprites.room(combat)
        else:
            rows = self.game.fr(obj + combat, f)
            side = top = 0
        return elf.placed_tile(self.game, rows, self.floor, scale, side, top, 0)

    def comparison(self, output):
        canvas = Image.new("RGB", (915, 66 + len(CASES) * 135), dwarf.PAPER)
        label(canvas, (8, 6), "Worn equipment on the arena floor", 19)
        for j, title in enumerate((*FIGURES, "Retail figure")):
            label(canvas, (156 + 116 * j, 40), title, 12, "ma")
        for i, (name, (role, npc, pose)) in enumerate(CASES.items()):
            y = 62 + 135 * i
            label(canvas, (5, y + 16), name, 11)
            label(canvas, (5, y + 39), dwarf.NAMES[pose], 10)
            label(canvas, (5, y + 62), f"Ref. {npc}", 11)
            for j, obj in enumerate((*range(300, 306), npc)):
                for scale, offset in ((2, 0), (1, 89)):
                    tile = self.tile(obj, pose, role, name, scale)
                    canvas.paste(tile, (156 + j * 116 - tile.width // 2, y + offset))
        canvas.save(output / "worn-equipment.png")

    def materials(self, output):
        # Read across a row to see a change of material on exactly the same pose.
        self.gear.update({
            "Leather": ({}, (6, 7, 8)), "Studded bone": ({}, (12, 13, 14)),
            "Scale": ({}, (15, 55, 56)), "Chain": ({}, (57, 58, 59)),
            "Magic plate": ({}, (88 | sg.MAGIC_ARMOUR,)),
            "Leather boots": ({"boots": (68, 5)}, ()),
            "Wood": ({"right": (18, 0)}, ()), "Bone": ({"right": (game.BONE_SHORT_SWORD_TYPE, 1)}, ()),
            "Stone": ({"right": (20, 2)}, ()), "Obsidian": ({"right": (game.OBSIDIAN_SHORT_SWORD_TYPE, 3)}, ()),
            "Steel": ({"right": (game.METAL_SHORT_SWORD_TYPE, 4)}, ()),
        })
        cases = (
            ("Armor", 300, "Fighter", 0, ("Leather", "Studded bone", "Scale", "Chain", "Full plate"), 1342),
            ("Mantle", 304, "Preserver", 0, ("Class colors", "Chest plate", "Magic plate", "Veiled Robe", "Cloak"), 724),
            ("Rear mantle", 304, "Preserver", 8, ("Class colors", "Full plate", "Warden's Plate", "Ashen Robe", "Cloak"), 724),
            ("Footwear", 301, "Warrior", 3, ("Class colors", "Leather boots", "Elven boots", "Boots of Speed", "Full plate"), 2099),
            ("Weapons", 302, "Fighter", 16, ("Wood", "Bone", "Stone", "Obsidian", "Steel"), 1252),
        )
        canvas = Image.new("RGB", (828, 38 + 160 * len(cases)), dwarf.PAPER)
        label(canvas, (8, 7), "Equipment materials in the same pose", 18)
        for i, (title, obj, role, k, options, npc) in enumerate(cases):
            y = 40 + 160 * i
            label(canvas, (5, y + 28), title, 13)
            label(canvas, (5, y + 49), FIGURES[obj - 300], 11)
            label(canvas, (5, y + 70), dwarf.NAMES[k], 10)
            for j, name in enumerate((*options, f"Retail {npc}")):
                x = 155 + 120 * j
                label(canvas, (x, y), name, 12, "ma")
                for scale, off in ((2, 19), (1, 109)):
                    tile = self.tile(obj if j < 5 else npc, k, role, name, scale)
                    canvas.paste(tile, (x - tile.width // 2, y + off))
        canvas.save(output / "worn-materials.png")

    def motion(self, output, obj, weapons=False):
        names = list(WEAPONS if weapons else CASES)
        cols = 5
        images = []
        for pose, caption in enumerate(dwarf.NAMES):
            canvas = Image.new("RGB", (cols * 130, 34 + 151 * ((len(names) + cols - 1) // cols)), dwarf.PAPER)
            label(canvas, (8, 5), FIGURES[obj - 300] + (" · weapon families" if weapons else " · equipment"), 17)
            label(canvas, (640, 8), caption, 13, "ra")
            for i, name in enumerate(names):
                x, y = (i % cols) * 130 + 65, (i // cols) * 151 + 32
                role = "Fighter" if weapons else CASES[name][0]
                label(canvas, (x, y), name, 12, "ma")
                for scale, offset in ((2, 16), (1, 105)):
                    tile = self.tile(obj, pose, role, name, scale)
                    canvas.paste(tile, (x - tile.width // 2, y + offset))
            images.append(canvas)
        stem = "worn-weapons" if weapons else "worn-" + FIGURES[obj - 300].lower().replace(" ", "-")
        loop(images, output / (stem + ".gif"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    atlas = Atlas(args.game_dir)
    atlas.comparison(args.output)
    atlas.materials(args.output)
    for obj in range(300, 306):
        atlas.motion(args.output, obj)
    atlas.motion(args.output, 302, weapons=True)
