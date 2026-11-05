"""The champions' bout (champions.py): their objects, their gear put in place, the arena's scripts."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import champions, dataitems, game, gff, gpl, kalzith, sprites  # noqa: E402


def item(kind: int, name: int = 0, plus: int = 0) -> bytes:
    rec = bytearray(game.ITEM_SIZE)
    struct.pack_into("<H", rec, game.ITEM_TYPE, kind)
    struct.pack_into("<H", rec, game.ITEM_NAME, name)
    rec[game.ITEM_PLUS] = plus
    rec[game.ITEM_SLOT] = 0xFF
    return bytes(rec)


def person(obj: int, name: bytes, ac: int = 5, items=()) -> bytes:
    """An object's record of a person (its creature record and sheet) with ITEMS."""
    head = bytearray(58)
    struct.pack_into("<h", head, dataitems.SELF, -obj)
    head[kalzith.RDFF_NAME - dataitems.HEADER.size:kalzith.RDFF_NAME - dataitems.HEADER.size + len(name)] = name
    sheet = bytearray(game.SHEET_SIZE)
    sheet[game.SHEET_BASE_AC] = ac
    recs = [dataitems.Record(1, 0, 2, 7, 71, bytes(head)), dataitems.Record(3, 0, 4, 7, 71, bytes(sheet))]
    rdff = dataitems.chunk(recs, b"\xff" + bytes(9))
    return dataitems.with_items(rdff, list(items))


def picture(width: int, height: int, colour: int) -> bytes:
    return sprites.encode_frames([[[colour] * width for _ in range(height)]])


def ojff(picture_id: int) -> bytes:
    out = bytearray(16)
    struct.pack_into("<H", out, kalzith.OJFF_PICTURE, picture_id)
    return bytes(out)


class ObjectTests(unittest.TestCase):
    def setUp(self):
        stock = [item(t) for t in (game.GYTHKA_TYPE, champions.SHIELD_TYPE, champions.SCALE_CHEST,
                                   champions.SCALE_ARM, champions.SCALE_LEGS, champions.SLING_TYPE,
                                   champions.LEATHER_CHEST, champions.BOW_TYPE, champions.ARROWS_TYPE,
                                   champions.LONG_SWORD_TYPE)]
        self.chunks = {("RDFF", 900): person(900, b"Merchant", items=stock)}
        for obj, base in champions.BASES.items():
            self.chunks[("RDFF", base)] = person(base, b"Kind %d" % base, items=[item(18)])
            self.chunks[("OJFF", base)] = ojff(base + 3000)
        self.chunks[("OJFF", champions.BASES[champions.TOHR_KREEN])] = ojff(2331)
        self.chunks[("BMP ", 2331)] = picture(10, 20, 7)
        self.chunks[("OJFF", champions.DEAD_BODY)] = ojff(495)
        self.chunks[("BMP ", 495)] = picture(12, 6, 40)
        recs = [dataitems.Record(1, 0, 1, 417, 71, item(0x6C, 0x69))]
        self.chunks[("RDFF", champions.DEAD_BODY)] = dataitems.chunk(recs, b"\xff" + bytes(9))

    def test_six_and_a_body(self):
        out = champions.object_chunks(self.chunks)
        for obj in champions.OBJECTS:
            with self.subTest(obj=obj):
                rdff = out[("RDFF", obj)]
                self.assertEqual(struct.unpack_from("<h", rdff, dataitems.HEADER.size + dataitems.SELF)[0], -obj)
                self.assertEqual(rdff[kalzith.RDFF_NAME:kalzith.RDFF_NAME + 9], b"Champion\0")
                kinds = [struct.unpack_from("<H", r, game.ITEM_TYPE)[0] for r in dataitems.items_of(rdff)]
                self.assertNotIn(18, kinds)  # (the kind's own gear left out)
                self.assertEqual(sorted(kinds), sorted(k for k, _ in champions.SLOTS[obj]))
                self.assertEqual(out[("OJFF", obj)], self.chunks[("OJFF", champions.BASES[obj])])
                sheet = next(r.data for r in dataitems.records(rdff)[0] if r.kind == champions.SHEET_RECORD)
                self.assertEqual(sheet[game.SHEET_BASE_AC], 5)  # (the kind's: armour counts on top)
        gythka, = dataitems.items_of(out[("RDFF", champions.TOHR_KREEN)])
        self.assertEqual((gythka[game.ITEM_PLUS], struct.unpack_from("<H", gythka, game.ITEM_NAME)[0]), (1, 0x148))
        self.assertEqual(struct.unpack_from("<H", out[("OJFF", champions.BODY)], kalzith.OJFF_PICTURE)[0], champions.BODY)
        self.assertIn(("BMP ", champions.BODY), out)
        body = out[("RDFF", champions.BODY)]
        self.assertEqual(struct.unpack_from("<h", body, dataitems.HEADER.size)[0], -champions.BODY)

    def test_numbers_taken(self):
        self.chunks[("OJFF", champions.ELF)] = b"x"
        with self.assertRaises(KeyError):
            champions.object_chunks(self.chunks)

    def test_gear_missing(self):
        del self.chunks[("RDFF", 900)]
        with self.assertRaises(KeyError):
            champions.object_chunks(self.chunks)


