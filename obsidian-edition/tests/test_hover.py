"""The chance to hit over the enemy under the pointer (hover.py): which enemy (the game's own word
for the thing under the pointer, believed inside its picture), which swing, the label's words
within a label's width, its place below "Miss" among the labels, when it shows and its switch."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, combatlog, game, gff, hitchance, hover, labels, launch, shadows, targeting, usable
from test_dicelog import DS, HDR
from test_hitchance import FOE, fight, place
from test_labels import Font

TAIL, SLOTS_OFF, FAR, DAC = 0x7800, 0x20, 0x7900, 0x100
ALLY = 1  # (combatant 1, a party member)
CAMERA = (160, 0)
LEFT, TOP, WIDE, HIGH = 320, 100, 20, 34  # the stalker's picture on the map


def scene(near=True, **more):
    """test_hitchance's fight (Dag, the Mountain Stalker east of him) on the map, Dag's turn, the
    stalker's picture at screen (160-180, 100-134) and the pointer on it, the walk arrow."""
    log = fight(near, **more)
    m = log.guest.mem
    log.tsr_hdr = HDR
    struct.pack_into("<H", m, HDR + labels.TSR_TAIL_SEG, TAIL)
    struct.pack_into("<H", m, HDR + labels.TSR_LABELS, SLOTS_OFF)
    struct.pack_into("<H", m, HDR + combatlog.TSR_FAR_SEG, FAR)
    struct.pack_into("<H", m, HDR + combatlog.TSR_DAC, DAC)
    for i in range(256):
        m[FAR * 16 + DAC + i * 3:FAR * 16 + DAC + i * 3 + 3] = bytes((i // 4,) * 3)
    ds = DS * 16
    struct.pack_into("<hh", m, ds + targeting.CAMERA, *CAMERA)
    rec = ds + targeting.MAP_THINGS + FOE * targeting.MAP_THING_SIZE
    m[rec + hover.MAP_FLAGS] = hover.MAP_SHOWN
    struct.pack_into("<hh", m, rec + hover.MAP_LEFT, LEFT, TOP)
    struct.pack_into("<H", m, rec + hover.MAP_PICTURE, 7)
    m[rec + hover.MAP_WIDTH], m[rec + hover.MAP_HEIGHT] = WIDE, HIGH
    log.game.in_combat = lambda: True
    struct.pack_into("<h", m, ds + game.WHOSE_TURN, 0)
    log._labels.font = Font()
    log._labels_font_tried = True
    log._foes = [FOE]
    point(log, 170, 120)
    return log


def point(log, x, y, under=FOE, mode=hover.WALK, on_map=1):
    m, ds = log.guest.mem, DS * 16
    struct.pack_into("<hh", m, ds + usable.POINTER, x, y)
    struct.pack_into("<HH", m, ds + hover.ON_MAP, on_map, under)
    struct.pack_into("<H", m, ds + hover.MODE, mode)


def slots(log):
    """(thing, width) of each of DSCLOG's label slots in use."""
    out = []
    for n in range(labels.SLOTS):
        s = log.guest.read(TAIL * 16 + SLOTS_OFF + n * labels.SIZE, 8)
        if s[0]:
            out.append((struct.unpack_from("<H", s, 6)[0], s[1]))
    return out


def texts(log):
    return [(s[1], s[2]) for s in log._labels._slots if s is not None]


class WhichEnemy(unittest.TestCase):
    def test_the_picture_on_the_screen(self):
        """A thing's box as the game's finder has it: left and top less the camera, the top
        raised by the record's +0Dh, the width and height inclusive; none for a thing not drawn."""
        rec = bytearray(32)
        rec[hover.MAP_FLAGS] = hover.MAP_SHOWN
        struct.pack_into("<hh", rec, hover.MAP_LEFT, 320, 100)
        struct.pack_into("<H", rec, hover.MAP_PICTURE, 7)
        rec[hover.MAP_WIDTH], rec[hover.MAP_HEIGHT], rec[hover.MAP_RISE] = 20, 34, 6
        self.assertEqual(hover.box(bytes(rec), CAMERA), (160, 94, 180, 128))
        for x, y, inside in ((160, 94, True), (180, 128, True), (159, 100, False), (181, 100, False),
                             (170, 93, False), (170, 129, False)):
            self.assertEqual(hover.inside(bytes(rec), CAMERA, (x, y)), inside, (x, y))
        rec[hover.MAP_FLAGS] = 0
        self.assertIsNone(hover.box(bytes(rec), CAMERA))
        rec[hover.MAP_FLAGS] = hover.MAP_SHOWN
        struct.pack_into("<H", rec, hover.MAP_PICTURE, hover.NONE)
        self.assertIsNone(hover.box(bytes(rec), CAMERA))

    def test_the_games_word_believed_inside_the_picture(self):
        log = scene()
        gd = log.game
        self.assertEqual(hover.target(gd, hover.look(gd), [FOE]), FOE)
        self.assertIsNone(hover.target(gd, hover.look(gd), []))  # (not an enemy: an ally, a body)
        point(log, 170, 120, under=ALLY)  # (an ally in front of it: the click is the ally's)
        self.assertIsNone(hover.target(gd, hover.look(gd), [FOE]))
        point(log, 170, 120, under=hover.NONE)  # (between its legs: no pixel of it)
        self.assertIsNone(hover.target(gd, hover.look(gd), [FOE]))
        point(log, 100, 120)  # (the pointer gone, the word still the thing lit last)
        self.assertIsNone(hover.target(gd, hover.look(gd), [FOE]))
        point(log, 170, 120, on_map=2)  # (a menu up)
        self.assertIsNone(hover.target(gd, hover.look(gd), [FOE]))
        for mode, shown in ((hover.WALK, True), (hover.LOOK, True), (hover.ATTACK, True), (3, False), (5, False)):
            point(log, 170, 120, mode=mode)
            self.assertEqual(hover.target(gd, hover.look(gd), [FOE]) == FOE, shown, mode)


class WhichSwing(unittest.TestCase):
    def test_by_the_pointer(self):
        sword = hitchance.Swing("Long Sword", False, 12)
        knife = hitchance.Swing("Dagger", False, 14)
        bow = hitchance.Swing("Bow", True, 9)
        self.assertIs(hover.swing([sword, knife], hover.WALK, True), sword)  # (next to it: the first swung)
        self.assertIs(hover.swing([sword, knife, bow], hover.WALK, True), sword)  # (the walk arrow walks up)
        self.assertIs(hover.swing([sword, knife, bow], hover.LOOK, True), sword)
        self.assertIs(hover.swing([sword, knife, bow], hover.ATTACK, True), bow)  # (the attack pointer shoots)
        self.assertIs(hover.swing([sword, knife, bow], hover.ATTACK, False), sword)  # (an empty quiver)
        self.assertIs(hover.swing([sword, knife], hover.ATTACK, True), sword)  # (out of the bow's range)
        self.assertIsNone(hover.swing([], hover.WALK, True))

    def test_in_the_fight(self):
        """Dag five squares off: the walk arrow his sword's walk-up number, the attack pointer his
        bow's when his quiver holds something."""
        log = scene(near=False)
        self.assertEqual(log._hover.update(log.game, HDR, True, 10.0, log._labels, lambda: [FOE], log._predict), None)
        log._hover.update(log.game, HDR, True, 10.05, log._labels, lambda: [FOE], log._predict)
        self.assertEqual(texts(log), [(FOE, "7+ (70%)")])
        point(log, 170, 120, mode=hover.ATTACK)
        log._hover.update(log.game, HDR, True, 10.1, log._labels, lambda: [FOE], log._predict)
        self.assertEqual(texts(log), [(FOE, "7+ (70%)")])  # (no arrows: it would walk up)
        m = log.guest.mem  # (arrows in the ammunition slot: item 7, after the bow in his list)
        from test_dicelog import ITEMS
        from dsloader import weaponchoice
        struct.pack_into("<h", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_NEXT, 7)
        struct.pack_into("<h", m, ITEMS + 7 * game.ITEM_SIZE + game.ITEM_NEXT, game.NO_ITEM)
        m[ITEMS + 7 * game.ITEM_SIZE + game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
        log._hover.update(log.game, HDR, True, 10.7, log._labels, lambda: [FOE], log._predict)
        self.assertEqual(texts(log), [(FOE, "16+ (25%)")])


class Words(unittest.TestCase):
    def test_one_swing(self):
        s = hitchance.Swing
        self.assertEqual(hitchance.over(s("x", False, 12)), "12+ (45%)")
        self.assertEqual(hitchance.over(s("x", False, 1)), "2+ (95%)")
        self.assertEqual(hitchance.over(s("x", False, 23)), "20 (5%)")
        self.assertEqual(hitchance.over(s("x", False, 10, "from behind")), "Behind 10+ (55%)")
        self.assertEqual(hitchance.over(s("x", False, 8, "a backstab")), "Backstab 8+ (65%)")
        self.assertEqual(hitchance.over(s("x", True, 10, "unseen")), "Unseen 10+ (55%)")
        self.assertEqual(hitchance.over(s("x", False, 14, behind=10, behind_how="from behind")), "14+ (35%), behind 10+")
        self.assertEqual(hitchance.over(s("x", False, 14, behind=8, behind_how="a backstab")), "14+ (35%), backstab 8+")
        self.assertEqual(hitchance.over(s("x", False, 14, auto="Paralyzed")), "Hits")

    @unittest.skipUnless(os.environ.get("DSUN_RESOURCE"), "DSUN_RESOURCE (the game's RESOURCE.GFF) not given")
    def test_within_a_labels_width(self):
        """Every text the label can be, whole in a label's 128 pixels of the game's font."""
        with open(os.environ["DSUN_RESOURCE"], "rb") as f:
            font = art.Font(gff.read_gff(f.read())[("FONT", art.FONT_ID)])
        s, widest = hitchance.Swing, 0
        for need in range(-3, 26):
            made = [s("x", False, need), s("x", False, need, auto="Out Cold")]
            made += [s("x", False, need, how) for how in ("from behind", "a backstab", "unseen")]
            made += [s("x", False, need, behind=b, behind_how=how) for b in range(-3, 26)
                     for how in ("from behind", "a backstab")]
            for swing in made:
                text = hitchance.over(swing)
                self.assertEqual(labels.fit(font, text), text)
                widest = max(widest, labels.width(font, text))
        self.assertLessEqual(widest, labels.WIDTH_MOST)
        self.assertGreater(widest, 100)  # (the walk-up's two numbers: nearly a label's whole width)


class AmongTheLabels(unittest.TestCase):
    def setUp(self):
        self.log = scene()
        self.lab, self.guest = self.log._labels, self.log.guest

    def test_miss_takes_its_place_and_gives_it_back(self):
        lab, guest = self.lab, self.guest
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 10.0)
        self.assertEqual(texts(self.log), [(FOE, "12+ (45%)")])
        lab.show(guest, HDR, FOE, labels.MISS, labels.MISS_INK, 10.1)
        self.assertEqual(texts(self.log), [(FOE, "Miss")])  # (in the chance's own slot)
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 10.2)
        self.assertEqual(texts(self.log), [(FOE, "Miss")])  # (it waits while "Miss" shows)
        lab.tick(guest, HDR, 10.1 + labels.SHOW_FOR)
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 11.7)
        self.assertEqual(texts(self.log), [(FOE, "12+ (45%)")])

    def test_it_never_pushes_one_out(self):
        lab, guest = self.lab, self.guest
        for thing in (4, 5, 6, 7):
            lab.show(guest, HDR, thing, labels.MISS, labels.MISS_INK, 10.0)
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 10.1)
        self.assertEqual(sorted(texts(self.log)), [(4, "Miss"), (5, "Miss"), (6, "Miss"), (7, "Miss")])
        lab.tick(guest, HDR, 12.0)
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 12.0)
        for thing in (4, 5, 6):
            lab.show(guest, HDR, thing, "Armor: 7 left", labels.CHARGE_INK, 12.1, priority=1)
        self.assertIn((FOE, "12+ (45%)"), texts(self.log))
        lab.show(guest, HDR, 7, labels.MISS, labels.MISS_INK, 12.2)  # (no slot free: the chance's goes)
        self.assertEqual(sorted(t for _, t in texts(self.log)), ["Armor: 7 left"] * 3 + ["Miss"])

    def test_no_flicker(self):
        """The same text asked for again writes nothing; another text is written in the same slot;
        one label at most."""
        lab, guest = self.lab, self.guest
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 10.0)
        self.assertFalse(lab.took_off())
        writes, write = [], guest.write
        guest.write = lambda at, data: (writes.append(at), write(at, data))
        for n in range(1, 40):
            lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 10.0 + n * 0.05)
        self.assertEqual(writes, [])
        lab.tick(guest, HDR, 12.5)  # (kept up by the asking: HOVER_FOR past the last one)
        self.assertEqual(texts(self.log), [(FOE, "12+ (45%)")])
        lab.hover(guest, HDR, 5, "9+ (60%)", hover.INK, 12.6)
        self.assertEqual((texts(self.log), [t for t, _ in slots(self.log)]), ([(5, "9+ (60%)")], [5]))
        self.assertTrue(lab.took_off())  # (the old place: the view drawn again)
        self.assertFalse(lab.took_off())
        lab.hover(guest, HDR, None, "", hover.INK, 12.7)
        self.assertEqual((texts(self.log), slots(self.log)), ([], []))
        self.assertTrue(lab.took_off())
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 13.0)
        lab.tick(guest, HDR, 13.0 + labels.HOVER_FOR)  # (no longer asked for)
        self.assertEqual(texts(self.log), [])

    def test_another_loaders_label_is_taken_off(self):
        """A dice log stopped with the label up leaves its slot filled: the next one empties it."""
        lab, guest = self.lab, self.guest
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 10.0)
        lab.tick(guest, HDR, 10.1)
        self.assertEqual([t for t, _ in slots(self.log)], [FOE])  # (its own: kept)
        new = labels.Labels()
        new.tick(guest, HDR, 10.2)
        self.assertEqual(slots(self.log), [])
        self.assertTrue(new.took_off())
        lab.hover(guest, HDR, FOE, "9+ (60%)", hover.INK, 10.3)  # (once only: not another's later label)
        new.tick(guest, HDR, 10.4)
        self.assertEqual([t for t, _ in slots(self.log)], [FOE])
        new.attached()
        new.tick(guest, HDR, 10.5)
        self.assertEqual(slots(self.log), [])

    def test_shown_with_the_floating_names_off(self):
        lab, guest = self.lab, self.guest
        lab.on = False
        lab.hover(guest, HDR, FOE, "12+ (45%)", hover.INK, 10.0)
        lab.show(guest, HDR, FOE, labels.MISS, labels.MISS_INK, 10.1)
        lab.tick(guest, HDR, 10.2)
        self.assertEqual(texts(self.log), [(FOE, "12+ (45%)")])


