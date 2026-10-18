"""New weapons and bracers in the world: merchants' stock and people's packs.

- The Loader's plain weapons (weaponchoice.py): the bone and obsidian short swords and axes, the
  obsidian mace and a plain metal short sword. The game has no other short sword than Kurzak's,
  no axe but a metal one, and no obsidian mace but Blackmace. The two merchants who sell plain
  weapons stock them, and a few kinds of people carry one, as their loot.
- Metal versions of the plain weapons the game has in no metal (a dagger but Dag's Dagger +3, a
  mace, a great axe, a pick, a polearm): one each, on people who fight with the like.
- Magic weapons of the kinds the game has none of (a club, a pick, a staff sling; a short sword
  but Shadowseeker): one each, priced as the game's magic weapons of the like.
- A circlet and a crown, worn on the head and not armour (no AC; bracers of defense and a
  preserver's spells go with them), each with a spell the game keeps on its wearer while it's
  worn, as it does its own magic items': Arrowbane, Protection from Normal Missiles, sold by
  Kel; the Sunking Crown, Protection from Evil, worn by Keldar, the templar of Dagolar's tunnels.
- The Warden's Plate, plate mail +1 (DSCLOG's plate types: AC 3 chest, 2 arms, 2 legs, as AD&D's
  piecemeal plate; the helm the game's metal one), its four pieces scattered: the helm on
  Dagolar's body; the arms in the Lower Castle's treasure chest with Dark Flame (behind the
  wall the Serpent Boots show, the vrock's cliff); the legs in the Gemfields' chest; the chest
  on Balkazar's body. The chest puts Resist Fire on its wearer while worn, the helm Cloak of
  Bravery; the arms and legs are plain.
- The Cloak and Boots of Elvenkind (DSCLOG's types, the game's Cloak's and Boots', for thieves and
  rangers; their stealth: stealth.py): the cloak the Elven Leader's gift with his Gythka (+2: his
  script gives it: elvenleader.py), the boots in the buried chest of Kel's caravan, with the
  Cahulaks +1.
- The Flame Blade, an obsidian long sword +1 (fire clerics can wield it) whose blade burns what it
  hits, as the game's Dark Flame does with Burning Hands: Focus Heat, the fire clerics' spell, cast
  as a weapon's spells are, at caster level 0: 2d6 of fire to the one hit, a save for half (AD&D's
  flame blade: 1d6 of fire; the game's Produce Fire, 1d6, sets the ground alight and burns friends
  standing there): in the pack of the Hot Springs' Templar (the one with the Drake Shield).
- The magic axes: Drakejaw, a bone axe +1, on one of the Magera guarding the wagon's prisoners;
  Glasshewer, an obsidian axe +2, on the elven slavers' Templar; Headsman, a metal great axe +2,
  in the arena Announcer's stash. And the Elven Leader's Gythka +1 made +2.
- Weapons for those who had too few magic ones: Galefang, a metal dagger +2 of DSCLOG's own type
  (made when no dagger was an air cleric's; now every one is), on the Rogue Shaman; Mindshard, an obsidian short sword +1, on Maris,
  and Stillwater, a bone short sword +1, in the chest Chaya gives as her apology (psionicists',
  alone or with a cleric's); Linebreaker, a metal polearm +2, on the Troop Leader; Thornwall, a
  bone polearm +1, on the slave pens' weapon rack, in place of one of its two plain ones.
- Magic shields, which the game has two of (the Drake Shield +1 and El's Shield +2, both
  leather): Gutterward, a wooden shield +1, on a skeleton in the warrens (one of the region's
  three, given an object of its own: the skeletons of five regions share theirs); Ironbulwark, a
  metal shield +3 (DSCLOG's type: the game has no metal shield), carried by the Guardian of
  Balkazar's fortress.
- Bracers of defense (DSCLOG's BRACERS type, worn on the arms: their plus counts for AC while neither
  armour nor a helm is worn), now that a preserver can't cast in armour: on four
  of the game's wizards, better the later they're met.

All of them are in the game's data (dataitems.py): the launcher writes them into their people's
and chests' objects in its copy of SEGOBJEX.GFF, by the Options tab's switches, so a new game
has them where the game makes those people and chests. People of a kind who share an object
(the Tari, Renegades, Wild Muls) each carry the item; one Castle Guard, one Undermountain miner
and one Magera have an object of their own for theirs (a copy of their kind's, and their region's entity
pointing to it, in the Loader's copy of that region's file).
"""

import struct
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

from . import dataitems, game, npcitems, specialize, weaponchoice

