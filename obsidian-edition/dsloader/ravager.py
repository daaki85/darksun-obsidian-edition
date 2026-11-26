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
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import game, gamepatch, gff
from .gamepatch import Patch

WOTR_SIZE = 634416  # DSUN.EXE of the GOG release (1.1)
PATCHED_EXE = "DSUNLOG2.EXE"
RESOURCE_FILE = "RESOURCE.GFF"
RESOURCE_COPY = "RESOURC2.GFF"  # (the copy's name in the mod's dos folder: SL's own copy is RESOURCE.GFF there)
SCRIPT_FILE = "GPLDATA.GFF"
SCRIPT_COPY = "GPLDAT2.GFF"  # (likewise: the helper opens it for GPLDATA.GFF)
OBJECTS_FILE = "OBJEX.GFF"
OBJECTS_COPY = "OBJEX2.GFF"  # (likewise: the helper opens it for OBJEX.GFF)
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
                | game.RULE_ENLARGE | game.RULE_INT_LEARN | game.RULE_REST | game.RULE_RESTRICT
                | game.RULE_ITEM_SAVES | game.RULE_MULTI_HP | game.RULE_ROLLED | game.RULE_ADND_TABLES
                | game.RULE_CON | game.RULE_DUAL_CLASS | game.RULE_AGING | game.RULE_STEALTH
                | game.RULE_SPECIALIZE | game.RULE_KITS | game.RULE_THIEF_TABLE | game.RULE_CHA_PRICES
                | game.RULE_LEVEL_10)
# Helms: the sequel's two helm types, 55 (AC 0, hats too: only an item named Helm, its name 24h, counts
# AC 1 with RULE_HELMS: DSCLOG2's PROBE_HELM_AC) and 56 (a Helm and the Helm of Domination: AC 1 of its own)
HELM_TYPE, HELM_NAME, ITEM_NAME = 55, 0x24, 0x14
# and the mod's Bone Helm (its type the Loader's for SL's 117, which only it has: AC 1 with RULE_HELMS too,
# DSCLOG2's BONE_HELM_TYPE; Shattered Lands' DSCLOG HELM_BONE)
BONE_HELM_TYPE = 104  # (mod_type(117): GAME_TYPES + 117 - 115)
# the XP table's reads (its "imul eax,eax,64h": XP_NEED's sites, 3 bytes on)
XP_READS = (0x6C3E4, 0x6C48A, 0x6C4CC, 0x6FB8B, 0x958E3, 0x95931, 0x9597A, 0x95C84)
DS_FILE = 0x47E0 * 16 + 0x5200  # the data segment's start in DSUN.EXE (its DGROUP, past the header)
# The level cap by XP (game.RULE_LEVEL_10; DSCLOG2's LEVEL_ROOM): a class goes up while its next level
# needs no more than its share of RAV_XP_CAP (the owner's, 2026-11-25: most characters of three classes
# reach 15th, of one or two higher), past the game's cap of 15, up to the XP table's 30th level (the owner's,
# 2026-11-25: no stop at 20th)
RAV_XP_CAP, RAV_LEVEL_MOST = 5_625_000, 30
# the sheet's classes (1-17) to the XP table's rows (1-8: tables.ROWS), as the game's map at 360h:9Dh
CLASS_ROWS = (0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 8)


def xp_share(classes: Sequence[int], levels: Sequence[int], human: bool, rows: bool = False) -> int:
    """The XP the first class of a character may gather under RAV_XP_CAP (DSCLOG2's LEVEL_ROOM): all of
    it for one class, an equal share for several (not a human), and for a human what is left after the
    XP its old classes' levels needed (slots 1 and 2). CLASSES the sheet's (1-17), or rows (1-8) with
    ROWS, as View Character's copy has them."""
    from . import tables
    if not human:
        n = sum(1 for c in classes if c)
        return RAV_XP_CAP // n if n else RAV_XP_CAP
    share = RAV_XP_CAP
    for cls, level in zip(classes[1:3], levels[1:3]):
        row = cls if rows else (CLASS_ROWS[cls] if 0 <= cls < len(CLASS_ROWS) else 0)
        if row and 1 <= level <= RAV_LEVEL_MOST:
            share = max(share - tables.RAV_XP[tables.ROWS[row - 1]][level - 1], 0)
    return share


def level_room(classes: Sequence[int], levels: Sequence[int], human: bool, slot: int, rows: bool = False) -> bool:
    """Whether the class in SLOT may go up a level under the cap (LEVEL_ROOM's CF): its next level's
    XP (tables.RAV_XP at its level) no more than its share, and below 30th."""
    from . import tables
    cls, level = classes[slot], levels[slot]
    row = cls if rows else (CLASS_ROWS[cls] if 0 <= cls < len(CLASS_ROWS) else 0)
    if not row or not 0 <= level < RAV_LEVEL_MOST:
        return False
    return tables.RAV_XP[tables.ROWS[row - 1]][level] <= xp_share(classes, levels, human, rows)


def level_most(row: str, classes: int) -> int:
    """The highest level a class of ROW reaches under the cap in a character of CLASSES classes."""
    from . import tables
    share, level = RAV_XP_CAP // classes, 1
    while level < RAV_LEVEL_MOST and tables.RAV_XP[row][level] <= share:
        level += 1
    return level

# The game's reads of an item's name (file offsets: SITE_NAME's)
NAME_READS = (0x5E496, 0x768A3, 0x7B036, 0x7B081, 0x98CAA, 0x9A227, 0x9A252)
# The item names: the game's table holds 256 (RESOURCE.GFF's TEXT 1000: its 255 lines are names 1-255);
# DSCLOG2's ITEM_NAMES (its header's +196, NAMES_ROOM of NAME_KEPT bytes, written by the Loader as it
# attaches) are names 256 on. The mod's own come first, each at 256 + its Shattered Lands entry less
# names.OWN (so the mod's Short Sword, SL's 144h, is 258).
NAMES_GAME, NAMES_ROOM, NAME_KEPT = 256, 160, 16
TSR_NAMES_OFF, TSR_NAMES_COUNT = 196, 198
KEEPSAKE_NAMES_FIRST = NAMES_GAME + 50  # (after the mod's, names.EXTRA of them: the party transfer's keepsakes, ravitems)


def mod_name(sl_entry: int) -> int:
    """The sequel's name number for the mod's Shattered Lands name entry SL_ENTRY (names.OWN on)."""
    from . import names
    return NAMES_GAME + sl_entry - names.OWN


def item_names(kept: Sequence[bytes] = ()) -> bytes:
    """DSCLOG2's ITEM_NAMES as the Loader writes them: the mod's names at mod_name's places, then the
    party transfer's keepsakes' KEPT from KEEPSAKE_NAMES_FIRST (as many as there is room for)."""
    from . import names
    out = bytearray(NAMES_ROOM * NAME_KEPT)
    for entry, name in names.NAMES.items():
        at = (mod_name(entry) - NAMES_GAME) * NAME_KEPT
        out[at:at + NAME_KEPT] = name[:NAME_KEPT - 1].ljust(NAME_KEPT, b"\0")
    for i, name in enumerate(kept[:NAMES_GAME + NAMES_ROOM - KEEPSAKE_NAMES_FIRST]):
        at = (KEEPSAKE_NAMES_FIRST - NAMES_GAME + i) * NAME_KEPT
        out[at:at + NAME_KEPT] = name[:NAME_KEPT - 1].ljust(NAME_KEPT, b"\0")
    return bytes(out)


def _site(number: int, length: int) -> bytes:
    """DSCLOG2's SITE at a patch site: INT VEC_SITE, the site's number, NOPs to LENGTH (3 or more)."""
    return bytes((0xCD, VEC_SITE, number)) + b"\x90" * (length - 3)


