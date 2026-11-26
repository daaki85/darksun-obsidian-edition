"""DSCLOG2's kits' gear in Wake of the Ravager (KIT_FORBIDS, KIT_ALLOWS, and CLASS_FORBIDS' Elementalist's
second sphere, run in an emulated CPU), against Shattered Lands' rules (restrict.kit_forbids,
restrict.kit_allows, restrict.allowed: kits.forbids, kits.allows) on the transferred party's sheets
(test_ravkits.wotr_sheet, ravlog's layout) and the sequel's item types (+0 flags, +4 material, +5 worn,
+0Bh armour and two-handed: ravager.wotr_type of Shattered Lands' records), each at a sequel type of
the weapon kind it has there (DSCLOG2's KIND_OF_TYPE, specialize.KIND_OF_TYPE under the layout). And
CU_SITE, the site in the sequel's "may this character equip this item" (19), as SL's PROBE_CAN_USE puts
them together: the game's no made yes by the kit's own, the kit's limits over everything, the off hand
(the equip routine's slot 14) for a Battle Mage and a Healer. Needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, kitpages, kits, npcitems, ravager, ravlog, restrict, specialize  # noqa: E402
import test_ravkits  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = test_ravkits.ASM
TSR, SS, GDS = 0x1000, 0x4000, 0x6000
TYPES_AT = 0x7000  # (the item types' table in the test's game segment)
ITEM_TYPES_PTR = 0x19CD
K = specialize.KINDS.index
CAHULAKS = frozenset((24, ravager.mod_type(146), ravager.mod_type(147)))  # (the sequel's and the mod's two)
LEATHER, NO_MAT = restrict.LEATHER, restrict.NO_MATERIAL_BIT


def record(flags: int, mat: int, kinds: int = 0, worn: int = 0, classes: int = 0xFFFF) -> bytes:
    """A Shattered Lands item type record (20 bytes) of these fields."""
    rec = bytearray(game.ITEM_TYPE_SIZE if game.ITEM_TYPE_SIZE >= 0x14 else 0x14)
    rec[0], rec[8], rec[9], rec[0x0F] = flags, mat, worn, kinds
    rec[0x10:0x12] = classes.to_bytes(2, "little")
    return bytes(rec[:0x14])


def sequel(rec: bytes) -> bytes:
    """REC in the sequel's layout (ravager.wotr_type's fields: +0, and SL's +8 on at +4)."""
    out = bytearray(ravager.TYPE_SIZE)
    out[0] = rec[0]
    out[4:ravager.TYPE_SIZE] = rec[8:8 + ravager.TYPE_SIZE - 4]
    return bytes(out)


MELEE, MISSILE, SHIELD, THROWN = restrict.MELEE, restrict.MISSILE, restrict.SHIELD, restrict.THROWN
ARMOUR, TWO = kits.ARMOUR, kits.TWO_HANDED
MATERIALS = (restrict.WOOD, restrict.BONE, restrict.STONE, restrict.OBSIDIAN, restrict.METAL, LEATHER, NO_MAT)
# the records tried at every weapon type: one-handed and two-handed melee, missile, thrown, by material
WEAPONS = [record(f, m, k) for f, k in ((MELEE, 0), (MELEE, TWO), (MISSILE, 0), (MISSILE, TWO), (MELEE | THROWN, 0))
           for m in MATERIALS]
# ... and at a type of no kind: shields, armour, helms, bracers, a robe, a cloak of protection, a ring
GEAR = [record(SHIELD, m, ARMOUR) for m in MATERIALS] + [record(0, m, ARMOUR, 9) for m in MATERIALS] \
    + [record(0, m, ARMOUR, 7) for m in (restrict.METAL, LEATHER)] \
    + [record(0, NO_MAT, ARMOUR, 3), record(0, NO_MAT, ARMOUR, 1, 0x0190), record(0, NO_MAT, ARMOUR, restrict.CLOAK_SLOT),
       record(0, NO_MAT, 0, 4)]


