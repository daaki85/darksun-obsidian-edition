"""Obsidian Edition for Wake of the Ravager: the sequel's side of the Loader.

Wake of the Ravager (GOG 1.1, DSUN.EXE 634,416 bytes) runs on Shattered Lands' engine, recompiled with
other record sizes and addresses, so the mod's patches are found in it one by one (the port plan:
reports/wake-of-the-ravager-port-plan.md in the repository). This module holds what is known:

  * WOTR_SIZE and is_wotr_dir: a folder is Wake of the Ravager's by its DSUN.EXE's size.
  * PATCHES: the patched copy's changes (DSUNLOG2.EXE), each found in the sequel's program and read
    against Shattered Lands' (its twin's offset; the original bytes are checked as the copy is made,
    as gamepatch.patched does for Shattered Lands). Most reuse Shattered Lands' patch bytes; those
    whose code differs round them carry the sequel's own.
  * SPELL_FIXES: the spell records' fixes. The sequel keeps no spell table in its program: each spell
    is RESOURCE.GFF's DATA chunk 0-319, 73 bytes, whose first 32 are Shattered Lands' record. A fix
    is gamepatch's patch of the same name (its bytes) written to the same field of the sequel's
    record, only where that record still holds the original bytes (SSI fixed two itself: Dispel
    Magic's "No spell use" and Bestow Curse's save, left out here).
  * SCRIPT_FIXES: the game's own script slips, mended in GPLDATA.GFF's copy (bytes of a GPL chunk,
    checked as the copy is made).
  * prepare: writes DSUNLOG2.EXE and the copies of RESOURCE.GFF and GPLDATA.GFF into the mod's dos
    folder (the helper, DSCLOG2.EXE, opens them for the game's own).
  * conf_lines: the DOSBox autoexec that starts it: the game folder as C: (the copy reads its data
    from the current folder, the "path" patch), its CD as D: (GOG's game.ins, as GOG's own config
    mounts it) as F:, the mod's dos folder as D: as for Shattered Lands, EMS off and UMBPLUS.COM first
    (the sequel runs on XMS without EMS: measured).

The data files' copies are read in place of the game's through the helper's file redirection (its
COPIES table), so the game folder is never written to."""

import os
import struct
from typing import Dict, List, Optional, Tuple

from . import game, gamepatch, gff
from .gamepatch import Patch

WOTR_SIZE = 634416  # DSUN.EXE of the GOG release (1.1)
PATCHED_EXE = "DSUNLOG2.EXE"
RESOURCE_FILE = "RESOURCE.GFF"
RESOURCE_COPY = "RESOURC2.GFF"  # (the copy's name in the mod's dos folder: SL's own copy is RESOURCE.GFF there)
SCRIPT_FILE = "GPLDATA.GFF"
SCRIPT_COPY = "GPLDAT2.GFF"  # (likewise: the helper opens it for GPLDATA.GFF)
ARGS = "-W0 -L"  # (as GOG's RAVAGER.BAT starts it)
CD_DRIVE = "f"  # (the game finds its CD through MSCDEX, whatever the letter: D: stays the mod's dos
# folder, as for Shattered Lands, where GAMEEND.COM and the helper look)

_SL = {p.name: p for p in gamepatch.PATCHES}


def _sl(name: str, at: int) -> Patch:
    """Shattered Lands' patch NAME, its bytes as they are, at the sequel's offset AT."""
    p = _SL[name]
    return Patch(name, at, p.original, p.replacement)


# The program's changes. Each offset found by byte likeness and read side by side with Shattered
# Lands' (playtest/logs/2026-11-19-ravager-fixes.md and -fixes-2.md); the bytes are checked as the
# copy is made, so a wrong offset stops the copy rather than breaking the game.
VEC_RAND = gamepatch.VEC_RAND  # (as DSCLOG2's: dos/dsclog2.asm)
VEC_PIC_FULL, VEC_PIC_PLACE, VEC_PIC_COUNT, VEC_PIC_FAIL = 0xC0, 0xC1, 0xC2, 0xC3
VEC_REAR = 0xC4  # (DSCLOG2's MISSILE_REAR)
VEC_REST_POISON = 0xC5  # (DSCLOG2's REST_POISON)
VEC_NPP = 0xC6  # (DSCLOG2's NPP_SAVE)
VEC_ACID_ROUNDS, VEC_ACID_BURN, VEC_ACID_ONCE, VEC_ACID_USE, VEC_ACID_ROUND = 0xC7, 0xC8, 0xC9, 0xCA, 0xCB
VEC_IMAGE, VEC_BLOW = 0xCC, 0xCD  # (DSCLOG2's IMAGE_SPELL, IMAGE_BLOW)  # (DSCLOG2's own: 66h is DOSBox's)
VEC_USE, VEC_WIN = 0xCE, 0xCF  # (DSCLOG2's PROBE_USE, PROBE_WIN: the spell slots on USE)
VEC_ITEM_BOX = 0xD0  # (DSCLOG2's PROBE_ITEM_BOX: charges in item boxes)
VEC_CHAR = 0xD1  # (DSCLOG2's PROBE_CHAR: THAC0, saves and thief skills on the inventory)
VEC_CAST, VEC_SCROLL, VEC_TICK = 0xD2, 0xD3, 0xD4  # (DSCLOG2's PROBE_CAST, PROBE_SCROLL, PROBE_TICK: names over figures)
VEC_FLIP, VEC_POINTER = 0xD5, 0xD6  # (DSCLOG2's FLIP_SITE, PROBE_POINTER: the combat log's panel)
VEC_LOOK = 0xDA  # (DSCLOG2's PROBE_LOOK: the monster's defences in the Look box)
VEC_VIEW = 0xD9  # (DSCLOG2's PROBE_VIEW: the saves, MOVE and THAC0 on View Character)
VEC_FOLLOW = 0xD8  # (DSCLOG2's PROBE_FOLLOW: the same after the view follows a figure)
VEC_HELM_AC, VEC_BOX_AC = 0xDD, 0xDE  # (DSCLOG2's PROBE_HELM_AC, PROBE_BOX_AC: a Helm's AC 1)
VEC_HELD_HIT, VEC_HELD_DAMAGE = 0xDF, 0xE0  # (DSCLOG2's HELD_HIT, HELD_DAMAGE: AD&D's held target)
VEC_TWO, VEC_OFF_HAND, VEC_ROLL_MAX = 0xE1, 0xE2, 0xE3  # (DSCLOG2's PROBE_TWO, OFF_HAND: AD&D's two weapons)
VEC_CAH_TWO, VEC_CAH_SWING = 0xE5, 0xE6  # (DSCLOG2's CAH_TWO, CAH_SWING: the cahulaks' two heads)
VEC_CAH_HIT, VEC_CAH_MOVE = 0xE7, 0xE8  # (DSCLOG2's CAH_HIT, CAH_MOVE: the cahulaks' tangle)
VEC_REACH, VEC_RANGER_LEVEL, VEC_ENL_ROLL, VEC_ENL_SITE = 0xE9, 0xEA, 0xEB, 0xEC
VEC_SCROLL_LEARN, VEC_LEARN_SAID, VEC_LEARN_REFUSED = 0xED, 0xEE, 0xEF  # (DSCLOG2's preservers' INT)
VEC_SITE = 0xF5  # (DSCLOG2's SITE: INT F5h and a byte, the site's number in its SITE_TABLE)
VEC_BLUR_SAVE, VEC_FSHIELD_SAVE = 0xF3, 0xF4  # (DSCLOG2's BLUR_SAVE, FSHIELD_SAVE: the spells as the manual has them)
VEC_PICK_ANY, VEC_PICK_LIST, VEC_PICK_PAGE = 0xF0, 0xF1, 0xF2  # (DSCLOG2's PICK_ANY, PICK_LIST, PICK_PAGE: preservers' INT at a level up)
# the effects' records (31 bytes: the name, 29, and the icon), file offset (the load + 3C870h: ravlog's
# EFFECT_RECORDS), and the empty one the stinkpots' Nauseated takes (DSCLOG2's STINK_EFFECT)
EFFECT_RECORDS_FILE, NAUSEATED = 0x3C870 + 0x5200, 12
VEC_TWO_HANDED = 0xE4  # (DSCLOG2's TWO_HANDED: a half-giant's two-handed weapon in one hand)
VEC_HP_BEST = 0xDC  # (DSCLOG2's PROBE_HP_BEST: a hit die rolled twice, the better kept)
VEC_CR_HP = 0xDB  # (DSCLOG2's PROBE_CR_HP: THAC0 beside the hit points on the creation screen)
VEC_CENTRE = 0xD7  # (DSCLOG2's PROBE_CENTRE: a move of the view drawn again at once while the panel is shown)
HELPER_EXE = "DSCLOG2.EXE"
# The rule changes (game.RULE_*) ported to the sequel: the only ones the Loader turns on in DSCLOG2's
# header and counts in the dice log; the rest of the Options tab's rules leave the sequel as it is.
RULES_PORTED = (game.RULE_HP_BEST | game.RULE_HELMS | game.RULE_HELD | game.RULE_TWO_WEAPONS
                | game.RULE_HALF_GIANT | game.RULE_CAHULAKS | game.RULE_SIZE | game.RULE_RANGER_CAST
                | game.RULE_ENLARGE | game.RULE_INT_LEARN | game.RULE_REST)
