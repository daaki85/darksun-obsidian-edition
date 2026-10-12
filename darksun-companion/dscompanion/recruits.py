"""People who join the party: their characters, in the Ledger's own RECRUITS.GFF (a prototype).

A recruit is a saved character, the kind the game keeps in CHARSAVE.GFF and its ADD lists: a CHAR
chunk (an object record: the creature, its sheet, its items) with its spells and psionics (SPST,
PSST, PSIN). The Ledger writes them to D:\\RECRUITS.GFF (FILE), never the player's CHARSAVE.GFF:
while DSCLOG's RECRUIT adds one, the game's open of CHARSAVE.GFF is sent there instead.

A script asks for one with its random command, N = RECRUIT_N + the recruit's number (RECRUIT in
DSCLOG); the command's result is 0 if the recruit joined, else (no empty slot) not 0, for the
script to answer either way.

Each recruit is made from TEMPLATE, a 3rd-level human fighter's records as the game writes them,
with the recruit's own name, race, scores, class, level, hit points, saves, kit, weapon specs and
gear.
"""

import struct
from typing import Dict, List, NamedTuple, Sequence, Tuple

from . import dataitems, game, kitpages, specialize, weaponchoice, worldgear
from .dataitems import Record

FILE = "RECRUITS.GFF"
RECRUIT_N = 30000

# The template: the creature's record (3Ah bytes) and the sheet's (47h), as a 3rd-level fighter's
CREATURE = bytes.fromhex(
    "1b001b0000000580070206020f270f270f2700000000000000000a0c01010012630a1110121110104761726e2000"
    "000000000000000000000000")
SHEET = bytes.fromhex(
    "a00f0000b80b00001b000f001b00e80305802000000000000101051110121110100900000300000a0c0003030000"
    "0100000100000000000d0f0e10100100000300000000000000")
PSST = bytes.fromhex("08000008080800000000000000000000000000000000000000000000000008000000")
PSIN = bytes.fromhex("010000000000ff")
SPST = bytes(138)
# the creature's record: hit points, PSP, its tag, its figure, its THAC0, its scores, its name
C_HP, C_PSP, C_TAG, C_FIGURE, C_THAC0, C_SCORES, C_NAME, NAME_SIZE = 0, 2, 6, 0x18, 0x1F, 0x22, 0x28, 16
# the sheet's: XP, most hit points, hit points rolled, PSP most, tag, sex, alignment
S_MAX_HP, S_HP_ROLLED, S_PSP, S_TAG, S_SEX, S_ALIGN = 0x08, 0x0A, 0x0C, 0x10, 0x19, 0x1A
MALE = 1
TRUE_NEUTRAL, NEUTRAL_GOOD, CHAOTIC_GOOD = 5, 2, 3  # (the game's alignments: 5 Garn's, true neutral)
LIST_WORN, LIST_HELD = 77, 78  # an item list's header flags: the creature's +08h and +0Ah lists
LAST = game.NO_ITEM
TAGS = 0x8020  # recruit R's tag: TAGS + R (the game's own run up from 8001h)


class Recruit(NamedTuple):
    number: int  # its number in FILE (DSCLOG's RECRUIT: N = RECRUIT_N + number)
    name: str
    race: int  # game.RACE_NAMES
    figure: int  # its party figure: (race - 1) * 2, + 1 for a woman
    scores: Tuple[int, int, int, int, int, int]
    cls: int  # game.CLASS_NAMES
    level: int
    xp: int
    hp: int
    thac0: int
    saves: Tuple[int, int, int, int, int]
    kit: int  # 1-3: its class's kit in kitpages.KITS's order; 0 none
    specs: Tuple[str, ...]  # weapon types (specialize.KINDS)
    alignment: int
    gear: Tuple[Tuple[bytes, int], ...]  # (item record, equipment slot)


def _slot(name: str) -> int:
    return game.EQUIP_SLOTS.index(name)


