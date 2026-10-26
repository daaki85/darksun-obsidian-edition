"""Dice log: shows the rolls Shattered Lands makes behind the scenes.

How it works:
  * The launcher runs DSUNLOG.EXE, a copy of the game whose rand() and two
    "probe" places (the end of the saving throw and of the AC calculation)
    start with INT instructions (see gamepatch.py).
  * DSCLOG.EXE (see dos/dsclog.asm), loaded before the game, answers those
    interrupts. Its rand() gives the same numbers as the game's but also
    records each call and the caller's stack frames in a ring buffer; the
    probes record the game's final numbers there.
  * attach() finds DSCLOG and the game in DOSBox's memory; lines() reads new
    entries and turns them into text, using what the calling code does with
    each number and the game's own data (names, THAC0, weapons, spell effects).

Everything game-specific here was taken from the GOG release of Shattered
Lands (DSUN.EXE, 611408 bytes).
"""

import itertools
import random
import re
import struct
import sys
import threading
import time
from collections import Counter, deque
from dataclasses import dataclass
from typing import Callable, Deque, Dict, List, NamedTuple, Optional, Sequence, Tuple

from . import bowyer, buyback, gamepatch, itemgate, combatlog, labels, dance, wheel, wild, defaultparty, defilerscrolls, dust, game, kits, rings, targeting, icons, kalzith, monsters, names, pickpocket, ring, scrolling, scriptchecks, searches, semyon, shadows, specialize, spellarrows, sprites, startgear, stealth, tools, vulture, stuckwalk, heapcheck, weaponchoice, worldgear
from .game import (CONVENTIONAL_AND_UPPER, CREATURE_ABILITIES, CREATURE_SIDE, CREATURE_THAC0, EFFECT_NAMES,
                   EFFECT_RULES, MATERIAL_TO_HIT, MATERIALS, SAVE_NAMES, GameData)
from .guestmem import GuestMemory
from .itemwatch import ItemWatch
from .textlog import KIND_MESSAGE, KIND_PORTRAIT, KIND_TEXT, Dialogue, DialogueEntry, TextBuffer
from .tracker import PartyTracker

HDR_SIG = b"DSCLOGva"
TSR_HDR_OFF = 20  # DSCLOG's header: where it is in DSCLOG's segment
# ... the party's spell slots, for the game's USE screen (PROBE_USE)
TSR_SLOTS_OFF, SLOTS_SIZE = 148, 128
SLOT_LIST = {"Wizard": 1, "Priest": 2}  # the USE screen's list on show (DS:4AE8h + the member): 1 MAGE, 2 CLERIC, 3 PSIONIC
SLOT_KEY = 0x80  # a line's first byte: SLOT_KEY | the list << 4 | the spell level (0: the heading)
# ... and what the Look box says about a monster (PROBE_LOOK)
TSR_LOOK_SEQ, TSR_LOOK_REPLY, TSR_LOOK_WHO, TSR_LOOK_OFF, TSR_LOOK_FULL_OFF, TSR_LOOK_ON = 150, 152, 154, 156, 158, 160
LOOK_SIZE, LOOK_FULL_SIZE = 80, 700
# ... and the party's THAC0 and saves as they stand now, for the game's screens (see STATS)
TSR_STATS_OFF, TSR_STATS_STAMP, TSR_STATS_REQ, TSR_STATS_REPLY, STATS_SIZE = 162, 164, 166, 168, 24
STATS_RANGER = 2  # a STATS entry's +17 for a ranger: only move silently and hide in shadows count
BIOS_TIMER = 0x46C
# ... and the rule changes it makes to the game (the Options tab)
TSR_RULES = 170
TSR_MAIN_TICKS = 260  # the map's main loop run (counted)
TSR_XP_WHO, TSR_XP_AMOUNT = 262, 264  # a party member to be given XP with the pick's text (FFFFh: none)
TSR_SKILLS_ON = 266  # bits: item boxes name a cloak's and boots' bonus to hiding and moving silently;
SKILLS_STEALTH, SKILLS_BELT = 1, 2  # a worn belt adds to picking pockets and opening locks (and its box says)
SKILLS_ELVEN = 4  # the Cloak and Boots of Elvenkind's boxes name their chances (the hiding rule on)
TSR_RING_SEG = 268  # the ring's segment (past the image, so it takes none of DSCLOG's 64 KB)
TSR_CREATING = 361  # 1 while DSCLOG's weapon window asks a character being made for its weapon specs (CR_WEAPONS)
TSR_READ_LANG = 362  # each party member's chance to read languages, kept with STATS (DSCLOG's SHINOBI_READ)
TSR_LEARN_READ = 366  # a Shinobi's try at a scroll: the d100 to read it and the chance (intlearn.py)
TSR_KIT_OUTDOORS = 350  # bit N: party member N under the open sky (the Loader's: _kit_tick)
TSR_RULES_HI = 270  # the rules' bits past 16 (game.RULE_KITS), shifted down
TSR_LEARN = 272  # a preserver's try at a scroll's spell: count, who, spell, INT, chance, d100, result (intlearn.py)
# character creation: each ability's 4d4 rolled (counted), and the last four of each, STR to CHA (DSCLOG's
# RL_TRY: the die tumbles faster than the ring is read)
TSR_TRIES_SEQ, TSR_TRIES = 280, 282
TSR_PICK_OFF, TSR_PICK_ON, PICK_SIZE = 176, 178, 240
USE_ASK, PICK_BUTTON = 1, 2  # (TSR_PICK_ON: items used on the map asked about; a thief's Pick Pockets button)
PICKED_BY = 0xFF00  # (TSR_USE_ITEM: the Pick Pockets button's pick, the thief its low byte)
TSR_USE_SEQ, TSR_USE_REPLY, TSR_USE_WHO, TSR_USE_TAKEN, TSR_USE_ITEM = 180, 182, 184, 186, 188
TSR_SWAP_ON, TSR_SWAP_SEQ, TSR_SWAP_OFF, SWAP_SIZE, SWAP_TEXT_SIZE = 190, 192, 194, 64, 240
RULE_HELMS = game.RULE_HELMS
SLOT_KINDS = {"Wizard": "WIZ", "Priest": "PRI"}
RAND_PATCHED = b"\xcd\x60"  # INT 60h at the start of rand() in DSUNLOG.EXE
RAND_IP = 0x822  # rand()'s offset in the game's first code segment
SEED = 0x4122  # DS offset of rand()'s 32-bit seed

TARGET_GLOBAL = 0x494A  # DS word: combatant id of the current attack's target
CHECK_MODS = (0x3971, 4)  # segment (relative to the load segment), offset: ability check modifiers

ABILITIES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")

# Code right after known rand() calls (the calling code, identified by its bytes)
ATTACK_SITE = bytes.fromhex("660fbfc0666bc01466bb00800000669966f7fb408946fa")
DICE_SITE = bytes.fromhex("660fbfc0660fbf5608660fafc266bb00800000669966f7fb")
CHECK_SITE = bytes.fromhex("660fbfc0666bc01466bb00800000669966f7fb8946fc3d13")
PERCENT_SITE = bytes.fromhex("bb640099f7fb3b56fe")
# The weapon break check after an attack: 0-7, then 0-19; both under the chance (1) breaks it
BREAK_ROLL_1 = bytes.fromhex("660fbfc066c1e00366bb00800000669966f7fb3bc77d")
BREAK_ROLL_2 = bytes.fromhex("660fbfc0666bc01466bb00800000669966f7fb3bc77d")
# Code right after the attack function's call to the dice function
WEAPON_DAMAGE_RETURN = bytes.fromhex("83c4068946fc0bc07f05")
# ... and after the 1d10 for a creature's 1-in-10 special effect on a hit (the thri-kreen
# bite, for one); the caller's arguments are (target, attacker)
SPECIAL_EFFECT_RETURN = bytes.fromhex("83c4043d01007510")
# The code after rand() in the game's random(low, high) (1A0A:2FA9h): low + rand() * (high - low + 1) / 8000h
RANGE_SITE = bytes.fromhex("660fbfc08bd72bd642660fbfd2660fafc2")
# ... and after its calls in a psionic power's check (5D59Dh; its arguments: combatant, power 0-33, bonus): the
# d20 against [BP-2], the power's score (POWER_CHECK_RETURN); with someone else's Synaptic Static
# about, first a d20 against [BP-8] (STATIC_FIRST_RETURN) and one against [BP-6], the Static's own
# score, by the one keeping it up ([BP-4]; STATIC_SECOND_RETURN)
POWER_CHECK_RETURN = bytes.fromhex("83c4048846ff807eff147413")
STATIC_FIRST_RETURN = bytes.fromhex("83c4048846ff666801001400")
STATIC_SECOND_RETURN = bytes.fromhex("83c4048ad08a46ff983b46f8")
# A psionic attack mode's target defends (5D718h, the target, the attack's elements 400h): two
# random(1, its defence) rolls, each over the attacker's power check d20 (pushed after them, the
# call's [BP+0Ah]); both over it resist the attack (the second rolled only after a first over it)
DEFENCE_FIRST_RETURN = bytes.fromhex("83c4045a3bd07d20")
DEFENCE_SECOND_RETURN = bytes.fromhex("83c4045a3bd07d05")
# ... and in the routine that adds up a spell's damage dice
SPELL_DAMAGE_RETURN = bytes.fromhex("83c4045a03d0")
# ... and in the routine that works out a spell's duration (its arguments: spell, caster level);
# the dice are often NdS with S = 1, a fixed number
SPELL_DURATION_RETURN = bytes.fromhex("83c406660fbfc0665a66")
# The routine run whenever an effect uses up a charge (arguments: creature, effect): it rolls
# 2d4 first, and deals it as acid damage only for the acid effect (Acid Arrow: DSCLOG's ACID
# makes its time rounds as charges and spends one at each round's start)
CHARGE_USED_RETURN = bytes.fromhex("83c4048946fe8b4608")
ACID = 1
ROUND_SECONDS = 60  # (DSCLOG's ACID_ROUNDS: an Acid's time in rounds, 1 a started minute, at most 127)
# A confused creature's turn (its routine's first argument is the creature): d10, 1 it runs
# off, 2-6 it does nothing, 7-9 it fights for a side picked with a d2 (as a berserk creature
# always does), 10 it acts normally
CONFUSION_ROLL_RETURN = bytes.fromhex("83c4048ad080fa0174da")
RANDOM_SIDE_RETURN = bytes.fromhex("83c4048bde6bdb03ba")
CONFUSION_RESULTS = ((1, "runs off"), (6, "does nothing"), (9, "fights for a side picked at random"),
                     (10, "acts normally"))
# Strength (and the psionic Adrenalin Control): the special handler rolls 1d6 and stores it in
# the effect; while it lasts the game adds it to STR, keeping STR between 3 and 24
STRENGTH_ROLL_RETURN = bytes.fromhex("83c40450660fbf4618")
STR_MOST = 24
MIND_BAR, LOW_RESISTANCE, MIND_BAR_RESISTANCE = 32, 31, 75
WAIST_SLOT, NECK_SLOT = (game.EQUIP_SLOTS.index(s) for s in ("waist", "neck"))
# The magic resistance roll made straight from the spell code (arguments: target, spell, level)
RESISTANCE_ROLL_RETURN = bytes.fromhex("83c404508a460a50ff76")
# Dispel Magic, for each effect on the target (the effect id in [BP-2], the dispeller's level
# the handler's argument at +14h): d100 at or under 50 + 5 x (that level - the effect's level)
DISPEL_ROLL_RETURN = bytes.fromhex("83c4045a3bd07c108a46")
# Mirror Images taking a spell for one creature (7A5BFh): its d100 (1d100), compared with 75 by
# DSCLOG's NS_IMAGE (50 for Reflected Image's; 0 from the target's own side), the spell's routine's
# arguments (target, caster); and taking an attack's hit (DSCLOG's NS_BLOW): the game's rand() from
# DSCLOG, its code after the call marked IMAGE, in a frame of (target, attacker, chance)
IMAGE_SPELL_RETURN = bytes.fromhex("83c404cd98") + bytes((gamepatch.NS_IMAGE,))
IMAGE_BLOW_SITE = b"\xeb\x05IMAGE"
IMAGE_VANISH = 0xBF  # (the game's own sight of an image vanishing: a "spell" a creature casts on itself)
# Abjure: d20, which must reach 11 - the caster's level + the target's level; a creature of
# kind 14 (a summoned one) is then sent away (1000 damage)
ABJURE_ROLL_RETURN = bytes.fromhex("83c4045a3bd07e03e968")
ABJURE_KIND = 14
# A summoning spell picking which of its three creatures comes
SUMMON_ROLL_RETURN = bytes.fromhex("83c4043d0100740d3d02")
# What a return address shows when the overlay manager has redirected it (INT 3Fh)
OVERLAY_TRAP = b"\xcd\x3f"
# DSCLOG only records calls whose calling code starts like one of these, so
# bursts of other randomness (animations) don't crowd out the rolls that
# matter: the "rand()*N/32768" rolls (attacks, checks, saves, damage dice)
# and the percentile check. The same list is built into DSCLOG.
SCALED_ROLL = b"\x66\x0f\xbf\xc0"  # movsx eax, ax
FILTERS = tuple(SCALED_ROLL + bytes.fromhex(h) for h in (
    "666bc0", "6669c0", "66c1e0", "660fbf56", "8bd72bd6")) + (PERCENT_SITE[:8], b"\xeb\x05IMAGE")  # (DSCLOG's NS_BLOW: IMAGE_BLOW_SITE)
# (the fifth: random(low, high), RANGE_SITE: the psionic power check's d20s, and points of some
# spells' pictures, which the log passes over)

# The rolls at the start of each round (the code after each rand() call): initiative
# 20 + 0-9 + DEX + effects for every combatant, then 0-199 to break ties
INITIATIVE_ROLL = bytes.fromhex("660fbfc0666bc00a66bb00800000669966f7fb665057")
INITIATIVE_TIE = bytes.fromhex("660fbfc06669c0c800000066bb00800000669966f7fb8bde")
INITIATIVE_BASE = 20
INITIATIVE_WAIT = 0.3  # seconds after the last initiative roll before the order is shown

# Character creation (the die on the creation screen). Each ability is the best of four
# 4d4 + 4 + the race's adjustment, raised to the class's minimum; the code after the
# ability routine's call to the dice routine, whose arguments are (?, ability, ...,
# classes counted):
CREATION_ABILITY_RETURN = (bytes.fromhex("83c404cd98069089"),  # (RL_TRY's INT in place of "add ax,[499Ah]")
                           bytes.fromhex("83c40403069a498946fe"))
CREATION_ABILITY_TRIES = 4
# Then each class level's hit point die, through the level-up routine (its caller's
# arguments are (sheet, class, level)); called from the creation screen, it returns here:
LEVEL_HP_RETURN = bytes.fromhex("83c4048bc8c45efc268a")
# (the same with DSCLOG's PROBE_HP_BEST in place of "mov cx,ax", as the patched game has it)
LEVEL_HP_RETURNS = (LEVEL_HP_RETURN, bytes.fromhex("83c404cdbac45efc268a"))
CREATION_HP_CALLER = 0x0232
CREATION_HP_WAIT = 0.3  # seconds after the last hit point roll before the total is shown
CREATION_TUMBLE = 1.0  # seconds after the creation die's last 4d4 that missed rolls go unmentioned
# ... and in the handler for spells with rules of their own (its arguments: caster, target, ...,
# spell at +0Eh): code after its dice calls -> what the roll is and what the game adds
SPELL_HANDLER_RETURNS = (
    (bytes.fromhex("83c40440e988"), 1),  # Cure Serious Wounds: 2d8 + 1
    (bytes.fromhex("83c404050300eb"), 3),  # Cure Critical Wounds: 3d8 + 3
    (bytes.fromhex("83c4045057900e"), 0),  # Cure Light Wounds 1d8, Blood Flow 2d6 (healing)
    (bytes.fromhex("83c4045057cdb1"), 0),  # (the same with DSCLOG's PROBE_CURE, as the patched game has it)
    (bytes.fromhex("83c40450ff7608"), 0),  # Aid 1d8, Vampiric Touch (level / 2)d6, drains
)
# ... and a name picked at random from the game's lists (the code after the dice call)
RANDOM_NAME_RETURNS = (bytes.fromhex("83c40448eb11"), bytes.fromhex("83c4040563008b"),
                       bytes.fromhex("83c40405c700eb"))

KIND_ROLL, KIND_SAVE, KIND_AC = 0, 1, 2
KIND_ITEM = 4  # DSCLOG's item save against acid (PROBE_ITEM_*): raw = d20 | needed << 8
ITEM_ARMOUR = 0x8000  # (in the entry's extra, with the item)
ITEM_DETONATE = 0x4000  # (... Detonate's blast on a worn item: DSCLOG's DET_ITEM)
# Detonate's 1d20 against a worn item (7AAEBh): the line comes with DET_ITEM's record
DETONATE_ROLL_RETURN = bytes.fromhex("83c4048bde6bdb0a8d96e4fc")
KIND_SCRIPT = 5  # DSCLOG's scripts' random command (PROBE_SCRIPT_RAND): raw = result | N << 8
KIND_REQUEST = 6  # DSCLOG's REQ_SITE: a script's REQUEST (command 22h): raw = the request, the frame
# its arguments: [BP+8] who, [BP+0Ah] and [BP+0Ch] its two values (the game's jump table at 7FF30h)
REQUEST_NAMES = {
    0: "the party rests (the game's own rest, each member)", 1: "the party rests (and the fallen get up)", 2: "a door opened or closed", 3: "a skill check",
    4: "the party rests", 5: "an object's state turned", 6: "a cinematic plays", 7: "a trap goes off",
    8: "random monsters come", 9: "a creature transforms", 10: "a map cell blocked", 11: "a map cell unblocked",
    12: "a map cell blocks sight", 13: "a map cell stops blocking sight", 14: "an arena bout begins",
    15: "the pointer set to walk", 16: "the music's level set", 17: "an object placed on the map",
    18: "a creature changes sides", 19: "game over", 20: "creatures counted",
}
KIND_CAST = 8  # DSCLOG's CAST_SITE: a spell or power cast: raw = the spell, the frame (caster [BP+6])
KIND_HEAT = 10  # DSCLOG's HEAT_SITE: Sunstroke's heat on a creature: raw = the damage | the spell << 8,
# the creature the extra (its 1d4 rolled just before, by a caller the overlay manager may hide)
KIND_SWEPT = 11  # DSCLOG's SWEPT_MARK: Whirlwind's damage on a creature that failed its save: raw = it
KIND_WALL = 9  # DSCLOG's THORNS_DAMAGE: Wall of Thorns' damage on a creature in it, taken instead of
# its record's dice: raw = the damage | the spell << 8, extra the creature
THORNS_BASE = 8  # Wall of Thorns: 8 + the creature's AC (DSCLOG's THORNS_AC: it + 80h in the entry's extra's high byte)
KIND_AIM = 7  # DSCLOG's AIM_SITE: a spell cast with a click, refused: raw = the answer | spell << 8,
# extra the caster. The aim check's (84C54h) answers:
AIM_REASONS = {-1: "no creature there", -2: "not a creature that spell can be cast on",
               -3: "the wall would be too long", -4: "no line of sight", -5: "too far away"}
# the requests worth a line of their own (the others only with "Show unlabelled rolls"; skill
# checks and traps have their rolls' lines; a creature changing sides, 18, comes in runs of a
# dozen as a fight's scripts set up)
REQUESTS_SHOWN = frozenset((1, 4, 6, 8, 9, 14, 17, 19))
FIGHT_LINES_AFTER = 5.0  # seconds after a fight its lines still go into the combat log's panel (XP, the last kill)
REGENERATES = 20  # CON from which a creature regains a hit point now and then by itself


def combat_log_level(settings: dict) -> str:
    """The combat log panel's level as saved: in short unless chosen."""
    level = settings.get("combat_log_level")
    return level if level in combatlog.LEVEL_ORDER else combatlog.SHORT


def _remember(values: dict) -> None:
    """Settings the game itself changed (the combat log panel's level and size), saved."""
    from . import launch
    try:
        settings = launch.load_settings()
        settings.update(values)
        launch.save_settings(settings)
    except OSError:
        pass


def _game_font(game_dir: Optional[str]):
    """The game's font (art.Font) from its folder, or None."""
    from . import art, launch
    folder = launch.find_game_dir(game_dir)
    return art.GameArt(folder).font if folder else None


THIEF = 17  # class number

EFFECT_INTERVAL = 0.25  # seconds between looks at the active effects
RING_INTERVAL = 3.0  # seconds between looks for the arena's Ring +1
STATS_ANSWER_STEP = 0.001  # seconds between the stats thread's looks at DSCLOG's requests
STATS_ANSWER_IDLE = 0.5  # ... while the game isn't attached, or a look failed
ITEMS_STILL_WAIT = 0.06  # seconds the game's free lists are watched for, before the Loader changes item lists
LOAD_SETTLE = 3.0  # seconds after the party changes (a game was loaded) when effects are not news
PENDING_SECONDS = 1.0  # how long dice wait to learn which spell they belong to
SPELL_WINDOW = 15.0  # seconds after a spell's roll in which HP changes are put down to the spell
RECENT_DAMAGE = 8  # spell damages kept to tell an HP loss's spell by its amount (two walls at once)
HITS_MATCHED = 8  # weapon hits waiting on one target at most, for matching an HP fall to them
HIT_WAIT = 3.0  # seconds after a weapon hit's damage roll with no HP lost: the target took none
FIGHT_GAP = 120  # game seconds without a new round after which the fight is over
# seconds (of ours) the game's fight flag stays down, once seen up in the fight, before the fight
# counts as over: the game clears it as a fight ends and between the arena's waves (and it is
# still clear as round 1's initiative is rolled, before it was ever up: that doesn't count)
FIGHT_OVER = 2.0


class DiceLogError(Exception):
    pass


