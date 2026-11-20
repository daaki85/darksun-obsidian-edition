"""The dice log for Wake of the Ravager (dsloader.ravlog): the layout profile it swaps in (and back),
the item type records served in Shattered Lands' layout, the read-only view of the game's memory, and
the sequel's item names."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dicelog, game, ravager, ravlog  # noqa: E402


class FakeGuest:
    def __init__(self, size=0x110000):
        self.mem = bytearray(size)
        self.writes = 0

    def read(self, addr, size):
        return bytes(self.mem[addr:addr + size])

    def write(self, addr, data):
        self.writes += 1
        self.mem[addr:addr + len(data)] = data


class ProfileTests(unittest.TestCase):
    def tearDown(self):
        ravlog.restore_layout()

    def test_layout_maps_record_fields(self):
        layout = ravlog.layout()
        self.assertEqual(layout["CREATURE_NAME"], 0x21)
        self.assertEqual(layout["CREATURE_THAC0"], 0x16)
        self.assertEqual(layout["SHEET_LEVELS"], 0x1E)
        self.assertEqual(layout["ITEM_PLUS"], 0x16)
        self.assertEqual(layout["CREATURE_SIZE"], ravager.CREATURE_SIZE)
        self.assertNotIn("SHEET_AGE", layout)  # (no such field in the sequel: left as SL's, not ported)
        self.assertNotIn("SHEET_FLAG_RANGER", layout)  # (a flag, not an offset)

    def test_apply_and_restore(self):
        sl = (game.CREATURE_NAME, game.DGROUP, dicelog.HDR_SIG, dicelog.CREATURE_THAC0)
        self.assertGreater(ravlog.apply_layout(), 0)
        self.assertEqual((game.CREATURE_NAME, game.DGROUP, dicelog.HDR_SIG, dicelog.CREATURE_THAC0),
                         (0x21, ravager.DGROUP, ravlog.HDR_SIG, 0x16))  # (dicelog's imported copy too)
        self.assertEqual(ravlog.apply_layout(), 0)  # (once)
        ravlog.restore_layout()
        self.assertEqual((game.CREATURE_NAME, game.DGROUP, dicelog.HDR_SIG, dicelog.CREATURE_THAC0), sl)


class TypeTests(unittest.TestCase):
    def test_sl_type(self):
        """The sequel's type 18 and SL's type 1 (the same weapon): the fields from +8 on line up."""
        wotr = bytes.fromhex("0a2000fa400c1104080100407b1700")
        sl = ravlog.sl_type(wotr)
        self.assertEqual(len(sl), game.ITEM_TYPE_SIZE)
        self.assertEqual(sl[0], 0x0A)
        self.assertEqual(sl[2], 0x20)
        self.assertEqual(sl[6], 0xFA)
        self.assertEqual(sl[0x0B:0x10], bytes.fromhex("0408010040"))  # rate, sides, count, bonus, flags
        self.assertEqual(sl[0x10:0x13], bytes.fromhex("7b1700"))

    def test_view_serves_types_in_sl_layout(self):
        g = FakeGuest()
        ds = 0x4982
        base = 0x72B94
        struct.pack_into("<HH", g.mem, ds * 16 + ravlog.ADDRESSES["ITEM_TYPES_PTR"], base & 0xF, base >> 4)
        for k in range(3):
            g.mem[base + k * 15:base + (k + 1) * 15] = bytes([k + 1]) + bytes(range(2, 16))
        view = ravlog.ReadOnlyGuest(g)
        view.ds = ds
        two = view.read(base + 2 * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
        self.assertEqual(two, ravlog.sl_type(bytes([3]) + bytes(range(2, 16))))
        across = view.read(base + game.ITEM_TYPE_SIZE - 2, 4)  # (a read across two records)
        self.assertEqual(across, ravlog.sl_type(bytes([1]) + bytes(range(2, 16)))[-2:] +
                         ravlog.sl_type(bytes([2]) + bytes(range(2, 16)))[:2])
        self.assertEqual(view.read(0x500, 2), bytes(2))  # (elsewhere: the memory as it is)

    def test_view_drops_writes(self):
        g = FakeGuest()
        view = ravlog.ReadOnlyGuest(g)
        view.write(0x100, b"\x01")
        self.assertEqual((g.writes, view.dropped, g.mem[0x100]), (0, 1, 0))


class NameTests(unittest.TestCase):
    def test_names_by_line_from_one(self):
        g = FakeGuest()
        names = ["Tombstone", "Olive Branch", "One-use Scroll"] + [f"n{i}" for i in range(20)] + ["Lotulis", "Polearm", "Longsword"]
        at = 0x73000
        data = "\r\x00".join(names).encode("latin1") + b"\r\x00\x00\x00"
        g.mem[at:at + len(data)] = data
        gd = ravlog.RavGameData.__new__(ravlog.RavGameData)
        gd.guest = g
        self.assertEqual(gd.item_name(1), "Tombstone")
        self.assertEqual(gd.item_name(26), "Longsword")  # (Ar'anda's, in a running game)
        self.assertEqual(gd.item_name(24), "Lotulis")  # (the Draxans', as the Look box has it)
        self.assertEqual(gd.item_name(999), "item 999")


if __name__ == "__main__":
    unittest.main()