# The sheet made 48h bytes (SHEET_SIZE; the game's 42h, GAME_SHEET_SIZE), as Shattered Lands' 47h has
# room for the weapon specs: +42h..+44h hold SL's +14h..+16h as game.packed_specs packs them (the specs
# less 17, the starting age's roll, the flag bits: game.SPEC_SLOTS in ravlog's layout), +45h..+47h four more
# weapon specs, 5 bits each (SPEC_MORE: a gladiator's 5th to 8th, past SL's levels; game.spec_more).
# Every "imul r,r,42h" of the program is followed within four instructions by a load of the sheets'
# pointer [19C5h]/[19C7h] (386 of them, all "imul ax,ax,42h" or "imul dx,dx,42h", root and overlays, no
# other form; the overlays are read from the file, so file patches reach them): each one's 42h made 48h
# (sheet_stride_*; tests/test_ravsheet.py scans the patched program for one left). The rest that knows
# the size is at the end of PATCHES (sheet_*).
SHEET_STRIDES_AX = (
    0x1D084, 0x1D096, 0x1D0B0, 0x1D0C4, 0x1D0DC, 0x1D100, 0x1D138, 0x1D151, 0x1D177, 0x1D18A,
    0x1D1C9, 0x1D1DC, 0x1D1F4, 0x1D209, 0x1D225, 0x1DFB6, 0x1DFF8, 0x1E028, 0x1EDB9, 0x1EDD0,
    0x1EDE7, 0x1EDFE, 0x1EE15, 0x1EE2C, 0x21CF0, 0x2297E, 0x24B0A, 0x2532F, 0x2534B, 0x25A75,
    0x26550, 0x265D8, 0x590B5, 0x59109, 0x59145, 0x59CEC, 0x5A02C, 0x5A3C3, 0x5C566, 0x5C7E4,
    0x5C7F7, 0x5C80A, 0x5C824, 0x5C83E, 0x5C858, 0x5C955, 0x5CB86, 0x5CEDB, 0x5D187, 0x5D58D,
    0x5D6AA, 0x5DA28, 0x5DE5E, 0x5F441, 0x5F963, 0x5F987, 0x615B0, 0x61734, 0x61FC1, 0x61FD7,
    0x62250, 0x6228B, 0x622D6, 0x626FA, 0x62732, 0x6275E, 0x627BD, 0x62802, 0x6283E, 0x62883,
    0x6291A, 0x62C2D, 0x62C59, 0x62C95, 0x62CF2, 0x62D5D, 0x62E2D, 0x62E7B, 0x62EC2, 0x62F67,
    0x62FAE, 0x63AF7, 0x63B30, 0x63F08, 0x63F43, 0x63F6B, 0x64003, 0x6529B, 0x652CA, 0x6532A,
    0x656BD, 0x65728, 0x65842, 0x65C29, 0x66029, 0x66E20, 0x66F3C, 0x6819C, 0x68219, 0x68278,
    0x6CA4C, 0x6D221, 0x6D23E, 0x6D2A9, 0x6D2DA, 0x6D306, 0x6D36F, 0x6D3B4, 0x6E19A, 0x6E450,
    0x6E486, 0x6E4AE, 0x6E6B9, 0x6E716, 0x6E76A, 0x6E7EB, 0x6E7FD, 0x6E80D, 0x6E82D, 0x6E83D,
    0x6E84D, 0x6E85F, 0x6E86F, 0x6E87F, 0x6E88F, 0x6E89F, 0x6E8AF, 0x6E929, 0x6EA2B, 0x6EA41,
    0x6EA77, 0x6EAAC, 0x6EE22, 0x6EEA3, 0x6EF7B, 0x6EF8B, 0x6F2AC, 0x70384, 0x703A1, 0x73760,
    0x73ADE, 0x7453F, 0x74556, 0x7456B, 0x74AC2, 0x74B1B, 0x74BC6, 0x75176, 0x752A9, 0x752DE,
    0x75321, 0x75BD8, 0x75CC2, 0x75D6B, 0x7763E, 0x77A6F, 0x7876D, 0x787E2, 0x78855, 0x78961,
    0x789AA, 0x78B71, 0x78C56, 0x78D20, 0x79170, 0x79263, 0x7927C, 0x793C0, 0x79482, 0x7949B,
    0x7976D, 0x7A061, 0x7A133, 0x7A1AE, 0x7AA70, 0x7AB40, 0x7ABCB, 0x7AEE0, 0x7B195, 0x7BA38,
    0x7CA7C, 0x81BFB, 0x81F2D, 0x8243F, 0x82622, 0x8283F, 0x83437, 0x8363C, 0x8376C, 0x83799,
    0x837C6, 0x84248, 0x84274, 0x84584, 0x84805, 0x84A9C, 0x84ADE, 0x84D0F, 0x84DC2, 0x84E6C,
    0x84EE9, 0x852C7, 0x852F9, 0x85391, 0x853A8, 0x85835, 0x85868, 0x85B18, 0x85CE4, 0x85D26,
    0x85D53, 0x85D80, 0x8614D, 0x86199, 0x8638A, 0x86572, 0x866B5, 0x869E4, 0x869FD, 0x86A16,
    0x86A2F, 0x86E1C, 0x875F7, 0x87797, 0x877C3, 0x8780A, 0x8A4A8, 0x8A566, 0x8A5E8, 0x8A699,
    0x8CF54, 0x8CF98, 0x8CFDD, 0x8D019, 0x8D512, 0x8D529, 0x8D540, 0x8DF5E, 0x8DFFA, 0x8EA50,
    0x8FEAE, 0x8FEE7, 0x8FF35, 0x8FF9C, 0x8FFD5, 0x9001E, 0x9114D, 0x9121A, 0x92836, 0x9286A,
    0x9289B, 0x928C7, 0x928F6, 0x92928, 0x92957, 0x93391, 0x93BFD, 0x94478, 0x944D8, 0x94599,
    0x945F2, 0x9461C, 0x94651, 0x94749, 0x9478B, 0x947BB, 0x9494F, 0x94973, 0x94997, 0x949C4,
    0x949D6, 0x949F6, 0x94B1C, 0x94B33, 0x94BAE, 0x94BC3, 0x94BDA, 0x94C20, 0x94C32, 0x94C44,
    0x94C63, 0x94F71, 0x950B5, 0x951A0, 0x951CE, 0x95225, 0x9523E, 0x95300, 0x95312, 0x95329,
    0x95339, 0x953CC, 0x954EF, 0x95590, 0x955A2, 0x955ED, 0x95605, 0x95639, 0x956CF, 0x95701,
    0x95720, 0x95731, 0x95753, 0x9576B, 0x957F7, 0x9585F, 0x95876, 0x9588F, 0x958AC, 0x958FA,
    0x95946, 0x9599A, 0x959BC, 0x959DA, 0x959FC, 0x95B19, 0x95BDB, 0x95C33, 0x95C50, 0x95C9B,
    0x95CDD, 0x95CFF, 0x95D1C, 0x95D78, 0x95E18, 0x95ED6, 0x95F58, 0x96009, 0x9602C, 0x9610D,
    0x96996, 0x96AEE, 0x97C7D, 0x97C93, 0x97E77, 0x9820D, 0x982D1, 0x98359, 0x98463, 0x98524,
    0x98554, 0x98584, 0x985B4, 0x985F5, 0x9867F, 0x986F5, 0x98772, 0x99C64, 0x9A55A, 0x9A56C,
)
SHEET_STRIDES_DX = (
    0x2653F, 0x265C7, 0x5AEA1, 0x61CD4, 0x61D07, 0x621CE, 0x62789, 0x628E0, 0x6294A, 0x62975,
    0x629A4, 0x629E5, 0x62C84, 0x6D258, 0x6E7CD, 0x6E8D6, 0x703D1, 0x74516, 0x82814, 0x8C6F0,
    0x94961, 0x94985, 0x949A9, 0x949E7, 0x94A09, 0x94A1F, 0x951BA, 0x954B4, 0x957E8, 0x958E9,
    0x95937, 0x95980, 0x95C22, 0x95C8A, 0x95D4A, 0x95D67,
)
SHEET_STRIDES = tuple(sorted(SHEET_STRIDES_AX + SHEET_STRIDES_DX))
GAME_SHEET_SIZE = 0x42
SPEC_MORE = 0x45  # (four more weapon specs: game.spec_more, DSCLOG2's SPEC_MORE)


# The program's constant-offset uses of a sheet (sheet 4's fields, the summoned ally's: PATCHES' sheet4_*):
# (file offset, the ES-prefixed opcode, the field, an immediate's bytes) for "opcode es:[bx+4 x 42h + field]".
SUMMON_SHEET = 4
SHEET4_FIELDS = (
    (0x866CF, 0x89, 0x0A, b""), (0x866D4, 0x89, 0x08, b""),  # (mov es:[bx+112h],ax; [bx+110h])
    (0x866FD, 0x88, 0x1E, b""),                               # (mov es:[bx+126h],al)
    (0x868E5, 0xC6, 0x36, b"\x04"), (0x868EB, 0xC6, 0x12, b"\x0e"),  # (mov byte es:[bx+13Eh],4; [bx+11Ah],0Eh)
)


def _sheet4(at: int, opcode: int, field: int, imm: bytes) -> Patch:
    def code(size: int) -> bytes:
        return bytes((0x26, opcode, 0x87)) + struct.pack("<H", SUMMON_SHEET * size + field) + imm
    return Patch("sheet4_%x" % at, at, code(GAME_SHEET_SIZE), code(0x48))


# GEAR_HANDS: a new character's starting gear (the creation screen's DONE, 6F197h; its giver 6EF49h) comes from
# a table of 3-byte entries (a word, the object in OBJEX.GFF's RDFF; a byte, the worn slot), file 43680h
# (selector 358h in the overlay), each class a range of it by the sheet's class flags (+12h, tested in this
# order): fighter 16h-1Ah, druid 7-8, gladiator 12h-15h, ranger 0Dh-11h, cleric 2-6, thief 1Fh-22h,
# psionicist 1Bh-1Eh, preserver 9-0Ch, a thri-kreen 0-1. The game put most classes' weapon in the left hand
# (slot 10), which swings once a round whatever the weapon specialization (the right hand, 3, is the one the
# attacks a round are counted for): a fighter's +1 long sword (633) behind its +1 shield (842) in the right,
# a cleric's club (609) behind its shield, and a druid's or psionicist's club and a preserver's +1
# quarterstaff (632) with the right hand empty. Each weapon goes to the right hand, the shield to the left
# (playtest/logs/2026-11-26-ravager-starting-gear.md); a gladiator's (two +1 long swords, 3 and 10), a
# ranger's and a thief's (a long sword in 3) and a thri-kreen's (its gythka in 3) as they were.
GEAR_TABLE_AT = 0x43680
GEAR_TABLE = bytes.fromhex(
    "dd0202" "760203"                                   # 0-1 a thri-kreen: chatkcha +1 (missile), gythka +1
    "4a0303" "61020a" "2a0309" "2f0300" "340306"        # 2-6 cleric: shield +1, club, chest, arms, legs
    "61020a" "de0202"                                   # 7-8 druid: club, sling +1
    "de0202" "78020a" "4d0609" "5c060c"                 # 9-0Ch preserver: sling +1, quarterstaff +1, chest, cloak
    "bc0202" "da0201" "2a0309" "2f0300" "5b0203"        # 0Dh-11h ranger: bow, arrows, chest, arms, long sword (603)
    "790203" "79020a" "2b0309" "350306"                 # 12h-15h gladiator: two long swords +1, chest, legs
    "4a0303" "79020a" "2c0309" "310300" "360306"        # 16h-1Ah fighter: shield +1, long sword +1, chest, arms, legs
    "61020a" "bc0202" "da0201" "2a0309"                 # 1Bh-1Eh psionicist: club, bow, arrows, chest
    "c10202" "790203" "2a0309" "64020e")                # 1Fh-22h thief: sling, long sword +1, chest, dagger (pack)
GEAR_RIGHT, GEAR_LEFT = 3, 10
# (entry, its new slot): the weapons to the right hand, the shields to the left
GEAR_HANDS = ((2, GEAR_LEFT), (3, GEAR_RIGHT), (7, GEAR_RIGHT), (0x0A, GEAR_RIGHT),
              (0x16, GEAR_LEFT), (0x17, GEAR_RIGHT), (0x1B, GEAR_RIGHT))


def gear_table_fixed() -> bytes:
    """GEAR_TABLE with GEAR_HANDS' slots."""
    table = bytearray(GEAR_TABLE)
    for entry, slot in GEAR_HANDS:
        table[entry * 3 + 2] = slot
    return bytes(table)


