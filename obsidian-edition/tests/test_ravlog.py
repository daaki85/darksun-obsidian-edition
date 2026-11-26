"""The dice log for Wake of the Ravager (dsloader.ravlog): the layout profile it swaps in (and back),
the item type records served in Shattered Lands' layout, the read-only view of the game's memory, and
the sequel's item names."""
import os
import struct
import types
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import aging, dicelog, game, kits, ravager, ravlog  # noqa: E402


class FakeGuest:
    def __init__(self, size=0x110000):
        self.mem = bytearray(size)
        self.writes = 0

    def read(self, addr, size):
        return bytes(self.mem[addr:addr + size])

    def write(self, addr, data):
        self.writes += 1
        self.mem[addr:addr + len(data)] = data


class ProfileTests(unittest.TestCase):
    def tearDown(self):
        ravlog.restore_layout()

    def test_mod_bytes(self):
        """The kit byte and the second sphere / new spells byte at the sequel's +3Dh and +3Fh (SL's +43h,
        +45h) while the layout is on, in game, kitpages and kits alike; Shattered Lands' back after."""
        from dsloader import kitpages
        layout = ravlog.layout()
        self.assertEqual((layout["KIT_SHEET"], layout["KIT_BYTE"], layout["NEW_KNOWN_SHEET"], layout["SPHERE2"]),
                         (0x3D, 0x3D, 0x3F, 0x3F))
        self.assertEqual(layout["NEW_KNOWN"][game.FRIENDS_SPELL], (0x3D, 0x80))
        self.assertEqual(layout["NEW_KNOWN"][game.FOG_SPELL], (0x3F, 0x40))
        sl = (game.KIT_SHEET, game.NEW_KNOWN_SHEET, kitpages.KIT_BYTE, kits.SPHERE2, dict(game.NEW_KNOWN))
        ravlog.apply_layout()
        self.assertEqual((game.KIT_SHEET, game.NEW_KNOWN_SHEET, kitpages.KIT_BYTE, kits.SPHERE2), (0x3D, 0x3F, 0x3D, 0x3F))
        ravlog.restore_layout()
        self.assertEqual((game.KIT_SHEET, game.NEW_KNOWN_SHEET, kitpages.KIT_BYTE, kits.SPHERE2, game.NEW_KNOWN), sl)

    def test_kits_read_from_a_sequel_sheet(self):
        """A transferred sheet (SL's through ravtransfer.sheet) reads the same kits, sphere, own feature
        and new spells under the sequel's layout as the SL sheet does under SL's."""
        from dsloader import kitpages, ravtransfer
        sl = bytearray(game.SHEET_SIZE)
        sl[game.SHEET_RACE], sl[game.SHEET_CLASSES], sl[game.SHEET_LEVELS] = 3, 11, 7  # (an elf preserver)
        sl[0x43] = kitpages.KIT_IDS["Battle Mage"] % 4  # (the class's second kit)
        sl[0x45] = 0x40 | 3  # (Fogbolt known; a second sphere's bits, an Elementalist's only)
        sl[0x42], sl[0x44] = 0x2A, 0x2B  # (the sounds)
        want = (kitpages.kit_names(bytes(sl)), kits.second_sphere(kits.ELEMENTALIST, bytes(sl)),
                game.knows_new_spell(bytes(sl), game.FOG_SPELL), kitpages.kit_level(bytes(sl), kitpages.KIT_IDS["Battle Mage"]))
        self.assertEqual(want, (["Battle Mage"], 2, True, 7))
        wotr = ravtransfer.sheet(bytes(sl))
        ravlog.apply_layout()
        try:
            got = (kitpages.kit_names(wotr), kits.second_sphere(kits.ELEMENTALIST, wotr),
                   game.knows_new_spell(wotr, game.FOG_SPELL), kitpages.kit_level(wotr, kitpages.KIT_IDS["Battle Mage"]))
            self.assertEqual(got, want)
            self.assertEqual((wotr[0x3C], wotr[0x3E]), (0x2A, 0x2B))
        finally:
            ravlog.restore_layout()

    def test_layout_maps_record_fields(self):
        layout = ravlog.layout()
        self.assertEqual(layout["CREATURE_NAME"], 0x21)
        self.assertEqual(layout["CREATURE_THAC0"], 0x16)
        self.assertEqual(layout["SHEET_LEVELS"], 0x1E)
        self.assertEqual(layout["ITEM_PLUS"], 0x16)
        self.assertEqual(layout["CREATURE_SIZE"], ravager.CREATURE_SIZE)
        self.assertEqual(layout["AC_ARMOUR_LOCAL"], -4)
        self.assertEqual(layout["SHEET_AGE"], 0x41)  # (its own byte in the sequel: AGE_PLAIN)
        self.assertNotIn("SHEET_FLAG_RANGER", layout)  # (a flag, not an offset)

    def test_apply_and_restore(self):
        sl = (game.CREATURE_NAME, game.DGROUP, dicelog.HDR_SIG, dicelog.CREATURE_THAC0)
        self.assertGreater(ravlog.apply_layout(), 0)
        self.assertEqual((game.CREATURE_NAME, game.DGROUP, dicelog.HDR_SIG, dicelog.CREATURE_THAC0),
                         (0x21, ravager.DGROUP, ravlog.HDR_SIG, 0x16))  # (dicelog's imported copy too)
        self.assertEqual(ravlog.apply_layout(), 0)  # (once)
        ravlog.restore_layout()
        self.assertEqual((game.CREATURE_NAME, game.DGROUP, dicelog.HDR_SIG, dicelog.CREATURE_THAC0), sl)

    def test_weapon_specs_in_the_loaders_bytes(self):
        """The sequel's +14h..+17h are other fields (DEX 16 once read as a staff sling's spec, "+2
        specialized"): the specs and the roll are read at +42h (the Loader's 48h sheet), the age at +41h,
        and none for a sheet of the game's own (0 there); a respec writes the three bytes alone."""
        sheet = bytearray(ravager.SHEET_SIZE); sheet[0x14:0x18] = bytes((5, 18, 16, 15))
        self.assertEqual(game.spec_kinds(bytes(sheet)), bytes((5, 18, 16, 15)))
        ravlog.apply_layout()
        self.assertEqual((game.SPEC_SLOTS, game.SHEET_AGE), (0x42, 0x41))
        self.assertEqual((game.spec_kinds(bytes(sheet)), game.sheet_roll(bytes(sheet))), (bytes(4), None))
        sheet[0x41], sheet[0x42:0x45] = 7, game.packed_specs([4, 2], 0, 11)[:3]
        self.assertEqual((game.spec_kinds(bytes(sheet)), game.sheet_roll(bytes(sheet)), game.sheet_age(bytes(sheet))),
                         (bytes((4, 2, 0, 0)), 11, 7))
        new = game.with_specs(bytes(sheet), [1])
        self.assertEqual((len(new), new[:0x42], new[0x45:]), (ravager.SHEET_SIZE, bytes(sheet[:0x42]), bytes(3)))
        self.assertEqual((game.spec_kinds(new), game.sheet_roll(new), new[0x41]), (bytes((1, 0, 0, 0)), 11, 7))
        self.assertEqual(len(game.respecced(bytes(sheet), [1])), 3)

    def test_size_rule_takes_the_sequels_tables(self):
        from dsloader import sizes
        sl = (sizes.TABLE, sizes.SPELLS, sizes.SHILLELAGH_TYPE, sizes.HAMMER_TYPE)
        ravlog.apply_layout()
        try:
            self.assertEqual((sizes.SHILLELAGH_TYPE, sizes.HAMMER_TYPE), (90, 95))  # (as DSCLOG2's)
            self.assertIs(sizes.SPELLS, sizes.RAV_SPELLS)
            self.assertTrue(sizes.large_by_table("Giant Skeleton", 0))
            self.assertFalse(sizes.large_by_table("Draxan", 1))  # (a people's size is its race's)
        finally:
            ravlog.restore_layout()
        self.assertEqual((sizes.TABLE, sizes.SPELLS, sizes.SHILLELAGH_TYPE, sizes.HAMMER_TYPE), sl)

    def test_psionic_powers_by_the_sequels_numbers(self):
        # (DSCLOG2's records name a power from 0: the sequel's powers start at 0EBh, Cellular Adjustment 248)
        self.assertEqual(ravlog.RavGameData.psionic_first, 0xEB)
        self.assertEqual(game.GameData.psionic_first, game.PSIONIC_FIRST)

    def test_magic_resistance_reads_the_sequels_effects(self):
        # (Low Magic Res. 61 and Mind Barred 64 in the sequel's list, as its routine at 84AB5h tests them)
        ravlog.apply_layout()
        try:
            self.assertEqual((game.LOW_RESISTANCE_EFFECT, game.MIND_BAR_EFFECT), (61, 64))
        finally:
            ravlog.restore_layout()
        self.assertEqual((game.LOW_RESISTANCE_EFFECT, game.MIND_BAR_EFFECT), (31, 32))


