"""DSCLOG2's PROTECTION in Wake of the Ravager (PROT_AC and PROT_SAVE, run in an emulated CPU): the
party transfer's rings, cloak, bracers and robes of protection as AD&D (and Shattered Lands' DSCLOG) has
them, on every mix of two rings, a cloak, bracers, a robe, armour (none, leather, magical leather,
metal) and a shield. Needs nasm and unicorn, else skipped."""

import itertools
import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, npcitems, ravager  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
TSR, GAME_DS, SS, TYPES, ITEMS, CREATURES = 0x1000, 0x5000, 0x4000, 0x8000, 0x9000, 0xA000
FIGHTERS = GAME_DS + 0x3F49 - 0x47E0  # (DSCLOG2's FIGHTERS_SEG)
FIGHTERS_OFF, ITEM_SIZE, CREATURE_SIZE = 0xC33, 0x17, 0x31
RING, CLOAK, BRACERS, ROBE = 45, ravager.mod_type(game.CLOAK_TYPE), ravager.mod_type(game.BRACERS_TYPE), \
    ravager.mod_type(game.ROBE_TYPE)
PLATE, SHIELD, LEATHER = ravager.mod_type(game.PLATE_CHEST_TYPE), ravager.mod_type(game.METAL_SHIELD_TYPE), 140
FINGER, FINGER2, BACK, ARMS, CHEST, RIGHT_HAND, LEFT_HAND, FOOT, WAIST, NECK = 4, 11, 12, 0, 9, 3, 10, 13, 5, 8
BOOTS = ravager.mod_type(game.SPEED_BOOTS_TYPE)
COMBATANT, THING, LIST = 7, 0x300, 0x301  # (the combatant attacked or saving, its creature's list)