# Helms: the sequel's two helm types, 55 (AC 0, hats too: only an item named Helm, its name 24h, counts
# AC 1 with RULE_HELMS: DSCLOG2's PROBE_HELM_AC) and 56 (a Helm and the Helm of Domination: AC 1 of its own)
HELM_TYPE, HELM_NAME, ITEM_NAME = 55, 0x24, 0x14
DS_FILE = 0x47E0 * 16 + 0x5200  # the data segment's start in DSUN.EXE (its DGROUP, past the header)

def _site(number: int, length: int) -> bytes:
    """DSCLOG2's SITE at a patch site: INT VEC_SITE, the site's number, NOPs to LENGTH (3 or more)."""
    return bytes((0xCD, VEC_SITE, number)) + b"\x90" * (length - 3)


PATCHES: Tuple[Patch, ...] = (
    # rand(): INT VEC_RAND at its start, DSCLOG2's INT_RAND being it (the same function as SL's at
    # 5C22h, its seed at DS:384Ah): the dice log's every roll.
    Patch("rand", 0x5A22, bytes.fromhex("8b0e4c388b"), gamepatch._interrupt(VEC_RAND, 5)),
    # the saving throw's end: "mov al,[bp-2] / cmp al,[bp-1]" (SL's 79BB7h, its six bytes the same),
    # INT VEC_SAVE: DSCLOG2's PROBE_SAVE records the total and the number needed, then compares
    Patch("save", 0x66EA6, bytes.fromhex("8a46fe3a46ff"), gamepatch._interrupt(gamepatch.VEC_SAVE, 6)),
    # INT VEC_AC: DSCLOG2's PROBE_AC records the AC the attack uses, at the AC function's end. The
    # sequel's function (5D520h) was rewritten: the AC after armour in [bp-4], its adjustments in a
    # local ([bp-6]) where SL's had SI, so "mov ax,[bp-4] / add ax,[bp-6]", 6 bytes (SL's 5).
    Patch("ac", 0x5D6E6, bytes.fromhex("8b46fc0346fa"), gamepatch._interrupt(gamepatch.VEC_AC, 6)),
    # The data path: argv[0] cut after its last \ or :, kept at DS:44F2h (SL's 4B81h), made ".\"
    # (the current folder: the game's, C:), the same code as SL's and the jump landing the same.
    Patch("path", 0x6740E, bytes.fromhex("8bf00bc0740346eb166a3a"),
          bytes.fromhex("c706f2442e5c"  # mov word [44F2h], ".\"
                        "bef444"  # mov si, 44F4h
                        "eb14")),  # jmp to mov byte [si],0
    # The game's bugs, the same code as SL's round each:
    _sl("party_best", 0x8C60E),     # a thief skill rolled for the whole party went to the first member
    _sl("monster_count", 0x8D3FB),  # random monsters: the next slot's strength, a divide by 0
    _sl("thief_slots", 0x49C90),    # thief skills' equipment penalty for anything in the hands
    _sl("dam_half", 0x7B1E8),       # a slowed character's DAM line on the inventory
    _sl("page_free", 0x28412),      # the view's second page freed unset: "Null pointer assignment"
    # The saving throw's last compare unsigned, so "can't save" (-100) saved (SL's save_signed): the
    # sequel's at 66EA6h is "cmp al,[bp-1] / jb fail / jmp saved", its branch the other way from
    # SL's, so its own bytes: jb made jl. (Seen at work: logs/2026-11-19-ravager-cant-save.md.)
    Patch("save_signed", 0x66EAC, bytes.fromhex("7203"), bytes.fromhex("7c03")),
    # Share Strength (any maintained power on someone else) ended only on the psionicist, and could end
    # another of its effects (SL's power_end_*): the sequel's loop at 61A7Dh is SL's 5CEECh with its
    # effect records' fields 147h on (+24Dh owner, +24Fh creature, +251h spell, +254h handle: SL's
    # +106h...10Dh) and the live count at DS:2100h (SL's 1E24h): SL's six patches with those.
    Patch("power_end_live", 0x61A91, bytes.fromhex("8bde6bdb0a"), bytes.fromhex("3b36002190")),
    Patch("power_end_skip", 0x61A99, bytes.fromhex("8ec0"), bytes.fromhex("7d20")),
    Patch("power_end_handle", 0x61AA2, bytes.fromhex("8bde6bdb0a"), bytes.fromhex("26ffb75402")),
    Patch("power_end_owner", 0x61AAA, bytes.fromhex("8ec0268a8754025057"), bytes.fromhex("26ffb74d02") + b"\x90" * 4),
    Patch("power_end_again", 0x61AB8, bytes.fromhex("83c404"), bytes.fromhex("59594e")),
    Patch("power_end_count", 0x61ABC, bytes.fromhex("81fec0007cbb"), bytes.fromhex("3b3600217cbb")),
    # Armor's charge used where any spell or blow landed on its wearer as well as for damage (SL's
    # armor_charge, the same bytes): the routine at 84B60h is SL's 7A539h, the sequel numbering Armor's
    # effect 5 (its flag 20h; SL's 2 and 4), its damage routine's charge at 66CF0h as SL's 79A3Bh.
    _sl("armor_charge", 0x84B7E),
    # Bless and Aid leave out those of the caster's side with an enemy near, measured from (x, x) of where
    # each stands: the routine (86638h; SL's 7B03Dh, the side's mask its own) pushes the map thing's fine x
    # (+0Ah, DS:67C5h) twice; its first push made the y (+0Ch, 67C7h), as SL's bless_from_cell.
    Patch("bless_from_cell", 0x86687, bytes((0xC5,)), bytes((0xC7,))),
    # Absorb Disease (its handler at 661FFh, curing effect 27, Diseased) went on into Strength's (6623Bh):
    # the psionicist took the disease and 1d6 STR too, the STR alone with no disease. Both ways now go to
    # the end of Strength's handler ("mov bx,[bp+12h] / or byte [bx],2", 65B0Ah, then its way out), as
    # SL's absorb_no_strength and absorb_end: no disease, the jz to the cure's end; there, a jmp there.
    Patch("absorb_no_strength", 0x66207, bytes.fromhex("7432"), bytes.fromhex("742c")),
    Patch("absorb_end", 0x66235, bytes.fromhex("8b5e12"), bytes.fromhex("e9d2f8")),
    # Resting while poisoned with a druid of 5th level and more: the rest killed the Poisoned from a copy of
    # each member's effects taken before the free Neutralize Poison (SL's rest_cures_*, which moved the
    # casts): DSCLOG2's REST_POISON answers the test (8D02Dh) from the effects as they are then.
    Patch("rest_cures_first", 0x8D02D, bytes.fromhex("f646ea80"), bytes((0xCD, VEC_REST_POISON, 0x90, 0x90))),
    # Negative Plane Protection saved as against Vampiric Touch (here spell 38), whose record allows no
    # save, so it never stopped an undead's touch (SL's npp_save): DSCLOG2's NPP_SAVE in the place of
    # "add sp,4 / push 6 / push 26h" (84DDAh) makes the save one against paralysis, poison and death.
    Patch("npp_save", 0x84DDA, bytes.fromhex("83c4046a066a26"), bytes((0xCD, VEC_NPP)) + b"\x90" * 5),
    # Acid Arrow's acid never burned after the hit (SL's acid_*): its time made rounds as charges where
    # an effect is added, one spent for each creature at each round's start (Acid's burn, 2d4), none
    # spent by any other call, and the burn's damage putting no Acid on again: DSCLOG2's ACID_ROUNDS,
    # ACID_ROUND, ACID_USE, ACID_BURN and ACID_ONCE, each INT followed by NOPs to the site's length.
    Patch("acid_rounds", 0x7FAA6, bytes.fromhex("66817e0ef1d8ffff"), bytes((0xCD, VEC_ACID_ROUNDS)) + b"\x90" * 6),
    Patch("acid_burn", 0x82BF3, bytes.fromhex("8b7606"), bytes((0xCD, VEC_ACID_BURN, 0x90))),
    Patch("acid_once", 0x651FE, bytes.fromhex("837ef600"), bytes((0xCD, VEC_ACID_ONCE, 0x90, 0x90))),
    Patch("acid_use", 0x7FD99, bytes.fromhex("8b7e06"), bytes((0xCD, VEC_ACID_USE, 0x90))),
    Patch("acid_round", 0x5B592, bytes.fromhex("803e4e0500"), bytes((0xCD, VEC_ACID_ROUND, 0x90, 0x90, 0x90))),
    # Mirror Image stopped no weapon blow and took any spell for one creature, one's own and a friend's
    # too (SL's ns_image, ns_blow): DSCLOG2's IMAGE_SPELL (the d100 against 75 only for a foe's spell)
    # and IMAGE_BLOW (a hit on a target with images: 75 in 100 an image takes it, the attack a miss).
    Patch("ns_image", 0x84BF8, bytes.fromhex("3d4b00"), bytes((0xCD, VEC_IMAGE, 0x90))),
    Patch("ns_blow", 0x5D09F, bytes.fromhex("837e1a00"), bytes((0xCD, VEC_BLOW, 0x90, 0x90))),
    # Missiles from behind: the attack's set-up (5C8xxh, SL's 582xxh) makes an attack one from behind by
    # the target's facing alone, missiles too, whatever the distance (+2 to hit, the target's DEX and
    # shield lost). DSCLOG2's MISSILE_REAR at SL's site (its "stealth" probe's, there "push word
    # [bp-1Ah]"): here "mov al,[bp-19h] / push ax", the INT in the mov's place.
    Patch("stealth", 0x5C99F, bytes.fromhex("8a46e750"), bytes((0xCD, VEC_REAR, 0x50, 0x90))),
    # Graphics disappearing in a busy area (SSI's note 2712 is this game's): the picture cache's 300
    # slots (its loader at 2A568h, SL's 25FA6h) reused once all are taken, DSCLOG2's PIC_REUSE on four
    # interrupts of its own at SL's four sites (SL's pic_full, pic_place, pic_count, pic_fail).
    Patch("pic_full", 0x2A5E7, bytes.fromhex("813e5d262c01739fa15d26"), gamepatch._interrupt(VEC_PIC_FULL, 11)),
    Patch("pic_place", 0x2A6FD, bytes.fromhex("c45efc"), gamepatch._interrupt(VEC_PIC_PLACE, 3)),
    Patch("pic_count", 0x2A75C, bytes.fromhex("8b365d26ff065d26"), gamepatch._interrupt(VEC_PIC_COUNT, 8)),
    Patch("pic_fail", 0x2A58E, bytes.fromhex("b8ffff"), gamepatch._interrupt(VEC_PIC_FAIL, 3)),
    # Spell slots on the USE screen (SL's use and window probes, the same code at the sequel's offsets):
    # DSCLOG2's PROBE_USE after the LEVEL button is labelled (79543h, SL's 70FBBh: "add sp,0Ch"), and
    # PROBE_WIN at the end of the routine bringing a window to the front (303BEh, SL's 2BBA9h: "xor
    # ax,ax / pop si"), each drawing the Loader's lines (the helper's SLOTS_TEXT) in the panel.
    Patch("use", 0x79543, bytes.fromhex("83c40c"), gamepatch._interrupt(VEC_USE, 3)),
    Patch("window", 0x303BE, bytes.fromhex("33c05e"), gamepatch._interrupt(VEC_WIN, 3)),
    # Charges in item boxes (SL's item_box): DSCLOG2's PROBE_ITEM_BOX at the end of the routine filling an
    # item's box (9A4FEh, SL's 8C1A1h: "push 0"), the item's charges, or a plain weapon's material's to-hit.
    Patch("item_box", 0x9A4FE, bytes.fromhex("6a00"), gamepatch._interrupt(VEC_ITEM_BOX, 2)),
    # THAC0, saves and thief skills on the inventory (SL's inventory): DSCLOG2's PROBE_CHAR after the
    # panel's weapon lines (91286h, SL's 6F6BFh: "add sp,0Eh"), the text routine and the character's
    # selector read from the code before it, at SL's distances.
    # View Character's panels, once drawn (987FBh, SL's 8A471h: "push dword 000B0140h"; SL's code at
    # the same distances): DSCLOG2's PROBE_VIEW adds the saves, MOVE and THAC0, and does the push.
    Patch("view", 0x987FB, bytes.fromhex("666840010b00"), gamepatch._interrupt(VEC_VIEW, 6)),
    # The Effects screen: a click on an effect's icon ends it (its handler for the selected character's
    # effects, SL's code at 8B05Fh). Only a psionic power's effect (the sequel's powers EBh-10Ch) still
    # ends so; a spell's is left on: the two "not a psionic power" jumps go to the handler's way out
    # (8B104h's jump to 8B128h), as SL's "effects_click_low"/"_high" (the same bytes, the switch the same).
    Patch("effects_click_low", 0x8B08F, bytes.fromhex("7c51"), bytes.fromhex("7c73")),
    Patch("effects_click_high", 0x8B09F, bytes.fromhex("7d41"), bytes.fromhex("7d63")),
    # The Look box, its first status rows drawn (640FBh: "mov si,ax / mov word [bp-0Ah],0"; SL's
    # "mov si,ax / xor di,di" at 5FCDAh, the routine rewritten a little): DSCLOG2's PROBE_LOOK adds the
    # Loader's lines about the monster and does the moves.
    Patch("look", 0x640FB, bytes.fromhex("8bf0c746f60000"), gamepatch._interrupt(VEC_LOOK, 7)),
    # The creation screen's THAC0 ("THAC0: M18 R19", SL's cr_thac0_*): DSCLOG2's PROBE_CR_HP right of
    # the hit points, after they are drawn again (6B84Ch, 6BC62h; SL's 63AC3h, 63EDAh) and after PSP,
    # drawn after them (6D6AEh at the die, a choice, the screen opening; 6B79Ch at a click on CON; SL's
    # CR_AGE sites 65A89h, 63A13h): each "add sp,10h". The hit points' box (the 7th, DS:1224h, as SL's
    # F92h) wider, to x 243 (DONE's left 244), so its saved background clears what is drawn there.
    # A hit die rolled twice, the better kept (SL's hp_best; the Options tab's "best_hit_die"):
    # DSCLOG2's PROBE_HP_BEST at the game's "mov cx,ax" after the roll (95025h, SL's 87319h).
    Patch("hp_best", 0x95025, bytes.fromhex("8bc8"), gamepatch._interrupt(VEC_HP_BEST, 2)),
    # A fix of the sequel's: its hit die routine (94F60h) adds the roll to the rolled hit points and stops,
    # where SL's works out the most hit points again and raises the creature's; the sequel left that to
    # the level-up (957E0h), so the creation screen's die never set them and a new character kept the
    # least (7 for a 7th-level fighter). DSCLOG2's ROLL_MAX_HP at the add (9506Ch) does SL's part.
    Patch("roll_max_hp", 0x9506C, bytes.fromhex("26014f0a"), gamepatch._interrupt(VEC_ROLL_MAX, 4)),
    # Half-giants hold a two-handed weapon in one hand (SL's two_handed_other, two_handed_new; the Options
    # tab's "half_giant_hands"): DSCLOG2's TWO_HANDED at the inventory's two reads of an item type's
    # two-handed bit (77976h the other hand's, 77A0Dh the new one's: "test byte es:[bx+0Bh],40h"; SL's
    # 6F33Fh, 6F3CCh).
    Patch("two_handed_other", 0x77976, bytes.fromhex("26f6470b40"), gamepatch._interrupt(VEC_TWO_HANDED, 5)),
    Patch("two_handed_new", 0x77A0D, bytes.fromhex("26f6470b40"), gamepatch._interrupt(VEC_TWO_HANDED, 5)),
    # The cahulaks' two heads (SL's cahulaks_two, cahulaks_swing; Weapon traits, always on): DSCLOG2's
    # CAH_TWO at the two-weapon routine's "two weapons ready?" (5DE6Fh, SL's 59627h: on for the cahulaks
    # too) and CAH_SWING at each swing's start (5D052h, SL's 589B6h: the off head's -4 on the round's
    # last); the off head's one more attack a round is OFF_HAND's, PROBE_TWO the main head's -2.
    Patch("cahulaks_two", 0x5DE6F, bytes.fromhex("837e06017e11"), gamepatch._interrupt(VEC_CAH_TWO, 6)),
    Patch("cahulaks_swing", 0x5D052, bytes.fromhex("c746fc0000"), gamepatch._interrupt(VEC_CAH_SWING, 5)),
    # The cahulaks' tangle (SL's cahulaks_hit and PROBE_MOVE's part): DSCLOG2's CAH_HIT where a weapon's hit
    # has done damage (5D1FEh: "mov byte [bp-19h],0"; SL's 58B54h) and CAH_MOVE where a creature's turn
    # starts (5B838h: its movement stored; SL's 57566h), a tangled one's turn taken.
    Patch("cahulaks_hit", 0x5D1FE, bytes.fromhex("c646e700"), gamepatch._interrupt(VEC_CAH_HIT, 4)),
    Patch("cahulaks_move", 0x5B838, bytes.fromhex("2689872e02"), gamepatch._interrupt(VEC_CAH_MOVE, 5)),
    # a polearm's reach (DSCLOG2's REACH): the combatant distance routine's "mov ax,[bp-1Ch]" at its end
    Patch("reach", 0x25CDD, bytes.fromhex("8b46e4"), gamepatch._interrupt(VEC_REACH, 3)),
    # the stinkpots' Nauseated (DSCLOG2's STINKPOTS): the sequel's effect 12, empty (no name, icon 0), named
    # and given Stinking Cloud's icon (ICON 21000 + 22, as the effects' icons are their spells')
    Patch("nauseated_name", EFFECT_RECORDS_FILE + NAUSEATED * 31, bytes(31),
          b"Nauseated".ljust(29, b"\0") + struct.pack("<H", 21000 + 22)),
    # Helms count AC 1 (SL's ring_ac's helm part and box_ac; the Options tab's "helm_ac"): DSCLOG2's
    # PROBE_HELM_AC at the AC function's two reads of a worn item's type's AC (5D663h, 5D67Bh: "mov
    # al,es:[bx+0Eh] / cwde"; SL's 58EBDh) and PROBE_BOX_AC at the item box's AC BONUS (9A4B7h, SL's 8C15Ah).
    Patch("helm_ac", 0x5D663, bytes.fromhex("268a470e98"), gamepatch._interrupt(VEC_HELM_AC, 5)),
    Patch("helm_ac_2", 0x5D67B, bytes.fromhex("268a470e98"), gamepatch._interrupt(VEC_HELM_AC, 5)),
    Patch("box_ac", 0x9A4B7, bytes.fromhex("268a470e98"), gamepatch._interrupt(VEC_BOX_AC, 5)),
    # AD&D's held target (SL's held_hit, held_damage; the Options tab's "held_hit"): DSCLOG2's HELD_HIT at
    # the attack's natural 20 test (5D088h, SL's 589E9h: "cmp word [bp-6],14h", before its JE to the
    # hit), a helpless target hit too; HELD_DAMAGE at what a helpless target takes (5D1B7h, SL's 58B0Dh:
    # "mov ax,[bp-4] / shl ax,1"), not doubled.
    # Fire, cold and electricity: DEX instead of a doubled d20 (SL's RULE_NO_DOUBLE, always on: DSCLOG's
    # PROBE_DOUBLE and the Loader's set_dodge). The saving throw doubles its d20 when the spell's flags
    # word (its record's +1Ah) has 86h: "shl al,1" at 66E63h (SL's 79B74h), made two NOPs; the spells so
    # flagged get the dodge bit in their category word instead (DODGE_FIX), which the modifiers routine
    # (83606h, SL's own test: "test word [es:bx+11h],40h") turns into the target's DEX defence.
    Patch("no_double", 0x66E63, bytes.fromhex("d0e0"), bytes.fromhex("9090")),
    # Rangers' casting level (SL's ranger_level, game.RULE_RANGER_CAST, always on): DSCLOG2's RANGER_LEVEL
    # where the level a spell's duration and damage take reads a class's level (629F0h, SL's 5E3B8h:
    # "mov al,es:[bx+1Eh] / mov ah,0"), a ranger's 7 less as the caster level routine has it.
    Patch("ranger_level", 0x629F0, bytes.fromhex("268a471eb400"), gamepatch._interrupt(VEC_RANGER_LEVEL, 6)),
    # Enlarge multiplies the weapon's dice only (SL's stab_roll's keeping of the dice and enl_site;
    # game.RULE_ENLARGE, always on): DSCLOG2's ENL_ROLL after the attack's damage roll (5D0C8h, SL's
    # 58A29h: "cmp word [bp+16h],1") and ENL_SITE at Enlarge's multiplying (863E7h, SL's 7C246h: 32 bytes).
    # Preservers' INT (SL's scroll_learn, learn_said, learn_refused; game.RULE_INT_LEARN, always on):
    # DSCLOG2's SCROLL_LEARN at the scroll's "already known" test (99A2Fh: "or ax,ax", SL's 8B6D3h),
    # LEARN_SAID at YOU LEARN THE SPELL's push (99A7Fh: "push ds / push 2E97h", SL's 8B712h) and
    # LEARN_REFUSED at YOU ALREADY KNOW THIS SPELL's (99A86h: "push ds / push 2EABh", SL's 8B719h).
    Patch("scroll_learn", 0x99A2F, bytes.fromhex("0bc0"), gamepatch._interrupt(VEC_SCROLL_LEARN, 2)),
    Patch("learn_said", 0x99A7F, bytes.fromhex("1e68972e"), gamepatch._interrupt(VEC_LEARN_SAID, 4)),
    Patch("learn_refused", 0x99A86, bytes.fromhex("1e68ab2e"), gamepatch._interrupt(VEC_LEARN_REFUSED, 4)),
    # ... and at a level up (SL's pick_any and pick_list): DSCLOG2's PICK_ANY where the preserver's level up
    # takes its level (9317Fh: "mov [bp-2],ax / or ax,ax", SL's 85580h) and PICK_LIST after CHOOSE A
    # SPELL's page is listed (93246h: "mov di,ax", SL's 8563Fh); and PICK_PAGE where the window takes its
    # first page's level (93487h: "mov [43ECh],al"), the highest with room.
    Patch("pick_any", 0x9317F, bytes.fromhex("8946fe0bc0"), gamepatch._interrupt(VEC_PICK_ANY, 5)),
    Patch("pick_list", 0x93246, bytes.fromhex("8bf8"), gamepatch._interrupt(VEC_PICK_LIST, 2)),
    Patch("pick_page", 0x93487, bytes.fromhex("a2ec43"), gamepatch._interrupt(VEC_PICK_PAGE, 3)),
    # Spells as the manual has them (SL's names, so the option's skip covers them: gamepatch.SPELLS_MANUAL):
    # Blur's +1 on saves against magic (DSCLOG2's BLUR_SAVE at Barkskin's test, 8373Ah, SL's 79DC0h) and
    # Fire Shield's +2 against fire and cold (FSHIELD_SAVE at Protection from Cold's, 837F7h, SL's 79E03h)
    Patch("blur_save", 0x8373A, bytes.fromhex("c45e0a26f607407401 47".replace(" ", "")), gamepatch._interrupt(VEC_BLUR_SAVE, 10)),
    Patch("fire_shield_save", 0x837F7, bytes.fromhex("f746fc0400740dc45e0a26f64709027403 83c703".replace(" ", "")),
          gamepatch._interrupt(VEC_FSHIELD_SAVE, 20)),
    # ... through DSCLOG2's SITE (INT F5h, then the site's number; NOPs to the site's length): Stinking
    # Cloud's 1d4+1 rounds (its time's routine, 80249h, SL's 76D73h: "les bx,[bp-4]"); a classless
    # creature's hit dice as its level for saves (83656h, SL's 79D8Ch: "mov [bp-6],ax"); Chaos saved
    # against by INT 21 and up or 4 and down (its "sub di,100", 83E83h, SL's 79F80h); Color Spray's
    # levels (Dismissal's test, 83E86h, SL's 79F83h); Cloudkill's bands (83E98h, SL's 79F95h) and its
    # kill (the save's answer kept, 651C5h, SL's 78DB6h: "mov [bp-1],al").
    Patch("stinking_cloud_round", 0x80249, bytes.fromhex("c45efc"), _site(0, 3)),
    Patch("classless_save_level", 0x83656, bytes.fromhex("8946fa"), _site(1, 3)),
    Patch("chaos_int", 0x83E83, bytes.fromhex("83ef64"), _site(2, 3)),
    Patch("color_spray_level", 0x83E86, bytes.fromhex("837e143c750c"), _site(3, 6)),
    Patch("cloudkill_save", 0x83E98, bytes.fromhex("837e14397509837efa067f0383ef64"), _site(4, 15)),
    Patch("cloudkill_kills", 0x651C5, bytes.fromhex("8846ff"), _site(5, 3)),
    # ... Flaming Arrow's bolts, one for every five levels (a cast's tail, 7E8E0h, SL's 7567Fh: "mov
    # dl,[es:bx]", the record's count), and Biofeedback's least 1 of a blow (8348Bh, SL's 79C83h: "sub si,2")
    Patch("flame_arrow_count", 0x7E8E0, bytes.fromhex("268a17"), _site(6, 3)),
    Patch("biofeedback_least", 0x8348B, bytes.fromhex("83ee02"), _site(7, 3)),
    # ... Lower Resistance's 30% + 1% a caster level off, not the resistance halved (84B2Eh-84B4Eh, SL's
    # 7A507h-7A527h), the cast's level kept from the cast's tail's start (7E338h: "mov di,[bp+0Ah]") for
    # ACID_ROUNDS to put into the effect's amount
    Patch("cast_level_kept", 0x7E338, bytes.fromhex("8b7e0a"), _site(8, 3)),
    Patch("lower_resistance_manual", 0x84B2E, bytes.fromhex(
        "f646f520740b8b46fe992bc2d1f88946fe83fe40750b8a460ab400051e002946fe"), _site(9, 33)),
    # ... Strength's dice by the target's classes, AD&D's (6624Eh, SL's 79483h: "push dword 60001h", 1d6;
    # Adrenalin Control's the same code, kept 1d6)
    Patch("strength_dice", 0x6624E, bytes.fromhex("666801000600"), _site(10, 6)),
    # ... Cell Adjustment's 1d4 HP, not 2 (664C5h, SL's 795A2h: "push 2 / jmp", to Neutralize Poison's
    # "push ax" at 66545h)
    Patch("cell_adjustment_heal", 0x664C5, bytes.fromhex("6a02e947f3"), _site(11, 5)),
    # ... and no psionic power for a feebleminded user (the power check 61D2Eh, after its test that the user
    # has the power, 61D47h; SL's 5D5B4h)
    Patch("feeblemind_psionics", 0x61D47, bytes.fromhex("0bc07505b000"), _site(12, 6)),
    # ... and any damage to a creature Rainbow Pattern holds ends the hold (the start of the routine taking
    # hit points off, 5CBECh, SL's 585A2h: "mov di,[bp+6] / mov dx,[bp+8]")
    Patch("rainbow_pattern_damage", 0x5CBEC, bytes.fromhex("8b7e068b5608"), _site(13, 6)),
    # ... and Hold Undead leaves an undead of more levels than the cast's immune (the immunity routine's
    # common way out, 84A65h: "mov ax,si / cmp ax,0FCh"; SL's 7A345h)
    Patch("hold_undead_level", 0x84A65, bytes.fromhex("8bc63dfc00"), _site(14, 5)),
    # ... and Turn Undead AD&D's way: the turning of one undead (97C50h, SL's 7ADB7h) where it reads the
    # undead's hit dice, "mov al,[es:bx+1Eh]" (97C9Ch; SL's 7AE01h): DSCLOG2's TU_SITE, which sends the
    # routine on to its destroy, its failure or its end
    Patch("turn_undead_manual", 0x97C9C, bytes.fromhex("268a471e"), _site(15, 4)),
    # Spells that roll to hit (SL's spell_to_hit, always on): the immunity routine's "not immune" answer
    # (84AAFh, "xor ax,ax / pop di"; the sequel has no always-hit stub to answer instead), DSCLOG2's
    # TH_SITE: the missile and hostile touch spells' attack roll, a miss answering immune
    Patch("spell_hit", 0x84AAF, bytes.fromhex("33c05f"), _site(16, 3)),
    # Resting as in AD&D (SL's rest_hp; RULE_REST, always on): the rest's HP restore (8CF79h, "mov
    # [es:bx],ax", SL's 808AFh): DSCLOG2's REST_HP, a night's natural healing, 3 + CON's bonus
    Patch("rest_hp", 0x8CF79, bytes.fromhex("268907"), _site(17, 3)),
    Patch("enlarge_roll", 0x5D0C8, bytes.fromhex("837e1601"), gamepatch._interrupt(VEC_ENL_ROLL, 4)),
    Patch("enlarge_dice", 0x863E7, bytes.fromhex("6bc00a660fbfc06683c064660fbfd6660fafc266bb64000000669966f7fb8bf0"),
          gamepatch._interrupt(VEC_ENL_SITE, 32)),
    Patch("held_hit", 0x5D088, bytes.fromhex("837efa14"), gamepatch._interrupt(VEC_HELD_HIT, 4)),
    Patch("held_damage", 0x5D1B7, bytes.fromhex("8b46fcd1e0"), gamepatch._interrupt(VEC_HELD_DAMAGE, 5)),
    # AD&D's two weapons (SL's two_weapons and PROBE_ATTACKS' off hand; always on, game.RULES_ALWAYS):
    # DSCLOG2's PROBE_TWO at the two-weapon to-hit adjustment (5DE7Ch, SL's 59634h: "neg ax / mov dx,ax /
    # or dx,dx / jge +2 / xor dx,dx"), -2 in the right hand and -4 in the left; OFF_HAND where the attack
    # stores its attacks a round (5CEE8h, SL's 58892h: "mov ah,0 / mov [bp-0Ah],ax"), one in the off hand.
    Patch("two_weapons", 0x5DE7C, bytes.fromhex("f7d88bd00bd27d0233d2"), gamepatch._interrupt(VEC_TWO, 10)),
    Patch("off_hand", 0x5CEE8, bytes.fromhex("b4008946f6"), gamepatch._interrupt(VEC_OFF_HAND, 5)),
    Patch("cr_thac0_box", DS_FILE + 0x1228, struct.pack("<h", 140), struct.pack("<h", 243)),
    Patch("cr_thac0_hp", 0x6B84C, bytes.fromhex("83c410"), gamepatch._interrupt(VEC_CR_HP, 3)),
    Patch("cr_thac0_hp2", 0x6BC62, bytes.fromhex("83c410"), gamepatch._interrupt(VEC_CR_HP, 3)),
    Patch("cr_thac0_psp", 0x6D6AE, bytes.fromhex("83c410"), gamepatch._interrupt(VEC_CR_HP, 3)),
    Patch("cr_thac0_con", 0x6B79C, bytes.fromhex("83c410"), gamepatch._interrupt(VEC_CR_HP, 3)),
    Patch("inventory", 0x91286, bytes.fromhex("83c40e"), gamepatch._interrupt(VEC_CHAR, 3)),
    # Names over figures (SL's labels.py, DSCLOG's LABELS): a spell cast recorded (80585h, SL's 772AAh:
    # "mov cx,[bp+6]", the caster), the map's main loop asking where the pointer is (20230h, SL's
    # 1CAACh: "call far 35B9:0034", its segment kept as a "test ax,imm" for the relocation), the
    # game's timer (3DA2Ch, SL's 3925Ch: "inc word cs:[4]").
    Patch("spell_cast", 0x80585, bytes.fromhex("8b4e06"), gamepatch._interrupt(VEC_CAST, 3)),
    Patch("scroll", 0x20230, bytes.fromhex("9a3400"), bytes((0xCD, VEC_SCROLL, 0xA9))),
    Patch("tick", 0x3DA2C, bytes.fromhex("2eff060400"), gamepatch._interrupt(VEC_TICK, 5)),
    # The combat log's panel (SL's combatlog.py, DSCLOG's PANEL; the main loop's PROBE_SCROLL above):
    # the game's flip of its two screens (16974h, SL's 14444h: "mov ax,0A000h / cmp word [118Eh],0"),
    # and its routine drawing the pointer (3326Ah, SL's 2EA55h: the stack check).
    Patch("panel_flip", 0x16974, bytes.fromhex("b800a0833e8e1100"), gamepatch._interrupt(VEC_FLIP, 8)),
    Patch("pointer", 0x3326A, bytes.fromhex("39269c00"), gamepatch._interrupt(VEC_POINTER, 4)),
    # The end of the routine centring the view (1C5F:01F3, 219E3h: "mov byte [143Fh],0"): a move of
    # the view while the panel is shown drawn again at once, the scrolled copy of the panel gone.
    Patch("centre", 0x21A5A, bytes.fromhex("c6063f1400"), gamepatch._interrupt(VEC_CENTRE, 5)),
    # The same after the three calls drawing the view moved after a figure (262C:06C4; the view moved
    # by 262C:0D80): their "add sp,8".
    Patch("follow_1", 0x1E3EC, bytes.fromhex("83c408"), gamepatch._interrupt(VEC_FOLLOW, 3)),
    Patch("follow_2", 0x20193, bytes.fromhex("83c408"), gamepatch._interrupt(VEC_FOLLOW, 3)),
    Patch("follow_3", 0x2143E, bytes.fromhex("83c408"), gamepatch._interrupt(VEC_FOLLOW, 3)),
)

