import os
import struct
import unittest

from dsloader import game, gff, spellgrid
from dsloader.weaponpages import ITEM_AT, ITEM_SIZE, WIND_COUNT


def window(places):
    """A WIND with two buttons and the spell places (id, x, y), laid out as the game's."""
    head = bytearray(ITEM_AT)
    head[0:4] = b"WIND"
    items = [(b"BUTN", 0x4394, 23, 102), (b"BUTN", 0x4395, 121, 102)] + [(b"APFM", i, x, y) for i, x, y in places]
    body = b"".join(bytes(4) + tag + struct.pack("<IHH", i, x, y) + bytes(ITEM_SIZE - 16) for tag, i, x, y in items)
    out = bytearray(bytes(head) + body)
    struct.pack_into("<H", out, WIND_COUNT, len(items))
    return bytes(out)


GAME = ([(0x2BCD + n, 47 + 19 * (n % 5), 24 + 20 * (n // 5)) for n in range(15)]
        + [(0x2BDC + n, 142, 24 + 20 * n) for n in range(3)] + [(0x2BDF + n, 28, 24 + 20 * n) for n in range(3)])


def places(w):
    count, = struct.unpack_from("<H", w, WIND_COUNT)
    return [(struct.unpack_from("<I", w, ITEM_AT + i * ITEM_SIZE + 8)[0],) + struct.unpack_from("<HH", w, ITEM_AT + i * ITEM_SIZE + 12)
            for i in range(count)]


class SpellGridTests(unittest.TestCase):
    def test_relaid(self):
        """The first 18 places six to a row, in the order the game fills them, centred where the
        game's seven columns were (28 to 160: the middle at 94); the buttons and the last three kept."""
        got = places(spellgrid.relaid(window(GAME)))
        self.assertEqual(got[:2], [(0x4394, 23, 102), (0x4395, 121, 102)])
        spells = got[2:]
        self.assertEqual(spells[:18], [(0x2BCD + n, 38 + 19 * (n % 6), 24 + 20 * (n // 6)) for n in range(18)])
        self.assertEqual(spells[18:], [(0x2BDF + n, 28, 24 + 20 * n) for n in range(3)])
        left, right = 38, 38 + 19 * 5 + 18
        self.assertLessEqual(abs((left + right) / 2 - (28 + 142 + 18) / 2), 0.5)

    def test_no_level_offers_more(self):
        """No wizard level has more than the grid's 18 with the new spells: the game's 12, 13, 15, 16
        and 13 (1st to 5th), the 1st five more and the 2nd one."""
        game_counts = {1: 12, 2: 13, 3: 15, 4: 16, 5: 13}
        for spell, level in game.NEW_SPELL_LEVELS.items():
            game_counts[level] += 1
        self.assertLessEqual(max(game_counts.values()), spellgrid.PLACES)

    @unittest.skipUnless(os.environ.get("DSUN_RESOURCE"), "needs the game's RESOURCE.GFF")
    def test_the_games_window(self):
        """The game's own WIND 17500 is laid out as GAME, and comes out as the grid."""
        chunks = gff.read_gff(open(os.environ["DSUN_RESOURCE"], "rb").read())
        w = chunks[("WIND", spellgrid.WINDOW)]
        self.assertEqual(places(w)[2:], GAME)
        self.assertEqual(places(spellgrid.chunks(chunks)[("WIND", spellgrid.WINDOW)])[2:20],
                         [(0x2BCD + n, 38 + 19 * (n % 6), 24 + 20 * (n // 6)) for n in range(18)])
