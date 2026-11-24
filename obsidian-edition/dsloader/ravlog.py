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
    is dropped (and counted) until a feature is ported with writes of its own: so far only the spell
    slots' lines for the USE screen (DSCLOG2's SLOTS_TEXT, by its header's +148: `writable`).
  * RavDiceLog: the sequel's helper's signature, and none of Shattered Lands' side features after the
    rolls (its people, items and screens), only the rolls' lines and the fight's tally.
"""

import struct
import sys
from typing import Dict, List, Optional, Tuple

from . import aging, combatlog, dicelog, game, labels, monsters, ravager, sizes, stealth

HDR_SIG = b"DSCLOGR1"

# game.py's names -> the sequel's values (the rest of game.py's addresses are Shattered Lands' until
# found: what reads them isn't ported yet)
# The sequel's effects are numbered otherwise (its list alphabetical: effect_names): Shattered Lands'
# numbers the log's rules use, by name in the sequel's list. Where the sequel's list has a name twice
# (Hasted 42 and 51, Slowed 52 and 91) the one in alphabetical place is taken (unverified). The mod's
# own effects (Cat's Grace, Erdlu Claw, Fogbolt, Friends, the stinkpot's Nauseated) and SL's save
# penalty aren't in the sequel: numbers it never uses (NO_EFFECT and on), so they never match.
NO_EFFECT = 240
EFFECTS: Dict[str, object] = {
    "PARALYZED_EFFECT": 69, "MIRROR_EFFECT": 46, "AFRAID_EFFECT": 35, "ENLARGE_EFFECT": 32,
    "HASTED_EFFECT": 42, "SLOWED_EFFECT": 91, "FIRE_SHIELD_EFFECT": 38, "BLUR_EFFECT": 13,
    "BIOFEEDBACK_EFFECT": 8, "LOW_RESISTANCE_EFFECT": 61, "MIND_BAR_EFFECT": 64, "AFFINITY_EFFECT": 3, "BODY_WEAPONRY_EFFECT": 14,
    "EFFECT_BLESSED": 9, "EFFECT_BLIND": 10, "EFFECT_DETECT_INVIS": 25, "EFFECT_INVISIBLE": 53,
    "EFFECT_INVIS_UNDEAD": 54, "EFFECT_PROT_EVIL": 75, "EFFECT_PROT_COLD": 73, "EFFECT_PROT_FIRE": 77,
    "EFFECT_PROT_LIGHTNING": 78, "EFFECT_FIRE_SHIELD": 38, "EFFECT_SPIRIT_ARMOR": 94, "EFFECT_BARKSKIN": 6,
    "EFFECT_PRAYER": 72, "EFFECT_FLESH_ARMOR": 40, "EFFECT_VESTMENTS": 104, "EFFECT_BRAVE": 18,
    "EFFECT_SAVE_PENALTY": NO_EFFECT, "GRACE_EFFECT": NO_EFFECT + 1, "CLAW_EFFECT": NO_EFFECT + 2,
    "FOG_EFFECT": NO_EFFECT + 3, "FRIENDS_EFFECT": NO_EFFECT + 4, "STINK_EFFECT": NO_EFFECT + 5,
    "INITIATIVE_EFFECTS": {10: -2, 42: 2, 91: -2},  # Blind, Hasted, Slowed
    "HALVING_EFFECTS": ((77, 0x02), (73, 0x04), (78, 0x80), (38, 0x06)),  # Prot Fire, Cold, Lightning; Fire Shield
    "HIT_EFFECTS": ((9, 1), (22, -1), (91, -4), (106, 1)),  # Blessed, Cursed, Slowed, Weapon Grafted
    # the effects that rule thief skills out or make one certain (game.THIEF_BLOCKED, THIEF_CERTAIN): SL's
    # by name in the sequel's numbers (SL's 25, Mirror Images, is the sequel's Detect Invisible, which had a
    # thief in Tyr hiding at 0): Berserk 7 and 102, Blind 10, Confused 21, Afraid 35, Feebleminded 37,
    # Fire Shielded 38, Mirror Images 46, Paralyzed 69, Slowed 52 and 91, Weapon Grafted 106; Detect Traps
    # 26, Invisible 53
    "THIEF_BLOCKED": {7: tuple(range(8)), 102: tuple(range(8)), 10: (0, 1, 2, 3, 4, 6, 7), 21: tuple(range(8)),
                      35: tuple(range(8)), 69: tuple(range(8)), 52: (0,), 91: (0,), 38: (0, 4), 46: (4,),
                      106: (0, 1, 6), 37: (7,)},
    "THIEF_CERTAIN": {26: (2,), 53: (4,)},
    "POWER_EFFECT_NAMES": {69: "Paralysing attack", 27: "Disease attack", 71: "Poison attack"},
}
# Its effects' names: 31-byte records in the program's data at load + 3C870h (its file's 41A70h), the
# name in the first 29 bytes, EFFECT_COUNT_ALL of them (some numbers unused: an empty name)
EFFECT_RECORDS, EFFECT_RECORD, EFFECT_COUNT_ALL = 0x3C870, 31, 113


def effect_names(guest, load: int) -> Dict[int, str]:
    """The sequel's effect names by number, as its program holds them ({} if they don't read as names)."""
    data = guest.read(load * 16 + EFFECT_RECORDS, EFFECT_RECORD * EFFECT_COUNT_ALL)
    out = {}
    for n in range(EFFECT_COUNT_ALL):
        raw = data[n * EFFECT_RECORD:n * EFFECT_RECORD + 29].split(b"\0", 1)[0]
        if not all(32 <= c < 127 for c in raw):
            return {}
        if raw:
            out[n] = raw.decode("ascii")
    return out if out.get(5) == "Armor" else {}


RAV_ITEM_TYPE, RAV_ITEM_SLOT, RAV_ITEM_PLUS = 0x0A, 0x13, 0x16  # (the sequel's item fields, as DSCLOG2's)
ADDRESSES: Dict[str, object] = {
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
    # a fight on: the game's flag, a byte at DS:13FAh in the sequel (16 uses of SL's word at 1168h matched by
    # their code: "cmp byte [13FAh],0"; RavGameData reads the byte), and the fight's state at 3C10h:19h
    # (the main loop's "mov ax,3C10h / mov es,ax / cmp word es:[19h],0", SL's 377Eh)
    "IN_COMBAT": 0x13FA, "FIGHT_STATE_FROM_DS": ravager.DGROUP - 0x3C10,
    # the game's clock: its scale (a byte) and a far pointer to the dword (ravds: SL's 9B70h, 9B72h + 9Ah;
    # read in play: scale 1, 406 s into a new game's first fight)
    "GAME_TIME_SCALE": 0x9C0A, "GAME_TIME_PTR": 0x9C0C,
    # the rules' small tables in the data segment, each found once by its bytes, each SL's + 70h
    "DEX_AC": 0x0866, "DEX_INITIATIVE": 0x084C, "DEX_MISSILE": 0x084C, "SAVE_CON": 0x0880,
    "SAVE_WIS": 0x089A, "STR_DAMAGE_TABLE": 0x0818, "STR_TO_HIT": 0x0832,
    # the AC function keeps the AC after armour in [BP-4] (its adjustments in [BP-6]: SL's SI)
    "AC_ARMOUR_LOCAL": -4,
    # spell slots left: a member's 22h bytes from DS:446Ah, a wizard level L at +L-1, a priest's from
    # +0Bh (each level's byte at SLOTS_LEFT + level, as SL's); the slot rules each SL's + 0Ch (ravds)
    "SLOTS_LEFT": {"Wizard": 0x4469, "Priest": 0x4474}, "SLOTS_STRIDE": 0x22,
    "SLOT_CLASS_RULES": 0x0670, "SLOT_RULES": 0x0684,
    # the thief skills' table (base, race, DEX limits, the armour penalty): its bytes at the sequel's
    # file offset 49BB0h, the load + 449Bh:0 (SL's 3FAAh)
    "THIEF_TABLE_SEG": 0x449B,
    # ... its race rows two longer (16 bytes), so what follows them each SL's + 10h
    "THIEF_DEX_LOW": 0xA0, "THIEF_DEX_HIGH": 0xA8, "THIEF_DEX_TOP": 0xB0, "THIEF_ARMOUR": 0xB8,
    "THIEF_PENALTY_LIST": 0xE0,  # (its slots list: the thief_slots patch at 49C90h)
    # the active effects, 10 bytes each (SL's record): selector 370h at 24Dh in the sequel's code (its
    # Share Strength loop, 61A87h), selector 370h being the load segment + 3E71h (SL's 3BF6h:106h)
    "EFFECTS_SEG": 0x3E71, "EFFECTS_OFF": 0x24D,
    # SL's helm types aren't the sequel's (its 5 is Scale Armor): RavGameData.counted_ac has its own
    "HELM_TYPES": (),
    # the Cloak and Boots of Elvenkind: the party transfer's (the mod's types in the sequel, ravager.mod_type)
    "ELVEN_CLOAK_TYPE": ravager.mod_type(game.ELVEN_CLOAK_TYPE),
    "ELVEN_BOOTS_TYPE": ravager.mod_type(game.ELVEN_BOOTS_TYPE),
    "CAHULAKS_TYPE": 24, "CAHULAKS_TYPES": frozenset((24,)),  # (the sequel's Cahulaks, OBJEX.GFF; no metal or obsidian ones)
    # the stinkpots (DSCLOG2's STINKPOTS): the Staff Sling's type, its Nauseated (ravager.NAUSEATED), the
    # save against Stinking Cloud (the sequel has no monster poison power as SL's 176)
    "STAFF_SLING_TYPE": 98, "STINK_EFFECT": ravager.NAUSEATED, "STINK_SAVE_POWER": 22,
    # the powers that can destroy an item (its power handler's switch, 656ECh: 103 the weapon then the
    # armour, 275 and 283 the armour, 284 the weapon; SL's 178, 186, 187), as the dice log names them
    # the hit point table (dice by class group, CON's bonus at +52h): SL's own bytes, at the load + 45BEh
    # (the most hit points' 4D0h:52h; SL's 40B1h)
    "LEVEL_HP_SEG": 0x45BE,
    # ages (aging.py): the age alone at the sheet's +41h, a byte the sequel's program never reads or
    # writes (no instruction with its offset on a sheet; 0 in every sheet of a new game and the saves,
    # 2026-11-22), and none more: +3Dh and +3Fh, the only others, hold CHARTRAN's kit and second sphere
    "SHEET_AGE": 0x41, "AGE_PLAIN": True,
    "ITEM_ATTACKS": {103: "Crystal Brittle", 275: "corroding touch", 283: "corroding touch",
                     284: "corroding touch"},
}
OFFSET_KINDS = (("CREATURE_", ravager.creature_field), ("SHEET_", ravager.sheet_field),
                ("ITEM_", ravager.item_field))
NOT_OFFSETS = {"CREATURE_SIZE", "SHEET_SIZE", "ITEM_SIZE", "ITEM_TYPE_SIZE", "ITEM_NAME_SIZE",
               "SHEET_FLAG_GLADIATOR", "SHEET_FLAG_RANGER", "ITEM_TYPES_PTR", "ITEM_NAMES_PTR"}


def layout() -> Dict[str, int]:
    """game.py's name -> the sequel's value, for every name the profile changes."""
    out = dict(ADDRESSES, **EFFECTS)
    for name, value in vars(game).items():
        if name in NOT_OFFSETS or name in out or not isinstance(value, int) or isinstance(value, bool):
            continue
        for prefix, field in OFFSET_KINDS:
            if name.startswith(prefix):
                mapped = field(value)
                if mapped is not None:
                    out[name] = mapped
    return out


# The colours the panel and the labels may take (combatlog.nearest: SL's 16-223, its 224-255 cycling for
# fire and water). The sequel cycles only 1-15: its 224-253 are the interface's (232-239 its blue-greys,
# the panel's stone and well; 240-253 greys), the same in Tyr's street and in the Roost (2026-11-21).
PALETTE_LAST = 253

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
    from . import combatlog  # (the panel's and the labels' colours: the sequel's palette, PALETTE_LAST)
    _SAVED.append((combatlog, "LAST", combatlog.LAST))
    combatlog.LAST = PALETTE_LAST
    from . import sizes  # (the creature size rule: the sequel's monsters and spell numbers)
    _SAVED.append((sizes, "TABLE", sizes.TABLE))
    _SAVED.append((sizes, "SPELLS", sizes.SPELLS))
    _SAVED.append((sizes, "PERSON_ONLY", sizes.PERSON_ONLY))
    _SAVED.append((sizes, "SHILLELAGH_TYPE", sizes.SHILLELAGH_TYPE))
    _SAVED.append((sizes, "HAMMER_TYPE", sizes.HAMMER_TYPE))
    sizes.TABLE, sizes.SPELLS, sizes.PERSON_ONLY = sizes.RAV_NAMES, sizes.RAV_SPELLS, frozenset()
    sizes.SHILLELAGH_TYPE, sizes.HAMMER_TYPE = sizes.RAV_SHILLELAGH_TYPE, sizes.RAV_HAMMER_TYPE
    from . import kalzith  # (dying and dead: the sequel's 4 and 7, SL's 4 and 5; aging.kill's dead)
    _SAVED.append((kalzith, "DEAD_STATUS", kalzith.DEAD_STATUS))
    kalzith.DEAD_STATUS = RAV_DEAD_STATUS
    from . import stealth  # (hiding in shadows: the sequel's positions, regions, footprint, dying and dead)
    for name, value in (("POSITIONS", RAV_POSITIONS), ("POSITION_SIZE", RAV_POSITION_SIZE),
                        ("OUTDOORS", RAV_OUTDOORS), ("INDOOR_TILES", {}), ("STATUS_GONE", RAV_DEAD_STATUS),
                        ("SHEET_FOOTPRINT", ravager.sheet_field(stealth.SHEET_FOOTPRINT))):
        _SAVED.append((stealth, name, getattr(stealth, name)))
        setattr(stealth, name, value)
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
RAV_DEAD_STATUS = (4, 7)  # a creature's status (+14h): dying, dead (SL's 4, 5)
# Each map object's x, y (16ths of a square), 25h bytes apart (the attack's set-up reads them for the
# attacker SI and the target DI: 5C8B7h; SL's 669Dh, 32 apart)
RAV_POSITIONS, RAV_POSITION_SIZE = 0x67C5, 0x25
# The regions under the open sky (stealth.daylight), by each RGNxx.GFF's own name (its RNME): forest
# (Humbleton Forest), Tyr (its streets; its buildings' floors aren't told apart yet), Jann (the Jann
# tribe's desert), Silt Giants (the Silt Sea islands), Cloud and Limbo. The rest are under a roof or
# underground: VA Headquarters, Pyramid, Yuan-ti Tunnels, El's Temple, Mines1-3, Mosaic, Volcano
# Levels 1-3, Crypt, Cosmos, UnderTyr.
RAV_OUTDOORS = frozenset((0x01, 0x32, 0x3B, 0x41, 0x42, 0xFF))
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
        self.writable: List[Tuple[int, int]] = []  # (address, size): the helper's buffers a ported feature writes

    def _types(self) -> Optional[int]:
        if self.ds is None:
            return None
        off, seg = struct.unpack("<HH", self.guest.read(self.ds * 16 + ADDRESSES["ITEM_TYPES_PTR"], 4))
        return seg * 16 + off

    def read(self, addr: int, size: int) -> bytes:
        if CLASS_MAGIC_AT <= addr < CLASS_MAGIC_AT + len(CLASS_MAGIC):
            return CLASS_MAGIC[addr - CLASS_MAGIC_AT:addr - CLASS_MAGIC_AT + size]
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
        if any(start <= addr and addr + len(data) <= start + size for start, size in self.writable):
            self.guest.write(addr, data)
        else:
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
# Which classes cast which magic (a byte every 4 by class number: bit 1 wizard, bit 2 priest, as SL's
# table at load + 3800h:118h has them). The sequel has no such table: its slot routine (626B7h) asks
# whether the class can cast a wizard spell (8) and a priest spell (73h) of a routine (62B45h): wizard
# spells classes 11 and 18 (SL's preserver and the sequel's new one), priest spells those whose spheres
# (its jump table: 1-8, 13-16 and 19, the sequel's new one, all spheres) meet spell 73h's (30h: every
# priest class). The view serves those bits from CLASS_MAGIC_AT (past the spells), CLASS_MAGIC_SEG
# pointed there at attach. (Not the spheres: the dice log's caster levels for Dispel Magic aren't ported.)
CLASS_MAGIC_AT = 0xF4000 + game.CLASS_MAGIC_OFF
WIZARD_CLASSES, PRIEST_CLASSES = (11, 18), (1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 19)
CLASS_MAGIC = bytes(b for c in range(32) for b in ((2 if c in PRIEST_CLASSES else 1 if c in WIZARD_CLASSES
                                                       else 0), 0, 0, 0))
# The sequel's spells by kind (its DATA names): wizard 0-114, priest 115-234, psionic powers 235 (0EBh,
# the caster level routine's bound) to 268 (10Ch), then the monsters' powers
RAV_PRIEST_FIRST, RAV_PSIONIC_FIRST, RAV_MONSTER_FIRST = 115, 0xEB, 0x10D
SPELL_STARTS, SPELL_STARTS_ROW, SPELL_LEVELS_MOST = 0x0656, 11, 10  # (DS bytes, a row of 11 for wizard spells then
# priest: each level's first spell, 1 to 10, then the end: 0, 12, 25 ... 111, 115; 115, 127 ... 233, 235)
SLOTS_ALL_19 = 0x13F8  # a DS byte the slot routine checks: 1 gives the party 19 of everything (SL's word 1164h)
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


# The sequel's damage resistance (its routine at 85052h, not SL's kinds table): a creature's resistance
# class is the byte at +0Fh of its record (0 for people; a Giant Skeleton's 2). DS:2588h holds a word a
# class (18): the damage kinds it takes none of, its weapon kinds (crushing, edged, pointed) only from
# weapons below the magic its bits B000h say (1000h: +1 or better hurts). DS:25ACh a word for each of
# the first 7 classes: kinds it takes half of. (The routine also halves or stops some kinds for a
# creature's active resistances, its record's flags, which the Look box doesn't count.)
CREATURE_RESIST = 0x0F
RESIST_IMMUNE, RESIST_IMMUNE_COUNT = 0x2588, 18
RESIST_HALF, RESIST_HALF_COUNT = 0x25AC, 7
WEAPON_BITS, MAGIC_BITS = 0x38, 0xB000


def resist_percent(immune: int, half: int, kinds: int) -> int:
    """The percent of a hit with KINDS a creature of a class with these masks takes, as 85052h works it out."""
    taken = -1
    if immune & kinds & WEAPON_BITS:
        if (immune & MAGIC_BITS) > (kinds & MAGIC_BITS):
            taken = 0
    elif immune & kinds:
        taken = 0
    if taken < 0:
        taken = 100
    if half & kinds:
        taken //= 2
    return taken


def resist_masks(gd, resist: int) -> Tuple[int, int]:
    """(immune, half) for resistance class RESIST, read from the running game's data segment."""
    immune = half = 0
    if 0 <= resist < RESIST_IMMUNE_COUNT:
        immune, = struct.unpack("<H", gd.guest.read(gd.ds * 16 + RESIST_IMMUNE + 2 * resist, 2))
    if 0 <= resist < RESIST_HALF_COUNT:
        half, = struct.unpack("<H", gd.guest.read(gd.ds * 16 + RESIST_HALF + 2 * resist, 2))
    return immune, half


