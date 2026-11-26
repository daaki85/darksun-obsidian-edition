"""The mod's six new wizard spells in Wake of the Ravager: their records, icons and descriptions in the
Loader's copy of RESOURCE.GFF (RESOURC2.GFF: ravager.resources_fixed).

**Their numbers.** The sequel has no six free wizard numbers below 120: its spells are RESOURCE.GFF's DATA
0-319 (wizard 0-114, priest 115-234, psionic 235-268, the monsters' powers 269-319, every record in use),
and a member's 15-byte known bitset (bit n, spell n) has only bits 115-119 unused, five, whose numbers are
priest records (Bless, Curse, Cure Light Wounds, Cause Light Wounds, Entangle). So the six take the numbers
past the table, 320-325 (FIRST), as in Shattered Lands they took 196-201 past its 196: records DATA 320-325,
icons ICON 21320-21325 (21000 + the spell, as the game's own), descriptions SPIN 321-326 (the spell + 1).
Who knows them is not in the bitset but in the sheet's bits that Shattered Lands' copy keeps and the
party transfer already carries (game.NEW_KNOWN at the sequel's +3Fh and +3Dh: ravlog's NEW_KNOWN), so a
transferred character's known new spells need nothing more. The game's own code never asks for a spell
past 319: DSCLOG2's NEW SPELLS answers for these (the program's side below, sites 140-147).

**The records** are Shattered Lands' (DSCLOG's NS_SETUP): each a template spell's record, the sequel's own
of the same spell (Strength 23, Enlarge 5, Charm Person 2, Mirror Image 19: the same numbers in both games),
with NS_PATCHES' changes, its sound as it lands from the spell SL names (Haste's, Shocking Grasp's, Fog
Cloud's) and Fogbolt's sound as it is cast Fog Cloud's, then the name (32 bytes) and the short name (9).
The effect byte (+19h) is the template's, but Spook's (the sequel's Afraid, 35) and Erdlu Claw's and
Fogbolt's: their own effects, 114 and 115, past the sequel's 113 records (EFFECTS; Cat's Grace's and
Friends', 113 and 116, put by Strength's handler). Fogbolt flies as Magic Missile does (its +10h; SL's grey bolt is a later picture).

**The icons**: Shattered Lands' (icons.py's, made from the player's SL RESOURCE.GFF) brought into the
sequel's palette, each colour the nearest of those its own spell icons use, in its PLNR form; without
Shattered Lands' files, the template's own icon in the sequel (Strength's for Cat's Grace...)."""

import os
import struct
from typing import Dict, List, Optional, Sequence, Tuple

from . import art, game, gff, spelltexts
from .gamepatch import Patch

FIRST = 320  # (past the sequel's 320 records: DATA 0-319)
GRACE, CLAW, FOG, REFLECT, SPOOK, FRIENDS = range(FIRST, FIRST + 6)
SPELLS = {GRACE: "Cat's Grace", CLAW: "Erdlu Claw", FOG: "Fogbolt", REFLECT: "Reflected Image",
          SPOOK: "Spook", FRIENDS: "Friends"}
SL_NUMBER = {spell: game.GRACE_SPELL + k for k, spell in enumerate(SPELLS)}  # (Shattered Lands' 196-201)
LEVELS = {spell: game.NEW_SPELL_LEVELS[SL_NUMBER[spell]] for spell in SPELLS}
NAMES = {GRACE: b"CAT'S GRACE", CLAW: b"ERDLU CLAW", FOG: b"FOGBOLT", REFLECT: b"REFLECTED IMAGE",
         SPOOK: b"SPOOK", FRIENDS: b"FRIENDS"}
SHORT_NAMES = {GRACE: b"CATGRACE", CLAW: b"ERDLUCLW", FOG: b"FOGBOLT", REFLECT: b"REFLIMAG",
               SPOOK: b"SPOOK", FRIENDS: b"FRIENDS"}