class TypeTests(unittest.TestCase):
    def test_sl_type(self):
        """The sequel's type 18 and SL's type 1 (the same weapon): the fields from +8 on line up."""
        wotr = bytes.fromhex("0a2000fa400c1104080100407b1700")
        sl = ravlog.sl_type(wotr)
        self.assertEqual(len(sl), game.ITEM_TYPE_SIZE)
        self.assertEqual(sl[0], 0x0A)
        self.assertEqual(sl[2], 0x20)
        self.assertEqual(sl[6], 0xFA)
        self.assertEqual(sl[0x0B:0x10], bytes.fromhex("0408010040"))  # rate, sides, count, bonus, flags
        self.assertEqual(sl[0x10:0x13], bytes.fromhex("7b1700"))

    def test_view_serves_types_in_sl_layout(self):
        g = FakeGuest()
        ds = 0x4982
        base = 0x72B94
        struct.pack_into("<HH", g.mem, ds * 16 + ravlog.ADDRESSES["ITEM_TYPES_PTR"], base & 0xF, base >> 4)
        for k in range(3):
            g.mem[base + k * 15:base + (k + 1) * 15] = bytes([k + 1]) + bytes(range(2, 16))
        view = ravlog.ReadOnlyGuest(g)
        view.ds = ds
        two = view.read(base + 2 * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
        self.assertEqual(two, ravlog.sl_type(bytes([3]) + bytes(range(2, 16))))
        across = view.read(base + game.ITEM_TYPE_SIZE - 2, 4)  # (a read across two records)
        self.assertEqual(across, ravlog.sl_type(bytes([1]) + bytes(range(2, 16)))[-2:] +
                         ravlog.sl_type(bytes([2]) + bytes(range(2, 16)))[:2])
        self.assertEqual(view.read(0x500, 2), bytes(2))  # (elsewhere: the memory as it is)

    def test_view_drops_writes(self):
        g = FakeGuest()
        view = ravlog.ReadOnlyGuest(g)
        view.write(0x100, b"\x01")
        self.assertEqual((g.writes, view.dropped, g.mem[0x100]), (0, 1, 0))

    def test_view_writes_only_where_writable(self):
        g = FakeGuest()
        view = ravlog.ReadOnlyGuest(g)
        view.writable = [(0x200, 0x10)]
        view.write(0x208, b"\x01\x02")
        view.write(0x20F, b"\x01\x02")  # (past the end: dropped whole)
        self.assertEqual((g.writes, view.dropped, g.mem[0x208:0x20A], g.mem[0x20F]), (1, 1, b"\x01\x02", 0))


class WindowTests(unittest.TestCase):
    def tearDown(self):
        ravlog.restore_layout()

    def test_window_layout(self):
        """The party tabs' layout for the sequel, made from Shattered Lands' (layouts/shattered_lands.json)."""
        import json
        from dsloader import layout
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "layouts", "shattered_lands.json")
        sl = json.load(open(path))
        raw = ravlog.window_layout(sl)
        lay = layout.Layout(raw)
        self.assertEqual((lay.name.offset, lay.records["creature"].stride, lay.records["sheet"].stride),
                         (0x21, ravager.CREATURE_SIZE, ravager.SHEET_SIZE))
        fields = {f.label: f for f in lay.fields}
        self.assertEqual((fields["THAC0"].offset, fields["Gender"].offset, fields["Level 1"].offset,
                          fields["Save: Spell"].offset), (0x16, 0x13, 0x1E, 0x35))
        self.assertEqual((fields["STR"].base.record, fields["STR"].base.offset), ("sheet", 0x15))
        self.assertEqual(lay.records["sheet"].link.match, [(0x15, 0x19, 6), (0x0E, 0x06, 2)])
        self.assertEqual(json.load(open(path)), sl)  # (Shattered Lands' left as it was)

    def test_profile_slots_and_thief_table(self):
        ravlog.apply_layout()
        self.assertEqual(game.SLOTS_LEFT, {"Wizard": 0x4469, "Priest": 0x4474})
        self.assertEqual((game.SLOTS_STRIDE, game.THIEF_TABLE_SEG, game.THIEF_DEX_LOW, game.THIEF_PENALTY_LIST),
                         (0x22, 0x449B, 0xA0, 0xE0))

    def test_item_attacks_named(self):
        """Items saving against acid: the sequel's powers that can destroy an item, named in the dice log
        (Crystal Brittle 103, the monsters' touches 275, 283, 284) in place of SL's 178, 186, 187."""
        ravlog.apply_layout()
        try:
            self.assertEqual(game.ITEM_ATTACKS[103], "Crystal Brittle")
            self.assertEqual(sorted(game.ITEM_ATTACKS), [103, 275, 283, 284])
            self.assertEqual(game.RULES_ALWAYS & ravager.RULES_PORTED & game.RULE_ITEM_SAVES, game.RULE_ITEM_SAVES)
        finally:
            ravlog.restore_layout()
        self.assertEqual(sorted(game.ITEM_ATTACKS), [game.ACID, game.TOUCH_ARMOUR, game.TOUCH_WEAPON])

    def test_multiclass_hp_ported(self):
        """Multiclass hit points: the rule's bit passed to DSCLOG2, and the dice log reading the sequel's
        hit point table (SL's bytes at the load + 45BEh) for CON's bonus."""
        self.assertEqual(ravager.RULES_PORTED & game.RULE_MULTI_HP, game.RULE_MULTI_HP)
        ravlog.apply_layout()
        try:
            self.assertEqual(game.LEVEL_HP_SEG, 0x45BE)
        finally:
            ravlog.restore_layout()
        self.assertEqual(game.LEVEL_HP_SEG, 0x40B1)

    def test_adnd_tables_ported(self):
        """AD&D's class tables: the rule's bit passed to DSCLOG2, and the slots the dice log counts
        AD&D's to 20th level with it (tables.rav_slots), the game's own rule without."""
        self.assertEqual(ravager.RULES_PORTED & game.RULE_ADND_TABLES, game.RULE_ADND_TABLES)
        data = ravlog.RavGameData.__new__(ravlog.RavGameData)
        data.rules = game.RULE_ADND_TABLES
        self.assertEqual([data.adnd_slots(11, 16, s) for s in range(1, 10)], [5, 5, 5, 5, 5, 3, 2, 1, 0])
        self.assertEqual(data.adnd_slots(5, 12, 3), 5)
        self.assertEqual([data.adnd_slots(13, 12, s) for s in (1, 2, 3)], [2, 2, 1])  # (a ranger's AD&D's)
        self.assertEqual(data.adnd_slots(5, 16, 1), 6)  # (a druid's 15th's past it)
        self.assertIsNone(data.adnd_slots(17, 12, 1))  # (a thief has none)
        data.rules = 0
        self.assertIsNone(data.adnd_slots(11, 16, 1))

    def test_con_ported(self):
        """CON as in AD&D: the rule's bit passed to DSCLOG2 (REGEN_SITE, CON_SAVE)."""
        self.assertEqual(ravager.RULES_PORTED & game.RULE_CON, game.RULE_CON)

    def test_class_magic_served(self):
        view = ravlog.ReadOnlyGuest(FakeGuest())
        magic = view.read(ravlog.CLASS_MAGIC_AT, 4 * 20)
        self.assertEqual([magic[c * 4] for c in (1, 8, 9, 10, 11, 12, 13, 17, 18, 19)],
                         [2, 2, 0, 0, 1, 0, 2, 0, 1, 2])  # (18 and 19 the sequel's new classes)


