"""The Loader's changes to the game's item lists: made only while the game leaves them be
(itemgate.py), and put off whole, not half made, while it doesn't."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, itemgate
from dsloader.guestmem import GuestMemory

DS = 0x5000
ITEMS, CREATURES = 0x70000, 0x60000


class FakeProcess:
    def __init__(self, size):
        self.mem = bytearray(size)
        self.paused = 0  # (paused now)
        self.pauses = 0
        self.on_pause = None  # (what the game does as the Loader pauses it: a test's)

    def read(self, addr, n):
        return bytes(self.mem[addr:addr + n])

    def write(self, addr, data):
        self.mem[addr:addr + len(data)] = data

    def suspend(self):
        if self.on_pause:
            self.on_pause()
        self.paused += 1
        self.pauses += 1
        return True

    def resume(self):
        self.paused -= 1


class Clock:
    def __init__(self):
        self.now = 0.0
        self.slept = []

    def __call__(self):
        return self.now

    def sleep(self, s):
        self.slept.append(round(s, 3))
        self.now += s


def far(seg_off: int) -> bytes:
    return struct.pack("<HH", seg_off % 16, seg_off // 16)


def setup():
    proc = FakeProcess(0x100000)
    guest = GuestMemory(proc, 0, 0x100000)
    gd = game.GameData(guest, DS)
    proc.write(DS * 16 + game.ITEMS_PTR, far(ITEMS))
    proc.write(DS * 16 + game.CREATURES_PTR, far(CREATURES))
    clock = Clock()
    gate = itemgate.ItemGate(gd, clock=clock, sleep=clock.sleep)
    guest.item_gate = gate
    return proc, guest, gd, gate, clock


class CoversTests(unittest.TestCase):
    def test_what_is_the_item_lists(self):
        """The free lists' heads, item records, the things table and a creature's list heads are
        the item lists; the rest of a creature's record, and other memory, are not."""
        _, _, gd, gate, _ = setup()
        ds = DS * 16
        things = (gd.load_seg + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
        creature = CREATURES + 5 * game.CREATURE_SIZE
        self.assertTrue(gate.covers(ds + itemgate.FREE_ITEMS, 2))
        self.assertTrue(gate.covers(ds + itemgate.FREE_THINGS + 1, 1))
        self.assertTrue(gate.covers(ds + itemgate.THINGS_USED, 2))
        self.assertTrue(gate.covers(ITEMS + 399 * game.ITEM_SIZE + game.ITEM_NEXT, 2))
        self.assertFalse(gate.covers(ITEMS + 400 * game.ITEM_SIZE, 2))
        self.assertTrue(gate.covers(things + 300 * 3 + 1, 2))
        self.assertTrue(gate.covers(creature + game.CREATURE_ITEM_LISTS[1], 2))
        self.assertFalse(gate.covers(creature + game.CREATURE_NAME, 16))
        self.assertTrue(gate.covers(creature, game.CREATURE_SIZE))  # (a whole record: its heads too)
        self.assertFalse(gate.covers(ds + 0x2000, 2))


    def test_tables_moved_mid_pass(self):
        """The game moving its item table, or emptying the pointer as it rebuilds it, after the
        pass began: a write to the old place is still covered (so refused, the heads changed);
        a write elsewhere is not, the pointer null or not (a reply to DSCLOG, the see-through
        tables: refused, they once left the see-through figures off for good)."""
        proc, guest, _, gate, _ = setup()
        gate.begin()
        old = ITEMS + 3 * game.ITEM_SIZE
        proc.write(DS * 16 + game.ITEMS_PTR, far(ITEMS + 0x4000))
        self.assertTrue(gate.covers(old, 2))
        with self.assertRaises(itemgate.ItemsBusy):
            guest.write(old, b"\x07")
        self.assertEqual(proc.mem[old], 0)
        gate.end()
        proc.write(DS * 16 + game.ITEMS_PTR, far(ITEMS))
        gate.begin()
        proc.write(DS * 16 + game.ITEMS_PTR, b"\0\0\0\0")
        self.assertTrue(gate.covers(old, 2))  # (where the table was)
        self.assertTrue(gate.covers(77 * game.ITEM_SIZE, 2))  # (where a null pointer's write lands: past
        with self.assertRaises(itemgate.ItemsBusy):           # low memory's guard, in DOS's own)
            guest.write(77 * game.ITEM_SIZE + game.ITEM_NEXT, b"\x07")
        self.assertEqual(proc.mem[77 * game.ITEM_SIZE + game.ITEM_NEXT], 0)
        gate.end()
        gate.begin()
        self.assertFalse(gate.covers(DS * 16 + 0x2000, 2))  # (anything else, even with it null)
        gate.end()
        self.assertFalse(gate.covers(DS * 16 + 0x2000, 2))  # (no pass: nothing moved to see)


class OwnWritesTests(unittest.TestCase):
    def test_own_changes_not_refused_later(self):
        """The Loader's own block (a list made: the free list's head moved) released: a later block
        of the same pass compares with the heads as that block left them, not refused for them."""
        proc, guest, _, gate, _ = setup()
        gate.begin()
        guest.write(DS * 16 + itemgate.FREE_THINGS, struct.pack("<H", 400))
        gate.release()
        guest.write(DS * 16 + itemgate.THINGS_USED, struct.pack("<H", 5))
        self.assertEqual((gate.refusals, struct.unpack_from("<H", proc.mem, DS * 16 + itemgate.THINGS_USED)[0]), (0, 5))
        gate.end()


class PassTests(unittest.TestCase):
    def test_writes_held_still(self):
        """A pass's item writes: made after the wait, with the game paused once until the pass
        ends; other writes neither wait nor pause it."""
        proc, guest, _, gate, clock = setup()
        gate.begin()
        clock.now += 0.02
        guest.write(DS * 16 + 0x2000, b"\x01")  # (not the item lists)
        self.assertEqual((proc.pauses, clock.slept), (0, []))
        guest.write(ITEMS + 3 * game.ITEM_SIZE, b"\x07")
        guest.write(ITEMS + 4 * game.ITEM_SIZE, b"\x08")
        self.assertEqual(clock.slept, [0.04])  # (the rest of the wait, once)
        self.assertEqual((proc.pauses, proc.paused), (1, 1))
        self.assertEqual(proc.mem[ITEMS + 4 * game.ITEM_SIZE], 8)
        gate.end()
        self.assertEqual(proc.paused, 0)

    def test_load_under_way(self):
        """The game's free list moved on since the pass began (an area loading): nothing of the
        pass's item writes made, the game running on, and the next pass free to try."""
        proc, guest, _, gate, _ = setup()
        gate.begin()
        proc.write(DS * 16 + itemgate.FREE_ITEMS, struct.pack("<H", 17))
        with self.assertRaises(itemgate.ItemsBusy):
            guest.write(ITEMS + 3 * game.ITEM_SIZE, b"\x07")
        with self.assertRaises(itemgate.ItemsBusy):  # (the rest of the pass's too)
            guest.write(DS * 16 + itemgate.FREE_ITEMS, b"\x00\x00")
        self.assertEqual(proc.mem[ITEMS + 3 * game.ITEM_SIZE], 0)
        self.assertEqual(proc.paused, 0)
        self.assertEqual(gate.refusals, 1)
        gate.end()
        gate.begin()
        guest.write(ITEMS + 3 * game.ITEM_SIZE, b"\x07")
        gate.end()
        self.assertEqual(proc.mem[ITEMS + 3 * game.ITEM_SIZE], 7)

    def test_load_begun_as_paused(self):
        """The area changed by the time the game is paused (after the wait): refused too."""
        proc, guest, _, gate, _ = setup()
        gate.begin()
        proc.on_pause = lambda: proc.write(DS * 16 + itemgate.REGION, b"\x29\x00")
        with self.assertRaises(itemgate.ItemsBusy):
            guest.write(ITEMS, b"\x07")
        self.assertEqual(proc.paused, 0)

    def test_release_and_again(self):
        """Released after a block, the game runs on; a later block in the pass is looked at again,
        against the lists as the pass began."""
        proc, guest, _, gate, _ = setup()
        gate.begin()
        guest.write(ITEMS, b"\x07")
        itemgate.release(type("G", (), {"guest": guest})())
        self.assertEqual(proc.paused, 0)
        guest.write(ITEMS + 1, b"\x08")
        self.assertEqual((proc.pauses, proc.paused), (2, 1))
        gate.release()
        proc.write(DS * 16 + game.ITEMS_PTR, far(ITEMS + 0x100))  # (the table moved: a load)
        with self.assertRaises(itemgate.ItemsBusy):
            guest.write(ITEMS + 0x100, b"\x09")
        gate.end()
        self.assertEqual(proc.paused, 0)

    def test_hold_before_a_roll(self):
        """hold: the gate opened before anything that can't be done twice; refused, it raises
        before it, and with no gate (a test's game) it does nothing."""
        proc, guest, gd, gate, _ = setup()
        gate.begin()
        proc.write(DS * 16 + itemgate.FREE_THINGS, b"\x01\x00")
        with self.assertRaises(itemgate.ItemsBusy):
            itemgate.hold(gd)
        itemgate.hold(object())

    def test_outside_a_pass(self):
        """A write outside a pass (a tool's): the lists looked at over the wait, the game not
        paused (no one to let it go)."""
        proc, guest, _, gate, clock = setup()
        guest.write(ITEMS, b"\x07")
        self.assertEqual((clock.slept, proc.pauses, proc.mem[ITEMS]), ([itemgate.WAIT], 0, 7))

    def test_no_pausing(self):
        """A process that can't be paused: the writes follow the look."""
        proc, guest, _, gate, _ = setup()
        proc.suspend = lambda: False
        gate.begin()
        guest.write(ITEMS, b"\x07")
        gate.end()
        self.assertEqual(proc.mem[ITEMS], 7)


class MovedDuringTheWaitTests(unittest.TestCase):
    """The game moving an item between two lists during the gate's wait (an inventory drag, a
    GIVE): none of the heads the gate looks at change, so it lets the writes go; a change worked
    out from the lists as read before the wait would then cut a list into another (the audit's
    auditwork-4/toctou.py). Every change to the lists reads them with the gate held (ring.held)."""

    def setUp(self):
        from dsloader import ring
        self.proc, self.guest, self.gd, self.gate, _ = setup()
        self.things = (self.gd.load_seg + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
        for t in range(ring.THING_COUNT):
            self.proc.write(self.things + t * 3, bytes(3))
        # thing 10: 1 -> 2 -> 3; thing 11: 5; the free list: 7
        self.thing(10, 1), self.next(1, 2), self.next(2, 3), self.next(3, game.NO_ITEM)
        self.thing(11, 5), self.next(5, game.NO_ITEM)
        self.proc.write(DS * 16 + ring.FREE_ITEMS, struct.pack("<H", 7))
        self.next(7, game.NO_ITEM)

    def next(self, item, after):
        self.proc.write(ITEMS + item * game.ITEM_SIZE + game.ITEM_NEXT, struct.pack("<h", after))

    def thing(self, t, first):
        self.proc.write(self.things + t * 3, struct.pack("<Bh", game.THING_ITEM, first))

    def walk(self, first):
        out, i = [], first
        while 0 <= i < game.NO_ITEM and len(out) < 10:
            out.append(i)
            i = struct.unpack("<h", self.proc.read(ITEMS + i * game.ITEM_SIZE + game.ITEM_NEXT, 2))[0]
        return out

    def first(self, t):
        return struct.unpack_from("<h", self.proc.read(self.things + t * 3, 3), 1)[0]

    def drag(self):
        """The game's move: item 2 to the head of thing 11 (the free lists' heads untouched)."""
        self.next(1, 3), self.next(2, 5), self.thing(11, 2)

    def test_unlink_after_a_move(self):
        from dsloader import ring
        self.gate.begin()
        it = ring.Items(self.gd)  # (the caller's reads, as the pass began)
        self.proc.on_pause = self.drag  # (as the gate pauses the game: its wait is over)
        self.assertTrue(ring.unlink(self.gd, it, 3, "test"))
        self.gate.end()
        self.assertEqual(self.walk(self.first(10)), [1])
        self.assertEqual(self.walk(self.first(11)), [2, 5])
        self.assertEqual(self.walk(struct.unpack("<H", self.proc.read(DS * 16 + ring.FREE_ITEMS, 2))[0]), [3, 7])

    def test_take_after_a_move(self):
        """pickpocket._take with the item ahead of it read before the move: refused, nothing written."""
        from dsloader import pickpocket, ring
        creature = CREATURES + 5 * game.CREATURE_SIZE
        self.proc.write(creature + game.CREATURE_ITEM_LISTS[0], struct.pack("<h", 10))
        self.gate.begin()
        it = ring.Items(self.gd)
        self.proc.on_pause = self.drag
        with self.assertRaises(ValueError):
            pickpocket._take(self.gd, it, 5, 0, 3, 2)  # (3 after 2, as read before the move)
        self.gate.end()
        self.assertEqual(self.walk(self.first(10)), [1, 3])
        self.assertEqual(self.walk(self.first(11)), [2, 5])


class PutOffTests(unittest.TestCase):
    def test_buyback_kept_later(self):
        """A sold item the game's busy lists put off: kept in a later look, not passed over."""
        from dsloader import buyback

        class Guest:
            def __init__(self):
                self.mem = {}

            def read(self, addr, n):
                return bytes(self.mem.get(addr + i, 0) for i in range(n))

            def write(self, addr, data):
                self.mem.update((addr + i, b) for i, b in enumerate(data))

        g = Guest()
        hdr = 0x1000
        gd = type("G", (), {"guest": g})()
        b = buyback.Buyback()
        b.seen = 0
        g.mem[hdr + buyback.SOLD_SEQ] = 1
        g.write(hdr + buyback.SOLD_ITEMS, struct.pack("<4H", 40, *[buyback.DONE] * 3))
        calls = []

        def keep(gd_, thing, merchant, item):
            calls.append(thing)
            if len(calls) == 1:
                raise itemgate.ItemsBusy("busy")
            return []
        b.keep = keep
        with self.assertRaises(itemgate.ItemsBusy):
            b.watch(gd, hdr)
        self.assertEqual(b.seen, 0)
        b.watch(gd, hdr)
        self.assertEqual((b.seen, len(calls)), (1, 2))
        self.assertEqual(g.read(hdr + buyback.SOLD_ITEMS, 2), b"\xff\xff")  # (seen to)


if __name__ == "__main__":
    unittest.main()