# the bone long sword the game's merchants sell (SEGOBJEX's), which the weapons are made from
TEMPLATE = npcitems._item("0cfc000000002d000000510000000000" "04ff1c0000")
KIND = specialize.KINDS.index
BONE_SHORT_SWORD = weaponchoice.PLAIN[KIND("short sword")]
OBSIDIAN_SHORT_SWORD = weaponchoice.OTHERS[KIND("short sword")][0]
BONE_AXE = weaponchoice.PLAIN[KIND("axe")]
OBSIDIAN_AXE = weaponchoice.OTHERS[KIND("axe")][0]
OBSIDIAN_MACE = weaponchoice.OTHERS[KIND("mace")][0]
METAL_SHORT_SWORD = (game.METAL_SHORT_SWORD_TYPE, 0x144, 0x10000 - 2427, 300)  # (the metal long sword: 500)
METAL_DAGGER = (game.METAL_DAGGER_TYPE, 0x10, 0x10000 - 2504, 50)
METAL_MACE = (game.METAL_MACE_TYPE, 0x13, 0x10000 - 2506, 200)
BONE_DAGGER = weaponchoice.OTHERS[KIND("dagger")][1]
BONE_GREAT_AXE = weaponchoice.PLAIN[KIND("great axe")]
OBSIDIAN_GREAT_AXE = weaponchoice.OTHERS[KIND("great axe")][0]
METAL_GREAT_AXE = weaponchoice.OTHERS[KIND("great axe")][1]  # (300)
METAL_PICK = (game.METAL_PICK_TYPE, 0xAD, 0x10000 - 2510, 150)
METAL_POLEARM = weaponchoice.OTHERS[KIND("polearm")][0]  # (250)
# (type, name entry, picture, price) and plus, priced as the game prices its own: a melee weapon as
# the Obsidian Bloodwrath +1 (20,800, as its Hornblade +1 and Gythka +1), 20,800 a plus; a missile
# weapon far less, as its Sling +1 (2,800; the Chatkcha +1 1,800, the Sling +2 3,500)
PLUS_VALUE, SLING_VALUE = 20800, 2800
# each with a name of its own (DSCLOG's names; Alagorn tells their stories, alagorn.py)
GUTTERKNOT, DEEPBITER, WINDLASH, GREENBRIGHT = 0x14A, 0x14B, 0x14C, 0x14D
NAMES = {GUTTERKNOT: b"Gutterknot", DEEPBITER: b"Deepbiter", WINDLASH: b"Windlash", GREENBRIGHT: b"Greenbright"}
CLUB_1 = ((18, GUTTERKNOT, 0x10000 - 2494, PLUS_VALUE), 1)  # a club +1
PICK_1 = ((112, DEEPBITER, 0x10000 - 2496, PLUS_VALUE), 1)  # a stone pick +1
STAFF_SLING_1 = ((0, WINDLASH, 0x10000 - 2498, SLING_VALUE), 1)  # a staff sling +1
SHORT_SWORD_2 = ((game.METAL_SHORT_SWORD_TYPE, GREENBRIGHT, 0x10000 - 2500, 2 * PLUS_VALUE), 2)  # a metal short sword +2
# the magic axes: a bone axe +1 (a water cleric's), an obsidian axe +2 (a fire or earth cleric's),
# a metal great axe +2
DRAKEJAW, GLASSHEWER, HEADSMAN = 0x159, 0x15A, 0x15B
NAMES.update({DRAKEJAW: b"Drakejaw", GLASSHEWER: b"Glasshewer", HEADSMAN: b"Headsman"})
BONE_AXE_1 = ((game.BONE_AXE_TYPE, DRAKEJAW, 0x10000 - 2554, PLUS_VALUE), 1)
OBSIDIAN_AXE_2 = ((game.OBSIDIAN_AXE_TYPE, GLASSHEWER, 0x10000 - 2556, 2 * PLUS_VALUE), 2)
GREAT_AXE_2 = ((game.METAL_GREAT_AXE_TYPE, HEADSMAN, 0x10000 - 2558, 2 * PLUS_VALUE), 2)
# the weapons for those who had too few magic ones: an air cleric's dagger +2 (DSCLOG's own type: no dagger
# of the game's is an air cleric's), an obsidian and a bone short sword +1 (a psionicist's, alone or
# with a fire, earth or water cleric's), a metal polearm +2 and a bone one +1 (the game has no
# polearm to find)
GALEFANG, MINDSHARD, STILLWATER, LINEBREAKER, THORNWALL = 0x15C, 0x15D, 0x15E, 0x15F, 0x160
NAMES.update({GALEFANG: b"Galefang", MINDSHARD: b"Mindshard", STILLWATER: b"Stillwater", LINEBREAKER: b"Linebreaker",
              THORNWALL: b"Thornwall"})