class AgingTests(unittest.TestCase):
    """Ages in the sequel (RULE_AGING: RavDiceLog._aging_pass), on a party in fake memory: the age alone
    at the sheet's +41h, the years the clock passes, Haste's aging, the sequel's dead status."""
    DS, SHEETS, CREATURES = 0x1000, 0x20000, 0x30000

    def tearDown(self):
        ravlog.restore_layout()

    def make(self, rules=game.RULE_AGING):
        g = FakeGuest()
        log = ravlog.RavDiceLog(g)  # (the sequel's layout from here)
        struct.pack_into("<HH", g.mem, self.DS * 16 + game.SHEETS_PTR, 0, self.SHEETS >> 4)
        struct.pack_into("<HH", g.mem, self.DS * 16 + game.CREATURES_PTR, 0, self.CREATURES >> 4)
        for m, (name, race) in enumerate((("Gerakis", 5), ("Ar'Anda", 3))):
            c = self.CREATURES + m * game.CREATURE_SIZE
            struct.pack_into("<hH", g.mem, c, 50, 0)
            struct.pack_into("<H", g.mem, c + game.CREATURE_SHEET_INDEX, m)
            g.mem[c + game.CREATURE_STATUS] = 1
            g.mem[c + game.CREATURE_ABILITIES:c + game.CREATURE_ABILITIES + 6] = bytes((18, 15, 25, 13, 15, 14))
            g.mem[c + game.CREATURE_NAME:c + game.CREATURE_NAME + len(name)] = name.encode()
            s = self.SHEETS + m * game.SHEET_SIZE
            g.mem[s + game.SHEET_RACE] = race
            g.mem[s + game.SHEET_ABILITIES:s + game.SHEET_ABILITIES + 6] = bytes((18, 15, 25, 13, 15, 14))
        class Game(ravlog.RavGameData):
            clock, hastes = 100, []

            def game_time(self):
                return self.clock

            def effect_records(self):
                return [(game.Effect(o, 1, game.HASTED_EFFECT), 41, h) for o, h in self.hastes]

            def combatant_creature(self, combatant):
                return combatant

            def combatant_name(self, combatant):
                return self.creature_name(combatant)

        log.game = Game(log.guest, self.DS, rules)
        return g, log

    def test_ages_given_alone_in_their_byte(self):
        g, log = self.make()
        self.assertEqual(log._aging_pass(), [])  # (the first look only records)
        lines = log._aging_pass()
        self.assertTrue(lines[0].startswith("Gerakis is "), lines)
        self.assertTrue(lines[1].startswith("Ar'Anda is "), lines)
        age = g.mem[self.SHEETS + game.SHEET_AGE]
        self.assertTrue(6 <= age <= 21, age)  # (a half-giant: 20 + 5d4, the byte the age less 19)
        self.assertEqual(game.SHEET_AGE, 0x41)
        self.assertEqual(log.guest.dropped, 0)
        self.assertEqual(log._aging_pass(), [])  # (given once)

    def test_a_year_of_the_clock(self):
        g, log = self.make()
        log._aging_pass(), log._aging_pass()
        before = g.mem[self.SHEETS + game.SHEET_AGE]
        log.game.clock = aging.YEAR + 50  # (a long jump, as a load: waits for a steady look)
        self.assertEqual(log._aging_pass(), [])
        self.assertEqual(log._aging_pass(), [])
        log.game.clock = 2 * aging.YEAR - 10
        log._aging_pass()
        log.game.clock = 2 * aging.YEAR + 10
        lines = log._aging_pass()
        self.assertTrue(lines[0].startswith("A year has passed: Gerakis is "), lines)
        self.assertEqual(g.mem[self.SHEETS + game.SHEET_AGE], before + 1)
        self.assertEqual(log.guest.dropped, 0)

    def test_hastes_age_a_year(self):
        g, log = self.make()
        log.game.hastes = [(1, 7)]  # (Ar'Anda's, there at the first look: not news)
        log._aging_pass(), log._aging_pass()
        before = g.mem[self.SHEETS + game.SHEET_AGE]
        log.game.hastes = [(1, 7), (0, 8)]
        lines = log._aging_pass()
        self.assertEqual(lines[0], "Ar'Anda gives Hasted to Gerakis")
        self.assertIn("system shock (Haste's aging)", lines[1])
        self.assertIn("survives", lines[1])  # (CON 25: 100%)
        self.assertEqual(g.mem[self.SHEETS + game.SHEET_AGE], before + 1)
        self.assertEqual(log._aging_pass(), [])  # (the same effect: once)

    def test_dead_is_the_sequels_status(self):
        from dsloader import kalzith
        g, log = self.make()
        aging.kill(log.game, 1)
        self.assertEqual(kalzith.DEAD_STATUS, (4, 7))
        self.assertEqual(g.mem[self.CREATURES + game.CREATURE_SIZE + game.CREATURE_STATUS], 1)  # (read-only: not writable yet)
        log._aging_writable([1])
        aging.kill(log.game, 1)
        self.assertEqual(g.mem[self.CREATURES + game.CREATURE_SIZE + game.CREATURE_STATUS], 7)

    def test_rule_off_nothing(self):
        g, log = self.make(rules=0)
        log.hp_changes = lambda now: []
        log._after_rolls(False, 1.0), log._after_rolls(False, 2.0)
        self.assertEqual(g.mem[self.SHEETS + game.SHEET_AGE], 0)

    def test_aging_ported(self):
        self.assertEqual(ravager.RULES_PORTED & game.RULE_AGING, game.RULE_AGING)


