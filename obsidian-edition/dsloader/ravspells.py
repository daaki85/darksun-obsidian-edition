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
past 319 until DSCLOG2 answers for these (the known test, the wizard-spell compares, the effects: the
port plan's row, not yet done), so the records are inert till then.

**The records** are Shattered Lands' (DSCLOG's NS_SETUP): each a template spell's record, the sequel's own
of the same spell (Strength 23, Enlarge 5, Charm Person 2, Mirror Image 19: the same numbers in both games),
with NS_PATCHES' changes, its sound as it lands from the spell SL names (Haste's, Shocking Grasp's, Fog
Cloud's) and Fogbolt's sound as it is cast Fog Cloud's, then the name (32 bytes) and the short name (9).
The effect byte (+19h) is the template's, but Spook's: the sequel's Afraid (35). Erdlu Claw's and Fogbolt's
own effects (SL's unused 6 and 27) and Cat's Grace's and Friends' (54 and 74, put by Strength's handler)
have no number yet: the sequel's effects table has one empty record (88), so they wait for the helper's
effects. Fogbolt flies as Magic Missile does (its +10h; SL's grey bolt is a later picture).

**The icons**: Shattered Lands' (icons.py's, made from the player's SL RESOURCE.GFF) brought into the
sequel's palette, each colour the nearest of those its own spell icons use, in its PLNR form; without
Shattered Lands' files, the template's own icon in the sequel (Strength's for Cat's Grace...)."""

import os
import struct
from typing import Dict, List, Optional, Sequence, Tuple

from . import art, game, gff, spelltexts

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
