"""The chance to hit shown before the swing (hitchance.py): what the d20 must show for the one
whose turn it is to hit the enemy chosen with Tab, on the dice log's "Chosen with Tab" line and in
the combat log's header."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import combatlog, dicelog, game, hitchance, kits, launch, stealth, targeting
from test_combatlog import FakeFont
from test_dicelog import CREATURES, DS, HDR, ITEM_TYPES, ITEMS, KIND_AC, LOAD_SEG, SHEETS, STALKER, entry, set_effects, words
from test_now import THINGS, dag

FOE = 0x29  # the stalker's combatant
SWORD, BOW = 9, 11  # Dag's weapons' types (test_now.dag: item 5 in his right hand, item 6 his missile weapon)
FACING = (LOAD_SEG + game.INITIATIVE_SEG) * 16 + game.FACING_OFF + STALKER


def fight(near=True, facing=None):
    """Dag (THAC0 9 with his long sword +1, 18 with his bow) and the Mountain Stalker (base AC 4,
    DEX 16: AC 2, 4 from behind), Dag in the square west of it or five squares west; the stalker
    facing nowhere, or FACING."""
    log = dag()
    m = log.guest.mem
    m[SHEETS + STALKER * game.SHEET_SIZE + game.SHEET_BASE_AC] = 4
    m[ITEM_TYPES + SWORD * game.ITEM_TYPE_SIZE + 0x0A] = 1
    m[ITEM_TYPES + BOW * game.ITEM_TYPE_SIZE + 0x0A] = 12
    struct.pack_into("<3h", m, CREATURES + STALKER * game.CREATURE_SIZE + game.CREATURE_ITEM_LISTS[0], *[game.NO_ITEM] * 3)
    place(log, 0, 10 if near else 6, 10)
    place(log, FOE, 11, 10)
    m[FACING] = 0xFF if facing is None else facing
    struct.pack_into("<H", m, DS * 16 + hitchance.EIGHT_WAYS, 1)
    return log


def place(log, combatant, x, y):
    at = DS * 16 + stealth.POSITIONS + combatant * stealth.POSITION_SIZE
    struct.pack_into("<HH", log.guest.mem, at, x * 16 + 8, y * 16 + 8)


def wear(log, creature, thing, item, item_type, slot, plus=0, type_ac=0, flags=0):
    """ITEM of ITEM_TYPE (counting for AC, TYPE_AC) worn by CREATURE in SLOT, alone in its worn list."""
    m = log.guest.mem
    struct.pack_into("<Bh", m, THINGS + thing * 3, game.THING_ITEM, item)
    at = ITEMS + item * game.ITEM_SIZE
    struct.pack_into("<H", m, at + game.ITEM_TYPE, item_type)
    struct.pack_into("<h", m, at + game.ITEM_NEXT, game.NO_ITEM)
    m[at + game.ITEM_SLOT], m[at + game.ITEM_PLUS] = slot, plus
    typ = ITEM_TYPES + item_type * game.ITEM_TYPE_SIZE
    m[typ], m[typ + 0x0F], m[typ + 0x12] = flags, 0x80, type_ac
    struct.pack_into("<h", m, CREATURES + creature * game.CREATURE_SIZE + game.CREATURE_ITEM_LISTS[0], thing)


def needs(log, **more):
    return [(s.weapon, s.need, s.how, s.behind, s.behind_how) for s in hitchance.predict(log.game, 0, FOE, **more)]


class PredictTests(unittest.TestCase):
    def test_next_to_it_the_melee_weapon(self):
        """Next to the target: the weapon in hand only, THAC0 9 against AC 2."""
        log = fight()
        self.assertEqual(needs(log), [("Metal Long Sword +1", 7, "", None, "")])
        swing, = hitchance.predict(log.game, 0, FOE)
        self.assertEqual((swing.thac0, swing.ac, swing.missile), (9, 2, False))
        self.assertEqual(hitchance.line([swing]), "needs 7+ (70%)")
        self.assertEqual(hitchance.brief([swing]), "Needs 7+ (70%)")

    def test_farther_off_the_shot_too(self):
        """Five squares off: the sword (Enter walks up) and the bow (the attack pointer shoots), each
        named; a bow whose range doesn't reach is left out."""
        log = fight(near=False)
        swings = hitchance.predict(log.game, 0, FOE)
        self.assertEqual([(s.missile, s.need) for s in swings], [(False, 7), (True, 16)])
        self.assertEqual(hitchance.line(swings),
                         f"{swings[0].weapon} needs 7+ (70%); {swings[1].weapon} needs 16+ (25%)")
        self.assertEqual(hitchance.brief(swings), "Needs 7+ (70%)")  # (the header: what Enter does)
        log.guest.mem[ITEM_TYPES + BOW * game.ITEM_TYPE_SIZE + 0x0A] = 3
        self.assertEqual([s.missile for s in hitchance.predict(log.game, 0, FOE)], [False])

    def test_only_a_bow_fights_with_fists(self):
        """A bow alone: hand to hand it is unarmed (the game's picker finds no weapon of range 1)."""
        log = fight()
        m = log.guest.mem
        struct.pack_into("<Bh", m, THINGS + 40 * 3, game.THING_ITEM, 6)  # (the bow the first of his items)
        self.assertEqual([h.name for h in log.game.weapon_hits(0)], [log.game.weapon_hits(0)[0].name])
        self.assertEqual([h.item for h in log.game.weapon_hits(0, unarmed=True)], [6, -1])
        self.assertEqual(needs(log), [("unarmed", 8, "", None, "")])  # 16 - 6 STR against AC 2

    def test_facing_nowhere_never_from_behind(self):
        """A target facing nowhere yet (the round's start) turns to its first attacker: in front."""
        log = fight(near=False)
        self.assertEqual(needs(log)[0][3], None)

    def test_farther_off_both_numbers(self):
        """The target facing a way already and the attacker still to walk up: the number as it
        stands, and from behind (2 better, no DEX: AC 4) as the other; never for the shot
        (DSCLOG's MISSILE_REAR)."""
        log = fight(near=False, facing=2)
        melee, shot = needs(log)
        self.assertEqual(melee[1:], (7, "", 3, "from behind"))
        self.assertEqual(shot[1:], (16, "", None, ""))
        swings = hitchance.predict(log.game, 0, FOE)
        self.assertEqual(hitchance.line(swings[:1]), "needs 7+ (70%), from behind 3+ (90%)")
        self.assertEqual(hitchance.brief(swings), "7+ 70%, behind 3+")

    def test_next_to_it_behind_or_not(self):
        """Next to it the answer is known: Dag is west of the stalker, behind it when it faces
        east (its attacker was there), in front any other way."""
        log = fight(facing=hitchance.WAYS[(1, 0)])
        self.assertEqual(needs(log), [("Metal Long Sword +1", 3, "from behind", None, "")])
        swings = hitchance.predict(log.game, 0, FOE)
        self.assertEqual((swings[0].thac0, swings[0].ac), (7, 4))
        self.assertEqual(hitchance.line(swings), "needs 3+ (90%) from behind")
        self.assertEqual(hitchance.brief(swings), "Behind: 3+ (90%)")
        for way in set(hitchance.WAYS.values()) - {hitchance.WAYS[(1, 0)]}:
            log.guest.mem[FACING] = way
            self.assertEqual(needs(log)[0][1:3], (7, ""), way)

    def test_the_way(self):
        """The game's direction from the target to the attacker (0EB5Bh): by the signs of the
        squares' difference, 0 north and on clockwise; with its four directions, the nearer of
        north, east, south and west."""
        log = fight()
        for (x, y), way in (((11, 9), 0), ((12, 9), 1), ((12, 10), 2), ((12, 11), 3), ((11, 11), 4), ((10, 11), 5),
                            ((10, 10), 6), ((10, 9), 7), ((11, 2), 0), ((20, 9), 1), ((3, 10), 6), ((3, 11), 5)):
            place(log, 0, x, y)
            self.assertEqual(hitchance.way(log.game, FOE, 0), way, (x, y))
        struct.pack_into("<H", log.guest.mem, DS * 16 + hitchance.EIGHT_WAYS, 0)
        for (x, y), way in (((11, 9), 0), ((12, 9), 2), ((12, 10), 2), ((11, 11), 4), ((10, 11), 6), ((9, 12), 6),
                            ((10, 13), 4), ((10, 7), 0)):
            place(log, 0, x, y)
            self.assertEqual(hitchance.way(log.game, FOE, 0), way, (x, y))

    def test_a_shield_doesnt_count_from_behind(self):
        """From behind the target's shield isn't counted (the AC routine, 58ED5h)."""
        log = fight(facing=hitchance.WAYS[(1, 0)])
        wear(log, STALKER, 60, 30, 40, game.WEAPON_HANDS[1], plus=1, type_ac=1, flags=game.TYPE_SHIELD)
        self.assertEqual(needs(log)[0][1], 3)
        log.guest.mem[FACING] = 0xFF
        self.assertEqual(needs(log)[0][1], 9)  # (AC 2, the shield 1 and its +1: 0)

    def test_hidden_thief_backstabs(self):
        """Hidden in shadows: from behind whatever the facing; a thief with a light weapon
        backstabs (2 more); a Military Scout doesn't, a Rescuer's from behind is 1; a Girdle of
        Back Defense on the target takes it all back."""
        log = fight()
        self.assertEqual(needs(log, hidden=True)[0][1:3], (3, "from behind"))
        m = log.guest.mem
        struct.pack_into("<H", m, SHEETS + game.SHEET_FLAGS, hitchance.THIEF_FLAG)
        struct.pack_into("<H", m, ITEM_TYPES + SWORD * game.ITEM_TYPE_SIZE + 4, 40)
        self.assertEqual(needs(log, hidden=True)[0][1:3], (1, "a backstab"))
        self.assertEqual(hitchance.brief(hitchance.predict(log.game, 0, FOE, hidden=True)), "Backstab: 2+ 95%")
        self.assertEqual(hitchance.line(hitchance.predict(log.game, 0, FOE, hidden=True)),
                         "hits on anything but a 1 (95%) a backstab")
        struct.pack_into("<H", m, ITEM_TYPES + SWORD * game.ITEM_TYPE_SIZE + 4, 41)  # (too heavy)
        self.assertEqual(needs(log, hidden=True)[0][1:3], (3, "from behind"))
        struct.pack_into("<H", m, ITEM_TYPES + SWORD * game.ITEM_TYPE_SIZE + 4, 40)
        log.game.kit_ids = lambda creature: [kits.SCOUT]
        self.assertEqual(needs(log, hidden=True)[0][1:3], (3, "from behind"))
        log.game.kit_ids = lambda creature: [kits.RESCUER]
        self.assertEqual(needs(log, hidden=True)[0][1:3], (2, "a backstab"))
        del log.game.kit_ids
        wear(log, STALKER, 60, 30, game.BACK_GIRDLE_TYPE, hitchance.WAIST_SLOT)
        log.guest.mem[ITEM_TYPES + game.BACK_GIRDLE_TYPE * game.ITEM_TYPE_SIZE + 0x0F] = 0
        self.assertEqual(needs(log, hidden=True)[0][1:3], (7, ""))

    def test_hidden_ones_second_weapon(self):
        """The game swings the weapons in its item list's order, and a hidden thief's second one
        is a plain swing (DSCLOG's REAR_FRESH, #116: before it, the first's flags stayed up, the AC
        from behind and THAC0 2 worse: Seneca's Shadowseeker at the fountain, 2026-11-17), or from
        behind by the target's facing, with no backstab (STAB_FIRST)."""
        log = fight()
        m = log.guest.mem
        struct.pack_into("<H", m, SHEETS + game.SHEET_FLAGS, hitchance.THIEF_FLAG)
        struct.pack_into("<H", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_TYPE, SWORD)  # (the bow's item a second sword)
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = game.WEAPON_HANDS[1]
        log.game.two_weapons = lambda creature, slot, head=None: ("two weapons", 0)
        struct.pack_into("<Bh", m, THINGS + 40 * 3, game.THING_ITEM, 6)  # (the left hand's the first of his items)
        struct.pack_into("<h", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_NEXT, 5)
        struct.pack_into("<h", m, ITEMS + 5 * game.ITEM_SIZE + game.ITEM_NEXT, game.NO_ITEM)
        got = hitchance.predict(log.game, 0, FOE, hidden=True)
        self.assertEqual([(s.weapon, s.need, s.how, s.thac0, s.ac) for s in got],
                         [("Metal Long Sword", 2, "a backstab", 6, 4), ("Metal Long Sword +1", 7, "", 9, 2)])
        m[FACING] = (hitchance.way(log.game, FOE, 0) + 4) % 8  # (the target's back to him)
        got = hitchance.predict(log.game, 0, FOE, hidden=True)
        self.assertEqual([(s.weapon, s.need, s.how, s.thac0, s.ac) for s in got],
                         [("Metal Long Sword", 2, "a backstab", 6, 4), ("Metal Long Sword +1", 3, "from behind", 7, 4)])

    def test_hidden_archer_unseen(self):
        log = fight(near=False)
        self.assertEqual(needs(log, hidden=True)[1][1:3], (12, "unseen"))
        self.assertEqual(hitchance.brief(hitchance.predict(log.game, 0, FOE, hidden=True)[1:]), "Unseen: 12+ (45%)")

    def test_the_targets_part(self):
        """The target's Blur 2 worse, its Fogbolt 2 better, its Golden Girdle of Urnst 3 worse
        for a sword in melee."""
        log = fight()
        set_effects(log, [(FOE, FOE, hitchance.BLUR)])
        self.assertEqual(needs(log)[0][1], 9)
        set_effects(log, [(FOE, 0, game.FOG_EFFECT)])
        self.assertEqual(needs(log)[0][1], 5)
        set_effects(log, [])
        wear(log, STALKER, 60, 30, game.URNST_GIRDLE_TYPE, hitchance.WAIST_SLOT)
        log.guest.mem[ITEM_TYPES + game.URNST_GIRDLE_TYPE * game.ITEM_TYPE_SIZE + 0x0F] = 0
        from dsloader import specialize, worldgear
        if specialize.kind_of(SWORD) in worldgear.SWORD_KINDS:
            self.assertEqual(needs(log)[0][1], 10)

    def test_a_held_target(self):
        """AD&D's held target (always on): a Paralyzed one is hit whatever the roll."""
        log = fight()
        self.assertEqual(hitchance.line(hitchance.predict(log.game, 0, FOE)), "needs 7+ (70%)")
        set_effects(log, [(FOE, 0, game.PARALYZED_EFFECT)])
        swings = hitchance.predict(log.game, 0, FOE)
        self.assertEqual(hitchance.line(swings), "hits whatever the roll (Paralyzed)")
        self.assertEqual(hitchance.brief(swings), "Hits (Paralyzed)")

    def test_what_the_game_added_to_the_ac(self):
        """AC_GAP: what the game's AC for the target was above the Loader's count when last attacked."""
        log = fight()
        self.assertEqual(needs(log, ac_gap=-2)[0][1], 9)

    def test_the_ends_of_the_d20(self):
        """A 20 always hits, a 1 always misses: 95% at best, 5% at worst."""
        self.assertEqual([hitchance.chance(n) for n in (-3, 2, 3, 11, 20, 21, 30)], [95, 95, 90, 50, 5, 5, 5])
        self.assertEqual([hitchance.chance(n) for n in range(-5, 30)], [dicelog.hit_chance(n) for n in range(-5, 30)])
        self.assertEqual(hitchance.line([hitchance.Swing("x", False, 1)]), "hits on anything but a 1 (95%)")
        self.assertEqual(hitchance.line([hitchance.Swing("x", False, 23)]), "only a 20 hits (5%)")
        self.assertEqual(hitchance.brief([hitchance.Swing("x", False, 23)]), "Needs 20 (5%)")
        self.assertEqual(hitchance.brief([hitchance.Swing("x", False, 0)]), "Needs 2+ (95%)")
        self.assertEqual((hitchance.line([]), hitchance.brief([])), ("", ""))

    def test_not_a_creature(self):
        log = fight()
        self.assertEqual(hitchance.predict(log.game, 0, 77), [])

    def test_distance(self):
        """The game's squares: next to each other 1, diagonally too; two across 2, two across and
        two down 3."""
        log = fight()
        for (x, y), squares in (((10, 10), 1), ((10, 9), 1), ((9, 10), 2), ((9, 9), 2), ((9, 8), 3), ((11, 10), 0)):
            place(log, 0, x, y)
            self.assertEqual(hitchance.squares(log.game, 0, FOE), squares, (x, y))


