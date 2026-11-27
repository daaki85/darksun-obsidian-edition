"""DSCLOG2's last ports from Shattered Lands' DSCLOG, run in an emulated CPU: EF_CHARGES (site 247: the Effects
screen's line under the pointer named with the effect's charges, SL's fix with it), ARROWS_FORBID (in CU_SITE,
site 19: only a Spellarcher readies spell arrows) and the spell arrows' cast sound (ARROWS_ASK: the game's sound
routine, B8h:0A22h, with Vampiric Touch's 6Eh). Needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, ravager, ravlog  # noqa: E402
import test_ravkits  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = test_ravkits.ASM
TSR, SS, GDS, CODE = 0x1000, 0x4000, 0x6000, 0x3000
NAMES = 0x5555  # (the effects' records' segment, as the code's "push 318h" has it fixed up)
EFFECTS = GDS - (0x47E0 - 0x3E71)  # (the active effects' segment: DSCLOG2's EFFECTS_GAP)
USE_WHO = GDS + 0x3E71 - 0x47E0  # (370h: the character on show at 0B44h)
EVENTS = 0x5800
WAY_BACK = 0x0100
AP_ARROW_NAME = 256 + 42  # (DSCLOG2's: the spell arrows' names, Burning to Vampiric)
WOTR = os.environ.get("DSUN_WOTR")


def _word(mu, at):
    return struct.unpack("<H", bytes(mu.mem_read(at, 2)))[0]


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class EffectChargesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def line(self, effect, records=(), events=(), segment=NAMES, offset=None, member=2, stats=None, hi=0, stale=False):
        """The name's far pointer the cells' handler gets for EFFECT's record (offset EFFECT x 31 in SEGMENT)
        with these active effects (thing, spell, effect, handle, charges) and timed events (kind, thing,
        handle): the text there, and the three words pushed under it."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(CODE * 16, b"\xF4" * 0x400)
        mu.mem_write(CODE * 16 + WAY_BACK - 6, struct.pack("<H", NAMES))  # ("push 318h", as fixed up)
        mu.mem_write(NAMES * 16 + 5 * 31, b"Armor\0")
        mu.mem_write(NAMES * 16 + 13 * 31, b"Detect Invisible\0")
        mu.mem_write(NAMES * 16 + 46 * 31, b"Mirror Image\0")
        for n, name in ((6, b"Barkskin"), (32, b"Enlarged"), (40, b"Flesh Armor"), (104, b"Magical Vestments")):
            mu.mem_write(NAMES * 16 + n * 31, name + b"\0")
        hdr = TSR * 16 + self.sym["hdr"]
        mu.mem_write(hdr + test_ravkits.RULES_HI, struct.pack("<H", hi))
        mu.mem_write(0x46C, struct.pack("<H", 500 if stale else 30))  # (the BIOS timer: the Loader's stamp 0)
        if stats is not None:  # (EF_STATS: the Loader's rows)
            mu.mem_write(TSR * 16 + self.sym["ef_stats"], bytes(stats))
        mu.mem_write(GDS * 16 + 0x1431, struct.pack("<HH", 0x1234, 0x5678))
        mu.mem_write(USE_WHO * 16 + 0x0B44, struct.pack("<H", member))
        mu.mem_write(GDS * 16 + 0x2100, struct.pack("<H", len(records)))
        for k, (thing, spell, eff, handle, charges) in enumerate(records):
            mu.mem_write(EFFECTS * 16 + 0x24D + k * 10, struct.pack("<HHHBBBB", thing, 0, spell, eff, handle, charges, 0))
        mu.mem_write(GDS * 16 + 0x2A63, struct.pack("<HH", 0, EVENTS))
        mu.mem_write(GDS * 16 + 0x2A6B, struct.pack("<H", len(events)))
        for k, (kind, thing, handle) in enumerate(events):
            mu.mem_write(EVENTS * 16 + k * 0x11, struct.pack("<IBHB", 1000, kind, thing, handle))
        sp = 0x7F0
        offset = effect * 31 if offset is None else offset
        mu.mem_write(SS * 16 + sp, struct.pack("<HHHHH", WAY_BACK, CODE, 0x2, offset, segment))
        for reg, value in dict(cs=TSR, ds=GDS, es=0x1111, ss=SS, esp=sp, ebp=0x600, eax=0xAAAA, ebx=0xBBBB,
                               esi=0x5151, edi=0xD1D1, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["ef_charges"], CODE * 16 + WAY_BACK + 5, count=100000)
        self.mu_last = mu
        self.assertEqual(mu.reg_read(r.UC_X86_REG_IP) & 0xFFFF, WAY_BACK + 5)  # (past the NOPs: the call)
        self.assertEqual([mu.reg_read(x) & 0xFFFF for x in (r.UC_X86_REG_SP, r.UC_X86_REG_BP, r.UC_X86_REG_AX,
                                                             r.UC_X86_REG_BX, r.UC_X86_REG_SI, r.UC_X86_REG_DI,
                                                             r.UC_X86_REG_ES)],
                         [sp, 0x600, 0xAAAA, 0xBBBB, 0x5151, 0xD1D1, 0x1111])
        pushed = struct.unpack("<HHHHH", bytes(mu.mem_read(SS * 16 + sp, 10)))
        self.assertEqual(pushed[:3], (0x1234, 0x5678, 0x2C06))  # (the window, far, then the line's 2C06h)
        text = bytes(mu.mem_read(pushed[4] * 16 + pushed[3], 48)).split(b"\0")[0].decode()
        return text, (pushed[3], pushed[4]) == (offset, segment)

    def test_a_spell_of_uses(self):
        """Armor (spell 0, its time -1: until its hits are used) names its charges; one is a charge."""
        self.assertEqual(self.line(5, [(2, 0, 5, 3, 3)]), ("Armor (3 charges)", False))
        self.assertEqual(self.line(5, [(2, 0, 5, 3, 1)])[0], "Armor (1 charge)")
        self.assertEqual(self.line(46, [(1, 19, 46, 1, 4), (2, 19, 46, 1, 12)])[0], "Mirror Image (12 charges)")
        self.assertEqual(self.line(46, [(2, 323, 46, 1, 100)])[0], "Reflected Image (100 charges)")

    def test_reflected_image(self):
        """Mirror Images from Reflected Image (spell 323) take its name, with no charges too; Mirror Image's keep theirs."""
        self.assertEqual(self.line(46, [(2, 323, 46, 1, 0)]), ("Reflected Image", False))
        self.assertEqual(self.line(46, [(1, 323, 46, 1, 3), (2, 19, 46, 1, 0)]), ("Mirror Image", True))
        self.assertEqual(_word(self.mu_last, TSR * 16 + self.sym["hdr"] + 2136), 0)
        self.line(46, [(2, 323, 46, 1, 0)])
        self.assertEqual(_word(self.mu_last, TSR * 16 + self.sym["hdr"] + 2136), 1)
        self.line(46, [(2, 323, 46, 1, 2)])  # (with charges: both counted)
        self.assertEqual([_word(self.mu_last, TSR * 16 + self.sym["hdr"] + n) for n in (2128, 2136)], [1, 1])

    def test_enlarge_and_the_armour_spells(self):
        """SL's mod lines from the Loader's EF_STATS (member 2's row): Enlarge's damage ("dice" with RULE_HI_ENLARGE),
        the armour spells' AC; nothing from a row without one, another member's, or with the Loader gone."""
        stats = [0, 0x80, 0x80, 0x80] * 4
        stats[8:12] = [9, 4, 0xFF, 0x80]
        timed = [(2, 51, 32, 2, 7)]
        self.assertEqual(self.line(32, timed, [(7, 2, 2)], stats=stats, hi=512)[0], "Enlarged (+90% dice)")
        self.assertEqual(self.line(32, timed, [(7, 2, 2)], stats=stats)[0], "Enlarged (+90% damage)")
        self.assertEqual(self.line(6, [(2, 82, 6, 1, 5)], stats=stats)[0], "Barkskin (AC 4)")
        self.assertEqual(self.line(40, [(2, 133, 40, 1, 0)], stats=stats)[0], "Flesh Armor (AC -1)")
        self.assertEqual(self.line(104, [(2, 200, 104, 1, 0)], stats=stats), ("Magical Vestments", True))
        self.assertEqual(self.line(104, [(2, 200, 104, 1, 3)], stats=stats)[0], "Magical Vestments (3 charges)")
        self.assertEqual(self.line(6, [(2, 82, 6, 1, 0)], stats=stats, member=1), ("Barkskin", True))
        self.assertEqual(self.line(6, [(5, 82, 6, 1, 0)], stats=stats, member=5), ("Barkskin", True))
        self.assertEqual(self.line(6, [(2, 82, 6, 1, 0)], stats=stats, stale=True), ("Barkskin", True))
        stats[8] = 25
        self.assertEqual(self.line(32, [], stats=stats, hi=512)[0], "Enlarged (+250% dice)")
        self.assertEqual(_word(self.mu_last, TSR * 16 + self.sym["hdr"] + 2136), 1)

    def test_an_item_power_has_none(self):
        """Shadowseeker's Detect Invisible (spell 13, its time 60, cast for -9999 with no timer): its stray 15
        isn't shown; with a timer of its own ("effect ends" for the thing and handle) it is."""
        self.assertEqual(self.line(13, [(2, 13, 13, 5, 15)]), ("Detect Invisible", True))
        self.assertEqual(self.line(13, [(2, 13, 13, 5, 15)], [(7, 2, 4), (7, 1, 5), (3, 2, 5)]),
                         ("Detect Invisible", True))
        self.assertEqual(self.line(13, [(2, 13, 13, 5, 15)], [(3, 2, 5), (7, 2, 5)])[0], "Detect Invisible (15 charges)")

    def test_none_left_or_not_its_own(self):
        self.assertEqual(self.line(5, [(2, 0, 5, 3, 0)]), ("Armor", True))  # (no charges)
        self.assertEqual(self.line(5, [(1, 0, 5, 3, 3)]), ("Armor", True))  # (another member's)
        self.assertEqual(self.line(5, [(2, 0, 5, 3, 3)], segment=0x4444), ("", True))  # (another line's text)
        self.assertEqual(self.line(5, [(2, 0, 5, 3, 3)], offset=5 * 31 + 1), ("rmor", True))  # (not a record)
        self.assertEqual(self.sym["ef_charge_lines"] - self.sym["hdr"], 2128)
        self.assertEqual(self.sym["ef_stats_off"] - self.sym["hdr"], 2134)
        self.assertEqual(self.sym["ef_mod_lines"] - self.sym["hdr"], 2136)
        self.assertEqual(self.sym["hdr_end"] - self.sym["hdr"], 2138)
        self.assertEqual(ravlog.EF_STATS_OFF, 2134)
        self.assertEqual(ravlog.EF_MOD_LINES, 2136)

    @unittest.skipUnless(WOTR, "needs the sequel's files (DSUN_WOTR)")
    def test_the_site_and_its_uses(self):
        """The site's bytes in the sequel (8ABBDh, after "push 318h / push ax"), and EC_USES the spells whose
        records' time is negative but not -9999 (RESOURCE.GFF's), with Reflected Image (Mirror Image's)."""
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        p = next(p for p in ravager.PATCHES if p.name == "ef_charges")
        self.assertEqual(exe[p.offset - 4:p.offset + 8].hex(), "68180350" + p.original.hex())
        with open(os.path.join(WOTR, "RESOURCE.GFF"), "rb") as f:
            table, _ = ravlog.spell_table(f.read())
        uses = [s for s in range(320) if -9999 < struct.unpack_from("<h", table, s * 32 + 7)[0] < 0]
        with open(ASM) as f:
            src = f.read()
        listed = src.split("\nec_uses dw ")[1].split("\n")[0].split(", ")
        self.assertEqual([int(x) for x in listed], uses + [323, -1])


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class ArrowsForbidTests(unittest.TestCase):
    ITEMS = 0x4800

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def setUp(self):
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x100000)
        self.mu.mem_write(TSR * 16, self.image)
        self.mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        self.mu.mem_write(GDS * 16 + 0x19C1, struct.pack("<HH", 0, self.ITEMS))
        self.mu.mem_write(GDS * 16 + 0x19CD, struct.pack("<HH", 0x7000, GDS))
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        self.rules(1)

    def rules(self, hi):
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + test_ravkits.RULES_HI, struct.pack("<H", hi))

    def ready(self, sheet: bytes, name: int) -> int:
        """CU_SITE's answer for item 3 (type 6, named NAME) to the quiver, the game's lists saying yes."""
        frame, caller = 0x600, 0x640
        rec = bytearray(0x17)
        struct.pack_into("<H", rec, 0x0A, 6)
        struct.pack_into("<H", rec, 0x14, name)
        self.mu.mem_write(self.ITEMS * 16 + 3 * 0x17, bytes(rec))
        self.mu.mem_write(SS * 16 + 0x500, sheet)
        self.mu.mem_write(SS * 16 + frame, struct.pack("<H", caller))
        self.mu.mem_write(SS * 16 + frame + 0x0A, struct.pack("<HH", 0x500, SS))
        self.mu.mem_write(SS * 16 + frame - 1, b"\xEE")
        self.mu.mem_write(SS * 16 + caller + 6, struct.pack("<HH", 3, 6))
        self.mu.mem_write(SS * 16 + 0x5F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        for reg, value in dict(cs=TSR, ds=GDS, es=0, ebx=0, edx=6, eax=1, ss=SS, esp=0x5F0, ebp=frame,
                               eflags=0x2).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym["cu_site"], TSR * 16 + 0xFFF0)
        return self.mu.mem_read(SS * 16 + frame - 1, 1)[0]

    def test_only_a_spellarcher(self):
        archer = test_ravkits.wotr_sheet((9, 11), (5, 5), 4, 1)  # (a half-elf fighter/preserver's first kit)
        fighter = test_ravkits.wotr_sheet((9,), (5,), 2, 0)
        for row in range(4):
            self.assertEqual(self.ready(archer, AP_ARROW_NAME + row), 1)
            self.assertEqual(self.ready(fighter, AP_ARROW_NAME + row), 0)
        self.assertEqual(self.ready(fighter, AP_ARROW_NAME + 4), 1)  # (not a spell arrow)
        self.assertEqual(self.ready(fighter, 12), 1)
        self.assertEqual(_word(self.mu, TSR * 16 + self.sym["hdr"] + 2130), 4)
        self.rules(0)  # (no kits: no Spellarcher, and the arrows as any)
        self.assertEqual(self.ready(fighter, AP_ARROW_NAME + 1), 1)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class ArrowsSoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def made(self, text: bytes):
        """ARROWS_ASK's answer read (its .ready) with the Loader's words TEXT: the sounds the game's routine
        (B8h:0A22h, the load + 1C5Fh) was asked for."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        mu.mem_write(TSR * 16 + self.sym["pick_text"], text + b"\0")
        mu.mem_write(TSR * 16 + self.sym["showing"], b"\1")  # (a window up: no words shown here)
        sound = (GDS - 0x47E0 + 0x1C5F) * 16 + 0x0A22
        mu.mem_write(sound, b"\xCB")  # (retf)
        played = []
        mu.hook_add(UC_HOOK_CODE, lambda uc, at, size, data: played.append(
            uc.mem_read(SS * 16 + (uc.reg_read(r.UC_X86_REG_SP) & 0xFFFF) + 4, 1)[0]), begin=sound, end=sound)
        mu.mem_write(SS * 16 + 0x5FE, struct.pack("<H", 0xFFF0))
        for reg, value in dict(cs=TSR, ds=GDS, ss=SS, esp=0x5FE, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["arrows_ask.ready"], TSR * 16 + 0xFFF0, count=100000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP) & 0xFFFF, 0x600)
        return played, _word(mu, TSR * 16 + self.sym["hdr"] + 2132)

    def test_made_plays_vampiric_touchs(self):
        self.assertEqual(self.made(b""), ([0x6E], 1))

    def test_refused_plays_none(self):
        self.assertEqual(self.made(b"Not in armour."), ([], 0))

    @unittest.skipUnless(WOTR, "needs the sequel's files (DSUN_WOTR)")
    def test_the_sound_routine_is_there(self):
        """B8h:0A22h at the load + 1C5Fh (file 22212h): "push bp / mov bp,sp / sub sp,54h", the sound on
        test, then "cmp byte [bp+6],0FFh" (none); and the touch spells' cast sounds, Vampiric Touch's alone."""
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        self.assertEqual(exe[0x22212:0x22218].hex(), "558bec83ec54")
        self.assertEqual(exe[0x22224:0x22228].hex(), "807e06ff")
        with open(os.path.join(WOTR, "RESOURCE.GFF"), "rb") as f:
            table, _ = ravlog.spell_table(f.read())
        self.assertEqual([table[s * 32 + 0x0F] for s in (3, 10, 38)], [0xFF, 0xFF, 0x6E])


if __name__ == "__main__":
    unittest.main()


class EfStatsTests(unittest.TestCase):
    def test_the_rows(self):
        """RavDiceLog's EF_STATS: each member's Enlarge level and armour spells' AC (the sequel's effect numbers),
        -128 without one; an empty place none at all."""
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)

        class G:
            def creature(self, m):
                rec = bytearray(game.CREATURE_SIZE)
                rec[game.CREATURE_NAME] = 0 if m == 3 else 65
                return bytes(rec)

            def enlarge_level(self, m):
                return {0: 9, 1: 300}.get(m, 0)

            def armour_spells_ac(self, m):
                return {0: {6: 4}, 2: {40: -1, 104: 3, 6: 200}}.get(m, {})

        self.assertEqual((game.EFFECT_BARKSKIN, game.EFFECT_FLESH_ARMOR, game.EFFECT_VESTMENTS), (6, 40, 104))
        self.assertEqual(struct.unpack("<16b", ravlog.ef_stats(G())),
                         (9, 4, -128, -128, -1, -128, -128, -128, 0, 127, -1, 3, 0, -128, -128, -128))
