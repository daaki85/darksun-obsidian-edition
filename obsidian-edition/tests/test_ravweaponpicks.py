"""The weapon picks at creation in Wake of the Ravager: the patch sites (ravager.PATCHES' cr_weapons and pk_*,
DSCLOG2's sites 120-125) and the sequel's bytes they replace and read (needs DSUN_WOTR), the Loader's weapon
window for the sequel's RESOURCE.GFF (weaponpages.rav_chunks, its pictures in the sequel's PLNR form:
art.plnr_frames, read back by wotrart.decode_plnr), and DSCLOG2's WEAPON PICKS run in an emulated CPU (LV_DUE
against the rule; WP_PUT and SPEC_SET writing game.packed_specs' V3 bytes, +45h kept; WP_FILL's defaults). The
emulated checks need nasm and unicorn, else skipped."""

import os
import random
import re
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import art, game, gff, ravager, ravlog, weaponpages as wp, wotrart  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

WOTR = os.environ.get("DSUN_WOTR")
ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
TSR, SS = 0x1000, 0x4000
RULES_HI = 270
SPEC_SLOTS, SH_RACE, SH_CLASSES, SH_LEVELS = 0x42, 0x12, 0x1B, 0x1E  # (the sequel's 48h sheet)
SITES = {"cr_weapons": 120, "pk_win": 121, "pk_title": 122, "pk_fill": 123, "pk_click": 124, "pk_hover": 125,
         "lv_weapons": 150}


def due(classes, levels, race) -> int:
    """The weapon specs a new character is due (WEAPON-SPECS.md): a gladiator 2, 3 from 6th level, 4 from
    9th, and past SL's levels one more at 13th, 17th, 21st and 25th; a fighter 1, 2 from 13th; a ranger 1
    (the owner's 2026-11-26); a human's earlier classes only once its first class's level has passed theirs
    (no kits here)."""
    most = 0
    for i, (c, lv) in enumerate(zip(classes, levels)):
        if i and race == 1 and lv >= levels[0]:
            continue
        if c == 10:
            most = max(most, 2 + (lv >= 6) + (lv >= 9) + sum(lv >= n for n in (13, 17, 21, 25)))
        elif c == 9:
            most = max(most, 1 + (lv >= 13))
        elif 13 <= c <= 16:
            most = max(most, 1)
    return most


class SiteTests(unittest.TestCase):
    def test_sites(self):
        """Each patch is DSCLOG2's SITE with its number (NOPs after), that site's routine of the same name."""
        src = open(ASM).read()
        by_name = {p.name: p for p in ravager.PATCHES}
        for name, number in SITES.items():
            p = by_name[name]
            self.assertEqual(p.replacement[:3], bytes((0xCD, ravager.VEC_SITE, number)), name)
            self.assertEqual(p.replacement[3:], b"\x90" * (len(p.original) - 3), name)
            self.assertRegex(src, r"\n        dw %s +; %d SITE_" % (name, number))

    def test_before_resident_end(self):
        """The WEAPON PICKS block is in the resident part."""
        src = open(ASM).read()
        self.assertLess(src.index("\ncr_weapons:"), src.index("\nresident_end:"))

    @unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
    def test_in_the_program(self):
        """The bytes the sites replace are the sequel's, and the constants the routines read from around them:
        the pop-up's calls (168:71Fh, 168:7FFh), the title's colours, width and place, the click handler's
        ways out, the event loop's lines routine."""
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        by_name = {p.name: p for p in ravager.PATCHES}
        for name in SITES:
            p = by_name[name]
            self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original, name)
        self.assertEqual(exe[0x93D08:0x93D0D], bytes.fromhex("9a1f076801"))  # (call 168:71Fh)
        self.assertEqual(exe[0x93CF3:0x93CF8], bytes.fromhex("9aff076801"))  # (call 168:7FFh)
        self.assertEqual(exe[0x93D6B], 0xE7)
        self.assertEqual(exe[0x93D6F], 0x9F)
        self.assertEqual(exe[0x93D71], 0xE3)
        self.assertEqual(exe[0x93D73:0x93D75], bytes.fromhex("6a46"))  # (push 46h)
        self.assertEqual(exe[0x93F7E:0x93F80], bytes.fromhex("33c0"))  # (the list's end: xor ax,ax)
        self.assertEqual(exe[0x93C8F:0x93C94], bytes.fromhex("6850002b00"))  # (push 2B0050h)


