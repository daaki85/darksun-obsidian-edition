"""The party transfer's items the sequel lacks, as objects of the Loader's (dsloader/ravitems.py).

Made-up objects here; with DSUN_WOTR (the player's Wake of the Ravager folder) and DSUN_SL (Shattered
Lands'), the kit's trap-user party goes through with every item kept (no money bag)."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import dataitems, game, gff, icons, names, npcitems, ravager, ravitems, ravtransfer as rt  # noqa: E402

WOTR, SL = os.environ.get("DSUN_WOTR"), os.environ.get("DSUN_SL")
SAVES = os.path.join(os.path.dirname(__file__), "..", "..", "playtest", "saves")


def record(obj, kind):
    data = bytearray(0x17)
    struct.pack_into("<hH", data, 0, -obj, 0)
    struct.pack_into("<H", data, 0x0A, kind)
    return dataitems.chunk([dataitems.Record(1, 0, 1, 1, 0, bytes(data))], dataitems.HEADER.pack(dataitems.END, 0, 0, 0, 0, 0))


def sl_item(obj, kind, name):
    rec = bytearray(rt.SL_ITEM)
    struct.pack_into("<h", rec, 0, -obj)
    struct.pack_into("<H", rec, 0x0A, kind)
    struct.pack_into("<H", rec, 0x12, name)
    return bytes(rec)


class NumbersTests(unittest.TestCase):
    def test_own_object(self):
        self.assertEqual([ravitems.own_object(o) for o in (2427, 1095, 30032, 31999, 0, 36000)],
                         [22427, 21095, 14032, 15999, None, None])

    def test_type_map_most(self):
        sl = {("RDFF", 1): record(1, 66), ("RDFF", 2): record(2, 66), ("RDFF", 3): record(3, 66)}
        wotr = {("RDFF", 10): record(10, 10), ("RDFF", 11): record(11, 10), ("RDFF", 12): record(12, 5)}
        self.assertEqual(ravitems.type_map({1: 10, 2: 11, 3: 12}, sl, wotr), {66: 10})

    def test_sequel_type(self):
        self.assertEqual(ravitems.sequel_type(115, {}), 102)
        self.assertEqual(ravitems.sequel_type(66, {66: 10}), 10)
        self.assertEqual(ravitems.sequel_type(60, {}), ravitems.KEEPSAKE_TYPE)


    def test_backported_weapons_are_the_sequels(self):
        """SL's plain Ravager weapons backported (148-152) become the sequel's type of that weapon, not
        keepsakes."""
        from dsloader import game, specialize
        want = {"two-handed sword": 101, "lotulis": 61, "double spear": 39, "trikal": 100, "javelin": 59}
        for t in ravager.SEQUEL_OWN_WEAPONS:
            self.assertEqual(ravitems.sequel_type(t, {}), want[specialize.KINDS[specialize.KIND_OF_TYPE[t]]], t)

    def test_darts_keep_their_type(self):
        """SL's darts (wood) become the mod's own darts in the sequel (140), not its stone ones (43) or its
        ones of no material (38); game.RAVAGER_TYPES is what the transfer gives each (2026-11-27: it said 38,
        the transfer 43)."""
        from dsloader import game
        self.assertEqual(ravitems.sequel_type(game.DARTS_TYPE, {}), 140)
        for t, want in game.RAVAGER_TYPES.items():
            self.assertEqual(ravitems.sequel_type(t, {}), want, t)

    def test_material_weapons_keep_their_type(self):
        """The metal great sword, lotulis and javelin, the obsidian lotulis and the bone great sword (SL
        154-158) become the mod's own types in the sequel (141-145), SL's record (material, sphere bits,
        dice, weight) theirs: not the sequel's one type of the kind, which loses the material (a water
        cleric's bone great sword an obsidian one, a fire cleric's obsidian lotulis a stone one)."""
        from dsloader import game
        five = (game.METAL_TWOHAND_SWORD_TYPE, game.METAL_LOTULIS_TYPE, game.METAL_JAVELIN_TYPE,
                game.OBSIDIAN_LOTULIS_TYPE, game.BONE_GREAT_SWORD_TYPE)
        self.assertEqual([ravitems.sequel_type(t, {}) for t in five], [141, 142, 143, 144, 145])
        self.assertEqual([game.RAVAGER_TYPES[t] for t in five], [141, 142, 143, 144, 145])
        table = ravager.mod_types_table(bytes(ravager.GAME_TYPES * ravager.TYPE_SIZE))
        for t in five:
            sl = npcitems.TYPES[t - game.GAME_TYPES]
            w = ravager.mod_type(t)
            self.assertEqual(table[w * ravager.TYPE_SIZE:(w + 1) * ravager.TYPE_SIZE], ravager.wotr_type(sl), t)
            self.assertEqual(table[w * ravager.TYPE_SIZE + ravager.TYPE_WEIGHT], struct.unpack_from("<H", sl, 4)[0])
            self.assertEqual(table[w * ravager.TYPE_SIZE + 4], sl[8], t)  # (the material)
        bone = npcitems.TYPES[game.BONE_GREAT_SWORD_TYPE - game.GAME_TYPES]
        self.assertEqual(struct.unpack_from("<H", bone, 4)[0], 110)  # (11 lb, both games: the user's, 2026-11-27)


class MaterialTests(unittest.TestCase):
    """SL's own weapons keep their kind and material in the sequel (the user's, 2026-11-27)."""

    @staticmethod
    def tables():
        """An SL type table: type 81 a bone long sword (SL's), 33 a stone dagger, 2 a metal great axe, 84 a
        metal melee dagger; and the sequel's: 73 an obsidian long sword, 37 a stone dagger, 99 a thrown metal
        dagger (ravager.rav_kinds' kinds; its other bytes 0), the mod's and SL's extra types after them."""
        sl = bytearray(game.GAME_TYPES * 20)
        def put(t, flags, material):
            sl[t * 20], sl[t * 20 + 8] = flags, material
        put(81, 1, 1); put(33, 1, 2); put(2, 1, 4); put(84, 0x11, 4)
        wotr = bytearray(ravager.GAME_TYPES * ravager.TYPE_SIZE)
        for t, flags, material in ((73, 1, 3), (37, 1, 2), (99, 0x12, 4)):
            wotr[t * 15], wotr[t * 15 + 4] = flags, material
        return bytes(sl) + b"".join(npcitems.TYPES), ravager.mod_types_table(bytes(wotr))

    def test_same_kind_and_material(self):
        sl, wotr = self.tables()
        self.assertEqual(ravitems.sequel_type(81, {81: 73}, sl, wotr), ravager.EXTRA_FIRST)  # (bone: SL's copy)
        self.assertEqual(ravitems.sequel_type(33, {33: 72}, sl, wotr), 37)  # (stone: the sequel's own)
        self.assertEqual(ravitems.sequel_type(2, {}, sl, wotr), ravager.mod_type(game.METAL_GREAT_AXE_TYPE))
        self.assertEqual(ravitems.sequel_type(84, {}, sl, wotr), ravager.mod_type(game.METAL_DAGGER_TYPE))  # (not 99)
        self.assertEqual(ravitems.sequel_type(33, {33: 72}), 72)  # (no tables: ITEMS.BIN's, as before)

    def test_pairs_of_another_material_dropped(self):
        sl, wotr = self.tables()
        sl_objects = {("RDFF", 1012): record(1012, 81), ("RDFF", 1190): record(1190, 33), ("RDFF", 5): record(5, 60)}
        sequel_objects = {("RDFF", 614): record(614, 73), ("RDFF", 648): record(648, 37), ("RDFF", 9): record(9, 9)}
        seq = rt.Sequel({1012: 614, 1190: 648, 5: 9}, sequel_objects)
        self.assertEqual(rt.weapon_pairs(seq, sl_objects, sl, wotr), {1190: 648, 5: 9})

    def test_stale_weapon_made_anew(self):
        sl, wotr = self.tables()
        kept = {("RDFF", 21012): record(21012, 73)}
        self.assertTrue(ravitems.stale(kept, 21012, sl_item(1012, 81, 1), sl, wotr))
        kept = {("RDFF", 21012): record(21012, ravager.EXTRA_FIRST)}
        self.assertFalse(ravitems.stale(kept, 21012, sl_item(1012, 81, 1), sl, wotr))
        kept = {("RDFF", 21012): record(21012, 61)}
        self.assertTrue(ravitems.stale(kept, 21012, sl_item(1012, game.OBSIDIAN_LOTULIS_TYPE, 1)))


class NamesTests(unittest.TestCase):
    def test_names(self):
        sl = bytearray(25 * 4)
        sl[25:25 + 4], sl[50:50 + 12], sl[75:75 + 4] = b"Gem\0", b"Slavepen key", b"Gem\0"
        n = ravitems.Names(bytes(sl), b"Tombstone\r\nGem\r\n", [b"Old one"])
        self.assertEqual(n.number(1), 2)  # (the sequel's Gem: line 1, name 2)
        self.assertEqual(n.number(npcitems.SHORT_SWORD), 258)
        self.assertEqual(n.number(2), ravager.KEEPSAKE_NAMES_FIRST + 1)
        self.assertEqual(n.number(2), ravager.KEEPSAKE_NAMES_FIRST + 1)
        self.assertEqual(n.kept, [b"Old one", b"Slavepen key"])

    def test_item_names_table(self):
        table = ravager.item_names([b"Slavepen key"])
        at = (ravager.KEEPSAKE_NAMES_FIRST - ravager.NAMES_GAME) * ravager.NAME_KEPT
        self.assertEqual(table[at:at + 13], b"Slavepen key\0")
        self.assertEqual(len(table), ravager.NAMES_ROOM * ravager.NAME_KEPT)

    def test_keepsakes_after_the_mods_names(self):
        """The keepsakes' names come after every one of the mod's (names.NAMES at ravager.mod_name): none of
        the mod's is overwritten (2026-11-27: the first keepsake's "Long Sword" took the Great Sword's 306)."""
        from dsloader import names
        self.assertEqual(ravager.KEEPSAKE_NAMES_FIRST, ravager.NAMES_GAME + names.EXTRA)
        self.assertLess(max(ravager.mod_name(e) for e in names.NAMES), ravager.KEEPSAKE_NAMES_FIRST)
        table = ravager.item_names([b"Long Sword"] * ravager.NAMES_ROOM)
        for entry, name in names.NAMES.items():
            at = (ravager.mod_name(entry) - ravager.NAMES_GAME) * ravager.NAME_KEPT
            self.assertEqual(table[at:at + ravager.NAME_KEPT].split(b"\0")[0], name[:ravager.NAME_KEPT - 1], hex(entry))


class ObjectTests(unittest.TestCase):
    def test_picture_mapped(self):
        sl_palette = [(0, 0, 0)] * 256
        sl_palette[5], sl_palette[6] = (250, 0, 0), (0, 0, 250)
        stable = [(40, (255, 10, 10)), (41, (10, 10, 255))]
        out = icons.decode(ravitems.picture(icons.encode([[0, 5], [6, None]]), sl_palette, stable))
        self.assertEqual(out, [[0, 40], [41, None]])

    def test_item_records(self):
        recs, end = dataitems.records(ravitems.item_records(22427, 2000, b"t" * 15, 102, 258, 0))
        self.assertEqual([(r.level, r.of, r.kind, r.number, r.flags) for r in recs], [(1, 0, 1, 2000, 0), (3, 0, 4, 102, 5)])
        item = recs[0].data
        self.assertEqual((len(item), struct.unpack_from("<h", item, 0)[0], struct.unpack_from("<H", item, 0x0A)[0],
                          struct.unpack_from("<H", item, 0x14)[0], item[0x12:0x14]), (0x17, -22427, 102, 258, b"\x04\xff"))

    def test_make(self):
        pic = icons.encode([[1, 2]])
        sl_objects = {("OJFF", 2427): bytes(12) + struct.pack("<H", 900) + bytes(2), ("BMP ", 900): pic,
                      ("OJFF", 1095): bytes(12) + struct.pack("<H", 901) + bytes(2)}
        table = bytes(range(15)) * 102 + ravager.wotr_type(npcitems.TYPES[0])
        names_ = ravitems.Names(bytes(25 * 400), b"", [])
        pairs, chunks, failed = ravitems.make({2427: sl_item(2427, 115, npcitems.SHORT_SWORD), 1095: sl_item(1095, 60, 5)},
                                              sl_objects, {}, {}, names_, [(0, 0, 0)] * 256, [(1, (0, 0, 0))], table)
        self.assertEqual((pairs, failed), ({2427: 22427}, [(1095, "no picture")]))
        self.assertEqual(struct.unpack_from("<H", chunks[("OJFF", 22427)], 12)[0], 22427)
        recs, _ = dataitems.records(chunks[("RDFF", 22427)])
        self.assertEqual(recs[1].data, ravager.wotr_type(npcitems.TYPES[0]))


@unittest.skipUnless(WOTR and SL, "DSUN_WOTR and DSUN_SL: the player's two game folders")
class GameTests(unittest.TestCase):
    def test_trap_user_every_item(self):
        save = gff.read_gff(open(os.path.join(SAVES, "trap-user", "SAVE01.SAV"), "rb").read())
        with tempfile.TemporaryDirectory() as d:
            sequel, failed = rt.with_added(save, rt.load_sequel(WOTR), SL, WOTR, d)
            self.assertEqual(failed, [])
            _, moved = rt.roster(save, sequel)
            self.assertFalse([old for m in moved for old, new in m.items if new == rt.MONEY_BAG])
            again, _ = rt.with_added(save, rt.load_sequel(WOTR), SL, WOTR, d)  # (kept, not made again)
            self.assertEqual(again.counterparts, sequel.counterparts)
            copy, done = ravager.objects_fixed(open(os.path.join(WOTR, "OBJEX.GFF"), "rb").read(), frozenset(),
                                               ravager.read_added(d))
            self.assertEqual(done, ["mod_types", "object_types", "free_action_potion", "transfer_items", "weights", "melee_range", "materials",
                                    "item_shine", "figures",
                                    "wide_sheets"])  # (the monsters' sheets 48h too)
            chunks = gff.read_gff(copy)
            self.assertIn(("RDFF", 22427 if ("OJFF", 22427) in sequel.objects else 22419), chunks)
            types = chunks[ravager.TYPES_CHUNK]
            for key in ravager.read_added(d):  # (the added objects' copies of their types weighed as ALL 4)
                if key[0] == "RDFF":
                    for r in dataitems.records(chunks[key])[0]:
                        if r.kind == ravager.TYPE_KIND_RECORD and r.number < ravager.GAME_TYPES:
                            self.assertEqual(r.data, types[r.number * 15:(r.number + 1) * 15], key)


    def test_every_weapon_keeps_kind_and_material(self):
        """Every one of Shattered Lands' weapon objects (337 in the GOG release) becomes in the sequel a weapon
        of its kind and material, melee or missile as it is: ITEMS.BIN's counterpart where that is one
        (rt.weapon_pairs), else the Loader's object of such a type (ravitems.sequel_type) (the user's,
        2026-11-27: SSI's pairs made a bone Long Sword an obsidian one, a Polearm +1 a Double Spear)."""
        from dsloader import icons, itemtables
        sl_objects = gff.read_gff(open(os.path.join(SL, "SEGOBJEX.GFF"), "rb").read())
        sl_objects.update(icons.new_chunks(sl_objects))
        gpl = gff.read_gff(open(os.path.join(SL, "GPLDATA.GFF"), "rb").read())
        sl_table = itemtables.types_chunk(gpl[itemtables.TYPES_CHUNK])
        sequel = rt.load_sequel(WOTR)
        table = ravager.mod_types_table(ravager.materialled_table(sequel.objects[ravager.TYPES_CHUNK]))
        sequel = sequel._replace(counterparts=rt.weapon_pairs(sequel, sl_objects, sl_table, table))
        self.assertEqual(sequel.counterparts.get(2605), 675)  # (SL's Dragonsbane the sequel's own, metal now)
        types = ravitems.type_map(sequel.counterparts, sl_objects, sequel.objects)
        kinds, weapons = ravitems.sl_kinds(), 0
        for key in sorted(sl_objects):
            rec = ravitems._first_record(sl_objects, key[1]) if key[0] == "RDFF" else None
            if rec is None or struct.unpack_from("<H", rec, 0x0A)[0] not in kinds:
                continue
            weapons += 1
            sl_type = struct.unpack_from("<H", rec, 0x0A)[0]
            pair = ravitems._first_record(sequel.objects, sequel.counterparts.get(key[1], -1))
            wotr = struct.unpack_from("<H", pair, 0x0A)[0] if pair else ravitems.sequel_type(sl_type, types, sl_table, table)
            self.assertTrue(ravitems.same_weapon(sl_type, sl_table, wotr, table), (key[1], sl_type, wotr))
        self.assertGreater(weapons, 300)
        for sl_type in game.RAVAGER_TYPES:  # (the mod's Ravager weapons, which no SL object of the game has)
            wotr = ravitems.sequel_type(sl_type, types, sl_table, table)
            self.assertTrue(ravitems.same_weapon(sl_type, sl_table, wotr, table), (sl_type, wotr))


if __name__ == "__main__":
    unittest.main()
