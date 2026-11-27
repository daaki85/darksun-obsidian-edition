"""The dice log for Wake of the Ravager (the port's step 3).

The sequel's helper (DSCLOG2, dos/dsclog2.asm) records the rolls in DSCLOG's ring layout, and every roll
site the sequel's fights use has the same code after its rand() call as Shattered Lands' (the dice log
names a roll by that code: playtest/ravring.py's corpus, 2026-11-19). So the dice log is Shattered
Lands' (dicelog.DiceLog), run with:

  * the sequel's layout (LAYOUT): game.py's addresses and record offsets, and the copies other modules
    imported, rebound to the sequel's values while it is attached (apply_layout; restore_layout puts
    Shattered Lands' back). Record offsets come from ravager.creature_field, sheet_field and
    item_field (each checked in a running game); a Shattered Lands field the sequel hasn't is left out
    of the profile, so whatever reads it isn't ported yet (the mod's age, weapon specs and starting
    roll have places of their own: SHEET_AGE, SPEC_SLOTS, the Loader's 48h sheet).
  * a read-only view of the game's memory (ReadOnlyGuest): Shattered Lands' features write to DSCLOG's
    header past +146 (in DSCLOG2 that is code) and to the game's records by its layouts, so every write
    is dropped (and counted) until a feature is ported with writes of its own: so far only the spell
    slots' lines for the USE screen (DSCLOG2's SLOTS_TEXT, by its header's +148: `writable`).
  * RavDiceLog: the sequel's helper's signature, and none of Shattered Lands' side features after the
    rolls (its people, items and screens), only the rolls' lines and the fight's tally.
"""

import struct
import sys
from contextlib import contextmanager
from typing import Dict, Iterator, List, Optional, Tuple

from . import aging, combatlog, dicelog, dust, ghost, shopstock, startgear, game, hitchance, hover, itemgate, journal, kitpages, kits, \
    keywatch, labels, loot, monsters, moveback, psiblast, quicksave, ravager, ravfirstweapon, ravkitstart, ravspells, ring, rings, \
    gff, shadows, sizes, spellarrows, squares, stealth, pickpocket, targeting, textlog, usable, weaponchoice

HDR_SIG = b"DSCLOGR1"

# game.py's names -> the sequel's values (the rest of game.py's addresses are Shattered Lands' until
# found: what reads them isn't ported yet)
# The sequel's effects are numbered otherwise (its list alphabetical: effect_names): Shattered Lands'
# numbers the log's rules use, by name in the sequel's list. Where the sequel's list has a name twice
# (Hasted 42 and 51, Slowed 52 and 91) the one in alphabetical place is taken (unverified). The mod's
# own effects (Cat's Grace, Erdlu Claw, Fogbolt, Friends, the stinkpot's Nauseated) and SL's save
# penalty aren't in the sequel: numbers it never uses (NO_EFFECT and on), so they never match.
NO_EFFECT = 240
EFFECTS: Dict[str, object] = {
    "PARALYZED_EFFECT": 69, "MIRROR_EFFECT": 46, "AFRAID_EFFECT": 35, "ENLARGE_EFFECT": 32,
    "HASTED_EFFECT": 42, "SLOWED_EFFECT": 91, "FIRE_SHIELD_EFFECT": 38, "BLUR_EFFECT": 13,
    "BIOFEEDBACK_EFFECT": 8, "LOW_RESISTANCE_EFFECT": 61, "MIND_BAR_EFFECT": 64, "AFFINITY_EFFECT": 3, "BODY_WEAPONRY_EFFECT": 14,
    "EFFECT_BLESSED": 9, "EFFECT_BLIND": 10, "EFFECT_DETECT_INVIS": 25, "EFFECT_INVISIBLE": 53,
    "EFFECT_INVIS_UNDEAD": 54, "EFFECT_PROT_EVIL": 75, "EFFECT_PROT_COLD": 73, "EFFECT_PROT_FIRE": 77,
    "EFFECT_PROT_LIGHTNING": 78, "EFFECT_FIRE_SHIELD": 38, "EFFECT_SPIRIT_ARMOR": 94, "EFFECT_BARKSKIN": 6,
    "EFFECT_PRAYER": 72, "EFFECT_FLESH_ARMOR": 40, "EFFECT_VESTMENTS": 104, "EFFECT_BRAVE": 18,
    # the AC's effects (game.attack_ac, the chance to hit): Armor, Bio-Feedback, Shielded, Dispel Evil, Displaced
    "EFFECT_IMPROVED_AC": 5, "EFFECT_BIOFEEDBACK": 8, "EFFECT_SHIELDED": 89, "EFFECT_DISPEL_EVIL": 28,
    "EFFECT_DISPLACEMENT": 29,
    "EFFECT_SAVE_PENALTY": NO_EFFECT, "STINK_EFFECT": NO_EFFECT + 5,
    # the new spells' (ravspells: 320-325, their effects the records 113-116 the Loader fills in)
    "GRACE_EFFECT": ravspells.GRACE_EFFECT, "CLAW_EFFECT": ravspells.CLAW_EFFECT,
    "FOG_EFFECT": ravspells.FOG_EFFECT, "FRIENDS_EFFECT": ravspells.FRIENDS_EFFECT,
    "GRACE_SPELL": ravspells.GRACE, "CLAW_SPELL": ravspells.CLAW, "FOG_SPELL": ravspells.FOG,
    "REFLECT_SPELL": ravspells.REFLECT, "SPOOK_SPELL": ravspells.SPOOK, "FRIENDS_SPELL": ravspells.FRIENDS,
    "NEW_SPELLS": dict(ravspells.SPELLS), "NEW_SPELL_LEVELS": dict(ravspells.LEVELS),
    "INITIATIVE_EFFECTS": {10: -2, 42: 2, 91: -2},  # Blind, Hasted, Slowed
    "HALVING_EFFECTS": ((77, 0x02), (73, 0x04), (78, 0x80), (38, 0x06)),  # Prot Fire, Cold, Lightning; Fire Shield
    "HIT_EFFECTS": ((9, 1), (22, -1), (91, -4), (106, 1)),  # Blessed, Cursed, Slowed, Weapon Grafted
    # the effects that rule thief skills out or make one certain (game.THIEF_BLOCKED, THIEF_CERTAIN): SL's
    # by name in the sequel's numbers (SL's 25, Mirror Images, is the sequel's Detect Invisible, which had a
    # thief in Tyr hiding at 0): Berserk 7 and 102, Blind 10, Confused 21, Afraid 35, Feebleminded 37,
    # Fire Shielded 38, Mirror Images 46, Paralyzed 69, Slowed 52 and 91, Weapon Grafted 106; Detect Traps
    # 26, Invisible 53
    "THIEF_BLOCKED": {7: tuple(range(8)), 102: tuple(range(8)), 10: (0, 1, 2, 3, 4, 6, 7), 21: tuple(range(8)),
                      35: tuple(range(8)), 69: tuple(range(8)), 52: (0,), 91: (0,), 38: (0, 4), 46: (4,),
                      106: (0, 1, 6), 37: (7,)},
    "THIEF_CERTAIN": {26: (2,), 53: (4,)},
    "POWER_EFFECT_NAMES": {69: "Paralysing attack", 27: "Disease attack", 71: "Poison attack"},
}
# Its effects' names: 31-byte records in the program's data at load + 3C870h (its file's 41A70h), the
# name in the first 29 bytes, EFFECT_COUNT_ALL of them (some numbers unused: an empty name)
EFFECT_RECORDS, EFFECT_RECORD, EFFECT_COUNT_ALL = 0x3C870, 31, ravspells.FRIENDS_EFFECT + 1  # (113 the game's, then the new spells')


def effect_names(guest, load: int) -> Dict[int, str]:
    """The sequel's effect names by number, as its program holds them ({} if they don't read as names)."""
    data = guest.read(load * 16 + EFFECT_RECORDS, EFFECT_RECORD * EFFECT_COUNT_ALL)
    out = {}
    for n in range(EFFECT_COUNT_ALL):
        raw = data[n * EFFECT_RECORD:n * EFFECT_RECORD + 29].split(b"\0", 1)[0]
        if not all(32 <= c < 127 for c in raw):
            return {}
        if raw:
            out[n] = raw.decode("ascii")
    return out if out.get(5) == "Armor" else {}


RAV_ITEM_TYPE, RAV_ITEM_SLOT, RAV_ITEM_PLUS = 0x0A, 0x13, 0x16  # (the sequel's item fields, as DSCLOG2's)
ADDRESSES: Dict[str, object] = {
    "DGROUP": ravager.DGROUP,
    "CREATURES_PTR": ravager.CREATURES_PTR, "SHEETS_PTR": ravager.SHEETS_PTR, "ITEMS_PTR": ravager.ITEMS_PTR,
    "ITEM_TYPES_PTR": 0x19CD,  # (ravds --fuzzy: 40 uses agree)
    "CREATURE_SIZE": ravager.CREATURE_SIZE, "SHEET_SIZE": ravager.SHEET_SIZE, "ITEM_SIZE": ravager.ITEM_SIZE,
    "WHOSE_TURN": ravager.WHOSE_TURN, "REGION": 0x140C, "EFFECT_COUNT": 0x2100,
    "FINE_BOW_NAME": ravager.FINE_BOW_NAME,  # (the Spellarcher's Fine Bow: DSCLOG2's FINE_HIT)
    # the monsters' poison, a Poisoner's first hits (DSCLOG2's POISON_HIT): the sequel's 273 and 274 are
    # Shattered Lands' 176 and 177 by their records
    "POISON_POWERS": {273: "Poison (10 damage)", 274: "Poison (30 damage)"}, "POISON_DAMAGE": {273: 10, 274: 30},
    # the fight's combatants, 3 bytes each (kind, the creature's number): the sequel's code reads them
    # as selector 388h at C34h (SL's 360h at C37h), selector 388h being the load segment + 3F49h
    "COMBATANTS_SEG": 0x3F49, "COMBATANTS_OFF": 0xC33,
    # each creature's initiative (score, tie-break: words), selector 308h at DCh in the sequel's code
    # (its 5B7F6h: SL's 37BDh:D9h), selector 308h being the load segment + 3C4Fh
    "INITIATIVE_SEG": 0x3C4F, "INITIATIVE_OFF": 0xDC,
    # ... and each creature's facing, a byte at +5Eh there (the attack set-up's "cmp byte es:[bx+5Eh],0"
    # with selector 308h, 5CA36h; SL's +5Bh): an attack from behind (hitchance.predict)
    "FACING_OFF": 0x5E,
    # a fight on: the game's flag, a byte at DS:13FAh in the sequel (16 uses of SL's word at 1168h matched by
    # their code: "cmp byte [13FAh],0"; RavGameData reads the byte), and the fight's state at 3C10h:19h
    # (the main loop's "mov ax,3C10h / mov es,ax / cmp word es:[19h],0", SL's 377Eh)
    "IN_COMBAT": 0x13FA, "FIGHT_STATE_FROM_DS": ravager.DGROUP - 0x3C10,
    # a creature's status (+14h) by name: the sequel's names, in its own order (the far pointers at
    # DS:1463h to "New" ... "Gone", 2026-11-25): Animated and Petrified before Dead (SL's Dead 5, Animated 6,
    # Petrified 7); the dice log's and psiblast's words for one
    "STATUS_NAMES": {0: "New", 1: "Okay", 2: "Stunned", 3: "Out Cold", 4: "Dying", 5: "Animated",
                     6: "Petrified", 7: "Dead", 8: "Gone"},
    # the party's money, a dword at selector 2E8h:357h (the shop's pay, 91021h; SL's 3781h:357h), selector
    # 2E8h the load segment + 3C13h (the sequel's segment table, the load + 45E8h:selector)
    "MONEY_SEG": 0x3C13,
    # an item's power a word (item_field: SL's byte at 0Fh, the sequel's word at 10h; game.item_power)
    "POWER_BYTES": 2,
    # the game's clock: its scale (a byte) and a far pointer to the dword (ravds: SL's 9B70h, 9B72h + 9Ah;
    # read in play: scale 1, 406 s into a new game's first fight)
    "GAME_TIME_SCALE": 0x9C0A, "GAME_TIME_PTR": 0x9C0C,
    # the dialogue window's replies (its input, 87BA0h: SL's 7CE83h, the same code): each copied to DS:6356h +
    # n x 33h (SL's 5537h), the row clicked DS:25BAh (FFh till then; SL's 1F0Ah), the list's scroll DS:6321h
    # (5502h); the thing a script was started on (who is talked to), the load + 3C13h at 365h (SL's 3781h,
    # the same offset: "mov ax,3C13h / mov es,ax / mov es:[365h],di" at BEA4h)
    "REPLY_CHOSEN": 0x25BA, "REPLY_SCROLL": 0x6321, "REPLY_TEXTS": 0x6356, "TALK_SEG": 0x3C13,
    # the event queues (far pointers, then their counts: SL's 2FBEh and 2FC6h; ravds), 11h bytes an event,
    # an effect's end kind 7 there with its owner and handle (the queue routines at 2C4FCh on: "imul eax,11h")
    "EVENT_QUEUE": 0x2A63, "EVENT_COUNT": 0x2A6B,
    # the rules' small tables in the data segment, each found once by its bytes, each SL's + 70h
    "DEX_AC": 0x0866, "DEX_INITIATIVE": 0x084C, "DEX_MISSILE": 0x084C, "SAVE_CON": 0x0880,
    "SAVE_WIS": 0x089A, "STR_DAMAGE_TABLE": 0x0818, "STR_TO_HIT": 0x0832,
    # the AC function keeps the AC after armour in [BP-4] (its adjustments in [BP-6]: SL's SI)
    "AC_ARMOUR_LOCAL": -4,
    # the attack's count of the attacker's attacks made this round: [BP-16h] (5D04Ch, SL's [BP-14h]), its
    # [BP-14h] what the damage roll adds to the dice (DSCLOG2's STAB_TIMES)
    "ATTACKS_MADE_LOCAL": -0x16,
    # the attack set-up's locals (5C5E1h, SL's 58019h): the THAC0 [BP-1Eh] (SL's [BP-20h]), the weapon's bonus
    # [BP-8], from behind and backstab bytes [BP-19h] and [BP-21h] (SL's words [BP-1Ah], [BP-24h]), the natural
    # attacks' set [BP-20h] (SL's [BP-22h]), the weapons ready [BP-16h] (the dice log's THAC0 line)
    "SETUP_THAC0_LOCAL": -0x1E, "SETUP_BONUS_LOCAL": -8, "SETUP_REAR_LOCAL": -0x19, "SETUP_BACKSTAB_LOCAL": -0x21,
    "SETUP_NATURAL_LOCAL": -0x20, "SETUP_READY_LOCAL": -0x16, "SETUP_FLAG_MASK": 0xFF,
    # the difficulty, a DS word (monsters' to hit: the set-up's "mov ax,[143Ah] / dec ax", 5C9C9h; SL's 11AEh)
    "DIFFICULTY": 0x143A,
    # spell slots left: a member's 22h bytes from DS:446Ah, a wizard level L at +L-1, a priest's from
    # +0Bh (each level's byte at SLOTS_LEFT + level, as SL's); the slot rules each SL's + 0Ch (ravds)
    "SLOTS_LEFT": {"Wizard": 0x4469, "Priest": 0x4474}, "SLOTS_STRIDE": 0x22,
    "SLOT_CLASS_RULES": 0x0670, "SLOT_RULES": 0x0684,
    # the thief skills' table (base, race, DEX limits, the armour penalty): its bytes at the sequel's
    # file offset 49BB0h, the load + 449Bh:0 (SL's 3FAAh)
    "THIEF_TABLE_SEG": 0x449B,
    # ... its race rows two longer (16 bytes), so what follows them each SL's + 10h
    "THIEF_DEX_LOW": 0xA0, "THIEF_DEX_HIGH": 0xA8, "THIEF_DEX_TOP": 0xB0, "THIEF_ARMOUR": 0xB8,
    "THIEF_PENALTY_LIST": 0xE0,  # (its slots list: the thief_slots patch at 49C90h)
    # the active effects, 10 bytes each (SL's record): selector 370h at 24Dh in the sequel's code (its
    # Share Strength loop, 61A87h), selector 370h being the load segment + 3E71h (SL's 3BF6h:106h)
    "EFFECTS_SEG": 0x3E71, "EFFECTS_OFF": 0x24D,
    # SL's helm types aren't the sequel's (its 5 is Scale Armor): RavGameData.counted_ac has its own
    "HELM_TYPES": (),
    # the Cloak and Boots of Elvenkind: the party transfer's (the mod's types in the sequel, ravager.mod_type)
    "ELVEN_CLOAK_TYPE": ravager.mod_type(game.ELVEN_CLOAK_TYPE),
    "ELVEN_BOOTS_TYPE": ravager.mod_type(game.ELVEN_BOOTS_TYPE),
    "BACK_GIRDLE_TYPE": ravager.mod_type(game.BACK_GIRDLE_TYPE),  # (the dice log's magic resistance
    "URNST_GIRDLE_TYPE": ravager.mod_type(game.URNST_GIRDLE_TYPE),  # line and its girdles: SL's numbers
    "MR_AMULET_TYPE": ravager.mod_type(game.MR_AMULET_TYPE),  # read 0% on a sequel wearer)
    "CAHULAKS_TYPE": 24, "CAHULAKS_TYPES": frozenset((24,)),  # (the sequel's Cahulaks, OBJEX.GFF; no metal or obsidian ones)
    # the stinkpots (DSCLOG2's STINKPOTS): the Staff Sling's type, its Nauseated (ravager.NAUSEATED), the
    # save against Stinking Cloud (the sequel has no monster poison power as SL's 176)
    "STAFF_SLING_TYPE": 98, "STINK_EFFECT": ravager.NAUSEATED, "STINK_SAVE_POWER": 22,
    # the powers that can destroy an item (its power handler's switch, 656ECh: 103 the weapon then the
    # armour, 275 and 283 the armour, 284 the weapon; SL's 178, 186, 187), as the dice log names them
    # the hit point table (dice by class group, CON's bonus at +52h): SL's own bytes, at the load + 45BEh
    # (the most hit points' 4D0h:52h; SL's 40B1h)
    "LEVEL_HP_SEG": 0x45BE,
    # the creation screen (the dice log's 4d4 of each try, DSCLOG2's RL_TRY): the sheet being made, DS:1429h
    # (SL's 119Ch), its creature DS:142Dh (SL's 11A0h: in the sequel not straight after the sheet,
    # RavGameData.creation_abilities), the races' adjustments at the load + 3E4Fh:120h (the sequel's
    # selector 360h; SL's 38D4h:14Dh, the same 96 bytes found in the file)
    "CREATION_SHEET_PTR": 0x1429, "CREATION_CREATURE_PTR": 0x142D, "CREATION_SEG": 0x3E4F, "CREATION_RACE_OFF": 0x120,
    # ages (aging.py): the age alone at the sheet's +41h, a byte the sequel's program never reads or
    # writes (no instruction with its offset on a sheet; 0 in every sheet of a new game and the saves,
    # 2026-11-22); +3Dh and +3Fh hold the kit and the second sphere (MOD_BYTES); the weapon specs and
    # the starting age's roll (SL's +14h..+16h) in the three bytes the Loader's copy adds, +42h..+44h
    # (ravager.SHEET_SIZE 48h, sheet_field)
    "SHEET_AGE": 0x41, "AGE_PLAIN": True, "SPEC_SLOTS": ravager.sheet_field(game.SPEC_SLOTS),
    # four more weapon specs past SL's levels (a gladiator's 5th to 8th, the owner's 2026-11-26): +45h..+47h,
    # the rest of the Loader's widening (game.spec_more; DSCLOG2's SPEC_MORE)
    "SPEC_MORE": ravager.SPEC_MORE,
    "ITEM_ATTACKS": {103: "Crystal Brittle", 275: "corroding touch", 283: "corroding touch",
                     284: "corroding touch"},
}
# The mod's sheet bytes, by the names that hold them in Shattered Lands' layout (+43h the kit byte, +45h
# the second sphere and the new spells known), at the sequel's +3Dh and +3Fh, where the party transfer
# copies them (as CHARTRAN does; the Loader's copy of the game reads the sound words below them as
# bytes: ravager's sound_3c, sound_3e). The kits' rules are DSCLOG2's KITS; the second sphere and new spells are only kept.
MOD_BYTES = {"KIT_SHEET": (game, "KIT_SHEET"), "NEW_KNOWN_SHEET": (game, "NEW_KNOWN_SHEET"),
             "KIT_BYTE": (kitpages, "KIT_BYTE"), "SPHERE2": (kits, "SPHERE2")}