AIR_DAGGER_2 = ((game.AIR_DAGGER_TYPE, GALEFANG, 0x10000 - 2564, 2 * PLUS_VALUE), 2)
OBSIDIAN_SHORT_SWORD_1 = ((game.OBSIDIAN_SHORT_SWORD_TYPE, MINDSHARD, 0x10000 - 2566, PLUS_VALUE), 1)
BONE_SHORT_SWORD_1 = ((game.BONE_SHORT_SWORD_TYPE, STILLWATER, 0x10000 - 2568, PLUS_VALUE), 1)
POLEARM_2 = ((game.METAL_POLEARM_TYPE, LINEBREAKER, 0x10000 - 2570, 2 * PLUS_VALUE), 2)
BONE_POLEARM = 19  # (the game's Polearm, of bone)
BONE_POLEARM_1 = ((BONE_POLEARM, THORNWALL, 0x10000 - 2572, PLUS_VALUE), 1)
# the weapons for the kits with too few (the dagger fighters, the archers, the thri-kreen): a bone
# dagger +1 in Merzol's hay stash (his script's: haystash.py), an obsidian dagger +2 on the Lava
# Rift's Hermit (in place of his stone one), a bow +1 the Bowyer sells (priced as a melee weapon:
# the game's Bow +2 is 50,800), a chatkcha +2 on a thri-kreen of the Gemfields' packs
HAYNEEDLE, NIGHTSLIVER, DUNESONG, SKYCUTTER = 0x165, 0x166, 0x167, 0x168
NAMES.update({HAYNEEDLE: b"Hayneedle", NIGHTSLIVER: b"Nightsliver", DUNESONG: b"Dunesong", SKYCUTTER: b"Skycutter"})
HAYNEEDLE_OBJECT = 2590  # (its picture's object: the item the hay stash's script drops)
BONE_DAGGER_1 = ((game.BONE_DAGGER_TYPE, HAYNEEDLE, 0x10000 - HAYNEEDLE_OBJECT, PLUS_VALUE), 1)
OBSIDIAN_DAGGER = 17  # (the game's Dagger, of obsidian; its other, 33, is stone)
OBSIDIAN_DAGGER_2 = ((OBSIDIAN_DAGGER, NIGHTSLIVER, 0x10000 - 2592, 2 * PLUS_VALUE), 2)
BOW = 1  # (the game's Bow)
BOW_1 = ((BOW, DUNESONG, 0x10000 - 2594, PLUS_VALUE), 1)
CHATKCHA = 48
CHATKCHA_2 = ((CHATKCHA, SKYCUTTER, 0x10000 - 2596, 3500), 2)  # (as the game's Sling +2)
HERMIT, LAVA_RIFT = 81, 0x1B
STONE_DAGGER = 33
GEMFIELDS, GEMFIELDS_KREEN, THRIKREEN = 0x06, 22, 215  # (one of a pack: object 215 is shared)
# the Elven Leader's Gythka +1 (in his pack, object 124; and the item his script gives, a new one of
# object 2534) a Gythka +2
ELVEN_LEADER, ELVEN_GYTHKA = 124, 2534

BRACERS_NAME = 0x149  # the name entry DSCLOG adds ("Bracers/Defense")
ARROWBANE, SUNKING_CROWN = 0x14E, 0x14F  # and the circlet's and crown's
NAMES[ARROWBANE], NAMES[SUNKING_CROWN] = b"Arrowbane", b"Sunking Crown"
ITEM_SPELL, ITEM_SPELL_SHOWN = 0x0F, 0x02  # a magic item's spell, one past its number (as arms.py's)
PROT_MISSILES, PROT_EVIL = 36, 76  # the game's Prot'n from Normal Missiles, Protection from Evil
HEAD = game.EQUIP_SLOTS.index("head")
BRACERS_PICTURE = 0x10000 - 2502
ARM = game.EQUIP_SLOTS.index("arm")


def weapon(spec: Tuple[int, int, int, int], plus: int = 0) -> bytes:
    """A weapon's item record, in no list and no slot."""
    rec = bytearray(weaponchoice.plain_weapon(TEMPLATE, 0, spec)[0])
    rec[game.ITEM_PLUS] = plus
    return bytes(rec)


def bracers(ac: int) -> bytes:
    """Bracers of defense of armour class AC (AD&D's 2-8): a plus of 10 - AC, priced 5,000 a
    point (AC 6 20,000, as the game's magic armour and shields: Shimmer Armor +3 24,000, the Drake
    Shield +1 25,400; AC 2 40,000, as its magic rings, 30,000-50,000)."""
    rec = bytearray(TEMPLATE)
    struct.pack_into("<H", rec, 0, BRACERS_PICTURE)
    struct.pack_into("<H", rec, weaponchoice.ITEM_VALUE, 5000 * (10 - ac))
    struct.pack_into("<H", rec, game.ITEM_TYPE, game.BRACERS_TYPE)
    struct.pack_into("<H", rec, game.ITEM_NAME, BRACERS_NAME)
    rec[game.ITEM_PLUS] = 10 - ac
    return bytes(rec)


