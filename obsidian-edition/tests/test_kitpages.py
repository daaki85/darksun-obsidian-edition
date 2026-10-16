import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, kitpages, weaponpages  # noqa: E402


class KitPageTests(unittest.TestCase):
    def test_ids_clear(self):
        """The kit pages' buttons come after the weapon pages' and the level-up window's rows (to
        86Fh), and their windows are none of the game's (3000-3013, 3020, 3024) nor the weapon
        pages' (3014-3019, 3021)."""
        buttons = [kitpages.row_id(g, k + 1) for g, names in kitpages.KITS.items() for k in range(len(names))] \
            + [kitpages.KIT_NONE, kitpages.KIT_VIEW]
        self.assertEqual(len(set(buttons)), 39)
        self.assertTrue(all(0x870 <= b < 0x8B0 for b in buttons))  # (STORE and RECALL after them: rollstore.py)
        windows = [kitpages.KIT_DISCIPLINES, kitpages.KIT_SPHERES, kitpages.KIT_LAST_PAGE] \
            + [kitpages.KIT_WINDOW + c for c in range(len(kitpages.KITS))]
        taken = set(range(3000, 3014)) | {3020, 3024, weaponpages.PICKER, weaponpages.WARRIOR_DISCIPLINES,
                                          weaponpages.WARRIOR_SPHERES} | set(weaponpages.PAGES)
        self.assertEqual(len(set(windows)), 22)
        self.assertFalse(taken & set(windows))

    def test_rows(self):
        self.assertEqual(sorted(kitpages.KITS), list(game.CREATION_CLASS_NAMES) + sorted(kitpages.MULTI))
        self.assertEqual(kitpages.KITS[4], ("Arena Champion", "Twin-blade", "Brute"))
        texts = [kitpages.row_text(n) for names in kitpages.KITS.values() for n in names]
        self.assertEqual(len(texts), 37)
        self.assertIn("W-AVENGER", texts)
        self.assertIn("CHAMPION", texts)
        self.assertIn("M-WARRIOR", texts)
        self.assertIn("BATTLMAGE", texts)
        self.assertIn("WARDEN", texts)
        self.assertIn("ELEMENTAL", texts)
        self.assertTrue(all(len(t) <= 11 for t in texts))

    @unittest.skipUnless(os.environ.get("DSUN_RESOURCE"), "DSUN_RESOURCE (the game's RESOURCE.GFF) not given")
    def test_row_widths(self):
        """Every row within ROW_WIDTH in the game's own letters, clear of the panel's frame."""
        from dsloader import gff
        with open(os.environ["DSUN_RESOURCE"], "rb") as f:
            widths = kitpages.row_widths(gff.read_gff(f.read()))
        self.assertEqual(len(widths), 38)
        self.assertEqual({n: w for n, w in widths.items() if w > kitpages.ROW_WIDTH}, {})

    def test_kit_names(self):
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21], sheet[kitpages.KIT_BYTE] = 10, 1  # a gladiator
        self.assertEqual(kitpages.kit_names(bytes(sheet)), ["Arena Champion"])
        sheet[0x21] = 15  # a fire ranger
        self.assertEqual(kitpages.kit_names(bytes(sheet)), ["Stalker"])
        sheet[0x22] = 12  # and a psionicist: no kit
        self.assertEqual(kitpages.kit_names(bytes(sheet)), [])
        sheet[0x22], sheet[kitpages.KIT_BYTE] = 0, 0
        self.assertEqual(kitpages.kit_names(bytes(sheet)), [])
        sheet[kitpages.KIT_BYTE] = 0xFF  # (KIT_OPEN: none chosen)
        self.assertEqual(kitpages.kit_names(bytes(sheet)), [])

    def test_panel_windows(self):
        both = game.RULE_SPECIALIZE | game.RULE_KITS
        self.assertEqual(kitpages.SPECIALIZE, game.RULE_SPECIALIZE)
        self.assertEqual(kitpages.KITS_ON, game.RULE_KITS)
        self.assertEqual(kitpages.panel_windows((8, 0, 0), both), (3022, 3023))
        self.assertEqual(kitpages.panel_windows((3, 0, 0), both), (3018, 3019))  # (KITS on the last page)
        self.assertEqual(kitpages.panel_windows((3, 0, 0), game.RULE_KITS), (3022, 3023))
        self.assertEqual(kitpages.panel_windows((1, 0, 0), both), (3012, 3023))
        self.assertEqual(kitpages.panel_windows((7, 0, 0), both), (3012, 3019))
        # a Battle Mage (a preserver's second kit): a warrior's windows, for its weapon spec
        self.assertEqual(kitpages.panel_windows((5, 0, 0), both, kit=2), (3018, 3019))
        self.assertEqual(kitpages.panel_windows((5, 0, 0), both, kit=1), (3022, 3023))
        self.assertEqual(kitpages.panel_windows((5, 0, 0), game.RULE_KITS, kit=2), (3022, 3023))
        self.assertEqual(kitpages.panel_windows((8, 6, 0), both), (3012, 3013))

    def test_no_kit_first(self):
        """The kit page's rows: NO KIT at the top (the kit the sheet starts with), then the
        class's three in KITS's order."""
        ids = [c for c, _, _ in weaponpages._items(self.kit_window(3))]
        self.assertEqual(ids, [kitpages.KIT_NONE, kitpages.KIT_ROW + 6, kitpages.KIT_ROW + 7, kitpages.KIT_ROW + 8,
                               weaponpages.BACK])

    def test_row_as_wide_as_its_label(self):
        """A row's button is as wide as its label, not AIR's 33 pixels (a click on the rest of a
        longer name, MYRMIDON's or LNG SWORD's, was taken by nothing)."""
        import struct
        air = bytearray(110)
        air[:4] = b"BUTN"
        struct.pack_into("<I", air, 8, weaponpages.ROW_TEMPLATE)
        struct.pack_into("<HH", air, weaponpages.BUTN_SIZE, 33, 7)
        font = {ch: [[True] * 5 for _ in range(weaponpages.HEIGHT)] for ch in "MYRIDON"}
        button = weaponpages.row_button(bytes(air), 0x871, font, "MYRMIDON")
        want = len(weaponpages.label(font, "MYRMIDON", weaponpages.ROW_PAD, 1)[0])
        self.assertGreater(want, 33)
        self.assertEqual(struct.unpack_from("<HH", button, weaponpages.BUTN_SIZE), (want, 7))
        self.assertEqual(struct.unpack_from("<I", button, 8)[0], 0x871)

    def kit_window(self, cls):
        """CLS's kit page, from a spheres' window of four rows and a button (pictures left out)."""
        import struct
        from unittest import mock
        spheres = bytearray(weaponpages.ITEM_AT + 5 * weaponpages.ITEM_SIZE)
        struct.pack_into("<I", spheres, 4, len(spheres))
        struct.pack_into("<H", spheres, weaponpages.WIND_COUNT, 5)
        for i, cid in enumerate((0x7FA, 0x7FB, 0x7FC, 0x7FD, 0x7FF)):
            struct.pack_into("<IHH", spheres, weaponpages.ITEM_AT + i * weaponpages.ITEM_SIZE + 8, cid, 7, 15 + 8 * i)
        resource = {("WIND", weaponpages.SPHERES): bytes(spheres), ("WIND", weaponpages.DISCIPLINES): bytes(spheres),
                    ("ICON", weaponpages.ROW_TEMPLATE): b"", ("ICON", weaponpages.TOGGLE_TEMPLATE): b"",
                    ("BUTN", weaponpages.ROW_TEMPLATE): b"", ("BUTN", weaponpages.TOGGLE_TEMPLATE): b""}
        with mock.patch.object(weaponpages, "glyphs", return_value={}), \
                mock.patch.object(weaponpages, "_colours", return_value=[1, 2, 3]), \
                mock.patch.object(weaponpages, "picture", return_value=b"pic"):
            return kitpages.chunks(resource)[("WIND", kitpages.KIT_WINDOW + cls - 1)]


