"""A polearm's reach (Weapon traits, game.RULE_CAHULAKS; DSCLOG's REACH): the combatant distance routine's
end (REACH_SITE, 2211Fh) runs in Unicorn at the game's bytes: a distance of 2 made 1 for the game's melee
tests when the attacker's hands hold a polearm and no other weapon; and, with DSUN.EXE beside the game's
GPLDATA.GFF, the callers it knows checked against the game's code."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gamepatch, specialize  # noqa: E402

import test_cahulaks as tc  # noqa: E402
import test_dsclog as td  # noqa: E402

try:
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    r = None

GAME_DS, SS, BP = td.GAME_DS, td.SS, td.BP
RULE = 8192                 # RULES_HI's RULE_HI_CAHULAKS
TYPES = 0xB000              # (the item types here)
OVERLAY = 0xD000            # (overlay 612Eh's code, loaded here)
POLEARM, METAL_POLEARM, LONG_SWORD, SHIELD, BOW = 19, game.METAL_POLEARM_TYPE, 81, 4, 1
RIGHT, LEFT, MISSILE, PACK = 3, 10, 2, 0xFF
# The distance routine's melee callers: (DSUN.EXE's segment, the way back's IP), and DSUN.EXE's offset
RESIDENT = ((0x1587, 0x2B7A), (0x1587, 0x0AC5), (0x1587, 0x04B8), (0x1587, 0x1C36), (0x1A0A, 0x3071),
            (0x1A0A, 0x14A2))
OVERLAY_BASE = 0x56CC0      # (overlay 612Eh's code in DSUN.EXE: 612E:22C6h is 58F86h)
OVERLAY_RETS = (0x0DA7, 0x1229)
# ... and the callers left alone (the call's offset in DSUN.EXE): an ambush's, the spells', the rest
OTHERS = (0x2013C, 0x56E1F, 0x59FBE, 0x7AEC6, 0x20924, 0x209AF, 0x209C5, 0x209E3)
LINE_SEG = (GAME_DS - 0x4356 + 0x898) & 0xFFFF  # (898:00A4h, the game's line test, as loaded here)
LINE_ARGS, LINE_RESULT = 0x200, 0x20C           # (the stub's: the six arguments it was given, its answer)


def file_offset(seg, ip):
    return 0x5400 + seg * 16 + ip


def load_tests(loader, tests, pattern):
    suite = loader.loadTestsFromTestCase(LoaderTests)
    suite.addTests(ReachTests(name) for name in sorted(vars(ReachTests)) if name.startswith("test_"))
    return suite


class LoaderTests(unittest.TestCase):
    def test_patch(self):
        p = next(x for x in gamepatch.PATCHES if x.name == "polearm_reach")
        self.assertEqual((p.offset, p.original.hex()), (0x2211F, "8b46ea"))
        self.assertEqual(p.replacement, bytes((0xCD, 0x98, gamepatch.REACH_SITE)))
        self.assertEqual(gamepatch.REACH_SITE, gamepatch.NS_IMAGE + 111)
        self.assertIn(("cahulaks", game.RULE_CAHULAKS), game.RULE_SETTINGS)

    def test_polearm_kind(self):
        """The polearms are kind_of_type's 10 (the kind + 1), and no other type is."""
        kind = specialize.KINDS.index("polearm")
        self.assertEqual(kind + 1, 10)
        self.assertEqual(sorted(t for t, k in specialize.KIND_OF_TYPE.items() if k == kind), [19, 111, METAL_POLEARM])

    @unittest.skipUnless(os.environ.get("DSUN_GPLDATA"), "DSUN_GPLDATA (the game's GPLDATA.GFF) not given")
    def test_game_types(self):
        """IT1R: the polearms melee weapons (flags 1), the shields none (4: neither 1 nor 2), the bow a
        missile weapon."""
        from dsloader import gff
        with open(os.environ["DSUN_GPLDATA"], "rb") as f:
            types = gff.read_gff(f.read())[("IT1R", 1)]
        flags = lambda t: types[t * 20]  # noqa: E731
        for t in (19, 111):
            self.assertEqual(flags(t) & 3, 1, t)
        for t in (4, 16, 34, 83):
            self.assertEqual(flags(t) & 7, 4, t)
        self.assertEqual(flags(BOW) & 3, 2)

    @unittest.skipUnless(os.environ.get("DSUN_GPLDATA"), "DSUN_GPLDATA (the game's GPLDATA.GFF) not given")
    def test_callers_in_the_game(self):
        """DSUN.EXE's code: the routine's end at 2211Fh; each melee caller a call to 1A0A:2BA5h whose
        result is compared with 1 (the AI's two: put in [BP-0Ah]); the overlay's two ways back with the
        code REACH_CALLER reads; every call of the routine one of these or one left alone."""
        exe = os.path.join(os.path.dirname(os.environ["DSUN_GPLDATA"]), "DSUN.EXE")
        if not os.path.exists(exe):
            self.skipTest("no DSUN.EXE beside GPLDATA.GFF")
        with open(exe, "rb") as f:
            data = f.read()
        self.assertEqual(data[0x2211F:0x22126].hex(), "8b46ea5f5ec9cb")
        self.assertEqual(data[file_offset(0x898, 0xA4):file_offset(0x898, 0xA4) + 6].hex(), "558bec1e5657")  # (the line test,
        self.assertEqual(data[0x1B700:0x1B705].hex(), "9aa4009808")                                        # the click's)
        start = file_offset(0x1A0A, 0x2BA5)
        self.assertEqual(start, 0x22045)
        seen = set()
        for seg, ip in RESIDENT:
            at = file_offset(seg, ip)
            if seg == 0x1A0A:   # (push cs / call near)
                self.assertEqual(data[at - 4:at - 2].hex(), "0ee8")
                self.assertEqual(at + struct.unpack_from("<h", data, at - 2)[0], start)
                seen.add(at - 4)
            else:
                self.assertEqual(data[at - 5:at].hex(), "9aa52b0a1a")
                seen.add(at - 5)
            self.assertEqual(data[at:at + 3].hex(), "83c404")
            after = data[at + 3:at + 10]
            self.assertTrue(after.startswith(bytes.fromhex("3d0100")) or after.startswith(bytes.fromhex("8bd083fa01"))
                            or after.startswith(bytes.fromhex("a36c49")), (hex(seg), hex(ip)))
        for ip in OVERLAY_RETS:
            at = OVERLAY_BASE + ip
            self.assertEqual(data[at - 5:at - 2].hex(), "9aa52b")
            self.assertEqual(data[at:at + 6].hex(), "83c4048946f6")
            seen.add(at - 5)
        self.assertEqual(data[OVERLAY_BASE + 0x22C6:OVERLAY_BASE + 0x22C6 + 2].hex(), "26f7")  # (PROBE_WORN's site)
        calls = set()
        for at in range(len(data) - 5):
            if data[at] == 0x9A and data[at + 1:at + 3] == b"\xa5\x2b" and data[at + 3:at + 5] in (b"\x0a\x1a", b"\xa0\x00"):
                calls.add(at)
            elif data[at:at + 2] == b"\x0e\xe8" and at + 4 + struct.unpack_from("<h", data, at + 2)[0] == start \
                    and file_offset(0x1A0A, 0) <= at < file_offset(0x1A0A, 0x10000):
                calls.add(at)
        self.assertEqual(calls, seen | set(OTHERS))
        self.assertFalse(seen & set(OTHERS))


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class ReachTests(tc.CahulaksTests):
    def setUp(self):
        super().setUp()
        mu = self.mu
        mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, TYPES))
        for t, flags in ((POLEARM, 1), (METAL_POLEARM, 1), (LONG_SWORD, 1), (SHIELD, 4), (BOW, 0x0A), (102, 0)):
            mu.mem_write(TYPES * 16 + t * 20, bytes((flags,)))
        for ip in OVERLAY_RETS:  # (the overlay's code around its two ways back, as loaded)
            mu.mem_write(OVERLAY * 16 + ip - 5, bytes.fromhex("9aa52b0010") + bytes.fromhex("83c4048946f6"))
        self.combatant(6, 3)
        # the line test: a stub keeping its six arguments at LINE_ARGS and answering LINE_RESULT's word
        code = bytes.fromhex("558bec")
        for n in range(6):
            code += bytes.fromhex("8b46") + bytes((6 + 2 * n,)) + bytes.fromhex("2ea3") + struct.pack("<H", LINE_ARGS + 2 * n)
        code += bytes.fromhex("2ea1") + struct.pack("<H", LINE_RESULT) + bytes.fromhex("5dcb")
        mu.mem_write(LINE_SEG * 16 + 0xA4, code)
        self.line(0)
        for thing, x, y in ((6, 100, 40), (20, 102, 41)):  # (sixteenths: squares 100,40 and 102,41)
            mu.mem_write(GAME_DS * 16 + 0x669D + thing * 32, struct.pack("<HH", x * 16 + 5, y * 16 + 9))

    def line(self, result):
        self.mu.mem_write(LINE_SEG * 16 + LINE_RESULT, struct.pack("<H", result))
        self.mu.mem_write(LINE_SEG * 16 + LINE_ARGS, bytes(12))

    def hands(self, *items, creature=3):
        """Creature CREATURE's items, (type, slot) each: the first two in its list +0Ah, the rest in +0Ch."""
        mu = self.mu
        rec = tc.CREATURES * 16 + creature * 0x3A
        held, pack = items[:2], items[2:]
        lists = []
        for thing, group, first in ((400, held, 20), (401, pack, 30)):
            if not group:
                lists.append(0x270F)
                continue
            mu.mem_write(self.THINGS + thing * 3, struct.pack("<BH", 1, first))
            for n, (kind, slot) in enumerate(group):
                item = bytearray(0x15)
                struct.pack_into("<H", item, 4, first + n + 1 if n + 1 < len(group) else 0x270F)
                struct.pack_into("<H", item, 0x0A, kind)
                item[0x11] = slot
                mu.mem_write(tc.ITEMS * 16 + (first + n) * 0x15, bytes(item))
            lists.append(thing)
        mu.mem_write(rec + 8, struct.pack("<HHH", 0x270F, *lists))

    def distance(self, dist=2, rules=RULE, back=(0x1587, 0x2B7A), attacker=6):
        """REACH_SITE's AX, with [BP-16h] DIST, the way back BACK (DSUN.EXE's segment and IP, or
        (OVERLAY, IP) for the overlay's), the attacker ATTACKER at [BP+6]."""
        self.rules_hi(rules)
        seg, ip = back
        cs = seg if seg == OVERLAY else GAME_DS - (0x4356 - seg)
        self.frame(m16=dist, p2=ip, p6=attacker, p8=20)
        self.mu.mem_write(SS * 16 + BP + 4, struct.pack("<H", cs))
        self.assertEqual(self.where("polearm_reach", (), eax=0xBEEF, ebx=0x1111, ecx=0x2222, edx=0x3333,
                                    esi=0x4444, edi=0x5555, es=0x6666), "end")
        mu = self.mu
        self.assertEqual([mu.reg_read(getattr(r, "UC_X86_REG_" + x)) for x in ("BX", "CX", "DX", "SI", "DI", "ES")],
                         [0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666])
        return mu.reg_read(r.UC_X86_REG_AX)

    def test_polearm_alone(self):
        """A polearm in either hand, the other empty, from every melee caller: 2 is 1; 1 and 3 kept."""
        for kind in (POLEARM, METAL_POLEARM):
            for slot in (RIGHT, LEFT):
                self.hands((kind, slot))
                for back in RESIDENT + tuple((OVERLAY, ip) for ip in OVERLAY_RETS):
                    self.assertEqual(self.distance(back=back), 1, (kind, slot, back))
                self.assertEqual(self.distance(1), 1)
                self.assertEqual(self.distance(3), 3)
                self.assertEqual(self.distance(999), 999)

    def test_shield_and_missile_slot(self):
        """A shield in the other hand, a bow in the missile slot, a long sword in the pack: reach still."""
        self.hands((POLEARM, RIGHT), (SHIELD, LEFT))
        self.assertEqual(self.distance(), 1)
        self.hands((POLEARM, LEFT), (BOW, MISSILE), (LONG_SWORD, PACK), (SHIELD, PACK))
        self.assertEqual(self.distance(), 1)
        self.hands((102, LEFT), (POLEARM, RIGHT))  # (no weapon: a ring's type in the hand)
        self.assertEqual(self.distance(), 1)

    def test_another_weapon(self):
        """Another weapon in a hand (a long sword, a second polearm, a bow), or no polearm: 2 kept."""
        for items in (((POLEARM, RIGHT), (LONG_SWORD, LEFT)), ((LONG_SWORD, RIGHT), (POLEARM, LEFT)),
                      ((POLEARM, RIGHT), (METAL_POLEARM, LEFT)), ((POLEARM, RIGHT), (BOW, LEFT)),
                      ((LONG_SWORD, RIGHT),), ((SHIELD, LEFT),), ((POLEARM, PACK),), ((POLEARM, MISSILE),), ()):
            self.hands(*items)
            self.assertEqual(self.distance(), 2, items)

    def test_wall_between(self):
        """The game's line test asked from the attacker's square to the target's (x, y, 0 each): a wall
        on the line (its -1) keeps 2."""
        self.hands((POLEARM, RIGHT))
        self.assertEqual(self.distance(), 1)
        self.assertEqual(struct.unpack("<6H", self.mu.mem_read(LINE_SEG * 16 + LINE_ARGS, 12)), (100, 40, 0, 102, 41, 0))
        self.line(0xFFFF)
        for back in RESIDENT:
            self.assertEqual(self.distance(back=back), 2, back)
        self.line(0)
        self.assertEqual(self.distance(back=(0x1A0A, 0x3071)), 1)
        self.hands((POLEARM, RIGHT), (LONG_SWORD, LEFT))
        self.line(0)
        self.assertEqual(self.distance(), 2)
        self.assertEqual(bytes(self.mu.mem_read(LINE_SEG * 16 + LINE_ARGS, 12)), bytes(12))  # (not asked)

    def test_other_callers(self):
        """Another caller's way back (an ambush's, a spell's, a resident IP in another segment, an overlay
        IP whose code isn't the AI's), the rule off, or an attacker that is no creature: 2 kept."""
        self.hands((POLEARM, RIGHT))
        for back in ((0x1A0A, 0x0CA0), (0x1A0A, 0x1488), (0x1587, 0x14A2), (0x1A0A, 0x2B7A), (OVERLAY, 0x0164)):
            self.assertEqual(self.distance(back=back), 2, back)
        self.mu.mem_write(OVERLAY * 16 + 0x1229, b"\x90")
        self.assertEqual(self.distance(back=(OVERLAY, 0x1229)), 2)
        self.assertEqual(self.distance(back=(OVERLAY, 0x0DA7)), 1)
        self.mu.mem_write(OVERLAY * 16 + 0x0DA7 - 4, b"\x00")
        self.assertEqual(self.distance(back=(OVERLAY, 0x0DA7)), 2)
        self.assertEqual(self.distance(rules=0), 2)
        self.assertEqual(self.distance(rules=0xFFFF ^ RULE), 2)
        self.assertEqual(self.distance(attacker=7), 2)  # (no creature)
        self.assertEqual(self.distance(attacker=600), 2)  # (past the map's things)


if __name__ == "__main__":
    unittest.main()