STRENGTH, ENLARGE, CHARM, MIRROR = 23, 5, 2, 19
TEMPLATES = {GRACE: STRENGTH, CLAW: ENLARGE, FOG: CHARM, REFLECT: MIRROR, SPOOK: CHARM, FRIENDS: STRENGTH}
HASTE, SHOCKING_GRASP, FOG_CLOUD, MAGIC_MISSILE = 29, 10, 15, 8
LANDING = {GRACE: HASTE, CLAW: SHOCKING_GRASP, FOG: FOG_CLOUD}  # (+16h, the sound as it lands: whose)
CAST_SOUND, FLIGHT, LANDING_SOUND, EFFECT = 0x0F, 0x10, 0x16, 0x19
AFRAID = 35  # (the sequel's Afraid: ravlog's AFRAID_EFFECT)
RECORD, NAME, SHORT = 0x20, 32, 9  # (the record's first 32 bytes, then the name and the short name)
SPELL_SIZE = RECORD + NAME + SHORT  # (73: ravager.SPELL_SIZE)
# DSCLOG's NS_PATCHES for the wizard spells: (spell, place, size, value)
PATCHES: Tuple[Tuple[int, int, int, int], ...] = (
    (FOG, 4, 1, 0x42), (FOG, 5, 2, 0), (FOG, 7, 2, 60), (FOG, 0x11, 2, 0x4000),  # 2d4 rounds, not mind-affecting
    (REFLECT, 4, 1, 0x11), (REFLECT, 5, 2, 0),  # one image
    (SPOOK, 4, 1, 0x13), (SPOOK, 5, 2, 0), (SPOOK, 7, 2, 60), (SPOOK, 0x11, 2, 0x4304),  # 3 rounds, fear's
    (FRIENDS, 4, 1, 0x41), (FRIENDS, 5, 2, 1), (FRIENDS, 7, 2, 60), (FRIENDS, 0x1D, 1, 1),  # 1d4 rounds + 1 a level
    (FRIENDS, 1, 2, 0xFFFF), (FRIENDS, 0x0C, 1, 7),  # on the caster alone
)
ICON_BASE = 21000
TEXT_BASE = 1  # (SPIN the spell + 1)
SKIP = "new_spells"  # (resources_fixed's name for them, a SKIP's to leave them out: the Options tab's switch)


def _record(chunks: gff.Chunks, spell: int) -> bytes:
    data = chunks[("DATA", spell)]
    if len(data) != SPELL_SIZE:
        raise ValueError(f"spell record {spell} is {len(data)} bytes")
    return data


def record(chunks: gff.Chunks, spell: int) -> bytes:
    """New spell SPELL's 73-byte record, from the sequel's own records (CHUNKS, its RESOURCE.GFF's)."""
    out = bytearray(_record(chunks, TEMPLATES[spell])[:RECORD])
    if spell in LANDING:
        out[LANDING_SOUND] = _record(chunks, LANDING[spell])[LANDING_SOUND]
    if spell == FOG:
        out[CAST_SOUND] = _record(chunks, FOG_CLOUD)[CAST_SOUND]
        out[FLIGHT] = _record(chunks, MAGIC_MISSILE)[FLIGHT]
    if spell == SPOOK:
        out[EFFECT] = AFRAID
    if spell in (CLAW, FOG):
        out[EFFECT] = CLAW_EFFECT if spell == CLAW else FOG_EFFECT
    for which, at, size, value in PATCHES:
        if which == spell:
            out[at:at + size] = value.to_bytes(size, "little")
    return bytes(out) + NAMES[spell].ljust(NAME, b"\0") + SHORT_NAMES[spell].ljust(SHORT, b"\0")


def texts() -> Dict[Tuple[str, int], bytes]:
    """Their descriptions, SPIN the spell + 1 (spelltexts.TEXTS', Shattered Lands' 197-202)."""
    return {("SPIN", spell + TEXT_BASE): spelltexts.TEXTS[SL_NUMBER[spell] + 1].encode("ascii") + b"\r\n"
            for spell in SPELLS}


def _sl_icons(sl_resources: str) -> Dict[int, List[List[Optional[int]]]]:
    """Shattered Lands' icons for them, rows of its palette numbers (icons.py's, from SL_RESOURCES)."""
    from . import icons
    with open(sl_resources, "rb") as f:
        sl = gff.read_gff(f.read())
    make = {GRACE: (icons.cat_icon, icons.STRENGTH_ICON), CLAW: (icons.claw_icon, icons.GAZE_ICON),
            FOG: (icons.fog_icon, icons.ARMOR_ICON), REFLECT: (icons.reflect_icon, icons.MIRROR_ICON),
            SPOOK: (icons.spook_icon, icons.SCARE_ICON), FRIENDS: (icons.friends_icon, icons.HOLD_ICON)}
    return {spell: how(icons.decode(sl[("ICON", tile)])) for spell, (how, tile) in make.items()}


def _sl_palette(sl_dir: str) -> List[Tuple[int, int, int]]:
    """Shattered Lands' palette (GPLDATA.GFF's first, as wotrart's area pictures read it)."""
    path = art._find(sl_dir, "GPLDATA.GFF")
    with open(path, "rb") as f:
        chunks = gff.read_gff(f.read())
    return next(art.palette_colours(v) for k, v in sorted(chunks.items()) if k[0] == "PAL " and len(v) >= 768)


