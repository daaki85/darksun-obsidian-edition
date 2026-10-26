"""Names floating over figures (labels.py): their masks, and the slots in DSCLOG's header."""

import struct
import unittest

from dsloader import combatlog, labels

HDR, BASE, DAC = 0x2000, 0x1F00, 0x3000


class Font:
    """Every letter 3 pixels wide, ink in its middle column, 9 rows high."""
    height = 9

    def glyph(self, ch):
        return 3, bytes((0, combatlog.FONT_INK, 0) * self.height)


class Guest:
    def __init__(self):
        self.mem = bytearray(0x4000)
        self.writes = []
        struct.pack_into("<H", self.mem, HDR + combatlog.TSR_HDR_OFF, HDR - BASE)
        struct.pack_into("<H", self.mem, HDR + combatlog.TSR_DAC, DAC - BASE)
        for i in range(256):
            self.mem[DAC + i * 3:DAC + i * 3 + 3] = bytes((i // 4,) * 3)  # (a grey ramp)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.writes.append((at, bytes(data)))
        self.mem[at:at + len(data)] = data


def slot(guest, n):
    return guest.read(HDR + labels.TSR_LABELS + n * labels.SIZE, labels.SIZE)


class LabelTests(unittest.TestCase):
    def test_masks(self):
        """The ink where the font's is, a pixel in from the edge; the edge round it, not on it."""
        w, h, ink, edge = labels.masks(Font(), "ab")
        self.assertEqual((w, h), (8, 11))
        bit = lambda mask, x, y: bool(mask[y * labels.ROW + x // 8] >> (x % 8) & 1)
        self.assertEqual([x for x in range(w) if bit(ink, x, 5)], [2, 5])
        self.assertEqual([x for x in range(w) if bit(edge, x, 5)], [1, 3, 4, 6])
        self.assertTrue(bit(edge, 2, 0) and bit(edge, 2, 10) and not bit(ink, 2, 0))

    def test_long_names_fit(self):
        font = Font()
        self.assertEqual(labels.fit(font, "Miss"), "Miss")
        name = labels.fit(font, "Conjure Lesser Water Elemental Protection From Everything At Once")
        self.assertLessEqual(labels.width(font, name), labels.WIDTH_MOST)
        self.assertTrue(name.startswith("Lesser Water Elem."))

    def test_show_and_tick(self):
        """A label's slot: its number written last (DSCLOG never puts a half-written one); the same
        text over the same figure kept longer; a full set's oldest taken; gone when its time is up."""
        guest, lab = Guest(), labels.Labels()
        lab.font = Font()
        lab.show(guest, HDR, 0x25, "Miss", labels.MISS_INK, 10.0)
        number, w, h, up, ink, edge, thing = struct.unpack_from("<BBBBBBH", slot(guest, 0))
        self.assertEqual((number, w, h, up, thing), (1, 14, 11, labels.UP, 0x25))
        self.assertEqual((ink, edge), (combatlog.nearest(guest.read(DAC, 768), labels.MISS_INK),
                                       combatlog.nearest(guest.read(DAC, 768), labels.EDGE)))
        self.assertEqual(guest.writes[0], (HDR + labels.TSR_LABELS, b"\0"))
        self.assertEqual(guest.writes[-1], (HDR + labels.TSR_LABELS, b"\1"))
        lab.show(guest, HDR, 0x25, "Miss", labels.MISS_INK, 11.0)  # (kept longer, not written again)
        self.assertEqual(slot(guest, 0)[0], 1)
        lab.show(guest, HDR, 2, "Enlarge", labels.SPELL_INK, 11.2)
        lab.show(guest, HDR, 3, "Friends", labels.SPELL_INK, 11.4)
        lab.show(guest, HDR, 4, "Bless", labels.SPELL_INK, 11.5)
        lab.show(guest, HDR, 5, "Haste", labels.SPELL_INK, 11.6)  # (the oldest's slot: the miss's)
        things = [struct.unpack_from("<H", slot(guest, n), 6)[0] for n in range(labels.SLOTS)]
        self.assertEqual(things, [5, 2, 3, 4])
        lab.tick(guest, HDR, 11.2 + labels.SHOW_FOR)
        self.assertEqual([slot(guest, n)[0] for n in range(labels.SLOTS)], [5, 0, 3, 4])
        lab.on = False
        lab.tick(guest, HDR, 11.3)
        self.assertEqual(slot(guest, 0)[0], 0)
        lab.show(guest, HDR, 2, "Enlarge", labels.SPELL_INK, 12.0)  # (switched off: none)
        self.assertEqual([slot(guest, n)[0] for n in range(2)], [0, 0])

    def test_charge_first(self):
        """A charge used stays CHARGE_FOR seconds and no "Miss" or spell's name replaces it, over its
        figure or as the oldest of a full set; a newer charge over the same figure does."""
        guest, lab = Guest(), labels.Labels()
        lab.font = Font()
        thing = lambda n: struct.unpack_from("<H", slot(guest, n), 6)[0]
        text_ink = lambda n: slot(guest, n)[4]
        lab.show(guest, HDR, 0x25, "Armor: 7 left", labels.CHARGE_INK, 10.0, priority=1)
        lab.show(guest, HDR, 0x25, "Miss", labels.MISS_INK, 10.5)  # (left out: the charge shows)
        self.assertEqual(text_ink(0), combatlog.nearest(guest.read(DAC, 768), labels.CHARGE_INK))
        lab.show(guest, HDR, 2, "Miss", labels.MISS_INK, 10.6)
        lab.show(guest, HDR, 3, "Miss", labels.MISS_INK, 10.7)
        lab.show(guest, HDR, 4, "Miss", labels.MISS_INK, 10.8)
        lab.show(guest, HDR, 5, "Miss", labels.MISS_INK, 10.9)  # (the oldest miss's slot, not the charge's)
        self.assertEqual([thing(n) for n in range(labels.SLOTS)], [0x25, 5, 3, 4])
        lab.show(guest, HDR, 0x25, "Armor: 6 left", labels.CHARGE_INK, 11.0, priority=1)
        lab.tick(guest, HDR, 11.0 + labels.SHOW_FOR)
        self.assertEqual([slot(guest, n)[0] != 0 for n in range(2)], [True, False])
        lab.tick(guest, HDR, 11.0 + labels.CHARGE_FOR)
        self.assertEqual(slot(guest, 0)[0], 0)


if __name__ == "__main__":
    unittest.main()