# The spell records' fixes: gamepatch's patch name -> (the sequel's DATA chunk, the field's offset).
# Found by Shattered Lands' spell names (Ironskin is "Iron Skin" in the sequel, Turn Pebble into
# Boulder "Pebble to Boulder", Flame Arrow "Flaming Arrow").
SPELL_FIXES: Dict[str, Tuple[int, int]] = {
    "cause_serious": (171, 0x1C), "cause_critical": (195, 0x1C),
    "brave_fear_21": (21, 0x12), "brave_fear_43": (41, 0x12), "brave_fear_78": (124, 0x12),
    "brave_fear_132": (199, 0x12), "scare_save": (21, 0x1F),
    "blood_flow_save": (166, 0x1F), "flaming_sphere_negates": (14, 0x12),
    "solid_fog_time": (50, 0x04), "solid_fog_rounds": (50, 0x07),
    "spell_turning_time": (46, 0x04), "spell_turning_rounds": (46, 0x07),
    "cause_fear_time": (124, 0x04), "quicksand_no_save": (202, 0x1F),
    "ironskin_per_level": (200, 0x1D), "pebble_damage": (53, 0x1C),
    "meteors_count": (33, 0x00), "meteors_damage": (33, 0x1C), "flame_arrow_damage": (28, 0x1C),
    "chill_touch_time": (3, 0x04), "rainbow_pattern_time": (49, 0x04), "stinking_cloud_dice": (22, 0x04),
}
SPELL_COUNT = 320  # (DATA 0-319)
SPELL_SIZE = 73
# ... and the dodge (with the patch no_double): every spell record whose flags word (+1Ah) has
# game.DOUBLED_FLAGS gets game.CATEGORY_DODGE in its category word (+11h), as SL's set_dodge does in
# memory: the fire, cold and electricity spells and the monsters' powers so flagged (32 records).
DODGE_FIX, SPELL_FLAGS, SPELL_CATEGORY = "dodge", 0x1A, 0x11


