"""The keys read from the BIOS keyboard buffer (dsloader/keywatch.py), and R, which shows and hides
the squares in reach (the dice log's _squares_key)."""
import os
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dicelog, keywatch, quicksave, squares
from test_squares import DS, HDR, Game


class Keyboard:
    """A BIOS keyboard buffer in a guest's memory, typed into as DOSBox's handler does."""

    def __init__(self, guest, tail=keywatch.FIRST):
        self.guest = guest
        struct.pack_into("<HH", guest.mem, keywatch.BIOS + keywatch.HEAD, tail, tail)

    def press(self, *keys):
        m = self.guest.mem
        for key in keys:
            tail, = struct.unpack_from("<H", m, keywatch.BIOS + keywatch.TAIL)
            struct.pack_into("<H", m, keywatch.BIOS + tail, key)
            tail = tail + 2 if tail + 2 < keywatch.END else keywatch.FIRST
            struct.pack_into("<H", m, keywatch.BIOS + keywatch.TAIL, tail)

    def read_all(self):
        """The game has read every key (INT 16h): the head catches the tail up; the words stay."""
        m = self.guest.mem
        m[keywatch.BIOS + keywatch.HEAD:keywatch.BIOS + keywatch.HEAD + 2] = \
            m[keywatch.BIOS + keywatch.TAIL:keywatch.BIOS + keywatch.TAIL + 2]


class KeyWatchTests(unittest.TestCase):
    def setUp(self):
        self.gd = Game()
        self.kb = Keyboard(self.gd.guest)
        self.watch = keywatch.KeyWatch()

    def test_keys_since_the_last_look(self):
        """None at the first look (what was typed before the Loader came); then each key once, in
        order, whether the game has read it or not."""
        self.kb.press(0x1E61)
        self.assertEqual(self.watch.take(self.gd.guest), [])
        self.assertEqual(self.watch.take(self.gd.guest), [])
        self.kb.press(keywatch.KEY_R)
        self.kb.read_all()
        self.assertEqual(self.watch.take(self.gd.guest), [keywatch.KEY_R])
        self.assertEqual(self.watch.take(self.gd.guest), [])
        self.kb.press(0x1C0D, keywatch.KEY_SHIFT_R, 0x3F00)
        self.assertEqual(self.watch.take(self.gd.guest), [0x1C0D, keywatch.KEY_SHIFT_R, 0x3F00])

    def test_round_the_buffers_end(self):
        kb = Keyboard(self.gd.guest, tail=keywatch.END - 4)
        self.watch.take(self.gd.guest)
        kb.press(1, 2, 3, 4)  # (3Ah, 3Ch, then 1Eh, 20h)
        self.assertEqual(self.watch.take(self.gd.guest), [1, 2, 3, 4])
        self.assertEqual(struct.unpack_from("<H", self.gd.guest.mem, keywatch.BIOS + keywatch.TAIL)[0],
                         keywatch.FIRST + 4)

    def test_no_buffer(self):
        """Words that are no buffer's (a game not started yet, memory of something else): no keys,
        and nothing taken for one at the next look."""
        self.watch.take(self.gd.guest)
        for bad in (0, keywatch.FIRST + 1, keywatch.END, 0xFFFF):
            struct.pack_into("<H", self.gd.guest.mem, keywatch.BIOS + keywatch.TAIL, bad)
            self.assertEqual(self.watch.take(self.gd.guest), [], bad)
        struct.pack_into("<H", self.gd.guest.mem, keywatch.BIOS + keywatch.TAIL, keywatch.FIRST + 6)
        self.assertEqual(self.watch.take(self.gd.guest), [])
        self.watch.forget()
        self.kb.press(5)
        self.assertEqual(self.watch.take(self.gd.guest), [])


class SquaresKeyTests(unittest.TestCase):
    """R on the map in a fight: the squares shown or hidden, remembered, said."""

    def setUp(self):
        self.gd = Game()
        self.gd._word = lambda offset: struct.unpack("<h", self.gd.guest.read(DS * 16 + offset, 2))[0]
        self.on_map(1)
        self.kb = Keyboard(self.gd.guest)
        self.log = dicelog.DiceLog.__new__(dicelog.DiceLog)
        log = self.log
        log.game, log.tsr_hdr = self.gd, HDR
        log.show_squares, log.squares_shown = True, True
        log._keys, log._squares = keywatch.KeyWatch(), squares.Squares()
        log._shadows = mock.Mock(palettes=1)
        self.floated = []
        log._float = lambda thing, text, colour, now, priority=0: self.floated.append((thing, text))
        self.saved = []
        patch = mock.patch.object(dicelog, "_remember", self.saved.append)
        patch.start()
        self.addCleanup(patch.stop)
        self.assertEqual(self.press(), [])  # (the first look)

    def on_map(self, value):
        struct.pack_into("<H", self.gd.guest.mem, DS * 16 + quicksave.SCREEN_IS, value)

    def press(self, *keys):
        self.kb.press(*keys)
        return self.log._squares_key(10.0)

    def test_r_hides_and_shows(self):
        log = self.log
        log._squares.update(self.gd, HDR, True, 1)
        self.assertEqual(self.gd.on(), 1)
        self.assertEqual(self.press(keywatch.KEY_R), ["Squares in reach: hidden (R shows them)"])
        self.assertEqual((log.squares_shown, self.gd.on()), (False, 0))  # (DSCLOG's marks off at once)
        self.assertEqual(self.saved, [{"squares_shown": False}])
        self.assertEqual(self.floated, [(self.gd.turn, "Squares hidden")])
        self.assertEqual(self.press(keywatch.KEY_SHIFT_R), ["Squares in reach: shown (R hides them)"])  # (Caps Lock, Shift)
        self.assertEqual((log.squares_shown, self.gd.on()), (True, 1))
        self.assertEqual(self.saved[-1], {"squares_shown": True})
        self.assertEqual(self.floated[-1], (self.gd.turn, "Squares shown"))

    def test_only_on_the_map_in_a_fight_with_the_switch(self):
        log = self.log
        self.assertEqual(self.press(0x1E61, 0x1C0D), [])  # (other keys)
        self.on_map(2)  # (a window, a menu, a name being typed)
        self.assertEqual(self.press(keywatch.KEY_R), [])
        self.on_map(1)
        self.gd.fight = False
        self.assertEqual(self.press(keywatch.KEY_R), [])
        self.gd.fight = True
        log.show_squares = False  # (the Options tab's switch off: R is nobody's)
        self.assertEqual(self.press(keywatch.KEY_R), [])
        log.show_squares = True
        self.assertEqual(self.press(keywatch.KEY_R, keywatch.KEY_R), [])  # (twice between two looks)
        self.assertEqual((log.squares_shown, self.saved, self.floated), (True, [], []))
        self.assertEqual(len(self.press(keywatch.KEY_R)), 1)  # (and the key still works)

    def test_an_enemys_turn(self):
        """On an enemy's turn the word floats over the leader."""
        self.gd.turn = 9
        self.assertEqual(len(self.press(keywatch.KEY_R)), 1)
        self.assertEqual(self.floated, [(0, "Squares hidden")])


if __name__ == "__main__":
    unittest.main()