def _new_known() -> Dict[int, Tuple[int, int]]:
    """game.NEW_KNOWN with its sheet offsets the sequel's."""
    return {ravspells.FIRST + (spell - game.GRACE_SPELL): (ravager.sheet_field(at), bit)
            for spell, (at, bit) in game.NEW_KNOWN.items()}


OFFSET_KINDS = (("CREATURE_", ravager.creature_field), ("SHEET_", ravager.sheet_field),
                ("ITEM_", ravager.item_field))
NOT_OFFSETS = {"CREATURE_SIZE", "SHEET_SIZE", "ITEM_SIZE", "ITEM_TYPE_SIZE", "ITEM_NAME_SIZE",
               "SHEET_FLAG_GLADIATOR", "SHEET_FLAG_RANGER", "ITEM_TYPES_PTR", "ITEM_NAMES_PTR"}


def layout() -> Dict[str, int]:
    """game.py's name -> the sequel's value, for every name the profile changes."""
    out = dict(ADDRESSES, **EFFECTS)
    for name, (module, sl_name) in MOD_BYTES.items():
        out[name] = ravager.sheet_field(getattr(module, sl_name))
    out["NEW_KNOWN"] = _new_known()
    for name, value in vars(game).items():
        if name in NOT_OFFSETS or name in out or not isinstance(value, int) or isinstance(value, bool):
            continue
        for prefix, field in OFFSET_KINDS:
            if name.startswith(prefix):
                mapped = field(value)
                if mapped is not None:
                    out[name] = mapped
    return out


# The colours the panel and the labels may take (combatlog.nearest: SL's 16-223, its 224-255 cycling for
# fire and water). The sequel cycles only 1-15: its 224-253 are the interface's (232-239 its blue-greys,
# the panel's stone and well; 240-253 greys), the same in Tyr's street and in the Roost (2026-11-21).
PALETTE_LAST = 253

# The kits' saves in the sequel's spell numbers (DSCLOG2's KIT_CHARMS and PROT_SPELL_LAST): a Myrmidon's
# charms (Charm Person, Charm Monster, Dominate, Mass Charm, Charm Mammal, the psionic Domination and Mass
# Domination; RESOURCE.GFF's names) and a Sentinel's spells (the wizards' and priests', its psionic powers
# EBh on)
RAV_CHARMS = (2, 39, 61, 94, 131, 255, 256)
RAV_SPELL_LAST = 0xEA
# ... and the kits' spells in the sequel's numbers (ravager.RAV_*: DSCLOG2's CURE_DICE, AV_CAUSES, AV_HEALS,
# AV_HARMS), for the dice log's kit parts of a cure's and a Cause Wounds' lines (kits.cure_bonus, cure_die,
# harm_bonus) and kits.arc_level's and sky_level's wizard and priest spells (the new spells 320-325)
RAV_KIT_SPELLS = (
    ("WIZARD_LAST", ravager.RAV_WIZARD_LAST), ("NEW_WIZARD_SPELLS", ravager.RAV_NEW_WIZARD_SPELLS),
    ("CURE_LIGHT", ravager.RAV_CURE_LIGHT), ("CURE_SERIOUS", ravager.RAV_CURE_SERIOUS),
    ("CURE_CRITICAL", ravager.RAV_CURE_CRITICAL), ("BLOOD_FLOW", ravager.RAV_BLOOD_FLOW),
    ("CURE_DICE", ravager.RAV_CURE_DICE), ("AVENGER_NO_HEAL", ravager.RAV_AVENGER_NO_HEAL),
    ("CAUSE_LIGHT", ravager.RAV_CAUSE_LIGHT), ("CAUSE_SERIOUS", ravager.RAV_CAUSE_SERIOUS),
    ("CAUSE_CRITICAL", ravager.RAV_CAUSE_CRITICAL), ("NO_HARM", ravager.RAV_NO_HARM),
    ("CAUSE_DICE", ravager.RAV_CAUSE_DICE))
# The sequel's cures' dice calls, by the code after them (dicelog.SPELL_HANDLER_RETURNS: the handler's own
# bonus), in the patched game: Cure Light Wounds' 1d8 and Blood Flow's 2d6 healing (66542h, then DSCLOG2's
# KIT_CURE, site 206, where the game had "push ax / jmp 65811h"), Cure Serious Wounds' 2d8 + 1 (6649Eh), Cure
# Critical Wounds' 3d8 + 3 (664BCh)
RAV_SPELL_HANDLER_RETURNS = (
    (bytes.fromhex("83c404cdf5ce90"), 0),
    (bytes.fromhex("83c40440e9a000"), 1),
    (bytes.fromhex("83c404050300e9"), 3),
)
RAV_POISON_POWER = 273  # (a Poisoner's hit's poison: DSCLOG2's RAV_POISON_POWER, kits.POISON_POWER's)

# Choosing an enemy with Tab, the ring and the chance to hit under the pointer (targeting.py, rings.py,
# hover.py): the sequel's map things (DS:67BBh, 25h bytes; the feet +0Ah, +0Ch; its finder, 29DBDh, reads
# the flags +0, left +3, top +5, rise +0Eh, picture +10h, width +13h and height +14h, unsigned), the view
# DS:1408h, the pointer DS:A109h, its mode DS:1440h (the routine setting it, 2037Bh; SL's 11B8h), the
# thing under it DS:0DADh and the map up DS:0DABh (the routine lighting it, 21060h; SL's 0BCBh, 0BC9h),
# the eight directions' byte DS:0442h (the direction routine, 1109Dh: "cmp byte [0442h],1"); the party's
# foes those on sides 7-11 (rings.HOSTILE_SIDES: the creature's +15h, the game's own mask 0F80h at 21112h,
# the figure under the pointer coloured as a foe)
RAV_TARGETING = {
    targeting: {"MAP_THINGS": 0x67BB, "MAP_THING_SIZE": 0x25, "MAP_FEET": 0x0A, "CAMERA": 0x1408},
    hover: {"UNDER": 0x0DAD, "ON_MAP": 0x0DAB, "MODE": 0x1440, "MAP_RISE": 0x0E, "MAP_PICTURE": 0x10,
            "MAP_WIDTH": 0x13, "MAP_HEIGHT": 0x14, "MAP_SIZES": "<BB"},
    usable: {"POINTER": 0xA109},
    hitchance: {"EIGHT_WAYS": 0x0442},
    rings: {"STATUS_DEAD": 7, "HOSTILE_SIDES": 0xF80},
    # the map up (SL's DS:0BC9h word; hover's ON_MAP here): the combat log's panel is drawn only while it is
    # 1 (DiceLog._map_up), and SL's address read 0A2Eh in the sequel, so L never showed the panel
    quicksave: {"SCREEN_IS": 0x0DAB},
}
# The ring's colours: the sequel cycles 1-31 (water, flame, a turn's marker) and its street's floor has
# greys up to 255 (WALL SHADOWS' WS_FIRST, WS_LAST)
RED_FIRST, RED_LAST = 32, 255

# Looting with T and selling with S (loot.py, sell.py; DSCLOG2's LOOT_KEY, SELL_KEY), their item moves made
# by the Loader as in Shattered Lands (pickpocket's, ring's; the item gate held, itemgate.py), on the
# sequel's words: the free list of things DS:56EFh and the count of them out DS:55C6h (SL's 4D72h, 4C48h:
# the allocator's "push 56EFh / inc word [55C6h]", 23234h, 23252h, as SL's 1FC73h, 1FC91h), the free item
# records DS:5AF3h (SL's 4D76h: 23483h, 2349Ch), the container whose window is open DS:05D6h (SL's 05E6h:
# 607E8h "mov word [5D6h],270Fh", SL's 5BBC0h), dying and dead 4 and 7. Its item table, as SL's, 400 records
# (the allocation of 23F0h bytes, 72FF7h); its things 0-519, the backpack's cells 14-25 (DSCLOG2's
# THING_COUNT, PACK_FIRST). No icons of the Loader's own (icons.fit: Shattered Lands' pictures).
RAV_FREE_THINGS, RAV_THINGS_USED, RAV_FREE_ITEMS, RAV_LOOT_OPEN = 0x56EF, 0x55C6, 0x5AF3, 0x05D6
STOCK_INTERVAL = 1.0  # (seconds between looks for a saved game's sellers without the new items: shopstock)


# Fuller starting gear (startgear.py, on DSCLOG2's GEAR_DONE: site 85) from the sequel's own plain items:
# OBJEX.GFF's item records (17h bytes: the picture, the value at +6, the type at +0Ah, the name at +14h; in no
# list, no slot), by weapon kind (specialize.KINDS) in the order tried, each a material the classes may use
# (restrict.usable): club (type 29, wood), mace (67, bone), dagger (72, obsidian), quarterstaff (85),
# chatkcha (25, obsidian), sling (93), and for a weapon spec long sword (73, obsidian), axe (48, obsidian),
# great axe (51), pick (79, stone), polearm (80), gythka (52), cahulaks (24); no short sword (the sequel has
# none of its own) and no bow (a Battle Dancer has a sling: no arrows made). Its leather ("Armor", of leather:
# type 32 for the chest, 3 the arms, 64 the legs; its armour types come in fives, 1-5 worn on the arms, 30-34
# on the chest, 62-66 on the legs, as a new fighter wears them), and a cloak (type 28, object 1615) for the kits
# that hide. An item's name number is its line in RESOURCE.GFF's TEXT 1000 counted from 1.
def _rav_item(hexed: str) -> bytes:
    return bytes.fromhex(hexed)


RAV_PLAIN: Dict[int, Tuple[Tuple[int, bytes], ...]] = {
    1: ((29, _rav_item("9ffd00000f2701000f271d0000000000000004ff210000")),),   # club (object 609)
    4: ((67, _rav_item("9efd00000f2718000f27430000000000000004ff1c0000")),),   # mace (610)
    2: ((72, _rav_item("9cfd00000f270a000f27480000000000000004ff1d0000")),),   # dagger (612)
    8: ((85, _rav_item("a3fd00000f2701000f27550000000000000004ff320000")),),   # quarterstaff (605)
    12: ((25, _rav_item("40fd00000f2701000f27190000000000000004ff170000")),),  # chatkcha (704)
    14: ((93, _rav_item("3ffd00000f2701000f275d0000000000000004ff350000")),),  # sling (705)
    0: ((73, _rav_item("9afd00000f274b000f27490000000000000004ff1a0000")),),   # long sword (614)
    5: ((48, _rav_item("8bfd00000f270f000f27300000000000000005ff1f0000")),),   # axe (629)
    6: ((51, _rav_item("a0fd00000f27f4010f27330000000000000005ff200000")),),   # great axe (608)
    7: ((79, _rav_item("8cfd00000f2732000f274f0000000000000006ff220000")),),   # pick (628)
    9: ((80, _rav_item("a2fd00000f2707000f27500000000000000004ff190000")),),   # polearm (606)
    10: ((52, _rav_item("99fd00000f2706000f27340000000000000004ff160000")),),  # gythka (615)
    11: ((24, _rav_item("9dfd00000f2701000f27180000000000000004ff310000")),),  # cahulaks (611)
}
RAV_LEATHER = ((game.EQUIP_SLOTS.index("chest"), _rav_item("d6fc00000f2718000f27200000000000000004ff450000")),
               (game.EQUIP_SLOTS.index("arm"), _rav_item("d1fc00000f2714000f27030000000000000004ff450000")),
               (game.EQUIP_SLOTS.index("legs"), _rav_item("ccfc00000f2714000f27400000000000000004ff450000")))
RAV_CLOAK = _rav_item("b1f900000f2701000f271c0000000000000004ff260000")


# and with the mod's new items (ravgear's, made with its picture: GD.new_items, the "new_items" setting), its
# obsidian mace (the sequel's type 74, ravgear.PLAIN's): a fire cleric's, as in Shattered Lands
RAV_PLAIN_NEW: Dict[int, Tuple[Tuple[int, bytes], ...]] = {
    4: ((74, _rav_item("2aa800000f270f000f274a0000000000000004ff1c0000")),),  # obsidian mace (ravgear's)
}


def rav_weapon(gd, sheet: bytes, kind: int, read):
    """startgear._weapon's for the sequel: a plain weapon of KIND the character can use (RAV_PLAIN, then
    RAV_PLAIN_NEW's with the new items), as (record, (type, ...)); None if there is none."""
    from . import startgear
    new = RAV_PLAIN_NEW.get(kind, ()) if getattr(gd, "new_items", True) else ()
    for type_, rec in RAV_PLAIN.get(kind, ()) + new:
        if startgear.can_use(gd, sheet, type_, read(type_)):
            return rec, (type_, 0, 0, 0)
    return None


# Picking pockets (pickpocket.pocket_sized): the sequel's item types keep Shattered Lands' weight byte (SL's
# word +4, the sequel's +2). The Loader's copy of OBJEX.GFF gives every carried type its weight (ravager.RAV_WEIGHTS:
# SSI left 71 of 102 at 0, its dagger, long sword, shield and armour alike: 2026-11-26, the Caravan Master's
# Obsidian Longsword lifted), so a type goes by its weight (MAX_WEIGHT or less), as in SL. One still at 0 (furniture,
# doors, a monster's weapon; or the copy made with RAV_SKIP=weights) goes by its kind: no shield nor armour, a
# weapon whose damage is RAV_POCKET_DAMAGE or less at most (a dagger's 1d4, darts, a sling: not a long sword's
# 1d8), anything else (rings, amulets, potions, scrolls) small.
RAV_POCKET_DAMAGE = 4


def rav_pocket_sized(typ: bytes) -> bool:
    from . import pickpocket, restrict
    weight, = struct.unpack_from("<H", typ, pickpocket.TYPE_WEIGHT)
    if weight:
        return weight <= pickpocket.MAX_WEIGHT
    if restrict.is_shield(typ) or typ[restrict.TYPE_KIND_FLAGS] & restrict.ARMOUR:
        return False
    if typ[0] & pickpocket.WEAPON_KINDS:
        return typ[0x0C] * max(1, typ[0x0D]) <= RAV_POCKET_DAMAGE
    return True


def rav_items() -> Dict[object, Dict[str, object]]:
    """The modules' names rebound for looting and selling in the sequel (apply_layout), and for fuller
    starting gear (startgear's items: the sequel's)."""
    from . import icons, itemgate, loot, pickpocket, ring, startgear
    words = {"FREE_THINGS": RAV_FREE_THINGS, "THINGS_USED": RAV_THINGS_USED, "FREE_ITEMS": RAV_FREE_ITEMS}
    return {ring: dict(words), itemgate: dict(words),
            # (picking pockets: none of Shattered Lands' people or weapons, its type and name numbers the
            # sequel's others)
            pickpocket: {"LIFTABLE_TYPES": (), "LIFTABLE_NAMES": {}, "OWN_POCKETS": (),
                         "pocket_sized": rav_pocket_sized},
            loot: {"OPEN": RAV_LOOT_OPEN, "STATUS_GONE": RAV_DEAD_STATUS},
            icons: {"fit": lambda gd, item: None},
            startgear: {"LEATHER": RAV_LEATHER, "CLOAK": RAV_CLOAK, "_weapon": rav_weapon,
                        "HANDS": game.WEAPON_HANDS}}


_SAVED: List[Tuple[object, str, object]] = []  # (module, name, Shattered Lands' value) as apply_layout found them


def apply_layout() -> int:
    """game.py's values, and the copies dsloader's modules imported (by the same name, the same value),
    rebound to the sequel's; dicelog's header signature too. Returns how many names were rebound."""
    if _SAVED:
        return 0
    profile = dict(layout(), HDR_SIG=HDR_SIG)
    originals = {name: getattr(game, name) for name in profile if hasattr(game, name)}
    originals["HDR_SIG"] = dicelog.HDR_SIG
    for name, (module, sl_name) in MOD_BYTES.items():
        originals.setdefault(name, getattr(module, sl_name))
    for module in [m for name, m in sys.modules.items() if name.startswith("dsloader.") and m is not None]:
        for name, value in profile.items():
            if name in vars(module) and vars(module)[name] == originals.get(name):
                _SAVED.append((module, name, vars(module)[name]))
                setattr(module, name, value)
    from . import combatlog  # (the panel's and the labels' colours: the sequel's palette, PALETTE_LAST)
    _SAVED.append((combatlog, "LAST", combatlog.LAST))
    combatlog.LAST = PALETTE_LAST
    from . import sizes  # (the creature size rule: the sequel's monsters and spell numbers)
    _SAVED.append((sizes, "TABLE", sizes.TABLE))
    _SAVED.append((sizes, "SPELLS", sizes.SPELLS))
    _SAVED.append((sizes, "PERSON_ONLY", sizes.PERSON_ONLY))
    _SAVED.append((sizes, "SHILLELAGH_TYPE", sizes.SHILLELAGH_TYPE))
    _SAVED.append((sizes, "HAMMER_TYPE", sizes.HAMMER_TYPE))
    sizes.TABLE, sizes.SPELLS, sizes.PERSON_ONLY = sizes.RAV_NAMES, sizes.RAV_SPELLS, frozenset()
    sizes.SHILLELAGH_TYPE, sizes.HAMMER_TYPE = sizes.RAV_SHILLELAGH_TYPE, sizes.RAV_HAMMER_TYPE
    from . import specialize  # (weapon specialization: the sequel's item types' kinds, DSCLOG2's
    for name, value in (("KIND_OF_TYPE", ravager.rav_kinds()),  # KIND_OF_TYPE and SPEC_KINDS_OWN)
                        ("CONJURED_KINDS", ravager.rav_spec_kinds())):
        _SAVED.append((specialize, name, getattr(specialize, name)))
        setattr(specialize, name, value)
    from . import kits  # (the kits' saves: the sequel's charms and its wizards' and priests' spells, 0-EAh;
    for name, value in (("CHARMS", RAV_CHARMS), ("SPELL_LAST", RAV_SPELL_LAST), ("POISON_POWER", RAV_POISON_POWER)) + RAV_KIT_SPELLS:  # the cures')
        _SAVED.append((kits, name, getattr(kits, name)))
        setattr(kits, name, value)
    _SAVED.append((dicelog, "SPELL_HANDLER_RETURNS", dicelog.SPELL_HANDLER_RETURNS))  # (the cures' lines)
    dicelog.SPELL_HANDLER_RETURNS = RAV_SPELL_HANDLER_RETURNS
    for module, names in RAV_TARGETING.items():  # (Tab, the ring, the chance under the pointer)
        for name, value in names.items():
            _SAVED.append((module, name, getattr(module, name)))
            setattr(module, name, value)
    for module, names in RAV_FIGHT_KEYS.items():  # (R's squares in reach, F10 after the last step)
        for name, value in names.items():
            _SAVED.append((module, name, getattr(module, name)))
            setattr(module, name, value)
    _SAVED.append((journal, "REGIONS", journal.REGIONS))  # (the Journal tab's headings: the sequel's regions)
    journal.REGIONS = REGIONS
    for name, value in (("TSR_LEARN_READ", SH_LEARN_READ), ("TSR_LEARN_SPELL_HI", SH_LEARN_SPELL_HI)):
        _SAVED.append((dicelog, name, getattr(dicelog, name)))  # (a Shinobi's scroll: DSCLOG2's own header)
        setattr(dicelog, name, value)
    for module, names in rav_items().items():  # (looting with T, selling with S: the item lists' words)
        for name, value in names.items():
            _SAVED.append((module, name, getattr(module, name)))
            setattr(module, name, value)
    from . import kalzith  # (dying and dead: the sequel's 4 and 7, SL's 4 and 5; aging.kill's dead)
    _SAVED.append((kalzith, "DEAD_STATUS", kalzith.DEAD_STATUS))
    kalzith.DEAD_STATUS = RAV_DEAD_STATUS
    from . import stealth  # (hiding in shadows: the sequel's positions, regions, footprint, dying and dead)
    for name, value in (("POSITIONS", RAV_POSITIONS), ("POSITION_SIZE", RAV_POSITION_SIZE),
                        ("OUTDOORS", RAV_OUTDOORS), ("INDOOR_TILES", {}), ("STATUS_GONE", RAV_DEAD_STATUS),
                        ("SHEET_FOOTPRINT", ravager.sheet_field(stealth.SHEET_FOOTPRINT))):
        _SAVED.append((stealth, name, getattr(stealth, name)))
        setattr(stealth, name, value)
    return len(_SAVED)


