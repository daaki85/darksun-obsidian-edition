"""The party's way from Shattered Lands into Wake of the Ravager: the sequel's roster records made
from a Shattered Lands save, as SSI's own transfer program (the sequel's CHARTRAN.EXE) makes them.

This first part is CHARTRAN's work, in Python: on every save tried it gives the very bytes CHARTRAN
writes (playtest/logs/2026-11-22-ravager-transfer-format.md), but for one stray spell bit CHARTRAN
sets now and then (its 72nd, set for no spell the member knows). What the mod adds to it (the items
the sequel lacks, the months between the games, the starting age's roll) builds on this. Kits, the
second sphere and the new spells known come across in the sheet's +3Dh and +3Fh as CHARTRAN copies
them (the Loader's DSUNLOG2 reads the sound words below them as bytes: ravager's sound_3c, sound_3e);
the Loader's way, the weapon specs and the starting age's roll (SL's +14h..+16h) in the three bytes
its copy of the game adds to the sheet (48h bytes, ravager.SHEET_SIZE: +42h..+44h).

What it reads from the save (SAVEnn.SAV, its SAVE chunks):
- 5: the creatures (3Ah bytes; the party first), 6: their sheets (47h), 7: the items (15h), 3: the
  item lists (3 bytes: a kind, the list's first item; 9999 none);
- 19: the spells each member knows (138 bytes a member, one a spell: the wizard's 0-68 go across),
  20: the psionic powers (34 bytes a member; 8 known, in the bits CHARTRAN keeps, F8h).

What it writes, for party member M, in the sequel's CHARSAVE.GFF under number 35 - M:
- CHAR: the character, as a list of records each with a 10-byte header (dataitems.HEADER: level,
  of, kind, number, flags, length) and its data, an end record after them: the creature (level 1,
  kind 2, 31h bytes), its sheet (level 3, kind 3, 42h bytes; the Loader's way 48h, LOADER_SHEET),
  then its three item lists in turn (the creature's +8, +0Ah and +0Ch, flags 16, 17 and 4), each a first item (level 2, "of" 0) and the
  next ones (level 4, "of" the record before), each list followed by the contents of its bags,
  the last bag first and a bag in a bag next (its first "of" the bag's record, flags 4). The items keep their numbers, the lists theirs.
- CACT: the creature's +6 (its word of actions); SPST: the wizard's spells known, a bit each (72);
  PSST: the powers known (their byte >> 2); PSIN: the disciplines with a power known (1, 2, 4).
- Each item becomes the sequel's object that ITEMS.BIN (in the sequel's folder: an SL object and the
  object to give, a pair of words each) names for it, else 900, a money bag: its record is that
  object's own (the sequel's OBJEX.GFF), with the save's item's links, flags, slot and plus.
"""

import struct
from typing import Callable, Dict, List, Mapping, NamedTuple, Optional, Tuple

from . import dataitems, game, ravager
from .gff import Chunks, GffError

SL_SHEET_AGE = game.SHEET_AGE

NONE = 9999
MONEY_BAG = 900
FIRST_CHAR = 32  # (CHARTRAN's: member M goes to 35 - M)
# The sequel's roster, the characters its ADD list offers: CHAR 32-39, a place taken while its CACT
# word isn't 0 (the install's 32-35 are 0, and their characters unlisted; 36-39 its four to pick).
# CHARTRAN writes 32-35 whatever is there; the Loader takes the places of the party's own earlier
# copies (by name), then free ones (places)
ROSTER_PLACES = range(32, 40)
PARTY = 4

SL_CREATURE, SL_SHEET, SL_ITEM = 0x3A, 0x47, 0x15
CREATURE, SHEET, ITEM = 0x31, 0x42, 0x17
# The Loader's way the sheet is its copy's 48h (ravager.SHEET_SIZE; the game started by itself can't
# read it), SL's packed +14h..+16h at +42h (LOADER_SPECS)
LOADER_SHEET, LOADER_SPECS = ravager.SHEET_SIZE, 0x42
SL_SPECS = 0x14  # (game.SPEC_SLOTS in SL's layout: read by its own name, which no layout rebinds)
CREATURES, SHEETS, ITEMS, LISTS, SPELLS, POWERS = 5, 6, 7, 3, 19, 20
SL_SPELLS, SL_POWERS = 138, 34
SL_NAME, SL_SHEET_INDEX, SL_ACTIONS, SL_LISTS = 0x28, 0x04, 0x06, ((0x08, 16), (0x0A, 17), (0x0C, 4))
ITEM_NEXT, ITEM_CONTENTS, SL_ITEM_NAME = 0x04, 0x08, 0x12
BAG_FLAGS, NEXT_FLAGS = 4, 2
CREATURE_KIND, SHEET_KIND, SHEET_FLAGS = 2, 3, 15

# The creature: the sequel's byte from the save's (as CHARTRAN copies them), the name after them
CREATURE_BYTES = [(w, w) for w in range(0x0E)] + [(0x10, 0x18), (0x12, 0x1A), (0x13, 0x1B), (0x14, 0x1C),
                                                  (0x16, 0x1F), (0x1F, 0x38)]
