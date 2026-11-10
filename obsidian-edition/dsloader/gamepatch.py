"""The patched copy of the game the dice log runs: DSUNLOG.EXE.

The copy differs from DSUN.EXE in a few places, each replaced by an INT
instruction that DSCLOG.EXE answers (see dos/dsclog.asm):

  * the start of rand(), so every random number goes through DSCLOG, which
    gives the same numbers and records who asked;
  * the end of the saving throw, where DSCLOG records the final total and the
    number it had to reach;
  * the end of the AC calculation, where DSCLOG records the AC the game uses;
  * the start of the routine that feeds the dialogue window, where DSCLOG
    copies the text, the replies to choose from and the portrait shown;
  * the start of the message box routine ("... is broken !", level ups);
  * two places where the game adds up AC and saving throw modifiers, so that a worn
    ring with a plus (the Ring +1 the Loader can put in the arena) counts;
  * the routine that lists a character's weapons, where DSCLOG adds each one's THAC0;
  * the start of a turn in a fight, where DSCLOG can add a move for boots (a rule change
    the Loader turns on, like AC 1 for helms, which the AC place above gives).

A last change lets the copy live outside the game folder: the game looks for
its data files in the folder its EXE is in, and the copy looks in the current
folder instead (the launcher runs it from the game folder).

Patching the file rather than the running game means the patches are in place
before the game runs, including in overlays each time they are loaded. The
original DSUN.EXE is only read.
"""

import os
import struct
from typing import NamedTuple

GOG_SIZE = 611408  # DSUN.EXE of the GOG release (1.1)

VEC_RAND, VEC_SAVE, VEC_AC, VEC_TEXT, VEC_MSG, VEC_CHAR = range(0x60, 0x66)  # as in dsclog.asm
VEC_USE, VEC_VIEW, VEC_WIN, VEC_LOOK, VEC_UNLOOK = 0xF2, 0xF3, 0xF4, 0xF5, 0xF6  # (none free) not 66h-6Fh: the game calls those itself, looking for drivers
VEC_RING_AC, VEC_RING_SAVE, VEC_WEAPON, VEC_MOVE, VEC_MISSILE_LINE, VEC_USE_ITEM = 0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD
VEC_TWO, VEC_DOUBLE = 0xFE, 0xF0
VEC_GRACE_CAST, VEC_GRACE_EFFECT, VEC_GRACE_ABILITY = 0xED, 0xEE, 0xEF
VEC_NAMES_SIZE, VEC_NAMES_FILL = 0xEC, 0xEB
VEC_STEALTH = 0xEA
VEC_TYPES_SIZE, VEC_TYPES_FILL = 0xE9, 0xE8
VEC_LEVEL, VEC_HD_ROLL, VEC_HD_CON, VEC_THIEF_SKILL, VEC_TWO_HANDED = 0xE7, 0xE6, 0xE5, 0xE4, 0xE3
VEC_SPELL_TEXT, VEC_CHUNK_ID = 0xE2, 0xE1
VEC_FLOOR_ALL, VEC_FLOOR_RECT, VEC_REDRAW, VEC_REDRAW_ALL = 0xE0, 0xDF, 0xDE, 0xDD
VEC_SCROLL, VEC_HIT, VEC_ITEM_BOX = 0xDC, 0xDB, 0xDA
VEC_GHOST = 0x80  # (a see-through figure: DSCLOG's PROBE_GHOST; 62h was VEC_AC's)
VEC_BELT = 0xD9
VEC_SAVE_PAGE, VEC_SAVE_CLICK = 0xD8, 0xD7
VEC_ITEM_WEAPON, VEC_ITEM_SKIP, VEC_ITEM_ARMOUR = 0xD6, 0xD5, 0xD4  # (item saves)
VEC_SCRIPT_RAND = 0xD3
VEC_XP_NEXT = 0xD2
VEC_ATTACKS = 0xD1
VEC_SPEC_DAMAGE = 0xD0
VEC_DAM_LINE = 0xCF
VEC_VIEW_DAM = 0xCE
VEC_CAN_USE = 0xCD
VEC_NO_CAST = 0xCC
VEC_MC_CON, VEC_MC_UNCON = 0xCA, 0xC9
VEC_WP_DISC_WIN, VEC_WP_SPHERE_WIN, VEC_WP_DISC_CLICK, VEC_WP_SPHERE_CLICK, VEC_WP_SHOWN = 0xC8, 0xC7, 0xC6, 0xC5, 0xC4
VEC_WP_CLASS = 0xC3
VEC_LV_PICK = 0xC2
VEC_PK_COUNT, VEC_PK_WIN, VEC_PK_LEFT, VEC_PK_TITLE, VEC_PK_FILL, VEC_PK_CLICK = 0xC1, 0xC0, 0xBF, 0xBE, 0xBD, 0xBC
VEC_EF_ROWS = 0xBB
VEC_HP_BEST = 0xBA
VEC_TOME = 0xB9
VEC_INIT = 0xB8
VEC_THAC0 = 0xB7
VEC_SLOTS, VEC_SLOT_LEVEL = 0xB6, 0xB5
VEC_PSP_USE, VEC_PSP_TABLE, VEC_PSP_DEFENCE = 0xB4, 0xB3, 0xB2
VEC_CURE, VEC_PSP_KEEP = 0xB1, 0xB0
VEC_RANGER_CAST, VEC_PSP_KEEP_DX, VEC_HIT_ROUND = 0xAF, 0xAE, 0xAD
VEC_CAST_LEVEL, VEC_PICK_LEVEL, VEC_PICK_LIST, VEC_SCROLL_LEARN, VEC_SPELL_LEVEL = 0xAC, 0xAB, 0xAA, 0xA9, 0xA8
VEC_PICK_ANY, VEC_RANGER_LEVEL = 0xA7, 0xA6
VEC_HIT_DIE, VEC_MAX_PSP, VEC_CR_DIE, VEC_CR_PSP = 0xA5, 0xA4, 0xA3, 0xA2
VEC_EL_GRANT, VEC_EL_CAST, VEC_EL_LEVEL, VEC_EL_KNOW = 0xA1, 0xA0, 0x9F, 0x9E
VEC_DUAL_BAN, VEC_DUAL_SPELLS, VEC_SOUND_42, VEC_SOUND_44, VEC_DUAL_KIT = 0x9D, 0x9C, 0x9B, 0x9A, 0x99
VEC_CR_SPELLS, VEC_EF_CLICK = 0x98, 0x97
VEC_CAST_MARK, VEC_ROUND_MARK, VEC_CAST_DONE, VEC_END_TURN = 0x96, 0x95, 0x94, 0x93
VEC_LEARN_SAID, VEC_LEARN_REFUSED = 0x92, 0x91
VEC_XP, VEC_PRIEST_THAC0, VEC_ADND_SLOTS = 0x90, 0x8F, 0x8E
VEC_POINTER = 0xF1
VEC_PRICE, VEC_PRICE_EAX = 0x8D, 0x8C
VEC_RS_CLICK = 0x8A
VEC_RACE_PANEL = 0x89
VEC_BOX_AC = 0x88
VEC_TICK = 0x87
VEC_POISON = 0x86
VEC_ARROW = 0x85
VEC_OVR_BUF = 0x84
VEC_HEAP = 0xCB
VEC_FLIP = 0x8B
VEC_PACE_PASS, VEC_PACE_DRAW = 0x83, 0x82
VEC_WORN = 0x81
VEC_TAKE = 0xF7
VEC_SPHERE = 0xFF
# the game's data segment (4356h) in DSUN.EXE: after the 5400h-byte header
DS_FILE = 0x5400 + 0x4356 * 16
RL_SCORE, RL_HP, RL_ROLL, RL_SUM, RL_CON, RL_TRY = 1, 2, 3, 4, 5, 6  # (sites sharing VEC_CR_SPELLS, as in dsclog.asm)
PK_HOVER = 7
RG_TWO = 8  # (the ranger's two weapons, light armour only: DSCLOG's RG_TWO)
# The new spells (196-201: DSCLOG's NEW SPELLS) share it too: NS_KNOWN, NS_LEARN, NS_NAME, NS_CLAW,
# NS_HIT, then NS_CMP's sites in the order of DSCLOG's NS_CMP_SITES
NS_KNOWN, NS_LEARN, NS_NAME, NS_CLAW, NS_HIT, NS_CMP = 9, 10, 11, 12, 13, 14
# Each "cmp" of a spell's number with 8Ah (a psionic power from there), 45h (a priest spell), 0ACh
# (a monster's power) or 0C4h (the end) that a new spell meets, which NS_CMP makes as a wizard's
NS_CMP_SITES = (
    (0x5585C, "81fe8a00"), (0x55865, "83fe45"),  # the USE screen's spells, drawn
    (0x55AEC, "807eff8a"), (0x55AF2, "807eff45"),  # ... a click on one (its icon, which slots)
    (0x55FEC, "81fe8a00"), (0x55FF5, "83fe45"),  # ... those that can be cast
    (0x6CC93, "813ef54a8a00"), (0x6CCBE, "813ef54ac400"),  # the spell cast in a fight, shown
    (0x72051, "813ef9548a00"),  # the readied spell's icon
    (0x76883, "2681bf0a018a00"), (0x76C00, "2681bf0a018a00"),  # an effect's spell: not a power's upkeep
    (0x772BB, "81fac400"), (0x772C7, "81faac00"), (0x772EC, "81fa8a00"),  # the cast
    (0x7A258, "81fe8a00"),  # its effect on the target
    (0x7BDA7, "81fe8a00"), (0x7BDB1, "81fe8a00"), (0x7BDCB, "81fe8a00"),  # 1st to 3rd level (Minor Globe)
    (0x81B23, "817e088a00"),  # the caster level
    (0x84C76, "81fe8a00"), (0x851BB, "81fe8a00"),  # the level the spell is cast at
    (0x88DE0, "813ef54a8a00"), (0x88DFF, "813ef54ac400"),  # the spell cast, shown
    (0x8B491, "807efdc4"), (0x8B6B5, "807efd8a"), (0x8B875, "817efe8a00"),  # a scroll used: its
    (0x8B8AA, "807efdc4"), (0x8BA37, "807efdc4"), (0x8BA70, "807efdc4"),  # spell, learnt, its icon
    (0x6F827, "807effc4"), (0x6F8D8, "81fac400"),  # an item's spell used, and cast
    (0x720D3, "81fa8a00"), (0x8C457, "81fa8a00"),  # an item's spell's icon (a scroll's in its box)
    (0x8C64E, "81fe8a00"),  # the spell info box's icon
    (0x8B0FA, "80f9c4"), (0x58B7E, "80f9c4"),  # a scroll's spell, read; a weapon's, on a hit
)
# the lists of spells a member knows, may learn, may cast (500:25h, 2Ah, 2Fh): "cmp si,8Ah", the
# end of their loops, made the new spells' end (their rows are empty while the rule is off)
NS_FIST = NS_CMP + len(NS_CMP_SITES)  # (a melee hit's magic: after NS_CMP's)
NS_IMAGE = NS_FIST + 1  # (an image taking a spell: Reflected Image's chance, only a foe's)
# an effect's entry in the effects' table (its number times 6): Reflected Image's own name and icon
# where Mirror Images is its (DSCLOG's NS_ENTRY): the Effects screen's, the Look box's, a portrait's
NS_ENTRY_EF, NS_ENTRY_LOOK, NS_ENTRY_STATUS = NS_IMAGE + 1, NS_IMAGE + 2, NS_IMAGE + 3
SELL_KEEP = NS_IMAGE + 4  # (a shop freeing an item sold: DSCLOG keeps a magical one, buyback.py)
SELL_PRICE = NS_IMAGE + 5  # (what a shop pays: half with the CHA prices rule, prices.sell_price)
NS_BLOW = NS_IMAGE + 6  # (an attack's hit, which an image may take instead)
NS_HOLD = NS_IMAGE + 7  # (Hold Undead on a target that isn't undead: immune)
# A thief's Pick Pockets button where a priest's Turn Undead is (DSCLOG's PICK POCKETS): the
# button shown, let go of, its spell readied (none: the pick), and the talk it makes a pick
PP_SHOW, PP_CLICK, PP_ARM, PP_HAND, PP_LIT = NS_IMAGE + 8, NS_IMAGE + 9, NS_IMAGE + 10, NS_IMAGE + 11, NS_IMAGE + 12
PP_TEXT, PP_INFO = NS_IMAGE + 13, NS_IMAGE + 14  # (its name under the screen; its spell's description)
PP_CLOSE = NS_IMAGE + 15  # (the USE screen closing: a cleric/thief's second button's icon let go of)
CR_LABELS = NS_IMAGE + 16  # (the ability labels: the creation screen's in its white)
CR_WEAPONS = NS_IMAGE + 17  # (the creation screen's DONE: a warrior picks its weapon specs)
NS_NPP = NS_IMAGE + 18  # (Negative Plane Protection's save: one allowed)
NS_SIDE = NS_IMAGE + 19  # (an effect ended: Berserk and Confused give the side back)
NS_WALL = NS_IMAGE + 20  # (the computer's cast: a wall across the line of fire)
SHOP_SHINE = NS_IMAGE + 21  # (the wait for an event: a shop's magic items' shine turned, as on the map)
SHOP_LOOP = NS_IMAGE + 22  # (... and a shop's own event loop)
DET_ITEM = NS_IMAGE + 23  # (Detonate's blast on an item: the check recorded for the dice log)
WANDER_DMG = NS_IMAGE + 24  # (a spell's damage: a Wanderer guarded from fire and cold, halving it)
REQ_SITE = NS_IMAGE + 25  # (a script's REQUEST: recorded for the dice log)
AIM_SITE = NS_IMAGE + 26  # (a spell cast with a click, refused: why, recorded for the dice log)
AMULET_SITE = NS_IMAGE + 27  # (a creature's magic resistance: the Amulet of Magic Resistance's 15% added)
ARROW_HIT_SITE, ARROW_SPELL_SITE = NS_IMAGE + 28, NS_IMAGE + 29  # (a hit's spell: a spell arrow's, spellarrows.py)
CAST_SITE = NS_IMAGE + 30  # (a spell cast: recorded, its name floated over the caster, labels.py)
REST_SITE = NS_IMAGE + 31  # (the game's rest: recorded, the spell arrows fade, spellarrows.py)
HARM_SITE = NS_IMAGE + 32  # (a one-target spell's damage: Harm's all but 1d4)
AREA_SITE = NS_IMAGE + 33  # (the game's own code reading the ground pictures' table: DSCLOG's copy)
ACID_SITE = NS_IMAGE + 34  # (an effect added: Acid's time made rounds as charges, DSCLOG's ACID_ROUNDS)
BURN_SITE, ONCE_SITE = NS_IMAGE + 35, NS_IMAGE + 36
STAB_SITE, TIMES_SITE = NS_IMAGE + 39, NS_IMAGE + 40  # (a backstab: the weapon's dice only, RULE_BACKSTAB)
DRAW_SITE = NS_IMAGE + 42  # (a thing on the map about to be drawn: Whirlwind's funnel once, DSCLOG's DRAW_SITE)
CINE_STEP, CINE_END = NS_IMAGE + 43, NS_IMAGE + 44  # (scenes: the pointer shown, a click ends one)
MOUSE_SET, MOUSE_INIT = NS_IMAGE + 45, NS_IMAGE + 46  # (the pointer starting in the middle, as fast up as across)
SPREAD_SITE = NS_IMAGE + 48  # (a game loaded with the party in one figure: spread out on the map)
GATHER_SITE = NS_IMAGE + 55  # (the party put in one figure: after a fight, spread out again)
FLIP_SITE = NS_IMAGE + 56  # (the game's flip of its screens: the combat log's panel put on the new one first)
WW_SITE = NS_IMAGE + 57  # (a one-target spell's damage starting: Whirlwind's once a round, DSCLOG's WW_GATE)
ENL_SITE = NS_IMAGE + 58  # (a melee hit's damage made bigger by Enlarge: the weapon's dice only, RULE_ENLARGE)
REGEN_SITE, CON_SITE = NS_IMAGE + 59, NS_IMAGE + 60  # (CON as in AD&D: regeneration's rates, dwarves' poison saves)
CR_AGE_SITE = NS_IMAGE + 61  # (the creation panel's PSP drawn: the age above RECALL, a new roll, DSCLOG's CR_AGE)
CR_AGE_CON_SITE = NS_IMAGE + 66  # (the same after a click on CON: the roll kept, DSCLOG's CR_AGE_CON)
CR_OPEN_SITE = NS_IMAGE + 67  # (the creation screen opening, a new member or EDIT: DSCLOG's CR_OPEN)
CR_HP_SITE = NS_IMAGE + 68  # (the hit points drawn again: the THAC0 after them, DSCLOG's CR_HP)
STINK_SITE, CHAOS_SITE = NS_IMAGE + 69, NS_IMAGE + 70  # (Stinking Cloud's round more; Chaos's INT exception: DSCLOG's STINK_SITE, CHAOS_SITE)
# (a classless creature's level for its saves its hit dice; Color Spray unsaved by the caster's
# level or lower; Hold Undead only on undead of no more levels than its caster's: DSCLOG's
# HD_SAVE, SPRAY_SITE, HOLD_HD)
HD_SAVE_SITE, SPRAY_SITE, HOLD_HD_SITE = NS_IMAGE + 71, NS_IMAGE + 72, NS_IMAGE + 73
# (a missile spell or a hostile touch spell on its target: its attack roll, and the always-hit
# stub of the missile spells answering it: DSCLOG's SPELL_HIT, SPELL_STUB)
SPELL_HIT_SITE, SPELL_STUB_SITE = NS_IMAGE + 74, NS_IMAGE + 75
# (Turn Undead by AD&D's table, its outcomes turned, destroyed and D*, once a priest a creature a
# fight; a cast's repeats, Flame Arrow's one for every five levels: DSCLOG's TURN_SITE, FLAME_SITE)
TURN_SITE, FLAME_SITE = NS_IMAGE + 76, NS_IMAGE + 77
# (the spells and psionics as the manual describes them, group 3: Barkskin's and Blur's +1 on saves;
# Protection from Cold's +3 and Fire Shield's +2; Cloudkill's save by level and its kill; Lower
# Resistance's 30 + its level off; Strength's and Cat's Grace's dice by class; damage ending Rainbow
# Pattern's hold; no psionics while feebleminded; Biofeedback's 2 off a blow leaving at least 1; Cell
# Adjustment's 1d4:
# DSCLOG's BLUR_SITE ... CELL_SITE)
BLUR_SITE, FSHIELD_SITE, CLOUD_SAVE_SITE, CLOUD_KILL_SITE, LOWRES_SITE = range(NS_IMAGE + 78, NS_IMAGE + 83)
STRENGTH_SITE, RAINBOW_SITE, PSI_SITE, BIO_SITE, CELL_SITE = range(NS_IMAGE + 83, NS_IMAGE + 88)
# (dual-classing as the manual has it, RULE_DUAL_CLASS: the level DUAL needs, the old and the new class's
# prime requisites: DSCLOG's DUAL_LEVEL, DUAL_PRIMES)
DUAL_LEVEL_SITE, DUAL_OLD_SITE, DUAL_NEW_SITE = range(NS_IMAGE + 88, NS_IMAGE + 91)
# (the monsters as the manual describes them: a shadow's STR drain; a Tari's 1 in 20: DSCLOG's
# SHADOW_DRAIN, TARI_BITE)
DRAIN_SITE, TARI_SITE = NS_IMAGE + 91, NS_IMAGE + 92
# (resting, RULE_REST: the priests' and psionicists' cures before it, natural healing in it: DSCLOG's
# REST_PRE, REST_HP)
# (NS_IMAGE + 93 is 90h, a NOP: DSCLOG takes the byte after its INT for no site then, so no site has it)
REST_PRE_SITE, REST_HP_SITE = NS_IMAGE + 94, NS_IMAGE + 95
# (a saving throw's natural 20, saving unless the save can't be made: DSCLOG's SAVE_SUM)
SAVE_SUM_SITE, SAVE_NAT_SITE = NS_IMAGE + 96, NS_IMAGE + 97
# (the item box's picture: a tall weapon's small copy, icons.BOX_TALL: DSCLOG's BOX_PICS)
BOX_PIC_ITEM_SITE, BOX_PIC_OBJECT_SITE = NS_IMAGE + 98, NS_IMAGE + 99
# (the picture cache's 300 slots: one reused once all are taken, DSCLOG's PIC_REUSE)
PIC_FULL_SITE, PIC_PLACE_SITE, PIC_COUNT_SITE = NS_IMAGE + 100, NS_IMAGE + 101, NS_IMAGE + 102
# (the cahulaks' rule, RULE_CAHULAKS: two weapons ready, the off head's swing, the tangle: DSCLOG's CAHULAKS)
CAH_TWO_SITE, CAH_SWING_SITE, CAH_HIT_SITE = NS_IMAGE + 103, NS_IMAGE + 104, NS_IMAGE + 105
# (a weapon's damage line drawn, the item box's and the inventory's: its large dice, DSCLOG's SIZE_LINE)
SIZE_LINE_SITE, SIZE_PRE_SITE = NS_IMAGE + 106, NS_IMAGE + 107
# (AD&D's held target, RULE_HELD: hit automatically, normal damage: DSCLOG's HELD)
HELD_HIT_SITE, HELD_DAMAGE_SITE = NS_IMAGE + 108, NS_IMAGE + 109
# (the picture loader's failure: a reused slot let go again, DSCLOG's PIC_FAIL)
PIC_FAIL_SITE = NS_IMAGE + 110
# the monster kinds' table (DSUN.EXE, the load segment's 3E45h: monsters.MONSTER_KINDS_SEG): a kind's
# properties (a dword), its resistance class (a byte), a class's damage kinds (four words) and percents
KINDS_FILE = 0x5400 + 0x3E45 * 16
def _kind(kind: int) -> int:
    return KINDS_FILE + 4 * kind