def rebind(name: str, value: int) -> None:
    """One more of game.py's names (and its imported copies) set to VALUE while the sequel is attached,
    put back by restore_layout (SPELLS_SEG: its value depends on the game's load segment)."""
    old = getattr(game, name)
    for module in [m for n, m in sys.modules.items() if n.startswith("dsloader.") and m is not None]:
        if name in vars(module) and vars(module)[name] in (old, value):
            if not any(m is module and n == name for m, n, _ in _SAVED):
                _SAVED.append((module, name, vars(module)[name]))
            setattr(module, name, value)


def restore_layout() -> None:
    """Shattered Lands' values back where apply_layout changed them."""
    while _SAVED:
        module, name, value = _SAVED.pop()
        setattr(module, name, value)


# The sequel's item types are 15-byte records (SL's 20): SL's with its words at +2, +4 and +6 narrowed to
# bytes and its last byte gone; from SL's +8 on (material, rate of fire, damage dice, flags, the icon,
# AC) the same, one for one (SL's type 1 and the sequel's 18, the same item, side by side, 2026-11-20).
TYPE_SIZE = 15
RAV_DEAD_STATUS = (4, 7)  # a creature's status (+14h): dying, dead (SL's 4, 5)
# Each map object's x, y (16ths of a square), 25h bytes apart (the attack's set-up reads them for the
# attacker SI and the target DI: 5C8B7h; SL's 669Dh, 32 apart)
RAV_POSITIONS, RAV_POSITION_SIZE = 0x67C5, 0x25
# The regions under the open sky (stealth.daylight), by each RGNxx.GFF's own name (its RNME): forest
# (Humbleton Forest), Tyr (its streets; its buildings' floors aren't told apart yet), Jann (the Jann
# tribe's desert), Silt Giants (the Silt Sea islands), Cloud and Limbo. The rest are under a roof or
# underground: VA Headquarters, Pyramid, Yuan-ti Tunnels, El's Temple, Mines1-3, Mosaic, Volcano
# Levels 1-3, Crypt, Cosmos, UnderTyr.
RAV_OUTDOORS = frozenset((0x01, 0x32, 0x3B, 0x41, 0x42, 0xFF))
# The squares in reach shown and hidden with R, and F10 taking a move back after its last step (squares.py,
# moveback.py; DSCLOG2's SQUARES, VIEW_REDRAW and F10_PIN): the sequel's live walk map, DS:0538h (SL's 0556h:
# ravds, five uses agree; the walls' cells C0h, a cell no one walks into 40h), a creature's movement points
# and its turn's flags, words at the load + 3C4Fh (selector 308h) +22Eh and +1D8h (the step routine 5D8C9h-
# 5D8F1h: SL's 37BDh +22Bh and +1D5h, the step 10 or 14 from DS:0551h), its swings this round and attack
# commands this turn, bytes there at +184h and +1AEh (SL's +181h, +1ABh: their only such reads); F10's
# turn's own points and first square, DS:4258h, 425Ah (y), 425Ch (x) (F10 at 1EC05h: SL's 4964h, 4966h,
# 4968h), the map things' standing still (bit 20h of +0, 1F3FCh) and feet; a walk's next step and steps
# left, the load + 3F49h (selector 388h) +374h a thing x 1Ch and +8A7h x 13h (SL's 3972h +377h, +8AAh: each
# their commonest use); the effects that pin, Paralyzed 69 and Cannot Move 66 (826F6h, SL's 34 and 51). DSCLOG2's
# header past the quick saves' (+1922 VIEW_REDRAW, +1924 SQUARES_ON, +1926 LIGHT's offset: DSCLOG's +242,
# +1890, +236), LIGHT made in the sequel's colours (RED_FIRST to RED_LAST: its 1-31 cycle).
FK_VIEW_REDRAW, FK_SQUARES_ON, FK_LIGHT = 1922, 1924, 1926
FK_SQUARE_DRAWS, FK_F10_MOVES, FK_F10_KEPT, FK_MARK_DRAWS = 1928, 1930, 1932, 1934
# The walkers' dust (DSCLOG2's DUST, dust.py's): its header's DUST_ON (+1972, the Loader's: 1 once LIGHT is made), the
# puffs raised (+1974) and its signature (+1976, DUST_SIG_WORD: a helper before DUST has its code there)
DUST_ON, DUST_PUFFS, DUST_SIG, DUST_SIG_WORD = 1972, 1974, 1976, 0x7544
DUST_LEAST = 0.2  # (dust.is_ground's least value here: Tyr's dirt, 56,44,28 to 85,73,52, is darker than SL's sand)
# The see-through figures (DSCLOG2's SEE-THROUGH FIGURES, ghost.py's): its header's GHOST_SEG (+1984, the block of
# pixels in upper memory: 0 none), GHOST_ON (+1986, the Loader's), the offsets of BLEND, REP and GHOST_TAB in the far
# block (+1988, +1990, +1992) and the figures drawn so (+1994)
GHOST_SEG, GHOST_ON, GHOST_BLEND, GHOST_REP, GHOST_TAB, GHOST_DRAWS = 1984, 1986, 1988, 1990, 1992, 1994


class RavGhosts(ghost.Ghosts):
    """ghost.Ghosts on the sequel: its stable colours (32-255; it cycles 1-31), its effects (Invisible 53, Detect
    Invisible 25) and the tables in DSCLOG2's far block."""
    TSR_ON = GHOST_ON
    FIRST, LAST, CYCLED = 32, 255, (range(1, 32),)
    INVISIBLE, DETECT = 53, 25

    def places(self, guest, tsr_hdr):
        seg, = struct.unpack("<H", guest.read(tsr_hdr + GHOST_SEG, 2))
        far, = struct.unpack("<H", guest.read(tsr_hdr + rings.TSR_FAR_SEG, 2))
        if not seg or not far:
            return None
        blend, rep, tab = struct.unpack("<HHH", guest.read(tsr_hdr + GHOST_BLEND, 6))
        return far * 16 + blend, far * 16 + rep, far * 16 + tab


DUST_LIGHTER = 0.2  # (and less toward white than SL's 0.45, which made it near white there: a step up its ramp)
RAV_FIGHT_KEYS = {
    squares: {"TSR_SQUARES_ON": FK_SQUARES_ON, "TSR_LIGHT": FK_LIGHT, "WALK_MAP": 0x0538, "POINTS_SEG": 0x3C4F,
              "POINTS_OFF": 0x22E, "FLAGS_OFF": 0x1D8, "POSITIONS": RAV_POSITIONS, "POSITION_SIZE": RAV_POSITION_SIZE,
              "LIGHT_FIRST": 32, "LIGHT_LAST": 255, "LIGHT_LEAST": DUST_LEAST,
              "LIGHT_LIGHTER": DUST_LIGHTER},
    moveback: {"POINTS_SEG": 0x3C4F, "POINTS_OFF": 0x22E, "FLAGS_OFF": 0x1D8, "ATTACKS_OFF": 0x184,
               "COMMANDS_OFF": 0x1AE, "START_POINTS": 0x4258, "START_Y": 0x425A, "START_X": 0x425C,
               "MAP_RECORD": 0x67BB, "MAP_SIZE": RAV_POSITION_SIZE, "POSITIONS": RAV_POSITIONS,
               "WALK_SEG": 0x3F49, "WALK_STEP": 0x374, "WALK_LEFT": 0x8A7, "PINNING": (69, 66)},
    shadows: {"TSR_VIEW_REDRAW": FK_VIEW_REDRAW},
    usable: {"DRAW_LIST": 0x67B7, "DRAW_COUNT": 0x264E, "DRAW_MOST": 2000, "MAP_OBJECT": 0x1B,
             "TRIGGERS_PTR": 0x40C0, "HEADS_SEG": 0x3C10, "STATUS_DEAD": 7, "HOSTILE_SIDES": 0xF80,
             "DOOR_TYPES": (41,), "BODIES": (2200,)},
}
TYPE_FIELDS = {0: 0, 2: 1, 4: 2, 6: 3, **{sl: sl - 4 for sl in range(8, 19)}}  # SL's offset -> the sequel's
TYPES_SHOWN = 256  # (the types a read of the table may name: SL's layout served for this many)


def sl_type(record: bytes) -> bytes:
    """One of the sequel's item type records (TYPE_SIZE bytes) in Shattered Lands' layout (20 bytes)."""
    out = bytearray(game.ITEM_TYPE_SIZE)
    for sl, wotr in TYPE_FIELDS.items():
        if wotr < len(record):
            out[sl] = record[wotr]
    return bytes(out)


class ReadOnlyGuest:
    """The game's memory as GUEST has it, every write dropped (and counted in `dropped`), and the item
    type table read in Shattered Lands' layout (sl_type): the code shared with Shattered Lands reads
    its fields by their offsets there."""

    def __init__(self, guest):
        self.guest = guest
        self.dropped = 0
        self.ds: Optional[int] = None  # (set by RavDiceLog once the game's found: the type table's pointer)
        self.spells: bytes = b""  # the sequel's spell records in SL's table layout (spell_table), served
        self.spells_at = SPELLS_AT  #   from SPELLS_AT, where the game has nothing the dice log reads
        self.writable: List[Tuple[int, int]] = []  # (address, size): the helper's buffers a ported feature writes
        self.item_gate = None  # (the item gate, as GuestMemory's: a write to the item lists waits for it, itemgate.py)

    def _types(self) -> Optional[int]:
        if self.ds is None:
            return None
        off, seg = struct.unpack("<HH", self.guest.read(self.ds * 16 + ADDRESSES["ITEM_TYPES_PTR"], 4))
        return seg * 16 + off

    def read(self, addr: int, size: int) -> bytes:
        if CLASS_MAGIC_AT <= addr < CLASS_MAGIC_AT + len(CLASS_MAGIC):
            return CLASS_MAGIC[addr - CLASS_MAGIC_AT:addr - CLASS_MAGIC_AT + size]
        if self.spells and self.spells_at <= addr < self.spells_at + len(self.spells):
            end = min(addr + size, self.spells_at + len(self.spells))
            return self.spells[addr - self.spells_at:end - self.spells_at]
        base = self._types()
        sl_size = game.ITEM_TYPE_SIZE
        if base is not None and base <= addr < base + TYPES_SHOWN * sl_size and size > 0:
            first, last = (addr - base) // sl_size, (addr + size - 1 - base) // sl_size
            table = self.guest.read(base + first * TYPE_SIZE, (last - first + 1) * TYPE_SIZE)
            view = b"".join(sl_type(table[i * TYPE_SIZE:(i + 1) * TYPE_SIZE]) for i in range(last - first + 1))
            start = addr - base - first * sl_size
            return view[start:start + size]
        return self.guest.read(addr, size)

    def write(self, addr: int, data: bytes) -> None:
        if any(start <= addr and addr + len(data) <= start + size for start, size in self.writable):
            if self.item_gate is not None and self.item_gate.covers(addr, len(data)):
                self.item_gate.open()  # (ItemsBusy: the game is changing its lists; nothing written)
            self.guest.write(addr, data)
        else:
            self.dropped += 1

    def __getattr__(self, name):  # (snapshot, the base address... the guest's own, but writes)
        return getattr(self.guest, name)


# The sequel's spells: RESOURCE.GFF's DATA 0-319, 73 bytes each, the first 32 Shattered Lands' record,
# then its name (32 bytes) and a short name. Shattered Lands' code reads the table at
# (load + SPELLS_SEG) x 16 + SPELLS_OFF + 32 x spell (SPELLS_OFF 16 bytes into the first record), so the
# view serves the records back to back from SPELLS_AT (the BIOS's ROM, which nothing here reads) and
# SPELLS_SEG is pointed there once the load segment is known (RavDiceLog.attach).
SPELLS_AT = 0xF0000
# Which classes cast which magic (a byte every 4 by class number: bit 1 wizard, bit 2 priest, as SL's
# table at load + 3800h:118h has them). The sequel has no such table: its slot routine (626B7h) asks
# whether the class can cast a wizard spell (8) and a priest spell (73h) of a routine (62B45h): wizard
# spells classes 11 and 18 (SL's preserver and the sequel's new one), priest spells those whose spheres
# (its jump table: 1-8, 13-16 and 19, the sequel's new one, all spheres) meet spell 73h's (30h: every
# priest class). The view serves those bits from CLASS_MAGIC_AT (past the spells), CLASS_MAGIC_SEG
# pointed there at attach. (Not the spheres: the dice log's caster levels for Dispel Magic aren't ported.)
CLASS_MAGIC_AT = 0xF4000 + game.CLASS_MAGIC_OFF
WIZARD_CLASSES, PRIEST_CLASSES = (11, 18), (1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 19)
CLASS_MAGIC = bytes(b for c in range(32) for b in ((2 if c in PRIEST_CLASSES else 1 if c in WIZARD_CLASSES
                                                       else 0), 0, 0, 0))
# The sequel's spells by kind (its DATA names): wizard 0-114, priest 115-234, psionic powers 235 (0EBh,
# the caster level routine's bound) to 268 (10Ch), then the monsters' powers
RAV_PRIEST_FIRST, RAV_PSIONIC_FIRST, RAV_MONSTER_FIRST = 115, 0xEB, 0x10D
SPELL_STARTS, SPELL_STARTS_ROW, SPELL_LEVELS_MOST = 0x0656, 11, 10  # (DS bytes, a row of 11 for wizard spells then
# priest: each level's first spell, 1 to 10, then the end: 0, 12, 25 ... 111, 115; 115, 127 ... 233, 235)
SLOTS_ALL_19 = 0x13F8  # a DS byte the slot routine checks: 1 gives the party 19 of everything (SL's word 1164h)
SPELL_COUNT, SPELL_RECORD = ravager.SPELL_COUNT, ravager.SPELL_SIZE
SPELLS_END = ravspells.FIRST + len(ravspells.SPELLS)  # (past the new spells, 320-325, in the Loader's copy)


def spell_table(resources: bytes) -> Tuple[bytes, List[str]]:
    """The sequel's RESOURCE.GFF's spell records as Shattered Lands' table (32 bytes a spell), and the
    spells' names (title case, as game.title makes Shattered Lands')."""
    from . import gff
    chunks = gff.read_gff(resources)
    table, names = bytearray(), []
    for spell in range(SPELLS_END):  # (the game's, then the new spells' in the copy)
        rec = chunks.get(("DATA", spell), b"")
        table += (rec[:32] + bytes(32))[:32]
        names.append(game.title(rec[32:64].split(b"\0", 1)[0].decode("latin1").strip()) if len(rec) >= 64 else "")
    return bytes(table), names


def resources_file() -> Optional[str]:
    """The sequel's RESOURCE.GFF as the game reads it: the Loader's copy (with the spell fixes) in its
    dos folder, else the game's own (its folder found as the Loader finds it)."""
    import os
    from . import launch
    copy = os.path.join(launch.DOS_DIR, ravager.RESOURCE_COPY)
    if os.path.isfile(copy):
        return copy
    folder = ravager.find_dir(launch.load_settings().get("game_dir"))
    return os.path.join(folder, ravager.RESOURCE_FILE) if folder else None


# The sequel's item names: RESOURCE.GFF's TEXT 1000, a name a line, an item's name number the line's
# (from 1: Ar'anda's +1 long sword is 26, "Longsword"; the Draxans' 24, "Lotulis", as the game's Look box
# names it). In memory the lines end in CR NUL; the list is found by its first two names.
NAMES_START = b"Tombstone\r\x00Olive Branch\r\x00"


# The sequel's damage resistance (its routine at 85052h, not SL's kinds table): a creature's resistance
# class is the byte at +0Fh of its record (0 for people; a Giant Skeleton's 2). DS:2588h holds a word a
# class (18): the damage kinds it takes none of, its weapon kinds (crushing, edged, pointed) only from
# weapons below the magic its bits B000h say (1000h: +1 or better hurts). DS:25ACh a word for each of
# the first 7 classes: kinds it takes half of. (The routine also halves or stops some kinds for a
# creature's active resistances, its record's flags, which the Look box doesn't count.)
CREATURE_RESIST = 0x0F
RESIST_IMMUNE, RESIST_IMMUNE_COUNT = 0x2588, 18
RESIST_HALF, RESIST_HALF_COUNT = 0x25AC, 7
WEAPON_BITS, MAGIC_BITS = 0x38, 0xB000


def resist_percent(immune: int, half: int, kinds: int) -> int:
    """The percent of a hit with KINDS a creature of a class with these masks takes, as 85052h works it out."""
    taken = -1
    if immune & kinds & WEAPON_BITS:
        if (immune & MAGIC_BITS) > (kinds & MAGIC_BITS):
            taken = 0
    elif immune & kinds:
        taken = 0
    if taken < 0:
        taken = 100
    if half & kinds:
        taken //= 2
    return taken


def resist_masks(gd, resist: int) -> Tuple[int, int]:
    """(immune, half) for resistance class RESIST, read from the running game's data segment."""
    immune = half = 0
    if 0 <= resist < RESIST_IMMUNE_COUNT:
        immune, = struct.unpack("<H", gd.guest.read(gd.ds * 16 + RESIST_IMMUNE + 2 * resist, 2))
    if 0 <= resist < RESIST_HALF_COUNT:
        half, = struct.unpack("<H", gd.guest.read(gd.ds * 16 + RESIST_HALF + 2 * resist, 2))
    return immune, half


