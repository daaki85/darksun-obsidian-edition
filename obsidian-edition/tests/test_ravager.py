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

from dsloader import dataitems, game, gamepatch, gff, icons, launch, npcitems, ravager, ravspells  # noqa: E402

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
                               "pic_full", "pic_place", "pic_count", "pic_fail", "stealth", "bless_from_cell", "absorb_no_strength", "absorb_end", "rest_cures_first", "npp_save", "acid_rounds", "acid_burn", "acid_once", "acid_use", "acid_round", "ns_image", "ns_blow", "use", "window", "window_fail", "item_box", "view", "look", "inventory", "spell_cast", "scroll", "tick", "panel_flip", "pointer", "centre", "follow_1", "follow_2", "follow_3",
                               "cr_thac0_hp", "cr_thac0_hp2", "cr_thac0_psp", "cr_thac0_con", "hp_best", "helm_ac", "helm_ac_2", "box_ac", "held_hit", "held_damage", "two_weapons", "off_hand", "roll_max_hp",
                               "two_handed_other", "two_handed_new", "cahulaks_two", "cahulaks_swing",
                               "cahulaks_hit", "cahulaks_move", "nauseated_name", "reach", "second_foe_back", "no_double", "ranger_level", "enlarge_roll", "enlarge_dice", "scroll_learn", "learn_said", "learn_refused", "pick_any", "pick_list", "pick_page", "blur_save", "fire_shield_save", "stinking_cloud_round", "classless_save_level", "chaos_int", "color_spray_level", "cloudkill_save", "cloudkill_kills", "flame_arrow_count", "biofeedback_least", "cast_level_kept", "lower_resistance_manual", "strength_dice", "cell_adjustment_heal", "feeblemind_psionics", "rainbow_pattern_damage", "hold_undead_level", "turn_undead_manual", "spell_hit", "spell_hit_immune", "rest_hp", "rest_spells", "class_can_use", "thief_skill_armour", "thief_skill_armour_out", "cast_armour", "item_weapon", "item_skip", "item_armour", "mc_con", "mc_uncon", "rl_score", "rl_hp", "rl_roll_4", "rl_roll_6", "rl_roll_7", "rl_con", "rl_sum", "priest_thac0", "adnd_slots", "regen_rate", "con_save", "dual_level_menu", "dual_level_view",
                            "kit_initiative", "kit_ranger_cast", "kp_disc_win", "kp_sphere_win", "kp_disc_click",
                            "kp_sphere_click", "kp_shown", "kp_class", "kp_race", "kp_open", "dual_kit",
                            "el_sphere_know", "el_sphere_level", "el_sphere_cast",
                            "psionic_blast", "blast_knockout", "rl_try", "roll_store", "gear_done",
                            "price_shown", "price_afford", "price_buy", "sell_price", "sell_keep",
                            "message_window", "message_shown", "text", "message",
                            "dual_level_window", "dual_old_prime", "dual_new_prime", "floor_all", "floor_rect", "protection_ac", "protection_save", "amulet_resistance", "weapon_cast", "worn_spell_off", "join_ready", "tome", "plain_arrow", "spec_damage", "dam_line", "missile_line", "view_dam", "ef_rows", "ef_click", "unlook", "hit", "ranger_two", "greq_load", "shop_loop",
                            "sound_3c", "sound_3e", "sheet_party_loop", "sheet_table", "sheet_record_size",
                            "sheet_record_load", "sheet_save_size", "sheet_new_tail", "thief_table", "backstab_dice",
                            "cr_picks", "psi_grant", "psi_grant_psionicist", "psi_count", "psi_list", "psi_cycle",
                            "psi_click", "pick_top", "level_cap_up", "level_cap_view", "level_clamp", "xp_suffix", "level_ordinal",
                            "thief_hd_roll", "thief_hd_con", "thief_hd_clamp", "save_table", "f10_pin",
                            "cr_weapons", "pk_win", "pk_title", "pk_fill", "pk_click", "pk_hover", "gear_hands", "lv_weapons",
                            "fig_wide_all", "fig_wide", "fig_keep", "shop_shine",
                            "pp_show", "pp_click", "pp_lit", "pp_arm", "pp_text_hover", "pp_text_info", "pp_info",
                            "pp_hand", "shinobi_mage", "psp_use", "psp_can_use", "psp_failed", "psp_defence", "psp_keep",
                            "psp_can_keep", "hit_die", "hit_gain", "max_psp", "hit_round", "kit_cast_level", "kit_cure", "avenger_cause_area",
                            "avenger_cause_one",
                            "cr_die", "cr_psp_wis", "cr_psp", "shinobi_cast_level", "shinobi_level_up"}
                         | {"sheet_stride_%x" % at for at in ravager.SHEET_STRIDES}  # (the 48h sheet)
                         | {"sheet4_%x" % f[0] for f in ravager.SHEET4_FIELDS}  # (the summoned ally's sheet)
                         | {"xp_need_%x" % at for at in ravager.XP_READS}  # (DSCLOG2's own interrupts)
                         | {"item_name_%x" % at for at in ravager.NAME_READS}
                         | {p.name for p in ravspells.program_patches()})  # (the new spells)
        self.assertEqual(len({p.name for p in ravager.PATCHES}), len(ravager.PATCHES))

    def test_gear_hands(self):
        """A new character's starting gear (the table of GEAR_TABLE_AT) puts every weapon in the right hand
        (3) and every shield in the left (10): the fighter's long sword and the cleric's club in front of their
        shields, the druid's, preserver's and psionicist's weapon out of the empty left hand; only slots
        change, and the gladiator's second long sword stays in the left hand."""
        old, new = ravager.GEAR_TABLE, ravager.gear_table_fixed()
        self.assertEqual(len(old), 35 * 3)
        entries = lambda t: [(struct.unpack_from("<H", t, 3 * n)[0], t[3 * n + 2]) for n in range(35)]
        before, after = entries(old), entries(new)
        self.assertEqual([o for o, _ in before], [o for o, _ in after])
        changed = {n: (before[n][1], after[n][1]) for n in range(35) if before[n] != after[n]}
        self.assertEqual(changed, {2: (3, 10), 3: (10, 3), 7: (10, 3), 0x0A: (10, 3), 0x16: (3, 10),
                                   0x17: (10, 3), 0x1B: (10, 3)})
        self.assertEqual(after[0x16], (842, 10))  # (the fighter's +1 shield)
        self.assertEqual(after[0x17], (633, 3))   # (its +1 long sword)
        self.assertEqual(after[0x13], (633, 10))  # (the gladiator's second)

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

    def test_screens_sites(self):
        """The DAM lines, the Effects screen's lines and the Look box's whole description are DSCLOG2's sites
        70-75 (the kits' take 60 up, the kit pages 62-69), each a routine in its SITE_TABLE, and the
        header's +158 points at LOOK_FULL (700 zeros inside the image)."""
        from dsloader import dicelog
        sites = {"dam_line": 70, "missile_line": 71, "view_dam": 72, "ef_rows": 73, "ef_click": 74, "unlook": 75}
        for name, number in sites.items():
            p = next(p for p in ravager.PATCHES if p.name == name)
            self.assertEqual(p.replacement[:3], bytes((0xCD, ravager.VEC_SITE, number)), name)
        src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        for name, number in sites.items():
            self.assertRegex(src, r"\n        dw %s +; %d SITE_" % (name, number))
        exe = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                ravager.HELPER_EXE), "rb").read()
        image = exe[32:]
        hdr = image.find(b"DSCLOGR1")
        full = struct.unpack_from("<H", image, hdr + dicelog.TSR_LOOK_FULL_OFF)[0]
        self.assertGreater(full, hdr + 268)
        self.assertEqual(image[full:full + dicelog.LOOK_FULL_SIZE], bytes(dicelog.LOOK_FULL_SIZE))

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

    def test_helper_pans_to_the_chosen_enemy(self):
        """DSCLOG2 has DSCLOG's PAN_X and PAN_Y (+230, +232: zeros in the file, targeting.TSR_PAN), PAN_TICK
        called from PROBE_SCROLL and kept resident (before RESIDENT_END), and the Loader makes the two words
        writable with Tab's (RavDiceLog._target_ranges); with DSUN_WOTR, the game's centring routine (file
        219E3h, VIEW_AGAIN's CENTRE) starts as PAN_TICK has it: x less 160 and y less 100, rounded to 8, to
        the view's top left (DS:1408h, 140Ah), then kept inside the map's limits (DS:14D7h to 14DDh)."""
        import inspect
        from dsloader import ravlog, targeting
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image = open(os.path.join(here, "dos", ravager.HELPER_EXE), "rb").read()[32:]
        hdr = image.find(b"DSCLOGR1")
        self.assertEqual(struct.unpack_from("<HH", image, hdr + targeting.TSR_PAN), (0, 0))
        src = open(os.path.join(here, "dos", "dsclog2.asm")).read()
        self.assertRegex(src, r"\npan_x +dw 0 +; \+%d " % targeting.TSR_PAN)
        self.assertRegex(src, r"\npan_y +dw 0 +; \+%d " % (targeting.TSR_PAN + 2))
        scroll = src[src.index("\nprobe_scroll:"):]
        self.assertIn("call pan_tick", scroll[:scroll.index("iret")])
        self.assertLess(src.index("\npan_tick:"), src.index("\nresident_end:"))
        self.assertIn("targeting.TSR_PAN", inspect.getsource(ravlog.RavDiceLog._target_ranges))
        if WOTR:
            exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
            self.assertEqual(exe[0x219E3:0x219E3 + 15], bytes.fromhex("558bec8b46060560ff25f8ffa30814"))
            self.assertEqual(exe[0x219E3 + 0x1E:0x219E3 + 0x22], bytes.fromhex("3b06d714"))
            self.assertEqual(exe[0x219E3 + 0x54:0x219E3 + 0x58], bytes.fromhex("3b06dd14"))

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

    def test_start_forgets_shattered_lands_left_out(self):
        """What Shattered Lands' last start left out isn't said again after the sequel's start (it showed
        a SEGOBJEX warning that was Shattered Lands', 2026-11-26)."""
        launch.LEFT_OUT[:] = ["the new items, people and icons (SEGOBJEX.GFF: Shattered Lands')"]
        self.addCleanup(launch.LEFT_OUT.clear)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(launch.LaunchError):  # (no GOG DOSBox in it: the start stops there)
                launch._launch_wotr(d, {})
        self.assertIsNone(launch.left_out_line())