# The sequel's records in memory and where Shattered Lands' fields are in them (for the dice log's
# layout profile, step 3 of the plan). Far pointers in its data segment (each SL's + 364h):
CREATURES_PTR, SHEETS_PTR, ITEMS_PTR = 0x19C9, 0x19C5, 0x19C1  # (SL's 1665h, 1661h, 165Dh)
CREATURE_SIZE, SHEET_SIZE, ITEM_SIZE = 0x31, 0x42, 0x17  # (SL's 3Ah, 47h, 15h)
DGROUP = 0x47E0  # its DS less its load segment (4982h - 1A2h in a GOG start; SL's 4356h)
WHOSE_TURN, CAMERA, MAP_OBJECTS = 0x426D, 0x1408, 0x67BB  # (SL's 4979h, 1178h, 6694h; the map objects 25h bytes apart)
SPELL_SLOTS, SLOTS_STRIDE, PRIEST_SLOTS = 0x446A, 0x22, 0x0B  # wizard casts left by level, a member a row
KNOWN_BITSET = 15  # bytes of known wizard spells a member (bit n, spell n), the roster's SPST chunk
AFRAID = 0x60  # a creature's +18h while Afraid

# Shattered Lands' creature and sheet offsets -> the sequel's (None: no such field), found by aligning
# the transfer's records (CHARTRAN) and checked against Gerakis's in memory (HP 165, PSP 27, sheet 3,
# base AC 10, Move 12, Okay, THAC0 14, STR 24..CHA 14, name):
def creature_field(sl: int) -> Optional[int]:
    """The sequel's offset of Shattered Lands' creature field SL (CREATURE_SIZE 3Ah there)."""
    if sl < 0x0E:
        return sl              # HP, PSP, the sheet's number, the entity's id, the item lists
    if 0x16 <= sl <= 0x1C:
        return sl - 8          # 1Ah base AC -> 12h, 1Bh Move -> 13h, 1Ch status -> 14h
    if sl == 0x1D:
        return 0x15            # the side (00 the party's, 07 the Draxans': not in the transfer's record)
    if 0x1F <= sl <= 0x27:
        return sl - 9          # 1Fh THAC0 -> 16h, 22h the abilities -> 19h
    if 0x28 <= sl < 0x38:
        return sl - 7          # 28h the name -> 21h (16 bytes there, SL's 18: its last two have no place)
    return None