def _icon_colours(chunks: gff.Chunks) -> List[int]:
    """The palette numbers the sequel's own spell icons use (ICON 21000-21268, PLNR): safe on its screens."""
    from . import wotrart
    used = set()
    for (kind, number), data in chunks.items():
        if kind == "ICON" and ICON_BASE <= number < ICON_BASE + FIRST:
            try:
                used.update(p for row in wotrart.decode_plnr(data) for p in row if p)
            except (ValueError, struct.error, IndexError):
                pass
    return sorted(used)


def in_sequel(rows: Sequence[Sequence[Optional[int]]], sl_palette, palette, colours: Sequence[int]) -> List[List[Optional[int]]]:
    """ROWS (Shattered Lands' palette) in the nearest of COLOURS (the sequel's palette PALETTE)."""
    cache: Dict[int, int] = {}

    def nearest(p: int) -> int:
        if p not in cache:
            rgb = sl_palette[p]
            cache[p] = min(colours, key=lambda c: sum((a - b) ** 2 for a, b in zip(palette[c], rgb)))
        return cache[p]
    return [[None if p is None else nearest(p) for p in row] for row in rows]


def icons_for(chunks: gff.Chunks, sl_dir: Optional[str]) -> Dict[Tuple[str, int], bytes]:
    """Their icons, ICON 21000 + the spell: Shattered Lands' brought into the sequel's palette (SL_DIR its
    folder), else the template's own icon."""
    out = {("ICON", ICON_BASE + spell): chunks[("ICON", ICON_BASE + TEMPLATES[spell])] for spell in SPELLS
           if ("ICON", ICON_BASE + TEMPLATES[spell]) in chunks}
    sl_resources = sl_dir and art._find(sl_dir, "RESOURCE.GFF")
    if not sl_resources:
        return out
    try:
        drawn = _sl_icons(sl_resources)
        sl_palette = _sl_palette(sl_dir)
        palette = art.palette_colours(chunks[("PAL ", 1000)])
        colours = _icon_colours(chunks)
        if not colours:
            return out
        for spell, rows in drawn.items():
            out[("ICON", ICON_BASE + spell)] = art.plnr_frames([in_sequel(rows, sl_palette, palette, colours)])
    except (OSError, TypeError, KeyError, ValueError, IndexError, StopIteration, struct.error, gff.GffError):
        pass  # (Shattered Lands' files unreadable: the templates' icons)
    return out


def chunks(resource: gff.Chunks, sl_dir: Optional[str] = None) -> Dict[Tuple[str, int], bytes]:
    """The chunks the copy of the sequel's RESOURCE.GFF (RESOURCE its own) gains: DATA 320-325, their
    icons and their descriptions."""
    out: Dict[Tuple[str, int], bytes] = {("DATA", spell): record(resource, spell) for spell in SPELLS}
    out.update(icons_for(resource, sl_dir))
    out.update(texts())
    return out


# ---- The program's side (DSCLOG2's NEW SPELLS, sites 140-149) ----
VEC_SITE = 0xF5  # (DSCLOG2's SITE: INT F5h, then the site's number)
NS_CMP, NS_KNOW, NS_LEVEL, NS_LIST = 140, 141, 142, 143
NS_CAST, NS_EFFECT, NS_ABILITY, NS_CLAW = 144, 145, 146, 147
# The spells' effects: the sequel's effect records past its 113 (0-112; zeros after them, and the creature's
# effect bits 15 bytes, 0-119), named and given their spells' icons by "ns_effects". Cat's Grace's and
# Friends' are put by Strength's case (DSCLOG2's NS_EFFECT) and raise DEX and CHA (NS_ABILITY), Erdlu
# Claw's and Fogbolt's by their records (+19h) and weighed by NS_CLAW and NS_SWING.
EFFECT_RECORDS_FILE, EFFECT_RECORD, EFFECT_NAME = 0x3C870 + 0x5200, 31, 29  # (ravager.EFFECT_RECORDS_FILE)
GRACE_EFFECT, CLAW_EFFECT, FOG_EFFECT, FRIENDS_EFFECT = 113, 114, 115, 116
EFFECTS = {GRACE_EFFECT: (b"Cat's Grace", GRACE), CLAW_EFFECT: (b"Erdlu Claw", CLAW),
           FOG_EFFECT: (b"Fogbolt", FOG), FRIENDS_EFFECT: (b"Friends", FRIENDS)}  # (the name, the spell's icon)
