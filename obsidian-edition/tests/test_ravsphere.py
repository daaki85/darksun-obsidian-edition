"""The Elementalist's second sphere in Wake of the Ravager: DSCLOG2's EL_SPHERE (sites 90-92, run in an
emulated CPU through SITE's INT F5h way in) against ravager.casts (kits.spell_spheres' rule on the sequel's
spheres) on the transferred party's sheets (test_ravkits.wotr_sheet: the kit byte +3Dh, the second sphere
+3Fh's low bits); and the sequel's own 62B45h (spell, class), run from its DSUN.EXE, against
ravager.class_spheres, with the three sites each right after a call to it. Needs nasm and unicorn, else
skipped; the program's parts need the sequel (DSUN_WOTR)."""

import os
import re
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, kitpages, kits, ravager, ravlog  # noqa: E402
from test_ravkits import ASM, characters, wotr_sheet  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

WOTR = os.environ.get("DSUN_WOTR")
TSR, GDS, SS = 0x1000, 0x6000, 0x7000
SHEETS, CREATURES = 0x4800, 0x4900  # (segments of the test's sheets and creatures)
FIGHTERS_SEG, SPHERES_SEG = 0x3F49 - 0x47E0, 0x41F1 - 0x47E0  # (DSCLOG2's, less DS's)
GAME_CS, GAME_IP = 0x5555, 0x1233  # (the site's byte there, the way back after it)
RULES_HI = 270
SITES = {"el_sphere_know": 90, "el_sphere_level": 91, "el_sphere_cast": 92}
SHINOBI_SITE = {"shinobi_mage": 190}  # (the slot routine's "casts wizard spells": a Shinobi's thief class)