def item_field(sl: int) -> Optional[int]:
    """The sequel's offset of Shattered Lands' item field SL (ITEM_SIZE 15h there; 17h here): SL's
    power (its spell + 1, or its own effect: a byte at 0Fh) is a word at 10h (the sequel has 320 spells),
    and from SL's 10h on everything is two bytes on (read from the party's items in a running game, the +1
    long sword's plus; and the program's uses of each field counted alike, 2026-11-20: SL's 0Fh 37 uses,
    the sequel's 10h 35, mostly words; 0Fh none)."""
    if sl < 0x0F:
        return sl              # 04h the next item, 08h a container's contents, 0Ah the type, 0Eh the charges
    if sl == 0x0F:
        return 0x10            # the power (its low byte: the word's, for spells below 255)
    if sl < 0x15:
        return sl + 2          # 10h -> 12h, 11h the slot -> 13h, 12h the name -> 14h, 14h the plus -> 16h
    return None


def sheet_field(sl: int) -> Optional[int]:
    """The sequel's offset of Shattered Lands' sheet field SL (SHEET_SIZE 47h there)."""
    if sl < 0x0E:
        return sl              # XP, max HP, the HP rolled, max PSP
    if 0x10 <= sl <= 0x13:
        return sl - 2          # 10h the entity's id, 12h the class flags
    if 0x18 <= sl <= 0x3B:
        return sl - 6          # 18h race -> 12h, 21h classes -> 1Bh, 24h levels -> 1Eh, 37h saves -> 31h
    if 0x3D <= sl <= 0x46:
        return sl - 6          # 3Fh the levels before any were lost -> 39h, 43h the kit byte -> 3Dh
    return None                # 0Eh-0Fh, 14h-17h (the mod's weapon specs), 3Ch: none in the sequel


