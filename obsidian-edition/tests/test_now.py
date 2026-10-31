"""THAC0 with each weapon and the saves as they stand now (the game's screens and the Loader's)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dicelog, game
from test_dicelog import CREATURES, DS, ITEM_TYPES, ITEMS, LOAD_SEG, SHEETS, make_game, set_effects

THINGS = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF


def dag():
    """Dag (THAC0 16, STR 24, DEX 16, CON 21): a metal long sword +1 in his right hand (item 5)
    and a wooden bow (item 6, type 11) ready as his missile weapon; saves 13 14 12 15 16."""
    log = make_game()
    m = log.guest.mem
    rec = CREATURES
    m[rec + game.CREATURE_ABILITIES:rec + game.CREATURE_ABILITIES + 3] = bytes((24, 16, 21))
    struct.pack_into("<hhh", m, rec + 8, 40, game.NO_ITEM, game.NO_ITEM)
    struct.pack_into("<Bh", m, THINGS + 40 * 3, game.THING_ITEM, 5)
    struct.pack_into("<h", m, ITEMS + 5 * game.ITEM_SIZE + game.ITEM_NEXT, 6)
    struct.pack_into("<h", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_NEXT, game.NO_ITEM)
    struct.pack_into("<H", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_TYPE, 11)
    m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = game.WEAPON_HANDS[0]
    m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = game.MISSILE_SLOT
    bow = ITEM_TYPES + 11 * game.ITEM_TYPE_SIZE
    m[bow + 0x08], m[bow + 0x0C], m[bow + 0x0D] = 0, 6, 1  # wooden, 1d6
    ds = DS * 16
    m[ds + game.STR_TO_HIT + 24], m[ds + game.DEX_MISSILE + 16] = 6, 1
    m[ds + game.SAVE_CON + 21] = 2
    m[SHEETS + game.SHEET_SAVES:SHEETS + game.SHEET_SAVES + 5] = bytes((13, 14, 12, 15, 16))
    return log


class HitTests(unittest.TestCase):
    def test_each_weapon(self):
        g = dag().game
        self.assertEqual([(h.item, h.thac0, h.parts) for h in g.weapon_hits(0)], [
            (5, 9, [("STR", 6), ("weapon", 1)]),  # 16 - 6 - 1
            (6, 18, [("DEX", 1), ("wooden", -3)])])  # 16 - 1 + 3

    def test_blessed_and_cursed(self):
        log = dag()
        set_effects(log, [(0, 0, 7)])
        self.assertEqual(log.game.weapon_hits(0)[0].thac0, 8)
        set_effects(log, [(0, 0, 7), (0, 0, 12)])  # +1, -1
        self.assertEqual(log.game.weapon_hits(0)[0].thac0, 9)

    def test_hasted_and_slowed(self):
        """Hasted: each weapon's attacks a round twice; Slowed: half, rounded down (the game's
        attack, after the rest: 5883Ah). Dag's long sword 3/2 (the sheet's), his bow 1 (its own)."""
        log = dag()
        g = log.game
        log.guest.mem[SHEETS + game.SHEET_ATTACKS] = 3
        log.guest.mem[ITEM_TYPES + 11 * game.ITEM_TYPE_SIZE + 0x0B] = 2
        self.assertEqual([h.halves for h in g.weapon_hits(0)], [None, 2])
        set_effects(log, [(0, 0, game.HASTED_EFFECT)])
        self.assertEqual([h.halves for h in g.weapon_hits(0)], [6, 4])
        set_effects(log, [(0, 0, game.SLOWED_EFFECT)])
        self.assertEqual([h.halves for h in g.weapon_hits(0)], [1, 1])
        set_effects(log, [(1, 1, game.HASTED_EFFECT)])  # (someone else's)
        self.assertEqual([h.halves for h in g.weapon_hits(0)], [None, 2])

    def test_to_hit_effects(self):
        """Dag's THAC0 with his long sword (9: +6 STR, +1 weapon) under each effect the game's
        attack counts (HIT_EFFECTS, Prayer by its caster's side), named in the breakdown; another
        creature's effects change nothing."""
        log = dag()
        g = log.game
        for effects, thac0, part in (
                ([], 9, None),
                ([(0, 0, 7)], 8, ("Blessed", 1)),
                ([(0, 0, 12)], 10, ("Cursed", -1)),
                ([(0, 0, 7), (0, 0, 12)], 9, ("Cursed", -1)),
                ([(0, 0, game.SLOWED_EFFECT)], 13, ("Slowed", -4)),
                ([(0, 0, 49)], 8, ("Graft Weapon", 1)),
                ([(0, 0, game.FOG_EFFECT)], 12, ("Fogbolt", -3)),
                ([(0, 0, game.EFFECT_PRAYER)], 8, ("Prayer", 1)),  # (his own side's)
                ([(0, 0x29, game.EFFECT_PRAYER)], 10, ("Prayer", -1)),  # (the Mountain Stalker's)
                ([(1, 1, 7), (1, 1, 12)], 9, None)):  # (on someone else)
            with self.subTest(effects=effects):
                set_effects(log, effects)
                sword = g.weapon_hits(0)[0]
                self.assertEqual(sword.thac0, thac0)
                if part:
                    self.assertIn(part, sword.parts)
                else:
                    self.assertEqual(sword.parts, [("STR", 6), ("weapon", 1)])
        set_effects(log, [(0, 0, 7)])
        self.assertEqual([h.thac0 for h in g.weapon_hits(0)], [8, 17])  # (the bow too)
        self.assertEqual(log.stats_entry(0)[1], 8)  # (the game's screens show it)

    def test_kratcheks_chatkcha_with_specialization(self):
        """K'ratchek (the game's own thri-kreen) throws her chatkcha once more a round, weapon
        specialization on or off (its item type is not the weapon's kind)."""
        from dsloader import kits
        log = dag()
        g = log.game
        m = log.guest.mem
        struct.pack_into("<H", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_TYPE, 48)  # (a chatkcha)
        chatkcha = ITEM_TYPES + 48 * game.ITEM_TYPE_SIZE
        m[chatkcha + 0x0B], m[chatkcha], m[chatkcha + 0x0C], m[chatkcha + 0x0D] = 2, 2, 6, 1  # (1d6)
        m[SHEETS + game.SHEET_RACE] = kits.THRI_KREEN
        for rules in (game.RULE_KITS, game.RULE_KITS | game.RULE_SPECIALIZE):
            with self.subTest(rules=rules):
                g.rules = rules
                m[SHEETS + 0x43] = 0
                plain = g.weapon_hits(0)[-1].halves
                m[SHEETS + 0x43] = kits.OWN_BIT
                self.assertEqual(g.weapon_hits(0)[-1].halves, (plain or 2) + kits.OWN_THROWS_MORE)

    def test_two_weapon_rule_needs_two_weapons(self):
        """Dag's long sword and his bow (the missile slot): one melee weapon, so no penalty with
        the AD&D rule on; a second melee weapon in the left hand brings -2 and -4; a ranger never."""
        g = dag().game
        g.rules = game.RULE_TWO_WEAPONS
        m = g.guest.mem
        self.assertEqual([h.parts for h in g.weapon_hits(0)][0], [("STR", 6), ("weapon", 1)])
        m[ITEM_TYPES + 11 * game.ITEM_TYPE_SIZE + 0x0A] = 1  # the bow's type as a melee weapon...
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 10  # ... in the left hand
        m[ITEM_TYPES + 10 * game.ITEM_TYPE_SIZE + 0x0A] = 1
        m[ITEM_TYPES + 9 * game.ITEM_TYPE_SIZE + 0x0A] = 1
        dex = g.creature(0)[game.CREATURE_ABILITIES + 1]
        parts = {h.slot: h.parts[-1] for h in g.weapon_hits(0)}
        self.assertEqual(parts[3], (f"two weapons, main hand at DEX {dex}", -2 + g.dex_initiative(dex)))
        self.assertEqual(parts[10][1], min(0, -4 + g.dex_initiative(dex)))
        struct.pack_into("<H", m, SHEETS + game.SHEET_FLAGS, game.SHEET_FLAG_RANGER)
        self.assertFalse(any("two weapons" in why for h in g.weapon_hits(0) for why, _ in h.parts))

    def test_unarmed(self):
        log = dag()
        struct.pack_into("<h", log.guest.mem, CREATURES + 8, game.NO_ITEM)
        self.assertEqual([(h.item, h.name, h.thac0) for h in log.game.weapon_hits(0)], [(-1, "unarmed", 10)])

    def test_unarmed_kits(self):
        """The kits' to-hit unarmed too, as DSCLOG's KIT_TO_HIT and WILD_TO_HIT: a Poisoner's none, a
        Ghetto Fighter's -1 (no dagger), a Wild Fury's -3 with its check failed (none when passed)."""
        from dsloader import kits
        log = dag()
        struct.pack_into("<h", log.guest.mem, CREATURES + 8, game.NO_ITEM)
        g = log.game
        for kid, wild, thac0 in ((kits.POISONER, None, 10), (kits.GHETTO, None, 11),
                                 (kits.WILD_FURY, False, 13), (kits.WILD_FURY, True, 10)):
            g.kit_ids = lambda creature, kid=kid: [kid]
            g.wild = {} if wild is None else {0: wild}
            self.assertEqual([(h.name, h.thac0) for h in g.weapon_hits(0)], [("unarmed", thac0)], kits.name(kid))


class StrengthDamageTests(unittest.TestCase):
    def test_the_games_table(self):
        g = dag().game
        m, ds = g.guest.mem, DS * 16
        table = [game.STR_DAMAGE.get(n, 0) for n in range(1, 26)]
        table[17] = 5  # (STR 18, as the game's table might have it)
        m[ds + game.STR_DAMAGE_TABLE + 1:ds + game.STR_DAMAGE_TABLE + 26] = struct.pack("25b", *table)
        self.assertEqual((g.str_damage(18), g.str_damage(1), g.str_damage(24)), (5, -4, 12))

    def test_unread_table(self):  # (not the game's: the AD&D table, STR 18 as the game has it)
        g = dag().game
        self.assertEqual((g.str_damage(17), g.str_damage(18), g.str_damage(10)), (1, 4, 0))


class SaveTests(unittest.TestCase):
    def test_con_on_paralysis_poison_death(self):
        """Dag, a half-giant: CON 21 is +2 on his first save only."""
        self.assertEqual([s.needs for s in dag().game.saves_now(0)], [11, 14, 12, 15, 16])

    def test_blessed_and_spirit_armor(self):
        log = dag()
        set_effects(log, [(0, 0, 7), (0, 0, game.EFFECT_SPIRIT_ARMOR)])
        saves = log.game.saves_now(0)
        self.assertEqual([s.needs for s in saves], [10, 10, 8, 11, 12])  # Spirit Armor: not the first
        self.assertEqual(saves[0].parts, [(1, "Blessed"), (2, "CON 21")])

    def test_never_below_2(self):
        log = dag()
        log.guest.mem[SHEETS + game.SHEET_SAVES] = 3
        self.assertEqual(log.game.saves_now(0)[0].needs, 2)  # a 1 always fails


class RuleTests(unittest.TestCase):
    def test_boots(self):
        log = dag()
        self.assertFalse(log.game.wears_boots(0))
        log.guest.mem[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 12  # the cloak's
        self.assertFalse(log.game.wears_boots(0))
        log.guest.mem[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 13  # the feet, as the inventory screen shows
        self.assertTrue(log.game.wears_boots(0))

    def test_rules_for_dsclog(self):
        log = dag()
        log.set_rules(dicelog.RULE_HELMS | game.RULE_TWO_WEAPONS)
        self.assertEqual(struct.unpack_from("<H", log.guest.mem, log.tsr_hdr + dicelog.TSR_RULES)[0], 5)


class ThiefTests(unittest.TestCase):
    def setUp(self):
        """Dag as a 4th level thief (DEX 16), his long sword in his right hand; the game's tables
        made simple: open locks 18 and +5 for DEX 16, the other skills 0; an equipment penalty
        of 5 on picking pockets and 10 on climbing."""
        self.log = log = dag()
        m = log.guest.mem
        table = (LOAD_SEG + game.THIEF_TABLE_SEG) * 16
        for skill in range(8):
            m[table + game.THIEF_DEX_HIGH + skill] = m[table + game.THIEF_DEX_TOP + skill] = 25
        m[table + game.THIEF_BASE + 1] = 18
        m[table + game.THIEF_DEX_LOW + 1], m[table + game.THIEF_DEX_HIGH + 1], m[table + game.THIEF_DEX_TOP + 1] = 11, 15, 20
        m[table + game.THIEF_ARMOUR + 0], m[table + game.THIEF_ARMOUR + 6] = 5, 10
        m[SHEETS + game.SHEET_CLASSES + 1], m[SHEETS + game.SHEET_LEVELS + 1] = game.THIEF, 4
        m[CREATURES + game.CREATURE_STATUS] = game.STATUS_OKAY

    def now(self):
        return [n for _, n in self.log.game.thief_skills_now(0)]

    def test_equipment(self):
        self.assertEqual(self.now(), [11, 39, 16, 16, 16, 6])  # move silently 4th
        self.log.guest.mem[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = 0xFF  # put away
        self.log.guest.mem[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 0xFF
        self.assertEqual(self.now(), [16, 39, 16, 16, 16, 16])

    def test_new_counts_as_okay(self):
        """A character not yet played (New) has its skills as when Okay; one Out Cold has 0."""
        m = self.log.guest.mem
        m[CREATURES + game.CREATURE_STATUS] = game.STATUS_NEW
        self.assertEqual(self.now(), [11, 39, 16, 16, 16, 6])
        m[CREATURES + game.CREATURE_STATUS] = game.OUT_COLD
        self.assertEqual(self.now(), [0] * 6)

    def test_belt(self):
        """A worn belt (the waist slot) adds BELT_BONUS to picking pockets and opening locks, with
        its switch on (BELT_IN_FORCE); nothing else, and nothing carried in the pack."""
        m, gd = self.log.guest.mem, self.log.game
        m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = 0xFF  # (no equipment penalty)
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = game.WAIST
        plain = [16, 39, 16, 16, 16, 16]
        gd.belt = False
        self.assertEqual(self.now(), plain)
        gd.belt = True
        self.assertEqual(self.now(), [21, 44, 16, 16, 16, 16])
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 20  # (in the pack)
        self.assertEqual(self.now(), plain)

    def test_cloak_and_boots(self):
        """With the stealth rule and the cloak, boots and belt switch: a worn cloak adds 10 to hiding
        in shadows, boots 10 to moving silently (no more than 95); the Cloak and Boots of Elvenkind
        their 95. Without the rule or the switch, nothing; nor for the rolls' own chance (gear=False)."""
        m, gd = self.log.guest.mem, self.log.game
        m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = game.CLOAK_SLOT  # (no equipment penalty)
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = game.FOOT
        plain = [16, 39, 16, 16, 16, 16]
        gd.belt, gd.rules = True, game.RULE_STEALTH
        skills = lambda **kw: [n for _, n in gd.thief_skills_now(0, game.PANEL_SKILLS, **kw)]
        self.assertEqual(skills(), [16, 39, 16, 26, 26, 16])  # (pick, lock, traps, move, hide, climb)
        self.assertEqual(skills(gear=False), plain)
        gd.belt = False
        self.assertEqual(skills(), plain)
        gd.belt, gd.rules = True, 0
        self.assertEqual(skills(), plain)
        gd.rules = game.RULE_STEALTH
        struct.pack_into("<H", m, ITEMS + 5 * game.ITEM_SIZE + game.ITEM_TYPE, game.ELVEN_CLOAK_TYPE)
        struct.pack_into("<H", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_TYPE, game.ELVEN_BOOTS_TYPE)
        self.assertEqual(skills(), [16, 39, 16, 95, 95, 16])

    def test_a_rangers_cloak_and_boots(self):
        """A ranger's move silently and hide in shadows in the panel count a worn cloak and boots."""
        m = self.log.guest.mem
        m[SHEETS + game.SHEET_CLASSES + 1], m[SHEETS + game.SHEET_LEVELS + 1] = 13, 10
        m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = game.CLOAK_SLOT
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = game.FOOT
        self.log.game.belt = True
        self.log.rules = self.log.game.rules = game.RULE_STEALTH
        self.assertEqual(list(self.log.stats_entry(0)[17:24]), [dicelog.STATS_RANGER, 0, 0, 0, 88, 73, 0])
        self.assertEqual(self.log.game.ranger_skill_now(0, 4, gear=False), 63)

    def test_panel_shows_a_rangers(self):
        """A ranger (10th, no thief levels) with the stealth rule: move silently and hide in
        shadows in a thief's places (AD&D's 78 and 63), the rest 0; nothing without the rule."""
        self.log.guest.mem[SHEETS + game.SHEET_CLASSES + 1] = 13
        self.log.guest.mem[SHEETS + game.SHEET_LEVELS + 1] = 10
        self.log.rules = game.RULE_STEALTH
        entry = self.log.stats_entry(0)
        self.assertEqual(list(entry[17:24]), [dicelog.STATS_RANGER, 0, 0, 0, 78, 63, 0])
        self.log.rules = 0
        self.assertEqual(list(self.log.stats_entry(0)[17:24]), [0] * 7)

    def test_penalty_slots_from_the_game(self):
        """The slots come from the game's list in memory: the game's own (the sword in Dag's
        right hand counts) or the dice log's copy (empty: nothing does)."""
        m = self.log.guest.mem
        at = (LOAD_SEG + game.THIEF_TABLE_SEG) * 16 + game.THIEF_PENALTY_LIST
        m[at:at + 10] = struct.pack("<5H", 6, 1, 10, 3, 13)
        self.assertEqual(self.log.game.thief_penalty_slots(), (6, 1, 10, 3))
        self.assertEqual(self.now(), [11, 39, 16, 16, 16, 6])
        m[at:at + 10] = struct.pack("<5H", 13, 13, 13, 13, 13)
        self.assertEqual(self.log.game.thief_penalty_slots(), ())
        self.assertEqual(self.now(), [16, 39, 16, 16, 16, 16])

    def test_ad_d_table(self):
        """With RULE_THIEF_TABLE: AD&D's average for the level (4th here) and Dark Sun's DEX
        adjustment (17: +5 pick, +10 open, +5 move and hide), the race's as the game's."""
        m = self.log.guest.mem
        m[CREATURES + game.CREATURE_ABILITIES + 1] = 17
        self.log.game.rules = game.RULE_THIEF_TABLE
        total = lambda skill: sum(n for _, n in self.log.game.thief_skill_parts(0, skill))
        self.assertEqual([total(s) for s in range(8)], [50, 47, 35, 38, 30, 15, 88, 20])
        self.assertEqual(self.log.game.thief_skill_parts(0, 0), [("thief level 4", 45), ("DEX 17", 5)])
        self.log.game.rules = 0
        self.assertEqual(self.log.game.thief_skill_parts(0, 0)[0], ("base", 0))

    def test_ad_d_table_most(self):
        """With RULE_THIEF_TABLE no skill comes out above AD&D's 95 (a 13th level thief with DEX 22:
        pick pockets 99 + 27, move silently 99 + 30, climbing 99); without it, the game's sum."""
        m = self.log.guest.mem
        m[SHEETS + game.SHEET_LEVELS + 1], m[CREATURES + game.CREATURE_ABILITIES + 1] = 13, 22
        m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = 0xFF  # (no equipment penalty)
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 0xFF
        self.log.game.rules = game.RULE_THIEF_TABLE
        self.assertEqual(self.now(), [95, 95, 95, 95, 40, 95])
        self.assertEqual(sum(n for _, n in self.log.game.thief_skill_parts(0, 3)), 129)
        self.log.game.rules = 0
        self.assertGreater(max(self.now()), 95)

    def test_dex_adjustment(self):
        self.assertEqual([game.dex_adjustment(d, 3) for d in (5, 9, 12, 16, 18, 22, 24)], [-20, -20, -5, 0, 10, 30, 30])
        self.assertEqual(game.dex_adjustment(22, 6), 0)  # climb walls: none

    def test_panel_shows_hiding(self):
        """The inventory screen's six (DSCLOG's STATS): hide in shadows in hear noise's place."""
        self.log.guest.mem[(LOAD_SEG + game.THIEF_TABLE_SEG) * 16 + game.THIEF_BASE + 4] = 7  # hide 7 + 16
        entry = self.log.stats_entry(0)
        self.assertEqual(list(entry[17:24]), [1, 11, 39, 16, 16, 23, 6])

    def test_effects(self):
        set_effects(self.log, [(0, 0, 47)])  # Slowed: all but picking pockets
        self.assertEqual(self.now(), [11, 0, 0, 0, 0, 0])
        set_effects(self.log, [(0, 0, 14)])  # Detect Traps
        self.assertEqual(self.now()[2], 100)

    def test_in_stats(self):
        self.assertEqual(struct.unpack_from("<B6B", self.log.stats_entry(0), 17), (1, 11, 39, 16, 16, 16, 6))


class SettingsTests(unittest.TestCase):

    def test_every_rule_has_its_box(self):
        """Each of game.RULE_SETTINGS has a box with its text on the Options tab (viewer.py's
        list, read without Tk), and each its own bit."""
        import re
        with open(os.path.join(os.path.dirname(game.__file__), "viewer.py"), encoding="utf-8") as f:
            source = f.read()
        for key, _ in game.RULE_SETTINGS:
            self.assertRegex(source, r'\(\s*"' + re.escape(key) + r'",\s*(?:None|"\w+"),\s*"', key)  # (its group, then its text)
        bits = [bit for _, bit in game.RULE_SETTINGS]
        self.assertEqual(len(set(bits)), len(bits))
    def test_saved_options(self):
        log = dag()
        log.use_settings({"helm_ac": False, "new_items": False, "arena_ring": True, "no_doubled_save": False})
        self.assertEqual((log.rules, log.arena_ring, log.monster_info),
                         (game.RULE_TWO_WEAPONS | game.RULE_SPELL_SAVE | game.RULE_NEW_SPELLS
                          | game.RULE_STEALTH | game.RULE_LEVEL_10 | game.RULE_THIEF_TABLE
                          | game.RULE_HALF_GIANT | game.RULE_PROTECTION | game.RULE_ITEM_SAVES
                          | game.RULE_SPECIALIZE | game.RULE_RESTRICT | game.RULE_MULTI_HP | game.RULE_HP_BEST
                          | game.RULE_KITS | game.RULE_RANGER_CAST | game.RULE_INT_LEARN | game.RULE_ADND_TABLES | game.RULE_CHA_PRICES
                          | game.RULE_ROLLED | game.RULE_BUYBACK | game.RULE_BACKSTAB | game.RULE_AGING
                          | game.RULE_ENLARGE | game.RULE_CON, False, True))


class SpeakerTests(unittest.TestCase):
    def test_announcer_not_relearned(self):
        """A name learned for the Announcer mid-fight (from a Slig) doesn't stick."""
        log = dag()
        log.learned_speakers = {119: "Slig"}
        self.assertEqual(log.speaker(119), "The Announcer")


class StatsTests(unittest.TestCase):
    def test_entry_for_dsclog(self):
        log = dag()
        entry = log.stats_entry(0)
        self.assertEqual(len(entry), dicelog.STATS_SIZE)
        self.assertEqual(struct.unpack_from("<Bb5B", entry), (1, 9, 11, 14, 12, 15, 16))
        self.assertEqual(struct.unpack_from("<3H3b", entry, 8), (5, 6, game.NO_ITEM, 9, 18, 0))

    def test_empty_slot(self):
        self.assertEqual(dag().stats_entry(3), bytes(dicelog.STATS_SIZE))

    def test_enlarge_level(self):
        """The Effects screen's ENLARGED (+90% DAMAGE): the level of the Enlarge on a member, at its
        caster's level, in the last byte (DSCLOG's STATS_ENLARGE); none on someone else's."""
        log = dag()
        g = log.game
        self.assertEqual(log.stats_entry(0)[24], 0)
        g.effect_spells = lambda: [(game.Effect(0, 5, game.ENLARGE_EFFECT), 5),
                                   (game.Effect(1, 5, game.ENLARGE_EFFECT), 5)]
        creature_of = g.combatant_creature
        g.combatant_creature = lambda combatant: 2 if combatant == 5 else creature_of(combatant)
        g.effect_caster_level = lambda creature, spell: {2: 9}[creature]
        self.assertEqual(g.enlarge_level(0), 9)
        self.assertEqual(log.stats_entry(0)[24], 9)
        g.effect_spells = lambda: [(game.Effect(1, 5, game.ENLARGE_EFFECT), 5)]
        self.assertEqual(log.stats_entry(0)[24], 0)

    def test_armour_spells_ac(self):
        """The Effects screen's BARKSKIN (AC 4): the AC each armour spell on a member gives, as the
        game's AC routine (7C557h) has it from the effect's level (81B16h's: a spell's caster level,
        a psionic power's psionicist level), in bytes 25-27 (DSCLOG's STATS_ARMOUR; -128 none)."""
        log = dag()
        g = log.game
        self.assertEqual(struct.unpack_from("<3b", log.stats_entry(0), 25), (-128, -128, -128))
        g.effect_spells = lambda: [(game.Effect(0, 5, game.EFFECT_BARKSKIN), 81),
                                   (game.Effect(0, 5, game.EFFECT_FLESH_ARMOR), 154),
                                   (game.Effect(0, 5, game.EFFECT_VESTMENTS), 99)]
        creature_of = g.combatant_creature
        g.combatant_creature = lambda combatant: 2 if combatant == 5 else creature_of(combatant)
        g.effect_caster_level = lambda creature, spell: {81: 9, 99: 11}.get(spell)  # (None: a power)
        g.class_level = lambda creature, cls: 7 if cls == game.PSIONICIST else 0
        self.assertEqual(g.armour_spells_ac(0), {game.EFFECT_BARKSKIN: 4,  # 6 - 9 // 4
                                                 game.EFFECT_FLESH_ARMOR: 3,  # 10 - 7
                                                 game.EFFECT_VESTMENTS: 3})  # 5 - (11 - 5) // 3
        self.assertEqual(struct.unpack_from("<3b", log.stats_entry(0), 25), (4, 3, 3))
        g.effect_caster_level = lambda creature, spell: 4
        self.assertEqual(g.armour_spells_ac(0)[game.EFFECT_VESTMENTS], 5)  # (none better below 6th)


if __name__ == "__main__":
    unittest.main()