@dataclass
class Entry:
    seq: int
    ip: int
    cs: int
    raw: int
    bp: int
    ss: int
    ds: int
    parent_bp: int
    frame: bytes  # from SS:BP+2 (return address, then arguments)
    parent: bytes  # from SS:parentBP+2
    glob: Tuple[int, int, int, int]
    locals: bytes  # from SS:BP-10h
    code: bytes  # the code right after this call, copied when it ran
    parent_code: bytes  # the code at the caller's own return address
    parent_locals: bytes  # from SS:parentBP-28h
    kind: int  # KIND_ROLL, KIND_SAVE or KIND_AC
    extra: int = 0  # KIND_SAVE: the segment of the game's spell table

    SIZE = 192

    @classmethod
    def parse(cls, data: bytes) -> "Entry":
        head = struct.unpack_from("<8H", data, 0)
        return cls(*head, data[16:48], data[48:80], struct.unpack_from("<4H", data, 80), data[88:104],
                   data[104:128], data[128:144], data[144:184], *struct.unpack_from("<2H", data, 184))

    @staticmethod
    def _word(data: bytes, index: int) -> Optional[int]:
        if 0 <= index <= len(data) - 2:
            return struct.unpack_from("<h", data, index)[0]
        return None

    def arg(self, bp_offset: int) -> Optional[int]:
        """Signed word at [BP+bp_offset] in the caller's frame (2..20h), or None."""
        return self._word(self.frame, bp_offset - 2)

    def parent_arg(self, bp_offset: int) -> Optional[int]:
        """Signed word at [parentBP+bp_offset] (2..20h), or None."""
        return self._word(self.parent, bp_offset - 2)

    def local(self, bp_offset: int) -> Optional[int]:
        """Signed word at [BP+bp_offset] for bp_offset in -10h..-2, or None."""
        return self._word(self.locals, bp_offset + 0x10)

    def local_byte(self, bp_offset: int) -> int:
        return self.locals[bp_offset + 0x10]

    def parent_local(self, bp_offset: int) -> Optional[int]:
        """Signed word at [parentBP+bp_offset] for bp_offset in -28h..-2, or None."""
        return self._word(self.parent_locals, bp_offset + 0x28)


def scaled(raw: int, sides: int) -> int:
    """The game's rand()*N/32768: a number from 0 to N-1."""
    return raw * sides // 0x8000


def hit_chance(need: int) -> int:
    """The chance (percent) of a d20 attack roll reaching `need`: a 20 always hits, a 1 always misses."""
    return 5 * sum(1 for d in range(1, 21) if d == 20 or (d != 1 and d >= need))


def save_chance(needed: int, doubled: bool) -> int:
    """The chance (percent) that a d20 (doubled for some spells) reaches `needed` after the rest
    is added; a natural 20 always saves and a natural 1 always fails."""
    wins = sum(1 for d in range(1, 21) if d == 20 or (d != 1 and (d * 2 if doubled else d) >= needed))
    return wins * 5


def signed(n: int) -> str:
    return f"+{n}" if n >= 0 else f"-{abs(n)}"


def generic_roll(code: bytes, entry: Entry) -> Optional[Tuple[str, int]]:
    """(die, value), e.g. ("d20", 14) or ("0-9", 3), for the common 'rand()*N/32768 (+1)' shapes."""
    if not code.startswith(SCALED_ROLL):
        return None
    rest = code[4:]
    if rest[:3] == b"\x66\x6b\xc0":  # imul eax, eax, imm8
        sides, rest = rest[3], rest[4:]
    elif rest[:3] == b"\x66\x69\xc0":  # imul eax, eax, imm32
        sides, rest = struct.unpack_from("<i", rest, 3)[0], rest[7:]
    elif rest[:3] == b"\x66\xc1\xe0":  # shl eax, n
        sides, rest = 1 << rest[3], rest[4:]
    elif rest[:4] == b"\x66\x0f\xbf\x56" and rest[5:9] == b"\x66\x0f\xaf\xc2":  # N = word [bp+x]
        sides, rest = entry.arg(rest[4]), rest[9:]
    else:
        return None
    if sides is None or sides <= 0 or not rest.startswith(b"\x66\xbb\x00\x80\x00\x00\x66\x99\x66\xf7\xfb"):
        return None
    face = scaled(entry.raw, sides)
    if rest[11:12] == b"\x40":  # inc ax: a 1..N die
        return f"d{sides}", face + 1
    return f"0-{sides - 1}", face


@dataclass
class PendingDice:
    """Dice from the general dice routine, waiting to learn which spell they belong to."""
    text: str  # e.g. "9d6 = [4 + 3 + ...] = 29"
    at: float
    damage: bool = False  # rolled by the spell damage routine
    # a 1d100 whose caller's arguments are (target, spell): the magic resistance check
    # (its caller can't be told by its code: the overlay manager replaces that return address)
    resistance: Optional[Tuple[int, int, int]] = None  # target, spell, roll


class AcDetail(NamedTuple):
    base: int  # from the character sheet
    armour: int  # armour and shields (and spells that stand in for armour)
    dex: int
    other: int  # spells, rings and the rest
    total: int


def _new_fight(log) -> None:
    """A new fight for dice log LOG, by the clock (_round_number) or the fight flag (_kits_due): the
    rounds counted from 0 again, and the game hands its creature records to new monsters, so an AC
    worked out for one in an earlier fight isn't this one's (the party's stay theirs)."""
    log._round = 0
    for remembered in (log.last_ac, log.ac_detail):
        for index in [i for i in remembered if i >= game.PARTY_SIZE]:
            del remembered[index]


