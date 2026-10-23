"""Where Shattered Lands (GOG release, DSUN.EXE) keeps things in memory.

The game is a 16-bit Borland C++ program. Its data segment (DS) starts with
Borland's copyright string at DS:0004, which makes DS easy to find; the
creature and character-sheet tables are reached through far pointers in DS.

Other data lives in segments at fixed distances from the load segment (DS -
0x4356). The game's overlaid code names these segments with different
numbers; the real ones are given here.
"""

import re
import string
import struct
from typing import Dict, List, NamedTuple, Optional, Tuple

from .guestmem import GuestMemory

CONVENTIONAL_AND_UPPER = 0x110000  # real-mode programs live below this

BORLAND_SIG = b"Borland C++ - Copyright 1991 Borland Intl."
BORLAND_SIG_OFFSET = 4  # the string's offset in DS
DGROUP = 0x4356  # DS relative to the load segment

CREATURES_PTR = 0x1665  # DS offset of a far pointer to the creature table
SHEETS_PTR = 0x1661  # DS offset of a far pointer to the character sheet table
ITEMS_PTR = 0x165D  # far pointer to the item table (21-byte records)
ITEM_TYPES_PTR = 0x1669  # far pointer to the item type table (20-byte records)
ITEM_NAMES_PTR = 0x166D  # far pointer to the item names (GPLDATA's NAME list, 25 bytes each)
DEX_AC = 0x07F6  # DS: AC adjustment for each DEX score (bytes)
DEX_INITIATIVE = 0x07DC  # DS: initiative adjustment for each DEX score (bytes)
DIFFICULTY = 0x11AE  # DS word: game difficulty (monsters get difficulty-1 to hit)
EFFECT_COUNT = 0x1E24  # DS word: number of active effects
SPELL_NAMES = 0x254E  # DS offset of the NUL-separated spell and psionic names
SPELL_NAMES_END = 0x2F00

CREATURE_SIZE = 0x3A
THINGS = 520  # the game's things (map entries; a fight's combatants are among them)
SHEET_SIZE = 0x47
ITEM_SIZE = 0x15
ITEM_TYPE_SIZE = 0x14
CREATURE_SHEET_INDEX = 0x04
CREATURE_PSP = 0x02  # word: PSP now
CREATURE_THAC0 = 0x1F
CREATURE_SIDE = 0x1D  # creatures on the same side share this value
CREATURE_ABILITIES = 0x22
CREATURE_NAME = 0x28
# +1Ch: the character's condition, as the party screen shows it (the game shows the most
# important active effect instead of "Okay")
CREATURE_STATUS = 0x1C
OUT_COLD = 3
STATUS_NAMES = {0: "New", 1: "Okay", 2: "Stunned", 3: "Out Cold", 4: "Dying", 5: "Dead", 6: "Animated",
                7: "Petrified", 8: "Gone"}
PARTY_SIZE = 4  # the party are the first creatures in the table

# Segments relative to the load segment
COMBATANTS_SEG, COMBATANTS_OFF = 0x3972, 0xC36  # 3 bytes per combatant: kind (2 = creature), creature index
# The same table holds every object the game tracks ("things": kind 1 an item, 2 a creature).
# A creature's items: three lists, each starting at an object number in the creature's record;
# each item names the next by item number (9999 ends the list). An item's slot is where it is
# worn (the game's own slot names, in this order), 255 if only carried.
THING_ITEM = 1
CREATURE_ITEM_LISTS = (0x08, 0x0A, 0x0C)  # (+0Ch: where the game puts items handed to a character)
ITEM_NEXT, ITEM_SLOT, ITEM_TYPE, ITEM_NAME, ITEM_PLUS = 0x04, 0x11, 0x0A, 0x12, 0x14
ITEM_POWER = 0x0F  # an item's magical power (0: none; the game's weapon breaking and acid read it)
NO_ITEM = 9999
# (as the inventory screen shows them: a ring on each hand, 4 and 11; the cloak 12, the feet 13)
EQUIP_SLOTS = ("arm", "ammo", "missile", "right hand", "finger", "waist", "legs", "head", "neck", "chest",
               "left hand", "finger", "cloak", "foot")
FINGERS = tuple(n for n, s in enumerate(EQUIP_SLOTS) if s == "finger")
FINGER = FINGERS[0]
FOOT = EQUIP_SLOTS.index("foot")
CLOAK_SLOT = EQUIP_SLOTS.index("cloak")
# armour, as RULE_PROTECTION weighs it: a piece worn on the arms, legs, head or chest that counts
# for AC (its type's +0Fh bit 80h); a shield, a type whose flags word (+00h) has bit 4 (the
# flag the game's AC routine reads for one), held in a hand
ARMOUR_SLOTS = tuple(EQUIP_SLOTS.index(s) for s in ("arm", "legs", "head", "chest"))
TYPE_SHIELD = 4
# The plain "Ring" item type. With the dice log's patched game, a worn one's plus betters AC
# and saving throws (DSCLOG's PROBE_RING_AC and PROBE_RING_SAVE); the game has no such ring of
# its own, and the Loader can put a Ring +1 in the arena (ring.py).
RING_TYPE = 102
# Item types of the Loader's own, which DSCLOG adds after the game's 115 (npcitems.py): a
# metal short sword, and a cloak of protection, whose plus counts for AC and, worn (CLOAK),
# on saves as a ring's does
GAME_TYPES = 115
SHORT_SWORD_TYPE, CLOAK_TYPE, BONE_HELM_TYPE = GAME_TYPES, GAME_TYPES + 1, GAME_TYPES + 2
BONE_SHORT_SWORD_TYPE, BONE_AXE_TYPE = GAME_TYPES + 3, GAME_TYPES + 4  # (a new warrior's, weaponchoice.py)
OBSIDIAN_SHORT_SWORD_TYPE, OBSIDIAN_AXE_TYPE = GAME_TYPES + 5, GAME_TYPES + 6
METAL_SHORT_SWORD_TYPE = GAME_TYPES + 7  # a plain one (Kurzak's type is his alone: Shadowseeker)
BRACERS_TYPE = GAME_TYPES + 8  # bracers of defense: worn on the arms, their plus counting for AC
# metal versions of the game's plain weapons that have none (worldgear.py)
METAL_DAGGER_TYPE, METAL_MACE_TYPE, METAL_GREAT_AXE_TYPE = GAME_TYPES + 9, GAME_TYPES + 10, GAME_TYPES + 11
METAL_PICK_TYPE, METAL_POLEARM_TYPE = GAME_TYPES + 12, GAME_TYPES + 13
CIRCLET_TYPE, CROWN_TYPE = GAME_TYPES + 14, GAME_TYPES + 15  # worn on the head, not armour (worldgear.py)
# plate mail's chest, arm and leg armour (worldgear.py's Warden's Plate): AC 3, 2, 2
PLATE_CHEST_TYPE, PLATE_ARMS_TYPE, PLATE_LEGS_TYPE = GAME_TYPES + 16, GAME_TYPES + 17, GAME_TYPES + 18
# the Cloak and Boots of Elvenkind (worldgear.py; their stealth: stealth.py)
ELVEN_CLOAK_TYPE, ELVEN_BOOTS_TYPE = GAME_TYPES + 19, GAME_TYPES + 20
AIR_DAGGER_TYPE = GAME_TYPES + 21  # a metal dagger air clerics may use (worldgear.py's Galefang)
BONE_GREAT_AXE_TYPE, OBSIDIAN_GREAT_AXE_TYPE = GAME_TYPES + 22, GAME_TYPES + 23  # (a new warrior's, weaponchoice.py)
BONE_DAGGER_TYPE = GAME_TYPES + 24  # (a water cleric's dagger: weaponchoice.py)
ROBE_TYPE = GAME_TYPES + 25  # the robes (robes.py): worn on the chest, not armour
METAL_SHIELD_TYPE = GAME_TYPES + 26  # a metal shield (worldgear.py's Ironbulwark): the game has none
# the Girdle of Back Defense, the Golden Girdle of Urnst and the Amulet of Magic Resistance (worldgear.py)
BACK_GIRDLE_TYPE, URNST_GIRDLE_TYPE, MR_AMULET_TYPE = GAME_TYPES + 27, GAME_TYPES + 28, GAME_TYPES + 29
GYTHKA_TYPE = 0x2C  # the game's gythka ("2 handed Bone Gythka")
# The Loader's rule changes (DSCLOG's RULES): helms count AC 1; AD&D's two-weapon penalties;
# spells saved against with the spell save; no doubled d20 (2, once boots' movement, is unused)
RULE_HELMS, RULE_TWO_WEAPONS, RULE_SPELL_SAVE, RULE_NO_DOUBLE = 1, 4, 8, 16
RULE_NEW_SPELLS = 32  # the new wizard spells (NEW_SPELLS)
RULE_STEALTH = 64  # a thief hiding in shadows and moving silently backstabs (stealth.py)
RULE_LEVEL_10 = 128  # an XP cap (XP_CAP, shared out) in place of the game's level cap of 9
XP_CAP = 749_999  # DSCLOG's XP_CAP
RULE_THIEF_TABLE = 256  # thief skills from AD&D's table and Dark Sun's DEX adjustments
RULE_HALF_GIANT = 512  # half-giants wield two-handed weapons in one hand
# AD&D's rings and cloaks of protection: of two rings only the better counts, and a ring betters
# AC only without magical armour; a cloak counts only without magical armour, metal armour or a
# shield (DSCLOG's PROBE_RING_AC and RING_PLUS)
RULE_PROTECTION = 1024
# Items saving against acid (DSCLOG's PROBE_ITEM_*): a weapon or armour the game's acid or
# corroding touch would destroy needs the easier of the game's number and AD&D's save for
# its material (ACID_SAVES), less its plus and 1 more for a magical power
RULE_ITEM_SAVES = 2048
# Weapon specialization (specialize.py; DSCLOG's PROBE_ATTACKS): the kinds a warrior chose, kind + 1
# each in the sheet's SPEC_SLOTS bytes (four the game never uses), set the attacks a round
RULE_SPECIALIZE = 4096
RULE_RESTRICT = 8192  # class restrictions on armour, shields and weapons (restrict.py)
RULE_MULTI_HP = 16384  # multiclass hit points as in AD&D: each level's die and CON's bonus shared
RULE_HP_BEST = 32768  # a hit die rolled twice, the better kept (DSCLOG's PROBE_HP_BEST)
RULE_KITS = 65536  # kits for characters of one class (kitpages.py; DSCLOG's second rules word)
# a ranger's spells' durations and damage at its level less 7, as the spell levels it may cast are
# (the game takes the whole level: DSCLOG's PROBE_RANGER_LEVEL, kits.spell_class_level)
RULE_RANGER_CAST = 131072
# INT's chance to learn a scroll's spell and the most spells a level a preserver may know
# (intlearn.py; DSCLOG's INT_LEARN)
RULE_INT_LEARN = 262144
# AD&D's class tables (tables.py; DSCLOG's RULE_HI_TABLES): the XP each class needs, priests'
# THAC0, and clerics', druids' and preservers' spell slots by level
RULE_ADND_TABLES = 524288
RULE_CHA_PRICES = 1048576
# creation's scores and hit points as rolled (DSCLOG's RULE_HI_ROLLED, RL_*): a score raised only while
# the six add up to no more than the die gave, the hit points not changed by a click
RULE_ROLLED = 2097152
# magical items sold to a merchant kept in its pack, to buy back (buyback.py; DSCLOG's RULE_HI_BUYBACK)
RULE_BUYBACK = 4194304
# a backstab multiplies the weapon's dice only, STR and the rest added after (the PHB; DSCLOG's
# RULE_HI_BACKSTAB, STAB_TIMES); else the game's, the whole damage multiplied
RULE_BACKSTAB = 8388608
SPEC_SLOTS, SPEC_COUNT = 0x14, 4
# AD&D's item saving throws against acid (the DMG's table), by the game's materials: wood
# (thick), bone, stone and obsidian (glass's), metal, leather; and cloth for no material
ACID_SAVES = {0: ("wood", 8), 1: ("bone", 11), 2: ("stone", 5), 3: ("obsidian", 5), 4: ("metal", 13),
              5: ("leather", 10), 6: ("cloth", 12)}
# the game's attacks that destroy items, as the dice log names them
ACID, TOUCH_ARMOUR, TOUCH_WEAPON = 178, 186, 187
ITEM_ATTACKS = {ACID: "acid", TOUCH_ARMOUR: "corroding touch", TOUCH_WEAPON: "corroding touch"}
# the powers a monster's hit casts for its poison properties (monsters.SPECIAL_ATTACKS: bits 13 and
# 14, the routine giving a hit's special effects, DSUN.EXE 7A776h)
POISON_POWERS = {176: "Poison (10 damage)", 177: "Poison (30 damage)"}
# a monster's power the game has no name for, named by the effect its record puts on (+19h)
POWER_EFFECT_NAMES = {34: "Paralysing attack", 13: "Disease attack", 51: "Entangling attack",
                      35: "Poison attack"}
POWER_KIND_NAMES = {"pointed": "piercing", "edged": "slashing"}  # (else the damage kind's own name)
# the Options' setting for each, all on unless unticked
RULE_SETTINGS = (("helm_ac", RULE_HELMS), ("two_weapons", RULE_TWO_WEAPONS),
                 ("spell_save", RULE_SPELL_SAVE), ("no_doubled_save", RULE_NO_DOUBLE),
                 ("new_spells", RULE_NEW_SPELLS), ("stealth", RULE_STEALTH), ("level_10", RULE_LEVEL_10),
                 ("thief_table", RULE_THIEF_TABLE), ("half_giant_hands", RULE_HALF_GIANT),
                 ("protection_rules", RULE_PROTECTION), ("item_saves", RULE_ITEM_SAVES),
                 ("weapon_specialization", RULE_SPECIALIZE), ("class_restrictions", RULE_RESTRICT),
                 ("multiclass_hp", RULE_MULTI_HP), ("best_hit_die", RULE_HP_BEST), ("kits", RULE_KITS),
                 ("ranger_casting_level", RULE_RANGER_CAST), ("int_learning", RULE_INT_LEARN),
                 ("adnd_tables", RULE_ADND_TABLES), ("cha_prices", RULE_CHA_PRICES),
                 ("rolled_scores", RULE_ROLLED), ("buyback", RULE_BUYBACK),
                 ("backstab_dice", RULE_BACKSTAB))
# The new spells (RULE_NEW_SPELLS; DSCLOG's NEW SPELLS): six wizard spells numbered after the game's
# 196 (0-195), in records past its own (the 200h bytes after them, two small tables, moved into
# DSCLOG at the game's start: its SEG_MOVE, SEGMENT_TABLE here); DSCLOG fills their records and rows
# in, names them, and keeps who knows them in the sheet (NEW_KNOWN's bits).
# Cat's Grace works as Strength does, for DEX: Strength's code rolls 1d6 into an effect of its own
# (54, a number the game leaves unused) that adds to DEX, at most 24. Erdlu Claw's effect (6, unused
# too) makes each natural (unarmed) attack 1d6+1 where that is better than its own (NS_CLAW), +1 to hit and at least
# a +1 weapon (NS_FIST: its hit's damage kinds get PLUS1); Fogbolt's (27) takes 3 off the fogged creature's attacks and
# gives 2 to attacks on it. Reflected Image is Mirror Image's record with one image (its effect, 25,
# the game's Mirror Images: one takes the other's place); Spook is Charm Person's with the game's
# Afraid (17) for 3 rounds, its save 1 worse for each 2 caster levels (up to 6: SPOOK_MOST); Friends
# goes through Strength's code as Cat's Grace does, rolling 2d4 into an effect of its own (74, unused
# too) that adds to CHA (at most 25) for 1d4 rounds and 1 a level.
GRACE_SPELL, CLAW_SPELL, FOG_SPELL, REFLECT_SPELL, SPOOK_SPELL, FRIENDS_SPELL = range(196, 202)
NEW_SPELLS = {GRACE_SPELL: "Cat's Grace", CLAW_SPELL: "Erdlu Claw", FOG_SPELL: "Fogbolt",
              REFLECT_SPELL: "Reflected Image", SPOOK_SPELL: "Spook", FRIENDS_SPELL: "Friends"}
NEW_SPELL_LEVELS = {GRACE_SPELL: 2, CLAW_SPELL: 1, FOG_SPELL: 1, REFLECT_SPELL: 1, SPOOK_SPELL: 1,
                    FRIENDS_SPELL: 1}
# ... and nine 6th-level priest spells after them (DSCLOG's PRIEST6 on): Wake of the Ravager's eight
# and Whirlwind, the air's. A priest casts those of its spheres, as the game's own: their rows' masks
# (PRIEST6_MASKS: the cosmos's as its 4th- and 5th-level spells', the druids'; the elements' as
# theirs), meeting its priest classes' (DSCLOG's NS_PRIEST_KNOWS; the sheet holds no bit for them)
HEAL_SPELL, HARM_SPELL, BLADE_SPELL, THORNS_SPELL, SUNSTROKE_SPELL = range(202, 207)
SEEDS_SPELL, HEARTSEEKER_SPELL, WATER_LIFE_SPELL, WHIRLWIND_SPELL = range(207, 211)
PRIEST6_SPELLS = {HEAL_SPELL: "Heal", HARM_SPELL: "Harm", BLADE_SPELL: "Blade Barrier",
                  THORNS_SPELL: "Wall of Thorns", SUNSTROKE_SPELL: "Sunstroke", SEEDS_SPELL: "Fire Seeds",
                  HEARTSEEKER_SPELL: "Heartseeker", WATER_LIFE_SPELL: "Water of Life", WHIRLWIND_SPELL: "Whirlwind"}