def head_item(type_: int, name: int, picture: int, value: int, spell: int) -> bytes:
    """A circlet's or crown's item record: its spell put on its wearer while worn."""
    rec = bytearray(TEMPLATE)
    struct.pack_into("<H", rec, 0, picture)
    struct.pack_into("<H", rec, ITEM_SPELL_SHOWN, spell + 1)  # (as the game keeps it)
    struct.pack_into("<H", rec, weaponchoice.ITEM_VALUE, value)
    struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
    struct.pack_into("<H", rec, game.ITEM_NAME, name)
    rec[ITEM_SPELL] = spell + 1
    return bytes(rec)


# priced as the game's magic helms: the Helm of Might 30,000, the Helm of Contemplation 35,000
ARROWBANE_ITEM = head_item(game.CIRCLET_TYPE, ARROWBANE, 0x10000 - 2514, 30000, PROT_MISSILES)
CROWN_ITEM = head_item(game.CROWN_TYPE, SUNKING_CROWN, 0x10000 - 2516, 40000, PROT_EVIL)


WARDENS_CHEST, WARDENS_ARMS, WARDENS_LEGS, WARDENS_HELM = 0x150, 0x151, 0x152, 0x153
NAMES.update({WARDENS_CHEST: b"Warden's Chest", WARDENS_ARMS: b"Warden's Arms", WARDENS_LEGS: b"Warden's Legs",
              WARDENS_HELM: b"Warden's Helm"})
RESIST_FIRE, CLOAK_OF_BRAVERY = 87, 109
METAL_HELM_TYPE = 89  # (the game's metal helm: the Helm of Contemplation's)


def armour(type_: int, name: int, picture: int, value: int, spell: Optional[int] = None, plus: int = 1) -> bytes:
    """A piece of magic armour's item record: SPELL, if any, put on its wearer while worn."""
    rec = bytearray(head_item(type_, name, picture, value, spell or 0))
    if spell is None:
        struct.pack_into("<H", rec, ITEM_SPELL_SHOWN, 0)
        rec[ITEM_SPELL] = 0
    rec[game.ITEM_PLUS] = plus
    return bytes(rec)


# priced as the game's own: the arms and legs (AC 3) as a piece of Grey's Scale (27,000, now AC 3
# too), the chest (AC 4, a spell) 36,000, the helm as the Helm of Might (30,000)
WARDENS_PLATE = (
    armour(game.PLATE_CHEST_TYPE, WARDENS_CHEST, 0x10000 - 2538, 36000, RESIST_FIRE),
    armour(game.PLATE_ARMS_TYPE, WARDENS_ARMS, 0x10000 - 2540, 27000),
    armour(game.PLATE_LEGS_TYPE, WARDENS_LEGS, 0x10000 - 2542, 27000),
    armour(METAL_HELM_TYPE, WARDENS_HELM, 0x10000 - 2544, 30000, CLOAK_OF_BRAVERY),
)


DARK_FLAME_CHEST, GEMFIELDS_CHEST = 1360, 1065  # (SEGOBJEX objects: their item records' picture, negated)
CARAVAN_CHEST = 2293  # the elven caravan's buried chest (with the Cahulaks +1)
CLOAK_OF_ELVENKIND, BOOTS_OF_ELVENKIND = 0x154, 0x155
NAMES.update({CLOAK_OF_ELVENKIND: b"Cloak/Elvenkind", BOOTS_OF_ELVENKIND: b"Boots/Elvenkind"})
# priced as the game's magic clothes: its Serpent Boots 20,000, Chameleon Gloves 30,000
ELVEN_CLOAK = armour(game.ELVEN_CLOAK_TYPE, CLOAK_OF_ELVENKIND, 0x10000 - 2546, 25000, plus=0)
ELVEN_BOOTS = armour(game.ELVEN_BOOTS_TYPE, BOOTS_OF_ELVENKIND, 0x10000 - 2548, 20000, plus=0)
FLAME_BLADE_NAME, OBSIDIAN_LONG_SWORD, FOCUS_HEAT = 0x156, 45, 116
from . import robes  # noqa: E402 (the robes: the Veiled Robe sold by Kel)
VEILED_ROBE = armour(game.ROBE_TYPE, robes.VEILED, robes.PICTURE_VEILED, robes.VEILED_VALUE, plus=robes.VEILED_PLUS)
# the magic shields, priced as the game's (the Drake Shield +1 25,400, El's Shield +2 50,200): 25,000
# a plus, the +3 at 65,000 (a price is a word: the game's dearest, the Wand of Missiles, is 65,000)
GUTTERWARD, IRONBULWARK = 0x163, 0x164
NAMES.update({GUTTERWARD: b"Gutterward", IRONBULWARK: b"Ironbulwark"})
WOODEN_SHIELD_TYPE = 16  # (the game's wooden Shield; its other, 4, is leather)
WOODEN_SHIELD_1 = armour(WOODEN_SHIELD_TYPE, GUTTERWARD, 0x10000 - 2586, 25000)
METAL_SHIELD_3 = armour(game.METAL_SHIELD_TYPE, IRONBULWARK, 0x10000 - 2588, 65000, plus=3)
WARRENS, WARRENS_SKELETON, SKELETON = 0x28, 85, 2266  # (the skeleton at 1913, 577; object 2266 is shared)
GUARDIAN, BALKAZARS = 216, 0x0D  # (the Guardian of Balkazar's fortress, with the Chatkcha +1)
NAMES[FLAME_BLADE_NAME] = b"Flame Blade"


