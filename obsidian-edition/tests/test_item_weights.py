"""The same item weighs the same in both games (the owner's, 2026-11-27: "Just ensure weight is the same in
both games"). Read from the player's real files, as the Loader's copies give them: Shattered Lands' item
types (DSUN_SL's GPLDATA.GFF through itemtables.types_chunk: the word at +4) and Wake of the Ravager's
(DSUN_WOTR's OBJEX.GFF through ravager.weighted_table: the byte at +2), both in tenths of a pound.

Two checks: PAIRS, each SL type and the sequel's type of the same thing (the armour pieces are named
differently in each game, so they are paired by hand); and every item name both games have, carried (the
sequel's furniture, doors, bodies and scenery types SCENERY are left out, as RAV_WEIGHTS leaves them), each
of its sequel weights one of its SL weights, but for NAMED, each with why. Without the folders they are
skipped (CI has no game files)."""

import collections
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dataitems, game, gff, itemtables, ravager, ravitems  # noqa: E402

SL = os.environ.get("DSUN_SL")
WOTR = os.environ.get("DSUN_WOTR")

# {SL type: the sequel's type of the same thing} (reports/wake-of-the-ravager-item-weights.md's table)
PAIRS = {
    6: 32, 7: 3, 8: 64,            # leather: chest, arms, legs
    9: 33, 10: 4, 11: 65,          # ring mail
    12: 30, 13: 1, 14: 62,         # brigandine
    15: 34, 55: 5, 56: 63,         # scale mail
    57: 31, 58: 2, 59: 63,         # chain mail
    4: 91, 16: 92, 5: 55,          # shields, helm
    0: 98, 64: 93, 1: 18, 62: 6,   # staff sling, sling, bow, arrows
    2: 51, 3: 85, 17: 72, 18: 29, 19: 80, 20: 67, 21: 24, 22: 8, 44: 52, 48: 25,
    45: 73, 63: 97, 81: 57,        # long swords: obsidian, metal, bone
    42: 12, 60: 9, 65: 28, 66: 10, 68: 44, 96: 77,  # belt, small things, cloak, bag, boots, scroll
    148: 101, 149: 61, 150: 39, 151: 100, 152: 59, 153: 43,  # the Ravager weapons backported to SL
}
# the sequel's types RAV_WEIGHTS leaves as they are: furniture, doors, bodies, chests, scenery
SCENERY = (19, 41, 49, 50, 58, 76)
SL_SCENERY = 2000  # (SL's furniture, doors and scenery weigh 2000 or 3000: no one carries them)
# (name, the sequel's type): why its weight is another game's
NAMED = {
    (b"AXE", 48): "the sequel's obsidian axe (30, as SL's obsidian axe, type 50); SL's Axe is its metal one (70)",
    (b"BAG", 9): "one bag among the sequel's small things (1); its bags' own type, 10, weighs SL's 10",
    (b"ROCK", 94): "the sequel's rock to strike with, a weapon (10); SL's Rock is a small thing (1)",
    (b"DRAGONSBANE", 73): "the sequel's Dragonsbane is an obsidian long sword (30), SL's a metal one (40): "
                          "another material, so another type (the owner's call)",
}


def _read(folder, name):
    for f in os.listdir(folder):
        if f.upper() == name:
            with open(os.path.join(folder, f), "rb") as fh:
                return gff.read_gff(fh.read())
    raise FileNotFoundError(name)


@unittest.skipUnless(SL and WOTR, "needs DSUN_SL and DSUN_WOTR (both games' folders)")
class ItemWeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gpl = _read(SL, "GPLDATA.GFF")
        cls.sl_types = itemtables.types_chunk(gpl[itemtables.TYPES_CHUNK])
        cls.sl_names = next(v for k, v in sorted(gpl.items()) if k[0] == "NAME")
        cls.sl_objects = _read(SL, "SEGOBJEX.GFF")
        cls.objects = _read(WOTR, "OBJEX.GFF")
        cls.types = ravager.weighted_table(cls.objects[ravager.TYPES_CHUNK])
        cls.resources = _read(WOTR, "RESOURCE.GFF")

    def sl_weight(self, kind):
        return struct.unpack_from("<H", self.sl_types, kind * game.ITEM_TYPE_SIZE + 4)[0]

    def weight(self, kind):
        return self.types[kind * ravager.TYPE_SIZE + ravager.TYPE_WEIGHT]

    def test_pairs(self):
        for sl, wotr in PAIRS.items():
            with self.subTest(sl=sl, wotr=wotr):
                self.assertEqual(self.sl_weight(sl), self.weight(wotr))

    def _names(self, objects, at_type, at_name, size, weight, name_of):
        out = collections.defaultdict(set)
        for key in objects:
            if key[0] != "RDFF":
                continue
            try:
                recs, _ = dataitems.records(objects[key])
            except (gff.GffError, struct.error, ValueError):
                continue
            if not recs or len(recs[0].data) < at_name + 2:
                continue
            kind, name = struct.unpack_from("<HH", recs[0].data, at_type)[0], \
                struct.unpack_from("<H", recs[0].data, at_name)[0]
            if (kind + 1) * size > len(self.sl_types if size == game.ITEM_TYPE_SIZE else self.types):
                continue
            text = name_of(name).upper()
            if text:
                out[text].add((kind, weight(kind)))
        return out

    def test_every_item_both_games_have(self):
        names = ravitems.Names(self.sl_names, self.resources[("TEXT", 1000)])
        lines = {n: t for t, n in names.sequel.items()}
        sl = self._names(self.sl_objects, ravitems.SL_ITEM_TYPE, ravitems.SL_ITEM_NAME, game.ITEM_TYPE_SIZE,
                         self.sl_weight, names.sl_name)
        wotr = self._names(self.objects, ravitems.ITEM_TYPE, ravitems.ITEM_NAME, ravager.TYPE_SIZE,
                           self.weight, lambda n: lines.get(n, b""))
        both = set(sl) & set(wotr)
        self.assertGreater(len(both), 20)
        for name in sorted(both):
            weights = {w for _, w in sl[name]}
            if min(weights) >= SL_SCENERY:
                continue  # (SL's own furniture: nobody carries it)
            for kind, w in sorted(wotr[name]):
                if kind in SCENERY or (name, kind) in NAMED:
                    continue
                with self.subTest(name=name, type=kind):
                    self.assertIn(w, weights)

    def test_named_are_still_so(self):
        """Each of NAMED still differs (else it comes off the list)."""
        self.assertEqual(self.weight(73), 30)
        self.assertEqual(self.sl_weight(47), 40)


if __name__ == "__main__":
    unittest.main()
