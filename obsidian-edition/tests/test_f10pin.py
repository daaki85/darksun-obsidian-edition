"""F10 in a fight leaves a pinned member where it is (DSCLOG's F10_PIN, gamepatch "f10_pin"): the game's
F10 (DSUN.EXE 1B83Ah) puts the member on its turn back on the turn's first square with the turn's
points once it stands still; the site, over its "or ax,ax / jz 1B872h" (1B86Bh), makes that jump only
for a member with neither Paralyzed (34) nor Stuck (51) on it. Run in Unicorn at the game's bytes."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gamepatch, moveback  # noqa: E402

import test_cahulaks as tc  # noqa: E402
import test_dsclog as td  # noqa: E402

try:
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    r = None

GAME_DS = td.GAME_DS
WHOSE_TURN = 0x4979
PARALYZED, STUCK = 34, 51
MOVE = 0x1B872 - 0x1B86E  # (the jump's target: the move taken back, less the address after the site's number)


def load_tests(loader, tests, pattern):
    suite = loader.loadTestsFromTestCase(LoaderTests)
    suite.addTests(F10PinTests(name) for name in sorted(vars(F10PinTests)) if name.startswith("test_"))
    return suite


class LoaderTests(unittest.TestCase):
    def test_patch(self):
        p = next(x for x in gamepatch.PATCHES if x.name == "f10_pin")
        self.assertEqual((p.offset, p.original.hex()), (0x1B86B, "0bc07403"))
        self.assertEqual(p.replacement, bytes((0xCD, 0x98, gamepatch.F10_PIN_SITE, 0x90)))
        self.assertEqual(gamepatch.F10_PIN_SITE, gamepatch.NS_IMAGE + 122)
        self.assertEqual(set(moveback.PINNING), {PARALYZED, STUCK})  # (the Loader's mend: the same two)

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "DSUN_OBJECTS (the game's files) not given")
    def test_the_games_bytes(self):
        """In DSUN.EXE the site sits after F10's call of the standing-still test (1BF9Dh) and before
        the "jmp 1BC55h" (the key's end) that the jump skips to the move (1B872h: the turn's first
        square pushed)."""
        exe = os.path.join(os.path.dirname(os.environ["DSUN_OBJECTS"]), "DSUN.EXE")
        if not os.path.exists(exe):
            self.skipTest("no DSUN.EXE beside DSUN_OBJECTS")
        with open(exe, "rb") as f:
            data = f.read()
        self.assertEqual(data[0x1B861:0x1B872].hex(), "ff367949900ee83307590bc07403e9e303")
        self.assertEqual(data[0x1B872:0x1B87A].hex(), "ff366649ff366849")


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class F10PinTests(tc.CahulaksTests):
    def f10(self, still=0, turn=2, effects=()):
        """The site with AX 1BF9Dh's answer (0 standing still) and the member on its turn: True if it went
        on to the move, False to the key's end. AX and the other registers back as they were."""
        self.effects(*effects)
        self.mu.mem_write(GAME_DS * 16 + WHOSE_TURN, struct.pack("<H", turn))
        regs = dict(eax=still, ebx=0x1234, ecx=0x5678, edx=0x9ABC, esi=0x1111, edi=0x2222)
        to = self.where("f10_pin", (MOVE,), **regs)
        self.assertIn(to, ("end", MOVE))
        for reg, value in regs.items():
            self.assertEqual(self.mu.reg_read(getattr(r, "UC_X86_REG_" + reg[1:].upper())), value & 0xFFFF, reg)
        return to == MOVE

    def test_the_games_move(self):
        """Standing still with no pin: the game's move, for each member; walking: the key's end."""
        for turn in range(4):
            self.assertTrue(self.f10(turn=turn), turn)
            self.assertFalse(self.f10(still=1, turn=turn), turn)

    def test_pinned_left_where_it_is(self):
        """Paralyzed or Stuck on the member on its turn: no move, among other effects too."""
        for effect in (PARALYZED, STUCK):
            self.assertFalse(self.f10(effects=((2, effect),)), effect)
            self.assertFalse(self.f10(effects=((0, 4), (2, 16), (2, effect), (3, 2))), effect)
            self.assertFalse(self.f10(still=1, effects=((2, effect),)), effect)

    def test_a_pin_on_another(self):
        """A pin on another combatant (a member or a foe), or another effect on this one: the game's."""
        for effect in (PARALYZED, STUCK):
            self.assertTrue(self.f10(effects=((1, effect), (3, effect), (20, effect))), effect)
        self.assertTrue(self.f10(effects=((2, 16), (2, 47), (2, 2))))  # (Enlarged, Slowed, ...)


if __name__ == "__main__":
    unittest.main()