def monster_lines(gd, creature: int, ac: Optional[int]) -> Tuple[List[str], List[str]]:
    """monsters.monster_lines for the sequel: (the Look box's short lines, the whole description), its
    records' fields through the layout (game's constants rebound) and its resistance classes."""
    rec, sheet = gd.creature(creature), gd.sheet(creature)
    if len(rec) < ravager.CREATURE_SIZE or len(sheet) < ravager.SHEET_SIZE:
        return [], []
    hp = struct.unpack_from("<h", rec, 0)[0]
    max_hp = struct.unpack_from("<h", sheet, 0x08)[0]
    thac0 = struct.unpack_from("b", rec, ravager.creature_field(0x1F))[0]
    mr = sheet[ravager.sheet_field(0x29)]
    attacks = sheet[ravager.sheet_field(0x2A)]
    immune, half = resist_masks(gd, rec[CREATURE_RESIST])
    d = monsters.defences([], 0, False, percent=lambda kinds: resist_percent(immune, half, kinds))
    if ac is None:
        ac = gd.counted_ac(creature)
    ac_text = str(ac) if ac is not None else str(struct.unpack_from("b", sheet, ravager.sheet_field(0x27))[0])
    alignment = monsters.ALIGNMENTS.get(sheet[ravager.sheet_field(monsters.SHEET_ALIGNMENT)])
    second = f"THAC0 {thac0}"
    if alignment and monsters.look_pixels(f"{second} AL {alignment[0]}") <= monsters.LOOK_PIXELS:
        second += f" AL {alignment[0]}"
    short = [monsters.look_fit(f"HP {hp}/{max_hp} AC {ac_text}", f"HP{hp}/{max_hp} AC{ac_text}"), second]
    if mr:
        side = f"MR {mr}" if monsters.look_pixels(f"MR {mr}") <= monsters.SIDE_PIXELS else f"MR{mr}"
        short.insert(0, monsters.LOOK_SIDE + side)
    line = monsters.short_line(d)
    spells = bool(immune & monsters.MAGIC)  # (every spell carries MAGIC: none hurts it)
    if spells and not d.weapon_plus:
        line = "IMM SPELLS PSI" if immune & monsters.PSIONIC else "IMM SPELLS"
    if line:
        short.append(line)
    said = monsters.describe(d)
    if spells:  # (the list of kinds said as what it is)
        said = [("Immune to spells" + (" and psionic attacks." if immune & monsters.PSIONIC else "."))
                if t.startswith("Immune to ") else t for t in said]
    per_round = f"{attacks // 2}" if attacks % 2 == 0 else f"{attacks}/2"
    head = f"{gd.creature_name(creature)}: HP {hp}/{max_hp}, AC {ac_text}, THAC0 {thac0}"
    if attacks:
        head += f", {per_round} attack{'s' if attacks != 2 else ''} a round"
    full = [head + (f", magic resistance {mr}%" if mr else "") + (f", {alignment[1]}" if alignment else "") + "."]
    return short, full + said


# The sequel's saving throw modifiers (628h:A7h, 83606h; SL's 79D3Ch, otherwise built): the target's and
# the caster's effects as bit sets (608h:25h, 7FE93h: effect N's bit N % 8 of byte N / 8), the spell's
# record (its +11h category word, +1Ah kinds word) and the target's sheet; what the routine adds, in its
# order (RavGameData.save_modifiers). Effects by the sequel's numbers (effect_names).
LIFE_DRAINED, WEATHER_GUARD, WEATHER_BANE = 59, 80, 107  # (-2 a level drained; +6, -20 against WEATHER_SPELLS)
WEATHER_SPELLS = (32, 58, 69, 93)  # Lightning Bolt, Cone of Cold, Chain Lightning, Incendiary Cloud
ENTRANCED, ENTRANCED_SPELLS = 33, (2, 39, 94, 131, 255)  # (-3 against the charms but Dominate)
THORNS, THORNS_SPELL = 16, 188  # Bound By Thorns, -4 against Thorns of Binding
SAVE_EFFECTS = ((44, -2, "Heat Exhaustion"), (88, -1, "effect 88"))  # (88: an unnamed effect of the game's)
SPIRIT_ARMOR, BARKSKIN, BLESSED, BLURRY, BRAVE, PRAYER = 94, 6, 9, 13, 18, 72
PROT_EVIL = 75
SPOOK_CLASSES = (11, 18)  # (Spook's save by the caster's preserver or wizard level: DSCLOG2's NS_SPOOK_SAVE)
PROT_KINDS = ((0x80, 78, 4, "Protected vs Lightning"), (0x04, 73, 3, "Protected vs Cold"),
              (0x02, 77, 4, "Protected vs Fire"))  # (the record's kinds bit, the effect, its bonus)
FIRE_SHIELD = 38  # (+2 against fire and cold with the spells as the manual has them: DSCLOG2's FSHIELD_SAVE)
BLIND, DETECT_INVISIBLE, INVISIBLE, INVISIBLE_UNDEAD = 10, 25, 53, 54
UNSEEN_RANGE = 8  # (the can't-see +4 only for a spell whose range at level 1 is this or less: 680h:20h)
CLOSE_TARGETS = (3, 4, 5, 7, 8)  # (a record's +0Ch target kinds 680h:20h gives range 8)
AREAS_SEG, AREA_SIZE = 0x41F1, 0x12  # (the areas' table, selector 3D0h: +5 bits 2-3 1 doubles the range)
UNDEAD_RACE, DRUIDS, PSIONICIST_CLASS = 9, (5, 6, 7, 8), 12
DWARF_RACE, HALFLING_RACE = 2, 6
# DSCLOG2's PROT_SAVE (site 44): the protection items, the sequel's types (PROT_RING the sequel's Ring, the
# others the mod's: ravager.mod_type), their slots SL's
PROT_RING, PROT_CLOAK, PROT_ROBE = 45, 103, 127
RING_SLOTS, CLOAK_SLOT, CHEST_SLOT = (4, 11), 12, 9
ARMOUR_SLOTS, HAND_SLOTS = (0, 6, 7, 9), (3, 10)
METAL = 2  # (a type's material, its SL +8h & 4Fh)


# The sequel's to-hit routine (628h:66h): the attacker's effects (Blessed, Cursed, Slowed, Impeded, Weapon
# Grafted, Heat Exhaustion), Berserk's by the preserver level, Soothe's Extra Hit Points, the halfling's range
HIT_EFFECTS_RAV = ((9, 1, "Blessed"), (22, -1, "Cursed"), (91, -4, "Slowed"), (50, -2, "Impeded"),
                   (106, 1, "Weapon Grafted"), (44, -2, "Heat Exhaustion"))
BERSERK, BERSERK_CLASS, EXTRA_HP, SOOTHE, HALFLING_RANGE, ANTI_MAGIC = 102, 11, 34, 187, 0x1C, 4
STINK_TO_HIT = 2  # (DSCLOG2's, on a nauseated attacker's swing)