class GearTests(unittest.TestCase):
    """In the arena, a champion's gear moved from its backpack (where the game makes it) to its
    slots, once; the defiler given a scroll."""

    def setUp(self):
        import test_ring
        from dsloader import ring
        self.ring = ring
        self.log = test_ring.arena()
        self.m, self.gd = self.log.guest.mem, self.log.game
        struct.pack_into("<H", self.m, test_ring.DS * 16 + ring.REGION, champions.ARENA)
        self.creature = 5
        base = game.far_pointer(self.gd.guest, self.gd.ds, game.CREATURES_PTR) + self.creature * game.CREATURE_SIZE
        self.base = base

    def make(self, obj, kinds):
        """Creature 5 a champion OBJ, alive, with KINDS in its backpack (thing 300, items 10 on)."""
        import test_ring
        m, base = self.m, self.base
        for kind in (game.BONE_AXE_TYPE, game.BONE_DAGGER_TYPE):  # (weapons: their types say so)
            m[test_ring.ITEM_TYPES + kind * game.ITEM_TYPE_SIZE] = 1
        struct.pack_into("<h", m, base, 30)
        m[base + game.CREATURE_STATUS] = game.STATUS_OKAY
        m[base + game.CREATURE_NAME:base + game.CREATURE_NAME + 9] = b"Champion\0"
        struct.pack_into("<h", m, base + champions.CREATURE_OBJECT, -obj)
        struct.pack_into("<HHH", m, base + 8, game.NO_ITEM, game.NO_ITEM, 300)
        struct.pack_into("<Bh", m, test_ring.THINGS + 300 * 3, game.THING_ITEM, 10)
        for i, kind in enumerate(kinds):
            rec = bytearray(item(kind))
            struct.pack_into("<h", rec, game.ITEM_NEXT, 10 + i + 1 if i + 1 < len(kinds) else game.NO_ITEM)
            rec[game.ITEM_SLOT] = 14 + i
            at = test_ring.ITEMS + (10 + i) * game.ITEM_SIZE
            m[at:at + game.ITEM_SIZE] = rec

    def lists(self):
        rec = self.gd.creature(self.creature)
        it = self.ring.Items(self.gd)
        return [sorted((struct.unpack_from("<H", d, game.ITEM_TYPE)[0], d[game.ITEM_SLOT])
                       for _, d in it.chain(struct.unpack_from("<h", rec, o)[0], inside=False))
                for o in game.CREATURE_ITEM_LISTS]

    def test_mul_armed_and_armoured(self):
        kinds = [game.BONE_AXE_TYPE, game.BONE_AXE_TYPE, champions.SCALE_CHEST, champions.SCALE_ARM]
        self.make(champions.MUL, kinds)
        gear = champions.Gear()
        gear.watch(self.gd)
        worn, held, pack = self.lists()
        self.assertEqual(worn, sorted([(champions.SCALE_CHEST, champions.CHEST), (champions.SCALE_ARM, champions.ARM)]))
        self.assertEqual(held, sorted([(game.BONE_AXE_TYPE, champions.RIGHT), (game.BONE_AXE_TYPE, champions.LEFT)]))
        self.assertEqual(pack, [])
        gear.watch(self.gd)  # (once)
        self.assertEqual(self.lists()[1], held)

    def test_not_a_champion(self):
        self.make(champions.MUL, [game.BONE_AXE_TYPE])
        struct.pack_into("<h", self.m, self.base + champions.CREATURE_OBJECT, -290)
        champions.Gear().watch(self.gd)
        self.assertEqual(self.lists()[2], [(game.BONE_AXE_TYPE, 14)])

    def test_elsewhere(self):
        import test_ring
        self.make(champions.MUL, [game.BONE_AXE_TYPE])
        struct.pack_into("<H", self.m, test_ring.DS * 16 + self.ring.REGION, 0x29)
        champions.Gear().watch(self.gd)
        self.assertEqual(self.lists()[2], [(game.BONE_AXE_TYPE, 14)])

    def test_defiler_scroll(self):
        from dsloader import defilerscrolls
        self.make(champions.DEFILER, [game.BONE_DAGGER_TYPE])
        self.gd.spell_level = lambda spell: 2
        chosen = []
        champions.Gear().watch(self.gd, True, lambda pool: chosen.append(list(pool)) or pool[1])
        self.assertEqual(chosen, [list(champions.SCROLL_SPELLS)])
        it = self.ring.Items(self.gd)
        rec = self.gd.creature(self.creature)
        scrolls = [d for o in game.CREATURE_ITEM_LISTS for _, d in it.chain(struct.unpack_from("<h", rec, o)[0])
                   if defilerscrolls.is_ours(d)]
        self.assertEqual(len(scrolls), 1)
        self.assertEqual(self.lists()[1], [(game.BONE_DAGGER_TYPE, champions.RIGHT)])