def sphere_bytes() -> bytes:
    """Each spell's sphere byte (0-EAh): the sequel's, else one of each kind on every spell."""
    if ravager.is_wotr_dir(WOTR):
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        return exe[ravager.SPHERES_FILE:ravager.SPHERES_FILE + 0xEB]
    kinds = (0x30, 0x02, 0x01, 0x03, 0x04, 0x05, 0x08, 0x0A, 0x20, 0x21, 0x25)
    return bytes(kinds[s % len(kinds)] for s in range(0xEB))


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class ElSphereTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        cls.spheres = sphere_bytes()

    def setUp(self):
        mu = self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(0xF5 * 4, struct.pack("<HH", self.sym["site_int"], TSR))
        mu.mem_write(GDS * 16 + 0x19C5, struct.pack("<HHHH", 0, SHEETS, 0, CREATURES))
        mu.mem_write((GDS + SPHERES_SEG) * 16 + 0x7D3, self.spheres)
        for member in range(4):  # (combatant N: creature N + 5, its sheet N)
            mu.mem_write((GDS + FIGHTERS_SEG) * 16 + 0xC33 + 3 * member, struct.pack("<BH", 2, member + 5))
            mu.mem_write(CREATURES * 16 + (member + 5) * 0x31 + 4, struct.pack("<H", member))
        self.rules(1)
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        old = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = old | game.RULE_KITS
        self.addCleanup(setattr, game, "RULES_IN_FORCE", old)

    def rules(self, hi: int) -> None:
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + RULES_HI, struct.pack("<H", hi))

    def site(self, number: int, member: int, spell: int, cls: int, answer: int) -> int:
        """Site NUMBER run as the game reaches it (INT F5h's frame, SITE's way in reading its byte), right
        after 62B45h's retf: the
        call's two words on the stack, AL the game's ANSWER; checks the way back past the byte with the
        two words gone and every register but AL kept. Returns AL."""
        mu = self.mu
        mu.mem_write(GAME_CS * 16 + GAME_IP, bytes((0xCD, 0xF5, number, 0xF4)))  # (hlt after: the OR's place)
        sp, bp = 0x7F0, 0x900
        mu.mem_write(SS * 16 + sp - 6, struct.pack("<HHHHH", GAME_IP + 2, GAME_CS, 0x2, spell, cls))  # (the INT's frame)
        mu.mem_write(SS * 16 + bp + 6, struct.pack("<H", member))
        regs = dict(cs=GAME_CS, ds=GDS, es=0x1234, ss=SS, esp=sp - 6, ebp=bp, eax=0xAB00 | answer, ebx=0x2222,
                    ecx=0x3333, edx=0x4444, esi=member if number == 190 else 0x5555,
                    edi=member if number == 90 else 0x7777, eflags=0x2)
        for reg, value in dict(regs, cs=TSR).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["site_int"], GAME_CS * 16 + GAME_IP + 3, count=2000)  # (as INT F5h)
        regs["esp"] = sp
        got = {reg: mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper())) & 0xFFFF for reg in regs}
        self.assertEqual(mu.reg_read(r.UC_X86_REG_IP), GAME_IP + 3)
        for reg, value in regs.items():
            if reg == "esp":
                self.assertEqual(got[reg], sp + 4)
            elif reg == "eax":
                self.assertEqual(got[reg] >> 8, 0xAB)
            elif reg != "eflags":
                self.assertEqual(got[reg], value & 0xFFFF, reg)
        return got["eax"] & 0xFF

    def sheets(self):
        """(sheet) for the test: every cleric an Elementalist with each second sphere (none, the four,
        two out of range), the new spells' bits above it on and off; and every sheet of
        test_ravkits.characters with a cleric class (Healers, Crusaders, a human once a cleric)."""
        out = []
        for cls in range(1, 5):
            for second in range(7):
                for high in (0, 0xF8):
                    sheet = bytearray(wotr_sheet((cls,), (7,), 1, 1))
                    sheet[kits.SPHERE2] = second | high
                    out.append(bytes(sheet))
        for classes, levels, race, byte in characters():
            if any(1 <= c <= 4 for c in classes) and (len(classes) > 1 or levels == (6,)):
                sheet = bytearray(wotr_sheet(classes, levels, race, byte))
                sheet[kits.SPHERE2] = 3
                out.append(bytes(sheet))
        return out

    def test_el_sphere(self):
        """Each site's AL is ravager.casts: the game's answer kept, and for an Elementalist's own cleric
        class a priest spell of its second sphere's made yes; a spell of each sphere byte, each class."""
        kinds = {}
        for spell in ravager.PRIEST_SPELLS:
            kinds.setdefault(self.spheres[spell], spell)
        spells = sorted(kinds.values()) + [0x10, 0xEB]
        made, seen = 0, set()
        for n, sheet in enumerate(self.sheets()):
            member = n % 4
            self.mu.mem_write(SHEETS * 16 + member * ravager.SHEET_SIZE, sheet)
            for cls in range(20):
                for spell in spells:
                    byte = self.spheres[spell] if spell < 0xEB else 0
                    game_says = int(spell in ravager.PRIEST_SPELLS and bool(byte & ravager.class_spheres(cls)))
                    want = ravager.casts(sheet, cls, spell, byte) if spell in ravager.PRIEST_SPELLS else False
                    site = (90, 91, 92)[(cls + spell) % 3]
                    with self.subTest(sheet=n, cls=cls, spell=spell, site=site):
                        self.assertEqual(self.site(site, member, spell, cls, game_says), int(want))
                        made += want and not game_says
                        if want and not game_says:
                            seen.add(sheet[kits.SPHERE2] & kits.SPHERE2_MASK)
        self.assertGreater(made, 0)
        self.assertEqual(seen & {1, 2, 3, 4}, {1, 2, 3, 4})
        self.assertEqual(self.site(91, 0, spells[0], 1, 1), 1)  # (the game's yes kept)

    def test_rule_off(self):
        """With the kits' rule off, the game's answer stands, an Elementalist's second sphere none."""
        sheet = bytearray(wotr_sheet((1,), (7,), 1, 1))
        sheet[kits.SPHERE2] = 3  # (fire)
        self.mu.mem_write(SHEETS * 16, bytes(sheet))
        fire = next(s for s in ravager.PRIEST_SPELLS if self.spheres[s] == ravager.FIRE)
        self.assertEqual(self.site(90, 0, fire, 1, 0), 1)
        self.rules(0)
        for number in (90, 91, 92):
            self.assertEqual(self.site(number, 0, fire, 1, 0), 0)

    def test_shinobi_mage(self):
        """SHINOBI_MAGE (site 190, the member SI) answers yes to "does the class cast wizard spells" (spell 8)
        for a Shinobi's own thief class, awake, with the kits' rule on (kits.slots then gives it the Seeker's
        table: ADND_SLOTS's KIT_TABLE); the game's answer kept for every other class and sheet, and with
        the rule off."""
        made = 0
        for n, (classes, levels, race, byte) in enumerate(characters()):
            sheet = wotr_sheet(classes, levels, race, byte)
            member = n % 4
            self.mu.mem_write(SHEETS * 16 + member * ravager.SHEET_SIZE, sheet)
            own = kitpages.kit_class_of(sheet, kits.SHINOBI) if kits.SHINOBI in kitpages.kit_ids(sheet) else 0
            for cls in (11, 13, 17, 18):
                for rules in (1, 0):
                    self.rules(rules)
                    for answer in (0, 1):
                        want = answer or int(bool(rules) and cls == 17 and own == 17)
                        with self.subTest(classes=classes, levels=levels, byte=byte, cls=cls, rules=rules, answer=answer):
                            self.assertEqual(self.site(190, member, 8, cls, answer), want)
                        made += want and not answer
        self.assertGreater(made, 0)

    def test_patches(self):
        """The four sites' patches: SITE's bytes (sites 90-92, 190) on "add sp,4", the "or al,al" after."""
        by_name = {p.name: p for p in ravager.PATCHES}
        for name, number in {**SITES, **SHINOBI_SITE}.items():
            p = by_name[name]
            self.assertEqual((p.original, p.replacement), (bytes.fromhex("83c404"), bytes((0xCD, 0xF5, number))))
            self.assertEqual(struct.unpack_from("<H", self.image, self.sym["site_table"] + 2 * number)[0],
                             self.sym["shinobi_mage" if number == 190 else "el_sphere_di" if number == 90 else "el_sphere_bp"])