class PlnrTests(unittest.TestCase):
    def test_round_trip(self):
        """art.plnr_frames read back by the sequel's decoder as they were (see-through as 0): runs, pixel 0."""
        rnd = random.Random(5)
        for case in range(60):
            w, h = rnd.randint(1, 40), rnd.randint(1, 12)
            pal = [None, 0] + rnd.sample(range(1, 256), rnd.randint(1, 6))
            rows = []
            for _ in range(h):
                row = []
                for _ in range(w):
                    row.append(row[-1] if row and rnd.random() < 0.5 else rnd.choice(pal))
                rows.append(row)
            chunk = art.plnr_frames([rows])
            with self.subTest(case=case):
                self.assertEqual(wotrart.decode_plnr(chunk), [[p or 0 for p in row] for row in rows])


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
class ResourceTests(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb") as f:
            self.data = f.read()
        with open(os.path.join(WOTR, ravager.OBJECTS_FILE), "rb") as f:
            self.raw_objects = f.read()
        self.objects = gff.read_gff(self.raw_objects)
        self.game = gff.read_gff(self.data)

    def test_chunks(self):
        """rav_chunks: the weapon window (WIND 3021, its marble BMP 3022) and a slot for each of the 22 kinds
        in its three states, none of the sequel's ids; the slots where weaponpages.PICKER has them."""
        added = wp.rav_chunks(self.game, self.objects)
        self.assertFalse(set(added) & set(self.game))
        self.assertIn(("WIND", wp.PICKER), added)
        items = wp._items(added[("WIND", wp.PICKER)])
        slots = [c for c, _, _ in items if wp.PICK_FIRST <= c < wp.PICK_FIRST + 22]
        self.assertEqual(sorted(slots), list(range(wp.PICK_FIRST, wp.PICK_FIRST + 22)))
        for cid in slots:
            self.assertIn(("ICON", cid), added)

    def test_copy(self):
        """resources_fixed adds them with the objects given, and not without."""
        out, _ = ravager.resources_fixed(self.data, objects=self.raw_objects)
        self.assertIn(("WIND", wp.PICKER), gff.read_gff(out))
        out, _ = ravager.resources_fixed(self.data)
        self.assertNotIn(("WIND", wp.PICKER), gff.read_gff(out))


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class EmulatedTests(unittest.TestCase):
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
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + RULES_HI, struct.pack("<H", 0))  # (no kits)

    def run_routine(self, name: str, sheet=None, **regs) -> dict:
        if sheet is not None:
            self.mu.mem_write(SS * 16 + 0x500, bytes(sheet))
        self.mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
        for reg, value in dict(dict(cs=TSR, ds=SS, es=SS, ebx=0x500, ss=SS, esp=0x7FC, eflags=0x2), **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[name], TSR * 16 + 0xFFF0)
        return {reg: self.mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper())) for reg in ("eax", "ecx", "edx")}

    def sheet(self) -> bytes:
        return bytes(self.mu.mem_read(SS * 16 + 0x500, ravager.SHEET_SIZE))

    def poke(self, name: str, data: bytes) -> None:
        self.mu.mem_write(TSR * 16 + self.sym[name], data)

    @staticmethod
    def new_sheet(race=1, classes=(9,), levels=(7,), raw=b"\0\0\0\0") -> bytearray:
        sheet = bytearray(ravager.SHEET_SIZE)
        sheet[SH_RACE] = race
        sheet[SH_CLASSES:SH_CLASSES + len(classes)] = bytes(classes)
        sheet[SH_LEVELS:SH_LEVELS + len(levels)] = bytes(levels)
        sheet[SPEC_SLOTS:SPEC_SLOTS + 4] = raw
        return sheet

    def test_lv_due(self):
        """LV_DUE's CX is what the rule says for every class at levels 1-30, and for two-class humans and
        others (a human's earlier class counting only once passed)."""
        cases = [((c,), (lv,), 1) for c in range(1, 18) for lv in range(1, 31)]
        cases += [((a, b), (la, lb), race) for race in (1, 3) for a in (9, 10, 11, 17) for b in (9, 10, 13, 17)
                  if a != b for la in (3, 7, 10) for lb in (5, 9)]
        for classes, levels, race in cases:
            with self.subTest(classes=classes, levels=levels, race=race):
                got = self.run_routine("lv_due", self.new_sheet(race, classes, levels))["ecx"] & 0xFFFF
                self.assertEqual(got, due(classes, levels, race))

    def test_wp_put_v3(self):
        """WP_PUT, one kind after another into an empty sheet (the sequel's 0 bytes, or a V3 one with its
        roll), writes game.packed_specs' bytes: the first picked first; the roll and +45h kept."""
        rnd = random.Random(7)
        for case in range(80):
            kinds = rnd.sample(range(game.KIND_COUNT), rnd.randint(1, 4))
            roll = rnd.choice((None, 0, 3, 17))
            spare = rnd.randint(0, 255)
            raw = (b"\0\0\0" if roll is None else game.packed_specs([], 0, roll)[:3]) + bytes([spare])
            sheet = self.new_sheet(raw=raw)
            with self.subTest(kinds=kinds, roll=roll):
                for kind in kinds:
                    self.run_routine("wp_put", sheet, eax=kind)
                    sheet = bytearray(self.sheet())
                self.assertEqual(bytes(sheet[SPEC_SLOTS:SPEC_SLOTS + 3]),
                                 game.packed_specs([k + 1 for k in kinds], 0, roll)[:3])
                self.assertEqual(sheet[SPEC_SLOTS + 3], spare)
                self.assertEqual(game.specs_of(sheet[SPEC_SLOTS:SPEC_SLOTS + 4])[0][0], kinds[0] + 1)

    def test_more_slots(self):
        """Slots 4-7 (SPEC_MORE: +45h..+47h, 5 bits each): WP_PUT fills them after the packed four, SPEC_GET
        reads them as game.spec_kinds, SPEC_COUNT counts all eight; the packed three and the roll kept."""
        kinds = [5, 1, 2, 17, 22, 9, 3, 12]
        sheet = self.new_sheet(classes=(10,), levels=(25,), raw=game.packed_specs([], 0, 6)[:3] + b"\0")
        for kind in kinds:
            self.run_routine("wp_put", sheet, eax=kind - 1)
            sheet = bytearray(self.sheet())
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        self.assertEqual(bytes(sheet[SPEC_SLOTS:SPEC_SLOTS + 3]), game.packed_specs(kinds[:4], 0, 6)[:3])
        self.assertEqual(sorted(game.spec_kinds(bytes(sheet))[4:]), sorted(kinds[4:]))
        self.assertEqual(game.spec_kinds(bytes(sheet))[4:], bytes(kinds[4:]))
        for slot in range(8):
            got = self.run_routine("spec_get", sheet, esi=slot)["eax"] & 0xFFFF
            self.assertEqual(got, game.spec_kinds(bytes(sheet))[slot], slot)
        self.assertEqual(self.run_routine("spec_count", sheet)["edx"] & 0xFFFF, 8)
        self.assertEqual(game.sheet_roll(bytes(sheet)), 6)

    def test_spec_count(self):
        """SPEC_COUNT's DX: how many specs a V3 sheet has."""
        for kinds in ([], [5], [3, 1], [22, 1, 2, 17]):
            sheet = self.new_sheet(raw=game.packed_specs(kinds, 0, 4)[:3] + b"\0")
            self.assertEqual(self.run_routine("spec_count", sheet)["edx"] & 0xFFFF, len(kinds))

    def test_wp_fill(self):
        """WP_FILL: the long sword, then the club, then the first left; a thri-kreen's chatkcha first; none
        when nothing is left to pick."""
        for race, avail, left, want in ((1, 0x3FFFFF, 2, [1, 2]), (1, 0x3FFFFE, 2, [2, 3]),
                                        (1, 0x3FFFFC, 1, [3]), (8, 0x3FFFFF, 2, [13, 1]),
                                        (1, 0x3FFFFF, 0, []), (1, 0, 2, [])):
            self.poke("lv_avail", struct.pack("<I", avail))
            self.poke("lv_left", bytes((left,)))
            self.run_routine("wp_fill", self.new_sheet(race))
            with self.subTest(race=race, avail=hex(avail), left=left):
                raw = self.sheet()[SPEC_SLOTS:SPEC_SLOTS + 4]
                got = [k for k in game.specs_of(raw)[0] if k] if raw[2] & game.SPEC_PACKED else []
                self.assertEqual(got[:1], want[:1])
                self.assertEqual(sorted(got), sorted(want))


if __name__ == "__main__":
    unittest.main()