def monster_lines(gd, creature: int, ac: Optional[int]) -> Tuple[List[str], List[str]]:
    """monsters.monster_lines for the sequel: (the Look box's short lines, the whole description), its
    records' fields through the layout (game's constants rebound) and its resistance classes."""
    rec, sheet = gd.creature(creature), gd.sheet(creature)
    if len(rec) < ravager.CREATURE_SIZE or len(sheet) < ravager.SHEET_SIZE:
        return [], []
    hp = struct.unpack_from("<h", rec, 0)[0]
    max_hp = struct.unpack_from("<h", sheet, 0x08)[0]
    thac0 = struct.unpack_from("b", rec, ravager.creature_field(0x1F))[0]
    mr = sheet[ravager.sheet_field(0x29)]
    attacks = sheet[ravager.sheet_field(0x2A)]
    immune, half = resist_masks(gd, rec[CREATURE_RESIST])
    d = monsters.defences([], 0, False, percent=lambda kinds: resist_percent(immune, half, kinds))
    if ac is None:
        ac = gd.counted_ac(creature)
    ac_text = str(ac) if ac is not None else str(struct.unpack_from("b", sheet, ravager.sheet_field(0x27))[0])
    alignment = monsters.ALIGNMENTS.get(sheet[ravager.sheet_field(monsters.SHEET_ALIGNMENT)])
    second = f"THAC0 {thac0}"
    if alignment and monsters.look_pixels(f"{second} AL {alignment[0]}") <= monsters.LOOK_PIXELS:
        second += f" AL {alignment[0]}"
    short = [monsters.look_fit(f"HP {hp}/{max_hp} AC {ac_text}", f"HP{hp}/{max_hp} AC{ac_text}"), second]
    if mr:
        side = f"MR {mr}" if monsters.look_pixels(f"MR {mr}") <= monsters.SIDE_PIXELS else f"MR{mr}"
        short.insert(0, monsters.LOOK_SIDE + side)
    line = monsters.short_line(d)
    spells = bool(immune & monsters.MAGIC)  # (every spell carries MAGIC: none hurts it)
    if spells and not d.weapon_plus:
        line = "IMM SPELLS PSI" if immune & monsters.PSIONIC else "IMM SPELLS"
    if line:
        short.append(line)
    said = monsters.describe(d)
    if spells:  # (the list of kinds said as what it is)
        said = [("Immune to spells" + (" and psionic attacks." if immune & monsters.PSIONIC else "."))
                if t.startswith("Immune to ") else t for t in said]
    per_round = f"{attacks // 2}" if attacks % 2 == 0 else f"{attacks}/2"
    head = f"{gd.creature_name(creature)}: HP {hp}/{max_hp}, AC {ac_text}, THAC0 {thac0}"
    if attacks:
        head += f", {per_round} attack{'s' if attacks != 2 else ''} a round"
    full = [head + (f", magic resistance {mr}%" if mr else "") + (f", {alignment[1]}" if alignment else "") + "."]
    return short, full + said


