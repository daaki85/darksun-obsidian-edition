import struct
import unittest
from unittest import mock

from dsloader import game, names, spellarrows, weaponchoice


class FakeGame:
    """The bits of GameData SpellArrows asks for: party member 0 a 4th-level Spellarcher."""
    def __init__(self):
        self.slots = {1: 2, 3: 0}
        self.written = []
        self.guest = mock.Mock()
        self.guest.write = lambda at, data: self.written.append((at, data))
        self.guest.read = lambda at, size: bytes((self.slots.get((at - 0x10000 - game.SLOTS_LEFT["Wizard"]) % 0x1E, 0),))
        self.ds = 0x1000

    def class_level(self, member, cls):
        return 4 if cls == game.PRESERVER else 5

    def creature_name(self, member):
        return "Daaki"

    def no_spells(self, member):  # (in armour: ARMOURED)
        return getattr(self, "armoured", False)

    def _worn(self, member):  # (what's in the quiver: QUIVER, or nothing; and the pack: PACK)
        if getattr(self, "quiver", None) is not None:  # (True: plain arrows; else the arrow's name, a count)
            rec = bytearray(game.ITEM_SIZE)
            rec[game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
            if self.quiver is not True:
                struct.pack_into("<H", rec, game.ITEM_NAME, self.quiver[0])
                struct.pack_into("<H", rec, weaponchoice.ITEM_COUNT, self.quiver[1])
            else:
                struct.pack_into("<H", rec, game.ITEM_NAME, 0x36)
            yield 9, bytes(rec), b""
        for index, (name, count) in getattr(self, "pack", {}).items():  # (item number: the arrow's name, a count)
            rec = bytearray(game.ITEM_SIZE)
            rec[game.ITEM_SLOT] = 20
            struct.pack_into("<H", rec, game.ITEM_NAME, name)
            struct.pack_into("<H", rec, weaponchoice.ITEM_COUNT, count)
            yield index, bytes(rec), b""


class CastSoundTests(unittest.TestCase):
    def test_cast_sound_is_the_spells_own(self):
        gd = mock.Mock()
        gd.spell_record = lambda spell: bytes(range(32)) if spell == spellarrows.ARROWS[1].spell else b""
        self.assertEqual(spellarrows.cast_sound(gd, 1), spellarrows.CAST_SOUND)  # (byte 0Fh of the record)
        self.assertEqual(spellarrows.cast_sound(gd, 0), 0)  # (no record: none)
        self.assertEqual(spellarrows.cast_sound(gd, 9), 0)  # (no such arrows)


class SpellArrowsTests(unittest.TestCase):
    def test_arrows_item(self):
        """A stack of the game's Arrows (type 62) with the spell's name and picture, worth nothing."""
        rec = spellarrows.arrows_item(spellarrows.ARROWS[1], 20)
        self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_TYPE)[0], 62)
        self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_NAME)[0], 0x16D)
        self.assertEqual(struct.unpack_from("<HH", rec, 0), (0x10000 - 2616, 20))
        self.assertEqual(struct.unpack_from("<H", rec, weaponchoice.ITEM_VALUE)[0], 0)
        self.assertTrue(spellarrows.is_arrow(rec))
        self.assertFalse(spellarrows.is_arrow(weaponchoice.arrows(spellarrows.TEMPLATE)))

    def test_names(self):
        """The four names, 15 letters at most, after the amulet's in DSCLOG's table."""
        self.assertEqual([names.NAMES[a.name] for a in spellarrows.ARROWS],
                         [b"Burning Arrows", b"Chill Arrows", b"Shocking Arrows", b"Vampiric Arrows"])
        self.assertTrue(all(len(n) <= 15 for n in spellarrows.NAMES.values()))
        self.assertEqual(max(names.NAMES), names.OWN + names.EXTRA - 1)

    def patched(self, add_to=True):
        return (mock.patch.object(spellarrows, "is_spellarcher", lambda gd, m: m == 0),
                mock.patch.object(spellarrows, "knows", lambda gd, m, s: s in {1, 3, 10, 39}),
                mock.patch.object(spellarrows, "item_address", lambda gd, index: 0x50000 + index * game.ITEM_SIZE),
                mock.patch.object(spellarrows.weaponchoice, "bow_ahead"),
                mock.patch.object(spellarrows.npcitems, "add_to", return_value=add_to))

    def count_written(self, gd, index, n):
        return (0x50000 + index * game.ITEM_SIZE + weaponchoice.ITEM_COUNT, struct.pack("<H", n)) in gd.written

    def test_make(self):
        """A Spellarcher's button, its quiver empty: a slot of the spell's level used for one arrow,
        a new stack of it in the quiver (the bow put ahead of it); none for a spell it doesn't know,
        without a slot, or for one not a Spellarcher."""
        gd = FakeGame()
        arrows = spellarrows.SpellArrows()
        a, b, c, ahead, add = self.patched()
        with a, b, c, ahead as ahead, add as add:
            done = arrows.make(gd, 0, 1)
            self.assertEqual(done.text, "")  # (no window)
            self.assertIn("makes one of the chill arrows in the quiver (1 of 24 now)", done.log[0])
            self.assertIn("lasts until shot", done.log[0])
            rec = add.call_args[0][2]
            self.assertEqual(struct.unpack_from("<HH", rec, 0)[1], spellarrows.ARROWS_A_SLOT)
            self.assertEqual(add.call_args[0][3], weaponchoice.AMMO_SLOT)  # (in the quiver)
            ahead.assert_called_with(gd, 0)
            self.assertEqual(gd.written[-1][1], bytes((1,)))  # (a 1st-level slot used: 2 to 1)
            self.assertIn("no 3rd-level spell left", arrows.make(gd, 0, 3).text)
            self.assertIn("can't weave", arrows.make(gd, 1, 1).text)  # (not a Spellarcher)
            self.assertEqual(add.call_count, 1)

    def test_make_onto_the_stack(self):
        """The spell's own stack, in the quiver or the pack: one more on it, a slot used; at
        STACK_MOST none, the slot kept."""
        for where in ("quiver", "pack"):
            gd = FakeGame()
            chill = spellarrows.ARROWS[1]
            if where == "quiver":
                gd.quiver, index = (chill.name, 7), 9
            else:
                gd.quiver, gd.pack, index = True, {30: (chill.name, 7)}, 30
            arrows = spellarrows.SpellArrows()
            a, b, c, ahead, add = self.patched()
            with self.subTest(where=where), a, b, c, ahead, add as add:
                done = arrows.make(gd, 0, 1)
                self.assertEqual(done.text, "")
                self.assertIn("makes one of the chill arrows (8 of 24 now)", done.log[0])
                self.assertTrue(self.count_written(gd, index, 8))
                self.assertEqual(gd.written[-1][1], bytes((1,)))  # (a 1st-level slot used)
                self.assertEqual(add.call_count, 0)
                gd.written.clear()
                if where == "quiver":
                    gd.quiver = (chill.name, spellarrows.STACK_MOST)
                else:
                    gd.pack = {30: (chill.name, spellarrows.STACK_MOST)}
                self.assertIn("chill arrows are a full stack (24)", arrows.make(gd, 0, 1).text)
                self.assertEqual(gd.written, [])

    def test_make_into_the_pack(self):
        """No stack of the spell's and something else in the quiver (other arrows, another spell's):
        a new stack in the pack, the quiver as it is."""
        for quiver in (True, (spellarrows.ARROWS[1].name, 5)):
            gd = FakeGame()
            gd.quiver = quiver
            arrows = spellarrows.SpellArrows()
            a, b, c, ahead, add = self.patched()
            with self.subTest(quiver=quiver), a, b, c, ahead as ahead, add as add:
                done = arrows.make(gd, 0, 2)  # (Shocking Grasp)
                self.assertIn("makes one of the shocking arrows in the pack (1 of 24 now)", done.log[0])
                self.assertIsNone(add.call_args[0][3])  # (a backpack cell)
                ahead.assert_not_called()

    def test_burning_hands_retired(self):
        """Burning Hands is a cone, not a touch: no arrows of it, whatever is asked (DSCLOG never offers it)."""
        gd = FakeGame()
        a, b, c, ahead, add = self.patched()
        with a, b, c, ahead, add as add:
            self.assertIn("can't weave Burning Hands", spellarrows.SpellArrows().make(gd, 0, 0).text)
            add.assert_not_called()
        self.assertEqual(gd.written, [])

    def test_make_in_armour(self):
        """In armour a Spellarcher casts nothing (restrict.no_spells), so it weaves no arrows: the
        slot kept."""
        gd = FakeGame()
        gd.armoured = True
        arrows = spellarrows.SpellArrows()
        with mock.patch.object(spellarrows, "is_spellarcher", return_value=True), \
                mock.patch.object(spellarrows, "knows", return_value=True), \
                mock.patch.object(spellarrows.npcitems, "add_to", return_value=True) as add:
            done = arrows.make(gd, 0, 1)
        self.assertIn("in armour", done.text)
        self.assertEqual(add.call_count, 0)
        self.assertEqual(gd.written, [])


