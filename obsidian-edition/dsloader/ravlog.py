"""The dice log for Wake of the Ravager (the port's step 3).

The sequel's helper (DSCLOG2, dos/dsclog2.asm) records the rolls in DSCLOG's ring layout, and every roll
site the sequel's fights use has the same code after its rand() call as Shattered Lands' (the dice log
names a roll by that code: playtest/ravring.py's corpus, 2026-11-19). So the dice log is Shattered
Lands' (dicelog.DiceLog), run with:

  * the sequel's layout (LAYOUT): game.py's addresses and record offsets, and the copies other modules
    imported, rebound to the sequel's values while it is attached (apply_layout; restore_layout puts
    Shattered Lands' back). Record offsets come from ravager.creature_field, sheet_field and
    item_field (each checked in a running game); a Shattered Lands field the sequel hasn't (SHEET_AGE,
    the weapon specs) is left out of the profile, so whatever reads it isn't ported yet.
  * a read-only view of the game's memory (ReadOnlyGuest): Shattered Lands' features write to DSCLOG's
    header past +146 (in DSCLOG2 that is code) and to the game's records by its layouts, so every write
    is dropped (and counted) until a feature is ported with writes of its own.
  * RavDiceLog: the sequel's helper's signature, and none of Shattered Lands' side features after the
    rolls (its people, items and screens), only the rolls' lines and the fight's tally.
"""

import struct
import sys
from typing import Dict, List, Optional, Tuple

from . import dicelog, game, ravager

HDR_SIG = b"DSCLOGR1"

# game.py's names -> the sequel's values (the rest of game.py's addresses are Shattered Lands' until
# found: what reads them isn't ported yet)
ADDRESSES: Dict[str, int] = {
    "DGROUP": ravager.DGROUP,
    "CREATURES_PTR": ravager.CREATURES_PTR, "SHEETS_PTR": ravager.SHEETS_PTR, "ITEMS_PTR": ravager.ITEMS_PTR,
    "ITEM_TYPES_PTR": 0x19CD,  # (ravds --fuzzy: 40 uses agree)
    "CREATURE_SIZE": ravager.CREATURE_SIZE, "SHEET_SIZE": ravager.SHEET_SIZE, "ITEM_SIZE": ravager.ITEM_SIZE,
    "WHOSE_TURN": ravager.WHOSE_TURN, "REGION": 0x140C, "EFFECT_COUNT": 0x2100,
    # the fight's combatants, 3 bytes each (kind, the creature's number): the sequel's code reads them
    # as selector 388h at C34h (SL's 360h at C37h), selector 388h being the load segment + 3F49h
    "COMBATANTS_SEG": 0x3F49, "COMBATANTS_OFF": 0xC33,
    # each creature's initiative (score, tie-break: words), selector 308h at DCh in the sequel's code
    # (its 5B7F6h: SL's 37BDh:D9h), selector 308h being the load segment + 3C4Fh
    "INITIATIVE_SEG": 0x3C4F, "INITIATIVE_OFF": 0xDC,
    # the rules' small tables in the data segment, each found once by its bytes, each SL's + 70h
    "DEX_AC": 0x0866, "DEX_INITIATIVE": 0x084C, "DEX_MISSILE": 0x084C, "SAVE_CON": 0x0880,
    "SAVE_WIS": 0x089A, "STR_DAMAGE_TABLE": 0x0818, "STR_TO_HIT": 0x0832,
}
OFFSET_KINDS = (("CREATURE_", ravager.creature_field), ("SHEET_", ravager.sheet_field),
                ("ITEM_", ravager.item_field))
NOT_OFFSETS = {"CREATURE_SIZE", "SHEET_SIZE", "ITEM_SIZE", "ITEM_TYPE_SIZE", "ITEM_NAME_SIZE",
               "SHEET_FLAG_GLADIATOR", "SHEET_FLAG_RANGER", "ITEM_TYPES_PTR", "ITEM_NAMES_PTR"}


def layout() -> Dict[str, int]:
    """game.py's name -> the sequel's value, for every name the profile changes."""
    out = dict(ADDRESSES)
    for name, value in vars(game).items():
        if name in NOT_OFFSETS or name in out or not isinstance(value, int) or isinstance(value, bool):
            continue
        for prefix, field in OFFSET_KINDS:
            if name.startswith(prefix):
                mapped = field(value)
                if mapped is not None:
                    out[name] = mapped
    return out


