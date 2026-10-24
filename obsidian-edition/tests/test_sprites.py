"""The party's own sprites in the Loader's SEGOBJEX copy, and dressing them in what they wear."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, game, gff, icons, sprites, spriteparts as sp, spritegear as sg
from test_spriteparts import rows

SWORD, METAL = 63, 4


def read(path):
    with open(path, "rb") as f:
        return f.read()


def game_chunks():
    """A SEGOBJEX's pieces: object 300 the human man, its walking and combat pictures (the test
    figure in each frame), and the cloak's model's."""
    walk = sprites.encode_frames([rows()] * 15)
    fight = sprites.encode_frames([rows()] * 14)
    ojff = bytes(12) + struct.pack("<H", 2095) + b"\0\0"
    return {("OJFF", 300): ojff, ("BMP ", 2095): walk, ("BMP ", 2096): fight,
            ("BMP ", sg.CLOAK_MODEL): walk, ("BMP ", sg.CLOAK_MODEL + 1): fight}



class WornTests(unittest.TestCase):
    def test_named_weapons(self):
        """Kreenfang (the gythka +1) goes to spritegear with its name; a plain gythka without."""
        def item(kind, plus, slot):
            rec = bytearray(game.ITEM_SIZE)
            struct.pack_into("<H", rec, game.ITEM_TYPE, kind)
            rec[game.ITEM_PLUS], rec[game.ITEM_SLOT] = plus & 0xFF, slot
            return bytes(rec)
        typ = bytearray(game.ITEM_TYPE_SIZE)
        typ[0x08] = 1  # (bone)

        class Worn:
            def __init__(self, items):
                self.items = items

            def _worn(self, member):
                return [(0, it, bytes(typ)) for it in self.items]

        right = game.EQUIP_SLOTS.index("right hand")
        gear, _ = sprites.worn(Worn([item(game.GYTHKA_TYPE, 1, right)]), 0)
        self.assertEqual(gear["right"], (game.GYTHKA_TYPE, 1, "Kreenfang", sg.FIRE_GLOW))
        gear, _ = sprites.worn(Worn([item(game.GYTHKA_TYPE, 0, right)]), 0)
        self.assertEqual(gear["right"], (game.GYTHKA_TYPE, 1))
        sword = 45  # any other weapon with a plus: MAGIC, its edge glinting
        gear, _ = sprites.worn(Worn([item(sword, 2, right)]), 0)
        self.assertEqual(gear["right"], (sword, 1, sg.MAGIC, sg.FIRE_GLOW))  # (no objects file: the fire's)
        gear, _ = sprites.worn(Worn([item(sword, 0, right)]), 0)
        self.assertEqual(gear["right"], (sword, 1))
        chest = game.EQUIP_SLOTS.index("chest")
        _, armour = sprites.worn(Worn([item(57, 1, chest)]), 0)  # (chain mail +1: glints)
        self.assertEqual(armour, (57 | sg.MAGIC_ARMOUR,))
        _, armour = sprites.worn(Worn([item(57, 0, chest)]), 0)
        self.assertEqual(armour, (57,))

    def test_glow_for(self):
        """A magic item glows in the cycled colours nearest its icon's: one already shining in
        them, else by hue; greys the blue."""
        sg.set_palette([(0, 0, 0)] * 16 + [(40, 200, 40), (200, 40, 230), (128, 128, 128), (230, 60, 20)] + [(0, 0, 0)] * 236)
        self.assertEqual(sg.glow_for([[16] * 8]), sg.GREEN_GLOW)
        self.assertEqual(sg.glow_for([[17] * 8]), sg.VIOLET_GLOW)
        self.assertEqual(sg.glow_for([[19] * 8]), sg.FIRE_GLOW)
        self.assertEqual(sg.glow_for([[18] * 8]), sg.BLUE_GLOW)
        self.assertEqual(sg.glow_for([[12, 12, 13, 18]]), sg.BLUE_GLOW)  # (the water's shine)
        self.assertEqual(sg.glow_for([[242, 243, 244, 18]]), sg.FIRE_GLOW)

    def test_magic_glint(self):
        """A magic weapon's lightest cells are drawn in the fire colours the game cycles; a plain
        one's in its material's."""
        def drawn(glint, shape=sg.SWORD):
            rows = [[None] * 30 for _ in range(30)]
            sg.draw_weapon(rows, [r[:] for r in rows], (5, 15), 0.0, shape, sg.MATERIAL_COLOURS[4], False,
                           glint=glint)
            return {p for r in rows for p in r if p is not None}
        self.assertFalse(drawn(False) & set(sg.GLINT))
        self.assertTrue(drawn(True) & set(sg.GLINT))
        self.assertTrue(drawn(True, sg.STAFF) & set(sg.GLINT))  # (a staff has no light cells: every third)

    def test_sparkle(self):
        """Magic worn gear glints only on the pixels it changed; a small piece at least twice."""
        before = [[1] * 20 for _ in range(20)]
        rows = [r[:] for r in before]
        for x in range(10):
            rows[5][x] = 7
        sg.sparkle(rows, before)
        glints = [(x, y) for y, r in enumerate(rows) for x, p in enumerate(r) if p in sg.GLINT]
        self.assertGreaterEqual(len(glints), 2)
        self.assertTrue(all(y == 5 and x < 10 for x, y in glints))
        tiny = [r[:] for r in before]
        tiny[3][3] = tiny[3][4] = 7
        sg.sparkle(tiny, before)
        self.assertTrue(any(p in sg.GLINT for r in tiny for p in r))

    def test_magic_shield_glint(self):
        """A magic shield's light and part of its rim glint; a plain one's don't."""
        def drawn(glint):
            rows = [[None] * 30 for _ in range(30)]
            sg.draw_shield(rows, [r[:] for r in rows], (15, 15), sp.FRONT, sg.MATERIAL_COLOURS[4], False, glint=glint)
            return {p for r in rows for p in r if p is not None}
        self.assertFalse(drawn(False) & set(sg.GLINT))
        self.assertTrue(drawn(True) & set(sg.GLINT))