CREATURE_SCORES, SHEET_SCORES = 0x19, 0x1B  # the six scores: the sheet's (its base ones, not the creature's +22h)
CREATURE_FIXED = {0x17: 7}
CREATURE_NAME, NAME_LENGTH = 0x21, 15
# The sheet: SL's less seven bytes (+0Eh, +0Fh, the weapon specs +14h-+17h, +3Ch)
SHEET_RUNS = ((0x00, 0x00, 0x0E), (0x0E, 0x10, 4), (0x12, 0x18, 0x24), (0x37, 0x3D, 0x0A))
# The mod's kit byte (SL +43h) and its new-spells/second-sphere byte (+45h) land, as CHARTRAN copies
# the sheet, at +3Dh and +3Fh (ravlog's layout reads them there): the high bytes of two words the
# sequel reads whole, +3Ch and +3Eh, sound numbers it plays at a member's turn in a fight (0 its
# default). The unpatched game took a kit for a sound 100h or 8100h and stopped with "Mel Fatal Error"
# (playtest/RESEARCH.md); the Loader's copy reads the low bytes alone (ravager's sound_3c, sound_3e).
MOD_SHEET_BYTES = (0x3D, 0x3F)
# An item: the save's links, flags, slot and plus over the new object's record
ITEM_RUNS = ((0x02, 0x02, 8), (0x0E, 0x0E, 1), (0x12, 0x10, 1), (0x13, 0x11, 1), (0x16, 0x14, 1))

WIZARD_SPELLS = 69  # (SL's 0-68; its priests' after them aren't kept: a priest knows its spheres')
DROPPED_SPELLS = (34, 42, 49, 64)  # (none in the sequel)
POWER_KEPT = 0xF8
DISCIPLINES = ((0, 6, 1), (6, 20, 2), (20, 34, 4))  # (the powers' places of each, its PSIN bit)

# Scrolls, the mod's way (Sequel.scrolls; CHARTRAN gives each SL scroll object one sequel object,
# whatever spell the item names, and Kalzith's a money bag). SL's wizard scrolls (type 60h) and
# priest scrolls (63h) name their spell at +2, one past SL's number for it; the sequel's (types 4Dh
# and 4Eh) at +2 and at +10h, by its own numbers: a wizard spell's place in SPST plus one
# (spell_place), a priest spell SL's word plus 97 (so all ten of ITEMS.BIN's priest pairs).
SL_TYPE, SCROLL_SPELL, SCROLL_POWER, SCROLL_USES = 0x0A, 0x02, 0x10, 0x0E  # (uses: the object's own,
# 1 on a One-use Scroll, where CHARTRAN copies SL's 0)
SL_WIZARD_SCROLL, SL_PRIEST_SCROLL = 0x60, 0x63
WIZARD_SCROLL, PRIEST_SCROLL = 0x4D, 0x4E
PRIEST_SCROLL_SHIFT = 97
SPELL_MADE = (28, 29, 30)  # (SL's Shillelagh, Flame Blade, Spiritual Hammer: left behind the Loader's way,
# their spell over; itemwatch.SPELL_MADE)
LEFT = 0  # (what a left item became, in Moved.items)

# Ages (the mod's age rule, aging.py), the Loader's way: SL keeps an age at the sheet's +17h when the
# sheet is packed (game.SHEET_AGE, game.spec_packed), the sequel at +41h (ravlog's SHEET_AGE), which
# CHARTRAN leaves 0. Between the games a gap of MONTHS (rolled once a transfer): each member a year
# older with a chance of months in 12, its scores changed at the age categories reached (aging.changes)
WOTR_SHEET_AGE, WOTR_SHEET_RACE, WOTR_SHEET_ABILITIES = 0x41, 0x12, 0x15
MONTHS = (3, 12)
SCROLL_NAMES = (3, 4, 73)  # (One-use Scroll, Spellbook, the priests' Bracelet: the sequel's other
# objects of the two types are a rod, a deck of illusions, a powerstone)


def spell_place(spell: int) -> Optional[int]:
    """The sequel's place in SPST of SL's wizard spell SPELL, or None (not carried)."""
    if spell >= WIZARD_SPELLS or spell in DROPPED_SPELLS:
        return None
    if spell < 34 or 52 <= spell < 64:
        return spell
    if spell < 42 or 50 <= spell < 52 or spell > 64:
        return spell - 1
    return spell - 2


def is_scroll(rec: bytes) -> bool:
    return struct.unpack_from("<H", rec, SL_TYPE)[0] in (SL_WIZARD_SCROLL, SL_PRIEST_SCROLL)


def scroll_spell(rec: bytes) -> Optional[Tuple[int, int]]:
    """For SL's scroll item REC, the sequel's scroll type and its number for the spell; None for a
    spell the sequel lacks (or an item that isn't a scroll)."""
    kind, = struct.unpack_from("<H", rec, SL_TYPE)
    word, = struct.unpack_from("<H", rec, SCROLL_SPELL)
    if kind == SL_PRIEST_SCROLL and word:
        return PRIEST_SCROLL, word + PRIEST_SCROLL_SHIFT
    place = spell_place(word - 1) if kind == SL_WIZARD_SCROLL and word else None
    return None if place is None else (WIZARD_SCROLL, place + 1)


