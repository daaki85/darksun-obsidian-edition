"""The game's own party, the one START GAME plays when no party has been made: made ready for
the rule changes, once, while the game is new (tools.new_game: its first hour, in the arena).

They are the game's objects (32000 to 32003, and 300, 307, 308 and 313 for their figures), a
creature record and a sheet each, already Okay, so the Loader's way with a new character
(weaponchoice.finish_new) passes them by; the game gives them their gear and spells as it
starts. Each is known by name, race and classes together.

- With weapon specialization: their weapon kinds, matching what they carry. Gerakis (a
  half-giant gladiator) the long sword and the gythka, with the half-giants' rule his club a
  bone gythka, in the same hand: a two-handed weapon beside a one-handed one (the long sword
  weighs 20, the gythka 120: one heavy weapon, as the game allows). K'ratchek (a fighter,
  druid and psionicist) the chatkcha, the one weapon she has. Cermak (a gladiator who became a
  preserver) the long sword and the axe, which count once his gladiator levels do again.
- With kits: Cermak an Arcanist (his preserver class's kit; none for his gladiator class), with
  no change to his gear (an Arcanist has none of its own) or to the hit points the game gave him
  (the Arcanist's d3 counts from his next level).
- With class restrictions: Cilla (a preserver, druid and thief) can't wear armour (the druid's
  rule), so her leather armour is taken away and she knows Armor, the first wizard spell (0),
  the one Old One-Eye's scroll in the fields teaches.
- With fuller starting gear: what a new character would be given (startgear.fill_member), after
  the rest.

Cilla is an elf, but the game gives her the half-elf woman's figure (7, object 307: the human
woman's pictures in the game, the half-elf woman's in the Loader's copy, figures.py). She has
the elf woman's (5) instead: in her record and her object's picture in the Loader's copy of
SEGOBJEX (figure_chunks, for a new game), and in the running game's creature table (elf_figure, for a game begun without
it: the map shows her new figure from the next area or load on).
"""

import struct
from typing import Dict, List, NamedTuple, Set, Tuple

from . import game, restrict, ring, specialize, weaponchoice
from .game import GameData

CILLA_OBJECT = 32003  # (her record in SEGOBJEX: the party's objects are 32000 to 32003)
RDFF_FIGURE = 0x22  # (the record's figure word: the creature's +18h)
CREATURE_FIGURE = 0x18  # (the creature record's figure: sprites.CREATURE_FIGURE)
ELF_WOMAN, HALF_ELF_WOMAN = 5, 7  # (figures: object 300 + the figure)
OBJECT_FIRST, OJFF_PICTURE = 300, 0x0C  # (an object's picture: sprites.OJFF_PICTURE)
KNOWN_SPELLS_PTR = 0x132A  # DS: far pointer to the party's known spells, a byte for each (0 to 137)
KNOWN_STRIDE = game.SPELL_COUNT + 1
ARMOR = 0  # the spell
CLUB_TYPE = 18
KIND = {k: specialize.KINDS.index(k) for k in ("long sword", "axe", "gythka", "chatkcha")}


class Member(NamedTuple):
    race: int
    classes: Tuple[int, int, int]
    kinds: Tuple[str, ...]


PARTY: Dict[str, Member] = {
    "Gerakis": Member(5, (10, 0, 0), ("long sword", "gythka")),  # half-giant gladiator
    "K'ratchek": Member(8, (9, 7, 12), ("chatkcha",)),  # thri-kreen fighter, druid (fire), psionicist
    "Cermak": Member(1, (11, 10, 0), ("long sword", "axe")),  # human preserver, once a gladiator
    "Cilla": Member(3, (11, 6, 17), ()),  # elf preserver, druid (earth), thief
}


def who(gd: GameData, member: int) -> str:
    """The default party's name for party member MEMBER, or "" if it isn't one of them."""
    name = gd.creature_name(member)
    want = PARTY.get(name)
    sheet = gd.sheet(member)
    if want is None or len(sheet) < game.SHEET_SIZE:
        return ""
    if sheet[game.SHEET_RACE] != want.race or tuple(sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]) != want.classes:
        return ""
    return name


def figure_chunks(chunks, current=None) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX (the game's CHUNKS, and the copy's chunks so far,
    CURRENT): Cilla's record with the elf woman's figure, and her object with the elf woman's
    picture (the game's), if they are the game's, with the half-elf woman's."""
    current = chunks if current is None else current
    rec = current.get(("RDFF", CILLA_OBJECT))
    obj = current.get(("OJFF", CILLA_OBJECT))
    elf = chunks.get(("OJFF", OBJECT_FIRST + ELF_WOMAN))
    if rec is None or len(rec) < RDFF_FIGURE + 2 or b"Cilla\0" not in rec \
            or struct.unpack_from("<H", rec, RDFF_FIGURE)[0] != HALF_ELF_WOMAN:
        return {}
    out = bytearray(rec)
    struct.pack_into("<H", out, RDFF_FIGURE, ELF_WOMAN)
    fixed = {("RDFF", CILLA_OBJECT): bytes(out)}
    if obj is not None and elf is not None and len(obj) >= OJFF_PICTURE + 2:
        picture = bytearray(obj)
        picture[OJFF_PICTURE:OJFF_PICTURE + 2] = elf[OJFF_PICTURE:OJFF_PICTURE + 2]
        fixed[("OJFF", CILLA_OBJECT)] = bytes(picture)
    return fixed


def elf_figure(gd: GameData) -> List[str]:
    """Cilla (the game's own, an elf) given the elf woman's figure in a running game, if she has
    the half-elf woman's; a line for the log."""
    for member in range(game.PARTY_SIZE):
        if who(gd, member) != "Cilla":
            continue
        rec = gd.creature(member)
        if struct.unpack_from("<H", rec, CREATURE_FIGURE)[0] != HALF_ELF_WOMAN:
            continue
        creatures = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR)
        gd.guest.write(creatures + member * game.CREATURE_SIZE + CREATURE_FIGURE, struct.pack("<H", ELF_WOMAN))
        return ["Cilla, an elf, has the elf woman's figure (from the next area on)."]
    return []


