"""ghost.py: the see-through figures' tables (REP, BLEND) and who is drawn see-through (GHOST_TAB)."""

import struct
import threading
import time
from unittest import mock
import unittest

from dsloader import game, ghost


def grey_palette() -> bytes:
    return bytes(v for i in range(256) for v in (i * 63 // 255,) * 3)


class TableTests(unittest.TestCase):

    def test_sizes(self):
        blend, rep = ghost.tables(grey_palette())
        self.assertEqual((len(blend), len(rep)), (ghost.REP_COUNT * 256, 256))
        self.assertEqual(max(rep), ghost.REP_COUNT - 1)

    def test_halfway(self):
        """Each BLEND entry is the colour (of those the game doesn't animate) nearest the halfway
        mix of the figure's colour (its REP's) and the one under it."""
        dac = grey_palette()
        colours = ghost.palette_colours(dac)
        reps = ghost.representatives(colours)
        blend, rep = ghost.tables(dac)
        for c in (16, 100, 223):  # (a figure's colour)
            r = rep[c]
            for under in (16, 60, 200, 223):
                mix = (reps[r][0] + colours[under][0]) / 2
                got = blend[r * 256 + under]
                self.assertTrue(ghost.FIRST <= got <= ghost.LAST)
                self.assertLessEqual(abs(colours[got][0] - mix), 1.01)

    def test_reps_nearest(self):
        dac = grey_palette()
        colours = ghost.palette_colours(dac)
        reps = ghost.representatives(colours)
        _, rep = ghost.tables(dac)
        for c in (20, 128, 220):
            best = min(abs(reps[r][0] - colours[c][0]) for r in range(ghost.REP_COUNT))
            self.assertAlmostEqual(abs(reps[rep[c]][0] - colours[c][0]), best)


class TableOfThingsTests(unittest.TestCase):

    def bits(self, table):
        return [t for t in range(ghost.THINGS) if table[t // 8] >> t % 8 & 1]

    def test_party_always(self):
        effects = [game.Effect(2, 2, ghost.INVISIBLE), game.Effect(40, 40, ghost.INVISIBLE)]
        self.assertEqual(self.bits(ghost.ghost_table(effects)), [2, 40])
        # one of the party detecting invisibility: the enemy seen, the party member still unseen
        seen = effects + [game.Effect(1, 1, ghost.DETECT_INVISIBILITY)]
        self.assertEqual(self.bits(ghost.ghost_table(seen)), [2])
        # an enemy detecting it changes nothing
        theirs = effects + [game.Effect(41, 41, ghost.DETECT_INVISIBILITY)]
        self.assertEqual(self.bits(ghost.ghost_table(theirs)), [2, 40])

    def test_none(self):
        self.assertEqual(ghost.ghost_table([game.Effect(5, 5, 7)]), bytes(65))


class FakeGuest:
    def __init__(self):
        self.mem = bytearray(0x110000)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class FakeGame:
    def __init__(self):
        self.guest = FakeGuest()
        self.fx = []

    def effects(self):
        return self.fx


class UpdateTests(unittest.TestCase):
    HDR, SEG, DAC = 0x5000, 0x8000, 0x6000

    def setUp(self):
        self.gd = FakeGame()
        m = self.gd.guest.mem
        struct.pack_into("<H", m, self.HDR + ghost.TSR_HDR_OFF, 0)
        struct.pack_into("<H", m, self.HDR + ghost.TSR_DAC, self.DAC - self.HDR)
        struct.pack_into("<H", m, self.HDR + ghost.TSR_FAR_SEG, self.HDR // 16)  # (DAC's: the far block)
        m[self.DAC:self.DAC + 768] = grey_palette()
        struct.pack_into("<H", m, self.HDR + ghost.TSR_GHOST_SEG, self.SEG)
        self.redraws = 0

    def redraw(self):
        self.redraws += 1

    def on(self):
        return struct.unpack_from("<H", self.gd.guest.mem, self.HDR + ghost.TSR_GHOST_ON)[0]

    def test_made_then_written(self):
        g = ghost.Ghosts()
        g.update(self.gd, self.HDR, True, 1, self.redraw)
        self.assertEqual(self.on(), 0)  # (being made)
        for _ in range(100):
            time.sleep(0.05)
            g.update(self.gd, self.HDR, True, 1, self.redraw)
            if self.on():
                break
        self.assertEqual(self.on(), 1)
        blend, rep = ghost.tables(grey_palette())
        m = self.gd.guest.mem
        self.assertEqual(bytes(m[self.SEG * 16:self.SEG * 16 + len(blend)]), blend)
        self.assertEqual(bytes(m[self.SEG * 16 + ghost.GH_REP:self.SEG * 16 + ghost.GH_REP + 256]), rep)
        drawn = self.redraws
        # someone invisible: the table written, the view drawn again
        self.gd.fx = [game.Effect(3, 3, ghost.INVISIBLE)]
        g.update(self.gd, self.HDR, True, 1, self.redraw)
        self.assertEqual(m[self.SEG * 16 + ghost.GH_TAB], 0x08)
        self.assertEqual(m[self.SEG * 16 + ghost.GH_CHANGED], 1)  # (DSCLOG draws the whole view: GHOST_UNION)
        self.assertEqual(self.redraws, drawn + 1)
        # off: DSCLOG draws them as ever
        g.update(self.gd, self.HDR, False, 1, self.redraw)
        self.assertEqual(self.on(), 0)

    def wait_on(self, g, palettes):
        for _ in range(100):
            g.update(self.gd, self.HDR, True, palettes, self.redraw)
            if self.on():
                return
            time.sleep(0.05)
        self.fail("tables never made")

    def test_cycling_colours_keep_the_tables(self):
        """DSCLOG's palette copy changing only in the colours the game cycles (fire, water: 1-15,
        240-248, every 30 s): the tables kept, GHOST_ON left on, nothing made, the view not drawn
        again. A change in any other (another area, 224-239 too) makes them anew. At most
        MADE_KEPT kept."""
        g = ghost.Ghosts()
        self.wait_on(g, 1)
        m = self.gd.guest.mem
        drawn = self.redraws
        for n, colour in enumerate((12, 3, 245), start=2):
            m[self.DAC + colour * 3] = (m[self.DAC + colour * 3] + 7) % 64
            g.update(self.gd, self.HDR, True, n, self.redraw)
            self.assertEqual(self.on(), 1)
        self.assertEqual((self.redraws, len(g._made)), (drawn, 1))
        m[self.DAC + 100 * 3] = (m[self.DAC + 100 * 3] + 9) % 64  # (another area's palette)
        g.update(self.gd, self.HDR, True, 9, self.redraw)
        self.assertEqual(self.on(), 0)  # (being made)
        self.wait_on(g, 9)
        self.assertEqual(len(g._made), 2)
        for n in range(ghost.MADE_KEPT + 2):
            m[self.DAC + 50 * 3] = n
            self.wait_on(g, 20 + n)
        self.assertEqual(len(g._made), ghost.MADE_KEPT)

    def test_made_after_a_refused_write(self):
        """The first write refused (the game busy with its item lists: ItemsBusy, a ValueError):
        the tables are still made at a later pass (marked as being made before the write, they
        never were, and see-through figures stayed off in that area)."""
        g = ghost.Ghosts()
        real = self.gd.guest.write
        refused = []

        def write(addr, data):
            if not refused:
                refused.append(addr)
                raise ValueError("ItemsBusy")
            real(addr, data)
        self.gd.guest.write = write
        with self.assertRaises(ValueError):
            g.update(self.gd, self.HDR, True, 1, self.redraw)
        self.gd.guest.write = real
        self.wait_on(g, 1)

    def test_area_colours_count(self):
        """Colours 224-239 differ from area to area (reds in one, magenta in another): a change
        there makes the tables anew."""
        g = ghost.Ghosts()
        self.wait_on(g, 1)
        m = self.gd.guest.mem
        m[self.DAC + 233 * 3] = (m[self.DAC + 233 * 3] + 9) % 64
        g.update(self.gd, self.HDR, True, 2, self.redraw)
        self.assertEqual(self.on(), 0)
        self.wait_on(g, 2)
        self.assertEqual(len(g._made), 2)

    def test_back_before_made(self):
        """The palette changed and back before the other's tables were made: GHOST_ON on again
        (it stayed 0, the figures solid, till the next change)."""
        g = ghost.Ghosts()
        self.wait_on(g, 1)
        m = self.gd.guest.mem
        before = m[self.DAC + 100 * 3]
        with mock.patch.object(threading.Thread, "start"):  # (the other's tables never made)
            m[self.DAC + 100 * 3] = (before + 9) % 64
            g.update(self.gd, self.HDR, True, 2, self.redraw)
            self.assertEqual(self.on(), 0)
            m[self.DAC + 100 * 3] = before
            g.update(self.gd, self.HDR, True, 3, self.redraw)
        self.assertEqual(self.on(), 1)

    def test_no_block(self):
        struct.pack_into("<H", self.gd.guest.mem, self.HDR + ghost.TSR_GHOST_SEG, 0)
        g = ghost.Ghosts()
        g.update(self.gd, self.HDR, True, 1, self.redraw)
        self.assertEqual((self.on(), self.redraws), (0, 0))


if __name__ == "__main__":
    unittest.main()
