"""Showing what can be used while Alt is held (usable.py): what is marked, the key, the rings'
table and its colours shared with the Tab ring (rings.py), the names (labels.py)."""

import struct
import unittest

from dsloader import combatlog, game, labels, rings, shadows, targeting, usable

DS = 0x5000
LOAD = DS - game.DGROUP
HDR, BASE, DAC, TAIL, SLOTS_OFF = 0x9000, 0x8000, 0x8800, 0x980, 0x20
RING_TAB, RED = 0x100, 0x400
CREATURES, ITEMS, TYPES, NAMES, TRIGGERS, DRAWN = 0x20000, 0x24000, 0x28000, 0x29000, 0x2C000, 0x2E000
PLAIN_TYPE, SCENERY_TYPE, CHEST_TYPE = 0x3C, 0x3D, 0x31
# things: the party's leader, Kurzak (talked to), a Guard (another side, no talk), a neutral
# onlooker, a door, a secret door, a chest, a haystack with a use trigger, a plain one, a pot on the
# ground, a body, a dead guard
LEADER, KURZAK, GUARD, ONLOOKER, DOOR, SECRET, CHEST, HAY, PLAIN_HAY, POT, BODY, DEAD, FOUNTAIN = range(13)


class Guest:
    def __init__(self):
        self.mem = bytearray(0x110000)
        self.writes = []

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.writes.append((at, bytes(data)))
        self.mem[at:at + len(data)] = data

    def far(self, offset, linear):
        struct.pack_into("<HH", self.mem, DS * 16 + offset, linear & 15, linear >> 4)


class Font:
    height = 9

    def glyph(self, ch):
        return 3, bytes((0, combatlog.FONT_INK, 0) * self.height)