def sheets():
    """(name, sheet): every kit of one class at 5th level (a Seeker and a Grove Warden of each sphere's
    class), with no specs and with specs of a long sword and a bow; the multiclass groups' kits; a
    half-giant Twin-blade and Brute; a dual-classed human, its kit asleep and awake; an Elementalist of
    each second sphere."""
    out = []
    for cls in range(1, 18):
        for kit in range(4):
            for kinds in ((), (K("long sword"), K("bow"))):
                race = 1 if cls < 9 or cls > 12 else 2
                out.append(((cls, kit, kinds), test_ravkits.wotr_sheet((cls,), (5,), race, kit, kinds)))
    for group, (race, classes) in kitpages.MULTI.items():
        sheet_classes = [next(c for c in range(1, 18) if kitpages.CREATION_CLASS.get(c) == k) for k in sorted(classes)]
        for kit in range(4):
            for kinds in ((), (K("dagger"),)):
                out.append(((tuple(sheet_classes), race, kit, kinds),
                            test_ravkits.wotr_sheet(tuple(sheet_classes), (5,) * len(sheet_classes), race, kit, kinds)))
    for kit in (2, 3):  # (a half-giant gladiator: Twin-blade, Brute)
        out.append((("half-giant", kit), test_ravkits.wotr_sheet((10,), (5,), 5, kit)))
    for levels in ((3, 7), (8, 7)):  # (a human fighter once a Ravager, now a thief; a preserver once a Battle Mage)
        out.append((("dual", levels, 3), test_ravkits.wotr_sheet((17, 9), levels, 1, 0x03 << 2)))
        out.append((("dual mage", levels), test_ravkits.wotr_sheet((9, 11), levels, 1, 0x02 << 2, (K("axe"),))))
    return out


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class KitGearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def setUp(self):
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x100000)
        self.mu.mem_write(TSR * 16, self.image)
        self.mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))  # (hlt: where the routine returns)
        self.mu.mem_write(GDS * 16 + ITEM_TYPES_PTR, struct.pack("<HH", TYPES_AT, GDS))
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        old = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = old | game.RULE_KITS | game.RULE_SPECIALIZE
        self.addCleanup(setattr, game, "RULES_IN_FORCE", old)
        self.rules(game.RULES_IN_FORCE >> 16, game.RULES_IN_FORCE & 0xFFFF)  # (the half-giants' hands among them)
        self.at = {}  # (a sequel type of each kind + 1: 0 for none)
        for t in range(ravager.GAME_TYPES + ravager.MOD_TYPES):
            kind = specialize.kind_of(t)
            self.at.setdefault(0 if kind is None else kind + 1, t)

    def rules(self, hi: int, lo: int = 0) -> None:
        hdr = TSR * 16 + self.sym["hdr"]
        self.mu.mem_write(hdr + test_ravkits.RULES_HI, struct.pack("<H", hi))
        self.mu.mem_write(hdr + 170, struct.pack("<H", lo))

    @staticmethod
    def sl(fn, *args, **kw):
        """restrict's FN with the mod's cahulaks counted as the cahulaks too (the layout's CAHULAKS_TYPES has
        the sequel's alone; each wotr_sheet puts it back)."""
        old = game.CAHULAKS_TYPES
        game.CAHULAKS_TYPES = CAHULAKS
        try:
            return fn(*args, **kw)
        finally:
            game.CAHULAKS_TYPES = old

    def put_type(self, t: int, rec: bytes) -> None:
        self.mu.mem_write(GDS * 16 + TYPES_AT + t * ravager.TYPE_SIZE, sequel(rec))

    def call(self, name: str, sheet: bytes, t: int, off_hand: bool = False) -> bool:
        self.mu.mem_write(SS * 16 + 0x500, sheet)
        self.mu.mem_write(TSR * 16 + self.sym["kf_off_hand"], bytes((int(off_hand),)))
        self.mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
        for reg, value in dict(cs=TSR, ds=GDS, es=SS, ebx=0x500, edx=t, ss=SS, esp=0x7FC, eflags=0x2).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[name], TSR * 16 + 0xFFF0)
        return bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 1)

    def cases(self):
        """(sequel type, record): each weapon record at a type of each kind (the cahulaks' three types),
        the gear at a type of no kind, and the mod's own 33 types as they are."""
        for kind in sorted(k for k in self.at if k):
            types = sorted(CAHULAKS) if kind == K("cahulaks") + 1 else [self.at[kind]]
            for t in types:
                for rec in WEAPONS:
                    yield t, rec
        for rec in GEAR + WEAPONS:
            yield self.at[0], rec
        for k, typ in enumerate(npcitems.TYPES[:ravager.MOD_TYPES]):
            yield ravager.GAME_TYPES + k, bytes.fromhex(typ) if isinstance(typ, str) else typ

    def test_forbids_and_allows(self):
        """KIT_FORBIDS (to either hand) and KIT_ALLOWS are restrict.kit_forbids and restrict.kit_allows for
        every sheet and item; with the rule off, neither ever."""
        seen_forbid, seen_allow = set(), set()
        cases = list(self.cases())
        for name, sheet in sheets():
            ids = kitpages.kit_ids(sheet)
            for t, rec in cases:
                self.put_type(t, rec)
                for off_hand in (False, True):
                    want = self.sl(restrict.kit_forbids, sheet, t, rec, off_hand=off_hand)
                    with self.subTest(sheet=name, type=t, rec=rec[:0x10].hex(), off_hand=off_hand):
                        self.assertEqual(self.call("kit_forbids", sheet, t, off_hand), want)
                    if want:
                        seen_forbid.update(ids)
                want = self.sl(restrict.kit_allows, sheet, t, rec)
                with self.subTest(sheet=name, type=t, rec=rec[:0x10].hex(), allows=True):
                    self.assertEqual(self.call("kit_allows", sheet, t), want)
                if want:
                    seen_allow.update(ids)
        self.assertTrue({kits.RAVAGER, kits.TWIN_BLADE, kits.BRUTE, kits.STALKER, kits.ASSASSIN, kits.SHINOBI,
                         kits.SHADOWBLADE, kits.POISONER, kits.SPELLARCHER, kits.GROVE_WARDEN, kits.SEEKER,
                         kits.LIFEBINDER, kits.BATTLE_DANCER, kits.GHETTO, kits.RESCUER, kits.BATTLE_MAGE,
                         kits.HEALER} <= seen_forbid, seen_forbid)
        self.assertEqual(seen_allow, {kits.BATTLE_MAGE, kits.BATTLE_DANCER})
        self.rules(0)
        sheet = test_ravkits.wotr_sheet((9,), (5,), 2, 3)  # (a Ravager: a shield)
        self.put_type(self.at[0], GEAR[0])
        self.assertFalse(self.call("kit_forbids", sheet, self.at[0]))
        mage = test_ravkits.wotr_sheet((11,), (5,), 1, 2, (K("axe"),))
        self.put_type(self.at[K("axe") + 1], WEAPONS[0])
        self.assertFalse(self.call("kit_allows", mage, self.at[K("axe") + 1]))

    def test_elementalist_weapons(self):
        """CLASS_FORBIDS lets an Elementalist use its second sphere's weapons as well as its own sphere's
        (restrict.allowed's elementalist_sphere): a fire cleric with water bone and wood, with earth
        stone and metal too, with air a missile weapon; another fire cleric not; none with the rule off."""
        mace = self.at[K("mace") + 1]
        for second in range(5):
            sheet = bytearray(test_ravkits.wotr_sheet((3,), (5,), 1, 1))  # (a fire cleric, an Elementalist)
            sheet[kits.SPHERE2] = second
            plain = bytearray(test_ravkits.wotr_sheet((3,), (5,), 1, 0))
            plain[kits.SPHERE2] = second
            for rec in WEAPONS:
                self.put_type(mace, rec)
                for s in (bytes(sheet), bytes(plain)):
                    want = not self.sl(restrict.allowed, s, mace, rec)
                    with self.subTest(second=second, rec=rec[:0x10].hex(), kit=s[0x3D]):
                        self.assertEqual(self.call("class_forbids", s, mace), want)
        sheet = bytearray(test_ravkits.wotr_sheet((3,), (5,), 1, 1))
        sheet[kits.SPHERE2] = 4  # (water)
        self.put_type(mace, record(MELEE, restrict.BONE))
        self.assertFalse(self.call("class_forbids", bytes(sheet), mace))
        self.rules(0, game.RULE_RESTRICT & 0xFFFF)
        self.assertTrue(self.call("class_forbids", bytes(sheet), mace))

    def can_use(self, sheet: bytes, t: int, game_yes: bool, slot: int) -> int:
        """CU_SITE's answer ([BP-1]) for the sequel's AL GAME_YES, the equip routine's slot SLOT."""
        frame, caller = 0x600, 0x640  # (the can-use routine's BP, the equip routine's)
        self.mu.mem_write(SS * 16 + 0x500, sheet)
        self.mu.mem_write(SS * 16 + frame, struct.pack("<H", caller))
        self.mu.mem_write(SS * 16 + frame + 0x0A, struct.pack("<HH", 0x500, SS))
        self.mu.mem_write(SS * 16 + frame - 1, b"\xEE")
        self.mu.mem_write(SS * 16 + caller + 8, struct.pack("<H", slot))
        self.mu.mem_write(SS * 16 + 0x5F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2))  # (the INT's frame)
        for reg, value in dict(cs=TSR, ds=GDS, es=0, ebx=0, edx=t, eax=int(game_yes), ss=SS, esp=0x5F0, ebp=frame,
                               eflags=0x2).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym["cu_site"], TSR * 16 + 0xFFF0)
        return self.mu.mem_read(SS * 16 + frame - 1, 1)[0]

    def test_cu_site(self):
        """CU_SITE as SL's PROBE_CAN_USE: (the game's lists or the kit's own) and not the kit's limits, to the
        off hand too, and (the kit's own or not the classes' limits): a Battle Mage's axe of its weapon
        spec in the right hand and leather allowed where the game's lists say no, nothing in its off hand;
        a Ravager's shield and bow refused where the game's say yes; a plain preserver's axe as the game's
        lists (no), a plain fighter's shield yes; a Healer's club not to the off hand."""
        axe, none = self.at[K("axe") + 1], self.at[0]
        mage = test_ravkits.wotr_sheet((11,), (5,), 1, 2, (K("axe"),))
        plain = test_ravkits.wotr_sheet((11,), (5,), 1, 0, (K("axe"),))
        ravager_ = test_ravkits.wotr_sheet((9,), (5,), 2, 3)
        fighter = test_ravkits.wotr_sheet((9,), (5,), 2, 0)
        healer = bytearray(test_ravkits.wotr_sheet((4,), (5,), 1, 2))  # (a water cleric's Healer)
        right, left = 7, 14
        self.put_type(axe, record(MELEE, restrict.METAL))
        self.assertEqual(self.can_use(mage, axe, False, right), 1)
        self.assertEqual(self.can_use(mage, axe, False, left), 0)
        self.assertEqual(self.can_use(plain, axe, False, right), 0)
        self.put_type(none, record(0, LEATHER, ARMOUR, 9))
        self.assertEqual(self.can_use(mage, none, False, 13), 1)
        self.put_type(none, record(SHIELD, restrict.METAL, ARMOUR))
        self.assertEqual(self.can_use(ravager_, none, True, left), 0)
        self.assertEqual(self.can_use(fighter, none, True, left), 1)
        bow = self.at[K("bow") + 1]
        self.put_type(bow, record(MISSILE, restrict.WOOD))
        self.assertEqual(self.can_use(ravager_, bow, True, 6), 0)
        self.assertEqual(self.can_use(fighter, bow, True, 6), 1)
        club = self.at[K("club") + 1]
        self.put_type(club, record(MELEE, restrict.WOOD))
        self.assertEqual(self.can_use(bytes(healer), club, True, right), 1)
        self.assertEqual(self.can_use(bytes(healer), club, True, left), 0)
        counts = {n: struct.unpack_from("<H", self.mu.mem_read(TSR * 16 + self.sym[n], 2))[0]
                  for n in ("kit_refused", "kit_allowed")}
        self.assertGreater(counts["kit_refused"], 0)
        self.assertGreater(counts["kit_allowed"], 0)
        self.rules(0, game.RULE_RESTRICT & 0xFFFF)  # (the kits off: the game's and the classes' alone)
        self.assertEqual(self.can_use(ravager_, bow, True, 6), 1)
        self.assertEqual(self.can_use(mage, axe, False, right), 0)


if __name__ == "__main__":
    unittest.main()
