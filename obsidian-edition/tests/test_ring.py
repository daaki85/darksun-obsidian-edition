"""The Ring +1: found on the Tied-up Prisoner's body in the arena, named, and counted on saving throws."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, pickpocket, ring
from test_dicelog import CREATURES, DS, ITEM_TYPES, ITEMS, LOAD_SEG, NAMES, make_game

THINGS = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
def arena():
    """The arena, the ring still to be found; item 60 first on the free item list, object 505
    first on the free object list; Dag (creature 0) leads."""
    log = make_game()
    m = log.guest.mem
    struct.pack_into("<H", m, DS * 16 + ring.REGION, ring.ARENA)
    struct.pack_into("<HH", m, DS * 16 + ring.FREE_ITEMS, 60, 0)
    struct.pack_into("<h", m, ITEMS + 60 * game.ITEM_SIZE + game.ITEM_NEXT, 61)
    struct.pack_into("<H", m, DS * 16 + ring.FREE_THINGS, 505)
    struct.pack_into("<Bh", m, THINGS + 505 * 3, 0, 504)
    struct.pack_into("<H", m, DS * 16 + ring.THINGS_USED, 15)
    struct.pack_into("<H", m, DS * 16 + game.WHOSE_TURN, 0)
    # (the fake's creatures' lists: none)
    for index in range(8):
        struct.pack_into("<hhh", m, CREATURES + index * game.CREATURE_SIZE + 8, *(game.NO_ITEM,) * 3)
    return log


def word(m, addr):
    return struct.unpack_from("<H", m, addr)[0]


class SearchTests(unittest.TestCase):
    def test_found_on_the_body(self):
        """Looked for on the body: into the leader's backpack (its first cell), and then no
        more is needed."""
        log = arena()
        m = log.guest.mem
        self.assertTrue(ring.ring_needed(log.game))
        self.assertEqual(ring.give_ring(log.game), ring.MESSAGE.format(who=log.game.creature_name(0)))
        thing, = struct.unpack_from("<h", m, CREATURES + pickpocket.PACK_LIST)  # (the backpack's list)
        self.assertEqual(struct.unpack_from("<Bh", m, THINGS + thing * 3), (game.THING_ITEM, 60))
        rec = bytearray(ring.RING)
        rec[game.ITEM_SLOT] = 14
        struct.pack_into("<H", rec, game.ITEM_NEXT, game.NO_ITEM)
        self.assertEqual(bytes(m[ITEMS + 60 * game.ITEM_SIZE:ITEMS + 61 * game.ITEM_SIZE]), bytes(rec))
        self.assertFalse(ring.ring_needed(log.game))

    def test_its_own_icon_at_once(self):
        """With the game's copy of the objects open, the ring is given with its own icon (the
        fire-coloured one) and an empty picture cache, not the plain ring's until a later pass
        (the inventory drew the plain one and kept it until the ring was clicked); without the
        copy, the plain one."""
        from dsloader import icons
        for open_, want in ((True, icons.picture("Ring of Protection +1", True)), (False, ring.RING_PICTURE)):
            with self.subTest(copy_open=open_):
                log = arena()
                icons.COPY_OPEN = open_
                try:
                    ring.give_ring(log.game)
                finally:
                    icons.COPY_OPEN = False
                self.assertEqual(word(log.guest.mem, ITEMS + 60 * game.ITEM_SIZE), want)

    def test_no_list_keeps_the_record_free(self):
        """No backpack list to be had (no free object to make one): no ring given, and the item
        record stays first on the free list, not taken and lost."""
        log = arena()
        m = log.guest.mem
        struct.pack_into("<H", m, DS * 16 + ring.FREE_THINGS, ring.THING_COUNT)  # (no free object)
        self.assertIsNone(ring.give_ring(log.game))
        self.assertEqual(word(m, DS * 16 + ring.FREE_ITEMS), 60)
        self.assertEqual(struct.unpack_from("<h", m, ITEMS + 60 * game.ITEM_SIZE + game.ITEM_NEXT)[0], 61)

    def test_party_has_it(self):
        """Dag carries a Ring +1 already (his list starting at object 401)."""
        log = arena()
        m = log.guest.mem
        struct.pack_into("<Bh", m, THINGS + 401 * 3, game.THING_ITEM, 70)
        struct.pack_into("<h", m, CREATURES + 8, 401)
        m[ITEMS + 70 * game.ITEM_SIZE:ITEMS + 71 * game.ITEM_SIZE] = ring.RING
        self.assertFalse(ring.ring_needed(log.game))

    def test_elsewhere(self):
        log = arena()
        struct.pack_into("<H", log.guest.mem, DS * 16 + ring.REGION, 0x2B)
        self.assertFalse(ring.ring_needed(log.game))


class NameTests(unittest.TestCase):
    def test_rule_names(self):
        """Helms and boots by the game's own names, the rule on or off (the item box shows a helm's
        AC as AC BONUS), and an earlier version's "Helm (AC 1)" and "Boots (Speed+1)" put back."""
        log = arena()
        m = log.guest.mem
        for entry, text in ((6, b"Helm (AC 1)"), (43, b"Boots (Speed+1)")):
            m[NAMES + 3 + entry * game.ITEM_NAME_SIZE:NAMES + 3 + entry * game.ITEM_NAME_SIZE + len(text)] = text
        ring.name_items(log.game, game.RULE_HELMS)
        self.assertEqual((log.game.item_name(6), log.game.item_name(43)), ("Helm", "Boots"))
        ring.name_items(log.game, 0)
        self.assertEqual((log.game.item_name(6), log.game.item_name(43)), ("Helm", "Boots"))

    def test_old_boots_name(self):
        """Boots earlier versions named for their movement ("Boots (+1 Move)", "Boots (Speed+1)")
        get the game's own name back."""
        log = arena()
        m = log.guest.mem
        at = NAMES + 3 + 43 * game.ITEM_NAME_SIZE
        for old in (b"Boots (+1 Move)", b"Boots (Speed+1)"):
            m[at:at + 15] = old
            ring.name_items(log.game, game.RULE_HELMS)
            self.assertEqual(log.game.item_name(43), "Boots")

    def test_rule_names_fit_the_look_box(self):
        """Names the rule would make longer than 15 letters stay the game's own (and one an
        earlier version made that long goes back)."""
        log = arena()
        m = log.guest.mem
        for entry, text in ((236, b"Helm of Might (AC 1)"), (286, b"Serpent Boots")):
            at = NAMES + 3 + entry * game.ITEM_NAME_SIZE
            m[at:at + game.ITEM_NAME_SIZE] = text.ljust(game.ITEM_NAME_SIZE, b"\0")
        ring.name_items(log.game, game.RULE_HELMS)
        self.assertEqual((log.game.item_name(236), log.game.item_name(286)), ("Helm of Might", "Serpent Boots"))