class RavGameData(game.GameData):
    """game.GameData for the sequel: its item names from its own list (NAMES_START), and only the mod's
    rule changes ported to it (ravager.RULES_PORTED: the spell slots, for one, are the game's own)."""

    _rules = 0
    psionic_first = RAV_PSIONIC_FIRST

    @property
    def rules(self) -> int:
        return self._rules

    def in_combat(self) -> bool:
        """SL's, the game's flag read as the byte it is in the sequel (DS:13FAh, IN_COMBAT)."""
        return self.guest.read(self.ds * 16 + game.IN_COMBAT, 1)[0] != 0 and self.fight_on()

    @rules.setter
    def rules(self, value: int) -> None:  # (the Loader's settings name SL's rules: the sequel's ported ones)
        self._rules = value & ravager.RULES_PORTED

    def creation_abilities(self) -> Optional[List[int]]:
        """SL's, from the creature being made's own pointer (DS:142Dh, CREATION_CREATURE_PTR): the
        sequel's isn't straight after the sheet."""
        at = game.far_pointer(self.guest, self.ds, game.CREATION_CREATURE_PTR) + game.CREATURE_ABILITIES
        values = list(self.guest.read(at, 6))
        return values if len(values) == 6 and all(3 <= v <= 25 for v in values) else None

    def counted_ac(self, creature: int) -> Optional[int]:
        """SL's, and with RULE_HELMS a worn Helm of the sequel's type 55 counting AC 1 (DSCLOG2's
        PROBE_HELM_AC: ravager.HELM_TYPE, HELM_NAME; its type reads AC 0, as a hat's), and the mod's Bone
        Helm (ravager.BONE_HELM_TYPE, whatever its name)."""
        ac = super().counted_ac(creature)
        if ac is None or not self.rules & game.RULE_HELMS:
            return ac
        for _, item, typ in self._worn(creature, game.CREATURE_ITEM_LISTS[:1]):
            if len(item) < ravager.ITEM_NAME + 2 or not typ[0x0F] & 0x80:
                continue
            kind = struct.unpack_from("<H", item, game.ITEM_TYPE)[0]
            if kind == ravager.BONE_HELM_TYPE or (
                    kind == ravager.HELM_TYPE and struct.unpack_from("<H", item, ravager.ITEM_NAME)[0] == ravager.HELM_NAME):
                ac -= 1
        return ac

    def party_position(self) -> Tuple[int, int]:
        """SL's, from the sequel's map things (RAV_POSITIONS: the leader's feet, the thing 0's)."""
        return struct.unpack("<HH", self.guest.read(self.ds * 16 + RAV_POSITIONS, 4))

    def talk_target_distance(self) -> Optional[int]:
        """SL's, on the sequel's map things (RAV_POSITIONS, RAV_POSITION_SIZE bytes each)."""
        combatant, = struct.unpack("<h", self.guest.read((self.load_seg + game.TALK_SEG) * 16 + game.TALK_TARGET, 2))
        if not game.PARTY_SIZE <= combatant < game.THINGS:
            return None
        x, y = struct.unpack("<HH", self.guest.read(self.ds * 16 + RAV_POSITIONS + combatant * RAV_POSITION_SIZE, 4))
        lx, ly = self.party_position()
        if x >= 0xFFF0 or y >= 0xFFF0:  # (off the map)
            return None
        return max(abs(x - lx), abs(y - ly))

    def creating(self) -> bool:
        """Never (SL's test reads its creation screen's pointers, not the sequel's): the sequel's screen
        rolls no age, so the character being made may have one given at once (aging.give_ages)."""
        return False

    def spell_level(self, spell: int) -> int:
        """The spell's level: the sequel's table at DS:0656h (SPELL_STARTS), the first spell of each
        level, a row for wizard spells then one for priest (SL's 7-byte table isn't in the sequel). 0 for a
        psionic power or a monster's."""
        if not 0 <= spell < RAV_PSIONIC_FIRST:
            return 0
        at = self.ds * 16 + SPELL_STARTS + (0 if spell < RAV_PRIEST_FIRST else SPELL_STARTS_ROW)
        return sum(1 for first in self.guest.read(at, SPELL_LEVELS_MOST) if first <= spell)

    def no_spells(self, creature: int) -> bool:
        """SL's, with class restrictions on (DSCLOG2's CAST_ARMOUR: a multiclass preserver casts nothing
        in armour)."""
        return bool(self.rules & game.RULE_RESTRICT) and super().no_spells(creature)

    def thief_heavy(self, creature: int) -> bool:
        """SL's, with class restrictions on (DSCLOG2's BELT_SITE and THIEF_REAR: no thief skills or
        backstab in armour that isn't light)."""
        return bool(self.rules & game.RULE_RESTRICT) and super().thief_heavy(creature)

    def effect_caster_level(self, creature: int, spell: int) -> Optional[int]:
        """The level a spell effect counts as cast at: the sequel's caster level routine (698h:34h,
        97DC5h; SL's 81B16h, which game.effect_caster_level models with SL's sphere tables, not in the
        sequel). Below psionic powers (RAV_PSIONIC_FIRST) the best level of the classes that cast the
        spell (wizard spells below RAV_PRIEST_FIRST: WIZARD_CLASSES; the rest PRIEST_CLASSES, spheres
        aside), a ranger's 7 less; a psionic power the psionicist's level; Enlarge's levels for the
        attack (DSCLOG2's ENL_SITE, 608h:52h) come from here. None for monsters' own powers."""
        if not 0 <= spell < RAV_MONSTER_FIRST:
            return None
        if spell >= RAV_PSIONIC_FIRST:
            return self.class_level(creature, game.PSIONICIST)
        casters = WIZARD_CLASSES if spell < RAV_PRIEST_FIRST else PRIEST_CLASSES
        return max([self.class_level(creature, c) - (7 if c in game.RANGER_CLASSES else 0) for c in casters] + [0])

    def max_spell_slots(self, member: int, bit: int, spell_level: int, wis: bool = True) -> int:
        """The game's slot routine (626B7h; SL's 5E0ACh, the same but for its test switch, a byte at
        DS:13F8h, SL's word at 1164h, and which classes cast: CLASS_MAGIC)."""
        if member < 4 and self.guest.read(self.ds * 16 + SLOTS_ALL_19, 1)[0] == 1:
            return 19
        return super().max_spell_slots(member, bit, spell_level, wis)

    def adnd_slots(self, cls: int, level: int, spell_level: int) -> Optional[int]:
        """The sequel's: AD&D's to 20th level with AD&D's class tables (tables.rav_slots, DSCLOG2's
        ADND_SLOTS), else None (the game's own rule for the level)."""
        from . import tables
        return tables.rav_slots(cls, level, spell_level) if self.rules & game.RULE_ADND_TABLES else None

    def robe_slots(self, member: int, bit: int, spell_level: int, total: int) -> int:
        """TOTAL slots with the member's worn robe's: the party transfer's robes are the mod's type in the
        sequel (ravager.mod_type), the Veiled Robe's one more as SL's (robes.slots; DSCLOG2's VEILED_SLOT)."""
        from . import robes
        robe = ravager.mod_type(game.ROBE_TYPE)
        plus = next((struct.unpack("b", rec[RAV_ITEM_PLUS:RAV_ITEM_PLUS + 1])[0] for _, rec, _ in self._worn(member)
                     if struct.unpack_from("<H", rec, RAV_ITEM_TYPE)[0] == robe and rec[RAV_ITEM_SLOT] == robes.CHEST_SLOT),
                    0)
        return robes.slots(plus, bit, spell_level, total)

    def spell_record(self, spell: int) -> bytes:
        """SL's, for all of the sequel's spells (SPELL_COUNT: its psionic powers and monsters' powers go past
        255, Psionic Blast 266)."""
        if not 0 <= spell < SPELLS_END:
            return b""
        return self.guest.read((self.load_seg + game.SPELLS_SEG) * 16 + game.SPELLS_OFF - 0x10 + spell * game.SPELL_SIZE,
                               game.SPELL_SIZE)

    def spell_rules(self, spell: int) -> Optional[game.SpellRules]:
        """SL's (the save modifier in the record's +1Fh bits 1-4: the saving throw's 66E99h), for all the
        sequel's spells."""
        rec = self.spell_record(spell)
        if len(rec) < game.SPELL_SIZE:
            return None
        nibble = (rec[0x1F] >> 1) & 0x0F
        return game.SpellRules(nibble - 16 if nibble & 8 else nibble)

    def _effect_ids(self, combatant: Optional[int]) -> set:
        """The effects COMBATANT has (608h:25h's bit set: none for a combatant past 2Fh)."""
        if combatant is None or not 0 <= combatant < 0x30:
            return set()
        return {x.id for x in self.effects() if x.owner == combatant}

    def _first_effect(self, combatant: int, eid: int) -> Optional[bytes]:
        """COMBATANT's first EID effect's 10-byte record (D8h:A8h), else None."""
        count = self._word(game.EFFECT_COUNT)
        if not 0 <= count <= 400:
            return None
        data = self.guest.read((self.load_seg + game.EFFECTS_SEG) * 16 + game.EFFECTS_OFF, count * 10)
        for i in range(count):
            rec = data[i * 10:i * 10 + 10]
            if struct.unpack_from("<h", rec, 0)[0] == combatant and rec[6] == eid:
                return rec
        return None

    def _side(self, combatant: Optional[int]) -> Optional[int]:
        creature = self.combatant_creature(combatant) if combatant is not None else None
        rec = self.creature(creature) if creature is not None else b""
        return rec[game.CREATURE_SIDE] if len(rec) > game.CREATURE_SIDE else None

    def _ability(self, creature: int, n: int) -> int:
        rec = self.creature(creature)
        return rec[game.CREATURE_ABILITIES + n] if len(rec) > game.CREATURE_ABILITIES + n else 9

    def spell_range(self, spell: int, level: int = 1) -> int:
        """A spell's range at LEVEL (680h:20h, 92115h): 8 for the close target kinds (the record's +0Ch),
        else its +9 word + its +0Bh x LEVEL, doubled for an area (+17h) of the kind 1 (the areas' +5 bits
        2-3); 0 made 1."""
        rec = self.spell_record(spell)
        if len(rec) < 0x18:
            return 0
        if rec[0x0C] in CLOSE_TARGETS:
            return UNSEEN_RANGE
        reach = struct.unpack_from("<H", rec, 9)[0] + rec[0x0B] * level
        if rec[0x17] != 0xFF:
            kind = self.guest.read((self.load_seg + AREAS_SEG) * 16 + struct.unpack("b", rec[0x17:0x18])[0] * AREA_SIZE + 5, 1)
            if kind and (kind[0] >> 2) & 3 == 1:
                reach *= 2
        return reach or 1

    def save_protection(self, creature: int, spell: int) -> List[Tuple[int, str]]:
        """What DSCLOG2's PROT_SAVE (site 44, first in the save modifiers) adds: the better ring of
        protection's plus, a cloak of protection's without magical or metal armour or a shield in a hand,
        the Veiled Robe +1, the Ashen Robe +1 against a wizard's or priest's spell (PROT_SCAN's reading)."""
        from . import restrict
        rings, cloak, robe, blocked = [0], 0, 0, False
        for _, item, typ in self._worn(creature):
            kind, slot = struct.unpack_from("<H", item, game.ITEM_TYPE)[0], item[game.ITEM_SLOT]
            plus = struct.unpack("b", item[game.ITEM_PLUS:game.ITEM_PLUS + 1])[0]
            if kind == PROT_RING:
                if slot in RING_SLOTS and plus > 0:
                    rings.append(plus)
            elif kind == PROT_CLOAK:
                if slot == CLOAK_SLOT:
                    cloak = plus
            elif kind == PROT_ROBE:
                if slot == CHEST_SLOT:
                    robe = plus & 0xFF
            elif len(typ) == game.ITEM_TYPE_SIZE:
                if typ[0] & 4:
                    blocked |= slot in HAND_SLOTS
                elif slot in ARMOUR_SLOTS and restrict.is_armour(typ):
                    blocked |= plus > 0 or typ[8] & 0x4F == METAL
        out = [(max(rings), "Ring of Protection")]
        if cloak > 0 and not blocked:
            out.append((cloak, "Cloak of Protection"))
        if robe >= 2 or robe == 1 and spell <= RAV_SPELL_LAST:
            out.append((1, "Veiled Robe" if robe >= 2 else "Ashen Robe"))
        return out

    def save_modifiers(self, target: int, caster: int, spell: int, save: int) -> List[Tuple[int, str]]:
        """What the sequel adds to a saving throw's d20 (its routine 628h:A7h, 83606h, with DSCLOG2's sites
        in it: PROT_SAVE and the kits', Blur's and Fire Shield's as the manual has them, CON as in AD&D),
        as [(amount, why), ...], in the routine's order. Its -100 and +100 (Chaos, Cloudkill, Scare, Color
        Spray) and Dismissal's levels are left to the save line ("cannot save", "saves automatically",
        "levels")."""
        ti, ci = self.combatant_creature(target), self.combatant_creature(caster)
        if ti is None:
            return []
        rec, sheet = self.spell_record(spell), self.sheet(ti)
        if len(rec) < 0x20 or len(sheet) < game.SHEET_SIZE or len(self.creature(ti)) < game.CREATURE_SIZE:
            return []
        category, kinds = struct.unpack_from("<H", rec, 0x11)[0], struct.unpack_from("<H", rec, 0x1A)[0]
        mine, theirs = self._effect_ids(target), self._effect_ids(caster)
        caster_sheet = self.sheet(ci) if ci is not None else b""
        out = self.save_protection(ti, spell)  # (DSCLOG2's PROT_SAVE, then its KIT_SAVE)
        from . import kits
        for kid in self.kit_ids(ti):
            if kits.save(kid, spell, kinds):
                out.append((kits.save(kid, spell, kinds), kits.name(kid)))
        if spell == ravspells.SPOOK and self.rules & game.RULE_NEW_SPELLS:  # (DSCLOG2's NS_SPOOK_SAVE)
            levels = [caster_sheet[game.SHEET_LEVELS + p] for p in range(3) if len(caster_sheet) >= game.SHEET_SIZE
                      and caster_sheet[game.SHEET_CLASSES + p] in SPOOK_CLASSES]
            penalty = -min(game.SPOOK_MOST, max(levels, default=0) // 2)
            if penalty:
                out.append((penalty, "Spook, the caster's levels"))
        drained = self._first_effect(target, LIFE_DRAINED)
        if drained is not None and drained[8]:
            out.append((-2 * drained[8], f"Life Drained ({drained[8]})"))
        if spell in WEATHER_SPELLS:
            if WEATHER_GUARD in mine:
                out.append((6, "Protected vs Weather"))
            if WEATHER_BANE in mine:
                out.append((-20, "Vulnerable to Weather"))
        if ENTRANCED in mine and spell in ENTRANCED_SPELLS:
            out.append((-3, "Entranced"))
        if spell == THORNS_SPELL and THORNS in mine:
            out.append((-4, "Bound By Thorns"))
        out += [(amount, why) for eid, amount, why in SAVE_EFFECTS if eid in mine]
        if SPIRIT_ARMOR in mine and save != game.PPD_SAVE:
            out.append((3, "Spirit Armored"))
        if BARKSKIN in mine:
            out.append((1, "Barkskin"))
        manual = self.spells_manual()
        if manual and BLURRY in mine:  # (DSCLOG2's BLUR_SAVE)
            out.append((1, "Blurry"))
        if BLESSED in mine:
            out.append((1, "Blessed"))
        if PROT_EVIL in mine and len(caster_sheet) > 0x14 and caster_sheet[0x14] in game.EVIL_ALIGNMENTS:
            out.append((2, "Protected vs Evil, an evil caster"))
        for bit, eid, amount, why in PROT_KINDS:
            if kinds & bit and eid in mine:
                out.append((amount, why))
            if bit == 0x04 and manual and kinds & 0x06 and FIRE_SHIELD in mine:  # (DSCLOG2's FSHIELD_SAVE)
                out.append((2, "Fire Shielded"))
        if PRAYER in mine:
            prayer = self._first_effect(target, PRAYER)
            same = prayer is not None and self._side(struct.unpack_from("<h", prayer, 2)[0]) == self._side(target)
            out.append((1 if same else -1, "Prayer, " + ("its caster's side" if same else "the other side's")))
        if caster is not None and 0 <= caster < 0x30 and self.spell_range(spell) <= UNSEEN_RANGE:
            undead = len(caster_sheet) > 0x12 and caster_sheet[0x12] == UNDEAD_RACE
            if BLIND in theirs:
                out.append((4, "the caster is Blind"))
            elif DETECT_INVISIBLE not in theirs and (INVISIBLE in mine or undead and INVISIBLE_UNDEAD in mine):
                out.append((4, "Invisible to the caster"))
        if category & game.FEAR_CATEGORY and BRAVE in mine:
            out.append((4, "Cloak of Bravery"))
        if kinds & 0x82 and any(self.class_level(ti, c) for c in DRUIDS):
            out.append((2, "druid against fire and electricity"))
        if category & 0x06 and self.dual_level(ti, PSIONICIST_CLASS):
            out.append((2, "psionicist against the mind"))
        if category & game.CATEGORY_DODGE:
            dex = self._ability(ti, 1)
            adjust = -struct.unpack("b", self.guest.read(self.ds * 16 + game.DEX_AC + dex, 1))[0] if dex < 26 else 0
            if adjust:
                out.append((adjust, f"DEX {dex} dodging"))
        if category & game.SAVE_WIS_CATEGORY:
            wis = self._ability(ti, 4)
            adjust = struct.unpack("b", self.guest.read(self.ds * 16 + game.SAVE_WIS + wis, 1))[0] if wis < 26 else 0
            if adjust:
                out.append((adjust, f"WIS {wis}"))
        if save == game.PPD_SAVE:
            con, race = self._ability(ti, 2), sheet[game.SHEET_RACE]
            small = race in (DWARF_RACE, HALFLING_RACE)
            if small:
                out.append((con * 2 // 7, f"{'dwarf' if race == DWARF_RACE else 'halfling'} CON {con}"))
            adjust = struct.unpack("b", self.guest.read(self.ds * 16 + game.SAVE_CON + con, 1))[0] if con < 26 else 0
            if small and self.rules & game.RULE_CON:
                adjust = 0  # (DSCLOG2's CON_SAVE)
            if adjust:
                out.append((adjust, f"CON {con}"))
        return [(amount, why) for amount, why in out if amount]

    def dual_level(self, creature: int, cls: int) -> int:
        """The level in CLS that counts (98h:C1h, 1D111h): a human's class past the first only while its
        level is below the first's (the game's test, as it is)."""
        sheet = self.sheet(creature)
        if len(sheet) < game.SHEET_SIZE:
            return 0
        for n in range(3):
            if sheet[game.SHEET_CLASSES + n] == cls:
                level = sheet[game.SHEET_LEVELS + n]
                if level and n and sheet[game.SHEET_RACE] == 1 and sheet[game.SHEET_LEVELS] <= level:
                    return 0
                return level
        return 0

    _names: Optional[List[str]] = None
    _names_at: Optional[int] = None

    def _name_list(self) -> List[str]:
        at = self._names_at
        if at is None or self.guest.read(at, len(NAMES_START)) != NAMES_START:
            low = self.guest.read(0, game.CONVENTIONAL_AND_UPPER)
            at = low.find(NAMES_START)
            if at < 0:
                return []
            end = low.find(b"\x00\x00", at)
            text = low[at:end if end > at else at + 4096].decode("latin1")
            self._names_at, self._names = at, [n.rstrip("\r") for n in text.split("\r\x00")]  # (the last one's CR, before its NULs)
        return self._names or []

    spell_names: List[str] = []  # (set by RavDiceLog.attach: spell_table's)

    def spell_name(self, spell: int) -> str:
        if spell in game.POISON_POWERS:  # (the monsters' poison, a Poisoner's: the records' "Mons273" and on)
            return game.POISON_POWERS[spell]
        if 0 <= spell < len(self.spell_names) and self.spell_names[spell]:
            return self.spell_names[spell]
        return super().spell_name(spell)

    def items_readable(self, creature: int) -> bool:
        """Whether a creature's items read as items: each name in the sequel's list, its type in range."""
        try:
            names = self._name_list()
            return bool(names) and all(1 <= struct.unpack_from("<H", item, game.ITEM_NAME)[0] <= len(names)
                                       and len(typ) == game.ITEM_TYPE_SIZE for _, item, typ in self._worn(creature))
        except (struct.error, IndexError, ValueError):
            return False

    mod_names: Optional[bytes] = None  # (DSCLOG2's ITEM_NAMES as the Loader wrote them: RavDiceLog._write_item_names)

    def item_name(self, name_index: int) -> str:
        """The sequel's list's name (1-255), else the Loader's own from 256 (ravager.NAMES_GAME: the mod's names,
        the Fine Bow and the spell arrows among them, then the transfer's keepsakes; DSCLOG2's ITEM_NAMES, which
        the game shows), else "item N"."""
        names = self._name_list()
        if 1 <= name_index <= len(names) and names[name_index - 1]:
            return names[name_index - 1]
        if ravager.NAMES_GAME <= name_index < ravager.NAMES_GAME + ravager.NAMES_ROOM:
            table = self.mod_names if self.mod_names is not None else ravager.item_names()
            at = (name_index - ravager.NAMES_GAME) * ravager.NAME_KEPT
            raw = table[at:at + ravager.NAME_KEPT].split(b"\0", 1)[0]
            if raw and game.plain_name(raw):
                return raw.decode("ascii")
        return f"item {name_index}"


# The sequel's areas (each RGNxx.GFF's RNME chunk names it: forest, Tyr, VA Headquarters, ...), for an
# autosave's name ("Auto - Day 1, 08:12 - Tyr")
REGIONS = {0x01: "The forest", 0x32: "Tyr", 0x33: "The Veiled Alliance", 0x34: "The pyramid",
           0x36: "The yuan-ti tunnels", 0x37: "El's temple", 0x38: "The mines, level 1", 0x39: "The mines, level 2",
           0x3A: "The mines, level 3", 0x3B: "The jann", 0x3C: "The mosaic", 0x3D: "The volcano, level 2",
           0x3E: "The volcano, level 1", 0x3F: "The volcano, level 3", 0x41: "The silt giants", 0x42: "The cloud",
           0x43: "The crypt", 0x44: "The cosmos", 0x45: "Under Tyr", 0xFF: "Limbo"}


def region_name(region: Optional[int]) -> str:
    if region is None:
        return ""
    return REGIONS.get(region) or f"Area {region:02X}h"


# ... and shorter, for an autosave's name in the sequel's narrower rows (QUICK_LAYOUT.name_most: "Auto Day 1,
# 09:05 Mines 1"; its LOAD window showed "Auto - Day 1, 00:06 - after a" of the name, 2026-11-25)
REGIONS_SHORT = {0x01: "Forest", 0x32: "Tyr", 0x33: "Alliance", 0x34: "Pyramid", 0x36: "Yuan-ti", 0x37: "Temple",
                 0x38: "Mines 1", 0x39: "Mines 2", 0x3A: "Mines 3", 0x3B: "Jann", 0x3C: "Mosaic",
                 0x3D: "Volcano 2", 0x3E: "Volcano 1", 0x3F: "Volcano 3", 0x41: "Giants", 0x42: "Cloud",
                 0x43: "Crypt", 0x44: "Cosmos", 0x45: "Under Tyr", 0xFF: "Limbo"}


def region_short(region: Optional[int]) -> str:
    if region is None:
        return ""
    return REGIONS_SHORT.get(region) or f"Area {region:02X}h"


# Quick save, quick load and autosave (quicksave.py) on DSCLOG2's QUICK SAVES: its header's fields past
# DSCLOG's (+1904 on: DSCLOG's +1878 to +1889 are others there), its MAIN_TICKS at DSCLOG's +260, and the
# sequel's addresses: the map's screen word (DS:0DABh, SL's 0BC9h), the save path (44F2h, SL's 4B81h, the
# Loader's "path" patch), the page letter in "SAVE??.SAV" and "SAVE%.2d.SAV" (DS:2085h + 3, 20B6h + 3), the
# save window's chosen row (its data 2F8h, the load + 3C4Ch: the word at 0; SL's 388h:4E4h). The sequel has
# no camp the F9 key breaks (its rests are at fire rings and inns, the party not on the map), and one page.
# An autosave's name at most 28 letters ("Auto Day 1, 00:06 fight"; the sequel's LOAD window cut "Auto - Day 1,
# 00:06 - after a fight" at 29 in its name field, and the row ran past its edge at 32)
# The page goes back to the game's E by DSCLOG2 itself (SAVE_TICK), not by the Loader (page_back False): the
# sequel's LOAD window runs passes of the map's main loop while it is open, so the Loader's test (the loop
# running, the game on the map, no answer waited for after ANSWER_WAIT) took the QUICK page off under F9's
# open window (seen in play, 2026-11-25), and a load from it would have read the game's own page's file.
RAV_NAME_MOST = 28
QUICK_LAYOUT = quicksave.Layout(keys=1904, seq=1908, req=1912, save_off=1914, tail_seg=1834, main_ticks=260,
                                greq=1916, screen_is=0x0DAB, save_path=0x44F2, name_find=0x2085 + 3,
                                name_save=0x20B6 + 3, window_from_ds=ravager.DGROUP - 0x3C4C, chosen=0,
                                camp=None, kept_pages=(b"E",), region_name=region_short,
                                name_most=RAV_NAME_MOST, name_join=" ", after_fight="fight",
                                page_back=False)
QUICK_GREQ_SAVES, QUICK_GREQ_LOADS = 1918, 1920  # (DSCLOG2's counts of the GREQ chunks written and read)


def wotr_folder(given: Optional[str]) -> Optional[str]:
    """The sequel's folder, where its saves are: GIVEN if it is one, else the one the Loader finds (wotrart's
    search: the folder chosen on the Options tab, beside Shattered Lands', GOG's usual places)."""
    if ravager.is_wotr_dir(given):
        return given
    from . import launch, wotrart
    try:
        found = wotrart.find_resources(launch.find_game_dir())
    except OSError:
        return None
    folder = found and __import__("os").path.dirname(found)
    return folder if ravager.is_wotr_dir(folder) else None


KIT_HEADER_BYTES = 6  # DSCLOG2's KIT_OUTDOORS, KIT_DANCE (4) and KIT_WILD, from the header's +350 (DSCLOG's)
# Picking pockets (pickpocket.py; DSCLOG2's PICK POCKETS, sites 180-186): its header's own words past the
# others' (DSCLOG's are at +176 to +189 there): +2000 PICK_ON (PICK_BUTTON), +2002 PICK_SEQ, +2004 PICK_REPLY,
# +2006 PICK_WHO (the map's thing), +2008 PICK_THIEF (the party member), +2010 PICK_TAKEN, +2012 PICK_TEXT's
# offset; +2014 to +2018 its counts (purses shown, picks readied, picks not answered in time)
PP_ON, PP_SEQ, PP_REPLY, PP_WHO, PP_THIEF, PP_TAKEN, PP_TEXT_OFF = 2000, 2002, 2004, 2006, 2008, 2010, 2012
PP_SHOWN, PP_ARMED, PP_LATE = 2014, 2016, 2018
# A Shinobi's try at a scroll (DSCLOG2's THE SHINOBI'S SPELLS): +2076 the d100 to read it and its chance
# (DSCLOG's +366 and +367), +2078 the spell's high byte (the new spells 320-325); +2080 to +2086 its counts
# (casting levels made, CHOOSE A SPELL asked, pages cut, scroll tries)
SH_LEARN_READ, SH_LEARN_SPELL_HI = 2076, 2078
SH_LEVELS, SH_ASKS, SH_PAGED, SH_SCROLLS = 2080, 2082, 2084, 2086
# The weapon traits' counts (DSCLOG2's THE TRIKAL AND THE TWO-HEADED WEAPONS, its header's +2020 to +2059): +2020
# a lotulis or double spear specialist's last swings turned on a second foe, +2022 the double spear's of them
# done 1 less, +2024 the first targets put back, +2026 a trikal specialist's hits that asked a save, +2028 trips
SF_SWINGS, SF_LESSES, SF_BACKS, TRIP_SAVES, TRIPS = 2020, 2022, 2024, 2026, 2028
# A Spellarcher's spell arrows (ravarrows.py; DSCLOG2's SPELL ARROWS, site 240 and PICK POCKETS' 180-185): its
# header's words from +2098: ARROWS_ON (the Loader's 1), ARROWS_SEQ, ARROWS_REPLY, ARROWS_WHO (the member),
# ARROWS_ROW (spellarrows.ARROWS' place); +2108 to +2112 its counts (buttons shown, asks late, buttons beside
# Turn Undead's drawn). The refusal's words go in PICK POCKETS' PICK_TEXT.
AR_ON, AR_SEQ, AR_REPLY, AR_WHO, AR_ROW = 2098, 2100, 2102, 2104, 2106
AR_SHOWN, AR_LATE, AR_DRAWN = 2108, 2110, 2112
DSCLOG2_SELL_DONE = 1884  # DSCLOG2's header (its own): SELL_SEQ as the Loader last saw to it (SHOP_LOOP waits on it)
DSCLOG2_DAC_CHANGES = 240  # DSCLOG2's header: the palette's changes counted (its own: DSCLOG's dust count there)
PANEL_H_MOST = 130  # (DSCLOG2's PANEL_H_MOST: the picture's rows at most)


# The sequel's dialogue portraits are its own (its PORTRAIT numbers aren't SL's faces): the Loader keeps them
# as RAV_PORTRAITS + the number, so the names given and learned (settings.json's "speakers", "speakers_learned")
# stay apart from Shattered Lands', and none of SL's own (game.SPEAKERS) is taken for one of them.
RAV_PORTRAITS = 10000


class SequelText:
    """DSCLOG2's text buffer (textlog.TextBuffer, its TEXT: the header's +126 to +138, DSCLOG's), each
    portrait's number made RAV_PORTRAITS + the game's (0, the emblem, kept: narration)."""

    def __init__(self, inner: textlog.TextBuffer):
        self.inner = inner

    def poll(self) -> List[textlog.TextRecord]:
        return [r._replace(value=RAV_PORTRAITS + r.value) if r.kind == textlog.KIND_PORTRAIT and r.value else r
                for r in self.inner.poll()]

    def __getattr__(self, name):
        return getattr(self.inner, name)


class RavDiceLog(dicelog.DiceLog):
    """dicelog.DiceLog for Wake of the Ravager: on its layout (apply_layout), its memory read only,
    and only the rolls (no side features after them yet)."""

    def __init__(self, guest, *args, **kwargs):
        apply_layout()
        super().__init__(ReadOnlyGuest(guest), *args, **kwargs)
        self._next_slots = 0.0
        self._next_stock = 0.0
        self.first_pick_weapon = True  # (a new warrior's weapon a +1 of its first pick: ravfirstweapon; off for a control)
        self.kit_start_gear = True  # (a new character's gear fitted to its classes and kit: ravkitstart; off for a control)
        self._stock: Optional[Dict[int, List[bytes]]] = None  # (shopstock's: the sellers' new items, read once)
        keys, auto = self.quicksave.keys, self.quicksave.auto
        self.quicksave = quicksave.QuickSave(QUICK_LAYOUT)  # (the sequel's: DSCLOG2's QUICK SAVES)
        self.quicksave.keys, self.quicksave.auto = keys, auto

    def attach(self) -> str:
        found = game.find_data_segment(self.guest.guest)
        self.guest.ds = found  # (the type table's pointer is in the data segment)
        if found is not None:
            path = resources_file()
            if path and not self.guest.spells:
                with open(path, "rb") as f:
                    self.guest.spells, RavGameData.spell_names = spell_table(f.read())
            load = found - ravager.DGROUP
            rebind("SPELLS_SEG", (SPELLS_AT + 0x10 - game.SPELLS_OFF) // 16 - load)
            rebind("CLASS_MAGIC_SEG", (CLASS_MAGIC_AT - game.CLASS_MAGIC_OFF) // 16 - load)
            names = effect_names(self.guest.guest, load)
            if names:
                rebind("EFFECT_NAMES", names)
        real, dicelog.GameData = dicelog.GameData, RavGameData  # (the base attach makes its GameData)
        try:
            result = super().attach()
        finally:
            dicelog.GameData = real
        self._write_item_names()
        if self.text is not None:  # (the sequel's portraits apart from SL's: RAV_PORTRAITS)
            self.text = SequelText(self.text)
        return result

    def speaker(self, portrait: Optional[int]) -> str:
        """SL's, for the sequel's portraits (RAV_PORTRAITS + the game's number): the names the player gave
        and the Loader learned, never SL's own faces' (game.SPEAKERS); else "Portrait N", the game's N."""
        if portrait is None or portrait < RAV_PORTRAITS:
            return super().speaker(portrait)
        return (self.speaker_names.get(portrait) or self.learned_speakers.get(portrait)
                or f"Portrait {portrait - RAV_PORTRAITS}")

    def _journal_sync(self) -> None:
        """The journal's look (SL's DiceLog._journal_sync), but the sequel's game keeps no id of it: SL's
        place in the game's numbers (journal.NUMBERS, at game.NUMBERS_PTR) isn't found in the sequel, nor two
        numbers its scripts leave alone. So the sequel's game is read as one begun (0) and nothing is written
        into it: its journal is a chain of its own from the Loader's start, not following its saves."""
        if self.journal is not None:
            self.journal.sync(lambda: 0, lambda head: False, self.game.game_time())

    def _tail_at(self, field: int) -> Optional[int]:
        """The address of a buffer of DSCLOG2's tail (TAIL: the tables and buffers it keeps outside its
        64 KB segment) whose offset is the header's word at FIELD: the tail's segment (+1834, as it sets it
        while loading) x 16 + the offset. None without the helper, or with either 0."""
        if self.tsr_hdr is None:
            return None
        seg, = struct.unpack("<H", self.guest.read(self.tsr_hdr + labels.TSR_TAIL_SEG, 2))
        off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + field, 2))
        return seg * 16 + off if seg and off else None

    def _write_item_names(self) -> None:
        """The mod's item names into DSCLOG2's ITEM_NAMES (its header's +196 in the tail, +198), if it has
        them."""
        at = self._tail_at(ravager.TSR_NAMES_OFF)
        if at is None:
            return
        count, = struct.unpack("<H", self.guest.read(self.tsr_hdr + ravager.TSR_NAMES_OFF + 2, 2))
        from . import launch, ravitems
        kept = ravager.read_added(launch.DOS_DIR).get(ravitems.NAMES_CHUNK, b"")
        names = ravager.item_names([n for n in kept.split(b"\n") if n])
        if self.game is not None:
            self.game.mod_names = names  # (the dice log's names for them too: RavGameData.item_name)
        if count * ravager.NAME_KEPT < len(names):  # (a helper before the names)
            return
        self.guest.guest.write(at, names)

    def set_rules(self, rules: int) -> None:
        """SL's, the rules ported to the sequel alone (ravager.RULES_PORTED), into DSCLOG2's header
        (+170, +270) made writable for them; the rest of SL's writes (the spell save's table, the
        stealth gear's word) dropped."""
        if self.tsr_hdr is not None:
            for r in ((self.tsr_hdr + dicelog.TSR_RULES, 2), (self.tsr_hdr + dicelog.TSR_RULES_HI, 2)):
                if r not in self.guest.writable:
                    self.guest.writable = self.guest.writable + [r]
        super().set_rules(rules & ravager.RULES_PORTED)

    def _set_stealth(self, hidden: bool, member: int = 0) -> None:
        """SL's: DSCLOG2's STEALTH (its header's +204) made writable and set, this party member's next
        attack one from behind (MISSILE_REAR); not the hiding's sound nor the figure drawn see-through
        (SL's SOUND_REQ and shadows: not in DSCLOG2 yet)."""
        if self.tsr_hdr is None:
            return
        word = (self.tsr_hdr + stealth.TSR_STEALTH, 2)
        if word not in self.guest.writable:
            self.guest.writable = self.guest.writable + [word]
        self.guest.write(word[0], struct.pack("<H", 1 << member if hidden else 0))

    def _slots_table(self) -> Optional[int]:
        """Where DSCLOG2's SLOTS_TEXT is (its header's +148, in the tail), made writable; None without the
        helper."""
        at = self._tail_at(dicelog.TSR_SLOTS_OFF)
        if at is None:  # (a helper before the spell slots: none)
            return None
        table = (at, game.PARTY_SIZE * dicelog.SLOTS_SIZE)
        if table not in self.guest.writable:
            self.guest.writable = [table] + self.guest.writable
        return table[0]

    def _label_slots(self) -> Optional[int]:
        """Where DSCLOG2's LBL_SLOTS are (its header's +1834:+1838, labels.slots_at), made writable;
        None without them (a helper before the labels)."""
        if self.tsr_hdr is None:
            return None
        seg, _, off = struct.unpack("<HHH", self.guest.read(self.tsr_hdr + labels.TSR_TAIL_SEG, 6))
        if not seg or not off:
            return None
        slots = (seg * 16 + off, labels.SLOTS * labels.SIZE)
        if slots not in self.guest.writable:
            self.guest.writable = self.guest.writable + [slots]
        return slots[0]

    def _large_bits(self) -> Optional[int]:
        """Where DSCLOG2's LARGE_BITS are (its header's +1834:+1842, as DSCLOG's tail), made writable;
        None without them (a helper before the creature size rule)."""
        if self.tsr_hdr is None:
            return None
        seg, = struct.unpack("<H", self.guest.read(self.tsr_hdr + sizes.TSR_TAIL_SEG, 2))
        off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + sizes.TSR_LARGE, 2))
        if not seg or not off:
            return None
        bits = (seg * 16 + off, sizes.LARGE_BYTES)
        if bits not in self.guest.writable:
            self.guest.writable = self.guest.writable + [bits]
        return bits[0]

    def _panel_ranges(self) -> bool:
        """DSCLOG2's combat log panel's picture (its far block, header +328:+140) and the header's
        words for it (+164 the Loader's stamp, +326 to +349 the panel's), made writable; False
        without them (a helper before the panel)."""
        if self.tsr_hdr is None:
            return False
        seg, = struct.unpack("<H", self.guest.read(self.tsr_hdr + combatlog.TSR_PANEL_SEG, 2))
        off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + combatlog.TSR_PANEL_OFF, 2))
        if not seg or not off:
            return False
        want = [(seg * 16 + off, combatlog.PANEL_W * PANEL_H_MOST),
                (self.tsr_hdr + dicelog.TSR_STATS_STAMP, 2),
                (self.tsr_hdr + combatlog.TSR_PANEL_ON, combatlog.TSR_KEYS + 2 - combatlog.TSR_PANEL_ON)]
        for r in want:
            if r not in self.guest.writable:
                self.guest.writable = self.guest.writable + [r]
        return True

    def _panel_pass(self, now: float) -> None:
        """The Loader's stamp (DSCLOG2 takes the panel off when it is old), the palette's changes
        (DSCLOG2's count, for the panel's colours: SL's shadows' count) and the panel drawn
        (dicelog.DiceLog._update_panel, as Shattered Lands' four times a second)."""
        if not self._panel_ranges():
            return
        self.guest.write(self.tsr_hdr + dicelog.TSR_STATS_STAMP, self.guest.read(dicelog.BIOS_TIMER, 2))
        self._shadows.palettes, = struct.unpack("<H", self.guest.read(self.tsr_hdr + DSCLOG2_DAC_CHANGES, 2))
        self._update_panel(now)

    def _look_ranges(self) -> Optional[int]:
        """DSCLOG2's Look box words (header +150 to +161) and its LOOK_TEXT, made writable; LOOK_TEXT's
        address, None without them (a helper before the Look box)."""
        if self.tsr_hdr is None:
            return None
        off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_LOOK_OFF, 2))
        if not off:
            return None
        base = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_HDR_OFF, 2))[0]
        full_at = self._tail_at(dicelog.TSR_LOOK_FULL_OFF)  # (LOOK_FULL: the tail's)
        for r in ((self.tsr_hdr + dicelog.TSR_LOOK_SEQ, dicelog.TSR_LOOK_ON + 2 - dicelog.TSR_LOOK_SEQ),
                  (base + off, dicelog.LOOK_SIZE)) + (((full_at, dicelog.LOOK_FULL_SIZE),) if full_at else ()):
            if r not in self.guest.writable:
                self.guest.writable = self.guest.writable + [r]
        return base + off

    def set_monster_info(self, on: bool) -> None:
        """Shattered Lands' switch, into DSCLOG2's header once it has the Look box."""
        self.monster_info = on
        if self._look_ranges() is not None:
            self.guest.write(self.tsr_hdr + dicelog.TSR_LOOK_ON, struct.pack("<H", int(on)))

    def _answer_look(self) -> List[str]:
        """Shattered Lands' (DSCLOG asks about a creature looked at in a fight), with the sequel's
        monster_lines: the Look box's short lines, and the whole description for the dialogue window as the
        box closes (DSCLOG2's LOOK_FULL, UNLOOK) when the helper has room for it (its header's +158)."""
        text_at = self._look_ranges()
        if text_at is None:
            return []
        seq, = struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_LOOK_SEQ, 2))
        if seq == self._look_seq:
            return []
        self._look_seq = seq
        who, = struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_LOOK_WHO, 2))
        short: List[str] = []
        full: List[str] = []
        index = self.game.combatant_creature(who)
        if index is not None and index >= game.PARTY_SIZE:
            try:
                short, full = monster_lines(self.game, index, self.monster_ac(index))
            except (struct.error, IndexError, ValueError):
                short, full = [], []
        text = "|".join(short).encode("cp437", "replace")[:dicelog.LOOK_SIZE - 1]
        full_at = self._tail_at(dicelog.TSR_LOOK_FULL_OFF)
        if full_at:  # (the window only when there's more to say than the box's HP, AC and THAC0, as SL's)
            whole = " ".join(full).replace("%", " pct").encode("cp437", "replace")[:dicelog.LOOK_FULL_SIZE - 1] \
                if len(full) > 1 else b""
            if whole and whole.decode("cp437") not in self._own_text:  # (not dialogue: the Dialogue tab leaves it out)
                self._own_text.append(whole.decode("cp437"))
            self.guest.write(full_at, whole + b"\0")
        self.guest.write(text_at, text + b"\0")
        self.guest.write(self.tsr_hdr + dicelog.TSR_LOOK_REPLY, struct.pack("<H", seq))
        return [f"Look: {full[0]}"] + [f"    {line}" for line in full[1:]] if full else []

    def _float(self, thing, text, colour, now, priority=0) -> None:
        """Shattered Lands' names over figures (labels.py), into DSCLOG2's slots once it has them."""
        if self._label_slots() is not None:
            super()._float(thing, text, colour, now, priority)

    def _kit_tick(self, now: float) -> None:
        """SL's (KIT_OUTDOORS, the dances and Wild Fighting ended with a fight), DSCLOG2's header bytes
        for them (+350 to +355, as DSCLOG's: its KITS) made writable while the kits are on."""
        if self.tsr_hdr is not None and self.game is not None and self.game.rules & game.RULE_KITS:
            kit_bytes = (self.tsr_hdr + dicelog.TSR_KIT_OUTDOORS, KIT_HEADER_BYTES)
            if kit_bytes not in self.guest.writable:
                self.guest.writable = self.guest.writable + [kit_bytes]
        super()._kit_tick(now)

    def _target_ranges(self) -> Optional[int]:
        """DSCLOG2's words for choosing an enemy and its ring (header +244 to +259: RINGS_ON, RED's
        offset, TARGET_ON, the Tab and Enter counts, HIT_TARGET; +230 and +232, PAN_X and PAN_Y, the
        view scrolled to the chosen enemy off the screen, as DSCLOG's: targeting.TSR_PAN) and RED, made
        writable; RED's address, None without them (a helper before Tab: its RED offset 0). (A helper
        before PAN had zeros there that nothing read: the Loader's adding to them did nothing.)"""
        if self.tsr_hdr is None:
            return None
        red_off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + rings.TSR_RED, 2))
        far, = struct.unpack("<H", self.guest.read(self.tsr_hdr + rings.TSR_FAR_SEG, 2))
        if not red_off or not far:
            return None
        for r in ((self.tsr_hdr + rings.TSR_RINGS_ON, targeting.TSR_ATTACK + 2 - rings.TSR_RINGS_ON),
                  (self.tsr_hdr + targeting.TSR_PAN, 4), (far * 16 + red_off, 256)):
            if r not in self.guest.writable:
                self.guest.writable = self.guest.writable + [r]
        return far * 16 + red_off

    def _target_pass(self, now: float) -> List[str]:
        """Shattered Lands' choosing an enemy (targeting.py: Tab and Shift+Tab counted by DSCLOG2, the
        enemies the nearest first, HIT_TARGET; the line "Chosen with Tab: ..., needs 14+ (35%)" with the
        chance to hit, hit_chance) and its ring (ring_mode; RED made from DSCLOG2's palette, DAC_TICK's,
        whenever it changes: rings.red_table in the sequel's colours)."""
        red_at = self._target_ranges()
        if red_at is None or self.game is None:
            return []
        foes = self._foes = rings.enemies(self.game)
        out = self._targeting.update(self.game, self.tsr_hdr, True, foes,
                                     lambda turn, chosen: hitchance.line(self._swings(turn, chosen)))
        on = self.ring_mode != rings.OFF
        changes, = struct.unpack("<H", self.guest.read(self.tsr_hdr + DSCLOG2_DAC_CHANGES, 2))
        if on and changes and changes != self._red_at and not self._gold:  # (RED gold while Alt marks: _marks)
            dac_off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + rings.TSR_DAC, 2))
            far, = struct.unpack("<H", self.guest.read(self.tsr_hdr + rings.TSR_FAR_SEG, 2))
            self.guest.write(red_at, rings.red_table(self.guest.read(far * 16 + dac_off, 768), RED_FIRST, RED_LAST))
            self._red_at = changes
        want = int(bool((on and self._red_at is not None) or self._gold))
        if want != self._rings_on:
            self.guest.write(self.tsr_hdr + rings.TSR_RINGS_ON, struct.pack("<H", want))
            self._rings_on = want
        return out

    _red_at: Optional[int] = None  # (DSCLOG2's count of palette changes RED was made at)
    _gold: Optional[int] = None  # (while Alt's rings are up: DSCLOG2's count of palette changes RED was made gold at)
    _ring_tab: Optional[bytes] = None  # (RING_TAB as last written)

    def _marks(self, now: float) -> None:
        """SL's (Alt held on the map out of a fight: a gold ring under everything that can be used, usable.py, the
        names of those nearest the pointer), on DSCLOG2's RING_TAB (its header's +246) and RED, which is the Tab
        ring's red again once Alt is let go (rings.py's Rings has the table's one owner in SL; here _target_pass
        makes RED red, and leaves it while the marks are up). Each change of the table has the view drawn again
        (DSCLOG2's VIEW_REDRAW)."""
        if self.game is None or not self._fight_keys_helper() or self._label_slots() is None:
            return
        if self.show_usable and self._labels.font is None and not self._labels_font_tried:
            self._labels_font_tried = True
            self._labels.font = dicelog._game_font(self.game_dir)
        table = self._usable.update(self.game, self.tsr_hdr, self.show_usable, now, self._labels)
        hdr = self.tsr_hdr
        far = struct.unpack("<H", self.guest.read(hdr + rings.TSR_FAR_SEG, 2))[0] * 16
        tab_at = far + struct.unpack("<H", self.guest.read(hdr + rings.TSR_RING_TAB, 2))[0]
        red_at = far + struct.unpack("<H", self.guest.read(hdr + rings.TSR_RED, 2))[0]
        changes = self._dac_changes()
        with self._writable([(tab_at, rings.THINGS), (red_at, 256), (hdr + FK_VIEW_REDRAW, 2),
                             (hdr + rings.TSR_RINGS_ON, 2)]):
            want = table or bytes(rings.THINGS)
            dac = lambda: self.guest.read(far + struct.unpack("<H", self.guest.read(hdr + rings.TSR_DAC, 2))[0], 768)
            if table is not None and self._gold != changes:  # (gold, made again when the palette changes)
                self.guest.write(red_at, rings.gold_table(dac(), RED_FIRST, RED_LAST))
                self._gold = changes
                if not self._rings_on:
                    self.guest.write(hdr + rings.TSR_RINGS_ON, struct.pack("<H", 1))
                    self._rings_on = 1
            elif table is None and self._gold is not None:  # (Alt let go: the Tab ring's red again)
                self._gold = None
                self.guest.write(red_at, rings.red_table(dac(), RED_FIRST, RED_LAST))
                self._red_at = changes
            if want != self._ring_tab:
                self.guest.write(tab_at, want)
                self._ring_tab = want
                shadows.redraw(self.game, hdr)
    _rings_on: Optional[int] = None  # (RINGS_ON as last written)

    @contextmanager
    def _writable(self, ranges: List[Tuple[int, int]]) -> Iterator[None]:
        """RANGES (address, size) writable while a pass runs, then read only again."""
        before = self.guest.writable
        self.guest.writable = before + [r for r in ranges if r not in before]
        try:
            yield
        finally:
            self.guest.writable = before

    def _fight_keys_helper(self) -> bool:
        """Whether DSCLOG2 has the squares, VIEW_REDRAW and RING_TAB (its header's +246, RING_TAB's offset, 0 in a
        helper before them)."""
        return self.tsr_hdr is not None and self.guest.read(self.tsr_hdr + rings.TSR_RING_TAB, 2) != b"\0\0"

    def _squares_ranges(self) -> List[Tuple[int, int]]:
        """What squares.Squares writes: SQUARES_ON, VIEW_REDRAW, SQ_MAP in DSCLOG2's PSP and LIGHT in its far block."""
        hdr = self.tsr_hdr
        far, = struct.unpack("<H", self.guest.read(hdr + rings.TSR_FAR_SEG, 2))
        light, = struct.unpack("<H", self.guest.read(hdr + FK_LIGHT, 2))
        return [(hdr + FK_VIEW_REDRAW, 2), (hdr + FK_SQUARES_ON, 2),
                (hdr - squares.PSP_BYTES + squares.SQ_MAP_PSP, squares.MAP_BYTES), (far * 16 + light, 256)]

    def _dac_changes(self) -> int:
        """DSCLOG2's count of the palette's changes (DAC_TICK's): LIGHT made again when it counts (SL's
        shadows.Shadows.palettes)."""
        return struct.unpack("<H", self.guest.read(self.tsr_hdr + DSCLOG2_DAC_CHANGES, 2))[0]

    def _squares_pass(self, now: float) -> None:
        """SL's squares in reach (squares.py, in SL's _drawn four times a second), on DSCLOG2's SQUARES, and
        Alt's rings (_marks) as often."""
        if now < self._next_squares or self.game is None or not self._fight_keys_helper():
            return
        self._next_squares = now + dicelog.EFFECT_INTERVAL
        with self._writable(self._squares_ranges()):
            self._squares.update(self.game, self.tsr_hdr, self.show_squares and self.squares_shown, self._dac_changes())
        self._marks(now)  # (Alt's rings: the view scrolled, the names nearest the pointer)

    _next_squares = 0.0

    def _dust_pass(self, now: float) -> None:
        """SL's dust (dust.py) on DSCLOG2's DUST: LIGHT made from the palette each time DSCLOG2 counts it changed
        (dust.light_table in the sequel's colours, RED_FIRST to RED_LAST: only sand and dirt have a lighter one), then
        DUST_ON set; DUST_ON cleared with SHOW_DUST off (RAV_NO_DUST, a control). Nothing for a helper without DUST
        (its DUST_SIG not there)."""
        if now < self._next_dust or self.game is None or not self._fight_keys_helper():
            return
        self._next_dust = now + dicelog.EFFECT_INTERVAL
        hdr = self.tsr_hdr
        if self.guest.read(hdr + DUST_SIG, 2) != struct.pack("<H", DUST_SIG_WORD):
            return
        far = struct.unpack("<H", self.guest.read(hdr + rings.TSR_FAR_SEG, 2))[0] * 16
        light = far + struct.unpack("<H", self.guest.read(hdr + FK_LIGHT, 2))[0]
        changes = self._dac_changes()
        with self._writable([(hdr + DUST_ON, 2), (light, 256)]):
            if not self.show_dust:
                if self._dust_light is not None or self.guest.read(hdr + DUST_ON, 2) != b"\0\0":
                    self.guest.write(hdr + DUST_ON, struct.pack("<H", 0))
                self._dust_light = None
                return
            if changes and changes != self._dust_light:
                dac_at = far + struct.unpack("<H", self.guest.read(hdr + rings.TSR_DAC, 2))[0]
                dac = self.guest.read(dac_at, 768)
                self.guest.write(light, dust.light_table(dac, RED_FIRST, RED_LAST, DUST_LEAST, DUST_LIGHTER))
                self._dust_light = changes
                self.guest.write(hdr + DUST_ON, struct.pack("<H", 1))

    _next_dust = 0.0

    def _ghost_pass(self, now: float) -> None:
        """SL's see-through figures (ghost.py) on DSCLOG2's: BLEND and REP made from the palette each time DSCLOG2
        counts it changed, GHOST_TAB from the effects; nothing for a helper without them (its GHOST_BLEND 0)."""
        if now < self._next_ghost or self.game is None or not self._fight_keys_helper():
            return
        self._next_ghost = now + dicelog.EFFECT_INTERVAL
        hdr = self.tsr_hdr
        if self.guest.read(hdr + GHOST_BLEND, 2) == b"\0\0":
            return
        if self._rav_ghosts is None:
            self._rav_ghosts = RavGhosts()
        at = self._rav_ghosts.places(self.guest, hdr)
        if at is None:
            return
        blend, rep, tab = at
        with self._writable([(blend, ghost.REP_COUNT * 256), (rep, 256), (tab, 80), (hdr + GHOST_ON, 2),
                             (hdr + FK_VIEW_REDRAW, 2)]):
            self._rav_ghosts.update(self.game, hdr, self.show_ghosts, self._dac_changes(),
                                lambda: shadows.redraw(self.game, hdr))

    _next_ghost = 0.0
    _rav_ghosts: Optional[RavGhosts] = None
    show_ghosts = True  # (the see-through figures: RAV_NO_GHOST, a control, turns them off)
    _dust_light: Optional[int] = None  # (DSCLOG2's palette count LIGHT was last made at)
    show_dust = True  # (the walkers' dust: RAV_NO_DUST, a control, turns it off)

    def _squares_key(self, now: float) -> List[str]:
        """SL's (R on the map in a fight shows or hides the squares in reach, read from the BIOS keyboard
        buffer: keywatch.py; the sequel's map keys, its table at 1F091h, have no R), on DSCLOG2's SQUARES."""
        if self.game is None:
            return []
        pressed = [key for key in self._keys.take(self.game.guest) if key in (keywatch.KEY_R, keywatch.KEY_SHIFT_R)]
        if not pressed or not self.show_squares or not self._fight_keys_helper():
            return []
        if self.game._word(quicksave.SCREEN_IS) != quicksave.ON_MAP or not self.game.in_combat():
            return []
        if len(pressed) % 2 == 0:  # (pressed twice between two looks: as it was)
            return []
        self.squares_shown = not self.squares_shown
        dicelog._remember({"squares_shown": self.squares_shown})
        with self._writable(self._squares_ranges()):
            self._squares.update(self.game, self.tsr_hdr, self.squares_shown, self._dac_changes())
        turn = self.game.whose_turn()
        self._float(turn if turn is not None and turn < game.PARTY_SIZE else 0,
                    "Squares shown" if self.squares_shown else "Squares hidden", labels.SPELL_INK, now)
        return ["Squares in reach: shown (R hides them)" if self.squares_shown
                else "Squares in reach: hidden (R shows them)"]

    def _move_back_pass(self) -> List[str]:
        """SL's (moveback.py: F10 after the last step gives the walk back), the member's turn flags and its
        walk's words made writable while it runs."""
        if self.game is None or not self.game.in_combat():
            return super()._move_back_pass()
        turn = self.game.whose_turn()
        creature = self.game.combatant_creature(turn) if turn is not None and turn < game.PARTY_SIZE else None
        if creature is None:
            return super()._move_back_pass()
        load = self.game.load_seg
        flags = (load + moveback.POINTS_SEG) * 16 + moveback.FLAGS_OFF + creature * 2
        walk = (load + moveback.WALK_SEG) * 16
        with self._writable([(flags, 2), (walk + moveback.WALK_STEP + turn * moveback.WALK_STEP_SIZE, 1),
                             (walk + moveback.WALK_LEFT + turn * moveback.WALK_LEFT_SIZE, 2)]):
            return super()._move_back_pass()

    def _quick_ranges(self) -> bool:
        """DSCLOG2's quick save words (its header's +1904 to +1917), SAVE_TEXT, and the game's page letters
        and the save window's chosen row, made writable (quicksave.QuickSave.ranges); False without them (a
        helper before QUICK SAVES: SAVE_TEXT's offset 0)."""
        if self.tsr_hdr is None or self.game is None:
            return False
        off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + QUICK_LAYOUT.save_off, 2))
        if not off:
            return False
        for r in self.quicksave.ranges(self.game, self.tsr_hdr):
            if r not in self.guest.writable:
                self.guest.writable = self.guest.writable + [r]
        return True

    def _quick_pass(self, loading: bool, now: float) -> List[str]:
        """Shattered Lands' (quicksave.py: F5, F9, the autosaves; "Quick save" over the leader), on DSCLOG2's
        QUICK SAVES, the saves in the sequel's folder (wotr_folder)."""
        if not self._quick_ranges():
            return []
        if not self._quick_dir:
            self._quick_dir = wotr_folder(self.game_dir) or ""
        return super()._quick_pass(loading, now)

    def _write_slots(self) -> None:
        """Shattered Lands' (the lines for the USE screen), into DSCLOG2's SLOTS_TEXT."""
        if self._slots_table() is not None:
            super()._write_slots()

    def _slots_at(self) -> int:
        """(SL's _write_slots' table: DSCLOG2's is in its tail.)"""
        return self._slots_table()

    def _hit_effects(self, attacker: int, attacker_combatant: int, target_combatant: int, mode: Optional[int],
                     item_type: Optional[int], e) -> List[Tuple[str, int]]:
        """The sequel's to-hit routine (628h:66h, 8599Eh; SL's 5B8h:EDh), besides STR or DEX: the target's
        Life Drained, the attacker's effects (HIT_EFFECTS_RAV; Berserk by its preserver level), a Soothe's
        Extra Hit Points in melee, the target's Blurry, Prayer, a halfling's +1 with a sling or a thrown
        weapon (a range past HALFLING_RANGE); the girdle of Urnst (DSCLOG2's ITEM_REAR)."""
        g = self.game
        mine, theirs = g._effect_ids(attacker_combatant), g._effect_ids(target_combatant)
        parts: List[Tuple[str, int]] = []
        drained = g._first_effect(target_combatant, LIFE_DRAINED)
        if drained is not None and drained[8]:
            parts.append((f"target's Life Drained ({drained[8]})", -2 * drained[8]))
        parts += [(name, value) for eid, value, name in HIT_EFFECTS_RAV if eid in mine]
        if BERSERK in mine:
            level = g.dual_level(attacker, BERSERK_CLASS) - 1
            parts.append(("Berserk", level - int(level / 3)))
        if EXTRA_HP in mine and mode is not None and mode <= 1:
            extra = g._first_effect(attacker_combatant, EXTRA_HP)
            if extra is not None and struct.unpack_from("<H", extra, 4)[0] == SOOTHE:
                parts.append(("Soothe", -2))
        if BLURRY in theirs:
            parts.append(("target's Blurry", -2))
        if PRAYER in mine:
            prayer = g._first_effect(attacker_combatant, PRAYER)
            same = prayer is not None and g._side(struct.unpack_from("<h", prayer, 2)[0]) == g._side(attacker_combatant)
            parts.append(("Prayer", 1 if same else -1))
        sheet = g.sheet(attacker)
        if len(sheet) > game.SHEET_RACE and sheet[game.SHEET_RACE] == HALFLING_RACE and mode is not None \
                and mode > HALFLING_RANGE and item_type is not None and 0 <= item_type < 0x400:
            flags = g.guest.read(game.far_pointer(g.guest, g.ds, game.ITEM_TYPES_PTR)
                                 + item_type * game.ITEM_TYPE_SIZE, 1)
            if flags and (flags[0] & 0x10 or flags[0] & 2 and not flags[0] & 8):
                parts.append(("halfling", 1))
        on = lambda combatant, eid: eid in g._effect_ids(combatant)
        return parts + self._mod_hit_effects(attacker_combatant, target_combatant, mode, item_type, on)

    def _mod_hit_effects(self, attacker_combatant: int, target_combatant: int, mode: Optional[int],
                         item_type: Optional[int], on) -> List[Tuple[str, int]]:
        """SL's, the girdle of Urnst alone (DSCLOG2's ITEM_REAR): the sequel has no Fogbolt, and a stinkpot's
        Nauseated is taken off after the set-up (_after_setup)."""
        return [part for part in super()._mod_hit_effects(attacker_combatant, target_combatant, mode, item_type, on)
                if part[0] == "target's Girdle of Urnst"]

    CLAW_IN_SETUP = False  # (DSCLOG2's NS_SWING, after the set-up: _after_setup)

    def _after_setup(self, attacker_combatant: Optional[int], target_combatant: Optional[int] = None,
                     e=None, item: Optional[int] = None) -> List[Tuple[str, int]]:
        """A nauseated attacker's -2 (DSCLOG2's STINK_SWING, at the hit routine's swing: after the set-up);
        with the new spells (DSCLOG2's NS_SWING) a fogged attacker's -3, +2 on a fogged target, and Erdlu
        Claw's +1 for an unarmed attack of the first set (the set-up's SETUP_NATURAL_LOCAL 0)."""
        out: List[Tuple[str, int]] = []
        if attacker_combatant is None:
            return out
        mine = self.game._effect_ids(attacker_combatant)
        if ravager.NAUSEATED in mine:
            out.append(("Nauseated", -STINK_TO_HIT))
        if not self.game.rules & game.RULE_NEW_SPELLS:
            return out
        if ravspells.FOG_EFFECT in mine:
            out.append(("Fogbolt", -3))
        if target_combatant is not None and ravspells.FOG_EFFECT in self.game._effect_ids(target_combatant):
            out.append(("target's Fogbolt", 2))
        natural = e.parent_local(game.SETUP_NATURAL_LOCAL) if e is not None else None
        if ravspells.CLAW_EFFECT in mine and (item is None or item < 0 or item >= game.NO_ITEM) \
                and natural is not None and natural & game.SETUP_FLAG_MASK == 0:
            out.append(("Erdlu Claw", 1))
        return out

    def _plus_counts(self, target_combatant: int, on) -> bool:
        """The weapon's plus counts unless the target has an Anti Magic Shell (the set-up's 608h:20h, 5C745h)."""
        return not on(target_combatant, ANTI_MAGIC)

    def _is_save_roll(self, e) -> bool:
        """SL's, with the sequel's saving throw's frame (66D26h): the target's creature record's far
        pointer at [BP-0Ah] (SL's [BP-1Eh]), set before the d20 (66E33h)."""
        target = e.parent_arg(6)
        index = self.game.combatant_creature(target) if target is not None else None
        off, seg = e.parent_local(-0x0A), e.parent_local(-0x08)
        if index is None or off is None or seg is None:
            return False
        table = game.far_pointer(self.guest, self.game.ds, game.CREATURES_PTR)
        return (seg & 0xFFFF) * 16 + (off & 0xFFFF) == table + index * game.CREATURE_SIZE

    def _blast_pass(self, now: float) -> List[str]:
        """Psionic Blast's imagined wounds given back as a fight ends (SL's psiblast.BlastWatch): DSCLOG2's
        BLAST_HP (its header's +1814, BLAST_LOSS) and the party's hit points and status made writable."""
        if self.tsr_hdr is None or self.game is None:
            return []
        table = game.table_pointer(self.guest, self.game.ds, game.CREATURES_PTR)
        want = [(self.tsr_hdr + psiblast.TSR_BLAST, 2 * game.PARTY_SIZE)]
        for c in range(game.PARTY_SIZE):
            at = table + c * game.CREATURE_SIZE
            want += [(at, 2), (at + game.CREATURE_STATUS, 1)]
        self.guest.writable = self.guest.writable + [r for r in want if r not in self.guest.writable]
        return self._blast.tick(self.game, self.tsr_hdr, now)

    RAV_LEAST_MOST = 17  # (the sequel's least for a score: a class's prime requisite 17, the others 9 to 14)
    _creation_shown: Optional[List[int]] = None

    def creation_lines(self) -> List[str]:
        """SL's, with the scores shown noted first for _ability_line."""
        self._creation_shown = self.game.creation_abilities()
        return super().creation_lines()

    def _ability_line(self, ability: int, tries: List[int], sheet: bytes, classes: List[int]) -> Tuple[int, str]:
        """SL's, with the sequel's own least: it keeps the game's rule (each class's prime requisite 17,
        every other score one number a class, 9 to 14; SL's least_scores, the manual's table, isn't
        ported), so a score shown above the roll and no more than 17 was raised to it."""
        value, line = super()._ability_line(ability, tries, sheet, classes)
        shown = self._creation_shown
        if shown is not None and value < shown[ability] <= self.RAV_LEAST_MOST and "raised to" not in line:
            value = shown[ability]
            steps = line.split(": ", 1)[1]
            line = f"Character creation, {dicelog.ABILITIES[ability]} {value}: {steps}, raised to {value} " \
                   f"(the classes' least)"
        return value, line

    def _creation_pass(self, now: float) -> List[str]:
        """SL's creation lines from DSCLOG2's RL_TRY (its header's +280, +282: each try's 4d4): once the
        die has been still CREATION_HP_WAIT, each ability's best of four 4d4, +4, the race's adjustment."""
        self._creation_tries_moved(now)
        if (self._creation_hp or self._creation_abilities or self._tries_new) \
                and now - self._creation_hp_at >= dicelog.CREATION_HP_WAIT:
            return self.creation_lines()
        return []

    def _after_rolls(self, show_all: bool, now: float) -> List[str]:
        """Of Shattered Lands' pass after the rolls, only the hit points' changes (hp_changes: each
        fall matched with the weapon hits it took in, regeneration, spells' damage), the names over
        figures whose time is up (labels.Labels.tick), the spell slots' lines for the USE screen
        (_write_slots, as often as Shattered Lands' writes them), a wizard's try at a scroll's spell
        (_learn_lines), Psionic Blast's wounds given back (_blast_pass), the creation screen's tries
        (_creation_pass), the combat log's panel (_panel_pass), and the dialogue and message boxes for the
        Dialogue and Journal tabs and the "Message:" lines (_take_text, DSCLOG2's TEXT; the journal its own
        chain: _journal_sync): the rest reads and writes what isn't ported yet."""
        out = self._step(self._gear_pass)  # (a new character's fuller starting gear: DONE waits for it)
        self._step(self._forget_undone_picks)  # (pockets tried since the save loaded: forgotten)
        out += self._step(self._answer_pick)  # (a thief's Pick Pockets button: DSCLOG2's PICK POCKETS, PP_HAND waits)
        out += self._step(self._answer_arrows)  # (a Spellarcher's arrows buttons: DSCLOG2's SPELL ARROWS waits)
        out += self._step(self._strays_pass)  # (spell arrows only a Spellarcher carries: ravarrows.return_strays)
        out += self._step(lambda: self.hp_changes(now))
        out += self._step(lambda: self._blast_pass(now))
        out += self._step(lambda: self._creation_pass(now))
        self._step(lambda: self._kit_tick(now))  # (the kits: who is under the open sky, a fight's end)
        if self.monster_info:  # (the Look box: answered at once, the game waits for it)
            self.set_monster_info(True)
            out += self._step(self._answer_look)
        if self._label_slots() is not None:  # (names over figures: those whose time is up taken off)
            self._labels.on = self.floating_names
            self._step(lambda: self._labels.tick(self.guest, self.tsr_hdr, now))
        out += self._step(lambda: self._target_pass(now))  # (Tab, Enter and the ring: DSCLOG2's TARGETING)
        out += self._step(lambda: self._squares_key(now), quiet=True)  # (R: the squares in reach, SQUARES)
        self._step(lambda: self._squares_pass(now), quiet=True)
        self._step(lambda: self._dust_pass(now), quiet=True)  # (the walkers' dust: DSCLOG2's DUST)
        self._step(lambda: self._ghost_pass(now), quiet=True)  # (the hidden and invisible see-through)
        out += self._step(self._move_back_pass, quiet=True)  # (F10 after the last step: moveback.py)
        self._step(lambda: self._usable_key(now), quiet=True)  # (Alt held: what can be used ringed, usable.py)
        if self._label_slots() is not None:  # (the chance to hit over the enemy under the pointer: hover.py)
            self._step(lambda: self._hover_pass(now))
        if self._large_bits() is not None:  # (the creature size rule: who is large, for DSCLOG2's IS_LARGE)
            self._step(lambda: self._large.update(self.game, self.tsr_hdr))
        out += self._step(self._learn_lines)  # (a wizard's try at a scroll: DSCLOG2's INT_LEARN, +272)
        if self.text is not None:  # (dialogue and message boxes: DSCLOG2's TEXT, +126)
            out += self._step(lambda: self._take_text(now))
        out += self._step(self._loot_pass)  # (T and Shift+T: a container's things to the backpacks, LOOT_KEY)
        out += self._step(self._sell_pass)  # (S: the member's plain gear sold, SELL_KEY)
        out += self._step(lambda: self._stock_pass(now))  # (a saved game's sellers given the new items: shopstock)
        if self.game is not None and self.game.rules & game.RULE_STEALTH:
            out += self._step(self.turn_lines)  # (whose turn, a thief's hiding: stealth.turn, DSCLOG2's STEALTH)
        if now >= self._next_slots:
            self._next_slots = now + dicelog.EFFECT_INTERVAL
            self._step(self._write_slots)
            out += self._step(lambda: self._panel_pass(now))
            if self.game is not None and self.game.rules & game.RULE_AGING:
                out += self._step(self._aging_pass)
            out += self._step(self._party_pass)  # (the sequel's own party's weapon specs and features, once)
            try:
                loading = self._party_check(now)
            except Exception:  # (unknown: no save asked for this pass)
                loading = True
            out += self._step(lambda: self._quick_pass(loading, now))  # (F5, F9, the autosaves: DSCLOG2's QUICK SAVES)
            if not loading:
                self._step(self._journal_sync)  # (the Journal tab: the sequel's own chain)
        return out

    @contextmanager
    def _items_writable(self, header: Tuple[int, ...] = ()) -> Iterator[None]:
        """The bytes looting and selling write (loot.py, sell.py: pickpocket's and ring's item moves) made
        writable while they run, then read only again: the item table, the things, the free lists' words,
        the party's three item lists' heads, the party's money, and the helper's header words HEADER (their
        offsets). The item gate (itemgate.py) holds the game still for the writes, as in Shattered Lands."""
        gd, before = self.game, self.guest.writable
        ds = gd.ds * 16
        creatures = game.table_pointer(self.guest, gd.ds, game.CREATURES_PTR)
        want = [(game.far_pointer(self.guest, gd.ds, game.ITEMS_PTR), itemgate.ITEM_RECORDS * game.ITEM_SIZE),
                ((gd.load_seg + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF,
                 (itemgate.THING_COUNT + itemgate.THINGS_PAST) * 3),
                (ds + ring.FREE_THINGS, 2), (ds + ring.THINGS_USED, 2), (ds + ring.FREE_ITEMS, 2),
                ((gd.load_seg + game.MONEY_SEG) * 16 + game.MONEY, 4)]
        want += [(creatures + c * game.CREATURE_SIZE + game.CREATURE_ITEM_LISTS[0], 6) for c in range(game.PARTY_SIZE)]
        want += [(self.tsr_hdr + at, 2) for at in header]
        self.guest.writable = before + [r for r in want if r not in before]
        try:
            yield
        finally:
            self.guest.writable = before

    def _gear_pass(self) -> List[str]:
        """Fuller starting gear (startgear.fill, the sequel's items: rav_items), on DSCLOG2's GEAR_DONE: the
        Loader's heartbeat (LOADER_BEAT, its header's +1865) written every pass, and with GEAR_DUE (+1830) set
        the new character DONE has just made (GEAR_WHO, +1867: game.being_new's GD.making) given its gear
        while DONE waits; then the members whose items changed (GEAR_GIVEN, +1831) and GEAR_DUE cleared. The
        item moves writable while it runs (_items_writable); the game's item lists moving: the next pass."""
        if self.tsr_hdr is None or self.game is None:
            return []
        hdr = self.tsr_hdr
        want = [(hdr + dicelog.TSR_GEAR_DUE, 2), (hdr + dicelog.TSR_LOADER_BEAT, 2), (hdr + dicelog.TSR_GEAR_WHO, 1)]
        self.guest.writable = self.guest.writable + [r for r in want if r not in self.guest.writable]
        self.guest.write(hdr + dicelog.TSR_LOADER_BEAT, self.guest.read(dicelog.BIOS_TIMER, 2))
        if not self.guest.read(hdr + dicelog.TSR_GEAR_DUE, 1)[0]:
            return []
        out: List[str] = []
        if self.starting_gear or self.first_pick_weapon or self.kit_start_gear:
            if not self._items_still():
                return []
            def items() -> Dict[int, frozenset]:
                mine: Dict[int, set] = {}
                for i in self.game.party_items():
                    mine.setdefault(i.member, set()).add((i.index, i.record))
                return {m: frozenset(v) for m, v in mine.items()}
            before = items()
            who = self.guest.read(hdr + dicelog.TSR_GEAR_WHO, 1)[0]
            self.game.making = None if who == 0xFF else who
            new_items = (getattr(self, "_settings", None) or {}).get("new_items", True) is not False
            self.game.new_items = new_items  # (ravgear's items there: rav_weapon, ravfirstweapon)
            try:
                with self._items_writable():
                    if self.first_pick_weapon:  # (a warrior's weapon a +1 of its first pick: ravfirstweapon)
                        out += ravfirstweapon.fill(self.game, new_items)
                    if self.kit_start_gear:  # (the kit's: ravkitstart, its armour made leather before the
                        if self.game.rules & game.RULE_KITS:  # classes' step leaves it behind; then what the
                            out += ravkitstart.kit_gear(self.game, new_items)  # classes can't use left behind)
                        out += weaponchoice.class_gear(self.game)
                    if self.starting_gear:
                        out += startgear.fill(self.game)
                    if self.first_pick_weapon or self.kit_start_gear:  # (the weapon in hand first in its list: the weapon lines)
                        ravfirstweapon.weapon_first(self.game)
            finally:
                self.game.making = None
                itemgate.release(self.game)
            after = items()
            given = sum(1 << m for m in range(game.PARTY_SIZE) if before.get(m) != after.get(m))
            self.guest.write(hdr + dicelog.TSR_GEAR_GIVEN, bytes((given,)))
        self.guest.write(hdr + dicelog.TSR_GEAR_DUE, b"\0")
        return out

    def _answer_pick(self) -> List[str]:
        """Shattered Lands' Pick Pockets button (DiceLog._answer_use's PICKED_BY: pickpocket.attempt), on
        DSCLOG2's PICK POCKETS: PICK_ON (its header's +2000) set while the helper has it; someone clicked on
        with the thief's pointer (PICK_SEQ, +2002, ahead of PICK_REPLY), their pocket tried by that thief
        (PICK_THIEF), the item gate held and the request looked at again before anything is moved (one
        DSCLOG2 gave up waiting for is dropped); what came of it into PICK_TEXT (+2012's), PICK_TAKEN set
        and PICK_REPLY given PICK_SEQ. No XP and no purse's sound (the sequel's helper has neither)."""
        if self.tsr_hdr is None or self.game is None:
            return []
        hdr = self.tsr_hdr
        text_off, = struct.unpack("<H", self.guest.read(hdr + PP_TEXT_OFF, 2))
        if not text_off:
            return []  # (a helper before PICK POCKETS)
        base = hdr - struct.unpack("<H", self.guest.read(hdr + dicelog.TSR_HDR_OFF, 2))[0]
        want = [(hdr + PP_ON, PP_TEXT_OFF - PP_ON), (base + text_off, dicelog.PICK_SIZE)]
        self.guest.writable = self.guest.writable + [r for r in want if r not in self.guest.writable]
        if self.guest.read(hdr + PP_ON, 2) != struct.pack("<H", dicelog.PICK_BUTTON):
            self.guest.write(hdr + PP_ON, struct.pack("<H", dicelog.PICK_BUTTON))
        seq = self.guest.read(hdr + PP_SEQ, 2)
        if seq == self.guest.read(hdr + PP_REPLY, 2):
            return []
        result = None
        try:
            thing, thief = struct.unpack("<HH", self.guest.read(hdr + PP_WHO, 4))
            with self._items_writable():
                itemgate.hold(self.game)  # (held, DOSBox paused, before anything is moved)
                try:
                    if self.guest.read(hdr + PP_REPLY, 2) == seq:
                        return []  # (DSCLOG2 gave up waiting: the talk went on, nothing moved)
                    it = ring.Items(self.game)
                    kind, index = it.thing(thing) if 0 <= thing < ring.THING_COUNT else (None, None)
                    if self._fighting():
                        result = pickpocket.Attempt(pickpocket.NOT_IN_A_FIGHT, [])
                    elif kind == 2:
                        creatures = game.table_pointer(self.guest, self.game.ds, game.CREATURES_PTR)
                        lists = (creatures + index * game.CREATURE_SIZE + game.CREATURE_ITEM_LISTS[0], 6)
                        self.guest.writable = self.guest.writable + [lists]  # (the person's lists, emptied)
                        result = pickpocket.attempt(self.game, self.picked, who=index, thief=thief & 0xFF)
                    if result is None:
                        result = pickpocket.Attempt("There are no pockets to pick there.", [])
                finally:
                    itemgate.release(self.game)
        except itemgate.ItemsBusy:
            return []  # (the game changing its item lists: answered in a later pass)
        except (struct.error, IndexError, ValueError):
            result = None
        text = (result.text if result else "").encode("cp437", "replace")[:dicelog.PICK_SIZE - 1]
        self.guest.write(base + text_off, text + b"\0")
        self.guest.write(hdr + PP_TAKEN, struct.pack("<H", int(result is not None)))
        self.guest.write(hdr + PP_REPLY, seq)
        if not result:
            return []
        if result.key:
            self._remember_pick(result.key)
        if result.text and result.text not in self._own_text:  # (not dialogue: the Dialogue tab leaves it out)
            self._own_text.append(result.text)
        return result.log or [result.text]

    spell_arrows = True  # (a Spellarcher's arrows buttons: ARROWS_ON; off for a control)

    def _arrows_ready(self) -> bool:
        """Whether the Loader's copy of OBJEX.GFF has the spell arrows' objects (ravarrows.chunks): without
        them an arrow made would be an item of no object, so no buttons are offered. Read once."""
        if getattr(self, "_arrows_objects", None) is None:
            import os
            from . import launch, ravarrows
            try:
                with open(os.path.join(launch.DOS_DIR, ravager.OBJECTS_COPY), "rb") as f:
                    chunks = gff.read_gff(f.read())
                self._arrows_objects = ("OJFF", ravarrows.own_object(ravarrows.ARROWS[0].row)) in chunks
            except (OSError, gff.GffError, struct.error):
                self._arrows_objects = False
        return self._arrows_objects

    def _answer_arrows(self) -> List[str]:
        """Shattered Lands' spell arrows made (DiceLog._answer_use's ARROWS_BY: spellarrows.SpellArrows.make), on
        DSCLOG2's SPELL ARROWS: ARROWS_ON (its header's +2098) set while the arrows' objects are there
        (_arrows_ready); an arrows button let go of (ARROWS_SEQ, +2100, ahead of ARROWS_REPLY), ravarrows.make for
        that member (ARROWS_WHO) and spell (ARROWS_ROW) under the item gate, the request looked at again first
        (one DSCLOG2 gave up waiting for is dropped); a refusal's words into PICK_TEXT (PICK POCKETS' +2012's),
        empty when made, and ARROWS_REPLY given ARROWS_SEQ."""
        if self.tsr_hdr is None or self.game is None:
            return []
        hdr = self.tsr_hdr
        text_off, = struct.unpack("<H", self.guest.read(hdr + PP_TEXT_OFF, 2))
        if not text_off:
            return []  # (a helper before PICK POCKETS)
        base = hdr - struct.unpack("<H", self.guest.read(hdr + dicelog.TSR_HDR_OFF, 2))[0]
        want = [(hdr + AR_ON, 2), (hdr + AR_REPLY, 2), (base + text_off, dicelog.PICK_SIZE)]
        self.guest.writable = self.guest.writable + [r for r in want if r not in self.guest.writable]
        on = struct.pack("<H", int(self.spell_arrows and self._arrows_ready()))
        if self.guest.read(hdr + AR_ON, 2) != on:
            self.guest.write(hdr + AR_ON, on)
        seq = self.guest.read(hdr + AR_SEQ, 2)
        if seq == self.guest.read(hdr + AR_REPLY, 2):
            return []
        from . import ravarrows
        result = None
        try:
            member, row = struct.unpack("<HH", self.guest.read(hdr + AR_WHO, 4))
            with self._items_writable():
                if 0 <= member < game.PARTY_SIZE:
                    self.guest.writable = self.guest.writable + [ravarrows.slots_range(self.game, member)]
                itemgate.hold(self.game)  # (held, DOSBox paused, before anything is moved)
                try:
                    if self.guest.read(hdr + AR_REPLY, 2) == seq:
                        return []  # (DSCLOG2 gave up waiting: nothing made)
                    if self._fighting():
                        result = pickpocket.Attempt(spellarrows.NOT_IN_A_FIGHT, [])
                    else:
                        result = ravarrows.make(self.game, member, row)
                finally:
                    itemgate.release(self.game)
        except itemgate.ItemsBusy:
            return []  # (the game changing its item lists: answered in a later pass)
        except (struct.error, IndexError, ValueError):
            result = None
        text = (result.text if result else "").encode("cp437", "replace")[:dicelog.PICK_SIZE - 1]
        self.guest.write(base + text_off, text + b"\0")
        self.guest.write(hdr + AR_REPLY, seq)
        if result and result.text and result.text not in self._own_text:
            self._own_text.append(result.text)
        return ravarrows.lines_for(result)

    def _strays_pass(self) -> List[str]:
        """Spell arrows another party member carries given back to the Spellarcher, or taken out of its quiver
        (ravarrows.return_strays: Shattered Lands' return_strays, with the kits; out of a fight, the map up), the
        item moves writable while it runs; the game's item lists moving: a later pass."""
        if self.tsr_hdr is None or self.game is None or not self.game.rules & game.RULE_KITS:
            return []
        from . import ravarrows
        try:
            with self._items_writable():
                return ravarrows.return_strays(self.game)
        except itemgate.ItemsBusy:
            return []
        finally:
            itemgate.release(self.game)

    def _stock_pass(self, now: float) -> List[str]:
        """A saved game's sellers given the mod's new items once (shopstock.py), every STOCK_INTERVAL while the
        new items are on (the "new_items" setting): the sellers loaded and not yet marked, then, with the game's
        item lists still (_items_still), their items added and their mark set, the item moves and each one's
        lists and mark writable while it runs (_items_writable)."""
        if self.tsr_hdr is None or self.game is None or now < self._next_stock:
            return []
        self._next_stock = now + STOCK_INTERVAL
        if (getattr(self, "_settings", None) or {}).get("new_items", True) is False:
            return []
        if self._stock is None:
            self._stock = shopstock.from_file(shopstock.default_path())
        if not self._stock:
            return []
        due = shopstock.due(self.game, self._stock)
        if not due or not self._items_still():
            return []
        creatures = game.table_pointer(self.guest, self.game.ds, game.CREATURES_PTR)
        out: List[str] = []
        try:
            with self._items_writable():
                before = self.guest.writable
                for c in due:
                    at = creatures + c * game.CREATURE_SIZE
                    want = [(at + game.CREATURE_ITEM_LISTS[0], 6), (at + shopstock.CREATURE_MARK, 1)]
                    self.guest.writable = self.guest.writable + [r for r in want if r not in self.guest.writable]

                    def mark(creature: int, at: int = at) -> None:
                        self.guest.write(at + shopstock.CREATURE_MARK, bytes((shopstock.MARKED,)))
                    out += shopstock.top_up(self.game, c, self._stock, mark)
                self.guest.writable = before
        finally:
            itemgate.release(self.game)
        return out

    def _loot_pass(self) -> List[str]:
        """Shattered Lands' (T or Shift+T with a container's window open: what is in it into the party's
        backpacks once the window is shut, loot.py), on DSCLOG2's LOOT_KEY (its header's +1846 to +1851,
        DSCLOG's), the item moves writable while it runs (_items_writable). No purse's sound: DSCLOG2 has
        no SOUND_REQ (its +1822 written to nothing)."""
        if self.tsr_hdr is None or self.game is None:
            return []
        with self._items_writable((loot.TSR_LOOT_THING,)):
            return super()._loot_pass()

    def _sell_pass(self) -> List[str]:
        """Shattered Lands' (S on a shop's screen: the member's plain gear sold once the shop is shut,
        sell.py), on DSCLOG2's SELL_KEY and SHOP_LOOP (its header's +1852 to +1859, DSCLOG's). Then
        SELL_DONE (+1884, DSCLOG2's own) given the S seen to (sold, or nothing to sell): SHOP_LOOP holds
        the shop's way back to its merchant's talk till then, as the script there reads the money to
        tell a sale from none (Notaku's "Thank you, your business is appreciated.")."""
        if self.tsr_hdr is None or self.game is None:
            return []
        with self._items_writable((DSCLOG2_SELL_DONE,)):
            try:
                return super()._sell_pass()
            finally:
                seen = self._sell_seen
                if seen is not None and seen[0] == self.tsr_hdr:
                    done = struct.pack("<H", seen[1])
                    if self.guest.read(self.tsr_hdr + DSCLOG2_SELL_DONE, 2) != done:
                        self.guest.write(self.tsr_hdr + DSCLOG2_SELL_DONE, done)

    _aging_at: Optional[Tuple[bytes, Optional[int]]] = None  # (the party and the clock the last look found)
    _hastes: Optional[set] = None  # (the Hasted effects' records the last steady look found)

    def _aging_writable(self, creatures) -> None:
        """The bytes aging.py writes made writable: for each of CREATURES (numbers) its hit points,
        status and abilities, and for a party member its sheet's abilities, SHEET_AGE and the packed
        specs and roll (SPEC_SLOTS' three bytes)."""
        sheets = game.table_pointer(self.guest, self.game.ds, game.SHEETS_PTR)
        table = game.table_pointer(self.guest, self.game.ds, game.CREATURES_PTR)
        ranges = []
        for c in creatures:
            at = table + c * game.CREATURE_SIZE
            ranges += [(at, 2), (at + game.CREATURE_STATUS, 1), (at + game.CREATURE_ABILITIES, 6)]
            if c < game.PARTY_SIZE:
                index = struct.unpack_from("<H", self.game.creature(c), game.CREATURE_SHEET_INDEX)[0]
                sheet = sheets + index * game.SHEET_SIZE
                ranges += [(sheet + game.SHEET_ABILITIES, 6), (sheet + game.SHEET_AGE, 1), (sheet + game.SPEC_SLOTS, 3)]
        self.guest.writable = self.guest.writable + [r for r in ranges if r not in self.guest.writable]

    def _party_pass(self) -> List[str]:
        """The sequel's own party made ready (defaultparty.rav_ready: their weapon specs, Terrannus's
        Crusader, their features of their own), the bytes it writes made writable while it runs."""
        from . import defaultparty
        gd = self.game
        if gd is None or not gd.rules & (game.RULE_SPECIALIZE | game.RULE_KITS):
            return []
        before = self.guest.writable
        self.guest.writable = before + defaultparty.rav_ranges(gd)
        try:
            return defaultparty.rav_ready(gd, gd.rules)
        finally:
            self.guest.writable = before

    def _aging_pass(self) -> List[str]:
        """Ages (RULE_AGING, aging.py), on a steady look only (the same party as the last, the clock
        on by no more than NATURAL_JUMP: not a game being loaded): a starting age for each member
        without one (give_ages), a year for each year the clock passes from the last look
        (natural_tick: the years it passes while the Loader watches; the sequel has no place for
        Shattered Lands' count of them, natural_years_due's flags), and Haste's aging (hasted: a
        system shock, a year) for each Hasted effect not there at the last look."""
        gd = self.game
        party, clock = gd.party_signature(), gd.game_time()
        last, self._aging_at = self._aging_at, (party, clock)
        hastes = {(e.owner, e.caster, spell, handle) for e, spell, handle in gd.effect_records()
                  if e.id == game.HASTED_EFFECT}
        before, self._hastes = self._hastes, hastes
        if clock is None or last is None or last[0] != party or last[1] is None \
                or not 0 <= clock - last[1] <= dicelog.NATURAL_JUMP:
            self._hastes = None  # (what a loaded game has already is not news)
            return []
        self._aging_writable(range(game.PARTY_SIZE))
        out = aging.give_ages(gd)
        if clock // aging.YEAR > last[1] // aging.YEAR:
            out += aging.natural_tick(gd, clock // aging.YEAR - last[1] // aging.YEAR)
        if before is None:
            return out
        for owner, caster, _, _ in sorted(hastes - before):
            creature = gd.combatant_creature(owner)
            if creature is not None:
                self._aging_writable([creature])
                out += [f"{self._name(caster)} gives Hasted to {self._name(owner)}"] + aging.hasted(gd, creature)
        return out


def window_layout(sl_raw: dict) -> dict:
    """The Loader window's party layout (layouts/*.json, as a dict) for the sequel, made from Shattered
    Lands': every record offset through ravager.creature_field / sheet_field, the strides the sequel's;
    a field the sequel hasn't (no mapped offset) left out."""
    import copy
    raw = copy.deepcopy(sl_raw)
    field = {"creature": ravager.creature_field, "sheet": ravager.sheet_field}
    size = {"creature": ravager.CREATURE_SIZE, "sheet": ravager.SHEET_SIZE}

    def mapped(record: str, offset) -> Optional[int]:
        return field[record](int(offset, 0) if isinstance(offset, str) else offset) if record in field else None

    raw["game"] = "Dark Sun: Wake of the Ravager"
    for name, spec in raw.get("records", {}).items():
        spec["stride"] = hex(size[name]) if name in size else spec.get("stride")
        spec["slots"] = [None] * len(spec.get("slots", []))
        link = spec.get("link")
        if link:
            pairs = [[mapped(name, a), mapped(link["to"], b), n] for a, b, n in link["match"]]
            link["match"] = [[hex(a), hex(b), n] for a, b, n in pairs if a is not None and b is not None]
    name = raw.get("name", {})
    name["offset"] = hex(mapped(name.get("record", "creature"), name.get("offset", 0)))
    fields = []
    for f in raw.get("fields", []):
        at = mapped(f.get("record", "creature"), f.get("offset", 0))
        if at is None:
            continue
        f["offset"] = hex(at)
        base = f.get("base")
        if base is not None:
            b = mapped(base["record"], base["offset"])
            if b is None:
                f.pop("base")
            else:
                base["offset"] = hex(b)
        fields.append(f)
    raw["fields"] = fields
    return raw


def running(guest) -> Optional[bool]:
    """Which helper the game in GUEST has loaded: True the sequel's (DSCLOG2's signature), False
    Shattered Lands' (DSCLOG's), None neither yet."""
    try:
        low = guest.read(0, game.CONVENTIONAL_AND_UPPER)
    except Exception:
        return None
    if not isinstance(low, (bytes, bytearray)):  # (a stand-in guest: neither)
        return None
    for sig, sequel in ((HDR_SIG, True), (dicelog.HDR_SIG if not _SAVED else b"DSCLOGva", False)):
        at = low.find(sig)
        while at >= 0:
            if at % 16 == 0:
                return sequel
            at = low.find(sig, at + 1)
    return None


def make(guest, **kwargs) -> dicelog.DiceLog:
    """The dice log for the game GUEST runs: the sequel's (RavDiceLog) when its helper is there, else
    Shattered Lands' (with Shattered Lands' layout back, if a sequel's game ran before in this Loader)."""
    if running(guest):
        return RavDiceLog(guest, **kwargs)
    restore_layout()
    return dicelog.DiceLog(guest, **kwargs)