class PassTests(unittest.TestCase):
    def tearDown(self):
        ravlog.restore_layout()

    def test_after_rolls_runs_the_hp_watch_only(self):
        """The hit points' changes follow the rolls (each hit matched with its fall: else the round's
        end calls every hit "takes none"); nothing else of Shattered Lands' pass (the text, with no helper
        attached, not read either)."""
        log = ravlog.RavDiceLog(FakeGuest())
        log.hp_changes = lambda now: ["  Gerakis now 64/165 HP (-12)"]
        log._changes = log._answer_use = lambda *a: self.fail("not ported")
        self.assertEqual(log._after_rolls(False, 1.0), ["  Gerakis now 64/165 HP (-12)"])


    def test_slots_written_to_the_helper(self):
        """The USE screen's lines go into DSCLOG2's SLOTS_TEXT (its header's +148), a member's in each
        SLOTS_SIZE bytes, and nowhere else."""
        g = FakeGuest()
        seg_base, hdr, slots = 0xC91B0, 0x20, 0x900
        struct.pack_into("<H", g.mem, seg_base + hdr + dicelog.TSR_HDR_OFF, hdr)
        struct.pack_into("<H", g.mem, seg_base + hdr + dicelog.TSR_SLOTS_OFF, slots)
        log = ravlog.RavDiceLog(g)
        log.tsr_hdr = seg_base + hdr
        log.slots_lines = lambda member: "\x80SPELLS LEFT|\x81WIZ 2/4" if member == 1 else ""
        log._write_slots()
        at = seg_base + slots + dicelog.SLOTS_SIZE
        self.assertEqual(bytes(g.mem[at:at + 24]), b"\x80SPELLS LEFT|\x81WIZ 2/4".ljust(24, b"\0"))
        self.assertEqual(log.guest.dropped, 0)
        writes = g.writes
        log._write_slots()  # (unchanged: not written again)
        self.assertEqual(g.writes, writes)

    def test_labels_written_to_the_helper(self):
        """Names over figures go into DSCLOG2's LBL_SLOTS (its header's +1834:+1838), in the colours of
        the palette it read (DAC, +238 in its far block), and come off when their time is up."""
        from dsloader import combatlog, labels
        g = FakeGuest()
        seg, hdr, off, far = 0xC91B, 0x20, 0x2000, 0xD000
        base = seg * 16 + hdr
        struct.pack_into("<H", g.mem, base + dicelog.TSR_HDR_OFF, hdr)
        struct.pack_into("<HHH", g.mem, base + labels.TSR_TAIL_SEG, seg, 0, off)
        struct.pack_into("<H", g.mem, base + combatlog.TSR_FAR_SEG, far)
        struct.pack_into("<H", g.mem, base + combatlog.TSR_DAC, 0x10)
        g.mem[far * 16 + 0x10:far * 16 + 0x10 + 768] = bytes(range(64)) * 12

        class Font:
            height = 7
            def glyph(self, c):
                return 4, bytes([combatlog.FONT_INK] * 28)

        log = ravlog.RavDiceLog(g)
        log.tsr_hdr = base
        log.game = types.SimpleNamespace(guest=log.guest, rules=0)  # (as attach makes it: on the read-only view)
        log._labels_font_tried, log._labels.font = True, Font()
        log._float(7, labels.MISS, labels.MISS_INK, 100.0)
        at = seg * 16 + off
        self.assertEqual(g.mem[at], 1)                       # (the label's number)
        self.assertEqual(g.mem[at + 1], labels.width(Font(), labels.MISS))
        self.assertEqual(struct.unpack_from("<H", g.mem, at + 6)[0], 7)  # (over thing 7)
        self.assertEqual(log.guest.dropped, 0)
        log.hp_changes = lambda now: []
        log._after_rolls(False, 100.0 + labels.SHOW_FOR + 1)
        self.assertEqual(g.mem[at], 0)

    def test_in_combat_is_a_byte(self):
        """A fight on: the byte at DS:13FAh (the next byte whatever it is) and the fight's state at
        (DS - 47E0h + 3C10h):19h."""
        ravlog.apply_layout()
        g = FakeGuest()
        ds = 0x4982
        data = ravlog.RavGameData(g, ds)
        g.mem[ds * 16 + 0x13FA:ds * 16 + 0x13FC] = b"\x00\x05"
        state = (ds - 0x47E0 + 0x3C10) * 16 + 0x19
        g.mem[state] = 2
        self.assertFalse(data.in_combat())
        g.mem[ds * 16 + 0x13FA] = 1
        self.assertTrue(data.in_combat())
        g.mem[state] = 0
        self.assertFalse(data.in_combat())
        ravlog.restore_layout()

    def test_panel_colours_from_the_interface(self):
        """The sequel's panel picks its colours from 16-253 (its interface's blue-greys are 232-239);
        Shattered Lands' range comes back with its layout."""
        from dsloader import combatlog
        ravlog.apply_layout()
        try:
            self.assertEqual(combatlog.LAST, ravlog.PALETTE_LAST)
            dac = bytearray(768)
            for i in range(256):
                dac[i * 3:i * 3 + 3] = bytes((40, 10, 40))  # (purple everywhere ...)
            dac[236 * 3:236 * 3 + 3] = bytes((22, 22, 27))  # (... but the interface's 88,88,108)
            self.assertEqual(combatlog.nearest(bytes(dac), (88, 88, 108)), 236)
        finally:
            ravlog.restore_layout()
        self.assertEqual(combatlog.LAST, 223)

    def test_only_ported_rules(self):
        """The sequel's game data takes only the mod's rules ported to it (the Loader's settings name
        SL's): the better hit die, and none of the spell slots' rules."""
        data = ravlog.RavGameData(FakeGuest(), 0x4982, rules=0xFFFFFFFF)
        self.assertEqual(data.rules, ravager.RULES_PORTED)
        self.assertTrue(data.rules & game.RULE_HP_BEST)
        self.assertFalse(data.no_spells(0))

    def test_restrictions_ported(self):
        """Class restrictions: a thief in heavy armour loses its skills (DSCLOG2's BELT_SITE) with the rule
        on, and a multiclass preserver in armour can't cast (CAST_ARMOUR)."""
        real = game.GameData.no_spells, game.GameData.thief_heavy
        game.GameData.no_spells = game.GameData.thief_heavy = lambda self, c: True
        try:
            data = ravlog.RavGameData(FakeGuest(), 0x4982, rules=0xFFFFFFFF)
            self.assertTrue(data.no_spells(0))
            self.assertTrue(data.thief_heavy(0))
            data = ravlog.RavGameData(FakeGuest(), 0x4982, rules=0)
            self.assertFalse(data.no_spells(0))
            self.assertFalse(data.thief_heavy(0))
        finally:
            game.GameData.no_spells, game.GameData.thief_heavy = real

    def test_spell_level(self):
        """A spell's level from the sequel's table of each level's first spell (DS:0656h)."""
        g = FakeGuest()
        ds = 0x4982
        g.mem[ds * 16 + ravlog.SPELL_STARTS:ds * 16 + ravlog.SPELL_STARTS + 22] = bytes(
            [0, 12, 25, 39, 56, 68, 81, 92, 102, 111, 115, 115, 127, 143, 165, 189, 208, 216, 231, 232, 233, 235])
        data = ravlog.RavGameData(g, ds)
        self.assertEqual([data.spell_level(s) for s in (0, 11, 12, 27, 105, 111, 115, 126, 127, 0xEB)],
                         [1, 1, 2, 3, 9, 10, 1, 1, 2, 0])

    def test_effect_caster_level(self):
        """The sequel's caster level routine (97DC5h): a wizard spell the preserver's level, a priest
        spell the best priest class's (a ranger's 7 less), a psionic power the psionicist's, a
        monster's power none."""
        data = ravlog.RavGameData(FakeGuest(), 0x4982)
        levels = {11: 6, 12: 5, 15: 12, 2: 3}
        data.class_level = lambda creature, cls: levels.get(cls, 0)
        self.assertEqual(data.effect_caster_level(0, 5), 6)       # Enlarge
        self.assertEqual(data.effect_caster_level(0, 126), 5)     # Shillelagh: the ranger's 12 less 7
        self.assertEqual(data.effect_caster_level(0, 0xEB), 5)    # a psionic power
        self.assertIsNone(data.effect_caster_level(0, 0x10D))

    def test_helm_counts_with_the_rule(self):
        """A worn Helm of type 55 counts AC 1 with RULE_HELMS (its type reads 0); a hat of the same
        type, and anything without the rule, doesn't."""
        def item(kind, name):
            rec = bytearray(ravager.ITEM_SIZE)
            struct.pack_into("<H", rec, 0x0A, kind)
            struct.pack_into("<H", rec, ravager.ITEM_NAME, name)
            return bytes(rec)
        typ = bytearray(game.ITEM_TYPE_SIZE)
        typ[0x0F] = 0x80
        worn = [(1, item(ravager.HELM_TYPE, ravager.HELM_NAME), bytes(typ)), (2, item(ravager.HELM_TYPE, 0x27), bytes(typ))]
        real = game.GameData.counted_ac
        game.GameData.counted_ac = lambda self, c: 7
        try:
            for rules, ac in ((game.RULE_HELMS, 6), (0, 7)):
                data = ravlog.RavGameData(FakeGuest(), 0x4982, rules=rules)
                data._worn = lambda c, lists=None: worn
                self.assertEqual(data.counted_ac(0), ac)
        finally:
            game.GameData.counted_ac = real

    def test_slots_test_switch_is_a_byte(self):
        """The slot routine's test switch is a byte at DS:13F8h (the next byte whatever it is)."""
        g = FakeGuest()
        ds = 0x4982
        data = ravlog.RavGameData(g, ds)
        g.mem[ds * 16 + ravlog.SLOTS_ALL_19:ds * 16 + ravlog.SLOTS_ALL_19 + 2] = b"\x01\x47"
        self.assertEqual(data.max_spell_slots(0, 1, 1), 19)
        self.assertEqual(data.robe_slots(0, 1, 1, 3), 3)

    def test_veiled_robe_slots(self):
        """The Veiled Robe (the mod's robe type in the sequel, plus 2, on the chest) gives a wizard a slot more
        at spell levels 1-3 where there are any (DSCLOG2's VEILED_SLOT); the Ashen Robe, a robe in the pack,
        a priest and level 4 don't."""
        data = ravlog.RavGameData(FakeGuest(), 0x4982)

        def robe(plus, slot=0x09):
            rec = bytearray(ravager.ITEM_SIZE)
            struct.pack_into("<H", rec, 0x0A, ravager.mod_type(game.ROBE_TYPE))
            rec[0x13], rec[0x16] = slot, plus
            return [(1, bytes(rec), bytes(game.ITEM_TYPE_SIZE))]
        for worn, bit, level, total, want in ((robe(2), kits.WIZARD, 1, 3, 4), (robe(2), kits.WIZARD, 3, 2, 3),
                                              (robe(2), kits.WIZARD, 4, 2, 2), (robe(2), kits.WIZARD, 2, 0, 0),
                                              (robe(1), kits.WIZARD, 1, 3, 3), (robe(2, 20), kits.WIZARD, 1, 3, 3),
                                              (robe(2), kits.PRIEST, 1, 3, 3), ([], kits.WIZARD, 1, 3, 3)):
            data._worn = lambda c, lists=None, worn=worn: worn
            with self.subTest(worn=worn, bit=bit, level=level):
                self.assertEqual(data.robe_slots(0, bit, level, total), want)


