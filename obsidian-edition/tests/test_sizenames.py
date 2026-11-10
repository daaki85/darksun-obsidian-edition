"""sizes.NAMES' generic names ("Guard", "Slave", "Worker", "Wagon Guard", "Slave Leaders", "Blind One"),
large for the one tusked figure (race 12, kind 31): sizes.size applies NAMES to any creature whose race
isn't a people's, so no other non-person creature in the game may carry one of those names."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gff, monsters, sizes  # noqa: E402

TUSKED = ("Blind One", "Guard", "Slave Leaders", "Wagon Guard", "Worker", "Slave")
TUSKED_RACE, TUSKED_KIND = 12, 31


def creatures(chunks):
    """(name, race, kind) of every object's creature record in CHUNKS (as doccreatures.creatures finds them)."""
    for (kind, _), data in sorted(chunks.items()):
        if kind != "RDFF" or len(data) < monsters.RDFF_SHEET + game.SHEET_SIZE:
            continue
        if any(struct.unpack_from("<H", data, at)[0] != size for at, size in monsters.RDFF_SIZES):
            continue
        at = monsters.RDFF_CREATURE + game.CREATURE_NAME
        name = data[at:at + 16].split(b"\0", 1)[0].decode("cp437").strip()
        yield (name, data[monsters.RDFF_SHEET + game.SHEET_RACE],
               struct.unpack_from("<H", data, monsters.RDFF_CREATURE + monsters.CREATURE_KIND)[0])


class TuskedNamesTests(unittest.TestCase):
    def test_names_large(self):
        for name in TUSKED:
            self.assertEqual(sizes.size(name, TUSKED_RACE), "L", name)
        # (a person of the same name keeps its race's size: the human guards and slaves)
        self.assertEqual(sizes.size("Guard", 1), "M")
        self.assertEqual(sizes.size("Slave", 1), "M")

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the game's SEGOBJEX.GFF (DSUN_OBJECTS)")
    def test_only_the_tusked_figure(self):
        """Every non-person creature the game names so is the tusked figure (race 12, kind 31): the names
        need no kind check (checked 2026-11-10 over SEGOBJEX and the RGN files: none elsewhere)."""
        with open(os.environ["DSUN_OBJECTS"], "rb") as f:
            chunks = gff.read_gff(f.read())
        found = set()
        for name, race, kind in creatures(chunks):
            if name in TUSKED and not 1 <= race <= 8:
                self.assertEqual((race, kind), (TUSKED_RACE, TUSKED_KIND), name)
                found.add(name)
        self.assertEqual(found, set(TUSKED))


if __name__ == "__main__":
    unittest.main()
