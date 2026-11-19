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
  * prepare: writes DSUNLOG2.EXE and RESOURCE.GFF's copy into the mod's dos folder.
  * conf_lines: the DOSBox autoexec that starts it: the game folder as C: (the copy reads its data
    from the current folder, the "path" patch), its CD as D: (GOG's game.ins, as GOG's own config
    mounts it) as F:, the mod's dos folder as D: as for Shattered Lands, EMS off and UMBPLUS.COM first
    (the sequel runs on XMS without EMS: measured).

The helper (DSCLOG) isn't loaded for the sequel yet: until it is, the copies of the data files are
read in place of the game's by mounting nothing over them, so RESOURCE.GFF's copy is the one thing
that needs the helper's file redirection; it is written now, and read once the helper is in."""

import os
import struct
from typing import Dict, List, Optional, Tuple

from . import gamepatch, gff
from .gamepatch import Patch

WOTR_SIZE = 634416  # DSUN.EXE of the GOG release (1.1)
PATCHED_EXE = "DSUNLOG2.EXE"
RESOURCE_FILE = "RESOURCE.GFF"
RESOURCE_COPY = "RESOURC2.GFF"  # (the copy's name in the mod's dos folder: SL's own copy is RESOURCE.GFF there)
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
HELPER_EXE = "DSCLOG2.EXE"

PATCHES: Tuple[Patch, ...] = (
    # rand(): INT VEC_RAND at its start, DSCLOG2's INT_RAND being it (the same function as SL's at
    # 5C22h, its seed at DS:384Ah): the dice log's every roll.
    Patch("rand", 0x5A22, bytes.fromhex("8b0e4c388b"), gamepatch._interrupt(VEC_RAND, 5)),
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
    source = _find_file(game_dir, RESOURCE_FILE)
    if not source:
        raise RavagerError(f"no {RESOURCE_FILE} in {game_dir}")
    with open(source, "rb") as f:
        data, done = spell_fixed(f.read(), skip)
    try:
        with open(dest, "rb") as f:
            if f.read() == data:
                return done
    except OSError:
        pass
    gff.write_atomic(dest, data)
    return done


def skipped(settings: dict) -> frozenset:
    """The patches and spell fixes the switches leave out: the spells as the manual describes them
    (as for Shattered Lands, gamepatch.SPELLS_MANUAL)."""
    on = settings.get("spells_manual", True) is not False
    return frozenset() if on else frozenset(gamepatch.SPELLS_MANUAL)


def prepare(game_dir: str, dos_dir: str, settings: dict) -> Optional[str]:
    """Write DSUNLOG2.EXE and the RESOURCE.GFF copy into DOS_DIR. Returns why the game can't be
    patched, or None."""
    skip = skipped(settings)
    try:
        write_patched(game_dir, os.path.join(dos_dir, PATCHED_EXE), skip)
        write_resources(game_dir, os.path.join(dos_dir, RESOURCE_COPY), skip)
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