if __name__ == "__main__":
    unittest.main()


class StrayTests(unittest.TestCase):
    """return_strays: spell arrows another party member carries go back to the Spellarcher."""

    def gd(self, items, combat=False, inventory=False):
        """ITEMS: member -> {item number: (name, count, slot)}."""
        gd = mock.Mock()
        gd.items = {m: dict(v) for m, v in items.items()}

        def worn(m):
            for index, (name, count, slot) in gd.items.get(m, {}).items():
                rec = bytearray(game.ITEM_SIZE)
                rec[game.ITEM_SLOT] = slot
                struct.pack_into("<H", rec, game.ITEM_NAME, name)
                struct.pack_into("<H", rec, weaponchoice.ITEM_COUNT, count)
                yield index, bytes(rec), b""
        gd._worn = lambda m: list(worn(m))
        gd.creature = lambda m: bytes(game.CREATURE_SIZE)
        gd.creature_name = lambda m: ("Lex", "Jenna", "Ester", "Seneca")[m]
        gd.in_combat = lambda: combat
        gd.inventory = inventory
        return gd

    def run_it(self, gd):
        written, added, removed = [], [], []
        with mock.patch.object(spellarrows, "is_spellarcher", lambda gd_, m: m == 0), \
                mock.patch.object(spellarrows, "inventory_up", lambda gd_: gd.inventory), \
                mock.patch.object(spellarrows, "item_address", lambda gd_, i: i * 100), \
                mock.patch.object(spellarrows.ring, "Items", lambda gd_: None), \
                mock.patch.object(spellarrows.ring, "unlink", lambda gd_, it, i, what, empty=False: removed.append(i) or True), \
                mock.patch.object(spellarrows.npcitems, "add_to", lambda gd_, m, rec, slot=None: added.append(m) or True):
            gd.guest.write = lambda at, data: written.append((at // 100, struct.unpack("<H", data)[0]))
            lines = spellarrows.return_strays(gd)
        return lines, written, added, removed

    def test_onto_the_stack(self):
        shock, chill = spellarrows.ARROWS[2].name, spellarrows.ARROWS[1].name
        gd = self.gd({0: {5: (shock, 10, 1)}, 1: {30: (shock, 7, 20), 31: (0x36, 40, 1)}, 2: {40: (chill, 3, 21)}})
        lines, written, added, removed = self.run_it(gd)
        self.assertEqual(written, [(5, 17)])  # (Jenna's 7 onto Lex's 10)
        self.assertEqual(added, [0])  # (Ester's chill arrows: Lex has none, a stack of their own)
        self.assertEqual(sorted(removed), [30, 40])  # (plain arrows stay with Jenna)
        self.assertEqual(lines[0], "The shocking arrows go back to Lex from Jenna: only a Spellarcher carries them (7)")

    def test_over_a_stack(self):
        """Two that would come to more than STACK_MOST: the stray stack into the pack as it is."""
        shock = spellarrows.ARROWS[2].name
        gd = self.gd({0: {5: (shock, 20, 1)}, 1: {30: (shock, 7, 20)}})
        lines, written, added, removed = self.run_it(gd)
        self.assertEqual((written, added, removed), ([], [0], [30]))

    def test_left_be(self):
        """Nothing in a fight, with the inventory up, or with no Spellarcher in the party."""
        shock = spellarrows.ARROWS[2].name
        for kw in (dict(combat=True), dict(inventory=True)):
            with self.subTest(**kw):
                self.assertEqual(self.run_it(self.gd({0: {}, 1: {30: (shock, 7, 20)}}, **kw)), ([], [], [], []))
        gd = self.gd({1: {30: (shock, 7, 20)}})
        with mock.patch.object(spellarrows, "is_spellarcher", lambda gd_, m: False), \
                mock.patch.object(spellarrows, "inventory_up", lambda gd_: False):
            self.assertEqual(spellarrows.return_strays(gd), [])

    def test_out_of_the_quiver(self):
        """With no Spellarcher in the party, spell arrows another member has readied (the ammunition
        slot) go into a backpack cell of its own; those in its pack, and plain arrows, stay."""
        shock, chill = spellarrows.ARROWS[2].name, spellarrows.ARROWS[1].name
        gd = self.gd({1: {30: (shock, 7, weaponchoice.AMMO_SLOT), 31: (chill, 3, 20)},
                      2: {40: (0x36, 9, weaponchoice.AMMO_SLOT)}})
        placed = []
        with mock.patch.object(spellarrows, "is_spellarcher", lambda gd_, m: False), \
                mock.patch.object(spellarrows, "inventory_up", lambda gd_: False), \
                mock.patch.object(spellarrows.ring, "Items", lambda gd_: None), \
                mock.patch.object(spellarrows.pickpocket, "free_cell", lambda gd_, it, m: 22), \
                mock.patch.object(spellarrows.pickpocket, "place",
                                  lambda gd_, m, i, cell: placed.append((m, i, cell)) or True):
            lines = spellarrows.return_strays(gd)
        self.assertEqual(placed, [(1, 30, 22)])
        self.assertEqual(lines, ["Jenna's shocking arrows are put away in the backpack: only a Spellarcher "
                                 "readies them (7)"])
        with mock.patch.object(spellarrows, "is_spellarcher", lambda gd_, m: False), \
                mock.patch.object(spellarrows, "inventory_up", lambda gd_: False), \
                mock.patch.object(spellarrows.ring, "Items", lambda gd_: None), \
                mock.patch.object(spellarrows.pickpocket, "free_cell", lambda gd_, it, m: None):
            self.assertEqual(spellarrows.return_strays(gd), [])  # (a full pack: left as they are)


class StartingGearTests(unittest.TestCase):
    """A new Spellarcher's Fine Bow and arrows by the touch spells it picked (starting_gear)."""
    BOW_TYPE = 1  # (the game's Bow: specialize's bow kind)

    def run_it(self, known, items):
        """(the items after, the log) for a Spellarcher knowing KNOWN, with ITEMS (index: record)."""
        gd = mock.Mock()
        gd.creature_name = lambda m: "Daaki"
        gd._worn = lambda m: [(i, bytes(rec), b"") for i, rec in sorted(items.items())]
        gd.guest.write = lambda at, data: items[(at - 0x50000) // game.ITEM_SIZE].__setitem__(
            slice((at - 0x50000) % game.ITEM_SIZE, (at - 0x50000) % game.ITEM_SIZE + len(data)), data)

        def add_to(gd_, m, rec, slot=None):
            new = bytearray(rec)
            new[game.ITEM_SLOT] = slot if slot is not None else 20
            items[max(items, default=0) + 1] = new
            return True

        def unlink(gd_, it, index, why, empty=False):
            del items[index]
            return True
        bow = bytearray(game.ITEM_SIZE)
        struct.pack_into("<H", bow, game.ITEM_TYPE, self.BOW_TYPE)
        with mock.patch.object(game, "far_pointer", return_value=0x50000), \
                mock.patch.object(spellarrows, "knows", lambda gd_, m, s: s in known), \
                mock.patch.object(spellarrows.npcitems, "add_to", add_to), \
                mock.patch("dsloader.ring.unlink", unlink), mock.patch("dsloader.ring.Items"), \
                mock.patch("dsloader.startgear._weapon", return_value=(bytes(bow), None)), \
                mock.patch.object(weaponchoice, "bow_ahead"):
            log = spellarrows.starting_gear(gd, 0, b"", None)
        return items, log

    def stacks(self, items):
        return sorted((struct.unpack_from("<H", r, game.ITEM_NAME)[0], struct.unpack_from("<H", r, 2)[0],
                       r[game.ITEM_SLOT]) for r in items.values())

    def test_by_the_picks(self):
        chill, shock = spellarrows.ARROWS[1].name, spellarrows.ARROWS[2].name
        fine, quiver, missile = game.FINE_BOW_NAME, weaponchoice.AMMO_SLOT, weaponchoice.MISSILE_SLOT
        for known, want in (({10}, [(shock, 24, quiver)]), ({3}, [(chill, 24, quiver)]),
                            ({3, 10}, [(chill, 24, quiver), (shock, 24, 20)]),
                            ({1}, [(0x36, 24, quiver)]), (set(), [(0x36, 24, quiver)])):
            with self.subTest(known=known):
                items, log = self.run_it(known, {})
                self.assertEqual([s for s in self.stacks(items) if s[0] != fine], sorted(want))
                self.assertEqual([s[2] for s in self.stacks(items) if s[0] == fine], [missile])
                self.assertIn("Fine Bow", log[0])
                self.assertEqual(self.run_it(known, items)[1], [])  # (once: it has its Fine Bow)

    def test_the_weapon_rules_bow(self):
        """The bow and arrows the weapon rules gave (a bow chosen): the bow made the Fine Bow, the plain
        arrows gone for the spell's, or made STARTING."""
        for known in ({10}, set()):
            bow, arrows = bytearray(game.ITEM_SIZE), bytearray(weaponchoice.arrows(spellarrows.TEMPLATE))
            struct.pack_into("<H", bow, game.ITEM_TYPE, self.BOW_TYPE)
            bow[game.ITEM_SLOT], arrows[game.ITEM_SLOT] = weaponchoice.MISSILE_SLOT, weaponchoice.AMMO_SLOT
            with self.subTest(known=known):
                items, _ = self.run_it(known, {1: bow, 2: arrows})
                self.assertEqual(struct.unpack_from("<H", items[1], game.ITEM_NAME)[0], game.FINE_BOW_NAME)
                name = spellarrows.ARROWS[2].name if known else 0x36
                self.assertEqual([s for s in self.stacks(items) if s[0] != game.FINE_BOW_NAME],
                                 [(name, 24, weaponchoice.AMMO_SLOT)])
