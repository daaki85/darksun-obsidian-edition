"""R, F10 and Alt in Wake of the Ravager (squares.py, moveback.py, usable.py on ravlog.RAV_FIGHT_KEYS; DSCLOG2's
SQUARES, VIEW_REDRAW, RING_TAB rings and F10_PIN, site 100): the Loader's modules on the sequel's addresses, the
helper's header and site, F10_PIN run in an emulated CPU (needs nasm and unicorn, else skipped), and with DSUN_WOTR
the sequel's own bytes where it reads and patches."""

import os
import re
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, moveback, ravager, ravlog, rings, shadows, squares, usable  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(HERE, "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")
DS = 0x5000
LOAD = DS - ravager.DGROUP


class Sequel(unittest.TestCase):
    """The sequel's layout bound for each test, Shattered Lands' back after."""

    def setUp(self):
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)


class LayoutTests(Sequel):
    def test_bound_and_put_back(self):
        self.assertEqual((squares.WALK_MAP, squares.POINTS_SEG, squares.POINTS_OFF, squares.FLAGS_OFF), (0x538, 0x3C4F, 0x22E, 0x1D8))
        self.assertEqual((squares.POSITIONS, squares.POSITION_SIZE, squares.TSR_SQUARES_ON, squares.TSR_LIGHT),
                         (0x67C5, 0x25, 1924, 1926))
        self.assertEqual((moveback.START_POINTS, moveback.START_Y, moveback.START_X, moveback.MAP_RECORD, moveback.MAP_SIZE),
                         (0x4258, 0x425A, 0x425C, 0x67BB, 0x25))
        self.assertEqual((moveback.ATTACKS_OFF, moveback.COMMANDS_OFF, moveback.WALK_SEG, moveback.WALK_STEP,
                          moveback.WALK_LEFT, moveback.PINNING), (0x184, 0x1AE, 0x3F49, 0x374, 0x8A7, (69, 66)))
        self.assertEqual(shadows.TSR_VIEW_REDRAW, 1922)
        self.assertEqual((usable.DRAW_LIST, usable.DRAW_COUNT, usable.TRIGGERS_PTR, usable.HEADS_SEG, usable.MAP_OBJECT,
                          usable.HOSTILE_SIDES, usable.DOOR_TYPES, usable.BODIES), (0x67B7, 0x264E, 0x40C0, 0x3C10, 0x1B, 0xF80,
                                                                                     (41,), (2200,)))
        ravlog.restore_layout()
        self.assertEqual((squares.WALK_MAP, squares.POSITION_SIZE, moveback.MAP_SIZE, shadows.TSR_VIEW_REDRAW,
                          usable.HOSTILE_SIDES, moveback.PINNING), (0x556, 32, 32, 242, None, (game.PARALYZED_EFFECT, 51)))


class Guest:
    def __init__(self):
        self.mem = bytearray(0x110000)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class Fight:
    """The sequel's fight: party member TURN (combatant and creature 1) on square 50,50 with POINTS."""
    PARTY = game.PARTY_SIZE

    def __init__(self, points=120, flags=0x3EF, turn=1):
        self.guest, self.ds, self.load_seg, self.turn = Guest(), DS, LOAD, turn
        self.on_it = []
        self.place(50, 50)
        self.points(points, flags)
        struct.pack_into("<hHH", self.guest.mem, DS * 16 + 0x4258, points, 50 * 16 + 8, 50 * 16 + 8)

    def in_combat(self):
        return True

    def whose_turn(self):
        return self.turn

    def combatant_creature(self, c):
        return c

    def creature_name(self, c):
        return "Lex"

    def effects(self):
        return list(self.on_it)

    def place(self, col, row):
        struct.pack_into("<HH", self.guest.mem, DS * 16 + 0x67C5 + self.turn * 0x25, col * 16 + 8, row * 16 + 8)

    def points(self, points, flags):
        at = (LOAD + 0x3C4F) * 16 + self.turn * 2
        struct.pack_into("<hH", self.guest.mem, at + 0x22E, points, 0)
        struct.pack_into("<H", self.guest.mem, at + 0x1D8, flags)

    def flags(self):
        return struct.unpack_from("<H", self.guest.mem, (LOAD + 0x3C4F) * 16 + self.turn * 2 + 0x1D8)[0]