# The game's compares of a spell's number with the ends of its ranges (73h the first priest spell, EBh the
# first psionic power, 10Dh the first monster's power), each where the number is a spell's: DSCLOG2's NS_CMP
# makes each with a new spell as a wizard's (NS_AS), so the code a wizard spell takes takes it (its icon
# 21000 + the spell, its name from its record, the wizard classes that cast it, its effect a spell's...).
# Each is (its file offset, the start of its overlay in the file, its bytes). Not here: the loops over the
# known bits (counters, never a new spell), the psionic powers' own (an index + EBh), and those NS_KNOW and
# NS_LEVEL answer (62625h, 62AD0h, and the ones after them that a new spell no longer reaches).
CMP_SITES: Tuple[Tuple[int, int, str], ...] = (
    (0x59E84, 0x59430, "81feeb00"), (0x59EBF, 0x59430, "81fe0d01"), (0x5A0BB, 0x59430, "81feeb00"),
    (0x5A0C1, 0x59430, "83fe73"), (0x5A0D2, 0x59430, "81fe0d01"), (0x5A551, 0x59430, "81feeb00"),
    (0x5A58C, 0x59430, "81fe0d01"), (0x62AAE, 0x62100, "3deb00"), (0x62B28, 0x62100, "3d7300"),
    (0x62B32, 0x62100, "3d7300"), (0x62B37, 0x62100, "3deb00"), (0x62B58, 0x62100, "81feeb00"),
    (0x62B5E, 0x62100, "83fe73"), (0x62B75, 0x62100, "83fe73"), (0x62B7A, 0x62100, "81feeb00"),
    (0x65E00, 0x642E0, "2681bf5102eb00"), (0x754AB, 0x749B0, "813ef543eb00"), (0x754BD, 0x749B0, "813ef5430d01"),
    (0x7A7B3, 0x78340, "813e7362eb00"), (0x7A7BB, 0x78340, "813e73620d01"), (0x7A828, 0x78340, "81faeb00"),
    (0x7A82E, 0x78340, "81fa0d01"), (0x7FE14, 0x7E2F0, "2681bf5102eb00"), (0x800BD, 0x7E2F0, "2681bf5102eb00"),
    (0x8059F, 0x7E2F0, "81fa0d01"), (0x805C7, 0x7E2F0, "81faeb00"), (0x805E8, 0x7E2F0, "81fa0d01"),
    (0x8430A, 0x83400, "81feeb00"), (0x84350, 0x83400, "81feeb00"), (0x843D6, 0x83400, "83fe73"),
    (0x846B0, 0x83400, "81feeb00"), (0x84893, 0x83400, "83fe73"), (0x84898, 0x83400, "81feeb00"),
    (0x848CD, 0x83400, "83fe73"), (0x84BD1, 0x83400, "81ffeb00"), (0x84BD7, 0x83400, "81ff0d01"),
    (0x84C72, 0x83400, "81ffeb00"), (0x84C7C, 0x83400, "81ffeb00"), (0x84C96, 0x83400, "81ffeb00"),
    (0x85335, 0x83400, "2681bf5102eb00"), (0x8B088, 0x8A4A0, "2681bf5102eb00"), (0x8B098, 0x8A4A0, "2681bf51020d01"),
    (0x91E80, 0x91890, "81ffeb00"), (0x91E92, 0x91890, "81ffeb00"), (0x91E98, 0x91890, "81ff0d01"),
    (0x923C3, 0x91890, "81feeb00"), (0x923D5, 0x91890, "81feeb00"), (0x923DB, 0x91890, "81fe0d01"),
    (0x96E78, 0x95E10, "813ef543eb00"), (0x96E86, 0x95E10, "813ef5430d01"), (0x97DCF, 0x95E10, "817e08eb00"),
    (0x97E12, 0x95E10, "817e080d01"), (0x999EE, 0x99260, "817efceb00"), (0x99A8D, 0x99260, "817efc0d01"),
    (0x99BD7, 0x99260, "817efeeb00"), (0x99BE5, 0x99260, "817efe0d01"), (0x9A7B4, 0x99260, "81faeb00"),
    (0x9A7C1, 0x99260, "81fa0d01"), (0x9A9A6, 0x99260, "81feeb00"), (0x9A9B2, 0x99260, "81fe0d01"),
)
# NS_CMP's forms of the compare's operand: a register (its number, AX 0 ... DI 7), [BP+disp], [disp] (DS),
# ES:[BX+disp]; all words
FORM_REG, FORM_BP, FORM_MEM, FORM_ES_BX = 0, 1, 2, 3