CR_NAME_SITE, CR_NAME2_SITE, CR_NAME3_SITE, CR_NAME4_SITE = range(NS_IMAGE + 62, NS_IMAGE + 66)  # (a name the game gave copied to the creature: PSP and the age drawn again)
ARROW_LEVEL = NS_IMAGE + 47  # (a spell arrow's spell at the archer's preserver level, not a weapon's 6)
SCROLL_USE = NS_IMAGE + 49  # (an item's box: a Shinobi's scroll picture a button, so it can learn the spell)
AREA_DMG = NS_IMAGE + 54  # (a spell's damage to the creatures it reaches: a Wilderness Avenger's Cause Wounds, kits.harm_bonus)
AV_GRANT = NS_IMAGE + 53  # (a priest given its spheres' spells: a Wilderness Avenger's healing ones not: kits.AVENGER_NO_HEAL)
BOX_SAID, LINE_SAID, LINE_CLEARED = range(NS_IMAGE + 50, NS_IMAGE + 53)  # (an item's box: its message, never seen on the
#   inventory, put on the inventory's line for 5 s each time the pointer's handler writes or clears it)
HEAT_SITE = NS_IMAGE + 41  # (a spell's damage on a creature: Sunstroke's heat named and made fire, DSCLOG's HEAT_SITE)
USE_SITE, ROUND_SITE = NS_IMAGE + 37, NS_IMAGE + 38  # (Acid spent once a round, at its start, and only then)  # (an Acid's burn: its damage puts no Acid on again)
NS_LIST_ENDS = (0x5DDEF, 0x5DE72, 0x5DF06)
NS_END = 0xD4  # (past the new spells: 196-211, DSCLOG's NS_FIRST + NS_COUNT; game.NEW_SPELLS_END)


def _site(number: int, length: int) -> bytes:
    """INT VEC_CR_SPELLS and a site's number, NOPs to LENGTH."""
    return bytes((0xCD, VEC_CR_SPELLS, number)) + b"\x90" * (length - 3)


SCRIPT_BUFFER = 0x2E00  # the scripts' buffer, made bigger (the game's: 10000 bytes)
CHARACTERS = 29  # the saved characters (CHARSAVE.GFF's numbers 1 to this; the game's: 19)


class Patch(NamedTuple):
    name: str
    offset: int  # in DSUN.EXE
    original: bytes
    replacement: bytes


def _interrupt(vector: int, length: int) -> bytes:
    return bytes((0xCD, vector)) + b"\x90" * (length - 2)


# "New" counted as "Okay": a character not yet played has the status New (0, the creature's
# +1Ch; the game makes it Okay, 1, when the game starts, and gives starting gear to a New one).
# The game's tests for Okay ("cmp byte es:[bx+1Ch],1" then "jz" or "jnz", on the creature table's
# record) left a New one out: the inventory screen's thief skills all 0, for one. Each test's
# jump becomes "jbe" or "ja" (0 or 1, as Okay); the tests for New itself, and the code that
# makes one Okay (DSUN.EXE 59DA4h, healing), are left as they are, and so is the one that
# picks the status shown under the portrait (71DB6h): a New character still reads "New".
NEW_AS_OKAY = ((0x1C97F, 0x75), (0x1DE08, 0x75), (0x1E0C5, 0x75), (0x1EBB3, 0x75), (0x200F7, 0x74),
               (0x2075C, 0x74), (0x20B0F, 0x74), (0x556A9, 0x74), (0x5747B, 0x74), (0x583EA, 0x75),
               (0x5843F, 0x74), (0x584A4, 0x75), (0x5850E, 0x74), (0x586C7, 0x74), (0x58809, 0x75),
               (0x59E35, 0x75), (0x5A73F, 0x75), (0x5CA45, 0x75), (0x6B6D4, 0x75), (0x761F0, 0x74),
               (0x802AC, 0x74), (0x806FA, 0x75), (0x80864, 0x74), (0x89B75, 0x75))
_OKAY_TEST = bytes.fromhex("26807f1c01")  # cmp byte es:[bx+1Ch],1
_OKAY_JUMPS = {0x74: 0x76, 0x75: 0x77}  # jz -> jbe, jnz -> ja


# The object records routine's "lea dx/ax,[bp-1F8h]" (96h dx, 86h ax), its table's start, and
# the most records an object can have with the table made larger (gamepatch "records_most")
RECORDS_TABLE = ((0x680FA, 0x96), (0x6813B, 0x96), (0x6814D, 0x86), (0x68198, 0x96), (0x681AA, 0x86),
                 (0x6820C, 0x96), (0x6821E, 0x86))
RECORDS_MOST = 120


def _new_as_okay(offset: int, jump: int) -> "Patch":
    return Patch(f"new_okay_{offset:x}", offset, _OKAY_TEST + bytes((jump,)), _OKAY_TEST + bytes((_OKAY_JUMPS[jump],)))