def _stride(at: int) -> Patch:
    modrm = 0xC0 if at in SHEET_STRIDES_AX else 0xD2
    return Patch("sheet_stride_%x" % at, at, bytes((0x6B, modrm, GAME_SHEET_SIZE)), bytes((0x6B, modrm, 0x48)))


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
    # ... and the routine's failure exit (2AF11h in the image, "jmp 2B1C0h") jumped to that "pop si", the
    # second byte of the patch (its NOP after the INT): SI was not restored. Sent instead to the same
    # "pop si / leave / retf" at 2B4F0h in the same segment (window_fail; SL's gamepatch has the same
    # jump into its window patch, 264FCh to 267ABh in SL's image)
    Patch("window_fail", 0x30111, bytes.fromhex("e9ac02"), bytes.fromhex("e9dc05")),
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
    # Shops as in AD&D (SL's price_buy, price_shown, price_afford, sell_price, sell_keep; game.RULE_CHA_PRICES,
    # always on): DSCLOG2's PRICE_CX at the price under an item (90E2Ah: "mov cx,es:[bx+6]", SL's 83BB1h),
    # PRICE_EAX at the price charged (90AA7h, SL's 8384Bh) and the list's affordable test (9036Ch, SL's
    # 8310Ch: "movzx eax,word es:[bx+6]"), SELL_PRICE at what the shop pays (90F4Dh, SL's 83CCAh) and
    # SELL_KEEP where it frees the item sold (91043h: "push word [1A32h]", SL's 83D9Eh)
    Patch("price_shown", 0x90E2A, bytes.fromhex("268b4f06"), _site(54, 4)),
    Patch("price_afford", 0x9036C, bytes.fromhex("66260fb74706"), _site(55, 6)),
    Patch("price_buy", 0x90AA7, bytes.fromhex("66260fb74706"), _site(55, 6)),
    Patch("sell_price", 0x90F4D, bytes.fromhex("66260fb74706"), _site(56, 6)),
    Patch("sell_keep", 0x91043, bytes.fromhex("ff36321a"), _site(57, 4)),
    # The game's message box (560h:2Ah: a scroll's YOU LEARN THE SPELL, a shop's I COULDN'T SELL THAT and
    # the rest) seen (a fix of the sequel's, whatever the rules: it was never drawn, and its wait was over at
    # once): DSCLOG2's MSG_WINDOW where its window is kept (59AD3h: "mov es:[9],dx", counted) and MSG_SHOWN
    # as its wait starts (59B62h: "mov ax,[26B7h]": the picture shown, the options' message time waited)
    # What the game shows as text, for the Loader's Dialogue and Journal tabs and the dice log's "Message:" lines
    # (SL's text and message, PROBE_TEXT and PROBE_MSG: DSCLOG2's TEXT): its "push bp / mov bp,sp" at the
    # start of the dialogue window's input (87BA0h, SL's 7CE83h: (kind, far text, word)) and of the message
    # box (59A0Bh, SL's 5536Eh: (far text)), each recorded into the text buffer (the header's +126 to +138)
    Patch("text", 0x87BA0, bytes.fromhex("558bec"), _site(93, 3)),
    Patch("message", 0x59A0B, bytes.fromhex("558bec"), _site(94, 3)),
    Patch("message_window", 0x59AD3, bytes.fromhex("2689160900"), _site(59, 5)),
    Patch("message_shown", 0x59B62, bytes.fromhex("a1b726"), _site(58, 3)),
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
    # ... and the routine's "immune" answer (7F362h, "mov ax,1 / jmp 7F8B1h") jumped to that "pop di",
    # the third byte of the site: the site number 10h, so "adc [bp-37h],bl", then the "retf" took DI:SI
    # for the return address, and the game quit with "Illegal Op (gpl=49)" when a spell met an immune
    # target (Ester's Charm Mammal in Tyr's ambush: playtest/logs/2026-11-25-ravager-illegal-op.md). Sent
    # instead to the same "pop di / pop si / leave / retf" at 7F2FEh, in the same overlay
    Patch("spell_hit_immune", 0x84565, bytes.fromhex("e94905"), bytes.fromhex("e996ff")),
    # Resting as in AD&D (SL's rest_hp; RULE_REST, always on): the rest's HP restore (8CF79h, "mov
    # [es:bx],ax", SL's 808AFh): DSCLOG2's REST_HP, a night's natural healing, 3 + CON's bonus
    Patch("rest_hp", 0x8CF79, bytes.fromhex("268907"), _site(17, 3)),
    # ... and the party's priests spending their spells left on the party first (SL's rest_spells): the
    # rest's first move (8CA82h, "mov word [bp-6],0", SL's 80675h), DSCLOG2's REST_PRE
    Patch("rest_spells", 0x8CA82, bytes.fromhex("c746fa0000"), _site(18, 5)),
    # Class restrictions (SL's PROBE_CAN_USE, PROBE_BELT's and THIEF_REAR's THIEF_HEAVY; RULE_RESTRICT,
    # always on): the end of "may this character equip it" (775FDh, "mov [bp-1],al", SL's 6EF34h),
    # DSCLOG2's CU_SITE (the classes' limits); the thief skill routine's end (8C7C5h, "mov ax,si / pop di",
    # SL's 803B2h), BELT_SITE (no skills in armour that isn't light); the backstab is taken back at the
    # "stealth" patch's MISSILE_REAR (THIEF_REAR)
    Patch("class_can_use", 0x775FD, bytes.fromhex("8846ff"), _site(19, 3)),
    Patch("thief_skill_armour", 0x8C7C5, bytes.fromhex("8bc65f"), _site(20, 3)),
    # ... whose "jmp 875C7h" (874C3h in the image) to that "pop di" landed on the site number 14h, so
    # the skill came back about 5Eh where the game's answer was 0: sent to the same "pop di / pop si /
    # leave / retf" at 87443h
    Patch("thief_skill_armour_out", 0x8C6C3, bytes.fromhex("e90101"), bytes.fromhex("e97dff")),
    # ... and a multiclass preserver casting in armour (SL's PROBE_NO_CAST): the "yes" of the casting case
    # (84F6Eh, "mov ax,1") of the sequel's "can this creature do it" (84E94h), DSCLOG2's CAST_ARMOUR
    Patch("cast_armour", 0x84F6E, bytes.fromhex("b80100"), _site(21, 3)),
    # Items saving against acid (SL's item_weapon, item_skip, item_armour; always on, game.RULES_ALWAYS):
    # DSCLOG2's ITEM SAVES, the game's acid and corroding touch on the first melee weapon (7CEC0h) and
    # worn armour (7D02Ah) needing the easier of its number and AD&D's for the item's material
    Patch("item_weapon", 0x7CF22, bytes.fromhex("ba08002b56fe"), _site(22, 6)),
    Patch("item_skip", 0x7D0AA, bytes.fromhex("837efe00"), _site(23, 4)),
    Patch("item_armour", 0x7D0BE, bytes.fromhex("ba0a002b56fe"), _site(24, 6)),
    # Multiclass hit points (SL's mc_con, mc_uncon; RULE_MULTI_HP, always on): the most hit points' CON
    # (95208h, "add di,ax / mov ax,di", SL's 87523h) and its reverse (954BDh, "mov dx,[es:bx+8] / sub
    # dx,ax", SL's 877DAh): DSCLOG2's MC_CON and MC_UNCON, CON's bonus on each die, the total shared
    Patch("mc_con", 0x95208, bytes.fromhex("03f88bc7"), _site(25, 4)),
    Patch("mc_uncon", 0x954BD, bytes.fromhex("268b57082bd0"), _site(26, 6)),
    # Creation's scores and hit points as rolled (SL's rl_*; game.RULE_ROLLED): the creation screen's
    # score click (6D1DDh, "mov al,[bp-2]", SL's 655C6h), hit point click (6B7D2h, "add ax,[bp-2]", SL's
    # 63A49h), the die's three loops (6D55Ah, 6D593h, 6D5CCh, "mov es:[bx+19h],al", SL's 65944h...),
    # CON's case (6B6CFh, "les bx,[1429h]", SL's 63946h) and the scores' redraw (6CD98h, "add sp,4", SL's
    # 65185h): DSCLOG2's RL_SCORE, RL_HP, RL_ROLL, RL_CON and RL_SUM; the scores' box (DS:11F4h, SL's
    # F62h) a line taller and wider for SUM (SL's rl_sum_box)
    Patch("rl_score", 0x6D1DD, bytes.fromhex("8a46fe"), _site(27, 3)),
    Patch("rl_hp", 0x6B7D2, bytes.fromhex("0346fe"), _site(28, 3)),
    Patch("rl_roll_4", 0x6D55A, bytes.fromhex("26884719"), _site(29, 4)),
    Patch("rl_roll_6", 0x6D593, bytes.fromhex("26884719"), _site(29, 4)),
    Patch("rl_roll_7", 0x6D5CC, bytes.fromhex("26884719"), _site(29, 4)),
    Patch("rl_con", 0x6B6CF, bytes.fromhex("c41e2914"), _site(30, 4)),
    Patch("rl_sum", 0x6CD98, bytes.fromhex("83c404"), _site(31, 3)),
    # ... and every try's 4d4 for the dice log (SL's rl_try, whatever the rule): DSCLOG2's RL_TRY (site 81) at the
    # ability's roll's "add ax,[42DAh]" (6C585h, SL's "add ax,[499Ah]" at 6498Bh), into its header's RL_TRIES
    Patch("rl_try", 0x6C585, bytes.fromhex("0306da42"), _site(81, 4)),
    Patch("rl_sum_box", DS_FILE + 0x11F8, struct.pack("<hh", 48, 178), struct.pack("<hh", 77, 185)),
    # STORE and RECALL (SL's roll_store, PROBE_RS_CLICK; rollstore.rav_chunks puts the buttons in the window):
    # the click routine's "mov cx,16h" as it looks the button up (6DE85h, SL's 6625Dh), DSCLOG2's RS_CLICK
    Patch("roll_store", 0x6DE85, bytes.fromhex("b91600"), _site(83, 3)),
    # Fuller starting gear (SL's GEAR_DUE and GEAR_HOLD at its cr_weapons' place): DONE's "pop cx / push si /
    # nop" between the game's gear for the new character and its roster write (6E2F2h, SL's 666DFh),
    # DSCLOG2's GEAR_DONE, which waits there for the Loader's gear (startgear.py)
    Patch("gear_done", 0x6E2F2, bytes.fromhex("595690"), _site(85, 3)),
    # AD&D's class tables (SL's xp_level_up, xp_view, priest_thac0, adnd_slots; game.RULE_ADND_TABLES,
    # always on): the eight reads of the XP table ("add sp,6 / imul eax,eax,64h", SL's "imul" at 87BBBh
    # and 67D41h), the THAC0 routine's group step (95391h, "mov [bp-2],ax", SL's 876ABh) and the slot
    # routine's call (62893h, "nop / push cs / call 2A10h", SL's 5E240h): DSCLOG2's XP_NEED, PRIEST_THAC0
    # and ADND_SLOTS, AD&D's tables to 20th level and the owner's to 30th (tables.RAV_*; XP_NEED answers
    # RAV_XP's past the game's 20 entries)
    *(Patch("xp_need_%x" % at, at - 3, bytes.fromhex("83c406666bc064"), _site(32, 7))
      for at in XP_READS),
    Patch("priest_thac0", 0x95391, bytes.fromhex("8946fe"), _site(33, 3)),
    # The level cap by XP (SL's level_up_cap, xp_view_cap, xp_next, thief_hd_*; game.RULE_LEVEL_10, always on,
    # with RAV_XP_CAP): the level up's "cmp byte es:[bx+1Eh],0Fh" (959A5h) and View Character's (6FB51h),
    # DSCLOG2's LV_UP and LV_VIEW (sites 110, 111: LEVEL_ROOM's share in place of the game's 15th); the level
    # up's hold on XP ("add ax,3", 958BDh), LV_CLAMP (112: none past RAV_XP's 30 entries); View
    # Character's ")" ("push 1386h", 6FC08h), XP_SUFFIX (117: the class the next XP is for); and a thief's
    # d6 to 10th (the hit die's "mov al,es:[bx+1]", 94FECh, and the most hit points' "cmp al,es:[bx+1]",
    # 95460h, and its "mov", 95471h: HD_ROLL, HD_CON, HD_CLAMP, 113-115; the psionicist's stays 9th)
    Patch("level_cap_up", 0x959A5, bytes.fromhex("26807f1e0f"), _site(110, 5)),
    Patch("level_cap_view", 0x6FB51, bytes.fromhex("26807f1e0f"), _site(111, 5)),
    Patch("level_clamp", 0x958BD, bytes.fromhex("050300"), _site(112, 3)),
    Patch("xp_suffix", 0x6FC08, bytes.fromhex("688613"), _site(117, 3)),
    # (the level up's message's "th", "mov ax,2B7Eh" at 959D3h: LV_ORDINAL, 118, "21st" past 20th)
    Patch("level_ordinal", 0x959D3, bytes.fromhex("b87e2b"), _site(118, 3)),
    Patch("thief_hd_roll", 0x94FEC, bytes.fromhex("268a870100"), _site(113, 5)),
    Patch("thief_hd_con", 0x95460, bytes.fromhex("263a870100"), _site(114, 5)),
    Patch("thief_hd_clamp", 0x95471, bytes.fromhex("268a870100"), _site(115, 5)),
    # ... and the saves as in AD&D (game.RULE_ADND_TABLES): the save routine's "mov al,es:[bx+6Ch]" (955DFh),
    # a group's 1st-level save, DSCLOG2's SAVE_BASE (116: the Player's Handbook's table, tables.rav_saves;
    # the game's own held every save at its table's last, a warrior at 11/11/11/13/11 from 10th)
    Patch("save_table", 0x955DF, bytes.fromhex("268a876c00"), _site(116, 5)),
    Patch("adnd_slots", 0x62893, bytes.fromhex("900ee87801"), _site(34, 5)),
    # CON as in AD&D (SL's regen_rate, con_save; game.RULE_CON): regeneration's rate (26599h, "mov dx,cx /
    # imul dx,dx,31h" after its "div ebx", SL's 228BFh) and CON's save adjustment (1D36Bh, "mov bx,ax /
    # mov al,[bx+880h]", SL's 5EAA1h): DSCLOG2's REGEN_SITE and CON_SAVE
    Patch("regen_rate", 0x26599, bytes.fromhex("8bd16bd231"), _site(35, 5)),
    Patch("con_save", 0x1D36B, bytes.fromhex("8bd88a878008"), _site(36, 6)),
    # Dual-classing as the manual has it (SL's dual_*; game.RULE_DUAL_CLASS, always on): the level DUAL
    # needs on the two portrait menus (7926Ch, 7948Bh) and in the DUAL window (94BCCh), "cmp byte
    # [es:bx+1Eh],2" (SL's 70CE4h, 70F03h, 86F58h), and the old and new class's prime requisite (94B70h,
    # 94BA5h, "cmp byte [es:bx+19h],0Fh" and "...,11h", SL's 86EFCh, 86F31h): DSCLOG2's DUAL_LEVEL and
    # DUAL_PRIMES
    Patch("dual_level_menu", 0x7926C, bytes.fromhex("26807f1e02"), _site(37, 5)),
    Patch("dual_level_view", 0x7948B, bytes.fromhex("26807f1e02"), _site(37, 5)),
    Patch("dual_level_window", 0x94BCC, bytes.fromhex("26807f1e02"), _site(37, 5)),
    Patch("dual_old_prime", 0x94B70, bytes.fromhex("26807f190f"), _site(38, 5)),
    Patch("dual_new_prime", 0x94BA5, bytes.fromhex("26807f1911"), _site(39, 5)),
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
    # ... and a ranger's ease only in light armour (SL's RG_TWO): DSCLOG2's site 78 at the routine's test for
    # a ranger (5DE67h, SL's 5961Fh: "test word es:[bx+10h],200h"), on to PROBE_TWO's penalty in armour not light
    Patch("ranger_two", 0x5DE67, bytes.fromhex("26f747100002"), _site(78, 6)),
    Patch("off_hand", 0x5CEE8, bytes.fromhex("b4008946f6"), gamepatch._interrupt(VEC_OFF_HAND, 5)),
    # Psionic Blast's imagined wounds (SL's psionic_blast and blast_knockout, PROBE_WORN's; always on, a game
    # bug fixed): DSCLOG2's BLAST_LOSS (site 79) where the effect routine's blast case keeps the loss
    # ("mov [bp-16h],dx", 6662Dh: SL's "or byte [si],1" at 79707h has no likeness here, its tail shared), into
    # BLAST_HP for psiblast.py to give back as the fight ends; BLAST_KO (site 80) before the damage routine's
    # death test ("add ax,0Ah", 5CC51h: SL's "cmp ax,dx" at 5860Bh, 5CC54h here), a knock-out while it is owed
    Patch("psionic_blast", 0x6662D, bytes.fromhex("8956ea"), _site(79, 3)),
    Patch("blast_knockout", 0x5CC51, bytes.fromhex("050a00"), _site(80, 3)),
    # Weapon specialization (SL's PROBE_ATTACKS and PROBE_SPEC_DAMAGE, game.RULE_SPECIALIZE, always on;
    # the transferred party's specs at the sheet's +42h..+44h): OFF_HAND above makes the attacks a round
    # and the THAC0 the skill's (DSCLOG2's SPEC_ATTACKS), and DSCLOG2's SPEC_DAMAGE (site 51) adds its
    # damage where the attack adds the strength bonus to the weapon's ("add [bp-14h],ax", 5CF6Dh, SL's 588F2h)
    Patch("spec_damage", 0x5CF6D, bytes.fromhex("0146ec"), _site(51, 3)),
    # Kits (SL's RULE_KITS, the transferred party's kits at the sheet's +3Dh): DSCLOG2's KIT_INIT (site 60)
    # at "add dx,14h" where a combatant's initiative for the round is made (5B7E9h, SL's PROBE_INIT site
    # 5750Eh: SI the creature); the rest of the kits' rules at the sites above (DSCLOG2's KITS)
    Patch("kit_initiative", 0x5B7E9, bytes.fromhex("83c214"), _site(60, 3)),
    # ... and KIT_RANGER_CAST (site 61) at the caster level routine's "sub dx,7" for a ranger class (97E00h,
    # SL's PROBE_RANGER_CAST at 81B6Ah): a Seeker's 5, a Justifier's 9 (RANGER_LEVEL has them for a spell's
    # duration and damage)
    Patch("kit_ranger_cast", 0x97E00, bytes.fromhex("83ea07"), _site(61, 3)),
    # ... and the creation panel's KIT pages (SL's PROBE_WP_* and PROBE_RACE_PANEL: kitpages.rav_chunks' windows
    # in the Loader's RESOURC2.GFF): DSCLOG2's KIT PAGE, sites 62-69. The creation overlay is SL's code at the
    # sequel's offsets (SL's in brackets): the disciplines' and spheres' windows opened ("push 4C30h", "push
    # 4C31h": 6FA45h, 6BEC2h [67BFBh, 6413Bh]), their clicks ("mov bx,[bp+8]": 6C096h, 6C036h [64311h,
    # 642B0h]), the spheres' window asked for ("cmp ax,8": 6B10Ah [6337Ah]), the routine after each click
    # ("mov cl,1 / les bx,[1429h]": 6E026h [66406h, "mov cx,1"]), a new race ("add sp,6": 6B191h [63403h]),
    # the screen opening ("mov byte [1C96h],0FFh": 6D891h [65C68h, CR_OPEN's])
    Patch("kp_disc_win", 0x6FA45, bytes.fromhex("68304c"), _site(62, 3)),
    Patch("kp_sphere_win", 0x6BEC2, bytes.fromhex("68314c"), _site(63, 3)),
    Patch("kp_disc_click", 0x6C096, bytes.fromhex("8b5e08"), _site(64, 3)),
    Patch("kp_sphere_click", 0x6C036, bytes.fromhex("8b5e08"), _site(65, 3)),
    Patch("kp_shown", 0x6B10A, bytes.fromhex("3d0800"), _site(66, 3)),
    Patch("kp_class", 0x6E026, bytes.fromhex("b101c41e2914"), _site(67, 6)),
    Patch("kp_race", 0x6B191, bytes.fromhex("83c406"), _site(68, 3)),
    Patch("kp_open", 0x6D891, bytes.fromhex("c606961cff"), _site(69, 5)),
    # ... and after DUAL (SL's PROBE_DUAL_KIT at 86D90h): DSCLOG2's DUAL_KIT (site 76) at "cmp word [bp+8],0Ch"
    # (94A57h) in the routine that changes a human's class (9493Ch), the new class's kit asked on the game's
    # three-choice menu
    Patch("dual_kit", 0x94A57, bytes.fromhex("837e080c"), _site(76, 4)),
    # Preservers' first spells and psionic powers at creation (SL's PROBE_CR_SPELLS, PSI_GRANT, PSI_ASK,
    # PSI_LIST, PSI_CYCLE; always on): DSCLOG2's FIRST SPELLS AND POWERS. The creation screen's DONE (6E0B9h,
    # SL's 6649Ch) gives the powers (6E906h [66CF1h]) and then a preserver's spells (6EA10h [66DF7h], the
    # sequel's own grants, some drawn by rand()): PSI_GRANT (site 88) at the powers' "cmp dx,-1" in both loops
    # (6E9C9h the psionicist's, 6E9F7h the others' [66DDEh]), CR_PICKS (site 87) at the spells' routine's end
    # ("cmp byte [bp-6],0", 6ED55h), which has the given spells and powers picked on the level up's CHOOSE A
    # SPELL (93160h [85560h]) and psionicists' pop-up (93B62h [85EECh]); in the pop-up PSI_COUNT (site 95,
    # "or dx,dx / jz", 93B95h [85F01h]), PSI_LIST (96, "or ax,ax / jz", 93E1Bh [86143h]), PSI_CYCLE (97, "inc
    # byte [bx-6285h]", 93FF1h [8631Ah]), PSI_CLICK (98, "or al,al / jz", 94245h); in CHOOSE A SPELL PICK_TOP
    # (99, "cmp ax,[bp-2]", 93831h: its level button) with PICK_ANY and PICK_PAGE for the levels on offer
    Patch("psi_grant_psionicist", 0x6E9C9, bytes.fromhex("83faff"), _site(88, 3)),
    Patch("psi_grant", 0x6E9F7, bytes.fromhex("83faff"), _site(88, 3)),
    Patch("cr_picks", 0x6ED55, bytes.fromhex("807efa00"), _site(87, 4)),
    Patch("psi_count", 0x93B95, bytes.fromhex("0bd2743a"), _site(95, 4)),
    Patch("psi_list", 0x93E1B, bytes.fromhex("0bc07422"), _site(96, 4)),
    Patch("psi_cycle", 0x93FF1, bytes.fromhex("fe877b9d"), _site(97, 4)),
    Patch("psi_click", 0x94245, bytes.fromhex("0ac07420"), _site(98, 4)),
    Patch("pick_top", 0x93831, bytes.fromhex("3b46fe"), _site(99, 3)),
    # ... and a warrior's weapon specs (SL's CR_WEAPONS, LV_CHECK and PROBE_PK_*; game.RULE_SPECIALIZE): DSCLOG2's
    # WEAPON PICKS. DONE's "push si / nop / push cs" before its call for the game's gear (6E2ECh, just before SL's
    # CR_WEAPONS' place, the screen's windows let go by then), CR_WEAPONS (site 120): the psionicists' pop-up in
    # weapon mode for the specs the new member is due, which shows the weapon window (weaponpages.rav_chunks,
    # RESOURC2.GFF's 3021) through PK_WIN (121, "push 445Dh", 93C94h [85FF4h]), PK_TITLE (122, "push ds / push
    # 2ACCh", 93D63h [860C3h]), PK_FILL (123, "xor di,di / mov si,di", 93DECh [8610Fh]), PK_CLICK (124, "mov
    # ax,[bp+8]", 93FABh [862D4h]) and PK_HOVER (125, "or ax,ax / jnz", 93BBAh [85F44h]); PSI_COUNT the picks left
    Patch("cr_weapons", 0x6E2EC, bytes.fromhex("56900e"), _site(120, 3)),
    # ... and at a level up (site 150, LV_WEAPONS: the level-up routine's "cmp word [bp+8],0Ch", 957BEh, between
    # the preserver's spell pick and the psionicist's power pick, SL's PROBE_LV_PICK's place): the weapon specs
    # due and not yet picked (a gladiator's 3rd to 8th, a fighter's second at 13th: the owner's 2026-11-26)
    Patch("lv_weapons", 0x957BE, bytes.fromhex("837e080c"), _site(150, 4)),
    Patch("pk_win", 0x93C94, bytes.fromhex("685d44"), _site(121, 3)),
    Patch("pk_title", 0x93D63, bytes.fromhex("1e68cc2a"), _site(122, 4)),
    Patch("pk_fill", 0x93DEC, bytes.fromhex("33ff8bf7"), _site(123, 4)),
    Patch("pk_click", 0x93FAB, bytes.fromhex("8b4608"), _site(124, 3)),
    Patch("pk_hover", 0x93BBA, bytes.fromhex("0bc07515"), _site(125, 4)),
    # ... and the Elementalist's second sphere (SL's EL_SPHERES and PROBE_EL_*): the sequel asks 62B45h
    # (spell, class) whether a class casts a priest spell each time, never with the character, so DSCLOG2's
    # EL_SPHERE (sites 90-92) answers yes for an Elementalist's cleric class and a spell of its second
    # sphere after each of its three callers that know the member: "add sp,4" (the call's words) after the
    # call in 62C00h (the USE screen's spells known, 62CAEh: the member DI), 628AFh (the cast's level,
    # 629BEh) and 97DC5h (the caster level, 97DE1h: both [BP+6]); the "or al,al" after kept.
    Patch("el_sphere_know", 0x62CAE, bytes.fromhex("83c404"), _site(90, 3)),
    Patch("el_sphere_level", 0x629BE, bytes.fromhex("83c404"), _site(91, 3)),
    Patch("el_sphere_cast", 0x97DE1, bytes.fromhex("83c404"), _site(92, 3)),
    # ... and a Shinobi's wizard slots (SL's PROBE_SLOTS: the Seeker's table by thief level): the slot
    # routine (626B7h) asks 62B45h (spell 8, the class) whether a class casts wizard spells before it asks
    # ADND_SLOTS (site 34) its slots; DSCLOG2's SHINOBI_MAGE (site 190) answers yes for a Shinobi's thief
    # class at its "add sp,4" (627D6h, the member SI), the "or al,al" after kept.
    Patch("shinobi_mage", 0x627D6, bytes.fromhex("83c404"), _site(190, 3)),
    # ... and the kits' casting levels, cures and spells known (SL's PROBE_SPELL_LEVEL, PROBE_CURE, AREA_DMG and
    # HARM_SITE's AV_CAUSE; the spells known are EL_SPHERE's, sites 90-92, and Cell Adjustment's CELL_HEAL's,
    # site 11): DSCLOG2's KIT_CAST_LEVEL (site 205) at the loop's "inc byte [bp-1]" in 628AFh (the level a spell
    # is cast at for its duration and damage: an Arcanist's wizard spells 1 higher, a Spirit Caller's and
    # Wasteland Seer's priest spells 2 higher under the open sky, 1 lower under a roof), KIT_CURE (site 206) at
    # the cures' "push ax / jmp 65811h" (66545h: a Healer's and Rescuer's 1 more a die, a Lifebinder's a die
    # more), AVENGER_AREA and AVENGER_ONE (sites 207, 208) where a spell's damage is stored after its roll
    # (7E7A6h "mov [bp-14h],ax", the area's; 7F727h "mov [bp-6],ax", one creature's: a Wilderness Avenger's
    # Cause Wounds 1 more a die)
    Patch("kit_cast_level", 0x629FE, bytes.fromhex("fe46ff"), _site(205, 3)),
    Patch("kit_cure", 0x66545, bytes.fromhex("50e9c8f2"), _site(206, 4)),
    Patch("avenger_cause_area", 0x7E7A6, bytes.fromhex("8946ec"), _site(207, 3)),
    Patch("avenger_cause_one", 0x7F727, bytes.fromhex("8946fa"), _site(208, 3)),
    # The DAM lines (SL's PROBE_DAM_LINE, PROBE_MISSILE_LINE, PROBE_VIEW_DAM): the inventory's line routine
    # (7AF9Eh, SL's 7286Ah) where it reads a melee weapon's attacks a round from the sheet (+24h, 7B19Eh)
    # and a missile weapon's from its type (+7, 7B124h), and View Character's where it stores the damage
    # bonus (6CAC9h): DSCLOG2's DAM_LINE, MISSILE_LINE and VIEW_DAM (sites 70-72) give the attack's numbers
    # with weapon specialization, the cahulaks' off head and the off hand's one a round.
    Patch("dam_line", 0x7B19E, bytes.fromhex("268a4724"), _site(70, 4)),
    Patch("missile_line", 0x7B124, bytes.fromhex("268a4707"), _site(71, 4)),
    Patch("view_dam", 0x6CAC9, bytes.fromhex("8956f2"), _site(72, 3)),
    # The Effects screen's lines (SL's PROBE_EF_ROWS, PROBE_EF_CLICK): the end of its routine that fills the
    # selected character's cells (8AC6Fh, SL's 7EDFAh: "pop di / pop si / leave" at 8AFA9h) and its handler for
    # them (8AB13h, SL's 7EC97h: "mov si,[bp+8]" at 8AB1Ah): DSCLOG2's EF_ROWS (site 73) lists the kits and
    # weapon kinds in the lower panel, EF_CLICK (site 74) shows their next page on a click there.
    Patch("ef_rows", 0x8AFA9, bytes.fromhex("5f5ec9"), _site(73, 3)),
    Patch("ef_click", 0x8AB1A, bytes.fromhex("8b7608"), _site(74, 3)),
    # The Look box's whole description (SL's PROBE_UNLOOK): where the routine that closes the box forgets whom
    # it looked at ("mov word [08CAh],270Fh", 6378Dh, SL's 5F2AAh), DSCLOG2's UNLOOK (site 75) shows the
    # Loader's description of the monster in the dialogue window.
    Patch("unlook", 0x6378D, bytes.fromhex("c706ca080f27"), _site(75, 6)),
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
    # Shattered Lands' shadows cast by the walls, drawn into the floor (DSCLOG2's WALL SHADOWS): the
    # two floor routines' starts, "push bp / mov bp,sp / sub sp,N" (SL's 2700Eh and 27162h, the same
    # frames), DSCLOG2's sites 40 and 41 (SITE_FLOOR_ALL, SITE_FLOOR_RECT), their way back its FLOOR_POST.
    Patch("floor_all", 0x2B81C, bytes.fromhex("558bec83ec1c"), _site(40, 6)),
    Patch("floor_rect", 0x2B97F, bytes.fromhex("558bec83ec1e"), _site(41, 6)),
    # Choosing an enemy with Tab, Enter attacking it (SL's PROBE_HIT, DSCLOG's TARGETING): the start of
    # the routine finding the thing under the pointer (21E0:2DBD, 29DBDh, SL's 25B52h: "push bp / mov
    # bp,sp / sub sp,0Eh"), DSCLOG2's site 77 (SITE_HIT): for a moment after Enter's click, the chosen enemy.
    Patch("hit", 0x29DBD, bytes.fromhex("558bec83ec0e"), _site(77, 6)),
    # F10 in a fight leaves a pinned member where it is (SL's F10_PIN, DSCLOG's): the F10 key's standing-still
    # test (1EC05h, SL's 1B83Ah, from the map's key table at 1F091h), "mov ah,0 / or ax,ax / jz 1EC3Fh"
    # (1EC36h, SL's "or ax,ax / jz" at 1B86Bh), DSCLOG2's site 100 (SITE_F10_PIN): the move taken back only
    # for a member neither Paralyzed (69) nor Cannot Move (66), the effects whose landing clears "can walk".
    Patch("f10_pin", 0x1EC36, bytes.fromhex("b4000bc07403"), _site(100, 6)),
    # Quick saves (DSCLOG2's QUICK SAVES, quicksave.py): the load's wrapper (7D8EEh on) reads the slot's GREQ
    # chunk (the map's limits, in the roster file) numbered by "mov ax,es:[2]" (the window's first row) + the row
    # + 1; DSCLOG2's site 84 (SITE_GREQ_LOAD) adds GREQ_QUICK on the quick saves' page, whose saves DSCLOG2
    # numbers so (GREQ_WRITE).
    Patch("greq_load", 0x7DA30, bytes.fromhex("26a10200"), _site(84, 4)),
    # S on a shop's screen sells the member's plain gear (DSCLOG's SELL_KEY, SHOP_LOOP; sell.py): the test of
    # the shop's own loop (88D52h, "while byte [143Dh] is 1", 143Dh set at 7BCA6h for a merchant's shop; SL's
    # word [11B2h] at 7DE11h), DSCLOG2's site 82 (SITE_SHOP_LOOP): the BIOS tick kept while the shop is open.
    Patch("shop_loop", 0x88D99, bytes.fromhex("803e3d1401"), _site(82, 5)),
    # The game's 7 reads of an item's name, "push dword [bx+56F3h]" (its table of 256 far pointers):
    # DSCLOG2's SITE_NAME, names 256 on the Loader's (NAMES_GAME, item_names).
    *(Patch("item_name_%x" % at, at, bytes.fromhex("66ffb7f356"), _site(42, 5))
      for at in NAME_READS),
    # AD&D's rings, cloaks, bracers and robes of protection (SL's RULE_PROTECTION, always on; the party
    # transfer's items): DSCLOG2's PROT_AC at the AC function's test of whether a worn item counts
    # (5D61Ah: "mov al,es:[bx+0Bh] / mov ah,0", SL's PROBE_RING_AC at 58EBDh) and PROT_SAVE at the
    # start of the save modifiers (8360Eh: "mov si,[bp+6] / xor di,di", SL's PROBE_RING_SAVE at 79D47h).
    Patch("protection_ac", 0x5D61A, bytes.fromhex("268a470bb400"), _site(43, 6)),
    Patch("protection_save", 0x8360E, bytes.fromhex("8b760633ff"), _site(44, 5)),
    # the Amulet of Magic Resistance (SL's AMULET_MR): DSCLOG2's site 45 at the magic resistance routine's
    # "cmp word [bp-2],0" (84B24h, SL's 7A4FDh), its 15% added first (the girdles: ITEM_REAR, from MISSILE_REAR)
    Patch("amulet_resistance", 0x84B24, bytes.fromhex("837efe00"), bytes((0xCD, VEC_SITE, 45, 0x90))),
    # a weapon's spell on a hit rolls no attack (SL's ARROW_LEVEL, TH_WEAPON): DSCLOG2's WEAPON_CAST
    # makes the cast's pushes of its level and spell ("push 6 / push word [bp-18h]", 5D2C2h, SL's
    # 58BE6h) and marks the cast a weapon's for TH_CAST
    Patch("weapon_cast", 0x5D2C2, bytes.fromhex("6a06ff76e8"), _site(46, 5)),
    # a spell arrow shot by a party member with no preserver class: a plain arrow (DSCLOG2's PLAIN_ARROW)
    Patch("plain_arrow", 0x5D248, bytes.fromhex("8946e8ff4ee8"), _site(49, 6)),
    # A worn item's spell never ended when the item was taken off (SL's does: its 6F8B9h): the unready
    # routine (77CDBh, the item's +10h less 1 in DX) skips the removal (628h:BBh, 864EDh: the wearer's
    # effects of that spell) with "cmp dx,-1 / jbe" (77D0Fh), an unsigned compare every spell passes
    # (the C's "spell > -1" on an unsigned): jbe made jle (logs/2026-11-23-ravager-worn.md)
    Patch("worn_spell_off", 0x77D12, bytes.fromhex("7610"), bytes.fromhex("7e10")),
    # a member added from the roster (the ADD screen, 58CB5h) wears its items with no spell on, the
    # game putting one on only as an item is readied: DSCLOG2's JOIN_READY readies each worn item with
    # a spell (77C1Ah) at "cmp byte [13FAh],0" (58D81h), right after the character's CHAR is loaded
    Patch("join_ready", 0x58D81, bytes.fromhex("803efa1300"), _site(47, 5)),
    # the Tome of Understanding (SL's tome, DSCLOG's PROBE_TOME), as the transfer makes it (ravtransfer's
    # WOTR_TOME_SPELL): DSCLOG2's TOME at "dec word [bp-4]" (999CDh) where a scroll's clicked icon reads
    # the item's power, a point of WIS for the reader and the tome used up
    Patch("tome", 0x999CD, bytes.fromhex("ff4efc"), _site(48, 3)),
    # The two sound numbers on a sheet, +3Ch and +3Eh (SL's +42h and +44h), read as words, though the
    # bytes above them are the mod's (the transfer's kit byte +3Dh and second sphere / new spells +3Fh,
    # SL's +43h and +45h: kitpages.KIT_BYTE, kits.SPHERE2 in ravlog's layout): the low byte alone, as
    # SL's sound_42 and sound_44 (DSCLOG's PROBE_SOUND_*), but in place, no helper code: "xor ax,ax /
    # or al,es:[bx+N]" (ZF as the game's "or ax,ax" had it), then the game's own move. These are the
    # sequel's only reads of +3Ch..+3Fh (every decode of the program with those displacements, ES or
    # not, 2026-11-24; the other two, 8ACB7h and 8ADA5h, read +3Ch as a byte already). A kit in +3Dh read
    # whole made sound 100h or 8100h, "Mel Fatal Error" (playtest/logs/2026-11-24-ravager-quit-hunt.md).
    # A member's turn in a fight (6012Ah in the image: "mov dx,es:[bx+3Ch] / mov ax,dx / or ax,ax",
    # 62h when 0, pushed to the sound routine B8h:0A22h):
    Patch("sound_3c", 0x65333, bytes.fromhex("268b573c8bc20bc0"), bytes.fromhex("33c0260a473c8bd0")),
    # ... and 89859h in the image ("mov ax,es:[bx+3Eh] / mov [bp-4],ax / or ax,ax", its low byte pushed)
    Patch("sound_3e", 0x8EA59, bytes.fromhex("268b473e8946fc0bc0"), bytes.fromhex("33c0260a473e8946fc")),
    # The 48h sheet (SHEET_SIZE, above): the strides,
    *(_stride(at) for at in SHEET_STRIDES),
    # ... the loop over the party's four sheets at 1C57Bh in the image ("add di,42h", beside the
    # creatures' "add si,31h"),
    Patch("sheet_party_loop", 0x2177B, bytes.fromhex("83c742"), bytes.fromhex("83c748")),
    # ... the table's allocation (6DE4Dh: "push dword 462h" to the far heap's 1D0h:8, 17 sheets, its
    # pointer to [19C5h]; freed at 6E0D5h, no size there): 17 x 48h,
    Patch("sheet_table", 0x7304D, bytes.fromhex("666862040000"), bytes.fromhex("6668c8040000")),
    # ... the record sizes by kind (6DD62h: "mov word es:[616Dh],42h" in 6D0h's table at 6169h, the
    # sheets' beside the items' 17h and the creatures' 31h; the record writer at 1F6BDh puts it in a
    # record's header, and the generic accessors at AA46h, AB66h, AC46h, 1E259h and 1F6AEh step by it):
    # a CHARSAVE or SAVE file's sheet record is written 48h long,
    Patch("sheet_record_size", 0x72F62, bytes.fromhex("26c7066d614200"), bytes.fromhex("26c7066d614800")),
    # ... a sheet record read from a file into its slot (6B17Ch: "push 42h" to memcpy 0:3F5Ah, from
    # the record's data: an ADD from the roster, a map's monsters from OBJEX.GFF's RDFF): 48h, so the
    # files' records must be 48h too (widened: the Loader's OBJEX copy, objects_fixed, and the game
    # folder's files, widen_files),
    Patch("sheet_record_load", 0x7037C, bytes.fromhex("6a42"), bytes.fromhex("6a48")),
    # ... a save game's chunk sizes (a dword table at selector 378h:0, file 3F38h x 16 + 5200h; SAVE 6,
    # the sheets' table, 462h at +14h; a load reads the chunk whole, length -1): 48h x 17,
    Patch("sheet_save_size", 0x44594, bytes.fromhex("62040000"), bytes.fromhex("c8040000")),
    # ... and a character made on the creation screen: its template (360h:29h, 42h bytes, the creature's
    # at 360h:6Bh right after it, so the three copies of 42h between it and a sheet, 6950Bh, 69560h and
    # 69C67h, stay 42h: an edit keeps the sheet's +42h..+47h as they were) copied into a new slot at
    # 69560h, whose last six bytes would be the slot's last owner's: DSCLOG2's NEW_SHEET clears them at
    # the "add sp,0Ah" after that memcpy (6957Dh in the image).
    Patch("sheet_new_tail", 0x6E77D, bytes.fromhex("83c40a"), _site(50, 3)),
    # ... and sheet 4 by a constant offset (no stride: "les bx,[19C5h]" then es:[bx+4 x 42h + field]), the
    # summoned ally's (creature and sheet 4, the slot after the party's four): the summoning spells'
    # routine (81515h in the image: Conjure Elemental, Monster Summoning, Dustdevil...) gives it race 0Eh
    # (+12h) and 4 at +36h, Mordenkainen's Sword (58h, 814A1h) its level (+1Eh), Bigby's Clenched Fist (5Ch)
    # the caster's +08h in its +08h and +0Ah. Left 42h-based they went to sheet 3's +38h, +3Ah and +42h and
    # sheet 4's +06h and +1Eh (found hunting the "Illegal Op (gpl=49)" quit in Tyr's ambush, though not
    # its cause, spell_hit_immune: playtest/logs/2026-11-25-ravager-illegal-op.md). Each 4 x 48h + field:
    *(_sheet4(at, opcode, field, imm) for at, opcode, field, imm in SHEET4_FIELDS),
    # Thieves as in AD&D (SL's RULE_THIEF_TABLE, always on): a thief skill from AD&D's table and Dark Sun's
    # DEX adjustment, "mov ax,si / shl ax,2 / add dx,ax / mov si,dx" (8C716h, SL's thief_skill at 80307h,
    # the same bytes) made DSCLOG2's site 52 (THIEF_SKILL) and "jc" past the game's DEX formula to its
    # armour and effects (8C795h); and a backstab multiplying the weapon's dice only (SL's stab_times):
    # "push ax / mov ax,[bp-4] / pop dx / imul dx / mov [bp-4],ax" (5D11Bh, SL's 58A80h, the same bytes),
    # DSCLOG2's STAB_TIMES (site 53), the dice from ENL_ROLL (the enlarge_roll patch, SL's stab_roll's
    # site); with the kits (RULE_KITS) an Assassin's multiplier one more there (SL's kit rule, x3 to x6)
    Patch("thief_table", 0x8C716, _SL["thief_skill"].original,
          bytes((0xCD, VEC_SITE, 52, 0x72, 0x8C795 - 0x8C71B)) + b"\x90" * 4),
    Patch("backstab_dice", 0x5D11B, _SL["stab_times"].original, _site(53, 10)),
    # A new character's weapon in the weapon hand (GEAR_HANDS, below): the starting gear's table, its slots
    # changed (data, no helper code)
    Patch("gear_hands", GEAR_TABLE_AT, GEAR_TABLE, gear_table_fixed()),
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
CREATURE_SIZE, SHEET_SIZE, ITEM_SIZE = 0x31, 0x48, 0x17  # (SL's 3Ah, 47h, 15h; the sheet the Loader's: GAME_SHEET_SIZE)
DGROUP = 0x47E0  # its DS less its load segment (4982h - 1A2h in a GOG start; SL's 4356h)
WHOSE_TURN, CAMERA, MAP_OBJECTS = 0x426D, 0x1408, 0x67BB  # (SL's 4979h, 1178h, 6694h; the map objects 25h bytes apart)
SPELL_SLOTS, SLOTS_STRIDE, PRIEST_SLOTS = 0x446A, 0x22, 0x0B  # wizard casts left by level, a member a row
KNOWN_BITSET = 15  # bytes of known wizard spells a member (bit n, spell n), the roster's SPST chunk
# ... at selector 320h:39Ch (the load + 3D62h), a member's after another's (DSCLOG2's KNOWN_BITS); the
# game's spells are bits 0-114, 115-119 unused (playtest/RESEARCH.md: the starting age's roll was kept
# there before the sheet was made 48h, SHEET_SIZE)
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
    if 0x14 <= sl <= 0x16:
        return sl + 0x2E       # the mod's weapon specs and starting roll -> 42h, the Loader's bytes (SHEET_SIZE)
    return None                # 0Eh-0Fh, 17h (the mod's age: +41h, ravlog's SHEET_AGE), 3Ch: none in the sequel