class DiceLog:
    def __init__(self, guest: GuestMemory, record_everything: bool = False):
        self.guest = guest
        self.record_everything = record_everything  # also rand() calls that aren't rolls (noisy)
        self.script_file = scriptchecks.default_path()  # the scripts the game runs (scriptchecks.py)
        self.tsr_hdr: Optional[int] = None
        self.rand_addr: Optional[int] = None
        self.last_seq: Optional[int] = None
        self.missed = 0
        self.game: Optional[GameData] = None
        self.last_ac: Dict[int, int] = {}  # creature index -> the AC the game last computed for it
        self._ac_whose: Dict[int, str] = {}  # ... and the name of the creature it was then
        self.ac_detail: Dict[int, AcDetail] = {}  # creature index -> how that AC was made up
        self._dice: Dict[Tuple[int, int, int, int], List[int]] = {}
        self._pending: List[PendingDice] = []
        self._out_cold: Dict[int, bool] = {}  # creature index -> Out Cold when last looked at
        self._psp: Dict[int, int] = {}  # party member -> PSP when last looked at
        # party member -> (name, scores) last reported, and a change seen once (reported when it holds)
        self._abilities: Dict[int, Tuple[str, Tuple[int, ...]]] = {}
        self._abilities_new: Dict[int, Tuple[str, Tuple[int, ...]]] = {}
        self.itemwatch = ItemWatch()  # the party's items, and a report when one is gone (itemwatch.py)
        self._settings: Optional[dict] = None  # as last given to use_settings, for the reports
        self._last_damage: Optional[Tuple[int, int]] = None  # (spell, damage) last rolled
        # the last few spell damages rolled, (spell, damage), to tell which spell an HP loss came from
        # when two hurt the same creature before its HP is seen (two walls standing)
        self._recent_damage: Deque[Tuple[int, int]] = deque(maxlen=RECENT_DAMAGE)
        self._turn: Optional[int] = None  # whose turn it was when last looked at
        self.round_order: List[Tuple[Optional[int], str, int]] = []  # this round: (combatant, name, score)
        self.round_number = 0
        self._acted: set = set()  # combatants whose turn has come this round
        self._reply: Optional[Tuple[int, str]] = None  # the reply being flashed when last looked at
        self.speaker_names: Dict[int, str] = {}  # portrait -> the name the player gave it
        self.learned_speakers: Dict[int, str] = {}  # portrait -> the name worked out from conversations
        self._new_speakers: Dict[int, str] = {}  # learned since take_speakers()
        self._talk: Optional[dict] = None  # the conversation on screen: its portraits and who it's with
        self.monster_info = True  # monsters' defences in the game's Look box (set_monster_info)
        self.arena_ring = True  # put the Ring +1 on the Tied-up Prisoner's body in the arena (ring.py)
        self.pickpockets = True  # a thief's Pick Pockets button (pickpocket.py)
        self.show_gear = True  # the party's map sprites dressed in what they wear (sprites.py)
        self.starting_gear = True  # new characters' starting gear filled out (startgear.py)
        self.show_shadows = True  # shadows under the figures on the map (shadows.py)
        self._shadows = shadows.Shadows()
        self.combat_log = False  # the combat log's panel in the game, in a fight (combatlog.py)
        self.floating_names = True  # spells' names over their casters, "Miss" over the missed (labels.py)
        self._panel = combatlog.Panel()
        self._labels = labels.Labels()  # names floating over figures: a spell's, a miss (labels.py)
        self._labels_font_tried = False
        self.combat_log_level = combatlog.SHORT  # ... its lines in short, in detail or the results only
        self._fight_at: Optional[float] = None  # ... when a fight was last seen (its last lines go in too)
        self._fight_monsters: set = set()  # ... the monsters' names in it (their colour)
        self._font_tried = False  # ... the game's font looked for (none: the panel without lines)
        self.game_dir: Optional[str] = None  # the game's folder (its font)
        self._wheel: Optional[wheel.WheelHook] = None  # ... the mouse wheel over it (Windows)
        self.show_dust = True  # dust raised by walkers on sand and dirt (dust.py)
        self.elf_looks = True  # elves' ears and half-elves' own figures, as the copy was written (sprites.py)
        self.cilla_elf = True  # Cilla, an elf, given the elf woman's figure (defaultparty.py)
        self.vulture_on = True  # the cooked vulture quest (vulture.py)
        self.stealth_gear = True  # a worn cloak's and boots' bonuses to hiding (stealth.py)
        self._dust = dust.Dust()
        self.ring_mode = rings.ONLY_CHOSEN  # a ring in a fight: off, or the chosen enemy's (rings.py)
        self._rings = rings.Rings()
        self.use_targeting = True  # Tab chooses an enemy in a fight, Enter attacks it (targeting.py)
        self._targeting = targeting.Targeting()
        self.scroll_map = True  # the map scrolled by dragging with the wheel pressed (scrolling.py)
        self._scrolling = scrolling.Scrolling()
        self._dresser: Optional[sprites.Dresser] = None
        self._dresser_tried = False
        self.picked: set = set()  # the pockets tried already (each person gets one try)
        # ... and when, by the game's clock: one tried after the game being played was saved is
        # forgotten when that save is loaded (the clock goes back past it)
        self.picked_at: Dict[str, Optional[int]] = {}
        self._picked_changed = False
        self._clock: Optional[int] = None
        self._mended_in: Optional[int] = None  # the area Kalzith's scrolls were last mended in
        self._party_done: set = set()  # the game's own party's changes made (defaultparty.py)
        self._swap_seq = 0  # DSCLOG's text swaps seen (the arena ring's search, ring.py)
        self.rules = 0  # RULE_HELMS ...: rule changes DSCLOG makes (set_rules)
        self.stealth_roll: Callable[[], int] = lambda: random.randint(1, 100)  # hiding, moving silently
        self._ring_check = 0.0
        self._main_ticks: Optional[int] = None  # DSCLOG's count of the map's main loop, last read
        self._learn_seq: Optional[int] = None  # DSCLOG's count of tries at a scroll's spell, last read
        self._look_seq = 0
        self._slots_written = b""
        self._stats_written = b""
        self._stats_lock = threading.Lock()  # (the stats thread's and the main loop's writes of STATS)
        self._stats_thread: Optional[threading.Thread] = None
        self._stats_stop = threading.Event()  # (close: the stats thread ends)
        self._own_text: set = set()  # summaries shown in the game's window, not to log as dialogue
        self._skip_choice = False
        self._hits: Dict[int, dict] = {}  # creature -> weapon hits not yet seen in its HP: their
        # damage, in order ("hits"), when the last landed ("at"), its HP then ("hp")
        self._tables: Optional[monsters.MonsterTables] = None  # the monster kinds (read once)
        self._round, self._round_time = 0, None  # this fight's round, and the game time it began
        self._dances = dance.Dances()  # (the Battle Dancers' dances, round by round)
        self._wild = wild.WildFights()  # (the Wild Furies' Wild Fighting, fight by fight)
        self._arrows = spellarrows.SpellArrows()  # (the Spellarchers' spell arrows, made and faded)
        self._rest_due = False  # (a rest seen: the spell arrows fade in the next pass)
        self._kit_check = 0.0  # (when KIT_OUTDOORS was last brought up to date)
        self._out_of_fight: Optional[float] = None  # (since when the game's fight flag is down)
        self._fight_seen = False  # (the flag seen up since the dances and Wild Fighting were rolled)
        self._kits_due = False  # (a fight is over: the next round rolls the dances and Wild Fighting)
        self._stale_turn: Optional[int] = None  # the last round's last turn, until the new one's first
        self._save_rolls: Dict[Tuple[int, int], int] = {}  # (SS, save frame BP) -> natural d20
        self._static_rolls: Dict[Tuple[int, int], int] = {}  # (SS, power check BP) -> the first d20 of a Static contest
        self._defence_rolls: Dict[Tuple[int, int], int] = {}  # (SS, defence BP) -> a psionic defence's first roll
        self._effects: Optional[Counter] = None
        self._party: Optional[bytes] = None
        self._party_changed_at = 0.0
        self._next_effect_check = 0.0
        self._initiative: List[Tuple[int, int]] = []  # this round's (0-9 roll, 0-199 roll) pairs
        self._initiative_roll: Optional[int] = None
        self._initiative_at = 0.0
        self._names: Dict[int, str] = {}  # combatant -> name, for effects that end after a fight
        self._last_attacker = ""
        self._break_first: Optional[int] = None  # the 0-7 roll of a break check in progress
        self._ability_tries: List[int] = []  # character creation: this ability's 4d4 totals so far
        self._ability_of: Optional[int] = None  # ... and which ability they are for
        self._creation_hp: List[Tuple[int, int, int, str, int]] = []  # (sheet, class, hit points, text, level)
        self._creation_hp_at = 0.0
        self._hp_first: Optional[Tuple[tuple, int]] = None  # RULE_HP_BEST: a hit die's first roll
        self._creation_con: Optional[int] = None  # the CON just rolled
        self._creation_abilities: Dict[int, Tuple[int, str]] = {}  # ability: (value, line), this set's
        self._tries_seq: Optional[int] = None  # DSCLOG's count of creation 4d4s at the last look
        self._tries_new = False  # ... and whether it has moved since the lines were last given
        self._tries_at = -CREATION_TUMBLE  # ... and when it last moved
        self._hp: Dict[int, int] = {}  # creature index -> HP at the last look
        self._spell_until = 0.0  # HP changes before this are a spell's doing
        self._acid_burn = False  # an Acid burn's line just given (its damage's duration roll follows)
        self._charges_ahead: Dict[Tuple[int, int], float] = {}  # charges this poll still to tell of
        self._charged: set = set()  # (combatant, effect) with charges, at this poll and the last
        self._charge_spells: Dict[Tuple[int, int], int] = {}  # ... and the spell each came from
        self._charged_before: set = set()
        self._sun_burn = False  # a Sunstroke heat line just given (the same)
        self._spell_name = ""
        self._spell_id: Optional[int] = None
        self._cast: Tuple[Optional[int], Optional[int]] = (None, None)  # (the last spell cast: its caster, the spell)
        self.tracker: Optional[PartyTracker] = None
        self.defilers = defilerscrolls.DefilerScrolls()  # (a defiler in a fight may carry a scroll)
        self.walkers = stuckwalk.StuckWalkers()  # (people a saved walk left standing)
        self.defiler_scrolls = True
        self.buyback = buyback.Buyback()  # (magical items sold, kept to buy back: the rule's DSCLOG part)
        self.text: Optional[TextBuffer] = None
        self.dialogue = Dialogue()
        self._dialogue: List[DialogueEntry] = []

    # ---- attaching ------------------------------------------------------------

    def attach(self) -> str:
        """Find DSCLOG and the game. Returns a status line."""
        low = self.guest.read(0, CONVENTIONAL_AND_UPPER)
        hdr = next((m.start() for m in re.finditer(re.escape(HDR_SIG), low) if m.start() % 16 == 0), None)
        if hdr is None:
            if re.search(rb"DSCLOGv[0-9A-Za-z]", low):
                raise DiceLogError("An older DSCLOG is loaded. Restart the game with 'Start Game with Dice Log.bat'.")
            raise DiceLogError("DSCLOG is not loaded. Start the game with 'Start Game with Dice Log.bat'.")
        ds = game.find_data_segment(self.guest, low)
        if ds is None:
            raise DiceLogError("Shattered Lands is not running yet.")
        rand_addr = (ds - game.DGROUP) * 16 + RAND_IP
        if low[rand_addr:rand_addr + 2] != RAND_PATCHED:
            raise DiceLogError("The game was started without the dice log. "
                               "Restart it with 'Start Game with Dice Log.bat'.")
        with self._stats_lock:  # (the stats thread sees the new DSCLOG and game together)
            self.tsr_hdr, self.rand_addr = hdr, rand_addr
            self.guest.write(hdr + 22, struct.pack("<5H", SEED, TARGET_GLOBAL, 0, 0, 0))
            self.game = GameData(self.guest, ds)
        self._scrolling.forget()  # (a DSCLOG of its own: told again)
        self._dust = dust.Dust()
        self._rings = rings.Rings()
        self._targeting.forget()
        self.tracker = PartyTracker(self.game)
        self.defilers = defilerscrolls.DefilerScrolls()
        self.walkers.forget()
        heapcheck.WATCH = heapcheck.Watch()  # (a new game, a new session's lowest)
        self.text = TextBuffer(self.guest.read, hdr)
        self.set_record_everything(self.record_everything)
        self.set_monster_info(self.monster_info)
        self.set_rules(self.rules)
        self.set_pickpockets(self.pickpockets)
        self._look_seq = struct.unpack("<H", self.guest.read(hdr + TSR_LOOK_SEQ, 2))[0]
        self._swap_seq = struct.unpack("<H", self.guest.read(hdr + TSR_SWAP_SEQ, 2))[0]
        self.last_seq = struct.unpack("<H", self.guest.read(hdr + 8, 2))[0]
        self._effects = None
        return "Dice log attached."

    def set_record_everything(self, record_everything: bool) -> None:
        """Record every rand() call, or (the default) only the ones shaped like rolls."""
        self.record_everything = record_everything
        if self.tsr_hdr is not None:
            filters = () if record_everything else FILTERS
            packed = b"".join(bytes([len(f)]) + f.ljust(8, b"\0") for f in filters)
            self.guest.write(self.tsr_hdr + 32, struct.pack("<H", len(filters)) + packed)

    def set_pickpockets(self, on: bool) -> None:
        """Picking pockets (ON): a thief's Pick Pockets button on the USE screen. Items used on the
        map are asked about either way (the cooked vulture)."""
        self.pickpockets = on
        if self.tsr_hdr is not None:
            flags = USE_ASK | (PICK_BUTTON if on else 0)
            self.guest.write(self.tsr_hdr + TSR_PICK_ON, struct.pack("<H", flags))

    def load_picked(self, entries) -> None:
        """The pockets tried, as remembered (settings.json): "key@game time" (or a bare key, from
        an earlier version: forgotten the first time a game is loaded)."""
        self.picked, self.picked_at = set(), {}
        for entry in entries:
            key, at, when = entry.rpartition("@")
            if not (at and when.isdigit()):
                key, when = entry, ""
            self.picked.add(key)
            self.picked_at[key] = int(when) if when else None

    def take_picked(self) -> Optional[List[str]]:
        """All the pockets tried, for the caller to remember in place of what it had (settings.json),
        when they have changed since the last call; else None."""
        if not self._picked_changed:
            return None
        self._picked_changed = False
        return sorted(key if self.picked_at.get(key) is None else f"{key}@{self.picked_at[key]}"
                      for key in self.picked)

    def _remember_pick(self, key: str) -> None:
        self.picked.add(key)
        try:
            self.picked_at[key] = self.game.game_time()
        except (struct.error, IndexError, ValueError):
            self.picked_at[key] = None
        self._picked_changed = True

    def _forget_undone_picks(self) -> None:
        """Pockets tried later than the game's clock are forgotten (the person can be tried
        again): those since a save, when the save is loaded; another game's, in a new game."""
        try:
            now = self.game.game_time()
        except (struct.error, IndexError, ValueError):
            return
        if not now or now <= 0:  # (no game, or the menus)
            return
        went_back = self._clock is not None and now < self._clock
        if went_back:
            self.defilers.reset()  # (a save loaded: its fights rolled for again)
            self._mended_in = None  # (a save loaded: its scrolls looked at again)
        # A try later than the game's clock is not this game's: one undone by loading an earlier
        # save, or another game's (a new game started with the same party, the Loader started
        # after it: seen the first time the clock is read)
        undone = [k for k in self.picked
                  if (self.picked_at.get(k) is None and went_back)
                  or (self.picked_at.get(k) is not None and self.picked_at[k] > now)]
        for key in undone:
            self.picked.discard(key)
            self.picked_at.pop(key, None)
        self._picked_changed = self._picked_changed or bool(undone)
        self._clock = now

    def _write_pick_text(self, text: str) -> None:
        self._write_pick_bytes(text.encode("cp437", "replace")[:PICK_SIZE - 1] + b"\0")

    def _write_pick_bytes(self, data: bytes) -> None:
        offset = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_PICK_OFF, 2))[0]
        base = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_HDR_OFF, 2))[0]
        self.guest.write(base + offset, data)

    def _write_xp(self, result: Optional["pickpocket.Attempt"]) -> None:
        """The XP that came with what was lifted (Kurzak's Short Sword), for DSCLOG to give with
        the game's own routine as it shows the text; none otherwise."""
        who, xp = (result.xp_to, result.xp) if result is not None and result.xp_to is not None else (0xFFFF, 0)
        self.guest.write(self.tsr_hdr + TSR_XP_AMOUNT, struct.pack("<H", xp))
        self.guest.write(self.tsr_hdr + TSR_XP_WHO, struct.pack("<H", who))

    def _answer_use(self) -> List[str]:
        """An item was used on something on the map, or a thief's Pick Pockets button chose someone
        (PICKED_BY): try their pockets with that thief's hand; and have DSCLOG show what came of
        it instead of the game's doing."""
        if self.tsr_hdr is None:
            return []
        seq = self.guest.read(self.tsr_hdr + TSR_USE_SEQ, 2)
        if seq == self.guest.read(self.tsr_hdr + TSR_USE_REPLY, 2):
            return []
        result, taken = None, False
        try:
            item, thing = struct.unpack("<HH", self.guest.read(self.tsr_hdr + TSR_USE_ITEM, 2) +
                                        self.guest.read(self.tsr_hdr + TSR_USE_WHO, 2))
            it = ring.Items(self.game)
            kind, index = it.thing(thing) if 0 <= thing < ring.THING_COUNT else (None, None)
            if spellarrows.ARROWS_BY <= item < PICKED_BY:
                taken = True
                if self._fighting():
                    result = pickpocket.Attempt(spellarrows.NOT_IN_A_FIGHT, [])
                else:
                    result = self._arrows.make(self.game, item & 0xFF, thing)
            elif PICKED_BY <= item < 0xFFFF and self.pickpockets:
                taken = True
                if self._fighting():
                    result = pickpocket.Attempt(pickpocket.NOT_IN_A_FIGHT, [])
                elif kind == 2:
                    result = pickpocket.attempt(self.game, self.picked, who=index, thief=item & 0xFF)
                if result is None:
                    result = pickpocket.Attempt("There are no pockets to pick there.", [])
        except itemgate.ItemsBusy:
            return []  # (the game changing its item lists: answered in a later pass)
        except (struct.error, IndexError, ValueError):
            result, taken = None, False
        self._write_pick_text(result.text if result else "")
        self._write_xp(result)
        self.guest.write(self.tsr_hdr + TSR_USE_TAKEN, struct.pack("<H", int(taken)))
        self.guest.write(self.tsr_hdr + TSR_USE_REPLY, seq)
        if not result:
            return []
        if result.key:
            self._remember_pick(result.key)
        return result.log or [result.text]

    def _arrows_pass(self) -> List[str]:
        """The Spellarchers' spell arrows: after a rest, every one fades (spellarrows.py)."""
        if self.tsr_hdr is None:
            return []
        out: List[str] = []
        try:
            if self._rest_due:
                out = self._arrows.rest(self.game)
                self._rest_due = False
        except itemgate.ItemsBusy:
            pass  # (tried again in the next pass)
        except (struct.error, IndexError, ValueError):
            pass
        return out

    def set_monster_info(self, on: bool) -> None:
        """Have the game's Look box (in a fight) say what hurts a monster, and then show all of it."""
        self.monster_info = on
        if self.tsr_hdr is not None:
            self.guest.write(self.tsr_hdr + TSR_LOOK_ON, struct.pack("<H", int(on)))

    def use_settings(self, settings: dict) -> None:
        """The Options tab's switches for the game, as saved (for the logs without a window)."""
        self._settings = settings
        self.monster_info = bool(settings.get("monster_info", True))
        self.arena_ring = settings.get("new_items", True) is not False  # (with the new items)
        self.pickpockets = bool(settings.get("pickpockets", True))
        self.show_gear = bool(settings.get("show_gear", True))
        self.starting_gear = bool(settings.get("starting_gear", True))
        self.show_shadows = bool(settings.get("shadows", True))
        self.combat_log = bool(settings.get("combat_log", True))
        self.floating_names = bool(settings.get("floating_names", True))
        self.combat_log_level = combat_log_level(settings)
        if settings.get("combat_log_size") in combatlog.SIZES:
            self._panel.resize(settings["combat_log_size"])
        self._panel.open = settings.get("combat_log_open") is True  # (hidden till L)
        self.game_dir = settings.get("game_dir") or self.game_dir
        self.scroll_map = bool(settings.get("scroll_map", True))
        self.show_dust = bool(settings.get("dust", True))
        self.elf_looks = settings.get("elf_looks", True) is not False
        self.cilla_elf = settings.get("cilla_elf", True) is not False
        self.vulture_on = bool(settings.get("vulture", True))
        self.defiler_scrolls = settings.get("defiler_scrolls", True) is not False
        self.stealth_gear = bool(settings.get("stealth_gear", True))
        self.ring_mode = rings.mode(settings)
        self.use_targeting = bool(settings.get("targeting", True))
        self.load_picked(settings.get("pickpocketed", []))
        self.rules = game.rules_from_settings(settings)

    def set_rules(self, rules: int) -> None:
        """Turn the rule changes on or off (game.RULE_*). DSCLOG makes most of them; the spell
        save is the game's own table, written here."""
        self.rules = rules
        game.RULES_IN_FORCE = rules
        game.BELT_IN_FORCE = self.stealth_gear
        if self.game is not None:
            self.game.rules = rules
            self.game.belt = self.stealth_gear
        if self.tsr_hdr is not None:
            self.guest.write(self.tsr_hdr + TSR_RULES, struct.pack("<H", rules & 0xFFFF))
            self.guest.write(self.tsr_hdr + TSR_RULES_HI, struct.pack("<H", rules >> 16 & 0xFFFF))
            skills = (SKILLS_STEALTH if rules & game.RULE_STEALTH and self.stealth_gear else 0) \
                | (SKILLS_BELT if self.stealth_gear else 0) \
                | (SKILLS_ELVEN if rules & game.RULE_STEALTH else 0)  # (the hiding rule's cloak and boots; the belt's own)
            self.guest.write(self.tsr_hdr + TSR_SKILLS_ON, struct.pack("<H", skills))
            table = self.game.ds * 16 + game.SAVE_KINDS if self.game is not None else None
            # (only over the game's own table: kind 5 is petrification/polymorph or, so far, the spell save)
            if table is not None and struct.unpack("<5H", self.guest.read(table, 10)) == game.KIND_TO_SAVE[:5] \
                    and struct.unpack("<H", self.guest.read(table + 2 * game.SPELL_KIND, 2))[0] in (3, 5):
                save = game.kind_to_save(game.SPELL_KIND, rules)
                self.guest.write(table + 2 * game.SPELL_KIND, struct.pack("<H", save))
            if self.game is not None:
                self.game.set_dodge(bool(rules & game.RULE_NO_DOUBLE))

    def monster_ac(self, index: int) -> Optional[int]:
        """The AC the game last computed for creature INDEX, if it was this creature's: a fight
        soon after another (no gap in the game's time to tell them apart) hands the earlier
        one's creature records to new monsters."""
        if index not in self.last_ac or self._ac_whose.get(index) != self.game.creature_name(index):
            return None
        return self.last_ac[index]

    def _answer_look(self) -> List[str]:
        """DSCLOG asks about a creature the player looks at in a fight: give the Look box its
        short lines and the whole description, and log it."""
        if self.tsr_hdr is None:
            return []
        seq = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_LOOK_SEQ, 2))[0]
        if seq == self._look_seq:
            return []
        self._look_seq = seq
        who = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_LOOK_WHO, 2))[0]
        short: List[str] = []
        full: List[str] = []
        index = self.game.combatant_creature(who)
        if index is not None and index >= game.PARTY_SIZE:
            try:
                tables = monsters.MonsterTables(self.guest.read, self.game.load_seg)
                short, full = monsters.monster_lines(self.game, tables, index, self.monster_ac(index))
            except (struct.error, IndexError, ValueError):
                short, full = [], []
        base = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_HDR_OFF, 2))[0]
        text = "|".join(short).encode("cp437", "replace")[:LOOK_SIZE - 1]
        # the window only when there's more to say than the box's HP, AC and THAC0
        whole = " ".join(full).replace("%", " pct").encode("cp437", "replace")[:LOOK_FULL_SIZE - 1] \
            if len(full) > 1 else b""
        if whole:
            self._own_text.add(whole.decode("cp437"))  # not dialogue
        self.guest.write(base + struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_LOOK_OFF, 2))[0], text + b"\0")
        self.guest.write(base + struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_LOOK_FULL_OFF, 2))[0],
                         whole + b"\0")
        self.guest.write(self.tsr_hdr + TSR_LOOK_REPLY, struct.pack("<H", seq))
        return [f"Look: {full[0]}"] + [f"    {line}" for line in full[1:]] if full else []

    def slots_lines(self, member: int) -> str:
        """A party member's spell slots for the game's USE screen, "|" between lines, each line
        keyed by its first character (SLOT_KEY | the list << 4 | the spell level, level 0 the
        heading): for each kind of spells, a heading then a line for each spell level,
        "SPELLS LEFT", "PRI 5/5". DSCLOG shows the heading and the line of the list and level
        the screen is on. A multiclass preserver in armour has "NO SPELLS IN ARMOUR" for its
        wizard spells."""
        lines = []
        for kind, levels in self.game.spell_slots(member):
            key = SLOT_KEY | SLOT_LIST.get(kind, 0) << 4
            name = SLOT_KINDS.get(kind, kind[:3].upper())
            armour = kind == "Wizard" and self.game.no_spells(member)
            lines.append(chr(key) + ("NO SPELLS IN ARMOUR" if armour else "SPELLS LEFT"))
            lines += [chr(key | level) + f"{name} {left}/{most}" for level, left, most in levels]
        return "|".join(lines)

    def _write_slots(self) -> None:
        """Keep DSCLOG's copy of the party's spell slots current."""
        if self.tsr_hdr is None:
            return
        base = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_HDR_OFF, 2))[0]
        table = base + struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_SLOTS_OFF, 2))[0]
        data = b""
        for member in range(game.PARTY_SIZE):
            try:
                text = self.slots_lines(member)
            except (struct.error, IndexError, ValueError):
                text = ""
            data += text.encode("latin-1", "replace")[:SLOTS_SIZE - 1].ljust(SLOTS_SIZE, b"\0")
        if data != self._slots_written:
            self.guest.write(table, data)
            self._slots_written = data

    def stats_entry(self, member: int) -> bytes:
        """A party member's STATS entry for DSCLOG: THAC0 with the main weapon, the five saves as
        the d20 needed now, THAC0 with each weapon ready, and a thief's skills as they stand."""
        g = self.game
        rec = g.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME]:
            return bytes(STATS_SIZE)
        saves, hits = g.saves_now(member), g.weapon_hits(member)
        if len(saves) != 5 or not hits:
            return bytes(STATS_SIZE)
        clamp = lambda n: max(-99, min(99, n))
        weapons = [h for h in hits if h.item >= 0][:3]
        out = struct.pack("<Bb5Bx", 1, clamp(hits[0].thac0), *(s.needs for s in saves))
        out += struct.pack("<3H", *([h.item for h in weapons] + [game.NO_ITEM] * (3 - len(weapons))))
        out += struct.pack("<3b", *([clamp(h.thac0) for h in weapons] + [0] * (3 - len(weapons))))
        thief = g.thief_skills_now(member, game.PANEL_SKILLS)
        ranger = g.ranger_skills_now(member) if self.rules & game.RULE_STEALTH and not thief else []
        if len(thief) == 6:
            out += struct.pack("<B6B", 1, *(n for _, n in thief))
        elif len(ranger) == 2:  # move silently and hide in shadows, in a thief's places
            out += struct.pack("<B6B", STATS_RANGER, 0, 0, 0, *(min(n, 255) for _, n in ranger), 0)
        else:
            out += bytes(7)
        return out.ljust(STATS_SIZE, b"\0")

    def read_languages(self, member: int) -> int:
        """A party member's chance to read languages as it stands (0 without thief levels): a
        Shinobi reads a scroll with it (DSCLOG's SHINOBI_READ)."""
        try:
            skills = self.game.thief_skills_now(member, (game.READ_LANGUAGES,))
        except (struct.error, IndexError, ValueError):
            return 0
        return max(0, min(100, skills[0][1])) if skills else 0

    def _answer_stats(self) -> None:
        """A game screen is about to show THAC0 and the saves: bring them up to date first (the
        game waits for this, so an item just put on counts)."""
        with self._stats_lock:
            if self.tsr_hdr is None or self.rand_addr is None:
                return
            req = self.guest.read(self.tsr_hdr + TSR_STATS_REQ, 2)
            if req != self.guest.read(self.tsr_hdr + TSR_STATS_REPLY, 2):
                self._write_stats_now()
                self.guest.write(self.tsr_hdr + TSR_STATS_REPLY, req)

    def answer_stats_in_background(self) -> None:
        """Answer DSCLOG's requests for fresh STATS from a thread of their own, within a
        millisecond or two: the game stands still while it waits (STATS_SYNC: each time an item is
        picked up or put down on the inventory screen), and a wait for the main loop's next pass
        (20-40 ms, more with the Ledger's window) held the pointer still, then made it jump."""
        if self._stats_thread is not None:
            return
        if sys.platform == "win32":  # (Windows' timer ticks every 15.6 ms unless asked: the thread's
            try:                     #   millisecond waits would last that long)
                import ctypes
                ctypes.windll.winmm.timeBeginPeriod(1)
            except (AttributeError, OSError):
                pass
        def run() -> None:
            step = STATS_ANSWER_STEP
            while not self._stats_stop.wait(step):
                try:
                    self._answer_stats()
                    step = STATS_ANSWER_STEP
                except Exception:  # (DOSBox gone or restarting: the main loop attaches again)
                    step = STATS_ANSWER_IDLE
        self._stats_thread = threading.Thread(target=run, name="stats", daemon=True)
        self._stats_thread.start()

    def _write_stats(self) -> None:
        """Keep DSCLOG's copy of the party's THAC0 and saves current, and say it is."""
        with self._stats_lock:
            self._write_stats_now()

    def _write_stats_now(self) -> None:
        if self.tsr_hdr is None:
            return
        offset = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_STATS_OFF, 2))[0]
        if not offset:
            return
        table = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_HDR_OFF, 2))[0] + offset
        data = b""
        for member in range(game.PARTY_SIZE):
            try:
                data += self.stats_entry(member)
            except (struct.error, IndexError, ValueError):
                data += bytes(STATS_SIZE)
        if data != self._stats_written:
            self.guest.write(table, data)
            self._stats_written = data
        self.guest.write(self.tsr_hdr + TSR_READ_LANG, bytes(self.read_languages(member) for member in range(game.PARTY_SIZE)))
        self.guest.write(self.tsr_hdr + TSR_STATS_STAMP, self.guest.read(BIOS_TIMER, 2))

    def _not_ours(self, entries: List[DialogueEntry]) -> List[DialogueEntry]:
        """Dialogue without the turn summaries the log itself had the game show (and their
        "Continue")."""
        out = []
        for entry in entries:
            said = " ".join(entry.text.split())  # DSCLOG keeps the first 400 characters of a text
            own = next((t for t in self._own_text if said and " ".join(t.split()).startswith(said)), None)
            if own is not None:
                self._own_text.discard(own)
                self._skip_choice = True
            elif entry.chosen and self._skip_choice:
                self._skip_choice = False
            else:
                out.append(entry)
        return out

    @property
    def attached(self) -> bool:
        return self.rand_addr is not None

    @property
    def load_seg(self) -> int:
        return (self.rand_addr - RAND_IP) // 16

    def still_patched(self) -> bool:
        """False when the game has quit or been replaced by an unpatched one."""
        sig = self.guest.read(self.game.ds * 16 + game.BORLAND_SIG_OFFSET, len(game.BORLAND_SIG))
        return sig == game.BORLAND_SIG and self.guest.read(self.rand_addr, 2) == RAND_PATCHED

    def detach(self) -> None:
        self.rand_addr = None

    def close(self) -> None:
        """Done with: the stats thread stops (answer_stats_in_background)."""
        self._stats_stop.set()

    # ---- reading ----------------------------------------------------------------

    def poll(self) -> List[Entry]:
        """Entries written since the last poll, oldest first."""
        head = self.guest.read(self.tsr_hdr, 24)
        seq, _, nent, esize, ring_off = struct.unpack_from("<5H", head, 8)
        new = (seq - self.last_seq) & 0xFFFF
        if not new:
            return []
        ring_seg = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_RING_SEG, 2))[0]
        ring_base = ring_seg * 16 + ring_off  # (the ring: a segment of its own, past the image)
        ring = self.guest.read(ring_base, nent * esize)
        entries = {}
        for i in range(nent):
            e = Entry.parse(ring[i * esize:(i + 1) * esize])
            if 0 < (e.seq - self.last_seq) & 0xFFFF <= new:
                entries[e.seq] = e
        self.missed += new - len(entries)
        self.last_seq = seq
        return [entries[s] for s in sorted(entries, key=lambda s: (s - seq - 1) & 0xFFFF)]

    def _kit_tick(self, now: float) -> None:
        """Once a second: DSCLOG's KIT_OUTDOORS, the party members under the open sky (a Military
        Scout's skills, a Spirit Caller's casting), and the dances ended with the fight."""
        if self.game is None or self.tsr_hdr is None or now < self._kit_check:
            return
        self._kit_check = now + 1.0
        try:
            if not self.game.rules & game.RULE_KITS:
                return
            bits = sum(1 << m for m in range(game.PARTY_SIZE) if self.game.outdoors(m))
            self.guest.write(self.tsr_hdr + TSR_KIT_OUTDOORS, bytes((bits,)))
            if self.game.in_combat():
                self._out_of_fight, self._fight_seen = None, True
            else:
                # the dances and Wild Fighting end with the fight, whatever came of them, and the
                # next fight's first round rolls them again: once the game's fight flag, seen up
                # in the fight, has been down FIGHT_OVER, or the game's clock has run FIGHT_GAP
                # past the last round, or gone back (a game loaded)
                if self._out_of_fight is None:
                    self._out_of_fight = now
                over = self._fight_seen and now - self._out_of_fight >= FIGHT_OVER
                now_game = self.game.game_time()
                if now_game is not None and self._round_time is not None \
                        and (now_game - self._round_time > FIGHT_GAP or now_game < self._round_time):
                    over = True
                if over and not self._kits_due:
                    self._dances.stop(self.game, self.tsr_hdr)
                    self._wild.stop(self.game, self.tsr_hdr)
                    self._kits_due, self._fight_seen = True, False
        except (struct.error, IndexError, ValueError):
            pass

    def _kit_attack(self, attacker: Optional[int], item_type: Optional[int], mode: Optional[int],
                    target: Optional[int] = None) -> Tuple[str, int, int]:
        """(the kits' names, to hit, damage) the attacker's kits add to a weapon attack, as DSCLOG's
        KIT_TO_HIT, KIT_ATTACK_DAMAGE and KIT_EXTRA: a Ravager's, a Brute's, a Ghetto Fighter's (in
        melee), an Arena Champion's; a Battle Dancer's dance, a Wilderness Avenger's; and Wild Fighting, a Wild Fury's or Gerakis's (WILD_*)."""
        g = self.game
        names, to_hit, damage = [], 0, 0
        melee = mode is not None and mode <= 1
        kind = specialize.kind_of(item_type) if item_type is not None else None
        for kid in (g.kit_ids(attacker) if attacker is not None else []):
            weapon = kits.melee(kid, g.two_handed_type(item_type), kind) if melee and not g.missile_type(item_type) else 0
            hit, dam = kits.champion(kid, g.holds_shield(attacker), melee)
            more = kits.extra(kid, g.dance.get(attacker, 0))
            if mode is not None and mode > 1 and attacker is not None and attacker < game.PARTY_SIZE:  # (DSCLOG's KIT_TO_HIT)
                hit += kits.missile_to_hit(kid, kind, g.outdoors(attacker))
            if mode is not None:  # (DSCLOG's KIT_TO_HIT: anything but a dagger, unarmed too)
                hit += kits.ghetto_to_hit(kid, kind)
            if weapon or hit or dam or more:
                names.append(kits.name(kid) + (" under the open sky" if kid == kits.SCOUT else ""))
                to_hit, damage = to_hit + weapon + hit + more, damage + weapon + dam + more
        if attacker in g.wild and mode is not None:  # (DSCLOG's WILD_*: a Wild Fury's, or Gerakis's own)
            names.append("Wild Fighting")
            if g.wild[attacker]:
                damage += kits.WILD_DAMAGE
            else:
                to_hit += kits.WILD_TO_HIT
        return " and ".join(names), to_hit, damage

    def lines(self, show_all: bool = False, now: Optional[float] = None) -> List[str]:
        """Everything new since the last call, as log lines. Call it every few tens of ms. Its
        changes to the game's item lists are made only if the game left them be all the while
        (itemgate.py: the pass begins before anything is read, and ends with DOSBox running on)."""
        gate = getattr(self.guest, "item_gate", None)
        if gate is not None:
            gate.begin()
        try:
            return self._lines(show_all, now)
        finally:
            if gate is not None:
                gate.end()

    def _lines(self, show_all: bool, now: Optional[float]) -> List[str]:
        now = time.monotonic() if now is None else now
        out: List[str] = []
        entries = self.poll()
        self.count_charges(entries)
        for e in entries:
            out += self.describe(e, show_all, now)
        self._forget_undone_picks()
        self._kit_tick(now)
        self._answer_stats()
        out += self._answer_use()
        out += self._arrows_pass()
        out += self._answer_look()
        changes = self.hp_changes(now) + self.psp_changes() + self.ability_changes()
        if not self._party_check(now):  # not while a game is loading: its records are half-filled
            out += changes
        for rec in self.text.poll():
            if rec.kind == KIND_MESSAGE:
                if rec.text.strip():
                    out.append(f"Message: {' '.join(rec.text.split())}")
            else:
                self._follow_talk(rec)
                self._dialogue += self._not_ours(self.dialogue.add(rec, now))
        self._dialogue += self._not_ours(self.dialogue.idle(now))
        self._dialogue += self._not_ours(self._reply_choice(now))
        if now >= self._next_effect_check:
            self._next_effect_check = now + EFFECT_INTERVAL
            out += self.effect_changes(now)
            self._write_slots()
            self._write_stats()
            if not self._party_check(now):
                out += self.tracker.check(now)
                try:  # (each waits for a later pass while the game changes its item lists)
                    if self.rules & game.RULE_BUYBACK:  # (a magical item sold: into its merchant's pack)
                        out += self.buyback.watch(self.game, self.tsr_hdr)
                    if self.defiler_scrolls:  # (a defiler in a fight may carry a scroll: defilerscrolls.py)
                        out += self.defilers.watch(self.game, bool(self.rules & game.RULE_NEW_SPELLS))
                except itemgate.ItemsBusy:
                    pass
                itemgate.release(self.game)
                out += self._arena_ring(now)
                out += self._drawn(now)
                self._kalzith_sold_out()
                out += self._learn_lines()
                self._dress_now(now)
                out += self.itemwatch.check(self.game, now, self._settings)
        self._scroll()
        if self._initiative and now - self._initiative_at >= INITIATIVE_WAIT:
            out += self.initiative_lines()
        out += self.turn_lines()  # after the round's order and the last turn's XP
        self._creation_tries_moved(now)
        if (self._creation_hp or self._creation_abilities or self._tries_new) \
                and now - self._creation_hp_at >= CREATION_HP_WAIT:
            out += self.creation_lines()
        out += self.flush(now)
        refused = getattr(self.guest, "refused", None)
        if refused:
            out += [f"(The Loader stopped one of its own writes over the game's memory: {r}. "
                    "Please send this line.)" for r in refused[:3]]
            refused.clear()
        if self.missed:
            # (not while the creation die tumbles: DSCLOG keeps the rolls that count, RL_TRY)
            if now - self._tries_at > CREATION_TUMBLE:
                out.append(f"({self.missed} rolls came too fast to record)")
            self.missed = 0
        if self.combat_log and out:
            self._panel_lines(out, now)
        if self.combat_log:
            self._panel_input(now)
        self.itemwatch.remember(out)  # (the context an item report carries)
        return out

    def _weapons_asked(self) -> bool:
        """Whether DSCLOG's weapon window is up after the creation screen's DONE (TSR_CREATING): the
        new character's weapon specs are still being picked, its defaults and weapon wait."""
        if self.tsr_hdr is None:
            return False
        try:
            return bool(self.guest.read(self.tsr_hdr + TSR_CREATING, 1)[0])
        except (OSError, IndexError):
            return False

    def _arena_ring(self, now: float) -> List[str]:
        """The helms' and boots' names for the rules; once the game's name table has DSCLOG's
        names, the ring and tools from earlier versions named in them; then new characters' gear,
        the game's own party, and the watches of the Loader's people and items."""
        if now < self._ring_check:
            return []
        self._ring_check = now + RING_INTERVAL
        out: List[str] = []
        try:
            ring.name_items(self.game, self.rules)
            if not names.update(self.game, self.tsr_hdr):
                return out  # no names for them yet: none given
            still = self._items_still()
            if still:  # (the item lists changed only while the game leaves them be: itemgate.py)
                # A new character's gear waits while DSCLOG's weapon window is up after DONE: its weapon
                # specs decide its weapon, and the steps after build on that weapon, in this order.
                new_ok = not self._weapons_asked()
                if self.rules & game.RULE_SPECIALIZE and new_ok:  # (new characters' weapon kinds and starting weapon:
                    out += weaponchoice.finish_new(self.game)  #   the long sword made a club before a psionicist's classes leave it behind)
                if self.rules & game.RULE_RESTRICT and new_ok:  # (new characters' gear their classes can't use: left behind)
                    out += weaponchoice.class_gear(self.game)
                if self.rules & game.RULE_KITS:  # (new characters' starting gear fitted to their kits; a
                    if new_ok:  #   Healer's cosmos spells, one made by an earlier version)
                        out += weaponchoice.kit_gear(self.game)
                    for member in range(game.PARTY_SIZE):  # (and a Wilderness Avenger's healing spells)
                        out += kits.cosmos_spells(self.game, member) + kits.avenger_heals(self.game, member)
                if self.starting_gear and new_ok:  # (new characters' starting gear filled out)
                    out += startgear.fill(self.game)
                out += defaultparty.ready(self.game, self.rules, self._party_done, self.starting_gear)  # (the game's own party, once)
                if not self.game.in_combat():  # (items an earlier version put in the wrong list)
                    out += pickpocket.mend_lists(self.game)
                itemgate.release(self.game)
            if self.cilla_elf:
                out += defaultparty.elf_figure(self.game)  # (Cilla, an elf, drawn as one)
            # (the slave pens' and the world's new items are in the game's data: worldgear.py)
            if self.stealth_gear:
                stealth.reprice(self.game)  # (cloaks and boots: they help a thief hide and move silently)
            kalzith.stock(self.game, bool(self.rules & game.RULE_NEW_SPELLS))  # (once a game, by its flag)
            semyon.watch(self.game)  # (killed: never put in the pens)
            if self.vulture_on:
                out += vulture.meal(self.game)  # (Dinos's script has set its flag: XP and a full rest)
            if kalzith.watch(self.game):  # (killed: Dinos and the Trustee speak of him so)
                left = kalzith.loot(self.game)  # (one of his scrolls, his Cloak and Quarterstaff)
                if left:
                    out.append("Kalzith leaves: " + ", ".join(left))
            region = self.game.region()
            if region != self._mended_in:  # (his scrolls of before the fix, once in each area)
                kalzith.mend(self.game)
                self._mended_in = region
            tools.repaint(self.game)  # (sets of Thieves' Tools an earlier version gave: their name and picture)
            out += [stuckwalk.stopped_line(name) for name in self.walkers.check(self.game)]
            out += heapcheck.WATCH.take(self.guest.read, self.game.load_seg, self.game.ds, self.tsr_hdr)  # (the game's memory: a crash report's, and a word when it runs low)
            out += self._ring_search()
            icons.repaint(self.game, icons.ready(self.game, self.tsr_hdr))  # the items' own icons
        except (struct.error, IndexError, ValueError):  # (itemgate.ItemsBusy too: tried in a later pass)
            return out
        finally:
            itemgate.release(self.game)
        return out

    def _drawn(self, now: float) -> List[str]:
        """What DSCLOG draws and does for the Loader, kept up four times a second (not with the
        ring's search, every 3 s: a Tab's ring and the Enter's target were that late): shadows,
        the enemy chosen with Tab and the rings, dust."""
        if self.tsr_hdr is None:
            return []
        try:
            self._shadows.update(self.game, self.tsr_hdr, self.show_shadows, now,
                                 needed=self.show_dust or self.ring_mode != rings.OFF or self.combat_log)
            self._update_panel(now)
            self._labels.on = self.floating_names
            self._labels.tick(self.game.guest, self.tsr_hdr, now)
            foes = rings.enemies(self.game)
            out = self._targeting.update(self.game, self.tsr_hdr, self.use_targeting, foes)
            self._rings.update(self.game, self.tsr_hdr, self.ring_mode != rings.OFF, self._shadows.palettes,
                               self._targeting.chosen)
            self._dust.update(self.game, self.tsr_hdr, self.show_dust, self._shadows.palettes)
        except (struct.error, IndexError, ValueError):
            return []
        return out

    def _panel_lines(self, lines: List[str], now: float) -> None:
        """A fight's lines into the combat log's panel (and those just after it: XP, the last kill);
        out of fights, those with a roll (a thief's skills, a scroll learned), for the panel opened
        with L."""
        try:
            if self.game is not None and self.game.in_combat():
                if self._fight_at is None or now - self._fight_at > FIGHT_LINES_AFTER:
                    self._fight_monsters = set()  # (a new fight)
                self._fight_at = now
        except (struct.error, IndexError, ValueError):
            pass
        if self._fight_at is not None and now - self._fight_at <= FIGHT_LINES_AFTER:
            self._panel.log.add(lines)
        else:
            self._panel.log.add(lines, rolls_only=True)

    def _panel_input(self, now: float) -> None:
        """The mouse on the combat log's panel: the scrollbar and the chip (DSCLOG's), the wheel
        (wheel.py) with the game's pointer over it; drawn again when it scrolls."""
        if self._wheel is None:
            self._wheel = wheel.WheelHook(getattr(getattr(self.guest, "proc", None), "pid", None))
        notches = self._wheel.take()
        if self.tsr_hdr is None or self.game is None:
            return
        panel = self._panel
        if not panel.shown:  # (L with the panel over the map hidden: show it)
            try:
                if panel.keys(self.game, self.tsr_hdr) and self.combat_log:
                    panel.open = True
                    _remember({"combat_log_open": True})
                    self._update_panel(now)
            except (struct.error, IndexError, ValueError):
                pass
            return
        before = (panel.first, panel.size, panel.level, panel.filter, panel.open)
        try:
            panel.mouse(self.game, self.tsr_hdr)
            if notches and panel.over():
                panel.wheel(notches)
            if panel.level != self.combat_log_level or panel.size != before[1] or panel.open != before[4]:
                self.combat_log_level = panel.level  # (the panel's level chip: the Options tab's too)
                _remember({"combat_log_level": panel.level, "combat_log_size": panel.size,
                           "combat_log_open": panel.open})
            if (panel.first, panel.size, panel.level, panel.filter, panel.open) != before:
                self._update_panel(now)
        except (struct.error, IndexError, ValueError):
            pass

    def _update_panel(self, now: float) -> None:
        """The combat log: the panel over the map while shown (L shows and hides it); in a fight with who acts and who is next in the header, the newest
        lines again when a fight starts."""
        fighting = self.combat_log and self.game.in_combat()
        if fighting:
            if self._fight_at is None or now - self._fight_at > FIGHT_LINES_AFTER:
                self._fight_monsters = set()  # (a new fight)
                self._panel.first = None
            self._fight_at = now
        on = self.combat_log and self._panel.open
        top, names = "", {}
        if on:
            if not self._font_tried:
                self._font_tried = True
                self._panel.font = _game_font(self.game_dir)
            self._panel.level = self.combat_log_level
            for n in range(game.PARTY_SIZE):
                name = self.game.creature_name(n)
                if name and not name.startswith("creature "):
                    names.setdefault(name, f"member{n}")
        if fighting:
            for index in set(self.game.combatants().values()):
                name = self.game.creature_name(index)
                if index >= game.PARTY_SIZE and name and not name.startswith("creature "):
                    self._fight_monsters.add(name)
            top = combatlog.header(self.round_status())
        names.update({m: "monster" for m in self._fight_monsters if m not in names})
        arena = None  # (between fights in the slave pens and the arena: their count in the header)
        if on and not fighting:
            try:
                if self.game.region() in combatlog.ARENA_REGIONS:
                    arena = self.game.number(game.ARENA_FIGHTS)
            except (struct.error, IndexError, ValueError):
                pass
        self._panel.update(self.game, self.tsr_hdr, on, self._shadows.palettes, top, names, arena)

    def _learn_lines(self) -> List[str]:
        """A preserver's tries at a scroll's spell since the last look (the rule for INT's chance:
        DSCLOG's INT_LEARN tells the last one in its header)."""
        if self.tsr_hdr is None or self.game is None:
            return []
        try:
            seq, who, spell, intelligence, rate, roll, result = struct.unpack(
                "<H6B", self.guest.read(self.tsr_hdr + TSR_LEARN, 8))
            if self._learn_seq is None or seq == self._learn_seq:
                self._learn_seq = seq
                return []
            self._learn_seq = seq
            from . import intlearn
            read, read_rate = self.guest.read(self.tsr_hdr + TSR_LEARN_READ, 2)
            return [intlearn.line(self.game.creature_name(who), self.game.spell_name(spell), intelligence, rate,
                                  roll, result, self.game.spell_level(spell), read, read_rate)]
        except (struct.error, IndexError, ValueError):
            return []

    def _items_still(self) -> bool:
        """The game's free lists of item records and of things the same over ITEMS_STILL_WAIT: it
        isn't building its item lists afresh (as START GAME does, or loading an area). The
        Loader's changes to them are made only then: one made across START GAME took the game's
        free list of item records from it (its head written over with the end of a party member's
        list), and the arena's things, the announcer among them, were never put on the map."""
        def heads() -> bytes:
            return b"".join(self.guest.read(self.game.ds * 16 + at, 2)
                            for at in (ring.FREE_ITEMS, ring.FREE_THINGS, ring.THINGS_USED))
        try:
            before = heads()
            time.sleep(ITEMS_STILL_WAIT)
            return heads() == before
        except (struct.error, IndexError, ValueError):
            return False

    def _kalzith_sold_out(self) -> None:
        """All six of Kalzith's scrolls bought: no more shop, and he carries his two, put on him
        only while the map's main loop runs (DSCLOG's count of it went up since the last look: no
        talk, menu or shop open)."""
        if self.tsr_hdr is None:
            return
        try:
            ticks = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_MAIN_TICKS, 2))[0]
            quiet = self._main_ticks is not None and ticks != self._main_ticks
            self._main_ticks = ticks
            kalzith.sold_out(self.game, quiet)
        except (struct.error, IndexError, ValueError):
            pass

    def _scroll(self) -> None:
        """The map's drag switches written to DSCLOG when they change."""
        if self.tsr_hdr is None:
            return
        try:
            self._scrolling.update(self.game, self.tsr_hdr, self.scroll_map)
        except (struct.error, IndexError, ValueError):
            pass

    def _dress_now(self, now: float) -> None:
        """The party dressed four times a second (not with the ring's search, every 3 s: a party
        walking off as an area loads was drawn plain till then)."""
        try:
            self._dress(now)
        except (struct.error, IndexError, ValueError):
            pass

    def _dress(self, now: float) -> None:
        """The party's sprites in what they wear, once the game has the Loader's SEGOBJEX (whose
        party pictures the Loader keeps dressed); as the game's own when switched off."""
        if not icons.ready(self.game, self.tsr_hdr):
            return
        if self._dresser is None and not self._dresser_tried:
            from . import launch
            self._dresser_tried = True
            import os
            copy = os.path.join(launch.DOS_DIR, icons.OBJECTS_FILE)
            self._dresser = sprites.Dresser.for_game(self.game, launch.find_game_dir(),
                                                     copy if os.path.exists(copy) else None, self.elf_looks)
            if self._dresser is not None and self.tsr_hdr is not None:
                hdr = self.tsr_hdr
                self._dresser.request_redraw = lambda: shadows.redraw(self.game, hdr)
        if self._dresser is not None and (self.show_gear or self._dresser.shown):
            self._dresser.update(self.show_gear, now)

    def _ring_search(self) -> List[str]:
        """While the arena's ring is still to be found: have DSCLOG show ring.SEARCH_TEXT instead
        of the arena script's "There is nothing on the body.", and once it has, put the ring
        in the leader's backpack."""
        if self.tsr_hdr is None:
            return []
        needed = self.arena_ring and ring.ring_needed(self.game)
        seq, = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_SWAP_SEQ, 2))
        fired = seq != self._swap_seq
        out = []
        if needed and fired:
            itemgate.hold(self.game)  # (ItemsBusy: the search is answered in a later pass)
        self._swap_seq = seq
        if needed and fired:
            given = ring.give_ring(self.game)
            itemgate.release(self.game)
            out.append(given or "No one in the party has room for the ring: make room and look at the body again.")
            needed = given is None
        on = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_SWAP_ON, 2))[0]
        if needed and not on:
            offset, = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_SWAP_OFF, 2))
            base = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_HDR_OFF, 2))[0] + offset
            self.guest.write(base, ring.NOTHING.encode("cp437").ljust(SWAP_SIZE, b"\0")[:SWAP_SIZE])
            self.guest.write(base + SWAP_SIZE, ring.SEARCH_TEXT.encode("cp437")[:SWAP_TEXT_SIZE - 1] + b"\0")
            self.guest.write(self.tsr_hdr + TSR_SWAP_ON, struct.pack("<H", 1))
        elif not needed and on:
            self.guest.write(self.tsr_hdr + TSR_SWAP_ON, struct.pack("<H", 0))
        return out

    def psp_changes(self) -> List[str]:
        """The party's PSP going down (a psionic power used, or kept up another round: the game
        takes each maintained power's cost every round) or back up."""
        out = []
        for index in range(game.PARTY_SIZE):
            rec = self.game.creature(index)
            if len(rec) < 4:
                continue
            psp = struct.unpack_from("<h", rec, game.CREATURE_PSP)[0]
            before, self._psp[index] = self._psp.get(index), psp
            if before is None or before == psp or not rec[game.CREATURE_NAME] or not 0 <= before <= 1000:
                continue  # unchanged, an empty party slot, or a record still being loaded
            who = self.game.creature_name(index)
            if psp < before:
                out.append(f"    {who} spends {before - psp} PSP ({before} -> {psp})")
            else:
                out.append(f"    {who} regains {psp - before} PSP ({before} -> {psp})")
        return out

    def ability_changes(self) -> List[str]:
        """The party's ability scores going up or down, once a change holds at two looks: a
        spell's or an effect's (Strength, Remove Curse giving back a lowered STR, Raise Dead's
        point of CON), and the game's own as time passes."""
        out = []
        for index in range(game.PARTY_SIZE):
            rec = self.game.creature(index)
            if len(rec) < CREATURE_ABILITIES + len(ABILITIES) or not rec[game.CREATURE_NAME]:
                self._abilities.pop(index, None)
                continue
            seen = (self.game.creature_name(index), tuple(rec[CREATURE_ABILITIES:CREATURE_ABILITIES + len(ABILITIES)]))
            before = self._abilities.get(index)
            if before is None or before[0] != seen[0] or not all(1 <= v <= 25 for v in before[1]):
                self._abilities[index] = seen  # (a new member, or a record being loaded)
                self._abilities_new.pop(index, None)
                continue
            if seen == before:
                self._abilities_new.pop(index, None)
                continue
            if self._abilities_new.get(index) != seen:
                self._abilities_new[index] = seen  # (seen once: it must hold)
                continue
            del self._abilities_new[index]
            self._abilities[index] = seen
            moved = [f"{name} {a} -> {b}" for name, a, b in zip(ABILITIES, before[1], seen[1]) if a != b]
            out.append(f"    {seen[0]}'s {', '.join(moved)}")
        return out

    def hp_changes(self, now: float) -> List[str]:
        """Every combatant's HP going down or up, with what's left (the game never shows a
        monster's HP). Put down to a spell while one is being cast (the damage after saves,
        resistances and protections, or the healing)."""
        g = self.game
        out = []
        current = {}
        for combatant, index in sorted(g.combatants().items()):
            rec = g.creature(index)
            if len(rec) < 2:
                continue
            hp = struct.unpack_from("<h", rec, 0)[0]
            current[index] = hp
            was_out_cold = self._out_cold.get(index, False)
            self._out_cold[index] = rec[game.CREATURE_STATUS] == game.OUT_COLD
            before = self._hp.get(index)
            if before is None or before == hp or not -100 <= before <= 2000:
                continue  # unchanged, or a record still being loaded
            who = g.creature_name(index)
            sheet = g.sheet(index)
            most = struct.unpack_from("<h", sheet, game.SHEET_MAX_HP)[0] if len(sheet) >= game.SHEET_SIZE else None
            left = f"now {hp}/{most} HP" if most and most > 0 else f"now {hp} HP"
            hit, resisted, unhurt = self._hits_seen(index, max(before - hp, 0), hp)
            for rolled in unhurt:
                reason = self._weapon_reason(index) or "a protection or resistance took it"
                out.append(f"  {who} takes none of the {rolled} damage: {reason}")
            if now <= self._spell_until and before - hp > hit:
                # the game's damage code gives a creature that was Out Cold the most the dice can do
                out_cold = " (Out Cold: the most the dice can do)" if was_out_cold else ""
                also = f" and {hit} from the hit" if hit else ""
                spell_id, spell_name = self._damage_source(before - hp - hit)
                halved = g.damage_halved_by(combatant, spell_id) if spell_id is not None else None
                halved = f" (halved: {halved})" if halved else ""
                out.append(f"  {who} takes {before - hp - hit} from {spell_name}{halved}{out_cold}{also}, {left}")
            elif hp - before == 1 and rec[game.CREATURE_ABILITIES + 2] >= REGENERATES:
                con = rec[game.CREATURE_ABILITIES + 2]  # (as AD&D's CON 20 and more: the game's own;
                # before a spell's healing: a tick of it just after a fire attack isn't the attack's)
                out.append(f"  {who} regenerates 1 HP (CON {con}), {left}")
            elif now <= self._spell_until and hp > before:
                out.append(f"  {who} regains {hp - before} HP from {self._spell_name}, {left}")
            elif hp < before:
                out.append(f"  {who} {left} (-{before - hp}{resisted})")
            else:
                out.append(f"  {who} {left} (+{hp - before})")
        self._hp = current
        return out + self.unhurt(now)

    def _hit(self, target: int, damage: int, now: float) -> None:
        """A weapon hit's damage rolled against TARGET: to be seen in its HP."""
        entry = self._hits.setdefault(target, {"hits": [], "at": now, "hp": self._hp.get(target)})
        entry["hits"].append(damage)
        entry["at"] = now

    def _hits_seen(self, index: int, lost: int, hp: int) -> Tuple[int, str, List[int]]:
        """The weapon hits a fall of LOST HP (to HP) took in, in the order they landed: (their
        damage, a note when one did less than its roll: resisted, and the hits before them that
        took none: immune, when the fall is just the later ones')."""
        entry = self._hits.get(index)
        if not entry:
            return 0, "", []
        hits, taken, note = entry["hits"], 0, ""
        if hp <= 0:  # (down: whatever was rolled, its HP ran out)
            del self._hits[index]
            return min(sum(hits), lost), "", []
        unhurt = []
        if lost and len(hits) <= HITS_MATCHED and not self._hits_prefix(hits, lost) \
                and self._weapon_reason(index) != monsters.HALF_REASON:  # (halved hits match nothing whole)
            match = self._hits_matching(hits, lost)
            if match is not None:  # (the fall is these hits exactly: the ones passed over took none)
                last = max(match)
                unhurt = [hits[i] for i in range(last) if i not in match]
                taken = lost
                del hits[:last + 1]
                if not hits:
                    del self._hits[index]
                else:
                    entry["hp"] = hp
                return taken, note, unhurt
        while hits and lost - taken >= hits[0]:
            taken += hits.pop(0)
        if hits and not taken and lost:  # (less than the hit)
            reason = self._weapon_reason(index)
            if reason and len(hits) > 1:  # (all of them cut down alike, seen as one fall)
                rolled, hits[:] = sum(hits), []
            else:
                rolled = hits.pop(0)
            taken = lost
            note = f": {lost} of the {rolled} rolled" + (f", {reason}" if reason else "")
        if hits:
            entry["hp"] = hp
        else:
            del self._hits[index]
        return taken, note, unhurt

    @staticmethod
    def _hits_prefix(hits: List[int], lost: int) -> bool:
        """Whether the first hits, in order, add up to LOST exactly."""
        total = 0
        for damage in hits:
            total += damage
            if total == lost:
                return True
        return False

    @staticmethod
    def _hits_matching(hits: List[int], lost: int) -> Optional[Tuple[int, ...]]:
        """The places of hits adding up to LOST exactly, the set ending soonest (fewest hits
        passed over), or None."""
        best = None
        for size in range(1, len(hits) + 1):
            for places in itertools.combinations(range(len(hits)), size):
                if sum(hits[i] for i in places) == lost and (best is None or max(places) < max(best)):
                    best = places
        return best

    def unhurt(self, now: float, force: bool = False) -> List[str]:
        """Weapon hits that took no HP (HIT_WAIT seconds on, or FORCE: a new round): the target
        immune to the weapon, or protected (Stoneskin...)."""
        out = []
        for index, entry in list(self._hits.items()):
            if not force and now - entry["at"] < HIT_WAIT:
                continue
            del self._hits[index]
            rec = self.game.creature(index)
            hp = struct.unpack_from("<h", rec, 0)[0] if len(rec) >= 2 else None
            if hp is None or hp <= 0 or (entry["hp"] is not None and entry["hp"] != hp):
                continue  # (its HP did go down, or it's gone: not unhurt)
            reason = self._weapon_reason(index) or "a protection or resistance took it"
            rolled = sum(entry["hits"])
            out.append(f"  {self.game.creature_name(index)} takes none of the {rolled} damage: {reason}")
        return out

    def _weapon_reason(self, index: int) -> Optional[str]:
        """What the creature's defences say about weapons, if anything."""
        if index < game.PARTY_SIZE:
            return None
        try:
            if self._tables is None:
                self._tables = monsters.MonsterTables(self.guest.read, self.game.load_seg)
            d = monsters.creature_defences(self.game, self._tables, index)
        except (struct.error, IndexError, ValueError):
            return None
        return monsters.weapon_reason(d) if d is not None else None

    def _damage_source(self, lost: int) -> Tuple[Optional[int], str]:
        """The spell an HP loss of LOST came from: the latest recent roll it matches, whole or
        halved (taken off the list), else the spell being cast."""
        for i in range(len(self._recent_damage) - 1, -1, -1):
            spell, rolled = self._recent_damage[i]
            if lost in (rolled, rolled // 2):
                del self._recent_damage[i]
                return spell, self.game.spell_name(spell)
        return self._spell_id, self._spell_name

    def _spell_cast(self, spell: Optional[int], now: float) -> None:
        """A spell is taking effect: HP changes for the next few seconds are its doing."""
        if spell is not None:
            self._spell_name = self.game.spell_name(spell)
            self._spell_id = spell
            self._spell_until = now + SPELL_WINDOW

    def speaker(self, portrait: Optional[int]) -> str:
        """Who a dialogue portrait belongs to, as far as is known."""
        if portrait is None:
            return "(no portrait)"
        if portrait == 0:
            return "Narration"  # the window shows an emblem, not a face
        return (self.speaker_names.get(portrait) or game.SPEAKERS.get(portrait)
                or self.learned_speakers.get(portrait) or f"Portrait {portrait}")

    def _follow_talk(self, rec) -> None:
        """Learn portraits' names: a conversation (the window opening to CLOSE) that shows a single
        face, started on a named creature, is that creature talking. With several faces (a scene
        where others speak too) it can't be told who is who, so nothing is learned."""
        if rec.kind == KIND_PORTRAIT:
            if self._talk is None:
                try:
                    target = self.game.talk_target()
                except (struct.error, IndexError, ValueError):
                    target = None
                self._talk = {"portraits": set(), "with": target}
            if rec.value:
                self._talk["portraits"].add(rec.value)
        elif rec.kind == KIND_TEXT and rec.text == "CLOSE" and self._talk is not None:
            talk, self._talk = self._talk, None
            if len(talk["portraits"]) == 1 and talk["with"]:
                portrait = next(iter(talk["portraits"]))
                if portrait in game.SPEAKERS:
                    pass  # known already (the Announcer calls out mid-fight, "started on" a fighter)
                elif self.learned_speakers.get(portrait) != talk["with"]:
                    self.learned_speakers[portrait] = talk["with"]
                    self._new_speakers[portrait] = talk["with"]

    def take_speakers(self) -> Dict[int, str]:
        """Portrait names learned since the last call."""
        out, self._new_speakers = self._new_speakers, {}
        return out

    def _reply_choice(self, now: float) -> List[DialogueEntry]:
        """The player's answer, once, when they click a reply."""
        chosen, before = self.game.reply_chosen(), self._reply
        self._reply = chosen
        if chosen is None or chosen == before or not chosen[1]:
            return []
        return self.dialogue.flush() + [DialogueEntry(None, chosen=chosen[1])]

    def take_dialogue(self) -> List[DialogueEntry]:
        """Dialogue that has come in since the last call (lines() collects it)."""
        out, self._dialogue = self._dialogue, []
        self.itemwatch.remember_talk(out)
        return out

    def _party_check(self, now: float) -> bool:
        """True for a while after the party changes (a game was loaded): what's there is not news."""
        party = self.game.party_signature()
        if party != self._party:
            self._party, self._party_changed_at = party, now
        if now - self._party_changed_at < LOAD_SETTLE:
            if self.tracker:
                self.tracker.reset()
            self.defilers.reset()
            self.itemwatch.reset()
            return True
        return False

    # ---- effects (spells and powers on creatures) ------------------------------

    def count_charges(self, entries: Sequence[Entry]) -> None:
        """The charges these entries use, by (combatant, effect): by the time they are read, the
        effects' records show them all used, so each charge's line adds back those still to come."""
        self._charges_ahead = {}
        if self.game is not None:  # (and the effects with charges now, for _overlay_charge)
            held = {(effect.owner, effect.id) for effect, charges, _ in self.game.effects_left() if charges}
            self._charged, self._charged_before = held, self._charged
            for effect, spell in self.game.effect_spells():  # (kept: the last charge takes the record)
                if (effect.owner, effect.id) in held:
                    self._charge_spells[(effect.owner, effect.id)] = spell
        for e in entries:
            charge = (e.parent_code.startswith(CHARGE_USED_RETURN)
                      or self._overlay_charge(e, e.arg(6) or 0, e.arg(8) or 0))
            if (charge and e.parent_arg(6) is not None
                    and e.parent_arg(8) not in (None, ACID) and (e.arg(6) or 0) > 0):
                key = (e.parent_arg(6), e.parent_arg(8))  # (each charge's 2d4: one entry a die)
                self._charges_ahead[key] = self._charges_ahead.get(key, 0) + 1 / e.arg(6)

    def _overlay_charge(self, e: Entry, count: int, sides: int) -> bool:
        """The charge routine's 2d4 when the overlay manager has swapped its return address for an
        INT 3Fh stub (so CHARGE_USED_RETURN can't be matched): its arguments are still (creature,
        effect), an effect that creature has charges of, or had at the last poll (the last charge
        removes it). A spell's duration roll behind the same stub has (spell, level) there."""
        if not e.parent_code.startswith(OVERLAY_TRAP) or (count, sides) != (2, 4):
            return False
        key = (e.parent_arg(6), e.parent_arg(8))
        return key in self._charged or key in self._charged_before

    def _charges_after(self, owner: int, eid: int) -> int:
        """The charges on OWNER's effect EID once this charge is used. The record shows every
        charge used up to the poll, so the ones still to be told of in this poll's entries are
        added back."""
        key = (owner, eid)
        ahead = max(round(self._charges_ahead.get(key, 1)) - 1, 0)
        self._charges_ahead[key] = ahead
        return (self.game.charges_left(owner, eid) if self.game is not None else 0) + ahead

    def _name(self, combatant: int) -> str:
        """A combatant's name, remembered for when the fight is over."""
        name = self.game.combatant_name(combatant)
        if name != "?":
            self._names[combatant] = name
        return self._names.get(combatant, name)

    def effect_changes(self, now: float = 0.0) -> List[str]:
        """Lines for effects that started or ended since the last look."""
        current = Counter(self.game.effects())
        for eff in current:
            self._name(eff.owner)
            self._name(eff.caster)
        loading = self._party_check(now)
        if self._effects is None or loading:
            self._effects = current  # the first look, or just loaded: remember what is active
            return []
        started, ended = current - self._effects, self._effects - current
        self._effects = current
        out = []
        by_cast: Dict[Tuple[int, int], List[int]] = {}
        for eff in started.elements():
            by_cast.setdefault((eff.caster, eff.id), []).append(eff.owner)
        for (caster, eid), owners in by_cast.items():
            name = EFFECT_NAMES.get(eid, f"effect {eid}")
            targets = ", ".join(self._name(o) for o in owners)
            rule = f": {EFFECT_RULES[eid]}" if eid in EFFECT_RULES else ""
            if owners == [caster] * len(owners):  # on itself (or from a spell on the ground)
                out.append(f"{name} on {targets}{rule}")
            else:
                out.append(f"{self._name(caster)} gives {name} to {targets}{rule}")
        by_end: Dict[int, List[int]] = {}
        for eff in ended.elements():
            by_end.setdefault(eff.id, []).append(eff.owner)
        for eid, owners in by_end.items():
            name = EFFECT_NAMES.get(eid, f"effect {eid}")
            out.append(f"{name} ends on {', '.join(self._name(o) for o in owners)}")
        return out

    # ---- describing -----------------------------------------------------------

    def describe(self, e: Entry, show_all: bool = False, now: float = 0.0) -> List[str]:
        """Log lines for `e` (none if it isn't worth showing, or completes later)."""
        try:
            return self._describe(e, show_all, now)
        except Exception as err:  # an unexpected entry must never stop the log
            if show_all:
                return [f"rand() = {e.raw}  (at {e.cs:04x}:{e.ip:04x}; could not decode: {err})"]
            return []

    def flush(self, now: float, force: bool = False) -> List[str]:
        """Dice that waited long enough without a spell turning up."""
        out = []
        while self._pending and (force or now - self._pending[0].at >= PENDING_SECONDS):
            p = self._pending.pop(0)
            if p.resistance:
                out += self._magic_resistance(*p.resistance)
            else:
                out.append(f"Dice: {p.text}")
        return out

    def _describe(self, e: Entry, show_all: bool, now: float) -> List[str]:
        if e.kind == KIND_ROLL and e.code.startswith(INITIATIVE_ROLL):
            self._initiative_roll, self._initiative_at = scaled(e.raw, 10), now
            return []
        if e.kind == KIND_ROLL and e.code.startswith(INITIATIVE_TIE):
            if self._initiative_roll is not None:
                self._initiative.append((self._initiative_roll, scaled(e.raw, 200)))
            self._initiative_roll, self._initiative_at = None, now
            return []
        return self.initiative_lines() + self._describe_entry(e, show_all, now)

    def turn_lines(self) -> List[str]:
        """'Gerakis's turn' whenever the turn passes during a fight."""
        if self._initiative or self._initiative_roll is not None:
            return []  # a round is starting: its order comes first
        turn = self.game.whose_turn()
        if turn is None or turn == self._turn:
            return []
        first = self._first_able()
        if self._turn is None and turn == self._stale_turn and first is not None and first != turn:
            return []  # (the last round's last turn, still shown before the new round's first)
        self._turn, self._stale_turn = turn, None
        self._acted.add(turn)
        self._set_stealth(False)  # the last turn's hiding is over
        now = self.game.game_time()
        if self._round_time is None or now is None or now - self._round_time > FIGHT_GAP:
            return []  # not in a fight
        name = self.game.combatant_name(turn)
        out = [f"{name}'s turn"] if name != "?" else []
        if self.rules & game.RULE_STEALTH and turn < game.PARTY_SIZE:
            try:
                lines, hidden = stealth.turn(self.game, turn, self.stealth_roll, self.stealth_gear)
            except (struct.error, IndexError, ValueError):
                lines, hidden = [], False
            out += lines
            self._set_stealth(hidden, turn)
        return out

    def _first_able(self) -> Optional[int]:
        """The first in the round's order who can act (alive and up: one down is passed over)."""
        for combatant, _, _ in self.round_order or ():
            if combatant is None:  # (a name in the order matched to no one)
                continue
            index = self.game.combatant_creature(combatant)
            rec = self.game.creature(index) if index is not None else b""
            if len(rec) > game.CREATURE_STATUS and struct.unpack_from("<h", rec, 0)[0] > 0 \
                    and rec[game.CREATURE_STATUS] in game.STATUS_ABLE:
                return combatant
        return None

    def _fighting(self) -> bool:
        """In a fight, by the game's own test (game.fight_on: as its rest's and the USE screen's;
        its IN_COMBAT flag stays up while the party walks spread out, uncollapsed, with no one to
        fight; game time barely moves outside fights, so the time since the last round can't tell)."""
        try:
            return self.game.fight_on()
        except (struct.error, IndexError, ValueError):
            return False

    def _set_stealth(self, hidden: bool, member: int = 0) -> None:
        """Have DSCLOG make this party member's next attack one from behind (or no one's)."""
        if self.tsr_hdr is not None:
            self.guest.write(self.tsr_hdr + stealth.TSR_STEALTH, struct.pack("<H", 1 << member if hidden else 0))

    def round_status(self, acted_creatures: frozenset = frozenset()) -> Optional[dict]:
        """The round in progress, for keeping its order in view: {"round", "now": (name, score),
        "next": [(name, score)...], "done": [...], "down": [...]}, in initiative order; None
        outside a fight. Creatures (indexes) in `acted_creatures` count as done: their rolls
        are in, though the game hasn't passed the turn on yet."""
        now = self.game.game_time()
        if not self.round_order or self._round_time is None or now is None or now - self._round_time > FIGHT_GAP:
            return None
        acting = self.game.whose_turn()
        out = {"round": self.round_number, "now": None, "next": [], "done": [], "down": []}
        for combatant, name, score in self.round_order:
            index = self.game.combatant_creature(combatant) if combatant is not None else None
            try:
                if index is not None:
                    hp = struct.unpack_from("<h", self.game.creature(index), 0)[0]
                else:  # a killed creature leaves the fight's table
                    hp = 0 if combatant is not None else 1
            except (struct.error, IndexError, ValueError):
                hp = 1
            if hp <= 0:
                out["down"].append((name, score))
            elif index is not None and index in acted_creatures:
                out["done"].append((name, score))
            elif combatant == acting:
                out["now"] = (name, score)
            elif combatant in self._acted:
                out["done"].append((name, score))
            else:
                out["next"].append((name, score))
        return out

    def _round_number(self) -> int:
        """The round of this fight: the game's clock moves 60 seconds a round, and a longer gap
        means a new fight."""
        now = self.game.game_time()
        if now is None:
            return 0
        if self._round_time is None or now - self._round_time > FIGHT_GAP or now < self._round_time:  # (or a game loaded)
            _new_fight(self)
        self._round_time = now
        self._round += 1
        return self._round


    def initiative_lines(self) -> List[str]:
        """The round's order, from the rolls collected since the round began."""
        pairs, self._initiative = self._initiative, []
        if not pairs:
            return []
        unhurt = self.unhurt(0.0, force=True)  # a new round: hits not seen in HP by now never will be
        g = self.game
        combatants = g.combatants()
        table = g.initiative(max(combatants.values(), default=0) + 1)
        effects = g.effects()
        rows, used, path = [], set(), None
        for roll, tie in pairs:
            # the game keeps each creature's tie-break roll: that says whose rolls these were
            found = [(c, i) for c, i in sorted(combatants.items()) if i not in used and table[i][1] == tie]
            if not found:
                rows.append((INITIATIVE_BASE + roll, tie, f"? {INITIATIVE_BASE + roll}", f"{roll} (0-9 roll)", None, "?"))
                continue
            combatant, index = found[0]
            used.add(index)
            parts = []
            dex = g.dex_initiative(g.creature(index)[CREATURE_ABILITIES + 1])
            if dex:
                parts.append((dex, "DEX"))
            ids = {x.id for x in effects if x.owner == combatant and x.id in game.INITIATIVE_EFFECTS}
            parts += [(game.INITIATIVE_EFFECTS[eid], EFFECT_NAMES[eid]) for eid in sorted(ids)]
            outdoors = index < game.PARTY_SIZE and g.outdoors(index)
            for kid in g.kit_ids(index):
                if kits.initiative(kid, outdoors):
                    parts.append((kits.initiative(kid, outdoors), kits.name(kid) + (
                        " under the open sky" if kid == kits.SCOUT else "")))
            if index < game.PARTY_SIZE and path is None:  # (the same for the whole party: once a round)
                path = (kits.PATH_INITIATIVE, "Wayfinder's Path-finder") if g.path_finder() else \
                    (-kits.PATH_INITIATIVE, "Wayfinder down") if g.path_lost() else ()
            if index < game.PARTY_SIZE and path:
                parts.append(path)
            score = INITIATIVE_BASE + roll + sum(v for v, _ in parts)
            stored = table[index][0]
            if stored >= 0 and stored != score:  # not acted yet, and something else counted
                parts.append((stored - score, "other"))
                score = stored
            steps = f"{roll} (0-9 roll)" + "".join(f" {signed(v)} {name}" for v, name in parts)
            rows.append((score, tie, f"{g.creature_name(index)} {score}", steps, combatant, g.creature_name(index)))
        rows.sort(key=lambda r: (-r[0], -r[1]))
        scores = Counter(r[0] for r in rows)
        number = self._round_number()
        if self._kits_due and number != 1:  # (a new fight by the fight flag, the clock not yet past FIGHT_GAP:
            _new_fight(self)                #   the arena's next wave) everything a new fight resets
            self._round = number = 1
        self.round_number = number
        start, self._kits_due = number == 1, False  # (a new fight, or one after a fight's end)
        if start:
            self._fight_seen, self._out_of_fight = False, None
        danced = self._dances.round(g, self.tsr_hdr, number, start=start)
        danced += self._wild.round(g, self.tsr_hdr, number, start=start)
        self.round_order = [(combatant, name, score) for score, _, _, _, combatant, name in rows]
        self._acted = set()
        # a new round: its first turn is a new turn even for whoever had the last one (a thief
        # last in one round and first in the next still hides), so that one is forgotten
        self._stale_turn, self._turn = self._turn, None
        order = ", ".join(r[2] for r in rows)
        out = [f"Round {number}" + (f": {order}" if order else "") if number else f"Initiative: {order}"]
        for score, tie, who, steps, _, _ in rows:
            tied = f", tie broken by {tie} (0-199 roll)" if scores[score] > 1 else ""
            out.append(f"    {who} = {INITIATIVE_BASE} + {steps}{tied}")
        return unhurt + out + danced

    def _describe_entry(self, e: Entry, show_all: bool, now: float) -> List[str]:
        if e.kind == KIND_SAVE:
            return self._save(e)
        if e.kind == KIND_AC:
            return self._ac(e, show_all)
        if e.kind == KIND_ITEM:
            return self._item_check(e)
        if e.kind == KIND_SCRIPT:
            return self._script_roll(e, show_all)
        if e.kind == KIND_REQUEST:
            return self._request(e, show_all)
        if e.kind == KIND_AIM:
            return self._aim(e)
        if e.kind == KIND_WALL:
            return self._wall(e, now)
        if e.kind == KIND_HEAT:
            return self._heat(e, now)
        if e.kind == KIND_SWEPT:
            return [f"    {self._name(e.raw)} is swept off its feet: loses its next turn"]
        if e.kind == KIND_CAST:
            self._cast = (e.arg(6), e.raw)  # (who cast what, for a kit's damage: DSCLOG's CAST_WHO)
            self._float(e.arg(6), self.game.spell_name(e.raw), labels.SPELL_INK, now)
            return []
        code = e.code
        if code.startswith(ATTACK_SITE):
            self._spell_until = 0.0
            out = self.flush(now, force=True) + self._attack(e)
            if len(out) >= 2 and out[-2].endswith("-> miss"):
                self._float(e.glob[0], labels.MISS, labels.MISS_INK, now)
            return out
        if code.startswith(DICE_SITE):
            return self._dice_roll(e, show_all, now)
        if code.startswith(IMAGE_BLOW_SITE):
            target, chance = e.arg(6), e.arg(0x0A)
            if target is None or chance is None:
                return []
            return [self._image_line(target, scaled(e.raw, 100) + 1, chance, spell=False)]
        if code.startswith(CHECK_SITE):
            return self.flush(now, force=True) + self._check(e, show_all)
        if code.startswith(BREAK_ROLL_1) or code.startswith(BREAK_ROLL_2):
            return self._break_check(e, code.startswith(BREAK_ROLL_1), show_all)
        if code.startswith(PERCENT_SITE):
            return self._thief_skill(e)
        if code.startswith(RANGE_SITE):
            lines = self._range_roll(e)
            if lines is not None:
                return lines
        if show_all:
            generic = generic_roll(code, e)
            where = f"{e.cs:04x}:{e.ip:04x}"
            if generic:
                return [f"{generic[0]} = {generic[1]}  (at {where})"]
            return [f"rand() = {e.raw}  (at {where})"]
        return []

    def _image_line(self, target: int, roll: int, chance: int, spell: bool) -> str:
        """Mirror Images' d100 against a hit or a spell on TARGET: an image takes it on CHANCE or
        less (0: a spell from the target's own side, which no image takes)."""
        what = "spell" if spell else "blow"
        head = f"    {EFFECT_NAMES[game.MIRROR_EFFECT]} on {self._name(target)}: d100 = {roll}"
        if not chance:
            return f"{head}, a spell from its own side -> no image takes it"
        took = (f"an image is struck instead, the {what} lost" if roll <= chance else f"the {what} gets through")
        return f"{head}, {chance} or less strikes an image -> {took}"

    def _thief_skill(self, e: Entry) -> List[str]:
        """A thief skill check (the game's routine at 803B8h): d100 under the skill's chance plus
        the situation's bonus. Its arguments are (character, skill, bonus); [BP-2] the chance.
        Effects change the bonus in place before the roll (Enlarge scales it; an effect that
        rules the skill out takes 1000 off), so the frame holds the bonus as it was used."""
        chance, roll = e.local(-2), e.raw % 100 + 1
        who, skill, bonus = e.arg(6), e.arg(8), e.arg(0x0C) or 0
        if chance is None or who is None or skill is None:
            return []
        name = game.THIEF_SKILLS[skill] if 0 <= skill < len(game.THIEF_SKILLS) else f"skill {skill}"
        head = f"{self._name(who)} tries to {name}: d100 = {roll}"
        if chance <= -500:  # the game takes 1000 off when an effect makes it impossible
            return [f"{head} -> failure (an effect stops it)"]
        head += f", needs {chance} or less -> {'success' if roll <= chance else 'failure'}"
        creature = self.game.combatant_creature(who)
        parts = self.game.thief_skill_parts(creature, skill) if creature is not None else None
        if parts is None:
            return [head]
        outdoors = self.game.outdoors(creature)
        kid = next((k for k in self.game.kit_ids(creature) if kits.thief_skill(k, skill, outdoors)), 0)
        kit = kits.thief_skill(kid, skill, outdoors)
        if kit and chance == 0:  # (no less than 0: what the kit took off can't be told apart)
            kit = 0
        rest = chance - bonus - kit - sum(n for _, n in parts)
        steps = [f"{n}" if what == "base" else f"{n} {what}" if not i else f"{signed(n)} {what}"
                 for i, (what, n) in enumerate(parts)]
        if kit:
            steps.append(f"{signed(kit)} {kits.name(kid)}")
        capped = self.game.rules & game.RULE_THIEF_TABLE and rest < 0 and chance - bonus == game.THIEF_MOST
        if bonus:
            steps.append(f"{signed(bonus)} this attempt")
        if rest and not capped:  # the only other part of the chance: the equipment penalty
            steps.append(f"{signed(rest)} equipment")
        if capped:  # (DSCLOG's PROBE_BELT: AD&D's most, the equipment penalty, if any, within it)
            steps.append(f"(at most {game.THIEF_MOST})")
        return [head, f"    {name} {chance} = " + " ".join(steps).replace(" +", " + ").replace(" -", " - ")]

    def _float(self, thing: Optional[int], text: str, colour, now: float, priority: int = 0) -> None:
        """TEXT floating over combatant THING for a moment (labels.py), with the switch on."""
        if not self.floating_names or self.tsr_hdr is None:
            return
        if not self._labels_font_tried:
            self._labels_font_tried = True
            self._labels.font = _game_font(self.game_dir)
        try:
            self._labels.show(self.game.guest, self.tsr_hdr, thing, text, colour, now, priority)
        except (struct.error, IndexError, ValueError):
            pass

    # attacks ---------------------------------------------------------------------

    def _attack(self, e: Entry) -> List[str]:
        g = self.game
        d20 = scaled(e.raw, 20) + 1
        thac0, ac = e.arg(0x0A), e.arg(0x0C)
        attacker, item, item_type, mode = e.arg(0x0E), e.arg(0x12), e.arg(0x14), e.arg(0x16)
        attacker_combatant, target_combatant = e.arg(0x18), e.glob[0]
        need = thac0 - ac
        hit = d20 == 20 or (d20 != 1 and d20 >= need)
        note = " (natural 20)" if d20 == 20 else " (natural 1)" if d20 == 1 else ""

        self._last_attacker = g.creature_name(attacker)
        target_index = g.combatant_creature(target_combatant)
        if target_index is not None:
            self.last_ac[target_index] = ac
            self._ac_whose[target_index] = g.creature_name(target_index)
        weapon = g.weapon(item, item_type)
        with_what = f" with {g.weapon_name(weapon)} ({weapon.dice()})" if weapon else ""
        target = g.combatant_name(target_combatant)
        # the attack's own arguments: [BP+1Eh] a backstab, [BP+20h] from behind
        how = " BACKSTAB" if e.arg(0x1E) and e.arg(0x20) else " from behind" if e.arg(0x20) else ""
        chance = hit_chance(need)
        needs = ("hits on anything but a 1" if need <= 2 else "only a 20 hits" if need > 20 else f"needs {need}+")
        head = (f"{g.creature_name(attacker)} attacks {target}{how}{with_what}: d20 = {d20}{note}, "
                f"{needs} ({chance}%), hits AC {thac0 - d20}, target AC {ac} -> {'HIT' if hit else 'miss'}")
        skill = self.weapon_skill(attacker, item_type)
        kit_name, kit_hit, _ = self._kit_attack(attacker, item_type, mode, target_combatant)
        breakdown = self._thac0_breakdown(e, thac0, attacker, attacker_combatant, target_combatant, weapon, mode, item_type,
                                          (specialize.SKILL_NAMES.get(skill, ""), specialize.to_hit(skill)),
                                          [(kit_name, kit_hit)] if kit_hit else [])
        return [head, "    " + breakdown]

    def weapon_skill(self, attacker: Optional[int], item_type: Optional[int]) -> int:
        """A creature's weapon specialization skill with a weapon (specialize.skill), with the rule on."""
        if attacker is None or not self.game.rules & game.RULE_SPECIALIZE:
            return specialize.NONE
        sheet = self.game.sheet(attacker)
        return specialize.skill(sheet, item_type) if len(sheet) >= game.SHEET_SIZE else specialize.NONE

    def _thac0_breakdown(self, e: Entry, thac0: int, attacker: int, attacker_combatant: int,
                         target_combatant: int, weapon, mode: int, item_type: Optional[int] = None,
                         skill: Tuple[str, int] = ("", 0),
                         kit: Sequence[Tuple[str, int]] = ()) -> str:
        """'THAC0 16, +6 STR, +1 Blessed, ... = 9', from the attack setup's locals and the game's rules
        (and SKILL, weapon specialization's (name, to-hit), which DSCLOG takes off after them)."""
        g = self.game
        base = g.creature(attacker)[CREATURE_THAC0]
        after_f1, hit_bonus = e.parent_local(-0x20), e.parent_local(-8)
        rear, backstab = e.parent_local(-0x1A), e.parent_local(-0x24)
        parts: List[Tuple[str, int]] = []
        if None in (after_f1, hit_bonus) or after_f1 - hit_bonus != thac0 + skill[1] + sum(v for _, v in kit):
            return f"THAC0 {base} base, {signed(base - thac0)} in bonuses = {thac0}"
        rear_hit = min((kits.rear_to_hit(k) for k in g.kit_ids(attacker)), default=kits.REAR) \
            if attacker < game.PARTY_SIZE else kits.REAR  # (DSCLOG's KIT_REAR)
        if rear:
            parts.append(("from behind" + (" (Rescuer)" if rear_hit != kits.REAR else ""), rear_hit))
        if backstab:
            parts.append(("backstab", 2))
        situational = base - after_f1 - rear_hit * bool(rear) - 2 * bool(backstab)
        # the spell effects the game checks here (from its code)
        effects = g.effects()
        on = lambda combatant, eid: any(x.owner == combatant and x.id == eid for x in effects)
        for eid, value in ((7, 1), (12, -1), (47, -4), (49, 1)):  # (Fogbolt's below, with Blur)
            if on(attacker_combatant, eid):
                parts.append((EFFECT_NAMES[eid], value))
                situational -= value
        if on(target_combatant, 55):
            parts.append(("target's Blur", -2))
            situational += 2
        if mode is not None and mode <= 1 and specialize.kind_of(item_type) in worldgear.SWORD_KINDS \
                and g.wears_type(g.combatant_creature(target_combatant), game.URNST_GIRDLE_TYPE, WAIST_SLOT):
            parts.append(("target's Girdle of Urnst", -worldgear.URNST_AC))  # (DSCLOG's ITEM_REAR)
            situational += worldgear.URNST_AC
        if on(attacker_combatant, game.FOG_EFFECT):  # (the new spells' Fogbolt: DSCLOG's NS_HIT)
            parts.append(("Fogbolt", -3))
            situational += 3
        if on(target_combatant, game.FOG_EFFECT):
            parts.append(("target's Fogbolt", 2))
            situational -= 2
        prayer = next((x for x in effects if x.owner == attacker_combatant and x.id == 73), None)
        if prayer:
            caster = g.combatant_creature(prayer.caster)
            same = caster is not None and g.creature(caster)[CREATURE_SIDE] == g.creature(attacker)[CREATURE_SIDE]
            parts.append(("Prayer", 1 if same else -1))
            situational -= 1 if same else -1
        if situational:
            parts.append(("STR" if mode <= 1 else "DEX", situational))
        rest = hit_bonus
        if weapon:
            if weapon.plus:
                parts.append(("weapon", weapon.plus))
                rest -= weapon.plus
            if not weapon.plus and not weapon.nonmagical_flag and weapon.material in MATERIAL_TO_HIT:
                penalty = MATERIAL_TO_HIT[weapon.material]
                parts.append((MATERIALS[weapon.material].lower(), penalty))
                rest -= penalty
        elif g.rules & game.RULE_NEW_SPELLS and on(attacker_combatant, game.CLAW_EFFECT):
            parts.append(("Erdlu Claw", 1))  # (unarmed: DSCLOG's NS_FIST, in [BP-8])
            rest -= 1
        # With two weapons ready the game adjusts every melee attack by the DEX table it
        # also uses for initiative, sign flipped and never below 0 (rangers excepted): a
        # bonus at DEX 5 or less, nothing otherwise. The manual's off-hand penalty isn't there,
        # unless the Loader's rule puts AD&D's in (GameData.two_weapons).
        weapons_ready = e.parent_local(-0x16)
        if mode <= 1 and weapons_ready is not None and weapons_ready >= 2:
            item = e.arg(0x12)
            slot = None
            if item is not None and 0 <= item < game.NO_ITEM:
                at = game.far_pointer(g.guest, g.ds, game.ITEMS_PTR) + item * game.ITEM_SIZE
                slot = g.guest.read(at + game.ITEM_SLOT, 1)[0]
            why, two_weapons = g.two_weapons(attacker, slot)
            if two_weapons:
                parts.append((why, two_weapons))
                rest -= two_weapons
        if attacker_combatant is not None and attacker_combatant >= 4:
            difficulty = g.difficulty() - 1
            if difficulty:
                parts.append(("difficulty", difficulty))
                rest -= difficulty
        if rest:
            parts.append(("off-hand and other", rest))
        if skill[1]:
            parts.append(skill)
        parts += kit
        text = ", ".join(f"{signed(v)} {name}" for name, v in parts if v)
        return f"THAC0 {base}" + (f", {text}" if text else "") + f" = {thac0}"

    def _dice_roll(self, e: Entry, show_all: bool, now: float) -> List[str]:
        weapon = e.parent_code.startswith(WEAPON_DAMAGE_RETURN)
        # Two routines roll NdS with this code; only the weapon one takes a bonus argument
        count, sides, bonus = e.arg(6), e.arg(8), e.arg(0x0A) if weapon else 0
        key = (e.ss, e.bp, e.cs, e.ip)
        faces = self._dice.setdefault(key, [])
        faces.append(scaled(e.raw, sides) + 1)
        if len(faces) < count:
            return []
        del self._dice[key]
        faces_text = "[" + " + ".join(map(str, faces)) + "]"
        if not weapon:
            if count == 1 and sides == 20 and self._is_save_roll(e):
                return self._save_roll(e, now)
            if count == 1 and sides == 10 and e.parent_code.startswith(SPECIAL_EFFECT_RETURN):
                target, attacker = e.parent_arg(6), e.parent_arg(8)
                return [f"    {self._name(attacker)}'s special effect on {self._name(target)}: d10 = {faces[0]}, "
                        f"works on a 1 -> {'it works' if faces[0] == 1 else 'no effect'}"]
            if e.parent_code.startswith(CREATION_ABILITY_RETURN):
                return self._creation_ability(e, sum(faces), now)
            if count == 1 and e.parent_code.startswith(LEVEL_HP_RETURNS) and e.parent_arg(2) == CREATION_HP_CALLER:
                return self._creation_hp_roll(e, sides, faces[0], now)
            if count == 1 and any(e.parent_code.startswith(c) for c in RANDOM_NAME_RETURNS):
                return [f"Character creation: a name picked at random, 1d{sides} = {faces[0]}"]
            if count == 1:
                level_up = self._level_hp(e, sides, faces[0])
                if level_up is not None:
                    return level_up
            if count == 1 and sides == 10 and e.parent_code.startswith(CONFUSION_ROLL_RETURN):
                what = next(text for top, text in CONFUSION_RESULTS if faces[0] <= top)
                return self.flush(now, force=True) + [
                    f"{self._name(e.parent_arg(6))} is confused: d10 = {faces[0]} -> {what}"]
            if count == 1 and sides == 2 and e.parent_code.startswith(RANDOM_SIDE_RETURN):
                side = "the party's" if faces[0] == 1 else "the monsters'"
                return [f"    {self._name(e.parent_arg(6))} fights on {side} side this turn (d2 = {faces[0]})"]
            if e.parent_code.startswith(STRENGTH_ROLL_RETURN) and e.parent_arg(0x0E) is not None:
                spell, target = e.parent_arg(0x0E), e.parent_arg(6)
                self._spell_cast(spell, now)
                if spell == game.FRIENDS_SPELL:  # (Friends, a new spell, uses Strength's code, rolling 2d4)
                    total = sum(faces)
                    return self.flush(now, force=True) + [
                        f"Friends: {count}d{sides} = {faces_text} = {total} -> {self._name(target)}'s CHA +{total} "
                        f"while it lasts (at most {game.FRIENDS_MOST})"]
                # (Cat's Grace, a new spell, uses Strength's code for DEX)
                ability = "DEX" if spell == game.GRACE_SPELL else "STR"
                return self.flush(now, force=True) + [
                    f"{self.game.spell_name(spell)}: 1d{sides} = {faces[0]} -> {self._name(target)}'s {ability} "
                    f"+{faces[0]} while it lasts (at most {STR_MOST})"]
            if count == 1 and sides == 100 and e.parent_code.startswith(RESISTANCE_ROLL_RETURN):
                return self._magic_resistance(e.parent_arg(6), e.parent_arg(8), faces[0])
            if count == 1 and sides == 100 and (e.parent_code.startswith(IMAGE_SPELL_RETURN) or self._overlay_image(e)):
                target, caster = e.parent_arg(6), e.parent_arg(8)
                if target is None or caster is None or e.parent_arg(0x12) == IMAGE_VANISH:
                    return []
                ours = (target < game.PARTY_SIZE) == (caster < game.PARTY_SIZE)
                return self.flush(now, force=True) + [
                    self._image_line(target, faces[0], 0 if ours else self.game.image_chance(target), spell=True)]
            if count == 1 and sides == 100 and e.parent_code.startswith(DISPEL_ROLL_RETURN):
                return self._dispel(e, faces[0])
            if count == 1 and sides == 20 and e.parent_code.startswith(DETONATE_ROLL_RETURN):
                return []  # (DET_ITEM's record shows it, with the item and the number)
            if count == 1 and sides == 20 and e.parent_code.startswith(ABJURE_ROLL_RETURN):
                return self._abjure(e, faces[0])
            if count == 1 and e.parent_code.startswith(SUMMON_ROLL_RETURN):
                return [f"    Summoning: 1d{sides} = {faces[0]} picks which of its {sides} creatures comes"]
            if e.parent_code.startswith(CHARGE_USED_RETURN) or self._overlay_charge(e, count, sides):
                who, eid = self._name(e.parent_arg(6)), e.parent_arg(8)
                if eid == ACID and count == 1:  # (DSCLOG's BURN_PASS: Sunstroke's heat; its line KIND_HEAT's)
                    return []
                if eid == ACID:
                    self._acid_burn = True  # (the damage's own duration roll after it means nothing)
                    return self.flush(now, force=True) + [
                        f"    {EFFECT_NAMES[ACID]} on {who}: {count}d{sides} = {faces_text} = {sum(faces)} acid damage"]
                # the 2d4 means nothing here: a Stoneskin, Ironskin, Mirror Image... used a charge
                owner = e.parent_arg(6)
                left = self._charges_after(owner, eid)
                spell = self._charge_spells.get((owner, eid))
                said = self.game.spell_name(spell) if spell is not None else EFFECT_NAMES.get(eid, f"effect {eid}")
                self._float(owner, f"{said}: {left} left" if left else f"{said} ends", labels.CHARGE_INK, now, priority=1)
                tail = f"{left} left" if left else "none left: it ends"
                if eid == game.MIRROR_EFFECT:
                    return [f"    {EFFECT_NAMES[eid]} on {who}: an image vanishes, {tail}"]
                name = EFFECT_NAMES.get(eid, f"effect {eid}")
                return [f"    {name} on {who}: one charge used, {tail}"]
            handler = next((bonus for code, bonus in SPELL_HANDLER_RETURNS if e.parent_code.startswith(code)), None)
            if handler is not None and e.parent_arg(0x0E) is not None:
                spell = e.parent_arg(0x0E)
                self._spell_cast(spell, now)
                total = sum(faces) + handler
                kit = ""
                caster = self.game.combatant_creature(e.parent_arg(8)) if e.parent_arg(8) is not None else None
                outdoors = caster is not None and self.game.outdoors(caster)
                kid = next((k for k in self.game.kit_ids(caster) if kits.cure_bonus(k, spell, outdoors)
                            or kits.cure_die(k, spell)), 0) if caster is not None else 0
                if kits.cure_bonus(kid, spell, outdoors):  # (DSCLOG's PROBE_CURE)
                    total += kits.cure_bonus(kid, spell, outdoors)
                    kit = f" {signed(kits.cure_bonus(kid, spell, outdoors))} {kits.name(kid)}"
                elif kits.cure_die(kid, spell):
                    kit = f" + 1d{kits.cure_die(kid, spell)} {kits.name(kid)} (the helper's roll)"
                return self.flush(now, force=True) + [
                    f"{self.game.spell_name(spell)}: {count}d{sides} = [" + " + ".join(map(str, faces)) + "]"
                    + (f" {signed(handler)}" if handler else "") + kit + (f" = {total}" if "1d" not in kit else "")]
            if e.parent_code.startswith(SPELL_DURATION_RETURN) or self._overlay_duration(e, count, sides):
                return self._spell_duration(e, count, sides, faces)
            if e.parent_code.startswith(SPELL_DAMAGE_RETURN):
                self._spell_cast(e.parent_arg(6), now)
                return self.flush(now, force=True) + [self._spell_damage(e, count, sides, faces)]
            steps = self._missile_steps(e, count, sides)
            if steps is not None:
                self._spell_cast(e.parent_arg(6), now)
                return self.flush(now, force=True) + [self._spell_damage(e, count, sides, faces, steps)]
            if sides > 1:  # the game sometimes "rolls" 1d1
                pending = PendingDice(f"{count}d{sides} = {faces_text} = {sum(faces)}", now,
                                      damage=e.parent_code.startswith(SPELL_DAMAGE_RETURN))
                target, spell = e.parent_arg(6), e.parent_arg(8)
                if count == 1 and sides == 100 and target is not None and game.cast_spell(spell) \
                        and self.game.combatant_creature(target) is not None:
                    pending.resistance = (target, spell, faces[0])
                self._pending.append(pending)
            return []
        g = self.game
        attacker, mode = e.parent_arg(0x0E), e.parent_arg(0x16)
        total = max(sum(faces) + bonus, 1)
        skill = self.weapon_skill(attacker, e.parent_arg(0x14))
        extra = specialize.damage(skill)
        kit_name, _, kit = self._kit_attack(attacker, e.parent_arg(0x14), mode, e.glob[0])
        steps = f"{count}d{sides} = {faces_text}" + (f" {signed(bonus - extra - kit)} weapon" if bonus - extra - kit else "") \
            + (f" {signed(extra)} {specialize.SKILL_NAMES[skill]}" if extra else "") \
            + (f" {signed(kit)} {kit_name}" if kit else "")
        if skill == specialize.GRAND:
            steps += f" (d{sides} for d{sides - 2}: grand mastery)"
        if sum(faces) + bonus < 1:
            steps += " (raised to the minimum of 1)"
        if mode is not None and mode <= 1:  # melee: the game adds the attacker's STR bonus
            strength = g.creature(attacker)[CREATURE_ABILITIES]
            str_bonus = g.str_damage(strength)
            if str_bonus:
                steps += f" {signed(str_bonus)} STR {strength}"
                total += str_bonus
            # Enlarge (DSUN 7C211h, with the STR bonus): +10% a level of the spell, the levels of
            # every Enlarge on the attacker added up (598:52h), 32-bit and rounded down
            level = self._enlarge_level(e.parent_arg(0x18))
            if level:
                percent = 100 + 10 * level
                total = total * percent // 100
                steps = f"({steps}) x{percent}% Enlarge (level {level})"
        # a backstab (a thief attacking from right behind, see the THAC0 line) multiplies all of
        # that on the attacker's first two attacks of the round: x2, x3 from thief level 5, x4 from
        # 9, x5 from 13; with RULE_BACKSTAB only the weapon's dice, the rest added once, and on the
        # first attack only (DSCLOG's STAB_TIMES). The attack's frame: [BP+1Eh] backstab, [BP+20h]
        # from behind, [BP-14h] the attacks already made this round
        backstab, rear, made = e.parent_arg(0x1E), e.parent_arg(0x20), e.parent_local(-0x14)
        most = 0 if self.rules & game.RULE_BACKSTAB else 1
        if backstab and rear and made is not None and made <= most:
            sheet = g.sheet(attacker)
            thief = [sheet[game.SHEET_LEVELS + i] for i in range(3) if sheet[game.SHEET_CLASSES + i] == THIEF]
            times = min(2 + (max(thief[0], 1) - 1) // 4, 5) if thief else 2
            if attacker < game.PARTY_SIZE:  # (an Assassin's one more: DSCLOG's STAB_TIMES)
                times = max(kits.backstab_times(k, times) for k in g.kit_ids(attacker) or [0])
            if self.rules & game.RULE_BACKSTAB:
                dice = sum(faces)
                more = (times - 1) * dice
                total += more
                steps += f" +{more} backstab (the dice {dice} x{times} = {dice * times})"
            else:
                total *= times
                steps = f"({steps}) x{times} backstab"
        target = g.combatant_creature(e.glob[0])
        if target is not None:  # so the HP it takes isn't put down to a spell being cast
            self._hit(target, total, now)
        line = f"{g.creature_name(attacker)} hits {g.combatant_name(e.glob[0])} for {total}: {steps}"
        return ["  " + line]

    def _enlarge_level(self, combatant: Optional[int]) -> int:
        """The level Enlarge counts at on COMBATANT: each Enlarge on them at its caster's level
        (as Dispel Magic weighs it), added up; 0 without one."""
        if combatant is None:
            return 0
        g = self.game
        level = 0
        for effect, spell in g.effect_spells():
            if effect.owner == combatant and effect.id == game.ENLARGE_EFFECT:
                caster = g.combatant_creature(effect.caster)
                level += (g.effect_caster_level(caster, spell) if caster is not None else None) or 0
        return level

    def _overlay_image(self, e: Entry) -> bool:
        """Mirror Images' d100 on a spell (IMAGE_SPELL_RETURN) when the overlay manager has
        swapped its return address for an INT 3Fh stub (the dice routine's overlay loaded over
        the spell's): known by the routine's arguments, (target, caster, ..., spell at +12h), a
        spell cast on a target with Mirror Images on it."""
        if not e.parent_code.startswith(OVERLAY_TRAP):
            return False
        target, caster, spell = e.parent_arg(6), e.parent_arg(8), e.parent_arg(0x12)
        if target is None or caster is None or spell is None or not 0 <= spell < 0x100:
            return False
        return any(eff.owner == target and eff.id == game.MIRROR_EFFECT for eff in self.game.effects())

    def _overlay_duration(self, e: Entry, count: int, sides: int) -> bool:
        """The duration routine's roll when the overlay manager has swapped its return address
        for an INT 3Fh stub (so its code can't be matched): its arguments are still (spell,
        caster level), and the dice are the spell record's duration dice."""
        if not e.parent_code.startswith(OVERLAY_TRAP):
            return False
        spell, level = e.parent_arg(6), e.parent_arg(8)
        if spell is None or level is None or not game.cast_spell(spell) or not 1 <= level <= 40:
            return False
        rec = self.game.spell_record(spell)
        return len(rec) > 4 and (rec[4] & 0x0F, rec[4] >> 4) == (count, sides)

    def _spell_duration(self, e: Entry, count: int, sides: int, faces: List[int]) -> List[str]:
        g = self.game
        spell, level = e.parent_arg(6), (e.parent_arg(8) or 0) & 0xFF
        if spell is None:
            return []
        if spell == game.SUNSTROKE_SPELL and self._sun_burn:
            self._sun_burn = False  # (Sunstroke's heat: the same)
            return []
        dice = f"{count}d{sides}" + (f" = [{' + '.join(map(str, faces))}]" if sides > 1 else "")
        rec = g.spell_record(spell)
        acid = len(rec) > 0x19 and rec[0x19] == ACID
        if acid and self._acid_burn:
            self._acid_burn = False  # (a round's burn: the damage rolls the time it puts on no more)
            return []
        found = g.spell_duration(spell, level, sum(faces))
        if found is not None:
            units, how = found
            if acid:
                rounds = min(max(-(-units // ROUND_SECONDS), 1), 0x7F)
                return [f"    {g.spell_name(spell)} burns {rounds} round{'' if rounds == 1 else 's'} more, "
                        f"2d4 at the start of each ({game.game_time(units)}: caster level {level}: {how}; "
                        f"dice {dice})"]
            return [f"    {g.spell_name(spell)} lasts {game.game_time(units)} (caster level {level}: {how}; "
                    f"dice {dice})"]
        charges = g.spell_charges(spell, level, sum(faces))
        if charges is not None:  # lasts until used up (blows taken, images struck...)
            count, how = charges
            return [f"    {g.spell_name(spell)} has {count} charge{'' if count == 1 else 's'} "
                    f"(caster level {level}: {how}; dice {dice})"]
        return []  # permanent until removed

    def _missile_steps(self, e: Entry, count: int, sides: int) -> Optional[int]:
        """Magic Missile, Flame Arrow, Minute Meteors: their damage is rolled by another routine,
        whose return address the overlay manager has taken, but the dice routine's own
        arguments name the spell (as does its caller's first). The steps of caster level the
        roll stands for, when the dice fit the spell's formula; else None."""
        if not e.parent_code.startswith(OVERLAY_TRAP):
            return None
        spell = e.arg(0x0C)
        if spell is None or spell != e.parent_arg(6) or not game.cast_spell(spell):
            return None
        rule = self.game.spell_damage(spell)
        if rule is None or rule.sides != sides or sides < 2:
            return None
        if not rule.step_dice:  # fixed dice (Slay Living's 4d8)
            return 0 if count == rule.base_dice else None
        steps, extra = divmod(count - rule.base_dice, rule.step_dice)
        return steps if steps >= 1 and not extra else None

    def _harm_bonus(self, spell: Optional[int]) -> int:
        """A kit's damage added to SPELL, as DSCLOG's AV_CAUSE has it: a Wilderness Avenger's
        Cause Wounds, when its caster (the last spell cast, KIND_CAST) is one."""
        who, cast = self._cast
        if spell is None or spell != cast or who is None or spell not in kits.CAUSE_DICE:
            return 0
        creature = self.game.combatant_creature(who)
        if creature is None or kits.AVENGER not in self.game.kit_ids(creature):
            return 0
        return kits.harm_bonus(kits.AVENGER, spell)

    def _spell_damage(self, e: Entry, count: int, sides: int, faces: List[int],
                      missile_steps: Optional[int] = None) -> str:
        """A spell's damage dice, rolled by the routine whose arguments are (spell, caster level):
        the game adds a flat bonus for each step of caster level."""
        g = self.game
        spell, level = e.parent_arg(6), (e.parent_arg(8) or 0) & 0xFF
        name = g.spell_name(spell) if spell is not None else "Spell"
        if spell == game.HARM_SPELL:  # (DSCLOG's HARM_SITE puts its own in the roll's place)
            self._last_damage = None
            return f"{name}: all the target's hit points but 1d4 (the {count}d{sides} the game rolls goes unused)"
        text = f"{name} damage: {count}d{sides} = [" + " + ".join(map(str, faces)) + "]"
        rule = g.spell_damage(spell) if spell is not None else None
        kit, kit_text = self._harm_bonus(spell), ""  # (DSCLOG's AV_CAUSE)
        if kit:
            kit_text = f" {signed(kit)} {kits.name(kits.AVENGER)}"
        self._last_damage = (spell, sum(faces) + kit)
        self._recent_damage.append(self._last_damage)
        if rule is None or rule.sides != sides:
            return f"{text}{kit_text} = {sum(faces) + kit}"
        steps = rule.steps(level) if missile_steps is None else missile_steps
        bonus = rule.step_bonus * steps
        self._last_damage = (spell, sum(faces) + bonus + kit)
        self._recent_damage[-1] = self._last_damage
        if bonus:
            text += f" {signed(bonus)}"
        text += f"{kit_text} = {sum(faces) + bonus + kit}"
        per = (f"{rule.step_dice}d{sides}" if rule.step_dice else "") + \
            (f"{signed(rule.step_bonus)}" if rule.step_dice and rule.step_bonus else
             f"{rule.step_bonus}" if rule.step_bonus else "")
        if not per or rule.flat():
            return text
        unit = "caster level" if rule.per_levels == 1 else f"{rule.per_levels} caster levels"
        counted = min(level, game.SPELL_LEVEL_CAP) + rule.adjust
        how = f"{per} for each {unit}"
        if rule.adjust:
            how += f" (counting {signed(rule.adjust)})"
        base = f"{rule.base_dice}d{sides} + " if rule.base_dice else ""
        if missile_steps is not None:  # the caster's level isn't in this routine's arguments
            return f"{text} ({base}{how}, counted up to level {game.SPELL_LEVEL_CAP}: {steps})"
        cap = f", which counts as {game.SPELL_LEVEL_CAP}" if level > game.SPELL_LEVEL_CAP else ""
        return f"{text} ({base}{how}: {steps} at caster level {level}{cap})" if counted >= 0 else text

    # weapons breaking and levels ------------------------------------------------------

    def _script_roll(self, e: Entry, show_all: bool) -> List[str]:
        """A script's random command: a junk, haystack or wardrobe search or its damage
        (searches.py); any other only with "Show unlabelled rolls"."""
        result, most = e.raw & 0xFF, e.raw >> 8 & 0xFF
        counts = tuple(e.arg(at) for at in searches.COUNTS_AT)
        lines = searches.describe(result, most, e.extra, counts)
        if not lines and e.extra == bowyer.POSITION and most == bowyer.MOST:
            lines = self._archery(result)
        if not lines:
            lines = self._script_check(result, most, e.extra)
        if not lines and show_all:
            lines = [f"Script roll: 0-{most} = {result} (script position {e.extra})"]
        return lines

    def _archery(self, roll: int) -> List[str]:
        """A shot at the Bowyer's archery target (bowyer.py): the archer is the one whose turn it
        is (outside a fight, the party's leader), the distances the game's, from where they stand."""
        turn = self.game.whose_turn()
        index = self.game.combatant_creature(turn) if turn is not None else None
        if index is None:
            return []
        here = self.game.thing_square(turn)

        def nearest(obj: int) -> Optional[int]:
            found = [bowyer.distance(*here, *self.game.thing_square(t)) for t in self.game.things_of(obj)]
            return min(found) if found else None
        target = nearest(bowyer.TARGET)
        if target is None:
            return []
        dex = self.game.creature(index)[CREATURE_ABILITIES + 1]
        return bowyer.describe(roll, dex, target, nearest(bowyer.BOWYER), self.game.flag(bowyer.REWARD_FLAG),
                               self.game.creature_name(index))

    def _script_check(self, result: int, most: int, position: int) -> List[str]:
        """A random command a script compares with an ability of the character acting
        (scriptchecks.py): Chahl's CHA, the chains' STR... The character acting is the one whose
        turn it is (outside a fight, the party's leader)."""
        check = scriptchecks.load(self.script_file).get(position)
        if check is None or check.most != most:
            return []
        turn = self.game.whose_turn()
        index = self.game.combatant_creature(turn) if turn is not None else None
        if index is None:
            return []
        score = self.game.creature(index)[CREATURE_ABILITIES + check.ability]
        return scriptchecks.describe(check, result, score, self.game.creature_name(index))

    def _request(self, e: Entry, show_all: bool) -> List[str]:
        """A script's REQUEST (DSCLOG's REQ_SITE), named; the everyday ones only with "Show
        unlabelled rolls"."""
        number = e.raw & 0xFFFF
        if number in spellarrows.REST_REQUESTS:
            self._rest_due = True  # (the spell arrows fade)
        if number not in REQUESTS_SHOWN and not show_all:
            return []
        name = REQUEST_NAMES.get(number, "an unknown request")
        values = ", ".join(str(v) for v in (e.arg(8), e.arg(0x0A), e.arg(0x0C)) if v is not None)
        return [f"Script: {name} (request {number}: {values})"]

    def _wall(self, e: Entry, now: float) -> List[str]:
        """Wall of Thorns' damage (DSCLOG's THORNS_DAMAGE): the game rolled its record's dice (the
        line before), 8 + the creature's AC taken instead."""
        damage, spell = e.raw & 0xFF, e.raw >> 8 & 0xFF
        name = self.game.spell_name(spell)
        self._spell_cast(spell, now)
        self._last_damage = (spell, damage)
        self._recent_damage.append(self._last_damage)
        whose = f"{name}'" if name.endswith("s") else f"{name}'s"
        ac = (e.extra >> 8 & 0xFF) - 0x80
        low = " (at least 1)" if THORNS_BASE + ac < 1 else ""
        return [f"  {whose} wall instead: {THORNS_BASE} + AC {ac} = {damage}{low}"]

    def _heat(self, e: Entry, now: float) -> List[str]:
        """Sunstroke's heat at a round's start on a creature it holds (DSCLOG's BURN_PASS, HEAT_SITE):
        1d4 of fire. The roll's own line, if its caller was hidden (left pending), is dropped."""
        damage, spell = e.raw & 0xFF, e.raw >> 8 & 0xFF
        rolled = f"1d4 = [{damage}] = {damage}"
        for p in self._pending:
            if p.text == rolled:
                self._pending.remove(p)
                break
        self._spell_cast(spell, now)
        self._last_damage = (spell, damage)
        self._recent_damage.append(self._last_damage)
        self._sun_burn = True  # (the damage's own duration roll after it means nothing)
        return [f"    Sunstroke's heat on {self._name(e.extra)}: 1d4 = {damage} fire damage"]

    def _aim(self, e: Entry) -> List[str]:
        """A spell cast with a click that the game refused (DSCLOG's AIM_SITE), and why: the game
        itself only shows the crossed-out pointer."""
        answer = struct.unpack("b", bytes([e.raw & 0xFF]))[0]
        spell = e.raw >> 8 & 0xFF
        why = AIM_REASONS.get(answer, f"refused ({answer})")
        return [f"{self._name(e.extra)} can't cast {self.game.spell_name(spell)} there: {why}"]

    def _item_check(self, e: Entry) -> List[str]:
        """An item the acid or corroding touch could destroy, after a failed save (DSCLOG's
        PROBE_ITEM_*): the d20, the number it needed and whose number that was."""
        roll, needed = e.raw & 0xFF, struct.unpack("b", bytes([e.raw >> 8 & 0xFF]))[0]
        if e.extra & ITEM_DETONATE and not e.extra & ITEM_ARMOUR:
            return self._detonate_item(e, e.extra & 0x3FFF, roll, needed)
        item, armour = e.extra & 0x7FFF, bool(e.extra & ITEM_ARMOUR)
        g = self.game
        save = g.item_save(item, armour)
        target, attacker, attack = e.arg(6), e.parent_arg(8), e.parent_arg(0x0E)
        who = self._name(target) if target is not None else "someone"
        by = game.ITEM_ATTACKS.get(attack, "acid")
        source = self._name(attacker) if attacker is not None else ""
        by = f"{source}'s {by}" if source else by.capitalize()
        name = save.name if save else ("armour" if armour else "weapon")
        head = f"  {by} on {who}'s {name}"
        if not roll:
            return [f"{head}: no magical power, destroyed without a roll (the game's rule) -> CORRODED"]
        corroded = roll < needed
        why = ""
        if save:
            own = "destroyed without a roll" if save.own is None else (
                f"{save.own}" if save.own > 1 else "safe whatever the roll")
            base = save.adnd + save.plus + (1 if save.power else 0)
            adnd = f"{base} for {save.material}"
            if save.plus:
                adnd += f", {signed(-save.plus)} for its plus"
            if save.power:
                adnd += ", -1 for its power"
            if save.adnd != base:
                adnd = f"{save.adnd} ({adnd})"
            if g.rules & game.RULE_ITEM_SAVES:
                if save.own is not None and needed == save.own and save.own <= save.adnd:
                    why = f" (the game's; AD&D's: {adnd})"
                else:
                    why = f" (AD&D's, {adnd}; the game's: {own})"
            else:
                why = " (the game's)"
        need = f"needs {needed}" if needed > 1 else "safe whatever the roll"
        return [f"{head}: d20 = {roll}, {need}{why} -> {'CORRODED' if corroded else 'safe'}"]

    def _detonate_item(self, e: Entry, item: int, roll: int, needed: int) -> List[str]:
        """Detonate's blast on the target's worn item that breaks most easily (the lowest item
        +10h, under 6): a d20 under 15 less its plus, or it's gone (one of a stack)."""
        who = self._name(e.arg(6)) if e.arg(6) is not None else "someone"
        rec = self.game.item_record(item)
        name = self.game.item_label(rec, self.game.item_type_record(rec)) if len(rec) == game.ITEM_SIZE else "item"
        plus = 15 - needed
        why = f"15 {signed(-plus)} for its plus" if plus else "15"
        gone = roll < needed
        return [f"  Detonate's blast on {who}'s {name}: d20 = {roll}, breaks it under {needed} ({why}) -> "
                + ("DESTROYED" if gone else "safe")]

    def _break_check(self, e: Entry, first: bool, show_all: bool) -> List[str]:
        """After an attack the game checks the weapon: non-magical wood, bone, stone and
        obsidian break when a 0-7 roll and then a 0-19 roll both come up 0 (1 in 160)."""
        item, item_type = e.arg(6), e.arg(8)
        weapon = self.game.weapon(item, item_type)
        name = self.game.weapon_name(weapon) if weapon else "weapon"
        who = f"{self._last_attacker}'s " if self._last_attacker else ""
        if not self.game.item_breaks(item, item_type):
            return [f"    {who}{name} can't break"] if show_all and first else []
        if first:
            self._break_first = scaled(e.raw, 8)
            if self._break_first == 0 or show_all:
                return []  # wait for the second roll (there is one only if this was 0)
            return []
        second, first_roll, self._break_first = scaled(e.raw, 20), self._break_first, None
        if second == 0:
            return [f"    {who}{name} BREAKS: 0 on 0-7 and 0 on 0-19 (1 in 160 after each hit)"]
        return [f"    {who}{name} nearly broke: {first_roll if first_roll is not None else 0} on 0-7, "
                f"then {second} on 0-19 (needed 0)"]

    def _hp_rolls(self, key: tuple, roll: int) -> Optional[Tuple[int, ...]]:
        """A hit die's rolls: just ROLL, or with RULE_HP_BEST (DSCLOG's PROBE_HP_BEST: the game rolls
        it twice) None for the first of the two (kept by KEY: who, class, level), then both."""
        if not self.game.rules & game.RULE_HP_BEST:
            return (roll,)
        if self._hp_first is not None and self._hp_first[0] == key:
            first, self._hp_first = self._hp_first[1], None
            return first, roll
        self._hp_first = (key, roll)
        return None

    def _kit(self, sheet: bytes) -> int:
        """A sheet's kit for its hit dice (kitpages.kit_at), with kits on; else 0. A human who has
        changed class rolls for its new class, not the kit's (DSCLOG's PROBE_HIT_DIE)."""
        if not self.game.rules & game.RULE_KITS or len(sheet) < game.SHEET_SIZE or sheet[0x22]:
            return 0
        from . import kitpages
        return kitpages.kit_at(sheet, 0)

    def _level_hp(self, e: Entry, sides: int, roll: int) -> Optional[List[str]]:
        """The hit point roll of a new level: the caller's arguments are (party member, class, level).
        None if it isn't one."""
        member, cls, level = e.parent_arg(6), e.parent_arg(8), e.parent_arg(0x0A)
        if member is None or not 0 <= member < game.PARTY_SIZE or cls is None or level is None:
            return None
        sheet = self.game.sheet(member)
        if len(sheet) < game.SHEET_SIZE:
            return None
        slots = [i for i in range(3) if sheet[game.SHEET_CLASSES + i] == cls]
        if not slots or sheet[game.SHEET_LEVELS + slots[0]] != level:
            return None
        rule = self.game.level_hp_rule(cls)
        if rule is None or kits.hit_die(self._kit(sheet), rule.sides) != sides:
            return None
        rolls = self._hp_rolls(("level", member, cls, level), roll)
        if rolls is None:
            return []  # (the first of two: the line comes with the second)
        roll = max(rolls)
        con = sheet[game.SHEET_ABILITIES + 2]
        text = f"d{sides} = {roll}" if len(rolls) == 1 else f"d{sides} = {rolls[0]} and {rolls[1]}, the better {roll}"
        gained = roll
        minimum = self.game.level_hp_minimum(con)
        if minimum > roll:
            gained = minimum
            text += f", raised to {minimum} for CON {con}"
        if sheet[game.SHEET_RACE] == game.RACE_HALF_GIANT:
            gained *= 2
            text += f", doubled for a half-giant = {gained}"
        classes = game.class_share(sheet)
        if self.game.rules & game.RULE_MULTI_HP and classes > 1:  # (DSCLOG's CON_SHARE)
            per = self.game.con_per_die(sheet, con)
            text += f", {signed(per)} CON {con}, into the total shared by {classes} classes"
        cls_name = game.CLASS_NAMES.get(cls, f"class {cls}")
        return [f"{self.game.creature_name(member)}'s {game.ordinal(level)} {cls_name} level: hit points {text}"]

    # character creation ----------------------------------------------------------------

    def _creation_ability(self, e: Entry, roll: int, now: float = 0.0) -> List[str]:
        """One of the four 4d4 rolls for an ability; the line comes with the fourth."""
        ability, class_count = e.parent_arg(8), e.parent_arg(0x0E)
        if self._ability_of != ability:  # a new ability (or rolls went missing)
            self._ability_of, self._ability_tries = ability, []
        self._ability_tries.append(roll)
        if len(self._ability_tries) < CREATION_ABILITY_TRIES:
            return []
        tries, self._ability_tries, self._ability_of = self._ability_tries, [], None
        # (the die rolls a whole character again and again while it tumbles: a set begun anew, or
        # one whose hit points have come, gives way to the next; the last is logged when it stops)
        if self._creation_hp or (ability is not None and any(a >= ability for a in self._creation_abilities)):
            self._creation_hp, self._creation_abilities = [], {}
        self._creation_hp_at = now
        out: List[str] = []
        if ability is None or not 0 <= ability < 6:
            return out + [f"Character creation: 4d4 four times: {', '.join(map(str, tries))}"]
        sheet = self.game.creation_sheet()
        classes = [sheet[game.SHEET_CLASSES + i] for i in range(min(max(class_count or 1, 1), 3))]
        value, line = self._ability_line(ability, tries, sheet, classes)
        if ability == 2:
            self._creation_con = value
        self._creation_abilities[ability] = (value, line)
        return out

    def _ability_line(self, ability: int, tries: List[int], sheet: bytes, classes: List[int]) -> Tuple[int, str]:
        """An ability rolled at creation: the best of its four 4d4 + 4, the race's adjustment, raised to
        the classes' least; (the value, its line)."""
        g = self.game
        race = sheet[game.SHEET_RACE]
        adjustment = g.race_adjustment(race, ability)
        best = max(tries)
        steps = f"best of four 4d4 ({', '.join(map(str, tries))}) = {best}, +4"
        value = best + 4 + adjustment
        if adjustment:
            steps += f", {signed(adjustment)} {game.RACE_NAMES.get(race, f'race {race}')}"
        steps += f" = {value}"
        minimums = [(g.class_minimum(c, ability), c) for c in classes if c]
        if minimums:
            least, cls = max(minimums)
            if value < least:
                name = game.CREATION_CLASS_NAMES.get(cls, f"class {cls}")
                why = "prime requisite" if least == game.CREATION_PRIME_MINIMUM else "least"
                steps += f", raised to {least} (the {name}'s {why})"
                value = least
        return value, f"Character creation, {ABILITIES[ability]} {value}: {steps}"

    def _creation_tries_moved(self, now: float) -> None:
        """DSCLOG's count of creation 4d4s (RL_TRY): moved since the last look, the die has rolled;
        the lines come once it has been still for CREATION_HP_WAIT."""
        if self.tsr_hdr is None:
            return
        try:
            seq, = struct.unpack("<H", self.guest.read(self.tsr_hdr + TSR_TRIES_SEQ, 2))
        except (struct.error, IndexError, ValueError):
            return
        if self._tries_seq is not None and seq != self._tries_seq:
            self._tries_new, self._creation_hp_at, self._tries_at = True, now, now
        self._tries_seq = seq

    def _creation_tries(self) -> Optional[List[List[int]]]:
        """The last four 4d4 of each ability, STR to CHA, as DSCLOG kept them (None if it can't be read)."""
        if self.tsr_hdr is None:
            return None
        try:
            raw = self.guest.read(self.tsr_hdr + TSR_TRIES, 24)
        except (IndexError, ValueError):
            return None
        if len(raw) < 24 or not all(4 <= b <= 16 for b in raw):
            return None
        return [list(raw[i * 4:i * 4 + 4]) for i in range(6)]

    def _creation_hp_roll(self, e: Entry, sides: int, roll: int, now: float) -> List[str]:
        """A class level's hit point die on the creation screen: (sheet, class, level)."""
        index, cls, level = e.parent_arg(6), e.parent_arg(8), e.parent_arg(0x0A)
        sheet = self.game.sheet_at(index) if index is not None and index >= 0 else b""
        rolls = self._hp_rolls(("creation", index, cls, level), roll)
        if rolls is None:
            return []  # (the first of two)
        roll = max(rolls)
        best = "" if len(rolls) == 1 else f" (the better of {rolls[0]} and {rolls[1]})"
        if len(sheet) < game.SHEET_SIZE or cls is None:
            return [f"Character creation: hit points d{sides} = {roll}{best}"]
        text, gained = f"{roll}{best}", roll
        con = sheet[game.SHEET_ABILITIES + 2]
        minimum = self.game.level_hp_minimum(con)
        if minimum > roll:
            text, gained = f"{roll}{best} (raised to {minimum} for CON {con})", minimum
        if sheet[game.SHEET_RACE] == game.RACE_HALF_GIANT:
            gained *= 2
        if any(r[1] == cls and r[4] == level for r in self._creation_hp):
            self._creation_hp = []  # (rolled again: a new set, the last one given way)
        self._creation_hp.append((index, cls, gained, text, level))
        self._creation_hp_at = now
        return []

    def creation_lines(self) -> List[str]:
        """The character the die stopped on: its abilities as rolled, each checked against the one
        the game shows (rolls that came too fast to record leave only the game's), and its hit
        points."""
        got, self._creation_abilities = self._creation_abilities, {}
        shown = self.game.creation_abilities()
        tries = self._creation_tries() if self._tries_new else None
        self._tries_new = False
        out = []
        if tries is not None:  # (DSCLOG's: every roll, however fast the die tumbled)
            sheet = self.game.creation_sheet()
            classes = list(sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3])
            for ability in range(6):
                value, line = self._ability_line(ability, tries[ability], sheet, classes)
                if shown is None or value == shown[ability]:
                    got[ability] = (value, line)
        if got:
            for ability in range(6):
                line = got.get(ability)
                if shown is not None and (line is None or line[0] != shown[ability]):
                    out.append(f"Character creation, {ABILITIES[ability]} {shown[ability]} "
                               f"(its rolls came too fast to record)")
                    if ability == 2:
                        self._creation_con = shown[ability]
                elif line is not None:
                    out.append(line[1])
            if shown is not None:  # (what game.RULE_ROLLED lets the six add up to)
                out.append(f"Character creation: the six scores add up to {sum(shown)}")
        if shown is not None:
            self._creation_con = shown[2]
        return out + self.creation_hp_lines()

    def creation_hp_lines(self) -> List[str]:
        """The new character's hit points, from the rolls collected. The game adds them up,
        divides by the number of classes (a dual-classed human counts one) and adds CON's
        bonus for each level that rolled: the full bonus for warriors, at most +2 for others."""
        rolls, self._creation_hp = self._creation_hp, []
        if not rolls:
            return []
        g = self.game
        index = rolls[-1][0]
        sheet = g.sheet_at(index)
        by_class: Dict[int, List[str]] = {}
        for _, cls, _, text, _ in rolls:
            by_class.setdefault(cls, []).append(text)
        parts = []
        for cls, texts in by_class.items():
            rule = g.level_hp_rule(cls)
            die = f" d{kits.hit_die(self._kit(sheet), rule.sides)}" if rule else ""
            parts.append(f"{game.CLASS_NAMES.get(cls, f'class {cls}')}{die} per level: {' + '.join(texts)}")
        rolled = sum(r[2] for r in rolls)
        steps = "; ".join(parts)
        if len(sheet) < game.SHEET_SIZE:
            return [f"Character creation, hit points: {steps} = {rolled}"]
        if sheet[game.SHEET_RACE] == game.RACE_HALF_GIANT:
            steps = f"({steps}) x2 half-giant"
        steps += f" = {rolled}"
        classes = game.class_share(sheet)
        multi = bool(g.rules & game.RULE_MULTI_HP) and classes > 1
        con = self._creation_con if self._creation_con is not None \
            else g.creature(index)[CREATURE_ABILITIES + 2]
        levels = {}
        for _, cls, _, _, _ in rolls:
            levels[cls] = levels.get(cls, 0) + 1
        if multi:  # (RULE_MULTI_HP, DSCLOG's CON_SHARE: CON's bonus on each die, then the total shared)
            per = g.con_per_die(sheet, con)
            total = rolled + per * len(rolls)
            hp = int(total / classes)
            if per:
                steps += f", {signed(per)} CON {con} on each of {len(rolls)} dice = {total}"
            steps += f", / {classes} classes = {hp}" + (" (rounded down)" if total % classes else "")
        else:
            hp = rolled // classes
            if classes > 1:
                steps += f", / {classes} classes = {hp}" + (" (rounded down)" if rolled % classes else "")
            # CON's bonus counts levels that roll dice: a warrior's (group 1) at the full bonus, and
            # the rest of the highest class's up to +2
            bonus_per_level = g.level_hp_con_bonus(con)
            warrior = max((n for c, n in levels.items() if g.level_hp_group(c) == game.WARRIOR_GROUP), default=0)
            highest = max(levels.values())
            bonus = bonus_per_level * warrior + min(bonus_per_level, 2) * (highest - warrior)
            if bonus:
                hp += bonus
                steps += f", {signed(bonus)} CON {con} = {hp}"
        least = sum(levels.values())
        if hp < least:
            hp = least
            steps += f", raised to {least} (at least 1 per level)"
        shown = struct.unpack_from("<h", g.creation_sheet(), game.SHEET_MAX_HP)[0] \
            if len(g.creation_sheet()) >= game.SHEET_SIZE else 0
        if shown > 0 and shown != hp:  # (rolls missed: the game's own)
            return [f"Character creation, hit points {shown} (some of its rolls came too fast to record; "
                    f"those caught: {steps})"]
        return [f"Character creation, hit points {hp}: {steps}"]

    # saving throws -------------------------------------------------------------------

    def _is_save_roll(self, e: Entry) -> bool:
        """The dice routine's caller is the saving throw if its frame holds a far pointer to
        the target's creature record at [BP-1Eh] (set just before it rolls)."""
        target = e.parent_arg(6)
        index = self.game.combatant_creature(target) if target is not None else None
        off, seg = e.parent_local(-0x1E), e.parent_local(-0x1C)
        if index is None or off is None or seg is None:
            return False
        table = game.far_pointer(self.guest, self.game.ds, game.CREATURES_PTR)
        return (seg & 0xFFFF) * 16 + (off & 0xFFFF) == table + index * game.CREATURE_SIZE

    def _range_roll(self, e: Entry) -> Optional[List[str]]:
        """A number from LOW to HIGH (the game's 1A0A:2FA9h, arguments low, high): the psionic
        power check's d20s; None for one the log doesn't know."""
        low, high = e.arg(6), e.arg(8)
        if low is None or high is None or high < low:
            return None
        roll = low + scaled(e.raw, high - low + 1)
        if e.parent_code.startswith(DEFENCE_FIRST_RETURN) or e.parent_code.startswith(DEFENCE_SECOND_RETURN):
            return self._psionic_defence(e, roll, high, e.parent_code.startswith(DEFENCE_SECOND_RETURN))
        if (low, high) != (1, 20):
            return None
        if e.parent_code.startswith(POWER_CHECK_RETURN):
            return self._power_check(e, roll)
        if e.parent_code.startswith(STATIC_FIRST_RETURN):
            self._static_rolls[(e.ss, e.parent_bp)] = roll
            return []
        if e.parent_code.startswith(STATIC_SECOND_RETURN):
            return self._static_check(e, roll)
        return None

    def _power_check(self, e: Entry, roll: int) -> List[str]:
        """A psionic power's check: a d20 at or under the power's score, a 1 always and a 20
        never; the score is the ability the power uses (as the game reads it now) + the power's
        adjustment + the user's own for it (the game keeps one a power, 1 and up, from 1) - 1 +
        the call's bonus (none so far)."""
        who, power, bonus = e.parent_arg(6), e.parent_arg(8), e.parent_arg(0x0A) or 0
        if who is None or power is None:
            return []
        score = struct.unpack("<b", e.parent_locals[0x28 - 2:0x28 - 1])[0]
        works = roll != 20 and (roll <= score or roll == 1)
        name = self.game.spell_name(game.PSIONIC_FIRST + power)
        head = f"{self._name(who)} uses {name}: power check d20 = {roll}, needs {score} or less"
        if roll in (1, 20):
            head += f" (a {roll} always {'works' if roll == 1 else 'fails'})"
        out = [f"{head} -> {'it works' if works else 'it fails'}"]
        parts = self.game.power_score_parts(who, power)
        if parts is not None:
            ability, adjustment, own = parts
            level = score - adjustment - own - bonus
            steps = [f"{level} {ability}", f"{signed(adjustment)} {name}"]
            if own:
                steps.append(f"{signed(own)} practised")
            if bonus:
                steps.append(f"{signed(bonus)} this use")
            out.append(f"    power score {score} = " + " ".join(steps).replace(" +", " + ").replace(" -", " - "))
        return out

    def _psionic_defence(self, e: Entry, roll: int, defence: int, second: bool) -> List[str]:
        """A psionic attack mode's target resists with two rolls of 1 to its defence (the better of
        WIS - 7, a raised defence mode's, a monster's level; at least 1), each over the attacker's
        power check d20: the first, then the second only if the first is over it."""
        attack, who = e.arg(0x0A), e.parent_arg(6)
        if attack is None:
            return []
        name = self._name(who) if who is not None else "the target"
        head = f"  {name}'s psionic defence: d{defence} = "
        need = f"over {attack} (the attacker's power check d20)"
        key = (e.ss, e.parent_bp)
        if not second:
            if roll > attack:
                self._defence_rolls[key] = roll
                return []
            return [f"{head}{roll}, needs {need} -> not resisted"]
        first = self._defence_rolls.pop(key, None)
        rolls = f"{first} and {roll}" if first is not None else f"... and {roll}"
        return [f"{head}{rolls}, both need {need} -> {'resisted' if roll > attack else 'not resisted'}"]

    def _static_check(self, e: Entry, second: int) -> List[str]:
        """Someone else's Synaptic Static against a power: the user's d20 (the first) over its
        number ([BP-8]: the game means the power's score, but its ability is read and dropped, so
        it is the user's own number for the power, 1 for a monster) disrupts it; else the Static's
        keeper ([BP-4]) rolls at or under its own Static score ([BP-6]) and no lower than the first
        to disrupt it. Otherwise the power check follows."""
        first = self._static_rolls.pop((e.ss, e.parent_bp), None)
        who, power = e.parent_arg(6), e.parent_arg(8)
        keeper, against, holds = e.parent_local(-4), e.parent_local(-6), e.parent_local(-8)
        if first is None or who is None or power is None or None in (keeper, against, holds):
            return []
        disrupted = first > holds or (second <= against and second >= first)
        name = self.game.spell_name(game.PSIONIC_FIRST + power)
        return [f"{self._name(who)} uses {name} within {self._name(keeper)}'s Synaptic Static: "
                f"d20 = {first} against {holds}, {self._name(keeper)}'s d20 = {second} against {against} "
                f"(and at least {first}) -> {'disrupted by the static' if disrupted else 'not disrupted: the power check follows'}"]

    def _save_roll(self, e: Entry, now: float = 0.0) -> List[str]:
        """The d20 of a saving throw. A natural 1 or 20 ends the save here; otherwise the
        save probe reports the total."""
        natural = scaled(e.raw, 20) + 1
        spell, target, caster = e.parent_arg(0x0A), e.parent_arg(6), e.parent_arg(8)
        self._spell_cast(spell, now)
        needed = e.parent_locals[0x28 - 1]
        index = e.parent_local(-6)
        pending = self._flush_spell(spell)
        if natural in (1, 20):
            return pending + [self._save_line(target, caster, spell, index, natural, None, needed)]
        self._save_rolls[(e.ss, e.parent_bp)] = natural
        return pending

    def _save(self, e: Entry) -> List[str]:
        total, needed = e.raw & 0xFF, e.raw >> 8
        natural = self._save_rolls.pop((e.ss, e.bp), None)
        spell, target, caster = e.arg(0x0A), e.arg(6), e.arg(8)
        return self._flush_spell(spell) + [
            self._save_line(target, caster, spell, e.local(-6), natural, total, needed)]

    def _dispel(self, e: Entry, roll: int) -> List[str]:
        """One effect's chance against Dispel Magic."""
        g = self.game
        target, level, eid = e.parent_arg(6), (e.parent_arg(0x14) or 0) & 0xFF, e.parent_local(-2)
        if target is None or eid is None:
            return []
        name = EFFECT_NAMES.get(eid, f"effect {eid}")
        # the game weighs every effect of that kind on the target (usually one): each effect's level
        levels = []
        for effect, spell in g.effect_spells():
            if effect.owner == target and effect.id == eid:
                caster = g.combatant_creature(effect.caster)
                found = g.effect_caster_level(caster, spell) if caster is not None else None
                levels.append(found or 0)
        chance = 50 + 5 * level - 5 * sum(levels)
        against = f" - 5 x {sum(levels)} (its caster's level)" if levels else ""
        return [f"    Dispel Magic on {self._name(target)}'s {name}: d100 = {roll}, needs {chance} or less "
                f"(50 + 5 x {level}{against}) -> {'dispelled' if roll <= chance else 'stays'}"]

    def _abjure(self, e: Entry, roll: int) -> List[str]:
        g = self.game
        target, level = e.parent_arg(6), (e.parent_arg(0x14) or 0) & 0xFF
        creature = g.combatant_creature(target) if target is not None else None
        sheet = g.sheet(creature) if creature is not None else b""
        if len(sheet) < game.SHEET_SIZE:
            return [f"    Abjure: d20 = {roll}"]
        their = sheet[game.SHEET_LEVELS]
        need = 11 - level + their
        kind = sheet[game.SHEET_RACE]
        works = roll >= need
        result = ("sent away" if kind == ABJURE_KIND else "no effect: only summoned creatures can be sent away") \
            if works else "fails"
        return [f"    Abjure on {self._name(target)}: d20 = {roll}, needs {need} or more (11 - caster level {level} "
                f"+ its level {their}) -> {result}"]

    def _magic_resistance(self, target: int, spell: int, roll: int) -> List[str]:
        """The d100 the game rolls against a target's magic resistance before its saving throw."""
        g = self.game
        resistance = g.magic_resistance(target) or 0
        how = []
        if g.wears_type(g.combatant_creature(target), game.MR_AMULET_TYPE, NECK_SLOT):  # (DSCLOG's AMULET_MR)
            resistance += worldgear.AMULET_PERCENT
            how.append(f"+{worldgear.AMULET_PERCENT} Amulet of Magic Resistance")
        # the game's rules (its routine at 7A4A1h): Mind Bar +75 against mind-affecting spells,
        # then Lower Resistance halves it
        on = {x.id for x in g.effects() if x.owner == target}
        if MIND_BAR in on and g.mind_affecting(spell):
            resistance += MIND_BAR_RESISTANCE
            how.append(f"+{MIND_BAR_RESISTANCE} Mind Bar")
        if LOW_RESISTANCE in on and resistance:
            resistance //= 2
            how.append("halved by Lower Resistance")
        if not resistance:  # the roll can't matter
            return []
        detail = f" ({', '.join(how)})" if how else ""
        return [f"{g.combatant_name(target)} magic resistance {resistance}%{detail} vs "
                f"{g.spell_name(spell)}: d100 = {roll} -> {'resisted' if roll < resistance else 'not resisted'}"]

    def _flush_spell(self, spell: int) -> List[str]:
        """Dice rolled just before a spell's saving throws belong to that spell."""
        name = self.game.spell_name(spell)
        out = []
        for p in self._pending:
            if p.resistance:
                out += self._magic_resistance(*p.resistance)
            elif not p.damage and self._power_lasts(spell, p.text):
                out.append(f"{name}: {self._power_lasts(spell, p.text)} unless saved against ({p.text})")
            else:
                out.append(f"{name}{' damage' if p.damage else ''}: {p.text}")
        self._pending.clear()
        return out

    def _power_lasts(self, spell: int, dice: str) -> str:
        """"lasts 7 rounds" when DICE (a pending roll's text) are how long a monster's power's
        effect would last (the game rolls its record's dice for that before the saving throw),
        else ""."""
        if spell is None or spell <= game.SPELL_COUNT or self.game.power_effect(spell) <= 0:
            return ""
        try:
            found = self.game.spell_duration(spell, 0, int(dice.rsplit("=", 1)[1]))
        except (ValueError, IndexError, struct.error, OSError):
            return ""
        return f"lasts {game.game_time(found[0])}" if found else ""

    def _save_line(self, target, caster, spell, index, natural, total, needed) -> str:
        g = self.game
        kind = SAVE_NAMES.get(index, "?")
        # a spell left on the ground (Grease, a cloud) makes its victims save with themselves as the caster
        source = f" from {g.combatant_name(caster)}" if caster != target else ""
        who = f"{g.combatant_name(target)}'s saving throw vs {g.spell_name(spell)}{source} ({kind})"
        if total is None:
            return f"{who}: d20 = {natural} (natural {natural}) -> {self._save_result(spell, natural == 20)}"
        if total >= 0x80:  # the game adds -100 / +100 for "can't save" / "always saves"
            total -= 0x100
        if total < -50:
            return f"{who}: none allowed (cannot save) -> failed"
        if total > 100:
            return f"{who}: not needed (saves automatically) -> saved"
        rules = g.spell_rules(spell)
        steps, rolled = "d20", None
        if natural is not None:
            steps, rolled = f"d20 = {natural}", natural
            if rules and rules.doubles_roll:
                rolled = natural * 2
                steps += f", doubled against {rules.doubled_for} = {rolled}"
            parts = []
            if rules and rules.save_modifier:
                parts.append(f"{signed(rules.save_modifier)} spell")
            rest = total - rolled - (rules.save_modifier if rules else 0)
            try:
                known = g.save_modifiers(target, caster, spell, index)
            except (struct.error, IndexError, ValueError):
                known = []
            parts += [f"{signed(amount)} {why}" for amount, why in known]
            other = rest - sum(amount for amount, _ in known)
            if other:  # Dismissal weighs the levels; anything else the log doesn't know of
                parts.append(f"{signed(other)} " + ("levels (the target's less the caster's)"
                                                    if g.spell_name(spell) == "Dismissal" else "other"))
            if parts:
                steps += " " + " ".join(parts) + f" = {total}"
        else:
            steps += f" total {total}"
        chance = ""
        if natural is not None:
            doubled = bool(rules and rules.doubles_roll)
            chance = f" ({save_chance(needed - (total - (rolled or 0)), doubled)}% to save)"
        return f"{who}: {steps}, needs {needed}{chance} -> {self._save_result(spell, total >= needed)}"

    def _save_result(self, spell: int, saved: bool) -> str:
        """'saved' or 'failed', and what that does to the spell's damage: the amount from the
        damage roll just before (the game rolls each target's damage, then its save; resistances
        and protections can still lower it, which the HP line after shows)."""
        rule = self.game.spell_damage(spell)
        rolled = self._last_damage[1] if self._last_damage and self._last_damage[0] == spell else None
        if rule is None or rule.sides < 2:  # no damage dice (1d1 is the game's "none")
            return "saved" if saved else "failed"
        if not saved:
            return f"failed: full damage, {rolled}" if rolled is not None else "failed: full damage"
        if self.game.save_negates_damage(spell):
            return f"saved: no damage (not {rolled})" if rolled is not None else "saved: no damage"
        return f"saved: half damage, {rolled // 2} of {rolled}" if rolled is not None else "saved: half damage"

    # AC --------------------------------------------------------------------------------

    def _ac(self, e: Entry, show_all: bool) -> List[str]:
        """The end of the game's AC calculation: [BP-6] is the AC after armour (and spells that
        replace armour, such as Spirit Armor); SI adds DEX, when not attacked from behind,
        and spells."""
        target, rear = e.arg(6), e.arg(0x0A)
        index = self.game.combatant_creature(target) if target is not None else None
        ac = e.raw if e.raw < 0x8000 else e.raw - 0x10000
        if index is not None:
            self.last_ac[index] = ac
            self._ac_whose[index] = self.game.creature_name(index)
            sheet, rec = self.game.sheet(index), self.game.creature(index)
            armour = e.local(-6)
            if len(sheet) >= game.SHEET_SIZE and len(rec) >= game.CREATURE_SIZE and armour is not None:
                base = struct.unpack("b", sheet[game.SHEET_BASE_AC:game.SHEET_BASE_AC + 1])[0]
                dex = self.game.dex_ac(rec[CREATURE_ABILITIES + 1]) if not rear else 0
                self.ac_detail[index] = AcDetail(base, armour - base, dex, ac - armour - dex, ac)
        if show_all:
            return [f"AC of {self.game.combatant_name(target)} against {self.game.combatant_name(e.arg(8))}: {ac}"]
        return []

    # ability checks --------------------------------------------------------------------

    def _check(self, e: Entry, show_all: bool) -> List[str]:
        d20 = scaled(e.raw, 20) + 1
        ability = e.arg(0x0A)
        if not 0 <= ability < 6:
            return [f"Check: d20 = {d20}"] if show_all else []
        base = self.game.creature(e.arg(6))[CREATURE_ABILITIES + ability]
        seg, off = CHECK_MODS
        mod = struct.unpack("<b", self.guest.read((self.load_seg + seg) * 16 + off + e.arg(8), 1))[0]
        ok = d20 != 20 and d20 <= base + mod
        mod_text = f" {signed(mod)}" if mod else ""
        return [f"{self.game.creature_name(e.arg(6))} {ABILITIES[ability]} check: d20 = {d20}, "
                f"needs {base + mod} or less ({ABILITIES[ability]} {base}{mod_text}) "
                f"-> {'success' if ok else 'failure'}"]