COSMOS_MASK, FIRE_MASK, EARTH_MASK, AIR_MASK = 0x001003C2, 0x00110112, 0x0010808A, 0x00104046
PRIEST6_MASKS = {HEAL_SPELL: COSMOS_MASK, HARM_SPELL: COSMOS_MASK, BLADE_SPELL: AIR_MASK,
                 THORNS_SPELL: EARTH_MASK, SUNSTROKE_SPELL: FIRE_MASK, SEEDS_SPELL: FIRE_MASK,
                 HEARTSEEKER_SPELL: 0x001282AA, WATER_LIFE_SPELL: 0x00120222, WHIRLWIND_SPELL: AIR_MASK}
PRIEST6_LEVEL = 6
NEW_SPELLS_END = 211  # (past the last)
# Negative Plane Protection's save, as the patched game makes it (DSCLOG's NS_NPP): Vampiric Touch's
# record copied to the records' room past the new spells, a save against death allowed
NPP_SAVE_RECORD = 211
STRENGTH_SPELL, GRACE_EFFECT, CLAW_EFFECT, FOG_EFFECT = 23, 54, 6, 27
MIRROR_EFFECT, AFRAID_EFFECT, FRIENDS_EFFECT = 25, 17, 74
ENLARGE_EFFECT = 16
IMAGE_CHANCE, REFLECT_CHANCE = 75, 50  # (an image taking a blow or a foe's spell: DSCLOG's)
FRIENDS_MOST, SPOOK_MOST = 25, 6
FLAMING_SPHERE = 14  # (once Cat's Grace's place)


def cast_spell(spell: Optional[int]) -> bool:
    """A wizard's or priest's spell, a psionic power, or a new spell: not a monster's power."""
    return spell is not None and (SPELL_FIRST <= spell < PSIONIC_FIRST + PSIONIC_COUNT or spell in NEW_SPELLS
                                  or spell in PRIEST6_SPELLS)
DETECT_INVISIBILITY = 13  # the spell (as the Loader numbers them: 1 Burning Hands)
# the sheet's byte and bit that say a character knows each new spell: most in +45h, whose low three
# bits are an Elementalist's second sphere (kits.SPHERE2); Friends' in the kit byte's top bit (its
# 0FFh, kitpages.KIT_OPEN, none chosen and no spell known)
NEW_KNOWN_SHEET, KIT_SHEET, KIT_OPEN_BYTE = 0x45, 0x43, 0xFF
NEW_KNOWN = {GRACE_SPELL: (NEW_KNOWN_SHEET, 0x10), CLAW_SPELL: (NEW_KNOWN_SHEET, 0x20),
             FOG_SPELL: (NEW_KNOWN_SHEET, 0x40), REFLECT_SPELL: (NEW_KNOWN_SHEET, 0x08),
             SPOOK_SPELL: (NEW_KNOWN_SHEET, 0x80), FRIENDS_SPELL: (KIT_SHEET, 0x80)}


def knows_new_spell(sheet: bytes, spell: int) -> bool:
    """Whether SHEET says it knows new spell SPELL (NEW_KNOWN)."""
    at, bit = NEW_KNOWN[spell]
    if len(sheet) <= at or at == KIT_SHEET and sheet[at] == KIT_OPEN_BYTE:
        return False
    return bool(sheet[at] & bit)
# The game's table of effects (DSUN.EXE 44CD0h, from the load segment 3F8Dh), 6 bytes each from
# effect 1: a far pointer to its name (the line under a portrait: "Hasted" for "Okay") and its
# icon (an ICON chunk of RESOURCE.GFF, as the spells' are) on the Effects screen, which shows
# only those with one. Effects 6, 27 and 54 have neither (an empty name, icon 0): DSCLOG gives the
# new spells' theirs, the spell's icon (ICON 21000 + the spell, in the Loader's RESOURCE.GFF).
EFFECT_TABLE_SEG, EFFECT_ENTRY = 0x3F8D, 6
NEW_SPELL_ICON = 21000  # + the spell
# The game turns a spell's kind of save (bits 5-7 of its +0Fh) into one of the sheet's five
# saves (1-5: paralysis/poison/death ... spell) with a table of words at DS:1E75h, read afresh
# for each save. Kind 5, what almost every spell is marked with, is petrification/polymorph
# (3); RULE_SPELL_SAVE makes it the spell save (5). Kind 1 (paralysis/poison/death: the
# clouds, Poison, Slay Living, the psionic attacks) and kind 4 (petrification/polymorph:
# three monsters' powers) stay as they are.
SAVE_KINDS = 0x1E75
KIND_TO_SAVE = (1, 1, 1, 2, 3, 3, 4, 5, 5, 5)
SPELL_KIND, SPELL_SAVE = 5, 5
# AD&D's two weapons: -2 with the main (right) hand, -4 with the off (left) hand, the DEX
# reaction adjustment (the game's initiative table, the same numbers) added and no better than
# 0; rangers have none
TWO_WEAPON_PENALTY = {3: -2, 10: -4}


# A spell's category word (its rules' +01h, the record's +11h; WIS counts against 0x1E, ...):
# with bit 40h set, the game's saving throw adds the target's DEX defensive adjustment (its
# DEX AC table, sign flipped: +4 at DEX 18, -4 at DEX 3), AD&D's rule for attacks that can be
# dodged. The game marks no spell so; with RULE_NO_DOUBLE the Loader marks the fire, cold and
# electricity spells (DOUBLED_KINDS), in place of the doubled d20 (set_dodge).
CATEGORY_DODGE = 0x40
DOUBLED_FLAGS = 0x86


# settings kept under an earlier name (the new spells' switch was Cat's Grace's alone)
OLD_SETTING_NAMES = {"new_spells": "cats_grace"}


def rules_from_settings(settings: dict) -> int:
    return sum(bit for key, bit in RULE_SETTINGS
               if settings.get(key, settings.get(OLD_SETTING_NAMES.get(key, key), True)))


def kind_to_save(kind: int, rules: int) -> int:
    if kind == SPELL_KIND and rules & RULE_SPELL_SAVE:
        return SPELL_SAVE
    return KIND_TO_SAVE[kind]


# The rules in force (DiceLog.set_rules): GameData objects made without rules of their own use these
RULES_IN_FORCE = 0
# ... and whether a worn belt adds BELT_BONUS to picking pockets and opening locks (the Options tab's
# cloak, boots and belt switch; DSCLOG adds it where the game works the chance out: PROBE_BELT)
BELT_IN_FORCE = False
BELT_BONUS, BELT_SKILLS, WAIST = 5, (0, 1), 5  # (the skills' numbers in THIEF_SKILLS; the slot)
EFFECTS_SEG, EFFECTS_OFF = 0x3BF6, 0x106  # 10 bytes per active effect
# The game's clock and event queue: a far pointer to the time (a dword, divided by the byte at
# GAME_TIME_SCALE); the first queue's entries (17 bytes: due time, kind, then the event's data),
# sorted by time, with their count. An effect ending is kind 7, its data the owner and handle.
GAME_TIME_PTR, GAME_TIME_SCALE = 0x9B72, 0x9B70
WHOSE_TURN = 0x4979  # DS word: the combatant whose turn it is (outside a fight: the leader)
# DS word: 1 while the party is in a fight. The routine that starts a fight sets it (DSUN.EXE
# 1DD8Bh, unless it is already 1); the one that ends it clears it (1DFE8h)
IN_COMBAT = 0x1168
# ... though it stays 1 while the party walks spread out (uncollapsed) with no one to fight. The
# game's own test for a fight (its rest's "NO RESTING DURING COMBAT", the USE screen's buttons;
# DSCLOG's PP_FIGHTING) is the word at +19h of the fight's state, a segment this far below DS
FIGHT_STATE_FROM_DS, FIGHT_STATE_ON = 0x4356 - 0x377E, 0x19
REGION = 0x117C  # DS word: the region the party is in
POSITIONS = 0x669D  # DS: each map object's x, y (in 16ths of a square), 32 bytes apart; the party's leader is object 0
# The party's money, in ceramic pieces (the inventory screen's bottom bar): a dword the game's
# script command for giving money (0Ch) adds to
MONEY_SEG, MONEY = 0x3781, 0x357
# The game's global flags (its scripts' 13h/8Dh variables): bits, flag n bit n % 8 of byte n // 8,
# at the far pointer here (a save keeps them: SAVE chunk 29)
FLAGS_PTR = 0x1352
# The game's global numbers (its scripts' 07h/87h variables): words, at the far pointer here
NUMBERS_PTR = 0x1356
ARENA_FIGHTS = 12  # the number counting the party's trips to the arena (scripts 2 and 3)
# Speakers the game names in its own text (the dialogue window shows only a portrait):
# 119 is asked about as "Yell something back at the Announcer?"
SPEAKERS = {119: "The Announcer"}
# The object a script was started on, e.g. the person clicked to talk to (a combatant number):
# the game's script trigger (DSUN.EXE 9520h) puts it here before running the script.
TALK_SEG, TALK_TARGET = 0x3781, 0x365
# The dialogue window's replies: the game copies each into DS:5537 + n * 33h; the row the
# player clicks goes in DS:1F0A (FFh until then), plus the list's scroll position at DS:5502
REPLY_CHOSEN, REPLY_SCROLL, REPLY_TEXTS, REPLY_SIZE = 0x1F0A, 0x5502, 0x5537, 0x33
EVENT_QUEUE, EVENT_COUNT, EVENT_SIZE, EVENT_EFFECT_ENDS = 0x2FBE, 0x2FC6, 0x11, 7
# Each round, per creature (4 bytes each): the initiative score (-1 once it has
# acted) and the 0-199 roll that breaks ties
INITIATIVE_SEG, INITIATIVE_OFF = 0x37BD, 0xD9
# Wizard and cleric spells, 7 bytes each from id 1: level, ..., DS offset of the name (+5)
SPELL_INFO_OFF, SPELL_INFO_SIZE, SPELL_COUNT = 0x3FD33, 7, 137
SPELL_FIRST = 0  # Armor, the first wizard spell: spells are 0 to SPELL_COUNT (Old One-Eye's scroll is 0's)
# Psionic powers are numbered after the spells (Detonate 138 ... Thought Shield 171) and share
# the spells' records and casting code; higher numbers are monsters' own powers
PSIONIC_FIRST, PSIONIC_COUNT = 138, 34
# The spells' rules, 32 bytes each; the saving throw reads a flags word at +0Ah
# (0x86: the d20 is doubled) and a byte at +0Fh (bits 1-4: a save modifier,
# bits 5-7: the kind of save)
SPELLS_SEG, SPELLS_OFF, SPELL_SIZE = 0x3CB4, 0x40, 0x20
SPELL_LEVELS_SEG, SPELL_LEVELS_OFF = 0x3FB9, 0x19C  # each spell's level, 7 bytes a spell (DSCLOG's SPELL_LEVELS)
# The psionic powers' table, 8 bytes a power (0-33) from 3FB9h:0000h: +0 the ability its check uses
# (bits 0-2: STR, DEX, CON, INT, WIS, CHA) and the power's adjustment (bits 3-7, signed); +1 its
# PSP. And a byte a party member a power (selector 2F0h, +77h + member * 22h + power) whose bits 3-7
# are the member's own number for it: 0 not known, 1 known, more adding to the check (the game has
# code to raise and lower it, 1 to 30; nothing found to call it)
POWERS_SEG, POWER_SIZE = 0x3FB9, 8
POWER_OWN_SELECTOR, POWER_OWN_OFF, POWER_OWN_STRIDE = 0x2F0, 0x77, 0x22
SEGMENT_TABLE = 0x4137  # the game's segment table: a selector's segment at +selector (8 bytes each)
ABILITY_NAMES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
SHEET_MAGIC_RESISTANCE = 0x29
SPHERE_NAMES = ("air", "earth", "fire", "water")  # the clerics' and druids' spheres, by class order
SHEET_ATTACKS = 0x2A  # the game's attacks a round, in halves (2: 1, 3: 3/2)
SHEET_XP, SHEET_XP_VALUE, SHEET_MAX_HP = 0x00, 0x04, 0x08  # a monster's sheet holds its XP value at +4
SHEET_RACE, SHEET_ABILITIES = 0x18, 0x1B
SHEET_CLASSES, SHEET_LEVELS, SHEET_BASE_AC = 0x21, 0x24, 0x27
SHEET_HP_BASE = 0x0A  # the hit points rolled (the game divides them by the classes for the most)
SHEET_LEVELS_BEFORE = 0x3F  # the levels before any were lost (the game scales SHEET_HP_BASE by them)
# sheet +0x12: a word of flags, one bit per class the character has (druid 0x10, fighter
# 0x20, gladiator 0x40, preserver 0x80, psionicist 0x100, ranger 0x200, thief 0x400)
SHEET_FLAGS = 0x12
SHEET_FLAG_RANGER = 0x200
RACE_HALF_GIANT = 5
# Hit points per level (segment relative to the load segment): +10h + class = the class's
# group; group * 4 = (die, levels that roll it, fixed gain after that); +38h + CON = the
# least a roll counts for
LEVEL_HP_SEG = 0x40B1
LEVEL_HP_CON_BONUS = 0x52  # +52h + CON: hit points per level (a warrior's; others get at most +2)
WARRIOR_GROUP = 1  # (the hit point group of the warrior classes)
# Character creation. DS:119Ch is a far pointer to the character being made, a sheet whose
# classes (+21h) are numbered as in the creation screen's list (CREATION_CLASS_NAMES).
CREATION_SHEET_PTR = 0x119C
# Its tables (segment relative to the load segment): +14Dh + race * 6 + ability = the race's
# adjustment (signed); +180h + class * 3 = the class's prime requisite (a word: its ability
# index), then the least any other ability may be
CREATION_SEG, CREATION_RACE_OFF, CREATION_CLASS_OFF = 0x38D4, 0x14D, 0x180
CREATION_PRIME_MINIMUM = 17
ITEM_NAME_SIZE = 25
BROKEN_ITEM_TYPE = 0x6B  # what a broken weapon becomes
DETONATE_BLAST = 195  # the effect Detonate puts on its target besides the power: 1d10, no save

MATERIALS = ("Wooden", "Bone", "Stone", "Obsidian", "Metal", "Leather")
NO_MATERIAL = 0x40  # in the type's material byte, with material 0: things with none (rings, bodies)
# Dark Sun's to-hit penalty for non-magical weapons of weaker materials (from the game's code)
MATERIAL_TO_HIT = {0: -3, 1: -1, 2: -2, 3: -2}
# The character sheet's saving throws, in order (the game's own grouping: Fireball, for
# one, is saved against with petrification/polymorph)
SAVE_NAMES = {1: "paralysis/poison/death", 2: "rod/staff/wand", 3: "petrification/polymorph",
              4: "breath weapon", 5: "spell"}

# Effect ids, as the game names them (1-based, from its table in DSUN.EXE)
EFFECT_NAMES = {
    1: "Acid", 2: "Improved AC", 3: "Berserk", 4: "Biofeedback", 5: "Blink", 7: "Blessed", 8: "Blind",
    9: "Brave", 10: "Charmed", 11: "Confused", 12: "Cursed", 13: "Diseased", 14: "Detect Traps",
    15: "Detect Invis", 16: "Enlarged", 17: "Afraid", 18: "Cloak of Fear", 19: "Feeblemind",
    20: "Fire Shield", 21: "Free Action", 22: "Hasted", 23: "Invisible", 24: "Invis to Undead",
    25: "Mirror Images", 26: "Englobed", 28: "Prot Missile", 29: "Prot Paralysis",
    30: "Synaptic Static", 31: "Low Resistance", 32: "Mind Bar", 33: "Can't Attack", 34: "Paralyzed",
    35: "Poisoned", 36: "Prot Cold", 37: "Prot Energy", 38: "Prot Evil", 39: "Prot Evil 10'",
    40: "Prot Fire", 41: "Prot Lightning", 42: "Neg Plane Prot", 43: "Gaze Reflection",
    44: "Spell Turning", 45: "Save penalty", 46: "Shielded", 47: "Slowed", 48: "Stoneskin",
    49: "Graft Weapon", 50: "No spell use", 51: "Stuck", 52: "Dispelling evil", 53: "Ironskin",
    55: "Blur", 56: "Spirit Armor", 57: "Barkskin", 58: "Displacement", 59: "Flesh Armor",
    60: "Magical Vestments", 61: "Animal Affinity", 62: "Body Weaponry", 63: "Strength Enhanced",
    64: "Strength Borrowed", 65: "Strength Lent", 66: "Adrenalin Control", 67: "Strength",
    68: "Weakened", 69: "Extra Hitpoints", 70: "Flame Blade", 71: "Spirit. Hammer", 72: "Shillelagh",
    73: "Prayer", GRACE_EFFECT: "Cat's Grace", CLAW_EFFECT: "Erdlu Claw", FOG_EFFECT: "Fogbolt",
    FRIENDS_EFFECT: "Friends",
}