# The priests' spheres in the sequel: a byte a priest spell (73h-EAh; DSUN.EXE's data at selector 3D0h:7D3h,
# SPHERES_FILE) met by its class's (62B45h's jump table: a cleric's EVERY_PRIEST and its element's, a druid's
# DRUIDS too, a ranger's as its element's cleric, class 19 all), asked each time a priest spell is listed or
# cast (DSCLOG2's EL_SPHERE).
SPHERES_FILE = 0x41F1 * 16 + 0x5200 + 0x7D3
PRIEST_SPELLS = range(0x73, 0xEB)
AIR, EARTH, FIRE, WATER, EVERY_PRIEST, DRUIDS = 1, 2, 4, 8, 0x10, 0x20


def class_spheres(cls: int) -> int:
    """The sphere bits class CLS (the sheet's 1-19) casts by: 62B45h's."""
    if 1 <= cls <= 4 or 13 <= cls <= 16:
        return EVERY_PRIEST | 1 << (cls - 1) % 4
    if 5 <= cls <= 8:
        return DRUIDS | EVERY_PRIEST | 1 << (cls - 5)
    return 0x3F if cls == 19 else 0


# The kits' spells in the sequel's numbers (RESOURCE.GFF's names; DSCLOG2's AV_HEALS, AV_HARMS, CURE_DICE,
# AV_CAUSES): the healing spells a Wilderness Avenger never knows (kits.AVENGER_NO_HEAL: Cure Light Wounds,
# Blood Flow, Cure Serious and Critical Wounds, Heal, Waters of Life), the harming ones a Healer or Lifebinder
# never knows (kits.NO_HARM: Cause Light, Serious and Critical Wounds, Cause Disease, Poison, Slay Living,
# Harm), the cures' dice (kits.CURE_DICE: the game's own +1 and +3 on Cure Serious and Critical Wounds are
# its, not a die's) and the Cause Wounds spells' (kits.CAUSE_DICE)
RAV_CURE_LIGHT, RAV_CURE_SERIOUS, RAV_CURE_CRITICAL, RAV_BLOOD_FLOW = 117, 170, 194, 166
RAV_CAUSE_LIGHT, RAV_CAUSE_SERIOUS, RAV_CAUSE_CRITICAL = 118, 171, 195
RAV_HEAL, RAV_WATERS_OF_LIFE, RAV_HARM = 210, 215, 211
RAV_CAUSE_DISEASE, RAV_POISON, RAV_SLAY_LIVING = 149, 179, 204
RAV_AVENGER_NO_HEAL = frozenset((RAV_CURE_LIGHT, RAV_BLOOD_FLOW, RAV_CURE_SERIOUS, RAV_CURE_CRITICAL, RAV_HEAL,
                                 RAV_WATERS_OF_LIFE))