def cmp_form(code: bytes) -> Tuple[int, int, int, int]:
    """(form, register, displacement, immediate) of a word compare with an immediate: CODE its bytes."""
    if code[0] == 0x3D:  # cmp ax,imm16
        return FORM_REG, 0, 0, struct.unpack_from("<H", code, 1)[0]
    es = code[0] == 0x26
    if es:
        code = code[1:]
    op, modrm = code[0], code[1]
    if op not in (0x81, 0x83) or modrm >> 3 & 7 != 7:
        raise ValueError(f"not a compare: {code.hex()}")
    mod, rm = modrm >> 6, modrm & 7
    imm_at = {3: 2, 1: 3, 0: 4, 2: 4}[mod]
    imm = struct.unpack_from("<H", code, imm_at)[0] if op == 0x81 else struct.unpack_from("<b", code, imm_at)[0] & 0xFFFF
    if mod == 3 and not es:
        return FORM_REG, rm, 0, imm
    if mod == 1 and rm == 6 and not es:
        return FORM_BP, 0, struct.unpack_from("<b", code, 2)[0] & 0xFFFF, imm
    if mod == 0 and rm == 6 and not es:
        return FORM_MEM, 0, struct.unpack_from("<H", code, 2)[0], imm
    if mod == 2 and rm == 7 and es:
        return FORM_ES_BX, 0, struct.unpack_from("<H", code, 2)[0], imm
    raise ValueError(f"a compare NS_CMP has no form for: {code.hex()}")


def site_bytes(number: int, length: int) -> bytes:
    """INT VEC_SITE, the site's number, NOPs to LENGTH (ravager._site's)."""
    return bytes((0xCD, VEC_SITE, number)) + b"\x90" * (length - 3)


def cmp_patches() -> List[Patch]:
    return [Patch(f"ns_cmp_{at:x}", at, bytes.fromhex(code), site_bytes(NS_CMP, len(code) // 2))
            for at, _, code in CMP_SITES]


def effect_patch() -> Patch:
    """"ns_effects": the effect records 113-116 (EFFECTS), each its name and its spell's icon."""
    data = b"".join(name.ljust(EFFECT_NAME, b"\0") + struct.pack("<H", ICON_BASE + spell)
                    for _, (name, spell) in sorted(EFFECTS.items()))
    return Patch("ns_effects", EFFECT_RECORDS_FILE + GRACE_EFFECT * EFFECT_RECORD, bytes(len(data)), data)


def program_patches() -> List[Patch]:
    """The program's patches for them (ravager.PATCHES'): DSCLOG2's sites 140-147 and the effect records."""
    return [
        Patch("ns_list", 0x6254F, bytes.fromhex("33f63b7efe"), site_bytes(NS_LIST, 5)),
        Patch("ns_know", 0x62625, bytes.fromhex("837e0873"), site_bytes(NS_KNOW, 4)),
        Patch("ns_level", 0x62AD0, bytes.fromhex("83fa73"), site_bytes(NS_LEVEL, 3)),
        *cmp_patches(),
        Patch("ns_cast", 0x656D0, bytes.fromhex("8b460e8946e2"), site_bytes(NS_CAST, 6)),
        Patch("ns_effect", 0x6623B, bytes.fromhex("817e0ef5007507c746ee0200eb05c746ee6200"), site_bytes(NS_EFFECT, 19)),
        Patch("ns_ability", 0x85351, bytes.fromhex("8946f4b90900"), site_bytes(NS_ABILITY, 6)),
        Patch("ns_claw", 0x86A45, bytes.fromhex("0bd27547"), site_bytes(NS_CLAW, 4)),
        effect_patch(),
    ]


def cmp_table(exe: bytes) -> List[Tuple[int, int, int, int, int, int]]:
    """NS_CMP's table from the patched program EXE: for each site the way back (its IP in its overlay, past
    the site's byte), the word there, then cmp_form's four."""
    out = []
    for at, start, code in CMP_SITES:
        back = at + 3
        out.append((back - start, struct.unpack_from("<H", exe, back)[0], *cmp_form(bytes.fromhex(code))))
    return out


def cmp_table_asm(exe: bytes) -> str:
    """dos/ns_cmp_table.inc (DSCLOG2's NS_CMP_TABLE), from the patched program EXE."""
    lines = ["; NS_CMP's table (made by dsloader.ravspells.cmp_table_asm from the patched DSUNLOG2.EXE: do not edit):",
             "; the way back's IP, the word there, the form, the register, the displacement, the immediate"]
    for ip, check, form, reg, disp, imm in cmp_table(exe):
        lines.append(f"        dw 0x{ip:04X}, 0x{check:04X}\n        db {form}, {reg}\n        dw 0x{disp:04X}, 0x{imm:04X}")
    return "\n".join(lines) + "\n"
