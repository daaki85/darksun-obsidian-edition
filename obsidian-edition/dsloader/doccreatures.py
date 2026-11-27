"""The creatures' table (CREATURES.md): every creature the game defines (its objects' records, RDFF,
with a creature record and a sheet: monsters.RDFF_SIZES), one row a name and race, the default party
left out, each with its figure as the game draws it standing (the object's picture, OJFF +0Ch: its
first frame) and whether the cahulaks can tangle it (cahulaks.why_not). `python -m
dsloader.doccreatures GAME_FOLDER` writes docs/creatures/*.png (twice their size, the rest
transparent, as docicons' items) and CREATURES.md, from the game's SEGOBJEX.GFF and palette."""

import os
import re
import struct
import sys
from typing import Dict, List, NamedTuple, Optional, Tuple

from . import art, cahulaks, docicons, game, gff, monsters, sizes

PICTURE = 0x0C          # an object's picture (OJFF +0Ch, as sprites.OJFF_PICTURE)
PARTY = frozenset(("Gerakis", "Cermak", "Cilla", "K'ratchek"))  # (the default party: not foes)
RACES = {**game.RACE_NAMES, 0: "elemental", 9: "undead"}  # (the rest: "monster")
BIG = 64                # (a figure wider than this drawn at its own size, not doubled)
# the creatures that walk under the ground or the silt and come up to fight: drawn with their
# fighting picture (the next number), not the mound or ripple they walk as. Only these: for anyone
# else the next number is another object's picture (Gilal's coffin, an elf on a box)
BURROWERS = frozenset(("Bulette", "Fire Eel", "Silt Horror"))
# where the game's creatures of one name are met (their objects' places in the regions' ETAB, by the
# cluebook's names for the regions), for a name more than one kind of creature has
NOTES = {("Guard", 1): "the towns' and camps' guards", ("Guard", 5): "the slave pens' half-giants",
         ("Guard", 12): "a magera, at the Silt Sea Summoning", ("Slave", 1): "the elven slavers' captives, and others",
         ("Slave", 12): "a magera, in the Wyrm Belly", ("Worker", 12): "a magera, in the Wyrm Belly"}


class Creature(NamedTuple):
    obj: int
    name: str
    race: int


def creatures(chunks) -> List[Creature]:
    """One for each name and race, its lowest object with a picture, sorted people first, then by name."""
    seen: Dict[Tuple[str, int], Creature] = {}
    for (kind, obj), data in sorted(chunks.items()):
        if kind != "RDFF" or len(data) < monsters.RDFF_SHEET + game.SHEET_SIZE:
            continue
        if any(struct.unpack_from("<H", data, at)[0] != size for at, size in monsters.RDFF_SIZES):
            continue
        at = monsters.RDFF_CREATURE + game.CREATURE_NAME
        name = data[at:at + 16].split(b"\0", 1)[0].decode("cp437").strip()
        race = data[monsters.RDFF_SHEET + game.SHEET_RACE]
        if not name or name in PARTY or (name, race) in seen or rows_of(chunks, obj) is None:
            continue
        seen[(name, race)] = Creature(obj, name, race)
    return sorted(seen.values(), key=lambda c: (not 1 <= c.race <= 8, c.name.lower(), c.race))


def _first(chunks, number: int) -> Optional[List[List[Optional[int]]]]:
    if ("BMP ", number) not in chunks:
        return None
    try:
        return art.decode_frame(chunks[("BMP ", number)], 0)[2]
    except (ValueError, IndexError, struct.error):
        return None


def _size(rows) -> int:
    return sum(p is not None for row in rows for p in row) if rows else 0


def rows_of(chunks, obj: int, name: str = "") -> Optional[List[List[Optional[int]]]]:
    """Object OBJ's figure as rows of palette numbers: its picture's first frame (standing), or, for
    one of BURROWERS (NAME), its fighting picture's (the next number) where that shows half as much
    again."""
    rec = chunks.get(("OJFF", obj))
    if rec is None or len(rec) < PICTURE + 2:
        return None
    number, = struct.unpack_from("<H", rec, PICTURE)
    walking, fighting = _first(chunks, number), _first(chunks, number + 1)
    if name in BURROWERS and fighting is not None and _size(fighting) * 2 > _size(walking) * 3:
        return fighting
    return walking


def slug(c: Creature) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", c.name.lower().replace("'", "")).strip("-")
    return f"{base}-{RACES.get(c.race, 'monster').replace(' ', '-')}"


def race_name(race: int) -> str:
    return RACES.get(race, "monster")