RAV_NO_HARM = frozenset((RAV_CAUSE_LIGHT, RAV_CAUSE_SERIOUS, RAV_CAUSE_CRITICAL, RAV_CAUSE_DISEASE, RAV_POISON,
                         RAV_SLAY_LIVING, RAV_HARM))
RAV_CURE_DICE = {RAV_CURE_LIGHT: (1, 8), RAV_CURE_SERIOUS: (2, 8), RAV_CURE_CRITICAL: (3, 8), RAV_BLOOD_FLOW: (2, 6)}
RAV_CAUSE_DICE = {RAV_CAUSE_LIGHT: 1, RAV_CAUSE_SERIOUS: 2, RAV_CAUSE_CRITICAL: 3}
RAV_WIZARD_LAST = 0x72  # (the wizard spells, 0-72h; the priests' 73h-EAh, PRIEST_SPELLS)
# A Healer's sphere of the cosmos in the sequel: the spells every druid casts and no cleric (a sphere byte with
# DRUIDS: Cure Serious and Critical Wounds, Free Action, Neutralize Poison, Raise Dead, Heal and the rest), and
# Whirlwind and Restore Youth, which Shattered Lands' Healer casts at 6th level: they aren't in the sequel yet,
# and their numbers go here (and in DSCLOG2's COSMOS_MORE, the header's +2060) once they are ported.
RAV_COSMOS_MORE = {"Whirlwind": None, "Restore Youth": None}


