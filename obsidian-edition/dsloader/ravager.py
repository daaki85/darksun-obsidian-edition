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

from . import gamepatch, gff
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
HELPER_EXE = "DSCLOG2.EXE"

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
    """The sequel's offset of Shattered Lands' item field SL (ITEM_SIZE 15h there; 17h here, two bytes
    put in before the slot: read from the party's items in a running game, the +1 long sword's plus)."""
    if sl < 0x11:
        return sl              # 04h the next item, 08h a container's contents, 0Ah the type, 0Fh the power
    if sl < 0x15:
        return sl + 2          # 11h the slot -> 13h, 12h the name -> 14h, 14h the plus -> 16h
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
    (as for Shattered Lands, gamepatch.SPELLS_MANUAL)."""
    on = settings.get("spells_manual", True) is not False
    return frozenset() if on else frozenset(gamepatch.SPELLS_MANUAL)


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