def magic_weapon(spec: Tuple[int, int, int, int], plus: int, spell: int) -> bytes:
    """A magic weapon that casts SPELL (the game's number) on what it hits (a helpful one: on its
    wielder while readied)."""
    rec = bytearray(weapon(spec, plus))
    struct.pack_into("<H", rec, ITEM_SPELL_SHOWN, spell + 1)
    rec[ITEM_SPELL] = spell + 1
    return bytes(rec)


# priced as Shadowseeker (a plus and a spell: 22,000)
FLAME_BLADE = magic_weapon((OBSIDIAN_LONG_SWORD, FLAME_BLADE_NAME, 0x10000 - 2550, 22000), 1, FOCUS_HEAT)  # the Elven Leader's gift (the game's own: its own name, not Kreenfang)


class Gift(NamedTuple):
    """Items for the people or chests of OBJECTS (SEGOBJEX's), written into their data. CLONE: the
    objects' people share theirs with others of their kind (one object each kind), and the items
    are for one of them: the person of entity ENTITY of the region's table (ETAB), who gets an
    object of their own, NEW, a copy of their kind's. INSTEAD: (item type, plus) of an item of
    theirs the (one) item takes the place of, the first of the kind; None, the items are added."""
    name: str
    items: Tuple[bytes, ...]
    objects: Tuple[int, ...]
    region: Optional[int] = None  # (where: the region's file, for a clone; None, RGNFF's people)
    clone: Optional[Tuple[int, int]] = None  # (entity, new object)
    instead: Optional[Tuple[int, int]] = None  # (item type, plus)


