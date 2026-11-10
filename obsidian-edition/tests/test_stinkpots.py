"""The staff sling's stinkpots (game.RULE_STINKPOTS; DSCLOG's STINKPOTS): the staff sling's dice made
1d3 with the rule (STINK_SIDES, at the type table's read and each pass of the main loop), a hit's save
against poison or Nauseated (STINK_HIT, from CAH_HIT's site), its -2 to hit (NS_HIT) and its name on the
Effects screen (NS_ENTRY), all run in Unicorn; and the Loader's side: the rule, the effect, the dice log's
lines."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dicelog, game, gamepatch  # noqa: E402

import test_cahulaks as tc  # noqa: E402
import test_dsclog as td  # noqa: E402
import test_dsclog_drawing as tdd  # noqa: E402

try:
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    r = None

GAME_DS, SS, CALLER, TSR, BP, IF = td.GAME_DS, td.SS, td.CALLER, td.TSR, td.BP, td.IF
RULE = 2                    # RULES' RULE_STINKPOTS (the low word)
NAUSEATED = 75
SAVE_LOG, SAVE_COUNT = 0x400, 0x5FE     # (the stubs' logs: DS offsets, a call's words each 20h)
ADD_LOG, ADD_COUNT = 0x480, 0x5FC
SAVE_STUB = 0x42AB          # 5B8h's stub segment (DSUN.EXE): A2h undead, 66h the damage share, 2Fh the save
ADD_STUB = 0x428F           # 598h's: 3Eh adds an effect


def load_tests(loader, tests, pattern):  # (only this file's: not the classes', inherited, again)
    suite = loader.loadTestsFromTestCase(LoaderTests)
    suite.addTests(loader.loadTestsFromTestCase(DiceLogTests))
    for cls in (StinkHitTests, StinkSidesTests, StinkEffectTests):
        suite.addTests(cls(name) for name in sorted(vars(cls)) if name.startswith("test_"))
    return suite


class LoaderTests(unittest.TestCase):
    def test_rule(self):
        """Bit 2 of the rules (unused since boots' movement), on unless unticked, no other rule's."""
        self.assertEqual(game.RULE_STINKPOTS, RULE)
        self.assertIn(("stinkpots", game.RULE_STINKPOTS), game.RULE_SETTINGS)
        self.assertTrue(game.rules_from_settings({}) & game.RULE_STINKPOTS)
        self.assertFalse(game.rules_from_settings({"stinkpots": False}) & game.RULE_STINKPOTS)
        others = [bit for key, bit in game.RULE_SETTINGS if key != "stinkpots"]
        self.assertFalse(any(bit & RULE for bit in others))

    def test_effect(self):
        """Nauseated: 75, past the game's 74 (its bits reach 79: 10 bytes), -2 to hit in the attack's sum."""
        self.assertEqual(game.STINK_EFFECT, NAUSEATED)
        self.assertEqual(game.EFFECT_NAMES[NAUSEATED], "Nauseated")
        self.assertIn("-2 to hit", game.EFFECT_RULES[NAUSEATED])
        self.assertIn((NAUSEATED, -2), game.HIT_EFFECTS)
        self.assertEqual((game.STINK_DICE, game.SLING_DICE, game.STAFF_SLING_TYPE), ((1, 3), (1, 4), 0))

    def test_asm_numbers(self):
        """DSCLOG's numbers are the Loader's."""
        asm = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog.asm")
        with open(asm, encoding="latin-1") as f:
            text = f.read()
        for line in ("RULE_STINKPOTS equ 2 ", "STINK_EFFECT equ 75", "STINK_SAVE   equ 176", "STAFF_SLING  equ 0 ",
                     "STINK_SIDES  equ 3 ", "MN_STINK     equ 11", "MN_NAUSEA    equ 12"):
            self.assertIn(line, text)
        self.assertEqual(game.STINK_SAVE_POWER, 176)
        self.assertEqual((dicelog.MANUAL_STINK, dicelog.MANUAL_NAUSEA), (11, 12))

    def test_staff_sling_kind(self):
        """Type 0 is the staff sling: its only type (specialize.KINDS), no large dice of its own."""
        from dsloader import sizes, specialize
        kind = specialize.KINDS.index("staff sling")
        self.assertEqual([t for t, k in specialize.KIND_OF_TYPE.items() if k == kind], [0])
        self.assertIsNone(sizes.LARGE_DICE[kind])
        self.assertEqual(specialize.next_die(3), 4)  # (grand mastery: 1d4)

    @unittest.skipUnless(os.environ.get("DSUN_GPLDATA"), "DSUN_GPLDATA (the game's GPLDATA.GFF) not given")
    def test_game_records(self):
        """The game's staff sling (IT1R's type 0, in GPLDATA.GFF): missile only (+0 2), crushing (+2 8),
        1d4 (sides +0Ch, count +0Dh, bonus +0Eh), which STINK_SIDES makes 1d3; and power 176's spell record
        (DSUN.EXE, beside it) a save against paralysis/poison/death (+1Fh 21h), its d20 not doubled."""
        from dsloader import gff
        with open(os.environ["DSUN_GPLDATA"], "rb") as f:
            sling = gff.read_gff(f.read())[("IT1R", 1)][:20]
        self.assertEqual(sling.hex(), "020008001400fa00050c0f0204010040f11e0001")
        self.assertEqual((sling[0], sling[2], sling[0x0D], sling[0x0C], sling[0x0E]), (2, 8, 1, 4, 0))
        exe = os.path.join(os.path.dirname(os.environ["DSUN_GPLDATA"]), "DSUN.EXE")
        if not os.path.exists(exe):
            return
        with open(exe, "rb") as f:
            data = f.read()
        record = data[0x41F70 + 0x20 * 176:0x41F70 + 0x20 * 177]
        self.assertEqual(record[0x1F], 0x21)
        self.assertFalse(struct.unpack_from("<H", record, 0x1A)[0] & 0x86)


class FakeGame:
    def __init__(self):
        self.rules = game.RULE_STINKPOTS

    def combatant_name(self, c):
        return {1: "Lex", 20: "Templar", 21: "Skeleton"}.get(c, f"#{c}")

    def spell_name(self, s):
        return {176: "Poison (10 damage)"}.get(s, f"spell {s}")

    def spell_rules(self, s):
        return None

    def save_modifiers(self, *a):
        return [(1, "ring")]

    def spell_damage(self, s):
        return None


class DiceLogTests(unittest.TestCase):  # (its _save_line's other ways: the dice log's tests)
    """The lines: the stinkpot named in the game's save line (power 176's, named 'Poison (10 damage)'
    otherwise), the nausea's rounds after a failure, nothing more after a save, and the spared."""

    def log(self):
        log = dicelog.DiceLog.__new__(dicelog.DiceLog)
        log._stink, log._last_damage = None, None
        log.game = FakeGame()
        log._name = log.game.combatant_name
        return log

    def manual(self, log, what, *args):
        class E:
            raw = what

            def arg(self, at):
                return dict(zip((6, 8, 0x0A, 0x0C), args)).get(at)
        return log._manual(E())

    def test_failed(self):
        log = self.log()
        self.assertEqual(self.manual(log, dicelog.MANUAL_STINK, 20, 1, 0, 0), [])
        line = log._save_line(20, 1, 176, 1, 7, 8, 14)
        self.assertEqual(line, "Templar's saving throw vs a stinkpot from Lex (paralysis/poison/death): d20 = 7 +1 ring"
                               " = 8, needs 14 (40% to save) -> failed: nauseated")
        self.assertEqual(self.manual(log, dicelog.MANUAL_NAUSEA, 20, 1, 2, 3),
                         ["    Lex's stinkpot: Templar is nauseated, -2 to hit for 1d3+1 = 2 + 1 = 3 rounds"])
        self.assertIsNone(log._stink)
        # (the next save against power 176 on it is a Poisoner's: named as ever)
        self.assertIn("vs Poison (10 damage)", log._save_line(20, 1, 176, 1, 7, 8, 14))

    def test_saved(self):
        log = self.log()
        self.manual(log, dicelog.MANUAL_STINK, 20, 1, 0, 0)
        self.assertTrue(log._save_line(20, 1, 176, 1, 15, 16, 14).endswith("-> saved"))
        self.assertEqual(self.manual(log, dicelog.MANUAL_NAUSEA, 20, 1, 0, 0), [])

    def test_helpless(self):
        """A held target fails with no d20 (the game's save, before its roll): no save line came."""
        log = self.log()
        self.manual(log, dicelog.MANUAL_STINK, 20, 1, 0, 0)
        self.assertEqual(self.manual(log, dicelog.MANUAL_NAUSEA, 20, 1, 3, 4),
                         ["    Lex's stinkpot: Templar is nauseated, no saving throw (helpless), -2 to hit for "
                          "1d3+1 = 3 + 1 = 4 rounds"])

    def test_spared(self):
        log = self.log()
        self.assertEqual(self.manual(log, dicelog.MANUAL_STINK, 21, 1, 1, 0),
                         ["    Lex's stinkpot bursts on Skeleton: undead, unaffected"])
        self.assertEqual(self.manual(log, dicelog.MANUAL_STINK, 20, 1, 2, 0),
                         ["    Lex's stinkpot bursts on Templar: immune to poison, unaffected"])
        self.assertIsNone(log._stink)