GPLDATA = os.environ.get("DSUN_GPLDATA")


@unittest.skipUnless(GPLDATA, "DSUN_GPLDATA (the game's GPLDATA.GFF) not given")
class ScriptTests(unittest.TestCase):
    """On the game's own scripts: the arena's bout and the king's flag."""

    def setUp(self):
        with open(GPLDATA, "rb") as f:
            self.scripts, self.types = gpl.load_scripts(f.read())

    def test_bout(self):
        was = self.scripts[("GPL ", champions.ARENA_SCRIPT)]
        new = champions.with_bout(was, self.types)
        ops = {o.at: o for o in gpl.decode(new, self.types)}  # (it all decodes)
        self.assertEqual(ops[champions.INTRO_AT].code, champions.GOTO)
        call = ops[champions.WAVE_CALL]
        self.assertEqual(call.code, champions.CALL)
        added = [o for at, o in sorted(ops.items()) if at >= len(was)]
        made = [o.args[0][1].args[0] for o in added if o.code == champions.SET and o.args[0][0] == "op"]
        self.assertEqual(made, [("n", -obj) for obj in champions.OBJECTS])
        self.assertIn(("n", champions.RANDOM_WAVES), [o.args[0] for o in added if o.code == champions.CALL])
        self.assertEqual(champions.with_bout(b"\x31", self.types), b"\x31")  # (not the arena's: unchanged)

    def test_king(self):
        was = self.scripts[("GPL ", champions.DEATHS_SCRIPT)]
        new = champions.with_king(was, self.types)
        ops = [o for o in gpl.decode(new, self.types) if o.at >= len(was)]
        self.assertEqual([o.args for o in ops[:2]], [[("n", 1), ("var", 13, 19)], [("n", 1), ("var", 13, champions.KING)]])
        self.assertEqual(ops[2].code, champions.GOTO)