class EnemiesTests(unittest.TestCase):
    def test_the_sequels_sides(self):
        """Shattered Lands': another side than the leader's, not the neutral 4. Wake of the Ravager's
        (rings.HOSTILE_SIDES, ravlog's 0F80h): the sides whose bit is in the mask, 7-11 (the Draxans' 7),
        not the street's people on 1-6."""
        from dsloader import rings
        log = fight()
        log.game.in_combat = lambda: True
        side = CREATURES + STALKER * game.CREATURE_SIZE + game.CREATURE_SIDE
        struct.pack_into("<h", log.guest.mem, CREATURES + STALKER * game.CREATURE_SIZE, 30)  # (its HP)
        self.assertEqual(rings.enemies(log.game), [FOE])
        self.addCleanup(setattr, rings, "HOSTILE_SIDES", rings.HOSTILE_SIDES)
        rings.HOSTILE_SIDES = 0xF80
        for value, foe in ((2, False), (1, False), (6, False), (7, True), (11, True), (12, False), (200, False)):
            log.guest.mem[side] = value
            self.assertEqual(rings.enemies(log.game), [FOE] if foe else [], value)


class AttackAcTests(unittest.TestCase):
    """The game's AC routine (58DD3h, 7C557h) as GameData.attack_ac counts it."""

    def setUp(self):
        self.log = fight()
        self.g = self.log.game

    def ac(self, rear=False):
        return self.g.attack_ac(STALKER, 0, rear)

    def test_dex_not_from_behind(self):
        self.assertEqual((self.ac(), self.ac(True)), (2, 4))
        self.assertEqual(self.ac(), self.g.counted_ac(STALKER))

    def test_armour_and_the_spells_that_stand_in_for_it(self):
        """Chest armour AC 3 (base 4: 1); Spirit Armor makes the armour 4 at worst, so no better
        here; without the armour it is the 4."""
        wear(self.log, STALKER, 60, 30, 40, game.EQUIP_SLOTS.index("chest"), type_ac=3)
        self.assertEqual(self.ac(), -1)  # 4 - 3, DEX -2
        set_effects(self.log, [(FOE, FOE, game.EFFECT_SPIRIT_ARMOR)])
        self.assertEqual(self.ac(), -1)
        self.log.guest.mem[SHEETS + STALKER * game.SHEET_SIZE + game.SHEET_BASE_AC] = 10
        self.assertEqual(self.ac(), 2)  # (armour 7 made 4, DEX -2)
        set_effects(self.log, [(FOE, FOE, game.EFFECT_IMPROVED_AC)])
        self.assertEqual(self.ac(), 4)  # (6)
        set_effects(self.log, [(FOE, FOE, game.EFFECT_SHIELDED)])
        self.assertEqual((self.ac(), self.ac(True)), (2, 7))  # (Shielded: 4, from the front only)

    def test_a_gladiators_armour_before_it_has_fought(self):
        """A gladiator in armour is a fifth of its level better (level 8: 1). A monster that hasn't fought
        yet has its gear unplaced (every slot byte past the equip slots: a Draxan's brigandine in 14-16 in
        Wake of the Ravager's Tyr ambush, 2026-11-25); the game puts it on before its first attacker's
        swing, so its armour counts as worn then too (armour_ready). In a pack beside gear in place, not."""
        m = self.log.guest.mem
        sheet = SHEETS + STALKER * game.SHEET_SIZE
        struct.pack_into("<H", m, sheet + game.SHEET_FLAGS, game.SHEET_FLAG_GLADIATOR)
        m[sheet + game.SHEET_CLASSES:sheet + game.SHEET_CLASSES + 3] = bytes((game.GLADIATOR_CLASS, 0, 0))
        m[sheet + game.SHEET_LEVELS:sheet + game.SHEET_LEVELS + 3] = bytes((8, 0, 0))
        chest = game.EQUIP_SLOTS.index("chest")
        wear(self.log, STALKER, 60, 30, 40, chest, type_ac=3)
        placed = self.ac()
        self.assertEqual(placed, -2)  # (4 - 3, DEX -2, the gladiator's 1)
        m[ITEMS + 30 * game.ITEM_SIZE + game.ITEM_SLOT] = len(game.EQUIP_SLOTS)  # (unplaced)
        self.assertEqual(self.ac(), placed)
        struct.pack_into("<h", m, ITEMS + 30 * game.ITEM_SIZE + game.ITEM_NEXT, 31)  # (a ring in place beside it)
        at = ITEMS + 31 * game.ITEM_SIZE
        struct.pack_into("<H", m, at + game.ITEM_TYPE, game.RING_TYPE)
        struct.pack_into("<h", m, at + game.ITEM_NEXT, game.NO_ITEM)
        m[at + game.ITEM_SLOT], m[at + game.ITEM_PLUS] = game.FINGERS[0], 0
        self.assertEqual(self.ac(), placed + 1)

    def test_other_effects(self):
        """Displacement 2 better, Blind and Slowed 4 worse each, Biofeedback 1 better; the attacker
        Blind, or the target Invisible, 4 better (not with Detect Invis)."""
        for effects, ac in (([(FOE, FOE, game.EFFECT_DISPLACEMENT)], 0), ([(FOE, 0, game.EFFECT_BLIND)], 6),
                            ([(FOE, 0, game.SLOWED_EFFECT)], 6), ([(FOE, FOE, game.EFFECT_BIOFEEDBACK)], 1),
                            ([(0, FOE, game.EFFECT_BLIND)], -2), ([(FOE, FOE, game.EFFECT_INVISIBLE)], -2),
                            ([(FOE, FOE, game.EFFECT_INVISIBLE), (0, 0, game.EFFECT_DETECT_INVIS)], 2),
                            ([(FOE, FOE, game.EFFECT_PROT_EVIL)], 2)):
            set_effects(self.log, effects)
            self.assertEqual(self.ac(), ac, effects)
        self.log.guest.mem[SHEETS + 0x1A] = game.EVIL_ALIGNMENTS[0]  # (Dag evil)
        self.assertEqual(self.ac(), 0)

    def test_a_ring_of_protection(self):
        """A ring's plus counts (DSCLOG's PROBE_RING_AC: the Templar's Ring of Protection +1 at the
        fountain, AC 4 in the game where the armour alone made 5, 2026-11-17); with AD&D's
        protection rule (always on) not over magical armour."""
        wear(self.log, STALKER, 60, 30, game.RING_TYPE, game.FINGERS[0], plus=1)
        self.log.guest.mem[ITEM_TYPES + game.RING_TYPE * game.ITEM_TYPE_SIZE + 0x0F] = 0
        self.assertEqual(self.ac(), 1)
        m = self.log.guest.mem
        struct.pack_into("<h", m, ITEMS + 30 * game.ITEM_SIZE + game.ITEM_NEXT, 31)  # (and magical chest armour)
        at = ITEMS + 31 * game.ITEM_SIZE
        struct.pack_into("<H", m, at + game.ITEM_TYPE, 40)
        struct.pack_into("<h", m, at + game.ITEM_NEXT, game.NO_ITEM)
        m[at + game.ITEM_SLOT], m[at + game.ITEM_PLUS] = game.EQUIP_SLOTS.index("chest"), 1
        m[ITEM_TYPES + 40 * game.ITEM_TYPE_SIZE + 0x0F], m[ITEM_TYPES + 40 * game.ITEM_TYPE_SIZE + 0x12] = 0x80, 2
        self.assertEqual(self.ac(), -1)  # (4, the armour 2 and its +1, DEX -2: the ring not counted)

    def test_facing(self):
        self.assertIsNone(self.g.facing(STALKER))
        self.log.guest.mem[FACING] = 5
        self.assertEqual(self.g.facing(STALKER), 5)