class RavagerError(Exception):
    pass


def _find_file(folder: str, name: str) -> Optional[str]:
    try:
        for entry in os.listdir(folder):
            if entry.lower() == name.lower():
                return os.path.join(folder, entry)
    except OSError:
        pass
    return None


def is_wotr_dir(folder: Optional[str]) -> bool:
    """FOLDER holds Wake of the Ravager (its DSUN.EXE the GOG release's size)."""
    exe = folder and _find_file(folder, "DSUN.EXE")
    try:
        return bool(exe) and os.path.getsize(exe) == WOTR_SIZE
    except OSError:
        return False


def find_dir(sl_dir: Optional[str] = None, given: Optional[str] = None) -> Optional[str]:
    """Wake of the Ravager's folder: GIVEN, else the one chosen on the Options tab or found beside
    Shattered Lands' SL_DIR or in GOG's usual places (wotrart's search, for its RESOURCE.GFF)."""
    if given:
        return os.path.abspath(given) if is_wotr_dir(given) else None
    from . import wotrart
    found = wotrart.find_resources(sl_dir)
    folder = found and os.path.dirname(found)
    return os.path.abspath(folder) if folder and is_wotr_dir(folder) else None


def write_patched(game_dir: str, dest: str, skip=frozenset()) -> None:
    """DSUNLOG2.EXE: the sequel's DSUN.EXE with PATCHES (but those named in SKIP)."""
    source = _find_file(game_dir, "DSUN.EXE")
    if not source:
        raise RavagerError(f"no DSUN.EXE in {game_dir}")
    gamepatch.write_patched(source, dest, skip, PATCHES, WOTR_SIZE)


