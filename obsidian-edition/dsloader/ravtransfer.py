"""The party's way from Shattered Lands into Wake of the Ravager: the sequel's roster records made
from a Shattered Lands save, as SSI's own transfer program (the sequel's CHARTRAN.EXE) makes them.

This first part is CHARTRAN's work, in Python: on every save tried it gives the very bytes CHARTRAN
writes (playtest/logs/2026-11-22-ravager-transfer-format.md), but for one stray spell bit CHARTRAN
sets now and then (its 72nd, set for no spell the member knows). What the mod adds to it (the items
the sequel lacks, kits and weapon specs kept, the months between the games) builds on this.

What it reads from the save (SAVEnn.SAV, its SAVE chunks):
- 5: the creatures (3Ah bytes; the party first), 6: their sheets (47h), 7: the items (15h), 3: the
  item lists (3 bytes: a kind, the list's first item; 9999 none);
- 19: the spells each member knows (138 bytes a member, one a spell: the wizard's 0-68 go across),
  20: the psionic powers (34 bytes a member; 8 known, in the bits CHARTRAN keeps, F8h).

What it writes, for party member M, in the sequel's CHARSAVE.GFF under number 35 - M:
- CHAR: the character, as a list of records each with a 10-byte header (dataitems.HEADER: level,
  of, kind, number, flags, length) and its data, an end record after them: the creature (level 1,
  kind 2, 31h bytes), its sheet (level 3, kind 3, 42h bytes), then its three item lists in turn (the
  creature's +8, +0Ah and +0Ch, flags 16, 17 and 4), each a first item (level 2, "of" 0) and the
  next ones (level 4, "of" the record before), the contents of a bag after the list it is in (its
  first "of" the bag's record, flags 4). The items keep their numbers, the lists theirs.
- CACT: the creature's +6 (its word of actions); SPST: the wizard's spells known, a bit each (72);
  PSST: the powers known (their byte >> 2); PSIN: the disciplines with a power known (1, 2, 4).
- Each item becomes the sequel's object that ITEMS.BIN (in the sequel's folder: an SL object and the
  object to give, a pair of words each) names for it, else 900, a money bag: its record is that
  object's own (the sequel's OBJEX.GFF), with the save's item's links, flags, slot and plus.
"""

import struct
from typing import Dict, List, Mapping, NamedTuple, Optional, Tuple

from . import dataitems
from .gff import Chunks, GffError

NONE = 9999
MONEY_BAG = 900
FIRST_CHAR = 32  # (CHARTRAN's: member M goes to 35 - M)
PARTY = 4

SL_CREATURE, SL_SHEET, SL_ITEM = 0x3A, 0x47, 0x15
CREATURE, SHEET, ITEM = 0x31, 0x42, 0x17
CREATURES, SHEETS, ITEMS, LISTS, SPELLS, POWERS = 5, 6, 7, 3, 19, 20
SL_SPELLS, SL_POWERS = 138, 34
SL_NAME, SL_SHEET_INDEX, SL_ACTIONS, SL_LISTS = 0x28, 0x04, 0x06, ((0x08, 16), (0x0A, 17), (0x0C, 4))
ITEM_NEXT, ITEM_CONTENTS = 0x04, 0x08
BAG_FLAGS, NEXT_FLAGS = 4, 2
CREATURE_KIND, SHEET_KIND, SHEET_FLAGS = 2, 3, 15

# The creature: the sequel's byte from the save's (as CHARTRAN copies them), the name after them
CREATURE_BYTES = [(w, w) for w in range(0x0E)] + [(0x10, 0x18), (0x12, 0x1A), (0x13, 0x1B), (0x14, 0x1C),
                                                  (0x16, 0x1F)] + [(0x19 + i, 0x22 + i) for i in range(6)] + [(0x1F, 0x38)]
CREATURE_FIXED = {0x17: 7}
CREATURE_NAME, NAME_LENGTH = 0x21, 15
# The sheet: SL's less seven bytes (+0Eh, +0Fh, the weapon specs +14h-+17h, +3Ch)
SHEET_RUNS = ((0x00, 0x00, 0x0E), (0x0E, 0x10, 4), (0x12, 0x18, 0x24), (0x37, 0x3D, 0x0A))
# An item: the save's links, flags, slot and plus over the new object's record
ITEM_RUNS = ((0x02, 0x02, 8), (0x0E, 0x0E, 1), (0x12, 0x10, 1), (0x13, 0x11, 1), (0x16, 0x14, 1))

WIZARD_SPELLS = 69  # (SL's 0-68; its priests' after them aren't kept: a priest knows its spheres')
DROPPED_SPELLS = (34, 42, 49, 64)  # (none in the sequel)
POWER_KEPT = 0xF8
DISCIPLINES = ((0, 6, 1), (6, 20, 2), (20, 34, 4))  # (the powers' places of each, its PSIN bit)


