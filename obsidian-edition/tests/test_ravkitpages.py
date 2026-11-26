"""The creation panel's KIT pages in Wake of the Ravager: the pictures' planar form (art.planar_frames,
decode_frame), the Loader's kit windows for the sequel's RESOURCE.GFF (kitpages.rav_chunks, made from its
own windows and letters: needs DSUN_WOTR), the patch sites (ravager.PATCHES' kp_* and dual_kit, DSCLOG2's
sites 62-69 and 76),
and DSCLOG2's KIT PAGE run in an emulated CPU (KIT_CLASS and WP_IDS against kitpages.kit_class and
panel_windows on every class and multiclass group, the rule on and off; NEW_SHEET making a kit taken back
none; DK_BANNED, after DUAL, against kits.dual_kit_banned). The emulated checks need nasm and unicorn,
else skipped."""

import os
import re
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import art, game, gff, kitpages, ravager, weaponpages as wp  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

WOTR = os.environ.get("DSUN_WOTR")
ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
TSR, SS, GDS = 0x1000, 0x4000, 0x6000
RULES_HI = 270
CREATION = 0x1429  # (DS: the sheet being made, far)
SH_RACE, SH_CLASSES, KIT_BYTE = 0x12, 0x1B, 0x3D  # (the sequel's sheet)


class PlanarTests(unittest.TestCase):
    def test_round_trip(self):
        """A picture of two colours and a picture of one, written planar and read back as they were."""
        frames = [[[None, 5, 5, None, 7], [7, None, None, 5, None], [None] * 5],
                  [[9] * 5, [None] * 5, [None, None, 9, None, None]]]
        chunk = art.planar_frames(frames)
        self.assertEqual(struct.unpack_from("<IH", chunk, 0), (len(chunk), 2))
        for i, rows in enumerate(frames):
            self.assertEqual(art.decode_frame(chunk, i), (5, 3, rows))