# What effects do, where the game's own code shows it (to-hit, AC and saving throws)
EFFECT_RULES = {
    2: "armour AC at most 6", 4: "AC -1", 7: "+1 to hit, +1 on saves", 8: "AC 4 worse",
    12: "-1 to hit", 16: "+10% melee damage per level of the spell",
    36: "+3 on saves against cold spells, half damage from them",
    38: "AC -2 and +2 on saves against evil",
    40: "+3 on saves against fire spells, half damage from them",
    41: "+4 on saves against lightning spells, half damage from them",
    45: "-1 on saves", 46: "AC 4 except from behind", 47: "-4 to hit, AC 4 worse", 49: "+1 to hit",
    52: "AC -7 against evil", 55: "attackers -2 to hit", 56: "armour AC at most 4, +3 on saves",
    57: "AC at most 6 - level/4, +1 on saves", 58: "AC -2", 59: "AC at most 10 - level",
    60: "AC 5, 1 better per 3 caster levels above 5", 63: "STR 24 (higher kept)",
    64: "STR + the amount borrowed, at most 24", 65: "STR - twice the amount lent, at least 3",
    66: "STR + 1d6, at most 24",
    67: "STR + 1d6, at most 24", 68: "STR - the amount, at least 3", GRACE_EFFECT: "DEX + 1d6, at most 24",
    CLAW_EFFECT: "each natural (unarmed) attack does 1d6+1 where that is better, +1 to hit, as a +1 magical edged weapon (talons)",
    FOG_EFFECT: "-3 to hit, and +2 to hit it (as AC 2 worse)",
    FRIENDS_EFFECT: f"CHA + 2d4, at most {FRIENDS_MOST}",
    73: "+1 to hit and saves for the caster's side, -1 for the other",
    # what the game's turn, movement, casting and damage code does with the rest
    28: "missile attacks miss it", 37: "no damage from fire, cold, electricity or magic alone",
    30: "its keeper can use no psionic powers; anyone else must beat the static to use one",
    1: "2d4 acid damage each round",
    3: "fights for a side picked at random each turn; can't cast spells",
    9: "ends fear, and the next fear fails (which ends it); +4 on saves against fear spells",
    10: "joins the caster's side, the computer controlling it",
    11: "each turn a d10: 1 runs off, 2-6 does nothing, 7-9 fights for a random side, 10 acts normally",
    17: "the computer controls it; can't attack or cast spells (undead are immune; Bravery stops it)",
    18: "whoever hits the wearer has Cause Fear cast on them (once)",
    19: "can't cast spells",
    21: "can't be Paralyzed, Slowed or Stuck",
    # attacking uses a charge, and only effects with charges end that way: Invisibility has
    # one, Improved Invisibility (timed) has none
    23: "attacking or casting at an enemy ends it, unless it is Improved Invisibility",
    24: "ends when it attacks or casts at an enemy",
    25: ("each hit, and each foe's spell for one creature, has a 75% chance (50% for Reflected Image's) "
         "to strike an image instead, which vanishes"),
    29: "can't be Paralyzed or Slowed",
    33: "can't attack or cast harmful spells",
    34: "loses its turns, can't move, fails every saving throw",
    35: "fatal (1000 damage) if time passes out of combat, such as resting, before it ends or is cured",
    44: "turns spells cast at it back on their caster, one per charge",
    48: "no damage from weapons; any damage uses up one charge",
    50: "can't cast spells",
    51: "can't move (Free Action prevents it; some creatures are immune)",
    53: "no damage from weapons, using up one charge each time",
    # (the time routine, 8066Dh: a STR below the score's own comes back as time passes, unless Diseased)
    13: "a lowered STR doesn't come back until it is cured (the spell itself lowers nothing)",
    14: "finds traps for certain, thief or not",
    20: "half damage from spells that are all fire or cold",
    # (the effect routine, 78223h: each round Protection from Evil, for a round, on its keeper's side near it)
    39: "each round gives Prot Evil (AC -2, +2 on saves against evil) to its side close by",
    42: "one undead's draining touch: a save against paralysis/poison/death stops it (and the undead takes 2d6)",
    # psionic powers' effects
    31: "magic resistance halved",
    32: "+75% magic resistance against mind-affecting spells (charms, holds, fear, confusion...)",
    61: "unarmed attacks do at least 1d10",
    62: "unarmed attacks do 2d4 (the arm is the weapon)",
}
# Effects that change a rule already listed above, from the same code
EFFECT_RULES[8] += "; can't cast spells that need sight"
EFFECT_RULES[47] += ", half movement and attacks, loses every other turn; ends Haste (Free Action and " \
                    "Protection from Paralysis prevent it)"
EFFECT_RULES[22] = "double movement and attacks; ends Slow"
# The strength damage adjustments the game adds after rolling melee damage: its own table
# (STR_DAMAGE_TABLE), which gives STR 18 +4 (AD&D's 18/76-90; Dark Sun has no exceptional
# strength); these if it can't be read. Seen in play for STR 17, 18, 19, 20, 22 and 24.
STR_DAMAGE = {1: -4, 2: -2, 3: -1, 4: -1, 5: -1, 16: 1, 17: 1, 18: 4, 19: 7, 20: 8, 21: 9,
              22: 10, 23: 11, 24: 12, 25: 14}


RACE_NAMES = {1: "human", 2: "dwarf", 3: "elf", 4: "half-elf", 5: "half-giant", 6: "halfling", 7: "mul",
              8: "thri-kreen"}
CREATION_CLASS_NAMES = {1: "Cleric", 2: "Druid", 3: "Fighter", 4: "Gladiator", 5: "Preserver",
                        6: "Psionicist", 7: "Ranger", 8: "Thief"}

SMALL_WORDS = {"of", "from", "to", "the", "and", "or", "in"}


def signed_text(n: int) -> str:
    return f"+{n}" if n >= 0 else str(n)