@unittest.skipIf(Uc is None, "needs unicorn")
@unittest.skipUnless(ravager.is_wotr_dir(WOTR), "needs the sequel (DSUN_WOTR)")
class SequelSpheresTests(unittest.TestCase):
    ROUTINE, SEGMENT_FILE = 0x62B45, 0x62100  # (62B45h; its overlay's code from 62100h, CS:0 there)

    @classmethod
    def setUpClass(cls):
        cls.exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()

    def test_routine(self):
        """62B45h (spell, class), run from the sequel's program, says yes for a priest spell (73h-EAh)
        exactly when the spell's sphere byte meets ravager.class_spheres(class), for every class 0-20."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        cs = 0x2000
        mu.mem_write(cs * 16, self.exe[self.SEGMENT_FILE:self.SEGMENT_FILE + 0x1000])
        mu.mem_write(0x3D0 * 16 + 0x7D3, self.exe[ravager.SPHERES_FILE:ravager.SPHERES_FILE + 0xEB])
        mu.mem_write(cs * 16 + 0xFFF0, b"\xF4")
        yes = 0
        for cls in range(21):
            for spell in ravager.PRIEST_SPELLS:
                mu.mem_write(0x7000 * 16 + 0x7F0, struct.pack("<HHHH", 0xFFF0, cs, spell, cls))
                for reg, value in dict(cs=cs, ss=0x7000, esp=0x7F0, eax=0, eflags=2).items():
                    mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
                mu.emu_start(cs * 16 + self.ROUTINE - self.SEGMENT_FILE, cs * 16 + 0xFFF0, count=200)
                al = mu.reg_read(r.UC_X86_REG_EAX) & 0xFF
                byte = self.exe[ravager.SPHERES_FILE + spell]
                self.assertEqual(al, int(bool(byte & ravager.class_spheres(cls))), (cls, hex(spell)))
                yes += al
        self.assertGreater(yes, 0)

    def test_sites_follow_the_call(self):
        """Each site is right after a call to 62B45h: "push cs / call" in its overlay (62C00h, 628AFh) or
        the far call through its stub (97DC5h's "call 588h:20h"), and the program's only calls to it
        besides 626B7h's two (its class-is-a-caster test with spells 8 and 73h, no member's sphere): its
        first (spell 8, 627D6h) is SHINOBI_MAGE's (site 190), the second (73h) left alone."""
        calls = set()
        for m in re.finditer(rb"\x0e\xe8", self.exe):
            at = m.start() + 1
            if at + 3 + struct.unpack_from("<h", self.exe, at + 1)[0] == self.ROUTINE:
                calls.add(at + 3)
        calls |= {m.end() for m in re.finditer(re.escape(bytes.fromhex("9a20008805")), self.exe)}
        sites = {p.offset for p in ravager.PATCHES if p.name in SITES or p.name in SHINOBI_SITE}
        self.assertEqual(calls - sites, {0x6281B})
        self.assertTrue(sites <= calls)
        for at in sites:
            self.assertEqual(self.exe[at:at + 5], bytes.fromhex("83c4040ac0"))


if __name__ == "__main__":
    unittest.main()