class SpriteTests(unittest.TestCase):
    def test_encode_round_trip(self):
        chunk = sprites.encode_frames([rows(), rows()])
        self.assertEqual(struct.unpack_from("<H", chunk, 4)[0], 2)
        self.assertEqual(art.decode_frame(chunk, 1)[2], rows())

    def test_new_chunks(self):
        """Object 300 pointing at its own pair of pictures, each as long as it needs be: walking,
        the room gear needs there (sprites.room); in a fight, all of PAD."""
        new = sprites.new_chunks(game_chunks())
        walk, fight = sprites.picture_ids(300)
        self.assertEqual((walk, fight), (2450, 2451))
        self.assertEqual(struct.unpack_from("<H", new[("OJFF", 300)], sprites.OJFF_PICTURE)[0], walk)
        chunk = new[("BMP ", walk)]
        self.assertEqual(struct.unpack_from("<I", chunk, 0)[0], len(chunk))
        self.assertEqual(struct.unpack_from("<H", chunk, 4)[0], 15)
        self.assertEqual(art.decode_frame(chunk, 0)[2], sprites.trimmed(sg.padded(rows(), sprites.PAD), False))
        frame = art.decode_frame(chunk, 0)[2]
        self.assertEqual((len(frame[0]), len(frame)), (len(rows()[0]) + 2 * sprites.WALK_SIDE, len(rows()) + sprites.WALK_TOP))
        self.assertEqual(len(art.decode_frame(new[("BMP ", fight)], 0)[2][0]),
                         len(art.decode_frame(game_chunks()[("BMP ", 2096)], 0)[2][0]) + 2 * sprites.PAD)

    def test_room_in_the_copy(self):
        """In the copy each party picture has room after it for its bulkiest outfit, not counted
        in its length (the game loads, and draws, only what the index says)."""
        from test_icons import ranged_gff
        chunks = game_chunks()
        data = ranged_gff({"OJFF": {300: chunks[("OJFF", 300)]},
                           "BMP ": {k[1]: v for k, v in chunks.items() if k[0] == "BMP "}})
        new = sprites.new_chunks(chunks)
        room = sprites.new_room(chunks, new)
        out = icons.with_chunks(data, new, room)
        places = gff.index_places(out, "BMP ")
        pics = sprites.Pictures(chunks)
        walk, fight = sprites.picture_ids(300)
        for picture, combat in ((walk, False), (fight, True)):
            entry, offset, length = places[picture]
            self.assertEqual(out[offset:offset + length], new[("BMP ", picture)])
            self.assertEqual(length + room[("BMP ", picture)], pics.room(300, combat))
            self.assertEqual(struct.unpack_from("<II", out, entry), (offset, length))
        self.assertEqual(gff.read_gff(out)[("BMP ", walk)], new[("BMP ", walk)])
        ordered = sorted(places.values(), key=lambda p: p[1])  # (nothing overlaps the room)
        for (_, a, n), (_, b, _) in zip(ordered, ordered[1:]):
            if a in (places[walk][1], places[fight][1]):
                self.assertGreaterEqual(b - a, pics.room(300, a == places[fight][1]))

    def test_dressed_fits(self):
        """The bulkiest outfit fits the room kept for the picture."""
        pics = sprites.Pictures(game_chunks())
        plain = pics.build(300, False, {}, ())
        dressed = pics.build(300, False, {"right": (SWORD, METAL), "cloak": (65, 5), "boots": (68, 5)}, (57,))
        self.assertGreater(len(dressed), len(plain))
        self.assertLessEqual(len(dressed), pics.room(300, False))
        self.assertNotEqual(art.decode_frame(dressed, 0)[2], art.decode_frame(plain, 0)[2])

    def test_spares(self):
        """A spare pair for each party place, with room for any model."""
        chunks = game_chunks()
        new = sprites.new_chunks(chunks)
        room = sprites.new_room(chunks, new)
        pics = sprites.Pictures(chunks)
        for k, obj in enumerate(sprites.SPARES):
            walk, fight = sprites.picture_ids(obj)
            self.assertEqual(walk, 2478 + 2 * k)
            self.assertIn(("BMP ", walk), new)
            self.assertIn(("BMP ", fight), new)
            self.assertNotIn(("OJFF", obj), new)
            self.assertEqual(len(new[("BMP ", walk)]) + room[("BMP ", walk)], pics.spare_capacity(False))

    def test_same_figure_a_spare(self):
        """The second member of a figure is dressed in their place's spare pair."""
        dresser = sprites.Dresser.__new__(sprites.Dresser)
        dresser.pics = sprites.Pictures(game_chunks())
        dresser.gd = FakeGame(figures=[0, 0, 0])
        self.assertEqual(dresser.objects(), {300: (0, 300), 315: (1, 300), 316: (2, 300)})

    def test_pointed_at_the_spare(self):
        """On the map: the member's picture named the spare and their slot emptied (the game loads
        it); the first member left as they were; back to their own when no longer sharing; a save's
        picture of the game's own made the Loader's; one whose pictures are written anew loaded
        again."""
        gd = FakeGame(figures=[0, 0])
        shared, spare = sprites.picture_ids(300), sprites.picture_ids(315)
        gd.entry(0, shared[0], 3)
        gd.entry(1, shared[0], 3)
        dresser = sprites.Dresser.__new__(sprites.Dresser)
        dresser.gd = gd
        dresser.pics = sprites.Pictures(game_chunks())
        dresser.request_redraw = None
        self.assertTrue(dresser._point(1, 300, 315))
        self.assertEqual(gd.entry_fields(1), (spare[0], sprites.NO_SLOT))
        self.assertFalse(dresser._point(0, 300, 300))
        self.assertEqual(gd.entry_fields(0), (shared[0], 3))
        entry0 = gd.ds * 16 + sprites.MAP_ENTRIES
        self.assertEqual(gd.guest.read(entry0, 1)[0] & sprites.MAP_CHANGED, 0)
        self.assertTrue(dresser._point(0, 300, 300, reload=True))  # (its pictures written anew)
        self.assertEqual(gd.entry_fields(0), (shared[0], sprites.NO_SLOT))
        self.assertEqual(gd.guest.read(entry0, 1)[0] & sprites.MAP_CHANGED, sprites.MAP_CHANGED)
        gd.entry(1, spare[0], 4)
        self.assertFalse(dresser._point(1, 300, 315))  # (already: left alone)
        self.assertTrue(dresser._point(1, 300, 300))
        self.assertEqual(gd.entry_fields(1), (shared[0], sprites.NO_SLOT))
        gd.entry(0, 2095, 5)  # (the game's own picture, from an old save)
        at = gd.ds * 16 + sprites.MAP_ENTRIES + sprites.MAP_ANCHOR
        gd.guest.write(at, bytes([9, 26]))
        self.assertTrue(dresser._point(0, 300, 300))
        self.assertEqual(gd.entry_fields(0), (shared[0], sprites.NO_SLOT))
        self.assertEqual(gd.guest.read(at, 2), bytes([9 + sprites.WALK_SIDE, 26 + sprites.WALK_TOP]))  # (where ours has room)

    def test_in_a_fight_the_view_redrawn(self):
        """Written anew in a fight: the view drawn again (DSCLOG), the figure not marked changed
        (that can set it walking)."""
        gd = FakeGame(figures=[0])
        gd.entry(0, sprites.picture_ids(300)[0], 3)
        dresser = sprites.Dresser.__new__(sprites.Dresser)
        dresser.gd, dresser.pics = gd, sprites.Pictures(game_chunks())
        asked = []
        dresser.request_redraw = lambda: asked.append(True)
        self.assertTrue(dresser._point(0, 300, 300, reload=True))
        self.assertEqual(asked, [True])
        self.assertEqual(gd.entry_fields(0)[1], sprites.NO_SLOT)
        self.assertEqual(gd.guest.read(gd.ds * 16 + sprites.MAP_ENTRIES, 1)[0] & sprites.MAP_CHANGED, 0)

    def dressed_copy(self, d, figures=(0,)):
        """A Dresser for FIGURES with a copy of SEGOBJEX (as the launcher writes it) in D."""
        from test_icons import ranged_gff
        chunks = game_chunks()
        data = ranged_gff({"OJFF": {300: chunks[("OJFF", 300)]},
                           "BMP ": {k[1]: v for k, v in chunks.items() if k[0] == "BMP "}})
        new = sprites.new_chunks(chunks)
        path = os.path.join(d, "SEGOBJEX.GFF")
        with open(path, "wb") as f:
            f.write(icons.with_chunks(data, new, sprites.new_room(chunks, new)))
        dresser = sprites.Dresser.__new__(sprites.Dresser)
        dresser.gd, dresser.pics = FakeGame(figures=list(figures)), sprites.Pictures(chunks)
        dresser.copy_file, dresser.places, dresser._stamp = path, {}, None
        dresser.shown, dresser.request_redraw, dresser._redraw_at = {}, None, None
        return dresser, path

    def test_outfit_written_to_the_copy(self):
        """A new outfit: both pictures written into the copy at their own length (the index says
        so), the game's loaded ones taken out of its table, the figure loaded again; nothing more
        while it stays the same."""
        outfits = [({"right": (SWORD, METAL)}, ())]
        worn, sprites.worn = sprites.worn, lambda gd, member, chunks=None: outfits[0]
        self.addCleanup(setattr, sprites, "worn", worn)
        with tempfile.TemporaryDirectory() as d:
            dresser, path = self.dressed_copy(d)
            gd = dresser.gd
            walk, fight = sprites.picture_ids(300)
            gd.entry(0, walk, 7)
            gd.loaded([1234, walk, fight, 99])
            self.assertEqual(dresser.update(True, 1.0), [300])
            data = read(path)
            places = gff.index_places(data, "BMP ")
            for picture, combat in ((walk, False), (fight, True)):
                chunk = dresser.pics.build(300, combat, *outfits[0])
                _, offset, length = places[picture]
                self.assertEqual(data[offset:offset + length], chunk)
                self.assertEqual(gff.read_gff(data)[("BMP ", picture)], chunk)
            self.assertEqual(gd.loaded_numbers(), [1234, sprites.STALE, sprites.STALE, 99])
            self.assertEqual(gd.entry_fields(0), (walk, sprites.NO_SLOT))
            gd.entry(0, walk, 8)  # (the game has loaded it)
            self.assertEqual(dresser.update(True, 2.0), [])
            self.assertEqual(gd.entry_fields(0), (walk, 8))
            outfits[0] = ({}, ())  # (taken off: plain again, as long as the plain one)
            self.assertEqual(dresser.update(True, 3.0), [300])
            data = read(path)
            self.assertEqual(gff.read_gff(data)[("BMP ", walk)], dresser.pics.build(300, False, {}, ()))

    def test_view_redrawn_after(self):
        """Shortly after pictures are loaded anew the view is drawn again (their shadows: the floor
        is drawn before the figures, while the new picture was still loading)."""
        outfits = [({"right": (SWORD, METAL)}, ())]
        worn, sprites.worn = sprites.worn, lambda gd, member, chunks=None: outfits[0]
        self.addCleanup(setattr, sprites, "worn", worn)
        with tempfile.TemporaryDirectory() as d:
            dresser, path = self.dressed_copy(d)
            asked = []
            dresser.request_redraw = lambda: asked.append(True)
            dresser.gd.entry(0, sprites.picture_ids(300)[0], 7)
            dresser.update(True, 1.0)
            self.assertEqual(len(asked), 1)  # (at once: the figure loaded and drawn)
            dresser.update(True, 1.0 + sprites.REDRAW_AFTER / 2)
            self.assertEqual(len(asked), 1)
            dresser.update(True, 1.0 + sprites.REDRAW_AFTER)
            self.assertEqual(len(asked), 2)
            dresser.update(True, 5.0)
            self.assertEqual(len(asked), 2)

    def test_copy_written_anew(self):
        """The launcher writes the copy anew (plain) for the next game: the outfit written again."""
        outfits = [({"right": (SWORD, METAL)}, ())]
        worn, sprites.worn = sprites.worn, lambda gd, member, chunks=None: outfits[0]
        self.addCleanup(setattr, sprites, "worn", worn)
        with tempfile.TemporaryDirectory() as d:
            dresser, path = self.dressed_copy(d)
            plain = read(path)
            dresser.update(True, 1.0)
            with open(path, "wb") as f:
                f.write(plain + b"\0")  # (written anew: another size, another time)
            self.assertEqual(dresser.update(True, 2.0), [300])
            data = read(path)
            walk = sprites.picture_ids(300)[0]
            self.assertEqual(gff.read_gff(data)[("BMP ", walk)], dresser.pics.build(300, False, *outfits[0]))

    def test_copy_not_writable(self):
        """The copy can't be written: nothing changed in the game, tried again next time."""
        outfits = [({"right": (SWORD, METAL)}, ())]
        worn, sprites.worn = sprites.worn, lambda gd, member, chunks=None: outfits[0]
        self.addCleanup(setattr, sprites, "worn", worn)
        with tempfile.TemporaryDirectory() as d:
            dresser, path = self.dressed_copy(d)
            walk = sprites.picture_ids(300)[0]
            dresser.gd.entry(0, walk, 7)
            real = dresser._write
            dresser._write = lambda pictures: False
            self.assertEqual(dresser.update(True, 1.0), [])
            self.assertEqual(dresser.gd.entry_fields(0), (walk, 7))
            dresser._write = real
            self.assertEqual(dresser.update(True, 2.0), [300])