class LookTests(unittest.TestCase):
    """The sequel's damage resistance (85052h's classes) and the Look box's lines from it."""

    def test_resist_percent(self):
        # class 9 (1038h): weapons only from +1; class 6 (half 86h): fire, cold, electricity halved
        self.assertEqual(ravlog.resist_percent(0x1038, 0, 0x10), 0)
        self.assertEqual(ravlog.resist_percent(0x1038, 0, 0x10 | 0x1000), 100)
        self.assertEqual(ravlog.resist_percent(0x3038, 0, 0x10 | 0x1000), 0)
        self.assertEqual(ravlog.resist_percent(0, 0x86, 0x202), 50)
        self.assertEqual(ravlog.resist_percent(0x7FF, 0x14, 0x202), 0)
        self.assertEqual(ravlog.resist_percent(0x7FF, 0x14, 0x10), 50)  # (weapons: no magic needed)

    def _lines(self, resist, immune, half):
        ravlog.apply_layout()
        try:
            from dsloader import ravager
            rec = bytearray(ravager.CREATURE_SIZE)
            rec[0:2] = (25).to_bytes(2, "little")
            rec[ravager.creature_field(0x1F)] = 15
            rec[ravlog.CREATURE_RESIST] = resist
            rec[0x21:0x2F] = b"Giant Skeleton"
            sheet = bytearray(ravager.SHEET_SIZE)
            sheet[0x08:0x0A] = (25).to_bytes(2, "little")
            gd = types.SimpleNamespace(creature=lambda i: bytes(rec), sheet=lambda i: bytes(sheet),
                                       counted_ac=lambda i: 6, creature_name=lambda i: "Giant Skeleton")
            real = ravlog.resist_masks
            ravlog.resist_masks = lambda g, r: (immune, half)
            try:
                return ravlog.monster_lines(gd, 20, None)
            finally:
                ravlog.resist_masks = real
        finally:
            ravlog.restore_layout()

    def test_spells_immune(self):
        short, full = self._lines(2, 0x7FF, 0x14)
        self.assertEqual(short, ["HP 25/25 AC 6", "THAC0 15", "IMM SPELLS PSI"])
        self.assertIn("Immune to spells and psionic attacks.", full)

    def test_needs_a_magic_weapon(self):
        short, full = self._lines(9, 0x1038, 0)
        self.assertEqual(short[-1], "NEEDS +1 WEAPON")
        self.assertIn("Only +1 or better weapons hurt it.", full)