def kinds_bytes(member: Member) -> bytes:
    """The sheet's kinds (each one past the kind's number, 0 none) for MEMBER."""
    out = bytes(KIND[k] + 1 for k in member.kinds)
    return out + bytes(game.SPEC_COUNT - len(out))


def _type_record(gd: GameData, type_: int) -> bytes:
    types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
    return gd.guest.read(types + type_ * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)


def set_kinds(gd: GameData, member: int, name: str) -> List[str]:
    sheet = gd.sheet(member)
    want = kinds_bytes(PARTY[name])
    if not PARTY[name].kinds or any(sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT]):
        return []
    index = struct.unpack_from("<H", gd.creature(member), game.CREATURE_SHEET_INDEX)[0]
    sheets = game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    gd.guest.write(sheets + index * game.SHEET_SIZE + game.SPEC_SLOTS, want)
    kinds = " and the ".join(PARTY[name].kinds)
    return [f"{name} specializes in the {kinds}."]


def club_to_gythka(gd: GameData, member: int, name: str) -> List[str]:
    """Gerakis's club, in his hand, made a plain bone gythka."""
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    for index, item, _ in gd._worn(member):
        if struct.unpack_from("<H", item, game.ITEM_TYPE)[0] == CLUB_TYPE and item[game.ITEM_PLUS] == 0 \
                and item[game.ITEM_SLOT] in game.WEAPON_HANDS:
            new, _ = weaponchoice.plain_weapon(item, KIND["gythka"])
            gd.guest.write(items + index * game.ITEM_SIZE, new)
            return [f"{name} carries a bone gythka in place of the club."]
    return []


def take_armour(gd: GameData, member: int, name: str) -> List[str]:
    """Plain armour (not a shield) taken from MEMBER, as many pieces as there are."""
    it = ring.Items(gd)
    taken = 0
    for index, item, _ in list(gd._worn(member)):
        type_ = struct.unpack_from("<H", item, game.ITEM_TYPE)[0]
        if item[game.ITEM_PLUS] == 0 and restrict.is_armour(_type_record(gd, type_)) \
                and ring.unlink(gd, it, index, f"{name}'s armour, taken away", empty=True):
            taken += 1
    return [f"{name} has no armour: a druid wears none."] if taken else []


def set_kit(gd: GameData, member: int, name: str) -> List[str]:
    """Cermak an Arcanist: the kit of his preserver class (the one he has now, place 0), if he
    has none yet."""
    from . import kitpages
    sheet = gd.sheet(member)
    if sheet[kitpages.KIT_BYTE] not in (0, 0xFF) or kitpages.kit_place(sheet) is None:
        return []
    kit = kitpages.KITS[5].index("Arcanist") + 1
    index = struct.unpack_from("<H", gd.creature(member), game.CREATURE_SHEET_INDEX)[0]
    sheets = game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    gd.guest.write(sheets + index * game.SHEET_SIZE + kitpages.KIT_BYTE, bytes([kitpages.kit_byte(sheet, 0, kit)]))
    return [f"{name} is an Arcanist."]


def learn(gd: GameData, member: int, name: str, spell: int = ARMOR) -> List[str]:
    known = game.far_pointer(gd.guest, gd.ds, KNOWN_SPELLS_PTR) + member * KNOWN_STRIDE + spell
    if gd.guest.read(known, 1) == b"\x01":
        return []
    gd.guest.write(known, b"\x01")
    return [f"{name} knows {gd.spell_name(spell)}."]


def gear(gd: GameData, member: int, name: str) -> List[str]:
    """MEMBER's starting gear filled out, as a new character's (startgear.py)."""
    from . import startgear
    return startgear.fill_member(gd, member)


def ready(gd: GameData, rules: int, done: Set[Tuple[str, str]], starting_gear: bool = False) -> List[str]:
    """The default party's changes, each once (DONE: what has been done, in this session), while
    the game is new; with STARTING_GEAR, their starting gear filled out too (after the others);
    lines for the log."""
    from . import tools
    if not tools.new_game(gd):
        return []
    out: List[str] = []
    for member in range(game.PARTY_SIZE):
        name = who(gd, member)
        if not name:
            continue
        steps = []
        if rules & game.RULE_SPECIALIZE:
            steps.append(("kinds", set_kinds))
            if name == "Gerakis" and rules & game.RULE_HALF_GIANT:
                steps.append(("gythka", club_to_gythka))
        if name == "Cermak" and rules & game.RULE_KITS:
            steps.append(("kit", set_kit))
        if name == "Cilla" and rules & game.RULE_RESTRICT:
            steps += [("armour", take_armour), ("armor spell", learn)]
        if starting_gear:
            steps.append(("gear", gear))
        for key, step in steps:
            if (name, key) in done:
                continue
            done.add((name, key))
            out += step(gd, member, name)
    return out