class ShownTests(unittest.TestCase):
    def test_on_the_tab_line(self):
        """targeting.update's line with what the chooser needs, between the hit points and the key."""
        log = fight()
        t = targeting.Targeting()
        t.update(log.game, HDR, True, [FOE])
        log.guest.write(HDR + targeting.TSR_TAB, struct.pack("<HH", 1, 0))
        log.game.in_combat = lambda: True
        log.game.whose_turn = lambda: 0
        t2 = targeting.Targeting()
        t2.update(log.game, HDR, True, [FOE])
        log.guest.write(HDR + targeting.TSR_TAB, struct.pack("<HH", 2, 0))
        lines = t2.update(log.game, HDR, True, [FOE], lambda turn, chosen: f"needs {turn + chosen}+ (5%)")
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("Chosen with Tab: Mountain Stalker"), lines)
        self.assertTrue(lines[0].endswith(f", needs {FOE}+ (5%) - Enter attacks it"), lines)
        log.guest.write(HDR + targeting.TSR_TAB, struct.pack("<HH", 3, 0))
        lines = t2.update(log.game, HDR, True, [FOE], lambda turn, chosen: "")
        self.assertNotIn(",", lines[0])

    def test_in_the_header(self):
        """While an enemy is chosen the header is the chance (it has no room for the round's line
        too); where it doesn't fit, the part after the comma goes first."""
        status = {"round": 2, "now": ("Gerakis", 14), "next": [("Cermak", 9), ("Cilla", 3)]}
        self.assertEqual(combatlog.header(status, "Needs 14+ (35%)"), "Needs 14+ (35%)")
        self.assertEqual(combatlog.header(status), "Round 2: Gerakis, then Cermak, Cilla")
        self.assertEqual(combatlog.header({"round": 2, "now": None, "next": [("Cermak", 9)]}, "Needs 14+ (35%)"),
                         "Round 2: then Cermak")
        self.assertEqual(combatlog.header(None, "Needs 14+ (35%)"), "")
        font = FakeFont()  # (5 pixels a character)
        self.assertEqual(combatlog.fit(font, "14+ 35%, behind 10+", 80), "14+ 35%...")

    def test_the_dice_logs_part(self):
        """The dice log: the switch (on unless turned off), the hidden one's bit read from DSCLOG, what the game
        added to the AC kept from the last attack on the target, and the header's text."""
        log = fight()
        self.assertTrue(log.hit_chance)
        self.assertTrue(launch.SWITCH_DEFAULTS["hit_chance"])
        self.assertEqual(hitchance.line(log._swings(0, FOE)), "needs 7+ (70%)")
        log.guest.write(HDR + stealth.TSR_STEALTH, struct.pack("<H", 1))
        self.assertEqual(hitchance.line(log._swings(0, FOE)), "needs 3+ (90%) from behind")
        log.guest.write(HDR + stealth.TSR_STEALTH, struct.pack("<H", 2))  # (someone else hidden)
        self.assertEqual(hitchance.line(log._swings(0, FOE)), "needs 7+ (70%)")
        # the game's AC routine ends with 0 for the stalker against Dag (the Loader counts 2)
        log.describe(entry(0, frame=words(0, 0, FOE, 0, 0), kind=KIND_AC))
        self.assertEqual(log.ac_gap, {STALKER: -2})
        self.assertEqual(hitchance.line(log._swings(0, FOE)), "needs 9+ (60%)")
        log._targeting.chosen = FOE
        log.game.whose_turn = lambda: 0
        self.assertEqual(log._chance_brief(10.0), "Needs 9+ (60%)")
        log.ac_gap.clear()
        self.assertEqual(log._chance_brief(10.2), "Needs 9+ (60%)")  # (kept a moment)
        self.assertEqual(log._chance_brief(10.6), "Needs 7+ (70%)")
        log._targeting.chosen = None
        self.assertEqual(log._chance_brief(11.0), "")
        log._targeting.chosen = FOE
        log.use_settings({"hit_chance": False})
        self.assertEqual((log._chance_brief(12.0), log._swings(0, FOE)), ("", []))
        log.use_settings({})
        self.assertTrue(log.hit_chance)

    def test_a_new_fight_forgets_the_gap(self):
        log = fight()
        log.ac_gap[STALKER] = -3
        dicelog._new_fight(log)
        self.assertEqual(log.ac_gap, {})


