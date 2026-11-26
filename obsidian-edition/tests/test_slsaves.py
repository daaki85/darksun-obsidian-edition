"""SAVING THROWS AS IN AD&D in Shattered Lands (DSCLOG's SAVE_BASE, gamepatch "save_table", RULE_ADND_TABLES):
the game's save routine (DSUN.EXE 877EBh, at a level up) makes a class group's save its 1st-level save less
(level - 1) x a rate / 100, but takes its table's third byte (AD&D's last save) as the most a save improves,
so a warrior stays at 11/11/11/13/11 from 10th level. The site, over its "mov al,es:[bx+6Ch]" (878F7h), gives
the Player's Handbook's save (Table 60, tables.rav_saves: Wake of the Ravager's DSCLOG2 SAVE_BASE has the same)
plus the game's improvement, so the game's "sub" leaves the Handbook's, less a dwarf's or halfling's CON bonus;
for the rogues (the game's thieves and psionicists together) the better of the thief's save at its thief level
and the psionicist's (Dark Sun's Table 8) at its psionicist level, read from the sheet.
Run in an emulated CPU; needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, gamepatch, tables  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

DOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos")
TSR, GAME_DS, SS, GROUPS, SHEET_SEG = 0x1000, 0x5000, 0x4000, 0x6000, 0x7000
SHEETS, SHEET_SIZE, CREATURE = 0x1661, 0x47, 3  # (DS:1661h the sheets' far pointer; the creature, DI)
BP = 0x600
TABLES = 8  # (DSCLOG's RULE_HI_TABLES)
# the game's table (420h:6Ch): by group (priest, warrior, wizard, rogue) and save, the 1st level's save,
# the rate, AD&D's last save
GAME_TABLE = ((10, 45, 2), (14, 45, 6), (13, 45, 5), (16, 45, 8), (15, 45, 7),
              (14, 69, 3), (16, 69, 5), (15, 69, 4), (17, 82, 4), (17, 69, 6),
              (14, 30, 8), (11, 40, 3), (13, 40, 5), (15, 40, 7), (12, 40, 4),
              (13, 25, 8), (14, 50, 4), (12, 25, 7), (16, 25, 11), (15, 50, 5))
# the game's class groups (420h:10h + the class): clerics and druids priests, fighters, gladiators and
# rangers warriors, preservers wizards, psionicists and thieves rogues
GROUP_OF_CLASS = {**{c: 0 for c in range(1, 9)}, 9: 1, 10: 1, 11: 2, 12: 3, **{c: 1 for c in range(13, 17)}, 17: 3}


def build():
    """DSCLOG built with a full map: (the image as loaded, the image's symbols, the tail's symbols, the
    tail's offset in the image)."""
    with tempfile.TemporaryDirectory() as tmp:
        src, out, mp = (os.path.join(tmp, n) for n in ("m.asm", "m.exe", "m.map"))
        with open(os.path.join(DOS, "dsclog.asm")) as f:
            text = f.read()
        with open(src, "w") as f:
            f.write(f"[map all {mp}]\n" + text)
        subprocess.run(["nasm", "-f", "bin", "-I", DOS + os.sep, "-o", out, src], check=True)
        with open(out, "rb") as f:
            exe = f.read()
        with open(mp) as f:
            listing = f.read()
    header = struct.unpack_from("<H", exe, 8)[0] * 16
    symbols = {}
    for section in ("image", "tail"):
        names = {}
        part = listing.split("---- Section %s " % section)[-1].split("---- Section")[0]
        for line in part.splitlines():
            parts = line.split()
            if len(parts) == 3 and all(all(c in "0123456789ABCDEF" for c in p) for p in parts[:2]):
                names[parts[2]] = (int(parts[0], 16), int(parts[1], 16))
        symbols[section] = names
    real, virtual = symbols["tail"]["tail_start"]
    return (exe[header:], {k: v for k, (_, v) in symbols["image"].items()},
            {k: v for k, (_, v) in symbols["tail"].items()}, real - header - virtual)


class LoaderTests(unittest.TestCase):
    def test_patch(self):
        p = next(x for x in gamepatch.PATCHES if x.name == "save_table")
        self.assertEqual((p.offset, p.original.hex()), (0x878F7, "268a876c00"))
        self.assertEqual(p.replacement, bytes((0xCD, 0x98, gamepatch.SAVE_BASE_SITE, 0x90, 0x90)))
        self.assertEqual(gamepatch.SAVE_BASE_SITE, gamepatch.NS_IMAGE + 123)
        self.assertTrue(game.RULE_ADND_TABLES & game.RULES_ALWAYS)

    def test_the_games_bytes(self):
        """In DSUN.EXE the site reads the 1st level's save (ES 420h) before "cbw / sub ax,[bp-2] / mov
        [bp-2],ax", and the game's table and class groups are the ones above."""
        folder = os.environ.get("DSUN_SL")
        exe = os.path.join(folder, "DSUN.EXE") if folder else ""
        if not os.path.exists(exe):
            self.skipTest("DSUN_SL (the game's folder) not given")
        with open(exe, "rb") as f:
            data = f.read()
        self.assertEqual(data[0x878F2:0x87903].hex(), "b820048ec0268a876c00982b46fe8946fe")
        seg = 0x45F10  # (420h:0 in the file)
        self.assertEqual([tuple(data[seg + 0x6C + 3 * k:seg + 0x6F + 3 * k]) for k in range(20)], list(GAME_TABLE))
        self.assertEqual({c: data[seg + 0x10 + c] for c in range(1, 18)}, GROUP_OF_CLASS)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class SaveBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image, cls.sym, cls.tail, cls.tail_at = build()

    def test_band_table(self):
        """SAVE_BANDS, in the tail, is tables.RAV_SAVE_BANDS (the sequel's too: save_bands.inc), the
        psionicists' set fifth."""
        bands = bytes(self.image[self.tail_at + self.tail["save_bands"]:self.tail_at + self.tail["save_bands_end"]])
        want = bytes(b for group in tables.RAV_SAVE_BANDS for first, saves in group for b in (first, *saves))
        self.assertEqual(bands, want)
        self.assertEqual(self.tail_at % 16, 0)

    def save(self, rules_hi, group, level, save, race_bonus=0, classes=()):
        """SAVE_BASE and the game's sum after it (AL - [BP-2], [BP-2] the game's improvement + the race's);
        CLASSES the sheet's (class, level) pairs."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        mu.mem_write(TSR * 16 + self.sym["rules_hi"], struct.pack("<H", rules_hi))
        mu.mem_write(TSR * 16 + self.sym["tail_seg"], struct.pack("<H", TSR + self.tail_at // 16))
        mu.mem_write(GROUPS * 16 + 0x6C, bytes(b for row in GAME_TABLE for b in row))
        mu.mem_write(SS * 16 + BP - 0x0A + 2 * group, bytes((level,)))
        mu.mem_write(GAME_DS * 16 + SHEETS, struct.pack("<HH", 0x100, SHEET_SEG))
        pairs = list(classes) + [(0, 0)] * (3 - len(classes))
        sheet = SHEET_SEG * 16 + 0x100 + CREATURE * SHEET_SIZE
        mu.mem_write(sheet + 0x21, bytes(c for c, _ in pairs) + bytes(lv for _, lv in pairs))
        mu.mem_write(SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        regs = dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7F0, ebp=BP, eflags=0x2, es=GROUPS,
                    ebx=group * 15 + save * 3, ecx=group, esi=save, edx=0x1234, edi=CREATURE)
        for name, value in regs.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["save_base"], TSR * 16 + 0xFFF0, count=20000)
        for name in ("bx", "cx", "dx", "si", "di", "ds", "es", "bp", "sp"):
            want = 0x7F6 if name == "sp" else regs.get(name, regs.get("e" + name)) & 0xFFFF
            self.assertEqual(mu.reg_read(getattr(r, "UC_X86_REG_" + name.upper())), want, name)
        base, rate, last = GAME_TABLE[group * 5 + save]
        improve = min((level - 1) * rate // 100, last) + race_bonus
        return struct.unpack("b", bytes((mu.reg_read(r.UC_X86_REG_AL),)))[0] - improve

    def test_every_group_and_level(self):
        """With the rule, the Player's Handbook's for each group (a psionicist the rogues') at levels 1-25."""
        for group in range(4):
            for level in range(1, 26):
                for save in range(5):
                    with self.subTest(group=group, level=level, save=save):
                        self.assertEqual(self.save(TABLES, group, level, save), tables.rav_saves(group, level)[save])

    def test_warrior_past_ninth(self):
        """The bug: the game's warrior 11/11/11/13/11 from 10th; the Handbook's 8/10/9/9/11 at 9th, 3/5/4/4/6 from 17th."""
        self.assertEqual([self.save(0, 1, 12, s) for s in range(5)], [11, 11, 11, 13, 11])
        self.assertEqual([self.save(0, 1, 20, s) for s in range(5)], [11, 11, 11, 13, 11])
        self.assertEqual([self.save(TABLES, 1, 9, s) for s in range(5)], [8, 10, 9, 9, 11])
        self.assertEqual([self.save(TABLES, 1, 12, s) for s in range(5)], [7, 9, 8, 8, 10])
        self.assertEqual([self.save(TABLES, 1, 20, s) for s in range(5)], [3, 5, 4, 4, 6])

    def test_rule_off_is_the_games(self):
        """Without the rule, the game's own: the 1st level's less the capped improvement."""
        for group in range(4):
            for level in (1, 5, 12, 20):
                for save in range(5):
                    base, rate, last = GAME_TABLE[group * 5 + save]
                    self.assertEqual(self.save(0, group, level, save), base - min((level - 1) * rate // 100, last))

    def test_race_bonus(self):
        """A dwarf's or halfling's CON bonus, in the game's [BP-2], still comes off the Handbook's."""
        self.assertEqual(self.save(TABLES, 1, 12, 0, race_bonus=5), tables.rav_saves(1, 12)[0] - 5)

    def test_multiclass_best(self):
        """A multiclass character keeps the best (lowest) of its groups' saves, as the game's "jle": a fighter/
        thief, a cleric/preserver, a psionicist/thief at their levels."""
        for groups, levels in (((1, 3), (11, 13)), ((0, 2), (12, 12)), ((3, 3), (10, 14)), ((1, 0, 2), (9, 9, 10))):
            got = [min(self.save(TABLES, g, lv, s) for g, lv in zip(groups, levels)) for s in range(5)]
            want = [min(tables.rav_saves(g, lv)[s] for g, lv in zip(groups, levels)) for s in range(5)]
            self.assertEqual(got, want, (groups, levels))

    def test_psionicists(self):
        """A psionicist saves by Dark Sun's table at its psionicist level; a thief by the Handbook's at its
        thief level; a psionicist/thief the better of each save (the game's group level the best of the
        two: its improvement given back as it takes it off). A sheet with neither (no class read) is a
        thief at the group's level."""
        for level in range(1, 26):
            with self.subTest(level=level):
                self.assertEqual([self.save(TABLES, 3, level, s, classes=((12, level),)) for s in range(5)],
                                 list(tables.rav_saves(3, level, psionicist=True)))
                self.assertEqual([self.save(TABLES, 3, level, s, classes=((17, level),)) for s in range(5)],
                                 list(tables.rav_saves(3, level)))
        for psi, thief in ((9, 13), (13, 9), (5, 20), (21, 1)):
            with self.subTest(psi=psi, thief=thief):
                got = [self.save(TABLES, 3, max(psi, thief), s, classes=((12, psi), (17, thief))) for s in range(5)]
                self.assertEqual(got, list(tables.class_saves([(12, psi), (17, thief)])))
        # (a half-giant fighter/psionicist: the rogues' its psionicist level, the warriors' as before)
        self.assertEqual([self.save(TABLES, 3, 7, s, classes=((9, 8), (12, 7))) for s in range(5)],
                         list(tables.rav_saves(3, 7, psionicist=True)))
        self.assertEqual([self.save(TABLES, 3, 10, s) for s in range(5)], list(tables.rav_saves(3, 10)))
        # (the rule off: the game's, a psionicist as a thief)
        self.assertEqual([self.save(0, 3, 12, s, classes=((12, 12),)) for s in range(5)], [11, 10, 10, 14, 10])


if __name__ == "__main__":
    unittest.main()
