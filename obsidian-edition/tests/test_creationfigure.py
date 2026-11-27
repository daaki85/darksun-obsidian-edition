"""The creation screen's figure in the class's outfit (creationfigure.py): the class as a party
member's, and the game's handle of the screen's figures read and written where DOSBox has it."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import creationfigure as cf, game, sprites  # noqa: E402


class FakeGuest:
    def __init__(self):
        self.mem = bytearray(0x300000)  # (the figures past 2 MB, as in the game)
        self.size = len(self.mem)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


def chunk(n, size):
    """A one-frame picture chunk of SIZE bytes (its head, then N's bytes)."""
    return cf.FRAME_HEAD.pack(size, 1, cf.FRAME_HEAD.size) + bytes([n]) * (size - cf.FRAME_HEAD.size)


class FakeGame:
    """The figures' handle (1, id 2A2Ah) of FIGURES_SIZE, its pages a chain in the first page
    directory block on the XMS backend, XMS pages FIRST_PAGE on at XMS_BASE; the entries before the
    figures' and the figures' (14, of SIZES) one after another from START."""
    XMS_BASE, FIRST_PAGE, START = 0x110000, 0x30, 0x3C000

    def __init__(self, sizes=tuple(300 + 10 * k for k in range(cf.END - cf.FIRST))):
        self.guest = FakeGuest()
        self.ds, self.load_seg = 0x4000, 0x100
        d = self.ds * 16
        self.guest.write(d + cf.FIGURES_HANDLE, struct.pack("<I", 0x2A2A0001))
        self.guest.write(d + sprites.HANDLES + sprites.HANDLE_SIZE, struct.pack("<HHI", self.FIRST_PAGE, 0x2A2A, cf.FIGURES_SIZE))
        for b in range(2):  # (links of 40h on in the second block)
            self.guest.write(d + sprites.DIR_BLOCKS + b * sprites.DIR_BLOCK + 2, struct.pack("<HH", 1, b))
        for n in range((cf.FIGURES_SIZE + sprites.STORE_PAGE - 1) // sprites.STORE_PAGE):
            link = self.FIRST_PAGE + n
            block = d + sprites.DIR_BLOCKS + (link >> 6) * sprites.DIR_BLOCK
            self.guest.write(block + sprites.DIR_ENTRIES + (link & 0x3F) * 4, struct.pack("<HH", link, link + 1))
        self.guest.write(d + sprites.BACKEND_WRITE, struct.pack("<I", (self.load_seg + sprites.XMS_WRITE[0]) << 16 | sprites.XMS_WRITE[1]))
        tab = [8 * n for n in range(cf.FIRST + 1)]  # (the screen's other pictures: not the figures')
        tab[cf.FIRST] = self.START
        for k, size in enumerate(sizes):
            self.write(tab[-1], chunk(k, size))
            tab.append(tab[-1] + size)
        self.guest.write(d + cf.FIGURES_TABLE, struct.pack("<%dI" % len(tab), *tab))

    def at(self, place):
        return self.XMS_BASE + self.FIRST_PAGE * sprites.STORE_PAGE + place

    def write(self, place, data):
        self.guest.write(self.at(place), data)

    def table(self):
        return list(struct.unpack("<%dI" % (cf.END + 1), self.guest.read(self.ds * 16 + cf.FIGURES_TABLE, 4 * (cf.END + 1))))

    def entry(self, n):
        tab = self.table()
        return self.guest.read(self.at(tab[n]), tab[n + 1] - tab[n])


class CreationRole(unittest.TestCase):
    def sheet(self, race, *classes):
        s = bytearray(game.SHEET_SIZE)
        s[game.SHEET_RACE] = race
        s[game.SHEET_CLASSES:game.SHEET_CLASSES + len(classes)] = bytes(classes)
        return bytes(s)

    def test_the_screens_classes_as_a_members(self):
        self.assertEqual(cf.creation_role(self.sheet(game.HUMAN, 3), 2095), "Warrior")
        self.assertEqual(cf.creation_role(self.sheet(game.HUMAN, 5), 2095), "Mage")
        self.assertEqual(cf.creation_role(self.sheet(game.HUMAN, 8), 2099), "Thief")
        self.assertIsNone(cf.creation_role(self.sheet(game.HUMAN), 2095))  # (no class: plain)

    def test_multiclass(self):
        role = cf.creation_role(self.sheet(game.DWARF, 3, 8), 2055)
        self.assertIsNotNone(role)
        self.assertEqual(set(role.split("/")), {"Fighter", "Thief"})


class Figures(unittest.TestCase):
    def test_found_where_dosbox_has_it(self):
        gd = FakeGame()
        figures = cf.Figures(gd)
        self.assertTrue(figures.locate())
        self.assertEqual(figures.base, FakeGame.XMS_BASE)

    def test_not_taken_without_every_head(self):
        gd = FakeGame()
        gd.write(gd.table()[cf.FIRST + 5], bytes(10))
        self.assertFalse(cf.Figures(gd).locate())

    def test_a_figure_written_the_rest_moved_along(self):
        gd = FakeGame()
        before = [gd.entry(n) for n in range(cf.FIRST, cf.END)]
        tab = gd.table()
        new = chunk(99, 700)
        self.assertTrue(cf.Figures(gd).put(3, new))
        after = gd.table()
        self.assertEqual(after[:cf.FIRST + 4], tab[:cf.FIRST + 4])  # (those before it as they were)
        self.assertEqual(after[cf.FIRST + 4] - after[cf.FIRST + 3], 700)
        self.assertEqual(after[cf.END], tab[cf.END] + 700 - (tab[cf.FIRST + 4] - tab[cf.FIRST + 3]))
        self.assertEqual(gd.entry(cf.FIRST + 3), new)
        for n in range(cf.FIRST, cf.END):
            if n != cf.FIRST + 3:
                self.assertEqual(gd.entry(n), before[n - cf.FIRST])
        smaller = chunk(98, 200)  # (and back, smaller)
        self.assertTrue(cf.Figures(gd).put(3, smaller))
        self.assertEqual(gd.entry(cf.FIRST + 3), smaller)
        self.assertEqual(gd.entry(cf.END - 1), before[-1])

    def test_no_room_past_the_handle(self):
        gd = FakeGame()
        self.assertFalse(cf.Figures(gd).put(0, chunk(1, cf.FIGURES_SIZE)))
        self.assertEqual(gd.entry(cf.FIRST), chunk(0, 300))

    def test_another_backend_not_used(self):
        gd = FakeGame()
        gd.guest.write(gd.ds * 16 + sprites.BACKEND_WRITE, bytes(4))
        self.assertFalse(cf.Figures(gd).put(0, chunk(1, 400)))


class Update(unittest.TestCase):
    class Pics:
        def __init__(self):
            self.built = []

        def model(self, obj):
            return 2095

        def supports_outfits(self, figure, model):
            return True

        def build(self, obj, combat, gear, armour, model, figure, stage, role, only=None):
            self.built.append((obj, role, only))
            return chunk(77, 333 + len(role or ""))

    def game(self, classes):
        gd = FakeGame()
        sheet, creature = 0x30000, 0x30000 + game.SHEET_SIZE
        s = bytearray(game.SHEET_SIZE)
        s[game.SHEET_RACE] = game.HUMAN
        s[game.SHEET_CLASSES:game.SHEET_CLASSES + len(classes)] = bytes(classes)
        gd.guest.write(sheet, bytes(s))
        gd.guest.write(creature + sprites.CREATURE_FIGURE, struct.pack("<H", 0))
        d = gd.ds * 16
        gd.guest.write(d + game.CREATION_SHEET_PTR, struct.pack("<HH", sheet & 0xF, sheet >> 4))
        gd.guest.write(d + game.CREATION_CREATURE_PTR, struct.pack("<HH", creature & 0xF, creature >> 4))
        gd.creating = lambda: True
        gd.creation_sheet = lambda: gd.guest.read(sheet, game.SHEET_SIZE)
        return gd

    def test_written_once_and_due_cleared(self):
        gd = self.game([3])
        hdr = 0x90000
        gd.guest.write(hdr + cf.TSR_FIG_DUE, b"\1")
        figure, pics = cf.CreationFigure(gd), self.Pics()
        self.assertTrue(figure.update(pics, hdr))
        self.assertEqual(pics.built, [(300, "Warrior", 0)])
        self.assertEqual(gd.entry(cf.FIRST), chunk(77, 340))
        self.assertEqual(gd.guest.read(hdr + cf.TSR_FIG_DUE, 1), b"\0")
        self.assertFalse(figure.update(pics, hdr))  # (the same: not again)
        self.assertEqual(len(pics.built), 1)

    def test_due_cleared_without_pictures(self):
        gd = self.game([3])
        hdr = 0x90000
        gd.guest.write(hdr + cf.TSR_FIG_DUE, b"\1")
        self.assertFalse(cf.CreationFigure(gd).update(None, hdr))
        self.assertEqual(gd.guest.read(hdr + cf.TSR_FIG_DUE, 1), b"\0")


if __name__ == "__main__":
    unittest.main()