PLAIN = (BONE_SHORT_SWORD, OBSIDIAN_SHORT_SWORD, BONE_AXE, OBSIDIAN_AXE, OBSIDIAN_MACE)
# (the objects: the people of each name in the region, as SEGOBJEX and the region's ETAB have them)
GIFTS: Tuple[Gift, ...] = (
    # (the great axes in every material, a warrior's starting one being bone, and bone breaks:
    # bone ones on every Wild Mul too. The game's shop shows a seller's first 34 items: Kalzith,
    # given 42, showed 34 and none of the 8 oldest; these sellers have 29, 31 and 20)
    Gift("Weapon Merchant", tuple(weapon(w) for w in PLAIN + (METAL_SHORT_SWORD, BONE_GREAT_AXE, OBSIDIAN_GREAT_AXE,
                                                              METAL_GREAT_AXE, METAL_PICK, BONE_DAGGER)), (285,), 0x0B),
    Gift("Jark", tuple(weapon(w) for w in (BONE_SHORT_SWORD, OBSIDIAN_SHORT_SWORD, BONE_AXE, OBSIDIAN_MACE,
                                           BONE_GREAT_AXE, OBSIDIAN_GREAT_AXE, BONE_DAGGER)), (106,), 0x1A),
    Gift("Merzol", (weapon(OBSIDIAN_AXE),), (180,), 0x29),  # the slave pens' gladiator
    Gift("Chaero", (weapon(OBSIDIAN_SHORT_SWORD),), (41,), 0x1D),
    Gift("Tari", (weapon(OBSIDIAN_MACE),), (60, 243), 0x28),  # the warrens' Tari, every one
    Gift("Renegade", (weapon(BONE_SHORT_SWORD),), (289,)),  # (every one)
    Gift("Wild Mul", (weapon(BONE_AXE), weapon(BONE_GREAT_AXE)), (290,)),
    # the defilers (both kinds, made by scripts) carried nothing, so left no body: a dagger each,
    # one kind obsidian (the game's plain one), the other bone
    Gift("Defiler", (weapon(weaponchoice.PLAIN[KIND("dagger")]),), (258,)),
    Gift("Defiler", (weapon(BONE_DAGGER),), (296,)),
    # the metal ones, on people who fight with the like
    Gift("Tobrian", (weapon(METAL_DAGGER),), (104,), 0x1A),  # (a stone dagger)
    Gift("Templar", (weapon(METAL_MACE),), (131,), 0x14),  # the slavers' camp's (a bone mace)
    Gift("Castle Guard", (weapon(METAL_POLEARM),), (55,), 0x1C, clone=(121, 2560)),  # (one of six)
)
CHAYAS_CHEST = 2249  # (her script's)
WEAPON_RACK, PENS, PENS_RACK = 1647, 0x29, 131  # (the slave pens' rack: its region, its entity)
DAGOLAR, BALKAZAR = 26, 14  # (Dagolar: the one with Dag's Dagger, object 26; his double is 27)
MAGIC: Tuple[Gift, ...] = (
    Gift("Bowyer", (weapon(*STAFF_SLING_1), weapon(*BOW_1)), (283,), 0x0B),
    Gift("Undermt Folk", (weapon(*PICK_1),), (51,), 0x1E, clone=(169, 2561)),  # (one of the four miners)
    Gift("Churrr", (weapon(*CLUB_1),), (9,), 0x28),  # (the warrens' fighter, with his club)
    Gift("Arant", (weapon(*SHORT_SWORD_2),), (22,), 0x04),  # (the gladiators' captor, Silt Sea Summoning)
    # bracers of defense on the wizards
    Gift("Mikquetzl", (bracers(6),), (10,), 0x28),
    Gift("Wyrmias", (bracers(5),), (32,), 0x03),
    Gift("Balkazar", (bracers(4),), (BALKAZAR,), 0x0D),
    Gift("Dagolar", (bracers(2),), (DAGOLAR,)),
    # the circlet sold by Kel (the game's magic items' merchant), the crown worn by Keldar
    # (with the Veiled Robe, robes.py: the Ashen Robe is Kalzith's, kalzith.py)
    Gift("Kel", (ARROWBANE_ITEM, VEILED_ROBE), (107,), 0x1A),
    Gift("Keldar", (CROWN_ITEM,), (28,), 0x27),
    # the Warden's Plate, scattered: the helm on Dagolar (a boss's body, early on), the arms in the
    # Lower Castle's treasure chest (object 1360, with Dark Flame: behind the barrier the Serpent
    # Boots show, the vrock near), the legs in the Gemfields' chest (object 1065), the chest on
    # Balkazar (the hardest kill, after his mirror)
    Gift("Dagolar", (WARDENS_PLATE[3],), (DAGOLAR,)),
    Gift("Treasure chest", (WARDENS_PLATE[1],), (DARK_FLAME_CHEST,), 0x1D),
    Gift("Gemfields chest", (WARDENS_PLATE[2],), (GEMFIELDS_CHEST,), 0x08),
    Gift("Balkazar", (WARDENS_PLATE[0],), (BALKAZAR,), 0x0D),
    # the Boots of Elvenkind in the caravan's buried chest (made by the dig's script); the cloak
    # is the Elven Leader's gift (his script: elvenleader.py)
    Gift("Buried chest", (ELVEN_BOOTS,), (CARAVAN_CHEST,), 0x1A),
    # the Flame Blade on the Hot Springs' Templar
    Gift("Templar", (FLAME_BLADE,), (34,), 0x23),
    # the axes: Drakejaw on one of the Magera guarding the wagon's prisoners (five of them there, with
    # four more elsewhere, share an object), Glasshewer on the elven slavers' Templar (with his Chain
    # Arm Armor), Headsman in the arena Announcer's stash
    Gift("Magera", (weapon(*BONE_AXE_1),), (71,), 0x08, clone=(122, 2562)),
    Gift("Templar", (weapon(*OBSIDIAN_AXE_2),), (131,), 0x14),
    Gift("Announcer", (weapon(*GREAT_AXE_2),), (91,)),
    # Galefang on the Rogue Shaman (with his Shaman Followers), Mindshard on Maris (carrying psionic
    # scrolls), Stillwater in the chest Chaya gives as her apology (its object made by her script,
    # with the Sling +2, the Grapes of Bless and the obelisk's gem), Linebreaker on the Troop
    # Leader, Thornwall on the slave pens' weapon rack, in place of one of its two bone polearms
    # (the Lower Castle's rack is the same object: the pens' one gets its own)
    Gift("Rogue Shaman", (weapon(*AIR_DAGGER_2),), (77,), 0x0F),
    Gift("Maris", (weapon(*OBSIDIAN_SHORT_SWORD_1),), (228,), 0x22),
    Gift("Chaya's chest", (weapon(*BONE_SHORT_SWORD_1),), (CHAYAS_CHEST,)),
    Gift("Troop Leader", (weapon(*POLEARM_2),), (18,), 0x21),
    Gift("Weapon Rack", (weapon(*BONE_POLEARM_1),), (WEAPON_RACK,), PENS, clone=(PENS_RACK, 2563),
         instead=(BONE_POLEARM, 0)),
    # the magic shields: Gutterward on a skeleton in the warrens (its own object), Ironbulwark on
    # the Guardian of Balkazar's fortress
    Gift("Skeleton", (WOODEN_SHIELD_1,), (SKELETON,), WARRENS, clone=(WARRENS_SKELETON, 2585)),
    Gift("Guardian", (METAL_SHIELD_3,), (GUARDIAN,), BALKAZARS),
    # Nightsliver on the Lava Rift's Hermit, in place of his stone dagger; Skycutter on a thri-kreen
    # hunting the Gemfields (its own object); Dunesong with Windlash at the Bowyer's (above)
    Gift("Hermit", (weapon(*OBSIDIAN_DAGGER_2),), (HERMIT,), LAVA_RIFT, instead=(STONE_DAGGER, 0)),
    Gift("Thrikreen", (weapon(*CHATKCHA_2),), (THRIKREEN,), GEMFIELDS, clone=(GEMFIELDS_KREEN, 2598)),
)
HAYNEEDLE_ITEM = weapon(*BONE_DAGGER_1)  # (Merzol's hay stash's: haystash.py)