def world(fight: bool = False) -> game.GameData:
    """A map with one of each kind of thing, the view's corner at (1000, 500)."""
    g = Guest()
    m = g.mem
    for offset, at in ((game.CREATURES_PTR, CREATURES), (game.ITEMS_PTR, ITEMS), (game.ITEM_TYPES_PTR, TYPES),
                       (game.ITEM_NAMES_PTR, NAMES), (usable.TRIGGERS_PTR, TRIGGERS), (usable.DRAW_LIST, DRAWN)):
        g.far(offset, at)
    things = (LOAD + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
    drawn = []

    def place(thing, kind, index, x, y, obj=0, height=40):
        struct.pack_into("<Bh", m, things + thing * 3, kind, index)
        rec = DS * 16 + targeting.MAP_THINGS + thing * 32
        m[rec + usable.MAP_HEIGHT] = height
        struct.pack_into("<HH", m, rec + targeting.MAP_FEET, x, y)
        struct.pack_into("<h", m, rec + usable.MAP_OBJECT, obj)
        drawn.append(struct.pack("<hhBBH", x, y, 0, 0x0F, thing))

    def creature(thing, index, name, ident, side, hp=20, status=1, x=1100, y=600):
        rec = bytearray(game.CREATURE_SIZE)
        struct.pack_into("<h", rec, 0, hp)
        struct.pack_into("<h", rec, usable.CREATURE_ID, ident)
        rec[game.CREATURE_STATUS], rec[game.CREATURE_SIDE] = status, side
        rec[game.CREATURE_NAME:game.CREATURE_NAME + len(name)] = name
        m[CREATURES + index * game.CREATURE_SIZE:CREATURES + (index + 1) * game.CREATURE_SIZE] = rec
        place(thing, 2, index, x, y, obj=-ident)

    def item(thing, index, name, ident, typ, contents=game.NO_ITEM, x=1100, y=600, obj=None, height=20):
        rec = bytearray(game.ITEM_SIZE)
        struct.pack_into("<h", rec, 0, ident)
        struct.pack_into("<H", rec, usable.ITEM_CONTENTS, contents)
        struct.pack_into("<H", rec, game.ITEM_TYPE, typ)
        struct.pack_into("<H", rec, game.ITEM_NAME, index)
        m[ITEMS + index * game.ITEM_SIZE:ITEMS + (index + 1) * game.ITEM_SIZE] = rec
        m[NAMES + index * game.ITEM_NAME_SIZE:NAMES + index * game.ITEM_NAME_SIZE + len(name)] = name
        place(thing, game.THING_ITEM, index, x, y, obj=-ident if obj is None else obj, height=height)

    for typ, flags in ((PLAIN_TYPE, 0x40), (SCENERY_TYPE, 0x60), (CHEST_TYPE, 0x40), (0x17, 0x60), (0x72, 0x60)):
        m[TYPES + typ * game.ITEM_TYPE_SIZE + usable.TYPE_FLAGS] = flags
    creature(LEADER, 0, b"Gerakis", 32000, side=1, x=1160, y=600)
    creature(KURZAK, 14, b"Kurzak", -29, side=4, x=1200, y=620)
    creature(GUARD, 15, b"Guard", -293, side=2, x=1040, y=560)
    creature(ONLOOKER, 16, b"Slave", -500, side=4, x=1060, y=660)
    creature(DEAD, 17, b"Guard", -293, side=2, hp=0, status=usable.STATUS_DEAD, x=1250, y=650)
    item(DOOR, 1, b"Door", -2143, 0x72, x=1020, y=640, height=47)
    item(SECRET, 2, b"Brick Wall", -2700, 0x17, x=1300, y=540)
    item(CHEST, 3, b"Chest", -1563, CHEST_TYPE, contents=501, x=1280, y=580, height=15)
    item(HAY, 4, b"A haystack", -2049, SCENERY_TYPE, x=1100, y=680, height=25)
    item(PLAIN_HAY, 5, b"A haystack", -2050, SCENERY_TYPE, x=1140, y=690)
    item(POT, 6, b"Pot of Water", -1095, PLAIN_TYPE, x=1180, y=540, height=10)
    item(BODY, 7, b"Dead Body", -1101, SCENERY_TYPE, x=1220, y=560, obj=1101)
    item(FOUNTAIN, 8, b"Fountain", -1250, SCENERY_TYPE, x=2000, y=900)  # (out of the view)
    drawn.append(struct.pack("<hhBBH", 1050, 510, 0, 0x0B, 55135))  # (the region's scenery: not a thing)
    m[DRAWN:DRAWN + len(b"".join(drawn))] = b"".join(drawn)
    struct.pack_into("<H", m, DS * 16 + usable.DRAW_COUNT, len(drawn))
    # the triggers: Kurzak's talk (two in the list), the haystack's use, the pot on the fountain
    lists = {usable.TALK: [(-88, 0), (-29, 0)], usable.USE: [(-2049, 0)], usable.USE_WITH: [(-30119, -1250)],
             usable.LOOK: []}
    n = 0
    for head, entries in lists.items():
        struct.pack_into("<H", m, (LOAD + usable.HEADS_SEG) * 16 + head, n if entries else usable.NO_TRIGGER)
        for k, (ident, other) in enumerate(entries):
            at = TRIGGERS + n * usable.TRIGGER_SIZE
            struct.pack_into("<hh", m, at + usable.TRIGGER_ID, ident, other)
            struct.pack_into("<H", m, at + usable.TRIGGER_NEXT, n + 1 if k + 1 < len(entries) else usable.NO_TRIGGER)
            n += 1
    struct.pack_into("<hh", m, DS * 16 + targeting.CAMERA, 1000, 500)
    struct.pack_into("<hh", m, DS * 16 + usable.POINTER, 205, 100)  # (on Kurzak)
    if fight:
        struct.pack_into("<H", m, DS * 16 + game.IN_COMBAT, 1)
        struct.pack_into("<H", m, (DS - game.FIGHT_STATE_FROM_DS) * 16 + game.FIGHT_STATE_ON, 1)
    # DSCLOG's header: the far block (RING_TAB, RED, the palette), the tail's label slots
    struct.pack_into("<H", m, HDR + rings.TSR_HDR_OFF, HDR - BASE)
    struct.pack_into("<H", m, HDR + rings.TSR_FAR_SEG, BASE // 16)
    struct.pack_into("<H", m, HDR + rings.TSR_RING_TAB, RING_TAB)
    struct.pack_into("<H", m, HDR + rings.TSR_RED, RED)
    struct.pack_into("<H", m, HDR + combatlog.TSR_DAC, DAC - BASE)
    struct.pack_into("<H", m, HDR + labels.TSR_TAIL_SEG, TAIL)
    struct.pack_into("<H", m, HDR + labels.TSR_LABELS, SLOTS_OFF)
    for i in range(256):  # (greys below 128, then ever more golden)
        m[DAC + i * 3:DAC + i * 3 + 3] = bytes((i // 4,) * 3) if i < 128 else bytes((i // 4, i // 5, (255 - i) // 8))
    g.writes.clear()
    return game.GameData(g, DS)


def hold(gd, down: bool = True) -> None:
    gd.guest.mem[usable.KEY_FLAGS] = usable.ALT | 0x20 if down else 0x20  # (Num Lock's bit: not Alt)


def slot(gd, n):
    return gd.guest.read(TAIL * 16 + SLOTS_OFF + n * labels.SIZE, labels.SIZE)


def ring_tab(gd):
    return gd.guest.read(BASE + RING_TAB, rings.THINGS)


class WhatIsMarked(unittest.TestCase):
    def test_marks(self):
        """People with a talk trigger, foes on another side, doors, containers, bodies, things a
        trigger names and items to pick up; not the party, the dead, a neutral with nothing to
        say, a secret door, plain scenery, nor the region's scenery in the draw list."""
        found = {m.thing: m for m in usable.marks(world())}
        self.assertEqual({t: m.kind for t, m in found.items()},
                         {KURZAK: usable.PERSON, GUARD: usable.FOE, DOOR: usable.DOOR, CHEST: usable.CONTAINER,
                          HAY: usable.USED, POT: usable.ITEM, BODY: usable.BODY, FOUNTAIN: usable.USED})
        self.assertEqual((found[KURZAK].name, found[KURZAK].x, found[KURZAK].y), ("Kurzak", 1200, 620))
        self.assertEqual(found[HAY].name, "A haystack")

    def test_name_heights(self):
        """A name goes just over a low thing, and no higher than over a man."""
        found = {m.thing: m for m in usable.marks(world())}
        self.assertEqual(found[POT].up, 10 + usable.UP_OVER)
        self.assertEqual(found[DOOR].up, labels.UP)
        self.assertEqual(found[KURZAK].up, labels.UP)

    def test_triggers(self):
        """The lists walked from their heads; a use-with's two ids both count."""
        found = usable.triggers(world())
        self.assertEqual(found[usable.TALK], {-88, -29})
        self.assertEqual(found[usable.USE], {-2049})
        self.assertEqual(found[usable.USE_WITH], {-30119, -1250})
        self.assertEqual(found[usable.LOOK], set())

    def test_a_looping_list_ends(self):
        gd = world()
        struct.pack_into("<H", gd.guest.mem, TRIGGERS + 1 * usable.TRIGGER_SIZE + usable.TRIGGER_NEXT, 0)
        self.assertEqual(usable.triggers(gd)[usable.TALK], {-88, -29})

    def test_nameless_things_ringed_not_named(self):
        gd = world()
        gd.guest.mem[NAMES + 4 * game.ITEM_NAME_SIZE] = 0  # (the haystack: no name)
        hay = next(m for m in usable.marks(gd) if m.thing == HAY)
        self.assertEqual(hay.name, "")
        self.assertNotIn(hay, usable.nearest([hay], (1000, 500), (100, 170)))

    def test_nearest_the_pointer(self):
        """The four named: those in the view nearest the pointer, the nearest first."""
        found = usable.marks(world())
        named = usable.nearest(found, (1000, 500), (205, 100))
        self.assertEqual(len(named), usable.NAMED)
        self.assertEqual(named[0].thing, KURZAK)
        self.assertNotIn(FOUNTAIN, [m.thing for m in named])  # (off the screen)
        self.assertEqual(usable.nearest(found, (1000, 500), (22, 120))[0].thing, DOOR)

    def test_rings_near_the_view_only(self):
        found = usable.marks(world())
        table = usable.ring_table(found, (1000, 500))
        self.assertEqual({t for t in range(game.THINGS) if table[t]}, {KURZAK, GUARD, DOOR, CHEST, HAY, POT, BODY})
        self.assertEqual(set(table), {0, usable.RING})
        self.assertTrue(usable.ring_table(found, (2000 - 320 - usable.NEAR + 1, 900 - 200 - usable.NEAR + 1))[FOUNTAIN])


class TheKey(unittest.TestCase):
    def test_alt(self):
        gd = world()
        self.assertFalse(usable.alt_held(gd.guest))
        hold(gd)
        self.assertTrue(usable.alt_held(gd.guest))

    def test_a_stuck_flag(self):
        """Alt reading held for STUCK_AFTER seconds is a flag left set: nothing until it clears."""
        gd, u = world(), usable.Usable()
        hold(gd)
        self.assertTrue(u.held(gd.guest, 10.0))
        self.assertTrue(u.held(gd.guest, 10.0 + usable.STUCK_AFTER - 0.1))
        self.assertFalse(u.held(gd.guest, 10.0 + usable.STUCK_AFTER))
        self.assertFalse(u.held(gd.guest, 500.0))
        hold(gd, False)
        self.assertFalse(u.held(gd.guest, 501.0))
        hold(gd)
        self.assertTrue(u.held(gd.guest, 502.0))

    def test_up_and_down(self):
        """Held out of a fight with the switch on: the table and the names; let go: neither."""
        gd, u, lab = world(), usable.Usable(), labels.Labels()
        lab.font = Font()
        self.assertIsNone(u.update(gd, HDR, True, 1.0, lab))
        self.assertFalse(u.changed(gd, True, 1.1))
        hold(gd)
        self.assertTrue(u.changed(gd, True, 1.2))
        table = u.update(gd, HDR, True, 1.2, lab)
        self.assertTrue(table[KURZAK] and u.active)
        self.assertFalse(u.changed(gd, True, 1.3))
        struct.pack_into("<hh", gd.guest.mem, DS * 16 + targeting.CAMERA, 1016, 500)  # (the view scrolled)
        self.assertTrue(u.changed(gd, True, 1.3))
        struct.pack_into("<hh", gd.guest.mem, DS * 16 + targeting.CAMERA, 1000, 500)
        things = {struct.unpack_from("<H", slot(gd, n), 6)[0] for n in range(labels.SLOTS) if slot(gd, n)[0]}
        self.assertEqual(len(things), usable.NAMED)
        self.assertIn(KURZAK, things)
        hold(gd, False)
        self.assertTrue(u.changed(gd, True, 1.4))
        self.assertIsNone(u.update(gd, HDR, True, 1.4, lab))
        self.assertEqual([slot(gd, n)[0] for n in range(labels.SLOTS)], [0] * labels.SLOTS)

    def test_switched_off_or_in_a_fight(self):
        gd, u = world(), usable.Usable()
        hold(gd)
        self.assertIsNone(u.update(gd, HDR, False, 1.0))
        self.assertIsNone(u.update(gd, None, True, 1.0))
        fight, lab = world(fight=True), labels.Labels()
        lab.font = Font()
        hold(fight)
        self.assertIsNone(u.update(fight, HDR, True, 1.0, lab))
        self.assertEqual(fight.guest.writes, [])

    def test_a_fight_begun_while_held_takes_the_marks_down(self):
        gd, u, lab = world(), usable.Usable(), labels.Labels()
        lab.font = Font()
        hold(gd)
        u.update(gd, HDR, True, 1.0, lab)
        struct.pack_into("<H", gd.guest.mem, DS * 16 + game.IN_COMBAT, 1)
        struct.pack_into("<H", gd.guest.mem, (DS - game.FIGHT_STATE_FROM_DS) * 16 + game.FIGHT_STATE_ON, 1)
        self.assertTrue(u.changed(gd, True, 1.1))
        self.assertIsNone(u.update(gd, HDR, True, 1.1, lab))
        self.assertEqual([slot(gd, n)[0] for n in range(labels.SLOTS)], [0] * labels.SLOTS)


class TheRingsTable(unittest.TestCase):
    """rings.py owns DSCLOG's RING_TAB and its colours: gold marks out of a fight, the red Tab
    ring in one."""

    def redraws(self, gd):
        return struct.unpack("<H", gd.guest.read(HDR + shadows.TSR_VIEW_REDRAW, 2))[0]

    def test_gold_marks_then_none(self):
        gd, r = world(), rings.Rings()
        marks = usable.ring_table(usable.marks(gd), (1000, 500))
        dac = gd.guest.read(DAC, 768)
        r.update(gd, HDR, False, 1, None, marks)  # (the Options tab's ring off: the marks still show)
        self.assertEqual(ring_tab(gd), marks)
        self.assertEqual(gd.guest.read(BASE + RED, 256), rings.gold_table(dac))
        self.assertEqual(struct.unpack("<H", gd.guest.read(HDR + rings.TSR_RINGS_ON, 2))[0], 1)
        self.assertEqual(self.redraws(gd), 1)
        # (on last of all: DSCLOG never draws an old table, or these in the old colours)
        self.assertEqual(gd.guest.writes[-1][0], HDR + rings.TSR_RINGS_ON)
        gd.guest.write(HDR + shadows.TSR_VIEW_REDRAW, b"\0\0")
        r.update(gd, HDR, False, 1, None, None)  # (let go)
        self.assertEqual(struct.unpack("<H", gd.guest.read(HDR + rings.TSR_RINGS_ON, 2))[0], 0)
        self.assertEqual(ring_tab(gd), bytes(rings.THINGS))
        self.assertEqual(self.redraws(gd), 1)

    def test_red_again_for_the_tab_ring(self):
        """With the Tab ring on: gold while the marks are up, red again once they are down."""
        gd, r = world(), rings.Rings()
        marks = usable.ring_table(usable.marks(gd), (1000, 500))
        dac = gd.guest.read(DAC, 768)
        r.update(gd, HDR, True, 1)
        self.assertEqual(gd.guest.read(BASE + RED, 256), rings.red_table(dac))
        r.update(gd, HDR, True, 1, None, marks)
        self.assertEqual(gd.guest.read(BASE + RED, 256), rings.gold_table(dac))
        self.assertEqual(ring_tab(gd), marks)
        r.update(gd, HDR, True, 1, None, None)
        self.assertEqual(gd.guest.read(BASE + RED, 256), rings.red_table(dac))
        self.assertEqual(ring_tab(gd), bytes(rings.THINGS))

    def test_a_fight_keeps_the_table(self):
        """In a fight the table is the Tab ring's, red, whatever marks are handed in."""
        gd, r = world(fight=True), rings.Rings()
        marks = bytes([usable.RING]) * rings.THINGS
        saved, rings.enemies = rings.enemies, lambda g: [GUARD]
        try:
            r.update(gd, HDR, True, 1, GUARD, marks)
        finally:
            rings.enemies = saved
        table = ring_tab(gd)
        self.assertEqual({t: table[t] for t in range(rings.THINGS) if table[t]}, {GUARD: rings.CHOSEN})
        self.assertEqual(gd.guest.read(BASE + RED, 256), rings.red_table(gd.guest.read(DAC, 768)))

    def test_gold_table(self):
        """Each colour's golder one: nearer gold than it, clearly; none for one as gold as any."""
        dac = world().guest.read(DAC, 768)
        table = rings.gold_table(dac)
        pal = [tuple(min(255, dac[i * 3 + k] * 4) for k in range(3)) for i in range(256)]
        far = lambda p: sum((a - b) ** 2 for a, b in zip(p, rings.GOLD)) ** 0.5
        self.assertTrue(table[40] and table[100])
        for i in range(256):
            if table[i]:
                self.assertLessEqual(far(pal[table[i]]), far(pal[i]) - rings.GOLD_NEARER)
                self.assertTrue(rings.FIRST <= table[i] <= rings.LAST)
        best = min(range(rings.FIRST, rings.LAST + 1), key=lambda i: far(pal[i]))
        self.assertEqual(table[best], 0)
        self.assertEqual(set(table[:rings.FIRST]) | set(table[rings.LAST + 1:]), {0})


class TheNames(unittest.TestCase):
    def setUp(self):
        self.gd, self.lab = world(), labels.Labels()
        self.lab.font = Font()
        self.guest = self.gd.guest

    def things(self):
        return [struct.unpack_from("<H", slot(self.gd, n), 6)[0] if slot(self.gd, n)[0] else None
                for n in range(labels.SLOTS)]

    def test_names_stand_and_go(self):
        """A name stays while asked for (not written again), and goes when no longer wanted."""
        self.lab.names(self.guest, HDR, [(KURZAK, "Kurzak", usable.NAME_INK, 34), (POT, "Pot", usable.NAME_INK, 13)], 1.0)
        self.assertEqual(self.things(), [KURZAK, POT, None, None])
        self.assertEqual(slot(self.gd, 1)[3], 13)  # (how far over its feet)
        written = len(self.guest.writes)
        self.lab.names(self.guest, HDR, [(KURZAK, "Kurzak", usable.NAME_INK, 34), (POT, "Pot", usable.NAME_INK, 13)], 1.2)
        self.assertEqual(len(self.guest.writes), written)
        self.lab.tick(self.guest, HDR, 1.0 + labels.NAME_FOR + 0.1)  # (asked for again since: kept)
        self.assertEqual(self.things(), [KURZAK, POT, None, None])
        self.lab.names(self.guest, HDR, [(POT, "Pot", usable.NAME_INK, 13)], 1.4)
        self.assertEqual(self.things(), [None, POT, None, None])
        self.lab.tick(self.guest, HDR, 1.4 + labels.NAME_FOR)  # (no longer asked for: its time up)
        self.assertEqual(self.things(), [None] * 4)

    def test_names_take_free_slots_only(self):
        """A "Miss" or a spell's name keeps its slot, and takes a name's when none is free."""
        for thing, text in ((20, "Miss"), (21, "Bless"), (22, "Haste")):
            self.lab.show(self.guest, HDR, thing, text, labels.MISS_INK, 1.0)
        wanted = [(KURZAK, "Kurzak", usable.NAME_INK, 34), (POT, "Pot", usable.NAME_INK, 13)]
        self.lab.names(self.guest, HDR, wanted, 1.1)
        self.assertEqual(self.things(), [20, 21, 22, KURZAK])
        self.lab.show(self.guest, HDR, 23, "Miss", labels.MISS_INK, 1.2)  # (no slot free: the name's)
        self.assertEqual(self.things(), [20, 21, 22, 23])
        self.lab.names(self.guest, HDR, wanted, 1.3)
        self.assertEqual(self.things(), [20, 21, 22, 23])

    def test_a_label_over_the_same_figure_stays(self):
        self.lab.show(self.guest, HDR, KURZAK, "Miss", labels.MISS_INK, 1.0)
        self.lab.names(self.guest, HDR, [(KURZAK, "Kurzak", usable.NAME_INK, 34)], 1.1)
        self.assertEqual(self.things(), [KURZAK, None, None, None])
        self.assertEqual(self.lab._slots[0][2], "Miss")
        self.lab.show(self.guest, HDR, POT, "Bless", labels.SPELL_INK, 1.2)
        self.lab.names(self.guest, HDR, [], 1.3)  # (the names taken down: the others left)
        self.assertEqual(self.things(), [KURZAK, POT, None, None])

    def test_names_show_with_floating_names_off(self):
        """The floating names' switch is not the names': they stay, a "Miss" goes."""
        self.lab.show(self.guest, HDR, 20, "Miss", labels.MISS_INK, 1.0)
        self.lab.names(self.guest, HDR, [(KURZAK, "Kurzak", usable.NAME_INK, 34)], 1.0)
        self.lab.on = False
        self.lab.tick(self.guest, HDR, 1.1)
        self.assertEqual(self.things(), [None, KURZAK, None, None])


if __name__ == "__main__":
    unittest.main()