def effect_text(effect: "Effect", charges: Optional[int], seconds: Optional[int]) -> str:
    """ "Blur (23 rounds)", "Stoneskin (5 charges)", or just the name."""
    name = EFFECT_NAMES.get(effect.id, f"effect {effect.id}")
    if charges:
        return f"{name} ({charges} charge{'' if charges == 1 else 's'})"
    if seconds is not None:
        rounds = -(-seconds // 60)  # a round started counts
        return f"{name} ({rounds} round{'' if rounds == 1 else 's'})"
    return name


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def slots_text(levels) -> str:
    """ "1st 3/5, 2nd 2/3": spell slots left and the most, by spell level."""
    return ", ".join(f"{ordinal(level)} {left}/{most}" for level, left, most in levels)


def game_time(seconds: int) -> str:
    """Game time: seconds, 60 to a round (AD&D's one-minute round)."""
    if seconds % 60 == 0:
        rounds = seconds // 60
        return f"{rounds} round{'' if rounds == 1 else 's'}"
    return f"{seconds} seconds ({seconds / 60:.1f} rounds)"


def title(text: str) -> str:
    """'CONE OF COLD' -> 'Cone of Cold'."""
    words = string.capwords(text).split(" ")
    return " ".join(w.lower() if i and w.lower() in SMALL_WORDS else w for i, w in enumerate(words))


def find_data_segment(guest: GuestMemory, low: Optional[bytes] = None) -> Optional[int]:
    """The game's DS, or None if the game isn't running."""
    low = guest.read(0, CONVENTIONAL_AND_UPPER) if low is None else low
    for m in re.finditer(re.escape(BORLAND_SIG), low):
        base = m.start() - BORLAND_SIG_OFFSET
        if base % 16 == 0:
            return base // 16
    return None


NULL_AREA = 0x40  # the first bytes of the game's data segment, which its C runtime checks at exit


def plain_name(raw: bytes) -> bool:
    """An item's name as the game's tables hold it: printable ASCII with a letter in it."""
    return bool(raw) and all(32 <= b < 127 for b in raw) and any(chr(b).isalpha() for b in raw)


def far_pointer(guest: GuestMemory, ds: int, offset: int) -> int:
    off, seg = struct.unpack("<HH", guest.read(ds * 16 + offset, 4))
    return seg * 16 + off


def party_records(guest: GuestMemory, ds: int) -> List[Tuple[Optional[int], Optional[int]]]:
    """(creature record, character sheet) addresses for each party slot."""
    creatures = far_pointer(guest, ds, CREATURES_PTR)
    sheets = far_pointer(guest, ds, SHEETS_PTR)
    result = []
    for slot in range(PARTY_SIZE):
        creature = creatures + slot * CREATURE_SIZE
        record = guest.read(creature, CREATURE_SIZE)
        if len(record) < CREATURE_SIZE or not record[CREATURE_NAME]:
            result.append((None, None))
            continue
        sheet_index = struct.unpack_from("<H", record, CREATURE_SHEET_INDEX)[0]
        result.append((creature, sheets + sheet_index * SHEET_SIZE))
    return result


# Effects that change initiative (effect id -> adjustment), from the game's code
INITIATIVE_EFFECTS = {8: -2, 22: 2, 47: -2}  # Blind, Hasted, Slowed


# A saving throw's modifiers, as the game's routine (79D3Ch in DSUN.EXE) adds them to the d20:
# effects on the target, its class, race and WIS or CON, and who cast the spell
SAVE_CON, SAVE_WIS = 0x810, 0x82A  # DS: a byte per ability score (CON for paralysis/poison/death saves)
PPD_SAVE = 1  # the sheet's paralysis/poison/death save
EVIL_ALIGNMENTS = (3, 6, 9)  # lawful, neutral and chaotic evil
SAVE_WIS_CATEGORY = 0x1E  # spells WIS counts against: mind-affecting, charms and holds, fear, illusions
SAVE_PSIONICIST_CATEGORY = 0x06  # ... and psionicists' +2: mind-affecting, charms and holds
DRUID_CLASSES, PSIONICIST = range(5, 9), 12
DWARF, HALFLING, UNDEAD = 2, 6, 9
EFFECT_BLESSED, EFFECT_BLIND, EFFECT_DETECT_INVIS, EFFECT_INVISIBLE, EFFECT_INVIS_UNDEAD = 7, 8, 15, 23, 24
EFFECT_PROT_EVIL, EFFECT_PROT_COLD, EFFECT_PROT_FIRE, EFFECT_PROT_LIGHTNING = 38, 36, 40, 41
EFFECT_FIRE_SHIELD = 20
# The game's damage routine (7B4C0h) halves a spell's damage when every kind it does (its record's
# +1Ah; magic, 200h, aside) is one the target is protected from: Resist and Protection from Fire
# fire (2), Resist Cold cold (4), Protection from Lightning electricity (80h), Fire Shield both
# fire and cold
HALVING_EFFECTS = ((EFFECT_PROT_FIRE, 0x02), (EFFECT_PROT_COLD, 0x04), (EFFECT_PROT_LIGHTNING, 0x80),
                   (EFFECT_FIRE_SHIELD, 0x06))
EFFECT_SAVE_PENALTY, EFFECT_SPIRIT_ARMOR, EFFECT_BARKSKIN, EFFECT_PRAYER = 45, 56, 57, 73
EFFECT_BRAVE = 9  # (Cloak of Bravery: +4 against a spell flagged FEAR_CATEGORY, a charge used)
FEAR_CATEGORY = 0x100  # (a record's +11h word: the patched game's fear spells, gamepatch brave_fear_*)
SHEET_SAVES = 0x37  # the five saves, in SAVE_NAMES order
SAVE_SHORT = ("PPD", "RSW", "PP", "BW", "SP")  # as the game's inventory screen labels them
# To hit, as the game's attack setup adds it: STR (melee) or DEX (missiles) from these tables,
# the attacker's effects, the weapon's plus or its material's penalty
STR_TO_HIT, DEX_MISSILE = 0x7C2, 0x7DC  # DS: a byte per ability score
STR_DAMAGE_TABLE = 0x7A8  # DS: the same, for melee damage (just before STR_TO_HIT)
HIT_EFFECTS = ((7, 1), (12, -1), (47, -4), (49, 1), (FOG_EFFECT, -3))  # Blessed, Cursed, Slowed, Graft Weapon, Fogbolt
WEAPON_HANDS = (EQUIP_SLOTS.index("right hand"), EQUIP_SLOTS.index("left hand"))
MISSILE_SLOT = EQUIP_SLOTS.index("missile")


class ItemSeen(NamedTuple):
    """An item of the party's, as party_items saw it."""
    index: int          # the item's number (its record in the game's item table)
    member: int         # the party slot that has it
    owner: str          # ... and that member's name
    slot: Optional[str]  # where it is worn ("chest"), None if only carried
    label: str          # "Inix Hide Chest Armor"
    type: int           # its item type
    record: bytes       # the item's record (ITEM_SIZE bytes)
    kind: bytes         # its type's record (ITEM_TYPE_SIZE bytes)


class WeaponHit(NamedTuple):
    item: int  # its item number
    slot: int
    name: str
    thac0: int  # with this weapon, now
    parts: List[Tuple[str, int]]  # what is taken off the base THAC0 for it
    skill: int = 0  # weapon specialization's skill with it (specialize.NONE...), with the rule on
    halves: Optional[int] = None  # a missile weapon's attacks a round, in halves (its own, not the
    # character's), or a Battle Mage's with its chosen weapon spec, a Crusader's or Mind Warrior's
    # from 7th level, or the off hand's one a round (the rule for two weapons)


class ItemSave(NamedTuple):
    """An item's numbers against the game's acid and corroding touch (game.item_save)."""
    name: str  # "Leather Chest Armor +1"
    material: str  # as ACID_SAVES names it
    own: Optional[int]  # the game's number to reach (None: destroyed without a roll)
    adnd: int  # AD&D's
    plus: int
    power: bool  # it has a magical power (the item's +0Fh)


class SaveNow(NamedTuple):
    base: int  # the character sheet's
    needs: int  # the d20 needed now (2-20: a 1 always fails, a 20 always saves)
    parts: List[Tuple[int, str]]  # the modifiers that always count (not the situational ones)


class Effect(NamedTuple):
    owner: int  # combatant id
    caster: int  # combatant id
    id: int


# Class numbers: a cleric, druid and ranger class for each element, in the order air, earth,
# fire, water (from the spheres in the game's class and spell tables: Flame Blade and Flame
# Strike belong to the third, Blood Flow and Dehydrate to the fourth, Deflection to the first)
CLASS_NAMES = {1: "Cleric (air)", 2: "Cleric (earth)", 3: "Cleric (fire)", 4: "Cleric (water)",
               5: "Druid (air)", 6: "Druid (earth)", 7: "Druid (fire)", 8: "Druid (water)", 9: "Fighter",
               10: "Gladiator", 11: "Preserver", 12: "Psionicist", 13: "Ranger (air)", 14: "Ranger (earth)",
               15: "Ranger (fire)", 16: "Ranger (water)", 17: "Thief"}


def class_share(sheet: bytes) -> int:
    """The classes a character's hit points are shared between: its number of classes, 1 for a
    human (who dual-classes)."""
    if sheet[SHEET_RACE] == HUMAN:
        return 1
    return max(sum(1 for c in sheet[SHEET_CLASSES:SHEET_CLASSES + 3] if c), 1)


def con_share(sheet: bytes, bonus: int, groups: Dict[int, int], last_die: Dict[int, int]) -> Optional[int]:
    """With RULE_MULTI_HP (DSCLOG's CON_SHARE), the hit points CON adds to the most of a character of
    more than one class, as Demihuman Deities (TSR 1998) has them: each hit die so far with CON's
    bonus on it, in the total the game keeps (the sheet's +0Ah: the dice), the total divided by the
    classes. BONUS is a warrior's (LEVEL_HP_CON_BONUS for CON), on every die if a class is a
    warrior's (group 1), else at most +2; GROUPS each class's hit point group, LAST_DIE each group's
    last level that rolls a die. That is (total + bonus x dice) / classes less total / classes,
    the total as the game scales it for lost levels. One class: None (the game's own)."""
    n = class_share(sheet)
    if n == 1:
        return None
    levels = sum(sheet[SHEET_LEVELS:SHEET_LEVELS + 3])
    before = sum(sheet[SHEET_LEVELS_BEFORE:SHEET_LEVELS_BEFORE + 3])
    total = struct.unpack_from("<h", sheet, SHEET_HP_BASE)[0]
    if before:
        total = int(total * levels / before)
    classes = [(c, sheet[SHEET_LEVELS + i]) for i, c in enumerate(sheet[SHEET_CLASSES:SHEET_CLASSES + 3])
               if 0 < c < 32 and groups.get(c) is not None]
    dice = sum(min(level, last_die.get(groups[c], level)) for c, level in classes)
    if not any(groups[c] == WARRIOR_GROUP for c, _ in classes):
        bonus = min(bonus, 2)
    return int((total + bonus * dice) / n) - int(total / n)


class LevelHp(NamedTuple):
    sides: int  # the hit die
    dice_levels: int  # levels up to this one roll it
    fixed: int  # hit points per level after that


class SpellDamage(NamedTuple):
    """A spell's damage, from its record (+0Ch..+0Eh): base dice, then per step some dice and a
    flat bonus; steps = (caster level, at most 10, + adjust) // per_levels, at least 1."""
    base_dice: int
    step_dice: int
    step_bonus: int
    per_levels: int
    adjust: int
    sides: int

    def steps(self, level: int) -> int:
        return max(1, (min(level, SPELL_LEVEL_CAP) + self.adjust) // self.per_levels)

    def flat(self) -> bool:
        """Its step only a flat bonus, the same at every caster level (one step whatever the
        level: the patched Cause Serious and Critical Wounds' +1 and +3)."""
        return not self.step_dice and all(self.steps(level) == 1 for level in range(1, SPELL_LEVEL_CAP + 1))


SPELL_LEVEL_CAP = 10  # damage stops growing at caster level 10
PERMANENT = -9999  # a spell record's time unit for effects that last until removed
MIND_AFFECTING = 0x26  # flags in the spell record's word at +11h

# Spell slots. What's left: a byte for each spell level (index 1-9) for each party member,
# 1Eh apart, wizard and priest apart; casting takes one, resting refills them.
SLOTS_LEFT = {"Wizard": 0x4B08, "Priest": 0x4B11}
SLOTS_STRIDE, SPELL_LEVELS = 0x1E, 9
MAGIC_KINDS = (("Wizard", 1), ("Priest", 2))
# The most: each class's magic (bit 1 wizard, bit 2 priest; a byte every 4, by class number)...
CLASS_MAGIC_SEG, CLASS_MAGIC_OFF = 0x3800, 0x118
# ...and its slot rules: DS byte per class number, a rule number in each nibble (low first:
# class level, then WIS), and the rule words, a DS word each
SLOT_CLASS_RULES, SLOT_RULES = 0x664, 0x678
# Each spell's spheres (a dword, 7 bytes a spell), matched against each class's (above)
SPELL_SPHERES_SEG, SPELL_SPHERES_OFF, SPELL_SPHERES_SIZE = 0x3FB9, 0x19D, 7
RANGER_CLASSES = range(13, 17)
SLOTS_ALL_19 = 0x1164  # a DS word the game checks: 1 gives the party 19 of everything
HUMAN = 1

# Thief skills (the game's routine at 8023Bh in DSUN.EXE). Their order is AD&D's; the game
# never names them, but its checks fit: blindness stops all but hearing noise, Fire Shield
# and Mirror Image stop hiding, Graft Weapon stops picking pockets, opening locks and
# climbing, Detect Traps lets anyone find traps, Feeblemind stops reading languages.
THIEF_SKILLS = ("pick pockets", "open locks", "find/remove traps", "move silently", "hide in shadows",
                "hear noise", "climb walls", "read languages")
READ_LANGUAGES = 7  # (a Shinobi reads a scroll with it: intlearn.py)
# the ones shown: those the game ever rolls (no script asks for the other three), and move
# silently, which the Loader rolls when a pocket isn't picked (pickpocket.py)
ROLLED_SKILLS = (0, 1, 2, 3, 5, 6)
# the ones the game's inventory screen shows (DSCLOG's STATS): hide in shadows, which the Loader's
# stealth rule rolls, in hear noise's place (one script check in the game, and no room for both)
PANEL_SKILLS = (0, 1, 2, 3, 4, 6)
# ... and the ones the Loader's own screens show (room for all that are ever rolled)
LEDGER_SKILLS = (0, 1, 2, 3, 4, 5, 6)
THIEF = 17  # class number
PRESERVER = 11
# Tables (a byte per skill): base; then 8 per race (race 1 first); DEX below which each point
# costs 5, above which each gives 5, above which each costs 3 again; the armour penalty
THIEF_TABLE_SEG = 0x3FAA
THIEF_BASE, THIEF_RACE, THIEF_DEX_LOW, THIEF_DEX_HIGH, THIEF_DEX_TOP, THIEF_ARMOUR = 0, 8, 0x90, 0x98, 0xA0, 0xA8
THIEF_PER_LEVEL = 4
# The equipment the thief routine checks for its penalty (anything at all in these slots): a
# list of words at the thief table's +D0h, ended by 13: the legs, the quiver and both hands. The
# dice log's copy of the game empties it (gamepatch.py), so the Loader reads it
THIEF_PENALTY_LIST, PENALTY_LIST_END = 0xD0, 13
THIEF_PENALTY_SLOTS = tuple(EQUIP_SLOTS.index(s) for s in ("legs", "ammo", "left hand", "right hand"))
# RULE_THIEF_TABLE (DSCLOG's PROBE_THIEF_SKILL does the same in the game): a skill is AD&D's
# average for the thief level (1-10, by skill) in place of the game's base + 4 a level, plus the
# game's race adjustment (Dark Sun's own numbers already), plus Dark Sun's DEX adjustment (AD&D's
# table to 19, the Dark Sun rules' past it, 9-22; none for the last three skills) in place of the
# game's DEX formula
AD_D_THIEF = ((30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 95, 99),  # pick pockets
              (25, 29, 33, 37, 42, 47, 52, 57, 62, 67, 72, 77, 82),  # open locks
              (20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80),  # find/remove traps
              (15, 21, 27, 33, 40, 47, 55, 62, 70, 78, 86, 94, 99),  # move silently
              (10, 15, 20, 25, 31, 37, 43, 49, 56, 63, 70, 77, 85),  # hide in shadows
              (10, 10, 15, 15, 20, 20, 25, 25, 30, 30, 35, 35, 40),  # hear noise
              (85, 86, 87, 88, 90, 92, 94, 96, 98, 99, 99, 99, 99),  # climb walls
              (0, 0, 0, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65))     # read languages
DEX_FIRST = 9
DEX_ADJUST = ((-15, -10, -10, -20, -10), (-10, -5, -10, -15, -5), (-5, 0, -5, -10, 0), (0, 0, 0, -5, 0),  # 9-12
              (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 5, 0, 0, 0),  # 13-16
              (5, 10, 0, 5, 5), (10, 15, 5, 10, 10), (15, 20, 10, 15, 15),  # 17-19
              (20, 25, 12, 20, 17), (25, 27, 15, 25, 20), (27, 30, 17, 30, 22))  # 20-22


def dex_adjustment(dex: int, skill: int) -> int:
    """Dark Sun's DEX adjustment to a thief skill (DEX below 9 as 9, above 22 as 22)."""
    if skill >= len(DEX_ADJUST[0]):
        return 0
    return DEX_ADJUST[min(max(dex, DEX_FIRST), DEX_FIRST + len(DEX_ADJUST) - 1) - DEX_FIRST][skill]


# AD&D's ranger: hide in shadows and move silently by ranger level (1-13), the Loader's own
# (the game gives rangers no thief skills); race and DEX adjust them as a thief's
RANGER_HIDE = AD_D_THIEF[4]
RANGER_MOVE = AD_D_THIEF[3]
# Effects that rule skills out (the chance can't come up), and ones that make a skill certain
THIEF_BLOCKED = {8: (0, 1, 2, 3, 4, 6, 7), 17: tuple(range(8)), 11: tuple(range(8)), 3: tuple(range(8)),
                 34: tuple(range(8)), 47: (1, 2, 3, 4, 5, 6, 7), 20: (0, 4), 25: (4,), 49: (0, 1, 6), 19: (7,)}
THIEF_CERTAIN = {14: (2,), 23: (4,)}  # Detect Traps, Invisible
STATUS_OKAY = 1
STATUS_NEW = 0  # not yet played (the game makes it Okay when the game starts)
STATUS_ABLE = (STATUS_NEW, STATUS_OKAY)  # counted as Okay (the patched game's NEW_AS_OKAY)


# The spell's damage kinds (its flags word): the saving throw doubles the d20 against fire,
# cold and electricity, and no other kind
DOUBLED_KINDS = {0x02: "fire", 0x04: "cold", 0x80: "electricity"}


class SpellRules(NamedTuple):
    doubles_roll: bool  # the saving throw's d20 counts double
    save_modifier: int  # added to every saving throw against the spell
    doubled_for: str = ""  # the damage kind that doubles it: "fire", "cold" or "electricity"


class Weapon(NamedTuple):
    name: str
    count: int
    sides: int
    bonus: int
    plus: int
    material: int
    nonmagical_flag: bool  # item type flag that exempts it from material penalties

    def dice(self) -> str:
        bonus = self.bonus + self.plus
        return f"{self.count}d{self.sides}" + (f"{bonus:+d}" if bonus else "")


class GameData:
    """Lookups into the running game's memory for one session."""

    def __init__(self, guest: GuestMemory, ds: int, rules: Optional[int] = None):
        self.guest = guest
        self.ds = ds
        self.load_seg = ds - DGROUP
        if hasattr(guest, "guarded"):  # (the C runtime's check, at exit: "Null pointer assignment")
            guest.guarded["the game's data segment's start"] = (ds * 16, ds * 16 + NULL_AREA)
        if hasattr(guest, "item_gate"):  # (the Loader's changes to the item lists: never mid-load)
            from .itemgate import ItemGate
            guest.item_gate = ItemGate(self)
        self.rules = RULES_IN_FORCE if rules is None else rules
        self.belt = BELT_IN_FORCE
        self.dance: Dict[int, int] = {}  # each party member's Battle Dancer's dance now (+1, -1: dance.py)
        self.wild: Dict[int, bool] = {}  # each Wild Fury (or Gerakis) fighting wild this fight: whether its check passed (wild.py)

    def _word(self, offset: int) -> int:
        return struct.unpack("<h", self.guest.read(self.ds * 16 + offset, 2))[0]

    def str_damage(self, strength: int) -> int:
        """What STRENGTH adds to melee damage: the game's table (STR_DAMAGE_TABLE, taken as the
        game's when it starts as STR_DAMAGE does), else STR_DAMAGE."""
        if 1 <= strength <= 25:
            data = self.guest.read(self.ds * 16 + STR_DAMAGE_TABLE + 1, 25)
            if len(data) == 25 and struct.unpack_from("b", data)[0] == STR_DAMAGE[1]:
                return struct.unpack_from("b", data, strength - 1)[0]
        return STR_DAMAGE.get(strength, 0)

    def creature(self, index: int) -> bytes:
        if not 0 <= index < 512:
            return b""
        return self.guest.read(far_pointer(self.guest, self.ds, CREATURES_PTR) + index * CREATURE_SIZE,
                               CREATURE_SIZE)

    def creature_name(self, index: int) -> str:
        rec = self.creature(index)
        name = rec[CREATURE_NAME:CREATURE_NAME + 16].split(b"\0", 1)[0].decode("cp437", "replace")
        return name or f"creature {index}"

    def party_signature(self) -> bytes:
        """The party's names, which change when a game is loaded (from the main menu, at least)."""
        return b"".join(self.creature(i)[CREATURE_NAME:CREATURE_NAME + 16] for i in range(PARTY_SIZE))

    def combatant_creature(self, combatant: int) -> Optional[int]:
        """The creature record of one of the game's things on the map (all THINGS of them: the
        people put in later, such as Kalzith and Semyon in the pens, are past the 256th)."""
        if not 0 <= combatant < THINGS:
            return None
        kind, index = struct.unpack("<Bh", self.guest.read(
            (self.load_seg + COMBATANTS_SEG) * 16 + COMBATANTS_OFF + combatant * 3, 3))
        return index if kind == 2 else None

    def combatants(self) -> Dict[int, int]:
        """{combatant: creature index} for every creature in the fight (or the area): all THINGS
        of the map's things (people put in later, such as Kalzith and Semyon, are past the 256th)."""
        data = self.guest.read((self.load_seg + COMBATANTS_SEG) * 16 + COMBATANTS_OFF, THINGS * 3)
        out = {}
        for combatant in range(len(data) // 3):
            kind, index = struct.unpack_from("<Bh", data, combatant * 3)
            if kind == 2 and 0 <= index < 512:
                out[combatant] = index
        return out

    def creatures(self, count: int) -> bytes:
        """The first `count` creature records, in one read."""
        return self.guest.read(far_pointer(self.guest, self.ds, CREATURES_PTR), count * CREATURE_SIZE)

    def talk_target(self) -> Optional[str]:
        """The name of the creature the current script was started on (the person being talked to),
        when it is a living, named creature outside the party."""
        combatant, = struct.unpack("<h", self.guest.read((self.load_seg + TALK_SEG) * 16 + TALK_TARGET, 2))
        if combatant < PARTY_SIZE:
            return None
        index = self.combatant_creature(combatant)
        if index is None:
            return None
        rec = self.creature(index)
        name = rec[CREATURE_NAME:CREATURE_NAME + 16].split(b"\0", 1)[0].decode("cp437", "replace").strip()
        if not name or struct.unpack_from("<h", rec, 0)[0] <= 0:
            return None
        return name

    def living_npc(self, index: int) -> bool:
        """A creature outside the party, named and alive."""
        rec = self.creature(index)
        return index >= PARTY_SIZE and len(rec) >= CREATURE_SIZE and bool(rec[CREATURE_NAME]) \
            and struct.unpack_from("<h", rec, 0)[0] > 0

    def talk_target_creature(self) -> Optional[int]:
        """The creature index of the person being talked to (see talk_target), or None."""
        combatant, = struct.unpack("<h", self.guest.read((self.load_seg + TALK_SEG) * 16 + TALK_TARGET, 2))
        if combatant < PARTY_SIZE:
            return None
        index = self.combatant_creature(combatant)
        if index is None or index < PARTY_SIZE:
            return None
        rec = self.creature(index)
        if not rec[CREATURE_NAME] or struct.unpack_from("<h", rec, 0)[0] <= 0:
            return None
        return index

    def money(self) -> int:
        return struct.unpack("<I", self.guest.read((self.load_seg + MONEY_SEG) * 16 + MONEY, 4))[0]

    def add_money(self, amount: int) -> None:
        self.guest.write((self.load_seg + MONEY_SEG) * 16 + MONEY,
                         struct.pack("<I", max(0, self.money() + amount) & 0xFFFFFFFF))

    def flag(self, n: int) -> bool:
        """Flag N (False while the flags have no place in memory: their pointer is null at times,
        such as in the arena outside a script's run)."""
        flags = far_pointer(self.guest, self.ds, FLAGS_PTR)
        if not flags:
            return False
        return bool(self.guest.read(flags + n // 8, 1)[0] >> (n % 8) & 1)

    def set_flag(self, n: int, on: bool = True) -> None:
        """Flag N set (or cleared); nothing while the flags have no place in memory (see flag)."""
        flags = far_pointer(self.guest, self.ds, FLAGS_PTR)
        if not flags:
            return
        at = flags + n // 8
        byte = self.guest.read(at, 1)[0]
        self.guest.write(at, bytes([byte | 1 << (n % 8) if on else byte & ~(1 << (n % 8))]))

    def number(self, n: int) -> Optional[int]:
        """Global number N (None while the numbers have no place in memory, as flag)."""
        numbers = far_pointer(self.guest, self.ds, NUMBERS_PTR)
        if not numbers:
            return None
        return struct.unpack("<h", self.guest.read(numbers + n * 2, 2))[0]

    def region(self) -> int:
        """The region the party is in (its RGNxx.GFF)."""
        return self._word(REGION)

    def party_position(self) -> Tuple[int, int]:
        """Where the party's leader (object 0) stands on the map: x, y in 16ths of a square."""
        return struct.unpack("<HH", self.guest.read(self.ds * 16 + POSITIONS, 4))

    def item_type_record(self, item: bytes) -> bytes:
        types = far_pointer(self.guest, self.ds, ITEM_TYPES_PTR)
        return self.guest.read(types + struct.unpack_from("<H", item, ITEM_TYPE)[0] * ITEM_TYPE_SIZE, ITEM_TYPE_SIZE)

    def combatant_name(self, combatant: int) -> str:
        index = self.combatant_creature(combatant)
        return self.creature_name(index) if index is not None else "?"

    def difficulty(self) -> int:
        return self._word(DIFFICULTY)

    def effects_left(self) -> List[Tuple[Effect, Optional[int], Optional[int]]]:
        """Each active effect with its charges left (None if it has none) and its game seconds
        left (None if untimed). A timed effect sits in the game's event queue as an entry of
        type 7 holding its owner and handle (the effect's byte +7), due at a game time."""
        count = self._word(EFFECT_COUNT)
        if not 0 <= count <= 400:
            return []
        data = self.guest.read((self.load_seg + EFFECTS_SEG) * 16 + EFFECTS_OFF, count * 10)
        due = {}
        queued = self._word(EVENT_COUNT)
        if 0 <= queued <= 500:
            events = self.guest.read(far_pointer(self.guest, self.ds, EVENT_QUEUE), queued * EVENT_SIZE)
            for i in range(queued):
                at, kind, owner, handle = struct.unpack_from("<iBhB", events, i * EVENT_SIZE)
                if kind == EVENT_EFFECT_ENDS:
                    due[(owner, handle)] = at
        now = self.game_time()
        out = []
        for i in range(count):
            rec = data[i * 10:i * 10 + 10]
            effect = Effect(*struct.unpack_from("<hh", rec), rec[6])
            at = due.get((effect.owner, rec[7]))
            charges = rec[8] or None
            spell, = struct.unpack_from("<h", rec, 4)
            spell_rec = self.spell_record(spell) if 0 < spell < 256 else b""
            if len(spell_rec) >= SPELL_SIZE and struct.unpack_from("<h", spell_rec, 7)[0] == PERMANENT:
                charges = None  # a permanent effect keeps a meaningless 15 there
            out.append((effect, charges, max(at - now, 0) if at is not None and now is not None else None))
        return out

    def effect_spells(self) -> List[Tuple[Effect, int]]:
        """Each active effect with the spell (or power) that made it."""
        count = self._word(EFFECT_COUNT)
        if not 0 <= count <= 400:
            return []
        data = self.guest.read((self.load_seg + EFFECTS_SEG) * 16 + EFFECTS_OFF, count * 10)
        return [(Effect(*struct.unpack_from("<hh", data, i * 10), data[i * 10 + 6]),
                 struct.unpack_from("<h", data, i * 10 + 4)[0]) for i in range(count)]

    def reply_chosen(self) -> Optional[Tuple[int, str]]:
        """The reply the player has just clicked (its place in the list, and its text), while
        the game flashes it; None the rest of the time."""
        row = self.guest.read(self.ds * 16 + REPLY_CHOSEN, 1)[0]
        if row == 0xFF:
            return None
        n = row + self.guest.read(self.ds * 16 + REPLY_SCROLL, 1)[0]
        text = self.guest.read(self.ds * 16 + REPLY_TEXTS + n * REPLY_SIZE, REPLY_SIZE)
        return n, text.split(b"\0", 1)[0].decode("cp437", "replace").strip()

    def in_combat(self) -> bool:
        """The party is in a fight (the game's own flag, IN_COMBAT)."""
        return self._word(IN_COMBAT) != 0

    def fight_on(self) -> bool:
        """A fight is on, as the game's rest and USE screen tell (FIGHT_STATE_ON), not merely the
        party spread out (IN_COMBAT)."""
        at = (self.ds - FIGHT_STATE_FROM_DS) * 16 + FIGHT_STATE_ON
        return struct.unpack("<H", self.guest.read(at, 2))[0] != 0

    def whose_turn(self) -> Optional[int]:
        """The combatant whose turn it is in a fight (the game's word at WHOSE_TURN)."""
        turn = self._word(WHOSE_TURN)
        return turn if 0 <= turn < THINGS else None

    def game_time(self) -> Optional[int]:
        """Game seconds since the start (60 to a round): the dword the game keeps its clock in."""
        scale = self.guest.read(self.ds * 16 + GAME_TIME_SCALE, 1)[0]
        raw = self.guest.read(far_pointer(self.guest, self.ds, GAME_TIME_PTR), 4)
        return struct.unpack("<i", raw)[0] // scale if scale and len(raw) == 4 else None

    def effects(self) -> List[Effect]:
        count = self._word(EFFECT_COUNT)
        if not 0 <= count <= 400:
            return []
        data = self.guest.read((self.load_seg + EFFECTS_SEG) * 16 + EFFECTS_OFF, count * 10)
        return [Effect(*struct.unpack_from("<hh", data, i * 10), data[i * 10 + 6]) for i in range(count)]

    def image_chance(self, combatant: int) -> int:
        """The chance (percent) of an image of COMBATANT's Mirror Images taking a blow or a foe's
        spell: 75, or 50 for one of Reflected Image (DSCLOG's IMAGE_CHANCE)."""
        count = self._word(EFFECT_COUNT)
        if 0 < count <= 400:
            data = self.guest.read((self.load_seg + EFFECTS_SEG) * 16 + EFFECTS_OFF, count * 10)
            for i in range(count):
                owner, _, spell = struct.unpack_from("<hhh", data, i * 10)
                if owner == combatant and data[i * 10 + 6] == MIRROR_EFFECT:
                    return REFLECT_CHANCE if spell == REFLECT_SPELL else IMAGE_CHANCE
        return IMAGE_CHANCE

    def _power_dice(self, spell: int) -> str:
        """" (1d10 crushing)": a monster's power's damage dice and kinds, from its record, to tell
        it by (the game has no name for it), or ""."""
        from . import spellbook
        try:
            rule = self.spell_damage(spell)
            rec = self.spell_record(spell)
        except (struct.error, IndexError, ValueError):
            return ""
        if rule is None or len(rec) < 0x1C or rule.sides <= 1 or not rule.base_dice \
                or rule.step_dice or rule.step_bonus:
            return ""
        kinds = struct.unpack_from("<H", rec, 0x1A)[0]
        names = [name for bit, name in spellbook.DAMAGE_KINDS if kinds & bit]
        return f" ({rule.base_dice}d{rule.sides}{' ' + ', '.join(names) if names else ''})"

    def power_effect(self, spell: int) -> int:
        """The effect a monster's power puts on (its record's +19h), 0 for none."""
        try:
            rec = self.spell_record(spell)
        except (struct.error, IndexError, ValueError, OSError):
            return 0
        return struct.unpack_from("b", rec, 0x19)[0] if len(rec) > 0x19 else 0

    def _power_name(self, spell: int) -> str:
        """A monster's power, named by what its record does: the effect it puts on ("Paralysing
        attack"), else its damage's kind ("Fire attack (6d6 fire)"), else its number."""
        dice = self._power_dice(spell)
        harms = " " in dice.strip(" ()")  # (dice with a damage kind: else they may be its time)
        if self.power_effect(spell) in POWER_EFFECT_NAMES:
            return POWER_EFFECT_NAMES[self.power_effect(spell)] + (dice if harms else "")
        if harms:
            kind = dice.strip(" ()").split(" ", 1)[1].split(",")[0]
            return f"{POWER_KIND_NAMES.get(kind, kind).capitalize()} attack{dice}"
        return f"special attack {spell}{dice}"

    def power_score_parts(self, combatant: int, power: int) -> Optional[Tuple[str, int, int]]:
        """A psionic power's check score parts for COMBATANT (as the game's 5D59Dh adds them): the
        ability's name, the power's adjustment, and the user's own number for it less 1 (a party
        member's; a monster's is 1, so 0)."""
        if not 0 <= power < PSIONIC_COUNT:
            return None
        try:
            first = self.guest.read((self.load_seg + POWERS_SEG) * 16 + power * POWER_SIZE, 1)[0]
            own = 0
            if 0 <= combatant < PARTY_SIZE:
                seg, = struct.unpack("<H", self.guest.read((self.load_seg + SEGMENT_TABLE) * 16 + POWER_OWN_SELECTOR, 2))
                byte = self.guest.read(seg * 16 + POWER_OWN_OFF + combatant * POWER_OWN_STRIDE + power, 1)[0]
                own = max((byte >> 3) - 1, 0)
        except (OSError, ValueError):
            return None
        index = first & 7
        adjustment = (first >> 3) - 32 if first >> 3 > 15 else first >> 3
        return (ABILITY_NAMES[index] if index < len(ABILITY_NAMES) else f"ability {index}"), adjustment, own

    def spell_name(self, spell: int) -> str:
        if PSIONIC_FIRST <= spell < PSIONIC_FIRST + PSIONIC_COUNT:
            # the psionic powers' names come first in the names list, in number order
            names = self.guest.read(self.ds * 16 + SPELL_NAMES, 0x400).split(b"\0")
            text = names[spell - PSIONIC_FIRST].decode("cp437", "replace") if spell - PSIONIC_FIRST < len(names) else ""
            return title(text) if text else f"psionic power {spell}"
        if spell in NEW_SPELLS:
            return NEW_SPELLS[spell]
        if spell in PRIEST6_SPELLS:
            return PRIEST6_SPELLS[spell]
        if spell == NPP_SAVE_RECORD:
            return "Negative Plane Protection"
        if spell in ITEM_ATTACKS:  # (the ones that can destroy an item)
            return ITEM_ATTACKS[spell].capitalize()
        if spell in POISON_POWERS:  # (a monster's poisoned hit, and a Poisoner's: kits.POISON_POWER)
            return POISON_POWERS[spell]
        if spell == DETONATE_BLAST:
            return f"Detonate's blast{self._power_dice(spell)}"
        if spell > SPELL_COUNT:  # monsters' powers, such as a paralysing touch: the game names none
            return self._power_name(spell)
        if SPELL_FIRST <= spell <= SPELL_COUNT:
            info = self.load_seg * 16 + SPELL_INFO_OFF + (spell - 1) * SPELL_INFO_SIZE
            name = struct.unpack("<H", self.guest.read(info + 5, 2))[0]
            if SPELL_NAMES <= name < SPELL_NAMES_END:
                text = self.guest.read(self.ds * 16 + name, 40).split(b"\0", 1)[0].decode("cp437", "replace")
                if text:
                    return title(text)
        return f"spell {spell}"

    def spell_rules(self, spell: int) -> Optional[SpellRules]:
        if not 0 <= spell < 256:
            return None
        rec = self.guest.read((self.load_seg + SPELLS_SEG) * 16 + SPELLS_OFF + spell * SPELL_SIZE, SPELL_SIZE)
        if len(rec) < SPELL_SIZE:
            return None
        nibble = (rec[0x0F] >> 1) & 0x0F
        flags = struct.unpack_from("<H", rec, 0x0A)[0]
        kinds = " and ".join(name for bit, name in DOUBLED_KINDS.items() if flags & bit)
        doubled = bool(kinds) and not self.rules & RULE_NO_DOUBLE
        return SpellRules(doubled, nibble - 16 if nibble & 8 else nibble, kinds if doubled else "")

    def set_dodge(self, on: bool) -> int:
        """Mark the fire, cold and electricity spells for DEX on their saves (CATEGORY_DODGE),
        or unmark them. Returns how many records changed."""
        changed = 0
        for spell in range(SPELL_FIRST, NEW_SPELLS_END):  # (past them the game's live data)
            at = (self.load_seg + SPELLS_SEG) * 16 + SPELLS_OFF + spell * SPELL_SIZE
            rec = self.guest.read(at, SPELL_SIZE)
            if len(rec) < SPELL_SIZE:
                break
            want = on and bool(struct.unpack_from("<H", rec, 0x0A)[0] & DOUBLED_FLAGS)
            byte = rec[0x01]
            new = byte | CATEGORY_DODGE if want else byte & ~CATEGORY_DODGE
            if new != byte:
                self.guest.write(at + 0x01, bytes((new,)))
                changed += 1
        return changed

    def new_spells_known(self, member: int) -> List[int]:
        """The new spells (NEW_SPELLS) party member MEMBER knows: its sheet's bits (NEW_KNOWN)."""
        sheet = self.sheet(member)
        if len(sheet) <= NEW_KNOWN_SHEET:
            return []
        return [spell for spell in NEW_SPELLS if knows_new_spell(sheet, spell)]

    def spell_level(self, spell: int) -> int:
        """The spell's level (the game's table of spells, 7 bytes each: SPELL_LEVELS)."""
        if not 0 <= spell < 256:
            return 0
        return self.guest.read((self.load_seg + SPELL_LEVELS_SEG) * 16 + SPELL_LEVELS_OFF + spell * 7, 1)[0]

    def spell_record(self, spell: int) -> bytes:
        """The spell's whole 32-byte record (it starts 10h before the fields SPELLS_OFF names)."""
        if not 0 <= spell < 256:
            return b""
        return self.guest.read((self.load_seg + SPELLS_SEG) * 16 + SPELLS_OFF - 0x10 + spell * SPELL_SIZE,
                               SPELL_SIZE)

    def spell_duration(self, spell: int, level: int, roll: int) -> Optional[Tuple[int, str]]:
        """(game seconds, how) for a spell cast at `level` whose duration dice came up `roll`:
        ((level + adjust) * per_level // per_levels + dice) * unit. 60 seconds are a round."""
        rec = self.spell_record(spell)
        if len(rec) < SPELL_SIZE:
            return None
        unit, = struct.unpack_from("<h", rec, 7)
        if unit <= 0:
            return None  # not timed: charges (see spell_charges), or -9999: permanent
        return self._spell_amount(rec, spell, level, roll, unit)

    def spell_charges(self, spell: int, level: int, roll: int) -> Optional[Tuple[int, str]]:
        """(charges, how) for an effect that lasts a number of uses rather than a time: the
        game stores a negative duration as that many charges (Stoneskin's blows, Mirror
        Image's images, Invisibility's one attack)."""
        rec = self.spell_record(spell)
        if len(rec) < SPELL_SIZE:
            return None
        unit, = struct.unpack_from("<h", rec, 7)
        if not PERMANENT < unit < 0:
            return None
        found = self._spell_amount(rec, spell, level, roll, -unit)
        return (found[0], found[1]) if found[0] > 0 else None

    def _spell_amount(self, rec: bytes, spell: int, level: int, roll: int, unit: int) -> Tuple[int, str]:
        per_level, = struct.unpack_from("<H", rec, 5)
        rule = self.spell_damage(spell)
        per_levels, adjust = (rule.per_levels, rule.adjust) if rule else (1, 0)
        levels = (max(level, 1) + adjust) * per_level // per_levels
        total = min((levels + roll) * unit, 0x7FFF)
        how = []
        if per_level:
            how.append(f"{per_level} for each " + ("caster level" if per_levels == 1 else f"{per_levels} caster levels")
                       + (f" ({signed_text(adjust)})" if adjust else "") + f" = {levels}")
        how.append(f"{roll} from the dice")
        return total, " + ".join(how)

    def damage_halved_by(self, target: int, spell: int) -> Optional[str]:
        """The protection on combatant TARGET that halves SPELL's damage (as the game's damage
        routine does), or None."""
        rec = self.spell_record(spell)
        if len(rec) < SPELL_SIZE:
            return None
        kinds = struct.unpack_from("<H", rec, 0x1A)[0]
        mine = {x.id for x in self.effects() if x.owner == target}
        guarded = 0
        names = []
        for eff, bits in HALVING_EFFECTS:
            if eff in mine and kinds & bits:
                guarded |= bits
                names.append(EFFECT_NAMES[eff])
        from . import kits
        ti = self.combatant_creature(target)  # (the patched game's WANDER_DMG: as Resist Fire and Cold)
        if ti is not None and kinds & kits.WANDERER_GUARDS and kits.WANDERER in self.kit_ids(ti):
            guarded |= kits.WANDERER_GUARDS
            names.append("Wanderer")
        if not guarded or kinds & ~(guarded | 0x200):
            return None
        return " and ".join(names)

    def save_negates_damage(self, spell: int) -> bool:
        """A successful save stops all the damage (else it halves it): flag 8000h of the word at +11h."""
        rec = self.spell_record(spell)
        return len(rec) >= SPELL_SIZE and bool(struct.unpack_from("<H", rec, 0x11)[0] & 0x8000)

    def spell_damage(self, spell: int) -> Optional[SpellDamage]:
        if not 0 <= spell < 256:
            return None
        rec = self.guest.read((self.load_seg + SPELLS_SEG) * 16 + SPELLS_OFF + spell * SPELL_SIZE, SPELL_SIZE)
        if len(rec) < SPELL_SIZE:
            return None
        b0, b1, b2 = rec[0x0C], rec[0x0D], rec[0x0E]
        adjust = (b2 >> 4) - 16 if b2 & 0x80 else b2 >> 4
        return SpellDamage(b1 >> 3, b0 >> 5, b0 & 0x1F, (b1 & 7) or 1, adjust, b2 & 0x0F)

    def mind_affecting(self, spell: int) -> bool:
        """A mind-affecting spell (charms, fear, feeblemind...): bits 26h of the word at +11h."""
        rec = self.spell_record(spell)
        return len(rec) >= SPELL_SIZE and bool(struct.unpack_from("<H", rec, 0x11)[0] & MIND_AFFECTING)

    def save_modifiers(self, target: int, caster: int, spell: int, save: int) -> List[Tuple[int, str]]:
        """What the game adds to a saving throw's d20 (besides the spell's own modifier), as
        [(amount, why), ...]: the target's rings (with the patched game), effects, class, race
        and WIS or CON, and whether the caster is evil or can see the target."""
        ti, ci = self.combatant_creature(target), self.combatant_creature(caster)
        if ti is None:
            return []
        rec, sheet, creature = self.spell_record(spell), self.sheet(ti), self.creature(ti)
        if len(rec) < SPELL_SIZE or len(sheet) < SHEET_SIZE or len(creature) < CREATURE_SIZE:
            return []
        category, = struct.unpack_from("<H", rec, 0x11)
        kinds, = struct.unpack_from("<H", rec, 0x1A)
        area = rec[0x17] != 0xFF  # a spell with an area (a table entry for it)
        effects = self.effects()
        mine = {x.id for x in effects if x.owner == target}
        theirs = {x.id for x in effects if x.owner == caster} if caster != target else set()
        caster_sheet = self.sheet(ci) if ci is not None else b""
        out: List[Tuple[int, str]] = []
        out += self.protection(ti)
        from . import kits
        for kid in self.kit_ids(ti):
            if kits.save(kid, spell, kinds):
                out.append((kits.save(kid, spell, kinds), kits.name(kid)))
        from . import robes
        robe = robes.worn_plus(self._worn(ti))
        if robes.save(robe, spell):
            out.append((robes.save(robe, spell), "Veiled Robe" if robe >= robes.VEILED_PLUS else "Ashen Robe"))
        if EFFECT_SAVE_PENALTY in mine:
            out.append((-1, EFFECT_NAMES[EFFECT_SAVE_PENALTY]))
        if spell == SPOOK_SPELL and self.rules & RULE_NEW_SPELLS and len(caster_sheet) >= SHEET_SIZE:
            places = range(3)
            preserver = max((caster_sheet[SHEET_LEVELS + p] for p in places
                             if caster_sheet[SHEET_CLASSES + p] == PRESERVER), default=0)
            thief = max((caster_sheet[SHEET_LEVELS + p] for p in places
                         if caster_sheet[SHEET_CLASSES + p] == THIEF), default=0)
            shinobi = kits.SHINOBI in self.kit_ids(ci)
            penalty = kits.spook_penalty(preserver, thief if shinobi else 0)
            if penalty:
                out.append((penalty, "Spook, the caster's levels"))
        if EFFECT_SPIRIT_ARMOR in mine and save != PPD_SAVE:
            out.append((3, EFFECT_NAMES[EFFECT_SPIRIT_ARMOR]))
        if EFFECT_BARKSKIN in mine:
            out.append((1, EFFECT_NAMES[EFFECT_BARKSKIN]))
        if EFFECT_BLESSED in mine:
            out.append((1, EFFECT_NAMES[EFFECT_BLESSED]))
        if category & FEAR_CATEGORY and EFFECT_BRAVE in mine:
            out.append((4, "Cloak of Bravery"))
        if EFFECT_PROT_EVIL in mine and len(caster_sheet) >= SHEET_SIZE and caster_sheet[0x1A] in EVIL_ALIGNMENTS:
            out.append((2, "Prot Evil against an evil caster"))
        for bit, eff, amount in ((0x80, EFFECT_PROT_LIGHTNING, 4), (0x04, EFFECT_PROT_COLD, 3),
                                 (0x02, EFFECT_PROT_FIRE, 3)):
            if kinds & bit and eff in mine:
                out.append((amount, EFFECT_NAMES[eff]))
        prayer = next((x for x in effects if x.id == EFFECT_PRAYER and x.owner == target), None)
        if prayer is not None:
            source = self.combatant_creature(prayer.caster)
            same = source is not None and self.creature(source)[CREATURE_SIDE] == creature[CREATURE_SIDE]
            out.append((1 if same else -1, "Prayer, " + ("its caster's side" if same else "the other side's")))
        if not area and caster != target:
            undead_caster = len(caster_sheet) >= SHEET_SIZE and caster_sheet[SHEET_RACE] == UNDEAD
            if EFFECT_BLIND in theirs:
                out.append((4, "the caster is Blind"))
            elif EFFECT_DETECT_INVIS not in theirs and (EFFECT_INVISIBLE in mine
                                                         or (EFFECT_INVIS_UNDEAD in mine and undead_caster)):
                out.append((4, "Invisible to the caster"))
        if kinds & 0x82 and any(self.class_level(ti, c) for c in DRUID_CLASSES):
            out.append((2, "druid against fire and electricity"))
        if self.class_level(ti, PSIONICIST) and category & SAVE_PSIONICIST_CATEGORY:
            out.append((2, "psionicist against the mind"))
        abilities = creature[CREATURE_ABILITIES:CREATURE_ABILITIES + 6]
        if category & SAVE_WIS_CATEGORY:
            wis = abilities[4]
            adjust = struct.unpack("b", self.guest.read(self.ds * 16 + SAVE_WIS + wis, 1))[0]
            if adjust:
                out.append((adjust, f"WIS {wis}"))
        if category & CATEGORY_DODGE:  # (the game's rule; see CATEGORY_DODGE)
            dex = abilities[1]
            adjust = -struct.unpack("b", self.guest.read(self.ds * 16 + DEX_AC + dex, 1))[0] if dex < 26 else 0
            if adjust:
                out.append((adjust, f"DEX {dex} dodging"))
        if save == PPD_SAVE:
            con = abilities[2]
            if sheet[SHEET_RACE] in (DWARF, HALFLING):
                out.append((con * 2 // 7, f"{'dwarf' if sheet[SHEET_RACE] == DWARF else 'halfling'} CON {con}"))
            adjust = struct.unpack("b", self.guest.read(self.ds * 16 + SAVE_CON + con, 1))[0]
            if adjust:
                out.append((adjust, f"CON {con}"))
        return [(amount, why) for amount, why in out if amount]

    def magic_resistance(self, combatant: int) -> Optional[int]:
        """The base magic resistance (percent) on a creature's character sheet."""
        index = self.combatant_creature(combatant)
        if index is None:
            return None
        sheet = struct.unpack_from("<H", self.creature(index), CREATURE_SHEET_INDEX)[0]
        return self.guest.read(far_pointer(self.guest, self.ds, SHEETS_PTR) + sheet * SHEET_SIZE
                               + SHEET_MAGIC_RESISTANCE, 1)[0]

    def items_readable(self, creature: int) -> bool:
        """Whether a creature's items read as items: each name plain text and its type in the table.
        Before the game has loaded its item tables (the main menu, character creation) the pointers
        lead to other data, and the names come out as noise (\"Wooden GF╨╢...\")."""
        try:
            for _, item, typ in self._worn(creature):
                index = struct.unpack_from("<H", item, ITEM_NAME)[0]
                if not 0 <= index < 0x400 or len(typ) != ITEM_TYPE_SIZE:
                    return False
                rec = self.guest.read(far_pointer(self.guest, self.ds, ITEM_NAMES_PTR) + index * ITEM_NAME_SIZE,
                                      ITEM_NAME_SIZE)
                if not plain_name(rec.split(b"\0", 1)[0]):
                    return False
        except (struct.error, IndexError, ValueError):
            return False
        return True

    def item_name(self, name_index: int) -> str:
        if 0 <= name_index < 0x400:
            rec = self.guest.read(far_pointer(self.guest, self.ds, ITEM_NAMES_PTR) + name_index * ITEM_NAME_SIZE,
                                  ITEM_NAME_SIZE)
            raw = rec.split(b"\0", 1)[0]
            if plain_name(raw):  # (not noise read before the game has its tables: items_readable)
                return raw.decode("ascii")
        return f"item {name_index}"

    def sheet(self, creature: int) -> bytes:
        """The character sheet of a creature (party members and monsters alike)."""
        rec = self.creature(creature)
        if len(rec) < CREATURE_SIZE:
            return b""
        index = struct.unpack_from("<H", rec, CREATURE_SHEET_INDEX)[0]
        return self.guest.read(far_pointer(self.guest, self.ds, SHEETS_PTR) + index * SHEET_SIZE, SHEET_SIZE)

    def spell_slots(self, member: int) -> List[Tuple[str, List[Tuple[int, int, int]]]]:
        """A party member's spell slots: [(kind, [(spell level, left, most), ...]), ...] for
        the kinds of magic (Wizard, Priest) their classes cast, at the spell levels their class
        levels reach. (The game gives WIS's bonus slots at spell levels the class can't cast yet
        too: no use to them, so not shown.)"""
        out = []
        for kind, bit in MAGIC_KINDS:
            left = self.guest.read(self.ds * 16 + SLOTS_LEFT[kind] + member * SLOTS_STRIDE, SPELL_LEVELS + 1)
            levels = [(lvl, left[lvl], self.max_spell_slots(member, bit, lvl)) for lvl in range(1, SPELL_LEVELS + 1)
                      if self.max_spell_slots(member, bit, lvl, wis=False)]
            if levels:
                out.append((kind, levels))
        return out

    def max_spell_slots(self, member: int, bit: int, spell_level: int, wis: bool = True) -> int:
        """The slots the game gives on resting (its routine at 5E0ACh in DSUN.EXE): for each class
        casting this kind of magic, rules from its tables applied to the class level and then WIS.
        A rule word: bits 8-11 the most it gives, bits 4-7 one more than the spell level it
        starts below, bit 0 how odd values round. A human's later (dual) classes count only while
        their level is below the first class's. Without `wis`, the class levels' alone. Then the
        kit's (kits.slot_level, kits.slots), as DSCLOG's PROBE_SLOT_LEVEL and PROBE_SLOTS."""
        if member < 4 and self._word(SLOTS_ALL_19) == 1:  # the game's own test switch
            return 19
        sheet = self.sheet(member)
        if len(sheet) < SHEET_SIZE:
            return 0
        ability = self.creature(member)[CREATURE_ABILITIES + 4]
        magic = self.guest.read((self.load_seg + CLASS_MAGIC_SEG) * 16 + CLASS_MAGIC_OFF, 4 * 32)
        from . import kitpages, kits, tables
        kids = self.kit_ids(member)
        total = 0
        for n in range(3):  # (an Elementalist's slots behind for its own class alone)
            own = kitpages.kit_at(sheet, n) if self.rules & RULE_KITS and kitpages.kit_awake(sheet, n) else 0
            cls, level = sheet[SHEET_CLASSES + n], kits.slot_level(own, sheet[SHEET_LEVELS + n])
            if not cls or cls >= 32 or not magic[cls * 4] & bit:
                continue
            if n and sheet[SHEET_RACE] == HUMAN and level >= sheet[SHEET_LEVELS]:
                continue
            rules = self.guest.read(self.ds * 16 + SLOT_CLASS_RULES + cls, 1)[0]
            ours = tables.slots(cls, level, spell_level) if self.rules & RULE_ADND_TABLES else None
            if ours is not None:  # (AD&D's for the level, the game's for WIS: DSCLOG's PROBE_ADND_SLOTS)
                total += ours
                rules >>= 4
            for value in ((ability,) if wis else ()) if ours is not None else ((level, ability) if wis else (level,)):
                if not rules:
                    break
                word, = struct.unpack("<H", self.guest.read(self.ds * 16 + SLOT_RULES + (rules & 0x0F) * 2, 2))
                start, odd, most = ((word >> 4) & 0x0F) - 1, word & 1, (word >> 8) & 0x0F
                count = value - (value + odd) // 2 - (spell_level + start)
                if count == 1 and (value & 1) == odd:
                    count += 1
                total += min(max(count, 0), most)
                rules >>= 4
        for kid in kids:
            total = kits.slots(kid, bit, kitpages.kit_level(sheet, kid), spell_level, total)
        from . import robes
        return robes.slots(robes.worn_plus(self._worn(member)), bit, spell_level, total)

    def class_level(self, creature: int, cls: int) -> int:
        """The creature's level in one class (0 if it hasn't that class)."""
        sheet = self.sheet(creature)
        if len(sheet) < SHEET_SIZE:
            return 0
        return next((sheet[SHEET_LEVELS + n] for n in range(3) if sheet[SHEET_CLASSES + n] == cls), 0)

    def effect_caster_level(self, creature: int, spell: int) -> Optional[int]:
        """The level a spell effect counts as having been cast at, as Dispel Magic weighs it (the
        game's routine at 81B16h): the caster's best level in a class sharing a sphere with the
        spell, rangers 7 levels less (a Seeker 5, a Justifier 9: kits.ranger_cast_drop), a Shinobi's
        wizard spells its thief level less 5 (kits.cast_level). None for
        psionic powers and monsters' own powers."""
        if not 0 < spell < PSIONIC_FIRST and spell not in NEW_SPELLS:
            return None
        spheres, = struct.unpack("<I", self.guest.read(
            (self.load_seg + SPELL_SPHERES_SEG) * 16 + SPELL_SPHERES_OFF + spell * SPELL_SPHERES_SIZE, 4))
        classes = self.guest.read((self.load_seg + CLASS_MAGIC_SEG) * 16 + CLASS_MAGIC_OFF, 4 * 20)
        from . import kitpages, kits
        kids = self.kit_ids(creature)
        sheet = self.sheet(creature)
        if len(sheet) >= SHEET_SIZE:  # (an Elementalist's second sphere: DSCLOG's PROBE_EL_CAST)
            for kid in kids:
                spheres = kits.spell_spheres(kid, kitpages.kit_class_of(sheet, kid), kits.second_sphere(kid, sheet),
                                             spheres)
        drop = kits.ranger_cast_drop(next((k for k in kids if k in (kits.SEEKER, kits.JUSTIFIER)), 0))  # (the game's 7)
        best = 0
        for cls in range(1, 20):
            if struct.unpack_from("<I", classes, cls * 4)[0] & spheres:
                level = self.class_level(creature, cls) - (drop if cls in RANGER_CLASSES else 0)
                best = max(best, level)
        for kid in kids:
            best = kits.cast_level(kid, spell, best, self.class_level(creature, THIEF))
        return best

    def thief_skill_parts(self, creature: int, skill: int) -> Optional[List[Tuple[str, int]]]:
        """What a thief skill's chance (percent) is made of, before armour, effects and the
        situation: [(what, amount), ...], or None for a character without thief levels."""
        sheet = self.sheet(creature)
        rec = self.creature(creature)
        if len(sheet) < SHEET_SIZE or len(rec) < CREATURE_SIZE or not 0 <= skill < len(THIEF_SKILLS):
            return None
        level = next((sheet[SHEET_LEVELS + n] for n in range(3) if sheet[SHEET_CLASSES + n] == THIEF), 0)
        if not level:
            return None
        table = self.guest.read((self.load_seg + THIEF_TABLE_SEG) * 16, THIEF_ARMOUR + 8)
        signed_byte = lambda offset: struct.unpack_from("b", table, offset)[0]
        race, dex = sheet[SHEET_RACE], rec[CREATURE_ABILITIES + 1]
        if self.rules & RULE_THIEF_TABLE:
            parts = [(f"thief level {level}", AD_D_THIEF[skill][min(level, len(AD_D_THIEF[0])) - 1])]
        else:
            parts = [("base", signed_byte(THIEF_BASE + skill)),
                     (f"thief level {level}", level * THIEF_PER_LEVEL)]
        if 1 <= race <= 8:
            parts.append((RACE_NAMES[race], signed_byte(THIEF_RACE + race * 8 + skill)))
        parts.append((f"DEX {dex}", self._dex_part(table, dex, skill)))
        return [(what, n) for what, n in parts if n or what in ("base", parts[0][0])]

    def _dex_part(self, table: bytes, dex: int, skill: int) -> int:
        """DEX's adjustment to a thief skill: Dark Sun's table (RULE_THIEF_TABLE), else the game's
        formula (each point below its low costs 5, above its high gives 5, above its top 3 less)."""
        if self.rules & RULE_THIEF_TABLE:
            return dex_adjustment(dex, skill)
        low, high, top = (table[o + skill] for o in (THIEF_DEX_LOW, THIEF_DEX_HIGH, THIEF_DEX_TOP))
        return -5 * max(low - dex, 0) + 5 * max(dex - high, 0) - 3 * max(dex - top, 0)

    def thief_skills(self, creature: int) -> List[Tuple[str, int]]:
        """[(skill, chance before armour and the situation), ...] for a thief, else []: the skills
        the game ever rolls, and move silently (hide in shadows and read languages never are)."""
        out = []
        for skill in ROLLED_SKILLS:
            name = THIEF_SKILLS[skill]
            parts = self.thief_skill_parts(creature, skill)
            if parts is None:
                return []
            out.append((name, sum(n for _, n in parts)))
        return out

    def thief_penalty_slots(self) -> Tuple[int, ...]:
        """The slots where anything at all brings the thief skills' equipment penalty: the game's
        list, as it is in memory (THIEF_PENALTY_SLOTS if it can't be read)."""
        data = self.guest.read((self.load_seg + THIEF_TABLE_SEG) * 16 + THIEF_PENALTY_LIST, 16)
        slots = []
        for (slot,) in struct.iter_unpack("<H", data):
            if slot >= PENALTY_LIST_END:  # (as the game's loop: 13 and up end it)
                return tuple(slots)
            slots.append(slot)
        return THIEF_PENALTY_SLOTS  # (no end: not the game's list)

    def ranger_level(self, creature: int) -> int:
        return max((self.class_level(creature, cls) for cls in RANGER_CLASSES), default=0)

    def outdoors(self, creature: int) -> bool:
        """A party member stands under the open sky (stealth.daylight, its combatant its own number):
        the Military Scout's skills, the Rescuer's cures (DSCLOG's KIT_OUTDOORS)."""
        from . import stealth
        try:
            return creature < PARTY_SIZE and stealth.daylight(self, creature)
        except (struct.error, IndexError, ValueError):
            return False

    def ranger_skill_parts(self, creature: int, skill: int) -> Optional[List[Tuple[str, int]]]:
        """A ranger's hide in shadows (4) or move silently (3), as thief_skill_parts: AD&D's
        chance for the ranger level, the race's and DEX's adjustments. None without ranger levels."""
        sheet, rec = self.sheet(creature), self.creature(creature)
        from . import kits
        level = self.ranger_level(creature) if len(sheet) >= SHEET_SIZE else 0
        avenger = not level and len(sheet) >= SHEET_SIZE and kits.AVENGER in self.kit_ids(creature)
        if avenger:  # (a Wilderness Avenger: 5 a level of its best class)
            level = max(sheet[SHEET_LEVELS:SHEET_LEVELS + 3])
        if not level or len(rec) < CREATURE_SIZE or skill not in (3, 4):
            return None
        table = self.guest.read((self.load_seg + THIEF_TABLE_SEG) * 16, THIEF_ARMOUR + 8)
        signed_byte = lambda offset: struct.unpack_from("b", table, offset)[0]
        race, dex = sheet[SHEET_RACE], rec[CREATURE_ABILITIES + 1]
        parts = [(f"ranger level {level}", (RANGER_HIDE if skill == 4 else RANGER_MOVE)[min(level, len(RANGER_HIDE)) - 1])]
        if avenger:
            parts = [(f"ranger as a Wilderness Avenger, level {level}", kits.AVENGER_STEALTH * level)]
        if 1 <= race <= 8:
            parts.append((RACE_NAMES[race], signed_byte(THIEF_RACE + race * 8 + skill)))
        parts.append((f"DEX {dex}", self._dex_part(table, dex, skill)))
        for kid in self.kit_ids(creature):
            if kits.stealth(kid):  # (a Stalker's)
                parts.append((kits.name(kid), kits.stealth(kid)))
        return [(what, n) for what, n in parts if n or what.startswith("ranger")]

    def gear_skill(self, creature: int, skill: int, chance: int) -> int:
        """CHANCE at moving silently (3) or hiding in shadows (4) with what the character wears,
        as the stealth rule's rolls count it (stealth.turn): with the cloak, boots and belt switch
        (BELT_IN_FORCE), a worn cloak's or boots' bonus, to no more than stealth.MOST (a chance
        already above it kept); the Cloak or Boots of Elvenkind's chance, if better (the cloak's
        under the open sky). Without the stealth rule, CHANCE."""
        from . import stealth
        if skill not in (3, 4) or not self.rules & RULE_STEALTH:
            return chance
        slot, elven, best, bonus = (CLOAK_SLOT, ELVEN_CLOAK_TYPE, stealth.ELVEN_HIDE_OUT, stealth.CLOAK_HIDE) \
            if skill == 4 else (FOOT, ELVEN_BOOTS_TYPE, stealth.ELVEN_QUIET, stealth.BOOTS_QUIET)
        if stealth.wears(self, creature, elven, slot):
            return max(chance, best)
        if self.belt and any(item[ITEM_SLOT] == slot for _, item, _ in self._worn(creature)):
            return max(chance, min(stealth.MOST, chance + bonus))
        return chance

    def ranger_skill_now(self, creature: int, skill: int, gear: bool = True) -> Optional[int]:
        """A ranger's chance as it stands: effects that rule hiding out or make it certain count
        as for a thief (no equipment penalty); with GEAR, a worn cloak's or boots' (gear_skill).
        None without ranger levels."""
        parts = self.ranger_skill_parts(creature, skill)
        if parts is None:
            return None
        ids = {e.id for e in self._mine(creature, self.effects())}
        if any(skill in THIEF_CERTAIN.get(e, ()) for e in ids):
            return 100
        if self.creature(creature)[CREATURE_STATUS] not in STATUS_ABLE or any(skill in THIEF_BLOCKED.get(e, ()) for e in ids):
            return 0
        chance = sum(n for _, n in parts)
        if gear:
            chance = self.gear_skill(creature, skill, chance)
        return max(0, min(255, chance))

    def ranger_skills_now(self, creature: int) -> List[Tuple[str, int]]:
        """[(skill, chance), ...]: a ranger's move silently and hide in shadows as they stand
        (the stealth rule's, with what it wears), or [] without ranger levels."""
        out = [(THIEF_SKILLS[skill], self.ranger_skill_now(creature, skill)) for skill in (3, 4)]
        return [(name, n) for name, n in out if n is not None]

    def thief_skills_now(self, creature: int, skills: Tuple[int, ...] = ROLLED_SKILLS,
                         gear: bool = True) -> List[Tuple[str, int]]:
        """[(skill, chance), ...] for the skills the game rolls, as they stand now: with the
        equipment penalty, a worn belt's bonus (BELT_IN_FORCE), with GEAR a worn cloak's or boots'
        (gear_skill), 0 for a skill an effect rules out (or when the thief isn't Okay or New, or wears armour that isn't light: thief_heavy), 100
        for one an effect makes certain. Not the situation's bonus (a hard lock...). [] for
        someone without thief levels. `skills`: which (numbers in THIEF_SKILLS)."""
        rec = self.creature(creature)
        if len(rec) < CREATURE_SIZE:
            return []
        table = self.guest.read((self.load_seg + THIEF_TABLE_SEG) * 16 + THIEF_ARMOUR, 8)
        slots = self.thief_penalty_slots()
        penalty = any(item[ITEM_SLOT] in slots for _, item, _ in self._worn(creature))
        ids = {e.id for e in self._mine(creature, self.effects())}
        okay = rec[CREATURE_STATUS] in STATUS_ABLE and not self.thief_heavy(creature)
        belt = self.belt and any(item[ITEM_SLOT] == WAIST for _, item, _ in self._worn(creature))
        from . import kits
        kids = self.kit_ids(creature)
        out = []
        for skill in skills:
            parts = self.thief_skill_parts(creature, skill)
            if parts is None:
                return []
            chance = sum(n for _, n in parts) - (table[skill] if penalty and len(table) == 8 else 0)
            if belt and skill in BELT_SKILLS:
                chance += BELT_BONUS
            outdoors = self.outdoors(creature) if kits.SCOUT in kids else False
            for kid in kids:  # (an Assassin's, a Swashbuckler's...: no less than 0, as DSCLOG's PROBE_BELT)
                if kits.thief_skill(kid, skill, outdoors):
                    chance = max(0, chance + kits.thief_skill(kid, skill, outdoors))
            if gear:
                chance = self.gear_skill(creature, skill, chance)
            if any(skill in THIEF_CERTAIN.get(e, ()) for e in ids):
                chance = 100
            elif not okay or any(skill in THIEF_BLOCKED.get(e, ()) for e in ids):
                chance = 0
            out.append((THIEF_SKILLS[skill], max(0, min(255, chance))))
        return out

    def item_label(self, item: bytes, typ: bytes) -> str:
        """"Metal Long Sword +1": an item's material (when it has one), name and plus."""
        material = typ[0x08] & 0x0F if len(typ) == ITEM_TYPE_SIZE else len(MATERIALS)
        if len(typ) == ITEM_TYPE_SIZE and typ[0x08] & NO_MATERIAL and not material:
            material = len(MATERIALS)  # a ring, a body...: no material to name
        plus = struct.unpack("b", item[ITEM_PLUS:ITEM_PLUS + 1])[0]
        name = self.item_name(struct.unpack_from("<H", item, ITEM_NAME)[0])
        if plus and not name.endswith(f"{plus:+d}"):  # (a name such as "Sling +2" has it)
            name += f" {plus:+d}"
        return (f"{MATERIALS[material]} " if material < len(MATERIALS) else "") + name

    def party_items(self) -> List["ItemSeen"]:
        """Every item a party member has, worn or carried (itemwatch.py watches them)."""
        out = []
        for member in range(PARTY_SIZE):
            rec = self.creature(member)
            if len(rec) < CREATURE_SIZE or not rec[CREATURE_NAME]:
                continue
            for index, item, typ in self._worn(member):
                slot = item[ITEM_SLOT]
                out.append(ItemSeen(index, member, self.creature_name(member),
                                    EQUIP_SLOTS[slot] if slot < len(EQUIP_SLOTS) else None,
                                    self.item_label(item, typ), struct.unpack_from("<H", item, ITEM_TYPE)[0],
                                    bytes(item), bytes(typ)))
        return out

    def item_record(self, index: int) -> bytes:
        """An item's record by number, whoever has it now."""
        items = far_pointer(self.guest, self.ds, ITEMS_PTR)
        return self.guest.read(items + index * ITEM_SIZE, ITEM_SIZE)

    def equipment(self, creature: int) -> List[Tuple[Optional[str], str]]:
        """A creature's items: [(slot it's worn in or None if only carried, "Leather Chest Armor"), ...],
        worn items first, in the game's slot order."""
        out = [(item[ITEM_SLOT], self.item_label(item, typ)) for _, item, typ in self._worn(creature)]
        out.sort(key=lambda x: x[0])
        return [(EQUIP_SLOTS[slot] if slot < len(EQUIP_SLOTS) else None, name) for slot, name in out]

    def worn_in(self, creature: Optional[int], slot: int) -> List[bytes]:
        """The item records a creature wears in SLOT (an index of EQUIP_SLOTS)."""
        if creature is None:
            return []
        return [item for _, item, _ in self._worn(creature) if item[ITEM_SLOT] == slot]

    def wears_type(self, creature: Optional[int], item_type: int, slot: int) -> bool:
        """Whether a creature wears an item of ITEM_TYPE in SLOT."""
        return any(struct.unpack_from("<H", item, ITEM_TYPE)[0] == item_type for item in self.worn_in(creature, slot))

    def _worn(self, creature: int):
        """(item number, item record, type record) for each of a creature's items."""
        rec = self.creature(creature)
        if len(rec) < CREATURE_SIZE:
            return
        things = (self.load_seg + COMBATANTS_SEG) * 16 + COMBATANTS_OFF
        items = far_pointer(self.guest, self.ds, ITEMS_PTR)
        types = far_pointer(self.guest, self.ds, ITEM_TYPES_PTR)
        seen = set()
        for field in CREATURE_ITEM_LISTS:
            thing, = struct.unpack_from("<H", rec, field)
            if thing >= NO_ITEM:
                continue
            kind, index = struct.unpack("<Bh", self.guest.read(things + thing * 3, 3))
            if kind != THING_ITEM:
                continue
            while 0 <= index < NO_ITEM and index not in seen and len(seen) < 100:
                seen.add(index)
                item = self.guest.read(items + index * ITEM_SIZE, ITEM_SIZE)
                typ = self.guest.read(types + struct.unpack_from("<H", item, ITEM_TYPE)[0] * ITEM_TYPE_SIZE,
                                      ITEM_TYPE_SIZE)
                yield index, item, typ
                index, = struct.unpack_from("<h", item, ITEM_NEXT)

    def _mine(self, creature: int, effects: List[Effect]) -> List[Effect]:
        """The effects on a creature (effects name combatants)."""
        combatants = {c for c, i in self.combatants().items() if i == creature}
        if creature < PARTY_SIZE:
            combatants.add(creature)  # the party's combatant numbers are theirs
        return [e for e in effects if e.owner in combatants]

    def _prayer(self, creature: int, mine: List[Effect]) -> Optional[int]:
        """+1 under a Prayer from its own side, -1 from the other side's, None without."""
        prayer = next((e for e in mine if e.id == EFFECT_PRAYER), None)
        if prayer is None:
            return None
        source = self.combatant_creature(prayer.caster)
        same = source is not None and self.creature(source)[CREATURE_SIDE] == self.creature(creature)[CREATURE_SIDE]
        return 1 if same else -1

    def saves_now(self, creature: int) -> List[SaveNow]:
        """The five saves as the d20 roll needed now: the sheet's number less the modifiers the
        game's saving throw adds whatever the spell (rings, Blessed, Prayer, Barkskin, Spirit
        Armor, the save penalty, and CON on paralysis/poison/death saves). The rest depend on
        the spell or the caster (WIS against the mind, Protection from Fire...): see save_modifiers."""
        sheet, rec = self.sheet(creature), self.creature(creature)
        if len(sheet) < SHEET_SIZE or len(rec) < CREATURE_SIZE:
            return []
        mine = self._mine(creature, self.effects())
        ids = {e.id for e in mine}
        prayer = self._prayer(creature, mine)
        protection = self.protection(creature)
        from . import robes
        if robes.worn_plus(self._worn(creature)) >= robes.VEILED_PLUS:  # (the Ashen Robe's: against spells)
            protection = protection + [(1, "Veiled Robe")]
        con = rec[CREATURE_ABILITIES + 2]
        out = []
        for save in range(1, 6):
            parts: List[Tuple[int, str]] = []
            parts += protection
            if EFFECT_SAVE_PENALTY in ids:
                parts.append((-1, EFFECT_NAMES[EFFECT_SAVE_PENALTY]))
            if EFFECT_SPIRIT_ARMOR in ids and save != PPD_SAVE:
                parts.append((3, EFFECT_NAMES[EFFECT_SPIRIT_ARMOR]))
            if EFFECT_BARKSKIN in ids:
                parts.append((1, EFFECT_NAMES[EFFECT_BARKSKIN]))
            if EFFECT_BLESSED in ids:
                parts.append((1, EFFECT_NAMES[EFFECT_BLESSED]))
            if prayer is not None:
                parts.append((prayer, "Prayer"))
            if save == PPD_SAVE:
                if sheet[SHEET_RACE] in (DWARF, HALFLING):
                    parts.append((con * 2 // 7, f"{'dwarf' if sheet[SHEET_RACE] == DWARF else 'halfling'} CON {con}"))
                adjust = struct.unpack("b", self.guest.read(self.ds * 16 + SAVE_CON + con, 1))[0] if con < 26 else 0
                if adjust:
                    parts.append((adjust, f"CON {con}"))
            parts = [(n, why) for n, why in parts if n]
            base = sheet[SHEET_SAVES + save - 1]
            out.append(SaveNow(base, min(20, max(2, base - sum(n for n, _ in parts))), parts))
        return out

    def weapon_hits(self, creature: int) -> List[WeaponHit]:
        """THAC0 with each weapon the creature has ready (right hand, left hand, missile), as the
        game's attack works it out before the target is known (not from behind or backstabbing,
        nor the target's Blur); unarmed (item -1) when it has none."""
        rec = self.creature(creature)
        if len(rec) < CREATURE_SIZE:
            return []
        base = struct.unpack("b", rec[CREATURE_THAC0:CREATURE_THAC0 + 1])[0]
        mine = self._mine(creature, self.effects())
        ids = {e.id for e in mine}
        common = [(EFFECT_NAMES[eid], n) for eid, n in HIT_EFFECTS if eid in ids]
        prayer = self._prayer(creature, mine)
        if prayer is not None:
            common.append(("Prayer", prayer))
        from . import kits
        kids, shield = self.kit_ids(creature), self.holds_shield(creature)
        strength, dex = rec[CREATURE_ABILITIES], rec[CREATURE_ABILITIES + 1]
        table = lambda off, score: struct.unpack("b", self.guest.read(self.ds * 16 + off + score, 1))[0] \
            if score < 26 else 0
        weapons = []
        for index, item, typ in self._worn(creature):
            slot = item[ITEM_SLOT]
            if slot in WEAPON_HANDS + (MISSILE_SLOT,) and typ[0x0C] and typ[0x0D]:  # it has damage dice
                weapons.append((index, item, typ, slot))
        two_weapons = all(self.melee_weapon_in(creature, hand) for hand in WEAPON_HANDS)
        out = []
        order = {WEAPON_HANDS[0]: 0, WEAPON_HANDS[1]: 1, MISSILE_SLOT: 2}
        for index, item, typ, slot in sorted(weapons, key=lambda w: order[w[3]]):
            missile = slot == MISSILE_SLOT
            parts = [("DEX", table(DEX_MISSILE, dex))] if missile else [("STR", table(STR_TO_HIT, strength))]
            parts += common
            plus = struct.unpack("b", item[ITEM_PLUS:ITEM_PLUS + 1])[0]
            material = typ[0x08] & 0x0F
            if plus:
                parts.append(("weapon", plus))
            elif not typ[0x08] & 0x80 and material in MATERIAL_TO_HIT:
                parts.append((MATERIALS[material].lower(), MATERIAL_TO_HIT[material]))
            if two_weapons and not missile:
                parts.append(self.two_weapons(creature, slot))
            skill = 0
            halves = typ[0x0B] if missile else None  # (the game's rate of fire: the weapon's own)
            # the kit's (DSCLOG's KIT_TO_HIT, KIT_EXTRA): a Ravager's, a Brute's, an Arena Champion's,
            # a Ghetto Fighter's with a dagger, a Battle Dancer's dance (not the target's: a Wilderness
            # Avenger's against undead)
            from . import specialize as spec
            kind = spec.kind_of(struct.unpack_from("<H", item, ITEM_TYPE)[0])
            for kid in kids:
                kit = kits.champion(kid, shield, not missile)[0] \
                    + (kits.melee(kid, bool(typ[0x0F] & 0x40), kind) if not missile and not typ[0] & 2 else 0) \
                    + kits.extra(kid, self.dance.get(creature, 0)) \
                    + (kits.missile_to_hit(kid, kind, self.outdoors(creature)) if missile else 0) \
                    + (kits.POISONER_TO_HIT if kid == kits.POISONER else 0) \
                    + kits.ghetto_to_hit(kid, kind)
                if kit:
                    parts.append((kits.name(kid), kit))
            if self.wild.get(creature) is False:  # (DSCLOG's WILD_TO_HIT: a Wild Fury, or Gerakis)
                parts.append(("Wild Fighting failed", kits.WILD_TO_HIT))
            if self.rules & RULE_SPECIALIZE:  # (weapon specialization: DSCLOG's PROBE_ATTACKS)
                from . import specialize
                kind = struct.unpack_from("<H", item, ITEM_TYPE)[0]
                skill = specialize.skill(self.sheet(creature), kind)
                parts.append((specialize.SKILL_NAMES.get(skill, ""), specialize.to_hit(skill)))
                if missile:
                    halves = specialize.missile_attacks(halves, skill, kind, self.sheet(creature))
                elif skill == specialize.EXPERT and self.sheet(creature)[SHEET_ATTACKS] <= 2:
                    # (a Battle Mage's expertise: DSCLOG's EXPERT_HALVES)
                    halves = specialize.expert_attacks(self.sheet(creature)[SHEET_ATTACKS], skill, self.sheet(creature))
            if not missile and self.rules & RULE_KITS:  # (a Crusader's or Mind Warrior's extra attacks)
                have = self.sheet(creature)[SHEET_ATTACKS] if halves is None else halves
                if kits.warrior_attacks(have, self.sheet(creature)) != have:
                    halves = kits.warrior_attacks(have, self.sheet(creature))
            if missile and kind == kits.CHATKCHA and self.own_race(creature) == kits.THRI_KREEN:
                # (K'ratchek's chatkcha comes back as if she had several: DSCLOG's OWN_THROWS)
                halves = (typ[0x0B] if halves is None else halves) + kits.OWN_THROWS_MORE
            if not missile and self.wild.get(creature):
                # (Wild Fighting, its check passed: 1 more attack a round in melee; DSCLOG's WILD_HALVES)
                halves = (self.sheet(creature)[SHEET_ATTACKS] if halves is None else halves) + kits.WILD_HALVES
            if not missile and self.rules & RULE_TWO_WEAPONS and slot == WEAPON_HANDS[1]:
                # (AD&D's two weapons: the off hand one a round, the extra attacks the main hand's;
                # DSCLOG's OFF_HAND_HALVES)
                have = self.sheet(creature)[SHEET_ATTACKS] if halves is None else halves
                if have > 2:
                    halves = 2
            parts = [(why, n) for why, n in parts if n]
            out.append(WeaponHit(index, slot, self.item_label(item, typ), base - sum(n for _, n in parts), parts,
                                 skill, halves))
        if not out:
            parts = [("STR", table(STR_TO_HIT, strength))] + common
            if self.rules & RULE_NEW_SPELLS and CLAW_EFFECT in ids:
                parts.append((EFFECT_NAMES[CLAW_EFFECT], 1))  # (DSCLOG's NS_FIST)
            for kid in kids:  # (DSCLOG's KIT_TO_HIT and WILD_TO_HIT, unarmed too)
                kit = (kits.POISONER_TO_HIT if kid == kits.POISONER else 0) + kits.ghetto_to_hit(kid, None)
                if kit:
                    parts.append((kits.name(kid), kit))
            if self.wild.get(creature) is False:
                parts.append(("Wild Fighting failed", kits.WILD_TO_HIT))
            parts = [(why, n) for why, n in parts if n]
            out.append(WeaponHit(-1, -1, "unarmed", base - sum(n for _, n in parts), parts))
        return out

    def two_weapons(self, creature: int, slot: int) -> Tuple[str, int]:
        """The to-hit adjustment for an attack with the weapon in SLOT while two are ready (in
        melee), and what it's called. The game's: its DEX table for initiative, sign flipped and
        never below 0 (a bonus at DEX 5 or less). With RULE_TWO_WEAPONS, AD&D's: -2 main hand,
        -4 off hand, plus the DEX reaction adjustment, never above 0. Rangers: none, but with the
        rule only in light armour (DSCLOG's RG_TWO), a Justifier in any; a Twin-blade (kits.py) none with the rule, in
        light armour too."""
        dex = self.creature(creature)[CREATURE_ABILITIES + 1]
        sheet = self.sheet(creature)
        ranger = len(sheet) >= SHEET_FLAGS + 2 and struct.unpack_from("<H", sheet, SHEET_FLAGS)[0] & SHEET_FLAG_RANGER
        if not self.rules & RULE_TWO_WEAPONS:
            return f"two weapons at DEX {dex}", 0 if ranger else max(0, -self.dex_initiative(dex))
        hand = "off hand" if slot == WEAPON_HANDS[1] else "main hand"
        from . import kits
        if ranger and kits.JUSTIFIER in self.kit_ids(creature):
            return f"two weapons, {hand} (Justifier)", 0  # (in any armour)
        light = not self.heavy_armour_worn(creature)
        if ranger and light:
            return f"two weapons, {hand} (ranger)", 0
        kids = self.kit_ids(creature)
        for kid in (kits.TWIN_BLADE, kits.BATTLE_DANCER):
            if light and kid in kids:
                return f"two weapons, {hand} ({kits.name(kid)})", 0
        if slot not in WEAPON_HANDS or not self.melee_weapon_in(creature, sum(WEAPON_HANDS) - slot):
            return "two weapons", 0  # not a hand's weapon, or nothing to fight with in the other hand
        base = TWO_WEAPON_PENALTY.get(slot, -2)
        for kid in kids:  # (a Ghetto Fighter's: none in the main hand, -2 in the off hand)
            if kits.two_weapon_base(kid, base) != base:
                base, hand = kits.two_weapon_base(kid, base), f"{hand}, {kits.name(kid)}"
        return (f"two weapons, {hand} at DEX {dex}", min(0, base + self.dex_initiative(dex)))

    def heavy_armour_worn(self, creature: int) -> bool:
        """Armour worn that isn't light (not leather, and of a material: DSCLOG's HEAVY_WORN),
        a helm too: an armour piece (not a shield, nor bracers or a robe) on the arms, legs, head
        or chest."""
        from . import kits, restrict
        slots = {EQUIP_SLOTS.index(s) for s in ("arm", "legs", "head", "chest")}
        return any(item[ITEM_SLOT] in slots and len(typ) > 0x0F and restrict.is_armour(typ)
                   and typ[8] & 0x4F not in (kits.LEATHER, kits.NO_MATERIAL)
                   for _, item, typ in self._worn(creature))

    def melee_weapon_in(self, creature: int, slot: int) -> bool:
        """A melee weapon (its type's class 1, as the game counts weapons ready) in SLOT: not
        a shield, a bow or a sling."""
        return any(item[ITEM_SLOT] == slot and len(typ) > 0x0A and typ[0x0A] == 1
                   for _, item, typ in self._worn(creature))

    def missile_type(self, item_type: Optional[int]) -> bool:
        """A missile weapon's item type (its +00h, bit 2), as DSCLOG's KIT_MELEE tells one."""
        if item_type is None or not 0 <= item_type < 0x200:
            return False
        typ = self.guest.read(far_pointer(self.guest, self.ds, ITEM_TYPES_PTR) + item_type * ITEM_TYPE_SIZE, 1)
        return bool(typ[0] & 2)

    def two_handed_type(self, item_type: Optional[int]) -> bool:
        """An item type that takes both hands (its +0Fh, 40h), as DSCLOG's KIT_MELEE tells one."""
        if item_type is None or not 0 <= item_type < 0x200:
            return False
        typ = self.guest.read(far_pointer(self.guest, self.ds, ITEM_TYPES_PTR) + item_type * ITEM_TYPE_SIZE, ITEM_TYPE_SIZE)
        return len(typ) > 0x0F and bool(typ[0x0F] & 0x40)

    def holds_shield(self, creature: int) -> bool:
        """A shield in a hand (as DSCLOG's PROT_SCAN finds one)."""
        return any(len(typ) == ITEM_TYPE_SIZE and typ[0] & TYPE_SHIELD and item[ITEM_SLOT] in WEAPON_HANDS
                   for _, item, typ in self._worn(creature))

    def wears_boots(self, creature: int) -> bool:
        """Something worn on the feet (with the Options' rule, a move more in a fight)."""
        return any(item[ITEM_SLOT] == FOOT for _, item, _ in self._worn(creature))

    def ring_plus(self, creature: int) -> int:
        """The pluses of the rings a creature wears (see RING_TYPE), and of a cloak of
        protection (CLOAK_TYPE)."""
        total = 0
        for _, item, _ in self._worn(creature):
            plus = struct.unpack("b", item[ITEM_PLUS:ITEM_PLUS + 1])[0]
            kind, slot = struct.unpack_from("<H", item, ITEM_TYPE)[0], item[ITEM_SLOT]
            if plus > 0 and (kind == RING_TYPE and slot in FINGERS or kind == CLOAK_TYPE and slot == CLOAK_SLOT):
                total += plus
        return total

    def item_save(self, item: int, armour: bool) -> Optional["ItemSave"]:
        """What item ITEM needs on a d20 against the acid or corroding touch: the game's number
        (None: armour with no magical power, destroyed without a roll) and AD&D's (ACID_SAVES)."""
        rec = self.guest.read(far_pointer(self.guest, self.ds, ITEMS_PTR) + item * ITEM_SIZE, ITEM_SIZE)
        if len(rec) < ITEM_SIZE:
            return None
        kind = struct.unpack_from("<H", rec, ITEM_TYPE)[0]
        typ = self.guest.read(far_pointer(self.guest, self.ds, ITEM_TYPES_PTR) + kind * ITEM_TYPE_SIZE, ITEM_TYPE_SIZE)
        if len(typ) < ITEM_TYPE_SIZE:
            return None
        plus = struct.unpack("b", rec[ITEM_PLUS:ITEM_PLUS + 1])[0]
        power = struct.unpack("b", rec[ITEM_POWER:ITEM_POWER + 1])[0]
        material = typ[0x08] & 0x0F
        if typ[0x08] & NO_MATERIAL and not material:
            material = 6
        name, adnd = ACID_SAVES.get(material, ACID_SAVES[4])
        adnd -= plus + (1 if power else 0)
        own = (10 - power if power else None) if armour else 8 - plus
        return ItemSave(self.item_label(rec, typ), name, own, adnd, plus, bool(power))

    def protection(self, creature: int) -> List[Tuple[int, str]]:
        """What the creature's rings and cloak of protection add to its saving throws, as
        [(amount, why), ...]. The game's (with the patched game): every worn one's plus, as
        "Ring of Protection". With RULE_PROTECTION, AD&D's: the better ring only, and the cloak
        only without magical or metal armour (helms too) and without a shield."""
        if not self.rules & RULE_PROTECTION:
            ring = self.ring_plus(creature)
            return [(ring, "Ring of Protection")] if ring else []
        rings, cloak, blocked = [], 0, False
        for _, item, typ in self._worn(creature):
            plus = struct.unpack("b", item[ITEM_PLUS:ITEM_PLUS + 1])[0]
            kind, slot = struct.unpack_from("<H", item, ITEM_TYPE)[0], item[ITEM_SLOT]
            if kind == RING_TYPE:
                if slot in FINGERS and plus > 0:
                    rings.append(plus)
            elif kind == CLOAK_TYPE:
                if slot == CLOAK_SLOT and plus > 0:
                    cloak = plus
            elif kind in (BRACERS_TYPE, ROBE_TYPE):
                pass  # (not armour)
            elif len(typ) == ITEM_TYPE_SIZE:
                if typ[0] & TYPE_SHIELD:
                    blocked |= slot in WEAPON_HANDS
                elif slot in ARMOUR_SLOTS and typ[0x0F] & 0x80:
                    blocked |= plus > 0 or typ[0x08] & 0x4F == MATERIALS.index("Metal")
        out = [(max(rings), "Ring of Protection")] if rings else []
        if cloak and not blocked:
            out.append((cloak, "Cloak of Protection"))
        return out

    def kit_ids(self, creature: int) -> List[int]:
        """With kits, the creature's kits that count (kitpages.kit_ids: awake), else []."""
        if not self.rules & RULE_KITS:
            return []
        from . import kitpages
        return kitpages.kit_ids(self.sheet(creature))

    def own_race(self, creature: int) -> int:
        """With kits, the race of one of the game's own party given a feature of its own
        (kits.own_race: Gerakis, K'ratchek, Cilla), else 0."""
        if not self.rules & RULE_KITS:
            return 0
        from . import kits
        return kits.own_race(self.sheet(creature))

    def own_features(self, creature: int) -> List[str]:
        """The names of those features (kits.OWN_FEATURES), as the Effects screen lists them."""
        from . import kits
        return list(kits.OWN_FEATURES.get(self.own_race(creature), ()))

    def has_kit(self, creature: int, kid: int) -> bool:
        return kid in self.kit_ids(creature)

    def path_lost(self) -> bool:
        """No party member up is a Wayfinder, and one down (stunned to petrified; not Gone) is:
        Path-finder lost, the party's 1 less (DSCLOG's PATH_DOWN)."""
        from . import kits
        if self.path_finder():
            return False
        for m in range(PARTY_SIZE):
            rec = self.creature(m)
            if len(rec) > CREATURE_STATUS and 2 <= rec[CREATURE_STATUS] <= 7 and kits.WAYFINDER in self.kit_ids(m):
                return True
        return False

    def path_finder(self) -> bool:
        """A party member up (New or Okay) is a Wayfinder: the party's Path-finder (DSCLOG's
        PATH_UP: kits.PATH_MOVE, kits.PATH_INITIATIVE)."""
        from . import kits
        for m in range(PARTY_SIZE):
            rec = self.creature(m)
            if len(rec) > CREATURE_STATUS and rec[CREATURE_STATUS] <= 1 and kits.WAYFINDER in self.kit_ids(m):
                return True
        return False

    def kit(self, creature: int) -> Optional[str]:
        """With kits, the kits the creature took (kitpages.KITS), the oldest class's first, then the
        features of its own of one of the game's own party (kits.OWN_FEATURES), or None; an
        Elementalist's with its second sphere ("Elementalist (and water)"), a kit asleep with the
        level its class sleeps till."""
        if not self.rules & RULE_KITS:
            return None
        from . import kitpages, kits
        sheet = self.sheet(creature)
        names = []
        for kid, place, awake in kitpages.kits_of(sheet):
            name = kitpages.name_of(kid)
            second = kits.second_sphere(kid, sheet)
            if second is not None:
                name = f"{name} (and {SPHERE_NAMES[second]})"
            if not awake:  # (a human's who has changed class)
                name += (f", dormant until the {CLASS_NAMES[sheet[SHEET_CLASSES]].split(' (')[0].lower()} level "
                         f"passes {sheet[SHEET_LEVELS + place]}")
            names.append(name)
        names += kits.OWN_FEATURES.get(kits.own_race(sheet), ())  # (the game's own party's: Gerakis...)
        return "; ".join(names) or None

    def specializations(self, creature: int) -> List[Tuple[str, str]]:
        """With weapon specialization, (kind, skill) for each weapon kind the creature has chosen:
        "specialized", "mastery", "grand mastery", "expertise", or "not yet" for a dual-classed
        warrior whose warrior class isn't back yet; then a ranger's bow, chosen or not (DSCLOG's
        EF_LINES_OF)."""
        if not self.rules & RULE_SPECIALIZE:
            return []
        from . import specialize, weaponchoice
        sheet = self.sheet(creature)
        if len(sheet) < SHEET_SIZE:
            return []
        names = {**specialize.SKILL_NAMES, specialize.EXPERT: "expertise", specialize.PLAIN: "not yet"}
        out = []
        for k in sheet[SPEC_SLOTS:SPEC_SLOTS + SPEC_COUNT]:
            if 0 < k <= len(specialize.KINDS):
                skill = specialize.skill(sheet, weaponchoice.PLAIN[k - 1][0])
                out.append((specialize.KINDS[k - 1], names.get(skill, "")))
        bow = specialize.KINDS.index("bow")
        if bow + 1 not in sheet[SPEC_SLOTS:SPEC_SLOTS + SPEC_COUNT]:
            skill = specialize.skill(sheet, weaponchoice.PLAIN[bow][0])
            if skill not in (specialize.NONE, specialize.PLAIN):  # (a ranger's expertise)
                out.append(("bow", names.get(skill, "")))
        return out

    def thief_heavy(self, creature: int) -> bool:
        """With class restrictions, whether a character with a thief class wears armour that isn't
        light: no thief skills and no backstab (DSCLOG's THIEF_HEAVY; restrict.thief_heavy)."""
        if not self.rules & RULE_RESTRICT:
            return False
        from . import restrict
        worn = [typ for _, item, typ in self._worn(creature) if item[ITEM_SLOT] in ARMOUR_SLOTS]
        return restrict.thief_heavy(self.sheet(creature), worn)

    def no_spells(self, creature: int) -> bool:
        """With class restrictions, whether a multiclass preserver can't cast for the armour it
        wears (DSCLOG's PROBE_NO_CAST; restrict.no_spells)."""
        if not self.rules & RULE_RESTRICT:
            return False
        from . import restrict
        worn = [typ for _, item, typ in self._worn(creature) if item[ITEM_SLOT] in ARMOUR_SLOTS]
        return restrict.no_spells(self.sheet(creature), worn)

    def dex_ac(self, dex: int) -> int:
        """The game's AC adjustment for a DEX score."""
        if not 0 <= dex < 26:
            return 0
        return struct.unpack("b", self.guest.read(self.ds * 16 + DEX_AC + dex, 1))[0]

    def dex_initiative(self, dex: int) -> int:
        """The game's initiative adjustment for a DEX score."""
        if not 0 <= dex < 26:
            return 0
        return struct.unpack("b", self.guest.read(self.ds * 16 + DEX_INITIATIVE + dex, 1))[0]

    def initiative(self, count: int) -> List[Tuple[int, int]]:
        """(score, tie-break roll) for the first `count` creatures."""
        data = self.guest.read((self.load_seg + INITIATIVE_SEG) * 16 + INITIATIVE_OFF, count * 4)
        return [struct.unpack_from("<hh", data, i * 4) for i in range(len(data) // 4)]

    def level_hp_group(self, cls: int) -> Optional[int]:
        """The class's hit point group: 0 priests, 1 warriors, 2 wizards, 3 rogues and psionicists."""
        if not 0 < cls < 32:
            return None
        group = self.guest.read((self.load_seg + LEVEL_HP_SEG) * 16 + 0x10 + cls, 1)[0]
        return group if group < 4 else None

    def level_hp_rule(self, cls: int) -> Optional[LevelHp]:
        group = self.level_hp_group(cls)
        if group is None:
            return None
        return LevelHp(*self.guest.read((self.load_seg + LEVEL_HP_SEG) * 16 + group * 4, 3))

    def level_hp_minimum(self, con: int) -> int:
        return self.guest.read((self.load_seg + LEVEL_HP_SEG) * 16 + 0x38 + min(max(con, 0), 25), 1)[0]

    def level_hp_con_bonus(self, con: int) -> int:
        """Hit points a warrior gains per level for a CON score (others get at most +2)."""
        base = (self.load_seg + LEVEL_HP_SEG) * 16 + LEVEL_HP_CON_BONUS
        return struct.unpack("b", self.guest.read(base + min(max(con, 0), 25), 1))[0]

    def con_per_die(self, sheet: bytes, con: int) -> int:
        """With RULE_MULTI_HP, CON's bonus on each hit die of a character of more than one class:
        a warrior's (LEVEL_HP_CON_BONUS) if any class is a warrior's, else at most +2."""
        bonus = self.level_hp_con_bonus(con)
        warrior = any(self.level_hp_group(c) == WARRIOR_GROUP for c in sheet[SHEET_CLASSES:SHEET_CLASSES + 3] if c)
        return bonus if warrior else min(bonus, 2)

    def multiclass_con(self, sheet: bytes, con: int) -> Optional[int]:
        """con_share for SHEET and CON, from the game's hit point table (None: one class)."""
        groups = {c: self.level_hp_group(c) for c in sheet[SHEET_CLASSES:SHEET_CLASSES + 3] if c}
        last_die = {g: self.level_hp_rule(c).dice_levels for c, g in groups.items() if g is not None}
        return con_share(sheet, self.level_hp_con_bonus(con), groups, last_die)

    def sheet_at(self, index: int) -> bytes:
        """Character sheet number `index`."""
        return self.guest.read(far_pointer(self.guest, self.ds, SHEETS_PTR) + index * SHEET_SIZE, SHEET_SIZE)

    def creation_sheet(self) -> bytes:
        """The character being made on the creation screen."""
        return self.guest.read(far_pointer(self.guest, self.ds, CREATION_SHEET_PTR), SHEET_SIZE)

    def creation_abilities(self) -> Optional[List[int]]:
        """The abilities the creation screen shows, STR to CHA: in the creature record after the
        creation sheet (None if they don't look like abilities)."""
        at = far_pointer(self.guest, self.ds, CREATION_SHEET_PTR) + SHEET_SIZE + CREATURE_ABILITIES
        values = list(self.guest.read(at, 6))
        return values if len(values) == 6 and all(3 <= v <= 25 for v in values) else None

    def race_adjustment(self, race: int, ability: int) -> int:
        if not 0 < race < 16 or not 0 <= ability < 6:
            return 0
        addr = (self.load_seg + CREATION_SEG) * 16 + CREATION_RACE_OFF + race * 6 + ability
        return struct.unpack("b", self.guest.read(addr, 1))[0]

    def class_minimum(self, cls: int, ability: int) -> int:
        """The least an ability may be for a class on the creation screen (17 for its prime requisite)."""
        if not 0 < cls < 16:
            return 0
        prime, least = struct.unpack("<hB", self.guest.read(
            (self.load_seg + CREATION_SEG) * 16 + CREATION_CLASS_OFF + cls * 3, 3))
        return CREATION_PRIME_MINIMUM if prime == ability else least

    def item_breaks(self, item: int, item_type: int) -> bool:
        """Whether a weapon can break: the game's rule for non-magical wood, bone, stone and obsidian."""
        rec = self.guest.read(far_pointer(self.guest, self.ds, ITEMS_PTR) + item * ITEM_SIZE, ITEM_SIZE)
        typ = self.guest.read(far_pointer(self.guest, self.ds, ITEM_TYPES_PTR) + item_type * ITEM_TYPE_SIZE,
                              ITEM_TYPE_SIZE)
        if len(rec) < ITEM_SIZE or len(typ) < ITEM_TYPE_SIZE:
            return False
        return not typ[0x08] & 0x80 and rec[0x14] == 0 and rec[0x0F] == 0 and typ[0x08] & 0x0F <= 3

    def weapon(self, item: int, item_type: int) -> Optional[Weapon]:
        if item < 0 or item_type < 0:
            return None
        rec = self.guest.read(far_pointer(self.guest, self.ds, ITEMS_PTR) + item * ITEM_SIZE, ITEM_SIZE)
        typ = self.guest.read(far_pointer(self.guest, self.ds, ITEM_TYPES_PTR) + item_type * ITEM_TYPE_SIZE,
                              ITEM_TYPE_SIZE)
        if len(rec) < ITEM_SIZE or len(typ) < ITEM_TYPE_SIZE:
            return None
        return Weapon(self.item_name(struct.unpack_from("<H", rec, ITEM_NAME)[0]), typ[0x0D], typ[0x0C], struct.unpack("b", typ[0x0E:0x0F])[0],
                      struct.unpack("b", rec[0x14:0x15])[0], typ[0x08] & 0x0F, bool(typ[0x08] & 0x80))

    def weapon_name(self, w: Weapon) -> str:
        material = MATERIALS[w.material] + " " if w.material < len(MATERIALS) and w.material != 4 else ""
        return f"{material}{w.name}" + (f" {w.plus:+d}" if w.plus else "")