# An item's spell (a weapon's on a hit, a worn item's on its wearer), the Loader's way. Shattered
# Lands keeps it at the item's +0Fh, one past its number (worldgear.ITEM_SPELL; its box's icon the
# word at +2); the sequel at +10h, a word, one past its own number, the icon's at +2 too (its weapons'
# hit casts it: DSUN 5D20Dh, SL's 58B63h). The two games number their spells apart (Focus Heat SL's
# 116, the sequel's 174), so spell_map matches them by name: SL's RESOURCE.GFF's SPIN n (spell n - 1,
# "NAME: what it does") with the sequel's spell records' names (ravlog.spell_table). CHARTRAN's
# objects keep the sequel's own spell; the Loader's own objects (ravitems: the mod's items) take
# their SL item's. The Spellarcher's arrows have their spell by their name (spellarrows.ARROWS).
SL_ITEM_SPELL, ITEM_POWER, ITEM_SPELL_SHOWN = 0x0F, 0x10, 0x02
SPELL_ALIASES = {  # (SL's name: the sequel's, where the two spell one spell apart)
    "DETECT INVISIBILITY": "DETECT INVISIBLE", "MELF'S ACID ARROW": "ACID ARROW",
    "MELF'S MINUTE METEORS": "MINUTE METEORS", "PROTECTION FROM NORMAL MISSILES": "PROTECTION FROM MISSILES",
    "STONESKIN": "STONE SKIN", "TURN PEBBLE TO BOULDER": "PEBBLE TO BOULDER", "CLOUDKILL": "CLOUD KILL",
    "FEEBLEMIND": "FEEBLE MIND", "INVISIBILITY TO UNDEAD": "INVISIBLE TO UNDEAD", "MAGICAL STONE": "MAGIC STONE",
    "MAGICAL VESTMENT": "MAGIC VESTMENT", "GLITTERDUST": "GLITTER DUST", "FLAME ARROW": "FLAMING ARROW",
    "PROTECTION FROM EVIL, 10' RADIUS": "PROTECTION FROM EVIL 10", "IRONSKIN": "IRON SKIN",
    "CURE BLINDNESS OR DEAFNESS": "CURE BLINDNESS", "CAUSE BLINDNESS OR DEAFNESS": "CAUSE BLINDNESS",
    "LIFE DRAINING": "LIFE DRAIN", "MINOR GLOBE OF INVULNERABILITY": "M GLOBE OF INVULNERABILITY",
}


def spell_map(sl_resources: Chunks, sequel_names: List[str]) -> Dict[int, int]:
    """Each SL spell (its number) the sequel has, and the sequel's number for it, by their names."""
    ours = {n.upper(): i for i, n in enumerate(sequel_names) if n}
    out: Dict[int, int] = {}
    for (kind, number), text in sl_resources.items():
        if kind != "SPIN" or number < 1:
            continue
        name = text.split(b":", 1)[0].decode("latin1").strip().upper()
        spell = ours.get(SPELL_ALIASES.get(name, name))
        if spell is not None:
            out[number - 1] = spell
    return out


def is_own(obj: int) -> bool:
    """One of the Loader's own objects (ravitems: OWN_HIGH on, below SL_HIGH)."""
    from .ravitems import OWN_HIGH, SL_HIGH
    return OWN_HIGH <= obj < SL_HIGH


def item_spell(rec: bytes, spells: Mapping[int, int]) -> int:
    """The sequel's spell, one past its number (0: none), for SL's item REC: its +0Fh, or a spell
    arrow's by its name; 0 for a spell the sequel lacks."""
    from .spellarrows import ARROWS
    spell = rec[SL_ITEM_SPELL] - 1
    if spell < 0:
        name, = struct.unpack_from("<H", rec, game.ITEM_NAME)
        spell = next((a.spell for a in ARROWS if a.name == name), -1)
    return spells[spell] + 1 if spell in spells else 0


# The Tome of Understanding (tome.py) in the sequel: a wizard scroll of the Loader's (ravitems) whose
# power names TOME_SPELL, one of the sequel's unused monster spells (Mons317: 269-319 the scroll routine
# answers CANNOT LEARN FROM THIS ITEM, 99B6Eh; below 320h-327h, which a readied item's routine treats
# apart), so that DSCLOG2's TOME (site 48) knows it when its box's icon is clicked: +1 WIS
WOTR_TOME_SPELL = 317


def is_tome(rec: bytes) -> bool:
    from . import tome
    return tome.is_tome(rec)


class Sequel(NamedTuple):
    """What the transfer reads from the sequel's folder: ITEMS.BIN's pairs and the objects' records;
    with SCROLLS (scroll_objects: each scroll type and spell, the sequel's object) scrolls go the
    mod's way, and with SPELLS (spell_map) the Loader's own objects take their SL item's spell."""
    counterparts: Dict[int, int]
    objects: Chunks
    scrolls: Optional[Dict[Tuple[int, int], int]] = None
    spells: Optional[Dict[int, int]] = None

    @property
    def loader(self) -> bool:
        """The Loader's way (with_added), not CHARTRAN's."""
        return self.scrolls is not None

    def record(self, obj: int) -> bytes:
        """The item record the sequel's object OBJ holds (its first record's data)."""
        try:
            recs, _ = dataitems.records(self.objects[("RDFF", obj)])
        except KeyError:
            raise GffError(f"the sequel's OBJEX.GFF has no object {obj}") from None
        if not recs or len(recs[0].data) != ITEM:
            raise GffError(f"the sequel's object {obj} is not an item")
        return recs[0].data


def counterparts(items_bin: bytes) -> Dict[int, int]:
    """ITEMS.BIN: SL's object and the sequel's to give in its place (the first pair for an object wins)."""
    out: Dict[int, int] = {}
    for at in range(0, len(items_bin) - 3, 4):
        old, new = struct.unpack_from("<HH", items_bin, at)
        out.setdefault(old, new)
    return out


