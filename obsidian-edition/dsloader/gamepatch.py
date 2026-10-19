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
VEC_STRIP = 0xF7
VEC_PALETTE = 0x8B
VEC_COLOURS = 0xCB
VEC_PRICE, VEC_PRICE_EAX = 0x8D, 0x8C
VEC_RS_CLICK = 0x8A
VEC_RACE_PANEL = 0x89
VEC_BOX_AC = 0x88
VEC_TICK = 0x87
VEC_POISON = 0x86
VEC_ARROW = 0x85
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
NS_LIST_ENDS = (0x5DDEF, 0x5DE72, 0x5DF06)
NS_END = 0xCA


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
    # Bugs of the game's spells, fixed whatever the rules (DEVELOPMENT.md's "The game's spells"):
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
    # the combat log below the map (DSCLOG's STRIP; a switch, STRIP): the game's screen 320 x 222,
    # its rows and the split below row 200 set at the end of its mode X set up ("mov al,2 / mov
    # ah,1 / out dx,ax"); the strip shown there is video memory's first 1760 bytes, so the screens
    # move up, each to a multiple of 256 bytes (the page flip sets the high byte of where the
    # screen starts only): A070h and A460h, the pages kept in video memory after them from A848h
    # (to AFFBh as before). Where the screens are set up (0980:271Bh: "mov cx,0FFBh / mov
    # ax,0A000h", the second's "add ax,400h") and in the page flip ("mov ax,0A000h / mov
    # bx,0A400h"; "mov ax,0A000h"; "mov ax,0A400h")
    Patch("strip_lines", 0x11640, bytes.fromhex("b002b401ef"), _interrupt(VEC_STRIP, 5)),
    Patch("strip_screens", 0x11323, bytes.fromhex("b9fb0fb800a0"), bytes.fromhex("b98b0fb870a0")),
    Patch("strip_second", 0x11356, bytes.fromhex("050004"), bytes.fromhex("05f003")),
    Patch("strip_flip", 0x1442F, bytes.fromhex("b800a0bb00a4"), bytes.fromhex("b870a0bb60a4")),
    Patch("strip_shown0", 0x14444, bytes.fromhex("b800a0"), bytes.fromhex("b870a0")),
    Patch("strip_shown1", 0x1444E, bytes.fromhex("b800a4"), bytes.fromhex("b860a4")),
    # ... and the strip dark in each new palette: "sti / pop di" at the end of the routine that
    # sets the whole palette (DSCLOG's PROBE_PALETTE)
    Patch("strip_palette", 0x144F5, bytes.fromhex("fb5f"), bytes((0xCD, VEC_PALETTE))),
    # ... and "pop dx / pop cx" at the end of the one that sets a run of colours (the title's, a
    # fade's steps: DSCLOG's PROBE_COLOURS)
    Patch("strip_colours", 0x288BA, bytes.fromhex("5a59"), bytes((0xCD, VEC_COLOURS))),
    # scrolling (DSCLOG's SCROLLING): the main loop asking where the pointer is, "call far
    # 3118:002E", its first 3 bytes (the segment after them is relocated as the game loads: A9h
    # makes the 5 a "test ax,<segment>", which DSCLOG returns past)
    Patch("scroll", 0x1CAAC, bytes.fromhex("9a2e00"), bytes((0xCD, VEC_SCROLL, 0xA9))),
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
    # A kit's hit die (the Battle Mage's d6, the Mind Warrior's d8) where a level's die is taken from
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
    # jmp to its end (DSCLOG queues a Poisoner's poison on its first hit in a fight, then jumps)
    Patch("poison", 0x7A6DD, bytes.fromhex("e9e500"), _interrupt(VEC_POISON, 3)),
    # the routine finding a missile weapon's ammunition, where it keeps the ammunition's plus:
    # mov es:[0006h],al (DSCLOG makes a Spellarcher's arrows 1 better, at least +1)
    Patch("arrow", 0x58D27, bytes.fromhex("26a20600"), _interrupt(VEC_ARROW, 4)),
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
STRIP = ("strip_lines", "strip_screens", "strip_second", "strip_flip", "strip_shown0", "strip_shown1",
         "strip_palette", "strip_colours")  # the combat log below the map (off by default)


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