class LoaderTests(Sequel):
    def test_mover_on_the_sequels_records(self):
        """squares.mover: the member's square from the map things' feet (DS:67C5h, 25h apart), its points and
        "can walk" from 3C4Fh:22Eh and +1D8h."""
        f = Fight(points=96)
        self.assertEqual(squares.mover(f), (50, 50, 96))
        f.points(0, 0x3EE)
        self.assertEqual(squares.mover(f), (50, 50, 0))

    def test_move_back_after_the_last_step(self):
        """moveback: the last step (points 0, bit 0 cleared), then F10 (the turn's square and points back, as the
        game's F10 at 1EC05h does): the bit set again and the walk's next step and steps left forgotten (3F49h:374h
        + 1Ch a member, 8A7h + 13h)."""
        f = Fight()
        mb = moveback.MoveBack()
        self.assertIsNone(mb.update(f, True))
        f.place(58, 50)
        f.points(0, 0x3EE)
        self.assertIsNone(mb.update(f, True))
        walk = (LOAD + 0x3F49) * 16
        f.guest.mem[walk + 0x374 + 0x1C] = 7
        f.guest.mem[walk + 0x8A7 + 0x13:walk + 0x8A7 + 0x15] = b"\x05\x00"
        f.place(50, 50)
        f.points(120, 0x3EE)  # (the game's F10)
        self.assertEqual(mb.update(f, True), "F10: Lex's move taken back (can walk again)")
        self.assertEqual(f.flags(), 0x3EF)
        self.assertEqual((f.guest.mem[walk + 0x374 + 0x1C], f.guest.mem[walk + 0x8A7 + 0x13:walk + 0x8A7 + 0x15]),
                         (0xFF, b"\0\0"))

    def test_no_walk_given_to_the_pinned_or_after_an_attack(self):
        for case in ("Paralyzed", "Cannot Move", "attack", "walking"):
            f = Fight()
            mb = moveback.MoveBack()
            mb.update(f, True)
            f.points(0, 0x3EE)
            mb.update(f, True)
            f.points(120, 0x3EE)
            if case == "Paralyzed":
                f.on_it.append(game.Effect(1, 20, 69))
            elif case == "Cannot Move":
                f.on_it.append(game.Effect(1, 20, 66))
            elif case == "attack":
                f.guest.mem[(LOAD + 0x3C4F) * 16 + 0x1AE + 1] = 1
            else:
                f.guest.mem[DS * 16 + 0x67BB + 0x25] = moveback.WALKING
            self.assertIsNone(mb.update(f, True), case)
            self.assertEqual(f.flags(), 0x3EE, case)

    def test_foes_by_the_sequels_sides(self):
        """usable.creature_kind: a foe is a creature on a side in the game's mask 0F80h (7-11), whatever the leader's;
        the street's people (side 1) are nothing unless a talk trigger names them."""
        rec = bytearray(game.CREATURE_SIZE)
        struct.pack_into("<h", rec, 0, 40)
        rec[game.CREATURE_NAME] = ord("D")
        leader = bytearray(game.CREATURE_SIZE)
        for side, talk, want in ((7, set(), usable.FOE), (11, set(), usable.FOE), (1, set(), None), (4, set(), None),
                                 (1, {-206}, usable.PERSON)):
            rec[game.CREATURE_SIDE] = side
            struct.pack_into("<h", rec, usable.CREATURE_ID, -206)
            self.assertEqual(usable.creature_kind(bytes(rec), 9, bytes(leader), talk), want, side)
        rec[game.CREATURE_SIDE], rec[game.CREATURE_STATUS] = 7, 7  # (dead: the sequel's 7)
        self.assertIsNone(usable.creature_kind(bytes(rec), 9, bytes(leader), set()))

    def test_light_and_gold_in_the_sequels_colours(self):
        """LIGHT and the gold rings' table made from the colours past the sequel's cycling ones (1-31)."""
        dac = bytearray(768)
        for i in range(256):
            v = i // 4  # (a ramp of sand)
            dac[i * 3:i * 3 + 3] = bytes((v, v * 4 // 5, v // 2))
        from dsloader import dust
        for table in (dust.light_table(bytes(dac), squares.LIGHT_FIRST, squares.LIGHT_LAST),
                      rings.gold_table(bytes(dac), ravlog.RED_FIRST, ravlog.RED_LAST)):
            self.assertTrue(any(table))
            self.assertFalse(any(table[:32]))
            self.assertTrue(all(c == 0 or c >= 32 for c in table))


def built():
    from test_dsclog_drawing import build
    exe, sym = build(ASM)
    return exe[struct.unpack_from("<H", exe, 8)[0] * 16:], sym


@unittest.skipIf(Uc is None, "unicorn not installed")
class HelperTests(unittest.TestCase):
    TSR, SS = 0x1000, 0x4000

    @classmethod
    def setUpClass(cls):
        cls.image, cls.sym = built()

    def test_header(self):
        """The new fields past the quick saves' (+1922 on), RING_TAB's and LIGHT's offsets in the far block, the code
        resident."""
        hdr = self.sym["hdr"]
        for name, at in (("view_redraw", ravlog.FK_VIEW_REDRAW), ("squares_on", ravlog.FK_SQUARES_ON),
                         ("light_off", ravlog.FK_LIGHT), ("square_draws", ravlog.FK_SQUARE_DRAWS),
                         ("f10_moves", ravlog.FK_F10_MOVES), ("f10_kept", ravlog.FK_F10_KEPT),
                         ("mark_draws", ravlog.FK_MARK_DRAWS), ("ring_tab_off", rings.TSR_RING_TAB)):
            self.assertEqual(self.sym[name] - hdr, at, name)
        word = lambda at: struct.unpack_from("<H", self.image, hdr + at)[0]
        self.assertEqual(word(ravlog.FK_LIGHT), self.sym["FAR_LIGHT"])
        self.assertEqual(word(rings.TSR_RING_TAB), self.sym["FAR_RING_TAB"])
        self.assertEqual(self.sym["FAR_SC"] - self.sym["FAR_RING_TAB"], rings.THINGS)
        for routine in ("f10_pin", "squares_pass", "ring_at", "redraw_tick", "extras_wanted"):
            self.assertLess(self.sym[routine], self.sym["resident_end"], routine)

    def run_pin(self, effects):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(self.TSR * 16, self.image)
        mu.mem_write(self.TSR * 16 + 0xFFF0, b"\xf4" * 16)
        mu.mem_write(DS * 16 + 0x426D, struct.pack("<H", 2))
        base = (LOAD + 0x3E71) * 16 + 0x24D
        for i, (owner, eff) in enumerate(effects):
            mu.mem_write(base + i * 10, struct.pack("<hhhBBBB", owner, owner, 0, eff, 0, 0, 0))
        mu.mem_write(DS * 16 + 0x2100, struct.pack("<H", len(effects)))
        mu.mem_write(self.SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, self.TSR, 0x2))  # (the INT's IP, CS, flags)
        for name, value in dict(cs=self.TSR, ds=DS, ss=self.SS, esp=0x7F0, eflags=0x2, eax=0x7700).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        try:
            mu.emu_start(self.TSR * 16 + self.sym["f10_pin"], 0, count=5000)
        except Exception:
            pass
        return mu.reg_read(r.UC_X86_REG_IP) - 1 - 0xFFF0, mu.reg_read(r.UC_X86_REG_AX)  # (past the HLT)

    def test_f10_pin(self):
        """F10_PIN: AL 0 (standing still) jumps to the move taken back (6 on: 1EC3Fh from the NOPs at 1EC39h) unless the
        member on its turn is Paralyzed (69) or Cannot Move (66); AL 1 (walking) never; AH zeroed as the game's."""
        self.assertEqual(self.run_pin([]), (6, 0))
        self.assertEqual(self.run_pin([(1, 69), (3, 66)]), (6, 0))  # (another's)
        self.assertEqual(self.run_pin([(2, 66)]), (0, 0))
        self.assertEqual(self.run_pin([(0, 5), (2, 13), (2, 69)]), (0, 0))


class PatchTests(unittest.TestCase):
    def test_site(self):
        p = next(p for p in ravager.PATCHES if p.name == "f10_pin")
        self.assertEqual((p.offset, p.original.hex(), p.replacement),
                         (0x1EC36, "b4000bc07403", bytes((0xCD, ravager.VEC_SITE, 100, 0x90, 0x90, 0x90))))
        src = open(ASM).read()
        self.assertRegex(src, r"\n        dw f10_pin +; 100 SITE_F10_PIN")
        scroll = src[src.index("\nprobe_scroll:"):]
        self.assertIn("call redraw_tick", scroll[:scroll.index("iret")])
        self.assertIn("F10_TO_MOVE equ 0x1EC3F - 0x1EC39", src)

    @unittest.skipUnless(WOTR, "DSUN_WOTR (the sequel's folder) not given")
    def test_the_games_bytes(self):
        """F10 (from the map's key table at 1F091h: F10's entry 0D75h, its code's segment 1DE90h), its turn's start
        words and the standing-still test, the step routine's points and flags, the pin's effects."""
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        keys = struct.unpack_from("<24H", exe, 0x1F091)
        self.assertEqual(struct.unpack_from("<24H", exe, 0x1F091 + 0x30)[keys.index(0x4400)] + 0x1DE90, 0x1EC05)
        self.assertNotIn(0x1372, keys)  # (no R among the map's keys)
        self.assertEqual(exe[0x1EC2C:0x1EC3F], bytes.fromhex("ff366d42900ee8c70759b4000bc07403e94d04"))
        self.assertEqual(exe[0x1EC3F:0x1EC4B], bytes.fromhex("ff365a42ff365c42ff366d42"))  # (the turn's y, x)
        self.assertEqual(exe[0x1EC66:0x1EC74], bytes.fromhex("b84f3c8b1658428ec02689972e02"))  # (its points back)
        self.assertEqual(exe[0x1F3FC:0x1F40A], bytes.fromhex("558bec8b5e066bdb25f687bb6720"))  # (standing still)
        self.assertEqual(exe[0x5D8C9:0x5D8CE], bytes.fromhex("2629872e02"))
        self.assertEqual(exe[0x5D8F1:0x5D8F7], bytes.fromhex("2683a7d801fe"))
        self.assertEqual(exe[0x826F6:0x82702], bytes.fromhex("837e0a457406837e0a42751c"))
        self.assertEqual(exe[0x4D551:0x4D559], bytes((10, 14) * 4))  # (the steps' costs, DS:0551h)


if __name__ == "__main__":
    unittest.main()