def creature(rec: bytes, sh: bytes) -> bytes:
    """The sequel's creature for the save's creature REC with its sheet SH."""
    out = bytearray(CREATURE)
    for w, s in CREATURE_BYTES:
        out[w] = rec[s]
    out[CREATURE_SCORES:CREATURE_SCORES + 6] = sh[SHEET_SCORES:SHEET_SCORES + 6]
    for w, value in CREATURE_FIXED.items():
        out[w] = value
    name = rec[SL_NAME:SL_CREATURE].split(b"\0")[0][:NAME_LENGTH]
    out[CREATURE_NAME:CREATURE_NAME + len(name)] = name
    return bytes(out)


def sheet(rec: bytes, loader: bool = False) -> bytes:
    """The sequel's sheet for the save's sheet REC: CHARTRAN's 42h bytes, or (LOADER) the Loader's 48h
    with the weapon specs and the starting age's roll packed at LOADER_SPECS (game.packed_specs' first
    three; 0 for a sheet with neither)."""
    out = bytearray(LOADER_SHEET if loader else SHEET)
    for w, s, n in SHEET_RUNS:
        out[w:w + n] = rec[s:s + n]
    if loader:
        kinds, roll = game.specs_of(rec[SL_SPECS:SL_SPECS + game.SPEC_COUNT])
        if any(kinds) or roll is not None:
            out[LOADER_SPECS:LOADER_SPECS + 3] = game.packed_specs(kinds, 0, roll)[:3]
    return bytes(out)


def sl_object(rec: bytes) -> int:
    return -struct.unpack_from("<h", rec, 0)[0]


def item(rec: bytes, sequel: Sequel) -> Tuple[bytes, int]:
    """The sequel's item record for the save's item REC, and the object it became: ITEMS.BIN's
    counterpart, or the money bag when there is none or the counterpart has no record (ITEMS.BIN
    pairs a few SL objects with sequel objects that are only a picture, as 1572 with 2228:
    CHARTRAN gives those the money bag too)."""
    spell = None
    if sequel.loader and is_scroll(rec):
        spell = scroll_spell(rec)
        if spell is None:  # (a keepsake of the Loader's: with_added)
            from .ravitems import own_object
            new = own_object(sl_object(rec)) or MONEY_BAG
        else:
            new = sequel.scrolls.get(spell, sequel.scrolls.get((spell[0], 0), MONEY_BAG))
    else:
        new = sequel.counterparts.get(sl_object(rec), MONEY_BAG)
    if ("RDFF", new) not in sequel.objects:
        new, spell = MONEY_BAG, None
    out = bytearray(sequel.record(new))
    for w, s, n in ITEM_RUNS:
        out[w:w + n] = rec[s:s + n]
    if is_tome(rec) and is_own(new):
        struct.pack_into("<H", out, ITEM_POWER, WOTR_TOME_SPELL + 1)
        struct.pack_into("<H", out, ITEM_SPELL_SHOWN, WOTR_TOME_SPELL + 1)
    elif spell is not None:
        out[SCROLL_USES] = sequel.record(new)[SCROLL_USES]
        struct.pack_into("<H", out, SCROLL_SPELL, spell[1])
        struct.pack_into("<H", out, SCROLL_POWER, spell[1])
    elif sequel.spells is not None and is_own(new) and not is_scroll(rec):  # (a keepsake scroll: none)
        power = item_spell(rec, sequel.spells)
        struct.pack_into("<H", out, ITEM_POWER, power)
        struct.pack_into("<H", out, ITEM_SPELL_SHOWN, power)
    return bytes(out), new


def scroll_objects(sequel: Sequel) -> Dict[Tuple[int, int], int]:
    """Each sequel scroll type and spell (by its numbers), the object to give: one ITEMS.BIN gives an
    SL scroll, else its lowest; under spell 0, the type's first One-use Scroll (whose record a scroll
    of a spell with no object of its own takes, its spell set)."""
    found: Dict[Tuple[int, int], List[int]] = {}
    first: Dict[int, List[Tuple[int, int]]] = {}
    for (kind, obj) in sequel.objects:
        if kind != "RDFF":
            continue
        try:
            rec = sequel.record(obj)
        except GffError:
            continue
        t, = struct.unpack_from("<H", rec, SL_TYPE)
        if t in (WIZARD_SCROLL, PRIEST_SCROLL) and struct.unpack_from("<H", rec, 0x14)[0] in SCROLL_NAMES:
            found.setdefault((t, struct.unpack_from("<H", rec, SCROLL_POWER)[0]), []).append(obj)
            first.setdefault(t, []).append((SCROLL_NAMES.index(struct.unpack_from("<H", rec, 0x14)[0]), obj))
    paired = set(sequel.counterparts.values())
    out = {key: min(objs, key=lambda o: (o not in paired, o)) for key, objs in found.items()}
    for t, objs in first.items():
        out[(t, 0)] = min(objs)[1]
    return out


