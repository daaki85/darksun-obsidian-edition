"""Two magic robes for those who go without armour: preservers, psionicists and druids (the
type's class bits). A robe is worn on the chest, in the chest armour's place, its plus counting
for AC as bracers' does (and, like them, only with no armour on the arms, legs or head), and it
isn't armour: a preserver casts in it, a cloak of protection still counts (DSCLOG's ROBE type,
BRACERS_AX, ROBE_PLUS).

- The Ashen Robe (+1): AC 1 better, and +1 on saves against wizards' and priests' spells. Worn by
  Kalzith, who sells it, and left with his body (kalzith.py).
- The Veiled Robe (+2), a robe of the Veiled Alliance: AC 2 better, +1 on every save, and a
  wizard spell slot more at spell levels 1 to 3 where its wearer has any. Sold by Kel
  (worldgear.py).

The two are told apart by their plus (the item's +14h)."""

import struct

from . import game

ASHEN, VEILED = 0x161, 0x162  # their names (DSCLOG's EXTRA_NAMES)
NAMES = {ASHEN: b"Ashen Robe", VEILED: b"Veiled Robe"}
FULL_NAMES = {ASHEN: "Ashen Robe", VEILED: "Robe of the Veiled Alliance"}
ASHEN_PLUS, VEILED_PLUS = 1, 2
SPELL_LAST = 137  # (the wizards' and priests' spells: not psionic powers nor monsters' own)
# priced as the game's magic clothes and the mod's: a cloak of protection 15,000 (the Ashen Robe
# less, being early), the Warden's Chest 36,000
ASHEN_VALUE, VEILED_VALUE = 6000, 40000
PICTURE_ASHEN, PICTURE_VEILED = 0x10000 - 2580, 0x10000 - 2582  # (their objects, icons.py: negated)


def item(name: int) -> bytes:
    """A robe's item record (the game's 21 bytes), as the worldgear items are made."""
    from . import worldgear
    plus, value, picture = ((ASHEN_PLUS, ASHEN_VALUE, PICTURE_ASHEN) if name == ASHEN
                            else (VEILED_PLUS, VEILED_VALUE, PICTURE_VEILED))
    return worldgear.armour(game.ROBE_TYPE, name, picture, value, plus=plus)


def save(plus: int, spell: int) -> int:
    """What a worn robe of PLUS adds to a save against SPELL (KIT_SAVE's)."""
    if plus >= VEILED_PLUS:
        return 1
    if plus == ASHEN_PLUS and 0 <= spell <= SPELL_LAST:
        return 1
    return 0


def slots(plus: int, magic: int, spell_level: int, slots_now: int) -> int:
    """The wizard slots at SPELL_LEVEL with a worn robe of PLUS (PROBE_SLOTS'): the Veiled Robe's
    one more at spell levels 1-3 where there are any."""
    from . import kits
    if plus >= VEILED_PLUS and magic == kits.WIZARD and slots_now and 1 <= spell_level <= 3:
        return slots_now + 1
    return slots_now


def worn_plus(worn) -> int:
    """The plus of the robe among WORN ((index, item record, type record), as GameData._worn
    gives them) on the chest, else 0."""
    for _, rec, _ in worn:
        if struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] == game.ROBE_TYPE and rec[game.ITEM_SLOT] == CHEST_SLOT:
            return struct.unpack("b", rec[game.ITEM_PLUS:game.ITEM_PLUS + 1])[0]
    return 0


CHEST_SLOT = game.EQUIP_SLOTS.index("chest")
