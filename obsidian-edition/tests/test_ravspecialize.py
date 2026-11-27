"""DSCLOG2's weapon specialization in Wake of the Ravager (SPEC_OF_SHEET, MISSILE_RATE and NEXT_DIE, run in
an emulated CPU), against Shattered Lands' rules (specialize.skill, missile_attacks, next_die) on the
transferred party's sheets (ravtransfer.sheet: the specs at +42h..+44h) with ravlog's layout, the
sequel's item types' kinds (ravager.rav_kinds, rav_spec_kinds) for every type, warrior or not, at the
levels where the skill changes. Kits aside: the sequel has none yet. Needs nasm and unicorn, else
skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, ravager, ravitems, ravlog, ravtransfer, specialize  # noqa: E402
import test_restrict  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
TSR, SS = 0x1000, 0x4000
K = specialize.KINDS.index
# (classes, levels, race): a fighter at each of mastery's steps, a gladiator, rangers, a multiclass
# fighter, a non-warrior, a dual-classed human whose fighter class is or isn't back yet
CHARACTERS = [((9,), (1,), 2), ((9,), (5,), 2), ((9,), (9,), 2), ((9,), (13,), 2), ((10,), (7,), 2),
              ((9,), (17,), 2), ((9,), (21,), 2), ((10,), (25,), 2),  # (a fighter's second kind: the owner's 2026-11-26)
              ((16,), (3,), 1), ((13,), (8,), 2), ((9, 11), (3, 2), 4), ((17, 9), (2, 3), 6),
              ((11,), (6,), 2), ((17, 9), (3, 5), 1), ((17, 9), (6, 5), 1), ((15, 7), (12, 14), 8)]
SPECS = ([], [K("long sword")], [K("bow"), K("short sword")], [K("polearm"), K("dagger"), K("sling")],
         [K("chatkcha"), K("gythka"), K("mace"), K("club")], [K("lotulis"), K("javelin")],
         [K("two-handed sword"), K("darts"), K("trikal"), K("double spear")])


def wotr_sheet(classes, levels, race, kinds) -> bytes:
    sl = bytearray(test_restrict.sheet(*classes, race=race))
    sl[game.SHEET_LEVELS:game.SHEET_LEVELS + len(levels)] = bytes(levels)
    sl = game.with_specs(bytes(sl) + bytes(ravtransfer.SL_SHEET - len(sl)), [k + 1 for k in kinds])
    return ravtransfer.sheet(sl, loader=True).ljust(ravager.SHEET_SIZE, b"\0")


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class SpecializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        cls.sheets = [(c, l, race, kinds, wotr_sheet(c, l, race, kinds))
                      for c, l, race in CHARACTERS for kinds in SPECS]
        cls.sequel_kinds = {t: (specialize.KIND_OF_TYPE[t], ravitems.sequel_type(t, {}))
                            for kind in specialize.KINDS[16:] for t in specialize._TYPES[kind]}
        cls.fighters = {kind: wotr_sheet((9,), (3,), 2, [K(kind)]) for kind in specialize.KINDS}

    def setUp(self):
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x100000)
        self.mu.mem_write(TSR * 16, self.image)
        self.mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))  # (hlt: where the routine returns)
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)

    def run_routine(self, name: str, sheet: bytes, **regs) -> dict:
        self.mu.mem_write(SS * 16 + 0x500, sheet)
        self.mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
        for reg, value in dict(dict(cs=TSR, ds=TSR, es=SS, ebx=0x500, ss=SS, esp=0x7FC, eflags=0x2), **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[name], TSR * 16 + 0xFFF0)
        return {reg: self.mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper())) for reg in ("eax", "edx", "esi", "ebx")}

    def test_tables(self):
        """DSCLOG2's kind_of_type is ravager.rav_kinds (kind + 1, 0 none) for the sequel's 102 types and the
        mod's 33, and its spec_kinds_own ravager.rav_spec_kinds, for types kind_of_type leaves without one."""
        kinds, own = ravager.rav_kinds(), ravager.rav_spec_kinds()
        table = bytes(self.image[self.sym["kind_of_type"]:self.sym["kind_of_type"] + ravager.GAME_TYPES + ravager.MOD_TYPES])
        self.assertEqual(list(table), [kinds.get(t, -1) + 1 for t in range(len(table))])
        at, got = self.sym["spec_kinds_own"], {}
        while self.image[at]:
            got[self.image[at]] = self.image[at + 1] - 1
            at += 2
        self.assertEqual(got, own)
        self.assertFalse(set(own) & set(kinds))  # (only types with no kind of their own)

    def test_skill(self):
        """SPEC_OF_SHEET's DL is specialize.skill for every sheet and item type."""
        seen = set()
        for classes, levels, race, kinds, sheet in self.sheets:
            for t in range(ravager.GAME_TYPES + ravager.MOD_TYPES):
                want = specialize.skill(sheet, t)
                got = self.run_routine("spec_of_sheet", sheet, esi=t, edx=0xFF)["edx"] & 0xFF
                with self.subTest(classes=classes, levels=levels, kinds=kinds, type=t):
                    self.assertEqual(got, want)
                seen.add(want)
        self.assertEqual(seen, {specialize.NONE, specialize.PLAIN, specialize.EXPERT, specialize.SPECIAL,
                                specialize.MASTER, specialize.GRAND})

    def test_missile_rate(self):
        """MISSILE_RATE's AX is specialize.missile_attacks for the missile weapons, the sequel's darts,
        javelins and Rainbow with them, at each skill and the weapon's own rate."""
        missiles = [t for t in range(ravager.GAME_TYPES + ravager.MOD_TYPES)
                    if specialize.spec_kind_of(t) in [K(k) for k in specialize.MISSILE_RATES]]
        self.assertTrue({18, 25, 93, 98, 38, 43, 59, 87} <= set(missiles))
        changed = 0
        for classes, levels, race, kinds, sheet in self.sheets:
            for t in missiles:
                skill = specialize.skill(sheet, t)
                for halves in (1, 2, 4, 10):
                    want = specialize.missile_attacks(halves, skill, t, sheet)
                    got = self.run_routine("missile_rate", sheet, eax=halves, esi=t, edx=skill)["eax"] & 0xFFFF
                    with self.subTest(classes=classes, levels=levels, kinds=kinds, type=t, halves=halves):
                        self.assertEqual(got, want)
                    changed += got != halves
        self.assertGreater(changed, 100)

    def test_spec_get(self):
        """SPEC_GET reads each slot of the three layouts (a byte each, five bits each, base 17) as
        game.spec_kinds, the upper half of EAX kept."""
        kinds = (K("bow") + 1, K("long sword") + 1, 0, K("staff sling") + 1)
        for raw in (bytes(kinds), (kinds[0] | kinds[1] << 5 | kinds[2] << 10 | kinds[3] << 15 | 0x800000).to_bytes(4, "little"),
                    game.packed_specs(kinds, 0, 7)[:3] + b"\0"):
            sheet = bytearray(ravager.SHEET_SIZE)
            sheet[0x42:0x46] = raw
            for slot in range(4):
                got = self.run_routine("spec_get", bytes(sheet), esi=slot, eax=0x12340000)["eax"]
                self.assertEqual((got >> 16, got & 0xFFFF), (0x1234, game.specs_of(raw)[0][slot]), (raw.hex(), slot))

    def test_spec_get_keeps_sl_kinds(self):
        """A V3 sheet's kinds past the first sixteen (SL's six from the sequel, carried by the party
        transfer) read as themselves: the sequel knows all 22."""
        for sl in specialize.KINDS[16:]:
            sheet = bytearray(ravager.SHEET_SIZE)
            sheet[0x42:0x46] = game.packed_specs((K(sl) + 1, K("bow") + 1), 0, 7)[:3] + b"\0"
            got = [self.run_routine("spec_get", bytes(sheet), esi=slot)["eax"] & 0xFFFF for slot in range(4)]
            self.assertEqual(got, [K(sl) + 1, K("bow") + 1, 0, 0], sl)

    def test_six_kinds(self):
        """The sequel's own weapons of SL's six kinds from it: a fighter specialized in each is
        specialized with them (SPEC_OF_SHEET), and not with the kind #181 folded it into."""
        own = {"two-handed sword": (101, 35), "lotulis": (61,), "double spear": (39,), "trikal": (100,),
               "javelin": (59,), "darts": (38, 43)}
        old = {"two-handed sword": "long sword", "lotulis": "gythka", "double spear": "polearm",
               "trikal": "polearm", "javelin": "chatkcha", "darts": "chatkcha"}
        for kind, types in own.items():
            spec, folded = self.fighters[kind], self.fighters[old[kind]]
            for t in types:
                self.assertEqual(specialize.spec_kind_of(t), K(kind), (kind, t))
                got = self.run_routine("spec_of_sheet", spec, esi=t, edx=0xFF)["edx"] & 0xFF
                self.assertEqual(got, specialize.SPECIAL, (kind, t))
                got = self.run_routine("spec_of_sheet", folded, esi=t, edx=0xFF)["edx"] & 0xFF
                self.assertEqual(got, specialize.PLAIN, (kind, t))

    def test_transfer_keeps_kind(self):
        """Each of SL's types of the six kinds (148-158: the plain, metal, obsidian and bone ones) goes across as
        a sequel type of the same kind in DSCLOG2's kind_of_type (ravitems.sequel_type: the plain six the
        sequel's own, the metal, obsidian and bone ones the mod's own, 141-145)."""
        table = self.image[self.sym["kind_of_type"]:self.sym["kind_of_type"] + ravager.GAME_TYPES + ravager.MOD_TYPES]
        self.assertEqual(len(self.sequel_kinds), 11)  # (148-158)
        for sl_type, (kind, sequel) in self.sequel_kinds.items():
            self.assertEqual(table[sequel] - 1, kind, sl_type)
            self.assertEqual(sequel < ravager.GAME_TYPES, sl_type in ravager.SEQUEL_OWN_WEAPONS, sl_type)

    def test_effects_names(self):
        """EF_LINES_OF's names (ef_kinds) are specialize.KINDS', all 22."""
        at = self.sym["ef_kinds"]
        for i, kind in enumerate(specialize.KINDS):
            ptr = struct.unpack_from("<H", self.image, at + 2 * i)[0]
            name = bytes(self.image[ptr:self.image.index(0, ptr)]).decode()
            self.assertEqual(name, "  " + kind.upper())

    def test_next_die(self):
        for sides in range(1, 25):
            self.assertEqual(self.run_routine("next_die", bytes(ravager.SHEET_SIZE), eax=sides)["eax"] & 0xFFFF,
                             specialize.next_die(sides), sides)


if __name__ == "__main__":
    unittest.main()