def _item(spec: Tuple[int, int, int, int], slot: str, count: int = 0) -> Tuple[bytes, int]:
    rec = bytearray(worldgear.weapon(spec))
    if count:
        struct.pack_into("<H", rec, weaponchoice.ITEM_COUNT, count)
    return bytes(rec), _slot(slot)


def _kind(name: str) -> Tuple[int, int, int, int]:
    return weaponchoice.PLAIN[specialize.KINDS.index(name)]


# The game's starting leather pieces (a new warrior's), as type, name, picture, price
LEATHER_CHEST = (6, 0x07, 0xFC02, 10)
LEATHER_ARMS = (7, 0x08, 0xFC01, 20)
LEATHER_LEGS = (8, 0x09, 0xFBFE, 20)
LEATHER_SHIELD = weaponchoice.SHIELD
ARROWS = (weaponchoice.ARROWS[1], weaponchoice.ARROWS[2], weaponchoice.ARROWS[0], weaponchoice.ARROWS[3])

SEMYON = Recruit(
    30, "Semyon", game.HUMAN, 0, (17, 18, 18, 12, 16, 12), 14, 3, 4500, 27, 18, (13, 15, 14, 16, 16),
    1, ("short sword",), NEUTRAL_GOOD,
    (_item(_kind("short sword"), "right hand"), _item(_kind("bow"), "missile"),
     _item(ARROWS, "ammo", weaponchoice.ARROWS[4]), _item(LEATHER_CHEST, "chest"),
     _item(LEATHER_ARMS, "arm"), _item(LEATHER_LEGS, "legs")))

# a half-giant gladiator of the arena (torvak.py): STR, CON and the doubled hit dice a half-giant has
TORVAK = Recruit(
    31, "Torvak", game.RACE_HALF_GIANT, 8, (20, 13, 19, 8, 10, 9), 10, 3, 4500, 48, 18, (13, 15, 14, 16, 16),
    1, ("long sword", "axe"), TRUE_NEUTRAL,
    (_item(LEATHER_SHIELD, "left hand"), _item(LEATHER_CHEST, "chest"), _item(LEATHER_ARMS, "arm"),
     _item(LEATHER_LEGS, "legs"), _item(_kind("long sword"), "right hand")))

RECRUITS: Sequence[Recruit] = (SEMYON, TORVAK)


def _sheet(r: Recruit) -> bytes:
    s = bytearray(SHEET)
    struct.pack_into("<I", s, game.SHEET_XP, r.xp)
    struct.pack_into("<HH", s, S_MAX_HP, r.hp, r.hp)
    struct.pack_into("<H", s, S_TAG, TAGS + r.number)
    flag = {9: 0x20, 10: 0x40, 11: 0x80, 12: 0x100, 17: 0x400}.get(r.cls, 0x200 if r.cls in specialize.RANGERS else 0)
    struct.pack_into("<H", s, game.SHEET_FLAGS, flag)
    kinds = [specialize.KINDS.index(k) + 1 for k in r.specs]
    s[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT] = bytes(kinds + [0] * (game.SPEC_COUNT - len(kinds)))
    s[game.SHEET_RACE], s[S_SEX], s[S_ALIGN] = r.race, MALE, r.alignment
    s[game.SHEET_ABILITIES:game.SHEET_ABILITIES + 6] = bytes(r.scores)
    s[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] = bytes((r.cls, 0, 0))
    s[game.SHEET_LEVELS:game.SHEET_LEVELS + 3] = bytes((r.level, 0, 0))
    s[game.SHEET_LEVELS_BEFORE:game.SHEET_LEVELS_BEFORE + 3] = bytes((r.level, 0, 0))
    s[game.SHEET_SAVES:game.SHEET_SAVES + 5] = bytes(r.saves)
    s[kitpages.KIT_BYTE] = r.kit
    return bytes(s)