def size_text(c: Creature) -> str:
    """The size's letter (the intro gives their words), and " ?" for the mod's guess."""
    letter = sizes.size(c.name, c.race)
    unsure = c.race in sizes.UNSURE_RACES if 1 <= c.race <= 8 else c.name in sizes.UNSURE
    return f"{letter}{' ?' if unsure else ''}"


def name_text(c: Creature) -> str:
    """The creature's name, and where it is met (NOTES) in brackets after it."""
    note = NOTES.get((c.name, c.race))
    return f"{c.name} ({note})" if note else c.name


def tangle(c: Creature) -> str:
    why = cahulaks.why_not(c.name, c.race)
    return f"no: {why}" if why else "yes"


INTRO = """# Creatures

*Part of Obsidian Edition's documentation. **Spoilers:** this page names every creature in both games,
those met late in the story too.*

Every creature [Shattered Lands](#shattered-lands) and [Wake of the Ravager](#wake-of-the-ravager) define,
each game's in its own tables, with its figure as the game draws it standing, its size, and whether
[cahulaks](FEATURES.md#cahulaks) can tangle it (a hit that does damage tangles a man-sized or smaller
creature that fails a save against petrification, and it loses its next turn). The people the party meets
in towns are here too: any of them can be fought. The mod's own people (Shattered Lands' slave pens' and
arena's, and the champions) are on [their own page](PEOPLE.md).

**Size** is AD&D's (T tiny, S small, M man-sized, L large, H huge, G gargantuan), which neither game
keeps: the mod gives people theirs by race (a half-giant large, a halfling small) and the rest by name,
from AD&D's and Dark Sun's monster books; a **?** marks the mod's guess, for the games' own creatures no
book describes. [Creature size](FEATURES.md#creature-size) goes by it: a large one (or bigger) takes AD&D's
large weapon dice and isn't held or charmed by Hold Person or Charm Person (nor, in Shattered Lands, by
Charm Person or Mammal on a person).

## Shattered Lands

Who is too big for the cahulaks is the mod's call: half-giants and anything large or bigger can't be
tangled (nor anyone Enlarged, while the spell lasts), nor anything with nothing a rope could hold, nor
two the mod keeps from being tangled by name (the Sand Howler and the Strine). Names are the game's own,
cut short as the game has them ("Lsr Fire Elem"). A name the game gives more than one kind of creature
says, in brackets, where each is met.
"""


def table(rows: List[Creature]) -> str:
    out = [INTRO.rstrip("\n")]
    for title, people in (("People", True), ("Monsters", False)):
        race = "Race | " if people else ""  # (a monster's race is the figure's name's last word: monster, undead...)
        out += ["", f"### {title} in Shattered Lands", "", f"| Figure | Creature | {race}Size | Cahulaks can tangle it |",
                "|---" * (5 if people else 4) + "|"]
        for c in rows:
            if (1 <= c.race <= 8) == people:
                cells = [f"![](docs/creatures/{slug(c)}.png)", name_text(c)] + ([race_name(c.race)] if people else [])
                out.append("| " + " | ".join(cells + [size_text(c), tangle(c)]) + " |")
    return "\n".join(out) + "\n"


# --- Wake of the Ravager: its creatures (OBJEX.GFF), drawn as the mod draws them ---

RAV_FOLDER = "ravager"  # (their figures: docs/creatures/ravager/*.png)
RAV_PARTY = frozenset(range(32000, 32004))  # (the sequel's own party, Terrannus, Thy-rohk, Gerrakis, Ar'Anda: not foes)
RAV_CREATURE_KIND, RAV_SHEET_KIND = 2, 3  # (an object's records, dataitems: the creature's and its sheet's)
RAV_PALETTE = ("RESOURCE.GFF", ("PAL ", 1000))  # (the sequel's map colours)
# the creatures the sequel draws in their fights from RESOURCE.GFF's pictures, redrawn there too (ravfigures'
# RESOURCE.GFF chunks: the Tarrasque's halves 11001-11002, whose object's own picture is blank)
RAV_FIGHT_DRAWN = frozenset(("Tarrasque",))
RAV_RACES = {**game.RACE_NAMES, 9: "undead", 14: "elemental", 15: "yuan-ti", 16: "illithid"}  # (the rest: "monster")
class RavCreature(NamedTuple):
    obj: int
    name: str
    race: int
    picture: Optional[int]  # (its picture's number as the mod draws it, None for an object with none)