PATCHES = (
    # rand(): mov cx,[seed+2] / mov bx,... (the second instruction's first byte)
    Patch("rand", 0x5C22, bytes.fromhex("8b0e24418b"), _interrupt(VEC_RAND, 5)),
    # saving throw: mov al,[bp-2] / cmp al,[bp-1]
    Patch("save", 0x79BB7, bytes.fromhex("8a46fe3a46ff"), _interrupt(VEC_SAVE, 6)),
    # AC: mov ax,[bp-6] / add ax,si
    Patch("ac", 0x58FB6, bytes.fromhex("8b46fa03c6"), _interrupt(VEC_AC, 5)),
    # the dialogue window's input routine (kind, far pointer, word): push bp / mov bp,sp
    Patch("text", 0x7CE83, bytes.fromhex("558bec"), _interrupt(VEC_TEXT, 3)),
    # the message box routine (far pointer to the message): push bp / mov bp,sp
    Patch("message", 0x5536E, bytes.fromhex("558bec"), _interrupt(VEC_MSG, 3)),
    # the inventory screen's right-hand panel, just after its weapon lines: add sp,0Eh
    # (DSCLOG then adds THAC0, the saves and thief skills, in the game's own lettering)
    Patch("inventory", 0x6F6BF, bytes.fromhex("83c40e"), _interrupt(VEC_CHAR, 3)),
    # the USE (cast spells) screen, after it labels its LEVEL button: add sp,0Ch
    # (DSCLOG then draws the character's spell slots under the spells)
    Patch("use", 0x70FBB, bytes.fromhex("83c40c"), _interrupt(VEC_USE, 3)),
    # the View Character screen's upper panel, once drawn: push dword 000B0140h
    # (DSCLOG then adds THAC0 and the saves under the item icons, and does the push)
    Patch("view", 0x8A471, bytes.fromhex("666840010b00"), _interrupt(VEC_VIEW, 6)),
    # the end of the routine that brings a window to the front and redraws it: xor ax,ax /
    # pop si (for the USE screen's window, DSCLOG draws the spell slots again)
    Patch("window", 0x2BBA9, bytes.fromhex("33c05e"), _interrupt(VEC_WIN, 3)),
    # the Look box (a creature in a fight), once its first status rows are drawn: mov si,ax /
    # xor di,di (DSCLOG then adds the monster's defences in the rows left, and does the moves)
    Patch("look", 0x5FCDA, bytes.fromhex("8bf033ff"), _interrupt(VEC_LOOK, 4)),
    # the end of the routine that closes the Look box: mov word [0844h],270Fh (DSCLOG does it,
    # then shows the monster's whole description in the dialogue window)
    Patch("unlook", 0x5F2AA, bytes.fromhex("c70644080f27"), _interrupt(VEC_UNLOOK, 6)),
    # the AC function, as it reads a worn item's type flags: mov al,es:[bx+0Fh] / cbw (DSCLOG
    # does it, marking rings as counting for AC, so a ring's plus betters AC)
    Patch("ring_ac", 0x58EBD, bytes.fromhex("268a470f98"), _interrupt(VEC_RING_AC, 5)),
    # the start of the saving throw's modifiers: xor si,si (DSCLOG starts SI, their sum, at
    # the plus of the rings the one saving wears)
    Patch("ring_save", 0x79D47, bytes.fromhex("33f6"), _interrupt(VEC_RING_SAVE, 2)),
    # the AC function's gladiator test: test word es:[bx+12h],40h (DSCLOG answers it for a
    # gladiator who wears armour only: armour optimisation needs armour)
    Patch("gladiator_armour", 0x58F86, bytes.fromhex("26f747124000"), _interrupt(VEC_WORN, 6)),
    # the ability routine, as it reads a listed item's ability byte: mov al,es:[bx+0Fh] (DSCLOG
    # gives it only for an item worn, so one in the pack raises no score)
    Patch("ability_worn", 0x7B8AB, bytes.fromhex("268a470f"), _interrupt(VEC_WORN, 4)),
    # Psionic Blast (the effect routine's case 169), once a target that failed its save is down to
    # a fifth of its most hit points: or byte [si],1 (DSCLOG does it, and keeps a party member's
    # loss for the Loader to give back as the fight ends: psiblast.py)
    Patch("psionic_blast", 0x79707, bytes.fromhex("800c01"), _interrupt(VEC_WORN, 3)),
    # ... and the damage routine's death test (612E:194Bh: hit points + 10 against the damage):
    # cmp ax,dx (DSCLOG does it, and a party member with Psionic Blast's hit points still to come
    # back is knocked out, not killed: the jg after it kept)
    Patch("blast_knockout", 0x5860B, bytes.fromhex("3bc2"), _interrupt(VEC_WORN, 2)),
    # ... and where the game makes a Dead Body for a creature that dies carrying something:
    # push 0FFFF044Dh, object 1101 (DSCLOG answers with the body's object in AX, the champions'
    # Tohr-kreen's own for that champion: champions.py), then push 0FFFFh, push ax
    Patch("champion_body", 0x59412, bytes.fromhex("66684d04ffff"), _interrupt(VEC_WORN, 2) + bytes.fromhex("6aff5090")),
    # the routine that lists a creature's weapons (the inventory screen, the Look box), straight
    # after drawing one: add sp,10h (DSCLOG does it, then adds that weapon's THAC0)
    Patch("weapon", 0x7276E, bytes.fromhex("83c410"), _interrupt(VEC_WEAPON, 3)),
    # where a creature's turn in a fight starts: mov es:[bx+22Bh],ax, its movement for the turn
    # (DSCLOG does it, adding 1 move for boots when the Loader's rule is on)
    Patch("move", 0x57566, bytes.fromhex("2689872b02"), _interrupt(VEC_MOVE, 5)),
    # the routine that uses the item on the pointer on what's under it on the map, once it has
    # found that: cmp si,-1 / jne +3 (DSCLOG has the Loader see to its thieving tools there)
    Patch("use_item", 0x73615, bytes.fromhex("83feff7503"), _interrupt(VEC_USE_ITEM, 5)),
    # the to-hit adjustment for two weapons ready, once it has the DEX's initiative adjustment:
    # neg ax / mov dx,ax / or dx,dx / jge +2 / xor dx,dx (DSCLOG does it, or AD&D's penalties
    # by hand when the Loader's rule is on)
    Patch("two_weapons", 0x59634, bytes.fromhex("f7d88bd00bd27d0233d2"), _interrupt(VEC_TWO, 10)),
    Patch("ranger_two", 0x5961F, bytes.fromhex("26f747120002"), bytes((0xCD, VEC_CR_SPELLS, RG_TWO, 0x90, 0x90, 0x90))),
    # the saving throw, doubling its d20 against fire, cold and electricity: shl al,1 (DSCLOG
    # does it, unless the Loader's rule is on)
    Patch("double", 0x79B74, bytes.fromhex("d0e0"), _interrupt(VEC_DOUBLE, 2)),
    # Cat's Grace (the Loader's rule, in Flaming Sphere's place): the spells with handlers of
    # their own, picking one by the spell's number: mov ax,[bp+0Eh] / mov [bp-1Ah],ax (DSCLOG
    # sends Cat's Grace to Strength's) ...
    Patch("grace_cast", 0x791F3, bytes.fromhex("8b460e8946e6"), _interrupt(VEC_GRACE_CAST, 6)),
    # ... Strength's handler choosing its effect, 43h (Adrenalin Control's 42h): cmp/jne/mov/
    # jmp/mov (DSCLOG gives Cat's Grace its own) ...
    Patch("grace_effect", 0x79470, bytes.fromhex("817e0e94007507c746ec4200eb05c746ec4300"),
          _interrupt(VEC_GRACE_EFFECT, 19)),
    # ... and the routine working out a creature's abilities, at each of its effects:
    # mov [bp-0Ah],ax / mov cx,7 (DSCLOG adds Cat's Grace's amount to DEX)
    Patch("grace_ability", 0x7B7D7, bytes.fromhex("8946f6b90700"), _interrupt(VEC_GRACE_ABILITY, 6)),
    # The new spells (DSCLOG's NEW SPELLS): the routine giving a spell's known byte (500:48h): its
    # "cmp si,4" (a new spell's is DSCLOG's, from the sheet) ...
    Patch("ns_known", 0x5DD04, bytes.fromhex("83fe04"), _site(NS_KNOWN, 3)),
    # ... the routine teaching one (500:43h), marking it: and byte es:[bx],0F0h / or byte es:[bx],1
    # (DSCLOG puts a new spell's in the sheet) ...
    Patch("ns_learn", 0x5E3F7, bytes.fromhex("268027f026800f01"), _site(NS_LEARN, 8)),
    # ... the routine giving a spell's name (500:61h): cmp ax,8Ah (DSCLOG's for a new one) ...
    Patch("ns_name", 0x5E560, bytes.fromhex("3d8a00"), _site(NS_NAME, 3)),
    # ... a natural attack's dice, before the game's effects for the first: or dx,dx / jne (Erdlu
    # Claw's 1d6+1 for each where it is better) ...
    Patch("ns_claw", 0x7B70A, bytes.fromhex("0bd27547"), _site(NS_CLAW, 4)),
    # ... an attack's to-hit adjustments from effects, the target's Blur: test byte [bp-8],80h
    # (Fogbolt's) ...
    Patch("ns_hit", 0x7C430, bytes.fromhex("f646f880"), _site(NS_HIT, 4)),
    # ... a melee hit's magic, as the hit's damage kinds get it: cmp word [bp-0Ch],0 (Erdlu Claw's
    # +1 to hit and +1 weapon for a natural attack) ...
    Patch("ns_fist", 0x58226, bytes.fromhex("837ef400"), _site(NS_FIST, 4)),
    # ... the d100 an image takes a spell on: cmp ax,4Bh (75; Reflected Image's one 50; only a
    # foe's, caster and target on opposite sides) ...
    Patch("ns_image", 0x7A5CD, bytes.fromhex("3d4b00"), _site(NS_IMAGE, 3)),
    # ... an attack's hit, before its damage: cmp word [bp+1Ah],0 (an image may take it instead,
    # the game's Mirror Images having stopped none) ...
    Patch("ns_blow", 0x58A00, bytes.fromhex("837e1a00"), _site(NS_BLOW, 4)),
    # ... an effect's entry, by its number times 6: Reflected Image's for its Mirror Images ...
    Patch("ns_entry_name", 0x7ED37, bytes.fromhex("6bc006"), _site(NS_ENTRY_EF, 3)),
    Patch("ns_entry_icon", 0x7EEC9, bytes.fromhex("6bc006"), _site(NS_ENTRY_EF, 3)),
    Patch("ns_entry_draw", 0x7EF34, bytes.fromhex("6bc006"), _site(NS_ENTRY_EF, 3)),
    Patch("ns_entry_look", 0x5FD1C, bytes.fromhex("6bdb06"), _site(NS_ENTRY_LOOK, 3)),
    Patch("ns_entry_status", 0x71DF5, bytes.fromhex("6bdb06"), _site(NS_ENTRY_STATUS, 3)),
    # ... the shop's "push word [179Eh]" before freeing an item sold (a magical one kept: buyback.py) ...
    Patch("sell_keep", 0x83D9E, bytes.fromhex("ff369e17"), _site(SELL_KEEP, 4)),
    # ... and the price the shop pays (mov si,es:[bx+6]: half, with the CHA prices rule) ...
    Patch("sell_price", 0x83CCA, bytes.fromhex("268b7706"), _site(SELL_PRICE, 4)),
    # ... the compares that tell a wizard's or priest's spell from the rest ...
    *(Patch(f"ns_cmp_{offset:x}", offset, bytes.fromhex(code), _site(NS_CMP + k, len(code) // 2))
      for k, (offset, code) in enumerate(NS_CMP_SITES)),
    # ... and the lists' ends
    *(Patch(f"ns_list_{offset:x}", offset, bytes.fromhex("81fe8a00"), bytes((0x81, 0xFE, NS_END, 0x00)))
      for offset in NS_LIST_ENDS),
    # Bugs of the game's spells, fixed whatever the rules (DEVELOPMENT-CONTENT.md's "The game's spells"):
    # Armor used a charge where any spell or blow landed on its wearer (7A557h, "je" past it
    # unless the target has Armor, 2), as well as where damage is taken (79A3Eh): the jump
    # always taken, so a damaging hit uses one charge and a friend's spell none ...
    Patch("armor_charge", 0x7A557, bytes.fromhex("740b"), bytes.fromhex("eb0b")),
    # ... a psionicist ending a maintained power removed each of its effects by the psionicist
    # and the effect's handle (5CEBDh), not by the creature it is on (Share Strength's on the
    # one it was shared with: another effect of the psionicist's went): pushed as the record's
    # owner and handle (ES:BX still the record), the slot looked at again after a removal (the
    # records move down), and only slots below the live count (DS:1E24h) looked at, not 192
    # (the body skipped past it, where the loop's top had already set ES:BX); the "mov ax,390h"
    # and the far call left where they were (their segments are fixed up) ...
    Patch("power_end_live", 0x5CF00, bytes.fromhex("8bde6bdb0a"), bytes.fromhex("3b36241e90")),
    Patch("power_end_skip", 0x5CF08, bytes.fromhex("8ec0"), bytes.fromhex("7d20")),
    Patch("power_end_handle", 0x5CF11, bytes.fromhex("8bde6bdb0a"), bytes.fromhex("26ffb70d01")),
    Patch("power_end_owner", 0x5CF19, bytes.fromhex("8ec0268a870d015057"),
          bytes.fromhex("26ffb70601") + b"\x90" * 4),
    Patch("power_end_again", 0x5CF27, bytes.fromhex("83c404"), bytes.fromhex("59594e")),
    Patch("power_end_count", 0x5CF2B, bytes.fromhex("81fec0007cbb"), bytes.fromhex("3b36241e7cbb")),
    # ... the preserver's Dispel Magic (spell 26) put "No spell use" (effect 50, which Dispel
    # Magic itself never ends) on all it caught, the cleric's none: its record's effect 0 ...
    Patch("dispel_effect", 0x422C9, bytes((50,)), bytes((0,))),
    # ... Cause Serious and Critical Wounds' damage was 2d9 and 3d9 (the Cure spells' 2d8+1 and
    # 3d8+3 as AD&D has them): their records' dice (+1Ch: steps' dice << 5 | the flat bonus a
    # step; +1Dh: base dice << 3 | caster levels a step; +1Eh: level adjustment << 4 | sides)
    # made 2d8 and 3d8, one step of +1 and +3 (a step for each 7 caster levels, the level
    # counted up to 10: always one) ...
    Patch("cause_serious", 0x42DAC, bytes.fromhex("001109"), bytes.fromhex("011708")),
    Patch("cause_critical", 0x42F8C, bytes.fromhex("001909"), bytes.fromhex("031f08")),
    # ... and Hold Undead held anything: where the game has just asked whether the target is
    # undead (7BE20h, AL), "or al,al / je +22h" (DSCLOG's NS_HOLD: Hold Undead on a living
    # target goes to the immunity's return, 7A1F0h)
    Patch("hold_undead", 0x7A333, bytes.fromhex("0ac07422"), _site(NS_HOLD, 4)),
    # ... and more of the game's own slips (DEVELOPMENT-CONTENT.md's "The game's spells"): Absorb Disease
    # (power 147) went on into Strength's handler (79470h), so the psionicist took the disease and
    # 1d6 STR too, and with no disease to take, the STR alone: both ways now jump to the end of
    # Strength's handler, its "or byte [si],2 / or byte [bp-15h],1 / jmp" (794ACh), past the effect
    Patch("absorb_no_strength", 0x79446, bytes.fromhex("7428"), bytes.fromhex("7464")),
    Patch("absorb_end", 0x7946D, bytes.fromhex("800c02"), bytes.fromhex("eb3d90")),
    # ... Bless and Aid leave out those of the caster's side with an enemy within 28 sixteenths, but
    # the routine (7B03Dh) measured from (x, x) of where each stands: its first push the y (+669Fh)
    Patch("bless_from_cell", 0x7B086, bytes((0x9D,)), bytes((0x9F,))),
    # ... the fire elementals' resistance classes (the monster kinds' table, 3E45h:00A8h + the
    # kind) were the wrong way round: the fire elemental (kind 32) hurt by +1 weapons (class 14) and
    # the lesser one (33) only by +2 and by fire (13). The fire elemental now class 15, which the
    # game has and no kind used (+2 weapons, nothing from fire), and the lesser one 14 (+1, nothing
    # from fire), as the clue book has them ...
    Patch("fire_elemental", 0x43918, bytes((14, 13)), bytes((15, 14))),
    # ... and Cloak of Bravery's +4 against fear (the save routine's 80F5:25A0h, Brave on the
    # target) asks for a flag no spell had (100h of a record's +11h word): set on the spells that
    # make one Afraid (effect 17): Scare, Fear, Cause Fear, Insect Plague
    *(Patch(f"brave_fear_{spell}", 0x42222 + (spell - 21) * 0x20, bytes((0x40,)), bytes((0x41,)))
      for spell in (21, 43, 78, 132)),
    # ... Negative Plane Protection saved as against Vampiric Touch, which allows none, so it never
    # stopped anything: "add sp,4 / push 6 / push 27h" (DSCLOG's NS_NPP: a save allowed) ...
    Patch("npp_save", 0x7A7E9, bytes.fromhex("83c4046a066a27"), _site(NS_NPP, 7)),
    # ... a thief skill for the whole party (801BDh: a trap's find/remove traps, GPL 28's hear
    # noise) was to go to the member with the best chance, but kept the lower, unsigned, of a best
    # that starts at 0: none was ever lower, so the first member rolled. "jna" made "jge": the
    # highest chance above 0 (one who can't, or isn't standing, has 0: the first then, as before)
    Patch("party_best", 0x80201, bytes.fromhex("7605"), bytes.fromhex("7d05")),
    # ... and an archer's pointer showed "can't shoot" (ICON 6006) after a shot that killed, with
    # shots left: the weapon attack routine (5883Ah) counts a combatant's attacks this round in a
    # byte (+181h of the round's tables, 37BDh) and makes it 63h (99) once all are made, and lets
    # another go while it is under 63h (58454h), but the pointer's missile test (1D5AEh) refused
    # any count but 0. "cmp byte es:[si+181h],0 / jnz" made "cmp ...,63h / jnl": as the attack
    Patch("shots_left", 0x1D657, bytes.fromhex("2680bc8101007505"), bytes.fromhex("2680bc8101637d05")),
    # ... and how many of a random monster come (REQUEST 8, 80BE4h; GPL 99 and 106): 2 x the
    # party's strength / the monster's, but its search left SI one past the slot found, so the
    # next slot's strength (the last slot's: the next record's first OJFF), and an empty one (the
    # slot after the last in regions 6, 13, 14, 27, 39, 40, 44 and 255) divided by 0 ("Divide error",
    # back to DOS). "idiv word es:[bx+4]" made [bx+0]: the slot found's own
    Patch("monster_count", 0x80CD8, bytes.fromhex("26f77f04"), bytes.fromhex("26f77f00")),
    # ... and the rest (8066Dh) killed the Poisoned even after the free Neutralize Poison of a druid of
    # 7th level or more: its pass 2 took each member's effects as a bitset (598:25h, 76944h, at
    # 8075Dh) before the free cures (809A2h: Cure Disease, Remove Curse, Remove Paralysis, Neutralize
    # Poison) and killed (1000 damage, 80963h) from that copy (seen in DOSBox 2026-11-09). The 7 casts
    # (near calls, no fixups) moved ahead of the read, their nops dropped: the loop's jump (80984h)
    # goes to the casts (80768h), which end with a jump to the read (80758h), which goes on past
    # them (80765h: "jmp 807EDh"). A disease cured at a rest gives STR back that rest too
    # (playtest/logs/2026-11-09-rest-order.asm)
    Patch("rest_cures_first", 0x80765, bytes.fromhex(
        "837ef0057c368a46f050ff76ea566a60900ee8280283c4088a46f050ff76ea566a67900ee8160283c4088a46f050ff76ea"
        "566a69900ee8040283c408837eee057c308a46ee5057566a60900ee8ee0183c4088a46ee5057566a67900ee8de0183c408"
        "8a46ee5057566a69900ee8ce0183c408837eee077c108a46ee5057566a76900ee8b80183c408"), bytes.fromhex(
        "e98500837ef0057c338a46f050ff76ea566a600ee8260283c4088a46f050ff76ea566a670ee8150283c4088a46f050ff76"
        "ea566a690ee8040283c408837eee057c2d8a46ee5057566a600ee8ef0183c4088a46ee5057566a670ee8e00183c4088a46"
        "ee5057566a690ee8d10183c408837eee077c0f8a46ee5057566a760ee8bc0183c408e96cff90")),
    Patch("rest_cures_loop", 0x80984, bytes.fromhex("e9d1fd"), bytes.fromhex("e9e1fd")),
    # ... and resting by the Loader's rule "rest_heal" (RULE_REST; each site the game's with it off): the
    # rest's first move, "mov word [bp-10h],0" (80675h), before any slot is refilled: the party's priests
    # and psionicists spend what they have left on the party (DSCLOG's REST_PRE); pass 2's hit points,
    # "mov [es:bx],ax" (808AFh): natural healing, not the most (REST_HP)
    Patch("rest_spells", 0x80675, bytes.fromhex("c746f00000"), _site(REST_PRE_SITE, 5)),
    Patch("rest_hp", 0x808AF, bytes.fromhex("268907"), _site(REST_HP_SITE, 3)),
    # ... and a fight's music: an attack that starts a fight asks for the music level the region
    # record gives its creature (62F75h, REQUEST 16): the creatures are words at +263h, their levels
    # bytes at +277h, but the level was read with the word's index ("mov bx,dx / shl bx,1"), so any
    # creature but the region's first got another's level or a byte past the list. The SHL made two
    # NOPs: the creature's own level (found by CalvinRodo's yuan-ti, checked in DSUN.EXE)
    Patch("fight_music", 0x62FC0, bytes.fromhex("d1e3b848038ec0"), bytes.fromhex("9090b848038ec0")),
    # Scare's save (the save modifiers' routine, 80F5:119Ch: spell 15h): a target of 6th level or
    # more always saves, and one below may save as usual only if a priest whose race is elf (3)
    # and half-elf (4) at once ("cmp race,3 / jne fail", then "cmp race,4 / je save"), so no one
    # could. The first test's jne to the fail made "je" to the save: an elf or half-elf priest
    # saves as usual (found by CalvinRodo's yuan-ti, checked in DSUN.EXE)
    Patch("scare_elves", 0x79FEA, bytes.fromhex("752c"), bytes.fromhex("7431")),
    # ... which never ran, nor the level rule before it: Scare's record (spell 21, its +1Fh, the
    # save's byte) had bit 0, "a save allowed", clear (A0h; Charm and Hold Person's A1h), and the
    # saving throw's routine (79A71h) answers "not saved" at its first test without it, so every
    # creature but the undead was Scared, a 7th-level fighter too (seen in DOSBox, 2026-11-08: no
    # save rolled). The bit set: the game's own rules above come into play
    Patch("scare_save", 0x4222F, bytes.fromhex("a0"), bytes.fromhex("a1")),
    # Spells as the manual has them (the Options tab's "Spells and psionics as the manual describes them",
    # SPELLS_MANUAL: skipped with it off). The spell records (spell s at 41F70h + 20h x s: +4 the
    # duration's dice, count low and sides high, +5 that a caster level, +7 the unit, 60 a round or
    # -1 charges or -9999 until removed; +12h's 80h a save negating the damage; +1Ch..+1Eh the
    # damage's dice; +1Fh the save, bit 0 one allowed). reports/spells-against-the-manual.md
    # Bestow Curse (104) and Blood Flow (108): "save negates", but no save was allowed
    Patch("bestow_curse_save", 0x42C8F, bytes.fromhex("a0"), bytes.fromhex("a1")),
    Patch("blood_flow_save", 0x42D0F, bytes.fromhex("a0"), bytes.fromhex("a1")),
    # Flaming Sphere (14): a save negates its 2d4, not halves it
    Patch("flaming_sphere_negates", 0x42142, bytes.fromhex("40"), bytes.fromhex("c0")),
    # Solid Fog (51): 1d3 rounds + 1 a caster level, not stuck until removed
    Patch("solid_fog_time", 0x425D4, bytes.fromhex("1000"), bytes.fromhex("3101")),
    Patch("solid_fog_rounds", 0x425D7, bytes.fromhex("f1d8"), bytes.fromhex("3c00")),
    # Minor Spell Turning (48): 3 rounds a caster level, not one spell turned and then none
    Patch("spell_turning_time", 0x42574, bytes.fromhex("1100"), bytes.fromhex("1003")),
    Patch("spell_turning_rounds", 0x42577, bytes.fromhex("ffff"), bytes.fromhex("3c00")),
    # Cause Fear (78): 1d4 rounds, not 1 a caster level
    Patch("cause_fear_time", 0x42934, bytes.fromhex("0001"), bytes.fromhex("4100")),

    # Quicksand (134): no save (its Stuck lasts a round and is put on again each round while the
    # quicksand lasts, a 5d3 of its own: the record's time changes nothing, seen in DOSBox)
    Patch("quicksand_no_save", 0x4304F, bytes.fromhex("a1"), bytes.fromhex("a0")),
    # Ironskin (133): a blow stopped a caster level, not 1d6 (its level divisor, +1Dh's low bits,
    # shared with the damage formula, made 1: it was 2; its damage stays none)
    Patch("ironskin_charges", 0x43014, bytes.fromhex("6100"), bytes.fromhex("1001")),
    Patch("ironskin_per_level", 0x4302D, bytes.fromhex("02"), bytes.fromhex("01")),
    # Turn Pebble to Boulder (53): 3d6+8 (11-26), not 6d6
    Patch("pebble_damage", 0x4262C, bytes.fromhex("003106"), bytes.fromhex("081f06")),
    # Melf's Minute Meteors (33): five globes of 1d4, each its own cast and landing (each rolling
    # to hit, +2, with spells that roll to hit: DSCLOG's TH_METEORS), not one of 1d4 a caster
    # level: +0's count (bits 2-7, Magical Stone's 3) made 5, the damage 1d4 whatever the level
    Patch("meteors_count", 0x42390, bytes.fromhex("06"), bytes.fromhex("16")),
    Patch("meteors_damage", 0x423AC, bytes.fromhex("200104"), bytes.fromhex("000904")),
    # Flame Arrow (28): a bolt of 1d6 + 4d6 fire (5d6) for every five caster levels, each its own
    # cast and landing (AD&D's), not one of 5d6 for every five levels: the damage 5d6 whatever the
    # level, the count the cast's tail reads (7567Fh, "mov dl,[es:bx]", the record's +0) one for
    # every five levels, at least one (DSCLOG's FLAME_SITE)
    Patch("flame_arrow_damage", 0x4230C, bytes.fromhex("a00506"), bytes.fromhex("002906")),
    Patch("flame_arrow_count", 0x7567F, bytes.fromhex("268a17"), _site(FLAME_SITE, 3)),
    # Turn Undead (190, the priests' button) by AD&D's turning table (DSCLOG's TURN_SITE): in the
    # game's routine (7ADB7h), where it works out its own number, "mov al,[es:bx+24h]" (7AE01h):
    # turned (Afraid, 3d4 rounds), destroyed, D* (2d4 more of the kind) or nothing, and a priest
    # who fails can't try that undead again that fight
    Patch("turn_undead_manual", 0x7AE01, bytes.fromhex("268a4724"), _site(TURN_SITE, 4)),
    # The saving throw (79A71h) compared its total with the number needed unsigned ("cmp al,[bp-1] /
    # jae", 79BBAh), so the save modifiers' -100 for "can't save" (Chaos's, Cloudkill's, Scare's below
    # 6th level, Color Spray's) made a negative total, read as 156 and up: always saved (seen in
    # DOSBox 2026-11-09: Arena Guards "unable to save" against Cloudkill took half its damage, a Guard
    # against Scare was never Afraid). The compare made signed ("jge"): -100 fails, +100 saves (Scare
    # from 6th level). Always applied (a fix of the game's, in no switch; the user's decision, 2026-11-09)
    Patch("save_signed", 0x79BBD, bytes.fromhex("73a6"), bytes.fromhex("7da6")),
    # ... and a natural 20, which the game took as saved before adding the modifiers (79B5Fh), saves
    # unless the save can't be made ("never save should be never save": the user, 2026-11-09): the
    # natural 20's test jumped over, so it goes on with the modifiers (DSCLOG's SAVE_SUM: the sum kept
    # in its byte, and the natural 20 made a save there, under the -100's). Always applied, as above.
    Patch("save_natural", 0x79B5F, bytes.fromhex("807e"), bytes.fromhex("eb09")),
    Patch("save_sum", 0x79B97, bytes.fromhex("8a56fe02d08856fe"), _site(SAVE_SUM_SITE, 8)),
    Patch("save_natural_saves", 0x79BB4, bytes.fromhex("0046fe"), _site(SAVE_NAT_SITE, 3)),
    # The item box's picture (DSUN.EXE 8C2F1h, called by the box alone): the number an item keeps
    # ("movsx eax,word [es:bx+0Ch]", 8C344h) or its object's icon ("movzx eax,word [bp-0Eh]", 8C384h,
    # then kept in the item) pushed for the load; DSCLOG's BOX_PICS pushes a tall weapon picture's
    # small copy instead (icons.BOX_TALL, BOX_SMALL), the item keeping its own number, so the box's
    # text starts as a 16-pixel picture's and its last row is inside it; the inventory and the ground
    # keep the picture. Always applied (the copies are in the Loader's SEGOBJEX.GFF whatever the Options)
    Patch("box_picture_item", 0x8C344, bytes.fromhex("66260fbf470c"), _site(BOX_PIC_ITEM_SITE, 6)),
    Patch("box_picture_object", 0x8C384, bytes.fromhex("660fb746f2"), _site(BOX_PIC_OBJECT_SITE, 5)),
    # The picture cache (DSUN.EXE 25FA6h: each WALL or BMP picture drawn has a slot of 300, given
    # back only when a region loads): with all taken a new picture had none and wasn't drawn (Wake of
    # the Ravager's "graphics disappear during play", the same engine's). DSCLOG's PIC_REUSE reuses a
    # slot out of memory that no wall or map thing names, the picture's store place the first gap it
    # fits. Always applied (a fix): below 300 slots the game's own way.
    Patch("pic_full", 0x26009, bytes.fromhex("813e841f2c0173bfa1841f"), _site(PIC_FULL_SITE, 11)),
    Patch("pic_place", 0x260CC, bytes.fromhex("c45efc"), _site(PIC_PLACE_SITE, 3)),
    Patch("pic_count", 0x2612B, bytes.fromhex("8b36841fff06841f"), _site(PIC_COUNT_SITE, 8)),
    Patch("pic_fail", 0x25FD0, bytes.fromhex("b8ffff"), _site(PIC_FAIL_SITE, 3)),
    # Cahulaks as Dark Sun's rules have them (the Loader's rule "cahulaks", RULE_CAHULAKS; each site the
    # game's with it off): the two-weapon adjustment's "two weapons ready?" (595ECh: "cmp word [bp+6],1 /
    # jle") on for them too; the attack's swing (589B6h, "mov word [bp-4],0": the off head's, the round's
    # last, its penalty); a weapon's hit that did damage (58B54h, "mov byte [bp-15h],0": the tangle).
    Patch("cahulaks_two", 0x59627, bytes.fromhex("837e06017e11"), _site(CAH_TWO_SITE, 6)),
    Patch("cahulaks_swing", 0x589B6, bytes.fromhex("c746fc0000"), _site(CAH_SWING_SITE, 5)),
    Patch("cahulaks_hit", 0x58B54, bytes.fromhex("c646eb00"), _site(CAH_HIT_SITE, 4)),
    # The creature size rule (RULE_SIZE): a weapon's damage line just drawn (7286Fh's "inc word [bp-2]"
    # at 72AA7h, the item box's and the inventory's): its dice against a large target with it.
    Patch("size_line", 0x72AA7, bytes.fromhex("ff46fe"), _site(SIZE_LINE_SITE, 3)),
    # ... and Shillelagh's line, about to be drawn ("push word [bp+12h]" at 72A8Ah): 1D6+1, AD&D's
    # against a smaller target, its 2D4 the large one.
    Patch("size_pre", 0x72A8A, bytes.fromhex("ff7612"), _site(SIZE_PRE_SITE, 3)),
    # AD&D's held target (RULE_HELD; each site the game's with it off): the attack's natural 20 test
    # (589E9h, "cmp word [bp-6],14h", before its JE to the hit), the hit on a helpless target too; and
    # what a helpless target takes (58B0Dh, "mov ax,[bp-4] / shl ax,1"), the damage, not x2.
    Patch("held_hit", 0x589E9, bytes.fromhex("837efa14"), _site(HELD_HIT_SITE, 4)),
    Patch("held_damage", 0x58B0D, bytes.fromhex("8b46fcd1e0"), _site(HELD_DAMAGE_SITE, 5)),
    # The monsters as the manual describes them (in the same switch; reports/group 4's research,
    # playtest/logs/2026-11-09-group-4-research.md). The kinds' properties: bit 15 a hit (the last
    # natural attack's) casting the priests' Poison (119), bit 24 the corroding touch, bit 25 disease
    # (184, 1 in 10), bit 31 a fire breath one turn in four (185, 3d6, a save halves). The Babau's and
    # the Blue Slaad's "deadly poison" in place of the corroding touch and the disease, which the
    # manual hasn't ...
    Patch("babau_poison", _kind(3), struct.pack("<I", 0x01400400), struct.pack("<I", 0x00408400)),
    Patch("blue_slaad_poison", _kind(17), struct.pack("<I", 0x12000400), struct.pack("<I", 0x10008400)),
    # ... kinds no creature of the game's has, for the Loader's copy of SEGOBJEX
    # (monsters.MANUAL_MONSTERS): the Styr's (38: its 3d6 fire breath; class 11 already, +1 weapons),
    # the Djinn's (39: nothing of its own; DSCLOG's DJINN_TURN its invisibility and images) and the
    # Tari's (40: disease, DSCLOG's TARI_BITE making it 1 in 20) ...
    Patch("styr_kind", _kind(38), struct.pack("<I", 0x00000601), struct.pack("<I", 0x80000400)),
    Patch("djinn_kind", _kind(39), struct.pack("<I", 0x00800020), struct.pack("<I", 0)),
    Patch("tari_kind", _kind(40), struct.pack("<I", 0x00000020), struct.pack("<I", 0x02000000)),
    Patch("tari_bite", 0x7A747, bytes.fromhex("3d0100"), _site(TARI_SITE, 3)),
    # ... the shadows "unaffected by cold-based attacks" (the greater shadow's, the manual's; the
    # shadow too, as AD&D's): class 4's first rule (0%) gets cold (4), and the greater shadow (kind 13)
    # class 4 for 11, whose 100% rule had any spell's damage hurt it in full (both: +1 weapons only)
    Patch("shadow_cold", KINDS_FILE + 0xD2 + 12 * 4, struct.pack("<H", 0x0139), struct.pack("<H", 0x013D)),
    Patch("greater_shadow_class", KINDS_FILE + 0xA8 + 13, bytes((11,)), bytes((4,))),
    # ... and their STR drain for the shadow's 2d6 cold and the greater shadow's paralysis (DSCLOG's
    # SHADOW_DRAIN), in the routine giving a hit's power (7A9A7h): "mov si,[bp+8] / mov al,[bp+0Ah]"
    Patch("shadow_drain", 0x7A9AB, bytes.fromhex("8b76088a460a"), _site(DRAIN_SITE, 6)),
    # Chill Touch (3): the game takes 1 STR off a creature that fails its save (Weakened, its handler's
    # tail, 79855h), but its record gave the effect no time (0 rounds), so it ended at once: an hour
    # (60 rounds; AD&D's lost Strength comes back a point an hour): +4..+8 "10 00 00 3C 00" made 1 x 3600
    Patch("chill_touch_time", 0x41F70 + 3 * 32 + 4, bytes.fromhex("1000003c00"), bytes.fromhex("110000100e")),
    # Blur (12): +1 on saves against magic, as Barkskin's, in the save modifiers (79D46h) at Barkskin's
    # test (79DC0h, "les bx,[bp+0Ah] / test byte [es:bx+7],2 / jz / inc si": DSCLOG's BLUR_SITE)
    Patch("blur_save", 0x79DC0, bytes.fromhex("c45e0a26f6470702740146"), _site(BLUR_SITE, 11)),
    # Fire Shield (44): +2 on saves against fire and cold (the caster already takes half from them,
    # 7B565h), at Protection from Cold's test (79E03h; DSCLOG's FSHIELD_SITE)
    Patch("fire_shield_save", 0x79E03, bytes.fromhex("f746fc0400740dc45e0a26f64704107403 83c603".replace(" ", "")),
          _site(FSHIELD_SITE, 20)),
    # Cloudkill (57): AD&D's bands by the level its saves count (HD_SAVE's: a classless creature's hit
    # dice): under 4 no save (the game's "6 or less", 79F95h: DSCLOG's CLOUD_SAVE_SITE), 4 or 5 a failed
    # save kills: the damage a thousand times over, at least 1000 as Slay Living's, where the spell's
    # damage keeps the save's answer (78DB6h: CLOUD_KILL_SITE); 6 and up the damage as before
    Patch("cloudkill_save", 0x79F95, bytes.fromhex("837e143975 09837efa067f0383ee64".replace(" ", "")),
          _site(CLOUD_SAVE_SITE, 15)),
    Patch("cloudkill_kills", 0x78DB6, bytes.fromhex("8846ff"), _site(CLOUD_KILL_SITE, 3)),
    # Lower Resistance (64): magic resistance 30% + 1% a caster level less (at least 0), the cast's
    # level kept in the effect (DSCLOG's ACID_ROUNDS), not halved; the cast's own check the same, the
    # two not added up (7A507h-7A527h: LOWRES_SITE)
    Patch("lower_resistance_manual", 0x7A507, bytes.fromhex(
        "f646f980740b8b46f4992bc2d1f88946f483fe40750b8a460ab400051e002946f4"), _site(LOWRES_SITE, 33)),
    # Strength (23) by the target's classes, AD&D's: warriors 1d8, priests, rogues and psionicists 1d6,
    # wizards 1d4; Cat's Grace (196) by the Tome of Magic's; a multiclass character's best die;
    # Adrenalin Control (the same code) 1d6: its "push dword 60001h" (79483h: DSCLOG's STRENGTH_SITE)
    Patch("strength_dice", 0x79483, bytes.fromhex("666801000600"), _site(STRENGTH_SITE, 6)),
    # Rainbow Pattern (50): 1 round a caster level (its record's +4 and +5: 1d3 rounds was), and
    # any damage to a creature it holds (its Paralyzed, told from Hold Person's by the effect's spell)
    # ends the hold: the start of the routine taking hit points off (585A2h: DSCLOG's RAINBOW_SITE)
    Patch("rainbow_pattern_time", 0x41F70 + 50 * 32 + 4, bytes.fromhex("3100"), bytes.fromhex("1001")),
    Patch("rainbow_pattern_damage", 0x585A2, bytes.fromhex("8b7e068b5608"), _site(RAINBOW_SITE, 6)),
    # Feeblemind (62): no psionic power works (it stopped spells only): the power check (5D59Dh), after
    # its test that the user has the power (5D5B4h: DSCLOG's PSI_SITE); Heal cures it (PROBE_CURE)
    Patch("feeblemind_psionics", 0x5D5B4, bytes.fromhex("0bc07505b000"), _site(PSI_SITE, 6)),
    # Biofeedback (psionic, effect 4): the game takes 2 off each blow (and any crushing, edged or
    # pointed damage) already, in its damage adjustments (79BF9h), but left none of a blow of 2 or
    # less: at least 1, as the manual's, at its "sub si,2" (79C83h: DSCLOG's BIO_SITE)
    Patch("biofeedback_least", 0x79C83, bytes.fromhex("83ee02"), _site(BIO_SITE, 3)),
    # Cell Adjustment (psionic 151): 1d4 HP, not 2 ("push 2 / jmp", 795A2h: DSCLOG's CELL_SITE); its
    # record already cures disease (effect -13)
    Patch("cell_adjustment_heal", 0x795A2, bytes.fromhex("6a02eb72"), _site(CELL_SITE, 4)),


    # Stinking Cloud (22): 1d4+1 rounds, not 1d6: the record's dice made 1d4, the round more by
    # DSCLOG's STINK_SITE in the time's routine (its dice are rolled with a bonus of 0)
    Patch("stinking_cloud_dice", 0x42234, bytes.fromhex("61"), bytes.fromhex("41")),
    Patch("stinking_cloud_round", 0x76D73, bytes.fromhex("c45efc"), _site(STINK_SITE, 3)),
    # Chaos (56): the save's -100 for anyone not a warrior (79F80h, "sub si,100") skipped for a
    # creature of INT 21 or more, or 4 or less, as the manual has it (DSCLOG's CHAOS_SITE)
    Patch("chaos_int", 0x79F80, bytes.fromhex("83ee64"), _site(CHAOS_SITE, 3)),
    # A classless creature (its sheet's classes, +21h..23h, all 0: an elemental, a slaad, Mastyrial,
    # the Rampager) has level 0 from the game's level routine (508h:2Ah, 5E85Fh), so Cloudkill,
    # Dismissal, Scare and Color Spray took it for a 0-level one: the save modifiers' target level,
    # "mov [bp-6],ax" (79D8Ch), made its hit dice (+24h) for it (DSCLOG's HD_SAVE)
    Patch("classless_save_level", 0x79D8C, bytes.fromhex("8946fa"), _site(HD_SAVE_SITE, 3)),
    # Color Spray (4): only creatures of more levels than the caster save, as in AD&D (-100 on
    # the save, as Chaos's and Cloudkill's): at Dismissal's test, "cmp word [bp+14h],3Ch / jnz"
    # (79F83h), which DSCLOG's SPRAY_SITE then makes itself
    Patch("color_spray_level", 0x79F83, bytes.fromhex("837e143c750c"), _site(SPRAY_SITE, 6)),
    # Hold Undead (31): only undead of no more levels (hit dice) than the caster's level, the
    # rest immune, at the undead's "test word [bp+0Eh],100h" (7A345h; DSCLOG's HOLD_HD, which
    # makes the test and its jump itself: the "hold_undead" patch above keeps it off the living)
    Patch("hold_undead_level", 0x7A345, bytes.fromhex("f7460e0001"), _site(HOLD_HD_SITE, 5)),
    # Spells that roll to hit (the Options tab's "Spells roll to hit", SPELL_TO_HIT: skipped with it
    # off). In the routine of what a spell (SI) does to thing DI (7A085h), after every immunity
    # check, "mov [bp-6],si" (7A15Ah), the spell kept for the dispatch on the table at 7A1A7h:
    # DSCLOG's SPELL_HIT rolls the caster's attack on the target for Acid Arrow, Turn Pebble to
    # Boulder, Magical Stone, Condense and the spines (180), and the touch spells on a creature of
    # another side, and on a miss puts Acid Arrow (12h) there: the table's "always hits" stub
    # (78BA0h, the overlay's first routine), its "mov ax,1" (78BA3h) DSCLOG's SPELL_STUB, then
    # answers 0, and the spell does nothing (7A0BEh)
    Patch("spell_hit", 0x7A15A, bytes.fromhex("8976fa"), _site(SPELL_HIT_SITE, 3)),
    Patch("spell_hit_stub", 0x78BA3, bytes.fromhex("b80100"), _site(SPELL_STUB_SITE, 3)),
    # Free Action (117), Remove Paralysis (105) and Protection from Paralysis (20) share one
    # handler (79406h, the spells' table at 79936h, their words at +4Ch): Slowed (47) removed, then
    # Paralyzed (34) unless the creature is Poisoned. Free Action frees the Stuck (51: Web, Solid
    # Fog, Quicksand, Entangle, Grease) too: the handler made a loop over the effects pushed on the
    # stack, through its two far calls (their segment words, which the overlay manager fixes up,
    # kept where they were), and Free Action's word pointed at a start that takes Stuck off first
    Patch("free_action_stuck", 0x79406, bytes.fromhex(
        "6a2f57" "9a4d009805" "83c404c45e0a268a4704b400a90800740 3e90b046a2257".replace(" ", "")),
        bytes.fromhex("579090" "9a4d009805" "5a583c22741cc45e0a26f6470408751 26a22ebe46a3357".replace(" ", ""))),
    Patch("free_action_loop", 0x7942A, bytes.fromhex("83c404e9fd03"), bytes.fromhex("5a586a2febd6")),
    Patch("free_action_word", 0x799A8, bytes.fromhex("6608"), bytes.fromhex("8208")),
    Patch("remove_paralysis_word", 0x799A0, bytes.fromhex("6608"), bytes.fromhex("8c08")),
    Patch("protection_paralysis_word", 0x79984, bytes.fromhex("6608"), bytes.fromhex("8c08")),
    # The least each score may be at creation (67399h, overlay code: for an ability, the highest
    # of the character's classes' least): the game raised each class's one prime requisite to 17
    # and every other score to one number a class (9 to 14), not the manual's requirements (a
    # gladiator's STR 13, DEX 12 and CON 15, nothing else; a druid's WIS 12 and CHA 15...). The
    # routine rewritten with the manual's table, 3 for none: dos/least_scores.asm (built with nasm
    # into these bytes, test_least_scores). Its two "mov dx,338h" stay at +1Eh and +42h, where the
    # overlay manager fixes up the segment as it loads the code.
    Patch("least_scores", 0x67399, bytes.fromhex(
        "558bec56578b7e0633f633c93bcf7d52c41e9c1103d9268a4721986bc003ba38038bd88ec2268b8780013b4608"
        "7505ba1100eb23c41e9c1103d9268a4721986bc003ba3803bb800183c30203c38bd88ec2268a07988bd03bd67e"
        "028bf2413bcf7cae8bc65f5e5dcb"), bytes.fromhex(
        "5589e5568a4e08c0e102b5038b6e06e800005e4d7825c41e9c1101eb9090ba3803268a4721986bd8032e668b40"
        "3066d3e8240f38e876dc88c5ebd888e8985e5dcb90ba38030000090000fc090000cd0f0000900000cb0fdd0e0e"
        "9000009090909090909090909090")),
    # ... and a berserk or confused party member kept the side its last turn rolled: "jmp 788BBh",
    # where an effect's end has no case of its own (DSCLOG's NS_SIDE: a charm's, the side put back)
    Patch("side_back", 0x78785, bytes.fromhex("e93301"), _site(NS_SIDE, 3)),
    # ... and the computer's casting gave a spell's two points both the chosen cell's middle, so its
    # walls were a single point: the four pushes (DSCLOG's NS_WALL: a wall across the line of fire)
    Patch("ai_wall", 0x5A38C, bytes.fromhex("8b46fcc1e004050800508b46fec1e004050800508b46fcc1e00405080050"
                                            "8b46fec1e00405080050"), _site(NS_WALL, 0x28)),
    # ... and a shop's magic items didn't shine: the map's main loop turns the palette's colour
    # cycles; a shop (opened from a conversation) runs a loop of its own and waits in the game's
    # wait for an event. The wait's test, "or di,di / jz 084Fh", and the shop's loop's, "cmp word
    # [11B2h],1" (DSCLOG's SHOP_SHINE, SHOP_LOOP: the cycles turned when due, a shop open)
    Patch("shop_shine", 0x2AFA6, bytes.fromhex("0bff74b5"), _site(SHOP_SHINE, 4)),
    Patch("shop_loop", 0x7DE11, bytes.fromhex("833eb21101"), _site(SHOP_LOOP, 5)),
    # Detonate's blast on an item (7AAEBh) left nothing in the dice log: "mov dx,0Fh / sub dx,ax",
    # the number its d20 must be under (DSCLOG's DET_ITEM: the check recorded, the game's rule kept)
    Patch("detonate_item", 0x7AB95, bytes.fromhex("ba0f002bd0"), _site(DET_ITEM, 5)),
    # ... and the kinds of a spell's damage a creature is guarded from, which halves a spell all of
    # those kinds (DSCLOG's WANDER_DMG: a Wanderer's fire and cold, as Resist Fire and Resist Cold)
    Patch("wanderer_damage", 0x7B56F, bytes.fromhex("857e0c"), _site(WANDER_DMG, 3)),
    # Dual-classing (the Loader's rule "dual_class", RULE_DUAL_CLASS; each site does the game's compare
    # with it off: DSCLOG's DUAL_LEVEL, DUAL_PRIMES): the level DUAL needs, "cmp byte [es:bx+24h],2" in
    # the two portrait menus (70CE4h, 70F03h) and the DUAL window's class test (86F58h), 3 with the
    # rule (the manual's third level) ...
    Patch("dual_level_menu", 0x70CE4, bytes.fromhex("26807f2402"), _site(DUAL_LEVEL_SITE, 5)),
    Patch("dual_level_view", 0x70F03, bytes.fromhex("26807f2402"), _site(DUAL_LEVEL_SITE, 5)),
    Patch("dual_level_window", 0x86F58, bytes.fromhex("26807f2402"), _site(DUAL_LEVEL_SITE, 5)),
    # ... and the class test's prime requisites (86E94h), "cmp byte [es:bx+22h],0Fh" for the old class's
    # one (86EFCh) and "...,11h" for the new class's (86F31h): with the rule every prime requisite the
    # manual gives the class, 15 or more for the old, 17 or more for the new
    Patch("dual_old_prime", 0x86EFC, bytes.fromhex("26807f220f"), _site(DUAL_OLD_SITE, 5)),
    Patch("dual_new_prime", 0x86F31, bytes.fromhex("26807f2211"), _site(DUAL_NEW_SITE, 5)),
    # a script's REQUEST (command 22h), its number read: recorded for the dice log (DSCLOG's REQ_SITE)
    Patch("script_request", 0x7FF42, bytes.fromhex("8b5e064b"), _site(REQ_SITE, 4)),
    # a click taking a readied spell's target, the aim check's answer: a refusal recorded (DSCLOG's AIM_SITE)
    Patch("spell_aim", 0x8455B, bytes.fromhex("83faff"), _site(AIM_SITE, 3)),
    # a creature's magic resistance against a spell, before the test for none: an Amulet of Magic
    # Resistance worn at the neck adds its 15% (DSCLOG's AMULET_MR; worldgear.py)
    Patch("amulet_resistance", 0x7A4FD, bytes.fromhex("837ef400"), _site(AMULET_SITE, 4)),
    Patch("arrow_hit", 0x58B63, bytes.fromhex("26807f0f00"), _site(ARROW_HIT_SITE, 5)),
    Patch("arrow_spell", 0x58B78, bytes.fromhex("268a4f0f"), _site(ARROW_SPELL_SITE, 4)),
    Patch("arrow_level", 0x58BE6, bytes.fromhex("6a068ac1b40050"), _site(ARROW_LEVEL, 7)),
    Patch("scroll_use", 0x6D3B9, bytes.fromhex("26854710"), _site(SCROLL_USE, 4)),
    Patch("box_said", 0x8B815, bytes.fromhex("83c404"), _site(BOX_SAID, 3)),
    Patch("line_said_6E125", 0x6E125, bytes.fromhex("83c40a"), _site(LINE_SAID, 3)),
    Patch("line_said_891A4", 0x891A4, bytes.fromhex("83c40a"), _site(LINE_SAID, 3)),
    Patch("line_said_89222", 0x89222, bytes.fromhex("83c40a"), _site(LINE_SAID, 3)),
    Patch("line_said_89552", 0x89552, bytes.fromhex("83c40a"), _site(LINE_SAID, 3)),
    Patch("line_said_8968B", 0x8968B, bytes.fromhex("83c40a"), _site(LINE_SAID, 3)),
    Patch("line_said_8A940", 0x8A940, bytes.fromhex("83c40a"), _site(LINE_SAID, 3)),
    Patch("line_cleared_6C9BF", 0x6C9BF, bytes.fromhex("83c406"), _site(LINE_CLEARED, 3)),
    Patch("line_cleared_701C2", 0x701C2, bytes.fromhex("83c406"), _site(LINE_CLEARED, 3)),
    Patch("line_cleared_89595", 0x89595, bytes.fromhex("83c406"), _site(LINE_CLEARED, 3)),
    # the routine casting a spell or a power, its caster read: recorded (DSCLOG's CAST_SITE)
    Patch("spell_cast", 0x772AA, bytes.fromhex("8b4e06"), _site(CAST_SITE, 3)),
    # the game's rest (its REST and a script's request 1, past "NO RESTING DURING COMBAT"), each
    # member's turn as their slots refill: recorded as request 0 (DSCLOG's REST_SITE)
    Patch("game_rest", 0x806C3, bytes.fromhex("8bc66bc03a"), _site(REST_SITE, 5)),
    # a one-target spell's rolled damage stored (76175h: SI the target, DI the spell): Harm's all the
    # target's hit points but 1d4; Wall of Thorns' 8 + AC (DSCLOG's HARM_SITE)
    Patch("harm_damage", 0x761A9, bytes.fromhex("8946fa"), _site(HARM_SITE, 3)),
    # the start of the one-target spell damage, which lasting areas deal at each creature's turn:
    # mov si,[bp+6] (DSCLOG's WW_GATE: Whirlwind's only once a round, at its start, and as cast)
    Patch("ww_gate", 0x7617D, bytes.fromhex("8b7606"), _site(WW_SITE, 3)),
    # ... and where the routine dealing a spell's damage to the creatures it reaches (7511Bh: DI the
    # spell; a touch spell's too) has rolled it: a Wilderness Avenger's Cause Wounds 1 more a die
    # (DSCLOG's AREA_DMG and HARM_SITE's AV_CAUSE)
    Patch("area_damage", 0x754EC, bytes.fromhex("8946ee"), _site(AREA_DMG, 3)),
    # the game's own code reading a ground picture's entry from its table, "mov ax,3C81h / mov es,ax
    # / mov al,es:[bx+2]": "cmp ax,3C81h" (the segment's word kept, as DOS fixes it up) and the
    # site, AX and ES the table's segment where DSCLOG has moved it (with an entry each for Blade
    # Barrier, Wall of Thorns, Fire Seeds and Whirlwind: DSCLOG's SEG_MOVE, AREA_SITE)
    # Acid (Acid Arrow's) burning each round: in the routine adding an effect, "cmp dword
    # [bp+0Eh],-9999" (its time), an Acid's seconds made rounds as charges, which the game spends a
    # turn at a time; at the burn's start, "mov si,[bp+6]"; where a spell's damage puts its effect
    # on, "cmp word [bp-1Eh],0": none during a burn; where a round starts, "cmp word [55Ah],0",
    # each creature's Acid spent; at the start of the routine spending charges, "mov di,[bp+6]":
    # Acid's spent only then (DSCLOG's ACID_ROUNDS, ACID_BURN, ACID_ONCE, ACID_ROUND, ACID_USE)
    Patch("acid_rounds", 0x76525, bytes.fromhex("66817e0ef1d8ffff"), _site(ACID_SITE, 8)),
    Patch("acid_burn", 0x78982, bytes.fromhex("8b7606"), _site(BURN_SITE, 3)),
    Patch("acid_once", 0x78DEF, bytes.fromhex("837ee200"), _site(ONCE_SITE, 4)),
    Patch("acid_use", 0x76808, bytes.fromhex("8b7e06"), _site(USE_SITE, 3)),
    Patch("acid_round", 0x5741D, bytes.fromhex("833e5a0500"), _site(ROUND_SITE, 5)),
    # Sunstroke's heat, burnt each round through Acid's burn: at the start of a spell's damage on a
    # creature, "mov si,[bp+0Ah]" (the spell), its spell, kind and a helpless creature's damage
    # made Sunstroke's (DSCLOG's HEAT_SITE)
    Patch("sun_heat", 0x78C24, bytes.fromhex("8b760a"), _site(HEAT_SITE, 3)),
    # a thing on the map about to be drawn: of a lasting area's copies of Whirlwind's funnel, only
    # one, at their middle (DSCLOG's DRAW_SITE)
    Patch("whirl_draw", 0x232D4, bytes.fromhex("be00008b470f"), _site(DRAW_SITE, 6)),
    # scenes and logos (the intro's too): the mouse driver's pointer shown, a click ending the scene
    # as a key does, and hidden at the scenes' end (DSCLOG's CINE_STEP, CINE_END)
    Patch("cine_step", 0x92A28, bytes.fromhex("0bd2740d"), _site(CINE_STEP, 4)),
    Patch("cine_end", 0x56BBE, bytes.fromhex("0bf67406"), _site(CINE_END, 4)),
    # the pointer starts in the middle of the screen, not at its right edge, and moves as far up and
    # down as across, from the game's start (DSCLOG's MOUSE_SET, MOUSE_INIT)
    Patch("mouse_set", 0x2A912, bytes.fromhex("c7062da10000"), _site(MOUSE_SET, 6)),
    Patch("mouse_init", 0x356F5, bytes.fromhex("0bc0750b"), _site(MOUSE_INIT, 4)),
    # a game loaded with the party in one figure: "mov word [1168h],0" in the loading routine, and
    # the whole party put in view on the map as 5 does (DSCLOG's SPREAD_LOAD)
    Patch("party_spread", 0x692CE, bytes.fromhex("c70668110000"), _site(SPREAD_SITE, 6)),
    # ... and the end of the routine putting it in one figure, after a fight too (not after 6:
    # DSCLOG's SPREAD_GATHER)
    Patch("party_gather", 0x1DFE8, bytes.fromhex("c70668110000"), _site(GATHER_SITE, 6)),
    # the game's flip of its two screens (0980:5814): "mov ax,0A000h / cmp word [118Eh],0", where the
    # screen to show is set and the VGA not yet told; the combat log's panel put on it first, if it
    # is on the screen shown now (DSCLOG's FLIP_SITE: else the panel went from the screen at a flip)
    Patch("panel_flip", 0x14444, bytes.fromhex("b800a0833e8e1100"), _site(FLIP_SITE, 8)),
    # a backstab: in the attack, "cmp word [bp+16h],1" just after the damage's roll (its dice kept),
    # and the multiplying (only the dice with RULE_BACKSTAB: DSCLOG's STAB_ROLL, STAB_TIMES)
    Patch("stab_roll", 0x58A29, bytes.fromhex("837e1601"), _site(STAB_SITE, 4)),
    Patch("stab_times", 0x58A80, bytes.fromhex("508b46fc5af7ea8946fc"), _site(TIMES_SITE, 10)),
    # Enlarge on a melee hit (7C211h, after STR's bonus): the damage x (100 + 10 a level)%, only the
    # weapon's dice with RULE_ENLARGE (DSCLOG's ENL_SITE)
    Patch("enlarge_dice", 0x7C246, bytes.fromhex("6bc00a660fbfc06683c064660fbfd6660fafc266bb640000006699"
                                                 "66f7fb8bf0"), _site(ENL_SITE, 32)),
    # a party member with CON 20 or more regenerating (227E5h), after its "div ebx" by 300 seconds:
    # AD&D's rate by CON with RULE_CON (DSCLOG's REGEN_SITE); and CON's adjustment to the
    # paralysis/poison/death save (5EA91h), none for a dwarf or a halfling with it (CON_SAVE)
    Patch("regen_rate", 0x228BF, bytes.fromhex("8bd16bd23a"), _site(REGEN_SITE, 5)),
    Patch("con_save", 0x5EAA1, bytes.fromhex("8bd88a871008"), _site(CON_SITE, 6)),
    *(Patch(f"area_table_{n}", offset, bytes.fromhex("b8813c8ec0268a870200"),
            bytes.fromhex("3d813c") + _site(AREA_SITE, 7))
      for n, offset in enumerate((0x23D32, 0x23D65, 0x23EBD, 0x23EF0, 0x28092, 0x280C6))),
    # A thief's Pick Pockets button (DSCLOG's PICK POCKETS; pickpocket.py): in the USE screen's
    # routine showing the Turn Undead button, "cmp word [9B82h],0" (the element: 0, none); in
    # the button's handler, "cmp word [9CDCh],0" (pressed) as it is let go of, "mov ax,[9CDEh]"
    # once the screen is closed (the menu button lit with its icon) and "push dword 0BEFFFFh"
    # (Turn Undead readied); at the start of the routine of a click on the map with
    # the pointer for talking, "mov si,[bp+6]" (the thing clicked on)
    Patch("pp_show", 0x89979, bytes.fromhex("833e829b00"), _site(PP_SHOW, 5)),
    Patch("pp_click", 0x8959B, bytes.fromhex("833edc9c00"), _site(PP_CLICK, 5)),
    Patch("pp_lit", 0x895F2, bytes.fromhex("a1de9c"), _site(PP_LIT, 3)),
    # ... and its name under the screen ("push ds / push 3262h", "TURN UNDEAD"), as the pointer is
    # on it and on a right click, and the description of its spell on the right click
    Patch("pp_text_hover", 0x89541, bytes.fromhex("1e686232"), _site(PP_TEXT, 4)),
    Patch("pp_text_info", 0x8967A, bytes.fromhex("1e686232"), _site(PP_TEXT, 4)),
    Patch("pp_info", 0x8968E, bytes.fromhex("a1de9c"), _site(PP_INFO, 3)),
    # ... and its frame lit as the pointer comes onto it and put back as it leaves, at the button's
    # own place ("push word [30F8h]", Turn Undead's, to "push word [bp-2]", the button's, as its
    # press already has it): the buttons beside it, which share its handler, light themselves
    Patch("pp_light_on", 0x89528, bytes.fromhex("ff36f830"), bytes.fromhex("ff76fe90")),
    Patch("pp_light_off", 0x8956F, bytes.fromhex("ff36f830"), bytes.fromhex("ff76fe90")),
    # ... a cleric/thief's purse beside Turn Undead, its icon let go of where the screen, closing,
    # lets go of Turn Undead's ("cmp dword [30F4h],0")
    Patch("pp_close", 0x88504, bytes.fromhex("66833ef43000"), _site(PP_CLOSE, 6)),
    Patch("pp_arm", 0x89610, bytes.fromhex("6668ffffbe00"), _site(PP_ARM, 6)),
    Patch("pp_hand", 0x5ECD8, bytes.fromhex("8b7606"), _site(PP_HAND, 3)),
    # The name table (GPLDATA's NAME chunk), loaded as the game starts and as a game is loaded:
    # the memory reserved for it, "push dword 1" before the size (DSCLOG adds room for more
    # names) ...
    Patch("names_size_start", 0x56676, bytes.fromhex("666a01"), _interrupt(VEC_NAMES_SIZE, 3)),
    Patch("names_size_load", 0x6A5A2, bytes.fromhex("666a01"), _interrupt(VEC_NAMES_SIZE, 3)),
    # ... and the "add sp,0Ch" after reading it in (DSCLOG copies its names after the game's)
    Patch("names_fill_start", 0x566AD, bytes.fromhex("83c40c"), _interrupt(VEC_NAMES_FILL, 3)),
    Patch("names_fill_load", 0x6A5D6, bytes.fromhex("83c40c"), _interrupt(VEC_NAMES_FILL, 3)),
    # where an attack is worked out from behind / a backstab: a hidden thief's is (RULE_STEALTH)
    Patch("stealth", 0x58353, bytes.fromhex("ff76e6"), _interrupt(VEC_STEALTH, 3)),
    # the item types (IT1R), read in just before the names: room for the Loader's own
    Patch("types_size_start", 0x56618, bytes.fromhex("666a01"), _interrupt(VEC_TYPES_SIZE, 3)),
    Patch("types_size_load", 0x6A54A, bytes.fromhex("666a01"), _interrupt(VEC_TYPES_SIZE, 3)),
    Patch("types_fill_start", 0x56647, bytes.fromhex("83c40c"), _interrupt(VEC_TYPES_FILL, 3)),
    Patch("types_fill_load", 0x6A579, bytes.fromhex("83c40c"), _interrupt(VEC_TYPES_FILL, 3)),
    # the class level cap (9, or 10 with the rule): "cmp byte es:[bx+24h],9" where a character
    # goes up a level, and where View Character shows the XP for the next one
    Patch("level_up", 0x87BE6, bytes.fromhex("26807f2409"), _interrupt(VEC_LEVEL, 5)),
    Patch("level_next", 0x67D08, bytes.fromhex("26807f2409"), _interrupt(VEC_LEVEL, 5)),
    # a thief's hit dice up to 10th with that rule: "mov al,es:[bx+1]" where a new level's hit
    # points are a roll or the fixed gain, "cmp al,es:[bx+1]" where CON's bonus is counted
    Patch("hd_roll", 0x872DE, bytes.fromhex("268a870100"), _interrupt(VEC_HD_ROLL, 5)),
    # the thief skills' equipment penalty: the list of slots where anything brings it (words,
    # ended by 13: the legs, the quiver and both hands) made empty, so nothing does
    Patch("thief_slots", 0x44F70, bytes.fromhex("060001000a0003000d00"), bytes.fromhex("0d000d000d000d000d00")),
    Patch("hd_con", 0x87779, bytes.fromhex("263a870100"), _interrupt(VEC_HD_CON, 5)),
    # a thief skill: base + race + 4 a level, "mov ax,si / shl ax,2 / add dx,ax / mov si,dx"
    # (DSCLOG does it, or with the rule AD&D's table and Dark Sun's DEX adjustment, then "jc"
    # past the game's DEX formula to its armour and effects at 80386h)
    # putting a weapon in a hand on the inventory screen: "test byte es:[bx+0Fh],40h", the
    # two-handed bit, of the other hand's weapon and of the one going in (DSCLOG answers "not
    # two-handed" for a half-giant with the rule on)
    Patch("two_handed_other", 0x6F33F, bytes.fromhex("26f6470f40"), _interrupt(VEC_TWO_HANDED, 5)),
    Patch("two_handed_new", 0x6F3CC, bytes.fromhex("26f6470f40"), _interrupt(VEC_TWO_HANDED, 5)),
    # a spell's description read in (RESOURCE.GFF's SPIN chunk) for its box: "add sp,0Ch" after the
    # read (DSCLOG makes Flaming Sphere's Cat's Grace's with that rule)
    # the two routines that load a GFF chunk (type, number): their stack check "cmp [9Ch],sp"
    # (DSCLOG does it, and asks for Cat's Grace's icon in Flaming Sphere's place with that rule)
    Patch("chunk_load", 0x29EA7, bytes.fromhex("39269c00"), _interrupt(VEC_CHUNK_ID, 4)),
    Patch("chunk_find", 0x29E37, bytes.fromhex("39269c00"), _interrupt(VEC_CHUNK_ID, 4)),
    Patch("spell_text", 0x8C74F, bytes.fromhex("83c40c"), _interrupt(VEC_SPELL_TEXT, 3)),
    # shadows (DSCLOG's SHADOWS): the start, "push bp / mov bp,sp / sub sp,N", of the routines
    # drawing the floor of the map's view and of a rectangle of it (the shadows go on it after),
    # and of the one drawing a rectangle of the view again (made to reach as far as shadows do)
    Patch("floor_all", 0x2700E, bytes.fromhex("558bec83ec1c"), _interrupt(VEC_FLOOR_ALL, 6)),
    Patch("floor_rect", 0x27162, bytes.fromhex("558bec83ec1e"), _interrupt(VEC_FLOOR_RECT, 6)),
    Patch("redraw", 0x2475F, bytes.fromhex("558bec83ec08"), _interrupt(VEC_REDRAW, 6)),
    # ... and where the routine drawing again what moved starts to, its rectangle made:
    # "push word [bp+8] / push word [bp+6]"
    Patch("redraw_all", 0x24B18, bytes.fromhex("ff7608ff7606"), _interrupt(VEC_REDRAW_ALL, 6)),
    # the combat log's panel under the pointer (DSCLOG's PROBE_POINTER): the stack check, "cmp
    # [9Ch],sp", of the routine that draws the game's pointer (28D1:093D)
    Patch("pointer", 0x2EA55, bytes.fromhex("39269c00"), _interrupt(VEC_POINTER, 4)),
    # scrolling (DSCLOG's SCROLLING): the main loop asking where the pointer is, "call far
    # 3118:002E", its first 3 bytes (the segment after them is relocated as the game loads: A9h
    # makes the 5 a "test ax,<segment>", which DSCLOG returns past)
    Patch("scroll", 0x1CAAC, bytes.fromhex("9a2e00"), bytes((0xCD, VEC_SCROLL, 0xA9))),
    # a thing on the map drawn ("call far 1A0A:3180" in its routine, 25E0Ch; DI the thing): a hidden
    # or invisible one drawn see-through by DSCLOG (PROBE_GHOST), back past the call's segment
    Patch("ghost", 0x25EBE, bytes.fromhex("9a8031"), bytes((0xCD, VEC_GHOST, 0x90))),
    # targeting (DSCLOG's TARGETING): the start, "push bp / mov bp,sp / sub sp,10h", of the routine
    # that finds the thing under the pointer
    Patch("hit", 0x25B52, bytes.fromhex("558bec83ec10"), _interrupt(VEC_HIT, 6)),
    # the end of the routine filling an item's box: a cloak's or boots' bonus to hiding, moving silently
    Patch("item_box", 0x8C1A1, bytes.fromhex("6a00"), _interrupt(VEC_ITEM_BOX, 2)),
    # the end of the game's thief skill routine: mov ax,si (DSCLOG adds a worn belt's bonus to
    # picking pockets and opening locks)
    Patch("belt", 0x803B2, bytes.fromhex("8bc6"), _interrupt(VEC_BELT, 2)),
    # the save/load window's events, where a key it has no use for goes to its end: jmp (DSCLOG
    # shows the next page of ten saves for PgDn, the one before for PgUp, then goes there)
    Patch("save_page", 0x74901, bytes.fromhex("e9e804"), _interrupt(VEC_SAVE_PAGE, 3)),
    # ... and Enter taken out of the window's key table (the overlay's CS:B28h, its first key Esc
    # at B26h), so it comes there too: DSCLOG goes on to LOAD (as the table did) unless the row
    # chosen in the load window has no save, as on an empty page (where the game would start a
    # new game)
    Patch("save_enter", 0x74E28, bytes.fromhex("0d1c"), bytes.fromhex("ffff")),
    # ... and where a click on a button it doesn't know goes to its end: jmp (DSCLOG: PAGE 1 to
    # PAGE 4, savepages.py)
    Patch("save_click", 0x74B9F, bytes.fromhex("e94302"), _interrupt(VEC_SAVE_CLICK, 3)),
    Patch("thief_skill", 0x80307, bytes.fromhex("8bc6c1e00203d08bf2"),
          bytes((0xCD, VEC_THIEF_SKILL, 0x72, 0x80386 - 0x8030B)) + b"\x90" * 5),
    # a bug of the game's own (DSUN.EXE 1DF3:142F, which makes two child pages of the view, frees
    # them after): when the first can't be made, "jz" went to the freeing with the second's number
    # never set, and the page routine was handed whatever was on the stack. Its size, read from past
    # the pages' table, took the top of video memory's pages down into the game's code, the next
    # pages were made there, and the game crashed (the opening fight, "Null pointer assignment").
    # Now the first failing goes past both frees (the first is -1: nothing to free)
    Patch("page_free", 0x248B3, bytes.fromhex("743b"), bytes.fromhex("7459")),
    # the scripts' buffer (one: a script called from another is read in over it): "push dword
    # 10000", its size, as it is allocated. A script of 9800 bytes ran, one of 10000 ended with
    # "BAD GPL EXIT" (the game's largest is 9792); the Trustee's, with the questions about
    # Kalzith and Semyon, alive and dead (pensasks.py), is 11000 and some
    Patch("script_buffer", 0x6A692, bytes.fromhex("666810270000"),
          bytes.fromhex("6668") + struct.pack("<I", SCRIPT_BUFFER)),
    # The Effects screen: a click on an effect's icon ends it (DSUN.EXE 7F19Dh, its handler for the
    # selected character's effects, then the game's routine ending an effect). Only a psionic
    # power's effect (spell 8Ah-ABh, which it stops maintaining) still ends so; a spell's is left
    # on: its two "not a psionic power" jumps (to the ending) go to the handler's way out instead.
    Patch("effects_click_low", 0x7F226, bytes.fromhex("7c51"), bytes.fromhex("7c73")),
    Patch("effects_click_high", 0x7F236, bytes.fromhex("7d41"), bytes.fromhex("7d63")),
    # The saved characters: CHARSAVE.GFF holds each under a number, 1 to 19, and the game's
    # loops over them stop at 20 (each "cmp ...,14h" or "push 14h" a byte); its roster list is
    # made 20 long and its "too many characters" check is for 19 found. The file's own writing
    # takes any number, the roster window scrolls by the number read and party members are
    # found by their own tags, so these are all that hold it at 19.
    Patch("characters_list", 0x53CD1, bytes.fromhex("666a14"), bytes((0x66, 0x6A, CHARACTERS + 1))),
    Patch("characters_read", 0x53D02, bytes.fromhex("6a14"), bytes((0x6A, CHARACTERS + 1))),
    Patch("characters_reread", 0x543B0, bytes.fromhex("6a14"), bytes((0x6A, CHARACTERS + 1))),
    Patch("characters_roster", 0x53F43, bytes.fromhex("83fe14"), bytes((0x83, 0xFE, CHARACTERS + 1))),
    Patch("characters_delete", 0x54B59, bytes.fromhex("83fe14"), bytes((0x83, 0xFE, CHARACTERS + 1))),
    Patch("characters_save", 0x6692E, bytes.fromhex("83ff14"), bytes((0x83, 0xFF, CHARACTERS + 1))),
    Patch("characters_join", 0x67094, bytes.fromhex("837efc14"), bytes((0x83, 0x7E, 0xFC, CHARACTERS + 1))),
    Patch("characters_joined", 0x6709F, bytes.fromhex("837efc14"), bytes((0x83, 0x7E, 0xFC, CHARACTERS + 1))),
    Patch("characters_count", 0x67CBF, bytes.fromhex("83fe14"), bytes((0x83, 0xFE, CHARACTERS + 1))),
    Patch("characters_full", 0x67CC9, bytes.fromhex("83ff13"), bytes((0x83, 0xFF, CHARACTERS))),
    # Items saving against the acid and corroding touch (the game's special attacks 178, 186
    # and 187): where the weapon's routine works out the number its d20 must reach, "mov dx,8 /
    # sub dx,[bp-2]" (DSCLOG gives the easier of the game's and AD&D's, and records the check);
    # where the armour's skips the roll for armour with no magical power, "cmp word [bp-2],0"
    # (before its "jz"); and where it works out the number, "mov dx,0Ah / sub dx,[bp-2]"
    Patch("item_weapon", 0x7AABC, bytes.fromhex("ba08002b56fe"), _interrupt(VEC_ITEM_WEAPON, 6)),
    Patch("item_skip", 0x7AC45, bytes.fromhex("837efe00"), _interrupt(VEC_ITEM_SKIP, 4)),
    Patch("item_armour", 0x7AC59, bytes.fromhex("ba0a002b56fe"), _interrupt(VEC_ITEM_ARMOUR, 6)),
    # the scripts' random command (0 to N): "inc eax / mov edx,eax", N in EAX (DSCLOG records the
    # result, N and the script's position: the junk, haystack and wardrobe searches, search.py)
    Patch("script_rand", 0xB300, bytes.fromhex("6640668bd0"), _interrupt(VEC_SCRIPT_RAND, 5)),
    # View Character's "EXP:10301 (16000)": "push 10F4h", the ")" after the next level's XP (DSCLOG
    # puts the class whose next level it is before it, for more than one class: "(16000 F)")
    Patch("xp_next", 0x67DBE, bytes.fromhex("68f410"), _interrupt(VEC_XP_NEXT, 3)),
    # weapon specialization, in the routine that makes a weapon attack: "cbw / mov [bp-8],ax",
    # its attacks a round (AD&D's plain rate for a warrior's weapon of a kind not chosen, one
    # more for grand mastery; and the to-hit bonus), and "add [bp-12h],ax", the strength bonus
    # added to its damage bonus (the damage bonus, and grand mastery's larger die)
    Patch("attacks", 0x58892, bytes.fromhex("988946f8"), _interrupt(VEC_ATTACKS, 4)),
    Patch("spec_damage", 0x588F2, bytes.fromhex("0146ee"), _interrupt(VEC_SPEC_DAMAGE, 3)),
    # ... and the same on the "DAM: 1.5x1D8+4" line (View Character, the inventory screen): its
    # "mov al,es:[bx+2Ah]", with the bonus, sides and count already pushed
    Patch("dam_line", 0x72A77, bytes.fromhex("268a472a"), _interrupt(VEC_DAM_LINE, 4)),
    # ... and on a missile weapon's line (the inventory screen's "1D4"): its "mov al,es:[bx+0Bh]",
    # the weapon's own rate of fire
    Patch("missile_line", 0x729FF, bytes.fromhex("268a470b"), _interrupt(VEC_MISSILE_LINE, 4)),
    # ... and on View Character's: "mov [bp-0Eh],dx", the damage bonus it stores
    Patch("view_dam", 0x64EB6, bytes.fromhex("8956f2"), _interrupt(VEC_VIEW_DAM, 3)),
    # ... and the inventory's line written with its count for one attack every other round (a
    # slowed character's 1 half: "0.5x1D8"), not as if one a round: its formatter's "cmp dx,2 /
    # jng" (no count for 2 halves or fewer) made "je" (no count for 2 alone; View Character's has one
    # always)
    Patch("dam_half", 0x72AC0, bytes.fromhex("83fa027e55"), bytes.fromhex("83fa027455")),
    Patch("can_use", 0x6EF34, bytes.fromhex("26234712"), _interrupt(VEC_CAN_USE, 4)),
    Patch("no_cast", 0x89B84, bytes.fromhex("83c404"), _interrupt(VEC_NO_CAST, 3)),
    Patch("mc_con", 0x87523, bytes.fromhex("03f8"), _interrupt(VEC_MC_CON, 2)),
    Patch("mc_uncon", 0x877DA, bytes.fromhex("2bd0"), _interrupt(VEC_MC_UNCON, 2)),
    # the creation panel's KIT pages, shown in the panel's discipline and sphere windows (weaponpages.py)
    Patch("wp_disc_win", 0x67BFB, bytes.fromhex("68c40b"), _interrupt(VEC_WP_DISC_WIN, 3)),
    Patch("wp_sphere_win", 0x6413B, bytes.fromhex("68c50b"), _interrupt(VEC_WP_SPHERE_WIN, 3)),
    Patch("wp_disc_click", 0x64311, bytes.fromhex("8b5e08"), _interrupt(VEC_WP_DISC_CLICK, 3)),
    Patch("wp_sphere_click", 0x642B0, bytes.fromhex("8b5e08"), _interrupt(VEC_WP_SPHERE_CLICK, 3)),
    Patch("wp_shown", 0x6337A, bytes.fromhex("3d0800"), _interrupt(VEC_WP_SHOWN, 3)),
    Patch("wp_class", 0x66406, bytes.fromhex("b90100"), _interrupt(VEC_WP_CLASS, 3)),
    # the level-up's weapon picks, in the psionicists' pop-up (its routine, in weapon mode)
    Patch("lv_pick", 0x87A9B, bytes.fromhex("837e080b"), _interrupt(VEC_LV_PICK, 4)),
    Patch("pk_count", 0x85F01, bytes.fromhex("8bd00bd2"), _interrupt(VEC_PK_COUNT, 4)),
    Patch("pk_win", 0x85FF4, bytes.fromhex("685d44"), _interrupt(VEC_PK_WIN, 3)),
    Patch("pk_left", 0x8602D, bytes.fromhex("a0ec4a"), _interrupt(VEC_PK_LEFT, 3)),
    Patch("pk_title", 0x860C3, bytes.fromhex("1e682630"), _interrupt(VEC_PK_TITLE, 4)),
    Patch("pk_fill", 0x8610F, bytes.fromhex("33ff8bf7"), _interrupt(VEC_PK_FILL, 4)),
    Patch("pk_click", 0x862D4, bytes.fromhex("8b4608"), _interrupt(VEC_PK_CLICK, 3)),
    # the pop-up's event loop, each time round: the weapon window's slot the pointer is on named
    # in its lines
    Patch("pk_hover", 0x85F44, bytes.fromhex("0bc07515"), bytes((0xCD, VEC_CR_SPELLS, PK_HOVER, 0x90))),
    # the weapon kinds under the selected character's effects on the Effects screen
    Patch("ef_rows", 0x7F13E, bytes.fromhex("5f5e"), _interrupt(VEC_EF_ROWS, 2)),
    Patch("hp_best", 0x87319, bytes.fromhex("8bc8"), _interrupt(VEC_HP_BEST, 2)),
    # the Tome of Understanding (tome.py), clicked as a scroll: a point of WIS
    Patch("tome", 0x8B80C, bytes.fromhex("1e684034"), _interrupt(VEC_TOME, 4)),
    # a combatant's initiative for the round: its 20 added, and a Sentinel's 2 more (kits.py)
    Patch("init", 0x5750E, bytes.fromhex("83c214"), _interrupt(VEC_INIT, 3)),
    # the end of the THAC0 routine: a kit's THAC0 (kits.thac0)
    Patch("thac0", 0x876BB, bytes.fromhex("b814002bc6"), _interrupt(VEC_THAC0, 5)),
    # the spell slot routine: a kit's slots (kits.slots), and the level an Elementalist's count from
    Patch("slots", 0x5E255, bytes.fromhex("8b46fe"), _interrupt(VEC_SLOTS, 3)),
    Patch("slot_level", 0x5E1F6, bytes.fromhex("268a4724"), _interrupt(VEC_SLOT_LEVEL, 4)),
    # a psionic power's PSP: a kit's cost (kits.psp_cost) where it's used, checked, half taken for
    # a failure, and for a defence raised
    Patch("psp_use", 0x5CBE7, bytes.fromhex("0bff7d0233ff"), _interrupt(VEC_PSP_USE, 6)),
    Patch("psp_can_use", 0x5CAA3, bytes.fromhex("268a870100"), _interrupt(VEC_PSP_TABLE, 5)),
    Patch("psp_failed", 0x5CCA2, bytes.fromhex("268a870100"), _interrupt(VEC_PSP_TABLE, 5)),
    Patch("psp_defence", 0x5D820, bytes.fromhex("26294702"), _interrupt(VEC_PSP_DEFENCE, 4)),
    # a cure's healing (the spells' own handler, as it goes to be healed): a Healer's and a
    # Lifebinder's (kits.cure_bonus, kits.cure_die)
    Patch("cure", 0x79619, bytes.fromhex("900e"), _interrupt(VEC_CURE, 2)),
    # a power's cost to keep it up: where it's taken, and the check whether it can be (kits.psp_cost)
    Patch("psp_keep", 0x5CE49, bytes.fromhex("268a870200"), _interrupt(VEC_PSP_KEEP, 5)),
    Patch("psp_can_keep", 0x5CB02, bytes.fromhex("268a870200"), _interrupt(VEC_PSP_KEEP_DX, 5)),
    # a creature marked hit this round (no spell till the next): not a Battle Mage
    Patch("hit_round", 0x58733, bytes.fromhex("26c684af0001"), _interrupt(VEC_HIT_ROUND, 6)),
    # the caster level routine's 7 off a ranger's level: a Seeker's 5, a Justifier's 9 (kits.py)
    Patch("ranger_cast", 0x81B6A, bytes.fromhex("83ea07"), _interrupt(VEC_RANGER_CAST, 3)),
    # The Shinobi's wizard spells (kits.py): its level, its thief level less 5, at the end of the
    # caster level routine (the spell levels it may cast; Dispel Magic) and of the routine giving
    # the level a spell is cast at (durations, damage); at a level up, CHOOSE A SPELL opened for it
    # (no preserver level), the highest spell level it may pick there and the list it picks from
    # (its own spells); a scroll of its own spells learnt once read (DSCLOG's SHINOBI_READ)
    Patch("cast_level", 0x81C06, bytes.fromhex("8b46fe"), _interrupt(VEC_CAST_LEVEL, 3)),
    Patch("spell_level", 0x5E3D1, bytes.fromhex("8bc7"), _interrupt(VEC_SPELL_LEVEL, 2)),
    # The level a spell's duration and damage take, where the game takes each class's (5E25Ch): a
    # ranger's whole (its spell levels count it 7 less), 7 less with the rule, a Seeker's 5 and a
    # Justifier's 9 (kits.spell_class_level)
    Patch("ranger_level", 0x5E3B8, bytes.fromhex("268a4724"), _interrupt(VEC_RANGER_LEVEL, 4)),
    # A kit's hit die (the Battle Mage's d6, the Arcanist's d3) where a level's die is taken from
    # the class's group, and the Mind Warrior's a tenth fewer PSP where a level up sets them; at
    # creation, the die for the most hit points a new character can have, and the end of the
    # routine working out its PSP
    Patch("hit_die", 0x87308, bytes.fromhex("268a870000"), _interrupt(VEC_HIT_DIE, 5)),
    Patch("max_psp", 0x8748F, bytes.fromhex("c45ef8"), _interrupt(VEC_MAX_PSP, 3)),
    Patch("cr_die", 0x65677, bytes.fromhex("268a874a01"), _interrupt(VEC_CR_DIE, 5)),
    Patch("cr_psp", 0x65C3D, bytes.fromhex("5dcb"), _interrupt(VEC_CR_PSP, 2)),
    # The Elementalist's second sphere (kits.py): its cleric bit added where the game gives a
    # priest its spheres' spells (and where it marks them known, on making a character and when a
    # human changes class), and a spell of that sphere counted as its own sphere's where the
    # caster level and the level a spell's duration and damage take are worked out
    Patch("el_grant", 0x5E489, bytes.fromhex("33f6"), _interrupt(VEC_EL_GRANT, 2)),
    Patch("el_cast", 0x81B42, bytes.fromhex("66268b949d01"), _interrupt(VEC_EL_CAST, 6)),
    Patch("el_level", 0x5E375, bytes.fromhex("66268b9f9d01"), _interrupt(VEC_EL_LEVEL, 6)),
    Patch("el_know_new", 0x66FC9, bytes.fromhex("662685879d01"), _interrupt(VEC_EL_KNOW, 6)),
    Patch("el_know_level", 0x86E56, bytes.fromhex("662685879d01"), _interrupt(VEC_EL_KNOW, 6)),
    # ... and a Wilderness Avenger's healing spells not given where the game gives a priest its
    # spheres' spells (no caller found, as for el_grant), a spell's mask tested (DSCLOG's AV_GRANT;
    # at creation, PROBE_EL_KNOW's AV_KNOW)
    Patch("av_grant", 0x5E499, bytes.fromhex("662685979d01"), _site(AV_GRANT, 6)),
    # The classes a kit bars a human from changing to (kits.dual_banned), greyed on the DUAL window
    Patch("dual_ban", 0x866FF, bytes.fromhex("0bc0"), _interrupt(VEC_DUAL_BAN, 2)),
    # A preserver picks its two spells on CHOOSE A SPELL on changing class, as at a level up (the
    # game gives Grease and Magic Missile)
    Patch("dual_spells", 0x86DE4, bytes.fromhex("6a08569a4300000583c4046a07569a4300000583c404"),
          _interrupt(VEC_DUAL_SPELLS, 22)),
    # A click on the Effects screen's lower panel shows the next page of the kits and weapon kinds
    Patch("ef_click", 0x7EC9E, bytes.fromhex("8b7608"), _interrupt(VEC_EF_CLICK, 3)),
    # An Arcanist's first preserver spell of its turn in a fight leaves it free to cast again: where
    # casting marks the caster, where a turn's start clears the mark, where finishing a cast asks
    # whether in a fight, and in the fight's routine that ends a turn
    Patch("cast_mark", 0x845F0, bytes.fromhex("26c687af0001"), _interrupt(VEC_CAST_MARK, 6)),
    Patch("round_mark", 0x57621, bytes.fromhex("26c684af0000"), _interrupt(VEC_ROUND_MARK, 6)),
    Patch("cast_done", 0x722AF, bytes.fromhex("26833e190000"), _interrupt(VEC_CAST_DONE, 6)),
    Patch("end_turn", 0x5925D, bytes.fromhex("8b7608"), _interrupt(VEC_END_TURN, 3)),
    # A scroll's spell: the message once taught (a failed INT roll takes it back) and once refused
    # (a spell level full for the reader's INT)
    Patch("learn_said", 0x8B712, bytes.fromhex("1e68f133"), _interrupt(VEC_LEARN_SAID, 4)),
    Patch("learn_refused", 0x8B719, bytes.fromhex("1e680534"), _interrupt(VEC_LEARN_REFUSED, 4)),
    # AD&D's class tables (game.RULE_ADND_TABLES): the XP for the next level, at a level up and
    # on View Character; priests' THAC0; clerics', druids' and preservers' spell slots
    Patch("xp_level_up", 0x87BBB, bytes.fromhex("666bc064"), _interrupt(VEC_XP, 4)),
    Patch("xp_view", 0x67D41, bytes.fromhex("666bc064"), _interrupt(VEC_XP, 4)),
    Patch("priest_thac0", 0x876AB, bytes.fromhex("8946fe"), _interrupt(VEC_PRIEST_THAC0, 3)),
    Patch("adnd_slots", 0x5E240, bytes.fromhex("900ee87d02"), _interrupt(VEC_ADND_SLOTS, 5)),
    # the leader's CHA lowers what a shop asks (game.RULE_CHA_PRICES, prices.py): the price charged,
    # the one shown under an item, and the one the list greys an item it can't afford by
    Patch("price_buy", 0x8384B, bytes.fromhex("268b4f06"), _interrupt(VEC_PRICE, 4)),
    Patch("price_shown", 0x83BB1, bytes.fromhex("268b4f06"), _interrupt(VEC_PRICE, 4)),
    Patch("price_afford", 0x8310C, bytes.fromhex("66260fbf4706"), _interrupt(VEC_PRICE_EAX, 6)),
    # STORE and RECALL on the creation screen (rollstore.py): the screen's click routine looking up
    # its buttons
    Patch("roll_store", 0x6625D, bytes.fromhex("b91600"), _interrupt(VEC_RS_CLICK, 3)),
    # the view in a fight (a switch, CAMERA): the routine moving a fight's figure a step (0AC0:C7B3)
    # had the view follow it, a step of the view's each time it came near an edge (2191:0BE3h, the
    # map's own walking's too: its margins at DS:2F6Fh); now only when the figure is off the screen
    # (0AC0:AC7Ah, the game's own test), the rest as it was (a monster only while the game shows
    # monsters' moves, ES:19h); out of a fight (IN_COMBAT, DS:1168h, 0: the arena's opening, where
    # the party walks out of the view) as the game has it. The figure's spot pushed straight, in
    # the same 54 bytes; "mov ax,377Eh" stays at 0AC0:CA15h, its segment one DOS relocates as the
    # game loads (RELOCATED).
    Patch("camera_still", 0x1C9F2,
          bytes.fromhex("8b1e7949c1e3058b879d668946fc8b1e7949c1e3058b879f668946fa833e7949047e0db87e378ec0"
                        "26833e1900007439ff76faff76fc"),
          bytes.fromhex("8b1e7949833e681100740a530ee878e25b09c07554c1e30581fb80007e129090909090b8"
                        "7e378ec026833e190000743966ffb79d6690")),
    # a new race or sex on the creation screen: "add sp,6" after the call that gives the default
    # class, where the panel is set right for it (DSCLOG opens the disciplines' window again)
    Patch("race_panel", 0x63403, bytes.fromhex("83c406"), _interrupt(VEC_RACE_PANEL, 3)),
    # the item box's "AC BONUS:": "mov al,es:[bx+12h]", the type's AC (a helm's AC 1 with the rule,
    # set there as the AC routine sets it, for a helm not worn yet)
    Patch("box_ac", 0x8C15A, bytes.fromhex("268a4712"), _interrupt(VEC_BOX_AC, 4)),
    # the game's timer handler (IRQ 0), its first instruction: inc word cs:[0004h] (DSCLOG does
    # it, and notes now and then where the game was, for the Loader's freeze report)
    Patch("tick", 0x3925C, bytes.fromhex("2eff060400"), _interrupt(VEC_TICK, 5)),
    # the routine giving a hit's special effects, where a person who isn't a thri-kreen has none:
    # jmp to its end (DSCLOG queues a Poisoner's poison on each hit, then jumps)
    Patch("poison", 0x7A6DD, bytes.fromhex("e9e500"), _interrupt(VEC_POISON, 3)),
    # the routine finding a missile weapon's ammunition, where it keeps the ammunition's plus:
    # mov es:[0006h],al (DSCLOG makes a Spellarcher's arrows 1 better, at least +1)
    Patch("arrow", 0x58D27, bytes.fromhex("26a20600"), _interrupt(VEC_ARROW, 4)),
    # the routine saying whether an item may be taken from an inventory slot, where it found none
    # of the spells that keep a weapon in the hand: jz to its yes (DSCLOG keeps a Spellarcher's
    # spell arrows in the quiver as those spells keep their weapons)
    Patch("take", 0x6F4B0, bytes.fromhex("7424"), _interrupt(VEC_TAKE, 2)),
    # the sphere menu after DUAL to a cleric, druid or ranger, its answer compared: cmp ax,1 (DSCLOG
    # makes it WATER ONLY for a Healer, when the DUAL window opens, and its answer water)
    Patch("sphere", 0x86BC3, bytes.fromhex("3d0100"), _interrupt(VEC_SPHERE, 3)),
    # the overlay manager's buffer (twice the largest overlay, 32,992 bytes, the game's for good):
    # call far farmalloc becomes "int / test ax,imm16", the call's segment, which DOS relocates,
    # the test's word (DSCLOG gives a block it has kept in upper memory, else calls farmalloc): the
    # game's heap, in the 640 KB, that much bigger
    Patch("overlay_umb", 0x3C68C, bytes.fromhex("9a31120000"), bytes.fromhex("cd%02xa90000" % VEC_OVR_BUF)),
    # ... and its music buffer (12,001 bytes, from its start to its end): the C library's farmalloc,
    # farfree and farrealloc (load:1231h, 1127h, 138Eh) start "push bp / mov bp,sp", which DSCLOG's
    # PROBE_HEAP does itself, giving that one block from upper memory and never letting the library
    # free or grow it
    Patch("heap_malloc", 0x6631, bytes.fromhex("558bec"), _interrupt(VEC_HEAP, 3)),
    Patch("heap_free", 0x6527, bytes.fromhex("558bec"), _interrupt(VEC_HEAP, 3)),
    Patch("heap_realloc", 0x678E, bytes.fromhex("558bec"), _interrupt(VEC_HEAP, 3)),
    # the page flip's wait for the vertical retrace, none with a full screen up (DSCLOG's PROBE_FLIP)
    Patch("flip_wait", 0x1445F, bytes.fromhex("0ee811d2"), _interrupt(VEC_FLIP, 4)),
    # a steady pace on the map (a switch, STEADY_PACE: DSCLOG's STEADY PACE): the map's frame's
    # "call far 1DF3:26DC" (everything a step) and "call far 1DF3:15EA" (what moved drawn, the page
    # flipped), their first 3 bytes (the segments after them are relocated: A9h makes each a "test
    # ax,<segment>", which DSCLOG returns past); a frame drawn late leaves the next undrawn
    Patch("pace_pass", 0x1E901, bytes.fromhex("9adc26"), bytes((0xCD, VEC_PACE_PASS, 0xA9))),
    Patch("pace_draw", 0x1E946, bytes.fromhex("9aea15"), bytes((0xCD, VEC_PACE_DRAW, 0xA9))),
    # A new preserver picks its spells on CHOOSE A SPELL at creation (the game gives Grease, Magic
    # Missile and more by its level)
    Patch("cr_spells", 0x66F2D, bytes.fromhex("8b46fe"), _interrupt(VEC_CR_SPELLS, 3)),
    # ... and a new warrior its weapon specs on the weapon window (DSCLOG's CR_WEAPONS), once DONE
    # has closed the screen's windows (their memory free for it): pop cx / push si / nop
    Patch("cr_weapons", 0x666DF, bytes.fromhex("595690"), _site(CR_WEAPONS, 3)),
    # Creation's scores and hit points as rolled (game.RULE_ROLLED): a score click kept to the
    # die's total, a hit point click doing nothing, the die's total kept as its three loops set
    # CHR, and the totals drawn under CHR. No vectors are left: these share VEC_CR_SPELLS, the
    # INT followed by the site's number (DSCLOG's RL_*) where cr_spells's has its NOP.
    Patch("rl_score", 0x655C6, bytes.fromhex("8a46fe"), bytes((0xCD, VEC_CR_SPELLS, RL_SCORE))),
    Patch("rl_hp", 0x63A49, bytes.fromhex("0346fe"), bytes((0xCD, VEC_CR_SPELLS, RL_HP))),
    Patch("rl_roll_4", 0x65944, bytes.fromhex("26884722"), bytes((0xCD, VEC_CR_SPELLS, RL_ROLL, 0x90))),
    Patch("rl_roll_6", 0x65979, bytes.fromhex("26884722"), bytes((0xCD, VEC_CR_SPELLS, RL_ROLL, 0x90))),
    Patch("rl_roll_7", 0x659AE, bytes.fromhex("26884722"), bytes((0xCD, VEC_CR_SPELLS, RL_ROLL, 0x90))),
    # the creation screen's ability labels (STR: to CHR:, 6511Fh) in its own white (34h): the
    # routine prints them in the colour the last screen left (DS:326Eh: a character screen's
    # yellow, 2Fh), and the creation screen never sets it before they're drawn. The inventory
    # screen draws its labels with the same routine, in the yellow it sets: DSCLOG sets the white
    # only for labels at the creation screen's place (CR_LABELS)
    Patch("cr_labels", 0x65125, bytes.fromhex("8bdec1e302"), _site(CR_LABELS, 5)),
    Patch("rl_sum", 0x65185, bytes.fromhex("83c404"), bytes((0xCD, VEC_CR_SPELLS, RL_SUM))),
    # a click on CON moving the hit points with the most they may be, and each ability's 4d4 kept
    # for the dice log (whatever the rule)
    Patch("rl_con", 0x63946, bytes.fromhex("c41e9c11"), bytes((0xCD, VEC_CR_SPELLS, RL_CON, 0x90))),
    Patch("rl_try", 0x6498B, bytes.fromhex("03069a49"), bytes((0xCD, VEC_CR_SPELLS, RL_TRY, 0x90))),
    # The box the scores' redraw puts back what was under (the screen's first, DS:0F62h: x1, y1,
    # x2, y2), its x2 and y2: a line more under CHR, and wide enough for "100/102" and its shadow
    # (the game's x 48, y 178; nothing else is drawn there, the next thing right a bullet at x 80)
    Patch("rl_sum_box", DS_FILE + 0xF66, struct.pack("<hh", 48, 178), struct.pack("<hh", 77, 185)),
    # the creation panel's age (DSCLOG's CR_AGE, with ages): after PSP's value is drawn, at the
    # die, a choice or the screen opening, and at a click on CON; and the PSP box (the 8th) wider,
    # to RECALL's right, so its saved background clears what was drawn there
    Patch("cr_age", 0x65A89, bytes.fromhex("83c410"), _site(CR_AGE_SITE, 3)),
    Patch("cr_age_con", 0x63A13, bytes.fromhex("83c410"), _site(CR_AGE_CON_SITE, 3)),
    # the creation screen opening: EDIT on a party member keeps its kit, age and weapon specs
    Patch("cr_open", 0x65C68, bytes.fromhex("c606581aff"), _site(CR_OPEN_SITE, 5)),
    Patch("cr_age_name", 0x66045, bytes.fromhex("83c40e"), _site(CR_NAME_SITE, 3)),
    Patch("cr_age_figure", 0x6349F, bytes.fromhex("83c40e"), _site(CR_NAME2_SITE, 3)),
    Patch("cr_age_typed", 0x63AE8, bytes.fromhex("83c40e"), _site(CR_NAME3_SITE, 3)),
    Patch("cr_age_typed_none", 0x63B2D, bytes.fromhex("83c40e"), _site(CR_NAME4_SITE, 3)),
    Patch("cr_age_box", DS_FILE + 0xF9E, struct.pack("<h", 140), struct.pack("<h", 200)),
    # the creation panel's THAC0 ("THAC0: M18 R19", DSCLOG's CR_THAC0_DRAW) right of the hit points:
    # their box (the 7th) wider, to x 243 (DONE's left 244), so its saved background clears it; and
    # drawn again after the two redraws of the hit points that don't draw PSP after them
    Patch("cr_thac0_box", DS_FILE + 0xF96, struct.pack("<h", 140), struct.pack("<h", 243)),
    Patch("cr_thac0_hp", 0x63AC3, bytes.fromhex("83c410"), _site(CR_HP_SITE, 3)),
    Patch("cr_thac0_hp2", 0x63EDA, bytes.fromhex("83c410"), _site(CR_HP_SITE, 3)),
    # After DUAL: the new class's kit on the game's three-choice menu (an Elementalist's second sphere
    # too), and a new warrior's weapon kinds
    Patch("dual_kit", 0x86D90, bytes.fromhex("837e080c"), _interrupt(VEC_DUAL_KIT, 4)),
    # Two sound numbers on the sheet the game reads as words, the kit (43h) and the second sphere
    # (45h) their high bytes: the low byte alone
    Patch("sound_42", 0x78FDA, bytes.fromhex("268b5742"), _interrupt(VEC_SOUND_42, 4)),
    Patch("sound_44", 0x81DE3, bytes.fromhex("268b4744"), _interrupt(VEC_SOUND_44, 4)),
    Patch("pick_any", 0x85580, bytes.fromhex("8946fe0bc0"), _interrupt(VEC_PICK_ANY, 5)),
    Patch("pick_level", 0x85861, bytes.fromhex("fec0"), _interrupt(VEC_PICK_LEVEL, 2)),
    Patch("pick_list", 0x8563F, bytes.fromhex("8bf8"), _interrupt(VEC_PICK_LIST, 2)),
    Patch("scroll_learn", 0x8B6D3, bytes.fromhex("0bc0"), _interrupt(VEC_SCROLL_LEARN, 2)),
    # A bug of the game's own: the roster's DELETE (DSUN.EXE 54AC1h) picked the character by the
    # row clicked alone, where ADD takes the row plus how far the list is scrolled; with the list
    # scrolled, another character was deleted (the row's from the top). The same code, the scroll
    # added; both "mov ax,<segment>" left where they were (their segment is fixed up on loading).
    Patch("roster_delete", 0x54ADF,
          bytes.fromhex("833e8903007417b8d0028ec026a100006bc033c41e324903d8268b07eb26b8d0028ec026a1"
                        "00006bc033c41e324903d8268b47028946fe6bc03ac41e651603d8268b4706"),
          bytes.fromhex("90909090909090"  # (7 nops)
                        "b8d0028ec0"  # mov ax,<segment>; mov es,ax
                        "26a100002603060200"  # mov ax,es:[0] (the row); add ax,es:[2] (the scroll)
                        "6bc033c41e324901c3"  # imul ax,ax,33h; les bx,[4932h] (the list); add bx,ax
                        "b8d002"  # mov ax,<segment> (not used)
                        "833e8903007405"  # cmp word [389h],0; je .party
                        "268b07eb17"  # mov ax,es:[bx]; jmp .done
                        "268b47028946fe6bc03ac41e651601c3268b4706"  # .party: as the game's
                        "909090")),  # .done (54B23h)
    # The routine that reads an object's records (RDFF, DSUN.EXE 68000h) keeps a 6-byte entry
    # for each in a table on its stack, 80 of them ([bp-1F8h]), and gives up on an object with
    # 80 or more (-2): the person is then not made, their map entry freed. The game's largest has
    # 74; the Weapon Merchant with the Loader's weapons has 89, Jark 95. The table made room for
    # 120 (the frame 0F0h bytes larger; the game's stack has some 20 KB it never reaches).
    Patch("records_frame", 0x68003, bytes.fromhex("81ecf801"), bytes.fromhex("81ece802")),
    *(Patch(f"records_table_{at:x}", at, bytes.fromhex(f"8d{reg:02x}08fe"), bytes.fromhex(f"8d{reg:02x}18fd"))
      for at, reg in RECORDS_TABLE),
    Patch("records_most", 0x68294, bytes.fromhex("837eee50"), bytes.fromhex(f"837eee{RECORDS_MOST:02x}")),
    # (not changed: DSCLOG reads the segment this "mov dx,<segment>" loads, the pointer's items')
    Patch("use_item_seg", 0x73A14, bytes.fromhex("ba8003"), bytes.fromhex("ba8003")),
    # The data path is argv[0] cut after its last \ or :, kept at DS:4B81h. The
    # code that finds the cut becomes: path = ".\", then on to "mov byte [si],0"
    # which ends it. (Not an empty path: the save list needs a \ in it.)
    Patch("path", 0x60D68, bytes.fromhex("8bf00bc0740346eb166a3a"),
          bytes.fromhex("c706814b2e5c"  # mov word [4B81h], ".\"
                        "be834b"  # mov si, 4B83h
                        "eb14")),  # jmp to mov byte [si],0
    *(_new_as_okay(offset, jump) for offset, jump in NEW_AS_OKAY),
)


class PatchError(Exception):
    pass


# Patches that are switches on the Options tab: left out when off (their bytes still checked)
EFFECTS_KEPT = ("effects_click_low", "effects_click_high")  # a click on the Effects screen keeps a spell
ROLL_STORE = ("roll_store",)  # STORE and RECALL on the creation screen
CAMERA = ("camera_still",)  # the view in a fight following a figure only off the screen
SCENE_POINTER = ("cine_step", "cine_end")  # a pointer in the scenes, a click ending one
MOUSE_START = ("mouse_set", "mouse_init")  # the pointer starting in the middle, as fast up and down as across
STEADY_PACE = ("pace_pass", "pace_draw")  # walking at full speed on the map, a late frame's next left undrawn
SPELLS_MANUAL = ("bestow_curse_save", "blood_flow_save", "flaming_sphere_negates", "solid_fog_time",
                 "solid_fog_rounds", "spell_turning_time", "spell_turning_rounds", "cause_fear_time",
                 "quicksand_no_save", "pebble_damage", "ironskin_charges", "ironskin_per_level",
                 "stinking_cloud_dice", "stinking_cloud_round", "chaos_int",
                 "classless_save_level", "color_spray_level", "hold_undead_level",
                 "free_action_stuck", "free_action_loop", "free_action_word", "remove_paralysis_word",
                 "protection_paralysis_word", "meteors_count", "meteors_damage", "flame_arrow_damage",
                 "flame_arrow_count", "turn_undead_manual", "chill_touch_time", "blur_save", "fire_shield_save", "cloudkill_save",
                 "cloudkill_kills", "lower_resistance_manual", "strength_dice", "rainbow_pattern_time",
                 "rainbow_pattern_damage", "feeblemind_psionics", "biofeedback_least",
                 "cell_adjustment_heal", "babau_poison", "blue_slaad_poison", "styr_kind", "djinn_kind",
                 "tari_kind", "tari_bite", "shadow_cold", "greater_shadow_class",
                 "shadow_drain")  # the spells and psionics as the manual has them (spells_manual)
SPELL_TO_HIT = ("spell_hit", "spell_hit_stub")  # missile and hostile touch spells roll to hit (spell_to_hit)
PARTY_SPREAD = ("party_spread", "party_gather")  # the whole party in view after a load and a fight


def relocated(data: bytes) -> set:
    """The file offsets of the words DOS relocates as it loads the EXE DATA (its relocation
    table: each such word gets the load segment added, whatever a patch put there)."""
    if len(data) < 0x1C:
        return set()
    count, = struct.unpack_from("<H", data, 6)
    header = struct.unpack_from("<H", data, 8)[0] * 16
    table, = struct.unpack_from("<H", data, 0x18)
    out = set()
    for i in range(count):
        if table + i * 4 + 4 > len(data):
            break
        off, seg = struct.unpack_from("<HH", data, table + i * 4)
        out.add(header + seg * 16 + off)
    return out


def patched(original: bytes, skip=frozenset()) -> bytes:
    """DSUN.EXE's bytes with the dice log patches applied (but those named in SKIP). A patch
    must leave the words DOS relocates as they were (RELOCATED: camera_still's "mov ax,377Eh")."""
    if len(original) != GOG_SIZE:
        raise PatchError(f"DSUN.EXE is {len(original)} bytes; the dice log knows the GOG release "
                         f"({GOG_SIZE} bytes) only")
    data = bytearray(original)
    for p in PATCHES:
        if data[p.offset:p.offset + len(p.original)] != p.original:
            raise PatchError(f"DSUN.EXE is not the version the dice log knows ({p.name} differs)")
        if p.name not in skip:
            data[p.offset:p.offset + len(p.original)] = p.replacement
    moved = relocated(original)
    for p in PATCHES:
        for at in range(p.offset - 1, p.offset + len(p.original)):
            if at in moved and data[at:at + 2] != original[at:at + 2]:
                raise PatchError(f"the patch {p.name} changes a word DOS relocates (at {at:X}h)")
    return bytes(data)


def write_patched(source: str, dest: str, skip=frozenset()) -> None:
    """Write the patched copy of `source` to `dest` (but the patches in SKIP), unless it is
    already there."""
    with open(source, "rb") as f:
        data = patched(f.read(), skip)
    try:
        with open(dest, "rb") as f:
            if f.read() == data:
                return
    except OSError:
        pass
    tmp = dest + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, dest)