def type_table() -> bytes:
    """The sequel's types as far as it matters here: its Ring (45, of no AC), the mod's after them,
    and a leather chest armour (LEATHER: the plate's, of leather)."""
    table = bytearray(ravager.TYPE_SIZE * ravager.GAME_TYPES)
    table[RING * 15:RING * 15 + 15] = bytes.fromhex("000001fa4009000000000000ff1f00")
    table += b"".join(ravager.wotr_type(t) for t in npcitems.TYPES)
    leather = bytearray(table[PLATE * 15:PLATE * 15 + 15])
    leather[4] = (leather[4] & 0xF0) | 5
    table += bytes((LEATHER - len(table) // 15) * 15) + leather
    return bytes(table)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class ProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        cls.consts = {}
        with open(ASM) as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "equ" and parts[0].endswith("_PTR"):
                    cls.consts[parts[0]] = int(parts[2], 16)

    def machine(self, worn):
        """A CPU with creature 0 wearing WORN, (type, slot, plus) each, items 0 on, as combatant
        COMBATANT."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        for name, seg in (("ITEMS_PTR", ITEMS), ("CREATURES_PTR", CREATURES), ("ITEM_TYPES_PTR", TYPES)):
            mu.mem_write(GAME_DS * 16 + self.consts[name], struct.pack("<HH", 0, seg))
        mu.mem_write(TYPES * 16, type_table())
        mu.mem_write(FIGHTERS * 16 + FIGHTERS_OFF + COMBATANT * 3, struct.pack("<BH", 2, 0))
        mu.mem_write(FIGHTERS * 16 + FIGHTERS_OFF + LIST * 3, struct.pack("<BH", 1, 0 if worn else 9999))
        creature = bytearray(CREATURE_SIZE)
        struct.pack_into("<HHH", creature, 8, LIST, 9999, 9999)
        mu.mem_write(CREATURES * 16, bytes(creature))
        for n, (typ, slot, plus) in enumerate(worn):
            item = bytearray(ITEM_SIZE)
            struct.pack_into("<H", item, 4, n + 1 if n + 1 < len(worn) else 9999)
            struct.pack_into("<H", item, 0x0A, typ)
            item[0x13], item[0x16] = slot, plus & 0xFF
            mu.mem_write(ITEMS * 16 + n * ITEM_SIZE, bytes(item))
        return mu

    def call(self, mu, site, **regs):
        """Run SITE as the game's INT would reach it (an IRET frame to a HLT); BP 600h in SS."""
        mu.mem_write(SS * 16 + 0x7FA, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        values = dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7FA, ebp=0x600, eflags=0x2)
        values.update(regs)
        for name, value in values.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(TSR * 16 + self.sym[site], TSR * 16 + 0xFFF0)

    def call_to(self, mu, site, ways, **regs):
        """Run SITE as the game's INT would reach it, its way back BACK; it ends at BACK + one of WAYS
        (which is returned)."""
        back = 0xF000
        mu.mem_write(SS * 16 + 0x7FA, struct.pack("<HHH", back, TSR, 0x2))
        values = dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7FA, ebp=0x600, eflags=0x2)
        values.update(regs)
        for name, value in values.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        ends = {TSR * 16 + back + w: w for w in ways}
        mu.hook_add(UC_HOOK_CODE, lambda uc, address, size, data: uc.emu_stop() if address in ends else None)
        mu.emu_start(TSR * 16 + self.sym[site], 0, count=200000)
        return ends[mu.reg_read(r.UC_X86_REG_CS) * 16 + mu.reg_read(r.UC_X86_REG_IP)]

    def ac_counts(self, mu, worn, n, other=0):
        """PROT_AC on worn item N: whether it counts for AC (AX bit 80h), and [BP-6] after."""
        typ = worn[n][0]
        mu.mem_write(SS * 16 + 0x600 - 6, struct.pack("<h", other))
        self.call(mu, "prot_ac", es=TYPES, ebx=typ * 15, ecx=typ, edx=n, esi=COMBATANT, eax=0xFFFF)
        ax = mu.reg_read(r.UC_X86_REG_AX)
        self.assertEqual(ax & 0xFF7F, type_table()[typ * 15 + 0x0B] & 0x7F)
        return bool(ax & 0x80), struct.unpack("<h", mu.mem_read(SS * 16 + 0x600 - 6, 2))[0]

    def save(self, mu, spell):
        mu.mem_write(SS * 16 + 0x606, struct.pack("<H", COMBATANT))
        mu.mem_write(SS * 16 + 0x614, struct.pack("<H", spell))
        self.call(mu, "prot_save", esi=0, edi=0x1234)
        return struct.unpack("<h", struct.pack("<H", mu.reg_read(r.UC_X86_REG_DI)))[0], \
            mu.reg_read(r.UC_X86_REG_SI)

    def test_every_mix(self):
        mixes = itertools.product((None, 1, 2, -1), (None, 1, 2), (None, 1), (None, "leather", "magic", "metal"),
                                  (False, True), (None, 2), (None, 1, 2))
        checked = 0
        for left, right, cloak, armour, shield, bracers, robe in mixes:
            worn = []
            if left is not None:
                worn.append((RING, FINGER, left))
            if right is not None:
                worn.append((RING, FINGER2, right))
            if cloak:
                worn.append((CLOAK, BACK, cloak))
            if armour:
                worn.append((PLATE if armour == "metal" else LEATHER, CHEST, 1 if armour == "magic" else 0))
            if shield:
                worn.append((SHIELD, LEFT_HAND, 0))
            if bracers:
                worn.append((BRACERS, ARMS, bracers))
            if robe:
                worn.append((ROBE, CHEST, robe))
            magic, metal = armour == "magic", armour == "metal"
            l_plus, r_plus = max(left or 0, 0), max(right or 0, 0)
            want = {
                "left": l_plus > 0 and not magic and l_plus >= r_plus,
                "right": r_plus > 0 and not magic and r_plus > l_plus,
                "cloak": not (magic or metal or shield),
                "bracers": not armour,
            }
            mu = self.machine(worn)
            with self.subTest(worn=worn):
                for n, (typ, slot, plus) in enumerate(worn):
                    counts, other = self.ac_counts(mu, worn, n, other=3)
                    if typ == RING:
                        self.assertEqual(counts, want["left" if slot == FINGER else "right"])
                    elif typ == CLOAK:
                        self.assertEqual(counts, want["cloak"])
                    elif typ == BRACERS:
                        self.assertEqual(counts, want["bracers"])
                    elif typ == ROBE:
                        self.assertEqual((counts, other), (False, 3 - (0 if armour else plus)))  # (on top)
                    else:
                        self.assertEqual(counts, bool(type_table()[typ * 15 + 0x0B] & 0x80))
                    if typ != ROBE:
                        self.assertEqual(other, 3)
                for spell, against in ((5, True), (0xEB, False)):
                    got, si = self.save(mu, spell)
                    expect = max(l_plus, r_plus) + (cloak if want["cloak"] and cloak else 0) \
                        + (1 if robe == 2 or (robe == 1 and against) else 0)
                    self.assertEqual((got, si), (expect, COMBATANT))
            checked += 1
        self.assertEqual(checked, 4 * 3 * 2 * 4 * 2 * 2 * 3)

    def test_not_a_creature(self):
        """A combatant that isn't a creature (kind 1): the item's own answer, and a save's DI 0."""
        mu = self.machine([(RING, FINGER, 2)])
        mu.mem_write(FIGHTERS * 16 + FIGHTERS_OFF + COMBATANT * 3, bytes((1,)))
        counts, _ = self.ac_counts(mu, [(RING, FINGER, 2)], 0)
        self.assertFalse(counts)
        self.assertEqual(self.save(mu, 5), (0, COMBATANT))

    def test_boots_of_speed(self):
        """The Boots of Speed on the feet: AC 2 better ([BP-6]) in a fight unless Cannot Move, Paralyzed or
        Slowed (either of the sequel's two), none out of a fight; a turn's movement doubled (BOOTS_MOVE)."""
        worn = [(BOOTS, FOOT, 0)]
        for fight, effect, want in ((1, None, 1), (0, None, 0), (1, 66, 0), (1, 69, 0), (1, 52, 0), (1, 91, 0),
                                    (1, 9, 1)):
            mu = self.machine(worn)
            mu.mem_write(GAME_DS * 16 + 0x13FA, bytes((fight,)))
            effects = (GAME_DS - (0x47E0 - 0x3E71)) * 16
            mu.mem_write(GAME_DS * 16 + 0x2100, struct.pack("<H", 0 if effect is None else 1))
            if effect is not None:
                mu.mem_write(effects + 0x24D, struct.pack("<HHHB", COMBATANT, 0, 0, effect))
            with self.subTest(fight=fight, effect=effect):
                counts, other = self.ac_counts(mu, worn, 0, other=3)
                self.assertEqual((counts, other), (False, 3 - 2 * want))
        for feet, want in ((FOOT, 120), (ARMS, 60)):
            mu = self.machine([(BOOTS, feet, 0)])
            mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
            for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7FC, eax=60, edi=COMBATANT,
                                    eflags=0x2).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.emu_start(TSR * 16 + self.sym["boots_move"], TSR * 16 + 0xFFF0)
            with self.subTest(slot=feet):
                self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), want)

    def test_veiled_robe_slots(self):
        """VEILED_SLOT (ADND_SLOTS's end): a preserver's (class 11) slot more at spell levels 1-3 where it has
        any, with the Veiled Robe (+2) on the chest; not the Ashen Robe (+1), another class, level 4, none."""
        cases = [(2, 11, 1, 2, 3), (2, 11, 3, 1, 2), (2, 11, 4, 1, 1), (2, 11, 2, 0, 0), (1, 11, 1, 2, 2),
                 (2, 2, 1, 2, 2), (None, 11, 1, 2, 2)]
        for robe, cls, level, slots, want in cases:
            mu = self.machine([(ROBE, CHEST, robe)] if robe else [])
            mu.mem_write(SS * 16 + 0x600 - 6, struct.pack("<H", COMBATANT))
            mu.mem_write(SS * 16 + 0x608, struct.pack("<HHH", cls, 0, level))
            mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
            for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7FC, ebp=0x600, eax=slots, esi=0x55,
                                    eflags=0x2).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.emu_start(TSR * 16 + self.sym["veiled_slot"], TSR * 16 + 0xFFF0)
            with self.subTest(robe=robe, cls=cls, level=level, slots=slots):
                self.assertEqual((mu.reg_read(r.UC_X86_REG_AX), mu.reg_read(r.UC_X86_REG_SI)), (want, 0x55))

    def test_girdles(self):
        """ITEM_REAR (from MISSILE_REAR): the Girdle of Back Defense at the waist takes back an attack from
        behind and a backstab (2 each on the THAC0 [BP-1Eh]); the Golden Girdle of Urnst makes a melee long or
        short sword 3 worse, not an axe nor a missile; a girdle in the pack does nothing."""
        def run(worn, rear, stab, weapon, melee=1):
            mu = self.machine(worn)
            mu.mem_write(SS * 16 + 0x600 - 0x21, bytes((stab,)))
            mu.mem_write(SS * 16 + 0x600 - 0x19, bytes((rear,)))
            mu.mem_write(SS * 16 + 0x600 - 0x1E, struct.pack("<h", 10))
            mu.mem_write(SS * 16 + 0x600 - 4, struct.pack("<H", weapon))
            mu.mem_write(SS * 16 + 0x600 + 0x0E, struct.pack("<H", melee))
            mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
            for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7FC, ebp=0x600, edi=COMBATANT, esi=0x22,
                                    eflags=0x2).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.emu_start(TSR * 16 + self.sym["item_rear"], TSR * 16 + 0xFFF0)
            return (mu.mem_read(SS * 16 + 0x600 - 0x19, 1)[0], mu.mem_read(SS * 16 + 0x600 - 0x21, 1)[0],
                    struct.unpack("<h", mu.mem_read(SS * 16 + 0x600 - 0x1E, 2))[0])
        back, urnst = ravager.mod_type(game.BACK_GIRDLE_TYPE), ravager.mod_type(game.URNST_GIRDLE_TYPE)
        long_sword, axe = 16, 8  # (the sequel's types: KIND_OF_TYPE's long sword and axe)
        for worn, rear, stab, weapon, melee, want in (
                ([(back, WAIST, 0)], 1, 1, axe, 1, (0, 0, 14)), ([(back, WAIST, 0)], 1, 0, axe, 1, (0, 0, 12)),
                ([(back, 20, 0)], 1, 1, axe, 1, (1, 1, 10)), ([], 1, 1, axe, 1, (1, 1, 10)),
                ([(urnst, WAIST, 0)], 0, 0, long_sword, 1, (0, 0, 13)), ([(urnst, WAIST, 0)], 0, 0, axe, 1, (0, 0, 10)),
                ([(urnst, WAIST, 0)], 0, 0, long_sword, 2, (0, 0, 10)), ([(urnst, WAIST, 0)], 1, 0, long_sword, 1, (1, 0, 13))):
            with self.subTest(worn=worn, rear=rear, stab=stab, weapon=weapon, melee=melee):
                self.assertEqual(run(worn, rear, stab, weapon, melee), want)

    def stealth_run(self, rules, bits, member=0, thief=True, melee=1, weapon_weight=0x10, obj=0,
                    rear=0, stab=0, thac0=10):
        """MISSILE_REAR (its STEALTH) for party member MEMBER (SI) attacking COMBATANT (DI), wearing
        nothing: creature 1 (THAC0 10, [BP-0Eh]) with sheet 2 ([BP-12h]; a thief or not), weapon type 3
        ([BP-4], its byte +2 WEAPON_WEIGHT); RULES and BITS (STEALTH) in the header; the game's flags
        REAR, STAB, OBJ and THAC0 [BP-1Eh] as it left them. ((rear, stab, THAC0, AL), STEALTH, STEALTH_USED)."""
        mu = self.machine([])
        sheets = 0xB000
        mu.mem_write(GAME_DS * 16 + self.consts["SHEETS_PTR"], struct.pack("<HH", 0, sheets))
        mu.mem_write(sheets * 16 + 2 * ravager.SHEET_SIZE + 0x10, struct.pack("<H", 0x400 if thief else 0x100))
        mu.mem_write(CREATURES * 16 + 1 * CREATURE_SIZE + 0x16, bytes((10,)))
        mu.mem_write(TYPES * 16 + 3 * 15 + 2, bytes((weapon_weight,)))
        bp = SS * 16 + 0x600
        mu.mem_write(bp - 0x0E, struct.pack("<H", 1))
        mu.mem_write(bp - 0x12, struct.pack("<H", 2))
        mu.mem_write(bp - 4, struct.pack("<H", 3))
        mu.mem_write(bp + 0x0E, struct.pack("<H", melee))
        mu.mem_write(bp - 0x1A, bytes((obj,)))
        mu.mem_write(bp - 0x19, bytes((rear,)))
        mu.mem_write(bp - 0x21, bytes((stab,)))
        mu.mem_write(bp - 0x1E, struct.pack("<h", thac0))
        mu.mem_write(TSR * 16 + self.sym["rules"], struct.pack("<H", rules))
        mu.mem_write(TSR * 16 + self.sym["stealth"], struct.pack("<H", bits))
        self.call(mu, "missile_rear", esi=member, edi=COMBATANT, eax=0x1100)
        got = (mu.mem_read(bp - 0x19, 1)[0], mu.mem_read(bp - 0x21, 1)[0],
               struct.unpack("<h", mu.mem_read(bp - 0x1E, 2))[0], mu.reg_read(r.UC_X86_REG_AX))
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SI), mu.reg_read(r.UC_X86_REG_DI)), (member, COMBATANT))
        return got, struct.unpack("<H", mu.mem_read(TSR * 16 + self.sym["stealth"], 2))[0], \
            struct.unpack("<H", mu.mem_read(TSR * 16 + self.sym["stealth_used"], 2))[0]

    def test_stealth(self):
        """MISSILE_REAR's STEALTH (SL's PROBE_STEALTH): with RULE_STEALTH, a hidden party member's attack is
        from behind (2 off THAC0) and, for a thief in melee with a light weapon, a backstab (2 more); the bit
        is cleared and counted; a hidden archer's shot stays from behind; an object has no back. Without
        the rule, or for someone not hidden, nothing changes; a missile's own "from behind" is taken back."""
        on = game.RULE_STEALTH
        for args, want in (
                (dict(rules=0, bits=1), ((0, 0, 10, 0x1100), 1, 0)),
                (dict(rules=on, bits=1), ((1, 1, 6, 0x1101), 0, 1)),
                (dict(rules=on, bits=4, member=2), ((1, 1, 6, 0x1101), 0, 1)),
                (dict(rules=on, bits=1, thief=False), ((1, 0, 8, 0x1101), 0, 1)),
                (dict(rules=on, bits=1, weapon_weight=0x30), ((1, 0, 8, 0x1101), 0, 1)),
                (dict(rules=on, bits=1, melee=2), ((1, 0, 8, 0x1101), 0, 1)),
                (dict(rules=on, bits=1, obj=1), ((0, 0, 10, 0x1100), 0, 1)),
                (dict(rules=on, bits=2), ((0, 0, 10, 0x1100), 2, 0)),
                (dict(rules=on, bits=0, member=5), ((0, 0, 10, 0x1100), 0, 0)),
                (dict(rules=on, bits=1, rear=1, thac0=8), ((1, 1, 6, 0x1101), 0, 1)),  # (the game's own rear)
                (dict(rules=on, bits=0, rear=1, thac0=8, melee=2), ((0, 0, 10, 0x1100), 0, 0)),  # (a shot's)
                (dict(rules=on, bits=0, rear=1, stab=1, thac0=6), ((1, 1, 6, 0x1101), 0, 0)),
                # REAR_FRESH: flags an earlier attack left, not paid for this one, cleared
                (dict(rules=on, bits=0, rear=1, stab=1, thac0=10), ((0, 0, 10, 0x1100), 0, 0)),
                (dict(rules=on, bits=0, rear=1, stab=1, thac0=8), ((1, 0, 8, 0x1101), 0, 0)),
                (dict(rules=on, bits=1, rear=1, stab=1, thac0=10), ((1, 1, 6, 0x1101), 0, 1))):
            with self.subTest(**args):
                self.assertEqual(self.stealth_run(**args), want)

    def test_amulet(self):
        """AMULET_MR: the Amulet of Magic Resistance at the neck adds 15 to [BP-2]; ZF handed back as
        "cmp word [bp-2],0" sets it."""
        amulet = ravager.mod_type(game.MR_AMULET_TYPE)
        for worn, before, after in (([(amulet, NECK, 0)], 0, 15), ([(amulet, NECK, 0)], 20, 35), ([], 0, 0),
                                    ([], 30, 30), ([(amulet, 20, 0)], 0, 0)):
            mu = self.machine(worn)
            mu.mem_write(SS * 16 + 0x600 - 2, struct.pack("<h", before))
            mu.mem_write(SS * 16 + 0x606, struct.pack("<H", COMBATANT))
            self.call(mu, "amulet_mr", esi=0x33)
            with self.subTest(worn=worn, before=before):
                self.assertEqual(struct.unpack("<h", mu.mem_read(SS * 16 + 0x600 - 2, 2))[0], after)
                self.assertEqual(bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40), after == 0)
                self.assertEqual(mu.reg_read(r.UC_X86_REG_SI), 0x33)

    def test_weapon_cast(self):
        """WEAPON_CAST: the game's "push 6 / push word [bp-18h]" made under the IRET frame, the cast
        marked a weapon's (TH_WEAPON), every register kept."""
        mu = self.machine([])
        mu.mem_write(SS * 16 + 0x600 - 0x18, struct.pack("<H", 174))
        self.call(mu, "weapon_cast", eax=0x1111, ebx=0x2222)
        sp = mu.reg_read(r.UC_X86_REG_SP)
        self.assertEqual(sp, 0x800 - 4)
        self.assertEqual(struct.unpack("<HH", mu.mem_read(SS * 16 + sp, 4)), (174, 6))
        self.assertEqual((mu.reg_read(r.UC_X86_REG_AX), mu.reg_read(r.UC_X86_REG_BX)), (0x1111, 0x2222))
        self.assertEqual(mu.mem_read(TSR * 16 + self.sym["th_weapon"], 1)[0], 1)

    def arrow_machine(self, creature, classes, levels, power, spell):
        """Combatant 9 (DI, the attacker: creature CREATURE, its sheet 2 of CLASSES and LEVELS) hitting
        with item 0 (SI, the weapon: its power POWER), the hit's spell SPELL ([BP-18h]: the weapon's, or
        its ammunition's)."""
        mu = self.machine([(RING, RIGHT_HAND, 0)])
        mu.mem_write(ITEMS * 16 + 0x10, struct.pack("<H", power))
        mu.mem_write(SS * 16 + 0x600 - 0x18, struct.pack("<H", spell))
        mu.mem_write(GAME_DS * 16 + 0x4206, struct.pack("<H", 5))  # (the target: not the archer)
        mu.mem_write(FIGHTERS * 16 + FIGHTERS_OFF + 9 * 3, struct.pack("<BH", 2, creature))
        sheets = 0xB000
        mu.mem_write(GAME_DS * 16 + self.consts["SHEETS_PTR"], struct.pack("<HH", 0, sheets))
        mu.mem_write(CREATURES * 16 + creature * CREATURE_SIZE + 4, struct.pack("<H", 2))
        mu.mem_write(sheets * 16 + 2 * ravager.SHEET_SIZE + 0x1B, bytes(classes) + bytes(levels))
        return mu

    def arrow_level(self, *shot):
        """WEAPON_CAST's level pushed for SHOT (arrow_machine's), the spell under it, registers kept."""
        mu = self.arrow_machine(*shot)
        self.call(mu, "weapon_cast", eax=0x1111, ebx=0x2222, esi=0, edi=9)
        sp = mu.reg_read(r.UC_X86_REG_SP)
        self.assertEqual(sp, 0x800 - 4)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_SI,
                                                   r.UC_X86_REG_DI)], [0x1111, 0x2222, 0, 9])
        got_spell, level = struct.unpack("<HH", mu.mem_read(SS * 16 + sp, 4))
        self.assertEqual(got_spell, shot[-1])
        return level

    def arrow_spell(self, *shot, melee=2):
        """PLAIN_ARROW for SHOT (its spell given as the game's AX, the spell + 1; [BP+16h] MELEE, 1 a melee
        hit): [BP-18h] after."""
        mu = self.arrow_machine(*shot)
        mu.mem_write(SS * 16 + 0x600 - 0x18, bytes(2))
        mu.mem_write(SS * 16 + 0x600 + 0x16, struct.pack("<H", melee))
        self.call(mu, "plain_arrow", eax=shot[-1] + 1, ebx=0x2222, esi=0, edi=9)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_SI,
                                                   r.UC_X86_REG_DI, r.UC_X86_REG_SP)],
                         [shot[-1] + 1, 0x2222, 0, 9, 0x800])
        return struct.unpack("<H", mu.mem_read(SS * 16 + 0x600 - 0x18, 2))[0]

    def test_spell_arrows(self):
        """The spell arrows (the user's choice, 2026-11-23): an arrow's Chill Touch, Shocking Grasp or
        Vampiric Touch (not the weapon's, item SI's, own spell: its ammunition's) cast at a party archer's
        preserver level; for a party archer with no preserver class not cast at all (PLAIN_ARROW: the
        spell past the game's, 148h, which the game skips); at a foe's highest level. A weapon's own
        spell, and any other spell, at 6 and kept."""
        PRES, FIGHTER, THIEF = 11, 2, 7
        pres, fighter, foe = (0, (FIGHTER, PRES, 0), (7, 5, 0)), (1, (FIGHTER, THIEF, 0), (7, 8, 0)), \
            (12, (FIGHTER, THIEF, 0), (4, 9, 0))
        for spell in (3, 10, 38):
            arrow = (0, spell)  # (a bow of no spell)
            self.assertEqual(self.arrow_level(*pres, *arrow), 5)
            self.assertEqual(self.arrow_spell(*pres, *arrow), spell)
            self.assertEqual(self.arrow_spell(*fighter, *arrow), 0x148)
            self.assertEqual(self.arrow_level(*foe, *arrow), 9)
            self.assertEqual(self.arrow_spell(*foe, *arrow), spell)
            self.assertEqual(self.arrow_level(*pres, spell + 4, spell), 5)  # (a bow of another spell)
            self.assertEqual(self.arrow_level(*pres, spell + 1, spell), 6)  # (the weapon's own)
            self.assertEqual(self.arrow_spell(*fighter, spell + 1, spell), spell)
        self.assertEqual(self.arrow_level(*fighter, 0, 174), 6)  # (not an arrow's)
        self.assertEqual(self.arrow_spell(*fighter, 0, 174), 174)

    def test_melee_casts_the_weapons_own(self):
        """PLAIN_ARROW: a melee hit casts the weapon's own spell alone, never the quiver's arrows' (the game
        takes those first: a sword hit with Shocking Arrows in the quiver cast Shocking Grasp, and the game
        died a few turns later); whoever hits, any spell; MELEE_ARROWS counts them."""
        pres, foe = (0, (2, 11, 0), (7, 5, 0)), (12, (2, 7, 0), (4, 9, 0))
        for who in (pres, foe):
            for spell in (10, 3, 174):
                with self.subTest(who=who[0], spell=spell):
                    self.assertEqual(self.arrow_spell(*who, 0, spell, melee=1), 0x148)  # (the arrows')
                    self.assertEqual(self.arrow_spell(*who, 200, spell, melee=1), 0x148)  # (a sword of another)
                    self.assertEqual(self.arrow_spell(*who, spell + 1, spell, melee=1), spell)  # (its own)

    def test_join_ready(self):
        """JOIN_READY: each worn item with a spell (+10h) of the member on show readied once through the
        game's routine (5E8h:39h: the creature, the item), none in the backpack (15) or without a
        spell; the compare's ZF in the INT's frame, every register kept."""
        worn = [(LEATHER, CHEST, 0), (RING, FINGER, 0), (RING, 15, 0), (RING, NECK, 0)]
        mu = self.machine(worn)
        for n, power in enumerate((139, 14, 36, 0)):  # (the backpack's and the last's not readied)
            mu.mem_write(ITEMS * 16 + n * ITEM_SIZE + 0x10, struct.pack("<H", power))
        stub = GAME_DS + 0x4713 - 0x47E0
        log = 0x200  # (in the stub's segment: a count of calls, then (creature, item) each)
        ready = bytes.fromhex("558bec5053" "2e8b1e0002" "8b4606" "2e898702" "02" "8b4608" "2e898704" "02"
                              "2e8306000204" "5b585dcb")
        mu.mem_write(stub * 16 + 0x39, ready)
        mu.mem_write(stub * 16 + log, bytes(2))
        mu.mem_write((GAME_DS + 0x3E71 - 0x47E0) * 16 + 0x0B44, struct.pack("<H", 0))
        for flag, zf in ((0, 0x40), (1, 0)):
            mu.mem_write(stub * 16 + log, bytes(2))
            mu.mem_write(GAME_DS * 16 + 0x13FA, bytes((flag,)))
            self.call(mu, "join_ready", eax=0x1111, ebx=0x2222, esi=0x3333, edi=0x4444)
            calls = struct.unpack("<H", mu.mem_read(stub * 16 + log, 2))[0] // 4
            got = [struct.unpack_from("<HH", mu.mem_read(stub * 16 + log + 2 + 4 * i, 4)) for i in range(calls)]
            self.assertEqual(got, [(0, 0), (0, 1)])
            self.assertEqual(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40, zf)
            self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_SI,
                                                       r.UC_X86_REG_DI, r.UC_X86_REG_SP, r.UC_X86_REG_BP)],
                             [0x1111, 0x2222, 0x3333, 0x4444, 0x800, 0x600])

    def test_tome_read(self):
        """TOME: the tome (object 21446, power 318) read by the member on show: WIS up by one in the
        sheet (+19h) and the creature (+1Dh), the message in [BP-56h], the way on the used-up path
        (99B44h); at 25 only the message and the shown one (99B67h); anything else the DEC."""
        sheets = 0xB000
        for wis, power, obj in ((18, 318, 21446), (25, 318, 21446), (18, 175, 21446), (18, 318, 31300)):
            mu = self.machine([])
            mu.mem_write(GAME_DS * 16 + self.consts["SHEETS_PTR"], struct.pack("<HH", 0, sheets))
            mu.mem_write((GAME_DS + 0x3E71 - 0x47E0) * 16 + 0x0B44, struct.pack("<H", 1))
            sheet = bytearray(ravager.SHEET_SIZE); sheet[0x19] = wis
            mu.mem_write(sheets * 16 + ravager.SHEET_SIZE, bytes(sheet))
            cre = bytearray(CREATURE_SIZE); cre[0x1D] = wis; cre[0x21:0x27] = b"Meggyn"
            mu.mem_write(CREATURES * 16 + CREATURE_SIZE, bytes(cre))
            mu.mem_write(SS * 16 + 0x600 - 4, struct.pack("<H", power))
            ip = self.call_to(mu, "tome_read", (0, 0x99B44 - 0x999D0, 0x99B67 - 0x999D0), edi=obj, esi=7, eax=0x1111)
            text = bytes(mu.mem_read(SS * 16 + 0x600 - 0x56, 40)).split(b"\0")[0]
            got_power = struct.unpack("<H", mu.mem_read(SS * 16 + 0x600 - 4, 2))[0]
            new_wis = mu.mem_read(sheets * 16 + ravager.SHEET_SIZE + 0x19, 1)[0], mu.mem_read(CREATURES * 16 + CREATURE_SIZE + 0x1D, 1)[0]
            self.assertEqual((mu.reg_read(r.UC_X86_REG_AX), mu.reg_read(r.UC_X86_REG_SI), mu.reg_read(r.UC_X86_REG_DI)),
                             (0x1111, 7, obj))
            if (power, obj) != (318, 21446):
                self.assertEqual((ip, got_power, new_wis), (0, power - 1, (wis, wis)))
            elif wis < 25:
                self.assertEqual((ip, text, new_wis), (0x99B44 - 0x999D0, b"Meggyn reads the tome: WIS 19.", (19, 19)))
            else:
                self.assertEqual((ip, text, new_wis), (0x99B67 - 0x999D0, b"Meggyn can grow no wiser.", (25, 25)))

    def test_patches(self):
        """The sites are where the game has what they replace."""
        patches = {p.name: p for p in ravager.PATCHES}
        self.assertEqual(patches["protection_ac"].replacement, bytes((0xCD, ravager.VEC_SITE, 43, 0x90, 0x90, 0x90)))
        self.assertEqual(patches["protection_save"].replacement, bytes((0xCD, ravager.VEC_SITE, 44, 0x90, 0x90)))
        self.assertEqual(patches["weapon_cast"].replacement, bytes((0xCD, ravager.VEC_SITE, 46, 0x90, 0x90)))
        self.assertEqual(patches["plain_arrow"].replacement, bytes((0xCD, ravager.VEC_SITE, 49, 0x90, 0x90, 0x90)))
        self.assertEqual(patches["join_ready"].replacement, bytes((0xCD, ravager.VEC_SITE, 47, 0x90, 0x90)))
        self.assertEqual(patches["worn_spell_off"].replacement, bytes.fromhex("7e10"))
        self.assertEqual(patches["tome"].replacement, bytes((0xCD, ravager.VEC_SITE, 48)))


if __name__ == "__main__":
    unittest.main()