def rav_creatures(chunks, mod=None) -> List[RavCreature]:
    """Wake of the Ravager's creatures in its OBJEX.GFF CHUNKS (an object's records, dataitems, with a
    creature record and a sheet, the game's sizes: ravager.CREATURE_SIZE, GAME_SHEET_SIZE), one for each name
    and race, its lowest object with a picture (in MOD, the chunks as the mod has them), or the lowest
    without; the sequel's party left out; people first, then by name."""
    from . import dataitems, ravager
    mod = mod if mod is not None else chunks
    name_at = ravager.creature_field(game.CREATURE_NAME)
    race_at = ravager.sheet_field(game.SHEET_RACE)
    seen: Dict[Tuple[str, int], RavCreature] = {}
    for (kind, obj), data in sorted(chunks.items()):
        if kind != "RDFF" or obj in RAV_PARTY:
            continue
        try:
            recs, _ = dataitems.records(data)
        except (ValueError, struct.error):
            continue
        creature = [r.data for r in recs if r.kind == RAV_CREATURE_KIND and len(r.data) == ravager.CREATURE_SIZE]
        sheet = [r.data for r in recs if r.kind == RAV_SHEET_KIND and len(r.data) == ravager.GAME_SHEET_SIZE]
        if not creature or not sheet:
            continue
        name = creature[0][name_at:name_at + 16].split(b"\0", 1)[0].decode("cp437").strip()
        race = sheet[0][race_at]
        if not name:
            continue
        rec = mod.get(("OJFF", obj))
        picture = struct.unpack_from("<H", rec, PICTURE)[0] if rec is not None and len(rec) >= PICTURE + 2 else None
        if picture is not None and not _size(_first(mod, picture)):
            picture = None  # (none, or blank: the Tarrasque's, RAV_FIGHT_DRAWN)
        old = seen.get((name, race))
        if old is None or (old.picture is None and picture is not None):
            seen[(name, race)] = RavCreature(obj, name, race, picture)
    return sorted(seen.values(), key=lambda c: (not 1 <= c.race <= 8, c.name.lower(), c.race))


def rav_race_name(race: int) -> str:
    return RAV_RACES.get(race, "monster")


def rav_slugs(rows: List[RavCreature]) -> Dict[int, str]:
    """Each creature's figure's name (by object): its name and race as slug's, and its object's number after
    them for a second of the same ("Guard" of two kinds of monster, "Int. Devourer" and "Int.Devourer")."""
    out: Dict[int, str] = {}
    for c in rows:
        base = re.sub(r"[^a-z0-9]+", "-", c.name.lower().replace("'", "")).strip("-") + "-" + rav_race_name(c.race)
        out[c.obj] = base if base not in out.values() else f"{base}-{c.obj}"
    return out


def rav_size_text(c: RavCreature) -> str:
    """The size's letter by the sequel's table (sizes.RAV_NAMES: people by race, the rest by name, else
    man-sized), and " ?" for the mod's guess (sizes.RAV_UNSURE, a thri-kreen, and any name the table lacks)."""
    from . import sizes
    people = 1 <= c.race <= 8
    if not people and c.name in sizes.RAV_NAMES:
        return sizes.RAV_NAMES[c.name] + (" ?" if c.name in sizes.RAV_UNSURE else "")
    letter = sizes.RACES.get(c.race, "M")
    return letter + (" ?" if (c.race in sizes.UNSURE_RACES if people else True) else "")


def rav_tangle(c: RavCreature) -> str:
    """The cahulaks in the sequel (DSCLOG2's CAH_HIT): no half-giant, nothing large or bigger by the sequel's
    table (IS_LARGE); no list by name, as Shattered Lands' cahulaks.why_not has."""
    if c.race == 5:
        return "no: too big (a half-giant)"
    if rav_size_text(c)[0] in "LHG":
        return "no: too big"
    return "yes"


def rav_redrawn(c: RavCreature, data: Optional[dict] = None) -> bool:
    """C's figure is one of the redrawn (ravfigures: its picture replaced or the object moved to a new one)."""
    from . import ravfigures
    data = data or ravfigures.load()
    if c.name in RAV_FIGHT_DRAWN:
        return True
    if c.picture is None:
        return False
    return ("BMP ", c.picture) in data["files"].get("OBJEX.GFF", {}) or any(o == c.obj for o, _, _ in data["objects"])


RAV_INTRO = """## Wake of the Ravager

Every creature [the sequel](RAVAGER.md) defines (its OBJEX.GFF), each with its figure as the mod draws it
standing: the **Drawn** column says *redrawn* for the ones [redrawn in Shattered Lands'
style](RAVAGER.md#the-mod-in-the-sequel) (the Loader puts them in each start) and *the game's* for the
rest. The sequel's own party (Terrannus, Thy'rokh, Gerakis, Ar'Anda) is left out; a creature the sequel
gives no figure says *none*. A name in two rows is two kinds of creature, each with its own figure, and a
name met in both games is a different creature in each (its own figure and numbers), so it is in each
game's tables. Names are the sequel's own, cut short as it has them ("Grt Air Elem").

**Size** goes by the sequel's own table, as Shattered Lands' does: people by race, the monsters the mod has
looked up by name. A name the table doesn't have is taken as man-sized and marked **?**. The cahulaks in the
sequel go by size alone: a half-giant or anything large or bigger can't be tangled (nor anyone Enlarged),
but the shapeless (a shadow, a dust devil) and Shattered Lands' creatures kept from being tangled by name have
no counterpart yet ([a gap](RAVAGER.md#not-in-the-sequel-yet)).
"""