class JumpIntoSiteTests(unittest.TestCase):
    """A near jump from outside a patch must not land past a patch's first byte: there it runs the
    middle of the patch's INT and its site number (spell_hit's "immune" exit quit the game). The three
    such jumps of the game's are sent to the same epilogue elsewhere in their segment."""
    REDIRECTS = {  # name: (the patch the jump landed in, the epilogue's bytes)
        "window_fail": ("window", bytes.fromhex("5ec9cb")),
        "spell_hit_immune": ("spell_hit", bytes.fromhex("5f5ec9cb")),
        "thief_skill_armour_out": ("thief_skill_armour", bytes.fromhex("5f5ec9cb")),
    }

    @staticmethod
    def target(at: int, code: bytes) -> int:
        """The file offset a 3-byte "jmp rel16" at AT goes to."""
        assert code[0] == 0xE9
        return at + 3 + struct.unpack("<h", code[1:3])[0]

    def test_redirects(self):
        by_name = {p.name: p for p in ravager.PATCHES}
        for name, (site, epilogue) in self.REDIRECTS.items():
            p, s = by_name[name], by_name[site]
            old, new = self.target(p.offset, p.original), self.target(p.offset, p.replacement)
            self.assertTrue(s.offset < old < s.offset + len(s.replacement), name)  # (the jump's old place)
            self.assertEqual(s.original[old - s.offset:], epilogue[:s.offset + len(s.original) - old], name)
            self.assertLess(abs(new - p.offset), 0x800, name)  # (near: the same routine's segment)

    @unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
    def test_in_the_program(self):
        """Each redirect lands on its epilogue, left unpatched, and a scan of every "jmp rel16" of the
        patched program finds none from outside a patch landing in one past its first byte (a byte scan:
        calls and short jumps found the same way were all data or mid-instruction bytes, checked against
        a disassembly)."""
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        patched = gamepatch.patched(exe, patches=ravager.PATCHES, size=ravager.WOTR_SIZE)
        by_name = {p.name: p for p in ravager.PATCHES}
        covered, inside = set(), {}
        for p in ravager.PATCHES:
            covered.update(range(p.offset, p.offset + len(p.replacement)))
            for k in range(1, len(p.replacement)):
                if p.replacement[k:] != p.original[k:]:
                    inside[p.offset + k] = p.name
        for name, (_, epilogue) in self.REDIRECTS.items():
            new = self.target(by_name[name].offset, by_name[name].replacement)
            self.assertEqual(patched[new:new + len(epilogue)], epilogue, name)
            self.assertFalse(covered & set(range(new, new + len(epilogue))), name)
        found = []
        for m in re.finditer(rb"\xe9", patched[0x5200:]):
            at = 0x5200 + m.start()
            if not covered & {at, at + 1, at + 2} and self.target(at, patched[at:at + 3]) in inside:
                found.append(hex(at))
        self.assertEqual(found, [])
        # (and in the game's own program, the redirects' three jumps and no others)
        others = covered - {by_name[n].offset + k for n in self.REDIRECTS for k in range(3)}
        found = [hex(at) for at in (0x5200 + m.start() for m in re.finditer(rb"\xe9", exe[0x5200:]))
                 if self.target(at, exe[at:at + 3]) in inside and not others & {at, at + 1, at + 2}]
        self.assertEqual(sorted(found), sorted(hex(by_name[n].offset) for n in self.REDIRECTS))


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
        out, done = ravager.objects_fixed(data, {"weights"})
        got = gff.read_gff(out)
        self.assertEqual((done, len(got[("ALL ", 4)]) // 15, got[("ALL ", 5)]), (["mod_types"], 135, b"names"))
        self.assertEqual(got[("ALL ", 4)][102 * 15:103 * 15], ravager.wotr_type(npcitems.TYPES[0]))
        self.assertEqual(ravager.objects_fixed(data, {"mod_types", "weights"}), (data, []))
        with self.assertRaises(ravager.RavagerError):  # (a table whose weights aren't SSI's)
            ravager.objects_fixed(data)
        with self.assertRaises(ravager.RavagerError):
            ravager.objects_fixed(_gff({("ALL ", 4): bytes(15)}))


    @staticmethod
    def _ssi_table() -> bytes:
        """A type table with SSI's weights where RAV_WEIGHTS names them (the rest of each record its number)."""
        out = bytearray()
        for k in range(ravager.GAME_TYPES):
            rec = bytearray([k % 256] * ravager.TYPE_SIZE)
            rec[ravager.TYPE_WEIGHT] = ravager.RAV_WEIGHTS[k][0] if k in ravager.RAV_WEIGHTS else 0
            out += rec
        return bytes(out)

    def test_weights(self):
        """The Loader's weights in ALL 4's +2 (a long sword 40, the leather chest 96, the two-handed sword 150,
        SSI's 20 replaced), nothing else in the records changed, the types not named left; and every weight
        fits the sequel's byte (the mod's types too, through wotr_type)."""
        from test_ravtransfer import _gff
        table = self._ssi_table()
        got = gff.read_gff(ravager.objects_fixed(_gff({("ALL ", 4): table}), {"mod_types"})[0])[("ALL ", 4)]
        self.assertEqual(len(got), len(table))
        for k in range(ravager.GAME_TYPES):
            old, new = table[k * 15:(k + 1) * 15], got[k * 15:(k + 1) * 15]
            self.assertEqual(old[:2] + old[3:], new[:2] + new[3:])
            self.assertEqual(new[2], ravager.RAV_WEIGHTS[k][1] if k in ravager.RAV_WEIGHTS else old[2], k)
        self.assertEqual([got[k * 15 + 2] for k in (97, 32, 101, 0, 41)], [40, 96, 150, 0, 0])
        self.assertTrue(all(0 < w <= 255 for _, w in ravager.RAV_WEIGHTS.values()))
        self.assertTrue(all(k < ravager.GAME_TYPES for k in ravager.RAV_WEIGHTS))
        self.assertEqual(ravager.weighted_table(got), got)  # (already weighed: as it is)

    def test_weights_skipped_and_guarded(self):
        """RAV_SKIP=weights leaves SSI's bytes (the control's copy); a byte neither SSI's nor the Loader's
        stops the copy (not the GOG release's table)."""
        from test_ravtransfer import _gff
        table = self._ssi_table()
        data = _gff({("ALL ", 4): table})
        self.assertEqual(ravager.objects_fixed(data, {"mod_types", "weights"}), (data, []))
        odd = bytearray(table)
        odd[97 * 15 + 2] = 33
        with self.assertRaises(ravager.RavagerError):
            ravager.objects_fixed(_gff({("ALL ", 4): bytes(odd)}))

    def test_weights_in_objects(self):
        """Each object's copy of its type (RDFF kind 4, its number the type's) weighed as ALL 4 is; another
        record, a type past the sequel's or a copy that isn't SSI's left as it is."""
        from dsloader import dataitems
        from test_ravtransfer import _gff
        table = self._ssi_table()
        recs = [dataitems.Record(1, 0, 1, 7, 0, bytes(23)),
                dataitems.Record(3, 0, 4, 97, 5, table[97 * 15:98 * 15]),
                dataitems.Record(3, 0, 4, 101, 5, b"\x55" * 15),
                dataitems.Record(3, 0, 4, 110, 5, bytes(15))]
        chunk = dataitems.chunk(recs, dataitems.HEADER.pack(dataitems.END, 0, 0, 0, 0, 0))
        got = gff.read_gff(ravager.objects_fixed(_gff({("ALL ", 4): table, ("RDFF", 5): chunk}), {"mod_types"})[0])
        out, _ = dataitems.records(got[("RDFF", 5)])
        self.assertEqual([r.data for r in out], [bytes(23), ravager.weighted(table[97 * 15:98 * 15], 97),
                                                 b"\x55" * 15, bytes(15)])
        self.assertEqual(out[1].data[2], 40)

    def test_mod_kinds_in_dsclog2(self):
        """DSCLOG2's kind_of_type goes on past the sequel's 102 types with the mod's 33 (SL's 115-147 as
        mod_type numbers them), each SL's kind (specialize.KIND_OF_TYPE) + 1: its class restrictions,
        polearm reach and large dice take them in (KIND_TYPES)."""
        from dsloader import specialize
        asm = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        body = asm[asm.index("\nkind_of_type:") + 1:]
        rows = []
        for line in body.splitlines()[1:]:
            code = line.split(";")[0].strip()
            if not code:
                continue
            if not code.startswith("db "):
                break
            rows += [int(n) for n in code[3:].split(",")]
        self.assertEqual(len(rows), ravager.GAME_TYPES + ravager.MOD_TYPES)
        self.assertIn("KIND_TYPES  equ %d" % len(rows), asm)
        for sl in range(game.GAME_TYPES, game.GAME_TYPES + ravager.MOD_TYPES):
            self.assertEqual(rows[ravager.mod_type(sl)], specialize.KIND_OF_TYPE.get(sl, -1) + 1, sl)


class LayoutTests(unittest.TestCase):
    def test_fields_checked_in_memory(self):
        """The fields read from Gerakis's records in a running game (2026-11-19)."""
        self.assertEqual([ravager.creature_field(o) for o in (0, 2, 4, 6, 0x1A, 0x1B, 0x1C, 0x1D, 0x1F, 0x22, 0x28)],
                         [0, 2, 4, 6, 0x12, 0x13, 0x14, 0x15, 0x16, 0x19, 0x21])
        self.assertEqual([ravager.sheet_field(o) for o in (0, 8, 0x10, 0x12, 0x18, 0x21, 0x24, 0x37, 0x3F, 0x43, 0x45)],
                         [0, 8, 0x0E, 0x10, 0x12, 0x1B, 0x1E, 0x31, 0x39, 0x3D, 0x3F])
        for gone in (0x0E, 0x0F, 0x17, 0x3C):
            self.assertIsNone(ravager.sheet_field(gone))
        self.assertEqual([ravager.sheet_field(o) for o in (0x14, 0x15, 0x16)], [0x42, 0x43, 0x44])  # (the Loader's)

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
            from dsloader import kitpages, ravspells, rollstore, weaponpages
            objects = gff.read_gff(open(os.path.join(WOTR, ravager.OBJECTS_FILE), "rb").read())
            self.assertEqual(set(res.keys()), set(game.keys()) | set(kitpages.rav_chunks(game))  # (the kit pages,
                             | set(rollstore.rav_chunks(game))  # STORE and RECALL,
                             | set(weaponpages.rav_chunks(game, objects))  # the weapon window,
                             | set(ravspells.chunks(game))  # the new spells,
                             | {("ICON", icons.PICK_ICON)})  # the Pick Pockets button's purse)
            from dsloader import wotrart
            purse = wotrart.decode_plnr(res[("ICON", icons.PICK_ICON)])
            self.assertEqual(purse, icons.rav_pick_icon(wotrart.decode_plnr(game[("ICON", icons.TURN_EARTH_ICON)])))
            changed_spells = {k[1] for k in game if k[0] == "DATA" and game[k] != res[k]}  # (the index chunks grow: GFFI)
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
            mended = bytearray(ravager.ranged_table(ravager.weighted_table(own[ravager.TYPES_CHUNK])))  # (weighed, the double spear's range 1; the daggers the air clerics' too)
            for t in ravager.AIR_DAGGER_TYPES:
                mended[t * ravager.TYPE_SIZE + ravager.TYPE_CLASSES] |= ravager.AIR_CLERIC_BIT
            self.assertEqual(types[:len(own[ravager.TYPES_CHUNK])], bytes(mended))
            self.assertEqual(len(types), (ravager.GAME_TYPES + ravager.MOD_TYPES) * ravager.TYPE_SIZE)
            sheets = {k for k in own if k[0] == "RDFF" and any(
                r.kind == ravager.SHEET_KIND for r in dataitems.records(own[k])[0])}
            self.assertEqual(len(sheets), 352)  # (the monsters, each with a sheet: made 48h, zeros added)
            from dsloader import ravshine
            shine = {("BMP ", ravshine.icon_of(own, s.obj)) for s in ravshine.SHINE}  # (the still magic items' icons)
            weighed = ravager.weighted_objects(own, ranges=True)  # (the objects' copies of their types, weighed as ALL 4)
            self.assertTrue(weighed)
            self.assertEqual({k for k in own if own[k] != objs[k] and k[0] != "GFFI"},
                             {ravager.TYPES_CHUNK} | sheets | shine | set(weighed))  # (GFFI: the index)
            for k, chunk in weighed.items():  # (every copy of a type now ALL 4's record of it)
                for r in dataitems.records(objs[k])[0]:
                    if r.kind == ravager.TYPE_KIND_RECORD and r.number < ravager.GAME_TYPES:
                        self.assertEqual(r.data, types[r.number * 15:(r.number + 1) * 15], (k, r.number))
            for k in sheets:
                old, new = dataitems.records(weighed.get(k, own[k]))[0], dataitems.records(objs[k])[0]
                self.assertEqual([r._replace(data=r.data[:ravager.GAME_SHEET_SIZE]) for r in new], old)
                self.assertEqual({len(r.data) for r in new if r.kind == ravager.SHEET_KIND}, {ravager.SHEET_SIZE})
                self.assertFalse(any(any(r.data[ravager.GAME_SHEET_SIZE:]) for r in new))

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
