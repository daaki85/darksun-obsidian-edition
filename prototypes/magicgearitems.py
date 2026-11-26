"""Equipment for the magic surface comparisons, resolved through the Loader's worn().

The leather is Legcrusher's Inixhide +1. Bone Scale Chest Armor is a retail
item without a bonus; the test enchants a copy of the placed chest piece +1.
The cloak, bracers, boots and belt use the mod's actual named item records and icons.
Each case equips one item, so its material and sparks can be checked in isolation.
"""
import struct

from wornreview import game, icons, sprites, worldgear
from dsloader import bonescale, dataitems, npcitems


class EquippedItem:
    def __init__(self, slot, record, retail_types):
        self.record = bytearray(record)
        self.record[game.ITEM_SLOT] = game.EQUIP_SLOTS.index(slot)
        name = icons.which(self.record)
        if name:
            # The attached Loader fits this icon when its objects file is active.
            struct.pack_into("<H", self.record, 0, icons.picture(name, True))
        kind, = struct.unpack_from("<H", self.record, game.ITEM_TYPE)
        if kind >= game.GAME_TYPES:
            self.kind = npcitems.TYPES[kind - game.GAME_TYPES]
        else:
            offset = kind * game.ITEM_TYPE_SIZE
            self.kind = retail_types[offset:offset + game.ITEM_TYPE_SIZE]
            if len(self.kind) != game.ITEM_TYPE_SIZE:
                raise ValueError(f"GPLDATA.GFF IT1R/1 has no record for item type {kind}")

    def _worn(self, member):
        return [(0, self.record, self.kind)]


def equipped_items(atlas):
    """The same equipped records used by the picture audit and DOSBox check."""
    records, _ = dataitems.records(atlas.game.chunks["RDFF", bonescale.CHEST_OBJECT])
    bone = bytearray(next(r.data for r in records if r.kind == dataitems.ITEM
                          and len(r.data) == game.ITEM_SIZE
                          and struct.unpack_from("<H", r.data)[0] == bonescale.CHEST_PICTURE))
    bone[game.ITEM_PLUS] = 1
    for label, slot, record in (
        ("Magic leather", "chest", npcitems.CHEST_ARMOR),
        ("Magic bone", "chest", bone),
        ("Magic cloak", "cloak", worldgear.ELVEN_CLOAK),
        ("Magic bracers", "arm", worldgear.bracers(5)),
        ("Magic boots", "foot", worldgear.SPEED_BOOTS),
        ("Magic belt", "waist", worldgear.BACK_GIRDLE_ITEM),
    ):
        yield label, EquippedItem(slot, record, atlas.game.item_types)


def _resolve(atlas, items):
    catalog = dict(atlas.game.chunks)
    catalog.update(icons.new_chunks(atlas.game.chunks))
    cases = {"Empty": ({}, ())}
    for label, equipped in items:
        cases[label] = sprites.worn(equipped, 0, catalog)
    return cases


def loadouts(atlas):
    return _resolve(atlas, equipped_items(atlas))


def belt_loadouts(atlas):
    """The retail Belt of Might and both Obsidian Edition girdles, each worn alone."""
    records, _ = dataitems.records(atlas.game.chunks["RDFF", 30017])
    might = next(r.data for r in records if r.kind == dataitems.ITEM
                 and len(r.data) == game.ITEM_SIZE and struct.unpack_from("<H", r.data, game.ITEM_TYPE)[0] == 35)
    belts = (("Belt of Might", might), ("Girdle of Back Defense", worldgear.BACK_GIRDLE_ITEM),
             ("Golden Girdle of Urnst", worldgear.URNST_GIRDLE_ITEM))
    return _resolve(atlas, ((name, EquippedItem("waist", record, atlas.game.item_types)) for name, record in belts))