def spell_fixed(data: bytes, skip=frozenset()) -> Tuple[bytes, List[str]]:
    """RESOURCE.GFF's bytes with SPELL_FIXES applied (but those named in SKIP), and the names of those
    applied. Each only where the record holds gamepatch's original bytes; anything else raises (a
    RESOURCE.GFF this module doesn't know)."""
    places = gff.index_places(data, "DATA")
    out, done = bytearray(data), []
    for name, (spell, field) in SPELL_FIXES.items():
        p = _SL[name]
        if spell not in places or places[spell][2] != SPELL_SIZE:
            raise RavagerError(f"{RESOURCE_FILE} has no spell record {spell}: not the GOG release's")
        at = places[spell][1] + field
        if bytes(out[at:at + len(p.original)]) != p.original:
            raise RavagerError(f"{RESOURCE_FILE}'s spell {spell} is not as the fix {name} expects")
        if name not in skip:
            out[at:at + len(p.original)] = p.replacement
            done.append(name)
    if DODGE_FIX not in skip:
        for spell in range(SPELL_COUNT):
            if spell in places and places[spell][2] == SPELL_SIZE:
                at = places[spell][1]
                if struct.unpack_from("<H", out, at + SPELL_FLAGS)[0] & game.DOUBLED_FLAGS:
                    out[at + SPELL_CATEGORY] |= game.CATEGORY_DODGE
        done.append(DODGE_FIX)
    return bytes(out), done