class EffectTests(unittest.TestCase):
    def tearDown(self):
        ravlog.restore_layout()

    def test_names_from_the_program(self):
        g = FakeGuest()
        load = 0x1A2
        names = ["None", "Acid", "Adrenalin Control", "Animal Affinity", "Anti Magic Shell", "Armor"] + [""] * 107
        for n, name in enumerate(names):
            at = load * 16 + ravlog.EFFECT_RECORDS + n * ravlog.EFFECT_RECORD
            g.mem[at:at + len(name)] = name.encode()
        got = ravlog.effect_names(g, load)
        self.assertEqual((got[5], got[1], 12 in got), ("Armor", "Acid", False))
        g.mem[load * 16 + ravlog.EFFECT_RECORDS + 7 * ravlog.EFFECT_RECORD] = 0xFF  # (not names: none)
        self.assertEqual(ravlog.effect_names(g, load), {})

    def test_profile_effect_numbers(self):
        ravlog.apply_layout()
        self.assertEqual((game.PARALYZED_EFFECT, game.MIRROR_EFFECT, game.EFFECT_BLESSED, dicelog.AFRAID_EFFECT),
                         (69, 46, 9, 35))
        self.assertGreaterEqual(game.STINK_EFFECT, ravlog.NO_EFFECT)
        self.assertEqual((game.EFFECTS_SEG, game.EFFECTS_OFF), (0x3E71, 0x24D))


class NameTests(unittest.TestCase):
    def test_names_by_line_from_one(self):
        g = FakeGuest()
        names = ["Tombstone", "Olive Branch", "One-use Scroll"] + [f"n{i}" for i in range(20)] + ["Lotulis", "Polearm", "Longsword"]
        at = 0x73000
        data = "\r\x00".join(names).encode("latin1") + b"\r\x00\x00\x00"
        g.mem[at:at + len(data)] = data
        gd = ravlog.RavGameData.__new__(ravlog.RavGameData)
        gd.guest = g
        self.assertEqual(gd.item_name(1), "Tombstone")
        self.assertEqual(gd.item_name(26), "Longsword")  # (Ar'anda's, in a running game)
        self.assertEqual(gd.item_name(24), "Lotulis")  # (the Draxans', as the Look box has it)
        self.assertEqual(gd.item_name(999), "item 999")


if __name__ == "__main__":
    unittest.main()


class StealthPortTests(unittest.TestCase):
    """SL's stealth (stealth.py) in the sequel: its positions, regions, footprint, dying and dead, the
    Elvenkind types; the Loader's word in DSCLOG2's header (STEALTH, +204) the only write."""
    DS = 0x4982

    def tearDown(self):
        ravlog.restore_layout()

    def test_rule_ported(self):
        self.assertEqual(ravager.RULES_PORTED & game.RULE_STEALTH, game.RULE_STEALTH)

    def test_layout(self):
        from dsloader import stealth
        sl = (stealth.POSITIONS, stealth.POSITION_SIZE, stealth.OUTDOORS, stealth.STATUS_GONE, game.ELVEN_CLOAK_TYPE)
        ravlog.apply_layout()
        self.assertEqual((stealth.POSITIONS, stealth.POSITION_SIZE), (0x67C5, 0x25))
        self.assertEqual(stealth.STATUS_GONE, (4, 7))
        self.assertEqual(stealth.SHEET_FOOTPRINT, ravager.sheet_field(0x3D))
        self.assertEqual((game.ELVEN_CLOAK_TYPE, game.ELVEN_BOOTS_TYPE),
                         (ravager.mod_type(134), ravager.mod_type(135)))
        self.assertEqual((game.BACK_GIRDLE_TYPE, game.URNST_GIRDLE_TYPE, game.MR_AMULET_TYPE), (129, 130, 131))
        ravlog.restore_layout()
        self.assertEqual((stealth.POSITIONS, stealth.POSITION_SIZE, stealth.OUTDOORS, stealth.STATUS_GONE,
                          game.ELVEN_CLOAK_TYPE), sl)

    def test_thief_effects_by_the_sequels_numbers(self):
        """The effects that rule a thief skill out are SL's by name in the sequel's numbers: its 25 is Detect
        Invisible (a thief in Tyr hid at 0 with it), Mirror Images (46) rules hiding out."""
        ravlog.apply_layout()
        self.assertNotIn(25, game.THIEF_BLOCKED)
        self.assertEqual(game.THIEF_BLOCKED[46], (4,))
        self.assertEqual(game.THIEF_CERTAIN, {26: (2,), 53: (4,)})

    def test_daylight_by_region(self):
        """Under the open sky in Tyr, the forest, the Jann's desert, the Silt Sea islands and the clouds;
        not in the Veiled Alliance's headquarters, the mines, the volcano, Under Tyr."""
        from dsloader import stealth
        g = FakeGuest()
        ravlog.apply_layout()
        data = ravlog.RavGameData(g, self.DS)
        for region, sun in ((0x32, True), (0x01, True), (0x3B, True), (0x41, True), (0x42, True),
                            (0x33, False), (0x38, False), (0x3D, False), (0x45, False), (0x36, False)):
            struct.pack_into("<H", g.mem, self.DS * 16 + 0x140C, region)
            with self.subTest(region=hex(region)):
                self.assertEqual(stealth.daylight(data, 0), sun)

    def test_square_from_the_sequels_positions(self):
        from dsloader import stealth
        g = FakeGuest()
        ravlog.apply_layout()
        struct.pack_into("<HH", g.mem, self.DS * 16 + 0x67C5 + 2 * 0x25, 0x123, 0x456)
        self.assertEqual(stealth.square(ravlog.RavGameData(g, self.DS), 2), (0x12, 0x45))

    def test_hidden_word_written(self):
        """_set_stealth writes DSCLOG2's STEALTH alone (no sound, no see-through figure: not in DSCLOG2)."""
        from dsloader import stealth
        g = FakeGuest()
        log = ravlog.RavDiceLog(g)
        log.tsr_hdr = 0xC91D0
        log._set_stealth(True, 2)
        self.assertEqual(struct.unpack_from("<H", g.mem, log.tsr_hdr + stealth.TSR_STEALTH)[0], 4)
        self.assertEqual(g.writes, 1)
        log._set_stealth(False)
        self.assertEqual(struct.unpack_from("<H", g.mem, log.tsr_hdr + stealth.TSR_STEALTH)[0], 0)

    def test_turn_lines_with_the_rule(self):
        log = ravlog.RavDiceLog(FakeGuest())
        log.hp_changes = lambda now: []
        log.turn_lines = lambda: ["Lex's turn"]
        log.game = ravlog.RavGameData(log.guest, self.DS, rules=game.RULE_STEALTH)
        self.assertIn("Lex's turn", log._after_rolls(False, 1.0))
        log.game = ravlog.RavGameData(log.guest, self.DS, rules=0)
        self.assertNotIn("Lex's turn", log._after_rolls(False, 2.0))