def healer_cosmos(sheet: bytes, cls: int, spell: int, sphere: int) -> bool:
    """Whether class CLS of SHEET is a Healer's own cleric class (1-4) and SPELL (its sphere byte SPHERE) one
    of the sphere of the cosmos's (DRUIDS, or RAV_COSMOS_MORE's): DSCLOG2's HEALER_COSMOS."""
    from . import kitpages, kits
    if kits.HEALER not in kitpages.kit_ids(sheet) or kitpages.kit_class_of(sheet, kits.HEALER) != cls \
            or not 1 <= cls <= 4:
        return False
    if spell in {s for s in RAV_COSMOS_MORE.values() if s is not None}:
        return True
    return spell in PRIEST_SPELLS and bool(sphere & DRUIDS)


def kit_barred(sheet: bytes, spell: int) -> bool:
    """Whether SHEET's kit never knows SPELL (kits.knows_heal in the sequel's numbers): DSCLOG2's KIT_BARS."""
    from . import kitpages, kits
    kids = kitpages.kit_ids(sheet)
    if kits.AVENGER in kids:
        return spell in RAV_AVENGER_NO_HEAL
    return bool({kits.HEALER, kits.LIFEBINDER} & set(kids)) and spell in RAV_NO_HARM


def casts(sheet: bytes, cls: int, spell: int, sphere: int) -> bool:
    """Whether class CLS of SHEET casts priest spell SPELL (its sphere byte SPHERE): the game's answer, and
    with the kits an Elementalist's (kits.spell_spheres): its own cleric class casts its second sphere's
    spells too (kits.SPHERE2's low bits: the sheet's +3Fh in ravlog's layout, which SHEET is read in); a
    Healer's own cleric class the sphere of the cosmos's (healer_cosmos); none that its kit never knows
    (kit_barred). DSCLOG2's EL_SPHERE."""
    from . import kitpages, kits
    yes = bool(sphere & class_spheres(cls)) or healer_cosmos(sheet, cls, spell, sphere)
    if not yes and spell in PRIEST_SPELLS and kits.ELEMENTALIST in kitpages.kit_ids(sheet) \
            and kitpages.kit_class_of(sheet, kits.ELEMENTALIST) == cls:
        second = sheet[kits.SPHERE2] & kits.SPHERE2_MASK
        yes = 1 <= second <= 4 and bool(sphere & 1 << (second - 1))
    return yes and not kit_barred(sheet, spell)


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