class RavGameData(game.GameData):
    """game.GameData for the sequel: its item names from its own list (NAMES_START), and only the mod's
    rule changes ported to it (ravager.RULES_PORTED: the spell slots, for one, are the game's own)."""

    _rules = 0
    psionic_first = RAV_PSIONIC_FIRST

    @property
    def rules(self) -> int:
        return self._rules

    def in_combat(self) -> bool:
        """SL's, the game's flag read as the byte it is in the sequel (DS:13FAh, IN_COMBAT)."""
        return self.guest.read(self.ds * 16 + game.IN_COMBAT, 1)[0] != 0 and self.fight_on()

    @rules.setter
    def rules(self, value: int) -> None:  # (the Loader's settings name SL's rules: the sequel's ported ones)
        self._rules = value & ravager.RULES_PORTED

    def counted_ac(self, creature: int) -> Optional[int]:
        """SL's, and with RULE_HELMS a worn Helm of the sequel's type 55 counting AC 1 (DSCLOG2's
        PROBE_HELM_AC: ravager.HELM_TYPE, HELM_NAME; its type reads AC 0, as a hat's)."""
        ac = super().counted_ac(creature)
        if ac is None or not self.rules & game.RULE_HELMS:
            return ac
        for _, item, typ in self._worn(creature, game.CREATURE_ITEM_LISTS[:1]):
            if len(item) >= ravager.ITEM_NAME + 2 and typ[0x0F] & 0x80 \
                    and struct.unpack_from("<H", item, game.ITEM_TYPE)[0] == ravager.HELM_TYPE \
                    and struct.unpack_from("<H", item, ravager.ITEM_NAME)[0] == ravager.HELM_NAME:
                ac -= 1
        return ac

    def creating(self) -> bool:
        """Never (SL's test reads its creation screen's pointers, not the sequel's): the sequel's screen
        rolls no age, so the character being made may have one given at once (aging.give_ages)."""
        return False

    def spell_level(self, spell: int) -> int:
        """The spell's level: the sequel's table at DS:0656h (SPELL_STARTS), the first spell of each
        level, a row for wizard spells then one for priest (SL's 7-byte table isn't in the sequel). 0 for a
        psionic power or a monster's."""
        if not 0 <= spell < RAV_PSIONIC_FIRST:
            return 0
        at = self.ds * 16 + SPELL_STARTS + (0 if spell < RAV_PRIEST_FIRST else SPELL_STARTS_ROW)
        return sum(1 for first in self.guest.read(at, SPELL_LEVELS_MOST) if first <= spell)

    def no_spells(self, creature: int) -> bool:
        """SL's, with class restrictions on (DSCLOG2's CAST_ARMOUR: a multiclass preserver casts nothing
        in armour)."""
        return bool(self.rules & game.RULE_RESTRICT) and super().no_spells(creature)

    def thief_heavy(self, creature: int) -> bool:
        """SL's, with class restrictions on (DSCLOG2's BELT_SITE and THIEF_REAR: no thief skills or
        backstab in armour that isn't light)."""
        return bool(self.rules & game.RULE_RESTRICT) and super().thief_heavy(creature)

    def effect_caster_level(self, creature: int, spell: int) -> Optional[int]:
        """The level a spell effect counts as cast at: the sequel's caster level routine (698h:34h,
        97DC5h; SL's 81B16h, which game.effect_caster_level models with SL's sphere tables, not in the
        sequel). Below psionic powers (RAV_PSIONIC_FIRST) the best level of the classes that cast the
        spell (wizard spells below RAV_PRIEST_FIRST: WIZARD_CLASSES; the rest PRIEST_CLASSES, spheres
        aside), a ranger's 7 less; a psionic power the psionicist's level; Enlarge's levels for the
        attack (DSCLOG2's ENL_SITE, 608h:52h) come from here. None for monsters' own powers."""
        if not 0 <= spell < RAV_MONSTER_FIRST:
            return None
        if spell >= RAV_PSIONIC_FIRST:
            return self.class_level(creature, game.PSIONICIST)
        casters = WIZARD_CLASSES if spell < RAV_PRIEST_FIRST else PRIEST_CLASSES
        return max([self.class_level(creature, c) - (7 if c in game.RANGER_CLASSES else 0) for c in casters] + [0])

    def max_spell_slots(self, member: int, bit: int, spell_level: int, wis: bool = True) -> int:
        """The game's slot routine (626B7h; SL's 5E0ACh, the same but for its test switch, a byte at
        DS:13F8h, SL's word at 1164h, and which classes cast: CLASS_MAGIC)."""
        if member < 4 and self.guest.read(self.ds * 16 + SLOTS_ALL_19, 1)[0] == 1:
            return 19
        return super().max_spell_slots(member, bit, spell_level, wis)

    def adnd_slots(self, cls: int, level: int, spell_level: int) -> Optional[int]:
        """The sequel's: AD&D's to 20th level with AD&D's class tables (tables.rav_slots, DSCLOG2's
        ADND_SLOTS), else None (the game's own rule for the level)."""
        from . import tables
        return tables.rav_slots(cls, level, spell_level) if self.rules & game.RULE_ADND_TABLES else None

    def robe_slots(self, member: int, bit: int, spell_level: int, total: int) -> int:
        """TOTAL slots with the member's worn robe's: the party transfer's robes are the mod's type in the
        sequel (ravager.mod_type), the Veiled Robe's one more as SL's (robes.slots; DSCLOG2's VEILED_SLOT)."""
        from . import robes
        robe = ravager.mod_type(game.ROBE_TYPE)
        plus = next((struct.unpack("b", rec[RAV_ITEM_PLUS:RAV_ITEM_PLUS + 1])[0] for _, rec, _ in self._worn(member)
                     if struct.unpack_from("<H", rec, RAV_ITEM_TYPE)[0] == robe and rec[RAV_ITEM_SLOT] == robes.CHEST_SLOT),
                    0)
        return robes.slots(plus, bit, spell_level, total)

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

    def items_readable(self, creature: int) -> bool:
        """Whether a creature's items read as items: each name in the sequel's list, its type in range."""
        try:
            names = self._name_list()
            return bool(names) and all(1 <= struct.unpack_from("<H", item, game.ITEM_NAME)[0] <= len(names)
                                       and len(typ) == game.ITEM_TYPE_SIZE for _, item, typ in self._worn(creature))
        except (struct.error, IndexError, ValueError):
            return False

    def item_name(self, name_index: int) -> str:
        names = self._name_list()
        if 1 <= name_index <= len(names) and names[name_index - 1]:
            return names[name_index - 1]
        return f"item {name_index}"