class WornTests(unittest.TestCase):
    def setUp(self):
        """Dag wears the Ring +1 (item 70, from object 401)."""
        self.log = arena()
        m = self.log.guest.mem
        struct.pack_into("<Bh", m, THINGS + 401 * 3, game.THING_ITEM, 70)
        struct.pack_into("<h", m, CREATURES + 0x0C, 401)
        m[ITEMS + 70 * game.ITEM_SIZE:ITEMS + 71 * game.ITEM_SIZE] = ring.RING
        m[ITEMS + 70 * game.ITEM_SIZE + game.ITEM_SLOT] = game.FINGER
        m[ITEM_TYPES + game.RING_TYPE * game.ITEM_TYPE_SIZE + 0x08] = game.NO_MATERIAL

    def test_named(self):
        self.assertEqual(self.log.game.equipment(0), [("finger", "Ring/Protection +1")])

    def test_saves(self):
        self.assertEqual(self.log.game.ring_plus(0), 1)
        self.assertIn((1, "Ring of Protection"), self.log.game.save_modifiers(0, 0x29, 27, 3))

    def test_carried_only(self):
        self.log.guest.mem[ITEMS + 70 * game.ITEM_SIZE + game.ITEM_SLOT] = 0xFF
        self.assertEqual(self.log.game.ring_plus(0), 0)

    def test_either_hand(self):
        """The inventory screen has a ring on each hand: slots 4 and 11."""
        self.log.guest.mem[ITEMS + 70 * game.ITEM_SIZE + game.ITEM_SLOT] = 11
        self.assertEqual(self.log.game.ring_plus(0), 1)


if __name__ == "__main__":
    unittest.main()