def write_resources(game_dir: str, dest: str, skip=frozenset()) -> List[str]:
    """RESOURCE.GFF's copy with the spell fixes, written to DEST unless already so; the fixes applied."""
    return _write_copy(game_dir, RESOURCE_FILE, dest, spell_fixed, skip)


# The game's script slips: {name: (GPL chunk, offset, original, replacement)}.
#   inn_rest: Reyhan's inn in Tyr. GPL 140 rents a fire ring (object kind -1317) for so many nights;
#   Tyr's master script gives the ring a look trigger, GPL 142 at 1478, which runs before the
#   program's own look (whose ring branch rests the party 8 hours, rest(0, 8, 7FFEh) at 6951Ch: the
#   program skips it if the look's scripts take the ring away). With nights left, the night is
#   counted down, and on the last one (1499) a proximity trigger is armed (GPL 23 at 47, range 15)
#   that deletes the ring: the party stands beside it, so it fires at once and the ring is gone
#   before the rest. One night paid, no rest. The fix jumps over that arming (the GOTO and fill of
#   gpl.put_jumps): the paid night rests, and a look at the spent ring (the ELSE, which arms the same
#   trigger) takes it away. Found 2026-11-20 (playtest/logs/2026-11-20-ravager-dicelog.md).
#   no_manual_check: the mod's "no manual check" (as dsloader/manualcheck.py for Shattered Lands). The
#   game's copy protection is GPL 331, which GPL 137 (at 3589) runs while (135,29) isn't 7: a presence
#   "creates a mindlink" and asks for a word from the manual, three wrong answers and the party dies.
#   Its right answer runs GPL 142 at 1 ((7,32) 255, (7,29) 7, "Your answer suffices") and returns.
#   In the copy 331 does that from its start (after (14,0) 0, as its own start sets): no presence,
#   no question; its first two commands (to 63) made those and the filler, so the rest still decodes.
SCRIPT_FIXES: Dict[str, Tuple[int, int, bytes, bytes]] = {
    "inn_rest": (142, 1499, bytes.fromhex("1b002f00179105258f0f"), bytes.fromhex("6405e561616161616161")),
    "no_manual_check": (331, 1, bytes.fromhex(
        "2a4f00629205a9a32a0c3a7920c38b7f5e883cefea831f2c38f5eccbcd077d3d3420db873e9c787620c9a79e3d187967cbcd06141c37f7cbcb375d880180"),
        bytes.fromhex("1600008e001600ff8720160007871d15") + b"\x61" * 46),
}


def script_fixed(data: bytes, skip=frozenset()) -> Tuple[bytes, List[str]]:
    """GPLDATA.GFF's bytes with SCRIPT_FIXES applied (but those named in SKIP), and the names of those
    applied; anything not as a fix expects raises (a GPLDATA.GFF this module doesn't know)."""
    places = gff.index_places(data, "GPL ")
    out, done = bytearray(data), []
    for name, (chunk, offset, original, replacement) in SCRIPT_FIXES.items():
        if chunk not in places or places[chunk][2] < offset + len(original):
            raise RavagerError(f"{SCRIPT_FILE} has no script {chunk}: not the GOG release's")
        at = places[chunk][1] + offset
        if bytes(out[at:at + len(original)]) != original:
            raise RavagerError(f"{SCRIPT_FILE}'s script {chunk} is not as the fix {name} expects")
        if name not in skip:
            out[at:at + len(original)] = replacement
            done.append(name)
    return bytes(out), done


def _write_copy(game_dir: str, name: str, dest: str, fixed, skip) -> List[str]:
    source = _find_file(game_dir, name)
    if not source:
        raise RavagerError(f"no {name} in {game_dir}")
    with open(source, "rb") as f:
        data, done = fixed(f.read(), skip)
    try:
        with open(dest, "rb") as f:
            if f.read() == data:
                return done
    except OSError:
        pass
    gff.write_atomic(dest, data)
    return done


def write_scripts(game_dir: str, dest: str, skip=frozenset()) -> List[str]:
    """GPLDATA.GFF's copy with the script fixes, written to DEST unless already so; the fixes applied."""
    return _write_copy(game_dir, SCRIPT_FILE, dest, script_fixed, skip)


def skipped(settings: dict) -> frozenset:
    """The patches and spell fixes the switches leave out: the spells as the manual describes them
    (as for Shattered Lands, gamepatch.SPELLS_MANUAL) and spells kept on the Effects screen
    (gamepatch.EFFECTS_KEPT)."""
    on = settings.get("spells_manual", True) is not False
    kept = settings.get("effects_kept", True) is not False  # (spells kept on the Effects screen)
    return (frozenset() if on else frozenset(gamepatch.SPELLS_MANUAL)) \
        | (frozenset() if kept else frozenset(gamepatch.EFFECTS_KEPT))


def prepare(game_dir: str, dos_dir: str, settings: dict) -> Optional[str]:
    """Write DSUNLOG2.EXE and the RESOURCE.GFF and GPLDATA.GFF copies into DOS_DIR. Returns why the game can't be
    patched, or None."""
    skip = skipped(settings)
    try:
        write_patched(game_dir, os.path.join(dos_dir, PATCHED_EXE), skip)
        write_resources(game_dir, os.path.join(dos_dir, RESOURCE_COPY), skip)
        write_scripts(game_dir, os.path.join(dos_dir, SCRIPT_COPY), skip)
    except (RavagerError, gamepatch.PatchError, gff.GffError, OSError, struct.error) as e:
        return str(e)
    return None


def cd_image(game_dir: str) -> Optional[str]:
    """The CD's sheet GOG's config mounts (game.ins, beside game.gog: mounted as F: here)."""
    return _find_file(game_dir, "game.ins")


def conf_lines(game_dir: str, dos_dir: str, cd: Optional[str] = None, umb_plus: str = "UMBPLUS.COM",
               game_end: Optional[str] = None) -> List[str]:
    """The [dos] section and the autoexec that start the patched sequel: EMS off (its memory layer
    takes XMS), the game folder as C: (its saves and data, the copy reading them from there), its CD
    as F: (CD, default its game.ins), the mod's dos folder as D:, UMBPLUS.COM, the helper (DSCLOG2.EXE)
    loaded high, then the copy."""
    cd = cd or cd_image(game_dir)
    lines = ["[dos]", "ems=false", "", "[autoexec]", "@echo off", "cls", f'mount c "{game_dir}"']
    if cd:
        lines.append(f'imgmount {CD_DRIVE} "{cd}" -t iso')
    lines += [f'mount d "{dos_dir}"', "d:\\" + umb_plus.lower(), f"lh d:\\{HELPER_EXE.lower()}", "cls", "c:",
              f"d:\\{PATCHED_EXE.lower()} {ARGS}"]
    if game_end:
        lines.append("d:\\" + game_end.lower())
    lines += ["exit", ""]
    return lines