def gythka_2(rec: bytes) -> bytes:
    out = bytearray(rec)
    out[game.ITEM_PLUS] = 2
    struct.pack_into("<H", out, weaponchoice.ITEM_VALUE, 2 * PLUS_VALUE)
    return bytes(out)


def is_gythka_1(rec: bytes) -> bool:
    return len(rec) >= game.ITEM_SIZE and struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] == game.GYTHKA_TYPE \
        and rec[game.ITEM_PLUS] == 1


def gythka_chunks(chunks, out: Dict[Tuple[str, int], bytes]) -> Dict[Tuple[str, int], bytes]:
    """The Elven Leader's Gythka +1 made +2: the one he carries, and his script's (object
    ELVEN_GYTHKA's own record, an item)."""
    changed: Dict[Tuple[str, int], bytes] = {}
    key = ("RDFF", ELVEN_LEADER)
    if key in chunks:
        changed[key] = dataitems.with_item_changed(out.get(key, chunks[key]), is_gythka_1, gythka_2)
    key = ("RDFF", ELVEN_GYTHKA)
    if key in chunks:
        recs, end = dataitems.records(out.get(key, chunks[key]))
        if recs and recs[0].kind == dataitems.ITEM and is_gythka_1(recs[0].data):
            recs[0] = recs[0]._replace(data=gythka_2(recs[0].data))
            changed[key] = dataitems.chunk(recs, end)
    return {k: v for k, v in changed.items() if v != chunks[k]}
ELVEN_CLOAK_OBJECT = 2546  # (its picture's object: the item the Elven Leader's script makes)
# the header numbers of the Loader's own item types: the game's item they're made from
BASE_TYPES = {game.SHORT_SWORD_TYPE: 63, game.CLOAK_TYPE: 65, game.BONE_HELM_TYPE: 5, game.BONE_SHORT_SWORD_TYPE: 81,
              game.BONE_AXE_TYPE: 22, game.OBSIDIAN_SHORT_SWORD_TYPE: 45, game.OBSIDIAN_AXE_TYPE: 22,
              game.METAL_SHORT_SWORD_TYPE: 63, game.BRACERS_TYPE: 7, game.METAL_DAGGER_TYPE: 33,
              game.METAL_MACE_TYPE: 20, game.METAL_GREAT_AXE_TYPE: 2, game.METAL_PICK_TYPE: 112,
              game.METAL_POLEARM_TYPE: 19, game.CIRCLET_TYPE: 36, game.CROWN_TYPE: 36, game.PLATE_CHEST_TYPE: 57,
              game.PLATE_ARMS_TYPE: 58, game.PLATE_LEGS_TYPE: 59, game.ELVEN_CLOAK_TYPE: 65, game.ELVEN_BOOTS_TYPE: 68,
              game.AIR_DAGGER_TYPE: 33, game.BONE_GREAT_AXE_TYPE: 2, game.OBSIDIAN_GREAT_AXE_TYPE: 2,
              game.BONE_DAGGER_TYPE: 17, game.ROBE_TYPE: 65, game.METAL_SHIELD_TYPE: 4}


def header_numbers(chunks) -> Dict[int, int]:
    out = dataitems.numbers(chunks)
    for kind, base in BASE_TYPES.items():
        if base in out:
            out.setdefault(kind, out[base])
    return out


