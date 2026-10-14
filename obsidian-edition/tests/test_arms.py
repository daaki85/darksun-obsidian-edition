"""The arena's gythka and Kurzak's short sword made magic: Kreenfang and Shadowseeker (arms.py)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import arms, dataitems, game, names, npcitems, worldgear
from test_worldgear import ITEM, rdff

BODY = bytes(game.ITEM_TYPE) + struct.pack("<H", 0x6C) + bytes(game.ITEM_SIZE - game.ITEM_TYPE - 2)  # (a dead body)


def record(rec):
    shown, = struct.unpack_from("<H", rec, arms.ITEM_SPELL_SHOWN)
    assert shown == rec[arms.ITEM_SPELL], (shown, rec[arms.ITEM_SPELL])  # (its box's icon: the same spell)
    return (rec[game.ITEM_PLUS], struct.unpack_from("<H", rec, game.ITEM_NAME)[0],
            struct.unpack_from("<H", rec, arms.ITEM_VALUE)[0], rec[arms.ITEM_SPELL])


def gythka(plus=0):
    rec = bytearray(ITEM)
    struct.pack_into("<H", rec, game.ITEM_TYPE, game.GYTHKA_TYPE)
    struct.pack_into("<H", rec, game.ITEM_NAME, 0x3A)
    rec[game.ITEM_PLUS] = plus
    return bytes(rec)


class ArmsTests(unittest.TestCase):
    def test_names_in_dsclog(self):
        """The names are the ones DSCLOG copies into the game's table, after the others'."""
        self.assertEqual(names.NAMES[arms.SWORD_NAME], b"Shadowseeker")
        self.assertEqual(names.NAMES[arms.GYTHKA_NAME], b"Kreenfang")
        self.assertEqual(sorted(names.NAMES), list(range(names.OWN, names.OWN + len(names.NAMES))))

    def test_sword(self):
        """Shadowseeker: +1, its name, priced near the Bloodwrath, Detect Invisibility (one past
        its number) for whoever readies it; Kurzak's, with the switch."""
        sword = arms.shadowseeker(npcitems.SWORD)
        self.assertEqual(record(sword), (1, arms.SWORD_NAME, arms.SWORD_VALUE, game.DETECT_INVISIBILITY + 1))
        self.assertEqual(struct.unpack_from("<H", sword, game.ITEM_TYPE)[0], game.SHORT_SWORD_TYPE)
        self.assertEqual(npcitems.pens(True)[0][1][0], sword)

    def test_the_bodys_gythka(self):
        """In the copy of the arena's dead body (object 1204), its plain gythka is Kreenfang (its
        name attribute too); its other items as they were."""
        chunks = {("RDFF", arms.BODY): rdff(BODY, [ITEM, gythka()]), ("RDFF", 1011): rdff(gythka())}
        out = arms.kreenfang_chunks(chunks)
        self.assertEqual(set(out), {("RDFF", arms.BODY)})
        first, kreenfang = dataitems.items_of(out[("RDFF", arms.BODY)])
        self.assertEqual(first, ITEM)
        self.assertEqual(record(kreenfang), (1, arms.GYTHKA_NAME, arms.GYTHKA_VALUE, 0))
        recs, _ = dataitems.records(out[("RDFF", arms.BODY)])
        self.assertEqual([r.number for r in recs if r.level == dataitems.ATTRIBUTE and r.kind == dataitems.NAME],
                         [struct.unpack_from("<H", ITEM, game.ITEM_NAME)[0], arms.GYTHKA_NAME])
        self.assertEqual(arms.kreenfang_chunks({("RDFF", arms.BODY): out[("RDFF", arms.BODY)]}), {})  # (not twice)

    def test_no_body(self):
        self.assertEqual(arms.kreenfang_chunks({}), {})

    def test_by_the_switch(self):
        """With the magic weapons' switch off: the body's gythka and Kurzak's sword plain."""
        chunks = {("RDFF", arms.BODY): rdff(BODY, [gythka()]), ("RDFF", npcitems.KURZAK): rdff(bytes(58))}
        on = worldgear.data_chunks(chunks, {"world_gear": False, "world_magic": False})
        self.assertEqual(record(dataitems.items_of(on[("RDFF", arms.BODY)])[0])[:2], (1, arms.GYTHKA_NAME))
        self.assertEqual(dataitems.items_of(on[("RDFF", npcitems.KURZAK)])[0][game.ITEM_PLUS], 1)
        off = worldgear.data_chunks(chunks, {"world_gear": False, "world_magic": False, "magic_arms": False})
        self.assertNotIn(("RDFF", arms.BODY), off)
        self.assertEqual(dataitems.items_of(off[("RDFF", npcitems.KURZAK)])[0][game.ITEM_PLUS], 0)


if __name__ == "__main__":
    unittest.main()