DSCLOG2_DAC_CHANGES = 240  # DSCLOG2's header: the palette's changes counted (its own: DSCLOG's dust count there)
PANEL_H_MOST = 130  # (DSCLOG2's PANEL_H_MOST: the picture's rows at most)


class RavDiceLog(dicelog.DiceLog):
    """dicelog.DiceLog for Wake of the Ravager: on its layout (apply_layout), its memory read only,
    and only the rolls (no side features after them yet)."""

    def __init__(self, guest, *args, **kwargs):
        apply_layout()
        super().__init__(ReadOnlyGuest(guest), *args, **kwargs)
        self._next_slots = 0.0

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
            rebind("CLASS_MAGIC_SEG", (CLASS_MAGIC_AT - game.CLASS_MAGIC_OFF) // 16 - load)
            names = effect_names(self.guest.guest, load)
            if names:
                rebind("EFFECT_NAMES", names)
        real, dicelog.GameData = dicelog.GameData, RavGameData  # (the base attach makes its GameData)
        try:
            result = super().attach()
        finally:
            dicelog.GameData = real
        self._write_item_names()
        return result

    def _write_item_names(self) -> None:
        """The mod's item names into DSCLOG2's ITEM_NAMES (its header's +196, +198), if it has them."""
        if self.tsr_hdr is None:
            return
        base = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_HDR_OFF, 2))[0]
        off, count = struct.unpack("<HH", self.guest.read(self.tsr_hdr + ravager.TSR_NAMES_OFF, 4))
        from . import launch, ravitems
        kept = ravager.read_added(launch.DOS_DIR).get(ravitems.NAMES_CHUNK, b"")
        names = ravager.item_names([n for n in kept.split(b"\n") if n])
        if not off or count * ravager.NAME_KEPT < len(names):  # (a helper before the names)
            return
        self.guest.guest.write(base + off, names)

    def set_rules(self, rules: int) -> None:
        """SL's, the rules ported to the sequel alone (ravager.RULES_PORTED), into DSCLOG2's header
        (+170, +270) made writable for them; the rest of SL's writes (the spell save's table, the
        stealth gear's word) dropped."""
        if self.tsr_hdr is not None:
            for r in ((self.tsr_hdr + dicelog.TSR_RULES, 2), (self.tsr_hdr + dicelog.TSR_RULES_HI, 2)):
                if r not in self.guest.writable:
                    self.guest.writable = self.guest.writable + [r]
        super().set_rules(rules & ravager.RULES_PORTED)

    def _set_stealth(self, hidden: bool, member: int = 0) -> None:
        """SL's: DSCLOG2's STEALTH (its header's +204) made writable and set, this party member's next
        attack one from behind (MISSILE_REAR); not the hiding's sound nor the figure drawn see-through
        (SL's SOUND_REQ and shadows: not in DSCLOG2 yet)."""
        if self.tsr_hdr is None:
            return
        word = (self.tsr_hdr + stealth.TSR_STEALTH, 2)
        if word not in self.guest.writable:
            self.guest.writable = self.guest.writable + [word]
        self.guest.write(word[0], struct.pack("<H", 1 << member if hidden else 0))

    def count_charges(self, entries) -> None:  # (the charges' counting writes to the game: not yet)
        return None

    def _slots_table(self) -> Optional[int]:
        """Where DSCLOG2's SLOTS_TEXT is (its header's +148), made writable; None without the helper."""
        if self.tsr_hdr is None:
            return None
        base = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_HDR_OFF, 2))[0]
        off = struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_SLOTS_OFF, 2))[0]
        if not off:  # (a helper before the spell slots: none)
            return None
        table = (base + off, game.PARTY_SIZE * dicelog.SLOTS_SIZE)
        if table not in self.guest.writable:
            self.guest.writable = [table] + self.guest.writable
        return table[0]

    def _label_slots(self) -> Optional[int]:
        """Where DSCLOG2's LBL_SLOTS are (its header's +1834:+1838, labels.slots_at), made writable;
        None without them (a helper before the labels)."""
        if self.tsr_hdr is None:
            return None
        seg, _, off = struct.unpack("<HHH", self.guest.read(self.tsr_hdr + labels.TSR_TAIL_SEG, 6))
        if not seg or not off:
            return None
        slots = (seg * 16 + off, labels.SLOTS * labels.SIZE)
        if slots not in self.guest.writable:
            self.guest.writable = self.guest.writable + [slots]
        return slots[0]

    def _large_bits(self) -> Optional[int]:
        """Where DSCLOG2's LARGE_BITS are (its header's +1834:+1842, as DSCLOG's tail), made writable;
        None without them (a helper before the creature size rule)."""
        if self.tsr_hdr is None:
            return None
        seg, = struct.unpack("<H", self.guest.read(self.tsr_hdr + sizes.TSR_TAIL_SEG, 2))
        off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + sizes.TSR_LARGE, 2))
        if not seg or not off:
            return None
        bits = (seg * 16 + off, sizes.LARGE_BYTES)
        if bits not in self.guest.writable:
            self.guest.writable = self.guest.writable + [bits]
        return bits[0]

    def _panel_ranges(self) -> bool:
        """DSCLOG2's combat log panel's picture (its far block, header +328:+140) and the header's
        words for it (+164 the Loader's stamp, +326 to +349 the panel's), made writable; False
        without them (a helper before the panel)."""
        if self.tsr_hdr is None:
            return False
        seg, = struct.unpack("<H", self.guest.read(self.tsr_hdr + combatlog.TSR_PANEL_SEG, 2))
        off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + combatlog.TSR_PANEL_OFF, 2))
        if not seg or not off:
            return False
        want = [(seg * 16 + off, combatlog.PANEL_W * PANEL_H_MOST),
                (self.tsr_hdr + dicelog.TSR_STATS_STAMP, 2),
                (self.tsr_hdr + combatlog.TSR_PANEL_ON, combatlog.TSR_KEYS + 2 - combatlog.TSR_PANEL_ON)]
        for r in want:
            if r not in self.guest.writable:
                self.guest.writable = self.guest.writable + [r]
        return True

    def _panel_pass(self, now: float) -> None:
        """The Loader's stamp (DSCLOG2 takes the panel off when it is old), the palette's changes
        (DSCLOG2's count, for the panel's colours: SL's shadows' count) and the panel drawn
        (dicelog.DiceLog._update_panel, as Shattered Lands' four times a second)."""
        if not self._panel_ranges():
            return
        self.guest.write(self.tsr_hdr + dicelog.TSR_STATS_STAMP, self.guest.read(dicelog.BIOS_TIMER, 2))
        self._shadows.palettes, = struct.unpack("<H", self.guest.read(self.tsr_hdr + DSCLOG2_DAC_CHANGES, 2))
        self._update_panel(now)

    def _look_ranges(self) -> Optional[int]:
        """DSCLOG2's Look box words (header +150 to +161) and its LOOK_TEXT, made writable; LOOK_TEXT's
        address, None without them (a helper before the Look box)."""
        if self.tsr_hdr is None:
            return None
        off, = struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_LOOK_OFF, 2))
        if not off:
            return None
        base = self.tsr_hdr - struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_HDR_OFF, 2))[0]
        for r in ((self.tsr_hdr + dicelog.TSR_LOOK_SEQ, dicelog.TSR_LOOK_ON + 2 - dicelog.TSR_LOOK_SEQ),
                  (base + off, dicelog.LOOK_SIZE)):
            if r not in self.guest.writable:
                self.guest.writable = self.guest.writable + [r]
        return base + off

    def set_monster_info(self, on: bool) -> None:
        """Shattered Lands' switch, into DSCLOG2's header once it has the Look box."""
        self.monster_info = on
        if self._look_ranges() is not None:
            self.guest.write(self.tsr_hdr + dicelog.TSR_LOOK_ON, struct.pack("<H", int(on)))

    def _answer_look(self) -> List[str]:
        """Shattered Lands' (DSCLOG asks about a creature looked at in a fight), with the sequel's
        monster_lines; only the Look box's short lines (no whole description in the dialogue window)."""
        text_at = self._look_ranges()
        if text_at is None:
            return []
        seq, = struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_LOOK_SEQ, 2))
        if seq == self._look_seq:
            return []
        self._look_seq = seq
        who, = struct.unpack("<H", self.guest.read(self.tsr_hdr + dicelog.TSR_LOOK_WHO, 2))
        short: List[str] = []
        full: List[str] = []
        index = self.game.combatant_creature(who)
        if index is not None and index >= game.PARTY_SIZE:
            try:
                short, full = monster_lines(self.game, index, self.monster_ac(index))
            except (struct.error, IndexError, ValueError):
                short, full = [], []
        text = "|".join(short).encode("cp437", "replace")[:dicelog.LOOK_SIZE - 1]
        self.guest.write(text_at, text + b"\0")
        self.guest.write(self.tsr_hdr + dicelog.TSR_LOOK_REPLY, struct.pack("<H", seq))
        return [f"Look: {full[0]}"] + [f"    {line}" for line in full[1:]] if full else []

    def _float(self, thing, text, colour, now, priority=0) -> None:
        """Shattered Lands' names over figures (labels.py), into DSCLOG2's slots once it has them."""
        if self._label_slots() is not None:
            super()._float(thing, text, colour, now, priority)

    def _write_slots(self) -> None:
        """Shattered Lands' (the lines for the USE screen), into DSCLOG2's SLOTS_TEXT."""
        if self._slots_table() is not None:
            super()._write_slots()

    def _after_rolls(self, show_all: bool, now: float) -> List[str]:
        """Of Shattered Lands' pass after the rolls, only the hit points' changes (hp_changes: each
        fall matched with the weapon hits it took in, regeneration, spells' damage), the names over
        figures whose time is up (labels.Labels.tick), the spell slots' lines for the USE screen
        (_write_slots, as often as Shattered Lands' writes them), a wizard's try at a scroll's spell
        (_learn_lines) and the combat log's panel (_panel_pass): the rest reads and writes what isn't ported yet."""
        out = self._step(lambda: self.hp_changes(now))
        if self.monster_info:  # (the Look box: answered at once, the game waits for it)
            self.set_monster_info(True)
            out += self._step(self._answer_look)
        if self._label_slots() is not None:  # (names over figures: those whose time is up taken off)
            self._labels.on = self.floating_names
            self._step(lambda: self._labels.tick(self.guest, self.tsr_hdr, now))
        if self._large_bits() is not None:  # (the creature size rule: who is large, for DSCLOG2's IS_LARGE)
            self._step(lambda: self._large.update(self.game, self.tsr_hdr))
        out += self._step(self._learn_lines)  # (a wizard's try at a scroll: DSCLOG2's INT_LEARN, +272)
        if self.game is not None and self.game.rules & game.RULE_STEALTH:
            out += self._step(self.turn_lines)  # (whose turn, a thief's hiding: stealth.turn, DSCLOG2's STEALTH)
        if now >= self._next_slots:
            self._next_slots = now + dicelog.EFFECT_INTERVAL
            self._step(self._write_slots)
            out += self._step(lambda: self._panel_pass(now))
            if self.game is not None and self.game.rules & game.RULE_AGING:
                out += self._step(self._aging_pass)
        return out

    _aging_at: Optional[Tuple[bytes, Optional[int]]] = None  # (the party and the clock the last look found)
    _hastes: Optional[set] = None  # (the Hasted effects' records the last steady look found)

    def _aging_writable(self, creatures) -> None:
        """The bytes aging.py writes made writable: for each of CREATURES (numbers) its hit points,
        status and abilities, and for a party member its sheet's abilities and SHEET_AGE."""
        sheets = game.table_pointer(self.guest, self.game.ds, game.SHEETS_PTR)
        table = game.table_pointer(self.guest, self.game.ds, game.CREATURES_PTR)
        ranges = []
        for c in creatures:
            at = table + c * game.CREATURE_SIZE
            ranges += [(at, 2), (at + game.CREATURE_STATUS, 1), (at + game.CREATURE_ABILITIES, 6)]
            if c < game.PARTY_SIZE:
                index = struct.unpack_from("<H", self.game.creature(c), game.CREATURE_SHEET_INDEX)[0]
                sheet = sheets + index * game.SHEET_SIZE
                ranges += [(sheet + game.SHEET_ABILITIES, 6), (sheet + game.SHEET_AGE, 1)]
        self.guest.writable = self.guest.writable + [r for r in ranges if r not in self.guest.writable]

    def _aging_pass(self) -> List[str]:
        """Ages (RULE_AGING, aging.py), on a steady look only (the same party as the last, the clock
        on by no more than NATURAL_JUMP: not a game being loaded): a starting age for each member
        without one (give_ages), a year for each year the clock passes from the last look
        (natural_tick: the years it passes while the Loader watches; the sequel has no place for
        Shattered Lands' count of them, natural_years_due's flags), and Haste's aging (hasted: a
        system shock, a year) for each Hasted effect not there at the last look."""
        gd = self.game
        party, clock = gd.party_signature(), gd.game_time()
        last, self._aging_at = self._aging_at, (party, clock)
        hastes = {(e.owner, e.caster, spell, handle) for e, spell, handle in gd.effect_records()
                  if e.id == game.HASTED_EFFECT}
        before, self._hastes = self._hastes, hastes
        if clock is None or last is None or last[0] != party or last[1] is None \
                or not 0 <= clock - last[1] <= dicelog.NATURAL_JUMP:
            self._hastes = None  # (what a loaded game has already is not news)
            return []
        self._aging_writable(range(game.PARTY_SIZE))
        out = aging.give_ages(gd)
        if clock // aging.YEAR > last[1] // aging.YEAR:
            out += aging.natural_tick(gd, clock // aging.YEAR - last[1] // aging.YEAR)
        if before is None:
            return out
        for owner, caster, _, _ in sorted(hastes - before):
            creature = gd.combatant_creature(owner)
            if creature is not None:
                self._aging_writable([creature])
                out += [f"{self._name(caster)} gives Hasted to {self._name(owner)}"] + aging.hasted(gd, creature)
        return out


def window_layout(sl_raw: dict) -> dict:
    """The Loader window's party layout (layouts/*.json, as a dict) for the sequel, made from Shattered
    Lands': every record offset through ravager.creature_field / sheet_field, the strides the sequel's;
    a field the sequel hasn't (no mapped offset) left out."""
    import copy
    raw = copy.deepcopy(sl_raw)
    field = {"creature": ravager.creature_field, "sheet": ravager.sheet_field}
    size = {"creature": ravager.CREATURE_SIZE, "sheet": ravager.SHEET_SIZE}

    def mapped(record: str, offset) -> Optional[int]:
        return field[record](int(offset, 0) if isinstance(offset, str) else offset) if record in field else None

    raw["game"] = "Dark Sun: Wake of the Ravager"
    for name, spec in raw.get("records", {}).items():
        spec["stride"] = hex(size[name]) if name in size else spec.get("stride")
        spec["slots"] = [None] * len(spec.get("slots", []))
        link = spec.get("link")
        if link:
            pairs = [[mapped(name, a), mapped(link["to"], b), n] for a, b, n in link["match"]]
            link["match"] = [[hex(a), hex(b), n] for a, b, n in pairs if a is not None and b is not None]
    name = raw.get("name", {})
    name["offset"] = hex(mapped(name.get("record", "creature"), name.get("offset", 0)))
    fields = []
    for f in raw.get("fields", []):
        at = mapped(f.get("record", "creature"), f.get("offset", 0))
        if at is None:
            continue
        f["offset"] = hex(at)
        base = f.get("base")
        if base is not None:
            b = mapped(base["record"], base["offset"])
            if b is None:
                f.pop("base")
            else:
                base["offset"] = hex(b)
        fields.append(f)
    raw["fields"] = fields
    return raw


def running(guest) -> Optional[bool]:
    """Which helper the game in GUEST has loaded: True the sequel's (DSCLOG2's signature), False
    Shattered Lands' (DSCLOG's), None neither yet."""
    try:
        low = guest.read(0, game.CONVENTIONAL_AND_UPPER)
    except Exception:
        return None
    if not isinstance(low, (bytes, bytearray)):  # (a stand-in guest: neither)
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
