"""Wake of the Ravager's side of the Loader (dsloader.ravager): its patch table, its spell records'
fixes, the config that starts it, and the launch's choice of game. With DSUN_WOTR naming the
player's own Wake of the Ravager folder (never in the repository), the copy is made from its files."""
import os
import re
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gamepatch, gff, launch, npcitems, ravager  # noqa: E402

WOTR = os.environ.get("DSUN_WOTR")


class TableTests(unittest.TestCase):
    def test_patches_reuse_sl_bytes_but_their_own(self):
        """A patch named after one of Shattered Lands' has its bytes, at the sequel's offset; only the
        path (the sequel's DS address), rand() (its seed's address), the saving throw's compare (its
        branch the other way), the AC function's end (rewritten) and Share Strength's loop (its effect
        records' fields and live count elsewhere) differ; the sequel's own patches (none of SL's name) count
        as differing."""
        sl = {p.name: p for p in gamepatch.PATCHES}
        own = set()
        for p in ravager.PATCHES:
            if p.name not in sl or (p.original, p.replacement) != (sl[p.name].original, sl[p.name].replacement):
                own.add(p.name)
        self.assertEqual(own, {"path", "save_signed", "rand", "ac", "power_end_live", "power_end_handle",
                               "power_end_owner", "power_end_count",  # (Share Strength's: the sequel's fields)
                               "pic_full", "pic_place", "pic_count", "pic_fail", "stealth", "bless_from_cell", "absorb_no_strength", "absorb_end", "rest_cures_first", "npp_save", "acid_rounds", "acid_burn", "acid_once", "acid_use", "acid_round", "ns_image", "ns_blow", "use", "window", "item_box", "view", "look", "inventory", "spell_cast", "scroll", "tick", "panel_flip", "pointer", "centre", "follow_1", "follow_2", "follow_3",
                               "cr_thac0_hp", "cr_thac0_hp2", "cr_thac0_psp", "cr_thac0_con", "hp_best", "helm_ac", "helm_ac_2", "box_ac", "held_hit", "held_damage", "two_weapons", "off_hand", "roll_max_hp",
                               "two_handed_other", "two_handed_new", "cahulaks_two", "cahulaks_swing",
                               "cahulaks_hit", "cahulaks_move", "nauseated_name", "reach", "no_double", "ranger_level", "enlarge_roll", "enlarge_dice", "scroll_learn", "learn_said", "learn_refused", "pick_any", "pick_list", "pick_page", "blur_save", "fire_shield_save", "stinking_cloud_round", "classless_save_level", "chaos_int", "color_spray_level", "cloudkill_save", "cloudkill_kills", "flame_arrow_count", "biofeedback_least", "cast_level_kept", "lower_resistance_manual", "strength_dice", "cell_adjustment_heal", "feeblemind_psionics", "rainbow_pattern_damage", "hold_undead_level", "turn_undead_manual", "spell_hit", "rest_hp", "rest_spells", "class_can_use", "thief_skill_armour", "cast_armour", "item_weapon", "item_skip", "item_armour", "mc_con", "mc_uncon", "rl_score", "rl_hp", "rl_roll_4", "rl_roll_6", "rl_roll_7", "rl_con", "rl_sum", "priest_thac0", "adnd_slots", "regen_rate", "con_save", "dual_level_menu", "dual_level_view",
                            "dual_level_window", "dual_old_prime", "dual_new_prime", "floor_all", "floor_rect"}
                         | {"xp_need_%x" % at for at in ravager.XP_READS}  # (DSCLOG2's own interrupts)
                         | {"item_name_%x" % at for at in ravager.NAME_READS})
        self.assertEqual(len({p.name for p in ravager.PATCHES}), len(ravager.PATCHES))

    def test_item_names(self):
        """The helper's header names ITEM_NAMES (+196) and its room (+198), as ravager has them; the mod's
        names land at their places (the Short Sword, SL's 144h, at 258)."""
        exe = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "DSCLOG2.EXE"), "rb").read()
        at = exe.index(b"DSCLOGR1")
        off, count = struct.unpack_from("<HH", exe, at + ravager.TSR_NAMES_OFF)
        hdr_off, = struct.unpack_from("<H", exe, at + 20)
        self.assertEqual(count, ravager.NAMES_ROOM)
        self.assertEqual(exe[at - hdr_off + off:at - hdr_off + off + count * ravager.NAME_KEPT],
                         bytes(count * ravager.NAME_KEPT))
        table = ravager.item_names()
        self.assertEqual(ravager.mod_name(npcitems.SHORT_SWORD), 258)
        place = (258 - 256) * ravager.NAME_KEPT
        self.assertEqual(table[place:place + 12], b"Short Sword\0")
        self.assertTrue(len(table) == count * ravager.NAME_KEPT)

    def test_helper_has_the_use_probes(self):
        """DSCLOG2 hooks the spell slots' two interrupts, and its header's +148 points at SLOTS_TEXT
        (zeros, four members' worth, inside the image)."""
        from dsloader import dicelog
        exe = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                ravager.HELPER_EXE), "rb").read()
        image = exe[32:]
        hdr = image.find(b"DSCLOGR1")
        self.assertEqual(hdr % 16, 0)
        slots = struct.unpack_from("<H", image, hdr + dicelog.TSR_SLOTS_OFF)[0]
        self.assertGreater(slots, hdr + 268)
        self.assertEqual(image[slots:slots + 4 * dicelog.SLOTS_SIZE], bytes(4 * dicelog.SLOTS_SIZE))
        table = struct.unpack_from("<H", image, hdr + 144)[0]  # (ALL_VECTORS)
        vectors = {image[table + 3 * n] for n in range(64) if table + 3 * n < len(image)}
        self.assertTrue({ravager.VEC_USE, ravager.VEC_WIN} <= vectors)
        self.assertTrue({ravager.VEC_ITEM_BOX, ravager.VEC_CHAR} <= vectors)
        for name, vec in (("use", ravager.VEC_USE), ("window", ravager.VEC_WIN), ("item_box", ravager.VEC_ITEM_BOX), ("inventory", ravager.VEC_CHAR)):
            p = next(p for p in ravager.PATCHES if p.name == name)
            self.assertEqual(p.replacement, bytes((0xCD, vec)) + b"\x90" * (len(p.original) - 2))

    def test_helper_has_the_labels(self):
        """DSCLOG2 hooks the labels' three interrupts (the scroll's segment kept as an immediate for the
        relocation); its header has DSCLOG's DAC offset (+238) and LBL_SLOTS (+1838, zeros, in the
        image), its +1834 the segment it sets as it loads."""
        from dsloader import combatlog, labels
        exe = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                ravager.HELPER_EXE), "rb").read()
        image = exe[32:]
        hdr = image.find(b"DSCLOGR1")
        self.assertGreater(struct.unpack_from("<H", image, hdr + combatlog.TSR_DAC)[0], 0x10)
        seg, _, off = struct.unpack_from("<HHH", image, hdr + labels.TSR_TAIL_SEG)
        self.assertEqual(seg, 0)
        self.assertGreater(off, hdr + 1872)
        self.assertEqual(image[off:off + labels.SLOTS * labels.SIZE], bytes(labels.SLOTS * labels.SIZE))
        self.assertLessEqual(off + labels.SLOTS * labels.SIZE, len(image))
        table = struct.unpack_from("<H", image, hdr + 144)[0]
        vectors = {image[table + 3 * n] for n in range(64) if table + 3 * n < len(image)}
        self.assertTrue({ravager.VEC_CAST, ravager.VEC_SCROLL, ravager.VEC_TICK} <= vectors)
        by = {p.name: p for p in ravager.PATCHES}
        self.assertEqual(by["spell_cast"].replacement, bytes((0xCD, ravager.VEC_CAST, 0x90)))
        self.assertEqual(by["tick"].replacement, bytes((0xCD, ravager.VEC_TICK)) + b"\x90" * 3)
        self.assertEqual(by["scroll"].replacement, bytes((0xCD, ravager.VEC_SCROLL, 0xA9)))

    def test_helper_has_the_panel(self):
        """DSCLOG2 hooks the panel's flip and pointer interrupts; its header has DSCLOG's panel fields:
        the picture's offset in the far block (+140, after the ring and the palette, room for
        PANEL_H_MOST rows), its segment set as it loads (+328: 0 in the file), its place (+344)."""
        from dsloader import combatlog, ravlog
        exe = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                ravager.HELPER_EXE), "rb").read()
        image = exe[32:]
        hdr = image.find(b"DSCLOGR1")
        dac = struct.unpack_from("<H", image, hdr + combatlog.TSR_DAC)[0]
        off = struct.unpack_from("<H", image, hdr + combatlog.TSR_PANEL_OFF)[0]
        self.assertEqual(off, dac + 768)
        self.assertLess(off + combatlog.PANEL_W * ravlog.PANEL_H_MOST, 0xFFF0)  # (in the HMA)
        self.assertEqual(struct.unpack_from("<H", image, hdr + combatlog.TSR_PANEL_SEG)[0], 0)
        self.assertEqual(struct.unpack_from("<HH", image, hdr + combatlog.TSR_PANEL_TOP),
                         (combatlog.PANEL_Y0, combatlog.PANEL_H))
        table = struct.unpack_from("<H", image, hdr + 144)[0]
        vectors = {image[table + 3 * n] for n in range(64) if table + 3 * n < len(image)}
        self.assertTrue({ravager.VEC_FLIP, ravager.VEC_POINTER} <= vectors)
        by = {p.name: p for p in ravager.PATCHES}
        self.assertEqual(by["panel_flip"].replacement, bytes((0xCD, ravager.VEC_FLIP)) + b"\x90" * 6)
        self.assertEqual(by["pointer"].replacement, bytes((0xCD, ravager.VEC_POINTER, 0x90, 0x90)))
        self.assertEqual(by["centre"].replacement, bytes((0xCD, ravager.VEC_CENTRE, 0x90, 0x90, 0x90)))
        for n in ("follow_1", "follow_2", "follow_3"):
            self.assertEqual(by[n].replacement, bytes((0xCD, ravager.VEC_FOLLOW, 0x90)))

    def test_item_fields(self):
        """SL's item power (a byte at 0Fh) is the sequel's word at 10h; from SL's 10h on, two bytes on."""
        self.assertEqual([ravager.item_field(sl) for sl in (0x0A, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x14, 0x15)],
                         [0x0A, 0x0E, 0x10, 0x12, 0x13, 0x14, 0x16, None])


    def test_path_writes_dot_backslash_at_its_ds(self):
        p = next(p for p in ravager.PATCHES if p.name == "path")
        self.assertEqual(p.replacement[:6], bytes.fromhex("c706f244") + b".\\")
        self.assertEqual(len(p.replacement), len(p.original))

    def test_spell_fixes_are_gamepatch_patches_in_its_records(self):
        names = {p.name for p in gamepatch.PATCHES}
        for name, (spell, field) in ravager.SPELL_FIXES.items():
            self.assertIn(name, names)
            self.assertLess(spell, ravager.SPELL_COUNT)
            self.assertLessEqual(field + len(next(p for p in gamepatch.PATCHES if p.name == name).original), 32)
        # (SSI fixed these two itself: not in the table)
        self.assertNotIn("dispel_effect", ravager.SPELL_FIXES)
        self.assertNotIn("bestow_curse_save", ravager.SPELL_FIXES)

    def test_spells_manual_switch_leaves_its_fixes_out(self):
        self.assertEqual(ravager.skipped({}), frozenset())
        self.assertEqual(ravager.skipped({"spells_manual": False}), frozenset(gamepatch.SPELLS_MANUAL))

    def test_conf_lines(self):
        lines = ravager.conf_lines(r"C:\GOG\Ravager", r"C:\mod\dos", cd=r"C:\GOG\Ravager\game.ins",
                                   game_end="GAMEEND.COM")
        self.assertIn("ems=false", lines)
        self.assertIn(r'mount c "C:\GOG\Ravager"', lines)
        self.assertIn(r'imgmount f "C:\GOG\Ravager\game.ins" -t iso', lines)
        self.assertIn(r'mount d "C:\mod\dos"', lines)
        self.assertLess(lines.index(r"d:\umbplus.com"), lines.index(r"lh d:\dsclog2.exe"))
        self.assertLess(lines.index(r"lh d:\dsclog2.exe"), lines.index(r"d:\dsunlog2.exe -W0 -L"))
        self.assertLess(lines.index("c:"), lines.index(r"d:\dsunlog2.exe -W0 -L"))
        self.assertEqual(lines[-3:], [r"d:\gameend.com", "exit", ""])

    def test_not_a_wotr_dir(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(ravager.is_wotr_dir(d))
            with open(os.path.join(d, "DSUN.EXE"), "wb") as f:
                f.write(b"\0" * gamepatch.GOG_SIZE)  # (Shattered Lands' size)
            self.assertFalse(ravager.is_wotr_dir(d))
            with open(os.path.join(d, "DSUN.EXE"), "wb") as f:
                f.write(b"\0" * ravager.WOTR_SIZE)
            self.assertTrue(ravager.is_wotr_dir(d))

    def test_launch_takes_the_sequel_its_own_way(self):
        """_launch hands a Wake of the Ravager folder to _launch_wotr (its own DOSBox config)."""
        called = []
        real = launch._launch_wotr
        launch._launch_wotr = lambda game_dir, settings: called.append(game_dir) or ("proc", "why")
        try:
            with tempfile.TemporaryDirectory() as d:
                with open(os.path.join(d, "DSUN.EXE"), "wb") as f:
                    f.write(b"\0" * ravager.WOTR_SIZE)
                self.assertEqual(launch._launch(d, {}), ("proc", "why"))
                self.assertEqual(called, [d])
        finally:
            launch._launch_wotr = real


class ItemTypeTests(unittest.TestCase):
    def test_wotr_type(self):
        """The mod's metal short sword (SL 115) in the sequel's 15 bytes: the words as bytes, the rest moved up."""
        self.assertEqual(ravager.wotr_type(npcitems.TYPES[0]).hex(), "01301efa040501010601000072160001"[:30])
        self.assertEqual(ravager.mod_type(game.SHORT_SWORD_TYPE), 102)
        with self.assertRaises(ravager.RavagerError):
            ravager.wotr_type(bytes(2) + struct.pack("<H", 300) + bytes(16))

    def test_objects_fixed(self):
        from test_ravtransfer import _gff
        data = _gff({("ALL ", 4): bytes(range(102)) * 15, ("ALL ", 5): b"names", ("OJFF", 1): b"o" * 16})
        out, done = ravager.objects_fixed(data)
        got = gff.read_gff(out)
        self.assertEqual((done, len(got[("ALL ", 4)]) // 15, got[("ALL ", 5)]), (["mod_types"], 135, b"names"))
        self.assertEqual(got[("ALL ", 4)][102 * 15:103 * 15], ravager.wotr_type(npcitems.TYPES[0]))
        self.assertEqual(ravager.objects_fixed(data, {"mod_types"}), (data, []))
        with self.assertRaises(ravager.RavagerError):
            ravager.objects_fixed(_gff({("ALL ", 4): bytes(15)}))


class LayoutTests(unittest.TestCase):
    def test_fields_checked_in_memory(self):
        """The fields read from Gerakis's records in a running game (2026-11-19)."""
        self.assertEqual([ravager.creature_field(o) for o in (0, 2, 4, 6, 0x1A, 0x1B, 0x1C, 0x1D, 0x1F, 0x22, 0x28)],
                         [0, 2, 4, 6, 0x12, 0x13, 0x14, 0x15, 0x16, 0x19, 0x21])
        self.assertEqual([ravager.sheet_field(o) for o in (0, 8, 0x10, 0x12, 0x18, 0x21, 0x24, 0x37, 0x3F, 0x43, 0x45)],
                         [0, 8, 0x0E, 0x10, 0x12, 0x1B, 0x1E, 0x31, 0x39, 0x3D, 0x3F])
        for gone in (0x0E, 0x0F, 0x14, 0x15, 0x16, 0x17, 0x3C):
            self.assertIsNone(ravager.sheet_field(gone))

    def test_fields_fit_the_records(self):
        for o in range(0x3A):
            f = ravager.creature_field(o)
            self.assertTrue(f is None or f < ravager.CREATURE_SIZE, hex(o))
        for o in range(0x47):
            f = ravager.sheet_field(o)
            self.assertTrue(f is None or f < ravager.SHEET_SIZE, hex(o))


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
class GameFileTests(unittest.TestCase):
    def test_xp_table_fixed(self):
        """The sequel's XP table (DATA 1000, in hundreds) with DSCLOG2's XP_FIXES is tables.RAV_XP;
        the fixes are where they differ."""
        from dsloader import tables
        data = gff.read_gff(open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read())[("DATA", 1000)]
        asm = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        fixes = {(int(r), int(i)): int(x) for r, i, x in re.findall(r"^\s+XP_FIX (\d+), (\d+), (\d+)", asm, re.M)}
        for row, name in enumerate(tables.ROWS):
            game = struct.unpack_from("<20H", data, row * 40)
            for index in range(20):
                self.assertEqual(fixes.get((row, index), game[index] * 100), tables.RAV_XP[name][index])
                self.assertEqual((row, index) in fixes, game[index] * 100 != tables.RAV_XP[name][index])

    def test_copy_made(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(ravager.prepare(WOTR, d, {}))
            exe = open(os.path.join(d, ravager.PATCHED_EXE), "rb").read()
            orig = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
            for p in ravager.PATCHES:
                self.assertEqual(exe[p.offset:p.offset + len(p.replacement)], p.replacement, p.name)
            changed = sum(len(p.original) for p in ravager.PATCHES)
            self.assertEqual(sum(a != b for a, b in zip(exe, orig)) <= changed, True)
            res = gff.read_gff(open(os.path.join(d, ravager.RESOURCE_COPY), "rb").read())
            game = gff.read_gff(open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read())
            self.assertEqual(res.keys(), game.keys())
            changed_spells = {k[1] for k in game if game[k] != res[k]}
            dodged = {k[1] for k in game if k[0] == "DATA" and k[1] < ravager.SPELL_COUNT
                      and len(game[k]) == ravager.SPELL_SIZE
                      and struct.unpack_from("<H", game[k], ravager.SPELL_FLAGS)[0] & 0x86}
            self.assertEqual(changed_spells, {s for s, _ in ravager.SPELL_FIXES.values()} | dodged)
            gpl = open(os.path.join(d, ravager.SCRIPT_COPY), "rb").read()
            own = open(os.path.join(WOTR, ravager.SCRIPT_FILE), "rb").read()
            places = gff.index_places(own, "GPL ")
            differ = [i for i, (a, b) in enumerate(zip(gpl, own)) if a != b]
            wanted = []
            for chunk, offset, original, replacement in ravager.SCRIPT_FIXES.values():
                at = places[chunk][1] + offset
                self.assertEqual(gpl[at:at + len(replacement)], replacement)
                wanted += [at + i for i in range(len(original)) if original[i] != replacement[i]]
            self.assertEqual((len(gpl), differ), (len(own), sorted(wanted)))
            objs = gff.read_gff(open(os.path.join(d, ravager.OBJECTS_COPY), "rb").read())
            own = gff.read_gff(open(os.path.join(WOTR, ravager.OBJECTS_FILE), "rb").read())
            types = objs[ravager.TYPES_CHUNK]
            self.assertEqual(types[:len(own[ravager.TYPES_CHUNK])], own[ravager.TYPES_CHUNK])
            self.assertEqual(len(types), (ravager.GAME_TYPES + len(npcitems.TYPES)) * ravager.TYPE_SIZE)
            self.assertEqual({k for k in own if own[k] != objs[k] and k[0] != "GFFI"}, {ravager.TYPES_CHUNK})  # (GFFI: the index)

    def test_effects_kept_switch(self):
        """Spells kept on the Effects screen: SL's two patches by name, left out with the switch off."""
        names = {p.name for p in ravager.PATCHES}
        self.assertTrue(set(gamepatch.EFFECTS_KEPT) <= names)
        self.assertEqual(ravager.skipped({}) & set(gamepatch.EFFECTS_KEPT), frozenset())
        self.assertEqual(ravager.skipped({"effects_kept": False}) & set(gamepatch.EFFECTS_KEPT),
                         frozenset(gamepatch.EFFECTS_KEPT))

    def test_hp_best(self):
        """The better hit die: SL's patch by name at the sequel's roll, DSCLOG2's PROBE_HP_BEST (the
        Options tab's switch is DSCLOG2's RULES word, written by the Loader: no patch left out)."""
        p = next(p for p in ravager.PATCHES if p.name == "hp_best")
        self.assertEqual((p.offset, p.original, p.replacement), (0x95025, b"\x8b\xc8", bytes((0xCD, ravager.VEC_HP_BEST))))
        self.assertEqual(ravager.RULES_PORTED & game.RULE_HP_BEST, game.RULE_HP_BEST)
        self.assertNotIn("hp_best", ravager.skipped({"best_hit_die": False}))

    def test_script_fix_skipped(self):
        data = open(os.path.join(WOTR, ravager.SCRIPT_FILE), "rb").read()
        same, done = ravager.script_fixed(data, set(ravager.SCRIPT_FIXES))
        self.assertEqual((same, done), (data, []))

    def test_manual_check_decodes(self):
        """The copy's GPL 331 still decodes whole, and starts with the right answer's settings."""
        from dsloader import gpl
        data, _ = ravager.script_fixed(open(os.path.join(WOTR, ravager.SCRIPT_FILE), "rb").read())
        scripts, types = gpl.load_scripts(data)
        ops = gpl.decode(scripts[("GPL ", 331)], types)
        self.assertEqual([(o.code, o.args) for o in ops[1:5]],
                         [(0x16, [("n", 0), ("var", 14, 0)]), (0x16, [("n", 255), ("var", 7, 32)]),
                          (0x16, [("n", 7), ("var", 7, 29)]), (0x15, [])])

    def test_spells_manual_off(self):
        data = open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read()
        _, done = ravager.spell_fixed(data, ravager.skipped({"spells_manual": False}))
        self.assertEqual(set(done), {"cause_serious", "cause_critical", "brave_fear_21", "brave_fear_43",
                                     "brave_fear_78", "brave_fear_132", "scare_save", ravager.DODGE_FIX})

    def test_dodge(self):
        """Fire, cold and electricity: the spells the saving throw doubled the d20 for (flags 86h) carry
        the dodge bit (SL's CATEGORY_DODGE), Fireball and Cone of Cold among them, Hold Person not; the
        doubling gone (no_double)."""
        data = open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read()
        fixed, done = ravager.spell_fixed(data)
        places = gff.index_places(fixed, "DATA")
        marked = {s for s in range(ravager.SPELL_COUNT) if s in places
                  and fixed[places[s][1] + ravager.SPELL_CATEGORY] & game.CATEGORY_DODGE}
        self.assertEqual(len(marked), 32)
        self.assertTrue({27, 58, 32, 1} <= marked)  # Fireball, Cone of Cold, Lightning Bolt, Burning Hands
        self.assertNotIn(30, marked)  # Hold Person
        self.assertEqual(ravager.spell_fixed(data, {ravager.DODGE_FIX})[0][places[27][1] + 0x11], 0)
        p = next(p for p in ravager.PATCHES if p.name == "no_double")
        self.assertEqual(open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()[p.offset - 0x0A:p.offset + 2],
                         bytes.fromhex("f746f48600" "7408" "8a46fe" "d0e0"))


if __name__ == "__main__":
    unittest.main()
