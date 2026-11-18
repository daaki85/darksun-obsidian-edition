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

*Part of Obsidian Edition's documentation. **Spoilers:** this page names every creature in the game,
those met late in the story too.*

Every creature Shattered Lands defines, each with its figure as the game draws it standing, and
whether [cahulaks](FEATURES.md#cahulaks) can tangle it (a hit that does damage
tangles a man-sized or smaller creature that fails a save against petrification, and it loses
its next turn). The game keeps no size for its creatures, so who is too big is the mod's call,
from AD&D's sizes: half-giants and anything large or bigger can't be tangled (nor anyone Enlarged,
while the spell lasts), nor anything with
nothing a rope could hold, nor two the mod keeps from being tangled by name (the Sand Howler and
the Strine). The people the party meets in towns are here too: any of them can be fought. Names
are the game's own, cut short as the game has them ("Lsr Fire Elem"). The mod's own people (the
slave pens' and the arena's, and the champions) are on [their own page](PEOPLE.md).

**Size** is AD&D's (T tiny, S small, M man-sized, L large, H huge, G gargantuan), which the game
doesn't keep either: people by race (a half-giant large, a halfling small), the
rest by name, from AD&D's and Dark Sun's monster books; a **?** marks the mod's guess, for the
game's own creatures no book describes. [Creature size](FEATURES.md#creature-size) goes by it: a
large one (or bigger) takes AD&D's large weapon dice and isn't held or charmed by Hold Person,
Charm Person, or Charm Person or Mammal (on a person). A name the game gives more than one kind of
creature says, in brackets, where each is met.
"""


def table(rows: List[Creature]) -> str:
    out = [INTRO.rstrip("\n")]
    for title, people in (("People", True), ("Monsters", False)):
        race = "Race | " if people else ""  # (a monster's race is the figure's name's last word: monster, undead...)
        out += ["", f"## {title}", "", f"| Figure | Creature | {race}Size | Cahulaks can tangle it |",
                "|---" * (5 if people else 4) + "|"]
        for c in rows:
            if (1 <= c.race <= 8) == people:
                cells = [f"![](docs/creatures/{slug(c)}.png)", name_text(c)] + ([race_name(c.race)] if people else [])
                out.append("| " + " | ".join(cells + [size_text(c), tangle(c)]) + " |")
    return "\n".join(out) + "\n"


def write(game_dir: str, root: str) -> int:
    """docs/creatures/*.png and CREATURES.md under ROOT; how many creatures."""
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
    with open(os.path.join(root, "CREATURES.md"), "w", encoding="utf-8") as f:
        f.write(table(rows))
    return len(rows)


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(write(sys.argv[1], here), "creatures")