class WhenItShows(unittest.TestCase):
    def look(self, log, now, on=True):
        return log._hover.update(log.game, HDR, on, now, log._labels, lambda: log._foes, log._predict)

    def test_two_looks_then_kept(self):
        log = scene()
        self.assertIsNone(self.look(log, 10.0))  # (a first look: not yet)
        self.assertEqual(texts(log), [])
        self.assertEqual(self.look(log, 10.05), FOE)
        self.assertEqual(texts(log), [(FOE, "7+ (70%)")])
        self.assertEqual(slots(log), [(FOE, labels.width(Font(), "7+ (70%)"))])
        made = log._hover.made
        for n in range(2, 8):
            self.look(log, 10.0 + n * 0.05)
        self.assertEqual(log._hover.made, made)  # (nothing moved: not worked out again)
        self.look(log, 10.0 + hover.AGAIN + 0.1)
        self.assertEqual(log._hover.made, made + 1)  # (... until AGAIN seconds have passed)
        place(log, 0, 10, 11)  # (the attacker moved)
        self.look(log, 10.7)
        self.assertEqual(log._hover.made, made + 2)

    def test_the_pointer_leaves(self):
        log = scene()
        self.look(log, 10.0), self.look(log, 10.05)
        point(log, 100, 120)  # (the game's word still the stalker for a pass: not believed)
        self.assertEqual(self.look(log, 10.1), FOE)  # (one look away doesn't take it off)
        point(log, 170, 120)
        self.assertEqual(self.look(log, 10.15), FOE)
        point(log, 100, 120, under=hover.NONE)
        self.look(log, 10.2)
        self.assertEqual(texts(log), [(FOE, "7+ (70%)")])
        self.assertIsNone(self.look(log, 10.2 + hover.LINGER))
        self.assertEqual((texts(log), slots(log)), ([], []))

    def test_only_on_a_party_members_turn_on_the_map(self):
        log = scene()
        m, ds = log.guest.mem, DS * 16
        self.look(log, 10.0), self.look(log, 10.05)
        struct.pack_into("<h", m, ds + game.WHOSE_TURN, FOE)  # (the turn passes to an enemy: gone at once)
        self.assertIsNone(self.look(log, 10.1))
        self.assertEqual(slots(log), [])
        self.look(log, 10.15), self.look(log, 10.2)
        self.assertEqual(slots(log), [])
        struct.pack_into("<h", m, ds + game.WHOSE_TURN, 1)  # (the next member's turn, the pointer at rest)
        self.look(log, 10.25), self.look(log, 10.3)
        self.assertEqual([t for t, _ in slots(log)], [FOE])
        point(log, 170, 120, on_map=2)  # (its END menu opens)
        self.assertIsNone(self.look(log, 10.35))
        self.assertEqual(slots(log), [])
        point(log, 170, 120)
        self.look(log, 10.4), self.look(log, 10.45)
        self.assertEqual([t for t, _ in slots(log)], [FOE])
        log.game.in_combat = lambda: False  # (the fight over)
        self.assertIsNone(self.look(log, 10.5))
        self.assertEqual(slots(log), [])
        log.game.in_combat = lambda: True
        log._foes = []  # (the stalker dead: no enemy)
        self.look(log, 10.55), self.look(log, 10.6)
        self.assertEqual(slots(log), [])

    def test_not_through_the_combat_logs_panel(self):
        """The pointer on the panel: the game still names the enemy behind it, the label doesn't."""
        log = scene()
        m = log.guest.mem
        struct.pack_into("<HH", m, HDR + combatlog.TSR_PANEL_TOP, 110, 78)
        point(log, 170, 120)
        self.look(log, 10.0), self.look(log, 10.05)
        self.assertEqual([t for t, _ in slots(log)], [FOE])  # (the panel hidden)
        struct.pack_into("<H", m, HDR + combatlog.TSR_PANEL_ON, 1)
        self.look(log, 10.1), self.look(log, 10.1 + hover.LINGER)
        self.assertEqual(slots(log), [])
        struct.pack_into("<HH", m, HDR + combatlog.TSR_PANEL_TOP, 122, 78)  # (the pointer above it)
        self.look(log, 10.5), self.look(log, 10.55)
        self.assertEqual([t for t, _ in slots(log)], [FOE])

    def test_the_switch_and_the_dice_logs_pass(self):
        log = scene()
        self.assertTrue(log.hit_hover)
        self.assertTrue(launch.SWITCH_DEFAULTS["hit_hover"])
        log.use_settings({"hit_hover": False, "floating_names": False, "hit_chance": False})
        self.assertFalse(log.hit_hover)
        log._hover_pass(10.0), log._hover_pass(10.05)
        self.assertEqual(slots(log), [])
        log.use_settings({"floating_names": False, "hit_chance": False})  # (its own switch: on with those two off)
        log._labels.on = False
        log._hover_pass(10.1), log._hover_pass(10.15)
        self.assertEqual(texts(log), [(FOE, "7+ (70%)")])
        self.assertEqual(log._chance_brief(10.2), "")  # (Tab's header is its own)
        self.assertIsNone(log._targeting.chosen)
        m = log.guest.mem
        struct.pack_into("<H", m, HDR + shadows.TSR_VIEW_REDRAW, 0)
        point(log, 100, 120, under=hover.NONE)
        log._hover_pass(10.2), log._hover_pass(10.2 + hover.LINGER)
        self.assertEqual(slots(log), [])
        # (the label taken off: the view drawn again, as its old place isn't left clean otherwise)
        self.assertEqual(struct.unpack_from("<H", m, HDR + shadows.TSR_VIEW_REDRAW)[0], 1)


if __name__ == "__main__":
    unittest.main()