def stub(seg, off, count, base, counter, ax=None):
    """The game's far routine SEG:OFF (its stub segment in DSUN.EXE): each call's first COUNT argument
    words kept at DS:BASE + 20h x the calls before it, the calls counted at DS:COUNTER; AX the word at
    DS:AX (data, not code: Unicorn keeps code it has run)."""
    ret = (b"\xa1" + struct.pack("<H", ax)).hex() if ax is not None else ""
    code = ("5589e5565751061e078d76068b3e" + struct.pack("<H", counter).hex() + "c1e70581c7"
            + struct.pack("<H", base).hex() + "b9" + struct.pack("<H", count).hex() + "f336a5ff06"
            + struct.pack("<H", counter).hex() + "07595f5e5d" + ret + "cb")
    return ((GAME_DS - (0x4356 - seg)) & 0xFFFF) * 16 + off, bytes.fromhex(code)


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class StinkHitTests(tc.CahulaksTests):
    def calls(self, base, counter, count):
        n, = struct.unpack("<H", self.mu.mem_read(GAME_DS * 16 + counter, 2))
        return [struct.unpack(f"<{count}h", self.mu.mem_read(GAME_DS * 16 + base + 0x20 * i, 2 * count))
                for i in range(n)]

    def entries(self, n):
        """The last N entries of the ring, oldest first: (kind, raw, +6, +8, +0Ah, +0Ch)."""
        hdr_off, ring = struct.unpack_from("<H", self.image, 20)[0], struct.unpack_from("<H", self.image, 16)[0]
        seq, _, size = struct.unpack("<HHH", self.mu.mem_read(TSR * 16 + hdr_off + 8, 6))
        out = []
        for k in range(n, 0, -1):
            e = td.Entry.parse(bytes(self.mu.mem_read(td.RING_SEG * 16 + ring + ((seq - k) % size) * td.Entry.SIZE,
                                                      td.Entry.SIZE)))
            out.append((e.kind, e.raw) + tuple(e.arg(at) for at in (6, 8, 0x0A, 0x0C)))
        return out

    def throw(self, d3=2, rules=RULE, kind=0, reach=2, attacker=1, undead=0, share=100, saved=0):
        """CAH_HIT after a hit with item type KIND: the game's routines stubbed (UNDEAD the undead test's
        AL, SHARE the poison's share, SAVED the save's AX); (the save's calls, the effects added, the
        records made)."""
        self.mu.mem_write(self.hdr + 170, struct.pack("<H", rules))
        self.rules_hi(0)
        self.mu.mem_write(GAME_DS * 16 + 0x5F0, struct.pack("<HHH", undead, share, saved))
        for (seg, off, count, base, counter, ax) in ((SAVE_STUB, 0xA2, 1, 0x500, 0x5FA, 0x5F0),
                                                     (SAVE_STUB, 0x66, 4, 0x520, 0x5F8, 0x5F2),
                                                     (SAVE_STUB, 0x2F, 4, SAVE_LOG, SAVE_COUNT, 0x5F4),
                                                     (ADD_STUB, 0x3E, 7, ADD_LOG, ADD_COUNT, None)):
            at, code = stub(seg, off, count, base, counter, ax)
            self.mu.mem_write(at, code)
            self.mu.mem_write(GAME_DS * 16 + counter, bytes(2))
        self.mu.mem_write(GAME_DS * 16 + self.SEED, struct.pack("<I", self.seed_for((d3, 3))))
        self.frame(p14=kind, p16=reach, p18=attacker)
        self.mu.mem_write(SS * 16 + BP - 0x15, b"\x63")
        before = self.seq()
        self.assertEqual(self.where("cahulaks_hit", ()), "end")
        self.assertEqual(self.mu.mem_read(SS * 16 + BP - 0x15, 1)[0], 0)
        made = (self.seq() - before) & 0xFFFF
        return (self.calls(SAVE_LOG, SAVE_COUNT, 4), self.calls(ADD_LOG, ADD_COUNT, 7),
                self.entries(made) if made else [])

    def test_nauseated(self):
        """A failed save: the game's save (target, thrower, power 176, level 0), then Nauseated (75)
        under Stinking Cloud (22) for 1d3+1 rounds (x 60 seconds), recorded before (kind 14, 11: a
        save follows) and after (12: the d3, the rounds)."""
        self.target(thing=20, creature=9)
        saves, added, recs = self.throw(d3=2)
        self.assertEqual(saves, [(20, 1, 176, 0)])
        self.assertEqual(added, [(20, 1, 22, NAUSEATED, 3 * 60, 0, 0)])
        self.assertEqual(recs, [(14, 11, 20, 1, 0, 0), (14, 12, 20, 1, 2, 3)])
        self.target(thing=21, creature=10)
        self.assertEqual(self.throw(d3=3)[1], [(21, 1, 22, NAUSEATED, 4 * 60, 0, 0)])

    def test_saved(self):
        self.target(thing=20, creature=9)
        saves, added, recs = self.throw(saved=1)
        self.assertEqual(len(saves), 1)
        self.assertEqual(added, [])
        self.assertEqual(recs, [(14, 11, 20, 1, 0, 0), (14, 12, 20, 1, 0, 0)])

    def test_spared(self):
        """An undead (the game's test), or one that takes none of the poison damage kind: no save, no
        effect, recorded (11: 1 undead, 2 immune)."""
        self.target(thing=20, creature=9)
        saves, added, recs = self.throw(undead=1)
        self.assertEqual((saves, added, recs), ([], [], [(14, 11, 20, 1, 1, 0)]))
        saves, added, recs = self.throw(share=0)
        self.assertEqual((saves, added, recs), ([], [], [(14, 11, 20, 1, 2, 0)]))
        self.assertEqual(self.calls(0x520, 0x5F8, 4)[0][0], 20)
        self.assertEqual(self.calls(0x520, 0x5F8, 4)[0][3], 1)  # (the poison kind)

    def test_not(self):
        """Without the rule, with another weapon, on a target the blow felled: nothing (the cahulaks'
        own way after)."""
        self.target(thing=20, creature=9)
        self.assertEqual(self.throw(rules=0), ([], [], []))
        self.assertEqual(self.throw(kind=64), ([], [], []))  # (a sling)
        self.target(thing=20, creature=9, hp=0)
        self.assertEqual(self.throw(), ([], [], []))


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class StinkSidesTests(td.TypesTests):
    """STINK_SIDES: type 0's sides 3 with the rule, the game's 4 without, at the table's read and again
    whenever it runs (the main loop's pass), only in the table read and only over a 3 or 4."""

    def rules(self, value):
        self.mu.mem_write(self.hdr + 170, struct.pack("<H", value))

    def sides(self):
        return self.mu.mem_read(self.TYPES_SEG * 16 + 0x0C, 1)[0]

    def call(self):
        _, sym = tdd.build()
        stub = TSR * 16 + 0xFFF0  # (a far stub in the helper's segment: a near call to it, RETF)
        self.mu.mem_write(stub, b"\xe8" + struct.pack("<H", (sym["stink_sides"] - (0xFFF0 + 3)) & 0xFFFF) + b"\xcb")
        self.mu.mem_write(CALLER * 16 + 0x700, bytes((0x9A,)) + struct.pack("<HH", 0xFFF0, TSR) + b"\xf4")
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, es=0x1234,
                                ebx=0x5678, eax=0x9ABC).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(CALLER * 16 + 0x700, 0, count=2000)
        self.assertEqual([self.mu.reg_read(getattr(r, "UC_X86_REG_" + n)) for n in ("ES", "BX", "AX")],
                         [0x1234, 0x5678, 0x9ABC])

    def test_read_and_switched(self):
        self.mu.mem_write(self.TYPES_SEG * 16, bytes.fromhex("020008001400fa00050c0f0204010040f11e0001"))
        self.rules(RULE)
        self.mu.mem_write(SS * 16 + BP - 4, struct.pack("<I", 2300))
        self.interrupt(td.VEC_TYPES_FILL, eax=0)
        self.assertEqual(self.sides(), 3)
        self.rules(0)
        self.call()
        self.assertEqual(self.sides(), 4)
        self.rules(RULE)
        self.call()
        self.assertEqual(self.sides(), 3)
        self.mu.mem_write(self.TYPES_SEG * 16 + 0x0C, b"\x06")  # (not the staff sling's: left alone)
        self.call()
        self.assertEqual(self.sides(), 6)
        self.mu.mem_write(self.TYPES_SEG * 16 + 0x0C, b"\x04")
        self.mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES_SEG + 1))  # (another table)
        self.call()
        self.assertEqual(self.sides(), 4)


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class StinkEffectTests(td.NewSpellTests):
    def test_to_hit(self):
        """NS_HIT: 2 off for a nauseated attacker (75: bit 3 of [BP-0Fh], the bits' last byte), whatever
        the rules; none for a nauseated target; Fogbolt's as ever beside it."""
        def run(attacker=False, target=False, fog=False):
            self.mu.mem_write(SS * 16 + BP - 0x18, bytes(0x18))
            if attacker:
                self.mu.mem_write(SS * 16 + BP - 0x0F, bytes([8]))
            if target:
                self.mu.mem_write(SS * 16 + BP - 0x05, bytes([8]))
            if fog:
                self.mu.mem_write(SS * 16 + BP - 0x15, bytes([8]))
            self.site(gamepatch.NS_HIT, esi=10)
            return self.mu.reg_read(r.UC_X86_REG_SI)
        for rules in (0, 32):
            self.rules(rules)
            self.assertEqual([run(), run(attacker=True), run(target=True)], [10, 8, 10])
        self.assertEqual(run(attacker=True, fog=True), 5)

    def test_entry(self):
        """NS_ENTRY: Nauseated (75, past the game's table of 74) is STINK_ENTRY's, after Reflected Image's
        past the spell rows: NAUSEATED, Stinking Cloud's icon (21022); the Effects screen's, the Look
        box's and a portrait's, whatever the rules."""
        effects = (GAME_DS - (0x4356 - 0x3BF6)) * 16 + 0x106
        self.mu.mem_write(effects, struct.pack("<hhhBB", 1, 0, 22, NAUSEATED, 0) + bytes(2))
        self.mu.mem_write(GAME_DS * 16 + 0x1E24, struct.pack("<H", 1))
        shown = (GAME_DS - (0x4356 - 0x3931)) * 16 + 0x25B
        table = (GAME_DS - (0x4356 - 0x3F8D)) * 16
        entry = (0x4010 - 0x3F8D) * 16 + 0x1FE
        self.mu.mem_write(shown, struct.pack("<H", 1))
        self.rules(0)
        self.site(gamepatch.NS_ENTRY_EF, eax=NAUSEATED)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), entry + 6)
        self.mu.mem_write(SS * 16 + BP + 0x0A, struct.pack("<H", 1))
        self.site(gamepatch.NS_ENTRY_LOOK, ebx=NAUSEATED)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_BX), entry + 6)
        self.site(gamepatch.NS_ENTRY_STATUS, ebx=NAUSEATED, edi=1)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_BX), entry + 6)
        self.site(gamepatch.NS_ENTRY_STATUS, ebx=17, edi=1)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_BX), 17 * 6)
        far, icon = struct.unpack("<IH", self.mu.mem_read(table + entry, 6))
        name = self.mu.mem_read((far >> 16) * 16 + (far & 0xFFFF), 10)
        self.assertEqual((bytes(name), icon), (b"NAUSEATED\0", 21022))


if __name__ == "__main__":
    unittest.main()