@unittest.skipUnless(os.environ.get("DSUN_RESOURCE"), "DSUN_RESOURCE (the game's RESOURCE.GFF) not given")
class HeaderFitTests(unittest.TestCase):
    def test_every_form_fits_the_header(self):
        """The header's room in the game's font (the same at each of the panel's sizes): every
        form of the chance fits it, at its widest numbers."""
        from dsloader import art, gff
        with open(os.environ["DSUN_RESOURCE"], "rb") as f:
            font = art.Font(gff.read_gff(f.read())[("FONT", art.FONT_ID)])
        room = min(combatlog.key_rect(font, g)[0] - 2 - combatlog.HEADER_X for g in combatlog.SIZES.values())
        swing = hitchance.Swing("x", False, 18)
        forms = [swing, swing._replace(need=24), swing._replace(how="from behind"), swing._replace(how="a backstab"),
                 swing._replace(how="unseen", missile=True), swing._replace(behind=18, behind_how="a backstab"),
                 swing._replace(auto="Paralyzed"), swing._replace(auto="Out Cold")]
        for need in range(2, 21):
            for form in forms:
                text = hitchance.brief([form._replace(need=need) if form.need == 18 else form])
                self.assertEqual(combatlog.fit(font, text, room), text, (text, room))


if __name__ == "__main__":
    unittest.main()