KIT_PAGES = "kit_pages"  # (resources_fixed's name for the kit pages, a SKIP's to leave them out)
ROLL_BUTTONS = "roll_buttons"  # (... for STORE and RECALL on the creation screen: rollstore.rav_chunks)
WEAPON_WINDOW = "weapon_window"  # (... for the weapon window: weaponpages.rav_chunks)


def resources_fixed(data: bytes, skip=frozenset(), objects: Optional[bytes] = None) -> Tuple[bytes, List[str]]:
    """RESOURCE.GFF's bytes with the spell fixes (spell_fixed), the creation panel's kit pages
    (kitpages.rav_chunks: the windows DSCLOG2's KIT PAGE opens, KIT_PAGES), the creation screen's STORE
    and RECALL (rollstore.rav_chunks, ROLL_BUTTONS) and the weapon window (weaponpages.rav_chunks, its
    pictures from OBJECTS, the game's OBJEX.GFF: WEAPON_WINDOW; none without it) unless in SKIP; the
    names of those applied."""
    from . import icons, kitpages
    out, done = spell_fixed(data, skip)
    if WEAPON_WINDOW not in skip and objects:  # (DSCLOG2's WEAPON PICKS opens it: sites 120-125)
        from . import weaponpages
        try:
            added = weaponpages.rav_chunks(gff.read_gff(out), gff.read_gff(objects))
        except (KeyError, ValueError, IndexError, struct.error, gff.GffError):
            added = {}  # (no psionicists' window to make it from: none, the picks never asked)
        if added:
            out = icons.with_chunks(out, added)
            done.append(WEAPON_WINDOW)
    if KIT_PAGES not in skip:
        try:
            added = kitpages.rav_chunks(gff.read_gff(out))
        except (KeyError, ValueError, IndexError, StopIteration, struct.error):
            added = {}  # (a RESOURCE.GFF without the panel's windows: no kit pages, KITS never shown)
        if added:
            out = icons.with_chunks(out, added)
            done.append(KIT_PAGES)
    if ROLL_BUTTONS not in skip:  # (STORE and RECALL: DSCLOG2's RS_CLICK, site 83)
        from . import rollstore
        try:
            added = rollstore.rav_chunks(gff.read_gff(out))
        except (KeyError, ValueError, IndexError, struct.error):
            added = {}  # (no such buttons to copy: the screen as the game has it)
        if added:
            out = icons.with_chunks(out, added)
            done.append(ROLL_BUTTONS)
    return out, done


def write_resources(game_dir: str, dest: str, skip=frozenset()) -> List[str]:
    """RESOURCE.GFF's copy with the spell fixes, kit pages and weapon window (resources_fixed, the weapons'
    pictures from the game's OBJEX.GFF), written to DEST unless already so; the fixes applied."""
    source = _find_file(game_dir, OBJECTS_FILE)
    objects = None
    if source:
        with open(source, "rb") as f:
            objects = f.read()
    return _write_copy(game_dir, RESOURCE_FILE, dest, lambda d, s: resources_fixed(d, s, objects), skip)


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


# The item types: OBJEX.GFF's ALL 4, the sequel's 102 types (15 bytes each: ravlog.TYPE_FIELDS), read into
# memory at the chunk's own length (a copy with 3 more had 105 there, the item names' block after them,
# 2026-11-22: playtest/logs/2026-11-22-ravager-item-types.md). The copy adds the mod's 33 (Shattered Lands'
# 115-147, npcitems.TYPES, DSCLOG's EXTRA_TYPES) after them, as MOD_TYPES on: the party transfer's items
# of those types take 102 on (mod_type).
TYPES_CHUNK = ("ALL ", 4)
TYPE_SIZE = 15
GAME_TYPES = 102
MOD_TYPES = 33  # (npcitems.TYPES)


def wotr_type(sl: bytes) -> bytes:
    """A Shattered Lands item type (20 bytes) in the sequel's layout: its words at +2, +4 and +6 as
    bytes (none of the mod's is over 255), +8 to +12h one for one, its last byte gone."""
    out = bytearray(TYPE_SIZE)
    for at, to in ((0, 0), (2, 1), (4, 2), (6, 3)):
        word, = struct.unpack_from("<H", sl, at)
        if word > 0xFF:
            raise RavagerError(f"an item type's word {word} at +{at:X}h doesn't fit the sequel's byte")
        out[to] = word
    out[4:TYPE_SIZE] = sl[8:8 + TYPE_SIZE - 4]
    return bytes(out)


# The sequel's item types' weapon kinds (specialize.KINDS' numbers: DSCLOG2's KIND_OF_TYPE, less 1), from
# OBJEX.GFF's items' names, dice and two-handed bit: its own (the Longswords, Flameblade, Magma blade; Club,
# Toothed Club; the Daggers; Maces; Axes; Great Axe; Pick; Quarterstaff; Polearm; Gythka; Cahulaks; Chatchka;
# Bow; Sling; Staff Sling; and SL's six kinds from the sequel: the Twohand Sword and the Crystal sword, both
# two-handed 1d10; Lotulis; Double Spear; Trikal; Javelin; the two Darts), and the mod's (mod_type: SL's
# 115-147, specialize.KIND_OF_TYPE's; none of the six, whose SL types are past them: sequel_weapon_type).
# ravlog's layout makes it specialize.KIND_OF_TYPE while the sequel is attached.
_RAV_OWN_KINDS = {
    "long sword": (16, 47, 69, 73, 97), "club": (29, 89), "dagger": (37, 72, 99), "mace": (67, 74),
    "axe": (8, 48), "great axe": (51,), "pick": (79,), "quarterstaff": (85,), "polearm": (80,),
    "gythka": (52,), "cahulaks": (24,), "chatkcha": (25,), "bow": (18,), "sling": (93,), "staff sling": (98,),
    "two-handed sword": (101, 35), "lotulis": (61,), "double spear": (39,), "trikal": (100,),
    "javelin": (59,), "darts": (38, 43)}


def rav_kinds() -> Dict[int, int]:
    """The sequel's item types' weapon kinds (_RAV_OWN_KINDS, and the mod's types SL's)."""
    from . import specialize
    out = {t: specialize.KINDS.index(kind) for kind, types in _RAV_OWN_KINDS.items() for t in types}
    for kind, types in specialize._TYPES.items():  # (SL's, whatever ravlog's layout has made KIND_OF_TYPE)
        out.update({mod_type(t): specialize.KINDS.index(kind) for t in types
                    if game.GAME_TYPES <= t < game.GAME_TYPES + MOD_TYPES})
    return out


# The sequel's weapons with no kind of SL's 22, and the kind each counts as for weapon specialization alone
# (DSCLOG2's SPEC_KINDS_OWN; as SL's spell-made weapons, specialize.CONJURED_KINDS, which ravlog's
# layout makes these): the nearest of SL's kinds, the reasoning in DEVELOPMENT-RULES.md
_RAV_SPEC_KINDS = {
    13: "long sword",  # Bloodletter (a 1d8 blade)
    81: "mace", 68: "mace", 95: "mace",  # Promere hammer, Jasmine, Spirit hammer (the spell's)
    90: "club",  # Shillelagh (the spell's)
    87: "bow",  # Rainbow (the spell's bow)
}