_SAVED: List[Tuple[object, str, object]] = []  # (module, name, Shattered Lands' value) as apply_layout found them


def apply_layout() -> int:
    """game.py's values, and the copies dsloader's modules imported (by the same name, the same value),
    rebound to the sequel's; dicelog's header signature too. Returns how many names were rebound."""
    if _SAVED:
        return 0
    profile = dict(layout(), HDR_SIG=HDR_SIG)
    originals = {name: getattr(game, name) for name in profile if hasattr(game, name)}
    originals["HDR_SIG"] = dicelog.HDR_SIG
    for module in [m for name, m in sys.modules.items() if name.startswith("dsloader.") and m is not None]:
        for name, value in profile.items():
            if name in vars(module) and vars(module)[name] == originals.get(name):
                _SAVED.append((module, name, vars(module)[name]))
                setattr(module, name, value)
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

    def _types(self) -> Optional[int]:
        if self.ds is None:
            return None
        off, seg = struct.unpack("<HH", self.guest.read(self.ds * 16 + ADDRESSES["ITEM_TYPES_PTR"], 4))
        return seg * 16 + off

    def read(self, addr: int, size: int) -> bytes:
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
        self.dropped += 1

    def __getattr__(self, name):  # (snapshot, the base address... the guest's own, but writes)
        if name in ("item_gate",):
            raise AttributeError(name)
        return getattr(self.guest, name)


# The sequel's spells: RESOURCE.GFF's DATA 0-319, 73 bytes each, the first 32 Shattered Lands' record,
# then its name (32 bytes) and a short name. Shattered Lands' code reads the table at
# (load + SPELLS_SEG) x 16 + SPELLS_OFF + 32 x spell (SPELLS_OFF 16 bytes into the first record), so the
# view serves the records back to back from SPELLS_AT (the BIOS's ROM, which nothing here reads) and
# SPELLS_SEG is pointed there once the load segment is known (RavDiceLog.attach).
SPELLS_AT = 0xF0000
SPELL_COUNT, SPELL_RECORD = ravager.SPELL_COUNT, ravager.SPELL_SIZE


def spell_table(resources: bytes) -> Tuple[bytes, List[str]]:
    """The sequel's RESOURCE.GFF's spell records as Shattered Lands' table (32 bytes a spell), and the
    spells' names (title case, as game.title makes Shattered Lands')."""
    from . import gff
    chunks = gff.read_gff(resources)
    table, names = bytearray(), []
    for spell in range(SPELL_COUNT):
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


class RavGameData(game.GameData):
    """game.GameData for the sequel: its item names from its own list (NAMES_START)."""

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
        if 0 <= spell < len(self.spell_names) and self.spell_names[spell]:
            return self.spell_names[spell]
        return super().spell_name(spell)

    def item_name(self, name_index: int) -> str:
        names = self._name_list()
        if 1 <= name_index <= len(names) and names[name_index - 1]:
            return names[name_index - 1]
        return f"item {name_index}"


class RavDiceLog(dicelog.DiceLog):
    """dicelog.DiceLog for Wake of the Ravager: on its layout (apply_layout), its memory read only,
    and only the rolls (no side features after them yet)."""

    def __init__(self, guest, *args, **kwargs):
        apply_layout()
        super().__init__(ReadOnlyGuest(guest), *args, **kwargs)

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
        real, dicelog.GameData = dicelog.GameData, RavGameData  # (the base attach makes its GameData)
        try:
            return super().attach()
        finally:
            dicelog.GameData = real

    def count_charges(self, entries) -> None:  # (the charges' counting writes to the game: not yet)
        return None

    def _after_rolls(self, show_all: bool, now: float) -> List[str]:
        return []


def running(guest) -> Optional[bool]:
    """Which helper the game in GUEST has loaded: True the sequel's (DSCLOG2's signature), False
    Shattered Lands' (DSCLOG's), None neither yet."""
    try:
        low = guest.read(0, game.CONVENTIONAL_AND_UPPER)
    except Exception:
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