def rav_table(rows: List[RavCreature], data: Optional[dict] = None) -> str:
    out = [RAV_INTRO.rstrip("\n")]
    slugs = rav_slugs(rows)
    for title, people in (("People", True), ("Monsters", False)):
        race = "Race | " if people else ""
        out += ["", f"### {title} in Wake of the Ravager", "",
                f"| Figure | Creature | {race}Size | Cahulaks can tangle it | Drawn |",
                "|---" * (6 if people else 5) + "|"]
        for c in rows:
            if (1 <= c.race <= 8) != people:
                continue
            figure = f"![](docs/creatures/{RAV_FOLDER}/{slugs[c.obj]}.png)" if c.picture is not None else "none"
            drawn = "redrawn" if rav_redrawn(c, data) else ("the game's" if c.picture is not None else "none")
            if c.name in RAV_FIGHT_DRAWN:
                drawn = "redrawn (its fight's figure; none on the map)"
            cells = [figure, c.name] + ([rav_race_name(c.race)] if people else [])
            out.append("| " + " | ".join(cells + [rav_size_text(c), rav_tangle(c), drawn]) + " |")
    return "\n".join(out) + "\n"


def rav_mod_chunks(rav_dir: str):
    """The sequel's OBJEX.GFF chunks as the game has them, and as the mod has them (the redrawn figures:
    ravfigures.object_chunks; RESOURCE.GFF's pictures too, for an object whose picture is there)."""
    from . import ravfigures
    with open(os.path.join(rav_dir, "OBJEX.GFF"), "rb") as f:
        chunks = gff.read_gff(f.read())
    mod = dict(chunks)
    mod.update(ravfigures.object_chunks(chunks))
    return chunks, mod


def write_ravager(rav_dir: str, root: str) -> Tuple[str, int]:
    """docs/creatures/ravager/*.png under ROOT, and the sequel's part of CREATURES.md (returned)."""
    chunks, mod = rav_mod_chunks(rav_dir)
    name, key = RAV_PALETTE
    with open(os.path.join(rav_dir, name), "rb") as f:
        palette = art.palette_colours(gff.read_gff(f.read())[key])
    rows = rav_creatures(chunks, mod)
    out_dir = os.path.join(root, "docs", "creatures", RAV_FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    for old in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, old))
    slugs = rav_slugs(rows)
    for c in rows:
        if c.picture is None:
            continue
        figure = _first(mod, c.picture)
        zoom = 1 if max((len(r) for r in figure), default=0) > BIG else docicons.ZOOM
        with open(os.path.join(out_dir, slugs[c.obj] + ".png"), "wb") as f:
            f.write(docicons.png(figure, palette, zoom))
    return rav_table(rows), len(rows)


def write(game_dir: str, root: str, rav_dir: Optional[str] = None) -> int:
    """docs/creatures/*.png and CREATURES.md under ROOT (with RAV_DIR, the sequel's folder, its part too:
    write_ravager); how many creatures."""
    with open(os.path.join(game_dir, "SEGOBJEX.GFF"), "rb") as f:
        chunks = gff.read_gff(f.read())
    with open(os.path.join(game_dir, "GPLDATA.GFF"), "rb") as f:
        palette = art.palette_colours(gff.read_gff(f.read())[("PAL ", 1)])
    rows = creatures(chunks)
    out_dir = os.path.join(root, "docs", "creatures")
    os.makedirs(out_dir, exist_ok=True)
    for c in rows:
        figure = rows_of(chunks, c.obj, c.name)
        zoom = 1 if max((len(r) for r in figure), default=0) > BIG else docicons.ZOOM
        with open(os.path.join(out_dir, slug(c) + ".png"), "wb") as f:
            f.write(docicons.png(figure, palette, zoom))
    text, count = table(rows), len(rows)
    if rav_dir:
        rav_text, rav_count = write_ravager(rav_dir, root)
        text, count = text + "\n" + rav_text, count + rav_count
    with open(os.path.join(root, "CREATURES.md"), "w", encoding="utf-8") as f:
        f.write(text)
    return count


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(write(sys.argv[1], here, sys.argv[2] if len(sys.argv) > 2 else None), "creatures")