def rav_spec_kinds() -> Dict[int, int]:
    """_RAV_SPEC_KINDS by specialize.KINDS' numbers."""
    from . import specialize
    return {t: specialize.KINDS.index(kind) for t, kind in _RAV_SPEC_KINDS.items()}


# Shattered Lands' types past the mod's first 33 (SL_WEAPON_TYPES' kinds: the sequel's own weapons
# backported, their metal and magic ones): in the sequel the sequel's own type of that weapon, by its
# kind (specialize.KINDS' two-handed sword, lotulis, double spear, trikal, javelin, darts)
SEQUEL_WEAPON_OF_KIND = {16: 101, 17: 61, 18: 39, 19: 100, 20: 59, 21: 43}


def sequel_weapon_type(sl_type: int) -> Optional[int]:
    """The sequel's own type for SL_TYPE when it is one of the Ravager weapons backported to
    Shattered Lands (past MOD_TYPES), else None."""
    from . import specialize
    if sl_type < game.GAME_TYPES + MOD_TYPES:
        return None
    return SEQUEL_WEAPON_OF_KIND.get(specialize.KIND_OF_TYPE.get(sl_type, -1))


def mod_type(sl_type: int) -> int:
    """The sequel's number for the mod's Shattered Lands item type SL_TYPE (115 on)."""
    return GAME_TYPES + sl_type - game.GAME_TYPES


def mod_types_table(types: bytes) -> bytes:
    """The sequel's type table TYPES (ALL 4) with the mod's after it."""
    from . import npcitems
    return types + b"".join(wotr_type(t) for t in npcitems.TYPES[:MOD_TYPES])


def objects_fixed(data: bytes, skip=frozenset(), added: Optional[gff.Chunks] = None,
                  gear: Optional[Callable[[gff.Chunks], gff.Chunks]] = None) -> Tuple[bytes, List[str]]:
    """OBJEX.GFF's bytes with the mod's item types after the sequel's (unless "mod_types" is in SKIP),
    ADDED's objects (the party transfer's: ravitems; but its names chunk) unless "transfer_items" is, and
    the mod's new items (GEAR(the sequel's chunks): ravgear's, its people's and things' objects with
    them) unless "new_items" is (or the mod's types are left out: they are its types)."""
    from . import icons, ravitems
    chunks = gff.read_gff(data)
    types = chunks.get(TYPES_CHUNK)
    if types is None or len(types) != GAME_TYPES * TYPE_SIZE:
        raise RavagerError(f"{OBJECTS_FILE}'s item types are not the GOG release's")
    new: gff.Chunks = {}
    done: List[str] = []
    if "mod_types" not in skip:
        new[TYPES_CHUNK] = mod_types_table(types)
        done.append("mod_types")
    if added and "transfer_items" not in skip:
        new.update({k: v for k, v in added.items() if k[0] in ravitems.OBJECT_KINDS})
        done.append("transfer_items")
    if gear and "new_items" not in skip and "mod_types" not in skip:
        made = gear(chunks)  # (a transfer's picture object of the same number is the same picture: kept)
        new.update({k: v for k, v in made.items() if k not in new})
        done.append("new_items")
    wide = resized_chunks({**chunks, **new}, SHEET_SIZE)
    if wide:  # (the monsters' sheets 48h, as the copy of the game reads them: sheet_record_load)
        new.update(wide)
        done.append("wide_sheets")
    return (icons.with_chunks(data, new) if new else data), done


# The game folder's files that hold sheets (the roster's CHAR records, a save's SAVE 6 table and any
# RDFF or CHAR records), made the Loader's 48h (widen_files, at each start of the sequel from the
# Loader) or the game's 42h again (python -m dsloader.ravager narrow FOLDER: the game started by
# itself reads them then, the weapon specs and the six bytes dropped). By length, so a file already so
# is left as it is, and a roster with both (the party transfer's 48h, CHARTRAN's 42h) is made one.
SHEET_RECORDS = ("CHAR", "RDFF")  # (record lists: a sheet is kind 3, SHEET_KIND)
SHEET_KIND = 3
SHEETS_CHUNK, SHEETS_COUNT = ("SAVE", 6), 17  # (a save game's sheet table, whole: sheet_save_size)
SHEET_FILES = ("CHARSAVE.GFF", "DARKRUN.GFF", "DARKSAVE.GFF")  # (and every SAVEnn.SAV)
SAVE_PREFIXES = ("SAVE", "SAVQ")  # (the saves: the game's page, the quick saves' page: quicksave.py)
BACKUP = {SHEET_SIZE: ".42H", GAME_SHEET_SIZE: ".48H"}  # (the file before it was made that size)


def _other(size: int) -> int:
    return GAME_SHEET_SIZE if size == SHEET_SIZE else SHEET_SIZE


def _resized(sheet: bytes, size: int) -> bytes:
    return bytes(sheet[:size]).ljust(size, b"\0")


def resized_sheets(chunk: bytes, size: int) -> Optional[bytes]:
    """A record list CHUNK (dataitems) with every sheet record of the other size (42h or 48h) made
    SIZE (zeros added, or the bytes past 42h dropped); None if there was none to change."""
    from . import dataitems
    other = _other(size)
    try:
        recs, end = dataitems.records(chunk)
    except (ValueError, struct.error):
        return None
    if not any(r.kind == SHEET_KIND and len(r.data) == other for r in recs):
        return None
    return dataitems.chunk([r._replace(data=_resized(r.data, size)) if r.kind == SHEET_KIND and len(r.data) == other
                            else r for r in recs], end)


def resized_chunks(chunks: gff.Chunks, size: int) -> gff.Chunks:
    """The chunks of CHUNKS that hold sheets of the other size, made SIZE (resized_sheets; the save's
    table SHEETS_CHUNK, 17 sheets one after another)."""
    other = _other(size)
    out: gff.Chunks = {}
    for key, chunk in chunks.items():
        if key == SHEETS_CHUNK and len(chunk) == SHEETS_COUNT * other:
            out[key] = b"".join(_resized(chunk[i * other:(i + 1) * other], size) for i in range(SHEETS_COUNT))
        elif key[0] in SHEET_RECORDS:
            new = resized_sheets(chunk, size)
            if new is not None:
                out[key] = new
    return out


def sheet_files(game_dir: str) -> List[str]:
    """The files of GAME_DIR that may hold sheets (SHEET_FILES, the saves SAVEnn.SAV and the quick saves
    SAVQnn.SAV)."""
    try:
        names = sorted(os.listdir(game_dir))
    except OSError:
        return []
    wanted = {n.upper() for n in SHEET_FILES}
    return [os.path.join(game_dir, n) for n in names
            if n.upper() in wanted or (n.upper()[:4] in SAVE_PREFIXES and n.upper().endswith(".SAV"))]


def widen_files(game_dir: str, size: int = SHEET_SIZE) -> List[str]:
    """GAME_DIR's files with sheets of the other size made SIZE (the Loader's 48h; GAME_SHEET_SIZE: the
    game's), each copied first as it was (its name + BACKUP's suffix, an older copy replaced). The
    names of the files changed."""
    import shutil
    from . import icons
    done = []
    for path in sheet_files(game_dir):
        with open(path, "rb") as f:
            data = f.read()
        try:
            new = resized_chunks(gff.read_gff(data), size)
        except (gff.GffError, struct.error, ValueError):
            continue  # (not a GFF file the game wrote: left alone)
        if not new:
            continue
        shutil.copyfile(path, path + BACKUP[size])
        gff.write_atomic(path, icons.with_chunks(data, new))
        done.append(os.path.basename(path))
    return done


def read_added(dos_dir: str) -> gff.Chunks:
    """The party transfer's objects kept in DOS_DIR (ravitems.ADDED_FILE), {} if none."""
    from . import ravitems
    try:
        with open(os.path.join(dos_dir, ravitems.ADDED_FILE), "rb") as f:
            return gff.read_gff(f.read())
    except (OSError, gff.GffError, struct.error):
        return {}


def write_objects(game_dir: str, dest: str, skip=frozenset(), sl_dir: Optional[str] = None) -> List[str]:
    """OBJEX.GFF's copy with the mod's item types, the party transfer's objects (beside DEST) and, with
    SL_DIR (Shattered Lands' folder: their pictures are its), the mod's new items (ravgear), written to
    DEST unless already so."""
    from . import ravgear
    added = read_added(os.path.dirname(dest))
    gear = (lambda chunks: ravgear.from_files(chunks, sl_dir, game_dir)) if sl_dir else None
    return _write_copy(game_dir, OBJECTS_FILE, dest, lambda d, s: objects_fixed(d, s, added, gear), skip)


def write_scripts(game_dir: str, dest: str, skip=frozenset()) -> List[str]:
    """GPLDATA.GFF's copy with the script fixes, written to DEST unless already so; the fixes applied."""
    return _write_copy(game_dir, SCRIPT_FILE, dest, script_fixed, skip)


def skipped(settings: dict) -> frozenset:
    """The patches and spell fixes the switches leave out: the spells as the manual describes them
    (as for Shattered Lands, gamepatch.SPELLS_MANUAL), spells kept on the Effects screen
    (gamepatch.EFFECTS_KEPT) and the new items (Shattered Lands' switch, "new_items": ravgear's)."""
    on = settings.get("spells_manual", True) is not False
    kept = settings.get("effects_kept", True) is not False  # (spells kept on the Effects screen)
    items = settings.get("new_items", True) is not False
    return (frozenset() if on else frozenset(gamepatch.SPELLS_MANUAL)) \
        | (frozenset() if kept else frozenset(gamepatch.EFFECTS_KEPT)) | (frozenset() if items else {"new_items"})


def prepare(game_dir: str, dos_dir: str, settings: dict, sl_dir: Optional[str] = None) -> Optional[str]:
    """Write DSUNLOG2.EXE and the RESOURCE.GFF, GPLDATA.GFF and OBJEX.GFF copies into DOS_DIR (the mod's new
    items in OBJEX.GFF's with Shattered Lands' folder SL_DIR, their pictures'). Returns why the game can't be
    patched, or None."""
    skip = skipped(settings)
    try:
        write_patched(game_dir, os.path.join(dos_dir, PATCHED_EXE), skip)
        write_resources(game_dir, os.path.join(dos_dir, RESOURCE_COPY), skip)
        write_scripts(game_dir, os.path.join(dos_dir, SCRIPT_COPY), skip)
        write_objects(game_dir, os.path.join(dos_dir, OBJECTS_COPY), skip, sl_dir)
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


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3 or sys.argv[1] not in ("widen", "narrow"):
        sys.exit("usage: python -m dsloader.ravager widen|narrow RAVAGER_FOLDER\n"
                 "  narrow: the roster and the saves the game's 42-byte sheets again, for the sequel started\n"
                 "  by itself (the weapon specs dropped); widen: the Loader's 48 (it does so at each start)")
    changed = widen_files(sys.argv[2], SHEET_SIZE if sys.argv[1] == "widen" else GAME_SHEET_SIZE)
    print("\n".join(changed) if changed else "nothing to change")