def spell_place(spell: int) -> Optional[int]:
    """The sequel's place in SPST of SL's wizard spell SPELL, or None (not carried)."""
    if spell >= WIZARD_SPELLS or spell in DROPPED_SPELLS:
        return None
    if spell < 34 or 52 <= spell < 64:
        return spell
    if spell < 42 or 50 <= spell < 52 or spell > 64:
        return spell - 1
    return spell - 2


class Sequel(NamedTuple):
    """What the transfer reads from the sequel's folder: ITEMS.BIN's pairs and the objects' records."""
    counterparts: Dict[int, int]
    objects: Chunks

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


def creature(rec: bytes) -> bytes:
    out = bytearray(CREATURE)
    for w, s in CREATURE_BYTES:
        out[w] = rec[s]
    for w, value in CREATURE_FIXED.items():
        out[w] = value
    name = rec[SL_NAME:SL_CREATURE].split(b"\0")[0][:NAME_LENGTH]
    out[CREATURE_NAME:CREATURE_NAME + len(name)] = name
    return bytes(out)


def sheet(rec: bytes) -> bytes:
    out = bytearray(SHEET)
    for w, s, n in SHEET_RUNS:
        out[w:w + n] = rec[s:s + n]
    return bytes(out)


def sl_object(rec: bytes) -> int:
    return -struct.unpack_from("<h", rec, 0)[0]


def item(rec: bytes, sequel: Sequel) -> Tuple[bytes, int]:
    """The sequel's item record for the save's item REC, and the object it became."""
    new = sequel.counterparts.get(sl_object(rec), MONEY_BAG)
    out = bytearray(sequel.record(new))
    for w, s, n in ITEM_RUNS:
        out[w:w + n] = rec[s:s + n]
    return bytes(out), new


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


def _chunk(save: Chunks, number: int) -> bytes:
    try:
        return save[("SAVE", number)]
    except KeyError:
        raise GffError(f"the save has no SAVE {number} chunk") from None


def roster(save: Chunks, sequel: Sequel) -> Tuple[Chunks, List[Moved]]:
    """The sequel's roster chunks (CHAR, CACT, SPST, PSST, PSIN) for the party of a parsed save,
    and what moved: each member and its items, SL's object and the sequel's."""
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
        records = [[1, 0, CREATURE_KIND, m, m, creature(rec)], [3, 0, SHEET_KIND, m, SHEET_FLAGS, sheet(sh)]]
        log: List[Tuple[int, int]] = []
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
                contents, bag = bags.pop(0)
                walk(contents, bag, BAG_FLAGS)
        count = len(records)
        records[0][1] = count
        recs = [dataitems.Record(*r) for r in records]
        end = dataitems.HEADER.pack(dataitems.END, count, CREATURE_KIND, m, m, 0)
        cid = FIRST_CHAR + PARTY - 1 - m
        out[("CHAR", cid)] = dataitems.chunk(recs, end)
        out[("CACT", cid)] = rec[SL_ACTIONS:SL_ACTIONS + 2]
        out[("SPST", cid)] = spells_known(spells[m * SL_SPELLS:(m + 1) * SL_SPELLS])
        out[("PSST", cid)], out[("PSIN", cid)] = powers_known(powers[m * SL_POWERS:(m + 1) * SL_POWERS])
        moved.append(Moved(m, rec[SL_NAME:SL_CREATURE].split(b"\0")[0].decode("latin1"), log))
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


def take_party(save_path: str, folder: str) -> List[Moved]:
    """The party of the Shattered Lands save SAVE_PATH written into the roster in the sequel's
    FOLDER (CHARSAVE.GFF, kept first as CHARSAVE.GFF.BAK when there is none yet). The save is
    only read. What moved is returned for the report."""
    import os
    import shutil
    from . import icons
    from .gff import read_gff, write_atomic
    with open(save_path, "rb") as f:
        save = read_gff(f.read())
    new, moved = roster(save, load_sequel(folder))
    path = os.path.join(folder, ROSTER)
    with open(path, "rb") as f:
        data = f.read()
    read_gff(data)  # (a roster the game can read, before anything is written)
    backup = path + ".BAK"
    if not os.path.exists(backup):
        shutil.copyfile(path, backup)
    write_atomic(path, icons.with_chunks(data, new))
    return moved


def report(moved: List[Moved]) -> str:
    """Who went across and what each item became, a line each."""
    lines = []
    for m in moved:
        bags = sum(1 for _, new in m.items if new == MONEY_BAG)
        lines.append(f"{m.name}: {len(m.items)} items, {bags} of them a money bag")
        for old, new in m.items:
            lines.append(f"  object {old} -> {new}{' (a money bag)' if new == MONEY_BAG else ''}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        sys.exit("usage: python -m dsloader.ravtransfer SAVEnn.SAV RAVAGER_FOLDER")
    print(report(take_party(sys.argv[1], sys.argv[2])))