class SiteTests(unittest.TestCase):
    SITES = {"kp_disc_win": 62, "kp_sphere_win": 63, "kp_disc_click": 64, "kp_sphere_click": 65,
             "kp_shown": 66, "kp_class": 67, "kp_race": 68, "kp_open": 69, "dual_kit": 76}

    def test_sites(self):
        """Each kp_ patch is DSCLOG2's SITE with its number, that site's routine of the same name."""
        src = open(ASM).read()
        by_name = {p.name: p for p in ravager.PATCHES}
        for name, number in self.SITES.items():
            p = by_name[name]
            self.assertEqual(p.replacement[:3], bytes((0xCD, ravager.VEC_SITE, number)), name)
            self.assertEqual(p.replacement[3:], b"\x90" * (len(p.original) - 3), name)
            self.assertRegex(src, r"\n        dw %s +; %d SITE_" % (name, number))
        # (86, 89, 101-109, 119, 126-129: none; 83 STORE and RECALL's RS_CLICK, 85 GEAR_DONE, 82 the shop loop's SHOP_LOOP, 79-80 Psionic Blast's, 81 RL_TRY, 84 the quick saves' GREQ_LOAD, 78 RG_TWO, 52-53 the thief table's, 54-59 the shops' and the message box's, 77 Tab's PROBE_HIT, 90-92 the second sphere's, 87-88 and 95-99 the first spells' and powers', 100 F10's F10_PIN)
        self.assertEqual(len(re.findall(r"\n        dw site_none ", src)), 16)

    FIRST = {"cr_picks": (87, "cr_picks"), "psi_grant": (88, "psi_grant"), "psi_grant_psionicist": (88, "psi_grant"),
             "psi_count": (95, "psi_count"), "psi_list": (96, "psi_list"), "psi_cycle": (97, "psi_cycle"),
             "psi_click": (98, "psi_click"), "pick_top": (99, "pick_top")}

    def test_first_spells_sites(self):
        """The first spells' and powers' patches are DSCLOG2's SITE with their numbers, their routines there."""
        src = open(ASM).read()
        by_name = {p.name: p for p in ravager.PATCHES}
        for name, (number, routine) in self.FIRST.items():
            p = by_name[name]
            self.assertEqual(p.replacement[:3], bytes((0xCD, ravager.VEC_SITE, number)), name)
            self.assertEqual(p.replacement[3:], b"\x90" * (len(p.original) - 3), name)
            self.assertRegex(src, r"\n        dw %s +; %d SITE_" % (routine, number))
        self.assertEqual(len(re.findall(r"\n        dw \w+ +; \d+ ", src)), 130)  # (sites 0-129)

    @unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
    def test_in_the_program(self):
        """The creation overlay's calls and constants the KIT PAGE reads are where it says (the sequel's
        bytes): the window ids pushed, the click routines' ends (the 'call 5C0:39h' redraw), the calls."""
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        src = open(ASM).read()
        value = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"\n(WP_[A-Z_]+) +equ 0x([0-9A-F]+)\b", src)}
        for name in ("WP_CALL_CLOSE", "WP_CALL_OPEN", "WP_CALL_PRINT", "WP_CALL_COLOUR", "WP_CALL_HELP",
                     "WP_CALL_BUTTON", "WP_CALL_MARK", "WP_SHOWN_CALL"):
            self.assertEqual(exe[value[name]], 0x9A, name)  # (a far call)
        for name in ("WP_SPHERE_END", "WP_DISC_END"):
            self.assertEqual(exe[value[name]:value[name] + 5], bytes.fromhex("9a3900c005"), name)
        self.assertEqual(exe[value["WP_MARK_SEG"]], 0xB8)  # (mov ax,360h)
        self.assertEqual(exe[value["WP_SPHERE_SEG"]], 0x68)  # (push 5B8h)
        menu = int(re.search(r"\nDK_MENU_CALL +equ 0x([0-9A-F]+) - 0x([0-9A-F]+)", src).group(1), 16)
        self.assertEqual(exe[menu - 1:menu + 4], bytes.fromhex("9a25006005"))  # (DUAL_KIT's menu: 560:25h)
        dual = next(p for p in ravager.PATCHES if p.name == "dual_kit")
        self.assertEqual(int(re.search(r"\nDK_MENU_CALL +equ 0x[0-9A-F]+ - 0x([0-9A-F]+)", src).group(1), 16),
                         dual.offset + 3)
        for name, ret in (("kp_disc_click", "WP_DISC_RET"), ("kp_sphere_click", "WP_SPHERE_RET"), ("kp_shown", "WP_SHOWN_RET")):
            p = next(p for p in ravager.PATCHES if p.name == name)
            self.assertEqual(p.offset + 3, value[ret], name)


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
class ResourceTests(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb") as f:
            self.data = f.read()
        self.game = gff.read_gff(self.data)

    def test_chunks(self):
        """rav_chunks: the kit pages' windows (none of the sequel's ids), their rows' pictures planar in the
        sequel's own letters, each within ROW_WIDTH, and its spheres' and disciplines' windows with KITS."""
        added = kitpages.rav_chunks(self.game)
        self.assertFalse(set(added) & set(self.game))
        for (kind, cid), chunk in added.items():
            if kind == "ICON":
                self.assertEqual(chunk[18 + 4:18 + 9], art.PLANAR, hex(cid))
                self.assertEqual(struct.unpack_from("<H", chunk, 4)[0], 3)
        self.assertEqual({n: w for n, w in kitpages.row_widths(self.game).items() if w > kitpages.ROW_WIDTH}, {})
        disc = wp._items(added[("WIND", kitpages.KIT_DISCIPLINES)])
        own = wp._items(self.game[("WIND", kitpages.RAV_DISCIPLINES)])
        self.assertEqual(disc, [(kitpages.KIT_VIEW if c == wp.DISCIPLINE_TOGGLE else c, x, y) for c, x, y in own])
        sph = wp._items(added[("WIND", kitpages.KIT_SPHERES)])
        self.assertIn(kitpages.KIT_VIEW, [c for c, _, _ in sph])
        for group, names in kitpages.KITS.items():
            items = wp._items(added[("WIND", kitpages.KIT_WINDOW + group - 1)])
            self.assertEqual([c for c, _, _ in items],
                             [kitpages.KIT_NONE] + [kitpages.row_id(group, k + 1) for k in range(len(names))]
                             + [kitpages.KIT_BACK])

    def test_copy(self):
        """resources_fixed adds them (KIT_PAGES among its fixes), and leaves them out when skipped."""
        out, done = ravager.resources_fixed(self.data)
        self.assertIn(ravager.KIT_PAGES, done)
        self.assertIn(("WIND", kitpages.KIT_WINDOW), gff.read_gff(out))
        out, done = ravager.resources_fixed(self.data, {ravager.KIT_PAGES})
        self.assertNotIn(ravager.KIT_PAGES, done)
        self.assertNotIn(("WIND", kitpages.KIT_WINDOW), gff.read_gff(out))


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
        self.mu.mem_write(GDS * 16 + CREATION, struct.pack("<HH", 0x500, SS))
        self.rules(game.RULE_KITS >> 16)

    def rules(self, hi: int) -> None:
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + RULES_HI, struct.pack("<H", hi))

    def run_routine(self, name: str, sheet: bytes, **regs) -> dict:
        self.mu.mem_write(SS * 16 + 0x500, sheet)
        self.mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
        for reg, value in dict(dict(cs=TSR, ds=GDS, es=0, ebx=0, ss=SS, esp=0x7FC, eflags=0x2), **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[name], TSR * 16 + 0xFFF0)
        return {reg: self.mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper())) for reg in ("eax", "edx", "eflags")}

    @staticmethod
    def creation_sheet(race: int, classes) -> bytes:
        sheet = bytearray(ravager.SHEET_SIZE)
        sheet[SH_RACE] = race
        sheet[SH_CLASSES:SH_CLASSES + len(classes)] = bytes(classes)
        return bytes(sheet)

    def cases(self):
        for race in range(1, 9):
            for a in range(1, 9):
                yield race, (a,)
                for b in range(a + 1, 9):
                    yield race, (a, b)
        yield 8, (2, 3, 6)  # (the thri-kreen druid/fighter/psionicist)
        yield 8, (1, 3, 6)

    def test_kit_class_and_windows(self):
        """KIT_CLASS's AL is kitpages.kit_class, WP_IDS's AX and DX kitpages.panel_windows (the sequel's
        windows for the game's), for every race with one class and two (and the thri-kreen's three); the
        rule off, none."""
        game_ids = {wp.DISCIPLINES: kitpages.RAV_DISCIPLINES, wp.SPHERES: kitpages.RAV_SPHERES}
        for hi, rules in ((1, game.RULE_KITS), (0, 0)):
            self.rules(hi)
            for race, classes in self.cases():
                sheet = self.creation_sheet(race, classes)
                padded = list(classes) + [0] * (3 - len(classes))
                with self.subTest(rules=hi, race=race, classes=classes):
                    al = self.run_routine("kit_class", sheet, eax=0xFF)["eax"] & 0xFF
                    self.assertEqual(al, kitpages.kit_class(padded, rules, race))
                    got = self.run_routine("wp_ids", sheet)
                    disc, sph = kitpages.panel_windows(padded, rules, race)
                    self.assertEqual((got["eax"] & 0xFFFF, got["edx"] & 0xFFFF),
                                     (game_ids.get(disc, disc), game_ids.get(sph, sph)))

    def test_dual_banned(self):
        """DK_BANNED's CF is kits.dual_kit_banned for every kit of every new class, on a human who had each
        class before (its kit, if it had one, each of the old class's)."""
        from dsloader import kits
        for new in range(1, 18):
            base = kitpages.CREATION_CLASS[new] * 4
            for old in range(1, 18):
                if old == new:
                    continue
                for old_kit in range(4):
                    sheet = bytearray(ravager.SHEET_SIZE)
                    sheet[SH_RACE], sheet[SH_CLASSES:SH_CLASSES + 2] = 1, bytes((new, old))
                    sheet[0x1E:0x20] = bytes((1, 5))
                    sheet[KIT_BYTE] = old_kit
                    self.mu.mem_write(SS * 16 + 0x500, bytes(sheet))
                    old_kids = [kitpages.CREATION_CLASS[old] * 4 + old_kit] if old_kit else []
                    for k in range(1, 4):
                        kid = base + k
                        got = self.run_routine("dk_banned", bytes(sheet), eax=kid, es=SS, ebx=0x500)
                        with self.subTest(new=new, old=old, old_kit=old_kit, kit=kid):
                            self.assertEqual(bool(got["eflags"] & 1), kits.dual_kit_banned(kid, [old], old_kids, new))

    def test_new_sheet(self):
        """NEW_SHEET (DONE's copy of the creation sheet): a kit taken back (KIT_OPEN) is none, a kit chosen
        kept, the six bytes past the game's 42h cleared."""
        for byte, want in ((0xFF, 0), (0x02, 0x02), (0, 0)):
            sheet = bytearray(b"\x55" * ravager.SHEET_SIZE)
            sheet[KIT_BYTE] = byte
            self.mu.mem_write(SS * 16 + 0x500, bytes(sheet))
            frame = struct.pack("<HHHHH", 0xFFF0, TSR, 0x2, 0x500, SS) + bytes(10)
            self.mu.mem_write(SS * 16 + 0x700, frame)
            for reg, value in dict(cs=TSR, ds=GDS, ss=SS, esp=0x700, eflags=0x2, ebp=0x1234).items():
                self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
            self.mu.emu_start(TSR * 16 + self.sym["new_sheet"], TSR * 16 + 0xFFF0)
            out = self.mu.mem_read(SS * 16 + 0x500, ravager.SHEET_SIZE)
            self.assertEqual(out[KIT_BYTE], want, hex(byte))
            self.assertEqual(bytes(out[0x42:0x48]), bytes(6))
            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_BP), 0x1234)


if __name__ == "__main__":
    unittest.main()