class XpTests(unittest.TestCase):
    def _body(self) -> bytes:
        """A script laid out as the arena's (script 5): the body's routine at BODY_AT - 1 (clear,
        the line, the click, clear, the end)."""
        from dsloader import gpl
        pad_to = ring.BODY_AT - 1
        sets, ends = divmod(pad_to, 5)
        pad = gpl.encode([(0x16, [("n", 0), ("var", 14, 1)])] * sets + [(0x31, [])] * ends)
        self.assertEqual(len(pad), pad_to)
        return pad + gpl.encode([(0x2A, []), (ring.PRINT, [("n", 98), ("str", ring.NOTHING + " ")]),
                                 (ring.PRINT, [("n", 98), ("var", 134, 2)]),
                                 (ring.PRINT, [("n", 98), ("var", 134, 3)]), (0x31, []), (0x31, [])])

    def test_with_xp(self):
        """The line becomes a jump to the line, the click and the clearing, then, the first time
        (XP_GIVEN), 50 XP by the game's routine for one person, and back to the routine's end; nothing of the
        game's moves; once only; from the game's script when another change made it undecodable."""
        from dsloader import gpl
        script = self._body()
        out = ring.with_xp(script)
        self.assertEqual(out[:ring.BODY_AT], script[:ring.BODY_AT])
        self.assertEqual(out[ring.BODY_AT + 3:len(script)], script[ring.BODY_AT + 3:])
        r = gpl._Reader(out, b"")
        r.i = ring.BODY_AT
        jump = gpl._op(r)
        self.assertEqual((jump.code, jump.args), (ring.GOTO, [("n", len(script))]))
        added = [(o.code, o.args) for o in gpl.decode(out[len(script):], b"")]
        self.assertEqual(added[0], (ring.PRINT, [("n", 98), ("str", ring.NOTHING + " ")]))
        self.assertEqual([c for c, _ in added[1:3]], [ring.PRINT, ring.PRINT])
        self.assertEqual(added[3], (0x18, [("expr", ["(", ("var", 0x8D, ring.XP_GIVEN), "==", ("n", 0), ")"])]))
        self.assertIn((0x16, [("n", 1), ("var", 13, ring.XP_GIVEN)]), added)
        self.assertIn((0x16, [("n", ring.XP_REWARD), ring.XP_AMOUNT]), added)
        self.assertIn((ring.CALL, list(ring.XP_ROUTINE)), added)
        end = len(gpl.encode([(0x2A, []), (ring.PRINT, [("n", 98), ("str", ring.NOTHING + " ")]),
                              (ring.PRINT, [("n", 98), ("var", 134, 2)]), (ring.PRINT, [("n", 98), ("var", 134, 3)])]))
        self.assertEqual(added[-1], (ring.GOTO, [("n", ring.BODY_AT - 1 + end)]))
        self.assertEqual(ring.with_xp(out, b"", script), out)
        other = script[:ring.BODY_AT] + gpl.encode([(0x31, [])] * 45)
        self.assertEqual(ring.with_xp(other), other)


class FlagsTests(unittest.TestCase):
    def test_numbers(self):
        """A global number: a word at the numbers' far pointer; None while the pointer is null."""
        log = arena()
        m = log.guest.mem
        struct.pack_into("<HH", m, DS * 16 + game.NUMBERS_PTR, 4, 0x6000)
        struct.pack_into("<h", m, 0x60004 + game.ARENA_FIGHTS * 2, 7)
        self.assertEqual(log.game.number(game.ARENA_FIGHTS), 7)
        struct.pack_into("<I", m, DS * 16 + game.NUMBERS_PTR, 0)
        self.assertIsNone(log.game.number(game.ARENA_FIGHTS))

    def test_arena_count_remembered_for_the_header(self):
        """Between fights in the arena, the panel's header gets the count last read: the numbers
        are in memory only now and then, and before any read it is not shown (the time instead)."""
        log = arena()
        m = log.guest.mem
        seen = []

        class Panel:
            open, first, level, font = True, None, None, None

            def update(self, *args):
                seen.append(args[-2:])

        log.combat_log, log._panel, log._font_tried = True, Panel(), True
        log.tsr_hdr = log.tsr_hdr or 0x100
        struct.pack_into("<I", m, DS * 16 + game.NUMBERS_PTR, 0)
        log._update_panel(0.0)
        struct.pack_into("<HH", m, DS * 16 + game.NUMBERS_PTR, 4, 0x6000)
        struct.pack_into("<h", m, 0x60004 + game.ARENA_FIGHTS * 2, 3)
        log._update_panel(0.0)
        struct.pack_into("<I", m, DS * 16 + game.NUMBERS_PTR, 0)
        log._update_panel(0.0)
        self.assertEqual(seen, [(None, False), (3, True), (3, True)])

    def test_no_flags_in_memory(self):
        """With the flags' pointer null (the arena outside a script's run): no flag, and nothing
        written (low memory left alone)."""
        log = arena()
        m = log.guest.mem
        struct.pack_into("<I", m, DS * 16 + game.FLAGS_PTR, 0)
        low = bytes(m[:0x400])
        self.assertFalse(log.game.flag(ring.XP_GIVEN))
        log.game.set_flag(ring.XP_GIVEN)
        self.assertEqual(bytes(m[:0x400]), low)