class FakeGuest:
    def __init__(self):
        self.mem = bytearray(0x100000)
        self.size = len(self.mem)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class FakeGame:
    """Party members of these FIGURES, each its own combatant; a picture cache; the map table."""
    def __init__(self, figures):
        self.guest = FakeGuest()
        self.ds, self.load_seg = 0x4000, 0x100
        self.figures = figures

    def creature(self, member):
        rec = bytearray(sprites.game.CREATURE_SIZE)
        if member < len(self.figures):
            rec[sprites.game.CREATURE_NAME] = ord("A")
            struct.pack_into("<H", rec, sprites.CREATURE_FIGURE, self.figures[member])
        return bytes(rec)

    def combatants(self):
        return {c: c for c in range(len(self.figures))}

    def entry(self, combatant, picture, slot):
        at = self.ds * 16 + sprites.MAP_ENTRIES + combatant * sprites.MAP_ENTRY_SIZE
        self.guest.write(at + sprites.MAP_PICTURE, struct.pack("<H", picture))
        self.guest.write(at + sprites.MAP_SLOT, struct.pack("<H", slot))

    def loaded(self, numbers):
        """The game's table of the pictures it has loaded: these NUMBERS."""
        self.guest.write(self.ds * 16 + sprites.PICTURE_COUNT, struct.pack("<H", len(numbers)))
        base = (self.load_seg + sprites.PICTURE_TABLE_SEG) * 16
        for k, n in enumerate(numbers):
            self.guest.write(base + k * sprites.PICTURE_ENTRY, struct.pack("<H", n))

    def loaded_numbers(self):
        count, = struct.unpack("<H", self.guest.read(self.ds * 16 + sprites.PICTURE_COUNT, 2))
        base = (self.load_seg + sprites.PICTURE_TABLE_SEG) * 16
        return [struct.unpack("<H", self.guest.read(base + k * sprites.PICTURE_ENTRY, 2))[0] for k in range(count)]

    def entry_fields(self, combatant):
        at = self.ds * 16 + sprites.MAP_ENTRIES + combatant * sprites.MAP_ENTRY_SIZE
        return (struct.unpack("<H", self.guest.read(at + sprites.MAP_PICTURE, 2))[0],
                struct.unpack("<H", self.guest.read(at + sprites.MAP_SLOT, 2))[0])


if __name__ == "__main__":
    unittest.main()