class ChargeLabelTests(unittest.TestCase):
    """Names over figures' charges ("Armor: 3 left", labels.py) in the sequel: SL's charges pass (DiceLog.
    count_charges) on the sequel's effect records (load + 3E71h:24Dh) and event queues (DS:2A63h, 2A6Bh),
    so the charge routine's 2d4 is known behind the overlay manager's INT 3Fh stub too."""
    DS = 0x4982

    def tearDown(self):
        ravlog.restore_layout()

    def test_queue_places(self):
        ravlog.apply_layout()
        self.assertEqual((game.EVENT_QUEUE, game.EVENT_COUNT, game.EVENT_SIZE), (0x2A63, 0x2A6B, 0x11))

    def test_armor_charge_floats_over_its_owner(self):
        from unittest import mock
        from dsloader import labels
        from test_dicelog import entry, raw_for, words
        g = FakeGuest()
        seg, hdr, off = 0xC91B, 0x20, 0x2000
        base = seg * 16 + hdr
        struct.pack_into("<H", g.mem, base + dicelog.TSR_HDR_OFF, hdr)
        struct.pack_into("<HHH", g.mem, base + labels.TSR_TAIL_SEG, seg, 0, off)
        log = ravlog.RavDiceLog(g)
        log.tsr_hdr = base
        load = self.DS - ravager.DGROUP
        ravlog.rebind("SPELLS_SEG", (ravlog.SPELLS_AT + 0x10 - game.SPELLS_OFF) // 16 - load)  # (as attach)
        ravlog.rebind("EFFECT_NAMES", {5: "Armor"})  # (... the sequel's names, from its program)
        armor, owner, eid = 5, 2, 5  # (the sequel's Armor effect, 5; its spell's record lasting by charges)
        table = bytearray(ravlog.SPELL_COUNT * 32)
        struct.pack_into("<h", table, armor * 32 + 7, -1)
        log.guest.spells = bytes(table)
        log.game = ravlog.RavGameData(log.guest, self.DS, rules=0)
        struct.pack_into("<h", g.mem, self.DS * 16 + 0x2100, 1)  # (EFFECT_COUNT: one effect)
        struct.pack_into("<hhhBBB", g.mem, (load + 0x3E71) * 16 + 0x24D, owner, owner, armor, eid, 0, 3)
        trap = dicelog.OVERLAY_TRAP + bytes(8)  # (the charge routine's return made a stub: in the sequel's overlays)
        e = [entry(raw_for(f, 4), dicelog.DICE_SITE, words(0, 0, 2, 4), words(0, 0, owner, eid), parent_code=trap)
             for f in (3, 1, 2, 4)]
        shown = []
        log._labels_font_tried = True
        with mock.patch.object(ravlog.RavGameData, "spell_names", [""] * armor + ["Armor"]), \
                mock.patch.object(log._labels, "show", lambda guest, hdr, thing, text, *a: shown.append((thing, text))):
            log.count_charges(e)
            lines = [line for x in e for line in log.describe(x)]
        self.assertEqual(lines, ["    Armor on {}: one charge used, 4 left".format(log._name(owner)),
                                 "    Armor on {}: one charge used, 3 left".format(log._name(owner))])
        self.assertEqual(shown, [(owner, "Armor: 4 left"), (owner, "Armor: 3 left")])
        self.assertEqual(log.guest.dropped, 0)

    def test_effect_ends_from_the_queue(self):
        """An effect's end in the sequel's event queue, found by its owner and handle."""
        g = FakeGuest()
        ravlog.apply_layout()
        load = self.DS - ravager.DGROUP
        data = ravlog.RavGameData(ravlog.ReadOnlyGuest(g), self.DS)
        struct.pack_into("<h", g.mem, self.DS * 16 + 0x2100, 1)
        struct.pack_into("<hhhBBB", g.mem, (load + 0x3E71) * 16 + 0x24D, 1, 1, 300, 9, 7, 15)
        queue = 0x6F100
        struct.pack_into("<HH", g.mem, self.DS * 16 + 0x2A63, queue & 0xF, queue >> 4)
        struct.pack_into("<h", g.mem, self.DS * 16 + 0x2A6B, 1)
        struct.pack_into("<iBhB", g.mem, queue, 5000, 7, 1, 7)
        self.assertEqual(data.effect_deadlines(), {(1, 7): 5000})


class BlastSaveCreationTests(unittest.TestCase):
    """Psionic Blast's wounds given back (DSCLOG2's BLAST_HP, +1814), the sequel's saving throw's d20 (its
    frame's [BP-0Ah] pointer) and the creation screen's tries (RL_TRY, +280/+282)."""
    DS, CREATURES, SHEETS, HDR = 0x1000, 0x30000, 0x20000, 0xC91B0

    def tearDown(self):
        ravlog.restore_layout()

    def make(self):
        g = FakeGuest()
        log = ravlog.RavDiceLog(g)  # (the sequel's layout from here)
        log.tsr_hdr = self.HDR
        struct.pack_into("<HH", g.mem, self.DS * 16 + game.SHEETS_PTR, 0, self.SHEETS >> 4)
        struct.pack_into("<HH", g.mem, self.DS * 16 + game.CREATURES_PTR, 0, self.CREATURES >> 4)
        fighting = [True]

        class Game(ravlog.RavGameData):
            def combatant_creature(self, combatant):
                return combatant

            def in_combat(self):
                return fighting[0]

            def game_time(self):
                return 100

        log.game = Game(log.guest, self.DS, 0)
        c = self.CREATURES + game.CREATURE_SIZE  # (member 1: 8 of 40 HP, Okay)
        struct.pack_into("<h", g.mem, c, 8)
        g.mem[c + game.CREATURE_STATUS] = game.STATUS_OKAY
        struct.pack_into("<H", g.mem, c + game.CREATURE_SHEET_INDEX, 1)
        g.mem[c + game.CREATURE_NAME:c + game.CREATURE_NAME + 4] = b"Lex\0"
        struct.pack_into("<h", g.mem, self.SHEETS + game.SHEET_SIZE + game.SHEET_MAX_HP, 40)
        return g, log, fighting

    def test_blast_given_back_at_the_fight_end(self):
        from dsloader import psiblast
        g, log, fighting = self.make()
        self.assertEqual(psiblast.TSR_BLAST, 1814)
        struct.pack_into("<4h", g.mem, self.HDR + psiblast.TSR_BLAST, 0, 24, 0, 0)
        self.assertEqual(log._blast_pass(0.0), [])
        fighting[0] = False
        self.assertEqual(log._blast_pass(1.0), [])
        out = log._blast_pass(1.0 + psiblast.FIGHT_OVER)
        self.assertEqual(len(out), 1, out)
        self.assertIn("+24 HP, now 32/40", out[0])
        self.assertEqual(struct.unpack_from("<h", g.mem, self.CREATURES + game.CREATURE_SIZE)[0], 32)
        self.assertEqual(struct.unpack_from("<4h", g.mem, self.HDR + psiblast.TSR_BLAST), (0, 0, 0, 0))
        self.assertEqual(log.guest.dropped, 0)

    def test_save_roll_by_the_sequels_frame(self):
        """The d20 is the saving throw's when its frame's [BP-0Ah]:[BP-8] points at the target's record."""
        g, log, _ = self.make()
        at = self.CREATURES + game.CREATURE_SIZE
        frame = {-0x0A: at & 0xF, -0x08: at >> 4, -0x1E: 0, -0x1C: 0}
        e = types.SimpleNamespace(parent_arg=lambda off: 1 if off == 6 else None,
                                  parent_local=lambda off: frame.get(off))
        self.assertTrue(log._is_save_roll(e))
        frame[-0x08] += 1
        self.assertFalse(log._is_save_roll(e))

    def test_creation_tries(self):
        """Each ability's best of its four 4d4, +4 and the race's adjustment, from DSCLOG2's RL_TRIES once
        RL_SEQ has moved; the scores read from the creature being made (DS:142Dh)."""
        g, log, _ = self.make()
        sheet, creature, load = 0x40000, 0x40100, 0x100
        log.game.load_seg = load
        struct.pack_into("<HH", g.mem, self.DS * 16 + 0x1429, 0, sheet >> 4)
        struct.pack_into("<HH", g.mem, self.DS * 16 + 0x142D, 0, creature >> 4)
        g.mem[sheet + game.SHEET_RACE] = 1
        g.mem[sheet + game.SHEET_CLASSES:sheet + game.SHEET_CLASSES + 3] = bytes((0, 0, 0))
        adjust = (load + 0x3E4F) * 16 + 0x120 + 6  # (race 1's: +1 DEX)
        g.mem[adjust + 1] = 1
        g.mem[creature + game.CREATURE_ABILITIES:creature + game.CREATURE_ABILITIES + 6] = \
            bytes((16, 17, 14, 12, 10, 9))
        log._creation_tries_moved(0.0)  # (the first look: the count noted)
        g.mem[self.HDR + 282:self.HDR + 306] = bytes((12, 9, 8, 7, 12, 11, 10, 9, 10, 8, 6, 5,
                                                       8, 6, 5, 4, 6, 6, 5, 4, 5, 5, 4, 4))
        struct.pack_into("<H", g.mem, self.HDR + 280, 24)
        self.assertEqual(log._creation_pass(1.0), [])  # (the die still moving)
        out = log._creation_pass(1.0 + dicelog.CREATION_HP_WAIT)
        self.assertEqual(out[0], "Character creation, STR 16: best of four 4d4 (12, 9, 8, 7) = 12, +4 = 16")
        self.assertIn("DEX 17: best of four 4d4 (12, 11, 10, 9) = 12, +4, +1 ", out[1])
        self.assertEqual(out[-1], "Character creation: the six scores add up to 78")
        g.mem[creature + game.CREATURE_ABILITIES] = 17  # (the sequel's least for a prime requisite: raised)
        struct.pack_into("<H", g.mem, self.HDR + 280, 48)
        log._creation_pass(2.0)
        out = log._creation_pass(3.0)
        self.assertEqual(out[0], "Character creation, STR 17: best of four 4d4 (12, 9, 8, 7) = 12, +4 = 16, "
                                 "raised to 17 (the classes' least)")


class StartGearTests(unittest.TestCase):
    """The sequel's items for fuller starting gear (ravlog.RAV_PLAIN, RAV_LEATHER, RAV_CLOAK): each record its
    type at +0Ah, a weapon of the kind it is listed under (ravager.rav_kinds), in no list and no slot; with
    the sequel there, each the record of one of OBJEX.GFF's objects (its own picture, value and name)."""

    def test_records(self):
        from dsloader import ravager, ravlog
        kinds = ravager.rav_kinds()
        for kind, choices in ravlog.RAV_PLAIN.items():
            for type_, rec in choices:
                self.assertEqual(len(rec), ravager.ITEM_SIZE)
                self.assertEqual(struct.unpack_from("<H", rec, 0x0A)[0], type_)
                self.assertEqual(kinds.get(type_), kind, type_)
                self.assertEqual((struct.unpack_from("<H", rec, 4)[0], rec[0x13], rec[0x16]), (9999, 0xFF, 0))
        self.assertEqual([struct.unpack_from("<H", r, 0x0A)[0] for _, r in ravlog.RAV_LEATHER], [32, 3, 64])

    @unittest.skipUnless(os.environ.get("DSUN_WOTR"), "DSUN_WOTR: the player's Wake of the Ravager folder")
    def test_from_the_game(self):
        import glob
        from dsloader import dataitems, gff, ravlog
        path = next(f for f in glob.glob(os.path.join(os.environ["DSUN_WOTR"], "*")) if f.lower().endswith("objex.gff"))
        objects = gff.read_gff(open(path, "rb").read())
        records = set()
        for key, chunk in objects.items():
            if key[0] == "RDFF":
                try:
                    recs, _ = dataitems.records(chunk)
                except Exception:
                    continue
                records.update(r.data[:0x17] for r in recs[:1])
        ours = [r for c in ravlog.RAV_PLAIN.values() for _, r in c] + [r for _, r in ravlog.RAV_LEATHER] + [ravlog.RAV_CLOAK]
        for rec in ours:
            self.assertIn(rec, records, rec.hex())

    def test_rebound(self):
        """While the sequel's layout is on, startgear's items are the sequel's."""
        from dsloader import ravlog, startgear
        sl = startgear.LEATHER
        ravlog.apply_layout()
        try:
            self.assertIs(startgear.LEATHER, ravlog.RAV_LEATHER)
            self.assertIs(startgear._weapon, ravlog.rav_weapon)
        finally:
            ravlog.restore_layout()
        self.assertIs(startgear.LEATHER, sl)