def object_chunks(chunks, gifts: Sequence[Gift], extra: Sequence[Tuple[int, Sequence[bytes]]] = ()) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX: the objects of GIFTS (and EXTRA: (object, items)) with
    their items, each clone a new object (its OJFF and its RDFF, renumbered), with them."""
    numbers = header_numbers(chunks)
    wanted: Dict[int, List[bytes]] = {}
    out: Dict[Tuple[str, int], bytes] = {}

    def given(base: bytes, gift: Gift) -> bytes:
        if not gift.instead:
            return dataitems.with_items(base, gift.items, numbers)
        kind, plus = gift.instead
        return dataitems.with_item_replaced(base, lambda r: struct.unpack_from("<H", r, game.ITEM_TYPE)[0] == kind
                                            and r[game.ITEM_PLUS] == plus, gift.items[0], numbers)
    for gift in gifts:
        for obj in gift.objects:
            if gift.clone:
                new = gift.clone[1]
                if ("OJFF", obj) not in chunks or ("RDFF", obj) not in chunks:
                    continue
                out[("OJFF", new)] = chunks[("OJFF", obj)]
                base = out.get(("RDFF", new), dataitems.renumbered(chunks[("RDFF", obj)], new))
                out[("RDFF", new)] = given(base, gift)
            elif gift.instead:
                if ("RDFF", obj) in chunks:
                    out[("RDFF", obj)] = given(out.get(("RDFF", obj), chunks[("RDFF", obj)]), gift)
            else:
                wanted.setdefault(obj, []).extend(gift.items)
    for obj, items in extra:
        wanted.setdefault(obj, []).extend(items)
    for obj, items in wanted.items():
        if ("RDFF", obj) in chunks:
            out[("RDFF", obj)] = dataitems.with_items(chunks[("RDFF", obj)], items, numbers)
    return out


def data_chunks(chunks, on: Dict[str, bool]) -> Dict[Tuple[str, int], bytes]:
    """The objects with the new items of the content switched ON (on unless False): the plain
    weapons (world_gear), the magic ones and the rest (world_magic: with the cloak's own object,
    for the Elven Leader's script), the slave pens' people's and the bone scale set (pens_gear:
    the set with the chest piece in the pens' chest), Kreenfang and Shadowseeker (magic_arms)."""
    from . import arms, bonescale, npcitems
    gifts: List[Gift] = []
    extra: List[Tuple[int, Sequence[bytes]]] = []
    if on.get("world_gear", True) is not False:
        gifts += GIFTS
    if on.get("world_magic", True) is not False:
        gifts += MAGIC
    magic_arms = on.get("magic_arms", True) is not False
    if on.get("pens_gear", True) is not False:
        extra.append((bonescale.CHEST_OBJECT, bonescale.PIECES))
        extra += npcitems.pens(magic_arms)
    try:
        out = object_chunks(chunks, gifts, extra)
        if magic_arms:
            out.update(arms.kreenfang_chunks(chunks))
    except (ValueError, struct.error):
        return {}
    if on.get("world_magic", True) is not False:
        out[("RDFF", ELVEN_CLOAK_OBJECT)] = dataitems.item_object(ELVEN_CLOAK, header_numbers(chunks).get(65, 0))
        out[("RDFF", HAYNEEDLE_OBJECT)] = dataitems.item_object(
            HAYNEEDLE_ITEM, header_numbers(chunks).get(game.BONE_DAGGER_TYPE, 0))
        out.update(gythka_chunks(chunks, out))
        from . import tome  # (the Tome of Understanding, Father Garyn's gift: garyn.py)
        try:
            out.update(tome.object_chunks(chunks, header_numbers(chunks).get(tome.SCROLL_TYPE, 0)))
        except KeyError:
            pass  # (a number of its taken in this copy of the game: no tome)
    return out


def region_chunks(region: int, rgn: Dict[Tuple[str, int], bytes], gifts: Sequence[Gift]) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of a region's file (RGNxx.GFF, its chunks RGN): its entity table
    with each of GIFTS' clones there pointed to its new object."""
    key = ("ETAB", region)
    if key not in rgn:
        return {}
    etab = rgn[key]
    for gift in gifts:
        if gift.clone and gift.region == region:
            etab = dataitems.with_entity_object(etab, gift.clone[0], gift.clone[1], gift.objects[0])
    return {key: etab} if etab != rgn[key] else {}


def region_file(region: int) -> str:
    return f"RGN{region:02X}.GFF"


def write_region(source: str, dest: str, region: int, gifts: Sequence[Gift]) -> None:
    """The game's region file (SOURCE, only read) with GIFTS' clones in it, to DEST."""
    import os
    from .gff import read_gff
    from .icons import with_chunks
    with open(source, "rb") as f:
        data = f.read()
    out = with_chunks(data, region_chunks(region, read_gff(data), gifts))
    tmp = dest + ".tmp"
    with open(tmp, "wb") as f:
        f.write(out)
    os.replace(tmp, dest)


def regions(gifts: Sequence[Gift]) -> List[int]:
    """The regions whose files the Loader copies (for a clone)."""
    return sorted({g.region for g in gifts if g.clone and g.region is not None})