def _creature(r: Recruit) -> bytes:
    c = bytearray(CREATURE)
    struct.pack_into("<H", c, C_HP, r.hp)
    struct.pack_into("<H", c, C_TAG, TAGS + r.number)
    struct.pack_into("<H", c, C_FIGURE, r.figure)
    c[C_THAC0] = r.thac0
    c[C_SCORES:C_SCORES + 6] = bytes(r.scores)
    name = r.name.encode("cp437")[:NAME_SIZE - 1]
    c[C_NAME:C_NAME + NAME_SIZE] = name + bytes(NAME_SIZE - len(name))
    return bytes(c)


WIELDED = frozenset(game.EQUIP_SLOTS.index(s) for s in ("right hand", "missile"))  # (list LIST_HELD's)


def character(r: Recruit) -> bytes:
    """Recruit R's CHAR chunk: its creature, its sheet and its gear in two lists as the game's
    own have them, the weapons in hand (and a bow) in LIST_HELD, the rest (armour, a shield,
    arrows) in LIST_WORN; each item in its slot and numbered, naming the next in its list."""
    recs: List[Record] = [Record(1, 0, 2, 0, 0, _creature(r)), Record(3, 0, 4, 0, 71, _sheet(r))]
    lists = ([g for g in r.gear if g[1] not in WIELDED], [g for g in r.gear if g[1] in WIELDED])
    number = len(r.gear)
    for flags, gear in zip((LIST_WORN, LIST_HELD), lists):
        for i, (item, slot) in enumerate(gear):
            number -= 1
            data = bytearray(dataitems.placed(item))
            struct.pack_into("<H", data, game.ITEM_NEXT, number - 1 if i < len(gear) - 1 else LAST)
            struct.pack_into("<H", data, 0x08, LAST)
            data[game.ITEM_SLOT] = slot
            if i == 0:
                recs.append(Record(dataitems.FIRST, 0, dataitems.ITEM, number, flags, bytes(data)))
            else:
                recs.append(Record(dataitems.NEXT, len(recs) - 1, dataitems.ITEM, number,
                                   dataitems.NEXT_FLAGS, bytes(data)))
    total = len(recs)
    recs[0] = recs[0]._replace(of=total)
    return dataitems.chunk(recs, bytes((dataitems.END, total, 2)) + bytes(7))


def chunks(recruits: Sequence[Recruit] = RECRUITS) -> Dict[Tuple[str, int], bytes]:
    """FILE's chunks: each recruit's CHAR, SPST, PSST and PSIN under its number."""
    out: Dict[Tuple[str, int], bytes] = {}
    for r in recruits:
        out[("CHAR", r.number)] = character(r)
        out[("SPST", r.number)] = SPST
        out[("PSST", r.number)] = PSST
        out[("PSIN", r.number)] = PSIN
    return out


def gff_file(chunks_: Dict[Tuple[str, int], bytes]) -> bytes:
    """A GFF file of CHUNKS, laid out as the game's CHARSAVE.GFF (a plain table of contents)."""
    body = bytearray(b"GFFI" + struct.pack("<IIIIII", 0x30000, 0x1C, 0, 0, 8, len(chunks_)))
    table: Dict[str, List[Tuple[int, int, int]]] = {}
    for (kind, number), data in sorted(chunks_.items()):
        table.setdefault(kind, []).append((number, len(body), len(data)))
        body += data
    toc = bytearray(struct.pack("<H", len(table)))
    for kind, entries in table.items():
        toc += struct.pack("<4sI", kind.encode("latin1"), len(entries))
        for e in entries:
            toc += struct.pack("<III", *e)
    toc = struct.pack("<II", 8, len(toc) - 2 + 10) + toc + bytes(10)
    struct.pack_into("<II", body, 12, len(body), len(toc))
    return bytes(body + toc)


def write(dest: str, recruits: Sequence[Recruit] = RECRUITS) -> None:
    with open(dest, "wb") as f:
        f.write(gff_file(chunks(recruits)))