if __name__ == "__main__":
    unittest.main()


class DormantKitTests(unittest.TestCase):
    """A human who changes class keeps its kit asleep until the new class's level passes the old."""

    def sheet(self, classes, levels, kit, race=1):
        s = bytearray(game.SHEET_SIZE)
        s[0x18], s[kitpages.KIT_BYTE] = race, kit
        s[0x21:0x21 + len(classes)] = bytes(classes)
        s[0x24:0x24 + len(levels)] = bytes(levels)
        return bytes(s)

    def test_dormant_then_awake(self):
        from dsloader import kits
        for new_level, awake in ((1, False), (3, False), (4, True)):
            with self.subTest(new_level=new_level):
                s = self.sheet((9, 11), (new_level, 3), 2)  # (a Battle Mage, preserver 3, now a fighter)
                self.assertEqual(kitpages.kit_place(s), 1)
                self.assertEqual(kitpages.kits_of(s), [(kits.BATTLE_MAGE, 1, awake)])
                self.assertEqual(kitpages.kit_ids(s), [kits.BATTLE_MAGE] if awake else [])
                self.assertEqual((kitpages.kit_level(s, kits.BATTLE_MAGE), kitpages.kit_class_of(s, kits.BATTLE_MAGE)),
                                 (3, 11))
                self.assertEqual(kitpages.kit_names(s), ["Battle Mage"])

    def test_twice_changed(self):
        """The first class's kit is the last of three's, in KIT_BYTE's lowest bits."""
        from dsloader import kits
        s = self.sheet((17, 9, 11), (6, 4, 3), 2)
        self.assertEqual((kitpages.kit_place(s), kitpages.kit_ids(s)), (2, [kits.BATTLE_MAGE]))

    def test_kits_of_each_class(self):
        """A kit for each class: two bits each, the first class's lowest, each class taken after the
        next two; each awake while its class is (the class it has now, or one passed by it)."""
        from dsloader import kits
        # a Myrmidon fighter 3, a Scholar preserver 5, now a psionicist 4: the fighter's awake
        s = self.sheet((12, 11, 9), (4, 5, 3), 0b000101)
        self.assertEqual(kitpages.kits_of(s), [(kits.MYRMIDON, 2, True), (kits.SCHOLAR, 1, False)])
        self.assertEqual(kitpages.kit_ids(s), [kits.MYRMIDON])
        self.assertEqual(kitpages.kit_names(s), ["Myrmidon", "Scholar"])
        self.assertEqual(kitpages.kit_level(s, kits.SCHOLAR), 5)
        s = self.sheet((12, 11, 9), (6, 5, 3), 0b100101)  # (psionicist 6, a Mind Warrior: all awake)
        self.assertEqual(kitpages.kit_ids(s), [kits.MYRMIDON, kits.SCHOLAR, kits.MIND_WARRIOR])
        self.assertEqual(kitpages.kit_place_of(s, kits.MIND_WARRIOR), 0)
        self.assertEqual(kitpages.kit_byte(s, 0, 0), 0b000101)
        self.assertEqual(kitpages.kit_byte(s, 1, 3), 0b101101)

    def test_multiclass_no_kit(self):
        """Two classes at once with no group of their race and pair: no kit."""
        from dsloader import kits
        s = self.sheet((9, 11), (3, 3), 2, race=2)
        self.assertIsNone(kitpages.kit_place(s))
        self.assertEqual((kitpages.kits_of(s), kitpages.kit_ids(s), kitpages.kit_level(s, kits.BATTLE_MAGE)),
                         ([], [], 0))
        self.assertIsNone(kitpages.kit_place(self.sheet((9, 17), (3, 3), 1, race=3)))  # (an elf fighter/thief)

    def test_multiclass_kits(self):
        """A race's pair of classes with a group (kitpages.MULTI): its kit in KIT_BYTE, place 0; the
        pair the other way round too; only the group's own kits."""
        from dsloader import kits
        for classes, race, kit, name in (((9, 17), 4, 1, "Shadowblade"), ((17, 9), 4, 2, "Military Scout"),
                                         ((9, 17), 2, 2, "Wayfinder"), ((3, 9), 3, 1, "Battle Dancer"),
                                         ((6, 9), 4, 1, "Wilderness Avenger"), ((2, 14), 4, 1, "Rescuer")):
            with self.subTest(classes=classes, race=race):
                s = self.sheet(classes, (2, 2), kit, race=race)
                self.assertEqual(kitpages.kit_place(s), 0)
                self.assertEqual(kitpages.kit_names(s), [name])
                self.assertEqual(kitpages.kit_ids(s), [kitpages.KIT_IDS[name]])
                self.assertEqual(kitpages.kit_level(s, kitpages.KIT_IDS[name]), 2)
        self.assertEqual(kitpages.kit_ids(self.sheet((3, 9), (2, 2), 2, race=3)), [])  # (the elf's group has one)
        self.assertEqual(kitpages.kit_ids(self.sheet((9, 17), (2, 2), 0, race=4)), [])
        self.assertEqual(kitpages.KIT_IDS["Battle Dancer"], 37)
        self.assertEqual(kitpages.multi_group(4, (8, 3, 0)), 10)
        self.assertEqual(kitpages.multi_group(1, (3, 8, 0)), 0)
        self.assertEqual(kitpages.multi_group(4, (3, 8, 6)), 0)
        self.assertEqual(kitpages.kit_class((3, 8, 0), game.RULE_KITS, race=2), 13)
        self.assertEqual(kitpages.kit_class((3, 8, 0), 0, race=2), 0)
        self.assertEqual(kitpages.panel_windows((3, 8, 0), game.RULE_KITS, race=4), (3022, 3023))
        self.assertEqual(kitpages.row_id(13, 2), 0x897)
        self.assertEqual(kitpages.row_id(8, 3), 0x887)

    def test_battle_mage_weapon_spec(self):
        """Its chosen weapon spec the kit's alone: nothing for the fighter while asleep, expertise
        (not specialization) when awake."""
        from dsloader import specialize
        rules = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = game.RULE_KITS | game.RULE_SPECIALIZE
        self.addCleanup(setattr, game, "RULES_IN_FORCE", rules)
        axe, sword = 22, 81  # (item types: the metal axe, the bone long sword)
        axe_kind = specialize.kind_of(axe)
        for new_level, want, other in ((2, specialize.NONE, specialize.NONE), (4, specialize.EXPERT, specialize.PLAIN)):
            s = bytearray(self.sheet((9, 11), (new_level, 3), 2))
            s[game.SPEC_SLOTS] = axe_kind + 1
            with self.subTest(new_level=new_level):
                self.assertEqual(specialize.skill(bytes(s), axe), want)
                self.assertEqual(specialize.skill(bytes(s), sword), other)