def spells_known(row: bytes) -> bytes:
    bits = bytearray(9)
    for spell in range(WIZARD_SPELLS):
        place = spell_place(spell)
        if row[spell] and place is not None:
            bits[place // 8] |= 1 << (place % 8)
    return bytes(bits)


def powers_known(row: bytes) -> Tuple[bytes, bytes]:
    """PSST and PSIN for a member's row of powers."""
    powers = bytes((b & POWER_KEPT) >> 2 for b in row)
    disciplines = 0
    for start, end, bit in DISCIPLINES:
        if any(powers[start:end]):
            disciplines |= bit
    return powers, bytes([disciplines])


class Moved(NamedTuple):
    member: int
    name: str
    items: List[Tuple[int, int]]  # (SL's object, the sequel's)
    place: int = 0  # (its roster CHAR)
    age: str = ""  # (what the months between the games did, for the report)
    named: Optional[Dict[int, int]] = None  # (each SL object's name entry, its item record's +12h)


def _chunk(save: Chunks, number: int) -> bytes:
    try:
        return save[("SAVE", number)]
    except KeyError:
        raise GffError(f"the save has no SAVE {number} chunk") from None


def roll_gap(rng) -> int:
    """The months between the games (MONTHS, rolled once a transfer)."""
    return rng.randint(*MONTHS)


def gap_years(members, months: int, rng) -> Dict[int, int]:
    """Each of MEMBERS a year older with a chance of MONTHS in 12 (a d12 at most MONTHS), else 0."""
    return {m: int(rng.randint(1, 12) <= months) for m in members}


def aged(cre: bytes, sh: bytes, name: str, years: int) -> Tuple[bytes, bytes, str]:
    """The sequel's creature CRE and sheet SH of a member named NAME, YEARS older (aging.py's rule:
    its scores changed at the age categories reached, each within 3 to 25 unless already past; a year
    that would bring it to the most its race lives isn't added), and a line for the report."""
    from . import aging
    race, stored = sh[WOTR_SHEET_RACE], sh[WOTR_SHEET_AGE]
    if race not in aging.RACES or not stored:
        return cre, sh, "no age yet" if race in aging.RACES else ""
    before = aging.RACES[race].start + stored - 1
    if not years:
        return cre, sh, f"still {before}"
    after = min(before + years, aging.RACES[race].start + 254)
    if after >= aging.most_age(name, race):
        return cre, sh, f"still {before} (a year more is the most {aging._a(race)} lives)"
    cre, sh = bytearray(cre), bytearray(sh)
    sh[WOTR_SHEET_AGE] = aging.stored(race, after)
    line = f"a year older: {after}"
    delta = aging.changes(race, before, after)
    for ability, n in sorted(delta.items()):
        for rec, off in ((sh, WOTR_SHEET_ABILITIES), (cre, CREATURE_SCORES)):
            score = rec[off + ability]
            new = score + n
            rec[off + ability] = min(new, max(score, aging.HIGHEST)) if n > 0 else max(new, min(score, aging.LOWEST))
    if delta:
        line += f", {aging.CATEGORY_NAMES[aging.category(race, after)]}: " + ", ".join(
            f"{aging.ABILITY_NAMES[a]} {n:+d}" for a, n in sorted(delta.items()))
    return bytes(cre), bytes(sh), line


def party_names(save: Chunks) -> Dict[int, bytes]:
    """The save's party members (their places 0-3) and names."""
    creatures = _chunk(save, CREATURES)
    out = {}
    for m in range(PARTY):
        rec = creatures[m * SL_CREATURE:(m + 1) * SL_CREATURE]
        if len(rec) == SL_CREATURE and rec[SL_NAME]:
            out[m] = rec[SL_NAME:SL_CREATURE].split(b"\0")[0][:NAME_LENGTH]
    return out


def roster_name(chunks: Mapping[Tuple[str, int], bytes], place: int) -> Optional[bytes]:
    """The name of the character listed at PLACE of a roster's CHUNKS (None: a free place)."""
    act = chunks.get(("CACT", place))
    if not act or not any(act) or ("CHAR", place) not in chunks:
        return None
    try:
        recs, _ = dataitems.records(chunks[("CHAR", place)])
    except (GffError, struct.error):
        return None
    return recs[0].data[CREATURE_NAME:CREATURE_NAME + NAME_LENGTH].split(b"\0")[0] if recs else None


def places(save: Chunks, roster_chunks: Mapping[Tuple[str, int], bytes]) -> Dict[int, int]:
    """For each party member, its roster place (CHAR number): the place of a character of its name,
    else a free one (member 0 the highest, as CHARTRAN's order); GffError when there are too few."""
    names = party_names(save)
    listed = {p: roster_name(roster_chunks, p) for p in ROSTER_PLACES}
    out: Dict[int, int] = {}
    for m, name in names.items():
        same = [p for p, n in listed.items() if n == name and p not in out.values()]
        if same:
            out[m] = same[0]
    need = [m for m in names if m not in out]
    free = sorted(p for p, n in listed.items() if n is None)
    if len(free) < len(need):
        raise GffError(f"the sequel's roster has room for {len(ROSTER_PLACES)} characters and the party "
                       f"needs {len(need) - len(free)} more places: delete some in the sequel first "
                       "(CREATE CHARACTERS, a character's DELETE)")
    out.update(zip(need, reversed(free[:len(need)])))  # (the lowest free ones, member 0 highest: CHARTRAN's order)
    return out


def roster(save: Chunks, sequel: Sequel, place_of: Optional[Mapping[int, int]] = None,
           years: Optional[Mapping[int, int]] = None) -> Tuple[Chunks, List[Moved]]:
    """The sequel's roster chunks (CHAR, CACT, SPST, PSST, PSIN) for the party of a parsed save,
    and what moved: each member and its items, SL's object and the sequel's. PLACE_OF: each member's
    place (places), else CHARTRAN's (35 - M). The Loader's way (SEQUEL.loader) the age comes across,
    each member YEARS older (gap_years; none without)."""
    creatures, sheets, items, lists = (_chunk(save, n) for n in (CREATURES, SHEETS, ITEMS, LISTS))
    spells, powers = _chunk(save, SPELLS), _chunk(save, POWERS)
    out: Dict[Tuple[str, int], bytes] = {}
    moved: List[Moved] = []
    for m in range(PARTY):
        rec = creatures[m * SL_CREATURE:(m + 1) * SL_CREATURE]
        if len(rec) < SL_CREATURE or not rec[SL_NAME]:
            continue
        index, = struct.unpack_from("<H", rec, SL_SHEET_INDEX)
        sh = sheets[index * SL_SHEET:(index + 1) * SL_SHEET]
        if len(sh) < SL_SHEET:
            raise GffError("a party member's sheet is missing")
        cre, wsh, age = creature(rec, sh), sheet(sh, sequel.loader), ""
        if sequel.loader:
            wsh = bytearray(wsh)
            wsh[WOTR_SHEET_AGE] = sh[SL_SHEET_AGE] if sh[SL_SPECS + 2] & game.SPEC_PACKED else 0
            name = rec[SL_NAME:SL_CREATURE].split(b"\0")[0].decode("latin1")
            cre, wsh, age = aged(cre, bytes(wsh), name, (years or {}).get(m, 0))
        records = [[1, 0, CREATURE_KIND, m, m, cre], [3, 0, SHEET_KIND, m, SHEET_FLAGS, wsh]]
        log: List[Tuple[int, int]] = []
        named: Dict[int, int] = {}
        bags: List[Tuple[int, int]] = []
        seen = set()

        def walk(lst: int, of: int, flags: int) -> None:
            if lst == NONE or (lst + 1) * 3 > len(lists):
                return
            number, = struct.unpack_from("<H", lists, lst * 3 + 1)
            before = None
            while number != NONE:
                if number in seen or (number + 1) * SL_ITEM > len(items):
                    raise GffError(f"the save's item list {lst} is broken at item {number}")
                seen.add(number)
                it = items[number * SL_ITEM:(number + 1) * SL_ITEM]
                named.setdefault(sl_object(it), struct.unpack_from("<H", it, SL_ITEM_NAME)[0])
                if sequel.loader and struct.unpack_from("<H", it, SL_TYPE)[0] in SPELL_MADE:
                    log.append((sl_object(it), LEFT))
                    number, = struct.unpack_from("<H", it, ITEM_NEXT)
                    if before is not None:  # (the item before it now leads to the next)
                        data = bytearray(records[before][5])
                        struct.pack_into("<H", data, ITEM_NEXT, number)
                        records[before][5] = bytes(data)
                    continue
                data, new = item(it, sequel)
                log.append((sl_object(it), new))
                if before is None:
                    records.append([dataitems.FIRST, of, dataitems.ITEM, number, flags, data])
                else:
                    records.append([dataitems.NEXT, before, dataitems.ITEM, number, NEXT_FLAGS, data])
                before = len(records) - 1
                contents, = struct.unpack_from("<H", it, ITEM_CONTENTS)
                if contents != NONE:
                    bags.append((contents, before))
                number, = struct.unpack_from("<H", it, ITEM_NEXT)

        for at, flags in SL_LISTS:
            walk(struct.unpack_from("<H", rec, at)[0], 0, flags)
            while bags:
                contents, bag = bags.pop()
                walk(contents, bag, BAG_FLAGS)
        count = len(records)
        records[0][1] = count
        recs = [dataitems.Record(*r) for r in records]
        end = dataitems.HEADER.pack(dataitems.END, count, CREATURE_KIND, m, m, 0)
        cid = place_of[m] if place_of is not None else FIRST_CHAR + PARTY - 1 - m
        out[("CHAR", cid)] = dataitems.chunk(recs, end)
        out[("CACT", cid)] = rec[SL_ACTIONS:SL_ACTIONS + 2]
        out[("SPST", cid)] = spells_known(spells[m * SL_SPELLS:(m + 1) * SL_SPELLS])
        out[("PSST", cid)], out[("PSIN", cid)] = powers_known(powers[m * SL_POWERS:(m + 1) * SL_POWERS])
        moved.append(Moved(m, rec[SL_NAME:SL_CREATURE].split(b"\0")[0].decode("latin1"), log, cid, age, named))
    return out, moved


def changed_roster(roster_chunks: Mapping[Tuple[str, int], bytes], new: Mapping[Tuple[str, int], bytes]) -> Chunks:
    """The sequel's roster with the party's chunks in it (the rest as it was)."""
    out = dict(roster_chunks)
    out.update(new)
    return out


ROSTER = "CHARSAVE.GFF"


def load_sequel(folder: str) -> Sequel:
    """ITEMS.BIN and OBJEX.GFF from the player's Wake of the Ravager folder."""
    import os
    from .gff import read_gff
    with open(os.path.join(folder, "ITEMS.BIN"), "rb") as f:
        pairs = counterparts(f.read())
    with open(os.path.join(folder, "OBJEX.GFF"), "rb") as f:
        objects = read_gff(f.read())
    return Sequel(pairs, objects)


def lacking(save: Chunks, sequel: Sequel) -> Dict[int, bytes]:
    """The party's items with no object in the sequel (CHARTRAN's money bags; with SEQUEL's scrolls,
    the scrolls of a spell it lacks instead of all scrolls without a pair): each SL object, the
    first of the save's item records of it."""
    _, moved = roster(save, sequel)
    objects = {old for m in moved for old, new in m.items if new == MONEY_BAG and old != MONEY_BAG}
    carried = {old for m in moved for old, _ in m.items}
    items = _chunk(save, ITEMS)
    out: Dict[int, bytes] = {}
    for at in range(0, len(items) - SL_ITEM + 1, SL_ITEM):
        rec = items[at:at + SL_ITEM]
        obj = sl_object(rec)
        if obj in out or obj not in carried:
            continue
        if sequel.loader and is_scroll(rec):
            if scroll_spell(rec) is None:  # (a scroll of a spell the sequel lacks: a keepsake)
                out[obj] = rec
        elif obj in objects:
            out[obj] = rec
    return out


def with_added(save: Chunks, sequel: Sequel, sl_dir: str, folder: str, dos_dir: str) -> Tuple[Sequel, List[Tuple[int, str]]]:
    """SEQUEL with the Loader's objects for the party's items it lacks (ravitems), made from the
    Shattered Lands in SL_DIR and the sequel in FOLDER, and kept in DOS_DIR's ADDED_FILE with the earlier
    transfers' (their keepsakes' names too); and the items that couldn't be made, with why."""
    import glob
    import os
    from . import art, icons, ravager, ravitems
    from .gff import read_gff, write_atomic
    from . import ravlog
    sequel = sequel._replace(scrolls=scroll_objects(sequel))
    with open(os.path.join(sl_dir, ravager.RESOURCE_FILE), "rb") as f:
        sl_resources = read_gff(f.read())
    with open(os.path.join(folder, ravager.RESOURCE_FILE), "rb") as f:
        sequel_names = ravlog.spell_table(f.read())[1]
    sequel = sequel._replace(spells=spell_map(sl_resources, sequel_names))
    need = lacking(save, sequel)
    kept = ravager.read_added(dos_dir)
    names_text = kept.get(ravitems.NAMES_CHUNK, b"")
    old_pairs = {sl: ravitems.own_object(sl) for sl in need if ("OJFF", ravitems.own_object(sl) or -1) in kept}
    need = {sl: rec for sl, rec in need.items() if sl not in old_pairs}
    failed: List[Tuple[int, str]] = []
    pairs = dict(old_pairs)
    added = {k: v for k, v in kept.items() if k[0] in ravitems.OBJECT_KINDS}
    if need:
        def read(path):
            with open(path, "rb") as f:
                return read_gff(f.read())
        sl_objects = read(os.path.join(sl_dir, "SEGOBJEX.GFF"))
        sl_objects.update(icons.new_chunks(sl_objects))
        loader_copy = os.path.join(dos_dir, icons.OBJECTS_FILE)  # (the Loader's copy for Shattered Lands:
        if os.path.exists(loader_copy):  # its own objects too, Kalzith's scrolls, the tome, the new items)
            sl_objects.update(read(loader_copy))
        gpl = read(os.path.join(sl_dir, "GPLDATA.GFF"))
        sl_names = next(v for k, v in sorted(gpl.items()) if k[0] == "NAME")
        sl_palette = next(art.palette_colours(v) for k, v in sorted(gpl.items()) if k[0] == "PAL " and len(v) >= 768)
        resources = read(os.path.join(folder, ravager.RESOURCE_FILE))
        regions = [v for f in sorted(glob.glob(os.path.join(folder, "RGN*.GFF")))
                   for k, v in read(f).items() if k[0] == "PAL "]
        names = ravitems.Names(sl_names, resources[("TEXT", 1000)],
                               [n for n in names_text.split(b"\n") if n])
        types = ravitems.type_map(sequel.counterparts, sl_objects, sequel.objects)
        table = ravager.mod_types_table(sequel.objects[ravager.TYPES_CHUNK])
        numbers = [r.number for k, v in added.items() if k[0] == "RDFF" for r in dataitems.records(v)[0]]
        new_pairs, chunks, failed = ravitems.make(need, sl_objects, sequel.objects, types, names, sl_palette,
                                                  ravitems.stable_colours(resources, regions), table,
                                                  max(numbers + [ravitems.ITEM_NUMBER_FIRST - 1]) + 1)
        pairs.update(new_pairs)
        added.update(chunks)
        out = dict(added)
        out[ravitems.NAMES_CHUNK] = b"".join(n + b"\n" for n in names.kept)
        write_atomic(os.path.join(dos_dir, ravitems.ADDED_FILE), _gff_file(out))
    objects = dict(sequel.objects)
    objects.update(added)
    return sequel._replace(counterparts={**sequel.counterparts, **pairs}, objects=objects), failed


def _gff_file(chunks: Chunks) -> bytes:
    """A GFF file holding CHUNKS (each type's listed one by one)."""
    types: Dict[str, List[int]] = {}
    for kind, cid in sorted(chunks):
        types.setdefault(kind, []).append(cid)
    data = bytearray(b"GFFI" + bytes(24))
    places = {}
    for key in sorted(chunks):
        places[key] = (len(data), len(chunks[key]))
        data += chunks[key]
    toc = bytearray(struct.pack("<IIH", 0, 0, len(types)))
    for kind, ids in types.items():
        toc += struct.pack("<4sI", kind.encode("latin1"), len(ids))
        for cid in ids:
            toc += struct.pack("<III", cid, *places[(kind, cid)])
    struct.pack_into("<II", data, 12, len(data), len(toc))
    return bytes(data + toc)


def take_party(save_path: str, folder: str, sl_dir: Optional[str] = None,
               dos_dir: Optional[str] = None, months: Optional[int] = None,
               rng=None) -> Tuple[List[Moved], List[Tuple[int, str]]]:
    """The party of the Shattered Lands save SAVE_PATH written into the roster in the sequel's
    FOLDER (CHARSAVE.GFF, kept first as CHARSAVE.GFF.BAK when there is none yet). With SL_DIR (the
    Shattered Lands folder) and DOS_DIR (the mod's dos folder), the items the sequel lacks become the
    Loader's own objects (with_added) instead of money bags, and the party takes free places in the
    roster (places) instead of 32-35, its ages with it; with MONTHS (roll_gap: the age rule on) each
    member a year older with a chance of MONTHS in 12 (RNG). The save is only read. What moved, and
    the items that couldn't be made (each SL object and why), are returned for the report."""
    import os
    import shutil
    from . import icons
    from .gff import read_gff, write_atomic
    with open(save_path, "rb") as f:
        save = read_gff(f.read())
    sequel = load_sequel(folder)
    path = os.path.join(folder, ROSTER)
    with open(path, "rb") as f:
        data = f.read()
    current = read_gff(data)  # (a roster the game can read, before anything is written)
    place_of = years = None
    failed: List[Tuple[int, str]] = []
    if sl_dir and dos_dir:
        import random
        place_of = places(save, current)
        sequel, failed = with_added(save, sequel, sl_dir, folder, dos_dir)
        if months:
            years = gap_years(party_names(save), months, rng or random.Random())
    new, moved = roster(save, sequel, place_of, years)
    backup = path + ".BAK"
    if not os.path.exists(backup):
        shutil.copyfile(path, backup)
    write_atomic(path, icons.with_chunks(data, new))
    return moved, failed


def report(moved: List[Moved], months: Optional[int] = None) -> str:
    """Who went across and what each item became, a line each (MONTHS: the gap between the games)."""
    lines = [f"{months} months have passed since Shattered Lands."] if months else []
    for m in moved:
        from .ravitems import OWN_HIGH
        bags = sum(1 for _, new in m.items if new == MONEY_BAG)
        own = sum(1 for _, new in m.items if new >= OWN_HIGH and new < 30000)
        lines.append(f"{m.name} (roster place {m.place - ROSTER_PLACES[0] + 1}): {len(m.items)} items, {bags} of them a money bag"
                     + (f", {own} the Loader's own" if own else "") + (f"; age: {m.age}" if m.age else ""))
        for old, new in m.items:
            note = (" (a money bag)" if new == MONEY_BAG else " (the Loader's)" if OWN_HIGH <= new < 30000
                    else " (left behind: a spell made it)" if new == LEFT else "")
            lines.append(f"  object {old} -> {new}{note}")
    return "\n".join(lines)


def player_report(moved: List[Moved], months: Optional[int], failed: List[Tuple[int, str]],
                  item_name: Callable[[int], str]) -> str:
    """The report the Loader shows after a transfer: the months, each member's roster place and age,
    and its items by name, what came across as the sequel's own, as the Loader's, left behind or a
    money bag (ITEM_NAME: an SL name entry's text)."""
    from .ravitems import OWN_HIGH
    lines = [f"{months} months have passed since Shattered Lands." if months else "",
             "Start Wake of the Ravager from the Loader: the items made for it are in the Loader's copy of "
             "its files, and the Loader's character sheets are bigger than the game's (they keep the weapon "
             "specs): the sequel started by itself shows the items as money bags and can't read the roster "
             "or the saves once the Loader has started it (python -m dsloader.ravager narrow FOLDER makes "
             "them the game's again, the specs dropped).", ""]
    why = dict(failed)
    for m in moved:
        lines.append(f"{m.name}: place {m.place - ROSTER_PLACES[0] + 1} of the roster (CREATE CHARACTERS, ADD)"
                     + (f"; {m.age}" if m.age else ""))
        kinds: Dict[str, List[str]] = {}
        for old, new in m.items:
            name = item_name((m.named or {}).get(old, 0)) or f"object {old}"
            kind = ("left behind (a spell made it, and the spell is over)" if new == LEFT
                    else f"a money bag ({why.get(old, 'no object for it')})" if new == MONEY_BAG
                    else "made for the sequel by the Loader" if OWN_HIGH <= new < 30000
                    else "the sequel's own")
            kinds.setdefault(kind, []).append(name)
        for kind, names in kinds.items():
            counted = {n: names.count(n) for n in names}
            lines.append(f"  {kind}: " + ", ".join(n if k == 1 else f"{n} ({k})" for n, k in counted.items()))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def transfer(save_path: str, folder: str, sl_dir: str, dos_dir: str, rng=None) -> str:
    """The Loader's button: the party of SAVE_PATH into the sequel in FOLDER, the Loader's way (its
    items made, free roster places, the months rolled and the ages with them), and the report."""
    import os
    import random
    from . import ravitems
    from .gff import read_gff
    rng = rng or random.Random()
    months = roll_gap(rng)
    moved, failed = take_party(save_path, folder, sl_dir, dos_dir, months, rng)
    with open(os.path.join(sl_dir, "GPLDATA.GFF"), "rb") as f:
        gpl = read_gff(f.read())
    names = ravitems.Names(next(v for k, v in sorted(gpl.items()) if k[0] == "NAME"), b"")
    return player_report(moved, months, failed, lambda e: names.sl_name(e).decode("latin1"))


if __name__ == "__main__":
    import sys
    if len(sys.argv) not in (3, 5, 6):
        sys.exit("usage: python -m dsloader.ravtransfer SAVEnn.SAV RAVAGER_FOLDER [SL_FOLDER DOS_FOLDER [MONTHS]]")
    gap = int(sys.argv[5]) if len(sys.argv) == 6 else None
    moved, failed = take_party(*sys.argv[1:5], months=gap)
    print(report(moved, gap))
    for obj, why in failed:
        print(f"object {obj} couldn't be made: {why}")
